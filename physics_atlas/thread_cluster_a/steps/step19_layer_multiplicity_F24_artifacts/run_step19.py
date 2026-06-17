#!/usr/bin/env python3
"""Validate Cluster A Step 19 F24/F47 layer multiplicity artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "layer_multiplicity_f24_step19.py"

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
]

REQUIRED_FILES = [
    "layer_multiplicity_f24_step19.py",
    "role_obstruction_fibers_step19.csv",
    "role_obstruction_witnesses_step19.csv",
    "f47_selector_region_step19.csv",
    "f47_selector_summary_step19.csv",
    "f24_resolution_step19.csv",
    "controls_step19.csv",
    "overall_verdict_step19.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step19_statement.tex",
    "run_step19.py",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves the hierarchy\b",
    r"\bsolve the hierarchy\b",
    r"\bderives m_H\b",
    r"\bderive m_H\b",
    r"\btwo physical layers\b",
    r"\bis a causal channel\b",
    r"\bcertified causal channel\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
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
    print(f"run_step19.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 19 chain\n"
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
        if path.name == "run_step19.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_obstruction_and_controls() -> None:
    verdict = json.loads((ARTIFACT_DIR / "overall_verdict_step19.json").read_text(encoding="utf-8"))
    if verdict.get("role_obstruction_pairs") != 5760:
        fail(f"role obstruction mismatch: {verdict.get('role_obstruction_pairs')}")
    if verdict.get("descends") is not False or verdict.get("role_split") is not True:
        fail("descends/RoleSplit verdict mismatch")
    if verdict.get("descending_control_obstruction") != 0:
        fail("descending control obstruction must be 0")
    if verdict.get("splitting_control_obstruction") != 8640:
        fail("splitting control obstruction must be 8640")
    controls = {row["control"]: row for row in read_csv("controls_step19.csv")}
    if controls.get("known_descending_role", {}).get("passes") != "True":
        fail("known descending control failed")
    if controls.get("known_splitting_role", {}).get("passes") != "True":
        fail("known splitting control failed")
    if controls.get("main_role_split", {}).get("passes") != "True":
        fail("main role split control failed")
    witnesses = read_csv("role_obstruction_witnesses_step19.csv")
    if not witnesses:
        fail("role obstruction witnesses missing")


def validate_f24_resolution() -> None:
    rows = read_csv("f24_resolution_step19.csv")
    firing = [row["family"] for row in rows if row["fires"] == "True"]
    if firing != ["BudgetedRole"]:
        fail(f"expected only BudgetedRole to fire, got {firing}")
    memory = [row for row in rows if row["family"] == "MemoryLayer"]
    if len(memory) != 1 or memory[0]["fires"] != "False":
        fail("MemoryLayer must be ruled out")
    verdict = json.loads((ARTIFACT_DIR / "overall_verdict_step19.json").read_text(encoding="utf-8"))
    if verdict.get("selected_f24_resolution") != "BudgetedRole":
        fail("schema F24 resolution mismatch")
    if verdict.get("memory_layer_forms") is not False:
        fail("schema incorrectly forms MemoryLayer")
    if verdict.get("budgeted_role") is not True:
        fail("schema does not mark BudgetedRole")
    if verdict.get("structural_dependency_not_tdgate") is not True:
        fail("schema must record structural-dependency note")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame transfer")


def validate_f47() -> None:
    rows = read_csv("f47_selector_summary_step19.csv")
    if len(rows) != 1:
        fail("F47 summary must have one row")
    row = rows[0]
    if int(row["mu_total"]) != 8640 or int(row["mu_sigma"]) != 342:
        fail(f"F47 measure counts mismatch: {row}")
    frac = float(row["selector_fraction"])
    if abs(frac - 0.039583333333) > 1e-12:
        fail(f"F47 selector fraction mismatch: {frac}")
    for key in ["positive_measure", "small", "realized_in_sigma", "realized"]:
        if row[key] != "True":
            fail(f"F47 {key} must be True")
    verdict = json.loads((ARTIFACT_DIR / "overall_verdict_step19.json").read_text(encoding="utf-8"))
    if verdict.get("f47_small") is not True or verdict.get("f47_realized") is not True:
        fail("schema F47 small/realized mismatch")


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
        "`|O_s|` unordered q-fiber pairs: `5760`",
        "Selected resolution: `BudgetedRole`",
        "MemoryLayer is not selected",
        "not a TDGate-certified cause relation",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    if "finite-toy instantiation" not in boundary or "not a TDGate-certified cause relation" not in boundary:
        fail("nonclaim boundary missing scope language")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guard()
    scan_overclaims()
    validate_obstruction_and_controls()
    validate_f24_resolution()
    validate_f47()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 19 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 19 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 19")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step19.py: PASS")


if __name__ == "__main__":
    main()
