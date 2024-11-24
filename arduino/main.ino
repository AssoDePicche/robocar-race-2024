#include <Servo.h>

#define ESC_LEFT_PIN 10

#define ESC_RIGHT_PIN 9

#define MIN_SPEED (long)20

#define MAX_SPEED (long)100

#define DELTA_SPEED (long)5

struct Speed {
  long x;
  long y;

  Speed(long k) : x{k}, y{k} {}

  Speed(long x, long y) : x{x}, y{x} {}

  Speed operator+(long k) {
    x += k;
    y += k;
  }

  Speed operator-(long k) {
    x -= k;
    y -= k;
  }
};

long SpeedRemap(long value) {
  long remap = map(value, 0, 1023, 0, 180);

  return constrain(remap, MIN_SPEED, MAX_SPEED);
}

struct Car {
  Servo left;
  Servo right;
  Speed speed;

  Car(int leftPin, int rightPin): speed{MIN_SPEED} {
    left.attach(leftPin);

    right.attach(rightPin);
  }

  void Update() {
    left.write(SpeedRemap(this->speed.x));

    right.write(SpeedRemap(this->speed.y));
  }

  void SetSpeed(Speed speed) {
    this->speed = speed;
  }

  Speed GetSpeed(void) {
    return speed;
  }

  void Forward(void) {
    SetSpeed(Speed(MAX_SPEED / 2));
  }

  void Left(void) {
    this->speed.x -= DELTA_SPEED;

    this->speed.y += DELTA_SPEED;
  }

  void Right(void) {
    this->speed.x += DELTA_SPEED;

    this->speed.y -= DELTA_SPEED;
  }

  void Stop(void) {
    SetSpeed(Speed(MIN_SPEED));
  }
};

Car car(ESC_LEFT_PIN, ESC_RIGHT_PIN);

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    Speed speed = car.GetSpeed();

    Serial.print("L Speed: ");

    Serial.println(speed.x);

    Serial.print("R Speed: ");

    Serial.println(speed.y);
    
    char command = Serial.read();

    switch (command) {
      case 'F':
        car.Forward();
        break;
      case 'L':
        car.Left();
        break;
      case 'R':
        car.Right();
        break;
      case 'S':
        car.Stop();
        break;
      case '+':
        car.SetSpeed(speed + DELTA_SPEED);
        break;
      case '-':
        car.SetSpeed(speed - DELTA_SPEED);
    }

    car.Update();
  }
}
