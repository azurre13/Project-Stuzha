#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

// ============================================================
// DEFINISI PIN HARDWARE (ESP32-S3) — PROJECT STUZHA
// ============================================================

// Pin Sensor (Sesuai Kabel Fisik Terpasang di ESP32)
#define PIN_MQ7_ANALOG      32   // Sensor Gas CO (Kabel Fisik -> Pin 32)
#define PIN_MQ135_ANALOG    33   // Sensor Gas VOC/Campuran (Kabel Fisik -> Pin 33)
#define PIN_DUST_VO         34   // Sensor Partikulat GP2Y1010AU0F (ADC Out -> Pin 34)
#define PIN_DUST_ILED        5   // Sensor Partikulat GP2Y1010AU0F (LED Pulse Drive)
#define PIN_DHT22            4   // Sensor Suhu & Kelembapan DHT22

// Pin Aktuator
#define PIN_FAN_PWM         19   // Kipas DC Adaptive Filtration (PWM)
#define PIN_BUZZER          18   // Buzzer Alarm

// Konfigurasi ADC
#define ADC_MAX_VALUE       4095.0f
#define VREF_VOLTAGE           3.3f

// Konfigurasi PWM Kipas (ESP32 LEDC)
#define FAN_PWM_FREQ        25000
#define FAN_PWM_RES             8
#define FAN_PWM_CHANNEL         0

// Level Kecepatan Kipas Khusus Kipas Industri 6200 RPM 12V 1.65A (PWM 8-bit: 0 - 255)
#define FAN_SPEED_STANDBY      33   // 13% (~806 RPM - Kategori Baik: Ultra-Silent Standby)
#define FAN_SPEED_LOW          38   // 15% (~930 RPM - Kategori Sedang: Silent Sleep Purify, Max Batas Nyaman)
#define FAN_SPEED_MEDIUM       56   // 22% (~1364 RPM - Kategori Tidak Sehat: Active Clean, Adem & Tidak Bising!)
#define FAN_SPEED_HIGH        128   // 50% (~3100 RPM - Kategori Sangat Tidak Sehat: Heavy Purge)
#define FAN_SPEED_MAX         217   // 85% (~5270 RPM - Kategori Berbahaya: Max Emergency Purge)

#endif // PIN_CONFIG_H
