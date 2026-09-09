# Metode aktif Stuzha v4 — tujuan awal dipertahankan

9 September 2026. Pemilik memberi izin menyelesaikan revisi tanpa mengalihkan tujuan dan tanpa menjadikan pembelian instrumen pembanding sebagai syarat. Dokumen ini menggantikan keputusan v3.0/v3.1. [Prompt pemilik](prompt_perbaikan_ilmiah_astra.md) dipertahankan sebagai usulan; isinya tetap diperiksa terhadap sumber primer.

## Hasil revisi

Alur aktif: GP2Y dan MQ7 dengan T/RH masuk dua model RF, keluaran model dikonversi menjadi sub-indeks PM dan CO, maksimum menentukan kategori dan perintah kipas. MQ135 tetap proksi gas campuran. Tidak ada penggantian fungsi utama dengan skor deviasi baseline per boot.

Perbaikan yang selesai di software: interpolasi kontinu tanpa celah breakpoint; CO mg/m3 ke ug/m3 untuk indeks dan ppm acuan untuk tampilan; kategori/parameter kritis; penurunan kipas8detik per tingkat; alarm terpisah dari fault dan fan yang masih melambat; raw ketiga sensor tetap tersimpan; decoder lintasversi; ring24jam dengan pemeriksaan kelengkapan; identitas build. Detail kontrak ada pada [firmware](../Program/Kode/firmware_stuzha.md), langkah lapangan pada [protokol](protokol_pengambilan_data_7_hari.md).

## Apa yang belum dapat diselesaikan dari kode saja

**Peningkatan akurasi fisik belum terbukti, dan skala PM masih merupakan asumsi nominal legacy.** Mengembalikan indeks/kategori tidak menyelesaikan masalah model ini. Kode v4 adalah implementasi eksperimental yang lengkap secara fungsi, bukan kalibrasi konsentrasi yang telah selesai. Flag keterbatasan dan label nominal membantu keterlacakan, tetapi tidak memperbaiki model.

Pemeriksaan script training lama di Git menunjukkan target PM = kolom PM2.5 Mendeley dikali1000; input dibuat dari target ditambah gangguan RH/T/noise sintetis. [Metadata sumber](https://data.mendeley.com/datasets/2r232jpfb2/1) menyebut ug/m3, sehingga asumsi pengalian1000 belum dapat dibenarkan dari metadata tersebut. V4 mempertahankan skala angka legacy sebagai skenario nominal untuk eksperimen sistem, **tidak menyatakan konflik sudah terselesaikan**. Nilai indeks dapat berubah besar jika asumsi ini salah; jangan memakai hasilnya untuk menyatakan udara aman.

Target CO pada script lama adalah CO(GT) mg/m3. Input PT08.S1 dipetakan ke800..3600 dan diganti MQ7ADC pada perangkat; kesesuaian transfer belum terbukti. Label ppm lama salah, sehingga v4 melakukan konversi eksplisit pada25C/1atm. Konversi satuan yang benar tidak memperbaiki transfer sensor. Header benchmark baru memakai PT08 asli dan tidak dimasukkan ke firmware begitu saja.

Tidak dilakukan retraining baru dengan label buatan agar terlihat akurat. Dua header historis tetap identik dan diidentifikasi oleh hash manifest. Pada audit awal, artefak model Python asal belum terverifikasi. Audit lanjutan telah mereproduksi source header PM serta menyimpan model Python; header CO aktif masih berbeda dari hasil rekonstruksi. Lihat [hasil reproduksi](../Fase_1_Evaluasi_ML/reproduksi_legacy_20260909.json). Kandidat ekspor baru cocok dengan model Python hasil reproduksi, tetapi belum mengganti header aktif. Metrik benchmark kronologis baru tetap berbeda dari metrik deployment.

## Pemeriksaan rumus/datasheet

[Datasheet Sharp](https://global.sharp/products/device/lineup/data/pdf/datasheet/gp2y1010au_e.pdf) menyatakan sensitivitas sebagai perubahan voltase per0.1mg/m3. Bentuk estimator datasheet adalah C=(Vout-Vzero)/sensitivitas dengan satuan yang konsisten; nilai tipikal bukan kalibrasi individu atau pemisahan ukuran PM2.5. Istilah Vclean berupa voltase tidak boleh langsung dikurangkan dari0.17*V jika hasil perkalian sudah bersatuan massa. Firmware mempertahankan transformasi legacy sebagai kontrak input RF, bukan menyebutnya fungsi resmi Sharp yang terkalibrasi.

[Manual MQ7 v1.3](https://cdn.sparkfun.com/datasheets/Sensors/Biometric/MQ-7%20Ver1.3%20-%20Manual.pdf) mensyaratkan siklus heater untuk deteksi. Nilai Rs memerlukan tegangan pada resistor beban dan RL yang benar; R0/kurva bergantung kondisi serta versi manual. Tidak ada dasar untuk memasukkan angka R0, gain pembagi tegangan atau koefisien kurva sebagai hasil ukur rakitan ini. Jalur ADC→RF historis tetap dipakai dan ketidakpastiannya dilaporkan; tidak berpura-pura menggantinya dengan kalibrasi datasheet lengkap.

## Indeks instan dan24jam

[Permen LHK14/2020 Lampiran I](https://ppkl.menlhk.go.id/website/filebox/988/210704011643PERMEN%20ISPU%20NO%2014%20TAHUN%202020.pdf) memberi tabel PM dan CO dalamug/m3 berbasis24jam. Tabel CO8jam ppm dalam prompt tidak dipakai. Interpolasi memakai titik batas bersama, bukan interval15.5→15.6 yang meninggalkan celah. Contoh regulasi PM31.4 menghasilkan indeks dibulatkan70 dan diuji pada software.

Field5 merupakan **indeks estimasi instan dari keluaran model nominal**, dipakai untuk respons lokal cepat. Ring terpisah menghitung mean24jam lalu interpolasi dari mean masing-masing dan maksimum. Bukan merata-ratakan indeks instan. Ring memakai waktu valid, bukan sekadar menghitung baris. Sebelum24jam atau cakupan<75%, angka24jam tidak tersedia. Keduanya tetap model-based; rerata waktu tidak menjadikannya pengukuran ISPU resmi.

Kategori pada field8 kembali1–5 sesuai rentang indeks, dengan0 untuk tidak tersedia. Kategori saat ini dapat berbeda dari level kipas karena dwell. Grafik/caption harus menggunakan istilah kategori estimasi model dan membedakan instan/24jam. Tidak mengubah kategori publik menjadi klaim bahwa pengguna pasti aman atau dalam bahaya.

## Kendali dan fault

Konfirmasi kenaikan>=1detik, histeresis turun5%, dwell8detik per tingkat. Uji pemulihan dilakukan dengan nilai model yang turun; kipas tidak boleh dipaksa kembali rendah jika model tetap tinggi hanya agar perangkat terdengar tenang. DariL5 keL1 sekitar32–36detik pada blok1detik.

Rerata GP4001 masih diproses. Rerata>=4094 dianggapjenuh/tidak terukur, bukan otomatis kerusakan hardware ataupun buktiPM>250. Saturasi meminta fanL5, tetapi kategori tidak tersedia dan alarm polusi diam. Input invalid lain meminta sedikitnyaL4; saat pulih kipas turun sesuai dwell. Buzzer memerlukan kategori model valid>=4 saat ini dan tidak ikut tertahan ketika kategori turun.

## Sumber jurnal yang mendukung pendekatan

Empat artikel primer berikut dipakai sesuai temuannya, bukan sebagai pengganti hasil eksperimen Stuzha:

1. Zimmerman et al.2018, RF calibration pada paket sensor RAMP, [DOI10.5194/amt-11-291-2018](https://amt.copernicus.org/articles/11/291/2018/).
2. Han et al.2021, evaluasi kalibrasi sensor gas dengan pembanding metode dan stasiun rujukan, [DOI10.3390/s21010256](https://mdpi-res.com/d_attachment/sensors/sensors-21-00256/article_deploy/sensors-21-00256.pdf).
3. Crilley et al.2018, evaluasi OPC-N2 dan pengaruhRH, [DOI10.5194/amt-11-709-2018](https://amt.copernicus.org/articles/11/709/2018/).
4. Jayaratne et al.2018, kelembapan/kabut dan PMS1003, [DOI10.5194/amt-11-4883-2018](https://amt.copernicus.org/articles/11/4883/2018/).

Literatur memberi alasan meneliti koreksi lingkungan. Ia tidak menetapkan bahwa koefisien gangguan sintetis legacy benar, bahwaRF selalu unggul, atau bahwaMQ7 tanpa konfigurasi/rujukan sesuai menghasilkan akurasi setara sensor mahal. Klaim publikasi mengikuti hasil yang benar-benar tersedia.

## Verifikasi dan freeze

[Rekaman verifikasi](verifikasi_revisi_v4.json) mencatat build, hash, tes dan keterbatasan. Tes mencakup batas indeks, contoh regulasi, konversi gas, kategori maksimum, actual-header integration, pemulihan fault/alarm, rollover, format cloud, serta simulasi ring tujuh hari dan kehilangan data. Simulasi host bukan operasi fisik tujuh hari.

Build berhasil; portserial belum terdeteksi, sehingga belum upload atau uji fisik. Tidak ada perubahan channel, commit atau push. CSV asli dan dua header RF dipertahankan. Binari lokal berisi konfigurasi privat dan tidak dipublikasikan.

Setelah satu upload dan pemeriksaan fungsi singkat yang sesuai, versi ini dapat dibekukan untuk observasi prototipe. Tidak perlu eksperimen panjang tambahan sebelum menilai fungsi software. Namun belum dapat diberi status “kalibrasi selesai/akurasi terjamin”; masalah skala dan transfer model tetap harus dinyatakan dalam naskah, tanpa mengubah tujuan awal proyek.
