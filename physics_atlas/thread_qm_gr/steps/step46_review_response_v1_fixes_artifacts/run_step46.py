#!/usr/bin/env python3
"""Validate Step 46 review-response precision/scoping fixes."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from pathlib import Path


STEP_DIR = Path(__file__).resolve().parent
THREAD_ROOT = STEP_DIR.parents[1]

STEP41 = THREAD_ROOT / "steps" / "step41_tensor_network_rt_bound_artifacts"
STEP42 = THREAD_ROOT / "steps" / "step42_faithful_holographic_rt_enrichment_artifacts"
STEP44 = THREAD_ROOT / "steps" / "step44_holographic_mmi_entropy_cone_artifacts"
STEP45 = THREAD_ROOT / "steps" / "step45_discrete_einstein_consistency_artifacts"

NEW_VERDICT = "DISCRETE_RT_CONSISTENCY_CONSTRAINT_DERIVED"
OLD_VERDICT = "DISCRETE_EINSTEIN_CONSISTENCY_DERIVED"

FIXED_CUT_CAVEAT = "built from the unperturbed min-cut edge incidence"
FINITE_SAMPLE_CAVEAT = (
    "The contracted-state MMI check is finite-sample evidence in this carrier"
)
STEP41_R5 = (
    "The graph and tensor class here are CHOSEN as an RT recognition carrier"
)
STEP42_R5 = (
    "The graph and tensor class here are CHOSEN as an RT/random-tensor recognition carrier"
)


def die(message: str) -> None:
    raise SystemExit(f"run_step46.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        die(f"missing file {path}")
    return path.read_text()


def load_json(path: Path) -> dict:
    return json.loads(read(path))


def assert_close(name: str, observed: float, expected: float, tol: float = 1e-12) -> None:
    if not math.isclose(float(observed), float(expected), rel_tol=0.0, abs_tol=tol):
        die(f"{name} changed: observed {observed!r}, expected {expected!r}")


def assert_contains(path: Path, needle: str) -> None:
    text = read(path)
    if needle not in text:
        die(f"{path} missing required text: {needle}")


def assert_absent_in_step45(needle: str) -> None:
    for path in STEP45.iterdir():
        if path.is_dir() or path.name == "__pycache__":
            continue
        if path.suffix not in {".py", ".json", ".md", ".tex", ".csv"}:
            continue
        if needle in path.read_text(errors="ignore"):
            die(f"old verdict string still present in Step45 artifact {path.name}")


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


def validate_artifacts_present() -> None:
    required = [
        "step46_results_summary.md",
        "step46_schema.json",
        "content_classification_step46.csv",
        "nonclaim_boundary_step46.md",
        "run_step46.py",
    ]
    for name in required:
        if not (STEP_DIR / name).exists():
            die(f"missing Step46 artifact {name}")


def validate_r1_r5() -> None:
    schema45 = load_json(STEP45 / "step45_schema.json")
    if schema45.get("verdict") != NEW_VERDICT:
        die("Step45 schema verdict was not relabeled")
    assert_absent_in_step45(OLD_VERDICT)

    for path in [
        STEP45 / "step45_results_summary.md",
        STEP45 / "step45_discrete_einstein_statement.tex",
        STEP45 / "nonclaim_boundary_step45.md",
    ]:
        assert_contains(path, FIXED_CUT_CAVEAT)

    for path in [
        STEP44 / "step44_results_summary.md",
        STEP44 / "nonclaim_boundary_step44.md",
    ]:
        assert_contains(path, FINITE_SAMPLE_CAVEAT)

    assert_contains(STEP44 / "run_step44.py", "--quick")
    assert_contains(STEP44 / "step44_results_summary.md", "run_step44.py --quick")

    assert_contains(STEP41 / "step41_results_summary.md", STEP41_R5)
    assert_contains(STEP42 / "step42_results_summary.md", STEP42_R5)


def validate_numbers() -> None:
    schema42 = load_json(STEP42 / "step42_schema.json")
    assert_close("Step42 D2 trend", schema42["saturation_trend_D2"], 0.729363692238)
    assert_close("Step42 D3 trend", schema42["saturation_trend_D3"], 0.903532922433)
    assert_close("Step42 D4 trend", schema42["saturation_trend_D4"], 0.940570240858)

    schema44 = load_json(STEP44 / "step44_schema.json")
    assert_close("Step44 GHZ I3", schema44["I3_GHZ_control"], 0.69314718056)

    schema45 = load_json(STEP45 / "step45_schema.json")
    if schema45["rank_M"] != 10:
        die(f"Step45 rank_M changed: {schema45['rank_M']!r}")
    if schema45["cokernel_dim"] != 28:
        die(f"Step45 cokernel_dim changed: {schema45['cokernel_dim']!r}")
    assert_close(
        "Step45 RT-preserving residual",
        schema45["rt_preserving_residual"],
        9.25136442279574e-17,
        tol=1e-25,
    )
    assert_close(
        "Step45 generic violation residual",
        schema45["generic_violation_residual"],
        0.04189319241105151,
    )


def validate_self_validators() -> None:
    run_validator(STEP41, "run_step41.py", "--self")
    run_validator(STEP42, "run_step42.py", "--self")
    run_validator(STEP44, "run_step44.py", "--self")
    run_validator(STEP45, "run_step45.py", "--self")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] != "--self":
        die("usage: run_step46.py --self")
    validate_artifacts_present()
    validate_r1_r5()
    validate_numbers()
    validate_self_validators()
    print("run_step46.py: PASS --self")


if __name__ == "__main__":
    main()
