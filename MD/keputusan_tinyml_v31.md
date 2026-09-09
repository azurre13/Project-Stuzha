# Keputusan TinyML dan revisi deployment Stuzha v3.1

> Arsip versi sebelumnya. Kontrak aktif telah digantikan [v4](metode_ispu_v4.md); hash/tes di dokumen ini tetap milik versi historis.

9 September 2026. Dokumen ini menggantikan keputusan shadow-only pada v3.0 atas arahan pemilik. Tujuan utama tetap prototipe monitoring indoor berbiaya rendah; kipas/filter merupakan respons pendukung. Detail rakitan dan pin tetap mengikuti [hardware](../Hardware/hardware_stuzha.md).

## 1. Koreksi arah penelitian

Menjadikan RF sekadar shadow mengurangi hubungan antara TinyML dan fungsi prototipe yang ingin diteliti pemilik. V3.1 mengembalikan kedua keluaran model ke grafik numerik ThingSpeak dan menjadikannya masukan utama keputusan kipas. Transparansi dicapai dengan menyimpan raw sensor, identitas model, flags dan batas interpretasi, tanpa menyingkirkan fungsi ML.

Namun, menyebut angka sebagai estimasi atau soft-sensor tidak dengan sendirinya membuktikan relasi masukan-target benar. Prototipe dapat mendemonstrasikan deployment dan respons aktuator yang bergantung pada model, sementara akurasi konsentrasi dan keberhasilan kompensasi drift tetap belum terbukti. Keduanya harus dibedakan dalam judul, abstrak, metode dan hasil.

## 2. Apa yang didukung literatur

- [Zimmerman et al. (2018)](https://amt.copernicus.org/articles/11/291/2018/) mengembangkan kalibrasi RF pada paket RAMP dan mengevaluasinya dengan monitor referensi serta beberapa unit/periode. Ini dasar yang relevan untuk mencoba sensor fusion; hasilnya tidak otomatis berlaku pada GP2Y/MQ7 Stuzha.
- [Han et al. (2021), PDF penerbit](https://mdpi-res.com/d_attachment/sensors/sensors-21-00256/article_deploy/sensors-21-00256.pdf) mengevaluasi sensor Alphasense selama 12 bulan dan memakai data stasiun rujukan untuk kalibrasi/validasi. Perbandingan metode tidak mendukung klaim RF selalu paling unggul. Menggunakan T/RH sebagai fitur adalah desain model; keberhasilan koreksinya harus dievaluasi.
- [Yadav et al. (2021), abstrak preprint](https://arxiv.org/abs/2108.00640) membahas transfer learning dengan data sensor lain ditambah sedikit data target yang dikolokasikan terhadap referensi. Status bacaan di sini hanya abstrak. Deployment C++ ke ESP32 bukan dengan sendirinya adaptasi domain target seperti dalam penelitian tersebut.

Implikasi pada Stuzha merupakan penilaian metode: gunakan istilah **estimator/soft-sensor eksperimental yang dieksekusi di edge**. Jangan menulis bahwa kompensasi drift telah berhasil atau transfer learning telah tervalidasi hanya karena model publik dijalankan pada ESP32. Sensor fusion dan kompensasi merupakan tujuan desain yang masih memerlukan pembuktian.

## 3. Model yang dipilih untuk build ini

Model deployment v3.1 adalah dua header historis, dipertahankan byte-identik. Tidak ada retraining baru atau penimpaan otomatis. Ini pilihan untuk eksperimen integrasi yang dapat diidentifikasi, bukan keputusan bahwa keduanya merupakan estimator konsentrasi terbaik atau sudah layak dipakai sebagai instrumen rujukan.

| Artefak | SHA256 |
|---|---|
| model_pm.h | 936cce94135cec0abe10d0af83b29bfea3856bd459fc6923ec4c77df27c9de99 |
| model_co.h | f7ef4fef9164724abd5d204ea39d9ae4dd4531606fa6716ddce753d36aa19048 |
| Pasangan model | d7f32c6097671a37ff90e22c4af5db2e333fbc0192f653125a4c9675bdd7cab7 |

Preprocessing terpusat di [experimental_models.h](../Program/Kode/include/experimental_models.h):

- PM memakai transformasi analog historis, T dan RH. Training lama memakai gangguan sintetis dari target. Konflik skala dataset dan perkalian 1000 belum terselesaikan; keluaran tidak diberi satuan fisik definitif pada dashboard.
- CO memakai MQ7 ADC, T dan RH. Target UCI asal CO(GT) bersatuan mg/m3, bukan ppm. Pemetaan respons PT08 ke rentang ADC pada eksperimen lama belum membuktikan kesesuaian sensor MQ7. Heater MQ7 sendiri belum diverifikasi.
- Artefak training sklearn asal kedua header belum teridentifikasi. Identitas dan kemampuan eksekusi header dapat diuji; kesetaraan dengan model Python asal serta hasil metrik lama belum dapat dinyatakan terverifikasi.

Mengapa bukan header baru dari pipeline.py? Benchmark UCI baru memakai PT08.S1 asli, bukan MQ7 ADC. Simulasi PM baru memakai skala angka asli, berbeda dari transformasi legacy. Menyalin kedua hasil itu langsung ke firmware akan memasangkan model dengan fitur/skala yang berbeda. Pipeline tetap berfungsi untuk benchmark yang reproduktif, bukan kalibrasi fisik tanpa data pasangan relevan.

Keluaran benchmark baru tetap terpisah dan metriknya tidak dilaporkan sebagai metrik dua header deployment. Jika nanti ada model dengan kontrak fitur yang sesuai dan evaluasi domain target yang dapat dipertanggungjawabkan, ekspor ke versi deployment baru, simpan manifest, uji lagi, dan mulai segmen data baru. Jangan mengganti model selama sesi tujuh hari hanya agar grafik terlihat baik.

## 4. Kontrak cloud dan aktuator

| Field | Isi v3.1 |
|---|---|
| 1 | Suhu |
| 2 | RH |
| 3 | PM_TinyML_Experimental, skala model legacy |
| 4 | CO_TinyML_Experimental, target nominal mg/m3; transfer belum tervalidasi |
| 5 | GP2Y raw ADC |
| 6 | PWM persen aktual |
| 7 | MQ135 raw ADC/proksi gas campuran |
| 8 | MQ7 raw ADC |

Status **STZ31|v=3.1.0** memuat sequence s, flags f, build/model/boot, uptime, baseline/skala kedua model, level, skor, timing, infer_us, heap dan counter jaringan. Field 3/4 menjadi grafik model; semua raw sensor tetap tersimpan. Decoder tetap mendukung STZ3/v3.0 dengan arti field lamanya. Perubahan nama channel tidak mengubah arti data historis; pisahkan interval grafik/analisis.

Kendali menggunakan maksimum kenaikan relatif keluaran PM dan CO terhadap baseline awal yang dibekukan setiap boot. Keduanya dapat menaikkan level tanpa memakai ADC sebagai keputusan utama. Histeresis, konfirmasi dua blok untuk naik, dan dwell turun 30 detik dipertahankan. Nilai input/model invalid meminta sedikitnya L4 dengan flag 128 dan prediksi kosong. Ini respons fault, bukan alarm CO terkalibrasi atau kategori kesehatan. Rumus dan parameter lengkap hanya dipelihara pada [dokumentasi firmware](../Program/Kode/firmware_stuzha.md).

Baseline tidak menganggap startup sebagai udara bersih. Output model yang datar atau sensitif terhadap T/RH harus dilaporkan, bukan diperhalus agar terlihat benar. Filter karbon/filter mobil dan fan tidak dijadikan klaim penghilangan CO, CADR, HEPA atau efisiensi energi.

## 5. Bukti yang dibutuhkan untuk kontribusi ilmiah

| Pertanyaan | Bukti yang tersedia/dapat dikumpulkan |
|---|---|
| Apakah RF benar-benar memengaruhi aktuator? | Uji controller tiap keluaran dan integrasi dua header aktual; kemudian observasi fan pada perangkat |
| Apakah model dapat dijalankan pada ESP32? | Build dan ukuran binari; pengukuran infer_us/heap di perangkat setelah upload |
| Apakah raw/model dapat ditelusuri? | Field berdampingan, versi/model hash, boot/sequence/status asli |
| Apakah sistem bertahan tujuh hari? | Data cloud bertimestamp, logbook, flags, gap/reset yang teramati; belum selesai |
| Apakah ML lebih akurat daripada baseline? | Benchmark publik menjawab domain sumber; akurasi Stuzha memerlukan rujukan relevan pada domain perangkat |
| Apakah kipas berbasis ML lebih efektif membersihkan kamar? | Belum diuji; simulasi keputusan atau penurunan angka model saja tidak cukup |

Perbandingan RF dan baseline tetap perlu dilaporkan meskipun RF tidak menang. Pada benchmark UCI kronologis yang sudah diperiksa, RF tiga fitur belum mengungguli linear tiga fitur. Rincian ada pada [evaluasi ML](../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md). Label TinyML dan banyaknya baris tidak menjamin kebaruan atau penerimaan Sinta 2/3.

Analisis lapangan yang realistis: timeline raw/model/T/RH/PWM, kejadian logbook, tingkat dan transisi kipas yang teramati, proporsi keluaran datar/invalid, distribusi latensi, kelengkapan cloud serta perubahan antarhari. Snapshot 20 detik tidak merekam semua keputusan per detik. Jika melakukan replay controller alternatif, sebut sebagai perbandingan simulasi keputusan, bukan eksperimen fisik efisiensi purifier.

## 6. Status revisi dan langkah freeze

Implementasi, pengujian dan identitas build dicatat pada [verifikasi v3.1](verifikasi_revisi_v31.json). Versi ini mempertahankan pemisahan task, pola pulsa GP2Y, kanal buzzer/kipas terpisah dan data asli. Model/CSV historis tidak diubah. Pipeline benchmark tidak dijalankan ulang karena model deployment tidak diganti.

Tes host memeriksa keluaran PM dan CO secara independen, baseline tetap, seluruh ambang, fault, histeresis/dwell, clock 64 bit, integrasi header aktual dan alokasi/status delapan field. Uji Python memeriksa downloader dan decoder campuran v3.0/v3.1. Pengujian ini bukan kalibrasi atau uji fisik.

Belum ada upload ke ESP32, perubahan dashboard, commit/push atau pengumpulan tujuh hari oleh revisi ini. Setelah upload satu kali, cocokkan status/build, ubah label grafik, jalankan [uji penerimaan dan protokol](protokol_pengambilan_data_7_hari.md), lalu freeze selama 168 jam bila fungsi sesuai. PC logger bukan prasyarat; saat Wi-Fi mati data tidak mempunyai antrean persisten/replay.

Perbaikan ini membuat implementasi lebih sesuai tujuan pemilik. Green light yang dapat diberikan setelah tes software adalah **siap commissioning sebagai prototipe TinyML eksperimental**, bukan pernyataan konsentrasi sudah benar atau jurnal pasti menerima. Freeze sesi final mengikuti hasil commissioning perangkat.

## 7. Hasil verifikasi repositori

- Build 3.1.0 berhasil untuk esp32dev; source ID **461171669a42**.
- Flash aplikasi 1.069.137 dari 1.310.720 byte (81,6%); RAM statis 45.364 byte. Ini bukan free heap/latensi runtime perangkat.
- Dua executable pengujian C++ dan 12 tes Python lulus. Fixture integrasi host: GP ADC 900 ke 3000 dan MQ7 ADC 1000 ke 3000 pada T=25/RH=50 menghasilkan keluaran model PM 20.0023 ke 267.261 dan CO 0.378528 ke 6.39036; controller mencapai L5 setelah dua blok. Angka ini masukan software buatan, bukan hasil uji konsentrasi atau eksperimen kamar.
- Fixture status untuk delapan hari berukuran 179 byte; pengujian juga memastikan buffer yang terlalu kecil terdeteksi. Batas ini adalah hasil fixture, bukan jaminan untuk semua nilai/counter tak terbatas.
- SHA256 CSV asli dan kedua header model tetap sesuai nilai sebelum revisi. Lima belas Markdown proyek diperiksa; tautan lokal diperiksa tanpa target hilang.
- Linker Xtensa memerlukan pengaturan penempatan literal untuk fungsi model besar. Build final sudah menyertakan perbaikan tersebut; header model tetap identik.
- Port serial tidak terdeteksi. Upload dan uji fisik belum dilakukan; tidak ada commit/push atau perubahan dashboard.
