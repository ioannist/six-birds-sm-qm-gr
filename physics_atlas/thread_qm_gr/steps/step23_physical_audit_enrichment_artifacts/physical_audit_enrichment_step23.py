#!/usr/bin/env python3
"""Enrich F51 descent statuses with physical-signature quadratic audits."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
TOL = 1e-10

MODES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]
QM_MODE_INDICES = [0, 1, 2]
GR_MODE_INDICES = [0, 2, 3]
QM_SHARED_INDICES = [0, 2]  # d0,d2 inside A_QM
GR_SHARED_INDICES = [0, 1]  # d0,d2 inside A_GR


def complete_mode_carrier() -> np.ndarray:
    return np.array(list(itertools.product([0.0, 1.0], repeat=4)), dtype=float)


CARRIER = complete_mode_carrier()

# Born-like probability/amplitude-square signature on (d0,d1,d2).
A_QM = np.array(
    [
        [1.20, 0.15, 0.20],
        [0.15, 0.80, -0.10],
        [0.20, -0.10, 1.10],
    ],
    dtype=float,
)

# Curvature/geodesic-transport signature on (d0,d2,d3), sharing the d0,d2 block.
A_GR = np.array(
    [
        [1.20, 0.20, 0.05],
        [0.20, 1.10, -0.30],
        [0.05, -0.30, 0.60],
    ],
    dtype=float,
)

# Same physical roles, but incompatible shared d0,d2 block.
A_GR_INCOMPATIBLE = np.array(
    [
        [1.45, 0.05, 0.05],
        [0.05, 0.90, -0.30],
        [0.05, -0.30, 0.60],
    ],
    dtype=float,
)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def residual(left: np.ndarray, right: np.ndarray) -> float:
    return float(norm(left - right) / max(norm(right), 1.0))


def is_symmetric(matrix: np.ndarray) -> bool:
    return residual(matrix, matrix.T) <= TOL


def eigenvalues(matrix: np.ndarray) -> list[float]:
    return [float(value) for value in np.linalg.eigvalsh(matrix)]


def is_psd(matrix: np.ndarray) -> bool:
    return min(eigenvalues(matrix)) >= -TOL


def shared_block_qm(matrix: np.ndarray) -> np.ndarray:
    return matrix[np.ix_(QM_SHARED_INDICES, QM_SHARED_INDICES)]


def shared_block_gr(matrix: np.ndarray) -> np.ndarray:
    return matrix[np.ix_(GR_SHARED_INDICES, GR_SHARED_INDICES)]


def parent_form(gr_form: np.ndarray) -> np.ndarray | None:
    if residual(shared_block_qm(A_QM), shared_block_gr(gr_form)) > TOL:
        return None
    parent = np.zeros((4, 4), dtype=float)
    parent[np.ix_(QM_MODE_INDICES, QM_MODE_INDICES)] = A_QM
    parent[np.ix_(GR_MODE_INDICES, GR_MODE_INDICES)] = gr_form
    parent[1, 3] = 0.0
    parent[3, 1] = 0.0
    return parent


def restrict_parent(parent: np.ndarray, modes: list[int]) -> np.ndarray:
    return parent[np.ix_(modes, modes)]


def quadratic_values(form: np.ndarray, modes: list[int]) -> np.ndarray:
    sub = CARRIER[:, modes]
    return np.einsum("bi,ij,bj->b", sub, form, sub)


def reconciliation_row(case: str, gr_form: np.ndarray) -> dict[str, object]:
    shared_res = residual(shared_block_qm(A_QM), shared_block_gr(gr_form))
    parent = parent_form(gr_form)
    if parent is None:
        qm_restriction_res = 1.0
        gr_restriction_res = 1.0
        sample_qm_res = 1.0
        sample_gr_res = 1.0
        parent_exists = False
    else:
        qm_restriction_res = residual(restrict_parent(parent, QM_MODE_INDICES), A_QM)
        gr_restriction_res = residual(restrict_parent(parent, GR_MODE_INDICES), gr_form)
        sample_qm_res = residual(
            quadratic_values(restrict_parent(parent, QM_MODE_INDICES), QM_MODE_INDICES),
            quadratic_values(A_QM, QM_MODE_INDICES),
        )
        sample_gr_res = residual(
            quadratic_values(restrict_parent(parent, GR_MODE_INDICES), GR_MODE_INDICES),
            quadratic_values(gr_form, GR_MODE_INDICES),
        )
        parent_exists = True
    status_compatible = (
        parent_exists
        and shared_res <= TOL
        and qm_restriction_res <= TOL
        and gr_restriction_res <= TOL
        and sample_qm_res <= TOL
        and sample_gr_res <= TOL
    )
    return {
        "case": case,
        "shared_subblock_residual": shared_res,
        "parent_quadratic_audit_exists": parent_exists,
        "parent_restricts_to_qm_residual": qm_restriction_res,
        "parent_restricts_to_gr_residual": gr_restriction_res,
        "qm_quadratic_value_residual": sample_qm_res,
        "gr_quadratic_value_residual": sample_gr_res,
        "f51_status_compatible": status_compatible,
    }


def matrix_properties_rows() -> list[dict[str, object]]:
    rows = []
    for name, matrix, motivation in [
        (
            "A_QM_Born_quadratic",
            A_QM,
            "Born-like probability signature: positive quadratic amplitude-square form on d0,d1,d2.",
        ),
        (
            "A_GR_curvature_quadratic",
            A_GR,
            "Curvature/geodesic-transport signature: symmetric quadratic form on density, transport, curvature modes.",
        ),
        (
            "A_GR_incompatible_control",
            A_GR_INCOMPATIBLE,
            "Curvature-like control with mismatched shared d0,d2 block.",
        ),
    ]:
        rows.append(
            {
                "audit": name,
                "dimension": matrix.shape[0],
                "symmetric": is_symmetric(matrix),
                "positive_semidefinite": is_psd(matrix),
                "eigenvalues": ";".join(f"{value:.12g}" for value in eigenvalues(matrix)),
                "motivation": motivation,
            }
        )
    return rows


def output_payload() -> dict[str, object]:
    compatible = reconciliation_row("L_physical_quadratic_audits", A_GR)
    incompatible = reconciliation_row("incompatible_physical_control", A_GR_INCOMPATIBLE)
    return {
        "step": 23,
        "verdict": {
            "physical_audit_verdict": "survives_physical_signature_enrichment"
            if compatible["f51_status_compatible"]
            else "content_specific_obstruction",
            "L_physical_audits_compatible": bool(compatible["f51_status_compatible"]),
            "incompatible_control_pass": bool(incompatible["f51_status_compatible"]),
        },
        "guardrails": {
            "quadratic_forms_used": True,
            "qm_form_psd": is_psd(A_QM),
            "subblock_residual_computed": True,
            "root_landed": False,
        },
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    compatible_parent = parent_form(A_GR)
    incompatible_parent = parent_form(A_GR_INCOMPATIBLE)
    matrices = {
        "modes": MODES,
        "qm_modes": ["d0_density", "d1_phase", "d2_transport"],
        "gr_modes": ["d0_density", "d2_transport", "d3_curvature"],
        "shared_modes": ["d0_density", "d2_transport"],
        "A_QM_Born_quadratic": A_QM.tolist(),
        "A_GR_curvature_quadratic": A_GR.tolist(),
        "A_GR_incompatible_control": A_GR_INCOMPATIBLE.tolist(),
        "A_L_parent_quadratic": None if compatible_parent is None else compatible_parent.tolist(),
        "A_L_incompatible_parent": None if incompatible_parent is None else incompatible_parent.tolist(),
    }
    with (ARTIFACT_DIR / "physical_audit_matrices_step23.json").open("w", encoding="utf-8") as handle:
        json.dump(matrices, handle, indent=2)
    write_csv(ARTIFACT_DIR / "quadratic_audit_properties_step23.csv", matrix_properties_rows())
    write_csv(
        ARTIFACT_DIR / "parent_audit_reconciliation_step23.csv",
        [
            reconciliation_row("L_physical_quadratic_audits", A_GR),
            reconciliation_row("incompatible_physical_control", A_GR_INCOMPATIBLE),
        ],
    )
    write_csv(
        ARTIFACT_DIR / "physical_f51_status_step23.csv",
        [
            {
                "case": row["case"],
                "f51_status_compatible": row["f51_status_compatible"],
                "shared_subblock_residual": row["shared_subblock_residual"],
                "parent_quadratic_audit_exists": row["parent_quadratic_audit_exists"],
            }
            for row in [
                reconciliation_row("L_physical_quadratic_audits", A_GR),
                reconciliation_row("incompatible_physical_control", A_GR_INCOMPATIBLE),
            ]
        ],
    )
    payload = output_payload()
    with (ARTIFACT_DIR / "physical_audit_output_step23.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    with (ARTIFACT_DIR / "physical_audit_output_step23.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 23 physical quadratic audit enrichment\n")
        handle.write(f"Verdict: {payload['verdict']['physical_audit_verdict']}\n")
        handle.write(f"L compatible: {payload['verdict']['L_physical_audits_compatible']}\n")
        handle.write(f"Incompatible control pass: {payload['verdict']['incompatible_control_pass']}\n")


if __name__ == "__main__":
    main()
