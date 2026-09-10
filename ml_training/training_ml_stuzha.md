# Training dan benchmark ML Stuzha

Diperbarui 9 September 2026. [pipeline.py](pipeline.py) adalah satu implementasi resmi untuk eksperimen data publik. [train_models.py](train_models.py) dan [entry point evaluasi](../Fase_1_Evaluasi_ML/run_fase1_evaluation.py) memanggil implementasi yang sama. Menjalankannya tidak mengganti header firmware atau laporan arsip.

## Reproduksi

Python 3.10+ dengan [requirements.txt](requirements.txt); g++ diperlukan untuk pemeriksaan ekspor. Versi runtime yang benar-benar dipakai disimpan pada report.json setiap run.

```sh
python ml_training/train_models.py --experiment uci-co
python ml_training/train_models.py --experiment pm-simulation
```

Default kini membuat folder unik di Fase_1_Evaluasi_ML/hasil/. --output harus direktori baru; penimpaan ditolak. Folder firmware bukan lokasi keluaran benchmark. Setiap run selesai memiliki report.json, metrics.csv, tabel_metrik_evaluasi.csv, test_predictions.csv, feature_importance.csv, laporan_evaluasi_metrik.md, empat PNG 300 DPI di grafik/, dan benchmark_model.h. Tidak adanya report.json berarti run belum selesai. File pemeriksa C++/exe merupakan artefak validasi host, bukan firmware ESP32. Hasil terdahulu di ml_training/runs/ tetap disimpan.

Untuk menjalankan kedua model sekaligus dan membuat laporan lengkap seperti alur Fase 1 awal:

```sh
python Fase_1_Evaluasi_ML/run_fase1_evaluation.py
```

Untuk mereproduksi training awal beserta CSV dan PNG, gunakan perintah yang sama dengan --experiment legacy-recovery. Prosedur ini memakai split acak historis; hasilnya dipisahkan dari benchmark split waktu. Semua hasil berada di Fase_1_Evaluasi_ML/hasil/ dan tidak menimpa grafik/CSV arsip.

## Metode dan batas

### Klarifikasi sumber GP2Y dan pilihan perbaikan — 10 September 2026

Dataset PM **merupakan pengukuran nyata peneliti, bukan dataset buatan**. [Sonawani & Patil, Mendeley v1 (2022)](https://data.mendeley.com/datasets/2r232jpfb2/1) menyebut 173.468 rekaman November 2020–Juli 2022, sensor GP2Y1010AU0F, suhu/RH BME280, serta satuan PM2.5 ug/m3. Istilah simulasi di proyek ini merujuk pada gangguan input yang ditambahkan oleh skrip kita, bukan pada asal kolom PM peneliti. CSV lokal yang diperiksa tidak menyediakan pasangan kolom ADC GP2Y dan PM instrumen pembanding. Dataset tetap berguna dan tidak dibuang.

Perbaikan PM yang memiliki dasar sekarang: gunakan satuan metadata tanpa pengalian 1000 yang tidak didukung; pisahkan evaluasi penghilangan gangguan buatan dari klaim kalibrasi fisik; cocokkan definisi input training dengan konversi sensor saat deployment. Benchmark baru sudah mempertahankan angka sumber, tetapi itu belum menyelesaikan pasangan input fisik/target referensi. Jangan sekadar membagi output model lama dengan 1000 atau menyalin header benchmark ke firmware: keduanya tidak otomatis memperbaiki kontrak input. DHT22 tetap menjadi sumber suhu/RH pada perangkat.

Untuk MQ-7, ditemukan sumber yang lebih relevan daripada pemetaan PT08 UCI: [Rathnayake et al. (2024), Machine Learning-based Calibration Approach for Low-cost Air Pollution Sensors MQ-7 and MQ-131](https://neptjournal.com/upload-images/%2834%29D-1457.pdf), DOI 10.46488/NEPT.2024.v23i01.034. Metodenya menggunakan pembacaan MQ-7 bersamaan dengan instrumen NBRO sekitar tiga bulan, kemudian regresi/jaringan saraf dengan pembacaan sensor dan suhu. Pada penelusuran ini belum ditemukan tautan unduhan CSV pasangan tersebut. Paper adalah rujukan metode, belum dataset siap training atau koefisien pengganti Stuzha.

Pilihan tanpa membeli alat: (1) memperoleh data pasangan sensor/referensi dari penelitian publik dengan rangkaian, satuan, dan pemanasan yang terdokumentasi, lalu melatih kandidat terpisah dan memeriksa kecocokan input; atau (2) membangun estimator berbasis kurva datasheet sebagai pembanding nominal, dengan parameter rangkaian yang benar, tanpa mengarang R0 atau menganggap udara kamar bernilai nol. Pilihan kedua tidak memberi label kebenaran baru kepada ML. Kalibrasi transfer tetap perlu dibedakan dari akurasi yang sudah dibuktikan pada unit Stuzha. Tidak ada perubahan model aktif, firmware, atau upload dalam penelusuran ini.

Paper penulis dataset [Sonawani & Patil, DOI 10.1108/IJPCC-07-2022-0271](https://doi.org/10.1108/IJPCC-07-2022-0271) juga ditemukan. Abstrak menyebut kalibrasi ML dan transfer learning untuk prediksi jam berikutnya; metode lengkap di balik akses berbayar belum diperiksa. Jangan mengutip peningkatan prediksi paper itu sebagai persentase kalibrasi GP2Y Stuzha.

**UCI:** urutkan timestamp, tangani -200 sebagai missing, split kronologis sekitar 80/20 pada batas timestamp. Target CO(GT) mg/m3. Fitur PT08.S1 asli, T dan RH. Tidak dipetakan ke skala ADC MQ7. Empat model dibandingkan pada holdout yang sama: linear/RF masing-masing satu fitur dan tiga fitur. Semua fitting memakai training; parameter RF tetap 30 pohon/depth 8/seed 42. Tidak mencari ulang split untuk memenangkan RF.

**PM simulation:** angka kolom PM2.5 asli dipertahankan tanpa x1000. Metadata menyebut ug/m3 sementara skrip lama menganggap mg/m3; unit fisik belum terselesaikan. Gangguan buatan: y*(1+0.65*(RH/100)^2)+(T-25)*0.00045+noise normal sd 0.0025, dibatasi bawah nol, semuanya dalam skala angka dataset. Koefisien ini asumsi eksperimen, bukan hasil fitting sensor fisik. Split waktu dan model pembanding sama prinsipnya dengan UCI.

Ekspor menggunakan input float32 dan threshold/akumulasi double untuk konsistensi benchmark sklearn di host. Pemeriksa membandingkan holdout serta probe sekitar threshold. Hasil tersebut tidak membuktikan kesesuaian header historis atau latensi ESP32; pada saat benchmark awal, artefak sklearn asal header belum teridentifikasi. Audit reproduksi lanjutan di bawah memperbarui status PM, sedangkan header CO lama masih berbeda dari hasil reproduksi.

Report menyimpan hash dataset, identitas metode, split/timestamp, ukuran training/test, metrik, versi library dan hasil pemeriksaan ekspor. Run terbaru juga memuat hash pipeline. Lihat [evaluasi](../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md).

## Model firmware

Header model_pm.h/model_co.h historis dipertahankan byte-identik sebagai estimator eksperimental utama v4. Kedua keluaran digrafikkan dan sub-indeks dari keluaran nominalnya menentukan kipas melalui IspuControl. Keputusan ini memulihkan fungsi TinyML, bukan bukti bahwa model sudah terkalibrasi atau optimal. Baca [keputusan deployment v4](../MD/metode_ispu_v4.md). Perubahan training berikutnya tidak perlu upload ulang perangkat pengumpulan data karena output run tidak menyentuh header aktif. Jangan mengklaim training ini sebagai kalibrasi sensor Stuzha.

[explore_datasets.py](explore_datasets.py) hanya mencetak inventaris dan batas asal data, tanpa klaim bahwa sensor setara atau dataset sudah memvalidasi perangkat.

Menyalin benchmark_model.h UCI ke model_co.h tidak dibenarkan: PT08.S1 asli berbeda kontrak masukan dengan MQ7 ADC. Simulasi PM baru juga memakai skala berbeda. Deployment model beku tidak sama dengan transfer learning yang mengevaluasi adaptasi domain target. Kompensasi drift merupakan tujuan penelitian, belum hasil yang terbukti.

V4 tidak melakukan retraining atau mengklaim peningkatan akurasi baru. Script training legacy di Git diperiksa: target PM dikali1000 dari angka sumber, target CO tetap CO(GT) mg/m3 walau label lama salah menyebut ppm. Ini menjelaskan asal angka, bukan menyelesaikan kebenaran skala fisik PM atau transfer MQ7. Tidak menambahkan A/B/R0 atau zero-offset udara kamar tanpa dasar ukur.

## Audit reproduksi training asli — pembaruan 9 September 2026

[audit_legacy_training.py](audit_legacy_training.py) khusus mereproduksi prosedur historis dari Git, bukan pipeline kalibrasi/benchmark produksi baru. Jalankan python ml_training/audit_legacy_training.py untuk membuat direktori run baru tanpa mengubah header aktif. Dataset/prosedur legacy sengaja dipertahankan agar asal artefak bisa diperiksa; bias metode lama tidak disembunyikan.

[Hasil audit](../Fase_1_Evaluasi_ML/reproduksi_legacy_20260909.json): training PM berhasil menghasilkan source header yang sama setelah normalisasi line ending. R2 pada holdout sintetis0.9997118, bukan akurasi fisik. Model Python hasil fit kini tersimpan. Training CO juga berhasil (R2 holdout sumber0.8086635), tetapi beberapa cabang header aktif berbeda dari rekonstruksi. Selisih maksimum pada1469probe adalah0.201724 dalam satuan angka CO model; ini belum mengidentifikasi penyebab perbedaan historisnya.

Kedua model rekonstruksi disimpan sebagai joblib. Kandidat ekspor baru menggunakan threshold/presisi konsisten dan lulus pemeriksaan Python/C++: PM2402probe (maks1.14e-13), CO2417probe (maks1.78e-15). Kandidat berada di run_directory pada laporan; belum dipromosikan ke firmware. Kelulusan ini menyelesaikan konsistensi pasangan model/ekspor kandidat, bukan konflik unit PM atau transfer PT08-ke-MQ7. Firmware v4 dan header aktif tidak berubah oleh audit.
