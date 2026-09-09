# Panduan folder evaluasi ML Stuzha

**Buka [laporan utama](laporan_evaluasi_metrik.md)** untuk melihat perbandingan sebelum–sesudah RF, persentase penurunan error, tabel CSV, dan grafik.

## Susunan folder

| Lokasi | Isi |
|---|---|
| laporan_evaluasi_metrik.md | Ringkasan utama dan tautan ke hasil rinci |
| tabel_metrik_evaluasi.csv | Ringkasan angka dan persentase dari hasil uji |
| grafik/ | Grafik ringkasan utama |
| hasil/reproduksi_awal_20260909_124230_faba1c/ | Training dengan metode awal, model, prediksi CSV, dan delapan grafik PM/CO |
| hasil/evaluasi_20260909_124246_f546a8/ | Evaluasi tambahan dengan split waktu, baseline linear/RF, CSV dan delapan grafik |
| arsip/sebelum_revisi/ | Laporan, CSV dan grafik lama; dipertahankan sebagai riwayat |

Dua folder hasil bukan duplikat: metode awal menggunakan split acak; evaluasi tambahan menggunakan split waktu. Jangan mencampur metrik keduanya sebagai bukti peningkatan versi firmware. Ringkasan utama hanya menautkan data rinci, tidak menyalin seluruh prediksi/grafiknya.

## Menjalankan kembali

```sh
python Fase_1_Evaluasi_ML/run_fase1_evaluation.py
python Fase_1_Evaluasi_ML/run_fase1_evaluation.py --experiment legacy-recovery
```

Perintah pertama menjalankan kedua eksperimen split waktu. Perintah kedua mereproduksi training awal. Keduanya membuat folder hasil baru, lengkap dengan CSV perbandingan sebelum–sesudah dan PNG; tidak menimpa arsip atau model firmware. Ringkasan utama saat ini menunjuk hasil tanggal 9 September 2026, bukan otomatis hasil run berikutnya.

## Bukti metode dan ekspor

- [Training dan fitur](../ml_training/training_ml_stuzha.md) menjelaskan data sumber, preprocessing dan split.
- [Audit reproduksi awal](reproduksi_legacy_20260909.json): header PM dapat direproduksi; header CO aktif berbeda dari rekonstruksi. Kandidat belum mengganti firmware.
- [Catatan UCI sebelumnya](evaluasi_uci_kronologis_20260908.json) dan [catatan simulasi PM sebelumnya](evaluasi_pm_simulasi_20260908.json) merupakan bukti run terdahulu.
- [Keputusan deployment](../MD/metode_ispu_v4.md) menjelaskan hubungan model dengan firmware.

PM memakai masukan sintetis dan skala legacy yang belum tervalidasi fisik. CO memakai data PT08, bukan pasangan MQ-7–rujukan. Persentase dalam laporan menyatakan penurunan error pada data uji eksperimen, bukan persentase akurasi sensor rakitan. R² bukan persentase akurasi.
