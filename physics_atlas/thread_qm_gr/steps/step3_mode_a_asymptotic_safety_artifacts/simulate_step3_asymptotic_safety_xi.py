#!/usr/bin/env python3
"""Step 3 finite-carrier Xi diagnostic for the asymptotic-safety P3 import."""

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
        "K_DD": k_dd,
        "Xi": xi,
        "eigvals": eigvals,
        "raw_trace": raw,
        "normalized_trace": normalized,
        "trace_K_DD": denom,
    }


def level_matrices(region_count: int) -> dict:
    """Reuse the Step 1/2 carrier and declare an AS-like P3 lens."""
    if region_count < 2:
        raise ValueError("region_count must be at least 2")

    dim = region_count + 2
    g_idx = region_count
    p3_idx = region_count + 1
    basis = [f"entanglement_region_{i}" for i in range(region_count)]
    basis += ["bulk_geometry_amplitude", "p3_route_mismatch"]

    p3_row = np.zeros(dim)
    p3_row[p3_idx] = 1.0
    as_native = np.vstack([p3_row])
    as_names = ["uv_fixed_point_route_closure"]

    amp_row = np.zeros(dim)
    amp_row[g_idx] = 1.0

    area_rows = []
    area_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0 / np.sqrt(region_count)
        area_rows.append(row)
        area_names.append(f"rt_area_shadow_{i}")
    d_area = np.vstack(area_rows)
    d_amp = np.vstack([amp_row])
    d_p3 = np.vstack([p3_row])
    d_three_sector = np.vstack([d_area, d_amp, d_p3])

    return {
        "basis": basis,
        "as_native": as_native,
        "as_names": as_names,
        "d_area": d_area,
        "d_area_names": area_names,
        "d_amp": d_amp,
        "d_p3": d_p3,
        "d_three_sector": d_three_sector,
    }


def summarize_level(region_count: int) -> dict:
    data = level_matrices(region_count)
    as_p3 = adequacy_residual(data["as_native"], data["d_p3"])
    as_amp = adequacy_residual(data["as_native"], data["d_amp"])
    as_area = adequacy_residual(data["as_native"], data["d_area"])
    as_three = adequacy_residual(data["as_native"], data["d_three_sector"])

    return {
        "region_count": region_count,
        "carrier_dimension": len(data["basis"]),
        "basis": data["basis"],
        "as_native_probe_names_used": data["as_names"],
        "as_on_p3_route_mismatch": {
            "raw_trace": as_p3["raw_trace"],
            "normalized_trace": as_p3["normalized_trace"],
            "trace_K_DD": as_p3["trace_K_DD"],
            "min_eigenvalue": float(np.min(as_p3["eigvals"])),
            "max_eigenvalue": float(np.max(as_p3["eigvals"])),
            "Xi_matrix": np.round(as_p3["Xi"], 10).tolist(),
        },
        "as_on_amplitude_geometry": {
            "raw_trace": as_amp["raw_trace"],
            "normalized_trace": as_amp["normalized_trace"],
            "trace_K_DD": as_amp["trace_K_DD"],
            "min_eigenvalue": float(np.min(as_amp["eigvals"])),
            "max_eigenvalue": float(np.max(as_amp["eigvals"])),
            "Xi_matrix": np.round(as_amp["Xi"], 10).tolist(),
        },
        "as_on_area_shadow_price": {
            "raw_trace": as_area["raw_trace"],
            "normalized_trace": as_area["normalized_trace"],
            "trace_K_DD": as_area["trace_K_DD"],
            "min_eigenvalue": float(np.min(as_area["eigvals"])),
            "max_eigenvalue": float(np.max(as_area["eigvals"])),
            "Xi_matrix": np.round(as_area["Xi"], 10).tolist(),
        },
        "as_on_three_sector_uncoupled_reference": {
            "raw_trace": as_three["raw_trace"],
            "normalized_trace": as_three["normalized_trace"],
            "trace_K_DD": as_three["trace_K_DD"],
            "note": "AS closes only the P3 row in this uncoupled reference",
        },
        "no_overread_check": {
            "amplitude_geometry_used_in_as_native_lens": False,
            "boundary_entanglement_used_in_as_native_lens": False,
            "fixed_bulk_metric_inserted": False,
            "planck_constant_inserted": False,
            "as_lens_spans_only_p3_route_mismatch": True,
        },
    }


def main() -> None:
    levels = [2, 4]
    results = [summarize_level(level) for level in levels]

    p3_norms = [row["as_on_p3_route_mismatch"]["normalized_trace"] for row in results]
    amp_norms = [row["as_on_amplitude_geometry"]["normalized_trace"] for row in results]
    area_norms = [row["as_on_area_shadow_price"]["normalized_trace"] for row in results]

    payload = {
        "step": 3,
        "toy_name": "finite_asymptotic_safety_p3_xi_diagnostic",
        "orientation": "Mode A recognition-import diagnostic for the P3 route-mismatch",
        "carrier": {
            "audit_energy": "identity on the Step 1 finite carrier",
            "levels": levels,
            "native_lens": "asymptotic-safety-like UV fixed point route closure probe",
            "tested_sectors": [
                "p3_route_mismatch",
                "amplitude_geometry",
                "area_shadow_price",
            ],
        },
        "results": results,
        "refinement_stability": {
            "as_p3_normalized_level_2": p3_norms[0],
            "as_p3_normalized_level_4": p3_norms[1],
            "as_amplitude_normalized_level_2": amp_norms[0],
            "as_amplitude_normalized_level_4": amp_norms[1],
            "as_area_normalized_level_2": area_norms[0],
            "as_area_normalized_level_4": area_norms[1],
            "as_p3_absolute_delta": float(abs(p3_norms[1] - p3_norms[0])),
            "as_amplitude_absolute_delta": float(abs(amp_norms[1] - amp_norms[0])),
            "as_area_absolute_delta": float(abs(area_norms[1] - area_norms[0])),
            "interpretation": "AS-like lens closes P3 only; amplitude and area sectors remain residual",
        },
        "verdict_from_toy": "finite-carrier P3-only recognition diagnostic",
    }

    json_path = ARTIFACT_DIR / "simulation_output_step3.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    csv_path = ARTIFACT_DIR / "xi_diagnostic_step3.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "level_regions",
                "carrier_dimension",
                "native_lens",
                "sector",
                "raw_trace_xi",
                "trace_kdd",
                "normalized_trace_xi",
                "scope",
            ],
        )
        writer.writeheader()
        for row in results:
            for sector, key, scope in [
                ("p3_route_mismatch", "as_on_p3_route_mismatch", "P3 route-mismatch child sector"),
                ("amplitude_geometry", "as_on_amplitude_geometry", "Step 2 LQG amplitude sector retested under AS lens"),
                ("area_shadow_price", "as_on_area_shadow_price", "Step 1 HED area sector retested under AS lens"),
            ]:
                block = row[key]
                writer.writerow(
                    {
                        "level_regions": row["region_count"],
                        "carrier_dimension": row["carrier_dimension"],
                        "native_lens": "asymptotic_safety_like",
                        "sector": sector,
                        "raw_trace_xi": block["raw_trace"],
                        "trace_kdd": block["trace_K_DD"],
                        "normalized_trace_xi": block["normalized_trace"],
                        "scope": scope,
                    }
                )

    text_path = ARTIFACT_DIR / "simulation_output_step3.txt"
    lines = [
        "Step 3 finite-carrier Xi diagnostic",
        f"levels={levels}",
        f"as_p3_normalized_residuals={p3_norms}",
        f"as_amplitude_normalized_residuals={amp_norms}",
        f"as_area_normalized_residuals={area_norms}",
        "as_p3_sector_residuals=zero to numerical precision at both levels",
        "as_amplitude_sector_residuals=one at both levels",
        "as_area_sector_residuals=one at both levels",
    ]
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload["refinement_stability"], indent=2))


if __name__ == "__main__":
    main()
