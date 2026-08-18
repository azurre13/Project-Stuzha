# Project Stuzha 🌬️

> **Sistem Pemantauan Kualitas Udara Indoor Terkalibrasi Machine Learning (Random Forest) Berstandar ISPU**

Repositori ini berisi dokumentasi perencanaan (*planning*), arsitektur sistem, referensi jurnal/standar regulasi, serta basis pengembangan kode untuk riset jurnal peningkatan kualitas udara indoor.

---

## 📌 Ringkasan Proyek

Proyek ini merupakan peningkatan (*upgrade*) dari sistem pemantauan dan filtrasi udara sebelumnya:
1. **Sensor Gas CO:** Menggunakan **MQ-7** (upgrade dari MQ-2 untuk akurasi spesifik CO ambient).
2. **Sensor Partikulat:** **GP2Y1010AU0F** (input kalibrasi PM).
3. **Sensor Koreksi Lingkungan:** **DHT22** (suhu & kelembapan relatif sebagai variabel koreksi drift).
4. **Algoritma Kalibrasi:** **Machine Learning (Random Forest Regression)** untuk mengoreksi pembacaan sensor murah (*sensor fusion*).
5. **Standarisasi Output:** Perhitungan sub-indeks & penentuan Parameter Pencemar Kritis menggunakan standar resmi **ISPU (Peraturan Menteri LHK No. 14 Tahun 2020)** dengan metode *Piecewise Linear Interpolation*.
6. **Edge Device & Aksi:** **ESP32-S3** untuk *edge inference*, pengatur kecepatan kipas dinamis (*adaptive filtration*), air purifier terintegrasi, dan pemantauan IoT real-time.

---

## 📂 Struktur Repositori

```text
Project Stuzha/
├── MD/
│   └── konteks _planing_jurnal_AQI.md   # Catatan lengkap arsitektur, rumus matematis, & roadmap jurnal
├── referensi/                           # Koleksi referensi paper, standar ISPU, dan jurnal sebelumnya
│   ├── (Jurnal lama kita) Sistem Pemantauan dan Filtrasi Udara.pdf
│   ├── AQ kasifikasi random forest mq7 & mq135.pdf
│   ├── Applying machine learning for large scale field calibration of low cost PM2.5 and PM10.pdf
│   ├── Permen_LHK_Nomor_14_Tahun_2020.pdf
│   └── sensors-21-00256.pdf
└── README.md
```

---

## 🔄 Alur Pemrosesan Data

```text
[ Raw ADC / Voltage: GP2Y1010, MQ-7 + Suhu & Kelembapan: DHT22 ]
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Tahap 1: Kalibrasi ML (Random Forest Regression)            │
│  Output: Konsentrasi terkalibrasi (PM: µg/m³, CO: ppm)       │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Tahap 2: Piecewise Linear Interpolation (Breakpoint ISPU)   │
│  Output: Sub-Indeks seragam per polutan                      │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Tahap 3: Penentuan Parameter Kritis — MAX(Sub-Indeks)       │
│  Output: Nilai AQI Final + Kategori ISPU + Parameter Dominan │
└──────────────────────────────────────────────────────────────┘
                            ↓
    [ Kontrol Kecepatan Kipas & Purifier + Dashboard IoT ]
```

---

## 👥 Kolaborator
- [@azurre13](https://github.com/azurre13)
- [@Garnie104](https://github.com/Garnie104)

