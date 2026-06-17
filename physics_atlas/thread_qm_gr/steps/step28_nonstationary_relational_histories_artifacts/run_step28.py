#!/usr/bin/env python3
"""Validate Step 28 non-stationary relational-history artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8

REQUIRED_FILES = [
    "nonstationary_relational_history_step28.py",
    "nonstationary_history_step28.json",
    "constraint_operators_step28.npz",
    "nonstationary_history_diagnostics_step28.csv",
    "constraint_singular_values_step28.csv",
    "constraint_residuals_step28.csv",
    "relational_readout_step28.csv",
    "nonstationary_relational_history_output_step28.json",
    "nonstationary_relational_history_output_step28.txt",
    "nonstationary_relational_history_statement_step28.tex",
    "step28_results_summary.md",
    "step28_schema.json",
    "content_classification_step28.csv",
    "nonclaim_boundary_step28.md",
    "construction_gate_audit_step28.csv",
    "run_step28.py",
]

FORBIDDEN_PHRASES = [
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


def fail(message: str) -> None:
    print(f"run_step28.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step28.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    schema = json.loads((ARTIFACT_DIR / "step28_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 28:
        fail("schema step is not 28")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "nonstationary_relational_history_constraint_consistent_on_toy":
        fail("schema verdict is not the expected non-stationary relational verdict")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("wrong_generator_control_passes") is not False:
        fail("schema says wrong-generator control passes")

    output = json.loads((ARTIFACT_DIR / "nonstationary_relational_history_output_step28.json").read_text(encoding="utf-8"))
    out_verdict = output.get("verdict", {})
    if out_verdict.get("nonstationary_relational_verdict") != "nonstationary_relational_history_constraint_consistent_on_toy":
        fail("output verdict mismatch")
    if out_verdict.get("history_is_nonstationary") is not True:
        fail("history is not non-stationary")
    if out_verdict.get("generated_constraint_passes") is not True:
        fail("generated constraint does not pass")
    if out_verdict.get("wrong_generator_control_passes") is not False:
        fail("wrong-generator control passes")
    if out_verdict.get("relational_readout_recovers_history") is not True:
        fail("relational field readout does not recover the history")
    if out_verdict.get("relational_potential_recovers_sourcing") is not True:
        fail("relational potential readout does not recover sourcing")

    diagnostics = read_csv(ARTIFACT_DIR / "nonstationary_history_diagnostics_step28.csv")
    if len(diagnostics) != 16:
        fail("history diagnostics must contain 16 clock rows")
    min_eigen_residual = min(float(row["eigen_residual"]) for row in diagnostics)
    max_state_change = max(float(row["state_change_to_next_phase_invariant"]) for row in diagnostics)
    max_potential_change = max(float(row["potential_change_to_next"]) for row in diagnostics)
    max_step_residual = max(float(row["single_step_evolution_residual"]) for row in diagnostics)
    max_unitary_norm_error = max(float(row["unitary_norm_error"]) for row in diagnostics)
    if min_eigen_residual <= 1e-2:
        fail("history is too close to an eigenstate")
    if max_state_change <= 1e-2:
        fail("state does not genuinely evolve")
    if max_potential_change <= 1e-4:
        fail("potential does not visibly change")
    if max_step_residual > TOL:
        fail(f"single-step evolution residual too large: {max_step_residual}")
    if max_unitary_norm_error > 1e-9:
        fail(f"unitary norm error too large: {max_unitary_norm_error}")

    residual_rows = {row["case"]: row for row in read_csv(ARTIFACT_DIR / "constraint_residuals_step28.csv")}
    if set(residual_rows) != {"generated_relational_constraint", "wrong_identity_generator_control"}:
        fail("constraint residuals missing required cases")
    generated = residual_rows["generated_relational_constraint"]
    control = residual_rows["wrong_identity_generator_control"]
    if generated["passes_constraint"] != "True":
        fail("generated constraint row does not pass")
    if float(generated["history_constraint_residual"]) > TOL:
        fail("generated constraint residual too large")
    if int(generated["null_dim_tol_1e_minus_8"]) <= 0:
        fail("generated constraint null dimension is zero")
    if control["passes_constraint"] != "False":
        fail("wrong-generator control row passes")
    if float(control["history_constraint_residual"]) <= 1e-2:
        fail("wrong-generator control residual too small")

    arrays = np.load(ARTIFACT_DIR / "constraint_operators_step28.npz")
    c_generated = arrays["C_generated"]
    c_control = arrays["C_wrong_identity_control"]
    history_state = arrays["history_state"]
    if float(np.linalg.norm(c_generated @ history_state)) > TOL:
        fail("computed generated C history residual too large")
    if float(np.linalg.norm(c_control @ history_state)) <= 1e-2:
        fail("computed control residual too small")

    readout_rows = read_csv(ARTIFACT_DIR / "relational_readout_step28.csv")
    if len(readout_rows) != 16:
        fail("relational readout must contain 16 clock rows")
    max_field_readout = max(float(row["field_readout_residual"]) for row in readout_rows)
    max_potential_readout = max(float(row["relational_potential_residual"]) for row in readout_rows)
    if max_field_readout > TOL:
        fail("field readout residual too large")
    if max_potential_readout > TOL:
        fail("potential readout residual too large")

    script_text = (ARTIFACT_DIR / "nonstationary_relational_history_step28.py").read_text(encoding="utf-8")
    required_patterns = [
        r"V_t = background \+ kappa\*T00",
        r"c\[row, current\] = -generator",
        r"control == \"identity\"",
        r"history_constraint_residual",
    ]
    # The first pattern is documented in JSON/output rather than a Python variable name.
    combined_text = script_text + (ARTIFACT_DIR / "nonstationary_history_step28.json").read_text(encoding="utf-8")
    for pattern in required_patterns:
        if not re.search(pattern, combined_text):
            fail(f"simulation artifacts missing required pattern {pattern}")

    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP28_NONSTATIONARY_INITIAL_STATE",
        "C_STEP28_CONSTRAINT_RESIDUAL_COMPUTED",
        "C_STEP28_WRONG_GENERATOR_CONTROL_FAILS",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_nonstationary_relational_history" not in lineage:
        fail("target lineage missing Step 28 residual")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 28 — Non-Stationary Relational Histories" not in findings:
        fail("findings_qm_gr.md missing Step 28 entry")

    print("run_step28.py: PASS")


if __name__ == "__main__":
    main()
