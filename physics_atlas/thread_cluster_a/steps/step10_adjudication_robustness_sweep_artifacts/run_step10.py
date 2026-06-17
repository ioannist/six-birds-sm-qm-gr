#!/usr/bin/env python3
"""Validate Cluster A Step 10 artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import runpy
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP6_SOURCE = THREAD_DIR / "steps" / "step6_e043_horn_adjudication_artifacts" / "e043_horn_adjudication_step6.py"
STEPS_DIR = THREAD_DIR / "steps"
STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_selection_layer_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_p2_selection_constraint_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_e043_scale_selection_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_e009_uv_fiber_artifacts" / "run_step5.py",
    STEPS_DIR / "step6_e043_horn_adjudication_artifacts" / "run_step6.py",
    STEPS_DIR / "step7_consolidated_statement_artifacts" / "run_step7.py",
    STEPS_DIR / "step8_structural_token_blind_selection_artifacts" / "run_step8.py",
    STEPS_DIR / "step9_facet_factorization_test_artifacts" / "run_step9.py",
]
TOL = 1e-9

REQUIRED_FILES = [
    "adjudication_robustness_sweep_step10.py",
    "sweep_cells_step10.csv",
    "robustness_map_step10.csv",
    "flip_boundaries_step10.csv",
    "operating_point_margin_step10.csv",
    "adjudication_robustness_output_step10.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step10_statement.tex",
]

FORBIDDEN_PATTERNS = [
    r"derives the gauge group",
    r"derives the standard model",
    r"computes the number of generations",
    r"selects the vacuum",
    r"solves the hierarchy problem",
    r"predicts the fermion masses",
    r"computes the cosmological constant",
    r"disproves anthropic",
    r"rejects anthropic",
    r"frame-transfer certificate",
    r"derivation of the EW scale",
    r"\bpsi\b",
    r"co-sourcing",
    r"common-refinement",
    r"stress-energy",
    r"field-layer",
    r"amplitude\(geometry\)",
]


def fail(message: str) -> None:
    print(f"STEP10 VALIDATION FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_file(path: Path) -> None:
    if not path.exists():
        fail(f"missing required file: {path}")


def scan_forbidden_text() -> None:
    checked_suffixes = {".md", ".tex", ".json", ".csv", ".py"}
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step10.py" or path.suffix not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"forbidden phrase/pattern {pattern!r} found in {path.name}")


def bool_text(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    fail(f"expected boolean text, got {value!r}")


def validate_sweep_cells() -> tuple[int, int, int]:
    rows = read_csv(ARTIFACT_DIR / "sweep_cells_step10.csv")
    if len(rows) != 9520:
        fail(f"unexpected sweep cell count: {len(rows)}")

    hold = sum(1 for row in rows if row["cell_class"] == "VERDICT_HOLDS")
    flip = sum(1 for row in rows if row["cell_class"] == "FLIP")
    if hold <= 0:
        fail("can-fail control failed: no hold cells")
    if flip <= 0:
        fail("can-fail control failed: no flip cells")
    if hold + flip != len(rows):
        fail("sweep cells include unknown classifications")

    for row in rows:
        broad_final = int(row["broad_final_degeneracy"])
        sharp_final = int(row["sharp_final_degeneracy"])
        broad_collapses = bool_text(row["broad_collapses"])
        sharp_collapses = bool_text(row["sharp_collapses"])
        expected_hold = (not broad_collapses) and sharp_collapses
        if broad_collapses != (broad_final == 1):
            fail("broad collapse flag disagrees with final degeneracy")
        if sharp_collapses != (sharp_final == 1):
            fail("sharp collapse flag disagrees with final degeneracy")
        if expected_hold and row["cell_class"] != "VERDICT_HOLDS":
            fail("hold classification disagrees with collapse flags")
        if (not expected_hold) and row["cell_class"] != "FLIP":
            fail("flip classification disagrees with collapse flags")
    return len(rows), hold, flip


def validate_operating_point() -> None:
    rows = read_csv(ARTIFACT_DIR / "operating_point_margin_step10.csv")
    if len(rows) != 1:
        fail("operating point file must have exactly one row")
    row = rows[0]
    if row["operating_cell_class"] != "VERDICT_HOLDS":
        fail("Step 6 operating point is not classified VERDICT_HOLDS")
    if row["operating_threshold"] != "0.25":
        fail("Step 6 threshold changed")
    if row["operating_broad_final_sigma"] != "2.00":
        fail("Step 6 broad final sigma changed")
    if row["operating_sharp_final_sigma"] != "0.10":
        fail("Step 6 sharp final sigma changed")
    if row["operating_broad_sequence"] != "6->6->6->6->6->6":
        fail("Step 6 broad sequence changed")
    if row["operating_sharp_sequence"] != "3->2->2->1->1":
        fail("Step 6 sharp sequence changed")
    if float(row["nearest_flip_normalized_margin"]) <= 0.0:
        fail("nearest flip margin must be positive")


def validate_json_schema(total: int, hold: int, flip: int) -> None:
    output = json.loads((ARTIFACT_DIR / "adjudication_robustness_output_step10.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))

    for doc, name in [(output, "output"), (schema, "schema")]:
        sweep = doc.get("sweep", {})
        if sweep.get("total_cells") != total:
            fail(f"{name} total_cells mismatch")
        if sweep.get("hold_cells") != hold:
            fail(f"{name} hold_cells mismatch")
        if sweep.get("flip_cells") != flip:
            fail(f"{name} flip_cells mismatch")
        if not math.isclose(float(sweep.get("hold_fraction")), hold / total, rel_tol=0.0, abs_tol=TOL):
            fail(f"{name} hold_fraction mismatch")

    verdict = output.get("verdict", {})
    if verdict.get("contains_hold_cells") is not True or verdict.get("contains_flip_cells") is not True:
        fail("JSON verdict must record both hold and flip cells")
    if verdict.get("step6_operating_point_holds") is not True:
        fail("JSON verdict must record Step 6 operating point as holding")
    schema_verdict = schema.get("verdict", {})
    if schema_verdict.get("parameter_free") is not False:
        fail("schema must not mark the result parameter-free")
    if schema_verdict.get("physical_value_computed") is not False:
        fail("schema must not mark a physical value as computed")
    if schema_verdict.get("physical_anthropic_verdict") is not False:
        fail("schema must not mark a physical anthropic verdict")


def validate_flip_boundaries(flip: int) -> None:
    rows = read_csv(ARTIFACT_DIR / "flip_boundaries_step10.csv")
    counts = {row["flip_kind"]: int(row["cell_count"]) for row in rows}
    if sum(counts.values()) != flip:
        fail("flip boundary counts do not sum to total flips")
    if counts.get("sharp_noncollapse", 0) <= 0:
        fail("missing sharp_noncollapse flip boundary")
    if counts.get("broad_false_collapse", 0) <= 0:
        fail("missing broad_false_collapse flip boundary")


def validate_robustness_map() -> None:
    rows = read_csv(ARTIFACT_DIR / "robustness_map_step10.csv")
    if not rows:
        fail("robustness map is empty")
    for row in rows:
        total = int(row["total_cells"])
        hold = int(row["hold_cells"])
        if not (0 <= hold <= total):
            fail("bad robustness map hold count")
        frac = float(row["hold_fraction"])
        if not math.isclose(frac, hold / total, rel_tol=0.0, abs_tol=TOL):
            fail("bad robustness map hold fraction")


def validate_content_classification() -> None:
    allowed_grades = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if not rows:
        fail("content classification is empty")
    for row in rows:
        if row.get("grade") not in allowed_grades:
            fail(f"bad grade: {row.get('grade')}")
        source_field = row.get("source_artifacts", "")
        if "/home/" in source_field or source_field.startswith("/"):
            fail("content classification uses an absolute source path")
        for source in [part.strip() for part in source_field.split(";") if part.strip()]:
            if not (THREAD_DIR / source).exists():
                fail(f"missing content source: {source}")


def run_prior_validators() -> None:
    for runner in STEP_RUNNERS:
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
            cwd=STEPS_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(
                f"{runner.name} failed during Step 10 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def run_self() -> None:
    require_file(STEP6_SOURCE)
    for filename in REQUIRED_FILES:
        require_file(ARTIFACT_DIR / filename)

    runpy.run_path(str(ARTIFACT_DIR / "adjudication_robustness_sweep_step10.py"), run_name="__main__")

    scan_forbidden_text()
    total, hold, flip = validate_sweep_cells()
    validate_operating_point()
    validate_json_schema(total, hold, flip)
    validate_flip_boundaries(flip)
    validate_robustness_map()
    validate_content_classification()

    print("STEP10 VALIDATION PASSED")


def run_chain() -> None:
    run_prior_validators()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 10 artifacts.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self", action="store_true", help="validate only this step's own artifacts (default)")
    mode.add_argument("--chain", action="store_true", help="validate prior steps once, then this step")
    args = parser.parse_args(argv)
    if args.chain:
        run_chain()
    else:
        run_self()


if __name__ == "__main__":
    main()
