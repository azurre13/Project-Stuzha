# Firmware Stuzha v4.0.0 — TinyML, indeks dan kendali

Versi 9 September 2026. Target esp32dev, espressif32 6.12.0 / Arduino-ESP32 2.0.17. Build berhasil; upload dan uji perangkat fisik belum dilakukan. [Metode dan keputusan v4](../../MD/metode_ispu_v4.md) merupakan acuan metode aktif. V3.0/v3.1 menjadi arsip.

## Alur aktif

GP2Y + T/RH masuk model PM; MQ7 ADC + T/RH masuk model CO. Dua keluaran RF masuk interpolasi sub-indeks; maksimum menjadi indeks estimasi instan, kategori, dan masukan kipas. MQ135 tetap proksi gas campuran. Tidak ada baseline relatif per boot dalam kendali v4.

Header model_pm.h/model_co.h tetap identik. Pembungkus [experimental_models.h](include/experimental_models.h) mempertahankan kontrak fitur historis: PM_input=max(0,(0.17*GP_ADC*3.3/4095-0.1)*1000), T, RH; CO_input=MQ7_ADC,T,RH. Ini mempertahankan eksperimen lama, bukan menyatakan rumus sensor sudah terkalibrasi. Target CO model adalah mg/m3; tampilan ppm memakai kondisi acuan tetap 25 C/101325 Pa dan massa molar 28.01 g/mol. Perhitungan indeks CO langsung memakai mg/m3 dikali 1000 menjadi ug/m3.

PM dianggap ug/m3 **nominal menurut asumsi skala training legacy**, belum satuan fisik yang terverifikasi. Konflik metadata Mendeley ug/m3 versus target lama dikali 1000 tetap material; flag 4096 selalu aktif. Model CO transfer PT08-ke-MQ7 belum tervalidasi; flag 2048 selalu aktif. Jangan menyebut keduanya calibrated atau menganggap flag dapat memperbaiki model. Pipeline benchmark baru bukan pengganti header ini.

## Akuisisi

Pin tetap: GP Vo34/LED5, MQ7 32, MQ135 33, DHT4, fan19, buzzer18. ADC1 12 bit, attenuasi ADC_ATTEN_DB_12. Task ADC core1/prioritas4, target GP 100 Hz: LED LOW, mulai ADC sekitar 280 us, matikan LED sekitar 320 us. MQ dibaca sesudah pulsa. Statistik blok sekitar satu detik memuat mean, jumlah sampel, peak/rail dan deviasi timing. Perioda di luar 9–11 ms, ADC mulai >300 us atau pulsa >340 us ditandai. Timing ini observasi software, bukan verifikasi osiloskop.

Task jaringan core0 terpisah. DHT dicoba pada blok pertama, selanjutnya setiap dua detik; invalid tetap kosong/NaN. Tidak memakai angka pengganti 25 C/50% RH. Brownout detector aktif. Fan kanal LEDC0 25kHz/8bit; tone kanal15 terpisah. -mtext-section-literals menjaga jangkauan literal Xtensa pada kode model besar.

## Indeks, kategori dan kipas

[ispu_calc.h](include/ispu_calc.h) memakai titik kontinu Lampiran I Permen LHK 14/2020. PM ug/m3: 0,15.5,55.4,150.4,250.4,500; CO ug/m3: 0,4000,8000,15000,30000,45000. Titik indeks: 0,50,100,200,300,500. Konsentrasi negatif/NaN invalid. Di atas tabel: indeks dibatasi 500 dan flag 8192 dicatat. Perhitungan tidak memakai tabel CO 8-jam ppm dari arsip.

Kategori kode 1 Baik, 2 Sedang, 3 Tidak Sehat, 4 Sangat Tidak Sehat, 5 Berbahaya ditentukan dari indeks dibulatkan; 0 tidak tersedia. Nama kategori pada dashboard selalu dijelaskan sebagai **kategori estimasi model**, bukan pernyataan aman/berbahaya dari instrumen tervalidasi. Parameter kritis c: 1 PM, 2 CO, 3 sama, 0 tidak tersedia. Kedua kanal diperlukan untuk maksimum final; tidak mengisi kanal hilang dengan nol.

[ispu_control.h](include/ispu_control.h): kenaikan kategori perlu bertahan >=1 detik dengan blok berjarak <=2.5 detik. Penurunan satu tingkat setelah indeks <95% batas bawah level selama delapan detik. Jeda pemrosesan tidak dihitung sebagai dwell. Duty L1–L5: 33,38,56,128,217 (12.941%,14.902%,21.961%,50.196%,85.098%). Duty bukan RPM/dB/efisiensi.

Pemeriksaan stabilitas 9 September: kenaikan hanya sampai kategori terendah yang teramati selama jendela konfirmasi. Contoh L2 lalu satu sampel L5 menaikkan kipas ke L2; L5 membutuhkan konfirmasinya sendiri. Ini mencegah lonjakan baru memakai waktu tunggu kategori lebih rendah. Persentase PWM, model/DHT, tabel indeks, histeresis dan waktu turun tetap sama.

Jika tidak ada blok baru selama lebih dari 2,5 detik dan main loop masih berjalan, penjaga kesegaran meminta minimal L4, mempertahankan L5 jika sudah tinggi, mematikan alarm polusi dan menandai PROCESSING_STALE/MODEL_INVALID. Timestamp/sequence sampel terakhir dipertahankan; output model/indeks dikosongkan, kategori menjadi0. Blok yang sudah basi saat diterima juga tidak boleh mengendalikan kipas sebagai bacaan valid. Pemulihan setelah data kembali tetap bertahap. Penjaga ini tidak menangani CPU/main loop yang macet total atau mendeteksi kipas fisik berhenti.

ADC tinggi 4000 masih dapat diproses. Satu sampel menyentuh rel tidak membatalkan seluruh blok. Rerata GP >=4094 ditandai jenuh, meminta L5, dan tidak ditafsirkan sebagai PM tertentu. Model/input invalid meminta sedikitnya L4, indeks kosong/kategori0. Pada kedua keadaan tersebut alarm polusi diam. Setelah masukan valid pulih, penurunan tetap delapan detik per tingkat; dari L5 ke L1 sekitar 32–36 detik pada blok 1 detik. Jari menutup optik bukan pengukuran massa PM.

Buzzer memerlukan kategori valid saat ini >=4 dan level kipas >=4, berbunyi 100 ms maksimal sekali lima detik tanpa delay. Alarm berhenti saat kategori turun meskipun kipas masih melambat. Ini indikator prototipe berbasis model, bukan alarm CO tersertifikasi.

## Rerata 24 jam

[rolling_ispu.h](include/rolling_ispu.h) menyimpan 1440 bucket menit di RAM. Integrasi menggunakan nilai blok sebelumnya dan durasi antarblok, hanya untuk sela <=1.5 detik dengan kedua model valid. Sela panjang tidak diisi ulang. Setiap batas menit, 24 jam menit lengkap dihitung sebelum bucket tertua dibuang. Setelah umur boot minimal 24 jam dan durasi valid >=75% dari 24 jam, mean PM/CO serta indeks dari kedua mean tersedia di status d. Sebelumnya NaN dengan flag32768. Indeks ini tetap **estimasi model 24 jam**, bukan otomatis ISPU resmi. Reset menghapus ring; Wi-Fi putus tidak menghapus ring selama ESP32 berjalan.

## Delapan field STZ4

| Field | Nama yang disarankan | Arti |
|---|---|---|
| 1 | Temperature_C | T DHT |
| 2 | Relative_Humidity_percent | RH DHT |
| 3 | PM_Model_Nominal_ugm3 | Output RF dengan asumsi skala legacy yang belum terverifikasi |
| 4 | CO_Model_Nominal_ppm | Output RF mg/m3 dikonversi pada kondisi acuan tetap |
| 5 | ISPU_Estimasi_Instan | Maksimum sub-indeks dari blok terbaru, bukan rerata 24 jam |
| 6 | Fan_PWM_percent | Duty aktual |
| 7 | MQ135_Raw_ADC | Proksi gas campuran |
| 8 | Kategori_Estimasi_Code | 0 invalid, 1–5 kategori dari indeks, dapat berbeda dari level kipas selama dwell |

Status diawali STZ4|v=4.0.0, panjang diperiksa <256 byte. Raw GP/MQ7 tetap direkam di a, sehingga tidak hilang saat field5/8 kembali menjadi indeks/kategori. [telemetry_v4.h](include/telemetry_v4.h) pemilik format:

- v,h,m,b: versi, hash sumber12/model8, boot ID8.
- u,r,l,f,s: uptime blok ms64bit, reset reason, level kipas, flags, sequence.
- n,j,i: jumlah sampel blok, deviasi timing, gabungan latensi inferensi us (termasuk pembungkus validasi).
- e: attempts,failures,unattempted slots sebelum hasil kiriman ini; q slot cloud; k heap.
- a: GP ADC,MQ7 ADC (dua desimal).
- d: PM mean24,CO mean24 mg/m3,index24,coverage persen. Tiga digit signifikan untuk status; nilai internal tidak dibulatkan. Ring diperbarui per menit lengkap; endpoint minute-aligned dapat diturunkan dari u.
- c: parameter kritis instan.

Flags: 1 DHT invalid; 2/4/8 ada raw rail GP/MQ7/MQ135 (diagnostik, tidak otomatis kerusakan); 16 deviasi timing; 64 Wi-Fi offline saat akuisisi; 128 model invalid/tidak dihitung; 256 heater MQ7 belum diverifikasi; 512 jumlah sampel blok di luar90..110; 1024 snapshot basi>2.5s; 2048 transfer model belum valid; 4096 skala PM belum valid; 8192 di atas rentang tabel; 16384 GP mean jenuh; 32768 mean24 belum tersedia. Bit32 tidak digunakan v4. Flags dasar6400; sebelum24jam biasanya39168. Flags bukan pendeteksi semua kerusakan/domain shift.

## Operasi, build dan arsip

Cloud snapshot setiap sekitar20detik, bukan mean20detik atau rekaman semua transisi. Reconnect setiap10detik, client timeout3detik. Buffer panjang1, tidak ada persistent queue/replay. Unduh status asli, pisahkan STZ3/STZ31/STZ4; tidak boleh mengubah arti arsip lewat rename kolom. CSV/data/model asli dipertahankan.

Dari Program/Kode: pio run; pio device list; pio run --target upload --upload-port COMx. Identitas di .pio/build_manifest.json, include/build_info.h otomatis. secrets.h dan binari lokal diabaikan Git. Binari berisi konfigurasi lokal, jangan dipublikasikan. [Protokol](../../MD/protokol_pengambilan_data_7_hari.md) memisahkan uji fungsi singkat dari observasi tujuh hari.

Build setelah pemeriksaan stabilitas: `5f1eb11d9548`. Tes C++ dan13tes Python lulus, build ESP32 berhasil (flash1105593byte, RAM statis80080byte). [Verifikasi terkini](../../MD/verifikasi_revisi_v4.json) menyimpan hash dan lokasi binari privat. Port COM3 terdeteksi, tetapi upload/uji fisik belum dilakukan pada revisi ini.
