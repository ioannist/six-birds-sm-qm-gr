#!/usr/bin/env python3
"""Step 27: finite clock constraint and relational-time readout."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP26_DIR = THREAD_DIR / "steps" / "step26_semiclassical_dynamics_artifacts"

M_CLOCK = 16
TOL = 1e-10


def normalize(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    if norm <= TOL:
        raise ValueError("cannot normalize zero vector")
    return vector / norm


def phase_align(candidate: np.ndarray, reference: np.ndarray) -> np.ndarray:
    overlap = np.vdot(candidate, reference)
    if abs(overlap) <= TOL:
        return candidate
    return candidate * np.exp(-1j * np.angle(overlap))


def complete_orthonormal_basis(first: np.ndarray) -> np.ndarray:
    first = normalize(first.astype(complex))
    basis = [first]
    n = len(first)
    for idx in range(n):
        candidate = np.zeros(n, dtype=complex)
        candidate[idx] = 1.0
        for vec in basis:
            candidate = candidate - vec * np.vdot(vec, candidate)
        norm = np.linalg.norm(candidate)
        if norm > 1e-12:
            basis.append(candidate / norm)
        if len(basis) == n:
            break
    if len(basis) != n:
        raise RuntimeError("failed to complete clock basis")
    return np.column_stack(basis)


def unitary_evolve(h: np.ndarray, psi: np.ndarray, time: float) -> np.ndarray:
    eigvals, eigvecs = np.linalg.eigh(h)
    phases = np.exp(-1j * eigvals * time)
    return eigvecs @ (phases * (eigvecs.conj().T @ psi))


def central_gradient(psi: np.ndarray) -> np.ndarray:
    return (np.roll(psi, -1) - np.roll(psi, 1)) / 2.0


def stress_energy_density(psi: np.ndarray, background: np.ndarray) -> np.ndarray:
    grad = central_gradient(psi)
    return (np.abs(grad) ** 2 + background * np.abs(psi) ** 2).real


def load_step26() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float, dict[str, object]]:
    params = json.loads((STEP26_DIR / "dynamics_parameters_step26.json").read_text(encoding="utf-8"))
    states = json.loads((STEP26_DIR / "fixed_point_states_step26.json").read_text(encoding="utf-8"))["states"]
    consistent = next(state for state in states if state["case"] == "consistent_coupling")
    psi = np.asarray(consistent["psi_re"], dtype=float) + 1j * np.asarray(consistent["psi_im"], dtype=float)
    psi = normalize(psi)
    potential = np.asarray(consistent["final_potential"], dtype=float)
    background = np.asarray(params["background_potential"], dtype=float)
    kinetic = np.asarray(params["kinetic_operator"], dtype=float)
    kappa = float(next(case["kappa"] for case in params["cases"] if case["case"] == "consistent_coupling"))
    dt = float(params["dt"])
    return psi, potential, background, kinetic, kappa, dt, params


def build_compatible_clock(energy: float, dt: float, m_clock: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    times = np.arange(m_clock, dtype=float)
    clock_vector = normalize(np.exp(-1j * energy * dt * times))
    q = complete_orthonormal_basis(clock_vector)
    rest = 0.75 + np.arange(1, m_clock, dtype=float) / m_clock
    clock_eigs = np.concatenate((np.array([-energy], dtype=float), rest))
    p_clock = q @ np.diag(clock_eigs) @ q.conj().T
    return p_clock, clock_vector, clock_eigs


def constraint_operator(p_clock: np.ndarray, h_field: np.ndarray) -> np.ndarray:
    return np.kron(p_clock, np.eye(h_field.shape[0])) + np.kron(np.eye(p_clock.shape[0]), h_field)


def kernel_summary(c_operator: np.ndarray, state: np.ndarray, tolerance: float = 1e-8) -> dict[str, object]:
    eigvals = np.linalg.eigvalsh(c_operator)
    residual = float(np.linalg.norm(c_operator @ state))
    return {
        "kernel_dim_tol_1e_minus_8": int(np.sum(np.abs(eigvals) <= tolerance)),
        "min_abs_eigenvalue": float(np.min(np.abs(eigvals))),
        "state_constraint_residual": residual,
        "state_norm": float(np.linalg.norm(state)),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    psi_star, potential, background, kinetic, kappa, dt, params = load_step26()
    h_field = kinetic + np.diag(potential)
    if not np.allclose(h_field, h_field.conj().T, atol=1e-12):
        raise RuntimeError("field Hamiltonian is not Hermitian")
    h_eigs, h_vecs = np.linalg.eigh(h_field)
    energy = float(np.real(np.vdot(psi_star, h_field @ psi_star)))
    eigen_residual = float(np.linalg.norm(h_field @ psi_star - energy * psi_star))
    lowest_energy = float(h_eigs[0])
    p_clock, clock_vector, clock_eigs = build_compatible_clock(energy, dt, M_CLOCK)
    c_operator = constraint_operator(p_clock, h_field)
    history_state = normalize(np.kron(clock_vector, psi_star))
    good_summary = kernel_summary(c_operator, history_state)

    bad_p_clock = (abs(energy) + 0.5) * np.eye(M_CLOCK, dtype=complex)
    bad_c_operator = constraint_operator(bad_p_clock, h_field)
    bad_summary = kernel_summary(bad_c_operator, history_state)

    spectrum_rows: list[dict[str, object]] = []
    for case, operator in [("compatible_constraint", c_operator), ("empty_kernel_control", bad_c_operator)]:
        eigvals = np.linalg.eigvalsh(operator)
        for idx, value in enumerate(eigvals):
            spectrum_rows.append(
                {
                    "case": case,
                    "eigen_index": idx,
                    "eigenvalue": float(value),
                    "abs_eigenvalue": float(abs(value)),
                    "in_kernel_tol_1e_minus_8": bool(abs(value) <= 1e-8),
                }
            )

    residual_rows = [
        {
            "case": "compatible_constraint",
            "clock_states": M_CLOCK,
            "field_dim": len(psi_star),
            "constraint_dim": c_operator.shape[0],
            "kernel_dim_tol_1e_minus_8": good_summary["kernel_dim_tol_1e_minus_8"],
            "min_abs_eigenvalue": good_summary["min_abs_eigenvalue"],
            "state_constraint_residual": good_summary["state_constraint_residual"],
            "state_norm": good_summary["state_norm"],
            "physical_space_nonempty": good_summary["kernel_dim_tol_1e_minus_8"] > 0
            and good_summary["state_constraint_residual"] <= 1e-8,
            "control_passes": False,
        },
        {
            "case": "empty_kernel_control",
            "clock_states": M_CLOCK,
            "field_dim": len(psi_star),
            "constraint_dim": bad_c_operator.shape[0],
            "kernel_dim_tol_1e_minus_8": bad_summary["kernel_dim_tol_1e_minus_8"],
            "min_abs_eigenvalue": bad_summary["min_abs_eigenvalue"],
            "state_constraint_residual": bad_summary["state_constraint_residual"],
            "state_norm": bad_summary["state_norm"],
            "physical_space_nonempty": bad_summary["kernel_dim_tol_1e_minus_8"] > 0
            and bad_summary["state_constraint_residual"] <= 1e-8,
            "control_passes": bad_summary["kernel_dim_tol_1e_minus_8"] > 0,
        },
    ]

    relational_rows: list[dict[str, object]] = []
    source_residuals: list[float] = []
    direct_residuals: list[float] = []
    aligned_residuals: list[float] = []
    for clock_t in range(M_CLOCK):
        component = history_state[clock_t * len(psi_star) : (clock_t + 1) * len(psi_star)]
        conditioned = normalize(component)
        external = unitary_evolve(h_field, psi_star, clock_t * dt)
        direct_residual = float(np.linalg.norm(conditioned - external))
        aligned_residual = float(np.linalg.norm(phase_align(conditioned, external) - external))
        sourced_potential = background + kappa * stress_energy_density(conditioned, background)
        source_residual = float(np.linalg.norm(sourced_potential - potential))
        direct_residuals.append(direct_residual)
        aligned_residuals.append(aligned_residual)
        source_residuals.append(source_residual)
        relational_rows.append(
            {
                "clock_t": clock_t,
                "time": clock_t * dt,
                "conditioned_field_norm": float(np.linalg.norm(conditioned)),
                "step26_external_norm": float(np.linalg.norm(external)),
                "direct_relational_residual": direct_residual,
                "phase_aligned_relational_residual": aligned_residual,
                "sourced_potential_residual": source_residual,
            }
        )

    verdict_name = (
        "timeless_relational_layer_exists_on_toy"
        if residual_rows[0]["physical_space_nonempty"]
        and not residual_rows[1]["physical_space_nonempty"]
        and max(direct_residuals) <= 1e-8
        else "constraint_obstruction_or_toothless_control"
    )

    np.savez(
        ARTIFACT_DIR / "constraint_operators_step27.npz",
        P_clock=p_clock,
        H_field=h_field,
        C_operator=c_operator,
        P_clock_control=bad_p_clock,
        C_operator_control=bad_c_operator,
        history_state=history_state,
    )
    write_csv(ARTIFACT_DIR / "constraint_spectrum_step27.csv", spectrum_rows)
    write_csv(ARTIFACT_DIR / "physical_space_residuals_step27.csv", residual_rows)
    write_csv(ARTIFACT_DIR / "relational_time_readout_step27.csv", relational_rows)

    carrier_payload = {
        "source_step26_dir": str(STEP26_DIR),
        "clock_states": M_CLOCK,
        "field_dim": len(psi_star),
        "constraint_dim": int(c_operator.shape[0]),
        "dt": dt,
        "kappa": kappa,
        "energy": energy,
        "field_eigen_residual": eigen_residual,
        "lowest_energy": lowest_energy,
        "clock_eigenvalues": clock_eigs.tolist(),
        "constraint_definition": "C = P_clock tensor I_field + I_clock tensor H_field",
        "P_clock_definition": "Hermitian finite compatible clock generator with the history clock vector as eigenvector of eigenvalue -E_star.",
        "control_definition": "Positive clock generator P=(|E_star|+0.5)I, giving no zero eigenvalue for C_control.",
        "relational_readout": "condition history state on clock_t and compare to exp(-i H_field t dt) psi_star",
        "step26_scope": "stationary self-sourced fixed potential from consistent_coupling, not the relaxation trajectory",
        "step26_hamiltonian_definition": params["hamiltonian_definition"],
    }
    with (ARTIFACT_DIR / "clock_extended_carrier_step27.json").open("w", encoding="utf-8") as handle:
        json.dump(carrier_payload, handle, indent=2)

    output = {
        "step": 27,
        "verdict": {
            "constraint_verdict": verdict_name,
            "physical_space_nonempty": bool(residual_rows[0]["physical_space_nonempty"]),
            "empty_kernel_control_passes": bool(residual_rows[1]["physical_space_nonempty"]),
            "relational_time_recovers_step26_stationary_dynamics": max(direct_residuals) <= 1e-8,
            "root_landed": False,
            "external_review_required": True,
        },
        "summary": {
            "constraint_residual": good_summary["state_constraint_residual"],
            "kernel_dim_tol_1e_minus_8": good_summary["kernel_dim_tol_1e_minus_8"],
            "control_min_abs_eigenvalue": bad_summary["min_abs_eigenvalue"],
            "control_state_constraint_residual": bad_summary["state_constraint_residual"],
            "max_direct_relational_residual": max(direct_residuals),
            "max_phase_aligned_relational_residual": max(aligned_residuals),
            "max_sourced_potential_residual": max(source_residuals),
            "field_eigen_residual": eigen_residual,
            "energy": energy,
        },
        "guardrails": {
            "kernel_computed_by_spectrum": True,
            "state_residual_computed": True,
            "relational_readout_computed": True,
            "empty_kernel_control_required_to_fail": True,
        },
    }
    with (ARTIFACT_DIR / "constraint_problem_of_time_output_step27.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    with (ARTIFACT_DIR / "constraint_problem_of_time_output_step27.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 27 constraint / problem-of-time toy\n")
        handle.write(f"Verdict: {verdict_name}\n")
        handle.write(f"Physical space nonempty: {residual_rows[0]['physical_space_nonempty']}\n")
        handle.write(f"Constraint residual: {good_summary['state_constraint_residual']}\n")
        handle.write(f"Kernel dimension (tol 1e-8): {good_summary['kernel_dim_tol_1e_minus_8']}\n")
        handle.write(f"Relational max residual: {max(direct_residuals)}\n")
        handle.write(f"Empty-kernel control physical: {residual_rows[1]['physical_space_nonempty']}\n")
        handle.write(f"Control min abs eigenvalue: {bad_summary['min_abs_eigenvalue']}\n")


if __name__ == "__main__":
    main()
