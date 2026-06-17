#!/usr/bin/env python3
"""Validate Step 15 audit-rung artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
LINEAGE = THREAD_DIR / "mode_b_target_lineage.csv"
GRAMMAR = THREAD_DIR / "mode_b_grammar_manifest.csv"
CONSTRAINTS = THREAD_DIR / "mode_b_constraint_ledger.csv"


REQUIRED_FILES = [
    "build_audit_rung_step15.py",
    "audit_matrices_step15.json",
    "audit_consistency_step15.csv",
    "audit_output_step15.json",
    "audit_output_step15.txt",
    "structural_constraint_step15.md",
    "step15_results_summary.md",
    "step15_schema.json",
    "content_classification_step15.csv",
    "nonclaim_boundary_step15.md",
    "construction_gate_audit_step15.csv",
    "run_step15.py",
]


FORBIDDEN_PHRASES = [
    "proves " + "quantum gravity",
    "solves " + "quantum gravity",
    "quantum gravity solved",
    "derives " + "the proton mass",
    "closes " + "QM-GR unconditionally",
    "discovers " + "a new physical law",
    "predicts " + "a new constant",
    "cross-layer " + "DERIVATION",
    "shadow-to-source " + "promotion",
]


LITERATURE_PATTERNS = [
    ("holography", re.compile(r"\bholography\b", re.I)),
    ("AdS", re.compile(r"(?<![A-Za-z])AdS(?![A-Za-z])")),
    ("CFT", re.compile(r"(?<![A-Za-z])CFT(?![A-Za-z])")),
    ("RT/HRT", re.compile(r"\bRT/HRT\b")),
    ("LQG", re.compile(r"(?<![A-Za-z])LQG(?![A-Za-z])")),
    ("asymptotic safety", re.compile(r"\basymptotic safety\b", re.I)),
    ("spin network", re.compile(r"\bspin network\b", re.I)),
]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\broot_landed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\broute_mismatch_control_passes\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\baudit_trivial_zero\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\baudit_trivial_constant\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bcircular_test_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bone_hot_set_cover_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bliterature_program_terms_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\btarget_layer_inserted\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bendpoint_derivation_claimed\b.{0,20}\btrue\b", re.I | re.S),
]


def fail(message: str) -> None:
    print(f"VALIDATION FAILED: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_required_files() -> None:
    for name in REQUIRED_FILES:
        path = ARTIFACT_DIR / name
        if not path.exists():
            fail(f"missing artifact {name}")
        if path.stat().st_size == 0:
            fail(f"empty artifact {name}")
    for path, label in [(LINEAGE, "lineage"), (GRAMMAR, "grammar"), (CONSTRAINTS, "constraint ledger")]:
        if not path.exists():
            fail(f"missing {label}")


def check_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step15_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 15:
        fail("schema step must be 15")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "audit_coheres_candidate_external_review_required":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("rung_built") is not True:
        fail("schema rung_built must be true")
    if verdict.get("rungs_cohere") is not True:
        fail("schema rungs_cohere must be true")
    if verdict.get("external_review_required") is not True:
        fail("schema must require external review")
    if verdict.get("next_move") != "STEP16_FULL_LADDER_DESCENT":
        fail("schema next move mismatch")
    controls = schema["carrier"]["no_smuggling_controls"]
    for key in [
        "route_mismatch_control_passes",
        "audit_trivial_zero",
        "audit_trivial_constant",
        "circular_test_used",
        "one_hot_set_cover_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
    ]:
        if controls.get(key) is not False:
            fail(f"no-smuggling flag must be false: {key}")
    if controls.get("step14_refinement_loaded") is not True:
        fail("schema must confirm Step-14 refinement loaded")
    residuals = schema["track_fields"]["audit_residuals"]
    if float(residuals["consistent_shared_mode_residual_max"]) > 1e-10:
        fail("consistent shared residual too large")
    if float(residuals["consistent_audit_refinement_commutator_max"]) > 1e-10:
        fail("audit refinement commutator too large")
    if float(residuals["route_mismatch_shared_mode_residual_min"]) <= 0.25:
        fail("route-mismatch residual too small")
    nontriv = schema["track_fields"]["audit_nontriviality"]
    if nontriv.get("nonzero") is not True or nontriv.get("nonconstant") is not True:
        fail("audit must be nonzero and nonconstant")


def check_payload() -> None:
    payload = json.loads((ARTIFACT_DIR / "audit_output_step15.json").read_text(encoding="utf-8"))
    verdict = payload["verdict"]
    for key in [
        "audit_coheres",
        "consistent_audit_passes",
        "route_mismatch_control_fails",
        "audit_commutes_with_refinement",
        "audit_nontrivial",
        "rungs_cohere",
    ]:
        if verdict.get(key) is not True:
            fail(f"payload verdict flag must be true: {key}")
    checks = payload["no_smuggling_check"]
    for key in [
        "route_mismatch_control_passes",
        "audit_trivial_zero",
        "audit_trivial_constant",
        "circular_test_used",
        "one_hot_set_cover_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
    ]:
        if checks.get(key) is not False:
            fail(f"payload no-smuggling flag must be false: {key}")
    if checks.get("step14_refinement_loaded") is not True:
        fail("payload must confirm Step-14 refinement loaded")
    residuals = payload["observed_residuals"]
    if float(residuals["consistent_shared_mode_residual_max"]) > 1e-10:
        fail("payload consistent shared residual too large")
    if float(residuals["consistent_audit_refinement_commutator_max"]) > 1e-10:
        fail("payload audit refinement commutator too large")
    if float(residuals["route_mismatch_shared_mode_residual_min"]) <= 0.25:
        fail("payload route-mismatch residual too small")
    if "agree on the shared currency modes" not in payload.get("structural_constraint", ""):
        fail("payload structural constraint missing shared-mode agreement")


def check_tables() -> None:
    rows = read_csv(ARTIFACT_DIR / "audit_consistency_step15.csv")
    by_case: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)
    for case in ["consistent_audit", "route_mismatch_control"]:
        if case not in by_case:
            fail(f"missing case {case}")
        if len(by_case[case]) != 2:
            fail(f"case {case} must have two levels")
    if any(row["status"] != "passes_candidate" or row["single_audit_exists"] != "True" for row in by_case["consistent_audit"]):
        fail("consistent audit rows must pass")
    if any(row["status"] != "fails_as_control_route_mismatch" or row["single_audit_exists"] != "False" for row in by_case["route_mismatch_control"]):
        fail("route-mismatch control rows must fail")
    if any(float(row["shared_mode_residual"]) <= 0.25 for row in by_case["route_mismatch_control"]):
        fail("route-mismatch shared residual must be large")
    if any(row["audit_nonzero"] != "True" or row["audit_nonconstant"] != "True" for row in by_case["consistent_audit"]):
        fail("consistent audit must be nontrivial")


def check_matrices_and_constraint() -> None:
    matrices = json.loads((ARTIFACT_DIR / "audit_matrices_step15.json").read_text(encoding="utf-8"))
    coefficients = matrices.get("coefficients", {})
    for name in [
        "consistent_qm",
        "consistent_gr",
        "consistent_u",
        "mismatch_qm",
        "mismatch_gr",
        "mismatch_u_attempt",
    ]:
        if name not in coefficients:
            fail(f"missing coefficients {name}")
    for level in ["level_1", "level_2"]:
        if level not in matrices["levels"]:
            fail(f"missing matrix level {level}")
        data = matrices["levels"][level]
        for key in ["A_QM_consistent", "A_GR_consistent", "A_u_consistent", "E_QM", "E_GR", "stable_currency_lift", "audit_lift"]:
            if key not in data:
                fail(f"missing matrix {key} at {level}")
    constraint = (ARTIFACT_DIR / "structural_constraint_step15.md").read_text(encoding="utf-8")
    for phrase in [
        "A_QM|_{d0,d2} = A_GR|_{d0,d2}",
        "A_u^{n+1} L_u = L_A A_u^n",
        "route consistency",
    ]:
        if phrase not in constraint:
            fail(f"structural constraint missing {phrase}")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step15.csv")
    expected = {
        "C1_step14_refinement_loaded",
        "C2_endpoint_audits_structured",
        "C3_single_audit_restricts",
        "C4_shared_overlap_agrees",
        "C5_audit_commutes_with_refinement",
        "C6_route_mismatch_control_fails",
        "C7_nontrivial_audit",
        "C8_no_circular_test",
        "C9_structural_constraint_extracted",
        "C10_next_move_named",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_RUNG3_audit_coherence_candidate" not in lineage_text:
        fail("lineage missing Step 15 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_FULL_LADDER_DESCENT_STEP16" not in grammar_text:
        fail("grammar manifest missing Step 16 row")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP15_AUDIT_OVERLAP_CONSISTENCY",
        "C_STEP15_ROUTE_MISMATCH_CONTROL_FAILS",
        "C_STEP15_AUDIT_COMMUTES_WITH_REFINEMENT",
        "C_STEP15_NONTRIVIAL_AUDIT",
        "C_STEP15_NEXT_FULL_LADDER",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    for path in ARTIFACT_DIR.glob("*"):
        if path.name == "run_step15.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for term, pattern in LITERATURE_PATTERNS:
            if pattern.search(text):
                fail(f"literature-program term in {path.name}: {term}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim/control pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_payload()
    check_tables()
    check_matrices_and_constraint()
    check_gate_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 15 validation passed.")


if __name__ == "__main__":
    main()
