#!/usr/bin/env python3
"""Validate Cluster A Step 36 higher-layer refinement artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "higher_layer_refinement_step36.py"

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
    STEPS_DIR / "step26_mode_b_integrated_normalization_artifacts" / "run_step26.py",
    STEPS_DIR / "step27_mode_b_normalization_robustness_artifacts" / "run_step27.py",
    STEPS_DIR / "step28_mode_b_neutral_representation_desmuggle_artifacts" / "run_step28.py",
    STEPS_DIR / "step29_mode_b_neutral_intrinsic_discriminator_artifacts" / "run_step29.py",
    STEPS_DIR / "step30_mode_b_conjoined_intrinsic_discriminator_artifacts" / "run_step30.py",
    STEPS_DIR / "step31_mode_b_consistency_discriminator_artifacts" / "run_step31.py",
    STEPS_DIR / "step32_mode_b_chirality_faithful_discriminator_artifacts" / "run_step32.py",
    STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "run_step33.py",
    STEPS_DIR / "step34_mode_b_role_obstruction_discriminator_artifacts" / "run_step34.py",
    STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "run_step35.py",
]

REQUIRED_FILES = [
    "higher_layer_refinement_step36.py",
    "higher_layer_refinement_scores_step36.csv",
    "refined_survivors_step36.csv",
    "refinement_counts_by_structure_step36.csv",
    "predicate_summary_step36.csv",
    "content_type_limit_assessment_step36.csv",
    "negative_controls_step36.csv",
    "stage2_audit_step36.csv",
    "forbidden_prior_self_check_step36.csv",
    "ablation_step36.csv",
    "dependency_trace_step36.csv",
    "six_gate_audit_step36.csv",
    "generated_vs_input_step36.csv",
    "higher_layer_refinement_output_step36.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step36_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step36.py",
]

BUILD_FORBIDDEN_SNIPPETS = [
    "total_slots",
    "FIVE",
    "SU(5)",
    "SO(10)",
    "10+5bar",
    "3 colors",
    "2 weak",
    "Higgs doublet",
    "observed Yukawa",
    "observed mass",
    "3 generations",
    "common-refinement",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "ψ",
]

BUILD_FORBIDDEN_PATTERNS = [
    r"\bembed(?:s|ding|ded)?\b",
    r"\bparent\s+group\b",
    r"\btarget_shape\b",
    r"\btarget_content\b",
    r"\bfixed_generation\b",
    r"\bgeneration_count\s*=\s*3\b",
    r"\bpotential_parameter\b",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bderives the content\b",
    r"\bderives the scalar sector\b",
    r"\bderives empirical masses\b",
    r"\bsolves mass generation\b",
    r"\bnew physical theory\b",
    r"\bframe-transfer certificate\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\bco-sourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"finite-carrier-diagnostic", "organizational", "remaining-external", "theorem-grade"}


def fail(message: str) -> None:
    print(f"run_step36.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
                f"{runner.name} failed during Step 36 chain\n"
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
            fail(f"build script contains forbidden primitive or construction snippet: {snippet}")
    for pattern in BUILD_FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            fail(f"build script appears to contain a forbidden primitive pattern: {pattern}")
    for required in [
        "staged_scalar_potential_closure",
        "scalar_quadratic_invariant",
        "active_factor_indices",
        "candidate_active_factors",
        "untouched_active_factors",
        "step35_survivors",
    ]:
        if required not in text:
            fail(f"build script missing required refinement component: {required}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step36.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "higher_layer_refinement_output_step36.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 36:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "CONTENT_TYPE_LIMIT":
            fail("expected CONTENT_TYPE_LIMIT verdict")
        if doc.get("reproduced_step35_survivors") != 12:
            fail("Step-35 survivor count was not reproduced")
        if doc.get("refined_survivors") != 8:
            fail("refined survivor count mismatch")
        if doc.get("single_factor_eliminated") is not True:
            fail("single-factor family should be eliminated")
        if doc.get("target_passes") is not True:
            fail("target/reference must pass")
        if doc.get("target_distinguished") is not False:
            fail("target/reference must not be uniquely distinguished")
        if doc.get("target_structure_only") is not True:
            fail("refined residual should be target-structure only")
        if doc.get("target_dimensions") != "2|3":
            fail("target/reference dimensions mismatch")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    for key in ("six_gates_pass", "forbidden_prior_self_check_pass", "stage_ii_pass", "negative_controls_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_computation_artifacts() -> None:
    scores = read_csv("higher_layer_refinement_scores_step36.csv")
    if len(scores) != 12:
        fail("refinement score table must contain Step-35 residual 12")
    refined = [row for row in scores if row["staged_potential_closure"] == "True"]
    if len(refined) != 8:
        fail("refined passing count mismatch")
    if any(row["dimensions"] != "2|3" for row in refined):
        fail("refined survivors must all be in the target structure family")
    if any(row["staged_potential_closure"] == "True" for row in scores if row["dimensions"] == "4"):
        fail("single-factor structure should be eliminated")
    target_rows = [row for row in scores if row["is_target_reference"] == "True"]
    if len(target_rows) != 1 or target_rows[0]["staged_potential_closure"] != "True":
        fail("target/reference status mismatch")
    survivors = read_csv("refined_survivors_step36.csv")
    if len(survivors) != 8:
        fail("refined survivor file count mismatch")
    counts = read_csv("refinement_counts_by_structure_step36.csv")
    keyed = {row["dimensions"]: row for row in counts}
    expected = {"2|3": ("8", "8", "1"), "4": ("4", "0", "0")}
    for dim, triple in expected.items():
        row = keyed.get(dim)
        if row is None:
            fail(f"missing structure count for {dim}")
        observed = (row["step35_survivors"], row["step36_survivors"], row["target_passes"])
        if observed != triple:
            fail(f"unexpected structure count for {dim}: {observed}")
    summary = read_csv("predicate_summary_step36.csv")
    if len(summary) != 1 or summary[0]["verdict"] != "CONTENT_TYPE_LIMIT":
        fail(f"unexpected predicate summary: {summary}")


def validate_gates_controls_and_classification() -> None:
    for name, field in [
        ("negative_controls_step36.csv", "passes"),
        ("stage2_audit_step36.csv", "passes"),
        ("six_gate_audit_step36.csv", "passes"),
        ("ablation_step36.csv", "load_bearing"),
    ]:
        rows = read_csv(name)
        if not rows or any(row[field] != "True" for row in rows):
            fail(f"{name} contains a failed gate/control/ablation")
    self_checks = read_csv("forbidden_prior_self_check_step36.csv")
    if not self_checks or any(row["passes"] != "False" for row in self_checks):
        fail("forbidden-prior self-check indicates a prior was used")
    classification = read_csv("content_classification.csv")
    if not classification:
        fail("content classification is empty")
    for row in classification:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad content grade: {row}")
        source = row["source_path"]
        if source.startswith("/") or ".." in Path(source).parts:
            fail(f"source path is not thread-root-relative: {source}")
        if not (THREAD_DIR / source).exists():
            fail(f"classified source missing: {source}")


def validate_self() -> None:
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_computation_artifacts()
    validate_gates_controls_and_classification()
    print("run_step36.py: PASS (--self)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="validate only Step 36 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 36 self-checks")
    args = parser.parse_args()
    if args.chain:
        run_prior_validators()
    validate_self()


if __name__ == "__main__":
    main()
