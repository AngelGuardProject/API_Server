#include <WiFi.h>
#include <DHT.h>
#include <Wire.h>
#include "SSD1306.h"
#include <ArduinoJson.h>
#include <ArduinoWebsockets.h>
#include <BluetoothSerial.h>

#define IN1 2
#define IN2 4
#define IN3 16
#define IN4 17

DHT dht(15, DHT11);
SSD1306 display(0x3c, 21, 22);
using namespace websockets;
WebsocketsClient client;
BluetoothSerial SerialBT;

int Steps = 0;
unsigned long last_time = 0;
unsigned long currentMillis = 0;

String ssid = "";
String password = "";

TaskHandle_t moter;

void moterCode(void *param)
{
    while (true)
    {
        currentMillis = micros();
        if (currentMillis - last_time >= 1000)
        { // 1밀리초마다 스텝 이동
            stepper(1);
            last_time = micros();
        }
    }
}

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
    display.drawString(0, 0, "AngelGuard");
    display.drawString(0, 16, "Waiting BLE");
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
                    display.drawString(i, 16, ".");
                    display.display();
                    delay(500);
                }

                if (WiFi.status() == WL_CONNECTED)
                {
                    // Serial.println("\nWiFi Connected!");
                    display.clear();
                    display.drawString(0, 0, "WiFi");
                    display.drawString(0, 16, "Connected!");
                    display.display();
                }
                else
                {
                    // Serial.println("\nFailed to connect to WiFi.");
                    display.clear();
                    display.drawString(0, 0, "WiFi");
                    display.drawString(0, 16, "Failed");
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
        display.drawString(0, 16, "Offline");
        display.display();
        delay(5000);
        return;
    }

    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);

    xTaskCreatePinnedToCore(
        moterCode, // 태스크를 구현한 함수
        "moter",   // 태스크 이름
        10000,     // 스택 크기 (word단위)
        NULL,      // 태스크 파라미터
        0,         // 태스크 우선순위
        &moter,    // 태스크 핸들
        0);
}

void loop()
{
    // DHT
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    if (isnan(temperature) || isnan(humidity))
    {
        // Serial.println("DHT Error__");
        display.clear();
        display.drawString(0, 0, "DHT Error");
        display.display();
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
    /*
    currentMillis = micros();
    if (currentMillis - last_time >= 1000) { // 1밀리초마다 스텝 이동
        stepper(1);
        last_time = micros();
    }
    */
}

void stepper(int xw)
{
    for (int x = 0; x < xw; x++)
    {
        switch (Steps)
        {
        case 0:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, HIGH);
            break;
        case 1:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, HIGH);
            digitalWrite(IN4, HIGH);
            break;
        case 2:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, HIGH);
            digitalWrite(IN4, LOW);
            break;
        case 3:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, HIGH);
            digitalWrite(IN3, HIGH);
            digitalWrite(IN4, LOW);
            break;
        case 4:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, HIGH);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, LOW);
            break;
        case 5:
            digitalWrite(IN1, HIGH);
            digitalWrite(IN2, HIGH);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, LOW);
            break;
        case 6:
            digitalWrite(IN1, HIGH);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, LOW);
            break;
        case 7:
            digitalWrite(IN1, HIGH);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, HIGH);
            break;
        default:
            digitalWrite(IN1, LOW);
            digitalWrite(IN2, LOW);
            digitalWrite(IN3, LOW);
            digitalWrite(IN4, LOW);
            break;
        }
        Steps++; // 스텝 증가 (한 방향으로 계속 회전)
        if (Steps > 7)
            Steps = 0;
    }
}
