"""Run both experiments and save complete CSV/PNG reports inside Fase_1_Evaluasi_ML."""
import argparse
from datetime import datetime, timezone
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ml_training"))
from pipeline import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", choices=["all", "uci-co", "pm-simulation", "legacy-recovery"], default="all")
    parser.add_argument("--output", help="New output directory; existing directories are never overwritten")
    args = parser.parse_args()
    if args.experiment == "legacy-recovery":
        from audit_legacy_training import run as recover
        recover(args.output)
        return
    base = Path(args.output).resolve() if args.output else Path(__file__).resolve().parent / "hasil" / f"evaluasi_{datetime.now(timezone.utc):%Y%m%d_%H%M%S}_{uuid.uuid4().hex[:6]}"
    firmware = Path(__file__).resolve().parents[1] / "Program/Kode"
    if base == firmware or firmware in base.parents:
        parser.error("Output evaluasi harus di luar firmware")
    base.mkdir(parents=True, exist_ok=False)
    experiments = ["pm-simulation", "uci-co"] if args.experiment == "all" else [args.experiment]
    for experiment in experiments:
        run(experiment, base / experiment)
    (base / "laporan_evaluasi_metrik.md").write_text("# Hasil evaluasi Fase 1\n\n" + "\n".join(
        f"- [{name}: tabel CSV dan grafik PNG]({name}/laporan_evaluasi_metrik.md)" for name in experiments), encoding="utf-8")
    print(f"Hasil lengkap: {base}")

if __name__ == "__main__":
    main()
