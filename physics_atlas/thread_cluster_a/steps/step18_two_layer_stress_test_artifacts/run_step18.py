#!/usr/bin/env python3
"""Validate Cluster A Step 18 two-layer stress-test artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "two_layer_stress_test_step18.py"

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
]

REQUIRED_FILES = [
    "two_layer_stress_test_step18.py",
    "radiative_channel_step18.csv",
    "coupling_strength_sweep_step18.csv",
    "robustness_sweep_step18.csv",
    "controls_step18.csv",
    "architecture_verdict_step18.csv",
    "overall_verdict_step18.json",
    "candidate_law_obligations_step18.csv",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step18_statement.tex",
    "run_step18.py",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves the hierarchy\b",
    r"\bsolve the hierarchy\b",
    r"\bsolves naturalness\b",
    r"\bderives m_H\b",
    r"\bderive m_H\b",
    r"\bderives y_top\b",
    r"\bderive y_top\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
    r"\bhierarchy_resolved[\"']?\s*:\s*true\b",
    r"\bphysical_mass_value_supplied[\"']?\s*:\s*true\b",
    r"\bdominant_yukawa_value_derived[\"']?\s*:\s*true\b",
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
    print(f"run_step18.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 18 chain\n"
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
        if path.name == "run_step18.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_active_coupling() -> None:
    rows = {row["quantity"]: row for row in read_csv("architecture_verdict_step18.csv")}
    active = float(rows["active_content_scale_coupling_bits"]["value"])
    inherited = float(rows["step17_inherited_residual_bits"]["value"])
    two_layer_fraction = float(rows["two_layer_fraction"]["value"])
    coupled_fraction = float(rows["coupled_but_distinct_fraction"]["value"])
    break_fraction = float(rows["one_layer_break_fraction"]["value"])
    if not (0.38 < active < 0.40):
        fail(f"active coupling outside expected stressed range: {active}")
    if not (0.03 < inherited < 0.05):
        fail(f"inherited residual outside expected range: {inherited}")
    if abs(two_layer_fraction - (1.0 / 3.0)) > 1e-9:
        fail(f"two-layer robustness fraction mismatch: {two_layer_fraction}")
    if abs(coupled_fraction - (2.0 / 3.0)) > 1e-9:
        fail(f"coupled-but-distinct robustness fraction mismatch: {coupled_fraction}")
    if abs(break_fraction) > 1e-12:
        fail(f"unexpected active-strength one-layer break fraction: {break_fraction}")


def validate_strength_sweep_and_controls() -> None:
    rows = read_csv("coupling_strength_sweep_step18.csv")
    if len(rows) < 5:
        fail("strength sweep too small")
    values = [float(row["content_scale_mi_bits"]) for row in rows]
    for before, after in zip(values, values[1:]):
        if after + 1e-12 < before:
            fail(f"coupling strength sweep is not monotone: {values}")
    if values[-1] <= values[0]:
        fail("coupling did not rise from off to strong injected channel")
    active_rows = [row for row in rows if row["channel_strength"] == "1.00"]
    if len(active_rows) != 1 or active_rows[0]["verdict_at_strength"] != "coupled_but_distinct":
        fail("active channel strength verdict mismatch")
    if rows[-1]["verdict_at_strength"] != "one_layer_break":
        fail("strong injected channel should break the two-layer architecture")
    controls = {row["control"]: row for row in read_csv("controls_step18.csv")}
    if controls.get("coupling_strength_monotone", {}).get("passes") != "True":
        fail("monotonic can-fail control did not pass")
    if controls.get("gauge_generation_reference_detected", {}).get("passes") != "True":
        fail("gauge-generation control did not pass")


def validate_robustness_and_verdict() -> None:
    rows = read_csv("robustness_sweep_step18.csv")
    if len(rows) != 36:
        fail(f"expected 36 robustness cells, got {len(rows)}")
    verdict_counts = {}
    for row in rows:
        verdict_counts[row["verdict"]] = verdict_counts.get(row["verdict"], 0) + 1
    if verdict_counts.get("two_layer", 0) != 12:
        fail(f"expected 12 two-layer cells, got {verdict_counts}")
    if verdict_counts.get("coupled_but_distinct", 0) != 24:
        fail(f"expected 24 coupled-but-distinct cells, got {verdict_counts}")
    if verdict_counts.get("one_layer_break", 0) not in {0, None}:
        fail(f"unexpected one-layer break cells at active strength: {verdict_counts}")
    verdict = json.loads((ARTIFACT_DIR / "overall_verdict_step18.json").read_text(encoding="utf-8"))
    if verdict.get("verdict") != "coupled_but_distinct":
        fail(f"unexpected verdict: {verdict.get('verdict')}")
    if verdict.get("coupling_strength_monotone") is not True:
        fail("schema monotonicity flag missing")
    if float(verdict.get("active_content_scale_coupling_bits", 0.0)) <= float(verdict.get("step17_inherited_residual_bits", 0.0)):
        fail("active channel did not exceed Step 17 residual")
    if float(verdict.get("active_content_scale_coupling_bits", 0.0)) >= float(verdict.get("gauge_generation_reference_bits", 0.0)):
        fail("active channel should remain below gauge-generation reference for coupled-but-distinct verdict")
    for key in [
        "hierarchy_resolved",
        "physical_mass_value_supplied",
        "dominant_yukawa_value_derived",
        "root_landed",
        "frame_transfer_certified",
    ]:
        if verdict.get(key):
            fail(f"schema overstates {key}")
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("verdict", {}).get("verdict") != "coupled_but_distinct":
        fail("schema wrapper verdict mismatch")


def validate_obligations() -> None:
    rows = {row["obligation"]: row["status"] for row in read_csv("candidate_law_obligations_step18.csv")}
    expected = {
        "faithful_enrichment": "radiative_channel_added",
        "independently_checkable_consequence": "advanced_as_coupled_but_distinct_architecture",
        "derived_formula": "not_advanced_this_step",
        "limit_recovery": "radiative_sensitivity_represented",
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
        "coupled_but_distinct",
        "content-scale coupling",
        "Coupling-Strength Can-Fail",
        "clean Step-17 two-layer split is not robust",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    if "finite-toy architecture stress test" not in boundary or "Frame transfer remains open" not in boundary:
        fail("nonclaim boundary missing scope language")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guard()
    scan_overclaims()
    validate_active_coupling()
    validate_strength_sweep_and_controls()
    validate_robustness_and_verdict()
    validate_obligations()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 18 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 18 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 18")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step18.py: PASS")


if __name__ == "__main__":
    main()
