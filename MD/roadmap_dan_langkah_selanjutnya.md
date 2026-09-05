# 🧭 Roadmap Kolaborasi & Rencana Langkah Selanjutnya — Project Stuzha

> **Dokumen Panduan Pengembangan & Eksperimen Tim**  
> **Kolaborator:** [@azurre13](https://github.com/azurre13) | [@Garnie104](https://github.com/Garnie104) | [@Riq-Z](https://github.com/Riq-Z)  
> **Tujuan Akhir:** Publikasi Artikel Jurnal Ilmiah Kualitas Udara Indoor (Target Sinta 3 / Sinta 2)

---

## 📌 1. Latar Belakang & Tujuan Dokumen Ini

Dokumen ini disusun untuk menyelaraskan visi, alur kerja, dan langkah konkret antar anggota tim setelah berhasil menyelesaikan kalibrasi Machine Learning awal dan restrukturisasi kode firmware ESP32-S3.

Seluruh langkah dalam dokumen ini diturunkan langsung dari **21 referensi jurnal ilmiah** dan regulasi resmi **Permen LHK No. 14 Tahun 2020** yang telah kita himpun.

---

## ✅ 2. Status Terkini: FASE 1 Telah Rampung (Data Science & TinyML)

Semua kebutuhan data science di laptop/PC telah berhasil dieksekusi dan tersimpan rapi di folder [`Fase_1_Evaluasi_ML/`](../Fase_1_Evaluasi_ML/):

1. **Pelatihan Model Bebas Leakage:**
   - Model **RF_PM** (GP2Y1010AU0F + DHT22) dan **RF_CO** (MQ-7 + DHT22) telah dilatih menggunakan 167.000+ data valid.
   - Masalah *target leakage* dan *scale mismatch* telah diselesaikan secara ilmiah mengikuti teori fisika aerosol (*Köhler hygroscopic growth curve*).
2. **Hasil Kuantitatif Akurasi (Siap Masuk Paper):**
   - **Partikulat PM2.5:** $R^2$ melonjak ke **0.9997 (Akurasi 99.97%)**, RMSE terpangkas **86.9%** (dari 15.05 ke 1.98 µg/m³), dan rata-rata error (MAE) hanya **0.58 µg/m³**.
   - **Gas CO:** $R^2$ meningkat ke **0.8087 (Akurasi 80.87%)**, RMSE turun ke **0.61 ppm**.
3. **Grafik Publikasi Ilmiah (300 DPI):**
   - 4 grafik standar publikasi telah selesai digenerate di `Fase_1_Evaluasi_ML/grafik/` (Scatter plot 1:1, Kurva koreksi RH, Evaluasi CO, dan Feature Importance).
4. **Ekspor Model ke Hardware:**
   - Model TinyML bahasa C murni telah terintegrasi di `Program/Kode/include/model_pm.h` dan `model_co.h`.

---

## ⚡ 3. Rencana FASE 2: Uji Eksperimental pada Perangkat Fisik (ESP32-S3)

*Tujuan: Mengambil data performa fisik alat nyata untuk membuktikan kontribusi sistem di jurnal.*

### A. Pengujian Benchmark Komputasi TinyML di ESP32-S3
* **Apa yang diuji:**
  1. **Latensi Inferensi (ms):** Mengukur waktu eksekusi fungsi `model_pm_predict()` dan `model_co_predict()` dalam satuan mikrodetik/milidetik menggunakan `micros()` di ESP32.
  2. **Konsumsi Memori (SRAM & Flash):** Mencatat persentase penggunaan memori saat kompilasi PlatformIO.
* **Landasan Referensi:** **Jurnal 8, 10, & 20** (*TinyML Edge Computing*). Reviewer jurnal sangat menyukai data kuantitatif yang membuktikan bahwa AI berjalan sangat cepat dan hemat daya pada mikrokontroler berbiaya murah.

### B. Pengujian Respons Aktuator Kipas Adaptif PWM
* **Apa yang diuji:**
  - Mengamati apakah putaran kipas DC (12V 1.65A 6.200 RPM, lubang kotak 12x12 cm) berubah halus secara *closed-loop* mengikuti kategori ISPU resmi dengan deadband histeresis 5-poin:
    * **Baik ($I \le 50$):** PWM 13% (~806 RPM, Ultra-Silent Standby < 22 dB)
    * **Sedang ($I \le 100$):** PWM 15% (~930 RPM, Silent Sleep Purify < 28 dB)
    * **Tidak Sehat ($I \le 200$):** PWM 22% (~1.364 RPM, Active Clean < 38 dB)
    * **Sangat Tidak Sehat ($I \le 300$):** PWM 50% (~3.100 RPM, Heavy Purge)
    * **Berbahaya ($I > 300$):** PWM 85% (~5.270 RPM, Max Emergency Purge) + Alarm Aktif.
* **Landasan Referensi:** **Jurnal 16 & 17** (*Dynamic Ventilation & Energy Efficiency*). Menjadi bukti bahwa kendali adaptif lebih efisien energi dibanding saklar *on-off* statis pada purwarupa lama (**Jurnal 19**).

### C. Validasi Logika ISPU & Secondary Safety Guard (MQ-135)
* **Apa yang diuji:**
  1. Menguji apakah sistem selalu memilih nilai tertinggi antara sub-indeks PM2.5 dan CO sebagai *Parameter Pencemar Kritis* sesuai **Permen LHK No. 14 Tahun 2020** dan **Jurnal 11**.
  2. Menguji fitur pengaman gas campuran: saat sensor MQ-135 mendeteksi uap kimia/alkohol pekat (nilai ADC > 2500), kipas otomatis dipaksa naik ke 85% (*booster*) tanpa merusak indeks resmi ISPU (**Jurnal 14**).

### D. Skenario Pengujian Fisik Ruangan:
1. **Skenario Udara Normal:** Ruangan kamar/laboratorium tertutup tanpa polutan.
2. **Skenario Polusi Partikulat:** Pengujian menggunakan sumber partikulat terkontrol (asap obat nyamuk / dupa) untuk menguji respons deteksi GP2Y dan penurunan konsentrasi oleh kipas filtrasi.
3. **Skenario Uji Gangguan Kelembapan:** Pengujian sensor debu saat diberi hembusan uap air/humidifier untuk membuktikan bahwa pembacaan tidak melonjak liar berkat filter koreksi Random Forest (**Jurnal 4 & 6**).

---

## 📝 4. Rencana FASE 3: Penyusunan Naskah Jurnal Ilmiah (Paper Drafting)

*Tujuan: Menulis artikel ilmiah siap submit ke jurnal terakreditasi Sinta 3 / Sinta 2.*

### Struktur Naskah & Pembagian Konten:
1. **Judul & Abstrak:**
   - Menyoroti kombinasi: *Low-Cost IoT Sensors, Edge AI TinyML Random Forest, ISPU Regulation, Adaptive Filtration Control, ESP32-S3*.
2. **Bab 1 — Pendahuluan (Introduction):**
   - Urgensi kesehatan mitigasi racun udara indoor (**Jurnal 21**).
   - Masalah kelemahan akurasi sensor murah akibat bias cuaca & kelembapan (**Jurnal 4, 5, 6**).
   - *State of the Art & Research Gap:* Membandingkan sistem kita dengan riset sebelumnya yang masih berbasis *rule-based* kaku atau tanpa kalibrasi AI (**Jurnal 9, 18, 19**).
3. **Bab 2 — Metodologi (Methodology):**
   - Arsitektur sistem 3-tahap (Fusi Sensor ML $\rightarrow$ Interpolasi ISPU $\rightarrow$ Parameter Kritis).
   - Formula matematik ISPU (Permen LHK No. 14 Tahun 2020).
   - Implementasi TinyML Random Forest (Scikit-Learn ke C-Header array).
4. **Bab 3 — Hasil dan Pembahasan (Results & Discussion):**
   - Memasukkan tabel metrik dari `Fase_1_Evaluasi_ML/tabel_metrik_evaluasi.csv`.
   - Menampilkan 4 grafik visualisasi dari `Fase_1_Evaluasi_ML/grafik/`.
   - Menampilkan hasil uji latensi (ms), efisiensi RAM ESP32-S3, dan grafik respons perubahan kecepatan kipas dari Fase 2.
5. **Bab 4 — Kesimpulan (Conclusion):**
   - Ringkasan pencapaian dan rekomendasi riset lanjutan.

---

## 📋 5. Checklist Pembagian Tindakan Tim (Action Items)

- [x] **Fase 1 Selesai:** Dataset dibersihkan, Random Forest dilatih bebas leakage, metrik dihitung, grafik 300 DPI dibuat, dan C header di-export.
- [ ] **Persiapan Hardware (Fase 2):**
  - [ ] Hubungkan ESP32-S3 dan sensor ke laptop, lakukan *build* & *upload* firmware via PlatformIO.
  - [ ] Buka Serial Monitor (115200 baud) untuk memverifikasi keluaran telemetri:
        `[TELEMETRI] T:.. | RH:.. | PM2.5:[Raw -> ML] | CO:.. | ISPU:.. | Kipas:..`
  - [ ] Catat latensi eksekusi fungsi ML dan penggunaan memori chip.
  - [ ] Lakukan uji paparan polutan terkontrol dan amati respon PWM kipas.
- [ ] **Penyusunan Paper (Fase 3):**
  - [ ] Buat file draf naskah di `MD/draft_paper_jurnal.md`.
  - [ ] Susun Pendahuluan dan Metodologi bersama tim.
  - [ ] Tempelkan grafik dan tabel evaluasi ke naskah.
