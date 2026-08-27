#!/usr/bin/env python3
"""Preregistered Step-3 capacity-to-state convention family."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import numpy as np


@dataclass(frozen=True)
class Convention:
    member_id: str
    dimension: int
    tensor_family: str
    alpha: int
    beta: int | None
    spectrum_family: str


CONVENTIONS = (
    Convention("R2_L1", 2, "seeded_random_complex", 1, None, "logistic"),
    Convention("R2_L2", 2, "seeded_random_complex", 2, None, "logistic"),
    Convention("C2_L1", 2, "structured_copy", 1, None, "logistic"),
    Convention("R3_S11", 3, "seeded_random_complex", 1, 1, "three_level"),
    Convention("R3_S21", 3, "seeded_random_complex", 2, 1, "three_level"),
)


def probabilities_and_derivative(
    convention: Convention, capacity: Fraction | float
) -> tuple[np.ndarray, np.ndarray]:
    """Return ordered probabilities and their analytic c derivative."""
    c = float(capacity)
    if not np.isfinite(c) or c <= 0.0:
        raise ValueError("capacity must be positive and finite")
    if convention.spectrum_family == "logistic":
        power = c**convention.alpha
        denominator = 1.0 + power
        probability = power / denominator
        derivative = (
            convention.alpha * c ** (convention.alpha - 1) / denominator**2
        )
        q = np.asarray([probability, 1.0 - probability], dtype=np.float64)
        dq = np.asarray([derivative, -derivative], dtype=np.float64)
    elif convention.spectrum_family == "three_level":
        if convention.beta is None:
            raise AssertionError("three-level convention requires beta")
        raw = np.asarray(
            [c**convention.alpha, 1.0, c ** (-convention.beta)],
            dtype=np.float64,
        )
        log_derivative = np.asarray(
            [convention.alpha / c, 0.0, -convention.beta / c],
            dtype=np.float64,
        )
        q = raw / float(np.sum(raw))
        dq = q * (log_derivative - float(np.dot(q, log_derivative)))
    else:
        raise ValueError(convention.spectrum_family)
    if len(q) != convention.dimension or np.min(q) <= 0.0:
        raise AssertionError("invalid convention spectrum")
    if abs(float(np.sum(q)) - 1.0) > 1e-14 or abs(float(np.sum(dq))) > 1e-12:
        raise AssertionError("spectrum normalization derivative failed")
    return q, dq


def coefficients_and_derivative(
    convention: Convention, capacity: Fraction | float
) -> tuple[np.ndarray, np.ndarray]:
    probabilities, derivative = probabilities_and_derivative(convention, capacity)
    coefficients = np.sqrt(probabilities)
    return coefficients, derivative / (2.0 * coefficients)


def convention_by_id(member_id: str) -> Convention:
    return next(item for item in CONVENTIONS if item.member_id == member_id)


def validate_family() -> list[dict[str, object]]:
    """Check normalization, analytic derivatives, and sampled injectivity."""
    rows = []
    samples = (Fraction(1, 3), Fraction(2, 3), Fraction(1), Fraction(3, 2), Fraction(3))
    for convention in CONVENTIONS:
        digests = []
        derivative_residual = 0.0
        for capacity in samples:
            q, dq = probabilities_and_derivative(convention, capacity)
            epsilon = 1e-6 * float(capacity)
            q_plus, _ = probabilities_and_derivative(convention, float(capacity) + epsilon)
            q_minus, _ = probabilities_and_derivative(convention, float(capacity) - epsilon)
            finite = (q_plus - q_minus) / (2.0 * epsilon)
            derivative_residual = max(
                derivative_residual, float(np.max(np.abs(finite - dq)))
            )
            digests.append(tuple(float(value) for value in q))
        injective = len(set(digests)) == len(samples)
        row = {
            "member_id": convention.member_id,
            "dimension": convention.dimension,
            "tensor_family": convention.tensor_family,
            "alpha": convention.alpha,
            "beta": "" if convention.beta is None else convention.beta,
            "sampled_ordered_spectra_distinct": injective,
            "maximum_analytic_derivative_check_residual": f"{derivative_residual:.17g}",
            "passes": injective and derivative_residual < 2e-9,
        }
        rows.append(row)
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"convention-family check failed: {rows}")
    return rows
