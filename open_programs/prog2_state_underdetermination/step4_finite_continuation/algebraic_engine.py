#!/usr/bin/env python3
"""Exact number-field cuts and generated gauge closure for PROG2 Step 4."""
from __future__ import annotations

import hashlib
import itertools
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from typing import Any, Iterable

import sympy as sp

def _q(value: Fraction | int) -> sp.Rational:
    value = Fraction(value)
    return sp.Rational(value.numerator, value.denominator)

def _f(value: sp.Rational) -> Fraction:
    return Fraction(int(value.p), int(value.q))

@dataclass(frozen=True)
class RootCertificate:
    polynomial_coefficients: tuple[Fraction, ...]
    minimal_polynomial_coefficients: tuple[Fraction, ...]  # descending
    lower: Fraction
    upper: Fraction
    root_index: int

    @property
    def width(self) -> Fraction:
        return self.upper - self.lower

    def interval(self, digits: int = 75) -> tuple[Fraction, Fraction]:
        return _refined_root_interval(
            self.minimal_polynomial_coefficients, self.lower, self.upper, digits
        )

    def decimal(self, digits: int = 100) -> str:
        lo, hi = self.interval(digits + 5)
        return str(sp.N((_q(lo) + _q(hi)) / 2, digits))

@lru_cache(maxsize=None)
def _refined_root_interval(
    coefficients: tuple[Fraction, ...], original_lower: Fraction,
    original_upper: Fraction, digits: int,
) -> tuple[Fraction, Fraction]:
    x = sp.symbols("x")
    poly = sp.Poly.from_list([_q(value) for value in coefficients], x, domain=sp.QQ)
    overlaps = []
    for (lo, hi), multiplicity in poly.intervals(eps=sp.Rational(1, 10**digits)):
        if multiplicity == 1 and not (hi < _q(original_lower) or lo > _q(original_upper)):
            overlaps.append((max(lo, _q(original_lower)), min(hi, _q(original_upper))))
    if len(overlaps) != 1:
        raise ArithmeticError("could not uniquely refine selected algebraic root")
    return _f(overlaps[0][0]), _f(overlaps[0][1])

@dataclass(frozen=True)
class NumberField:
    """QQ(alpha), with a monic irreducible modulus in ascending order."""
    modulus: tuple[Fraction, ...]
    root: RootCertificate

    @property
    def degree(self) -> int:
        return len(self.modulus) - 1

    def element(self, value: Fraction | int = 0) -> "FieldElement":
        return FieldElement((Fraction(value),) + (Fraction(0),) * (self.degree - 1), self)

    @property
    def alpha(self) -> "FieldElement":
        if self.degree < 2:
            raise AssertionError("unexpected rational continuation root")
        return FieldElement((Fraction(0), Fraction(1)) + (Fraction(0),) * (self.degree - 2), self)

    @classmethod
    def from_root(cls, root: RootCertificate) -> "NumberField":
        x = sp.symbols("x")
        poly = sp.Poly.from_list([_q(value) for value in root.minimal_polynomial_coefficients], x, domain=sp.QQ).monic()
        descending = [_f(value) for value in poly.all_coeffs()]
        return cls(tuple(reversed(descending)), root)

def _trim(values: list[Fraction]) -> list[Fraction]:
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return values

@lru_cache(maxsize=None)
def _inverse_coefficients(
    coefficients: tuple[Fraction, ...], modulus: tuple[Fraction, ...]
) -> tuple[Fraction, ...]:
    x = sp.symbols("x")
    element = sp.Poly(sum(_q(value) * x**i for i, value in enumerate(coefficients)), x, domain=sp.QQ)
    mod = sp.Poly(sum(_q(value) * x**i for i, value in enumerate(modulus)), x, domain=sp.QQ)
    inverse = sp.invert(element, mod)
    degree = len(modulus) - 1
    return tuple(_f(inverse.nth(i)) for i in range(degree))

@dataclass(frozen=True)
class FieldElement:
    coefficients: tuple[Fraction, ...]  # ascending, exactly field.degree entries
    field: NumberField

    def __post_init__(self) -> None:
        if len(self.coefficients) != self.field.degree:
            raise ValueError("field coefficient length mismatch")

    def _coerce(self, other: Any) -> "FieldElement":
        if isinstance(other, FieldElement):
            if other.field != self.field:
                raise TypeError("different number fields")
            return other
        return self.field.element(Fraction(other))

    def __add__(self, other: Any) -> "FieldElement":
        other = self._coerce(other)
        return FieldElement(tuple(a + b for a, b in zip(self.coefficients, other.coefficients)), self.field)
    __radd__ = __add__

    def __neg__(self) -> "FieldElement":
        return FieldElement(tuple(-value for value in self.coefficients), self.field)

    def __sub__(self, other: Any) -> "FieldElement":
        return self + (-self._coerce(other))

    def __rsub__(self, other: Any) -> "FieldElement":
        return self._coerce(other) - self

    def __mul__(self, other: Any) -> "FieldElement":
        other = self._coerce(other)
        degree = self.field.degree
        product = [Fraction(0)] * (2 * degree - 1)
        for i, left in enumerate(self.coefficients):
            for j, right in enumerate(other.coefficients):
                product[i + j] += left * right
        modulus = self.field.modulus
        for power in range(len(product) - 1, degree - 1, -1):
            factor = product[power]
            if not factor:
                continue
            for index in range(degree):
                product[power - degree + index] -= factor * modulus[index]
        return FieldElement(tuple(product[:degree]), self.field)
    __rmul__ = __mul__

    def inverse(self) -> "FieldElement":
        if self.is_zero:
            raise ZeroDivisionError
        return FieldElement(_inverse_coefficients(self.coefficients, self.field.modulus), self.field)

    def __truediv__(self, other: Any) -> "FieldElement":
        return self * self._coerce(other).inverse()

    @property
    def is_zero(self) -> bool:
        return not any(self.coefficients)

    def interval(self, digits: int = 75) -> tuple[Fraction, Fraction]:
        alpha_lo, alpha_hi = self.field.root.interval(digits)
        lo = hi = Fraction(0)
        for coefficient in reversed(self.coefficients):
            products = (lo * alpha_lo, lo * alpha_hi, hi * alpha_lo, hi * alpha_hi)
            lo, hi = min(products) + coefficient, max(products) + coefficient
        return lo, hi

    def sign(self) -> int:
        if self.is_zero:
            return 0
        for digits in (75, 100, 150, 225, 325, 500):
            lo, hi = self.interval(digits)
            if lo > 0:
                return 1
            if hi < 0:
                return -1
        raise ArithmeticError("isolating-interval refinement did not resolve algebraic sign")

    def key(self) -> tuple[tuple[int, int], ...]:
        return tuple((value.numerator, value.denominator) for value in self.coefficients)

    def expression(self, symbol: str = "alpha") -> str:
        terms = []
        for power, coefficient in enumerate(self.coefficients):
            if not coefficient:
                continue
            basis = "" if power == 0 else (symbol if power == 1 else f"{symbol}^{power}")
            terms.append(str(coefficient) if not basis else f"({coefficient})*{basis}")
        return "+".join(terms).replace("+-", "-") if terms else "0"

    def decimal(self, digits: int = 100) -> sp.Float:
        lo, hi = self.interval(digits + 5)
        return sp.N((_q(lo) + _q(hi)) / 2, digits)

@dataclass(frozen=True)
class NFGraph:
    name: str
    family: str
    boundaries: tuple[str, ...]
    boundary_nodes: tuple[tuple[str, str], ...]
    weighted_edges: tuple[tuple[str, str, FieldElement], ...]

    @property
    def boundary_map(self) -> dict[str, str]: return dict(self.boundary_nodes)
    @property
    def edges(self) -> tuple[tuple[str, str], ...]: return tuple((u, v) for u, v, _ in self.weighted_edges)
    @property
    def weights(self) -> tuple[FieldElement, ...]: return tuple(w for _u, _v, w in self.weighted_edges)
    @property
    def nodes(self) -> tuple[str, ...]:
        values = set(self.boundary_map.values())
        for u, v in self.edges: values.update((u, v))
        return tuple(sorted(values))

def edge(u: str, v: str) -> tuple[str, str]:
    if u == v: raise ValueError("self edge")
    return tuple(sorted((u, v)))

def make_graph(name: str, family: str, boundaries: Iterable[str],
               rows: Iterable[tuple[str, str, FieldElement]], boundary_map: dict[str, str]) -> NFGraph:
    combined: dict[tuple[str, str], FieldElement] = {}
    for u, v, weight in rows:
        pair = edge(u, v)
        combined[pair] = combined.get(pair, weight.field.element()) + weight
    kept = {pair: value for pair, value in combined.items() if value.sign() > 0}
    return NFGraph(name, family, tuple(boundaries), tuple(sorted(boundary_map.items())),
                   tuple((u, v, kept[(u, v)]) for u, v in sorted(kept)))

def lift_graph(graph: Any, capacities: tuple[FieldElement, ...]) -> NFGraph:
    return NFGraph(graph.name, graph.family, tuple(graph.boundaries), tuple(graph.boundary_nodes),
                   tuple((u, v, weight) for (u, v), weight in zip(graph.edges, capacities)))

@dataclass(frozen=True)
class NFRegion:
    region: tuple[str, ...]
    value: FieldElement
    margin_lower: Fraction
    active_row: tuple[int, ...]
    active_sides: tuple[int, ...]
    candidate_count: int

@dataclass(frozen=True)
class NFAnalysis:
    regions: tuple[NFRegion, ...]
    incidence: tuple[tuple[int, ...], ...]
    sides: tuple[tuple[int, ...], ...]
    all_candidate_count: int
    @property
    def minimum_margin_lower(self) -> Fraction: return min(row.margin_lower for row in self.regions)

def enumerate_cuts(graph: NFGraph) -> NFAnalysis:
    nodes, boundary_map = graph.nodes, graph.boundary_map
    free_nodes = tuple(node for node in nodes if node not in set(boundary_map.values()))
    rows, incidence, sides, total = [], [], [], 0
    zero = graph.weights[0].field.element()
    for mask in range(1, (1 << len(graph.boundaries)) - 1):
        region = tuple(label for i, label in enumerate(graph.boundaries) if mask & (1 << i))
        fixed: dict[str, int] = {}
        invalid = False
        for label in graph.boundaries:
            side, node = int(label in region), boundary_map[label]
            if node in fixed and fixed[node] != side:
                invalid = True; break
            fixed[node] = side
        if invalid:
            raise ValueError("transformation identified separable terminals")
        candidates = []
        for free_mask in range(1 << len(free_nodes)):
            assignment = dict(fixed)
            assignment.update({node: int(bool(free_mask & (1 << i))) for i, node in enumerate(free_nodes)})
            cut_row = tuple(int(assignment[u] != assignment[v]) for u, v in graph.edges)
            value = zero
            for weight, used in zip(graph.weights, cut_row):
                if used: value += weight
            candidates.append((value, cut_row, tuple(assignment[node] for node in nodes)))
        total += len(candidates)
        best = candidates[0]
        for candidate in candidates[1:]:
            sign = (candidate[0] - best[0]).sign()
            if sign < 0 or (sign == 0 and (candidate[1], candidate[2]) < (best[1], best[2])):
                best = candidate
        differences = [candidate[0] - best[0] for candidate in candidates if candidate != best]
        if any(value.sign() == 0 for value in differences):
            raise ValueError("nonunique terminal minimizer")
        margin = min(value.interval()[0] for value in differences)
        if margin <= 0: raise ArithmeticError("nonpositive rigorous margin")
        rows.append(NFRegion(region, best[0], margin, best[1], best[2], len(candidates)))
        incidence.append(best[1]); sides.append(best[2])
    return NFAnalysis(tuple(rows), tuple(incidence), tuple(sides), total)

def same_fingerprint(left: NFAnalysis, right: NFAnalysis) -> bool:
    return (tuple(row.region for row in left.regions) == tuple(row.region for row in right.regions)
            and tuple(row.value for row in left.regions) == tuple(row.value for row in right.regions))

def graph_degrees(graph: NFGraph) -> Counter[str]:
    result: Counter[str] = Counter()
    for u, v in graph.edges: result[u] += 1; result[v] += 1
    return result

def module_candidates(graph: NFGraph):
    boundary_nodes = set(graph.boundary_map.values())
    interior = tuple(node for node in graph.nodes if node not in boundary_nodes)
    result = []
    for size in range(len(interior), 0, -1):
        for values in itertools.combinations(interior, size):
            module, gateways, internal = frozenset(values), set(), False
            for u, v in graph.edges:
                if u in module and v in module: internal = True
                elif u in module: gateways.add(v)
                elif v in module: gateways.add(u)
            if len(gateways) == 2 and internal: result.append((module, tuple(sorted(gateways))))
    return result

def transform_contract(graph: NFGraph, u: str, v: str, suffix: str) -> NFGraph:
    merged, rows = f"<{u}+{v}>", []
    for left, right, weight in graph.weighted_edges:
        left = merged if left in {u, v} else left; right = merged if right in {u, v} else right
        if left != right: rows.append((left, right, weight))
    mapping = {label: merged if node in {u, v} else node for label, node in graph.boundary_nodes}
    return make_graph(graph.name + suffix, graph.family, graph.boundaries, rows, mapping)

def transform_series(graph: NFGraph, node: str) -> NFGraph:
    incident = [row for row in graph.weighted_edges if node in row[:2]]
    neighbors = [v if u == node else u for u, v, _ in incident]
    effective = incident[0][2] if (incident[0][2] - incident[1][2]).sign() < 0 else incident[1][2]
    rows = [row for row in graph.weighted_edges if node not in row[:2]] + [(neighbors[0], neighbors[1], effective)]
    return make_graph(graph.name + f"_series_{node}", graph.family, graph.boundaries, rows, graph.boundary_map)

def module_capacity(graph: NFGraph, module: frozenset[str], gateways: tuple[str, str]):
    values = []
    zero = graph.weights[0].field.element()
    internal = tuple(sorted(module))
    for mask in range(1 << len(internal)):
        assignment = {gateways[0]: 0, gateways[1]: 1}
        assignment.update({node: int(bool(mask & (1 << i))) for i, node in enumerate(internal)})
        capacity = zero
        for u, v, weight in graph.weighted_edges:
            if u in module or v in module:
                capacity += weight * int(assignment[u] != assignment[v])
        values.append(capacity)
    best = values[0]
    for value in values[1:]:
        if (value - best).sign() < 0: best = value
    return best, sum(value == best for value in values) == 1

def transform_module(graph: NFGraph, module: frozenset[str], gateways: tuple[str, str], capacity: FieldElement):
    rows = [row for row in graph.weighted_edges if row[0] not in module and row[1] not in module]
    rows.append((gateways[0], gateways[1], capacity))
    return make_graph(graph.name + "_two_terminal", graph.family, graph.boundaries, rows, graph.boundary_map)

def triangle_candidates(graph: NFGraph):
    edges = set(graph.edges)
    return [nodes for nodes in itertools.combinations(graph.nodes, 3)
            if all(edge(u, v) in edges for u, v in itertools.combinations(nodes, 2))]

def delta_to_y(graph: NFGraph, nodes: tuple[str, str, str]) -> NFGraph:
    u0, u1, u2 = nodes; weights = {edge(u, v): w for u, v, w in graph.weighted_edges}
    w01, w02, w12 = weights[edge(u0, u1)], weights[edge(u0, u2)], weights[edge(u1, u2)]
    center = "<Y:" + "+".join(nodes) + ">"; removed = {edge(u0, u1), edge(u0, u2), edge(u1, u2)}
    rows = [row for row in graph.weighted_edges if edge(row[0], row[1]) not in removed]
    rows += [(u0, center, w01 + w02), (u1, center, w01 + w12), (u2, center, w02 + w12)]
    return make_graph(graph.name + "_delta_y", graph.family, graph.boundaries, rows, graph.boundary_map)

def star_candidates(graph: NFGraph):
    degrees, boundary_nodes, result = graph_degrees(graph), set(graph.boundary_map.values()), []
    for center in graph.nodes:
        if center in boundary_nodes or degrees[center] != 3: continue
        incident = sorted((v if u == center else u, w) for u, v, w in graph.weighted_edges if center in {u, v})
        (u0, a0), (u1, a1), (u2, a2) = incident
        triangle = ((a0+a1-a2)/2, (a0+a2-a1)/2, (a1+a2-a0)/2)
        if all(value.sign() > 0 for value in triangle): result.append((center, (u0,u1,u2), triangle))
    return result

def y_to_delta(graph: NFGraph, candidate: Any) -> NFGraph:
    center, (u0,u1,u2), (w01,w02,w12) = candidate
    rows = [row for row in graph.weighted_edges if center not in row[:2]]
    rows += [(u0,u1,w01),(u0,u2,w02),(u1,u2,w12)]
    return make_graph(graph.name + "_y_delta", graph.family, graph.boundaries, rows, graph.boundary_map)

def reciprocal_edge(graph: NFGraph, index: int) -> NFGraph:
    rows = [(u, v, weight.inverse() if i == index else weight)
            for i, (u, v, weight) in enumerate(graph.weighted_edges)]
    return make_graph(graph.name + f"_reciprocal_{index}", graph.family, graph.boundaries, rows, graph.boundary_map)

def canonical_key(graph: NFGraph) -> tuple[Any, ...]:
    terminal_by_node: dict[str, tuple[str, ...]] = defaultdict(tuple)
    for label, node in graph.boundary_nodes:
        terminal_by_node[node] = tuple(sorted(terminal_by_node[node] + (label,)))
    interior = tuple(node for node in graph.nodes if node not in terminal_by_node)
    best = None
    for permutation in itertools.permutations(range(len(interior))):
        names = {node: f"I{permutation[i]}" for i, node in enumerate(interior)}
        names.update({node: "T:" + "+".join(labels) for node, labels in terminal_by_node.items()})
        rows = tuple(sorted((min(names[u],names[v]), max(names[u],names[v]), weight.key())
                            for u,v,weight in graph.weighted_edges))
        if best is None or rows < best: best = rows
    return tuple(graph.boundaries), best

def five_move_proposals(graph: NFGraph, analysis: NFAnalysis):
    boundary_nodes, degrees = set(graph.boundary_map.values()), graph_degrees(graph)
    for node in graph.nodes:
        if node not in boundary_nodes and degrees[node] == 2:
            yield "series", f"series_bivalent:{node}", transform_series(graph, node)
    for module, gateways in module_candidates(graph):
        capacity, unique = module_capacity(graph, module, gateways)
        if unique:
            candidate = transform_module(graph, module, gateways, capacity)
            if len(candidate.edges) < len(graph.edges):
                yield "two_terminal_module", "module:"+"+".join(sorted(module)), candidate
    zero = [i for i in range(len(graph.edges)) if not any(row[i] for row in analysis.incidence)]
    for index in zero:
        u,v = graph.edges[index]
        yield "saturated_or_zero_column", f"zero:{u}-{v}", transform_contract(graph,u,v,"_zero")
    signatures = {node: tuple(row[i] for row in analysis.sides) for i,node in enumerate(graph.nodes)}
    for u,v in itertools.combinations(graph.nodes,2):
        if u not in boundary_nodes and v not in boundary_nodes and signatures[u] == signatures[v]:
            yield "inseparable_contraction", f"inseparable:{u}+{v}", transform_contract(graph,u,v,"_inseparable")
    for nodes in triangle_candidates(graph):
        yield "delta_y_y_delta", "delta_y:"+"+".join(nodes), delta_to_y(graph,nodes)
    for candidate in star_candidates(graph):
        yield "delta_y_y_delta", "y_delta:"+candidate[0], y_to_delta(graph,candidate)

MOVE_CLASSES = ("series", "two_terminal_module", "saturated_or_zero_column",
                "inseparable_contraction", "delta_y_y_delta", "single_edge_reciprocal")

@dataclass(frozen=True)
class CombinedState:
    graph: NFGraph
    path: tuple[str, ...]

@dataclass(frozen=True)
class CombinedOrbit:
    states: dict[tuple[Any, ...], CombinedState]
    saturated: bool
    budget_reason: str
    max_depth: int
    accepted_census: dict[str, int]
    novel_census: dict[str, int]
    processed_state_count: int
    fingerprint_recheck_count: int

def saturate_combined(endpoint: NFGraph, state_cap: int, wall_seconds: float) -> CombinedOrbit:
    started = time.monotonic(); initial_key = canonical_key(endpoint)
    states = {initial_key: CombinedState(endpoint, ())}; queue = [initial_key]; cursor = 0
    accepted = {name: 0 for name in MOVE_CLASSES}; novel = dict(accepted); rechecks = 0
    saturated, reason = True, ""
    while cursor < len(queue):
        if time.monotonic() - started >= wall_seconds:
            saturated, reason = False, f"wall_seconds={wall_seconds:g}"; break
        key = queue[cursor]; cursor += 1; current = states[key]
        analysis = enumerate_cuts(current.graph)
        for move_class, label, candidate in five_move_proposals(current.graph, analysis):
            try: checked = enumerate_cuts(candidate)
            except (ValueError, ArithmeticError): continue
            rechecks += 1
            if not same_fingerprint(analysis, checked): continue
            accepted[move_class] += 1
            candidate_key = canonical_key(candidate)
            if candidate_key in states: continue
            if len(states) >= state_cap:
                saturated, reason = False, f"state_cap={state_cap}"; break
            states[candidate_key] = CombinedState(candidate, current.path + (label,)); queue.append(candidate_key)
            novel[move_class] += 1
        if not saturated: break
        for index in range(len(current.graph.edges)):
            candidate = reciprocal_edge(current.graph, index); accepted["single_edge_reciprocal"] += 1
            candidate_key = canonical_key(candidate)
            if candidate_key in states: continue
            if len(states) >= state_cap:
                saturated, reason = False, f"state_cap={state_cap}"; break
            states[candidate_key] = CombinedState(candidate, current.path + (f"reciprocal_edge:{index}",)); queue.append(candidate_key)
            novel["single_edge_reciprocal"] += 1
        if not saturated: break
    return CombinedOrbit(states, saturated, reason, max(len(state.path) for state in states.values()),
                         accepted, novel, cursor, rechecks)

def orbit_intersection(left: CombinedOrbit, right: CombinedOrbit):
    common = sorted(set(left.states) & set(right.states))
    if not common: return {"count": 0, "left_path": "", "right_path": ""}
    key = common[0]
    return {"count": len(common), "left_path": " -> ".join(left.states[key].path),
            "right_path": " -> ".join(right.states[key].path)}

def explored_capacity_signature(orbit: CombinedOrbit):
    values = {tuple(sorted(weight.key() for weight in state.graph.weights))
              for state in orbit.states.values()}
    return values, hashlib.sha256(repr(sorted(values)).encode()).hexdigest()

def reciprocal_first_canary(endpoint: NFGraph, edge_indices: Iterable[int]):
    rows = []
    for index in edge_indices:
        graph = reciprocal_edge(endpoint, index); analysis = enumerate_cuts(graph)
        proposals, accepted = [], []
        for move_class, label, candidate in five_move_proposals(graph, analysis):
            if move_class not in {"saturated_or_zero_column", "inseparable_contraction"}: continue
            proposals.append(f"{move_class}:{label}")
            try: checked = enumerate_cuts(candidate)
            except (ValueError, ArithmeticError): continue
            if same_fingerprint(analysis, checked): accepted.append(f"{move_class}:{label}")
        rows.append({"edge_index": index, "proposal_count": len(proposals),
                     "accepted_count": len(accepted), "proposals": "|".join(proposals),
                     "accepted": "|".join(accepted), "passes": bool(proposals)})
    return rows

def exact_root_certificate(poly: sp.Poly, capacities_at: Any, width_digits: int = 75) -> RootCertificate:
    candidates = []
    for (lo,hi), multiplicity in poly.intervals(eps=sp.Rational(1,10**width_digits)):
        if multiplicity != 1: continue
        midpoint = (lo+hi)/2
        if all(sp.N(expr.subs(poly.gens[0],midpoint),80)>0 for expr in capacities_at):
            candidates.append((abs(sp.N(midpoint,80)),lo,hi))
    if not candidates: raise ArithmeticError("no positive simple algebraic root")
    _distance,lo,hi = min(candidates,key=lambda row:row[0])
    minimal,root_index = None,-1
    for factor,_multiplicity in sp.factor_list(poly.as_expr())[1]:
        factor_poly = sp.Poly(factor,poly.gens[0],domain=sp.QQ)
        for index,((f_lo,f_hi),_mult) in enumerate(factor_poly.intervals(eps=sp.Rational(1,10**width_digits))):
            if not (f_hi<lo or f_lo>hi):
                minimal,root_index = factor_poly,index; lo,hi=max(lo,f_lo),min(hi,f_hi); break
        if minimal is not None: break
    if minimal is None: raise ArithmeticError("no irreducible root factor")
    return RootCertificate(tuple(_f(x) for x in poly.all_coeffs()),
                           tuple(_f(x) for x in minimal.all_coeffs()),_f(lo),_f(hi),root_index)
