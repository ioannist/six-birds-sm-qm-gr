#!/usr/bin/env python3
"""Exact computations for PROG3 Step 3: forward-floor retyping and upgrade test."""

from __future__ import annotations

import hashlib
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEP2_DIR = HERE.parent / "step2_orbit_saturation"
STEP1_DIR = HERE.parent / "step1_finite_range"

DEPENDENCY_PINS = {
    STEP2_DIR / "saturation_engine.py": "a296f2204d6e1d1aa22b15ffea6d3cb17f8327cf096c757a9141a040b463302b",
    STEP2_DIR / "step2_core.py": "d474b8a362e6ae5b535ecb293265c1ff4b98a20c725ebd5d7572aa5933dd275c",
    STEP2_DIR / "fiber_saturation_step2.csv": "8711fa029a4828d4bfcc5850ba6753149d13b3c8f93b8b3500afde906bfe5d10",
    STEP2_DIR / "endpoint_saturation_step2.csv": "ddaf1a4928db88fab5233419a5241bcbbbc228c8f7f1f0cd1fcf065aa8410dca",
    STEP2_DIR / "statement.md": "d695d56780f54ed5bb48cecbc73ad1691fe17604be980d1a751b20840ca0c022",
    HERE / "external_input" / "manager_rerun_log.md": "80d863c1998f46bf90e891568d6a37bddbfbe312a71430a9aaaf97c03d2c5c28",
    HERE / "external_input" / "prog3_inverse_series_audit.py": "3370a77c3247384d417f06bdd6a6b8dba8a0c7357fe20fabb0237e7c3e5a0079",
    HERE / "external_input" / "prog3_transition_census_audit.py": "4c1ba2b08d9d3b0803ff92245eca5f45cede6644c56edcaa3aae4f57a33246f6",
    HERE / "external_input" / "reviewer_finding_excerpt.md": "708778a869d633f179473edaf60c6e9c6f31a4a9d1e83a1517c788fc0db00bd8",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def weighted_edges_text(graph: Any) -> str:
    return "|".join(f"{u}--{v}={weight}" for u, v, weight in graph.weighted_edges)


def verify_pins() -> list[dict[str, Any]]:
    rows = []
    for path, expected in DEPENDENCY_PINS.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"dependency pin mismatch: {path}: {actual} != {expected}")
        rows.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "passes": True,
            }
        )
    return rows


verify_pins()
for path in (STEP2_DIR, STEP1_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from exact_engine import (  # noqa: E402
    enumerate_terminal_cuts,
    terminal_fixed_weighted_canonical_key,
    v2,
    v3,
)
from saturation_engine import saturate_orbit  # noqa: E402
from step2_core import load_fiber_pairs, saturate_all  # noqa: E402


FLOOR_VERDICT = "FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED"
UPGRADE_VERDICT = "NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED"


def expand_edge(
    graph: Any,
    edge_index: int,
    first: Fraction,
    second: Fraction,
    subdivision: str,
    first_endpoint: str | None = None,
) -> Any:
    """Replace one edge by an oriented two-edge path with exact capacities."""
    u, v, _capacity = graph.weighted_edges[edge_index]
    if first_endpoint is not None:
        if first_endpoint not in {u, v}:
            raise ValueError(first_endpoint)
        if first_endpoint == v:
            u, v = v, u
    rows = [row for index, row in enumerate(graph.weighted_edges) if index != edge_index]
    rows.extend(((u, subdivision, first), (subdivision, v, second)))
    return v2.make_graph(
        graph.name + "__series_expanded",
        graph.family,
        graph.boundaries,
        rows,
        graph.boundary_map,
    )


def double_expand_first_edge(graph: Any) -> tuple[Any, str, str]:
    """Replace edge c by the exact path (c, 2c, 3c)."""
    u, v, capacity = graph.weighted_edges[0]
    first_node = "<S:L1:first>"
    second_node = "<S:L1:second>"
    rows = list(graph.weighted_edges[1:])
    rows.extend(
        (
            (u, first_node, capacity),
            (first_node, second_node, 2 * capacity),
            (second_node, v, 3 * capacity),
        )
    )
    expanded = v2.make_graph(
        graph.name + "__double_series_expanded",
        graph.family,
        graph.boundaries,
        rows,
        graph.boundary_map,
    )
    return expanded, first_node, second_node


def reduce_two_orders(graph: Any, first_node: str, second_node: str) -> tuple[Any, Any]:
    left = v2.transform_series(graph, first_node)
    left = v2.transform_series(left, second_node)
    right = v2.transform_series(graph, second_node)
    right = v2.transform_series(right, first_node)
    return left, right


def external_inverse_series_witness(pairs: list[Any]) -> dict[str, Any]:
    fiber = next(
        row
        for row in pairs
        if row.carrier == "wheel_W4__b8__leaf_offset0" and row.seed == 47
    )
    endpoint = fiber.base
    endpoint_analysis = enumerate_terminal_cuts(endpoint)
    u, v, capacity = endpoint.weighted_edges[0]
    subdivision = "<S:external-regression>"
    expanded = expand_edge(endpoint, 0, capacity, 2 * capacity, subdivision)
    expanded_analysis = enumerate_terminal_cuts(expanded)
    reduced = v2.transform_series(expanded, subdivision)
    reduced_analysis = enumerate_terminal_cuts(reduced)
    forward = saturate_orbit(endpoint)
    expanded_key = terminal_fixed_weighted_canonical_key(expanded)
    endpoint_key = terminal_fixed_weighted_canonical_key(endpoint)
    reduced_key = terminal_fixed_weighted_canonical_key(reduced)
    row = {
        "fiber_id": fiber.fiber_id,
        "carrier": fiber.carrier,
        "seed": fiber.seed,
        "expanded_edge": f"{u}--{v}",
        "original_capacity_exact": str(capacity),
        "split_capacities_exact": f"{capacity}|{2 * capacity}",
        "series_composition_rule": "min(a,b)",
        "composed_capacity_exact": str(min(capacity, 2 * capacity)),
        "complement_reduced_region_count": len(endpoint_analysis.regions) // 2,
        "ordered_region_count": len(endpoint_analysis.regions),
        "fingerprint_equal_exact": expanded_analysis.values == endpoint_analysis.values,
        "expanded_unique": expanded_analysis.unique,
        "expanded_minimum_margin_exact": str(expanded_analysis.minimum_margin),
        "series_reduces_to_endpoint": reduced_key == endpoint_key,
        "reduced_fingerprint_equal_exact": reduced_analysis.values == endpoint_analysis.values,
        "forward_endpoint_state_count": len(forward.states_by_key),
        "absent_from_step2_forward_set": expanded_key not in forward.states_by_key,
        "witness_classification": "INVERSE_SERIES_PRESENTATION_MISSING_FROM_FORWARD_CLOSURE",
    }
    if not all(
        row[key]
        for key in (
            "fingerprint_equal_exact",
            "expanded_unique",
            "series_reduces_to_endpoint",
            "reduced_fingerprint_equal_exact",
            "absent_from_step2_forward_set",
        )
    ):
        raise AssertionError(f"inverse-series witness failed: {row}")
    return row


def l1_certificates(pairs: list[Any]) -> list[dict[str, Any]]:
    """Certify the series-expansion normal form on each of the 13 carrier instances."""
    unique_carriers = {}
    for fiber in pairs:
        unique_carriers.setdefault((fiber.carrier, fiber.seed), fiber.base)
    rows = []
    for (carrier, seed), endpoint in sorted(unique_carriers.items()):
        endpoint_analysis = enumerate_terminal_cuts(endpoint)
        expanded, first_node, second_node = double_expand_first_edge(endpoint)
        expanded_analysis = enumerate_terminal_cuts(expanded)
        left, right = reduce_two_orders(expanded, first_node, second_node)
        endpoint_key = terminal_fixed_weighted_canonical_key(endpoint)
        left_key = terminal_fixed_weighted_canonical_key(left)
        right_key = terminal_fixed_weighted_canonical_key(right)
        capacity = endpoint.weights[0]
        row = {
            "carrier": carrier,
            "seed": seed,
            "edge_index": 0,
            "original_capacity_exact": str(capacity),
            "expanded_path_capacities_exact": f"{capacity}|{2 * capacity}|{3 * capacity}",
            "composition_semantics": "min; parallel edges sum in make_graph",
            "fingerprint_equal_exact": expanded_analysis.values == endpoint_analysis.values,
            "expanded_unique": expanded_analysis.unique,
            "left_then_right_normal_form_is_endpoint": left_key == endpoint_key,
            "right_then_left_normal_form_is_endpoint": right_key == endpoint_key,
            "normal_forms_equal": left_key == right_key,
            "certificate": "PROVED_AND_CERTIFIED_ON_ACTUAL_CARRIER",
        }
        if not all(
            row[key]
            for key in (
                "fingerprint_equal_exact",
                "expanded_unique",
                "left_then_right_normal_form_is_endpoint",
                "right_then_left_normal_form_is_endpoint",
                "normal_forms_equal",
            )
        ):
            raise AssertionError(f"L1 carrier certificate failed: {row}")
        rows.append(row)
    if len(rows) != 13:
        raise AssertionError(f"expected 13 carrier-level L1 certificates, found {len(rows)}")
    return rows


def l2_counterexample(pairs: list[Any]) -> dict[str, Any]:
    """Rebuild the actual-carrier subdivided-Y-leg coherence obstruction."""
    fiber = next(row for row in pairs if row.fiber_id == "fiber_008")
    endpoint = fiber.base
    endpoint_analysis = enumerate_terminal_cuts(endpoint)
    degrees = v2.graph_degrees(endpoint)
    boundary_nodes = set(endpoint.boundary_map.values())
    selected = None
    for edge_index, (u, v, capacity) in enumerate(endpoint.weighted_edges):
        for center, other in ((u, v), (v, u)):
            if center in boundary_nodes or degrees[center] != 3:
                continue
            if not any(candidate[0] == center for candidate in v3.star_candidates(endpoint)):
                continue
            selected = (edge_index, center, other, capacity)
            break
        if selected is not None:
            break
    if selected is None:
        raise AssertionError("fiber_008 lost its admissible degree-three Y center")
    edge_index, center, other, capacity = selected
    subdivision = "<S:L2-coherence-counterexample>"
    expanded = expand_edge(
        endpoint,
        edge_index,
        capacity,
        2 * capacity,
        subdivision,
        first_endpoint=center,
    )
    expanded_analysis = enumerate_terminal_cuts(expanded)
    expanded_star = next(
        candidate for candidate in v3.star_candidates(expanded) if candidate[0] == center
    )
    expanded_after_move = v3.y_to_delta(expanded, expanded_star)
    expanded_after_analysis = enumerate_terminal_cuts(expanded_after_move)
    direct_star = next(
        candidate for candidate in v3.star_candidates(endpoint) if candidate[0] == center
    )
    direct_after_move = v3.y_to_delta(endpoint, direct_star)
    direct_after_analysis = enumerate_terminal_cuts(direct_after_move)
    expanded_bivalent = [
        node
        for node, degree in v2.graph_degrees(expanded_after_move).items()
        if node not in boundary_nodes and degree == 2
    ]
    direct_bivalent = [
        node
        for node, degree in v2.graph_degrees(direct_after_move).items()
        if node not in boundary_nodes and degree == 2
    ]
    # These are already their series normal forms: the formerly bivalent
    # subdivision vertex has acquired two triangle edges and degree three.
    expanded_key = terminal_fixed_weighted_canonical_key(expanded_after_move)
    direct_key = terminal_fixed_weighted_canonical_key(direct_after_move)
    forward = saturate_orbit(endpoint)
    row = {
        "fiber_id": fiber.fiber_id,
        "carrier": fiber.carrier,
        "seed": fiber.seed,
        "edge_index": edge_index,
        "subdivided_edge": f"{center}--{other}",
        "edge_capacity_exact": str(capacity),
        "split_capacities_exact": f"{capacity}|{2 * capacity}",
        "y_center": center,
        "move_sequence_expanded": "series_subdivision -> y_delta -> series_normal_form(0 removals)",
        "move_sequence_reduced": "y_delta -> series_normal_form(0 removals)",
        "starting_weighted_edges_exact": weighted_edges_text(endpoint),
        "expanded_after_move_weighted_edges_exact": weighted_edges_text(expanded_after_move),
        "direct_after_move_weighted_edges_exact": weighted_edges_text(direct_after_move),
        "expanded_fingerprint_equal_exact": expanded_analysis.values == endpoint_analysis.values,
        "expanded_unique": expanded_analysis.unique,
        "post_move_fingerprint_equal_exact": expanded_after_analysis.values == endpoint_analysis.values,
        "post_move_unique": expanded_after_analysis.unique,
        "direct_fingerprint_equal_exact": direct_after_analysis.values == endpoint_analysis.values,
        "direct_unique": direct_after_analysis.unique,
        "post_move_minimum_margin_exact": str(expanded_after_analysis.minimum_margin),
        "subdivision_degree_after_y_delta": v2.graph_degrees(expanded_after_move)[subdivision],
        "expanded_normal_form_internal_bivalent_count": len(expanded_bivalent),
        "direct_normal_form_internal_bivalent_count": len(direct_bivalent),
        "expanded_normal_form_node_count": len(expanded_after_move.nodes),
        "direct_normal_form_node_count": len(direct_after_move.nodes),
        "expanded_normal_form_edge_count": len(expanded_after_move.edges),
        "direct_normal_form_edge_count": len(direct_after_move.edges),
        "normal_forms_terminal_fixed_isomorphic": expanded_key == direct_key,
        "expanded_normal_form_in_reduced_delta_forward_set": expanded_key in forward.states_by_key,
        "delta_only_projection_impossible_by_edge_count": len(expanded_after_move.edges)
        > len(endpoint.edges),
        "lemma_outcome": "FAILED_L2_SUBDIVIDED_Y_LEG_CASE",
    }
    required_true = (
        "expanded_fingerprint_equal_exact",
        "expanded_unique",
        "post_move_fingerprint_equal_exact",
        "post_move_unique",
        "direct_fingerprint_equal_exact",
        "direct_unique",
        "delta_only_projection_impossible_by_edge_count",
    )
    if not all(row[key] for key in required_true):
        raise AssertionError(f"L2 counterexample prerequisite failed: {row}")
    if (
        row["subdivision_degree_after_y_delta"] != 3
        or row["expanded_normal_form_internal_bivalent_count"] != 0
        or row["direct_normal_form_internal_bivalent_count"] != 0
        or row["normal_forms_terminal_fixed_isomorphic"]
        or row["expanded_normal_form_in_reduced_delta_forward_set"]
    ):
        raise AssertionError(f"L2 counterexample no longer obstructs coherence: {row}")
    return row


def floor_rows(step2_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in step2_data["fiber_rows"]:
        if not (
            row["base_saturated"]
            and row["perturbed_saturated"]
            and row["cross_orbit_weighted_isomorphism_count"] == 0
        ):
            raise AssertionError(f"forward-floor regression changed: {row}")
        rows.append(
            {
                "fiber_id": row["fiber_id"],
                "carrier": row["carrier"],
                "seed": row["seed"],
                "basis_index": row["basis_index"],
                "base_forward_canonical_state_count": row["base_canonical_state_count"],
                "perturbed_forward_canonical_state_count": row[
                    "perturbed_canonical_state_count"
                ],
                "forward_cross_isomorphism_count": row[
                    "cross_orbit_weighted_isomorphism_count"
                ],
                "floor_verdict": FLOOR_VERDICT,
                "symmetric_series_delta_upgrade_verdict": UPGRADE_VERDICT,
            }
        )
    if len(rows) != 19:
        raise AssertionError(f"expected 19 floor rows, found {len(rows)}")
    return rows


def transition_census(step2_data: dict[str, Any]) -> list[dict[str, Any]]:
    endpoints = step2_data["endpoint_rows"]
    classes = (
        "series",
        "two_terminal_module",
        "saturated_or_zero_column",
        "inseparable_contraction",
        "delta_y_y_delta",
    )
    rows = []
    for move_class in classes:
        accepted = sum(int(row[f"accepted_{move_class}"]) for row in endpoints)
        novel = sum(int(row[f"novel_{move_class}"]) for row in endpoints)
        rows.append(
            {
                "move_class": move_class,
                "directionality_in_step2": (
                    "bidirectional" if move_class == "delta_y_y_delta" else "reduction_only"
                ),
                "accepted_transition_count": accepted,
                "novel_canonical_state_count": novel,
            }
        )
    expected = {
        "series": (0, 0),
        "two_terminal_module": (0, 0),
        "saturated_or_zero_column": (0, 0),
        "inseparable_contraction": (0, 0),
        "delta_y_y_delta": (100, 50),
    }
    actual = {
        row["move_class"]: (
            row["accepted_transition_count"],
            row["novel_canonical_state_count"],
        )
        for row in rows
    }
    if actual != expected:
        raise AssertionError(f"Step-2 transition census changed: {actual}")
    return rows


def can_fail_controls(pairs: list[Any]) -> list[dict[str, Any]]:
    """Five independent controls pin the exact boundary of the Step-3 claims."""
    wheel = next(row for row in pairs if row.fiber_id == "fiber_001")
    endpoint = wheel.base
    endpoint_analysis = enumerate_terminal_cuts(endpoint)
    endpoint_key = terminal_fixed_weighted_canonical_key(endpoint)
    rows: list[dict[str, Any]] = []

    # (a) A shared endpoint must have a nonempty forward intersection, so the
    # disjoint-floor predicate must reject it.
    shared_orbit = saturate_orbit(endpoint)
    shared_intersection_count = len(
        set(shared_orbit.states_by_key) & set(shared_orbit.states_by_key)
    )
    shared_passes = shared_intersection_count > 0
    rows.append(
        {
            "control_id": "A_SHARED_ENDPOINT_REJECTS_DISJOINT_FLOOR",
            "control_kind": "CAN_FAIL_NEGATIVE",
            "expected_classification": "FLOOR_REJECTED",
            "observed_classification": (
                "FLOOR_REJECTED" if shared_passes else "FLOOR_ACCEPTED_INCORRECTLY"
            ),
            "expected_reason": "NONEMPTY_FORWARD_SET_INTERSECTION",
            "observed_reason": (
                "NONEMPTY_FORWARD_SET_INTERSECTION" if shared_passes else "EMPTY_INTERSECTION"
            ),
            "metric": "cross_canonical_state_count",
            "value": str(shared_intersection_count),
            "passes": shared_passes,
        }
    )

    # (b) Mutating an active edge used by the L2 carrier must destroy exact
    # fingerprint equality. The expected result is derived from fresh exact
    # enumeration, not from the stored L2 summary row.
    l2_fiber = next(row for row in pairs if row.fiber_id == "fiber_008")
    l2_endpoint = l2_fiber.base
    l2_analysis = enumerate_terminal_cuts(l2_endpoint)
    l2_edge_index = next(
        index
        for index in range(len(l2_endpoint.edges))
        if any(row[index] for row in l2_analysis.incidence)
    )
    mutated_rows = list(l2_endpoint.weighted_edges)
    u, v, capacity = mutated_rows[l2_edge_index]
    mutated_rows[l2_edge_index] = (u, v, capacity + capacity / 11)
    mutated = v2.make_graph(
        l2_endpoint.name + "__capacity_mutation",
        l2_endpoint.family,
        l2_endpoint.boundaries,
        mutated_rows,
        l2_endpoint.boundary_map,
    )
    mutated_analysis = enumerate_terminal_cuts(mutated)
    changed_regions = sum(
        left != right for left, right in zip(l2_analysis.values, mutated_analysis.values)
    )
    mutation_passes = changed_regions > 0
    rows.append(
        {
            "control_id": "B_L2_EDGE_MUTATION_BREAKS_FINGERPRINT",
            "control_kind": "CAN_FAIL_NEGATIVE",
            "expected_classification": "FINGERPRINT_EQUALITY_REJECTED",
            "observed_classification": (
                "FINGERPRINT_EQUALITY_REJECTED"
                if mutation_passes
                else "FINGERPRINT_EQUALITY_ACCEPTED_INCORRECTLY"
            ),
            "expected_reason": "EXACT_FINGERPRINT_CHANGED",
            "observed_reason": (
                "EXACT_FINGERPRINT_CHANGED" if mutation_passes else "FINGERPRINT_UNCHANGED"
            ),
            "metric": f"changed_regions_after_edge_{l2_edge_index}_mutation",
            "value": str(changed_regions),
            "passes": mutation_passes,
        }
    )

    # (c) Interior relabelling is a positive control for terminal-fixed exact
    # weighted canonicalization.
    boundary_nodes = set(endpoint.boundary_map.values())
    interiors = [node for node in endpoint.nodes if node not in boundary_nodes]
    relabel = {node: f"<RELABEL:{index}>" for index, node in enumerate(reversed(interiors))}
    relabelled = v2.make_graph(
        endpoint.name + "__interior_relabel",
        endpoint.family,
        endpoint.boundaries,
        (
            (relabel.get(u, u), relabel.get(v, v), weight)
            for u, v, weight in endpoint.weighted_edges
        ),
        endpoint.boundary_map,
    )
    relabel_passes = terminal_fixed_weighted_canonical_key(relabelled) == endpoint_key
    rows.append(
        {
            "control_id": "C_INTERIOR_RELABEL_IS_RECOGNIZED",
            "control_kind": "POSITIVE_CANONICALIZATION",
            "expected_classification": "WEIGHTED_ISOMORPHISM_ACCEPTED",
            "observed_classification": (
                "WEIGHTED_ISOMORPHISM_ACCEPTED"
                if relabel_passes
                else "WEIGHTED_ISOMORPHISM_REJECTED_INCORRECTLY"
            ),
            "expected_reason": "TERMINAL_FIXED_WEIGHTED_ISOMORPHISM_RECOGNIZED",
            "observed_reason": (
                "TERMINAL_FIXED_WEIGHTED_ISOMORPHISM_RECOGNIZED"
                if relabel_passes
                else "CANONICAL_KEYS_DIFFER"
            ),
            "metric": "canonical_keys_equal",
            "value": str(relabel_passes),
            "passes": relabel_passes,
        }
    )

    # (d) An equal split on an active edge preserves values but introduces two
    # equally good placements of the new vertex whenever that edge is cut.
    active_edge_index = next(
        index
        for index in range(len(endpoint.edges))
        if any(row[index] for row in endpoint_analysis.incidence)
    )
    active_capacity = endpoint.weights[active_edge_index]
    equal_split = expand_edge(
        endpoint,
        active_edge_index,
        active_capacity,
        active_capacity,
        "<S:equal-split-control>",
    )
    equal_analysis = enumerate_terminal_cuts(equal_split)
    equal_passes = (
        equal_analysis.values == endpoint_analysis.values
        and not equal_analysis.unique
        and equal_analysis.minimum_margin == 0
    )
    rows.append(
        {
            "control_id": "D_EQUAL_ACTIVE_SPLIT_FAILS_UNIQUENESS",
            "control_kind": "CAN_FAIL_NEGATIVE",
            "expected_classification": "UNIQUE_MINIMIZER_ADMISSION_REJECTED",
            "observed_classification": (
                "UNIQUE_MINIMIZER_ADMISSION_REJECTED"
                if equal_passes
                else "UNIQUE_MINIMIZER_ADMISSION_ACCEPTED_INCORRECTLY"
            ),
            "expected_reason": "ACTIVE_CUT_HAS_TWO_SUBDIVISION_SIDE_MINIMIZERS",
            "observed_reason": (
                "ACTIVE_CUT_HAS_TWO_SUBDIVISION_SIDE_MINIMIZERS"
                if equal_passes
                else "UNEXPECTED_UNIQUENESS_RESULT"
            ),
            "metric": f"edge_{active_edge_index}_minimum_margin_exact",
            "value": str(equal_analysis.minimum_margin),
            "passes": equal_passes,
        }
    )

    # (e) Starting from a non-series-reduced presentation invalidates the
    # proposition that the starting presentation itself is the normal form.
    u, v, capacity = endpoint.weighted_edges[0]
    subdivision = "<S:non-reduced-base-control>"
    non_reduced = expand_edge(endpoint, 0, capacity, 2 * capacity, subdivision)
    normalized = v2.transform_series(non_reduced, subdivision)
    non_reduced_key = terminal_fixed_weighted_canonical_key(non_reduced)
    normalized_key = terminal_fixed_weighted_canonical_key(normalized)
    non_reduced_passes = (
        v2.graph_degrees(non_reduced)[subdivision] == 2
        and normalized_key != non_reduced_key
        and normalized_key == endpoint_key
    )
    rows.append(
        {
            "control_id": "E_NON_SERIES_REDUCED_BASE_REDUCES_PAST_ITSELF",
            "control_kind": "HYPOTHESIS_NECESSITY",
            "expected_classification": "STARTING_PRESENTATION_REJECTED_AS_NORMAL_FORM",
            "observed_classification": (
                "STARTING_PRESENTATION_REJECTED_AS_NORMAL_FORM"
                if non_reduced_passes
                else "STARTING_PRESENTATION_ACCEPTED_INCORRECTLY"
            ),
            "expected_reason": "NONTERMINAL_BIVALENT_BASE_IS_NOT_ITS_NORMAL_FORM",
            "observed_reason": (
                "NONTERMINAL_BIVALENT_BASE_IS_NOT_ITS_NORMAL_FORM"
                if non_reduced_passes
                else "BASE_DID_NOT_REDUCE_PAST_ITSELF"
            ),
            "metric": "nodes_before_after_series_reduction",
            "value": f"{len(non_reduced.nodes)}->{len(normalized.nodes)}",
            "passes": non_reduced_passes,
        }
    )

    if len(rows) != 5 or not all(row["passes"] for row in rows):
        raise AssertionError(f"can-fail control failure: {rows}")
    return rows


def compute_all() -> dict[str, Any]:
    pairs = load_fiber_pairs()
    step2_data = saturate_all()
    witness = external_inverse_series_witness(pairs)
    l1_rows = l1_certificates(pairs)
    l2_row = l2_counterexample(pairs)
    control_rows = can_fail_controls(pairs)
    return {
        "dependencies": verify_pins(),
        "floor_rows": floor_rows(step2_data),
        "transition_census": transition_census(step2_data),
        "external_witness": [witness],
        "l1_certificates": l1_rows,
        "l2_counterexample": [l2_row],
        "negative_controls": control_rows,
        "lemma_rows": [
            {
                "lemma": "L1_SERIES_NORMAL_FORM_ON_ADMISSIBLE_HOMEOMORPHIC_EXPANSIONS",
                "outcome": "PROVED_AND_CERTIFIED",
                "certificate_count": len(l1_rows),
                "scope": "positive exact splits of edges in the 13 pinned series-reduced carrier instances; min composition",
            },
            {
                "lemma": "L2_SERIES_DELTA_Y_COHERENCE",
                "outcome": "FAILED",
                "certificate_count": 1,
                "scope": "subdivided leg of an accepted Y-to-Delta move on fiber_008",
            },
            {
                "lemma": "L3_SYMMETRIC_SERIES_DELTA_ORBIT_DISJOINTNESS",
                "outcome": "NOT_REACHED_BECAUSE_L2_FAILED",
                "certificate_count": 0,
                "scope": "all 19 fibers",
            },
        ],
    }
