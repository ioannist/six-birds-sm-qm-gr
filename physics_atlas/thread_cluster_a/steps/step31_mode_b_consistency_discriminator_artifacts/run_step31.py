#!/usr/bin/env python3
"""Validate Cluster A Step 31 consistency discriminator artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_consistency_discriminator_step31.py"

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
]

REQUIRED_FILES = [
    "mode_b_consistency_discriminator_step31.py",
    "predicate_summary_step31.csv",
    "consistency_scores_step31.csv",
    "conjoined_survivors_step31.csv",
    "predicate_counts_by_structure_step31.csv",
    "reference_status_step31.csv",
    "ablation_step31.csv",
    "negative_controls_step31.csv",
    "stage2_audit_step31.csv",
    "dependency_trace_step31.csv",
    "forbidden_prior_self_check_step31.csv",
    "six_gate_audit_step31.csv",
    "generated_vs_input_step31.csv",
    "mode_b_consistency_discriminator_output_step31.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step31_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step31.py",
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
    r"strict_closure_currency_minimum\s*\(",
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
    print(f"run_step31.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 31 chain\n"
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
        "atomic_rewrite_packaging",
        "route_incidence_complete",
        "closure_consistency_completeness",
        "strict_closure_currency_minimum",
        "rank_one_global_chirality",
        "ablation",
    ]:
        if required not in text:
            fail(f"build script missing required consistency-discriminator component: {required}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step31.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "mode_b_consistency_discriminator_output_step31.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 31:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "NARROW":
            fail("expected NARROW verdict for consistency predicate")
        if doc.get("dropped_diagnostic") != "strict_closure_currency_minimum":
            fail("Step 30 currency minimum must be diagnostic only")
        if doc.get("reproduced_step29_count") != 1851:
            fail("Step 29 survivor count was not reproduced")
        if doc.get("conjoined_survivor_count") != 513:
            fail("conjoined survivor count changed unexpectedly")
        if doc.get("target_passes_step29") is not True:
            fail("target should pass Step 29 before consistency predicate")
        if doc.get("target_passes_conjunction") is not True:
            fail("target should pass consistency predicate")
        if doc.get("target_distinguished") is not False:
            fail("target must not be uniquely distinguished")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    for key in ("six_gates_pass", "forbidden_prior_self_check_pass", "stage_ii_pass", "negative_controls_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_conjunction_artifacts() -> None:
    summary = read_csv("predicate_summary_step31.csv")
    if len(summary) != 1 or summary[0]["verdict"] != "NARROW":
        fail(f"unexpected predicate summary: {summary}")
    row = summary[0]
    if row["reproduced_step29_count"] != "1851" or row["conjoined_survivors"] != "513":
        fail("predicate summary counts mismatch")
    if row["target_passes_conjunction"] != "True" or row["target_distinguished"] != "False":
        fail(f"unexpected reference outcome in summary: {row}")
    ref = read_csv("reference_status_step31.csv")
    if len(ref) != 1:
        fail("reference status must have one row")
    ref_row = ref[0]
    if ref_row["target_passes_step29"] != "True" or ref_row["target_passes_conjunction"] != "True":
        fail(f"unexpected reference status: {ref_row}")
    if ref_row["target_distinguished"] != "False" or ref_row["conjoined_survivor_count"] != "513":
        fail(f"unexpected reference status: {ref_row}")
    survivors = read_csv("conjoined_survivors_step31.csv")
    if len(survivors) != 513:
        fail("conjoined survivor table count mismatch")
    if sum(1 for row in survivors if row["is_target_reference"] == "True") != 1:
        fail("conjoined survivors must contain exactly one target/reference row")
    scores = read_csv("consistency_scores_step31.csv")
    if len(scores) != 1851:
        fail("consistency score table must contain all Step-29 survivors")
    if sum(1 for row in scores if row["is_target_reference"] == "True") != 1:
        fail("consistency scores must contain exactly one target/reference row")
    counts = read_csv("predicate_counts_by_structure_step31.csv")
    if sum(int(row["consistency_completeness_passes"]) for row in counts) != 513:
        fail("per-structure consistency count does not sum to 513")
    if sum(int(row["step29_survivors"]) for row in counts) != 1851:
        fail("per-structure Step-29 count does not sum to 1851")
    if sum(int(row["target_passes"]) for row in counts) != 1:
        fail("per-structure target pass count must be 1")


def validate_gates_and_controls() -> None:
    for name in ("negative_controls_step31.csv", "stage2_audit_step31.csv", "six_gate_audit_step31.csv"):
        rows = read_csv(name)
        if not rows or any(row["passes"] != "True" for row in rows):
            fail(f"{name} contains failing rows")
    ablations = read_csv("ablation_step31.csv")
    if len(ablations) != 2:
        fail("ablation file should contain two active components")
    expected = {"atomic_rewrite_packaging", "closure_consistency_completeness"}
    if {row["removed_component"] for row in ablations} != expected:
        fail(f"unexpected ablation components: {ablations}")
    if any(row["load_bearing"] != "True" for row in ablations):
        fail("both active components must be load-bearing")
    checks = read_csv("forbidden_prior_self_check_step31.csv")
    if not checks or any(row["passes"] != "False" for row in checks):
        fail("forbidden-prior self-check should report all forbidden reductions absent")
    if "reduces_to_minimality" not in {row["check"] for row in checks}:
        fail("forbidden-prior self-check missing reduces-to-minimality check")
    trace = read_csv("dependency_trace_step31.csv")
    primitives = {row["primitive"] for row in trace}
    if primitives != {"P5/P1/F27", "P3/P6", "P3"}:
        fail(f"dependency trace does not match declared primitives: {primitives}")
    generated = read_csv("generated_vs_input_step31.csv")
    statuses = {row["item"]: row["status"] for row in generated}
    if statuses.get("currency_minimum") != "dropped_diagnostic_only":
        fail("generated-vs-input must record currency minimum as diagnostic only")
    if statuses.get("rank_one_global_chirality") != "stage_ii_diagnostic":
        fail("rank-one global chirality must be diagnostic, not selector")


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
    if "R_cluster_a_after_step31_mode_b_consistency_discriminator" not in lineage_text:
        fail("target lineage missing Step 31 residual")


def validate_self() -> None:
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_conjunction_artifacts()
    validate_gates_and_controls()
    validate_content_classification()
    validate_mode_b_artifacts()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self", action="store_true", help="validate only Step 31 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior step validators once, then Step 31 self checks")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose only one of --self or --chain")
    if args.chain:
        run_prior_validators()
    validate_self()
    mode = "chain" if args.chain else "self"
    print(f"run_step31.py: PASS ({mode})")


if __name__ == "__main__":
    main()
