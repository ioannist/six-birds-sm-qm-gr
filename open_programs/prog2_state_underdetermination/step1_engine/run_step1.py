#!/usr/bin/env python3
"""Complete validator for PROG2 Step 1."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
import time
from pathlib import Path


os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from build_step1 import HERE, generate
from step1_core import TENSOR_REPLICATE, TENSOR_SEED_NAMESPACE, derive_tensor_seed


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> str:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="prog2_step1_") as temporary:
        rebuilt_dir = Path(temporary)
        rebuilt = generate(rebuilt_dir)
        mismatches = []
        for name in sorted(rebuilt):
            live = HERE / name
            if not live.exists() or live.read_bytes() != (rebuilt_dir / name).read_bytes():
                mismatches.append(name)
        if mismatches:
            raise AssertionError(f"artifact byte mismatch: {mismatches}")

    controls = read_csv(HERE / "control_summary_step1.csv")
    if len(controls) != 2 or not all(row["passes"] == "True" for row in controls):
        raise AssertionError("two calibration controls did not both pass")
    if float(controls[0]["max_entropy_vector_difference"]) < 0.69:
        raise AssertionError("injective control lost discriminatory power")
    if float(controls[1]["max_entropy_vector_difference"]) > 2e-12:
        raise AssertionError("degeneracy control entropy mismatch")

    gauges = read_csv(HERE / "gauge_verifications_step1.csv")
    expected_moves = {
        "internal_leg_g_g_inverse",
        "series_tensor_merge",
        "parallel_index_product_merge",
        "single_boundary_local_unitary",
    }
    if {row["move"] for row in gauges} != expected_moves:
        raise AssertionError("gauge library coverage mismatch")
    if not all(row["passes"] == "True" for row in gauges):
        raise AssertionError("a gauge verification failed")
    boundary_unitary = next(
        row for row in gauges if row["move"] == "single_boundary_local_unitary"
    )
    if (
        boundary_unitary["nonsymmetric_complex_unitary"] != "True"
        or boundary_unitary["independent_expected_contraction"]
        != "np.einsum('ij,jb->ib', U, psi)"
    ):
        raise AssertionError("conventional nonsymmetric boundary-unitary regression failed")

    engine_checks = read_csv(HERE / "engine_checks_step1.csv")
    if len(engine_checks) != 1 or engine_checks[0]["passes"] != "True":
        raise AssertionError("heterogeneous-dimension engine check failed")
    heterogeneous = engine_checks[0]
    if (
        heterogeneous["edge_dimensions"] != "2|3"
        or heterogeneous["boundary_dimensions"] != "2|3"
        or heterogeneous["contracted_state_shape"] != "2x3"
        or int(heterogeneous["entropy_subset_count"]) != 4
    ):
        raise AssertionError("heterogeneous-dimension coverage changed")

    anti_bypass = read_csv(HERE / "anti_bypass_step1.csv")
    if len(anti_bypass) != 10 or not all(row["passes"] == "True" for row in anti_bypass):
        raise AssertionError("anti-bypass structural audit failed")

    review_regressions = read_csv(HERE / "review_regressions_step1.csv")
    expected_regressions = {
        "source_seed_independence_mutation",
        "small_schmidt_weight_tolerance_sweep",
        "nonsymmetric_complex_boundary_unitary_left_action",
    }
    if (
        {row["regression"] for row in review_regressions} != expected_regressions
        or not all(row["passes"] == "True" for row in review_regressions)
    ):
        raise AssertionError("reviewer regression suite failed")

    seed_regression = read_csv(HERE / "seed_independence_regression_step1.csv")
    if len(seed_regression) != 1 or seed_regression[0]["passes"] != "True":
        raise AssertionError("source provenance mutation regression failed")
    if (
        seed_regression[0]["baseline_state_sha256"]
        != seed_regression[0]["mutated_state_sha256"]
        or seed_regression[0]["baseline_entropy_sha256"]
        != seed_regression[0]["mutated_entropy_sha256"]
    ):
        raise AssertionError("source provenance entered state or entropy dataflow")

    numerical = read_csv(HERE / "entropy_numerical_accountability_step1.csv")
    if len(numerical) != 5 or not all(
        row["passes"] == "True" and row["bound_covers_observed_error"] == "True"
        for row in numerical
    ):
        raise AssertionError("small-Schmidt tolerance sweep failed")
    threshold_row = next(
        row for row in numerical if float(row["probability_tolerance"]) == 1e-13
    )
    if (
        float(threshold_row["reported_untruncated_entropy_nats"]) <= 3e-13
        or int(threshold_row["numerical_rank"]) != 1
        or not (0.9e-14 <= float(threshold_row["discarded_probability_mass"]) <= 1.1e-14)
        or float(threshold_row["truncation_entropy_error_bound_nats"])
        < float(threshold_row["observed_truncation_error_nats"])
    ):
        raise AssertionError("small Schmidt probability was silently erased")

    survivor_scale = read_csv(HERE / "survivor_scale_control_step1.csv")
    if (
        len(survivor_scale) != 1
        or survivor_scale[0]["passes"] != "True"
        or int(survivor_scale[0]["boundary_count"]) < 6
        or float(survivor_scale[0]["maximum_entropy_vector_difference"]) <= 1e-6
        or survivor_scale[0]["base_entropy_sha256"]
        == survivor_scale[0]["mutated_entropy_sha256"]
    ):
        raise AssertionError("survivor-scale same-boundary control failed")

    census = read_csv(HERE / "survivor_tractability_step1.csv")
    carrier_keys = {(row["carrier"], row["source_seed"]) for row in census}
    if len(carrier_keys) != 13:
        raise AssertionError(f"expected 13 survivor carriers, found {len(carrier_keys)}")
    if len(census) != 52:
        raise AssertionError(f"expected 52 survivor family/dimension rows, found {len(census)}")
    if not all(row["tractable"] == "True" for row in census):
        raise AssertionError("a declared survivor census row was not tractable")
    if not all(int(row["entropy_subset_count"]) == 1 << int(row["boundary_count"]) for row in census):
        raise AssertionError("an entropy vector omitted boundary subsets")
    if not all(float(row["complement_symmetry_residual"]) <= 2e-11 for row in census):
        raise AssertionError("pure-state complement symmetry failed")
    random_rows = [row for row in census if row["tensor_family"] == "seeded_random_complex"]
    if len(random_rows) != 39:
        raise AssertionError("random survivor census coverage changed")
    for row in random_rows:
        expected_seed = derive_tensor_seed(
            row["carrier"], int(row["bond_dimension"]), TENSOR_REPLICATE
        )
        if (
            row["tensor_seed_namespace"] != TENSOR_SEED_NAMESPACE
            or int(row["tensor_seed"]) != expected_seed
            or row["entropy_digest_changed_from_legacy"] != "True"
            or row["entropy_digest_changed_from_legacy_seed_same_policy"] != "True"
            or row["state_digest_changed_from_legacy_seed"] != "True"
        ):
            raise AssertionError(
                f"independent tensor-seed namespace failed for {row['carrier']}"
            )
    seed_changes = read_csv(HERE / "seed_namespace_change_step1.csv")
    if len(seed_changes) != 39 or not all(
        row["entropy_digest_changed"] == "True"
        and row["entropy_digest_changed_same_policy"] == "True"
        and row["state_digest_changed"] == "True"
        and row["legacy_pre_fix_entropy_vector_sha256"] != row["new_entropy_vector_sha256"]
        and row["legacy_seed_corrected_entropy_vector_sha256"] != row["new_entropy_vector_sha256"]
        and row["legacy_state_sha256"] != row["new_state_sha256"]
        for row in seed_changes
    ):
        raise AssertionError("legacy/new seed digest audit failed")
    for carrier_key in carrier_keys:
        rows = [row for row in census if (row["carrier"], row["source_seed"]) == carrier_key]
        random_dims = {
            int(row["bond_dimension"])
            for row in rows
            if row["tensor_family"] == "seeded_random_complex"
        }
        structured_dims = {
            int(row["bond_dimension"])
            for row in rows
            if row["tensor_family"] == "structured_copy"
        }
        if random_dims != {2, 3, 4} or structured_dims != {2}:
            raise AssertionError(f"tractability coverage mismatch for {carrier_key}")

    elapsed = time.perf_counter() - started
    return (
        "run_step1.py: PASS: controls=3 gauge_moves=4 engine_checks=1 anti_bypass=10 "
        "regressions=3(seed_independence,small_schmidt,nonsymmetric_unitary) "
        f"survivors=13 census_rows=52 runtime_seconds={elapsed:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and validate all Step-1 artifacts")
    parser.parse_args()
    print(validate())


if __name__ == "__main__":
    main()
