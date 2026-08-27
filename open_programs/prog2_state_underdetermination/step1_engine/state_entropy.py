#!/usr/bin/env python3
"""Dense numerical entropy calculations from a contracted boundary state.

This module intentionally knows nothing about graphs, capacities, or cuts.  It
is the audited anti-bypass boundary for PROG2 Step 1.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np


SCHMIDT_PROBABILITY_TOL = 1e-13
STATE_NORM_TOL = 1e-15


@dataclass(frozen=True)
class EntropyDiagnostics:
    entropy_nats: float
    truncated_entropy_nats: float
    numerical_rank: int
    spectrum_dimension: int
    discarded_probability_mass: float
    truncation_entropy_error_bound_nats: float
    probability_tolerance: float


def normalize_state(state: np.ndarray) -> np.ndarray:
    vector = np.asarray(state, dtype=np.complex128)
    norm = float(np.linalg.norm(vector.ravel()))
    if not np.isfinite(norm) or norm <= STATE_NORM_TOL:
        raise ValueError("boundary state has zero or non-finite norm")
    return vector / norm


def subset_labels(labels: Sequence[str], mask: int) -> tuple[str, ...]:
    return tuple(label for index, label in enumerate(labels) if mask & (1 << index))


def schmidt_probabilities(
    state: np.ndarray,
    physical_dimensions: Sequence[int],
    subset: Iterable[int],
) -> np.ndarray:
    """Return every strictly positive numerical Schmidt probability."""
    dimensions = tuple(int(value) for value in physical_dimensions)
    if tuple(state.shape) != dimensions:
        raise ValueError(f"state shape {state.shape} does not match {dimensions}")
    selected = tuple(sorted(set(int(index) for index in subset)))
    if any(index < 0 or index >= len(dimensions) for index in selected):
        raise IndexError(selected)
    complement = tuple(index for index in range(len(dimensions)) if index not in selected)
    normalized = normalize_state(state)
    if not selected or not complement:
        return np.array([1.0], dtype=float)
    matrix = np.transpose(normalized, selected + complement).reshape(
        int(np.prod([dimensions[index] for index in selected], dtype=int)),
        int(np.prod([dimensions[index] for index in complement], dtype=int)),
    )
    singular_values = np.linalg.svd(matrix, compute_uv=False)
    probabilities = np.real_if_close(singular_values * singular_values).astype(float)
    probabilities = probabilities[probabilities > 0.0]
    probabilities /= float(np.sum(probabilities))
    return probabilities


def _binary_entropy(probability: float) -> float:
    if probability <= 0.0 or probability >= 1.0:
        return 0.0
    return float(
        -probability * np.log(probability)
        - (1.0 - probability) * np.log1p(-probability)
    )


def entropy_diagnostics(
    state: np.ndarray,
    physical_dimensions: Sequence[int],
    subset: Iterable[int],
    probability_tolerance: float = SCHMIDT_PROBABILITY_TOL,
) -> EntropyDiagnostics:
    """Return the untruncated entropy and explicit truncation accountability.

    The reported ``entropy_nats`` includes every strictly positive numerical
    Schmidt probability.  ``probability_tolerance`` is used only to report the
    rank and the hypothetical error from dropping smaller probabilities.
    """
    if probability_tolerance < 0.0:
        raise ValueError("probability tolerance must be nonnegative")
    probabilities = schmidt_probabilities(state, physical_dimensions, subset)
    entropy = float(-np.sum(probabilities * np.log(probabilities)))
    retained = probabilities[probabilities > probability_tolerance]
    discarded_mass = float(np.sum(probabilities[probabilities <= probability_tolerance]))
    if retained.size:
        retained = retained / float(np.sum(retained))
        truncated_entropy = float(-np.sum(retained * np.log(retained)))
    else:
        truncated_entropy = 0.0
    if abs(truncated_entropy) <= np.finfo(float).tiny:
        truncated_entropy = 0.0
    dimension = int(probabilities.size)
    error_bound = _binary_entropy(discarded_mass)
    if dimension > 1:
        error_bound += discarded_mass * float(np.log(dimension - 1))
    return EntropyDiagnostics(
        entropy_nats=0.0 if abs(entropy) <= np.finfo(float).tiny else entropy,
        truncated_entropy_nats=truncated_entropy,
        numerical_rank=int(retained.size),
        spectrum_dimension=dimension,
        discarded_probability_mass=discarded_mass,
        truncation_entropy_error_bound_nats=error_bound,
        probability_tolerance=float(probability_tolerance),
    )


def entropy_for_subset(
    state: np.ndarray,
    physical_dimensions: Sequence[int],
    subset: Iterable[int],
) -> float:
    return entropy_diagnostics(state, physical_dimensions, subset).entropy_nats


def full_entropy_analysis(
    state: np.ndarray,
    boundary_labels: Sequence[str],
    physical_dimensions: Sequence[int],
    probability_tolerance: float = SCHMIDT_PROBABILITY_TOL,
) -> tuple[
    dict[tuple[str, ...], float],
    dict[tuple[str, ...], EntropyDiagnostics],
]:
    labels = tuple(boundary_labels)
    dimensions = tuple(int(value) for value in physical_dimensions)
    if len(labels) != len(dimensions):
        raise ValueError("one physical dimension is required per boundary label")
    vector: dict[tuple[str, ...], float] = {}
    diagnostics: dict[tuple[str, ...], EntropyDiagnostics] = {}
    for mask in range(1 << len(labels)):
        region = subset_labels(labels, mask)
        indices = tuple(index for index in range(len(labels)) if mask & (1 << index))
        diagnostic = entropy_diagnostics(
            state, dimensions, indices, probability_tolerance
        )
        vector[region] = diagnostic.entropy_nats
        diagnostics[region] = diagnostic
    return vector, diagnostics


def full_entropy_vector(
    state: np.ndarray,
    boundary_labels: Sequence[str],
    physical_dimensions: Sequence[int],
) -> dict[tuple[str, ...], float]:
    """Compute all ``2**len(boundary_labels)`` von Neumann entropies."""
    return full_entropy_analysis(
        state, boundary_labels, physical_dimensions
    )[0]


def complement_symmetry_residual(
    vector: dict[tuple[str, ...], float], labels: Sequence[str]
) -> float:
    full = frozenset(labels)
    return max(
        abs(value - vector[tuple(label for label in labels if label not in set(region))])
        for region, value in vector.items()
        if frozenset(region).issubset(full)
    )


def all_regions(labels: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    return tuple(
        tuple(region)
        for size in range(len(labels) + 1)
        for region in itertools.combinations(labels, size)
    )
