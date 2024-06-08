//파티션 전부 사용하게 해야지 ESP32에 들어감
#include <WiFi.h>
#include <BluetoothSerial.h>

BluetoothSerial SerialBT;

const int ledPin = 2;

String ssid = "";
String password = "";

void blinkLED(int times, int delayTime) {
  for(int i = 0; i < times; i++) {
    digitalWrite(ledPin, HIGH);
    delay(delayTime);
    digitalWrite(ledPin, LOW);
    delay(delayTime);
  }
} 

void setup() {
  Serial.begin(115200);
  SerialBT.begin("AngelGuard");
  Serial.println("The device started, now you can pair it with Bluetooth!");

  pinMode(ledPin, OUTPUT);
}

void loop() {
  if (SerialBT.available()) {
    String receivedData = SerialBT.readStringUntil('\n');
    Serial.println("Received Data: " + receivedData);

    int separatorIndex = receivedData.indexOf(',');
    if (separatorIndex != -1) {
      ssid = receivedData.substring(0, separatorIndex);
      password = receivedData.substring(separatorIndex + 1);
      Serial.println("SSID: " + ssid);
      Serial.println("Password: " + password);

      WiFi.begin(ssid.c_str(), password.c_str());
      Serial.print("Connecting to WiFi");

      int attempts = 0;
      while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
      }

      if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi Connected!");
        blinkLED(5, 500);
      } else {
        Serial.println("\nFailed to connect to WiFi.");
      }
    }
  }
}
