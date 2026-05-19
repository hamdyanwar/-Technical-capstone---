const int gasSensor = A0;
const int soundSensor = A1;
const int greenLed = 8;
const int redLed = 9;
const int buzzer = 10;

void setup() {
  Serial.begin(9600);
  
  pinMode(gasSensor, INPUT);
  pinMode(soundSensor, INPUT);
  
  pinMode(greenLed, OUTPUT);
  pinMode(redLed, OUTPUT);
  pinMode(buzzer, OUTPUT);
  
  digitalWrite(greenLed, LOW);
  digitalWrite(redLed, LOW);
}

void loop() {
  // 1. قراءة السنسورات وإرسالها للسوفتوير
  int gasVal = analogRead(gasSensor);
  int soundVal = analogRead(soundSensor);
  
  Serial.print("DATA,Gas:");
  Serial.print(gasVal);
  Serial.print(",Sound:");
  Serial.println(soundVal);

  // 2. استقبال أوامر السوفتوير للتحكم في الليدات والبازر
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "CMD:RED_GAS") {
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      
      // التزمير مرتين بسرعة
      tone(buzzer, 1500); // الزمرة الأولى
      delay(150);        
      noTone(buzzer);
      delay(100);         // فاصل سريع
      
      tone(buzzer, 1500); // الزمرة الثانية
      delay(150);        
      noTone(buzzer);     // يقفل لوحده
      
      digitalWrite(redLed, LOW);
    }
    else if (command == "CMD:RED_PRESSURE") {
      digitalWrite(redLed, HIGH);
      digitalWrite(greenLed, LOW);
      
      // التزمير مرتين بسرعة
      tone(buzzer, 300);  // الزمرة الأولى
      delay(150);        
      noTone(buzzer);
      delay(100);         // فاصل سريع
      
      tone(buzzer, 300);  // الزمرة الثانية
      delay(150);        
      noTone(buzzer);     // يقفل لوحده
      
      digitalWrite(redLed, LOW);
    }
    else if (command == "CMD:GREEN") {
      digitalWrite(greenLed, HIGH);
      digitalWrite(redLed, LOW);
      noTone(buzzer);
    }
  }

  delay(200); 
}
