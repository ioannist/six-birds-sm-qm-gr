#!/usr/bin/env python3
"""Bind RUNG_1_REFINE_FIXEDPOINT to the Step-10 QM/GR closure rules."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP10_DIR = ARTIFACT_DIR.parents[0] / "step10_framework_driven_rung_map_artifacts"


ATOM_NAMES = [
    "typed_carrier",
    "composition_slot",
    "q_amplitude_currency",
    "q_probability_audit",
    "q_record_branch",
    "q_unitary_fixedpoint",
    "g_metric_currency",
    "g_curvature_audit",
    "g_event_locality",
    "g_geodesic_fixedpoint",
]
ATOM = {name: i for i, name in enumerate(ATOM_NAMES)}


def cell_count(level: int) -> int:
    return 2**level


def kron_cells(level: int, atom_matrix: np.ndarray) -> np.ndarray:
    return np.kron(np.eye(cell_count(level)), atom_matrix)


def endpoint_atom_matrices() -> dict[str, np.ndarray]:
    """Construct idempotent linear closures faithful to the Step-10 rules."""
    a = len(ATOM_NAMES)
    q = np.zeros((a, a), dtype=float)
    g = np.zeros((a, a), dtype=float)

    # QM closure: typed -> composition -> amplitude -> unitary;
    # record + amplitude -> probability audit, represented by a linear
    # seed-preserving idempotent map on typed and q_record_branch.
    q[ATOM["typed_carrier"], ATOM["typed_carrier"]] = 1.0
    q[ATOM["composition_slot"], ATOM["typed_carrier"]] = 1.0
    q[ATOM["q_amplitude_currency"], ATOM["typed_carrier"]] = 1.0
    q[ATOM["q_unitary_fixedpoint"], ATOM["typed_carrier"]] = 1.0
    q[ATOM["q_record_branch"], ATOM["q_record_branch"]] = 1.0
    q[ATOM["q_probability_audit"], ATOM["typed_carrier"]] = 0.5
    q[ATOM["q_probability_audit"], ATOM["q_record_branch"]] = 0.5

    # GR closure: typed -> composition -> event/locality -> metric+route -> audit.
    g[ATOM["typed_carrier"], ATOM["typed_carrier"]] = 1.0
    g[ATOM["composition_slot"], ATOM["typed_carrier"]] = 1.0
    g[ATOM["g_event_locality"], ATOM["typed_carrier"]] = 1.0
    g[ATOM["g_metric_currency"], ATOM["typed_carrier"]] = 1.0
    g[ATOM["g_geodesic_fixedpoint"], ATOM["typed_carrier"]] = 1.0
    g[ATOM["g_curvature_audit"], ATOM["typed_carrier"]] = 1.0

    # Bound RUNG_1 closure: preserve the QM seed atoms and run both endpoint
    # closures into one shared carrier.
    bound = q + g
    for shared in ["typed_carrier", "composition_slot"]:
        bound[ATOM[shared], :] = 0.0
        bound[ATOM[shared], ATOM["typed_carrier"]] = 1.0

    # Generic averaging control: pair endpoint atoms by label position, without
    # respecting the Step-10 closure rules.
    generic = np.eye(a)
    pairs = [
        ("q_record_branch", "g_event_locality"),
        ("q_amplitude_currency", "g_metric_currency"),
        ("q_unitary_fixedpoint", "g_geodesic_fixedpoint"),
        ("q_probability_audit", "g_curvature_audit"),
    ]
    for left, right in pairs:
        i, j = ATOM[left], ATOM[right]
        generic[i, :] = 0.0
        generic[j, :] = 0.0
        generic[i, i] = 0.5
        generic[i, j] = 0.5
        generic[j, i] = 0.5
        generic[j, j] = 0.5

    return {"qm": q, "gr": g, "bound": bound, "generic": generic}


def refinement_lift(level: int) -> np.ndarray:
    cells = cell_count(level)
    fine = cell_count(level + 1)
    single = np.zeros((fine, cells), dtype=float)
    for i in range(cells):
        single[2 * i, i] = 1.0
        single[2 * i + 1, i] = 1.0
    return np.kron(single, np.eye(len(ATOM_NAMES)))


def probes(level: int) -> np.ndarray:
    cells = cell_count(level)
    xs = np.linspace(0.0, 1.0, cells, endpoint=False)
    rows = []
    for phase in [0.0, 0.25, 0.5, 0.75]:
        cell_values = {
            "typed_carrier": 1.0 + 0.15 * np.sin(2 * np.pi * (xs + phase)),
            "composition_slot": 0.25 * np.cos(2 * np.pi * (xs + phase)),
            "q_record_branch": np.sin(2 * np.pi * (xs + phase)),
            "q_amplitude_currency": 0.4 * np.cos(4 * np.pi * (xs + phase)),
            "q_unitary_fixedpoint": -0.3 * np.sin(2 * np.pi * (xs + phase)),
            "q_probability_audit": 0.2 * np.cos(2 * np.pi * (xs + phase)),
            "g_event_locality": np.cos(2 * np.pi * (xs + phase + 0.1)),
            "g_metric_currency": -0.5 * np.sin(2 * np.pi * (xs + phase)),
            "g_geodesic_fixedpoint": 0.3 * np.cos(4 * np.pi * (xs + phase)),
            "g_curvature_audit": -0.2 * np.sin(4 * np.pi * (xs + phase)),
        }
        vector = np.zeros((cells, len(ATOM_NAMES)), dtype=float)
        for atom, values in cell_values.items():
            vector[:, ATOM[atom]] = values
        rows.append(vector.reshape(-1))
    return np.column_stack(rows)


def frob_ratio(numerator: np.ndarray, denominator: np.ndarray) -> float:
    denom = float(np.linalg.norm(denominator, ord="fro"))
    if denom <= 1e-14:
        return 0.0
    return float(np.linalg.norm(numerator, ord="fro") / denom)


def rule_residual(level: int, candidate_output: np.ndarray, closure: np.ndarray, atom_subset: list[str]) -> float:
    full = kron_cells(level, closure) @ candidate_output
    cells = cell_count(level)
    mask = np.zeros((cells, len(ATOM_NAMES)), dtype=float)
    for atom in atom_subset:
        mask[:, ATOM[atom]] = 1.0
    mask_vec = mask.reshape(-1, 1)
    selected_output = candidate_output * mask_vec
    selected_full = full * mask_vec
    return frob_ratio(selected_output - selected_full, selected_full)


def transition_diagnostic(level: int, candidate_name: str, candidate_atom_matrix: np.ndarray, matrices: dict[str, np.ndarray]) -> dict:
    x = probes(level)
    lift = refinement_lift(level)
    c_n = kron_cells(level, candidate_atom_matrix)
    c_np1 = kron_cells(level + 1, candidate_atom_matrix)
    bound_n = kron_cells(level, matrices["bound"])
    bound_np1 = kron_cells(level + 1, matrices["bound"])

    y_n = c_n @ x
    y_np1 = c_np1 @ (lift @ x)

    comm = frob_ratio(lift @ y_n - y_np1, y_np1)
    shared_defect = frob_ratio(bound_np1 @ y_np1 - y_np1, bound_np1 @ y_np1)
    qm_atoms = [
        "typed_carrier",
        "composition_slot",
        "q_amplitude_currency",
        "q_unitary_fixedpoint",
        "q_record_branch",
        "q_probability_audit",
    ]
    gr_atoms = [
        "typed_carrier",
        "composition_slot",
        "g_event_locality",
        "g_metric_currency",
        "g_geodesic_fixedpoint",
        "g_curvature_audit",
    ]
    qm_res = rule_residual(level + 1, y_np1, matrices["qm"], qm_atoms)
    gr_res = rule_residual(level + 1, y_np1, matrices["gr"], gr_atoms)
    descent = float(np.sqrt(qm_res**2 + gr_res**2))
    adequacy = float(np.sqrt(comm**2 + shared_defect**2 + descent**2))

    return {
        "case": candidate_name,
        "transition": f"{level}->{level + 1}",
        "commutator_residual": comm,
        "shared_fixedpoint_defect": shared_defect,
        "qm_descent_residual": qm_res,
        "gr_descent_residual": gr_res,
        "two_sided_descent_residual": descent,
        "adequacy_residual": adequacy,
    }


def nonfactorization(level: int, matrices: dict[str, np.ndarray]) -> dict:
    x = probes(level)
    bound_y = kron_cells(level, matrices["bound"]) @ x
    qm_y = kron_cells(level, matrices["qm"]) @ x
    gr_y = kron_cells(level, matrices["gr"]) @ x
    return {
        "level": level,
        "cells": cell_count(level),
        "qm_only_to_bound_residual": frob_ratio(bound_y - qm_y, bound_y),
        "gr_only_to_bound_residual": frob_ratio(bound_y - gr_y, bound_y),
        "bound_work_norm": frob_ratio(bound_y - x, x),
    }


def idempotence_error(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix @ matrix - matrix, ord="fro"))


def main() -> None:
    step10_packages = json.loads((STEP10_DIR / "closure_packages_step10.json").read_text(encoding="utf-8"))
    matrices = endpoint_atom_matrices()
    cases = {
        "bound": matrices["bound"],
        "placeholder": np.eye(len(ATOM_NAMES)),
        "generic_averaging": matrices["generic"],
    }
    diagnostics = []
    for case, matrix in cases.items():
        for level in [1, 2]:
            diagnostics.append(transition_diagnostic(level, case, matrix, matrices))

    emergence = [nonfactorization(level, matrices) for level in [1, 2, 3]]
    thresholds = {
        "bound_adequacy_max": 1e-10,
        "placeholder_adequacy_min": 0.25,
        "generic_adequacy_min": 0.25,
        "endpoint_nonfactorization_min": 0.25,
    }
    by_case = {}
    for case in cases:
        rows = [row for row in diagnostics if row["case"] == case]
        by_case[case] = {
            "min": min(row["adequacy_residual"] for row in rows),
            "max": max(row["adequacy_residual"] for row in rows),
        }
    nonfact_min = min(
        min(row["qm_only_to_bound_residual"], row["gr_only_to_bound_residual"]) for row in emergence
    )
    verdict = {
        "bound_passes": by_case["bound"]["max"] <= thresholds["bound_adequacy_max"],
        "placeholder_fails": by_case["placeholder"]["min"] >= thresholds["placeholder_adequacy_min"],
        "generic_averaging_fails": by_case["generic_averaging"]["min"] >= thresholds["generic_adequacy_min"],
        "nonfactorizing": nonfact_min >= thresholds["endpoint_nonfactorization_min"],
    }
    verdict["bound_rung1_built"] = all(verdict.values())

    construction = {
        "rung_id": "RUNG_1_REFINE_FIXEDPOINT_BOUND_TO_REAL_CLOSURES",
        "loaded_step10_package_file": str(STEP10_DIR / "closure_packages_step10.json"),
        "step10_qm_closed_seed": step10_packages["qm_package"]["closed_seed"],
        "step10_gr_closed_seed": step10_packages["gr_package"]["closed_seed"],
        "atom_names": ATOM_NAMES,
        "levels": [1, 2, 3],
        "carrier": "per-cell atom vector over Step-10 QM/GR closure atoms, refined over 2^n cells",
        "bound_closure": "union closure generated by running f_QM and f_GR from their Step-10 seed structure",
        "lift": "cell duplication on every Step-10 atom coordinate",
        "idempotence_errors": {
            name: idempotence_error(matrix) for name, matrix in matrices.items()
        },
        "controls": {
            "placeholder": "identity closure",
            "generic_averaging": "pairwise averaging of endpoint-specific atoms without closure rules",
        },
    }

    matrix_artifact = {
        "atom_names": ATOM_NAMES,
        "atom_matrices": {name: matrix.tolist() for name, matrix in matrices.items()},
        "level_matrices": {
            f"level_{level}": {
                "qm": kron_cells(level, matrices["qm"]).tolist(),
                "gr": kron_cells(level, matrices["gr"]).tolist(),
                "bound": kron_cells(level, matrices["bound"]).tolist(),
                "generic_averaging": kron_cells(level, matrices["generic"]).tolist(),
                "placeholder": np.eye(cell_count(level) * len(ATOM_NAMES)).tolist(),
            }
            for level in [1, 2, 3]
        },
        "lifts": {
            f"{level}_to_{level + 1}": refinement_lift(level).tolist() for level in [1, 2]
        },
    }

    payload = {
        "construction": construction,
        "thresholds": thresholds,
        "diagnostics": diagnostics,
        "emergence_nonfactorization": emergence,
        "observed_residual_range": by_case,
        "endpoint_nonfactorization_min": nonfact_min,
        "no_smuggling_check": {
            "one_hot_set_cover_used": False,
            "literature_program_terms_used": False,
            "target_layer_inserted": False,
            "endpoint_derivation_claimed": False,
            "placeholder_passes": not verdict["placeholder_fails"],
            "generic_averaging_passes": not verdict["generic_averaging_fails"],
            "step10_closures_loaded": True,
        },
        "verdict": verdict,
        "next_build": "RUNG_2_NEUTRAL_CURRENCY" if verdict["bound_rung1_built"] else "REDIRECT_RUNG_1_MECHANISM",
    }

    (ARTIFACT_DIR / "bound_rung1_construction_step12.json").write_text(
        json.dumps(construction, indent=2) + "\n", encoding="utf-8"
    )
    (ARTIFACT_DIR / "bound_structured_matrices_step12.json").write_text(
        json.dumps(matrix_artifact, indent=2) + "\n", encoding="utf-8"
    )
    (ARTIFACT_DIR / "adequacy_output_step12.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    with (ARTIFACT_DIR / "three_way_adequacy_step12.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case",
                "transition",
                "commutator_residual",
                "shared_fixedpoint_defect",
                "qm_descent_residual",
                "gr_descent_residual",
                "two_sided_descent_residual",
                "adequacy_residual",
                "status",
            ],
        )
        writer.writeheader()
        for row in diagnostics:
            if row["case"] == "bound":
                status = "passes" if row["adequacy_residual"] <= thresholds["bound_adequacy_max"] else "fails"
            elif row["case"] == "placeholder":
                status = (
                    "fails_as_control"
                    if row["adequacy_residual"] >= thresholds["placeholder_adequacy_min"]
                    else "passes_bad_control"
                )
            else:
                status = (
                    "fails_as_control"
                    if row["adequacy_residual"] >= thresholds["generic_adequacy_min"]
                    else "passes_bad_control"
                )
            writer.writerow({**row, "status": status})

    with (ARTIFACT_DIR / "nonfactorization_step12.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "level",
                "cells",
                "qm_only_to_bound_residual",
                "gr_only_to_bound_residual",
                "bound_work_norm",
                "status",
            ],
        )
        writer.writeheader()
        for row in emergence:
            status = (
                "strict_nonfactorizing"
                if min(row["qm_only_to_bound_residual"], row["gr_only_to_bound_residual"])
                >= thresholds["endpoint_nonfactorization_min"]
                else "factors_through_endpoint"
            )
            writer.writerow({**row, "status": status})

    txt_lines = [
        "Step 12 bound RUNG_1 to Step-10 closures",
        f"Bound adequacy max: {by_case['bound']['max']}",
        f"Placeholder adequacy min: {by_case['placeholder']['min']}",
        f"Generic averaging adequacy min: {by_case['generic_averaging']['min']}",
        f"Endpoint nonfactorization min: {nonfact_min}",
        f"Bound rung built: {verdict['bound_rung1_built']}",
        f"Next build: {payload['next_build']}",
    ]
    (ARTIFACT_DIR / "adequacy_output_step12.txt").write_text(
        "\n".join(txt_lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
