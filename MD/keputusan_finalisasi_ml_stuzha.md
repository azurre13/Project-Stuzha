# Keputusan Metode Machine Learning & Analisis Masalah Stuzha
**Project Stuzha — Edge AI ISPU Indoor Air Quality**  
**Tanggal Evaluasi:** 10 September 2026  
**Dokumen Acuan:** [README_handoff_antigravity.md](README_handoff_antigravity.md), [AGENTS.md](../AGENTS.md), [metode_ispu_v4.md](metode_ispu_v4.md)

---

## 1. Koreksi Evaluasi & Integritas Ilmiah

### A. Evaluasi Satuan Mendeley & Bukti Pengali $\times 1000$ (Konflik Belum Terselesaikan)
- **Fakta Metadata Penulis:** Metadata resmi Mendeley Data (Sonawani & Patil, DOI `10.17632/2r232jpfb2.1`) menyatakan parameter `PM2.5: Measured in µg/m³ using the GP2Y1010AU0F sensor`.
- **Fakta Angka CSV:** Nilai numerik pada kolom `PM2.5` berkisar antara $0.00$ hingga $0.47$.
- **Asal-usul Pengali $\times 1000$:** Penelusuran riwayat kode membuktikan bahwa pengali $\times 1000$ diperkenalkan sepihak oleh pengembang skrip training legacy terdahulu (commit `89bcfa3`) berdasarkan asumsi pribadi bahwa angka kecil tersebut mewakili $\text{mg/m}^3$ dan tabel ISPU membutuhkan skala $\mu\text{g/m}^3$.
- **Kesimpulan Ilmiah:** **Tidak ditemukan bukti primer** dari penulis dataset yang mengonfirmasi bahwa nilai tersebut adalah $\text{mg/m}^3$. Rentang tabel ISPU Permen LHK 14/2020 adalah acuan regulasi kualitas udara, **bukan alasan sah untuk mengubah satuan dataset sumber**. Konflik satuan ini dicatat secara resmi sebagai **belum terselesaikan (*unresolved unit conflict*)**.

---

### B. Audit Kebocoran Data (*Data Leakage*) Model Aktif
- **Temuan Irisan Data:** Model aktif historis (`model_pm.h`) dilatih menggunakan `train_test_split(random_state=42)` dengan pengacakan acak (*random shuffle*) pada seluruh dataset 167.465 baris.
- **Hasil Pemeriksaan Irisan:** Ketika model aktif diuji terhadap 20% data akhir deret waktu kronologis ($N = 33.493$ baris), ditemukan bahwa sebanyak **26.689 baris (79,69%) dari data uji tersebut telah masuk ke dalam data latih model aktif**.
- **Kesimpulan Ilmiah:** Perbandingan model aktif dengan model kronologis baru adalah **tidak adil** karena model aktif mengalami kebocoran data deret waktu yang parah. Oleh karena itu, pengujian model aktif dipisahkan secara ketat hanya untuk keterlacakan riwayat (*traceability/archive*).

---

## 2. Hasil Evaluasi Setara PM2.5 (GP2Y)

Evaluasi bersih dijalankan dengan skrip independen yang dapat direproduksi: [Fase_1_Evaluasi_ML/evaluasi_setara_pm.py](../Fase_1_Evaluasi_ML/evaluasi_setara_pm.py) dan data metrik tersimpan di [Fase_1_Evaluasi_ML/tabel_evaluasi_setara_pm.csv](../Fase_1_Evaluasi_ML/tabel_evaluasi_setara_pm.csv).

Metode: Pembagian waktu murni (*chronological split*) tanpa kebocoran data (80% masa lalu untuk training, 20% masa depan untuk testing, $N_{\text{test}} = 33.493$).

### Tabel Metrik Evaluasi Bersih

| Skala Evaluasi | Model / Metode | RMSE | MAE | $R^2$ | Penurunan RMSE | Sifat Evaluasi |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Skala Numerik Sumber**<br>*(Konflik Satuan Belum Terselesaikan)* | Raw Input (Tanpa Koreksi) | 0.00315 | 0.00227 | -2.0439 | 0.0% | Baseline masukan terganggu formula simulasi |
| | Regresi Linear (3 Fitur) | 0.00663 | 0.00576 | -12.5063 | -110.6% | Gagal memodelkan komponen non-linear uap air |
| | **Random Forest Chrono** | **0.00021** | **0.00001** | **0.9860** | **+93.21%** | Latih 80% lalu, uji 20% depan; bebas data leakage |
| **Skala $\times 1000$**<br>*(Asumsi Pengali Legacy)* | Raw Input (Tanpa Koreksi) | 3.14592 | 2.26507 | -2.0439 | 0.0% | Baseline masukan terganggu formula simulasi |
| | Regresi Linear (3 Fitur) | 6.62671 | 5.75826 | -12.5063 | -110.6% | Gagal memodelkan komponen non-linear uap air |
| | **Random Forest Chrono** | **0.21310** | **0.01186** | **0.9860** | **+93.23%** | Latih 80% lalu, uji 20% depan; bebas data leakage |
| *(Uji Keterlacakan Riwayat)* | *RF Aktif Legacy (`model_pm.h`)* | *0.20727* | *0.00930* | *0.9868* | *+93.41%* | *Tercemar 79.69% data leakage dari random split* |

### Batasan Kesimpulan PM yang Diakui
> **Pernyataan Batasan Ilmiah:**  
> Evaluasi ini **hanya membuktikan bahwa Random Forest berhasil mengoreksi gangguan buatan sesuai formula simulasi matematis**. Hasil ini **TIDAK BOLEH** diklaim sebagai bukti bahwa sistem telah mengatasi pertumbuhan partikel debu akibat kelembapan (*hygroscopic aerosol growth*) pada sensor fisik Sharp GP2Y di lapangan, karena dataset Mendeley tidak menyediakan data pengukuran ADC fisik paralel dengan instrumen referensi partikulat independen.

---

## 3. Analisis Jalur Sensor MQ-7 (CO): Solusi Nyata vs Mempertahankan Kondisi Lama

Penggantian model CO berbasis data pasangan (*data-driven transfer*) **belum dapat dilakukan secara valid** karena tidak adanya dataset publik yang merekam sensor MQ-7 bersama instrumen analitik gas CO rujukan.

Berikut pemilahan transparan antara **mana yang sekadar mempertahankan kondisi lama** dan **mana yang menyelesaikan masalah**:

---

### A. Mempertahankan Kondisi Lama untuk Demonstrasi Sistem (Opsi Model Aktif `model_co.h`)

- **Deskripsi:** Tetap menjalankan model Random Forest aktif di firmware yang dilatih dari sensor PT08.S1 dataset UCI.
- **Karakteristik:**
  - **TIDAK menyelesaikan masalah ilmiah:** Ketidakcocokan mendasar antara sensor resistif PT08 (Italia) dan MQ-7 (Hanwei) tetap ada. Label "transfer nominal" tidak memperbaiki ketidakcocokan fisik-kimia ini.
  - **Fungsi Utama:** Hanya sebagai **demonstrasi sistem fungsional** untuk menguji ketahanan runtime ESP32, FreeRTOS, transmisi ThingSpeak STZ4, dan kendali PWM kipas secara terus-menerus.
  - **Status untuk Penelitian:** **BUKAN solusi kalibrasi dan BUKAN model final siap publikasi.** Jika opsi ini diambil untuk pengambilan data 168 jam, laporan penelitian wajib menyatakan bahwa angka CO yang dihasilkan adalah sinyal demonstrasi numerik, bukan estimasi konsentrasi gas tervalidasi.

---

### B. Opsi yang Menyelesaikan Masalah Secara Bertahap

#### **1. Opsi Transisi ke Formula Karakteristik Datasheet Hanwei MQ-7**
Menghapus model ML transfer PT08 dan menggantinya dengan formula log-resistansi standar semikonduktor SnO2:
$$\text{ppm} = \left(\frac{R_s / R_0}{A}\right)^{1/B}$$
dengan:
$$V_{\text{out}} = \text{ADC} \times \frac{3.3}{4095}, \quad R_s = R_L \times \left(\frac{V_c - V_{\text{out}}}{V_{\text{out}}}\right)$$

**Hasil Verifikasi Manual Datasheet & Rangkaian:**
1. **Definisi $R_0$:** Sesuai datasheet Hanwei MQ-7, $R_0$ adalah resistansi sensor pada konsentrasi **$100\,\text{ppm}$ CO di udara bersih pada suhu $20^\circ\text{C}$ dan kelembapan $65\%$ RH**. Di udara bersih tanpa gas CO, rasio resistansi tipikal adalah $\frac{R_s}{R_0} \approx 20 - 30$ (rata-rata $27.0$).
2. **Kebutuhan Siklus Pemanasan (Heater Cycle):**
   - Datasheet mensyaratkan pemanasan ganda berkala:
     - **Suhu Tinggi ($5.0\,\text{V} \pm 0.1\,\text{V}$ selama 60 detik):** Untuk pembersihan adsorpsi gas pengotor.
     - **Suhu Rendah ($1.4\,\text{V} \pm 0.1\,\text{V}$ selama 90 detik):** Suhu di mana CO bereaksi secara selektif. Pengambilan sampel ADC **wajib dilakukan pada detik-detik akhir siklus 1.4V**.
3. **Kendala Rangkaian Fisik Stuzha Saat Ini:**
   - Hardware Stuzha saat ini menyuplai heater MQ-7 dengan tegangan **5V statis terus-menerus** tanpa sirkuit switching PWM/transistor untuk menurunkan ke 1.4V. Menjalankan sensor pada 5V konstan menyebabkan selektivitas CO menurun drastis dan sensor merespons gas campuran lain secara kasar.
   - Nilai resistor beban fisik ($R_L$) pada modul belum diverifikasi dengan multimeter.
- **Kesimpulan Opsi Datasheet:** Menyelesaikan masalah ketergantungan model PT08, namun **membutuhkan modifikasi hardware (sirkuit heater switching 1.4V) dan pengukuran fisik $R_L$** agar rumus bekerja sesuai spesifikasi pabrik.

#### **2. Opsi Menggeser MQ-7 Menjadi Indikator Anomali Relatif (Baseline Tracking)**
- **Metode:** Menghapus konversi ke satuan konsentrasi ppm semu. Sistem mengukur deviasi relatif terhadap baseline udara ruangan:
  $$\Delta \text{ADC} = \text{ADC}_{\text{saat\_ini}} - \text{ADC}_{\text{baseline\_24jam}}$$
- **Dampak Ilmiah:** **Menyelesaikan masalah secara jujur tanpa modifikasi hardware.** Sistem tidak lagi berpura-pura mengukur ppm gas CO, melainkan berfungsi sebagai pendeteksi lonjakan gas pereduksi kualitatif.
- **Konsekuensi Sistem:** Sub-indeks ISPU utama didorong penuh oleh PM2.5, sedangkan lonjakan gas bertindak sebagai pemicu ventilasi (*override*) darurat.

---

## 4. Matriks Perbandingan Strategis untuk Pemilik & Mitra

| Parameter Evaluasi | Opsi 1: Pertahankan Model Aktif untuk Demonstrasi | Opsi 2: Transisi ke Formula Datasheet MQ-7 | Opsi 3: Indikator Anomali Relatif Gas |
| :--- | :--- | :--- | :--- |
| **Menyelesaikan Masalah Ilmiah?** | **TIDAK.** Hanya menjaga demonstrasi pipeline software. | **YA (pada teori semikonduktor),** tapi terhambat suplai heater 5V statis. | **YA.** Menghilangkan klaim ppm palsu secara jujur. |
| **Kesiapan Sesi 168 Jam Saat Ini** | **Langsung siap jalan** (fokus uji stabilitas runtime & IoT). | **Tertunda** (perlu ukur $R_L$, kalibrasi $R_0$, dan idealnya rangkaian 1.4V). | **Cukup penyesuaian firmware sederhana** (tanpa ubah hardware). |
| **Status Publikasi / Astra** | Dilaporkan sebagai *demonstrasi edge AI sistem tertanam*, bukan kalibrasi gas. | Dilaporkan sebagai *pendekatan nominal kurva pabrik dengan batasan heater konstan*. | Dilaporkan sebagai *monitoring partikulat kuantitatif + deteksi anomali gas kualitatif*. |
