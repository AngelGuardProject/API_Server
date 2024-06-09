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
#include <BluetoothSerial.h>

DHT dht(15, DHT11);
SSD1306 display(0x3c, 21, 22);
using namespace websockets;
WebsocketsClient client;
BluetoothSerial SerialBT;

String ssid = "";
String password = "";

void setup()
{
    Serial.begin(115200);
    SerialBT.begin("AngelGuard");
    // Serial.println("Device Started");
    pinMode(2, OUTPUT);
    dht.begin();
    display.init();
    display.setFont(ArialMT_Plain_16);

    display.clear();
    display.drawString(0, 0, "Wait BLE");
    display.display();
    // Wi-Fi
    while (WiFi.status() != WL_CONNECTED)
    {
        if (SerialBT.available())
        {
            String receivedData = SerialBT.readStringUntil('\n');
            // Serial.println("Received Data: " + receivedData);

            int separatorIndex = receivedData.indexOf(',');
            if (separatorIndex != -1)
            {
                ssid = receivedData.substring(0, separatorIndex);
                password = receivedData.substring(separatorIndex + 1);
                // Serial.println("SSID: " + ssid);
                // Serial.println("Password: " + password);
                display.clear();
                display.drawString(0, 0, ssid);
                display.display();
                WiFi.begin(ssid.c_str(), password.c_str());
                // Serial.print("Wi-Fi Connecting");
                for (unsigned char i = 0; i < 20 && WiFi.status() != WL_CONNECTED; i++)
                {
                    // Serial.print(".");
                    display.drawString(16, i, '.');
                    display.display();
                    delay(1000);
                }

                if (WiFi.status() == WL_CONNECTED)
                {
                    // Serial.println("\nWiFi Connected!");
                    display.clear();
                    display.drawString(0, 0, "WiFi");
                    display.drawString(16, 0, "Connected!");
                    display.display();
                }
                else
                {
                    // Serial.println("\nFailed to connect to WiFi.");
                    display.clear();
                    display.drawString(0, 0, "WiFi");
                    display.drawString(16, 0, "Failed");
                    display.display();
                }
            }
        }
    }
    if (client.connect("ws://louk342.iptime.org:3030"))
    {
        Serial.println("WS Connected");
    }
    else
    {
        display.clear();
        display.drawString(0, 0, "Server");
        display.drawString(16, 0, "Offline");
        display.display();
        delay(5000);
        return;
    }
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