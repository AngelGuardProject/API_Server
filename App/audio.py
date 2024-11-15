import asyncio
import websockets

SERVER_HOST = "0.0.0.0"  # 모든 IP로부터 접속 허용
SERVER_PORT = 3020  # 사용할 포트 번호

# 연결된 클라이언트를 관리하기 위한 셋
connected_clients = set()


# 클라이언트로부터 오디오 데이터를 수신하고 다른 클라이언트로 브로드캐스트하는 함수
async def handle_client(websocket, path):
    # 연결된 클라이언트를 셋에 추가
    connected_clients.add(websocket)
    client_ip = websocket.remote_address[0]
    print(f"클라이언트 {client_ip} 연결됨")
    try:
        async for message in websocket:
            # 다른 클라이언트들에게 데이터 브로드캐스트
            for client in connected_clients:
                if client != websocket:
                    await client.send(message)
    except websockets.exceptions.ConnectionClosed:
        print(f"클라이언트 {client_ip} 연결 종료")
    finally:
        # 연결 종료 시 클라이언트를 셋에서 제거
        connected_clients.remove(websocket)


# WebSocket 서버 시작
async def main():
    async with websockets.serve(handle_client, SERVER_HOST, SERVER_PORT):
        print(f"WS 서버가 {SERVER_PORT} 포트에서 실행 중입니다...")
        await asyncio.Future()  # 서버가 종료되지 않도록 유지


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("서버가 사용자에 의해 종료되었습니다.")
