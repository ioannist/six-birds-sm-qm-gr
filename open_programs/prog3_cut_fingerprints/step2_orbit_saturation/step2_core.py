#!/usr/bin/env python3
"""Deterministic computations for PROG3 orbit saturation."""

from __future__ import annotations

import ast
import csv
import inspect
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from saturation_engine import (
    ENDPOINT_WALL_SECONDS,
    MOVE_CLASSES,
    STATE_CAP,
    intersect_saturated_orbits,
    saturate_orbit,
    verify_pins,
)
from exact_engine import (
    enumerate_terminal_cuts,
    five_move_closure_exact,
    nullspace_basis,
    perturb,
    terminal_fixed_weighted_canonical_key,
    v2,
)
from step1_core import carrier_map, read_survivor_rows


HERE = Path(__file__).resolve().parent
STEP1_DIR = HERE.parent / "step1_finite_range"


@dataclass(frozen=True)
class FiberPair:
    fiber_id: str
    carrier: str
    seed: int
    basis_index: int
    base: Any
    perturbed: Any
    t_star: Fraction


def read_csv(name: str) -> list[dict[str, str]]:
    with (STEP1_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_fiber_pairs() -> list[FiberPair]:
    carriers = carrier_map()
    reduced_by_key = {}
    for row in read_survivor_rows():
        key = (row["carrier"], int(row["seed"]))
        raw = v2.seeded_weights(carriers[key[0]], key[1])
        reduced, analysis, _moves = five_move_closure_exact(raw)
        reduced_by_key[key] = (reduced, analysis)

    exact_weight_rows = [
        row
        for row in read_csv("exact_weights_step1.csv")
        if row["stage"] == "five_move_reduced"
    ]
    weights_by_key: dict[tuple[str, int], list[dict[str, str]]] = {}
    for row in exact_weight_rows:
        weights_by_key.setdefault((row["carrier"], int(row["seed"])), []).append(row)

    pairs = []
    for number, row in enumerate(read_csv("certified_fibers_step1.csv"), start=1):
        key = (row["carrier"], int(row["seed"]))
        basis_index = int(row["basis_index"])
        base, analysis = reduced_by_key[key]
        exact_rows = sorted(weights_by_key[key], key=lambda item: int(item["edge_index"]))
        exact_weights = tuple(Fraction(item["weight_exact"]) for item in exact_rows)
        if exact_weights != base.weights:
            raise AssertionError(f"exact-weight artifact mismatch for {key}")
        basis = nullspace_basis(analysis.incidence)
        direction = basis[basis_index]
        t_star = Fraction(row["t_star_exact"])
        moved = perturb(base, direction, t_star)
        moved_analysis = enumerate_terminal_cuts(moved)
        if (
            not moved_analysis.unique
            or moved_analysis.values != analysis.values
            or min(moved.weights) <= 0
        ):
            raise AssertionError(f"invalid pinned fiber {key}, basis {basis_index}")
        pairs.append(
            FiberPair(
                fiber_id=f"fiber_{number:03d}",
                carrier=key[0],
                seed=key[1],
                basis_index=basis_index,
                base=base,
                perturbed=moved,
                t_star=t_star,
            )
        )
    if len(pairs) != 19:
        raise AssertionError(f"expected 19 fibers, found {len(pairs)}")
    return pairs


def _census_text(census: dict[str, int]) -> str:
    return "|".join(f"{name}:{census[name]}" for name in MOVE_CLASSES)


def endpoint_row(fiber: FiberPair, side: str, result) -> dict[str, Any]:
    return {
        "fiber_id": fiber.fiber_id,
        "carrier": fiber.carrier,
        "seed": fiber.seed,
        "basis_index": fiber.basis_index,
        "endpoint": side,
        "saturated": result.saturated,
        "budget_truncated": not result.saturated,
        "budget_reason": result.budget_reason,
        "canonical_state_count": len(result.states_by_key),
        "max_replacement_depth": result.max_replacement_depth,
        "accepted_move_census": _census_text(result.accepted_transition_census),
        "novel_state_census": _census_text(result.novel_state_census),
        **{
            f"accepted_{name}": result.accepted_transition_census[name]
            for name in MOVE_CLASSES
        },
        **{
            f"novel_{name}": result.novel_state_census[name]
            for name in MOVE_CLASSES
        },
        "fingerprint_full_recheck_count": result.fingerprint_full_recheck_count,
        "all_admitted_fingerprints_equal": result.all_admitted_fingerprints_equal,
        "all_weights_exact_fraction": all(
            isinstance(weight, Fraction)
            for state in result.states_by_key.values()
            for weight in state.graph.weights
        ),
    }


def saturate_all() -> dict[str, Any]:
    pairs = load_fiber_pairs()
    base_cache = {}
    endpoint_rows = []
    fiber_rows = []
    fingerprint_rows = []
    for fiber in pairs:
        cache_key = (fiber.carrier, fiber.seed)
        if cache_key not in base_cache:
            base_cache[cache_key] = saturate_orbit(fiber.base)
        base = base_cache[cache_key]
        perturbed = saturate_orbit(fiber.perturbed)
        intersection = intersect_saturated_orbits(base, perturbed)
        base_row = endpoint_row(fiber, "base", base)
        perturbed_row = endpoint_row(fiber, "perturbed", perturbed)
        endpoint_rows.extend((base_row, perturbed_row))
        fingerprint_rows.extend(
            {
                "fiber_id": fiber.fiber_id,
                "endpoint": side,
                "canonical_state_count": row["canonical_state_count"],
                "full_exact_recheck_count": row["fingerprint_full_recheck_count"],
                "all_states_rechecked": row["canonical_state_count"]
                == row["fingerprint_full_recheck_count"],
                "all_complete_terminal_fingerprints_equal": row[
                    "all_admitted_fingerprints_equal"
                ],
                "all_weights_exact_fraction": row["all_weights_exact_fraction"],
            }
            for side, row in (("base", base_row), ("perturbed", perturbed_row))
        )
        fiber_rows.append(
            {
                "fiber_id": fiber.fiber_id,
                "carrier": fiber.carrier,
                "seed": fiber.seed,
                "basis_index": fiber.basis_index,
                "t_star_exact": str(fiber.t_star),
                "base_saturated": base.saturated,
                "perturbed_saturated": perturbed.saturated,
                "base_canonical_state_count": len(base.states_by_key),
                "perturbed_canonical_state_count": len(perturbed.states_by_key),
                "base_max_replacement_depth": base.max_replacement_depth,
                "perturbed_max_replacement_depth": perturbed.max_replacement_depth,
                "base_accepted_move_census": _census_text(base.accepted_transition_census),
                "perturbed_accepted_move_census": _census_text(
                    perturbed.accepted_transition_census
                ),
                "cross_orbit_weighted_isomorphism_count": intersection[
                    "cross_orbit_weighted_isomorphism_count"
                ],
                "verdict": intersection["verdict"],
                "path_if_gauge": intersection["path_if_gauge"],
            }
        )
    return {
        "fiber_rows": fiber_rows,
        "endpoint_rows": endpoint_rows,
        "fingerprint_rows": fingerprint_rows,
    }


def structural_audit(endpoint_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    import saturation_engine

    source = inspect.getsource(saturation_engine.saturate_orbit)
    tree = ast.parse(source)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    rows = [
        {
            "gate": "exact_full_enumeration_before_admission",
            "passes": "same_fingerprint_unique" in calls,
            "evidence": "every accepted candidate is re-enumerated exactly before canonical admission",
        },
        {
            "gate": "terminal_fixed_exact_weighted_canonicalization",
            "passes": "terminal_fixed_weighted_canonical_key" in calls,
            "evidence": "terminal labels fixed pointwise; non-terminals free; Fraction weights included",
        },
        {
            "gate": "no_replacement_depth_cap",
            "passes": "depth ==" not in source and "depth >=" not in source,
            "evidence": "queue drains only at fixed point or explicit state/wall budget",
        },
        {
            "gate": "hard_safety_budgets_declared",
            "passes": STATE_CAP == 100_000 and ENDPOINT_WALL_SECONDS == 20.0,
            "evidence": f"state_cap={STATE_CAP}; endpoint_wall_seconds={ENDPOINT_WALL_SECONDS:g}",
        },
        {
            "gate": "all_recorded_capacity_paths_exact",
            "passes": all(row["all_weights_exact_fraction"] for row in endpoint_rows),
            "evidence": "every admitted edge weight is fractions.Fraction",
        },
    ]
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"structural audit failure: {rows}")
    return rows


def compute_all() -> dict[str, Any]:
    data = saturate_all()
    data["dependencies"] = verify_pins()
    data["structural_audit"] = structural_audit(data["endpoint_rows"])
    return data
