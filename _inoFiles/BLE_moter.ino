#include <DHT.h>
#include <Wire.h>
#include "SSD1306.h"
#include <BluetoothSerial.h>
#include <Stepper.h>

DHT dht(15, DHT11);
SSD1306 display(0x3c, 21, 22);


const int stepsPerRevolution = 2048; // 모터의 한 바퀴에 필요한 스텝 수
Stepper motor(stepsPerRevolution, 17, 4, 16, 2); // (IN4, IN2, IN3, IN1)
bool isMotorRunning = false;

unsigned long motorSpeedInterval = 10;  // 50ms 간격으로 모터 스텝 이동
unsigned long lastMotorStepTime = 0;

BluetoothSerial SerialBT;

void setup() {
  Serial.begin(115200);
  motor.setSpeed(10);  // 15 RPM으로 설정
  SerialBT.begin("AngelGuard");
  dht.begin();

  display.init();
  display.setFont(ArialMT_Plain_16);
  display.clear();
  display.drawString(0, 0, "AngelGuard");
  display.drawString(0, 16, "Waiting BLE");
  display.display();
}

void loop() {
  // 센서 데이터 읽기 및 OLED 디스플레이 업데이트
  updateSensorData();

  // 블루투스 데이터 수신 및 모터 상태 업데이트
  if (SerialBT.available()) {
    String receivedData = SerialBT.readStringUntil('\n');
    if(receivedData == "0") isMotorRunning = false;
    else if(receivedData == "1") isMotorRunning = true;
  }

  // 모터 상태 업데이트
  updateMotor();
}

void updateSensorData() {
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  if (isnan(temperature) || isnan(humidity)) {
    display.clear();
    display.drawString(0, 0, "DHT Error");
    display.display();
    return;
  }

  // OLED 업데이트
  display.clear();
  display.drawString(0, 0, "Temp : " + String(temperature));
  display.drawString(0, 16, "Humi : " + String(humidity));
  display.display();
}

void updateMotor() {
  unsigned long currentMillis = millis();

  // 모터가 실행 중이고, 특정 시간 간격이 지났다면 모터를 한 스텝 이동
  if (isMotorRunning && currentMillis - lastMotorStepTime >= motorSpeedInterval) {
    motor.step(5);  // 모터를 한 스텝 이동 (여기서 5 스텝씩 이동)
    lastMotorStepTime = currentMillis;  // 마지막 스텝 시간 갱신
  }
}
