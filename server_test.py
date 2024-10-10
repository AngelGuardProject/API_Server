# 파일명: ws_server.py

import asyncio
import websockets

# WebSocket 서버 함수
async def echo(websocket, path):
    print("클라이언트 연결됨")
    try:
        async for message in websocket:
            print(f"클라이언트로부터 메시지 수신: {message}")
            await websocket.send(f"서버로부터 응답: {message}")
    except websockets.ConnectionClosed:
        print("클라이언트 연결이 닫혔습니다")

# 서버 실행
async def main():
    async with websockets.serve(echo, "localhost", 3030):
        print("WebSocket 서버가 3030 포트에서 실행 중입니다")
        await asyncio.Future()  # 서버를 계속 실행하기 위해 비어 있는 Future 대기

# asyncio 이벤트 루프에서 서버 실행
if __name__ == "__main__":
    asyncio.run(main())
