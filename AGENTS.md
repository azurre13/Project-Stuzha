# Panduan AI untuk Project Stuzha

## Urutan membaca

Baca [README](README.md), [planning](MD/konteks%20_planing_jurnal_AQI.md), [roadmap](MD/roadmap_dan_langkah_selanjutnya.md), dan [protokol 7 hari](MD/protokol_pengambilan_data_7_hari.md), lalu dokumentasi topik sebelum kode/data. Dokumen bukan bukti perangkat telah di-upload. Periksa versi aktif, output build, dan status feed.

## Keputusan pemilik

- Fokus prototipe monitoring indoor; filter dan kipas pendukung. CADR, HEPA, kebisingan dan efisiensi energi bukan target wajib.
- Sensor terpasang MQ-7 dan MQ-135; jangan mengembalikan dugaan MQ-2 dari naskah/legacy.
- Pin dikonfirmasi dan dipertahankan; konfigurasi ada pada [hardware](Hardware/hardware_stuzha.md).
- Casing gabus keras, karbon kotak + potongan filter mobil non-HEPA, celah sekitar 5 cm, fan 12 × 12 cm, intake bawah/samping, exhaust atas.
- Belum ada instrumen pembanding. Jangan menyimpulkan akurasi sensor dari R², grafik halus, respons asap, atau banyaknya data.
- Selama tujuh hari hanya ESP32 dan Wi-Fi menyala. PC logger bukan prasyarat. Suplai 12 V ke fan/expansion; expansion menyediakan 5 V. Siklus heater MQ-7 belum terbukti.

## Kontrak revisi 4 — arahan pemilik mengembalikan tujuan awal

Tujuan tetap low-cost sensor → TinyML → estimasi PM/CO → sub-indeks menurut tabel Permen LHK14/2020 → maksimum → kategori/kendali. Jangan mengganti tujuan dengan raw-only atau skor baseline relatif. Field STZ4: 1T,2RH,3PM nominal,4CO nominal ppm,5indeks estimasi instan,6PWM%,7MQ135ADC,8kode kategori. Status a menyimpan GP/MQ7 ADC; f flags, s sequence, d mean24/indeks24/coverage. Pisahkan arsip STZ3/STZ31 yang kontraknya berbeda.

Kode v4 memakai tabel PM dan CO dalam ug/m3 dengan basis regulasi24jam; index instan untuk kendali diberi label eksplisit terpisah dari estimasi24jam. Tidak ada baseline kendali setiap boot. Dwell turun8detik, histeresis5%, alarm tidak mengikuti fan yang masih melambat. Saturasi bukan bukti PM tertentu atau pasti kerusakan hardware.

Model lama tetap identik. PM memakai asumsi skala ug/m3 nominal legacy yang belum terverifikasi, bukan unit fisik yang sudah diselesaikan. CO target mg/m3 bukan ppm, pemetaan PT08-ke-MQ7 belum tervalidasi; konversi tampilan ppm pada25C/1atm. Jangan mengarang R0/gain/kalibrasi, mengklaim akurasi meningkat, atau menganggap label estimasi menyelesaikan mismatch model. Rujuk [metode v4](MD/metode_ispu_v4.md). Pemilik tidak memiliki instrumen pembanding; membeli/meminjam bukan prasyarat revisi kode.

Tidak ada klaim ISPU resmi, konsentrasi tervalidasi, penghilangan CO atau rekaman offline tanpa kehilangan. Gap router mati adalah keterangan pemilik. Pisahkan edit/build dari upload dan uji fisik.

## Aturan bekerja

### Preferensi komunikasi pemilik — 10 September 2026

- Setiap kritik atau temuan kekurangan harus disertai solusi konkret, langkah yang akan dikerjakan AI, dan hasil yang akan diserahkan. Jangan berhenti pada daftar masalah atau mengulang keterbatasan.
- Gunakan bahasa sederhana dengan pola yang diminta pemilik: "Solusinya bisa begini ... Biar aku selesaikan dengan begini ... Setuju untuk aku bereskan?" Pertanyaan persetujuan dipakai untuk usulan baru yang membutuhkan keputusan; pekerjaan yang sudah diizinkan langsung dituntaskan tanpa meminta izin berulang.
- AI mengambil tanggung jawab pencarian referensi/data, perbaikan kode, training, dan evaluasi yang dapat dikerjakan dengan akses tersedia. Jangan melempar pekerjaan tersebut kembali kepada pemilik. Jika ada hambatan nyata, jelaskan singkat dan berikan alternatif yang bisa dikerjakan AI; jangan menjanjikan hasil yang belum terbukti.

- Jaga perubahan lokal pemilik dan semua data asli. Jangan hapus lonjakan atau isi missing dengan angka normal tanpa penanda.
- Perbaikan kode diizinkan oleh pemilik pada 8 September 2026. Bedakan edit, build, training, upload dan uji perangkat.
- Kredensial berada di secrets.h yang diabaikan Git. Jangan tampilkan nilainya. Binari firmware mengandung konfigurasi lokal dan tidak untuk dipublikasikan.
- Training/evaluasi kini memakai satu pipeline dan menghasilkan folder run baru. Tidak boleh mengganti header aktif secara otomatis. Header legacy deployment dipertahankan untuk keterlacakan; model benchmark baru bukan model MQ-7 pengganti.
- Jangan overwrite dataset lama dengan keluaran downloader baru. Default menghasilkan snapshot baru. Tidak ada feed bukan izin mengosongkan arsip.
- Tes software yang relevan wajib lulus sebelum menyatakan perbaikan selesai; uji fisik tidak dapat digantikan build.
- Update dokumentasi pemilik topik saat kontrak berubah. Jangan menyalin klaim status lama ke semua Markdown.
- Artefak/grafik lama memiliki label yang belum valid. Perlakukan sebagai arsip, bukan sumber kebenaran metode.
- Kutip sumber primer yang benar-benar dibaca. Koleksi 21 artikel merupakan kandidat, bukan seluruhnya telah diverifikasi.
