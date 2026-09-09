"""Download raw ThingSpeak feeds without silently accepting partial requests.

UTC queries, overlapping windows, recursive splitting at the API cap.
Preserves field1..8 and status verbatim, including mixed firmware schemas.
No physical concentration is inferred. Python standard library only.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

DEFAULT_CHANNEL_ID = "3480764"
BASE_DIR = Path(__file__).resolve().parent
WIB_OFFSET = timezone(timedelta(hours=7))
UTC = timezone.utc
API_CAP = 8000
HEADERS = ["Timestamp_UTC", "Timestamp_WIB", "Entry_ID", "Schema"] + [
    f"field{i}" for i in range(1, 9)
] + ["Status_Raw"]


def parse_iso_utc(value):
    if not value:
        raise ValueError("Timestamp feed kosong")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("Timestamp feed harus memiliki timezone")
    return dt.astimezone(UTC)


def parse_date_input(value, is_end=False):
    if not value:
        return None
    value = value.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        value += "T23:59:59" if is_end else "T00:00:00"
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=WIB_OFFSET)
    return dt.astimezone(UTC)


def request_json(channel_id, params, api_key="", retries=3):
    if api_key:
        params = {**params, "api_key": api_key}
    url = (f"https://api.thingspeak.com/channels/{int(channel_id)}/feeds.json?"
           + urllib.parse.urlencode(params))
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Stuzha-research/3"})
            with urllib.request.urlopen(req, timeout=30) as response:
                data = json.load(response)
            if not isinstance(data, dict) or not isinstance(data.get("feeds"), list):
                raise ValueError("Respons bukan feed JSON yang valid")
            return data
        except (OSError, ValueError) as exc:
            if attempt + 1 == retries:
                # Never print URLs containing private API keys.
                raise RuntimeError(f"Permintaan gagal setelah {retries} percobaan ({type(exc).__name__})") from None
            time.sleep(2 ** attempt)


def get_channel_info(channel_id, api_key=""):
    return request_json(channel_id, {"results": 1}, api_key)["channel"]


def fetch_feeds_window(channel_id, start_dt, end_dt, api_key=""):
    return request_json(channel_id, {
        "start": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "results": API_CAP, "status": "true", "timezone": "UTC",
    }, api_key)["feeds"]


def complete_window(channel_id, start, end, api_key):
    batch = fetch_feeds_window(channel_id, start, end, api_key)
    if len(batch) >= API_CAP:
        seconds = int((end - start).total_seconds())
        if seconds <= 1:
            raise RuntimeError("Batas API tercapai pada window minimum; hasil tidak disimpan")
        middle = start + timedelta(seconds=seconds // 2)
        # Re-fetch BOTH halves of this window; overlap is intentional.
        return (complete_window(channel_id, start, middle, api_key)
                + complete_window(channel_id, middle, end, api_key))
    for feed in batch:
        if not isinstance(feed, dict) or not isinstance(feed.get("entry_id"), int):
            raise ValueError("Feed tanpa entry_id integer")
        stamp = parse_iso_utc(feed.get("created_at"))
        if stamp < start or stamp > end:
            raise ValueError("API mengembalikan feed di luar window; hasil tidak disimpan")
    return batch


def fetch_all_feeds(channel_id, api_key="", start_date=None, end_date=None, window_hours=24):
    if not window_hours > 0 or not window_hours < 24 * 366:
        raise ValueError("window-hours harus positif dan kurang dari satu tahun")
    end = parse_date_input(end_date, True) or datetime.now(UTC)
    end = end.replace(microsecond=0)
    if start_date:
        start = parse_date_input(start_date)
    else:
        metadata = get_channel_info(channel_id, api_key)
        start = parse_iso_utc(metadata.get("created_at"))
    start = start.replace(microsecond=0)
    if start > end:
        raise ValueError("Waktu mulai melewati waktu akhir")
    if timedelta(hours=window_hours).total_seconds() < 1:
        raise ValueError("Window minimum satu detik")
    feeds = {}
    cursor = start
    while True:
        boundary = min(cursor + timedelta(seconds=int(window_hours * 3600)), end)
        batch = complete_window(channel_id, cursor, boundary, api_key)
        for feed in batch:
            eid = feed["entry_id"]
            if eid in feeds and feeds[eid] != feed:
                raise ValueError(f"Feed berubah selama unduh: entry_id {eid}")
            feeds[eid] = feed
        print(f"Window {cursor.isoformat()} .. {boundary.isoformat()}: {len(batch)}; unik {len(feeds)}")
        if boundary == end:
            break
        cursor = boundary
    return sorted(feeds.values(), key=lambda item: item["entry_id"])


def save_dataset_to_csv(feeds, output_file, skip_backup=False):
    if not feeds:
        raise ValueError("Tidak ada feed; file lama tidak diubah")
    output = Path(output_file).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="",
                                         dir=output.parent, suffix=".tmp", delete=False) as stream:
            tmp = Path(stream.name)
            writer = csv.DictWriter(stream, fieldnames=HEADERS)
            writer.writeheader()
            for feed in sorted(feeds, key=lambda item: item["entry_id"]):
                stamp = parse_iso_utc(feed.get("created_at"))
                status = feed.get("status") or ""
                row = {f"field{i}": feed.get(f"field{i}") for i in range(1, 9)}
                row.update(Timestamp_UTC=feed["created_at"],
                           Timestamp_WIB=stamp.astimezone(WIB_OFFSET).isoformat(),
                           Entry_ID=feed["entry_id"],
                           Schema="stuzha_v4" if status.startswith("STZ4|") else "stuzha_v31" if status.startswith("STZ31|") else ("stuzha_v3" if status.startswith("STZ3|") else "legacy_or_unknown"),
                           Status_Raw=status)
                writer.writerow(row)
            stream.flush()
            os.fsync(stream.fileno())
        if output.exists() and not skip_backup:
            backup = output.parent / "backup"
            backup.mkdir(exist_ok=True)
            name = f"{output.stem}_backup_{datetime.now(UTC):%Y%m%d_%H%M%S_%f}{output.suffix}"
            shutil.copy2(output, backup / name)
        os.replace(tmp, output)
        print(f"Disimpan: {output} ({len(feeds)} feed). Unduhan berhasil bukan jaminan semua sampel perangkat terkirim.")
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel", default=DEFAULT_CHANNEL_ID)
    parser.add_argument("--api-key", default=os.getenv("THINGSPEAK_READ_API_KEY", ""))
    parser.add_argument("--start", help="Tanggal/ISO; tanpa timezone = WIB")
    parser.add_argument("--end", help="Tanggal saja mencakup akhir hari WIB")
    parser.add_argument("--window-hours", type=float, default=24)
    parser.add_argument("--output", help="Default: snapshot baru di Program/data/downloads")
    parser.add_argument("--no-backup", action="store_true", help="Hanya untuk output eksplisit yang boleh diganti")
    args = parser.parse_args()
    output = args.output or BASE_DIR / "data" / "downloads" / f"thingspeak_{args.channel}_{datetime.now(UTC):%Y%m%d_%H%M%S_%f}.csv"
    try:
        feeds = fetch_all_feeds(args.channel, args.api_key, args.start, args.end, args.window_hours)
        save_dataset_to_csv(feeds, output, args.no_backup)
    except (ValueError, RuntimeError, OSError, KeyboardInterrupt) as exc:
        parser.exit(1, f"Unduh tidak selesai ({type(exc).__name__}): {exc}\n")


if __name__ == "__main__":
    main()
