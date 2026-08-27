#!/usr/bin/env python3
"""Pinned, exact-rational loading of the 19 PROG3 direction fibers."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from dataclasses import dataclass, replace
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEP1_DIR = HERE.parent / "step1_engine"
PROG3_DIR = REPO_ROOT / "open_programs/prog3_cut_fingerprints/step1_finite_range"

PATHS_AND_PINS = {
    STEP1_DIR / "tensor_engine.py": "52640d2d195d3928ff18c01af59f3a06a72d10fb10f136b69f5a4b2f65f774df",
    STEP1_DIR / "state_entropy.py": "24b27147295af99402193bec760957ef7041b555e5da6875e92524072821df5a",
    STEP1_DIR / "gauge_library.py": "8d0abd47615c2d5e62a6c6a8fd3bb868c7c4cec73ae81d7da19e583b48afcfe1",
    STEP1_DIR / "step1_core.py": "350902bd4c12150c1a5470e336d7a03e4334acbe907dede0d6f5bec71b872733",
    STEP1_DIR / "survivor_loader.py": "9a567e318961009ca69242da64fc268d49c5869dc5485693547126015d9bc78c",
    STEP1_DIR / "step2_contract_requirements.md": "f591296a3166773d5ed26cd3f7628a29feb4c26fa6f0627bf7b5070f88e83fd8",
    PROG3_DIR / "certified_fibers_step1.csv": "09a5abd737f95cb0429b97a4810fd3294bc675a6d6276e72a799c8b23e2a9298",
    PROG3_DIR / "kernel_intervals_step1.csv": "734c6142ad4e1c474b989080ba8f21b0c10094c0db04f70f9918a3a606cfa760",
    PROG3_DIR / "exact_weights_step1.csv": "6e7e6e321c6e6370c9ca63405809482f9b7502ceaa137a3ab315e124b36b78fc",
    PROG3_DIR / "exact_cut_regions_step1.csv": "5bf9d22fcb9e42045efddc6a14405cbca85b021744a4e356a964058a698afe49",
    PROG3_DIR / "exact_engine.py": "8cdb009724dd2d59e1100ecb048d95aa441fa485218e8cb5c34d5ad3b2f4e6c8",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> list[dict[str, Any]]:
    rows = []
    for path, expected in PATHS_AND_PINS.items():
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

from survivor_loader import reconstruct_reduced_graphs  # noqa: E402


@dataclass(frozen=True)
class FiberDefinition:
    fiber_id: str
    carrier: str
    source_seed_provenance: int
    basis_index: int
    graph: Any
    base_capacities: tuple[Fraction, ...]
    perturbed_capacities: tuple[Fraction, ...]
    direction: tuple[int, ...]
    t_star: Fraction


def _read_csv(name: str) -> list[dict[str, str]]:
    with (PROG3_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _parse_direction(graph: Any, text: str) -> tuple[int, ...]:
    coefficients = {}
    for token in text.split():
        coefficient, edge_name = token.split("*", 1)
        coefficients[edge_name] = int(coefficient)
    edge_names = tuple(f"{u}-{v}" for u, v in graph.edges)
    if set(coefficients) - set(edge_names):
        raise AssertionError(f"direction contains unknown edges: {set(coefficients) - set(edge_names)}")
    return tuple(coefficients.get(name, 0) for name in edge_names)


def load_fibers() -> list[FiberDefinition]:
    reconstructed = {
        (row["carrier"], int(row["seed"])): (row, graph)
        for row, graph, _analysis, _moves in reconstruct_reduced_graphs()
    }
    weight_rows = [
        row for row in _read_csv("exact_weights_step1.csv")
        if row["stage"] == "five_move_reduced"
    ]
    weights_by_key: dict[tuple[str, int], list[dict[str, str]]] = {}
    for row in weight_rows:
        weights_by_key.setdefault((row["carrier"], int(row["seed"])), []).append(row)
    intervals = {
        (row["carrier"], int(row["seed"]), int(row["basis_index"])): row
        for row in _read_csv("kernel_intervals_step1.csv")
    }
    fibers = []
    for number, row in enumerate(_read_csv("certified_fibers_step1.csv"), start=1):
        key = (row["carrier"], int(row["seed"]))
        basis_index = int(row["basis_index"])
        _source_row, graph = reconstructed[key]
        exact_rows = sorted(weights_by_key[key], key=lambda item: int(item["edge_index"]))
        if len(exact_rows) != len(graph.edges):
            raise AssertionError(f"edge count mismatch for {key}")
        base = tuple(Fraction(item["weight_exact"]) for item in exact_rows)
        if any(
            (item["u"], item["v"]) != edge
            for item, edge in zip(exact_rows, graph.edges)
        ):
            raise AssertionError(f"edge order mismatch for {key}")
        if base != tuple(weight for _u, _v, weight in graph.weighted_edges):
            raise AssertionError(f"exact base weights disagree with reconstructed graph for {key}")
        direction = _parse_direction(graph, intervals[key + (basis_index,)]["direction"])
        t_star = Fraction(row["t_star_exact"])
        perturbed = tuple(
            capacity + t_star * coefficient
            for capacity, coefficient in zip(base, direction)
        )
        if min(perturbed) <= 0 or base == perturbed:
            raise AssertionError(f"invalid perturbed capacities for {key}, basis {basis_index}")
        fibers.append(
            FiberDefinition(
                fiber_id=f"fiber_{number:03d}",
                carrier=key[0],
                source_seed_provenance=key[1],
                basis_index=basis_index,
                graph=graph,
                base_capacities=base,
                perturbed_capacities=perturbed,
                direction=direction,
                t_star=t_star,
            )
        )
    if len(fibers) != 19:
        raise AssertionError(f"expected 19 fibers, found {len(fibers)}")
    return fibers


def _load_prog3_exact_engine():
    specification = importlib.util.spec_from_file_location(
        "prog2_step2_prog3_exact", PROG3_DIR / "exact_engine.py"
    )
    if specification is None or specification.loader is None:
        raise ImportError(PROG3_DIR / "exact_engine.py")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def nonkernel_control() -> dict[str, Any]:
    """Preregistered edge-0 perturbation on the first wheel carrier."""
    fiber = next(
        item
        for item in load_fibers()
        if item.carrier == "wheel_W4__b8__leaf_offset0"
        and item.source_seed_provenance == 47
        and item.basis_index == 0
    )
    direction = (1,) + (0,) * (len(fiber.base_capacities) - 1)
    moved_weights = tuple(
        weight + fiber.t_star * coefficient
        for weight, coefficient in zip(fiber.base_capacities, direction)
    )
    exact = _load_prog3_exact_engine()
    base_analysis = exact.enumerate_terminal_cuts(fiber.graph)
    moved_graph = replace(
        fiber.graph,
        name=fiber.graph.name + "__step2_nonkernel_control",
        weighted_edges=tuple(
            (u, v, weight)
            for (u, v), weight in zip(fiber.graph.edges, moved_weights)
        ),
    )
    moved_analysis = exact.enumerate_terminal_cuts(moved_graph)
    active_image_nonzero = any(row[0] for row in base_analysis.incidence)
    fingerprint_changed = base_analysis.values != moved_analysis.values
    if not active_image_nonzero or not fingerprint_changed:
        raise AssertionError("preregistered non-kernel control did not change the exact fingerprint")
    return {
        "carrier": fiber.carrier,
        "source_seed_provenance": fiber.source_seed_provenance,
        "graph": fiber.graph,
        "base_capacities": fiber.base_capacities,
        "perturbed_capacities": moved_weights,
        "direction": direction,
        "t_star": fiber.t_star,
        "active_cut_jacobian_image_nonzero": active_image_nonzero,
        "exact_cut_fingerprint_changed": fingerprint_changed,
    }
