#!/usr/bin/env python3
"""Validate Cluster A Step 60 Mode-T theorem attempt artifacts."""

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
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "record_stability_structural_theorem_step60.py"
STEP35_BUILD = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
STEP41_BUILD = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "factorization_defect_clean_separation_step41.py"
STEP57_BUILD = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "record_stability_descent_step57.py"

REQUIRED_FILES = [
    "record_stability_structural_theorem_step60.py",
    "frozen_machinery_step60.csv",
    "reduction_check_step60.csv",
    "converse_probe_step60.csv",
    "sharpened_external_lemma_step60.csv",
    "anti_circularity_step60.csv",
    "six_gate_audit_step60.csv",
    "generated_vs_input_step60.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "step60_schema.json",
    "content_classification_step60.csv",
    "nonclaim_boundary_step60.md",
    "step60_results_summary.md",
    "step60_statement.tex",
    "run_step60.py",
]

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step59_mode_b_record_stability_coverage_artifacts" / "run_step59.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives\s+the\s+SM\b",
    r"\bproves\s+clean-separation\s+fundamental\b",
    r"\bproves\s+clean\s+separation\s+fundamental\b",
    r"\btrue,\s*period\b",
    r"\bconstructed_theorem\b",
    r"\bwindow_independent[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step60.py: FAIL: {message}", file=sys.stderr)
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


def step57_requirement_hash() -> str:
    text = STEP57_BUILD.read_text(encoding="utf-8")
    start = text.index("# RECORD_REQUIREMENT_BEGIN")
    end = text.index("# RECORD_REQUIREMENT_END")
    return sha256_text(text[start:end])


def function_hash(path: Path, module_name: str, function_names: list[str]) -> str:
    module = load_module(module_name, path)
    return sha256_text("\n\n".join(inspect.getsource(getattr(module, name)) for name in function_names))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_frozen_hashes() -> None:
    frozen = {row["machinery"]: row for row in read_csv("frozen_machinery_step60.csv")}
    if frozen["Step57_record_requirement"]["sha256"] != step57_requirement_hash():
        fail("Step57 frozen hash mismatch")
    step35_hash = function_hash(
        STEP35_BUILD,
        "step60_validate_s35",
        ["higher_layer_mass_closure", "mass_completion", "scalar_breaks_to_unbroken_u1"],
    )
    if frozen["Step35_base_substrate"]["sha256"] != step35_hash:
        fail("Step35 frozen hash mismatch")
    step41_hash = function_hash(STEP41_BUILD, "step60_validate_s41", ["build_bosons", "compute_delta"])
    if frozen["Step41_factorization_defect"]["sha256"] != step41_hash:
        fail("Step41 frozen hash mismatch")
    for row in frozen.values():
        if row["status"] != "imported_verbatim":
            fail(f"frozen machinery not imported verbatim: {row}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step60_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 60,
        "orientation": "ModeT_theorem_attempt",
        "exit_state": "sharpened_external",
        "verdict": "SHARPENED_EXTERNAL_OPEN_LEMMA_NO_STRUCTURAL_PROOF",
        "structural_proof_grade": "sharpened",
        "carrier_rows": 11990,
        "substrate_capacity_non_CS_count": 0,
        "non_CS_substrate_count": 60,
        "non_CS_capacity_count": 311,
        "six_gates_pass": False,
        "anti_circularity_pass": True,
        "converse_probe_counterexample_found": False,
        "converse_probe_counterexample_in_window": False,
        "converse_probe_counterexample_out_of_window": False,
        "window_independent": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "candidate_law_obligation_2_discharged": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema mismatch {key}: {schema.get(key)} != {value}")


def validate_reduction_and_probe() -> None:
    for row in read_csv("reduction_check_step60.csv"):
        if row["passes"] != "True":
            fail(f"reduction check failed: {row}")
    probes = read_csv("converse_probe_step60.csv")
    if len(probes) != 6:
        fail(f"expected 6 converse probe rows, got {len(probes)}")
    for row in probes:
        if row["counterexample_found"] != "False":
            fail(f"unexpected converse counterexample: {row}")
    inside = next(row for row in probes if row["probe"] == "inside_step59_full_carrier")
    if inside["chiral_closers_checked"] != "11990" or inside["substrate_nonclean_capacity_positive"] != "0":
        fail("inside probe did not reproduce Step59 terminal")
    larger = [row for row in probes if row["outside_reason"] != "inside_declared_carrier"]
    if not larger or not all(int(row["capacity_positive"]) > 0 for row in larger):
        fail("outside probes must have capacity-positive candidates")


def validate_audits() -> None:
    anti = {row["check"]: row for row in read_csv("anti_circularity_step60.csv")}
    for key in (
        "substrate_independently_satisfied_by_non_CS",
        "capacity_independently_satisfied_by_non_CS",
        "conjunction_lands_in_CS_on_carrier",
        "not_extensionally_tautological",
    ):
        if anti.get(key, {}).get("passes") != "True":
            fail(f"anti-circularity check failed: {key}")
    gates = {row["gate"]: row for row in read_csv("six_gate_audit_step60.csv")}
    if gates["uniform_parametric_bound"]["passes"] != "False":
        fail("uniform parametric bound must fail for sharpened_external exit")
    for gate, row in gates.items():
        if gate != "uniform_parametric_bound" and row["passes"] != "True":
            fail(f"unexpected theorem-gate failure: {row}")
    lemma = read_csv("sharpened_external_lemma_step60.csv")
    if len(lemma) != 1 or lemma[0]["lemma_id"] != "L60_record_capacity_leak_exclusion":
        fail("missing sharpened L60 lemma")
    if "not_structurally_proved" not in lemma[0]["status"]:
        fail("lemma must be marked not structurally proved")


def validate_generated_vs_input() -> None:
    statuses = {row["item"]: row["status"] for row in read_csv("generated_vs_input_step60.csv")}
    expected = {
        "Step59_enumeration_result": "input_evidence",
        "structural_reduction": "verified",
        "converse_probe": "computed",
        "structural_proof": "not_constructed",
        "exit_state": "computed",
    }
    for item, status in expected.items():
        if statuses.get(item) != status:
            fail(f"generated-vs-input mismatch for {item}: {statuses.get(item)}")


def validate_ledgers_and_classification() -> None:
    lineage = read_csv("mode_b_target_lineage.csv")
    if len(lineage) != 1 or lineage[0]["status"] != "sharpened_external":
        fail("lineage must record sharpened_external status")
    grammar = read_csv("mode_b_grammar_manifest.csv")
    if len(grammar) != 1 or grammar[0]["exit_state"] != "sharpened_external":
        fail("grammar manifest must record sharpened_external exit")
    rows = read_csv("content_classification_step60.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"required artifacts missing from classification: {missing}")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unknown grade: {row}")
        if row["grade"] == "theorem-grade":
            fail(f"Step60 must not grade any artifact theorem-grade under sharpened_external exit: {row}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step60.py":
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
    validate_reduction_and_probe()
    validate_audits()
    validate_generated_vs_input()
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
    print("run_step60.py: PASS")


if __name__ == "__main__":
    main()
