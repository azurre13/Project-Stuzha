# Planning penelitian Stuzha

Diperbarui 9 September 2026. Tujuan pemilik: memperbaiki prototipe monitoring indoor dan menyiapkan pengumpulan data tujuh hari untuk Bab 3. Kipas/filter pendukung; tidak ada alat pembanding konsentrasi.

## Pertanyaan dan kontribusi yang dievaluasi

Bagaimana implementasi dua estimator TinyML di ESP32 memengaruhi keputusan aktuator lokal, dan seberapa konsisten monitoring serta telemetrinya selama operasi kamar yang kondisi/versinya dicatat? Akurasi konsentrasi dan keberhasilan kompensasi drift merupakan pertanyaan terpisah yang belum dapat dijawab data tanpa rujukan.

Kontribusi terhadap naskah lama: data mentah yang dapat ditelusuri ke versi/boot, diagnosis kegagalan dan timing, pemisahan akuisisi dari jaringan, evaluasi kontrol relatif dengan histeresis/dwell, serta pengukuran komputasi TinyML. Naskah lama sudah memiliki IoT dan kendali bertingkat; keberadaan komponen tersebut bukan kebaruan baru. Hasil eksperimen menentukan apakah ada peningkatan, bukan nama algoritma.

## Implementasi yang dipilih

V4 mengembalikan tujuan awal: dua sensor utama bersama T/RH → dua RF → estimasi PM/CO → interpolasi sub-indeks → maksimum/kategori → kipas. MQ135 adalah proksi gas campuran. Indeks instan untuk respons cepat dan estimasi24jam untuk pembahasan dipisahkan. Kendali tidak lagi memakai baseline relatif setiap boot. [Metode v4](metode_ispu_v4.md) dan [firmware](../Program/Kode/firmware_stuzha.md) memiliki kontrak aktif.

Tidak ada klaim bahwa satuan PM legacy atau pemetaan MQ7 telah terkalibrasi. Keluaran PM memakai asumsi nominal legacy yang ditandai; CO memiliki target asal mg/m3. Mengembalikan fungsi ISPU tidak menyelesaikan mismatch model. Penelitian tetap memusatkan fungsi yang diminta pemilik, dengan hasil dibatasi bukti yang tersedia.

Cloud menjadi rekaman utama karena hanya ESP32+Wi-Fi menyala. Raw GP/MQ7 ada di status a; indeks/kategori kembali ke field5/8. Ring24jam berada di RAM, tidak memerlukan PC dan hilang saatreset; snapshot offline tidak memiliki replay.

## Metode yang diizinkan bukti

| Klaim | Bukti yang dibutuhkan / status |
|---|---|
| Operasi monitoring 168 jam | Sesi bertimestamp, logbook awal/akhir, versi, data cloud; belum dikumpulkan |
| Kelengkapan telemetri | Slot yang teramati, gap, counter, reset; jangan mengklaim packet-loss dari ID berurutan |
| Logika aktuasi | Uji batas software telah dibuat; respons fan/buzzer fisik perlu uji penerimaan |
| Latensi inferensi | Instrumentasi micros pada perangkat; nilai hardware belum tersedia |
| Konsistensi ekspor benchmark | Prediksi sklearn dibanding C++ pada holdout dan probe batas; hasil baru tersedia |
| Akurasi konsentrasi sensor | Belum dapat diklaim tanpa pasangan referensi relevan |
| Efisiensi filtrasi / energi | Di luar kontribusi yang diuji; jangan diturunkan dari penurunan ADC atau duty |

## Eksperimen ML

Satu pipeline baru memisahkan benchmark UCI dan simulasi PM. CO target mg/m3, fitur PT08.S1 asli + T/RH, split kronologis, baseline hanya fit training. Benchmark ini bukan kalibrasi MQ7. RF tiga fitur tidak mengungguli baseline linear tiga fitur pada holdout yang diperiksa; laporkan tanpa memilih ulang split agar RF terlihat lebih baik.

Simulasi PM mempertahankan angka dataset asli tanpa konversi x1000. Unit fisik sumber masih unresolved. Koefisien gangguan merupakan asumsi simulasi, bukan parameter sensor terukur. Hasil simulasi tidak dimasukkan sebagai bukti akurasi lapangan. Model baru diekspor ke folder run terpisah dan tidak mengganti model deployment eksperimental aktif.

## Rancangan lapangan dan Bab 3

Gunakan [protokol tujuh hari](protokol_pengambilan_data_7_hari.md). Tetapkan tempat, orientasi, filter, catu daya, versi dan jam mulai sebelum studi. Uji penerimaan singkat dilakukan lebih dulu. Pengujian batas memakai input software, bukan pembakaran bahan di kamar. Selama observasi gunakan aktivitas normal dan catat AC, pintu/jendela, okupansi, kegiatan, router/power dan perubahan posisi.

Bab 3 memuat rakitan aktual, variabel, jadwal sampling, skema data, persamaan kendali, protokol, definisi metrik dan batas validasi. Bab hasil diisi setelah data tersedia; jangan menulis hasil tujuh hari atau manfaat ML terlebih dahulu.

Judul kerja: **Prototipe Monitoring Kualitas Udara Indoor Berbiaya Rendah Berbasis TinyML dengan Estimasi Indeks Pencemar dan Kendali Kipas Adaptif**. Judul akhir mengikuti hasil dan scope jurnal. Sinta 2/3 bukan sertifikat kesiapan atau jaminan penerimaan.

## Acuan

Baca [daftar sumber primer dan kandidat](../referensi/referensi%20garnie/daftar_referensi.md). Permen LHK dipakai untuk menjelaskan mengapa output sesaat dari input tak tervalidasi tidak disebut ISPU resmi. WHO bukan pengganti tabel ISPU. Data publik dan hasil jurnal lain tidak otomatis berlaku pada Stuzha.

## Peran literatur dan pembuktian kontribusi TinyML

[Keputusan v4](metode_ispu_v4.md) menjelaskan Zimmerman, Han dan contoh transfer learning sensor. Literatur mendukung sensor fusion/soft-sensing sebagai pendekatan, tetapi tidak membuat pemetaan PT08 ke MQ7 atau gangguan sintetis PM menjadi kalibrasi fisik Stuzha. Mentransfer eksekusi model ke ESP32 adalah deployment; klaim transfer learning memerlukan mekanisme adaptasi dan evaluasi domain target yang jelas.

Laporkan tiga lapis bukti secara terpisah: benchmark sumber dengan baseline dan split waktu; uji integrasi header deployment yang benar-benar mengubah level; serta observasi raw/model/aktuator dan latensi perangkat selama sesi. Jangan memakai metrik benchmark baru sebagai metrik dua header historis. Uji masukan software menunjukkan keterhubungan algoritma, bukan efisiensi filtrasi atau konsentrasi nyata.

Analisis kontribusi fungsional: tampilkan timeline raw GP/MQ7, output kedua RF, T/RH dan PWM dengan kejadian logbook; laporkan jumlah transisi level, durasi tiap level, invalid model, keluaran datar dan latensi. Perbandingan controller pada input rekaman yang sama hanya simulasi keputusan; tanpa menjalankan kedua kebijakan pada kondisi sebanding, jangan mengklaim kontrol ML membersihkan kamar lebih baik. Snapshot cloud 20 detik tidak cukup untuk merekonstruksi semua dwell/transisi per detik.
