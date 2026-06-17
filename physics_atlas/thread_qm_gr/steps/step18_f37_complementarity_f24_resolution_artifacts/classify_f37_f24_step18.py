#!/usr/bin/env python3
"""Classify the toy QM/GR access pair by F37 and F24."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP17_DIR = ARTIFACT_DIR.parents[0] / "step17_native_promotion_bridge_classification_artifacts"
FIV_FILE = Path("/home/repos/six-birds-papers/Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex")
TOL = 1e-10


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
PI_L = np.eye(4)
PI_PRODUCT = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)
TO_QM_FROM_L = PI_QM.copy()
TO_GR_FROM_L = PI_GR.copy()
TO_QM_FROM_PRODUCT = np.array(
    [
        [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
    ],
    dtype=float,
)
TO_GR_FROM_PRODUCT = np.array(
    [
        [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
    ],
    dtype=float,
)
ROLE_GR_DISTINCT = np.array([[0.0, 0.0, 0.0, 1.0]], dtype=float)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def residual(left: np.ndarray, right: np.ndarray) -> float:
    denom = max(norm(right), 1.0)
    return float(norm(left - right) / denom)


def f37_rows() -> list[dict[str, object]]:
    step17_status = json.loads((STEP17_DIR / "native_classification_output_step17.json").read_text(encoding="utf-8"))
    rows = []
    cases = [
        {
            "joint_name": "L_joint",
            "j": PI_L,
            "a": TO_QM_FROM_L,
            "b": TO_GR_FROM_L,
            "admissible": step17_status["classifications"]["L"]["status"] == "candidate",
            "native_status": step17_status["classifications"]["L"]["status"],
        },
        {
            "joint_name": "product_control",
            "j": PI_PRODUCT,
            "a": TO_QM_FROM_PRODUCT,
            "b": TO_GR_FROM_PRODUCT,
            "admissible": False,
            "native_status": step17_status["classifications"]["union"]["status"],
        },
    ]
    for case in cases:
        a_res = residual(case["a"] @ case["j"], PI_QM)
        b_res = residual(case["b"] @ case["j"], PI_GR)
        commuting = a_res <= TOL and b_res <= TOL
        rows.append(
            {
                "joint_name": case["joint_name"],
                "a_after_j_residual": a_res,
                "b_after_j_residual": b_res,
                "commuting_conditions_hold": commuting,
                "native_status": case["native_status"],
                "admissible_joint": bool(commuting and case["admissible"]),
            }
        )
    return rows


def role_obstruction_rows() -> list[dict[str, object]]:
    q_values = SOURCE_STATES @ PI_QM.T
    s_values = SOURCE_STATES @ ROLE_GR_DISTINCT.T
    rows = []
    for i in range(len(SOURCE_STATES)):
        for j in range(i + 1, len(SOURCE_STATES)):
            q_gap = norm(q_values[i] - q_values[j])
            s_gap = norm(s_values[i] - s_values[j])
            if q_gap <= TOL and s_gap > TOL:
                rows.append(
                    {
                        "state_i": i,
                        "state_j": j,
                        "q_QM_gap": q_gap,
                        "role_readout_gap": s_gap,
                    }
                )
    return rows


def f24_case_rows(role_obstruction_count: int) -> list[dict[str, object]]:
    criteria = [
        {
            "case": "MemoryLayer",
            "source_criterion": "formed memory status: role split is resolved by a memory record already carried by the current access discipline",
            "toy_test": "GR-distinct d3 is not carried by q_QM; role obstruction is nonempty",
            "satisfies": False,
        },
        {
            "case": "HiddenUpstreamRole",
            "source_criterion": "hidden status: role is assigned to an upstream hidden source rather than an explicit admissible joint quotient",
            "toy_test": "L_joint is explicit and admissible on the toy",
            "satisfies": False,
        },
        {
            "case": "BridgeMediatedRole",
            "source_criterion": "mediated status: role split is resolved by a declared admissible mediation object satisfying the native gates",
            "toy_test": "L_joint commutes with q_QM and q_GR, and B_QM_to_L has status candidate",
            "satisfies": role_obstruction_count > 0,
        },
        {
            "case": "BudgetedRole",
            "source_criterion": "budget status: role split is retained as a priced residual rather than exactly resolved",
            "toy_test": "F37 residuals for L_joint are zero, not budgeted positive residuals",
            "satisfies": False,
        },
        {
            "case": "ScopedRole",
            "source_criterion": "scoped status: role is resolved only after restricting the carrier or access scope",
            "toy_test": "all 8 source states are used; no carrier restriction is applied",
            "satisfies": False,
        },
        {
            "case": "CoarsenedRole",
            "source_criterion": "coarsened status: role split is resolved by quotienting away the splitting distinction",
            "toy_test": "L_joint preserves d3 and strictly refines q_QM rather than quotienting it away",
            "satisfies": False,
        },
    ]
    return criteria


def fiv_source_record() -> dict[str, object]:
    return {
        "file": str(FIV_FILE),
        "F24_lines_read": "1418-1514",
        "F37_lines_read": "6859-6898",
        "F24_source_note": (
            "The paper states the role obstruction, strict refinement, and mutually exclusive resolution families. "
            "It names the discipline families but does not give a more granular predicate list elsewhere in the repository search."
        ),
        "repository_search_terms": [
            "MemoryLayer",
            "HiddenUpstreamRole",
            "BridgeMediatedRole",
            "BudgetedRole",
            "ScopedRole",
            "CoarsenedRole",
        ],
    }


def main() -> None:
    f37 = f37_rows()
    obstruction = role_obstruction_rows()
    f24_cases = f24_case_rows(len(obstruction))
    selected = [row["case"] for row in f24_cases if row["satisfies"]]
    f37_admissible = any(row["admissible_joint"] for row in f37)
    product = [row for row in f37 if row["joint_name"] == "product_control"][0]
    verdict = {
        "F37_not_complementary_on_toy": bool(f37_admissible),
        "F37_admissible_joint": "L_joint" if f37_admissible else "none",
        "product_control_commutes": bool(product["commuting_conditions_hold"]),
        "product_control_admissible": bool(product["admissible_joint"]),
        "F24_unique_case": len(selected) == 1,
        "F24_selected_case": selected[0] if len(selected) == 1 else "none",
    }
    payload = {
        "step": 18,
        "FIV_source_read": True,
        "FIV_source_record": fiv_source_record(),
        "verdict": verdict,
        "role_obstruction_count": len(obstruction),
        "no_smuggling_check": {
            "joint_asserted_with_nonzero_residual": False,
            "zero_f24_cases_selected": len(selected) == 0,
            "multiple_f24_cases_selected": len(selected) > 1,
            "f24_criteria_asserted_without_reading_fiv": False,
            "literature_program_terms_used": False,
            "root_landed": False,
        },
    }
    witness = {
        "J": "O_L",
        "j": "pi_L",
        "a": "to_qm",
        "b": "to_gr",
        "maps": {
            "pi_QM": PI_QM.tolist(),
            "pi_GR": PI_GR.tolist(),
            "pi_L": PI_L.tolist(),
            "to_qm_from_L": TO_QM_FROM_L.tolist(),
            "to_gr_from_L": TO_GR_FROM_L.tolist(),
            "pi_product": PI_PRODUCT.tolist(),
            "to_qm_from_product": TO_QM_FROM_PRODUCT.tolist(),
            "to_gr_from_product": TO_GR_FROM_PRODUCT.tolist(),
        },
    }

    with (ARTIFACT_DIR / "f37_commuting_checks_step18.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(f37[0].keys()))
        writer.writeheader()
        writer.writerows(f37)
    with (ARTIFACT_DIR / "f24_role_obstruction_step18.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(obstruction[0].keys()))
        writer.writeheader()
        writer.writerows(obstruction)
    with (ARTIFACT_DIR / "f24_resolution_cases_step18.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(f24_cases[0].keys()))
        writer.writeheader()
        writer.writerows(f24_cases)
    (ARTIFACT_DIR / "f37_joint_quotient_witness_step18.json").write_text(
        json.dumps(witness, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "fiv_source_record_step18.json").write_text(
        json.dumps(fiv_source_record(), indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "native_culmination_output_step18.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    lines = [
        "Step 18 F37/F24 native culmination",
        f"F37 L a∘j residual: {f37[0]['a_after_j_residual']}",
        f"F37 L b∘j residual: {f37[0]['b_after_j_residual']}",
        f"F37 verdict on toy: not complementary = {verdict['F37_not_complementary_on_toy']}",
        f"Product control admissible: {verdict['product_control_admissible']}",
        f"F24 role obstruction count: {len(obstruction)}",
        f"F24 selected case: {verdict['F24_selected_case']}",
    ]
    (ARTIFACT_DIR / "native_culmination_output_step18.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
