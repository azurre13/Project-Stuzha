# Arsip metrik ML sebelum revisi

Status diperbarui 9 September 2026. Angka di bawah dipertahankan dari hasil lama; bukan hasil training terbaru, bukan bukti akurasi fisik dan bukan metrik model benchmark kronologis baru.

| Eksperimen lama | R² baseline | R² RF | RMSE baseline ke RF | MAE baseline ke RF |
|---|---:|---:|---|---|
| PM input sintetis | 0.9833 | 0.9997 | 15.05 ke 1.98 | 7.68 ke 0.58 |
| CO UCI dengan pemetaan ADC | 0.7788 | 0.8087 | 0.66 ke 0.61 | 0.48 ke 0.44 |

Skala PM memakai perkalian x1000 yang asal satuannya belum diselesaikan. CO(GT) bersatuan mg/m3, tetapi label lama menggunakan ppm. Split acak dan baseline yang di-fit sebelum split membatasi evaluasi. Penurunan RMSE 86.9%/7.0% pada eksperimen lama bukan peningkatan akurasi sensor dengan persentase tersebut. R² 0.9997 bukan akurasi sensor 99.97%.

Input PM disintesis dari target, suhu/RH dan noise buatan. Sensor UCI yang rentangnya diubah belum terbukti ekuivalen dengan MQ7. MQ135 hanya proksi gas campuran; tidak memiliki model VOC terkalibrasi. Feature importance tidak membuktikan sebab-akibat.

Grafik/CSV historis tetap utuh untuk penelusuran, tetapi labelnya tidak dijadikan data baru. Generator lama sudah diganti sehingga tidak akan menimpa laporan ini. Hasil baru ada pada [evaluasi ML](../../evaluasi_ml_stuzha.md) dan mempunyai identitas split/pipeline terpisah.
