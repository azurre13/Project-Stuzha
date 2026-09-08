# Hardware Stuzha

Dokumentasi rakitan prototipe monitoring indoor. Acuan kondisi aktual adalah penjelasan pemilik pada 8 September 2026. Spesifikasi yang belum diukur ditandai sebagai pekerjaan terbuka.

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
