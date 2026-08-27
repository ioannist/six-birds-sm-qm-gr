#!/usr/bin/env python3
"""Pure computations for the PROG2 Step-1 engine and controls."""

from __future__ import annotations

import hashlib
import inspect
import json
import csv
from dataclasses import replace
from pathlib import Path
from typing import Any

import numpy as np

from gauge_library import (
    apply_boundary_local_unitary,
    apply_internal_gauge,
    merge_parallel_edges,
    merge_series_vertex,
    state_residual,
)
from state_entropy import (
    SCHMIDT_PROBABILITY_TOL,
    complement_symmetry_residual,
    entropy_diagnostics,
    full_entropy_analysis,
    full_entropy_vector,
)
from survivor_loader import HERE, REPO_ROOT, PINS as SURVIVOR_PINS, as_tensor_carrier, reconstruct_reduced_graphs, sha256
from tensor_engine import BoundaryLeg, Carrier, Edge, build_network, contract_boundary_state, uniform_carrier


CONTROL_TOL = 2e-12
SURVIVOR_DIMS = (2, 3, 4)
RANDOM_FAMILY = "seeded_random_complex"
STRUCTURED_FAMILY = "structured_copy"
TENSOR_SEED_NAMESPACE = "prog2_step2_tensor_seed_v1"
TENSOR_REPLICATE = 0

REFERENCE_PINS = {
    REPO_ROOT / "physics_atlas/thread_qm_gr/steps/step41_tensor_network_rt_bound_artifacts/tensor_network_rt_bound_step41.py": "014441ae0dcd309e47a8d3fbba206ca884e5f58995dda9b2fc6dd0f76c783a26",
    REPO_ROOT / "physics_atlas/thread_qm_gr/steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py": "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08",
    REPO_ROOT / "physics_atlas/thread_qm_gr/steps/step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py": "61f28d10e8170a9f37ac71a711b6d30c3dac9b4f014b8e634c70ba2166a47052",
    HERE / "legacy_seed_history_step1.csv": "62447825674a2dd70b71a7f3349110685777c281d4c4e4efa88ff6f9a738ba11",
}


def verify_all_pins() -> list[dict[str, Any]]:
    rows = []
    for path, expected in {**SURVIVOR_PINS, **REFERENCE_PINS}.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"pin mismatch for {path}: {actual} != {expected}")
        rows.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "passes": True,
                "usage": "imported" if path in SURVIVOR_PINS and path.name.startswith("active_cut") else "read_reference_or_data",
            }
        )
    return rows


def entropy_rows(case_id: str, labels: tuple[str, ...], vector: dict[tuple[str, ...], float]) -> list[dict[str, Any]]:
    rows = []
    for mask in range(1 << len(labels)):
        region = tuple(label for index, label in enumerate(labels) if mask & (1 << index))
        rows.append(
            {
                "case_id": case_id,
                "mask": mask,
                "region": "|".join(region) if region else "EMPTY",
                "entropy_nats": f"{vector[region]:.15g}",
            }
        )
    return rows


def vector_residual(
    left: dict[tuple[str, ...], float], right: dict[tuple[str, ...], float]
) -> float:
    if left.keys() != right.keys():
        return float("inf")
    return max(abs(left[key] - right[key]) for key in left)


def vector_digest(vector: dict[tuple[str, ...], float], labels: tuple[str, ...]) -> str:
    payload = "\n".join(
        f"{mask}:{vector[tuple(label for index, label in enumerate(labels) if mask & (1 << index))]:.17g}"
        for mask in range(1 << len(labels))
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def state_digest(state: np.ndarray) -> str:
    payload = "\n".join(
        f"{value.real:.17g},{value.imag:.17g}" for value in np.asarray(state).ravel()
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def derive_tensor_seed(carrier_name: str, dimension: int, replicate: int) -> int:
    payload = json.dumps(
        [TENSOR_SEED_NAMESPACE, carrier_name, int(dimension), int(replicate)],
        separators=(",", ":"),
    )
    return int.from_bytes(hashlib.sha256(payload.encode("utf-8")).digest()[:8], "big")


def _labels_and_dims(carrier) -> tuple[tuple[str, ...], tuple[int, ...]]:
    return (
        tuple(leg.label for leg in carrier.boundaries),
        tuple(leg.dimension for leg in carrier.boundaries),
    )


def legacy_seed_history() -> dict[tuple[str, int, int], dict[str, str]]:
    path = HERE / "legacy_seed_history_step1.csv"
    if sha256(path) != REFERENCE_PINS[path]:
        raise RuntimeError("legacy seed-history pin mismatch")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 39:
        raise AssertionError(f"expected 39 frozen legacy seed rows, found {len(rows)}")
    return {
        (row["carrier"], int(row["source_seed_provenance"]), int(row["bond_dimension"])): row
        for row in rows
    }


def compute_controls() -> dict[str, Any]:
    entangled_carrier = uniform_carrier(
        "injective_entangled_edge",
        ("u", "v"),
        (("e", "u", "v"),),
        (("A", "u"), ("B", "v")),
        2,
    )
    product_carrier = uniform_carrier(
        "injective_disconnected_product",
        ("u", "v"),
        (),
        (("A", "u"), ("B", "v")),
        2,
    )
    entangled_network = build_network(entangled_carrier, STRUCTURED_FAMILY)
    product_network = build_network(product_carrier, STRUCTURED_FAMILY)
    entangled_state = contract_boundary_state(entangled_network)
    product_state = contract_boundary_state(product_network)
    labels = ("A", "B")
    dimensions = (2, 2)
    entangled_vector = full_entropy_vector(entangled_state, labels, dimensions)
    product_vector = full_entropy_vector(product_state, labels, dimensions)

    gauge_matrix = np.array([[1.2 + 0.1j, 0.3], [-0.2j, 0.9 - 0.05j]], dtype=np.complex128)
    gauged_network = apply_internal_gauge(entangled_network, "e", gauge_matrix)
    gauged_state = contract_boundary_state(gauged_network)
    gauged_vector = full_entropy_vector(gauged_state, labels, dimensions)

    chain_carrier = uniform_carrier(
        "series_chain",
        ("left", "middle", "right"),
        (("e0", "left", "middle"), ("e1", "middle", "right")),
        (("A", "left"), ("B", "right")),
        2,
    )
    chain_network = build_network(chain_carrier, RANDOM_FAMILY, 7101)
    chain_state = contract_boundary_state(chain_network)
    series_merged = merge_series_vertex(chain_network, "middle")
    series_state = contract_boundary_state(series_merged)

    parallel_carrier = uniform_carrier(
        "parallel_pair",
        ("left", "right"),
        (("p0", "left", "right"), ("p1", "left", "right")),
        (("A", "left"), ("B", "right")),
        2,
    )
    parallel_network = build_network(parallel_carrier, RANDOM_FAMILY, 7102)
    parallel_state = contract_boundary_state(parallel_network)
    parallel_merged = merge_parallel_edges(parallel_network, "p0", "p1", "p_fused")
    parallel_merged_state = contract_boundary_state(parallel_merged)

    nonsymmetric_unitary = np.array(
        [[0.0, 1.0j], [1.0, 0.0]], dtype=np.complex128
    )
    boundary_rotated = apply_boundary_local_unitary(
        entangled_network, "A", nonsymmetric_unitary
    )
    rotated_state = contract_boundary_state(boundary_rotated)
    # Independent conventional left action: expected[i,b] = sum_j U[i,j] psi[j,b].
    predicted_rotated_state = np.einsum(
        "ij,jb->ib", nonsymmetric_unitary, entangled_state
    )
    rotated_vector = full_entropy_vector(rotated_state, labels, dimensions)

    unitary_is_nonsymmetric = bool(
        np.linalg.norm(nonsymmetric_unitary - nonsymmetric_unitary.T) > 0.5
    )
    gauge_rows = [
        {
            "move": "internal_leg_g_g_inverse",
            "relation": "boundary_state_equal",
            "state_residual": f"{state_residual(entangled_state, gauged_state):.15g}",
            "entropy_vector_residual": f"{vector_residual(entangled_vector, gauged_vector):.15g}",
            "independent_expected_contraction": "",
            "nonsymmetric_complex_unitary": "",
            "passes": state_residual(entangled_state, gauged_state) <= CONTROL_TOL,
        },
        {
            "move": "series_tensor_merge",
            "relation": "boundary_state_equal",
            "state_residual": f"{state_residual(chain_state, series_state):.15g}",
            "entropy_vector_residual": f"{vector_residual(full_entropy_vector(chain_state, labels, dimensions), full_entropy_vector(series_state, labels, dimensions)):.15g}",
            "independent_expected_contraction": "",
            "nonsymmetric_complex_unitary": "",
            "passes": state_residual(chain_state, series_state) <= CONTROL_TOL,
        },
        {
            "move": "parallel_index_product_merge",
            "relation": "boundary_state_equal",
            "state_residual": f"{state_residual(parallel_state, parallel_merged_state):.15g}",
            "entropy_vector_residual": f"{vector_residual(full_entropy_vector(parallel_state, labels, dimensions), full_entropy_vector(parallel_merged_state, labels, dimensions)):.15g}",
            "independent_expected_contraction": "",
            "nonsymmetric_complex_unitary": "",
            "passes": state_residual(parallel_state, parallel_merged_state) <= CONTROL_TOL,
        },
        {
            "move": "single_boundary_local_unitary",
            "relation": "state_related_by_explicit_local_unitary",
            "state_residual": f"{state_residual(rotated_state, predicted_rotated_state):.15g}",
            "entropy_vector_residual": f"{vector_residual(entangled_vector, rotated_vector):.15g}",
            "independent_expected_contraction": "np.einsum('ij,jb->ib', U, psi)",
            "nonsymmetric_complex_unitary": unitary_is_nonsymmetric,
            "passes": state_residual(rotated_state, predicted_rotated_state) <= CONTROL_TOL
            and unitary_is_nonsymmetric,
        },
    ]
    if not all(row["passes"] for row in gauge_rows):
        raise AssertionError(f"gauge verification failure: {gauge_rows}")

    schmidt_entangled = int(np.sum(np.linalg.svd(entangled_state, compute_uv=False) > 1e-12))
    schmidt_product = int(np.sum(np.linalg.svd(product_state, compute_uv=False) > 1e-12))
    injective_difference = vector_residual(entangled_vector, product_vector)
    if schmidt_entangled != 2 or schmidt_product != 1 or injective_difference <= 0.5:
        raise AssertionError("injective calibration did not distinguish the states")

    control_summary = [
        {
            "control": "injective_nonvacuousness",
            "case_left": entangled_carrier.name,
            "case_right": product_carrier.name,
            "max_entropy_vector_difference": f"{injective_difference:.15g}",
            "left_schmidt_rank_A_B": schmidt_entangled,
            "right_schmidt_rank_A_B": schmidt_product,
            "gauge_library_related": False,
            "reason": "Schmidt rank across A|B is invariant under internal presentation moves and boundary local unitaries",
            "passes": True,
        },
        {
            "control": "degeneracy_internal_gauge",
            "case_left": entangled_carrier.name,
            "case_right": entangled_carrier.name + "__g_g_inverse",
            "max_entropy_vector_difference": f"{vector_residual(entangled_vector, gauged_vector):.15g}",
            "left_schmidt_rank_A_B": schmidt_entangled,
            "right_schmidt_rank_A_B": schmidt_entangled,
            "gauge_library_related": True,
            "reason": "Explicit g and inverse(g) cancel on the contracted edge",
            "passes": vector_residual(entangled_vector, gauged_vector) <= CONTROL_TOL,
        },
    ]
    return {
        "control_summary": control_summary,
        "gauge_rows": gauge_rows,
        "entropy_rows": (
            entropy_rows(entangled_carrier.name, labels, entangled_vector)
            + entropy_rows(product_carrier.name, labels, product_vector)
            + entropy_rows(entangled_carrier.name + "__g_g_inverse", labels, gauged_vector)
        ),
        "headline": {
            "ln2": float(np.log(2.0)),
            "entangled_vector": [entangled_vector[()], entangled_vector[("A",)], entangled_vector[("B",)], entangled_vector[("A", "B")]],
            "product_vector": [product_vector[()], product_vector[("A",)], product_vector[("B",)], product_vector[("A", "B")]],
            "gauged_vector": [gauged_vector[()], gauged_vector[("A",)], gauged_vector[("B",)], gauged_vector[("A", "B")]],
            "gauge_state_residual": state_residual(entangled_state, gauged_state),
        },
    }


def compute_engine_checks() -> list[dict[str, Any]]:
    heterogeneous = Carrier(
        name="heterogeneous_edge_dimensions",
        vertices=("left", "middle", "right"),
        edges=(
            Edge("d2", "left", "middle", 2, "source_capacity_alpha"),
            Edge("d3", "middle", "right", 3, "source_capacity_beta"),
        ),
        boundaries=(BoundaryLeg("A", "left", 2), BoundaryLeg("B", "right", 3)),
    )
    network = build_network(heterogeneous, RANDOM_FAMILY, 7201)
    state = contract_boundary_state(network)
    vector = full_entropy_vector(state, ("A", "B"), (2, 3))
    row = {
        "check": "heterogeneous_per_edge_bond_dimensions",
        "edge_dimensions": "2|3",
        "boundary_dimensions": "2|3",
        "contracted_state_shape": "x".join(map(str, state.shape)),
        "entropy_subset_count": len(vector),
        "complement_symmetry_residual": f"{complement_symmetry_residual(vector, ('A', 'B')):.15g}",
        "maximum_entropy": f"{max(vector.values()):.15g}",
        "passes": state.shape == (2, 3) and len(vector) == 4,
    }
    if not row["passes"]:
        raise AssertionError(f"heterogeneous bond-dimension check failed: {row}")
    return [row]


def compute_survivor_census() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    history = legacy_seed_history()
    for source_row, graph, analysis, moves in reconstruct_reduced_graphs():
        cases = [(2, STRUCTURED_FAMILY, None)] + [
            (
                dimension,
                RANDOM_FAMILY,
                derive_tensor_seed(
                    source_row["carrier"], dimension, TENSOR_REPLICATE
                ),
            )
            for dimension in SURVIVOR_DIMS
        ]
        for dimension, family, tensor_seed in cases:
            carrier = as_tensor_carrier(graph, dimension)
            network = build_network(carrier, family, tensor_seed)
            state = contract_boundary_state(network)
            labels, physical_dimensions = _labels_and_dims(carrier)
            vector, diagnostics = full_entropy_analysis(
                state, labels, physical_dimensions
            )
            if family == RANDOM_FAMILY:
                historical = history[
                    (source_row["carrier"], int(source_row["seed"]), dimension)
                ]
                legacy_tensor_seed = int(historical["legacy_coupled_tensor_seed"])
                legacy_corrected_digest = historical[
                    "legacy_seed_corrected_entropy_vector_sha256"
                ]
                legacy_pre_fix_digest = historical[
                    "legacy_pre_fix_entropy_vector_sha256"
                ]
                legacy_state_digest = historical["legacy_state_sha256"]
            else:
                legacy_tensor_seed = None
                legacy_corrected_digest = ""
                legacy_pre_fix_digest = ""
                legacy_state_digest = ""
            new_digest = vector_digest(vector, labels)
            new_state_digest = state_digest(state)
            rows.append(
                {
                    "carrier": source_row["carrier"],
                    "source_seed": int(source_row["seed"]),
                    "named_regression": source_row["named_regression"],
                    "reduced_vertex_count": len(graph.nodes),
                    "reduced_edge_count": len(graph.edges),
                    "residual_deficiency": len(graph.edges) - analysis.rank,
                    "boundary_count": len(labels),
                    "bond_dimension": dimension,
                    "tensor_family": family,
                    "tensor_seed_namespace": TENSOR_SEED_NAMESPACE if tensor_seed is not None else "",
                    "tensor_seed_replicate": TENSOR_REPLICATE if tensor_seed is not None else "",
                    "tensor_seed": "" if tensor_seed is None else tensor_seed,
                    "legacy_tensor_seed": "" if legacy_tensor_seed is None else legacy_tensor_seed,
                    "boundary_state_entries": int(np.prod(state.shape, dtype=int)),
                    "entropy_subset_count": len(vector),
                    "expected_subset_count": 1 << len(labels),
                    "complement_symmetry_residual": f"{complement_symmetry_residual(vector, labels):.15g}",
                    "minimum_entropy": f"{min(vector.values()):.15g}",
                    "maximum_entropy": f"{max(vector.values()):.15g}",
                    "entropy_vector_sha256": new_digest,
                    "legacy_pre_fix_entropy_vector_sha256": legacy_pre_fix_digest,
                    "legacy_seed_corrected_entropy_vector_sha256": legacy_corrected_digest,
                    "entropy_digest_changed_from_legacy": "" if not legacy_pre_fix_digest else legacy_pre_fix_digest != new_digest,
                    "entropy_digest_changed_from_legacy_seed_same_policy": "" if not legacy_corrected_digest else legacy_corrected_digest != new_digest,
                    "state_sha256": new_state_digest,
                    "legacy_state_sha256": legacy_state_digest,
                    "state_digest_changed_from_legacy_seed": "" if not legacy_state_digest else legacy_state_digest != new_state_digest,
                    "maximum_discarded_probability_mass": f"{max(item.discarded_probability_mass for item in diagnostics.values()):.15g}",
                    "maximum_truncation_entropy_error_bound_nats": f"{max(item.truncation_entropy_error_bound_nats for item in diagnostics.values()):.15g}",
                    "minimum_numerical_rank": min(item.numerical_rank for item in diagnostics.values()),
                    "maximum_numerical_rank": max(item.numerical_rank for item in diagnostics.values()),
                    "schmidt_probability_tolerance": SCHMIDT_PROBABILITY_TOL,
                    "closure_moves": "|".join(move["move"] for move in moves),
                    "tractable": True,
                }
            )
    return rows


def compute_numerical_accountability() -> list[dict[str, Any]]:
    epsilon = 1e-14
    state = np.diag(
        [np.sqrt(1.0 - epsilon), np.sqrt(epsilon)]
    ).astype(np.complex128)
    analytic_entropy = float(
        -(1.0 - epsilon) * np.log1p(-epsilon) - epsilon * np.log(epsilon)
    )
    rows = []
    for tolerance in (0.0, 1e-15, 1e-14, 1e-13, 1e-12):
        diagnostic = entropy_diagnostics(state, (2, 2), (0,), tolerance)
        observed_truncation_error = abs(
            diagnostic.entropy_nats - diagnostic.truncated_entropy_nats
        )
        rows.append(
            {
                "case": "two_coefficient_small_schmidt_weight",
                "small_probability": f"{epsilon:.17g}",
                "probability_tolerance": f"{tolerance:.17g}",
                "reported_untruncated_entropy_nats": f"{diagnostic.entropy_nats:.17g}",
                "analytic_entropy_nats": f"{analytic_entropy:.17g}",
                "truncated_entropy_nats": f"{diagnostic.truncated_entropy_nats:.17g}",
                "numerical_rank": diagnostic.numerical_rank,
                "spectrum_dimension": diagnostic.spectrum_dimension,
                "discarded_probability_mass": f"{diagnostic.discarded_probability_mass:.17g}",
                "observed_truncation_error_nats": f"{observed_truncation_error:.17g}",
                "truncation_entropy_error_bound_nats": f"{diagnostic.truncation_entropy_error_bound_nats:.17g}",
                "bound_covers_observed_error": observed_truncation_error
                <= diagnostic.truncation_entropy_error_bound_nats + 1e-27,
                "passes": diagnostic.entropy_nats > 3e-13
                and abs(diagnostic.entropy_nats - analytic_entropy) < 2e-16,
            }
        )
    if not all(row["passes"] and row["bound_covers_observed_error"] for row in rows):
        raise AssertionError(f"small-Schmidt numerical regression failed: {rows}")
    return rows


def _selected_survivor():
    return next(
        item
        for item in reconstruct_reduced_graphs()
        if item[0]["carrier"] == "K23_bipartite__b6__leaf_offset0"
        and int(item[0]["seed"]) == 31
    )


def compute_survivor_scale_control() -> list[dict[str, Any]]:
    source_row, graph, _analysis, _moves = _selected_survivor()
    carrier = as_tensor_carrier(graph, 2)
    seed = derive_tensor_seed(source_row["carrier"], 2, TENSOR_REPLICATE)
    network = build_network(carrier, RANDOM_FAMILY, seed)
    state = contract_boundary_state(network)
    labels, dimensions = _labels_and_dims(carrier)
    vector = full_entropy_vector(state, labels, dimensions)
    boundary_vertices = {leg.vertex for leg in carrier.boundaries}
    mutated_vertex = next(
        vertex for vertex in carrier.vertices if vertex not in boundary_vertices
    )
    mutated_network = network.copy()
    mutated_tensor = mutated_network.tensors[mutated_vertex].copy()
    mutated_tensor.flat[0] += 0.75 + 0.25j
    mutated_tensor /= np.linalg.norm(mutated_tensor.ravel())
    mutated_network.tensors[mutated_vertex] = mutated_tensor
    mutated_state = contract_boundary_state(mutated_network)
    mutated_vector = full_entropy_vector(mutated_state, labels, dimensions)
    differences = {region: abs(vector[region] - mutated_vector[region]) for region in vector}
    witness_region = max(differences, key=differences.get)
    maximum_difference = differences[witness_region]
    row = {
        "control": "survivor_scale_same_boundary_mutation",
        "carrier": source_row["carrier"],
        "source_seed_provenance": source_row["seed"],
        "bond_dimension": 2,
        "boundary_count": len(labels),
        "boundary_labels": "|".join(labels),
        "tensor_seed_namespace": TENSOR_SEED_NAMESPACE,
        "tensor_seed": seed,
        "mutation": f"{mutated_vertex}.flat[0] += 0.75+0.25j; renormalize vertex tensor",
        "base_state_sha256": state_digest(state),
        "mutated_state_sha256": state_digest(mutated_state),
        "base_entropy_sha256": vector_digest(vector, labels),
        "mutated_entropy_sha256": vector_digest(mutated_vector, labels),
        "witness_region": "|".join(witness_region) if witness_region else "EMPTY",
        "maximum_entropy_vector_difference": f"{maximum_difference:.15g}",
        "gauge_invariant_obstruction": "full entropy vector differs; every library move preserves it",
        "passes": maximum_difference > 1e-6,
    }
    if not row["passes"]:
        raise AssertionError(f"survivor-scale control did not distinguish: {row}")
    return [row]


def compute_seed_independence_regression() -> list[dict[str, Any]]:
    source_row, graph, _analysis, _moves = _selected_survivor()
    carrier = as_tensor_carrier(graph, 2)
    seed = derive_tensor_seed(source_row["carrier"], 2, TENSOR_REPLICATE)
    baseline_network = build_network(carrier, RANDOM_FAMILY, seed)
    baseline_state = contract_boundary_state(baseline_network)
    labels, dimensions = _labels_and_dims(carrier)
    baseline_vector = full_entropy_vector(baseline_state, labels, dimensions)
    mutated_carrier = replace(
        carrier,
        edges=tuple(
            replace(edge, source_weight=f"mutated_capacity_provenance_{index}")
            for index, edge in enumerate(carrier.edges)
        ),
    )
    mutated_network = build_network(mutated_carrier, RANDOM_FAMILY, seed)
    mutated_state = contract_boundary_state(mutated_network)
    mutated_vector = full_entropy_vector(mutated_state, labels, dimensions)
    row = {
        "regression": "source_seed_and_weight_provenance_independence",
        "carrier": source_row["carrier"],
        "original_source_seed_provenance": source_row["seed"],
        "mutated_source_seed_provenance": int(source_row["seed"]) + 99991,
        "tensor_seed_namespace": TENSOR_SEED_NAMESPACE,
        "tensor_seed_held_fixed": seed,
        "baseline_state_sha256": state_digest(baseline_state),
        "mutated_state_sha256": state_digest(mutated_state),
        "baseline_entropy_sha256": vector_digest(baseline_vector, labels),
        "mutated_entropy_sha256": vector_digest(mutated_vector, labels),
        "state_residual": f"{state_residual(baseline_state, mutated_state):.15g}",
        "entropy_residual": f"{vector_residual(baseline_vector, mutated_vector):.15g}",
        "passes": state_digest(baseline_state) == state_digest(mutated_state)
        and vector_digest(baseline_vector, labels) == vector_digest(mutated_vector, labels),
    }
    if not row["passes"]:
        raise AssertionError(f"source-provenance mutation changed the state: {row}")
    return [row]


def resource_envelope() -> list[dict[str, Any]]:
    rows = []
    for dimension in range(2, 7):
        rows.append(
            {
                "bond_dimension": dimension,
                "maximum_boundary_count": 8,
                "boundary_state_entries": dimension**8,
                "largest_balanced_schmidt_side": dimension**4,
                "subset_count": 256,
                "leading_full_vector_svd_scaling": f"256*O({dimension}^12)",
                "full_13_survivor_census_run": dimension in SURVIVOR_DIMS,
                "status": "CERTIFIED_TRACTABLE_ALL_13" if dimension in SURVIVOR_DIMS else "OUTSIDE_STEP1_RUNTIME_ENVELOPE_NOT_A_FAILURE",
            }
        )
    return rows


def anti_bypass_audit(source_provenance_mutation_passes: bool) -> list[dict[str, Any]]:
    import ast
    import state_entropy
    import survivor_loader
    import tensor_engine

    path = Path(state_entropy.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    allowed_roots = {"__future__", "itertools", "dataclasses", "typing", "numpy"}
    imports_clean = all(name.split(".")[0] in allowed_roots for name in imports)
    function_nodes = {
        node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)
    }
    reachable = set()
    frontier = ["full_entropy_vector"]
    while frontier:
        name = frontier.pop()
        if name in reachable or name not in function_nodes:
            continue
        reachable.add(name)
        frontier.extend(
            node.func.id
            for node in ast.walk(function_nodes[name])
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in function_nodes
        )
    required_reachable = {
        "full_entropy_vector",
        "full_entropy_analysis",
        "entropy_diagnostics",
        "schmidt_probabilities",
        "normalize_state",
    }
    source = "\n".join(
        ast.get_source_segment(path.read_text(encoding="utf-8"), function_nodes[name]) or ""
        for name in sorted(reachable)
    )
    forbidden_identifiers = ("mincut", "min_cut", "capacity", "cut_value", "area", "carrier", "graph")
    identifiers_clean = not any(token in source for token in forbidden_identifiers)
    signature = str(inspect.signature(state_entropy.full_entropy_vector))
    signature_clean = all(name in signature for name in ("state", "boundary_labels", "physical_dimensions"))
    seed_source = inspect.getsource(derive_tensor_seed)
    census_source = inspect.getsource(compute_survivor_census)
    census_tree = ast.parse(census_source)
    tensor_build_payloads = [
        ast.unparse(call)
        for call in ast.walk(census_tree)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "build_network"
    ]
    tensor_value_source = "\n".join(
        inspect.getsource(function)
        for function in (
            tensor_engine._random_tensor,
            tensor_engine.build_network,
            tensor_engine.leg_dimensions,
            tensor_engine.vertex_leg_orders,
        )
    )
    cut_tokens = (
        "source_weight",
        "source_seed",
        "minimum_margin",
        "cut_value",
        "mincut",
        "capacity",
    )
    carrier_adapter_source = inspect.getsource(survivor_loader.as_tensor_carrier)
    postprocessing_source = inspect.getsource(vector_digest) + inspect.getsource(
        state_entropy.complement_symmetry_residual
    )
    postprocessing_clean = not any(
        token in postprocessing_source for token in forbidden_identifiers
    )
    rows = [
        {
            "gate": "entropy_module_import_isolation",
            "passes": imports_clean,
            "evidence": "|".join(imports),
        },
        {
            "gate": "complete_reachable_entropy_call_graph",
            "passes": required_reachable.issubset(reachable),
            "evidence": "|".join(sorted(reachable)),
        },
        {
            "gate": "reachable_entropy_call_graph_forbidden_identifier_scan",
            "passes": identifiers_clean,
            "evidence": "complete reachable graph has no mincut/min_cut/capacity/cut_value/area/carrier/graph identifier",
        },
        {
            "gate": "entropy_function_state_only_signature",
            "passes": signature_clean,
            "evidence": signature,
        },
        {
            "gate": "tensor_seed_namespace_excludes_source_seed",
            "passes": "source_seed" not in seed_source
            and "source_weight" not in seed_source
            and "TENSOR_SEED_NAMESPACE" in seed_source,
            "evidence": "derive_tensor_seed payload=(namespace,carrier_name,D,replicate)",
        },
        {
            "gate": "survivor_tensor_build_calls_exclude_P1_seed_and_legacy_history",
            "passes": bool(tensor_build_payloads)
            and all(
                "source_row" not in payload and "legacy" not in payload
                for payload in tensor_build_payloads
            ),
            "evidence": "|".join(tensor_build_payloads),
        },
        {
            "gate": "cut_values_excluded_from_tensor_values_and_dimensions",
            "passes": not any(token in tensor_value_source for token in cut_tokens),
            "evidence": "tensor values use shape, independent tensor seed, and vertex label; leg dimensions use declared Edge.dimension only",
        },
        {
            "gate": "cut_values_excluded_from_entropy_tolerance_and_postprocessing",
            "passes": identifiers_clean and postprocessing_clean,
            "evidence": "complete reachable entropy graph and entropy digest/symmetry post-processors accept only state-derived values, labels, dimensions, subsets, and declared numerical tolerance",
        },
        {
            "gate": "carrier_adapter_separates_dimension_from_weight_provenance",
            "passes": "dimension=dimension" in carrier_adapter_source
            and "source_weights=weights" in carrier_adapter_source,
            "evidence": "cut weights populate Edge.source_weight provenance; declared dimension independently populates bond and boundary dimensions",
        },
        {
            "gate": "source_provenance_dataflow_mutation",
            "passes": source_provenance_mutation_passes,
            "evidence": "after topology freeze, changing source-seed metadata and all Edge.source_weight strings leaves state and entropy digests unchanged",
        },
    ]
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"anti-bypass failure: {rows}")
    return rows


def compute_all() -> dict[str, Any]:
    controls = compute_controls()
    survivor_census = compute_survivor_census()
    numerical_accountability = compute_numerical_accountability()
    survivor_scale = compute_survivor_scale_control()
    seed_independence = compute_seed_independence_regression()
    unitary_row = next(
        row
        for row in controls["gauge_rows"]
        if row["move"] == "single_boundary_local_unitary"
    )
    review_regressions = [
        {
            "regression": "source_seed_independence_mutation",
            "passes": seed_independence[0]["passes"],
            "evidence": "mutated P1 source-seed metadata and every source_weight; state and entropy digests unchanged",
        },
        {
            "regression": "small_schmidt_weight_tolerance_sweep",
            "passes": all(row["passes"] and row["bound_covers_observed_error"] for row in numerical_accountability),
            "evidence": "p=1e-14 remains in reported entropy; ranks, discarded mass, sweeps, and error bounds exported",
        },
        {
            "regression": "nonsymmetric_complex_boundary_unitary_left_action",
            "passes": unitary_row["passes"],
            "evidence": "library result agrees with independent np.einsum('ij,jb->ib', U, psi)",
        },
    ]
    seed_changes = [
        {
            "carrier": row["carrier"],
            "source_seed_provenance": row["source_seed"],
            "bond_dimension": row["bond_dimension"],
            "legacy_coupled_tensor_seed": row["legacy_tensor_seed"],
            "new_tensor_seed_namespace": row["tensor_seed_namespace"],
            "new_independent_tensor_seed": row["tensor_seed"],
            "legacy_pre_fix_entropy_vector_sha256": row["legacy_pre_fix_entropy_vector_sha256"],
            "legacy_seed_corrected_entropy_vector_sha256": row["legacy_seed_corrected_entropy_vector_sha256"],
            "new_entropy_vector_sha256": row["entropy_vector_sha256"],
            "entropy_digest_changed": row["entropy_digest_changed_from_legacy"],
            "entropy_digest_changed_same_policy": row["entropy_digest_changed_from_legacy_seed_same_policy"],
            "legacy_state_sha256": row["legacy_state_sha256"],
            "new_state_sha256": row["state_sha256"],
            "state_digest_changed": row["state_digest_changed_from_legacy_seed"],
        }
        for row in survivor_census
        if row["tensor_family"] == RANDOM_FAMILY
    ]
    return {
        "dependency_pins": verify_all_pins(),
        "controls": controls,
        "engine_checks": compute_engine_checks(),
        "survivor_census": survivor_census,
        "seed_namespace_changes": seed_changes,
        "numerical_accountability": numerical_accountability,
        "survivor_scale_control": survivor_scale,
        "seed_independence": seed_independence,
        "review_regressions": review_regressions,
        "resource_envelope": resource_envelope(),
        "anti_bypass": anti_bypass_audit(seed_independence[0]["passes"]),
    }
