# Project Stuzha

Prototipe low-cost berbasis ESP32: **GP2Y/MQ7 + suhu/RH → dua RF TinyML → estimasi polutan → sub-indeks → maksimum/kategori → kipas**, dengan MQ135 sebagai proksi gas campuran pendukung. Versi aktif repositori **4.0.0, 10 September 2026**.

## Status dan batas

**Status Aktif (10 September 2026):** Firmware v4.0.0 build `a945ea070fcc` telah berhasil di-upload ke ESP32 melalui port `COM3` dan diverifikasi aktif mentransmisikan data secara live ke ThingSpeak (Channel 3480764, mulai Entry 3609, boot ID `c43d4d72`). Pengambilan data uji stres kontinu 168 jam (7 hari) resmi berjalan aktif di lapangan. Identitas verifikasi tersimpan pada [verifikasi v4](MD/verifikasi_revisi_v4.json). Pengujian sensor, inferensi TinyML, kendali kipas responsif, dan telemetri IoT telah aktif secara fisik. Keberhasilan deployment tidak menggantikan kalibrasi laboratorium resmi.

Kedua header RF historis dipertahankan dengan fitur yang sesuai eksperimen lamanya. PM memakai asumsi unit ug/m3 nominal legacy yang belum terverifikasi; CO target asal mg/m3, dikonversi ke ppm untuk tampilan, dengan transfer MQ7 belum tervalidasi. Flags tetap menyatakan keterbatasan ini. Tidak ada retraining yang diklaim meningkatkan akurasi tanpa label rujukan. [Keputusan metode v4](MD/metode_ispu_v4.md) dan [Keputusan Finalisasi ML](MD/keputusan_finalisasi_ml_stuzha.md) menjelaskan apa yang selesai dan apa yang tidak dapat diselesaikan dari kode saja.

## Pengambilan dan alur data

Field STZ4: T, RH, PM model nominal, CO model nominal ppm, indeks estimasi instan, PWM%, MQ135 ADC, kode kategori estimasi. Raw GP/MQ7, flags, sequence, versi/boot, latensi dan estimasi indeks24jam tersimpan pada status. Detail [firmware](Program/Kode/firmware_stuzha.md).

Indeks instan memakai interpolasi tabel regulasi untuk respons cepat, dengan label estimasi instan. Ring RAM terpisah menghitung rerata24jam dan indeks dari kedua rerata setelah durasi/kelengkapan cukup. Tidak ada baseline relatif per boot. Semua hasil konsentrasi/indeks tetap bergantung pada asumsi model; tidak disebut ISPU resmi.

Kipas naik setelah konfirmasi sekitar 1 detik, turun 8 detik per tingkat dengan histeresis 5%. Sinyal jenuh/fault tidak otomatis membunyikan alarm polusi. Buzzer berhenti ketika kategori saat ini turun meskipun kipas masih melambat.

ESP32 dan Wi-Fi saja cukup untuk operasi. Cloud sekitar 20 detik; tanpa jaringan tidak ada replay sampel, tetapi ring 24 jam tetap berjalan di RAM selama alat menyala. Baca [protokol tujuh hari](MD/protokol_pengambilan_data_7_hari.md). Pisahkan data STZ3, STZ31, STZ4 dan legacy; jangan menghapus arsip.

## Rakitan aktual

Menurut pemilik: casing gabus keras, intake bawah/samping, karbon kotak dan filter mobil dipotong (bukan HEPA), ruang sekitar 5 cm sebelum kipas 12 × 12 cm, exhaust atas. GP2Y berlubang horizontal di intake; MQ-7 tegak sebelum filter. Adaptor 12 V menyuplai kipas dan expansion board yang menyediakan jalur 5 V. Pengaturan heater MQ-7 belum terbukti; lihat [hardware](Hardware/hardware_stuzha.md).

Pin dikonfirmasi pemilik dan dipertahankan: GP2Y Vo 34/LED 5, MQ-7 32, MQ-135 33, DHT22 4, fan 19, buzzer 18. Target build `esp32dev`; jangan menulis ESP32-S3 tanpa bukti.

## Bukti dan batas penelitian

Pengujian awal telah membuktikan stabilitas transmisi lebih dari 20 jam continuous run tanpa reboot. Dataset live tersimpan secara otomatis di cloud ThingSpeak Channel 3480764. Statistik lengkap dan riwayat sesi berada pada [data](Program/data/dataset_stuzha.md).

Belum ada alat pembanding laboratorium. Respons terhadap debu/asap tidak membuktikan akurasi konsentrasi atau efisiensi filtrasi. Model PM lama menggunakan gangguan sintetis; model CO lama memakai respons UCI yang diubah skalanya. Model tersebut tidak memvalidasi sensor fisik. Pembuktian akurasi fisik membutuhkan instrumen acuan berpasangan sesuai [Protokol Kalibrasi Masa Depan](MD/protokol_kalibrasi_co_masa_depan.md).

## Navigasi konteks

| Dokumen | Pemilik informasi |
|---|---|
| [AGENTS](AGENTS.md) | Aturan kerja AI dan pembedaan bukti |
| [Planning](MD/konteks%20_planing_jurnal_AQI.md) | Pertanyaan penelitian dan kontribusi |
| [Roadmap](MD/roadmap_dan_langkah_selanjutnya.md) | Status software dan pekerjaan lapangan |
| [Protokol 7 hari](MD/protokol_pengambilan_data_7_hari.md) | Persiapan, logbook, analisis Bab 3 |
| [Hardware](Hardware/hardware_stuzha.md) | Rakitan, daya, pin dan ketidakpastian fisik |
| [Firmware](Program/Kode/firmware_stuzha.md) | Algoritma dan kontrak telemetri |
| [Data](Program/data/dataset_stuzha.md) | Sesi, format, downloader dan analisis |
| [Training](ml_training/training_ml_stuzha.md) | Pipeline yang tidak menimpa firmware |
| [Evaluasi ML](Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md) | Eksperimen publik dan batas interpretasi |
| [Keputusan Final ML](MD/keputusan_finalisasi_ml_stuzha.md) | Paritas C++ vs Python dan audit pohon PM |
| [Protokol Kalibrasi Masa Depan](MD/protokol_kalibrasi_co_masa_depan.md) | Prosedur kalibrasi jika tersedia alat referensi |
| [Referensi](referensi/referensi%20garnie/daftar_referensi.md) | Sumber primer dan koleksi kandidat |

Target Sinta 2/3 merupakan tujuan publikasi, bukan jaminan penerimaan. Perbaikan ini memusatkan kontribusi pada evaluasi deployment TinyML yang menggerakkan aktuator, transparansi raw/model, serta operasi monitoring yang dapat ditelusuri. Manfaat terhadap akurasi fisik memerlukan bukti tambahan.

## Kolaborator

- [@azurre13](https://github.com/azurre13)
- [@Garnie104](https://github.com/Garnie104)
- [@Riq-Z](https://github.com/Riq-Z)
