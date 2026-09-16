"""CSV, PNG and readable reports shared by the Stuzha evaluation workflows."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def save_comparison(directory, metrics):
    """Compare RF against an explicit baseline on the same test observations."""
    indexed = {m['model']: m for m in metrics}
    base_name = 'linear_all_features' if 'linear_all_features' in indexed else metrics[0]['model']
    rf_candidates = [m['model'] for m in metrics if 'rf' in m['model'].lower() or 'forest' in m['model'].lower()]
    rf_name = 'rf_all_features' if 'rf_all_features' in indexed else ('random_forest' if 'random_forest' in indexed else (rf_candidates[0] if rf_candidates else metrics[-1]['model']))
    baseline, rf = indexed[base_name], indexed[rf_name]
    rows = []
    for key in ('rmse', 'mae'):
        before, after = float(baseline[key]), float(rf[key])
        rows.append(dict(baseline=base_name, model=rf_name, metrik=key.upper(),
                         sebelum=before, sesudah_ml=after,
                         penurunan_error_persen=100*(before-after)/before if before else np.nan))
    pd.DataFrame(rows).to_csv(directory / 'perbandingan_sebelum_sesudah.csv', index=False)
    lines = ['## Perbandingan sebelum dan sesudah ML', '',
             f'Pembanding: {base_name}; model ML: {rf_name}. Keduanya dinilai pada data uji yang sama.', '',
             '| Metrik | Pembanding | Setelah RF | Penurunan error |', '|---|---:|---:|---:|']
    for row in rows:
        lines.append(f"| {row['metrik']} | {row['sebelum']:.8g} | {row['sesudah_ml']:.8g} | {row['penurunan_error_persen']:.2f}% |")
    lines += ['', 'Rumus: 100 × (error pembanding − error RF) / error pembanding. Nilai negatif berarti RF lebih buruk. Persentase ini adalah perubahan error pada eksperimen dataset, bukan persentase akurasi sensor fisik atau peningkatan firmware baru atas firmware lama.', '',
              '[Unduh tabel perbandingan CSV](perbandingan_sebelum_sesudah.csv)', '']
    return '\n'.join(lines)


def save_evaluation(directory, predictions, metrics, importances, features, title, unit, notes):
    """Plot only actual held-out predictions; retain all rows in CSV."""
    directory.mkdir(parents=True, exist_ok=True)
    graphics = directory / "grafik"
    graphics.mkdir(exist_ok=True)
    predictions.to_csv(directory / "test_predictions.csv", index=False)
    pd.DataFrame(metrics).to_csv(directory / "tabel_metrik_evaluasi.csv", index=False)
    pd.DataFrame({"feature": features, "importance": importances}).to_csv(
        directory / "feature_importance.csv", index=False)
    names = [row["model"] for row in metrics]
    sample = predictions.iloc[np.linspace(0, len(predictions)-1, min(2500, len(predictions)), dtype=int)]
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})

    def finish(fig, filename):
        fig.suptitle(title, fontsize=13)
        fig.text(.5, .01, "Evaluasi data uji model; bukan pengukuran akurasi sensor rakitan.", ha="center", fontsize=9)
        fig.tight_layout(rect=(0, .04, 1, .94))
        fig.savefig(graphics / filename, dpi=300)
        plt.close(fig)

    nrows = max(1, (len(names) + 1) // 2)
    fig, axes = plt.subplots(nrows, 2, figsize=(12, 4.5 * nrows), squeeze=False)
    for ax, metric in zip(axes.flat, metrics):
        name = metric["model"]
        ax.scatter(sample.target, sample[name], s=7, alpha=.35, rasterized=True)
        lo = min(predictions.target.min(), predictions[name].min())
        hi = max(predictions.target.max(), predictions[name].max())
        ax.plot([lo, hi], [lo, hi], "--", color="black", lw=1)
        ax.set(xlabel=f"Target ({unit})", ylabel=f"Prediksi ({unit})",
               title=f"{name}\nR²={metric['r2']:.5f}; RMSE={metric['rmse']:.5g}")
    for ax in list(axes.flat)[len(names):]:
        ax.set_visible(False)
    finish(fig, "1_target_vs_prediksi.png")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for name in (names[0], names[-1]):
        residual = sample[name] - sample.target
        axes[0].scatter(sample.humidity, residual, s=7, alpha=.3, label=name)
        axes[1].hist(predictions[name] - predictions.target, bins=60, alpha=.5, label=name)
    axes[0].axhline(0, color="black", lw=1)
    axes[0].set(xlabel="Kelembapan (%)", ylabel=f"Prediksi - target ({unit})", title="Residual terhadap kelembapan")
    axes[1].set(xlabel=f"Prediksi - target ({unit})", ylabel="Jumlah data uji", title="Distribusi residual")
    for ax in axes: ax.legend(fontsize=8)
    finish(fig, "2_residual_dan_kelembapan.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(features, importances, color="#267d9d")
    ax.bar_label(bars, labels=[f"{v:.1%}" for v in importances], padding=4)
    ax.set(xlim=(0, 1.12), xlabel="Feature importance RF (impurity)", title="Bobot fitur pada model RF tiga fitur")
    finish(fig, "3_feature_importance.png")

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, key in zip(axes, ("mae", "rmse", "r2")):
        ax.bar(range(len(names)), [m[key] for m in metrics], color="#267d9d")
        ax.set_xticks(range(len(names)), [n.replace("_", "\n") for n in names], fontsize=8)
        ax.set(title=key.upper(), ylabel=unit if key != "r2" else "R²")
    finish(fig, "4_perbandingan_metrik.png")

    lines = [f"# {title}", "", notes, "", f"Satuan angka evaluasi: {unit}.", "",
             "| Model | MAE | RMSE | Bias | R² |", "|---|---:|---:|---:|---:|"]
    for m in metrics:
        lines.append(f"| {m['model']} | {m['mae']:.8g} | {m['rmse']:.8g} | {m['bias']:.8g} | {m['r2']:.8g} |")
    lines += ['', save_comparison(directory, metrics)]
    lines += ["", f"CSV berisi seluruh {len(predictions):,} baris uji. Scatter menampilkan maksimal 2.500 baris yang dipilih merata menurut urutan data; metrik memakai seluruh baris.",
              "", "[Prediksi CSV](test_predictions.csv) · [Metrik CSV](tabel_metrik_evaluasi.csv) · [Bobot fitur CSV](feature_importance.csv)", ""]
    for path in sorted(graphics.glob("*.png")):
        lines.append(f"![{path.stem}](grafik/{path.name})\n")
    (directory / "laporan_evaluasi_metrik.md").write_text("\n".join(lines), encoding="utf-8")
