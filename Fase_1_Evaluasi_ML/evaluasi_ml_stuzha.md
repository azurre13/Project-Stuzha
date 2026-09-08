# Fase 1 — eksperimen ML dan ekspor model

Folder ini menyimpan hasil eksperimen awal, bukan validasi kalibrasi sensor fisik Stuzha. Status diperbarui pada 8 September 2026: model dan artefak tersedia; validitas skala, evaluasi, dan penerapan pada perangkat belum selesai.

## Artefak

- [Laporan metrik dengan batas interpretasi](laporan_evaluasi_metrik.md).
- [CSV metrik lama](tabel_metrik_evaluasi.csv).
- [Skrip evaluasi](run_fase1_evaluation.py).
- Grafik di `grafik/`: scatter PM/CO, residual terhadap RH, dan feature importance.
- Header model hasil ekspor di `../Program/Kode/include/`.

Label “ground truth”, “calibrated”, sensor MQ-7 pada benchmark UCI, dan satuan pada grafik/CSV lama belum diperbarui. MQ-7 memang terpasang untuk CO dan MQ-135 untuk proksi VOC/gas campuran menurut konfirmasi pemilik, tetapi data UCI berasal dari sensor berbeda. Gunakan artefak tersebut sebagai arsip eksperimen; jangan salin langsung ke naskah sebagai bukti akurasi perangkat. Tidak ada model kalibrasi VOC untuk MQ-135 dalam folder ini.

## Apa yang sebenarnya dievaluasi

### PM

Skrip membentuk target dari kolom PM2.5 Mendeley ×1.000, kemudian membuat input sintetis:

```text
factor = 1 + 0.65 × (RH/100)^2
noise = (T - 25) × 0.45 + noise acak
pm_raw = clip(target × factor + noise, 0, 600)
```

Random Forest belajar memetakan input buatan tersebut ke target. R² tinggi menunjukkan hasil pada konstruksi data ini; belum menunjukkan koreksi kelembapan atau akurasi GP2Y fisik. Dasar koefisien simulasi dan kesesuaian fisiknya belum divalidasi. Metadata Mendeley menyebut µg/m³, sehingga perkalian 1.000 harus ditelusuri.

### CO

Skrip memetakan PT08.S1(CO) UCI ke 800–3.600, memakai suhu/RH, lalu memprediksi CO(GT). Hasil berlaku untuk benchmark ini. Sensor UCI belum dibuktikan setara dengan sensor gas Stuzha. CO(GT) bersatuan mg/m³; label ppm di artefak lama perlu dikoreksi.

### Masalah evaluasi

- Train/test dibagi acak 80:20, random_state 42. Evaluasi generalisasi waktu perlu split berdasarkan waktu/sesi.
- Pemetaan rentang CO memakai seluruh data; baseline linear juga di-fit sebelum split. Fit preprocessing dan baseline hanya pada training.
- R² bukan persentase akurasi. Penurunan RMSE bukan kenaikan akurasi dengan persentase yang sama.
- Feature importance tidak membuktikan koreksi fisik atau hubungan sebab-akibat.
- Bandingkan model/fitur pada test set yang sama. Laporkan bias, MAE, RMSE, R² dan ketidakpastian bila rancangan datanya mendukung.
- Jangan memakai output model sebagai target untuk mengklaim kalibrasi ulang perangkat.

## Reproduksi dan efek samping

Perintah historis:

```sh
python Fase_1_Evaluasi_ML/run_fase1_evaluation.py
```

Skrip menimpa grafik, CSV metrik, laporan Markdown, dan header model. Teks generator masih memuat klaim lama dan dapat menimpa koreksi dokumentasi ini. Jangan menjalankan ulang untuk eksperimen berikutnya sebelum generator/evaluasi diperbaiki dan artefak diberi versi. Skrip `ml_training/train_models.py` juga menimpa header.

Tidak ada training ulang atau perubahan model pada pembaruan dokumentasi ini. Lihat [roadmap](../MD/roadmap_dan_langkah_selanjutnya.md).
