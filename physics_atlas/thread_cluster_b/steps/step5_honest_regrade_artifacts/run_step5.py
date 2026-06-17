#!/usr/bin/env python3
"""Validate Cluster B Step 5 honest regrade artifacts."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "regrade_diff_step5.md",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step5.py",
]

FORBIDDEN_PATTERNS = [
    r"proves quantum gravity",
    r"solves quantum gravity",
    r"closes QM-GR unconditionally",
    r"discovers a new physical law",
    r"predicts a new constant",
    r"computes the cosmological constant",
    r"derives the value of lambda",
    r"solves the cosmological constant problem",
    r"resolves the singularity",
    r"quantizes gravity",
    r"root_landed[\"']?\s*:\s*true",
    r"frame_transfer_certified[\"']?\s*:\s*true",
]


def fail(message: str) -> None:
    print(f"run_step5.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step5.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_regrade_edits() -> None:
    step1_summary = (THREAD_DIR / "steps/step1_shared_substrate_frame_artifacts/results_summary.md").read_text(
        encoding="utf-8"
    )
    step3_schema = json.loads(
        (THREAD_DIR / "steps/step3_e021_cosmological_constant_artifacts/schema.json").read_text(encoding="utf-8")
    )
    step3_output = json.loads(
        (
            THREAD_DIR
            / "steps/step3_e021_cosmological_constant_artifacts/e021_cosmological_constant_output_step3.json"
        ).read_text(encoding="utf-8")
    )
    step3_summary = (THREAD_DIR / "steps/step3_e021_cosmological_constant_artifacts/results_summary.md").read_text(
        encoding="utf-8"
    )
    step4_tex = (
        THREAD_DIR / "steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex"
    ).read_text(encoding="utf-8")
    step4_rows = read_csv(THREAD_DIR / "steps/step4_consolidated_statement_artifacts/content_classification.csv")
    by_claim = {row["claim_id"]: row for row in step4_rows}

    branch_sentence = "readouts are deliberately INSTANTIATED by branch splits"
    if branch_sentence not in step1_summary:
        fail("R4 branch-split transparency sentence missing from Step 1 summary")
    if branch_sentence not in step4_tex:
        fail("R4 branch-split transparency sentence missing from consolidated statement")

    if "The continuation is ASSIGNED" not in step4_tex:
        fail("R1 assigned-continuation disclaimer missing from consolidated statement")
    e042_row = by_claim.get("e042_planck_continuation")
    if not e042_row:
        fail("Step 4 classification missing e042_planck_continuation row")
    if e042_row["grade"] == "finite-toy-diagnostic":
        fail("Claim 5 is still finite-toy-diagnostic")
    if e042_row["grade"] != "modeled-shape":
        fail("Claim 5 must be modeled-shape")

    for document_name, document in [
        ("Step 3 schema", step3_schema.get("final_verdict", {})),
        ("Step 3 output", step3_output.get("verdict", {})),
    ]:
        if document.get("firm_part_missing_audit_ledger") is not False:
            fail(f"{document_name} still marks firm_part_missing_audit_ledger true")
        if document.get("modeled_p6_ledger_illustrative") is not True:
            fail(f"{document_name} does not mark modeled_p6_ledger_illustrative true")
        if document.get("firm_part_selected_run_readout") is not True:
            fail(f"{document_name} lost firm_part_selected_run_readout")

    required_step3 = [
        "Firm part: selected/run readout on the toy",
        "non-factorization obstruction `4`",
        "descending-control contrast (obstruction `0`)",
        "not a firm audit computed from a coarse map, RG flow, or package dynamics",
    ]
    for snippet in required_step3:
        if snippet not in step3_summary:
            fail(f"Step 3 firm narrowing text missing: {snippet}")

    if "booked UV-to-IR ledger is MODELED/illustrative P6 bookkeeping" not in step4_tex:
        fail("Step 4 does not mark the booked ledger as modeled/illustrative")
    if "NOT a firm audit computed from a coarse map / RG / package dynamics" not in step4_tex:
        fail("Step 4 does not state the ledger is not a firm computed audit")
    if "selected/run toy readout with computed non-factorization obstruction \\(4\\)" not in step4_tex:
        fail("Step 4 does not narrow the firm E021 claim to selected/run non-factorization")

    e021_selected = by_claim.get("e021_selected_nonfactorization")
    e021_ledger = by_claim.get("e021_p6_modeled_ledger")
    if not e021_selected or e021_selected["grade"] != "finite-toy-diagnostic":
        fail("Step 4 selected/run non-factorization row is missing or wrongly graded")
    if not e021_ledger or e021_ledger["grade"] != "modeled-shape":
        fail("Step 4 P6 ledger row is missing or not modeled-shape")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "honest_regrade_applied_validators_pass":
        fail("unexpected Step 5 verdict type")
    if verdict.get("no_new_computation") is not True:
        fail("Step 5 must be marked no_new_computation")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("Step 5 overstates landing or frame transfer")
    fixes = schema.get("applied_fixes", {})
    for key in [
        "R1_e042_continuation_modeled_shape",
        "R2_e021_ledger_modeled_illustrative",
        "R4_branch_split_transparency",
    ]:
        if fixes.get(key) is not True:
            fail(f"accepted fix not marked applied: {key}")


def validate_content_paths() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"content row has no source artifacts: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"absolute source path is not allowed: {source}")
            source_path = THREAD_DIR / source
            if not source_path.exists():
                fail(f"source artifact does not exist: {source}")


def validate_ledgers() -> None:
    checks = [
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step5_honest_regrade"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_EXTERNAL_REVIEW_AFTER_HONEST_REGRADE"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP5_R2_LEDGER_REMODELED"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 5 - Honest Regrade"),
    ]
    for path, needle in checks:
        if not path.exists():
            fail(f"ledger missing: {path}")
        if needle not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {needle}")


def run_prior_validators() -> None:
    validators = [
        THREAD_DIR / "steps/step1_shared_substrate_frame_artifacts/run_step1.py",
        THREAD_DIR / "steps/step2_e042_singularity_resolution_artifacts/run_step2.py",
        THREAD_DIR / "steps/step3_e021_cosmological_constant_artifacts/run_step3.py",
        THREAD_DIR / "steps/step4_consolidated_statement_artifacts/run_step4.py",
    ]
    for validator in validators:
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=validator.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(
                f"{validator.name} failed during Step 5 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def main() -> None:
    validate_required()
    scan_overclaims()
    validate_schema()
    validate_regrade_edits()
    validate_content_paths()
    validate_ledgers()
    run_prior_validators()
    print("run_step5.py: PASS")


if __name__ == "__main__":
    main()
