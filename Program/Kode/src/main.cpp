#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <ThingSpeak.h>
#include <DHT.h>

#include "pin_config.h"
#include "ispu_calc.h"
#include "model_pm.h"
#include "model_co.h"

// ============================================================
// KONFIGURASI WIFI & CLOUD THINGSPEAK
// ============================================================
const char* ssid     = "Redmi 12";
const char* password = "12345678";

unsigned long myChannelNumber = 3404261;
const char*   myWriteAPIKey   = "8H9F253CU87BIGFZ";

WiFiClient client;
DHT dht(PIN_DHT22, DHT22);

// ============================================================
// STRUKTUR DATA MONITORING
// ============================================================
struct AirQualityData {
    // Data Sensor Mentah
    float raw_pm_adc;
    float raw_pm_ug;     // Estimasi awal tegangan GP2Y (µg/m³) sebelum kalibrasi ML
    float raw_co_adc;
    float raw_voc_adc;
    float suhu;
    float kelembapan;

    // Output Kalibrasi TinyML (Random Forest)
    float pm25_calibrated; // µg/m³
    float co_calibrated;   // ppm

    // Standarisasi ISPU (Permen LHK No. 14 Tahun 2020)
    int sub_ispu_pm25;
    int sub_ispu_co;
    int ispu_final;
    const char* kategori_ispu;
    const char* parameter_kritis;

    // Status Aktuator
    int fan_pwm_value;
    int fan_percent;
    bool alarm_active;
} g_data;

// ============================================================
// PROTOTIPE FUNGSI
// ============================================================
void initSensorsAndPins();
void readSensors();
void runMachineLearningInference();
void calculateISPU();
void controlActuators();
void sendSerialTelemetry();
void sendThingSpeakTelemetry();
void playIndustrialAlarm();

// ============================================================
// SETUP
// ============================================================
void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println(F("\n=================================================="));
    Serial.println(F(" Project Stuzha — Edge AI ISPU Indoor Air Quality"));
    Serial.println(F(" ESP32-S3 TinyML Random Forest Firmware v2.0"));
    Serial.println(F("=================================================="));

    initSensorsAndPins();

    // Koneksi WiFi
    Serial.print(F("Menghubungkan ke WiFi: "));
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    
    int wifiTimeout = 20; // 10 detik timeout
    while (WiFi.status() != WL_CONNECTED && wifiTimeout > 0) {
        delay(500);
        Serial.print(".");
        wifiTimeout--;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.print(F("\n[WiFi] Terhubung dengan IP: "));
        Serial.println(WiFi.localIP());
    } else {
        Serial.println(F("\n[WiFi] Mode Offline (Tidak ada koneksi). Tetap menjalankan Edge AI lokal."));
    }

    ThingSpeak.begin(client);
    Serial.println(F("[System] Inisialisasi selesai. Memulai continuous inference...\n"));
}

// ============================================================
// LOOP UTAMA
// ============================================================
void loop() {
    // 1. Baca data sensor fisik (Sampling interval ~1 detik)
    static unsigned long lastSampleTime = 0;
    if (millis() - lastSampleTime >= 1000) {
        lastSampleTime = millis();

        readSensors();
        runMachineLearningInference();
        calculateISPU();
        controlActuators();
        sendSerialTelemetry();
    }

    // 2. Kirim telemetri IoT ke ThingSpeak (interval 20 detik)
    static unsigned long lastThingSpeakTime = 0;
    if (millis() - lastThingSpeakTime >= 20000) {
        lastThingSpeakTime = millis();
        sendThingSpeakTelemetry();
    }
}

// ============================================================
// IMPLEMENTASI FUNGSI
// ============================================================

void initSensorsAndPins() {
    pinMode(PIN_DUST_ILED, OUTPUT);
    digitalWrite(PIN_DUST_ILED, HIGH); // Standby HIGH (GP2Y1010 aktif LOW)
    pinMode(PIN_DUST_VO, INPUT);

    pinMode(PIN_MQ7_ANALOG, INPUT);
    pinMode(PIN_MQ135_ANALOG, INPUT);

    pinMode(PIN_BUZZER, OUTPUT);
    digitalWrite(PIN_BUZZER, LOW);

    // Inisialisasi PWM Kipas (ESP32 LEDC PWM)
    ledcSetup(FAN_PWM_CHANNEL, FAN_PWM_FREQ, FAN_PWM_RES);
    ledcAttachPin(PIN_FAN_PWM, FAN_PWM_CHANNEL);
    ledcWrite(FAN_PWM_CHANNEL, FAN_SPEED_STANDBY);

    dht.begin();
}

void readSensors() {
    // 1. Baca Suhu & Kelembapan dari DHT22
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    g_data.suhu = (!isnan(t)) ? t : 25.0f;
    g_data.kelembapan = (!isnan(h)) ? h : 50.0f;

    // 2. Baca Sensor Debu GP2Y1010AU0F (Pulsa Optik 0.28ms)
    digitalWrite(PIN_DUST_ILED, LOW);
    delayMicroseconds(280);
    int rawDust = analogRead(PIN_DUST_VO);
    delayMicroseconds(40);
    digitalWrite(PIN_DUST_ILED, HIGH);
    delayMicroseconds(9680);
    g_data.raw_pm_adc = (float)rawDust;

    // Konversi ADC ke Tegangan & Hitung Estimasi Awal Datasheet Sharp (µg/m³)
    float v_dust = (g_data.raw_pm_adc * VREF_VOLTAGE) / ADC_MAX_VALUE;
    float pm_raw_calc = (0.17f * v_dust - 0.1f) * 1000.0f;
    g_data.raw_pm_ug = (pm_raw_calc > 0.0f) ? pm_raw_calc : 0.0f;

    // 3. Baca Sensor Gas (MQ-7 untuk CO dan MQ-135 untuk VOC)
    g_data.raw_co_adc  = (float)analogRead(PIN_MQ7_ANALOG);
    g_data.raw_voc_adc = (float)analogRead(PIN_MQ135_ANALOG);
}

void runMachineLearningInference() {
    // TAHAP 1: Kalibrasi Machine Learning (Random Forest Regression)
    // Mengoreksi drift suhu & kelembapan pada sensor berbiaya rendah

    // Array Fitur PM2.5: [PM_raw (µg/m³), Suhu (°C), Kelembapan (%)]
    float input_pm[3] = { g_data.raw_pm_ug, g_data.suhu, g_data.kelembapan };
    
    // Array Fitur CO: [Raw ADC MQ-7 (0-4095), Suhu (°C), Kelembapan (%)]
    float input_co[3] = { g_data.raw_co_adc, g_data.suhu, g_data.kelembapan };

    // Eksekusi model TinyML yang berjalan offline di ESP32-S3
    g_data.pm25_calibrated = model_pm_predict(input_pm);
    g_data.co_calibrated   = model_co_predict(input_co);

    if (g_data.pm25_calibrated < 0.0f) g_data.pm25_calibrated = 0.0f;
    if (g_data.co_calibrated < 0.0f)   g_data.co_calibrated   = 0.0f;
}

void calculateISPU() {
    // TAHAP 2: Hitung Sub-Indeks ISPU per parameter (Permen LHK 14/2020)
    g_data.sub_ispu_pm25 = hitung_ispu_pm25(g_data.pm25_calibrated);
    g_data.sub_ispu_co   = hitung_ispu_co(g_data.co_calibrated);

    // TAHAP 3: Ambil Nilai Maksimum & Tentukan Parameter Kritis
    if (g_data.sub_ispu_pm25 >= g_data.sub_ispu_co) {
        g_data.ispu_final       = g_data.sub_ispu_pm25;
        g_data.parameter_kritis = "PM2.5 (Partikulat)";
    } else {
        g_data.ispu_final       = g_data.sub_ispu_co;
        g_data.parameter_kritis = "CO (Karbon Monoksida)";
    }

    g_data.kategori_ispu = get_kategori_ispu(g_data.ispu_final);
}

void controlActuators() {
    // Kendali Kipas Adaptif Tertutup (Closed-Loop Adaptive PWM)
    // Berdasarkan Kategori ISPU Resmi (Sesuai Jurnal 16, 17, 18)
    if (g_data.ispu_final <= 50) {
        // Kategori BAIK: Silent Sampling Draft (15% ~960 RPM)
        g_data.fan_pwm_value = FAN_SPEED_STANDBY;
        g_data.fan_percent   = 15;
        g_data.alarm_active  = false;
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (g_data.ispu_final <= 100) {
        // Kategori SEDANG: Gentle Filtration (35% ~2240 RPM)
        g_data.fan_pwm_value = FAN_SPEED_LOW;
        g_data.fan_percent   = 35;
        g_data.alarm_active  = false;
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (g_data.ispu_final <= 200) {
        // Kategori TIDAK SEHAT: Active Filtration (55% ~3520 RPM)
        g_data.fan_pwm_value = FAN_SPEED_MEDIUM;
        g_data.fan_percent   = 55;
        g_data.alarm_active  = false;
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (g_data.ispu_final <= 300) {
        // Kategori SANGAT TIDAK SEHAT: Heavy Purge (75% ~4800 RPM)
        g_data.fan_pwm_value = FAN_SPEED_HIGH;
        g_data.fan_percent   = 75;
        g_data.alarm_active  = true;
        playIndustrialAlarm();
    } 
    else {
        // Kategori BERBAHAYA: Max Emergency Purge (100% 6400 RPM)
        g_data.fan_pwm_value = FAN_SPEED_MAX;
        g_data.fan_percent   = 100;
        g_data.alarm_active  = true;
        playIndustrialAlarm();
    }

    ledcWrite(FAN_PWM_CHANNEL, g_data.fan_pwm_value);
}

void playIndustrialAlarm() {
    tone(PIN_BUZZER, 1200, 200);
    delay(200);
    tone(PIN_BUZZER, 800, 200);
    delay(200);
    noTone(PIN_BUZZER);
}

void sendSerialTelemetry() {
    // Format Serial Logger: Menampilkan perbandingan nilai Mentah vs Terkalibrasi ML
    Serial.printf("[TELEMETRI] T:%.1f C | RH:%.1f %% | PM2.5:[Raw:%.1f -> ML:%.1f] ug/m3 | CO:%.2f ppm | ISPU:%d (%s) | Dominan:%s | Kipas:%d %%\r\n",
                  g_data.suhu,
                  g_data.kelembapan,
                  g_data.raw_pm_ug,
                  g_data.pm25_calibrated,
                  g_data.co_calibrated,
                  g_data.ispu_final,
                  g_data.kategori_ispu,
                  g_data.parameter_kritis,
                  g_data.fan_percent);
}

void sendThingSpeakTelemetry() {
    if (WiFi.status() != WL_CONNECTED) {
        return;
    }

    ThingSpeak.setField(1, g_data.suhu);
    ThingSpeak.setField(2, g_data.kelembapan);
    ThingSpeak.setField(3, g_data.pm25_calibrated);
    ThingSpeak.setField(4, g_data.co_calibrated);
    ThingSpeak.setField(5, (float)g_data.ispu_final);
    ThingSpeak.setField(6, (float)g_data.fan_percent);
    ThingSpeak.setField(7, g_data.raw_voc_adc);

    int status = ThingSpeak.writeFields(myChannelNumber, myWriteAPIKey);
    if (status == 200) {
        Serial.println(F("[ThingSpeak] Data berhasil dikirim ke Cloud IoT (HTTP 200)."));
    } else {
        Serial.printf("[ThingSpeak] Gagal mengirim data, HTTP Error: %d\r\n", status);
    }
}
