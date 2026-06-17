#!/usr/bin/env python3
"""Validate Cluster A Step 11 artifacts."""

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
STEP8_SOURCE = THREAD_DIR / "steps" / "step8_structural_token_blind_selection_artifacts" / "structural_survivors_step8.csv"
BUILD_SCRIPT = ARTIFACT_DIR / "refinement_order_battery_step11.py"
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
    STEPS_DIR / "step10_adjudication_robustness_sweep_artifacts" / "run_step10.py",
]
TOL = 1e-9

REQUIRED_FILES = [
    "refinement_order_battery_step11.py",
    "order_results_step11.csv",
    "random_order_distribution_step11.csv",
    "adversarial_orders_step11.csv",
    "separation_step11.csv",
    "refinement_order_battery_output_step11.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step11_statement.tex",
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
    r"derivation of any SM value",
    r"\bpsi\b",
    r"co-sourcing",
    r"common-refinement",
    r"stress-energy",
    r"field-layer",
    r"amplitude\(geometry\)",
]

TOKEN_BLIND_FORBIDDEN = [
    r"G_SM",
    r"R_SM_CHIRAL",
    r"Y_SM_TOY",
    r"EW_LOW_TOY",
    r"UV_SM_TOY",
    r"VAC_SM_TOY",
    r"n_gen\s*==\s*3",
    r"n_gen==3",
    r"is_realized_point",
    r"REALIZED",
    r"realized_world",
    r"world_id\s*==",
]


def fail(message: str) -> None:
    print(f"STEP11 VALIDATION FAILED: {message}", file=sys.stderr)
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
        if path.name == "run_step11.py" or path.suffix not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"forbidden phrase/pattern {pattern!r} found in {path.name}")


def validate_token_blind_build_script() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for pattern in TOKEN_BLIND_FORBIDDEN:
        if re.search(pattern, text):
            fail(f"token-blindness guard failed on build script pattern {pattern!r}")


def validate_order_results() -> tuple[list[dict[str, str]], int, int]:
    rows = read_csv(ARTIFACT_DIR / "order_results_step11.csv")
    if len(rows) != 204:
        fail(f"expected 204 order rows, found {len(rows)}")
    random_rows = [row for row in rows if row["order_type"] == "random"]
    adversarial_rows = [row for row in rows if row["order_type"] == "adversarial"]
    if len(random_rows) != 200:
        fail(f"expected 200 random orders, found {len(random_rows)}")
    expected_adversarial = {"adversarial_delay_genuine", "adversarial_force_landscape"}
    actual_adversarial = {row["order_id"] for row in adversarial_rows}
    if expected_adversarial != actual_adversarial:
        fail(f"adversarial orders missing or renamed: {actual_adversarial}")
    if not any(int(row["genuine_final_degeneracy"]) == 1 for row in rows):
        fail("can-fail guard failed: genuine case never collapses")
    if all(int(row["landscape_final_degeneracy"]) == 1 for row in rows):
        fail("can-fail guard failed: landscape collapses under all orders")
    if any(int(row["landscape_final_degeneracy"]) < 1 for row in rows):
        fail("bad landscape degeneracy")
    if any(int(row["genuine_final_degeneracy"]) < 1 for row in rows):
        fail("bad genuine degeneracy")
    return rows, len(random_rows), len(adversarial_rows)


def validate_distributions() -> None:
    rows = {row["case"]: row for row in read_csv(ARTIFACT_DIR / "random_order_distribution_step11.csv")}
    genuine = rows.get("genuine_selection")
    landscape = rows.get("landscape_measure")
    if genuine is None or landscape is None:
        fail("missing distribution row")
    if int(genuine["random_order_count"]) != 200 or int(landscape["random_order_count"]) != 200:
        fail("random order count mismatch in distribution")
    if not math.isclose(float(genuine["collapse_fraction"]), 1.0, rel_tol=0.0, abs_tol=TOL):
        fail("genuine random collapse fraction should be 1.0 for emitted artifact")
    if not math.isclose(float(landscape["noncollapse_fraction"]), 1.0, rel_tol=0.0, abs_tol=TOL):
        fail("landscape random noncollapse fraction should be 1.0 for emitted artifact")
    if int(landscape["min_final_degeneracy"]) <= 1:
        fail("landscape random min final degeneracy should stay greater than 1")


def validate_adversarial_and_separation() -> None:
    adversarial = {row["order_id"]: row for row in read_csv(ARTIFACT_DIR / "adversarial_orders_step11.csv")}
    delay = adversarial["adversarial_delay_genuine"]
    force = adversarial["adversarial_force_landscape"]
    if int(delay["genuine_final_degeneracy"]) != 1 or int(delay["landscape_final_degeneracy"]) != 27:
        fail("adversarial_delay_genuine outcome mismatch")
    if int(force["genuine_final_degeneracy"]) != 1 or int(force["landscape_final_degeneracy"]) != 6:
        fail("adversarial_force_landscape outcome mismatch")

    rows = read_csv(ARTIFACT_DIR / "separation_step11.csv")
    if len(rows) != 1:
        fail("separation_step11.csv should have one row")
    sep = rows[0]
    if int(sep["separation_margin"]) != 5:
        fail("separation margin mismatch")
    if int(sep["flipping_order_count"]) != 0:
        fail("flipping order count mismatch")
    if sep["verdict"] != "order_invariant_separation":
        fail("separation verdict mismatch")


def validate_json_schema() -> None:
    output = json.loads((ARTIFACT_DIR / "refinement_order_battery_output_step11.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output.get("verdict", {})
    if verdict.get("type") != "refinement_order_battery_constructed":
        fail("output verdict type mismatch")
    if verdict.get("adversarial_order_count") != 2:
        fail("output must record two adversarial orders")
    if not math.isclose(float(verdict.get("genuine_random_collapse_fraction")), 1.0, rel_tol=0.0, abs_tol=TOL):
        fail("output genuine collapse fraction mismatch")
    if not math.isclose(float(verdict.get("landscape_random_noncollapse_fraction")), 1.0, rel_tol=0.0, abs_tol=TOL):
        fail("output landscape noncollapse fraction mismatch")
    if verdict.get("separation_margin") != 5:
        fail("output separation margin mismatch")
    schema_verdict = schema.get("verdict", {})
    if schema_verdict.get("parameter_free") is not False:
        fail("schema must not mark result parameter-free")
    if schema_verdict.get("physical_values_inferred") is not False:
        fail("schema must not mark physical values as inferred")
    if schema_verdict.get("physical_anthropic_verdict") is not False:
        fail("schema must not mark a physical anthropic verdict")


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
            fail("content classification uses an absolute path")
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
                f"{runner.name} failed during Step 11 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def run_self() -> None:
    require_file(STEP8_SOURCE)
    for filename in REQUIRED_FILES:
        require_file(ARTIFACT_DIR / filename)

    validate_token_blind_build_script()
    runpy.run_path(str(BUILD_SCRIPT), run_name="__main__")

    scan_forbidden_text()
    validate_order_results()
    validate_distributions()
    validate_adversarial_and_separation()
    validate_json_schema()
    validate_content_classification()

    print("STEP11 VALIDATION PASSED")


def run_chain() -> None:
    run_prior_validators()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 11 artifacts.")
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
