#!/usr/bin/env python3
"""Validate Step 39 currency-constraint area-shadow-price artifacts."""

from __future__ import annotations

import csv
import json
import math
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
BUILD_SCRIPT = ARTIFACT_DIR / "currency_constraint_area_shadow_price_step39.py"
TOL = 1e-8

REQUIRED_FILES = [
    "currency_constraint_area_shadow_price_step39.py",
    "step39_results_summary.md",
    "step39_schema.json",
    "content_classification_step39.csv",
    "nonclaim_boundary_step39.md",
    "step39_area_shadow_price_statement.tex",
    "shadow_price_relation_sim_step39.csv",
    "can_fail_controls_step39.csv",
    "stage2_shadow_price_sweep_step39.csv",
    "dependency_trace_step39.csv",
    "ablation_step39.csv",
    "generated_vs_input_step39.csv",
    "anti_hardcode_step39.csv",
    "six_gate_audit_step39.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step39.py",
]

OVERCLAIM_PATTERNS = [
    r"derives\s+1/4G",
    r"derives\s+(?:a\s+)?(?:constant|mass)",
    r"proves\s+quantum\s+gravity",
    r"solves\s+quantum\s+gravity",
    r"closes\s+E018",
    r"unconditional\s+new[- ]physics",
]


def fail(message: str) -> None:
    print(f"run_step39.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def validate_presence() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required artifacts: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step39_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 39,
        "orientation": "ModeB_E018_currency_constraint_area_shadow_price",
        "final_verdict": "SHADOW_PRICE_RELATION_DERIVED",
        "can_fail_control_result": "collapsed",
        "rt_recognition_landed": True,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "other_law_landing_legs_attempted": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if abs(float(schema["computed_k_refinement_1"]) - float(schema["computed_k_refinement_2"])) > TOL:
        fail("computed k drifts between refinements")
    if float(schema["k_refinement_abs_drift"]) > TOL:
        fail("schema reports non-stable k")
    return schema


def validate_relation_rows() -> None:
    rows = read_csv("shadow_price_relation_sim_step39.csv")
    if len(rows) != 2:
        fail("expected exactly two refinement rows")
    k_values = []
    for row in rows:
        entropy = float(row["entanglement_entropy_S"])
        area = float(row["geometric_area_A"])
        k = float(row["shadow_price_k_dA_dS"])
        derived_area = float(row["derived_area_k_times_S"])
        k_values.append(k)
        if entropy <= 0 or area <= 0:
            fail(f"nonpositive entropy or area in {row['refinement_id']}")
        if abs(derived_area - area) > TOL:
            fail(f"area relation residual too large in {row['refinement_id']}")
        if float(row["relation_abs_residual"]) > TOL:
            fail(f"recorded residual too large in {row['refinement_id']}")
        if abs(float(row["maxcal_expected_entropy_budget"]) - entropy) > TOL:
            fail(f"MaxCal entropy budget mismatch in {row['refinement_id']}")
        if abs(float(row["maxcal_expected_area"]) - area) > TOL:
            fail(f"MaxCal expected area mismatch in {row['refinement_id']}")
        if float(row["maxcal_budget_residual"]) > TOL:
            fail(f"MaxCal budget residual too large in {row['refinement_id']}")
    if max(k_values) - min(k_values) > TOL:
        fail("k values are not refinement-stable")


def validate_controls() -> None:
    rows = read_csv("can_fail_controls_step39.csv")
    by_id = {row["control_id"]: row for row in rows}
    product = by_id.get("product_state_same_boundary")
    if product is None or not as_bool(product["relation_collapses"]):
        fail("product-state can-fail control did not collapse")
    if float(product["control_residual"]) <= TOL:
        fail("product-state control residual has no teeth")
    volume_rows = [row for row in rows if row["control_id"].startswith("volume_law_extra_pairs")]
    if len(volume_rows) < 2:
        fail("missing volume-law controls")
    for row in volume_rows:
        if not as_bool(row["relation_collapses"]) or float(row["control_residual"]) <= TOL:
            fail(f"volume-law control did not collapse: {row['control_id']}")
    slack = by_id.get("slack_budget_reversible_price_tail")
    if slack is None or not as_bool(slack["relation_collapses"]) or "lambda=0" not in slack["reason"]:
        fail("slack control did not recover zero price")


def validate_stage2_sweep() -> None:
    rows = read_csv("stage2_shadow_price_sweep_step39.csv")
    if len(rows) < 5:
        fail("stage-II sweep too small")
    if not all(as_bool(row["monotone_nonincreasing_from_previous"]) for row in rows):
        fail("stage-II lambda sweep is not monotone")
    if not any(float(row["lambda"]) > TOL and not as_bool(row["slack_tail"]) for row in rows):
        fail("stage-II sweep lacks a binding positive-price region")
    if not any(as_bool(row["slack_tail"]) and abs(float(row["lambda"])) <= TOL for row in rows):
        fail("stage-II sweep lacks a zero-price slack tail")


def validate_gates_and_antihardcode() -> None:
    gates = read_csv("six_gate_audit_step39.csv")
    required = {
        "primitive_exclusion",
        "dependency_trace",
        "ablation",
        "negative_controls_have_teeth",
        "stage_II_earns_place",
        "no_single_axiom_equivalence",
        "refinement_stability",
    }
    seen = {row["gate"]: row for row in gates}
    missing = required - set(seen)
    if missing:
        fail(f"missing six-gate rows: {sorted(missing)}")
    for gate in required:
        if not as_bool(seen[gate]["passes"]):
            fail(f"six-gate row failed: {gate}")
    for row in read_csv("anti_hardcode_step39.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-hardcode check failed: {row['check']}")
    build_text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ["0" + ".25", "1" + "/4G", "RT" + "_CONSTANT"]:
        if forbidden in build_text:
            fail(f"forbidden constant literal in build path: {forbidden}")


def validate_content_paths() -> None:
    rows = read_csv("content_classification_step39.csv")
    if not rows:
        fail("content classification is empty")
    for row in rows:
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"classification row lacks source path: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"source path is absolute: {source}")
            if not source.startswith("steps/"):
                fail(f"source path is not thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source path does not exist: {source}")
    statement_rows = [row for row in rows if row["artifact"] == "step39_area_shadow_price_statement.tex"]
    if not statement_rows or statement_rows[0]["grade"] != "recognition-landing":
        fail("statement must be graded as recognition-landing")


def validate_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in [
            "step39_results_summary.md",
            "nonclaim_boundary_step39.md",
            "step39_area_shadow_price_statement.tex",
            "mode_b_target_lineage.csv",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim phrase: {pattern}")


def run_chain() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"--self", "--chain"}:
        print("usage: run_step39.py --self|--chain", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_relation_rows()
    validate_controls()
    validate_stage2_sweep()
    validate_gates_and_antihardcode()
    validate_content_paths()
    validate_overclaims()
    print(f"run_step39.py: PASS {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
