#!/usr/bin/env python3
"""Validate Cluster A Step 63 unification common-refinement artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = ARTIFACT_DIR / "unification_common_refinement_step63.py"

REQUIRED_FILES = [
    "step63_results_summary.md",
    "step63_schema.json",
    "content_classification_step63.csv",
    "nonclaim_boundary_step63.md",
    "step63_statement.tex",
    "run_step63.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "generated_vs_input_step63.csv",
    "six_gate_audit_step63.csv",
    "anti_circularity_step63.csv",
    "no_hardcode_step63.csv",
    "parent_candidates_step63.csv",
    "trace_arithmetic_step63.csv",
    "hypercharge_normalization_step63.csv",
    "refinement_defect_step63.csv",
]


def fail(message: str) -> None:
    print(f"run_step63.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_fraction(text: str) -> Fraction:
    return Fraction(text)


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step63_schema.json").read_text(encoding="utf-8"))
    required = {
        "step": 63,
        "orientation": "ModeB_F51_common_refinement_descent",
        "exit_state": "GROUND_landing_conditional_on_named_source",
        "sin2thetaW_hardcoded": False,
        "hypercharge_norm_computed": True,
        "anti_circularity_pass": True,
        "no_hardcode_pass": True,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "derives_sm_couplings": False,
        "root_landed": True,
    }
    for key, expected in required.items():
        if schema.get(key) != expected:
            fail(f"schema field {key!r} expected {expected!r}, got {schema.get(key)!r}")
    if not schema.get("parent_forced"):
        fail("parent_forced should be true under the declared source")
    if not schema.get("declared_recognition_source"):
        fail("declared recognition source missing")
    converted = set(schema.get("shadows_converted", []))
    expected = {"hypercharge_normalization", "embedding_trace_ratio", "xy_refinement_defect"}
    if converted != expected:
        fail(f"unexpected shadows_converted: {converted}")
    return schema


def validate_trace(schema: dict[str, object]) -> None:
    rows = read_csv(ARTIFACT_DIR / "trace_arithmetic_step63.csv")
    total = next((row for row in rows if row["state_id"] == "TOTAL"), None)
    ratio = next((row for row in rows if row["state_id"] == "TRACE_RATIO"), None)
    if not total or not ratio:
        fail("trace arithmetic missing TOTAL or TRACE_RATIO")
    computed = parse_fraction(total["multiplicity_times_T3_sq"]) / parse_fraction(total["multiplicity_times_Q_sq"])
    if str(computed) != schema["sin2thetaW_computed_value"]:
        fail(f"schema trace ratio mismatch: table {computed}, schema {schema['sin2thetaW_computed_value']}")
    if parse_fraction(ratio["Q"]) != computed:
        fail("TRACE_RATIO row does not match totals")
    parent_rows = read_csv(ARTIFACT_DIR / "parent_candidates_step63.csv")
    selected = [row for row in parent_rows if row["declared_source_selects"] == "True"]
    if len(selected) != 1:
        fail(f"expected one selected parent, got {len(selected)}")
    if selected[0]["sin2thetaW_fraction"] != str(computed):
        fail("selected parent ratio does not match computed trace ratio")


def validate_hypercharge_norm(schema: dict[str, object]) -> None:
    row = read_csv(ARTIFACT_DIR / "hypercharge_normalization_step63.csv")[0]
    trace_y = parse_fraction(row["fundamental_trace_Y_sq"])
    canonical_trace = parse_fraction(row["canonical_generator_trace"])
    k_y = trace_y / canonical_trace
    scale_sq = canonical_trace / trace_y
    if row["canonical_kY"] != str(k_y):
        fail("canonical_kY is not computed from trace")
    if row["normalized_scale_squared"] != str(scale_sq):
        fail("normalized scale squared is not computed from trace")
    if schema["hypercharge_kY"] != row["canonical_kY"]:
        fail("schema hypercharge_kY mismatch")


def validate_no_hardcode() -> None:
    rows = read_csv(ARTIFACT_DIR / "no_hardcode_step63.csv")
    failing = [row for row in rows if row["passes"] != "True"]
    if failing:
        fail(f"no-hardcode checks failed: {failing}")
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    target_fraction = f"{3}/{8}"
    target_decimal = "0." + "375"
    if target_fraction in source or target_decimal in source:
        fail("target trace ratio literal appears in build source")
    if "TARGET_RATIO" in source or "target_ratio" in source:
        fail("target ratio flag appears in build source")


def validate_anti_circularity() -> None:
    rows = read_csv(ARTIFACT_DIR / "anti_circularity_step63.csv")
    failing = [row for row in rows if row["passes"] != "True"]
    if failing:
        fail(f"anti-circularity checks failed: {failing}")
    by_check = {row["check"]: row for row in rows}
    if "REQ_U_alone_not_enough" not in by_check:
        fail("missing REQ_U_alone_not_enough check")
    if "declared_source_load_bearing" not in by_check:
        fail("missing declared_source_load_bearing check")
    if "product control" not in by_check["REQ_U_alone_not_enough"]["evidence"]:
        fail("anti-circularity evidence does not cite product control")


def validate_defect() -> None:
    row = read_csv(ARTIFACT_DIR / "refinement_defect_step63.csv")[0]
    if row["delta_sm_to_parent_count"] != "15":
        fail("expected Step47 Delta_fact(SM,parent) count 15")
    if row["delta_parent_to_sm_count"] != "0":
        fail("expected reverse defect count 0")
    if row["xy_witness_identity"] != "True":
        fail("X/Y witness identity failed")


def validate_gates_and_docs() -> None:
    for csv_name in ("six_gate_audit_step63.csv",):
        failing = [row for row in read_csv(ARTIFACT_DIR / csv_name) if row["passes"] != "True"]
        if failing:
            fail(f"{csv_name} has failing rows: {failing}")
    generated = read_csv(ARTIFACT_DIR / "generated_vs_input_step63.csv")
    statuses = {row["item"]: row["status"] for row in generated}
    if statuses.get("minimal_simple_single_irrep_source") != "declared_recognition_source":
        fail("declared source is not recorded as an input recognition source")
    summary = (ARTIFACT_DIR / "step63_results_summary.md").read_text(encoding="utf-8")
    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary_step63.md").read_text(encoding="utf-8")
    for snippet in ("not derived here", "conditional on the declared", "measured low-energy"):
        if snippet not in summary:
            fail(f"summary missing caveat snippet: {snippet}")
    for snippet in ("does not derive", "does not prove", "frame transfer"):
        if snippet not in nonclaim:
            fail(f"nonclaim missing caveat snippet: {snippet}")


def run_build() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def validate() -> None:
    validate_required_files()
    schema = validate_schema()
    validate_trace(schema)
    validate_hypercharge_norm(schema)
    validate_no_hardcode()
    validate_anti_circularity()
    validate_defect()
    validate_gates_and_docs()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if args.chain:
        run_build()
    validate()
    print("run_step63.py: PASS")


if __name__ == "__main__":
    main()
