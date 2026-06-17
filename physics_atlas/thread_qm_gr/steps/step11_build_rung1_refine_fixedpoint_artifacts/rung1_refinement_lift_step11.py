#!/usr/bin/env python3
"""Build and audit RUNG_1_REFINE_FIXEDPOINT as structured finite maps."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent


def refinement_lift(n: int) -> np.ndarray:
    """Lift two-channel level n to n+1 by duplicating each cell."""
    cells = 2**n
    fine = 2 ** (n + 1)
    single = np.zeros((fine, cells), dtype=float)
    for i in range(cells):
        single[2 * i, i] = 1.0
        single[2 * i + 1, i] = 1.0
    out = np.zeros((2 * fine, 2 * cells), dtype=float)
    out[:fine, :cells] = single
    out[fine:, cells:] = single
    return out


def rung_closure(n: int) -> np.ndarray:
    """Idempotent closure to the record/locality shared fixed-point subspace."""
    cells = 2**n
    eye = np.eye(cells)
    top = np.hstack([0.5 * eye, 0.5 * eye])
    bottom = np.hstack([0.5 * eye, 0.5 * eye])
    return np.vstack([top, bottom])


def placeholder_closure(n: int) -> np.ndarray:
    """Inert placeholder: idempotent but no record/locality reconciliation."""
    return np.eye(2 * (2**n))


def qm_endpoint_closure(n: int) -> np.ndarray:
    """Endpoint-side record-only closure, used for nonfactorization control."""
    cells = 2**n
    eye = np.eye(cells)
    zero = np.zeros((cells, cells))
    return np.vstack([np.hstack([eye, zero]), np.hstack([zero, zero])])


def gr_endpoint_closure(n: int) -> np.ndarray:
    """Endpoint-side locality-only closure, used for nonfactorization control."""
    cells = 2**n
    eye = np.eye(cells)
    zero = np.zeros((cells, cells))
    return np.vstack([np.hstack([zero, zero]), np.hstack([zero, eye])])


def qm_coarsening(n: int) -> np.ndarray:
    cells = 2**n
    return np.hstack([np.eye(cells), np.zeros((cells, cells))])


def gr_coarsening(n: int) -> np.ndarray:
    cells = 2**n
    return np.hstack([np.zeros((cells, cells)), np.eye(cells)])


def test_probes(n: int) -> np.ndarray:
    """Deterministic probes with record/locality mismatch and cell structure."""
    cells = 2**n
    xs = np.linspace(0.0, 1.0, cells, endpoint=False)
    probes = []
    record_patterns = [
        np.sin(2.0 * np.pi * xs),
        np.cos(2.0 * np.pi * xs),
        np.where(np.arange(cells) % 2 == 0, 1.0, -1.0),
        np.linspace(-1.0, 1.0, cells),
    ]
    locality_patterns = [
        np.cos(2.0 * np.pi * xs + 0.35),
        -np.sin(2.0 * np.pi * xs),
        np.linspace(1.0, -1.0, cells),
        np.where(np.arange(cells) % 2 == 0, -0.5, 0.75),
    ]
    for r, e in zip(record_patterns, locality_patterns):
        probes.append(np.concatenate([r, e]))
    return np.column_stack(probes)


def frob_ratio(numerator: np.ndarray, denominator: np.ndarray) -> float:
    denom = float(np.linalg.norm(denominator, ord="fro"))
    if denom <= 1e-14:
        return 0.0
    return float(np.linalg.norm(numerator, ord="fro") / denom)


def channel_discrepancy(n: int, closed: np.ndarray) -> float:
    cells = 2**n
    record = closed[:cells, :]
    locality = closed[cells:, :]
    return frob_ratio(record - locality, closed)


def descent_discrepancy(n: int, closure: np.ndarray, probes: np.ndarray) -> float:
    closed = closure @ probes
    q_read = qm_coarsening(n) @ closed
    g_read = gr_coarsening(n) @ closed
    return frob_ratio(q_read - g_read, closed)


def transition_diagnostic(n: int, closure_fn) -> dict:
    closure_n = closure_fn(n)
    closure_np1 = closure_fn(n + 1)
    lift = refinement_lift(n)
    probes = test_probes(n)
    lifted = lift @ probes

    left = lift @ (closure_n @ probes)
    right = closure_np1 @ lifted
    commutator = frob_ratio(left - right, right if np.linalg.norm(right) > 1e-14 else lifted)

    closed_n = closure_n @ probes
    closed_np1 = closure_np1 @ lifted
    fixed_n = channel_discrepancy(n, closed_n)
    fixed_np1 = channel_discrepancy(n + 1, closed_np1)
    descent_n = descent_discrepancy(n, closure_n, probes)
    descent_np1 = descent_discrepancy(n + 1, closure_np1, lifted)

    adequacy = float(np.sqrt(commutator**2 + fixed_np1**2 + descent_np1**2))
    return {
        "transition": f"{n}->{n + 1}",
        "cells_n": 2**n,
        "cells_np1": 2 ** (n + 1),
        "commutator_residual": commutator,
        "fixedpoint_discrepancy_n": fixed_n,
        "fixedpoint_discrepancy_np1": fixed_np1,
        "descent_discrepancy_n": descent_n,
        "descent_discrepancy_np1": descent_np1,
        "adequacy_residual": adequacy,
    }


def endpoint_nonfactorization(n: int) -> dict:
    probes = test_probes(n)
    rung = rung_closure(n) @ probes
    qm = qm_endpoint_closure(n) @ probes
    gr = gr_endpoint_closure(n) @ probes
    return {
        "level": n,
        "cells": 2**n,
        "qm_only_to_rung_residual": frob_ratio(rung - qm, rung),
        "gr_only_to_rung_residual": frob_ratio(rung - gr, rung),
        "rung_work_norm": frob_ratio(rung - probes, probes),
    }


def idempotence_error(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix @ matrix - matrix, ord="fro"))


def main() -> None:
    transitions = [1, 2]
    built = [transition_diagnostic(n, rung_closure) for n in transitions]
    placeholder = [transition_diagnostic(n, placeholder_closure) for n in transitions]
    emergence = [endpoint_nonfactorization(n) for n in [1, 2, 3]]

    construction = {
        "rung_id": "RUNG_1_REFINE_FIXEDPOINT",
        "levels": [1, 2, 3],
        "carrier": "two-channel finite carrier: record channel plus locality channel over 2^n cells",
        "closure": "idempotent projection (record, locality) -> shared channel average",
        "lift": "cell-duplication refinement lift applied to both channels",
        "qm_side_coarsening": "record-channel projection",
        "gr_side_coarsening": "locality-channel projection",
        "idempotence_errors": {
            f"level_{n}": idempotence_error(rung_closure(n)) for n in [1, 2, 3]
        },
        "placeholder": "identity closure with same lift; tests whether commutation alone is toothless",
    }

    thresholds = {
        "built_adequacy_max": 1e-10,
        "placeholder_adequacy_min": 0.25,
        "endpoint_nonfactorization_min": 0.25,
    }
    built_max = max(row["adequacy_residual"] for row in built)
    placeholder_min = min(row["adequacy_residual"] for row in placeholder)
    nonfact_min = min(
        min(row["qm_only_to_rung_residual"], row["gr_only_to_rung_residual"]) for row in emergence
    )
    verdict = {
        "built_passes": built_max <= thresholds["built_adequacy_max"],
        "placeholder_fails": placeholder_min >= thresholds["placeholder_adequacy_min"],
        "nonfactorizing": nonfact_min >= thresholds["endpoint_nonfactorization_min"],
        "candidate_built": (
            built_max <= thresholds["built_adequacy_max"]
            and placeholder_min >= thresholds["placeholder_adequacy_min"]
            and nonfact_min >= thresholds["endpoint_nonfactorization_min"]
        ),
    }

    payload = {
        "construction": construction,
        "thresholds": thresholds,
        "built_transition_diagnostics": built,
        "placeholder_transition_diagnostics": placeholder,
        "emergence_nonfactorization": emergence,
        "observed_residual_range": {
            "built_min": min(row["adequacy_residual"] for row in built),
            "built_max": built_max,
            "placeholder_min": placeholder_min,
            "placeholder_max": max(row["adequacy_residual"] for row in placeholder),
        },
        "no_smuggling_check": {
            "one_hot_set_cover_used": False,
            "literature_program_terms_used": False,
            "target_layer_inserted": False,
            "endpoint_derivation_claimed": False,
            "placeholder_passes": not verdict["placeholder_fails"],
        },
        "verdict": verdict,
        "next_build": "RUNG_2_NEUTRAL_CURRENCY" if verdict["candidate_built"] else "REDIRECT_RUNG_1_MECHANISM",
    }

    (ARTIFACT_DIR / "rung1_construction_step11.json").write_text(
        json.dumps(construction, indent=2) + "\n", encoding="utf-8"
    )
    matrices = {
        "levels": {
            f"level_{n}": {
                "rung_closure": rung_closure(n).tolist(),
                "placeholder_closure": placeholder_closure(n).tolist(),
                "qm_endpoint_closure": qm_endpoint_closure(n).tolist(),
                "gr_endpoint_closure": gr_endpoint_closure(n).tolist(),
            }
            for n in [1, 2, 3]
        },
        "lifts": {
            f"{n}_to_{n + 1}": refinement_lift(n).tolist() for n in [1, 2]
        },
    }
    (ARTIFACT_DIR / "structured_matrices_step11.json").write_text(
        json.dumps(matrices, indent=2) + "\n", encoding="utf-8"
    )
    (ARTIFACT_DIR / "adequacy_output_step11.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )

    with (ARTIFACT_DIR / "adequacy_diagnostic_step11.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "case",
                "transition",
                "commutator_residual",
                "fixedpoint_discrepancy_np1",
                "descent_discrepancy_np1",
                "adequacy_residual",
                "status",
            ],
        )
        writer.writeheader()
        for case, rows in [("built", built), ("placeholder", placeholder)]:
            for row in rows:
                if case == "built":
                    status = "passes" if row["adequacy_residual"] <= thresholds["built_adequacy_max"] else "fails"
                else:
                    status = "fails_as_control" if row["adequacy_residual"] >= thresholds["placeholder_adequacy_min"] else "passes_bad_control"
                writer.writerow(
                    {
                        "case": case,
                        "transition": row["transition"],
                        "commutator_residual": row["commutator_residual"],
                        "fixedpoint_discrepancy_np1": row["fixedpoint_discrepancy_np1"],
                        "descent_discrepancy_np1": row["descent_discrepancy_np1"],
                        "adequacy_residual": row["adequacy_residual"],
                        "status": status,
                    }
                )

    with (ARTIFACT_DIR / "emergence_check_step11.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "level",
                "cells",
                "qm_only_to_rung_residual",
                "gr_only_to_rung_residual",
                "rung_work_norm",
                "status",
            ],
        )
        writer.writeheader()
        for row in emergence:
            status = (
                "strict_nonfactorizing"
                if min(row["qm_only_to_rung_residual"], row["gr_only_to_rung_residual"])
                >= thresholds["endpoint_nonfactorization_min"]
                else "factors_through_endpoint"
            )
            writer.writerow({**row, "status": status})

    txt_lines = [
        "Step 11 RUNG_1_REFINE_FIXEDPOINT construction",
        f"Built adequacy max: {built_max}",
        f"Placeholder adequacy min: {placeholder_min}",
        f"Endpoint nonfactorization min: {nonfact_min}",
        f"Candidate built: {verdict['candidate_built']}",
        f"Next build: {payload['next_build']}",
    ]
    (ARTIFACT_DIR / "adequacy_output_step11.txt").write_text(
        "\n".join(txt_lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
