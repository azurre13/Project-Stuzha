# Planning penelitian Stuzha

Acuan diperbarui 8 September 2026 setelah penegasan pemilik: **tujuan utama adalah prototipe monitoring kualitas udara indoor**. Kipas dan filter merupakan fitur pendukung. Detail fisik mengacu pada [Hardware](../Hardware/hardware_stuzha.md).

## Pertanyaan penelitian

Seberapa andal prototipe melakukan pembacaan, pemrosesan lokal, pencatatan IoT, dan respons aktuator pada kondisi pengujian indoor yang didokumentasikan?

Fokus evaluasi:
- Kelengkapan dan interval data, kegagalan sensor, reset, dan pemulihan koneksi.
- Konsistensi implementasi pemrosesan dan logika kontrol.
- Latensi dan kebutuhan memori inferensi lokal.
- Keterulangan respons pada sesi yang kondisi serta versinya tercatat.

Akurasi konsentrasi absolut, koreksi bias sensor oleh ML, CADR, efisiensi filter, kebisingan dan penghematan energi hanya dapat diklaim jika tersedia pengujian yang mendukung masing-masing besaran.

## Konfigurasi aktual dan ketidakpastian

Casing gabus keras, intake bawah, exhaust atas. Susunan: intake → karbon kotak → filter mobil dipotong → ruang kosong sekitar 5 cm → kipas 12 × 12 cm. Filter bukan HEPA. Lubang GP2Y horizontal di intake. MQ-7 untuk CO dipasang tegak pada dinding bawah sebelum filter. MQ-135 digunakan sebagai indikator/proksi VOC atau gas campuran. Kedua sensor gas telah dikonfirmasi pemilik.

Kode telah memakai MQ-7 dan MQ-135 sesuai klarifikasi pemilik. Sebagian komentar menyebut ESP32-S3, sedangkan PlatformIO memakai esp32dev; varian board masih perlu dicocokkan dengan marking. Posisi MQ-135 serta DHT22 perlu dilengkapi dalam dokumentasi fisik. Koreksi identitas sensor tidak menyelesaikan validasi model atau konsentrasi.

Pemilik menilai pemetaan pin sudah benar. Gunakan konfigurasi kerja yang ada; jangan menganggap pin bermasalah hanya dari perbedaan penyebutan board. Detail status dan tabel pin dimiliki oleh [Hardware](../Hardware/hardware_stuzha.md).

## Status bukti

- Prototipe fisik berjalan.
- Snapshot uji pendahuluan kamar tersedia: 3.126 baris, 6 September 2026, 01.00.11–18.22.33 WIB.
- Pemilik menyatakan AC disetel 24–27°C; suhu sensor tidak harus sama dengan setpoint.
- Belum ada alat pembanding PM/gas.
- Raw PM dan raw sensor gas utama belum tersedia dalam CSV cloud.
- Model RF dan header tersedia, tetapi kalibrasi perangkat belum tervalidasi.
- Pencatatan satu minggu masih merupakan pekerjaan berjalan; snapshot lokal yang diperiksa belum satu minggu.

## Peran ML

Model PM sekarang dievaluasi dengan input sintetis yang dibentuk dari target. Model CO merupakan benchmark pada sensor UCI yang responsnya dipetakan ke skala ADC. Hasil tidak membuktikan peningkatan akurasi GP2Y atau MQ-7 pada Stuzha. MQ-135 dibaca sebagai proksi VOC/gas campuran dan tidak memiliki model kalibrasi VOC dalam implementasi saat ini.

Sebelum eksperimen ML lanjutan:
1. Telusuri satuan PM Mendeley dan perbaiki label satuan CO UCI.
2. Pisahkan training/validation/test menurut waktu atau sesi yang relevan.
3. Fit preprocessing dan baseline hanya pada training.
4. Evaluasi baseline dan RF pada data uji yang sama; lakukan pembandingan fitur jika ingin membahas manfaat suhu/RH.
5. Validasi kesesuaian output Python dan C serta ukur kinerja komputasi.
6. Untuk klaim kalibrasi fisik, kumpulkan pasangan sensor dan instrumen pembanding pada kondisi yang sama.

Tanpa pembanding, model dapat dibahas sebagai eksperimen pendukung dan demonstrasi implementasi lokal dengan keterbatasan eksplisit. Output model sendiri bukan ground truth kalibrasi baru.

## Indeks dan standar

Acuan yang dipilih tetap Permen LHK 14/2020, tetapi implementasi belum sesuai penuh. Kode saat ini memakai input sesaat, tabel CO berlabel ppm, dan belum menghitung rerata sesuai acuan.

Lampiran menggunakan konsentrasi dalam µg/m³, dengan titik CO 4.000; 8.000; 15.000; 30.000; 45.000 serta basis 24 jam. Tinjau seluruh batas dan interpolasi, bukan hanya mengganti beberapa angka.

Rumus acuan:
```text
I = (Ia - Ib) / (Xa - Xb) × (X - Xb) + Ib
```

Bedakan indikator sesaat untuk respons prototipe dengan pelaporan indeks berbasis waktu perataan. Nyatakan parameter yang dicakup; dua sensor tidak mewakili seluruh parameter ISPU. Koreksi rumus tidak memvalidasi konsentrasi input. MQ-135 diposisikan sebagai respons/proksi gas campuran, bukan sub-indeks resmi.

## Rancangan pengujian tanpa instrumen pembanding

| Pengujian | Bukti yang dikumpulkan | Batas interpretasi |
|---|---|---|
| Operasi berkelanjutan | Timestamp, uptime/reset, flag sensor, jeda data | Kelengkapan cloud berbeda dari uptime perangkat |
| WiFi terputus/pulih | Waktu kejadian, respons loop lokal, reconnect | Perlu log lokal untuk periode offline |
| Injeksi nilai uji software | Transisi ambang, histeresis, alarm, perintah PWM | Uji logika, bukan validasi sensor atau paparan nyata |
| Benchmark inferensi | Distribusi latensi, flash, heap runtime, output Python/C | Tidak membuktikan akurasi konsentrasi |
| Sesi kamar berulang | Raw sensor, posisi alat, setelan AC, aktivitas, versi | Respons relatif; bukan pembuktian efisiensi filtrasi |

Variasikan kondisi secara terencana dan dokumentasikan waktu perubahan. Jangan membuat sumber CO di kamar untuk pengujian. Pengujian batas software cukup menggunakan input simulasi yang diberi label. Tinjau pengaruh aliran kipas dan panas komponen pada pembacaan.

## Arah naskah

Judul kerja: **Evaluasi Operasional Prototipe Monitoring Kualitas Udara Indoor Berbasis ESP32 dengan Pencatatan IoT dan Kendali Kipas Bertingkat**.

Kontribusi harus ditentukan dari hasil eksperimen, bukan daftar komponen. Jika membahas TinyML, jelaskan sumber data, batas generalisasi, dan kinerja komputasi aktual. Jelaskan perbedaan dengan karya tim sebelumnya dan sitasikan jika telah dipublikasikan; hindari mengulang kontribusi yang sama.

Struktur:
1. Pendahuluan: kebutuhan monitoring dan celah evaluasi yang spesifik.
2. Metode: rakitan aktual, versi kode, pemrosesan, skenario, dan definisi metrik.
3. Hasil: data operasional, uji logika, dan benchmark yang benar-benar dilakukan.
4. Pembahasan: batas sensor, kondisi kamar, data publik, dan tidak adanya pembanding.
5. Kesimpulan: klaim yang didukung hasil; validasi fisik sebagai pekerjaan lanjutan bila belum dilakukan.

SINTA 3/2 merupakan target yang harus disesuaikan dengan scope jurnal dan kebaruan hasil. Tidak ada durasi pengambilan data atau jumlah baris yang otomatis menjamin penerimaan.

## Sumber acuan

- [Permen LHK 14/2020, Lampiran ISPU](https://ppkl.menlhk.go.id/website/filebox/988/210704011643PERMEN%20ISPU%20NO%2014%20TAHUN%202020.pdf).
- [Metadata Mendeley](https://data.mendeley.com/datasets/2r232jpfb2/1).
- [Metadata UCI Air Quality](https://archive.ics.uci.edu/dataset/360/air+quality).
- [Zimmerman dkk.: random forest calibration](https://doi.org/10.5194/amt-11-291-2018).
- [Han dkk.: calibrations of low-cost sensors](https://www.mdpi.com/1424-8220/21/1/256).
- [WHO 2021 guidelines](https://iris.who.int/handle/10665/345329), sebagai konteks konsentrasi/paparan, bukan tabel interpolasi ISPU.
- [Koleksi referensi tim](../referensi/referensi%20garnie/daftar_referensi.md).

Hasil studi lain tidak otomatis berlaku pada rakitan ini. Tindak lanjut berada di [roadmap](roadmap_dan_langkah_selanjutnya.md).
