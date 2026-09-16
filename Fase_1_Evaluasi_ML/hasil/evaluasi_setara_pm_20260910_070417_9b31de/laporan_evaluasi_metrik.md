# Laporan Evaluasi Setara PM & Audit Data Leakage

**Tanggal Evaluasi:** 2026-09-10 07:04:32 UTC
**Audit Data Leakage:** 26689 dari 33493 baris (79.685%)
**Eksekusi C++ Probe:** success
**Status Paritas Header C++ vs Joblib:** `passed_aggregate_with_exceptions` (99,988% sampel memenuhi toleransi, empat sampel melampauinya)
- **Kriteria Agregat:** Lolos (Rata-rata selisih 2.63e-05 <= 1e-4, 99.988% sampel identik dalam batas toleransi 1e-4)
- **Kriteria Pointwise:** 4 pelanggaran batas (0.012% dari 33.493 baris; maks selisih 0.324; diverifikasi otomatis via `Fase_1_Evaluasi_ML/trace_pm_legacy_parity.py`)

### Jejak Eksak 4 Pelanggaran Batas Pointwise (Terbukti Matematis)
| Baris Uji | Baris Sumber | Fitur | Nilai Float32 | Pohon | Node | Ambang C++ vs Py Double | Cabang C++ vs Py | $\Delta$ Prediksi |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |
| 8090 | 148060 | Temp | 33.4000015 | 17 | 47 | `33.400000f` vs `33.3999996` | Kiri (11.197) vs Kanan (1.471) | +0.324213 |
| 9432 | 149402 | Temp | 31.5300007 | 29 | 27 | `31.530001f` vs `31.5299997` | Kiri (1.200) vs Kanan (4.500) | -0.110000 |
| 13708 | 153678 | Temp | 31.5400009 | 4 | 39 | `31.540000f` vs `31.5399999` | Kiri (5.000) vs Kanan (10.889) | -0.196296 |
| 29821 | 169792 | Temp | 26.3600006 | 26 | 14 | `26.360001f` vs `26.3599996` | Kiri (9.947) vs Kanan (2.500) | +0.248227 |

## Model Kandidat Tersimpan (.joblib)

- Skala Sumber: `candidate_model_pm_raw.joblib` (SHA256: `9fdcf9b05dbc7bc9...`)
- Skala x1000: `candidate_model_pm_x1000.joblib` (SHA256: `b8127744efedd6e2...`)

## Tabel Metrik Lengkap

| Skala | Model | MAE | RMSE | $R^2$ | Penurunan RMSE | Evaluasi & Catatan |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| skala_sumber_numerik | `raw_input_tanpa_ml` | 0.00226507 | 0.00314592 | -2.0439 | +0.00% | Baseline input dengan gangguan formula simulasi |
| skala_sumber_numerik | `regresi_linear_3fitur` | 0.00575826 | 0.00662671 | -12.5063 | -110.64% | Fit 80% masa lalu, diuji 20% masa depan (float64); tidak mampu menangani suku kuadratik RH |
| skala_sumber_numerik | `rf_chrono_3fitur` | 1.18784e-05 | 0.000213392 | 0.9860 | +93.22% | Fit 80% masa lalu, diuji 20% masa depan; bebas data leakage |
| skala_x1000 | `raw_input_x1000_tanpa_ml` | 2.26507 | 3.14592 | -2.0439 | +0.00% | Baseline input skala x1000 dengan gangguan formula simulasi |
| skala_x1000 | `regresi_linear_x1000_3fitur` | 5.75826 | 6.62671 | -12.5063 | -110.64% | Fit 80% masa lalu, diuji 20% masa depan skala x1000 (float64) |
| skala_x1000 | `rf_chrono_x1000_3fitur` | 0.0118591 | 0.213105 | 0.9860 | +93.23% | Fit 80% masa lalu, diuji 20% masa depan skala x1000; bebas data leakage |
| skala_x1000 | `rf_rekonstruksi_python_joblib` | 0.00930183 | 0.207266 | 0.9868 | +93.41% | Model rekonstruksi Python; mengandung data leakage 79.685% (26689/33493 baris) akibat random split lama |
| skala_x1000 | `rf_header_cpp_aktif_model_pm_h` | 0.00930975 | 0.207573 | 0.9867 | +93.40% | Uji binary C++ (eksekusi: success, paritas: passed); mean selisih 2.63e-05, maks 0.324 (99.99% data <= 1e-4); tercemar 79.685% leakage |
