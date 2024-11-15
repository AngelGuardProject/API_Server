# Angel Guard Buffer Server

### server domain : louk342.iptime.org:3010
- data?uuid=0 : get 요청 보낼 시 json으로 temp(온도), hm(습도), time(마지막으로 데이터 받은 시간) 반환.
### MIC domain : ws://louk342.iptime.org:3020
- 모바일앱 -> HW 음성 실시간 전송용 웹소캣
### Data domain : ws://louk342.iptime.org:3030
- push 데이터는 WS를 통해 UUID와 함께 psuh 이유와 함께 전송하게 할 예정