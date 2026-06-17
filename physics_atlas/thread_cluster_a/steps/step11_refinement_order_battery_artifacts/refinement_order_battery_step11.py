#!/usr/bin/env python3
"""Cluster A Step 11: refinement-order battery on Step 8 survivor carrier."""

from __future__ import annotations

import csv
import json
import math
import random
from collections import Counter
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP8_DIR = THREAD_DIR / "steps" / "step8_structural_token_blind_selection_artifacts"

FACETS = ["gauge_code", "rep_code", "n_gen", "texture_code", "ew_code", "uv_code", "vacuum_code"]
CANONICAL_ORDER = ["gauge_code", "rep_code", "n_gen", "texture_code", "ew_code", "uv_code", "vacuum_code"]
PARTIAL_DEPTH = 4
SIGNIFICANCE_THRESHOLD = 0.25
SHARP_RANK_SIGMA = 0.55
RANDOM_ORDER_COUNT = 200
RANDOM_SEED = 20260606


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


def select_structural_point(rows: list[dict[str, str]]) -> dict[str, str]:
    return sorted(
        rows,
        key=lambda row: (
            -float(row["structural_score"]),
            int(row["structural_rank"]),
            row["candidate_id"],
        ),
    )[0]


def revealed_facets(order: list[str]) -> list[str]:
    return order[:PARTIAL_DEPTH]


def cylinder(rows: list[dict[str, str]], selected: dict[str, str], order: list[str]) -> list[dict[str, str]]:
    facets = revealed_facets(order)
    return [row for row in rows if all(row[facet] == selected[facet] for facet in facets)]


def sharp_weight(row: dict[str, str], selected: dict[str, str]) -> float:
    rank_gap = int(row["structural_rank"]) - int(selected["structural_rank"])
    return math.exp(-(rank_gap**2) / (2.0 * SHARP_RANK_SIGMA**2))


def significant_count_from_weights(weights: list[float]) -> int:
    if not weights:
        return 0
    max_weight = max(weights)
    return sum(1 for weight in weights if weight >= SIGNIFICANCE_THRESHOLD * max_weight)


def evaluate_order(rows: list[dict[str, str]], selected: dict[str, str], order: list[str]) -> dict[str, object]:
    support = cylinder(rows, selected, order)
    genuine_weights = [sharp_weight(row, selected) for row in support]
    genuine_final = significant_count_from_weights(genuine_weights)
    landscape_final = len(support)
    return {
        "revealed_facets": "+".join(revealed_facets(order)),
        "genuine_final_degeneracy": genuine_final,
        "genuine_collapses": genuine_final == 1,
        "landscape_final_degeneracy": landscape_final,
        "landscape_collapses": landscape_final == 1,
        "landscape_support_ids": ";".join(row["candidate_id"] for row in support[:12]),
    }


def greedy_order(
    rows: list[dict[str, str]],
    selected: dict[str, str],
    objective: str,
) -> list[str]:
    prefix: list[str] = []
    remaining = list(FACETS)
    while len(prefix) < PARTIAL_DEPTH:
        candidates = []
        for facet in remaining:
            trial_prefix = prefix + [facet]
            trial_order = trial_prefix + [candidate for candidate in FACETS if candidate not in trial_prefix]
            evaluated = evaluate_order(rows, selected, trial_order)
            if objective == "delay_genuine":
                score = (int(evaluated["genuine_final_degeneracy"]), int(evaluated["landscape_final_degeneracy"]))
            elif objective == "force_landscape":
                score = (-int(evaluated["landscape_final_degeneracy"]), -int(evaluated["genuine_final_degeneracy"]))
            else:
                raise ValueError(f"unknown objective {objective}")
            candidates.append((score, facet))
        _, chosen = max(candidates, key=lambda item: (item[0], item[1]))
        prefix.append(chosen)
        remaining.remove(chosen)
    return prefix + [facet for facet in FACETS if facet not in prefix]


def random_orders() -> list[list[str]]:
    rng = random.Random(RANDOM_SEED)
    orders = []
    for _ in range(RANDOM_ORDER_COUNT):
        order = list(FACETS)
        rng.shuffle(order)
        orders.append(order)
    return orders


def histogram(values: list[int]) -> str:
    counts = Counter(values)
    return ";".join(f"{key}:{counts[key]}" for key in sorted(counts))


def distribution_rows(order_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    random_rows = [row for row in order_rows if row["order_type"] == "random"]
    genuine_values = [int(row["genuine_final_degeneracy"]) for row in random_rows]
    landscape_values = [int(row["landscape_final_degeneracy"]) for row in random_rows]
    return [
        {
            "case": "genuine_selection",
            "random_order_count": len(random_rows),
            "collapse_count": sum(1 for value in genuine_values if value == 1),
            "collapse_fraction": f"{sum(1 for value in genuine_values if value == 1) / len(random_rows):.12f}",
            "noncollapse_count": sum(1 for value in genuine_values if value > 1),
            "noncollapse_fraction": f"{sum(1 for value in genuine_values if value > 1) / len(random_rows):.12f}",
            "min_final_degeneracy": min(genuine_values),
            "max_final_degeneracy": max(genuine_values),
            "histogram": histogram(genuine_values),
        },
        {
            "case": "landscape_measure",
            "random_order_count": len(random_rows),
            "collapse_count": sum(1 for value in landscape_values if value == 1),
            "collapse_fraction": f"{sum(1 for value in landscape_values if value == 1) / len(random_rows):.12f}",
            "noncollapse_count": sum(1 for value in landscape_values if value > 1),
            "noncollapse_fraction": f"{sum(1 for value in landscape_values if value > 1) / len(random_rows):.12f}",
            "min_final_degeneracy": min(landscape_values),
            "max_final_degeneracy": max(landscape_values),
            "histogram": histogram(landscape_values),
        },
    ]


def main() -> None:
    rows = read_csv(STEP8_DIR / "structural_survivors_step8.csv")
    selected = select_structural_point(rows)

    order_specs: list[tuple[str, str, list[str]]] = [
        ("canonical", "canonical", CANONICAL_ORDER),
        ("reverse", "reverse", list(reversed(CANONICAL_ORDER))),
        ("adversarial_delay_genuine", "adversarial", greedy_order(rows, selected, "delay_genuine")),
        ("adversarial_force_landscape", "adversarial", greedy_order(rows, selected, "force_landscape")),
    ]
    for idx, order in enumerate(random_orders()):
        order_specs.append((f"random_{idx:03d}", "random", order))

    order_rows: list[dict[str, object]] = []
    for order_id, order_type, order in order_specs:
        evaluated = evaluate_order(rows, selected, order)
        order_rows.append(
            {
                "order_id": order_id,
                "order_type": order_type,
                "order": "+".join(order),
                "partial_depth": PARTIAL_DEPTH,
                "selected_candidate_id": selected["candidate_id"],
                "selected_structural_rank": selected["structural_rank"],
                "selected_structural_score": selected["structural_score"],
                **evaluated,
            }
        )

    distribution = distribution_rows(order_rows)
    adversarial_rows = [row for row in order_rows if row["order_type"] == "adversarial"]
    genuine_values = [int(row["genuine_final_degeneracy"]) for row in order_rows]
    landscape_values = [int(row["landscape_final_degeneracy"]) for row in order_rows]
    random_distribution = {row["case"]: row for row in distribution}
    separation = min(landscape_values) - max(genuine_values)
    flip_rows = [
        row
        for row in order_rows
        if int(row["genuine_final_degeneracy"]) != 1 or int(row["landscape_final_degeneracy"]) == 1
    ]
    separation_rows = [
        {
            "all_order_count": len(order_rows),
            "random_order_count": RANDOM_ORDER_COUNT,
            "min_genuine_final_degeneracy": min(genuine_values),
            "max_genuine_final_degeneracy": max(genuine_values),
            "min_landscape_final_degeneracy": min(landscape_values),
            "max_landscape_final_degeneracy": max(landscape_values),
            "separation_margin": separation,
            "flipping_order_count": len(flip_rows),
            "verdict": "order_invariant_separation" if separation > 0 and not flip_rows else "order_scope_boundary_found",
        }
    ]

    write_csv(
        ARTIFACT_DIR / "order_results_step11.csv",
        order_rows,
        [
            "order_id",
            "order_type",
            "order",
            "partial_depth",
            "selected_candidate_id",
            "selected_structural_rank",
            "selected_structural_score",
            "revealed_facets",
            "genuine_final_degeneracy",
            "genuine_collapses",
            "landscape_final_degeneracy",
            "landscape_collapses",
            "landscape_support_ids",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "random_order_distribution_step11.csv",
        distribution,
        [
            "case",
            "random_order_count",
            "collapse_count",
            "collapse_fraction",
            "noncollapse_count",
            "noncollapse_fraction",
            "min_final_degeneracy",
            "max_final_degeneracy",
            "histogram",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "adversarial_orders_step11.csv",
        adversarial_rows,
        [
            "order_id",
            "order_type",
            "order",
            "partial_depth",
            "selected_candidate_id",
            "selected_structural_rank",
            "selected_structural_score",
            "revealed_facets",
            "genuine_final_degeneracy",
            "genuine_collapses",
            "landscape_final_degeneracy",
            "landscape_collapses",
            "landscape_support_ids",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "separation_step11.csv",
        separation_rows,
        [
            "all_order_count",
            "random_order_count",
            "min_genuine_final_degeneracy",
            "max_genuine_final_degeneracy",
            "min_landscape_final_degeneracy",
            "max_landscape_final_degeneracy",
            "separation_margin",
            "flipping_order_count",
            "verdict",
        ],
    )

    output = {
        "step": 11,
        "artifact_type": "refinement_order_battery",
        "source_step": "steps/step8_structural_token_blind_selection_artifacts/structural_survivors_step8.csv",
        "parameters": {
            "facets": FACETS,
            "partial_depth": PARTIAL_DEPTH,
            "significance_threshold": SIGNIFICANCE_THRESHOLD,
            "sharp_rank_sigma": SHARP_RANK_SIGMA,
            "random_order_count": RANDOM_ORDER_COUNT,
            "random_seed": RANDOM_SEED,
        },
        "selected_point": {
            "candidate_id": selected["candidate_id"],
            "structural_rank": int(selected["structural_rank"]),
            "structural_score": float(selected["structural_score"]),
            "selection_rule": "max structural_score, then structural_rank, then candidate_id",
        },
        "verdict": {
            "type": "refinement_order_battery_constructed",
            "genuine_random_collapse_fraction": float(random_distribution["genuine_selection"]["collapse_fraction"]),
            "landscape_random_noncollapse_fraction": float(random_distribution["landscape_measure"]["noncollapse_fraction"]),
            "min_landscape_final_degeneracy": min(landscape_values),
            "max_genuine_final_degeneracy": max(genuine_values),
            "separation_margin": separation,
            "flipping_order_count": len(flip_rows),
            "adversarial_order_count": len(adversarial_rows),
            "order_invariant_on_declared_battery": separation > 0 and not flip_rows,
            "finite_grammar_only": True,
        },
        "nonclaim": "Finite token-blind order battery only; no physical value or physical mechanism is determined.",
    }
    (ARTIFACT_DIR / "refinement_order_battery_output_step11.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
