#!/usr/bin/env python3
"""Validate Cluster A Step 51 N_gen neutrality assay artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "ngen_neutrality_step51.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step48_mode_b_content_cascade_artifacts" / "run_step48.py",
]

REQUIRED_FILES = [
    "ngen_neutrality_step51.py",
    "ngen_closure_table_step51.csv",
    "minimality_selector_step51.csv",
    "cp_phase_bound_step51.csv",
    "selector_classification_step51.csv",
    "negative_controls_step51.csv",
    "anti_smuggle_self_check_step51.csv",
    "six_gate_audit_step51.csv",
    "typed_ngen_verdict_step51.csv",
    "generated_vs_input_step51.csv",
    "ngen_neutrality_output_step51.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step51_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step51.py",
]

LOGIC_FORBIDDEN_SNIPPETS = [
    "N_GEN_SM",
    "target_N",
    "target_n",
    "if family_count == 3",
    "if n == 3",
    "bonus",
    "3 generations",
    "three generations",
    "GUT",
    "string parent",
    "common-refinement",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi-as-cosourcing",
]

OVERCLAIM_PATTERNS = [
    r"\bderive[sd]?\s+three\s+generations\b",
    r"\bderive[sd]?\s+N_gen\s*=\s*3\b",
    r"\bexplains?\s+N_gen\b",
    r"\bselects?\s+3\b",
    r"\bselects?\s+three\s+generations\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew physics\b",
    r"\bco-sourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step51.py: FAIL: {message}", file=sys.stderr)
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
            fail(f"build logic contains forbidden selector/prior snippet: {snippet}")
    if "cp_phase_count(" not in logic_region or "(family_count - 1) * (family_count - 2) // 2" not in logic_region:
        fail("general CP phase formula is missing")
    if "min(minimal_candidates" not in logic_region:
        fail("minimality negative-control computation missing")
    if "N_VALUES = list(range(0, 7))" not in text:
        fail("neutral N carrier declaration missing")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step51.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "ngen_neutrality_output_step51.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 51:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates status")
    if output.get("carrier_N_values") != "0..6" or output.get("active_N_values") != "1..6":
        fail("neutral N carrier mismatch")
    if output.get("full_chain_blind_for_all_active_N") is not True:
        fail("closure chain blindness should hold for all active N")
    if output.get("minimality_choice_N") != 1 or output.get("minimality_selects_target") is not False:
        fail("minimality negative-control status mismatch")
    if output.get("cp_lower_bound_N") != 3:
        fail("CP lower-bound computation mismatch")
    if output.get("cp_bound_is_selection") is not False or output.get("cp_bound_classification") != "recognition_source_lower_bound":
        fail("CP handle must be flagged as bound-not-selection")
    if output.get("verdict") != "N_GEN_BLIND_TYPE_LIMIT" or output.get("content_type_limit") is not True:
        fail("unexpected Step 51 verdict")
    if output.get("observed_input_required") is not True or output.get("simulations_excluded_by_design") is not True:
        fail("observed-input/E0 exclusion status missing")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_smuggle_self_check_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    rows = read_csv("ngen_closure_table_step51.csv")
    if [row["N"] for row in rows] != [str(n) for n in range(7)]:
        fail("N carrier table should cover 0..6 exactly")
    active = [row for row in rows if int(row["N"]) >= 1]
    if not all(row["full_chain_passes"] == "True" for row in active):
        fail("all active N rows should pass the full chain")
    if not all(row["same_as_one_unit"] == "True" for row in active):
        fail("all active N rows should be same-as-one-unit")
    if any(row[key] != "0" for row in active for key in ("su3_cubic", "su3_sq_u1", "su2_sq_u1", "u1_cubic", "grav_u1")):
        fail("active N anomaly coefficients should vanish")
    for row in active:
        if int(row["su2_doublet_count"]) != 4 * int(row["N"]) or row["witten_even"] != "True":
            fail(f"Witten parity row mismatch: {row}")
    if rows[0]["full_chain_passes"] != "False":
        fail("N=0 should not be counted as active full closure")

    cp = {int(row["N"]): int(row["cp_phase_count"]) for row in read_csv("cp_phase_bound_step51.csv")}
    expected_cp = {0: 0, 1: 0, 2: 0, 3: 1, 4: 3, 5: 6, 6: 10}
    if cp != expected_cp:
        fail(f"CP phase table mismatch: {cp}")
    cp_rows = read_csv("cp_phase_bound_step51.csv")
    if any(row["classification"] == "recognition_source_bound_not_selection" and int(row["N"]) < 3 for row in cp_rows):
        fail("CP recognition bound should not be flagged below the first positive phase count")

    minimality = read_csv("minimality_selector_step51.csv")[0]
    if minimality["computed_choice_N"] != "1" or minimality["selects_observed_value"] != "False":
        fail("minimality selector table mismatch")
    verdict = read_csv("typed_ngen_verdict_step51.csv")[0]
    if verdict["verdict"] != "N_GEN_BLIND_TYPE_LIMIT" or verdict["full_chain_blind_for_all_active_N"] != "True":
        fail("typed verdict mismatch")
    if verdict["minimality_choice_N"] != "1" or verdict["cp_lower_bound_N"] != "3":
        fail("typed selector results mismatch")
    if verdict["cp_bound_classification"] != "recognition_source_lower_bound":
        fail("typed CP classification mismatch")

    for row in read_csv("negative_controls_step51.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("anti_smuggle_self_check_step51.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle self-check failed: {row}")
    for row in read_csv("six_gate_audit_step51.csv"):
        if row["passes"] != "True":
            fail(f"gate failed: {row}")


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
    print("run_step51.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 51 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 51 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 48 first, then Step 51")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
