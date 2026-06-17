#!/usr/bin/env python3
"""Cluster A Step 10: robustness sweep for E043 collapse adjudication."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP6_DIR = THREAD_DIR / "steps" / "step6_e043_horn_adjudication_artifacts"

R_SM = 1.0e-4
STEP6_GRID = [1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 2.0e-2]
THRESHOLDS = [0.02, 0.05, 0.10, 0.15, 0.20, 0.25, 0.35, 0.50, 0.65, 0.80]
BROAD_FINAL_SIGMAS = [1.00, 1.25, 1.50, 2.00, 2.50, 3.00, 4.00]
SHARP_FINAL_SIGMAS = [0.02, 0.05, 0.10, 0.20, 0.40, 0.60, 0.80, 1.00]
GRID_SIZES = [6, 12, 24, 48]
GRID_HIGHS = [2.0e-2, 1.0e-1]
BROAD_SCHEDULE_LEVELS = 6
SHARP_SCHEDULE_LEVELS = 5
STEP6_OPERATING_POINT = {
    "threshold": 0.25,
    "broad_final_sigma": 2.00,
    "sharp_final_sigma": 0.10,
    "grid_config": "step6_exact",
}


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def log_grid(size: int, high: float) -> list[float]:
    if size < 2:
        return [R_SM]
    return [R_SM * ((high / R_SM) ** (idx / (size - 1))) for idx in range(size)]


def linear_grid(size: int, high: float) -> list[float]:
    if size < 2:
        return [R_SM]
    return [R_SM + (high - R_SM) * idx / (size - 1) for idx in range(size)]


def grid_configs() -> list[dict[str, object]]:
    configs: list[dict[str, object]] = [
        {
            "grid_config": "step6_exact",
            "grid_size": 6,
            "spacing": "step6_declared",
            "range_high": 2.0e-2,
            "grid": STEP6_GRID,
        }
    ]
    for size in GRID_SIZES:
        for spacing in ["log", "linear"]:
            for high in GRID_HIGHS:
                grid = log_grid(size, high) if spacing == "log" else linear_grid(size, high)
                configs.append(
                    {
                        "grid_config": f"{spacing}_{size}_high_{high:.0e}",
                        "grid_size": size,
                        "spacing": spacing,
                        "range_high": high,
                        "grid": grid,
                    }
                )
    return configs


def schedule(start: float, final: float, levels: int) -> list[float]:
    if levels == 1:
        return [final]
    return [start + (final - start) * idx / (levels - 1) for idx in range(levels)]


def broad_schedule(final_sigma: float) -> list[float]:
    return schedule(max(3.0, final_sigma), final_sigma, BROAD_SCHEDULE_LEVELS)


def sharp_schedule(final_sigma: float) -> list[float]:
    if abs(final_sigma - 0.10) < 1e-12:
        return [0.8, 0.5, 0.3, 0.2, 0.1]
    return schedule(max(0.8, final_sigma), final_sigma, SHARP_SCHEDULE_LEVELS)


def weights_for_grid(grid: list[float], target: float, sigma: float) -> list[float]:
    weights = []
    for value in grid:
        distance = math.log10(value / target)
        weights.append(math.exp(-(distance**2) / (2.0 * sigma**2)))
    return weights


def significant_values(grid: list[float], target: float, sigma: float, threshold: float) -> list[float]:
    weights = weights_for_grid(grid, target, sigma)
    max_weight = max(weights)
    return [grid[idx] for idx, weight in enumerate(weights) if weight >= threshold * max_weight]


def degeneracy_sequence(grid: list[float], sigmas: list[float], threshold: float) -> list[int]:
    return [len(significant_values(grid, R_SM, sigma, threshold)) for sigma in sigmas]


def monotone_nonincreasing(values: list[int]) -> bool:
    return all(values[idx + 1] <= values[idx] for idx in range(len(values) - 1))


def classify_cell(
    grid: list[float], threshold: float, broad_final_sigma: float, sharp_final_sigma: float
) -> dict[str, object]:
    broad_seq = degeneracy_sequence(grid, broad_schedule(broad_final_sigma), threshold)
    sharp_seq = degeneracy_sequence(grid, sharp_schedule(sharp_final_sigma), threshold)
    broad_final = broad_seq[-1]
    sharp_final = sharp_seq[-1]
    broad_collapses = broad_final == 1
    sharp_collapses = sharp_final == 1
    holds = (not broad_collapses) and sharp_collapses
    if holds:
        flip_kind = "none"
        cell_class = "VERDICT_HOLDS"
    elif broad_collapses and sharp_collapses:
        flip_kind = "broad_false_collapse"
        cell_class = "FLIP"
    elif (not broad_collapses) and (not sharp_collapses):
        flip_kind = "sharp_noncollapse"
        cell_class = "FLIP"
    else:
        flip_kind = "both_fail"
        cell_class = "FLIP"
    return {
        "broad_sequence": "->".join(str(value) for value in broad_seq),
        "sharp_sequence": "->".join(str(value) for value in sharp_seq),
        "broad_final_degeneracy": broad_final,
        "sharp_final_degeneracy": sharp_final,
        "broad_monotone": monotone_nonincreasing(broad_seq),
        "sharp_monotone": monotone_nonincreasing(sharp_seq),
        "broad_collapses": broad_collapses,
        "sharp_collapses": sharp_collapses,
        "cell_class": cell_class,
        "flip_kind": flip_kind,
    }


def normalized_distance_to_operating_point(row: dict[str, object]) -> float:
    threshold_range = max(THRESHOLDS) - min(THRESHOLDS)
    broad_range = max(BROAD_FINAL_SIGMAS) - min(BROAD_FINAL_SIGMAS)
    sharp_range = max(SHARP_FINAL_SIGMAS) - min(SHARP_FINAL_SIGMAS)
    return (
        abs(float(row["threshold"]) - STEP6_OPERATING_POINT["threshold"]) / threshold_range
        + abs(float(row["broad_final_sigma"]) - STEP6_OPERATING_POINT["broad_final_sigma"]) / broad_range
        + abs(float(row["sharp_final_sigma"]) - STEP6_OPERATING_POINT["sharp_final_sigma"]) / sharp_range
    )


def summarize_flips(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        if row["cell_class"] == "FLIP":
            grouped[str(row["flip_kind"])].append(row)

    summaries: list[dict[str, object]] = []
    for flip_kind, members in sorted(grouped.items()):
        thresholds = [float(row["threshold"]) for row in members]
        broad = [float(row["broad_final_sigma"]) for row in members]
        sharp = [float(row["sharp_final_sigma"]) for row in members]
        examples = "; ".join(
            f"{row['grid_config']}@thr={float(row['threshold']):.2f},b={float(row['broad_final_sigma']):.2f},s={float(row['sharp_final_sigma']):.2f}"
            for row in members[:5]
        )
        if flip_kind == "broad_false_collapse":
            description = "threshold/grid/narrow-broad regimes where the broad family is counted as a singleton"
        elif flip_kind == "sharp_noncollapse":
            description = "wide-sharp or low-threshold regimes where the sharp family remains multiply supported"
        else:
            description = "mixed regimes where neither family gives the Step-6 qualitative verdict"
        summaries.append(
            {
                "flip_kind": flip_kind,
                "cell_count": len(members),
                "threshold_min": f"{min(thresholds):.2f}",
                "threshold_max": f"{max(thresholds):.2f}",
                "broad_final_sigma_min": f"{min(broad):.2f}",
                "broad_final_sigma_max": f"{max(broad):.2f}",
                "sharp_final_sigma_min": f"{min(sharp):.2f}",
                "sharp_final_sigma_max": f"{max(sharp):.2f}",
                "description": description,
                "example_cells": examples,
            }
        )
    return summaries


def robustness_map(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[tuple[float, float, float], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        gap = round(float(row["broad_final_sigma"]) - float(row["sharp_final_sigma"]), 2)
        grouped[(float(row["threshold"]), gap, float(row["sharp_final_sigma"]))].append(row)
    output: list[dict[str, object]] = []
    for (threshold, gap, sharp_sigma), members in sorted(grouped.items()):
        hold_count = sum(1 for row in members if row["cell_class"] == "VERDICT_HOLDS")
        output.append(
            {
                "threshold": f"{threshold:.2f}",
                "sigma_gap": f"{gap:.2f}",
                "sharp_final_sigma": f"{sharp_sigma:.2f}",
                "total_cells": len(members),
                "hold_cells": hold_count,
                "hold_fraction": f"{hold_count / len(members):.12f}",
            }
        )
    return output


def operating_point_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    op_matches = [
        row
        for row in rows
        if row["grid_config"] == STEP6_OPERATING_POINT["grid_config"]
        and abs(float(row["threshold"]) - STEP6_OPERATING_POINT["threshold"]) < 1e-12
        and abs(float(row["broad_final_sigma"]) - STEP6_OPERATING_POINT["broad_final_sigma"]) < 1e-12
        and abs(float(row["sharp_final_sigma"]) - STEP6_OPERATING_POINT["sharp_final_sigma"]) < 1e-12
    ]
    if len(op_matches) != 1:
        raise RuntimeError("Step 6 operating point not found exactly once")
    op = op_matches[0]
    same_grid_flips = [row for row in rows if row["grid_config"] == "step6_exact" and row["cell_class"] == "FLIP"]
    nearest = min(same_grid_flips, key=normalized_distance_to_operating_point)
    return [
        {
            "operating_grid_config": op["grid_config"],
            "operating_threshold": f"{float(op['threshold']):.2f}",
            "operating_broad_final_sigma": f"{float(op['broad_final_sigma']):.2f}",
            "operating_sharp_final_sigma": f"{float(op['sharp_final_sigma']):.2f}",
            "operating_cell_class": op["cell_class"],
            "operating_broad_sequence": op["broad_sequence"],
            "operating_sharp_sequence": op["sharp_sequence"],
            "nearest_flip_kind": nearest["flip_kind"],
            "nearest_flip_threshold": f"{float(nearest['threshold']):.2f}",
            "nearest_flip_broad_final_sigma": f"{float(nearest['broad_final_sigma']):.2f}",
            "nearest_flip_sharp_final_sigma": f"{float(nearest['sharp_final_sigma']):.2f}",
            "nearest_flip_normalized_margin": f"{normalized_distance_to_operating_point(nearest):.12f}",
        }
    ]


def main() -> None:
    if not (STEP6_DIR / "e043_horn_adjudication_step6.py").exists():
        raise FileNotFoundError("missing Step 6 horn adjudication source")

    rows: list[dict[str, object]] = []
    for config in grid_configs():
        grid = list(config["grid"])
        for threshold in THRESHOLDS:
            for broad_final_sigma in BROAD_FINAL_SIGMAS:
                for sharp_final_sigma in SHARP_FINAL_SIGMAS:
                    classified = classify_cell(grid, threshold, broad_final_sigma, sharp_final_sigma)
                    rows.append(
                        {
                            "grid_config": config["grid_config"],
                            "grid_size": config["grid_size"],
                            "spacing": config["spacing"],
                            "range_high": f"{float(config['range_high']):.12g}",
                            "threshold": f"{threshold:.2f}",
                            "broad_final_sigma": f"{broad_final_sigma:.2f}",
                            "sharp_final_sigma": f"{sharp_final_sigma:.2f}",
                            "sigma_gap": f"{broad_final_sigma - sharp_final_sigma:.2f}",
                            **classified,
                        }
                    )

    hold_cells = sum(1 for row in rows if row["cell_class"] == "VERDICT_HOLDS")
    flip_cells = len(rows) - hold_cells
    op_rows = operating_point_rows(rows)
    flip_rows = summarize_flips(rows)

    write_csv(
        ARTIFACT_DIR / "sweep_cells_step10.csv",
        rows,
        [
            "grid_config",
            "grid_size",
            "spacing",
            "range_high",
            "threshold",
            "broad_final_sigma",
            "sharp_final_sigma",
            "sigma_gap",
            "broad_sequence",
            "sharp_sequence",
            "broad_final_degeneracy",
            "sharp_final_degeneracy",
            "broad_monotone",
            "sharp_monotone",
            "broad_collapses",
            "sharp_collapses",
            "cell_class",
            "flip_kind",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "robustness_map_step10.csv",
        robustness_map(rows),
        ["threshold", "sigma_gap", "sharp_final_sigma", "total_cells", "hold_cells", "hold_fraction"],
    )
    write_csv(
        ARTIFACT_DIR / "flip_boundaries_step10.csv",
        flip_rows,
        [
            "flip_kind",
            "cell_count",
            "threshold_min",
            "threshold_max",
            "broad_final_sigma_min",
            "broad_final_sigma_max",
            "sharp_final_sigma_min",
            "sharp_final_sigma_max",
            "description",
            "example_cells",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "operating_point_margin_step10.csv",
        op_rows,
        [
            "operating_grid_config",
            "operating_threshold",
            "operating_broad_final_sigma",
            "operating_sharp_final_sigma",
            "operating_cell_class",
            "operating_broad_sequence",
            "operating_sharp_sequence",
            "nearest_flip_kind",
            "nearest_flip_threshold",
            "nearest_flip_broad_final_sigma",
            "nearest_flip_sharp_final_sigma",
            "nearest_flip_normalized_margin",
        ],
    )

    output = {
        "step": 10,
        "artifact_type": "adjudication_robustness_sweep",
        "source_step": "steps/step6_e043_horn_adjudication_artifacts/e043_horn_adjudication_step6.py",
        "sweep": {
            "total_cells": len(rows),
            "hold_cells": hold_cells,
            "flip_cells": flip_cells,
            "hold_fraction": hold_cells / len(rows),
            "threshold_count": len(THRESHOLDS),
            "broad_final_sigma_count": len(BROAD_FINAL_SIGMAS),
            "sharp_final_sigma_count": len(SHARP_FINAL_SIGMAS),
            "grid_config_count": len(grid_configs()),
        },
        "operating_point": op_rows[0],
        "flip_boundaries": flip_rows,
        "verdict": {
            "type": "robustness_sweep_constructed",
            "step6_operating_point_holds": op_rows[0]["operating_cell_class"] == "VERDICT_HOLDS",
            "contains_hold_cells": hold_cells > 0,
            "contains_flip_cells": flip_cells > 0,
            "finite_grammar_only": True,
            "external_review_required": True,
        },
        "nonclaim": "Finite parameter sweep over the toy degeneracy audit only; no physical scale value or physical mechanism is determined.",
    }
    (ARTIFACT_DIR / "adjudication_robustness_output_step10.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
