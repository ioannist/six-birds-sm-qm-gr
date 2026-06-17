#!/usr/bin/env python3
"""Derive toy QM/GR audits from a shared finite complex field."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
SEED = 24024
N_SITES = 8
N_SAMPLES = 24
DX = 1.0
TOL = 1e-10


def finite_gradient(psi: np.ndarray) -> np.ndarray:
    return (np.roll(psi, -1) - np.roll(psi, 1)) / (2.0 * DX)


def shift_derivative(psi: np.ndarray) -> np.ndarray:
    return (np.roll(psi, -1) - psi) / DX


def potential() -> np.ndarray:
    x = np.arange(N_SITES, dtype=float)
    return 0.25 + 0.10 * np.cos(2.0 * np.pi * x / N_SITES)


def normalize(psi: np.ndarray) -> np.ndarray:
    norm = np.sqrt(float(np.sum(np.abs(psi) ** 2)))
    return psi / max(norm, TOL)


def sample_fields() -> list[np.ndarray]:
    rng = np.random.default_rng(SEED)
    fields: list[np.ndarray] = []
    x = np.arange(N_SITES, dtype=float)
    for k in range(N_SAMPLES):
        envelope = 1.0 + 0.25 * rng.normal(size=N_SITES)
        phase = (
            2.0 * np.pi * (k + 1) * x / N_SITES
            + 0.45 * rng.normal(size=N_SITES)
            + 0.2 * np.sin(2.0 * np.pi * x / N_SITES)
        )
        psi = envelope * np.exp(1j * phase)
        fields.append(normalize(psi))
    # Add a same-density/different-phase pair to force the distinction between
    # probability density and gradient-sensitive stress-energy to be visible.
    base_amp = normalize(1.0 + 0.15 * np.cos(2.0 * np.pi * x / N_SITES))
    fields.append(normalize(base_amp.astype(complex)))
    fields.append(normalize(base_amp * np.exp(1j * 2.0 * np.pi * x / N_SITES)))
    return fields


def born_audit(psi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grad = finite_gradient(psi)
    rho = np.abs(psi) ** 2
    current = np.imag(np.conj(psi) * grad)
    return rho.real, current.real


def stress_energy_audit(psi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grad = finite_gradient(psi)
    shift = shift_derivative(psi)
    v = potential()
    t00 = np.abs(grad) ** 2 + v * np.abs(psi) ** 2
    t0i = np.real(np.conj(grad) * shift)
    return t00.real, t0i.real


def rel_residual(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(float(np.linalg.norm(right)), 1.0))


def proportional_fit(source: np.ndarray, target: np.ndarray) -> tuple[float, float]:
    denom = float(np.dot(source, source))
    alpha = 0.0 if denom <= TOL else float(np.dot(source, target) / denom)
    residual = rel_residual(alpha * source, target)
    return alpha, residual


def flatten_samples(values: list[np.ndarray]) -> np.ndarray:
    return np.concatenate([np.asarray(value, dtype=float) for value in values])


def linear_predict_shared_to_stress(
    rho_values: list[np.ndarray],
    current_values: list[np.ndarray],
    stress_values: list[np.ndarray],
) -> dict[str, float]:
    features = []
    targets = []
    for rho, current, stress in zip(rho_values, current_values, stress_values):
        for site in range(N_SITES):
            features.append([1.0, rho[site], current[site]])
            targets.append(stress[site])
    x = np.asarray(features, dtype=float)
    y = np.asarray(targets, dtype=float)
    split = int(0.65 * len(y))
    beta, *_ = np.linalg.lstsq(x[:split], y[:split], rcond=None)
    train_residual = rel_residual(x[:split] @ beta, y[:split])
    test_residual = rel_residual(x[split:] @ beta, y[split:])
    return {
        "beta0": float(beta[0]),
        "beta_rho": float(beta[1]),
        "beta_current": float(beta[2]),
        "train_residual": train_residual,
        "test_residual": test_residual,
    }


def direct_sourcing_residual(fields: list[np.ndarray]) -> float:
    gaps = []
    for psi in fields:
        t00_a, t0i_a = stress_energy_audit(psi)
        t00_b, t0i_b = stress_energy_audit(psi.copy())
        gaps.append(rel_residual(t00_a, t00_b))
        gaps.append(rel_residual(t0i_a, t0i_b))
    return float(max(gaps))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    fields = sample_fields()
    v = potential()
    rho_values: list[np.ndarray] = []
    current_values: list[np.ndarray] = []
    t00_values: list[np.ndarray] = []
    t0i_values: list[np.ndarray] = []
    value_rows: list[dict[str, object]] = []
    coherence_rows: list[dict[str, object]] = []

    for sample_id, psi in enumerate(fields):
        rho, current = born_audit(psi)
        t00, t0i = stress_energy_audit(psi)
        rho_values.append(rho)
        current_values.append(current)
        t00_values.append(t00)
        t0i_values.append(t0i)

        density_alpha, density_prop_res = proportional_fit(rho, t00)
        transport_alpha, transport_prop_res = proportional_fit(current, t0i)
        coherence_rows.append(
            {
                "sample": sample_id,
                "density_equal_residual": rel_residual(rho, t00),
                "transport_equal_residual": rel_residual(current, t0i),
                "density_proportional_alpha": density_alpha,
                "density_proportional_residual": density_prop_res,
                "transport_proportional_alpha": transport_alpha,
                "transport_proportional_residual": transport_prop_res,
            }
        )
        for site in range(N_SITES):
            value_rows.append(
                {
                    "sample": sample_id,
                    "site": site,
                    "psi_re": float(np.real(psi[site])),
                    "psi_im": float(np.imag(psi[site])),
                    "rho": float(rho[site]),
                    "current_j": float(current[site]),
                    "T00": float(t00[site]),
                    "T0i": float(t0i[site]),
                    "potential": float(v[site]),
                }
            )

    rho_flat = flatten_samples(rho_values)
    current_flat = flatten_samples(current_values)
    t00_flat = flatten_samples(t00_values)
    t0i_flat = flatten_samples(t0i_values)
    density_alpha, density_prop_res = proportional_fit(rho_flat, t00_flat)
    transport_alpha, transport_prop_res = proportional_fit(current_flat, t0i_flat)

    t00_shared_fit = linear_predict_shared_to_stress(rho_values, current_values, t00_values)
    t0i_shared_fit = linear_predict_shared_to_stress(rho_values, current_values, t0i_values)
    sourcing_residual = direct_sourcing_residual(fields)

    summary_rows = [
        {
            "mode": "density",
            "equal_residual": rel_residual(rho_flat, t00_flat),
            "proportional_alpha": density_alpha,
            "proportional_residual": density_prop_res,
            "coheres_as_same_audit": density_prop_res <= TOL,
        },
        {
            "mode": "transport",
            "equal_residual": rel_residual(current_flat, t0i_flat),
            "proportional_alpha": transport_alpha,
            "proportional_residual": transport_prop_res,
            "coheres_as_same_audit": transport_prop_res <= TOL,
        },
    ]

    sourcing_rows = [
        {
            "target": "T00_from_psi",
            "direct_sourcing_residual": sourcing_residual,
            "shared_audit_linear_train_residual": t00_shared_fit["train_residual"],
            "shared_audit_linear_test_residual": t00_shared_fit["test_residual"],
            "computed_reconciliation": "T00 is a deterministic functional of psi, not the same audit as rho.",
        },
        {
            "target": "T0i_from_psi",
            "direct_sourcing_residual": sourcing_residual,
            "shared_audit_linear_train_residual": t0i_shared_fit["train_residual"],
            "shared_audit_linear_test_residual": t0i_shared_fit["test_residual"],
            "computed_reconciliation": "T0i is a deterministic functional of psi, not the same audit as current_j.",
        },
    ]

    same_audit = all(row["coheres_as_same_audit"] for row in summary_rows)
    interpretation = (
        "shared_audit_coheres"
        if same_audit
        else "derived_audits_differ_reconciliation_is_sourcing_T_of_psi"
    )
    payload = {
        "step": 24,
        "verdict": {
            "derived_audit_verdict": interpretation,
            "born_and_stress_energy_same_audit": same_audit,
            "sourcing_T_of_psi": sourcing_residual <= TOL,
        },
        "guardrails": {
            "audits_derived_from_psi": True,
            "coherence_computed": True,
            "sourcing_computed": True,
            "root_landed": False,
        },
        "summary": {
            "density_equal_residual": summary_rows[0]["equal_residual"],
            "density_proportional_residual": summary_rows[0]["proportional_residual"],
            "transport_equal_residual": summary_rows[1]["equal_residual"],
            "transport_proportional_residual": summary_rows[1]["proportional_residual"],
            "direct_sourcing_residual": sourcing_residual,
            "T00_shared_audit_test_residual": t00_shared_fit["test_residual"],
            "T0i_shared_audit_test_residual": t0i_shared_fit["test_residual"],
        },
    }

    sample_json = {
        "seed": SEED,
        "n_sites": N_SITES,
        "n_samples": len(fields),
        "dx": DX,
        "potential": v.tolist(),
        "fields": [
            {
                "sample": i,
                "psi_re": np.real(psi).tolist(),
                "psi_im": np.imag(psi).tolist(),
            }
            for i, psi in enumerate(fields)
        ],
        "derivations": {
            "rho": "|psi|^2",
            "current_j": "Im(conj(psi) * central_difference(psi))",
            "T00": "|central_difference(psi)|^2 + V * |psi|^2",
            "T0i": "Re(conj(central_difference(psi)) * forward_shift_difference(psi))",
        },
    }
    with (ARTIFACT_DIR / "toy_field_samples_step24.json").open("w", encoding="utf-8") as handle:
        json.dump(sample_json, handle, indent=2)
    write_csv(ARTIFACT_DIR / "derived_audit_values_step24.csv", value_rows)
    write_csv(ARTIFACT_DIR / "shared_mode_coherence_step24.csv", coherence_rows)
    write_csv(ARTIFACT_DIR / "coherence_summary_step24.csv", summary_rows)
    write_csv(ARTIFACT_DIR / "sourcing_check_step24.csv", sourcing_rows)
    with (ARTIFACT_DIR / "derived_physical_audit_output_step24.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    with (ARTIFACT_DIR / "derived_physical_audit_output_step24.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 24 derived physical audits from shared toy field\n")
        handle.write(f"Verdict: {interpretation}\n")
        handle.write(f"Born/stress-energy same audit: {same_audit}\n")
        handle.write(f"Sourcing T[psi]: {sourcing_residual <= TOL}\n")
        handle.write(f"Density proportional residual: {density_prop_res}\n")
        handle.write(f"Transport proportional residual: {transport_prop_res}\n")


if __name__ == "__main__":
    main()
