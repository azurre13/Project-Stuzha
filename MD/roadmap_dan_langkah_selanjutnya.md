# Roadmap perbaikan dan evaluasi Stuzha

Diperbarui 8 September 2026. Fokus: prototipe monitoring indoor; filter dan kipas sebagai pendukung. Alat tidak perlu dianggap gagal atau dirakit ulang hanya karena validasi belum lengkap.

## Status saat ini

| Bagian | Status |
|---|---|
| Rakitan dan pembacaan/IoT | Beroperasi menurut pemilik; snapshot awal tersedia |
| Uji kamar awal | 3.126 baris selama 17 jam 22 menit 22 detik |
| Pengujian satu minggu | Berlangsung menurut pemilik; snapshot lokal yang dianalisis masih sesi awal |
| Model dan ekspor C | Tersedia, masih eksperimental |
| Kalibrasi fisik dan akurasi absolut | Belum tervalidasi; tidak ada alat pembanding |
| Sensor gas | MQ-7 untuk CO dan MQ-135 untuk proksi VOC/gas campuran, dikonfirmasi pemilik |
| Varian board | Masih perlu dicocokkan dengan marking |
| Pin | Dinilai sudah benar oleh pemilik; pertahankan konfigurasi kerja, belum diverifikasi independen |
| Dokumentasi | Diselaraskan dengan kondisi dan batas bukti terbaru |
| Perbaikan kode di bawah | Belum dikerjakan pada pembaruan dokumentasi ini |

## Tahap 1 — amankan keterlacakan data

- [ ] Simpan salinan data serta versi firmware/model yang menghasilkan sesi lama.
- [x] Konfirmasi sensor gas: MQ-7 untuk CO dan MQ-135 untuk indikator/proksi VOC atau gas campuran.
- [ ] Catat varian board, part number GP2Y, serta foto/wiring dan posisi MQ-7/MQ-135.
- [ ] Tambahkan raw ADC semua sensor analog, suhu/RH, status validitas, output model, dan perintah PWM ke log.
- [ ] Catat uptime, alasan reset, versi firmware/model, dan kejadian jaringan.
- [ ] Pisahkan nilai fallback DHT dari pengukuran valid.
- [ ] Sediakan log lokal selama offline; tandai perubahan AC, aktivitas, posisi, dan awal/akhir sesi.
- [ ] Perbaiki downloader dengan rentang tanggal/waktu, deduplikasi, pemeriksaan cakupan, serta arsip yang tidak tertimpa hasil parsial.

Hasil yang diharapkan: setiap rekaman dapat ditelusuri ke input dan versi perangkat. Sesi sebelum/sesudah perubahan tetap dapat dibedakan. Tidak perlu membuang data 18 jam; gunakan sebagai uji pendahuluan.

## Tahap 2 — telusuri pembacaan dan benahi implementasi

- [ ] Periksa raw ADC, tegangan, catu daya, timing GP2Y, dan pengaruh kecepatan kipas pada PM.
- [ ] Telusuri 84,39% output PM yang menetap pada 0,00031 serta tiga lonjakan besar. Jangan hapus outlier tanpa alasan terdokumentasi.
- [ ] Verifikasi kebutuhan pemanasan sensor gas menurut tipe aktual.
- [ ] Tinjau penonaktifan brownout detector dan penyebab gangguan daya.
- [ ] Perbaiki satuan, breakpoint, interpolasi, waktu perataan, dan label indeks.
- [ ] Lengkapi dan uji histeresis, termasuk batas 300. Dokumentasikan aturan waktu stabil bila ditambahkan.
- [ ] Tentukan kebutuhan booster MQ-135. Jika dipakai, implementasikan dan uji; ADC 2.500 bukan batas kesehatan tervalidasi.
- [ ] Evaluasi blocking pada jaringan/alarm dan ukur interval loop aktual.

Hasil yang diharapkan: perilaku kode sesuai spesifikasi yang ditulis dan anomali dapat ditelusuri. Filtering noise dipilih setelah diagnosis serta dievaluasi dampaknya pada respons.

## Tahap 3 — evaluasi prototipe monitoring

- [ ] Uji semua tingkat PWM dan batas logika dengan input software yang diberi label simulasi.
- [ ] Uji kegagalan sensor, offline/reconnect, serta restart yang terkendali.
- [ ] Ukur distribusi latensi inferensi, flash, dan heap runtime; periksa kesesuaian Python/C.
- [ ] Rekam sesi operasional berulang dengan kondisi kamar dan versi perangkat tercatat.
- [ ] Laporkan missing/gap, reset, error sensor, dan respons aktual; jangan menyamakan ID cloud berurutan dengan uptime sempurna.
- [ ] Dokumentasikan filter non-HEPA dan aliran aktual, foto komponen, serta skematik.

Durasi satu minggu dapat menjadi uji operasi berkelanjutan. Banyaknya baris berdekatan bukan banyaknya eksperimen independen. Pengujian kamar dengan AC tidak memisahkan pengaruh AC, aktivitas, kipas, dan filter secara otomatis.

## Tahap 4 — rapikan eksperimen ML dan naskah

- [ ] Telusuri skala PM Mendeley dan satuan target CO UCI.
- [ ] Perbaiki split waktu/sesi dan fit preprocessing/baseline hanya pada training.
- [ ] Beri versi artefak dan perbaiki teks generator laporan sebelum training ulang.
- [ ] Tandai eksperimen PM sintetis dan benchmark CO secara eksplisit.
- [ ] Hindari klaim kalibrasi fisik tanpa pasangan data referensi. Jika akses pembanding diperoleh, buat protokol co-location terpisah.
- [ ] Tulis pendahuluan/metode sesuai fokus monitoring; tentukan kontribusi dari hasil nyata.
- [ ] Periksa artikel pembanding dan perbedaan dengan karya tim sebelumnya.
- [ ] Pilih jurnal sesuai scope; sesuaikan template serta tuntutan bukti.

Klaim CADR, efisiensi filtrasi, penghilangan CO, dB, RPM aktual, dan penghematan energi bukan keluaran wajib untuk fokus monitoring ini. Jika dimasukkan, ukur besaran terkait dengan metode yang layak.

## Dampak pembaruan dokumentasi

Dokumentasi, komentar sensor firmware, dan deskripsi eksplorasi dataset telah dikoreksi. Logika firmware, model, CSV, dan grafik tidak diubah; tidak ada training ulang atau upload perangkat. Generator evaluasi masih dapat menimpa laporan Markdown dengan klaim lama ketika dijalankan. Perubahan logger, downloader, dan model perlu dikerjakan sebagai langkah berikutnya dengan versi baru. Panduan menjaga konteks berada di [AGENTS.md](../AGENTS.md).
