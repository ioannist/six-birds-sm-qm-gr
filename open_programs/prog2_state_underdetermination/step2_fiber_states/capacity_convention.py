#!/usr/bin/env python3
"""Declared injective positive-capacity edge-state convention."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
import sys
from typing import Mapping

import numpy as np

STEP1_DIR = Path(__file__).resolve().parent.parent / "step1_engine"
if str(STEP1_DIR) not in sys.path:
    sys.path.insert(0, str(STEP1_DIR))

from tensor_engine import TensorNetwork, validate_network


CONVENTION_ID = "ordered_qubit_schmidt_c_over_one_plus_c_v1"
EDGE_DIMENSION = 2


def capacity_probability(capacity: Fraction) -> Fraction:
    """The exact ordered first-basis probability p(c)=c/(1+c)."""
    value = Fraction(capacity)
    if value <= 0:
        raise ValueError("edge capacities must be strictly positive")
    return value / (1 + value)


def capacity_schmidt_coefficients(capacity: Fraction) -> np.ndarray:
    """Return coefficients of sqrt(p)|00>+sqrt(1-p)|11>."""
    probability = capacity_probability(capacity)
    return np.asarray(
        [np.sqrt(float(probability)), np.sqrt(float(1 - probability))],
        dtype=np.float64,
    )


def dress_network_by_capacities(
    capacity_independent_network: TensorNetwork,
    capacities: Mapping[str, Fraction],
) -> TensorNetwork:
    """Transport base tensors, inserting one declared state on every edge.

    The stored edge orientation fixes the ordered Schmidt basis.  The diagonal
    coefficient vector is placed on the ``u`` endpoint; contraction with the
    untouched ``v`` endpoint realizes the declared two-qubit edge state.
    """
    expected = {edge.edge_id for edge in capacity_independent_network.carrier.edges}
    if set(capacities) != expected:
        raise ValueError("one and only one capacity is required for every edge")
    result = capacity_independent_network.copy()
    for edge in result.carrier.edges:
        if edge.dimension != EDGE_DIMENSION:
            raise ValueError("this convention is declared only at edge dimension two")
        coefficients = capacity_schmidt_coefficients(Fraction(capacities[edge.edge_id]))
        axis = result.leg_orders[edge.u].index(edge.edge_id)
        broadcast_shape = [1] * result.tensors[edge.u].ndim
        broadcast_shape[axis] = EDGE_DIMENSION
        result.tensors[edge.u] = result.tensors[edge.u] * coefficients.reshape(
            broadcast_shape
        )
    result.family += "+" + CONVENTION_ID
    validate_network(result)
    return result
