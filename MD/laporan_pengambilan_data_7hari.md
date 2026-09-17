# Laporan Pengambilan Data Uji Kontinu 7 Hari Project Stuzha (10–17 September 2026)

Laporan resmi evaluasi empiris operasional firmware v4.0.0 (`a945ea070fcc`) pada ESP32 Dev Module berdasarkan data mentah CSV ThingSpeak Channel 3480764. Seluruh angka dihitung langsung dari berkas CSV tanpa manipulasi data asli.

---

## 1. Identitas Berkas dan Ringkasan Durasi

- **Berkas CSV Sumber:** [`Program/data/downloads/stuzha_dataset_20260910-20260917.csv`](../Program/data/downloads/stuzha_dataset_20260910-20260917.csv)
- **Waktu Awal Pengujian:** 10 September 2026 pukul 20:01:51 WIB
- **Waktu Akhir Pengujian:** 17 September 2026 pukul 22:33:57 WIB
- **Total Durasi Kalender:** **170,535 Jam (7 Hari 2 Jam 32 Menit)**
- **Total Baris Data Mentah:** **30.260 rekaman telemetri**
- **Skrip Analisis Reproducible:** [`Program/analisis_sesi_7hari.py`](../Program/analisis_sesi_7hari.py)
- **Folder Hasil Turunan:** [`Program/data/hasil_7hari/`](../Program/data/hasil_7hari/)

---

## 2. Rincian Sesi Booting dan Rekonsiliasi Restart

Data 30.260 baris terdiri atas 5 sesi booting yang tercatat pada field status `b`. Sesuai prinsip kehati-hatian metodologis, penyebab fisik eksternal di luar mikrokontroler tidak diasumsikan secara spekulatif, melainkan dicatat murni berdasarkan kode register reset perangkat keras (`r`) dan jeda stempel waktu:

| No | Boot ID | Jumlah Sampel | Waktu Mulai (WIB) | Waktu Selesai (WIB) | Uptime Tercatat | Kode Reset (`r`) | Data Teramati pada Transisi |
|:--:|---|---:|---|---|---:|:---:|---|
| **1** | `c43d4d72` | 13 | 10 Sep 20:01:51 | 10 Sep 20:05:51 | 0,033 – 0,100 jam | 1 (`ESP_RST_POWERON`) | Sesi awal observasi pasca-booting pertama (durasi 0,10 jam). |
| — | *Transisi 1* | — | 10 Sep 20:05:51 | 10 Sep 20:06:28 | Jeda: 37,0 detik | — | Jeda waktu 37,0 detik; register reset Boot 2 mencatat `r=1` (`POWERON`). |
| **2** | `f27413f0` | **27.022** | **10 Sep 20:06:28** | **17 Sep 03:21:46** | **0,005 – 151,259 jam** | **1 (`ESP_RST_POWERON`)** | **Sesi operasional kontinu terpanjang (151,26 jam non-stop).** |
| — | *Transisi 2* | — | 17 Sep 03:21:46 | 17 Sep 03:22:08 | Jeda: 22,0 detik | — | Jeda waktu 22,0 detik; register reset Boot 3 mencatat `r=1` (`POWERON`). |
| **3** | `2ee94f8f` | 2.842 | 17 Sep 03:22:08 | 17 Sep 20:21:25 | 0,005 – 16,993 jam | 1 (`ESP_RST_POWERON`) | Sesi operasional kontinu selama 16,99 jam. |
| — | *Transisi 3* | — | 17 Sep 20:21:25 | 17 Sep 20:22:00 | Jeda: 35,0 detik | — | Jeda waktu 35,0 detik; register reset Boot 4 mencatat `r=7` (`TG0WDT_SYS`). |
| **4** | `9f05ffe4` | 18 | 17 Sep 20:22:00 | 17 Sep 20:27:41 | 0,005 – 0,100 jam | 7 (`ESP_RST_TG0WDT_SYS`) | Sesi transien singkat 18 sampel pasca-reset watchdog. |
| — | *Transisi 4* | — | 17 Sep 20:27:41 | 17 Sep 20:28:32 | Jeda: 51,0 detik | — | Jeda waktu 51,0 detik; register reset Boot 5 mencatat `r=1` (`POWERON`). |
| **5** | `37cbdc54` | 365 | 17 Sep 20:28:32 | 17 Sep 22:33:57 | 0,005 – 2,095 jam | 1 (`ESP_RST_POWERON`) | Sesi penutupan observasi hingga akhir hari ke-7. |
| **Total** | **5 Sesi** | **30.260** | **10 Sep 20:01:51** | **17 Sep 22:33:57** | **170,535 jam** | — | **Ambang batas 168 jam terpenuhi secara akumulatif.** |

**Prinsip Non-Spekulatif Analisis Restart:**  
Telemetri mikrokontroler merekam nilai kode register reset `r` dan jeda stempel waktu. Tanpa instrumen perekam tegangan eksternal independen (*external power logger* / *oscilloscope capture trap*), penyebab fisik eksternal (seperti fluktuasi tegangan listrik jala-jala, gangguan suplai adaptor daya, atau intervensi mekanis kabel) **tidak dapat dipastikan secara definitif**. Demikian pula untuk kode `r=7` (*Task Watchdog Timer Group 0*), reset terjadi karena pewaktu pengawas kedaluwarsa akibat perulangan loop tertahan, namun rute pemblokiran fungsi perangkat lunak spesifik tidak tersimpan pada telemetri jarak jauh. Oleh karena itu, laporan ini tidak membuat asumsi spekulatif mengenai penyebab fisik restart.

---

## 3. Metrik Reliabilitas Sistem Tertanam

### A. Kestabilan Heap Memori
- **Sesi Utama (`f27413f0`, 27.022 Sampel):**
  - Heap Awal: 201.348 bytes
  - Heap Akhir: 199.132 bytes
  - Heap Minimum: 196.728 bytes
  - Heap Maksimum: 201.348 bytes
  - Deviasi Standar Heap: **86,41 bytes**
- **Keseluruhan 7 Hari (Semua 5 Sesi, 30.260 Sampel):**
  - Heap Minimum: 196.728 bytes
  - Heap Maksimum: 201.372 bytes
  - Heap Rata-rata: 199.148,93 bytes
  - Deviasi Standar Heap: **100,64 bytes**
- **Evaluasi Objektif:** Sisa memori RAM statis berfluktuasi dalam rentang sempit tanpa tren degradasi progresif, menunjukkan kestabilan alokasi array statis ring buffer dan inferensi C++.

### B. Rekonsiliasi Telemetri Cloud
| Parameter Telemetri | Sesi Utama (`f27413f0`) | Keseluruhan 7 Hari (Semua 5 Sesi) |
|---|:---:|:---:|
| Total Slot Terbentang (*Slot Span*) | 27.226 slot | 30.692 slot |
| Feed Diterima di Cloud | 27.022 baris | 30.260 baris |
| **Kelengkapan Slot (*Slot Completeness*)** | **99,251%** | **98,592%** |
| Percobaan Pengiriman (*Attempts*) | 27.135 kali | 30.596 kali |
| Kegagalan Pengiriman (*Failures*) | 118 kali | 337 kali |
| **Tingkat Keberhasilan Percobaan** | **99,565%** | **98,899%** |
| Slot Tidak Dicoba (*Skipped*) | 91 slot | 101 slot |

*Keterangan:* Slot skipped terjadi saat mikrokontroler mendeteksi status koneksi Wi-Fi belum siap pada interval pengiriman sehingga slot dilewati tanpa melakukan blocking.

---

## 4. Analisis Kejadian Khusus: Saturasi Optik 13 September 2026

Pada **13 September 2026 pukul 02:13:06 WIB**, teramati satu kejadian pembacaan ekstrem pada sensor partikulat GP2Y:
```text
Timestamp WIB: 2026-09-13T02:13:06+07:00
GP2Y Raw ADC: 4095.00 (Batas maksimum ADC 12-bit)
MQ-7 Raw ADC: 2611.29
Status Raw: STZ4|v=4.0.0|h=a945ea070fcc|m=d7f32c60|b=f27413f0|u=194815312|r=1|l=5|f=22930|s=194555|n=100|j=1|i=5|e=9708,23,32|q=9740|k=199140|a=4095.00,2611.29|d=30.2,4.07,68.4,100|c=0
```
- **Pengamatan Flags (`22930`):** Menandakan aktivasi bit flag terprogram: $16384 \text{ (GP mean jenuh)} + 4096 + 2048 + 256 + 128 \text{ (model invalid)} + 16 + 2 \text{ (raw rail GP)}$.
- **Respon Firmware Terprogram:** Nilai ISPU instan disetel `NaN`, Kategori disetel `0.0`, buzzer polusi dimatikan, dan perintah kendali kipas dinaikkan ke Level 5 darurat (`PWM = 85.10%`).
- **Pola Pemulihan (*Smooth Decay*):**
  - 02:13:26 WIB: Nilai GP ADC kembali ke 986,48; perintah kipas diturunkan bertahap ke Level 4 (`PWM = 50.20%`, Kategori 2.0).
  - 02:13:46 WIB: Perintah kipas kembali normal ke Level 2 (`PWM = 14.90%`, Kategori 2.0).

---

## 5. Rangkuman Statistik Parameter Sensor dan Model

### A. Tabel Statistik Komparatif
| Parameter | Sesi Kontinu Utama (`f27413f0`, 27.022 Sampel) | | | | | Keseluruhan 7 Hari (30.260 Sampel) | | | | |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| | Min | Mean | Median | Max | Std | Min | Mean | Median | Max | Std |
| Suhu (°C) | 22,20 | 25,92 | 25,40 | 31,50 | 1,99 | 22,20 | 26,02 | 25,50 | 31,50 | 2,07 |
| Kelembaban Relatif (% RH) | 39,50 | 55,51 | 55,70 | 75,50 | 7,25 | 39,50 | 55,64 | 55,90 | 75,50 | 6,95 |
| GP2Y Raw ADC (12-bit) | 937,87 | 1.033,07 | 1.021,94 | 4.095,00 | 49,21 | 937,87 | 1.039,00 | 1.029,32 | 4.095,00 | 50,54 |
| MQ-7 Raw ADC (12-bit) | 2.103,42 | 2.559,36 | 2.536,57 | 3.743,83 | 198,58 | 2.103,42 | 2.581,19 | 2.558,86 | 3.743,83 | 200,22 |
| MQ-135 Raw ADC (12-bit) | 1.179,41 | 1.616,25 | 1.597,59 | 3.403,95 | 234,56 | 1.179,41 | 1.642,06 | 1.652,44 | 3.403,95 | 236,96 |
| Estimasi $\text{PM}_{2.5}$ ($\mu\text{g/m}^3$) | 20,46 | 33,80 | 30,67 | 80,25 | 5,64 | 20,46 | 34,42 | 31,04 | 80,25 | 5,80 |
| Estimasi $\text{CO}$ ($\text{ppm}$) | 2,68 | 4,05 | 3,81 | 7,44 | 0,80 | 2,68 | 4,13 | 3,89 | 7,44 | 0,80 |
| Indeks ISPU Instan | 56,22 | 73,70 | 69,40 | 126,16 | 7,95 | 56,22 | 74,44 | 70,29 | 126,16 | 7,98 |
| Commanded Fan PWM (%) | 14,90 | 14,96 | 14,90 | 85,10 | 0,80 | 14,90 | 14,96 | 14,90 | 85,10 | 0,75 |
| Free Heap RAM (bytes) | 196.728 | 199.145 | 199.140 | 201.348 | 86,41 | 196.728 | 199.149 | 199.140 | 201.372 | 100,64 |

### B. Distribusi Kategori ISPU (Semua 30.260 Sampel)
- **Kategori 2 (Sedang, ISPU 51–100):** **30.080 sampel (99,405%)**
- **Kategori 3 (Tidak Sehat, ISPU 101–200):** **179 sampel (0,592%)** — teramati mengalami kenaikan temporer melampaui batas 100 pada periode 11 dan 15 September.
- **Kategori 0 (Invalid / Sesar Saturasi):** **1 sampel (0,003%)** — kejadian saturasi optik rel 4095 pada 13 September 02:13:06 WIB.

### C. Distribusi Perintah Kipas (*Commanded PWM*)
- **Level 2 (PWM 14,90%):** **30.034 sampel (99,253%)**
- **Level 3 (PWM 21,96%):** **224 sampel (0,740%)**
- **Level 4 (PWM 50,20%):** **1 sampel (0,003%)**
- **Level 5 (PWM 85,10%):** **1 sampel (0,003%)**

---

## 6. Pembahasan Konteks Operasional dan Keterbatasan Pengamatan

1. **Status Fisik Motor Kipas:** Sinyal pada field 6 mencatat *commanded duty cycle* dari algoritma kontrol. Karena konektor motor kipas dilepas secara fisik selama periode istirahat malam demi kenyamanan akustik penghuni, status putaran mekanis motor berstatus tidak diketahui (*unknown physical state*). Penelitian ini tidak mengevaluasi laju pengiriman udara bersih (*CADR*) atau efisiensi pembersihan partikulat.
2. **Dinamika Suhu Ruangan dan Penyejuk Udara (AC):** Variasi suhu kamar (22,20°C–31,50°C) dibahas berdasarkan catatan logbook aktivitas pemilik: suhu tinggi bertepatan dengan ketiadaan penghuni saat AC dimatikan, dan suhu stabil rendah (22°C–25°C) saat penghuni berada di kamar dengan AC menyala. Mengingat T dan RH adalah fitur input model TinyML, korelasinya dengan estimasi model dipahami sebagai interaksi fitur komputasi, bukan pembuktian kompensasi *drift* fisik sensor.

---

## 7. Kesimpulan Evaluasi 7 Hari

1. **Kelayakan Deployment Operasional Edge:** Evaluasi 170,535 jam kalender (10–17 September 2026) membuktikan kemampuan mikrokontroler ESP32 dalam mengeksekusi inferensi TinyML Random Forest C++ statis dan interpolasi sub-indeks regulasi Permen LHK 14/2020 secara deterministik di kamar tidur hunian nyata (30.260 rekaman telemetri terkumpul).
2. **Keandalan Telemetri dan Kestabilan Memori:** Secara kumulatif 7 hari, kelengkapan slot mencapai 98,59% (30.260 feed dari 30.692 slot) dan keberhasilan percobaan pengiriman mencapai 98,90% (30.259 sukses dari 30.596 percobaan; 337 kegagalan jaringan, 101 slot dilewati saat Wi-Fi belum siap). Memori heap RAM berfluktuasi stabil pada rentang 196.728–201.372 bytes dengan deviasi standar 100,64 bytes tanpa kebocoran memori progresif. Sesi kontinu terpanjang berjalan 151,26 jam non-stop (27.022 sampel, Boot `f27413f0`, std heap 86,41 bytes, kelengkapan slot 99,25%).
3. **Pencatatan Restart Berbasis Fakta:** Tercatat 4 transisi restart (3 kali kode `r=1` / *power-on*, 1 kali kode `r=7` / *task watchdog timer*) dengan jeda 22–51 detik. Penyebab fisik di balik kejadian restart tidak dipastikan secara spekulatif karena sistem tidak memiliki instrumentasi pencatat daya/tegangan eksternal independen.
4. **Validasi Respon Sesar Terprogram:** Kejadian saturasi optik rel 4095 pada 13 September 02:13:06 WIB membuktikan aktivasi aturan proteksi firmware terprogram (Kategori 0, ISPU NaN, perintah kipas Level 5 darurat lalu *smooth decay* bertahap ke Level 4 dan Level 2).
5. **Integritas Batasan Metrologi:** Angka estimasi PM2.5 dan CO beroperasi pada skala transfer nominal eksperimental dan tidak diklaim sebagai konsentrasi tervalidasi sebelum dilakukan uji komparatif berpasangan dengan instrumen acuan laboratorium bersertifikat. Perintah kecepatan kipas dibangkitkan secara reguler, namun tidak ada klaim efisiensi pembersihan udara (CADR) karena ketiadaan instrumentasi takometer mekanis.
