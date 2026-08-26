#!/usr/bin/env python3
"""Full in-memory/byte validator for P1-REPAIR-2."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import active_cut_quotient_v2 as core
import build_active_cut_quotient_v2 as build


HERE = Path(__file__).resolve().parent


def validate() -> dict:
    result = core.run()
    for name, payload in build.render(result).items():
        path = HERE / name
        if not path.is_file() or path.read_bytes() != payload:
            raise AssertionError(f"full rebuild byte mismatch: {name}")
    if not all(row["passes"] and row["expected_sha256"] == row["actual_sha256"]
               for row in result["pin"]):
        raise AssertionError("v1 dependency pin failure")
    grouped = {}
    for row in result["regressions"]:
        grouped.setdefault(row["carrier"], []).append(row)
        if not row["unique_all_regions"] or not row["all_region_values_preserved"]:
            raise AssertionError(f"regression uniqueness/preservation failure: {row}")
        if row["residual_deficiency"]:
            raise AssertionError(f"known regression not fully explained: {row}")
    if [row["raw_exact_rank"] for row in grouped["published_step42_raw"]] != [9, 9, 9]:
        raise AssertionError("published exact ranks changed")
    if [row["raw_exact_rank"] for row in grouped["crosslinked_three_path"]] != [9, 9, 9]:
        raise AssertionError("crosslinked exact ranks changed")
    if [row["raw_exact_rank"] for row in grouped["grid_2x3_multiterminal"]] != [10, 10, 9]:
        raise AssertionError("grid exact ranks changed")
    if [row["raw_exact_rank"] for row in grouped["k4_well_connected_stiff_chord"]] != [11, 11, 11]:
        raise AssertionError("stiff-K4 exact ranks changed")
    definition = result["search_definition"]
    if (definition["topology_template_count"], definition["unweighted_carrier_count"],
            definition["evaluated_weighted_carrier_count"]) != (14, 126, 378):
        raise AssertionError(f"search family changed: {definition}")
    census = result["search_census"][0]
    if census["residual_survivor_count"] != 35 or census["fully_explained_after_closure"] != 343:
        raise AssertionError(f"search census changed: {census}")
    candidate = result["candidate"][0]
    if not (candidate["boundary_count"] == 6 and candidate["edge_count_after_closure"] == 9
            and candidate["exact_rank"] == 8 and candidate["residual_deficiency"] == 1):
        raise AssertionError(f"landing candidate changed: {candidate}")
    if len(result["candidate_active_cuts"]) != 62:
        raise AssertionError("candidate does not include all 62 boundary regions")
    if any(row["applicable_object_count"] or not row["blocks_candidate"]
           for row in result["candidate_irreducibility"]):
        raise AssertionError(f"a named reduction remains applicable: {result['candidate_irreducibility']}")
    dependency = result["dependencies"][0]
    if dependency["integer_column_dependency"] != "-1*I0-I1 +1*I0-I2 +1*I1-I2":
        raise AssertionError(f"candidate dependency changed: {dependency}")
    if not dependency["incidence_times_direction_zero"]:
        raise AssertionError("candidate dependency is not exact")
    if len(result["finite_checks"]) != 2 or any(
            not row["unique_after_move"] or not row["active_cuts_unchanged"]
            or not row["all_region_values_unchanged"] for row in result["finite_checks"]):
        raise AssertionError(f"finite two-sided invariance failed: {result['finite_checks']}")
    if result["outcome"] != "RESIDUAL_ACTIVE_CUT_DEFICIENCY_SURVIVES_FOUR_NAMED_REDUCTIONS":
        raise AssertionError(f"outcome changed: {result['outcome']}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        raise SystemExit("run_active_cut_quotient_v2.py: FAIL: use --self")
    started = time.perf_counter()
    result = validate()
    print("run_active_cut_quotient_v2.py: PASS: pin=1/1 regressions=12/12 "
          "ranks=published9|crosslinked9|grid10,10,9|stiff11 search=378 "
          f"survivors={result['search_census'][0]['residual_survivor_count']} "
          "candidate=edges9|rank8|deficiency1 finite_checks=2/2 "
          f"elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
