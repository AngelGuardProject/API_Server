import json
import asyncio
import threading
import websockets
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

data_store = {}  # 데이터 저장소
push_clients = set()  # 푸시 서버에 연결된 클라이언트들

connected_clients = set()

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

# 스텝모터 조종용
@app.route('/moter', methods=['POST'])
def control_moter():
    """ /moter 경로로 POST 요청이 들어오면 WebSocket 클라이언트에 데이터를 전송 """
    data = request.get_json()
    moter_value = data.get("moter")

    # moter 값이 0 또는 1일 때만 연결된 WebSocket 클라이언트에 전송
    if moter_value in [0, 1]:
        # 비동기로 WebSocket 메시지를 전송
        asyncio.run(send_to_clients(moter_value))
        print(f"Sent to WebSocket clients: {moter_value}")
        return jsonify({"status": "success", "moter": moter_value}), 200
    else:
        return jsonify({"status": "error", "message": "Invalid value"}), 400


async def send_to_clients(moter_value):
    """연결된 모든 WebSocket 클라이언트에게 메시지를 전송"""
    print('send',moter_value)
    if connected_clients:  # 연결된 클라이언트가 있을 때만 전송
        message = str(moter_value)
        await asyncio.wait([client.send(message) for client in connected_clients])

# WS 서버 (포트 3030) - 라즈베리파이로부터 데이터 수신 및 알람 송신
async def ws_server(websocket, path):
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
                if temp * humidity > 100:
                    await notify_push_clients(uuid)
            else:
                print("UUID not found in message")
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(type(e), e)


# WS push 알림 서버 포트 3020
async def push_server(websocket, path):
    push_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        push_clients.remove(websocket)


# 특정 UUID를 푸시 서버에 연결된 모든 클라이언트에게 전송
async def notify_push_clients(uuid):
    if push_clients:
        message = json.dumps({"alert": f"Condition met for UUID: {uuid}"})
        await asyncio.wait([client.send(uuid) for client in push_clients])
        print(f"Sent alert for UUID: {uuid}")

# WS, PUSH 서버 실행용 3030 3020
async def run_ws_servers():
    '''
    ws_server_task = websockets.serve(ws_server, "0.0.0.0", 3030, ping_interval=20, ping_timeout=30)
    #push_server_task = websockets.serve(push_server, "0.0.0.0", 3020, ping_interval=20, ping_timeout=30)
    await asyncio.gather(ws_server_task) #, push_server_task
    print("WS Servers started")
    '''
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
