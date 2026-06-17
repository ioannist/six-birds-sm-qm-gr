#!/usr/bin/env python3
"""Validate Cluster A Step 33 corrected anomaly/chirality artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "corrected_anomaly_chirality_step33.py"

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
]

REQUIRED_FILES = [
    "corrected_anomaly_chirality_step33.py",
    "corrected_structure_summary_step33.csv",
    "corrected_trajectory_step33.csv",
    "corrected_chirality_scores_step33.csv",
    "corrected_final_survivors_step33.csv",
    "corrected_counts_by_structure_step33.csv",
    "dominance_step33.csv",
    "predicate_summary_step33.csv",
    "correctness_self_check_step33.csv",
    "forbidden_prior_self_check_step33.csv",
    "negative_controls_step33.csv",
    "stage2_audit_step33.csv",
    "ablation_step33.csv",
    "dependency_trace_step33.csv",
    "six_gate_audit_step33.csv",
    "generated_vs_input_step33.csv",
    "corrected_anomaly_chirality_output_step33.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step33_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step33.py",
]

BUILD_FORBIDDEN_SNIPPETS = [
    "total_slots",
    "FIVE",
    "SU(5)",
    "SO(10)",
    "10+5bar",
    "3|-2",
    "3 colors",
    "2 weak",
    "common-refinement",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi",
    "ψ",
]

BUILD_FORBIDDEN_PATTERNS = [
    r"\bembed(?:s|ding|ded)?\b",
    r"\bparent\s+group\b",
    r"\btarget_shape\b",
    r"\btarget_content\b",
    r"\bis_target\s*=\s*True\b",
    r"==\s*5\b",
    r"!=\s*5\b",
    r"\bminimum_currency\b",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bderives the SM\b",
    r"\bsolves E019\b",
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
    print(f"run_step33.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 33 chain\n"
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
            fail(f"build script contains forbidden prior/construction snippet: {snippet}")
    for pattern in BUILD_FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            fail(f"build script appears to contain a forbidden prior pattern: {pattern}")
    for required in [
        "cubic_a_corrected",
        "rep_is_self_conjugate",
        "witten_vector",
        "vectorlike_only_corrected",
        "chirality_faithfulness",
        "old_step32_dominant",
    ]:
        if required not in text:
            fail(f"build script missing required corrected component: {required}")
    if "cubic_a_corrected(name: str, dimension: int)" not in text:
        fail("corrected cubic function missing")
    if "dimension == TWO" not in text:
        fail("rank-one cubic correction is not explicit")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step33.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "corrected_anomaly_chirality_output_step33.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 33:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "NARROW":
            fail("expected NARROW verdict for corrected Step 33")
        if doc.get("old_carrier_count") != 280983:
            fail("old carrier count mismatch")
        if doc.get("corrected_carrier_count") != 11990:
            fail("corrected carrier count mismatch")
        if doc.get("atomic_rewrite_packaging_count") != 156:
            fail("corrected atomic count mismatch")
        if doc.get("closure_consistency_count") != 130:
            fail("corrected consistency count mismatch")
        if doc.get("corrected_chirality_count") != 80:
            fail("corrected chirality count mismatch")
        if doc.get("target_passes_final") is not True:
            fail("target should pass corrected final predicate")
        if doc.get("target_distinguished") is not False:
            fail("target must not be uniquely distinguished")
        if doc.get("old_dominance_broken") is not True:
            fail("old Step-32 dominance should be broken by the corrected computation")
        if doc.get("target_structure_is_post_dominant") is not False:
            fail("target structure should not be final dominant")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    for key in ("correctness_self_check_pass", "six_gates_pass", "forbidden_prior_self_check_pass", "stage_ii_pass", "negative_controls_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_corrected_counts() -> None:
    trajectory = read_csv("corrected_trajectory_step33.csv")
    expected = {
        "corrected_neutral_carrier": ("11990", "True"),
        "atomic_rewrite_packaging": ("156", "True"),
        "closure_consistency_completeness": ("130", "True"),
        "corrected_chirality_faithfulness": ("80", "True"),
    }
    for row in trajectory:
        if row["stage"] in expected and (row["survivor_count"], row["target_passes"]) != expected[row["stage"]]:
            fail(f"trajectory mismatch: {row}")
    if set(expected) != {row["stage"] for row in trajectory}:
        fail("trajectory stages mismatch")
    counts = read_csv("corrected_counts_by_structure_step33.csv")
    if sum(int(row["corrected_carrier"]) for row in counts) != 11990:
        fail("corrected carrier per-structure sum mismatch")
    if sum(int(row["atomic_rewrite_packaging"]) for row in counts) != 156:
        fail("atomic per-structure sum mismatch")
    if sum(int(row["consistency_completeness"]) for row in counts) != 130:
        fail("consistency per-structure sum mismatch")
    if sum(int(row["chirality_faithful_final"]) for row in counts) != 80:
        fail("final per-structure sum mismatch")
    keyed = {row["dimensions"]: row for row in counts}
    if keyed.get("2|2", {}).get("chirality_faithful_final") != "0":
        fail("old dominant 2|2 should be eliminated in corrected final pool")
    if keyed.get("2|3", {}).get("chirality_faithful_final") != "15":
        fail("target-structure final count mismatch")
    if keyed.get("3", {}).get("chirality_faithful_final") != "49":
        fail("final dominant count mismatch")
    dominance = read_csv("dominance_step33.csv")
    if len(dominance) != 1:
        fail("dominance table must have one row")
    dom = dominance[0]
    if dom["old_step32_dominant_dimensions"] != "2|2" or dom["old_dominant_corrected_final_count"] != "0":
        fail(f"old dominance break not recorded correctly: {dom}")
    if dom["post_chirality_dominant_dimensions"] != "3" or dom["post_chirality_dominant_count"] != "49":
        fail(f"corrected final dominance mismatch: {dom}")
    if dom["old_dominance_broken"] != "True" or dom["target_structure_is_post_dominant"] != "False":
        fail(f"dominance verdict mismatch: {dom}")
    final_rows = read_csv("corrected_final_survivors_step33.csv")
    if len(final_rows) != 80:
        fail("corrected final survivor count mismatch")
    if sum(1 for row in final_rows if row["is_target_reference"] == "True") != 1:
        fail("corrected final survivors must contain exactly one target/reference row")
    score_rows = read_csv("corrected_chirality_scores_step33.csv")
    if len(score_rows) != 130:
        fail("corrected chirality score table must contain all corrected consistency survivors")


def validate_gates_and_controls() -> None:
    for name in ("correctness_self_check_step33.csv", "negative_controls_step33.csv", "stage2_audit_step33.csv", "six_gate_audit_step33.csv"):
        rows = read_csv(name)
        if not rows or any(row["passes"] != "True" for row in rows):
            fail(f"{name} contains failing rows")
    ablations = read_csv("ablation_step33.csv")
    if len(ablations) != 3:
        fail("ablation file should contain three active components")
    expected = {"atomic_rewrite_packaging", "closure_consistency_completeness", "corrected_chirality_faithfulness"}
    if {row["removed_component"] for row in ablations} != expected:
        fail(f"unexpected ablation components: {ablations}")
    if any(row["load_bearing"] != "True" for row in ablations):
        fail("all active components must be load-bearing")
    checks = read_csv("forbidden_prior_self_check_step33.csv")
    if not checks or any(row["passes"] != "False" for row in checks):
        fail("forbidden-prior self-check should report all forbidden reductions absent")
    required_checks = {"reduces_to_minimality", "reduces_to_shape", "uses_target_reference"}
    if not required_checks.issubset({row["check"] for row in checks}):
        fail("forbidden-prior self-check missing required reductions")
    trace = read_csv("dependency_trace_step33.csv")
    primitives = {row["primitive"] for row in trace}
    if primitives != {"P2", "P5/P1/F27", "P3/P6", "P3"}:
        fail(f"dependency trace does not match declared primitives: {primitives}")
    generated = read_csv("generated_vs_input_step33.csv")
    statuses = {row["item"]: row["status"] for row in generated}
    if statuses.get("su2_cubic_proxy_bug") != "corrected":
        fail("generated-vs-input must record the corrected cubic bug")
    if statuses.get("corrected_trajectory") != "computed":
        fail("generated-vs-input must record corrected trajectory")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content classification is empty")
    for row in rows:
        grade = row["grade"]
        if grade not in ALLOWED_GRADES:
            fail(f"invalid grade in content classification: {grade}")
        source = row["source_path"]
        if source.startswith("/") or source.startswith("physics_atlas/"):
            fail(f"source path is not thread-root-relative: {source}")
        if not (THREAD_DIR / source).exists():
            fail(f"classified source does not exist: {source}")


def validate_mode_b_artifacts() -> None:
    for name in ("mode_b_constraint_ledger.csv", "mode_b_grammar_manifest.csv", "mode_b_target_lineage.csv"):
        rows = read_csv(name)
        if not rows:
            fail(f"{name} is empty")
    grammar_text = (ARTIFACT_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    for field in ("non_triviality_argument", "excluded_designs_rationale", "constraint_transfer"):
        if field not in grammar_text:
            fail(f"grammar manifest missing required field: {field}")
    lineage_text = (ARTIFACT_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_cluster_a_after_step33_mode_b_corrected_anomaly_chirality" not in lineage_text:
        fail("target lineage missing Step 33 residual")


def validate_self() -> None:
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_corrected_counts()
    validate_gates_and_controls()
    validate_content_classification()
    validate_mode_b_artifacts()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self", action="store_true", help="validate only Step 33 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior step validators once, then Step 33 self checks")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose only one of --self or --chain")
    if args.chain:
        run_prior_validators()
    validate_self()
    mode = "chain" if args.chain else "self"
    print(f"run_step33.py: PASS ({mode})")


if __name__ == "__main__":
    main()
