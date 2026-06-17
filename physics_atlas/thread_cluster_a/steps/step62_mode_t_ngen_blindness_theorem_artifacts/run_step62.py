#!/usr/bin/env python3
"""Validate Cluster A Step 62 N_gen blindness theorem artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "ngen_blindness_theorem_step62.py"
STEP51_BUILD = STEPS_DIR / "step51_mode_b_ngen_neutrality_artifacts" / "ngen_neutrality_step51.py"

REQUIRED_FILES = [
    "ngen_blindness_theorem_step62.py",
    "frozen_machinery_step62.csv",
    "faithfulness_step62.csv",
    "proof_chain_step62.csv",
    "converse_probe_step62.csv",
    "unit_properties_step62.csv",
    "anti_circularity_step62.csv",
    "six_gate_audit_step62.csv",
    "generated_vs_input_step62.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "step62_schema.json",
    "content_classification_step62.csv",
    "nonclaim_boundary_step62.md",
    "step62_results_summary.md",
    "step62_statement.tex",
    "run_step62.py",
]

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step51_mode_b_ngen_neutrality_artifacts" / "run_step51.py",
]

OVERCLAIM_PATTERNS = [
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\bderives_n_equals_3[\"']?\s*:\s*true\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step62.py: FAIL: {message}", file=sys.stderr)
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


def source_hash(functions: list[Any]) -> str:
    return sha256_text("\n\n".join(inspect.getsource(function) for function in functions))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_frozen_hashes() -> None:
    s51 = load_module("step62_validate_s51", STEP51_BUILD)
    unit_functions = [
        s51.parse_content_key,
        s51.selected_generation_fields,
        s51.weak_dimension,
        s51.color_dimension,
        s51.color_cubic_index,
        s51.one_unit_anomalies,
        s51.cp_phase_count,
    ]
    expected = {
        "Step51_closure_row": source_hash([s51.closure_row]),
        "Step51_unit_builder_and_cp": source_hash(unit_functions),
    }
    rows = {row["machinery"]: row for row in read_csv("frozen_machinery_step62.csv")}
    for machinery, expected_hash in expected.items():
        row = rows.get(machinery)
        if row is None:
            fail(f"missing frozen machinery row: {machinery}")
        if row["sha256"] != expected_hash:
            fail(f"hash mismatch for {machinery}")
        if row["status"] != "imported_verbatim":
            fail(f"frozen row should be imported_verbatim: {row}")
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "def closure_row" in text:
        fail("Step62 must not reimplement closure_row")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step62_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 62,
        "orientation": "ModeT_ngen_blindness_theorem",
        "exit_state": "constructed_theorem",
        "verdict": "N_GEN_BLINDNESS_CONSTRUCTED_FOR_ALL_N_GE_1",
        "structural_proof_grade": "constructed",
        "window_independent": True,
        "six_gates_pass": True,
        "anti_circularity_pass": True,
        "even_doublet_hypothesis_load_bearing": True,
        "odd_doublet_control_is_N_sensitive": True,
        "sm_unit_all_active_probe_passes": True,
        "sm_unit_all_active_same_gate_status": True,
        "derives_n_equals_3": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": True,
        "unit_su2_doublet_count": 4,
        "unit_anomaly_free": True,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema mismatch {key}: {schema.get(key)} != {value}")


def validate_probe() -> None:
    rows = read_csv("converse_probe_step62.csv")
    sm = [row for row in rows if row["unit_label"] == "sm_unit"]
    odd = [row for row in rows if row["unit_label"] == "odd_doublet_control"]
    if [int(row["N"]) for row in sm] != [0, 1, 2, 3, 4, 5, 6, 7, 8, 20, 1000]:
        fail("SM probe N values mismatch")
    for row in sm:
        n_value = int(row["N"])
        if n_value == 0:
            if row["full_chain_passes"] != "False":
                fail("N=0 should fail the nonempty full chain")
            continue
        if row["full_chain_passes"] != "True" or row["same_gate_status_as_N1"] != "True":
            fail(f"SM active probe row should pass and match N=1: {row}")
    odd_statuses = {row["full_chain_passes"] for row in odd}
    if odd_statuses != {"False", "True"}:
        fail(f"odd-doublet control should be N-sensitive: {odd_statuses}")
    for row in odd:
        n_value = int(row["N"])
        expected_witten = "True" if n_value % 2 == 0 else "False"
        if row["witten_even"] != expected_witten:
            fail(f"odd control Witten parity mismatch: {row}")
    units = {row["unit_label"]: row for row in read_csv("unit_properties_step62.csv")}
    if units["sm_unit"]["su2_doublet_count"] != "4":
        fail("SM unit doublet count should be 4")
    if units["odd_doublet_control"]["su2_doublet_count"] != "1":
        fail("odd control doublet count should be 1")


def validate_faithfulness_and_audits() -> None:
    for file_name in ("faithfulness_step62.csv", "anti_circularity_step62.csv", "six_gate_audit_step62.csv"):
        for row in read_csv(file_name):
            if row["passes"] != "True":
                fail(f"{file_name} row failed: {row}")
    for row in read_csv("proof_chain_step62.csv"):
        if row["status"] not in {"proved_from_frozen_closure_row", "proved_by_arithmetic"}:
            fail(f"bad proof-chain status: {row}")
    generated = {row["item"]: row["status"] for row in read_csv("generated_vs_input_step62.csv")}
    expected = {
        "Step51_closure_row": "imported_frozen",
        "Step51_unit_builder_and_cp": "imported_frozen",
        "faithfulness_to_Step33_corrected": "checked",
        "SM_unit_probe": "computed",
        "odd_doublet_control": "computed",
        "exit_state": "computed",
    }
    for item, status in expected.items():
        if generated.get(item) != status:
            fail(f"generated-vs-input mismatch for {item}: {generated.get(item)}")


def validate_ledgers_and_classification() -> None:
    lineage = read_csv("mode_b_target_lineage.csv")
    if len(lineage) != 1 or lineage[0]["status"] != "constructed_theorem":
        fail("lineage must record constructed_theorem")
    grammar = read_csv("mode_b_grammar_manifest.csv")
    if len(grammar) != 1 or grammar[0]["exit_state"] != "constructed_theorem" or grammar[0]["window_independent"] != "True":
        fail("grammar manifest must record constructed theorem")
    rows = read_csv("content_classification_step62.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"missing classifications: {missing}")
    if not any(row["grade"] == "theorem-grade" for row in rows):
        fail("constructed theorem should include theorem-grade proof artifacts")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unknown grade: {row}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step62.py":
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
    validate_probe()
    validate_faithfulness_and_audits()
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
    print("run_step62.py: PASS")


if __name__ == "__main__":
    main()
