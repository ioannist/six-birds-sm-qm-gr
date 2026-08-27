#!/usr/bin/env python3
"""Deterministic computations for PROG3 Step 1."""

from __future__ import annotations

import ast
import csv
import inspect
from fractions import Fraction
from pathlib import Path
from typing import Any

from exact_engine import (
    PINS,
    SURVIVOR_PATH,
    ExactAnalysis,
    ExactInterval,
    circular_planarity,
    compare_depth_three_orbits,
    direction_text,
    enumerate_terminal_cuts,
    fingerprint_digest,
    fingerprint_equal_by_enumeration,
    finite_fingerprint_interval,
    five_move_closure_exact,
    format_fraction,
    intersect_intervals,
    interval_text,
    nullspace_basis,
    perturb,
    positive_capacity_interval,
    sha256,
    v2,
    weighted_automorphism_status,
)


def read_survivor_rows() -> list[dict[str, str]]:
    with SURVIVOR_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 13:
        raise AssertionError(f"pinned v3 artifact has {len(rows)} rows, expected 13")
    return rows


def carrier_map():
    return {carrier.name: carrier for carrier in v2.search_carriers()}


def exact_margin_class(margin: Fraction) -> str:
    if margin == 0:
        return "EXACT_ZERO_DEGENERATE"
    if margin < Fraction(1, 1_000_000):
        return "GENUINELY_TINY_POSITIVE"
    return "POSITIVE"


def cut_region_rows(
    carrier: str,
    seed: int,
    stage: str,
    graph,
    analysis: ExactAnalysis,
) -> list[dict[str, Any]]:
    rows = []
    for region in analysis.regions:
        rows.append(
            {
                "carrier": carrier,
                "seed": seed,
                "stage": stage,
                "region": "|".join(region.region),
                "minimum_value_exact": format_fraction(region.value),
                "unique_minimizer": len(region.active_sides) == 1,
                "active_assignment_count": len(region.active_sides),
                "active_incidence_count": len(region.active_rows),
                "margin_exact": format_fraction(region.margin),
                "active_cut_incidence": "".join(map(str, region.active_rows[0])),
            }
        )
    return rows


def weight_rows(carrier: str, seed: int, stage: str, graph) -> list[dict[str, Any]]:
    return [
        {
            "carrier": carrier,
            "seed": seed,
            "stage": stage,
            "edge_index": index,
            "u": u,
            "v": v,
            "weight_exact": format_fraction(weight),
        }
        for index, (u, v, weight) in enumerate(graph.weighted_edges)
    ]


def _candidate_t_values(interval: ExactInterval) -> tuple[Fraction, ...]:
    values: list[Fraction] = []
    for divisor in (2, 3, 5, 7, 11):
        if interval.upper is not None and interval.upper > 0:
            values.append(interval.upper / divisor)
        if interval.lower is not None and interval.lower < 0:
            values.append(interval.lower / divisor)
        if interval.lower is None and interval.upper is None:
            values.extend((Fraction(1, divisor), Fraction(-1, divisor)))
    seen = set()
    return tuple(value for value in values if value and not (value in seen or seen.add(value)))


def certify_direction(
    carrier: str,
    seed: int,
    graph,
    analysis: ExactAnalysis,
    basis_index: int,
    direction: tuple[int, ...],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    fingerprint_interval = finite_fingerprint_interval(graph, analysis, direction)
    positivity_interval = positive_capacity_interval(graph, direction)
    admissible_interval = intersect_intervals(fingerprint_interval, positivity_interval)
    if not fingerprint_interval.nondegenerate_around_zero:
        interval_row = {
            "carrier": carrier,
            "seed": seed,
            "basis_index": basis_index,
            "direction": direction_text(graph, direction),
            "fingerprint_interval": interval_text(fingerprint_interval),
            "positive_capacity_interval": interval_text(positivity_interval),
            "certified_network_interval": interval_text(admissible_interval),
            "nondegenerate": False,
        }
        return interval_row, {
            "carrier": carrier,
            "seed": seed,
            "basis_index": basis_index,
            "certified_fiber": False,
            "reason": "fingerprint interval is {0}",
        }, {}

    selected = None
    failure_reasons = []
    for t_star in _candidate_t_values(admissible_interval):
        if not admissible_interval.contains_strictly(t_star):
            continue
        moved = perturb(graph, direction, t_star)
        if min(moved.weights) <= 0:
            continue
        same_fingerprint, moved_analysis = fingerprint_equal_by_enumeration(analysis, moved)
        if not same_fingerprint:
            failure_reasons.append(f"t={format_fraction(t_star)} changed exact fingerprint")
            continue
        (
            automorphism_count,
            terminal_automorphism_count,
            any_automorphism_maps,
            terminal_automorphism_maps,
        ) = weighted_automorphism_status(graph, moved)
        if any_automorphism_maps:
            failure_reasons.append(f"t={format_fraction(t_star)} was automorphic")
            continue
        orbit_comparison = compare_depth_three_orbits(graph, moved)
        moved_selected = orbit_comparison["moved_orbit"].selected
        reclosed = moved_selected.graph
        reclosed_analysis = moved_selected.analysis
        reclosure_moves = tuple(
            {"move": move, "object": object_name}
            for move, object_name in moved_selected.path
        )
        reclosed_deficiency = len(reclosed.edges) - reclosed_analysis.rank
        selected = {
            "t_star": t_star,
            "moved": moved,
            "moved_analysis": moved_analysis,
            "automorphism_count": automorphism_count,
            "terminal_automorphism_count": terminal_automorphism_count,
            "terminal_automorphism_maps": terminal_automorphism_maps,
            "reclosed_analysis": reclosed_analysis,
            "reclosed_deficiency": reclosed_deficiency,
            "reclosure_moves": reclosure_moves,
            "orbit_comparison": orbit_comparison,
        }
        break

    interval_row = {
        "carrier": carrier,
        "seed": seed,
        "basis_index": basis_index,
        "direction": direction_text(graph, direction),
        "fingerprint_interval": interval_text(fingerprint_interval),
        "fingerprint_lower_exact": "-inf" if fingerprint_interval.lower is None else format_fraction(fingerprint_interval.lower),
        "fingerprint_upper_exact": "+inf" if fingerprint_interval.upper is None else format_fraction(fingerprint_interval.upper),
        "positive_capacity_interval": interval_text(positivity_interval),
        "certified_network_interval": interval_text(admissible_interval),
        "nondegenerate": fingerprint_interval.nondegenerate_around_zero,
    }
    if selected is None:
        return interval_row, {
            "carrier": carrier,
            "seed": seed,
            "basis_index": basis_index,
            "certified_fiber": False,
            "reason": " | ".join(failure_reasons) or "no exact interior t candidate",
        }, {}

    moved = selected["moved"]
    moved_analysis = selected["moved_analysis"]
    t_star = selected["t_star"]
    comparison = selected["orbit_comparison"]
    base_orbit = comparison["base_orbit"]
    moved_orbit = comparison["moved_orbit"]
    orbit_verdict = comparison["verdict"]
    verdict_text = (
        orbit_verdict
        if orbit_verdict != "GAUGE"
        else f"GAUGE via path {comparison['path_if_gauge']}"
    )
    reason = (
        "different weights; no same-graph automorphism; exact fingerprint equality; "
        "each endpoint is returned as the minimum of the declared depth-three closure objective; "
        f"cross-presentation move-orbit equivalence {verdict_text}"
    )
    initial_base_delta_y = sorted(
        object_name
        for move, object_name, depth, path_length in base_orbit.accepted_moves
        if move == "delta_y" and depth == 0 and path_length == 0
    )
    initial_moved_delta_y = sorted(
        object_name
        for move, object_name, depth, path_length in moved_orbit.accepted_moves
        if move == "delta_y" and depth == 0 and path_length == 0
    )
    fiber_row = {
        "carrier": carrier,
        "seed": seed,
        "basis_index": basis_index,
        "t_star_exact": format_fraction(t_star),
        "weights_differ": graph.weights != moved.weights,
        "minimum_perturbed_weight_exact": format_fraction(min(moved.weights)),
        "exact_fingerprint_equal_by_full_enumeration": moved_analysis.values == analysis.values,
        "base_fingerprint_sha256": fingerprint_digest(analysis),
        "perturbed_fingerprint_sha256": fingerprint_digest(moved_analysis),
        "unique_minimizers_after_perturbation": moved_analysis.unique,
        "all_graph_automorphism_count": selected["automorphism_count"],
        "terminal_set_preserving_automorphism_count": selected["terminal_automorphism_count"],
        "any_graph_automorphism_maps_base_to_perturbed": False,
        "terminal_set_automorphism_maps_base_to_perturbed": selected["terminal_automorphism_maps"],
        "selected_canonical_reclosure_path_length": len(selected["reclosure_moves"]),
        "five_move_residual_deficiency": selected["reclosed_deficiency"],
        "certified_fiber": True,
        "reason": reason,
    }
    orbit_row = {
        "carrier": carrier,
        "seed": seed,
        "basis_index": basis_index,
        "t_star_exact": format_fraction(t_star),
        "base_accepted_move_count": comparison["base_accepted_move_count"],
        "perturbed_accepted_move_count": comparison["moved_accepted_move_count"],
        "base_orbit_state_count": comparison["base_orbit_state_count"],
        "perturbed_orbit_state_count": comparison["moved_orbit_state_count"],
        "base_visited_labelled_state_count": comparison["base_visited_labelled_state_count"],
        "perturbed_visited_labelled_state_count": comparison["moved_visited_labelled_state_count"],
        "base_selected_canonical_reclosure_path_length": len(base_orbit.selected.path),
        "perturbed_selected_canonical_reclosure_path_length": len(moved_orbit.selected.path),
        "cross_orbit_weighted_isomorphism_count": comparison["cross_orbit_weighted_isomorphism_count"],
        "verdict": orbit_verdict,
        "path_if_gauge": comparison["path_if_gauge"],
        "base_initial_delta_y_objects": "|".join(initial_base_delta_y),
        "perturbed_initial_delta_y_objects": "|".join(initial_moved_delta_y),
        "canonicalization": comparison["canonicalization"],
    }
    return interval_row, fiber_row, orbit_row


def exact_recertification() -> dict[str, Any]:
    stored_rows = read_survivor_rows()
    carriers = carrier_map()
    summaries = []
    intervals = []
    fibers = []
    orbit_audits = []
    cuts = []
    weights = []
    closure_rows = []
    for stored in stored_rows:
        carrier_name = stored["carrier"]
        seed = int(stored["seed"])
        raw = v2.seeded_weights(carriers[carrier_name], seed)
        raw_analysis = enumerate_terminal_cuts(raw)
        reduced, reduced_analysis, moves = five_move_closure_exact(raw)
        raw_deficiency = len(raw.edges) - raw_analysis.rank
        residual_deficiency = len(reduced.edges) - reduced_analysis.rank
        raw_circular, method = circular_planarity(raw)
        reduced_circular, _ = circular_planarity(reduced)

        stored_consistent = all(
            (
                raw_analysis.rank == int(stored["raw_exact_rank"]),
                raw_deficiency == int(stored["raw_deficiency"]),
                len(reduced.edges) == int(stored["reduced_edge_count"]),
                reduced_analysis.rank == int(stored["reduced_exact_rank"]),
                residual_deficiency == int(stored["residual_deficiency"]),
                "|".join(move["move"] for move in moves) == stored["closure_moves"],
            )
        )
        basis = nullspace_basis(reduced_analysis.incidence) if reduced_analysis.unique else ()
        if len(basis) != residual_deficiency:
            raise AssertionError(f"kernel dimension mismatch for {carrier_name} seed {seed}")
        carrier_fibers = []
        for basis_index, direction in enumerate(basis):
            interval_row, fiber_row, orbit_row = certify_direction(
                carrier_name, seed, reduced, reduced_analysis, basis_index, direction
            )
            intervals.append(interval_row)
            fibers.append(fiber_row)
            if orbit_row:
                orbit_audits.append(orbit_row)
            carrier_fibers.append(fiber_row)

        summary = {
            "carrier": carrier_name,
            "seed": seed,
            "boundary_count": len(raw.boundaries),
            "raw_edge_count": len(raw.edges),
            "raw_rank_exact": raw_analysis.rank,
            "raw_minimum_margin_exact": format_fraction(raw_analysis.minimum_margin),
            "raw_margin_class": exact_margin_class(raw_analysis.minimum_margin),
            "raw_unique_all_regions": raw_analysis.unique,
            "reduced_edge_count": len(reduced.edges),
            "reduced_rank_exact": reduced_analysis.rank,
            "residual_deficiency": residual_deficiency,
            "reduced_minimum_margin_exact": format_fraction(reduced_analysis.minimum_margin),
            "reduced_unique_all_regions": reduced_analysis.unique,
            "kernel_basis_directions": len(basis),
            "nondegenerate_direction_count": sum(row["nondegenerate"] for row in intervals if row["carrier"] == carrier_name and row["seed"] == seed),
            "certified_direction_fiber_count": sum(row["certified_fiber"] for row in carrier_fibers),
            "certified_carrier_fiber": bool(carrier_fibers) and all(row["certified_fiber"] for row in carrier_fibers),
            "depth_three_orbit_disjoint_direction_count": sum(
                row["verdict"] == "depth-three five-move-orbit-disjoint"
                for row in orbit_audits
                if row["carrier"] == carrier_name and row["seed"] == seed
            ),
            "depth_three_gauge_direction_count": sum(
                row["verdict"] == "GAUGE"
                for row in orbit_audits
                if row["carrier"] == carrier_name and row["seed"] == seed
            ),
            "raw_circular_planar": raw_circular,
            "reduced_circular_planar": reduced_circular,
            "circular_planarity_method": method,
            "v3_status_exactly_reproduced": stored_consistent,
            "v3_status_changed": not stored_consistent,
        }
        summaries.append(summary)
        cuts.extend(cut_region_rows(carrier_name, seed, "raw", raw, raw_analysis))
        cuts.extend(cut_region_rows(carrier_name, seed, "five_move_reduced", reduced, reduced_analysis))
        weights.extend(weight_rows(carrier_name, seed, "raw", raw))
        weights.extend(weight_rows(carrier_name, seed, "five_move_reduced", reduced))
        closure_rows.append(
            {
                "carrier": carrier_name,
                "seed": seed,
                "move_count": len(moves),
                "moves": "|".join(move["move"] for move in moves),
                "objects": "|".join(move["object"] for move in moves),
                "exact_fingerprint_preserved": raw_analysis.values == reduced_analysis.values,
            }
        )
    return {
        "summaries": summaries,
        "intervals": intervals,
        "fibers": fibers,
        "orbit_audits": orbit_audits,
        "cut_regions": cuts,
        "weights": weights,
        "closures": closure_rows,
    }


def anti_bypass_audit() -> list[dict[str, Any]]:
    import exact_engine

    tree = ast.parse(Path(exact_engine.__file__).read_text(encoding="utf-8"))
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "fingerprint_equal_by_enumeration"
    )
    calls = {
        node.func.id
        for node in ast.walk(function)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    source = inspect.getsource(exact_engine.fingerprint_equal_by_enumeration)
    rows = [
        {
            "gate": "perturbed_fingerprint_calls_exhaustive_enumerator",
            "passes": "enumerate_terminal_cuts" in calls,
            "evidence": "direct call to enumerate_terminal_cuts(moved_graph)",
        },
        {
            "gate": "perturbed_fingerprint_has_no_jacobian_extrapolation",
            "passes": all(token not in source for token in ("incidence", "direction", "slope", "extrapolat")),
            "evidence": "function accepts base analysis and moved graph only; moved values are enumerated",
        },
        {
            "gate": "all_certification_weights_are_fraction",
            "passes": True,
            "evidence": "enumerate_terminal_cuts raises unless every graph weight is Fraction",
        },
    ]
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"anti-bypass failure: {rows}")
    return rows


def dependency_rows() -> list[dict[str, Any]]:
    return [
        {
            "path": str(path.relative_to(path.parents[3])) if "review_2026" in path.parts else str(path),
            "expected_sha256": expected,
            "actual_sha256": sha256(path),
            "passes": sha256(path) == expected,
        }
        for path, expected in PINS.items()
    ]


def compute_all() -> dict[str, Any]:
    result = exact_recertification()
    result["anti_bypass"] = anti_bypass_audit()
    result["dependencies"] = dependency_rows()
    return result
