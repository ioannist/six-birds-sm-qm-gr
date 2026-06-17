#!/usr/bin/env python3
"""Validate Cluster A Step 46 F48 monopole fork artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "monopole_f48_step46.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "run_step41.py",
    STEPS_DIR / "step45_mode_b_proton_decay_F27_artifacts" / "run_step45.py",
]

REQUIRED_FILES = [
    "monopole_f48_step46.py",
    "breaking_coset_generators_step46.csv",
    "f48_gluing_obstruction_step46.csv",
    "coset_delta_witness_identity_step46.csv",
    "negative_controls_step46.csv",
    "typed_fork_summary_step46.csv",
    "six_gate_audit_step46.csv",
    "generated_vs_input_step46.csv",
    "monopole_f48_output_step46.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step46_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step46.py",
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
    r"\bsolves?\s+the\s+monopole problem\b",
    r"\bsolution\s+to\s+the\s+monopole problem\b",
    r"\bproves?\s+no\s+monopoles\b",
    r"\bno\s+monopoles\s+are\s+proved\b",
    r"\bderive[sd]?\s+absence\s+of\s+monopoles\b",
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
    print(f"run_step46.py: FAIL: {message}", file=sys.stderr)
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
    if "f48_gluing_obstruction" not in logic_region or "charged_pair_count" not in logic_region:
        fail("F48 gluing invariant is not computed in build logic")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step46.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "monopole_f48_output_step46.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 46:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates status")
        if doc.get("conditional_on_clean_separation") is not True:
            fail("conditional clean-separation status missing")
        if doc.get("physical_reading_resolved") is not False:
            fail("physical reading must remain unresolved")
    if output.get("verdict") != "CANDIDATE_SHADOW_VS_BREAKING_FORK_TYPED":
        fail("unexpected Step 46 verdict")
    if output.get("clean_shadow_gluing_obstruction") != 0 or output.get("clean_shadow_monopole_typed") is not False:
        fail("clean/shadow gluing mismatch")
    if output.get("dynamical_breaking_gluing_obstruction", 0) <= 0 or output.get("dynamical_breaking_monopole_typed") is not True:
        fail("dynamical gluing mismatch")
    if output.get("dynamical_breaking_coset_count") != 6:
        fail("expected six dynamical coset generators")
    if output.get("coset_delta_witness_identity") is not True:
        fail("coset/witness identity did not pass")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    obstruction = {row["reading_id"]: row for row in read_csv("f48_gluing_obstruction_step46.csv")}
    clean = obstruction.get("clean_shadow_reading")
    dynamic = obstruction.get("dynamical_breaking_reading")
    if clean is None or dynamic is None:
        fail("missing clean or dynamical gluing row")
    if clean["f48_gluing_obstruction"] != "0" or clean["monopole_typed"] != "False" or clean["realized_coset_generator_count"] != "0":
        fail(f"bad clean gluing row: {clean}")
    if dynamic["f48_gluing_obstruction"] != "3" or dynamic["monopole_typed"] != "True" or dynamic["realized_coset_generator_count"] != "6":
        fail(f"bad dynamical gluing row: {dynamic}")

    identity = read_csv("coset_delta_witness_identity_step46.csv")
    if len(identity) != 2:
        fail("expected two identity rows")
    for row in identity:
        if row["step45_identity_consistent"] != "True" or row["coset_equals_delta_witnesses"] != "True":
            fail(f"identity row failed: {row}")

    coset = read_csv("breaking_coset_generators_step46.csv")
    if len(coset) != 6:
        fail("expected six dynamical coset generators")
    if not all(row["step41_witness_id"] for row in coset):
        fail("coset generator missing Step41 witness id")
    if sorted({row["finite_u1_charge"] for row in coset}) != ["-1", "1"]:
        fail("coset charges should include both orientations")

    for row in read_csv("negative_controls_step46.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("six_gate_audit_step46.csv"):
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
    print("run_step46.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 46 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 46 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 41 and Step 45 first, then Step 46")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
