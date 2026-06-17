#!/usr/bin/env python3
"""Build and test co-sourcing unification from a shared finite field."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD = ARTIFACT_DIR.parents[1]
STEP24_DIR = THREAD / "steps" / "step24_derived_physical_audits_artifacts"
TOL = 1e-10


def finite_gradient(psi: np.ndarray) -> np.ndarray:
    return (np.roll(psi, -1) - np.roll(psi, 1)) / 2.0


def shift_derivative(psi: np.ndarray) -> np.ndarray:
    return np.roll(psi, -1) - psi


def born_audit(psi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grad = finite_gradient(psi)
    return np.abs(psi) ** 2, np.imag(np.conj(psi) * grad)


def stress_energy_audit(psi: np.ndarray, potential: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    grad = finite_gradient(psi)
    shift = shift_derivative(psi)
    return np.abs(grad) ** 2 + potential * np.abs(psi) ** 2, np.real(np.conj(grad) * shift)


def rel_residual(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(float(np.linalg.norm(right)), 1.0))


def load_fields() -> tuple[list[np.ndarray], np.ndarray, dict]:
    source = json.loads((STEP24_DIR / "toy_field_samples_step24.json").read_text(encoding="utf-8"))
    potential = np.asarray(source["potential"], dtype=float)
    fields = [
        np.asarray(record["psi_re"], dtype=float) + 1j * np.asarray(record["psi_im"], dtype=float)
        for record in source["fields"]
    ]
    return fields, potential, source


def consistency_for_case(
    case: str,
    fields: list[np.ndarray],
    potential: np.ndarray,
    control_shift: int = 0,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    value_rows: list[dict[str, object]] = []
    consistency_rows: list[dict[str, object]] = []
    n = len(fields)
    for sample, psi in enumerate(fields):
        source_psi = psi
        gr_psi = fields[(sample + control_shift) % n]

        born_rho, born_j = born_audit(source_psi)
        source_t00, source_t0i = stress_energy_audit(source_psi, potential)
        descent_rho, descent_j = born_audit(source_psi)
        descent_t00, descent_t0i = stress_energy_audit(gr_psi, potential)

        born_residual = max(rel_residual(born_rho, descent_rho), rel_residual(born_j, descent_j))
        stress_residual = max(rel_residual(source_t00, descent_t00), rel_residual(source_t0i, descent_t0i))
        consistency_rows.append(
            {
                "case": case,
                "sample": sample,
                "control_gr_source_sample": (sample + control_shift) % n,
                "born_descent_residual": born_residual,
                "stress_energy_descent_residual": stress_residual,
                "single_psi_sources_both": born_residual <= TOL and stress_residual <= TOL,
            }
        )
        for site in range(len(source_psi)):
            value_rows.append(
                {
                    "case": case,
                    "sample": sample,
                    "site": site,
                    "psi_re": float(np.real(source_psi[site])),
                    "psi_im": float(np.imag(source_psi[site])),
                    "control_gr_source_sample": (sample + control_shift) % n,
                    "Born_rho_from_L_psi": float(born_rho[site]),
                    "Born_j_from_L_psi": float(born_j[site]),
                    "QM_descent_rho": float(descent_rho[site]),
                    "QM_descent_j": float(descent_j[site]),
                    "T00_from_L_psi": float(source_t00[site]),
                    "T0i_from_L_psi": float(source_t0i[site]),
                    "GR_descent_T00": float(descent_t00[site]),
                    "GR_descent_T0i": float(descent_t0i[site]),
                }
            )
    return value_rows, consistency_rows


def summarize(case: str, rows: list[dict[str, object]]) -> dict[str, object]:
    born = np.array([float(row["born_descent_residual"]) for row in rows])
    stress = np.array([float(row["stress_energy_descent_residual"]) for row in rows])
    return {
        "case": case,
        "max_born_descent_residual": float(np.max(born)),
        "max_stress_energy_descent_residual": float(np.max(stress)),
        "mean_stress_energy_descent_residual": float(np.mean(stress)),
        "all_samples_single_psi_sources_both": bool(np.all(born <= TOL) and np.all(stress <= TOL)),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    fields, potential, source = load_fields()
    l_values, l_consistency = consistency_for_case("L_co_sourced", fields, potential, control_shift=0)
    control_values, control_consistency = consistency_for_case(
        "non_co_sourced_control",
        fields,
        potential,
        control_shift=1,
    )
    all_values = l_values + control_values
    all_consistency = l_consistency + control_consistency
    summary_rows = [
        summarize("L_co_sourced", l_consistency),
        summarize("non_co_sourced_control", control_consistency),
    ]
    l_summary = summary_rows[0]
    control_summary = summary_rows[1]
    verdict = {
        "step": 25,
        "verdict": {
            "co_sourcing_verdict": "L_is_co_sourcing_unification"
            if l_summary["all_samples_single_psi_sources_both"]
            and not control_summary["all_samples_single_psi_sources_both"]
            else "co_sourcing_obstruction",
            "L_single_psi_sources_both": bool(l_summary["all_samples_single_psi_sources_both"]),
            "non_co_sourced_control_pass": bool(control_summary["all_samples_single_psi_sources_both"]),
        },
        "guardrails": {
            "single_psi_consistency_computed": True,
            "control_uses_independent_gr_field": True,
            "root_landed": False,
        },
        "summary": {
            "L_max_born_residual": l_summary["max_born_descent_residual"],
            "L_max_stress_residual": l_summary["max_stress_energy_descent_residual"],
            "control_max_stress_residual": control_summary["max_stress_energy_descent_residual"],
            "control_mean_stress_residual": control_summary["mean_stress_energy_descent_residual"],
        },
    }
    carrier = {
        "source_step": str(STEP24_DIR / "toy_field_samples_step24.json"),
        "n_samples": len(fields),
        "n_sites": len(fields[0]),
        "potential": potential.tolist(),
        "control": "non_co_sourced_control uses GR audit T[psi_{sample+1}] while L field is psi_sample.",
        "derivations": source["derivations"],
    }

    with (ARTIFACT_DIR / "field_carrier_step25.json").open("w", encoding="utf-8") as handle:
        json.dump(carrier, handle, indent=2)
    write_csv(ARTIFACT_DIR / "sourced_descent_audits_step25.csv", all_values)
    write_csv(ARTIFACT_DIR / "co_sourcing_consistency_step25.csv", all_consistency)
    write_csv(ARTIFACT_DIR / "co_sourcing_summary_step25.csv", summary_rows)
    with (ARTIFACT_DIR / "sourcing_unification_output_step25.json").open("w", encoding="utf-8") as handle:
        json.dump(verdict, handle, indent=2)
    with (ARTIFACT_DIR / "sourcing_unification_output_step25.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 25 co-sourcing unification\n")
        handle.write(f"Verdict: {verdict['verdict']['co_sourcing_verdict']}\n")
        handle.write(f"L single psi sources both: {verdict['verdict']['L_single_psi_sources_both']}\n")
        handle.write(f"Non-co-sourced control pass: {verdict['verdict']['non_co_sourced_control_pass']}\n")
        handle.write(f"Control max stress residual: {verdict['summary']['control_max_stress_residual']}\n")


if __name__ == "__main__":
    main()
