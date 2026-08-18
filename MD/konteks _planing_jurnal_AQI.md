# Master Note: Sistem Monitoring Kualitas Udara Indoor (Versi Upgrade)

## 1. Konteks & Ruang Lingkup

Alat fisik sudah ada dan berfungsi (hasil tugas besar embedded systems), dengan fitur yang **sudah ada dan TIDAK diubah**:
- Fan speed dinamis (adaptive filtration)
- Air purifier terintegrasi
- IoT monitoring (dapat dipantau real-time via HP)

**Yang diupgrade untuk jurnal (fokus utama dokumen ini):**
1. Sensor gas CO: MQ-2 → **MQ-7**
2. Tambah **algoritma ML (Random Forest)** untuk kalibrasi sensor
3. Perhitungan output **AQI final** dengan standar referensi yang proper (ISPU)

Target awal publikasi: Sinta 3-4 (realistis untuk paper pertama di topik ini), dengan Sinta 2 sebagai target paper lanjutan.

---

## 2. Hardware (Alat Sekarang)

| Komponen | Fungsi | Peran dalam Sistem |
|---|---|---|
| **ESP32-S3** | Microcontroller + Edge AI | Menjalankan inference model ML (bukan training). Dipilih S3 karena punya vector instruction extension untuk AI/DSP acceleration dan Bluetooth, tidak seperti S2. |
| **GP2Y1010AU0F** | Sensor debu (PM) | ⚠️ Pastikan part number ini benar (bukan "GP2Y1014AU0F"), cek datasheet fisik alat. Input ke model ML untuk kalibrasi PM. |
| **MQ-7** | Sensor CO | Upgrade dari MQ-2. Lebih presisi untuk CO dibanding MQ-2 yang broad-spectrum (LPG/propane/smoke). Input ke model ML untuk kalibrasi CO. |
| **MQ-135** | Sensor gas campuran (NH3, VOC, dll) | TIDAK dipaksa masuk sub-indeks AQI resmi (tidak ada breakpoint ISPU untuk gas campuran ini). Diposisikan sebagai "indoor VOC/air quality proxy" terpisah dengan threshold sendiri. |
| **DHT22** | Suhu & kelembapan | Dipakai sebagai variabel koreksi di model ML (bukan komponen AQI langsung) — karena pembacaan sensor gas/debu bergeser seiring perubahan suhu/kelembapan. |

**Catatan penting soal training vs inference (ESP32):**
- **Training model Random Forest dilakukan di laptop/PC** (Python, scikit-learn) — BUKAN di ESP32. Proses ini butuh dataset besar dan komputasi berat yang di luar kapasitas microcontroller.
- **ESP32-S3 hanya menjalankan inference** (pemakaian model yang sudah jadi) — ini ringan, karena Random Forest setelah dilatih cuma berupa kumpulan aturan if-else yang dikonversi ke kode C/C++ (pakai tools seperti `m2cgen`, `micromlgen`, atau library `emlearn`).
- Batasi jumlah trees (misal 50-100) dan depth (10-15) saat training supaya ukuran model hasil konversi tetap muat di flash/RAM ESP32-S3.

---

## 3. Alur Kerja Sistem — 3 Tahap Perhitungan

```
[Data mentah sensor: GP2Y1010, MQ-7, DHT22]
            ↓
┌─────────────────────────────────────────┐
│  TAHAP 1: Kalibrasi ML (Random Forest)   │
│  Input: raw ADC/voltage + suhu + RH      │
│  Output: konsentrasi murni terkalibrasi  │
│  (PM dalam µg/m³, CO dalam ppm)          │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  TAHAP 2: Piecewise Linear Interpolation │
│  Input: konsentrasi murni per polutan    │
│  Proses: breakpoint ISPU per parameter   │
│  Output: sub-indeks per polutan          │
│  (skala seragam, sesuai kategori ISPU)   │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│  TAHAP 3: Ambil Nilai MAKSIMUM           │
│  Input: semua sub-indeks (PM, CO)        │
│  Proses: MAX() — bukan rata-rata         │
│  Output: AQI final + kategori +          │
│  nama "Parameter Pencemar Kritis"        │
└─────────────────────────────────────────┘
            ↓
   [Output ke layar/IoT + trigger fan speed
    & air purifier sesuai polutan dominan]
```

### Penjelasan tiap tahap

**Tahap 1 — Kalibrasi ML (Sensor Fusion)**
Sensor murah punya kelemahan: pembacaannya bergeser saat suhu/kelembapan berubah. Data semua sensor (gas, debu, suhu, kelembapan) dimasukkan bersama ke satu model Random Forest yang sudah dilatih sebelumnya di laptop. Model ini mengoreksi bias tersebut sehingga keluarannya adalah nilai konsentrasi yang mendekati akurasi alat reference-grade, meski sensor yang dipakai murah.

**Tahap 2 — Sub-Indeks per Polutan**
Konsentrasi murni (misal CO dalam ppm, PM dalam µg/m³) belum bisa disebut "AQI" karena satuannya berbeda-beda antar polutan. Setiap polutan dihitung dengan rumus interpolasi linear terhadap breakpoint resmi ISPU, menghasilkan skor dalam skala yang seragam (Sub-Indeks).

**Tahap 3 — AQI Final**
Dari sub-indeks yang ada (misal sub-indeks PM dan sub-indeks CO), sistem TIDAK merata-ratakan. Sistem mengambil nilai **tertinggi** sebagai output AQI final, karena itu mewakili "Parameter Pencemar Kritis" — polutan yang paling berbahaya pada saat itu. Nilai ini yang dipakai untuk trigger fan speed dan air purifier (idealnya per-polutan dominan, bukan cuma satu angka gabungan, supaya sistem bisa membedakan respons: PM tinggi → prioritaskan filter mekanis/HEPA, CO/gas tinggi → prioritaskan filter karbon aktif).

---

## 4. Output Sistem

Output akhir yang ditampilkan (baik di layar alat maupun di aplikasi HP via IoT) terdiri dari:
1. **Angka indeks** (integer, misal "70")
2. **Kategori** sesuai rentang ISPU (Baik/Sedang/Tidak Sehat/Sangat Tidak Sehat/Berbahaya)
3. **Nama parameter pencemar kritis** (polutan mana yang jadi sumber nilai maksimum tadi — misal "PM2.5" atau "CO")

Contoh format resmi ISPU (dari lampiran Permen LHK 14/2020) yang bisa dijadikan acuan tampilan:
> Indeks Standar Pencemar Udara Maksimum: 70 — Parameter Pencemar Kritis: partikulat (PM2.5) — Kategori ISPU: Sedang

---

## 5. Standar Referensi yang Dipakai (Keputusan Final)

- **Breakpoint AQI utama: ISPU** (Peraturan Menteri LHK No. 14 Tahun 2020) — karena deployment di Indonesia, breakpoint CO & PM sudah tersedia resmi, dan relevan untuk konteks lokal/penguji.
- **WHO 2021 Air Quality Guidelines**: dipakai sebagai **pembanding di bagian discussion** (bukan breakpoint utama), karena WHO cuma punya ambang batas konsentrasi, tidak punya formula interpolasi.
- **US EPA (2018)**: dicitasi sebagai referensi **konsep dasar** piecewise linear interpolation dan logika ambil nilai maksimum (bukan breakpoint angkanya).

---

## 6. Referensi Lengkap per Tahap

### Tahap 1 — ML Calibration (Random Forest)
1. Zimmerman, N., Presto, A. A., Kumar, S. P. N., Gu, J., Hauryliuk, A., Robinson, E. S., Robinson, A. L., & Subramanian, R. (2018). "A machine learning calibration model using random forests to improve sensor performance for lower-cost air quality monitoring." *Atmospheric Measurement Techniques*, 11(1), 291–313. https://doi.org/10.5194/amt-11-291-2018
   - Catatan: paper ini pakai sensor elektrokimia, bukan MQ/optik — dicitasi sebagai landasan metodologi, bukan klaim akurasi langsung sama.
2. Wang, Y., Du, Y., Wang, J., & Li, T. (2019). "Calibration of a low-cost PM2.5 monitor using a random forest model." *Environment International*, 133, 105161.
3. Han, P., et al. (2021). "Calibrations of Low-Cost Air Pollution Monitoring Sensors for CO, NO2, O3, and SO2." *Sensors*, 21(1), 256. https://www.mdpi.com/1424-8220/21/1/256
4. (Untuk bagian limitations) Studi yang menyarankan kehati-hatian penggunaan RF di lapangan non-laboratorium: https://www.sciencedirect.com/science/article/pii/S0048969725010009

### Tahap 2 — Sub-Indeks (Piecewise Linear Interpolation)
1. Peraturan Menteri LHK No. P.14/MENLHK/SETJEN/KUM.1/7/2020 tentang ISPU (dokumen resmi, berisi rumus dan tabel breakpoint): https://jdih.menlhk.go.id/new2/uploads/files/P_14_2020_ISPU_menlhk_07302020074834.pdf
2. Artikel pendukung (penjelasan + tabel kategori): https://ditppu.menlhk.go.id/portal/read/indeks-standar-pencemar-udara-ispu-sebagai-informasi-mutu-udara-ambien-di-indonesia
3. US EPA (2018). "Technical Assistance Document for the Reporting of Daily Air Quality – the Air Quality Index (AQI)." — referensi konsep interpolasi.
4. World Health Organization (2021). *WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide*. Geneva: WHO. https://iris.who.int/handle/10665/345329

### Tahap 3 — AQI Final (Ambil Nilai Maksimum)
1. Peraturan Menteri LHK No. P.14/MENLHK/SETJEN/KUM.1/7/2020 — dokumen sama seperti Tahap 2, yang juga mewajibkan logika ambil nilai maksimum (Parameter Pencemar Kritis).
2. US EPA (2018) — referensi konsep "highest sub-index wins" yang dipakai universal di sistem AQI dunia.

### Output
#### Amerika:
EPA AQI (Amerika Serikat):

Rentang	Kategori
0–50	Good
51–100	Moderate
101–150	Unhealthy for Sensitive Groups
151–200	Unhealthy
201–300	Very Unhealthy
301–500	Hazardous

Referensi: US EPA (2018). "Technical Assistance Document for the Reporting of Daily Air Quality – the Air Quality Index (AQI)."

#### indo:
Kategori ISPU (Permen LHK No. 14/2020):

Rentang	Kategori
0–50	Baik
51–100	Sedang
101–200	Tidak Sehat
201–300	Sangat Tidak Sehat
diatas 300	= Berbahaya

Referensi: Peraturan Menteri LHK No. P.14/MENLHK/SETJEN/KUM.1/7/2020 tentang ISPU.

### Referensi Pembanding / State-of-the-Art (untuk bagian related work di jurnal)
1. Prasetyo, D.P., Lamada, I., & Adzillah, W.N. (2021). "Implementasi Monitoring Kualitas Udara menggunakan Sensor MQ-7 dan MQ-131 berbasis Internet of Things." *Electrician: Jurnal Rekayasa dan Teknologi Elektro*, 15(3), 239-245. https://doi.org/10.23960/elc.v15n3.2184
   - Riset sejenis (MQ-7 + ISPU) tapi masih rule-based, belum ML — bisa jadi pembanding untuk menonjolkan kontribusi upgrade ke ML.
2. Studi dengan kombinasi sensor mirip (GP2Y1010AU0F + MQ-135 + DHT) di Diskominfotik Lampung, masih pakai kalibrasi relatif sederhana (bukan ML): https://jurnal.ubl.ac.id/index.php/explore/article/view/4891

---

## 7. Kebutuhan Data (khusus Tahap 1 — ML Training)

| Aspek | Rekomendasi |
|---|---|
| Jumlah data minimal | 500–1000 baris (raw sensor value + reference/ground truth) |
| Jumlah data ideal | 2000–5000+ baris |
| Durasi pengumpulan | Beberapa minggu (bukan hanya beberapa jam), untuk menangkap variasi kondisi (siang/malam, aktivitas indoor berbeda — memasak, merokok, AC nyala/mati, dll) |
| Split data | 70:30 atau 80:20 (train:test); tambah validation set jadi 70:15:15 kalau data cukup banyak |
| Sumber ground truth | Idealnya alat kalibrasi standar/reference-grade (pinjam lab kampus/instansi lingkungan). Kalau tidak memungkinkan, jelaskan metodologi pengumpulan data secara transparan di paper (kondisi terkontrol, durasi, variasi yang direpresentasikan) |

Tahap 2 dan Tahap 3 **tidak** butuh dataset training — cuma butuh tabel breakpoint resmi ISPU (hardcoded sebagai lookup table) dan logika perbandingan `MAX()`.

---

## 8. Justifikasi Teknis Tambahan (antisipasi pertanyaan penguji/reviewer)

1. **Kenapa MQ-7, bukan MQ-2?** MQ-2 broad-spectrum (LPG, propane, smoke, CO ikut kedetect tapi tidak presisi). MQ-7 didesain spesifik untuk CO dengan respons lebih akurat di rentang CO ambient/indoor — parameter yang diregulasi resmi di ISPU.
2. **Kenapa MQ-135 tetap dipakai tapi tidak masuk AQI?** Karena MQ-135 mendeteksi campuran gas (NH3, VOC, benzene, dll), tidak ada breakpoint resmi ISPU/EPA untuknya. Diposisikan sebagai indikator VOC indoor tambahan, bukan komponen sub-indeks resmi — supaya tidak overclaim validitas ilmiah.
3. **Kenapa Random Forest, bukan neural network?** RF ringan untuk inference di edge device (ESP32), interpretable (bisa cek feature importance), dan robust terhadap noise sensor murah yang non-linear.
4. **Kenapa breakpoint ISPU, bukan EPA?** Breakpoint EPA didesain untuk konteks AS (angka konsentrasi beda dari ISPU), sehingga hasil akhir device tidak akan apple-to-apple dengan pelaporan resmi pemerintah/BMKG Indonesia kalau pakai EPA sebagai breakpoint utama.
5. **Kontribusi utama paper (draf kalimat):** "Peningkatan sistem monitoring kualitas udara indoor dari klasifikasi rule-based (if-else) menjadi sistem AQI terkalibrasi ML (Random Forest) yang comply dengan standar ISPU, diimplementasikan pada purwarupa yang telah memiliki fitur fan speed dinamis, air purifier, dan monitoring IoT."

---

## 9. To-Do Sebelum Submit (Checklist)

- [ ] Cek ulang part number sensor debu (GP2Y1010AU0F, bukan GP2Y1014AU0F)
- [ ] Kumpulkan data validasi eksperimen (bandingkan hasil kalibrasi ML dengan reference instrument, minimal sebagian sampel)
- [ ] Tentukan dan dokumentasikan durasi pengumpulan data serta skema split train/test
- [ ] Tulis justifikasi jelas soal MQ-7 vs MQ-135 (presisi vs broad-spectrum) di bagian metodologi
- [ ] Pastikan satu kalimat kontribusi utama tercantum jelas di abstrak/pendahuluan
- [ ] Verifikasi breakpoint yang di-hardcode di sistem sesuai persis lampiran Permen LHK 14/2020 (bukan campur dengan angka EPA)


---


## 10. Spesifikasi Teknis Algoritma & Mathematical Rules (Context for AI)

### A. Formula Matematis ISPU (Permen LHK No. 14 Tahun 2020)
Perhitungan sub-indeks wajib menggunakan Piecewise Linear Interpolation:
$$I = \frac{I_a - I_b}{X_a - X_b} (X_x - X_b) + I_b$$

### B. Arsitektur Dual-Path Sistem:
1. Primary Path (Regulated ISPU):
   - Model 1: RF_PM = f(GP2Y_raw, DHT_Temp, DHT_RH) -> Output: µg/m³
   - Model 2: RF_CO = f(MQ7_raw, DHT_Temp, DHT_RH) -> Output: ppm
   - Index Calculation: SubIndex_PM & SubIndex_CO dihitung dengan rumus ISPU.
   - Final ISPU = MAX(SubIndex_PM, SubIndex_CO). Parameter kritis diambil dari nilai tertinggi.
2. Secondary Path (VOC/Gas Guard):
   - Sensor MQ-135 berjalan independen. Jika kadar gas campuran terdeteksi abnormal, sistem memicu booster filtrasi tanpa mengubah kalkulasi resmi ISPU.

### C. Target Deployment TinyML:
- Library Konversi: `emlearn` / `micromlgen` (Scikit-Learn -> Pure C array `model.h`).
- Target Hardware: ESP32-S3 (Offline Edge Inference, zero-latency cloud dependency).
- Actuator: Kipas Filtrasi DC dikontrol via PWM (10% - 100%) mengikuti tingkatan kategori ISPU.

---

## 11. Direktori & Pemetaan Referensi Literatur (Context for AI & Research Gap)

Bagian ini merangkum seluruh referensi primer yang digunakan sebagai landasan metodologis, pembenaran perangkat keras, kalibrasi Machine Learning (TinyML), dan regulasi baku sistem.

---

### A. Regulasi Baku & Standar Perhitungan AQI (Tahap 2 & 3)

1. **Permen LHK No. P.14/MENLHK/SETJEN/KUM.1/7/2020**

   - **Judul:** *Indeks Standar Pencemar Udara (ISPU)*
   - **Penerbit:** Kementerian Lingkungan Hidup dan Kehutanan Republik Indonesia (2020)
   - **Peran dalam Sistem:** - Sumber hukum mutlak untuk rumus *Piecewise Linear Interpolation* (Tahap 2).
     - Acuan tabel *breakpoint* baku konsentrasi polutan Indonesia (PM2.5 dalam µg/m³ dan CO dalam ppm/µg/m³).
     - Landasan aturan pengambilan nilai *MAX()* untuk menetapkan *Parameter Pencemar Kritis* (Tahap 3).
     - Landasan ilmiah pemisahan sensor MQ-135 dari formula ISPU (karena senyawa campuran/VOC tidak termasuk dalam 7 parameter baku ambien LHK).
2. **US EPA (2018)**

   - **Judul:** *Technical Assistance Document for the Reporting of Daily Air Quality – the Air Quality Index (AQI)*
   - **Penerbit:** United States Environmental Protection Agency
   - **Peran dalam Sistem:** Rujukan metodologis internasional untuk konsep interpolasi linier bertingkat dan prinsip "sub-indeks tertinggi menentukan kategori kualitas udara".
3. **WHO (2021)**

   - **Judul:** *WHO Global Air Quality Guidelines*
   - **Penerbit:** World Health Organization
   - **Peran dalam Sistem:** Parameter pembanding ambang batas kesehatan global pada bab Pembahasan (*Discussion*).

---

### B. Baseline Riset & Asal Muasal Proyek

4. **Hermansyah, D., Athallah, M. A., & Al Qarnie, M. (2022/2025)**
   - **Judul:** *Rancang Bangun Purwarupa Pemantauan dan Filtrasi Udara Berbiaya Rendah Berbasis Kendali Kipas Adaptif*
   - **Publikasi:** *JMECS (Journal of Measurements, Electronics, Communications, and Systems)*
   - **Peran dalam Sistem:** **Paper Baseline**. Menyediakan purwarupa awal (ESP32, MQ-2, MQ-135, GP2Y1014AU0F, DHT22) dengan kendali kipas statis *if-else*.
   - **Research Gap yang Diisi:** Mengupgrade sensor CO (MQ-2 → MQ-7), mengganti logika statis menjadi *Edge AI Random Forest Regression*, dan menyelaraskan output ke standar ISPU resmi.

---

### C. Kalibrasi Machine Learning — Sensor Partikulat / Debu (GP2Y & DHT22)

5. **Adong, P., Bainomugisha, E., Okure, D., & Sserunjogi, R. (2022)**

   - **Judul:** *Applying machine learning for large scale field calibration of low‐cost PM2.5 and PM10 air pollution sensors*
   - **Publikasi:** *Applied AI Letters (Wiley)*, Vol. 3, No. 3, e76.
   - **Peran dalam Sistem:** - Membuktikan bahwa **Random Forest (RF)** adalah algoritma kalibrasi terbaik untuk sensor partikulat optik berbiaya rendah (*light-scattering*) dengan fusi fitur Suhu dan RH dari DHT22.
     - Memangkas error sensor optik secara drastis (RMSE turun dari 18.6 ke 7.2 µg/m³, $R^2 = 0.92$).
     - Menjustifikasi bahwa penyakit sensor debu optik (seperti Sharp GP2Y) berupa pembiasan uap air (*hygroscopic growth*) wajib diselesaikan via Random Forest.
6. **Wang, Y., Du, Y., Wang, J., & Li, T. (2019)**

   - **Judul:** *Calibration of a low-cost PM2.5 monitor using a random forest model*
   - **Publikasi:** *Environment International*, Vol. 133, 105161.
   - **Peran dalam Sistem:** Rujukan pendukung efektivitas Random Forest untuk kompensasi fluktuasi cuaca pada sensor PM.

---

### D. Kalibrasi Machine Learning — Sensor Gas (MQ-7, MQ-135, MOS & DHT22)

7. **Han, P., Mei, H., Liu, D., Zeng, N., Tang, X., Wang, Y., & Pan, Y. (2021)**

   - **Judul:** *Calibrations of Low-Cost Air Pollution Monitoring Sensors for CO, NO2, O3, and SO2*
   - **Publikasi:** *Sensors (MDPI)*, Vol. 21, No. 1, Art. 256.
   - **Peran dalam Sistem:** - Memvalidasi penggunaan **Random Forest Regressor (RFR)** untuk mengkalibrasi sensor Karbon Monoksida (CO) berbiaya rendah terhadap instrumen referensi stasiun nasional.
     - Membuktikan bahwa Random Forest sukses mengoreksi *baseline drift* non-linear akibat suhu dan kelembaban lingkungan.
8. **Maharani, A. A. P., Sakti, R. H., Haq, M. F. I., Ajis, M., & Silaban, A. M. (2024)**

   - **Judul:** *Air Quality Classification System using Random Forest Algorithm using MQ-7 and MQ-135 Sensors with IoT-based*
   - **Publikasi:** *Journal of Mechatronics and Artificial Intelligence (JMAI UPI)*, Vol. 1, No. 2, pp. 65–74.
   - **Peran dalam Sistem:** - Memvalidasi implementasi spesifik Random Forest pada kombinasi perangkat **MQ-7 dan MQ-135** berbasis IoT.
     - **Research Gap yang Diisi:** Riset Maharani dkk. hanya melakukan klasifikasi label diskrit (*Good/Bad*). Riset kita mengembangkannya menjadi **Regresi Multi-Variabel** untuk menghasilkan angka konsentrasi terstandarisasi ISPU.
9. **Biagi, R., et al. (2024)**

   - **Judul:** *Development and machine learning-based calibration of low-cost multiparametric stations for the measurement of CO2 and CH4 in air*
   - **Publikasi:** *Heliyon*, Vol. 10, No. 6, e29772.
   - **Peran dalam Sistem:** Menunjukkan bahwa model berbasis *decision-tree ensemble* sangat tangguh mengoreksi distorsi fisik sensor Metal-Oxide Semiconductor (MOS) akibat kondisi mikro-lingkungan.
10. **Apostolopoulos, I. D., Fouskas, G., & Pandis, S. N. (2023)**

    - **Judul:** *Field Calibration of a Low-Cost Air Quality Monitoring Device in an Urban Background Site Using Machine Learning Models*
    - **Publikasi:** *Atmosphere (MDPI)*, Vol. 14, No. 2, Art. 368.
    - **Peran dalam Sistem:** Pembuktian eksperimen jangka panjang (22 bulan) bahwa Random Forest unggul dalam menangani pergeseran musiman (*seasonal drift*) dan *cross-sensitivity* antar-sensor gas.

---

### E. Integrasi Hardware, Edge AI (TinyML), dan Aktuator Mitigasi

11. **Fikri, A., Ridwan, M., & Agustine, D. (2025)**

    - **Judul:** *Implementation Of Internet Of Things (IOT) In Air Quality Monitoring (AQI)*
    - **Publikasi:** *Jurnal Ilmiah Sistem Informasi dan Ilmu Komputer (JUISIK)*
    - **Peran dalam Sistem:** - Memvalidasi kesamaan kombinasi hardware: **ESP32 + Sharp GP2Y1010AU0F + MQ-7 + MQ-135**.
      - **Research Gap yang Diisi:** Paper Fikri dkk. murni monitoring pasif di cloud (tanpa mitigasi udara dan komputasi masih di server luar). Riset kita menerapkan **Edge AI lokal di ESP32-S3** dan kendali **Closed-Loop PWM Kipas**.
12. **Malik, N., Aqiq, S., Ashraf, E., & Amir, A. (2026)**

    - **Judul:** *Lightweight Edge AI framework for Real Time Air Quality Analysis*
    - **Publikasi:** *ResearchGate Preprint / Review*
    - **Peran dalam Sistem:** - Validasi bahwa model AI terkompresi mampu dijalankan secara *offline* di mikrokontroler ESP32 dengan latensi rendah.
      - **Research Gap yang Diisi:** Sistem Malik dkk. hanya mendukung polutan tunggal (PM) dan inference beratnya masih dilempar ke HP. Riset kita menjalankan fusi *multi-polutan* (PM + CO + VOC) murni di ESP32-S3.
13. **Chelloug, S. A., Muthanna, M., Alshahrani, A., Al-Onaizan, M. H. A., Muthanna, A., & Jamil, F. (2026)**

    - **Judul:** *An IoT-Edge Enabled Deep–Fuzzy Hybrid Model for Real-Time Indoor Air Quality Optimization*
    - **Publikasi:** *Sensors (MDPI)*, Vol. 26, No. 13, Art. 3989.
    - **Peran dalam Sistem:** Memvalidasi pentingnya aktuasi mitigasi cerdas lingkar tertutup (*closed-loop adaptive fan control*) berbasis komputasi lokal untuk menghemat konsumsi energi dan menekan latensi respon.
14. **Rao, K. V., Kumar, C. M., Saritha, V., & Kanthamma, B. (2026)**

    - **Judul:** *Air Aware IoT: Low-Cost Sensor Solutions for Urban Pollution Monitoring and Public Health*
    - **Publikasi:** *Nature Environment and Pollution Technology*, Vol. 25, No. 1, Art. B4328.
    - **Peran dalam Sistem:** Memperkuat justifikasi bahwa kompensasi suhu secara real-time pada firmware adalah keharusan mutlak sebelum data dieksekusi oleh aktuator.
