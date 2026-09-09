import csv
from datetime import datetime, timedelta, timezone
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("downloader", Path(__file__).parents[1] / "Program/download_thingspeak_dataset.py")
d = importlib.util.module_from_spec(spec)
spec.loader.exec_module(d)


def feed(i, time, status=""):
    return dict(entry_id=i, created_at=time.isoformat(), field3="123.45", status=status)


class DownloadTests(unittest.TestCase):
    def test_wib_end_includes_whole_day(self):
        self.assertEqual(d.parse_date_input("2026-09-08", True).isoformat(), "2026-09-08T16:59:59+00:00")
        self.assertEqual(d.parse_date_input("2026-09-08").isoformat(), "2026-09-07T17:00:00+00:00")

    def test_window_failure_propagates(self):
        start = datetime(2026, 9, 8, tzinfo=timezone.utc)
        with patch.object(d, "fetch_feeds_window", side_effect=[[feed(1, start)], RuntimeError("outage")]):
            with self.assertRaises(RuntimeError):
                d.fetch_all_feeds(1, start_date=start.isoformat(), end_date=(start + timedelta(days=2)).isoformat())

    def test_cap_retries_current_window_and_deduplicates_boundary(self):
        start = datetime(2026, 9, 8, tzinfo=timezone.utc)
        all_data = [feed(i + 1, start + timedelta(seconds=i)) for i in range(5)]
        calls = []
        def fetch(channel, a, b, key):
            calls.append((a, b))
            return [f for f in all_data if a <= d.parse_iso_utc(f["created_at"]) <= b][:3]
        with patch.object(d, "API_CAP", 3), patch.object(d, "fetch_feeds_window", side_effect=fetch):
            result = d.fetch_all_feeds(1, start_date=start.isoformat(), end_date=(start + timedelta(seconds=4)).isoformat())
        self.assertEqual([f["entry_id"] for f in result], [1, 2, 3, 4, 5])
        self.assertGreater(len(calls), 1)

    def test_failed_replace_preserves_original_and_cleans_tmp(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "data.csv"
            output.write_text("original\n")
            f = feed(1, datetime.now(timezone.utc))
            with patch.object(d.os, "replace", side_effect=OSError("busy")):
                with self.assertRaises(OSError):
                    d.save_dataset_to_csv([f], output)
            self.assertEqual(output.read_text(), "original\n")
            self.assertFalse(list(Path(directory).glob("*.tmp")))
            self.assertEqual(len(list((Path(directory) / "backup").glob("*.csv"))), 1)

    def test_mixed_schema_preserves_raw_status_and_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "data.csv"
            stamp = datetime.now(timezone.utc)
            d.save_dataset_to_csv([feed(1, stamp, "old category"), feed(2, stamp, "STZ3|v=3.0.0|b=abc"), feed(3, stamp, "STZ31|v=3.1.0|f=2304|s=20"), feed(4, stamp, "STZ4|v=4.0.0|f=39168|s=20")], output)
            with output.open(newline="") as f:
                rows = list(csv.DictReader(f))
            self.assertEqual(rows[0]["Schema"], "legacy_or_unknown")
            self.assertEqual(rows[1]["Schema"], "stuzha_v3")
            self.assertEqual(rows[1]["Status_Raw"], "STZ3|v=3.0.0|b=abc")
            self.assertEqual(rows[1]["field3"], "123.45")
            self.assertEqual(rows[2]["Schema"], "stuzha_v31")
            self.assertEqual(rows[2]["Status_Raw"], "STZ31|v=3.1.0|f=2304|s=20")
            self.assertEqual(rows[3]["Schema"], "stuzha_v4")

    def test_bad_ranges_and_empty_results_do_not_overwrite(self):
        with self.assertRaises(ValueError):
            d.fetch_all_feeds(1, start_date="2026-09-09", end_date="2026-09-08")
        with self.assertRaises(ValueError):
            d.fetch_all_feeds(1, window_hours=0)
        with self.assertRaises(ValueError):
            d.save_dataset_to_csv([], "never-written.csv")


if __name__ == "__main__":
    unittest.main()
