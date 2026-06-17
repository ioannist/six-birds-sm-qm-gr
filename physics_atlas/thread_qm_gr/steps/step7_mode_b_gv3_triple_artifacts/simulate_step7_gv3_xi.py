#!/usr/bin/env python3
"""Step 7 finite-carrier diagnostic for bounded G_v3 triple-audit search."""

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


def block_summary(native: np.ndarray, dissolving: np.ndarray) -> dict:
    block = adequacy_residual(native, dissolving)
    return {
        "raw_trace": block["raw_trace"],
        "normalized_trace": block["normalized_trace"],
        "trace_K_DD": block["trace_K_DD"],
        "min_eigenvalue": float(np.min(block["eigvals"])),
        "max_eigenvalue": float(np.max(block["eigvals"])),
        "Xi_matrix": np.round(block["Xi"], 10).tolist(),
    }


def level_matrices(region_count: int) -> dict:
    """Declare inherited pairwise rows, triple residual, and a witness control."""
    if region_count < 2:
        raise ValueError("region_count must be at least 2")

    # Basis:
    # u_i, v, w are the filtered inherited G_v1+G_v2 source rows.
    # t is the triple-package target row.
    # s is an independent witness coordinate used only to test whether an
    # independent atom without a bridge map can close the triple row.  It cannot.
    dim = region_count + 4
    v_idx = region_count
    w_idx = region_count + 1
    t_idx = region_count + 2
    s_idx = region_count + 3

    basis = [f"inherited_shared_area_geometry_currency_{i}" for i in range(region_count)]
    basis += [
        "inherited_route_holonomy_rg_source",
        "inherited_holographic_rg_boundary_continuum_flow",
        "residual_triple_joint_package",
        "independent_witness_without_bridge_map",
    ]

    inherited_rows = []
    inherited_names = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0
        inherited_rows.append(row)
        inherited_names.append(f"inherited_shared_currency_{i}")

    v_row = np.zeros(dim)
    v_row[v_idx] = 1.0
    inherited_rows.append(v_row)
    inherited_names.append("inherited_route_holonomy_rg")

    w_row = np.zeros(dim)
    w_row[w_idx] = 1.0
    inherited_rows.append(w_row)
    inherited_names.append("inherited_holographic_rg_flow")

    pairwise_native = np.vstack(inherited_rows)

    u_avg = np.zeros(dim)
    u_avg[:region_count] = 1.0 / np.sqrt(region_count)

    # Pairwise-union candidate: a dependent row in the existing u/v/w span.
    # It has no independent content, so it cannot generate t.
    q_union = u_avg + v_row + w_row
    q_union = q_union / np.linalg.norm(q_union)
    pairwise_union_native = np.vstack([pairwise_native, q_union])

    # Independent witness control: adding an independent row s still does not
    # generate the triple row without an audited bridge map s -> t.
    s_row = np.zeros(dim)
    s_row[s_idx] = 1.0
    witness_native = np.vstack([pairwise_native, s_row])

    triple_row = np.zeros(dim)
    triple_row[t_idx] = 1.0
    d_triple = np.vstack([triple_row])

    # Rejected control: adding t itself as native makes the residual vanish.
    native_triple_insertion = np.vstack([pairwise_native, triple_row])

    area_rows = []
    for i in range(region_count):
        row = np.zeros(dim)
        row[i] = 1.0 / np.sqrt(region_count)
        area_rows.append(row)
    d_area = np.vstack(area_rows)
    d_amplitude = np.vstack([u_avg])
    d_p3 = np.vstack([v_row])
    bridge_hl = np.vstack([u_avg])
    bridge_la = np.vstack([v_row])
    bridge_ha = np.vstack([w_row])
    d_all_bridges = np.vstack([bridge_hl, bridge_la, bridge_ha, d_triple])
    d_coupled = np.vstack([d_area, d_amplitude, d_p3, d_all_bridges])

    return {
        "basis": basis,
        "pairwise_native": pairwise_native,
        "pairwise_native_names": inherited_names,
        "pairwise_union_native": pairwise_union_native,
        "witness_native": witness_native,
        "native_triple_insertion": native_triple_insertion,
        "d_triple": d_triple,
        "d_coupled": d_coupled,
        "d_all_bridges": d_all_bridges,
        "bridge_HED_LQG": bridge_hl,
        "bridge_LQG_AS": bridge_la,
        "bridge_HED_AS": bridge_ha,
        "candidate_tests": {
            "pairwise_union_as_triple": "dependent row in span(u_i, v, w); no independent content",
            "independent_witness_without_bridge_map": "independent s row with no audited map to t",
            "native_triple_insertion": "t inserted directly; rejected control",
        },
    }


def summarize_level(region_count: int) -> dict:
    data = level_matrices(region_count)

    pairwise_triple = block_summary(data["pairwise_native"], data["d_triple"])
    pairwise_coupled = block_summary(data["pairwise_native"], data["d_coupled"])
    union_triple = block_summary(data["pairwise_union_native"], data["d_triple"])
    union_coupled = block_summary(data["pairwise_union_native"], data["d_coupled"])
    witness_triple = block_summary(data["witness_native"], data["d_triple"])
    witness_coupled = block_summary(data["witness_native"], data["d_coupled"])
    insertion_triple = block_summary(data["native_triple_insertion"], data["d_triple"])
    insertion_coupled = block_summary(data["native_triple_insertion"], data["d_coupled"])

    bridge_blocks = {
        "Bridge_HED_LQG_area_geometry": block_summary(data["pairwise_native"], data["bridge_HED_LQG"]),
        "Bridge_LQG_AS_discrete_continuum": block_summary(data["pairwise_native"], data["bridge_LQG_AS"]),
        "Bridge_HED_AS_boundary_continuum": block_summary(data["pairwise_native"], data["bridge_HED_AS"]),
        "Bridge_triple_joint_package": pairwise_triple,
    }

    return {
        "region_count": region_count,
        "carrier_dimension": len(data["basis"]),
        "basis": data["basis"],
        "inherited_native_probe_names": data["pairwise_native_names"],
        "candidate_tests": data["candidate_tests"],
        "bridge_results": bridge_blocks,
        "accepted_G_v3_search_result": {
            "candidate_type": "no_admissible_independent_triple_atom",
            "triple_bridge": pairwise_triple,
            "coupled_joint": pairwise_coupled,
        },
        "rejected_controls": {
            "pairwise_union_as_triple_completion": {
                "triple_bridge": union_triple,
                "coupled_joint": union_coupled,
                "flag": "no new span; not a triple package",
            },
            "independent_witness_without_bridge_map": {
                "triple_bridge": witness_triple,
                "coupled_joint": witness_coupled,
                "flag": "independent content without a map to t does not generate the bridge",
            },
            "native_triple_row_insertion": {
                "triple_bridge": insertion_triple,
                "coupled_joint": insertion_coupled,
                "flag": "zero residual only after inserting t itself",
            },
        },
        "no_overread_check": {
            "pairwise_union_treated_as_triple_package": False,
            "triple_row_inserted_as_native_probe": False,
            "primitive_package_coherence_used": False,
            "independent_witness_declared": False,
            "triple_has_generation_map": False,
            "fixed_bulk_metric_inserted": False,
            "planck_constant_inserted": False,
        },
    }


def main() -> None:
    levels = [2, 4]
    results = [summarize_level(level) for level in levels]

    triple_norms = [
        row["accepted_G_v3_search_result"]["triple_bridge"]["normalized_trace"]
        for row in results
    ]
    coupled_norms = [
        row["accepted_G_v3_search_result"]["coupled_joint"]["normalized_trace"]
        for row in results
    ]
    coupled_raw = [
        row["accepted_G_v3_search_result"]["coupled_joint"]["raw_trace"]
        for row in results
    ]

    payload = {
        "step": 7,
        "toy_name": "finite_gv3_triple_audit_saturation_xi_diagnostic",
        "orientation": "Mode B bounded no-go diagnostic for G_v3",
        "bounded_grammar": "G_E018_TriplePackageAudit_v3",
        "gv3_search": {
            "inherited_native_rows": "filtered u_i, v, w rows from G_v1+G_v2",
            "admissible_new_atom_requirement": "independent witness predicate plus generated shadow to the triple row",
            "result": "no admissible independent triple atom declared inside posited-atom-shadow grammar",
        },
        "results": results,
        "refinement_stability": {
            "triple_normalized_level_2": triple_norms[0],
            "triple_normalized_level_4": triple_norms[1],
            "coupled_normalized_level_2": coupled_norms[0],
            "coupled_normalized_level_4": coupled_norms[1],
            "coupled_raw_level_2": coupled_raw[0],
            "coupled_raw_level_4": coupled_raw[1],
            "triple_absolute_delta": float(abs(triple_norms[1] - triple_norms[0])),
            "coupled_absolute_delta": float(abs(coupled_norms[1] - coupled_norms[0])),
            "interpretation": (
                "Pairwise union leaves the triple bridge residual; direct triple "
                "insertion is rejected; no independent witness-generated atom is "
                "available in G_v3."
            ),
        },
        "verdict_from_toy": "bounded-grammar saturation no-go on G_v3",
    }

    json_path = ARTIFACT_DIR / "simulation_output_step7.json"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    csv_path = ARTIFACT_DIR / "xi_diagnostic_step7.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "level_regions",
                "carrier_dimension",
                "test",
                "target",
                "raw_trace_xi",
                "trace_kdd",
                "normalized_trace_xi",
                "status",
            ],
        )
        writer.writeheader()
        for row in results:
            accepted = row["accepted_G_v3_search_result"]
            writer.writerow(
                {
                    "level_regions": row["region_count"],
                    "carrier_dimension": row["carrier_dimension"],
                    "test": "accepted_G_v3_search",
                    "target": "Bridge_triple_joint_package",
                    "raw_trace_xi": accepted["triple_bridge"]["raw_trace"],
                    "trace_kdd": accepted["triple_bridge"]["trace_K_DD"],
                    "normalized_trace_xi": accepted["triple_bridge"]["normalized_trace"],
                    "status": "survives_G_v3",
                }
            )
            writer.writerow(
                {
                    "level_regions": row["region_count"],
                    "carrier_dimension": row["carrier_dimension"],
                    "test": "accepted_G_v3_search",
                    "target": "coupled_joint",
                    "raw_trace_xi": accepted["coupled_joint"]["raw_trace"],
                    "trace_kdd": accepted["coupled_joint"]["trace_K_DD"],
                    "normalized_trace_xi": accepted["coupled_joint"]["normalized_trace"],
                    "status": "bounded_no_go_residual",
                }
            )
            for test_name, test_data in row["rejected_controls"].items():
                for target_name in ["triple_bridge", "coupled_joint"]:
                    block = test_data[target_name]
                    writer.writerow(
                        {
                            "level_regions": row["region_count"],
                            "carrier_dimension": row["carrier_dimension"],
                            "test": test_name,
                            "target": target_name,
                            "raw_trace_xi": block["raw_trace"],
                            "trace_kdd": block["trace_K_DD"],
                            "normalized_trace_xi": block["normalized_trace"],
                            "status": "rejected_control",
                        }
                    )

    txt_lines = [
        "Step 7 finite G_v3 Xi diagnostic",
        "Inherited native lens: u_i, v, w.",
        "Accepted G_v3 search result: no admissible independent triple atom.",
    ]
    for result in results:
        accepted = result["accepted_G_v3_search_result"]
        txt_lines.append(
            "r={r}: triple normalized Xi={tnorm}; coupled raw Xi={raw}; coupled normalized Xi={cnorm}".format(
                r=result["region_count"],
                tnorm=accepted["triple_bridge"]["normalized_trace"],
                raw=accepted["coupled_joint"]["raw_trace"],
                cnorm=accepted["coupled_joint"]["normalized_trace"],
            )
        )
    txt_lines.append("Rejected control 1: native triple row insertion gives zero residual but is not generation.")
    txt_lines.append("Rejected control 2: pairwise u/v/w union leaves the triple residual and cannot be read as a triple package.")
    (ARTIFACT_DIR / "simulation_output_step7.txt").write_text(
        "\n".join(txt_lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
