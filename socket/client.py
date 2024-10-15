import asyncio
import websockets

# 서버에서 오는 메시지를 수신하고 출력
async def receive_message(websocket):
    try:
        async for message in websocket:
            print(f"\n받은 메시지: {message}\n", end="")
    except websockets.exceptions.ConnectionClosed:
        print("서버와의 연결이 종료되었습니다.")

# 1초마다 값을 증가시키며 서버로 전송
async def send_message(websocket):
    value = 0
    try:
        while True:
            await websocket.send(str(value))
            print(f"보낸 메시지: {value}")
            value += 1
            await asyncio.sleep(1)  # 1초마다 값을 증가시키며 전송
    except websockets.exceptions.ConnectionClosed:
        print("서버와의 연결이 종료되었습니다.")

async def main():
    # 서버에 연결
    uri = "ws://localhost:6789"
    try:
        async with websockets.connect(uri) as websocket:
            print("서버에 연결되었습니다.")
            # 수신 및 송신 작업을 동시에 실행하여 연결을 유지
            await asyncio.gather(
                receive_message(websocket),
                send_message(websocket)
            )
    except websockets.exceptions.ConnectionClosed:
        print("서버와의 연결이 종료되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())
