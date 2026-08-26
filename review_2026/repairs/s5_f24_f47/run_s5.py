#!/usr/bin/env python3
"""Validate S5 by rebuilding every verdict and byte-comparing the artifacts."""

from __future__ import annotations

import argparse
import tempfile
import time
from pathlib import Path

import build_s5_f24_f47 as build


def self_validate() -> None:
    started = time.perf_counter()
    data = build.build_data()
    if not all(row["passes"] for row in data["controls"]):
        raise AssertionError("one or more S5 controls failed")
    firing = [row["family"] for row in data["baseline"] if row["status"] == "FIRES"]
    if firing != ["MemoryLayer", "BudgetedRole"]:
        raise AssertionError(f"real-carrier F24 verdict moved: {firing}")
    if data["schema"].get("memory_layer_closure_gate", {}).get("status") != "EXPERIMENTAL_INSUFFICIENT":
        raise AssertionError("MemoryLayer round-23 closure qualification missing")
    mutation_sets = data["schema"]["mutation_firing_families"]
    if mutation_sets != {
        "mutation_budget_decoupled": ["MemoryLayer"],
        "mutation_sealed_e0_scope": ["ScopedRole"],
    }:
        raise AssertionError(f"mutation firing sets moved: {mutation_sets}")
    if data["f47"]["realized_score"] != 2.75:
        raise AssertionError("realized-point boundary moved")

    with tempfile.TemporaryDirectory(prefix="s5_f24_f47_") as scratch:
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
    print(
        "run_s5.py: PASS: "
        f"firing={','.join(firing)} memory_gate=EXPERIMENTAL_INSUFFICIENT mutations=MemoryLayer|ScopedRole "
        f"headline={data['f47']['headline'][0]['selector_fraction']} "
        f"byte_compare={len(build.OUTPUT_FILES)} elapsed={elapsed:.3f}s"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        parser.error("--self is required")
    self_validate()


if __name__ == "__main__":
    main()
