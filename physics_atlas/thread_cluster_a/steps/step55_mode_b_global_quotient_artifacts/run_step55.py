#!/usr/bin/env python3
"""Validate Cluster A Step 55 global quotient artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "global_quotient_step55.py"
STEP48_GVI = STEPS_DIR / "step48_mode_b_content_cascade_artifacts" / "generated_vs_input_step48.csv"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step48_mode_b_content_cascade_artifacts" / "run_step48.py",
    STEPS_DIR / "step49_mode_b_content_cascade_2_artifacts" / "run_step49.py",
]

REQUIRED_FILES = [
    "global_quotient_step55.py",
    "global_center_scores_step55.csv",
    "step55_schema.json",
    "content_classification_step55.csv",
    "nonclaim_boundary_step55.md",
    "step55_results_summary.md",
    "step55_statement.tex",
    "run_step55.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "generated_vs_input_step55.csv",
    "negative_controls_step55.csv",
    "six_gate_audit_step55.csv",
    "anti_smuggle_self_check_step55.csv",
]

OVERCLAIM_PATTERNS = [
    r"\bderives\s+the\s+hypercharge\b",
    r"\bderives\s+sin\b",
    r"\bderives\s+the\s+standard\s+model\b",
    r"\bgenerates\s+the\s+global\s+gauge\s+group\b",
    r"\bderives/predicts\s+a\s+constant\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bco-sourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

LOGIC_FORBIDDEN_SNIPPETS = [
    "common-refinement-as-QMGR-cosourcing",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi-as-cosourcing",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step55.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name_or_path: str | Path) -> list[dict[str, str]]:
    path = ARTIFACT_DIR / name_or_path if isinstance(name_or_path, str) else name_or_path
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_logic() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    solver_region = text.split("def build", maxsplit=1)[0]
    for snippet in LOGIC_FORBIDDEN_SNIPPETS:
        if snippet in solver_region:
            fail(f"solver logic contains forbidden snippet: {snippet}")
    if "Z6" in solver_region:
        fail("solver logic hard-codes Z6 instead of computing it")
    if "target_class" in solver_region:
        fail("center solver references target metadata")
    required_solver_terms = [
        "phase_exponent(",
        "compute_center_kernel(",
        "triality(",
        "duality(",
        "kernel.add",
    ]
    for term in required_solver_terms:
        if term not in solver_region:
            fail(f"center congruence solver missing term: {term}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step55.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_step50_conventions() -> None:
    rows = read_csv(STEP48_GVI)
    declared = {row["item"]: row["status"] for row in rows}
    for item in ("UNIT_DENOMINATOR=6", "WEAK_SHIFT_UNIT=3", "inherited_step38_scalar_charge_normalization"):
        if declared.get(item) != "input":
            fail(f"missing Step-50 declared input convention in Step48 generated-vs-input: {item}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step55_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 55:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_computation_plus_recognition_landing":
        fail("unexpected orientation")
    expected_centers = {"class_00": "Z6", "class_01": "Z6"}
    if schema.get("per_class_trivially_acting_center") != expected_centers:
        fail(f"unexpected center map: {schema.get('per_class_trivially_acting_center')}")
    if schema.get("sm_class_id") != "class_01" or schema.get("sm_center_recovered_as") != "Z6":
        fail("SM Z6 recovery record mismatch")
    if schema.get("selection_result") != "blind":
        fail("selection result should be blind")
    if schema.get("verdict") != "GLOBAL_QUOTIENT_RECOVERED_SELECTION_BLIND":
        fail("unexpected Step55 verdict")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_smuggle_self_check_pass") is not True:
        fail("schema gate status did not pass")


def validate_scores() -> None:
    scores = read_csv("global_center_scores_step55.csv")
    if len(scores) != 2:
        fail(f"expected two center score rows, got {len(scores)}")
    if {row["content_class_id"] for row in scores} != {"class_00", "class_01"}:
        fail("unexpected content classes in center table")
    if sum(1 for row in scores if row["target_class"] == "True") != 1:
        fail("target class should be unique")
    expected_generators = {
        "class_00": "omega3^2;minus1^1;u1_turn=1/6",
        "class_01": "omega3^1;minus1^1;u1_turn=1/6",
    }
    for row in scores:
        if row["trivially_acting_center_group"] != "Z6":
            fail(f"expected Z6 center for both classes: {row}")
        if row["kernel_order"] != "6" or row["nontrivial_center"] != "True":
            fail(f"kernel order/nontrivial mismatch: {row}")
        if row["generator"] != expected_generators[row["content_class_id"]]:
            fail(f"unexpected generator: {row}")
        elements = row["kernel_elements"].split("|")
        if len(elements) != 6:
            fail(f"expected six kernel elements: {row}")
        evidence_parts = row["per_field_congruence_evidence"].split(";")
        if len(evidence_parts) != 5:
            fail(f"expected five field evidence entries: {row}")


def validate_controls_and_gates() -> None:
    negative = read_csv("negative_controls_step55.csv")
    if not any(row["control"] == "incommensurate_charge_collapses_center" and row["passes"] == "True" and "group=Z1" in row["evidence"] for row in negative):
        fail("incommensurate-charge negative control missing or failed")
    for row in negative:
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("anti_smuggle_self_check_step55.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle self-check failed: {row}")
    for row in read_csv("six_gate_audit_step55.csv"):
        if row["passes"] != "True":
            fail(f"gate failed: {row}")


def validate_generated_vs_input() -> None:
    rows = read_csv("generated_vs_input_step55.csv")
    statuses = {row["item"]: row["status"] for row in rows}
    if statuses.get("content_classes") != "read_from_step48":
        fail("Step55 should read content classes from Step48")
    for item in ("UNIT_DENOMINATOR=6", "WEAK_SHIFT_UNIT=3", "inherited_step38_scalar_charge_normalization"):
        if statuses.get(item) != "input_declared_step50":
            fail(f"Step50 charge convention not declared in generated-vs-input: {item}")
    if statuses.get("hypercharge_pattern") != "input_content_class":
        fail("hypercharge pattern must be recorded as input")
    if statuses.get("trivially_acting_center") != "computed":
        fail("center must be recorded as computed")
    if statuses.get("selection_verdict") != "computed":
        fail("verdict must be recorded as computed")


def validate_classification() -> None:
    rows = read_csv("content_classification_step55.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"required artifacts missing from classification: {missing}")
    required_grades = {
        f"steps/{ARTIFACT_DIR.name}/global_center_scores_step55.csv": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/step55_schema.json": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/step55_results_summary.md": "organizational",
        f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step55.md": "organizational",
        f"steps/{ARTIFACT_DIR.name}/step55_statement.tex": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv": "organizational",
    }
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        source = THREAD_DIR / row["source"]
        if not source.exists():
            fail(f"classification source missing: {row['source']}")
        if row["source"].startswith("/"):
            fail(f"classification source must be thread-relative: {row['source']}")
        if row["artifact"] in required_grades and row["grade"] != required_grades[row["artifact"]]:
            fail(f"misgraded artifact: {row}")


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
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=ARTIFACT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"Step55 rebuild failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_self() -> None:
    validate_required_files()
    validate_build_logic()
    scan_overclaims()
    validate_step50_conventions()
    validate_schema()
    validate_scores()
    validate_controls_and_gates()
    validate_generated_vs_input()
    validate_classification()
    print("run_step55.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step55 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step55 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate dependencies, rebuild Step55, then validate")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
