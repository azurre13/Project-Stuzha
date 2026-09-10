"""Read-only quality audit of raw downloader CSVs and historical Stuzha CSVs.

Reports observed cloud coverage, not packet-loss rate or sensor accuracy.
Unknown and malformed rows are counted; the source is never modified.
"""
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import statistics

FLAG_NAMES = {1: "dht_invalid", 2: "gp_adc_rail", 4: "mq7_adc_rail", 8: "mq135_adc_rail",
              16: "gp_timing_deviation", 32: "baseline_pending", 64: "wifi_offline_at_sample",
              128: "model_invalid_or_not_computed", 256: "mq7_heater_unverified", 512: "frame_incomplete",
              1024: "processing_stale", 2048: "model_transfer_unverified", 4096: "pm_scale_unverified",
              8192: "index_above_range", 16384: "gp_saturated", 32768: "average24_pending"}


def status_values(status):
    if not status.startswith(("STZ3|", "STZ31|", "STZ4|")):
        return None
    fields = {}
    for piece in status.split("|")[1:]:
        key, value = piece.split("=", 1)
        if key in fields:
            raise ValueError("Duplicate status key")
        fields[key] = value
    required = {"v", "h", "m", "b", "u", "r", "l", "z", "a", "n", "j", "x", "i", "e", "q", "k"}
    is_v4 = status.startswith("STZ4|")
    is_v31 = status.startswith("STZ31|")
    if is_v4:
        required = {"v","h","m","b","u","r","l","f","s","n","j","i","e","q","k","a","d","c"}
    else:
        required |= {"f", "s"} if is_v31 else {"p", "c"}
    if not required.issubset(fields):
        raise ValueError("Incomplete versioned status")
    if fields["v"] != ("4.0.0" if is_v4 else "3.1.0" if is_v31 else "3.0.0"):
        raise ValueError("Unknown version/schema combination")
    fields["_schema"] = "stuzha_v4" if is_v4 else "stuzha_v31" if is_v31 else "stuzha_v3"
    return fields


def finite(value):
    n = float(value)
    if not math.isfinite(n):
        raise ValueError("Expected a finite numeric field")
    return n


def integer_field(value):
    """ThingSpeak numeric fields may serialize integers as '2.000000'."""
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise ValueError("Expected an integer numeric field") from None
    if not number.is_finite() or number != number.to_integral_value():
        raise ValueError("Expected an integer numeric field")
    return int(number)


def analyze(path):
    path = Path(path)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    report = {"file": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "rows": len(rows), "scope": "observed cloud snapshots; no calibration or uninterrupted uptime claim",
              "malformed": [], "schema_counts": {}, "flag_counts": {}, "boots": [], "gaps_over_30s": []}
    schemas, flags, ids = Counter(), Counter(), Counter()
    points, boots = [], defaultdict(list)
    builds, levels = Counter(), Counter()
    for line, row in enumerate(rows, 2):
        try:
            stamp = datetime.fromisoformat(row["Timestamp_UTC"].replace("Z", "+00:00"))
            if stamp.tzinfo is None:
                raise ValueError("Timestamp has no timezone")
            stamp = stamp.astimezone(timezone.utc)
            eid = int(row["Entry_ID"])
            ids[eid] += 1
            points.append((stamp, eid))
            status = status_values(row.get("Status_Raw", ""))
            if status is None:
                schemas["legacy_or_unknown"] += 1
                continue
            schema = status["_schema"]
            schemas[schema] += 1
            v4 = schema == "stuzha_v4"
            v31 = schema == "stuzha_v31"
            flag = integer_field(status["f"] if v31 or v4 else row["field8"])
            seq = integer_field(status["s"] if v31 or v4 else row["field5"])
            if flag < 0 or seq < 1:
                raise ValueError("Negative flags or invalid sequence")
            if (v31 or v4) and not flag & 128:
                if finite(row["field3"]) < 0 or finite(row["field4"]) < 0:
                    raise ValueError("Negative model output")
            if v4:
                raw_adc = [finite(x) for x in status["a"].split(",")]
                if len(raw_adc)!=2 or any(x<0 or x>4095 for x in raw_adc):
                    raise ValueError("Invalid raw ADC status")
                category = integer_field(row["field8"])
                if not 0 <= category <= 5:
                    raise ValueError("Invalid index category")
                if flag & 128:
                    if category != 0 or row["field5"].strip():
                        raise ValueError("Invalid model cannot publish a final category/index")
                else:
                    index=finite(row["field5"])
                    if not 0<=index<=500:
                        raise ValueError("Index outside range")
                    rounded=math.floor(index+0.5)
                    expected=1 if rounded<=50 else 2 if rounded<=100 else 3 if rounded<=200 else 4 if rounded<=300 else 5
                    if category!=expected:
                        raise ValueError("Index/category mismatch")
                averages=status["d"].split(",")
                if len(averages)!=4 or not 0<=finite(averages[3])<=100.01:
                    raise ValueError("Invalid 24-hour metadata")
                if not flag & 32768:
                    for value in averages[:3]: finite(value)
                adc_fields=["field7"]
            else:
                adc_fields=["field5","field8","field7"] if v31 else ["field3","field4","field7"]
            for name in adc_fields:
                if not 0 <= finite(row[name]) <= 4095:
                    raise ValueError(f"ADC outside range: {name}")
            if not 0 <= finite(row["field6"]) <= 100:
                raise ValueError("PWM outside range")
            if not flag & 1:
                finite(row["field1"]); finite(row["field2"])
            level = int(status["l"])
            if not 1 <= level <= 5:
                raise ValueError("Invalid control level")
            for mask, name in FLAG_NAMES.items():
                if flag & mask:
                    flags[name] += 1
            builds[status["h"]] += 1
            levels[str(level)] += 1
            attempts, failures, unattempted = map(int, status["e"].split(","))
            boots[(schema, status["h"], status["b"])].append(dict(
                stamp=stamp.isoformat(), seq=seq, uptime_ms=int(status["u"]), slot=int(status["q"]),
                reset_reason=int(status["r"]), infer_us=int(status["i"]), heap=int(status["k"]),
                attempts=attempts, failures=failures, unattempted=unattempted, flag=flag,
                samples=int(status["n"]), timing_bad=int(status["j"])))
        except (ValueError, KeyError, TypeError) as exc:
            report["malformed"].append({"csv_line": line, "reason": str(exc)})
    points.sort()
    intervals = [(b[0] - a[0]).total_seconds() for a, b in zip(points, points[1:])]
    if points:
        report.update(first_utc=points[0][0].isoformat(), last_utc=points[-1][0].isoformat(),
                      observed_span_hours=(points[-1][0] - points[0][0]).total_seconds() / 3600)
    if intervals:
        report["interval_seconds"] = dict(min=min(intervals), median=statistics.median(intervals), max=max(intervals))
    for a, b in zip(points, points[1:]):
        seconds = (b[0] - a[0]).total_seconds()
        if seconds > 30:
            report["gaps_over_30s"].append(dict(after_entry=a[1], before_entry=b[1],
                                                  start_utc=a[0].isoformat(), end_utc=b[0].isoformat(), seconds=seconds))
    for (schema, build, boot), values in boots.items():
        values.sort(key=lambda v: v["stamp"])
        slots = [v["slot"] for v in values]
        slot_span = max(slots) - min(slots) + 1
        # A zero duration means inference was not timed/computed on that snapshot.
        latency = [v["infer_us"] for v in values if not v["flag"] & 128 and v["infer_us"] > 0]
        monotonic_errors = sum(b["uptime_ms"] <= a["uptime_ms"] or b["seq"] <= a["seq"] or b["slot"] <= a["slot"]
                               for a, b in zip(values, values[1:]))
        item = dict(schema=schema, build=build, boot=boot, rows=len(values), first=values[0], last=values[-1],
                    observed_cloud_slot_coverage_percent=100 * len(set(slots)) / slot_span,
                    missing_observed_slots=slot_span - len(set(slots)), nonmonotonic_records=monotonic_errors,
                    heap_min_bytes=min(v["heap"] for v in values), heap_last_bytes=values[-1]["heap"],
                    max_timing_bad_fraction=max(v["timing_bad"] / max(1, v["samples"]) for v in values))
        if latency:
            ordered = sorted(latency)
            item["inference_us"] = dict(n=len(latency), median=statistics.median(latency),
                                       p95=ordered[math.ceil(0.95 * len(ordered)) - 1], max=max(latency))
        report["boots"].append(item)
    report["schema_counts"], report["flag_counts"] = dict(schemas), dict(flags)
    report["build_counts"], report["level_counts"] = dict(builds), dict(levels)
    report["duplicate_entry_ids"] = {str(k): v for k, v in ids.items() if v > 1}
    report["notes"] = [
        "Coverage denominator is the slot range observed within one boot, not all planned seven-day slots.",
        "A boot first seen in cloud may have started earlier; offline resets may be entirely unobserved.",
        "Network counters in status describe state before the corresponding write result is known.",
        "Latency is sampled on received cloud snapshots; it is not the distribution of every inference.",
        "MQ7 heater-unverified flag is expected until hardware operation is established; it is not a failed Wi-Fi flag.",
        "v3.0/v3.1 initial baselines are not calibration; v4 has no per-boot concentration baseline.",
        "v4 field5 is an instantaneous model-based index, not a regulatory 24-hour reading. PM unit scale and MQ7 transfer remain unvalidated.",
        "v3.1 fields 3/4 are experimental model outputs, not validated room concentrations; flags/sequence are in status.",
    ]
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv")
    parser.add_argument("--output", help="New JSON file; refuses overwrite")
    parser.add_argument("--require-v3", action="store_true", help="Fail if no usable v3 boot records exist")
    parser.add_argument("--require-v31", action="store_true", help="Require only v3.1 records for the new deployment")
    parser.add_argument("--require-v4", action="store_true", help="Require only v4 deployment records")
    parser.add_argument("--preflight", action="store_true", help="Evaluate the documented 15-minute field acceptance gate")
    args = parser.parse_args()
    report = analyze(args.csv)
    if args.preflight:
        report["preflight"] = preflight(report)
    result = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    if args.output:
        with Path(args.output).open("x", encoding="utf-8") as stream:
            stream.write(result + "\n")
    print(result)
    if report["malformed"] or (args.require_v4 and (not report["boots"] or set(report["schema_counts"]) != {"stuzha_v4"})) or (args.require_v31 and (not report["boots"] or set(report["schema_counts"]) != {"stuzha_v31"})) or (args.require_v3 and not report["boots"]) or (args.preflight and not report["preflight"]["passed"]):
        parser.exit(1, "Audit memerlukan perhatian: periksa format, versi, dan hasil preflight pada laporan.\n")


def preflight(report):
    """A conservative engineering gate, not an accuracy or publication certificate."""
    problems = []
    if report["malformed"] or report["duplicate_entry_ids"]:
        problems.append("Malformed rows or duplicate cloud IDs")
    if report["schema_counts"].get("legacy_or_unknown", 0):
        problems.append("Use a v3-only acceptance interval; legacy rows are present")
    if len(report["boots"]) != 1:
        problems.append("Expected one observed firmware build/boot for this short test")
    if report.get("observed_span_hours", 0) < 0.25:
        problems.append("Need at least 15 minutes of cloud observations")
    for name in ("dht_invalid", "gp_adc_rail", "mq7_adc_rail", "mq135_adc_rail", "frame_incomplete", "processing_stale", "model_invalid_or_not_computed"):
        if report["flag_counts"].get(name, 0):
            problems.append(f"Investigate flagged records: {name}")
    for boot in report["boots"]:
        if boot["rows"] < 30 or boot["last"]["flag"] & 32:
            problems.append("Need 30 received records and a completed initial baseline")
        if boot["nonmonotonic_records"] or boot["missing_observed_slots"]:
            problems.append("Sequence/slot discontinuity in the short acceptance run")
        if "inference_us" not in boot:
            problems.append("No measured inference duration received")
        if boot["max_timing_bad_fraction"] > 0.1:
            problems.append("More than 10% GP timing deviations in at least one received block")
    return {"passed": not problems, "problems": problems,
            "scope": "short software/telemetry acceptance only; physical pulse timing, wiring and sensor accuracy remain separate"}


if __name__ == "__main__":
    main()
