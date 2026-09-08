# Firmware prototipe monitoring Stuzha

Dokumentasi implementasi yang ada pada 8 September 2026. Pada rangkaian pembaruan ini, komentar sensor firmware diperjelas; logika pembacaan dan kontrol tidak diubah. Tidak ada upload/flash atau validasi hardware baru.

## Target dan identitas perangkat

[platformio.ini](platformio.ini) menggunakan environment dan board `esp32dev`, framework Arduino, serta port COM3. Sebutan ESP32-S3 di komentar/banner kode belum dikonfirmasi pada board fisik.

Pemilik telah mengonfirmasi **MQ-7 untuk CO** dan **MQ-135 sebagai indikator/proksi VOC atau gas campuran**. Kode membaca MQ-7 melalui `PIN_MQ7_ANALOG` (GPIO 32) dan MQ-135 melalui `PIN_MQ135_ANALOG` (GPIO 33), sesuai identitas tersebut. MQ-7 berada di intake sebelum filter. Dokumentasikan wiring serta varian board; pin yang didefinisikan kode tercantum di [Hardware](../../Hardware/hardware_stuzha.md).

Pemilik menilai pin saat ini sudah benar. Pertahankan pemetaan tersebut; pemeriksaan ini belum menemukan bukti kesalahan pin. Jangan mengganti pin hanya untuk mengikuti sebutan board pada komentar lama. Varian board masih perlu dicatat, tetapi hal itu tidak membatalkan keterangan pemilik tentang pin.

## Struktur dan fungsi

| Berkas | Fungsi saat ini |
|---|---|
| [src/main.cpp](src/main.cpp) | Pembacaan sensor, inferensi, indeks sesaat, PWM, alarm, serial, IoT |
| [include/pin_config.h](include/pin_config.h) | Pin, asumsi ADC, dan PWM |
| [include/model_pm.h](include/model_pm.h) | Model PM dari eksperimen data sintetis |
| [include/model_co.h](include/model_co.h) | Model CO dari benchmark UCI |
| [include/ispu_calc.h](include/ispu_calc.h) | Interpolasi indeks; kesesuaian ISPU masih perlu diperbaiki |
| [legacy/](legacy/arsip_legacy.md) | Arsip implementasi sebelumnya; bukan konfigurasi sensor saat ini |

Model menggunakan 30 pohon dengan kedalaman maksimum 8. Training dilakukan di komputer; fungsi C digunakan untuk inferensi lokal.

### API model

- `model_pm_predict(const float *features)`: input [estimasi debu dari ADC, suhu, RH].
- `model_co_predict(const float *features)`: input [ADC sensor gas utama, suhu, RH].

Keluaran adalah estimasi eksperimental, belum konsentrasi tervalidasi pada perangkat. Label `pm25_calibrated` dan `co_calibrated` dipertahankan dalam kode lama. Target CO UCI bersatuan mg/m³, sementara kode memberi label ppm; kesalahan satuan ini belum diperbaiki. Lihat [evaluasi ML](../../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md).

### API indeks

- `hitung_ispu_pm25(float)`
- `hitung_ispu_co(float)`
- `get_kategori_ispu(int)`

Kode mengambil maksimum dua sub-indeks. Perhitungan dilakukan dari output sesaat, tanpa perataan 24 jam. Tabel CO saat ini memakai batas 4,4; 9,4; 15,4; 30,4; 50,0 dengan label ppm. Ini belum sesuai acuan ISPU yang dipilih proyek. Koreksi satuan, tabel, interpolasi batas, perataan, dan penamaan output merupakan pekerjaan terbuka.

## Kendali kipas

PWM dikonfigurasi 25 kHz dengan resolusi 8 bit.

| Label kategori pada kode | Nilai PWM | Persen yang dilaporkan |
|---|---:|---:|
| Baik | 33 | 13% |
| Sedang | 38 | 15% |
| Tidak Sehat | 56 | 22% |
| Sangat Tidak Sehat | 128 | 50% |
| Berbahaya | 217 | 85% |

Persen merupakan perintah kontrol, bukan pengukuran putaran, daya, atau airflow. Alarm dipanggil pada dua kategori tertinggi. Deadband turun diterapkan di sekitar batas 50, 100, dan 200; batas 300 belum memiliki deadband serupa. Tidak ada syarat durasi stabil yang eksplisit.

MQ-135 dibaca ke `raw_voc_adc` dan dikirim ke field 7 ThingSpeak. Jalur ini memantau respons/proksi VOC atau gas campuran dalam satuan ADC, bukan konsentrasi VOC/TVOC terkalibrasi. MQ-135 tidak menjadi input model CO, sub-indeks ISPU, atau penentu PWM pada kode saat ini. Fitur booster saat ADC >2.500 dalam roadmap lama **belum diimplementasikan**. Ambang tersebut juga belum tervalidasi sebagai batas kesehatan.

## Telemetri

Pembacaan dijadwalkan sekitar satu detik; pengiriman cloud sekitar 20 detik. Operasi jaringan dan fungsi alarm dapat memengaruhi interval aktual.

| Field ThingSpeak | Isi kode saat ini | Interpretasi |
|---|---|---|
| 1 | Suhu | Pembacaan DHT atau nilai pengganti jika gagal |
| 2 | RH | Pembacaan DHT atau nilai pengganti jika gagal |
| 3 | PM calibrated | Output model; akurasi dan skala belum tervalidasi |
| 4 | CO calibrated ppm | Output model; ada ketidaksesuaian satuan |
| 5 | ISPU final | Indeks sesaat implementasi, belum pelaporan resmi |
| 6 | PWM persen | Perintah kipas |
| 7 | Raw VOC ADC | Pembacaan MQ-135, bukan konsentrasi VOC terkalibrasi |
| 8 | Kode kategori | Turunan field 5 |

Status feed berisi kategori dan parameter dominan menurut perhitungan kode. CSV downloader saat ini tidak menyertakan status feed.

Serial mencetak suhu/RH, estimasi PM sebelum dan sesudah ML, raw ADC gas utama, output model gas, indeks, dominan, serta PWM. Serial belum menyertakan raw ADC GP2Y, flag validitas, uptime/reset, dan versi model dalam setiap rekaman.

## Masalah terbuka

1. Identitas MQ-7/MQ-135 telah dikonfirmasi; dokumentasikan wiring keduanya dan cocokkan part number GP2Y serta varian board dengan rakitan.
2. Simpan raw ADC, flag sensor gagal, uptime, reset, dan versi firmware/model.
3. DHT gagal saat ini diganti 25°C/50% RH tanpa penanda; jangan anggap nilai pengganti sebagai pengukuran.
4. Brownout detector dimatikan saat startup. Periksa catu daya dan strategi deteksi gangguan sebelum menyatakan stabilitas perangkat.
5. Telusuri PM yang menetap rendah dan lonjakan; jangan menghapus kejadian hanya agar grafik halus.
6. Verifikasi ADC/tegangan, timing GP2Y, kebutuhan heater sensor gas, dan pengaruh aliran kipas.
7. Benahi indeks dan kendali sesuai ruang lingkup monitoring.
8. Ukur latensi, penggunaan memori saat runtime, serta keterlambatan akibat jaringan/alarm.
9. Kode mencoba reconnect dan dapat melanjutkan loop lokal tanpa WiFi; pemulihan nyata perlu diuji. Tidak ada antrean persisten untuk mengirim ulang data selama offline.
10. Pisahkan konfigurasi kredensial lokal dari dokumentasi/publikasi.

## Build dan upload

Gunakan PlatformIO, periksa target board dan port yang benar, lalu dari folder ini:

```sh
pio run
pio device monitor
```

Perintah upload setelah konfigurasi sesuai perangkat:

```sh
pio run --target upload
```

Build berhasil tidak membuktikan wiring benar atau sensor terkalibrasi. Simpan salinan firmware pengujian dan tandai sesi baru setelah perubahan.
