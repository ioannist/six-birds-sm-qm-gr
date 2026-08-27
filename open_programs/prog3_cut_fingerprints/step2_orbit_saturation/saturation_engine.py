#!/usr/bin/env python3
"""Exact breadth-first saturation under the five declared move classes."""

from __future__ import annotations

import hashlib
import itertools
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEP1_DIR = HERE.parent / "step1_finite_range"
STEP1_PINS = {
    STEP1_DIR / "exact_engine.py": "8cdb009724dd2d59e1100ecb048d95aa441fa485218e8cb5c34d5ad3b2f4e6c8",
    STEP1_DIR / "step1_core.py": "d2bdf6498b7abf851f81e04cf8f3988a960a2b1391e7763c869961c52583cfd2",
    STEP1_DIR / "certified_fibers_step1.csv": "09a5abd737f95cb0429b97a4810fd3294bc675a6d6276e72a799c8b23e2a9298",
    STEP1_DIR / "kernel_intervals_step1.csv": "734c6142ad4e1c474b989080ba8f21b0c10094c0db04f70f9918a3a606cfa760",
    STEP1_DIR / "exact_weights_step1.csv": "6e7e6e321c6e6370c9ca63405809482f9b7502ceaa137a3ab315e124b36b78fc",
    STEP1_DIR / "statement.md": "3f4e04d884cdf7638c85bb3cbdb1876b910e19bbd6c9e87c0aa98b86948a9fba",
}

STATE_CAP = 100_000
ENDPOINT_WALL_SECONDS = 20.0

MOVE_CLASSES = (
    "series",
    "two_terminal_module",
    "saturated_or_zero_column",
    "inseparable_contraction",
    "delta_y_y_delta",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> list[dict[str, Any]]:
    rows = []
    for path, expected in STEP1_PINS.items():
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
if str(STEP1_DIR) not in sys.path:
    sys.path.insert(0, str(STEP1_DIR))

from exact_engine import (  # noqa: E402
    ExactAnalysis,
    enumerate_terminal_cuts,
    path_text,
    same_fingerprint_unique,
    terminal_fixed_weighted_canonical_key,
    v2,
    v3,
)


@dataclass(frozen=True)
class SaturationState:
    graph: Any
    analysis: ExactAnalysis
    path: tuple[tuple[str, str], ...]
    replacement_depth: int


@dataclass(frozen=True)
class SaturationResult:
    states_by_key: dict[tuple[Any, ...], SaturationState]
    saturated: bool
    budget_reason: str
    max_replacement_depth: int
    accepted_transition_census: dict[str, int]
    novel_state_census: dict[str, int]
    fingerprint_full_recheck_count: int
    all_admitted_fingerprints_equal: bool


def move_candidates(
    graph: Any, analysis: ExactAnalysis
) -> Iterable[tuple[str, str, str, Any]]:
    """Yield every applicable labelled proposal in deterministic class order."""
    degrees = v2.graph_degrees(graph)
    boundary_nodes = set(graph.boundary_map.values())

    for node in graph.nodes:
        if node not in boundary_nodes and degrees[node] == 2:
            yield "series", "series_bivalent", node, v2.transform_series(graph, node)

    for module, gateways in v2.module_candidates(graph):
        capacity, unique = v2.module_capacity(graph, module, gateways)
        if not unique:
            continue
        candidate = v2.transform_module(graph, module, gateways, capacity)
        if len(candidate.edges) < len(graph.edges):
            yield (
                "two_terminal_module",
                "exact_two_terminal_module",
                "+".join(sorted(module)),
                candidate,
            )

    zero_columns = [
        index
        for index in range(len(graph.edges))
        if not any(row[index] for row in analysis.incidence)
    ]
    for index in zero_columns:
        u, v = graph.edges[index]
        if {u, v} & boundary_nodes:
            move = "saturated_terminal_zero_column_contraction"
            suffix = "_saturated"
        else:
            move = "zero_column_contraction"
            suffix = "_zero"
        yield (
            "saturated_or_zero_column",
            move,
            f"{u}-{v}",
            v2.transform_contract(graph, u, v, suffix),
        )

    node_signatures = {
        node: tuple(row[index] for row in analysis.sides)
        for index, node in enumerate(graph.nodes)
    }
    for u, v in itertools.combinations(graph.nodes, 2):
        if (
            u not in boundary_nodes
            and v not in boundary_nodes
            and node_signatures[u] == node_signatures[v]
        ):
            yield (
                "inseparable_contraction",
                "inseparable_vertex_contraction_parallel_sum",
                f"{u}+{v}",
                v2.transform_contract(graph, u, v, "_inseparable"),
            )

    for move, object_name, candidate in v3.fifth_candidates(graph):
        yield "delta_y_y_delta", move, object_name, candidate


def saturate_orbit(
    endpoint: Any,
    state_cap: int = STATE_CAP,
    wall_seconds: float = ENDPOINT_WALL_SECONDS,
) -> SaturationResult:
    """Close an endpoint under every exact accepted move until queue exhaustion."""
    started = time.monotonic()
    endpoint_analysis = enumerate_terminal_cuts(endpoint)
    if not endpoint_analysis.unique:
        raise ValueError(f"endpoint {endpoint.name} has nonunique terminal minimizers")
    initial = SaturationState(endpoint, endpoint_analysis, (), 0)
    initial_key = terminal_fixed_weighted_canonical_key(endpoint)
    states_by_key = {initial_key: initial}
    queue = [initial]
    accepted = {move_class: 0 for move_class in MOVE_CLASSES}
    novel = {move_class: 0 for move_class in MOVE_CLASSES}
    cursor = 0
    saturated = True
    budget_reason = ""
    while cursor < len(queue):
        if time.monotonic() - started >= wall_seconds:
            saturated = False
            budget_reason = f"endpoint_wall_seconds={wall_seconds:g}"
            break
        current = queue[cursor]
        cursor += 1
        for move_class, move, object_name, candidate in move_candidates(
            current.graph, current.analysis
        ):
            checked = same_fingerprint_unique(current.analysis, candidate)
            if checked is None:
                continue
            if checked.values != endpoint_analysis.values:
                raise AssertionError(
                    f"accepted {move} at {object_name} changed endpoint fingerprint"
                )
            accepted[move_class] += 1
            key = terminal_fixed_weighted_canonical_key(candidate)
            if key in states_by_key:
                continue
            if len(states_by_key) >= state_cap:
                saturated = False
                budget_reason = f"state_cap={state_cap}"
                break
            replacement_depth = current.replacement_depth + int(
                move_class == "delta_y_y_delta"
            )
            state = SaturationState(
                candidate,
                checked,
                current.path + ((move, object_name),),
                replacement_depth,
            )
            states_by_key[key] = state
            queue.append(state)
            novel[move_class] += 1
        if not saturated:
            break
    max_depth = max(state.replacement_depth for state in states_by_key.values())
    all_equal = all(
        state.analysis.unique and state.analysis.values == endpoint_analysis.values
        for state in states_by_key.values()
    )
    if not all_equal:
        raise AssertionError("an admitted canonical state failed full fingerprint audit")
    return SaturationResult(
        states_by_key=states_by_key,
        saturated=saturated,
        budget_reason=budget_reason,
        max_replacement_depth=max_depth,
        accepted_transition_census=accepted,
        novel_state_census=novel,
        fingerprint_full_recheck_count=len(states_by_key),
        all_admitted_fingerprints_equal=all_equal,
    )


def intersect_saturated_orbits(
    base: SaturationResult, perturbed: SaturationResult
) -> dict[str, Any]:
    common = sorted(set(base.states_by_key) & set(perturbed.states_by_key))
    if common:
        key = common[0]
        left = base.states_by_key[key]
        right = perturbed.states_by_key[key]
        path = f"base:{path_text(left.path)} || perturbed:{path_text(right.path)}"
        verdict = f"GAUGE via path {path}"
    elif base.saturated and perturbed.saturated:
        path = ""
        verdict = "complete five-move-orbit-disjoint (saturated)"
    else:
        reasons = sorted(
            reason
            for reason in (base.budget_reason, perturbed.budget_reason)
            if reason
        )
        path = ""
        verdict = (
            f"budget-truncated at {'|'.join(reasons)}, disjoint within explored sets"
        )
    return {
        "cross_orbit_weighted_isomorphism_count": len(common),
        "verdict": verdict,
        "path_if_gauge": path,
    }
