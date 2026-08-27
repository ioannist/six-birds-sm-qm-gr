#!/usr/bin/env python3
"""Pinned reconstruction of the 13 P1-v3 reduced survivor carriers."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
from pathlib import Path

from tensor_engine import Carrier, uniform_carrier


HERE = Path(__file__).resolve().parent
REPO_ROOT = next(path for path in (HERE, *HERE.parents) if (path / "physics_atlas").is_dir())
P1_DIR = REPO_ROOT / "review_2026/probes/p1_kernel_quotient"
V2_PATH = P1_DIR / "active_cut_quotient_v2.py"
V3_PATH = P1_DIR / "active_cut_quotient_v3.py"
SURVIVORS_PATH = P1_DIR / "p1_v3_survivors.csv"

PINS = {
    V2_PATH: "adcfa43bf35fc2994c9f46fa57d9f9d380e86d6a5eac92a55c7e036a9fea9cc2",
    V3_PATH: "852c3a53e9fe7358c09d5dd60fcdedd28fe2c42d13977dad3390f941479b116d",
    SURVIVORS_PATH: "a0adf2a6dfc97aafdc385beed4ff63d9e90f4f38bcd95e861c25d3097525df07",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> None:
    for path, expected in PINS.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"dependency pin mismatch: {path}: {actual} != {expected}")


def import_v3():
    verify_pins()
    if str(P1_DIR) not in sys.path:
        sys.path.insert(0, str(P1_DIR))
    spec = importlib.util.spec_from_file_location("prog2_p1_v3", V3_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import pinned P1-v3 machinery")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def survivor_rows() -> list[dict[str, str]]:
    verify_pins()
    with SURVIVORS_PATH.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def reconstruct_reduced_graphs():
    module = import_v3()
    bases = {graph.name: graph for graph in module.v2.search_carriers()}
    reconstructed = []
    for row in survivor_rows():
        name = row["carrier"]
        seed = int(row["seed"])
        raw = module.v2.seeded_weights(bases[name], seed)
        reduced, analysis, moves, _audits = module.five_move_closure(raw)
        if len(reduced.edges) != int(row["reduced_edge_count"]):
            raise AssertionError(f"reduced edge mismatch for {name}, seed {seed}")
        if analysis.rank != int(row["reduced_exact_rank"]):
            raise AssertionError(f"rank mismatch for {name}, seed {seed}")
        if len(reduced.edges) - analysis.rank != int(row["residual_deficiency"]):
            raise AssertionError(f"deficiency mismatch for {name}, seed {seed}")
        reconstructed.append((row, reduced, analysis, moves))
    return reconstructed


def as_tensor_carrier(graph, dimension: int) -> Carrier:
    edges = []
    weights = {}
    for index, (u, v, weight) in enumerate(graph.weighted_edges):
        edge_id = f"e{index:02d}"
        edges.append((edge_id, u, v))
        weights[edge_id] = f"{weight.numerator}/{weight.denominator}"
    return uniform_carrier(
        name=f"{graph.name}__D{dimension}",
        vertices=graph.nodes,
        edges=edges,
        boundaries=graph.boundary_nodes,
        dimension=dimension,
        source_weights=weights,
    )
