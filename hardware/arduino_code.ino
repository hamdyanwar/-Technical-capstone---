/*
 * ==========================================================================
 *   MED-GUARD — Unified Non-Blocking Hardware Controller (كود أردوينو المطور)
 *   التعديل البرمجي الاحترافي: إزالة التأخيرات المانعة (Non-Blocking) لضمان
 *   إرسال واستقبال البيانات في الوقت الحقيقي دون أي تجميد (Freezing).
 * ==========================================================================
 *   التوصيل (Wiring):
 *     - A0 : Gas Sensor (مستشعر الغاز)
 *     - A1 : Pressure/Sound Sensor (مستشعر الضغط/الصوت)
 *     - Pin 8 : Green LED (الليد الأخضر)
 *     - Pin 9 : Red LED (الليد الأحمر)
 *     - Pin 10: Buzzer (البازر)
 * ==========================================================================
 */

// ==========================================
// تعريف البنات (Pins) بناءً على التوصيلة الخاصة بك
// ==========================================
const int gasSensor = A0;
const int soundSensor = A1; // نستخدمه هنا كمستشعر للبريشر/الصوت
const int greenLed = 8;
const int redLed = 9;
const int buzzer = 10;

// ==========================================
// متغيرات التوقيت الذكية لمنع التجمد (Non-Blocking Timing)
// ==========================================
unsigned long alarmEndTime = 0;      // وقت انتهاء الإنذار الحالي
String currentCommand = "NONE";       // الأمر الحالي النشط
unsigned long lastSendTime = 0;      // وقت آخر إرسال للبيانات للكمبيوتر
const unsigned long sendInterval = 500; // إرسال القراءات كل 500 ملي ثانية

void setup() {
  // فتح الاتصال مع السوفتوير (البايثون) بسرعة 9600
  Serial.begin(9600);
  
  // إعداد حساسات الإدخال
  pinMode(gasSensor, INPUT);
  pinMode(soundSensor, INPUT);
  
  // إعداد الليدات والبازر كمخرجات
  pinMode(greenLed, OUTPUT);
  pinMode(redLed, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  // التأكد من إطفاء كل شيء في البداية (حالة آمنة افتراضية)
  digitalWrite(greenLed, HIGH); // تشغيل الليد الأخضر كدليل على أن النظام يعمل وآمن
  digitalWrite(redLed, LOW);
  noTone(buzzer);
}

void loop() {
  unsigned long currentMillis = millis();

  // ==========================================
  // 1. قراءة السنسورات وإرسالها للسوفتوير كل 500 ملي ثانية (بدون تأخير)
  // ==========================================
  if (currentMillis - lastSendTime >= sendInterval) {
    int gasVal = analogRead(gasSensor);
    int soundVal = analogRead(soundSensor);
    
    // إرسال البيانات بشكل يفهمه كود البايثون
    Serial.print("DATA,Gas:");
    Serial.print(gasVal);
    Serial.print(",Sound:");
    Serial.println(soundVal);
    
    lastSendTime = currentMillis;
  }

  // ==========================================
  // 2. استقبال أوامر السوفتوير للتحكم في الليدات والبازر
  // ==========================================
  if (Serial.available() > 0) {
    // قراءة الأمر القادم من البايثون
    String command = Serial.readStringUntil('\n');
    command.trim(); // تنظيف المسافات الزائدة

    if (command == "CMD:RED_GAS" || command == "CMD:RED_PRESSURE" || command == "CMD:GREEN") {
      currentCommand = command;
      alarmEndTime = currentMillis + 3000; // تشغيل الحالة المطلوبة لمدة 3 ثوانٍ
    }
  }

  // ==========================================
  // 3. محرك الحالة الذكي (State Machine) لتشغيل الإنذارات بدون تجميد الأردوينو
  // ==========================================
  if (currentMillis < alarmEndTime) {
    // ---- هناك أمر نشط من السوفتوير حالياً ولم تنته الـ 3 ثواني ----
    if (currentCommand == "CMD:RED_GAS") {
      digitalWrite(redLed, HIGH);     // تشغيل الليد الأحمر
      digitalWrite(greenLed, LOW);    // إطفاء الليد الأخضر
      tone(buzzer, 1500);             // تشغيل البازر بصوت حاد للغاز
    }
    else if (currentCommand == "CMD:RED_PRESSURE") {
      digitalWrite(redLed, HIGH);     // تشغيل الليد الأحمر
      digitalWrite(greenLed, LOW);    // إطفاء الليد الأخضر
      tone(buzzer, 300);              // تشغيل البازر بصوت غليظ للبريشر
    }
    else if (currentCommand == "CMD:GREEN") {
      digitalWrite(greenLed, HIGH);   // تشغيل الليد الأخضر
      digitalWrite(redLed, LOW);      // إطفاء الليد الأحمر
      noTone(buzzer);                 // إيقاف البازر
    }
  } 
  else {
    // ---- انتهت الـ 3 ثواني الخاصة بأمر السوفتوير، ننتقل لوضع الحماية الذاتية المحلّي (Fallback) ----
    int localGas = analogRead(gasSensor);
    int localSound = analogRead(soundSensor);

    if (localGas < 45) { // إنذار غاز محلي
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      tone(buzzer, 1500);
    } 
    else if (localSound < 45) { // إنذار ضغط محلي
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      tone(buzzer, 300);
    } 
    else {
      // كل القراءات آمنة
      digitalWrite(greenLed, HIGH);   // الليد الأخضر منور دليل الأمان
      digitalWrite(redLed, LOW);
      noTone(buzzer);
    }
  }

  // انتظار بسيط جداً لاستقرار المعالج ولا يؤثر على التدفق
  delay(10); 
}
