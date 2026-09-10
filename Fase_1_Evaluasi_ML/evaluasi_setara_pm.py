"""Evaluasi Setara PM (GP2Y1010AU0F) - Bebas Data Leakage.

Skrip ini menjalankan evaluasi bersih:
1. Split waktu murni (80% awal untuk training, 20% akhir untuk testing).
2. Membandingkan:
   - Raw Input (tanpa koreksi)
   - Regresi Linear (3 fitur: PM_raw, T, RH)
   - Random Forest Chrono (dilatih murni pada 80% awal)
3. Menguji model aktif historis secara terpisah untuk keterlacakan,
   dengan mencatat data leakage sebesar 79.69% akibat split acak lama.
4. Menghitung pada skala asli dataset dan skala x1000 untuk transparansi.
"""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pathlib import Path
import joblib

ROOT = Path(__file__).resolve().parents[1]

def main():
    mendeley_path = ROOT / "Program/data/mendeley/Indoor_Air_Pollution_Data.csv"
    df = pd.read_csv(mendeley_path, low_memory=False)[["Date", "PM2.5", "Temp", "Humidity"]]
    for col in ["PM2.5", "Temp", "Humidity"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["stamp"] = pd.to_datetime(df["Date"].str.replace("|", " ", regex=False), format="mixed", errors="coerce")
    df = df.dropna(subset=["PM2.5", "Temp", "Humidity", "stamp"]).sort_values("stamp", kind="stable").reset_index(drop=True)
    df = df[(df["PM2.5"] >= 0) & df.Temp.between(10, 45) & df.Humidity.between(20, 95)].reset_index(drop=True)

    n_total = len(df)
    n_train = int(n_total * 0.8)
    
    # Skala 1: Nilai numerik dataset sumber (0.0 - 0.47)
    y_raw = df["PM2.5"].to_numpy()
    temp = df.Temp.to_numpy()
    rh = df.Humidity.to_numpy()

    # Formula simulasi perturbasi buatan:
    # y * (1 + 0.65 * (rh/100)^2) + (temp-25)*0.00045 + noise normal
    rng = np.random.default_rng(42)
    noise_raw = rng.normal(0, 0.0025, n_total)
    x_pert_raw = np.maximum(0, y_raw * (1 + 0.65 * (rh / 100)**2) + (temp - 25) * 0.00045 + noise_raw)

    # Skala 2: Skala x1000 (0.0 - 470.0)
    y_x1000 = y_raw * 1000.0
    x_pert_x1000 = x_pert_raw * 1000.0

    records = []

    for scale_name, y_arr, x_arr, unit_str in [
        ("skala_sumber_numerik", y_raw, x_pert_raw, "unit numerik sumber (konflik belum terselesaikan)"),
        ("skala_x1000", y_x1000, x_pert_x1000, "ug/m3 (asumsi pengali 1000)")
    ]:
        X = np.column_stack([x_arr, temp, rh])
        X_tr, X_te = X[:n_train], X[n_train:]
        y_tr, y_te = y_arr[:n_train], y_arr[n_train:]

        # 1. Baseline: Raw input (tanpa ML)
        rmse_raw = float(np.sqrt(mean_squared_error(y_te, X_te[:, 0])))
        mae_raw = float(mean_absolute_error(y_te, X_te[:, 0]))
        r2_raw = float(r2_score(y_te, X_te[:, 0]))
        records.append({
            "skala": scale_name,
            "satuan": unit_str,
            "evaluasi": "split_waktu_murni",
            "model": "raw_input_tanpa_ml",
            "rmse": rmse_raw,
            "mae": mae_raw,
            "r2": r2_raw,
            "penurunan_rmse_persen": 0.0,
            "catatan": "Baseline masukan dengan gangguan buatan formula simulasi"
        })

        # 2. Regresi Linear 3-fitur (fit pada training 80%)
        lr = LinearRegression().fit(X_tr, y_tr)
        pred_lr = lr.predict(X_te)
        rmse_lr = float(np.sqrt(mean_squared_error(y_te, pred_lr)))
        mae_lr = float(mean_absolute_error(y_te, pred_lr))
        r2_lr = float(r2_score(y_te, pred_lr))
        records.append({
            "skala": scale_name,
            "satuan": unit_str,
            "evaluasi": "split_waktu_murni",
            "model": "regresi_linear_3fitur",
            "rmse": rmse_lr,
            "mae": mae_lr,
            "r2": r2_lr,
            "penurunan_rmse_persen": (rmse_raw - rmse_lr) / rmse_raw * 100.0,
            "catatan": "Fit 80% masa lalu, diuji 20% masa depan; tidak mampu menangani suku kuadratik RH"
        })

        # 3. Random Forest Chrono (fit pada training 80%)
        rf = RandomForestRegressor(n_estimators=30, max_depth=8, random_state=42, n_jobs=-1).fit(X_tr, y_tr)
        pred_rf = rf.predict(X_te)
        rmse_rf = float(np.sqrt(mean_squared_error(y_te, pred_rf)))
        mae_rf = float(mean_absolute_error(y_te, pred_rf))
        r2_rf = float(r2_score(y_te, pred_rf))
        records.append({
            "skala": scale_name,
            "satuan": unit_str,
            "evaluasi": "split_waktu_murni",
            "model": "rf_chrono_3fitur",
            "rmse": rmse_rf,
            "mae": mae_rf,
            "r2": r2_rf,
            "penurunan_rmse_persen": (rmse_raw - rmse_rf) / rmse_raw * 100.0,
            "catatan": "Fit 80% masa lalu, diuji 20% masa depan; bebas data leakage"
        })

    # 4. Pengujian model aktif historis untuk keterlacakan
    legacy_joblib = ROOT / "Fase_1_Evaluasi_ML/hasil/reproduksi_awal_20260909_124230_faba1c/model_pm.joblib"
    if legacy_joblib.exists():
        model_legacy = joblib.load(legacy_joblib)
        X_te_x1000 = np.column_stack([x_pert_x1000[n_train:], temp[n_train:], rh[n_train:]])
        y_te_x1000 = y_x1000[n_train:]
        pred_legacy = model_legacy.predict(X_te_x1000)
        rmse_leg = float(np.sqrt(mean_squared_error(y_te_x1000, pred_legacy)))
        mae_leg = float(mean_absolute_error(y_te_x1000, pred_legacy))
        r2_leg = float(r2_score(y_te_x1000, pred_legacy))
        records.append({
            "skala": "skala_x1000",
            "satuan": "ug/m3 (asumsi pengali 1000)",
            "evaluasi": "keterlacakan_header_aktif",
            "model": "rf_aktif_legacy_model_pm_h",
            "rmse": rmse_leg,
            "mae": mae_leg,
            "r2": r2_leg,
            "penurunan_rmse_persen": (3.146 - rmse_leg) / 3.146 * 100.0,
            "catatan": "PERINGATAN: Mengandung 79.69% data leakage terhadap data uji kronologis karena dilatih dengan split acak"
        })

    out_df = pd.DataFrame(records)
    out_csv = ROOT / "Fase_1_Evaluasi_ML/tabel_evaluasi_setara_pm.csv"
    out_df.to_csv(out_csv, index=False)
    print(f"Hasil evaluasi bersih disimpan di {out_csv}")
    print(out_df[["skala", "model", "rmse", "mae", "r2", "penurunan_rmse_persen"]])

if __name__ == "__main__":
    main()
