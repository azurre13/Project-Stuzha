# Protokol pengambilan tujuh hari — v4.0

9 September 2026. Tujuan tetap prototipe low-cost dengan dua RF, estimasi PM/CO, maksimum sub-indeks/kategori dan kipas. Tidak memerlukan PC logger atau pembelian alat pembanding. [Metode v4](metode_ispu_v4.md) dan [firmware](../Program/Kode/firmware_stuzha.md) menetapkan arti angka dan parameter.

## 1. Status yang perlu dibedakan

Kode/build/tes software bukan upload, uji fisik atau bukti akurasi. Kedua header RF tetap historis: PM skala nominal legacy belum terverifikasi dan transfer MQ7 belum tervalidasi. Observasi tujuh hari dapat mengevaluasi operasi/pola model, tetapi tidak mengubah ketidakpastian tersebut menjadi bukti kalibrasi.

## 2. Sekali sebelum mulai

Simpan manifest/binari yang akan dipasang. Hubungkan ESP32 sesaat untuk upload melalui port yang terdeteksi; perintah ada di dokumentasi firmware. Cocokkan status STZ4|v=4.0.0 dan hash h dengan manifest. Revisi ini belum mengunggah karena port belum terdeteksi. Tidak perlu upload/training harian setelah versi dibekukan.

Catat posisi/dimensi kamar, jarak terhadap AC, orientasi sensor, kondisi filter, catu daya dan jam mulai. Pin tetap sesuai pemilik. Foto/riwayat rakitan membantu penulisan; jangan mengarang R0, pembagi tegangan, siklus heater atau konsentrasi referensi. Suplai5V belum membuktikan heater MQ7 bersiklus.

Sesuaikan delapan label dashboard dengan tabel firmware. Field5 adalah ISPU_Estimasi_Instan dan field8 kategori estimasi; raw GP/MQ7 ada di status a. Caption harus menyatakan keluaran model belum terkalibrasi dan indeks instan berbeda dari rerata24jam. Jangan menghapus feed lama; pisahkan rentang STZ3/STZ31/STZ4.

## 3. Pemeriksaan fungsi singkat

Gunakan jaringan normal selama sedikitnya15menit sebelum t0 final. Pastikan kipas berputar, data T/RH tersedia, dua keluaran model dan indeks terbaca, raw ADC tidak mentok berkepanjangan, boot tetap sama dan tidak ada gangguan sampling. Pemeriksaan ini bukan kampanye kalibrasi baru.

```sh
python Program/download_thingspeak_dataset.py --start WAKTU_MULAI --end WAKTU_AKHIR
python Program/analyze_session.py Program/data/downloads/NAMA_FILE.csv --require-v4 --preflight --output preflight_BARU.json
```

Ganti waktu dengan tanggal/jam WIB sebenarnya. Downloader default membuat snapshot baru. Gate software meminta15menit, >=30rekaman, satu schema/build/boot, format/sequence/slot sesuai, model valid, tanpa rail berkepanjangan/fault yang perlu diperiksa, serta latensi tersedia. Flag32768 sebelum24jam bukan kegagalan; flags256/2048/4096 tetap sesuai keterbatasan model/hardware. Umumnya flags39168 pada kondisi tanpa fault sebelum24jam.

Saturasi/obstruksi tidak otomatis berarti konsentrasi tinggi tertentu. Tidak perlu membakar kertas atau membuat CO untuk menguji batas; tes software mencakup kategori maksimum. Kipas melambat8detik per tingkat saat indeks benar-benar rendah; alarm mengikuti kategori saat ini, bukan level kipas yang tertahan. Jika ada fault, pertahankan bukti dan perbaiki penyebab sebelum sesi final, bukan menghapus baris agar lolos.

## 4. Logbook yang diisi selama studi

Catat kejadian saat terjadi, tidak harus menulis setiap detik. Gunakan jam perangkat pencatat yang sama bila memungkinkan; nyatakan waktu perkiraan jika tidak ingat tepat.

| Tanggal/jam mulai–selesai WIB | Kejadian | Detail yang diisi | Sumber kepastian |
|---|---|---|---|
| Diisi saat studi | AC | ON/OFF, setpoint 24–27 C atau nilai aktual setelan, fan mode bila berubah | Observasi / perkiraan |
| Diisi saat studi | Pintu/jendela | Terbuka/tertutup dan durasinya | Observasi / perkiraan |
| Diisi saat studi | Okupansi | Jumlah orang dan kegiatan umum | Observasi / perkiraan |
| Diisi saat studi | Aktivitas | Menyapu, merapikan kain, penggunaan pewangi atau sumber gas/partikel normal yang memang terjadi | Observasi / perkiraan |
| Diisi saat studi | Router/internet | Mati, menyala, internet bermasalah; kapan dashboard pulih | Observasi / perkiraan |
| Diisi saat studi | Daya/perangkat | Adaptor lepas, restart, fan berhenti, bunyi tidak biasa, perubahan posisi | Observasi / perkiraan |
| Diisi saat studi | Pemeliharaan | Penggantian filter/pembersihan jika terpaksa dilakukan | Observasi / perkiraan |

Tidak perlu mencatat identitas penghuni. Jangan mengubah aktivitas menjadi sumber polusi sengaja hanya demi grafik. Foto kondisi awal/akhir serta catatan perubahan lebih berguna daripada klaim kebersihan udara tanpa referensi.

## 5. Mulai dan pertahankan168jam

Setelah pemeriksaan fungsi sesuai, catat t0 dan rencana akhir t0+168jam. Tidak wajib restart setelah commissioning. Gunakan posisi,filter,firmware,model dan daya yang sama. Restart/perubahan terpaksa dicatat sebagai segmen baru. Tidak ada baseline konsentrasi per boot; reset menghapus ring24jam.

ESP32+Wi-Fi berjalan mandiri. Analog menargetkan100Hz, blok sekitar1detik, DHT2detik, cloud20detik. Nominal168jam sekitar30240slot cloud; bukan jaminan jumlah feed. Snapshot bukan rerata20detik dan tidak merekam setiap transisi kipas.

Cek singkat feed melalui HP bila memungkinkan. Saat router mati, kendali dan akumulasi24jam tetap berjalan selama ESP32 hidup, tetapi snapshot mentah selama offline tidak disimpan untuk replay. Catat gap; jangan isi nilai hilang dengan angka normal. Tidak ada automation atau jaminan nol packet loss.

## 6. Analisis dan naskah

Simpan CSV asli/hash, manifest, foto dan logbook. Analyzer memisahkan versi/boot dan tidak mengubah sumber. Grafik utama: raw GP/MQ7 dari status, estimasi PM/CO, indeks instan/kategori, PWM serta T/RH. Tambahkan kejadian AC/pintu/aktivitas/jaringan. Plot estimasi24jam terpisah dan tampilkan coverage. Jangan menukar indeks instan dengan indeks24jam atau menyebut estimasi model sebagai ISPU resmi.

Ring24jam mengintegrasikan waktu sampel valid dalam1440menit lengkap. Data baru tersedia setelah>=24jam sejakboot dan>=75% waktu valid; missing tetap missing. Nilai dalam status dibulatkan sehingga replay angka dekat ambang tidak persis identik. Rerata24jam ini tetap mewarisi ketidakpastian model/satuan.

Laporkan durasi dan jumlah feed aktual, gap, boot, flags, rentang keluaran, plateau model, distribusi level serta latensi inferensi median/p95/maks. Coverage perboot = slot unik/(slot terakhir-slot pertama+1); tidak termasuk reset offline yang tak terlihat dan bukan packet-loss protokol. Jangan membuat ribuan snapshot menjadi ribuan eksperimen independen.

Kalimat metode: “Prototipe mengakuisisi sensor murah dan menjalankan dua model RF untuk menghasilkan estimasi nominal PM dan CO. Sub-indeks dihitung menggunakan interpolasi tabel Permen LHK14/2020 dan maksimum digunakan sebagai indeks estimasi instan untuk respons aktuator. Rerata24jam dihitung terpisah dengan pemeriksaan cakupan waktu. Skala model PM, transfer MQ7 dan akurasi fisik belum tervalidasi; penelitian mengevaluasi implementasi dan operasi prototipe pada kondisi kamar yang dicatat.”

Batas naskah: tidak mengklaim akurasi99.97%, model setara sensor mahal, drift berhasil dikoreksi, udara pasti aman, penghilanganCO, CADR,HEPA,dB,efisiensi energi atau nol kehilangan data tanpa bukti sesuai. Evaluasi benchmark publik tetap terpisah dari kinerja sensor ruangan.
