import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).parents[1] / "Program"))
from analyze_session import analyze, status_values, preflight
from download_thingspeak_dataset import HEADERS


def row(eid, second, slot, seq):
    status = f"STZ3|v=3.0.0|h=abc|m=def|b=123|u={seq*1000}|r=1|l=1|z=0|a=500,10|n=100|j=0|x=510|p=1|c=2|i=40|e={slot},0,1|q={slot}|k=150000"
    stamp = datetime(2026, 9, 8, 12, tzinfo=timezone.utc) + timedelta(seconds=second)
    return dict(Timestamp_UTC=stamp.isoformat(), Entry_ID=eid, Schema="stuzha_v3",
                field1="25", field2="50", field3="500", field4="1400", field5=seq,
                field6="12.941", field7="1600", field8="256", Status_Raw=status)


class AnalysisTests(unittest.TestCase):
    def test_v4_acceptance_and_invalid_category(self):
        values=[]
        for i in range(46):
            v=row(i+1,i*20,i+1,(i+1)*20)
            v.update(field3="31.4",field4="1.398",field5="70",field8="2")
            v["Status_Raw"]=f"STZ4|v=4.0.0|h=abc|m=def|b=123|u={(i+1)*20000}|r=1|l=2|f=39168|s={(i+1)*20}|n=100|j=0|i=40|e={i+1},0,0|q={i+1}|k=150000|a=1000,1400|d=nan,nan,nan,1|c=1"
            values.append(v)
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"v4.csv"
            def write():
                with path.open("w",newline="") as stream:
                    writer=csv.DictWriter(stream,fieldnames=HEADERS);writer.writeheader();writer.writerows(values)
            write(); report=analyze(path)
            self.assertEqual(report["schema_counts"],{"stuzha_v4":46})
            self.assertTrue(preflight(report)["passed"],report)
            values[10]["field8"]="5";write()
            self.assertTrue(analyze(path)["malformed"])
            values[10]["field8"]="0";values[10]["field5"]=""
            values[10]["Status_Raw"]=values[10]["Status_Raw"].replace("f=39168","f=39296")
            write();report=analyze(path)
            self.assertFalse(report["malformed"])
            self.assertFalse(preflight(report)["passed"])

    def test_v31_and_v3_are_decoded_separately(self):
        old = row(1, 0, 1, 20)
        new = row(2, 20, 2, 40)
        new.update(field3="12.5", field4="0.8", field5="500", field8="1400")
        new["Status_Raw"] = new["Status_Raw"].replace("STZ3|v=3.0.0", "STZ31|v=3.1.0").replace("|p=1|c=2", "|f=2304|s=40")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.csv"
            def write(values):
                with path.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=HEADERS); writer.writeheader(); writer.writerows(values)
            write([old, new])
            report = analyze(path)
            self.assertEqual(report["schema_counts"], {"stuzha_v3": 1, "stuzha_v31": 1})
            self.assertFalse(report["malformed"])
            self.assertEqual(len(report["boots"]), 2)
            self.assertEqual(report["boots"][1]["last"]["seq"], 40)
            self.assertEqual(report["boots"][1]["last"]["flag"], 2304)
            new["field8"] = "5000"
            write([new]); self.assertTrue(analyze(path)["malformed"])

    def test_unknown_firmware_cannot_silently_use_known_schema(self):
        with self.assertRaises(ValueError):
            status_values(row(1, 0, 1, 20)["Status_Raw"].replace("v=3.0.0", "v=3.9.0"))

    def test_observed_gap_is_not_sensor_accuracy_or_packet_loss(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic_fixture.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=HEADERS); writer.writeheader()
                writer.writerows([row(1, 0, 1, 20), row(2, 40, 3, 60)])
            report = analyze(path)
        self.assertEqual(report["rows"], 2)
        self.assertEqual(report["gaps_over_30s"][0]["seconds"], 40)
        self.assertEqual(report["boots"][0]["missing_observed_slots"], 1)
        self.assertAlmostEqual(report["boots"][0]["observed_cloud_slot_coverage_percent"], 200/3)
        self.assertEqual(report["flag_counts"]["mq7_heater_unverified"], 2)
        self.assertEqual(report["boots"][0]["inference_us"]["median"], 40)

    def test_truncated_status_cannot_pass_as_v3(self):
        with self.assertRaises(ValueError):
            status_values("STZ3|v=3.0.0|b=123")

    def test_preflight_checks_middle_timing_fault_not_just_last_record(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic_15min.csv"
            rows = [row(i+1, i*20, i+1, (i+1)*20) for i in range(46)]
            def write():
                with path.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=HEADERS); writer.writeheader(); writer.writerows(rows)
            write()
            self.assertTrue(preflight(analyze(path))["passed"])
            rows[10]["Status_Raw"] = rows[10]["Status_Raw"].replace("j=0", "j=11")
            rows[10]["field8"] = "272"
            write()
            result = preflight(analyze(path))
            self.assertFalse(result["passed"])
            self.assertTrue(any("10%" in message for message in result["problems"]))

    def test_legacy_rows_cannot_earn_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "legacy_fixture.csv"
            with path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=HEADERS); writer.writeheader()
                value = row(1, 0, 1, 20); value["Status_Raw"] = "old category"
                writer.writerow(value)
            self.assertFalse(preflight(analyze(path))["passed"])


if __name__ == "__main__":
    unittest.main()
