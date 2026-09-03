"""
Skrip Pengunduh Otomatis Dataset Lengkap ThingSpeak (Project Stuzha)
Mendukung pengunduhan data jangka panjang (1 minggu - 1 bulan+) tanpa terpotong batas 8000 baris.
Dikonversi otomatis ke Waktu Indonesia Barat (WIB) dengan nama kolom akademis rapi.
"""

import urllib.request
import urllib.parse
import json
import csv
import os
import sys
from datetime import datetime, timezone, timedelta

# ============================================================
# KONFIGURASI CHANNEL THINGSPEAK
# ============================================================
CHANNEL_ID = "3480764"
# Jika channel dibuat Public (Sharing: Everyone), API_KEY boleh dikosongkan.
# Jika Private, isi dengan Read API Key dari tab API Keys.
READ_API_KEY = ""  

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "data", "Dataset_Project_Stuzha_ThingSpeak_Lengkap.csv")

# Skala Kategori ISPU
KATEGORI_MAP = {
    "1": "Baik",
    "2": "Sedang",
    "3": "Tidak Sehat",
    "4": "Sangat Tidak Sehat",
    "5": "Berbahaya"
}

def fetch_thingspeak_data():
    print("=" * 65)
    print(f" [Project Stuzha] Mengunduh Dataset ThingSpeak (Channel: {CHANNEL_ID})")
    print("=" * 65)

    base_url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json"
    all_feeds = []
    page = 1
    results_per_page = 8000  # Maksimum limit per request dari MathWorks

    # Loop penarikan data berkala (pagination)
    last_entry_id = 0

    while True:
        params = {
            "results": str(results_per_page)
        }
        if READ_API_KEY:
            params["api_key"] = READ_API_KEY
        if last_entry_id > 0:
            params["start"] = str(last_entry_id + 1)

        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        print(f"  --> Menghubungi server ThingSpeak (Batch {page})...", end=" ", flush=True)

        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status != 200:
                    print(f"\n[Error] HTTP Status: {response.status}")
                    break
                data = json.loads(response.read().decode('utf-8'))
        except Exception as e:
            print(f"\n[Error] Gagal mengambil data: {e}")
            break

        feeds = data.get("feeds", [])
        if not feeds:
            print("Selesai (Tidak ada data tambahan).")
            break

        print(f"Berhasil ({len(feeds):,} baris data).")
        all_feeds.extend(feeds)

        # Jika data yang diterima kurang dari batas 8000, berarti ini halaman terakhir
        if len(feeds) < results_per_page:
            break

        last_entry_id = feeds[-1]["entry_id"]
        page += 1

    total = len(all_feeds)
    print("\n" + "-" * 65)
    print(f" Total data yang berhasil ditarik: {total:,} baris.")
    print("-" * 65)

    if total == 0:
        print("[Peringatan] Tidak ada baris data yang ditemukan. Pastikan Channel sudah Public atau Read API Key sudah diisi.")
        return

    # Pastikan folder target ada
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    # Tulis ke file CSV berstandar ilmiah
    wib_offset = timezone(timedelta(hours=7))

    headers = [
        "Timestamp_UTC",
        "Timestamp_WIB",
        "Entry_ID",
        "Suhu_C",
        "Kelembapan_RH_Persen",
        "PM25_Calibrated_ug_m3",
        "CO_Calibrated_ppm",
        "ISPU_Final",
        "Kipas_PWM_Persen",
        "Raw_VOC_ADC",
        "Kategori_ISPU_Kode",
        "Kategori_ISPU_Teks"
    ]

    print(f" Menyimpan data ke: {OUTPUT_FILE} ...")
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for item in all_feeds:
            # Konversi UTC ke WIB
            utc_str = item.get("created_at", "")
            wib_str = ""
            if utc_str:
                try:
                    dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
                    dt_wib = dt_utc.astimezone(wib_offset)
                    wib_str = dt_wib.strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    wib_str = utc_str

            entry_id = item.get("entry_id", "")
            f1 = item.get("field1", "")
            f2 = item.get("field2", "")
            f3 = item.get("field3", "")
            f4 = item.get("field4", "")
            f5 = item.get("field5", "")
            f6 = item.get("field6", "")
            f7 = item.get("field7", "")
            f8 = item.get("field8", "")

            kat_code = str(int(float(f8))) if (f8 and f8.strip()) else ""
            kat_teks = KATEGORI_MAP.get(kat_code, "")

            writer.writerow([
                utc_str,
                wib_str,
                entry_id,
                f1, f2, f3, f4, f5, f6, f7,
                kat_code,
                kat_teks
            ])

    print(" [SUKSES] Dataset lengkap berhasil disimpan dan siap dibuka di Excel / Python!")
    print(f" Ukuran file: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")

if __name__ == "__main__":
    fetch_thingspeak_data()
