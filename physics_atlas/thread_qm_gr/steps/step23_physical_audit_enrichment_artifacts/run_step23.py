#!/usr/bin/env python3
"""Validate Step 23 physical-signature quadratic audit enrichment."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]
TOL = 1e-10

REQUIRED_FILES = [
    "physical_audit_enrichment_step23.py",
    "physical_audit_matrices_step23.json",
    "quadratic_audit_properties_step23.csv",
    "parent_audit_reconciliation_step23.csv",
    "physical_f51_status_step23.csv",
    "physical_audit_statement_step23.tex",
    "physical_audit_output_step23.json",
    "physical_audit_output_step23.txt",
    "step23_results_summary.md",
    "step23_schema.json",
    "content_classification_step23.csv",
    "nonclaim_boundary_step23.md",
    "construction_gate_audit_step23.csv",
    "run_step23.py",
]

FORBIDDEN_PHRASES = [
    "proves quantum gravity",
    "solves quantum gravity",
    "derives the proton mass",
    "closes QM-GR unconditionally",
    "closes QM↔GR unconditionally",
    "discovers a new physical law",
    "predicts a new constant",
    "unconditional new-physics claim",
    "cross-layer derivation",
    "derive across a layer",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(name: str):
    return json.loads((BASE / name).read_text(encoding="utf-8"))


def load_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    fail(f"non-boolean value {value!r}")


def matrix_shape(matrix) -> tuple[int, int]:
    if not isinstance(matrix, list) or not matrix or not all(isinstance(row, list) for row in matrix):
        fail("audit matrix is not a 2D list")
    row_count = len(matrix)
    col_count = len(matrix[0])
    if any(len(row) != col_count for row in matrix):
        fail("audit matrix rows have inconsistent lengths")
    return row_count, col_count


def check_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (BASE / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def check_schema_payload() -> None:
    schema = load_json("step23_schema.json")
    payload = load_json("physical_audit_output_step23.json")
    if schema.get("step") != 23:
        fail("schema step is not 23")
    verdict = schema.get("final_verdict", {})
    if verdict.get("physical_audit_verdict") != "survives_physical_signature_enrichment":
        fail("schema physical audit verdict mismatch")
    if verdict.get("L_physical_audits_compatible") is not True:
        fail("schema says L physical audits are incompatible")
    if verdict.get("incompatible_control_pass") is not False:
        fail("schema says incompatible control passes")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")

    track = schema.get("track_fields", {})
    for key in ["quadratic_forms_used", "qm_form_psd", "parent_quadratic_audit_exists", "subblock_residual_computed"]:
        if track.get(key) is not True:
            fail(f"schema track field {key} is not true")
    if abs(float(track.get("shared_subblock_residual", 1.0))) > TOL:
        fail("schema shared sub-block residual is not zero")
    if float(track.get("incompatible_control_shared_residual", 0.0)) <= TOL:
        fail("schema incompatible control residual is not positive")

    out_verdict = payload.get("verdict", {})
    if out_verdict.get("physical_audit_verdict") != "survives_physical_signature_enrichment":
        fail("payload physical audit verdict mismatch")
    if out_verdict.get("L_physical_audits_compatible") is not True:
        fail("payload says L physical audits are incompatible")
    if out_verdict.get("incompatible_control_pass") is not False:
        fail("payload says incompatible control passes")
    guards = payload.get("guardrails", {})
    for key in ["quadratic_forms_used", "qm_form_psd", "subblock_residual_computed"]:
        if guards.get(key) is not True:
            fail(f"payload guard {key} is not true")
    if guards.get("root_landed") is not False:
        fail("payload root_landed must be false")


def check_matrices_and_properties() -> None:
    matrices = load_json("physical_audit_matrices_step23.json")
    for key in ["A_QM_Born_quadratic", "A_GR_curvature_quadratic", "A_GR_incompatible_control"]:
        if matrix_shape(matrices.get(key)) != (3, 3):
            fail(f"{key} is not a 3x3 quadratic form")
    if matrix_shape(matrices.get("A_L_parent_quadratic")) != (4, 4):
        fail("A_L_parent_quadratic is not a 4x4 parent form")
    if matrices.get("A_L_incompatible_parent") is not None:
        fail("incompatible control unexpectedly has a parent form")

    rows = load_csv("quadratic_audit_properties_step23.csv")
    by_audit = {row["audit"]: row for row in rows}
    qm = by_audit.get("A_QM_Born_quadratic")
    gr = by_audit.get("A_GR_curvature_quadratic")
    bad = by_audit.get("A_GR_incompatible_control")
    if qm is None or gr is None or bad is None:
        fail("quadratic audit properties missing one or more audits")
    if int(qm["dimension"]) != 3 or int(gr["dimension"]) != 3 or int(bad["dimension"]) != 3:
        fail("audit dimension is not 3")
    if not as_bool(qm["symmetric"]) or not as_bool(qm["positive_semidefinite"]):
        fail("QM Born-like form is not symmetric PSD")
    if "Born-like" not in qm["motivation"]:
        fail("QM physical motivation missing")
    if "Curvature" not in gr["motivation"] and "curvature" not in gr["motivation"]:
        fail("GR physical motivation missing")


def check_reconciliation_and_control() -> None:
    rows = load_csv("parent_audit_reconciliation_step23.csv")
    by_case = {row["case"]: row for row in rows}
    l_row = by_case.get("L_physical_quadratic_audits")
    c_row = by_case.get("incompatible_physical_control")
    if l_row is None or c_row is None:
        fail("missing reconciliation rows")
    if abs(float(l_row["shared_subblock_residual"])) > TOL:
        fail("L shared sub-block residual is not zero")
    if not as_bool(l_row["parent_quadratic_audit_exists"]):
        fail("L parent quadratic audit does not exist")
    for key in [
        "parent_restricts_to_qm_residual",
        "parent_restricts_to_gr_residual",
        "qm_quadratic_value_residual",
        "gr_quadratic_value_residual",
    ]:
        if abs(float(l_row[key])) > TOL:
            fail(f"L {key} is not zero")
    if not as_bool(l_row["f51_status_compatible"]):
        fail("L F51 status compatibility is false")

    if float(c_row["shared_subblock_residual"]) <= TOL:
        fail("incompatible control shared sub-block residual is not positive")
    if as_bool(c_row["parent_quadratic_audit_exists"]):
        fail("incompatible control unexpectedly has a parent audit")
    if as_bool(c_row["f51_status_compatible"]):
        fail("incompatible control passes F51 status compatibility")

    status = load_csv("physical_f51_status_step23.csv")
    by_status = {row["case"]: row for row in status}
    if not as_bool(by_status["L_physical_quadratic_audits"]["f51_status_compatible"]):
        fail("physical F51 status table says L is incompatible")
    if as_bool(by_status["incompatible_physical_control"]["f51_status_compatible"]):
        fail("physical F51 status table says incompatible control passes")


def check_gate_audit_ledgers_findings() -> None:
    gate_rows = load_csv("construction_gate_audit_step23.csv")
    if len(gate_rows) != 7:
        fail("expected seven gate-audit rows")
    failed = [row for row in gate_rows if row["status"] != "pass"]
    if failed:
        fail(f"gate audit has non-pass rows: {failed}")

    lineage = (THREAD / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    grammar = (THREAD / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    constraints = (THREAD / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    findings = (THREAD / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "R_child_E018_after_physical_audit_enrichment" not in lineage:
        fail("target lineage missing Step 23 residual")
    if "G_E018_PHYSICAL_AUDIT_ENRICHMENT_EXTERNAL_REVIEW_STEP24" not in grammar:
        fail("grammar manifest missing Step 23 review row")
    for marker in [
        "C_STEP23_QUADRATIC_FORMS_USED",
        "C_STEP23_QM_FORM_PSD",
        "C_STEP23_PHYSICAL_MOTIVATION_DECLARED",
        "C_STEP23_SUBBLOCK_COMPUTED",
        "C_STEP23_PARENT_RESTRICTS",
        "C_STEP23_INCOMPATIBLE_CONTROL_FAILS",
        "C_STEP23_EXTERNAL_REVIEW",
    ]:
        if marker not in constraints:
            fail(f"constraint ledger missing {marker}")
    if "Step 23 — Physical-Signature Quadratic Audit Enrichment" not in findings:
        fail("findings missing Step 23 entry")
    if "physical_audit_verdict = survives_physical_signature_enrichment" not in findings:
        fail("findings missing Step 23 verdict")


def check_text_guardrails() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step23.py"
        and path.suffix.lower() in {".py", ".json", ".csv", ".md", ".txt", ".tex"}
    ]
    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in text:
                fail(f"forbidden overclaim phrase {phrase!r} found in {path.name}")


def main() -> None:
    check_required_files()
    check_schema_payload()
    check_matrices_and_properties()
    check_reconciliation_and_control()
    check_gate_audit_ledgers_findings()
    check_text_guardrails()
    print("run_step23.py: validation passed")


if __name__ == "__main__":
    main()
