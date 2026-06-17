#!/usr/bin/env python3
"""Validate Cluster A Step 41 factorization-defect clean-separation artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "factorization_defect_clean_separation_step41.py"

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
    STEPS_DIR / "step39_mode_b_clean_separation_derivation_artifacts" / "run_step39.py",
]

REQUIRED_FILES = [
    "factorization_defect_clean_separation_step41.py",
    "boson_quotients_step41.csv",
    "delta_fact_pairs_step41.csv",
    "delta_fact_witnesses_step41.csv",
    "delta_fact_summary_step41.csv",
    "delta_fact_by_structure_step41.csv",
    "faithfulness_crosscheck_step41.csv",
    "negative_controls_step41.csv",
    "stage2_audit_step41.csv",
    "six_gate_audit_step41.csv",
    "generated_vs_input_step41.csv",
    "factorization_defect_output_step41.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step41_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step41.py",
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

OVERCLAIM_PATTERNS = [
    r"\bderive[sd]?\s+clean[- ]separation\b",
    r"\bfundamental\b",
    r"\bforced by\b",
    r"\bfollows from SBT primitives\b",
    r"\btheorem that the SM is selected\b",
    r"\bthe SM is selected\b",
    r"\bnew physics claim\b",
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

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step41.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 41 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_guards() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    logic_region = text.split("def write_docs", maxsplit=1)[0]
    for snippet in BUILD_FORBIDDEN_SNIPPETS:
        if snippet in logic_region:
            fail(f"build logic contains forbidden primitive or construction snippet: {snippet}")
    for snippet in ["2|3", "target_shape", "target_content"]:
        if snippet in logic_region:
            fail(f"build logic contains forbidden target-shape snippet: {snippet}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step41.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "factorization_defect_output_step41.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 41:
            fail("schema/output step mismatch")
        if doc.get("new_physics_claim") or doc.get("frame_transfer_certified"):
            fail("schema/output overstates physical status")
    if output.get("pi0") != "pi_conf_interference" or output.get("pi1") != "pi_mass":
        fail("faithful quotient pair mismatch")
    if output.get("reproduced_step38_supports") != 12:
        fail("Step-38 support count was not reproduced")
    if output.get("delta_empty_count") != 8 or output.get("delta_nonempty_count") != 4:
        fail("Delta empty/nonempty counts mismatch")
    if output.get("faithfulness_pass") is not True or schema.get("faithfulness_pass") is not True:
        fail("faithfulness gate did not pass")
    if output.get("recognition_source") is not True or schema.get("recognition_source") is not True:
        fail("recognition-source boundary missing")


def validate_delta_tables() -> None:
    rows = read_csv("delta_fact_summary_step41.csv")
    if len(rows) != 12:
        fail(f"expected 12 summary rows, got {len(rows)}")
    for row in rows:
        clean = row["step38_clean_shadow"] == "True"
        delta_empty = row["delta_empty"] == "True"
        if clean != delta_empty:
            fail(f"Delta emptiness disagrees with Step-38 clean verdict: {row}")
        if int(row["delta_witness_count"]) != int(row["broken_vector_exotic_count"]):
            fail(f"witness count does not track exotic count: {row}")
        if row["faithful_to_step38"] != "True":
            fail(f"faithfulness row failed: {row}")
    by_structure = {row["dimensions"]: row for row in read_csv("delta_fact_by_structure_step41.csv")}
    if by_structure.get("2|3", {}).get("delta_empty_count") != "8":
        fail(f"2|3 structure should have 8 empty defects: {by_structure.get('2|3')}")
    if by_structure.get("4", {}).get("delta_nonempty_count") != "4":
        fail(f"single-factor structure should have 4 nonempty defects: {by_structure.get('4')}")
    if by_structure.get("4", {}).get("typical_witness_count") != "6":
        fail(f"single-factor structure should have 6 witnesses per support: {by_structure.get('4')}")
    witnesses = read_csv("delta_fact_witnesses_step41.csv")
    if len(witnesses) != 24:
        fail(f"expected 24 witness rows, got {len(witnesses)}")
    if any(row["witness_kind"] != "confining_charged_massive_vector" for row in witnesses):
        fail("unexpected witness kind")


def validate_gates_and_controls() -> None:
    faith = read_csv("faithfulness_crosscheck_step41.csv")
    if len(faith) != 3 or any(row["passes"] != "True" for row in faith):
        fail(f"faithfulness crosscheck failed: {faith}")
    controls = read_csv("negative_controls_step41.csv")
    if len(controls) != 2 or any(row["passes"] != "True" for row in controls):
        fail(f"negative controls failed: {controls}")
    stage = read_csv("stage2_audit_step41.csv")
    if len(stage) != 2 or any(row["passes"] != "True" for row in stage):
        fail(f"Stage II audit failed: {stage}")
    gates = {row["gate"]: row for row in read_csv("six_gate_audit_step41.csv")}
    expected = {
        "primitive_exclusion",
        "faithfulness",
        "negative_controls",
        "stage_ii",
        "recognition_source_boundary",
        "no_unconditional_physics_claim",
    }
    if set(gates) != expected:
        fail(f"gate set mismatch: {set(gates)}")
    for gate, row in gates.items():
        if row["passes"] != "True":
            fail(f"gate failed: {gate}")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"claim lacks source artifacts: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"source path must be thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact missing: {source}")


def validate_required_prose() -> None:
    summary = (ARTIFACT_DIR / "results_summary.md").read_text(encoding="utf-8")
    for snippet in [
        "This step is a RESTATEMENT",
        "recognition-source closure condition",
        "`pi0 = pi_conf_interference`",
        "`pi1 = pi_mass`",
        "`RECOGNITION_SOURCE_RESTATEMENT`",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    statement = (ARTIFACT_DIR / "step41_statement.tex").read_text(encoding="utf-8")
    for snippet in [
        "\\Delta_{\\mathrm{fact}}(\\pi_{\\mathrm{conf,int}},\\pi_{\\mathrm{mass}})=\\varnothing",
        "faithful restatement",
        "does not claim that the framework supplies the condition",
    ]:
        if snippet not in statement:
            fail(f"statement missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    if "recognition-source closure condition" not in boundary or "does not claim that the framework supplies clean separation" not in boundary:
        fail("nonclaim boundary missing recognition-source caveat")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_schema_and_output()
    validate_delta_tables()
    validate_gates_and_controls()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 41 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 41 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 41")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step41.py: PASS")


if __name__ == "__main__":
    main()
