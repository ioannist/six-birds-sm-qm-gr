#!/usr/bin/env python3
"""Probe whether Step 55 fingerprint kernels survive exact graph quotients."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np


PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parents[2]
THREAD_DIR = REPO_ROOT / "physics_atlas" / "thread_qm_gr"
STEP42_SCRIPT = THREAD_DIR / "steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"
STEP44_SCRIPT = THREAD_DIR / "steps/step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py"
STEP55_SCRIPT = THREAD_DIR / "steps/step55_f51_entanglement_underdetermines_geometry_artifacts/entanglement_underdetermines_geometry_step55.py"

EXPECTED_HASHES = {
    STEP42_SCRIPT: "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08",
    STEP44_SCRIPT: "61f28d10e8170a9f37ac71a711b6d30c3dac9b4f014b8e634c70ba2166a47052",
    STEP55_SCRIPT: "a21740d3f8266c1213bf46f1e1a4a37367b6cb3f2d61b742301539a626d760aa",
}

SEEDS = [101, 202, 303]
RESULTS_FILE = PROBE_DIR / "p1_kernel_verdicts.csv"
FINDINGS_FILE = PROBE_DIR / "FINDINGS.md"


@dataclass(frozen=True)
class Carrier:
    name: str
    labels: list[str]
    edges: list[tuple[str, str]]
    base_weights: np.ndarray
    topology: str


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_frozen_inputs() -> None:
    for path, expected in EXPECTED_HASHES.items():
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"frozen hash mismatch for {path}: {actual} != {expected}")


def canonical_edge(u: str, v: str) -> tuple[str, str]:
    return tuple(sorted((u, v)))


def carrier_from_edges(
    name: str,
    labels: list[str],
    weighted_edges: list[tuple[str, str, float]],
    topology: str,
) -> Carrier:
    by_edge: dict[tuple[str, str], float] = {}
    for u, v, weight in weighted_edges:
        edge = canonical_edge(u, v)
        if edge in by_edge:
            raise ValueError(f"parallel edge in {name}: {edge}")
        by_edge[edge] = float(weight)
    edges = sorted(by_edge)
    return Carrier(name, labels, edges, np.array([by_edge[edge] for edge in edges]), topology)


def published_carrier(s42: Any, s55: Any) -> Carrier:
    labels = s55.frozen_boundary_labels(s42)
    edges, weights = s55.extract_step42_edges(s42)
    return Carrier(
        "published_step42_raw",
        labels,
        edges,
        weights,
        "three bivalent L-Mi-R paths; exact per-path-minimum/sum quotient",
    )


def crosslinked_carrier() -> Carrier:
    labels = [f"L{i}" for i in range(4)] + [f"R{i}" for i in range(4)]
    rows: list[tuple[str, str, float]] = []
    rows.extend((label, "L", 2.8) for label in labels[:4])
    rows.extend((label, "R", 2.8) for label in labels[4:])
    for index in range(3):
        rows.append(("L", f"M{index}", 1.1))
        rows.append((f"M{index}", "R", 1.1))
    rows.extend((f"M{i}", f"M{j}", 0.9) for i in range(3) for j in range(i + 1, 3))
    return carrier_from_edges(
        "crosslinked_three_path",
        labels,
        rows,
        "all Mi cross-linked; no bivalent interior node, but one exact two-terminal module",
    )


def grid_carrier() -> Carrier:
    labels = [f"B{i}" for i in range(6)]
    nodes = ["U0", "U1", "U2", "V0", "V1", "V2"]
    rows = [(label, node, 3.0) for label, node in zip(labels, nodes)]
    rows.extend(
        [
            ("U0", "U1", 1.0),
            ("U1", "U2", 1.0),
            ("V0", "V1", 1.0),
            ("V1", "V2", 1.0),
            ("U0", "V0", 1.0),
            ("U1", "V1", 1.0),
            ("U2", "V2", 1.0),
        ]
    )
    return carrier_from_edges(
        "grid_2x3_multiterminal",
        labels,
        rows,
        "2x3 grid with a boundary terminal at every grid node; no eliminable interior node",
    )


def k4_carrier(stiff_chord: bool = False) -> Carrier:
    labels = [f"B{i}" for i in range(8)]
    interiors = [f"I{i}" for i in range(4)]
    rows = [(label, interiors[index // 2], 3.0) for index, label in enumerate(labels)]
    rows.extend(
        (
            interiors[i],
            interiors[j],
            8.0 if stiff_chord and (i, j) == (0, 1) else 1.0,
        )
        for i in range(4)
        for j in range(i + 1, 4)
    )
    return carrier_from_edges(
        "k4_well_connected_stiff_chord" if stiff_chord else "k4_well_connected",
        labels,
        rows,
        (
            "K4 interior with a stiff I0-I1 chord; two boundary leaves per interior node; interior degree five"
            if stiff_chord
            else "K4 interior with two boundary leaves per interior node; interior degree five"
        ),
    )


def generic_weights(carrier: Carrier, seed: int, s55: Any) -> np.ndarray:
    return s55.generic_weights(carrier.base_weights, seed)


def structural_summary(carrier: Carrier) -> tuple[int, int, int]:
    boundary = set(carrier.labels)
    degrees: dict[str, int] = {}
    gateways: set[str] = set()
    for u, v in carrier.edges:
        degrees[u] = degrees.get(u, 0) + 1
        degrees[v] = degrees.get(v, 0) + 1
        if u in boundary and v not in boundary:
            gateways.add(v)
        if v in boundary and u not in boundary:
            gateways.add(u)
    interior = [node for node in degrees if node not in boundary]
    series_nodes = sum(degrees[node] == 2 for node in interior)
    return series_nodes, len(gateways), min(degrees[node] for node in interior)


def analyze(
    carrier: Carrier,
    weights: np.ndarray,
    spec: dict[str, Any],
    s44: Any,
    s55: Any,
) -> dict[str, Any]:
    jacobian = s55.central_jacobian(carrier.edges, weights, carrier.labels, spec, s44)
    rank, nullity, singular_values = s55.rank_nullity(jacobian)
    _u, _s, vt = np.linalg.svd(jacobian, full_matrices=True)
    base = s55.full_fingerprint(carrier.edges, weights, carrier.labels, spec, s44)
    finite_kernel_residuals: list[float] = []
    for vector in vt[rank:]:
        direction = 0.01 * vector / float(np.max(np.abs(vector)))
        for sign in [1.0, -1.0]:
            moved = weights + sign * direction
            finite_kernel_residuals.append(
                float(
                    np.max(
                        np.abs(
                            s55.full_fingerprint(carrier.edges, moved, carrier.labels, spec, s44)
                            - base
                        )
                    )
                )
            )
    shadows = s55.clean_shadow_edges(carrier.edges, weights, carrier.labels, spec, s44)
    return {
        "rank": rank,
        "nullity": nullity,
        "clean_shadow_count": len(shadows),
        "clean_shadow_edges": [str(row["edge"]) for row in shadows],
        "finite_kernel_basis_max_residual": max(finite_kernel_residuals, default=0.0),
        "singular_values": singular_values,
    }


def rank_only(
    carrier: Carrier,
    weights: np.ndarray,
    spec: dict[str, Any],
    s44: Any,
    s55: Any,
) -> dict[str, int]:
    jacobian = s55.central_jacobian(carrier.edges, weights, carrier.labels, spec, s44)
    rank, nullity, _singular_values = s55.rank_nullity(jacobian)
    return {"rank": rank, "nullity": nullity}


def two_terminal_capacity(
    carrier: Carrier,
    weights: np.ndarray,
    left: str,
    right: str,
    s44: Any,
    s55: Any,
) -> float:
    boundary = set(carrier.labels)
    graph: dict[str, dict[str, float]] = {}
    for (u, v), weight in zip(carrier.edges, weights):
        if u not in boundary and v not in boundary:
            s44.add_undirected(graph, u, v, float(weight))
    s44.add_edge(graph, "source", left, s55.INF)
    s44.add_edge(graph, right, "sink", s55.INF)
    return float(s44.maxflow_mincut(graph)["min_cut"])


def aggregate_two_terminal(
    carrier: Carrier,
    weights: np.ndarray,
    s44: Any,
    s55: Any,
) -> tuple[Carrier, np.ndarray, int]:
    boundary = set(carrier.labels)
    boundary_rows = [
        (u, v, float(weight))
        for (u, v), weight in zip(carrier.edges, weights)
        if u in boundary or v in boundary
    ]
    capacity = two_terminal_capacity(carrier, weights, "L", "R", s44, s55)
    reduced = carrier_from_edges(
        f"{carrier.name}_aggregate",
        carrier.labels,
        boundary_rows + [("L", "R", capacity)],
        "eight leaf weights plus one aggregate L-R capacity",
    )
    internal_count = len(carrier.edges) - len(boundary_rows)
    return reduced, reduced.base_weights.copy(), internal_count - 1


def prune_terminal_cut_irrelevant_edges(
    carrier: Carrier,
    weights: np.ndarray,
    spec: dict[str, Any],
    s44: Any,
    s55: Any,
) -> tuple[Carrier, np.ndarray, list[str], float]:
    target = s55.full_fingerprint(carrier.edges, weights, carrier.labels, spec, s44)
    edges = list(carrier.edges)
    kept_weights = weights.copy()
    removed: list[str] = []
    while True:
        changed = False
        for idx, (u, v) in enumerate(edges):
            candidate_edges = edges[:idx] + edges[idx + 1 :]
            candidate_weights = np.delete(kept_weights, idx)
            candidate = s55.full_fingerprint(candidate_edges, candidate_weights, carrier.labels, spec, s44)
            if float(np.max(np.abs(candidate - target))) < s55.FINGERPRINT_TOL:
                removed.append(f"{u}-{v}")
                edges = candidate_edges
                kept_weights = candidate_weights
                changed = True
                break
        if not changed:
            break
    reduced = Carrier(
        f"{carrier.name}_terminal_cut_reduced",
        carrier.labels,
        edges,
        kept_weights.copy(),
        "exact pruning of edges irrelevant to every terminal minimum cut at this seeded carrier",
    )
    reduced_fingerprint = s55.full_fingerprint(edges, kept_weights, carrier.labels, spec, s44)
    residual = float(np.max(np.abs(reduced_fingerprint - target)))
    return reduced, kept_weights, removed, residual


def original_k_formula(carrier: Carrier, weights: np.ndarray) -> float:
    by_edge = {edge: float(weight) for edge, weight in zip(carrier.edges, weights)}
    return sum(
        min(by_edge[canonical_edge("L", f"M{i}")], by_edge[canonical_edge(f"M{i}", "R")])
        for i in range(3)
    )


def k_compensated_invariance(
    carrier: Carrier,
    weights: np.ndarray,
    spec: dict[str, Any],
    s44: Any,
    s55: Any,
) -> float:
    by_edge = {edge: idx for idx, edge in enumerate(carrier.edges)}
    limiting: list[int] = []
    slack: list[int] = []
    gaps: list[float] = []
    for i in range(3):
        pair = [by_edge[canonical_edge("L", f"M{i}")], by_edge[canonical_edge(f"M{i}", "R")]]
        pair.sort(key=lambda idx: weights[idx])
        limiting.append(pair[0])
        slack.append(pair[1])
        gaps.append(float(weights[pair[1]] - weights[pair[0]]))
    delta = min(0.05, min(gaps) / 4.0, min(weights[limiting]) / 4.0)
    if delta <= 1e-8:
        raise RuntimeError("generic original carrier is too close to a path-minimum tie")
    directions: list[np.ndarray] = []
    for idx in slack:
        direction = np.zeros(len(weights))
        direction[idx] = delta
        directions.append(direction)
    for left, right in [(0, 1), (1, 2)]:
        direction = np.zeros(len(weights))
        direction[limiting[left]] = delta
        direction[limiting[right]] = -delta
        directions.append(direction)
    base = s55.full_fingerprint(carrier.edges, weights, carrier.labels, spec, s44)
    residuals = []
    base_k = original_k_formula(carrier, weights)
    for direction in directions:
        for sign in [1.0, -1.0]:
            moved = weights + sign * direction
            residuals.append(float(np.max(np.abs(s55.full_fingerprint(carrier.edges, moved, carrier.labels, spec, s44) - base))))
            if abs(original_k_formula(carrier, moved) - base_k) > 1e-10:
                raise RuntimeError("K-compensated direction did not preserve K")
    return max(residuals)


def feature_count(spec: dict[str, Any], s55: Any) -> int:
    zeros = np.zeros(len(spec["region_masks"]))
    return len(s55.feature_vector(zeros, spec))


def format_ints(values: list[int]) -> str:
    return "[" + ", ".join(str(value) for value in values) + "]"


def write_results(rows: list[dict[str, Any]]) -> None:
    fields = [
        "carrier",
        "seed",
        "topology",
        "boundary_count",
        "region_count",
        "fingerprint_feature_count",
        "enumeration",
        "raw_parameter_count",
        "raw_rank",
        "raw_nullity",
        "clean_shadow_count_both_direction",
        "clean_shadow_edges",
        "finite_kernel_basis_max_residual",
        "series_node_count",
        "boundary_gateway_count",
        "minimum_interior_degree",
        "exact_reduction",
        "reducible_redundancy_dimension",
        "quotient_parameter_count",
        "quotient_rank",
        "residual_kernel_after_quotient",
        "original_vs_quotient_fingerprint_residual",
        "k_compensated_invariance_residual",
        "removed_terminal_cut_irrelevant_edges",
    ]
    with RESULTS_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_findings(rows: list[dict[str, Any]]) -> None:
    by_carrier: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_carrier.setdefault(str(row["carrier"]), []).append(row)
    order = [
        "published_step42_raw",
        "published_step42_aggregate_control",
        "crosslinked_three_path",
        "grid_2x3_multiterminal",
        "k4_well_connected",
        "k4_well_connected_stiff_chord",
    ]
    table = [
        "| Carrier | Raw nullity | Reducible redundancy | Residual after quotient | Clean shadows |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in order:
        carrier_rows = by_carrier[name]
        table.append(
            "| "
            + name
            + " | "
            + format_ints([int(row["raw_nullity"]) for row in carrier_rows])
            + " | "
            + format_ints([int(row["reducible_redundancy_dimension"]) for row in carrier_rows])
            + " | "
            + format_ints([int(row["residual_kernel_after_quotient"]) for row in carrier_rows])
            + " | "
            + format_ints([int(row["clean_shadow_count_both_direction"]) for row in carrier_rows])
            + " |"
        )
    tested_nonreducible = [
        "crosslinked_three_path",
        "grid_2x3_multiterminal",
        "k4_well_connected",
        "k4_well_connected_stiff_chord",
    ]
    residual = {
        name: [int(row["residual_kernel_after_quotient"]) for row in by_carrier[name]]
        for name in tested_nonreducible
    }
    survivors = [name for name, values in residual.items() if any(value > 0 for value in values)]
    if survivors:
        conclusion = (
            "A residual fingerprint kernel survives the declared exact quotients on "
            + ", ".join(survivors)
            + ". This is finite-carrier evidence that underdetermination is not solely the published carrier's series/parallel parameter redundancy; it is not a universal theorem, and clean-shadow counts identify locally inactive edge directions where present."
        )
    else:
        conclusion = (
            "No residual fingerprint kernel survives on any tested non-reducible carrier after the identifiable exact quotients. In this probe, every observed kernel is parameterization redundancy, so the published Step 55 carrier does not support a robust non-gauge underdetermination claim."
        )
    max_original_residual = max(
        float(row["original_vs_quotient_fingerprint_residual"])
        for row in by_carrier["published_step42_raw"]
    )
    max_k_residual = max(
        float(row["k_compensated_invariance_residual"])
        for row in by_carrier["published_step42_raw"]
    )
    grid_removed = [str(row["removed_terminal_cut_irrelevant_edges"]) for row in by_carrier["grid_2x3_multiterminal"]]
    grid_shadows = [str(row["clean_shadow_edges"]) for row in by_carrier["grid_2x3_multiterminal"]]
    stiff_shadows = [str(row["clean_shadow_edges"]) for row in by_carrier["k4_well_connected_stiff_chord"]]
    stiff_finite_residuals = [
        float(row["finite_kernel_basis_max_residual"])
        for row in by_carrier["k4_well_connected_stiff_chord"]
    ]
    if any(grid_removed):
        grid_reduction_note = f"Exact deletion removed edge sets `{grid_removed}`."
    else:
        grid_reduction_note = (
            f"the clean-shadow edge sets are `{grid_shadows}`, but deleting each candidate changes at least one terminal min-cut; "
            "the exact pruning pass therefore removed no edge."
        )
    stiff_removed = [
        str(row["removed_terminal_cut_irrelevant_edges"])
        for row in by_carrier["k4_well_connected_stiff_chord"]
    ]
    text = f"""# P1 Kernel-Quotient Probe Findings

The probe hash-pins and imports the frozen Step 42, Step 44, and Step 55 Python machinery. It uses Step 55's generic weights, complete boundary-region fingerprint, central difference (`1e-6`), rank tolerance (`1e-6`), and both-direction finite clean-shadow test. Every carrier enumerates all `2^n-2` nontrivial boundary regions; no enumeration is truncated.

## Verdict table

{chr(10).join(table)}

The published carrier reproduces rank/nullity `[9, 9, 9] / [5, 5, 5]`. Replacing its six bridge-half-edge coordinates by `K=sum_i min(w_LMi,w_MiR)` gives nine parameters and rank/nullity `[9, 9, 9] / [0, 0, 0]`. The maximum original-versus-aggregate full-fingerprint residual is `{max_original_residual:.3g}`; five independent finite slack/K-compensated directions have maximum residual `{max_k_residual:.3g}`.

The cross-linked carrier has no bivalent interior node but remains an exact two-terminal module, so it is replaced by its computed L-R min-cut capacity before assigning any residual kernel. The grid and K4 carriers have no parallel edges, no bivalent interior nodes, and boundary access through more than two interior gateways. For every raw kernel, a stronger exact-reduction pass attempts to delete each edge and retains the deletion only if every terminal min-cut remains unchanged. For the grid, {grid_reduction_note} The balanced K4 carrier is already full rank. The stiff-chord K4 clean-shadow sets are `{stiff_shadows}` and exact-pruning removals are `{stiff_removed}`. Its seed-303 nullity is three despite zero clean-shadow edges, so that kernel is a coupled invisible subspace rather than a collection of zero Jacobian columns. Finite `0.01` moves along every numerical kernel-basis direction have per-seed maximum full-fingerprint residuals `{stiff_finite_residuals}`.

## Honest conclusion

{conclusion}
"""
    FINDINGS_FILE.write_text(text, encoding="utf-8")


def main() -> None:
    verify_frozen_inputs()
    s42 = import_module(STEP42_SCRIPT, "p1_step42_frozen")
    s44 = import_module(STEP44_SCRIPT, "p1_step44_frozen")
    s55 = import_module(STEP55_SCRIPT, "p1_step55_frozen")
    original = published_carrier(s42, s55)
    carriers = [original, crosslinked_carrier(), grid_carrier(), k4_carrier(), k4_carrier(stiff_chord=True)]
    specs = {len(carrier.labels): s55.precompute_feature_spec(len(carrier.labels)) for carrier in carriers}
    rows: list[dict[str, Any]] = []

    for seed in SEEDS:
        original_weights = generic_weights(original, seed, s55)
        for carrier in carriers:
            weights = original_weights if carrier.name == original.name else generic_weights(carrier, seed, s55)
            spec = specs[len(carrier.labels)]
            raw = analyze(carrier, weights, spec, s44, s55)
            series_nodes, gateway_count, min_degree = structural_summary(carrier)
            reduction = "none_identified"
            quotient = carrier
            quotient_weights = weights
            redundancy = 0
            quotient_residual = 0.0
            k_residual: float | str = ""
            removed_edges: list[str] = []
            if carrier.name in {"published_step42_raw", "crosslinked_three_path"}:
                quotient, quotient_weights, redundancy = aggregate_two_terminal(carrier, weights, s44, s55)
                reduction = (
                    "K=sum_i_min(path_halves)"
                    if carrier.name == "published_step42_raw"
                    else "exact_two_terminal_LR_mincut_capacity"
                )
                base_fp = s55.full_fingerprint(carrier.edges, weights, carrier.labels, spec, s44)
                quotient_fp = s55.full_fingerprint(quotient.edges, quotient_weights, quotient.labels, spec, s44)
                quotient_residual = float(np.max(np.abs(base_fp - quotient_fp)))
                if carrier.name == "published_step42_raw":
                    mincut_k = two_terminal_capacity(carrier, weights, "L", "R", s44, s55)
                    if abs(original_k_formula(carrier, weights) - mincut_k) > 1e-10:
                        raise RuntimeError("per-path K formula disagrees with L-R min-cut")
                    k_residual = k_compensated_invariance(carrier, weights, spec, s44, s55)
            elif raw["nullity"] > 0:
                quotient, quotient_weights, removed_edges, quotient_residual = prune_terminal_cut_irrelevant_edges(
                    carrier, weights, spec, s44, s55
                )
                if removed_edges:
                    reduction = "exact_terminal_cut_irrelevant_edge_pruning"
                    redundancy = len(removed_edges)
                else:
                    quotient = carrier
                    quotient_weights = weights
            quotient_spec = specs[len(quotient.labels)]
            quotient_analysis = (
                raw
                if quotient is carrier
                else rank_only(quotient, quotient_weights, quotient_spec, s44, s55)
            )
            rows.append(
                {
                    "carrier": carrier.name,
                    "seed": seed,
                    "topology": carrier.topology,
                    "boundary_count": len(carrier.labels),
                    "region_count": len(spec["region_masks"]),
                    "fingerprint_feature_count": feature_count(spec, s55),
                    "enumeration": "complete",
                    "raw_parameter_count": len(carrier.edges),
                    "raw_rank": raw["rank"],
                    "raw_nullity": raw["nullity"],
                    "clean_shadow_count_both_direction": raw["clean_shadow_count"],
                    "clean_shadow_edges": ";".join(raw["clean_shadow_edges"]),
                    "finite_kernel_basis_max_residual": f"{float(raw['finite_kernel_basis_max_residual']):.12g}",
                    "series_node_count": series_nodes,
                    "boundary_gateway_count": gateway_count,
                    "minimum_interior_degree": min_degree,
                    "exact_reduction": reduction,
                    "reducible_redundancy_dimension": redundancy,
                    "quotient_parameter_count": len(quotient.edges),
                    "quotient_rank": quotient_analysis["rank"],
                    "residual_kernel_after_quotient": quotient_analysis["nullity"],
                    "original_vs_quotient_fingerprint_residual": f"{quotient_residual:.12g}",
                    "k_compensated_invariance_residual": "" if k_residual == "" else f"{float(k_residual):.12g}",
                    "removed_terminal_cut_irrelevant_edges": ";".join(removed_edges),
                }
            )

        reduced, reduced_weights, _dimension = aggregate_two_terminal(original, original_weights, s44, s55)
        spec = specs[len(reduced.labels)]
        result = analyze(reduced, reduced_weights, spec, s44, s55)
        series_nodes, gateway_count, min_degree = structural_summary(reduced)
        rows.append(
            {
                "carrier": "published_step42_aggregate_control",
                "seed": seed,
                "topology": reduced.topology,
                "boundary_count": len(reduced.labels),
                "region_count": len(spec["region_masks"]),
                "fingerprint_feature_count": feature_count(spec, s55),
                "enumeration": "complete",
                "raw_parameter_count": len(reduced.edges),
                "raw_rank": result["rank"],
                "raw_nullity": result["nullity"],
                "clean_shadow_count_both_direction": result["clean_shadow_count"],
                "clean_shadow_edges": ";".join(result["clean_shadow_edges"]),
                "finite_kernel_basis_max_residual": f"{float(result['finite_kernel_basis_max_residual']):.12g}",
                "series_node_count": series_nodes,
                "boundary_gateway_count": gateway_count,
                "minimum_interior_degree": min_degree,
                "exact_reduction": "already_reduced_positive_control",
                "reducible_redundancy_dimension": 0,
                "quotient_parameter_count": len(reduced.edges),
                "quotient_rank": result["rank"],
                "residual_kernel_after_quotient": result["nullity"],
                "original_vs_quotient_fingerprint_residual": "0",
                "k_compensated_invariance_residual": "",
                "removed_terminal_cut_irrelevant_edges": "",
            }
        )

    expected = [
        (int(row["raw_rank"]), int(row["raw_nullity"]))
        for row in rows
        if row["carrier"] == "published_step42_raw"
    ]
    if expected != [(9, 5), (9, 5), (9, 5)]:
        raise RuntimeError(f"published raw result did not reproduce: {expected}")
    control = [
        (int(row["raw_rank"]), int(row["raw_nullity"]))
        for row in rows
        if row["carrier"] == "published_step42_aggregate_control"
    ]
    if control != [(9, 0), (9, 0), (9, 0)]:
        raise RuntimeError(f"aggregate positive control failed: {control}")
    write_results(rows)
    write_findings(rows)
    print(f"wrote {RESULTS_FILE.relative_to(REPO_ROOT)}")
    print(f"wrote {FINDINGS_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
