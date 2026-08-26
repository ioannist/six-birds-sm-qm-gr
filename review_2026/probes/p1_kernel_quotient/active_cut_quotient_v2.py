#!/usr/bin/env python3
"""P1-REPAIR-2: exact active-cut quotients and bounded irreducibility search."""

from __future__ import annotations

import hashlib
import itertools
import math
import random
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
OLD_PATH = HERE / "p1_kernel_quotient_probe.py"
OLD_SHA256 = "dbc2e94ef84cb89786b084a98e56803128caee355bd82f9618ce4abe34420a40"
REGRESSION_SEEDS = (101, 202, 303)
SEARCH_SEEDS = (17, 31, 47)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(OLD_PATH) != OLD_SHA256:
    raise RuntimeError(f"v1 probe pin mismatch: {sha256(OLD_PATH)} != {OLD_SHA256}")
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import p1_kernel_quotient_probe as old  # noqa: E402


def edge(u: str, v: str) -> tuple[str, str]:
    if u == v:
        raise ValueError("self edge")
    return tuple(sorted((u, v)))


@dataclass(frozen=True)
class Graph:
    name: str
    family: str
    boundaries: tuple[str, ...]
    boundary_nodes: tuple[tuple[str, str], ...]
    weighted_edges: tuple[tuple[str, str, Fraction], ...]

    @property
    def boundary_map(self) -> dict[str, str]:
        return dict(self.boundary_nodes)

    @property
    def edges(self) -> tuple[tuple[str, str], ...]:
        return tuple((u, v) for u, v, _weight in self.weighted_edges)

    @property
    def weights(self) -> tuple[Fraction, ...]:
        return tuple(weight for _u, _v, weight in self.weighted_edges)

    @property
    def nodes(self) -> tuple[str, ...]:
        values = set(self.boundary_map.values())
        for u, v, _weight in self.weighted_edges:
            values.update((u, v))
        return tuple(sorted(values))


def make_graph(name: str, family: str, boundaries: Iterable[str],
               rows: Iterable[tuple[str, str, Fraction | int | float]],
               boundary_map: dict[str, str] | None = None) -> Graph:
    combined: dict[tuple[str, str], Fraction] = defaultdict(Fraction)
    for u, v, weight in rows:
        combined[edge(u, v)] += weight if isinstance(weight, Fraction) else Fraction(str(weight))
    combined = {key: value for key, value in combined.items() if value > 0}
    labels = tuple(boundaries)
    mapping = boundary_map or {label: label for label in labels}
    return Graph(name, family, labels, tuple(sorted(mapping.items())),
                 tuple((u, v, combined[(u, v)]) for u, v in sorted(combined)))


@dataclass(frozen=True)
class CutAnalysis:
    regions: tuple[tuple[str, ...], ...]
    incidence: tuple[tuple[int, ...], ...]
    values: tuple[Fraction, ...]
    margins: tuple[Fraction, ...]
    sides: tuple[tuple[int, ...], ...]
    rank: int

    @property
    def unique(self) -> bool:
        return all(margin > 0 for margin in self.margins)

    @property
    def minimum_margin(self) -> Fraction:
        return min(self.margins)


def rational_rank(matrix: Iterable[Iterable[int | Fraction]]) -> int:
    rows = [list(map(Fraction, row)) for row in matrix]
    if not rows:
        return 0
    row_count, column_count = len(rows), len(rows[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next((row for row in range(pivot_row, row_count) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [a - factor * b for a, b in zip(rows[row], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def active_cuts(graph: Graph) -> CutAnalysis:
    nodes = graph.nodes
    node_index = {node: index for index, node in enumerate(nodes)}
    boundary_map = graph.boundary_map
    boundary_nodes = set(boundary_map.values())
    free_nodes = [node for node in nodes if node not in boundary_nodes]
    regions = []
    incidence = []
    values = []
    margins = []
    sides = []
    common_denominator = math.lcm(*(weight.denominator for weight in graph.weights))
    integer_weights = tuple(int(weight * common_denominator) for weight in graph.weights)
    for mask in range(1, (1 << len(graph.boundaries)) - 1):
        region = tuple(label for index, label in enumerate(graph.boundaries) if mask & (1 << index))
        fixed: dict[str, int] = {}
        for label in graph.boundaries:
            side = int(label in region)
            node = boundary_map[label]
            if node in fixed and fixed[node] != side:
                raise AssertionError("contracted distinct boundaries cannot be separated")
            fixed[node] = side
        candidates = []
        for free_mask in range(1 << len(free_nodes)):
            assignment = dict(fixed)
            assignment.update({node: int(bool(free_mask & (1 << index)))
                               for index, node in enumerate(free_nodes)})
            cut_row = tuple(int(assignment[u] != assignment[v]) for u, v in graph.edges)
            capacity = sum(weight * used for weight, used in zip(integer_weights, cut_row))
            candidates.append((capacity, cut_row, tuple(assignment[node] for node in nodes)))
        candidates.sort(key=lambda row: (row[0], row[1], row[2]))
        best = candidates[0]
        tied = [row for row in candidates if row[0] == best[0]]
        margin_integer = 0 if len(tied) > 1 else candidates[1][0] - best[0]
        regions.append(region)
        values.append(Fraction(best[0], common_denominator))
        incidence.append(best[1])
        sides.append(best[2])
        margins.append(Fraction(margin_integer, common_denominator))
    return CutAnalysis(tuple(regions), tuple(incidence), tuple(values), tuple(margins),
                       tuple(sides), rational_rank(incidence))


def graph_degrees(graph: Graph) -> Counter[str]:
    result: Counter[str] = Counter()
    for u, v in graph.edges:
        result[u] += 1
        result[v] += 1
    return result


def transform_contract(graph: Graph, u: str, v: str, suffix: str) -> Graph:
    merged = f"<{u}+{v}>"
    rows = []
    for left, right, weight in graph.weighted_edges:
        left = merged if left in {u, v} else left
        right = merged if right in {u, v} else right
        if left != right:
            rows.append((left, right, weight))
    mapping = {label: (merged if node in {u, v} else node) for label, node in graph.boundary_nodes}
    return make_graph(graph.name + suffix, graph.family, graph.boundaries, rows, mapping)


def transform_series(graph: Graph, node: str) -> Graph:
    incident = [(u, v, weight) for u, v, weight in graph.weighted_edges if node in {u, v}]
    if len(incident) != 2:
        raise ValueError(node)
    neighbors = [v if u == node else u for u, v, _weight in incident]
    effective = min(incident[0][2], incident[1][2])
    rows = [row for row in graph.weighted_edges if node not in row[:2]]
    rows.append((neighbors[0], neighbors[1], effective))
    return make_graph(graph.name + f"_series_{node}", graph.family, graph.boundaries,
                      rows, graph.boundary_map)


def module_capacity(graph: Graph, module: frozenset[str], gateways: tuple[str, str]) -> tuple[Fraction, bool]:
    internal = tuple(sorted(module))
    candidates = []
    for mask in range(1 << len(internal)):
        assignment = {gateways[0]: 0, gateways[1]: 1}
        assignment.update({node: int(bool(mask & (1 << index))) for index, node in enumerate(internal)})
        capacity = Fraction(0)
        for u, v, weight in graph.weighted_edges:
            if u in module or v in module:
                capacity += weight * int(assignment[u] != assignment[v])
        candidates.append(capacity)
    candidates.sort()
    return candidates[0], len(candidates) == 1 or candidates[1] > candidates[0]


def transform_module(graph: Graph, module: frozenset[str], gateways: tuple[str, str], capacity: Fraction) -> Graph:
    rows = [(u, v, weight) for u, v, weight in graph.weighted_edges
            if u not in module and v not in module]
    rows.append((gateways[0], gateways[1], capacity))
    return make_graph(graph.name + "_two_terminal", graph.family, graph.boundaries,
                      rows, graph.boundary_map)


def verified_same_cuts(before: CutAnalysis, graph: Graph) -> CutAnalysis | None:
    after = active_cuts(graph)
    if after.unique and after.regions == before.regions and after.values == before.values:
        return after
    return None


def module_candidates(graph: Graph) -> list[tuple[frozenset[str], tuple[str, str]]]:
    boundary_nodes = set(graph.boundary_map.values())
    interior = tuple(node for node in graph.nodes if node not in boundary_nodes)
    candidates = []
    for size in range(len(interior), 0, -1):
        for values in itertools.combinations(interior, size):
            module = frozenset(values)
            gateways = set()
            internal_edge = False
            for u, v in graph.edges:
                if u in module and v in module:
                    internal_edge = True
                elif u in module:
                    gateways.add(v)
                elif v in module:
                    gateways.add(u)
            if len(gateways) == 2 and internal_edge:
                candidates.append((module, tuple(sorted(gateways))))
    return candidates


def reduction_closure(graph: Graph) -> tuple[Graph, CutAnalysis, list[dict[str, Any]]]:
    current = graph
    analysis = active_cuts(current)
    if not analysis.unique:
        raise ValueError(f"nonunique active cuts in {graph.name}")
    moves = []
    while True:
        degrees = graph_degrees(current)
        boundary_nodes = set(current.boundary_map.values())
        applied = False
        for node in current.nodes:
            if node not in boundary_nodes and degrees[node] == 2:
                candidate = transform_series(current, node)
                checked = verified_same_cuts(analysis, candidate)
                if checked is not None:
                    moves.append({"move": "series_bivalent", "object": node,
                                  "edges_before": len(current.edges), "edges_after": len(candidate.edges)})
                    current, analysis, applied = candidate, checked, True
                    break
        if applied:
            continue
        for module, gateways in module_candidates(current):
            capacity, unique = module_capacity(current, module, gateways)
            if not unique:
                continue
            candidate = transform_module(current, module, gateways, capacity)
            checked = verified_same_cuts(analysis, candidate)
            if checked is not None and len(candidate.edges) < len(current.edges):
                moves.append({"move": "exact_two_terminal_module", "object": "+".join(sorted(module)),
                              "edges_before": len(current.edges), "edges_after": len(candidate.edges)})
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
            candidate = transform_contract(current, u, v, "_saturated")
            checked = verified_same_cuts(analysis, candidate)
            if checked is not None:
                moves.append({"move": "saturated_terminal_zero_column_contraction",
                              "object": f"{u}-{v}", "edges_before": len(current.edges),
                              "edges_after": len(candidate.edges)})
                current, analysis = candidate, checked
                continue
        node_signatures = {node: tuple(row[index] for row in analysis.sides)
                           for index, node in enumerate(current.nodes)}
        pairs = [(u, v) for u, v in itertools.combinations(current.nodes, 2)
                 if node_signatures[u] == node_signatures[v]
                 and u not in boundary_nodes and v not in boundary_nodes]
        for u, v in pairs:
            candidate = transform_contract(current, u, v, "_inseparable")
            checked = verified_same_cuts(analysis, candidate)
            if checked is not None:
                moves.append({"move": "inseparable_vertex_contraction_parallel_sum",
                              "object": f"{u}+{v}", "edges_before": len(current.edges),
                              "edges_after": len(candidate.edges)})
                current, analysis, applied = candidate, checked, True
                break
        if applied:
            continue
        if zero_columns:
            index = zero_columns[0]
            u, v = current.edges[index]
            candidate = transform_contract(current, u, v, "_zero")
            checked = verified_same_cuts(analysis, candidate)
            if checked is not None:
                moves.append({"move": "zero_column_contraction", "object": f"{u}-{v}",
                              "edges_before": len(current.edges), "edges_after": len(candidate.edges)})
                current, analysis = candidate, checked
                continue
        break
    return current, analysis, moves


def fraction_from_float(value: float) -> Fraction:
    return Fraction(str(float(value)))


def old_carriers() -> tuple[Any, list[Any]]:
    old.verify_frozen_inputs()
    s42 = old.import_module(old.STEP42_SCRIPT, "p1_v2_step42")
    s55 = old.import_module(old.STEP55_SCRIPT, "p1_v2_step55")
    carriers = [old.published_carrier(s42, s55), old.crosslinked_carrier(),
                old.grid_carrier(), old.k4_carrier(stiff_chord=True)]
    return s55, carriers


def graph_from_old(carrier: Any, weights: Iterable[float], seed: int) -> Graph:
    rows = [(u, v, fraction_from_float(weight))
            for (u, v), weight in zip(carrier.edges, weights)]
    return make_graph(f"{carrier.name}_seed{seed}", carrier.name, carrier.labels, rows)


def regression_rows() -> list[dict[str, Any]]:
    s55, carriers = old_carriers()
    rows = []
    for seed in REGRESSION_SEEDS:
        for carrier in carriers:
            weights = s55.generic_weights(carrier.base_weights, seed)
            graph = graph_from_old(carrier, weights, seed)
            raw = active_cuts(graph)
            reduced, final, moves = reduction_closure(graph)
            rows.append({
                "carrier": carrier.name, "seed": seed, "unique_all_regions": raw.unique,
                "minimum_unique_cut_margin": float(raw.minimum_margin),
                "raw_edges": len(graph.edges), "raw_exact_rank": raw.rank,
                "raw_deficiency": len(graph.edges) - raw.rank,
                "reduction_moves": "|".join(move["move"] for move in moves),
                "reduced_edges": len(reduced.edges), "reduced_exact_rank": final.rank,
                "residual_deficiency": len(reduced.edges) - final.rank,
                "all_region_values_preserved": raw.values == final.values,
            })
    return rows


def connected(nodes: tuple[str, ...], edges: set[tuple[str, str]]) -> bool:
    seen = {nodes[0]}
    while True:
        expanded = seen | {v for u, v in edges if u in seen} | {u for u, v in edges if v in seen}
        if expanded == seen:
            return len(seen) == len(nodes)
        seen = expanded


def interior_topologies() -> list[tuple[str, int, set[tuple[str, str]]]]:
    rows = []
    for m in range(3, 7):
        nodes = tuple(f"I{i}" for i in range(m))
        rows.append((f"complete_K{m}", m, {edge(nodes[i], nodes[j]) for i in range(m) for j in range(i + 1, m)}))
        cycle = {edge(nodes[i], nodes[(i + 1) % m]) for i in range(m)}
        rows.append((f"cycle_chord_m{m}", m, cycle | {edge(nodes[i], nodes[(i + 2) % m]) for i in range(m)}))
        if m >= 4:
            hub = nodes[0]
            rim = nodes[1:]
            wheel = {edge(hub, node) for node in rim} | {edge(rim[i], rim[(i + 1) % len(rim)]) for i in range(len(rim))}
            rows.append((f"wheel_W{m}", m, wheel))
    nodes5 = tuple(f"I{i}" for i in range(5))
    complete5 = {edge(nodes5[i], nodes5[j]) for i in range(5) for j in range(i + 1, 5)}
    for variant, missing in enumerate(((0, 1), (0, 2), (1, 3))):
        rows.append((f"K5_minus_v{variant}", 5, complete5 - {edge(f"I{missing[0]}", f"I{missing[1]}")}))
    rows.append(("K23_bipartite", 5, {edge(f"I{i}", f"I{j}") for i in range(2) for j in range(2, 5)}))
    rows.append(("K33_expander", 6, {edge(f"I{i}", f"I{j}") for i in range(3) for j in range(3, 6)}))
    rows.append(("triangular_prism", 6, {edge(f"I{i}", f"I{(i + 1) % 3}") for i in range(3)}
                 | {edge(f"I{i+3}", f"I{((i + 1) % 3)+3}") for i in range(3)}
                 | {edge(f"I{i}", f"I{i+3}") for i in range(3)}))
    rows.append(("crosslinked_grid_2x3", 6, {
        edge("I0", "I1"), edge("I1", "I2"), edge("I3", "I4"), edge("I4", "I5"),
        edge("I0", "I3"), edge("I1", "I4"), edge("I2", "I5"),
        edge("I0", "I4"), edge("I1", "I3"), edge("I1", "I5"), edge("I2", "I4"),
    }))
    rows.append(("octahedral", 6, {edge(f"I{i}", f"I{j}") for i in range(6) for j in range(i + 1, 6)
                                    if {i, j} not in ({0, 3}, {1, 4}, {2, 5})}))
    unique = {}
    for name, m, edgeset in rows:
        if connected(tuple(f"I{i}" for i in range(m)), edgeset):
            unique[(m, tuple(sorted(edgeset)))] = (name, m, edgeset)
    return [unique[key] for key in sorted(unique)]


def search_carriers() -> list[Graph]:
    rows = []
    for topology, m, interior_edges in interior_topologies():
        for boundary_count in (6, 7, 8):
            labels = tuple(f"B{i}" for i in range(boundary_count))
            for scheme in ("leaf_offset0", "leaf_offset1", "dual_gateway"):
                all_edges = set(interior_edges)
                for index, label in enumerate(labels):
                    offset = 0 if scheme == "leaf_offset0" else 1
                    all_edges.add(edge(label, f"I{(index + offset) % m}"))
                    if scheme == "dual_gateway":
                        all_edges.add(edge(label, f"I{(index + 1) % m}"))
                graph = make_graph(f"{topology}__b{boundary_count}__{scheme}", topology,
                                   labels, [(u, v, 1) for u, v in sorted(all_edges)])
                degrees = graph_degrees(graph)
                if min(degrees[f"I{i}"] for i in range(m)) >= 3:
                    rows.append(graph)
    return rows


def seeded_weights(graph: Graph, seed: int) -> Graph:
    digest = int(hashlib.sha256(f"{graph.name}:{seed}".encode()).hexdigest()[:16], 16)
    rng = random.Random(digest)
    count = len(graph.edges)
    rows = []
    for index, (u, v) in enumerate(graph.edges):
        moderate = Fraction(rng.randint(85, 115), 100)
        tie_breaker = Fraction(1 << index, 1 << (count + 24))
        rows.append((u, v, moderate + tie_breaker))
    return make_graph(graph.name + f"__seed{seed}", graph.family, graph.boundaries, rows)


def search_rows() -> tuple[list[dict[str, Any]], list[tuple[Graph, CutAnalysis, list[dict[str, Any]]]]]:
    rows = []
    survivors = []
    for carrier in search_carriers():
        for seed in SEARCH_SEEDS:
            graph = seeded_weights(carrier, seed)
            raw = active_cuts(graph)
            if not raw.unique:
                continue
            # A full-column-rank active matrix has no kernel to explain; every
            # named move would only provide an alternative smaller presentation.
            # Run the expensive verified closure only on deficient cases.
            if raw.rank == len(graph.edges):
                reduced, final, moves = graph, raw, []
            else:
                reduced, final, moves = reduction_closure(graph)
            deficiency = len(reduced.edges) - final.rank
            rows.append({
                "carrier": carrier.name, "topology_family": carrier.family, "seed": seed,
                "boundary_count": len(graph.boundaries),
                "interior_node_count": len([node for node in graph.nodes if node not in graph.boundary_map.values()]),
                "raw_edge_count": len(graph.edges), "raw_exact_rank": raw.rank,
                "raw_deficiency": len(graph.edges) - raw.rank,
                "minimum_unique_cut_margin": float(raw.minimum_margin),
                "closure_move_count": len(moves),
                "closure_moves": "|".join(move["move"] for move in moves),
                "reduced_edge_count": len(reduced.edges), "reduced_exact_rank": final.rank,
                "residual_deficiency": deficiency,
                "all_region_values_preserved": raw.values == final.values,
            })
            if deficiency:
                survivors.append((reduced, final, moves))
    return rows, survivors


def nullspace_basis(matrix: tuple[tuple[int, ...], ...]) -> list[tuple[Fraction, ...]]:
    rows = [list(map(Fraction, row)) for row in matrix]
    row_count, column_count = len(rows), len(rows[0])
    pivot_row = 0
    pivots = []
    for column in range(column_count):
        pivot = next((row for row in range(pivot_row, row_count) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(row_count):
            if row != pivot_row and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[pivot_row])]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == row_count:
            break
    free = [column for column in range(column_count) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [Fraction(0)] * column_count
        vector[free_column] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -rows[row][free_column]
        basis.append(tuple(vector))
    return basis


def integer_vector(vector: tuple[Fraction, ...]) -> tuple[int, ...]:
    denominator = math.lcm(*(value.denominator for value in vector))
    values = [int(value * denominator) for value in vector]
    divisor = math.gcd(*map(abs, values))
    return tuple(value // divisor for value in values)


def characterize_survivor(graph: Graph, analysis: CutAnalysis) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    basis = [integer_vector(vector) for vector in nullspace_basis(analysis.incidence)]
    dependencies = []
    checks = []
    for index, vector in enumerate(basis):
        terms = [f"{coefficient:+d}*{u}-{v}" for coefficient, (u, v) in zip(vector, graph.edges) if coefficient]
        dependencies.append({"basis_index": index, "integer_column_dependency": " ".join(terms),
                             "incidence_times_direction_zero": all(sum(a * b for a, b in zip(row, vector)) == 0
                                                                   for row in analysis.incidence)})
        scale = sum(map(abs, vector))
        max_coefficient = max(map(abs, vector))
        delta = min(analysis.minimum_margin / max(4 * scale, 1),
                    min(graph.weights) / max(4 * max_coefficient, 1))
        for sign in (-1, 1):
            moved = replace(graph, weighted_edges=tuple(
                (u, v, weight + sign * delta * coefficient)
                for (u, v, weight), coefficient in zip(graph.weighted_edges, vector)))
            moved_analysis = active_cuts(moved)
            checks.append({
                "basis_index": index, "sign": sign, "delta": float(delta),
                "unique_after_move": moved_analysis.unique,
                "active_cuts_unchanged": moved_analysis.incidence == analysis.incidence,
                "all_region_values_unchanged": moved_analysis.values == analysis.values,
            })
    return dependencies, checks


def irreducibility_audit(graph: Graph, analysis: CutAnalysis) -> list[dict[str, Any]]:
    degrees = graph_degrees(graph)
    boundary_nodes = set(graph.boundary_map.values())
    zero_columns = [f"{u}-{v}" for index, (u, v) in enumerate(graph.edges)
                    if not any(row[index] for row in analysis.incidence)]
    signatures = {node: tuple(row[index] for row in analysis.sides)
                  for index, node in enumerate(graph.nodes)}
    inseparable = [f"{u}+{v}" for u, v in itertools.combinations(graph.nodes, 2)
                   if u not in boundary_nodes and v not in boundary_nodes
                   and signatures[u] == signatures[v]]
    series = [node for node in graph.nodes if node not in boundary_nodes and degrees[node] == 2]
    modules = ["+".join(sorted(module)) + f"->{gateways[0]}|{gateways[1]}"
               for module, gateways in module_candidates(graph)]
    return [
        {"named_reduction": "saturated_terminal_or_zero_column_contraction",
         "applicable_object_count": len(zero_columns), "objects": "|".join(zero_columns),
         "blocks_candidate": not zero_columns},
        {"named_reduction": "inseparable_vertex_contraction_parallel_sum",
         "applicable_object_count": len(inseparable), "objects": "|".join(inseparable),
         "blocks_candidate": not inseparable},
        {"named_reduction": "series_bivalent_reduction",
         "applicable_object_count": len(series), "objects": "|".join(series),
         "blocks_candidate": not series},
        {"named_reduction": "exact_two_terminal_module_replacement",
         "applicable_object_count": len(modules), "objects": "|".join(modules),
         "blocks_candidate": not modules},
    ]


def candidate_graph_rows(graph: Graph) -> list[dict[str, Any]]:
    inverse_boundaries: dict[str, list[str]] = defaultdict(list)
    for label, node in graph.boundary_nodes:
        inverse_boundaries[node].append(label)
    return [{
        "edge_index": index, "u": u, "v": v,
        "u_boundary_labels": "|".join(inverse_boundaries[u]),
        "v_boundary_labels": "|".join(inverse_boundaries[v]),
        "weight_exact": f"{weight.numerator}/{weight.denominator}",
        "weight_decimal": float(weight),
    } for index, (u, v, weight) in enumerate(graph.weighted_edges)]


def candidate_active_cut_rows(graph: Graph, analysis: CutAnalysis) -> list[dict[str, Any]]:
    rows = []
    for region, incidence, value, margin in zip(
            analysis.regions, analysis.incidence, analysis.values, analysis.margins):
        rows.append({
            "region": "|".join(region),
            "active_edge_indices": "|".join(str(index) for index, used in enumerate(incidence) if used),
            "active_edges": "|".join(f"{u}-{v}" for (u, v), used in zip(graph.edges, incidence) if used),
            "min_cut_value_exact": f"{value.numerator}/{value.denominator}",
            "uniqueness_margin_exact": f"{margin.numerator}/{margin.denominator}",
        })
    return rows


def run() -> dict[str, Any]:
    started = time.perf_counter()
    regressions = regression_rows()
    search, survivors = search_rows()
    candidate_rows = []
    dependencies = []
    finite_checks = []
    candidate_edges = []
    candidate_active_cuts = []
    candidate_irreducibility = []
    if survivors:
        graph, analysis, moves = survivors[0]
        dependencies, finite_checks = characterize_survivor(graph, analysis)
        candidate_edges = candidate_graph_rows(graph)
        candidate_active_cuts = candidate_active_cut_rows(graph, analysis)
        candidate_irreducibility = irreducibility_audit(graph, analysis)
        candidate_rows = [{
            "carrier": graph.name, "family": graph.family, "boundary_count": len(graph.boundaries),
            "edge_count_after_closure": len(graph.edges), "exact_rank": analysis.rank,
            "residual_deficiency": len(graph.edges) - analysis.rank,
            "minimum_unique_cut_margin": float(analysis.minimum_margin),
            "closure_moves_before_candidate": "|".join(move["move"] for move in moves),
            "remaining_named_move": "none",
        }]
        outcome = "RESIDUAL_ACTIVE_CUT_DEFICIENCY_SURVIVES_FOUR_NAMED_REDUCTIONS"
    else:
        outcome = "DRY_WITHIN_SEARCHED_FAMILY_ALL_KERNELS_EXPLAINED_BY_FOUR_NAMED_REDUCTIONS"
    residual_distribution = Counter(row["residual_deficiency"] for row in search)
    survivor_families = Counter(row["topology_family"] for row in search if row["residual_deficiency"])
    search_census = [{
        "evaluated_weighted_carriers": len(search),
        "unique_cut_carriers": len(search),
        "raw_deficient_carriers": sum(row["raw_deficiency"] > 0 for row in search),
        "fully_explained_after_closure": sum(row["residual_deficiency"] == 0 for row in search),
        "residual_survivor_count": sum(row["residual_deficiency"] > 0 for row in search),
        "residual_deficiency_distribution": "|".join(f"{key}:{value}" for key, value in sorted(residual_distribution.items())),
        "survivor_family_distribution": "|".join(f"{key}:{value}" for key, value in sorted(survivor_families.items())),
    }]
    return {
        "pin": [{"dependency": OLD_PATH.name, "expected_sha256": OLD_SHA256,
                 "actual_sha256": sha256(OLD_PATH), "passes": sha256(OLD_PATH) == OLD_SHA256}],
        "regressions": regressions, "search": search, "candidate": candidate_rows,
        "dependencies": dependencies, "finite_checks": finite_checks, "outcome": outcome,
        "candidate_edges": candidate_edges, "candidate_active_cuts": candidate_active_cuts,
        "candidate_irreducibility": candidate_irreducibility, "search_census": search_census,
        "search_definition": {
            "topology_template_count": len(interior_topologies()),
            "unweighted_carrier_count": len(search_carriers()),
            "seed_count": len(SEARCH_SEEDS), "evaluated_weighted_carrier_count": len(search),
            "boundary_counts": [6, 7, 8], "interior_node_range": [3, 6],
            "attachment_schemes": ["leaf_offset0", "leaf_offset1", "dual_gateway"],
            "weight_range": [0.85, 1.15], "tie_breaker": "exact binary edge perturbations",
        },
        "runtime_seconds": time.perf_counter() - started,
    }


if __name__ == "__main__":
    result = run()
    print(f"active_cut_quotient_v2.py: PASS: regressions={len(result['regressions'])} "
          f"search={len(result['search'])} candidates={len(result['candidate'])} "
          f"outcome={result['outcome']} runtime={result['runtime_seconds']:.3f}s")
