#!/usr/bin/env python3
"""Validate Cluster A Step 21 Mode-B unifying-carrier artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import runpy
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_unifying_carrier_step21.py"

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
    STEPS_DIR / "step11_refinement_order_battery_artifacts" / "run_step11.py",
    STEPS_DIR / "step14_real_anomaly_enrichment_artifacts" / "run_step14.py",
    STEPS_DIR / "step15_minimal_anomaly_support_artifacts" / "run_step15.py",
    STEPS_DIR / "step16_content_selection_principle_artifacts" / "run_step16.py",
    STEPS_DIR / "step17_two_layer_test_artifacts" / "run_step17.py",
    STEPS_DIR / "step18_two_layer_stress_test_artifacts" / "run_step18.py",
    STEPS_DIR / "step19_layer_multiplicity_F24_artifacts" / "run_step19.py",
    STEPS_DIR / "step20_gut_recognition_value_relations_artifacts" / "run_step20.py",
]

REQUIRED_FILES = [
    "mode_b_unifying_carrier_step21.py",
    "carrier_signature_step21.csv",
    "generator_table_step21.csv",
    "q_lens_step21.csv",
    "u_non_descent_step21.csv",
    "descent_audit_step21.csv",
    "generated_normalization_step21.csv",
    "dependency_trace_step21.csv",
    "ablation_step21.csv",
    "negative_controls_step21.csv",
    "stage2_reproduction_step21.csv",
    "six_gate_audit_step21.csv",
    "mode_b_unifying_carrier_output_step21.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step21_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step21.py",
]

PRIMITIVE_EXCLUSION_PATTERNS = [
    r"3/8",
    r"0\.375",
    r"SU\(5\)",
    r"10\+5bar",
    r"sin2\s*=",
    r"5/3",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves unification\b",
    r"\bsolve unification\b",
    r"\bSBT derives the SM\b",
    r"\bSBT-derived SM\b",
    r"\bSBT derives the gauge\b",
    r"\bnew physics prediction\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
]

BUILD_FORBIDDEN = [
    "psi",
    "ψ",
    "co-sourcing",
    "common-refinement",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
]

ALLOWED_GRADES = {"finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step21.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def run_build_script() -> None:
    runpy.run_path(str(BUILD_SCRIPT), run_name="__main__")


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
                f"{runner.name} failed during Step 21 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_guards() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for snippet in BUILD_FORBIDDEN:
        if snippet in text:
            fail(f"build script contains forbidden construction term: {snippet}")
    for pattern in PRIMITIVE_EXCLUSION_PATTERNS:
        if re.search(pattern, text):
            fail(f"primitive-exclusion violation in build script: {pattern}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step21.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_unifying_outputs() -> None:
    output = json.loads((ARTIFACT_DIR / "mode_b_unifying_carrier_output_step21.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if output.get("mode") != "ModeB_generation":
        fail("output mode mismatch")
    if output["u_non_descent"]["non_descending"] is not True:
        fail("U must be non-descending")
    if output["u_non_descent"]["obstruction_count"] < 1:
        fail("U obstruction count must be positive")
    if output["c_u_descent"]["descends"] is not True:
        fail("C(U) must descend")
    if output["c_u_descent"]["obstruction_count"] != 0:
        fail("C(U) obstruction must be zero")
    ratio = parse_fraction(output["c_u_descent"]["normalization_ratio"])
    weak_mix = parse_fraction(output["c_u_descent"]["weak_mixing_relation"])
    if ratio != Fraction(5, 3):
        fail(f"generated normalization mismatch: {ratio}")
    if weak_mix != Fraction(3, 8):
        fail(f"generated weak-mixing relation mismatch: {weak_mix}")
    if schema.get("generated_normalization_ratio") != "5/3":
        fail("schema normalization mismatch")
    if schema.get("generated_weak_mixing_relation") != "3/8":
        fail("schema weak-mixing mismatch")
    if schema.get("recognition_lands_on_su5_value") is not True:
        fail("schema must record recognition landing")
    if output.get("six_gates_pass") is not True or schema.get("verdict") != "PASS-with-recognition":
        fail("six-gates/verdict mismatch")
    if output.get("root_landed") or output.get("frame_transfer_certified") or output.get("new_physics_claim"):
        fail("output overstates status")


def validate_tables() -> None:
    gates = {row["gate"]: row for row in read_csv("six_gate_audit_step21.csv")}
    required_gates = {
        "primitive_exclusion",
        "dependency_trace",
        "ablation",
        "negative_controls",
        "stage_ii_earning",
        "no_single_axiom_equivalence",
    }
    if set(gates) != required_gates:
        fail(f"gate set mismatch: {set(gates)}")
    for gate, row in gates.items():
        if row["passes"] != "True":
            fail(f"gate failed: {gate}")
    negative_rows = read_csv("negative_controls_step21.csv")
    if len(negative_rows) < 2:
        fail("need at least two false targets")
    for row in negative_rows:
        if row["descends_to_false_target"] != "False":
            fail(f"false target descended: {row}")
    ablation_rows = read_csv("ablation_step21.csv")
    if len(ablation_rows) < 6:
        fail("ablation table too small")
    if any(row["single_axiom_equivalent_to_target"] != "False" for row in ablation_rows):
        fail("single-axiom equivalence detected")
    non_descent = read_csv("u_non_descent_step21.csv")
    if not non_descent or non_descent[0]["obstruction"] != "True":
        fail("U non-descent witness missing")
    descent = read_csv("descent_audit_step21.csv")
    if not descent or descent[0]["obstruction_count"] != "0":
        fail("C(U) descent audit mismatch")
    norm_rows = {row["quantity"]: row for row in read_csv("generated_normalization_step21.csv")}
    if parse_fraction(norm_rows["normalization_ratio"]["fraction"]) != Fraction(5, 3):
        fail("normalization table mismatch")
    if parse_fraction(norm_rows["weak_mixing_relation"]["fraction"]) != Fraction(3, 8):
        fail("weak-mixing table mismatch")


def validate_stage_ii() -> None:
    rows = read_csv("stage2_reproduction_step21.csv")
    totals = [row for row in rows if row["role"] == "total"]
    if len(totals) != 1:
        fail("Stage II total row missing")
    total = totals[0]
    for key in [
        "color_color_charge_contribution",
        "weak_weak_charge_contribution",
        "charge_cubed_contribution",
        "charge_gravity_contribution",
    ]:
        if parse_fraction(total[key]) != 0:
            fail(f"Stage II anomaly sum not zero for {key}: {total[key]}")
    output = json.loads((ARTIFACT_DIR / "mode_b_unifying_carrier_output_step21.json").read_text(encoding="utf-8"))
    if output["stage_ii"]["passes"] is not True:
        fail("output Stage II flag false")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"claim lacks source artifacts: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"source path must be thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact missing: {source}")


def validate_required_prose() -> None:
    summary = (ARTIFACT_DIR / "results_summary.md").read_text(encoding="utf-8")
    for snippet in [
        "PASS-with-recognition",
        "Primitive exclusion",
        "Stage II reproduction passes",
        "Step-20 real-world non-SUSY near-miss still stands",
    ]:
        if snippet not in summary:
            fail(f"summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for snippet in [
        "finite Mode-B generation",
        "not a carrier primitive",
        "near-miss/failure",
        "frame-transfer status",
    ]:
        if snippet not in boundary:
            fail(f"nonclaim boundary missing snippet: {snippet}")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_unifying_outputs()
    validate_tables()
    validate_stage_ii()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 21 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 21 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 21")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step21.py: PASS")


if __name__ == "__main__":
    main()
