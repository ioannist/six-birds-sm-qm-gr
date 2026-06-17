#!/usr/bin/env python3
"""Validate Cluster A Step 61 single-factor structural theorem artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
STEPS_DIR = ARTIFACT_DIR.parent
BUILD_SCRIPT = ARTIFACT_DIR / "single_factor_clean_separation_theorem_step61.py"
STEP35_BUILD = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
STEP41_BUILD = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "factorization_defect_clean_separation_step41.py"

REQUIRED_FILES = [
    "single_factor_clean_separation_theorem_step61.py",
    "frozen_machinery_step61.csv",
    "converse_probe_step61.csv",
    "single_factor_substrate_exemplars_step61.csv",
    "proof_chain_step61.csv",
    "anti_circularity_step61.csv",
    "six_gate_audit_step61.csv",
    "generated_vs_input_step61.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "step61_schema.json",
    "content_classification_step61.csv",
    "nonclaim_boundary_step61.md",
    "step61_results_summary.md",
    "step61_statement.tex",
    "run_step61.py",
]

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "run_step35.py",
    STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "run_step41.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives\s+the\s+SM\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step61.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def function_hash(path: Path, module_name: str, function_names: list[str]) -> str:
    module = load_module(module_name, path)
    return sha256_text("\n\n".join(inspect.getsource(getattr(module, name)) for name in function_names))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_frozen_hashes() -> None:
    frozen = {row["machinery"]: row for row in read_csv("frozen_machinery_step61.csv")}
    step35 = function_hash(STEP35_BUILD, "step61_validate_s35", ["higher_layer_mass_closure", "mass_completion", "scalar_breaks_to_unbroken_u1"])
    step41 = function_hash(STEP41_BUILD, "step61_validate_s41", ["build_bosons", "compute_delta"])
    if frozen["Step35_base_substrate"]["sha256"] != step35:
        fail("Step35 hash mismatch")
    if frozen["Step35_base_substrate"]["expected_sha256"] != "6a378357c3dea96d4e7a51e54c8dbb94af9785d39cb9622c3469d2f6a6462c06":
        fail("Step35 expected hash mismatch")
    if frozen["Step41_factorization_defect"]["sha256"] != step41:
        fail("Step41 hash mismatch")
    if frozen["Step41_factorization_defect"]["expected_sha256"] != "ed5be4969244ae18279a9b6fc5ba73977fc9bc47fcec81ff3c25e8ad076e19c0":
        fail("Step41 expected hash mismatch")
    for row in frozen.values():
        if row["status"] != "imported_verbatim":
            fail(f"frozen row must be imported_verbatim: {row}")
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ("def higher_layer_mass_closure", "def compute_delta", "def build_bosons"):
        if forbidden in text:
            fail(f"build script reimplements frozen machinery: {forbidden}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step61_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 61,
        "orientation": "ModeT_single_factor_structural_theorem",
        "exit_state": "constructed_theorem",
        "verdict": "SINGLE_FACTOR_CLEAN_SEPARATION_EXCLUSION_CONSTRUCTED",
        "structural_proof_grade": "constructed",
        "window_independent": True,
        "six_gates_pass": True,
        "anti_circularity_pass": True,
        "converse_counterexample_found": False,
        "single_factor_substrate_count": 12,
        "single_factor_clean_count": 0,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": True,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema mismatch {key}: {schema.get(key)} != {value}")


def validate_probe_and_proof() -> None:
    rows = {row["N"]: row for row in read_csv("converse_probe_step61.csv")}
    expected = {
        "2": ("1630", "0", "0"),
        "3": ("85", "0", "0"),
        "4": ("56", "12", "0"),
        "5": ("20", "0", "0"),
        "6": ("20", "0", "0"),
        "7": ("0", "0", "0"),
        "8": ("0", "0", "0"),
    }
    for n, (closers, substrate, clean) in expected.items():
        row = rows.get(n)
        if row is None:
            fail(f"missing probe row N={n}")
        observed = (row["closers_checked"], row["single_factor_substrate_count"], row["single_factor_clean_count"])
        if observed != (closers, substrate, clean):
            fail(f"probe mismatch N={n}: {observed}")
        if row["counterexample_found"] != "False":
            fail(f"unexpected counterexample N={n}")
    exemplars = read_csv("single_factor_substrate_exemplars_step61.csv")
    if len(exemplars) != 1 or exemplars[0]["N"] != "4":
        fail("expected one N=4 anti-vacuity exemplar")
    if exemplars[0]["transition_leak_count"] != "6" or exemplars[0]["delta_witness_count"] != "6":
        fail("N=4 exemplar should have six defect witnesses")
    for row in read_csv("proof_chain_step61.csv"):
        if row["status"] not in {"proved_from_frozen_code", "proved_by_residual_arithmetic", "proved_from_frozen_delta_code", "verified"}:
            fail(f"bad proof status: {row}")


def validate_audits() -> None:
    for file_name in ("anti_circularity_step61.csv", "six_gate_audit_step61.csv"):
        for row in read_csv(file_name):
            if row["passes"] != "True":
                fail(f"audit failed in {file_name}: {row}")
    generated = {row["item"]: row["status"] for row in read_csv("generated_vs_input_step61.csv")}
    for item, status in {
        "Step35_substrate_code": "imported_frozen",
        "Step41_defect_code": "imported_frozen",
        "single_factor_converse_probe": "computed",
        "proof_chain": "constructed",
        "exit_state": "computed",
    }.items():
        if generated.get(item) != status:
            fail(f"generated-vs-input mismatch {item}: {generated.get(item)}")


def validate_ledgers_and_classification() -> None:
    lineage = read_csv("mode_b_target_lineage.csv")
    if len(lineage) != 1 or lineage[0]["status"] != "constructed_theorem":
        fail("lineage must record constructed_theorem")
    grammar = read_csv("mode_b_grammar_manifest.csv")
    if len(grammar) != 1 or grammar[0]["exit_state"] != "constructed_theorem" or grammar[0]["window_independent"] != "True":
        fail("grammar manifest must record constructed theorem and window independence")
    rows = read_csv("content_classification_step61.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"missing classifications: {missing}")
    theorem_rows = [row for row in rows if row["grade"] == "theorem-grade"]
    if not theorem_rows:
        fail("constructed theorem should have theorem-grade proof artifacts")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unknown grade: {row}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step61.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def run_build() -> None:
    result = subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), text=True, capture_output=True)
    if result.returncode != 0:
        fail(f"build failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def run_chain_dependencies() -> None:
    for runner in DEPENDENCY_RUNNERS:
        if runner.exists():
            result = subprocess.run([sys.executable, str(runner), "--self"], cwd=str(runner.parent), text=True, capture_output=True)
            if result.returncode != 0:
                fail(f"dependency validator failed for {runner}:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def validate_all() -> None:
    validate_required_files()
    validate_frozen_hashes()
    validate_schema()
    validate_probe_and_proof()
    validate_audits()
    validate_ledgers_and_classification()
    scan_overclaims()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if args.chain:
        run_chain_dependencies()
        run_build()
    elif not args.self:
        args.self = True
    if args.self:
        validate_all()
    print("run_step61.py: PASS")


if __name__ == "__main__":
    main()
