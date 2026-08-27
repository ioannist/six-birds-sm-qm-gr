#!/usr/bin/env python3
"""Deterministic rebuild-and-byte-compare validator for PROG3 Step 2."""

from __future__ import annotations

import argparse
import csv
import tempfile
import time
from pathlib import Path

from build_step2 import HERE, generate
from saturation_engine import MOVE_CLASSES


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_census(text: str) -> dict[str, int]:
    result = {}
    for token in text.split("|"):
        name, value = token.split(":", 1)
        result[name] = int(value)
    if tuple(result) != MOVE_CLASSES:
        raise AssertionError(f"move-class census mismatch: {result}")
    return result


def validate() -> str:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="prog3_step2_") as temporary:
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

    fibers = read_csv(HERE / "fiber_saturation_step2.csv")
    endpoints = read_csv(HERE / "endpoint_saturation_step2.csv")
    if len(fibers) != 19 or len(endpoints) != 38:
        raise AssertionError(f"coverage mismatch: fibers={len(fibers)} endpoints={len(endpoints)}")
    for row in fibers:
        cross = int(row["cross_orbit_weighted_isomorphism_count"])
        both_saturated = row["base_saturated"] == row["perturbed_saturated"] == "True"
        if cross > 0:
            if not row["verdict"].startswith("GAUGE via path") or not row["path_if_gauge"]:
                raise AssertionError(f"missing gauge path for {row['fiber_id']}")
        elif both_saturated:
            if row["verdict"] != "complete five-move-orbit-disjoint (saturated)":
                raise AssertionError(f"wrong saturated verdict for {row['fiber_id']}")
        elif not row["verdict"].startswith("budget-truncated at"):
            raise AssertionError(f"budget truncation silently misclassified for {row['fiber_id']}")
        parse_census(row["base_accepted_move_census"])
        parse_census(row["perturbed_accepted_move_census"])

    for row in endpoints:
        canonical_count = int(row["canonical_state_count"])
        if canonical_count <= 0:
            raise AssertionError(f"empty endpoint orbit: {row}")
        if row["saturated"] == "True":
            if row["budget_truncated"] != "False" or row["budget_reason"]:
                raise AssertionError(f"saturated endpoint carries a budget failure: {row}")
        else:
            if row["budget_truncated"] != "True" or not row["budget_reason"]:
                raise AssertionError(f"unsaturated endpoint lacks a budget reason: {row}")
        if (
            int(row["fingerprint_full_recheck_count"]) != canonical_count
            or row["all_admitted_fingerprints_equal"] != "True"
            or row["all_weights_exact_fraction"] != "True"
        ):
            raise AssertionError(f"endpoint fingerprint/exactness audit failed: {row}")
        accepted = parse_census(row["accepted_move_census"])
        novel = parse_census(row["novel_state_census"])
        if any(novel[name] > accepted[name] for name in MOVE_CLASSES):
            raise AssertionError(f"novel-state census exceeds accepted transitions: {row}")

    fingerprint = read_csv(HERE / "fingerprint_invariance_step2.csv")
    if len(fingerprint) != 38 or not all(
        row["all_states_rechecked"] == "True"
        and row["all_complete_terminal_fingerprints_equal"] == "True"
        and row["all_weights_exact_fraction"] == "True"
        and row["canonical_state_count"] == row["full_exact_recheck_count"]
        for row in fingerprint
    ):
        raise AssertionError("full fingerprint invariance coverage failed")

    canary = next(row for row in fibers if row["fiber_id"] == "fiber_001")
    expected_canary_census = {
        "series": 0,
        "two_terminal_module": 0,
        "saturated_or_zero_column": 0,
        "inseparable_contraction": 0,
        "delta_y_y_delta": 8,
    }
    if (
        int(canary["base_canonical_state_count"]) != 5
        or int(canary["perturbed_canonical_state_count"]) != 5
        or int(canary["base_max_replacement_depth"]) != 1
        or int(canary["perturbed_max_replacement_depth"]) != 1
        or parse_census(canary["base_accepted_move_census"]) != expected_canary_census
        or parse_census(canary["perturbed_accepted_move_census"]) != expected_canary_census
    ):
        raise AssertionError("wheel canary saturation regression changed")

    structural = read_csv(HERE / "structural_audit_step2.csv")
    if len(structural) != 5 or not all(row["passes"] == "True" for row in structural):
        raise AssertionError("structural saturation audit failed")
    dependencies = read_csv(HERE / "dependency_pins_step2.csv")
    if len(dependencies) != 6 or not all(row["passes"] == "True" for row in dependencies):
        raise AssertionError("dependency pin failure")

    saturated_endpoints = sum(row["saturated"] == "True" for row in endpoints)
    disjoint = sum(
        row["verdict"] == "complete five-move-orbit-disjoint (saturated)"
        for row in fibers
    )
    gauge = sum(row["verdict"].startswith("GAUGE via path") for row in fibers)
    truncated = sum(row["verdict"].startswith("budget-truncated") for row in fibers)
    maximum_depth = max(int(row["max_replacement_depth"]) for row in endpoints)
    state_counts = [int(row["canonical_state_count"]) for row in endpoints]
    elapsed = time.perf_counter() - started
    return (
        "run_step2.py: PASS: fibers=19 endpoints=38 "
        f"saturated_endpoints={saturated_endpoints} complete_disjoint={disjoint} "
        f"gauge={gauge} budget_truncated={truncated} canonical_states_range="
        f"{min(state_counts)}-{max(state_counts)} max_replacement_depth={maximum_depth} "
        f"recorded_canonical_state_coverage={sum(state_counts)} runtime_seconds={elapsed:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and validate every saturation artifact")
    parser.parse_args()
    print(validate())


if __name__ == "__main__":
    main()
