#!/usr/bin/env python3
"""Validate Cluster A Step 38 higher-layer shadow artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "higher_layer_shadow_step38.py"

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
]

REQUIRED_FILES = [
    "higher_layer_shadow_step38.py",
    "low_energy_shadow_scores_step38.csv",
    "low_energy_outcomes_by_structure_step38.csv",
    "shadow_requirement_survivors_step38.csv",
    "shape_minimality_detectors_step38.csv",
    "predicate_summary_step38.csv",
    "negative_controls_step38.csv",
    "stage2_audit_step38.csv",
    "forbidden_prior_self_check_step38.csv",
    "ablation_step38.csv",
    "dependency_trace_step38.csv",
    "six_gate_audit_step38.csv",
    "generated_vs_input_step38.csv",
    "higher_layer_shadow_output_step38.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step38_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step38.py",
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
    r"\bsolves unification\b",
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
    print(f"run_step38.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 38 chain\n"
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
        "low_energy_shadow",
        "broken_vector_exotic_count",
        "base_stable_composite_mass_requirement",
        "clean_shadow_requirement",
        "shape_minimality_detector",
    ]:
        if required not in text:
            fail(f"build script missing required shadow component: {required}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step38.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "higher_layer_shadow_output_step38.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 38:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "SHADOW_UNIQUENESS_WITH_CONTENT_LIMIT":
            fail("expected shadow uniqueness with content limit verdict")
        if doc.get("reproduced_step35_survivors") != 12:
            fail("Step-35 survivor count was not reproduced")
        if doc.get("base_shadow_survivors") != 12:
            fail("base shadow should keep all 12")
        if doc.get("clean_shadow_survivors") != 8:
            fail("clean shadow survivor count mismatch")
        if doc.get("clean_shadow_structures") != "2|3:8":
            fail("clean shadow structure mismatch")
        if doc.get("single_factor_base_survives") is not True:
            fail("single-factor family should pass base shadow")
        if doc.get("single_factor_clean_survives") is not False:
            fail("single-factor family should fail clean shadow")
        if doc.get("target_passes") is not True or doc.get("target_distinguished") is not False:
            fail("target/reference status mismatch")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    for key in ("six_gates_pass", "forbidden_prior_self_check_pass", "stage_ii_pass", "negative_controls_pass", "shape_minimality_detector_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_computation_artifacts() -> None:
    scores = read_csv("low_energy_shadow_scores_step38.csv")
    if len(scores) != 12:
        fail("score table must contain Step-35 residual 12")
    if sum(1 for row in scores if row["base_stable_composite_mass_requirement"] == "True") != 12:
        fail("base shadow count mismatch")
    clean = [row for row in scores if row["clean_shadow_requirement"] == "True"]
    if len(clean) != 8 or any(row["dimensions"] != "2|3" for row in clean):
        fail("clean shadow survivor set mismatch")
    if not any(row["dimensions"] == "4" and row["base_stable_composite_mass_requirement"] == "True" for row in scores):
        fail("single-factor base shadow did not survive")
    if any(row["dimensions"] == "4" and row["clean_shadow_requirement"] == "True" for row in scores):
        fail("single-factor clean shadow should fail")
    if not all(int(row["broken_vector_exotic_count"]) == 6 for row in scores if row["dimensions"] == "4"):
        fail("single-factor broken-vector count mismatch")
    if not all(int(row["broken_vector_exotic_count"]) == 0 for row in scores if row["dimensions"] == "2|3"):
        fail("target-structure broken-vector count mismatch")
    outcomes = {row["dimensions"]: row for row in read_csv("low_energy_outcomes_by_structure_step38.csv")}
    if outcomes["2|3"]["clean_shadow_survivors"] != "8" or outcomes["4"]["clean_shadow_survivors"] != "0":
        fail("outcome table mismatch")
    detectors = {row["criterion"]: row for row in read_csv("shape_minimality_detectors_step38.csv")}
    if detectors["clean_shadow_requirement"]["flagged"] != "False":
        fail("clean shadow was flagged as shape/minimality")
    if detectors["step36_factor_local_breaking"]["flagged"] != "True":
        fail("factor-local diagnostic was not flagged")
    if detectors["step37_scalar_stage_currency"]["flagged"] != "True":
        fail("scalar-stage currency diagnostic was not flagged")
    summary = read_csv("predicate_summary_step38.csv")
    if len(summary) != 1 or summary[0]["verdict"] != "SHADOW_UNIQUENESS_WITH_CONTENT_LIMIT":
        fail(f"unexpected predicate summary: {summary}")


def validate_gates_controls_and_classification() -> None:
    for name, field in [
        ("negative_controls_step38.csv", "passes"),
        ("stage2_audit_step38.csv", "passes"),
        ("six_gate_audit_step38.csv", "passes"),
    ]:
        rows = read_csv(name)
        if not rows or any(row[field] != "True" for row in rows):
            fail(f"{name} contains a failed gate/control/ablation")
    ablations = {row["removed_component"]: row for row in read_csv("ablation_step38.csv")}
    expected_ablation = {
        "clean_broken_vector_exotic_condition": ("12", "True", "False"),
        "mass_completion": ("8", "False", "True"),
        "confining_subgroup_requirement": ("8", "False", "True"),
    }
    for component, (count, load_bearing, upstream) in expected_ablation.items():
        row = ablations.get(component)
        if row is None or row["survivors_without_component"] != count or row["load_bearing"] != load_bearing or row["upstream_load_bearing"] != upstream:
            fail(f"ablation row mismatch for {component}: {row}")
    self_checks = read_csv("forbidden_prior_self_check_step38.csv")
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
    print("run_step38.py: PASS (--self)")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="validate only Step 38 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 38 self-checks")
    args = parser.parse_args()
    if args.chain:
        run_prior_validators()
    validate_self()


if __name__ == "__main__":
    main()
