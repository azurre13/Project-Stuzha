# Laporan Pengambilan Data Uji Kontinu Project Stuzha (10–15 September 2026)

Laporan hasil observasi operasional firmware v4.0.0 (`a945ea070fcc`) pada ESP32 Dev Module untuk penulisan jurnal ilmiah.

---

## 1. Ringkasan Durasi dan File Dataset

- **Nama File Dataset:** [`Program/data/downloads/stuzha_dataset_20260910-20260915.csv`](file:///c:/Users/daffa/Documents/Project%20Stuzha/Program/data/downloads/stuzha_dataset_20260910-20260915.csv)
- **Waktu Mulai Sesi Aktif:** 10 September 2026 pukul 20:06:28 WIB
- **Waktu Snapshot Terakhir:** 15 September 2026 pukul 23:50:55 WIB
- **Durasi Berjalan:** **123,75 Jam (5 Hari 3 Jam 45 Menit)**
- **Target Total:** 168 Jam (7 Hari Penuh)
- **Sisa Waktu Menuju 7 Hari:** $\approx$ 44,25 Jam ($\approx$ 1,8 Hari / sampai 17 September 2026 pukul 20:06 WIB)
- **Total Sampel Terkirim:** **22.117 sampel** (rata-rata 1 sampel per 20,1 detik)

---

## 2. Metrik Reliabilitas dan Stabilitas Sistem Embedded

| Parameter | Nilai Observasi | Evaluasi Ilmiah untuk Jurnal |
|---|---|---|
| **Reboot / Crash Count** | **0 kali reboot** | Sistem berjalan 123,75 jam non-stop tanpa hang (*single boot ID: `f27413f0`*) |
| **Konsumsi Memori RAM (Heap)** | Awal: 199.392 bytes<br>Akhir: 199.124 bytes<br>Min: 196.728 bytes | **Zero Memory Leak.** Alokasi statis dan ring buffer 24 jam di RAM terbukti stabil |
| **Keberhasilan Transmisi IoT** | Percobaan: 22.199<br>Gagal: 87<br>**Success Rate: 99,61%** | Protokol koneksi nirkabel ThingSpeak sangat andal |
| **Cakupan Rerata 24 Jam (`d`)** | **100% Coverage** | Ring buffer 1.440 menit terisi penuh dan konsisten menghitung rerata bergerak |

---

## 3. Rangkuman Statistik Kualitas Udara (22.117 Sampel)

| Parameter Sensor & Model | Nilai Min | Rata-rata (Mean) | Median (50%) | Nilai Max | Standar Deviasi |
|---|---:|---:|---:|---:|---:|
| **Suhu Ruangan (°C)** | 22,20 | 25,92 | 25,40 | 31,10 | 1,97 |
| **Kelembaban Relatif (% RH)** | 39,50 | 55,48 | 55,70 | 75,50 | 7,02 |
| **GP2Y Raw ADC** | 812,40 | 985,12 | 972,30 | 1.420,10 | 54,20 |
| **MQ-7 Raw ADC** | 2.102,15 | 2.584,30 | 2.590,10 | 3.120,40 | 115,80 |
| **MQ-135 Raw ADC (VOC/Gas)** | 1.179,41 | 1.585,02 | 1.525,15 | 3.403,95 | 241,57 |
| **Estimasi PM2.5 (µg/m³)** | 20,46 | 33,29 | 30,01 | 80,25 | 5,74 |
| **Estimasi CO (ppm)** | 2,68 | 3,92 | 3,70 | 7,44 | 0,74 |
| **ISPU Instan Gabungan** | 56,22 | 72,86 | 68,27 | 126,16 | 7,79 |
| **Perintah Fan PWM (%)** | 14,90 | 14,98 | 14,90 | 85,10 | 0,88 |

---

## 4. Rincian Harian (Daily Breakdown)

| Tanggal | Jumlah Sampel | Suhu (°C) | RH (%) | PM2.5 (µg/m³) | CO (ppm) | Rerata ISPU | Maks ISPU | Kategori Dominan |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **10 Sep 2026** (Malam) | 699 | 25,24 | 52,50 | 29,15 | 3,52 | 67,10 | 70,43 | Sedang (L2) |
| **11 Sep 2026** | 4.301 | 25,62 | 53,60 | 31,15 | 3,45 | 69,61 | 126,16 | Sedang (Lonjakan L3) |
| **12 Sep 2026** | 4.288 | 26,08 | 57,87 | 31,47 | 3,51 | 70,02 | 104,58 | Sedang (L2) |
| **13 Sep 2026** | 4.300 | 25,74 | 56,46 | 30,21 | 3,59 | 68,44 | 104,55 | Sedang (L2) |
| **14 Sep 2026** | 4.256 | 26,58 | 56,94 | 34,41 | 4,78 | 76,60 | 107,37 | Sedang (L2) |
| **15 Sep 2026** | 4.273 | 25,68 | 53,03 | 39,95 | 4,36 | 80,63 | 125,97 | Sedang (Lonjakan L3) |

---

## 5. Distribusi Kategori ISPU & Respon Kipas PWM

- **Kategori Sedang (ISPU 51–100):** **99,19%** (21.938 sampel) $\rightarrow$ Perintah Kipas PWM Level 2 (14,90%).
- **Kategori Tidak Sehat (ISPU 101–200):** **0,81%** (179 sampel) $\rightarrow$ Perintah Kipas PWM Level 3 (21,96%) hingga Level 4/5 (50,2% / 85,1%).
- **Analisis Aktuasi:** Mikrokontroler berhasil mengeksekusi kendali bertingkat dinamis (*smooth decay*) saat terjadi lonjakan polusi pada tanggal 11 dan 15 September tanpa membebani memori CPU.

---

## 6. Kesimpulan dan Rekomendasi Jurnal

1. **Apakah data sudah cukup?**
   - **Untuk Penulisan Naskah:** **SUDAH SANGAT CUKUP.** Volume 22.117 baris data yang mencakup 5 hari siklus diurnal sudah lebih dari cukup untuk mengisi tabel hasil, grafik time-series, evaluasi reliabilitas firmware, dan korelasi multi-polutan di Bab 4 jurnal.
   - **Untuk Klaim 7 Hari (168 Jam):** Biarkan alat menyala sekitar **1,8 hari lagi** sampai tanggal 17 September 2026 pukul 20:00 WIB agar target 168 jam tercapai secara sempurna.
2. **Langkah Kerja:** Sambil alat tetap menyala di meja, naskah jurnal (Bab 1 Pendahuluan, Bab 2 Metodologi, Bab 3 Arsitektur Sistem, dan draf awal Bab 4) sudah bisa langsung mulai disusun sekarang.
