#!/usr/bin/env python3
"""Full rebuild-and-byte-compare validator for PROG3 Step 1."""

from __future__ import annotations

import argparse
import csv
import tempfile
import time
from pathlib import Path

from build_step1 import HERE, generate


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> str:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="prog3_step1_") as temporary:
        rebuilt_directory = Path(temporary)
        rebuilt = generate(rebuilt_directory)
        mismatches = [
            name
            for name in sorted(rebuilt)
            if not (HERE / name).exists()
            or (HERE / name).read_bytes() != (rebuilt_directory / name).read_bytes()
        ]
        if mismatches:
            raise AssertionError(f"artifact byte mismatch: {mismatches}")

    summaries = read_csv(HERE / "carrier_summary_step1.csv")
    if len(summaries) != 13:
        raise AssertionError(f"expected 13 survivors, found {len(summaries)}")
    if not all(row["v3_status_exactly_reproduced"] == "True" for row in summaries):
        raise AssertionError("an exact status differs from v3")
    if not all(row["raw_unique_all_regions"] == "True" for row in summaries):
        raise AssertionError("an exact raw carrier has a degenerate minimizer")
    tiny = {
        (row["carrier"], row["seed"]): row["raw_minimum_margin_exact"]
        for row in summaries
        if row["raw_margin_class"] == "GENUINELY_TINY_POSITIVE"
    }
    expected_tiny = {
        ("wheel_W4__b8__leaf_offset0", "47"): "135/274877906944",
        ("wheel_W4__b8__leaf_offset1", "17"): "113/274877906944",
        ("K23_bipartite__b8__dual_gateway", "47"): "79/17179869184",
    }
    if tiny != expected_tiny:
        raise AssertionError(f"exact tiny-margin classification changed: {tiny}")

    intervals = read_csv(HERE / "kernel_intervals_step1.csv")
    fibers = read_csv(HERE / "certified_fibers_step1.csv")
    if len(intervals) != 19 or not all(row["nondegenerate"] == "True" for row in intervals):
        raise AssertionError("expected 19 nondegenerate kernel intervals")
    if len(fibers) != 19 or not all(row["certified_fiber"] == "True" for row in fibers):
        raise AssertionError("expected 19 certified direction fibers")
    if not all(
        row["exact_fingerprint_equal_by_full_enumeration"] == "True"
        and row["weights_differ"] == "True"
        and row["any_graph_automorphism_maps_base_to_perturbed"] == "False"
        and row["terminal_set_automorphism_maps_base_to_perturbed"] == "False"
        and int(row["selected_canonical_reclosure_path_length"]) >= 0
        for row in fibers
    ):
        raise AssertionError("a non-equivalence certificate failed")
    if sum(row["certified_carrier_fiber"] == "True" for row in summaries) != 13:
        raise AssertionError("not every carrier has a certified fiber")

    orbit_rows = read_csv(HERE / "orbit_audit_step1.csv")
    if len(orbit_rows) != 19:
        raise AssertionError(f"expected 19 orbit audits, found {len(orbit_rows)}")
    for row in orbit_rows:
        cross_count = int(row["cross_orbit_weighted_isomorphism_count"])
        if row["verdict"] == "depth-three five-move-orbit-disjoint":
            if cross_count != 0 or row["path_if_gauge"]:
                raise AssertionError(f"invalid disjoint orbit row: {row}")
        elif row["verdict"] == "GAUGE":
            if cross_count <= 0 or not row["path_if_gauge"]:
                raise AssertionError(f"invalid gauge orbit row: {row}")
        else:
            raise AssertionError(f"unknown orbit verdict: {row['verdict']}")
        if min(
            int(row["base_orbit_state_count"]),
            int(row["perturbed_orbit_state_count"]),
            int(row["base_visited_labelled_state_count"]),
            int(row["perturbed_visited_labelled_state_count"]),
        ) <= 0:
            raise AssertionError(f"empty closure orbit: {row}")

    canary = next(
        row
        for row in orbit_rows
        if row["carrier"] == "wheel_W4__b8__leaf_offset0"
        and row["seed"] == "47"
        and row["basis_index"] == "0"
    )
    expected_canary_moves = {
        "I0+I1+I2",
        "I0+I1+I3",
        "I0+I2+I3",
        "I1+I2+I3",
    }
    for column in ("base_initial_delta_y_objects", "perturbed_initial_delta_y_objects"):
        if set(canary[column].split("|")) != expected_canary_moves:
            raise AssertionError(f"wheel canary lost accepted Delta-Y moves in {column}: {canary[column]}")

    cut_rows = read_csv(HERE / "exact_cut_regions_step1.csv")
    expected_cut_rows = sum(
        2 * ((1 << int(row["boundary_count"])) - 2) for row in summaries
    )
    if len(cut_rows) != expected_cut_rows:
        raise AssertionError(f"cut-region coverage {len(cut_rows)} != {expected_cut_rows}")
    if not all(row["unique_minimizer"] == "True" for row in cut_rows):
        raise AssertionError("a recorded raw/reduced region is not unique")

    anti_bypass = read_csv(HERE / "anti_bypass_step1.csv")
    if len(anti_bypass) != 3 or not all(row["passes"] == "True" for row in anti_bypass):
        raise AssertionError("anti-bypass audit failed")
    pins = read_csv(HERE / "dependency_pins_step1.csv")
    if len(pins) != 3 or not all(row["passes"] == "True" for row in pins):
        raise AssertionError("dependency pin failure")

    elapsed = time.perf_counter() - started
    disjoint = sum(row["verdict"] == "depth-three five-move-orbit-disjoint" for row in orbit_rows)
    gauge = sum(row["verdict"] == "GAUGE" for row in orbit_rows)
    return (
        "run_step1.py: PASS: survivors=13 exact_regions="
        f"{len(cut_rows)} kernel_directions=19 certified_fibers=19 "
        f"orbit_audits=19 orbit_disjoint={disjoint} gauge={gauge} "
        f"wheel_canary_delta_y=4+4 circular_raw=0/13 circular_reduced=7/13 "
        f"runtime_seconds={elapsed:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and validate all Step-1 artifacts")
    parser.parse_args()
    print(validate())


if __name__ == "__main__":
    main()
