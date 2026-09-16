# Keputusan Metode Machine Learning & Analisis Masalah Stuzha
**Project Stuzha — Edge AI ISPU Indoor Air Quality**  
**Tanggal Evaluasi:** 10 September 2026  
**Dokumen Acuan:** [README_handoff_antigravity.md](README_handoff_antigravity.md), [AGENTS.md](../AGENTS.md), [metode_ispu_v4.md](metode_ispu_v4.md)

---

## 1. Koreksi Evaluasi & Integritas Ilmiah

### A. Evaluasi Satuan Mendeley & Bukti Pengali $\times 1000$ (Konflik Belum Terselesaikan)
- **Fakta Metadata Penulis:** Metadata resmi Mendeley Data (Sonawani & Patil, DOI `10.17632/2r232jpfb2.1`) menyatakan parameter `PM2.5: Measured in µg/m³ using the GP2Y1010AU0F sensor`.
- **Fakta Angka CSV:** Nilai numerik pada kolom `PM2.5` berkisar antara $0.00$ hingga $0.47$.
- **Asal-usul Pengali $\times 1000$:** Penelusuran riwayat kode git membuktikan bahwa pengali $\times 1000$ diperkenalkan pada commit `67f2639` (*Wed Sep 2 23:21:30 2026*, `fix(ml): eliminate target leakage, align physical sensor scales, and update firmware inference`) berdasarkan komentar kode pengembang: *"Ground Truth sebenarnya (µg/m³): Nilai kolom Mendeley (mg/m³) dikalikan 1000"*, dengan asumsi pribadi bahwa angka kecil tersebut mewakili $\text{mg/m}^3$ dan tabel ISPU membutuhkan skala $\mu\text{g/m}^3$.
- **Kesimpulan Ilmiah:** **Tidak ditemukan bukti primer** dari penulis dataset yang mengonfirmasi bahwa nilai tersebut adalah $\text{mg/m}^3$. Rentang tabel ISPU Permen LHK 14/2020 adalah acuan regulasi kualitas udara, **bukan alasan sah untuk mengubah satuan dataset sumber**. Konflik satuan ini dicatat secara resmi sebagai **belum terselesaikan (*unresolved unit conflict*)**.

---

### B. Audit Kebocoran Data (*Data Leakage*) Model Aktif
- **Temuan Irisan Data:** Model aktif historis (`model_pm.h`) dilatih menggunakan `train_test_split(random_state=42)` dengan pengacakan acak (*random shuffle*) pada dataset sensor valid historis sebanyak **167.466 baris** (tanpa filter kolom tanggal). Pada split kronologis berbasis deret waktu, terdapat 1 baris (indeks 2310) yang memiliki format tanggal tidak valid sehingga dataset kronologis berjumlah **167.465 baris** ($N_{\text{train}} = 133.972$, $N_{\text{test}} = 33.493$).
- **Hasil Perhitungan Dinamis Irisan Data:** Skrip evaluasi menghitung irisan indeks baris asli secara dinamis (`set(legacy_train_idx) & set(chrono_test_idx)`): terbukti bahwa sebanyak **26.689 dari 33.493 baris uji (79,6853% atau 79,685%) telah masuk ke dalam data latih model aktif**.
- **Kesimpulan Ilmiah:** Perbandingan model aktif dengan model kronologis baru adalah **tidak adil** karena model aktif mengalami kebocoran data deret waktu yang parah. Oleh karena itu, pengujian model aktif dipisahkan secara ketat hanya untuk keterlacakan riwayat (*traceability/archive*).

---

## 2. Hasil Evaluasi Setara PM2.5 (GP2Y)

Evaluasi terintegrasi ke dalam pipeline utama [ml_training/pipeline.py](../ml_training/pipeline.py) dan dijalankan melalui [Fase_1_Evaluasi_ML/evaluasi_setara_pm.py](../Fase_1_Evaluasi_ML/evaluasi_setara_pm.py). Seluruh artefak lengkap (prediksi 33.493 baris, metrik, model kandidat Python .joblib, grafik PNG, model card, report) tersimpan di folder run baru: [Fase_1_Evaluasi_ML/hasil/evaluasi_setara_pm_20260910_070417_9b31de/](../Fase_1_Evaluasi_ML/hasil/evaluasi_setara_pm_20260910_070417_9b31de/).

Metode: Pembagian waktu murni (*chronological split*) tanpa kebocoran data (80% masa lalu untuk training, 20% masa depan untuk testing, $N_{\text{test}} = 33.493$).

### Tabel Metrik Evaluasi Bersih

| Skala Evaluasi | Model / Metode | RMSE | MAE | $R^2$ | Penurunan RMSE | Sifat Evaluasi |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Skala Numerik Sumber**<br>*(Konflik Satuan Belum Terselesaikan)* | Raw Input (Tanpa Koreksi) | 0.00315 | 0.00227 | -2.0439 | 0.0% | Baseline masukan terganggu formula simulasi |
| | Regresi Linear (3 Fitur, float64) | 0.00663 | 0.00576 | -12.5063 | -110.64% | Konsisten multi-skala; gagal memodelkan komponen non-linear uap air |
| | **Random Forest Chrono** | **0.00021** | **0.00001** | **0.9860** | **+93.22%** | Latih 80% lalu, uji 20% depan; bebas data leakage |
| **Skala $\times 1000$**<br>*(Asumsi Pengali Legacy Commit `67f2639`)* | Raw Input (Tanpa Koreksi) | 3.14592 | 2.26507 | -2.0439 | 0.0% | Baseline masukan terganggu formula simulasi |
| | Regresi Linear (3 Fitur, float64) | 6.62671 | 5.75826 | -12.5063 | -110.64% | Konsisten multi-skala; gagal memodelkan komponen non-linear uap air |
| | **Random Forest Chrono** | **0.21310** | **0.01186** | **0.9860** | **+93.23%** | Latih 80% lalu, uji 20% depan; bebas data leakage |
| *(Uji Keterlacakan Riwayat)* | *RF Rekonstruksi Python (`model_pm.joblib`)* | *0.20727* | *0.00930* | *0.9868* | *+93.41%* | *Tercemar 79.685% data leakage dari random split* |
| | *RF Header C++ Aktif (`model_pm.h` via g++)* | *0.20757* | *0.00931* | *0.9867* | *+93.40%* | *Uji binary C++ (eksekusi: success, status paritas: passed_aggregate_with_exceptions); 99,988% sampel memenuhi toleransi, empat sampel melampauinya; tercemar 79.685% leakage* |

> **Penjelasan Teknis Paritas C++ vs Joblib & Presisi Baseline Linear:**
> 1. **Baseline Linear & Presisi Float64:** Pada skala numerik sumber ($0 - 0,47$), kolom respon berorde $\approx 0,04$ sedangkan suhu $\approx 30$ dan kelembapan $\approx 60$. Matriks inversi pada float32 mengalami *poor conditioning*. Menggunakan float64 memulihkan konsistensi skala penuh: RMSE skala sumber tepat $0,00663$ dan skala $\times 1000$ tepat $6,62671$ ($1000 \times 0,00663$).
> 2. **Paritas C++ vs Python & Jejak 4 Pelanggaran Batas:** Status paritas ditetapkan sebagai **`passed_aggregate_with_exceptions`**: **99,988% sampel memenuhi toleransi, empat sampel melampauinya** (toleransi $10^{-4}$, rata-rata selisih $2,63 \times 10^{-5}$, selisih maksimal $0,324$). Keempat selisih ini telah diverifikasi secara otomatis melalui skrip penelusuran jalur pohon [Fase_1_Evaluasi_ML/trace_pm_legacy_parity.py](../Fase_1_Evaluasi_ML/trace_pm_legacy_parity.py) yang membuktikan percabangan biner per pohon dan per node:
>    - **Baris uji 8090 (baris sumber 148060):** Temp $= 33.4000015^\circ\text{C}$ menguji Pohon 17, Node 47. Ambang batas di C++ bernilai `33.400000f` sedangkan di Python sklearn bernilai double `33.39999961853027`. Pada representasi biner, Python mengambil cabang kanan (daun $1,470588$), sedangkan C++ mengambil cabang kiri (daun $11,196970$). Selisih pada pohon ini adalah $+9,726381$, yang setelah dibagi rata ke 30 pohon menghasilkan lonjakan prediksi total sebesar $\Delta = +0,324213$.
>    - **Baris uji 9432 (baris sumber 149402):** Temp $= 31.5300007^\circ\text{C}$ menguji Pohon 29, Node 27. Ambang C++ `31.530001f` vs Python `31.52999973297119`. Python ke kanan (daun $4,5$), C++ ke kiri (daun $1,2$). Selisih daun $-3,3 / 30 \implies \Delta = -0,110000$.
>    - **Baris uji 13708 (baris sumber 153678):** Temp $= 31.5400009^\circ\text{C}$ menguji Pohon 4, Node 39. Ambang C++ `31.540000f` vs Python `31.539999961853027`. Python ke kanan (daun $10,888889$), C++ ke kiri (daun $5,0$). Selisih daun $-5,888889 / 30 \implies \Delta = -0,196296$.
>    - **Baris uji 29821 (baris sumber 169792):** Temp $= 26.3600006^\circ\text{C}$ menguji Pohon 26, Node 14. Ambang C++ `26.360001f` vs Python `26.359999656677246`. Python ke kanan (daun $2,5$), C++ ke kiri (daun $9,946809$). Selisih daun $+7,446809 / 30 \implies \Delta = +0,248227$.
> 3. **Model Kandidat Tersimpan:** Model Python kandidat untuk reproduksi tersimpan di folder run sebagai `candidate_model_pm_raw.joblib` dan `candidate_model_pm_x1000.joblib` lengkap dengan hash SHA256.

### Batasan Kesimpulan PM yang Diakui
> **Pernyataan Batasan Ilmiah:**  
> Evaluasi ini **hanya membuktikan bahwa Random Forest berhasil mengoreksi gangguan buatan sesuai formula simulasi matematis**. Hasil ini **TIDAK BOLEH** diklaim sebagai bukti bahwa sistem telah mengatasi pertumbuhan partikel debu akibat kelembapan (*hygroscopic aerosol growth*) pada sensor fisik Sharp GP2Y di lapangan, karena dataset Mendeley tidak menyediakan data pengukuran ADC fisik paralel dengan instrumen referensi partikulat independen.

---

## 3. Analisis Jalur Sensor MQ-7 (CO): Solusi Nyata vs Mempertahankan Kondisi Lama

Penggantian model CO berbasis data pasangan (*data-driven transfer*) **belum dapat dilakukan secara valid** karena **belum ditemukan dataset MQ-7 berpasangan yang cocok** dengan instrumen analitik gas CO rujukan.

Berikut pemilahan transparan antara **mana yang mempertahankan fungsi prototipe** dan **mana yang menjadi batas metode**:

---

### A. Mempertahankan Model Aktif untuk Pengujian Prototipe (Opsi Model Aktif `model_co.h`)

- **Deskripsi:** Tetap menjalankan model Random Forest aktif di firmware yang dilatih dari sensor PT08.S1 dataset UCI.
- **Karakteristik:**
  - **Batas Metode:** Ketidakcocokan mendasar antara sensor resistif PT08 (Italia) dan MQ-7 tetap ada. Label "estimasi eksperimental" menjelaskan batasan tersebut, bukan menghilangkannya.
  - **Fungsi Utama:** Menjalankan **prototipe sistem monitoring indoor** untuk menguji implementasi, stabilitas runtime ESP32, telemetri ThingSpeak STZ4, komputasi TinyML, dan dinamika kendali PWM kipas.
  - **Status untuk Penelitian:** Penelitian menilai perilaku sistem kendali dan telemetri, **bukan mengklaim kalibrasi konsentrasi gas tervalidasi fisik** atau akurasi berdasarkan $R^2$.

---

### B. Analisis Pendekatan Alternatif

#### **1. Opsi Transisi ke Formula Karakteristik Datasheet MQ-7**
Pendekatan menggunakan formula log-resistansi semikonduktor SnO2:
$$\text{ppm} = \left(\frac{R_s / R_0}{A}\right)^{1/B}$$
dengan:
$$V_{\text{out}} = \text{ADC} \times \frac{3.3}{4095}, \quad R_s = R_L \times \left(\frac{V_c - V_{\text{out}}}{V_{\text{out}}}\right)$$

**Catatan Verifikasi Rangkaian & Komponen:**
- Suplai expansion board sebesar 5 V **belum membuktikan konfigurasi heater internal modul**. Produsen modul spesifik, ada/tidaknya sirkuit siklus heater, nilai resistor beban fisik ($R_L$), serta nilai resistansi udara bersih ($R_0$) **belum diverifikasi secara fisik** sehingga tidak boleh diasumsikan sebagai fakta pasti.
- Menerapkan rumus ini tanpa pengukuran fisik berisiko mengarang nilai $R_0$ atau gain kalibrasi.

#### **2. Karakteristik Penentuan Sub-Indeks & Kendali Firmware**
- **Prinsip Sub-Indeks Maksimum:** Sesuai Permen LHK 14/2020, firmware menghitung sub-indeks PM dan sub-indeks CO, lalu mengambil **nilai maksimum** untuk menentukan indeks ISPU dan kategori kendali kipas. Kategori tidak hanya ditentukan oleh PM.
- **Dua Basis Waktu:** Indeks instan (dihitung tiap detik) digunakan secara khusus untuk kendali respon cepat kipas (beserta histeresis dan penundaan penurunan level), sedangkan estimasi berbasis rata-rata bergerak 24 jam dicatat terpisah untuk analisis tren jangka panjang.
- **Ketidakpastian Model:** Ketidakpastian estimasi pada kedua model (PM dan CO) ikut memengaruhi indeks instan dan kategori yang terbentuk.

---

## 4. Keputusan Sesi Ini untuk Pemilik & Pelaksanaan Pengujian

Sesuai arahan pemilik, sesi pengujian daya tahan (stress test) tujuh hari **menggunakan Opsi 1 (mempertahankan model aktif)**:
1. **Fokus Pengujian:** Menilai stabilitas jangka panjang, kinerja FreeRTOS, ketiadaan reset/crash berulang, integritas telemetri STZ4, dan perilaku respon kendali kipas pada kondisi indoor nyata.
2. **Integritas Naskah:** Naskah publikasi melaporkan hasil implementasi edge AI sistem tertanam dengan jujur tanpa mengklaim kalibrasi gas analitik.
3. **Firmware Frozen:** Header `model_pm.h` dan `model_co.h` dibekukan untuk sesi ini; tidak ada retraining dan tidak ada modifikasi arsitektur kendali.
