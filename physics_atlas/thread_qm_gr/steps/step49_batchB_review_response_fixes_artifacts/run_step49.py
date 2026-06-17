#!/usr/bin/env python3
"""Validate Step 49 Batch B review-response fixes."""

from __future__ import annotations

import csv
import json
import math
import os
import subprocess
import sys
from pathlib import Path


STEP_DIR = Path(__file__).resolve().parent
THREAD_ROOT = STEP_DIR.parents[1]
STEP47 = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
STEP48 = THREAD_ROOT / "steps" / "step48_ladder_vs_fork_resolution_artifacts"
OLD_WEAK_RT_PREFIX = "emergent_" + "spacetime_ladder"


def die(message: str) -> None:
    raise SystemExit(f"run_step49.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        die(f"missing file {path}")
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(read(path))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def assert_close(name: str, observed: float, expected: float, tol: float = 1e-12) -> None:
    if not math.isclose(float(observed), float(expected), rel_tol=0.0, abs_tol=tol):
        die(f"{name} changed: observed {observed!r}, expected {expected!r}")


def assert_contains(path: Path, needle: str) -> None:
    if needle not in read(path):
        die(f"{path.name} missing required text: {needle}")


def assert_old_weak_rt_absent_from_step48() -> None:
    for path in STEP48.iterdir():
        if path.is_dir() or path.name == "__pycache__":
            continue
        if path.suffix not in {".py", ".json", ".md", ".tex", ".csv"}:
            continue
        if OLD_WEAK_RT_PREFIX in path.read_text(encoding="utf-8", errors="ignore"):
            die(f"old weak-RT predecessor string still present in Step48 artifact {path.name}")


def run_validator(step_dir: Path, script: str, mode: str) -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, script, mode],
        cwd=step_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        timeout=180,
    )
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        die(f"{step_dir.name}/{script} {mode} failed")


def validate_step47_reframe() -> None:
    schema = load_json(STEP47 / "step47_schema.json")
    if schema.get("landing_mode") != "LANDED_GROUND_CONDITIONAL":
        die("Step47 schema missing LANDED_GROUND_CONDITIONAL")
    if schema.get("premise_ground_landed") is not True:
        die("Step47 premise_ground_landed must be true")
    if schema.get("warrant_extended_via_step26") is not True:
        die("Step47 Step26 warrant extension missing")
    for path in [
        STEP47 / "step47_results_summary.md",
        STEP47 / "common_carrier_door_test_statement_step47.tex",
        STEP47 / "nonclaim_boundary_step47.md",
    ]:
        assert_contains(path, "LANDED * GROUND (conditional)")
    assert_contains(STEP47 / "step47_results_summary.md", "structural reading of the framework sources")
    assert_contains(STEP47 / "step47_results_summary.md", "Step26")
    assert_contains(STEP47 / "step47_results_summary.md", "matter-sourced geometry")
    assert_contains(STEP47 / "co_sourcing_warrant_step47.csv", "steps/step26_semiclassical_dynamics_artifacts/step26_schema.json")


def validate_step48_rename() -> None:
    schema = load_json(STEP48 / "step48_schema.json")
    if "weak_rt_ladder_defect" not in schema:
        die("Step48 schema missing weak_rt_ladder_defect")
    if "emergent_" + "spacetime_ladder_defect" in schema:
        die("Step48 schema still has old weak-RT predecessor field")
    assert_contains(STEP48 / "ladder_vs_fork_sim_step48.csv", "weak_RT_QM_accessible_shadow_ladder")
    assert_contains(STEP48 / "step48_results_summary.md", "WEAK-RT / QM-accessible-shadow ladder")
    assert_contains(STEP48 / "step48_results_summary.md", "strong bulk reconstruction")
    assert_contains(STEP48 / "ladder_vs_fork_statement_step48.tex", "WEAK-RT ladder only")
    assert_old_weak_rt_absent_from_step48()


def validate_numbers() -> None:
    controls = {row["control"]: row for row in load_csv(STEP47 / "common_carrier_controls_step47.csv")}
    assert_close(
        "Step47 complementary commutator",
        float(controls["complementary_noncommuting_pair"]["value"]),
        0.707106781187,
    )
    assert_close(
        "Step47 non-co-sourcing residual",
        float(controls["non_co_sourcing_independent_field"]["value"]),
        0.380602660378,
    )
    attempts = {row["attempt_id"]: row for row in load_csv(STEP48 / "ladder_vs_fork_sim_step48.csv")}
    if int(attempts["plain_ladder_GR_as_quotient_of_QM"]["pair_defect_count"]) != 8:
        die("Step48 direct ladder defect changed")
    if int(attempts["weak_RT_QM_accessible_shadow_ladder"]["pair_defect_count"]) != 8:
        die("Step48 weak-RT ladder defect changed")
    if int(attempts["nested_control_GR_nested_as_quotient_of_QM"]["pair_defect_count"]) != 0:
        die("Step48 nested-control defect changed")
    assert_close(
        "Step48 direct route mismatch",
        float(attempts["plain_ladder_GR_as_quotient_of_QM"]["route_mismatch_normalized"]),
        0.5,
    )
    schema48 = load_json(STEP48 / "step48_schema.json")
    if schema48["weak_rt_ladder_defect"] != 8.0:
        die("Step48 weak_rt_ladder_defect changed")


def validate_self_validators() -> None:
    run_validator(STEP47, "run_step47.py", "--self")
    run_validator(STEP48, "run_step48.py", "--self")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] != "--self":
        die("usage: run_step49.py --self")
    for name in [
        "step49_results_summary.md",
        "step49_schema.json",
        "content_classification_step49.csv",
        "nonclaim_boundary_step49.md",
        "run_step49.py",
    ]:
        if not (STEP_DIR / name).exists():
            die(f"missing Step49 artifact {name}")
    schema = load_json(STEP_DIR / "step49_schema.json")
    if schema.get("verdict") != "REVIEW_RESPONSE_FIXES_APPLIED":
        die("unexpected Step49 verdict")
    validate_step47_reframe()
    validate_step48_rename()
    validate_numbers()
    validate_self_validators()
    print("run_step49.py: PASS --self")


if __name__ == "__main__":
    main()
