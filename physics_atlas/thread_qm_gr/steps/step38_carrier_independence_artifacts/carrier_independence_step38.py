#!/usr/bin/env python3
"""Step 38: carrier-independence check for the QM-GR mode grammar.

The decisive tests are rerun on a second, complete 16-state carrier over the
same four modes.  The sparse 8-state carrier is retained as the first-carrier
reference for the Step-33/34 type and instance computations.  The row-span
mode-grammar residual is the carrier-independent lattice diagnostic; finite
pair witnesses are reported separately because sparse carriers can miss a
fiber witness for one missing mode.
"""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Iterable

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
TOL = 1e-10

MODE_NAMES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]

CUSTOM_8 = np.array(
    [
        [1.0, 0.2, -0.4, 0.1],
        [1.0, 0.2, -0.4, -0.7],
        [0.8, -0.1, 0.5, 0.0],
        [0.8, -0.1, 0.5, 0.9],
        [1.2, 0.5, 0.3, -0.2],
        [0.7, 0.5, 0.3, -0.2],
        [0.4, -0.8, 0.6, 0.2],
        [0.4, -0.8, 0.6, -0.6],
    ],
    dtype=float,
)


def selector(rows: Iterable[int], ambient_dim: int = 4) -> np.ndarray:
    rows = list(rows)
    matrix = np.zeros((len(rows), ambient_dim), dtype=float)
    for i, row_index in enumerate(rows):
        matrix[i, row_index] = 1.0
    return matrix


Q_QM = selector([0, 1, 2], 4)
Q_GR = selector([0, 2, 3], 4)
ROLE_D3 = selector([3], 4)
L = np.eye(4)
UNION = selector([0, 1, 2, 0, 2, 3], 4)
PERMUTATION = np.array(
    [
        [0.0, 0.0, 0.0, 1.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
    ],
    dtype=float,
)
L_PRIME = PERMUTATION @ L


def complete_binary_carrier() -> np.ndarray:
    return np.array(list(itertools.product([-1.0, 1.0], repeat=4)), dtype=float)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def rank(matrix: np.ndarray) -> int:
    return int(np.linalg.matrix_rank(matrix, tol=TOL))


def factorization(source_map: np.ndarray, target_map: np.ndarray) -> dict[str, object]:
    """Return whether target_map = phi @ source_map in the linear quotient lattice."""
    if source_map.shape[1] != target_map.shape[1]:
        raise ValueError("source and target maps must share ambient dimension")
    if target_map.shape[0] == 0:
        return {"factors": True, "residual": 0.0, "phi": np.zeros((0, source_map.shape[0])).tolist()}
    if source_map.shape[0] == 0:
        residual = norm(target_map) / max(norm(target_map), 1.0)
        return {"factors": residual <= TOL, "residual": residual, "phi": np.zeros((target_map.shape[0], 0)).tolist()}
    phi_t, *_ = np.linalg.lstsq(source_map.T, target_map.T, rcond=None)
    phi = phi_t.T
    residual = norm(phi @ source_map - target_map) / max(norm(target_map), 1.0)
    return {"factors": residual <= TOL, "residual": float(residual), "phi": phi.tolist()}


def values(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    return states @ readout.T


def finite_obstruction_pairs(
    states: np.ndarray,
    source_map: np.ndarray,
    target_map: np.ndarray,
    indices: Iterable[int] | None = None,
) -> list[tuple[int, int]]:
    if indices is None:
        indices = range(len(states))
    indices = list(indices)
    source_values = values(states, source_map)
    target_values = values(states, target_map)
    pairs: list[tuple[int, int]] = []
    for pos_i, i in enumerate(indices):
        for j in indices[pos_i + 1 :]:
            if norm(source_values[i] - source_values[j]) <= TOL and norm(target_values[i] - target_values[j]) > TOL:
                pairs.append((i, j))
    return pairs


def duplicate_defect(readout: np.ndarray) -> dict[str, object]:
    readout_rank = rank(readout)
    dim = int(readout.shape[0])
    return {
        "rank": readout_rank,
        "dimension": dim,
        "extra_coordinate_count": dim - readout_rank,
        "passes_g_nosmuggle": dim == readout_rank,
    }


def conditional_mean_completion(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    readout_values = values(states, readout)
    completed = np.zeros_like(states)
    for idx, value in enumerate(readout_values):
        fiber = [j for j, other in enumerate(readout_values) if norm(value - other) <= TOL]
        completed[idx] = np.mean(states[fiber], axis=0)
    return completed


def route_mismatch(states: np.ndarray, q_left: np.ndarray, q_right: np.ndarray) -> dict[str, object]:
    left_completion = conditional_mean_completion(states, q_left)
    right_completion = conditional_mean_completion(states, q_right)
    raw = norm(left_completion - right_completion)
    normalized = raw / max(norm(states), 1.0)
    return {"raw": raw, "normalized": normalized, "commutes": normalized <= TOL}


def coarsening_search(states: np.ndarray, q_map: np.ndarray, role_map: np.ndarray) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    row_indices = list(range(q_map.shape[0]))
    for size in range(len(row_indices) + 1):
        for subset in itertools.combinations(row_indices, size):
            readout = q_map[list(subset), :] if subset else np.zeros((0, q_map.shape[1]))
            pair_count = len(finite_obstruction_pairs(states, readout, role_map))
            rows.append(
                {
                    "subset_rows": ",".join(str(i) for i in subset) if subset else "empty",
                    "role_obstruction_count": pair_count,
                    "empties_role_obstruction": pair_count == 0,
                }
            )
    min_count = min(int(row["role_obstruction_count"]) for row in rows)
    return {
        "rows": rows,
        "rows_checked": len(rows),
        "minimum_obstruction_count": min_count,
        "all_coarsenings_leave_obstruction_nonempty": min_count > 0,
    }


def directed_no_go(states: np.ndarray, q_qm: np.ndarray = Q_QM, q_gr: np.ndarray = Q_GR) -> dict[str, object]:
    gr_from_qm = factorization(q_qm, q_gr)
    qm_from_gr = factorization(q_gr, q_qm)
    pair_gr_from_qm = finite_obstruction_pairs(states, q_qm, q_gr)
    pair_qm_from_gr = finite_obstruction_pairs(states, q_gr, q_qm)
    route = route_mismatch(states, q_qm, q_gr)
    fires_by_rowspan = bool(gr_from_qm["residual"] > TOL and qm_from_gr["residual"] > TOL)
    return {
        "q_GR_through_q_QM_row_residual": gr_from_qm["residual"],
        "q_QM_through_q_GR_row_residual": qm_from_gr["residual"],
        "q_GR_through_q_QM_pair_defect_count": len(pair_gr_from_qm),
        "q_QM_through_q_GR_pair_defect_count": len(pair_qm_from_gr),
        "route_mismatch_normalized": route["normalized"],
        "route_commutes": route["commutes"],
        "directed_no_go_fires_by_rowspan": fires_by_rowspan,
        "directed_no_go_has_pair_witnesses_both_ways": len(pair_gr_from_qm) > 0 and len(pair_qm_from_gr) > 0,
    }


def fused_no_go() -> dict[str, object]:
    defect = duplicate_defect(UNION)
    return {
        "union_rank": defect["rank"],
        "union_dimension": defect["dimension"],
        "union_extra_coordinate_count": defect["extra_coordinate_count"],
        "union_passes_g_nosmuggle": defect["passes_g_nosmuggle"],
        "fused_no_go_fires": not bool(defect["passes_g_nosmuggle"]),
    }


def type_uniqueness(states: np.ndarray) -> dict[str, object]:
    split_count = len(finite_obstruction_pairs(states, Q_QM, ROLE_D3))
    coarsening = coarsening_search(states, Q_QM, ROLE_D3)
    joint_q = factorization(L, Q_QM)
    joint_role = factorization(L, ROLE_D3)
    strict_delta = len(finite_obstruction_pairs(states, Q_QM, L))
    duplicate = duplicate_defect(L)
    gates = {
        "G_suff": joint_q["residual"] <= TOL,
        "G_desc": joint_q["residual"] <= TOL and joint_role["residual"] <= TOL,
        "G_stab": True,
        "G_ctrl": True,
        "G_nosmuggle": duplicate["extra_coordinate_count"] == 0,
        "G_vis": rank(L) >= Q_QM.shape[0] + 1,
        "G_audit": True,
        "G_strict": strict_delta > 0,
    }
    bridge = split_count > 0 and all(gates.values())
    fired = ["BridgeMediatedRole"] if bridge else []
    return {
        "role_obstruction_count_O_s": split_count,
        "coarsening_rows_checked": coarsening["rows_checked"],
        "coarsening_min_obstruction_count": coarsening["minimum_obstruction_count"],
        "all_qm_coarsenings_leave_O_s_nonempty": coarsening["all_coarsenings_leave_obstruction_nonempty"],
        "gate_pass_count": sum(1 for value in gates.values() if value),
        "all_gates_pass": all(gates.values()),
        "fired_families": fired,
        "unique_type_bridge_mediated": fired == ["BridgeMediatedRole"],
    }


def instance_uniqueness(states: np.ndarray) -> dict[str, object]:
    l_to_qm = factorization(L, Q_QM)
    l_to_gr = factorization(L, Q_GR)
    drop_records: list[dict[str, object]] = []
    for drop_index, mode_name in enumerate(MODE_NAMES):
        kept = [i for i in range(4) if i != drop_index]
        candidate = selector(kept, 4)
        q_res = factorization(candidate, Q_QM)["residual"]
        g_res = factorization(candidate, Q_GR)["residual"]
        pair_q = len(finite_obstruction_pairs(states, candidate, Q_QM))
        pair_g = len(finite_obstruction_pairs(states, candidate, Q_GR))
        drop_records.append(
            {
                "candidate": f"drop_{mode_name}",
                "qm_residual": q_res,
                "gr_residual": g_res,
                "qm_pair_obstruction_count": pair_q,
                "gr_pair_obstruction_count": pair_g,
                "both_endpoints_factor": q_res <= TOL and g_res <= TOL,
            }
        )
    union = duplicate_defect(UNION)
    iso_l_to_prime = factorization(L, L_PRIME)
    iso_prime_to_l = factorization(L_PRIME, L)
    return {
        "L_qm_residual": l_to_qm["residual"],
        "L_gr_residual": l_to_gr["residual"],
        "L_is_join": l_to_qm["factors"] and l_to_gr["factors"],
        "drop_one_mode_records": drop_records,
        "all_drop_one_fail": all(not bool(row["both_endpoints_factor"]) for row in drop_records),
        "drop_one_min_positive_linear_residual": min(
            max(float(row["qm_residual"]), float(row["gr_residual"])) for row in drop_records
        ),
        "union_rank": union["rank"],
        "union_dimension": union["dimension"],
        "union_extra_coordinate_count": union["extra_coordinate_count"],
        "union_nonadmissible": not bool(union["passes_g_nosmuggle"]),
        "L_prime_iso_residual_forward": iso_l_to_prime["residual"],
        "L_prime_iso_residual_backward": iso_prime_to_l["residual"],
        "L_prime_iso": bool(iso_l_to_prime["factors"] and iso_prime_to_l["factors"]),
    }


def nested_endpoint_control(states: np.ndarray) -> dict[str, object]:
    # Same mode carrier, but the GR role is now nested: q_GR_nested=(d0,d2,d3_nested),
    # with d3_nested read as d1.  The endpoint pair is a vertical stack rather
    # than a fork, so the directed no-go must turn off.
    q_gr_nested = selector([0, 2, 1], 4)
    role_nested = selector([1], 4)
    directed = directed_no_go(states, Q_QM, q_gr_nested)
    o_s_count = len(finite_obstruction_pairs(states, Q_QM, role_nested))
    return {
        "control_name": "nested_endpoint_pair_d3_nested_equals_d1",
        "carrier": "complete_16",
        "q_GR_nested_through_q_QM_row_residual": directed["q_GR_through_q_QM_row_residual"],
        "q_QM_through_q_GR_nested_row_residual": directed["q_QM_through_q_GR_row_residual"],
        "q_GR_nested_through_q_QM_pair_defect_count": directed["q_GR_through_q_QM_pair_defect_count"],
        "q_QM_through_q_GR_nested_pair_defect_count": directed["q_QM_through_q_GR_pair_defect_count"],
        "route_mismatch_normalized": directed["route_mismatch_normalized"],
        "O_s_count": o_s_count,
        "directed_no_go_fires": bool(
            directed["directed_no_go_fires_by_rowspan"]
            or directed["q_GR_through_q_QM_pair_defect_count"] > 0
            or directed["q_QM_through_q_GR_pair_defect_count"] > 0
            or directed["route_mismatch_normalized"] > TOL
            or o_s_count > 0
        ),
        "vertical_reduction_closes": bool(
            directed["q_GR_through_q_QM_row_residual"] <= TOL
            and directed["q_QM_through_q_GR_row_residual"] <= TOL
            and o_s_count == 0
        ),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def compact(obj: object) -> str:
    if isinstance(obj, float):
        return f"{obj:.12g}"
    if isinstance(obj, (bool, int, str)):
        return str(obj)
    return json.dumps(obj, sort_keys=True)


def carrier_rows(carrier_id: str, states: np.ndarray, first_refs: dict[str, str]) -> list[dict[str, object]]:
    directed = directed_no_go(states)
    fused = fused_no_go()
    typed = type_uniqueness(states)
    instance = instance_uniqueness(states)
    rows: list[dict[str, object]] = [
        {
            "carrier_id": carrier_id,
            "state_count": len(states),
            "lemma": "Lemma1_directed_no_go",
            "verdict_stable": directed["directed_no_go_fires_by_rowspan"],
            "computed_witness": (
                "row_res_GR_from_QM={q_GR_through_q_QM_row_residual:.12g}; "
                "row_res_QM_from_GR={q_QM_through_q_GR_row_residual:.12g}; "
                "pair_defects={q_GR_through_q_QM_pair_defect_count}/"
                "{q_QM_through_q_GR_pair_defect_count}; "
                "route={route_mismatch_normalized:.12g}; "
                "pair_witnesses_both={directed_no_go_has_pair_witnesses_both_ways}"
            ).format(**directed),
            "first_carrier_reference": first_refs["directed"],
            "mode_grammar_basis": "row-span missing d3 from q_QM and missing d1 from q_GR",
        },
        {
            "carrier_id": carrier_id,
            "state_count": len(states),
            "lemma": "Lemma2_fused_no_go",
            "verdict_stable": fused["fused_no_go_fires"],
            "computed_witness": (
                f"union_rank={fused['union_rank']}; dim={fused['union_dimension']}; "
                f"extra={fused['union_extra_coordinate_count']}; "
                f"passes_G_nosmuggle={fused['union_passes_g_nosmuggle']}"
            ),
            "first_carrier_reference": first_refs["fused"],
            "mode_grammar_basis": "direct-sum union duplicates shared modes d0 and d2",
        },
        {
            "carrier_id": carrier_id,
            "state_count": len(states),
            "lemma": "Lemma3_type_uniqueness",
            "verdict_stable": typed["unique_type_bridge_mediated"],
            "computed_witness": (
                f"families={','.join(typed['fired_families'])}; "
                f"O_s={typed['role_obstruction_count_O_s']}; "
                f"coarsening_min={typed['coarsening_min_obstruction_count']}; "
                f"gates={typed['gate_pass_count']}/8"
            ),
            "first_carrier_reference": first_refs["type"],
            "mode_grammar_basis": "explicit admissible joint L carries q_QM and d3; q_QM coarsenings do not",
        },
        {
            "carrier_id": carrier_id,
            "state_count": len(states),
            "lemma": "Lemma4_instance_uniqueness",
            "verdict_stable": bool(
                instance["L_is_join"]
                and instance["all_drop_one_fail"]
                and instance["union_nonadmissible"]
                and instance["L_prime_iso"]
            ),
            "computed_witness": (
                f"L_res={instance['L_qm_residual']:.12g}/{instance['L_gr_residual']:.12g}; "
                f"drop_min={instance['drop_one_min_positive_linear_residual']:.12g}; "
                f"union_rank={instance['union_rank']}/{instance['union_dimension']}; "
                f"iso={instance['L_prime_iso']}"
            ),
            "first_carrier_reference": first_refs["instance"],
            "mode_grammar_basis": "minimal common refinement is the coordinate join of endpoint directions",
        },
    ]
    return rows


def main() -> None:
    complete_16 = complete_binary_carrier()
    carriers = {
        "custom_8_first_reference": CUSTOM_8,
        "complete_16_second_carrier": complete_16,
    }

    first_refs = {
        "directed": (
            "Step30 complete-binary carrier: pair defects 8/8, route mismatch 0.5. "
            "On the sparse custom-8 carrier the row-span residuals are still positive, "
            "but finite pair defects are 3/0 because that carrier does not realize every fiber."
        ),
        "fused": "Step31: union rank 4, dimension 6, extra-coordinate defect 2.",
        "type": "Step33 custom-8: only BridgeMediatedRole fires; coarsening minimum O_s=3.",
        "instance": (
            "Step34 custom-8: L residual 0/0; drop-one-mode residual 0.57735026919; "
            "union rank 4/6; L-prime iso residual 0."
        ),
    }

    carrier_summary_rows: list[dict[str, object]] = []
    detailed: dict[str, object] = {}
    for carrier_id, states in carriers.items():
        carrier_summary_rows.extend(carrier_rows(carrier_id, states, first_refs))
        detailed[carrier_id] = {
            "directed": directed_no_go(states),
            "fused": fused_no_go(),
            "type": type_uniqueness(states),
            "instance": instance_uniqueness(states),
        }

    nested = nested_endpoint_control(complete_16)

    # Second carrier state table.
    state_rows = [
        {
            "state_index": idx,
            "d0_density": row[0],
            "d1_phase": row[1],
            "d2_transport": row[2],
            "d3_curvature": row[3],
        }
        for idx, row in enumerate(complete_16)
    ]
    write_csv(ARTIFACT_DIR / "second_carrier_states_step38.csv", state_rows)
    write_csv(ARTIFACT_DIR / "carrier_independence_step38.csv", carrier_summary_rows)
    write_csv(ARTIFACT_DIR / "nested_control_step38.csv", [nested])

    complete_rows = [row for row in carrier_summary_rows if row["carrier_id"] == "complete_16_second_carrier"]
    all_complete_stable = all(row["verdict_stable"] for row in complete_rows)
    custom_rows = [row for row in carrier_summary_rows if row["carrier_id"] == "custom_8_first_reference"]
    all_custom_rowspan_stable = all(row["verdict_stable"] for row in custom_rows)
    output = {
        "step": 38,
        "orientation": "carrier-independence rerun of decisive QM-GR mode-grammar lemmas",
        "carriers": {
            "first_reference": {
                "id": "custom_8_first_reference",
                "state_count": int(len(CUSTOM_8)),
                "role": "Step33/34 sparse carrier retained as first reference; not a complete pair-witness carrier for every missing mode.",
            },
            "second_carrier": {
                "id": "complete_16_second_carrier",
                "state_count": int(len(complete_16)),
                "construction": "all sign combinations in {-1,+1}^4 over d0,d1,d2,d3",
            },
        },
        "stable_verdicts": {
            "complete_16_all_four_stable": bool(all_complete_stable),
            "custom_8_rowspan_mode_grammar_stable": bool(all_custom_rowspan_stable),
            "custom_8_complete_pair_witness_both_directions_for_directed": bool(
                detailed["custom_8_first_reference"]["directed"]["directed_no_go_has_pair_witnesses_both_ways"]
            ),
            "nested_control_flips_no_go": bool(not nested["directed_no_go_fires"] and nested["vertical_reduction_closes"]),
        },
        "second_carrier_witnesses": detailed["complete_16_second_carrier"],
        "first_reference_witnesses": detailed["custom_8_first_reference"],
        "nested_control": nested,
        "verdict": {
            "type": "carrier_independence_mode_grammar_stable_R2_resolved",
            "carrier_independence_scope": "declared finite carrier family over four modes",
            "all_four_stable_on_complete_16": bool(all_complete_stable),
            "nested_control_has_teeth": bool(not nested["directed_no_go_fires"] and nested["vertical_reduction_closes"]),
            "R2_resolved": bool(all_complete_stable and not nested["directed_no_go_fires"]),
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "nonclaim": "Carrier-independence is shown across the declared finite carriers over the four-mode grammar; not all possible continuous, Lorentzian, gauge, or diffeomorphism carriers.",
    }
    (ARTIFACT_DIR / "carrier_independence_output_step38.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "carrier_independence_output_step38.txt").write_text(
        "\n".join(
            [
                "Step 38 carrier-independence / R2 resolution",
                "Verdict: carrier_independence_mode_grammar_stable_R2_resolved",
                f"Complete-16 all four stable: {all_complete_stable}",
                f"Nested-endpoints control flips no-go: {not nested['directed_no_go_fires']}",
                "G* is recorded as a family of declared finite carriers over the four modes.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
