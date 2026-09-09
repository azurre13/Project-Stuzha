# Catatan revisi Stuzha v3.0.0

> Arsip versi sebelumnya. Kontrak aktif telah digantikan [v4](metode_ispu_v4.md); hash/tes di dokumen ini tetap milik versi historis.

> Arsip keputusan/build v3.0.0. Kontrak dan peran ML pada dokumen ini telah digantikan oleh [revisi v3.1](keputusan_tinyml_v31.md) atas arahan pemilik 9 September 2026. Angka hash dan hasil tes di bawah hanya berlaku untuk build v3.0 historis.

Pekerjaan dimulai 8 September dan diselesaikan pada tingkat repositori 9 September 2026. Pemilik memberi izin memperbaiki program dan seluruh konteks proyek untuk pengumpulan data tujuh hari. Catatan ini membedakan perubahan software dari pekerjaan fisik yang belum dilaksanakan.

## Hasil utama

Stuzha sekarang mempunyai jalur monitoring raw yang dapat ditelusuri, kontrol relatif dengan aturan eksplisit, eksperimen TinyML terpisah, downloader yang tidak menyamarkan kegagalan, serta prosedur pengumpulan data dan analisis Bab 3. Pin, identitas sensor dan rakitan yang dijelaskan pemilik dipertahankan.

**Belum di-upload ke ESP32.** Tidak ada port serial terdeteksi pada pemeriksaan. Tidak ada uji perangkat fisik, perubahan dashboard/channel, atau sesi 168 jam yang diklaim selesai. Langkah pengguna berikutnya adalah upload, penyesuaian nama field, dan [uji penerimaan singkat](protokol_pengambilan_data_7_hari.md). Tidak ada commit/push oleh pekerjaan revisi ini.

## Perubahan dan alasan

| Area | Perubahan | Alasan |
|---|---|---|
| Firmware utama | Task ADC terpisah dari jaringan, blok raw sekitar satu detik | Jaringan tidak berada pada jalur akuisisi yang sama; data dasar tersedia untuk diagnosis |
| GP2Y | Target pulsa 10 ms/320 us dan mulai ADC sekitar 280 us, statistik timing/rail/min/maks | Jeda satu kali setiap detik sebelumnya belum memenuhi pola pulsa yang dirujuk; timing aktual kini dapat diperiksa |
| DHT22 | Cadence sekitar 2 detik, missing tetap invalid | Menghindari angka pengganti 25 C/50% RH terlihat sebagai pengukuran nyata |
| Kendali kipas | Baseline awal per boot, skor deviasi debu, L1-L5, dua blok untuk naik, deadband dan dwell turun 30 detik | Keluaran model lintas-sensor yang belum tervalidasi tidak lagi menentukan kategori kesehatan/aktuator |
| Alarm | Kanal tone 15, kipas tetap kanal 0; tanpa delay alarm pada loop pemrosesan | Framework terpasang memakai kanal tone 0 secara bawaan, sehingga berpotensi mengubah PWM kipas |
| Daya | Brownout detector tidak dimatikan | Gangguan daya tidak ditutupi sebagai operasi normal |
| TinyML | Header lama tetap identik, keluaran shadow dan waktu gabungan dua inferensi dicatat | Mempertahankan eksperimen deployment dengan batas bukti yang jelas |
| Identitas | Hash kode/model, boot ID acak, uptime 64 bit dan reset reason | Memisahkan versi dan restart pada data yang diterima |
| Cloud | Delapan field raw/validitas, status STZ3 dan slot berdasar clock boot | Kontrak data jelas tanpa konsentrasi/ISPU yang tidak tervalidasi |
| Jaringan | Task terpisah, timeout dalam satuan API yang benar, counter gagal/slot tanpa percobaan | Timeout WiFiClient versi terpasang memakai detik; gap dapat ditelusuri |
| Kredensial | Nilai lokal ke secrets.h yang diabaikan Git, contoh terpisah | Source baru tidak menyebarkan kredensial; riwayat Git lama tidak ditulis ulang |
| Downloader | Rentang UTC, end tanggal sampai akhir hari WIB, recursive window splitting, status asli, validasi dan retries | Menghindari truncation API dan window gagal yang tampak lengkap |
| Penyimpanan unduhan | Snapshot baru default, backup eksplisit, os.replace sesudah write/fsync | Arsip tidak dikosongkan atau dihapus sebelum pengganti siap |
| Analisis sesi | Laporan read-only, pemisahan schema/build/boot, gap/flags/slot/latensi dan preflight | Membantu menulis hasil berdasarkan rekaman nyata, tanpa mengarang packet-loss/akurasi |
| Training/evaluasi | Satu pipeline kronologis, preprocessing/baseline training-only, folder run baru | Menghilangkan pemetaan ADC yang tidak berdasar dan penimpaan header/laporan otomatis |
| Dokumentasi | Semua Markdown proyek diselaraskan, protokol tujuh hari dan sumber primer ditambahkan | AI berikutnya dapat membedakan keputusan, implementasi, hasil dan batas validasi |

## Bukti pengujian software

- Build PlatformIO untuk esp32dev berhasil pada source yang diidentifikasi di bawah.
- Sepuluh tes Python lulus: batas tanggal WIB, window gagal, window terpotong/deduplikasi, atomic replace gagal, schema campuran/status, rentang invalid, gap teramati, status terpotong, penolakan legacy pada preflight, dan fault timing pada bagian tengah sesi.
- Tes C++ native lulus untuk seluruh batas kenaikan, penolakan lonjakan tunggal, baseline tetap, deadband/dwell, fallback invalid serta clock 64 bit melewati rollover millis 32 bit.
- Downloader diuji langsung terhadap 6 feed historis pada 8 September 06:14–06:16 UTC; status dipertahankan. Tidak ada write ke cloud.
- Evaluasi UCI dan PM-simulation dijalankan ke direktori baru; ekspor C++ baru dibandingkan sklearn pada holdout dan probe sekitar threshold.
- Data CSV lokal dan dua header shadow diverifikasi dengan SHA256 tetap identik terhadap kondisi sebelum perubahan.

Uji host/build tidak memvalidasi tegangan sensor, heater, pulse fisik, putaran fan, bunyi buzzer, reconnect aktual perangkat, kalibrasi atau pengumpulan tujuh hari.

## Temuan ML baru

UCI kronologis: 5.875 training dan 1.469 test. RF tiga fitur RMSE 0.72588 mg/m3, baseline linear tiga fitur 0.70948 mg/m3. RF belum mengungguli baseline pada holdout tersebut. Ekspor benchmark diperiksa pada 2.246 probe.

PM-simulation: 133.972 training dan 33.493 test; angka sumber tidak dikali 1000, unit fisik unresolved. Ekspor diperiksa pada 2.447 probe. R² tinggi pada simulasi bukan akurasi sensor Stuzha. Detail dan artefak JSON ada pada [evaluasi ML](../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md).

Model benchmark baru tidak di-upload dan tidak mengganti header historis. Pemeriksaan ekspor baru bukan bukti kesesuaian model Python asal header historis, yang belum tersedia sebagai artefak teridentifikasi.

## Identitas build

- Firmware: 3.0.0, build ID: `6281fce3f66c`.
- Source SHA256: `6281fce3f66c016d88b5853a3b0eb92c11cdc94b494fdfcb7f2760f7a9638840`.
- Hash pasangan model: `d7f32c6097671a37ff90e22c4af5db2e333fbc0192f653125a4c9675bdd7cab7`.
- Firmware.bin SHA256: `9a3db724dd6a5de7d3c661ee5462637d5396a353d6c755365cb6ee1fc5a9227f`.
- Flash aplikasi: 1,072,969 / 1,310,720 byte (sekitar 81.9%).
- RAM statis build: 45,332 byte; bukan pengukuran free heap runtime.
- Salinan lokal privat: `../Program/Kode/release/v3.0.0_6281fce3f66c/`, berisi firmware, ELF, bootloader, partisi, manifest dan checksum. Binari mengandung konfigurasi lokal; jangan dipublikasikan.

[Rekaman verifikasi JSON](verifikasi_revisi_v3.json) menyimpan identitas dan batas pemeriksaan. Build identity mengecualikan secrets.h dari hash publik, sehingga hash ini mengidentifikasi sumber algoritma, bukan membuktikan semua perangkat memakai kredensial sama. Firmware checksum mengidentifikasi binari lokal yang benar-benar dibangun.

## Data lama tetap dipertahankan

CSV lokal telah berstatus modified sebelum pekerjaan dimulai karena diperbarui pada sesi sebelumnya. Perubahan ribuan baris yang terlihat pada git diff CSV bukan hasil pengubahan dataset oleh revisi ini. Hash file tetap 3fe753182a059ee0f6e4c76912dba3009be4e81b07bfb0cd7199fc9cfee8b7ee.

CSV tersebut memuat 1.389 baris sesi 8 September. Gap 1.279 detik dijelaskan pemilik sebagai router mati. Arsip sesi 18 jam berada di Program/data/backup/. Grafik/metrik lama dan naskah PDF tetap menjadi arsip; label lama tidak dipakai untuk klaim baru.

## Batas yang masih perlu dijalankan pemilik

- Upload dan pastikan feed berstatus STZ3 dengan build ID yang sesuai.
- Periksa jalur analog/suplai dan marking perangkat. Suplai 5 V expansion belum menunjukkan siklus heater MQ7; flag 256 sengaja tetap aktif.
- Lakukan uji penerimaan cloud minimal 15 menit dan observasi fisik, lalu tetapkan awal 168 jam.
- Catat kondisi kamar, AC, okupansi, pintu/jendela, aktivitas, router/daya dan perubahan konfigurasi.
- Terima dan laporkan gap saat offline karena firmware tidak mempunyai penyimpanan persisten/replay.

Dokumentasi utama pengambilan adalah [protokol tujuh hari](protokol_pengambilan_data_7_hari.md). Kelayakan submit jurnal memerlukan hasil studi dan naskah yang selesai; tidak ditentukan hanya dari keberhasilan build.
