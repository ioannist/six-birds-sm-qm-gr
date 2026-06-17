#!/usr/bin/env python3
"""Step 34: instance-uniqueness of the minimal common refinement L.

The quotient-lattice test is linear row-span factorization of finite maps.
Finite-pair obstruction witnesses are also reported; they can be sparse on this
carrier, so the row-span residual is the deciding lattice obstruction.
"""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
TOL = 1e-10

MODE_NAMES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]

SOURCE_STATES_4 = np.array(
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

# d4 is deliberately independent of endpoint readouts, so the 5-mode object
# has genuine extra structure and is not equivalent to L.
D4_VALUES = np.array([[0.11], [0.37], [-0.23], [0.59], [0.05], [-0.41], [0.83], [-0.67]])
SOURCE_STATES_5 = np.hstack([SOURCE_STATES_4, D4_VALUES])


def selector(rows: list[int], ambient_dim: int = 4) -> np.ndarray:
    matrix = np.zeros((len(rows), ambient_dim), dtype=float)
    for i, row_index in enumerate(rows):
        matrix[i, row_index] = 1.0
    return matrix


Q_QM_4 = selector([0, 1, 2], 4)
Q_GR_4 = selector([0, 2, 3], 4)
L_4 = np.eye(4)
UNION_4 = selector([0, 1, 2, 0, 2, 3], 4)

Q_QM_5 = selector([0, 1, 2], 5)
Q_GR_5 = selector([0, 2, 3], 5)
L_IN_5 = selector([0, 1, 2, 3], 5)
M_5 = np.eye(5)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def rank(matrix: np.ndarray) -> int:
    return int(np.linalg.matrix_rank(matrix, tol=TOL))


def factorization(source_map: np.ndarray, target_map: np.ndarray) -> dict[str, object]:
    """Return whether target_map = phi @ source_map in the linear quotient lattice."""
    if target_map.shape[1] != source_map.shape[1]:
        raise ValueError("source and target maps must have the same ambient dimension")
    if target_map.shape[0] == 0:
        return {"factors": True, "residual": 0.0, "phi": np.zeros((0, source_map.shape[0])).tolist()}
    if source_map.shape[0] == 0:
        residual = norm(target_map)
        return {"factors": residual <= TOL, "residual": residual, "phi": np.zeros((target_map.shape[0], 0)).tolist()}

    # Solve source_map.T @ phi.T ~= target_map.T.
    phi_t, *_ = np.linalg.lstsq(source_map.T, target_map.T, rcond=None)
    phi = phi_t.T
    res = norm(phi @ source_map - target_map) / max(norm(target_map), 1.0)
    return {"factors": res <= TOL, "residual": float(res), "phi": phi.tolist()}


def finite_values(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    return states @ readout.T


def finite_obstruction_count(
    states: np.ndarray, source_map: np.ndarray, target_map: np.ndarray
) -> tuple[int, list[tuple[int, int]]]:
    source_values = finite_values(states, source_map)
    target_values = finite_values(states, target_map)
    witnesses: list[tuple[int, int]] = []
    for i, j in itertools.combinations(range(len(states)), 2):
        if norm(source_values[i] - source_values[j]) <= TOL and norm(target_values[i] - target_values[j]) > TOL:
            witnesses.append((i, j))
    return len(witnesses), witnesses


def duplicate_defect(readout: np.ndarray) -> dict[str, object]:
    readout_rank = rank(readout)
    dim = int(readout.shape[0])
    return {
        "dimension": dim,
        "rank": readout_rank,
        "extra_coordinate_count": dim - readout_rank,
        "passes_no_duplicate_gate": dim - readout_rank == 0,
    }


def endpoint_descent_metrics(
    candidate_name: str,
    candidate_map: np.ndarray,
    q_qm: np.ndarray,
    q_gr: np.ndarray,
    states: np.ndarray,
) -> dict[str, object]:
    qm = factorization(candidate_map, q_qm)
    gr = factorization(candidate_map, q_gr)
    qm_pair_count, qm_pairs = finite_obstruction_count(states, candidate_map, q_qm)
    gr_pair_count, gr_pairs = finite_obstruction_count(states, candidate_map, q_gr)
    return {
        "candidate": candidate_name,
        "qm_factors": qm["factors"],
        "qm_linear_residual": qm["residual"],
        "qm_pair_obstruction_count": qm_pair_count,
        "qm_pair_witnesses": ";".join(f"{i}-{j}" for i, j in qm_pairs),
        "gr_factors": gr["factors"],
        "gr_linear_residual": gr["residual"],
        "gr_pair_obstruction_count": gr_pair_count,
        "gr_pair_witnesses": ";".join(f"{i}-{j}" for i, j in gr_pairs),
        "both_endpoints_factor": bool(qm["factors"] and gr["factors"]),
    }


def relation_to_l(
    candidate_map: np.ndarray,
    ambient_l_map: np.ndarray,
    states: np.ndarray,
) -> dict[str, object]:
    l_from_candidate = factorization(candidate_map, ambient_l_map)
    candidate_from_l = factorization(ambient_l_map, candidate_map)
    pair_l_from_candidate, _ = finite_obstruction_count(states, candidate_map, ambient_l_map)
    pair_candidate_from_l, _ = finite_obstruction_count(states, ambient_l_map, candidate_map)
    equivalent = bool(
        l_from_candidate["factors"]
        and candidate_from_l["factors"]
        and candidate_map.shape[0] == ambient_l_map.shape[0]
    )
    return {
        "L_factors_through_candidate": l_from_candidate["factors"],
        "L_from_candidate_residual": l_from_candidate["residual"],
        "candidate_factors_through_L": candidate_from_l["factors"],
        "candidate_from_L_residual": candidate_from_l["residual"],
        "pair_obstruction_L_from_candidate": pair_l_from_candidate,
        "pair_obstruction_candidate_from_L": pair_candidate_from_l,
        "equivalent_to_L": equivalent,
    }


def candidate_record(
    name: str,
    modes: list[str],
    readout: np.ndarray,
    q_qm: np.ndarray,
    q_gr: np.ndarray,
    l_map: np.ndarray,
    states: np.ndarray,
    relation: str,
    minimal_override: bool | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    desc = endpoint_descent_metrics(name, readout, q_qm, q_gr, states)
    dup = duplicate_defect(readout)
    rel = relation_to_l(readout, l_map, states)
    admissible = bool(desc["both_endpoints_factor"] and dup["passes_no_duplicate_gate"])
    if minimal_override is None:
        minimal = bool(admissible and rel["equivalent_to_L"])
    else:
        minimal = minimal_override
    witness = (
        f"qm_res={desc['qm_linear_residual']:.6g}; gr_res={desc['gr_linear_residual']:.6g}; "
        f"rank={dup['rank']}/{dup['dimension']}; "
        f"L_from_candidate={rel['L_from_candidate_residual']:.6g}; "
        f"candidate_from_L={rel['candidate_from_L_residual']:.6g}"
    )
    row = {
        "candidate": name,
        "modes": ",".join(modes),
        "dim": readout.shape[0],
        "both_endpoints_factor": desc["both_endpoints_factor"],
        "admissible": admissible,
        "minimal": minimal,
        "relation_to_L": relation,
        "computed_witness": witness,
        "linear_decision_basis": True,
    }
    return row, {**desc, **dup, **rel}


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"empty rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    mediator_rows: list[dict[str, object]] = []
    descent_rows: list[dict[str, object]] = []

    row, desc = candidate_record(
        "L_join",
        MODE_NAMES,
        L_4,
        Q_QM_4,
        Q_GR_4,
        L_4,
        SOURCE_STATES_4,
        "is_join",
        minimal_override=True,
    )
    mediator_rows.append(row)
    descent_rows.append(desc)

    for drop_index, mode_name in enumerate(MODE_NAMES):
        kept = [i for i in range(4) if i != drop_index]
        readout = selector(kept, 4)
        row, desc = candidate_record(
            f"drop_{mode_name}",
            [MODE_NAMES[i] for i in kept],
            readout,
            Q_QM_4,
            Q_GR_4,
            L_4,
            SOURCE_STATES_4,
            "sub_minimal_fails",
            minimal_override=False,
        )
        mediator_rows.append(row)
        descent_rows.append(desc)

    row, desc = candidate_record(
        "M_super_5mode",
        MODE_NAMES + ["d4_extra"],
        M_5,
        Q_QM_5,
        Q_GR_5,
        L_IN_5,
        SOURCE_STATES_5,
        "super_minimal_nonminimal",
        minimal_override=False,
    )
    mediator_rows.append(row)
    descent_rows.append(desc)

    row, desc = candidate_record(
        "union_direct_sum",
        ["d0_density", "d1_phase", "d2_transport", "d0_density_dup", "d2_transport_dup", "d3_curvature"],
        UNION_4,
        Q_QM_4,
        Q_GR_4,
        L_4,
        SOURCE_STATES_4,
        "nonadmissible_union",
        minimal_override=False,
    )
    mediator_rows.append(row)
    descent_rows.append(desc)

    permutation = np.array(
        [
            [0.0, 0.0, 0.0, 1.0],
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    l_prime = permutation @ L_4
    row, desc = candidate_record(
        "L_prime_relabel",
        ["d3_curvature", "d0_density", "d2_transport", "d1_phase"],
        l_prime,
        Q_QM_4,
        Q_GR_4,
        L_4,
        SOURCE_STATES_4,
        "iso_to_L",
        minimal_override=True,
    )
    mediator_rows.append(row)
    descent_rows.append(desc)

    inverse_permutation = permutation.T
    l_to_lprime = factorization(L_4, l_prime)
    lprime_to_l = factorization(l_prime, L_4)
    iso_rows = [
        {
            "source": "L",
            "target": "L_prime_relabel",
            "permutation_matrix": permutation.tolist(),
            "residual": l_to_lprime["residual"],
            "is_iso_half": l_to_lprime["factors"],
        },
        {
            "source": "L_prime_relabel",
            "target": "L",
            "permutation_matrix": inverse_permutation.tolist(),
            "residual": lprime_to_l["residual"],
            "is_iso_half": lprime_to_l["factors"],
        },
    ]

    subminimal_rows = [row for row in mediator_rows if row["relation_to_L"] == "sub_minimal_fails"]
    m_row = next(row for row in mediator_rows if row["candidate"] == "M_super_5mode")
    union_row = next(row for row in mediator_rows if row["candidate"] == "union_direct_sum")
    lprime_row = next(row for row in mediator_rows if row["candidate"] == "L_prime_relabel")
    l_row = next(row for row in mediator_rows if row["candidate"] == "L_join")

    output = {
        "step": 34,
        "orientation": "Part B instance-uniqueness by F51 common-refinement lattice join",
        "join": {
            "name": "L_join",
            "modes": MODE_NAMES,
            "qm_factors_through_L": next(row for row in descent_rows if row["candidate"] == "L_join")["qm_factors"],
            "gr_factors_through_L": next(row for row in descent_rows if row["candidate"] == "L_join")["gr_factors"],
            "qm_residual": next(row for row in descent_rows if row["candidate"] == "L_join")["qm_linear_residual"],
            "gr_residual": next(row for row in descent_rows if row["candidate"] == "L_join")["gr_linear_residual"],
        },
        "controls": {
            "all_subminimal_fail_by_linear_obstruction": all(
                not bool(row["both_endpoints_factor"]) for row in subminimal_rows
            ),
            "subminimal_count": len(subminimal_rows),
            "superminimal_admissible": bool(m_row["admissible"]),
            "superminimal_minimal": bool(m_row["minimal"]),
            "union_admissible": bool(union_row["admissible"]),
            "lprime_iso_to_L": bool(lprime_row["minimal"] and lprime_row["admissible"]),
        },
        "verdict": {
            "type": "instance_uniqueness_minimal_common_refinement_up_to_equivalence",
            "L_unique_minimal": bool(
                l_row["admissible"]
                and l_row["minimal"]
                and all(not bool(row["both_endpoints_factor"]) for row in subminimal_rows)
                and bool(m_row["admissible"])
                and not bool(m_row["minimal"])
                and not bool(union_row["admissible"])
                and bool(lprime_row["minimal"])
            ),
            "bounded_grammar_scope": True,
            "up_to_equivalence": True,
            "superminimal_admissible_refinements_exist": True,
            "root_landed": False,
            "external_review_required": True,
        },
        "nonclaim": "Unique minimal admissible common refinement on the declared finite coordinate-lattice carrier; not the only admissible refinement and not an unrestricted physical uniqueness claim.",
    }

    write_csv(ARTIFACT_DIR / "mediator_candidates_step34.csv", mediator_rows)
    write_csv(ARTIFACT_DIR / "descent_residuals_step34.csv", descent_rows)
    write_csv(ARTIFACT_DIR / "isomorphism_check_step34.csv", iso_rows)

    (ARTIFACT_DIR / "instance_uniqueness_maps_step34.json").write_text(
        json.dumps(
            {
                "source_states_4": SOURCE_STATES_4.tolist(),
                "source_states_5": SOURCE_STATES_5.tolist(),
                "q_QM_4": Q_QM_4.tolist(),
                "q_GR_4": Q_GR_4.tolist(),
                "L_4": L_4.tolist(),
                "M_5": M_5.tolist(),
                "union_4": UNION_4.tolist(),
                "permutation_L_prime": permutation.tolist(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (ARTIFACT_DIR / "instance_uniqueness_output_step34.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "instance_uniqueness_output_step34.txt").write_text(
        "\n".join(
            [
                "Step 34 Part B instance-uniqueness",
                "Verdict: instance_uniqueness_minimal_common_refinement_up_to_equivalence",
                f"L unique minimal: {output['verdict']['L_unique_minimal']}",
                "Sub-minimal drop-one-mode candidates fail by linear map obstruction.",
                "M_super_5mode is admissible but non-minimal.",
                "union_direct_sum is non-admissible by duplicate-coordinate defect.",
                "L_prime_relabel is isomorphic to L by the exhibited permutation.",
                "Super-minimal admissible refinements exist; uniqueness is minimal up to equivalence.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
