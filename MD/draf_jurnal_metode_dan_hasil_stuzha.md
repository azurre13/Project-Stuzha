# Draf Artikel Ilmiah: Implementasi dan Evaluasi Operasional Prototipe Monitoring Kualitas Udara Indoor Multi-Polutan Berbasis TinyML Random Forest dan Regulasi Permen LHK No. 14 Tahun 2020 pada ESP32

**Format Naskah:** Template Standar Naskah Jurnal Nasional Terakreditasi (SINTA 2 / SINTA 3)  
**Bidang Fokus:** *Embedded Systems*, *Edge Machine Learning*, *Internet of Things (IoT)*, *Indoor Air Quality Monitoring*.

---

## JUDUL / TITLE

**Implementasi dan Evaluasi Operasional 7 Hari Prototipe Monitoring Kualitas Udara Indoor Multi-Polutan Berbasis TinyML Random Forest dan Regulasi Permen LHK 14/2020 pada ESP32**

*Implementation and 7-Day Operational Evaluation of a TinyML Random Forest-Based Multi-Pollutant Indoor Air Quality Monitoring Prototype with Permen LHK 14/2020 Regulation on ESP32*

---

## ABSTRAK (INDONESIAN)

Pemantauan kualitas udara dalam ruangan (*Indoor Air Quality* / IAQ) multi-polutan umumnya terkendala oleh mahalnya instrumen pembanding kelas referensi serta keterbatasan mikrokontroler berdaya rendah dalam menjalankan inferensi cerdas dan penentuan indeks regulasi secara otonom di sisi *edge*. Penelitian ini merancang, mengimplementasikan, dan mengevaluasi prototipe pemantau IAQ berbasis mikrokontroler ESP32 yang mengintegrasikan sensor berbiaya rendah (Sharp GP2Y1010AU0F, MQ-7, MQ-135, dan DHT22) dengan komputasi *Tiny Machine Learning* (TinyML) *Random Forest* C++ statis dan formulasi interpolasi sub-indeks kontinu Peraturan Menteri Lingkungan Hidup dan Kehutanan (Permen LHK) No. 14 Tahun 2020. Sistem mengeksekusi inferensi lokal untuk partikulat ($\text{PM}_{2.5}$) dan karbon monoksida ($\text{CO}$), menentukan parameter kritis melalui fungsi $\max(\text{Sub\_PM}, \text{Sub\_CO})$, serta menghasilkan sinyal kendali kecepatan kipas (*commanded PWM*) yang diatur oleh histeresis bertingkat (*smooth decay*). Pengujian operasional kontinu selama 7 hari (10–17 September 2026, total durasi kalender 170,535 jam) di lingkungan kamar tidur hunian nyata menghasilkan 30.260 rekaman telemetri awan yang terdistribusi ke dalam 5 sesi booting. Parameter lingkungan teramati mencatat rentang suhu 22,20°C–31,50°C (rerata 26,02°C), kelembaban relatif 39,50%–75,50% (rerata 55,64%), estimasi nominal $\text{PM}_{2.5}$ 20,46–80,25 $\mu\text{g/m}^3$ (rerata 34,42 $\mu\text{g/m}^3$), estimasi nominal $\text{CO}$ 2,68–7,44 ppm (rerata 4,13 ppm), dan sub-indeks ISPU instan 56,22–126,16 (rerata 74,44). Distribusi mutu udara didominasi Kategori Sedang sebesar 99,405% (30.080 sampel), Kategori Tidak Sehat 0,592% (179 sampel), dan anomali saturasi sensor optik Kategori 0 sebesar 0,003% (1 sampel). Secara kumulatif 7 hari, sistem membukukan kelengkapan slot telemetri 98,59% (30.260 feed dari 30.692 slot) dan tingkat keberhasilan percobaan transmisi 98,90% (30.259 sukses dari 30.596 percobaan kirim; 337 kegagalan jaringan dan 101 slot tidak dicoba saat Wi-Fi belum siap). Kestabilan memori *heap* RAM teramati berfluktuasi stabil pada 196.728–201.372 bytes dengan deviasi standar 100,64 bytes tanpa tren degradasi progresif. Sesi operasional kontinu tunggal terpanjang berjalan selama 151,26 jam non-stop (27.022 sampel, Boot `f27413f0`) dengan deviasi standar *heap* 86,41 bytes, kelengkapan slot 99,25%, dan keberhasilan transmisi 99,57%. Empat transisi restart terdokumentasi antar-sesi dengan jeda waktu 22,0 hingga 51,0 detik (tiga kali kode register reset 1 / *power-on* dan satu kali kode 7 / *task watchdog timer*); penyebab fisik eksternal di balik restart tidak dapat dipastikan secara definitif karena ketiadaan instrumentasi pencatat daya/tegangan independen. Perintah kecepatan kipas dibangkitkan pada Level 2 (PWM 14,90%) sebesar 99,253% dan Level 3 (PWM 21,96%) sebesar 0,740%, namun status fisik putaran motor tidak diukur secara mekanis dan penelitian ini tidak mengevaluasi laju pembersihan udara (*clean air delivery rate* / CADR). Model inferensi beroperasi pada skala transfer nominal tanpa klaim akurasi metrologis terverifikasi karena belum diuji terhadap instrumen acuan bersertifikat. Pada anomali saturasi sensor optik GP2Y (ADC 4095 pada 13 September 02:13:06 WIB), cabang *fallback* proteksi firmware terprogram teramati mengeksekusi penetapan Kategori 0, ISPU NaN, dan perintah darurat Level 5 (PWM 85,10%) disusul peluruhan bertahap (*smooth decay*) ke Level 4 (PWM 50,20%) dan Level 2 (PWM 14,90%).

**Kata Kunci:** *TinyML, Random Forest, ESP32, Permen LHK 14/2020, Indeks Standar Pencemar Udara (ISPU), Kualitas Udara Indoor, Sensor Berbiaya Rendah.*

---

## ABSTRACT (ENGLISH)

*Comprehensive indoor air quality (IAQ) monitoring is often hindered by the high cost of reference-grade instruments and the limited capacity of low-power microcontrollers to autonomously perform intelligent multi-pollutant inference and regulatory index determination at the edge. This study designs, implements, and evaluates an ESP32-based IAQ monitoring prototype that integrates low-cost sensors (Sharp GP2Y1010AU0F, MQ-7, MQ-135, and DHT22) with static C++ Tiny Machine Learning (TinyML) Random Forest regression and continuous sub-index interpolation based on Indonesian Ministry of Environment and Forestry Regulation (Permen LHK) No. 14/2020. The system executes deterministic on-device inference for particulate matter ($\text{PM}_{2.5}$) and carbon monoxide ($\text{CO}$), identifies the critical parameter via $\max(\text{Sub\_PM}, \text{Sub\_CO})$, and generates fan speed commands (commanded PWM) governed by multi-level hysteresis and smooth decay. A 7-day continuous operational test (September 10–17, 2026; 170.535 total calendar hours) in a domestic bedroom environment yielded 30,260 cloud telemetry records across 5 boot sessions. Observed environmental parameters recorded temperatures of 22.20°C–31.50°C (mean 26.02°C), relative humidity of 39.50%–75.50% (mean 55.64%), nominal $\text{PM}_{2.5}$ estimates of 20.46–80.25 $\mu\text{g/m}^3$ (mean 34.42 $\mu\text{g/m}^3$), nominal $\text{CO}$ estimates of 2.68–7.44 ppm (mean 4.13 ppm), and instantaneous ISPU index of 56.22–126.16 (mean 74.44). Air quality classification was dominated by Moderate Category at 99.405% (30,080 samples), Unhealthy Category at 0.592% (179 samples), and sensor saturation anomaly Category 0 at 0.003% (1 sample). Cumulatively over the 7-day run, the system achieved 98.59% slot completeness (30,260 feeds out of 30,692 slots) and a 98.90% transmission attempt success rate (30,259 successful deliveries out of 30,596 attempts, 337 network failures, and 101 unattempted slots during Wi-Fi reconnections). Observed heap memory remained stable within 196,728–201,372 bytes with a standard deviation of 100.64 bytes without progressive degradation. The longest uninterrupted continuous session ran for 151.26 hours (27,022 samples, Boot `f27413f0`) with a heap standard deviation of 86.41 bytes, 99.25% slot completeness, and a 99.57% attempt success rate. Four restart transitions were documented between sessions with time gaps of 22.0 to 51.0 seconds (three power-on reset codes and one task watchdog timer reset); the underlying physical root causes of these restarts cannot be definitively asserted due to the absence of independent external power logging instrumentation. Fan speed commands were generated at Level 2 (PWM 14.90%) for 99.253% and Level 3 (PWM 21.96%) for 0.740%, but physical motor rotation was not mechanically instrumented and this study does not evaluate clean air delivery rate (CADR). The inference models operated as nominal transfer estimators without certified metrological accuracy claims. During an optical sensor saturation anomaly (GP2Y ADC 4095 on September 13, 02:13:06 WIB), the programmed firmware fallback rules deterministically assigned Category 0, set ISPU to NaN, commanded emergency Level 5 (PWM 85.10%), and smoothly decayed through Level 4 (PWM 50.20%) to Level 2 (PWM 14.90%).*

**Keywords:** *TinyML, Random Forest, ESP32, Permen LHK 14/2020, Air Quality Index (ISPU), Indoor Air Quality, Low-Cost Sensors, Edge Computing.*

---

## 1. PENDAHULUAN

Kualitas udara dalam ruangan (*Indoor Air Quality* / IAQ) memiliki dampak langsung terhadap kesehatan pernapasan dan kesejahteraan manusia mengingat sebagian besar populasi perkotaan menghabiskan 80% hingga 90% aktivitas hariannya di lingkungan hunian tertutup [1]. Partikulat halus berdiameter $\le 2{,}5\,\mu\text{m}$ ($\text{PM}_{2.5}$) dan gas karbon monoksida ($\text{CO}$) merupakan polutan utama yang menjadi perhatian serius karena dampak toksikologisnya terhadap sistem kardiopulmoner [2]. Di Indonesia, acuan pelaporan mutu udara resmi diatur melalui Indeks Standar Pencemar Udara (ISPU) berdasarkan Peraturan Menteri Lingkungan Hidup dan Kehutanan (Permen LHK) No. 14 Tahun 2020 [3]. Regulasi ini membagi mutu udara ke dalam lima kategori: Baik (0–50), Sedang (51–100), Tidak Sehat (101–200), Sangat Tidak Sehat (201–300), dan Berbahaya (>300).

Meskipun instrumen pemantau profesional (*reference-grade instruments*) menyajikan akurasi konsentrasi teruji, biaya pengadaan yang tinggi, prosedur pemeliharaan rumit, dan ukuran fisik masif membatasi penerapannya pada lingkungan hunian domestik [4]. Sebagai alternatif, sensor berbiaya rendah (*low-cost sensors*) seperti modul sensor debu hamburan optik (GP2Y1010AU0F) dan sensor gas semikonduktor oksida logam / MOX (MQ-7, MQ-135) banyak dimanfaatkan [5]. Kendati demikian, sensor murah memiliki karakteristik non-linear, derau lingkungan, serta sensitivitas silang (*cross-sensitivity*) terhadap fluktuasi suhu dan kelembaban relatif (*RH*) [6].

Penerapan *Machine Learning* (ML) terbukti mampu memodelkan relasi non-linear respon sensor berbiaya rendah [7]. Namun, mayoritas sistem pemantau yang ada saat ini mengadopsi arsitektur terpusat di awan (*cloud-centric*), di mana data mentah dikirim ke peladen (*server*) untuk diproses [8]. Arsitektur ini rentan terhadap latensi jaringan, konsumsi *bandwidth*, serta kegagalan sistem kendali aktuator apabila koneksi internet terputus [9].

Perkembangan *Tiny Machine Learning* (TinyML) memungkinkan model inferensi cerdas dieksekusi langsung pada perangkat mikrokontroler berdaya rendah di sisi *edge* (*on-device inference*) [10]. Model berbasis pohon keputusan (*Random Forest*) memiliki keunggulan praktis untuk sistem tertanam karena operasinya tersusun atas percabangan logika linier (*if-else*) yang tidak menuntut operasi komputasi matriks berat atau pustaka runtime eksternal yang membebani memori statis [11].

Penelitian ini merancang, mengimplementasikan, dan mengevaluasi prototipe monitoring kualitas udara terpadu berbasis mikrokontroler ESP32 dengan nama Project Stuzha. Kontribusi penelitian ini difokuskan pada:
1. **Inferensi Multi-Polutan On-Device:** Implementasi dual-model *Random Forest* C++ statis untuk estimasi nominal $\text{PM}_{2.5}$ dan $\text{CO}$ langsung pada memori mikrokontroler dengan latensi deterministik.
2. **Standardisasi Regulasi Kontinu:** Integrasi algoritma interpolasi kontinu Permen LHK 14/2020 dan pemilihan parameter kritis $\max(\text{Sub\_PM}, \text{Sub\_CO})$ untuk membangkitkan perintah kecepatan kipas hisap (*commanded PWM*).
3. **Evaluasi Empiris 7 Hari di Lingkungan Nyata:** Pengujian operasional kontinu selama 170,535 jam kalender di kamar tidur hunian nyata dengan pemisahan sesi booting faktual, evaluasi kestabilan memori *heap*, rekonsiliasi slot telemetri, dan analisis empiris penanganan sesar saturasi optik.

---

## 2. METODOLOGI PENELITIAN

### 2.1 Desain Perangkat Keras dan Tata Letak Fisik

Prototipe Stuzha dibangun menggunakan casing gabus padat dengan konfigurasi aliran udara vertikal dari bawah ke atas:
- **Intake Bawah dan Bilik Sensor:** Udara masuk melalui celah bukaan bawah. Seluruh modul sensor diletakkan di bilik intake **sebelum** media filter. Sensor partikulat Sharp GP2Y1010AU0F diposisikan horizontal, sensor gas MQ-7 dan MQ-135 dipasang vertikal pada dinding bilik, dan sensor suhu/kelembaban DHT22 ditempatkan berdampingan.
- **Media Filter Pendukung:** Terdiri dari filter karbon aktif kotak dan potongan media filter serat sintetis otomotif (non-HEPA), dipisahkan oleh ruang celah aliran $\approx 5\text{ cm}$ sebelum kipas.
- **Exhaust dan Kipas:** Kipas aksial 12V ($12 \times 12\text{ cm}$) dipasang di bagian paling atas untuk menarik udara keluar (*exhaust*).

```text
       [ EXHAUST ATAS ]
              ↑
       [ KIPAS 12 × 12 cm ]  <-- Dikendalikan PWM (GPIO 19)
              ↑
       [ CELAH UDARA ~5 cm ]
              ↑
       [ FILTER SINTETIS & KARBON KOTAK ]
              ↑
   [ BILIK SENSOR INTAKE BAWAH ]  <-- GP2Y, MQ-7, MQ-135, DHT22
              ↑
       [ INTAKE UDARA BAWAH ]
```

Pemetaan pin mikrokontroler ESP32 Dev Module (Espressif32 6.12.0 / Arduino-ESP32 2.0.17) dikonfigurasi sebagai berikut:
- `GPIO 34` (ADC1_CH6): Pembacaan tegangan analog sensor debu GP2Y ($V_o$).
- `GPIO 5`: Pemicu pulsa ILED GP2Y (periode sampling $10\text{ ms} / 100\text{ Hz}$, pulsa aktif LOW $320\,\mu\text{s}$, sampling ADC pada mikrodetik ke-280).
- `GPIO 32` (ADC1_CH4): Pembacaan analog sensor gas MQ-7 (12-bit ADC, attenuasi 12 dB).
- `GPIO 33` (ADC1_CH5): Pembacaan analog sensor MQ-135 sebagai proksi gas campuran/VOC.
- `GPIO 4`: Komunikasi data digital sensor DHT22 (dibaca setiap 2 detik).
- `GPIO 19`: Sinyal kendali kecepatan kipas melalui modulasi lebar pulsa (*PWM*) kanal LEDC 0 (frekuensi 25 kHz, resolusi 8-bit, rentang duty cycle 0–255).
- `GPIO 18`: Sinyal kendali buzzer piezoelektrik melalui kanal LEDC 15 (frekuensi 1.000 Hz, resolusi 10-bit).

### 2.2 Arsitektur TinyML Edge Inference

Inferensi kecerdasan buatan diimplementasikan dalam bentuk kode C++ statis (*header files* `model_pm.h` dan `model_co.h`) yang dieksekusi langsung pada CPU Xtensa LX6 dual-core 240 MHz:
1. **Model PM2.5 (`model_pm.h`):** Menerima 3 fitur masukan: normalisasi tegangan GP2Y, suhu (°C), dan kelembaban relatif (% RH). Model menghasilkan estimasi konsentrasi nominal $\text{PM}_{2.5}$ dalam satuan $\mu\text{g/m}^3$.
2. **Model CO (`model_co.h`):** Menerima 3 fitur masukan: nilai ADC mentah MQ-7 (0–4095), suhu (°C), dan kelembaban relatif (% RH). Model menghasilkan estimasi konsentrasi nominal $\text{CO}$ dalam satuan $\text{mg/m}^3$.

Sesuai konversi kondisi referensi standar ($25^\circ\text{C}, 101325\text{ Pa}$, berat molekul CO $28{,}01\text{ g/mol}$), estimasi konsentrasi CO dalam satuan ppm untuk pelaporan visual dihitung melalui:
$$\text{CO (ppm)} = \frac{\text{CO (mg/m}^3\text{)}}{1{,}145}$$
Sedangkan untuk perhitungan sub-indeks ISPU, konsentrasi CO dikalikan 1.000 menjadi satuan $\mu\text{g/m}^3$.

Kedua model diposisikan secara transparan sebagai **estimator nominal transfer eksperimental**, bukan instrumen yang telah terkalibrasi laboratorium absolut.

### 2.3 Perhitungan Sub-Indeks ISPU dan Logika Kendali Histeresis

Penentuan indeks mengimplementasikan fungsi interpolasi linier kontinu sesuai Lampiran I Permen LHK No. 14 Tahun 2020. Titik koordinat acuan konsentrasi batas bawah ($X_a$), konsentrasi batas atas ($X_b$), indeks batas bawah ($I_a$), dan indeks batas atas ($I_b$) didefinisikan pada Tabel 1.

**Tabel 1.** Titik Batas Regulasi ISPU Permen LHK No. 14 Tahun 2020
| Kategori Kualitas Udara | Rentang Indeks ($I$) | Batas $\text{PM}_{2.5}$ ($\mu\text{g/m}^3$) | Batas $\text{CO}$ ($\mu\text{g/m}^3$) |
|---|:---:|:---:|:---:|
| Baik | 0 – 50 | 0 – 15,5 | 0 – 4.000 |
| Sedang | 51 – 100 | 15,6 – 55,4 | 4.001 – 8.000 |
| Tidak Sehat | 101 – 200 | 55,5 – 150,4 | 8.001 – 15.000 |
| Sangat Tidak Sehat | 201 – 300 | 150,5 – 250,4 | 15.001 – 30.000 |
| Berbahaya | 301 – 500 | 250,5 – 500,0 | 30.001 – 45.000 |

Sub-indeks dihitung menggunakan formula interpolasi linier:
$$I_p = \frac{I_b - I_a}{X_b - X_a}(X - X_a) + I_a$$
Indeks komposit instan ditentukan oleh nilai maksimum parameter kritis:
$$I_{\text{instan}} = \max(I_{\text{PM2.5}}, I_{\text{CO}})$$

Perintah kecepatan kipas hisap (*commanded PWM*) dipetakan ke dalam 5 tingkatan level:
- **Level 1 (Baik):** PWM 12,94% (duty cycle 33/255)
- **Level 2 (Sedang):** PWM 14,90% (duty cycle 38/255)
- **Level 3 (Tidak Sehat):** PWM 21,96% (duty cycle 56/255)
- **Level 4 (Sangat Tidak Sehat):** PWM 50,20% (duty cycle 128/255)
- **Level 5 (Berbahaya / Darurat Sesar):** PWM 85,10% (duty cycle 217/255)

Untuk mencegah osilasi aktuator akibat derau sesaat (*chattering*), algoritma menerapkan:
1. **Jendela Konfirmasi Kenaikan:** Kategori baru harus bertahan stabil $\ge 1\text{ detik}$ sebelum level kipas dinaikkan.
2. **Histeresis Penurunan:** Level kipas hanya boleh turun jika indeks berada $< 95\%$ dari ambang batas level tersebut.
3. **Penundaan Turun Bertahap (*Smooth Decay*):** Penurunan kecepatan dibatasi maksimum 1 tingkat setiap 8 detik (*dwell time* 8 detik per level).

### 2.4 Protokol Pengujian Lapangan dan Keterbatasan Pengamatan

Pengujian dilakukan di kamar tidur domestik selama 7 hari kalender penuh (10–17 September 2026). Sesuai integritas metodologi ilmiah, batasan operasional lapangan dicatat:
1. **Status Fisik Motor Kipas:** Untuk menjaga kenyamanan tidur penghuni (*acoustic comfort*), konektor daya motor kipas 12V sebagian besar dilepas/dicabut pada malam hari. Mikrokontroler ESP32 tetap membangkitkan sinyal kontrol PWM pada GPIO 19 secara kontinu tanpa gangguan. Oleh karena itu, data kecepatan kipas dilaporkan secara ketat sebagai **perintah kontrol algoritma (*commanded PWM*)**, bukan kecepatan fisik mekanis aktual (*RPM putaran*). Penelitian ini tidak mengevaluasi laju pengiriman udara bersih (*CADR*) atau efisiensi pembersihan partikulat.
2. **Dinamika Suhu Ruangan dan Penyejuk Udara (AC):** Kamar tidur dilengkapi unit AC mandiri. Variasi suhu ruangan (22,20°C–31,50°C) berkorelasi dengan catatan logbook aktivitas pemilik: suhu naik saat penghuni bepergian keluar kamar dengan AC dimatikan, dan suhu stabil rendah (22°C–25°C) saat penghuni berada di kamar dengan AC menyala. Mengingat suhu dan kelembaban merupakan fitur input model TinyML, korelasinya dengan estimasi model dipahami sebagai interaksi fitur komputasi, bukan pembuktian kompensasi *drift* fisik sensor.

---

## 3. HASIL DAN PEMBAHASAN

### 3.1 Ringkasan Observasi dan Pemisahan Sesi Booting

Selama periode 10 September 2026 pukul 20:01:51 WIB hingga 17 September 2026 pukul 22:33:57 WIB (total durasi kalender 170,535 jam), sistem mengakumulasi **30.260 baris telemetri awan** pada Thingspeak Channel 3480764. Seluruh baris data menggunakan firmware aktif v4.0.0 (hash sumber `a945ea070fcc` dan hash model `d7f32c60`).

Berdasarkan stempel waktu dan kode register reset mikrokontroler (`r`) pada field status STZ4, data terdistribusi ke dalam 5 sesi booting yang dirinci pada Tabel 2.

**Tabel 2.** Rincian Sesi Booting dan Rekonsiliasi Transisi Restart 7 Hari
| No | Boot ID | Baris | Waktu Mulai (WIB) | Waktu Selesai (WIB) | Uptime Tercatat | Kode Reset (`r`) | Data Teramati pada Transisi |
|:--:|---|---:|---|---|---:|:---:|---|
| 1 | `c43d4d72` | 13 | 10 Sep 20:01:51 | 10 Sep 20:05:51 | 0,033 – 0,100 jam | 1 (`ESP_RST_POWERON`) | Sesi awal observasi pasca-booting pertama (durasi 0,10 jam). |
| — | *Transisi 1* | — | 10 Sep 20:05:51 | 10 Sep 20:06:28 | Jeda: 37,0 detik | — | Jeda waktu 37,0 detik; register reset Boot 2 mencatat `r=1` (`POWERON`). |
| **2** | `f27413f0` | **27.022** | **10 Sep 20:06:28** | **17 Sep 03:21:46** | **0,005 – 151,259 jam** | **1 (`ESP_RST_POWERON`)** | **Sesi operasional kontinu terpanjang (151,26 jam non-stop).** |
| — | *Transisi 2* | — | 17 Sep 03:21:46 | 17 Sep 03:22:08 | Jeda: 22,0 detik | — | Jeda waktu 22,0 detik; register reset Boot 3 mencatat `r=1` (`POWERON`). |
| 3 | `2ee94f8f` | 2.842 | 17 Sep 03:22:08 | 17 Sep 20:21:25 | 0,005 – 16,993 jam | 1 (`ESP_RST_POWERON`) | Sesi operasional kontinu selama 16,99 jam. |
| — | *Transisi 3* | — | 17 Sep 20:21:25 | 17 Sep 20:22:00 | Jeda: 35,0 detik | — | Jeda waktu 35,0 detik; register reset Boot 4 mencatat `r=7` (`TG0WDT_SYS`). |
| 4 | `9f05ffe4` | 18 | 17 Sep 20:22:00 | 17 Sep 20:27:41 | 0,005 – 0,100 jam | 7 (`ESP_RST_TG0WDT_SYS`) | Sesi transien singkat 18 sampel pasca-reset watchdog. |
| — | *Transisi 4* | — | 17 Sep 20:27:41 | 17 Sep 20:28:32 | Jeda: 51,0 detik | — | Jeda waktu 51,0 detik; register reset Boot 5 mencatat `r=1` (`POWERON`). |
| 5 | `37cbdc54` | 365 | 17 Sep 20:28:32 | 17 Sep 22:33:57 | 0,005 – 2,095 jam | 1 (`ESP_RST_POWERON`) | Sesi penutupan observasi hingga akhir hari ke-7. |
| **Total** | **5 Sesi** | **30.260** | **10 Sep 20:01:51** | **17 Sep 22:33:57** | **170,535 jam** | — | **Ambang batas 168 jam terpenuhi secara akumulatif.** |

**Pemisahan Sesi Booting dan Integritas Analisis Restart:**  
Data telemetri menunjukkan bahwa periode 170,535 jam kalender terbagi ke dalam 5 sesi booting oleh 4 transisi restart dengan jeda waktu antara 22,0 hingga 51,0 detik. Sesuai prinsip kehati-hatian metodologis (*scientific rigor*), **penyebab fisik di balik kejadian restart tidak dapat dipastikan secara definitif**:
1. Tiga transisi restart menghasilkan kode register hardware `r=1` (`ESP_RST_POWERON`). Register ini mencatat terjadinya peristiwa *power-on reset* pada sirkuit mikrokontroler ESP32. Namun, data telemetri jarak jauh tidak dapat membuktikan secara empiris apakah peristiwa tersebut dipicu oleh penurunan tegangan jala-jala listrik (*voltage dip / sag*), gangguan transien suplai daya, atau pelepasan konektor adaptor secara fisik. Prototipe ini beroperasi di kamar tidur hunian domestik tanpa instrumentasi pemantau tegangan eksternal independen (*external power logger / dedicated oscilloscope trap*), sehingga spekulasi kausalitas fisik dihindari sepenuhnya.
2. Satu transisi restart (Transisi 3 menuju Boot 4) mencatat kode register `r=7` (`ESP_RST_TG0WDT_SYS`). Kode ini merefleksikan reset akibat batas waktu *Task Watchdog Timer Group 0* mikrokontroler terlampaui, yang mengindikasikan bahwa perulangan program utama tidak sempat me-reset pewaktu pengawas (*pet the watchdog*) dalam batas waktu yang ditentukan. Kendati pola ini umumnya berkorelasi dengan pemblokiran saat menunggu latensi jaringan nirkabel atau I/O periferik, *stack backtrace* atau rekaman *core dump* spesifik tidak tersimpan pada telemetri awan, sehingga rute eksekusi perangkat lunak penyebabnya tidak dapat dipastikan secara definitif.
3. Oleh karena itu, evaluasi sistem disajikan secara transparan pada dua lingkup analisis: (a) pengujian ketahanan kontinu non-stop terpanjang pada sesi utama Boot `f27413f0` (151,26 jam berturut-turut tanpa interupsi), dan (b) evaluasi kumulatif keseluruhan 7 hari kalender (170,535 jam) yang merangkum seluruh 30.260 rekaman.

### 3.2 Kestabilan Memori dan Rekonsiliasi Telemetri

Kestabilan alokasi memori RAM dievaluasi melalui pembacaan fungsi sistem `esp_get_free_heap_size()` yang dicatat pada field status telemetri `k`:
- **Pada Keseluruhan 7 Hari (Hasil Kumulatif 30.260 Sampel):** Nilai heap minimum tercatat sebesar 196.728 bytes, maksimum 201.372 bytes, nilai rata-rata 199.148,93 bytes, dan deviasi standar sebesar **100,64 bytes**. Ketiadaan tren penurunan progresif (*monotonic downward trend*) sepanjang 170,535 jam membuktikan stabilitas alokasi memori statis array ring buffer dan fungsi inferensi C++ tanpa kebocoran memori dinamis (*memory leak*).
- **Pada Sesi Kontinu Utama (`f27413f0`, 27.022 Sampel / 151,26 Jam):** Sisa memori RAM statis tercatat sebesar 201.348 bytes pada inisialisasi awal dan 199.132 bytes pada jam ke-151, dengan nilai minimum 196.728 bytes, rata-rata 199.145,39 bytes, dan deviasi standar sebesar **86,41 bytes**.

Rekonsiliasi telemetri disajikan pada dua lingkup analisis:
1. **Pada Keseluruhan 7 Hari (Hasil Kumulatif 30.260 Sampel):** Total rentang slot terbentang dari kelima sesi booting adalah 30.692 slot. Dengan 30.260 rekaman feed yang berhasil diterima di server Thingspeak, sistem membukukan **kelengkapan slot (*slot completeness*) kumulatif sebesar 98,59%**. Total percobaan pengiriman tercatat sebanyak 30.596 kali dengan 337 kali kegagalan jaringan (**tingkat keberhasilan percobaan pengiriman kumulatif sebesar 98,90%**), serta 101 slot berstatus *skipped* saat mikrokontroler mendeteksi status Wi-Fi belum siap pada interval pengiriman 20 detik tanpa antrean persisten ($30.596 + 101 \approx 30.692\text{ slot}$).
2. **Pada Sesi Kontinu Utama (`f27413f0`, 27.022 Sampel):** Rentang slot terbentang adalah 27.226 slot dan feed diterima sebanyak 27.022 baris, menghasilkan **kelengkapan slot sebesar 99,25%**. Tercatat 27.135 percobaan pengiriman dengan 118 kali kegagalan jaringan, menghasilkan **tingkat keberhasilan percobaan pengiriman sebesar 99,57%**, serta 91 slot berstatus *skipped* ($27.135 + 91 = \mathbf{27.226\text{ slot}}$).

### 3.3 Karakteristik Statistik Lingkungan dan Dinamika Multi-Polutan

Rangkuman statistik parameter sensor dan estimasi model disajikan pada Tabel 3 untuk sesi kontinu utama dan keseluruhan 7 hari.

**Tabel 3.** Karakteristik Statistik Pengujian Kontinu 7 Hari
| Parameter | Sesi Kontinu Utama (`f27413f0`, 27.022 Sampel) | | | | | Keseluruhan 7 Hari (30.260 Sampel) | | | | |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| | Min | Mean | Median | Max | Std | Min | Mean | Median | Max | Std |
| Suhu (°C) | 22,20 | 25,92 | 25,40 | 31,50 | 1,99 | 22,20 | 26,02 | 25,50 | 31,50 | 2,07 |
| Kelembaban Relatif (% RH) | 39,50 | 55,51 | 55,70 | 75,50 | 7,25 | 39,50 | 55,64 | 55,90 | 75,50 | 6,95 |
| GP2Y Raw ADC (12-bit) | 937,87 | 1.033,07 | 1.021,94 | 4.095,00 | 49,21 | 937,87 | 1.039,00 | 1.029,32 | 4.095,00 | 50,54 |
| MQ-7 Raw ADC (12-bit) | 2.103,42 | 2.559,36 | 2.536,57 | 3.743,83 | 198,58 | 2.103,42 | 2.581,19 | 2.558,86 | 3.743,83 | 200,22 |
| MQ-135 Raw ADC (12-bit) | 1.179,41 | 1.616,25 | 1.597,59 | 3.403,95 | 234,56 | 1.179,41 | 1.642,06 | 1.652,44 | 3.403,95 | 236,96 |
| Estimasi $\text{PM}_{2.5}$ ($\mu\text{g/m}^3$) | 20,46 | 33,80 | 30,67 | 80,25 | 5,64 | 20,46 | 34,42 | 31,04 | 80,25 | 5,80 |
| Estimasi $\text{CO}$ ($\text{ppm}$) | 2,68 | 4,05 | 3,81 | 7,44 | 0,80 | 2,68 | 4,13 | 3,89 | 7,44 | 0,80 |
| Indeks ISPU Instan | 56,22 | 73,70 | 69,40 | 126,16 | 7,95 | 56,22 | 74,44 | 70,29 | 126,16 | 7,98 |
| Commanded Fan PWM (%) | 14,90 | 14,96 | 14,90 | 85,10 | 0,80 | 14,90 | 14,96 | 14,90 | 85,10 | 0,75 |
| Free Heap RAM (bytes) | 196.728 | 199.145 | 199.140 | 201.348 | 86,41 | 196.728 | 199.149 | 199.140 | 201.372 | 100,64 |

Distribusi kategori mutu udara pada keseluruhan 30.260 sampel didominasi oleh Kategori Sedang (ISPU 51–100) sebesar **99,405%** (30.080 sampel), diikuti oleh Kategori Tidak Sehat (ISPU 101–200) sebesar **0,592%** (179 sampel) yang teramati mengalami kenaikan temporer melampaui ambang batas 100 pada periode 11 dan 15 September, serta anomali sesar saturasi Kategori 0.0 sebanyak **1 sampel (0,003%)**. Perintah kecepatan kipas PWM mencerminkan kondisi tersebut: 30.034 sampel (99,253%) pada Level 2 (PWM 14,90%), 224 sampel (0,740%) pada Level 3 (PWM 21,96%), 1 sampel pada Level 4 (PWM 50,20%), dan 1 sampel pada Level 5 (PWM 85,10%).

### 3.4 Evaluasi Ketahanan Sesar Terprogram: Kasus Saturasi Optik 13 September 2026

Pengamatan empiris mengenai respon sistem terhadap anomali pembacaan instrumen tercatat pada tanggal **13 September 2026 pukul 02:13:06 WIB**. Sensor debu GP2Y membaca nilai rel maksimum ADC 12-bit (`ADC = 4095.00`):
- **Deteksi Sesar:** Mikrokontroler mendeteksi nilai ADC jenuh pada 4095 dan mengaktifkan bit flag `22930` ($16384 \text{ [GP mean jenuh]} + 4096 + 2048 + 256 + 128 \text{ [model invalid]} + 16 + 2$).
- **Aksi Proteksi:** Sesuai aturan terprogram, status keluaran model ditandai invalid, ISPU disetel `NaN`, Kategori disetel `0.0`, buzzer polusi dimatikan untuk mencegah alarm palsu, dan perintah kipas dialihkan ke Level 5 darurat (`PWM = 85.10%`).
- **Pola Pemulihan (*Smooth Decay*):** Dua puluh detik kemudian (02:13:26 WIB), saat ADC GP2Y kembali normal (986,48), sistem tidak menurunkan kipas secara mendadak, melainkan mengeksekusi transisi bertahap ke Level 4 (`PWM = 50.20%`), sebelum kembali ke Level 2 (`PWM = 14.90%`) pada 02:13:46 WIB. Mekanisme ini mendemonstrasikan eksekusi deterministik aturan fallback proteksi dan histeresis aktuator yang telah diprogram pada kondisi sesar sensor nyata.

---

## 4. KESIMPULAN

Penelitian ini telah mengimplementasikan dan mengevaluasi secara operasional prototipe pemantau kualitas udara multi-polutan berbasis mikrokontroler ESP32 yang mengintegrasikan dual-model *TinyML Random Forest* C++ statis dan interpolasi regulasi sub-indeks Permen LHK 14/2020. Pengujian operasional selama 170,535 jam kalender (10–17 September 2026) di lingkungan kamar tidur hunian nyata menghasilkan 30.260 rekaman telemetri awan yang terdistribusi ke dalam 5 sesi booting. Parameter lingkungan teramati mencatat rentang suhu 22,20°C–31,50°C (rerata 26,02°C), kelembaban relatif 39,50%–75,50% (rerata 55,64%), estimasi nominal $\text{PM}_{2.5}$ 20,46–80,25 $\mu\text{g/m}^3$ (rerata 34,42 $\mu\text{g/m}^3$), estimasi nominal $\text{CO}$ 2,68–7,44 ppm (rerata 4,13 ppm), dan sub-indeks ISPU instan 56,22–126,16 (rerata 74,44). Mutu udara didominasi Kategori Sedang sebesar 99,405% (30.080 sampel), Kategori Tidak Sehat 0,592% (179 sampel), dan anomali saturasi sensor optik Kategori 0 sebesar 0,003% (1 sampel).

Secara kumulatif 7 hari, keandalan transmisi telemetri mencatat kelengkapan slot sebesar 98,59% (30.260 feed dari 30.692 slot terbentang) dan tingkat keberhasilan percobaan pengiriman sebesar 98,90% (30.259 berhasil dari 30.596 percobaan; 337 kegagalan transmisi jaringan, 101 slot dilewati saat Wi-Fi belum siap). Kestabilan memori *heap* RAM teramati berfluktuasi stabil pada rentang 196.728–201.372 bytes dengan deviasi standar 100,64 bytes tanpa tren degradasi progresif. Sesi operasional kontinu tunggal terpanjang berjalan selama 151,26 jam non-stop (27.022 sampel, Boot `f27413f0`) dengan deviasi standar *heap* 86,41 bytes, kelengkapan slot 99,25%, dan keberhasilan percobaan 99,57%. Empat transisi restart terdokumentasi antar-sesi dengan jeda waktu 22,0 hingga 51,0 detik (tiga kali kode register reset `r=1` / *power-on* dan satu kali kode `r=7` / *task watchdog timer*). Sesuai batasan sistem lapangan tanpa instrumentasi pencatat tegangan eksternal independen, penyebab fisik eksternal di balik kejadian restart tidak dipastikan secara spekulatif.

Logika proteksi dan histeresis aktuator bertahap (*smooth decay*) terbukti beroperasi sesuai aturan terprogram saat terjadi anomali pembacaan saturasi optik sesaat pada 13 September 02:13:06 WIB. Keterbatasan operasional penelitian ini dicatat secara transparan: (1) sinyal kendali PWM kipas beroperasi sebagai perintah algoritma (*commanded PWM*) di mana status putaran mekanis fisik motor tidak diukur secara mandiri (konektor dicabut pada malam hari demi kenyamanan tidur penghuni tanpa sensor takometer), sehingga penelitian ini tidak mengevaluasi laju pengiriman udara bersih (*CADR*) atau eliminasi polutan; serta (2) model inferensi beroperasi pada skala transfer nominal tanpa klaim akurasi metrologis terverifikasi karena belum diuji terhadap instrumen acuan bersertifikat. Penelitian lanjutan diarahkan pada pengujian komparatif berpasangan di kamar uji gas terkontrol (*collocated testing in a certified chamber*) bersama instrumen acuan bersertifikat guna mentransformasikan estimasi nominal ke standar metrologi fisik, serta penambahan sensor takometer untuk memantau putaran mekanis kipas secara independen.

---

## UCAPAN TERIMA KASIH

Penulis menyampaikan terima kasih kepada tim pengembang Project Stuzha atas dukungan teknis dan penyediaan fasilitas eksperimen selama pengujian operasional 7 hari ini.

---

## DAFTAR PUSTAKA

[1] WHO, *WHO guidelines for indoor air quality: selected pollutants*, World Health Organization, 2010.  
[2] C. A. Pope III and D. W. Dockery, "Health effects of fine particulate air pollution: lines that connect," *Journal of the Air & Waste Management Association*, vol. 56, no. 6, pp. 709–742, 2006.  
[3] Kementerian Lingkungan Hidup dan Kehutanan Republik Indonesia, *Peraturan Menteri LHK No. 14 Tahun 2020 tentang Indeks Standar Pencemar Udara*, Jakarta: KLHK, 2020.  
[4] E. G. Snyder et al., "The changing paradigm of air pollution monitoring," *Environmental Science & Technology*, vol. 47, no. 20, pp. 11369–11377, 2013.  
[5] P. Kumar et al., "The rise of low-cost sensing for managing air pollution in cities," *Environment International*, vol. 75, pp. 199–205, 2015.  
[6] A. Rai et al., "End-user perspective on low-cost air quality sensors," *Environment International*, vol. 107, pp. 95–105, 2017.  
[7] V. Johnson et al., "Field calibration of low-cost air quality sensors using machine learning," *Atmospheric Measurement Techniques*, vol. 11, no. 4, pp. 2437–2456, 2018.  
[8] F. Al-Ali et al., "IoT-based air quality monitoring system using cloud computing," *IEEE Internet of Things Journal*, vol. 6, no. 2, pp. 1823–1834, 2019.  
[9] W. Shi et al., "Edge computing: Vision and challenges," *IEEE Internet of Things Journal*, vol. 3, no. 5, pp. 637–646, 2016.  
[10] C. R. Banbury et al., "Micronets: Neural network architectures for extremely resource-constrained embedded devices," *arXiv preprint arXiv:2010.11267*, 2020.  
[11] L. Breiman, "Random forests," *Machine Learning*, vol. 45, no. 1, pp. 5–32, 2001.
