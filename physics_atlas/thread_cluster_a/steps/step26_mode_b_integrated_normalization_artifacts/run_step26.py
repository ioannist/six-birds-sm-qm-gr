#!/usr/bin/env python3
"""Validate Cluster A Step 26 integrated normalization artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_integrated_normalization_step26.py"

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
    STEPS_DIR / "step25_mode_b_f51_descent_hierarchy_artifacts" / "run_step25.py",
]

REQUIRED_FILES = [
    "mode_b_integrated_normalization_step26.py",
    "integrated_normalization_step26.csv",
    "trace_terms_step26.csv",
    "negative_controls_step26.csv",
    "stage2_reproduction_step26.csv",
    "dependency_trace_step26.csv",
    "ablation_step26.csv",
    "generated_vs_input_step26.csv",
    "six_gate_audit_step26.csv",
    "mode_b_integrated_normalization_output_step26.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step26_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step26.py",
]

BUILD_FORBIDDEN_SNIPPETS = [
    "3/8",
    "0.375",
    "2|3",
    "3|-2",
    "r1|2",
    "hardcoded",
    "psi",
    "ψ",
    "co-sourcing",
    "common-refinement-as-QMGR-cosourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
]

BUILD_FORBIDDEN_PATTERNS = [
    r"if\s+.*structure_id\s*(?:==|!=)\s*[\"']",
    r"if\s+.*dimensions\s*(?:==|!=)\s*[\"']",
    r"if\s+.*selected_charge_vector\s*(?:==|!=)\s*[\"']",
    r"target_shape\s*=",
    r"target_charge",
    r"sin2_target\s*=",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves unification\b",
    r"\bsolves E019\b",
    r"\bderives the gauge group\b",
    r"\bderive the gauge group\b",
    r"\bderives measured gauge couplings\b",
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
    print(f"run_step26.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 26 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_guards() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "minimal_closures_step23.csv" not in text or "sector_enumeration_step23.csv" not in text:
        fail("build script does not read the Step-23 generated outputs")
    for snippet in BUILD_FORBIDDEN_SNIPPETS:
        if snippet in text:
            fail(f"build script contains forbidden primitive/construction snippet: {snippet}")
    for pattern in BUILD_FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            fail(f"build script appears to reintroduce a target primitive: {pattern}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step26.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "mode_b_integrated_normalization_output_step26.json").read_text(encoding="utf-8"))
    if schema.get("step") != 26 or output.get("step") != 26:
        fail("schema/output step mismatch")
    if schema.get("verdict") != "INTEGRATED" or output.get("verdict") != "INTEGRATED":
        fail("expected INTEGRATED verdict")
    if schema.get("typed_no_go") or output.get("typed_no_go"):
        fail("integrated verdict should not be typed no-go")
    for doc in (schema, output):
        if doc.get("new_physics_claim") or doc.get("root_landed") or doc.get("frame_transfer_certified"):
            fail("schema/output overstates status")
    computed = schema.get("computed_normalization", {})
    expected = {
        "trace_y2": "5/6",
        "trace_t3_2": "1/2",
        "normalization_ratio": "5/3",
        "sin2_theta_w": "3/8",
    }
    if computed != expected:
        fail(f"computed normalization mismatch: {computed}")
    if not schema.get("negative_controls_pass") or not schema.get("stage_ii_pass") or not schema.get("six_gates_pass"):
        fail("schema controls/gates mismatch")


def validate_normalization_tables() -> None:
    rows = read_csv("integrated_normalization_step26.csv")
    if len(rows) != 1:
        fail("integrated normalization table must have one row")
    row = rows[0]
    expected = {
        "source": "step23_generated_minimal_closure",
        "charge_unit": "1/6",
        "trace_y2": "5/6",
        "trace_t3_2": "1/2",
        "normalization_ratio": "5/3",
        "sin2_theta_w": "3/8",
        "status": "COMPUTED",
        "verdict": "INTEGRATED",
    }
    for key, value in expected.items():
        if row.get(key) != value:
            fail(f"normalization row mismatch for {key}: {row}")
    terms = read_csv("trace_terms_step26.csv")
    if len(terms) != 2:
        fail(f"expected two trace term rows, got {len(terms)}")
    if sorted(term["trace_y2_contribution"] for term in terms) != ["1/2", "1/3"]:
        fail(f"trace term contributions mismatch: {terms}")


def validate_controls_and_gates() -> None:
    controls = read_csv("negative_controls_step26.csv")
    if len(controls) < 3:
        fail("expected at least three negative controls")
    if any(row["passes"] != "True" for row in controls):
        fail(f"negative control failed: {controls}")
    if not any(row["normalization_status"] == "COMPUTED" and row["sin2_theta_w"] != "3/8" for row in controls):
        fail("no computed different-value negative control")
    if not any(row["normalization_status"] == "FAILED" for row in controls):
        fail("no failed-readout negative control")
    stage = read_csv("stage2_reproduction_step26.csv")
    if len(stage) != 1 or stage[0]["passes"] != "True" or stage[0]["charge_unit"] != "1/6":
        fail(f"Stage II mismatch: {stage}")
    gates = {row["gate"]: row for row in read_csv("six_gate_audit_step26.csv")}
    expected_gates = {
        "primitive_exclusion",
        "dependency_trace",
        "ablation",
        "negative_controls",
        "stage_ii_earning",
        "no_single_axiom_equivalence",
    }
    if set(gates) != expected_gates:
        fail(f"gate set mismatch: {set(gates)}")
    if any(row["passes"] != "True" for row in gates.values()):
        fail(f"gate failure: {gates}")
    ablations = read_csv("ablation_step26.csv")
    if len(ablations) != 4 or any(row["normalization_supported"] != "False" for row in ablations):
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
    for snippet in [
        "Generated-vs-input breakdown first",
        "verdict: `INTEGRATED`",
        "Negative Controls",
        "not a physical unification theorem",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for snippet in ["does not claim", "frame-transfer status upgrade", "Remaining inputs are explicit"]:
        if snippet not in boundary:
            fail(f"nonclaim boundary missing snippet: {snippet}")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_normalization_tables()
    validate_controls_and_gates()
    validate_content_classification()
    validate_summary_text()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 26 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 26 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 26 self checks")
    args = parser.parse_args()
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step26.py: PASS")


if __name__ == "__main__":
    main()
