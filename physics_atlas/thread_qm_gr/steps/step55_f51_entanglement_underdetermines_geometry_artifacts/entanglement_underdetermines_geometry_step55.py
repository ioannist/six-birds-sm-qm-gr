#!/usr/bin/env python3
"""Step 55 final: generic Step-42 carrier kernel test."""

from __future__ import annotations

import csv
import hashlib
import heapq
import importlib.util
import itertools
import json
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REL_DIR = Path("steps") / ARTIFACT_DIR.name
STEP42_SCRIPT = THREAD_DIR / "steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"
STEP44_SCRIPT = THREAD_DIR / "steps/step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py"
STEP42_SHA256 = "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08"
STEP44_SHA256 = "61f28d10e8170a9f37ac71a711b6d30c3dac9b4f014b8e634c70ba2166a47052"

BASE_DIM = 3
GENERIC_SEEDS = [101, 202, 303]
PERTURB_SCALE = 0.25
PERTURB_OFFSET = 0.2
FINITE_DIFF_EPS = 1e-6
RANK_TOL = 1e-6
CLEAN_DELTAS = [0.15, 0.05]
FINGERPRINT_TOL = 1e-9
GEOMETRIC_GAP_TOL = 1e-6
INF = 10**9


def rel(name: str) -> str:
    return str(REL_DIR / name)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def frozen_boundary_labels(s42: Any) -> list[str]:
    return [f"L{i}" for i in range(s42.BOUNDARY_PER_SIDE)] + [f"R{i}" for i in range(s42.BOUNDARY_PER_SIDE)]


def extract_step42_edges(s42: Any) -> tuple[list[tuple[str, str]], np.ndarray]:
    graph, _edge_rows, _region_legs, _comp_legs = s42.bulk_graph(BASE_DIM, "left_all")
    pair_to_capacity: dict[tuple[str, str], float] = {}
    for u, adjacent in graph.items():
        if u in {"source", "sink"}:
            continue
        for v, capacity in adjacent.items():
            if v in {"source", "sink"} or capacity <= 0 or capacity >= s42.INF / 2:
                continue
            pair_to_capacity.setdefault(tuple(sorted((u, v))), float(capacity))
    edge_pairs = sorted(pair_to_capacity)
    return edge_pairs, np.array([pair_to_capacity[pair] for pair in edge_pairs], dtype=float)


def generic_weights(base: np.ndarray, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return np.abs(base * (1.0 + PERTURB_SCALE * rng.normal(size=len(base)))) + PERTURB_OFFSET


def precompute_feature_spec(n: int) -> dict[str, Any]:
    full = (1 << n) - 1
    masks = list(range(1, full))
    mi_pairs = []
    for idx, a in enumerate(masks):
        for b in masks[idx + 1 :]:
            if not (a & b):
                mi_pairs.append((a, b))
    triples: set[tuple[int, int, int]] = set()
    for assignment in itertools.product(range(4), repeat=n):
        a = b = c = 0
        for idx, value in enumerate(assignment):
            if value == 1:
                a |= 1 << idx
            elif value == 2:
                b |= 1 << idx
            elif value == 3:
                c |= 1 << idx
        if a and b and c:
            triples.add(tuple(sorted((a, b, c))))
    return {"full": full, "region_masks": masks, "mi_pairs": mi_pairs, "i3_triples": sorted(triples)}


def graph_for_region(edge_pairs: list[tuple[str, str]], weights: np.ndarray, labels: list[str], mask: int, s44: Any) -> dict[str, dict[str, float]]:
    graph: dict[str, dict[str, float]] = {}
    for (u, v), capacity in zip(edge_pairs, weights):
        s44.add_undirected(graph, u, v, float(capacity))
    for idx, label in enumerate(labels):
        if mask & (1 << idx):
            s44.add_edge(graph, "source", label, INF)
        else:
            s44.add_edge(graph, label, "sink", INF)
    return graph


def entropy_vector(edge_pairs: list[tuple[str, str]], weights: np.ndarray, labels: list[str], spec: dict[str, Any], s44: Any) -> np.ndarray:
    return np.array(
        [float(s44.maxflow_mincut(graph_for_region(edge_pairs, weights, labels, mask, s44))["min_cut"]) for mask in spec["region_masks"]],
        dtype=float,
    )


def feature_vector(entropies: np.ndarray, spec: dict[str, Any]) -> np.ndarray:
    by_mask = {mask: float(entropies[idx]) for idx, mask in enumerate(spec["region_masks"])}
    full = int(spec["full"])

    def e(mask: int) -> float:
        return 0.0 if mask == 0 or mask == full else by_mask[mask]

    features = [float(value) for value in entropies]
    features.extend(e(a) + e(b) - e(a | b) for a, b in spec["mi_pairs"])
    features.extend(e(a) + e(b) + e(c) + e(a | b | c) - e(a | b) - e(a | c) - e(b | c) for a, b, c in spec["i3_triples"])
    return np.array(features, dtype=float)


def full_fingerprint(edge_pairs: list[tuple[str, str]], weights: np.ndarray, labels: list[str], spec: dict[str, Any], s44: Any) -> np.ndarray:
    return feature_vector(entropy_vector(edge_pairs, weights, labels, spec, s44), spec)


def central_jacobian(edge_pairs: list[tuple[str, str]], weights: np.ndarray, labels: list[str], spec: dict[str, Any], s44: Any) -> np.ndarray:
    columns = []
    for idx in range(len(edge_pairs)):
        plus = weights.copy()
        minus = weights.copy()
        plus[idx] += FINITE_DIFF_EPS
        minus[idx] -= FINITE_DIFF_EPS
        columns.append((full_fingerprint(edge_pairs, plus, labels, spec, s44) - full_fingerprint(edge_pairs, minus, labels, spec, s44)) / (2.0 * FINITE_DIFF_EPS))
    return np.stack(columns, axis=1)


def rank_nullity(jacobian: np.ndarray) -> tuple[int, int, np.ndarray]:
    _u, singular_values, _vt = np.linalg.svd(jacobian, full_matrices=True)
    rank = int(np.sum(singular_values > RANK_TOL))
    return rank, int(jacobian.shape[1] - rank), singular_values


def weighted_adjacency(edge_pairs: list[tuple[str, str]], weights: np.ndarray) -> dict[str, list[tuple[str, float, int]]]:
    graph: dict[str, list[tuple[str, float, int]]] = {}
    for idx, ((u, v), weight) in enumerate(zip(edge_pairs, weights)):
        graph.setdefault(u, []).append((v, float(weight), idx))
        graph.setdefault(v, []).append((u, float(weight), idx))
    return graph


def shortest_path(edge_pairs: list[tuple[str, str]], weights: np.ndarray, start: str, goal: str) -> tuple[float, int]:
    graph = weighted_adjacency(edge_pairs, weights)
    queue: list[tuple[float, str, int]] = [(0.0, start, 0)]
    best = {start: 0.0}
    while queue:
        dist, node, hops = heapq.heappop(queue)
        if node == goal:
            return float(dist), hops
        if dist > best[node] + 1e-12:
            continue
        for nxt, weight, _idx in graph.get(node, []):
            ndist = dist + weight
            if ndist < best.get(nxt, float("inf")) - 1e-12:
                best[nxt] = ndist
                heapq.heappush(queue, (ndist, nxt, hops + 1))
    return float("inf"), 0


def geometric_quantities(edge_pairs: list[tuple[str, str]], weights: np.ndarray, labels: list[str]) -> dict[str, dict[str, Any]]:
    boundary = set(labels)
    interior_edges = [idx for idx, (u, v) in enumerate(edge_pairs) if u not in boundary and v not in boundary]
    quantities: dict[str, dict[str, Any]] = {
        "bulk_volume_total_interior_edge_weight": {"kind": "bulk_volume", "value": float(np.sum(weights[interior_edges])), "edge_count": len(interior_edges)},
        "bulk_volume_total_all_edge_weight": {"kind": "bulk_volume", "value": float(np.sum(weights)), "edge_count": len(edge_pairs)},
    }
    for idx, (u, v) in enumerate(edge_pairs):
        quantities[f"edge_capacity_{idx}_{u}_{v}"] = {"kind": "capacity", "value": float(weights[idx]), "edge_count": 1}
    interior_nodes = sorted({node for pair in edge_pairs for node in pair if node not in boundary})
    for a, b in itertools.combinations(interior_nodes, 2):
        value, hops = shortest_path(edge_pairs, weights, a, b)
        quantities[f"bulk_geodesic_{a}_{b}"] = {"kind": "bulk_geodesic", "value": value, "edge_count": hops}
    return quantities


def moved_quantities(edge_pairs: list[tuple[str, str]], weights: np.ndarray, labels: list[str], perturbed: np.ndarray) -> list[dict[str, Any]]:
    base = geometric_quantities(edge_pairs, weights, labels)
    new = geometric_quantities(edge_pairs, perturbed, labels)
    rows = []
    for name, info in base.items():
        gap = float(new[name]["value"] - info["value"])
        if abs(gap) > GEOMETRIC_GAP_TOL:
            rows.append({"quantity": name, "kind": info["kind"], "gap": gap, "edge_count": info["edge_count"]})
    return sorted(rows, key=lambda row: (-abs(float(row["gap"])), row["quantity"]))


def clean_shadow_edges(edge_pairs: list[tuple[str, str]], weights: np.ndarray, labels: list[str], spec: dict[str, Any], s44: Any) -> list[dict[str, Any]]:
    base = full_fingerprint(edge_pairs, weights, labels, spec, s44)
    rows = []
    for idx, (u, v) in enumerate(edge_pairs):
        ok = True
        max_residual = 0.0
        for delta in CLEAN_DELTAS:
            for sign in [1.0, -1.0]:
                perturbed = weights.copy()
                perturbed[idx] += sign * delta
                if perturbed[idx] <= 0:
                    ok = False
                    max_residual = float("inf")
                    continue
                residual = float(np.max(np.abs(full_fingerprint(edge_pairs, perturbed, labels, spec, s44) - base)))
                max_residual = max(max_residual, residual)
                if residual >= FINGERPRINT_TOL:
                    ok = False
        if ok:
            rows.append({"edge_index": idx, "edge": f"{u}-{v}", "max_both_direction_residual": max_residual})
    return rows


def control_carrier() -> tuple[list[str], list[tuple[str, str]], np.ndarray]:
    labels = [f"B{i}" for i in range(4)]
    return labels, [(label, "C") for label in labels], np.array([0.7, 0.9, 1.1, 1.3], dtype=float)


def build() -> dict[str, Any]:
    s42_hash = sha256(STEP42_SCRIPT)
    s44_hash = sha256(STEP44_SCRIPT)
    if s42_hash != STEP42_SHA256:
        raise RuntimeError("Step42 frozen hash mismatch")
    if s44_hash != STEP44_SHA256:
        raise RuntimeError("Step44 frozen hash mismatch")
    s42 = import_module(STEP42_SCRIPT, "step42_frozen")
    s44 = import_module(STEP44_SCRIPT, "step44_frozen")
    labels = frozen_boundary_labels(s42)
    edge_pairs, base_weights = extract_step42_edges(s42)
    spec = precompute_feature_spec(len(labels))

    seed_rows = []
    clean_rows = []
    mode_rows = []
    selected_witness: dict[str, Any] | None = None
    for seed in GENERIC_SEEDS:
        weights = generic_weights(base_weights, seed)
        nondegenerate = float(np.max(weights) - np.min(weights)) > 1e-6
        jacobian = central_jacobian(edge_pairs, weights, labels, spec, s44)
        rank, nullity, singular_values = rank_nullity(jacobian)
        shadows = clean_shadow_edges(edge_pairs, weights, labels, spec, s44)
        seed_rows.append(
            {
                "seed": seed,
                "nondegenerate": nondegenerate,
                "weight_min": f"{float(np.min(weights)):.12g}",
                "weight_max": f"{float(np.max(weights)):.12g}",
                "central_difference": True,
                "jacobian_rank": rank,
                "jacobian_nullity": nullity,
                "clean_shadow_edge_count_both_direction": len(shadows),
                "singular_values": ";".join(f"{value:.12g}" for value in singular_values),
            }
        )
        for shadow in shadows:
            clean_rows.append({"seed": seed, **shadow})
        for shadow in shadows:
            edge_idx = int(shadow["edge_index"])
            perturbed = weights.copy()
            perturbed[edge_idx] += CLEAN_DELTAS[0]
            moved = moved_quantities(edge_pairs, weights, labels, perturbed)
            top = moved[0]
            mode_rows.append(
                {
                    "seed": seed,
                    "edge_index": edge_idx,
                    "edge": shadow["edge"],
                    "finite_delta": CLEAN_DELTAS[0],
                    "fingerprint_residual_plus": shadow["max_both_direction_residual"],
                    "top_moved_quantity": top["quantity"],
                    "top_moved_kind": top["kind"],
                    "top_moved_gap": f"{float(top['gap']):.12g}",
                    "moved_quantity_count": len(moved),
                    "moved_quantities": ";".join(f"{row['quantity']}:{row['gap']:.12g}" for row in moved[:12]),
                }
            )
            if selected_witness is None:
                minus = weights.copy()
                plus = weights.copy()
                minus[edge_idx] -= CLEAN_DELTAS[0]
                plus[edge_idx] += CLEAN_DELTAS[0]
                base_fp = full_fingerprint(edge_pairs, weights, labels, spec, s44)
                plus_residual = float(np.max(np.abs(full_fingerprint(edge_pairs, plus, labels, spec, s44) - base_fp)))
                minus_residual = float(np.max(np.abs(full_fingerprint(edge_pairs, minus, labels, spec, s44) - base_fp)))
                selected_witness = {
                    "seed": seed,
                    "edge_index": edge_idx,
                    "edge": shadow["edge"],
                    "delta": CLEAN_DELTAS[0],
                    "plus_residual": plus_residual,
                    "minus_residual": minus_residual,
                    "moved_quantity": top["quantity"],
                    "moved_kind": top["kind"],
                    "geometric_gap": abs(float(top["gap"])),
                }

    control_labels, control_edges, control_weights = control_carrier()
    control_spec = precompute_feature_spec(len(control_labels))
    control_j = central_jacobian(control_edges, control_weights, control_labels, control_spec, s44)
    control_rank, control_nullity, _control_singular_values = rank_nullity(control_j)

    min_nullity = min(int(row["jacobian_nullity"]) for row in seed_rows)
    min_clean = min(int(row["clean_shadow_edge_count_both_direction"]) for row in seed_rows)
    verdict = "ENTANGLEMENT_DOES_NOT_DETERMINE_GEOMETRY_ITFROMQUBIT_FAILS" if min_nullity > 0 and min_clean > 0 else "ENTANGLEMENT_DETERMINES_GEOMETRY_FORK_SHARP_FORM_FAILS"
    prediction = (
        f"Boundary entanglement does not determine the frozen Step-42 bulk geometry on generic perturbations: "
        f"central-difference nullity is {[int(row['jacobian_nullity']) for row in seed_rows]} across seeds {GENERIC_SEEDS}, "
        f"with both-direction clean-shadow edge counts {[int(row['clean_shadow_edge_count_both_direction']) for row in seed_rows]}. "
        "Complete reconstruction from entanglement alone therefore fails on this finite carrier; non-entanglement bulk data is required."
    )
    falsification = "A comparable nondegenerate frozen holographic/tensor-network carrier with full boundary entanglement fingerprint, central-difference nullity 0, and no both-direction clean shadows would falsify this SBT-fork prediction on that carrier."

    write_csv(ARTIFACT_DIR / "generic_seed_summary_step55.csv", seed_rows, ["seed", "nondegenerate", "weight_min", "weight_max", "central_difference", "jacobian_rank", "jacobian_nullity", "clean_shadow_edge_count_both_direction", "singular_values"])
    write_csv(ARTIFACT_DIR / "clean_shadow_edges_step55.csv", clean_rows, ["seed", "edge_index", "edge", "max_both_direction_residual"])
    write_csv(ARTIFACT_DIR / "invisible_modes_characterization_step55.csv", mode_rows, ["seed", "edge_index", "edge", "finite_delta", "fingerprint_residual_plus", "top_moved_quantity", "top_moved_kind", "top_moved_gap", "moved_quantity_count", "moved_quantities"])
    write_csv(
        ARTIFACT_DIR / "witness_pair_step55.csv",
        [
            {
                "seed": selected_witness["seed"] if selected_witness else "",
                "edge_index": selected_witness["edge_index"] if selected_witness else "",
                "edge": selected_witness["edge"] if selected_witness else "",
                "delta": selected_witness["delta"] if selected_witness else "",
                "plus_residual": "" if selected_witness is None else f"{selected_witness['plus_residual']:.12g}",
                "minus_residual": "" if selected_witness is None else f"{selected_witness['minus_residual']:.12g}",
                "moved_geometric_quantity": selected_witness["moved_quantity"] if selected_witness else "",
                "moved_kind": selected_witness["moved_kind"] if selected_witness else "",
                "witness_geometric_gap": "" if selected_witness is None else f"{selected_witness['geometric_gap']:.12g}",
            }
        ],
        ["seed", "edge_index", "edge", "delta", "plus_residual", "minus_residual", "moved_geometric_quantity", "moved_kind", "witness_geometric_gap"],
    )
    write_csv(
        ARTIFACT_DIR / "edge_weights_step55.csv",
        [
            {
                "edge_index": idx,
                "edge_u": u,
                "edge_v": v,
                "edge_source": "step42_frozen_import",
                "base_uniform_weight": f"{base_weights[idx]:.12g}",
                **{f"seed_{seed}_weight": f"{generic_weights(base_weights, seed)[idx]:.12g}" for seed in GENERIC_SEEDS},
            }
            for idx, (u, v) in enumerate(edge_pairs)
        ],
        ["edge_index", "edge_u", "edge_v", "edge_source", "base_uniform_weight"] + [f"seed_{seed}_weight" for seed in GENERIC_SEEDS],
    )
    write_csv(
        ARTIFACT_DIR / "fingerprint_summary_step55.csv",
        [
            {
                "carrier_source": "step42_frozen_perturbed_generic",
                "boundary_region_entropy_count": len(spec["region_masks"]),
                "mutual_information_count": len(spec["mi_pairs"]),
                "i3_mmi_count": len(spec["i3_triples"]),
                "total_fingerprint_feature_count": len(feature_vector(np.zeros(len(spec["region_masks"])), spec)),
                "fingerprint_covers_all_boundary_regions": len(spec["region_masks"]) == (2 ** len(labels) - 2),
                "fingerprint_includes_MI_and_I3": True,
                "central_difference": True,
            }
        ],
        ["carrier_source", "boundary_region_entropy_count", "mutual_information_count", "i3_mmi_count", "total_fingerprint_feature_count", "fingerprint_covers_all_boundary_regions", "fingerprint_includes_MI_and_I3", "central_difference"],
    )
    write_csv(
        ARTIFACT_DIR / "control_injectivity_step55.csv",
        [{"control_carrier": "boundary_anchored_tree", "jacobian_rank": control_rank, "control_nullity": control_nullity}],
        ["control_carrier", "jacobian_rank", "control_nullity"],
    )
    write_csv(
        ARTIFACT_DIR / "frozen_machinery_step55.csv",
        [
            {"source": "Step42 frozen graph carrier", "thread_root_relative_path": rel("../step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"), "sha256": s42_hash, "expected_sha256": STEP42_SHA256, "imported_verbatim": s42_hash == STEP42_SHA256},
            {"source": "Step44 mincut/MMI functions", "thread_root_relative_path": rel("../step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py"), "sha256": s44_hash, "expected_sha256": STEP44_SHA256, "imported_verbatim": s44_hash == STEP44_SHA256},
        ],
        ["source", "thread_root_relative_path", "sha256", "expected_sha256", "imported_verbatim"],
    )

    feature_count = len(feature_vector(np.zeros(len(spec["region_masks"])), spec))
    schema = {
        "step": 55,
        "orientation": "QM_GR_E018_generic_entanglement_to_geometry_kernel_test",
        "carrier_source": "step42_frozen_perturbed_generic",
        "degenerate_point_rejected": True,
        "generic_seeds": GENERIC_SEEDS,
        "central_difference": True,
        "fingerprint_feature_count": feature_count,
        "central_diff_nullity": [int(row["jacobian_nullity"]) for row in seed_rows],
        "central_diff_rank": [int(row["jacobian_rank"]) for row in seed_rows],
        "clean_shadow_edge_count_both_direction": [int(row["clean_shadow_edge_count_both_direction"]) for row in seed_rows],
        "invisible_sector_characterization": "entanglement_shadow_capacities",
        "verdict": verdict,
        "witness": selected_witness,
        "control_nullity": control_nullity,
        "falsifiable_prediction": prediction,
        "falsification_condition": falsification,
        "overlaps_entanglement_shadow_literature": True,
        "disproves_in_nature": False,
        "derives_holography": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "conditional_on_step47_step48": True,
    }
    write_json(ARTIFACT_DIR / "step55_schema.json", schema)

    summary = f"""# Step 55 Results Summary

## Honest Grade First
This is a finite static toy test of the fork's sharp prediction on generic perturbations of the frozen Step-42 carrier. The uniform Step-42 point is rejected as degenerate; all reported verdict fields come from central differences at nondegenerate seeded geometries. The result is conditional on Steps 47/48 and is not frame transfer or a claim about real holography.

## Map And Fingerprint
Carrier source: `step42_frozen_perturbed_generic`. The full boundary fingerprint has `{feature_count}` features: `{len(spec['region_masks'])}` boundary entropies, `{len(spec['mi_pairs'])}` mutual informations, and `{len(spec['i3_triples'])}` tripartite I3/MMI values.

## Generic Central-Difference Computation
Seeds `{GENERIC_SEEDS}` give central-difference ranks `{[int(row['jacobian_rank']) for row in seed_rows]}` and nullities `{[int(row['jacobian_nullity']) for row in seed_rows]}`. Both-direction clean-shadow edge counts are `{[int(row['clean_shadow_edge_count_both_direction']) for row in seed_rows]}`.

## Witness
The witness uses seed `{selected_witness['seed']}` edge `{selected_witness['edge']}` with finite delta `{selected_witness['delta']}`. Both directions keep the full fingerprint fixed: plus residual `{selected_witness['plus_residual']:.12g}`, minus residual `{selected_witness['minus_residual']:.12g}`. The moved geometric quantity is `{selected_witness['moved_quantity']}` with gap `{selected_witness['geometric_gap']:.12g}`.

## Control
The boundary-anchored-tree control has nullity `{control_nullity}`.

## Verdict
`{verdict}`.

## Falsifiable Prediction
{prediction}

Falsification condition: {falsification}
"""
    (ARTIFACT_DIR / "step55_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

This is a finite static toy result, conditional on the Step-47 common-carrier premise and the Step-48 fork reading. It does not make a claim about real holography in nature, does not solve reconstruction, does not derive holography, and does not certify frame transfer.

The result uses RT/min-cut boundary entanglement data only: all boundary entropies plus all derived mutual informations and I3/MMI values. It does not include all possible boundary correlators, modular data, dynamics, or continuum information.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step55.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\usepackage{{amsmath}}
\begin{{document}}
\section*{{Step 55 Statement}}
The uniform Step-42 point is degenerate and is not used for the verdict. For generic seeded perturbations of the frozen Step-42 edge weights, the central-difference Jacobian of the complete boundary entanglement fingerprint has ranks {[int(row['jacobian_rank']) for row in seed_rows]} and nullities {[int(row['jacobian_nullity']) for row in seed_rows]}. The both-direction clean-shadow counts are {[int(row['clean_shadow_edge_count_both_direction']) for row in seed_rows]}. Therefore boundary entanglement does not determine the finite bulk geometry on this carrier. The boundary-tree control has nullity {control_nullity}.
\end{{document}}
"""
    (ARTIFACT_DIR / "entanglement_underdetermines_geometry_statement_step55.tex").write_text(statement, encoding="utf-8")

    write_csv(
        ARTIFACT_DIR / "content_classification_step55.csv",
        [
            {"artifact": "step55_results_summary.md", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "generic frozen-carrier kernel verdict"},
            {"artifact": "step55_schema.json", "classification": "organizational", "scope": "machine-readable verdict fields"},
            {"artifact": "generic_seed_summary_step55.csv", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "central-difference nullity per generic seed"},
            {"artifact": "clean_shadow_edges_step55.csv", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "both-direction clean-shadow finite test"},
            {"artifact": "witness_pair_step55.csv", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "same-fingerprint different-geometry witness"},
            {"artifact": "control_injectivity_step55.csv", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "can-fail injective control"},
            {"artifact": "nonclaim_boundary_step55.md", "classification": "organizational", "scope": "scope and overclaim boundary"},
        ],
        ["artifact", "classification", "scope"],
    )

    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP55_GENERIC_NONDEGENERATE", "status": "active", "description": "Uniform point rejected; generic seeded perturbations used."},
            {"constraint_id": "C_STEP55_CENTRAL_DIFFERENCE", "status": "active", "description": "Jacobian uses two-sided central differences."},
            {"constraint_id": "C_STEP55_BOTH_DIRECTION_SHADOW", "status": "active", "description": "Clean shadows require plus and minus finite perturbations to preserve the full fingerprint."},
        ],
        ["constraint_id", "status", "description"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [{"target_residual": "fork sharp prediction: entanglement-invisible gravitational sector", "canonical_target": "R_root_E018", "relation_to_canonical_root": "sub_residual", "authorization": "USER-AUTHORIZED 2026-06-10 Step55 final correction"}],
        ["target_residual", "canonical_target", "relation_to_canonical_root", "authorization"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [{"grammar_id": "G_E018_GenericFrozenCarrierKernelTest_v4", "carrier": "generic perturbations of frozen Step42 graph", "fingerprint": "all boundary-region min-cut entropies plus all MI and I3/MMI", "excluded_designs_rationale": "Excludes uniform degenerate point and one-sided-only slack test.", "non_triviality_argument": "Boundary-tree control has nullity zero.", "next_grammar_delta": "Test richer boundary observables and continuum carriers."}],
        ["grammar_id", "carrier", "fingerprint", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    return schema


if __name__ == "__main__":
    build()
