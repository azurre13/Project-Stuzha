"""Evaluasi Setara PM (GP2Y1010AU0F) - Multi-Skala & Bebas Data Leakage.

Skrip ini menjalankan evaluasi komparatif multi-skala melalui pipeline terpadu:
1. Split waktu murni (80% masa lalu untuk training, 20% masa depan untuk testing).
2. Perhitungan data leakage secara dinamis menggunakan irisan indeks baris asli.
3. Evaluasi multi-skala (skala sumber 0-0.47 dan skala x1000).
4. Pengujian keterlacakan model historis:
   - Model rekonstruksi Python (.joblib)
   - Header C++ aktif fisik (model_pm.h) via kompilasi g++
5. Seluruh keluaran (prediksi per baris, metrik, grafik PNG, model card, report)
   disimpan dalam folder run baru di Fase_1_Evaluasi_ML/hasil/.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ml_training"))
from pipeline import run

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", help="Direktori baru output; jangan menimpa folder lama")
    args = parser.parse_args()
    report = run("pm-setara", args.output)
    return report

if __name__ == "__main__":
    main()
