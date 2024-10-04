import os
import json
import asyncio
import threading
import websockets
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__)

data_store = {}  # 데이터 저장소
connected_clients = []  # MIC 서버 클라이언트 목록

'''
# MIC 서버 WebSocket 설정 (포트 3020)
async def mic_server(websocket, path):
    print("MIC server connected")
    connected_clients.append(websocket)
    try : 
        async for message in websocket:
            # 모든 클라이언트에 메시지 전송
            disconnected_clients = []
            for client in connected_clients:
                if client.open : await client.send(message)
                else : disconnected_clients.append(client)
            # 끊어진 클라이언트 제거
            for client in disconnected_clients : connected_clients.remove(client)
    finally : connected_clients.remove(websocket)

# 정적 파일 제공 (예: 오디오 파일)
@app.route('/audio')
def serve_audio() :
    return send_from_directory(directory=os.getcwd(), filename="audio_client.html")

@app.route('/image/<path:filename>')
def serve_image(filename) :
    return send_from_directory(directory=os.path.join(os.getcwd(), 'image'), filename=filename)

@app.route('/js/<path:filename>')
def serve_js(filename) :
    return send_from_directory(directory=os.path.join(os.getcwd(), 'js'), filename=filename)
'''

# 데이터 서버 경로 설정
@app.route('/data')
def get_data():
    uuid = request.args.get('uuid')
    if uuid in data_store : return jsonify(data_store[uuid])
    else : return jsonify({"error": "UUID not found"}), 404

# WS 서버 (포트 3030) - 라즈베리파이로부터 데이터 수신 및 알람 송신
async def ws_server(websocket, path) :
    print("WS server connected")
    async for message in websocket:
        try :
            json_data = json.loads(message)
            uuid = json_data.get("UUID")
            temp = json_data.get("temperature")
            humidity = json_data.get("humidity")
            time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if uuid :
                print(f"UUID: {uuid}, Temp: {temp}, Humidity: {humidity}")
                data_store[uuid] = {"temp": temp, "humidity": humidity, "time": time}
            else :
                print("UUID not found in message")
        except json.JSONDecodeError as e : 
            print(f"Error parsing JSON: {e}")

# Flask 앱 실행 (포트 3010)
def run_flask() : app.run(host='0.0.0.0', port=3010)

# WebSocket 서버 실행 (포트 3020, 3030)
async def run_ws_servers() :
    #mic_server_task = websockets.serve(mic_server, '0.0.0.0', 3020)
    ws_server_task = websockets.serve(ws_server, '0.0.0.0', 3030)
    await asyncio.gather(ws_server_task)
    # await asyncio.gather(mic_server_task, ws_server_task)

if __name__ == "__main__" :
    flask_thread = threading.Thread(target=run_flask) # Flask 서버를 별도의 스레드에서 실행
    flask_thread.start()

    asyncio.run(run_ws_servers()) # asyncio 이벤트 루프에서 WebSocket 서버 실행