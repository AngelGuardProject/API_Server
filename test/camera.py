from flask import Flask, request, Response
import cv2
import numpy as np

app = Flask(__name__)

frame = None  # 라즈베리파이에서 받은 이미지를 저장할 전역 변수

# 라즈베리파이에서 이미지를 업로드하는 경로
@app.route('/upload', methods=['POST'])
def upload():
    global frame
    file = request.files['image'].read()
    npimg = np.frombuffer(file, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    return "이미지 수신 성공", 200

# 클라이언트에게 스트리밍하는 경로
@app.route('/stream')
def stream() : 
    def generate_frames():
        global frame
        while True:
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__" : app.run(host='0.0.0.0', port=3000)

'''
import cv2
import requests

camera = cv2.VideoCapture(0)

# 서버에 스트리밍 전송 함수
def send_frame_to_server(frame):
    _, encoded_image = cv2.imencode('.jpg', frame)
    frame_data = encoded_image.tobytes()

    # 서버에 POST 요청으로 전송
    response = requests.post('http://louk342.iptime.org:3000/upload', files={'image': frame_data})
    print(f"서버 응답: {response.status_code}")

while True:
    success, frame = camera.read()
    if not success:
        break
    send_frame_to_server(frame)
'''