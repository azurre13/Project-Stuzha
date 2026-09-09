"""Recover the original training experiment without changing deployed headers.

This is a reproducibility audit, NOT a new physical calibration. Output is a new
run directory with fitted models, reconstructed headers and numerical checks.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from pipeline import export_header, check_export
from evaluation_outputs import save_evaluation

ROOT = Path(__file__).resolve().parents[1]


def run(output=None):
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    source = subprocess.check_output(["git", "show", f"{revision}:ml_training/train_models.py"], cwd=ROOT).decode("utf-8")
    # Load only the already-inspected exporter function; do not run legacy main
    # or its top-level output-directory creation and overwrite behavior.
    fn = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "export_rf_to_c_header")
    namespace = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "legacy_exporter", "exec"), namespace)
    export = namespace["export_rf_to_c_header"]
    directory = Path(output).resolve() if output else ROOT / "Fase_1_Evaluasi_ML/hasil" / f"reproduksi_awal_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"
    firmware = (ROOT / "Program/Kode").resolve()
    if directory == firmware or firmware in directory.parents:
        raise ValueError("Evaluation outputs must stay outside firmware")
    directory.mkdir(parents=True, exist_ok=False)
    report = {"scope": "reproduction of original random-split/synthetic/mapped-input experiment; not physical calibration",
              "legacy_git_revision": revision, "legacy_script_sha256": hashlib.sha256(source.encode()).hexdigest(),
              "audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "versions": {"numpy": np.__version__, "pandas": pd.__version__, "sklearn": sklearn.__version__}, "models": {}}
    protected = {name: hashlib.sha256((ROOT/f"Program/Kode/include/model_{name}.h").read_bytes()).hexdigest() for name in ("pm", "co")}
    for name in ("pm", "co"):
        if name == "pm":
            path=ROOT/"Program/data/mendeley/Indoor_Air_Pollution_Data.csv"
            df=pd.read_csv(path,low_memory=False)[["PM2.5","Temp","Humidity"]].apply(pd.to_numeric,errors="coerce").dropna()
            df=df[df.Temp.between(10,45)&df.Humidity.between(20,95)&(df["PM2.5"]>=0)]
            y=df["PM2.5"].to_numpy()*1000
            temp,rh=df.Temp.to_numpy(),df.Humidity.to_numpy()
            random=np.random.RandomState(42)
            response=np.clip(y*(1+0.65*(rh/100)**2)+(temp-25)*0.45+random.normal(0,2.5,len(y)),0,600)
            x=np.column_stack([response,temp,rh]);features=["raw_pm_ug","temp","humidity"]
            assumptions={"target": "source numeric PM times 1000; physical unit conflict unresolved",
                         "input": "synthetic humidity/temperature/noise perturbation of target, not recorded GP raw"}
        else:
            path=ROOT/"Program/data/uci/AirQualityUCI.csv"
            df=pd.read_csv(path,sep=";",decimal=",")[["CO(GT)","PT08.S1(CO)","T","RH"]].apply(pd.to_numeric,errors="coerce").dropna()
            df=df[(df["CO(GT)"]>0)&(df["PT08.S1(CO)"]>0)&(df["T"]>-50)&(df.RH>0)]
            raw=df["PT08.S1(CO)"].to_numpy();response=800+(raw-raw.min())/(raw.max()-raw.min())*2800
            y=df["CO(GT)"].to_numpy();x=np.column_stack([response,df["T"].to_numpy(),df.RH.to_numpy()])
            features=["raw_co_adc","temp","humidity"]
            assumptions={"target": "CO(GT) mg/m3, not ppm", "input": "PT08.S1 min/max mapped to ADC scale; not a validated MQ7 relationship",
                         "pt08_min_all_data": float(raw.min()),"pt08_max_all_data": float(raw.max())}
        xt,xv,yt,yv,rows_train,rows_test=train_test_split(x,y,df.index.to_numpy(),test_size=0.2,random_state=42)
        model=RandomForestRegressor(n_estimators=30,max_depth=8,random_state=42,n_jobs=1).fit(xt,yt)
        prediction=model.predict(xv)
        baseline = xv[:, 0] if name == "pm" else LinearRegression().fit(xt[:, :1], yt).predict(xv[:, :1])
        baseline_name = "input_sintetis" if name == "pm" else "linear_training_only"
        metrics = []
        for label, values in ((baseline_name, baseline), ("random_forest", prediction)):
            metrics.append(dict(model=label, mae=float(mean_absolute_error(yv, values)),
                                rmse=float(np.sqrt(mean_squared_error(yv, values))),
                                bias=float(np.mean(values-yv)), r2=float(r2_score(yv, values))))
        predictions = pd.DataFrame(dict(source_row=rows_test, target=yv, response=xv[:, 0],
                                        temperature=xv[:, 1], humidity=xv[:, 2]))
        predictions[baseline_name] = baseline
        predictions["random_forest"] = prediction
        save_evaluation(directory / name, predictions, metrics, model.feature_importances_,
                        ["Respons sintetis" if name == "pm" else "PT08 skala legacy", "Suhu", "Kelembapan"],
                        f"Reproduksi model awal {name.upper()} - split acak",
                        "skala PM legacy (sumber x1000)" if name == "pm" else "mg/m³",
                        "Training RF mengikuti prosedur awal. PM memakai input sintetis dan skala legacy; CO memakai PT08 yang dipetakan. "
                        "Baseline CO kini hanya fit training, sehingga dapat berbeda dari baseline arsip yang memakai seluruh data. "
                        "Hasil ini bukan bukti kalibrasi sensor fisik dan tidak mengganti header firmware.")
        output=directory/f"model_{name}.h"
        export(model,features,f"model_{name}",f"model_{name}",str(output))
        active=ROOT/f"Program/Kode/include/model_{name}.h"
        normalized=lambda p:p.read_text(encoding="utf-8").replace("\r\n","\n")
        same=normalized(output)==normalized(active)
        joblib.dump(model,directory/f"model_{name}.joblib")
        candidate=directory/f"{name}_candidate"
        candidate.mkdir()
        # New exact-threshold export is paired with the stored fitted estimator.
        # It stays in this run; promotion to firmware is a separate versioned step.
        export_header(model,candidate/"benchmark_model.h")
        candidate_check=check_export(model,xv.astype(np.float32),candidate)
        # Numerical agreement of the ACTUAL deployed header on held-out inputs.
        probe=xv[::max(1,len(xv)//1000)].astype(np.float32)
        cpp=directory/f"probe_{name}.cpp";exe=directory/f"probe_{name}.exe"
        cpp.write_text(f'#include <cstdio>\n#include "{active.as_posix()}"\nint main(){{float x[3];while(scanf("%f %f %f",&x[0],&x[1],&x[2])==3)printf("%.9g\\n",model_{name}_predict(x));}}\n')
        subprocess.run(["g++","-std=c++11","-O2",str(cpp),"-o",str(exe)],check=True,capture_output=True)
        text="\n".join(" ".join(format(float(a),".9g") for a in row) for row in probe)
        actual=np.fromstring(subprocess.run([str(exe)],input=text,text=True,capture_output=True,check=True).stdout,sep="\n")
        expected=model.predict(probe)
        if len(actual)!=len(expected):raise RuntimeError("Incomplete header probe output")
        error=np.abs(actual-expected)
        report["models"][name]={"assumptions":assumptions,"dataset_sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "features":features,"train_count":len(xt),"test_count":len(xv),"header_source_matches_ignoring_line_endings":same,
            "active_header_sha256":protected[name],"mae_source_domain":float(mean_absolute_error(yv,prediction)),
            "rmse_source_domain":float(np.sqrt(mean_squared_error(yv,prediction))),"r2_source_domain":float(r2_score(yv,prediction)),
            "actual_header_probes":len(probe),"header_probe_max_abs_error":float(error.max()),
            "header_probe_mean_abs_error":float(error.mean()),"candidate_export_check":candidate_check,
            "physical_calibration_validated":False}
        print(name, "header match:",same,"probe max error:",float(error.max()),flush=True)
    for name,digest in protected.items():assert hashlib.sha256((ROOT/f"Program/Kode/include/model_{name}.h").read_bytes()).hexdigest()==digest
    (directory/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    (directory/"laporan_evaluasi_metrik.md").write_text(
        "# Hasil reproduksi training awal\n\n"
        "- [PM: CSV dan grafik PNG](pm/laporan_evaluasi_metrik.md)\n"
        "- [CO: CSV dan grafik PNG](co/laporan_evaluasi_metrik.md)\n\n"
        "Model dan kandidat header tersimpan di folder ini; firmware aktif tidak diganti.\n", encoding="utf-8")
    print(json.dumps({"output":str(directory),**report},indent=2))
    return directory


if __name__=="__main__":
    run()
