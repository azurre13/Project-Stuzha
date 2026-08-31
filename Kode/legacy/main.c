#include <WiFi.h>
#include <WiFiClient.h>
#include <ThingSpeak.h>
#include <MQUnifiedsensor.h>
#include <DHT.h>

char ssid[] = "Redmi 12"; 
char pass[] = "12345678";

// kredensial channel thingspeak
unsigned long myChannelNumber = 3404261; 
const char * myWriteAPIKey = "8H9F253CU87BIGFZ"; 
WiFiClient client; 

// definisi pin
#define MQ2_PIN         32
#define MQ135_PIN       33 
#define DUST_SENSOR_PIN 34
#define DUST_LED_PIN    5
#define DHTPIN          4
#define BUZZER_PIN      18
#define FAN_PWM_PIN     19

#define Board              "ESP-32"
#define Voltage_Resolution  3.3
#define ADC_Bit_Resolution   12

MQUnifiedsensor MQ2(Board, Voltage_Resolution, ADC_Bit_Resolution, MQ2_PIN, "MQ-2");
MQUnifiedsensor MQ135(Board, Voltage_Resolution, ADC_Bit_Resolution, MQ135_PIN, "MQ-135");
DHT dht(DHTPIN, DHT22);

#define NOTE_HIGH 1200
#define NOTE_LOW  800

const int pwmFreq       = 25000;
const int pwmResolution = 8;
const int FAN_SPEED_LOW    = 25;   
const int FAN_SPEED_MEDIUM = 76;  
const int FAN_SPEED_MAX    = 191;  

// fungsi alarm industri
void playIndustrialAlarm() {
  tone(BUZZER_PIN, NOTE_HIGH, 400); 
  delay(400);
  tone(BUZZER_PIN, NOTE_LOW, 400);  
  delay(400);
  noTone(BUZZER_PIN);
}

void setup() {
  Serial.begin(115200);
  Serial.println(F("Memulai Sistem..."));

  // inisialisasi WiFi
  WiFi.begin(ssid, pass);
  Serial.print(F("Connecting WiFi"));
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println(F("\nWiFi Connected"));

  ThingSpeak.begin(client); 

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  ledcAttach(FAN_PWM_PIN, pwmFreq, pwmResolution);
  ledcWrite(FAN_PWM_PIN, FAN_SPEED_LOW);

  dht.begin();
  pinMode(DUST_LED_PIN, OUTPUT);
  pinMode(DUST_SENSOR_PIN, INPUT);
  digitalWrite(DUST_LED_PIN, HIGH);

  // kalibrasi sensor gas berdasarkan datasheet
  MQ2.setRegressionMethod(1);
  MQ2.setA(3697.4);
  MQ2.setB(-3.109);
  MQ2.init();
  MQ2.setR0(3.81);

  MQ135.setRegressionMethod(1);
  MQ135.setA(110.47);
  MQ135.setB(-2.862);
  MQ135.init();
  MQ135.setR0(3.6);
}

void loop() {
  // baca sensor DHT
  float suhu       = dht.readTemperature();
  float kelembaban = dht.readHumidity();
  if (isnan(suhu) || isnan(kelembaban)) {
    suhu = 0.0;
    kelembaban = 0.0;
  }

  // baca sensor gas
  MQ2.update();
  float gas = MQ2.readSensor();
  if (gas > 4000.0) gas = 4000.0;

  MQ135.update();
  float eco2 = MQ135.readSensor() + 400.0;
  if (eco2 > 4000.0) eco2 = 4000.0;

  // baca sensor debu optik
  digitalWrite(DUST_LED_PIN, LOW);
  delayMicroseconds(280);
  int rawADC = analogRead(DUST_SENSOR_PIN);
  delayMicroseconds(40);
  digitalWrite(DUST_LED_PIN, HIGH);
  delayMicroseconds(9680);

  float tegangan = rawADC * (3.3 / 4095.0);
  float debu_ug  = (0.17 * tegangan - 0.1) * 1000.0;
  if (debu_ug < 0) debu_ug = 0.00;

  int persenKipas = 0;
  String statusUdara = "";

  // logika adaptif aktuator
  if (gas >= 600.0 || eco2 >= 2000.0) {
    persenKipas = 75; 
    statusUdara = "BAHAYA UDARA!";
    
    ledcWrite(FAN_PWM_PIN, FAN_SPEED_MAX);
    playIndustrialAlarm();
  }
  else if (debu_ug >= 150.0 || gas >= 150.0 || eco2 >= 1000 ) {
    persenKipas = 30; 
    statusUdara = "UDARA KOTOR";
    
    ledcWrite(FAN_PWM_PIN, FAN_SPEED_MEDIUM);
    noTone(BUZZER_PIN);
    digitalWrite(BUZZER_PIN, LOW);
  }
  else {
    persenKipas = 10; 
    statusUdara = "UDARA NORMAL";
    
    ledcWrite(FAN_PWM_PIN, FAN_SPEED_LOW);
    noTone(BUZZER_PIN);
    digitalWrite(BUZZER_PIN, LOW);
  }

  // print data logger serial
  static unsigned long lastMillisSerial = 0;
  if (millis() - lastMillisSerial >= 1000) {
    lastMillisSerial = millis();
    Serial.printf("%.1f,%.1f,%.0f,%.0f,%.0f,%d,%s\r\n", 
                  suhu, kelembaban, gas, eco2, debu_ug, persenKipas, statusUdara.c_str());
  }

  // kirim ke thingspeak tiap 20 detik
  static unsigned long lastMillisThingSpeak = 0;
  if (millis() - lastMillisThingSpeak >= 20000) { 
    lastMillisThingSpeak = millis();

    if (WiFi.status() != WL_CONNECTED) {
      Serial.println("QOS,WiFi Terputus, Mencoba Reconnect...");
      WiFi.reconnect();  
      return;            
    }

    ThingSpeak.setField(1, suhu);       
    ThingSpeak.setField(2, kelembaban); 
    ThingSpeak.setField(3, gas);       
    ThingSpeak.setField(4, eco2);       
    ThingSpeak.setField(5, debu_ug);    
    ThingSpeak.setField(6, persenKipas);

    long rssi = WiFi.RSSI();
    unsigned long t_start = millis(); 

    int tsCode = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
    
    unsigned long t_end = millis();
    unsigned long latency = t_end - t_start;

    Serial.printf("QOS,%lu,%d,%lu,%ld\r\n", millis(), tsCode, latency, rssi);
  }
}