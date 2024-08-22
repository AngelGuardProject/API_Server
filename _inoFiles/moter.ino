#define IN1 2
#define IN2 4
#define IN3 16
#define IN4 17

int Steps = 0;
unsigned long last_time = 0;
unsigned long currentMillis = 0;

void setup() {
    Serial.begin(115200);
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
}

void loop() {
    currentMillis = micros();
    if (currentMillis - last_time >= 1000) { // 1밀리초마다 스텝 이동
        stepper(1);
        last_time = micros();
    }
}

void stepper(int xw) {
    for (int x = 0; x < xw; x++) {
        switch (Steps) {
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
        if (Steps > 7) Steps = 0;
    }
}
