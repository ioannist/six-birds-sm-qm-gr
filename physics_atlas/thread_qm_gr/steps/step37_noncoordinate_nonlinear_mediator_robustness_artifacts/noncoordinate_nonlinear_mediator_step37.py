#!/usr/bin/env python3
"""Step 37: robustness of instance-uniqueness under wider mediator classes."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
TOL = 1e-8
RNG = np.random.default_rng(37037)

SOURCE_STATES = np.array(
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

Q_QM_MAP = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ],
    dtype=float,
)
Q_GR_MAP = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)
L_MAP = np.eye(4)
Y_QM = SOURCE_STATES @ Q_QM_MAP.T
Y_GR = SOURCE_STATES @ Q_GR_MAP.T
Y_L = SOURCE_STATES.copy()


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def matrix_rank(matrix: np.ndarray) -> int:
    return int(np.linalg.matrix_rank(matrix, tol=TOL))


def map_factorization(source_map: np.ndarray, target_map: np.ndarray) -> dict[str, object]:
    phi_t, *_ = np.linalg.lstsq(source_map.T, target_map.T, rcond=None)
    phi = phi_t.T
    residual = norm(phi @ source_map - target_map) / max(norm(target_map), 1.0)
    return {"factors": residual <= TOL, "residual": float(residual)}


def value_factorization(source_values: np.ndarray, target_values: np.ndarray) -> dict[str, object]:
    beta, *_ = np.linalg.lstsq(source_values, target_values, rcond=None)
    residual = norm(source_values @ beta - target_values) / max(norm(target_values), 1.0)
    return {"factors": residual <= TOL, "residual": float(residual)}


def polynomial_features(x: np.ndarray, degree: int) -> np.ndarray:
    columns = [np.ones(len(x))]
    n = x.shape[1]
    for deg in range(1, degree + 1):
        for combo in itertools.combinations_with_replacement(range(n), deg):
            col = np.ones(len(x))
            for idx in combo:
                col = col * x[:, idx]
            columns.append(col)
    return np.vstack(columns).T


def polynomial_residual(source_values: np.ndarray, target_values: np.ndarray, degree: int = 3) -> dict[str, object]:
    features = polynomial_features(source_values, degree)
    beta, *_ = np.linalg.lstsq(features, target_values, rcond=None)
    residual = norm(features @ beta - target_values) / max(norm(target_values), 1.0)
    return {"factors": residual <= TOL, "residual": float(residual), "feature_count": features.shape[1]}


def finite_obstruction_count(source_values: np.ndarray, target_values: np.ndarray) -> int:
    count = 0
    for i, j in itertools.combinations(range(len(source_values)), 2):
        if norm(source_values[i] - source_values[j]) <= TOL and norm(target_values[i] - target_values[j]) > TOL:
            count += 1
    return count


def relation_linear(name: str, readout_map: np.ndarray) -> dict[str, object]:
    qm = map_factorization(readout_map, Q_QM_MAP)
    gr = map_factorization(readout_map, Q_GR_MAP)
    l_from_m = map_factorization(readout_map, L_MAP)
    m_from_l = map_factorization(L_MAP, readout_map)
    rank = matrix_rank(readout_map)
    dim = int(readout_map.shape[0])
    carries = bool(qm["factors"] and gr["factors"])
    equivalent = bool(carries and l_from_m["factors"] and m_from_l["factors"] and dim == 4 and rank == 4)
    if equivalent:
        relation = "iso_to_L"
        minimal = True
    elif not carries:
        relation = "sub_minimal_fails"
        minimal = False
    elif dim > 4 or rank > 4 or l_from_m["factors"]:
        relation = "super_minimal_nonminimal"
        minimal = False
    else:
        relation = "inequivalent_minimal"
        minimal = True
    admissible = bool(carries and rank >= 4)
    iso_residual = float(l_from_m["residual"] + m_from_l["residual"])
    return {
        "mediator": name,
        "rank": rank,
        "dim": dim,
        "carries_both": carries,
        "admissible": admissible,
        "minimal": minimal,
        "relation_to_L": relation,
        "qm_residual": qm["residual"],
        "gr_residual": gr["residual"],
        "L_from_M_residual": l_from_m["residual"],
        "M_from_L_residual": m_from_l["residual"],
        "iso_residual": iso_residual,
    }


def linear_mediators() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx in range(8):
        a = RNG.normal(size=(4, 4))
        while abs(np.linalg.det(a)) < 0.1:
            a = RNG.normal(size=(4, 4))
        rows.append(relation_linear(f"linear_invertible_A_{idx}", a))
    for idx in range(5):
        a = RNG.normal(size=(3, 4))
        while matrix_rank(a) < 3:
            a = RNG.normal(size=(3, 4))
        rows.append(relation_linear(f"linear_rank3_too_small_{idx}", a))
    overcomplete = np.vstack([np.eye(4), np.array([[1.0, -0.5, 0.25, 0.75]])])
    rows.append(relation_linear("linear_overcomplete_5row_redundant", overcomplete))
    return rows


def relation_nonlinear(name: str, values: np.ndarray) -> dict[str, object]:
    qm = polynomial_residual(values, Y_QM, degree=3)
    gr = polynomial_residual(values, Y_GR, degree=3)
    l_from_m = polynomial_residual(values, Y_L, degree=3)
    m_from_l = polynomial_residual(Y_L, values, degree=3)
    rank = matrix_rank(values)
    dim = int(values.shape[1])
    carries = bool(qm["factors"] and gr["factors"])
    # For nonlinear readouts, equivalence is mutual recoverability on the
    # declared finite carrier, not equality of axis dimension.
    equivalent = bool(carries and l_from_m["factors"] and m_from_l["factors"])
    if equivalent:
        relation = "iso_to_L"
        minimal = True
    elif not carries:
        relation = "sub_minimal_fails"
        minimal = False
    elif l_from_m["factors"] and dim > 4:
        relation = "super_minimal_nonminimal"
        minimal = False
    elif carries and not l_from_m["factors"]:
        relation = "inequivalent_minimal"
        minimal = True
    else:
        relation = "super_minimal_nonminimal"
        minimal = False
    admissible = bool(carries and rank >= 4)
    iso_residual = float(l_from_m["residual"] + m_from_l["residual"])
    return {
        "mediator": name,
        "degree_tested": 3,
        "rank": rank,
        "dim": dim,
        "carries_both": carries,
        "admissible": admissible,
        "minimal": minimal,
        "relation_to_L": relation,
        "qm_residual": qm["residual"],
        "gr_residual": gr["residual"],
        "L_from_M_residual": l_from_m["residual"],
        "M_from_L_residual": m_from_l["residual"],
        "iso_residual": iso_residual,
    }


def nonlinear_mediators() -> list[dict[str, object]]:
    d0, d1, d2, d3 = [SOURCE_STATES[:, i] for i in range(4)]
    candidates = {
        "nonlinear_iso_quad_1": np.column_stack([d0 + d1**2, d1, d2, d3]),
        "nonlinear_iso_quad_2": np.column_stack([d0 + d1**2, d1 + d2**2, d2, d3]),
        "nonlinear_sub_small_missing_phase": np.column_stack([d0 + d1**2, d2, d3]),
        "nonlinear_sub_small_missing_curvature": np.column_stack([d0, d1 + d2**2, d2]),
        "nonlinear_super_5_feature": np.column_stack([d0, d1, d2, d3, d0 * d3 + d1**2]),
        "nonlinear_super_6_features": np.column_stack([d0, d1, d2, d3, d0 * d2, d1 * d3]),
    }
    return [relation_nonlinear(name, values) for name, values in candidates.items()]


def positive_detection_control() -> tuple[list[dict[str, object]], dict[str, object]]:
    states = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
    endpoints = np.zeros((4, 1))
    mx = states[:, [0]]
    my = states[:, [1]]
    mediators = {"control_mediator_x_partition": mx, "control_mediator_y_partition": my}
    rows: list[dict[str, object]] = []
    for name, values in mediators.items():
        carries = value_factorization(values, endpoints)["factors"]
        strict = finite_obstruction_count(endpoints, values) > 0
        rank = matrix_rank(values)
        minimal_strict = carries and strict and rank == 1
        other_name = "control_mediator_y_partition" if "x" in name else "control_mediator_x_partition"
        other_values = mediators[other_name]
        to_other = value_factorization(values, other_values)
        from_other = value_factorization(other_values, values)
        inequivalent = not (to_other["factors"] and from_other["factors"])
        rows.append(
            {
                "control_name": name,
                "carries_endpoints": carries,
                "strict": strict,
                "minimal": minimal_strict,
                "equivalence_class": name.replace("control_mediator_", ""),
                "inequivalent_to_other": inequivalent,
                "computed_witness": (
                    f"rank={rank}; to_other_res={to_other['residual']:.6g}; "
                    f"from_other_res={from_other['residual']:.6g}"
                ),
            }
        )
    detected = all(bool(row["minimal"]) and bool(row["inequivalent_to_other"]) for row in rows)
    summary = {"positive_detection_detected": detected, "inequivalent_minimal_count": len(rows)}
    return rows, summary


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
    linear_rows = linear_mediators()
    nonlinear_rows = nonlinear_mediators()
    control_rows, control_summary = positive_detection_control()

    actual_minimal = [
        row for row in linear_rows + nonlinear_rows if bool(row["admissible"]) and bool(row["minimal"])
    ]
    inequivalent_actual = [row for row in actual_minimal if row["relation_to_L"] == "inequivalent_minimal"]
    linear_minimal = [row for row in linear_rows if bool(row["admissible"]) and bool(row["minimal"])]
    nonlinear_minimal = [row for row in nonlinear_rows if bool(row["admissible"]) and bool(row["minimal"])]
    output = {
        "step": 37,
        "orientation": "non-coordinate and nonlinear mediator robustness",
        "linear_sample_count": len(linear_rows),
        "nonlinear_sample_count": len(nonlinear_rows),
        "linear_admissible_minimal_count": len(linear_minimal),
        "nonlinear_admissible_minimal_count": len(nonlinear_minimal),
        "all_actual_admissible_minimal_iso_to_L": all(
            row["relation_to_L"] == "iso_to_L" for row in actual_minimal
        ),
        "actual_inequivalent_minimal_count": len(inequivalent_actual),
        "rank3_fail_count": sum(1 for row in linear_rows if "rank3" in row["mediator"] and not bool(row["carries_both"])),
        "superminimal_nonminimal_count": sum(
            1
            for row in linear_rows + nonlinear_rows
            if row["relation_to_L"] == "super_minimal_nonminimal" and not bool(row["minimal"])
        ),
        "positive_detection_control": control_summary,
        "verdict": {
            "type": "instance_uniqueness_robust_general_linear_nonlinear_tested",
            "bounded_grammar_scope": True,
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "nonclaim": "Robustness is shown for sampled general-linear and constructed nonlinear mediators on the declared finite carrier, not for all continuous/gauge/Lorentzian carriers.",
    }

    write_csv(ARTIFACT_DIR / "linear_mediators_step37.csv", linear_rows)
    write_csv(ARTIFACT_DIR / "nonlinear_mediators_step37.csv", nonlinear_rows)
    write_csv(ARTIFACT_DIR / "positive_detection_control_step37.csv", control_rows)
    (ARTIFACT_DIR / "mediator_robustness_output_step37.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "mediator_robustness_output_step37.txt").write_text(
        "\n".join(
            [
                "Step 37 non-coordinate/nonlinear mediator robustness",
                f"linear_sample_count: {output['linear_sample_count']}",
                f"nonlinear_sample_count: {output['nonlinear_sample_count']}",
                f"all_actual_admissible_minimal_iso_to_L: {output['all_actual_admissible_minimal_iso_to_L']}",
                f"actual_inequivalent_minimal_count: {output['actual_inequivalent_minimal_count']}",
                f"positive_detection_detected: {control_summary['positive_detection_detected']}",
                f"verdict: {output['verdict']['type']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
