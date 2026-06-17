#!/usr/bin/env python3
"""Validate Step 24 derived physical audit artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np


BASE = Path(__file__).resolve().parent
THREAD = BASE.parents[1]
TOL = 1e-10

REQUIRED_FILES = [
    "derived_physical_audits_step24.py",
    "toy_field_samples_step24.json",
    "derived_audit_values_step24.csv",
    "shared_mode_coherence_step24.csv",
    "coherence_summary_step24.csv",
    "sourcing_check_step24.csv",
    "derived_audit_statement_step24.tex",
    "derived_physical_audit_output_step24.json",
    "derived_physical_audit_output_step24.txt",
    "step24_results_summary.md",
    "step24_schema.json",
    "content_classification_step24.csv",
    "nonclaim_boundary_step24.md",
    "construction_gate_audit_step24.csv",
    "run_step24.py",
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


def finite_gradient(psi: np.ndarray) -> np.ndarray:
    return (np.roll(psi, -1) - np.roll(psi, 1)) / 2.0


def shift_derivative(psi: np.ndarray) -> np.ndarray:
    return np.roll(psi, -1) - psi


def born(psi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grad = finite_gradient(psi)
    return np.abs(psi) ** 2, np.imag(np.conj(psi) * grad)


def stress(psi: np.ndarray, potential: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grad = finite_gradient(psi)
    shift = shift_derivative(psi)
    return np.abs(grad) ** 2 + potential * np.abs(psi) ** 2, np.real(np.conj(grad) * shift)


def check_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (BASE / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def check_schema_payload() -> None:
    schema = load_json("step24_schema.json")
    payload = load_json("derived_physical_audit_output_step24.json")
    if schema.get("step") != 24:
        fail("schema step is not 24")
    verdict = schema.get("final_verdict", {})
    if verdict.get("derived_audit_verdict") != "derived_audits_differ_reconciliation_is_sourcing_T_of_psi":
        fail("schema derived audit verdict mismatch")
    if verdict.get("born_and_stress_energy_same_audit") is not False:
        fail("schema says derived audits are the same audit")
    if verdict.get("sourcing_T_of_psi") is not True:
        fail("schema says sourcing does not hold")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")

    track = schema.get("track_fields", {})
    for key in ["audits_derived_from_psi", "coherence_computed", "sourcing_computed"]:
        if track.get(key) is not True:
            fail(f"schema track field {key} is not true")
    for key in [
        "density_proportional_residual",
        "transport_proportional_residual",
        "density_equal_residual",
        "transport_equal_residual",
    ]:
        if float(track.get(key, 0.0)) <= TOL:
            fail(f"schema residual {key} is not positive")
    if abs(float(track.get("direct_sourcing_residual", 1.0))) > TOL:
        fail("schema direct sourcing residual is not zero")

    out_verdict = payload.get("verdict", {})
    if out_verdict.get("derived_audit_verdict") != "derived_audits_differ_reconciliation_is_sourcing_T_of_psi":
        fail("payload derived audit verdict mismatch")
    if out_verdict.get("born_and_stress_energy_same_audit") is not False:
        fail("payload says audits are same")
    if out_verdict.get("sourcing_T_of_psi") is not True:
        fail("payload says sourcing does not hold")
    guards = payload.get("guardrails", {})
    for key in ["audits_derived_from_psi", "coherence_computed", "sourcing_computed"]:
        if guards.get(key) is not True:
            fail(f"payload guard {key} is not true")
    if guards.get("root_landed") is not False:
        fail("payload root_landed must be false")


def check_audit_values_recompute() -> None:
    samples = load_json("toy_field_samples_step24.json")
    potential = np.asarray(samples["potential"], dtype=float)
    fields = {
        int(record["sample"]): np.asarray(record["psi_re"], dtype=float)
        + 1j * np.asarray(record["psi_im"], dtype=float)
        for record in samples["fields"]
    }
    if len(fields) != int(samples["n_samples"]):
        fail("sample count mismatch")
    derivations = samples.get("derivations", {})
    for key in ["rho", "current_j", "T00", "T0i"]:
        if key not in derivations:
            fail(f"missing derivation formula for {key}")

    value_rows = load_csv("derived_audit_values_step24.csv")
    expected_rows = len(fields) * int(samples["n_sites"])
    if len(value_rows) != expected_rows:
        fail(f"expected {expected_rows} value rows, found {len(value_rows)}")

    for row in value_rows:
        sample = int(row["sample"])
        site = int(row["site"])
        psi = fields[sample]
        rho, current = born(psi)
        t00, t0i = stress(psi, potential)
        checks = {
            "rho": rho[site],
            "current_j": current[site],
            "T00": t00[site],
            "T0i": t0i[site],
        }
        for key, expected in checks.items():
            if abs(float(row[key]) - float(expected)) > 1e-9:
                fail(f"derived value mismatch for sample {sample} site {site} {key}")


def check_coherence_and_sourcing() -> None:
    summary = load_csv("coherence_summary_step24.csv")
    if len(summary) != 2:
        fail("coherence summary must have density and transport rows")
    by_mode = {row["mode"]: row for row in summary}
    for mode in ["density", "transport"]:
        row = by_mode.get(mode)
        if row is None:
            fail(f"missing coherence row {mode}")
        if as_bool(row["coheres_as_same_audit"]):
            fail(f"{mode} unexpectedly coheres as same audit")
        if float(row["equal_residual"]) <= TOL or float(row["proportional_residual"]) <= TOL:
            fail(f"{mode} residuals are not positive")

    per_sample = load_csv("shared_mode_coherence_step24.csv")
    if not per_sample:
        fail("per-sample coherence table is empty")
    if not any(float(row["density_proportional_residual"]) > TOL for row in per_sample):
        fail("no per-sample density mismatch recorded")
    if not any(float(row["transport_proportional_residual"]) > TOL for row in per_sample):
        fail("no per-sample transport mismatch recorded")

    sourcing = load_csv("sourcing_check_step24.csv")
    if len(sourcing) != 2:
        fail("sourcing check must have two target rows")
    for row in sourcing:
        if abs(float(row["direct_sourcing_residual"])) > TOL:
            fail(f"direct sourcing residual for {row['target']} is not zero")
        if float(row["shared_audit_linear_test_residual"]) <= TOL:
            fail(f"shared-audit held-out residual for {row['target']} is not positive")
        if "functional of psi" not in row["computed_reconciliation"]:
            fail(f"sourcing interpretation missing for {row['target']}")


def check_gate_audit_ledgers_findings() -> None:
    gate_rows = load_csv("construction_gate_audit_step24.csv")
    if len(gate_rows) != 7:
        fail("expected seven gate-audit rows")
    failed = [row for row in gate_rows if row["status"] != "pass"]
    if failed:
        fail(f"gate audit has non-pass rows: {failed}")

    lineage = (THREAD / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    grammar = (THREAD / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    constraints = (THREAD / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    findings = (THREAD / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "R_child_E018_after_derived_physical_audit_sourcing" not in lineage:
        fail("target lineage missing Step 24 residual")
    if "G_E018_SOURCING_AUDIT_RECONCILIATION_STEP25" not in grammar:
        fail("grammar manifest missing Step 24 next construction row")
    for marker in [
        "C_STEP24_SHARED_FIELD_DEFINED",
        "C_STEP24_AUDITS_DERIVED_FROM_PSI",
        "C_STEP24_COHERENCE_COMPUTED",
        "C_STEP24_SAME_AUDIT_REJECTED",
        "C_STEP24_SOURCING_COMPUTED",
        "C_STEP24_SHARED_AUDIT_NOT_SUFFICIENT",
        "C_STEP24_EXTERNAL_REVIEW",
    ]:
        if marker not in constraints:
            fail(f"constraint ledger missing {marker}")
    if "Step 24 — Derived Physical Audits from Shared Field" not in findings:
        fail("findings missing Step 24 entry")
    if "derived_audit_verdict = derived_audits_differ_reconciliation_is_sourcing_T_of_psi" not in findings:
        fail("findings missing Step 24 verdict")


def check_text_guardrails() -> None:
    scan_files = [
        path
        for path in BASE.iterdir()
        if path.is_file()
        and path.name != "run_step24.py"
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
    check_audit_values_recompute()
    check_coherence_and_sourcing()
    check_gate_audit_ledgers_findings()
    check_text_guardrails()
    print("run_step24.py: validation passed")


if __name__ == "__main__":
    main()
