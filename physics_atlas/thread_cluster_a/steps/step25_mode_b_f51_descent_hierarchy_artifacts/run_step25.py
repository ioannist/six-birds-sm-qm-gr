#!/usr/bin/env python3
"""Validate Cluster A Step 25 F51 descent-hierarchy artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_f51_descent_hierarchy_step25.py"

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
    STEPS_DIR / "step22_mode_b_group_shape_generation_artifacts" / "run_step22.py",
    STEPS_DIR / "step23_mode_b_factor_count_unsmuggle_artifacts" / "run_step23.py",
    STEPS_DIR / "step24_mode_b_robustness_stress_artifacts" / "run_step24.py",
]

REQUIRED_FILES = [
    "mode_b_f51_descent_hierarchy_step25.py",
    "branching_roles_step25.csv",
    "f51_descent_step25.csv",
    "descent_obstructions_step25.csv",
    "negative_controls_step25.csv",
    "dependency_trace_step25.csv",
    "ablation_step25.csv",
    "stage2_reproduction_step25.csv",
    "six_gate_audit_step25.csv",
    "mode_b_f51_descent_output_step25.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step25_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step25.py",
]

BUILD_FORBIDDEN_SNIPPETS = [
    "SU(5)",
    "SO(10)",
    "SU(6)",
    "2|3",
    "10+5bar",
    "SM ->",
    "SM->",
    "known breaking",
    "psi",
    "ψ",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
]

BUILD_FORBIDDEN_PATTERNS = [
    r"if\s+.*parent_id\s*(?:==|!=)",
    r"if\s+.*structure_id\s*(?:==|!=)",
    r"if\s+.*\bSU\b",
    r"if\s+.*\bSO\b",
    r"branch(?:ing)?_table\s*=",
    r"hardcoded_branch",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves unification\b",
    r"\bsolves E019\b",
    r"\bderives the gauge group\b",
    r"\bderive the gauge group\b",
    r"\bnew physics prediction\b",
    r"\bis a new physical theory\b",
    r"\b(?:claims?|is)\s+a\s+physical unification theorem\b",
    r"\b(?:claims?|is)\s+a\s+frame-transfer certificate\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\bco-sourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step25.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 25 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_guards() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for snippet in BUILD_FORBIDDEN_SNIPPETS:
        if snippet in text:
            fail(f"build script contains forbidden primitive or construction term: {snippet}")
    for pattern in BUILD_FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            fail(f"build script appears to hardcode a branching verdict: {pattern}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step25.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "mode_b_f51_descent_output_step25.json").read_text(encoding="utf-8"))
    if schema.get("step") != 25 or output.get("step") != 25:
        fail("schema/output step mismatch")
    if schema.get("verdict") != "HIERARCHY_SCOPED" or output.get("verdict") != "HIERARCHY_SCOPED":
        fail("expected HIERARCHY_SCOPED verdict")
    if schema.get("typed_no_go") or output.get("typed_no_go"):
        fail("Step 25 should not report typed no-go for the computed scoped hierarchy")
    for doc in (schema, output):
        if doc.get("new_physics_claim") or doc.get("root_landed") or doc.get("frame_transfer_certified"):
            fail("schema/output overstates status")
    if schema.get("exact_parent_count") != 1 or schema.get("scoped_neutral_parent_count") != 1:
        fail("expected one exact parent and one scoped neutral parent")
    if schema.get("negative_control_count") != 1 or not schema.get("six_gates_pass") or not schema.get("stage_ii_pass"):
        fail("controls/gates mismatch in schema")


def validate_descent_tables() -> None:
    rows = {row["parent_id"]: row for row in read_csv("f51_descent_step25.csv")}
    required = {"SU(5)", "SO(10)", "SU(6)_chiral_example"}
    if set(rows) != required:
        fail(f"unexpected parent rows: {set(rows)}")
    su5 = rows["SU(5)"]
    if su5["verdict"] != "PASS_EXACT_PARENT_SHADOW" or su5["charged_content_obstruction"] != "0" or su5["full_content_obstruction"] != "0":
        fail(f"exact parent row mismatch: {su5}")
    so10 = rows["SO(10)"]
    if so10["verdict"] != "PASS_SCOPED_NEUTRAL_RESIDUAL" or so10["charged_content_obstruction"] != "0" or so10["full_content_obstruction"] != "1":
        fail(f"scoped parent row mismatch: {so10}")
    su6 = rows["SU(6)_chiral_example"]
    if su6["verdict"] != "FAIL_NOT_PARENT" or su6["charged_content_obstruction"] != "5" or su6["full_content_obstruction"] != "5":
        fail(f"negative parent row mismatch: {su6}")
    controls = read_csv("negative_controls_step25.csv")
    if len(controls) != 1:
        fail("expected exactly one negative-control row")
    control = controls[0]
    if control["passes"] != "True" or control["passes_parent_test"] != "False":
        fail(f"negative control failed: {control}")


def validate_gates_and_stage2() -> None:
    gates = {row["gate"]: row for row in read_csv("six_gate_audit_step25.csv")}
    expected = {
        "primitive_exclusion",
        "dependency_trace",
        "ablation",
        "negative_controls",
        "stage_ii_earning",
        "no_single_axiom_equivalence",
    }
    if set(gates) != expected:
        fail(f"gate set mismatch: {set(gates)}")
    for gate, row in gates.items():
        if row["passes"] != "True":
            fail(f"gate failed: {gate}")
    stage_rows = read_csv("stage2_reproduction_step25.csv")
    if len(stage_rows) != 1:
        fail("Stage II table row mismatch")
    stage = stage_rows[0]
    if stage["passes"] != "True" or stage["charge_gravity_sum"] != "0" or stage["charge_cubed_sum"] != "0":
        fail(f"Stage II balance mismatch: {stage}")
    ablations = read_csv("ablation_step25.csv")
    if len(ablations) != 4 or any(row["descent_supported"] != "False" for row in ablations):
        fail(f"ablation evidence mismatch: {ablations}")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"invalid grade: {row}")
        for source in row["source_artifacts"].split(";"):
            source = source.strip()
            if source.startswith("/"):
                fail(f"absolute source path is not allowed: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"missing cited source: {source}")


def validate_summary_text() -> None:
    summary = (ARTIFACT_DIR / "results_summary.md").read_text(encoding="utf-8")
    required = [
        "Generated-vs-input breakdown first",
        "PASS_EXACT_PARENT_SHADOW",
        "PASS_SCOPED_NEUTRAL_RESIDUAL",
        "FAIL_NOT_PARENT",
        "HIERARCHY_SCOPED",
        "not a physical gauge-unification claim",
    ]
    for snippet in required:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for snippet in ["finite Mode-B parent-shadow audit", "does not claim", "frame-transfer status upgrade"]:
        if snippet not in boundary:
            fail(f"nonclaim boundary missing snippet: {snippet}")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_descent_tables()
    validate_gates_and_stage2()
    validate_content_classification()
    validate_summary_text()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 25 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 25 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 25 self checks")
    args = parser.parse_args()
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step25.py: PASS")


if __name__ == "__main__":
    main()
