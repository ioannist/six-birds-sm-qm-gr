#!/usr/bin/env python3
"""Validate Cluster A Step 17 two-layer architecture artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "two_layer_test_step17.py"

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
]

REQUIRED_FILES = [
    "two_layer_test_step17.py",
    "scale_enrichment_step17.csv",
    "architecture_characterization_step17.csv",
    "coupling_step17.csv",
    "controls_step17.csv",
    "overall_verdict_step17.json",
    "candidate_law_obligations_step17.csv",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step17_statement.tex",
    "run_step17.py",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves the hierarchy\b",
    r"\bsolve the hierarchy\b",
    r"\bsolves naturalness\b",
    r"\bderives m_H\b",
    r"\bderives the Higgs\b",
    r"\bpredicts the Higgs\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
    r"\bhierarchy_resolved[\"']?\s*:\s*true\b",
    r"\bphysical_mass_value_supplied[\"']?\s*:\s*true\b",
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
    print(f"run_step17.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 17 chain\n"
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
        if path.name == "run_step17.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_architecture() -> None:
    rows = {row["test"]: row for row in read_csv("architecture_characterization_step17.csv")}
    if rows.get("carrier_disjointness", {}).get("result") != "True":
        fail("carrier disjointness did not pass")
    if rows.get("measure_kind", {}).get("result") != "True":
        fail("measure-kind distinction did not pass")
    if rows.get("content_selection_status", {}).get("result") != "rigorous_type_limit_negative":
        fail("content-selection status did not preserve Step 16 result")


def validate_couplings_and_controls() -> None:
    rows = {row["measure_id"]: row for row in read_csv("coupling_step17.csv")}
    required = {"scale_vs_content_product", "step8_ew_vs_content_residual", "gauge_generation_control"}
    if set(rows) != required:
        fail(f"coupling rows mismatch: {sorted(rows)}")
    product_mi = float(rows["scale_vs_content_product"]["mi_bits"])
    residual_mi = float(rows["step8_ew_vs_content_residual"]["mi_bits"])
    control_mi = float(rows["gauge_generation_control"]["mi_bits"])
    if abs(product_mi) > 1e-12:
        fail(f"scale/content product MI should be zero, got {product_mi}")
    if not (0.03 < residual_mi < 0.05):
        fail(f"inherited EW/content residual out of expected low range: {residual_mi}")
    if control_mi <= 0.1:
        fail(f"can-fail control failed: gauge-generation MI too small: {control_mi}")
    if rows["gauge_generation_control"]["verdict"] != "coupling_detected":
        fail("gauge-generation control verdict not detected")
    controls = {row["control"]: row for row in read_csv("controls_step17.csv")}
    if controls.get("gauge_generation_known_coupling", {}).get("passes") != "True":
        fail("known-coupling control did not pass")
    if controls.get("scale_product_independence_not_forced_by_metric", {}).get("passes") != "True":
        fail("scale independence anti-artifact control did not pass")


def validate_schema_and_verdict() -> None:
    verdict = json.loads((ARTIFACT_DIR / "overall_verdict_step17.json").read_text(encoding="utf-8"))
    if verdict.get("verdict") != "two_selection_layers":
        fail(f"unexpected verdict: {verdict.get('verdict')}")
    if verdict.get("carrier_disjoint") is not True:
        fail("schema carrier disjointness false")
    if verdict.get("measure_kind_distinct") is not True:
        fail("schema measure-kind distinction false")
    if verdict.get("control_detects_known_coupling") is not True:
        fail("schema does not record coupling control")
    if verdict.get("scale_vs_content_product_mi_bits") != 0.0:
        fail("schema product MI mismatch")
    if not (0.03 < float(verdict.get("step8_ew_vs_content_residual_bits", 0.0)) < 0.05):
        fail("schema residual MI mismatch")
    if float(verdict.get("gauge_generation_control_mi_bits", 0.0)) <= 0.1:
        fail("schema control MI too small")
    for key in ["hierarchy_resolved", "physical_mass_value_supplied", "root_landed", "frame_transfer_certified"]:
        if verdict.get(key):
            fail(f"schema overstates {key}")
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("verdict", {}).get("verdict") != "two_selection_layers":
        fail("schema wrapper verdict mismatch")


def validate_obligations() -> None:
    rows = {row["obligation"]: row["status"] for row in read_csv("candidate_law_obligations_step17.csv")}
    expected = {
        "faithful_enrichment": "light_scale_enrichment",
        "independently_checkable_consequence": "advanced_as_architecture_split",
        "derived_formula": "not_advanced_this_step",
        "limit_recovery": "hierarchy_structure_represented_only",
    }
    for key, status in expected.items():
        if rows.get(key) != status:
            fail(f"obligation {key} expected {status}, got {rows.get(key)}")


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
        "two_selection_layers",
        "Scale-vs-content product MI",
        "Gauge-generation control MI",
        "content/anomaly-selection layer and a separate scale/naturalness-selection layer",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    if "toy-internal" not in boundary or "does not provide a physical Higgs-scale value" not in boundary:
        fail("nonclaim boundary missing scope language")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guard()
    scan_overclaims()
    validate_architecture()
    validate_couplings_and_controls()
    validate_schema_and_verdict()
    validate_obligations()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 17 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 17 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 17")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step17.py: PASS")


if __name__ == "__main__":
    main()
