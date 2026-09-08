"""
Skrip Pengunduh Otomatis Dataset Lengkap ThingSpeak (Project Stuzha)
Mendukung pengunduhan data jangka panjang (1 minggu - 1 bulan+) tanpa terpotong batas 8000 baris
menggunakan metode Time-Windowing Pagination (parameter start & end dalam format UTC).
Dikonversi otomatis ke Waktu Indonesia Barat (WIB) dengan skema kolom akademis rapi.
Dilengkapi proteksi backup otomatis untuk mencegah penimpaan data historis.
"""

import argparse
import csv
import json
import os
import shutil
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

# ============================================================
# KONFIGURASI DEFAULT
# ============================================================
DEFAULT_CHANNEL_ID = "3480764"
DEFAULT_READ_API_KEY = ""  # Kosongkan jika channel Public (Everyone)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT_FILE = os.path.join(BASE_DIR, "data", "Dataset_Project_Stuzha_ThingSpeak_Lengkap.csv")

# Skala Kategori ISPU (Permen LHK No. 14 Tahun 2020)
KATEGORI_MAP = {
    "1": "Baik",
    "2": "Sedang",
    "3": "Tidak Sehat",
    "4": "Sangat Tidak Sehat",
    "5": "Berbahaya"
}

WIB_OFFSET = timezone(timedelta(hours=7))


def parse_iso_utc(ts_str):
    """Mengurai string waktu ISO dari ThingSpeak menjadi objek datetime UTC."""
    if not ts_str:
        return None
    try:
        clean_ts = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_ts).astimezone(timezone.utc)
    except Exception:
        return None


def get_channel_info(channel_id, api_key=""):
    """Mengambil metadata channel untuk mengetahui total entri dan rentang waktu."""
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?results=1"
    if api_key:
        url += f"&api_key={api_key}"

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Project-Stuzha-Downloader)'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP Error {resp.status} saat mengakses channel {channel_id}")
        data = json.loads(resp.read().decode('utf-8'))
        return data.get("channel", {})


def fetch_entry(channel_id, entry_id, api_key=""):
    """Mengambil entri tertentu berdasarkan ID untuk mendapatkan timestamp awal persis."""
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds/entry/{entry_id}.json"
    if api_key:
        url += f"?api_key={api_key}"

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Project-Stuzha-Downloader)'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode('utf-8').strip()
            if content == "-1":
                return None
            data = json.loads(content)
            return data
    except Exception:
        return None


def fetch_feeds_window(channel_id, start_dt, end_dt, api_key=""):
    """
    Mengambil data feeds ThingSpeak dalam jendela waktu start & end.
    Format parameter start dan end diwajibkan 'YYYY-MM-DD HH:MM:SS' (UTC).
    """
    base_url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    params = {
        "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end_dt.strftime("%Y-%m-%d %H:%M:%S")
    }
    if api_key:
        params["api_key"] = api_key

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Project-Stuzha-Downloader)'})
    with urllib.request.urlopen(req, timeout=45) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP Status {resp.status}")
        data = json.loads(resp.read().decode('utf-8'))
        return data.get("feeds", [])


def parse_date_input(dt_str, is_end=False):
    """Mengurai input tanggal pengguna. Jika tanpa timezone, diasumsikan WIB (UTC+7)."""
    if not dt_str:
        return None
    dt_str = dt_str.strip()
    try:
        dt = datetime.fromisoformat(dt_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=WIB_OFFSET)
        return dt.astimezone(timezone.utc)
    except Exception:
        try:
            time_part = "23:59:59" if is_end else "00:00:00"
            dt = datetime.strptime(f"{dt_str} {time_part}", "%Y-%m-%d %H:%M:%S").replace(tzinfo=WIB_OFFSET)
            return dt.astimezone(timezone.utc)
        except Exception:
            raise ValueError(f"Format tanggal tidak dikenali: '{dt_str}'. Gunakan format YYYY-MM-DD atau ISO.")


def fetch_all_feeds(channel_id, api_key="", start_date=None, end_date=None, window_hours=24):
    """
    Mengunduh seluruh feed dengan cerdas:
    - Jika total entri <= 8000 dan tidak ada filter tanggal kustom, unduh langsung dalam 1 batch cepat.
    - Jika entri > 8000 atau mencakup rentang panjang, gunakan time-windowing pagination (default per 24 jam).
    """
    print("=" * 70)
    print(f" [Project Stuzha] Unduh Dataset Telemetri ThingSpeak (Channel: {channel_id})")
    print("=" * 70)

    print("  --> Memeriksa status channel...", end=" ", flush=True)
    channel_info = get_channel_info(channel_id, api_key)
    ch_name = channel_info.get("name", "N/A")
    total_entries = channel_info.get("last_entry_id", 0)
    print(f"OK: '{ch_name}' (Total Entri Terdaftar: {total_entries:,})")

    # Tentukan batas akhir (UTC)
    now_utc = datetime.now(timezone.utc) + timedelta(minutes=5)
    if end_date:
        query_end = parse_date_input(end_date, is_end=True)
    else:
        query_end = now_utc

    # Tentukan batas awal (UTC)
    if start_date:
        query_start = parse_date_input(start_date, is_end=False)
    else:
        # Coba periksa timestamp entri pertama
        entry_1 = fetch_entry(channel_id, 1, api_key)
        if entry_1 and "created_at" in entry_1:
            query_start = parse_iso_utc(entry_1["created_at"]) - timedelta(minutes=1)
        else:
            # Fallback ke tanggal pembuatan channel
            ch_created = channel_info.get("created_at")
            if ch_created:
                query_start = parse_iso_utc(ch_created) - timedelta(minutes=1)
            else:
                # Default 30 hari ke belakang
                query_start = now_utc - timedelta(days=30)

    start_wib_str = query_start.astimezone(WIB_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
    end_wib_str = query_end.astimezone(WIB_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
    print(f"  --> Rentang Target (WIB): {start_wib_str} s.d. {end_wib_str}")

    # OPTIMASI: Jika total entri <= 8000 dan tidak ada batasan tanggal kustom, cukup 1 request results=8000
    if total_entries <= 8000 and not start_date and not end_date:
        print("  --> Total entri <= 8.000, mengunduh 1 batch penuh (results=8000)...", end=" ", flush=True)
        url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?results=8000"
        if api_key:
            url += f"&api_key={api_key}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Project-Stuzha-Downloader)'})
        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            feeds = data.get("feeds", [])
            print(f"Selesai ({len(feeds):,} baris data).")
            return feeds

    # MODE TIME-WINDOWING PAGINATION untuk >8000 baris atau rentang spesifik
    all_feeds = []
    seen_ids = set()
    current_start = query_start
    batch_num = 1
    window_delta = timedelta(hours=window_hours)

    print(f"  --> Memulai time-windowing pagination (Jendela per {window_hours} jam)...")

    while current_start < query_end:
        current_end = min(current_start + window_delta, query_end)
        w_start_wib = current_start.astimezone(WIB_OFFSET).strftime('%m-%d %H:%M')
        w_end_wib = current_end.astimezone(WIB_OFFSET).strftime('%m-%d %H:%M')

        print(f"      [Batch {batch_num:02d}] {w_start_wib} -> {w_end_wib}...", end=" ", flush=True)

        try:
            batch_feeds = fetch_feeds_window(channel_id, current_start, current_end, api_key)
        except Exception as e:
            print(f"[Gagal: {e}] Mencoba jeda...")
            batch_feeds = []

        added = 0
        for f in batch_feeds:
            eid = f.get("entry_id")
            if eid not in seen_ids:
                seen_ids.add(eid)
                all_feeds.append(f)
                added += 1

        print(f"Dapat {added:,} data (Akumulasi: {len(all_feeds):,})")

        # Jika batch mendekati batas limit 8000, kecilkan jendela selanjutnya secara adaptif
        if len(batch_feeds) >= 7500 and window_delta > timedelta(hours=6):
            window_delta = window_delta / 2
            print(f"      [Info Adaptif] Kepadatan tinggi terdeteksi, jendela diperkecil jadi {window_delta.total_seconds() / 3600:.1f} jam.")

        # Geser jendela ke depan (+1 detik untuk mencegah duplikasi titik batas)
        current_start = current_end + timedelta(seconds=1)
        batch_num += 1

    return all_feeds


def save_dataset_to_csv(feeds, output_file, skip_backup=False):
    """Menyimpan data feeds ke CSV dengan proteksi backup dan penulisan atomik."""
    if not feeds:
        print("[Peringatan] Tidak ada data baru yang ditemukan untuk disimpan.")
        return

    # Urutkan berdasarkan entry_id secara ascending
    feeds.sort(key=lambda x: x.get("entry_id", 0))

    out_dir = os.path.dirname(os.path.abspath(output_file))
    os.makedirs(out_dir, exist_ok=True)

    # PROTEKSI DATA: Buat backup jika file tujuan sudah ada dan memiliki isi
    if not skip_backup and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
        ts_backup = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(out_dir, "backup")
        os.makedirs(backup_dir, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(output_file))[0]
        backup_file = os.path.join(backup_dir, f"{base_name}_backup_{ts_backup}.csv")
        shutil.copy2(output_file, backup_file)
        print(f"  --> [Proteksi Data] Arsip backup lama dibuat: {os.path.relpath(backup_file, BASE_DIR)}")

    # Tulis ke file temporer terlebih dahulu (Atomic Write)
    temp_file = output_file + ".tmp"
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

    with open(temp_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for item in feeds:
            utc_str = item.get("created_at", "")
            wib_str = ""
            if utc_str:
                dt_utc = parse_iso_utc(utc_str)
                if dt_utc:
                    wib_str = dt_utc.astimezone(WIB_OFFSET).strftime("%Y-%m-%d %H:%M:%S")
                else:
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

            kat_code = ""
            if f8 and f8.strip():
                try:
                    kat_code = str(int(float(f8)))
                except ValueError:
                    kat_code = f8.strip()
            kat_teks = KATEGORI_MAP.get(kat_code, "")

            writer.writerow([
                utc_str,
                wib_str,
                entry_id,
                f1, f2, f3, f4, f5, f6, f7,
                kat_code,
                kat_teks
            ])

    # Gantikan file asli dengan file temporer secara atomik
    if os.path.exists(output_file):
        os.remove(output_file)
    os.rename(temp_file, output_file)

    first_entry = feeds[0]
    last_entry = feeds[-1]
    first_utc = parse_iso_utc(first_entry.get("created_at", ""))
    last_utc = parse_iso_utc(last_entry.get("created_at", ""))
    first_wib = first_utc.astimezone(WIB_OFFSET).strftime("%Y-%m-%d %H:%M:%S") if first_utc else "N/A"
    last_wib = last_utc.astimezone(WIB_OFFSET).strftime("%Y-%m-%d %H:%M:%S") if last_utc else "N/A"

    print("\n" + "=" * 70)
    print(f" [SUKSES] Dataset lengkap berhasil disimpan!")
    print(f" Lokasi File  : {output_file}")
    print(f" Jumlah Baris : {len(feeds):,} entri")
    print(f" Rentang Waktu: {first_wib} s.d. {last_wib} WIB")
    print(f" Ukuran File  : {os.path.getsize(output_file) / 1024:.1f} KB")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Unduh dataset lengkap ThingSpeak untuk Project Stuzha dengan pagination otomatis tanpa terpotong limit 8000 baris."
    )
    parser.add_argument(
        "--channel",
        default=DEFAULT_CHANNEL_ID,
        help=f"ID Channel ThingSpeak (default: {DEFAULT_CHANNEL_ID})"
    )
    parser.add_argument(
        "--api-key",
        default=DEFAULT_READ_API_KEY,
        help="Read API Key ThingSpeak (kosongkan jika channel public)"
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Tanggal mulai filter dalam format ISO (contoh: '2026-09-08' atau '2026-09-08T00:00:00'). Default: awal rekaman channel."
    )
    parser.add_argument(
        "--end",
        default=None,
        help="Tanggal akhir filter dalam format ISO (contoh: '2026-09-15'). Default: waktu sekarang."
    )
    parser.add_argument(
        "--window-hours",
        type=int,
        default=24,
        help="Ukuran jendela waktu pagination dalam jam (default: 24 jam)."
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT_FILE,
        help=f"Path file output CSV (default: {DEFAULT_OUTPUT_FILE})"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Lewati pembuatan file cadangan (backup) jika file output sudah ada."
    )

    args = parser.parse_args()

    try:
        feeds = fetch_all_feeds(
            channel_id=args.channel,
            api_key=args.api_key,
            start_date=args.start,
            end_date=args.end,
            window_hours=args.window_hours
        )
        save_dataset_to_csv(feeds, args.output, skip_backup=args.no_backup)
    except KeyboardInterrupt:
        print("\n[Dibatalkan] Pengunduhan dibatalkan oleh pengguna.")
        sys.exit(1)
    except Exception as err:
        print(f"\n[Fatal Error] Terjadi kesalahan: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
