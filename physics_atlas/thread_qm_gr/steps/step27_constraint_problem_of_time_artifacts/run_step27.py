#!/usr/bin/env python3
"""Validate Step 27 constraint/problem-of-time artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import constraint_problem_of_time_step27 as core


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8

REQUIRED_FILES = [
    "constraint_problem_of_time_step27.py",
    "constraint_spectrum_step27.csv",
    "physical_space_residuals_step27.csv",
    "relational_time_readout_step27.csv",
    "clock_extended_carrier_step27.json",
    "constraint_problem_of_time_output_step27.json",
    "constraint_problem_of_time_output_step27.txt",
    "constraint_problem_of_time_statement_step27.tex",
    "step27_results_summary.md",
    "step27_schema.json",
    "content_classification_step27.csv",
    "nonclaim_boundary_step27.md",
    "construction_gate_audit_step27.csv",
    "run_step27.py",
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
    print(f"run_step27.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step27.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def reconstructed_operators() -> dict[str, np.ndarray]:
    """Rebuild the actual operator from tracked sources, without a local NPZ."""
    psi, potential, _background, kinetic, _kappa, dt, _params = core.load_step26()
    h_field = kinetic + np.diag(potential)
    energy = float(np.real(np.vdot(psi, h_field @ psi)))
    p_clock, clock_vector, _eigenvalues = core.build_compatible_clock(energy, dt, core.M_CLOCK)
    bad_clock = (abs(energy) + 0.5) * np.eye(core.M_CLOCK, dtype=complex)
    return {
        "C_operator": core.constraint_operator(p_clock, h_field),
        "C_operator_control": core.constraint_operator(bad_clock, h_field),
        "history_state": core.normalize(np.kron(clock_vector, psi)),
    }


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    schema = json.loads((ARTIFACT_DIR / "step27_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 27:
        fail("schema step is not 27")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "timeless_relational_layer_exists_on_toy":
        fail("schema verdict is not the expected constraint verdict")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("empty_kernel_control_passes") is not False:
        fail("schema says the empty-kernel control passes")

    output = json.loads((ARTIFACT_DIR / "constraint_problem_of_time_output_step27.json").read_text(encoding="utf-8"))
    out_verdict = output.get("verdict", {})
    if out_verdict.get("constraint_verdict") != "timeless_relational_layer_exists_on_toy":
        fail("output verdict is not the expected toy constraint verdict")
    if out_verdict.get("physical_space_nonempty") is not True:
        fail("compatible constraint does not have a physical space")
    if out_verdict.get("empty_kernel_control_passes") is not False:
        fail("empty-kernel control passes")
    if out_verdict.get("relational_time_recovers_step26_stationary_dynamics") is not True:
        fail("relational time does not recover the Step 26 stationary dynamics")

    arrays = reconstructed_operators()
    c_operator = arrays["C_operator"]
    c_control = arrays["C_operator_control"]
    history_state = arrays["history_state"]
    if not np.allclose(c_operator, c_operator.conj().T, atol=1e-10):
        fail("constraint operator is not Hermitian")
    if not np.allclose(c_control, c_control.conj().T, atol=1e-10):
        fail("control constraint operator is not Hermitian")
    computed_residual = float(np.linalg.norm(c_operator @ history_state))
    if computed_residual > TOL:
        fail(f"computed ||C Psi|| too large: {computed_residual}")
    control_eigs = np.linalg.eigvalsh(c_control)
    if int(np.sum(np.abs(control_eigs) <= TOL)) != 0:
        fail("control has a numerical kernel")

    residual_rows = {row["case"]: row for row in read_csv(ARTIFACT_DIR / "physical_space_residuals_step27.csv")}
    if set(residual_rows) != {"compatible_constraint", "empty_kernel_control"}:
        fail("physical-space residuals missing required cases")
    compatible = residual_rows["compatible_constraint"]
    control = residual_rows["empty_kernel_control"]
    if compatible["physical_space_nonempty"] != "True":
        fail("compatible residual row does not report nonempty physical space")
    if int(compatible["kernel_dim_tol_1e_minus_8"]) <= 0:
        fail("compatible kernel dimension is zero")
    if float(compatible["state_constraint_residual"]) > TOL:
        fail("compatible state residual exceeds tolerance")
    if control["physical_space_nonempty"] != "False":
        fail("control residual row reports nonempty physical space")
    if int(control["kernel_dim_tol_1e_minus_8"]) != 0:
        fail("control kernel dimension is nonzero")
    if float(control["min_abs_eigenvalue"]) <= 1e-2:
        fail("control minimum eigenvalue is too small")

    relational_rows = read_csv(ARTIFACT_DIR / "relational_time_readout_step27.csv")
    if len(relational_rows) != 16:
        fail("relational readout does not have 16 clock rows")
    max_direct = max(float(row["direct_relational_residual"]) for row in relational_rows)
    max_sourced = max(float(row["sourced_potential_residual"]) for row in relational_rows)
    if max_direct > TOL:
        fail(f"relational residual too large: {max_direct}")
    if max_sourced > TOL:
        fail(f"sourced potential residual too large: {max_sourced}")

    script_text = (ARTIFACT_DIR / "constraint_problem_of_time_step27.py").read_text(encoding="utf-8")
    required_patterns = [
        r"constraint_operator\(p_clock, h_field\)",
        r"np\.linalg\.eigvalsh",
        r"history_state",
        r"unitary_evolve\(h_field, psi_star",
    ]
    for pattern in required_patterns:
        if not re.search(pattern, script_text):
            fail(f"simulation script missing required pattern {pattern}")

    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP27_KERNEL_COMPUTED",
        "C_STEP27_RELATIONAL_READOUT_COMPUTED",
        "C_STEP27_EMPTY_KERNEL_CONTROL_FAILS",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_problem_of_time_constraint" not in lineage:
        fail("target lineage missing Step 27 residual")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 27 — Constraint / Problem of Time" not in findings:
        fail("findings_qm_gr.md missing Step 27 entry")

    print("run_step27.py: PASS")


if __name__ == "__main__":
    main()
