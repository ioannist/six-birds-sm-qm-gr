#!/usr/bin/env python3
"""Validate Step 25 co-sourcing unification artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]
TOL = 1e-10

REQUIRED_FILES = [
    "sourcing_unification_step25.py",
    "field_carrier_step25.json",
    "sourced_descent_audits_step25.csv",
    "co_sourcing_consistency_step25.csv",
    "co_sourcing_summary_step25.csv",
    "sourcing_unification_statement_step25.tex",
    "sourcing_unification_output_step25.json",
    "sourcing_unification_output_step25.txt",
    "step25_results_summary.md",
    "step25_schema.json",
    "content_classification_step25.csv",
    "nonclaim_boundary_step25.md",
    "construction_gate_audit_step25.csv",
    "run_step25.py",
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
    schema = load_json("step25_schema.json")
    output = load_json("sourcing_unification_output_step25.json")
    if schema.get("step") != 25:
        fail("schema step is not 25")
    verdict = schema.get("final_verdict", {})
    if verdict.get("co_sourcing_verdict") != "L_is_co_sourcing_unification":
        fail("schema co-sourcing verdict mismatch")
    if verdict.get("L_single_psi_sources_both") is not True:
        fail("schema says L is not co-sourced")
    if verdict.get("non_co_sourced_control_pass") is not False:
        fail("schema says non-co-sourced control passes")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")

    track = schema.get("track_fields", {})
    if track.get("single_psi_consistency_computed") is not True:
        fail("schema missing single-psi computation flag")
    if track.get("control_uses_independent_gr_field") is not True:
        fail("schema missing independent control flag")
    if abs(float(track.get("L_max_born_residual", 1.0))) > TOL:
        fail("schema L Born residual is nonzero")
    if abs(float(track.get("L_max_stress_residual", 1.0))) > TOL:
        fail("schema L stress residual is nonzero")
    if float(track.get("control_max_stress_residual", 0.0)) <= TOL:
        fail("schema control stress residual is not positive")

    out_verdict = output.get("verdict", {})
    if out_verdict.get("co_sourcing_verdict") != "L_is_co_sourcing_unification":
        fail("output co-sourcing verdict mismatch")
    if out_verdict.get("L_single_psi_sources_both") is not True:
        fail("output says L is not co-sourced")
    if out_verdict.get("non_co_sourced_control_pass") is not False:
        fail("output says control passes")
    guards = output.get("guardrails", {})
    for key in ["single_psi_consistency_computed", "control_uses_independent_gr_field"]:
        if guards.get(key) is not True:
            fail(f"output guard {key} is not true")
    if guards.get("root_landed") is not False:
        fail("output root_landed must be false")


def check_carrier_and_consistency() -> None:
    carrier = load_json("field_carrier_step25.json")
    if "step24_derived_physical_audits_artifacts" not in carrier.get("source_step", ""):
        fail("field carrier does not reference Step 24 samples")
    n_samples = int(carrier["n_samples"])
    n_sites = int(carrier["n_sites"])
    if n_samples <= 0 or n_sites <= 0:
        fail("invalid carrier dimensions")
    for key in ["rho", "current_j", "T00", "T0i"]:
        if key not in carrier.get("derivations", {}):
            fail(f"carrier missing derivation {key}")

    values = load_csv("sourced_descent_audits_step25.csv")
    expected_value_rows = 2 * n_samples * n_sites
    if len(values) != expected_value_rows:
        fail(f"expected {expected_value_rows} sourced value rows, found {len(values)}")
    for row in values:
        case = row["case"]
        sample = int(row["sample"])
        gr_sample = int(row["control_gr_source_sample"])
        born_gap = max(
            abs(float(row["Born_rho_from_L_psi"]) - float(row["QM_descent_rho"])),
            abs(float(row["Born_j_from_L_psi"]) - float(row["QM_descent_j"])),
        )
        if born_gap > 1e-9:
            fail(f"Born descent mismatch in row {case} sample {sample}")
        stress_gap = max(
            abs(float(row["T00_from_L_psi"]) - float(row["GR_descent_T00"])),
            abs(float(row["T0i_from_L_psi"]) - float(row["GR_descent_T0i"])),
        )
        if case == "L_co_sourced" and stress_gap > 1e-9:
            fail(f"L stress descent mismatch in sample {sample}")
        if case == "non_co_sourced_control" and gr_sample == sample:
            fail("control GR source sample is not independent")

    consistency = load_csv("co_sourcing_consistency_step25.csv")
    if len(consistency) != 2 * n_samples:
        fail("wrong number of consistency rows")
    l_rows = [row for row in consistency if row["case"] == "L_co_sourced"]
    c_rows = [row for row in consistency if row["case"] == "non_co_sourced_control"]
    if len(l_rows) != n_samples or len(c_rows) != n_samples:
        fail("missing L or control consistency rows")
    for row in l_rows:
        if abs(float(row["born_descent_residual"])) > TOL:
            fail("L Born residual is nonzero")
        if abs(float(row["stress_energy_descent_residual"])) > TOL:
            fail("L stress residual is nonzero")
        if not as_bool(row["single_psi_sources_both"]):
            fail("L row does not pass single-psi sourcing")
    if not any(float(row["stress_energy_descent_residual"]) > TOL for row in c_rows):
        fail("control has no positive stress residual")
    if any(as_bool(row["single_psi_sources_both"]) for row in c_rows):
        fail("a control row passes single-psi sourcing")


def check_summary_and_ledgers() -> None:
    summary = load_csv("co_sourcing_summary_step25.csv")
    by_case = {row["case"]: row for row in summary}
    l_row = by_case.get("L_co_sourced")
    c_row = by_case.get("non_co_sourced_control")
    if l_row is None or c_row is None:
        fail("summary missing L or control")
    if abs(float(l_row["max_born_descent_residual"])) > TOL:
        fail("summary L Born residual nonzero")
    if abs(float(l_row["max_stress_energy_descent_residual"])) > TOL:
        fail("summary L stress residual nonzero")
    if not as_bool(l_row["all_samples_single_psi_sources_both"]):
        fail("summary L pass false")
    if float(c_row["max_stress_energy_descent_residual"]) <= TOL:
        fail("summary control stress residual not positive")
    if as_bool(c_row["all_samples_single_psi_sources_both"]):
        fail("summary control passes")

    gate_rows = load_csv("construction_gate_audit_step25.csv")
    if len(gate_rows) != 6:
        fail("expected six gate-audit rows")
    failed = [row for row in gate_rows if row["status"] != "pass"]
    if failed:
        fail(f"gate audit has non-pass rows: {failed}")

    lineage = (THREAD / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    grammar = (THREAD / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    constraints = (THREAD / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    findings = (THREAD / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "R_child_E018_after_sourcing_unification" not in lineage:
        fail("target lineage missing Step 25 residual")
    if "G_E018_COSOURCING_EXTERNAL_REVIEW_STEP26" not in grammar:
        fail("grammar manifest missing Step 25 review row")
    for marker in [
        "C_STEP25_FIELD_CARRIER_REUSED",
        "C_STEP25_SINGLE_PSI_CONSISTENCY_COMPUTED",
        "C_STEP25_L_ZERO_RESIDUALS",
        "C_STEP25_CONTROL_INDEPENDENT_GR_FIELD",
        "C_STEP25_CONTROL_FAILS",
        "C_STEP25_EXTERNAL_REVIEW",
    ]:
        if marker not in constraints:
            fail(f"constraint ledger missing {marker}")
    if "Step 25 — Co-Sourcing Unification" not in findings:
        fail("findings missing Step 25 entry")
    if "co_sourcing_verdict = L_is_co_sourcing_unification" not in findings:
        fail("findings missing Step 25 verdict")


def check_text_guardrails() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step25.py"
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
    check_carrier_and_consistency()
    check_summary_and_ledgers()
    check_text_guardrails()
    print("run_step25.py: validation passed")


if __name__ == "__main__":
    main()
