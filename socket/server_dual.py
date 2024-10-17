import json
import asyncio
import threading
import websockets
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

data_store = {}  # 데이터 저장소
connected_clients = set()  # 웹소켓에 연결된 클라이언트들


# 연결된 모든 클라이언트에게 메시지 브로드캐스트 (JSON 형식)
async def broadcast_message(message):
    json_message = json.dumps(message)
    tasks = [client.send(json_message) for client in connected_clients]
    if tasks:
        await asyncio.gather(*tasks)


# WebSocket 서버 (포트 3030) - 라즈베리파이로부터 데이터 수신 및 알람 송신
async def ws_server(websocket, path):
    # 클라이언트를 연결된 클라이언트 집합에 추가
    connected_clients.add(websocket)
    print("[3030] Client connected")
    try:
        async for message in websocket:
            try:
                # JSON 데이터 파싱
                json_data = json.loads(message)
                uuid = json_data.get("UUID")
                temp = json_data.get("temperature")
                humidity = json_data.get("humidity")
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if uuid is not None:
                    # UUID, 온도, 습도 정보 출력 및 저장
                    print(f"UUID: {uuid}, Temp: {temp}, Humidity: {humidity}")
                    data_store[uuid] = {
                        "temp": temp,
                        "humidity": humidity,
                        "time": time,
                    }
                    print(data_store[uuid])
                else:
                    print("UUID not found in message")
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(type(e), e)
    except websockets.exceptions.ConnectionClosed:
        print("[3030] Client closed")
    finally:
        # 클라이언트가 연결을 종료할 때 집합에서 제거
        connected_clients.remove(websocket)


# WebSocket 서버 실행 (포트 3030)
async def run_ws_servers():
    async with websockets.serve(
        ws_server, "0.0.0.0", 3030, ping_interval=20, ping_timeout=30
    ):
        print("WebSocket server [Port: 3030] is online")
        await asyncio.Future()  # 서버가 종료되지 않도록 대기


@app.route("/moter", methods=["POST"])
def moter_control():
    try:
        # 요청으로부터 JSON 데이터를 가져옵니다.
        data = request.get_json()
        if "uuid" in data and "moter" in data:
            # WebSocket 서버에 연결된 클라이언트들에게 JSON 데이터를 브로드캐스트
            asyncio.run(broadcast_message(data))
            print(f"브로드캐스트된 메시지: {data}")
            return jsonify({"status": "success", "message": "Broadcasted"}), 200
        else:
            return jsonify({"status": "error", "message": "Invalid JSON format"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/data")
def get_data():
    uuid = request.args.get("uuid")
    try:
        # uuid를 정수로 변환
        uuid = int(uuid)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid UUID format"}), 400
    if uuid in data_store:
        # 해당 uuid의 데이터를 반환
        return jsonify(data_store[uuid])
    else:
        return jsonify({"error": "UUID not found"}), 404


# Flask 앱 실행 (포트 3010)
def run_flask():
    app.run(host="0.0.0.0", port=3010)


if __name__ == "__main__":
    # Flask 서버를 별도의 스레드에서 실행
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # WebSocket 서버 실행
    try:
        asyncio.run(run_ws_servers())
    except KeyboardInterrupt:
        print("\nServers safely closed")
