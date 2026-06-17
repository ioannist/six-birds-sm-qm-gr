#!/usr/bin/env python3
"""Validate Step 21 structural F24 predicate artifacts."""

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
    "f24_structural_predicates_step21.py",
    "candidate_structures_step21.json",
    "f24_structural_predicate_definitions_step21.csv",
    "f24_structural_predicate_definitions_step21.json",
    "f24_structural_evaluation_step21.csv",
    "f24_structural_discrimination_step21.csv",
    "f24_structural_role_obstruction_step21.csv",
    "f24_structural_statement_step21.tex",
    "fiv_f24_source_record_step21.csv",
    "fiv_f24_source_record_step21.json",
    "f24_structural_output_step21.json",
    "f24_structural_output_step21.txt",
    "step21_results_summary.md",
    "step21_schema.json",
    "content_classification_step21.csv",
    "nonclaim_boundary_step21.md",
    "construction_gate_audit_step21.csv",
    "run_step21.py",
]

BANNED_SELECTOR_SHORTCUTS = [
    "mechanism_flags",
    "expected_family",
    "family_tag",
    "declared_family",
    "tag_imposed",
    "flag_bundle",
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


def check_no_shortcut_words() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step21.py"
        and path.suffix.lower() in {".py", ".json", ".csv", ".md", ".txt", ".tex"}
    ]
    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for banned in BANNED_SELECTOR_SHORTCUTS:
            if banned in text:
                fail(f"selector shortcut token {banned!r} found in {path.name}")


def check_schema_payload() -> None:
    schema = load_json("step21_schema.json")
    payload = load_json("f24_structural_output_step21.json")

    if schema.get("step") != 21:
        fail("schema step is not 21")
    verdict = schema.get("final_verdict", {})
    if verdict.get("L_computed_family") != "BridgeMediatedRole":
        fail("schema L family is not BridgeMediatedRole")
    for key in ["L_unique", "controls_discriminate", "all_eight_families_covered"]:
        if verdict.get(key) is not True:
            fail(f"schema verdict flag {key} is not true")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")

    track = schema.get("track_fields", {})
    for key in ["uses_input_case_names", "uses_input_selector_bundle", "mutual_exclusivity_from_case_names"]:
        if track.get(key) is not False:
            fail(f"schema guard {key} must be false")

    payload_verdict = payload.get("verdict", {})
    if payload_verdict.get("L_computed_family") != "BridgeMediatedRole":
        fail("payload L family is not BridgeMediatedRole")
    for key in ["L_unique", "all_candidates_unique", "all_eight_families_covered"]:
        if payload_verdict.get(key) is not True:
            fail(f"payload verdict flag {key} is not true")
    if set(payload_verdict.get("family_coverage", [])) != FAMILIES:
        fail("payload family coverage is not exactly all eight families")

    guards = payload.get("guardrails", {})
    for key in ["uses_input_case_names", "uses_input_selector_bundle", "mutual_exclusivity_from_case_names"]:
        if guards.get(key) is not False:
            fail(f"payload guard {key} must be false")
    if guards.get("root_landed") is not False:
        fail("payload root_landed must be false")


def check_real_candidate_structures() -> None:
    structures = load_json("candidate_structures_step21.json")
    by_name = {record["name"]: record for record in structures}
    if set(by_name) != set(EXPECTED_SELECTIONS):
        fail("candidate structures do not match expected suite")

    required_structural_fields = {
        "L_candidate_package": ["joint_map", "joint_to_q", "joint_to_role", "joint_audit"],
        "memory_control": ["history_map"],
        "hidden_control": ["latent_map"],
        "budget_control": ["residuals"],
        "scoped_control": ["scope_indices"],
        "coarsened_control": ["coarsened_role_readout"],
        "outside_scope_control": ["in_scope_directions", "named_outside_directions"],
        "blocked_control": ["closure_matrix", "residuals"],
    }
    for name, fields in required_structural_fields.items():
        record = by_name[name]
        for field in fields:
            value = record.get(field)
            if value in (None, [], {}):
                fail(f"{name} lacks structural field {field}")

    for record in structures:
        if "q_map" not in record or "role_map" not in record or "carrier_shape" not in record:
            fail(f"{record['name']} lacks common typed interface fields")


def check_predicates_and_sources() -> None:
    defs = load_csv("f24_structural_predicate_definitions_step21.csv")
    if {row["family"] for row in defs} != FAMILIES:
        fail("structural predicate definitions do not cover all eight families")
    for row in defs:
        criterion = row["structural_criterion"]
        if not criterion.strip():
            fail(f"empty structural criterion for {row['family']}")
        if "computed" not in criterion:
            fail(f"structural criterion for {row['family']} does not state computation")

    source = load_csv("fiv_f24_source_record_step21.csv")
    if {row["family"] for row in source} != FAMILIES:
        fail("FIV source record does not cover all eight families")
    for row in source:
        if "F24 1418-1514" not in row["source_lines"]:
            fail(f"missing F24 source lines for {row['family']}")


def check_evaluation_and_discrimination() -> None:
    role_rows = load_csv("f24_structural_role_obstruction_step21.csv")
    if len(role_rows) != 3:
        fail(f"expected 3 role obstruction witnesses, found {len(role_rows)}")

    evaluation = load_csv("f24_structural_evaluation_step21.csv")
    expected_rows = len(EXPECTED_SELECTIONS) * len(FAMILIES)
    if len(evaluation) != expected_rows:
        fail(f"expected {expected_rows} evaluation rows, found {len(evaluation)}")

    by_candidate: dict[str, list[dict[str, str]]] = {}
    for row in evaluation:
        by_candidate.setdefault(row["candidate"], []).append(row)
        if not row["reason"].strip():
            fail(f"missing structural reason for {row['candidate']} {row['family']}")
    if set(by_candidate) != set(EXPECTED_SELECTIONS):
        fail("evaluation candidates do not match expected suite")

    for candidate, expected_family in EXPECTED_SELECTIONS.items():
        rows = by_candidate[candidate]
        selected = [row["family"] for row in rows if as_bool(row["fires"])]
        if selected != [expected_family]:
            fail(f"{candidate} selected {selected}, expected {expected_family}")

    discrimination = load_csv("f24_structural_discrimination_step21.csv")
    selected_families = set()
    for row in discrimination:
        candidate = row["candidate"]
        expected = EXPECTED_SELECTIONS.get(candidate)
        if expected is None:
            fail(f"unexpected candidate {candidate}")
        if row["selected_family"] != expected:
            fail(f"{candidate} selected {row['selected_family']}, expected {expected}")
        if int(row["selected_count"]) != 1:
            fail(f"{candidate} selected_count is not 1")
        if row["fired_families"] != expected:
            fail(f"{candidate} fired_families is not exactly {expected}")
        selected_families.add(row["selected_family"])
    if selected_families != FAMILIES:
        fail("discrimination suite does not cover all eight families")


def check_no_name_branching_and_gates() -> None:
    script = (BASE / "f24_structural_predicates_step21.py").read_text(encoding="utf-8")
    predicate_region = script.split("def candidate_structures()", 1)[0]
    if re.search(r"candidate\.name\s*==", predicate_region):
        fail("predicate definitions branch on candidate.name")

    gate_rows = load_csv("construction_gate_audit_step21.csv")
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
    if "R_child_E018_after_F24_structural_predicate_classification" not in lineage:
        fail("target lineage missing Step 21 residual")
    if "G_E018_F24_STRUCTURAL_SELECTOR_EXTERNAL_REVIEW_STEP22" not in grammar:
        fail("grammar manifest missing Step 21 review row")
    for marker in [
        "C_STEP21_STRUCTURAL_INPUTS",
        "C_STEP21_NO_SELECTOR_LABELS",
        "C_STEP21_L_REDERIVED_BRIDGE_MEDIATED",
        "C_STEP21_MUTUAL_EXCLUSIVE_EXHAUSTIVE",
        "C_STEP21_CONTROLS_REAL_STRUCTURES",
        "C_STEP21_FAILURE_REASONS_RECORDED",
        "C_STEP21_EXTERNAL_REVIEW",
    ]:
        if marker not in constraints:
            fail(f"constraint ledger missing {marker}")
    if "Step 21 — F24 Structural Selector Construction" not in findings:
        fail("findings file missing Step 21 entry")
    if "re-computes uniquely as `BridgeMediatedRole`" not in findings:
        fail("findings file missing Step 21 L result")


def check_text_guardrails() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step21.py"
        and path.suffix.lower() in {".py", ".json", ".csv", ".md", ".txt", ".tex"}
    ]
    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in text:
                fail(f"forbidden overclaim phrase {phrase!r} found in {path.name}")


def main() -> None:
    check_required_files()
    check_no_shortcut_words()
    check_schema_payload()
    check_real_candidate_structures()
    check_predicates_and_sources()
    check_evaluation_and_discrimination()
    check_no_name_branching_and_gates()
    check_ledgers_and_findings()
    check_text_guardrails()
    print("run_step21.py: validation passed")


if __name__ == "__main__":
    main()
