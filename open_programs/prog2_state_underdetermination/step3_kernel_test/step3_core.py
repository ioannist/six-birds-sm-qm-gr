#!/usr/bin/env python3
"""Pure computations for PROG2 Step 3."""

from __future__ import annotations

import ast
import hashlib
import inspect
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEP1_DIR = HERE.parent / "step1_engine"
STEP2_DIR = HERE.parent / "step2_fiber_states"
PROG3_DIR = REPO_ROOT / "open_programs/prog3_cut_fingerprints/step1_finite_range"
for directory in (STEP2_DIR, STEP1_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from conventions_step3 import (  # noqa: E402
    CONVENTIONS,
    Convention,
    coefficients_and_derivative,
    validate_family,
)
from fiber_loader import FiberDefinition, load_fibers  # noqa: E402
from gauge_library import state_residual  # noqa: E402
from state_entropy import full_entropy_analysis  # noqa: E402
from step1_core import (  # noqa: E402
    TENSOR_REPLICATE,
    TENSOR_SEED_NAMESPACE,
    anti_bypass_audit as step1_anti_bypass_audit,
    derive_tensor_seed,
    state_digest,
    vector_digest,
)
from step2_core import (  # noqa: E402
    compare_entropy_vectors,
)
from survivor_loader import as_tensor_carrier  # noqa: E402
from tensor_engine import (  # noqa: E402
    TensorNetwork,
    build_network,
    physical_leg_id,
    validate_network,
)


ABSOLUTE_RANK_ALLOWANCE = 5e-8
RELATIVE_RANK_ALLOWANCE = 1e-8
STABILITY_ABSOLUTE_ALLOWANCE = 2e-7
STABILITY_RELATIVE_ALLOWANCE = 2e-5
STATE_CONTROL_ALLOWANCE = 5e-10
CONTROL_MEMBERS = (
    ("wheel_W4__b8__leaf_offset0", 47),
    ("K23_bipartite__b6__leaf_offset0", 31),
)


PINNED_DEPENDENCIES = {
    STEP1_DIR / "tensor_engine.py": "52640d2d195d3928ff18c01af59f3a06a72d10fb10f136b69f5a4b2f65f774df",
    STEP1_DIR / "state_entropy.py": "24b27147295af99402193bec760957ef7041b555e5da6875e92524072821df5a",
    STEP1_DIR / "gauge_library.py": "8d0abd47615c2d5e62a6c6a8fd3bb868c7c4cec73ae81d7da19e583b48afcfe1",
    STEP1_DIR / "step1_core.py": "350902bd4c12150c1a5470e336d7a03e4334acbe907dede0d6f5bec71b872733",
    STEP1_DIR / "survivor_loader.py": "9a567e318961009ca69242da64fc268d49c5869dc5485693547126015d9bc78c",
    STEP2_DIR / "capacity_convention.py": "32fc33597268f9df65fc71e97a8932922068fcf6508df0f523ff18c2e545bd97",
    STEP2_DIR / "fiber_loader.py": "4e0de61121dd76d31c3c05e48d5060d174ec674226b55db344af1142fd905e9e",
    STEP2_DIR / "step2_core.py": "231bdd70c0646f0a3ac38644a38de9c1a3b36c1dff4e11841af0b360128b91a6",
    STEP2_DIR / "step3_contract_requirements.md": "345941ce66dee9d28dfef38869661b7bf03e70d89d9b4a6807a1ce35e75a5d59",
    PROG3_DIR / "certified_fibers_step1.csv": "09a5abd737f95cb0429b97a4810fd3294bc675a6d6276e72a799c8b23e2a9298",
    PROG3_DIR / "kernel_intervals_step1.csv": "734c6142ad4e1c474b989080ba8f21b0c10094c0db04f70f9918a3a606cfa760",
    PROG3_DIR / "exact_weights_step1.csv": "6e7e6e321c6e6370c9ca63405809482f9b7502ceaa137a3ab315e124b36b78fc",
}


@dataclass(frozen=True)
class BaseCase:
    carrier: str
    source_seed_provenance: int
    graph: Any
    capacities: tuple[Fraction, ...]
    fibers: tuple[FiberDefinition, ...]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> list[dict[str, Any]]:
    rows = []
    for path, expected in PINNED_DEPENDENCIES.items():
        actual = sha256(path)
        row = {
            "path": str(path.relative_to(REPO_ROOT)),
            "expected_sha256": expected,
            "actual_sha256": actual,
            "passes": actual == expected,
        }
        rows.append(row)
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"dependency pin failure: {rows}")
    return rows


def group_base_cases(fibers: list[FiberDefinition]) -> tuple[BaseCase, ...]:
    grouped: dict[tuple[str, int], list[FiberDefinition]] = {}
    for fiber in fibers:
        grouped.setdefault(
            (fiber.carrier, fiber.source_seed_provenance), []
        ).append(fiber)
    cases = []
    for key, items in grouped.items():
        ordered = tuple(sorted(items, key=lambda item: item.basis_index))
        if tuple(item.basis_index for item in ordered) != tuple(range(len(ordered))):
            raise AssertionError(f"incomplete exact cut-kernel basis for {key}")
        first = ordered[0]
        if any(item.base_capacities != first.base_capacities for item in ordered):
            raise AssertionError(f"base weighting mismatch within {key}")
        cases.append(
            BaseCase(key[0], key[1], first.graph, first.base_capacities, ordered)
        )
    if len(cases) != 13 or sum(len(case.fibers) for case in cases) != 19:
        raise AssertionError("expected 13 base carriers and 19 exact basis fibers")
    return tuple(cases)


def labels_and_dimensions(carrier) -> tuple[tuple[str, ...], tuple[int, ...]]:
    return (
        tuple(leg.label for leg in carrier.boundaries),
        tuple(leg.dimension for leg in carrier.boundaries),
    )


def _raw_contract(network: TensorNetwork) -> np.ndarray:
    """Contract without normalization; entropy machinery is not imported here."""
    validate_network(network)
    internal = {edge.edge_id: index for index, edge in enumerate(network.carrier.edges)}
    offset = len(internal)
    physical = {
        physical_leg_id(boundary.label): offset + index
        for index, boundary in enumerate(network.carrier.boundaries)
    }
    labels = {**internal, **physical}
    operands: list[object] = []
    for vertex in network.carrier.vertices:
        operands.extend(
            [network.tensors[vertex], [labels[leg] for leg in network.leg_orders[vertex]]]
        )
    operands.append(
        [physical[physical_leg_id(boundary.label)] for boundary in network.carrier.boundaries]
    )
    return np.asarray(np.einsum(*operands, optimize="greedy"), dtype=np.complex128)


def dress_network(
    independent: TensorNetwork,
    capacities: tuple[Fraction | float, ...],
    convention: Convention,
) -> TensorNetwork:
    if len(capacities) != len(independent.carrier.edges):
        raise ValueError("capacity count mismatch")
    result = independent.copy()
    for edge, capacity in zip(result.carrier.edges, capacities):
        coefficients, _derivative = coefficients_and_derivative(convention, capacity)
        axis = result.leg_orders[edge.u].index(edge.edge_id)
        shape = [1] * result.tensors[edge.u].ndim
        shape[axis] = convention.dimension
        result.tensors[edge.u] *= coefficients.reshape(shape)
    result.family += "+" + convention.member_id
    validate_network(result)
    return result


def state_and_capacity_derivatives(
    independent: TensorNetwork,
    capacities: tuple[Fraction | float, ...],
    convention: Convention,
) -> tuple[np.ndarray, np.ndarray]:
    dressed = dress_network(independent, capacities, convention)
    raw = _raw_contract(dressed)
    norm = float(np.linalg.norm(raw.ravel()))
    if not np.isfinite(norm) or norm <= 1e-14:
        raise RuntimeError("zero/non-finite contracted state")
    state = raw / norm
    derivatives = []
    for edge, capacity in zip(dressed.carrier.edges, capacities):
        coefficients, coefficient_derivative = coefficients_and_derivative(
            convention, capacity
        )
        tangent_network = dressed.copy()
        axis = tangent_network.leg_orders[edge.u].index(edge.edge_id)
        shape = [1] * tangent_network.tensors[edge.u].ndim
        shape[axis] = convention.dimension
        tangent_network.tensors[edge.u] *= (
            coefficient_derivative / coefficients
        ).reshape(shape)
        raw_derivative = _raw_contract(tangent_network)
        norm_derivative = float(np.real(np.vdot(raw.ravel(), raw_derivative.ravel()))) / norm
        state_derivative = raw_derivative / norm - raw * norm_derivative / norm**2
        derivatives.append(state_derivative)
    return np.asarray(state, dtype=np.complex128), np.asarray(derivatives)


def entropy_jacobian(
    state: np.ndarray, state_derivatives: np.ndarray
) -> tuple[np.ndarray, float, float]:
    """Analytic full entropy Jacobian from reduced-density tangents."""
    dimensions = tuple(state.shape)
    count = len(dimensions)
    edge_count = state_derivatives.shape[0]
    jacobian = np.zeros((1 << count, edge_count), dtype=np.float64)
    maximum_zero_eigenvalue_tangent = 0.0
    maximum_trace_tangent = 0.0
    full_mask = (1 << count) - 1
    for mask in range(1, full_mask):
        complement_mask = full_mask ^ mask
        if mask > complement_mask:
            jacobian[mask] = jacobian[complement_mask]
            continue
        selected = tuple(index for index in range(count) if mask & (1 << index))
        complement = tuple(index for index in range(count) if index not in selected)
        if np.prod([dimensions[index] for index in selected]) > np.prod(
            [dimensions[index] for index in complement]
        ):
            selected, complement = complement, selected
        order = selected + complement
        rows = int(np.prod([dimensions[index] for index in selected], dtype=int))
        columns = int(np.prod([dimensions[index] for index in complement], dtype=int))
        matrix = np.transpose(state, order).reshape(rows, columns)
        derivative_matrices = np.transpose(
            state_derivatives, (0,) + tuple(index + 1 for index in order)
        ).reshape(edge_count, rows, columns)
        density = matrix @ matrix.conj().T
        eigenvalues, eigenvectors = np.linalg.eigh(density)
        eigenvalues = np.maximum(np.real(eigenvalues), 0.0)
        base_in_eigenbasis = eigenvectors.conj().T @ matrix
        derivative_in_eigenbasis = np.einsum(
            "ij,ejk->eik", eigenvectors.conj().T, derivative_matrices,
            optimize=True,
        )
        eigenvalue_derivatives = 2.0 * np.real(
            np.sum(derivative_in_eigenbasis * base_in_eigenbasis.conj()[None, :, :], axis=2)
        )
        maximum_trace_tangent = max(
            maximum_trace_tangent,
            float(np.max(np.abs(np.sum(eigenvalue_derivatives, axis=1)))),
        )
        positive = eigenvalues > 1e-13
        if np.any(~positive):
            maximum_zero_eigenvalue_tangent = max(
                maximum_zero_eigenvalue_tangent,
                float(np.max(np.abs(eigenvalue_derivatives[:, ~positive]))),
            )
        jacobian[mask] = -np.sum(
            eigenvalue_derivatives[:, positive]
            * (np.log(eigenvalues[positive])[None, :] + 1.0),
            axis=1,
        )
    return jacobian, maximum_zero_eigenvalue_tangent, maximum_trace_tangent


def entropy_vector_fast(state: np.ndarray) -> np.ndarray:
    dimensions = tuple(state.shape)
    count = len(dimensions)
    full_mask = (1 << count) - 1
    result = np.zeros(1 << count, dtype=np.float64)
    normalized = state / np.linalg.norm(state.ravel())
    for mask in range(1, full_mask):
        complement_mask = full_mask ^ mask
        if mask > complement_mask:
            result[mask] = result[complement_mask]
            continue
        selected = tuple(index for index in range(count) if mask & (1 << index))
        complement = tuple(index for index in range(count) if index not in selected)
        matrix = np.transpose(normalized, selected + complement).reshape(
            int(np.prod([dimensions[index] for index in selected], dtype=int)), -1
        )
        probabilities = np.linalg.svd(matrix, compute_uv=False) ** 2
        probabilities = probabilities[probabilities > 0.0]
        probabilities /= float(np.sum(probabilities))
        result[mask] = float(-np.sum(probabilities * np.log(probabilities)))
    return result


def state_for_capacities(
    independent: TensorNetwork,
    capacities: tuple[Fraction | float, ...],
    convention: Convention,
) -> np.ndarray:
    raw = _raw_contract(dress_network(independent, capacities, convention))
    return raw / np.linalg.norm(raw.ravel())


def kernel_matrix(case: BaseCase) -> np.ndarray:
    return np.asarray(
        [fiber.direction for fiber in case.fibers], dtype=np.float64
    ).T


def exact_copy_null_basis(case: BaseCase) -> list[tuple[Fraction, ...]]:
    """Exact nullspace in cut-basis coordinates of d log(product c)."""
    row = []
    for fiber in case.fibers:
        row.append(
            sum(
                Fraction(value, 1) / capacity
                for value, capacity in zip(fiber.direction, case.capacities)
            )
        )
    if all(value == 0 for value in row):
        return [
            tuple(Fraction(int(i == j), 1) for i in range(len(row)))
            for j in range(len(row))
        ]
    pivot = next(index for index, value in enumerate(row) if value != 0)
    basis = []
    for index in range(len(row)):
        if index == pivot:
            continue
        vector = [Fraction(0) for _ in row]
        vector[index] = row[pivot]
        vector[pivot] = -row[index]
        scale = max(abs(value) for value in vector)
        basis.append(tuple(value / scale for value in vector))
    return basis


def _direction_step(capacities: tuple[Fraction, ...], direction: np.ndarray) -> float:
    positive_limits = [
        float(capacity) / abs(float(value))
        for capacity, value in zip(capacities, direction)
        if value != 0
    ]
    return min(2.0**-12, 0.05 * min(positive_limits))


def directional_stability(
    independent: TensorNetwork,
    capacities: tuple[Fraction, ...],
    convention: Convention,
    direction: np.ndarray,
    analytic: np.ndarray,
) -> dict[str, Any]:
    h0 = _direction_step(capacities, direction)
    vectors = []
    for divisor in (1.0, 2.0, 4.0):
        step = h0 / divisor
        plus = tuple(float(c) + step * value for c, value in zip(capacities, direction))
        minus = tuple(float(c) - step * value for c, value in zip(capacities, direction))
        plus_entropy = entropy_vector_fast(state_for_capacities(independent, plus, convention))
        minus_entropy = entropy_vector_fast(state_for_capacities(independent, minus, convention))
        vectors.append((plus_entropy - minus_entropy) / (2.0 * step))
    max_norm = max(float(np.max(np.abs(item))) for item in vectors + [analytic])
    allowance = max(
        STABILITY_ABSOLUTE_ALLOWANCE, STABILITY_RELATIVE_ALLOWANCE * max_norm
    )
    last_step_change = float(np.max(np.abs(vectors[-1] - vectors[-2])))
    analytic_residual = float(np.max(np.abs(vectors[-1] - analytic)))
    stable = last_step_change <= allowance and analytic_residual <= 2.0 * allowance
    return {
        "h0": f"{h0:.17g}",
        "h0_over_2": f"{h0 / 2.0:.17g}",
        "h0_over_4": f"{h0 / 4.0:.17g}",
        "analytic_max_abs_response": f"{float(np.max(np.abs(analytic))):.17g}",
        "fd_h0_max_abs_response": f"{float(np.max(np.abs(vectors[0]))):.17g}",
        "fd_h0_over_2_max_abs_response": f"{float(np.max(np.abs(vectors[1]))):.17g}",
        "fd_h0_over_4_max_abs_response": f"{float(np.max(np.abs(vectors[2]))):.17g}",
        "last_step_change": f"{last_step_change:.17g}",
        "analytic_finest_residual": f"{analytic_residual:.17g}",
        "stability_allowance": f"{allowance:.17g}",
        "stable": stable,
    }


def _float_digest(array: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(array).tobytes()).hexdigest()


def evaluate_kernel_tests() -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]
]:
    fibers = load_fibers()
    cases = group_base_cases(fibers)
    intersection_rows: list[dict[str, Any]] = []
    classification_rows: list[dict[str, Any]] = []
    stability_rows: list[dict[str, Any]] = []
    cache: dict[tuple[str, int, str], dict[str, Any]] = {}
    for case in cases:
        cut_basis = kernel_matrix(case)
        for convention in CONVENTIONS:
            carrier = as_tensor_carrier(case.graph, convention.dimension)
            seed = (
                derive_tensor_seed(case.carrier, convention.dimension, TENSOR_REPLICATE)
                if convention.tensor_family == "seeded_random_complex"
                else None
            )
            independent = build_network(carrier, convention.tensor_family, seed)
            state, state_derivatives = state_and_capacity_derivatives(
                independent, case.capacities, convention
            )
            jacobian, zero_tangent, trace_tangent = entropy_jacobian(
                state, state_derivatives
            )
            projected = jacobian @ cut_basis
            singular_values = np.linalg.svd(projected, compute_uv=False)
            sigma_max = float(singular_values[0]) if singular_values.size else 0.0
            rank_allowance = max(
                ABSOLUTE_RANK_ALLOWANCE, RELATIVE_RANK_ALLOWANCE * sigma_max
            )
            numerical_rank = int(np.sum(singular_values > rank_allowance))
            intersection_dimension = cut_basis.shape[1] - numerical_rank
            stability_for_case = []
            for basis_position, fiber in enumerate(case.fibers):
                stability = directional_stability(
                    independent,
                    case.capacities,
                    convention,
                    cut_basis[:, basis_position],
                    projected[:, basis_position],
                )
                stability_row = {
                    "fiber_id": fiber.fiber_id,
                    "carrier": case.carrier,
                    "source_seed_provenance": case.source_seed_provenance,
                    "basis_index": fiber.basis_index,
                    "member_id": convention.member_id,
                    **stability,
                }
                stability_rows.append(stability_row)
                stability_for_case.append(stability_row)
            exact_null_basis = (
                exact_copy_null_basis(case)
                if convention.member_id == "C2_L1"
                else []
            )
            expected_copy_dimension = len(exact_null_basis)
            if convention.member_id == "C2_L1" and (
                intersection_dimension != expected_copy_dimension
            ):
                raise AssertionError(
                    f"copy symmetry/numerical dimension mismatch for {case.carrier}: "
                    f"{intersection_dimension} != {expected_copy_dimension}"
                )
            if intersection_dimension and convention.member_id == "C2_L1":
                for direction_index, coordinates in enumerate(exact_null_basis):
                    exact_edge_direction = tuple(
                        sum(
                            coordinate * Fraction(fiber.direction[edge_index], 1)
                            for coordinate, fiber in zip(coordinates, case.fibers)
                        )
                        for edge_index in range(cut_basis.shape[0])
                    )
                    exact_product_log_derivative = sum(
                        value / capacity
                        for value, capacity in zip(
                            exact_edge_direction, case.capacities
                        )
                    )
                    if exact_product_log_derivative != 0:
                        raise AssertionError("copy-product null direction is not exact")
                    edge_direction = np.asarray(
                        [float(value) for value in exact_edge_direction]
                    )
                    scale = float(np.max(np.abs(edge_direction)))
                    edge_direction /= scale
                    response = jacobian @ edge_direction
                    common_classification = {
                        "carrier": case.carrier,
                        "source_seed_provenance": case.source_seed_provenance,
                        "member_id": convention.member_id,
                        "intersection_direction_index": direction_index,
                        "classification": "SYMMETRY_PROTECTED",
                        "symmetry": "connected_copy_GHZ_product_P_equals_product_edge_capacities",
                        "cut_basis_coordinates_exact": "|".join(map(str, coordinates)),
                        "exact_product_log_derivative": str(
                            exact_product_log_derivative
                        ),
                        "normalized_edge_direction": "|".join(
                            f"{value:.17g}" for value in edge_direction
                        ),
                        "maximum_abs_state_entropy_response": f"{float(np.max(np.abs(response))):.17g}",
                        "continuation_eligible": True,
                        "grade": "ANALYTIC_SYMMETRY_PLUS_DENSE_NUMERICAL_CORROBORATION",
                    }
                    for fiber in case.fibers:
                        classification_rows.append(
                            {
                                "fiber_id": fiber.fiber_id,
                                "basis_index": fiber.basis_index,
                                **common_classification,
                            }
                        )
            elif intersection_dimension:
                classification_rows.append(
                    {
                        "fiber_id": case.fibers[0].fiber_id,
                        "basis_index": case.fibers[0].basis_index,
                        "carrier": case.carrier,
                        "source_seed_provenance": case.source_seed_provenance,
                        "member_id": convention.member_id,
                        "intersection_direction_index": 0,
                        "classification": "NUMERICAL-ARTIFACT",
                        "symmetry": "NONE_IDENTIFIED",
                        "cut_basis_coordinates_exact": "",
                        "normalized_edge_direction": "",
                        "maximum_abs_state_entropy_response": f"{rank_allowance:.17g}",
                        "continuation_eligible": False,
                        "grade": "DENSE_NUMERICAL_EVIDENCE_ONLY",
                    }
                )
            cache[(case.carrier, case.source_seed_provenance, convention.member_id)] = {
                "jacobian": jacobian,
                "state": state,
                "seed": seed,
            }
            common = {
                "carrier": case.carrier,
                "source_seed_provenance": case.source_seed_provenance,
                "member_id": convention.member_id,
                "bond_dimension": convention.dimension,
                "tensor_family": convention.tensor_family,
                "tensor_seed": "" if seed is None else seed,
                "edge_count": len(case.capacities),
                "entropy_subset_count": jacobian.shape[0],
                "exact_cut_kernel_dimension": cut_basis.shape[1],
                "state_restricted_rank": numerical_rank,
                "intersection_dimension": intersection_dimension,
                "rank_allowance": f"{rank_allowance:.17g}",
                "restricted_singular_values": "|".join(
                    f"{value:.17g}" for value in singular_values
                ),
                "jacobian_sha256": _float_digest(jacobian),
                "maximum_zero_eigenvalue_tangent": f"{zero_tangent:.17g}",
                "maximum_trace_tangent": f"{trace_tangent:.17g}",
                "all_imported_basis_step_sweeps_stable": all(
                    bool(row["stable"]) for row in stability_for_case
                ),
                "grade": "DENSE_NUMERICAL_EVIDENCE",
            }
            for fiber in case.fibers:
                intersection_rows.append(
                    {
                        "fiber_id": fiber.fiber_id,
                        "basis_index": fiber.basis_index,
                        **common,
                    }
                )
    if len(intersection_rows) != 95 or len(stability_rows) != 95:
        raise AssertionError("preregistered 19 x 5 census incomplete")
    if not all(row["all_imported_basis_step_sweeps_stable"] for row in intersection_rows):
        raise AssertionError("one or more analytic Jacobians failed the step sweep")
    return intersection_rows, classification_rows, stability_rows


def _axis_basis_swap(tensor: np.ndarray, axis: int) -> np.ndarray:
    return np.take(tensor, (1, 0), axis=axis)


def basis_swap_both_endpoints(network: TensorNetwork, edge_id: str) -> TensorNetwork:
    result = network.copy()
    edge = next(item for item in result.carrier.edges if item.edge_id == edge_id)
    for vertex in (edge.u, edge.v):
        axis = result.leg_orders[vertex].index(edge_id)
        result.tensors[vertex] = _axis_basis_swap(result.tensors[vertex], axis)
    result.family += "+internal_schmidt_basis_swap_X"
    validate_network(result)
    return result


def evaluate_controls() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    convention = next(item for item in CONVENTIONS if item.member_id == "R2_L1")
    cases = {
        (case.carrier, case.source_seed_provenance): case
        for case in group_base_cases(load_fibers())
    }
    rows = []
    comparison_rows = []
    for control_index, key in enumerate(CONTROL_MEMBERS, start=1):
        case = cases[key]
        carrier = as_tensor_carrier(case.graph, 2)
        seed = derive_tensor_seed(case.carrier, 2, TENSOR_REPLICATE)
        independent = build_network(carrier, "seeded_random_complex", seed)
        edge = carrier.edges[0]
        capacity = case.capacities[0]
        if capacity == 1:
            raise AssertionError("preregistered control edge capacity unexpectedly equals one")
        reciprocal = 1 / capacity
        right_capacities = (reciprocal,) + case.capacities[1:]
        left_state = state_for_capacities(independent, case.capacities, convention)
        swapped_independent = basis_swap_both_endpoints(independent, edge.edge_id)
        right_state = state_for_capacities(
            swapped_independent, right_capacities, convention
        )
        labels, dimensions = labels_and_dimensions(carrier)
        comparisons, summary = compare_entropy_vectors(
            left_state,
            right_state,
            labels,
            dimensions,
            f"control_{control_index:02d}",
        )
        comparison_rows.extend(comparisons)
        residual = state_residual(left_state, right_state)
        passes = summary["verdict"] == "COINCIDE" and residual <= STATE_CONTROL_ALLOWANCE
        rows.append(
            {
                "control_id": f"control_{control_index:02d}",
                "carrier": case.carrier,
                "source_seed_provenance": case.source_seed_provenance,
                "edge_id": edge.edge_id,
                "capacity_exact": str(capacity),
                "reciprocal_capacity_exact": str(reciprocal),
                "capacities_distinct": capacity != reciprocal,
                "analytic_relation": "q(1/c)=X q(c) X with X applied on both internal endpoints",
                "state_l2_residual": f"{residual:.17g}",
                "maximum_entropy_difference_nats": summary[
                    "max_entropy_difference_nats"
                ],
                "classifier_verdict": summary["verdict"],
                "state_level_classification": "STATE_LEVEL_GAUGE",
                "underdetermination_candidate": False,
                "left_state_sha256": state_digest(left_state),
                "right_state_sha256": state_digest(right_state),
                "passes": passes,
            }
        )
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"analytic coincidence controls failed: {rows}")
    return rows, comparison_rows


def anti_bypass_audit() -> list[dict[str, Any]]:
    import conventions_step3

    source = Path(conventions_step3.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = ("mincut", "min_cut", "cut_value", "kernel", "fiber_id", "basis_index")
    inherited = step1_anti_bypass_audit(True)
    dress_source = inspect.getsource(dress_network)
    return [
        {
            "gate": "inherited_step1_entropy_anti_bypass",
            "passes": len(inherited) == 10 and all(row["passes"] for row in inherited),
            "evidence": "all 10 closed Step-1 gates recomputed",
        },
        {
            "gate": "convention_import_isolation",
            "passes": not ({"fiber_loader", "exact_engine", "networkx"} & set(imports)),
            "evidence": "|".join(imports),
        },
        {
            "gate": "convention_forbidden_dataflow_scan",
            "passes": not any(token in source for token in forbidden),
            "evidence": "convention accepts only its member record and one edge capacity",
        },
        {
            "gate": "capacity_dressing_entrypoint",
            "passes": "coefficients_and_derivative(convention, capacity)" in dress_source,
            "evidence": "each capacity enters only coefficients_and_derivative then one oriented edge axis",
        },
        {
            "gate": "cut_kernel_separated_from_state_construction",
            "passes": "kernel_matrix" not in dress_source and "direction" not in dress_source,
            "evidence": "cut basis is multiplied with completed entropy Jacobian only after state construction",
        },
    ]


def compute_all() -> dict[str, Any]:
    pins = verify_pins()
    convention_checks = validate_family()
    intersections, classifications, stability = evaluate_kernel_tests()
    controls, control_comparisons = evaluate_controls()
    anti_bypass = anti_bypass_audit()
    if not all(row["passes"] for row in anti_bypass):
        raise AssertionError(f"anti-bypass failure: {anti_bypass}")
    eligible = sum(bool(row["continuation_eligible"]) for row in classifications)
    aggregate = (
        "TRIVIAL-INTERSECTION-EVERYWHERE"
        if not classifications
        else "STEP4-CANDIDATES-PRESENT"
        if eligible
        else "NO-ELIGIBLE-CANDIDATE"
    )
    return {
        "dependency_pins": pins,
        "convention_checks": convention_checks,
        "kernel_intersections": intersections,
        "direction_classifications": classifications,
        "direction_stability": stability,
        "controls": controls,
        "control_entropy_comparisons": control_comparisons,
        "anti_bypass": anti_bypass,
        "aggregate_verdict": aggregate,
    }
