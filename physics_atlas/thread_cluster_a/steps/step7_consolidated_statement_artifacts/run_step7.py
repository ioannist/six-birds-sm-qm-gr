#!/usr/bin/env python3
"""Validate Cluster A Step 7 consolidation artifacts."""

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
STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_selection_layer_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_p2_selection_constraint_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_e043_scale_selection_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_e009_uv_fiber_artifacts" / "run_step5.py",
    STEPS_DIR / "step6_e043_horn_adjudication_artifacts" / "run_step6.py",
]

REQUIRED_FILES = [
    "cluster_a_consolidated_statement.tex",
    "consolidated_findings_clustera.md",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step7.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bcomputes the number of generations\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy problem\b",
    r"\bpredicts the fermion masses\b",
    r"\bcomputes the cosmological constant\b",
    r"\brejects anthropic\b",
    r"\bdisproves anthropic\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
]

ALLOWED_GRADES = {"frame-signature", "finite-toy-diagnostic", "finite-carrier-diagnostic", "organizational"}


def fail(message: str) -> None:
    print(f"run_step7.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def scan_overclaims() -> None:
    text_chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step7.py":
            continue
        if path.is_file() and path.suffix.lower() in {".tex", ".md", ".csv", ".json", ".txt"}:
            text_chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(text_chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")
    if re.search(r"(?<![A-Za-z0-9_])psi(?![A-Za-z0-9_])|ψ", text):
        fail("forbidden field token appears in consolidation")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "cluster_a_deliverable_v2_review_response_consolidated":
        fail("unexpected final verdict type")
    for key in [
        "finite_carrier_bounded_grade",
        "claims_sourced",
        "claims_graded",
        "selection_construction",
        "single_layer_claim_narrowed_to_block_structured_coupling",
        "selection_type_adjudicated_where_applicable",
        "token_blind_response_included",
        "parameter_sweep_response_included",
        "order_battery_response_included",
        "validator_hardening_included",
        "interpretation_flagged_nonresult",
        "values_and_mechanisms_open",
    ]:
        if verdict.get(key) is not True:
            fail(f"schema verdict key false: {key}")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame transfer")


def validate_statement_text() -> None:
    tex = (ARTIFACT_DIR / "cluster_a_consolidated_statement.tex").read_text(encoding="utf-8")
    md = (ARTIFACT_DIR / "consolidated_findings_clustera.md").read_text(encoding="utf-8")
    combined = tex + "\n" + md
    required = [
        "Grade: finite-carrier bounded-grammar consolidation, v2 review-response packet",
        "not a field-readout pair",
        "R2 & MI artifact and one-layer over-grade tested",
        "obstruction \\(36\\)",
        "E019 \\(21\\), E020 \\(21\\), E043 \\(14\\), E009 \\(14\\), and E037 \\(14\\)",
        "anomaly-freedom is necessary but not sufficient",
        "0.330856",
        "9\\to5\\to4\\to2\\to1\\to1",
        "9\\to9\\to9\\to9\\to9\\to9",
        "obstruction \\(3\\)",
        "6\\to5\\to4\\to2\\to1\\to1",
        "6\\to6\\to6\\to6\\to6\\to6",
        "3\\to2\\to2\\to1\\to1",
        "collapse-not-label",
        "obstruction \\(16\\)",
        "8640",
        "468",
        "structural rank \\(2\\)",
        "\\(0.000\\) bits",
        "\\(0.466\\) bits",
        "2.229304481463",
        "0.035998916880",
        "block-structured",
        "9520",
        "0.306122448980",
        "sharp\\_noncollapse",
        "broad\\_false\\_collapse",
        "204",
        "separation margin is \\(5\\)",
        "non-recursive \\texttt{--self} mode",
        "E021 in Cluster B",
        "10\\to10\\to5\\to1\\to1\\to1",
        "not a physical rejection of anthropic reasoning",
        "Interpretation, Not a Result",
        "not a physics result, not a prediction",
        "does not derive the gauge group",
        "does not close the real physics question",
    ]
    for snippet in required:
        if snippet not in combined:
            fail(f"required statement snippet missing: {snippet}")
    if not re.search(
        r"framework is not agnostic[^.]*\.[^.]*not a physical rejection of anthropic reasoning",
        combined,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        fail("anthropic caveat must appear immediately next to not-agnostic statement")
    sections = [
        "Review Map",
        "Baseline Frame",
        "P2 and P6 Mechanics",
        "Facet Constructions",
        "Review-Response Strengthening",
        "Unified Criterion",
        "Interpretation, Not a Result",
        "Open Obligations",
    ]
    for section in sections:
        if section not in tex:
            fail(f"missing TeX section: {section}")


def validate_content_classification() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(rows) < 10:
        fail("content_classification.csv has too few rows")
    required_claims = {
        "shared_frame",
        "p2_constraint_pruning",
        "p6_decaying_degeneracy",
        "e043_scale_facet",
        "e043_horn_adjudication",
        "e009_uv_fiber",
        "step8_token_blind",
        "step8_mi_induced",
        "step9_factorization_narrowing",
        "step10_parameter_sweep",
        "step11_order_battery",
        "step12_validator_hardening",
        "unified_selection_criterion",
        "interpretation_only",
        "open_obligations",
    }
    seen = {row["claim_id"] for row in rows}
    missing = sorted(required_claims - seen)
    if missing:
        fail(f"missing classification rows: {missing}")
    for row in rows:
        if not row.get("grade"):
            fail(f"ungraded claim row: {row}")
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unexpected grade: {row}")
        if not row.get("claim") or not row.get("source_artifacts"):
            fail(f"row missing claim or source: {row}")
        for source in [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]:
            if source.startswith("/"):
                fail(f"absolute source path is not allowed: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_source_steps_exist() -> None:
    sources = [
        "steps/step1_shared_selection_layer_frame_artifacts/frame_signatures_step1.csv",
        "steps/step2_p2_selection_constraint_artifacts/selection_collapse_step2.csv",
        "steps/step3_p6_decaying_degeneracy_audit_artifacts/degeneracy_refinement_step3.csv",
        "steps/step4_e043_scale_selection_artifacts/scale_nonfactorization_step4.csv",
        "steps/step5_e009_uv_fiber_artifacts/uv_nonfactorization_step5.csv",
        "steps/step6_e043_horn_adjudication_artifacts/adjudication_step6.csv",
        "steps/step8_structural_token_blind_selection_artifacts/structural_survivors_step8.csv",
        "steps/step8_structural_token_blind_selection_artifacts/mi_comparison_step8.csv",
        "steps/step9_facet_factorization_test_artifacts/block_decomposition_step9.csv",
        "steps/step10_adjudication_robustness_sweep_artifacts/operating_point_margin_step10.csv",
        "steps/step11_refinement_order_battery_artifacts/separation_step11.csv",
        "steps/step12_validator_hardening_note.md",
        "steps/run_all_selfcheck.py",
        "../thread_cluster_b/steps/step10_e021_lambda_selection_adjudication_artifacts/results_summary.md",
    ]
    for source in sources:
        if not (THREAD_DIR / source).exists():
            fail(f"required source artifact missing: {source}")


def validate_ledgers() -> None:
    checks = {
        "mode_b_target_lineage.csv": "R_cluster_a_after_step7_consolidated_statement",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_A_STEP7_CONSOLIDATED_DELIVERABLE",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_A_STEP8_EXTERNAL_REVIEW_OR_ROBUSTNESS",
        "findings_cluster_a.md": "Step 7 - Consolidated SM Selection-Layer Statement",
    }
    for relative, marker in checks.items():
        path = THREAD_DIR / relative
        if not path.exists():
            fail(f"ledger missing: {relative}")
        if marker not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {marker}")


def run_prior_validators() -> None:
    for runner in STEP_RUNNERS:
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
            cwd=STEPS_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(
                f"{runner.name} failed during Step 7 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def run_self() -> None:
    validate_required_files()
    scan_overclaims()
    validate_schema()
    validate_statement_text()
    validate_content_classification()
    validate_source_steps_exist()
    validate_ledgers()
    print("run_step7.py: PASS")


def run_chain() -> None:
    run_prior_validators()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 7 artifacts.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self", action="store_true", help="validate only this step's own artifacts (default)")
    mode.add_argument("--chain", action="store_true", help="validate prior steps once, then this step")
    args = parser.parse_args(argv)
    if args.chain:
        run_chain()
    else:
        run_self()


if __name__ == "__main__":
    main()
