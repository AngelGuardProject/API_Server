const express = require("express");
const WebSocket = require("ws");
const path = require("path");
const app = express();

let dataStore = {}; //ws server

let connectedClients = []; //MIC server

const port = 3010;
const mics = new WebSocket.Server({ port: 3020 });
const wss = new WebSocket.Server({ port: 3030 });

app.listen(port, function () {
  console.log("Server running at " + port);
});

//MIC sever
app.use("/image", express.static("image"));
app.use("/js", express.static("js"));
app.get("/audio", (req, res) => res.sendFile(path.resolve(__dirname, "./audio_client.html")));
mics.on("connection", (ws, req) => {
  console.log("MIC server connected");
  connectedClients.push(ws);
  ws.on("message", (data) => {
    connectedClients.forEach((ws, i) => {
      if (ws.readyState === ws.OPEN) ws.send(data);
      else connectedClients.splice(i, 1);
    });
  });
});

//Data server
app.get("/data", function (req, res) {
  const uuid = req.query.uuid;
  if (uuid) {
    // 특정 uuid의 데이터를 반환
    if (dataStore[uuid]) res.json(dataStore[uuid]);
    else res.status(404).json({ error: "UUID not found" });
  } else res.status(404).json({ error: "UUID not found" });
});

//WS Server
wss.on("connection", (ws) => {
  ws.on('error', console.error);
  console.log("wws connected");
  ws.on("message", function incoming(data) {
    //console.log("Received message:", data);
    try {
      const jsonData = JSON.parse(data);
      const uuid = jsonData.UUID;
      const temp = jsonData.temperature;
      const hm = jsonData.humidity;
      const time = new Date().toLocaleString('ko-KR');
      console.log("UUID : ", uuid, "temp : ", temp, " / hm : ", hm);
      //이곳에 이상치값 알림 기능 구현 필요
      dataStore[uuid] = { temp, hm, time };
    } catch (error) {
      console.error("Error parsing JSON data:", error);
    }
  });
});