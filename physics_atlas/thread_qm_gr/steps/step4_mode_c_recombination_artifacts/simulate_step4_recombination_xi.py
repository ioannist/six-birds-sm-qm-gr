#!/usr/bin/env python3
"""Step 4 finite-carrier compatibility diagnostic for Mode C recombination."""

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
    """Declare sector rows plus compatibility bridge rows."""
    if region_count < 2:
        raise ValueError("region_count must be at least 2")

    bridge_count = 4
    dim = region_count + 2 + bridge_count
    g_idx = region_count
    p3_idx = region_count + 1
    bridge_start = region_count + 2

    bridge_names = [
        "bridge_HED_LQG_area_geometry",
        "bridge_LQG_AS_discrete_continuum",
        "bridge_HED_AS_boundary_continuum",
        "bridge_triple_joint_package",
    ]

    basis = [f"entanglement_region_{i}" for i in range(region_count)]
    basis += ["bulk_geometry_amplitude", "p3_route_mismatch"]
    basis += bridge_names

    hed_rows = []
    hed_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0
        hed_rows.append(row)
        hed_names.append(f"HED_boundary_entanglement_S_{i}")

    g_row = np.zeros(dim)
    g_row[g_idx] = 1.0

    p3_row = np.zeros(dim)
    p3_row[p3_idx] = 1.0

    # Recombined recognized import profile: HED sector rows, LQG amplitude row,
    # and AS P3 row.  No compatibility bridge row is included here.
    recombined_native = np.vstack(hed_rows + [g_row, p3_row])
    recombined_names = hed_names + ["LQG_geometry_amplitude", "AS_p3_route_closure"]

    area_rows = []
    area_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0 / np.sqrt(region_count)
        area_rows.append(row)
        area_names.append(f"area_shadow_{i}")

    bridge_rows = []
    for j in range(bridge_count):
        row = np.zeros(dim)
        row[bridge_start + j] = 1.0
        bridge_rows.append(row)

    sector_target = np.vstack(area_rows + [g_row, p3_row])
    compatibility_target = np.vstack(bridge_rows)
    coupled_target = np.vstack(area_rows + [g_row, p3_row] + bridge_rows)

    # Rejected control: add the bridge rows directly to the native lens.  This
    # is not used for the verdict; it records the target-equivalent move.
    overread_native = np.vstack([recombined_native, compatibility_target])

    return {
        "basis": basis,
        "recombined_native": recombined_native,
        "recombined_names": recombined_names,
        "sector_target": sector_target,
        "compatibility_target": compatibility_target,
        "coupled_target": coupled_target,
        "bridge_names": bridge_names,
        "overread_native": overread_native,
    }


def summarize_level(region_count: int) -> dict:
    data = level_matrices(region_count)
    sector_only = adequacy_residual(data["recombined_native"], data["sector_target"])
    compatibility = adequacy_residual(data["recombined_native"], data["compatibility_target"])
    coupled = adequacy_residual(data["recombined_native"], data["coupled_target"])
    overread = adequacy_residual(data["overread_native"], data["coupled_target"])

    return {
        "region_count": region_count,
        "carrier_dimension": len(data["basis"]),
        "basis": data["basis"],
        "recombined_native_probe_names": data["recombined_names"],
        "compatibility_bridge_rows": data["bridge_names"],
        "sector_only_control_rejected": {
            "raw_trace": sector_only["raw_trace"],
            "normalized_trace": sector_only["normalized_trace"],
            "note": "recognized sector rows only; rejected as a recombination verdict",
        },
        "compatibility_constraints": {
            "raw_trace": compatibility["raw_trace"],
            "normalized_trace": compatibility["normalized_trace"],
            "trace_K_DD": compatibility["trace_K_DD"],
            "min_eigenvalue": float(np.min(compatibility["eigvals"])),
            "max_eigenvalue": float(np.max(compatibility["eigvals"])),
            "Xi_matrix": np.round(compatibility["Xi"], 10).tolist(),
        },
        "coupled_joint_with_constraints": {
            "raw_trace": coupled["raw_trace"],
            "normalized_trace": coupled["normalized_trace"],
            "trace_K_DD": coupled["trace_K_DD"],
            "min_eigenvalue": float(np.min(coupled["eigvals"])),
            "max_eigenvalue": float(np.max(coupled["eigvals"])),
            "Xi_matrix": np.round(coupled["Xi"], 10).tolist(),
        },
        "target_equivalent_overread_control": {
            "raw_trace": overread["raw_trace"],
            "normalized_trace": overread["normalized_trace"],
            "flag": "zero only after adding compatibility bridge rows to the native lens",
        },
        "no_overread_check": {
            "sector_only_control_used_as_verdict": False,
            "compatibility_bridge_rows_used_as_native_probes": False,
            "fixed_bulk_metric_inserted": False,
            "planck_constant_inserted": False,
            "constraint_rows_declared_before_xi": True,
        },
    }


def main() -> None:
    levels = [2, 4]
    results = [summarize_level(level) for level in levels]

    coupled_norms = [row["coupled_joint_with_constraints"]["normalized_trace"] for row in results]
    coupled_raw = [row["coupled_joint_with_constraints"]["raw_trace"] for row in results]
    compatibility_norms = [row["compatibility_constraints"]["normalized_trace"] for row in results]

    payload = {
        "step": 4,
        "toy_name": "finite_mode_c_compatibility_recombination_xi_diagnostic",
        "orientation": "Mode C compatibility audit, not sector-span audit",
        "carrier": {
            "audit_energy": "identity on extended finite carrier",
            "levels": levels,
            "recognized_import_rows": "HED entanglement rows + LQG amplitude row + AS P3 row",
            "compatibility_rows": [
                "HED_LQG area/geometry bridge",
                "LQG_AS discrete/continuum bridge",
                "HED_AS boundary/continuum bridge",
                "triple joint package bridge",
            ],
        },
        "results": results,
        "refinement_stability": {
            "coupled_normalized_level_2": coupled_norms[0],
            "coupled_normalized_level_4": coupled_norms[1],
            "coupled_raw_level_2": coupled_raw[0],
            "coupled_raw_level_4": coupled_raw[1],
            "compatibility_normalized_level_2": compatibility_norms[0],
            "compatibility_normalized_level_4": compatibility_norms[1],
            "coupled_absolute_delta": float(abs(coupled_norms[1] - coupled_norms[0])),
            "compatibility_absolute_delta": float(abs(compatibility_norms[1] - compatibility_norms[0])),
            "interpretation": "recognized sector rows close, but compatibility bridge rows remain as stable residual",
        },
        "verdict_from_toy": "bounded-grammar no-go for recombination without a new compatibility bridge",
    }

    json_path = ARTIFACT_DIR / "simulation_output_step4.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    csv_path = ARTIFACT_DIR / "xi_diagnostic_step4.csv"
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
                "scope",
            ],
        )
        writer.writeheader()
        for row in results:
            for sector, key, scope in [
                ("sector_only_rejected_control", "sector_only_control_rejected", "not a recombination verdict"),
                ("compatibility_constraints", "compatibility_constraints", "pairwise and triple bridge rows"),
                ("coupled_joint_with_constraints", "coupled_joint_with_constraints", "Mode C recombination target"),
                ("target_equivalent_overread_control", "target_equivalent_overread_control", "rejected bridge-row overread"),
            ]:
                block = row[key]
                writer.writerow(
                    {
                        "level_regions": row["region_count"],
                        "carrier_dimension": row["carrier_dimension"],
                        "sector": sector,
                        "raw_trace_xi": block["raw_trace"],
                        "trace_kdd": block.get("trace_K_DD", ""),
                        "normalized_trace_xi": block["normalized_trace"],
                        "scope": scope,
                    }
                )

    text_path = ARTIFACT_DIR / "simulation_output_step4.txt"
    lines = [
        "Step 4 finite-carrier compatibility recombination diagnostic",
        f"levels={levels}",
        f"coupled_joint_normalized_residuals={coupled_norms}",
        f"coupled_joint_raw_residuals={coupled_raw}",
        f"compatibility_only_normalized_residuals={compatibility_norms}",
        "recognized_sector_only_control=zero but rejected as verdict",
        "overread_control=zero only if compatibility bridge rows are added to native lens",
        "typed_result=stable compatibility residual remains",
    ]
    text_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload["refinement_stability"], indent=2))


if __name__ == "__main__":
    main()
