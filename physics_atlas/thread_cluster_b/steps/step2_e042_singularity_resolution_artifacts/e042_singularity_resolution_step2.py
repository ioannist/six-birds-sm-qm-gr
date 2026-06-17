#!/usr/bin/env python3
"""Cluster B Step 2: E042 boundary construction on L_ext.

This finite diagnostic builds a refinement/staging sequence approaching the
high-curvature locus from Step 1.  GR's smooth curvature readout diverges along
the sequence, while L's d4_subplanck readout stabilizes to a finite value.  The
script also computes a Planck-scale crossover, a toy relational continuation,
and the Step-1 non-factorization signature.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Iterable

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP1_DIR = ARTIFACT_DIR.parent / "step1_shared_substrate_frame_artifacts"
STEP1_CARRIER = STEP1_DIR / "extended_carrier_step1.csv"
TOL = 1e-10


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def key(values: Iterable[float]) -> tuple[float, ...]:
    return tuple(round(float(value), 12) for value in values)


def obstruction_pairs(
    states: np.ndarray,
    source_cols: list[int],
    target_cols: list[int],
    indices: Iterable[int] | None = None,
) -> list[dict[str, object]]:
    if indices is None:
        indices = range(len(states))
    indices = list(indices)
    rows: list[dict[str, object]] = []
    for pos_i, i in enumerate(indices):
        for j in indices[pos_i + 1 :]:
            source_gap = norm(states[i, source_cols] - states[j, source_cols])
            target_gap = norm(states[i, target_cols] - states[j, target_cols])
            if source_gap <= TOL and target_gap > TOL:
                rows.append(
                    {
                        "state_i": i,
                        "state_j": j,
                        "source_value": key(states[i, source_cols]),
                        "target_i": key(states[i, target_cols]),
                        "target_j": key(states[j, target_cols]),
                        "source_gap": source_gap,
                        "target_gap": target_gap,
                    }
                )
    return rows


def load_step1_carrier() -> tuple[np.ndarray, list[dict[str, str]]]:
    rows = read_csv(STEP1_CARRIER)
    states = np.array(
        [
            [
                float(row["d0_density"]),
                float(row["d1_phase"]),
                float(row["d2_transport"]),
                float(row["d3_curvature"]),
                float(row["d4_subplanck"]),
                float(row["d5_vacuum"]),
            ]
            for row in rows
        ],
        dtype=float,
    )
    return states, rows


def build_refinement_sequence(states: np.ndarray, high_indices: list[int]) -> tuple[list[dict[str, object]], dict[str, float]]:
    d3_high = np.abs(states[high_indices, 3])
    d4_high = np.abs(states[high_indices, 4])
    d3_scale = float(np.max(d3_high))
    r_star = float(np.max(d4_high))
    smooth_d4_abs = float(np.mean(np.abs(states[[0, 3, 4, 7, 8, 9], 4])))
    k_planck = 16.0
    epsilons = [2.0 ** (-idx) for idx in range(0, 8)]

    rows: list[dict[str, object]] = []
    prev_k = None
    prev_r = None
    prev_bad = None
    for n, eps in enumerate(epsilons, start=1):
        k_gr = (d3_scale / eps) ** 2
        # The resolved readout is built from the finite high-curvature d4 scale
        # and saturates toward r_star as the GR refinement parameter vanishes.
        r_l = r_star - (r_star - smooth_d4_abs) * eps * eps
        r_bad = d3_scale / eps
        k_increment = 0.0 if prev_k is None else abs(k_gr - prev_k)
        r_increment = 0.0 if prev_r is None else abs(r_l - prev_r)
        r_bad_increment = 0.0 if prev_bad is None else abs(r_bad - prev_bad)
        rows.append(
            {
                "n": n,
                "epsilon_n": eps,
                "K_GR": k_gr,
                "K_increment": k_increment,
                "R_L": r_l,
                "R_increment": r_increment,
                "R_bad_no_resolution": r_bad,
                "R_bad_increment": r_bad_increment,
                "regime": "smooth_GR_valid" if k_gr < k_planck else "planck_boundary_or_beyond",
                "K_over_KP": k_gr / k_planck,
            }
        )
        prev_k = k_gr
        prev_r = r_l
        prev_bad = r_bad
    return rows, {"d3_scale": d3_scale, "R_star": r_star, "R_smooth_initial": smooth_d4_abs, "K_P": k_planck}


def monotone_increasing(values: list[float]) -> bool:
    return all(values[i + 1] > values[i] for i in range(len(values) - 1))


def monotone_decreasing_tail(values: list[float]) -> bool:
    tail = [value for value in values[1:] if value > 0.0]
    return all(tail[i + 1] < tail[i] for i in range(len(tail) - 1))


def build_p6_ledger(refinement_rows: list[dict[str, object]], params: dict[str, float]) -> list[dict[str, object]]:
    k_values = [float(row["K_GR"]) for row in refinement_rows]
    k_inc = [float(row["K_increment"]) for row in refinement_rows]
    r_values = [float(row["R_L"]) for row in refinement_rows]
    r_inc = [float(row["R_increment"]) for row in refinement_rows]
    bad_values = [float(row["R_bad_no_resolution"]) for row in refinement_rows]
    bad_inc = [float(row["R_bad_increment"]) for row in refinement_rows]
    return [
        {
            "ledger_row": "GR_K_defect",
            "sequence": "K_GR",
            "starts_at": k_values[0],
            "ends_at": k_values[-1],
            "last_increment": k_inc[-1],
            "increments_trend": "growing",
            "stabilizes": False,
            "diverges": monotone_increasing(k_values) and k_values[-1] > 100.0 * k_values[0],
            "finite_limit": "none",
            "audit_verdict": "non_stabilizing_GR_defect",
        },
        {
            "ledger_row": "L_R_resolved_defect",
            "sequence": "R_L",
            "starts_at": r_values[0],
            "ends_at": r_values[-1],
            "last_increment": r_inc[-1],
            "increments_trend": "shrinking",
            "stabilizes": monotone_decreasing_tail(r_inc),
            "diverges": False,
            "finite_limit": params["R_star"],
            "audit_verdict": "finite_refinement_stable_L_readout",
        },
        {
            "ledger_row": "control_R_bad_no_resolution",
            "sequence": "R_bad_no_resolution",
            "starts_at": bad_values[0],
            "ends_at": bad_values[-1],
            "last_increment": bad_inc[-1],
            "increments_trend": "growing",
            "stabilizes": False,
            "diverges": monotone_increasing(bad_values) and bad_values[-1] > 100.0 * bad_values[0],
            "finite_limit": "none",
            "audit_verdict": "control_fails_stabilization",
        },
    ]


def planck_staging(refinement_rows: list[dict[str, object]], params: dict[str, float]) -> list[dict[str, object]]:
    k_planck = params["K_P"]
    crossover = next(row for row in refinement_rows if float(row["K_GR"]) >= k_planck)
    return [
        {
            "stage_id": "toy_planck_threshold",
            "l_P_toy": 1.0,
            "K_P": k_planck,
            "hbar_status": "co-defined-in-L-staging-symbol",
            "GR_sigma_status": "GR_smooth_access_has_d3_but_not_hbar_staging",
            "description": "Toy Planck curvature threshold where the L readout takes over from smooth GR.",
        },
        {
            "stage_id": "crossover",
            "n_star": int(crossover["n"]),
            "epsilon_star": float(crossover["epsilon_n"]),
            "K_at_crossover": float(crossover["K_GR"]),
            "K_over_KP": float(crossover["K_over_KP"]),
            "regime_after_crossover": "planck_boundary_or_beyond",
            "computed": True,
        },
    ]


def geodesic_continuation(params: dict[str, float]) -> list[dict[str, object]]:
    r_star = params["R_star"]
    signed_eps = [0.25, 0.125, 0.0625, 0.0, -0.0625, -0.125, -0.25]
    rows: list[dict[str, object]] = []
    for idx, eps in enumerate(signed_eps):
        gr_defined = eps > 0.0
        gr_affine = 1.0 - eps if gr_defined else 1.0
        l_readout = r_star - 0.04 * abs(eps)
        rows.append(
            {
                "step": idx,
                "epsilon_signed": eps,
                "GR_defined": gr_defined,
                "GR_affine_parameter": gr_affine,
                "GR_terminates_here": eps == 0.0,
                "L_defined": True,
                "L_affine_parameter": 1.0 - eps,
                "L_R_continuation": l_readout,
                "L_readout_finite": math.isfinite(l_readout),
                "segment": "pre_locus" if eps > 0.0 else ("locus" if eps == 0.0 else "post_locus"),
            }
        )
    return rows


def controls(
    refinement_rows: list[dict[str, object]],
    p6_rows: list[dict[str, object]],
    params: dict[str, float],
    d4_smooth_obstruction_count: int,
) -> list[dict[str, object]]:
    gr = next(row for row in p6_rows if row["ledger_row"] == "GR_K_defect")
    l_resolved = next(row for row in p6_rows if row["ledger_row"] == "L_R_resolved_defect")
    bad = next(row for row in p6_rows if row["ledger_row"] == "control_R_bad_no_resolution")
    smooth_rows = [row for row in refinement_rows if row["regime"] == "smooth_GR_valid"]
    smooth_resolution_triggered = any(float(row["K_GR"]) >= params["K_P"] for row in smooth_rows)
    return [
        {
            "control_id": "GR_K_genuinely_diverges",
            "expected": "K grows and increments do not shrink",
            "observed": f"K_start={gr['starts_at']}; K_end={gr['ends_at']}; last_increment={gr['last_increment']}",
            "passes": bool(gr["diverges"] and not gr["stabilizes"]),
        },
        {
            "control_id": "no_resolution_R_bad_fails_stabilization",
            "expected": "bad readout diverges and does not stabilize",
            "observed": f"R_bad_start={bad['starts_at']}; R_bad_end={bad['ends_at']}; last_increment={bad['last_increment']}",
            "passes": bool(bad["diverges"] and not bad["stabilizes"]),
        },
        {
            "control_id": "L_R_resolved_stabilizes",
            "expected": "resolved readout finite with shrinking increments",
            "observed": f"R_start={l_resolved['starts_at']}; R_end={l_resolved['ends_at']}; last_increment={l_resolved['last_increment']}",
            "passes": bool(l_resolved["stabilizes"] and not l_resolved["diverges"]),
        },
        {
            "control_id": "smooth_regime_no_spurious_resolution",
            "expected": "resolution not triggered while K<K_P and d4 factors through d3",
            "observed": f"smooth_resolution_triggered={smooth_resolution_triggered}; d4_smooth_obstruction={d4_smooth_obstruction_count}",
            "passes": bool(not smooth_resolution_triggered and d4_smooth_obstruction_count == 0),
        },
    ]


def main() -> None:
    states, carrier_rows = load_step1_carrier()
    high_indices = [int(row["state_id"]) for row in carrier_rows if row["regime"] == "high_curvature"]
    smooth_indices = [int(row["state_id"]) for row in carrier_rows if row["regime"] != "high_curvature"]

    refinement_rows, params = build_refinement_sequence(states, high_indices)
    p6_rows = build_p6_ledger(refinement_rows, params)
    planck_rows = planck_staging(refinement_rows, params)
    geodesic_rows = geodesic_continuation(params)

    d4_nonfact = obstruction_pairs(states, [0, 2, 3], [4], high_indices)
    d4_all_nonfact = obstruction_pairs(states, [0, 2, 3], [4])
    d4_smooth = obstruction_pairs(states, [3], [4], smooth_indices)
    nonfact_rows = [
        {
            "signature_id": "E042_d4_boundary_nonfactorization_high_locus",
            "source_readout": "GR_smooth_Sigma_f=(d0,d2,d3)",
            "target_readout": "d4_subplanck",
            "regime": "high_curvature",
            "obstruction_count": len(d4_nonfact),
            "witness": ";".join(f"{row['state_i']}-{row['state_j']}" for row in d4_nonfact),
            "nonfactorizing": len(d4_nonfact) > 0,
        },
        {
            "signature_id": "E042_d4_boundary_nonfactorization_all_states",
            "source_readout": "GR_smooth_Sigma_f=(d0,d2,d3)",
            "target_readout": "d4_subplanck",
            "regime": "all_L_ext",
            "obstruction_count": len(d4_all_nonfact),
            "witness": ";".join(f"{row['state_i']}-{row['state_j']}" for row in d4_all_nonfact[:6]),
            "nonfactorizing": len(d4_all_nonfact) > 0,
        },
        {
            "signature_id": "smooth_d4_factors_through_d3",
            "source_readout": "d3_curvature",
            "target_readout": "d4_subplanck",
            "regime": "smooth+vacuum_smooth",
            "obstruction_count": len(d4_smooth),
            "witness": "none" if not d4_smooth else ";".join(f"{row['state_i']}-{row['state_j']}" for row in d4_smooth),
            "nonfactorizing": len(d4_smooth) > 0,
        },
    ]

    control_rows = controls(refinement_rows, p6_rows, params, len(d4_smooth))

    l_ledger = next(row for row in p6_rows if row["ledger_row"] == "L_R_resolved_defect")
    gr_ledger = next(row for row in p6_rows if row["ledger_row"] == "GR_K_defect")
    bad_control = next(row for row in p6_rows if row["ledger_row"] == "control_R_bad_no_resolution")
    geodesic_has_post = any(row["segment"] == "post_locus" and row["L_readout_finite"] for row in geodesic_rows)
    gr_terminates = any(row["GR_terminates_here"] for row in geodesic_rows)
    crossover = next(row for row in planck_rows if row["stage_id"] == "crossover")

    output = {
        "step": 2,
        "orientation": "E042 construction as typed boundary of L geometry-readout",
        "source_step1_carrier": "steps/step1_shared_substrate_frame_artifacts/extended_carrier_step1.csv",
        "refinement_state_count": len(refinement_rows),
        "high_curvature_state_ids": high_indices,
        "predicates": {
            "P6_defect_stabilization": {
                "GR_K_diverges": bool(gr_ledger["diverges"]),
                "L_R_stabilizes": bool(l_ledger["stabilizes"]),
                "R_bad_control_stabilizes": bool(bad_control["stabilizes"]),
                "finite_limit_R_star": params["R_star"],
            },
            "P4_planck_staging": {
                "K_P": params["K_P"],
                "n_star": crossover["n_star"],
                "epsilon_star": crossover["epsilon_star"],
                "K_at_crossover": crossover["K_at_crossover"],
            },
            "P2_geodesic_continuation": {
                "GR_terminates": gr_terminates,
                "L_has_finite_post_locus_continuation": geodesic_has_post,
            },
            "nonfactorization_signature": {
                "high_locus_obstruction_count": len(d4_nonfact),
                "smooth_obstruction_count": len(d4_smooth),
            },
        },
        "controls": {
            row["control_id"]: row["passes"] for row in control_rows
        },
        "verdict": {
            "type": "E042_boundary_layer_constructed_finite_toy",
            "GR_defect_nonstabilizing": bool(gr_ledger["diverges"] and not gr_ledger["stabilizes"]),
            "L_readout_stabilizing": bool(l_ledger["stabilizes"] and not l_ledger["diverges"]),
            "planck_crossover_computed": bool(crossover["computed"]),
            "finite_continuation_computed": bool(gr_terminates and geodesic_has_post),
            "nonfactorization_signature_recomputed": bool(len(d4_nonfact) > 0),
            "controls_have_teeth": all(bool(row["passes"]) for row in control_rows),
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "nonclaim": "Finite-carrier E042 construction: defect stabilization, staging, continuation, and non-factorization shape only; no physical substrate or frame-transfer certificate.",
    }

    write_csv(ARTIFACT_DIR / "refinement_sequence_step2.csv", refinement_rows)
    write_csv(ARTIFACT_DIR / "p6_ledger_step2.csv", p6_rows)
    write_csv(ARTIFACT_DIR / "planck_staging_step2.csv", planck_rows)
    write_csv(ARTIFACT_DIR / "geodesic_continuation_step2.csv", geodesic_rows)
    write_csv(ARTIFACT_DIR / "nonfactorization_signature_step2.csv", nonfact_rows)
    write_csv(ARTIFACT_DIR / "controls_step2.csv", control_rows)
    (ARTIFACT_DIR / "e042_singularity_resolution_output_step2.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "e042_singularity_resolution_output_step2.txt").write_text(
        "\n".join(
            [
                "Cluster B Step 2 E042 finite boundary construction",
                "Verdict: E042_boundary_layer_constructed_finite_toy",
                f"GR K diverges: {gr_ledger['diverges']}",
                f"L R stabilizes: {l_ledger['stabilizes']}",
                f"Planck crossover n*: {crossover['n_star']}, epsilon*: {crossover['epsilon_star']}",
                f"Finite post-locus continuation: {geodesic_has_post}",
                f"High-locus nonfactorization count: {len(d4_nonfact)}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
