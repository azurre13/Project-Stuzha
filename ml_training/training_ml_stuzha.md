# Training dan eksplorasi model Stuzha

Folder ini berisi skrip Python pendukung eksperimen model. Fokus proyek tetap prototipe monitoring; status validasi dijelaskan di [evaluasi ML](../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md).

## Peran skrip

| Skrip | Masukan | Keluaran/efek samping |
|---|---|---|
| [explore_datasets.py](explore_datasets.py) | Dataset Mendeley dan UCI di Program/data | Ringkasan eksplorasi di terminal; interpretasi lama dalam teks bukan bukti kalibrasi |
| [train_models.py](train_models.py) | Dataset Mendeley dan UCI | Melatih RF dan menimpa model_pm.h/model_co.h di Program/Kode/include |
| [run_fase1_evaluation.py](../Fase_1_Evaluasi_ML/run_fase1_evaluation.py) | Dataset yang sama | Pipeline lain untuk training/evaluasi; menimpa header, metrik, grafik, dan laporan |

Dua pipeline training tersedia; belum ada satu pipeline terversi yang ditetapkan sebagai acuan final. Jangan menganggap menjalankan salah satunya tidak memengaruhi model firmware.

## Batas metode saat ini

- PM memakai input sintetis yang dibentuk dari target dan gangguan buatan.
- CO memakai sensor UCI; pemetaan skala ADC belum memvalidasi transfer ke MQ-7.
- Identitas MQ-7/MQ-135 pada perangkat sudah dikonfirmasi. MQ-135 digunakan untuk proksi VOC/gas campuran dan tidak memiliki model kalibrasi VOC pada kedua pipeline.
- Satuan, split evaluasi, dan baseline masih perlu diperbaiki. Rincian serta metrik arsip ada di [evaluasi ML](../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md) dan [data](../Program/data/dataset_stuzha.md).
- Docstring, pesan terminal, dan generator laporan masih mengandung klaim lama seperti perbaikan leakage/kalibrasi selesai. Itu tidak menggantikan hasil pemeriksaan metode.

## Sebelum training berikutnya

Catat pipeline, versi kode, hash dataset, parameter, split, serta dependensi. Simpan keluaran ke lokasi/versi terpisah dan periksa dampaknya sebelum mengganti header aktif. Perbaiki teks generator bersama metode agar laporan lama tidak muncul kembali. Catat apakah model baru hanya diekspor, sudah dibuild, atau benar-benar di-upload; ketiganya berbeda.

Tidak ada training ulang pada rangkaian pembaruan dokumentasi 8 September 2026.
