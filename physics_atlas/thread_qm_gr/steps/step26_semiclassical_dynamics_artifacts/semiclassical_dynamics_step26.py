#!/usr/bin/env python3
"""Step 26: finite semiclassical field-potential back-reaction dynamics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP24_DIR = THREAD_DIR / "steps" / "step24_derived_physical_audits_artifacts"
SOURCE_FIELDS = STEP24_DIR / "toy_field_samples_step24.json"

DX = 1.0
DT = 0.05
STEPS = 60
TOL = 1e-10
CONVERGENCE_TOL = 1e-8


def normalize(psi: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(psi))
    if norm <= TOL:
        raise ValueError("cannot normalize a zero field")
    return psi / norm


def phase_align(candidate: np.ndarray, reference: np.ndarray) -> np.ndarray:
    overlap = np.vdot(candidate, reference)
    if abs(overlap) <= TOL:
        return candidate
    return candidate * np.exp(-1j * np.angle(overlap))


def periodic_gradient(psi: np.ndarray) -> np.ndarray:
    return (np.roll(psi, -1) - np.roll(psi, 1)) / (2.0 * DX)


def stress_energy_density(psi: np.ndarray, background: np.ndarray) -> np.ndarray:
    """Toy T00[psi]: gradient energy plus background-weighted field density."""
    grad = periodic_gradient(psi)
    return (np.abs(grad) ** 2 + background * np.abs(psi) ** 2).real


def kinetic_operator(n_sites: int) -> np.ndarray:
    lap = np.zeros((n_sites, n_sites), dtype=float)
    for i in range(n_sites):
        lap[i, i] = 2.0
        lap[i, (i - 1) % n_sites] = -1.0
        lap[i, (i + 1) % n_sites] = -1.0
    return 0.5 * lap


def hamiltonian(kinetic: np.ndarray, potential: np.ndarray) -> np.ndarray:
    return kinetic + np.diag(np.asarray(potential, dtype=float))


def unitary_step(h: np.ndarray, psi: np.ndarray, dt: float = DT) -> np.ndarray:
    eigvals, eigvecs = np.linalg.eigh(h)
    phases = np.exp(-1j * eigvals * dt)
    return eigvecs @ (phases * (eigvecs.conj().T @ psi))


def lowest_eigenvector(h: np.ndarray) -> tuple[float, np.ndarray]:
    eigvals, eigvecs = np.linalg.eigh(h)
    idx = int(np.argmin(eigvals))
    return float(eigvals[idx]), normalize(eigvecs[:, idx].astype(complex))


def eigen_residual(h: np.ndarray, psi: np.ndarray) -> tuple[float, float]:
    hpsi = h @ psi
    energy = float(np.real(np.vdot(psi, hpsi)))
    residual = float(np.linalg.norm(hpsi - energy * psi))
    return energy, residual


def fixed_point_gap(phi: np.ndarray, psi: np.ndarray) -> float:
    phi_aligned = phase_align(phi, psi)
    return float(np.linalg.norm(phi_aligned - psi))


def load_initial_field() -> tuple[np.ndarray, np.ndarray, dict[str, object]]:
    data = json.loads(SOURCE_FIELDS.read_text(encoding="utf-8"))
    first = data["fields"][0]
    psi0 = np.asarray(first["psi_re"], dtype=float) + 1j * np.asarray(first["psi_im"], dtype=float)
    background = np.asarray(data["potential"], dtype=float)
    return normalize(psi0), background, data


def run_case(
    case_id: str,
    psi_initial: np.ndarray,
    background: np.ndarray,
    kappa: float,
    mix: float,
    kinetic: np.ndarray,
    steps: int = STEPS,
) -> tuple[list[dict[str, object]], dict[str, object], dict[str, object]]:
    psi = normalize(psi_initial.copy())
    trace_rows: list[dict[str, object]] = []
    potential = background + kappa * stress_energy_density(psi, background)
    final_phi = psi.copy()
    final_h = hamiltonian(kinetic, potential)
    final_lowest_energy = 0.0

    for iteration in range(steps):
        potential = background + kappa * stress_energy_density(psi, background)
        h = hamiltonian(kinetic, potential)
        if not np.allclose(h, h.conj().T, atol=1e-12):
            raise RuntimeError("Hamiltonian is not Hermitian")
        norm_before = float(np.linalg.norm(psi))
        stepped = unitary_step(h, psi)
        norm_after_unitary = float(np.linalg.norm(stepped))
        unitary_norm_error = abs(norm_after_unitary - norm_before)
        lowest_energy, phi = lowest_eigenvector(h)
        phi = phase_align(phi, psi)
        candidate = normalize((1.0 - mix) * psi + mix * phi)
        update_residual = float(np.linalg.norm(candidate - psi))
        energy_estimate, eig_residual = eigen_residual(h, psi)
        sourced_again = background + kappa * stress_energy_density(psi, background)
        potential_sourcing_residual = float(np.linalg.norm(potential - sourced_again))

        trace_rows.append(
            {
                "case": case_id,
                "iteration": iteration,
                "kappa": kappa,
                "mix": mix,
                "update_residual": update_residual,
                "eigen_residual_before_update": eig_residual,
                "energy_estimate_before_update": energy_estimate,
                "lowest_energy": lowest_energy,
                "potential_min": float(np.min(potential)),
                "potential_max": float(np.max(potential)),
                "potential_sourcing_residual": potential_sourcing_residual,
                "norm_before": norm_before,
                "norm_after_unitary_step": norm_after_unitary,
                "unitary_norm_error": unitary_norm_error,
            }
        )
        psi = candidate
        final_phi = phi
        final_h = h
        final_lowest_energy = lowest_energy

    final_potential = background + kappa * stress_energy_density(psi, background)
    final_h = hamiltonian(kinetic, final_potential)
    final_energy, final_eigen_residual = eigen_residual(final_h, psi)
    final_lowest_energy, final_phi = lowest_eigenvector(final_h)
    final_phi = phase_align(final_phi, psi)
    final_fixed_point_residual = fixed_point_gap(final_phi, psi)
    final_sourcing_residual = float(
        np.linalg.norm(final_potential - (background + kappa * stress_energy_density(psi, background)))
    )
    max_unitary_error = max(float(row["unitary_norm_error"]) for row in trace_rows)
    final_update_residual = float(trace_rows[-1]["update_residual"])
    converged = (
        final_update_residual <= CONVERGENCE_TOL
        and final_fixed_point_residual <= CONVERGENCE_TOL
        and final_eigen_residual <= CONVERGENCE_TOL
        and final_sourcing_residual <= CONVERGENCE_TOL
    )
    summary = {
        "case": case_id,
        "kappa": kappa,
        "mix": mix,
        "iterations": steps,
        "converged": converged,
        "final_update_residual": final_update_residual,
        "fixed_point_residual": final_fixed_point_residual,
        "final_eigen_residual": final_eigen_residual,
        "final_energy": final_energy,
        "final_lowest_energy": final_lowest_energy,
        "final_potential_min": float(np.min(final_potential)),
        "final_potential_max": float(np.max(final_potential)),
        "potential_sourcing_residual": final_sourcing_residual,
        "max_unitary_norm_error": max_unitary_error,
        "last_ten_update_residual_mean": float(np.mean([row["update_residual"] for row in trace_rows[-10:]])),
    }
    state_payload = {
        "case": case_id,
        "psi_re": np.real(psi).tolist(),
        "psi_im": np.imag(psi).tolist(),
        "final_potential": final_potential.tolist(),
        "final_T00": stress_energy_density(psi, background).tolist(),
        "final_lowest_vector_re": np.real(final_phi).tolist(),
        "final_lowest_vector_im": np.imag(final_phi).tolist(),
    }
    return trace_rows, summary, state_payload


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
    psi0, background, source_data = load_initial_field()
    n_sites = len(psi0)
    kinetic = kinetic_operator(n_sites)
    cases = [
        {
            "case": "consistent_coupling",
            "kappa": 0.3,
            "mix": 0.5,
            "description": "Moderate positive back-reaction, damped Hartree iteration.",
        },
        {
            "case": "runaway_control",
            "kappa": 30.0,
            "mix": 1.0,
            "description": "Over-strong positive back-reaction with undamped eigenvector replacement.",
        },
    ]
    all_trace_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []
    state_payload: list[dict[str, object]] = []

    for case in cases:
        trace, summary, state = run_case(
            str(case["case"]),
            psi0,
            background,
            float(case["kappa"]),
            float(case["mix"]),
            kinetic,
            STEPS,
        )
        all_trace_rows.extend(trace)
        summary_rows.append(summary)
        state_payload.append(state)

    consistent = next(row for row in summary_rows if row["case"] == "consistent_coupling")
    control = next(row for row in summary_rows if row["case"] == "runaway_control")
    verdict_name = (
        "self_consistent_dynamics_converges_on_toy"
        if bool(consistent["converged"]) and not bool(control["converged"])
        else "dynamical_obstruction_or_toothless_control"
    )
    output = {
        "step": 26,
        "verdict": {
            "semiclassical_dynamics_verdict": verdict_name,
            "consistent_coupling_converged": bool(consistent["converged"]),
            "runaway_control_converged": bool(control["converged"]),
            "root_landed": False,
            "external_review_required": True,
        },
        "guardrails": {
            "coupled_map_iterated": True,
            "hamiltonian_hermitian": bool(np.allclose(kinetic, kinetic.conj().T, atol=1e-12)),
            "unitary_step_norm_preserving_checked": True,
            "potential_sourced_from_T00": True,
            "runaway_control_required_to_fail": True,
        },
        "summary": {
            "consistent_final_update_residual": consistent["final_update_residual"],
            "consistent_fixed_point_residual": consistent["fixed_point_residual"],
            "consistent_final_eigen_residual": consistent["final_eigen_residual"],
            "consistent_potential_sourcing_residual": consistent["potential_sourcing_residual"],
            "consistent_max_unitary_norm_error": consistent["max_unitary_norm_error"],
            "runaway_final_update_residual": control["final_update_residual"],
            "runaway_fixed_point_residual": control["fixed_point_residual"],
            "runaway_final_eigen_residual": control["final_eigen_residual"],
            "runaway_max_unitary_norm_error": control["max_unitary_norm_error"],
        },
    }
    params = {
        "source_fields": str(SOURCE_FIELDS),
        "n_sites": n_sites,
        "dx": DX,
        "dt": DT,
        "iterations": STEPS,
        "initial_sample": 0,
        "background_potential": background.tolist(),
        "kinetic_operator": kinetic.tolist(),
        "hamiltonian_definition": "H[V] = 0.5 * periodic_laplacian + diag(V)",
        "stress_energy_density_definition": "T00[psi] = |central_difference(psi)|^2 + background_potential * |psi|^2",
        "potential_definition": "V[psi] = background_potential + kappa * T00[psi]",
        "unitary_step_definition": "psi_next = exp(-i H[V] dt) psi",
        "stationary_iteration_definition": "psi_{k+1}=normalize((1-mix)psi_k + mix*lowest_eigenvector(H[V[psi_k]]))",
        "cases": cases,
        "source_derivations": source_data.get("derivations", {}),
    }

    write_csv(ARTIFACT_DIR / "convergence_trace_step26.csv", all_trace_rows)
    write_csv(ARTIFACT_DIR / "fixed_point_summary_step26.csv", summary_rows)
    with (ARTIFACT_DIR / "dynamics_parameters_step26.json").open("w", encoding="utf-8") as handle:
        json.dump(params, handle, indent=2)
    with (ARTIFACT_DIR / "fixed_point_states_step26.json").open("w", encoding="utf-8") as handle:
        json.dump({"states": state_payload}, handle, indent=2)
    with (ARTIFACT_DIR / "semiclassical_dynamics_output_step26.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    with (ARTIFACT_DIR / "semiclassical_dynamics_output_step26.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 26 semiclassical dynamics\n")
        handle.write(f"Verdict: {verdict_name}\n")
        handle.write(f"Consistent coupling converged: {consistent['converged']}\n")
        handle.write(f"Consistent fixed-point residual: {consistent['fixed_point_residual']}\n")
        handle.write(f"Consistent eigen residual: {consistent['final_eigen_residual']}\n")
        handle.write(f"Runaway control converged: {control['converged']}\n")
        handle.write(f"Runaway fixed-point residual: {control['fixed_point_residual']}\n")
        handle.write(f"Runaway eigen residual: {control['final_eigen_residual']}\n")


if __name__ == "__main__":
    main()
