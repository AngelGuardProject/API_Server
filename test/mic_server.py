import asyncio
import websockets
import base64

connected_clients = set()

async def audio_handler(websocket, path):
    print("클라이언트 연결됨")
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # 다른 연결된 클라이언트(라즈베리파이)에게도 데이터 브로드캐스트
            if connected_clients:
                await asyncio.wait([client.send(message) for client in connected_clients if client != websocket])
    except websockets.exceptions.ConnectionClosed:
        print("클라이언트 연결 종료")
    finally:
        connected_clients.remove(websocket)

async def main():
    async with websockets.serve(audio_handler, "0.0.0.0", 3030):
        print("WebSocket 서버가 3030 포트에서 실행 중")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
