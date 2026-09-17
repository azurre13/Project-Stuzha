# Draf Artikel Ilmiah: Implementasi dan Evaluasi Empiris Prototipe Monitoring Kualitas Udara Indoor Multi-Polutan Berbasis TinyML Edge Computing dan Regulasi Permen LHK No. 14 Tahun 2020

**Format Naskah:** Format Standar Jurnal Nasional Terakreditasi (SINTA 2 / SINTA 3)  
**Bidang Fokus:** *Embedded Systems*, *Edge Machine Learning*, *Internet of Things (IoT)*, *Indoor Air Quality Monitoring*.

---

## JUDUL / TITLE

**Implementasi dan Evaluasi Operasional 7 Hari Prototipe Monitoring Kualitas Udara Indoor Multi-Polutan Berbasis TinyML Random Forest dan Regulasi Permen LHK 14/2020 pada ESP32**

*Implementation and 7-Day Operational Evaluation of a TinyML Random Forest-Based Multi-Pollutant Indoor Air Quality Monitoring Prototype with Permen LHK 14/2020 Regulation on ESP32*

---

## ABSTRAK (INDONESIAN)

Pemantauan kualitas udara dalam ruangan (*Indoor Air Quality* / IAQ) multi-polutan umumnya terkendala oleh mahalnya instrumen pembanding kelas referensi serta keterbatasan mikrokontroler berdaya rendah dalam menjalankan inferensi cerdas dan penentuan indeks regulasi secara otonom di sisi *edge*. Penelitian ini merancang, mengimplementasikan, dan mengevaluasi prototipe monitoring IAQ berbasis mikrokontroler ESP32 yang mengintegrasikan sensor berbiaya rendah (Sharp GP2Y1010AU0F, MQ-7, MQ-135, dan DHT22) dengan komputasi *Tiny Machine Learning* (TinyML) *Random Forest* C++ statis dan formulasi interpolasi sub-indeks kontinu Peraturan Menteri Lingkungan Hidup dan Kehutanan (Permen LHK) No. 14 Tahun 2020. Sistem mengeksekusi inferensi lokal untuk partikulat ($\text{PM}_{2.5}$) dan karbon monoksida ($\text{CO}$), menentukan parameter kritis melalui fungsi $\max(\text{Sub\_PM}, \text{Sub\_CO})$, serta menghasilkan sinyal kendali kecepatan kipas hisap (*commanded PWM*) dengan mekanisme histeresis bertingkat (*smooth decay*). Pengujian operasional kontinu selama 7 hari (10–17 September 2026, total durasi kalender 170,53 jam) di lingkungan kamar tidur hunian nyata menghasilkan 30.260 rekaman telemetri awan. Hasil evaluasi empiris mencatat sesi operasional kontinu terpanjang mencapai 151,26 jam (27.022 sampel) dengan kestabilan *heap* memori yang teramati (196.728–201.348 bytes, deviasi standar 86,41 bytes), kelengkapan slot telemetri 99,25%, dan tingkat keberhasilan percobaan transmisi 99,57%. Sistem terbukti memiliki ketahanan sesar (*fault-resilience*) saat terjadi saturasi optik sesaat pada sensor GP2Y (ADC 4095 pada 13 September 02:13:06 WIB) dengan mengaktifkan proteksi Level 5 darurat (PWM 85,10%) dan memulihkan aktuator secara bertahap. Penelitian ini mendemonstrasikan kelayakan arsitektur *edge AI* deterministik untuk pemantauan lingkungan transparan dan kendali aktuasi bertingkat tanpa ketergantungan mutlak pada komputasi awan.

**Kata Kunci:** *TinyML, Random Forest, ESP32, Permen LHK 14/2020, Indeks Standar Pencemar Udara (ISPU), Kualitas Udara Indoor, Sensor Berbiaya Rendah.*

---

## ABSTRACT (ENGLISH)

*Comprehensive indoor air quality (IAQ) monitoring is often hindered by the high cost of reference-grade instruments and the limited capacity of low-power microcontrollers to autonomously perform intelligent multi-pollutant inference and regulatory index determination at the edge. This study designs, implements, and evaluates an ESP32-based IAQ monitoring prototype that integrates low-cost sensors (Sharp GP2Y1010AU0F, MQ-7, MQ-135, and DHT22) with static C++ Tiny Machine Learning (TinyML) Random Forest regression and continuous sub-index interpolation based on the Indonesian Ministry of Environment and Forestry Regulation (Permen LHK) No. 14/2020. The system deterministically executes local inference for fine particulate matter ($\text{PM}_{2.5}$) and carbon monoxide ($\text{CO}$), determines the critical parameter via $\max(\text{Sub\_PM}, \text{Sub\_CO})$, and generates closed-loop fan speed commands (commanded PWM) governed by multi-level hysteresis and smooth decay. A 7-day continuous operational stress test (September 10–17, 2026; 170.53 total calendar hours) in a real domestic bedroom environment yielded 30,260 cloud telemetry records. Empirical results demonstrate a longest continuous uninterrupted session of 151.26 hours (27,022 samples) with remarkable observed heap memory stability (196,728–201,348 bytes, standard deviation of 86.41 bytes), 99.25% telemetry slot completeness, and a 99.57% transmission attempt success rate. The firmware exhibited robust fault resilience during a transient optical saturation event (GP2Y ADC 4095 on September 13, 02:13:06 WIB) by triggering emergency Level 5 protection (PWM 85.10%) followed by autonomous staged decay. This research proves the feasibility of deterministic edge AI architectures on low-power microcontrollers for transparent environmental monitoring and staged actuation.*

**Keywords:** *TinyML, Random Forest, ESP32, ISPU, Air Quality Index, Low-Cost Sensors, Indoor Air Quality, Embedded Edge AI.*

---

## 1. PENDAHULUAN

Kualitas udara dalam ruangan (*Indoor Air Quality* / IAQ) merupakan faktor krusial bagi kesehatan masyarakat mengingat sebagian besar populasi perkotaan menghabiskan 80% hingga 90% waktu kesehariannya di dalam lingkungan tertutup [1]. Partikulat halus berdiameter $\le 2{,}5\,\mu\text{m}$ ($\text{PM}_{2.5}$) dan gas karbon monoksida ($\text{CO}$) merupakan dua polutan utama yang menjadi ancaman serius karena kemampuannya menembus alveolus paru-paru hingga aliran darah dan menyebabkan disfungsi kardiovaskular [2]. Di Indonesia, acuan pelaporan kualitas udara nasional diatur melalui Indeks Standar Pencemar Udara (ISPU) berdasarkan Peraturan Menteri Lingkungan Hidup dan Kehutanan (Permen LHK) No. 14 Tahun 2020 [3]. Regulasi ini menetapkan 5 kategori mutu udara: Baik (0–50), Sedang (51–100), Tidak Sehat (101–200), Sangat Tidak Sehat (201–300), dan Berbahaya (>300).

Meskipun instrumen pemantau profesional (*reference-grade instruments*) mampu menyajikan akurasi konsentrasi yang tersertifikasi, biaya pengadaan yang mencapai puluhan juta rupiah, kebutuhan kalibrasi berkala yang rumit, dan dimensi fisik yang masif membatasi penerapannya pada skala hunian domestik [4]. Sebagai alternatif, sensor berbiaya rendah (*low-cost sensors*) seperti modul sensor debu hamburan optik (GP2Y1010AU0F) dan sensor gas semikonduktor oksida logam / MOX (MQ-7, MQ-135) banyak digunakan [5]. Kendati demikian, sensor murah memiliki kelemahan mendasar berupa respon non-linear, derau lingkungan, serta sensitivitas silang (*cross-sensitivity*) yang kuat terhadap fluktuasi suhu dan kelembaban relatif (*RH*) [6].

Untuk mengatasi non-linearitas tersebut, teknik *Machine Learning* (ML) telah terbukti efektif dalam memetakan sinyal mentah sensor menjadi estimasi konsentrasi polutan [7]. Namun demikian, mayoritas sistem *Internet of Things* (IoT) yang ada saat ini menerapkan arsitektur *cloud-centric*, di mana seluruh data sensor mentah dikirim ke peladen (*cloud server*) untuk diproses [8]. Pola arsitektur ini rentan terhadap latensi jaringan, konsumsi *bandwidth*, serta kegagalan sistem kendali aktuator apabila konektivitas internet terputus [9].

Perkembangan *Tiny Machine Learning* (TinyML) memungkinkan model inferensi cerdas dieksekusi langsung pada perangkat mikrokontroler berdaya rendah di sisi *edge* (*on-device inference*) [10]. Model berbasis pohon keputusan (*Random Forest*) memiliki keunggulan komparatif untuk sistem tertanam karena operasinya didasarkan pada percabangan kondisi logika linier (*if-else*) yang tidak memerlukan operasi komputasi matriks kompleks atau pustaka *runtime* eksternal yang membebani RAM statis [11].

Penelitian ini merancang, mengimplementasikan, dan mengevaluasi prototipe monitoring kualitas udara terpadu berbasis mikrokontroler ESP32 dengan nama Project Stuzha. Kontribusi utama penelitian ini mencakup:
1. **Inferensi Multi-Polutan On-Device:** Implementasi dual-model *Random Forest* C++ statis untuk estimasi simultan $\text{PM}_{2.5}$ dan $\text{CO}$ langsung pada memori mikrokontroler dengan latensi mikrodetik.
2. **Standardisasi Regulasi Kontinu:** Integrasi algoritma interpolasi kontinu Permen LHK 14/2020 dan pemilihan parameter kritis $\max(\text{Sub\_PM}, \text{Sub\_CO})$ untuk kendali histeresis kipas hisap (*closed-loop commanded PWM*).
3. **Evaluasi Empiris 7 Hari di Lingkungan Nyata:** Pengujian operasional kontinu selama 170,53 jam kalender di lingkungan hunian nyata dengan pemisahan sesi booting, evaluasi kestabilan memori *heap*, rekonsiliasi slot telemetri, dan analisis empiris penanganan sesar saturasi optik.

---

## 2. METODOLOGI PENELITIAN

### 2.1 Desain Perangkat Keras dan Tata Letak Fisik

Prototipe Stuzha dibangun menggunakan casing berbahan gabus keras berdimensi aliran udara vertikal. Aliran udara dikonfigurasikan dari bawah ke atas:
- **Intake Bawah dan Bilik Sensor:** Udara masuk melalui bukaan bawah. Seluruh modul sensor diletakkan di bilik intake **sebelum** media filter. Sensor partikulat Sharp GP2Y1010AU0F diposisikan horizontal, sensor gas MQ-7 dan MQ-135 dipasang vertikal pada dinding bilik, dan sensor suhu/kelembaban DHT22 ditempatkan berdampingan.
- **Media Filter Pendukung:** Terdiri dari filter karbon aktif kotak dan potongan media filter sintetis otomotif (non-HEPA), dipisahkan oleh ruang celah aliran $\approx 5\text{ cm}$ sebelum kipas.
- **Exhaust dan Kipas:** Kipas aksial 12V ($12 \times 12\text{ cm}$) dipasang di bagian atas untuk menarik udara keluar (*exhaust*).

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

Sub-indeks dihitung menggunakan formula:
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

### 2.4 Protokol Pengujian Lapangan dan Keterbatasan

Pengujian dilakukan di kamar tidur domestik selama 7 hari kalender penuh (10–17 September 2026). Sesuai integritas metodologi ilmiah, dua batasan lapangan dicatat:
1. **Status Fisik Motor Kipas:** Untuk menjaga kenyamanan tidur penghuni (*acoustic comfort*), konektor daya motor kipas 12V sebagian besar dilepas/dicabut pada malam hari. Mikrokontroler ESP32 tetap membangkitkan sinyal kontrol PWM pada GPIO 19 secara kontinu tanpa gangguan. Oleh karena itu, data kecepatan kipas dilaporkan secara ketat sebagai **perintah kontrol algoritma (*commanded PWM*)**, bukan kecepatan fisik mekanis aktual (*RPM putaran*).
2. **Dinamika Suhu Ruangan dan Penyejuk Udara (AC):** Kamar dilengkapi pendingin udara (AC). Fluktuasi suhu ruangan (22,20°C–31,50°C) berkorelasi dengan catatan logbook penghuni: suhu naik saat penghuni bepergian keluar kamar dengan AC dimatikan, dan suhu stabil rendah (22°C–25°C) saat penghuni beristirahat dengan AC aktif. Mengingat suhu dan kelembaban merupakan fitur input model, korelasinya dengan estimasi model dipahami sebagai interaksi fitur TinyML, bukan pembuktian kompensasi *drift* fisik sensor.

---

## 3. HASIL DAN PEMBAHASAN

### 3.1 Ringkasan Observasi dan Pemisahan Sesi Booting

Selama periode 10 September 2026 pukul 20:01:51 WIB hingga 17 September 2026 pukul 22:33:57 WIB, sistem mengakumulasi **30.260 baris telemetri awan** pada Thingspeak Channel 3480764. Berdasarkan analisis stempel waktu dan kode reset pada field status STZ4, data terdiri atas 5 sesi booting yang dirinci pada Tabel 2.

**Tabel 2.** Rincian Sesi Booting dan Rekonsiliasi Transisi Restart 7 Hari
| No | Boot ID | Baris | Waktu Mulai (WIB) | Waktu Selesai (WIB) | Uptime Tercatat | Kode Reset | Keterangan Operasional |
|:--:|---|---:|---|---|---:|:---:|---|
| 1 | `c43d4d72` | 13 | 10 Sep 20:01:51 | 10 Sep 20:05:51 | 0,03 – 0,10 jam | 1 (`POWERON`) | Sesi uji commissioning via USB sebelum penempatan mandiri. |
| — | *Transisi 1* | — | 10 Sep 20:05:51 | 10 Sep 20:06:28 | Jeda: 37,0 detik | — | Pemindahan catu daya dari port USB PC ke adaptor dinding kamar. |
| **2** | `f27413f0` | **27.022** | **10 Sep 20:06:28** | **17 Sep 03:21:46** | **0,01 – 151,26 jam** | **1 (`POWERON`)** | **Sesi kontinu utama: 151,26 jam (6 Hari 7 Jam 15 Menit) non-stop.** |
| — | *Transisi 2* | — | 17 Sep 03:21:46 | 17 Sep 03:22:08 | Jeda: 22,0 detik | — | Fluktuasi tegangan sesaat (*power flicker/brownout*) dini hari. |
| 3 | `2ee94f8f` | 2.842 | 17 Sep 03:22:08 | 17 Sep 20:21:25 | 0,01 – 16,99 jam | 1 (`POWERON`) | Operasi pasca-flicker berjalan normal selama 16,99 jam. |
| — | *Transisi 3* | — | 17 Sep 20:21:25 | 17 Sep 20:22:00 | Jeda: 35,0 detik | — | Reset mikrokontroler oleh watchdog timer (`TG0WDT_SYS_RESET`). |
| 4 | `9f05ffe4` | 18 | 17 Sep 20:22:00 | 17 Sep 20:27:41 | 0,01 – 0,10 jam | 7 (`TG0WDT_SYS`) | Sesi transien pasca-watchdog. |
| — | *Transisi 4* | — | 17 Sep 20:27:41 | 17 Sep 20:28:32 | Jeda: 51,0 detik | — | Pemilik melakukan *power-cycle* adaptor dinding secara manual. |
| 5 | `37cbdc54` | 365 | 17 Sep 20:28:32 | 17 Sep 22:33:57 | 0,01 – 2,10 jam | 1 (`POWERON`) | Sesi penutupan observasi hingga akhir hari ke-7. |
| **Total** | **5 Sesi** | **30.260** | **10 Sep 20:01:51** | **17 Sep 22:33:57** | **170,53 jam** | — | **Ambang batas 168 jam terpenuhi secara akumulatif.** |

Data menunjukkan bahwa sesi operasi kontinu terpanjang tanpa interupsi mencapai **151,26 jam (Boot `f27413f0`)**, setara dengan 6,3 hari berturut-turut. Tiga kejadian restart pada hari ke-7 terdokumentasi secara transparan dengan rincian jeda waktu 22 hingga 51 detik.

### 3.2 Kestabilan Memori dan Rekonsiliasi Telemetri

Kestabilan memori dievaluasi pada sesi kontinu utama (`f27413f0`, 27.022 sampel). Kapasitas *free heap* RAM statis tercatat sebesar 201.348 bytes pada awal sesi dan 199.132 bytes pada jam ke-151, dengan nilai minimum 196.728 bytes dan deviasi standar sebesar **86,41 bytes**. Ketiadaan penurunan memori progresif (*progressive degradation*) membuktikan bahwa manajemen memori berbasis variabel statis dan alokasi array tetap pada ring buffer 1.440 menit tidak menimbulkan kebocoran memori (*memory leak*).

Rekonsiliasi telemetri pada sesi utama menunjukkan:
- Total slot telemetri yang terbentang antara sampel pertama dan terakhir adalah 27.226 slot (interval rata-rata 20,1 detik).
- Jumlah feed yang berhasil diterima peladen Thingspeak adalah 27.022 baris, menghasilkan **kelengkapan slot (*slot completeness*) sebesar 99,25%**.
- Dari sisi perangkat, tercatat 27.135 kali percobaan pengiriman dengan 118 kali kegagalan jaringan, menghasilkan **tingkat keberhasilan percobaan (*attempt success rate*) sebesar 99,57%**.
- Sebanyak 91 slot dilewati (*skipped slots*) secara otomatis saat perangkat mendeteksi koneksi Wi-Fi sedang dalam proses rekoneksi. Persamaan slot terbukti konsisten: $27.135 \text{ (attempts)} + 91 \text{ (skipped)} = \mathbf{27.226 \text{ slots}}$.

### 3.3 Statistik Lingkungan dan Dinamika Multi-Polutan

Rangkuman statistik parameter sensor dan estimasi model disajikan pada Tabel 3 untuk sesi utama dan keseluruhan 7 hari.

**Tabel 3.** Karakteristik Statistik Pengujian Kontinu 7 Hari
| Parameter | Sesi Utama (`f27413f0`, 27.022 Sampel) | | | | Keseluruhan 7 Hari (30.260 Sampel) | | | |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| | Min | Mean | Median | Max | Min | Mean | Median | Max |
| Suhu (°C) | 22,20 | 25,92 | 25,40 | 31,50 | 22,20 | 26,02 | 25,50 | 31,50 |
| Kelembaban Relatif (% RH) | 39,50 | 55,51 | 55,70 | 75,50 | 39,50 | 55,64 | 55,90 | 75,50 |
| GP2Y Raw ADC (12-bit) | 937,87 | 1.033,07 | 1.021,94 | 4.095,00 | 937,87 | 1.039,00 | 1.029,32 | 4.095,00 |
| MQ-7 Raw ADC (12-bit) | 2.103,42 | 2.559,36 | 2.536,57 | 3.743,83 | 2.103,42 | 2.581,19 | 2.558,86 | 3.743,83 |
| MQ-135 Raw ADC (12-bit) | 1.179,41 | 1.616,25 | 1.597,59 | 3.403,95 | 1.179,41 | 1.642,06 | 1.652,44 | 3.403,95 |
| Estimasi $\text{PM}_{2.5}$ ($\mu\text{g/m}^3$) | 20,46 | 33,80 | 30,67 | 80,25 | 20,46 | 34,42 | 31,04 | 80,25 |
| Estimasi $\text{CO}$ ($\text{ppm}$) | 2,68 | 4,05 | 3,81 | 7,44 | 2,68 | 4,13 | 3,89 | 7,44 |
| Indeks ISPU Instan | 56,22 | 73,70 | 69,40 | 126,16 | 56,22 | 74,44 | 70,29 | 126,16 |
| Commanded Fan PWM (%) | 14,90 | 14,96 | 14,90 | 85,10 | 14,90 | 14,96 | 14,90 | 85,10 |
| Free Heap RAM (bytes) | 196.728 | 199.145 | 199.140 | 201.348 | 196.728 | 199.149 | 199.140 | 201.372 |

Distribusi kategori kualitas udara menunjukkan dominasi Kategori Sedang (ISPU 51–100) sebesar **99,405%** (30.080 sampel), diikuti Kategori Tidak Sehat (ISPU 101–200) sebesar **0,592%** (179 sampel) yang bertepatan dengan aktivitas pembakaran/asap di sekitar hunian pada 11 dan 15 September, serta Kategori 0.0 (Invalid/Saturasi) sebanyak **1 sampel (0,003%)**. Perintah kipas mencerminkan distribusi ini: 30.034 sampel (99,25%) berada pada Level 2 (PWM 14,90%), 224 sampel (0,74%) pada Level 3 (PWM 21,96%), 1 sampel pada Level 4 (PWM 50,20%), dan 1 sampel pada Level 5 (PWM 85,10%).

### 3.4 Evaluasi Ketahanan Sesar: Kasus Saturasi Optik 13 September 2026

Bukti empiris ketahanan sesar (*fault tolerance*) teramati pada tanggal **13 September 2026 pukul 02:13:06 WIB**. Sensor debu GP2Y mengalami saturasi rel penuh (`ADC = 4095.00`):
- **Deteksi Sesar:** Mikrokontroler mendeteksi nilai ADC mencapai batas maksimum 4095 dan mencatat flag bit `22930` ($16384 \text{ [GP mean jenuh]} + 4096 + 2048 + 256 + 128 \text{ [model invalid]} + 16 + 2$).
- **Aksi Proteksi:** Alih-alih mengekstrapolasikan nilai partikulat ekstrem, sistem menetapkan status model invalid, ISPU disetel `NaN`, Kategori disetel `0.0`, alarm dimatikan (*prevent false alarm*), dan perintah kipas langsung dialihkan ke Level 5 darurat (`PWM = 85.10%`).
- **Pemulihan Bertingkat (*Smooth Decay*):** Dua puluh detik kemudian (02:13:26 WIB), saat ADC GP2Y kembali normal (986,48), sistem tidak menurunkan kipas secara mendadak, melainkan mengeksekusi transisi bertahap ke Level 4 (`PWM = 50.20%`), sebelum kembali ke Level 2 (`PWM = 14.90%`) pada 02:13:46 WIB. Mekanisme histeresis ini terbukti efektif melindungi aktuator mekanik dari lonjakan transien.

---

## 4. KESIMPULAN

Penelitian ini berhasil mendemonstrasikan implementasi terpadu *TinyML Random Forest* C++ dan interpolasi regulasi ISPU Permen LHK 14/2020 pada mikrokontroler berdaya rendah ESP32. Pengujian operasional selama 170,53 jam (7 hari penuh) di lingkungan hunian nyata membuktikan bahwa arsitektur komputasi *edge* mampu beroperasi secara stabil dengan deviasi standar *heap* memori hanya 86,41 bytes dan kelengkapan transmisi telemetri 99,25%. Mekanisme kendali histeresis dan penanganan saturasi optik terbukti andal dalam menjaga keselamatan aktuator dan mencegah alarm palsu. Riset lanjutan diarahkan pada kalibrasi kamar uji gas terkendali (*gas chamber*) berdampingan dengan instrumen acuan bersertifikat guna memvalidasi akurasi konsentrasi fisik di masa depan.

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
