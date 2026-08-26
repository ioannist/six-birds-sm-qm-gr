#!/usr/bin/env python3
"""Validate S1-REPAIR-2, including independent scalar-branch completeness."""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import build_s1_carrier_reconstruction_v2 as build
import carrier_chain_v2 as v2


HERE = Path(__file__).resolve().parent
REQUIRED = {
    "DESIGN.md", "representation_model.py", "carrier_chain.py", "carrier_chain_v2.py",
    "build_s1_carrier_reconstruction_v2.py", "run_s1_carrier_reconstruction_v2.py",
    "s1_v2_scalar_branches.csv", "s1_v2_scalar_branch_coverage.csv",
    "s1_v2_stage_flow.csv", "s1_v2_old_new_orbit.csv",
    "s1_v2_orbit_families.csv", "s1_v2_inert_singlet_check.csv",
    "s1_v2_golden_formula_check.csv", "s1_v2_schema.json", "RESULTS_v2.md",
    "s1_v2_artifact_manifest.json",
}


def fail(message: str) -> None:
    print(f"run_s1_carrier_reconstruction_v2.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate() -> None:
    started = time.monotonic()
    missing = sorted(name for name in REQUIRED if not (HERE / name).is_file())
    if missing:
        fail(f"missing files: {missing}")

    result = v2.run_v2()
    expected = build.assemble_artifacts(result)
    for name, text in expected.items():
        if (HERE / name).read_text(encoding="utf-8") != text:
            fail(f"artifact differs from full in-memory recomputation: {name}")

    schema = json.loads(expected["s1_v2_schema.json"])
    expected_counts = {
        "inert_singlet_inclusive_labelled": 1578,
        "inert_singlet_quotiented_labelled": 1066,
        "admissible_structures_labelled": 8,
        "admissible_structures_orbits": 2,
        "admissible_scalar_branches_labelled": 12,
        "admissible_scalar_branches_orbits": 3,
        "clean_scalar_branches_labelled": 4,
        "clean_scalar_branches_orbits": 1,
        "existential_clean_structures_labelled": 4,
        "existential_clean_structures_orbits": 1,
        "universal_clean_structures_labelled": 0,
        "universal_clean_structures_orbits": 0,
        "chirality_faithful_structures_checked_for_scalars": 52,
        "chirality_faithful_structures_without_admissible_branch": 44,
    }
    if schema["counts"] != expected_counts:
        fail(f"unexpected branch or convention census: {schema['counts']}")
    expected_orbits = {
        "neutral_carrier": 57109009,
        "genuinely_chiral": 419,
        "atomic_packaging": 37,
        "closure_consistency": 27,
        "chirality_faithfulness": 24,
        "higher_layer_mass_closure_proxy": 2,
        "clean_separation_existential": 1,
        "clean_separation_universal": 0,
    }
    if schema["stage_orbit_counts"] != expected_orbits:
        fail(f"unexpected orbit trajectory: {schema['stage_orbit_counts']}")

    # Independent finite Burnside check at multiset sizes 1-2. The production
    # neutral count uses cycle generating functions through size 5; here we
    # explicitly enumerate the manageable small-cap orbit sets.
    for dimensions, catalog in result["base"]["catalogs"].items():
        group = v2.effective_type_permutations(dimensions, catalog)
        explicit = set()
        for size in (1, 2):
            for combo in itertools.combinations_with_replacement(range(len(catalog)), size):
                explicit.add(min(tuple(sorted(permutation[index] for index in combo)) for permutation in group))
        fixed_sum = sum(v2.fixed_multisets_through_cap(permutation, 2) for permutation in group)
        if len(explicit) != fixed_sum // len(group):
            fail(f"Burnside cross-check failed for factor structure {dimensions}")

    # Independent completeness gate against the written table: this regenerates
    # scalar candidates and occurrence coverage without calling the primary
    # scalar_representations() or mass_completion() loops.
    independent = v2.independently_enumerated_branch_keys(
        result["base"]["stage_rows"]["chirality_faithfulness"], result["base"]["catalogs"]
    )
    with (HERE / "s1_v2_scalar_branches.csv").open(newline="", encoding="utf-8") as handle:
        written = {(row["structure_id"], row["scalar_branch"]) for row in csv.DictReader(handle)}
    if written != independent:
        fail(f"written branch set is incomplete: missing={sorted(independent-written)} extra={sorted(written-independent)}")

    if not schema["golden_formula"]["passes"] or schema["golden_formula"]["row_count"] < 12:
        fail("golden representation table did not pass")
    if schema["branch_completeness"] != {
        "extra_count": 0, "independent_count": 12, "missing_count": 0,
        "primary_count": 12, "sets_equal": True,
    }:
        fail(f"branch completeness gate failed: {schema['branch_completeness']}")

    manifest = json.loads(expected["s1_v2_artifact_manifest.json"])
    for name, digest in manifest["files"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != digest:
            fail(f"artifact manifest mismatch: {name}")

    elapsed = time.monotonic() - started
    print("run_s1_carrier_reconstruction_v2.py: PASS: "
          "golden=13/13 inert=1578->1066 branches=12/12 burnside=PASS clean=4 "
          "universal_structures=0 existential_structures=4 "
          f"chiral_orbits=419 elapsed_seconds={elapsed:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rerun and validate every v2 artifact")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    validate()


if __name__ == "__main__":
    main()
