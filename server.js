const express = require("express");
const WebSocket = require("ws");
const app = express();

const port = 3000;
let tmp = 0; // 값이 변경될 경우를 대비하여 'let' 사용
let hm = 0; // 값이 변경될 경우를 대비하여 'let' 사용

app.get("/data", function (req, res) {
  res.json({
    tmp: tmp,
    hm: hm,
  });
});

const server = app.listen(port, function () {
  console.log("Server running at " + port);
});

// Express 서버와 동일한 포트(3000)에서 WebSocket 서버 생성
const wss = new WebSocket.Server({ server });

wss.on("connection", (ws) => {
  console.log("WebSocket client connected");

  ws.on("message", function incoming(data) {
    console.log("Received message:", data);
    try {
      const jsonData = JSON.parse(data);
      console.log("Received JSON data:", jsonData);
      tmp = jsonData.tmp;
      hm = jsonData.hm;
    } catch (error) {
      console.error("Error parsing JSON data:", error);
    }
  });
});
