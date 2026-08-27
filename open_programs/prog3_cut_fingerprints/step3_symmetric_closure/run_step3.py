#!/usr/bin/env python3
"""Deterministic rebuild-and-byte-compare validator for PROG3 Step 3."""

from __future__ import annotations

import argparse
import csv
import tempfile
import time
from pathlib import Path

from build_step3 import HERE, generate
from step3_core import FLOOR_VERDICT, UPGRADE_VERDICT


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def require_true(row: dict[str, str], *fields: str) -> None:
    failed = [field for field in fields if row[field] != "True"]
    if failed:
        raise AssertionError(f"false gates {failed}: {row}")


def validate() -> str:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="prog3_step3_") as temporary:
        rebuilt_dir = Path(temporary)
        rebuilt = generate(rebuilt_dir)
        mismatches = [
            name
            for name in sorted(rebuilt)
            if not (HERE / name).exists()
            or (HERE / name).read_bytes() != (rebuilt_dir / name).read_bytes()
        ]
        if mismatches:
            raise AssertionError(f"artifact byte mismatch: {mismatches}")

    fibers = read_csv(HERE / "fiber_forward_floor_step3.csv")
    if len(fibers) != 19:
        raise AssertionError(f"fiber coverage mismatch: {len(fibers)}")
    if not all(
        row["floor_verdict"] == FLOOR_VERDICT
        and row["symmetric_series_delta_upgrade_verdict"] == UPGRADE_VERDICT
        and row["forward_cross_isomorphism_count"] == "0"
        and int(row["base_forward_canonical_state_count"]) > 0
        and int(row["perturbed_forward_canonical_state_count"]) > 0
        for row in fibers
    ):
        raise AssertionError("forward-floor or upgrade typing regression")

    census = read_csv(HERE / "transition_census_step3.csv")
    expected = {
        "series": ("reduction_only", 0, 0),
        "two_terminal_module": ("reduction_only", 0, 0),
        "saturated_or_zero_column": ("reduction_only", 0, 0),
        "inseparable_contraction": ("reduction_only", 0, 0),
        "delta_y_y_delta": ("bidirectional", 100, 50),
    }
    actual = {
        row["move_class"]: (
            row["directionality_in_step2"],
            int(row["accepted_transition_count"]),
            int(row["novel_canonical_state_count"]),
        )
        for row in census
    }
    if actual != expected:
        raise AssertionError(f"transition census mismatch: {actual}")

    witness_rows = read_csv(HERE / "external_witness_step3.csv")
    if len(witness_rows) != 1:
        raise AssertionError("external witness coverage mismatch")
    witness = witness_rows[0]
    require_true(
        witness,
        "fingerprint_equal_exact",
        "expanded_unique",
        "series_reduces_to_endpoint",
        "reduced_fingerprint_equal_exact",
        "absent_from_step2_forward_set",
    )
    if (
        witness["series_composition_rule"] != "min(a,b)"
        or witness["original_capacity_exact"] != witness["composed_capacity_exact"]
        or int(witness["forward_endpoint_state_count"]) != 5
    ):
        raise AssertionError(f"inverse-series regression changed: {witness}")

    l1 = read_csv(HERE / "l1_series_certificates_step3.csv")
    if len(l1) != 13:
        raise AssertionError(f"L1 coverage mismatch: {len(l1)}")
    for row in l1:
        require_true(
            row,
            "fingerprint_equal_exact",
            "expanded_unique",
            "left_then_right_normal_form_is_endpoint",
            "right_then_left_normal_form_is_endpoint",
            "normal_forms_equal",
        )
        if row["certificate"] != "PROVED_AND_CERTIFIED_ON_ACTUAL_CARRIER":
            raise AssertionError(f"L1 typing changed: {row}")

    l2_rows = read_csv(HERE / "l2_counterexample_step3.csv")
    if len(l2_rows) != 1:
        raise AssertionError("L2 counterexample coverage mismatch")
    l2 = l2_rows[0]
    require_true(
        l2,
        "expanded_fingerprint_equal_exact",
        "expanded_unique",
        "post_move_fingerprint_equal_exact",
        "post_move_unique",
        "direct_fingerprint_equal_exact",
        "direct_unique",
        "delta_only_projection_impossible_by_edge_count",
    )
    if (
        l2["fiber_id"] != "fiber_008"
        or l2["lemma_outcome"] != "FAILED_L2_SUBDIVIDED_Y_LEG_CASE"
        or l2["subdivision_degree_after_y_delta"] != "3"
        or l2["normal_forms_terminal_fixed_isomorphic"] != "False"
        or l2["expanded_normal_form_in_reduced_delta_forward_set"] != "False"
        or int(l2["expanded_normal_form_edge_count"])
        <= int(l2["direct_normal_form_edge_count"])
    ):
        raise AssertionError(f"L2 obstruction regression changed: {l2}")

    lemmas = read_csv(HERE / "lemma_outcomes_step3.csv")
    outcomes = {row["lemma"]: row["outcome"] for row in lemmas}
    if outcomes != {
        "L1_SERIES_NORMAL_FORM_ON_ADMISSIBLE_HOMEOMORPHIC_EXPANSIONS": "PROVED_AND_CERTIFIED",
        "L2_SERIES_DELTA_Y_COHERENCE": "FAILED",
        "L3_SYMMETRIC_SERIES_DELTA_ORBIT_DISJOINTNESS": "NOT_REACHED_BECAUSE_L2_FAILED",
    }:
        raise AssertionError(f"lemma typing mismatch: {outcomes}")

    controls = read_csv(HERE / "negative_controls_step3.csv")
    expected_controls = {
        "A_SHARED_ENDPOINT_REJECTS_DISJOINT_FLOOR": (
            "FLOOR_REJECTED",
            "NONEMPTY_FORWARD_SET_INTERSECTION",
        ),
        "B_L2_EDGE_MUTATION_BREAKS_FINGERPRINT": (
            "FINGERPRINT_EQUALITY_REJECTED",
            "EXACT_FINGERPRINT_CHANGED",
        ),
        "C_INTERIOR_RELABEL_IS_RECOGNIZED": (
            "WEIGHTED_ISOMORPHISM_ACCEPTED",
            "TERMINAL_FIXED_WEIGHTED_ISOMORPHISM_RECOGNIZED",
        ),
        "D_EQUAL_ACTIVE_SPLIT_FAILS_UNIQUENESS": (
            "UNIQUE_MINIMIZER_ADMISSION_REJECTED",
            "ACTIVE_CUT_HAS_TWO_SUBDIVISION_SIDE_MINIMIZERS",
        ),
        "E_NON_SERIES_REDUCED_BASE_REDUCES_PAST_ITSELF": (
            "STARTING_PRESENTATION_REJECTED_AS_NORMAL_FORM",
            "NONTERMINAL_BIVALENT_BASE_IS_NOT_ITS_NORMAL_FORM",
        ),
    }
    if len(controls) != 5 or {row["control_id"] for row in controls} != set(expected_controls):
        raise AssertionError(f"can-fail control coverage mismatch: {controls}")
    for row in controls:
        expected_classification, expected_reason = expected_controls[row["control_id"]]
        if (
            row["passes"] != "True"
            or row["expected_classification"] != expected_classification
            or row["observed_classification"] != expected_classification
            or row["expected_reason"] != expected_reason
            or row["observed_reason"] != expected_reason
        ):
            raise AssertionError(
                f"can-fail control did not fail/pass for its specified reason: {row}"
            )

    dependencies = read_csv(HERE / "dependency_pins_step3.csv")
    if len(dependencies) != 9 or not all(row["passes"] == "True" for row in dependencies):
        raise AssertionError("dependency/evidence pin failure")

    elapsed = time.perf_counter() - started
    control_lines = [
        "run_step3.py: CONTROL PASS: "
        f"{row['control_id']} classification={row['observed_classification']} "
        f"reason={row['observed_reason']} {row['metric']}={row['value']}"
        for row in controls
    ]
    pass_line = (
        "run_step3.py: PASS: fibers=19 forward_disjoint=19 controls=5/5 "
        "external_inverse_series_regression=PASS l1=PROVED_AND_CERTIFIED(13) "
        "l2=FAILED_EXACT_SUBDIVIDED_Y_LEG_CASE l3=NOT_REACHED "
        f"runtime_seconds={elapsed:.3f}"
    )
    return "\n".join(control_lines + [pass_line])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and validate every Step-3 artifact")
    parser.parse_args()
    print(validate())


if __name__ == "__main__":
    main()
