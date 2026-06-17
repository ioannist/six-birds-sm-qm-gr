#!/usr/bin/env python3
"""Validate Cluster A Step 34 F24 role-obstruction artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "role_obstruction_discriminator_step34.py"

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
]

REQUIRED_FILES = [
    "role_obstruction_discriminator_step34.py",
    "role_obstruction_scores_step34.csv",
    "role_obstruction_distribution_step34.csv",
    "f24_descending_survivors_step34.csv",
    "f24_counts_by_structure_step34.csv",
    "predicate_summary_step34.csv",
    "type_limit_assessment_step34.csv",
    "negative_controls_step34.csv",
    "stage2_audit_step34.csv",
    "forbidden_prior_self_check_step34.csv",
    "ablation_step34.csv",
    "dependency_trace_step34.csv",
    "six_gate_audit_step34.csv",
    "generated_vs_input_step34.csv",
    "role_obstruction_discriminator_output_step34.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step34_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step34.py",
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
    print(f"run_step34.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 34 chain\n"
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
            fail(f"build script appears to contain a forbidden prior/tuning pattern: {pattern}")
    for required in [
        "role_obstruction",
        "access_key",
        "role_readout",
        "f24_descends",
        "type_limit_assessment",
        "target_obstruction",
    ]:
        if required not in text:
            fail(f"build script missing required F24 component: {required}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step34.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "role_obstruction_discriminator_output_step34.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 34:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "TYPED_NO_GO_TYPE_LIMIT":
            fail("expected typed no-go/type-limit verdict")
        if doc.get("reproduced_corrected_carrier") != 80:
            fail("corrected carrier count was not reproduced")
        if doc.get("f24_descending_survivors") != 10:
            fail("F24-descending survivor count mismatch")
        if doc.get("target_obstruction") != 1:
            fail("target obstruction mismatch")
        if doc.get("target_passes_f24") is not False:
            fail("target should fail principled O_s=0 predicate")
        if doc.get("target_distinguished") is not False:
            fail("target must not be uniquely distinguished")
        if doc.get("type_limit_assessment") is not True:
            fail("type-limit assessment must be true")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    for key in ("six_gates_pass", "forbidden_prior_self_check_pass", "stage_ii_pass", "negative_controls_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_f24_artifacts() -> None:
    scores = read_csv("role_obstruction_scores_step34.csv")
    if len(scores) != 80:
        fail("role obstruction score table must contain corrected 80")
    target_rows = [row for row in scores if row["is_target_reference"] == "True"]
    if len(target_rows) != 1 or target_rows[0]["role_obstruction_pairs"] != "1":
        fail("target obstruction row missing or incorrect")
    distribution = read_csv("role_obstruction_distribution_step34.csv")
    expected_distribution = {"0": "10", "1": "34", "2": "36"}
    if {row["role_obstruction_pairs"]: row["survivor_count"] for row in distribution} != expected_distribution:
        fail(f"unexpected O_s distribution: {distribution}")
    if [row for row in distribution if row["target_has_this_obstruction"] == "True"][0]["role_obstruction_pairs"] != "1":
        fail("target obstruction distribution flag mismatch")
    f24 = read_csv("f24_descending_survivors_step34.csv")
    if len(f24) != 10:
        fail("F24 survivor table count mismatch")
    if any(row["is_target_reference"] == "True" for row in f24):
        fail("target must not be in O_s=0 survivor set")
    counts = read_csv("f24_counts_by_structure_step34.csv")
    if sum(int(row["corrected_final_carrier"]) for row in counts) != 80:
        fail("carrier count by structure mismatch")
    if sum(int(row["f24_descending_survivors"]) for row in counts) != 10:
        fail("F24 count by structure mismatch")
    keyed = {row["dimensions"]: row for row in counts}
    if keyed.get("2|3", {}).get("f24_descending_survivors") != "6":
        fail("target-structure F24 count mismatch")
    if keyed.get("4", {}).get("f24_descending_survivors") != "4":
        fail("rank-two F24 count mismatch")
    summary = read_csv("predicate_summary_step34.csv")
    if len(summary) != 1 or summary[0]["verdict"] != "TYPED_NO_GO_TYPE_LIMIT":
        fail(f"unexpected predicate summary: {summary}")
    type_limit = read_csv("type_limit_assessment_step34.csv")
    if len(type_limit) != 1 or type_limit[0]["target_requires_next_kind"] != "True":
        fail("type-limit assessment row missing or incorrect")


def validate_gates_and_controls() -> None:
    for name in ("negative_controls_step34.csv", "stage2_audit_step34.csv", "six_gate_audit_step34.csv"):
        rows = read_csv(name)
        if not rows or any(row["passes"] != "True" for row in rows):
            fail(f"{name} contains failing rows")
    ablations = read_csv("ablation_step34.csv")
    if len(ablations) != 2:
        fail("ablation file should contain two rows")
    if any(row["load_bearing"] != "True" for row in ablations):
        fail("F24 ablations must be load-bearing")
    checks = read_csv("forbidden_prior_self_check_step34.csv")
    if not checks or any(row["passes"] != "False" for row in checks):
        fail("forbidden-prior self-check should report all forbidden reductions absent")
    required_checks = {"reduces_to_minimality", "reduces_to_shape", "reduces_to_tuning", "uses_target_reference"}
    if not required_checks.issubset({row["check"] for row in checks}):
        fail("forbidden-prior self-check missing required reductions")
    trace = read_csv("dependency_trace_step34.csv")
    primitives = {row["primitive"] for row in trace}
    if primitives != {"P2/P5/P1/F27/P3/P6", "F24"}:
        fail(f"dependency trace does not match declared primitives: {primitives}")
    generated = read_csv("generated_vs_input_step34.csv")
    statuses = {row["item"]: row["status"] for row in generated}
    if statuses.get("role_obstruction_definition") != "declared_mode_b_input":
        fail("generated-vs-input missing role obstruction definition")
    if statuses.get("target_obstruction") != "computed":
        fail("target obstruction must be computed")


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
    if "R_cluster_a_after_step34_mode_b_role_obstruction_discriminator" not in lineage_text:
        fail("target lineage missing Step 34 residual")


def validate_self() -> None:
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_f24_artifacts()
    validate_gates_and_controls()
    validate_content_classification()
    validate_mode_b_artifacts()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self", action="store_true", help="validate only Step 34 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior step validators once, then Step 34 self checks")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose only one of --self or --chain")
    if args.chain:
        run_prior_validators()
    validate_self()
    mode = "chain" if args.chain else "self"
    print(f"run_step34.py: PASS ({mode})")


if __name__ == "__main__":
    main()
