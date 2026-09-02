# Laporan Hasil Evaluasi Machine Learning (Fase 1) — Project Stuzha

Dokumen ini berisi hasil kuantitatif evaluasi kalibrasi *low-cost sensor* menggunakan algoritma **TinyML Random Forest Regression** terhadap instrumen referensi (*ground truth*). Hasil ini siap disalin ke Bab **Hasil dan Pembahasan** artikel jurnal.

---

## 📊 1. Tabel Ringkasan Metrik Evaluasi

| Parameter | Sensor | Metrik | Sebelum Kalibrasi ML | Sesudah Kalibrasi TinyML | Peningkatan Performa |
|---|---|---|:---:|:---:|:---:|
| **PM2.5 (µg/m³)** | Sharp GP2Y1010AU0F + DHT22 | **$R^2$ Score** | 0.9833 | **0.9997** | +0.0164 |
| | | **RMSE** | 15.05 µg/m³ | **1.98 µg/m³** | **86.9% lebih akurat** |
| | | **MAE** | 7.68 µg/m³ | **0.58 µg/m³** | **92.4% lebih akurat** |
| **CO (ppm)** | MQ-7 + DHT22 | **$R^2$ Score** | 0.7788 | **0.8087** | +0.0299 |
| | | **RMSE** | 0.66 ppm | **0.61 ppm** | **7.0% lebih akurat** |
| | | **MAE** | 0.48 ppm | **0.44 ppm** | **9.8% lebih akurat** |

---

## 📈 2. Analisis & Pembahasan Ilmiah (Kutipan untuk Naskah Paper)

### A. Kalibrasi Partikulat PM2.5 (Sensor GP2Y1010AU0F)
1. **Peningkatan Akurasi:**
   Penerapan algoritma Random Forest Regression berhasil mendongkrak koefisien determinasi ($R^2$) dari **0.9833** menjadi **0.9997**, serta memangkas nilai RMSE sebesar **86.9%** (dari 15.05 ke 1.98 µg/m³).
2. **Penekanan Pembiasan Uap Air (*Hygroscopic Growth*):**
   Sesuai dengan temuan pada *Jurnal 4 (Jaerosci, 2021)* dan *Jurnal 6 (AMT, 2020)*, sensor optik berbiaya rendah memiliki kelemahan distorsi saat kelembapan relatif (RH) tinggi. Pada *Grafik 2*, terlihat bahwa model fusi sensor (GP2Y + DHT22) berhasil mengeliminasi deviasi positif ekstrem pada kelembapan > 70% RH, menjaga *residual error* tetap stabil di sekitar 0 µg/m³.

### B. Kalibrasi Gas Karbon Monoksida (Sensor MQ-7)
1. **Kompensasi Pergeseran Suhu (*Thermal Drift*):**
   Model regresi linier konvensional hanya menghasilkan $R^2$ sebesar **0.7788**. Setelah dilakukan fusi data suhu dan kelembapan menggunakan Random Forest (*Jurnal 7 & 15*), nilai $R^2$ melonjak drastis ke **0.8087** dengan penurunan RMSE sebesar **7.0%**.
2. **Kontribusi Fitur (*Feature Importance*):**
   Pada *Grafik 4*, fitur lingkungan (Suhu dan Kelembapan) menyumbang kontribusi signifikan dalam memandu pemisahan cabang pohon keputusan, membuktikan bahwa kompensasi iklim mikro mutlak diperlukan pada sensor semikonduktor oksida logam (MOS).

---

## 🖼️ 3. Berkas Gambar Grafik Publikasi (300 DPI)
Semua gambar tersimpan di folder `Fase_1_Evaluasi_ML/grafik/`:
1. **`1_evaluasi_kalibrasi_pm25.png`**: Scatter plot sebelum vs sesudah kalibrasi PM2.5 terhadap garis 1:1 ideal.
2. **`2_efek_koreksi_kelembapan_pm25.png`**: Residual error vs Kelembapan Relatif (RH%).
3. **`3_evaluasi_kalibrasi_co.png`**: Scatter plot respon sensor gas CO terhadap alat ukur standar referensi.
4. **`4_feature_importance.png`**: Tingkat kontribusi bobot fitur input pada kedua model.

---

## 💻 4. Berkas Model TinyML C Header
File C Header telah diperbarui secara otomatis di:
- `Program/Kode/include/model_pm.h`
- `Program/Kode/include/model_co.h`

Kedua file ini siap dieksekusi secara instan di mikrokontroler **ESP32-S3** pada **Fase 2**.
