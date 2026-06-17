#!/usr/bin/env python3
"""Validate Step 33 Part-B type-uniqueness artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "type_uniqueness_step33.py",
    "actual_L_maps_step33.json",
    "f24_predicates_on_L_step33.csv",
    "excluded_family_rulings_step33.csv",
    "coarsening_obstruction_step33.csv",
    "role_obstruction_pairs_step33.csv",
    "type_uniqueness_output_step33.json",
    "type_uniqueness_output_step33.txt",
    "f24_type_uniqueness_statement_step33.tex",
    "step33_results_summary.md",
    "step33_schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step33.py",
]

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

FORBIDDEN_PHRASES = [
    "qg impossible",
    "proven impossible",
    "quantum gravity is impossible",
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

DISALLOWED_SELECTOR_MARKERS = [
    "mechanism_flags",
    "expected_family",
    "declared_family",
    "family_tag",
    "case_tag",
]


def fail(message: str) -> None:
    print(f"run_step33.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bool_cell(value: str) -> bool:
    return str(value).strip().lower() == "true"


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step33.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def validate_no_selector_inputs() -> None:
    script = (ARTIFACT_DIR / "type_uniqueness_step33.py").read_text(encoding="utf-8").lower()
    for marker in DISALLOWED_SELECTOR_MARKERS:
        if marker in script:
            fail(f"type_uniqueness_step33.py contains selector marker {marker!r}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()
    validate_no_selector_inputs()

    output = json.loads((ARTIFACT_DIR / "type_uniqueness_output_step33.json").read_text(encoding="utf-8"))
    if output.get("step") != 33:
        fail("output step is not 33")
    if output.get("verdict") != "type_uniqueness_bridge_mediated_role_on_L":
        fail("unexpected Step 33 verdict")
    if output.get("unique_type") is not True:
        fail("unique_type must be true")
    if output.get("fired_families") != ["BridgeMediatedRole"]:
        fail("only BridgeMediatedRole may fire")
    guardrails = output.get("guardrails", {})
    if guardrails.get("case_selector_inputs_used") is not False:
        fail("selector-input guardrail not false")
    if guardrails.get("instance_uniqueness_open") is not True:
        fail("instance uniqueness must remain open")
    if guardrails.get("root_landed") is not False:
        fail("root_landed must remain false")

    schema = json.loads((ARTIFACT_DIR / "step33_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 33:
        fail("schema step is not 33")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "type_uniqueness_bridge_mediated_role_on_L":
        fail("schema verdict mismatch")
    if verdict.get("instance_uniqueness_open") is not True:
        fail("schema must leave instance uniqueness open")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")

    pred_rows = read_csv(ARTIFACT_DIR / "f24_predicates_on_L_step33.csv")
    if {row["family"] for row in pred_rows} != FAMILIES:
        fail("predicate table does not contain exactly the eight F24 families")
    fired = [row["family"] for row in pred_rows if bool_cell(row["fires"])]
    if fired != ["BridgeMediatedRole"]:
        fail(f"expected only BridgeMediatedRole to fire, got {fired}")
    for row in pred_rows:
        if not row["reason"] or "finite maps" not in row["computed_from"]:
            fail(f"predicate row for {row['family']} lacks computed-map evidence")

    excluded_rows = read_csv(ARTIFACT_DIR / "excluded_family_rulings_step33.csv")
    if len(excluded_rows) != 7:
        fail("excluded-family table must contain seven rows")
    excluded_families = {row["excluded_family"] for row in excluded_rows}
    if "BridgeMediatedRole" in excluded_families:
        fail("BridgeMediatedRole must not be in excluded-family table")
    if excluded_families != FAMILIES - {"BridgeMediatedRole"}:
        fail("excluded-family table has wrong family set")
    for row in excluded_rows:
        if not bool_cell(row["excluded"]):
            fail(f"excluded family {row['excluded_family']} is not excluded")
        if bool_cell(row["fires_on_L"]):
            fail(f"excluded family {row['excluded_family']} fires on L")
        for field in ["structural_reason", "predicate_reason", "computed_evidence", "bounded_ruling"]:
            if not row[field]:
                fail(f"excluded family {row['excluded_family']} missing {field}")

    coarsening_rows = read_csv(ARTIFACT_DIR / "coarsening_obstruction_step33.csv")
    if len(coarsening_rows) != 8:
        fail("coarsening search must check all eight q_QM subsets")
    for row in coarsening_rows:
        if bool_cell(row["empties_obstruction"]):
            fail(f"coarsening {row['coarsening_modes']} incorrectly empties O_s")
        if int(row["obstruction_count"]) <= 0:
            fail(f"coarsening {row['coarsening_modes']} lacks positive obstruction count")

    claim_rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(claim_rows) < 8:
        fail("content classification has too few rows")
    for row in claim_rows:
        if not row.get("claim_id") or not row.get("source_artifacts"):
            fail("content classification row missing id or source")
        for source in row["source_artifacts"].split(";"):
            if not (THREAD_DIR / source).exists():
                fail(f"missing cited source artifact: {source}")

    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for marker in ["type-uniqueness", "instance-uniqueness", "finite carrier", "external review"]:
        if marker not in nonclaim:
            fail(f"nonclaim boundary missing marker {marker!r}")

    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_partb_type_uniqueness" not in lineage:
        fail("target lineage missing Step 33 residual")
    grammar = (THREAD_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_PART_B_INSTANCE_UNIQUENESS_STEP34" not in grammar:
        fail("grammar manifest missing Step 34 instance-uniqueness obligation")
    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP33_PREDICATES_COMPUTED",
        "C_STEP33_ONLY_BRIDGE_MEDIATED_FIRES",
        "C_STEP33_COARSENING_EXCLUDED",
        "C_STEP33_INSTANCE_UNIQUENESS_OPEN",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 33 — Part B Type-Uniqueness" not in findings:
        fail("findings_qm_gr.md missing Step 33 entry")

    print("run_step33.py: PASS")


if __name__ == "__main__":
    main()
