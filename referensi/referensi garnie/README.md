# Daftar Referensi Jurnal & Fungsi Riset

Daftar 21 referensi jurnal ilmiah yang digunakan sebagai landasan teoritis, metodologis, justifikasi komponen, dan pengisi *research gap* pada **Project Stuzha**.

---

### Jurnal ke-1

- **Link:** https://doi.org/10.55606/juisik.v5i2.1326
- **Fungsi:** Membuktikan bahwa kombinasi sensor gas CO (MQ-7) dan sensor partikulat debu (GP2Y) merupakan standar umum yang sudah teruji di riset IoT pemantau kualitas udara. *(Catatan: Link/file asli hilang, dan tidak akan digunakan lagi anggap saja tidak ada).*

### Jurnal ke-2

- **Link:** https://doi.org/10.63581/JoCPES.v4i1.03
- **Fungsi:** Memperkuat Bab Latar Belakang mengenai alasan pemilihan GP2Y, yaitu harganya murah, mudah didapat, dan cukup reliabel untuk prototipe portabel. *(Catatan: File PDF hilang, namun metadata/abstrak tetap dapat disitasi, pencarian pdf asli masih akan terus dilakukan).*

### Jurnal ke-3

- **Link:** https://doi.org/10.13189/eer.2023.110605
- **Fungsi:** Dasar metode kalibrasi GP2Y dan justifikasi teknis mengapa tegangan analog mentah wajib dikonversi ke satuan standar ($\mu g/m^3$) agar datanya valid.

### Jurnal ke-4

- **Link:** https://doi.org/10.1016/j.jaerosci.2021.105809
- **Fungsi:** Bukti ilmiah bahwa pembacaan sensor debu optik sangat bias oleh suhu dan kelembapan, sekaligus membandingkan efektivitas berbagai algoritma Machine Learning (ML) untuk mengoreksi error tersebut. *(Catatan: File PDF berbayar, akan dilampirkan jika sudah dapat diakses).*.

### Jurnal ke-5

- **Link:** https://doi.org/10.1049/wss2.12043
- **Fungsi:** Bukti bahwa akurasi sensor murah (GP2Y) bisa meningkat drastis mendekati alat ukur standar laboratorium jika diolah dengan algoritma ML yang tepat.

### Jurnal ke-6

- **Link:** https://doi.org/10.5194/amt-13-1693-2020
- **Fungsi:** Alasan teknis memasukkan data sensor DHT22 (suhu dan kelembapan) sebagai variabel input (*feature*) dalam model ML guna mengoreksi pembacaan partikulat yang terdampak uap air.

### Jurnal ke-7

- **Link:** https://doi.org/10.3390/s24113650
- **Fungsi:** Landasan teoritis bahwa kalibrasi sensor murah wajib dilakukan berkala/berkelanjutan, bukan hanya sekali di awal, untuk mengatasi penurunan performa (*sensor drift*) seiring waktu.

### Jurnal ke-8

- **Link:** https://doi.org/10.64206/d8sh8k34
- **Fungsi:** Referensi metode konversi model ML dari Scikit-Learn (Python) menjadi file header C/C++ agar model bisa ditanam langsung di mikrokontroler (Edge AI/TinyML) dengan RAM terbatas.

### Jurnal ke-9

- **Link:** https://doi.org/10.1007/s44291-026-00157-3
- **Fungsi:** Pengisi *research gap*. Sistem mereka memiliki hardware mirip, namun masih menggunakan kalibrasi statis tanpa Random Forest dan tanpa mekanisme kalibrasi berkala seperti di sistem kita.

### Jurnal ke-10

- **Link:** https://ejournal.seaninstitute.or.id/index.php/esaprom/article/view/8110
- **Fungsi:** Bukti eksperimen bahwa teknik kuantisasi (Int8) mampu memangkas ukuran model ML hingga ~587 KB sehingga sangat realistis dijalankan di mikrokontroler.

### Jurnal ke-11

- **Link:** https://doi.org/10.58812/wsis.v2i08.1223
- **Fungsi:** Referensi perhitungan matematis konversi data MQ-7 dan sensor debu ke indeks standar (ISPU/AQI), sekaligus pembanding sistem konvensional non-ML.

### Jurnal ke-12

- **Link:** https://doi.org/10.48309/ajgc.2024.445430.1481
- **Fungsi:** Bukti akurasi hardware MQ-7 yang mampu mencapai 96,95% khusus dalam mendeteksi gas Karbon Monoksida (CO).

### Jurnal ke-13

- **Link:** https://doi.org/10.3390/atmos15121523
- **Fungsi:** Dasar argumen bahwa regresi linear biasa tidak cukup untuk sensor murah, sekaligus peringatan pentingnya tuning hyperparameter agar Random Forest tidak mengalami *overfitting*.

### Jurnal ke-14

- **Link:** https://doi.org/10.3390/smartcities8060200
- **Fungsi:** Justifikasi perlakuan sensor MQ-135 hanya sebagai indikator/proksi keberadaan VOC dan tidak dimasukkan ke dalam rumus baku ISPU/AQI utama karena karakteristik selektivitas gasnya yang luas.

### Jurnal ke-15

- **Link:** http://dx.doi.org/10.3390/atmos11020212
- **Fungsi:** Bukti kuat bahwa algoritma Random Forest paling efektif dalam mengoreksi penyimpangan data akibat gangguan cuaca dan lingkungan pada sensor berbiaya rendah.

### Jurnal ke-16

- **Link:** https://doi.org/10.3390/atmos11111140
- **Fungsi:** Dasar perancangan logika kendali kipas yang kecepatannya diatur adaptif (PWM) mengikuti beban polutan spesifik, bukan sekadar saklar on-off.

### Jurnal ke-17

- **Link:** https://doi.org/10.26599/JIC.2024.9180032
- **Fungsi:** Bukti efisiensi energi bahwa pengaturan kecepatan kipas secara dinamis dapat memangkas konsumsi daya sistem secara nyata.

### Jurnal ke-18

- **Link:** https://www.researchgate.net/publication/393789034_Design_and_Implementation_of_a_Low-Cost_IoT-Based_Air_Purification_Unit
- **Fungsi:** Referensi arsitektur dasar air purifier IoT murah untuk memetakan desain awal alat sebelum ditingkatkan ke model berbasis AI.

### Jurnal ke-19

- **Link:** https://ejournal.uinib.ac.id/jurnal/index.php/insearch/article/download/13689/5153
- **Fungsi:** Referensi kontrol kipas bertingkat berbasis mikrokontroler, sekaligus pembanding bahwa sistem lama masih menggunakan *threshold* kaku tanpa adaptasi ML.

### Jurnal ke-20

- **Link:** https://doi.org/10.3389/fenvs.2026.1822757
- **Fungsi:** Bukti bahwa implementasi ML pada edge device (TinyML) adalah pendekatan mutakhir dan berdampak nyata, bukan sekadar fitur tambahan.

### Jurnal ke-21

- **Link:** https://doi.org/10.1016/j.measen.2026.101994
- **Fungsi:** Argumen urgensi kesehatan bahwa mitigasi udara kotor memerlukan sistem yang merespons secara real-time untuk mencegah paparan racun akut di dalam ruangan.
