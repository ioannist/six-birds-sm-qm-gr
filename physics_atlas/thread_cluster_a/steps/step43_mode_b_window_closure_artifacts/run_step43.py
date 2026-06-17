#!/usr/bin/env python3
"""Validate Cluster A Step 43 window-closure artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "window_closure_step43.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "run_step33.py",
    STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "run_step35.py",
    STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "run_step38.py",
    STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "run_step41.py",
]

REQUIRED_FILES = [
    "window_closure_step43.py",
    "widened_structure_counts_step43.csv",
    "widened_support_scores_step43.csv",
    "clean_survivors_step43.csv",
    "per_factor_count_counts_step43.csv",
    "per_max_dim_counts_step43.csv",
    "monotonicity_bounds_step43.csv",
    "coverage_statement_step43.csv",
    "negative_controls_step43.csv",
    "stage2_audit_step43.csv",
    "six_gate_audit_step43.csv",
    "generated_vs_input_step43.csv",
    "window_closure_output_step43.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step43_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step43.py",
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
    r"\bclean[- ]separation\s+is\s+fundamental\b",
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
    print(f"run_step43.py: FAIL: {message}", file=sys.stderr)
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
        fail("build logic hardcodes the target dimensions")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step43.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "window_closure_output_step43.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 43:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates status")
        if doc.get("conditional_on_clean_separation") is not True:
            fail("conditional clean-separation status missing")
    if output.get("declared_factor_counts") != "1..3" or output.get("declared_dimensions") != "2..6":
        fail("declared widened window mismatch")
    if output.get("structures_declared") != 55:
        fail("widened structure count mismatch")
    if int(output.get("structures_exact", 0)) < 20:
        fail("exact coverage did not include at least all one/two-factor structures")
    if int(output.get("structures_skipped", 0)) <= 0:
        fail("honest skipped coverage row missing")
    if output.get("clean_survivor_count") != 8 or output.get("target_passes_clean") is not True:
        fail("clean target survivor count/status mismatch")
    if output.get("verdict") not in {"WINDOW_STABLE_BOUND_CANDIDATE_PARTIAL", "WINDOW_DEPENDENT"}:
        fail("unexpected verdict")
    if schema.get("six_gates_pass") is not True or schema.get("honest_coverage_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    structures = read_csv("widened_structure_counts_step43.csv")
    if len(structures) != 55:
        fail(f"expected 55 structure rows, got {len(structures)}")
    for row in structures:
        if row["factor_count"] in {"1", "2"} and row["coverage_mode"] != "exact_full_chain":
            fail(f"one/two-factor row was not exact: {row}")
    skipped = [row for row in structures if row["coverage_mode"] == "not_exact_enumerated"]
    exact = [row for row in structures if row["coverage_mode"] != "not_exact_enumerated"]
    if not skipped or not exact:
        fail("coverage ledger must contain both exact and skipped regions")

    clean = read_csv("clean_survivors_step43.csv")
    if len(clean) != 8:
        fail("expected 8 clean survivors")
    clean_dims = {row["dimensions"] for row in clean}
    if len(clean_dims) != 1:
        fail(f"clean survivors span multiple structures: {clean_dims}")
    if not any(row["is_target_reference"] == "True" for row in clean):
        fail("target reference is not among clean survivors")
    for row in clean:
        if row["broken_vector_exotic_count"] != "0" or row["clean_separation_delta_empty"] != "True":
            fail(f"clean row has non-clean values: {row}")

    factors = read_csv("per_factor_count_counts_step43.csv")
    factor_map = {row["factor_count"]: row for row in factors}
    if factor_map["1"]["clean_separation_delta_empty"] != "0":
        fail("single-factor clean count should be zero in exact rows")
    if factor_map["2"]["clean_separation_delta_empty"] != "8":
        fail("two-factor clean count should be 8")
    if int(factor_map["3"]["structures_skipped"]) <= 0:
        fail("three-factor skipped coverage not recorded")

    bounds = {row["bound_candidate"]: row for row in read_csv("monotonicity_bounds_step43.csv")}
    if bounds["single_factor_N_ge_3_clean_separation_bound"]["status"] != "structural-arguable":
        fail("single-factor bound status mismatch")
    if bounds["factor_count_ge_3_bound"]["status"] != "empirical-partial":
        fail("factor-count bound must remain partial")
    if bounds["charge_lattice_bound"]["status"] != "empirical-only":
        fail("charge bound must remain empirical-only")

    for table in ["negative_controls_step43.csv", "stage2_audit_step43.csv", "six_gate_audit_step43.csv"]:
        for row in read_csv(table):
            key = "passes" if "passes" in row else "stage_ii_check"
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
    print("run_step43.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 43 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 43 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate relevant dependency runners first, then Step 43")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
