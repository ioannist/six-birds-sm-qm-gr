#!/usr/bin/env python3
"""Validator for the versioned S3-REPAIR-1b closure artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from fractions import Fraction
from pathlib import Path

import s3_construction_v2 as v2
from build_s3_generator_construction_v2 import render_artifacts


HERE = Path(__file__).resolve().parent


def validate() -> tuple[list[str], dict]:
    result = v2.run_v2()
    expected = render_artifacts(result)
    errors: list[str] = []

    for name, data in expected.items():
        path = HERE / name
        if not path.is_file():
            errors.append(f"missing artifact: {name}")
        elif path.read_bytes() != data:
            errors.append(f"artifact differs from exact recomputation: {name}")

    manifest_path = HERE / "artifact_manifest_v2.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text())
        for name, digest in manifest["files"].items():
            path = HERE / name
            if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                errors.append(f"sha256 mismatch: {name}")

    full = result["full_commutant"]
    f48 = result["f48"]
    su4 = result["su4_slice"]
    pati = result["pati_salam"]
    if (full["coefficient_count"], full["rank"], full["nullity"]) != (24, 23, 1):
        errors.append("full 24-direction commutant is not rank 23/nullity 1")
    if not full["off_diagonal_zero"] or full["primitive_diagonal"] != (-2, -2, -2, 3, 3):
        errors.append("derived full-commutant direction changed")
    if f48["columns"] != [(1, -1, 0, 0), (0, 1, -1, 0), (0, 0, 0, 1)]:
        errors.append("matrix-extracted coroot columns changed")
    if (f48["smith_invariants"], f48["free_rank_pi1_h"],
            f48["central_u1_loop_index"], f48["pi2_SU5_over_H"]) != ((1, 1, 1), 1, 6, "Z"):
        errors.append("F48 Smith/index/exact-sequence result changed")
    if (len(su4["mapped_roots"]), su4["charge_rescale"], su4["target_outside_slice"]) != (
            6, Fraction(5, 8), True):
        errors.append("SU4 six-root slice or non-invariance witness changed")
    if pati["sin2_trace_ratio"] != Fraction(3, 8):
        errors.append("Pati-Salam product-parent trace ratio changed")

    ledger = {row["claim"]: row["status"] for row in result["claim_status"]}
    required_ledger = {
        "step41 six-generator identity": "REFUTED-BY-CONSTRUCTION",
        "step41 fixed-slice analogue relation": "LANDED-BY-CONSTRUCTION",
        "product parent yields 3/23": "REMAINING-IMPORT",
    }
    if any(ledger.get(claim) != status for claim, status in required_ledger.items()):
        errors.append("required claim-ledger statuses changed")

    required_mutations = {
        "generic_SO5_conjugated_embedding",
        "corrupt_extracted_coroot",
        "zero_one_coset_action",
        "enlarge_SU4_fixed_slice_with_E04",
    }
    mutation_names = {row["mutation"] for row in result["mutation_tests"]}
    if len(result["mutation_tests"]) != 7 or any(row["result"] != "PASS" for row in result["mutation_tests"]):
        errors.append("mutation suite did not reject all seven mutations")
    if not required_mutations <= mutation_names:
        errors.append("one or more S3-REPAIR-1b mutation strata is missing")
    return errors, result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="recompute and verify all v2 artifacts")
    args = parser.parse_args()
    if not args.self:
        parser.error("this validator must be run with --self")

    started = time.monotonic()
    errors, result = validate()
    elapsed = time.monotonic() - started
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        raise SystemExit(1)

    f48, su4 = result["f48"], result["su4_slice"]
    print("S3-REPAIR-1b validator: PASS")
    print("full commutant: PASS (24 coefficients; rank=23; nullity=1)")
    print(f"F48 extracted lattice: PASS (SNF={f48['smith_invariants']}; index=6; pi2=Z)")
    print(f"SU4 fixed slice: PASS (six roots; rescale={su4['charge_rescale']}; outside-slice witness)")
    print("product-parent control: PASS (Pati-Salam trace ratio=3/8; no derived 3/23)")
    print("mutation tests: PASS (7/7 rejected, including conjugation/coroot/F27/slice tests)")
    print(f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
