# Data penelitian Stuzha

Revisi 8 September 2026. Dataset perangkat, dataset publik, dan simulasi memiliki peran berbeda. CSV asli tidak diubah oleh revisi ini.

## Sesi historis

[CSV lokal terakhir](Dataset_Project_Stuzha_ThingSpeak_Lengkap.csv) diperiksa dengan analyze_session.py:

- 1.389 baris, 8 September 2026 13:14:07–21:17:50 WIB; durasi 8 jam 3 menit 43 detik.
- Interval median 20 detik, minimum 19 detik, maksimum 1.279 detik.
- Gap ID 1195–1196: 19:52:10–20:13:29 WIB. Pemilik menyatakan router mati.
- SHA256: 3fe753182a059ee0f6e4c76912dba3009be4e81b07bfb0cd7199fc9cfee8b7ee.
- Data ini memakai label lama, bukan format v3; tidak memiliki raw GP/MQ7 dan identitas boot.

[Arsip sesi 18 jam](backup/Dataset_Project_Stuzha_ThingSpeak_Sesi1_18Jam_Sept5-6.csv) menyimpan sesi sebelumnya. Statistik terdahulu 3.126 baris/17 jam 22 menit 22 detik dan PM menetap 0,00031 pada 84,39% baris adalah catatan sesi tersebut, bukan ringkasan CSV terakhir. Tidak boleh menafsirkan nilai model yang rendah sebagai udara bebas partikel.

Kolom historis PM25_Calibrated_ug_m3, CO_Calibrated_ppm dan ISPU_Final merupakan nama lama; tidak membuktikan kalibrasi/satuan benar. Field MQ135 merupakan ADC/proksi gas campuran. Pertahankan data historis untuk uji pendahuluan.

## Sesi v3.0, v3.1 dan v4

Pemetaan field dan status ada pada [firmware](../Kode/firmware_stuzha.md). CSV downloader baru menggunakan Timestamp_UTC, Timestamp_WIB (offset eksplisit), Entry_ID, Schema, field1..field8 dan Status_Raw. Tidak mengubah angka menjadi konsentrasi atau kategori.

Schema stuzha_v4 ditentukan dari STZ4|: field3 PM nominal, field4 CO nominal ppm, field5 indeks instan, field8 kode kategori. Raw GP/MQ7 berada pada status a; d berisi mean24/indeks24/coverage. Nama dan satuan nominal tidak memvalidasi konsentrasi fisik. Schema stuzha_v3 ditentukan dari STZ3|, stuzha_v31 dari STZ31|. Selain itu diberi legacy_or_unknown. Pada v3.1 field 3/4 adalah keluaran model eksperimental, field 5/7/8 raw GP/MQ135/MQ7, dan sequence/flags di status. Pada v3.0 field 3/4 masih raw dan field 5/8 sequence/flags. ID cloud bisa diulang setelah channel dibersihkan; jangan membersihkan channel di tengah studi. Data beda sesi/channel harus diberi identitas terpisah. Satu folder unduhan dapat memuat beberapa versi; analisis harus memisahkannya.

## Download tanpa menimpa arsip

Dari root proyek, menggunakan Python 3.10+:

```sh
python Program/download_thingspeak_dataset.py --start 2026-09-08 --end 2026-09-15
```

Tanggal tersebut hanya contoh; sesuaikan awal/akhir eksperimen. Tanpa timezone berarti WIB. --end berupa tanggal mencakup sampai 23:59:59 WIB; untuk tepat 168 jam gunakan tanggal/jam eksplisit. Tanpa --start, awal query memakai tanggal pembuatan channel. Default output adalah snapshot baru bertimestamp di Program/data/downloads/.

Pilihan --channel, --start, --end, --window-hours, --output, --api-key tersedia melalui --help. Read key bisa diberikan melalui THINGSPEAK_READ_API_KEY agar tidak ditulis pada command history. File output eksplisit yang sudah ada dibackup sebelum atomic replace; --no-backup hanya bila benar-benar menghendaki penggantian tanpa backup.

Downloader meminta status=true, memakai UTC, window tumpang tindih dan deduplikasi ID. Window penuh pada batas 8.000 dipecah dan kedua bagiannya diunduh ulang. Kegagalan request dicoba terbatas lalu menggagalkan seluruh unduhan; tidak disamarkan sebagai window kosong. Metadata/timestamp tidak valid juga menggagalkan operasi. Tidak ada klaim bahwa semua sampel perangkat telah terkirim hanya karena semua window cloud berhasil dibaca.

## Analisis untuk Bab 3

```sh
python Program/analyze_session.py Program/data/downloads/NAMA_FILE.csv --require-v4 --output HASIL_BARU.json
```

Output JSON baru tidak menimpa file yang ada. Laporan menghitung durasi observasi, interval/gap, ID duplikat, format rusak, build/boot, flags, tingkat kipas, monotonisitas sampel/uptime/slot, cakupan slot cloud yang teramati, heap dan latensi inferensi yang tersampel. Sumber tidak diubah. --require-v3 menerima keluarga format v3 yang dapat dibaca; --require-v31 menuntut hanya v3.1; --require-v4 dipakai untuk sesi baru dan menuntut hanya v4. Analyzer memisahkan schema/build/boot dan menolak kombinasi versi/status yang belum didukung. Kolom Schema CSV hanya petunjuk; status asli menentukan decoder.

Cakupan slot per boot = jumlah slot unik diterima / (slot terakhir - slot pertama + 1). Ini bukan packet-loss jaringan dan tidak mencakup waktu sebelum/di luar observasi. Awal/akhir tujuh hari tetap dicatat dalam logbook. Data yang tak pernah sampai ke cloud tidak dapat direkonstruksi. Reset ketika seluruh periode offline bisa tidak terlihat.

## Dataset publik

- Mendeley, Sonawani & Patil (2022): [metadata](https://data.mendeley.com/datasets/2r232jpfb2/1), berkas mendeley/Indoor_Air_Pollution_Data.csv. Metadata PM menyebut ug/m3, skrip lama mengasumsikan mg/m3. Konflik belum terselesaikan; pipeline simulasi baru mempertahankan angka asli tanpa x1000, dengan unit fisik unresolved. Sensor serupa tidak membuatnya ground truth perangkat Stuzha.
- UCI Air Quality: [metadata](https://archive.ics.uci.edu/dataset/360/air+quality), berkas uci/AirQualityUCI.csv. CO(GT) reference analyzer mg/m3; PT08.S1 bukan MQ7 ADC. Sentinel -200 missing. Pipeline baru tidak memetakan PT08 ke ADC ESP32.

Lihat [training](../../ml_training/training_ml_stuzha.md) dan [evaluasi](../../Fase_1_Evaluasi_ML/evaluasi_ml_stuzha.md). Jangan menggunakan model sendiri sebagai ground truth kalibrasi baru.
