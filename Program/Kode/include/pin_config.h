#ifndef PIN_CONFIG_H
#define PIN_CONFIG_H

// ============================================================
// DEFINISI PIN HARDWARE (ESP32-S3) — PROJECT STUZHA
// ============================================================

// Pin Sensor
#define PIN_MQ7_ANALOG      32   // Sensor Gas CO (ADC)
#define PIN_MQ135_ANALOG    33   // Sensor Gas VOC/Campuran (ADC)
#define PIN_DUST_VO         34   // Sensor Partikulat GP2Y1010AU0F (ADC Out)
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

// Level Kecepatan Kipas (PWM 8-bit: 0 - 255)
#define FAN_SPEED_STANDBY      25   // ~10% (Kategori Baik)
#define FAN_SPEED_LOW          76   // ~30% (Kategori Sedang)
#define FAN_SPEED_MEDIUM      153   // ~60% (Kategori Tidak Sehat)
#define FAN_SPEED_HIGH        217   // ~85% (Kategori Sangat Tidak Sehat)
#define FAN_SPEED_MAX         255   // 100% (Kategori Berbahaya)

#endif // PIN_CONFIG_H
