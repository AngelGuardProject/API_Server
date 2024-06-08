# Angel Guard Buffer Server

### server domain : louk342.iptime.org:3010
- data?uuid=0 : get 요청 보낼 시 json으로 temp(온도), hm(습도), time(마지막으로 데이터 받은 시간) 반환.
- /audio : 음성데이터 작동 서버이나 아직 작업중

### WS domain : ws://louk342.iptime.org:3030
### MIC domain : ws://louk342.iptime.org:3020
- push 데이터는 WS를 통해 UUID와 함께 psuh 이유와 함께 전송하게 할 예정
