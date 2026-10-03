#!/usr/bin/env python3
"""Full in-memory/byte validator for S6-ABLATION-3."""

from __future__ import annotations

import argparse
import time
from collections import defaultdict
from pathlib import Path

import build_s6_record_grammar_ablation_v3 as build
import record_grammar_ablation_v3 as core


HERE = Path(__file__).resolve().parent


def fail(message: str) -> None:
    raise AssertionError(message)


def validate() -> dict:
    result = core.run()
    expected = build.render(result)
    for name, payload in expected.items():
        path = HERE / name
        if not path.is_file() or path.read_bytes() != payload:
            fail(f"full rebuild byte mismatch: {name}")
    if not all(row["passes"] and row["expected_sha256"] == row["actual_sha256"]
               for row in result["pins"]):
        fail("dependency pin failure")
    if result["bounds"] != {"fermion_arity_min": 2, "fermion_arity_max": 4,
                            "scalar_insertion_max": 2, "total_constituent_cap": 6}:
        fail(f"search bounds changed: {result['bounds']}")
    if len(result["lifts"]) != 556 or len(result["operators"]) != 404:
        fail("bounded lift/operator census changed")
    if any(row["uv_u1_charge"] or row["residual_u1_charge"]
           or row["uv_singlet_multiplicity"] < 1
           or row["residual_singlet_multiplicity"] < 1
           for row in result["lifts"]):
        fail("candidate lift failed a separate UV/residual singlet or charge gate")
    regression = result["eval_049_regression"][0]
    if not (regression["regression_passes"] and regression["required_operator_found"]
            and regression["uv_charge_equation"] == "(-2)+(4)+(-2)=0"
            and regression["residual_charge_equation"] == "(-3)+(3)=0"
            and regression["required_operator_uv_singlet_multiplicity"] == 1
            and regression["required_operator_residual_singlet_multiplicity"] == 1
            and not regression["v1_spectator_cartan_token_survives_v3"]
            and regression["spectator_cartan_coefficient"] == 0):
        fail(f"mandatory eval_049 regression failed: {regression}")
    by_evaluation = defaultdict(list)
    for row in result["operators"]:
        by_evaluation[row["evaluation_id"]].append(row)
    for census in result["census"]:
        operators = by_evaluation[census["evaluation_id"]]
        undressed = sum(row["has_undressed_lift"] for row in operators)
        dressed = sum(row["has_dressed_lift"] for row in operators)
        new = sum(row["has_dressed_lift"] and not row["has_undressed_lift"] for row in operators)
        if (undressed, dressed, new, len(operators)) != (
                census["undressed_operator_count"], census["operators_with_dressed_lift_count"],
                census["dressed_new_operator_count"], census["inclusive_quotient_operator_count"]):
            fail(f"census recomputation failed: {census['evaluation_id']}")
    clean = [row for row in result["census"] if row["clean_classification"] == "clean_evaluated"]
    if len(clean) != 4 or any(not row["clean_branch_gains_dressed_tokens"]
                              or row["dressed_new_operator_count"] != 18 for row in clean):
        fail("clean-branch scalar-dressing mirror check changed")
    for threshold in result["thresholds"]:
        if (threshold["rs_branch_count"], threshold["rs_clean_count"],
                threshold["rs_breaking_count"], threshold["counterexample_count"]) != (12, 4, 8, 8):
            fail(f"threshold sensitivity changed: {threshold}")
    q2 = [row for row in result["quantifiers"] if row["threshold"] == 2]
    expected_counterexamples = {
        "branch_pointwise": 8, "structure_universal": 8, "structure_existential": 4,
    }
    if len(q2) != 6 or any(row["implication_passes"] or row["vacuous"]
                           or row["counterexample_count"] != expected_counterexamples[row["quantifier_reading"]]
                           for row in q2):
        fail(f"threshold-two quantifier table changed: {q2}")
    if result["outcome"] != "COUNTEREXAMPLES_PERSIST_SCALAR_DRESSED_COMPLETE_BOUNDED_CENSUS":
        fail(f"outcome derivation changed: {result['outcome']}")
    if [(row["rs_branch_count"], row["counterexample_count"],
         row["pointwise_implication_passes"]) for row in result["outcome_ruling"]] != [
            (4, 0, True), (12, 8, False), (12, 8, False)]:
        fail(f"three-way outcome ruling changed: {result['outcome_ruling']}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        raise SystemExit("run_s6_record_grammar_ablation_v3.py: FAIL: use --self")
    started = time.perf_counter()
    result = validate()
    regression = result["eval_049_regression"][0]
    print(f"run_s6_record_grammar_ablation_v3.py: PASS: pins=1/1 lifts={len(result['lifts'])} "
          f"operators={len(result['operators'])} eval_049_dressed={regression['required_operator_found']} "
          "spectator_token=False conventions=undressed_only|dressed_inclusive "
          f"counterexamples_t2=8|8 elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
