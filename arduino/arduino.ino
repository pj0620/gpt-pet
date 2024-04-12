#define TOTAL_SENSORS 4
#define REPEATS 4

const int trigPins[] = {2, 4, 6, 8};
const int echoPins[] = {3, 5, 7, 9};

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

void setup() {
  for (int i=0; i<TOTAL_SENSORS; i++) {
    pinMode(trigPins[i], OUTPUT);
    pinMode(echoPins[i], INPUT);
  }
  Serial.begin(9600);
}

void loop() {
  // if (Serial.available() > 0) {
    // Serial.read();
    // for (int i=0; i<REPEATS; i++) {
      sendSensorData();
    // }
  // }
}