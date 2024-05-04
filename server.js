const express = require("express");
const WebSocket = require("ws");
const app = express();

const port = 3000;
let tmp = 0; // Changed to 'let' for best practice if these will change
let hm = 0; // Changed to 'let' for best practice if these will change

app.get("/data", function (req, res) {
  res.json({
    tmp: tmp,
    hm: hm,
  });
});

app.listen(port, function () {
  console.log("Server running at " + port);
});

// Create a WebSocket server on port 3030
const wss = new WebSocket.Server({ port: 3030 });

wss.on("connection", (ws) => {
  console.log("WebSocket server started");
  ws.on("error", console.error);

  ws.on("message", function message(data) {
    console.log("received: %s", data);
    try {
      const jsonData = JSON.parse(message);
      console.log("수신된 JSON 데이터:", jsonData);
      tmp = jsonData.tmp;
      hm = jsonData.hm;
    } catch (error) {
      console.error("JSON 데이터 파싱 오류:", error);
    }
  });
});
