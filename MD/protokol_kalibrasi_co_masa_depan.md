# Protokol Kalibrasi CO (MQ-7) Masa Depan

Dokumen pelengkap metodologi Project Stuzha. Disiapkan sebagai acuan teknis jika di masa depan tersedia instrumen pembanding standar (reference instrument) atau ruang uji gas (gas chamber) berkalibrasi.

---

## 1. Status Saat Ini (Fase Prototipe Penelitian)

1. **Kondisi Aktif (Firmware v4.0.0):**
   - Sensor terpasang: MQ-7 (pembacaan tegangan analog via ADC pada GPIO 32).
   - Pemanas/Heater: Diberi tegangan continuous 5 V dari board expansion.
   - Model ML: Random Forest inferensi edge C++ (`model_co.h`) dengan input fitur `{mq7_adc, suhu, kelembaban}`.
   - Peran Sistem: Estimator eksperimental indoor multi-polutan untuk komparasi sub-indeks ISPU Permen LHK No. 14 Tahun 2020 dan penentuan tingkat kendali kipas.
   - Klasifikasi Penelitian: Prototipe monitoring indoor eksperimental berbasis TinyML. Bukan instrumen pengukur konsentrasi gas tervalidasi laboratorium.

2. **Keterbatasan yang Diakui:**
   - Model dilatih menggunakan dataset sekunder (UCI Air Quality) yang menggunakan basis sensor MOX berbeda (PT08.S1).
   - Belum dilakukan pengujian berpasangan (co-located test) dengan instrumen acuan bersertifikat karena keterbatasan fasilitas dan biaya penelitian mandiri.

---

## 2. Kebutuhan Minimum Kalibrasi Lapangan (Co-location)

Jika tersedia instrumen acuan CO portabel berkalibrasi (misal: GasAlertMicroClip, Testo 315, atau Aeroqual Seri 500 CO sensor head):

### A. Konfigurasi Penempatan
- Letakkan prototipe Stuzha dan instrumen pembanding berdampingan pada jarak < 30 cm dalam satu ruangan tertutup.
- Pastikan sensor tidak terkena hembusan langsung pendingin ruangan (AC) atau aliran kipas exhaust Stuzha itu sendiri.

### B. Protokol Perekaman Data
1. **Durasi Perekaman:** Minimum 7 × 24 jam untuk mencakup variasi harian temperatur, kelembaban, dan aktivitas indoor (aktivitas memasak, respirasi, ventilasi).
2. **Sinkronisasi Waktu:** Samakan jam perangkat pembanding dengan timestamp UTC/WIB pada ThingSpeak (resolusi per 20–30 detik).
3. **Data yang Diambil dari Stuzha:**
   - `mq7_adc` (raw ADC dari Field Status `a=...,MQ7`)
   - Suhu (°C) dari Field 1
   - Kelembaban (% RH) dari Field 2
4. **Data dari Instrumen Acuan:**
   - Konsentrasi CO referensi ($C_{\text{ref}}$) dalam ppm atau mg/m³.

---

## 3. Alur Training Model Kalibrasi Baru

Setelah dataset berpasangan terkumpul:

```text
[ Raw ADC MQ-7 + Suhu + RH ] + [ CO Referensi (ppm) ]
               ↓
    Pembersihan & Resampling Time-Series
               ↓
    Split Data: Train (70%), Test (30%)
               ↓
    Training Model Regresi (Linear / Ridge / TinyML Tree)
               ↓
    Evaluasi Metrik: RMSE, MAE, R² pada Test Set
               ↓
    Eksport ke Header C++ (menggantikan model_co.h)
```

---

## 4. Format Pelaporan untuk Publikasi Jurnal

Pada naskah publikasi (Sinta 2/3), metodologi sensor CO disajikan dengan klausul integritas ilmiah:
- **Pendekatan:** Sensor CO MQ-7 diintegrasikan dalam kerangka multi-sensor edge AI untuk mendemonstrasikan kapabilitas arsitektur komputasi embedded TinyML dalam mengeksekusi inferensi multi-polutan secara bersamaan.
- **Validasi:** Pengujian ditekankan pada latensi inferensi (< 10 ms), stabilitas memori (zero memory leak), keandalan telemetri nirkabel, dan responsivitas kendali aktuasi berbasis regulasi Permen LHK 14/2020.
- **Saran Riset Lanjutan:** Kalibrasi fisik menggunakan kamar uji terkendali dan instrumen pembanding kelas industri dialokasikan sebagai agenda pengembangan berikutnya.
