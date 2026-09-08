# Catatan hasil eksperimen ML awal

Diperbarui 8 September 2026. Angka berikut dipertahankan dari artefak evaluasi lama, bukan hasil evaluasi ulang dan bukan bukti kalibrasi fisik Stuzha.

## Metrik arsip

| Eksperimen | R² baseline | R² RF | RMSE baseline → RF | MAE baseline → RF |
|---|---:|---:|---|---|
| PM dengan input sintetis | 0,9833 | 0,9997 | 15,05 → 1,98 | 7,68 → 0,58 |
| CO pada UCI | 0,7788 | 0,8087 | 0,66 → 0,61 | 0,48 → 0,44 |

Nilai error mengikuti skala target skrip lama. Untuk PM, validitas perkalian target ×1.000 belum diselesaikan; jangan menetapkan interpretasi konsentrasi fisik dari angka tersebut. Target CO UCI memakai mg/m³, sedangkan artefak lama memberi label ppm secara tidak tepat.

Penurunan RMSE yang dicatat skrip adalah 86,9% untuk PM dan 7,0% untuk CO. Ini merupakan perbandingan error dalam eksperimen tersebut, bukan “lebih akurat” pada perangkat. R² 0,9997 bukan akurasi 99,97%.

## Batas interpretasi

1. Input PM dibuat dari target, faktor RH, dan noise buatan; belum ada pasangan raw GP2Y dan pembacaan instrumen referensi pada Stuzha.
2. Kolom PM Mendeley berasal dari sensor berbiaya rendah, bukan otomatis ground truth independen.
3. Respons sensor UCI yang diubah rentangnya belum dibuktikan setara dengan ADC MQ-7 Stuzha. Identitas MQ-7 untuk CO dan MQ-135 untuk proksi VOC/gas campuran telah dikonfirmasi; tidak ada model kalibrasi VOC dalam artefak ini.
4. Split acak dan fitting baseline CO sebelum split perlu diperbaiki sebelum evaluasi lanjutan.
5. Grafik residual RH belum membuktikan eliminasi bias kelembapan pada alat fisik; feature importance bukan bukti kausal.
6. Ketersediaan header C belum membuktikan latensi, akurasi sensor, atau kesesuaian Python/C; masing-masing memerlukan pengujian tersendiri.

Lihat [penjelasan metode](evaluasi_ml_stuzha.md) dan [asal dataset](../Program/data/dataset_stuzha.md). Belum tersedia instrumen pembanding. Untuk naskah monitoring, hasil ini hanya dapat digunakan sebagai eksperimen pendukung yang diberi batasan, bukan klaim kontribusi kalibrasi tervalidasi.

## Status artefak

Grafik dan CSV metrik belum diubah. Judul, label sensor, dan satuan di dalamnya masih mencerminkan interpretasi lama. Generator dalam run_fase1_evaluation.py juga belum diperbaiki; menjalankannya akan menimpa laporan ini dengan teks lama. Simpan versi artefak dan perbaiki generator sebelum menghasilkan laporan baru.
