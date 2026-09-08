# Panduan AI untuk Project Stuzha

## Mulai membaca

1. Baca [README utama](README.md) untuk tujuan, keputusan pemilik, dan status terkini.
2. Baca [planning](MD/konteks%20_planing_jurnal_AQI.md) dan [roadmap](MD/roadmap_dan_langkah_selanjutnya.md) untuk ruang lingkup serta pekerjaan terbuka.
3. Baca dokumentasi pada bagian yang dikerjakan: [hardware](Hardware/hardware_stuzha.md), [firmware](Program/Kode/firmware_stuzha.md), [data](Program/data/dataset_stuzha.md), [training](ml_training/training_ml_stuzha.md), atau [evaluasi ML](Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md).
4. Cocokkan klaim implementasi dengan kode aktif. Untuk klaim numerik, periksa data dan metode yang menghasilkan angka tersebut.

## Keputusan proyek yang harus dipertahankan

- Tujuan utama adalah prototipe **monitoring kualitas udara indoor**. Kipas dan filtrasi merupakan pendukung. Jangan mengubah fokus menjadi penelitian kinerja purifier tanpa arahan pemilik.
- Sensor gas terpasang adalah **MQ-7 untuk CO** dan **MQ-135 untuk indikator/proksi VOC atau gas campuran**. Identitas ini sudah dikonfirmasi; jangan mengulang dugaan MQ-2 dari riwayat lama.
- MQ-135 saat ini menghasilkan ADC mentah di field 7, bukan konsentrasi VOC/TVOC terkalibrasi dan bukan bagian sub-indeks ISPU.
- Rakitan aktual: gabus keras, intake bawah, karbon kotak, filter mobil dipotong, ruang sekitar 5 cm, kipas 12 × 12 cm, exhaust atas. Filter bukan HEPA.
- Pin saat ini dinilai sudah benar oleh pemilik. Pertahankan pemetaan pin; jangan menganggapnya salah atau memindahkannya hanya karena komentar menyebut S3. Periksa kembali jika ada bukti teknis relevan dengan tugas. Varian board yang belum terdokumentasi adalah persoalan terpisah.
- Belum tersedia alat pembanding. Jangan menyimpulkan akurasi konsentrasi dari output model, grafik yang halus, atau lama operasi.

## Cara menangani sumber yang berbeda

- Instruksi dan klarifikasi terbaru pemilik mengarahkan tujuan serta fakta rakitan. Catat tanggal dan sumber pembaruan, tanpa mengubah dugaan menjadi hasil pengukuran.
- Kode aktif menunjukkan implementasi dalam repositori; belum membuktikan versi yang terpasang pada perangkat atau perilaku hardware yang telah diuji.
- CSV menunjukkan rekaman pada periode dan versi yang dapat ditelusuri. Statistik di README adalah snapshot bertanggal, bukan ringkasan otomatis file yang kelak diperbarui.
- README bagian menjadi acuan penjelasan topik. Jika kode bertentangan dengan README, jelaskan perbedaan dan perbarui status; jangan diam-diam menganggap salah satunya telah tervalidasi.
- Komentar/banner kode, grafik lama, hasil generator, dan folder legacy bukan bukti kebenaran ilmiah. Ada klaim lama yang belum diperbaiki dalam generator.
- Literatur memberi metode dan konteks. Hasil studi lain tidak menjadi hasil Stuzha.

## Aturan perubahan dan pelaporan

- Pertahankan perubahan lokal pemilik dan data asli. Bedakan perubahan dokumentasi, komentar, logika, training, build, dan upload.
- Jangan menjalankan skrip training/evaluasi hanya untuk membaca konteks: skrip dapat menimpa header, metrik, grafik, dan laporan. Jika tugas memerlukan eksekusi, gunakan keluaran terpisah/versi atau salinan kerja agar arsip terjaga.
- Jangan menjalankan downloader pada satu-satunya arsip CSV; implementasi pagination masih bermasalah. Perbaiki/isolasi keluaran sesuai tugas terlebih dahulu.
- Jangan mengubah data pengujian, membuang lonjakan, atau memakai prediksi sendiri sebagai ground truth tanpa dasar metode yang dijelaskan.
- Saat memperbaiki fungsi, perbarui README pemilik topik serta status roadmap yang terdampak. Hindari menyalin rincian yang sama ke banyak dokumen baru.
- Nyatakan verifikasi yang benar-benar dilakukan. Build berhasil bukan validasi sensor, perubahan komentar bukan perbaikan logika, dan perubahan repositori bukan bukti firmware telah di-upload.
- Kerjakan bagian yang sudah jelas tanpa meminta ulang fakta yang telah dikonfirmasi. Pertanyaan hanya untuk informasi yang memengaruhi tindakan dan belum tersedia.
