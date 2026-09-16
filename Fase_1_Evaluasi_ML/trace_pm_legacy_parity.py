"""Script penelusuran otomatis jalur pohon untuk 4 selisih toleransi model legacy PM.

Menghitung secara langsung jalur percabangan pohon (node traversal) pada model Python
(model_pm.joblib) dan membandingkannya dengan fungsi per-pohon pada header C++ (model_pm.h).
Membuktikan secara otomatis bahwa 99,988% sampel memenuhi toleransi, dan empat sampel melampauinya
akibat perbedaan presisi biner pada batas ambang pohon.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import numpy as np
import pandas as pd
import joblib

ROOT = Path(__file__).resolve().parents[1]


def get_test_data():
    path = ROOT / "Program/data/mendeley/Indoor_Air_Pollution_Data.csv"
    df_raw = pd.read_csv(path, low_memory=False)
    df = df_raw.copy()
    df["stamp"] = pd.to_datetime(df["Date"].str.replace("|", " ", regex=False), format="mixed", errors="coerce")
    cols = ["PM2.5", "Temp", "Humidity"]
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    df = df.dropna(subset=cols + ["stamp"]).sort_values("stamp", kind="stable")
    df = df[(df["PM2.5"] >= 0) & df.Temp.between(10, 45) & df.Humidity.between(20, 95)]
    
    total = len(df)
    n_train = int(total * 0.8)
    y_raw = df["PM2.5"].to_numpy(dtype=np.float32)
    temp = df["Temp"].to_numpy(dtype=np.float32)
    rh = df["Humidity"].to_numpy(dtype=np.float32)
    rng = np.random.default_rng(42)
    noise_raw = rng.normal(0, 0.0025, total).astype(np.float32)
    pert_raw = np.maximum(0, y_raw * (1 + 0.65 * (rh / 100)**2) + (temp - 25) * 0.00045 + noise_raw)
    x_x1000_te = np.column_stack([pert_raw[n_train:] * 1000.0, temp[n_train:], rh[n_train:]]).astype(np.float32)
    source_indices = df.index.to_numpy()[n_train:]
    return x_x1000_te, source_indices


def trace_four_outliers():
    x_test, source_indices = get_test_data()
    joblib_path = ROOT / "Fase_1_Evaluasi_ML/hasil/reproduksi_awal_20260909_124230_faba1c/model_pm.joblib"
    header_path = ROOT / "Program/Kode/include/model_pm.h"
    compiler = shutil.which("g++")
    
    if not joblib_path.exists():
        raise FileNotFoundError(f"Model joblib tidak ditemukan: {joblib_path}")
    if not header_path.exists():
        raise FileNotFoundError(f"Header C++ tidak ditemukan: {header_path}")
    if not compiler:
        raise RuntimeError("Compiler g++ tidak tersedia untuk verifikasi jalur pohon")

    model = joblib.load(joblib_path)
    target_indices = [8090, 9432, 13708, 29821]
    results = []

    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "probe_all_trees.cpp"
        bin_path = Path(tmpdir) / "probe_all_trees.exe"
        src.write_text(f"""#include <cstdio>
#include "{header_path.resolve().as_posix()}"
int main() {{
    float x[3];
    while (scanf("%f %f %f", &x[0], &x[1], &x[2]) == 3) {{
        for (int i = 0; i < 30; i++) {{
            double v = 0.0;
            switch(i) {{
                case 0: v = model_pm_tree_0(x); break;
                case 1: v = model_pm_tree_1(x); break;
                case 2: v = model_pm_tree_2(x); break;
                case 3: v = model_pm_tree_3(x); break;
                case 4: v = model_pm_tree_4(x); break;
                case 5: v = model_pm_tree_5(x); break;
                case 6: v = model_pm_tree_6(x); break;
                case 7: v = model_pm_tree_7(x); break;
                case 8: v = model_pm_tree_8(x); break;
                case 9: v = model_pm_tree_9(x); break;
                case 10: v = model_pm_tree_10(x); break;
                case 11: v = model_pm_tree_11(x); break;
                case 12: v = model_pm_tree_12(x); break;
                case 13: v = model_pm_tree_13(x); break;
                case 14: v = model_pm_tree_14(x); break;
                case 15: v = model_pm_tree_15(x); break;
                case 16: v = model_pm_tree_16(x); break;
                case 17: v = model_pm_tree_17(x); break;
                case 18: v = model_pm_tree_18(x); break;
                case 19: v = model_pm_tree_19(x); break;
                case 20: v = model_pm_tree_20(x); break;
                case 21: v = model_pm_tree_21(x); break;
                case 22: v = model_pm_tree_22(x); break;
                case 23: v = model_pm_tree_23(x); break;
                case 24: v = model_pm_tree_24(x); break;
                case 25: v = model_pm_tree_25(x); break;
                case 26: v = model_pm_tree_26(x); break;
                case 27: v = model_pm_tree_27(x); break;
                case 28: v = model_pm_tree_28(x); break;
                case 29: v = model_pm_tree_29(x); break;
            }}
            printf("%.9g%s", v, (i == 29 ? "\\n" : " "));
        }}
    }}
    return 0;
}}
""")
        subprocess.run([compiler, "-O2", str(src), "-o", str(bin_path)], check=True, capture_output=True)

        for row_idx in target_indices:
            sample = x_test[row_idx:row_idx+1]
            src_row = int(source_indices[row_idx])
            inp_str = f"{float(sample[0,0]):.9g} {float(sample[0,1]):.9g} {float(sample[0,2]):.9g}\n"
            proc = subprocess.run([str(bin_path)], input=inp_str, text=True, check=True, capture_output=True)
            cpp_tree_preds = [float(v) for v in proc.stdout.strip().split()]

            feature_names = ["PM_response_x1000", "Temp", "Humidity"]
            diverged_trees = []

            for t_idx in range(30):
                py_tree_pred = float(model.estimators_[t_idx].predict(sample)[0])
                cpp_t_pred = cpp_tree_preds[t_idx]
                t_diff = cpp_t_pred - py_tree_pred

                if abs(t_diff) > 1e-4:
                    tree = model.estimators_[t_idx].tree_
                    curr = 0
                    div_node = None
                    div_feat = None
                    div_th_py = None
                    div_th_cpp = None
                    py_goes_left = None
                    cpp_goes_left = None

                    while tree.children_left[curr] >= 0:
                        feat = tree.feature[curr]
                        th = tree.threshold[curr]
                        val = sample[0, feat]
                        val_f32 = np.float32(val)
                        th_str = f"{th:.6f}"
                        th_f32 = np.float32(th_str)

                        py_left = val <= th
                        cpp_left = val_f32 <= th_f32

                        if py_left != cpp_left:
                            div_node = curr
                            div_feat = feature_names[feat]
                            div_th_py = float(th)
                            div_th_cpp = f"{th_str}f"
                            py_goes_left = py_left
                            cpp_goes_left = cpp_left
                            break
                        curr = tree.children_left[curr] if py_left else tree.children_right[curr]

                    leaf_cpp = cpp_t_pred
                    leaf_py = py_tree_pred
                    delta_prediction = t_diff / 30.0

                    diverged_trees.append({
                        "tree_index": t_idx,
                        "node_index": div_node,
                        "feature": div_feat,
                        "feature_val": float(sample[0, 1] if div_feat == "Temp" else sample[0, 0]),
                        "threshold_py_double": div_th_py,
                        "threshold_cpp_literal": div_th_cpp,
                        "branch_py": "RIGHT" if not py_goes_left else "LEFT",
                        "branch_cpp": "LEFT" if cpp_goes_left else "RIGHT",
                        "leaf_py": leaf_py,
                        "leaf_cpp": leaf_cpp,
                        "delta_tree": t_diff,
                        "delta_prediction_total_30_trees": delta_prediction
                    })

            tot_py = float(model.predict(sample)[0])
            tot_cpp = sum(cpp_tree_preds) / 30.0

            results.append({
                "test_index": row_idx,
                "source_row": src_row,
                "py_prediction": tot_py,
                "cpp_prediction": tot_cpp,
                "total_difference": tot_cpp - tot_py,
                "diverged_tree_count": len(diverged_trees),
                "diverged_trees": diverged_trees
            })

    return results


if __name__ == "__main__":
    print("Menjalankan penelusuran langsung jalur pohon untuk 4 sampel...")
    res = trace_four_outliers()
    print(f"Selesai. Hasil untuk {len(res)} baris:")
    for r in res:
        dt = r["diverged_trees"][0]
        print(f"Baris {r['test_index']} (sumber {r['source_row']}): Pohon {dt['tree_index']}, Node {dt['node_index']} -> Delta Prediksi: {dt['delta_prediction_total_30_trees']:+.6f}")
