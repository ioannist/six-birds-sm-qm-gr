"""Tampering controls for the new recomputation guards, in disposable copies."""
from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import csv
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]


def load_runner(relative, name):
    path = ROOT / relative
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ArtifactGuardTests(unittest.TestCase):
    def test_step69_rejects_changed_score_source(self):
        runner = load_runner(
            "physics_atlas/thread_cluster_a/steps/step69_mode_t_record_stability_baryon_no_monopole_falsifiable_prediction_artifacts/run_step69.py",
            "audit_step69_guard",
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "scores.csv"
            path.write_bytes(runner.STEP59_SCORES.read_bytes() + b"\n")
            with patch.object(runner, "STEP59_SCORES", path), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    runner.check_hashes()
            self.assertIn("Step59 frozen score carrier sha mismatch", str(raised.exception))

    def test_step61_rejects_forged_exemplar_content(self):
        runner = load_runner(
            "physics_atlas/thread_cluster_a/steps/step61_mode_t_single_factor_clean_separation_theorem_artifacts/run_step61.py",
            "audit_step61_guard",
        )
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / runner.ARTIFACT_DIR.name
            shutil.copytree(runner.ARTIFACT_DIR, copied)
            path = copied / "single_factor_substrate_exemplars_step61.csv"
            with path.open(newline="") as handle:
                rows = list(csv.DictReader(handle))
            # The old validator only read N and the two witness counts.
            field = next(key for key in rows[0] if key not in
                         {"N", "transition_leak_count", "delta_witness_count"})
            rows[0][field] = "forged_exemplar"
            with path.open("w", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=rows[0])
                writer.writeheader()
                writer.writerows(rows)
            with patch.object(runner, "ARTIFACT_DIR", copied), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    runner.validate_recomputed_artifacts()
            self.assertEqual(raised.exception.code, 1)

    def test_step28_rejects_forged_history_with_unchanged_summary(self):
        runner = load_runner(
            "physics_atlas/thread_qm_gr/steps/step28_nonstationary_relational_histories_artifacts/run_step28.py",
            "audit_step28_guard",
        )
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary)
            path = copied / "nonstationary_history_step28.json"
            payload = json.loads((runner.ARTIFACT_DIR / path.name).read_text())
            payload["states"][0]["psi_re"][0] += 0.1
            path.write_text(json.dumps(payload))
            with patch.object(runner, "ARTIFACT_DIR", copied), redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    runner.reconstructed_operators()
            self.assertEqual(raised.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
