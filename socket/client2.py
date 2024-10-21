import RPi.GPIO as GPIO
import adafruit_dht
import board
import asyncio
import websockets
import time
import json

UUID = 0
WS_SERVER_URL = "ws://louk342.iptime.org:3030"

DHT_PIN = 23
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DHT_PIN, GPIO.IN)
dhtDevice = adafruit_dht.DHT11(board.D23)

# 핀 번호 설정 (라즈베리파이의 GPIO 핀을 ULN2003의 IN1 ~ IN4에 연결)
IN1 = 18  # ULN2003 IN1
IN2 = 17  # ULN2003 IN2
IN3 = 27  # ULN2003 IN3
IN4 = 22  # ULN2003 IN4

# 핀을 출력 모드로 설정
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# 스텝 순서 (4-step sequence)
step_sequence = [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, 0],
    [0, 0, 0, 1],
]

# 전역 변수로 모터 전원 상태를 설정 (초기값: 0)
motor_power = 0


def set_step(w1, w2, w3, w4):
    """각 단계의 GPIO 핀 출력을 설정"""
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)


def rotate_motor(delay, steps):
    while True:
        if motor_power == 1:  # motor_power가 1일 때만 회전
            for _ in range(steps):
                for step in step_sequence:
                    if motor_power == 0:  # motor_power가 0으로 바뀌면 즉시 중지
                        set_step(0, 0, 0, 0)
                        return
                    set_step(*step)
                    time.sleep(delay)
        else:
            set_step(0, 0, 0, 0)  # 모터 정지 상태 유지


# 서버 재연결
async def reconnect():
    while True:
        try:
            async with websockets.connect(WS_SERVER_URL) as websocket:
                print("Reconnected to server")
                await asyncio.gather(receive_message(websocket), dht(websocket))
        except (websockets.exceptions.ConnectionClosed, OSError):
            print("Reconnection failed. Retrying in 5 seconds...")
            await asyncio.sleep(5)
        except KeyboardInterrupt:
            print("\nClient exited during reconnect")
            break


# 서버에서 오는 메시지를 수신하고 출력
async def receive_message(websocket):
    try:
        async for message in websocket:
            json_data = json.loads(message)
            print("message recieved : "),json_data
            uuid = json_data.get("uuid")
            motor_value = json_data.get("moter")
            if uuid == UUID:
                global motor_power
                motor_power = motor_value
                print(f"Updated motor_power to {motor_power}")
            else:
                print("Received UUID does not match")
    except websockets.exceptions.ConnectionClosed:
        print("Server closed")
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"Unexpected error: {type(e)} - {e}")


async def dht(websocket):
    while True:
        try:
            temp = dhtDevice.temperature
            humi = dhtDevice.humidity
            if humi is not None and temp is not None:
                data = {"UUID": UUID, "temperature": temp, "humidity": humi}
                await websocket.send(json.dumps(data))
                print(f"Data send: {data}")
            else:
                print("DHT error")
            await asyncio.sleep(1)
        except BrokenPipeError:
            print("Connetion lost. Reconneting")
            await asyncio.sleep(1)
            await reconnect()
        except KeyboardInterrupt:
            print("DHT stop")
            break
        except Exception as e:
            print(type(e), e)
            await asyncio.sleep(1)


async def main():
    try:
        async with websockets.connect(WS_SERVER_URL) as websocket:
            print("Server connected")
            # 수신 및 송신 작업을 동시에 실행하여 연결을 유지
            await asyncio.gather(receive_message(websocket), dht(websocket))
            # rotate_motor(0.005, 512)
    except websockets.exceptions.ConnectionClosed:
        print("Server closed")
    except KeyboardInterrupt:
        print("\nClient exited")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient exited")
    finally:
        GPIO.cleanup()
