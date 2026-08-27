#!/usr/bin/env python3
"""Deterministic rebuild-and-byte-compare validator for PROG2 Step 3."""

from __future__ import annotations

import argparse
import csv
import hashlib
import os
import tempfile
import time
from pathlib import Path


os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from build_step3 import HERE, generate


PREREGISTRATION_SHA256 = "5c46b7e87419ca3c1879ee2a4ead54219e44b2af01088f8dc14b321986194180"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> str:
    started = time.perf_counter()
    preregistration = HERE / "preregistration_step3.md"
    actual_preregistration_hash = hashlib.sha256(preregistration.read_bytes()).hexdigest()
    if actual_preregistration_hash != PREREGISTRATION_SHA256:
        raise AssertionError(
            f"frozen preregistration changed: {actual_preregistration_hash}"
        )

    with tempfile.TemporaryDirectory(prefix="prog2_step3_") as temporary:
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

    intersections = read_csv(HERE / "kernel_intersections_step3.csv")
    expected_members = {"R2_L1", "R2_L2", "C2_L1", "R3_S11", "R3_S21"}
    fiber_ids = {f"fiber_{index:03d}" for index in range(1, 20)}
    if (
        len(intersections) != 95
        or {row["fiber_id"] for row in intersections} != fiber_ids
        or {row["member_id"] for row in intersections} != expected_members
        or {
            (row["fiber_id"], row["member_id"]) for row in intersections
        }
        != {(fiber, member) for fiber in fiber_ids for member in expected_members}
    ):
        raise AssertionError("19 x 5 preregistered census incomplete")
    if not all(
        row["grade"] == "DENSE_NUMERICAL_EVIDENCE"
        and row["all_imported_basis_step_sweeps_stable"] == "True"
        for row in intersections
    ):
        raise AssertionError("grade or Jacobian stability gate failed")
    if any(
        int(row["intersection_dimension"]) != 0
        for row in intersections
        if row["tensor_family"] == "seeded_random_complex"
    ):
        raise AssertionError("unexpected seeded-random intersection")
    copy_rows = [row for row in intersections if row["member_id"] == "C2_L1"]
    if not all(
        int(row["intersection_dimension"])
        == int(row["exact_cut_kernel_dimension"]) - 1
        for row in copy_rows
    ):
        raise AssertionError("copy-product symmetry dimension mismatch")

    classifications = read_csv(HERE / "direction_classifications_step3.csv")
    unique_classifications = {
        (
            row["carrier"],
            row["source_seed_provenance"],
            row["member_id"],
            row["intersection_direction_index"],
        )
        for row in classifications
    }
    if len(classifications) != 14 or len(unique_classifications) != 6 or not all(
        row["classification"] == "SYMMETRY_PROTECTED"
        and row["member_id"] == "C2_L1"
        and row["continuation_eligible"] == "True"
        and row["exact_product_log_derivative"] == "0"
        and row["symmetry"]
        == "connected_copy_GHZ_product_P_equals_product_edge_capacities"
        for row in classifications
    ):
        raise AssertionError("nonzero direction typing failed")

    stability = read_csv(HERE / "direction_stability_step3.csv")
    if len(stability) != 95 or not all(row["stable"] == "True" for row in stability):
        raise AssertionError("three-step directional stability coverage failed")

    controls = read_csv(HERE / "controls_step3.csv")
    if len(controls) != 2 or not all(
        row["capacities_distinct"] == "True"
        and row["classifier_verdict"] == "COINCIDE"
        and row["state_level_classification"] == "STATE_LEVEL_GAUGE"
        and row["underdetermination_candidate"] == "False"
        and float(row["state_l2_residual"]) <= 5e-10
        and row["passes"] == "True"
        for row in controls
    ):
        raise AssertionError("distinct-capacity analytic controls failed")
    control_comparisons = read_csv(HERE / "control_entropy_comparisons_step3.csv")
    if len(control_comparisons) != 320 or not all(
        row["final_classification"] == "EQUAL_WITHIN_ALLOWANCE"
        for row in control_comparisons
    ):
        raise AssertionError("control entropy comparison census failed")

    convention_checks = read_csv(HERE / "convention_checks_step3.csv")
    if len(convention_checks) != 5 or not all(
        row["passes"] == "True" for row in convention_checks
    ):
        raise AssertionError("convention-family gates failed")
    anti_bypass = read_csv(HERE / "anti_bypass_step3.csv")
    if len(anti_bypass) != 5 or not all(row["passes"] == "True" for row in anti_bypass):
        raise AssertionError("anti-bypass inheritance failed")
    pins = read_csv(HERE / "dependency_pins_step3.csv")
    if len(pins) != 12 or not all(row["passes"] == "True" for row in pins):
        raise AssertionError("dependency pin failure")

    elapsed = time.perf_counter() - started
    nonzero_rows = sum(
        int(row["intersection_dimension"]) > 0 for row in intersections
    )
    return (
        "run_step3.py: PASS: preregistration=PINNED rows=95 fibers=19 "
        "members=5 seeded_random_trivial=76 copy_nonzero_rows="
        f"{nonzero_rows} protected_direction_records={len(classifications)} "
        f"distinct_protected_directions={len(unique_classifications)} "
        "direction_sweeps=95/95 controls=2/2 anti_bypass=5/5 "
        f"runtime_seconds={elapsed:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and recheck all Step-3 artifacts")
    parser.add_argument("--full", action="store_true", help="alias for the complete deterministic rebuild")
    parser.parse_args()
    print(validate())


if __name__ == "__main__":
    main()
