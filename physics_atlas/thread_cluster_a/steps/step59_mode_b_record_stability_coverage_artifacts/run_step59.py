#!/usr/bin/env python3
"""Validate Cluster A Step 59 record-stability coverage artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "record_stability_coverage_step59.py"
STEP35_BUILD = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
STEP41_BUILD = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "factorization_defect_clean_separation_step41.py"
STEP57_BUILD = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "record_stability_descent_step57.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "run_step33.py",
    STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "run_step35.py",
    STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "run_step41.py",
    STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "run_step57.py",
]

REQUIRED_FILES = [
    "record_stability_coverage_step59.py",
    "record_stability_coverage_scores_step59.csv",
    "record_stability_coverage_by_structure_step59.csv",
    "adversarial_candidates_step59.csv",
    "frozen_machinery_step59.csv",
    "negative_controls_step59.csv",
    "dependency_trace_step59.csv",
    "ablation_step59.csv",
    "stage2_record_fact_step59.csv",
    "anti_smuggle_self_check_step59.csv",
    "six_gate_audit_step59.csv",
    "structural_argument_step59.csv",
    "generated_vs_input_step59.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "step59_schema.json",
    "content_classification_step59.csv",
    "nonclaim_boundary_step59.md",
    "step59_results_summary.md",
    "step59_statement.tex",
    "run_step59.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives\s+clean\s+separation\b",
    r"\bproves\s+clean\s+separation\b",
    r"\bgrounds\s+clean\s+separation\s+unconditionally\b",
    r"\bproves\s+memory\s+implies\s+clean\s+separation\s+for\s+all\s+structures\b",
    r"\bSBT\s+derives\s+the\s+SM\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bpsi-as-cosourcing\b",
    r"\bcommon-refinement-as-QMGR-cosourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step59.py: FAIL: {message}", file=sys.stderr)
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


def validate_frozen_gates() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for required in ("STEP57_BUILD", "STEP35_BUILD", "STEP41_BUILD", "load_module"):
        if required not in text:
            fail(f"build script missing frozen import marker: {required}")
    forbidden_defs = [
        "def record_layer_membership",
        "def higher_layer_mass_closure",
        "def mass_completion",
        "def scalar_breaks_to_unbroken_u1",
        "def compute_delta",
    ]
    for token in forbidden_defs:
        if token in text:
            fail(f"build script reimplements frozen machinery: {token}")
    if re.search(r"(?m)^\s*MIN_RECORD_TOKENS\s*=", text):
        fail("Step59 must not assign MIN_RECORD_TOKENS")

    frozen = {row["machinery"]: row for row in read_csv("frozen_machinery_step59.csv")}
    if frozen["Step57_record_requirement"]["sha256"] != step57_requirement_hash():
        fail("Step57 frozen hash mismatch")
    step35_hash = function_hash(
        STEP35_BUILD,
        "step59_validate_s35",
        ["higher_layer_mass_closure", "mass_completion", "scalar_breaks_to_unbroken_u1"],
    )
    if frozen["Step35_base_substrate"]["sha256"] != step35_hash:
        fail("Step35 frozen hash mismatch")
    step41_hash = function_hash(
        STEP41_BUILD,
        "step59_validate_s41",
        ["build_bosons", "compute_delta"],
    )
    if frozen["Step41_factorization_defect"]["sha256"] != step41_hash:
        fail("Step41 frozen hash mismatch")
    for row in frozen.values():
        if row["status"] != "imported_verbatim":
            fail(f"frozen machinery row not imported_verbatim: {row}")
    for row in read_csv("anti_smuggle_self_check_step59.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle check failed: {row}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step59.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step59_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 59:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_record_stability_coverage":
        fail("unexpected orientation")
    expected_counts = {
        "carrier_rows": 11990,
        "CS_count": 316,
        "non_CS_count": 11674,
        "substrate_count": 376,
        "capacity_count": 339,
        "RS_count": 24,
        "RS_not_CS_count": 0,
        "non_CS_capacity_count": 311,
        "non_CS_substrate_count": 60,
        "non_CS_substrate_capacity_count": 0,
    }
    for key, expected in expected_counts.items():
        if schema.get(key) != expected:
            fail(f"unexpected schema count {key}: {schema.get(key)} != {expected}")
    if schema.get("divergence_witness_exists") is not False:
        fail("divergence witness should be absent")
    if schema.get("adversarial_search_nonvacuous") is not True:
        fail("adversarial search must be nonvacuous")
    if schema.get("structural_argument_grade") != "no_structural_proof_found":
        fail("structural argument should be recorded as enumeration-only")
    if schema.get("verdict") != "ROBUST_COVERAGE_ENUMERATION_ONLY":
        fail("unexpected verdict")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("frozen_gates_pass") is not True:
        fail("schema gate flags did not pass")


def validate_scores() -> None:
    rows = read_csv("record_stability_coverage_scores_step59.csv")
    if len(rows) != 11990:
        fail(f"expected 11990 score rows, got {len(rows)}")
    counts = {
        "CS": sum(1 for row in rows if row["CS_member"] == "True"),
        "non_CS": sum(1 for row in rows if row["CS_member"] != "True"),
        "RS": sum(1 for row in rows if row["RS_member"] == "True"),
        "div": sum(1 for row in rows if row["divergence_witness"] == "True"),
        "non_CS_capacity": sum(1 for row in rows if row["CS_member"] != "True" and row["capacity_passes"] == "True"),
        "non_CS_substrate": sum(1 for row in rows if row["CS_member"] != "True" and row["substrate_passes"] == "True"),
        "non_CS_substrate_capacity": sum(1 for row in rows if row["CS_member"] != "True" and row["substrate_passes"] == "True" and row["capacity_passes"] == "True"),
    }
    expected = {
        "CS": 316,
        "non_CS": 11674,
        "RS": 24,
        "div": 0,
        "non_CS_capacity": 311,
        "non_CS_substrate": 60,
        "non_CS_substrate_capacity": 0,
    }
    for key, value in expected.items():
        if counts[key] != value:
            fail(f"unexpected score count {key}: {counts[key]} != {value}")
    adv = read_csv("adversarial_candidates_step59.csv")
    if len(adv) != 371:
        fail(f"unexpected adversarial candidate table size: {len(adv)}")
    if not any(row["adversarial_capacity_non_CS"] == "True" for row in adv):
        fail("adversarial table must include capacity-positive non-CS rows")
    if not any(row["adversarial_substrate_non_CS"] == "True" for row in adv):
        fail("adversarial table must include substrate-positive non-CS rows")


def validate_structure_counts() -> None:
    rows = {row["dimensions"]: row for row in read_csv("record_stability_coverage_by_structure_step59.csv")}
    required = {"2", "2|2", "2|3", "2|4", "3", "3|3", "3|4", "4", "4|4"}
    if set(rows) != required:
        fail(f"unexpected structures: {sorted(rows)}")
    if rows["4"]["non_CS_substrate_count"] != "12":
        fail("single-factor dim-4 substrate adversarial region should be present")
    if int(rows["2|3"]["RS_count"]) <= 0:
        fail("2|3 should contain record-stable rows")


def validate_controls_and_gates() -> None:
    for file_name in ("negative_controls_step59.csv", "stage2_record_fact_step59.csv", "six_gate_audit_step59.csv"):
        for row in read_csv(file_name):
            if row["passes"] != "True":
                fail(f"{file_name} row failed: {row}")
    for row in read_csv("ablation_step59.csv"):
        if row["load_bearing"] != "True":
            fail(f"ablation should be load-bearing: {row}")
    structural = {row["claim"]: row for row in read_csv("structural_argument_step59.csv")}
    if structural["coverage_status"]["grade"] != "no_structural_proof_found":
        fail("coverage status must not claim proof")
    if structural["near_miss_pattern"]["grade"] != "empirical_on_carrier":
        fail("near-miss pattern must be empirical")


def validate_generated_vs_input() -> None:
    rows = read_csv("generated_vs_input_step59.csv")
    statuses = {row["item"]: row["status"] for row in rows}
    expected = {
        "Step57_record_requirement": "imported_frozen",
        "Step35_base_substrate": "imported_frozen",
        "Step41_defect": "imported_frozen",
        "Step33_corrected_closer_carrier": "rederived",
        "adversarial_non_CS_capacity_region": "computed",
        "divergence_witness_search": "computed",
        "verdict": "computed",
    }
    for item, status in expected.items():
        if statuses.get(item) != status:
            fail(f"generated-vs-input mismatch for {item}: {statuses.get(item)}")


def validate_ledgers() -> None:
    lineage = read_csv("mode_b_target_lineage.csv")
    if len(lineage) != 1:
        fail("expected one lineage row")
    relation = lineage[0]["relation_to_canonical_root"]
    if "super_residual" not in relation or "USER-AUTHORIZED 2026-06-09" not in relation:
        fail("lineage must record user-authorized parent-layer move")
    grammar = read_csv("mode_b_grammar_manifest.csv")
    if len(grammar) != 1 or grammar[0]["new_grammar_declared"] != "True":
        fail("Step59 should declare a coverage grammar")
    if "Step33 corrected closer carrier" not in grammar[0]["carrier"]:
        fail("grammar manifest must name the full Step33 carrier")
    if "adversarial" not in grammar[0]["tracked_object"]:
        fail("grammar manifest must track adversarial search")


def validate_classification() -> None:
    rows = read_csv("content_classification_step59.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"required artifacts missing from classification: {missing}")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unknown classification grade: {row}")
    statement = f"steps/{ARTIFACT_DIR.name}/step59_statement.tex"
    for row in rows:
        if row["artifact"] == statement and row["grade"] != "finite-carrier-diagnostic":
            fail("Step59 statement must be finite-carrier-diagnostic")


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
    validate_frozen_gates()
    validate_schema()
    validate_scores()
    validate_structure_counts()
    validate_controls_and_gates()
    validate_generated_vs_input()
    validate_ledgers()
    validate_classification()
    scan_overclaims()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="validate Step59 only")
    parser.add_argument("--chain", action="store_true", help="rebuild and validate dependencies")
    args = parser.parse_args()
    if args.chain:
        run_chain_dependencies()
        run_build()
    elif not args.self:
        args.self = True
    if args.self:
        validate_all()
    print("run_step59.py: PASS")


if __name__ == "__main__":
    main()
