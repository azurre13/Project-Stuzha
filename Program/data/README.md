# Dataset Ground Truth untuk ML Calibration

Folder ini berisi dataset publik yang digunakan sebagai **ground truth** untuk melatih model Random Forest Regressor pada Project Stuzha.

> ⚠️ **File CSV/ZIP tidak di-push ke Git** (terlalu besar). Download manual dari link berikut.

---

## Dataset yang Digunakan

### 1. Mendeley — Indoor Air Pollutants (`data/mendeley/`)

| Aspek | Detail |
|---|---|
| **Judul** | Dataset of Indoor Air Pollutants using Low-Cost Sensors |
| **Penulis** | Sonawani & Patil (2022) |
| **DOI** | [10.17632/2r232jpfb2.1](https://doi.org/10.17632/2r232jpfb2.1) |
| **Download** | https://data.mendeley.com/datasets/2r232jpfb2/1 |
| **Jumlah Data** | 173.468 record |
| **Periode** | Nov 2020 – Jul 2022 |
| **Sensor PM2.5** | **GP2Y1010AU0F** (identik dengan alat kita!) |
| **Digunakan untuk** | Training model **RF_PM** (kalibrasi partikulat debu) |

**Kolom:** `NH3, NO2, CO, PM2.5, Temp, Pressure, Humidity, O3, Date`

### 2. UCI — Air Quality (`data/uci/`)

| Aspek | Detail |
|---|---|
| **Judul** | Air Quality |
| **Sumber** | UCI Machine Learning Repository |
| **URL** | https://archive.ics.uci.edu/dataset/360/air+quality |
| **Jumlah Data** | 9.471 record (per jam) |
| **Periode** | Mar 2004 – Apr 2005 |
| **Ground Truth** | CO dari **certified reference analyzer** (Tier 1) |
| **Digunakan untuk** | Training model **RF_CO** (kalibrasi gas CO) |

**Kolom utama:** `CO(GT), PT08.S1(CO), T, RH, AH`

> Catatan: Nilai `-200` dalam dataset UCI berarti **missing data**.

---

## Cara Download

```bash
# Mendeley (download manual dari browser)
# Simpan di: data/mendeley/Indoor_Air_Pollution_Data.csv

# UCI (via command line)
curl -L -o data/uci/air_quality.zip https://archive.ics.uci.edu/static/public/360/air+quality.zip
cd data/uci && unzip air_quality.zip
```

## Eksplorasi Data

```bash
python ml_training/explore_datasets.py
```
