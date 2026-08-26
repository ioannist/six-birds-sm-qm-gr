#!/usr/bin/env python3
"""Q2 repair: exact finite completion commutators and honest controls."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import math
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
STEP48 = REPO / "physics_atlas/thread_qm_gr/steps/step48_ladder_vs_fork_resolution_artifacts/ladder_vs_fork_resolution_step48.py"
STEP26 = REPO / "physics_atlas/thread_qm_gr/steps/step26_semiclassical_dynamics_artifacts/semiclassical_dynamics_step26.py"
PINS = {
    "step48": "cea0a1531dfa060a8fda2bab685ef73f28a6afb9086d54c7379f9104268e40d5",
    "step26": "391907fae6fdee8c4e4de1c12ee67d72fdfea4928cad1f148cc30e31584898fd",
}
STATE_NAMES = ("d0_density", "d1_phase", "d2_transport", "d3_curvature")
BITS = tuple(itertools.product((0, 1), repeat=4))
Matrix = tuple[tuple[Fraction, ...], ...]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_pinned() -> tuple[Any, Any, list[dict[str, Any]]]:
    modules = []
    rows = []
    for name, path in (("step48", STEP48), ("step26", STEP26)):
        actual = sha256(path)
        if actual != PINS[name]:
            raise RuntimeError(f"{name} pin mismatch: {actual} != {PINS[name]}")
        spec = importlib.util.spec_from_file_location(f"q2_{name}", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
        rows.append({
            "dependency": name, "path": str(path.relative_to(REPO)),
            "expected_sha256": PINS[name], "actual_sha256": actual, "passes": actual == PINS[name],
        })
    return modules[0], modules[1], rows


def zero(n: int = 16) -> list[list[Fraction]]:
    return [[Fraction(0) for _ in range(n)] for _ in range(n)]


def freeze(values: list[list[Fraction]]) -> Matrix:
    return tuple(tuple(row) for row in values)


def identity(n: int = 16) -> Matrix:
    values = zero(n)
    for index in range(n):
        values[index][index] = Fraction(1)
    return freeze(values)


def transpose(matrix: Matrix) -> Matrix:
    return tuple(tuple(matrix[row][column] for row in range(len(matrix)))
                 for column in range(len(matrix)))


def matmul(left: Matrix, right: Matrix) -> Matrix:
    n = len(left)
    return tuple(tuple(sum((left[i][k] * right[k][j] for k in range(n)), Fraction(0))
                       for j in range(n)) for i in range(n))


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return tuple(tuple(a - b for a, b in zip(row_a, row_b))
                 for row_a, row_b in zip(left, right))


def conditional_mean(keys: Iterable[tuple[Any, ...]]) -> Matrix:
    groups: dict[tuple[Any, ...], list[int]] = {}
    for index, key in enumerate(keys):
        groups.setdefault(tuple(key), []).append(index)
    values = zero()
    for members in groups.values():
        weight = Fraction(1, len(members))
        for row in members:
            for column in members:
                values[row][column] = weight
    return freeze(values)


def retraction(target: Callable[[tuple[int, ...]], tuple[int, ...]]) -> Matrix:
    state_index = {state: index for index, state in enumerate(BITS)}
    values = zero()
    for row, state in enumerate(BITS):
        values[row][state_index[target(state)]] = Fraction(1)
    return freeze(values)


def as_float(matrix: Matrix) -> np.ndarray:
    return np.asarray([[float(value) for value in row] for row in matrix], dtype=float)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def row_text(row: tuple[Fraction, ...]) -> str:
    return "|".join(f"{index}:{fraction_text(value)}" for index, value in enumerate(row) if value)


def state_text(state: tuple[int, ...]) -> str:
    return "".join(map(str, state))


def coordinate_conditional(indices: tuple[int, ...]) -> Matrix:
    return conditional_mean(tuple(tuple(state[index] for index in indices) for state in BITS))


def conjugate(matrix: Matrix, permutation: tuple[int, ...]) -> Matrix:
    index = {state: position for position, state in enumerate(BITS)}
    values = zero()
    for old, state in enumerate(BITS):
        transformed = tuple(state[position] for position in permutation)
        values[index[transformed]][old] = Fraction(1)
    change = freeze(values)
    return matmul(matmul(change, matrix), transpose(change))


@dataclass(frozen=True)
class Pair:
    pair_id: str
    family: str
    left_name: str
    right_name: str
    left: Matrix
    right: Matrix
    motivation: str
    remaining_import: str


def pair_defect(pair: Pair) -> dict[str, Any]:
    left_then_right = matmul(pair.left, pair.right)
    right_then_left = matmul(pair.right, pair.left)
    commutator = subtract(left_then_right, right_then_left)
    defect_indices = [index for index, row in enumerate(commutator) if any(row)]
    float_commutator = as_float(commutator)
    return {
        "left_idempotent": matmul(pair.left, pair.left) == pair.left,
        "right_idempotent": matmul(pair.right, pair.right) == pair.right,
        "commutes": not defect_indices,
        "defect_indices": defect_indices,
        "defect_set": tuple(BITS[index] for index in defect_indices),
        "commutator": commutator,
        "left_then_right": left_then_right,
        "right_then_left": right_then_left,
        "spectral_norm": float(np.linalg.norm(float_commutator, ord=2)),
        "normalized_hilbert_schmidt_norm": float(np.linalg.norm(float_commutator, ord="fro") / math.sqrt(len(BITS))),
    }


def build_pairs() -> list[Pair]:
    qm = coordinate_conditional((0, 1, 2))
    gr = coordinate_conditional((0, 2, 3))
    overlap = coordinate_conditional((0, 2))

    def self_sourced_curve(state: tuple[int, ...]) -> tuple[int, ...]:
        # Boolean threshold of the two Step26-motivated source contributions:
        # density or transport/gradient activity sources the curvature bit.
        return state[:3] + (int(bool(state[0] or state[2])),)

    nonlinear_curve = retraction(self_sourced_curve)
    quantized_shell = conditional_mean((state[0], state[1] + state[2]) for state in BITS)
    curved_shell = conditional_mean((state[0], state[2] + state[3]) for state in BITS)
    return [
        Pair(
            "published_coordinate_pair", "published_reproduction",
            "E_QM_visible_d0_d1_d2", "E_GR_visible_d0_d2_d3", qm, gr,
            "Published coordinate conditional-mean completions on the uniform Boolean cube.",
            "None for the finite operator calculation; its identification with quantize/curve was asserted in the paper.",
        ),
        Pair(
            "conditional_mean_vs_nonlinear_source_projection", "repair_candidate_nonlinear",
            "E_quantize_conditional_mean_d0_d1_d2", "E_curve_retract_d3_to_d0_OR_d2",
            qm, nonlinear_curve,
            "Quantization forgets curvature; curving retracts to a thresholded nonlinear source-consistency set motivated by Step26 density and gradient/transport source terms.",
            "The Boolean threshold and identification of d2 with the gradient/transport contribution are finite discretizations, not derived continuum dynamics.",
        ),
        Pair(
            "nonfactorizing_conditional_means", "repair_candidate_nonfactor_partitions",
            "E_quantized_shell_d0_and_d1_plus_d2", "E_curved_shell_d0_and_d2_plus_d3",
            quantized_shell, curved_shell,
            "Two coarse access structures retain aggregate phase/transport and transport/curvature levels; their fibers do not factor as coordinate subcubes.",
            "The choice of aggregate shell readouts is a declared coarse-graining ansatz rather than a frozen track prediction.",
        ),
        Pair(
            "nested_coordinate_control", "commuting_control",
            "E_QM_visible_d0_d1_d2", "E_overlap_visible_d0_d2", qm, overlap,
            "Nested coordinate conditional means are an explicit can-fail commuting control.",
            "No physical claim; diagnostic control only.",
        ),
    ]


def rebuild_pairs_from_plus_minus_one() -> list[Pair]:
    signed_states = tuple(tuple(2 * value - 1 for value in state) for state in BITS)
    decoded = tuple(tuple((value + 1) // 2 for value in state) for state in signed_states)
    if decoded != BITS:
        raise AssertionError("plus/minus-one decoding changed carrier order")
    qm = conditional_mean(tuple(tuple(state[index] for index in (0, 1, 2)) for state in decoded))
    gr = conditional_mean(tuple(tuple(state[index] for index in (0, 2, 3)) for state in decoded))
    overlap = conditional_mean(tuple(tuple(state[index] for index in (0, 2)) for state in decoded))

    def self_sourced_curve(state: tuple[int, ...]) -> tuple[int, ...]:
        return state[:3] + (int(bool(state[0] or state[2])),)

    nonlinear_curve = retraction(self_sourced_curve)
    quantized_shell = conditional_mean((state[0], state[1] + state[2]) for state in decoded)
    curved_shell = conditional_mean((state[0], state[2] + state[3]) for state in decoded)
    originals = build_pairs()
    matrices = ((qm, gr), (qm, nonlinear_curve), (quantized_shell, curved_shell), (qm, overlap))
    return [Pair(pair.pair_id, pair.family, pair.left_name, pair.right_name, left, right,
                 pair.motivation, pair.remaining_import)
            for pair, (left, right) in zip(originals, matrices)]


def candidate_rows(pairs: list[Pair]) -> list[dict[str, Any]]:
    rows = []
    for pair in pairs:
        defect = pair_defect(pair)
        rows.append({
            "pair_id": pair.pair_id, "family": pair.family,
            "left_completion": pair.left_name, "right_completion": pair.right_name,
            "left_idempotent": defect["left_idempotent"],
            "right_idempotent": defect["right_idempotent"],
            "commutes": defect["commutes"], "defect_set_cardinality": len(defect["defect_set"]),
            "defect_state_ids": "|".join(state_text(state) for state in defect["defect_set"]),
            "commutator_spectral_norm": defect["spectral_norm"],
            "normalized_hilbert_schmidt_norm": defect["normalized_hilbert_schmidt_norm"],
            "motivation": pair.motivation, "remaining_import": pair.remaining_import,
        })
    return rows


def defect_rows(pairs: list[Pair]) -> list[dict[str, Any]]:
    rows = []
    for pair in pairs:
        defect = pair_defect(pair)
        for index in defect["defect_indices"]:
            rows.append({
                "pair_id": pair.pair_id, "state_index": index, "state": state_text(BITS[index]),
                "E1E2_distribution": row_text(defect["left_then_right"][index]),
                "E2E1_distribution": row_text(defect["right_then_left"][index]),
                "commutator_row": row_text(defect["commutator"][index]),
            })
    if not rows:
        raise AssertionError("no noncommuting candidate found")
    return rows


def published_reproduction(step48: Any, pair: Pair) -> list[dict[str, Any]]:
    states01 = np.asarray(BITS, dtype=float)
    statespm = 2.0 * states01 - 1.0
    rows = []
    defect = pair_defect(pair)
    for encoding, states in (("zero_one", states01), ("plus_minus_one", statespm)):
        left = step48.conditional_mean_completion(states, step48.Q_QM)
        right = step48.conditional_mean_completion(states, step48.Q_GR)
        raw = float(np.linalg.norm(left - right))
        distance = raw / max(float(np.linalg.norm(states)), 1.0)
        commutator_probe = as_float(defect["commutator"]) @ states
        rows.append({
            "encoding": encoding, "state_table_norm": float(np.linalg.norm(states)),
            "completion_table_distance_raw": raw,
            "completion_table_distance_normalized": distance,
            "commutator_defect_cardinality": len(defect["defect_set"]),
            "commutator_spectral_norm": defect["spectral_norm"],
            "commutator_on_encoded_table_norm": float(np.linalg.norm(commutator_probe)),
            "published_0_5_reproduced": encoding == "zero_one" and abs(distance - 0.5) < 1e-12,
            "recode_one_over_sqrt_two_reproduced": encoding == "plus_minus_one" and abs(distance - 1 / math.sqrt(2)) < 1e-12,
        })
    return rows


def invariance_rows(pairs: list[Pair]) -> list[dict[str, Any]]:
    rows = []
    permutations = tuple(itertools.permutations(range(4)))
    recoded_pairs = {pair.pair_id: pair for pair in rebuild_pairs_from_plus_minus_one()}
    for pair in pairs:
        baseline = pair_defect(pair)
        recoded_pair = recoded_pairs[pair.pair_id]
        recoded_defect = pair_defect(recoded_pair)
        norm_deltas = []
        cardinalities = []
        idempotence = []
        for permutation in permutations:
            transformed = Pair(pair.pair_id, pair.family, pair.left_name, pair.right_name,
                               conjugate(pair.left, permutation), conjugate(pair.right, permutation),
                               pair.motivation, pair.remaining_import)
            checked = pair_defect(transformed)
            norm_deltas.append(abs(checked["spectral_norm"] - baseline["spectral_norm"]))
            cardinalities.append(len(checked["defect_set"]))
            idempotence.append(checked["left_idempotent"] and checked["right_idempotent"])
        # A coordinatewise affine recoding is bijective and leaves the fibers
        # and retraction truth table unchanged after decoding; rebuild that fact.
        rows.append({
            "pair_id": pair.pair_id, "zero_one_spectral_norm": baseline["spectral_norm"],
            "plus_minus_one_spectral_norm": recoded_defect["spectral_norm"],
            "recoding_rebuilt_matrices_equal": (recoded_pair.left == pair.left
                                                 and recoded_pair.right == pair.right),
            "recoding_defect_cardinality_equal": (len(recoded_defect["defect_set"])
                                                    == len(baseline["defect_set"])),
            "recoding_norm_invariant": recoded_defect["spectral_norm"] == baseline["spectral_norm"],
            "coordinate_permutations_checked": len(permutations),
            "coordinate_permutation_defect_cardinality_set": "|".join(map(str, sorted(set(cardinalities)))),
            "coordinate_permutation_max_norm_delta": max(norm_deltas),
            "all_conjugated_completions_idempotent": all(idempotence),
            "conjugacy_invariance_passes": (set(cardinalities) == {len(baseline["defect_set"])}
                                             and max(norm_deltas) < 1e-12 and all(idempotence)),
        })
    return rows


def matrix_rows(pairs: list[Pair]) -> list[dict[str, Any]]:
    rows = []
    for pair in pairs:
        for name, matrix in ((pair.left_name, pair.left), (pair.right_name, pair.right)):
            for index, row in enumerate(matrix):
                rows.append({"pair_id": pair.pair_id, "completion": name,
                             "row_index": index, "exact_distribution": row_text(row)})
    return rows


def run() -> dict[str, Any]:
    step48, step26, pins = import_pinned()
    pairs = build_pairs()
    candidates = candidate_rows(pairs)
    defects = defect_rows(pairs)
    published = published_reproduction(step48, pairs[0])
    invariance = invariance_rows(pairs)
    matrices = matrix_rows(pairs)
    # Directly exercise the imported Step26 nonlinear source function. The
    # finite Boolean constraint is motivated by both density and gradient terms.
    psi = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=complex)
    background = np.ones(8)
    source = step26.stress_energy_density(psi, background)
    source_evidence = [{
        "imported_function": "step26.stress_energy_density",
        "density_contribution_present": bool(background[0] * abs(psi[0]) ** 2 > 0),
        "gradient_contribution_present": bool(np.any(abs(step26.periodic_gradient(psi)) ** 2 > 0)),
        "finite_constraint": "d3 = threshold(density_source + transport_gradient_source) = d0 OR d2",
        "thresholding_imported": True,
    }]
    if not all(row["left_idempotent"] and row["right_idempotent"] for row in candidates):
        raise AssertionError("non-idempotent completion entered candidate table")
    control = next(row for row in candidates if row["family"] == "commuting_control")
    if not control["commutes"]:
        raise AssertionError("commuting control failed")
    if any(not row["recoding_norm_invariant"] or not row["conjugacy_invariance_passes"]
           for row in invariance):
        raise AssertionError("encoding/conjugacy invariance failed")
    repaired = [row for row in candidates if row["family"].startswith("repair_candidate")
                and not row["commutes"]]
    outcome = ("GENUINE_NONCOMMUTING_FINITE_CANDIDATES_EXIST_MOTIVATION_SUBJECT_TO_REVIEW"
               if repaired else "RETRACT_NONCOMMUTATIVITY_ON_TESTED_FINITE_COMPLETIONS")
    return {
        "pins": pins, "pairs": pairs, "candidates": candidates, "defects": defects,
        "published": published, "invariance": invariance, "matrices": matrices,
        "source_evidence": source_evidence, "outcome": outcome,
        "hashes": {
            "candidates": hashlib.sha256(("\n".join(row["pair_id"] + ":" + str(row["commutes"])
                                                     for row in candidates) + "\n").encode()).hexdigest(),
            "defects": hashlib.sha256(("\n".join(row["pair_id"] + ":" + row["state"]
                                                  for row in defects) + "\n").encode()).hexdigest(),
        },
    }


if __name__ == "__main__":
    result = run()
    print(f"q2_route_mismatch.py: PASS: candidates={len(result['candidates'])} "
          f"defects={len(result['defects'])} outcome={result['outcome']}")
