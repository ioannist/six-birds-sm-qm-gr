#!/usr/bin/env python3
"""Full in-memory/byte validator for S6-ABLATION-2."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import build_s6_record_grammar_ablation_v2 as build
import record_grammar_ablation_v2 as core


HERE = Path(__file__).resolve().parent


def fail(message: str) -> None:
    print(f"run_s6_record_grammar_ablation_v2.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate() -> dict:
    result = core.run()
    expected = build.assemble(result)
    for name, text in expected.items():
        path = HERE / name
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            fail(f"full rebuild byte mismatch: {name}")
    if not all(row["passes"] and row["actual_sha256"] == row["expected_sha256"] for row in result["pins"]):
        fail("dependency pin failure")
    if len(result["stabilizers"]) != 12 or any(
        row["neutrality_lhs"] != 0 or row["spectator_cartans_in_u1"] != 0
        for row in result["stabilizers"]
    ):
        fail("stabilizer/neutrality assertion failed")
    group_counts = {}
    for row in result["stabilizers"]:
        group_counts[row["residual_group"]] = group_counts.get(row["residual_group"], 0) + 1
    expected_groups = {
        "SU(3)[spectator_f1] x U(1)_res": 4,
        "SU(2)[spectator_f0] x SU(2)[reduced_f1] x U(1)_res": 4,
        "SU(3)[reduced_f0] x U(1)_res": 4,
    }
    if group_counts != expected_groups:
        fail(f"residual-group census changed: {group_counts}")
    if any(row["residual_u1_charge"] != 0 or row["residual_singlet_multiplicity"] < 1 for row in result["tokens"]):
        fail("a written token is not a verified full-residual invariant")
    if {row["token_class"] for row in result["tokens"]} != {"mesonic", "baryonic", "mixed"}:
        fail("token class coverage incomplete")
    t2 = next(row for row in result["thresholds"] if row["threshold"] == 2)
    if (t2["rs_branch_count"], t2["rs_clean_count"], t2["rs_breaking_count"],
            t2["counterexample_count"], t2["implication_passes"], t2["vacuous"]) != (4, 4, 0, 0, True, False):
        fail(f"reference implication changed: {t2}")
    t1 = next(row for row in result["thresholds"] if row["threshold"] == 1)
    if (t1["rs_branch_count"], t1["rs_breaking_count"], t1["counterexample_count"]) != (12, 8, 8):
        fail(f"threshold-one sensitivity changed: {t1}")
    trace = result["eval_049_trace"][0]
    if not (trace["old_token_count"] == 2 and trace["full_residual_neutral_token_count"] == 1
            and trace["spectator_doublet_token_disappears"] and not trace["record_stability_threshold_2"]):
        fail(f"eval_049 trace changed: {trace}")
    if not all(row["control_passes"] and not row["distinguishability_passes"]
               for row in result["collision_controls"]):
        fail("collision control did not fail distinguishability")
    schema = json.loads(expected["s6_v2_schema.json"])
    if schema["outcome"] != "IMPLICATION_RESTORED_POINTWISE_FULL_RESIDUAL_NEUTRAL_GRAMMAR":
        fail(f"unexpected outcome: {schema['outcome']}")
    manifest = json.loads(expected["s6_v2_artifact_manifest.json"])
    for name, digest in manifest["files"].items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != digest:
            fail(f"manifest mismatch: {name}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    started = time.monotonic()
    result = validate()
    t2 = next(row for row in result["thresholds"] if row["threshold"] == 2)
    print("run_s6_record_grammar_ablation_v2.py: PASS: "
          "pins=5/5 stabilizers=12 neutrality=12/12 spectator_cartans=0 "
          f"tokens={len(result['tokens'])} RS_t2={t2['rs_branch_count']} "
          f"clean_t2={t2['rs_clean_count']} counterexamples_t2={t2['counterexample_count']} "
          "quantifiers=pointwise_PASS_nonvacuous|universal_PASS_vacuous|existential_PASS_nonvacuous "
          f"elapsed_seconds={time.monotonic()-started:.3f}")


if __name__ == "__main__":
    main()
