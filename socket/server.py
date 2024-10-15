import asyncio
import websockets

# 연결된 클라이언트들을 관리하기 위한 집합
connected_clients = set()

# 클라이언트에서 메시지를 수신하여 출력 및 브로드캐스트
async def receive_message(websocket):
    try:
        async for message in websocket:
            print(f"받은 메시지: {message}")
            # 수신한 메시지를 다른 클라이언트들에게 브로드캐스트
            await broadcast_message(message, websocket)
    except websockets.exceptions.ConnectionClosed:
        print("클라이언트가 연결을 종료했습니다.")

# 연결된 모든 클라이언트에게 메시지 브로드캐스트
async def broadcast_message(message, sender_socket):
    # 보낸 클라이언트를 제외한 모든 클라이언트에게 메시지 전송
    tasks = [
        client.send(message) for client in connected_clients if client != sender_socket
    ]
    if tasks:  # 클라이언트가 있는 경우에만 gather 실행
        await asyncio.gather(*tasks)

# 특정 함수에서 0을 모든 클라이언트에게 브로드캐스트
async def broadcast_zero():
    message = "0"
    tasks = [client.send(message) for client in connected_clients]
    if tasks:
        await asyncio.gather(*tasks)
    print(f"모든 클라이언트에게 {message} 전송")

# 클라이언트의 연결을 처리하고 연결을 항상 유지
async def handle_client(websocket, path):
    connected_clients.add(websocket)
    print("클라이언트가 연결되었습니다.")
    try:
        await receive_message(websocket)
    finally:
        connected_clients.remove(websocket)
        print("클라이언트가 연결을 종료했습니다.")

async def main():
    # 포트 6789에서 WebSocket 서버 시작
    async with websockets.serve(handle_client, "localhost", 6789):
        print("웹소켓 서버가 ws://localhost:6789 에서 시작되었습니다.")
        
        # 주기적으로 broadcast_zero() 함수를 호출
        while True:
            await asyncio.sleep(10)  # 10초마다 0을 브로드캐스트
            await broadcast_zero()

if __name__ == "__main__":
    asyncio.run(main())
