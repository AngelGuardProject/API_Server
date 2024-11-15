import asyncio
import websockets
import RPi.GPIO as GPIO
import time
import json
import adafruit_dht
import board
from threading import Thread

UUID = 0  # 고유 식별자 설정
WS_SERVER_URL = "ws://louk342.iptime.org:3030"  # WebSocket 서버 주소

# DHT11 센서 핀 설정
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

# 각 단계의 GPIO 핀 출력을 설정하는 함수
def set_step(w1, w2, w3, w4):
    GPIO.output(IN1, w1)
    GPIO.output(IN2, w2)
    GPIO.output(IN3, w3)
    GPIO.output(IN4, w4)

# 모터를 회전시키는 함수 (별도 스레드에서 실행)
def rotate_motor(delay=0.005, steps=512):
    global motor_power
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
            time.sleep(0.1)  # 모터가 꺼져 있을 때 대기

# WebSocket 서버에서 메시지를 수신하고 처리하는 함수
async def receive_message(websocket):
    global motor_power
    try:
        async for message in websocket:
            try:
                # JSON 데이터 파싱
                json_data = json.loads(message)
                print("Message received:", json_data)

                uuid = json_data.get("uuid")
                motor_value = json_data.get("moter")

                if uuid == UUID:
                    # 수신된 uuid가 자신의 uuid와 일치하는 경우
                    motor_power = int(motor_value)
                    if motor_power == 1:
                        print("Motor ON")
                    elif motor_power == 0:
                        print("Motor OFF")
                        set_step(0, 0, 0, 0)  # 모터 정지
                else:
                    print("Received UUID does not match")

            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
            except Exception as e:
                print(f"Unexpected error: {type(e)} - {e}")

    except websockets.exceptions.ConnectionClosed:
        print("Server closed")
    except Exception as e:
        print(f"Unexpected error: {type(e)} - {e}")

# DHT11 센서 데이터를 서버로 전송하는 함수
async def dht_send(websocket):
    while True:
        try:
            temp = dhtDevice.temperature
            humi = dhtDevice.humidity
            if humi is not None and temp is not None:
                data = {"UUID": UUID, "temperature": temp, "humidity": humi}
                await websocket.send(json.dumps(data))
                print(f"Data sent: {data}")
            else:
                print("DHT error")
            await asyncio.sleep(1)  # 1초 간격으로 데이터 전송
        except BrokenPipeError:
            print("Connection lost. Reconnecting...")
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("DHT stopped by user")
            break
        except Exception as e:
            print(type(e), e)
            await asyncio.sleep(1)

# WebSocket 클라이언트 연결 및 실행
async def main():
    try:
        async with websockets.connect(WS_SERVER_URL) as websocket:
            print("Connected to server")
            await asyncio.gather(receive_message(websocket), dht_send(websocket))
    except websockets.exceptions.ConnectionClosed:
        print("Server closed")
    except KeyboardInterrupt:
        print("Client exited by user")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        motor_thread = Thread(target=rotate_motor)
        motor_thread.daemon = True
        motor_thread.start()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Client stopped by user")
    finally:
        GPIO.cleanup()
