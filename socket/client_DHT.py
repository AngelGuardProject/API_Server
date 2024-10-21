#sudo su
#apt-get update
#apt-get install build-essential python3-dev
#pip install bleak websocket-client adafruit-circuitpython-dht --break-system-packages

import time
import adafruit_dht
import board
import RPi.GPIO as GPIO
import websocket
import json

DHT_PIN = 23
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(DHT_PIN, GPIO.IN)
dhtDevice = adafruit_dht.DHT11(board.D23)
WS_SERVER_URL = "ws://louk342.iptime.org:3030"
UUID = 0

def connect_ws():
    """웹소켓 서버에 연결하는 함수"""
    ws = websocket.WebSocket()
    ws.connect(WS_SERVER_URL)
    print("WS connected")
    return ws

def main():
    print("DHT started")
    ws = connect_ws()
    while True:
        try:
            print("trying dht")
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            print("trying success")
            if humidity is not None and temperature is not None:
                data = {
                    "UUID": UUID,
                    "temperature": temperature,
                    "humidity": humidity
                }
                ws.send(json.dumps(data))
                print(f"데이터 전송: {data}")
            else:
                print("DHT11 센서에서 데이터를 읽어오지 못했습니다.")
            time.sleep(1)

        except BrokenPipeError:
            print("연결 끊김: 재연결 시도 중...")
            ws = connect_ws()  # 서버 재연결 시도
            time.sleep(1)

        except KeyboardInterrupt:
            break

        except Exception as e:
            print(type(e), e)
            time.sleep(1)

if __name__ == "__main__" : main()
