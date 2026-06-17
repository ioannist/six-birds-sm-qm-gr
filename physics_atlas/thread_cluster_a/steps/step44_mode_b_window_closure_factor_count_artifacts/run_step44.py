#!/usr/bin/env python3
"""Validate Cluster A Step 44 factor-count window-closure artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "window_closure_factor_count_step44.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step43_mode_b_window_closure_artifacts" / "run_step43.py",
]

REQUIRED_FILES = [
    "window_closure_factor_count_step44.py",
    "three_factor_coverage_step44.csv",
    "three_factor_clean_separators_step44.csv",
    "signature_analysis_step44.csv",
    "factor_count_bound_step44.csv",
    "combined_window_status_step44.csv",
    "negative_controls_step44.csv",
    "stage2_audit_step44.csv",
    "six_gate_audit_step44.csv",
    "generated_vs_input_step44.csv",
    "window_closure_factor_count_output_step44.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step44_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step44.py",
]

LOGIC_FORBIDDEN_SNIPPETS = [
    "total_slots",
    "FIVE",
    "SU(5)",
    "SO(10)",
    "10+5bar",
    "GUT",
    "target_shape",
    "target_content",
    "common-refinement",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "ψ",
]

OVERCLAIM_PATTERNS = [
    r"\bwindow[- ]closed unconditionally\b",
    r"\bunconditional window closure\b",
    r"\bproves? the SM\b",
    r"\bthe SM is proved\b",
    r"\bderive[sd]?\s+the\s+SM\b",
    r"\bderive[sd]?\s+clean[- ]separation\b",
    r"\bframe-transfer certificate\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\bnew physics\b",
    r"\bco-sourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step44.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_logic() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    logic_region = text.split("def write_docs", maxsplit=1)[0]
    for snippet in LOGIC_FORBIDDEN_SNIPPETS:
        if snippet in logic_region:
            fail(f"build logic contains forbidden primitive snippet: {snippet}")
    if '"2|3"' in logic_region or "'2|3'" in logic_region:
        fail("build logic hardcodes the target shape")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step44.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "window_closure_factor_count_output_step44.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 44:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates status")
        if doc.get("conditional_on_clean_separation") is not True:
            fail("conditional clean-separation status missing")
    if output.get("three_factor_structures") != 35 or output.get("three_factor_structures_covered") != 35:
        fail("three-factor coverage count mismatch")
    if output.get("all_factor_incidence_obstructed_count") != 35:
        fail("all-factor incidence obstruction count mismatch")
    if output.get("three_factor_clean_separator_count") != 0:
        fail("three-factor clean separators should be zero")
    if output.get("three_factor_sm_signature_clean_separator_count") != 0:
        fail("three-factor reference-signature clean separators should be zero")
    if output.get("verdict") != "FACTOR_COUNT_CLOSED":
        fail("unexpected Step 44 verdict")
    if schema.get("six_gates_pass") is not True or schema.get("honest_coverage_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    rows = read_csv("three_factor_coverage_step44.csv")
    if len(rows) != 35:
        fail(f"expected 35 three-factor rows, got {len(rows)}")
    for row in rows:
        if row["coverage_mode"] != "structural_exact_route_obstruction":
            fail(f"bad coverage mode: {row}")
        if row["all_factor_incidence_count"] != "0":
            fail(f"all-factor incidence should be absent: {row}")
        if row["route_complete_possible"] != "False":
            fail(f"route completion should be impossible: {row}")
        if int(row["min_all_factor_component_dim"]) <= int(row["component_cap"]):
            fail(f"component-cap obstruction missing: {row}")
        if row["clean_separation_delta_empty"] != "0" or row["sm_signature_clean_separator"] != "False":
            fail(f"three-factor row incorrectly clean/signature positive: {row}")

    clean_rows = read_csv("three_factor_clean_separators_step44.csv")
    if clean_rows:
        fail("three-factor clean separator table must be empty")

    sig = read_csv("signature_analysis_step44.csv")
    if sig[0]["signature"] != "5|15" or sig[0]["three_factor_clean_separator_count"] != "0" or sig[0]["competitor_present"] != "False":
        fail("signature analysis mismatch")

    bound = read_csv("factor_count_bound_step44.csv")
    if bound[0]["status"] != "structural-arguable-within-finite-component-cap":
        fail("factor-count bound status mismatch")
    if bound[0]["covered_structures"] != "35" or bound[0]["obstructed_structures"] != "35":
        fail("factor-count bound coverage mismatch")

    combined = read_csv("combined_window_status_step44.csv")
    if combined[0]["clean_survivor_structures"] != "2|3":
        fail("combined status no longer points to Step43 clean set")
    if combined[0]["combined_window_status"] != "substantially_complete_conditional_window":
        fail("combined window status mismatch")

    for table in ["negative_controls_step44.csv", "stage2_audit_step44.csv", "six_gate_audit_step44.csv"]:
        for row in read_csv(table):
            if row.get("passes") != "True":
                fail(f"{table} has failing row: {row}")


def validate_classification() -> None:
    for row in read_csv("content_classification.csv"):
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        source = THREAD_DIR / row["source"]
        if not source.exists():
            fail(f"classification source missing: {row['source']}")
        if row["source"].startswith("/"):
            fail(f"classification source must be thread-relative: {row['source']}")


def run_dependency_chain() -> None:
    for runner in DEPENDENCY_RUNNERS:
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
            cwd=STEPS_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{runner.name} failed during dependency chain\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_self() -> None:
    validate_required_files()
    validate_build_logic()
    scan_overclaims()
    validate_schema()
    validate_tables()
    validate_classification()
    print("run_step44.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 44 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 44 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 43 first, then Step 44")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
