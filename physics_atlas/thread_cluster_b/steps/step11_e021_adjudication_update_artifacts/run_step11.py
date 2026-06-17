#!/usr/bin/env python3
"""Validate Cluster B Step 11 E021 adjudication update artifacts."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_substrate_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_e042_singularity_resolution_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_e021_cosmological_constant_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_consolidated_statement_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_honest_regrade_artifacts" / "run_step5.py",
    STEPS_DIR / "step6_shared_frame_robustness_artifacts" / "run_step6.py",
    STEPS_DIR / "step7_e042_earned_continuation_artifacts" / "run_step7.py",
    STEPS_DIR / "step8_e021_rg_measure_robustness_artifacts" / "run_step8.py",
    STEPS_DIR / "step9_r6_consolidation_artifacts" / "run_step9.py",
    STEPS_DIR / "step10_e021_lambda_selection_adjudication_artifacts" / "run_step10.py",
]

REQUIRED_FILES = [
    "update_diff_step11.md",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step11.py",
]

OVERCLAIM_PATTERNS = [
    r"\bsolves the cosmological constant problem\b",
    r"\bcomputes the cosmological constant\b",
    r"\bderives the value of lambda\b",
    r"\brejects anthropic\b",
    r"\bdisproves anthropic\b",
    r"\bproves quantum gravity\b",
    r"\bsolves quantum gravity\b",
    r"\bquantizes gravity\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
]


def fail(message: str) -> None:
    print(f"run_step11.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def scan_overclaims() -> None:
    paths = [path for path in ARTIFACT_DIR.iterdir() if path.name != "run_step11.py"]
    paths.append(THREAD_DIR / "steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex")
    text_chunks = []
    for path in paths:
        if path.is_file() and path.suffix.lower() in {".md", ".csv", ".json", ".txt", ".tex"}:
            text_chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(text_chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "e021_adjudication_update_applied":
        fail("unexpected final verdict type")
    required_true = [
        "selection_type_adjudicated",
        "lambda_value_remains_open",
        "real_physical_mechanism_remains_open",
        "collapse_not_label_precision_present",
        "unified_decaying_degeneracy_note_present",
        "no_new_computation",
    ]
    for key in required_true:
        if verdict.get(key) is not True:
            fail(f"schema verdict key false: {key}")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame transfer")


def validate_statement_update() -> None:
    statement = (THREAD_DIR / "steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex").read_text(
        encoding="utf-8"
    )
    required_snippets = [
        "Claim 10a",
        "finite-toy-diagnostic / selection-adjudication",
        "10\\to10\\to5\\to1\\to1\\to1",
        "10\\to10\\to10\\to10\\to10\\to10",
        "10\\to10\\to7\\to3\\to2\\to1",
        "framework is not agnostic on E021's selection type",
        "collapse-not-label",
        "not a physical disproof of anthropic reasoning",
        "selection type is adjudicated by Step 10",
        "real physical mechanism implementing the certified selection type",
        "Claim 12",
        "E037 vacuum selection, E043 scale selection, and E021 \\(\\Lambda\\)-selection",
    ]
    for snippet in required_snippets:
        if snippet not in statement:
            fail(f"statement missing required update snippet: {snippet}")
    forbidden_old_punts = [
        "the physical value and selection mechanism for \\(\\Lambda\\)",
        "selection mechanism unknown content",
        "selection mechanism is unknown content",
    ]
    for snippet in forbidden_old_punts:
        if snippet in statement:
            fail(f"statement still contains old unqualified punt: {snippet}")


def validate_step4_classification_update() -> None:
    rows = read_csv(THREAD_DIR / "steps/step4_consolidated_statement_artifacts/content_classification.csv")
    by_id = {row.get("claim_id", ""): row for row in rows}
    required = {
        "e021_lambda_selection_adjudication": "selection-adjudication",
        "unified_decaying_degeneracy_selection": "selection-adjudication",
    }
    for claim_id, classification in required.items():
        row = by_id.get(claim_id)
        if not row:
            fail(f"missing Step 4 classification row: {claim_id}")
        if row.get("grade") != "finite-toy-diagnostic":
            fail(f"{claim_id} must be finite-toy-diagnostic")
        if row.get("classification") != classification:
            fail(f"{claim_id} has wrong classification")
        for source in [source.strip() for source in row.get("source_artifacts", "").split(";") if source.strip()]:
            if source.startswith("/"):
                fail(f"absolute source path in Step 4 classification: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"Step 4 classification source missing: {source}")


def validate_step11_content_classification() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(rows) < 5:
        fail("Step 11 content classification has too few rows")
    for row in rows:
        if not row.get("grade"):
            fail(f"ungraded Step 11 claim row: {row}")
        if row["grade"] not in {"finite-toy-diagnostic", "organizational"}:
            fail(f"unexpected Step 11 grade: {row}")
        if not row.get("claim") or not row.get("source_artifacts"):
            fail(f"Step 11 row missing claim or source: {row}")
        for source in [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]:
            if source.startswith("/"):
                fail(f"absolute Step 11 source path is not allowed: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"Step 11 source artifact missing: {source}")


def validate_ledgers() -> None:
    checks = {
        "mode_b_target_lineage.csv": "R_cluster_b_after_step11_E021_adjudication_update",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_B_STEP11_SELECTION_TYPE_ADJUDICATED",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_B_STEP12_CLUSTER_B_PACKET_REFRESH_OR_REVIEW",
        "findings_cluster_b.md": "Step 11 - E021 Adjudication Update",
    }
    for relative, marker in checks.items():
        path = THREAD_DIR / relative
        if not path.exists():
            fail(f"ledger missing: {relative}")
        if marker not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {marker}")


def run_prior_validators() -> None:
    for validator in STEP_RUNNERS:
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
                f"{validator.name} failed during Step 11 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def main() -> None:
    validate_required_files()
    scan_overclaims()
    validate_schema()
    validate_statement_update()
    validate_step4_classification_update()
    validate_step11_content_classification()
    validate_ledgers()
    run_prior_validators()
    print("run_step11.py: PASS")


if __name__ == "__main__":
    main()
