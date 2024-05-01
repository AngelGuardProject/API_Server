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
    // Example: Parse data and update `tmp` and `hm`
    /*
    try {
      const parsedData = JSON.parse(data);
      tmp = parsedData.tmp;
      hm = parsedData.hm;
    } catch (error) {
      console.error("Error parsing data: ", error);
    }
    */
  });
});
