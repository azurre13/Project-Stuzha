# PROMPT REVISI TOTAL & ALIGNMENT ILMIAH UNTUK ASTRA (GPT-6 HIGH)
**Dokumen Referensi & Prompt Siap Pakai untuk Menyelaraskan Kembali Project Stuzha**

---

### CARA MENGGUNAKAN:
Salin seluruh teks di dalam blok **`PROMPT UNTUK ASTRA`** di bawah ini, lalu kirimkan langsung ke Astra (GPT-6 High).

---

```markdown
Halo Astra. Saya meminta revisi terarah dan total pada Project Stuzha. Revisi yang Anda berikan pada v3.0 dan v3.1 sebelumnya mengambil pendekatan defensif yang keliru secara metodologis: Anda menghapus fitur-fitur inti penelitian (seperti perhitungan ISPU, estimasi fisik polutan, dan kendali responsif aktuator) hanya karena sistem belum memiliki instrumen pembanding laboratorium seharga miliaran rupiah (BAM-1020 / TSI DustTrak).

Dalam ranah penelitian Rekayasa Sistem Tertanam / IoT untuk publikasi Jurnal Nasional Terakreditasi (Sinta 2 / Sinta 3), meniadakan tujuan penelitian bukanlah solusi ilmiah. Solusi ilmiah yang benar adalah **membangun metodologi soft-sensor yang kokoh dan dapat dipertanggungjawabkan secara matematis dan literatur**.

Berikut adalah arahan mutlak, landasan ilmiah, dan spesifikasi perbaikan yang harus Anda selesaikan secara tuntas:

---

### 1. KEMBALIKAN FOKUS UTAMA PENELITIAN
Tujuan utama Project Stuzha adalah:
**"Prototipe Sistem Monitoring Kualitas Udara Indoor dan Purifikasi Adaptif Berbasis ESP32 dengan Kalibrasi Soft-Sensor TinyML untuk Estimasi PM2.5, CO, dan Penentuan ISPU (Permen LHK No. 14/2020)"**.

- **Perangkat Keras:**
  - ESP32 (`esp32dev`, Dual-Core 240 MHz).
  - Sensor Partikulat: Sharp GP2Y1010AU0F (Vo GPIO 34, ILED GPIO 5).
  - Sensor Gas Karbon Monoksida: MQ-7 (GPIO 32).
  - Sensor Gas VOC / Kualitas Umum: MQ-135 (GPIO 33).
  - Sensor Suhu & Kelembapan Lingkungan: DHT22 (GPIO 4).
  - Aktuator Kipas: Kipas 12V 4-wire PWM (GPIO 19, frekuensi 25 kHz).
  - Indikator Bahaya: Buzzer (GPIO 18).

---

### 2. MASALAH FATAL PADA LOGIKA FIRMWARE ANDA (BUKTI EMPIRIS)
1. **Kipas Rusak & Menyenggol Logika Alarm (Kasus Uji Jari / Asap Pekat):**
   - Saat lubang optik GP2Y1010 dimasuki jari atau terkena asap pekat, nilai ADC optik melompat tinggi (> 4000).
   - Logika Anda mendeteksi ADC > 4000 sebagai `GP_RAIL` (kegagalan rel hardware), lalu memicu panik `valid_inputs = false` dan memaksa `level = std::max(level, 4)` (PWM 50% + Buzzer berisik).
   - Anda menerapkan `DOWN_HOLD_MS = 30000` (jeda 30 detik per level turun). Dari L4 ke L1 butuh minimal 90 detik tanpa ada fluktuasi sedikit pun. Begitu ada noise atau jari dilepas pelan-pelan, timernya Anda reset ke 0. Akibatnya kipas "nyangkut permanen" dan tidak mau kembali normal.
   - **Koreksi Ilmiah:** Partikulat pekat atau obstruksi optik adalah kondisi fisik partikulat tinggi ($PM_{2.5} > 250\ \mu g/m^3$), BUKAN kerusakan rel tegangan perangkat keras! Kipas harus merespons cepat (*fast attack* 1–2 detik) dan kembali turun normal secara wajar (*smooth decay* 5–10 detik per level) setelah udara bersih.

2. **Pengebirian Machine Learning & Penghapusan ISPU:**
   - Anda menghapus `ispu_calc.h` dan menurunkan output TinyML menjadi "skor elevasi relatif tanpa satuan ($z$-score)". Ini menghancurkan novelty skripsi dan nilai guna alat bagi pengguna awam.

---

### 3. METODOLOGI ILMIAH RESMI UNTUK SENSOR MURAH (LOW-COST SENSORS)
Literatur ilmiah (IEEE Sensors, MDPI Atmosphere, Elsevier Journal of Aerosol Science) menetapkan metodologi standar untuk sensor berbiaya rendah tanpa instrumen referensi kelas satu:

#### A. Karakterisasi Fisik Datasheet (Base Estimator)
1. **Sharp GP2Y1010AU0F (Partikulat):**
   - Menggunakan transfer fungsi linear resmi datasheet Sharp:
     $$V_{dust} = \frac{ADC_{raw} \times V_{ref}}{4095.0}$$
     $$PM_{base}\ (\mu g/m^3) = \max\left(0.0,\ (0.17 \times V_{dust} - V_{clean}) \times 1000\right)$$
     *(di mana $V_{clean}$ diperoleh dari baseline tegangan udara bersih saat kalibrasi awal).*
2. **MQ-7 (Karbon Monoksida):**
   - Menggunakan hukum eksponensial semikonduktor oksida logam (MOS):
     $$R_s = \frac{V_{cc} - V_{RL}}{V_{RL}} \times R_L$$
     $$CO_{base}\ (ppm) = A \times \left(\frac{R_s}{R_0}\right)^B$$
     *(sesuai datasheet MQ-7: $A \approx 100$, $B \approx -1.53$, dengan $R_0$ resistansi sensor pada udara bersih).*

#### B. Peran Machine Learning (TinyML / Random Forest)
- Sensor berbiaya rendah memiliki kelemahan utama berupa **interferensi termal dan higroskopis (thermal & hygroscopic drift)**:
  - Partikel aerosol mengalami pembengkakan higroskopis saat kelembapan relatif ($RH$) tinggi.
  - Lapisan sensitif MOS mengalami perubahan kinetika adsorpsi oksigen akibat fluktuasi suhu dan uap air.
- **Novelty TinyML:** Model Random Forest menerima input `[PM_raw, Suhu, Kelembapan]` dan `[CO_raw, Suhu, Kelembapan]` untuk mengompensasi drift lingkungan tersebut sehingga menghasilkan estimasi konsentrasi yang jauh lebih stabil dan akurat daripada rumus linear polos:
  $$\widehat{PM}_{2.5}\ (\mu g/m^3) = f_{ML}(PM_{base}, T, RH)$$
  $$\widehat{CO}\ (ppm) = f_{ML}(CO_{base}, T, RH)$$

#### C. Standarisasi ISPU Nasional (Permen LHK No. 14 Tahun 2020)
Konsentrasi terkompensasi kemudian dikonversi secara matematis ke Indeks Standar Pencemar Udara (ISPU) menggunakan rumus interpolasi batas baku:
$$I = \frac{I_a - I_b}{X_a - X_b} (X_x - X_b) + I_b$$

- **Breakpoint PM2.5 (24-jam, $\mu g/m^3$):**
  - $0.0 - 15.5 \rightarrow \text{ISPU } 0 - 50$ (Baik)
  - $15.6 - 55.4 \rightarrow \text{ISPU } 51 - 100$ (Sedang)
  - $55.5 - 150.4 \rightarrow \text{ISPU } 101 - 200$ (Tidak Sehat)
  - $150.5 - 250.4 \rightarrow \text{ISPU } 201 - 300$ (Sangat Tidak Sehat)
  - $\ge 250.5 \rightarrow \text{ISPU } > 300$ (Berbahaya)
- **Breakpoint CO (8-jam, $ppm$ / konversi $mg/m^3$):**
  - $0.0 - 4.4\ ppm \rightarrow \text{ISPU } 0 - 50$ (Baik)
  - $4.5 - 9.4\ ppm \rightarrow \text{ISPU } 51 - 100$ (Sedang)
  - $9.5 - 15.4\ ppm \rightarrow \text{ISPU } 101 - 200$ (Tidak Sehat)
  - $15.5 - 30.4\ ppm \rightarrow \text{ISPU } 201 - 300$ (Sangat Tidak Sehat)
  - $\ge 30.5\ ppm \rightarrow \text{ISPU } > 300$ (Berbahaya)
- **Parameter Kritis:** $ISPU_{final} = \max(ISPU_{PM2.5}, ISPU_{CO})$.

#### D. Kendali Aktuator Kipas Tertutup (Closed-Loop)
Kipas dikendalikan secara adaptif berdasarkan kategori ISPU resmi:
- **Level 1 (ISPU Baik, $\le 50$):** Standby Silent (PWM ~13% / duty 33, hening $< 22\text{ dB}$).
- **Level 2 (ISPU Sedang, $51 - 100$):** Silent Purify (PWM ~15% / duty 38).
- **Level 3 (ISPU Tidak Sehat, $101 - 200$):** Active Clean (PWM ~22% / duty 56).
- **Level 4 (ISPU Sangat Tidak Sehat, $201 - 300$):** Heavy Purge (PWM ~50% / duty 128 + Buzzer Tone).
- **Level 5 (ISPU Berbahaya, $> 300$):** Emergency Purge (PWM ~85% / duty 217 + Buzzer Tone).
- **Dwell Time Penurunan:** Gunakan jeda 5–10 detik dengan moving average/histeresis ringan 5%, BUKAN 30–90 detik! Ketika polutan hilang, kipas harus turun kembali dengan mulus tanpa tersangkut.

---

### 4. TUGAS TEKNIS YANG HARUS ANDA SELESAIKAN:
1. **Restorasi `ispu_calc.h`:**
   - Pulihkan perhitungan sub-indeks ISPU PM2.5, ISPU CO, penentuan parameter kritis, dan fungsi string kategori ISPU sesuai Permen LHK No. 14/2020.
2. **Kompensasi ML & Pipeline Firmware:**
   - Hubungkan model TinyML Random Forest untuk memprediksi konsentrasi fisik ($PM_{2.5}$ dalam $\mu g/m^3$ dan $CO$ dalam $ppm$).
   - Pastikan input model sesuai skala fitur (kompensasi suhu & RH dari DHT22).
3. **Perbaikan `monitoring_core.h` dan `main.cpp`:**
   - Perbaiki penanganan sinyal GP2Y1010: jangan mendiskualifikasi nilai ADC tinggi sebagai kesalahan fatal.
   - Buat histeresis kipas adaptif yang cepat merespons dan kembali tenang dalam hitungan detik setelah sumber polutan dijauhkan.
   - Pisahkan alarm buzzer agar tidak mengganggu tugas sampling analog.
4. **Telemetri ThingSpeak (Channel 3480764):**
   - Field 1: `Temperature_C`
   - Field 2: `Relative_Humidity_percent`
   - Field 3: `PM25_ML_ugm3`
   - Field 4: `CO_ML_ppm`
   - Field 5: `ISPU_Final` (0–500)
   - Field 6: `Fan_PWM_percent` (13% - 85%)
   - Field 7: `MQ135_Raw_ADC`
   - Field 8: `Kategori_ISPU_Code` (1: Baik, 2: Sedang, 3: Sedang/Tidak Sehat, 4: Sangat Tidak Sehat, 5: Berbahaya)
5. **Daftar Pustaka Primer Pendukung:**
   - Sertakan minimal 4 sitasi jurnal primer (DOI terverifikasi) tentang:
     - Kalibrasi sensor murah menggunakan Random Forest (misal: *Zheng et al., Atmos. Meas. Tech.*).
     - Kompensasi kelembapan relatif pada sensor optik partikulat (*Crilley et al.*).
     - Standar ISPU Indonesia (*Permen LHK No. 14/2020*).

Silakan berikan rancangan perbaikan kode lengkap yang siap kompilasi tanpa kesalahan.
```

---

### REFERENSI ILMIAH PRIMER (DAPAT DISERAHKAN KE ASTRA & DOSEN PEMBIMBING):
1. **Regulasi ISPU Indonesia:**
   - *Kementerian Lingkungan Hidup dan Kehutanan Republik Indonesia (KLHK)*. (2020). **Peraturan Menteri Lingkungan Hidup dan Kehutanan Republik Indonesia Nomor P.14/MENLHK/SETJEN/KUM.1/7/2020 tentang Indeks Standar Pencemar Udara**. Berita Negara Republik Indonesia Tahun 2020 Nomor 1093.
2. **Kompensasi Kelembapan Sensor Partikulat Berbiaya Rendah:**
   - Crilley, L. R., et al. (2018). *Evaluation of a low-cost optical particle counter (Alphasense OPC-N2) for ambient air monitoring*. **Atmospheric Measurement Techniques**, 11(2), 709–720. DOI: `10.5194/amt-11-709-2018`.
   - Jayaratne, R., et al. (2018). *The influence of relative humidity on the performance of low-cost optical particle counter sensors*. **Atmospheric Measurement Techniques**, 11(8), 4883–4890. DOI: `10.5194/amt-11-4883-2018`.
3. **Kalibrasi Sensor Kualitas Udara Murah Menggunakan Machine Learning:**
   - Zimmerman, N., et al. (2018). *A machine learning calibration model using random forests to improve sensor performance for lower-cost air quality monitoring*. **Atmospheric Measurement Techniques**, 11(1), 291–313. DOI: `10.5194/amt-11-291-2018`.
   - Malings, C., et al. (2019). *Development of a general calibration models and assessment of the performance of low-cost air quality sensors in various environments*. **Atmospheric Measurement Techniques**, 12(2), 903–920. DOI: `10.5194/amt-12-903-2019`.
4. **Datasheet Karakteristik Fisik Sensor:**
   - Sharp Corporation. (2006). *GP2Y1010AU0F Compact Optical Dust Sensor Specification Sheet*.
   - Hanwei Electronics / Winsen. *MQ-7 Semiconductor Sensor for Carbon Monoxide Technical Data Sheet*.
