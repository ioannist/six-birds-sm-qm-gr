#!/usr/bin/env python3
"""Cluster A Step 8: structural token-blind selection on a neutral product space."""

from __future__ import annotations

import csv
import itertools
import json
import math
from collections import Counter
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REALIZED_COORDS = ("g0", "r0", 3, "t0", "e0", "u0", "v0")


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


GAUGES = [
    {"code": "g0", "anomaly_charge": 0, "rank": 4, "family_index": 1, "complexity": 2, "allowed_rep_families": {"a", "b"}},
    {"code": "g1", "anomaly_charge": 1, "rank": 5, "family_index": 2, "complexity": 3, "allowed_rep_families": {"b", "c"}},
    {"code": "g2", "anomaly_charge": -1, "rank": 3, "family_index": 1, "complexity": 2, "allowed_rep_families": {"a", "c"}},
    {"code": "g3", "anomaly_charge": 0, "rank": 6, "family_index": 3, "complexity": 4, "allowed_rep_families": {"a", "b", "c"}},
]

REPS = [
    {"code": "r0", "anomaly_charge": 0, "family": "a", "chirality": 1, "complexity": 1},
    {"code": "r1", "anomaly_charge": -1, "family": "b", "chirality": 1, "complexity": 2},
    {"code": "r2", "anomaly_charge": 1, "family": "c", "chirality": -1, "complexity": 2},
    {"code": "r3", "anomaly_charge": 0, "family": "b", "chirality": 0, "complexity": 1},
]

GENERATION_COUNTS = [1, 2, 3, 4, 5]

TEXTURES = [
    {"code": "t0", "max_generations": 5, "complexity": 1, "chirality": 1},
    {"code": "t1", "max_generations": 2, "complexity": 2, "chirality": 1},
    {"code": "t2", "max_generations": 4, "complexity": 3, "chirality": -1},
    {"code": "t3", "max_generations": 6, "complexity": 2, "chirality": 0},
]

EW_SCALES = [
    {"code": "e0", "sensitivity": 1, "tuning_cost": 1},
    {"code": "e1", "sensitivity": 2, "tuning_cost": 2},
    {"code": "e2", "sensitivity": 3, "tuning_cost": 3},
]

UV_OPTIONS = [
    {"code": "u0", "capacity": 8, "control": 3, "consistency": 3},
    {"code": "u1", "capacity": 6, "control": 2, "consistency": 2},
    {"code": "u2", "capacity": 4, "control": 1, "consistency": 1},
]

VACUA = [
    {"code": "v0", "stability": 3, "measure_weight": 2},
    {"code": "v1", "stability": 2, "measure_weight": 1},
    {"code": "v2", "stability": 1, "measure_weight": 0},
]


def anomaly_value(gauge: dict[str, object], rep: dict[str, object]) -> int:
    return int(gauge["anomaly_charge"]) + int(rep["anomaly_charge"])


def gauge_rep_consistent(gauge: dict[str, object], rep: dict[str, object], anomaly: int) -> bool:
    allowed = set(gauge["allowed_rep_families"])
    rep_family = str(rep["family"])
    chirality = int(rep["chirality"])
    return rep_family in allowed or (anomaly == 0 and chirality != 0)


def generation_chirality_condition(gauge: dict[str, object], rep: dict[str, object], generation_count: int) -> bool:
    chirality_scale = max(1, abs(int(rep["chirality"])))
    family_index = int(gauge["family_index"])
    return ((generation_count * chirality_scale + family_index) % 2 == 0)


def texture_condition(rep: dict[str, object], texture: dict[str, object], generation_count: int) -> bool:
    rep_chirality = int(rep["chirality"])
    texture_chirality = int(texture["chirality"])
    chirality_matches = texture_chirality in {rep_chirality, 0} or rep_chirality == 0
    return chirality_matches and generation_count <= int(texture["max_generations"])


def uv_condition(gauge: dict[str, object], texture: dict[str, object], uv: dict[str, object], anomaly: int) -> bool:
    capacity_ok = int(uv["capacity"]) >= int(gauge["rank"]) + int(texture["complexity"])
    consistency_ok = int(uv["consistency"]) >= abs(anomaly) + 1
    return capacity_ok and consistency_ok


def naturalness_cost(
    gauge: dict[str, object],
    rep: dict[str, object],
    generation_count: int,
    texture: dict[str, object],
    ew_scale: dict[str, object],
    uv: dict[str, object],
    vacuum: dict[str, object],
) -> int:
    sensitivity_gap = max(0, int(ew_scale["sensitivity"]) - int(uv["control"]))
    structural_load = int(texture["complexity"]) + int(rep["complexity"]) + int(gauge["complexity"])
    control_gap = max(0, structural_load - int(vacuum["stability"]) - int(uv["control"]))
    capacity_gap = max(0, generation_count - int(uv["capacity"]))
    return sensitivity_gap + control_gap + capacity_gap


def structural_score(
    gauge: dict[str, object],
    rep: dict[str, object],
    texture: dict[str, object],
    ew_scale: dict[str, object],
    uv: dict[str, object],
    vacuum: dict[str, object],
    anomaly: int,
    naturalness: int,
    checks: dict[str, bool],
) -> float:
    structural_size = int(gauge["rank"]) + int(texture["complexity"]) + int(rep["complexity"]) + int(ew_scale["tuning_cost"])
    failed_checks = sum(0 if value else 1 for value in checks.values())
    return (
        100.0
        - 8.0 * abs(anomaly)
        - 5.0 * failed_checks
        - 9.0 * naturalness
        - 0.3 * structural_size
        + float(uv["control"])
        + float(vacuum["stability"])
    )


def build_candidate_space() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx, (gauge, rep, generation_count, texture, ew_scale, uv, vacuum) in enumerate(
        itertools.product(GAUGES, REPS, GENERATION_COUNTS, TEXTURES, EW_SCALES, UV_OPTIONS, VACUA)
    ):
        anomaly = anomaly_value(gauge, rep)
        checks = {
            "anomaly_free": anomaly == 0,
            "gauge_rep_consistent": gauge_rep_consistent(gauge, rep, anomaly),
            "generation_chirality_ok": generation_chirality_condition(gauge, rep, generation_count),
            "texture_ok": texture_condition(rep, texture, generation_count),
            "uv_consistent": uv_condition(gauge, texture, uv, anomaly),
        }
        naturalness = naturalness_cost(gauge, rep, generation_count, texture, ew_scale, uv, vacuum)
        checks["naturalness_ok"] = naturalness <= 2
        admissible = all(checks.values())
        coords = (
            str(gauge["code"]),
            str(rep["code"]),
            int(generation_count),
            str(texture["code"]),
            str(ew_scale["code"]),
            str(uv["code"]),
            str(vacuum["code"]),
        )
        rows.append(
            {
                "candidate_id": f"n_{idx:05d}",
                "gauge_code": coords[0],
                "rep_code": coords[1],
                "n_gen": coords[2],
                "texture_code": coords[3],
                "ew_code": coords[4],
                "uv_code": coords[5],
                "vacuum_code": coords[6],
                "source": "full_product",
                "anomaly_value": anomaly,
                "anomaly_free": checks["anomaly_free"],
                "gauge_rep_consistent": checks["gauge_rep_consistent"],
                "generation_chirality_ok": checks["generation_chirality_ok"],
                "texture_ok": checks["texture_ok"],
                "uv_consistent": checks["uv_consistent"],
                "naturalness_cost": naturalness,
                "naturalness_ok": checks["naturalness_ok"],
                "structurally_admissible": admissible,
                "structural_score": f"{structural_score(gauge, rep, texture, ew_scale, uv, vacuum, anomaly, naturalness, checks):.6f}",
                "is_realized_point": coords == REALIZED_COORDS,
            }
        )
    return rows


def sequential_breakdown(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    stages = [
        ("neutral_product", lambda row: True),
        ("anomaly_free", lambda row: str(row["anomaly_free"]).lower() == "true"),
        ("plus_gauge_rep_consistency", lambda row: str(row["anomaly_free"]).lower() == "true" and str(row["gauge_rep_consistent"]).lower() == "true"),
        (
            "plus_generation_chirality",
            lambda row: str(row["anomaly_free"]).lower() == "true"
            and str(row["gauge_rep_consistent"]).lower() == "true"
            and str(row["generation_chirality_ok"]).lower() == "true",
        ),
        (
            "plus_texture",
            lambda row: str(row["anomaly_free"]).lower() == "true"
            and str(row["gauge_rep_consistent"]).lower() == "true"
            and str(row["generation_chirality_ok"]).lower() == "true"
            and str(row["texture_ok"]).lower() == "true",
        ),
        (
            "plus_uv",
            lambda row: str(row["anomaly_free"]).lower() == "true"
            and str(row["gauge_rep_consistent"]).lower() == "true"
            and str(row["generation_chirality_ok"]).lower() == "true"
            and str(row["texture_ok"]).lower() == "true"
            and str(row["uv_consistent"]).lower() == "true",
        ),
        ("plus_naturalness", lambda row: str(row["structurally_admissible"]).lower() == "true"),
    ]
    out = []
    total = len(rows)
    previous = total
    for stage_id, predicate in stages:
        count = sum(1 for row in rows if predicate(row))
        out.append(
            {
                "stage": stage_id,
                "survivor_count": count,
                "removed_since_previous": previous - count,
                "fraction_of_neutral": f"{count / total:.8f}",
            }
        )
        previous = count
    return out


def mutual_information_bits(rows: list[dict[str, object]]) -> float:
    total = len(rows)
    if total == 0:
        return 0.0
    gauge_counts = Counter(str(row["gauge_code"]) for row in rows)
    generation_counts = Counter(int(row["n_gen"]) for row in rows)
    pair_counts = Counter((str(row["gauge_code"]), int(row["n_gen"])) for row in rows)
    mi = 0.0
    for (gauge_code, generation_count), pair_count in pair_counts.items():
        p_pair = pair_count / total
        p_gauge = gauge_counts[gauge_code] / total
        p_generation = generation_counts[generation_count] / total
        mi += p_pair * math.log2(p_pair / (p_gauge * p_generation))
    return mi


def support_stats(rows: list[dict[str, object]]) -> dict[str, object]:
    gauge_values = sorted({str(row["gauge_code"]) for row in rows})
    generation_values = sorted({int(row["n_gen"]) for row in rows})
    observed_pairs = sorted({f"{row['gauge_code']}|{row['n_gen']}" for row in rows})
    cartesian_pairs = [f"{gauge}|{generation}" for gauge in gauge_values for generation in generation_values]
    missing_pairs = sorted(set(cartesian_pairs) - set(observed_pairs))
    return {
        "gauge_values": ";".join(gauge_values),
        "generation_values": ";".join(str(value) for value in generation_values),
        "observed_pair_count": len(observed_pairs),
        "cartesian_pair_count": len(cartesian_pairs),
        "missing_pair_count": len(missing_pairs),
        "missing_pairs": ";".join(missing_pairs) if missing_pairs else "none",
    }


def top_tier_size(survivors: list[dict[str, object]]) -> int:
    if not survivors:
        return 0
    best = max(float(row["structural_score"]) for row in survivors)
    return sum(1 for row in survivors if abs(float(row["structural_score"]) - best) < 1e-9)


def main() -> None:
    rows = build_candidate_space()
    survivors = sorted(
        [row for row in rows if str(row["structurally_admissible"]).lower() == "true"],
        key=lambda row: (-float(row["structural_score"]), row["candidate_id"]),
    )
    for rank, row in enumerate(survivors, start=1):
        row["structural_rank"] = rank

    realized_rows = [row for row in rows if str(row["is_realized_point"]).lower() == "true"]
    realized_survivor = [row for row in survivors if str(row["is_realized_point"]).lower() == "true"]
    realized_rank = int(realized_survivor[0]["structural_rank"]) if realized_survivor else ""
    realized_score = realized_survivor[0]["structural_score"] if realized_survivor else ""
    max_score_tie = top_tier_size(survivors)
    if len(realized_survivor) == 1 and len(survivors) == 1:
        realized_status = "unique_structural_survivor"
    elif realized_survivor:
        realized_status = "among_structural_survivors_not_unique"
    else:
        realized_status = "not_structurally_admissible"

    neutral_stats = support_stats(rows)
    survivor_stats = support_stats(survivors)
    mi_rows = [
        {
            "population": "neutral_product",
            "population_size": len(rows),
            "gauge_generation_mi_bits": f"{mutual_information_bits(rows):.12f}",
            **neutral_stats,
        },
        {
            "population": "structural_survivors",
            "population_size": len(survivors),
            "gauge_generation_mi_bits": f"{mutual_information_bits(survivors):.12f}",
            **survivor_stats,
        },
    ]

    generation_rows = [
        {"facet": "gauge_code", "alphabet_size": len(GAUGES), "codes": ";".join(row["code"] for row in GAUGES), "generation": "full independent product"},
        {"facet": "rep_code", "alphabet_size": len(REPS), "codes": ";".join(row["code"] for row in REPS), "generation": "full independent product"},
        {"facet": "n_gen", "alphabet_size": len(GENERATION_COUNTS), "codes": ";".join(str(value) for value in GENERATION_COUNTS), "generation": "full independent product"},
        {"facet": "texture_code", "alphabet_size": len(TEXTURES), "codes": ";".join(row["code"] for row in TEXTURES), "generation": "full independent product"},
        {"facet": "ew_code", "alphabet_size": len(EW_SCALES), "codes": ";".join(row["code"] for row in EW_SCALES), "generation": "full independent product"},
        {"facet": "uv_code", "alphabet_size": len(UV_OPTIONS), "codes": ";".join(row["code"] for row in UV_OPTIONS), "generation": "full independent product"},
        {"facet": "vacuum_code", "alphabet_size": len(VACUA), "codes": ";".join(row["code"] for row in VACUA), "generation": "full independent product"},
    ]

    summary_rows = [
        {
            "neutral_space_size": len(rows),
            "structural_survivor_count": len(survivors),
            "structural_survivor_fraction": f"{len(survivors) / len(rows):.8f}",
            "realized_point_present_in_neutral_space": len(realized_rows) == 1,
            "realized_point_status": realized_status,
            "realized_point_structural_rank": realized_rank,
            "realized_point_structural_score": realized_score,
            "max_score_tie_count": max_score_tie,
            "mi_neutral_bits": mi_rows[0]["gauge_generation_mi_bits"],
            "mi_survivors_bits": mi_rows[1]["gauge_generation_mi_bits"],
            "coupling_interpretation": "neutral_product_independent_constraints_induce_coupling",
        }
    ]

    write_csv(
        ARTIFACT_DIR / "neutral_candidate_space_step8.csv",
        rows,
        [
            "candidate_id",
            "gauge_code",
            "rep_code",
            "n_gen",
            "texture_code",
            "ew_code",
            "uv_code",
            "vacuum_code",
            "source",
            "anomaly_value",
            "anomaly_free",
            "gauge_rep_consistent",
            "generation_chirality_ok",
            "texture_ok",
            "uv_consistent",
            "naturalness_cost",
            "naturalness_ok",
            "structurally_admissible",
            "structural_score",
            "is_realized_point",
            "structural_rank",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "structural_survivors_step8.csv",
        survivors,
        [
            "structural_rank",
            "candidate_id",
            "gauge_code",
            "rep_code",
            "n_gen",
            "texture_code",
            "ew_code",
            "uv_code",
            "vacuum_code",
            "source",
            "anomaly_value",
            "anomaly_free",
            "gauge_rep_consistent",
            "generation_chirality_ok",
            "texture_ok",
            "uv_consistent",
            "naturalness_cost",
            "naturalness_ok",
            "structurally_admissible",
            "structural_score",
            "is_realized_point",
        ],
    )
    write_csv(ARTIFACT_DIR / "admissibility_breakdown_step8.csv", sequential_breakdown(rows))
    write_csv(ARTIFACT_DIR / "mi_comparison_step8.csv", mi_rows)
    write_csv(ARTIFACT_DIR / "neutral_generation_procedure_step8.csv", generation_rows)
    write_csv(ARTIFACT_DIR / "structural_summary_step8.csv", summary_rows)

    output = {
        "step": 8,
        "verdict": {
            "type": "structural_token_blind_selection_constructed",
            "neutral_space_size": len(rows),
            "structural_survivor_count": len(survivors),
            "realized_point_status": realized_status,
            "realized_point_structural_rank": realized_rank,
            "max_score_tie_count": max_score_tie,
            "mi_neutral_bits": float(mi_rows[0]["gauge_generation_mi_bits"]),
            "mi_survivors_bits": float(mi_rows[1]["gauge_generation_mi_bits"]),
            "token_blind_structural_functional": True,
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "nonclaim": "Finite token-blind pruning shape only; no physical SM value or mechanism is derived.",
    }
    (ARTIFACT_DIR / "structural_token_blind_output_step8.json").write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
