#!/usr/bin/env python3
"""Cluster A Step 9: facet factorization test on Step 8 survivors."""

from __future__ import annotations

import csv
import itertools
import json
import math
import random
from collections import Counter
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP8_DIR = THREAD_DIR / "steps" / "step8_structural_token_blind_selection_artifacts"
FACETS = ["gauge_code", "rep_code", "n_gen", "texture_code", "ew_code", "uv_code", "vacuum_code"]
MI_EDGE_THRESHOLD_BITS = 0.01
SUBSAMPLE_SEED = 20260606
SUBSAMPLE_FRACTION = 0.8


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def entropy_bits(records: list[dict[str, str]], columns: list[str]) -> float:
    if not records:
        return 0.0
    counts = Counter(tuple(row[column] for column in columns) for row in records)
    n = len(records)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def total_correlation_bits(records: list[dict[str, str]]) -> tuple[float, float, float]:
    marginal_sum = sum(entropy_bits(records, [facet]) for facet in FACETS)
    joint = entropy_bits(records, FACETS)
    return marginal_sum - joint, marginal_sum, joint


def mutual_information_bits(records: list[dict[str, str]], left: str, right: str) -> float:
    return entropy_bits(records, [left]) + entropy_bits(records, [right]) - entropy_bits(records, [left, right])


def pairwise_matrix_rows(variation: str, records: list[dict[str, str]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for left in FACETS:
        for right in FACETS:
            value = entropy_bits(records, [left]) if left == right else mutual_information_bits(records, left, right)
            rows.append(
                {
                    "variation": variation,
                    "left_facet": left,
                    "right_facet": right,
                    "mi_bits": f"{value:.12f}",
                    "edge_above_threshold": left != right and value > MI_EDGE_THRESHOLD_BITS,
                }
            )
    return rows


def graph_components(records: list[dict[str, str]]) -> tuple[list[tuple[str, str, float]], list[list[str]]]:
    edges = []
    adjacency = {facet: set() for facet in FACETS}
    for left, right in itertools.combinations(FACETS, 2):
        value = mutual_information_bits(records, left, right)
        if value > MI_EDGE_THRESHOLD_BITS:
            edges.append((left, right, value))
            adjacency[left].add(right)
            adjacency[right].add(left)

    unvisited = set(FACETS)
    components: list[list[str]] = []
    while unvisited:
        start = sorted(unvisited)[0]
        unvisited.remove(start)
        stack = [start]
        component = {start}
        while stack:
            current = stack.pop()
            for neighbor in sorted(adjacency[current]):
                if neighbor in unvisited:
                    unvisited.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        components.append(sorted(component))
    components.sort(key=lambda comp: (-len(comp), comp))
    return edges, components


def block_residual_bits(records: list[dict[str, str]], blocks: list[list[str]]) -> float:
    return sum(entropy_bits(records, block) for block in blocks) - entropy_bits(records, FACETS)


def compact_block(blocks: list[list[str]]) -> str:
    return " / ".join("+".join(block) for block in blocks)


def variation_rows(name: str, records: list[dict[str, str]]) -> tuple[
    list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]
]:
    total_c, marginal_sum, joint = total_correlation_bits(records)
    if abs(total_c) < 1e-10:
        total_c = 0.0
    edges, components = graph_components(records)
    residual = block_residual_bits(records, components)
    if abs(residual) < 1e-10:
        residual = 0.0
    within = total_c - residual
    verdict = (
        "independent_neutral_control"
        if total_c == 0.0
        else "coupled_single_component"
        if len(components) == 1
        else "block_structured_coupling"
    )

    tc_rows = [
        {
            "variation": name,
            "population_size": len(records),
            "sum_marginal_entropy_bits": f"{marginal_sum:.12f}",
            "joint_entropy_bits": f"{joint:.12f}",
            "total_correlation_bits": f"{total_c:.12f}",
            "max_possible_sumH_bits": f"{marginal_sum:.12f}",
            "threshold_bits": MI_EDGE_THRESHOLD_BITS,
            "verdict": verdict,
        }
    ]
    graph_rows = [
        {
            "variation": name,
            "edge": f"{left}--{right}",
            "left_facet": left,
            "right_facet": right,
            "mi_bits": f"{value:.12f}",
            "threshold_bits": MI_EDGE_THRESHOLD_BITS,
        }
        for left, right, value in edges
    ]
    component_rows = [
        {
            "variation": name,
            "component_id": idx + 1,
            "component_size": len(component),
            "facets": "+".join(component),
        }
        for idx, component in enumerate(components)
    ]
    block_rows = [
        {
            "variation": name,
            "block_partition": compact_block(components),
            "component_count": len(components),
            "total_correlation_bits": f"{total_c:.12f}",
            "within_block_correlation_bits": f"{within:.12f}",
            "inter_block_residual_bits": f"{residual:.12f}",
            "separability_verdict": verdict,
        }
    ]
    return tc_rows, graph_rows, component_rows, block_rows


def deterministic_subsample(records: list[dict[str, str]]) -> list[dict[str, str]]:
    rng = random.Random(SUBSAMPLE_SEED)
    indices = list(range(len(records)))
    rng.shuffle(indices)
    keep = set(indices[: round(SUBSAMPLE_FRACTION * len(records))])
    return [record for idx, record in enumerate(records) if idx in keep]


def main() -> None:
    neutral = read_csv(STEP8_DIR / "neutral_candidate_space_step8.csv")
    survivors = read_csv(STEP8_DIR / "structural_survivors_step8.csv")
    strict = [row for row in survivors if int(row["naturalness_cost"]) <= 1]
    subsample = deterministic_subsample(survivors)

    variations = {
        "neutral_product": neutral,
        "structural_survivors": survivors,
        "strict_naturalness_le_1": strict,
        "subsample_80_seed_20260606": subsample,
    }

    tc_rows: list[dict[str, object]] = []
    matrix_rows: list[dict[str, object]] = []
    graph_rows: list[dict[str, object]] = []
    component_rows: list[dict[str, object]] = []
    block_rows: list[dict[str, object]] = []
    robustness_rows: list[dict[str, object]] = []

    for name, records in variations.items():
        tc_part, graph_part, comp_part, block_part = variation_rows(name, records)
        tc_rows.extend(tc_part)
        matrix_rows.extend(pairwise_matrix_rows(name, records))
        graph_rows.extend(graph_part)
        component_rows.extend(comp_part)
        block_rows.extend(block_part)
        robustness_rows.append(
            {
                "variation": name,
                "population_size": len(records),
                "total_correlation_bits": tc_part[0]["total_correlation_bits"],
                "component_count": block_part[0]["component_count"],
                "block_partition": block_part[0]["block_partition"],
                "inter_block_residual_bits": block_part[0]["inter_block_residual_bits"],
                "separability_verdict": block_part[0]["separability_verdict"],
                "seed": SUBSAMPLE_SEED if name.startswith("subsample") else "",
            }
        )

    write_csv(
        ARTIFACT_DIR / "total_correlation_step9.csv",
        tc_rows,
        [
            "variation",
            "population_size",
            "sum_marginal_entropy_bits",
            "joint_entropy_bits",
            "total_correlation_bits",
            "max_possible_sumH_bits",
            "threshold_bits",
            "verdict",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "pairwise_mi_matrix_step9.csv",
        matrix_rows,
        ["variation", "left_facet", "right_facet", "mi_bits", "edge_above_threshold"],
    )
    write_csv(
        ARTIFACT_DIR / "coupling_graph_step9.csv",
        graph_rows,
        ["variation", "edge", "left_facet", "right_facet", "mi_bits", "threshold_bits"],
    )
    write_csv(
        ARTIFACT_DIR / "components_step9.csv",
        component_rows,
        ["variation", "component_id", "component_size", "facets"],
    )
    write_csv(
        ARTIFACT_DIR / "block_decomposition_step9.csv",
        block_rows,
        [
            "variation",
            "block_partition",
            "component_count",
            "total_correlation_bits",
            "within_block_correlation_bits",
            "inter_block_residual_bits",
            "separability_verdict",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "robustness_step9.csv",
        robustness_rows,
        [
            "variation",
            "population_size",
            "total_correlation_bits",
            "component_count",
            "block_partition",
            "inter_block_residual_bits",
            "separability_verdict",
            "seed",
        ],
    )

    main_block = next(row for row in block_rows if row["variation"] == "structural_survivors")
    neutral_tc = next(row for row in tc_rows if row["variation"] == "neutral_product")
    survivor_tc = next(row for row in tc_rows if row["variation"] == "structural_survivors")
    output = {
        "step": 9,
        "verdict": {
            "type": "facet_factorization_test_constructed",
            "threshold_bits": MI_EDGE_THRESHOLD_BITS,
            "neutral_total_correlation_bits": float(neutral_tc["total_correlation_bits"]),
            "survivor_total_correlation_bits": float(survivor_tc["total_correlation_bits"]),
            "survivor_sum_marginal_entropy_bits": float(survivor_tc["sum_marginal_entropy_bits"]),
            "component_count": int(main_block["component_count"]),
            "block_partition": main_block["block_partition"],
            "inter_block_residual_bits": float(main_block["inter_block_residual_bits"]),
            "separability_verdict": main_block["separability_verdict"],
            "subsample_seed": SUBSAMPLE_SEED,
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "nonclaim": "Finite survivor-set information geometry only; no physical layer count or SM value is derived.",
    }
    (ARTIFACT_DIR / "facet_factorization_output_step9.json").write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
