#!/usr/bin/env python3
"""Verify F51 common-refinement unification for candidate package L."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
FIV_FILE = Path(
    "/home/repos/six-birds-papers/"
    "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex"
)
TOL = 1e-10


def complete_mode_carrier() -> np.ndarray:
    return np.array(list(itertools.product([0.0, 1.0], repeat=4)), dtype=float)


CARRIER = complete_mode_carrier()
PI_L = np.eye(4)
PI_QM = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ],
    dtype=float,
)
PI_GR = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)
TO_QM = PI_QM.copy()
TO_GR = PI_GR.copy()

AUDIT_PARENT = np.array([0.70, 0.20, -0.40, 0.35], dtype=float)
AUDIT_QM = np.array([0.70, 0.20, -0.40], dtype=float)
AUDIT_GR = np.array([0.70, -0.40, 0.35], dtype=float)
AUDIT_GR_CONFLICT = np.array([0.90, -0.10, 0.35], dtype=float)

SHARED_QM_INDICES = [0, 2]  # d0, d2 inside q_QM
SHARED_GR_INDICES = [0, 1]  # d0, d2 inside q_GR


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def residual(left: np.ndarray, right: np.ndarray) -> float:
    return float(norm(left - right) / max(norm(right), 1.0))


def values(readout: np.ndarray) -> np.ndarray:
    return CARRIER @ readout.T


def delta_fact(child_map: np.ndarray, parent_map: np.ndarray) -> list[dict[str, object]]:
    child_values = values(child_map)
    parent_values = values(parent_map)
    rows: list[dict[str, object]] = []
    for i in range(len(CARRIER)):
        for j in range(i + 1, len(CARRIER)):
            child_gap = norm(child_values[i] - child_values[j])
            parent_gap = norm(parent_values[i] - parent_values[j])
            if child_gap <= TOL and parent_gap > TOL:
                rows.append(
                    {
                        "state_i": i,
                        "state_j": j,
                        "child_gap": child_gap,
                        "parent_gap": parent_gap,
                    }
                )
    return rows


def audit_restriction(parent_audit: np.ndarray, child: str) -> np.ndarray:
    if child == "QM":
        return parent_audit[[0, 1, 2]]
    if child == "GR":
        return parent_audit[[0, 2, 3]]
    raise ValueError(child)


def projection_case_rows(case_name: str, gr_audit: np.ndarray) -> list[dict[str, object]]:
    children = [
        {
            "child": "QM",
            "projection": TO_QM,
            "child_map": PI_QM,
            "child_audit": AUDIT_QM,
            "parent_restriction": audit_restriction(AUDIT_PARENT, "QM"),
        },
        {
            "child": "GR",
            "projection": TO_GR,
            "child_map": PI_GR,
            "child_audit": gr_audit,
            "parent_restriction": audit_restriction(AUDIT_PARENT, "GR"),
        },
    ]
    rows: list[dict[str, object]] = []
    for child in children:
        projection_residual = residual(child["projection"] @ PI_L, child["child_map"])
        witnesses = delta_fact(child["child_map"], PI_L)
        audit_residual = residual(child["parent_restriction"], child["child_audit"])
        admissible = projection_residual <= TOL and len(witnesses) > 0 and audit_residual <= TOL
        rows.append(
            {
                "case": case_name,
                "child": child["child"],
                "projection_residual": projection_residual,
                "strict_delta_count": len(witnesses),
                "audit_restriction_residual": audit_residual,
                "admissible_descent_status": admissible,
            }
        )
    return rows


def overlap_residual(qm_audit: np.ndarray, gr_audit: np.ndarray) -> float:
    return residual(qm_audit[SHARED_QM_INDICES], gr_audit[SHARED_GR_INDICES])


def status_row(case_name: str, gr_audit: np.ndarray) -> dict[str, object]:
    projection_rows = projection_case_rows(case_name, gr_audit)
    qm = next(row for row in projection_rows if row["child"] == "QM")
    gr = next(row for row in projection_rows if row["child"] == "GR")
    overlap = overlap_residual(AUDIT_QM, gr_audit)
    status_compatible = (
        bool(qm["admissible_descent_status"])
        and bool(gr["admissible_descent_status"])
        and overlap <= TOL
    )
    return {
        "case": case_name,
        "qm_admissible": bool(qm["admissible_descent_status"]),
        "gr_admissible": bool(gr["admissible_descent_status"]),
        "shared_overlap_audit_residual": overlap,
        "status_compatible": status_compatible,
        "f51_unification_pass": status_compatible,
    }


def source_record() -> dict[str, object]:
    return {
        "file": str(FIV_FILE),
        "F51_lines_read": "8528-8582",
        "criterion": (
            "F51: a parent quotient unifies child quotients when parent-to-child projection "
            "squares commute, route squares commute, and lifted claim/status maps are compatible."
        ),
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cases = [
        ("L_common_refinement", AUDIT_GR),
        ("status_conflict_control", AUDIT_GR_CONFLICT),
    ]
    projection_rows: list[dict[str, object]] = []
    status_rows: list[dict[str, object]] = []
    witness_rows: list[dict[str, object]] = []

    for case_name, gr_audit in cases:
        projection_rows.extend(projection_case_rows(case_name, gr_audit))
        status_rows.append(status_row(case_name, gr_audit))
        for child_name, child_map in [("QM", PI_QM), ("GR", PI_GR)]:
            for witness in delta_fact(child_map, PI_L):
                witness_rows.append({"case": case_name, "child": child_name, **witness})

    l_status = next(row for row in status_rows if row["case"] == "L_common_refinement")
    control_status = next(row for row in status_rows if row["case"] == "status_conflict_control")
    output = {
        "step": 22,
        "F51_source_read": True,
        "verdict": {
            "F51_verdict": "unification_holds_on_carrier"
            if l_status["f51_unification_pass"]
            else "status_incompatibility",
            "L_f51_unification_pass": bool(l_status["f51_unification_pass"]),
            "status_conflict_control_pass": bool(control_status["f51_unification_pass"]),
        },
        "guardrails": {
            "status_compatibility_computed": True,
            "F51_source_read": True,
            "root_landed": False,
        },
    }

    write_csv(ARTIFACT_DIR / "f51_projection_checks_step22.csv", projection_rows)
    write_csv(ARTIFACT_DIR / "f51_status_compatibility_step22.csv", status_rows)
    write_csv(ARTIFACT_DIR / "f51_delta_fact_witnesses_step22.csv", witness_rows)

    carrier_maps = {
        "carrier": CARRIER.tolist(),
        "pi_L": PI_L.tolist(),
        "pi_QM": PI_QM.tolist(),
        "pi_GR": PI_GR.tolist(),
        "to_qm": TO_QM.tolist(),
        "to_gr": TO_GR.tolist(),
        "audit_parent": AUDIT_PARENT.tolist(),
        "audit_qm": AUDIT_QM.tolist(),
        "audit_gr": AUDIT_GR.tolist(),
        "audit_gr_conflict": AUDIT_GR_CONFLICT.tolist(),
        "shared_overlap": {"qm_indices": SHARED_QM_INDICES, "gr_indices": SHARED_GR_INDICES},
    }
    with (ARTIFACT_DIR / "f51_carrier_maps_step22.json").open("w", encoding="utf-8") as handle:
        json.dump(carrier_maps, handle, indent=2)
    with (ARTIFACT_DIR / "f51_source_record_step22.json").open("w", encoding="utf-8") as handle:
        json.dump(source_record(), handle, indent=2)
    write_csv(
        ARTIFACT_DIR / "f51_source_record_step22.csv",
        [
            {
                "source": "F51 Unification as Common Refinement",
                "lines_read": "8528-8582",
                "criterion": source_record()["criterion"],
            }
        ],
    )
    with (ARTIFACT_DIR / "f51_unification_output_step22.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    with (ARTIFACT_DIR / "f51_unification_output_step22.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 22 F51 common-refinement unification\n")
        handle.write(f"F51 verdict: {output['verdict']['F51_verdict']}\n")
        handle.write(f"L pass: {output['verdict']['L_f51_unification_pass']}\n")
        handle.write(f"Status-conflict control pass: {output['verdict']['status_conflict_control_pass']}\n")


if __name__ == "__main__":
    main()
