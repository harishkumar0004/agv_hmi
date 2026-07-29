/*
  Hotel Robot TTP223 Touch Emotion Controller

  Hardware:
    Arduino Nano
    TTP223 capacitive touch sensor

  Wiring:
    TTP223 VCC  -> Nano 5V or 3.3V
    TTP223 GND  -> Nano GND
    TTP223 OUT  -> Nano D2

  Serial commands sent to Raspberry Pi:
    NORMAL
    HAPPY
    EXCITED
    ANGRY
    SLEEPY
*/

const byte TOUCH_PIN = 2;

const unsigned long BAUD_RATE = 115200;
const unsigned long DEBOUNCE_MS = 35;
const unsigned long LONG_TOUCH_MS = 3000;
const unsigned long TAP_SETTLE_MS = 450;
const unsigned long RAPID_TAP_WINDOW_MS = 2000;
const unsigned long MAX_TAP_MS = 600;

bool stableTouchState = false;
bool lastRawTouchState = false;
bool longTouchSent = false;

unsigned long lastRawChangeAt = 0;
unsigned long touchStartedAt = 0;
unsigned long lastTapAt = 0;
unsigned long tapWindowStartedAt = 0;

byte tapCount = 0;

void sendCommand(const char *command) {
  Serial.println(command);
}

void resetTapState() {
  tapCount = 0;
  lastTapAt = 0;
  tapWindowStartedAt = 0;
}

void registerShortTap(unsigned long now) {
  if (tapCount == 0 || now - tapWindowStartedAt > RAPID_TAP_WINDOW_MS) {
    tapCount = 0;
    tapWindowStartedAt = now;
  }

  tapCount++;
  lastTapAt = now;

  if (tapCount >= 4) {
    sendCommand("ANGRY");
    resetTapState();
  }
}

void classifyTapSequence(unsigned long now) {
  if (tapCount == 0 || now - lastTapAt < TAP_SETTLE_MS) {
    return;
  }

  if (tapCount == 1) {
    sendCommand("HAPPY");
  } else if (tapCount == 2) {
    sendCommand("EXCITED");
  } else if (tapCount >= 4) {
    sendCommand("ANGRY");
  }

  resetTapState();
}

void handleTouchPressed(unsigned long now) {
  touchStartedAt = now;
  longTouchSent = false;
}

void handleTouchReleased(unsigned long now) {
  unsigned long touchDuration = now - touchStartedAt;

  if (!longTouchSent && touchDuration <= MAX_TAP_MS) {
    registerShortTap(now);
  }
}

void updateTouchState() {
  unsigned long now = millis();
  bool rawTouchState = digitalRead(TOUCH_PIN) == HIGH;

  if (rawTouchState != lastRawTouchState) {
    lastRawTouchState = rawTouchState;
    lastRawChangeAt = now;
  }

  if (now - lastRawChangeAt < DEBOUNCE_MS || rawTouchState == stableTouchState) {
    return;
  }

  stableTouchState = rawTouchState;

  if (stableTouchState) {
    handleTouchPressed(now);
  } else {
    handleTouchReleased(now);
  }
}

void updateLongTouch() {
  if (!stableTouchState || longTouchSent) {
    return;
  }

  if (millis() - touchStartedAt >= LONG_TOUCH_MS) {
    sendCommand("SLEEPY");
    longTouchSent = true;
    resetTapState();
  }
}

void setup() {
  pinMode(TOUCH_PIN, INPUT);
  Serial.begin(BAUD_RATE);
  delay(1200);
  sendCommand("NORMAL");
}

void loop() {
  unsigned long now = millis();

  updateTouchState();
  updateLongTouch();
  classifyTapSequence(now);
}
