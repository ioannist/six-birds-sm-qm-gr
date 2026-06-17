#!/usr/bin/env python3
"""Validate Cluster A Step 28 neutral representation de-smuggling artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_neutral_representation_desmuggle_step28.py"

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
]

REQUIRED_FILES = [
    "mode_b_neutral_representation_desmuggle_step28.py",
    "rep_set_step28.csv",
    "neutral_structure_summary_step28.csv",
    "neutral_anomaly_free_closers_step28.csv",
    "sm_distinguished_step28.csv",
    "anti_smuggle_audit_step28.csv",
    "cubic_self_check_step28.csv",
    "stage2_calibration_step28.csv",
    "generated_vs_input_step28.csv",
    "mode_b_neutral_representation_desmuggle_output_step28.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step28_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step28.py",
]

BUILD_FORBIDDEN_SNIPPETS = [
    "total_slots",
    "FIVE",
    "== 5",
    "!= 5",
    "==5",
    "!=5",
    "total_slots -",
    "SU(5)",
    "SO(10)",
    "SU(3)xSU(2)xU(1)",
    "2|3",
    "3|-2",
    "10+5bar",
    "co-sourcing",
    "common-refinement-as-QMGR-cosourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi",
    "ψ",
]

BUILD_FORBIDDEN_PATTERNS = [
    r"return\s+None",
    r"slot[_-]?count\s*[-+]",
    r"cubic[^=\n]*=\s*[^#\n]*slot",
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
REQUIRED_REPS = {"singlet", "fund", "antifund", "antisym2", "sym2", "adjoint"}


def fail(message: str) -> None:
    print(f"run_step28.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 28 chain\n"
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
            fail(f"build script appears to contain a slot-count or noncomputed shortcut: {pattern}")
    for required in [
        "REP_NAMES",
        "cubic_a",
        "dynkin_twice",
        "vectorlike_only",
        "cubic_recomputed_from_A_R",
        "uses_slot_count_formula",
        "reference_support_key",
    ]:
        if required not in text:
            fail(f"build script is missing required computation component: {required}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step28.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_rep_set() -> None:
    rows = read_csv("rep_set_step28.csv")
    reps = {row["rep"] for row in rows}
    if not REQUIRED_REPS.issubset(reps):
        fail(f"neutral rep set missing entries: {REQUIRED_REPS - reps}")
    if {"fund", "antifund", "antisym2"} == reps:
        fail("representation set is exterior-only")
    for row in rows:
        if row["rep"] == "sym2" and row["cubic_A"] == "0":
            fail("symmetric representation cubic coefficient was not computed")


def validate_schema_and_counts() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "mode_b_neutral_representation_desmuggle_output_step28.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 28:
            fail("schema/output step mismatch")
        if doc.get("verdict") != "CONFIRM_SMUGGLE":
            fail("expected CONFIRM_SMUGGLE verdict in this computed neutral window")
        if doc.get("typed_no_go") is not True:
            fail("CONFIRM_SMUGGLE must be typed_no_go=true")
        if doc.get("reference_present") is not True:
            fail("Stage II reference support calibration is absent")
        if doc.get("reference_distinguished_without_prior") is not False:
            fail("reference support was incorrectly marked distinguished")
        if doc.get("neutral_anomaly_free_closer_count", 0) <= 1:
            fail("neutral window does not contain genuine competing anomaly-free closers")
        for key in ("new_physics_claim", "root_landed", "frame_transfer_certified"):
            if doc.get(key):
                fail(f"schema/output overstates status: {key}")
    if schema.get("neutral_anomaly_free_closer_count") != output.get("neutral_anomaly_free_closer_count"):
        fail("schema/output closer count mismatch")
    if schema.get("anti_smuggle_gates_pass") is not True or schema.get("stage_ii_pass") is not True:
        fail("schema anti-smuggle or Stage II status failed")


def validate_audits() -> None:
    anti_rows = read_csv("anti_smuggle_audit_step28.csv")
    if not anti_rows or any(row["passes"] != "True" for row in anti_rows):
        fail("anti-smuggle audit has a failing row")
    cubic_rows = read_csv("cubic_self_check_step28.csv")
    if not cubic_rows:
        fail("missing cubic self-check rows")
    for row in cubic_rows:
        if row["uses_slot_count_formula"] != "False" or row["passes"] != "True":
            fail(f"cubic self-check failed: {row}")
    stage_rows = read_csv("stage2_calibration_step28.csv")
    if len(stage_rows) != 1 or stage_rows[0]["passes"] != "True" or stage_rows[0]["matching_dimensions"] == "none":
        fail("Stage II reference-support calibration failed")
    status_rows = read_csv("sm_distinguished_step28.csv")
    if len(status_rows) != 1:
        fail("reference status must have one row")
    row = status_rows[0]
    if row["reference_present"] != "True" or row["distinguished_without_prior"] != "False" or row["verdict"] != "CONFIRM_SMUGGLE":
        fail(f"unexpected reference status row: {row}")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
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
    text = (ARTIFACT_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_cluster_a_after_step28_mode_b_neutral_representation_desmuggle" not in text:
        fail("target lineage missing Step 28 residual")


def validate_self() -> None:
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_rep_set()
    validate_schema_and_counts()
    validate_audits()
    validate_content_classification()
    validate_mode_b_artifacts()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self", action="store_true", help="validate only Step 28 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior step validators once, then Step 28 self checks")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose only one of --self or --chain")
    if args.chain:
        run_prior_validators()
    validate_self()
    mode = "chain" if args.chain else "self"
    print(f"run_step28.py: PASS ({mode})")


if __name__ == "__main__":
    main()
