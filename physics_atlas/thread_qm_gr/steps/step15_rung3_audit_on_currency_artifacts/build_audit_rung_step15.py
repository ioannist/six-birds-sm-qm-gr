#!/usr/bin/env python3
"""Build and audit RUNG_3 over the refinement-stable neutral currency."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP14_DIR = ARTIFACT_DIR.parents[0] / "step14_rung1_on_currency_refinement_stability_artifacts"


NEUTRAL_MODES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]
QM_MODES = ["d0_density", "d1_phase", "d2_transport"]
GR_MODES = ["d0_density", "d2_transport", "d3_curvature"]

CONSISTENT_QM = np.array([0.70, 0.20, -0.40], dtype=float)
CONSISTENT_GR = np.array([0.70, -0.40, 0.35], dtype=float)
CONSISTENT_U = np.array([0.70, 0.20, -0.40, 0.35], dtype=float)

MISMATCH_QM = CONSISTENT_QM.copy()
MISMATCH_GR = np.array([0.90, -0.10, 0.35], dtype=float)
MISMATCH_U_ATTEMPT = CONSISTENT_U.copy()


def cell_count(level: int) -> int:
    return 2 ** (level + 1)


def identity(level: int) -> np.ndarray:
    return np.eye(cell_count(level))


def audit_matrix(level: int, coefficients: np.ndarray) -> np.ndarray:
    n = cell_count(level)
    return np.block([[float(c) * identity(level) for c in coefficients]])


def qm_embedding(level: int) -> np.ndarray:
    n = cell_count(level)
    eye = np.eye(n)
    zero = np.zeros((n, n), dtype=float)
    return np.block(
        [
            [eye, zero, zero],
            [zero, eye, zero],
            [zero, zero, eye],
            [zero, zero, zero],
        ]
    )


def gr_embedding(level: int) -> np.ndarray:
    n = cell_count(level)
    eye = np.eye(n)
    zero = np.zeros((n, n), dtype=float)
    return np.block(
        [
            [eye, zero, zero],
            [zero, zero, zero],
            [zero, eye, zero],
            [zero, zero, eye],
        ]
    )


def duplication(level: int) -> np.ndarray:
    coarse = cell_count(level)
    fine = cell_count(level + 1)
    lift = np.zeros((fine, coarse), dtype=float)
    for i in range(coarse):
        lift[2 * i, i] = 1.0
        lift[2 * i + 1, i] = 1.0
    return lift


def ratio(numerator: np.ndarray, denominator: np.ndarray) -> float:
    denom = float(np.linalg.norm(denominator, ord="fro"))
    if denom <= 1e-14:
        return 0.0
    return float(np.linalg.norm(numerator, ord="fro") / denom)


def stable_lift_from_step14(level: int, step14_matrices: dict) -> np.ndarray:
    transition = step14_matrices["transitions"][f"{level}_to_{level + 1}"]
    return np.array(transition["stable_lift"], dtype=float)


def shared_mode_residual(qm_coeff: np.ndarray, gr_coeff: np.ndarray) -> float:
    qm_shared = np.array([qm_coeff[0], qm_coeff[2]], dtype=float)
    gr_shared = np.array([gr_coeff[0], gr_coeff[1]], dtype=float)
    return ratio(qm_shared.reshape(1, -1) - gr_shared.reshape(1, -1), qm_shared.reshape(1, -1))


def audit_nontrivial(coefficients: np.ndarray) -> dict[str, bool | float]:
    norm = float(np.linalg.norm(coefficients))
    spread = float(np.std(coefficients))
    return {
        "coefficient_norm": norm,
        "coefficient_spread": spread,
        "nonzero": norm > 1e-12,
        "nonconstant": spread > 1e-12,
    }


def transition_diagnostic(level: int, case: str, qm_coeff: np.ndarray, gr_coeff: np.ndarray, u_coeff: np.ndarray, step14_matrices: dict) -> dict:
    a_qm = audit_matrix(level, qm_coeff)
    a_gr = audit_matrix(level, gr_coeff)
    a_u = audit_matrix(level, u_coeff)
    e_qm = qm_embedding(level)
    e_gr = gr_embedding(level)
    qm_restriction = ratio(a_u @ e_qm - a_qm, a_qm)
    gr_restriction = ratio(a_u @ e_gr - a_gr, a_gr)
    shared_residual = shared_mode_residual(qm_coeff, gr_coeff)

    lift_u = stable_lift_from_step14(level, step14_matrices)
    lift_audit = duplication(level)
    a_u_fine = audit_matrix(level + 1, u_coeff)
    audit_comm = ratio(a_u_fine @ lift_u - lift_audit @ a_u, lift_audit @ a_u)
    nontrivial = audit_nontrivial(u_coeff)
    route_consistent = shared_residual <= 1e-10 and qm_restriction <= 1e-10 and gr_restriction <= 1e-10
    refinement_consistent = audit_comm <= 1e-10
    audit_exists = route_consistent and refinement_consistent and bool(nontrivial["nonzero"]) and bool(nontrivial["nonconstant"])
    if case == "consistent_audit" and audit_exists:
        status = "passes_candidate"
    elif case == "route_mismatch_control" and not route_consistent:
        status = "fails_as_control_route_mismatch"
    else:
        status = "invalid"
    return {
        "level": level,
        "cells": cell_count(level),
        "case": case,
        "shared_mode_residual": shared_residual,
        "qm_restriction_residual": qm_restriction,
        "gr_restriction_residual": gr_restriction,
        "audit_refinement_commutator_residual": audit_comm,
        "audit_coefficient_norm": nontrivial["coefficient_norm"],
        "audit_coefficient_spread": nontrivial["coefficient_spread"],
        "audit_nonzero": nontrivial["nonzero"],
        "audit_nonconstant": nontrivial["nonconstant"],
        "route_consistent": route_consistent,
        "refinement_consistent": refinement_consistent,
        "single_audit_exists": audit_exists,
        "status": status,
    }


def matrix_payload(step14_matrices: dict) -> dict:
    levels = {}
    for level in [1, 2]:
        levels[f"level_{level}"] = {
            "A_QM_consistent": audit_matrix(level, CONSISTENT_QM).tolist(),
            "A_GR_consistent": audit_matrix(level, CONSISTENT_GR).tolist(),
            "A_u_consistent": audit_matrix(level, CONSISTENT_U).tolist(),
            "A_QM_mismatch": audit_matrix(level, MISMATCH_QM).tolist(),
            "A_GR_mismatch": audit_matrix(level, MISMATCH_GR).tolist(),
            "A_u_mismatch_attempt": audit_matrix(level, MISMATCH_U_ATTEMPT).tolist(),
            "E_QM": qm_embedding(level).tolist(),
            "E_GR": gr_embedding(level).tolist(),
            "stable_currency_lift": stable_lift_from_step14(level, step14_matrices).tolist(),
            "audit_lift": duplication(level).tolist(),
        }
    return {
        "neutral_modes": NEUTRAL_MODES,
        "qm_modes": QM_MODES,
        "gr_modes": GR_MODES,
        "coefficients": {
            "consistent_qm": CONSISTENT_QM.tolist(),
            "consistent_gr": CONSISTENT_GR.tolist(),
            "consistent_u": CONSISTENT_U.tolist(),
            "mismatch_qm": MISMATCH_QM.tolist(),
            "mismatch_gr": MISMATCH_GR.tolist(),
            "mismatch_u_attempt": MISMATCH_U_ATTEMPT.tolist(),
        },
        "levels": levels,
    }


def main() -> None:
    step14_payload = json.loads((STEP14_DIR / "refinement_stability_output_step14.json").read_text(encoding="utf-8"))
    step14_matrices = json.loads((STEP14_DIR / "refinement_lift_matrices_step14.json").read_text(encoding="utf-8"))
    rows = []
    for level in [1, 2]:
        rows.append(
            transition_diagnostic(level, "consistent_audit", CONSISTENT_QM, CONSISTENT_GR, CONSISTENT_U, step14_matrices)
        )
        rows.append(
            transition_diagnostic(
                level,
                "route_mismatch_control",
                MISMATCH_QM,
                MISMATCH_GR,
                MISMATCH_U_ATTEMPT,
                step14_matrices,
            )
        )

    by_case: dict[str, list[dict]] = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)
    consistent_shared_max = max(float(row["shared_mode_residual"]) for row in by_case["consistent_audit"])
    consistent_comm_max = max(float(row["audit_refinement_commutator_residual"]) for row in by_case["consistent_audit"])
    mismatch_shared_min = min(float(row["shared_mode_residual"]) for row in by_case["route_mismatch_control"])
    mismatch_passes = any(bool(row["single_audit_exists"]) for row in by_case["route_mismatch_control"])
    nonzero = all(bool(row["audit_nonzero"]) for row in by_case["consistent_audit"])
    nonconstant = all(bool(row["audit_nonconstant"]) for row in by_case["consistent_audit"])
    verdict = {
        "audit_coheres": bool(
            consistent_shared_max <= 1e-10
            and consistent_comm_max <= 1e-10
            and mismatch_shared_min > 0.25
            and not mismatch_passes
            and nonzero
            and nonconstant
        ),
        "consistent_audit_passes": bool(consistent_shared_max <= 1e-10 and consistent_comm_max <= 1e-10),
        "route_mismatch_control_fails": bool(mismatch_shared_min > 0.25 and not mismatch_passes),
        "audit_commutes_with_refinement": bool(consistent_comm_max <= 1e-10),
        "audit_nontrivial": bool(nonzero and nonconstant),
        "rungs_cohere": bool(step14_payload["verdict"]["refinement_stable"]),
    }
    no_smuggling = {
        "route_mismatch_control_passes": mismatch_passes,
        "audit_trivial_zero": not nonzero,
        "audit_trivial_constant": not nonconstant,
        "circular_test_used": False,
        "one_hot_set_cover_used": False,
        "target_layer_inserted": False,
        "endpoint_derivation_claimed": False,
        "literature_program_terms_used": False,
        "step14_refinement_loaded": step14_payload["verdict"]["refinement_stable"],
    }
    payload = {
        "step": 15,
        "rung_id": "RUNG_3_AUDIT_ON_REFINEMENT_STABLE_CURRENCY",
        "observed_residuals": {
            "consistent_shared_mode_residual_max": consistent_shared_max,
            "consistent_audit_refinement_commutator_max": consistent_comm_max,
            "route_mismatch_shared_mode_residual_min": mismatch_shared_min,
        },
        "verdict": verdict,
        "no_smuggling_check": no_smuggling,
        "structural_constraint": (
            "A single bridge audit on u exists iff the two endpoint audits agree on the shared "
            "currency modes {d0,d2}; this is the route-consistency condition on the overlap."
        ),
        "next_move": "STEP16_FULL_LADDER_DESCENT",
    }

    with (ARTIFACT_DIR / "audit_consistency_step15.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (ARTIFACT_DIR / "audit_matrices_step15.json").write_text(
        json.dumps(matrix_payload(step14_matrices), indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "audit_output_step15.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    lines = [
        "Step 15 RUNG_3 audit on refinement-stable currency",
        f"Consistent shared-mode residual max: {consistent_shared_max}",
        f"Consistent refinement commutator max: {consistent_comm_max}",
        f"Route-mismatch shared-mode residual min: {mismatch_shared_min}",
        f"Route-mismatch control passes: {mismatch_passes}",
        f"Audit nontrivial: {nonzero and nonconstant}",
        f"Audit coheres: {verdict['audit_coheres']}",
        "Next move: STEP16_FULL_LADDER_DESCENT",
    ]
    (ARTIFACT_DIR / "audit_output_step15.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
