#!/usr/bin/env python3
"""Validate Cluster A Step 27 normalization robustness artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "mode_b_normalization_robustness_step27.py"

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
]

REQUIRED_FILES = [
    "mode_b_normalization_robustness_step27.py",
    "normalization_conventions_step27.csv",
    "negative_controls_step27.csv",
    "residual_smuggle_hunt_step27.csv",
    "consequence_consistency_step27.csv",
    "stage2_reproduction_step27.csv",
    "dependency_trace_step27.csv",
    "ablation_step27.csv",
    "generated_vs_input_step27.csv",
    "six_gate_audit_step27.csv",
    "mode_b_normalization_robustness_output_step27.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step27_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step27.py",
]

BUILD_FORBIDDEN_SNIPPETS = [
    "3/8",
    "0.375",
    "2|3",
    "3|-2",
    "r1|2",
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
    r"factor_count\s*(?:==|!=)\s*\d",
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
    print(f"run_step27.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 27 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_guards() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for required in [
        "minimal_closures_step23.csv",
        "sector_enumeration_step23.csv",
        "generated_normalization_step21.csv",
        "f51_descent_step25.csv",
    ]:
        if required not in text:
            fail(f"build script does not read required prior artifact: {required}")
    for snippet in BUILD_FORBIDDEN_SNIPPETS:
        if snippet in text:
            fail(f"build script contains forbidden primitive/construction snippet: {snippet}")
    for pattern in BUILD_FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            fail(f"build script appears to contain a forcing shortcut: {pattern}")
    if "first_non_rank_one" not in text or "all_factors" not in text or "total_slots" not in text:
        fail("convention family does not include the required can-fail alternatives")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step27.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim or construction term found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "mode_b_normalization_robustness_output_step27.json").read_text(encoding="utf-8"))
    if schema.get("step") != 27 or output.get("step") != 27:
        fail("schema/output step mismatch")
    if schema.get("verdict") != "FRAGILE_CONVENTION_DEPENDENT" or output.get("verdict") != "FRAGILE_CONVENTION_DEPENDENT":
        fail("expected FRAGILE_CONVENTION_DEPENDENT verdict")
    if schema.get("typed_no_go") is not True or output.get("typed_no_go") is not True:
        fail("fragile convention-dependent result must be typed no-go for the normalization claim")
    for doc in (schema, output):
        if doc.get("new_physics_claim") or doc.get("root_landed") or doc.get("frame_transfer_certified"):
            fail("schema/output overstates status")
    if schema.get("convention_count") != 6 or schema.get("matching_conventions") != 2 or schema.get("flipping_conventions") != 4:
        fail(f"convention count mismatch: {schema}")
    if schema.get("natural_flip_count") != 1:
        fail("expected exactly one natural convention flip")
    for key in ("negative_controls_pass", "convention_can_fail", "consequence_consistency", "stage_ii_pass", "six_gates_pass"):
        if schema.get(key) is not True:
            fail(f"schema expected {key}=true")


def validate_conventions() -> None:
    rows = {row["convention_id"]: row for row in read_csv("normalization_conventions_step27.csv")}
    expected = {
        "product_charge__rank_one_t3": ("3/8", "True"),
        "lattice_lcm_charge__rank_one_t3": ("3/8", "True"),
        "total_slots_charge__rank_one_t3": ("5/17", "False"),
        "integer_weight_charge__rank_one_t3": ("1/61", "False"),
        "product_charge__alternate_t3": ("9/19", "False"),
        "product_charge__all_factor_t3": ("3/5", "False"),
    }
    if set(rows) != set(expected):
        fail(f"convention set mismatch: {set(rows)}")
    for convention_id, (sin2, matches) in expected.items():
        row = rows[convention_id]
        if row["sin2_theta_w"] != sin2 or row["matches_step21_target"] != matches or row["status"] != "COMPUTED":
            fail(f"convention row mismatch: {row}")


def validate_controls_and_consequences() -> None:
    controls = read_csv("negative_controls_step27.csv")
    if len(controls) < 12:
        fail("negative controls too sparse")
    if any(row["control_passes"] != "True" for row in controls):
        fail(f"negative control reproduced target: {controls}")
    if not any(row["status"] == "COMPUTED" for row in controls):
        fail("controls lack a computed non-target row")
    if not any(row["status"] == "FAILED" for row in controls):
        fail("controls lack a failed-readout row")
    smuggle = {row["choice"]: row for row in read_csv("residual_smuggle_hunt_step27.csv")}
    if smuggle["charge_unit_denominator"]["load_bearing"] != "True":
        fail("charge-unit smuggle hunt should be load-bearing")
    if smuggle["rank_one_readout_selection"]["load_bearing"] != "True":
        fail("readout smuggle hunt should be load-bearing")
    if smuggle["hidden_forcing_scan"]["load_bearing"] != "False":
        fail("hidden forcing scan should not be load-bearing")
    consequences = read_csv("consequence_consistency_step27.csv")
    if len(consequences) != 2 or any(row["consistent"] != "True" for row in consequences):
        fail(f"consequence consistency failed: {consequences}")
    pairs = {(row["parent_id"], row["charged_obstruction"], row["full_obstruction"]) for row in consequences}
    if ("SU(5)", "0", "0") not in pairs or ("SO(10)", "0", "1") not in pairs:
        fail(f"unexpected F51 consequence rows: {pairs}")


def validate_gates_and_stage2() -> None:
    gates = {row["gate"]: row for row in read_csv("six_gate_audit_step27.csv")}
    expected = {
        "primitive_exclusion",
        "convention_can_fail",
        "negative_controls",
        "consequence_consistency",
        "stage_ii_earning",
        "no_single_axiom_equivalence",
    }
    if set(gates) != expected:
        fail(f"gate set mismatch: {set(gates)}")
    if any(row["passes"] != "True" for row in gates.values()):
        fail(f"gate failure: {gates}")
    stage = read_csv("stage2_reproduction_step27.csv")
    if len(stage) != 1 or stage[0]["passes"] != "True" or stage[0]["all_integer_weights"] != "True":
        fail(f"Stage II mismatch: {stage}")
    ablations = read_csv("ablation_step27.csv")
    if len(ablations) != 4 or any(row["robustness_supported"] != "False" for row in ablations):
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
        "Deflationary truth first",
        "`FRAGILE_CONVENTION_DEPENDENT`",
        "total-slot normalization flips it to `5/17`",
        "F51 parent-shadow consequences remain on the same generated structure",
        "physical chiral-multiplet trace",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for snippet in ["does not claim", "toy sector trace", "frame-transfer status upgrade"]:
        if snippet not in boundary:
            fail(f"nonclaim boundary missing snippet: {snippet}")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_conventions()
    validate_controls_and_consequences()
    validate_gates_and_stage2()
    validate_content_classification()
    validate_summary_text()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 27 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 27 artifacts (default)")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 27 self checks")
    args = parser.parse_args()
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step27.py: PASS")


if __name__ == "__main__":
    main()
