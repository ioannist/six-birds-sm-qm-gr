#!/usr/bin/env python3
"""Validator for the S6 dimension-generic record-grammar ablation."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import build_s6_record_grammar_ablation as build
import record_grammar_ablation as core


HERE = Path(__file__).resolve().parent
REQUIRED = {
    "DESIGN.md", "record_grammar_ablation.py", "build_s6_record_grammar_ablation.py",
    "run_s6_record_grammar_ablation.py", "s6_branch_scores.csv",
    "s6_neutral_record_tokens.csv", "s6_generic_grammar_table.csv",
    "s6_structure_quantifiers.csv", "s6_threshold_sensitivity.csv",
    "s6_threshold_quantifiers.csv", "s6_counterexamples.csv",
    "s6_dependency_pins.csv", "s6_schema.json", "RESULTS.md",
    "s6_artifact_manifest.json",
}


def fail(message: str) -> None:
    print(f"run_s6_record_grammar_ablation.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate() -> dict:
    missing = sorted(name for name in REQUIRED if not (HERE / name).is_file())
    if missing:
        fail(f"missing files: {missing}")

    result = core.run_ablation()
    expected = build.assemble_artifacts(result)
    for name, text in expected.items():
        if (HERE / name).read_text(encoding="utf-8") != text:
            fail(f"artifact differs from full in-memory recomputation: {name}")

    if not all(row["passes"] and row["expected_sha256"] == row["actual_sha256"]
               for row in result["pins"]):
        fail("one or more S1-v2 dependency pins failed")
    schema = json.loads(expected["s6_schema.json"])
    if schema["carrier"] != {
        "chirality_faithful_structures": 52,
        "admissible_singleton_branch_rows": 12,
        "no_singleton_substrate_fail_rows": 44,
        "evaluation_rows": 56,
    }:
        fail(f"carrier typing changed: {schema['carrier']}")
    expected_reference = {
        "RS_branches": 8,
        "RS_clean": 4,
        "RS_breaking": 4,
        "counterexamples": 4,
        "two_by_three_SU2_active_RS": 4,
        "SU4_RS": 0,
        "pointwise_implication": False,
        "universal_implication": False,
        "existential_implication": True,
    }
    if schema["reference_threshold_result"] != expected_reference:
        fail(f"reference-threshold result changed: {schema['reference_threshold_result']}")
    if schema["threshold_one_result"] != {
        "RS_branches": 12, "RS_breaking": 8, "SU4_RS_breaking_counterexamples": 4,
    }:
        fail(f"threshold-one result changed: {schema['threshold_one_result']}")

    no_branch = [row for row in result["scores"] if row["branch_scope"] == "no_singleton_branch"]
    if len(no_branch) != 44 or any(row["stable_substrate"] or row["record_stability_passes"]
                                   or row["clean_classification"] != "undefined_no_singleton_branch"
                                   for row in no_branch):
        fail("no-singleton structures are not consistently typed substrate-fail/undefined")
    if len(result["counterexamples"]) != 4 or any(
        row["dimensions"] != "2|3"
        or row["branch_scope"] != "singleton_active_SU(3)"
        or row["clean_classification"] != "breaking_evaluated"
        for row in result["counterexamples"]
    ):
        fail("reference counterexample membership changed")

    token_classes = {row["token_class"] for row in result["tokens"]}
    if token_classes != {"mesonic", "baryonic", "mixed"}:
        fail(f"generic token bases are incomplete: {token_classes}")
    if set(core.projected_representation_weights("fund", 2)) != {-1, 1}:
        fail("SU(2) component splitting is not derived from actual weights")
    su4_baryons = [row for row in result["tokens"]
                   if row["substrate_dimension"] == 4 and row["token_class"] == "baryonic"]
    if not su4_baryons or any(row["epsilon_or_pair_arity"] != 4 for row in su4_baryons):
        fail("SU(4) epsilon basis is not four-fold")
    if core.rm.conjugate_rep("antisym2", 4) != "antisym2":
        fail("actual SU(4) antisym2 conjugacy was not preserved")

    thresholds = {row["threshold"]: row for row in result["threshold_sensitivity"]}
    if thresholds[3]["rs_branch_count"] or thresholds[4]["rs_branch_count"]:
        fail("threshold-three/four implications are not vacuous as recorded")

    manifest = json.loads(expected["s6_artifact_manifest.json"])
    for name, digest in manifest["files"].items():
        actual = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        if actual != digest:
            fail(f"artifact manifest mismatch: {name}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="recompute and validate every S6 artifact")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    started = time.monotonic()
    result = validate()
    elapsed = time.monotonic() - started
    print("run_s6_record_grammar_ablation.py: PASS: "
          "pins=3/3 rows=56 tokens=68 classes=mesonic|baryonic|mixed "
          "RS_t2=8 clean_RS_t2=4 breaking_RS_t2=4 counterexamples_t2=4 "
          "SU2_active_RS_t2=4 SU4_RS_t2=0 SU4_RS_t1=4 "
          "quantifiers_t2=pointwise_FAIL|universal_FAIL|existential_PASS "
          f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
