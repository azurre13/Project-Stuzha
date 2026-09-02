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
    // Data Sensor Mentah & Pra-Kalkulasi Fisik
    float raw_pm_adc;
    float pm_raw_ug;       // Estimasi awal rumus datasheet GP2Y (µg/m³)
    float raw_co_adc;
    float rs_r0_ratio;     // Rasio resistansi MQ-7 (Rs/R0)
    float raw_voc_adc;
    float suhu;
    float kelembapan;

    // Output Kalibrasi TinyML (Random Forest)
    float pm25_calibrated; // µg/m³ (Bebas bias kelembapan)
    float co_calibrated;   // ppm / mg/m³

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
        Serial.println(F("\n[WiFi] Terhubung dengan IP: ") + WiFi.localIP().toString());
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

    // Inisialisasi PWM Kipas (ESP32 Core v3 LEDC)
    ledcAttach(PIN_FAN_PWM, FAN_PWM_FREQ, FAN_PWM_RES);
    ledcWrite(PIN_FAN_PWM, FAN_SPEED_STANDBY);

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

    // Konversi Tegangan & Rumus Fisik Datasheet Sharp GP2Y (Jurnal 3):
    // Vout = ADC * (3.3 / 4095.0)
    // PM_raw = (0.17 * Vout - 0.1) * 1000.0 (µg/m³)
    float v_dust = (g_data.raw_pm_adc * 3.3f) / 4095.0f;
    float pm_raw = (0.17f * v_dust - 0.1f) * 1000.0f;
    g_data.pm_raw_ug = (pm_raw > 0.0f) ? pm_raw : 0.0f;

    // 3. Baca Sensor Gas MQ-7 (CO) & Hitung Rasio Resistansi Rs/R0:
    g_data.raw_co_adc = (float)analogRead(PIN_MQ7_ANALOG);
    float v_co = (g_data.raw_co_adc * 3.3f) / 4095.0f;
    if (v_co < 0.1f) v_co = 0.1f;
    // Rs = RL * (Vcc - Vout) / Vout (dengan RL = 10kOhm)
    float rs_co = 10.0f * (3.3f - v_co) / v_co;
    // R0 di udara bersih ruangan tipikal ~10kOhm
    g_data.rs_r0_ratio = rs_co / 10.0f;

    // 4. Baca Sensor Gas VOC (MQ-135)
    g_data.raw_voc_adc = (float)analogRead(PIN_MQ135_ANALOG);
}

void runMachineLearningInference() {
    // TAHAP 1: Kalibrasi Machine Learning (Random Forest Regression)
    // Mengoreksi drift suhu & pembiasan uap air (hygroscopic growth) pada sensor murah

    // Fitur PM: [PM_raw (µg/m³), Suhu (°C), Kelembapan (%)] — Skala 100% Matched!
    float input_pm[3] = { g_data.pm_raw_ug, g_data.suhu, g_data.kelembapan };

    // Fitur CO: [Rs/R0 Ratio, Suhu (°C), Kelembapan (%)] — Skala 100% Matched!
    float input_co[3] = { g_data.rs_r0_ratio, g_data.suhu, g_data.kelembapan };

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
    // Berdasarkan Kategori ISPU Resmi
    if (g_data.ispu_final <= 50) {
        // Kategori BAIK
        g_data.fan_pwm_value = FAN_SPEED_STANDBY;
        g_data.fan_percent   = 10;
        g_data.alarm_active  = false;
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (g_data.ispu_final <= 100) {
        // Kategori SEDANG
        g_data.fan_pwm_value = FAN_SPEED_LOW;
        g_data.fan_percent   = 30;
        g_data.alarm_active  = false;
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (g_data.ispu_final <= 200) {
        // Kategori TIDAK SEHAT
        g_data.fan_pwm_value = FAN_SPEED_MEDIUM;
        g_data.fan_percent   = 60;
        g_data.alarm_active  = false;
        noTone(PIN_BUZZER);
        digitalWrite(PIN_BUZZER, LOW);
    } 
    else if (g_data.ispu_final <= 300) {
        // Kategori SANGAT TIDAK SEHAT
        g_data.fan_pwm_value = FAN_SPEED_HIGH;
        g_data.fan_percent   = 85;
        g_data.alarm_active  = true;
        playIndustrialAlarm();
    } 
    else {
        // Kategori BERBAHAYA
        g_data.fan_pwm_value = FAN_SPEED_MAX;
        g_data.fan_percent   = 100;
        g_data.alarm_active  = true;
        playIndustrialAlarm();
    }

    // Secondary Safety Guard (MQ-135 VOC Boost)
    // Jika gas VOC campuran terdeteksi sangat pekat, paksa kecepatan kipas naik
    if (g_data.raw_voc_adc > 2500.0f && g_data.fan_percent < 85) {
        g_data.fan_pwm_value = FAN_SPEED_HIGH;
        g_data.fan_percent   = 85;
    }

    ledcWrite(PIN_FAN_PWM, g_data.fan_pwm_value);
}

void playIndustrialAlarm() {
    tone(PIN_BUZZER, 1200, 200);
    delay(200);
    tone(PIN_BUZZER, 800, 200);
    delay(200);
    noTone(PIN_BUZZER);
}

void sendSerialTelemetry() {
    // Format Serial Logger (Menampilkan nilai Mentah vs Terkalibrasi ML):
    Serial.printf("[TELEMETRI] T:%.1f C | RH:%.1f %% | PM[Raw:%.1f -> ML:%.1f ug/m3] | CO[Rs/R0:%.2f -> ML:%.2f ppm] | ISPU:%d (%s) | Kritis:%s | Fan:%d %%\r\n",
                  g_data.suhu,
                  g_data.kelembapan,
                  g_data.pm_raw_ug,
                  g_data.pm25_calibrated,
                  g_data.rs_r0_ratio,
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
