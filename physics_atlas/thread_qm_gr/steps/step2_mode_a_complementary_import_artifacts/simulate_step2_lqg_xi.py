#!/usr/bin/env python3
"""Step 2 finite-carrier Xi diagnostic for the LQG complementary import audit."""

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
    """Reuse the Step 1 carrier and declare HED, LQG, and combined lenses."""
    if region_count < 2:
        raise ValueError("region_count must be at least 2")

    dim = region_count + 2
    g_idx = region_count
    p3_idx = region_count + 1
    basis = [f"entanglement_region_{i}" for i in range(region_count)]
    basis += ["bulk_geometry_amplitude", "p3_route_mismatch"]

    ent_rows = []
    ent_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0
        ent_rows.append(row)
        ent_names.append(f"boundary_entanglement_S_{i}")
    hed_native = np.vstack(ent_rows)

    g_row = np.zeros(dim)
    g_row[g_idx] = 1.0

    p3_route_row = np.zeros(dim)
    p3_route_row[g_idx] = 0.30
    p3_route_row[p3_idx] = 1.0

    # LQG-like native source atoms: a spin-network geometry-amplitude row and
    # a spin-foam/canonical-constraint route row.  They do not include the
    # boundary entanglement ledger used by the Step 1 holographic lens.
    lqg_native = np.vstack([g_row, p3_route_row])
    lqg_names = ["spin_network_geometry_amplitude", "spin_foam_route_protocol"]

    combined_native = np.vstack([hed_native, lqg_native])

    area_rows = []
    area_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0 / np.sqrt(region_count)
        area_rows.append(row)
        area_names.append(f"rt_area_shadow_{i}")
    d_area = np.vstack(area_rows)

    d_surviving = np.vstack([g_row, p3_route_row])
    d_surviving_names = ["amplitude_geometry_probe", "p3_route_mismatch_probe"]

    d_full = np.vstack([d_area, d_surviving])

    return {
        "basis": basis,
        "hed_native": hed_native,
        "hed_names": ent_names,
        "lqg_native": lqg_native,
        "lqg_names": lqg_names,
        "combined_native": combined_native,
        "d_area": d_area,
        "d_area_names": area_names,
        "d_surviving": d_surviving,
        "d_surviving_names": d_surviving_names,
        "d_full": d_full,
    }


def summarize_level(region_count: int) -> dict:
    data = level_matrices(region_count)
    lqg_surviving = adequacy_residual(data["lqg_native"], data["d_surviving"])
    lqg_area = adequacy_residual(data["lqg_native"], data["d_area"])
    lqg_full = adequacy_residual(data["lqg_native"], data["d_full"])
    hed_surviving = adequacy_residual(data["hed_native"], data["d_surviving"])
    combined_full = adequacy_residual(data["combined_native"], data["d_full"])

    return {
        "region_count": region_count,
        "carrier_dimension": len(data["basis"]),
        "basis": data["basis"],
        "lqg_native_probe_names_used": data["lqg_names"],
        "hed_native_probe_names_reference": data["hed_names"],
        "dissolving_surviving_probe_names": data["d_surviving_names"],
        "lqg_on_surviving_amplitude_p3": {
            "raw_trace": lqg_surviving["raw_trace"],
            "normalized_trace": lqg_surviving["normalized_trace"],
            "trace_K_DD": lqg_surviving["trace_K_DD"],
            "min_eigenvalue": float(np.min(lqg_surviving["eigvals"])),
            "max_eigenvalue": float(np.max(lqg_surviving["eigvals"])),
            "Xi_matrix": np.round(lqg_surviving["Xi"], 10).tolist(),
        },
        "lqg_on_area_shadow_price": {
            "raw_trace": lqg_area["raw_trace"],
            "normalized_trace": lqg_area["normalized_trace"],
            "trace_K_DD": lqg_area["trace_K_DD"],
            "min_eigenvalue": float(np.min(lqg_area["eigvals"])),
            "max_eigenvalue": float(np.max(lqg_area["eigvals"])),
            "Xi_matrix": np.round(lqg_area["Xi"], 10).tolist(),
        },
        "lqg_on_uncoupled_full_toy": {
            "raw_trace": lqg_full["raw_trace"],
            "normalized_trace": lqg_full["normalized_trace"],
            "trace_K_DD": lqg_full["trace_K_DD"],
        },
        "hed_reference_on_surviving_amplitude_p3": {
            "raw_trace": hed_surviving["raw_trace"],
            "normalized_trace": hed_surviving["normalized_trace"],
            "trace_K_DD": hed_surviving["trace_K_DD"],
        },
        "combined_lens_reference_on_uncoupled_full_toy": {
            "raw_trace": combined_full["raw_trace"],
            "normalized_trace": combined_full["normalized_trace"],
            "note": "Mode C setup reference only; not used as a root verdict in Step 2",
        },
        "no_overread_check": {
            "boundary_entanglement_used_in_lqg_native_lens": False,
            "fixed_bulk_metric_inserted": False,
            "planck_constant_inserted": False,
            "full_root_target_collapsed_by_single_lens": False,
            "combined_lens_only_recorded_as_mode_c_setup": True,
        },
    }


def main() -> None:
    levels = [2, 4]
    results = [summarize_level(level) for level in levels]

    lqg_surv_norms = [row["lqg_on_surviving_amplitude_p3"]["normalized_trace"] for row in results]
    lqg_area_norms = [row["lqg_on_area_shadow_price"]["normalized_trace"] for row in results]

    payload = {
        "step": 2,
        "toy_name": "finite_lqg_complementarity_xi_diagnostic",
        "orientation": "Mode A complementary recognition-import diagnostic",
        "carrier": {
            "audit_energy": "identity on the Step 1 finite carrier",
            "levels": levels,
            "native_lens": "LQG-like spin-network geometry amplitude plus spin-foam route protocol",
            "area_shadow_price_test": "RT-like area rows from boundary entanglement ledger",
        },
        "results": results,
        "refinement_stability": {
            "lqg_surviving_normalized_level_2": lqg_surv_norms[0],
            "lqg_surviving_normalized_level_4": lqg_surv_norms[1],
            "lqg_area_normalized_level_2": lqg_area_norms[0],
            "lqg_area_normalized_level_4": lqg_area_norms[1],
            "lqg_surviving_absolute_delta": float(abs(lqg_surv_norms[1] - lqg_surv_norms[0])),
            "lqg_area_absolute_delta": float(abs(lqg_area_norms[1] - lqg_area_norms[0])),
            "interpretation": "LQG-like lens closes surviving amplitude/P3 sector but leaves area-shadow-price sector open",
        },
        "verdict_from_toy": "finite-carrier complementarity diagnostic: LQG and holography close opposite uncoupled sectors",
    }

    json_path = ARTIFACT_DIR / "simulation_output_step2.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    csv_path = ARTIFACT_DIR / "xi_diagnostic_step2.csv"
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
            writer.writerow(
                {
                    "level_regions": row["region_count"],
                    "carrier_dimension": row["carrier_dimension"],
                    "native_lens": "lqg_like",
                    "sector": "surviving_amplitude_p3",
                    "raw_trace_xi": row["lqg_on_surviving_amplitude_p3"]["raw_trace"],
                    "trace_kdd": row["lqg_on_surviving_amplitude_p3"]["trace_K_DD"],
                    "normalized_trace_xi": row["lqg_on_surviving_amplitude_p3"]["normalized_trace"],
                    "scope": "R_child_E018_after_HED_full_joint_P3",
                }
            )
            writer.writerow(
                {
                    "level_regions": row["region_count"],
                    "carrier_dimension": row["carrier_dimension"],
                    "native_lens": "lqg_like",
                    "sector": "area_shadow_price",
                    "raw_trace_xi": row["lqg_on_area_shadow_price"]["raw_trace"],
                    "trace_kdd": row["lqg_on_area_shadow_price"]["trace_K_DD"],
                    "normalized_trace_xi": row["lqg_on_area_shadow_price"]["normalized_trace"],
                    "scope": "Step 1 holographic sector retested under LQG lens",
                }
            )

    text_path = ARTIFACT_DIR / "simulation_output_step2.txt"
    lines = [
        "Step 2 finite-carrier Xi diagnostic",
        f"levels={levels}",
        f"lqg_surviving_normalized_residuals={lqg_surv_norms}",
        f"lqg_area_normalized_residuals={lqg_area_norms}",
        "lqg_surviving_sector_residuals=zero to numerical precision at both levels",
        "lqg_area_sector_residuals=one at both levels",
        "combined_lens_reference=zero only as Mode C setup reference, not a Step 2 root verdict",
    ]
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload["refinement_stability"], indent=2))


if __name__ == "__main__":
    main()
