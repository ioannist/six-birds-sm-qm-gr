#!/usr/bin/env python3
"""Full in-memory/byte validator for Q2-REPAIR-1."""

from __future__ import annotations

import argparse
import math
import time
from pathlib import Path

import build_q2_route_mismatch as build
import q2_route_mismatch as core


HERE = Path(__file__).resolve().parent


def validate() -> dict:
    result = core.run()
    for name, payload in build.render(result).items():
        path = HERE / name
        if not path.is_file() or path.read_bytes() != payload:
            raise AssertionError(f"full rebuild byte mismatch: {name}")
    if not all(row["passes"] and row["expected_sha256"] == row["actual_sha256"]
               for row in result["pins"]):
        raise AssertionError("dependency pin failure")
    if any(not row["left_idempotent"] or not row["right_idempotent"]
           for row in result["candidates"]):
        raise AssertionError("completion idempotence failure")
    rows = {row["pair_id"]: row for row in result["candidates"]}
    expected = {
        "published_coordinate_pair": (True, 0, 0.0),
        "conditional_mean_vs_nonlinear_source_projection": (False, 16, 1.0),
        "nonfactorizing_conditional_means": (False, 12, math.sqrt(3) / 4),
        "nested_coordinate_control": (True, 0, 0.0),
    }
    for pair_id, (commutes, cardinality, norm) in expected.items():
        row = rows[pair_id]
        if (row["commutes"] != commutes or row["defect_set_cardinality"] != cardinality
                or abs(row["commutator_spectral_norm"] - norm) > 1e-12):
            raise AssertionError(f"candidate result changed: {row}")
    published = {row["encoding"]: row for row in result["published"]}
    if not (abs(published["zero_one"]["completion_table_distance_normalized"] - 0.5) < 1e-12
            and abs(published["plus_minus_one"]["completion_table_distance_normalized"]
                    - 1 / math.sqrt(2)) < 1e-12
            and all(row["commutator_defect_cardinality"] == 0
                    and row["commutator_on_encoded_table_norm"] == 0 for row in published.values())):
        raise AssertionError(f"published reproduction changed: {published}")
    if any(not row["recoding_rebuilt_matrices_equal"]
           or not row["recoding_defect_cardinality_equal"]
           or not row["recoding_norm_invariant"] or not row["conjugacy_invariance_passes"]
           or row["coordinate_permutations_checked"] != 24
           for row in result["invariance"]):
        raise AssertionError("encoding or coordinate-permutation invariance failure")
    defects = {}
    for row in result["defects"]:
        defects.setdefault(row["pair_id"], set()).add(row["state"])
    if len(defects["conditional_mean_vs_nonlinear_source_projection"]) != 16:
        raise AssertionError("nonlinear exact defect set incomplete")
    if len(defects["nonfactorizing_conditional_means"]) != 12:
        raise AssertionError("nonfactor partition exact defect set incomplete")
    if result["outcome"] != "GENUINE_NONCOMMUTING_FINITE_CANDIDATES_EXIST_MOTIVATION_SUBJECT_TO_REVIEW":
        raise AssertionError(f"outcome changed: {result['outcome']}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        raise SystemExit("run_q2.py: FAIL: use --self")
    started = time.perf_counter()
    result = validate()
    print("run_q2.py: PASS: pins=2/2 pairs=4 idempotent=8/8 "
          "published=commutes|distance_0.5_to_1/sqrt2 nonlinear=defects16|norm1 "
          "nonfactor=defects12|norm_sqrt3/4 control=commutes invariance=4/4x24 "
          f"elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
