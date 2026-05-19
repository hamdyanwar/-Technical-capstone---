/*
 * ==========================================================================
 *   MED-GUARD — Unifed Arduino Hardware Controller (المتحكم الموحد للهاردوير)
 *   البروتوكول ثنائي الاتجاه المتوافق تماماً مع جميع إصدارات الجسر البرمجي
 * ==========================================================================
 *   التوصيل (Wiring):
 *     - Arduino Uno / Nano / Mega
 *     - Red LED     → Pin 9  (مقاومة 220Ω)
 *     - Green LED   → Pin 8  (مقاومة 220Ω)
 *     - Buzzer      → Pin 10
 *     - Gas Sensor (MQ-135/2)  → Analog Pin A0
 *     - Sound/Pressure Sensor  → Analog Pin A1
 *
 *   بروتوكولات الاستقبال المدعومة (Serial RX Protocols):
 *     1. بروتوكول الأوامر المباشرة (Direct Commands):
 *        - CMD:RED_GAS      (خطر غاز: LED أحمر + نغمة حادة)
 *        - CMD:RED_PRESSURE (خطر ضغط: LED أحمر + نغمة متقطعة غليظة)
 *        - CMD:GREEN        (آمن تماماً: LED أخضر)
 *
 *     2. بروتوكول قراءات السوفتوير (Software Telemetry Parser):
 *        - GAS:<value>      مثال: GAS:72.5
 *        - PRESSURE:<value> مثال: PRESSURE:38.2
 *
 *   بروتوكول الإرسال للسوفتوير (Serial TX Protocol):
 *     - يرسل كل 500 ملي ثانية: DATA,Gas:<analog_val>,Sound:<analog_val>
 * ==========================================================================
 */

// ─── تعريف أطراف التوصيل (Pins) ───
const int greenLed   = 8;
const int redLed     = 9;
const int buzzer     = 10;
const int gasSensor   = A0;
const int soundSensor = A1;

// ─── حدود التنبيه للقراءات المباشرة ───
const float GAS_MAX_THRESHOLD      = 50.0;  // تنبيه إذا تجاوزت السوفتوير
const float PRESSURE_MAX_THRESHOLD = 40.0;  // تنبيه إذا تجاوزت السوفتوير

// ─── متغيرات التحكم وتخزين الحالات ───
float swGasLevel = 0.0;
float swPressureLevel = 0.0;

unsigned long softwareAlarmEndTime = 0;
String currentSoftwareAlarm = "NONE";
unsigned long lastSendTime = 0;
String inputBuffer = "";

void setup() {
  Serial.begin(9600);

  pinMode(greenLed,   OUTPUT);
  pinMode(redLed,     OUTPUT);
  pinMode(buzzer,     OUTPUT);
  pinMode(gasSensor,   INPUT);
  pinMode(soundSensor, INPUT);

  // الحالة الافتراضية عند التشغيل: نظام سليم (أخضر)
  digitalWrite(greenLed, HIGH);
  digitalWrite(redLed,   LOW);
  noTone(buzzer);

  Serial.println("MED-GUARD Unified Hardware Protocol v2.0 - Ready!");
}

void loop() {
  unsigned long currentMillis = millis();

  // 1. إرسال قراءات المستشعرات المحلية للكمبيوتر كل 500 ملي ثانية
  if (currentMillis - lastSendTime > 500) {
    int gasVal = analogRead(gasSensor);
    int soundVal = analogRead(soundSensor);
    
    Serial.print("DATA,Gas:");
    Serial.print(gasVal);
    Serial.print(",Sound:");
    Serial.println(soundVal);
    
    lastSendTime = currentMillis;
  }

  // 2. استقبال ومعالجة البيانات القادمة عبر الـ Serial
  while (Serial.available() > 0) {
    char c = (char)Serial.read();
    if (c == '\n') {
      processIncomingCommand(inputBuffer, currentMillis);
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }

  // 3. اتخاذ القرار والتحكم بالأجهزة (ترتيب الأولويات)
  
  // -- الأولوية الأولى: أوامر السوفتوير المباشرة (Active Commands within 3.5 seconds) --
  if (currentMillis < softwareAlarmEndTime) {
    if (currentSoftwareAlarm == "CMD:RED_GAS") {
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      tone(buzzer, 2000); // صوت حاد ومستمر لإنذار الغاز
    }
    else if (currentSoftwareAlarm == "CMD:RED_PRESSURE") {
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      // نغمة غليظة ومتقطعة
      tone(buzzer, 300);
      delay(100);
      noTone(buzzer);
      delay(100);
    }
    else if (currentSoftwareAlarm == "CMD:GREEN") {
      digitalWrite(greenLed, HIGH);
      digitalWrite(redLed,   LOW);
      noTone(buzzer);
    }
  }
  // -- الأولوية الثانية: قراءات السوفتوير التناظرية الواردة (Telemetry Limits) --
  else if (swGasLevel > GAS_MAX_THRESHOLD) {
    digitalWrite(redLed, HIGH);
    digitalWrite(greenLed, LOW);
    int gasTone = map((int)swGasLevel, 0, 100, 200, 1500);
    tone(buzzer, gasTone);
    delay(150);
  }
  else if (swPressureLevel > PRESSURE_MAX_THRESHOLD) {
    digitalWrite(redLed, HIGH);
    digitalWrite(greenLed, LOW);
    tone(buzzer, 1000);
    delay(100);
    noTone(buzzer);
    delay(100);
  }
  // -- الأولوية الثالثة: الحماية الذاتية المحلية المستقلة (Offline Fallback Sensors) --
  else {
    currentSoftwareAlarm = "NONE";
    int localGas = analogRead(gasSensor);
    int localSound = analogRead(soundSensor);

    // قيم أقل من 45 تعني سحب تيار أو قصر أو خطر مبرمج من المستشعرات
    if (localGas < 45) {
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      tone(buzzer, 2000); // صوت حاد للغاز محلياً
    }
    else if (localSound < 45) {
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      tone(buzzer, 300); // صوت غليظ للبريشر محلياً
    }
    else {
      // كل المؤشرات آمنة تماماً
      digitalWrite(greenLed, HIGH);
      digitalWrite(redLed,   LOW);
      noTone(buzzer);
    }
  }

  delay(30); // استقرار المعالج
}

// ─── دالة فك التشفير ومعالجة النصوص البرمجية الواردة ───
void processIncomingCommand(String cmd, unsigned long currentMillis) {
  cmd.trim();
  if (cmd.length() == 0) return;

  // 1. فك تشفير الأوامر المباشرة
  if (cmd == "CMD:RED_GAS" || cmd == "CMD:RED_PRESSURE" || cmd == "CMD:GREEN") {
    currentSoftwareAlarm = cmd;
    softwareAlarmEndTime = currentMillis + 3500; // صلاحية التنبيه 3.5 ثوانٍ
    
    Serial.print("✔ Command Ack: ");
    Serial.println(cmd);
  }
  // 2. فك تشفير القيم التناظرية
  else if (cmd.startsWith("GAS:")) {
    swGasLevel = cmd.substring(4).toFloat();
    Serial.print("✔ Gas Telemetry Ack: ");
    Serial.println(swGasLevel);
  }
  else if (cmd.startsWith("PRESSURE:")) {
    swPressureLevel = cmd.substring(9).toFloat();
    Serial.print("✔ Pressure Telemetry Ack: ");
    Serial.println(swPressureLevel);
  }
}
