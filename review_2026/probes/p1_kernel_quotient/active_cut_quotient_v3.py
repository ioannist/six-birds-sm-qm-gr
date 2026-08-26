#!/usr/bin/env python3
"""P1-HYGIENE: add verified Delta-Y/Y-Delta to the maintained closure."""

from __future__ import annotations

import hashlib
import itertools
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
V2_PATH = HERE / "active_cut_quotient_v2.py"
V2_SHA256 = "adcfa43bf35fc2994c9f46fa57d9f9d380e86d6a5eac92a55c7e036a9fea9cc2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(V2_PATH) != V2_SHA256:
    raise RuntimeError(f"v2 machinery pin mismatch: {sha256(V2_PATH)} != {V2_SHA256}")
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import active_cut_quotient_v2 as v2  # noqa: E402


Graph = v2.Graph
CutAnalysis = v2.CutAnalysis


def triangle_candidates(graph: Graph) -> list[tuple[str, str, str]]:
    edges = set(graph.edges)
    return [
        nodes
        for nodes in itertools.combinations(graph.nodes, 3)
        if all(v2.edge(left, right) in edges for left, right in itertools.combinations(nodes, 2))
    ]


def delta_to_y(graph: Graph, nodes: tuple[str, str, str]) -> Graph:
    u0, u1, u2 = nodes
    weights = {v2.edge(u, v): weight for u, v, weight in graph.weighted_edges}
    w01 = weights[v2.edge(u0, u1)]
    w02 = weights[v2.edge(u0, u2)]
    w12 = weights[v2.edge(u1, u2)]
    center = "<Y:" + "+".join(nodes) + ">"
    if center in graph.nodes:
        raise ValueError(f"Delta-Y center collision: {center}")
    removed = {v2.edge(u0, u1), v2.edge(u0, u2), v2.edge(u1, u2)}
    rows = [
        row for row in graph.weighted_edges if v2.edge(row[0], row[1]) not in removed
    ]
    # Exact terminal cut function of the triangle.  For example, isolating u0
    # costs w01+w02, which is the u0 star leg below.
    rows.extend(
        (
            (u0, center, w01 + w02),
            (u1, center, w01 + w12),
            (u2, center, w02 + w12),
        )
    )
    return v2.make_graph(
        graph.name + "_delta_y", graph.family, graph.boundaries, rows, graph.boundary_map
    )


def star_candidates(
    graph: Graph,
) -> list[tuple[str, tuple[str, str, str], tuple[Fraction, Fraction, Fraction]]]:
    degrees = v2.graph_degrees(graph)
    boundary_nodes = set(graph.boundary_map.values())
    candidates = []
    for center in graph.nodes:
        if center in boundary_nodes or degrees[center] != 3:
            continue
        incident = sorted(
            (v if u == center else u, weight)
            for u, v, weight in graph.weighted_edges
            if center in {u, v}
        )
        (u0, a0), (u1, a1), (u2, a2) = incident
        triangle = (
            (a0 + a1 - a2) / 2,
            (a0 + a2 - a1) / 2,
            (a1 + a2 - a0) / 2,
        )
        if min(triangle) > 0:
            candidates.append((center, (u0, u1, u2), triangle))
    return candidates


def y_to_delta(
    graph: Graph,
    candidate: tuple[str, tuple[str, str, str], tuple[Fraction, Fraction, Fraction]],
) -> Graph:
    center, (u0, u1, u2), (w01, w02, w12) = candidate
    rows = [row for row in graph.weighted_edges if center not in row[:2]]
    rows.extend(((u0, u1, w01), (u0, u2, w02), (u1, u2, w12)))
    return v2.make_graph(
        graph.name + "_y_delta", graph.family, graph.boundaries, rows, graph.boundary_map
    )


def graph_key(graph: Graph) -> tuple[Any, ...]:
    """Deterministic labelled-state key; enough for the bounded search closure."""
    return graph.boundary_nodes, graph.weighted_edges


def fifth_candidates(graph: Graph) -> list[tuple[str, str, Graph]]:
    rows = [
        ("delta_y", "+".join(nodes), delta_to_y(graph, nodes))
        for nodes in triangle_candidates(graph)
    ]
    rows.extend(
        ("y_delta", candidate[0], y_to_delta(graph, candidate))
        for candidate in star_candidates(graph)
    )
    return rows


def deficiency(graph: Graph, analysis: CutAnalysis) -> int:
    return len(graph.edges) - analysis.rank


def move_audit(
    before: CutAnalysis, after: CutAnalysis, move: str, object_name: str, graph: Graph
) -> dict[str, Any]:
    return {
        "move": move,
        "object": object_name,
        "region_count": len(before.regions),
        "all_region_values_preserved": after.values == before.values,
        "unique_before": before.unique,
        "unique_after_move": after.unique,
        "minimum_margin_after_move": float(after.minimum_margin),
        "rank_recomputed_after_move": after.rank,
        "residual_deficiency_after_move": deficiency(graph, after),
    }


def four_move_closure_audited(
    graph: Graph,
) -> tuple[Graph, CutAnalysis, list[dict[str, Any]], list[dict[str, Any]]]:
    """The maintained v2 closure with an exact audit after every accepted move."""
    current = graph
    analysis = v2.active_cuts(current)
    if not analysis.unique:
        raise ValueError(f"nonunique active cuts in {graph.name}")
    moves: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    while True:
        degrees = v2.graph_degrees(current)
        boundary_nodes = set(current.boundary_map.values())
        applied = False
        for node in current.nodes:
            if node not in boundary_nodes and degrees[node] == 2:
                candidate = v2.transform_series(current, node)
                checked = v2.verified_same_cuts(analysis, candidate)
                if checked is not None:
                    moves.append({"move": "series_bivalent", "object": node,
                                  "edges_before": len(current.edges), "edges_after": len(candidate.edges),
                                  "certified_move": True})
                    audits.append(move_audit(analysis, checked, "series_bivalent", node, candidate))
                    current, analysis, applied = candidate, checked, True
                    break
        if applied:
            continue
        for module, gateways in v2.module_candidates(current):
            capacity, unique = v2.module_capacity(current, module, gateways)
            if not unique:
                continue
            candidate = v2.transform_module(current, module, gateways, capacity)
            checked = v2.verified_same_cuts(analysis, candidate)
            if checked is not None and len(candidate.edges) < len(current.edges):
                object_name = "+".join(sorted(module))
                moves.append({"move": "exact_two_terminal_module", "object": object_name,
                              "edges_before": len(current.edges), "edges_after": len(candidate.edges),
                              "certified_move": True})
                audits.append(move_audit(analysis, checked, "exact_two_terminal_module", object_name, candidate))
                current, analysis, applied = candidate, checked, True
                break
        if applied:
            continue
        zero_columns = [index for index in range(len(current.edges))
                        if not any(row[index] for row in analysis.incidence)]
        terminal_zero = next((index for index in zero_columns
                              if set(current.edges[index]) & boundary_nodes), None)
        if terminal_zero is not None:
            u, v = current.edges[terminal_zero]
            candidate = v2.transform_contract(current, u, v, "_saturated")
            checked = v2.verified_same_cuts(analysis, candidate)
            if checked is not None:
                object_name = f"{u}-{v}"
                moves.append({"move": "saturated_terminal_zero_column_contraction",
                              "object": object_name, "edges_before": len(current.edges),
                              "edges_after": len(candidate.edges), "certified_move": True})
                audits.append(move_audit(analysis, checked, "saturated_terminal_zero_column_contraction",
                                         object_name, candidate))
                current, analysis = candidate, checked
                continue
        node_signatures = {node: tuple(row[index] for row in analysis.sides)
                           for index, node in enumerate(current.nodes)}
        pairs = [(u, v) for u, v in itertools.combinations(current.nodes, 2)
                 if node_signatures[u] == node_signatures[v]
                 and u not in boundary_nodes and v not in boundary_nodes]
        for u, v in pairs:
            candidate = v2.transform_contract(current, u, v, "_inseparable")
            checked = v2.verified_same_cuts(analysis, candidate)
            if checked is not None:
                object_name = f"{u}+{v}"
                moves.append({"move": "inseparable_vertex_contraction_parallel_sum",
                              "object": object_name, "edges_before": len(current.edges),
                              "edges_after": len(candidate.edges), "certified_move": True})
                audits.append(move_audit(analysis, checked, "inseparable_vertex_contraction_parallel_sum",
                                         object_name, candidate))
                current, analysis, applied = candidate, checked, True
                break
        if applied:
            continue
        if zero_columns:
            index = zero_columns[0]
            u, v = current.edges[index]
            candidate = v2.transform_contract(current, u, v, "_zero")
            checked = v2.verified_same_cuts(analysis, candidate)
            if checked is not None:
                object_name = f"{u}-{v}"
                moves.append({"move": "zero_column_contraction", "object": object_name,
                              "edges_before": len(current.edges), "edges_after": len(candidate.edges),
                              "certified_move": True})
                audits.append(move_audit(analysis, checked, "zero_column_contraction", object_name, candidate))
                current, analysis = candidate, checked
                continue
        break
    return current, analysis, moves, audits


def five_move_closure(
    graph: Graph,
) -> tuple[Graph, CutAnalysis, list[dict[str, Any]], list[dict[str, Any]]]:
    """Explore verified Delta-Y/Y-Delta presentations, folding four moves after each.

    Three replacement rounds are exhaustive for the maintained search family
    and include equal/intermediate presentations (the named K2,3 regression
    needs both Y-Delta and Delta-Y).  The depth bound prevents inverse cycling;
    the returned path minimizes residual deficiency first and edge count second.
    """
    initial_graph, initial_analysis, initial_moves, initial_audits = four_move_closure_audited(graph)
    initial_path = initial_moves
    queue: list[tuple[Graph, CutAnalysis, list[dict[str, Any]], list[dict[str, Any]], int]] = [
        (initial_graph, initial_analysis, initial_path, initial_audits, 0)
    ]
    seen = {graph_key(initial_graph)}
    states = [(initial_graph, initial_analysis, initial_path, initial_audits, 0)]
    cursor = 0
    while cursor < len(queue):
        current, analysis, path, audits, depth = queue[cursor]
        cursor += 1
        if depth == 3:
            continue
        for move_name, object_name, candidate in fifth_candidates(current):
            checked = v2.verified_same_cuts(analysis, candidate)
            if checked is None:
                continue
            folded_graph, folded_analysis, folded_moves, fold_audits = four_move_closure_audited(candidate)
            state_key = graph_key(folded_graph)
            if state_key in seen:
                continue
            seen.add(state_key)
            move = {
                "move": move_name,
                "object": object_name,
                "edges_before": len(current.edges),
                "edges_after": len(candidate.edges),
                "certified_move": True,
            }
            audit = {
                "move": move_name,
                "object": object_name,
                "region_count": len(analysis.regions),
                "all_region_values_preserved": checked.values == analysis.values,
                "unique_before": analysis.unique,
                "unique_after_move": checked.unique,
                "minimum_margin_after_move": float(checked.minimum_margin),
                "rank_recomputed_after_move": checked.rank,
                "residual_deficiency_after_move": deficiency(candidate, checked),
            }
            folded_path = path + [move] + folded_moves
            folded_audits = audits + [audit] + fold_audits
            state = (folded_graph, folded_analysis, folded_path, folded_audits, depth + 1)
            states.append(state)
            queue.append(state)
    best = min(
        states,
        key=lambda state: (
            deficiency(state[0], state[1]),
            len(state[0].edges),
            state[4],
            graph_key(state[0]),
        ),
    )
    return best[0], best[1], best[2], best[3]


def normalized_direction(values: list[int]) -> tuple[int, ...]:
    first = next((value for value in values if value), 0)
    if first < 0:
        values = [-value for value in values]
    return tuple(values)


def cycle_transport_directions(graph: Graph) -> list[tuple[str, tuple[int, ...]]]:
    """Alternating four-cycle directions underlying K2,3 transportation moves."""
    edge_index = {edge: index for index, edge in enumerate(graph.edges)}
    rows = []
    seen = set()
    for nodes in itertools.combinations(graph.nodes, 4):
        anchor = nodes[0]
        for partner in nodes[1:]:
            left = (anchor, partner)
            right = tuple(node for node in nodes if node not in left)
            required = [
                v2.edge(left[0], right[0]), v2.edge(left[0], right[1]),
                v2.edge(left[1], right[0]), v2.edge(left[1], right[1]),
            ]
            if any(item not in edge_index for item in required):
                continue
            vector = [0] * len(graph.edges)
            vector[edge_index[required[0]]] = 1
            vector[edge_index[required[1]]] = -1
            vector[edge_index[required[2]]] = -1
            vector[edge_index[required[3]]] = 1
            direction = normalized_direction(vector)
            if direction in seen:
                continue
            seen.add(direction)
            rows.append((f"{left[0]}+{left[1]} | {right[0]}+{right[1]}", direction))
    return rows


def k4_matching_directions(graph: Graph) -> list[tuple[str, tuple[int, ...]]]:
    edge_index = {edge: index for index, edge in enumerate(graph.edges)}
    rows = []
    seen = set()
    for nodes in itertools.combinations(graph.nodes, 4):
        u0, u1, u2, u3 = nodes
        complete = [v2.edge(left, right) for left, right in itertools.combinations(nodes, 2)]
        if any(item not in edge_index for item in complete):
            continue
        matchings = (
            (v2.edge(u0, u1), v2.edge(u2, u3)),
            (v2.edge(u0, u2), v2.edge(u1, u3)),
            (v2.edge(u0, u3), v2.edge(u1, u2)),
        )
        for left_index, right_index in itertools.combinations(range(3), 2):
            vector = [0] * len(graph.edges)
            for item in matchings[left_index]:
                vector[edge_index[item]] += 1
            for item in matchings[right_index]:
                vector[edge_index[item]] -= 1
            direction = normalized_direction(vector)
            if direction in seen:
                continue
            seen.add(direction)
            rows.append((f"K4={'+'.join(nodes)};M{left_index}-M{right_index}", direction))
    return rows


def direction_text(graph: Graph, direction: tuple[int, ...]) -> str:
    return " ".join(
        f"{coefficient:+d}*{u}-{v}"
        for coefficient, (u, v) in zip(direction, graph.edges)
        if coefficient
    )


def finite_direction_passes(
    graph: Graph, analysis: CutAnalysis, direction: tuple[int, ...]
) -> tuple[bool, float]:
    if not all(sum(a * b for a, b in zip(row, direction)) == 0 for row in analysis.incidence):
        return False, 0.0
    scale = sum(map(abs, direction))
    maximum = max(map(abs, direction))
    affected_weights = [weight for weight, coefficient in zip(graph.weights, direction) if coefficient]
    delta = min(
        analysis.minimum_margin / max(4 * scale, 1),
        min(affected_weights) / max(4 * maximum, 1),
    )
    for sign in (-1, 1):
        moved = v2.replace(
            graph,
            weighted_edges=tuple(
                (u, v, weight + sign * delta * coefficient)
                for (u, v, weight), coefficient in zip(graph.weighted_edges, direction)
            ),
        )
        moved_analysis = v2.active_cuts(moved)
        if not (
            moved_analysis.unique
            and moved_analysis.values == analysis.values
            and moved_analysis.incidence == analysis.incidence
        ):
            return False, float(delta)
    return True, float(delta)


def experimental_diagnostics(
    survivors: list[tuple[Graph, CutAnalysis, str, int]]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summaries = []
    details = []
    rules = (
        ("EXPERIMENTAL_K23_FOUR_CYCLE_TRANSPORT", cycle_transport_directions),
        ("EXPERIMENTAL_K4_OPPOSITE_PERFECT_MATCHING", k4_matching_directions),
    )
    for graph, analysis, carrier, seed in survivors:
        residual = deficiency(graph, analysis)
        for rule, generator in rules:
            candidates = generator(graph)
            accepted: list[tuple[int, ...]] = []
            for structure, direction in candidates:
                exact_kernel = all(
                    sum(a * b for a, b in zip(row, direction)) == 0
                    for row in analysis.incidence
                )
                finite_passes, delta = finite_direction_passes(graph, analysis, direction)
                if exact_kernel and finite_passes:
                    accepted.append(direction)
                details.append(
                    {
                        "carrier": carrier,
                        "seed": seed,
                        "experimental_rule": rule,
                        "experimental_not_in_certified_closure": True,
                        "structure": structure,
                        "direction": direction_text(graph, direction),
                        "exact_incidence_kernel": exact_kernel,
                        "finite_two_sided_invariance": finite_passes,
                        "delta": delta,
                    }
                )
            unique_accepted = sorted(set(accepted))
            span_rank = v2.rational_rank(unique_accepted) if unique_accepted else 0
            summaries.append(
                {
                    "carrier": carrier,
                    "seed": seed,
                    "residual_deficiency_before_experimental": residual,
                    "experimental_rule": rule,
                    "experimental_not_in_certified_closure": True,
                    "candidate_direction_count": len(candidates),
                    "accepted_direction_count": len(unique_accepted),
                    "accepted_span_rank": span_rank,
                    "fully_explains_residual": span_rank == residual and residual > 0,
                }
            )
    return summaries, details


def regression_rows() -> list[dict[str, Any]]:
    s55, carriers = v2.old_carriers()
    rows = []
    for seed in v2.REGRESSION_SEEDS:
        for carrier in carriers:
            weights = s55.generic_weights(carrier.base_weights, seed)
            graph = v2.graph_from_old(carrier, weights, seed)
            raw = v2.active_cuts(graph)
            reduced, final, moves, _audits = five_move_closure(graph)
            rows.append(
                {
                    "carrier": carrier.name,
                    "seed": seed,
                    "unique_all_regions": raw.unique,
                    "minimum_unique_cut_margin": float(raw.minimum_margin),
                    "raw_edges": len(graph.edges),
                    "raw_exact_rank": raw.rank,
                    "raw_deficiency": deficiency(graph, raw),
                    "reduction_moves": "|".join(move["move"] for move in moves),
                    "fifth_move_count": sum(move["move"] in {"delta_y", "y_delta"} for move in moves),
                    "reduced_edges": len(reduced.edges),
                    "reduced_exact_rank": final.rank,
                    "residual_deficiency": deficiency(reduced, final),
                    "all_region_values_preserved": raw.values == final.values,
                    "unique_after_closure": final.unique,
                }
            )
    return rows


def five_move_search() -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[tuple[Graph, CutAnalysis, str, int]]
]:
    rows = []
    named_audits: list[dict[str, Any]] = []
    survivors: list[tuple[Graph, CutAnalysis, str, int]] = []
    for carrier in v2.search_carriers():
        for seed in v2.SEARCH_SEEDS:
            graph = v2.seeded_weights(carrier, seed)
            raw = v2.active_cuts(graph)
            if raw.rank == len(graph.edges):
                reduced, final, moves, audits = graph, raw, [], []
                four_move_residual = 0
            else:
                four_graph, four_analysis, four_moves = v2.reduction_closure(graph)
                four_move_residual = deficiency(four_graph, four_analysis)
                if four_move_residual:
                    reduced, final, moves, audits = five_move_closure(graph)
                else:
                    reduced, final, moves, audits = four_graph, four_analysis, four_moves, []
            residual = deficiency(reduced, final)
            if residual:
                survivors.append((reduced, final, carrier.name, seed))
            named = carrier.name == "K23_bipartite__b6__leaf_offset0" and seed == 31
            rows.append(
                {
                    "carrier": carrier.name,
                    "topology_family": carrier.family,
                    "seed": seed,
                    "boundary_count": len(graph.boundaries),
                    "raw_edge_count": len(graph.edges),
                    "raw_exact_rank": raw.rank,
                    "raw_deficiency": deficiency(graph, raw),
                    "four_move_residual_deficiency": four_move_residual,
                    "minimum_unique_cut_margin": float(raw.minimum_margin),
                    "closure_move_count": len(moves),
                    "closure_moves": "|".join(move["move"] for move in moves),
                    "fifth_move_count": sum(move["move"] in {"delta_y", "y_delta"} for move in moves),
                    "reduced_edge_count": len(reduced.edges),
                    "reduced_exact_rank": final.rank,
                    "residual_deficiency": residual,
                    "all_region_values_preserved": raw.values == final.values,
                    "unique_after_closure": final.unique,
                    "named_regression": named,
                }
            )
            if named:
                for move_index, audit in enumerate(audits):
                    named_audits.append({"carrier": carrier.name, "seed": seed,
                                         "move_index": move_index, **audit})
                named_audits.append(
                    {
                        "carrier": carrier.name,
                        "seed": seed,
                        "move_index": "final",
                        "move": "closure_result",
                        "object": "named_regression",
                        "region_count": len(final.regions),
                        "all_region_values_preserved": raw.values == final.values,
                        "unique_before": raw.unique,
                        "unique_after_move": final.unique,
                        "minimum_margin_after_move": float(final.minimum_margin),
                        "rank_recomputed_after_move": final.rank,
                        "residual_deficiency_after_move": residual,
                    }
                )
    return rows, named_audits, survivors


def run() -> dict[str, Any]:
    started = time.perf_counter()
    regressions = regression_rows()
    search, named, survivor_states = five_move_search()
    experimental, experimental_details = experimental_diagnostics(survivor_states)
    histogram = Counter(row["residual_deficiency"] for row in search if row["residual_deficiency"])
    four_survivor_ids = {
        (row["carrier"], row["seed"])
        for row in search
        if row["four_move_residual_deficiency"]
    }
    five_survivor_ids = {
        (row["carrier"], row["seed"])
        for row in search
        if row["residual_deficiency"]
    }
    experimental_counts = {
        rule: sum(
            row["fully_explains_residual"]
            for row in experimental
            if row["experimental_rule"] == rule
        )
        for rule in sorted({row["experimental_rule"] for row in experimental})
    }
    return {
        "pin": [
            {
                "dependency": V2_PATH.name,
                "expected_sha256": V2_SHA256,
                "actual_sha256": sha256(V2_PATH),
                "passes": sha256(V2_PATH) == V2_SHA256,
            }
        ],
        "regressions": regressions,
        "search": search,
        "named_regression": named,
        "experimental": experimental,
        "experimental_details": experimental_details,
        "summary": [
            {
                "evaluated_weighted_carriers": len(search),
                "four_move_survivors": len(four_survivor_ids),
                "explained_by_fifth_move": len(four_survivor_ids - five_survivor_ids),
                "five_move_survivors": len(five_survivor_ids),
                "residual_deficiency_histogram": "|".join(
                    f"{key}:{value}" for key, value in sorted(histogram.items())
                ),
                "experimental_k23_fully_explained": experimental_counts[
                    "EXPERIMENTAL_K23_FOUR_CYCLE_TRANSPORT"
                ],
                "experimental_k4_fully_explained": experimental_counts[
                    "EXPERIMENTAL_K4_OPPOSITE_PERFECT_MATCHING"
                ],
            }
        ],
        "outcome": "FIVE_MOVE_CLOSURE_LEAVES_13_RESIDUAL_SURVIVORS_EXPERIMENTAL_SIXTH_MOVES_EXPLAIN_NONE",
        "runtime_seconds": time.perf_counter() - started,
    }


if __name__ == "__main__":
    result = run()
    print(result["summary"][0])
    print(f"runtime_seconds={result['runtime_seconds']:.3f}")
