# Dataset Stuzha

Folder ini memuat rekaman prototipe dan dataset publik untuk eksperimen model. Ketiganya memiliki peran berbeda; dataset publik bukan ground truth bagi perangkat Stuzha secara otomatis.

## Rekaman kamar

Berkas: [Dataset_Project_Stuzha_ThingSpeak_Lengkap.csv](Dataset_Project_Stuzha_ThingSpeak_Lengkap.csv).

Ringkasan pemeriksaan 8 September 2026 atas snapshot lokal:

| Aspek | Hasil |
|---|---|
| Kondisi menurut pemilik | Kamar, AC disetel 24–27°C, tanpa alat pembanding |
| Periode WIB | 6 September 2026, 01.00.11–18.22.33 |
| Durasi tercatat | 17 jam 22 menit 22 detik |
| Baris | 3.126 |
| ID | 1–3.126, berurutan, tanpa duplikat |
| Kolom kosong / timestamp duplikat | Tidak ditemukan |
| Interval | Umumnya 20 detik; dua jeda >30 detik sebesar 40 dan 32 detik |
| Suhu sensor | 22,8–29,1°C; rata-rata 26,16°C |
| RH | 46,8–72,3%; rata-rata 61,72% |
| PWM terekam | 13%: 2.725; 15%: 398; 50%: 1; 85%: 2 baris |
| Perubahan PWM antarrekaman | 26 |

Setelan AC berbeda dari pengukuran suhu di titik sensor. Tidak adanya jeda panjang tidak membuktikan uptime tanpa reset. PWM 22% tidak terlihat dalam log; kejadian di antara snapshot 20 detik tidak dapat dikesampingkan.

### Pola yang perlu ditelusuri

- Output PM persis 0,00031 pada 2.638 baris (84,39%).
- Rangkaian terpanjang pada nilai tersebut: 878 baris, 13.28.58–18.21.32 WIB.
- Lonjakan PM pada 10.41.36: 372,61343; pada 13.28.38: 373,28568; pada 18.21.52: 189,25754. Rekaman berikutnya kembali rendah.
- Ada 25 baris MQ-135 ADC >2.500, dengan PWM 13–15%. Kode saat ini belum memiliki booster yang disebut roadmap lama.

Nilai di atas adalah keluaran implementasi, bukan konsentrasi referensi. Penyebab pola dapat berasal dari lingkungan, pembacaan, atau model dan belum diketahui. Penurunan dalam satu interval tidak membuktikan waktu pembersihan purifier.

### Arti kolom

Timestamp UTC/WIB menunjukkan waktu feed. Entry_ID adalah ID cloud. Suhu/RH berasal dari firmware, termasuk kemungkinan fallback tanpa flag. Kolom PM25_Calibrated_ug_m3 dan CO_Calibrated_ppm memakai label lama; status validasi dan satuan harus dijelaskan ketika dianalisis. Jalur gas utama menggunakan MQ-7 untuk CO. ISPU_Final dan kategori merupakan hasil hitungan firmware. Kipas_PWM_Persen adalah perintah. Raw_VOC_ADC adalah respons analog MQ-135 untuk indikator/proksi VOC atau gas campuran, bukan konsentrasi VOC/TVOC terkalibrasi. MQ-7 dan MQ-135 telah dikonfirmasi pemilik.

CSV belum memuat raw ADC GP2Y dan sensor gas utama, flag kegagalan, uptime/reset, versi firmware/model, serta catatan aktivitas/AC. Karena itu, koreksi model berikutnya tidak dapat diterapkan ulang secara andal ke seluruh rekaman ini. Simpan sebagai uji pendahuluan, dengan data asli tetap utuh.

## Dataset publik

### Mendeley — Indoor Air Pollutants

- Penulis: Shilpa Sonawani dan Kailas Patil; versi 1, 2022.
- [Sumber dan metadata](https://data.mendeley.com/datasets/2r232jpfb2/1), DOI 10.17632/2r232jpfb2.1.
- Lokasi lokal: `mendeley/Indoor_Air_Pollution_Data.csv`.
- Metadata: 173.468 rekaman, November 2020–Juli 2022; GP2Y1010AU0F dan sensor lingkungan BME280.
- PM pada metadata bersatuan µg/m³. Skrip lokal mengasumsikan mg/m³ dan mengalikan 1.000. Perbedaan ini harus ditelusuri ke sumber sebelum skala dipakai untuk klaim fisik.
- Data PM berasal dari sensor berbiaya rendah; tidak tersedia pasangan instrumen referensi independen dalam kolom yang dipakai skrip.
- Fungsi saat ini: sumber target untuk eksperimen PM sintetis, bukan validasi kalibrasi GP2Y Stuzha.

### UCI — Air Quality

- [Sumber dan metadata](https://archive.ics.uci.edu/dataset/360/air+quality), DOI 10.24432/C59K5F.
- Lokasi lokal: `uci/AirQualityUCI.csv`, XLSX, dan ZIP.
- Metadata menyebut 9.358 instance. Jumlah baris yang dibaca/valid setelah pembersihan harus dilaporkan dari berkas yang digunakan.
- Kolom relevan: CO(GT), PT08.S1(CO), T, RH; sentinel -200 menandakan data hilang.
- CO(GT) adalah konsentrasi rerata per jam dari reference analyzer dalam mg/m³. PT08.S1(CO) adalah respons sensor tin oxide.
- Pemetaan PT08.S1(CO) ke 800–3.600 tidak membuktikan kesetaraan dengan ADC MQ-7 pada Stuzha.
- Fungsi: benchmark model pada dataset UCI, bukan bukti akurasi sensor Stuzha.

## Skrip Pengunduh Telemetri (Downloader)

Skrip: [download_thingspeak_dataset.py](../download_thingspeak_dataset.py)

Skrip ini mengunduh rekaman telemetri dari ThingSpeak (Channel `3480764`), mengonversinya ke Waktu Indonesia Barat (WIB), dan menyimpannya dalam format CSV standar ilmiah.

### Status Implementasi (Diperbarui 8 September 2026)
- **Time-Windowing Pagination**: Batasan limit MathWorks 8.000 baris telah diatasi menggunakan metode *sliding window* berbasis waktu UTC (`start` dan `end`). Skrip mampu menarik data jangka panjang (>30.000 baris untuk periode 7 hari ke atas) tanpa terpotong.
- **Proteksi Data Historis (Auto-Backup)**: Skrip otomatis membuat salinan cadangan bertanggal di folder `Program/data/backup/` sebelum memperbarui file utama, sehingga data sesi sebelumnya tidak akan hilang tertimpa.
- **Atomic File Write**: Data ditulis ke berkas sementara `.tmp` terlebih dahulu, memastikan file CSV tidak akan rusak/korup jika koneksi terputus di tengah jalan.
- **Deduplikasi**: Pengecekan `entry_id` memastikan data tidak memiliki rekaman ganda di batas jendela waktu.

### Cara Penggunaan

1. **Unduh Otomatis Seluruh Rekaman (Default)**:
   ```bash
   python Program/download_thingspeak_dataset.py
   ```
   *Mengecek status channel, menarik seluruh data yang ada, dan menyimpannya ke `Program/data/Dataset_Project_Stuzha_ThingSpeak_Lengkap.csv`.*

2. **Unduh dengan Filter Tanggal Tertentu**:
   ```bash
   # Contoh: hanya dari tanggal 8 September 2026 ke atas
   python Program/download_thingspeak_dataset.py --start 2026-09-08

   # Contoh: rentang tanggal spesifik (WIB)
   python Program/download_thingspeak_dataset.py --start 2026-09-08 --end 2026-09-10
   ```

3. **Simpan ke File Berbeda (Tanpa Mengubah File Utama)**:
   ```bash
   python Program/download_thingspeak_dataset.py --output "Program/data/Dataset_Uji_Sesi2.csv"
   ```

4. **Daftar Opsi CLI**:
   - `--channel`: ID Channel ThingSpeak (default: `3480764`).
   - `--api-key`: Read API Key (kosongkan jika channel public).
   - `--start`: Waktu awal dalam format `YYYY-MM-DD` atau ISO.
   - `--end`: Waktu akhir dalam format `YYYY-MM-DD` atau ISO.
   - `--window-hours`: Ukuran jendela waktu per batch (default: `24` jam).
   - `--output`: Lokasi file keluaran CSV.
   - `--no-backup`: Lewati pembuatan file backup cadangan.

## Format pengambilan berikutnya

Tambahkan raw ADC seluruh sensor analog, suhu/RH beserta flag, output model, perintah PWM, uptime/reset, dan identitas firmware/model. Catat kondisi kamar, posisi alat, perubahan AC, aktivitas, awal/akhir sesi, serta perubahan hardware.

Pisahkan sesi sebelum dan setelah perubahan firmware. Simpan log lokal saat offline; keberhasilan monitoring lokal berbeda dari keberhasilan upload cloud. Data prediksi model sendiri tidak boleh diperlakukan sebagai ground truth kalibrasi baru.
