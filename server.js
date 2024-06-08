const express = require("express");
const WebSocket = require("ws");
const path = require("path");
const app = express();

let dataStore = {};

let connectedClients = []; //MIC server

const wss = new WebSocket.Server({ port: 3030 });
const mics = new WebSocket.Server({ port: 3020 });
const port = 3010;
app.listen(port, function () {
  console.log("Server running at " + port);
});

app.use("/image", express.static("image"));
app.use("/js", express.static("js"));
app.get("/audio", (req, res) =>
  res.sendFile(path.resolve(__dirname, "./audio_client.html"))
);
app.get("/data", function (req, res) {
  const uuid = req.query.uuid;
  if (uuid) {
    // 특정 uuid의 데이터를 반환
    if (dataStore[uuid]) res.json(dataStore[uuid]);
    else res.status(404).json({ error: "UUID not found" });
  } else res.status(404).json({ error: "UUID not found" });
});

wss.on("connection", (ws) => {
  console.log("wws connected");
  ws.on("message", function incoming(data) {
    //console.log("Received message:", data);
    try {
      const jsonData = JSON.parse(data);
      const uuid = jsonData.uuid;
      const temp = jsonData.temp;
      const hm = jsonData.hm;
      const time = new Date().toLocaleString();
      console.log("UUID : ", uuid, "temp : ", temp, " / hm : ", hm);
      dataStore[uuid] = { temp, hm , time};
    } catch (error) {
      console.error("Error parsing JSON data:", error);
    }
  });
});

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
