#!/usr/bin/env python3
"""Validate S1-REPAIR-1 by rerunning the complete chain in memory."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import build_s1_carrier_reconstruction as build
import carrier_chain as chain
import representation_model as rm


ARTIFACT_DIR = Path(__file__).resolve().parent
REQUIRED_FILES = {
    "DESIGN.md",
    "representation_model.py",
    "carrier_chain.py",
    "build_s1_carrier_reconstruction.py",
    "run_s1_carrier_reconstruction.py",
    "s1_stage_flow.csv",
    "s1_survivor_families.csv",
    "s1_final_family.csv",
    "s1_old_vs_new.csv",
    "s1_representation_self_test.csv",
    "s1_schema.json",
    "RESULTS.md",
}


def fail(message: str) -> None:
    print(f"run_s1_carrier_reconstruction.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def validate() -> None:
    started = time.monotonic()
    missing = sorted(name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).is_file())
    if missing:
        fail(f"missing files: {missing}")

    rep_test = rm.self_test()
    if not rep_test["passes"]:
        fail(f"representation-model consistency gate failed: {rep_test['failed_checks']}")

    result = chain.run_chain()
    expected = build.assemble_artifacts(result)
    for name, expected_text in expected.items():
        actual = (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        if actual != expected_text:
            fail(f"artifact differs from full in-memory recomputation: {name}")

    schema = json.loads(expected["s1_schema.json"])
    expected_counts = {
        "neutral_carrier": 281241820,
        "genuinely_chiral": 1066,
        "atomic_packaging": 84,
        "closure_consistency": 62,
        "chirality_faithfulness": 52,
        "higher_layer_mass_closure_proxy": 8,
        "clean_separation": 4,
    }
    if schema["stage_counts"] != expected_counts:
        fail(f"unexpected reconstructed trajectory: {schema['stage_counts']}")
    conclusion = schema["conclusion"]
    for required in (
        "six_vs_zero_survives",
        "two_three_and_su4_to_clean_two_three_survives",
        "target_passes_clean_separation",
        "step38_step41_faithful",
    ):
        if conclusion[required] is not True:
            fail(f"required conclusion check failed: {required}")
    if schema["window"]["truncated"] is not False:
        fail("carrier must not be truncated")

    for name, expected_hash in schema["artifact_sha256"].items():
        actual_hash = sha256_text((ARTIFACT_DIR / name).read_text(encoding="utf-8"))
        if actual_hash != expected_hash:
            fail(f"artifact hash mismatch: {name}")

    elapsed = time.monotonic() - started
    print(
        "run_s1_carrier_reconstruction.py: PASS: "
        f"rep_model=PASS checks={rep_test['check_count']} "
        f"rows={schema['stage_counts']['genuinely_chiral']} "
        f"clean={schema['stage_counts']['clean_separation']} "
        f"elapsed_seconds={elapsed:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rerun and validate the complete chain")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    validate()


if __name__ == "__main__":
    main()
