#!/usr/bin/env python3
"""Validate Cluster A Step 47 GUT-SM nonfactorization artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "gut_sm_nonfactorization_step47.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "run_step41.py",
    STEPS_DIR / "step46_mode_b_monopole_F48_artifacts" / "run_step46.py",
]

REQUIRED_FILES = [
    "gut_sm_nonfactorization_step47.py",
    "readout_states_step47.csv",
    "chosen_readouts_step47.csv",
    "delta_fact_sm_to_gut_step47.csv",
    "delta_fact_gut_to_sm_step47.csv",
    "xy_witness_identity_step47.csv",
    "structural_relationship_step47.csv",
    "negative_controls_step47.csv",
    "six_gate_audit_step47.csv",
    "generated_vs_input_step47.csv",
    "gut_sm_nonfactorization_output_step47.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step47_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step47.py",
]

LOGIC_FORBIDDEN_SNIPPETS = [
    "common-refinement",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi-as-cosourcing",
    "ψ",
]

OVERCLAIM_PATTERNS = [
    r"\bproves?\s+the\s+GUT\s+is\s+real\b",
    r"\bGUT layer exists\b",
    r"\bcertifies?\s+emergence\b",
    r"\bTopDownChannel\s+certified\b",
    r"\bphysical_reading_resolved[\"']?\s*:\s*true\b",
    r"\btopdown_channel_certified[\"']?\s*:\s*true\b",
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
    print(f"run_step47.py: FAIL: {message}", file=sys.stderr)
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
            fail(f"build logic contains forbidden snippet: {snippet}")
    if "delta_fact(" not in logic_region:
        fail("Delta_fact computation is not present in build logic")
    if "physical_reading_resolved" not in logic_region or "topdown_channel_certified" not in logic_region:
        fail("status-family flags are missing from build logic")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step47.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "gut_sm_nonfactorization_output_step47.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 47:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates physical status")
        if doc.get("structdown_only") is not True:
            fail("StructDown-only status missing")
        if doc.get("physical_reading_resolved") is not False or doc.get("topdown_channel_certified") is not False:
            fail("physical status must remain unresolved/uncertified")
    if output.get("structural_verdict") != "GENUINE_STRUCTURAL_REFINEMENT":
        fail("unexpected structural verdict")
    if output.get("delta_sm_to_gut_count") != 15 or output.get("delta_gut_to_sm_count") != 0:
        fail("Delta_fact counts mismatch")
    if output.get("xy_witness_identity") is not True or output.get("step46_identity_consistent") is not True:
        fail("witness identity did not pass")
    if schema.get("six_gates_pass") is not True or schema.get("status_family_separation_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    states = read_csv("readout_states_step47.csv")
    if len(states) != 9:
        fail(f"expected 9 readout states, got {len(states)}")
    if sum(1 for row in states if row["state_kind"] == "colored_coset_generator") != 6:
        fail("expected six colored-coset states")

    forward = read_csv("delta_fact_sm_to_gut_step47.csv")
    reverse = read_csv("delta_fact_gut_to_sm_step47.csv")
    if len(forward) != 15:
        fail(f"expected 15 forward Delta_fact witnesses, got {len(forward)}")
    if reverse:
        fail("reverse Delta_fact should be empty")
    if not all(row["shared_pi0"] == "SM:not_realized_colored_coset" for row in forward):
        fail("forward witnesses should be SM-lumped colored coset states")

    identity = read_csv("xy_witness_identity_step47.csv")
    if identity[0]["identity_holds"] != "True" or identity[0]["step46_identity_consistent"] != "True":
        fail("X/Y witness identity failed")
    if identity[0]["step41_witness_count"] != "6" or identity[0]["delta_witness_count"] != "6":
        fail("witness identity counts mismatch")

    relationship = read_csv("structural_relationship_step47.csv")[0]
    if relationship["structural_verdict"] != "GENUINE_STRUCTURAL_REFINEMENT":
        fail("relationship verdict mismatch")
    if relationship["structdown_only"] != "True" or relationship["physical_reading_resolved"] != "False" or relationship["topdown_channel_certified"] != "False":
        fail("status-family flags mismatch")

    for row in read_csv("negative_controls_step47.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("six_gate_audit_step47.csv"):
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
    print("run_step47.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 47 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 47 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 41 and Step 46 first, then Step 47")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
