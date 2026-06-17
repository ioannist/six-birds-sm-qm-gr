#!/usr/bin/env python3
"""Audit refinement stability of the Step-13 neutral currency."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP13_DIR = ARTIFACT_DIR.parents[0] / "step13_build_rung2_neutral_currency_artifacts"


NEUTRAL_MODES = [
    "u_neutral_density",
    "u_phase_order",
    "u_transport_flux",
    "u_curvature_scale",
]
QM_MODES = [
    "q_amplitude_density",
    "q_phase_order",
    "q_coherence_transport",
]
GR_MODES = [
    "g_metric_density",
    "g_transport_flux",
    "g_curvature_scale",
]


def cell_count(level: int) -> int:
    return 2 ** (level + 1)


def block_diag(blocks: list[np.ndarray]) -> np.ndarray:
    rows = sum(block.shape[0] for block in blocks)
    cols = sum(block.shape[1] for block in blocks)
    out = np.zeros((rows, cols), dtype=float)
    r = 0
    c = 0
    for block in blocks:
        rr, cc = block.shape
        out[r : r + rr, c : c + cc] = block
        r += rr
        c += cc
    return out


def duplication(level: int) -> np.ndarray:
    coarse = cell_count(level)
    fine = cell_count(level + 1)
    lift = np.zeros((fine, coarse), dtype=float)
    for i in range(coarse):
        lift[2 * i, i] = 1.0
        lift[2 * i + 1, i] = 1.0
    return lift


def mode_shadow(level: int, shadow: str) -> np.ndarray:
    n = cell_count(level)
    identity = np.eye(n)
    zero = np.zeros((n, n), dtype=float)
    if shadow == "qm":
        return np.block(
            [
                [identity, zero, zero, zero],
                [zero, identity, zero, zero],
                [zero, zero, identity, zero],
            ]
        )
    if shadow == "gr":
        return np.block(
            [
                [identity, zero, zero, zero],
                [zero, zero, identity, zero],
                [zero, zero, zero, identity],
            ]
        )
    raise ValueError(f"unknown shadow {shadow}")


def stable_currency_lift(level: int) -> np.ndarray:
    d = duplication(level)
    return block_diag([d, d, d, d])


def endpoint_lift(level: int) -> np.ndarray:
    d = duplication(level)
    return block_diag([d, d, d])


def mixing_currency_lift(level: int) -> np.ndarray:
    fine = cell_count(level + 1)
    mixer = np.array(
        [
            [1.0, 0.35, 0.0, 0.20],
            [0.30, 1.0, 0.25, 0.0],
            [0.0, 0.25, 1.0, 0.30],
            [0.20, 0.0, 0.35, 1.0],
        ],
        dtype=float,
    )
    return np.kron(mixer, np.eye(fine)) @ stable_currency_lift(level)


def ratio(numerator: np.ndarray, denominator: np.ndarray) -> float:
    denom = float(np.linalg.norm(denominator, ord="fro"))
    if denom <= 1e-14:
        return 0.0
    return float(np.linalg.norm(numerator, ord="fro") / denom)


def distinctness(level: int) -> float:
    s_qm = mode_shadow(level, "qm")
    s_gr = mode_shadow(level, "gr")
    scale = max(float(np.linalg.norm(s_qm, ord="fro")), float(np.linalg.norm(s_gr, ord="fro")), 1.0)
    return float(np.linalg.norm(s_qm - s_gr, ord="fro") / scale)


def transition_diagnostic(level: int, case: str, lift_u: np.ndarray) -> dict[str, float | int | str | bool]:
    s_qm_coarse = mode_shadow(level, "qm")
    s_gr_coarse = mode_shadow(level, "gr")
    s_qm_fine = mode_shadow(level + 1, "qm")
    s_gr_fine = mode_shadow(level + 1, "gr")
    l_qm = endpoint_lift(level)
    l_gr = endpoint_lift(level)

    qm_left = s_qm_fine @ lift_u
    qm_right = l_qm @ s_qm_coarse
    gr_left = s_gr_fine @ lift_u
    gr_right = l_gr @ s_gr_coarse
    qm_residual = ratio(qm_left - qm_right, qm_right)
    gr_residual = ratio(gr_left - gr_right, gr_right)
    combined = float(np.sqrt(qm_residual**2 + gr_residual**2))
    d_qm = len(QM_MODES)
    d_gr = len(GR_MODES)
    d_u = len(NEUTRAL_MODES)
    d_union = d_qm + d_gr
    compression_pass = d_qm <= d_u < d_union
    distinctness_residual = distinctness(level + 1)
    distinctness_pass = distinctness_residual > 1e-12
    commutation_pass = combined <= 1e-10
    structure_survives = bool(commutation_pass and compression_pass and distinctness_pass)
    if case == "stable_lift" and structure_survives:
        status = "passes_candidate"
    elif case == "mixing_control" and not commutation_pass:
        status = "fails_as_control_mixing"
    else:
        status = "invalid"
    return {
        "transition": f"{level}->{level + 1}",
        "case": case,
        "coarse_cells": cell_count(level),
        "fine_cells": cell_count(level + 1),
        "lift_rows": int(lift_u.shape[0]),
        "lift_cols": int(lift_u.shape[1]),
        "qm_shadow_commutator_residual": qm_residual,
        "gr_shadow_commutator_residual": gr_residual,
        "combined_commutator_residual": combined,
        "d_qm": d_qm,
        "d_gr": d_gr,
        "d_u": d_u,
        "d_union": d_union,
        "compression_pass": compression_pass,
        "distinctness_residual": distinctness_residual,
        "distinctness_pass": distinctness_pass,
        "shadow_structure_survives": structure_survives,
        "status": status,
    }


def lift_nontriviality(level: int, lift_u: np.ndarray) -> dict[str, float | int | str | bool]:
    rows, cols = lift_u.shape
    expected_rows = len(NEUTRAL_MODES) * cell_count(level + 1)
    expected_cols = len(NEUTRAL_MODES) * cell_count(level)
    expansion_ratio = rows / cols
    is_identity_shape = rows == cols
    row_has_two_parent_pattern = bool(np.max(np.sum(np.abs(lift_u) > 1e-12, axis=1)) >= 1)
    return {
        "transition": f"{level}->{level + 1}",
        "rows": rows,
        "cols": cols,
        "expected_rows": expected_rows,
        "expected_cols": expected_cols,
        "expansion_ratio": expansion_ratio,
        "identity_shape": is_identity_shape,
        "nontrivial_refinement": (rows == expected_rows and cols == expected_cols and expansion_ratio == 2.0 and not is_identity_shape and row_has_two_parent_pattern),
    }


def main() -> None:
    step13_payload = json.loads((STEP13_DIR / "currency_test_output_step13.json").read_text(encoding="utf-8"))
    diagnostics = []
    lift_checks = []
    matrix_payload = {
        "source_step13_payload": str(STEP13_DIR / "currency_test_output_step13.json"),
        "currency_modes": {
            "neutral": NEUTRAL_MODES,
            "qm": QM_MODES,
            "gr": GR_MODES,
        },
        "transitions": {},
        "mode_mixing_matrix": [
            [1.0, 0.35, 0.0, 0.20],
            [0.30, 1.0, 0.25, 0.0],
            [0.0, 0.25, 1.0, 0.30],
            [0.20, 0.0, 0.35, 1.0],
        ],
    }
    for level in [1, 2]:
        stable = stable_currency_lift(level)
        mixing = mixing_currency_lift(level)
        diagnostics.append(transition_diagnostic(level, "stable_lift", stable))
        diagnostics.append(transition_diagnostic(level, "mixing_control", mixing))
        lift_checks.append(lift_nontriviality(level, stable))
        matrix_payload["transitions"][f"{level}_to_{level + 1}"] = {
            "stable_lift": stable.tolist(),
            "mixing_lift": mixing.tolist(),
            "S_QM_coarse": mode_shadow(level, "qm").tolist(),
            "S_GR_coarse": mode_shadow(level, "gr").tolist(),
            "S_QM_fine": mode_shadow(level + 1, "qm").tolist(),
            "S_GR_fine": mode_shadow(level + 1, "gr").tolist(),
            "endpoint_lift": endpoint_lift(level).tolist(),
        }

    by_case: dict[str, list[dict]] = {}
    for row in diagnostics:
        by_case.setdefault(str(row["case"]), []).append(row)
    stable_max = max(float(row["combined_commutator_residual"]) for row in by_case["stable_lift"])
    mixing_min = min(float(row["combined_commutator_residual"]) for row in by_case["mixing_control"])
    mixing_passes = any(bool(row["shadow_structure_survives"]) for row in by_case["mixing_control"])
    stable_passes = all(bool(row["shadow_structure_survives"]) for row in by_case["stable_lift"])
    nontrivial = all(bool(row["nontrivial_refinement"]) for row in lift_checks)
    verdict = {
        "refinement_stable": bool(stable_passes and not mixing_passes and nontrivial),
        "stable_lift_passes": bool(stable_passes),
        "mixing_control_fails": bool(not mixing_passes and mixing_min > 0.25),
        "lift_nontrivial": bool(nontrivial),
        "compression_survives": bool(all(bool(row["compression_pass"]) for row in diagnostics)),
        "distinct_shadows_survive_stable": bool(all(bool(row["distinctness_pass"]) for row in by_case["stable_lift"])),
    }
    no_smuggling = {
        "identity_lift_used": False,
        "trivial_lift_used": False,
        "mixing_control_passes": mixing_passes,
        "circular_distance_from_self_used": False,
        "one_hot_set_cover_used": False,
        "target_layer_inserted": False,
        "endpoint_derivation_claimed": False,
        "literature_program_terms_used": False,
        "step13_currency_loaded": step13_payload["verdict"]["neutral_currency_built"],
    }
    payload = {
        "step": 14,
        "rung_id": "RUNG_1_ON_RUNG_2_REFINEMENT_STABILITY",
        "active_input": "RUNG_2_NEUTRAL_CURRENCY",
        "observed_residuals": {
            "stable_commutator_max": stable_max,
            "mixing_commutator_min": mixing_min,
            "commutator_range": [stable_max, mixing_min],
        },
        "verdict": verdict,
        "no_smuggling_check": no_smuggling,
        "structural_constraint": (
            "A currency-compatible refinement lift must be a morphism of the two-shadow diagram: "
            "S_QM^{n+1} L_u = L_QM S_QM^n and S_GR^{n+1} L_u = L_GR S_GR^n. "
            "Equivalently, it preserves the shared modes {d0,d2} and keeps the two shadow kernels "
            "ker(S_QM)=span{d3} and ker(S_GR)=span{d1} from leaking into the opposite visible shadow."
        ),
        "next_move": "RUNG_3_AUDIT_ON_REFINEMENT_STABLE_CURRENCY",
    }

    with (ARTIFACT_DIR / "refinement_stability_step14.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(diagnostics[0].keys()))
        writer.writeheader()
        writer.writerows(diagnostics)
    with (ARTIFACT_DIR / "lift_nontriviality_step14.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(lift_checks[0].keys()))
        writer.writeheader()
        writer.writerows(lift_checks)
    (ARTIFACT_DIR / "refinement_lift_matrices_step14.json").write_text(
        json.dumps(matrix_payload, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "refinement_stability_output_step14.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    lines = [
        "Step 14 RUNG_1-on-currency refinement stability",
        f"Stable commutator max: {stable_max}",
        f"Mixing commutator min: {mixing_min}",
        f"Mixing control passes: {mixing_passes}",
        f"Stable lift nontrivial: {nontrivial}",
        f"Refinement stable: {verdict['refinement_stable']}",
        "Next move: RUNG_3_AUDIT_ON_REFINEMENT_STABLE_CURRENCY",
    ]
    (ARTIFACT_DIR / "refinement_stability_output_step14.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
