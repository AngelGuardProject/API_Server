import json
import asyncio
import threading
import websockets
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

data_store = {}  # 데이터 저장소

# 데이터 서버 경로 설정
@app.route("/data")
def get_data():
    uuid = request.args.get("uuid")
    try:
        uuid = int(uuid)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid UUID format"}), 400
    if uuid in data_store:
        return jsonify(data_store[uuid])
    else:
        return jsonify({"error": "UUID not found"}), 404


# WS 서버 (포트 3030) - 라즈베리파이로부터 데이터 수신 및 스텝모터 명령
async def ws_server(websocket, path):
    print("WS server connected")
    async for message in websocket:
        try:
            json_data = json.loads(message)
            uuid = json_data.get("UUID")
            temp = json_data.get("temperature")
            humidity = json_data.get("humidity")
            time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if uuid is not None:
                print(f"UUID: {uuid}, Temp: {temp}, Humidity: {humidity}")
                data_store[uuid] = {"temp": temp, "humidity": humidity, "time": time}
                print(data_store[uuid])
            else:
                print("UUID not found in message")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(type(e), e)

async def run_ws_servers():
    async with websockets.serve(
        ws_server, "0.0.0.0", 3030, ping_interval=20, ping_timeout=30
    ):
        print("Server started")
        await asyncio.Future()

# Flask 앱 실행 (포트 3010)
def run_flask():app.run(host="0.0.0.0", port=3010)

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)  # Flask 서버를 별도의 스레드에서 실행
    flask_thread.start()

    asyncio.run(run_ws_servers())  # asyncio 이벤트 루프에서 WebSocket 서버 실행
