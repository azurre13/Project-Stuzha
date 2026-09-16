# Catatan Audit untuk Astra Sesi 6 — Project Stuzha

Dokumen ini disiapkan sebagai pengantar dan ringkasan audit lengkap untuk Astra (Sesi 6). Semua instruksi audit perbaikan dari Astra akan dikerjakan langsung oleh Antigravity pada repositori.

---

## 1. Identitas Sistem & Status Firmware Aktif

- **Versi Repositori:** 4.0.0 (Revisi 10 September 2026)
- **Firmware Terpasang:** Build `a945ea070fcc` (Target `esp32dev`, framework Arduino-ESP32 2.0.17)
- **Model TinyML:** Model PM (`model_pm.h`) & CO (`model_co.h`) terkunci, Model Pair Hash: `d7f32c60`
- **Boot ID Aktif:** `f27413f0`
- **Waktu Mulai Berjalan:** 10 September 2026 pukul 20:06:28 WIB
- **Waktu Snapshot Terkini:** 15 September 2026 pukul 23:50:55 WIB
- **Durasi Sesi Kontinu:** **123,75 Jam (5 Hari 3 Jam 45 Menit)** non-stop
- **Status Stabilitas:** **0 kali reboot** (`r=1`, *POWERON_RESET* tunggal), **Zero memory leak** (RAM Heap awal 199.392 bytes, akhir 199.124 bytes)
- **Konektivitas IoT:** ThingSpeak Channel 3480764, total kirim 22.199 kali, gagal 87 kali (**Tingkat Keberhasilan: 99,61%**)
- **Cakupan Rerata 24 Jam (`d`):** 100% (*full coverage* ring RAM 1.440 menit)

---

## 2. Fakta Lapangan Kondisi Fisik Pengujian (Catatan Pemilik)

Berikut adalah catatan jujur kondisi lingkungan fisik selama 5 hari pengujian untuk rujukan interpretasi data:

1. **Kondisi Kipas Fisik (Aktuator):**
   - Kabel daya motor kipas 12V sebagian besar **TIDAK dinyalakan / dicabut fisiknya** dari soket board, dan hanya dinyalakan sebentar di beberapa kesempatan.
   - Alasan pemilik: Pertimbangan kebisingan suara kipas (*acoustic comfort*) saat tidur di malam hari dan saat beraktivitas di kamar.
   - Perilaku Firmware: Karena tidak ada pin *tachometer / RPM feedback*, mikrokontroler ESP32 tetap menghasilkan sinyal PWM normal (rata-rata 14,90% Level 2, sesekali naik ke 21,96% Level 3 saat polusi naik) dan mencatatnya ke cloud sebagai *commanded PWM*. Namun, sirkulasi udara di dalam casing beroperasi secara konveksi pasif alami.
2. **Kondisi Suhu Ruangan & Pola AC:**
   - Kamar dilengkapi pendingin ruangan (AC).
   - **Saat Suhu Naik (puncak 28,0°C – 31,1°C):** Menandakan pemilik sedang bepergian/keluar rumah dalam durasi lama sehingga AC kamar dimatikan.
   - **Saat Suhu Rendah/Stabil (23,0°C – 25,5°C):** Menandakan pemilik berada di dalam kamar dengan AC menyala.
3. **Penempatan Sensor:**
   - Sensor GP2Y1010, MQ-7, MQ-135, dan DHT22 berada di bilik bawah (ruang intake), sebelum filter karbon kotak dan potongan filter mobil non-HEPA.

---

## 3. Rangkuman Data Telemetri 5 Hari (22.117 Sampel)

Berkas dataset tersimpan di: [`Program/data/downloads/stuzha_dataset_20260910-20260915.csv`](../Program/data/downloads/stuzha_dataset_20260910-20260915.csv)

| Parameter | Min | Rata-rata | Median | Max | Standar Deviasi | Keterangan |
|---|---:|---:|---:|---:|---:|---|
| **Suhu (°C)** | 22,20 | 25,92 | 25,40 | 31,10 | 1,97 | Efek siklus AC mati/nyala |
| **RH (%)** | 39,50 | 55,48 | 55,70 | 75,50 | 7,02 | Variasi wajar kelembaban indoor |
| **PM2.5 Nominal (µg/m³)** | 20,46 | 33,29 | 30,01 | 80,25 | 5,74 | Output RF model GP2Y |
| **CO Nominal (ppm)** | 2,68 | 3,92 | 3,70 | 7,44 | 0,74 | Output RF model MQ-7 |
| **MQ-135 ADC** | 1.179,41 | 1.585,02 | 1.525,15 | 3.403,95 | 241,57 | Proksi gas campuran/VOC |
| **ISPU Instan** | 56,22 | 72,86 | 68,27 | 126,16 | 7,79 | Permen LHK 14/2020: $\max(\text{Sub\_PM}, \text{Sub\_CO})$ |
| **Perintah Fan PWM (%)** | 14,90 | 14,98 | 14,90 | 85,10 | 0,88 | 99,19% Level 2 (14,9%), 1,01% Level 3+ |

### Distribusi Harian:
- **10 Sep (Malam):** 699 sampel | Suhu 25,2°C | RH 52,5% | ISPU rata-rata 67,10
- **11 Sep:** 4.301 sampel | Suhu 25,6°C | RH 53,6% | ISPU rata-rata 69,61 (Maks 126,16 - Lonjakan Polusi)
- **12 Sep:** 4.288 sampel | Suhu 26,1°C | RH 57,9% | ISPU rata-rata 70,02
- **13 Sep:** 4.300 sampel | Suhu 25,7°C | RH 56,5% | ISPU rata-rata 68,44
- **14 Sep:** 4.256 sampel | Suhu 26,6°C | RH 56,9% | ISPU rata-rata 76,60
- **15 Sep:** 4.273 sampel | Suhu 25,7°C | RH 53,0% | ISPU rata-rata 80,63 (Maks 125,97 - Lonjakan Polusi)

---

## 4. Poin Permintaan Audit ke Astra 6

Mohon Astra memberikan tinjauan audit dan instruksi teknis terinci mengenai:

1. **Kelayakan Data untuk Publikasi (Target Sinta 2/3):**
   - Apakah volume 22.117 baris data selama 5,16 hari kontinu (123,75 jam tanpa reboot) ini sudah dapat dijadikan dataset eksperimen utama dalam naskah jurnal, ataukah harus mutlak menunggu genap 168 jam (sisa 1,8 hari)?
2. **Penyajian Metodologi Terkait Kipas & Suhu AC:**
   - Bagaimana formula narasi ilmiah yang paling tepat untuk mendeskripsikan kondisi kipas yang fisiknya sering dicabut (misal: diposisikan sebagai evaluasi *commanded duty cycle* algoritma kontrol dan observasi emisi pada sirkulasi pasif, bukan pengujian efisiensi pembersihan udara CADR)?
   - Bagaimana membingkai korelasi fluktuasi suhu kamar akibat AC mati/hidup terhadap pembacaan sensor gas semikonduktor (MQ-7 & MQ-135) di bab pembahasan?
3. **Instruksi Tindak Lanjut untuk Antigravity:**
   - Apa saja langkah komputasi, visualisasi, tabel perbandingan, atau penyusunan draf naskah yang perlu dikerjakan Antigravity berikutnya berdasarkan data ini?
