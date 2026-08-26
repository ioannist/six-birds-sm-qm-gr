#!/usr/bin/env python3
"""Validate the S4 repair by rebuilding all computed artifacts in memory."""

from __future__ import annotations

import argparse
import tempfile
import time
from pathlib import Path

import build_s4_content_quotient as build


def self_validate() -> None:
    started = time.perf_counter()
    data = build.build_data()
    if not all(row["passes"] for row in data["controls"]):
        raise AssertionError("one or more load-bearing S4 controls failed")
    mutation_controls = {
        row["control"]: row for row in data["controls"] if row["control"].startswith("quotient_mutation_")
    }
    if set(mutation_controls) != {
        "quotient_mutation_identity_or_sign_only",
        "quotient_mutation_declared_global_action",
        "quotient_mutation_forbidden_per_field_conjugation_rejected",
    } or not all(row["passes"] for row in mutation_controls.values()):
        raise AssertionError(f"quotient mutation coverage failure: {mutation_controls}")
    with tempfile.TemporaryDirectory(prefix="s4_content_quotient_") as scratch:
        scratch_dir = Path(scratch)
        build.write_outputs(data, scratch_dir)
        mismatches = [
            name
            for name in build.OUTPUT_FILES
            if (build.ARTIFACT_DIR / name).read_bytes() != (scratch_dir / name).read_bytes()
        ]
    if mismatches:
        raise AssertionError(f"artifact byte mismatch after in-memory rebuild: {mismatches}")
    elapsed = time.perf_counter() - started
    n_status = ",".join(
        f"{row['N']}:{row['full_actual_chain_with_existential_branch']}" for row in data["n_rows"]
    )
    print(
        "run_s4.py: PASS: "
        f"28_labelled_to_{data['quotient']['orbit_count']}_orbits selected=1 "
        f"quotient_mutations=28/14/forbidden-rejected "
        f"N_full_chain={n_status} byte_compare={len(build.OUTPUT_FILES)} elapsed={elapsed:.3f}s"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild, check controls, and byte-compare all artifacts")
    args = parser.parse_args()
    if not args.self:
        parser.error("--self is required")
    self_validate()


if __name__ == "__main__":
    main()
