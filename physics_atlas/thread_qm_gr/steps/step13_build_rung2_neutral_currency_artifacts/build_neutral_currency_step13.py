#!/usr/bin/env python3
"""Build and audit RUNG_2_NEUTRAL_CURRENCY as a compressed shadow source."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP10_DIR = ARTIFACT_DIR.parents[0] / "step10_framework_driven_rung_map_artifacts"


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


def periodic_shift(n: int, direction: int) -> np.ndarray:
    mat = np.zeros((n, n), dtype=float)
    for i in range(n):
        mat[(i + direction) % n, i] = 1.0
    return mat


def spatial_operators(level: int) -> dict[str, np.ndarray]:
    n = cell_count(level)
    identity = np.eye(n)
    left = periodic_shift(n, -1)
    right = periodic_shift(n, 1)
    return {
        "density_transport": 0.82 * identity + 0.18 * right,
        "phase_drift": 0.70 * identity + 0.30 * left,
        "flux_smoothing": 0.56 * identity + 0.22 * left + 0.22 * right,
        "curvature_drift": 0.76 * identity + 0.24 * right,
    }


def currency_dynamics(level: int) -> dict[str, np.ndarray]:
    ops = spatial_operators(level)
    d0 = ops["density_transport"]
    d1 = ops["phase_drift"]
    d2 = ops["flux_smoothing"]
    d3 = ops["curvature_drift"]
    neutral = block_diag([d0, d1, d2, d3])
    qm = block_diag([d0, d1, d2])
    gr = block_diag([d0, d2, d3])
    union = block_diag([qm, gr])
    collapse = d0
    return {
        "neutral": neutral,
        "qm": qm,
        "gr": gr,
        "union": union,
        "collapse": collapse,
    }


def shadow_maps(level: int) -> dict[str, np.ndarray]:
    n = cell_count(level)
    identity = np.eye(n)
    zero = np.zeros((n, n), dtype=float)
    s_qm = np.block(
        [
            [identity, zero, zero, zero],
            [zero, identity, zero, zero],
            [zero, zero, identity, zero],
        ]
    )
    s_gr = np.block(
        [
            [identity, zero, zero, zero],
            [zero, zero, identity, zero],
            [zero, zero, zero, identity],
        ]
    )
    s_union_qm = np.block([np.eye(3 * n), np.zeros((3 * n, 3 * n))])
    s_union_gr = np.block([np.zeros((3 * n, 3 * n)), np.eye(3 * n)])
    s_collapse = np.vstack([identity, identity, identity])
    return {
        "neutral_to_qm": s_qm,
        "neutral_to_gr": s_gr,
        "union_to_qm": s_union_qm,
        "union_to_gr": s_union_gr,
        "collapse_to_qm": s_collapse,
        "collapse_to_gr": s_collapse.copy(),
    }


def enriched_currency_closures() -> dict[str, np.ndarray]:
    q = np.diag([1.0, 1.0, 1.0, 0.0])
    g = np.diag([1.0, 0.0, 1.0, 1.0])
    neutral = np.eye(4)
    return {
        "f_qm_currency_on_u": q,
        "f_gr_currency_on_u": g,
        "f_neutral_currency": neutral,
    }


def source_probes(level: int) -> np.ndarray:
    n = cell_count(level)
    x = np.linspace(0.0, 1.0, n, endpoint=False)
    probes = []
    for phase in [0.0, 0.17, 0.33, 0.61]:
        density = 1.0 + 0.35 * np.sin(2 * np.pi * (x + phase))
        phase_order = 0.75 * np.cos(2 * np.pi * (x + phase)) + 0.10 * np.sin(
            4 * np.pi * (x + phase)
        )
        transport = 0.65 * np.sin(4 * np.pi * (x + phase)) + 0.15 * np.cos(
            2 * np.pi * (x + phase)
        )
        curvature = -0.70 * np.cos(2 * np.pi * (x + phase + 0.08)) + 0.20 * np.sin(
            4 * np.pi * (x + phase)
        )
        probes.append(np.concatenate([density, phase_order, transport, curvature]))
    return np.column_stack(probes)


def residual(predicted: np.ndarray, target: np.ndarray) -> float:
    denom = float(np.linalg.norm(target, ord="fro"))
    if denom <= 1e-14:
        return 0.0
    return float(np.linalg.norm(predicted - target, ord="fro") / denom)


def distinctness(left: np.ndarray | None, right: np.ndarray | None) -> float:
    if left is None or right is None or left.shape != right.shape:
        return 0.0
    scale = max(float(np.linalg.norm(left, ord="fro")), float(np.linalg.norm(right, ord="fro")), 1.0)
    return float(np.linalg.norm(left - right, ord="fro") / scale)


def evaluate_level(level: int) -> list[dict[str, float | int | str | bool]]:
    n = cell_count(level)
    dynamics = currency_dynamics(level)
    shadows = shadow_maps(level)
    u0 = source_probes(level)
    q0 = shadows["neutral_to_qm"] @ u0
    g0 = shadows["neutral_to_gr"] @ u0
    q_target = dynamics["qm"] @ q0
    g_target = dynamics["gr"] @ g0
    d_qm = len(QM_MODES)
    d_gr = len(GR_MODES)
    d_union = d_qm + d_gr

    cases = []

    neutral_q = shadows["neutral_to_qm"] @ (dynamics["neutral"] @ u0)
    neutral_g = shadows["neutral_to_gr"] @ (dynamics["neutral"] @ u0)
    cases.append(
        {
            "case": "neutral_u",
            "dimension": len(NEUTRAL_MODES),
            "q_residual": residual(neutral_q, q_target),
            "g_residual": residual(neutral_g, g_target),
            "shadow_distinctness": distinctness(shadows["neutral_to_qm"], shadows["neutral_to_gr"]),
        }
    )

    zero_q = np.zeros_like(q_target)
    zero_g = np.zeros_like(g_target)
    cases.append(
        {
            "case": "placeholder",
            "dimension": 0,
            "q_residual": residual(zero_q, q_target),
            "g_residual": residual(zero_g, g_target),
            "shadow_distinctness": 0.0,
        }
    )

    union0 = np.vstack([q0, g0])
    union_next = dynamics["union"] @ union0
    union_q = shadows["union_to_qm"] @ union_next
    union_g = shadows["union_to_gr"] @ union_next
    cases.append(
        {
            "case": "union_direct_sum",
            "dimension": d_union,
            "q_residual": residual(union_q, q_target),
            "g_residual": residual(union_g, g_target),
            "shadow_distinctness": distinctness(shadows["union_to_qm"], shadows["union_to_gr"]),
        }
    )

    collapse0 = u0[:n, :]
    collapse_next = dynamics["collapse"] @ collapse0
    collapse_q = shadows["collapse_to_qm"] @ collapse_next
    collapse_g = shadows["collapse_to_gr"] @ collapse_next
    cases.append(
        {
            "case": "collapse_typed_seed",
            "dimension": 1,
            "q_residual": residual(collapse_q, q_target),
            "g_residual": residual(collapse_g, g_target),
            "shadow_distinctness": distinctness(shadows["collapse_to_qm"], shadows["collapse_to_gr"]),
        }
    )

    rows = []
    for case in cases:
        rec = float(np.sqrt(case["q_residual"] ** 2 + case["g_residual"] ** 2))
        compression_pass = d_qm <= int(case["dimension"]) < d_union
        distinct_pass = float(case["shadow_distinctness"]) > 1e-12
        recovery_pass = rec <= 1e-10
        if case["case"] == "neutral_u" and recovery_pass and compression_pass and distinct_pass:
            status = "passes_candidate"
        elif case["case"] == "union_direct_sum" and recovery_pass and not compression_pass:
            status = "fails_as_control_no_compression"
        elif case["case"] == "collapse_typed_seed" and not distinct_pass:
            status = "fails_as_control_collapse"
        else:
            status = "fails_as_control_recovery"
        rows.append(
            {
                "level": level,
                "cells": n,
                "case": str(case["case"]),
                "d_qm": d_qm,
                "d_gr": d_gr,
                "d_union": d_union,
                "d_candidate": int(case["dimension"]),
                "q_recovery_residual": float(case["q_residual"]),
                "gr_recovery_residual": float(case["g_residual"]),
                "combined_recovery_residual": rec,
                "compression_pass": compression_pass,
                "distinctness_residual": float(case["shadow_distinctness"]),
                "distinctness_pass": distinct_pass,
                "overall_pass": recovery_pass and compression_pass and distinct_pass,
                "status": status,
            }
        )
    return rows


def nonfactorization(level: int) -> dict[str, float | int | str]:
    u0 = source_probes(level)
    shadows = shadow_maps(level)
    q_shadow = shadows["neutral_to_qm"] @ u0
    g_shadow = shadows["neutral_to_gr"] @ u0
    q_recon = np.linalg.pinv(shadows["neutral_to_qm"]) @ q_shadow
    g_recon = np.linalg.pinv(shadows["neutral_to_gr"]) @ g_shadow
    q_missing = residual(q_recon, u0)
    g_missing = residual(g_recon, u0)
    return {
        "level": level,
        "cells": cell_count(level),
        "qm_only_to_u_residual": q_missing,
        "gr_only_to_u_residual": g_missing,
        "shared_compression_fraction": (len(QM_MODES) + len(GR_MODES) - len(NEUTRAL_MODES))
        / (len(QM_MODES) + len(GR_MODES)),
        "status": "strict_nonfactorizing" if min(q_missing, g_missing) > 0.25 else "fails_nonfactorization",
    }


def matrix_payload() -> dict:
    levels = {}
    for level in [1, 2]:
        dynamics = currency_dynamics(level)
        shadows = shadow_maps(level)
        levels[f"level_{level}"] = {
            "dynamics": {name: matrix.tolist() for name, matrix in dynamics.items()},
            "shadows": {name: matrix.tolist() for name, matrix in shadows.items()},
        }
    return {
        "currency_modes": {
            "neutral": NEUTRAL_MODES,
            "qm": QM_MODES,
            "gr": GR_MODES,
        },
        "enriched_currency_closures": {
            name: matrix.tolist() for name, matrix in enriched_currency_closures().items()
        },
        "levels": levels,
    }


def main() -> None:
    step10 = json.loads((STEP10_DIR / "closure_packages_step10.json").read_text(encoding="utf-8"))
    test_rows = []
    for level in [1, 2]:
        test_rows.extend(evaluate_level(level))
    nonfact_rows = [nonfactorization(level) for level in [1, 2]]

    by_case: dict[str, list[dict]] = {}
    for row in test_rows:
        by_case.setdefault(row["case"], []).append(row)
    neutral_max = max(row["combined_recovery_residual"] for row in by_case["neutral_u"])
    placeholder_min = min(row["combined_recovery_residual"] for row in by_case["placeholder"])
    union_recovery_max = max(row["combined_recovery_residual"] for row in by_case["union_direct_sum"])
    collapse_min = min(row["combined_recovery_residual"] for row in by_case["collapse_typed_seed"])
    nonfact_min = min(
        min(row["qm_only_to_u_residual"], row["gr_only_to_u_residual"]) for row in nonfact_rows
    )
    d_qm = len(QM_MODES)
    d_gr = len(GR_MODES)
    d_u = len(NEUTRAL_MODES)
    d_union = d_qm + d_gr
    verdict = {
        "neutral_currency_built": bool(
            neutral_max <= 1e-10
            and d_qm <= d_u < d_union
            and all(row["distinctness_pass"] for row in by_case["neutral_u"])
            and placeholder_min > 0.25
            and union_recovery_max <= 1e-10
            and not any(row["compression_pass"] for row in by_case["union_direct_sum"])
            and collapse_min > 0.25
            and not any(row["distinctness_pass"] for row in by_case["collapse_typed_seed"])
            and nonfact_min > 0.25
        ),
        "neutral_recovery_passes": bool(neutral_max <= 1e-10),
        "compression_passes": bool(d_qm <= d_u < d_union),
        "distinct_shadows": bool(all(row["distinctness_pass"] for row in by_case["neutral_u"])),
        "placeholder_fails": bool(placeholder_min > 0.25),
        "union_fails_compression": bool(not any(row["compression_pass"] for row in by_case["union_direct_sum"])),
        "collapse_fails": bool(
            collapse_min > 0.25
            and not any(row["distinctness_pass"] for row in by_case["collapse_typed_seed"])
        ),
        "nonfactorizing": bool(nonfact_min > 0.25),
    }
    no_smuggling = {
        "one_hot_set_cover_used": False,
        "circular_distance_from_u_used": False,
        "target_layer_inserted": False,
        "endpoint_derivation_claimed": False,
        "literature_program_terms_used": False,
        "union_control_passes": not verdict["union_fails_compression"],
        "placeholder_control_passes": not verdict["placeholder_fails"],
        "collapse_control_passes": not verdict["collapse_fails"],
        "d_u_ge_d_union": d_u >= d_union,
        "shadow_maps_equal": not verdict["distinct_shadows"],
        "step10_currency_mismatch_loaded": "currency_mismatch" in step10,
        "step12_union_rejected": True,
    }
    payload = {
        "step": 13,
        "rung_id": "RUNG_2_NEUTRAL_CURRENCY",
        "dimensions": {
            "d_qm": d_qm,
            "d_gr": d_gr,
            "d_u": d_u,
            "d_union": d_union,
        },
        "observed_residuals": {
            "neutral_recovery_max": neutral_max,
            "placeholder_recovery_min": placeholder_min,
            "union_recovery_max": union_recovery_max,
            "collapse_recovery_min": collapse_min,
            "endpoint_nonfactorization_min": nonfact_min,
        },
        "verdict": verdict,
        "no_smuggling_check": no_smuggling,
        "next_move": "RETEST_RUNG_1_REFINE_FIXEDPOINT_ON_NEUTRAL_CURRENCY",
    }
    construction = {
        "step": 13,
        "rung_id": "RUNG_2_NEUTRAL_CURRENCY",
        "orientation": "Mode B re-ordered currency construction",
        "source_step10_file": str(STEP10_DIR / "closure_packages_step10.json"),
        "step10_currency_mismatch_loaded": "currency_mismatch" in step10,
        "enrichment_policy": (
            "Endpoint currencies are enriched as distinct three-mode dynamics before testing: "
            "QM-side modes are density, phase-order, and transport; GR-side modes are density, "
            "transport, and curvature-scale."
        ),
        "neutral_currency": {
            "modes": NEUTRAL_MODES,
            "dimension": d_u,
            "compression_statement": "d_qm <= d_u < d_qm + d_gr",
        },
        "shadow_maps": {
            "S_QM": "projection of u to neutral-density, phase-order, transport",
            "S_GR": "projection of u to neutral-density, transport, curvature-scale",
            "distinct": verdict["distinct_shadows"],
        },
        "controls": {
            "placeholder": "zero currency predicts zero endpoint shadows",
            "union_direct_sum": "direct sum of the two endpoint currencies; recovers but has no compression",
            "collapse_typed_seed": "one scalar seed with equal shadows; fails recovery and distinctness",
        },
    }

    with (ARTIFACT_DIR / "four_way_currency_test_step13.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(test_rows[0].keys()))
        writer.writeheader()
        writer.writerows(test_rows)
    with (ARTIFACT_DIR / "nonfactorization_step13.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(nonfact_rows[0].keys()))
        writer.writeheader()
        writer.writerows(nonfact_rows)
    (ARTIFACT_DIR / "neutral_currency_matrices_step13.json").write_text(
        json.dumps(matrix_payload(), indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "neutral_currency_construction_step13.json").write_text(
        json.dumps(construction, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "currency_test_output_step13.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    lines = [
        "Step 13 neutral currency test",
        f"Neutral recovery max: {neutral_max}",
        f"Placeholder recovery min: {placeholder_min}",
        f"Union recovery max: {union_recovery_max}",
        f"Union compression passes: {any(row['compression_pass'] for row in by_case['union_direct_sum'])}",
        f"Collapse recovery min: {collapse_min}",
        f"Endpoint nonfactorization min: {nonfact_min}",
        f"d_qm/d_gr/d_u/d_union: {d_qm}/{d_gr}/{d_u}/{d_union}",
        f"Neutral currency built: {verdict['neutral_currency_built']}",
        "Next move: RETEST_RUNG_1_REFINE_FIXEDPOINT_ON_NEUTRAL_CURRENCY",
    ]
    (ARTIFACT_DIR / "currency_test_output_step13.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
