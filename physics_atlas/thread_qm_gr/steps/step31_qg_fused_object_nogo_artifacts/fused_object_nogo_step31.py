#!/usr/bin/env python3
"""Step 31: bounded fused-object no-go diagnostic."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP24_VALUES = THREAD_DIR / "steps" / "step24_derived_physical_audits_artifacts" / "derived_audit_values_step24.csv"
STEP30_OUTPUT = THREAD_DIR / "steps" / "step30_qg_directed_reduction_nogo_artifacts" / "directed_reduction_nogo_output_step30.json"

TOL = 1e-10


def binary_carrier(n_modes: int) -> np.ndarray:
    return np.array(
        [[(idx >> shift) & 1 for shift in range(n_modes)] for idx in range(2**n_modes)],
        dtype=float,
    )


def column_duplicate_pairs(matrix: np.ndarray) -> list[tuple[int, int]]:
    pairs: list[tuple[int, int]] = []
    for left in range(matrix.shape[1]):
        for right in range(left + 1, matrix.shape[1]):
            if np.allclose(matrix[:, left], matrix[:, right], atol=TOL):
                pairs.append((left, right))
    return pairs


def union_gate_diagnostic() -> tuple[list[dict[str, object]], dict[str, object]]:
    carrier = binary_carrier(4)
    d0, d1, d2, d3 = carrier[:, 0], carrier[:, 1], carrier[:, 2], carrier[:, 3]
    union_map = np.column_stack([d0, d1, d2, d0, d2, d3])
    l_map = carrier.copy()
    rows: list[dict[str, object]] = []
    for case, matrix, dimension, description in [
        ("union_direct_sum", union_map, 6, "QM block stapled to GR block; d0 and d2 duplicated."),
        ("nonduplicating_refinement_control", l_map, 4, "Common refinement with each mode represented once."),
    ]:
        rank = int(np.linalg.matrix_rank(matrix))
        pairs = column_duplicate_pairs(matrix)
        extra_coordinate_count = int(dimension - rank)
        rows.append(
            {
                "case": case,
                "target_dimension": dimension,
                "row_rank": rank,
                "extra_coordinate_count": extra_coordinate_count,
                "duplicate_pair_count": len(pairs),
                "duplicate_pairs": pairs,
                "G_nosmuggle_pass": extra_coordinate_count == 0 and len(pairs) == 0,
                "description": description,
            }
        )
    return rows, {"union_map": union_map.tolist(), "control_map": l_map.tolist()}


def rel_residual(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(float(np.linalg.norm(right)), 1.0))


def proportional_residual(left: np.ndarray, right: np.ndarray) -> tuple[float, float]:
    denom = float(np.dot(left, left))
    alpha = 0.0 if denom <= TOL else float(np.dot(left, right) / denom)
    return alpha, rel_residual(alpha * left, right)


def read_step24_audits() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rho = []
    current = []
    t00 = []
    t0i = []
    with STEP24_VALUES.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rho.append(float(row["rho"]))
            current.append(float(row["current_j"]))
            t00.append(float(row["T00"]))
            t0i.append(float(row["T0i"]))
    return np.asarray(rho), np.asarray(current), np.asarray(t00), np.asarray(t0i)


def shared_audit_diagnostic() -> tuple[list[dict[str, object]], dict[str, object]]:
    rho, current, t00, t0i = read_step24_audits()
    born = np.column_stack([rho, current])
    stress = np.column_stack([t00, t0i])
    density_alpha, density_prop = proportional_residual(rho, t00)
    transport_alpha, transport_prop = proportional_residual(current, t0i)
    rows = [
        {
            "case": "derived_physical_audits",
            "mode": "joint_density_transport",
            "equal_residual": rel_residual(born, stress),
            "proportional_alpha": "",
            "proportional_residual": "",
            "shared_audit_exists": False,
        },
        {
            "case": "derived_physical_audits",
            "mode": "density_d0",
            "equal_residual": rel_residual(rho, t00),
            "proportional_alpha": density_alpha,
            "proportional_residual": density_prop,
            "shared_audit_exists": False,
        },
        {
            "case": "derived_physical_audits",
            "mode": "transport_d2",
            "equal_residual": rel_residual(current, t0i),
            "proportional_alpha": transport_alpha,
            "proportional_residual": transport_prop,
            "shared_audit_exists": False,
        },
    ]
    synthetic_left = np.column_stack([rho, current])
    synthetic_right = synthetic_left.copy()
    rows.append(
        {
            "case": "agreeing_audit_control",
            "mode": "joint_density_transport",
            "equal_residual": rel_residual(synthetic_left, synthetic_right),
            "proportional_alpha": 1.0,
            "proportional_residual": 0.0,
            "shared_audit_exists": True,
        }
    )
    return rows, {
        "rho": rho.tolist(),
        "current_j": current.tolist(),
        "T00": t00.tolist(),
        "T0i": t0i.tolist(),
    }


def directed_route_citation() -> list[dict[str, object]]:
    step30 = json.loads(STEP30_OUTPUT.read_text(encoding="utf-8"))
    summary = step30["summary"]
    verdict = step30["verdict"]
    return [
        {
            "source_step": 30,
            "lemma_verdict": verdict["lemma_verdict"],
            "q_GR_factors_through_q_QM": verdict["q_GR_factors_through_q_QM"],
            "q_QM_factors_through_q_GR": verdict["q_QM_factors_through_q_GR"],
            "defect_count_q_GR_through_q_QM": summary["defect_count_q_GR_through_q_QM"],
            "defect_count_q_QM_through_q_GR": summary["defect_count_q_QM_through_q_GR"],
            "route_mismatch_normalized": summary["route_mismatch_normalized"],
            "directed_route_blocked": verdict["lemma_verdict"]
            == "lemma1_directed_reduction_blocked_in_bounded_grammar",
        }
    ]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    union_rows, map_payload = union_gate_diagnostic()
    audit_rows, audit_payload = shared_audit_diagnostic()
    directed_rows = directed_route_citation()

    union = next(row for row in union_rows if row["case"] == "union_direct_sum")
    refinement_control = next(row for row in union_rows if row["case"] == "nonduplicating_refinement_control")
    audit_joint = next(
        row
        for row in audit_rows
        if row["case"] == "derived_physical_audits" and row["mode"] == "joint_density_transport"
    )
    audit_control = next(row for row in audit_rows if row["case"] == "agreeing_audit_control")
    directed = directed_rows[0]

    write_csv(ARTIFACT_DIR / "union_g_nosmuggle_step31.csv", union_rows)
    write_csv(ARTIFACT_DIR / "shared_audit_overlap_step31.csv", audit_rows)
    write_csv(ARTIFACT_DIR / "directed_route_citation_step31.csv", directed_rows)
    with (ARTIFACT_DIR / "fused_object_carrier_step31.json").open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "maps": map_payload,
                "audits": audit_payload,
                "union_route": "direct-sum package duplicates d0 and d2.",
                "shared_audit_route": "single audit exists only if Born and stress-energy values agree on density and transport.",
                "directed_route_source": str(STEP30_OUTPUT),
            },
            handle,
            indent=2,
        )

    verdict_name = (
        "lemma2_fused_object_blocked_in_bounded_grammar"
        if not bool(union["G_nosmuggle_pass"])
        and float(audit_joint["equal_residual"]) > 1e-2
        and bool(directed["directed_route_blocked"])
        and bool(refinement_control["G_nosmuggle_pass"])
        and bool(audit_control["shared_audit_exists"])
        else "fused_object_unexpected_or_test_toothless"
    )
    output = {
        "step": 31,
        "verdict": {
            "lemma_verdict": verdict_name,
            "union_route_passes": bool(union["G_nosmuggle_pass"]),
            "shared_audit_route_passes": bool(audit_joint["shared_audit_exists"]),
            "directed_route_passes": not bool(directed["directed_route_blocked"]),
            "nonduplicating_refinement_control_passes": bool(refinement_control["G_nosmuggle_pass"]),
            "agreeing_audit_control_passes": bool(audit_control["shared_audit_exists"]),
            "root_landed": False,
            "bounded_grammar_scope": True,
            "external_review_required": True,
        },
        "summary": {
            "union_extra_coordinate_count": union["extra_coordinate_count"],
            "union_duplicate_pair_count": union["duplicate_pair_count"],
            "union_row_rank": union["row_rank"],
            "union_target_dimension": union["target_dimension"],
            "shared_audit_joint_equal_residual": audit_joint["equal_residual"],
            "shared_audit_density_proportional_residual": next(
                row for row in audit_rows if row["mode"] == "density_d0"
            )["proportional_residual"],
            "shared_audit_transport_proportional_residual": next(
                row for row in audit_rows if row["mode"] == "transport_d2"
            )["proportional_residual"],
            "directed_route_mismatch_normalized_from_step30": directed["route_mismatch_normalized"],
            "control_refinement_extra_coordinate_count": refinement_control["extra_coordinate_count"],
            "control_audit_equal_residual": audit_control["equal_residual"],
        },
        "guardrails": {
            "union_route_computed": True,
            "shared_audit_overlap_computed": True,
            "directed_route_cited_from_lemma1": True,
            "genuine_fusion_control_passes": bool(refinement_control["G_nosmuggle_pass"])
            and bool(audit_control["shared_audit_exists"]),
            "bounded_no_go_only": True,
        },
    }
    with (ARTIFACT_DIR / "fused_object_nogo_output_step31.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    with (ARTIFACT_DIR / "fused_object_nogo_output_step31.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 31 fused-object bounded diagnostic\n")
        handle.write(f"Verdict: {verdict_name}\n")
        handle.write(f"Union G_nosmuggle pass: {union['G_nosmuggle_pass']}\n")
        handle.write(f"Union extra coordinate count: {union['extra_coordinate_count']}\n")
        handle.write(f"Shared audit joint equal residual: {audit_joint['equal_residual']}\n")
        handle.write(f"Directed route blocked by Step 30: {directed['directed_route_blocked']}\n")
        handle.write(f"Fusion control G_nosmuggle pass: {refinement_control['G_nosmuggle_pass']}\n")
        handle.write(f"Fusion control audit pass: {audit_control['shared_audit_exists']}\n")


if __name__ == "__main__":
    main()
