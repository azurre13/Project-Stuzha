# Reproduksi model awal CO - split acak

Training RF mengikuti prosedur awal. PM memakai input sintetis dan skala legacy; CO memakai PT08 yang dipetakan. Baseline CO kini hanya fit training, sehingga dapat berbeda dari baseline arsip yang memakai seluruh data. Hasil ini bukan bukti kalibrasi sensor fisik dan tidak mengganti header firmware.

Satuan angka evaluasi: mg/m³.

| Model | MAE | RMSE | Bias | R² |
|---|---:|---:|---:|---:|
| linear_training_only | 0.48437107 | 0.65802047 | 0.037445299 | 0.77813883 |
| random_forest | 0.43536991 | 0.61107948 | 0.023302619 | 0.80866347 |

## Perbandingan sebelum dan sesudah ML

Pembanding: linear_training_only; model ML: random_forest. Keduanya dinilai pada data uji yang sama.

| Metrik | Pembanding | Setelah RF | Penurunan error |
|---|---:|---:|---:|
| RMSE | 0.65802047 | 0.61107948 | 7.13% |
| MAE | 0.48437107 | 0.43536991 | 10.12% |

Rumus: 100 × (error pembanding − error RF) / error pembanding. Nilai negatif berarti RF lebih buruk. Persentase ini adalah perubahan error pada eksperimen dataset, bukan persentase akurasi sensor fisik atau peningkatan firmware baru atas firmware lama.

[Unduh tabel perbandingan CSV](perbandingan_sebelum_sesudah.csv)


CSV berisi seluruh 1,469 baris uji. Scatter menampilkan maksimal 2.500 baris yang dipilih merata menurut urutan data; metrik memakai seluruh baris.

[Prediksi CSV](test_predictions.csv) · [Metrik CSV](tabel_metrik_evaluasi.csv) · [Bobot fitur CSV](feature_importance.csv)

![1_target_vs_prediksi](grafik/1_target_vs_prediksi.png)

![2_residual_dan_kelembapan](grafik/2_residual_dan_kelembapan.png)

![3_feature_importance](grafik/3_feature_importance.png)

![4_perbandingan_metrik](grafik/4_perbandingan_metrik.png)
