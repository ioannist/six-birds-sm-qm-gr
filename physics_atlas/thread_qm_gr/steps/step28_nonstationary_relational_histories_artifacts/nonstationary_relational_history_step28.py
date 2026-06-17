#!/usr/bin/env python3
"""Step 28: non-stationary relational history with self-sourced potentials."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP24_DIR = THREAD_DIR / "steps" / "step24_derived_physical_audits_artifacts"
STEP26_DIR = THREAD_DIR / "steps" / "step26_semiclassical_dynamics_artifacts"

M_CLOCK = 16
INITIAL_SAMPLE = 2
TOL = 1e-10


def normalize(psi: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(psi))
    if norm <= TOL:
        raise ValueError("cannot normalize zero field")
    return psi / norm


def phase_align(candidate: np.ndarray, reference: np.ndarray) -> np.ndarray:
    overlap = np.vdot(candidate, reference)
    if abs(overlap) <= TOL:
        return candidate
    return candidate * np.exp(-1j * np.angle(overlap))


def phase_invariant_gap(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(phase_align(a, b) - b))


def central_gradient(psi: np.ndarray) -> np.ndarray:
    return (np.roll(psi, -1) - np.roll(psi, 1)) / 2.0


def stress_energy_density(psi: np.ndarray, background: np.ndarray) -> np.ndarray:
    grad = central_gradient(psi)
    return (np.abs(grad) ** 2 + background * np.abs(psi) ** 2).real


def hamiltonian(kinetic: np.ndarray, potential: np.ndarray) -> np.ndarray:
    return kinetic + np.diag(potential)


def unitary_from_h(h: np.ndarray, dt: float) -> np.ndarray:
    eigvals, eigvecs = np.linalg.eigh(h)
    return eigvecs @ np.diag(np.exp(-1j * eigvals * dt)) @ eigvecs.conj().T


def eigen_residual(h: np.ndarray, psi: np.ndarray) -> tuple[float, float]:
    hpsi = h @ psi
    energy = float(np.real(np.vdot(psi, hpsi)))
    residual = float(np.linalg.norm(hpsi - energy * psi))
    return energy, residual


def load_sources() -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    fields = json.loads((STEP24_DIR / "toy_field_samples_step24.json").read_text(encoding="utf-8"))
    params = json.loads((STEP26_DIR / "dynamics_parameters_step26.json").read_text(encoding="utf-8"))
    record = fields["fields"][INITIAL_SAMPLE]
    psi0 = np.asarray(record["psi_re"], dtype=float) + 1j * np.asarray(record["psi_im"], dtype=float)
    background = np.asarray(params["background_potential"], dtype=float)
    kinetic = np.asarray(params["kinetic_operator"], dtype=float)
    kappa = float(next(case["kappa"] for case in params["cases"] if case["case"] == "consistent_coupling"))
    dt = float(params["dt"])
    return normalize(psi0), background, kinetic, kappa, dt


def build_history(
    psi0: np.ndarray,
    background: np.ndarray,
    kinetic: np.ndarray,
    kappa: float,
    dt: float,
    m_clock: int,
) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
    states = [normalize(psi0)]
    potentials: list[np.ndarray] = []
    hamiltonians: list[np.ndarray] = []
    unitaries: list[np.ndarray] = []
    for step in range(m_clock - 1):
        psi = states[-1]
        potential = background + kappa * stress_energy_density(psi, background)
        h = hamiltonian(kinetic, potential)
        if not np.allclose(h, h.conj().T, atol=1e-12):
            raise RuntimeError("non-Hermitian field Hamiltonian")
        unitary = unitary_from_h(h, dt)
        next_psi = normalize(unitary @ psi)
        potentials.append(potential)
        hamiltonians.append(h)
        unitaries.append(unitary)
        states.append(next_psi)
    final_potential = background + kappa * stress_energy_density(states[-1], background)
    potentials.append(final_potential)
    hamiltonians.append(hamiltonian(kinetic, final_potential))
    return states, potentials, hamiltonians, unitaries


def build_constraint(unitaries: list[np.ndarray], control: str = "generated") -> np.ndarray:
    n_field = unitaries[0].shape[0]
    rows = len(unitaries) * n_field
    cols = (len(unitaries) + 1) * n_field
    c = np.zeros((rows, cols), dtype=complex)
    for step, unitary in enumerate(unitaries):
        row = slice(step * n_field, (step + 1) * n_field)
        current = slice(step * n_field, (step + 1) * n_field)
        nxt = slice((step + 1) * n_field, (step + 2) * n_field)
        generator = np.eye(n_field, dtype=complex) if control == "identity" else unitary
        c[row, current] = -generator
        c[row, nxt] = np.eye(n_field, dtype=complex)
    return c


def singular_summary(c: np.ndarray, history_state: np.ndarray, tolerance: float = 1e-8) -> dict[str, object]:
    singular_values = np.linalg.svd(c, compute_uv=False)
    rank = int(np.sum(singular_values > tolerance))
    null_dim = int(c.shape[1] - rank)
    residual = float(np.linalg.norm(c @ history_state))
    return {
        "rank_tol_1e_minus_8": rank,
        "null_dim_tol_1e_minus_8": null_dim,
        "min_singular_value": float(np.min(singular_values)),
        "max_singular_value": float(np.max(singular_values)),
        "history_constraint_residual": residual,
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
    psi0, background, kinetic, kappa, dt = load_sources()
    states, potentials, hamiltonians, unitaries = build_history(
        psi0, background, kinetic, kappa, dt, M_CLOCK
    )
    n_field = len(states[0])
    history_state = normalize(np.concatenate(states) / np.sqrt(M_CLOCK))
    c_generated = build_constraint(unitaries, control="generated")
    c_control = build_constraint(unitaries, control="identity")
    generated_summary = singular_summary(c_generated, history_state)
    control_summary = singular_summary(c_control, history_state)

    history_rows: list[dict[str, object]] = []
    state_change_gaps: list[float] = []
    potential_change_gaps: list[float] = []
    eigen_gaps: list[float] = []
    unitary_norm_errors: list[float] = []
    for step, psi in enumerate(states):
        h = hamiltonians[step]
        energy, eig_residual = eigen_residual(h, psi)
        eigen_gaps.append(eig_residual)
        if step < len(unitaries):
            next_psi = states[step + 1]
            generated_next = normalize(unitaries[step] @ psi)
            evolution_residual = float(np.linalg.norm(generated_next - next_psi))
            norm_error = abs(float(np.linalg.norm(generated_next)) - float(np.linalg.norm(psi)))
            state_change = phase_invariant_gap(next_psi, psi)
            potential_change = float(np.linalg.norm(potentials[step + 1] - potentials[step]))
            state_change_gaps.append(state_change)
            potential_change_gaps.append(potential_change)
            unitary_norm_errors.append(norm_error)
        else:
            evolution_residual = 0.0
            norm_error = 0.0
            state_change = 0.0
            potential_change = 0.0
        history_rows.append(
            {
                "clock_t": step,
                "field_norm": float(np.linalg.norm(psi)),
                "energy_estimate": energy,
                "eigen_residual": eig_residual,
                "is_stationary_eigenstate_tol_1e_minus_8": bool(eig_residual <= 1e-8),
                "state_change_to_next_phase_invariant": state_change,
                "potential_change_to_next": potential_change,
                "single_step_evolution_residual": evolution_residual,
                "unitary_norm_error": norm_error,
                "potential_min": float(np.min(potentials[step])),
                "potential_max": float(np.max(potentials[step])),
            }
        )

    relational_rows: list[dict[str, object]] = []
    readout_residuals: list[float] = []
    potential_residuals: list[float] = []
    for step, expected in enumerate(states):
        component = history_state[step * n_field : (step + 1) * n_field]
        conditioned = normalize(component)
        readout_residual = float(np.linalg.norm(conditioned - expected))
        sourced_potential = background + kappa * stress_energy_density(conditioned, background)
        potential_residual = float(np.linalg.norm(sourced_potential - potentials[step]))
        readout_residuals.append(readout_residual)
        potential_residuals.append(potential_residual)
        relational_rows.append(
            {
                "clock_t": step,
                "conditioned_field_norm": float(np.linalg.norm(conditioned)),
                "field_readout_residual": readout_residual,
                "relational_potential_residual": potential_residual,
                "potential_min": float(np.min(sourced_potential)),
                "potential_max": float(np.max(sourced_potential)),
            }
        )

    singular_rows: list[dict[str, object]] = []
    for case, operator in [("generated_relational_constraint", c_generated), ("wrong_identity_generator_control", c_control)]:
        values = np.linalg.svd(operator, compute_uv=False)
        for idx, value in enumerate(values):
            singular_rows.append(
                {
                    "case": case,
                    "singular_index": idx,
                    "singular_value": float(value),
                    "near_zero_tol_1e_minus_8": bool(value <= 1e-8),
                }
            )

    residual_rows = [
        {
            "case": "generated_relational_constraint",
            "constraint_rows": c_generated.shape[0],
            "constraint_cols": c_generated.shape[1],
            "rank_tol_1e_minus_8": generated_summary["rank_tol_1e_minus_8"],
            "null_dim_tol_1e_minus_8": generated_summary["null_dim_tol_1e_minus_8"],
            "history_constraint_residual": generated_summary["history_constraint_residual"],
            "passes_constraint": generated_summary["history_constraint_residual"] <= 1e-8,
        },
        {
            "case": "wrong_identity_generator_control",
            "constraint_rows": c_control.shape[0],
            "constraint_cols": c_control.shape[1],
            "rank_tol_1e_minus_8": control_summary["rank_tol_1e_minus_8"],
            "null_dim_tol_1e_minus_8": control_summary["null_dim_tol_1e_minus_8"],
            "history_constraint_residual": control_summary["history_constraint_residual"],
            "passes_constraint": control_summary["history_constraint_residual"] <= 1e-8,
        },
    ]

    nonstationary = (
        min(eigen_gaps) > 1e-2
        and max(state_change_gaps) > 1e-2
        and max(potential_change_gaps) > 1e-4
    )
    verdict_name = (
        "nonstationary_relational_history_constraint_consistent_on_toy"
        if nonstationary
        and generated_summary["history_constraint_residual"] <= 1e-8
        and control_summary["history_constraint_residual"] > 1e-2
        and max(readout_residuals) <= 1e-8
        and max(potential_residuals) <= 1e-8
        else "nonstationary_relational_constraint_obstruction"
    )

    np.savez(
        ARTIFACT_DIR / "constraint_operators_step28.npz",
        C_generated=c_generated,
        C_wrong_identity_control=c_control,
        history_state=history_state,
        unitaries=np.asarray(unitaries),
        potentials=np.asarray(potentials),
        states=np.asarray(states),
    )
    write_csv(ARTIFACT_DIR / "nonstationary_history_diagnostics_step28.csv", history_rows)
    write_csv(ARTIFACT_DIR / "constraint_singular_values_step28.csv", singular_rows)
    write_csv(ARTIFACT_DIR / "constraint_residuals_step28.csv", residual_rows)
    write_csv(ARTIFACT_DIR / "relational_readout_step28.csv", relational_rows)

    history_payload = {
        "source_step24": str(STEP24_DIR / "toy_field_samples_step24.json"),
        "source_step26": str(STEP26_DIR / "dynamics_parameters_step26.json"),
        "initial_sample": INITIAL_SAMPLE,
        "clock_states": M_CLOCK,
        "field_dim": n_field,
        "dt": dt,
        "kappa": kappa,
        "constraint_definition": "C rows encode psi_{t+1} - U_t psi_t = 0 for t=0..M-2.",
        "U_t_definition": "U_t = exp(-i H[V_t] dt), V_t = background + kappa*T00[psi_t].",
        "control_definition": "wrong_identity_generator_control uses psi_{t+1} - psi_t = 0 on the same non-stationary history.",
        "states": [
            {"clock_t": idx, "psi_re": np.real(psi).tolist(), "psi_im": np.imag(psi).tolist()}
            for idx, psi in enumerate(states)
        ],
        "potentials": [
            {"clock_t": idx, "potential": potential.tolist()} for idx, potential in enumerate(potentials)
        ],
    }
    with (ARTIFACT_DIR / "nonstationary_history_step28.json").open("w", encoding="utf-8") as handle:
        json.dump(history_payload, handle, indent=2)

    output = {
        "step": 28,
        "verdict": {
            "nonstationary_relational_verdict": verdict_name,
            "history_is_nonstationary": bool(nonstationary),
            "generated_constraint_passes": bool(generated_summary["history_constraint_residual"] <= 1e-8),
            "wrong_generator_control_passes": bool(control_summary["history_constraint_residual"] <= 1e-8),
            "relational_readout_recovers_history": bool(max(readout_residuals) <= 1e-8),
            "relational_potential_recovers_sourcing": bool(max(potential_residuals) <= 1e-8),
            "root_landed": False,
            "external_review_required": True,
        },
        "summary": {
            "generated_constraint_residual": generated_summary["history_constraint_residual"],
            "generated_null_dim_tol_1e_minus_8": generated_summary["null_dim_tol_1e_minus_8"],
            "control_constraint_residual": control_summary["history_constraint_residual"],
            "max_field_readout_residual": max(readout_residuals),
            "max_relational_potential_residual": max(potential_residuals),
            "min_eigen_residual": min(eigen_gaps),
            "max_state_change_phase_invariant": max(state_change_gaps),
            "mean_state_change_phase_invariant": float(np.mean(state_change_gaps)),
            "max_potential_change": max(potential_change_gaps),
            "mean_potential_change": float(np.mean(potential_change_gaps)),
            "max_unitary_norm_error": max(unitary_norm_errors),
        },
        "guardrails": {
            "non_eigenstate_checked": True,
            "state_change_checked": True,
            "potential_change_checked": True,
            "constraint_residual_computed": True,
            "control_required_to_fail": True,
        },
    }
    with (ARTIFACT_DIR / "nonstationary_relational_history_output_step28.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    with (ARTIFACT_DIR / "nonstationary_relational_history_output_step28.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 28 non-stationary relational history\n")
        handle.write(f"Verdict: {verdict_name}\n")
        handle.write(f"History is non-stationary: {nonstationary}\n")
        handle.write(f"Generated constraint residual: {generated_summary['history_constraint_residual']}\n")
        handle.write(f"Control constraint residual: {control_summary['history_constraint_residual']}\n")
        handle.write(f"Max field readout residual: {max(readout_residuals)}\n")
        handle.write(f"Max potential residual: {max(potential_residuals)}\n")
        handle.write(f"Max state change: {max(state_change_gaps)}\n")
        handle.write(f"Max potential change: {max(potential_change_gaps)}\n")


if __name__ == "__main__":
    main()
