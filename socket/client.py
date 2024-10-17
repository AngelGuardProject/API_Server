import asyncio
import websockets
import json

# 서버에서 오는 메시지를 수신하고 출력
async def receive_message(websocket):
    try:
        async for message in websocket:
            print(f"\nRecevied: {message}\n", end="")
    except websockets.exceptions.ConnectionClosed:
        print("Server closed")


# 1초마다 값을 증가시키며 서버로 전송
async def dht(websocket):
    data = {"UUID": 1, "temperature": 10, "humidity":10}
    try:
        while True:
            await websocket.send(json.dumps(data))
            await asyncio.sleep(1)  # 1초마다 값을 증가시키며 전송
    except websockets.exceptions.ConnectionClosed:
        print("Server closed")


async def main():
    # 서버에 연결
    #uri = "ws://localhost:6666"
    uri = "ws://louk342.iptime.org:3030"
    try:
        async with websockets.connect(uri) as websocket:
            print("Server connected")
            # 수신 및 송신 작업을 동시에 실행하여 연결을 유지
            await asyncio.gather(receive_message(websocket), dht(websocket))
    except websockets.exceptions.ConnectionClosed:
        print("Server closed")
    except KeyboardInterrupt:
        print("\nClient exited")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nClient exited")
