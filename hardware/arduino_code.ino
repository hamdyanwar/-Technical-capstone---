// تعريف مكتبة البلوتوث والبنات رقم 4 و 5
#include <SoftwareSerial.h>
SoftwareSerial bluetooth(4, 5); 

// تعريف الحساسات والبازر والحد المسموح
const int gasSensor = A0;
const int soundSensor = A1; 
const int buzzer = 10;
const int threshold = 200;

// متغيرات التحكم والتوقيت
unsigned long alarmEndTime = 0;      
String currentCommand = "NONE";       
unsigned long lastSendTime = 0;      

void setup() {
  // تشغيل منافذ الاتصال وإعداد الحساسات والبازر
  Serial.begin(9600);
  bluetooth.begin(9600);
  pinMode(gasSensor, INPUT);
  pinMode(soundSensor, INPUT);
  pinMode(buzzer, OUTPUT);
  noTone(buzzer);
}

void loop() {
  unsigned long currentMillis = millis();

  // إرسال قراءات الحساسات للكمبيوتر والموبايل كل نصف ثانية
  if (currentMillis - lastSendTime >= 500) {
    int gasVal = analogRead(gasSensor);
    int soundVal = analogRead(soundSensor);
    
    Serial.print("DATA,Gas:");
    Serial.print(gasVal);
    Serial.print(",Sound:");
    Serial.println(soundVal);
    
    bluetooth.print("Gas: ");
    bluetooth.print(gasVal);
    bluetooth.print(" | Sound: ");
    bluetooth.println(soundVal);
    
    lastSendTime = currentMillis;
  }

  // فحص استقبال الأوامر من الكمبيوتر أو البلوتوث
  if (Serial.available() > 0 || bluetooth.available() > 0) {
    String command = Serial.available() > 0 ? Serial.readStringUntil('\n') : bluetooth.readStringUntil('\n');
    command.trim(); 
    if (command == "CMD:RED_GAS" || command == "CMD:RED_PRESSURE" || command == "CMD:GREEN") {
      currentCommand = command;
      alarmEndTime = currentMillis + 3000; 
    }
  }

  // التحكم في البازر بناءً على أوامر السوفتوير أو القراءات المحلية
  if (currentMillis < alarmEndTime) {
    if (currentCommand == "CMD:RED_GAS") tone(buzzer, 1500);             
    else if (currentCommand == "CMD:RED_PRESSURE") tone(buzzer, 300);              
    else if (currentCommand == "CMD:GREEN") noTone(buzzer);                 
  } else {
    int localGas = analogRead(gasSensor);
    int localSound = analogRead(soundSensor);
    if (localGas < threshold) tone(buzzer, 1500);
    else if (localSound < threshold) tone(buzzer, 300);
    else noTone(buzzer);
  }

  delay(10); 
}
