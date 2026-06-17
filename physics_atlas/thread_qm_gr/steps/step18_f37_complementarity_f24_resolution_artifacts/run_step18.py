#!/usr/bin/env python3
"""Validate Step 18 F37/F24 native classification artifacts."""

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
    "classify_f37_f24_step18.py",
    "f37_joint_quotient_witness_step18.json",
    "f37_commuting_checks_step18.csv",
    "f24_role_obstruction_step18.csv",
    "f24_resolution_cases_step18.csv",
    "fiv_source_record_step18.json",
    "fiv_source_extract_step18.md",
    "native_culmination_output_step18.json",
    "native_culmination_output_step18.txt",
    "step18_results_summary.md",
    "step18_schema.json",
    "content_classification_step18.csv",
    "nonclaim_boundary_step18.md",
    "construction_gate_audit_step18.csv",
    "run_step18.py",
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
    re.compile(r"\bjoint_asserted_with_nonzero_residual\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bzero_f24_cases_selected\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bmultiple_f24_cases_selected\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bf24_criteria_asserted_without_reading_fiv\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bliterature_program_terms_used\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step18_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 18:
        fail("schema step must be 18")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "native_f37_f24_classification_complete":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("F37_verdict") != "not_complementary_on_toy":
        fail("schema F37 verdict mismatch")
    if verdict.get("F24_selected_case") != "BridgeMediatedRole":
        fail("schema F24 case mismatch")
    if verdict.get("external_review_required") is not True:
        fail("schema must require external review")
    controls = schema["carrier"]["no_smuggling_controls"]
    for key in [
        "joint_asserted_with_nonzero_residual",
        "zero_f24_cases_selected",
        "multiple_f24_cases_selected",
        "f24_criteria_asserted_without_reading_fiv",
        "literature_program_terms_used",
        "root_landed",
    ]:
        if controls.get(key) is not False:
            fail(f"schema control flag must be false: {key}")
    if schema["track_fields"].get("FIV_source_read") is not True:
        fail("schema must mark FIV source read")
    f37 = schema["track_fields"]["F37"]
    if float(f37["L_a_after_j_residual"]) > 1e-10 or float(f37["L_b_after_j_residual"]) > 1e-10:
        fail("schema F37 L residuals must be zero")
    if f37.get("L_admissible_joint") is not True:
        fail("schema L must be admissible joint")
    if f37.get("product_control_admissible") is not False:
        fail("schema product control must not be admissible")
    f24 = schema["track_fields"]["F24"]
    if int(f24["selected_case_count"]) != 1:
        fail("schema must select exactly one F24 case")
    if f24["selected_case"] != "BridgeMediatedRole":
        fail("schema selected case mismatch")


def check_payload() -> None:
    payload = json.loads((ARTIFACT_DIR / "native_culmination_output_step18.json").read_text(encoding="utf-8"))
    if payload.get("FIV_source_read") is not True:
        fail("payload must mark FIV source read")
    verdict = payload["verdict"]
    if verdict.get("F37_not_complementary_on_toy") is not True:
        fail("payload F37 verdict must be true")
    if verdict.get("F37_admissible_joint") != "L_joint":
        fail("payload admissible joint mismatch")
    if verdict.get("product_control_commutes") is not True:
        fail("payload product control should commute")
    if verdict.get("product_control_admissible") is not False:
        fail("payload product control must not be admissible")
    if verdict.get("F24_unique_case") is not True:
        fail("payload F24 must be unique")
    if verdict.get("F24_selected_case") != "BridgeMediatedRole":
        fail("payload selected case mismatch")
    if int(payload["role_obstruction_count"]) <= 0:
        fail("role obstruction must be nonempty")
    checks = payload["no_smuggling_check"]
    for key in [
        "joint_asserted_with_nonzero_residual",
        "zero_f24_cases_selected",
        "multiple_f24_cases_selected",
        "f24_criteria_asserted_without_reading_fiv",
        "literature_program_terms_used",
        "root_landed",
    ]:
        if checks.get(key) is not False:
            fail(f"payload control flag must be false: {key}")


def check_tables() -> None:
    f37 = read_csv(ARTIFACT_DIR / "f37_commuting_checks_step18.csv")
    by_joint = {row["joint_name"]: row for row in f37}
    if float(by_joint["L_joint"]["a_after_j_residual"]) > 1e-10:
        fail("L a-after-j residual must be zero")
    if float(by_joint["L_joint"]["b_after_j_residual"]) > 1e-10:
        fail("L b-after-j residual must be zero")
    if by_joint["L_joint"]["admissible_joint"] != "True":
        fail("L joint must be admissible")
    if by_joint["product_control"]["commuting_conditions_hold"] != "True":
        fail("product control should commute")
    if by_joint["product_control"]["admissible_joint"] != "False":
        fail("product control must be non-admissible")

    obstruction = read_csv(ARTIFACT_DIR / "f24_role_obstruction_step18.csv")
    if len(obstruction) != 3:
        fail("role obstruction count must be 3")
    if any(float(row["q_QM_gap"]) > 1e-10 or float(row["role_readout_gap"]) <= 1e-10 for row in obstruction):
        fail("invalid role obstruction witness")

    cases = read_csv(ARTIFACT_DIR / "f24_resolution_cases_step18.csv")
    selected = [row["case"] for row in cases if row["satisfies"] == "True"]
    if selected != ["BridgeMediatedRole"]:
        fail(f"F24 selected cases mismatch: {selected}")
    if len(cases) != 6:
        fail("F24 table must contain six requested cases")


def check_json_artifacts() -> None:
    witness = json.loads((ARTIFACT_DIR / "f37_joint_quotient_witness_step18.json").read_text(encoding="utf-8"))
    for key in ["pi_QM", "pi_GR", "pi_L", "to_qm_from_L", "to_gr_from_L", "pi_product"]:
        if key not in witness["maps"]:
            fail(f"missing witness map {key}")
    source = json.loads((ARTIFACT_DIR / "fiv_source_record_step18.json").read_text(encoding="utf-8"))
    if "F24_lines_read" not in source or "F37_lines_read" not in source:
        fail("source record missing read locations")
    if "does not give a more granular predicate list" not in source.get("F24_source_note", ""):
        fail("source caveat missing")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step18.csv")
    expected = {
        "C1_fiv_source_read",
        "C2_f37_l_commutes",
        "C3_f37_l_admissible",
        "C4_product_control_nonadmissible",
        "C5_f24_role_obstruction",
        "C6_f24_unique_case",
        "C7_f24_selected_bridge_mediated",
        "C8_no_root_landing",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_F37_F24_native_classification" not in lineage_text:
        fail("lineage missing Step 18 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_F37_F24_EXTERNAL_REVIEW_STEP19" not in grammar_text:
        fail("grammar manifest missing Step 19 review row")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP18_FIV_SOURCE_READ",
        "C_STEP18_F37_NOT_COMPLEMENTARY_TOY",
        "C_STEP18_PRODUCT_CONTROL_NONADMISSIBLE",
        "C_STEP18_F24_BRIDGE_MEDIATED",
        "C_STEP18_F24_UNIQUE_CASE",
        "C_STEP18_EXTERNAL_REVIEW",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    for path in ARTIFACT_DIR.glob("*"):
        if path.name == "run_step18.py" or path.is_dir():
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
    check_json_artifacts()
    check_gate_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 18 validation passed.")


if __name__ == "__main__":
    main()
