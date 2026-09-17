# Roadmap Stuzha setelah revisi v4

Status 9 September 2026. Periksa [metode v4](metode_ispu_v4.md) untuk bukti dan [protokol](protokol_pengambilan_data_7_hari.md) untuk menjalankan sesi. Tanda selesai software tidak berarti perangkat fisik telah diuji.

## Selesai pada repositori

- [x] Mempertahankan pin/sensor/rakitan yang dikonfirmasi dan data asli.
- [x] Menjadikan keluaran kedua RF sebagai masukan kendali dan grafik utama, dengan label estimasi eksperimental dan batas validasi yang eksplisit.
- [x] Menambahkan task ADC terpisah, statistik timing/rail, raw semua sensor, validitas DHT, sequence/boot/uptime/hash.
- [x] Menambahkan kendali kategori indeks estimasi, histeresis di semua tingkat, penundaan turun, fallback dan uji logika.
- [x] Memisahkan kanal buzzer dari kipas dan menghapus delay alarm dari pemrosesan.
- [x] Mengaktifkan kembali brownout detector dan memisahkan kredensial lokal.
- [x] Menyediakan telemetri cloud v4 dengan decoder arsip v3.0/v3.1, downloader time-window dengan kegagalan eksplisit, status asli dan atomic replace.
- [x] Menyediakan pemeriksa sesi dan uji penerimaan cloud, tanpa memodifikasi sumber data.
- [x] Mengganti dua pipeline lama dengan satu pipeline beroutput versi baru; split waktu dan baseline training-only.
- [x] Menjalankan benchmark UCI dan simulasi PM; memeriksa ekspor baru Python/C++ pada host.
- [x] Menyelaraskan Markdown, sumber primer, protokol Bab 3 dan panduan pengambilan tujuh hari.

- [x] Mengembalikan interpolasi sub-indeks PM/CO, maksimum/kategori, konversi gas dan ring24jam; memisahkan indeks instan dari estimasi24jam.
- [x] Memperpendek pemulihan kipas dan memisahkan alarm polusi dari fault/kipas yang masih melambat.

## Harus dilaksanakan sebelum memulai 168 jam final

- [x] Upload firmware v4.0.0 ke ESP32 pada COM3 berhasil dan diverifikasi live (10 September 2026, build `a945ea070fcc`).
- [x] Cocokkan konfigurasi pin: GP2Y Vo 34/LED 5, MQ-7 32, MQ-135 33, DHT 4, Fan PWM 19, Buzzer 18.
- [x] Sesuaikan label field ThingSpeak dengan schema STZ4 tanpa menghapus data lama.
- [x] Jalankan uji verifikasi: keluaran ML, ISPU Permen LHK 14/2020, dan kendali dinamis kipas terbukti bekerja fisik.
- [x] Pastikan keluaran ML/field raw terbaca dengan arti yang benar, tidak ada reset berulang, data mentok, atau timing GP buruk.
- [x] Catat binari/manifest ([verifikasi v4](verifikasi_revisi_v4.json)), lokasi dan waktu awal. Sesi 7 hari resmi dimulai 10 September 2026 pukul 20:00 WIB.

Ini pekerjaan lapangan yang belum dapat digantikan tes host. Tidak ada kewajiban membeli instrumen referensi untuk studi implementasi TinyML/monitoring eksperimental; jika ingin klaim akurasi absolut, diperlukan studi kalibrasi terpisah.

## Selama dan setelah tujuh hari

- [x] Rekam kondisi/kejadian di logbook dan simpan snapshot unduhan harian (snapshot 5 hari dan 7 hari tersimpan).
- [x] Pertahankan firmware, posisi dan susunan perangkat; sesi 7 hari tuntas pada build `a945ea070fcc`.
- [x] Unduh akhir, simpan hash dan laporan kualitas ([laporan_audit_sesi_7hari.json](../Program/data/hasil_7hari/laporan_audit_sesi_7hari.json)).
- [x] Analisis pola harian/aktivitas, kestabilan heap (std 86,4 B), transisi kipas, kejadian saturasi 13 September, dan telemetri (slot completeness 99,25%).
- [x] Susun draf metode dan hasil monitoring untuk naskah jurnal ([draf_jurnal_metode_dan_hasil_stuzha.md](draf_jurnal_metode_dan_hasil_stuzha.md)).
- [ ] Pilih target jurnal (Sinta 2/3) sesuai scope dan finalisasi submit.

## Bukan prasyarat studi ini

CADR, efisiensi HEPA, dB, RPM aktual, penghematan energi, pembuktian penghilangan CO, dan kalibrasi gas absolut tidak dijadikan hasil wajib. Tidak ada janji tanpa packet loss; firmware tidak menyimpan ulang data saat offline. Satuan PM publik yang belum terselesaikan tetap ditandai, bukan ditebak.
