# 📡 Dokumentasi Firmware & Panduan API — Project Stuzha

Dokumentasi teknis resmi untuk firmware mikrokontroler **ESP32 Edge AI Air Purifier & ISPU Monitor** (Project Stuzha). Panduan ini disusun untuk memudahkan seluruh anggota tim dan kolaborator (*Daffa, Garnie, Riq-Z*) dalam mengompilasi, mengunggah, memahami arsitektur kode, serta melakukan pengujian perangkat fisik.

---

## 📋 Daftar Isi
1. [Spesifikasi Hardware & Pinout Fisik](#-1-spesifikasi-hardware--pinout-fisik)
2. [Panduan Cepat Memulai (Quickstart)](#-2-panduan-cepat-memulai-quickstart)
3. [Arsitektur File & Dokumentasi API Header](#-3-arsitektur-file--dokumentasi-api-header)
4. [Logika Kendali Kipas Adaptif (PWM)](#-4-logika-kendali-kipas-adaptif-pwm)
5. [Konfigurasi WiFi & ThingSpeak Cloud](#-5-konfigurasi-wifi--thingspeak-cloud)
6. [Format Telemetri Serial Monitor](#-6-format-telemetri-serial-monitor)

---

## 🔌 1. Spesifikasi Hardware & Pinout Fisik

Firmware ini berjalan pada modul **ESP32 Dual-Core (Xtensa LX6 @ 240 MHz)** menggunakan framework **Arduino ESP32 Core v2.x/v3.x**.

### Tabel Koneksi Pin (Wajib Diikuti)

| Komponen Hardware | Pin ESP32 | Tipe Pin / Mode | Keterangan Fungsi |
|---|:---:|:---:|---|
| **Sharp GP2Y1010AU0F (Vo)** | **GPIO 34** | ADC1 Input | Membaca tegangan analog hamburan optik partikulat debu |
| **Sharp GP2Y1010AU0F (ILED)**| **GPIO 5** | Digital Output | Mengirim pulsa drive inframerah ($0.28\text{ ms}$ aktif LOW) |
| **MQ-7 (Gas CO)** | **GPIO 32** | ADC1 Input | Membaca resistansi analog sensor gas Karbon Monoksida |
| **MQ-135 (VOC/Campuran)** | **GPIO 33** | ADC1 Input | Indikator pendamping kualitas udara campuran (*proxy indoor air*) |
| **DHT22 (AM2302)** | **GPIO 4** | Digital I/O | Membaca suhu lingkungan (°C) dan kelembapan relatif (RH%) |
| **Kipas DC (PWM Control)** | **GPIO 19** | LEDC PWM Out | Mengatur kecepatan putaran motor kipas intake/exhaust via NPN transistor |
| **Industrial Buzzer** | **GPIO 18** | Tone / PWM Out | Peringatan audio alarm saat polutan mencapai kategori Berbahaya |

> [!IMPORTANT]
> **Catatan Wiring Sensor Gas:**
> * Kabel analog sensor **MQ-7 wajib terhubung ke GPIO 32**.
> * Kabel analog sensor **MQ-135 wajib terhubung ke GPIO 33**.
> * Jangan menyambungkan pin analog sensor ke pin ADC2 (GPIO 0, 2, 4, 12-15, 25-27) karena ADC2 tidak dapat membaca analog saat modul WiFi ESP32 sedang aktif. Pin 32, 33, dan 34 berada di ADC1 sehingga 100% aman dan stabil bersama WiFi.

---

## 🚀 2. Panduan Cepat Memulai (Quickstart)

### Prasyarat:
* Install IDE: [Antigravity IDE](https://antigravity.google) atau [VS Code](https://code.visualstudio.com/).
* Install Ekstensi: **PlatformIO IDE**.

### Langkah Menjalankan:
1. **Buka Proyek:** Buka folder repositori di editor, lalu pastikan terminal Anda berada di sub-folder `Program/Kode/`.
2. **Cek Port USB (`platformio.ini`):**
   Buka file [`platformio.ini`](file:///c:/Users/daffa/Documents/Project%20Stuzha/Program/Kode/platformio.ini). Pastikan port COM sesuai dengan nomor port di laptop Anda (misal `COM3` di Windows atau `/dev/ttyUSB0` di Linux):
   ```ini
   upload_port = COM3
   monitor_port = COM3
   monitor_speed = 115200
   ```
3. **Kompilasi & Upload (Flash):**
   * **Lewat GUI:** Klik icon **Centang (Build)** di status bar bawah, lalu klik icon **Panah Kanan (Upload)**.
   * **Lewat Terminal PlatformIO:**
     ```bash
     pio run --target upload
     ```
4. **Membuka Serial Monitor:**
   * Klik icon **Colokan / Monitor** di status bar bawah, atau jalankan perintah:
     ```bash
     pio device monitor
     ```

---

## 📚 3. Arsitektur File & Dokumentasi API Header

Struktur file di dalam `Program/Kode/`:
```text
Program/Kode/
├── include/
│   ├── pin_config.h     # Definisi pin hardware & level kecepatan PWM kipas
│   ├── ispu_calc.h      # Rumus matematis ISPU resmi Permen LHK No. 14 Tahun 2020
│   ├── model_pm.h       # Model TinyML Random Forest terkompilasi C untuk PM2.5
│   └── model_co.h       # Model TinyML Random Forest terkompilasi C untuk CO
├── src/
│   └── main.cpp         # Logika utama: inisialisasi, inferensi AI, dan kontrol loop
└── platformio.ini       # Konfigurasi board, dependensi library, & compiler flags
```

### A. API Kalibrasi TinyML: `model_pm.h`
Header ini berisi pohon keputusan (*Decision Trees*) Random Forest hasil pelatihan dari dataset Mendeley Data yang telah dikonversi menjadi fungsi C murni tanpa dependensi eksternal.

* **Fungsi:**
  ```c
  float model_pm_predict(const float *features);
  ```
* **Parameter Input:** Array `features` berukuran 3 elemen float:
  * `features[0]`: Konsentrasi debu mentah hasil rumus optik datasheet Sharp ($\mu g/m^3$).
  * `features[1]`: Suhu lingkungan dari DHT22 (°C).
  * `features[2]`: Kelembapan relatif dari DHT22 (RH%).
* **Nilai Kembalian:** Konsentrasi partikulat $PM_{2.5}$ murni yang telah bebas dari bias pembiasan uap air (*hygroscopic growth*) dalam satuan $\mu g/m^3$.

---

### B. API Kalibrasi TinyML: `model_co.h`
Header pohon keputusan Random Forest yang dilatih menggunakan dataset benchmark referensi UCI Machine Learning Repository.

* **Fungsi:**
  ```c
  float model_co_predict(const float *features);
  ```
* **Parameter Input:** Array `features` berukuran 3 elemen float:
  * `features[0]`: Nilai ADC mentah dari sensor MQ-7 (skala $0 - 4095$).
  * `features[1]`: Suhu lingkungan dari DHT22 (°C).
  * `features[2]`: Kelembapan relatif dari DHT22 (RH%).
* **Nilai Kembalian:** Konsentrasi gas Karbon Monoksida ($CO$) murni terkompensasi pergeseran termal (*thermal drift*) dalam satuan $\text{ppm}$ ($mg/m^3$).

---

### C. API Standarisasi Regulasi: `ispu_calc.h`
Mengimplementasikan algoritma **Piecewise Linear Interpolation** resmi Republik Indonesia berdasarkan **Permen LHK No. 14 Tahun 2020**.

* **Fungsi Sub-Indeks PM2.5:**
  ```c
  int hitung_sub_ispu_pm25(float konsentrasi_ug_m3);
  ```
  Menghitung skor sub-indeks $PM_{2.5}$ berdasarkan batas breakpoint ($15.5$, $55.4$, $150.4$, $250.4\ \mu g/m^3$).

* **Fungsi Sub-Indeks CO:**
  ```c
  int hitung_sub_ispu_co(float konsentrasi_ppm);
  ```
  Menghitung skor sub-indeks $CO$ berdasarkan batas breakpoint ($4.0$, $8.0$, $15.0$, $30.0\text{ ppm}$).

* **Penentuan Polutan Dominan & Kategori:**
  $$\text{ISPU Final} = \max(\text{Sub-ISPU}_{PM2.5},\ \text{Sub-ISPU}_{CO})$$
  ```c
  const char* get_kategori_ispu(int ispu_val);
  ```
  Mengembalikan string resmi: `"Baik"`, `"Sedang"`, `"Tidak Sehat"`, `"Sangat Tidak Sehat"`, atau `"Berbahaya"`.

---

## 🌪️ 4. Logika Kendali Kipas Adaptif (PWM)

Sistem purifikasi udara menggunakan kipas DC berperforma tinggi (**maksimum 6.400 RPM**) yang dikendalikan dengan sinyal modulasi lebar pulsa (PWM frekuensi $25\text{ kHz}$, resolusi 8-bit $0 - 255$).

Sesuai landasan teoritis pada **Jurnal ke-16 (*Atmosphere*, MDPI)** dan **Jurnal ke-17 (*JIC*, 2024)**:
* Kipas **tidak pernah dimatikan ke 0%**, karena sensor Sharp GP2Y1010AU0F tidak memiliki kipas mikro internal (bersifat pasif). Aliran udara konstan dibutuhkan untuk menarik partikel debu kamar masuk melewati rongga optik sensor secara kontinu.
* Pengaturan kecepatan dinamis terbukti memangkas konsumsi daya motor kipas hingga $70\%$ dibanding berjalan pada RPM tinggi terus-menerus.

| Kategori ISPU | Rentang Skor ISPU | Duty Cycle PWM | Estimasi RPM | Mode Aerodinamika |
|---|:---:|:---:|:---:|---|
| **Baik** | **0 – 50** | **15% (PWM 38)** | **~960 RPM** | **Silent Sampling Draft:** Suara hening ($< 30\text{ dB}$), menyedot udara kamar secara laminer ke rongga sensor. |
| **Sedang** | **51 – 100** | **15% (PWM 38)** | **~960 RPM** | **Silent Sleep Purify:** Suara hening (< 28 dB), menyedot dan menyaring sirkulasi udara kamar secara kontinu tanpa mengganggu tidur. |
| **Tidak Sehat** | **101 – 200** | **55% (PWM 140)** | **~3.520 RPM** | **Active HEPA Filtration:** Pembersihan aktif saat ruangan terdeteksi asap/debu sedang. |
| **Sangat Tidak Sehat** | **201 – 300** | **75% (PWM 191)** | **~4.800 RPM** | **Heavy Purge:** Filtrasi intensif beban polutan pekat; buzzer aktif berselang. |
| **Berbahaya** | **> 300** | **100% (PWM 255)** | **6.400 RPM** | **Emergency Max Purge:** Sirkulasi darurat putaran penuh untuk mengevakuasi polusi ekstrem. |

---

## 📶 5. Konfigurasi WiFi & ThingSpeak Cloud

Pengaturan koneksi cloud berada di bagian atas file [`src/main.cpp`](file:///c:/Users/daffa/Documents/Project%20Stuzha/Program/Kode/src/main.cpp#L7-L13):

```cpp
// Konfigurasi WiFi Hotspot
char ssid[] = "Redmi 12";            // Ganti dengan SSID WiFi Anda
char pass[] = "password_wifi_anda";  // Ganti dengan kata sandi WiFi

// Kredensial Channel ThingSpeak IoT
unsigned long myChannelNumber = 3404261;                     // Nomor Channel
const char * myWriteAPIKey    = "YOUR_THINGSPEAK_WRITE_KEY"; // Write API Key
```

* **Mode Offline Otomatis:** Jika WiFi tidak terjangkau dalam waktu 10 detik setelah dinyalakan, ESP32 akan otomatis masuk ke **Mode Offline**. Seluruh inferensi AI lokal, perhitungan ISPU, dan kendali kipas tetap berjalan $100\%$ normal tanpa internet.
* **Interval Pengiriman:** Data dikirim ke ThingSpeak setiap **20 detik** (sesuai regulasi kuota gratis ThingSpeak $15\text{ detik}$, menghasilkan $\approx 4.320$ baris data berkualitas per hari).

---

## 🖥️ 6. Format Telemetri Serial Monitor

Pada baud rate **115200**, firmware mengeluarkan data terstruktur setiap detik dengan format:

```text
[TELEMETRI] T:24.3 C | RH:50.6 % | PM2.5:[Raw:9.9 -> ML:2.5] ug/m3 | CO:[ADC:1616 -> ML:1.51 ppm] | ISPU:17 (Baik) | Dominan:CO (Karbon Monoksida) | Kipas:15 %
[TELEMETRI] T:24.4 C | RH:50.6 % | PM2.5:[Raw:461.0 -> ML:372.3] ug/m3 | CO:[ADC:1619 -> ML:1.53 ppm] | ISPU:398 (Berbahaya) | Dominan:PM2.5 (Partikulat) | Kipas:100 %
```

### Arti Kolom Telemetri:
1. `T` & `RH`: Suhu dan kelembapan real-time dari sensor DHT22.
2. `PM2.5:[Raw -> ML]`: Perbandingan debu mentah (*Raw*) terhadap hasil koreksi AI Random Forest (*ML*).
3. `CO:[ADC -> ML]`: Nilai pembacaan tegangan ADC sensor MQ-7 ($0 - 4095$) dan hasil estimasi konsentrasi gas terkalibrasi AI (ppm).
4. `ISPU`: Skor komputasi indeks kualitas udara resmi berdasarkan Permen LHK 14/2020 beserta status kategorinya.
5. `Dominan`: Parameter pencemar kritis (polutan bernilai sub-indeks tertinggi yang memicu ISPU total).
6. `Kipas`: Persentase sinyal daya PWM yang saat itu sedang dialirkan ke motor kipas.

---
*© 2026 Project Stuzha — Tim Riset Kualitas Udara Cerdas IoT & TinyML.*
