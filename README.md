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

## 📐 Desain Fisik Purifier, Dimensi Kipas, & Orientasi Alat

Sistem Project Stuzha mengintegrasikan modul purifikasi udara aktif dengan desain mekanikal dan akustik yang disesuaikan untuk kenyamanan ruang tidur:

### 1. Spesifikasi Kipas & Saluran Udara (Duct Port)
* **Tipe Kipas:** *High-Speed Industrial Brushless DC (BLDC) Axial Fan*.
* **Spesifikasi Kelistrikan:** **12V DC, Arus 1.65A** (High-Power Server-Grade Motor).
* **Kecepatan Maksimum:** **~6.200 – 6.400 RPM**.
* **Dimensi Fisik Kipas:** **12 cm × 12 cm × 3.8 cm (120 mm × 120 mm × 38 mm)**.
* **Dimensi Lubang Saluran:** Lubang intake/exhaust dirancang berbentuk **kotak simetris 12 cm × 12 cm** presisi mengikuti dimensi luar penampang kipas. Desain rasio 1:1 ini bertujuan untuk:
  1. Mencegah penyempitan aliran (*airflow constriction*) dan menekan hambatan tekanan balik (*backpressure*).
  2. Meniadakan turbulensi udara pada sudut bodi box yang sering memicu resonansi bising.
  3. Memaksimalkan laju aliran udara volumetrik (*CFM / Clean Air Delivery Rate*) pada putaran rendah.

### 2. Orientasi Fisik: Wajib Posisi Berdiri (Vertical Standing)
Purifier dirancang untuk diletakkan dalam **posisi berdiri tegak (vertikal)**, bukan posisi tidur/horizontal. Hal ini didasari oleh tiga pertimbangan teknis krusial:
1. **Proteksi Optik Sensor Debu (Sharp GP2Y1010AU0F):** Posisi vertikal mencegah partikel debu gravitasi kasar mengendap dan melapisi lensa LED inframerah serta fototransistor optik. Posisi tidur akan membuat optik cepat berdebu dan memicu drift pembiasan permanen.
2. **Manajemen Termal Sensor Gas (Pencegahan Thermal Drift):** Sensor gas semikonduktor (MQ-7 dan MQ-135) memiliki koil pemanas internal (*heater coil*). Dalam posisi vertikal, panas konveksi alami bergerak lurus ke atas (*natural upward convection / chimney effect*) dan langsung terbuang, sehingga panasnya tidak terperangkap atau memanaskan sensor DHT22 (suhu/RH) dan optik PM2.5.
3. **Pola Sirkulasi Udara Kamar (*Chimney Effect*):** Udara kamar dihisap dari bukaan samping/bawah melewati filter HEPA & ruang sensor, lalu dihembuskan keluar secara aksial melalui exhaust fan atas, menghasilkan sirkulasi perputaran udara (*air changes per hour*) yang merata ke seluruh ruangan tidur.

### 3. Logika PWM Multi-Tier & Akustik (Kenyamanan Tidur)
Mengingat kipas 6.200 RPM memiliki daya dorong dan kebisingan sangat tinggi pada kecepatan penuh, firmware menerapkan kendali PWM berjenjang dengan deadband histeresis 5-poin:
* **Baik (ISPU ≤ 50):** 13% PWM (~806 RPM, < 22 dB) — *Ultra-Silent Standby*.
* **Sedang (ISPU 51–100):** 15% PWM (~930 RPM, < 28 dB) — *Silent Sleep Purify* (memenuhi baku mutu kebisingan tidur malam WHO/ASHRAE).
* **Tidak Sehat (ISPU 101–200):** 22% PWM (~1.364 RPM, < 38 dB) — *Active Clean* (pembersihan polutan aktif tanpa suara kasar).
* **Sangat Tidak Sehat (ISPU 201–300):** 50% PWM (~3.100 RPM) — *Heavy Purge*.
* **Berbahaya (ISPU > 300):** 85% PWM (~5.270 RPM) — *Max Emergency Purge* + Buzzer Alarm.

---

## 📂 Struktur Repositori

```text
Project Stuzha/
├── Download_Dataset_ThingSpeak.bat      # 1-Klik download dataset lengkap ThingSpeak (Windows)
├── Fase_1_Evaluasi_ML/                  # Artefak Fase 1: Evaluasi Machine Learning & Grafik
│   ├── grafik/                          # Gambar visualisasi ilmiah 300 DPI untuk paper
│   ├── laporan_evaluasi_metrik.md       # Laporan tabel metrik R², RMSE, MAE untuk paper
│   ├── tabel_metrik_evaluasi.csv        # Tabel metrik dalam format CSV
│   ├── run_fase1_evaluation.py          # Skrip eksekusi evaluasi & training model
│   └── README.md
├── Hardware/                            # Dokumentasi Fisik, Blueprint, Skematik & Foto Prototipe
│   ├── foto_alat/                       # Galeri foto prototipe fisik nyata (tampak samping, sensor, dll.)
│   ├── skematik/                        # Diagram rangkaian kelistrikan & wiring ESP32
│   ├── blueprint/                       # Desain mekanikal, dimensi bodi box, & duct kipas
│   └── README.md                        # Panduan teknis hardware & tata letak komponen
├── Program/
│   ├── download_thingspeak_dataset.py   # Skrip pengunduh otomatis IoT Cloud ke CSV (WIB)
│   ├── data/                            # Dataset Ground Truth, Benchmark, & Rekaman IoT
│   │   ├── Dataset_Project_Stuzha_ThingSpeak_Lengkap.csv # Rekaman live monitoring IoT
│   │   ├── mendeley/                    # Dataset GP2Y1010AU0F (Sonawani & Patil, 2022)
│   │   ├── uci/                         # Dataset MOS CO Reference Analyzer (UCI Repository)
│   │   └── README.md
│   └── Kode/                            # Firmware ESP32 (PlatformIO Framework)
│       ├── platformio.ini               # Konfigurasi PlatformIO & dependency library
│       ├── README.md                    # Dokumentasi lengkap pinout & API firmware
│       ├── include/
│       │   ├── model_pm.h               # Model TinyML Random Forest PM2.5 (Autogenerated C)
│       │   ├── model_co.h               # Model TinyML Random Forest CO (Autogenerated C)
│       │   ├── ispu_calc.h              # Rumus interpolasi linear ISPU Permen LHK 14/2020
│       │   └── pin_config.h             # Konfigurasi pin & PWM ESP32
│       ├── src/
│       │   └── main.cpp                 # Firmware utama: Sensor -> TinyML -> ISPU -> Kipas -> IoT
│       └── legacy/                      # Arsip kode lama purwarupa awal (rule-based)
│           └── kode_program_lama.cpp
├── ml_training/                         # Python Machine Learning (Scikit-Learn -> TinyML)
│   ├── explore_datasets.py              # Skrip eksplorasi statistik data
│   └── train_models.py                  # Skrip training Random Forest & C Header Exporter
├── MD/
│   ├── konteks _planing_jurnal_AQI.md  # Catatan lengkap arsitektur, rumus, & roadmap jurnal
│   └── roadmap_dan_langkah_selanjutnya.md # Panduan aksi kolaborasi tim: Fase 2 (Uji Hardware) & Fase 3 (Paper)
├── referensi/                           # Koleksi referensi paper, standar ISPU, dan metadata jurnal
│   └── referensi garnie/
└── README.md
```

---

## 🧭 Roadmap & Tahap Selanjutnya

Untuk detail panduan pengujian dan rencana penulisan artikel jurnal ilmiah, silakan merujuk ke dokumen:  
👉 **[MD/roadmap_dan_langkah_selanjutnya.md](MD/roadmap_dan_langkah_selanjutnya.md)**

* **Fase 1 (Selesai):** Kalibrasi Machine Learning, evaluasi metrik ($R^2$, RMSE, MAE), grafik 300 DPI, dan ekspor C Header.
* **Fase 2 (Berikutnya):** Uji komputasi TinyML di ESP32-S3, uji respons kipas adaptif PWM, dan validasi fisik polutan ruangan.
* **Fase 3 (Target Akhir):** Penyusunan draf naskah artikel jurnal ilmiah (Target Sinta 3 / Sinta 2).

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
- [@Riq-Z](https://github.com/Riq-Z)
