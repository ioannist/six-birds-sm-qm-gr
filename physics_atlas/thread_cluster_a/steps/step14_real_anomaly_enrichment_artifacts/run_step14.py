#!/usr/bin/env python3
"""Validate Cluster A Step 14 real anomaly enrichment artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "real_anomaly_enrichment_step14.py"

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
]

REQUIRED_FILES = [
    "real_anomaly_enrichment_step14.py",
    "candidate_anomalies_step14.csv",
    "fermion_content_step14.csv",
    "anomaly_free_survivors_step14.csv",
    "hypercharge_solution_step14.json",
    "scoped_consequence_step14.json",
    "candidate_law_obligations_step14.csv",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step14_statement.tex",
    "run_step14.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderive the gauge group\b",
    r"\bderives the hypercharges\b",
    r"\bderive the hypercharges\b",
    r"\bderives the standard model\b",
    r"\bcomputes the number of generations\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy\b",
    r"\bpredicts the fermion masses\b",
    r"\bcomputes the cosmological constant\b",
    r"\bnew physics prediction\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
    r"\bcertified law\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
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

ALLOWED_GRADES = {"finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step14.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 14 chain\n"
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
        if path.name == "run_step14.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_anomalies() -> None:
    rows = {row["candidate_id"]: row for row in read_csv("candidate_anomalies_step14.csv")}
    if len(rows) != 10:
        fail(f"expected 10 candidates, got {len(rows)}")
    sm = rows.get("SM_one_generation")
    if not sm:
        fail("SM_one_generation row missing")
    for key in ["su3_cubic", "su3_sq_u1", "su2_sq_u1", "u1_cubic", "grav_u1", "su5_cubic"]:
        if sm[key] != "0":
            fail(f"SM coefficient {key} is not zero: {sm[key]}")
    if sm["su2_witten_even"] != "True" or sm["anomaly_free"] != "True":
        fail("SM Witten/global anomaly or anomaly_free flag failed")
    anomalous = [row for row in rows.values() if row["anomaly_free"] == "False"]
    if len(anomalous) < 1:
        fail("candidate space lacks an anomalous can-fail witness")
    if rows["quark_sector_only"]["su2_witten_even"] != "False":
        fail("quark_sector_only should trigger Witten parity failure")
    if rows["bad_u_hypercharge"]["su3_sq_u1"] == "0":
        fail("bad_u_hypercharge should have nonzero mixed color anomaly")


def validate_survivors_and_schema() -> None:
    survivors = read_csv("anomaly_free_survivors_step14.csv")
    if len(survivors) < 2:
        fail("necessary-not-sufficient failed: need more than one anomaly-free survivor")
    reference = [row for row in survivors if row["selected_reference"] == "True"]
    unselected = [row for row in survivors if row["survivor_status"] == "unselected_survivor"]
    if len(reference) != 1 or reference[0]["candidate_id"] != "SM_one_generation":
        fail("reference survivor missing or wrong")
    if len(unselected) < 1:
        fail("no anomaly-free unselected survivor found")
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "real_anomaly_enrichment_limit_recovery_constructed":
        fail("schema verdict type mismatch")
    if verdict.get("sm_coefficients_all_zero") is not True:
        fail("schema does not mark SM anomaly-free limit recovery")
    if verdict.get("necessary_not_sufficient") is not True:
        fail("schema does not mark necessary-not-sufficient")
    if verdict.get("unselected_anomaly_free_survivor_count", 0) < 1:
        fail("schema unselected survivor count too small")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame transfer")


def validate_hypercharge_solution() -> None:
    solution = json.loads((ARTIFACT_DIR / "hypercharge_solution_step14.json").read_text(encoding="utf-8"))
    family = solution.get("closed_form_family", {})
    expected = {
        "Y_L": "-3 Y_Q",
        "Y_e_c": "6 Y_Q",
        "{Y_u_c,Y_d_c}": "{-4 Y_Q, 2 Y_Q}",
    }
    for key, value in expected.items():
        if family.get(key) != value:
            fail(f"hypercharge relation mismatch: {key} -> {family.get(key)}")
    relation = solution.get("electric_charge_check", {}).get("relation")
    if relation != "Q_proton = - Q_e":
        fail("charge-quantization relation missing")


def validate_obligations_and_consequence() -> None:
    rows = {row["obligation"]: row for row in read_csv("candidate_law_obligations_step14.csv")}
    required = {
        "faithful_enrichment": "advanced",
        "independently_checkable_consequence": "scoped_for_step15",
        "derived_formula": "advanced",
        "limit_recovery": "advanced",
    }
    for key, status in required.items():
        if rows.get(key, {}).get("status") != status:
            fail(f"obligation {key} has wrong status")
    consequence = json.loads((ARTIFACT_DIR / "scoped_consequence_step14.json").read_text(encoding="utf-8"))
    if consequence.get("most_promising_step15_consequence") != "minimal irreducible anomaly-cancellation support":
        fail("unexpected scoped consequence")
    if "Enumerate chiral spectra" not in consequence.get("independent_check", ""):
        fail("independent check is not concrete enough")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if len(rows) < 6:
        fail("content_classification.csv has too few rows")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unexpected grade: {row}")
        if not row.get("claim") or not row.get("source_artifacts"):
            fail(f"claim row missing content: {row}")
        for source in [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]:
            if source.startswith("/") or ".." in Path(source).parts:
                fail(f"source path must be thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_statement_text() -> None:
    text = (
        (ARTIFACT_DIR / "results_summary.md").read_text(encoding="utf-8")
        + "\n"
        + (ARTIFACT_DIR / "step14_statement.tex").read_text(encoding="utf-8")
        + "\n"
        + (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    )
    required = [
        "real_anomaly_enrichment_limit_recovery_constructed",
        "su3_cubic=0, su3_sq_u1=0, su2_sq_u1=0, u1_cubic=0, grav_u1=0, su5_cubic=0",
        "Y_L = -3 Y_Q",
        "Y_e_c = 6 Y_Q",
        "{Y_u_c, Y_d_c} = {-4 Y_Q, 2 Y_Q}",
        "Q_proton = - Q_electron",
        "Anomaly-free survivor count: `7`",
        "Unselected anomaly-free survivor count: `6`",
        "known physics limit recovery",
        "finite candidate-space",
        "not complete",
    ]
    for snippet in required:
        if snippet not in text:
            fail(f"required prose snippet missing: {snippet}")


def run_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guard()
    scan_overclaims()
    validate_anomalies()
    validate_survivors_and_schema()
    validate_hypercharge_solution()
    validate_obligations_and_consequence()
    validate_content_classification()
    validate_statement_text()
    print("run_step14.py: PASS")


def run_chain() -> None:
    run_prior_validators()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 14 artifacts.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self", action="store_true", help="validate only this step's own artifacts (default)")
    mode.add_argument("--chain", action="store_true", help="validate prior steps once, then this step")
    args = parser.parse_args(argv)
    if args.chain:
        run_chain()
    else:
        run_self()


if __name__ == "__main__":
    main()
