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
import uuid

import numpy as np
import pandas as pd
import sklearn
from evaluation_outputs import save_evaluation
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


def run(experiment, output=None):
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
    parser.add_argument("--experiment", choices=["uci-co", "pm-simulation"], default="uci-co")
    parser.add_argument("--output", help="New directory only; never firmware include directory")
    args = parser.parse_args()
    if args.output and (ROOT / "Program/Kode").resolve() in Path(args.output).resolve().parents:
        parser.error("Benchmark outputs must stay outside firmware")
    run(args.experiment, args.output)


if __name__ == "__main__":
    main()
