#!/usr/bin/env python3
"""Validate Cluster A Step 48 content-cascade artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "content_cascade_step48.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "run_step38.py",
]

REQUIRED_FILES = [
    "content_cascade_step48.py",
    "content_rosters_step48.csv",
    "content_classes_step48.csv",
    "content_shadow_scores_step48.csv",
    "content_shadow_survivors_step48.csv",
    "negative_controls_step48.csv",
    "anti_smuggle_self_check_step48.csv",
    "six_gate_audit_step48.csv",
    "typed_content_verdict_step48.csv",
    "generated_vs_input_step48.csv",
    "content_cascade_output_step48.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step48_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step48.py",
]

LOGIC_FORBIDDEN_SNIPPETS = [
    "target roster",
    "target_roster",
    "3 generations",
    "observed Yukawa",
    "common-refinement",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi-as-cosourcing",
    "ψ",
]

OVERCLAIM_PATTERNS = [
    r"\bderive[sd]?\s+the\s+SM\s+content\b",
    r"\bexplains?\s+the\s+Yukawa\s+texture\b",
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
    print(f"run_step48.py: FAIL: {message}", file=sys.stderr)
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
    forbidden_literals = [
        "rank_one_fundxfund:1",
        "rank_one_fundxsinglet:-3",
        "singletxantifund:-4",
        "singletxantifund:2",
        "singletxsinglet:6",
    ]
    for literal in forbidden_literals:
        if literal in logic_region:
            fail(f"build logic contains target content literal: {literal}")
    if "integer_charge_shadow(" not in logic_region:
        fail("content shadow computation missing")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step48.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "content_cascade_output_step48.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 48:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates status")
    if output.get("input_clean_rosters") != 8:
        fail("expected 8 clean input rosters")
    if output.get("distinct_content_classes") != 2:
        fail("expected 2 quotient content classes")
    if output.get("shadow_surviving_classes") != 2 or output.get("shadow_failed_classes") != 0:
        fail("integer charge shadow should not narrow the two content classes")
    if output.get("verdict") != "CONTENT_TYPE_LIMIT":
        fail("unexpected Step 48 verdict")
    if output.get("target_class_survives") is not True or output.get("observed_input_required") is not True:
        fail("target/type-limit status mismatch")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_smuggle_self_check_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    rosters = read_csv("content_rosters_step48.csv")
    classes = read_csv("content_classes_step48.csv")
    survivors = read_csv("content_shadow_survivors_step48.csv")
    if len(rosters) != 8:
        fail(f"expected 8 roster rows, got {len(rosters)}")
    if len(classes) != 2 or len(survivors) != 2:
        fail("expected 2 quotient classes and 2 survivors")
    if sum(1 for row in classes if row["target_class"] == "True") != 1:
        fail("target class should be unique")
    if any(row["integer_charge_shadow_passes"] != "True" for row in classes):
        fail("all quotient classes should pass the tested shadow")
    for row in classes:
        if row["elementary_failure_count"] != "0" or row["composite_failure_count"] != "0":
            fail(f"class has charge-integrality failure: {row}")
    verdict = read_csv("typed_content_verdict_step48.csv")[0]
    if verdict["verdict"] != "CONTENT_TYPE_LIMIT" or verdict["content_type_limit"] != "True":
        fail("typed verdict mismatch")
    if verdict["simulations_excluded_by_design"] != "True":
        fail("E0/simulation exclusion flag missing")
    for row in read_csv("negative_controls_step48.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("anti_smuggle_self_check_step48.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle self-check failed: {row}")
    for row in read_csv("six_gate_audit_step48.csv"):
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
    print("run_step48.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 48 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 48 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 38 first, then Step 48")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
