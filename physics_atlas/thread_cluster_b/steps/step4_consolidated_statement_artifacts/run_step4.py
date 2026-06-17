#!/usr/bin/env python3
"""Validate Cluster B Step 4 consolidation artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "cluster_b_consolidated_statement.tex",
    "consolidated_findings_clusterb.md",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step4.py",
]

ALLOWED_GRADES = {
    "frame-signature",
    "finite-toy-diagnostic",
    "modeled-shape",
    "contested-reading",
    "organizational",
}

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
    print(f"run_step4.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def truth(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def validate_required() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step4.py":
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
    if verdict.get("type") != "cluster_b_deliverable_consolidated_for_external_review":
        fail("unexpected final verdict type")
    for key in ["finite_carrier_bounded_grade", "claims_sourced", "claims_graded", "per_edge_honesty_flags_present"]:
        if not verdict.get(key):
            fail(f"schema verdict key false: {key}")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame transfer")


def validate_statement_text() -> None:
    tex = (ARTIFACT_DIR / "cluster_b_consolidated_statement.tex").read_text(encoding="utf-8")
    md = (ARTIFACT_DIR / "consolidated_findings_clusterb.md").read_text(encoding="utf-8")
    combined = tex + "\n" + md
    required_snippets = [
        "Grade: finite-carrier bounded-grammar consolidation",
        "Grade: frame-signature",
        "Grade: finite-toy-diagnostic",
        "Grade: modeled-shape",
        "Grade: contested-reading",
        "toy ratio",
        "not the physical 120-order",
        "The non-descending \\(d4_{\\mathrm{subplanck}}\\) / \\(d5_{\\mathrm{vacuum}}\\) readouts are deliberately INSTANTIATED by branch splits",
        "The continuation is ASSIGNED",
        "NOT derived from a constraint or evolution law",
        "booked UV-to-IR ledger is MODELED/illustrative P6 bookkeeping",
        "NOT a firm audit computed from a coarse map / RG / package dynamics",
        "selected/run toy readout with computed non-factorization obstruction \\(4\\)",
        "saturating form",
        "modeled",
        "contested and casting-dependent",
        "External frame-transfer review remains",
    ]
    for snippet in required_snippets:
        if snippet not in combined:
            fail(f"required honesty/grade snippet missing: {snippet}")
    for section in [
        "Shared-Substrate Frame",
        "E042: Typed Boundary",
        "E021: Audited Selected/Run Vacuum Readout",
        "Unifying Dissolution",
        "Open Obligations",
    ]:
        if section not in tex:
            fail(f"required TeX section missing: {section}")


def validate_content_classification() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(rows) < 8:
        fail("content_classification.csv has too few claim rows")
    by_id = {row.get("claim_id", ""): row for row in rows}
    e042_cont = by_id.get("e042_planck_continuation")
    if not e042_cont:
        fail("missing e042_planck_continuation classification row")
    if e042_cont.get("grade") == "finite-toy-diagnostic":
        fail("Claim 5/E042 continuation is still overgraded as finite-toy-diagnostic")
    if e042_cont.get("grade") != "modeled-shape":
        fail("Claim 5/E042 continuation must be graded modeled-shape")
    e021_selected = by_id.get("e021_selected_nonfactorization")
    if not e021_selected or e021_selected.get("grade") != "finite-toy-diagnostic":
        fail("E021 selected/run non-factorization must remain finite-toy-diagnostic")
    e021_ledger = by_id.get("e021_p6_modeled_ledger")
    if not e021_ledger or e021_ledger.get("grade") != "modeled-shape":
        fail("E021 UV-to-IR ledger must be graded modeled-shape")
    seen_grades = set()
    for row in rows:
        grade = row.get("grade", "")
        if not grade:
            fail(f"ungraded claim row: {row}")
        if grade not in ALLOWED_GRADES:
            fail(f"unexpected grade {grade!r} in row {row.get('claim_id')}")
        seen_grades.add(grade)
        if not row.get("claim") or not row.get("source_artifacts"):
            fail(f"claim row missing text or source: {row}")
        for source in [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]:
            if source.startswith("/"):
                fail(f"absolute source path is not allowed: {source}")
            source_path = THREAD_DIR / source
            if not source_path.exists():
                fail(f"source artifact does not exist: {source}")
    for required_grade in ["frame-signature", "finite-toy-diagnostic", "modeled-shape", "contested-reading"]:
        if required_grade not in seen_grades:
            fail(f"required grade absent from classification: {required_grade}")


def validate_source_outputs_still_passed() -> None:
    checks = [
        THREAD_DIR / "steps" / "step1_shared_substrate_frame_artifacts" / "shared_substrate_frame_output_step1.json",
        THREAD_DIR / "steps" / "step2_e042_singularity_resolution_artifacts" / "e042_singularity_resolution_output_step2.json",
        THREAD_DIR / "steps" / "step3_e021_cosmological_constant_artifacts" / "e021_cosmological_constant_output_step3.json",
    ]
    for path in checks:
        if not path.exists():
            fail(f"missing source output JSON: {path}")
        text = path.read_text(encoding="utf-8")
        if '"root_landed": true' in text or '"frame_transfer_certified": true' in text:
            fail(f"source output overstates landing/frame transfer: {path}")


def validate_ledgers() -> None:
    checks = [
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step4_consolidated_deliverable"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_EXTERNAL_REVIEW_AFTER_STEP4"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP4_CLAIMS_GRADED_AND_SOURCED"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 4 - Consolidated Cluster B Statement"),
    ]
    for path, needle in checks:
        if not path.exists():
            fail(f"ledger missing: {path}")
        if needle not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {needle}")


def main() -> None:
    validate_required()
    scan_overclaims()
    validate_schema()
    validate_statement_text()
    validate_content_classification()
    validate_source_outputs_still_passed()
    validate_ledgers()
    print("run_step4.py: PASS")


if __name__ == "__main__":
    main()
