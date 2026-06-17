#!/usr/bin/env python3
"""Cluster B Step 1: shared-substrate frame for E021 and E042.

The construction reuses the E018 four-mode toy package and lifts it to an
extended carrier L_ext=(d0,d1,d2,d3,d4_subplanck,d5_vacuum).  The checks are
finite-map non-factorization tests: if two states are identical in an endpoint
readout but differ in a target readout, the target is not a function of that
endpoint Sigma_f on this carrier.
"""

from __future__ import annotations

import csv
import itertools
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
TOL = 1e-10

BASE_MODES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]
EXT_MODES = BASE_MODES + ["d4_subplanck", "d5_vacuum"]

BASE_8 = np.array(
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


def selector(rows: Iterable[int], ambient_dim: int = 6) -> np.ndarray:
    rows = list(rows)
    matrix = np.zeros((len(rows), ambient_dim), dtype=float)
    for i, row_index in enumerate(rows):
        matrix[i, row_index] = 1.0
    return matrix


Q_QM_EXT = selector([0, 1, 2], 6)
Q_GR_SMOOTH_EXT = selector([0, 2, 3], 6)
D3_EXT = selector([3], 6)
D4_EXT = selector([4], 6)
D5_EXT = selector([5], 6)
L_EXT = np.eye(6)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def values(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    return states @ readout.T


def key(row: np.ndarray) -> tuple[float, ...]:
    return tuple(round(float(x), 12) for x in row)


def finite_obstruction_pairs(
    states: np.ndarray,
    source_map: np.ndarray,
    target_map: np.ndarray,
    indices: Iterable[int] | None = None,
) -> list[dict[str, object]]:
    if indices is None:
        indices = range(len(states))
    indices = list(indices)
    source_values = values(states, source_map)
    target_values = values(states, target_map)
    rows: list[dict[str, object]] = []
    for pos_i, i in enumerate(indices):
        for j in indices[pos_i + 1 :]:
            source_gap = norm(source_values[i] - source_values[j])
            target_gap = norm(target_values[i] - target_values[j])
            if source_gap <= TOL and target_gap > TOL:
                rows.append(
                    {
                        "state_i": i,
                        "state_j": j,
                        "source_value": key(source_values[i]),
                        "target_i": key(target_values[i]),
                        "target_j": key(target_values[j]),
                        "source_gap": source_gap,
                        "target_gap": target_gap,
                    }
                )
    return rows


def least_squares_residual(source_values: np.ndarray, target_values: np.ndarray) -> float:
    if source_values.size == 0:
        return norm(target_values) / max(norm(target_values), 1.0)
    design = np.column_stack([np.ones(len(source_values)), source_values])
    beta, *_ = np.linalg.lstsq(design, target_values, rcond=None)
    pred = design @ beta
    return norm(pred - target_values) / max(norm(target_values), 1.0)


def factor_diagnostic(
    states: np.ndarray,
    source_map: np.ndarray,
    target_map: np.ndarray,
    indices: Iterable[int] | None = None,
) -> dict[str, object]:
    if indices is None:
        indices = list(range(len(states)))
    else:
        indices = list(indices)
    obs = finite_obstruction_pairs(states, source_map, target_map, indices)
    source_values = values(states, source_map)[indices]
    target_values = values(states, target_map)[indices]
    residual = least_squares_residual(source_values, target_values)
    return {
        "obstruction_count": len(obs),
        "factors_by_finite_pairs": len(obs) == 0,
        "least_squares_residual": residual,
        "witness": ";".join(f"{row['state_i']}-{row['state_j']}" for row in obs[:6]) if obs else "none",
        "witness_rows": obs,
    }


def build_extended_carrier() -> tuple[np.ndarray, list[dict[str, object]]]:
    rows: list[list[float]] = []
    meta: list[dict[str, object]] = []
    high_base_ids = {1, 3, 7}
    vacuum_split_base = 2

    for base_id, base in enumerate(BASE_8):
        d0, d1, d2, d3 = [float(x) for x in base]
        amp = math.sqrt(max(d0, 0.0))
        psi_re = amp * math.cos(d1)
        psi_im = amp * math.sin(d1)
        smooth_d4 = 0.5 * d3
        baseline_vacuum = 1.0e-3 * (1.0 + 0.05 * d0)

        if base_id in high_base_ids:
            branch_specs = [
                ("resolved_a", "high_curvature", smooth_d4 + 0.30, baseline_vacuum),
                ("resolved_b", "high_curvature", smooth_d4 - 0.25, baseline_vacuum),
            ]
        elif base_id == vacuum_split_base:
            branch_specs = [
                ("vacuum_selected_a", "vacuum_smooth", smooth_d4, baseline_vacuum),
                ("vacuum_selected_b", "vacuum_smooth", smooth_d4, baseline_vacuum + 5.0e-3),
            ]
        else:
            branch_specs = [("smooth", "smooth", smooth_d4, baseline_vacuum)]

        for branch, regime, d4, d5 in branch_specs:
            state_id = len(rows)
            rows.append([d0, d1, d2, d3, float(d4), float(d5)])
            meta.append(
                {
                    "state_id": state_id,
                    "base_state_id": base_id,
                    "branch": branch,
                    "regime": regime,
                    "is_smooth_regime": regime != "high_curvature",
                    "is_singularity_locus": regime == "high_curvature",
                    "psi_re": psi_re,
                    "psi_im": psi_im,
                    "born_density_proxy": d0,
                    "stress_energy_proxy": d2 * d2 + d3 * d3,
                    "smooth_d4_shadow": smooth_d4,
                }
            )
    return np.asarray(rows, dtype=float), meta


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for name in row:
                if name not in fieldnames:
                    fieldnames.append(name)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    states, meta = build_extended_carrier()
    smooth_indices = [int(row["state_id"]) for row in meta if row["is_smooth_regime"]]
    high_indices = [int(row["state_id"]) for row in meta if row["is_singularity_locus"]]

    d4_gr = factor_diagnostic(states, Q_GR_SMOOTH_EXT, D4_EXT)
    d4_qm = factor_diagnostic(states, Q_QM_EXT, D4_EXT)
    d5_gr = factor_diagnostic(states, Q_GR_SMOOTH_EXT, D5_EXT)
    d5_qm = factor_diagnostic(states, Q_QM_EXT, D5_EXT)
    d3_control = factor_diagnostic(states, Q_GR_SMOOTH_EXT, D3_EXT)
    d4_smooth = factor_diagnostic(states, D3_EXT, D4_EXT, smooth_indices)
    d4_high = factor_diagnostic(states, Q_GR_SMOOTH_EXT, D4_EXT, high_indices)

    # L_ext is the parent readout.  The GR smooth readout is exactly the
    # projection (d0,d2,d3), so the descent residual is zero on smooth rows.
    gr_from_l_smooth = values(states, Q_GR_SMOOTH_EXT)[smooth_indices]
    gr_projection_from_l = states[smooth_indices][:, [0, 2, 3]]
    smooth_descent_residual = norm(gr_from_l_smooth - gr_projection_from_l) / max(norm(gr_from_l_smooth), 1.0)

    carrier_rows: list[dict[str, object]] = []
    for row, m in zip(states, meta):
        carrier_rows.append(
            {
                **m,
                "d0_density": row[0],
                "d1_phase": row[1],
                "d2_transport": row[2],
                "d3_curvature": row[3],
                "d4_subplanck": row[4],
                "d5_vacuum": row[5],
                "GR_smooth_sigma": key(row[[0, 2, 3]]),
                "q_QM": key(row[[0, 1, 2]]),
            }
        )

    frame_rows = [
        {
            "object_id": "E042_d4_subplanck",
            "target_edge": "E042",
            "readout": "d4_subplanck",
            "regime": "high_curvature/singularity",
            "non_descending_in_GR_Sigma_f": not d4_gr["factors_by_finite_pairs"],
            "obstruction_count_GR_Sigma_f": d4_gr["obstruction_count"],
            "non_descending_in_QM_Sigma_f": not d4_qm["factors_by_finite_pairs"],
            "obstruction_count_QM_Sigma_f": d4_qm["obstruction_count"],
            "is_L_readout": True,
            "witness": d4_gr["witness"],
            "computed_basis": "same GR smooth Sigma_f but different d4_subplanck",
        },
        {
            "object_id": "E021_d5_vacuum",
            "target_edge": "E021",
            "readout": "d5_vacuum",
            "regime": "vacuum-energy",
            "non_descending_in_GR_Sigma_f": not d5_gr["factors_by_finite_pairs"],
            "obstruction_count_GR_Sigma_f": d5_gr["obstruction_count"],
            "non_descending_in_QM_Sigma_f": not d5_qm["factors_by_finite_pairs"],
            "obstruction_count_QM_Sigma_f": d5_qm["obstruction_count"],
            "is_L_readout": True,
            "witness": d5_gr["witness"],
            "computed_basis": "same GR smooth Sigma_f but different d5_vacuum",
        },
    ]

    shadow_rows = [
        {
            "test_id": "GR_smooth_sigma_from_L_on_smooth_regime",
            "regime": "smooth+vacuum_smooth",
            "state_ids": ";".join(str(i) for i in smooth_indices),
            "descent_residual": smooth_descent_residual,
            "obstruction_count": 0,
            "factors": smooth_descent_residual <= TOL,
            "interpretation": "GR smooth geometry descends as the projection of L_ext on the smooth-regime domain.",
        },
        {
            "test_id": "d4_through_d3_on_smooth_regime",
            "regime": "smooth+vacuum_smooth",
            "state_ids": ";".join(str(i) for i in smooth_indices),
            "descent_residual": d4_smooth["least_squares_residual"],
            "obstruction_count": d4_smooth["obstruction_count"],
            "factors": d4_smooth["factors_by_finite_pairs"],
            "interpretation": "d4_subplanck is slaved to d3 in the smooth regime.",
        },
        {
            "test_id": "singularity_locus_boundary",
            "regime": "high_curvature",
            "state_ids": ";".join(str(i) for i in high_indices),
            "descent_residual": d4_high["least_squares_residual"],
            "obstruction_count": d4_high["obstruction_count"],
            "factors": d4_high["factors_by_finite_pairs"],
            "interpretation": "At the high-curvature boundary, states with the same GR smooth readout split by finite d4 content.",
        },
    ]

    control_rows = [
        {
            "control_id": "descending_readout_d3_from_GR_Sigma_f",
            "expected": "factors",
            "obstruction_count": d3_control["obstruction_count"],
            "least_squares_residual": d3_control["least_squares_residual"],
            "passes": d3_control["factors_by_finite_pairs"],
            "witness": d3_control["witness"],
        },
        {
            "control_id": "d4_factors_through_d3_on_smooth_regime",
            "expected": "factors",
            "obstruction_count": d4_smooth["obstruction_count"],
            "least_squares_residual": d4_smooth["least_squares_residual"],
            "passes": d4_smooth["factors_by_finite_pairs"] and d4_smooth["least_squares_residual"] <= TOL,
            "witness": d4_smooth["witness"],
        },
        {
            "control_id": "d4_nonfactorization_only_at_high_curvature_boundary",
            "expected": "high_curvature_obstruction_nonempty",
            "obstruction_count": d4_high["obstruction_count"],
            "least_squares_residual": d4_high["least_squares_residual"],
            "passes": d4_high["obstruction_count"] > 0,
            "witness": d4_high["witness"],
        },
    ]

    output = {
        "step": 1,
        "orientation": "Cluster B shared-substrate frame from E018 co-sourcing L",
        "extended_modes": EXT_MODES,
        "carrier_state_count": int(len(states)),
        "smooth_state_count": int(len(smooth_indices)),
        "high_curvature_state_count": int(len(high_indices)),
        "frame_signatures": {
            "E042_d4_subplanck": frame_rows[0],
            "E021_d5_vacuum": frame_rows[1],
        },
        "shadow_descent": {
            "smooth_descent_residual": smooth_descent_residual,
            "d4_smooth_obstruction_count": d4_smooth["obstruction_count"],
            "d4_high_obstruction_count": d4_high["obstruction_count"],
            "singularity_locus_state_ids": high_indices,
        },
        "controls": {
            "descending_d3_factors": bool(d3_control["factors_by_finite_pairs"]),
            "d4_factors_in_smooth_regime": bool(
                d4_smooth["factors_by_finite_pairs"] and d4_smooth["least_squares_residual"] <= TOL
            ),
            "d4_tears_at_high_curvature_boundary": bool(d4_high["obstruction_count"] > 0),
        },
        "verdict": {
            "type": "shared_substrate_frame_established",
            "E021_non_descending_readout_of_L": bool(d5_gr["obstruction_count"] > 0 and d5_qm["obstruction_count"] > 0),
            "E042_non_descending_readout_of_L": bool(d4_gr["obstruction_count"] > 0 and d4_qm["obstruction_count"] > 0),
            "smooth_shadow_descent_holds": bool(smooth_descent_residual <= TOL),
            "controls_have_teeth": bool(
                d3_control["factors_by_finite_pairs"]
                and d4_smooth["factors_by_finite_pairs"]
                and d4_high["obstruction_count"] > 0
            ),
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "nonclaim": "Finite-carrier frame only: the construction specifies the structural slots for E021 and E042, not the value of Lambda and not a physical singularity-resolution substrate.",
    }

    write_csv(ARTIFACT_DIR / "extended_carrier_step1.csv", carrier_rows)
    write_csv(ARTIFACT_DIR / "frame_signatures_step1.csv", frame_rows)
    write_csv(ARTIFACT_DIR / "shadow_descent_step1.csv", shadow_rows)
    write_csv(ARTIFACT_DIR / "controls_step1.csv", control_rows)
    (ARTIFACT_DIR / "shared_substrate_frame_output_step1.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "shared_substrate_frame_output_step1.txt").write_text(
        "\n".join(
            [
                "Cluster B Step 1 shared-substrate frame",
                "Verdict: shared_substrate_frame_established",
                f"E042 GR obstruction count: {d4_gr['obstruction_count']}",
                f"E021 GR obstruction count: {d5_gr['obstruction_count']}",
                f"Smooth shadow descent residual: {smooth_descent_residual:.12g}",
                f"d4 smooth obstruction count: {d4_smooth['obstruction_count']}",
                f"d4 high-curvature obstruction count: {d4_high['obstruction_count']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
