#!/usr/bin/env python3
"""Validate Cluster A Step 15 minimal anomaly-support artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "minimal_anomaly_support_step15.py"

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
]

REQUIRED_FILES = [
    "minimal_anomaly_support_step15.py",
    "multiplet_types_step15.csv",
    "raw_anomaly_free_supports_step15.csv",
    "irreducible_chiral_supports_step15.csv",
    "minimality_ordering_step15.csv",
    "competitors_at_or_below_sm_step15.csv",
    "enumeration_summary_step15.csv",
    "sm_location_step15.json",
    "candidate_law_obligations_step15.csv",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step15_statement.tex",
    "run_step15.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderive the gauge group\b",
    r"\bderives the SM\b",
    r"\bderive the SM\b",
    r"\bderives the standard model\b",
    r"\bcomputes the number of generations\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy\b",
    r"\bpredicts the fermion masses\b",
    r"\bcomputes the cosmological constant\b",
    r"\bnew physics prediction\b",
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
    print(f"run_step15.py: FAIL: {message}", file=sys.stderr)
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
                f"{runner.name} failed during Step 15 chain\n"
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
        if path.name == "run_step15.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_counts_and_can_fail() -> None:
    summary_rows = read_csv("enumeration_summary_step15.csv")
    if len(summary_rows) != 1:
        fail("enumeration_summary_step15.csv must have one row")
    row = summary_rows[0]
    expected_ints = {
        "multiplet_type_count": 66,
        "raw_candidate_count": 9705619,
        "raw_anomaly_free_count": 1161,
        "irreducible_chiral_support_count": 28,
        "non_sm_irreducible_support_count": 27,
        "sm_rank": 28,
        "sm_multiplet_count": 5,
        "sm_weyl_component_count": 15,
        "minimal_multiplet_count": 4,
        "minimal_weyl_component_count": 12,
        "competitors_at_or_below_sm": 27,
    }
    for key, expected in expected_ints.items():
        if int(row[key]) != expected:
            fail(f"{key} expected {expected}, got {row[key]}")
    if row["verdict"] != "honest_no_go_minimality_insufficient":
        fail(f"unexpected verdict: {row['verdict']}")
    if int(row["non_sm_irreducible_support_count"]) < 1:
        fail("can-fail control failed: no non-SM irreducible anomaly-free support")


def validate_sm_and_competitors() -> None:
    ordering = read_csv("minimality_ordering_step15.csv")
    sm_rows = [row for row in ordering if row["is_sm_support"] == "True"]
    if len(sm_rows) != 1:
        fail("SM support must appear exactly once in minimality ordering")
    sm = sm_rows[0]
    if int(sm["rank"]) != 28 or sm["minimality_relation_to_sm"] != "sm":
        fail(f"SM location mismatch: {sm}")
    competitors = read_csv("competitors_at_or_below_sm_step15.csv")
    if len(competitors) != 27:
        fail(f"expected 27 competitors at or below SM, got {len(competitors)}")
    if not any(row["relation_to_sm"] == "beats_sm" for row in competitors):
        fail("competitor list lacks a support that beats SM")
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "honest_no_go_minimality_insufficient":
        fail("schema verdict type mismatch")
    if verdict.get("sm_present_and_anomaly_free") is not True:
        fail("schema does not mark SM present and anomaly-free")
    if verdict.get("can_fail_control_non_sm_support_exists") is not True:
        fail("schema does not mark can-fail alternative")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame transfer")


def validate_quotient_outputs() -> None:
    raw_rows = read_csv("raw_anomaly_free_supports_step15.csv")
    if len(raw_rows) != 1161:
        fail(f"raw anomaly-free support count mismatch: {len(raw_rows)}")
    supports = read_csv("irreducible_chiral_supports_step15.csv")
    if len(supports) != 28:
        fail(f"irreducible support count mismatch: {len(supports)}")
    if sum(1 for row in supports if row["is_sm_support"] == "True") != 1:
        fail("irreducible supports must contain the SM support exactly once")
    if not any(row["irreducible_empty_after_quotient"] == "True" for row in raw_rows):
        fail("quotient should remove at least one trivial/vector-like support to empty")


def validate_obligations() -> None:
    rows = {row["obligation"]: row for row in read_csv("candidate_law_obligations_step15.csv")}
    required = {
        "faithful_enrichment": "continued",
        "independently_checkable_consequence": "advanced_as_typed_no_go",
        "derived_formula": "inherited_from_step14",
        "limit_recovery": "continued",
    }
    for key, status in required.items():
        if rows.get(key, {}).get("status") != status:
            fail(f"obligation {key} has wrong status")
    sm_location = json.loads((ARTIFACT_DIR / "sm_location_step15.json").read_text(encoding="utf-8"))
    if sm_location.get("lands") != "beaten":
        fail("SM location should be beaten under the declared measure")
    if "electroweak quark-lepton participation" not in sm_location.get("next_principle", ""):
        fail("next principle not named precisely")


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
        + (ARTIFACT_DIR / "step15_statement.tex").read_text(encoding="utf-8")
        + "\n"
        + (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    )
    required = [
        "Primary measure: irreducible chiral multiplet count",
        "Raw bounded supports: `9705619`",
        "Raw anomaly-free supports: `1161`",
        "Distinct irreducible chiral supports after quotient: `28`",
        "Non-SM irreducible anomaly-free supports: `27`",
        "The can-fail control passes",
        "SM rank: `28` of `28`",
        "honest_no_go_minimality_insufficient",
        "minimality must be supplemented by an electroweak quark-lepton participation",
        "conditional on the gauge group",
        "finite and bounded",
    ]
    for snippet in required:
        if snippet not in text:
            fail(f"required prose snippet missing: {snippet}")
    if "frame-transfer remains open" not in text.lower():
        fail("required prose snippet missing: frame-transfer remains open")


def run_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guard()
    scan_overclaims()
    validate_counts_and_can_fail()
    validate_sm_and_competitors()
    validate_quotient_outputs()
    validate_obligations()
    validate_content_classification()
    validate_statement_text()
    print("run_step15.py: PASS")


def run_chain() -> None:
    run_prior_validators()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 15 artifacts.")
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
