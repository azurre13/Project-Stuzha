"""Read-only inventory of public datasets. No calibration or verified-unit claim."""
import csv
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main():
    for relative, delimiter in [("mendeley/Indoor_Air_Pollution_Data.csv", ","), ("uci/AirQualityUCI.csv", ";")]:
        path = ROOT / "Program/data" / relative
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, delimiter=delimiter)
            header = next(reader)
            n = sum(any(cell.strip() for cell in row) for row in reader)
        print(f"{relative}: {n} nonempty rows; columns={header}")
    print("Mendeley PM source unit unresolved: metadata says ug/m3, old script assumed mg/m3.")
    print("UCI CO(GT) is mg/m3; PT08.S1 response is not MQ-7 ADC.")
    print("Neither dataset independently validates the assembled Stuzha sensors.")

if __name__ == "__main__":
    main()
