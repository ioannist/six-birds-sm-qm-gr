#!/usr/bin/env python3
"""Validate Step 22 F51 unification artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]
TOL = 1e-10

REQUIRED_FILES = [
    "f51_unification_step22.py",
    "f51_carrier_maps_step22.json",
    "f51_projection_checks_step22.csv",
    "f51_status_compatibility_step22.csv",
    "f51_delta_fact_witnesses_step22.csv",
    "f51_unification_statement_step22.tex",
    "f51_source_record_step22.csv",
    "f51_source_record_step22.json",
    "f51_source_extract_step22.md",
    "f51_unification_output_step22.json",
    "f51_unification_output_step22.txt",
    "step22_results_summary.md",
    "step22_schema.json",
    "content_classification_step22.csv",
    "nonclaim_boundary_step22.md",
    "construction_gate_audit_step22.csv",
    "run_step22.py",
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


def check_schema_payload_source() -> None:
    schema = load_json("step22_schema.json")
    output = load_json("f51_unification_output_step22.json")
    source = load_json("f51_source_record_step22.json")

    if schema.get("step") != 22:
        fail("schema step is not 22")
    verdict = schema.get("final_verdict", {})
    if verdict.get("F51_verdict") != "unification_holds_on_carrier":
        fail("schema F51 verdict mismatch")
    if verdict.get("L_f51_unification_pass") is not True:
        fail("schema says L does not pass F51")
    if verdict.get("status_conflict_control_pass") is not False:
        fail("schema says status-conflict control passes")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("external_review_required") is not True:
        fail("schema must require external review")

    track = schema.get("track_fields", {})
    if track.get("F51_source_read") is not True:
        fail("schema missing F51 source-read flag")
    if track.get("status_compatibility_computed") is not True:
        fail("schema does not record status compatibility computation")

    out_verdict = output.get("verdict", {})
    if out_verdict.get("F51_verdict") != "unification_holds_on_carrier":
        fail("output F51 verdict mismatch")
    if out_verdict.get("L_f51_unification_pass") is not True:
        fail("output says L does not pass")
    if out_verdict.get("status_conflict_control_pass") is not False:
        fail("status-conflict control passed")

    guards = output.get("guardrails", {})
    if guards.get("status_compatibility_computed") is not True:
        fail("output does not record computed status compatibility")
    if guards.get("F51_source_read") is not True:
        fail("output does not record F51 source read")
    if guards.get("root_landed") is not False:
        fail("output root_landed must be false")

    if source.get("F51_lines_read") != "8528-8582":
        fail("F51 source line record missing or changed")
    if "status" not in source.get("criterion", ""):
        fail("F51 source criterion does not mention status compatibility")


def check_projection_and_status_rows() -> None:
    projection_rows = load_csv("f51_projection_checks_step22.csv")
    if len(projection_rows) != 4:
        fail(f"expected 4 projection rows, found {len(projection_rows)}")
    by_key = {(row["case"], row["child"]): row for row in projection_rows}
    for key in [
        ("L_common_refinement", "QM"),
        ("L_common_refinement", "GR"),
        ("status_conflict_control", "QM"),
        ("status_conflict_control", "GR"),
    ]:
        if key not in by_key:
            fail(f"missing projection row {key}")

    for child in ["QM", "GR"]:
        row = by_key[("L_common_refinement", child)]
        if float(row["projection_residual"]) > TOL:
            fail(f"L projection residual for {child} is nonzero")
        if int(row["strict_delta_count"]) <= 0:
            fail(f"L strict delta count for {child} is empty")
        if float(row["audit_restriction_residual"]) > TOL:
            fail(f"L audit residual for {child} is nonzero")
        if not as_bool(row["admissible_descent_status"]):
            fail(f"L descent status for {child} is not admissible")

    conflict_gr = by_key[("status_conflict_control", "GR")]
    if float(conflict_gr["audit_restriction_residual"]) <= TOL:
        fail("conflict control GR audit residual is not positive")
    if as_bool(conflict_gr["admissible_descent_status"]):
        fail("conflict control GR descent status is admissible")

    status_rows = load_csv("f51_status_compatibility_step22.csv")
    if len(status_rows) != 2:
        fail("expected two status compatibility rows")
    by_case = {row["case"]: row for row in status_rows}
    l_row = by_case.get("L_common_refinement")
    c_row = by_case.get("status_conflict_control")
    if l_row is None or c_row is None:
        fail("missing status rows")
    if float(l_row["shared_overlap_audit_residual"]) > TOL:
        fail("L shared-overlap audit residual is nonzero")
    if not as_bool(l_row["status_compatible"]) or not as_bool(l_row["f51_unification_pass"]):
        fail("L status compatibility or F51 pass is false")
    if float(c_row["shared_overlap_audit_residual"]) <= TOL:
        fail("control shared-overlap audit residual is not positive")
    if as_bool(c_row["status_compatible"]) or as_bool(c_row["f51_unification_pass"]):
        fail("status-conflict control passes")


def check_delta_witnesses_and_maps() -> None:
    witnesses = load_csv("f51_delta_fact_witnesses_step22.csv")
    counts: dict[tuple[str, str], int] = {}
    for row in witnesses:
        key = (row["case"], row["child"])
        counts[key] = counts.get(key, 0) + 1
    for key in [
        ("L_common_refinement", "QM"),
        ("L_common_refinement", "GR"),
        ("status_conflict_control", "QM"),
        ("status_conflict_control", "GR"),
    ]:
        if counts.get(key) != 8:
            fail(f"expected 8 Delta_fact witnesses for {key}, found {counts.get(key)}")

    maps = load_json("f51_carrier_maps_step22.json")
    if len(maps.get("carrier", [])) != 16:
        fail("carrier is not the complete 16-state mode carrier")
    for key in ["pi_L", "pi_QM", "pi_GR", "to_qm", "to_gr", "audit_parent", "audit_qm", "audit_gr"]:
        if key not in maps:
            fail(f"carrier map file missing {key}")


def check_gate_audit_ledgers_findings() -> None:
    gate_rows = load_csv("construction_gate_audit_step22.csv")
    if len(gate_rows) != 7:
        fail("expected seven gate-audit rows")
    failed = [row for row in gate_rows if row["status"] != "pass"]
    if failed:
        fail(f"gate audit has non-pass rows: {failed}")

    lineage = (THREAD / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    grammar = (THREAD / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    constraints = (THREAD / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    findings = (THREAD / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "R_child_E018_after_F51_unification_classification" not in lineage:
        fail("target lineage missing Step 22 residual")
    if "G_E018_F51_EXTERNAL_REVIEW_STEP23" not in grammar:
        fail("grammar manifest missing Step 22 review row")
    for marker in [
        "C_STEP22_F51_SOURCE_READ",
        "C_STEP22_PROJECTION_SQUARES",
        "C_STEP22_STRICT_REFINES_BOTH",
        "C_STEP22_STATUS_COMPATIBILITY_COMPUTED",
        "C_STEP22_L_F51_PASSES",
        "C_STEP22_CONFLICT_CONTROL_FAILS",
        "C_STEP22_EXTERNAL_REVIEW",
    ]:
        if marker not in constraints:
            fail(f"constraint ledger missing {marker}")
    if "Step 22 — F51 Common-Refinement Unification" not in findings:
        fail("findings missing Step 22 entry")
    if "F51_verdict = unification_holds_on_carrier" not in findings:
        fail("findings missing F51 verdict")


def check_text_guardrails() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step22.py"
        and path.suffix.lower() in {".py", ".json", ".csv", ".md", ".txt", ".tex"}
    ]
    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in text:
                fail(f"forbidden overclaim phrase {phrase!r} found in {path.name}")


def main() -> None:
    missing = [name for name in REQUIRED_FILES if not (BASE / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")
    check_schema_payload_source()
    check_projection_and_status_rows()
    check_delta_witnesses_and_maps()
    check_gate_audit_ledgers_findings()
    check_text_guardrails()
    print("run_step22.py: validation passed")


if __name__ == "__main__":
    main()
