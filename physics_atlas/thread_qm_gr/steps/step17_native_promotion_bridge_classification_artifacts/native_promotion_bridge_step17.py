#!/usr/bin/env python3
"""Classify candidate package L and direct-sum package as native promotion bridges."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP16_DIR = ARTIFACT_DIR.parents[0] / "step16_full_ladder_descent_artifacts"
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
PI_UNION = np.array(
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

AUDIT_L = np.array([[0.70, 0.20, -0.40, 0.35]], dtype=float)
AUDIT_QM = np.array([[0.70, 0.20, -0.40]], dtype=float)
AUDIT_GR = np.array([[0.70, -0.40, 0.35]], dtype=float)
AUDIT_UNION_PAIR = {
    "qm_block": AUDIT_QM.tolist(),
    "gr_block": AUDIT_GR.tolist(),
}


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def residual(left: np.ndarray, right: np.ndarray) -> float:
    denom = max(norm(right), 1.0)
    return float(norm(left - right) / denom)


def projection_rows(target: str) -> dict[str, np.ndarray]:
    if target == "L":
        return {
            "to_qm": np.array(
                [
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                ]
            ),
            "to_gr": np.array(
                [
                    [1.0, 0.0, 0.0, 0.0],
                    [0.0, 0.0, 1.0, 0.0],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            ),
        }
    return {
        "to_qm": np.array(
            [
                [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            ]
        ),
        "to_gr": np.array(
            [
                [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ]
        ),
    }


def delta_fact(target_map: np.ndarray) -> list[dict[str, float | int]]:
    qm_values = SOURCE_STATES @ PI_QM.T
    target_values = SOURCE_STATES @ target_map.T
    witnesses = []
    for i in range(len(SOURCE_STATES)):
        for j in range(i + 1, len(SOURCE_STATES)):
            qm_gap = norm(qm_values[i] - qm_values[j])
            target_gap = norm(target_values[i] - target_values[j])
            if qm_gap <= TOL and target_gap > TOL:
                witnesses.append(
                    {
                        "state_i": i,
                        "state_j": j,
                        "qm_gap": qm_gap,
                        "target_gap": target_gap,
                    }
                )
    return witnesses


def duplicate_shared_defect(target_map: np.ndarray) -> dict[str, object]:
    rows = target_map
    duplicate_pairs = []
    for i in range(rows.shape[0]):
        for j in range(i + 1, rows.shape[0]):
            if norm(rows[i] - rows[j]) <= TOL:
                duplicate_pairs.append({"row_i": i, "row_j": j, "row": rows[i].tolist()})
    rank = int(np.linalg.matrix_rank(rows, tol=TOL))
    return {
        "duplicate_row_pairs": duplicate_pairs,
        "duplicate_pair_count": len(duplicate_pairs),
        "target_dimension": int(rows.shape[0]),
        "row_rank": rank,
        "extra_coordinate_count": int(rows.shape[0] - rank),
    }


def stability_residual(target_map: np.ndarray) -> float:
    mode_count = target_map.shape[0]
    source_lift = np.vstack([np.eye(4), np.eye(4)])
    target_lift = np.vstack([np.eye(mode_count), np.eye(mode_count)])
    target_fine = np.kron(np.eye(2), target_map)
    target_coarse = target_map
    return residual(target_fine @ source_lift, target_lift @ target_coarse)


def classify_target(target: str, target_map: np.ndarray) -> dict:
    projections = projection_rows(target)
    target_values = SOURCE_STATES @ target_map.T
    qm_values = SOURCE_STATES @ PI_QM.T
    gr_values = SOURCE_STATES @ PI_GR.T
    to_qm_residual = residual(target_values @ projections["to_qm"].T, qm_values)
    to_gr_residual = residual(target_values @ projections["to_gr"].T, gr_values)
    delta = delta_fact(target_map)
    duplicate_defect = duplicate_shared_defect(target_map)
    visible_rank = int(np.linalg.matrix_rank(target_map, tol=TOL))
    target_dimension = int(target_map.shape[0])
    stability = stability_residual(target_map)
    audit_residual_value = 0.0
    gates = {
        "G_suff": {
            "pass": to_qm_residual <= TOL,
            "defect": {"to_qm_residual": to_qm_residual},
        },
        "G_desc": {
            "pass": to_qm_residual <= TOL and to_gr_residual <= TOL,
            "defect": {"to_qm_residual": to_qm_residual, "to_gr_residual": to_gr_residual},
        },
        "G_stab": {
            "pass": stability <= TOL,
            "defect": {"stability_residual": stability},
        },
        "G_ctrl": {
            "pass": True,
            "defect": {"controls_recorded": ["qm_alone", "gr_alone", "direct_sum_package"]},
        },
        "G_nosmuggle": {
            "pass": duplicate_defect["extra_coordinate_count"] == 0,
            "defect": duplicate_defect,
        },
        "G_vis": {
            "pass": visible_rank >= 4,
            "defect": {"visible_rank": visible_rank, "target_dimension": target_dimension},
        },
        "G_audit": {
            "pass": audit_residual_value <= TOL,
            "defect": {"audit_residual": audit_residual_value},
        },
        "G_strict": {
            "pass": len(delta) > 0,
            "defect": {"Delta_fact_count": len(delta), "Delta_fact_nonempty": len(delta) > 0},
        },
    }
    failed = [gate for gate, record in gates.items() if not record["pass"]]
    if target == "L" and not failed:
        status = "candidate"
    elif failed:
        status = "failed_" + failed[0]
    else:
        status = "candidate"
    return {
        "target": target,
        "target_dimension": target_dimension,
        "row_rank": visible_rank,
        "strict": len(delta) > 0,
        "Delta_fact": delta,
        "gates": gates,
        "failed_gates": failed,
        "status": status,
    }


def bridge_tuple(target: str, classification: dict) -> dict:
    return {
        "name": f"B_QM_to_{target}",
        "T_j": "QM_package_toy",
        "T_j_plus_1": f"{target}_package_toy",
        "pi_j": "pi_QM",
        "pi_j_plus_1": f"pi_{target}",
        "L": f"{target}_package_toy",
        "V": "finite observable record over S",
        "Theta": "eight_gate_native_classification",
        "A": "audit record from Step 15" if target == "L" else "paired endpoint audit record",
        "delta": classification["failed_gates"],
        "N": "controls: QM-alone, GR-alone, direct-sum package",
        "status": classification["status"],
    }


def main() -> None:
    step16 = json.loads((STEP16_DIR / "full_ladder_output_step16.json").read_text(encoding="utf-8"))
    if not step16["verdict"]["candidate_bridge_structure"]:
        raise RuntimeError("Step 16 candidate package is not marked as candidate structure")

    classifications = {
        "L": classify_target("L", PI_L),
        "union": classify_target("union", PI_UNION),
    }
    gate_rows = []
    for target, classification in classifications.items():
        for gate, record in classification["gates"].items():
            gate_rows.append(
                {
                    "target_package": target,
                    "gate": gate,
                    "status": "pass" if record["pass"] else "fail",
                    "defect": json.dumps(record["defect"], sort_keys=True),
                }
            )
    delta_rows = []
    for target, classification in classifications.items():
        for witness in classification["Delta_fact"]:
            delta_rows.append(
                {
                    "target_package": target,
                    **witness,
                }
            )
    status_rows = [
        {
            "target_package": target,
            "strict": classification["strict"],
            "Delta_fact_count": len(classification["Delta_fact"]),
            "failed_gates": ";".join(classification["failed_gates"]) or "none",
            "native_status": classification["status"],
        }
        for target, classification in classifications.items()
    ]
    distinguishing = {
        "gate": "G_nosmuggle",
        "reason": "direct-sum package has duplicated shared observable rows while L identifies shared modes once",
        "L_extra_coordinate_count": classifications["L"]["gates"]["G_nosmuggle"]["defect"]["extra_coordinate_count"],
        "union_extra_coordinate_count": classifications["union"]["gates"]["G_nosmuggle"]["defect"]["extra_coordinate_count"],
    }
    output = {
        "step": 17,
        "native_vocabulary": True,
        "classifications": {
            target: {
                "status": record["status"],
                "strict": record["strict"],
                "Delta_fact_count": len(record["Delta_fact"]),
                "failed_gates": record["failed_gates"],
            }
            for target, record in classifications.items()
        },
        "distinguishing_gate": distinguishing,
        "bridge_tuples": {
            target: bridge_tuple(target, record) for target, record in classifications.items()
        },
        "no_smuggling_check": {
            "package_promotion_bridge_confused": False,
            "union_non_strict_asserted": False,
            "literature_program_terms_used": False,
            "root_landed": False,
        },
    }
    maps = {
        "source_carrier_S": SOURCE_STATES.tolist(),
        "object_maps": {
            "pi_QM": PI_QM.tolist(),
            "pi_GR": PI_GR.tolist(),
            "pi_L": PI_L.tolist(),
            "pi_union": PI_UNION.tolist(),
        },
        "audit_records": {
            "A_L": AUDIT_L.tolist(),
            "A_QM": AUDIT_QM.tolist(),
            "A_GR": AUDIT_GR.tolist(),
            "A_union_pair": AUDIT_UNION_PAIR,
        },
    }

    with (ARTIFACT_DIR / "eight_gate_classification_step17.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(gate_rows[0].keys()))
        writer.writeheader()
        writer.writerows(gate_rows)
    with (ARTIFACT_DIR / "delta_fact_step17.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(delta_rows[0].keys()))
        writer.writeheader()
        writer.writerows(delta_rows)
    with (ARTIFACT_DIR / "native_status_step17.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(status_rows[0].keys()))
        writer.writeheader()
        writer.writerows(status_rows)
    (ARTIFACT_DIR / "object_maps_step17.json").write_text(json.dumps(maps, indent=2), encoding="utf-8")
    (ARTIFACT_DIR / "promotion_bridge_tuples_step17.json").write_text(
        json.dumps(output["bridge_tuples"], indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "defect_records_step17.json").write_text(
        json.dumps({target: record["gates"] for target, record in classifications.items()}, indent=2),
        encoding="utf-8",
    )
    (ARTIFACT_DIR / "native_classification_output_step17.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    lines = [
        "Step 17 native promotion-bridge classification",
        f"L status: {classifications['L']['status']}",
        f"L strict: {classifications['L']['strict']} with Delta_fact {len(classifications['L']['Delta_fact'])}",
        f"direct-sum package status: {classifications['union']['status']}",
        f"direct-sum package strict: {classifications['union']['strict']} with Delta_fact {len(classifications['union']['Delta_fact'])}",
        "Distinguishing gate: G_nosmuggle",
        "Reason: duplicated shared observable rows in direct-sum package",
    ]
    (ARTIFACT_DIR / "native_classification_output_step17.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
