#!/usr/bin/env python3
"""Validate Cluster A Step 20 GUT recognition value-relation artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "gut_recognition_value_relations_step20.py"

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
]

REQUIRED_FILES = [
    "gut_recognition_value_relations_step20.py",
    "gut_trace_step20.csv",
    "value_relations_step20.csv",
    "rg_running_step20.csv",
    "unification_test_step20.csv",
    "sin2_running_comparison_step20.csv",
    "susy_comparison_step20.csv",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step20_statement.tex",
    "run_step20.py",
]

OVERCLAIM_PATTERNS = [
    r"\bSBT derives sin\b",
    r"\bSBT-derived sin\b",
    r"\bderives the gauge couplings\b",
    r"\bderive the gauge couplings\b",
    r"\bderives the SM\b",
    r"\bderive the SM\b",
    r"\bsolves the hierarchy\b",
    r"\bsolve the hierarchy\b",
    r"\bclean non-SUSY unification\b",
    r"\bnon-SUSY SU\(5\) cleanly unifies\b",
    r"\bnew physics prediction\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
    r"\bsbt_value_derivation[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
]

BUILD_FORBIDDEN = [
    "psi",
    "ψ",
    "co-sourcing",
    "common-refinement",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
]

ALLOWED_GRADES = {"recognition-import-derived-relation", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step20.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 20 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_guard() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for snippet in BUILD_FORBIDDEN:
        if snippet in text:
            fail(f"build script contains forbidden construction term: {snippet}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step20.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_trace_relation() -> None:
    trace_rows = read_csv("gut_trace_step20.csv")
    total = [row for row in trace_rows if row["multiplet"] == "total"]
    if len(total) != 1:
        fail("trace table must contain one total row")
    tr_y = float(total[0]["Tr_Y2_contribution"])
    tr_t3 = float(total[0]["Tr_T3_2_contribution"])
    if abs(tr_y - (10 / 3)) > 1e-12:
        fail(f"TrY2 mismatch: {tr_y}")
    if abs(tr_t3 - 2.0) > 1e-12:
        fail(f"TrT3sq mismatch: {tr_t3}")
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    trace = schema["trace_relation"]
    if abs(float(trace["hypercharge_normalization"]) - (5 / 3)) > 1e-12:
        fail("hypercharge normalization mismatch")
    if abs(float(trace["sin2_gut"]) - 0.375) > 1e-12:
        fail("sin2 GUT relation mismatch")
    relations = {row["relation"]: row for row in read_csv("value_relations_step20.csv")}
    if relations.get("sin2_thetaW_GUT", {}).get("value") != "0.375000000000":
        fail("value relation sin2 missing")
    if "m_b=m_tau" not in relations.get("bottom_tau_relation", {}).get("value", ""):
        fail("bottom-tau relation missing")


def validate_rg_near_miss() -> None:
    rows = read_csv("unification_test_step20.csv")
    pair_rows = [row for row in rows if row["test"] == "pair_crossing"]
    fit_rows = [row for row in rows if row["test"] == "least_squares_best_fit"]
    if len(pair_rows) != 3 or len(fit_rows) != 1:
        fail("unification test rows incomplete")
    pair_logs = [float(row["log10_scale_GeV"]) for row in pair_rows]
    if max(pair_logs) - min(pair_logs) < 3.5:
        fail(f"pair crossing spread too small for non-SUSY near-miss: {pair_logs}")
    fit = fit_rows[0]
    if fit["clean_unification"] != "False":
        fail("non-SUSY unification must not be reported clean")
    spread = float(fit["spread_inverse_coupling"])
    if spread < 3.0:
        fail(f"best-fit spread too small; expected near-miss/failure: {spread}")
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    sm = schema["sm_one_loop_unification"]
    if sm.get("clean_unification") is not False:
        fail("schema claims clean non-SUSY unification")
    if float(sm["spread_inverse_coupling"]) < 3.0:
        fail("schema spread too small for non-SUSY near-miss")


def validate_sin2_and_susy_comparison() -> None:
    rows = read_csv("sin2_running_comparison_step20.csv")
    if len(rows) != 1:
        fail("sin2 comparison must have one row")
    pred = float(rows[0]["sin2_thetaW_MZ_pred"])
    measured = float(rows[0]["sin2_thetaW_MZ_measured"])
    diff = abs(float(rows[0]["difference"]))
    if not (0.214 < pred < 0.215):
        fail(f"sin2 prediction outside expected non-SUSY best-fit range: {pred}")
    if abs(measured - 0.23122) > 1e-12:
        fail("measured sin2 mismatch")
    if diff < 0.01:
        fail("sin2 discrepancy should be visible for the near-miss")
    susy_rows = read_csv("susy_comparison_step20.csv")
    fit = [row for row in susy_rows if row["test"] == "least_squares_best_fit"]
    if len(fit) != 1:
        fail("SUSY comparison fit row missing")
    if float(fit[0]["spread_inverse_coupling"]) > 0.2:
        fail("SUSY comparison should be tighter than non-SUSY in this one-loop comparison")


def validate_schema_nonclaims() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("sbt_value_derivation") is not False:
        fail("schema must not mark SBT value derivation")
    if schema.get("absolute_values_residual") is not True:
        fail("schema must keep absolute values residual")
    if schema.get("frame_transfer_certified") or schema.get("root_landed"):
        fail("schema overstates frame transfer or root landing")


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
        "Mode A / E2 import",
        "sin^2(theta_W)",
        "does not cleanly unify",
        "Value-relations via E2 recognition import",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    if "not SBT-alone value derivations" not in boundary or "fails clean unification" not in boundary:
        fail("nonclaim boundary missing recognition/failure language")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guard()
    scan_overclaims()
    validate_trace_relation()
    validate_rg_near_miss()
    validate_sin2_and_susy_comparison()
    validate_schema_nonclaims()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 20 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 20 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 20")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step20.py: PASS")


if __name__ == "__main__":
    main()
