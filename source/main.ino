#include <Servo.h>

#define ESC_STOP 90

#define ESC_MAX_FORWARD 120

#define ESC_MAX_BACKWARD 60

#define ESC_LEFT_PIN 9

#define ESC_RIGHT_PIN 10

Servo leftESC;

Servo rightESC;

float leftTargetSpeed = 0.0f;

float rightTargetSpeed = 0.0f;

void setup() {
  Serial.begin(9600);

  leftESC.attach(ESC_LEFT_PIN);

  rightESC.attach(ESC_RIGHT_PIN);

  leftESC.write(ESC_STOP);

  rightESC.write(ESC_STOP);
}

void loop() {
  if (Serial.available()) {
    char command = Serial.read();

    switch (command) {
      case 'F':
        leftTargetSpeed = 100;
        rightTargetSpeed = 100;
        break;
      case 'L':
        leftTargetSpeed = -50;
        rightTargetSpeed = 50;
        break;
      case 'R':
        leftTargetSpeed = 50;
        rightTargetSpeed = -50;
        break;
      case 'S':
        leftTargetSpeed = 0;
        rightTargetSpeed = 0;
        break;
      default:
        Serial.println("Command error.");
  }

  setESC(leftESC, leftTargetSpeed);

  setESC(rightESC, rightTargetSpeed);
}

void setESC(Servo &esc, float speed) {
  int pwm = ESC_STOP;

  if (speed > 0) {
    pwm = ESC_STOP + map(speed, 0, 100, 0, ESC_MAX_FORWARD - ESC_STOP);
  } else if (speed < 0) {
    pwm = ESC_STOP + map(speed, 0, -100, 0, ESC_STOP - ESC_MAX_BACKWARD);
  }

  esc.write(constrain(pwm, ESC_MAX_BACKWARD, ESC_MAX_FORWARD));
}
