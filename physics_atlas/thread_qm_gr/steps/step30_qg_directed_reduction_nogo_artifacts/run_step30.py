#!/usr/bin/env python3
"""Validate Step 30 directed-reduction no-go artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "directed_reduction_nogo_step30.py",
    "factorization_defects_step30.csv",
    "factorization_summary_step30.csv",
    "audit_non_derivability_step30.csv",
    "route_mismatch_step30.csv",
    "directed_reduction_carrier_step30.json",
    "directed_reduction_nogo_output_step30.json",
    "directed_reduction_nogo_output_step30.txt",
    "lemma1_directed_reduction_statement_step30.tex",
    "step30_results_summary.md",
    "step30_schema.json",
    "content_classification_step30.csv",
    "nonclaim_boundary_step30.md",
    "run_step30.py",
]

FORBIDDEN_PHRASES = [
    "qg impossible",
    "proven impossible",
    "metaphysically impossible",
    "proves quantum gravity",
    "solves quantum gravity",
    "derives the proton mass",
    "derived proton mass",
    "closes qm-gr unconditionally",
    "discovers a new physical law",
    "predicts a new constant",
    "unconditional new-physics claim",
    "shadow-to-source promotion without an audited bridge",
]


def fail(message: str) -> None:
    print(f"run_step30.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step30.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    schema = json.loads((ARTIFACT_DIR / "step30_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 30:
        fail("schema step is not 30")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "lemma1_directed_reduction_blocked_in_bounded_grammar":
        fail("unexpected Step 30 verdict")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("bounded_grammar_scope") is not True:
        fail("bounded grammar scope missing")

    output = json.loads((ARTIFACT_DIR / "directed_reduction_nogo_output_step30.json").read_text(encoding="utf-8"))
    out_verdict = output.get("verdict", {})
    if out_verdict.get("lemma_verdict") != "lemma1_directed_reduction_blocked_in_bounded_grammar":
        fail("output verdict mismatch")
    if out_verdict.get("control_factors") is not True:
        fail("genuine-reduction control does not factor")
    if out_verdict.get("control_route_commutes") is not True:
        fail("control route does not commute")

    factor_summary = {row["case"]: row for row in read_csv(ARTIFACT_DIR / "factorization_summary_step30.csv")}
    required_cases = {"q_GR_through_q_QM", "q_QM_through_q_GR", "control_coarse_through_fine"}
    if set(factor_summary) != required_cases:
        fail("factorization summary missing required cases")
    if int(factor_summary["q_GR_through_q_QM"]["defect_count"]) <= 0:
        fail("q_GR through q_QM defect not positive")
    if int(factor_summary["q_QM_through_q_GR"]["defect_count"]) <= 0:
        fail("q_QM through q_GR defect not positive")
    if int(factor_summary["control_coarse_through_fine"]["defect_count"]) != 0:
        fail("vertical-stack control has a factorization defect")
    if factor_summary["control_coarse_through_fine"]["factors"] != "True":
        fail("vertical-stack control is not marked as factoring")

    audit_rows = read_csv(ARTIFACT_DIR / "audit_non_derivability_step30.csv")
    if len(audit_rows) < 6:
        fail("audit non-derivability rows missing")
    for row in audit_rows:
        if float(row["heldout_residual"]) <= 1e-2:
            fail(f"audit held-out residual too small for {row['direction']} {row['target_component']}")

    route_rows = {row["case"]: row for row in read_csv(ARTIFACT_DIR / "route_mismatch_step30.csv")}
    if float(route_rows["qm_gr_directed_completion"]["normalized_route_mismatch"]) <= 1e-2:
        fail("QM/GR route mismatch is not positive")
    if route_rows["qm_gr_directed_completion"]["commutes"] != "False":
        fail("QM/GR route is marked commuting")
    if float(route_rows["vertical_stack_control"]["normalized_route_mismatch"]) > 1e-10:
        fail("vertical-stack control route mismatch is nonzero")
    if route_rows["vertical_stack_control"]["commutes"] != "True":
        fail("vertical-stack control is not marked commuting")

    defect_rows = read_csv(ARTIFACT_DIR / "factorization_defects_step30.csv")
    real_defects = [row for row in defect_rows if row["case"] in {"q_GR_through_q_QM", "q_QM_through_q_GR"}]
    if len(real_defects) < 16:
        fail("factorization defect witnesses are missing")

    script_text = (ARTIFACT_DIR / "directed_reduction_nogo_step30.py").read_text(encoding="utf-8")
    for pattern in [
        r"factorization_defects",
        r"conditional_mean_completion",
        r"fit_heldout",
        r"route_mismatch_for_qm_gr",
    ]:
        if not re.search(pattern, script_text):
            fail(f"script missing computation pattern {pattern}")

    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP30_FACTORIZATION_DEFECTS_COMPUTED",
        "C_STEP30_ROUTE_MISMATCH_COMPUTED",
        "C_STEP30_CONTROL_PASSES",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_directed_reduction_nogo_lemma1" not in lineage:
        fail("target lineage missing Step 30 residual")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 30 — Directed Reduction No-Go Lemma 1" not in findings:
        fail("findings_qm_gr.md missing Step 30 entry")

    print("run_step30.py: PASS")


if __name__ == "__main__":
    main()
