#!/usr/bin/env python3
"""Validate Cluster A Step 39 clean-separation derivation artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "clean_separation_derivation_step39.py"

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
    STEPS_DIR / "step36_mode_b_higher_layer_refinement_artifacts" / "run_step36.py",
    STEPS_DIR / "step37_mode_b_uniqueness_stress_test_artifacts" / "run_step37.py",
    STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "run_step38.py",
]

REQUIRED_FILES = [
    "clean_separation_derivation_step39.py",
    "confining_standardness_scores_step39.csv",
    "standardness_by_structure_step39.csv",
    "implication_test_step39.csv",
    "relaxation_robustness_step39.csv",
    "detectors_step39.csv",
    "predicate_summary_step39.csv",
    "negative_controls_step39.csv",
    "stage2_audit_step39.csv",
    "forbidden_prior_self_check_step39.csv",
    "ablation_step39.csv",
    "dependency_trace_step39.csv",
    "six_gate_audit_step39.csv",
    "generated_vs_input_step39.csv",
    "clean_separation_derivation_output_step39.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step39_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step39.py",
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
    r"\brequires_two_factors\b",
    r"\bfactor_count\s*[<>=]",
    r"\bargmin\b",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bderives the content\b",
    r"\bderives the scalar sector\b",
    r"\bderived fundamental condition\b",
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
    print(f"run_step39.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 39 chain\n"
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
            fail(f"build script appears to contain a forbidden shape/minimality pattern: {pattern}")
    for required in [
        "confining_charged_fermion_types",
        "standard_confining_sector",
        "standard_implies_clean",
        "clean_implies_standard",
        "circularity_detected",
        "relaxed_allows_vectors",
    ]:
        if required not in text:
            fail(f"build script missing required derivation-test component: {required}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step39.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "clean_separation_derivation_output_step39.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 39:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "INDEPENDENT_INTRODUCED_CIRCULAR":
            fail("expected introduced/circular verdict")
        if doc.get("reproduced_step35_survivors") != 12:
            fail("Step-35 survivor count was not reproduced")
        if doc.get("standard_count") != 8 or doc.get("relaxed_count") != 12:
            fail("standard/relaxed counts mismatch")
        if doc.get("standard_implies_clean") is not True:
            fail("standardness should imply clean separation")
        if doc.get("clean_implies_standard") is not True:
            fail("clean separation should imply standardness on this carrier")
        if doc.get("circularity_detected") is not True:
            fail("circularity must be detected")
        if doc.get("derived_fundamental") is not False:
            fail("derived fundamental status must be false")
        if doc.get("single_factor_returns_when_relaxed") is not True:
            fail("relaxation should restore the single-factor family")
        if doc.get("target_passes") is not True or doc.get("target_distinguished") is not False:
            fail("target/reference status mismatch")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    for key in ("six_gates_pass", "forbidden_prior_self_check_pass", "stage_ii_pass", "negative_controls_pass", "detectors_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_computation_artifacts() -> None:
    scores = read_csv("confining_standardness_scores_step39.csv")
    if len(scores) != 12:
        fail("score table must contain Step-35 residual 12")
    if sum(1 for row in scores if row["standard_confining_sector"] == "True") != 8:
        fail("standardness count mismatch")
    if sum(1 for row in scores if row["relaxed_allows_vectors"] == "True") != 12:
        fail("relaxation count mismatch")
    if not all(row["standard_confining_sector"] == "False" for row in scores if row["dimensions"] == "4"):
        fail("single-factor rows should fail standardness")
    if not all(row["relaxed_allows_vectors"] == "True" for row in scores if row["dimensions"] == "4"):
        fail("single-factor rows should return under relaxation")
    implication = {row["test"]: row for row in read_csv("implication_test_step39.csv")}
    for test in [
        "standardness_implies_clean_separation",
        "clean_separation_implies_standardness",
        "extensional_equivalence_on_carrier",
        "derived_fundamental_not_established",
    ]:
        if implication[test]["passes"] != "True":
            fail(f"implication test failed: {test}")
    relaxation = {row["relaxation"]: row for row in read_csv("relaxation_robustness_step39.csv")}
    if relaxation["allow_confining_charged_massive_vectors"]["survivor_count"] != "12":
        fail("relaxed survivor count mismatch")
    if relaxation["enforce_standardness"]["survivor_count"] != "8":
        fail("standardness survivor count mismatch")
    detectors = {row["detector"]: row for row in read_csv("detectors_step39.csv")}
    if detectors["shape_flavored"]["flagged"] != "False":
        fail("shape detector should not flag")
    if detectors["minimality_or_size_selector"]["flagged"] != "False":
        fail("minimality detector should not flag")
    if detectors["circularity"]["flagged"] != "True":
        fail("circularity detector must flag")
    summary = read_csv("predicate_summary_step39.csv")
    if len(summary) != 1 or summary[0]["verdict"] != "INDEPENDENT_INTRODUCED_CIRCULAR":
        fail(f"unexpected predicate summary: {summary}")


def validate_gates_controls_and_classification() -> None:
    for name, field in [
        ("negative_controls_step39.csv", "passes"),
        ("stage2_audit_step39.csv", "passes"),
        ("six_gate_audit_step39.csv", "passes"),
    ]:
        rows = read_csv(name)
        if not rows or any(row[field] != "True" for row in rows):
            fail(f"{name} contains a failed gate/control/ablation")
    ablations = {row["removed_component"]: row for row in read_csv("ablation_step39.csv")}
    expected_ablation = {
        "standardness_no_vector_condition": ("12", "True", "False"),
        "mass_completion": ("8", "False", "True"),
        "confining_subgroup": ("8", "False", "True"),
    }
    for component, (count, load_bearing, upstream) in expected_ablation.items():
        row = ablations.get(component)
        if row is None or row["survivors_without_component"] != count or row["load_bearing"] != load_bearing or row["upstream_load_bearing"] != upstream:
            fail(f"ablation row mismatch for {component}: {row}")
    self_checks = read_csv("forbidden_prior_self_check_step39.csv")
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
    print("run_step39.py: PASS (--self)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="validate only Step 39 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 39 self-checks")
    args = parser.parse_args()
    if args.chain:
        run_prior_validators()
    validate_self()


if __name__ == "__main__":
    main()
