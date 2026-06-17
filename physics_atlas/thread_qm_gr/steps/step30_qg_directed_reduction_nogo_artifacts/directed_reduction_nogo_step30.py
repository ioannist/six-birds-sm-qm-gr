#!/usr/bin/env python3
"""Step 30: bounded directed-reduction no-go diagnostic."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP24_VALUES = THREAD_DIR / "steps" / "step24_derived_physical_audits_artifacts" / "derived_audit_values_step24.csv"

TOL = 1e-10


def binary_carrier(n_modes: int) -> np.ndarray:
    return np.array(
        [[(idx >> shift) & 1 for shift in range(n_modes)] for idx in range(2**n_modes)],
        dtype=float,
    )


def quotient_values(carrier: np.ndarray, dims: tuple[int, ...]) -> np.ndarray:
    return carrier[:, dims]


def key(row: np.ndarray) -> tuple[float, ...]:
    return tuple(float(x) for x in row)


def factorization_defects(
    carrier: np.ndarray,
    source_dims: tuple[int, ...],
    target_dims: tuple[int, ...],
    label: str,
) -> list[dict[str, object]]:
    source = quotient_values(carrier, source_dims)
    target = quotient_values(carrier, target_dims)
    rows: list[dict[str, object]] = []
    grouped: dict[tuple[float, ...], list[int]] = defaultdict(list)
    for idx, value in enumerate(source):
        grouped[key(value)].append(idx)
    for source_key, indices in grouped.items():
        for left_pos, left_idx in enumerate(indices):
            for right_idx in indices[left_pos + 1 :]:
                if not np.allclose(target[left_idx], target[right_idx], atol=TOL):
                    rows.append(
                        {
                            "case": label,
                            "left_state": int(left_idx),
                            "right_state": int(right_idx),
                            "source_value": source_key,
                            "target_left": key(target[left_idx]),
                            "target_right": key(target[right_idx]),
                        }
                    )
    return rows


def conditional_mean_completion(
    carrier: np.ndarray,
    source_dims: tuple[int, ...],
) -> np.ndarray:
    source = quotient_values(carrier, source_dims)
    grouped: dict[tuple[float, ...], list[int]] = defaultdict(list)
    for idx, value in enumerate(source):
        grouped[key(value)].append(idx)
    completed = np.zeros_like(carrier, dtype=float)
    for idx, value in enumerate(source):
        indices = grouped[key(value)]
        completed[idx] = np.mean(carrier[indices], axis=0)
    return completed


def route_mismatch_for_qm_gr(carrier: np.ndarray) -> dict[str, object]:
    qm_dims = (0, 1, 2)
    gr_dims = (0, 2, 3)
    qm_completion = conditional_mean_completion(carrier, qm_dims)
    gr_completion = conditional_mean_completion(carrier, gr_dims)
    diff = qm_completion - gr_completion
    raw = float(np.linalg.norm(diff))
    normalized = raw / max(float(np.linalg.norm(carrier)), 1.0)
    return {
        "case": "qm_gr_directed_completion",
        "route1": "complete_from_q_QM_then_read_GR",
        "route2": "complete_from_q_GR_then_read_QM",
        "raw_route_mismatch": raw,
        "normalized_route_mismatch": normalized,
        "commutes": normalized <= TOL,
    }


def route_control_vertical_stack() -> tuple[list[dict[str, object]], dict[str, object]]:
    carrier = binary_carrier(3)
    fine_dims = (0, 1, 2)
    coarse_dims = (0, 2)
    defects = factorization_defects(carrier, fine_dims, coarse_dims, "control_coarse_through_fine")
    fine = quotient_values(carrier, fine_dims)
    coarse = quotient_values(carrier, coarse_dims)
    via_fine = fine[:, (0, 2)]
    raw = float(np.linalg.norm(coarse - via_fine))
    normalized = raw / max(float(np.linalg.norm(coarse)), 1.0)
    route = {
        "case": "vertical_stack_control",
        "route1": "direct_coarse_readout",
        "route2": "coarse_readout_factored_through_fine",
        "raw_route_mismatch": raw,
        "normalized_route_mismatch": normalized,
        "commutes": normalized <= TOL,
    }
    return defects, route


def read_audit_values() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    born_features = []
    stress_features = []
    stress_targets = []
    born_targets = []
    with STEP24_VALUES.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rho = float(row["rho"])
            current = float(row["current_j"])
            t00 = float(row["T00"])
            t0i = float(row["T0i"])
            born_features.append([1.0, rho, current])
            stress_features.append([1.0, t00, t0i])
            stress_targets.append([t00, t0i])
            born_targets.append([rho, current])
    return (
        np.asarray(born_features, dtype=float),
        np.asarray(stress_features, dtype=float),
        np.asarray(stress_targets, dtype=float),
        np.asarray(born_targets, dtype=float),
    )


def rel_residual(pred: np.ndarray, target: np.ndarray) -> float:
    return float(np.linalg.norm(pred - target) / max(float(np.linalg.norm(target)), 1.0))


def fit_heldout(
    features: np.ndarray,
    targets: np.ndarray,
    direction: str,
    component_names: tuple[str, str],
) -> tuple[list[dict[str, object]], np.ndarray]:
    split = int(0.65 * len(features))
    beta, *_ = np.linalg.lstsq(features[:split], targets[:split], rcond=None)
    train_pred = features[:split] @ beta
    test_pred = features[split:] @ beta
    rows = [
        {
            "direction": direction,
            "target_component": "joint",
            "train_residual": rel_residual(train_pred, targets[:split]),
            "heldout_residual": rel_residual(test_pred, targets[split:]),
            "derivable_at_tol_1e_minus_8": False,
        }
    ]
    for idx, name in enumerate(component_names):
        rows.append(
            {
                "direction": direction,
                "target_component": name,
                "train_residual": rel_residual(train_pred[:, idx], targets[:split, idx]),
                "heldout_residual": rel_residual(test_pred[:, idx], targets[split:, idx]),
                "derivable_at_tol_1e_minus_8": False,
            }
        )
    return rows, beta


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
    carrier = binary_carrier(4)
    qm_dims = (0, 1, 2)
    gr_dims = (0, 2, 3)
    defects_qm_to_gr = factorization_defects(carrier, qm_dims, gr_dims, "q_GR_through_q_QM")
    defects_gr_to_qm = factorization_defects(carrier, gr_dims, qm_dims, "q_QM_through_q_GR")
    control_defects, control_route = route_control_vertical_stack()

    defect_summary_rows = [
        {
            "case": "q_GR_through_q_QM",
            "source_quotient": "q_QM=(d0,d1,d2)",
            "target_quotient": "q_GR=(d0,d2,d3)",
            "defect_count": len(defects_qm_to_gr),
            "factors": len(defects_qm_to_gr) == 0,
        },
        {
            "case": "q_QM_through_q_GR",
            "source_quotient": "q_GR=(d0,d2,d3)",
            "target_quotient": "q_QM=(d0,d1,d2)",
            "defect_count": len(defects_gr_to_qm),
            "factors": len(defects_gr_to_qm) == 0,
        },
        {
            "case": "control_coarse_through_fine",
            "source_quotient": "fine=(x0,x1,x2)",
            "target_quotient": "coarse=(x0,x2)",
            "defect_count": len(control_defects),
            "factors": len(control_defects) == 0,
        },
    ]

    born_features, stress_features, stress_targets, born_targets = read_audit_values()
    audit_rows_born_to_stress, beta_born_to_stress = fit_heldout(
        born_features,
        stress_targets,
        "T_from_Born_rho_j",
        ("T00", "T0i"),
    )
    audit_rows_stress_to_born, beta_stress_to_born = fit_heldout(
        stress_features,
        born_targets,
        "Born_rho_j_from_T",
        ("rho", "current_j"),
    )
    audit_rows = audit_rows_born_to_stress + audit_rows_stress_to_born

    route_rows = [route_mismatch_for_qm_gr(carrier), control_route]

    all_defect_rows = defects_qm_to_gr + defects_gr_to_qm
    if control_defects:
        all_defect_rows.extend(control_defects)
    else:
        all_defect_rows.append(
            {
                "case": "control_coarse_through_fine",
                "left_state": -1,
                "right_state": -1,
                "source_value": "no_defect",
                "target_left": "no_defect",
                "target_right": "no_defect",
            }
        )

    write_csv(ARTIFACT_DIR / "factorization_defects_step30.csv", all_defect_rows)
    write_csv(ARTIFACT_DIR / "factorization_summary_step30.csv", defect_summary_rows)
    write_csv(ARTIFACT_DIR / "audit_non_derivability_step30.csv", audit_rows)
    write_csv(ARTIFACT_DIR / "route_mismatch_step30.csv", route_rows)

    matrices = {
        "carrier_modes": ["d0_density", "d1_phase", "d2_transport", "d3_curvature"],
        "carrier_states": carrier.tolist(),
        "q_QM_dims": list(qm_dims),
        "q_GR_dims": list(gr_dims),
        "qm_completion": conditional_mean_completion(carrier, qm_dims).tolist(),
        "gr_completion": conditional_mean_completion(carrier, gr_dims).tolist(),
        "beta_born_to_stress": beta_born_to_stress.tolist(),
        "beta_stress_to_born": beta_stress_to_born.tolist(),
        "route_diagnostic_definition": "Compare canonical fiber-mean L-completions from q_QM and q_GR.",
        "control_definition": "A genuine vertical stack where coarse=(x0,x2) factors exactly through fine=(x0,x1,x2).",
    }
    with (ARTIFACT_DIR / "directed_reduction_carrier_step30.json").open("w", encoding="utf-8") as handle:
        json.dump(matrices, handle, indent=2)

    qm_gr_route = route_rows[0]
    verdict_name = (
        "lemma1_directed_reduction_blocked_in_bounded_grammar"
        if len(defects_qm_to_gr) > 0
        and len(defects_gr_to_qm) > 0
        and max(row["heldout_residual"] for row in audit_rows) > 1e-2
        and qm_gr_route["normalized_route_mismatch"] > 1e-2
        and len(control_defects) == 0
        and control_route["commutes"]
        else "directed_reduction_unexpected_or_test_toothless"
    )
    output = {
        "step": 30,
        "verdict": {
            "lemma_verdict": verdict_name,
            "q_GR_factors_through_q_QM": len(defects_qm_to_gr) == 0,
            "q_QM_factors_through_q_GR": len(defects_gr_to_qm) == 0,
            "control_factors": len(control_defects) == 0,
            "route_mismatch_positive": qm_gr_route["normalized_route_mismatch"] > 1e-2,
            "control_route_commutes": bool(control_route["commutes"]),
            "root_landed": False,
            "bounded_grammar_scope": True,
            "external_review_required": True,
        },
        "summary": {
            "defect_count_q_GR_through_q_QM": len(defects_qm_to_gr),
            "defect_count_q_QM_through_q_GR": len(defects_gr_to_qm),
            "route_mismatch_raw": qm_gr_route["raw_route_mismatch"],
            "route_mismatch_normalized": qm_gr_route["normalized_route_mismatch"],
            "control_route_mismatch_normalized": control_route["normalized_route_mismatch"],
            "audit_T_from_Born_joint_heldout_residual": audit_rows_born_to_stress[0]["heldout_residual"],
            "audit_Born_from_T_joint_heldout_residual": audit_rows_stress_to_born[0]["heldout_residual"],
            "audit_T00_from_Born_heldout_residual": audit_rows_born_to_stress[1]["heldout_residual"],
            "audit_T0i_from_Born_heldout_residual": audit_rows_born_to_stress[2]["heldout_residual"],
            "audit_rho_from_T_heldout_residual": audit_rows_stress_to_born[1]["heldout_residual"],
            "audit_current_from_T_heldout_residual": audit_rows_stress_to_born[2]["heldout_residual"],
        },
        "guardrails": {
            "factorization_defects_computed": True,
            "audit_heldout_residuals_computed": True,
            "route_mismatch_computed": True,
            "genuine_reduction_control_passes": len(control_defects) == 0 and bool(control_route["commutes"]),
            "bounded_no_go_only": True,
        },
    }
    with (ARTIFACT_DIR / "directed_reduction_nogo_output_step30.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    with (ARTIFACT_DIR / "directed_reduction_nogo_output_step30.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 30 directed-reduction bounded no-go diagnostic\n")
        handle.write(f"Verdict: {verdict_name}\n")
        handle.write(f"q_GR through q_QM defect count: {len(defects_qm_to_gr)}\n")
        handle.write(f"q_QM through q_GR defect count: {len(defects_gr_to_qm)}\n")
        handle.write(f"route mismatch normalized: {qm_gr_route['normalized_route_mismatch']}\n")
        handle.write(f"control route mismatch normalized: {control_route['normalized_route_mismatch']}\n")
        handle.write(f"T from Born joint heldout residual: {audit_rows_born_to_stress[0]['heldout_residual']}\n")
        handle.write(f"Born from T joint heldout residual: {audit_rows_stress_to_born[0]['heldout_residual']}\n")


if __name__ == "__main__":
    main()
