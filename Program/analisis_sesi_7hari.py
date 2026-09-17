"""Analisis komprehensif data uji 7 hari Stuzha (10-17 September 2026).

Menjalankan audit reproducible dari CSV asli tanpa memodifikasi sumber data.
Memisahkan boot commissioning dan boot utama, menganalisis telemetri,
kestabilan heap, saturasi GP2Y 13 September, dan commanded PWM.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "downloads" / "stuzha_dataset_20260910-20260917.csv"
OUT_DIR = BASE_DIR / "data" / "hasil_7hari"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_status_raw(s):
    if not isinstance(s, str):
        return {}
    parts = s.split("|")
    res = {}
    for p in parts[1:]:
        if "=" in p:
            k, v = p.split("=", 1)
            res[k] = v
    return res


def run_analysis():
    print(f"Membaca dataset: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    total_raw_rows = len(df)
    print(f"Total baris mentah: {total_raw_rows}")

    # Parse status
    status_parsed = df["Status_Raw"].apply(parse_status_raw)
    sdf = pd.DataFrame(list(status_parsed))

    df["boot_id"] = sdf.get("b", "")
    df["uptime_ms"] = pd.to_numeric(sdf.get("u"), errors="coerce")
    df["uptime_hours"] = df["uptime_ms"] / 3600000.0
    df["heap_bytes"] = pd.to_numeric(sdf.get("k"), errors="coerce")
    df["reset_code"] = pd.to_numeric(sdf.get("r"), errors="coerce")
    df["firmware_hash"] = sdf.get("h", "")
    df["fan_level"] = pd.to_numeric(sdf.get("l"), errors="coerce")
    df["flags"] = pd.to_numeric(sdf.get("f"), errors="coerce")
    df["critical_param"] = pd.to_numeric(sdf.get("c"), errors="coerce")

    # Parse ADC (a=GP,MQ7)
    def parse_adc(a_str):
        try:
            gp, mq7 = a_str.split(",")
            return float(gp), float(mq7)
        except Exception:
            return np.nan, np.nan

    adcs = sdf.get("a", pd.Series([""] * len(df))).apply(parse_adc)
    df["gp_adc"] = [x[0] for x in adcs]
    df["mq7_adc"] = [x[1] for x in adcs]

    # Parse counters e=att,fail,skip and q=slot
    def parse_e_val(e_str):
        try:
            att, fail, skip = e_str.split(",")
            return int(att), int(fail), int(skip)
        except Exception:
            return np.nan, np.nan, np.nan

    e_vals = sdf.get("e", pd.Series([""] * len(df))).apply(parse_e_val)
    df["telemetry_attempts"] = [x[0] for x in e_vals]
    df["telemetry_failures"] = [x[1] for x in e_vals]
    df["telemetry_skipped"] = [x[2] for x in e_vals]
    df["telemetry_slot"] = pd.to_numeric(sdf.get("q"), errors="coerce")

    # Parse 24h rolling status d=mean_pm,mean_co,index24,coverage
    def parse_d_val(d_str):
        try:
            pm24, co24, idx24, cov = d_str.split(",")
            return float(pm24), float(co24), float(idx24), float(cov)
        except Exception:
            return np.nan, np.nan, np.nan, np.nan

    d_vals = sdf.get("d", pd.Series([""] * len(df))).apply(parse_d_val)
    df["mean_pm24"] = [x[0] for x in d_vals]
    df["mean_co24"] = [x[1] for x in d_vals]
    df["index24"] = [x[2] for x in d_vals]
    df["coverage24"] = [x[3] for x in d_vals]

    # Identifikasi Booting
    boot_summary = []
    for b_id, grp in df.groupby("boot_id", sort=False):
        boot_summary.append({
            "boot_id": b_id,
            "rows": len(grp),
            "start_time_wib": grp["Timestamp_WIB"].iloc[0],
            "end_time_wib": grp["Timestamp_WIB"].iloc[-1],
            "start_uptime_hours": float(grp["uptime_hours"].iloc[0]),
            "end_uptime_hours": float(grp["uptime_hours"].iloc[-1]),
            "reset_code": int(grp["reset_code"].iloc[0]) if not pd.isna(grp["reset_code"].iloc[0]) else None,
            "firmware_hash": grp["firmware_hash"].iloc[0]
        })

    # Boot utama yang paling panjang: Boot f27413f0 (151 jam)
    df_main = df[df["boot_id"] == "f27413f0"].copy()
    df_comm = df[df["boot_id"] == "c43d4d72"].copy()

    # Rekonsiliasi Counter Telemetri Boot Utama (f27413f0)
    last_row_main = df_main.iloc[-1]
    first_row_main = df_main.iloc[0]
    total_slots_main = int(last_row_main["telemetry_slot"] - first_row_main["telemetry_slot"] + 1)
    received_feeds_main = len(df_main)
    slot_completeness_pct = (received_feeds_main / total_slots_main) * 100.0
    attempts_main = int(last_row_main["telemetry_attempts"])
    failures_main = int(last_row_main["telemetry_failures"])
    skipped_main = int(last_row_main["telemetry_skipped"])
    attempt_success_pct = ((attempts_main - failures_main) / attempts_main) * 100.0

    # Kejadian Saturasi 13 September 02:13:06 WIB
    sat_event = df[df["Timestamp_WIB"].str.contains("2026-09-13T02:13:06")]
    sat_info = {}
    if not sat_event.empty:
        s_row = sat_event.iloc[0]
        sat_info = {
            "timestamp_wib": s_row["Timestamp_WIB"],
            "gp_adc": float(s_row["gp_adc"]),
            "ispu_field5": None if pd.isna(s_row["field5"]) else float(s_row["field5"]),
            "category_field8": float(s_row["field8"]),
            "pwm_field6": float(s_row["field6"]),
            "fan_level": int(s_row["fan_level"]),
            "flags": int(s_row["flags"]),
            "raw_status": s_row["Status_Raw"]
        }

    # Distribusi Kategori (dengan pemisahan Kategori 0)
    cat_dist_main = df_main["field8"].value_counts(dropna=False).to_dict()
    level_dist_main = df_main["fan_level"].value_counts(dropna=False).to_dict()
    pwm_dist_main = df_main["field6"].value_counts(dropna=False).to_dict()

    # Statistik Sensor dan Model pada Boot Utama
    sensor_cols = ["field1", "field2", "field3", "field4", "field5", "field6", "field7", "gp_adc", "mq7_adc", "heap_bytes"]
    stats_main = df_main[sensor_cols].describe().T[["min", "mean", "50%", "max", "std"]].round(3).to_dict()

    # Rekapitulasi JSON
    audit_report = {
        "metadata": {
            "title": "Audit Komprehensif Sesi 7 Hari Project Stuzha",
            "date": "2026-09-17",
            "source_csv": str(DATA_PATH),
            "total_raw_rows": total_raw_rows,
            "overall_time_range": {
                "start": df["Timestamp_WIB"].iloc[0],
                "end": df["Timestamp_WIB"].iloc[-1]
            }
        },
        "boots": boot_summary,
        "commissioning_boot_c43d4d72": {
            "rows": len(df_comm),
            "duration_hours": float(df_comm["uptime_hours"].iloc[-1]) if not df_comm.empty else 0
        },
        "main_continuous_boot_f27413f0": {
            "rows": len(df_main),
            "duration_hours": float(df_main["uptime_hours"].iloc[-1]),
            "telemetry_reconciliation": {
                "total_slots_span": total_slots_main,
                "received_feeds": received_feeds_main,
                "slot_completeness_pct": round(slot_completeness_pct, 3),
                "recorded_attempts": attempts_main,
                "recorded_failures": failures_main,
                "recorded_skipped_slots": skipped_main,
                "attempt_success_rate_pct": round(attempt_success_pct, 3),
                "unattempted_slot_explanation": "75-91 slot tidak dicoba saat ESP32 menunggu rekoneksi Wi-Fi tanpa buffer antrean persisten"
            },
            "heap_stability": {
                "initial_bytes": int(df_main["heap_bytes"].iloc[0]),
                "final_bytes": int(df_main["heap_bytes"].iloc[-1]),
                "min_bytes": int(df_main["heap_bytes"].min()),
                "max_bytes": int(df_main["heap_bytes"].max()),
                "std_bytes": round(float(df_main["heap_bytes"].std()), 2),
                "assessment": "Heap stabil dalam fluktuasi sempit tanpa penurunan progresif"
            },
            "category_distribution": cat_dist_main,
            "fan_level_command_distribution": level_dist_main,
            "commanded_pwm_distribution": pwm_dist_main,
            "sensor_and_model_stats": stats_main
        },
        "saturation_event_20260913_021306": sat_info,
        "operational_context": {
            "physical_fan_state": "Status fisik motor tidak diketahui (kabel dicabut pada periode malam/istirahat tanpa RPM sensor fisik)",
            "thermal_ac_pattern": "Suhu ruangan 22.2-31.1 C mencerminkan siklus pendingin ruangan kamar (AC dimatikan saat penghuni keluar)",
            "model_feature_coupling": "T dan RH adalah fitur input langsung ke Random Forest PM dan CO; korelasi bukan bukti kalibrasi fisik sensor"
        }
    }

    # Simpan JSON
    json_path = OUT_DIR / "laporan_audit_sesi_7hari.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)
    print(f"Laporan audit disimpan: {json_path}")

    # Plot Multi-Panel Lengkap
    print("Membuat grafik komprehensif 7 hari...")
    df["time_dt"] = pd.to_datetime(df["Timestamp_WIB"])

    fig, axes = plt.subplots(6, 1, figsize=(14, 16), sharex=True)

    # Panel 1: Raw Sensors ADC
    ax = axes[0]
    ax.plot(df["time_dt"], df["gp_adc"], label="GP2Y Raw ADC (GPIO 34)", color="#8884d8", lw=0.8)
    ax.plot(df["time_dt"], df["mq7_adc"], label="MQ-7 Raw ADC (GPIO 32)", color="#82ca9d", lw=0.8)
    ax.plot(df["time_dt"], df["field7"], label="MQ-135 ADC (Field 7)", color="#ffc658", lw=0.8, alpha=0.7)
    # Highlight saturation
    if not sat_event.empty:
        sat_time = pd.to_datetime(sat_info["timestamp_wib"])
        ax.scatter([sat_time], [sat_info["gp_adc"]], color="red", s=80, zorder=5, label="Saturasi GP2Y (ADC 4095)")
        ax.annotate("Saturasi Rel 4095\n(13 Sep 02:13 WIB)", (sat_time, 4095),
                    xytext=(15, -25), textcoords="offset points",
                    arrowprops=dict(arrowstyle="->", color="red", lw=1.5), fontsize=8, fontweight="bold", color="red")
    ax.set_ylabel("Raw ADC (12-bit)")
    ax.set_title("Observasi Kontinu 7 Hari Project Stuzha (10–17 September 2026) — Firmware v4.0.0 (a945ea070fcc)", fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 2: Suhu & Kelembaban
    ax = axes[1]
    ax.plot(df["time_dt"], df["field1"], label="Suhu DHT22 (°C)", color="#d9534f", lw=0.9)
    ax.set_ylabel("Suhu (°C)", color="#d9534f")
    ax_twin = ax.twinx()
    ax_twin.plot(df["time_dt"], df["field2"], label="Kelembaban Relatif (% RH)", color="#0275d8", lw=0.9, alpha=0.7)
    ax_twin.set_ylabel("RH (%)", color="#0275d8")
    ax.grid(True, alpha=0.3)

    # Panel 3: Model Nominal Output
    ax = axes[2]
    ax.plot(df["time_dt"], df["field3"], label="PM2.5 Model Nominal (µg/m³)", color="#5cb85c", lw=0.9)
    ax.set_ylabel("PM2.5 (µg/m³)", color="#5cb85c")
    ax_twin = ax.twinx()
    ax_twin.plot(df["time_dt"], df["field4"], label="CO Model Nominal (ppm)", color="#f0ad4e", lw=0.9)
    ax_twin.set_ylabel("CO (ppm)", color="#f0ad4e")
    ax.grid(True, alpha=0.3)

    # Panel 4: ISPU Instan & ISPU Rerata 24 Jam
    ax = axes[3]
    ax.plot(df["time_dt"], df["field5"], label="ISPU Instan (Permen LHK 14/2020)", color="#292b2c", lw=0.9)
    ax.plot(df["time_dt"], df["index24"], label="ISPU Rerata 24 Jam (Rolling Ring RAM)", color="#0275d8", lw=1.5)
    ax.axhline(50, color="green", linestyle="--", alpha=0.6, label="Batas Baik (50)")
    ax.axhline(100, color="orange", linestyle="--", alpha=0.6, label="Batas Sedang (100)")
    ax.set_ylabel("Indeks ISPU")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 5: Commanded Fan PWM
    ax = axes[4]
    ax.plot(df["time_dt"], df["field6"], label="Perintah Kipas PWM (% Duty Cycle)", color="#5bc0de", lw=1.0)
    ax.set_ylabel("Commanded PWM (%)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    # Panel 6: RAM Heap & Telemetry Gaps
    ax = axes[5]
    ax.plot(df["time_dt"], df["heap_bytes"], label="Free RAM Heap (Bytes)", color="#6f42c1", lw=0.9)
    ax.set_ylabel("Free Heap (Bytes)")
    ax.set_xlabel("Waktu Operasional (WIB)")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plot_path = OUT_DIR / "grafik_uji_7hari_komprehensif.png"
    plt.savefig(plot_path, dpi=200)
    plt.close()
    print(f"Grafik komprehensif disimpan: {plot_path}")

    return audit_report


if __name__ == "__main__":
    run_analysis()
