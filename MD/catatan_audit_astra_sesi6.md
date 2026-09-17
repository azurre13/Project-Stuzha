# Catatan Audit untuk Astra Sesi 6 — Project Stuzha

Dokumen ini memuat catatan audit sesi 6 dan realisasi teknis 10 instruksi Astra setelah penuntasan pengujian kontinu 168 jam (7 hari penuh) per 17 September 2026.

---

## 1. Identitas Sistem & Status Firmware Aktif

- **Versi Repositori:** 4.0.0 (Revisi 17 September 2026)
- **Firmware Terpasang:** Build `a945ea070fcc` (Target `esp32dev`, framework Arduino-ESP32 2.0.17)
- **Model TinyML:** Model PM (`model_pm.h`) & CO (`model_co.h`) terkunci, Model Pair Hash: `d7f32c60`
- **Waktu Mulai Pengujian:** 10 September 2026 pukul 20:01:51 WIB
- **Waktu Penutupan Sesi 7 Hari:** 17 September 2026 pukul 22:33:57 WIB
- **Total Durasi Operasional:** **170,5 Jam (> 7 Hari Penuh)**
- **Total Sampel Terkumpul:** **30.260 baris telemetri** (ThingSpeak Channel 3480764)
- **Dataset Asli:** [`Program/data/downloads/stuzha_dataset_20260910-20260917.csv`](../Program/data/downloads/stuzha_dataset_20260910-20260917.csv)

---

## 2. Pemisahan Sesi Booting (Sesuai Arahan Astra)

Data 30.260 baris dipisahkan berdasarkan identitas booting (*boot ID*) tanpa menggabungkan sesi uji awal ke dalam sesi kontinu utama:

1. **Boot Commissioning (`c43d4d72`):**
   - 13 baris (0,10 jam), 10 September 2026 20:01:51 – 20:05:51 WIB. Sesi commissioning pasca-upload USB sebelum diletakkan permanen.
2. **Boot Utama Kontinu (`f27413f0`):**
   - **27.022 baris (151,26 jam / 6 Hari 7 Jam 15 Menit non-stop)**, 10 September 2026 20:06:28 – 17 September 2026 03:21:46 WIB. Sesi operasi kontinu terpanjang tanpa reset.
3. **Boot Tambahan Pasca-Hari ke-6 (`2ee94f8f`, `9f05ffe4`, `37cbdc54`):**
   - Mengakumulasi 3.225 baris pada 17 September 2026, menggenapkan total observasi melampaui 170 jam.

---

## 3. Realisasi Lengkap 10 Instruksi Audit Astra Sesi 6

| No | Poin Audit Astra | Realisasi Teknis yang Diselesaikan Antigravity | Bukti / Lokasi Berkas |
|:--:|---|---|---|
| **1** | Analisis reproducible & pemisahan boot | Dibuat skrip otomatis `Program/analisis_sesi_7hari.py`. Output disimpan ke folder baru `Program/data/hasil_7hari/`. | [`Program/analisis_sesi_7hari.py`](../Program/analisis_sesi_7hari.py)<br>[`Program/data/hasil_7hari/laporan_audit_sesi_7hari.json`](../Program/data/hasil_7hari/laporan_audit_sesi_7hari.json) |
| **2** | Perbaiki statistik sensor & pisahkan saturasi 13 Sep 02:13 WIB | Kejadian saturasi optik rel 4095 pada 13 Sep 02:13:06 WIB diisolasi secara eksplisit (Kategori 0, ISPU NaN, flags 22930, respon darurat Level 5 disusul *smooth decay* ke Level 4 lalu Level 2). | Draf Jurnal Sub-bab 3.4 & JSON audit |
| **3** | Laporkan kelengkapan slot terpisah dari attempt success | Rekonsiliasi counter telemetri boot utama: Total slot terbentang 27.226 slot, feeds diterima 27.022 (**Kelengkapan Slot 99,25%**). Percobaan kirim 27.135, gagal 118 (**Keberhasilan Percobaan 99,57%**). Sebanyak 91 slot berstatus *skipped* (tidak dicoba saat Wi-Fi belum siap). | JSON audit `telemetry_reconciliation` |
| **4** | Ganti klaim "zero memory leak" dengan kestabilan heap | Frasa diubah menjadi "kestabilan heap yang teramati". Heap pada sesi utama berfluktuasi pada 196.728–201.348 bytes dengan deviasi standar hanya **86,41 bytes** tanpa penurunan progresif. | Draf Jurnal Sub-bab 3.2 |
| **5** | Field PWM sebagai perintah (*commanded*), status fisik tidak diketahui | Laporan menegaskan bahwa field 6 adalah *commanded PWM*. Status fisik putaran motor (termasuk pelepasan kabel konektor saat tidur) dinyatakan berstatus **tidak diketahui** (*unknown physical state*). | Draf Jurnal Sub-bab 2.4 |
| **6** | Grafik komprehensif multi-panel | Dihasilkan grafik 6-panel resolusi tinggi memuat Raw ADC sensor, Suhu/RH, PM/CO nominal, ISPU instan vs 24-jam, Commanded PWM, dan Heap RAM, lengkap dengan penanda kejadian saturasi 13 Sep. | [`Program/data/hasil_7hari/grafik_uji_7hari_komprehensif.png`](../Program/data/hasil_7hari/grafik_uji_7hari_komprehensif.png) |
| **7** | Pembahasan AC berbasis catatan pemilik | Dinamika suhu 22,2°C–31,5°C dibahas berdasarkan logbook pemilik (kamar ber-AC saat ada orang, AC mati saat keluar). Korelasi T/RH dengan output ML dicatat sebagai sifat fitur model, bukan bukti kalibrasi fisik. | Draf Jurnal Sub-bab 2.4 & 3.3 |
| **8** | Penyelarasan dokumentasi repositori | README, roadmap, protokol 7 hari, dan laporan diperbarui secara konsisten menyatakan status firmware ter-upload dan pengujian 7 hari tuntas. | [`README.md`](../README.md)<br>[`roadmap_dan_langkah_selanjutnya.md`](roadmap_dan_langkah_selanjutnya.md) |
| **9** | Evaluasi ML terpisah dari kinerja sensor fisik | Hasil evaluasi benchmark UCI dan simulasi PM dipertahankan sebagai bukti komputasi terpisah, bukan bukti akurasi fisik sensor di ruangan. | [`keputusan_finalisasi_ml_stuzha.md`](keputusan_finalisasi_ml_stuzha.md) |
| **10** | Draf naskah metode & hasil monitoring | Disusun draf artikel ilmiah komprehensif (Abstrak, Pendahuluan, Metodologi, Hasil & Pembahasan, Kesimpulan) berstandar SINTA 2/3. | [`draf_jurnal_metode_dan_hasil_stuzha.md`](draf_jurnal_metode_dan_hasil_stuzha.md) |

---

## 4. Kesimpulan untuk Sesi Finalisasi

Pengujian kontinu 7 hari telah terlaksana secara lengkap dan transparan. Data mentah tetap utuh, turunan analisis tersimpan di folder terpisah, dan seluruh draf naskah publikasi telah siap untuk proses penulisan akhir.
