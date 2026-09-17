# Laporan Pengambilan Data Uji Kontinu 7 Hari Project Stuzha (10–17 September 2026)

Laporan resmi evaluasi empiris operasional firmware v4.0.0 (`a945ea070fcc`) pada ESP32 Dev Module berdasarkan data mentah CSV ThingSpeak Channel 3480764.

---

## 1. Identitas Berkas dan Ringkasan Durasi

- **Berkas CSV Sumber:** [`Program/data/downloads/stuzha_dataset_20260910-20260917.csv`](../Program/data/downloads/stuzha_dataset_20260910-20260917.csv)
- **Waktu Awal Pengujian:** 10 September 2026 pukul 20:01:51 WIB
- **Waktu Akhir Pengujian:** 17 September 2026 pukul 22:33:57 WIB
- **Total Durasi Operasional:** **170,53 Jam (7 Hari 2 Jam 32 Menit)**
- **Total Baris Data Mentah:** **30.260 rekaman telemetri**
- **Skrip Analisis Reproducible:** [`Program/analisis_sesi_7hari.py`](../Program/analisis_sesi_7hari.py)
- **Folder Hasil Turunan:** [`Program/data/hasil_7hari/`](../Program/data/hasil_7hari/)

---

## 2. Rincian Sesi Booting dan Rekonsiliasi Restart

Data 30.260 baris terdiri atas 5 sesi booting yang dipisahkan secara faktual tanpa menyamarkan restart:

| No | Boot ID | Jumlah Sampel | Waktu Mulai (WIB) | Waktu Selesai (WIB) | Uptime Tercatat | Kode Reset (`r`) | Keterangan & Analisis Transisi |
|:--:|---|---:|---|---|---:|:---:|---|
| **1** | `c43d4d72` | 13 | 10 Sep 20:01:51 | 10 Sep 20:05:51 | 0,03 – 0,10 jam | 1 (`POWERON`) | Sesi uji commissioning pasca-upload USB pada PC. |
| — | *Transisi 1* | — | 10 Sep 20:05:51 | 10 Sep 20:06:28 | Jeda: 37,0 detik | — | Pemindahan kabel USB dari PC ke catu daya permanen kamar. |
| **2** | `f27413f0` | **27.022** | **10 Sep 20:06:28** | **17 Sep 03:21:46** | **0,01 – 151,26 jam** | 1 (`POWERON`) | **Sesi kontinu utama: 151,26 jam (6 Hari 7 Jam 15 Menit) non-stop tanpa reset.** |
| — | *Transisi 2* | — | 17 Sep 03:21:46 | 17 Sep 03:22:08 | Jeda: 22,0 detik | — | Fluktuasi daya sesaat dini hari (*power flicker/brownout*); ESP32 restart otomatis. |
| **3** | `2ee94f8f` | 2.842 | 17 Sep 03:22:08 | 17 Sep 20:21:25 | 0,01 – 16,99 jam | 1 (`POWERON`) | Sesi pasca-flicker berjalan lancar selama 16,99 jam. |
| — | *Transisi 3* | — | 17 Sep 20:21:25 | 17 Sep 20:22:00 | Jeda: 35,0 detik | — | Reset sistem akibat watchdog timer (`TG0WDT_SYS_RESET`). |
| **4** | `9f05ffe4` | 18 | 17 Sep 20:22:00 | 17 Sep 20:27:41 | 0,01 – 0,10 jam | 7 (`TG0WDT_SYS`) | Sesi singkat pasca-watchdog. |
| — | *Transisi 4* | — | 17 Sep 20:27:41 | 17 Sep 20:28:32 | Jeda: 51,0 detik | — | Hard power-cycle (cabut-colok adaptor) oleh pemilik untuk pemulihan. |
| **5** | `37cbdc54` | 365 | 17 Sep 20:28:32 | 17 Sep 22:33:57 | 0,01 – 2,10 jam | 1 (`POWERON`) | Sesi penutupan uji 7 hari berjalan stabil hingga akhir observasi. |
| **Total** | **5 Sesi** | **30.260** | **10 Sep 20:01:51** | **17 Sep 22:33:57** | **> 170 jam** | — | **Ambang batas 168 jam terpenuhi secara akumulatif.** |

> **Catatan Ilmiah:** Sesi operasional kontinu terpanjang adalah **151,26 jam (Boot `f27413f0`)**, bukan 168 jam tanpa reboot. Tiga kejadian restart pada tanggal 17 September tercatat secara transparan dengan rincian kode reset dan durasi jeda di atas.

---

## 3. Metrik Reliabilitas Sistem Tertanam (Sesi Utama `f27413f0`)

### A. Kestabilan Heap Memori
- **Heap Awal:** 201.348 bytes
- **Heap Akhir:** 199.132 bytes
- **Heap Minimum:** 196.728 bytes
- **Heap Maksimum:** 201.348 bytes
- **Deviasi Standar Heap:** **86,41 bytes**
- **Evaluasi:** Memori berfluktuasi dalam rentang sempit tanpa tren penurunan progresif, membuktikan kestabilan struktur ring buffer RAM statis 1.440 menit dan inferensi C++.

### B. Rekonsiliasi Telemetri Cloud
- **Rentang Slot Telemetri:** Slot 1 hingga 27.226 (Total: 27.226 slot)
- **Feed Diterima di Cloud:** **27.022 baris**
- **Kelengkapan Slot (*Slot Completeness*):** **99,25%** ($27.022 / 27.226 \times 100\%$)
- **Percobaan Pengiriman (*Attempts*):** 27.135 kali
- **Kegagalan Jaringan (*Failures*):** 118 kali
- **Tingkat Keberhasilan Percobaan (*Attempt Success Rate*):** **99,57%** ($(27.135 - 118) / 27.135 \times 100\%$)
- **Slot Tidak Dicoba (*Skipped*):** **91 slot** (terjadi saat mikrokontroler mendeteksi status koneksi Wi-Fi belum terhubung, sehingga slot dilewati tanpa *blocking*).
- **Rekonsiliasi Persamaan:** $\text{Percobaan (27.135)} + \text{Skipped (91)} = \mathbf{27.226\text{ Slot}}$.

---

## 4. Analisis Kejadian Khusus: Saturasi Optik 13 September 2026

Pada **13 September 2026 pukul 02:13:06 WIB**, teramati satu kejadian sesar sensor partikulat GP2Y:
```text
Timestamp WIB: 2026-09-13T02:13:06+07:00
GP2Y Raw ADC: 4095.00 (Saturasi rel penuh ADC 12-bit)
MQ-7 Raw ADC: 2611.29
Status Raw: STZ4|v=4.0.0|h=a945ea070fcc|m=d7f32c60|b=f27413f0|u=194815312|r=1|l=5|f=22930|s=194555|n=100|j=1|i=5|e=9708,23,32|q=9740|k=199140|a=4095.00,2611.29|d=30.2,4.07,68.4,100|c=0
```
- **Analisis Flags (`22930`):** $16384 \text{ (GP mean jenuh)} + 4096 + 2048 + 256 + 128 \text{ (model invalid)} + 16 + 2 \text{ (raw rail GP)}$.
- **Respon Proteksi:** ISPU instan disetel `NaN`, Kategori disetel `0.0`, alarm polusi dimatikan (*prevent false alarm*), dan perintah kipas dinaikkan ke darurat **Level 5 (`PWM = 85.10%`)**.
- **Pemulihan Bertahap (*Smooth Decay*):** 
  - 02:13:26 WIB: GP ADC pulih ke 986,48; perintah kipas melambat ke Level 4 (`PWM = 50.20%`, Kategori 2.0).
  - 02:13:46 WIB: Perintah kipas kembali normal ke Level 2 (`PWM = 14.90%`, Kategori 2.0).

---

## 5. Rangkuman Statistik Parameter Lingkungan & Model

### A. Sesi Utama (`f27413f0`, 27.022 Sampel)
| Parameter | Minimum | Rata-rata | Median (50%) | Maksimum | Standar Deviasi |
|---|---:|---:|---:|---:|---:|
| **Suhu (°C)** | 22,20 | 25,92 | 25,40 | 31,50 | 1,99 |
| **Kelembaban (% RH)** | 39,50 | 55,51 | 55,70 | 75,50 | 7,25 |
| **PM2.5 Nominal (µg/m³)** | 20,46 | 33,80 | 30,67 | 80,25 | 5,64 |
| **CO Nominal (ppm)** | 2,68 | 4,05 | 3,81 | 7,44 | 0,80 |
| **ISPU Instan** | 56,22 | 73,70 | 69,40 | 126,16 | 7,95 |
| **Commanded Fan PWM (%)** | 14,90 | 14,96 | 14,90 | 85,10 | 0,80 |
| **MQ-135 Raw ADC** | 1.179,41 | 1.616,25 | 1.597,59 | 3.403,95 | 234,56 |
| **GP2Y Raw ADC** | 937,87 | 1.033,07 | 1.021,94 | 4.095,00 | 49,21 |
| **MQ-7 Raw ADC** | 2.103,42 | 2.559,36 | 2.536,57 | 3.743,83 | 198,58 |
| **Free Heap (bytes)** | 196.728 | 199.145 | 199.140 | 201.348 | 86,41 |

### B. Keseluruhan Dataset 7 Hari (30.260 Sampel)
| Parameter | Minimum | Rata-rata | Median (50%) | Maksimum | Standar Deviasi |
|---|---:|---:|---:|---:|---:|
| **Suhu (°C)** | 22,20 | 26,02 | 25,50 | 31,50 | 2,07 |
| **Kelembaban (% RH)** | 39,50 | 55,64 | 55,90 | 75,50 | 6,95 |
| **PM2.5 Nominal (µg/m³)** | 20,46 | 34,42 | 31,04 | 80,25 | 5,80 |
| **CO Nominal (ppm)** | 2,68 | 4,13 | 3,89 | 7,44 | 0,80 |
| **ISPU Instan** | 56,22 | 74,44 | 70,29 | 126,16 | 7,98 |
| **Commanded Fan PWM (%)** | 14,90 | 14,96 | 14,90 | 85,10 | 0,75 |
| **MQ-135 Raw ADC** | 1.179,41 | 1.642,06 | 1.652,44 | 3.403,95 | 236,96 |
| **GP2Y Raw ADC** | 937,87 | 1.039,00 | 1.029,32 | 4.095,00 | 50,54 |
| **MQ-7 Raw ADC** | 2.103,42 | 2.581,19 | 2.558,86 | 3.743,83 | 200,22 |
| **Free Heap (bytes)** | 196.728 | 199.149 | 199.140 | 201.372 | 100,64 |

### C. Distribusi Kategori Kualitas Udara (Semua Boot, 30.260 Sampel)
- **Kategori 2.0 (Sedang, ISPU 51–100):** **30.080 sampel (99,405%)**
- **Kategori 3.0 (Tidak Sehat, ISPU 101–200):** **179 sampel (0,592%)**
- **Kategori 0.0 (Invalid / Saturasi Optik):** **1 sampel (0,003%)**

---

## 6. Pembahasan Kondisi Operasional Lingkungan

1. **Status Kipas Fisik:** Sinyal kendali dilaporkan sebagai *commanded PWM*. Karena kabel daya kipas sebagian besar dicabut pada malam hari oleh pemilik untuk kenyamanan akustik tidur, status putaran mekanik aktual berstatus *unknown* (tidak dicatat sensor RPM).
2. **Pola Suhu AC:** Peningkatan suhu kamar hingga 31,5°C merefleksikan catatan logbook pemilik saat meninggalkan kamar dalam durasi panjang dengan AC dimatikan. Saat penghuni berada di kamar dengan AC menyala, suhu berkisar 22,2°C–25,5°C. Korelasi T/RH dengan output model dipengaruhi oleh penggunaan T/RH sebagai fitur input Random Forest, bukan bukti kalibrasi fisik sensor.
