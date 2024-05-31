const express = require("express");
const WebSocket = require("ws");
const path = require("path");
const app = express();

const port = 3010;
let temp = 0;
let hm = 0;
let UUID = "0";

let connectedClients = [];

const wss = new WebSocket.Server({ port: 3030 });

app.use("/image", express.static("image"));
app.use("/js", express.static("js"));
app.get("/audio", (req, res) =>
  res.sendFile(path.resolve(__dirname, "./audio_client.html"))
);
app.get("/data", function (req, res) {
  res.json({
    temp: temp,
    hm: hm,
  });
});

app.listen(port, function () {
  console.log("Server running at " + port);
});

wss.on("connection", (ws) => {
  console.log("wws connected");
  ws.on("message", function incoming(data) {
    console.log("Received message:", data);
    try {
      const jsonData = JSON.parse(data);
      temp = jsonData.temp;
      hm = jsonData.hm;
      console.log("temp : ", temp, " / hm : ", hm);
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

app.listen(port, function () {
  console.log("Server running at " + port);
});
