#!/usr/bin/env python3
"""Exact-rational cut, closure, interval, and equivalence machinery.

Every capacity-dependent decision in this module is made with ``Fraction``.
The terminal fingerprint is always rebuilt by exhaustive cut enumeration.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import math
import sys
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import networkx as nx


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
P1_DIR = REPO_ROOT / "review_2026/probes/p1_kernel_quotient"
V2_PATH = P1_DIR / "active_cut_quotient_v2.py"
V3_PATH = P1_DIR / "active_cut_quotient_v3.py"
SURVIVOR_PATH = P1_DIR / "p1_v3_survivors.csv"
PINS = {
    V2_PATH: "adcfa43bf35fc2994c9f46fa57d9f9d380e86d6a5eac92a55c7e036a9fea9cc2",
    V3_PATH: "852c3a53e9fe7358c09d5dd60fcdedd28fe2c42d13977dad3390f941479b116d",
    SURVIVOR_PATH: "a0adf2a6dfc97aafdc385beed4ff63d9e90f4f38bcd95e861c25d3097525df07",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> None:
    for path, expected in PINS.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"pin mismatch for {path}: {actual} != {expected}")


def _load_module(name: str, path: Path):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


verify_pins()
if str(P1_DIR) not in sys.path:
    sys.path.insert(0, str(P1_DIR))
v2 = _load_module("prog3_pinned_v2", V2_PATH)
# v3 imports active_cut_quotient_v2 by its historical module name.
sys.modules.setdefault("active_cut_quotient_v2", v2)
v3 = _load_module("prog3_pinned_v3", V3_PATH)
Graph = v2.Graph


@dataclass(frozen=True)
class RegionEnumeration:
    region: tuple[str, ...]
    value: Fraction
    margin: Fraction
    active_rows: tuple[tuple[int, ...], ...]
    active_sides: tuple[tuple[int, ...], ...]
    candidates: tuple[tuple[Fraction, tuple[int, ...], tuple[int, ...]], ...]


@dataclass(frozen=True)
class ExactAnalysis:
    regions: tuple[RegionEnumeration, ...]
    incidence: tuple[tuple[int, ...], ...]
    values: tuple[Fraction, ...]
    margins: tuple[Fraction, ...]
    sides: tuple[tuple[int, ...], ...]
    rank: int

    @property
    def unique(self) -> bool:
        return all(len(region.active_sides) == 1 for region in self.regions)

    @property
    def minimum_margin(self) -> Fraction:
        return min(self.margins)


@dataclass(frozen=True)
class ExactInterval:
    lower: Fraction | None
    upper: Fraction | None

    def contains_strictly(self, value: Fraction) -> bool:
        return (self.lower is None or self.lower < value) and (
            self.upper is None or value < self.upper
        )

    @property
    def nondegenerate_around_zero(self) -> bool:
        return (self.lower is None or self.lower < 0) and (
            self.upper is None or self.upper > 0
        )


@dataclass(frozen=True)
class ClosureState:
    graph: Any
    analysis: ExactAnalysis
    path: tuple[tuple[str, str], ...]
    replacement_depth: int


@dataclass(frozen=True)
class ClosureOrbit:
    states: tuple[ClosureState, ...]
    accepted_moves: tuple[tuple[str, str, int, int], ...]
    selected: ClosureState


def dot(left: Iterable[int | Fraction], right: Iterable[int | Fraction]) -> Fraction:
    return sum((Fraction(a) * Fraction(b) for a, b in zip(left, right)), Fraction(0))


def rational_rank(matrix: Iterable[Iterable[int | Fraction]]) -> int:
    rows = [list(map(Fraction, row)) for row in matrix]
    if not rows:
        return 0
    row_count = len(rows)
    column_count = len(rows[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if rows[row][column]), None
        )
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


def nullspace_basis(matrix: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    rows = [list(map(Fraction, row)) for row in matrix]
    row_count = len(rows)
    column_count = len(rows[0]) if rows else 0
    pivot_row = 0
    pivots: list[int] = []
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if rows[row][column]), None
        )
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
    basis = []
    for free_column in (column for column in range(column_count) if column not in pivots):
        vector = [Fraction(0)] * column_count
        vector[free_column] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -rows[row][free_column]
        denominator = math.lcm(*(value.denominator for value in vector))
        integers = [int(value * denominator) for value in vector]
        divisor = math.gcd(*map(abs, integers))
        integers = [value // divisor for value in integers]
        first = next(value for value in integers if value)
        if first < 0:
            integers = [-value for value in integers]
        basis.append(tuple(integers))
    return tuple(basis)


def enumerate_terminal_cuts(graph: Graph) -> ExactAnalysis:
    """Exhaust every interior assignment for every nontrivial terminal region."""
    if not graph.weights or any(not isinstance(weight, Fraction) for weight in graph.weights):
        raise TypeError("the certification path requires Fraction weights")
    nodes = graph.nodes
    boundary_map = graph.boundary_map
    boundary_nodes = set(boundary_map.values())
    free_nodes = tuple(node for node in nodes if node not in boundary_nodes)
    enumerations: list[RegionEnumeration] = []
    for mask in range(1, (1 << len(graph.boundaries)) - 1):
        region = tuple(
            label
            for index, label in enumerate(graph.boundaries)
            if mask & (1 << index)
        )
        fixed: dict[str, int] = {}
        for label in graph.boundaries:
            side = int(label in region)
            node = boundary_map[label]
            if node in fixed and fixed[node] != side:
                raise AssertionError("distinct terminals were contracted together")
            fixed[node] = side
        candidates = []
        for free_mask in range(1 << len(free_nodes)):
            assignment = dict(fixed)
            assignment.update(
                {
                    node: int(bool(free_mask & (1 << index)))
                    for index, node in enumerate(free_nodes)
                }
            )
            cut_row = tuple(int(assignment[u] != assignment[v]) for u, v in graph.edges)
            capacity = dot(graph.weights, cut_row)
            sides = tuple(assignment[node] for node in nodes)
            candidates.append((capacity, cut_row, sides))
        candidates.sort(key=lambda row: (row[0], row[1], row[2]))
        best_value = candidates[0][0]
        active = tuple(row for row in candidates if row[0] == best_value)
        inactive_values = [row[0] for row in candidates if row[0] > best_value]
        margin = min(inactive_values) - best_value if inactive_values else Fraction(0)
        if len(active) > 1:
            margin = Fraction(0)
        enumerations.append(
            RegionEnumeration(
                region,
                best_value,
                margin,
                tuple(sorted(set(row[1] for row in active))),
                tuple(row[2] for row in active),
                tuple(candidates),
            )
        )
    incidence = tuple(region.active_rows[0] for region in enumerations)
    return ExactAnalysis(
        tuple(enumerations),
        incidence,
        tuple(region.value for region in enumerations),
        tuple(region.margin for region in enumerations),
        tuple(region.active_sides[0] for region in enumerations),
        rational_rank(incidence),
    )


def same_fingerprint_unique(
    before: ExactAnalysis, candidate: Graph
) -> ExactAnalysis | None:
    after = enumerate_terminal_cuts(candidate)
    if after.unique and tuple(region.region for region in after.regions) == tuple(
        region.region for region in before.regions
    ) and after.values == before.values:
        return after
    return None


def four_move_closure_trace_exact(
    graph: Graph,
) -> tuple[
    Graph,
    ExactAnalysis,
    tuple[dict[str, Any], ...],
    tuple[tuple[Graph, ExactAnalysis, tuple[str, str] | None], ...],
]:
    current = graph
    analysis = enumerate_terminal_cuts(current)
    if not analysis.unique:
        raise ValueError(f"nonunique active cuts in {graph.name}")
    moves: list[dict[str, Any]] = []
    trace: list[tuple[Graph, ExactAnalysis, tuple[str, str] | None]] = [
        (current, analysis, None)
    ]
    while True:
        degrees = v2.graph_degrees(current)
        boundary_nodes = set(current.boundary_map.values())
        applied = False
        for node in current.nodes:
            if node not in boundary_nodes and degrees[node] == 2:
                candidate = v2.transform_series(current, node)
                checked = same_fingerprint_unique(analysis, candidate)
                if checked is not None:
                    moves.append({"move": "series_bivalent", "object": node})
                    current, analysis, applied = candidate, checked, True
                    trace.append((current, analysis, ("series_bivalent", node)))
                    break
        if applied:
            continue
        for module, gateways in v2.module_candidates(current):
            capacity, unique = v2.module_capacity(current, module, gateways)
            if not unique:
                continue
            candidate = v2.transform_module(current, module, gateways, capacity)
            checked = same_fingerprint_unique(analysis, candidate)
            if checked is not None and len(candidate.edges) < len(current.edges):
                moves.append(
                    {"move": "exact_two_terminal_module", "object": "+".join(sorted(module))}
                )
                current, analysis, applied = candidate, checked, True
                trace.append(
                    (
                        current,
                        analysis,
                        ("exact_two_terminal_module", "+".join(sorted(module))),
                    )
                )
                break
        if applied:
            continue
        zero_columns = [
            index
            for index in range(len(current.edges))
            if not any(row[index] for row in analysis.incidence)
        ]
        terminal_zero = next(
            (
                index
                for index in zero_columns
                if set(current.edges[index]) & boundary_nodes
            ),
            None,
        )
        if terminal_zero is not None:
            u, v = current.edges[terminal_zero]
            candidate = v2.transform_contract(current, u, v, "_saturated")
            checked = same_fingerprint_unique(analysis, candidate)
            if checked is not None:
                moves.append(
                    {
                        "move": "saturated_terminal_zero_column_contraction",
                        "object": f"{u}-{v}",
                    }
                )
                current, analysis = candidate, checked
                trace.append(
                    (
                        current,
                        analysis,
                        ("saturated_terminal_zero_column_contraction", f"{u}-{v}"),
                    )
                )
                continue
        node_signatures = {
            node: tuple(row[index] for row in analysis.sides)
            for index, node in enumerate(current.nodes)
        }
        pairs = [
            (u, v)
            for u, v in itertools.combinations(current.nodes, 2)
            if node_signatures[u] == node_signatures[v]
            and u not in boundary_nodes
            and v not in boundary_nodes
        ]
        for u, v in pairs:
            candidate = v2.transform_contract(current, u, v, "_inseparable")
            checked = same_fingerprint_unique(analysis, candidate)
            if checked is not None:
                moves.append(
                    {
                        "move": "inseparable_vertex_contraction_parallel_sum",
                        "object": f"{u}+{v}",
                    }
                )
                current, analysis, applied = candidate, checked, True
                trace.append(
                    (
                        current,
                        analysis,
                        ("inseparable_vertex_contraction_parallel_sum", f"{u}+{v}"),
                    )
                )
                break
        if applied:
            continue
        if zero_columns:
            index = zero_columns[0]
            u, v = current.edges[index]
            candidate = v2.transform_contract(current, u, v, "_zero")
            checked = same_fingerprint_unique(analysis, candidate)
            if checked is not None:
                moves.append({"move": "zero_column_contraction", "object": f"{u}-{v}"})
                current, analysis = candidate, checked
                trace.append(
                    (current, analysis, ("zero_column_contraction", f"{u}-{v}"))
                )
                continue
        break
    return current, analysis, tuple(moves), tuple(trace)


def four_move_closure_exact(
    graph: Graph,
) -> tuple[Graph, ExactAnalysis, tuple[dict[str, Any], ...]]:
    current, analysis, moves, _trace = four_move_closure_trace_exact(graph)
    return current, analysis, moves


def graph_key(graph: Graph) -> tuple[Any, ...]:
    return graph.boundary_nodes, graph.weighted_edges


def depth_three_closure_orbit_exact(graph: Graph) -> ClosureOrbit:
    """Expose every state visited by the declared depth-three closure.

    The maintained closure branches over every exact accepted Delta-Y/Y-Delta
    proposal for three replacement rounds and applies the four earlier moves in
    their preregistered deterministic order after each replacement.  The orbit
    includes replacement candidates and every intermediate folded state.
    """
    initial_graph, initial_analysis, initial_moves, initial_trace = (
        four_move_closure_trace_exact(graph)
    )
    initial_path = tuple((move["move"], move["object"]) for move in initial_moves)
    states: list[ClosureState] = []
    path: tuple[tuple[str, str], ...] = ()
    for trace_graph, trace_analysis, move in initial_trace:
        if move is not None:
            path += (move,)
        states.append(ClosureState(trace_graph, trace_analysis, path, 0))
    queue = [ClosureState(initial_graph, initial_analysis, initial_path, 0)]
    objective_states = list(queue)
    seen_folded = {graph_key(initial_graph)}
    accepted_moves: list[tuple[str, str, int, int]] = [
        (move["move"], move["object"], 0, index)
        for index, move in enumerate(initial_moves)
    ]
    cursor = 0
    while cursor < len(queue):
        current_state = queue[cursor]
        cursor += 1
        current = current_state.graph
        analysis = current_state.analysis
        path = current_state.path
        depth = current_state.replacement_depth
        if depth == 3:
            continue
        for move_name, object_name, candidate in v3.fifth_candidates(current):
            checked = same_fingerprint_unique(analysis, candidate)
            if checked is None:
                continue
            replacement_path = path + ((move_name, object_name),)
            accepted_moves.append((move_name, object_name, depth, len(path)))
            states.append(
                ClosureState(candidate, checked, replacement_path, depth + 1)
            )
            folded_graph, folded_analysis, folded_moves, fold_trace = (
                four_move_closure_trace_exact(candidate)
            )
            folded_path = replacement_path
            for trace_graph, trace_analysis, fold_move in fold_trace[1:]:
                if fold_move is None:
                    continue
                folded_path += (fold_move,)
                accepted_moves.append(
                    (fold_move[0], fold_move[1], depth + 1, len(folded_path) - 1)
                )
                states.append(
                    ClosureState(trace_graph, trace_analysis, folded_path, depth + 1)
                )
            key = graph_key(folded_graph)
            if key in seen_folded:
                continue
            seen_folded.add(key)
            queue.append(
                ClosureState(folded_graph, folded_analysis, folded_path, depth + 1)
            )
            objective_states.append(queue[-1])
    selected = min(
        objective_states,
        key=lambda state: (
            len(state.graph.edges) - state.analysis.rank,
            len(state.graph.edges),
            state.replacement_depth,
            graph_key(state.graph),
        ),
    )
    return ClosureOrbit(tuple(states), tuple(accepted_moves), selected)


def five_move_closure_exact(
    graph: Graph,
) -> tuple[Graph, ExactAnalysis, tuple[dict[str, Any], ...]]:
    orbit = depth_three_closure_orbit_exact(graph)
    return (
        orbit.selected.graph,
        orbit.selected.analysis,
        tuple(
            {"move": move, "object": object_name}
            for move, object_name in orbit.selected.path
        ),
    )


def terminal_fixed_weighted_canonical_key(graph: Graph) -> tuple[Any, ...]:
    """Canonicalize with terminal labels fixed pointwise and interior labels free.

    Exact Fraction weights are part of the key.  Terminal nodes are identified
    by the sorted tuple of boundary labels attached to them.  Only non-terminal
    node labels are permuted.
    """
    labels_by_node: dict[str, list[str]] = {}
    for label, node in graph.boundary_nodes:
        labels_by_node.setdefault(node, []).append(label)
    terminal_tokens = {
        node: "T:" + "&".join(sorted(labels))
        for node, labels in labels_by_node.items()
    }
    interiors = tuple(node for node in graph.nodes if node not in terminal_tokens)
    canonical_names = tuple(f"N{index}" for index in range(len(interiors)))
    encodings = []
    for permutation in itertools.permutations(canonical_names):
        mapping = dict(terminal_tokens)
        mapping.update(zip(interiors, permutation))
        edges = tuple(
            sorted(
                (
                    min(mapping[u], mapping[v]),
                    max(mapping[u], mapping[v]),
                    weight.numerator,
                    weight.denominator,
                )
                for u, v, weight in graph.weighted_edges
            )
        )
        boundary_map = tuple(
            (label, mapping[node]) for label, node in sorted(graph.boundary_nodes)
        )
        encodings.append((tuple(graph.boundaries), boundary_map, edges))
    return min(encodings)


def path_text(path: tuple[tuple[str, str], ...]) -> str:
    return "IDENTITY" if not path else "|".join(
        f"{move}({object_name})" for move, object_name in path
    )


def compare_depth_three_orbits(base: Graph, moved: Graph) -> dict[str, Any]:
    base_orbit = depth_three_closure_orbit_exact(base)
    moved_orbit = depth_three_closure_orbit_exact(moved)

    def canonical_groups(orbit: ClosureOrbit):
        groups: dict[tuple[Any, ...], list[ClosureState]] = {}
        for state in orbit.states:
            key = terminal_fixed_weighted_canonical_key(state.graph)
            groups.setdefault(key, []).append(state)
        return groups

    base_groups = canonical_groups(base_orbit)
    moved_groups = canonical_groups(moved_orbit)
    common = sorted(set(base_groups) & set(moved_groups))
    cross_count = sum(
        len(base_groups[key]) * len(moved_groups[key]) for key in common
    )
    if common:
        key = common[0]
        base_witness = min(base_groups[key], key=lambda state: (len(state.path), state.path))
        moved_witness = min(moved_groups[key], key=lambda state: (len(state.path), state.path))
        verdict = "GAUGE"
        witness_path = (
            f"base:{path_text(base_witness.path)} || "
            f"perturbed:{path_text(moved_witness.path)}"
        )
    else:
        verdict = "depth-three five-move-orbit-disjoint"
        witness_path = ""
    return {
        "base_orbit": base_orbit,
        "moved_orbit": moved_orbit,
        "base_orbit_state_count": len(base_groups),
        "moved_orbit_state_count": len(moved_groups),
        "base_visited_labelled_state_count": len(base_orbit.states),
        "moved_visited_labelled_state_count": len(moved_orbit.states),
        "base_accepted_move_count": len(base_orbit.accepted_moves),
        "moved_accepted_move_count": len(moved_orbit.accepted_moves),
        "cross_orbit_weighted_isomorphism_count": cross_count,
        "verdict": verdict,
        "path_if_gauge": witness_path,
        "canonicalization": "terminal labels fixed pointwise; non-terminal labels free; exact Fraction weights included",
    }


def perturb(graph: Graph, direction: tuple[int, ...], t: Fraction) -> Graph:
    return replace(
        graph,
        name=graph.name + "__perturbed",
        weighted_edges=tuple(
            (u, v, weight + t * coefficient)
            for (u, v, weight), coefficient in zip(graph.weighted_edges, direction)
        ),
    )


def finite_fingerprint_interval(
    graph: Graph, analysis: ExactAnalysis, direction: tuple[int, ...]
) -> ExactInterval:
    if not analysis.unique:
        return ExactInterval(Fraction(0), Fraction(0))
    if any(dot(row, direction) != 0 for row in analysis.incidence):
        raise ValueError("direction is not in the active-cut kernel")
    lower: Fraction | None = None
    upper: Fraction | None = None
    for region in analysis.regions:
        active = region.active_rows[0]
        active_value = dot(graph.weights, active)
        for _value, candidate, _sides in region.candidates:
            difference = tuple(a - b for a, b in zip(candidate, active))
            gap = dot(graph.weights, difference)
            slope = dot(direction, difference)
            if gap < 0:
                raise AssertionError("enumerated active cut was not minimal")
            if slope > 0:
                crossing = -gap / slope
                lower = crossing if lower is None else max(lower, crossing)
            elif slope < 0:
                crossing = -gap / slope
                upper = crossing if upper is None else min(upper, crossing)
        if active_value != region.value:
            raise AssertionError("active value mismatch")
    return ExactInterval(lower, upper)


def positive_capacity_interval(graph: Graph, direction: tuple[int, ...]) -> ExactInterval:
    lower: Fraction | None = None
    upper: Fraction | None = None
    for weight, coefficient in zip(graph.weights, direction):
        if coefficient > 0:
            bound = -weight / coefficient
            lower = bound if lower is None else max(lower, bound)
        elif coefficient < 0:
            bound = -weight / coefficient
            upper = bound if upper is None else min(upper, bound)
    return ExactInterval(lower, upper)


def intersect_intervals(left: ExactInterval, right: ExactInterval) -> ExactInterval:
    lower_values = [value for value in (left.lower, right.lower) if value is not None]
    upper_values = [value for value in (left.upper, right.upper) if value is not None]
    return ExactInterval(max(lower_values) if lower_values else None, min(upper_values) if upper_values else None)


def fingerprint_equal_by_enumeration(
    base: ExactAnalysis, moved_graph: Graph
) -> tuple[bool, ExactAnalysis]:
    moved = enumerate_terminal_cuts(moved_graph)
    return moved.values == base.values, moved


def weighted_automorphism_status(
    base: Graph, moved: Graph
) -> tuple[int, int, bool, bool]:
    topology = nx.Graph()
    boundary_nodes = set(base.boundary_map.values())
    topology.add_nodes_from(base.nodes)
    topology.add_edges_from(base.edges)
    matcher = nx.algorithms.isomorphism.GraphMatcher(topology, topology)
    moved_weights = {v2.edge(u, v): weight for u, v, weight in moved.weighted_edges}
    count = 0
    terminal_set_preserving_count = 0
    any_maps_weighting = False
    terminal_set_preserving_maps_weighting = False
    for mapping in matcher.isomorphisms_iter():
        count += 1
        preserves_terminal_set = {mapping[node] for node in boundary_nodes} == boundary_nodes
        terminal_set_preserving_count += int(preserves_terminal_set)
        maps_weighting = all(
            moved_weights[v2.edge(mapping[u], mapping[v])] == weight
            for u, v, weight in base.weighted_edges
        )
        any_maps_weighting = any_maps_weighting or maps_weighting
        terminal_set_preserving_maps_weighting = (
            terminal_set_preserving_maps_weighting
            or (preserves_terminal_set and maps_weighting)
        )
    return (
        count,
        terminal_set_preserving_count,
        any_maps_weighting,
        terminal_set_preserving_maps_weighting,
    )


def circular_planarity(graph: Graph) -> tuple[bool, str]:
    """Use the exact cofacial augmentation criterion: add one terminal apex."""
    augmented = nx.Graph()
    augmented.add_nodes_from(graph.nodes)
    augmented.add_edges_from(graph.edges)
    apex = "<terminal_outer_face_apex>"
    augmented.add_node(apex)
    augmented.add_edges_from((apex, node) for node in set(graph.boundary_map.values()))
    planar, _embedding = nx.check_planarity(augmented, counterexample=False)
    return bool(planar), "terminal-apex cofacial planarity test (NetworkX Left-Right Planarity Test)"


def format_fraction(value: Fraction | None) -> str:
    if value is None:
        return "-inf_or_+inf"
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def interval_text(interval: ExactInterval) -> str:
    lower = "-inf" if interval.lower is None else format_fraction(interval.lower)
    upper = "+inf" if interval.upper is None else format_fraction(interval.upper)
    return f"[{lower},{upper}]"


def direction_text(graph: Graph, direction: tuple[int, ...]) -> str:
    return " ".join(
        f"{coefficient:+d}*{u}-{v}"
        for (u, v), coefficient in zip(graph.edges, direction)
        if coefficient
    )


def fingerprint_digest(analysis: ExactAnalysis) -> str:
    payload = "\n".join(
        f"{'|'.join(region.region)}:{format_fraction(region.value)}"
        for region in analysis.regions
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
