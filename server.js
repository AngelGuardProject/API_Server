const express = require("express");
const WebSocket = require("ws");
const app = express();

const port = 3000;
const wsPort = 3030;

let temp = 0;
let hm = 0;
let UUID = "0";

const wss = new WebSocket.Server({ port: wsPort });

app.get("/data", function (req, res) {
  res.json({
    UUID: UUID,
    temp: temp,
    hm: hm,
  });
});

app.listen(port, function () {
  console.log("Server running at " + port);
});

wss.on("connection", (ws) => {
  console.log("WebSocket client connected");

  ws.on("message", function incoming(data) {
    console.log("Received message:", data);
    try {
      const jsonData = JSON.parse(data);
      temp = jsonData.temp;
      hm = jsonData.hm;
      UUID = jsonData.uuid;
      console.log("UUID : ", UUID, " / temp : ", temp, " / hm : ", hm);
    } catch (error) {
      console.error("Error parsing JSON data:", error);
    }
  });
});
