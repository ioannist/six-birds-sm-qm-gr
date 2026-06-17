#!/usr/bin/env python3
"""Validate Cluster A Step 22 Mode-B group-shape generation artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_group_shape_generation_step22.py"

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
    STEPS_DIR / "step21_mode_b_unifying_carrier_artifacts" / "run_step21.py",
]

REQUIRED_FILES = [
    "mode_b_group_shape_generation_step22.py",
    "sector_enumeration_step22.csv",
    "minimal_closures_step22.csv",
    "negative_controls_step22.csv",
    "stage2_reproduction_step22.csv",
    "six_gate_audit_step22.csv",
    "generated_vs_input_step22.csv",
    "mode_b_group_shape_output_step22.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step22_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step22.py",
]

PRIMITIVE_EXCLUSION_PATTERNS = [
    r"\b2\b",
    r"\b3\b",
    r"2\|3",
    r"1\|2",
    r"SU\(3\)",
    r"SU\(2\)",
    r"SU\(5\)",
    r"SU\(3\)xSU\(2\)xU\(1\)",
    r"rank 4",
    r"10\+5bar",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves E019\b",
    r"\bsolve E019\b",
    r"\bderives the gauge group\b",
    r"\bderive the gauge group\b",
    r"\bnew physics prediction\b",
    r"\bphysical gauge-sector theorem\b.*\btrue\b",
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
    print(f"run_step22.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
                f"{runner.name} failed during Step 22 chain\n"
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
        if path.name == "run_step22.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_generation_result() -> None:
    output = json.loads((ARTIFACT_DIR / "mode_b_group_shape_output_step22.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if output.get("mode") != "ModeB_generation" or output.get("verdict") != "GENERATED":
        fail("output must be ModeB GENERATED")
    enum = output["enumeration"]
    if enum["structure_count"] != 35 or enum["closing_count"] != 1:
        fail(f"enumeration counts mismatch: {enum}")
    minimal = output["minimal_closures"]
    if len(minimal) != 1:
        fail(f"expected one minimal closure, got {len(minimal)}")
    if minimal[0]["ranks"] != "1|2" or minimal[0]["dimensions"] != "2|3":
        fail(f"minimal generated structure mismatch: {minimal[0]}")
    schema_min = schema["minimal_generated_structures"]
    if len(schema_min) != 1 or schema_min[0]["recognition_lands_on_sm_shape"] is not True:
        fail("schema recognition landing mismatch")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")


def validate_controls_and_gates() -> None:
    controls = read_csv("negative_controls_step22.csv")
    if len(controls) < 3:
        fail("negative controls missing")
    for row in controls:
        if row["should_close"] != "False" or row["closes"] != "False" or row["passes"] != "True":
            fail(f"should-not-close control failed: {row}")
    stage_rows = read_csv("stage2_reproduction_step22.csv")
    if len(stage_rows) < 2:
        fail("Stage II rows missing")
    for row in stage_rows:
        if row["passes"] != "True":
            fail(f"Stage II check failed: {row}")
    gates = {row["gate"]: row for row in read_csv("six_gate_audit_step22.csv")}
    required = {
        "primitive_exclusion",
        "dependency_trace",
        "ablation",
        "negative_controls",
        "stage_ii_earning",
        "no_single_axiom_equivalence",
    }
    if set(gates) != required:
        fail(f"gate set mismatch: {set(gates)}")
    for gate, row in gates.items():
        if row["passes"] != "True":
            fail(f"gate failed: {gate}")


def validate_generated_vs_input() -> None:
    rows = {row["item"]: row for row in read_csv("generated_vs_input_step22.csv")}
    for item in ["bounded_rank_range", "bounded_factor_count", "chirality_requirement", "anomaly_and_charge_tests"]:
        if rows.get(item, {}).get("status") != "input":
            fail(f"input boundary missing for {item}")
    if rows.get("minimal_sector_structure", {}).get("status") != "generated":
        fail("minimal sector structure must be marked generated")
    if rows.get("minimal_sector_structure", {}).get("detail") != "2|3":
        fail("generated minimal sector detail mismatch")


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
        "Generated-vs-input breakdown",
        "Closing structures: `1`",
        "ranks `1|2`, dimensions `2|3`",
        "does not settle E019",
    ]:
        if snippet not in summary:
            fail(f"summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for snippet in [
        "finite Mode-B enumeration",
        "Inputs:",
        "Outputs:",
        "does not use that pattern as a primitive",
    ]:
        if snippet not in boundary:
            fail(f"nonclaim boundary missing snippet: {snippet}")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_generation_result()
    validate_controls_and_gates()
    validate_generated_vs_input()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 22 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 22 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 22")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step22.py: PASS")


if __name__ == "__main__":
    main()
