#!/usr/bin/env python3
"""Validate Cluster A Step 29 neutral intrinsic discriminator artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_neutral_intrinsic_discriminator_step29.py"

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
]

REQUIRED_FILES = [
    "mode_b_neutral_intrinsic_discriminator_step29.py",
    "predicate_summary_step29.csv",
    "predicate_counts_by_structure_step29.csv",
    "predicate_survivors_step29.csv",
    "reference_status_step29.csv",
    "negative_controls_step29.csv",
    "stage2_audit_step29.csv",
    "dependency_trace_step29.csv",
    "ablation_step29.csv",
    "forbidden_prior_self_check_step29.csv",
    "six_gate_audit_step29.csv",
    "generated_vs_input_step29.csv",
    "mode_b_neutral_intrinsic_discriminator_output_step29.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step29_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step29.py",
]

BUILD_FORBIDDEN_SNIPPETS = [
    "total_slots",
    "FIVE",
    "== 5",
    "!= 5",
    "==5",
    "!=5",
    "SU(5)",
    "SO(10)",
    "10+5bar",
    "2|3",
    "3|-2",
    "F51",
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
    print(f"run_step29.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 29 chain\n"
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
        "atomic_package",
        "no_spectator_action",
        "primitive_charge_orbit",
        "closed_chiral",
        "reference_support_key",
        "ablation",
    ]:
        if required not in text:
            fail(f"build script missing required intrinsic predicate component: {required}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step29.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "mode_b_neutral_intrinsic_discriminator_output_step29.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 29:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "NARROW":
            fail("expected NARROW verdict for computed Step 29 predicate")
        if doc.get("p2_closer_count") != 280983:
            fail("P2 closer count must match Step 28 carrier")
        if doc.get("predicate_survivor_count") != 1851:
            fail("predicate survivor count changed unexpectedly")
        if doc.get("target_passes_predicate") is not True:
            fail("target reference must pass the predicate")
        if doc.get("target_distinguished") is not False:
            fail("target reference must not be marked uniquely distinguished")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    for key in ("six_gates_pass", "forbidden_prior_self_check_pass", "stage_ii_pass", "negative_controls_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_predicate_artifacts() -> None:
    summary = read_csv("predicate_summary_step29.csv")
    if len(summary) != 1 or summary[0]["verdict"] != "NARROW" or summary[0]["survivors"] != "1851":
        fail(f"unexpected predicate summary: {summary}")
    ref = read_csv("reference_status_step29.csv")
    if len(ref) != 1:
        fail("reference status must have one row")
    ref_row = ref[0]
    if ref_row["target_passes_predicate"] != "True" or ref_row["target_distinguished"] != "False":
        fail(f"unexpected reference status: {ref_row}")
    survivors = read_csv("predicate_survivors_step29.csv")
    if len(survivors) != 1851:
        fail("predicate survivor table count mismatch")
    if sum(1 for row in survivors if row["is_target_reference"] == "True") != 1:
        fail("target reference survivor count must be exactly one")
    counts = read_csv("predicate_counts_by_structure_step29.csv")
    total = sum(int(row["intrinsic_predicate_passes"]) for row in counts)
    if total != 1851:
        fail("per-structure survivor counts do not sum to 1851")


def validate_gates_and_controls() -> None:
    for name in ("negative_controls_step29.csv", "stage2_audit_step29.csv", "six_gate_audit_step29.csv"):
        rows = read_csv(name)
        if not rows or any(row["passes"] != "True" for row in rows):
            fail(f"{name} contains failing rows")
    ablations = read_csv("ablation_step29.csv")
    if len(ablations) != 3 or any(row["load_bearing"] != "True" for row in ablations):
        fail("ablation rows must all be load-bearing")
    checks = read_csv("forbidden_prior_self_check_step29.csv")
    if not checks or any(row["passes"] != "False" for row in checks):
        fail("forbidden-prior self-check should report all forbidden reductions absent")
    trace = read_csv("dependency_trace_step29.csv")
    primitives = {row["primitive"] for row in trace}
    if primitives != {"P5", "P1", "F27"}:
        fail(f"dependency trace does not match declared primitives: {primitives}")


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
    if "non_triviality_argument" not in grammar_text or "excluded_designs_rationale" not in grammar_text:
        fail("grammar manifest missing required Step 29 fields")
    lineage_text = (ARTIFACT_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_cluster_a_after_step29_mode_b_neutral_intrinsic_discriminator" not in lineage_text:
        fail("target lineage missing Step 29 residual")


def validate_self() -> None:
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_predicate_artifacts()
    validate_gates_and_controls()
    validate_content_classification()
    validate_mode_b_artifacts()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self", action="store_true", help="validate only Step 29 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior step validators once, then Step 29 self checks")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose only one of --self or --chain")
    if args.chain:
        run_prior_validators()
    validate_self()
    mode = "chain" if args.chain else "self"
    print(f"run_step29.py: PASS ({mode})")


if __name__ == "__main__":
    main()
