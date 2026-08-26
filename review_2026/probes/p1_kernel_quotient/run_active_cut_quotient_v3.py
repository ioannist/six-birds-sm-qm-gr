#!/usr/bin/env python3
"""Full in-memory and byte validator for P1-HYGIENE v3."""

from __future__ import annotations

import argparse
import time
from collections import Counter
from pathlib import Path

import active_cut_quotient_v2 as v2
import active_cut_quotient_v3 as core
import build_active_cut_quotient_v3 as build


HERE = Path(__file__).resolve().parent
NAMED_CARRIER = "K23_bipartite__b6__leaf_offset0"
NAMED_SEED = 31


def validate() -> dict:
    result = core.run()
    for name, payload in build.render(result).items():
        path = HERE / name
        if not path.is_file() or path.read_bytes() != payload:
            raise AssertionError(f"full rebuild byte mismatch: {name}")

    if not all(
        row["passes"] and row["expected_sha256"] == row["actual_sha256"]
        for row in result["pin"]
    ):
        raise AssertionError("v2 dependency pin failure")

    grouped = {}
    for row in result["regressions"]:
        grouped.setdefault(row["carrier"], []).append(row)
        if not (
            row["unique_all_regions"]
            and row["unique_after_closure"]
            and row["all_region_values_preserved"]
            and row["residual_deficiency"] == 0
        ):
            raise AssertionError(f"known regression failed: {row}")
    expected_ranks = {
        "published_step42_raw": [9, 9, 9],
        "crosslinked_three_path": [9, 9, 9],
        "grid_2x3_multiterminal": [10, 10, 9],
        "k4_well_connected_stiff_chord": [11, 11, 11],
    }
    for carrier, ranks in expected_ranks.items():
        if [row["raw_exact_rank"] for row in grouped[carrier]] != ranks:
            raise AssertionError(f"regression rank changed for {carrier}")

    summary = result["summary"][0]
    expected_summary = {
        "evaluated_weighted_carriers": 378,
        "four_move_survivors": 35,
        "explained_by_fifth_move": 22,
        "five_move_survivors": 13,
        "residual_deficiency_histogram": "1:8|2:4|3:1",
        "experimental_k23_fully_explained": 0,
        "experimental_k4_fully_explained": 0,
    }
    if summary != expected_summary:
        raise AssertionError(f"five-move census changed: {summary}")
    if len(result["search"]) != 378:
        raise AssertionError("search table is not the declared 378 cases")
    survivors = [row for row in result["search"] if row["residual_deficiency"]]
    if Counter(row["residual_deficiency"] for row in survivors) != Counter({1: 8, 2: 4, 3: 1}):
        raise AssertionError("survivor histogram does not rederive")

    named_row = next(row for row in result["search"] if row["named_regression"])
    if not (
        named_row["carrier"] == NAMED_CARRIER
        and named_row["seed"] == NAMED_SEED
        and named_row["reduced_edge_count"] == 9
        and named_row["reduced_exact_rank"] == 8
        and named_row["residual_deficiency"] == 1
    ):
        raise AssertionError(f"named search row changed: {named_row}")
    audits = result["named_regression"]
    expected_moves = [
        "inseparable_vertex_contraction_parallel_sum",
        "y_delta",
        "delta_y",
        "series_bivalent",
        "closure_result",
    ]
    if [row["move"] for row in audits] != expected_moves:
        raise AssertionError(f"named move history changed: {audits}")
    for row in audits:
        if not (
            row["region_count"] == 62
            and row["all_region_values_preserved"]
            and row["unique_before"]
            and row["unique_after_move"]
            and row["rank_recomputed_after_move"] == 8
        ):
            raise AssertionError(f"named per-move audit failed: {row}")

    # Reconstruct the named weighted carrier independently of the stored rows.
    carrier = next(item for item in v2.search_carriers() if item.name == NAMED_CARRIER)
    graph = v2.seeded_weights(carrier, NAMED_SEED)
    raw = v2.active_cuts(graph)
    reduced, final, moves, independent_audits = core.five_move_closure(graph)
    recomputed_rank = v2.rational_rank(final.incidence)
    if not (
        len(raw.regions) == len(final.regions) == 62
        and raw.unique
        and final.unique
        and raw.values == final.values
        and len(reduced.edges) == 9
        and final.rank == recomputed_rank == 8
        and core.deficiency(reduced, final) == 1
        and len(independent_audits) + 1 == len(audits)
        and [row["move"] for row in moves] == expected_moves[:-1]
    ):
        raise AssertionError("independent named-candidate rederivation failed")

    if len(result["experimental"]) != 26:
        raise AssertionError("both experimental rules were not run on all 13 survivors")
    direction_totals = Counter()
    for row in result["experimental"]:
        if not row["experimental_not_in_certified_closure"]:
            raise AssertionError("experimental move leaked into certified status")
        direction_totals[row["experimental_rule"]] += row["candidate_direction_count"]
        if row["accepted_direction_count"] or row["accepted_span_rank"] or row["fully_explains_residual"]:
            raise AssertionError(f"experimental outcome changed: {row}")
    if direction_totals != Counter(
        {
            "EXPERIMENTAL_K23_FOUR_CYCLE_TRANSPORT": 25,
            "EXPERIMENTAL_K4_OPPOSITE_PERFECT_MATCHING": 3,
        }
    ):
        raise AssertionError(f"experimental direction census changed: {direction_totals}")
    if any(
        "EXPERIMENTAL" in row["closure_moves"]
        for row in result["search"]
    ):
        raise AssertionError("experimental rule entered the certified closure")
    if result["outcome"] != (
        "FIVE_MOVE_CLOSURE_LEAVES_13_RESIDUAL_SURVIVORS_"
        "EXPERIMENTAL_SIXTH_MOVES_EXPLAIN_NONE"
    ):
        raise AssertionError(f"outcome changed: {result['outcome']}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        raise SystemExit("run_active_cut_quotient_v3.py: FAIL: use --self")
    started = time.perf_counter()
    result = validate()
    summary = result["summary"][0]
    print(
        "run_active_cut_quotient_v3.py: PASS: pin=1/1 regressions=12/12 "
        f"search={summary['evaluated_weighted_carriers']} "
        f"four_survivors={summary['four_move_survivors']} "
        f"fifth_explained={summary['explained_by_fifth_move']} "
        f"survivors={summary['five_move_survivors']} "
        f"histogram={summary['residual_deficiency_histogram']} "
        "named_cuts=62/62 named_rank=8/9 experimental=0/13|0/13 "
        f"elapsed_seconds={time.perf_counter()-started:.3f}"
    )


if __name__ == "__main__":
    main()
