#!/usr/bin/env python3
"""Validate Cluster A Step 45 F27 proton-decay fork artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "proton_decay_f27_step45.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "run_step41.py",
]

REQUIRED_FILES = [
    "proton_decay_f27_step45.py",
    "orbit_edges_step45.csv",
    "orbit_components_step45.csv",
    "baryon_descent_obstructions_step45.csv",
    "f27_orbit_descent_step45.csv",
    "delta_witness_identity_step45.csv",
    "negative_controls_step45.csv",
    "typed_fork_summary_step45.csv",
    "six_gate_audit_step45.csv",
    "generated_vs_input_step45.csv",
    "proton_decay_f27_output_step45.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step45_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step45.py",
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
    r"\bsolves?\s+proton decay\b",
    r"\bsolution\s+to\s+proton decay\b",
    r"\bproves?\s+the\s+proton\s+(is\s+)?stable\b",
    r"\bproton\s+stability\s+is\s+proved\b",
    r"\bderive[sd]?\s+baryon[- ]number conservation\b",
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
    print(f"run_step45.py: FAIL: {message}", file=sys.stderr)
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
    if "B_conserved_conditional_stability" not in logic_region or "B_not_conserved_decay_channel" not in logic_region:
        fail("typed consequences are not computed in build logic")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step45.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "proton_decay_f27_output_step45.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 45:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates status")
        if doc.get("conditional_on_clean_separation") is not True:
            fail("conditional clean-separation status missing")
        if doc.get("physical_reading_resolved") is not False:
            fail("physical reading must remain unresolved")
    if output.get("verdict") != "CANDIDATE_SHADOW_VS_BREAKING_FORK_TYPED":
        fail("unexpected Step 45 verdict")
    if output.get("clean_shadow_baryon_obstruction_count") != 0 or output.get("clean_shadow_baryon_descends") is not True:
        fail("clean/shadow B descent mismatch")
    if output.get("dynamical_breaking_baryon_obstruction_count", 0) <= 0 or output.get("dynamical_breaking_baryon_descends") is not False:
        fail("dynamical-breaking B descent mismatch")
    if output.get("dynamical_breaking_delta_witness_count") != 6:
        fail("expected six dynamical witness generators")
    if output.get("xy_delta_witness_identity") is not True:
        fail("X/Y witness identity did not pass")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    descent = {row["reading_id"]: row for row in read_csv("f27_orbit_descent_step45.csv")}
    clean = descent.get("clean_shadow_reading")
    dynamic = descent.get("dynamical_breaking_reading")
    if clean is None or dynamic is None:
        fail("missing clean or dynamical reading row")
    if clean["baryon_readout_descends"] != "True" or clean["baryon_obstruction_count"] != "0" or clean["delta_fact_witness_count"] != "0":
        fail(f"bad clean descent row: {clean}")
    if dynamic["baryon_readout_descends"] != "False" or int(dynamic["baryon_obstruction_count"]) <= 0 or dynamic["delta_fact_witness_count"] != "6":
        fail(f"bad dynamical descent row: {dynamic}")
    if dynamic["orbit_enlarging_generator_count"] != dynamic["delta_fact_witness_count"]:
        fail("dynamical orbit generator count does not equal witness count")

    identity = read_csv("delta_witness_identity_step45.csv")
    if len(identity) != 2 or not all(row["identity_holds"] == "True" for row in identity):
        fail("witness identity rows failed")
    if next(row for row in identity if row["reading_id"] == "dynamical_breaking_reading")["step41_delta_witness_count"] != "6":
        fail("dynamical identity witness count mismatch")

    obstructions = read_csv("baryon_descent_obstructions_step45.csv")
    if len(obstructions) != 3 or any(row["reading_id"] != "dynamical_breaking_reading" for row in obstructions):
        fail("B obstructions must be exactly the dynamical baryon-distinct pairs")

    for row in read_csv("negative_controls_step45.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("six_gate_audit_step45.csv"):
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
    print("run_step45.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 45 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 45 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 41 first, then Step 45")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
