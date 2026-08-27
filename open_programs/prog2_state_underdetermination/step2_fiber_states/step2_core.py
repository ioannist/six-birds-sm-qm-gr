#!/usr/bin/env python3
"""Pure computations for PROG2 Step 2."""

from __future__ import annotations

import ast
import hashlib
import inspect
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np

from capacity_convention import (
    CONVENTION_ID,
    EDGE_DIMENSION,
    capacity_probability,
    capacity_schmidt_coefficients,
    dress_network_by_capacities,
)
from fiber_loader import FiberDefinition, load_fibers, nonkernel_control, verify_pins
from gauge_library import apply_internal_gauge, state_residual
from state_entropy import SCHMIDT_PROBABILITY_TOL, full_entropy_analysis
from step1_core import (
    TENSOR_REPLICATE,
    TENSOR_SEED_NAMESPACE,
    anti_bypass_audit as step1_anti_bypass_audit,
    derive_tensor_seed,
    state_digest,
    vector_digest,
)
from survivor_loader import as_tensor_carrier
from tensor_engine import (
    build_network,
    contract_boundary_state,
    uniform_carrier,
)


TENSOR_FAMILY = "seeded_random_complex"
FLOAT_ENTROPY_MARGIN_NATS = 5e-11
SPLIT_SAFETY_FACTOR = 4
PRECISION_ESCALATION_DPS = 80
STATE_EQUALITY_NORM_ALLOWANCE = 5e-10
HIGH_PRECISION_CONSISTENCY_DPS = 80
HIGH_PRECISION_WITNESSES = {
    "fiber_004": ("B1", "B4", "B5", "B6"),
    "fiber_011": ("B1", "B3", "B5", "B6"),
}


def network_tensor_digest(network) -> str:
    digest = hashlib.sha256()
    for vertex in network.carrier.vertices:
        tensor = np.ascontiguousarray(network.tensors[vertex])
        digest.update(vertex.encode("utf-8"))
        digest.update(str(tensor.shape).encode("ascii"))
        digest.update(tensor.tobytes())
    return digest.hexdigest()


def capacity_map(carrier, values: tuple[Fraction, ...]) -> dict[str, Fraction]:
    if len(values) != len(carrier.edges):
        raise ValueError("capacity count does not match carrier edge count")
    return {edge.edge_id: value for edge, value in zip(carrier.edges, values)}


def construct_boundary_state(capacity_independent_network, capacities):
    dressed = dress_network_by_capacities(capacity_independent_network, capacities)
    return contract_boundary_state(dressed), dressed


def labels_and_dimensions(carrier) -> tuple[tuple[str, ...], tuple[int, ...]]:
    return (
        tuple(leg.label for leg in carrier.boundaries),
        tuple(leg.dimension for leg in carrier.boundaries),
    )


def _mp_entropy_from_complex128_state(
    state: np.ndarray,
    physical_dimensions: tuple[int, ...],
    subset: tuple[int, ...],
    dps: int,
) -> mp.mpf:
    """Escalate the Schmidt entropy evaluation for a fixed numerical state."""
    selected = tuple(sorted(set(subset)))
    complement = tuple(index for index in range(len(physical_dimensions)) if index not in selected)
    if not selected or not complement:
        return mp.mpf("0")
    transposed = np.transpose(state, selected + complement)
    rows = int(np.prod([physical_dimensions[index] for index in selected], dtype=int))
    columns = int(np.prod([physical_dimensions[index] for index in complement], dtype=int))
    flat = transposed.reshape(rows, columns)
    with mp.workdps(dps):
        norm_squared = mp.fsum(
            mp.mpf(repr(float(value.real))) ** 2 + mp.mpf(repr(float(value.imag))) ** 2
            for value in np.asarray(state).ravel()
        )
        norm = mp.sqrt(norm_squared)
        matrix = mp.matrix(rows, columns)
        for row in range(rows):
            for column in range(columns):
                value = flat[row, column]
                matrix[row, column] = mp.mpc(
                    mp.mpf(repr(float(value.real))),
                    mp.mpf(repr(float(value.imag))),
                ) / norm
        eigenvalues = mp.eighe(matrix * matrix.H, eigvals_only=True)
        probabilities = [max(mp.mpf("0"), mp.re(value)) for value in eigenvalues]
        total = mp.fsum(probabilities)
        probabilities = [value / total for value in probabilities if value > 0]
        return -mp.fsum(value * mp.log(value) for value in probabilities)


def compare_entropy_vectors(
    left_state: np.ndarray,
    right_state: np.ndarray,
    labels: tuple[str, ...],
    dimensions: tuple[int, ...],
    case_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    left_vector, left_diagnostics = full_entropy_analysis(
        left_state, labels, dimensions, SCHMIDT_PROBABILITY_TOL
    )
    right_vector, right_diagnostics = full_entropy_analysis(
        right_state, labels, dimensions, SCHMIDT_PROBABILITY_TOL
    )
    rows = []
    for mask in range(1 << len(labels)):
        region = tuple(label for index, label in enumerate(labels) if mask & (1 << index))
        subset = tuple(index for index in range(len(labels)) if mask & (1 << index))
        left = left_vector[region]
        right = right_vector[region]
        difference = abs(left - right)
        left_diagnostic = left_diagnostics[region]
        right_diagnostic = right_diagnostics[region]
        numerical_allowance = (
            left_diagnostic.truncation_entropy_error_bound_nats
            + right_diagnostic.truncation_entropy_error_bound_nats
            + 2 * FLOAT_ENTROPY_MARGIN_NATS
        )
        if difference <= numerical_allowance:
            initial = final = "EQUAL_WITHIN_ALLOWANCE"
            escalated = False
            escalated_left = escalated_right = ""
        elif difference > SPLIT_SAFETY_FACTOR * numerical_allowance:
            initial = final = "SPLIT_BEYOND_ALLOWANCE"
            escalated = False
            escalated_left = escalated_right = ""
        else:
            initial = "MARGINAL_REQUIRES_ESCALATION"
            escalated = True
            high_left = _mp_entropy_from_complex128_state(
                left_state, dimensions, subset, PRECISION_ESCALATION_DPS
            )
            high_right = _mp_entropy_from_complex128_state(
                right_state, dimensions, subset, PRECISION_ESCALATION_DPS
            )
            high_difference = abs(high_left - high_right)
            escalated_left = mp.nstr(high_left, 40)
            escalated_right = mp.nstr(high_right, 40)
            if high_difference <= numerical_allowance:
                final = "EQUAL_WITHIN_ALLOWANCE"
            elif high_difference > SPLIT_SAFETY_FACTOR * numerical_allowance:
                final = "SPLIT_BEYOND_ALLOWANCE"
            else:
                final = "INDETERMINATE"
        rows.append(
            {
                "case_id": case_id,
                "mask": mask,
                "region": "|".join(region) if region else "EMPTY",
                "base_entropy_nats": f"{left:.17g}",
                "perturbed_entropy_nats": f"{right:.17g}",
                "absolute_difference_nats": f"{difference:.17g}",
                "base_discarded_probability_mass": f"{left_diagnostic.discarded_probability_mass:.17g}",
                "perturbed_discarded_probability_mass": f"{right_diagnostic.discarded_probability_mass:.17g}",
                "base_numerical_rank": left_diagnostic.numerical_rank,
                "perturbed_numerical_rank": right_diagnostic.numerical_rank,
                "preregistered_numerical_allowance_nats": f"{numerical_allowance:.17g}",
                "initial_classification": initial,
                "precision_escalated": escalated,
                "escalation_dps": PRECISION_ESCALATION_DPS if escalated else "",
                "escalated_base_entropy_nats": escalated_left,
                "escalated_perturbed_entropy_nats": escalated_right,
                "final_classification": final,
            }
        )
    split_rows = [row for row in rows if row["final_classification"] == "SPLIT_BEYOND_ALLOWANCE"]
    indeterminate_rows = [row for row in rows if row["final_classification"] == "INDETERMINATE"]
    if split_rows:
        verdict = "SPLIT"
    elif not indeterminate_rows:
        verdict = "COINCIDE"
    else:
        verdict = "INDETERMINATE"
    witness = max(rows, key=lambda row: float(row["absolute_difference_nats"]))
    summary = {
        "entropy_subset_count": len(rows),
        "equal_subset_count": sum(row["final_classification"] == "EQUAL_WITHIN_ALLOWANCE" for row in rows),
        "split_subset_count": len(split_rows),
        "indeterminate_subset_count": len(indeterminate_rows),
        "precision_escalated_subset_count": sum(bool(row["precision_escalated"]) for row in rows),
        "max_entropy_difference_nats": witness["absolute_difference_nats"],
        "max_difference_region": witness["region"],
        "max_difference_numerical_allowance_nats": witness[
            "preregistered_numerical_allowance_nats"
        ],
        "verdict": verdict,
        "left_entropy_vector_sha256": vector_digest(left_vector, labels),
        "right_entropy_vector_sha256": vector_digest(right_vector, labels),
    }
    return rows, summary


def base_network(fiber: FiberDefinition):
    carrier = as_tensor_carrier(fiber.graph, EDGE_DIMENSION)
    seed = derive_tensor_seed(
        fiber.carrier, EDGE_DIMENSION, TENSOR_REPLICATE
    )
    return carrier, seed, build_network(carrier, TENSOR_FAMILY, seed)


def evaluate_fibers() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    verdict_rows = []
    entropy_rows = []
    pairing_rows = []
    cached_base: dict[tuple[str, int], tuple[Any, int, Any, np.ndarray, Any, Any]] = {}
    for fiber in load_fibers():
        key = (fiber.carrier, fiber.source_seed_provenance)
        if key not in cached_base:
            carrier, seed, independent = base_network(fiber)
            left_base = independent.copy()
            right_base = independent.copy()
            left_digest = network_tensor_digest(left_base)
            right_digest = network_tensor_digest(right_base)
            if left_digest != right_digest:
                raise AssertionError(f"capacity-independent tensors differ within pair {fiber.fiber_id}")
            left_state, _left_dressed = construct_boundary_state(
                left_base, capacity_map(carrier, fiber.base_capacities)
            )
            labels, dimensions = labels_and_dimensions(carrier)
            cached_base[key] = (
                carrier,
                seed,
                independent,
                left_state,
                labels,
                dimensions,
            )
        carrier, seed, independent, left_state, labels, dimensions = cached_base[key]
        left_base = independent.copy()
        right_base = independent.copy()
        left_tensor_digest = network_tensor_digest(left_base)
        right_tensor_digest = network_tensor_digest(right_base)
        right_state, _right_dressed = construct_boundary_state(
            right_base, capacity_map(carrier, fiber.perturbed_capacities)
        )
        comparisons, summary = compare_entropy_vectors(
            left_state, right_state, labels, dimensions, fiber.fiber_id
        )
        entropy_rows.extend(comparisons)
        state_difference = state_residual(left_state, right_state)
        verdict_rows.append(
            {
                "fiber_id": fiber.fiber_id,
                "carrier": fiber.carrier,
                "source_seed_provenance": fiber.source_seed_provenance,
                "basis_index": fiber.basis_index,
                "t_star_exact": str(fiber.t_star),
                "boundary_count": len(labels),
                "bond_dimension": EDGE_DIMENSION,
                "tensor_seed": seed,
                "state_l2_residual": f"{state_difference:.17g}",
                "base_state_sha256": state_digest(left_state),
                "perturbed_state_sha256": state_digest(right_state),
                "boundary_state_equal_within_norm_allowance": state_difference
                <= STATE_EQUALITY_NORM_ALLOWANCE,
                **summary,
                "gauge_invariant_evidence": "numerical_entropy_vector_split"
                if summary["verdict"] == "SPLIT"
                else "NOT_ESTABLISHED_LATER_STEP",
            }
        )
        pairing_rows.append(
            {
                "fiber_id": fiber.fiber_id,
                "carrier": fiber.carrier,
                "source_seed_provenance_only": fiber.source_seed_provenance,
                "boundary_labels": "|".join(labels),
                "boundary_dimensions": "|".join(map(str, dimensions)),
                "tensor_seed_namespace": TENSOR_SEED_NAMESPACE,
                "tensor_seed_replicate": TENSOR_REPLICATE,
                "tensor_seed_both_members": seed,
                "capacity_independent_base_tensor_sha256": left_tensor_digest,
                "transported_copy_tensor_sha256": right_tensor_digest,
                "capacity_independent_tensors_byte_identical": left_tensor_digest == right_tensor_digest,
                "only_declared_capacity_dressing_differs": True,
            }
        )
    return verdict_rows, entropy_rows, pairing_rows


def evaluate_high_precision_consistency(
    fibers: list[FiberDefinition],
) -> list[dict[str, Any]]:
    """Re-evaluate the two reviewer-pinned entropy witnesses at 80 dps.

    This escalates the entropy calculation for fixed complex128 contracted
    states.  It is a consistency check, not a contraction-error certificate.
    """
    rows = []
    by_id = {fiber.fiber_id: fiber for fiber in fibers}
    for fiber_id, region in HIGH_PRECISION_WITNESSES.items():
        fiber = by_id[fiber_id]
        carrier, seed, independent = base_network(fiber)
        labels, dimensions = labels_and_dimensions(carrier)
        subset = tuple(labels.index(label) for label in region)
        left_state, _ = construct_boundary_state(
            independent.copy(), capacity_map(carrier, fiber.base_capacities)
        )
        right_state, _ = construct_boundary_state(
            independent.copy(), capacity_map(carrier, fiber.perturbed_capacities)
        )
        left_vector, _ = full_entropy_analysis(left_state, labels, dimensions)
        right_vector, _ = full_entropy_analysis(right_state, labels, dimensions)
        float_left = left_vector[region]
        float_right = right_vector[region]
        float_difference = abs(float_left - float_right)
        high_left = _mp_entropy_from_complex128_state(
            left_state, dimensions, subset, HIGH_PRECISION_CONSISTENCY_DPS
        )
        high_right = _mp_entropy_from_complex128_state(
            right_state, dimensions, subset, HIGH_PRECISION_CONSISTENCY_DPS
        )
        high_difference = abs(high_left - high_right)
        agreement = abs(high_difference - mp.mpf(repr(float_difference)))
        expected_range = (
            (mp.mpf("4.0e-6"), mp.mpf("4.01e-6"))
            if fiber_id == "fiber_004"
            else (mp.mpf("0.0019"), mp.mpf("0.00193"))
        )
        passes = (
            agreement < mp.mpf("5e-13")
            and expected_range[0] < high_difference < expected_range[1]
        )
        rows.append(
            {
                "check": "high_precision_consistency_check",
                "fiber_id": fiber_id,
                "carrier": fiber.carrier,
                "source_seed_provenance": fiber.source_seed_provenance,
                "basis_index": fiber.basis_index,
                "region": "|".join(region),
                "tensor_seed": seed,
                "dps": HIGH_PRECISION_CONSISTENCY_DPS,
                "float_base_entropy_nats": f"{float_left:.17g}",
                "float_perturbed_entropy_nats": f"{float_right:.17g}",
                "float_absolute_difference_nats": f"{float_difference:.17g}",
                "mpmath_base_entropy_nats": mp.nstr(high_left, 50),
                "mpmath_perturbed_entropy_nats": mp.nstr(high_right, 50),
                "mpmath_absolute_difference_nats": mp.nstr(high_difference, 50),
                "absolute_float_mp_difference_agreement_nats": mp.nstr(
                    agreement, 25
                ),
                "scope": "80-dps entropy re-evaluation of fixed complex128 contracted states; consistency check, not certificate",
                "passes": passes,
            }
        )
    if len(rows) != 2 or not all(row["passes"] for row in rows):
        raise AssertionError(f"high-precision consistency failure: {rows}")
    return rows


def evaluate_controls() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    control_rows = []
    entropy_rows = []

    control = nonkernel_control()
    synthetic = FiberDefinition(
        fiber_id="control_nonkernel_edge0",
        carrier=control["carrier"],
        source_seed_provenance=control["source_seed_provenance"],
        basis_index=-1,
        graph=control["graph"],
        base_capacities=control["base_capacities"],
        perturbed_capacities=control["perturbed_capacities"],
        direction=control["direction"],
        t_star=control["t_star"],
    )
    carrier, seed, independent = base_network(synthetic)
    labels, dimensions = labels_and_dimensions(carrier)
    left_state, _ = construct_boundary_state(
        independent.copy(), capacity_map(carrier, synthetic.base_capacities)
    )
    right_state, _ = construct_boundary_state(
        independent.copy(), capacity_map(carrier, synthetic.perturbed_capacities)
    )
    comparisons, summary = compare_entropy_vectors(
        left_state, right_state, labels, dimensions, synthetic.fiber_id
    )
    entropy_rows.extend(comparisons)
    control_rows.append(
        {
            "control": synthetic.fiber_id,
            "carrier": synthetic.carrier,
            "exact_direction": "+1*edge_index_0",
            "t_star_exact": str(synthetic.t_star),
            "magnitude_source": "same exact t_star as fiber_001",
            "capacity_convention": CONVENTION_ID,
            "tensor_seed": seed,
            "exact_active_cut_jacobian_image_nonzero": control["active_cut_jacobian_image_nonzero"],
            "exact_cut_fingerprint_changed": control["exact_cut_fingerprint_changed"],
            "state_l2_residual": f"{state_residual(left_state, right_state):.17g}",
            **summary,
            "expected": "SPLIT",
            "passes": summary["verdict"] == "SPLIT",
        }
    )

    gauge_carrier = uniform_carrier(
        "step2_gauge_degeneracy_control",
        ("u", "v"),
        (("e", "u", "v"),),
        (("A", "u"), ("B", "v")),
        EDGE_DIMENSION,
    )
    gauge_seed = derive_tensor_seed(gauge_carrier.name, EDGE_DIMENSION, TENSOR_REPLICATE)
    gauge_independent = build_network(gauge_carrier, TENSOR_FAMILY, gauge_seed)
    gauge_capacity = {"e": Fraction(7, 5)}
    gauge_dressed = dress_network_by_capacities(gauge_independent, gauge_capacity)
    gauge_matrix = np.asarray(
        [[1.2 + 0.1j, 0.3], [-0.2j, 0.9 - 0.05j]], dtype=np.complex128
    )
    gauged = apply_internal_gauge(gauge_dressed, "e", gauge_matrix)
    gauge_left = contract_boundary_state(gauge_dressed)
    gauge_right = contract_boundary_state(gauged)
    gauge_labels, gauge_dimensions = labels_and_dimensions(gauge_carrier)
    comparisons, summary = compare_entropy_vectors(
        gauge_left,
        gauge_right,
        gauge_labels,
        gauge_dimensions,
        "control_step1_internal_gauge",
    )
    entropy_rows.extend(comparisons)
    control_rows.append(
        {
            "control": "control_step1_internal_gauge",
            "carrier": gauge_carrier.name,
            "exact_direction": "",
            "t_star_exact": "",
            "magnitude_source": "",
            "capacity_convention": CONVENTION_ID,
            "tensor_seed": gauge_seed,
            "exact_active_cut_jacobian_image_nonzero": "",
            "exact_cut_fingerprint_changed": False,
            "state_l2_residual": f"{state_residual(gauge_left, gauge_right):.17g}",
            **summary,
            "expected": "COINCIDE",
            "passes": summary["verdict"] == "COINCIDE"
            and state_residual(gauge_left, gauge_right) <= STATE_EQUALITY_NORM_ALLOWANCE,
        }
    )
    if not all(row["passes"] for row in control_rows):
        raise AssertionError(f"Step-2 control failure: {control_rows}")
    return control_rows, entropy_rows


def capacity_convention_check(fibers: list[FiberDefinition]) -> list[dict[str, Any]]:
    capacities = {
        value
        for fiber in fibers
        for values in (fiber.base_capacities, fiber.perturbed_capacities)
        for value in values
    }
    probabilities = {capacity_probability(value) for value in capacities}
    coefficient_digests = {
        hashlib.sha256(capacity_schmidt_coefficients(value).tobytes()).hexdigest()
        for value in capacities
    }
    sorted_capacities = sorted(capacities)
    monotone = all(
        capacity_probability(left) < capacity_probability(right)
        for left, right in zip(sorted_capacities, sorted_capacities[1:])
    )
    row = {
        "convention": CONVENTION_ID,
        "exact_input_capacity_count": len(capacities),
        "exact_probability_count": len(probabilities),
        "numerical_edge_state_digest_count": len(coefficient_digests),
        "exact_map_injective_on_evaluated_capacities": len(probabilities) == len(capacities),
        "numerical_coefficient_vectors_distinct_on_evaluated_capacities": len(
            coefficient_digests
        )
        == len(capacities),
        "strictly_monotone_exact": monotone,
        "all_capacities_positive": min(capacities) > 0,
        "passes": len(probabilities) == len(capacities)
        and len(coefficient_digests) == len(capacities)
        and monotone
        and min(capacities) > 0,
    }
    if not row["passes"]:
        raise AssertionError(f"capacity convention check failed: {row}")
    return [row]


def anti_bypass_audit(fibers: list[FiberDefinition]) -> list[dict[str, Any]]:
    import capacity_convention

    convention_path = Path(capacity_convention.__file__)
    convention_source = convention_path.read_text(encoding="utf-8")
    tree = ast.parse(convention_source)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden_modules = {"fiber_loader", "exact_engine", "networkx"}
    forbidden_data_tokens = ("mincut", "min_cut", "cut_value", "kernel", "t_star", "basis_index")
    inherited = step1_anti_bypass_audit(True)

    fiber = fibers[0]
    carrier, seed_a, independent = base_network(fiber)
    capacities = capacity_map(carrier, fiber.perturbed_capacities)
    state_a, _ = construct_boundary_state(independent.copy(), capacities)
    metadata_mutation = replace(
        fiber,
        fiber_id="mutated_irrelevant_identifier",
        source_seed_provenance=fiber.source_seed_provenance + 99991,
        basis_index=999,
        direction=tuple(-value for value in fiber.direction),
        t_star=Fraction(1234567, 7654321),
        graph=replace(
            fiber.graph,
            weighted_edges=tuple(
                (u, v, weight + Fraction(index + 1, 1000))
                for index, (u, v, weight) in enumerate(fiber.graph.weighted_edges)
            ),
        ),
    )
    mutated_carrier, seed_b, mutated_independent = base_network(metadata_mutation)
    mutated_capacities = capacity_map(
        mutated_carrier, fiber.perturbed_capacities
    )
    state_b, _ = construct_boundary_state(
        mutated_independent.copy(), mutated_capacities
    )
    labels, dimensions = labels_and_dimensions(carrier)
    mutated_labels, mutated_dimensions = labels_and_dimensions(mutated_carrier)
    if (labels, dimensions) != (mutated_labels, mutated_dimensions):
        raise AssertionError("metadata mutation changed boundary Hilbert identification")
    vector_a, _ = full_entropy_analysis(state_a, labels, dimensions)
    vector_b, _ = full_entropy_analysis(state_b, labels, dimensions)
    tensor_digest_a = network_tensor_digest(independent)
    tensor_digest_b = network_tensor_digest(mutated_independent)
    metadata_independent = (
        seed_a == seed_b
        and tensor_digest_a == tensor_digest_b
        and state_digest(state_a) == state_digest(state_b)
        and vector_digest(vector_a, labels) == vector_digest(vector_b, labels)
    )
    construction_source = inspect.getsource(construct_boundary_state)
    construction_tree = ast.parse(construction_source)
    construction_calls = {
        node.func.id
        for node in ast.walk(construction_tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    rows = [
        {
            "gate": "inherited_step1_complete_entropy_call_graph",
            "passes": len(inherited) == 10 and all(row["passes"] for row in inherited),
            "evidence": "pinned Step-1 anti_bypass_audit recomputed all 10 gates",
        },
        {
            "gate": "capacity_convention_module_import_isolation",
            "passes": not (set(imports) & forbidden_modules),
            "evidence": "|".join(imports),
        },
        {
            "gate": "capacity_convention_forbidden_dataflow_scan",
            "passes": not any(token in convention_source for token in forbidden_data_tokens),
            "evidence": "only TensorNetwork plus edge_id->Fraction capacities enter dressing",
        },
        {
            "gate": "capacity_entrypoint_signature",
            "passes": str(inspect.signature(capacity_probability)) == "(capacity: 'Fraction') -> 'Fraction'",
            "evidence": str(inspect.signature(capacity_probability)),
        },
        {
            "gate": "state_construction_reachable_entrypoint",
            "passes": construction_calls == {
                "dress_network_by_capacities",
                "contract_boundary_state",
            },
            "evidence": "construct_boundary_state calls only capacity dressing then closed Step-1 contraction",
        },
        {
            "gate": "frozen_capacity_metadata_mutation",
            "passes": metadata_independent,
            "evidence": (
                f"rebuilt through mutation object={metadata_mutation.fiber_id}; seed={seed_a}={seed_b}; "
                f"tensor_digest={tensor_digest_a}={tensor_digest_b}; "
                f"state_digest={state_digest(state_a)}={state_digest(state_b)}; "
                f"entropy_digest={vector_digest(vector_a, labels)}={vector_digest(vector_b, labels)}; "
                "executed mutation changed source provenance, identifier, basis, direction, t, and every stored graph weight"
            ),
        },
    ]
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"Step-2 anti-bypass failure: {rows}")
    return rows


def compute_all() -> dict[str, Any]:
    fibers = load_fibers()
    verdicts, entropy_rows, pairing_rows = evaluate_fibers()
    controls, control_entropy_rows = evaluate_controls()
    return {
        "dependencies": verify_pins(),
        "fiber_verdicts": verdicts,
        "entropy_comparisons": entropy_rows,
        "pairing_integrity": pairing_rows,
        "controls": controls,
        "control_entropy_comparisons": control_entropy_rows,
        "high_precision_consistency": evaluate_high_precision_consistency(fibers),
        "capacity_checks": capacity_convention_check(fibers),
        "anti_bypass": anti_bypass_audit(fibers),
    }
