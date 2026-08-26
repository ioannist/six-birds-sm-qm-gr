#!/usr/bin/env python3
"""Validate S1-REPAIR-3 typed singleton and two-scalar artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import inspect
import json
import sys
import time
from pathlib import Path

import build_s1_carrier_reconstruction_v3 as build
import carrier_chain_v3 as v3


HERE = Path(__file__).resolve().parent
REQUIRED = {
    "DESIGN.md", "DESIGN_v3.md", "carrier_chain_v3.py", "build_s1_carrier_reconstruction_v3.py",
    "run_s1_carrier_reconstruction_v3.py", "s1_v3_singleton_scalar_branches.csv",
    "s1_v3_singleton_scalar_coverage.csv", "s1_v3_two_scalar_pair_branches.csv",
    "s1_v3_two_scalar_pair_coverage.csv", "s1_v3_charge_normalization_census.csv",
    "s1_v3_independent_scalar_alphabet.csv", "s1_v3_tensor_product_singlets.csv",
    "s1_v3_tensor_product_golden.csv", "s1_v3_independent_gate.csv",
    "s1_v3_schema.json", "RESULTS_v3.md", "s1_v3_artifact_manifest.json",
}


def fail(message: str) -> None:
    print(f"run_s1_carrier_reconstruction_v3.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_keys(filename: str, fields: tuple[str, ...]) -> set[tuple[str, ...]]:
    with (HERE / filename).open(newline="", encoding="utf-8") as handle:
        return {tuple(row[field] for field in fields) for row in csv.DictReader(handle)}


def validate() -> dict:
    missing = sorted(name for name in REQUIRED if not (HERE / name).is_file())
    if missing:
        fail(f"missing files: {missing}")

    result = v3.run_v3()
    expected = build.assemble_artifacts(result)
    for name, text in expected.items():
        if (HERE / name).read_text(encoding="utf-8") != text:
            fail(f"artifact differs from full in-memory recomputation: {name}")

    schema = json.loads(expected["s1_v3_schema.json"])
    expected_singleton = {
        "chirality_faithful_structures": 52,
        "admissible_singleton_branches": 12,
        "structures_with_singleton_branch": 8,
        "structures_without_singleton_branch": 44,
        "clean_singleton_branches": 4,
    }
    if schema["singleton_counts"] != expected_singleton:
        fail(f"unexpected singleton census: {schema['singleton_counts']}")
    expected_pairs = {
        "admissible_pair_branches": 2824,
        "admissible_pair_branch_orbits": 829,
        "structures_with_pair_branch": 52,
        "formerly_singleton_none_acquiring_pair": 44,
        "clean_pair_branches": 68,
        "clean_pair_branch_orbits": 17,
        "clean_pair_structures": 4,
        "clean_pairs_outside_2x3_su2_only": 0,
    }
    if schema["two_scalar_appendix_counts"] != expected_pairs:
        fail(f"unexpected two-scalar census: {schema['two_scalar_appendix_counts']}")
    expected_charge = {
        "genuinely_chiral": {"labelled": 1066, "declared_orbits": 419,
                             "primitive_normalized_orbits": 195},
        "atomic_packaging": {"labelled": 84, "declared_orbits": 37,
                             "primitive_normalized_orbits": 37},
        "closure_consistency": {"labelled": 62, "declared_orbits": 27,
                                "primitive_normalized_orbits": 27},
        "chirality_faithfulness": {"labelled": 52, "declared_orbits": 24,
                                   "primitive_normalized_orbits": 24},
    }
    if schema["charge_normalization_counts"] != expected_charge:
        fail(f"unexpected charge-normalization census: {schema['charge_normalization_counts']}")

    independent_singletons = result["exact_singleton_keys"]
    written_singletons = read_keys(
        "s1_v3_singleton_scalar_branches.csv", ("structure_id", "singleton_scalar_branch")
    )
    if independent_singletons != written_singletons:
        fail("independent exact-decomposition singleton key set differs from written table")
    expected_pair_keys = {(row.structure_id, row.pair_branch) for row in result["pair_branches"]}
    written_pair_keys = read_keys(
        "s1_v3_two_scalar_pair_branches.csv", ("structure_id", "two_scalar_pair_branch")
    )
    if expected_pair_keys != written_pair_keys:
        fail("written two-scalar table is missing or duplicating a pair branch")

    # Load-bearing independence audit. These are the complete functions on the
    # gate call path between the declared table and singleton branch keys.
    gate_functions = (
        v3.independent_rep_assignments,
        v3.independent_scalar_alphabet,
        v3.singlet_decomposition,
        v3.independent_yukawa_allowed,
        v3.scalar_coverage_mask,
        v3.independent_singleton_branch_keys,
    )
    forbidden = ("neutral_rep_assignments", "scalar_representations", "factor_invariant", "yukawa_invariant")
    for function in gate_functions:
        source = inspect.getsource(function)
        hits = [name for name in forbidden if f".{name}(" in source]
        if hits:
            fail(f"independent gate function {function.__name__} calls production helpers: {hits}")

    gate = schema["independent_gate"]
    if not gate["singleton_key_sets_equal"] or gate["independent_singleton_key_count"] != 12:
        fail(f"independent singleton gate failed: {gate}")
    if gate["tensor_triple_count"] != 368 or gate["tensor_golden_pass_count"] != gate["tensor_golden_count"]:
        fail(f"tensor-product gate failed: {gate}")

    with (HERE / "s1_v3_two_scalar_pair_branches.csv").open(newline="", encoding="utf-8") as handle:
        pair_rows = list(csv.DictReader(handle))
    outside = [row for row in pair_rows if row["clean_or_breaking"] == "clean"
               and not (row["dimensions"] == "2|3" and row["active_factor_indices"] == "0")]
    if outside:
        fail(f"clean two-scalar branches escaped the typed family: {outside[:3]}")

    manifest = json.loads(expected["s1_v3_artifact_manifest.json"])
    for name, digest in manifest["files"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != digest:
            fail(f"artifact manifest mismatch: {name}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="recompute and validate all v3 artifacts")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    started = time.monotonic()
    result = validate()
    elapsed = time.monotonic() - started
    print("run_s1_carrier_reconstruction_v3.py: PASS: "
          "singleton=12 singleton_none=44 independent_gate=12/12 tensor=368 golden=14/14 "
          f"pairs={len(result['pair_branches'])} pair_structures=52 new_pair_structures=44 "
          f"clean_pairs={len(result['clean_pair_branches'])} clean_outside_typed_family=0 "
          "charge_orbits=419/195->24 elapsed_seconds=" + f"{elapsed:.3f}")


if __name__ == "__main__":
    main()
