// DHT sensor library / by Adafruit
// ESP8266 and ESP32 OLED driver for SSD1306 displays / by THingPulse
// ArduinoJson / by Benoit Blanchon
// ArduinoWebsockets / by Gll Malmon
#include <WiFi.h>
#include <DHT.h>
#include <Wire.h>
#include "SSD1306.h"
#include <ArduinoJson.h>
#include <ArduinoWebsockets.h>
#include <EEPROM.h>

DHT dht(15, DHT11);
SSD1306 display(0x3c, 21, 22);
using namespace websockets;
WebsocketsClient client;

void setup()
{
  Serial.begin(115200);
  pinMode(2, OUTPUT);
  // Wi-Fi
  WiFi.begin("Louk-2.4G", "#i2ScO8unSF7");
  Serial.print("Wi-Fi Connecting");
  for (unsigned char i = 0; i < 200 && WiFi.status() != WL_CONNECTED; i++)
  {
    Serial.print(".");
    delay(50);
  }
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("Can't connect Wifi until 10 secends");
    return;
  }
  Serial.println("");
  Serial.println("Wi-Fi Connected");

  dht.begin();

  display.init();
  display.setFont(ArialMT_Plain_16);
  /*
  // EEPROM 초기화
  EEPROM.begin(512);
  // UUID 읽기
  String storedUUID = readUUID();
  Serial.println("Saved UUID: " + storedUUID);
  // 저장된 UUID가 없다면 새로운 UUID 생성 및 저장
  if (storedUUID == "") {
    String newUUID = "AG_001";
    Serial.println("Create new uuid: " + newUUID);
    saveUUID(newUUID);
  }
  */
  if (client.connect("ws://louk342.iptime.org:3030"))
    Serial.println("WS Connected");
}

void loop()
{
  // DHT
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity))
  {
    Serial.println("DHT Error__");
    return;
  }

  // OLED
  display.clear();
  display.drawString(0, 0, "Temp : " + String(temperature));
  display.drawString(0, 16, "Humi : " + String(humidity));
  display.display();

  // Data push
  if (temperature * humidity > 250)
  {
    StaticJsonDocument<200> json;
    json["temp"] = temperature;
    json["hm"] = humidity;
    json["uuid"] = 0;
    //  JSON parsing
    String push;
    serializeJson(json, push);
  }

  // WS
  StaticJsonDocument<200> json;
  json["temp"] = temperature;
  json["hm"] = humidity;
  json["uuid"] = 0;
  //  JSON parsing
  String data;
  serializeJson(json, data);
  client.send(data);

  // Blink
  digitalWrite(2, HIGH);
  delay(10);
  digitalWrite(2, LOW);

  // Console
  // Serial.println("Temp : "+String(temperature)+", Humi : "+String(humidity));

  delay(1000);
}
/*
void saveUUID(String uuid) {
  // EEPROM UUID store
  for (int i = 0; i < UUID_SIZE; i++) {
    EEPROM.write(UUID_ADDR + i, uuid.charAt(i));
  }
  EEPROM.commit();
}

String readUUID() {
  // EEPROM UUID read
  String storedUUID = "";
  for (int i = 0; i < UUID_SIZE; i++) {
    char c = EEPROM.read(UUID_ADDR + i);
    if (c != 0xFF) {
      storedUUID += c;
    } else {
      break; // EEPROM data end break
    }
  }
  return storedUUID;
}
*/