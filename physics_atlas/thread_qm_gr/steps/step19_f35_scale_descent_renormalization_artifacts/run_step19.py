#!/usr/bin/env python3
"""Validate Step 19 F35 scale descent artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]

REQUIRED_FILES = [
    "scale_descent_step19.py",
    "scale_structure_step19.json",
    "f35_scale_descent_step19.csv",
    "obstruction_witnesses_step19.csv",
    "fiv_f35_source_record_step19.json",
    "fiv_f35_source_extract_step19.md",
    "scale_descent_output_step19.json",
    "scale_descent_output_step19.txt",
    "step19_results_summary.md",
    "step19_schema.json",
    "content_classification_step19.csv",
    "nonclaim_boundary_step19.md",
    "construction_gate_audit_step19.csv",
    "run_step19.py",
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

LITERATURE_PROGRAM_TERMS = [
    "holography",
    "holographic",
    "AdS",
    "CFT",
    "LQG",
    "spin-network",
    "spin network",
    "asymptotic safety",
    "causal set",
    "string theory",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_json(name: str) -> dict:
    return json.loads((BASE / name).read_text())


def load_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    fail(f"non-boolean CSV value {value!r}")


def check_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (BASE / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def check_schema_and_payload() -> None:
    schema = load_json("step19_schema.json")
    payload = load_json("scale_descent_output_step19.json")

    if schema.get("step") != 19:
        fail("schema step is not 19")
    verdict = schema.get("final_verdict", {})
    if verdict.get("F35_verdict") != "renormalizes_on_toy":
        fail("schema F35 verdict is not renormalizes_on_toy")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("external_review_required") is not True:
        fail("external review flag must be true")

    carrier_flags = schema.get("carrier", {}).get("no_smuggling_controls", {})
    if carrier_flags.get("f35_source_read") is not True:
        fail("schema does not record F35 source read")
    if carrier_flags.get("non_descending_control_descends") is not False:
        fail("schema says the non-descending control descends")
    if carrier_flags.get("O_n_computed_without_coarsening") is not False:
        fail("schema says O_n was computed without coarsening")
    if carrier_flags.get("literature_program_terms_used") is not False:
        fail("schema says literature-program terms were used")

    payload_verdict = payload.get("verdict", {})
    if payload_verdict.get("F35_verdict") != "renormalizes_on_toy":
        fail("payload F35 verdict is not renormalizes_on_toy")
    if payload_verdict.get("joint_law_renormalizes") is not True:
        fail("payload says joint law does not renormalize")
    if payload_verdict.get("non_descending_control_fails") is not True:
        fail("payload says non-descending control does not fail")

    payload_flags = payload.get("no_smuggling_check", {})
    if payload_flags.get("non_descending_control_descends") is not False:
        fail("payload says non-descending control descends")
    if payload_flags.get("O_n_computed_without_coarsening") is not False:
        fail("payload says O_n was computed without coarsening")
    if payload_flags.get("f35_source_read") is not True:
        fail("payload does not record F35 source read")


def check_f35_tables() -> None:
    rows = load_csv("f35_scale_descent_step19.csv")
    if len(rows) != 4:
        fail(f"expected 4 F35 rows, found {len(rows)}")

    joint_rows = [row for row in rows if row["law"] == "joint_law"]
    control_rows = [row for row in rows if row["law"] == "non_descending_control"]
    if len(joint_rows) != 2 or len(control_rows) != 2:
        fail("expected two joint rows and two control rows")

    for row in rows:
        if not as_bool(row["coarsening_used"]):
            fail(f"coarsening was not used for {row['law']} {row['scale_step']}")

    for row in joint_rows:
        if int(row["obstruction_count"]) != 0:
            fail(f"joint law has O_n obstruction at {row['scale_step']}")
        if int(row["fiber_violation_count"]) != 0:
            fail(f"joint law has c-fiber violation at {row['scale_step']}")
        if not as_bool(row["descends_to_Qn"]):
            fail(f"joint law does not descend at {row['scale_step']}")
        if not as_bool(row["renormalizes_to_next"]):
            fail(f"joint law does not renormalize at {row['scale_step']}")
        if not as_bool(row["f35_pass"]):
            fail(f"joint law F35 row failed at {row['scale_step']}")

    if all(as_bool(row["f35_pass"]) for row in control_rows):
        fail("non-descending control passed every F35 row")
    if not any(int(row["obstruction_count"]) > 0 for row in control_rows):
        fail("non-descending control has no O_n obstruction")
    if not any(int(row["fiber_violation_count"]) > 0 for row in control_rows):
        fail("non-descending control has no c-fiber violation")

    witnesses = load_csv("obstruction_witnesses_step19.csv")
    if not witnesses:
        fail("obstruction witness table is empty")
    witness_kinds = {row["kind"] for row in witnesses if row["law"] == "non_descending_control"}
    if not {"fiber", "O_n"}.issubset(witness_kinds):
        fail("control witnesses must include both fiber and O_n rows")


def check_source_and_scale_structure() -> None:
    source = load_json("fiv_f35_source_record_step19.json")
    if source.get("F35_lines_read") != "6470-6523":
        fail("F35 source line record changed or missing")
    if "constant on c-fibers" not in source.get("source_statement", ""):
        fail("F35 source statement does not include c-fiber criterion")

    structure = load_json("scale_structure_step19.json")
    labels = structure.get("quotient_labels", {})
    if set(labels) != {"Q1_fine16", "Q2_mid8", "Q3_coarse4"}:
        fail("scale quotient labels are incomplete")
    matrices = structure.get("coarsening_matrices", {})
    if set(matrices) != {"c1_Q1_to_Q2", "c2_Q2_to_Q3"}:
        fail("coarsening matrices are incomplete")
    laws = structure.get("law_values", {})
    if set(laws) != {"joint_law", "non_descending_control"}:
        fail("law values missing joint or control law")


def check_gate_audit_and_ledgers() -> None:
    gate_rows = load_csv("construction_gate_audit_step19.csv")
    if len(gate_rows) != 7:
        fail("expected seven Step 19 gate rows")
    failed = [row for row in gate_rows if row["status"] != "pass"]
    if failed:
        fail(f"gate audit has non-pass rows: {failed}")

    lineage = (THREAD / "mode_b_target_lineage.csv").read_text()
    grammar = (THREAD / "mode_b_grammar_manifest.csv").read_text()
    constraints = (THREAD / "mode_b_constraint_ledger.csv").read_text()
    if "R_child_E018_after_F35_scale_descent_classification" not in lineage:
        fail("target lineage missing Step 19 residual")
    if "G_E018_F35_EXTERNAL_REVIEW_STEP20" not in grammar:
        fail("grammar manifest missing Step 19 review row")
    for marker in [
        "C_STEP19_F35_SOURCE_READ",
        "C_STEP19_SCALE_QUOTIENTS_BUILT",
        "C_STEP19_JOINT_LAW_RENORMALIZES_TOY",
        "C_STEP19_CONTROL_FAILS_F35",
        "C_STEP19_COARSENING_USED",
        "C_STEP19_EXTERNAL_REVIEW",
    ]:
        if marker not in constraints:
            fail(f"constraint ledger missing {marker}")


def check_text_guardrails() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step19.py"
        and path.suffix.lower() in {".md", ".json", ".csv", ".txt", ".py"}
    ]
    lowered = {path: path.read_text(errors="ignore").lower() for path in scan_files}
    for phrase in FORBIDDEN_PHRASES:
        needle = phrase.lower()
        for path, text in lowered.items():
            if needle in text:
                fail(f"forbidden overclaim phrase {phrase!r} found in {path.name}")
    for term in LITERATURE_PROGRAM_TERMS:
        pattern = re.compile(rf"\b{re.escape(term.lower())}\b")
        for path, text in lowered.items():
            if pattern.search(text):
                fail(f"literature-program term {term!r} found in {path.name}")


def main() -> None:
    check_required_files()
    check_schema_and_payload()
    check_f35_tables()
    check_source_and_scale_structure()
    check_gate_audit_and_ledgers()
    check_text_guardrails()
    print("run_step19.py: validation passed")


if __name__ == "__main__":
    main()
