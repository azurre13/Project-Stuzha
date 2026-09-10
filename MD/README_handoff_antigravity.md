# Rencana penyelesaian Stuzha untuk Antigravity

Tanggal serah-terima: 10 September 2026. Dokumen ini adalah instruksi pekerjaan berikutnya, **bukan laporan bahwa perbaikan ML sudah selesai**.

## Permintaan pemilik

Selesaikan kode, keputusan model dan evaluasinya sebelum pemilik memulai pengambilan data utama 168 jam. Pemilik tidak ingin mengulang satu minggu karena model belum final. Jangan mengubah total proyek atau mengembalikan sistem menjadi raw-only. Kerjakan bagian yang dapat diselesaikan AI, bukan hanya memberikan daftar kekurangan. Setiap hambatan harus disertai pilihan penyelesaian konkret. Jangan menjanjikan akurasi setara sensor mahal atau penerimaan Sinta.

Alur yang dipertahankan:

**GP2Y + DHT22 → RF PM; MQ-7 + DHT22 → RF CO → estimasi konsentrasi → interpolasi sub-indeks → maksimum → kategori dan kipas.** MQ-135 tetap indikator gas campuran/VOC berbasis ADC, bukan pengukur VOC terkalibrasi. DHT22 tetap memasok suhu dan RH. Kipas/filter adalah pendukung monitoring indoor.

Baca [AGENTS](../AGENTS.md), [README utama](../README.md), [planning](konteks%20_planing_jurnal_AQI.md), [roadmap](roadmap_dan_langkah_selanjutnya.md), [protokol](protokol_pengambilan_data_7_hari.md), lalu dokumentasi [hardware](../Hardware/hardware_stuzha.md), [training](../ml_training/training_ml_stuzha.md), [evaluasi](../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md) dan [firmware](../Program/Kode/firmware_stuzha.md).

## 1. Periksa pekerjaan yang sudah ada sebelum mengedit

- Jalankan `git status --short`; simpan perubahan lokal pemilik. Jangan reset, membersihkan folder, menghapus data atau overwrite hasil training.
- Ada hasil baru di `Fase_1_Evaluasi_ML/hasil/finalisasi_20260910_benchmark/` dan `finalisasi_20260910_reproduksi/`. Baca report, model_card, CSV dan kode pembentuknya sebelum memutuskan perlu run baru. Nama finalisasi bukan bukti model siap deployment. Isi hasil baru ini belum diaudit dalam penyusunan handoff.
- Ada kandidat `Program/data/public_candidates/cheriyan_2020/source.json` dan `DIB -data.xlsx`. Periksa asal, sensor, kolom dan satuannya; jangan menganggap kandidat tersebut cocok untuk MQ-7 hanya karena sudah diunduh.
- Hasil lama yang sudah ditata berada di `hasil/reproduksi_awal_20260909_124230_faba1c/`, `hasil/evaluasi_20260909_124246_f546a8/`, dan `arsip/sebelum_revisi/`. Jangan hapus sebagai duplikat: eksperimennya berbeda.
- Pertahankan header historis `Program/Kode/include/model_pm.h` dan `model_co.h`. Kandidat baru disimpan terpisah; jangan otomatis menyalin header benchmark ke firmware.

## 2. Bereskan metode GP2Y terlebih dahulu

**Masalah yang harus diselesaikan:** dataset asli merupakan pengukuran GP2Y nyata, tetapi skrip lama mengalikan target PM dengan 1000 dan membuat input terganggu dari target menggunakan formula suhu/RH/noise buatan. Ini dua persoalan berbeda; jangan menyebut dataset asli palsu.

Sumber [Mendeley 2r232jpfb2 v1](https://data.mendeley.com/datasets/2r232jpfb2/1) menyatakan GP2Y1010AU0F, 173.468 rekaman November 2020–Juli 2022, PM dalam ug/m3 dan T/RH dari BME280. CSV lokal berada di `Program/data/mendeley/Indoor_Air_Pollution_Data.csv`.

Pekerjaan:

1. Buat kontrak input/target yang eksplisit: nama fitur, urutan, satuan, preprocessing, rentang dan sumber. Cocokkan setiap langkah Python dengan `include/experimental_models.h` dan pembacaan `src/main.cpp`.
2. Gunakan satuan sumber kecuali ada koreksi primer yang benar-benar diperoleh. Periksa alasan historis x1000; jangan menebak dari besarnya angka. Jangan sekadar membagi output header lama dengan 1000.
3. Periksa hubungan konversi ADC/tegangan, offset dan sensitivitas dengan datasheet Sharp serta rangkaian yang terdokumentasi. Jangan memasukkan nilai kalibrasi individu yang tidak pernah diukur.
4. Periksa apakah data menyediakan pasangan bacaan sensor dan target referensi independen. Jika hanya satu kolom PM, jangan membuat input dari target lalu mengklaim hasilnya kalibrasi fisik. Menggunakan PM sebagai input sekaligus target tanpa pengukuran pasangan juga bukan bukti koreksi.
5. Simulasi penghilangan gangguan tetap boleh dievaluasi, tetapi dipisahkan dari kandidat kalibrasi deployment. Jika kontrak input fisik belum dapat didukung, selesaikan laporan keputusan dan alternatif; jangan mempromosikan simulasi hanya agar pekerjaan terlihat selesai.

Hasil wajib: tabel kontrak fitur/satuan, keputusan preprocessing, bukti sumber, kandidat yang dapat diuji bila datanya mendukung, serta penjelasan singkat apa yang benar-benar diperbaiki dibanding model awal.

## 3. Putuskan jalur MQ-7, jangan mencari tanpa kesimpulan

Model CO historis memakai target UCI CO(GT) dalam mg/m3 dan respons PT08.S1 yang dipetakan ke rentang angka menyerupai ADC. **PT08 bukan MQ-7; rescaling saja bukan kalibrasi transfer.** Dataset CO Mendeley milik Sonawani juga memakai MiCS-6814, bukan MQ-7.

Periksa kandidat lokal dahulu, lalu sumber yang sudah ditemukan:

| Sumber | Yang diketahui | Tindakan berikutnya |
|---|---|---|
| [Rathnayake et al. 2024](https://neptjournal.com/upload-images/%2834%29D-1457.pdf), DOI 10.46488/NEPT.2024.v23i01.034 | MQ-7 dan instrumen NBRO diukur bersamaan sekitar tiga bulan; ML memakai sensor dan suhu | Cari suplemen/repository data pasangan. CSV terbuka belum ditemukan dalam penelusuran sebelumnya. |
| [Indoor Air Quality Monitoring Dataset](https://www.kaggle.com/datasets/hemanthkarnati/indoor-air-quality-dataset) | Deskripsi menyebut MQ-7 dan MQ-135 selama 24 jam | Periksa berkas aktual, konversi ppm dan keberadaan referensi independen. Belum diterima sebagai data kalibrasi. |
| [Yildiz dan Sucuoglu 2025](https://www.mdpi.com/2071-1050/17/19/8531) | Paper menyebut MQ-7 dan GP2Y dengan pembanding; pernyataan ketersediaan data mengarahkan pertanyaan kepada penulis | Periksa data/suplemen dan konsistensi metode; jangan menyalin persentase paper ke Stuzha. |

Untuk menerima dataset, periksa jenis sensor, ADC/tegangan/resistansi, rangkaian, RL, definisi R0, tegangan/cara heater, unit target, timestamp pasangan dan suhu/RH. Dataset orang lain belum otomatis membuktikan akurasi unit Stuzha. Jangan mengganti masalah PT08 dengan ketidakcocokan sensor baru.

Jika data pasangan cocok tersedia: latih kandidat dengan preprocessing yang bisa diterapkan pada rangkaian Stuzha; uji terhadap baseline dan split waktu. Jika belum tersedia: laporkan sumber yang diperiksa dan hasilnya, siapkan permintaan data yang siap dikirim; jangan menghubungi penulis tanpa izin pemilik.

Alternatif yang dapat ditawarkan adalah estimator nominal berdasarkan kurva datasheet. Ini memerlukan dasar parameter rangkaian/R0 dan heater yang sesuai. RF yang dilatih meniru kurva tersebut hanya pendekatan numerik kurva, **bukan kalibrasi ML berdasarkan pengukuran referensi**. Jangan mengarang nilai R0, menganggap udara kamar nol CO, atau menerapkan kurva heater bersiklus pada suplai konstan tanpa pembuktian. Pelajari dokumen/foto yang sudah ada sebelum meminta pemeriksaan fisik minimal yang benar-benar tidak bisa dilakukan dari repositori.

Keputusan akhir CO harus salah satu: kandidat didukung data dan siap diuji; alternatif nominal konkret untuk dipilih pemilik; atau hambatan spesifik beserta pilihan kebutuhan minimal. Jangan menyatakan siap 168 jam sambil menyembunyikan keputusan CO yang belum selesai. Perubahan tujuan dua RF memerlukan keputusan pemilik, bukan dilakukan diam-diam.

## 4. Evaluasi yang harus diserahkan di Fase 1

Gunakan pipeline yang sudah ada (`ml_training/pipeline.py` dan entry point `Fase_1_Evaluasi_ML/run_fase1_evaluation.py`), bukan membuat pipeline paralel baru. Periksa argumen `--help` dan kode terkini sebelum menjalankan. Reproduksi historis tetap terpisah dari evaluasi kandidat.

- Split waktu atau kelompok sesi untuk data pengukuran; preprocessing hanya fit training. Hindari rekaman yang sangat berdekatan tersebar acak sebagai satu-satunya bukti generalisasi.
- Bandingkan baseline yang masuk akal, RF sensor saja, dan RF sensor + T/RH pada target, satuan dan holdout yang sama. Laporkan jika RF kalah; jangan memilih ulang split agar menang.
- Jangan membandingkan langsung RMSE legacy berskala x1000 dengan kandidat berskala sumber. Jangan menghitung peningkatan dari dua holdout berbeda.
- Simpan MAE, RMSE, R2, prediksi per baris, residual terhadap waktu/T/RH, rentang input, keluaran mentok/datar dan metrik per blok waktu bila tersedia.
- Persentase penurunan error = 100 × (error baseline − error kandidat) / error baseline, hanya untuk pembandingan setara; baseline nol diberi tidak terdefinisi. R2 bukan persentase akurasi sensor.
- Keluaran: report/model card, hash data dan kode, seed/split, model Python tersimpan, header kandidat, CSV perbandingan, PNG grafik dan laporan ringkas. Gunakan folder run baru; perbarui tautan laporan utama agar pengguna tidak bingung banyak folder.
- Uji ekspor Python versus C++ pada holdout dan sekitar threshold pohon dengan toleransi tertulis. Kelulusan host tidak sama dengan pengukuran latensi di ESP32.

## 5. Integrasi firmware hanya setelah keputusan model

Pertahankan pin, FreeRTOS pemisah sampling/jaringan, pulsa GP2Y, kendali bertingkat, hysteresis/dwell, pemisahan timer buzzer dan fan, serta telemetri STZ4. Perbaiki hanya jika ditemukan kesalahan dengan bukti.

Uji jalur konsentrasi → sub-indeks → maksimum → kategori. CO target mg/m3, konversi tampilan ppm dan masukan tabel ug/m3 harus konsisten. Periksa tabel dari [Permen LHK 14/2020](https://ppkl.menlhk.go.id/website/filebox/988/210704011643PERMEN%20ISPU%20NO%2014%20TAHUN%202020.pdf), batas kategori, pembulatan, invalid, saturasi, dominasi PM/CO dan ring rata-rata 24 jam. Indeks instan tetap diberi label terpisah dari rata-rata 24 jam.

STZ4 tetap: 1 T, 2 RH, 3 PM nominal, 4 CO ppm nominal, 5 indeks instan, 6 PWM%, 7 MQ135 ADC, 8 kategori. Status menyimpan raw GP/MQ7 dan metadata. Jika kontrak perlu berubah, versi/schema dan dokumentasi harus ikut berubah; arsip lama tidak diinterpretasi dengan kontrak baru.

Tes relevan: `python -m unittest discover -s tests -p 'test_*.py'`, kompilasi/jalankan `tests/ispu_v4_test.cpp` dengan include firmware, pemeriksaan parity model, lalu build PlatformIO dari `Program/Kode`. Periksa test/kode untuk perintah compiler yang sesuai lingkungan. Catat hasil aktual, bukan menyalin kelulusan sebelumnya. Tidak perlu menjalankan semua eksperimen lama berulang jika tidak terdampak.

## 6. Status perangkat yang harus diverifikasi ulang

[Verifikasi tersimpan](verifikasi_revisi_v4.json) mencatat kandidat lokal v4.0.0 build `a945ea070fcc`, build dan 14 tes Python serta tes C++ lulus, **uploaded=false, physical_acceptance_passed=false**. Cloud yang teramati sebelumnya memakai build `42429e9eca53`, bukan bukti kandidat lokal sudah terpasang. Ini catatan historis, bukan pemeriksaan feed langsung hari ini.

README/roadmap lama menyebut upload v4 berhasil; itu tidak berarti semua revisi v4 berikutnya sudah di-upload. Perbarui kalimat status berdasarkan hash/manifest, bukan sekadar nomor versi. Jangan menimpa bukti upload lama; bedakan kandidat lokal, build, upload, boot serial dan feed aktual.

Snapshot sebelumnya: 94 baris, sekitar 32 menit, terdapat gap 60 detik dan dua pengiriman gagal. Laporan `Program/data/downloads/audit_20260910_002359_corrected.json`. Ini bukan data satu jam lengkap atau bukti tanpa putus. Penyebab gap tersebut belum dipastikan; jangan otomatis menyamakan dengan kejadian router mati pada sesi lama.

## 7. Syarat mulai pengambilan utama tujuh hari

- [ ] Metode dan unit kedua model sudah diputuskan; ketidakcocokan penting tidak ditutup hanya dengan label estimasi.
- [ ] Evaluasi, model Python, header, kontrak fitur dan sumber dapat ditelusuri.
- [ ] Kandidat integrasi lolos tes relevan dan build; hash model/firmware dicatat.
- [ ] Firmware final benar-benar di-upload dan hash boot/feed cocok.
- [ ] Uji singkat sesuai protokol (minimal 15 menit) lulus; fan benar-benar berputar, sensor/telemetri valid, reset/fault ditangani. Bukan uji pembakaran atau membuat CO di kamar.
- [ ] Dokumentasi model, firmware, README dan protokol sesuai versi final. Semua status selesai memiliki bukti.
- [ ] Pemilik menerima konfigurasi dan batas hasil yang konkret, lalu t0 ditetapkan. Mulai 168 jam dengan ESP32 dan Wi-Fi saja; tidak ada kewajiban PC logger.

Setelah lolos, bekukan kode/model dan pengaturan fisik untuk sesi. Gangguan router/power dicatat; jangan mengisi data hilang dengan angka normal. Perubahan yang memang harus dilakukan dipisahkan sebagai segmen/version baru. Tidak ada janji tanpa gap atau akurasi setara alat mahal.

## Bentuk jawaban akhir Antigravity

Jawab singkat: apa yang diubah; lokasi CSV/grafik/model; hasil pengujian; model yang dipilih dan alasan; apakah versi itu sudah di-upload; apakah boleh mulai 168 jam. Jika belum boleh, sebut satu per satu hambatan yang tersisa beserta solusi nyata dan pekerjaan yang akan diambil AI. Jangan mengulang audit sebagai pengganti penyelesaian, memberi skor peluang Sinta tanpa dasar, atau meminta pemilik menjalankan pekerjaan software yang bisa dikerjakan sendiri.
