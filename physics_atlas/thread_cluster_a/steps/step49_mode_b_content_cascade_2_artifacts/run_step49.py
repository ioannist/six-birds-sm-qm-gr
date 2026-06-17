#!/usr/bin/env python3
"""Validate Cluster A Step 49 second content-cascade shadow artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "content_cascade_2_step49.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step48_mode_b_content_cascade_artifacts" / "run_step48.py",
]

REQUIRED_FILES = [
    "content_cascade_2_step49.py",
    "yukawa_texture_scores_step49.csv",
    "yukawa_texture_edges_step49.csv",
    "negative_controls_step49.csv",
    "anti_smuggle_self_check_step49.csv",
    "six_gate_audit_step49.csv",
    "typed_content_verdict_step49.csv",
    "generated_vs_input_step49.csv",
    "content_cascade_2_output_step49.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step49_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_grammar_manifest.csv",
    "mode_b_target_lineage.csv",
    "run_step49.py",
]

LOGIC_FORBIDDEN_SNIPPETS = [
    "3 generations",
    "observed Yukawa",
    "common-refinement",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi-as-cosourcing",
]

TARGET_CONTENT_LITERALS = [
    "rank_one_fundxfund:1",
    "rank_one_fundxsinglet:-3",
    "singletxantifund:-4",
    "singletxantifund:2",
    "singletxsinglet:6",
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
    print(f"run_step49.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bool_text(value: str) -> bool:
    return value == "True"


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_logic() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    logic_region = text.split("def write_docs", maxsplit=1)[0]
    shadow_definition_region = text.split("def build", maxsplit=1)[0]
    for snippet in LOGIC_FORBIDDEN_SNIPPETS:
        if snippet in logic_region:
            fail(f"build logic contains forbidden snippet: {snippet}")
    for literal in TARGET_CONTENT_LITERALS:
        if literal in logic_region:
            fail(f"build logic contains target content literal: {literal}")
    if "target_class" in shadow_definition_region or "target_row" in shadow_definition_region:
        fail("shadow definition references target-class metadata")
    if "integer_charge_shadow" in logic_region:
        fail("Step 49 shadow should be distinct from the Step 48 integer-charge shadow")
    if "texture_shadow(" not in logic_region or "yukawa_invariant(" not in logic_region:
        fail("Yukawa texture shadow computation is missing")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step49.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "content_cascade_2_output_step49.json").read_text(encoding="utf-8"))
    for doc in (schema, output):
        if doc.get("step") != 49:
            fail("schema/output step mismatch")
        if doc.get("frame_transfer_certified") or doc.get("new_physics_claim"):
            fail("schema/output overstates status")
    if output.get("reproduced_content_classes") != 2:
        fail("expected two reproduced content classes")
    if output.get("second_content_shadow") != "generic_yukawa_texture_connectivity":
        fail("unexpected second content shadow")
    if output.get("target_class_passes") is not True:
        fail("target class should pass the tested shadow")
    if output.get("shadow_surviving_classes") != 2 or output.get("shadow_failed_classes") != 0:
        fail("second shadow should be blind on the two residual classes")
    if output.get("verdict") != "CONTENT_TYPE_LIMIT" or output.get("content_type_limit") is not True:
        fail("unexpected Step 49 verdict")
    if output.get("two_blind_shadows") is not True or output.get("observed_input_required") is not True:
        fail("two-shadow type-limit status missing")
    if output.get("simulations_excluded_by_design") is not True:
        fail("E0/simulation exclusion flag missing")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_smuggle_self_check_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    scores = read_csv("yukawa_texture_scores_step49.csv")
    if len(scores) != 2:
        fail(f"expected 2 score rows, got {len(scores)}")
    if sum(1 for row in scores if row["target_class"] == "True") != 1:
        fail("target class should be unique")
    for row in scores:
        if row["yukawa_texture_shadow_passes"] != "True":
            fail(f"both residual classes should pass the second shadow: {row}")
        if row["field_count"] != "5" or row["covered_field_count"] != "5":
            fail(f"texture coverage mismatch: {row}")
        if row["edge_count"] != "3" or row["independent_channel_count"] != "3":
            fail(f"expected three independent texture channels: {row}")

    edges = read_csv("yukawa_texture_edges_step49.csv")
    if len(edges) != 6:
        fail(f"expected 6 texture edges, got {len(edges)}")
    edge_counts: dict[str, int] = {}
    for row in edges:
        edge_counts[row["content_class_id"]] = edge_counts.get(row["content_class_id"], 0) + 1
        if row["scalar_charge"] not in {"-3", "3"}:
            fail(f"unexpected scalar charge in texture edge: {row}")
    if sorted(edge_counts.values()) != [3, 3]:
        fail(f"expected three edges per class, got {edge_counts}")

    verdict = read_csv("typed_content_verdict_step49.csv")[0]
    if verdict["verdict"] != "CONTENT_TYPE_LIMIT" or verdict["content_type_limit"] != "True":
        fail("typed verdict mismatch")
    if verdict["two_blind_shadows"] != "True" or verdict["observed_input_required"] != "True":
        fail("typed type-limit flags missing")
    if verdict["simulations_excluded_by_design"] != "True":
        fail("E0/simulation exclusion flag missing in typed verdict")

    negative = read_csv("negative_controls_step49.csv")
    if not any(row["control"] == "underconnected_texture_fails" and bool_text(row["passes"]) for row in negative):
        fail("underconnected negative control did not pass")
    for row in negative:
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("anti_smuggle_self_check_step49.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle self-check failed: {row}")
    for row in read_csv("six_gate_audit_step49.csv"):
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
    print("run_step49.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 49 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 49 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 48 first, then Step 49")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
