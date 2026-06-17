#!/usr/bin/env python3
"""Validate Step 26 artifacts and guardrails."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8
STRICT_TOL = 1e-10

REQUIRED_FILES = [
    "semiclassical_dynamics_step26.py",
    "dynamics_parameters_step26.json",
    "convergence_trace_step26.csv",
    "fixed_point_summary_step26.csv",
    "fixed_point_states_step26.json",
    "semiclassical_dynamics_output_step26.json",
    "semiclassical_dynamics_output_step26.txt",
    "semiclassical_dynamics_statement_step26.tex",
    "step26_results_summary.md",
    "step26_schema.json",
    "content_classification_step26.csv",
    "nonclaim_boundary_step26.md",
    "construction_gate_audit_step26.csv",
    "run_step26.py",
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
    print(f"run_step26.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scan_forbidden() -> None:
    text_paths = [
        path
        for path in ARTIFACT_DIR.iterdir()
        if path.is_file()
        and path.name != "run_step26.py"
        and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
    ]
    for path in text_paths:
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                fail(f"forbidden phrase {phrase!r} found in {path.name}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    schema = json.loads((ARTIFACT_DIR / "step26_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 26:
        fail("schema step is not 26")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "self_consistent_dynamics_converges_on_toy":
        fail("schema verdict is not the expected toy dynamics verdict")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")

    output = json.loads((ARTIFACT_DIR / "semiclassical_dynamics_output_step26.json").read_text(encoding="utf-8"))
    out_verdict = output.get("verdict", {})
    if out_verdict.get("semiclassical_dynamics_verdict") != "self_consistent_dynamics_converges_on_toy":
        fail("simulation output does not report the measured toy verdict")
    if out_verdict.get("consistent_coupling_converged") is not True:
        fail("consistent coupling did not converge")
    if out_verdict.get("runaway_control_converged") is not False:
        fail("runaway control converged")

    params = json.loads((ARTIFACT_DIR / "dynamics_parameters_step26.json").read_text(encoding="utf-8"))
    if "T00[psi]" not in params.get("potential_definition", ""):
        fail("potential definition does not source from T00[psi]")
    if "diag(V)" not in params.get("hamiltonian_definition", ""):
        fail("Hamiltonian definition does not include the sourced potential")
    if "exp(-i H[V] dt)" not in params.get("unitary_step_definition", ""):
        fail("unitary Schrödinger step is not declared")

    trace = read_csv(ARTIFACT_DIR / "convergence_trace_step26.csv")
    if len(trace) < 120:
        fail("convergence trace does not contain both 60-iteration cases")
    cases = {row["case"] for row in trace}
    if cases != {"consistent_coupling", "runaway_control"}:
        fail(f"unexpected trace cases {cases}")
    max_unitary_error = max(float(row["unitary_norm_error"]) for row in trace)
    if max_unitary_error > 1e-9:
        fail(f"unitary norm error too large: {max_unitary_error}")
    max_sourcing_gap = max(float(row["potential_sourcing_residual"]) for row in trace)
    if max_sourcing_gap > STRICT_TOL:
        fail(f"potential sourcing residual too large: {max_sourcing_gap}")

    summaries = {row["case"]: row for row in read_csv(ARTIFACT_DIR / "fixed_point_summary_step26.csv")}
    if set(summaries) != {"consistent_coupling", "runaway_control"}:
        fail("fixed-point summary missing required cases")
    consistent = summaries["consistent_coupling"]
    control = summaries["runaway_control"]
    if consistent["converged"] != "True":
        fail("consistent summary is not converged")
    for key in ["final_update_residual", "fixed_point_residual", "final_eigen_residual", "potential_sourcing_residual"]:
        if float(consistent[key]) > TOL:
            fail(f"consistent {key} too large: {consistent[key]}")
    if control["converged"] != "False":
        fail("control summary is marked converged")
    if float(control["fixed_point_residual"]) <= 1e-2:
        fail("runaway control fixed-point residual is too small")
    if float(control["final_update_residual"]) <= 1e-2:
        fail("runaway control update residual is too small")

    script_text = (ARTIFACT_DIR / "semiclassical_dynamics_step26.py").read_text(encoding="utf-8")
    required_patterns = [
        r"for iteration in range\(steps\)",
        r"stress_energy_density\(psi, background\)",
        r"unitary_step\(",
        r"np\.linalg\.eigh",
    ]
    for pattern in required_patterns:
        if not re.search(pattern, script_text):
            fail(f"simulation script missing required pattern {pattern}")

    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP26_COUPLED_MAP_ITERATED",
        "C_STEP26_RUNAWAY_CONTROL_FAILS",
        "C_STEP26_EXTERNAL_REVIEW",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_semiclassical_dynamics" not in lineage:
        fail("target lineage missing Step 26 residual")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 26 — Semiclassical Dynamics" not in findings:
        fail("findings_qm_gr.md missing Step 26 entry")

    print("run_step26.py: PASS")


if __name__ == "__main__":
    main()
