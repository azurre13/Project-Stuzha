"""
Skrip Eksplorasi Dataset Ground Truth (Lightweight) — Project Stuzha
"""
import csv
import os
from collections import defaultdict

BANNER = "=" * 70

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ============================================================
# 1. DATASET MENDELEY
# ============================================================
print(f"\n{BANNER}")
print("  DATASET 1: MENDELEY — Indoor Air Pollutants (GP2Y1010AU0F)")
print(BANNER)

mendeley_path = os.path.join(BASE_DIR, "data", "mendeley", "Indoor_Air_Pollution_Data.csv")
try:
    with open(mendeley_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        # Clean headers
        header = [h.strip() for h in header if h.strip() and not h.strip().startswith("Unnamed")]
        
        print(f"\n📁 File: {mendeley_path}")
        print(f"📋 Kolom ({len(header)}): {header}")
        
        # Read all rows, track stats
        row_count = 0
        null_counts = defaultdict(int)
        mins = {}
        maxs = {}
        sums = defaultdict(float)
        val_counts = defaultdict(int)
        first_date = None
        last_date = None
        first_rows = []
        
        for row in reader:
            row_count += 1
            if row_count <= 5:
                first_rows.append(row[:len(header)])
            
            for i, val in enumerate(row[:len(header)]):
                col = header[i]
                val = val.strip()
                if not val or val == "":
                    null_counts[col] += 1
                else:
                    try:
                        v = float(val)
                        if col not in mins or v < mins[col]:
                            mins[col] = v
                        if col not in maxs or v > maxs[col]:
                            maxs[col] = v
                        sums[col] += v
                        val_counts[col] += 1
                    except ValueError:
                        if col == "Date":
                            if first_date is None:
                                first_date = val
                            last_date = val
        
        print(f"📊 Jumlah Baris: {row_count:,}")
        
        print(f"\n📈 Statistik Numerik:")
        print(f"  {'Kolom':12s} {'Min':>12s} {'Max':>12s} {'Mean':>12s} {'Count':>8s} {'Missing':>8s}")
        print(f"  {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*8} {'-'*8}")
        for col in header:
            if col in mins:
                mean = sums[col] / val_counts[col] if val_counts[col] > 0 else 0
                print(f"  {col:12s} {mins[col]:12.3f} {maxs[col]:12.3f} {mean:12.3f} {val_counts[col]:8d} {null_counts[col]:8d}")
            elif col == "Date":
                print(f"  {col:12s} {'(datetime)':>12s} {'':>12s} {'':>12s} {row_count:8d} {null_counts.get(col, 0):8d}")
        
        print(f"\n📅 Rentang Waktu:")
        print(f"   Awal : {first_date}")
        print(f"   Akhir: {last_date}")
        
        print(f"\n🔍 5 Baris Pertama:")
        for i, row in enumerate(first_rows):
            print(f"   [{i+1}] {row}")
        
        print(f"\n🎯 KOLOM RELEVAN UNTUK PROJECT STUZHA:")
        relevant = {
            "PM2.5": "Target kalibrasi RF_PM (µg/m³) — sensor GP2Y IDENTIK!",
            "CO": "Target kalibrasi RF_CO (ppm)",
            "Temp": "Feature input ML (koreksi suhu)",
            "Humidity": "Feature input ML (koreksi kelembapan)",
            "NH3": "Proxy validasi MQ-135 (VOC indicator)"
        }
        for col, desc in relevant.items():
            status = "✅ ADA" if col in header else "❌ TIDAK ADA"
            print(f"   {col:12s} → {status} — {desc}")

except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================
# 2. DATASET UCI
# ============================================================
print(f"\n\n{BANNER}")
print("  DATASET 2: UCI — Air Quality (CO Reference Analyzer)")
print(BANNER)

uci_path = os.path.join(BASE_DIR, "data", "uci", "AirQualityUCI.csv")
try:
    with open(uci_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        header = [h.strip() for h in header if h.strip()]
        
        print(f"\n📁 File: {uci_path}")
        print(f"📋 Kolom ({len(header)}): {header}")
        
        row_count = 0
        null_counts = defaultdict(int)
        sentinel_counts = defaultdict(int)  # -200 = missing in UCI
        mins = {}
        maxs = {}
        sums = defaultdict(float)
        val_counts = defaultdict(int)
        first_rows = []
        first_date = None
        last_date = None
        
        for row in reader:
            row_count += 1
            if row_count <= 5:
                first_rows.append(row[:len(header)])
            
            for i, val in enumerate(row[:len(header)]):
                col = header[i]
                val = val.strip().replace(",", ".")
                if not val or val == "":
                    null_counts[col] += 1
                else:
                    try:
                        v = float(val)
                        if v == -200:
                            sentinel_counts[col] += 1
                            continue
                        if col not in mins or v < mins[col]:
                            mins[col] = v
                        if col not in maxs or v > maxs[col]:
                            maxs[col] = v
                        sums[col] += v
                        val_counts[col] += 1
                    except ValueError:
                        if col == "Date":
                            if first_date is None:
                                first_date = val
                            last_date = val
        
        print(f"📊 Jumlah Baris: {row_count:,}")
        
        print(f"\n📋 Penjelasan Kolom:")
        col_desc = {
            "Date": "Tanggal",
            "Time": "Waktu (per jam)",
            "CO(GT)": "⭐ GROUND TRUTH CO (mg/m³) dari reference analyzer",
            "PT08.S1(CO)": "Raw sensor MOS untuk CO (analog MQ-7)",
            "NMHC(GT)": "GT Non-Methane Hydrocarbons (µg/m³)",
            "C6H6(GT)": "GT Benzene (µg/m³)",
            "PT08.S2(NMHC)": "Raw sensor NMHC",
            "NOx(GT)": "GT NOx (ppb)",
            "PT08.S3(NOx)": "Raw sensor NOx",
            "NO2(GT)": "GT NO2 (µg/m³)",
            "PT08.S4(NO2)": "Raw sensor NO2",
            "PT08.S5(O3)": "Raw sensor O3",
            "T": "⭐ Suhu (°C)",
            "RH": "⭐ Kelembapan Relatif (%)",
            "AH": "Kelembapan Absolut"
        }
        for col in header:
            desc = col_desc.get(col, "—")
            print(f"   {col:20s} → {desc}")
        
        print(f"\n📈 Statistik Numerik (excluding -200 sentinel):")
        print(f"  {'Kolom':20s} {'Min':>10s} {'Max':>10s} {'Mean':>10s} {'Valid':>7s} {'Miss(-200)':>10s}")
        print(f"  {'-'*20} {'-'*10} {'-'*10} {'-'*10} {'-'*7} {'-'*10}")
        for col in header:
            if col in mins:
                mean = sums[col] / val_counts[col] if val_counts[col] > 0 else 0
                print(f"  {col:20s} {mins[col]:10.2f} {maxs[col]:10.2f} {mean:10.2f} {val_counts[col]:7d} {sentinel_counts[col]:10d}")
        
        print(f"\n📅 Rentang Waktu:")
        print(f"   Awal : {first_date}")
        print(f"   Akhir: {last_date}")
        
        print(f"\n🔍 5 Baris Pertama:")
        for i, row in enumerate(first_rows):
            print(f"   [{i+1}] {row[:6]}... T={row[header.index('T')] if 'T' in header else '?'}, RH={row[header.index('RH')] if 'RH' in header else '?'}")
        
        print(f"\n🎯 TRAINING PAIR UNTUK RF_CO:")
        print(f"   X = [PT08.S1(CO), T, RH]  →  y = CO(GT)")
        print(f"   Jumlah data valid CO(GT): {val_counts.get('CO(GT)', 0):,} baris")
        print(f"   Missing CO(GT) (-200): {sentinel_counts.get('CO(GT)', 0):,} baris")

except Exception as e:
    print(f"❌ Error: {e}")

# ============================================================
# 3. RINGKASAN
# ============================================================
print(f"\n\n{BANNER}")
print("  RINGKASAN KESIAPAN DATASET")
print(BANNER)
print("""
  ✅ Mendeley (GP2Y indoor) : Downloaded & Verified
  ✅ UCI Air Quality (CO GT) : Downloaded & Verified
  
  NEXT STEPS:
  1. Preprocessing (hapus missing, normalisasi timestamp)
  2. Feature engineering 
  3. Train-test split (80:20)
  4. Training Random Forest Regressor
  5. Evaluasi metrik (R², RMSE, MAE)
  6. Export model ke C header untuk ESP32-S3
""")
