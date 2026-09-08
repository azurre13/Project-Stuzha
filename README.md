# Project Stuzha

Prototipe monitoring kualitas udara indoor berbasis ESP32, dengan pencatatan IoT, eksperimen inferensi Random Forest lokal, serta kipas dan filter sebagai fitur pendukung.

## Fokus dan status penelitian

Fokus utama penelitian adalah pembacaan sensor, keterlacakan data, kestabilan operasi, komunikasi IoT, dan respons sistem monitoring. Perangkat fisik sudah beroperasi. Pengumpulan data jangka panjang dan pemeriksaan perangkat sedang berlangsung.

Model ML dan keluaran indeks masih eksperimental. Belum tersedia alat pembanding untuk memvalidasi akurasi konsentrasi PM maupun gas pada Stuzha. Dataset publik dan hasil simulasi belum membuktikan kalibrasi alat fisik. Target SINTA 3 atau SINTA 2 merupakan arah publikasi, bukan status kelayakan atau jaminan penerimaan.

## Membaca konteks proyek

Untuk AI yang melanjutkan proyek, mulai dari [AGENTS.md](AGENTS.md), lalu planning/roadmap dan README bagian terkait. Dokumen ini adalah pintu masuk ringkasan; rincian tiap topik dimiliki oleh README pada tabel navigasi. Klarifikasi terbaru pemilik perlu dicatat pada dokumen terkait, bukan hanya di percakapan.

Bedakan **keterangan pemilik**, **implementasi kode**, **hasil pengujian**, dan **rencana**. Tanda selesai pada roadmap harus menjelaskan apa yang selesai. Kode yang ada di repositori belum otomatis teridentifikasi sebagai versi pembuat seluruh rekaman CSV atau versi yang terpasang saat ini.

## Rakitan aktual

Berdasarkan penjelasan pemilik pada 8 September 2026:

- Casing dari gabus keras; dimensi luar dan detail bentuk perlu didokumentasikan dari rakitan.
- Intake di bawah, exhaust di atas.
- Aliran: intake → filter karbon kotak → filter mobil yang dipotong → ruang kosong sekitar 5 cm → kipas 12 × 12 cm → exhaust.
- Filter bukan HEPA. Ruang sebelum kipas merupakan ruang aliran; istilah “vacuum” tidak menyatakan kondisi vakum terukur.
- Lubang sensor GP2Y menghadap horizontal di area intake.
- Sensor gas yang dikonfirmasi pemilik adalah **MQ-7 untuk CO** dan **MQ-135 sebagai indikator/proksi VOC atau gas campuran**. MQ-7 dipasang tegak pada dinding bawah di intake, sebelum filter.
- Konfigurasi kode memakai target `esp32dev`. Varian board fisik perlu dicocokkan dengan marking sebelum memakai sebutan ESP32-S3 dalam naskah.
- Pemilik menyatakan pin saat ini seharusnya sudah benar. Pemetaan dipertahankan sebagai konfigurasi kerja; belum ada bukti kesalahan pin dari pemeriksaan ini. Ini bukan hasil pengukuran wiring independen, dan terpisah dari pencatatan varian board.

Detail ada di [Hardware](Hardware/hardware_stuzha.md). Efisiensi filtrasi, CADR, penghilangan CO, kebisingan, RPM aktual, dan penghematan energi belum diukur pada perangkat ini.

## Bukti yang tersedia

Snapshot CSV lokal yang diperiksa pada 8 September 2026 memuat uji kamar tanggal 6 September 2026: 3.126 baris dari 01.00.11 sampai 18.22.33 WIB, selama 17 jam 22 menit 22 detik. Pemilik menyebut setelan AC 24–27°C. Ini merupakan uji pendahuluan operasional, bukan validasi akurasi sensor atau bukti efektivitas purifier. Jika CSV diperbarui, hitung ulang sebelum mengutip statistik ini sebagai kondisi file terbaru.

Sebanyak 84,39% keluaran model PM bernilai persis 0,00031 dan terdapat tiga lonjakan di atas 100 pada label skala CSV. Penyebab belum diketahui karena raw PM dan raw sensor gas utama belum tersimpan di CSV. Nilai rendah tidak membuktikan udara bebas partikel. Lihat [catatan dataset](Program/data/dataset_stuzha.md).

## Alur implementasi saat ini

```text
Sensor analog + suhu/RH
  → konversi/input model eksperimental
  → estimasi PM dan gas
  → indeks sesaat dari tabel firmware
  → perintah PWM, alarm, serial, dan ThingSpeak
```

Indeks saat ini belum dapat disebut pelaporan ISPU resmi: satuan, breakpoint CO, dan waktu perataan perlu diperbaiki. Nama variabel `calibrated` dalam kode/CSV adalah label implementasi lama, bukan bukti validasi.

## Navigasi

| Lokasi | Isi |
|---|---|
| [Planning](MD/konteks%20_planing_jurnal_AQI.md) | Ruang lingkup, kontribusi, batas klaim |
| [Roadmap](MD/roadmap_dan_langkah_selanjutnya.md) | Urutan perbaikan dan pengujian |
| [Hardware](Hardware/hardware_stuzha.md) | Rakitan aktual dan dokumentasi fisik |
| [Firmware](Program/Kode/firmware_stuzha.md) | Pin pada kode, API, telemetri, masalah terbuka |
| [Data](Program/data/dataset_stuzha.md) | Rekaman kamar, dataset publik, downloader |
| [Evaluasi ML](Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md) | Simulasi, benchmark, artefak lama |
| [Training](ml_training/training_ml_stuzha.md) | Dua pipeline model, keluaran dan efek samping eksekusi |
| [Referensi](referensi/referensi%20garnie/daftar_referensi.md) | Sumber dan batas penggunaannya |

Skrip training berada di `ml_training/`. Pengunduh berada di `Program/download_thingspeak_dataset.py`, dengan launcher `Download_Dataset_ThingSpeak.bat`.

## Prioritas

1. Dokumentasikan wiring MQ-7/MQ-135 yang telah dikonfirmasi dan cocokkan varian board dengan perangkat fisik.
2. Lengkapi logger raw sensor, validitas, uptime/reset, dan versi firmware/model.
3. Perbaiki downloader berdasarkan rentang waktu agar arsip satu minggu utuh.
4. Telusuri PM menetap/lonjakan, lalu periksa kendali dan indeks.
5. Jalankan pengujian operasional terstruktur dan tulis hasil sesuai bukti.

Pada rangkaian pembaruan 8 September 2026, README/planning/roadmap/laporan diperbaiki, komentar sensor firmware diperjelas, dan dua deskripsi eksplorasi dataset dikoreksi. Logika firmware, model, dataset, dan grafik tidak diubah. Tidak ada training ulang atau upload perangkat. Masalah fungsi kode pada roadmap tetap terbuka.

## Kolaborator

- [@azurre13](https://github.com/azurre13)
- [@Garnie104](https://github.com/Garnie104)
- [@Riq-Z](https://github.com/Riq-Z)
