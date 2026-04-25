const int CH1_PIN = 13;
const int CH2_PIN = 12;
const int CH3_PIN = 15;
const int CH5_PIN = 2;
const int CH6_PIN = 4;

const int L_PWM_F = 25; 
const int L_PWM_B = 26;
const int R_PWM_F = 27; 
const int R_PWM_B = 14;

long lastCh1 = 1500;
long lastCh2 = 1500;
long lastCh3 = 1000;
long lastCh5 = 1000;
long lastCh6 = 1000;
int errorCounter = 0;

void setup() {
  Serial.begin(115200);

  pinMode(CH1_PIN, INPUT); 
  pinMode(CH2_PIN, INPUT);
  pinMode(CH3_PIN, INPUT); 
  pinMode(CH5_PIN, INPUT);
  pinMode(CH6_PIN, INPUT);

  pinMode(L_PWM_F, OUTPUT); digitalWrite(L_PWM_F, LOW);
  pinMode(L_PWM_B, OUTPUT); digitalWrite(L_PWM_B, LOW);
  pinMode(R_PWM_F, OUTPUT); digitalWrite(R_PWM_F, LOW);
  pinMode(R_PWM_B, OUTPUT); digitalWrite(R_PWM_B, LOW);

  ledcAttach(L_PWM_F, 5000, 8); 
  ledcAttach(L_PWM_B, 5000, 8); 
  ledcAttach(R_PWM_F, 5000, 8); 
  ledcAttach(R_PWM_B, 5000, 8); 

  stopMotors();
}

void loop() {
  long rawCh1 = pulseIn(CH1_PIN, HIGH, 21000);
  long rawCh2 = pulseIn(CH2_PIN, HIGH, 21000);
  long rawCh3 = pulseIn(CH3_PIN, HIGH, 21000);
  long rawCh5 = pulseIn(CH5_PIN, HIGH, 21000);
  long rawCh6 = pulseIn(CH6_PIN, HIGH, 21000);

  bool signalValid = true;

  if (rawCh1 > 800 && rawCh1 < 2200) lastCh1 = rawCh1; else signalValid = false;
  if (rawCh6 > 800 && rawCh6 < 2200) lastCh6 = rawCh6; 
  
  if (lastCh6 > 1500) { 
    if (rawCh2 > 800 && rawCh2 < 2200) lastCh2 = rawCh2; else signalValid = false;
  } else { 
    if (rawCh3 > 800 && rawCh3 < 2200) lastCh3 = rawCh3; else signalValid = false;
    if (rawCh5 > 800 && rawCh5 < 2200) lastCh5 = rawCh5; 
  }

  if (!signalValid) {
    errorCounter++;
    if (errorCounter > 10) {
      stopMotors();
      return;
    }
  } else {
    errorCounter = 0; 
  }

  int finalThrottle = 0;
  int finalSteering = map(lastCh1, 1000, 2000, -255, 255);

  if (lastCh6 > 1500) { 
    finalThrottle = map(lastCh2, 1000, 2000, -255, 255);
  } else { 
    int rawSpeed = map(lastCh3, 1000, 2000, 0, 255);
    rawSpeed = constrain(rawSpeed, 0, 255);
    if (lastCh5 > 1500) {
      finalThrottle = -rawSpeed;
    } else {
      finalThrottle = rawSpeed;
    }
  }

  if (abs(finalThrottle) < 25) finalThrottle = 0;
  if (abs(finalSteering) < 25) finalSteering = 0;

  int leftSpeed = finalThrottle + finalSteering;
  int rightSpeed = finalThrottle - finalSteering;

  int maxVal = max(abs(leftSpeed), abs(rightSpeed));
  if (maxVal > 255) {
    leftSpeed = (leftSpeed * 255) / maxVal;
    rightSpeed = (rightSpeed * 255) / maxVal;
  }

  motorDrive(L_PWM_F, L_PWM_B, leftSpeed);
  motorDrive(R_PWM_F, R_PWM_B, rightSpeed);
  
  delay(5); 
}

void motorDrive(int fwd_pin, int rev_pin, int speed) {
  if (speed > 0) {
    ledcWrite(rev_pin, 0);
    ledcWrite(fwd_pin, speed);
  } else if (speed < 0) {
    ledcWrite(fwd_pin, 0);
    ledcWrite(rev_pin, abs(speed));
  } else {
    ledcWrite(fwd_pin, 0);
    ledcWrite(rev_pin, 0);
  }
}

void stopMotors() {
  ledcWrite(L_PWM_F, 0); 
  ledcWrite(L_PWM_B, 0);
  ledcWrite(R_PWM_F, 0); 
  ledcWrite(R_PWM_B, 0);
}
