# Fase 1: Evaluasi Machine Learning & Ekspor TinyML

Folder ini berisi seluruh artefak, skrip, data metrik, dan grafik visualisasi ilmiah untuk **Fase 1 (Data Science & ML Calibration)** pada **Project Stuzha**.

---

## 📂 Isi Folder

```text
Fase_1_Evaluasi_ML/
├── grafik/                                 # Berkas gambar visualisasi ilmiah (300 DPI)
│   ├── 1_evaluasi_kalibrasi_pm25.png       # Scatter plot PM2.5 (Sebelum vs Sesudah ML)
│   ├── 2_efek_koreksi_kelembapan_pm25.png  # Penekanan hygroscopic effect (RH%)
│   ├── 3_evaluasi_kalibrasi_co.png         # Scatter plot CO (Linear vs Random Forest)
│   └── 4_feature_importance.png           # Kontribusi fitur (Sensor, Suhu, RH)
├── laporan_evaluasi_metrik.md              # Laporan lengkap metrik & pembahasan untuk paper
├── tabel_metrik_evaluasi.csv               # Tabel metrik dalam format CSV
├── run_fase1_evaluation.py                 # Skrip Python komprehensif eksekusi Fase 1
└── README.md                               # Dokumentasi modul ini
```

---

## 📊 Ringkasan Hasil Evaluasi

| Parameter | Sensor | $R^2$ Sebelum | $R^2$ Sesudah ML | Penurunan RMSE | Penurunan MAE |
|---|---|:---:|:---:|:---:|:---:|
| **PM2.5 (µg/m³)** | Sharp GP2Y1010AU0F + DHT22 | 0.9833 | **0.9997** | **86.9%** | **92.4%** |
| **CO (ppm)** | MQ-7 (MOS) + DHT22 | 0.7788 | **0.8087** | **7.0%** | **9.8%** |

---

## 🔬 Kesesuaian dengan Referensi Jurnal
- **Jurnal 3 & 12**: Menggunakan formula dasar datasheet sensor sebagai baseline linear awal.
- **Jurnal 4 & 6**: Memodelkan dan mengoreksi pembiasan uap air (*hygroscopic growth*) via DHT22.
- **Jurnal 5 & 15**: Pembuktian bahwa *ensemble Random Forest* mengungguli regresi linear sederhana.
- **Jurnal 8, 10, & 20**: Menghasilkan C Header mandiri (`model_pm.h` & `model_co.h`) siap inferensi di ESP32-S3.

---

## 🚀 Cara Menjalankan Ulang
```bash
python Fase_1_Evaluasi_ML/run_fase1_evaluation.py
```
Skrip ini akan melatih model, menghitung metrik, memperbarui gambar di `grafik/`, dan langsung memperbarui file header di `Program/Kode/include/`.
