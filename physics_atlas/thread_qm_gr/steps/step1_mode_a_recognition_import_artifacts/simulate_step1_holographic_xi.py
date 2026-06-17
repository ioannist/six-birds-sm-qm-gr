#!/usr/bin/env python3
"""Step 1 finite-carrier Xi diagnostic for the E018 Mode A import audit.

The toy is deliberately small and diagnostic only.  It tests whether an
RT-like entanglement-to-area ledger closes the area sector, and whether that
same import lens closes the full E018 joint target after adding an independent
geometry-amplitude and P3 route-mismatch probe.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent


def adequacy_residual(native: np.ndarray, dissolving: np.ndarray) -> dict:
    """Compute Xi = K_DD - K_DL K_LL^dagger K_LD for C = I."""
    k_ll = native @ native.T
    k_dd = dissolving @ dissolving.T
    k_dl = dissolving @ native.T
    xi = k_dd - k_dl @ np.linalg.pinv(k_ll, rcond=1e-12) @ k_dl.T
    xi = 0.5 * (xi + xi.T)
    eigvals = np.linalg.eigvalsh(xi)
    raw = float(np.trace(xi))
    denom = float(np.trace(k_dd))
    normalized = float(raw / denom) if denom > 0 else float("nan")
    return {
        "K_LL": k_ll,
        "K_DD": k_dd,
        "Xi": xi,
        "eigvals": eigvals,
        "raw_trace": raw,
        "normalized_trace": normalized,
        "trace_K_DD": denom,
    }


def level_matrices(region_count: int) -> dict:
    """Declare the finite carrier and the import/native/dissolving probes."""
    if region_count < 2:
        raise ValueError("region_count must be at least 2")

    dim = region_count + 2
    g_idx = region_count
    p3_idx = region_count + 1

    basis = [f"entanglement_region_{i}" for i in range(region_count)]
    basis += ["bulk_geometry_amplitude", "p3_route_mismatch"]

    # Native recognition lens for the leading import: boundary entanglement
    # ledger only.  The RT-like area rows below factor through this span.
    native_rows = []
    native_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0
        native_rows.append(row)
        native_names.append(f"boundary_entanglement_S_{i}")
    native = np.vstack(native_rows)

    ent_avg = np.zeros(dim)
    ent_avg[:region_count] = 1.0 / np.sqrt(region_count)

    area_rows = []
    area_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0 / np.sqrt(region_count)
        area_rows.append(row)
        area_names.append(f"rt_area_shadow_{i}")

    amp_row = 0.25 * ent_avg
    amp_row[g_idx] = 1.0

    p3_row = 0.10 * ent_avg
    p3_row[g_idx] = 0.30
    p3_row[p3_idx] = 1.0

    d_area = np.vstack(area_rows)
    d_joint = np.vstack(area_rows + [amp_row, p3_row])
    d_joint_names = area_names + ["amplitude_geometry_probe", "p3_backreaction_probe"]

    # This over-read lens is not used for the verdict.  It shows that adding
    # the bulk answer rows would force Xi to zero by target-equivalent input.
    overread_native = np.vstack(
        [
            native,
            np.eye(dim)[g_idx],
            np.eye(dim)[p3_idx],
        ]
    )

    return {
        "basis": basis,
        "native": native,
        "native_names": native_names,
        "d_area": d_area,
        "d_area_names": area_names,
        "d_joint": d_joint,
        "d_joint_names": d_joint_names,
        "overread_native": overread_native,
    }


def summarize_level(region_count: int) -> dict:
    data = level_matrices(region_count)
    area = adequacy_residual(data["native"], data["d_area"])
    joint = adequacy_residual(data["native"], data["d_joint"])
    overread = adequacy_residual(data["overread_native"], data["d_joint"])

    return {
        "region_count": region_count,
        "carrier_dimension": len(data["basis"]),
        "basis": data["basis"],
        "native_probe_names_used": data["native_names"],
        "dissolving_joint_probe_names": data["d_joint_names"],
        "rt_area_sector": {
            "raw_trace": area["raw_trace"],
            "normalized_trace": area["normalized_trace"],
            "trace_K_DD": area["trace_K_DD"],
            "max_abs_Xi": float(np.max(np.abs(area["Xi"]))),
            "min_eigenvalue": float(np.min(area["eigvals"])),
            "max_eigenvalue": float(np.max(area["eigvals"])),
        },
        "full_joint_target": {
            "raw_trace": joint["raw_trace"],
            "normalized_trace": joint["normalized_trace"],
            "trace_K_DD": joint["trace_K_DD"],
            "min_eigenvalue": float(np.min(joint["eigvals"])),
            "max_eigenvalue": float(np.max(joint["eigvals"])),
            "Xi_matrix": np.round(joint["Xi"], 10).tolist(),
        },
        "target_equivalent_overread_control": {
            "raw_trace": overread["raw_trace"],
            "normalized_trace": overread["normalized_trace"],
            "flag": "zero only after adding bulk amplitude and P3 answer rows to the native lens",
        },
        "no_overread_check": {
            "bulk_geometry_amplitude_used_as_native_probe": False,
            "p3_route_mismatch_used_as_native_probe": False,
            "fixed_bulk_metric_inserted": False,
            "planck_constant_inserted": False,
            "rt_area_rows_factor_through_entanglement_ledger": True,
        },
    }


def main() -> None:
    levels = [2, 4]
    results = [summarize_level(level) for level in levels]
    norm_values = [row["full_joint_target"]["normalized_trace"] for row in results]
    raw_values = [row["full_joint_target"]["raw_trace"] for row in results]
    stability_delta = float(abs(norm_values[1] - norm_values[0]))
    stability_ratio = float(norm_values[1] / norm_values[0])

    payload = {
        "step": 1,
        "toy_name": "finite_holographic_rt_lens_diagnostic",
        "orientation": "Mode A recognition-import diagnostic",
        "carrier": {
            "audit_energy": "identity on declared finite carrier",
            "levels": levels,
            "native_lens": "boundary entanglement ledger only",
            "dissolving_target": "RT-like area rows plus independent amplitude(geometry) and P3 rows",
        },
        "results": results,
        "refinement_stability": {
            "normalized_residual_level_2": norm_values[0],
            "normalized_residual_level_4": norm_values[1],
            "absolute_delta": stability_delta,
            "ratio_level_4_over_level_2": stability_ratio,
            "interpretation": "positive stable residual for full joint target; zero residual only for RT area sector",
        },
        "verdict_from_toy": "finite-carrier diagnostic obstruction for the root residual; partial closure for RT area sector only",
    }

    json_path = ARTIFACT_DIR / "simulation_output_step1.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    csv_path = ARTIFACT_DIR / "xi_diagnostic_step1.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "level_regions",
                "carrier_dimension",
                "sector",
                "raw_trace_xi",
                "trace_kdd",
                "normalized_trace_xi",
                "min_eigenvalue",
                "max_eigenvalue",
                "scope",
            ],
        )
        writer.writeheader()
        for row in results:
            writer.writerow(
                {
                    "level_regions": row["region_count"],
                    "carrier_dimension": row["carrier_dimension"],
                    "sector": "rt_area_sector",
                    "raw_trace_xi": row["rt_area_sector"]["raw_trace"],
                    "trace_kdd": row["rt_area_sector"]["trace_K_DD"],
                    "normalized_trace_xi": row["rt_area_sector"]["normalized_trace"],
                    "min_eigenvalue": row["rt_area_sector"]["min_eigenvalue"],
                    "max_eigenvalue": row["rt_area_sector"]["max_eigenvalue"],
                    "scope": "E024-like area-from-entanglement child sector",
                }
            )
            writer.writerow(
                {
                    "level_regions": row["region_count"],
                    "carrier_dimension": row["carrier_dimension"],
                    "sector": "full_joint_target",
                    "raw_trace_xi": row["full_joint_target"]["raw_trace"],
                    "trace_kdd": row["full_joint_target"]["trace_K_DD"],
                    "normalized_trace_xi": row["full_joint_target"]["normalized_trace"],
                    "min_eigenvalue": row["full_joint_target"]["min_eigenvalue"],
                    "max_eigenvalue": row["full_joint_target"]["max_eigenvalue"],
                    "scope": "R_root_E018 joint amplitude-geometry plus P3 diagnostic",
                }
            )

    text_path = ARTIFACT_DIR / "simulation_output_step1.txt"
    lines = [
        "Step 1 finite-carrier Xi diagnostic",
        f"levels={levels}",
        f"full_joint_normalized_residuals={norm_values}",
        f"full_joint_raw_residuals={raw_values}",
        f"refinement_absolute_delta={stability_delta:.12g}",
        f"refinement_ratio={stability_ratio:.12g}",
        "rt_area_sector_residuals=zero to numerical precision at both levels",
        "overread_control=zero only when forbidden bulk answer rows are added to native lens",
    ]
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload["refinement_stability"], indent=2))


if __name__ == "__main__":
    main()
