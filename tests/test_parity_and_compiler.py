"""Unit tests for ML C++ parity verification, compiler fallbacks, and explicit outlier traces."""
import shutil
import sys
import unittest
from pathlib import Path
import numpy as np

# Ensure project root is in sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml_training.pipeline import (
    check_cpp_probe_environment,
    run_cpp_header_probe,
    verify_cpp_parity,
    LEGACY_PM_OUTLIER_TRACES,
)


class TestParityAndCompilerFallbacks(unittest.TestCase):
    def test_check_cpp_probe_environment_missing_header(self):
        """Returns ('header_missing') if header path does not exist."""
        dummy_header = Path("nonexistent/dummy_header.h")
        is_ready, status = check_cpp_probe_environment(compiler="g++", header_path=dummy_header)
        self.assertFalse(is_ready)
        self.assertEqual(status, "header_missing")

    def test_check_cpp_probe_environment_missing_compiler(self):
        """Returns ('compiler_unavailable') if g++ is missing or invalid."""
        existing_header = ROOT / "Program/Kode/include/model_pm.h"
        self.assertTrue(existing_header.exists())
        is_ready, status = check_cpp_probe_environment(compiler="nonexistent_compiler_xyz_123", header_path=existing_header)
        self.assertFalse(is_ready)
        self.assertEqual(status, "compiler_unavailable")

    def test_check_cpp_probe_environment_ready(self):
        """Returns ('ready') if g++ and header exist."""
        existing_header = ROOT / "Program/Kode/include/model_pm.h"
        compiler = shutil.which("g++")
        if compiler:
            is_ready, status = check_cpp_probe_environment(compiler=compiler, header_path=existing_header)
            self.assertTrue(is_ready)
            self.assertEqual(status, "ready")

    def test_verify_cpp_parity_pointwise_passed(self):
        """Pointwise parity passes when 100% of samples are within tolerance."""
        y_py = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        y_cpp = np.array([1.00001, 2.0, 2.99999, 4.00002, 5.0], dtype=np.float32)
        res = verify_cpp_parity(y_py, y_cpp, tolerance=1e-4, aggregate_pct_threshold=99.9)
        self.assertEqual(res["status"], "passed_pointwise")
        self.assertTrue(res["pointwise_criteria_met"])
        self.assertTrue(res["aggregate_criteria_met"])
        self.assertEqual(res["outlier_count"], 0)
        self.assertEqual(len(res["outlier_indices"]), 0)
        self.assertEqual(res["percent_within_tolerance"], 100.0)

    def test_verify_cpp_parity_aggregate_with_exceptions(self):
        """Parity passes aggregate criteria (>99.9% within 1e-4, mean diff < 1e-4) while explicitly reporting outliers."""
        # 10,000 samples, 4 outliers exceeding 1e-4
        rng = np.random.default_rng(42)
        y_py = rng.uniform(10.0, 50.0, 10000).astype(np.float32)
        y_cpp = y_py.copy()
        # Add 4 boundary outliers
        y_cpp[100] += 0.324
        y_cpp[500] -= 0.110
        y_cpp[1200] -= 0.196
        y_cpp[8500] += 0.248
        
        res = verify_cpp_parity(y_py, y_cpp, tolerance=1e-4, aggregate_pct_threshold=99.9)
        self.assertEqual(res["status"], "passed_aggregate_with_exceptions")
        self.assertTrue(res["aggregate_criteria_met"])
        self.assertFalse(res["pointwise_criteria_met"])
        self.assertEqual(res["outlier_count"], 4)
        self.assertEqual(res["outlier_indices"], [100, 500, 1200, 8500])
        self.assertAlmostEqual(res["percent_within_tolerance"], 99.96, places=2)
        self.assertLess(res["mean_abs_difference"], 1e-4)

    def test_verify_cpp_parity_failed(self):
        """Parity fails when difference exceeds acceptable aggregate criteria."""
        y_py = np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32)
        y_cpp = np.array([1.1, 2.0, 3.5, 4.0, 5.2], dtype=np.float32)
        res = verify_cpp_parity(y_py, y_cpp, tolerance=1e-4, aggregate_pct_threshold=99.9)
        self.assertEqual(res["status"], "failed")
        self.assertFalse(res["aggregate_criteria_met"])
        self.assertFalse(res["pointwise_criteria_met"])
        self.assertGreater(res["mean_abs_difference"], 1e-4)

    def test_run_cpp_header_probe_execution(self):
        """Direct execution of run_cpp_header_probe on active header with sample input."""
        compiler = shutil.which("g++")
        if not compiler:
            self.skipTest("g++ not available")
        header_path = ROOT / "Program/Kode/include/model_pm.h"
        sample_input = np.array([
            [10.0, 25.0, 50.0],
            [20.0, 30.0, 60.0],
            [30.0, 33.4, 70.0]
        ], dtype=np.float32)
        status, preds = run_cpp_header_probe(header_path, sample_input, compiler=compiler)
        self.assertEqual(status, "success")
        self.assertIsNotNone(preds)
        self.assertEqual(len(preds), 3)
        self.assertTrue(np.all(preds > 0))

    def test_explicit_four_legacy_outliers_exact_trace(self):
        """Verify the 4 explicit pointwise tolerance violations traced per tree/node/threshold."""
        self.assertEqual(len(LEGACY_PM_OUTLIER_TRACES), 4)
        indices = [t["test_index"] for t in LEGACY_PM_OUTLIER_TRACES]
        self.assertEqual(indices, [8090, 9432, 13708, 29821])
        
        # Verify row 8090: Tree 17 Node 47 delta +0.324213
        t8090 = LEGACY_PM_OUTLIER_TRACES[0]
        self.assertEqual(t8090["tree_index"], 17)
        self.assertEqual(t8090["node_index"], 47)
        self.assertEqual(t8090["threshold_cpp_literal"], "33.400000f")
        self.assertAlmostEqual(t8090["delta_prediction_total_30_trees"], 0.324213, places=5)
        
        # Verify row 9432: Tree 29 Node 27 delta -0.110000
        t9432 = LEGACY_PM_OUTLIER_TRACES[1]
        self.assertEqual(t9432["tree_index"], 29)
        self.assertEqual(t9432["node_index"], 27)
        self.assertEqual(t9432["threshold_cpp_literal"], "31.530001f")
        self.assertAlmostEqual(t9432["delta_prediction_total_30_trees"], -0.110000, places=5)

        # Verify row 13708: Tree 4 Node 39 delta -0.196296
        t13708 = LEGACY_PM_OUTLIER_TRACES[2]
        self.assertEqual(t13708["tree_index"], 4)
        self.assertEqual(t13708["node_index"], 39)
        self.assertEqual(t13708["threshold_cpp_literal"], "31.540000f")
        self.assertAlmostEqual(t13708["delta_prediction_total_30_trees"], -0.196296, places=5)

        # Verify row 29821: Tree 26 Node 14 delta +0.248227
        t29821 = LEGACY_PM_OUTLIER_TRACES[3]
        self.assertEqual(t29821["tree_index"], 26)
        self.assertEqual(t29821["node_index"], 14)
        self.assertEqual(t29821["threshold_cpp_literal"], "26.360001f")
        self.assertAlmostEqual(t29821["delta_prediction_total_30_trees"], 0.248227, places=5)

    def test_linear_regression_float64_numerical_stability(self):
        """Ensure float64 LinearRegression preserves numerical conditioning on unscaled data."""
        from sklearn.linear_model import LinearRegression
        rng = np.random.default_rng(42)
        x0 = rng.uniform(0.01, 0.4, 1000)
        temp = rng.uniform(20, 35, 1000)
        rh = rng.uniform(40, 80, 1000)
        y = x0 * 0.9 + temp * 0.001 + rh * 0.0005
        X = np.column_stack([x0, temp, rh])

        lr_f64 = LinearRegression().fit(X.astype(np.float64), y.astype(np.float64))
        r2_f64 = lr_f64.score(X.astype(np.float64), y.astype(np.float64))
        self.assertGreater(r2_f64, 0.99)


if __name__ == "__main__":
    unittest.main()
