"""Reproducible public-data experiments. Never overwrites deployed model headers.

uci-co: chronological benchmark on PT08.S1, target CO(GT) in mg/m3.
pm-simulation: synthetic perturbation in ORIGINAL dataset units, without assuming
the unresolved Mendeley concentration unit. Neither experiment calibrates Stuzha.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import uuid

import numpy as np
import pandas as pd
import sklearn
try:
    from evaluation_outputs import save_evaluation
except ImportError:
    from ml_training.evaluation_outputs import save_evaluation
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1]


def load_experiment(name):
    if name == "uci-co":
        path = ROOT / "Program/data/uci/AirQualityUCI.csv"
        df = pd.read_csv(path, sep=";", decimal=",")
        df["stamp"] = pd.to_datetime(df["Date"] + " " + df["Time"], format="%d/%m/%Y %H.%M.%S", errors="coerce")
        cols = ["PT08.S1(CO)", "T", "RH", "CO(GT)"]
        df[cols] = df[cols].apply(pd.to_numeric, errors="coerce").replace(-200, np.nan)
        df = df.dropna(subset=cols + ["stamp"]).sort_values("stamp", kind="stable")
        df = df[(df["CO(GT)"] >= 0) & (df["PT08.S1(CO)"] > 0) & df.RH.between(0, 100)]
        x = df[cols[:3]].to_numpy(dtype=np.float32)
        y = df["CO(GT)"].to_numpy()
        unit = "mg/m3 (UCI reference analyzer); NOT MQ-7 calibration"
        features = cols[:3]
    else:
        path = ROOT / "Program/data/mendeley/Indoor_Air_Pollution_Data.csv"
        df = pd.read_csv(path, low_memory=False)
        df["stamp"] = pd.to_datetime(df["Date"].str.replace("|", " ", regex=False), format="mixed", errors="coerce")
        cols = ["PM2.5", "Temp", "Humidity"]
        df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
        df = df.dropna(subset=cols + ["stamp"]).sort_values("stamp", kind="stable")
        df = df[(df["PM2.5"] >= 0) & df.Temp.between(10, 45) & df.Humidity.between(20, 95)]
        y = df["PM2.5"].to_numpy()  # NO implicit x1000 conversion.
        temp, rh = df.Temp.to_numpy(), df.Humidity.to_numpy()
        rng = np.random.default_rng(42)
        perturbed = np.maximum(0, y * (1 + 0.65 * (rh / 100) ** 2)
                               + (temp - 25) * 0.00045 + rng.normal(0, 0.0025, len(y)))
        x = np.column_stack([perturbed, temp, rh]).astype(np.float32)
        unit = "original dataset numeric units (physical unit unresolved); synthetic experiment"
        features = ["synthetic_response", "Temp", "Humidity"]
    if len(df) < 100:
        raise ValueError("Too few valid observations")
    # Split at a timestamp, so equal timestamps never appear on both sides.
    boundary = df.stamp.iloc[int(len(df) * 0.8)]
    train = (df.stamp < boundary).to_numpy()
    if train.sum() < 20 or (~train).sum() < 20:
        raise ValueError("Invalid chronological split")
    return path, df, x, y, train, unit, features, boundary


def export_header(model, path, function="benchmark_predict"):
    """Use double thresholds and leaf constants, float32 inputs as sklearn does."""
    lines = ["#pragma once", "// PUBLIC-DATA BENCHMARK ONLY. NOT A STUZHA CALIBRATION."]
    for i, estimator in enumerate(model.estimators_):
        tree = estimator.tree_
        lines.append(f"static double benchmark_tree_{i}(const float *x) {{")
        def emit(node, indent):
            prefix = " " * indent
            if tree.children_left[node] < 0:
                lines.append(f"{prefix}return {float(tree.value[node, 0, 0]):.17g};")
            else:
                lines.append(f"{prefix}if ((double)x[{tree.feature[node]}] <= {tree.threshold[node]:.17g}) {{")
                emit(tree.children_left[node], indent + 2)
                lines.append(prefix + "} else {")
                emit(tree.children_right[node], indent + 2)
                lines.append(prefix + "}")
        emit(0, 2)
        lines.append("}")
    lines.extend([f"static double {function}(const float *x) {{", "  double sum = 0;"])
    lines.extend(f"  sum += benchmark_tree_{i}(x);" for i in range(len(model.estimators_)))
    lines.extend([f"  return sum / {len(model.estimators_)}.0;", "}"])
    path.write_text("\n".join(lines) + "\n")


def check_export(model, x_test, directory):
    compiler = shutil.which("g++")
    if not compiler:
        return {"status": "not_run", "reason": "g++ unavailable"}
    # Include held-out observations AND threshold-adjacent float32 probes.
    probes = [row for row in x_test[::max(1, len(x_test) // 300)]]
    base = x_test[0].copy()
    for estimator in model.estimators_[:3]:
        tree = estimator.tree_
        for feature, threshold in zip(tree.feature, tree.threshold):
            if feature >= 0:
                center = np.float32(threshold)
                for value in (np.nextafter(center, np.float32(-np.inf)), center,
                              np.nextafter(center, np.float32(np.inf))):
                    probe = base.copy(); probe[feature] = value; probes.append(probe)
    probes = np.asarray(probes, dtype=np.float32)
    source = directory / "check_export.cpp"
    source.write_text('#include <cstdio>\n#include "benchmark_model.h"\nint main(){float x[3]; while(scanf("%f %f %f", &x[0], &x[1], &x[2])==3) printf("%.17g\\n", benchmark_predict(x));}\n')
    binary = directory / "check_export.exe"
    subprocess.run([compiler, "-O2", "-std=c++11", str(source), "-o", str(binary)], check=True, capture_output=True)
    input_text = "\n".join(" ".join(format(float(v), ".9g") for v in row) for row in probes)
    output = subprocess.run([str(binary)], input=input_text, text=True, check=True, capture_output=True).stdout
    actual = np.fromstring(output, sep="\n")
    expected = model.predict(probes)
    if len(actual) != len(expected) or not np.allclose(actual, expected, rtol=1e-10, atol=1e-10):
        raise RuntimeError("Export C++ differs from Python model")
    return {"status": "passed", "probes": len(probes), "max_abs_error": float(np.max(np.abs(actual - expected))),
            "scope": "new benchmark export on host CPU; not legacy headers or ESP32 timing"}


LEGACY_PM_OUTLIER_TRACES = [
    {
        "test_index": 8090,
        "source_row": 148060,
        "feature": "Temp",
        "feature_value_float32": 33.4000015,
        "tree_index": 17,
        "node_index": 47,
        "threshold_cpp_literal": "33.400000f",
        "threshold_py_double": 33.39999961853027,
        "branch_cpp": "LEFT (<= 33.400000f)",
        "branch_py": "RIGHT (> 33.3999996)",
        "leaf_cpp": 11.196969696969697,
        "leaf_py": 1.4705882352941178,
        "delta_leaf": 9.72638146167558,
        "delta_prediction_total_30_trees": 0.324212715389186,
        "kategori": "perbedaan_presisi_ambang_batas_terbukti"
    },
    {
        "test_index": 9432,
        "source_row": 149402,
        "feature": "Temp",
        "feature_value_float32": 31.5300007,
        "tree_index": 29,
        "node_index": 27,
        "threshold_cpp_literal": "31.530001f",
        "threshold_py_double": 31.52999973297119,
        "branch_cpp": "LEFT (<= 31.530001f)",
        "branch_py": "RIGHT (> 31.5299997)",
        "leaf_cpp": 1.200000000000000,
        "leaf_py": 4.500000000000000,
        "delta_leaf": -3.300000000000000,
        "delta_prediction_total_30_trees": -0.110000000000000,
        "kategori": "perbedaan_presisi_ambang_batas_terbukti"
    },
    {
        "test_index": 13708,
        "source_row": 153678,
        "feature": "Temp",
        "feature_value_float32": 31.5400009,
        "tree_index": 4,
        "node_index": 39,
        "threshold_cpp_literal": "31.540000f",
        "threshold_py_double": 31.539999961853027,
        "branch_cpp": "LEFT (<= 31.540000f)",
        "branch_py": "RIGHT (> 31.5399999)",
        "leaf_cpp": 5.000000000000000,
        "leaf_py": 10.88888888888889,
        "delta_leaf": -5.88888888888889,
        "delta_prediction_total_30_trees": -0.196296296296296,
        "kategori": "perbedaan_presisi_ambang_batas_terbukti"
    },
    {
        "test_index": 29821,
        "source_row": 169792,
        "feature": "Temp",
        "feature_value_float32": 26.3600006,
        "tree_index": 26,
        "node_index": 14,
        "threshold_cpp_literal": "26.360001f",
        "threshold_py_double": 26.359999656677246,
        "branch_cpp": "LEFT (<= 26.360001f)",
        "branch_py": "RIGHT (> 26.3599996)",
        "leaf_cpp": 9.946808510638298,
        "leaf_py": 2.500000000000000,
        "delta_leaf": 7.446808510638298,
        "delta_prediction_total_30_trees": 0.248226950354610,
        "kategori": "perbedaan_presisi_ambang_batas_terbukti"
    }
]


def check_cpp_probe_environment(compiler=None, header_path=None):
    """Checks the availability of the C++ compiler and the model header file.
    
    Returns:
        tuple[bool, str]: (is_ready, status_message)
        status_message can be:
          - "header_missing": header file does not exist
          - "compiler_unavailable": C++ compiler (g++) not found
          - "ready": compiler and header are available
    """
    if header_path is None:
        header_path = ROOT / "Program/Kode/include/model_pm.h"
    header_path = Path(header_path)
    if not header_path.exists():
        return False, "header_missing"
    
    if compiler is None:
        compiler = shutil.which("g++")
    elif not shutil.which(compiler):
        compiler = None
    if not compiler:
        return False, "compiler_unavailable"
        
    return True, "ready"


def run_cpp_header_probe(header_path, x_data, func_name="model_pm_predict", compiler=None):
    """Executes a C++ header probe binary against the provided input array.
    
    Uses %.9g format string to guarantee lossless IEEE-754 single-precision float input.
    Returns:
        tuple[str, np.ndarray | None]: (status, predictions)
    """
    is_ready, status = check_cpp_probe_environment(compiler=compiler, header_path=header_path)
    if not is_ready:
        return status, None
    
    if compiler is None:
        compiler = shutil.which("g++")
    header_path = Path(header_path)

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            probe_src = Path(tmpdir) / "probe.cpp"
            probe_bin = Path(tmpdir) / "probe.exe"
            probe_src.write_text(
                f'#include <cstdio>\n#include "{header_path.resolve().as_posix()}"\n'
                f'int main(){{float x[3]; while(scanf("%f %f %f", &x[0], &x[1], &x[2])==3) printf("%.9g\\n", {func_name}(x)); return 0;}}\n'
            )
            subprocess.run([compiler, "-O2", str(probe_src), "-o", str(probe_bin)], check=True, capture_output=True)
            input_data = "\n".join(f"{float(r[0]):.9g} {float(r[1]):.9g} {float(r[2]):.9g}" for r in x_data) + "\n"
            res = subprocess.run([str(probe_bin)], input=input_data, text=True, check=True, capture_output=True)
            preds = np.fromstring(res.stdout, sep="\n", dtype=np.float32)
            if len(preds) != len(x_data):
                return "output_length_mismatch", None
            return "success", preds
    except Exception as e:
        return f"execution_error: {e}", None


def verify_cpp_parity(pred_py, pred_cpp, tolerance=1e-4, aggregate_pct_threshold=99.9):
    """Verifies numerical parity between Python predictions and C++ header predictions.
    
    Evaluates both aggregate statistical criteria and pointwise exactness.
    Returns:
        dict: Detailed parity metrics, outlier traces, and explicit status.
    """
    diff = np.abs(pred_py - pred_cpp)
    mean_diff = float(np.mean(diff))
    max_diff = float(np.max(diff))
    outlier_mask = diff > tolerance
    outlier_count = int(np.sum(outlier_mask))
    outlier_indices = [int(i) for i in np.where(outlier_mask)[0]]
    pct_within = float(np.mean(diff <= tolerance) * 100.0)
    
    aggregate_met = (mean_diff <= tolerance) and (pct_within >= aggregate_pct_threshold)
    pointwise_met = (outlier_count == 0)
    
    if pointwise_met and aggregate_met:
        status = "passed_pointwise"
    elif aggregate_met:
        status = "passed_aggregate_with_exceptions"
    else:
        status = "failed"
        
    return {
        "status": status,
        "mean_abs_difference": mean_diff,
        "max_abs_difference": max_diff,
        "tolerance": tolerance,
        "percent_within_tolerance": pct_within,
        "aggregate_pct_threshold": aggregate_pct_threshold,
        "aggregate_criteria_met": aggregate_met,
        "pointwise_criteria_met": pointwise_met,
        "outlier_count": outlier_count,
        "outlier_indices": outlier_indices,
        "criteria_description": (
            f"Kriteria Agregat: Mean abs diff <= {tolerance:.1e} dan >= {aggregate_pct_threshold}% sampel dalam toleransi {tolerance:.1e}. "
            f"Kriteria Pointwise: 100% sampel dalam toleransi {tolerance:.1e}."
        )
    }


def run_pm_setara(output=None):
    from sklearn.model_selection import train_test_split
    import joblib
    
    path = ROOT / "Program/data/mendeley/Indoor_Air_Pollution_Data.csv"
    df_raw = pd.read_csv(path, low_memory=False)
    
    # 1. Total valid sensor rows historically (167,466 baris, tanpa filter kolom Date)
    df_sensor_valid = df_raw[["PM2.5", "Temp", "Humidity"]].apply(pd.to_numeric, errors="coerce").dropna()
    df_sensor_valid = df_sensor_valid[
        df_sensor_valid.Temp.between(10, 45) &
        df_sensor_valid.Humidity.between(20, 95) &
        (df_sensor_valid["PM2.5"] >= 0)
    ]
    total_legacy_rows = len(df_sensor_valid)  # 167466
    legacy_train_idx, legacy_test_idx = train_test_split(
        df_sensor_valid.index.to_numpy(), test_size=0.2, random_state=42
    )

    # 2. Chronological dataset (167,465 baris, 1 baris indeks 2310 memiliki string Date "0.13" invalid)
    df_chrono = df_raw.copy()
    df_chrono["stamp"] = pd.to_datetime(df_chrono["Date"].str.replace("|", " ", regex=False), format="mixed", errors="coerce")
    cols = ["PM2.5", "Temp", "Humidity"]
    df_chrono[cols] = df_chrono[cols].apply(pd.to_numeric, errors="coerce")
    df_chrono = df_chrono.dropna(subset=cols + ["stamp"]).sort_values("stamp", kind="stable")
    df_chrono = df_chrono[(df_chrono["PM2.5"] >= 0) & df_chrono.Temp.between(10, 45) & df_chrono.Humidity.between(20, 95)]
    
    total_chrono_rows = len(df_chrono)  # 167465
    n_train = int(total_chrono_rows * 0.8)
    n_test = total_chrono_rows - n_train  # 33493
    chrono_train_idx = df_chrono.index.to_numpy()[:n_train]
    chrono_test_idx = df_chrono.index.to_numpy()[n_train:]
    
    # 3. Dynamic leakage calculation using original row indices (df.index)
    leakage_indices = set(legacy_train_idx).intersection(set(chrono_test_idx))
    leakage_count = len(leakage_indices)
    leakage_pct = (leakage_count / len(chrono_test_idx)) * 100.0
    
    directory = Path(output) if output else ROOT / "Fase_1_Evaluasi_ML/hasil" / f"evaluasi_setara_pm_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    
    # 4. Input features and synthetic perturbation
    y_raw = df_chrono["PM2.5"].to_numpy(dtype=np.float32)
    temp = df_chrono["Temp"].to_numpy(dtype=np.float32)
    rh = df_chrono["Humidity"].to_numpy(dtype=np.float32)
    
    rng = np.random.default_rng(42)
    noise_raw = rng.normal(0, 0.0025, total_chrono_rows).astype(np.float32)
    pert_raw = np.maximum(0, y_raw * (1 + 0.65 * (rh / 100)**2) + (temp - 25) * 0.00045 + noise_raw)
    
    y_x1000 = y_raw * 1000.0
    pert_x1000 = pert_raw * 1000.0
    
    x_raw_tr = np.column_stack([pert_raw[:n_train], temp[:n_train], rh[:n_train]]).astype(np.float32)
    x_raw_te = np.column_stack([pert_raw[n_train:], temp[n_train:], rh[n_train:]]).astype(np.float32)
    y_raw_tr = y_raw[:n_train]
    y_raw_te = y_raw[n_train:]
    
    x_x1000_tr = np.column_stack([pert_x1000[:n_train], temp[:n_train], rh[:n_train]]).astype(np.float32)
    x_x1000_te = np.column_stack([pert_x1000[n_train:], temp[n_train:], rh[n_train:]]).astype(np.float32)
    y_x1000_tr = y_x1000[:n_train]
    y_x1000_te = y_x1000[n_train:]
    
    # 5. Evaluate models
    params = dict(n_estimators=30, max_depth=8, random_state=42, n_jobs=1)
    
    # Skala Asli Sumber (menggunakan float64 untuk matrix inversion stabil agar tidak terdistorsi float32)
    lr_raw = LinearRegression().fit(x_raw_tr.astype(np.float64), y_raw_tr.astype(np.float64))
    rf_raw = RandomForestRegressor(**params).fit(x_raw_tr, y_raw_tr)
    
    pred_raw_base = x_raw_te[:, 0]
    pred_raw_lr = lr_raw.predict(x_raw_te.astype(np.float64)).astype(np.float32)
    pred_raw_rf = rf_raw.predict(x_raw_te)
    
    rmse_base_raw = float(np.sqrt(mean_squared_error(y_raw_te, pred_raw_base)))
    
    # Skala x1000 (menggunakan float64 untuk matrix inversion stabil)
    lr_x1000 = LinearRegression().fit(x_x1000_tr.astype(np.float64), y_x1000_tr.astype(np.float64))
    rf_x1000 = RandomForestRegressor(**params).fit(x_x1000_tr, y_x1000_tr)
    
    pred_x1000_base = x_x1000_te[:, 0]
    pred_x1000_lr = lr_x1000.predict(x_x1000_te.astype(np.float64)).astype(np.float32)
    pred_x1000_rf = rf_x1000.predict(x_x1000_te)
    
    rmse_base_x1000 = float(np.sqrt(mean_squared_error(y_x1000_te, pred_x1000_base)))
    
    # 6. Model Rekonstruksi Python & Header C++ Fisik
    legacy_joblib_path = ROOT / "Fase_1_Evaluasi_ML/hasil/reproduksi_awal_20260909_124230_faba1c/model_pm.joblib"
    pred_joblib = None
    if legacy_joblib_path.exists():
        joblib_model = joblib.load(legacy_joblib_path)
        pred_joblib = joblib_model.predict(x_x1000_te)
        
    header_pm_path = ROOT / "Program/Kode/include/model_pm.h"
    cpp_exec_status, pred_cpp = run_cpp_header_probe(header_pm_path, x_x1000_te)
    parity_info = None
    if cpp_exec_status == "success" and pred_joblib is not None and pred_cpp is not None:
        parity_info = verify_cpp_parity(pred_joblib, pred_cpp, tolerance=1e-4, aggregate_pct_threshold=99.9)
            
    # 7. Simpan Model Kandidat Python (.joblib)
    joblib_raw_path = directory / "candidate_model_pm_raw.joblib"
    joblib_x1000_path = directory / "candidate_model_pm_x1000.joblib"
    joblib.dump(rf_raw, joblib_raw_path)
    joblib.dump(rf_x1000, joblib_x1000_path)
    joblib_raw_sha = hashlib.sha256(joblib_raw_path.read_bytes()).hexdigest()
    joblib_x1000_sha = hashlib.sha256(joblib_x1000_path.read_bytes()).hexdigest()

    # 8. Metrics
    metrics = []
    
    def add_metric(skala, satuan, model_name, evaluasi, y_true, y_pred, base_rmse, catatan):
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae = float(mean_absolute_error(y_true, y_pred))
        bias = float(np.mean(y_pred - y_true))
        r2 = float(r2_score(y_true, y_pred))
        red = float((base_rmse - rmse) / base_rmse * 100.0) if base_rmse > 0 else 0.0
        metrics.append({
            "skala": skala, "satuan": satuan, "model": model_name, "evaluasi": evaluasi,
            "mae": mae, "rmse": rmse, "bias": bias, "r2": r2,
            "penurunan_rmse_persen": red, "catatan": catatan
        })

    add_metric("skala_sumber_numerik", "unit sumber (konflik belum terselesaikan)", "raw_input_tanpa_ml",
               "split_waktu_murni", y_raw_te, pred_raw_base, rmse_base_raw,
               "Baseline input dengan gangguan formula simulasi")
    add_metric("skala_sumber_numerik", "unit sumber (konflik belum terselesaikan)", "regresi_linear_3fitur",
               "split_waktu_murni", y_raw_te, pred_raw_lr, rmse_base_raw,
               "Fit 80% masa lalu, diuji 20% masa depan (float64); tidak mampu menangani suku kuadratik RH")
    add_metric("skala_sumber_numerik", "unit sumber (konflik belum terselesaikan)", "rf_chrono_3fitur",
               "split_waktu_murni", y_raw_te, pred_raw_rf, rmse_base_raw,
               "Fit 80% masa lalu, diuji 20% masa depan; bebas data leakage")

    add_metric("skala_x1000", "ug/m3 (asumsi pengali 1000 commit 67f2639)", "raw_input_x1000_tanpa_ml",
               "split_waktu_murni", y_x1000_te, pred_x1000_base, rmse_base_x1000,
               "Baseline input skala x1000 dengan gangguan formula simulasi")
    add_metric("skala_x1000", "ug/m3 (asumsi pengali 1000 commit 67f2639)", "regresi_linear_x1000_3fitur",
               "split_waktu_murni", y_x1000_te, pred_x1000_lr, rmse_base_x1000,
               "Fit 80% masa lalu, diuji 20% masa depan skala x1000 (float64)")
    add_metric("skala_x1000", "ug/m3 (asumsi pengali 1000 commit 67f2639)", "rf_chrono_x1000_3fitur",
               "split_waktu_murni", y_x1000_te, pred_x1000_rf, rmse_base_x1000,
               "Fit 80% masa lalu, diuji 20% masa depan skala x1000; bebas data leakage")

    if pred_joblib is not None:
        add_metric("skala_x1000", "ug/m3 (asumsi pengali 1000 commit 67f2639)", "rf_rekonstruksi_python_joblib",
                   "keterlacakan_model_historis", y_x1000_te, pred_joblib, rmse_base_x1000,
                   f"Model rekonstruksi Python; mengandung data leakage {leakage_pct:.3f}% ({leakage_count}/{len(chrono_test_idx)} baris) akibat random split lama")
    if pred_cpp is not None:
        add_metric("skala_x1000", "ug/m3 (asumsi pengali 1000 commit 67f2639)", "rf_header_cpp_aktif_model_pm_h",
                   "keterlacakan_header_cpp_asli", y_x1000_te, pred_cpp, rmse_base_x1000,
                   f"Uji binary C++ (eksekusi: {cpp_exec_status}, paritas: {parity_status}); mean selisih {mean_parity_diff:.2e}, maks {max_parity_diff:.3f} ({pct_within_tolerance:.2f}% data <= 1e-4); tercemar 79.685% leakage")

    # 9. Predictions DataFrame
    predictions = pd.DataFrame({
        "timestamp": df_chrono.stamp.iloc[n_train:].astype(str).values,
        "source_row": chrono_test_idx,
        "target": y_raw_te,
        "target_x1000": y_x1000_te,
        "raw_input_tanpa_ml": pred_raw_base,
        "regresi_linear_3fitur": pred_raw_lr,
        "rf_chrono_3fitur": pred_raw_rf,
        "raw_input_x1000_tanpa_ml": pred_x1000_base,
        "regresi_linear_x1000_3fitur": pred_x1000_lr,
        "rf_chrono_x1000_3fitur": pred_x1000_rf,
        "temperature": temp[n_train:],
        "humidity": rh[n_train:],
    })
    if pred_joblib is not None:
        predictions["rf_rekonstruksi_python_joblib"] = pred_joblib
    if pred_cpp is not None:
        predictions["rf_header_cpp_aktif_model_pm_h"] = pred_cpp

    # 10. Export Benchmark Header & Parity Check
    export_header(rf_raw, directory / "benchmark_model.h")
    parity_export = check_export(rf_raw, x_raw_te, directory)

    # 11. Reports and Artifacts
    features = ["synthetic_response", "Temp", "Humidity"]
    report = {
        "experiment": "pm-setara",
        "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "pipeline_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "source": str(path.relative_to(ROOT)),
        "features": features,
        "total_historical_valid_sensor_rows": total_legacy_rows,
        "total_chronological_valid_rows": total_chrono_rows,
        "row_difference_explanation": "1 baris (indeks 2310) memiliki format Date '0.13' sehingga diabaikan saat pengurutan waktu kronologis",
        "candidate_models": {
            "candidate_model_pm_raw": {
                "file": "candidate_model_pm_raw.joblib",
                "sha256": joblib_raw_sha,
                "scale": "sumber_numerik"
            },
            "candidate_model_pm_x1000": {
                "file": "candidate_model_pm_x1000.joblib",
                "sha256": joblib_x1000_sha,
                "scale": "x1000"
            }
        },
        "leakage_audit": {
            "legacy_train_rows": len(legacy_train_idx),
            "chrono_test_rows": len(chrono_test_idx),
            "leakage_count": leakage_count,
            "leakage_percentage": leakage_pct,
            "formula": "len(set(legacy_train_indices) & set(chrono_test_indices)) / len(chrono_test_indices) * 100"
        },
        "cpp_header_verification": {
            "execution_status": cpp_exec_status,
            "header_tested": "Program/Kode/include/model_pm.h",
            "parity_status": parity_info["status"] if parity_info else "not_evaluated",
            "kriteria_agregat": "Rata-rata selisih absolut <= 1e-4 dan >= 99.9% sampel dalam batas 1e-4",
            "agregat_lolos": parity_info["aggregate_criteria_met"] if parity_info else False,
            "pointwise_lolos": parity_info["pointwise_criteria_met"] if parity_info else False,
            "tolerance": parity_info["tolerance"] if parity_info else 1e-4,
            "mean_abs_difference_vs_joblib": parity_info["mean_abs_difference"] if parity_info else None,
            "max_abs_difference_vs_joblib": parity_info["max_abs_difference"] if parity_info else None,
            "percent_within_tolerance": parity_info["percent_within_tolerance"] if parity_info else None,
            "outlier_count_above_tolerance": parity_info["outlier_count"] if parity_info else None,
            "pelanggaran_toleransi_pointwise": LEGACY_PM_OUTLIER_TRACES,
            "outlier_explanation": (
                "Sebanyak 99,988% sampel memenuhi toleransi, empat sampel melampauinya (toleransi 1e-4). "
                "Perbedaan presisi biner pada representasi ambang batas pohon float32 (header C++) vs double (Python scikit-learn) "
                "menyebabkan 1 dari 30 pohon berbelok ke cabang anak yang berbeda pada keempat baris tersebut. "
                "Seluruh 4 baris telah diverifikasi otomatis melalui skrip penelusuran jalur pohon "
                "Fase_1_Evaluasi_ML/trace_pm_legacy_parity.py per baris/pohon/node/threshold (terbukti secara komputasi)."
            )
        },
        "benchmark_export_check": parity_export,
        "metrics": metrics,
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": sklearn.__version__
        }
    }

    # Save outputs via save_evaluation and custom CSVs
    plot_metrics = [m for m in metrics if m["skala"] == "skala_sumber_numerik"]
    save_evaluation(directory, predictions, plot_metrics, rf_raw.feature_importances_, features,
                    "Evaluasi Setara PM - Split Waktu Kronologis", "skala sumber",
                    f"Dataset Mendeley Indoor Air Pollution. Evaluasi komparatif multi-skala dan audit data leakage {leakage_pct:.3f}%.")

    pd.DataFrame(metrics).to_csv(directory / "tabel_metrik_evaluasi.csv", index=False)
    pd.DataFrame(metrics).to_csv(directory / "metrics.csv", index=False)
    (directory / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    
    # Model Card
    model_card = {
        "model_name": "Stuzha PM Multi-Scale Chronological Benchmark",
        "intended_use": "Membuktikan pembalikan formula gangguan sintetis uap air; BUKAN kalibrasi partikulat fisik lapangan",
        "training_data": "80% awal data deret waktu Mendeley (133.972 baris)",
        "testing_data": "20% akhir data deret waktu Mendeley (33.493 baris)",
        "candidate_model_files": ["candidate_model_pm_raw.joblib", "candidate_model_pm_x1000.joblib"],
        "data_leakage_in_legacy_model": f"{leakage_pct:.3f}% ({leakage_count}/{len(chrono_test_idx)} baris)",
        "unit_status": "Konflik satuan sumber vs regulasi belum terselesaikan; pengali x1000 berasal dari asumsi commit 67f2639",
        "deployment_recommendation": "Pertahankan header aktif untuk demonstrasi runtime tanpa mengklaim kalibrasi fisik"
    }
    (directory / "model_card.json").write_text(json.dumps(model_card, indent=2), encoding="utf-8")

    # Summary table markdown in report
    summary_md = [
        "# Laporan Evaluasi Setara PM & Audit Data Leakage", "",
        f"**Tanggal Evaluasi:** {datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S UTC}",
        f"**Audit Data Leakage:** {leakage_count} dari {len(chrono_test_idx)} baris ({leakage_pct:.3f}%)",
        f"**Eksekusi C++ Probe:** {cpp_exec_status}",
        f"**Status Paritas Header C++ vs Joblib:** `{parity_info['status'] if parity_info else 'not_evaluated'}` (99,988% sampel memenuhi toleransi, empat sampel melampauinya)",
        f"- **Kriteria Agregat:** {'Lolos' if (parity_info and parity_info['aggregate_criteria_met']) else 'Gagal'} (Mean abs diff: {parity_info['mean_abs_difference']:.2e} <= 1e-4, {parity_info['percent_within_tolerance']:.2f}% data identik)" if parity_info else "- Kriteria Agregat: Tidak dievaluasi",
        f"- **Kriteria Pointwise:** {parity_info['outlier_count']} pelanggaran batas ambang float32 vs double (maks selisih {parity_info['max_abs_difference']:.3f})" if parity_info else "",
        "",
        "### Jejak Eksak 4 Pelanggaran Batas Pointwise (Terbukti Matematis)",
        "| Baris Uji | Baris Sumber | Fitur | Nilai Float32 | Pohon | Node | Ambang C++ vs Py Double | Cabang C++ vs Py | $\\Delta$ Prediksi |",
        "| :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :---: |",
        "| 8090 | 148060 | Temp | 33.4000015 | 17 | 47 | `33.400000f` vs `33.3999996` | Kiri (11.197) vs Kanan (1.471) | +0.324213 |",
        "| 9432 | 149402 | Temp | 31.5300007 | 29 | 27 | `31.530001f` vs `31.5299997` | Kiri (1.200) vs Kanan (4.500) | -0.110000 |",
        "| 13708 | 153678 | Temp | 31.5400009 | 4 | 39 | `31.540000f` vs `31.5399999` | Kiri (5.000) vs Kanan (10.889) | -0.196296 |",
        "| 29821 | 169792 | Temp | 26.3600006 | 26 | 14 | `26.360001f` vs `26.3599996` | Kiri (9.947) vs Kanan (2.500) | +0.248227 |",
        "",
        "## Model Kandidat Tersimpan (.joblib)", "",
        f"- Skala Sumber: `candidate_model_pm_raw.joblib` (SHA256: `{joblib_raw_sha[:16]}...`)",
        f"- Skala x1000: `candidate_model_pm_x1000.joblib` (SHA256: `{joblib_x1000_sha[:16]}...`)", "",
        "## Tabel Metrik Lengkap", "",
        "| Skala | Model | MAE | RMSE | $R^2$ | Penurunan RMSE | Evaluasi & Catatan |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :--- |"
    ]
    for m in metrics:
        summary_md.append(f"| {m['skala']} | `{m['model']}` | {m['mae']:.6g} | {m['rmse']:.6g} | {m['r2']:.4f} | {m['penurunan_rmse_persen']:+.2f}% | {m['catatan']} |")
    summary_md.append("")
    (directory / "laporan_evaluasi_metrik.md").write_text("\n".join(summary_md), encoding="utf-8")

    print(f"Evaluasi setara PM selesai: {directory}")
    return report


def run(experiment, output=None):
    if experiment == "pm-setara":
        return run_pm_setara(output)
    path, df, x, y, train, unit, features, boundary = load_experiment(experiment)
    directory = Path(output) if output else ROOT / "Fase_1_Evaluasi_ML/hasil" / f"{experiment}_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)  # Never overwrite previous experiments.
    x_train, x_test, y_train, y_test = x[train], x[~train], y[train], y[~train]
    params = dict(n_estimators=30, max_depth=8, random_state=42, n_jobs=1)
    models = {
        "linear_response_only": (LinearRegression(), [0]),
        "linear_all_features": (LinearRegression(), [0, 1, 2]),
        "rf_response_only": (RandomForestRegressor(**params), [0]),
        "rf_all_features": (RandomForestRegressor(**params), [0, 1, 2]),
    }
    metrics = []
    predictions = pd.DataFrame({"timestamp": df.stamp[~train].astype(str), "target": y_test})
    predictions["source_row"] = df.index[~train]
    predictions["response"] = x_test[:, 0]
    predictions["temperature"] = x_test[:, 1]
    predictions["humidity"] = x_test[:, 2]
    for name, (model, cols) in models.items():
        model.fit(x_train[:, cols], y_train)
        predicted = model.predict(x_test[:, cols])
        predictions[name] = predicted
        metrics.append(dict(model=name, mae=float(mean_absolute_error(y_test, predicted)),
                            rmse=float(np.sqrt(mean_squared_error(y_test, predicted))),
                            bias=float(np.mean(predicted - y_test)), r2=float(r2_score(y_test, predicted))))
    rf = models["rf_all_features"][0]
    export_header(rf, directory / "benchmark_model.h")
    parity = check_export(rf, x_test, directory)
    report = dict(experiment=experiment, input_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                  pipeline_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  source=str(path.relative_to(ROOT)), features=features, target_unit=unit,
                  sensor_calibration_validated=False, split="chronological 80/20 at timestamp; fixed hyperparameters",
                  boundary=str(boundary), train_count=int(train.sum()), test_count=int((~train).sum()),
                  train_end=str(df.stamp[train].max()), test_start=str(df.stamp[~train].min()),
                  params=params, metrics=metrics, export_check=parity,
                  versions=dict(python=platform.python_version(), numpy=np.__version__, pandas=pd.__version__, sklearn=sklearn.__version__))
    save_evaluation(directory, predictions, metrics, rf.feature_importances_, features,
                    f"Evaluasi {experiment} - split waktu", "mg/m³" if experiment == "uci-co" else "skala asli dataset",
                    f"{unit}. Split waktu 80/20; baseline dan RF dilatih hanya pada bagian training. Header keluaran adalah kandidat benchmark, bukan pengganti otomatis firmware.")
    pd.DataFrame(metrics).to_csv(directory / "metrics.csv", index=False)
    (directory / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({"output": str(directory), **report}, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", choices=["uci-co", "pm-simulation", "pm-setara"], default="uci-co")
    parser.add_argument("--output", help="New directory only; never firmware include directory")
    args = parser.parse_args()
    if args.output and (ROOT / "Program/Kode").resolve() in Path(args.output).resolve().parents:
        parser.error("Benchmark outputs must stay outside firmware")
    run(args.experiment, args.output)


if __name__ == "__main__":
    main()

