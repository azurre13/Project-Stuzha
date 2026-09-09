"""PlatformIO pre-build: deterministic identity from source and existing model headers."""
from pathlib import Path
import hashlib
import json
Import("env")

root = Path(env.subst("$PROJECT_DIR"))
paths = sorted(list((root / "src").glob("*.cpp")) + [
    root / "include" / name for name in
    ("pin_config.h", "monitoring_core.h", "experimental_models.h", "telemetry_contract.h", "telemetry_v4.h", "ispu_calc.h", "ispu_control.h", "rolling_ispu.h", "model_pm.h", "model_co.h")
] + [root / "platformio.ini", root / "scripts" / "build_identity.py"])
hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
identity = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
models = hashlib.sha256((hashes["include/model_pm.h"] + hashes["include/model_co.h"]).encode()).hexdigest()
header = root / "include" / "build_info.h"
content = f'#pragma once\n#define STUZHA_VERSION "4.0.0"\n#define STUZHA_BUILD "{identity[:12]}"\n#define STUZHA_MODELS "{models[:8]}"\n'
if not header.exists() or header.read_text() != content:
    header.write_text(content)
out = root / ".pio" / "build_manifest.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"firmware_version": "4.0.0", "source_sha256": identity,
                           "model_pair_sha256": models, "files": hashes,
                           "sensor_calibration_validated": False,
                           "model_role": "experimental_ml_ispu_control",
                           "telemetry_schema": "STZ4",
                           "pm_physical_unit": "nominal_ug/m3_legacy_scale_assumption_unverified",
                           "co_nominal_target_unit": "mg/m3 (unvalidated MQ7 transfer)",
                           "deployment_choice": "historical_headers_preserved_no_benchmark_replacement"}, indent=2))
