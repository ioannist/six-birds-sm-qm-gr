#!/usr/bin/env python3
"""Validate Cluster B Step 9 R6 consolidation artifacts."""

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
    "cluster_b_robustness_r6.tex",
    "findings_r6_clusterb.md",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step9.py",
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
    print(f"run_step9.py: FAIL: {message}", file=sys.stderr)
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
        if path.name == "run_step9.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "R6_robustness_battery_consolidated":
        fail("unexpected final verdict type")
    for key in [
        "no_new_computation",
        "claims_sourced",
        "claims_graded",
        "structural_claims_robust_under_declared_battery",
        "modeled_forms_bounded",
    ]:
        if verdict.get(key) is not True:
            fail(f"schema verdict key false: {key}")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates landing or frame transfer")


def validate_statement_text() -> None:
    tex = (ARTIFACT_DIR / "cluster_b_robustness_r6.tex").read_text(encoding="utf-8")
    md = (ARTIFACT_DIR / "findings_r6_clusterb.md").read_text(encoding="utf-8")
    combined = tex + "\n" + md
    required_snippets = [
        "Grade: finite-carrier robustness consolidation",
        "min \\Delta(d4)=3",
        "min \\Delta(d5)=1",
        "uses\\_layer\\_content=True",
        "x_{\\mathrm{next}}=x-\\mathrm{step}\\cdot K/(K+K_{\\mathrm{Planck}})",
        "-0.7821121792445374",
        "3298534883328.0",
        "0.7499999997671694",
        "\\Delta(\\Lambda\\mid \\mathrm{bare\\ UV})=4",
        "relocates to the selection",
        "modeled forms remain bounded",
        "not a frame-transfer certificate",
        "Richer continuous",
    ]
    for snippet in required_snippets:
        if snippet not in combined:
            fail(f"required consolidation snippet missing: {snippet}")
    forbidden_scope_errors = [
        "frame-transfer certificate.",
    ]
    if "This is not a frame-transfer certificate." not in combined:
        fail("explicit no-frame-transfer sentence missing")


def validate_content_classification() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(rows) < 10:
        fail("content_classification.csv has too few rows")
    required_claims = {
        "shared_frame_representation_independence",
        "shared_frame_smuggling_teeth",
        "e042_earned_continuation",
        "e042_lorentzian_stress",
        "e021_selection_relocation",
        "e021_rg_controls",
        "survived_bounded_summary",
        "review_relation",
    }
    seen = {row["claim_id"] for row in rows}
    missing = sorted(required_claims - seen)
    if missing:
        fail(f"missing required claim rows: {missing}")
    for row in rows:
        if not row.get("grade"):
            fail(f"ungraded claim row: {row}")
        if not row.get("claim") or not row.get("source_artifacts"):
            fail(f"claim row missing text or sources: {row}")
        for source in [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]:
            if source.startswith("/"):
                fail(f"absolute source path is not allowed: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_source_steps_exist() -> None:
    sources = [
        "steps/step6_shared_frame_robustness_artifacts/readout_battery_step6.csv",
        "steps/step6_shared_frame_robustness_artifacts/enrichment_step6.csv",
        "steps/step6_shared_frame_robustness_artifacts/controls_step6.csv",
        "steps/step7_e042_earned_continuation_artifacts/earned_continuation_step7.csv",
        "steps/step7_e042_earned_continuation_artifacts/lorentzian_curvature_step7.csv",
        "steps/step7_e042_earned_continuation_artifacts/controls_step7.csv",
        "steps/step8_e021_rg_measure_robustness_artifacts/rg_measure_vacua_step8.csv",
        "steps/step8_e021_rg_measure_robustness_artifacts/nonfactorization_step8.csv",
        "steps/step8_e021_rg_measure_robustness_artifacts/controls_step8.csv",
    ]
    for source in sources:
        if not (THREAD_DIR / source).exists():
            fail(f"required source artifact missing: {source}")


def validate_ledgers() -> None:
    checks = [
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step9_R6_consolidated"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_V2_REPACKAGE_AFTER_R6_STEP9"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP9_R6_CONSOLIDATED"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 9 - R6 Robustness Consolidation"),
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
        THREAD_DIR / "steps/step5_honest_regrade_artifacts/run_step5.py",
        THREAD_DIR / "steps/step6_shared_frame_robustness_artifacts/run_step6.py",
        THREAD_DIR / "steps/step7_e042_earned_continuation_artifacts/run_step7.py",
        THREAD_DIR / "steps/step8_e021_rg_measure_robustness_artifacts/run_step8.py",
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
                f"{validator.name} failed during Step 9 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def main() -> None:
    validate_required()
    scan_overclaims()
    validate_schema()
    validate_statement_text()
    validate_content_classification()
    validate_source_steps_exist()
    validate_ledgers()
    run_prior_validators()
    print("run_step9.py: PASS")


if __name__ == "__main__":
    main()
