# Hardware Stuzha

Dokumentasi rakitan prototipe monitoring indoor. Fakta pemilik dikonfirmasi 8 September 2026; dokumentasi diperbarui 9 September 2026. Spesifikasi yang belum diukur tetap ditandai sebagai pekerjaan lapangan.

## Casing dan susunan aliran

Casing menggunakan gabus keras. Intake di bawah dan exhaust di atas. Kipas berukuran 12 × 12 cm. Dimensi luar casing, ketebalan bahan, dan luas bukaan efektif belum dicatat.

```text
                    EXHAUST ATAS
                         ↑
                KIPAS 12 × 12 cm
                         ↑
             RUANG KOSONG sekitar 5 cm
                         ↑
             FILTER MOBIL YANG DIPOTONG
                         ↑
               FILTER KARBON KOTAK
                         ↑
       AREA INTAKE / SENSOR SEBELUM FILTER
       GP2Y: lubang menghadap horizontal
       MQ-7: tegak di dinding bawah
                         ↑
                    INTAKE BAWAH
```

Diagram menunjukkan urutan aliran yang dijelaskan pemilik, bukan gambar berdimensi. Filter bukan HEPA. Jenis, merek, kelas, ketebalan, dan ukuran potongan filter mobil belum diketahui. Ruang 5 cm merupakan celah/ruang aliran sebelum kipas; kondisi tekanan vakum belum diukur.

Filter dan kipas mendukung prototipe. Efisiensi penyaringan, CADR, distribusi udara ruangan, kebocoran antarfilter, penghilangan gas, kebisingan, dan konsumsi daya belum divalidasi. Jangan menghitung RPM aktual hanya dengan mengalikan duty cycle terhadap RPM maksimum atau menyamakan CFM dengan CADR.

## Komponen dan identitas

| Komponen | Keterangan tersedia | Tindak lanjut |
|---|---|---|
| Board ESP32 | PlatformIO memakai `esp32dev`; dokumen lama menyebut S3 | Foto marking board/modul dan catat varian sebenarnya |
| GP2Y | Dokumentasi lama menyebut GP2Y1010AU0F; lubang horizontal di intake menurut pemilik | Cocokkan part number fisik dan wiring |
| MQ-7 | Dikonfirmasi pemilik untuk CO, tegak di dinding bawah sebelum filter | Dokumentasikan marking, wiring, dan kebutuhan pemanasan |
| MQ-135 | Dikonfirmasi pemilik sebagai indikator/proksi VOC atau gas campuran | Dokumentasikan posisi aktual dan wiring; output saat ini ADC mentah |
| DHT22 | Ada pada dokumentasi dan firmware | Catat posisi relatif terhadap AC, sensor gas, dan kipas |
| Kipas | Ukuran 12 × 12 cm dikonfirmasi pemilik | Foto label dan catat konektor/driver |
| Spesifikasi kipas lama | Tercatat 12 V, 1,65 A, tebal 38 mm, sekitar 6.200–6.400 RPM | Verifikasi label/datasheet; bukan hasil pengukuran alat |
| Media filter | Karbon kotak dan filter mobil dipotong, bukan HEPA | Catat ukuran, label, pemasangan dan sealing |

Belum tersedia instrumen pembanding kualitas udara. Penempatan sebelum filter tidak menjamin pembacaan bebas pengaruh kipas; variasi aliran dan panas komponen perlu diperiksa melalui raw sensor.

## Wiring dalam kode saat ini

Tabel menyalin [pin_config.h](../Program/Kode/include/pin_config.h). Pada 8 September 2026, pemilik menyatakan pin seharusnya sudah benar. Pemetaan ini dipertahankan sebagai konfigurasi kerja dan tidak dicatat sebagai kesalahan yang ditemukan. Verifikasi wiring independen belum dilakukan; varian board yang belum terdokumentasi merupakan hal terpisah.

| Nama pada kode | GPIO |
|---|---:|
| `PIN_MQ7_ANALOG` | 32 |
| `PIN_MQ135_ANALOG` | 33 |
| `PIN_DUST_VO` | 34 |
| `PIN_DUST_ILED` | 5 |
| `PIN_DHT22` | 4 |
| `PIN_FAN_PWM` | 19 |
| `PIN_BUZZER` | 18 |

Sebelum perubahan wiring/firmware, cocokkan board, rentang input ADC, pembagi tegangan, catu daya, dan jenis driver kipas. Identitas MQ-7 dan MQ-135 telah dikonfirmasi pemilik. Verifikasi kebutuhan pemanasan dan pembacaan menurut datasheet masing-masing sensor. Respons MQ-135 dipakai sebagai proksi VOC/gas campuran; ADC mentah belum menunjukkan konsentrasi VOC dalam ppm atau TVOC dalam µg/m³.

## Foto arsip

### Prototipe tampak samping

![Foto prototipe](foto_alat/prototipe_fisik_tampak_samping.png)

### Modul sensor debu

![Foto modul sensor debu](foto_alat/sensor_gp2y1010_modul.png)

Foto arsip belum menggantikan konfirmasi setiap label komponen dan konfigurasi terkini.

## Dokumentasi yang perlu dilengkapi

- Foto keseluruhan dan bagian dalam: urutan filter serta ruang 5 cm.
- Ukuran casing, bukaan, filter, dan posisi sensor relatif terhadap lantai/AC.
- Foto marking sensor, board, kipas, catu daya, dan driver.
- Skematik aktual, termasuk pembagi tegangan dan jalur daya.
- Catatan perubahan rakitan, tanggal, dan versi firmware.

Diagram CAD/skematik terpisah belum tersedia dalam inventaris berkas yang diperiksa. Blueprint dan skematik pada dokumen lama masih berupa rencana.

## Daya dan pengoperasian sensor: klarifikasi terbaru

Pemilik menyatakan adaptor 12 V terhubung ke kipas dan expansion ESP32; expansion menyediakan jalur 5 V untuk ESP32/modul. Selama studi hanya ESP32 dan Wi-Fi menyala. Diagram berikut adalah alur yang diceritakan pemilik, bukan skematik elektronik yang telah diperiksa:

```text
Adaptor 12 V -> kipas
            -> input expansion ESP32 -> jalur 5 V ke board/modul
```

Tipe regulator expansion, kapasitas arus, tegangan aktual, ground bersama dan pembagi tegangan ADC belum diukur dalam revisi software ini. Pemetaan pin tetap sesuai konfirmasi. Jalur suplai sensor 5 V tidak berarti input analog ESP32 boleh diberi 5 V langsung; attenuasi ADC memperluas rentang ukur, bukan proteksi tegangan. Periksa rangkaian/pembagi tegangan aktual sebelum menilai data saturasi. Jangan memindah pin berdasarkan dugaan.

- **GP2Y1010AU0F:** firmware v3 menargetkan pulsa 10 ms, sampling sekitar 280 us, lebar 320 us; menyimpan deviasi timing dan rail ADC. Acuan [datasheet](https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y1010au_e.pdf) serta [application note](https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y1010au_appl_e.pdf). Orientasi konektor, cahaya luar, rangkaian LED dan komponen RC perlu dicocokkan dengan foto/rangkaian. Tidak ada perubahan wiring oleh AI.
- **MQ-7:** suplai 5 V yang disebut pemilik belum membuktikan siklus heater. [Manual MQ-7 Winsen v1.3](https://cdn.sparkfun.com/datasheets/Sensors/Biometric/MQ-7%20Ver1.3%20-%20Manual.pdf) menetapkan fase tinggi 5 V/60 s dan rendah 1,5 V/90 s. Model/modul aktual perlu dicocokkan. Firmware v3 tidak mengendalikan heater melalui GPIO baru; mencatat ADC dan flag heater-unverified. Pada v4 keluaran RF ditampilkan sebagai estimasi model CO eksperimental dengan target nominal mg/m3 dan konversi tampilan ppm pada25C/1atm; ini tidak memvalidasi heater atau konsentrasi CO ruangan.
- **MQ-135:** [manual Winsen v1.6](https://www.winsen-sensor.com/d/files/manual/mq135.pdf) menjelaskan respons terhadap beberapa gas, termasuk amonia dan uap kelompok benzena. Suplai heater 5 V tidak membuat sensor selektif TVOC. Pembacaan tetap respons gas campuran/proksi VOC dalam ADC.
- Manual MQ yang dirujuk memberi kondisi pemanasan awal lebih dari 48 jam. Catat riwayat sensor menyala/padam dan kondisi penyimpanan. Jangan menyebut baseline model pada arsip v3.1 sebagai pengganti pemanasan sensor gas atau kalibrasi gas.
- **DHT22:** tetap sensor suhu/RH; setpoint AC 24–27 C bukan nilai referensi suhu di posisi DHT.

Firmware v3 menjaga brownout detector aktif, menandai ADC rail, dan memisahkan kanal buzzer/kipas. Perubahan ini membantu diagnosis; belum membuktikan catu daya atau pulsa fisik telah lolos pengukuran. Tindak lanjut lapangan tercantum pada [protokol](../MD/protokol_pengambilan_data_7_hari.md).
