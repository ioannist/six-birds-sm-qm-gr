#!/usr/bin/env python3
"""Validate Step 20 F24 predicate construction artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]

FAMILIES = {
    "MemoryLayer",
    "HiddenUpstreamRole",
    "BridgeMediatedRole",
    "BudgetedRole",
    "ScopedRole",
    "CoarsenedRole",
    "OutsideRoleScope",
    "BlockedNonClosure",
}

EXPECTED_SELECTIONS = {
    "L_candidate_package": "BridgeMediatedRole",
    "memory_control": "MemoryLayer",
    "hidden_control": "HiddenUpstreamRole",
    "budget_control": "BudgetedRole",
    "scoped_control": "ScopedRole",
    "coarsened_control": "CoarsenedRole",
    "outside_scope_control": "OutsideRoleScope",
    "blocked_control": "BlockedNonClosure",
}

REQUIRED_FILES = [
    "construct_f24_predicates_step20.py",
    "f24_operational_predicates_step20.csv",
    "f24_operational_predicates_step20.json",
    "f24_predicate_evaluation_step20.csv",
    "f24_discrimination_table_step20.csv",
    "f24_role_obstruction_step20.csv",
    "f24_predicate_statement_step20.tex",
    "fiv_f24_source_record_step20.csv",
    "fiv_f24_source_record_step20.json",
    "fiv_f24_source_extract_step20.md",
    "f24_predicate_output_step20.json",
    "f24_predicate_output_step20.txt",
    "step20_results_summary.md",
    "step20_schema.json",
    "content_classification_step20.csv",
    "nonclaim_boundary_step20.md",
    "construction_gate_audit_step20.csv",
    "run_step20.py",
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


def check_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (BASE / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def check_schema_payload() -> None:
    schema = load_json("step20_schema.json")
    payload = load_json("f24_predicate_output_step20.json")

    if schema.get("step") != 20:
        fail("schema step is not 20")
    verdict = schema.get("final_verdict", {})
    if verdict.get("L_selected_family") != "BridgeMediatedRole":
        fail("schema L family is not BridgeMediatedRole")
    if verdict.get("L_unique") is not True:
        fail("schema does not record L as unique")
    if verdict.get("controls_discriminate") is not True:
        fail("schema controls_discriminate is not true")
    if verdict.get("all_eight_families_covered") is not True:
        fail("schema does not record full family coverage")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")

    payload_verdict = payload.get("verdict", {})
    if payload_verdict.get("L_selected_family") != "BridgeMediatedRole":
        fail("payload L family is not BridgeMediatedRole")
    for key in [
        "L_unique",
        "all_controls_classify_as_expected",
        "mutually_exclusive_on_suite",
        "exhaustive_on_suite",
    ]:
        if payload_verdict.get(key) is not True:
            fail(f"payload verdict flag {key} is not true")
    if set(payload_verdict.get("family_coverage", [])) != FAMILIES:
        fail("payload family coverage does not equal all eight families")

    flags = payload.get("no_smuggling_check", {})
    if flags.get("L_case_hardcoded") is not False:
        fail("payload says L case was hardcoded")
    if flags.get("predicates_asserted_without_FIV_read") is not False:
        fail("payload says predicates lacked FIV source read")
    if flags.get("control_misclassified") is not False:
        fail("payload says a control was misclassified")
    if flags.get("root_landed") is not False:
        fail("payload root_landed must be false")


def check_predicates_and_sources() -> None:
    predicates = load_csv("f24_operational_predicates_step20.csv")
    if {row["family"] for row in predicates} != FAMILIES:
        fail("operational predicate table does not contain exactly all eight families")
    for row in predicates:
        if not row["operational_predicate"].strip():
            fail(f"empty operational predicate for {row['family']}")
        if not row["source_lines"].strip():
            fail(f"missing source lines for {row['family']}")

    source_rows = load_csv("fiv_f24_source_record_step20.csv")
    if {row["family"] for row in source_rows} != FAMILIES:
        fail("FIV source record does not cover all eight families")
    for row in source_rows:
        if "1418-1514" not in row["lines_read"]:
            fail(f"F24 lines missing from source row {row['family']}")
        if not row["fiv_laws"].strip() or not row["grounding"].strip():
            fail(f"incomplete FIV grounding for {row['family']}")

    source_json = load_json("fiv_f24_source_record_step20.json")
    if set(source_json.get("families", {}).keys()) != FAMILIES:
        fail("FIV source JSON does not cover all eight families")


def check_role_split_and_evaluation() -> None:
    role_rows = load_csv("f24_role_obstruction_step20.csv")
    if len(role_rows) != 3:
        fail(f"expected role obstruction count 3, found {len(role_rows)}")

    evaluation = load_csv("f24_predicate_evaluation_step20.csv")
    expected_rows = len(EXPECTED_SELECTIONS) * len(FAMILIES)
    if len(evaluation) != expected_rows:
        fail(f"expected {expected_rows} evaluation rows, found {len(evaluation)}")

    by_candidate: dict[str, list[dict[str, str]]] = {}
    for row in evaluation:
        by_candidate.setdefault(row["candidate"], []).append(row)
    if set(by_candidate) != set(EXPECTED_SELECTIONS):
        fail("evaluation candidates do not match expected suite")

    for candidate, expected_family in EXPECTED_SELECTIONS.items():
        rows = by_candidate[candidate]
        selected = [row["family"] for row in rows if as_bool(row["fires"])]
        if selected != [expected_family]:
            fail(f"{candidate} selected {selected}, expected {expected_family}")


def check_discrimination() -> None:
    rows = load_csv("f24_discrimination_table_step20.csv")
    if len(rows) != len(EXPECTED_SELECTIONS):
        fail("discrimination table has wrong row count")
    selected_families = set()
    for row in rows:
        candidate = row["candidate"]
        if candidate not in EXPECTED_SELECTIONS:
            fail(f"unexpected discrimination candidate {candidate}")
        expected = EXPECTED_SELECTIONS[candidate]
        if row["expected_family"] != expected:
            fail(f"{candidate} expected family mismatch")
        if row["selected_family"] != expected:
            fail(f"{candidate} selected {row['selected_family']}, expected {expected}")
        if int(row["selected_count"]) != 1:
            fail(f"{candidate} selected_count is not 1")
        if not as_bool(row["passes"]):
            fail(f"{candidate} discrimination row does not pass")
        selected_families.add(row["selected_family"])
    if selected_families != FAMILIES:
        fail("discrimination suite is not exhaustive over all eight families")


def check_no_hardcoding_and_gates() -> None:
    script = (BASE / "construct_f24_predicates_step20.py").read_text(encoding="utf-8")
    predicate_region = script.split("def candidates()", 1)[0]
    if re.search(r"candidate\.name\s*==", predicate_region):
        fail("predicate definitions branch on candidate.name")

    gate_rows = load_csv("construction_gate_audit_step20.csv")
    if len(gate_rows) != 8:
        fail("expected eight gate-audit rows")
    failed = [row for row in gate_rows if row["status"] != "pass"]
    if failed:
        fail(f"gate audit has non-pass rows: {failed}")


def check_ledgers_and_findings() -> None:
    lineage = (THREAD / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    grammar = (THREAD / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    constraints = (THREAD / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    findings = (THREAD / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "R_child_E018_after_F24_predicate_construction_classification" not in lineage:
        fail("target lineage missing Step 20 residual")
    if "G_E018_F24_SELECTOR_EXTERNAL_REVIEW_STEP21" not in grammar:
        fail("grammar manifest missing Step 20 review row")
    for marker in [
        "C_STEP20_FIV_SOURCE_LINES",
        "C_STEP20_EIGHT_PREDICATES_BUILT",
        "C_STEP20_L_BRIDGE_MEDIATED",
        "C_STEP20_MUTUAL_EXCLUSIVE_EXHAUSTIVE",
        "C_STEP20_CONTROLS_DISCRIMINATE",
        "C_STEP20_EXTERNAL_REVIEW",
    ]:
        if marker not in constraints:
            fail(f"constraint ledger missing {marker}")
    if "Step 20 — F24 Operational Selector Construction" not in findings:
        fail("findings file missing Step 20 entry")
    if "L_candidate_package` selects uniquely as `BridgeMediatedRole`" not in findings:
        fail("findings file missing L family result")


def check_text_guardrails() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step20.py"
        and path.suffix.lower() in {".md", ".json", ".csv", ".txt", ".py", ".tex"}
    ]
    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in text:
                fail(f"forbidden overclaim phrase {phrase!r} found in {path.name}")


def main() -> None:
    check_required_files()
    check_schema_payload()
    check_predicates_and_sources()
    check_role_split_and_evaluation()
    check_discrimination()
    check_no_hardcoding_and_gates()
    check_ledgers_and_findings()
    check_text_guardrails()
    print("run_step20.py: validation passed")


if __name__ == "__main__":
    main()
