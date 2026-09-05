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

// Level Kecepatan Kipas (PWM 8-bit: 0 - 255) — Kipas 6400 RPM (Jurnal 16, 17, 18)
#define FAN_SPEED_STANDBY      38   // 15% (Kategori Baik - Silent Sampling Draft ~960 RPM)
#define FAN_SPEED_LOW          51   // 20% (Kategori Sedang - Quiet Night Sleep Purify ~1280 RPM, < 38 dB)
#define FAN_SPEED_MEDIUM      140   // 55% (Kategori Tidak Sehat - Active Filtration ~3520 RPM)
#define FAN_SPEED_HIGH        191   // 75% (Kategori Sangat Tidak Sehat - Heavy Purge ~4800 RPM)
#define FAN_SPEED_MAX         255   // 100% (Kategori Berbahaya - Max Emergency 6400 RPM)

#endif // PIN_CONFIG_H
