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
  const id = req.query.id;
  if (id) {
    // 특정 uuid의 데이터를 반환
    if (dataStore[id]) res.json(dataStore[id]);
    else res.status(404).json({ error: "ID not found" });
  } else res.status(404).json({ error: "ID not found" });
});

//ws Server
wss.on("connection", (ws) => {
  ws.on('error', console.error);
  console.log("wws connected");
  ws.on("message", function incoming(data) {
    //console.log("Received message:", data);
    try {
      const jsonData = JSON.parse(data);
      const id = jsonData.id;
      const temp = jsonData.temp;
      const hm = jsonData.hm;
      const time = new Date().toLocaleString('ko-KR');
      console.log("ID : ", id, "temp : ", temp, " / hm : ", hm);
      if(hm>70||temp>35) ws.send(id); //push
      dataStore[id] = { temp, hm , time};
    } catch (error) {
      
      console.error("Error parsing JSON data:", error);
    }
  });
});