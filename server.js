const express = require("express");
const WebSocket = require("ws");
const app = express();

const port = 3000;
let temp = 0;
let hm = 0;

app.get("/data", function (req, res) {
  res.json({
    temp: temp,
    hm: hm,
  });
});

const server = app.listen(port, function () {
  console.log("Server running at " + port);
});

const wss = new WebSocket.Server({ port: 3030 });

wss.on("connection", (ws) => {
  console.log("WebSocket client connected");

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
