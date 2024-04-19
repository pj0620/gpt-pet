#define TOTAL_SENSORS 4
#define REPEATS 4

const int trigPins[] = {2, 4, 6, 8};
const int echoPins[] = {3, 5, 7, 9};

const int redPin = A0;
const int greenPin = A1;
const int bluePin = A2;

float duration, distance;

void sendSensorData() {
  for (int i=0; i<TOTAL_SENSORS; i++) {
    digitalWrite(trigPins[i], LOW);
    delayMicroseconds(2);
    digitalWrite(trigPins[i], HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPins[i], LOW);

    duration = pulseIn(echoPins[i], HIGH);
    distance = (duration*.0343)/2;
    Serial.print(distance);
    if (i != TOTAL_SENSORS - 1) {
      Serial.print(", ");
    } else {
      Serial.println("");
    }
  }
  delay(100);
}

void updateLeds() {
  if (Serial.available() > 0) {
    // Read the incoming string until newline is received
    String data = Serial.readStringUntil('\n');

    analogWrite(redPin, 255);
    delay(1000);
    analogWrite(redPin, 0);

    // Split the string into RGB components
    int commaIndex1 = data.indexOf(',');
    int commaIndex2 = data.indexOf(',', commaIndex1 + 1);

    // Extract each color component
    int red = data.substring(0, commaIndex1).toInt();
    int green = data.substring(commaIndex1 + 1, commaIndex2).toInt();
    int blue = data.substring(commaIndex2 + 1).toInt();

    // Map the RGB values from 0-255 range to 0-1023 (as analogWrite on some Arduino models accepts 0-255 only,
    // you might need to change the scaling accordingly or use PWM resolution commands on supported models)
    int analogRed = map(red, 0, 255, 0, 1023);
    int analogGreen = map(green, 0, 255, 0, 1023);
    int analogBlue = map(blue, 0, 255, 0, 1023);

    // Write the analog values to the pins
    analogWrite(redPin, analogRed);
    analogWrite(greenPin, analogGreen);
    analogWrite(bluePin, analogBlue);
  }
}

void setup() {
  for (int i=0; i<TOTAL_SENSORS; i++) {
    pinMode(trigPins[i], OUTPUT);
    pinMode(echoPins[i], INPUT);
  }

  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  sendSensorData();
  updateLeds();
}