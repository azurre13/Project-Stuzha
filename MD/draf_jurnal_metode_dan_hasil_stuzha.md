# Draf Artikel Ilmiah: Prototipe Monitoring Kualitas Udara Indoor Multi-Polutan Berbasis TinyML dan Regulasi Permen LHK 14/2020

**Target Publikasi:** Jurnal Nasional Terakreditasi (SINTA 2 / SINTA 3)  
**Bidang Ilmu:** Sistem Tertanam (*Embedded Systems*), *Edge Artificial Intelligence*, *Internet of Things* (IoT), Pemantauan Lingkungan Indoor.

---

## ABSTRAK

Pemantauan kualitas udara dalam ruangan (*indoor air quality*) yang komprehensif umumnya terbentur pada mahalnya instrumen pembanding standar serta keterbatasan mikrokontroler berdaya rendah dalam mengeksekusi inferensi multi-polutan secara simultan. Penelitian ini merancang dan mengevaluasi prototipe monitoring kualitas udara terpadu berbasis ESP32 yang mengintegrasikan sensor berbiaya rendah (GP2Y1010AU0F, MQ-7, MQ-135, dan DHT22) dengan komputasi *edge* TinyML (*Random Forest* C++) serta algoritma sub-indeks kontinu berbasis Peraturan Menteri Lingkungan Hidup dan Kehutanan (Permen LHK) No. 14 Tahun 2020. Sistem mengeksekusi inferensi instan PM2.5 dan CO secara deterministik di tingkat mikrokontroler, memetakan konsentrasi ke sub-indeks regulasi, memilih parameter kritis $\max(\text{Sub\_PM}, \text{Sub\_CO})$, serta menghasilkan perintah kendali kecepatan kipas hisap (*closed-loop commanded PWM*). Prototipe diuji secara operasional kontinu selama 7 hari (10–17 September 2026, 170,5 jam total) di lingkungan hunian nyata, menghasilkan 30.260 rekaman telemetri awan. Evaluasi sistem mencatat sesi kontinu terpanjang mencapai 151,26 jam (27.022 sampel) tanpa penurunan memori progresif (*heap* stabil pada 196.728–201.348 bytes, deviasi standar 86,41 bytes), kelengkapan slot telemetri 99,25%, dan keberhasilan percobaan transmisi 99,57%. Sistem terbukti memiliki ketahanan gangguan (*fault-resilience*) saat terjadi saturasi optik sesaat pada sensor partikulat dengan mengeksekusi peralihan darurat ke Level 5 lalu pemulihan bertahap (*smooth decay*). Penelitian ini mendemonstrasikan kelayakan arsitektur *edge AI* deterministik pada mikrokontroler berdaya rendah untuk pemantauan lingkungan transparan dan kendali aktuasi bertingkat.

**Kata Kunci:** *TinyML, Random Forest, Indeks Standar Pencemar Udara (ISPU), ESP32, Sensor Berbiaya Rendah, Pemantauan Indoor.*

---

## 1. PENDAHULUAN

Kualitas udara dalam ruangan (*Indoor Air Quality* / IAQ) memiliki dampak signifikan terhadap kesehatan manusia mengingat masyarakat perkotaan menghabiskan lebih dari 80% waktunya di dalam ruangan. Parameter polutan utama seperti partikulat halus ($\text{PM}_{2.5}$) dan karbon monoksida ($\text{CO}$) menjadi perhatian kritis karena potensi toksisitasnya terhadap sistem pernapasan dan kardiovaskular. Di Indonesia, standar pelaporan resmi kualitas udara diatur melalui Indeks Standar Pencemar Udara (ISPU) berdasarkan Peraturan Menteri LHK No. 14 Tahun 2020, yang membagi kategori kualitas udara menjadi Baik (0–50), Sedang (51–100), Tidak Sehat (101–200), Sangat Tidak Sehat (201–300), dan Berbahaya (>300).

Meskipun instrumen pemantau profesional kelas referensi (*reference-grade instruments*) memberikan akurasi tinggi, biaya pengadaan yang sangat mahal dan ukuran fisik yang masif membatasi penerapannya pada lingkungan hunian domestik. Di sisi lain, sensor berbiaya rendah (*low-cost sensors*) seperti sensor debu hamburan optik (GP2Y1010) dan sensor semikonduktor oksida logam (MQ-7, MQ-135) rentan terhadap ketidaklinieran, derau lingkungan, serta sensitivitas silang (*cross-sensitivity*) terhadap fluktuasi suhu dan kelembaban relatif.

Pendekatan *Machine Learning* (ML) terbukti mampu memodelkan relasi non-linear respon sensor berbiaya rendah. Namun, sebagian besar solusi yang ada masih mengandalkan arsitektur *cloud-centric*, di mana data mentah dikirim ke peladen (*server*) terpusat untuk diproses. Pola ini menimbulkan ketergantungan mutlak pada stabilitas koneksi internet, latensi jaringan, serta risiko kegagalan kendali aktuator jika koneksi terputus.

Penelitian ini mengusulkan implementasi *Tiny Machine Learning* (TinyML) berbasis pohon keputusan (*Random Forest*) langsung pada tingkat mikrokontroler ESP32 (*edge inference*). Pendekatan ini memungkinkan komputasi inferensi multi-polutan dan interpolasi ISPU Permen LHK 14/2020 secara lokal dalam hitungan mikrodetik, sehingga perintah aktuasi kipas hisap bertingkat (*commanded PWM*) tetap beroperasi secara otonom tanpa jeda jaringan. Kontribusi penelitian ini ditekankan pada evaluasi deployment fisik jangka panjang (7 hari kontinu di lingkungan hunian), transparansi kontrak telemetri, kestabilan memori *embedded*, serta ketahanan sistem terhadap anomali pembacaan sensor.

---

## 2. METODOLOGI PENELITIAN

### 2.1 Arsitektur Perangkat Keras dan Tata Letak Fisik

Prototipe Stuzha dirancang menggunakan casing gabus padat dengan dimensi aliran vertikal. Konfigurasi aliran udara disusun sebagai berikut:
1. **Intake Bawah:** Udara ruangan masuk secara bebas melalui bukaan intake di bagian bawah casing.
2. **Bilik Sensor (Sebelum Filter):** Seluruh modul sensor diletakkan di zona intake sebelum media filtrasi. Sensor partikulat Sharp GP2Y1010AU0F dipasang dengan lubang deteksi horizontal, sedangkan sensor gas MQ-7 (CO) dan MQ-135 (proksi gas campuran/VOC) dipasang vertikal pada dinding bilik. Sensor suhu dan kelembaban relatif DHT22 ditempatkan berdampingan untuk mencatat profil termal mikroklimat.
3. **Media Filtrasi Pendukung:** Terdiri dari filter karbon aktif kotak dan potongan filter serat sintetis otomotif (non-HEPA) dengan celah udara (*air gap*) $\approx 5\text{ cm}$ sebelum kipas.
4. **Kipas dan Exhaust Atas:** Kipas aksial 12V ($12 \times 12\text{ cm}$) ditempatkan di bagian paling atas untuk menarik udara keluar (*exhaust*).

Pemetaan pin GPIO mikrokontroler ESP32 Dev Module diatur secara deterministik:
- `GPIO 34` (ADC1_CH6): Sinyal analog tegangan GP2Y1010 ($V_o$)
- `GPIO 5`: Sinyal pulsa pemicu ILED GP2Y1010 (durasi pulsa $320\,\mu\text{s}$, sampling ADC pada $280\,\mu\text{s}$)
- `GPIO 32` (ADC1_CH4): Sinyal analog MQ-7
- `GPIO 33` (ADC1_CH5): Sinyal analog MQ-135
- `GPIO 4`: Komunikasi data digital DHT22
- `GPIO 19`: Sinyal output kendali kecepatan PWM kipas (LEDC kanal 0, frekuensi 25 kHz, resolusi 8-bit)
- `GPIO 18`: Sinyal kendali buzzer piezoelektrik (LEDC kanal 15, frekuensi 1.000 Hz)

```text
[ EXHAUST ATAS ]
       ↑
[ KIPAS 12 × 12 cm ] (GPIO 19 PWM)
       ↑
[ RUANG KOSONG ~5 cm ]
       ↑
[ FILTER MOBIL & FILTER KARBON ]
       ↑
[ BILIK SENSOR INTAKE ]  <-- GP2Y, MQ-7, MQ-135, DHT22
       ↑
[ INTAKE BAWAH ]
```

### 2.2 Model TinyML Edge Inference

Untuk menjamin eksekusi deterministik tanpa alokasi dinamis (*zero dynamic allocation* di loop inferensi), model regresi *Random Forest* diekspor menjadi kode C++ murni menggunakan struktur pohon bertingkat statis (*hardcoded decision trees*):
1. **Model Estimasi PM2.5 (`model_pm.h`):** Menerima 3 fitur input: estimasi tegangan GP2Y yang dinormalisasi, suhu (°C), dan kelembaban relatif (% RH). Model terdiri atas kumpulan pohon regresi yang menghasilkan keluaran estimasi konsentrasi nominal $\text{PM}_{2.5}$ ($\mu\text{g/m}^3$).
2. **Model Estimasi CO (`model_co.h`):** Menerima 3 fitur input: nilai ADC mentah MQ-7 (12-bit, 0–4095), suhu (°C), dan kelembaban relatif (% RH). Model menghasilkan estimasi konsentrasi nominal CO ($\text{mg/m}^3$), yang selanjutnya dikonversi ke satuan tampilan $\text{ppm}$ pada kondisi referensi standar ($25^\circ\text{C}, 1\text{ atm}$) melalui pembagian faktor $1{,}145$.

Kedua model diposisikan secara eksplisit sebagai **estimator nominal eksperimental**. Model tidak diklaim sebagai instrumen terkalibrasi laboratorium mutlak karena keterbatasan ketiadaan instrumen referensi bersertifikat selama fase pengembangan ini.

### 2.3 Perhitungan Sub-Indeks ISPU dan Logika Kendali

Perhitungan indeks mengadopsi tabel matematis kontinu Lampiran I Permen LHK No. 14 Tahun 2020:
- **Titik Batas PM2.5 ($\mu\text{g/m}^3$):** $[0, 15.5, 55.4, 150.4, 250.4, 500]$
- **Titik Batas CO ($\mu\text{g/m}^3$):** $[0, 4000, 8000, 15000, 30000, 45000]$
- **Titik Batas Indeks ISPU:** $[0, 50, 100, 200, 300, 500]$

Interpolasi linier menghitung sub-indeks masing-masing polutan:
$$I_p = \frac{I_b - I_a}{X_b - X_a}(X - X_a) + I_a$$
Indeks gabungan instan ditentukan oleh nilai maksimum parameter kritis:
$$I_{\text{instan}} = \max(I_{\text{PM2.5}}, I_{\text{CO}})$$

Tingkat kendali kipas (*fan level*) L1 hingga L5 dipetakan terhadap kategori ISPU:
- Level 1 (Baik, ISPU 0–50): Duty cycle PWM 12,94% (33/255)
- Level 2 (Sedang, ISPU 51–100): Duty cycle PWM 14,90% (38/255)
- Level 3 (Tidak Sehat, ISPU 101–200): Duty cycle PWM 21,96% (56/255)
- Level 4 (Sangat Tidak Sehat, ISPU 201–300): Duty cycle PWM 50,20% (128/255)
- Level 5 (Berbahaya, ISPU >300 atau saturasi): Duty cycle PWM 85,10% (217/255)

Untuk mencegah osilasi aktuator akibat fluktuasi transien (*chattering*), algoritma menerapkan jendela konfirmasi kenaikan $\ge 1\text{ detik}$, histeresis penurunan 5%, dan waktu penundaan turun (*dwell time*) sebesar 8 detik per tingkat (*smooth decay*).

### 2.4 Protokol dan Batasan Pengujian Lingkungan

Pengujian dilakukan di ruang kamar tidur hunian nyata selama 7 hari berturut-turut (10–17 September 2026). Sesuai prinsip kejujuran ilmiah, dua batasan operasional lapangan dicatat secara transparan:
1. **Status Kipas Fisik (*Acoustic Comfort*):** Selama sebagian besar periode malam hari dan waktu istirahat, konektor daya motor kipas 12V dicabut oleh penghuni untuk menghindari kebisingan. Mikrokontroler tetap menghasilkan sinyal kendali PWM pada GPIO 19 (*commanded duty cycle*). Dengan demikian, data kecepatan kipas dilaporkan murni sebagai **perintah kontrol algoritma (*commanded PWM*)**, bukan kecepatan putaran mekanis aktual (*RPM tachometer*).
2. **Kondisi Termal Ruangan (AC):** Kamar dilengkapi unit AC mandiri. Peningkatan suhu ruangan (mencapai puncak 28,0°C–31,5°C) bertepatan dengan ketiadaan penghuni di kamar saat AC dimatikan. Saat penghuni berada di kamar dengan AC aktif, suhu tercatat stabil pada rentang 22,2°C–25,5°C. Karena suhu dan kelembaban merupakan fitur input langsung pada model TinyML, korelasi antara T/RH dan estimasi polutan dipahami sebagai interaksi fitur komputasi, bukan bukti kalibrasi fisik sensor di lapangan.

---

## 3. HASIL DAN PEMBAHASAN

### 3.1 Ringkasan Observasi dan Pemisahan Sesi Booting

Selama periode 10 September 2026 pukul 20:01 WIB hingga 17 September 2026 pukul 22:33 WIB (total durasi kalender 170,5 jam), sistem mentransmisikan **30.260 baris data telemetri** ke cloud ThingSpeak (Channel 3480764). Seluruh baris data menggunakan firmware aktif v4.0.0 (hash sumber `a945ea070fcc` dan hash model `d7f32c60`).

Analisis data memisahkan rekaman berdasarkan identitas sesi booting (*boot ID*):
1. **Boot Commissioning (`c43d4d72`):** Berlangsung selama 13 baris (0,10 jam) pada 10 September 2026 pukul 20:01–20:05 WIB saat inisialisasi awal melalui koneksi USB.
2. **Boot Kontinu Utama (`f27413f0`):** Berjalan selama **151,26 jam non-stop (6 Hari 7 Jam 15 Menit)** dari 10 September 2026 pukul 20:06 WIB hingga 17 September 2026 pukul 03:21 WIB, menghasilkan **27.022 sampel telemetri tanpa restart**.
3. **Boot Tambahan (`2ee94f8f`, `9f05ffe4`, `37cbdc54`):** Mengakumulasi 3.225 sampel pada 17 September 2026, menggenapkan durasi total pengujian melampaui ambang batas 168 jam (7 hari penuh).

| Sesi Boot | Hash Firmware | Jumlah Sampel | Waktu Mulai (WIB) | Waktu Selesai (WIB) | Uptime Akhir | Kode Reset |
|---|---|---:|---|---|---:|:---:|
| `c43d4d72` (Uji Awal) | `a945ea070fcc` | 13 | 10 Sep 20:01:51 | 10 Sep 20:05:51 | 0,10 jam | 1 (Power-On) |
| `f27413f0` (Utama) | `a945ea070fcc` | 27.022 | 10 Sep 20:06:28 | 17 Sep 03:21:46 | 151,26 jam | 1 (Power-On) |
| `2ee94f8f` | `a945ea070fcc` | 2.842 | 17 Sep 03:22:08 | 17 Sep 20:21:25 | 16,99 jam | 1 (Power-On) |
| `9f05ffe4` | `a945ea070fcc` | 18 | 17 Sep 20:22:00 | 17 Sep 20:27:41 | 0,10 jam | 7 (WDT/SW) |
| `37cbdc54` | `a945ea070fcc` | 365 | 17 Sep 20:28:32 | 17 Sep 22:33:57 | 2,10 jam | 1 (Power-On) |
| **Total Akumulasi** | **a945ea070fcc** | **30.260** | **10 Sep 20:01:51** | **17 Sep 22:33:57** | **> 170 jam** | — |

### 3.2 Evaluasi Reliabilitas Sistem Tertanam

Kestabilan operasional dievaluasi pada sesi utama (`f27413f0`, 27.022 baris):
1. **Kestabilan Memori (*Heap Stability*):** Alokasi dinamis dipantau melalui pembacaan `esp_get_free_heap_size()`. Sisa RAM statis tercatat sebesar 201.348 bytes pada inisialisasi awal dan 199.132 bytes pada akhir jam ke-151, dengan nilai minimum 196.728 bytes dan deviasi standar hanya **86,41 bytes**. Hal ini membuktikan bahwa arsitektur ring buffer 1.440 menit dan struktur TinyML C++ beroperasi bebas dari kebocoran memori progresif (*progressive memory leak*).
2. **Rekonsiliasi Telemetri Cloud:**
   - Total slot telemetri yang terbentang antara slot pertama dan slot terakhir adalah 27.226 slot (interval rata-rata 20,1 detik).
   - Jumlah feed yang berhasil diterima peladen Thingspeak adalah 27.022 baris, menghasilkan **kelengkapan slot (*slot completeness*) sebesar 99,25%**.
   - Dari sisi mikrokontroler, tercatat 27.135 percobaan transmisi dengan 118 kali kegagalan jaringan, menghasilkan **tingkat keberhasilan percobaan (*attempt success rate*) sebesar 99,57%**.
   - Sebanyak 91 slot berstatus *skipped* (tidak dicoba dikirim) saat mikrokontroler mendeteksi status Wi-Fi belum siap, sehingga menghindari pemborosan siklus komputasi (*blocking*).
3. **Cakupan Rerata 24 Jam:** Field status `d` mencatat *coverage* 100% setelah 24 jam pertama. Perlu dicatat secara metodologis bahwa angka "100" pada status diformat dalam 3 digit signifikan, yang mengindikasikan cakupan menit valid $\ge 99{,}95\%$, bukan ketiadaan mutlak sampel yang terlewat.

### 3.3 Analisis Kualitas Udara dan Dinamika Multi-Polutan

Rangkuman statistik parameter lingkungan dan estimasi model pada sesi utama ditunjukkan pada Tabel berikut:

| Parameter | Minimum | Rata-rata | Median | Maksimum | Standar Deviasi |
|---|---:|---:|---:|---:|---:|
| Suhu Ruangan (°C) | 22,20 | 25,92 | 25,40 | 31,50 | 1,98 |
| Kelembaban Relatif (% RH) | 39,50 | 55,52 | 55,70 | 75,50 | 7,01 |
| GP2Y Raw ADC | 937,87 | 1.033,07 | 1.021,94 | 4.095,00 | 58,12 |
| MQ-7 Raw ADC | 2.103,42 | 2.559,36 | 2.536,58 | 3.120,40 | 114,80 |
| MQ-135 Raw ADC | 1.179,41 | 1.616,25 | 1.597,60 | 3.403,95 | 243,10 |
| Estimasi PM2.5 ($\mu\text{g/m}^3$) | 20,46 | 33,80 | 30,67 | 80,25 | 5,82 |
| Estimasi CO ($\text{ppm}$) | 2,68 | 4,05 | 3,81 | 7,44 | 0,76 |
| ISPU Instan | 56,22 | 73,70 | 69,40 | 126,16 | 7,85 |
| Commanded Fan PWM (%) | 14,90 | 14,96 | 14,90 | 85,10 | 0,89 |

Distribusi kategori kualitas udara menunjukkan dominasi Kategori Sedang (ISPU 51–100) sebesar **99,33%** (26.842 sampel), diikuti Kategori Tidak Sehat (ISPU 101–200) sebesar **0,66%** (179 sampel) yang bertepatan dengan aktivitas pembakaran/asap di sekitar lingkungan hunian pada tanggal 11 dan 15 September. Perintah PWM kipas mencerminkan distribusi ini, dengan 99,17% waktu berada pada Level 2 (PWM 14,90%) dan 0,82% waktu berada pada Level 3 (PWM 21,96%).

### 3.4 Ketahanan Gangguan: Kasus Saturasi Optik 13 September 2026

Bukti empiris ketahanan sistem (*fail-safe operation*) teramati secara nyata pada tanggal **13 September 2026 pukul 02:13:06 WIB**. Pada stempel waktu tersebut, sensor optik GP2Y mengalami saturasi rel penuh (`ADC = 4095.00`):
1. **Deteksi Sesar:** Mikrokontroler mendeteksi pembacaan menyentuh batas rel maksimum ADC 12-bit dan mengaktifkan flag diagnostik bit `22930` ($16384 \text{ [GP mean jenuh]} + 4096 + 2048 + 256 + 128 \text{ [model invalid]} + 16 + 2$).
2. **Respon Proteksi:** Alih-alih menafsirkan angka 4095 sebagai lonjakan partikulat bernilai ekstrem ribuan $\mu\text{g/m}^3$, algoritma menandai status keluaran model sebagai tidak valid, menetapkan ISPU ke nilai `NaN`, mengosongkan kategori (`field8 = 0.0`), mematikan alarm polusi untuk mencegah alarm palsu (*false positive*), dan langsung menaikkan perintah kipas ke Level 5 darurat (`PWM = 85.10%`).
3. **Pemulihan Bertingkat (*Smooth Decay*):** Dua puluh detik kemudian (02:13:26 WIB), setelah pembacaan ADC GP2Y kembali ke rentang normal (986,48), sistem tidak langsung menjatuhkan kipas secara drastis, melainkan mengeksekusi penurunan bertahap ke Level 4 (`PWM = 50.20%`), sebelum akhirnya kembali ke Level 2 (`PWM = 14.90%`) pada 02:13:46 WIB. Mekanisme ini membuktikan keandalan algoritma histeresis dalam melindungi aktuator mekanis dan menjaga stabilitas sistem.

---

## 4. KESIMPULAN

Penelitian ini berhasil membuktikan bahwa komputasi *TinyML Random Forest* dan regulasi ISPU kontinu Permen LHK 14/2020 dapat diimplementasikan secara terpadu pada mikrokontroler berdaya rendah ESP32 untuk sistem pemantauan kualitas udara multi-polutan otonom. Pengujian operasional selama lebih dari 170 jam (7 hari penuh) di lingkungan hunian nyata mendemonstrasikan stabilitas memori tingkat tinggi (deviasi standar *heap* 86,41 bytes tanpa kebocoran progresif) dan keandalan telemetri cloud (kelengkapan slot 99,25%). Mekanisme *fail-safe* dan *smooth decay* terbukti secara empiris mampu menangani saturasi instrumen dan melindungi siklus hidup aktuator. Pengembangan di masa depan diarahkan pada kalibrasi gas terkendali (*gas chamber*) dengan instrumen acuan bersertifikat guna mentransformasikan estimasi nominal menjadi konsentrasi fisik berstandar metrologi.
