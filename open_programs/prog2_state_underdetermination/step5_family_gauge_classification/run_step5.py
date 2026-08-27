#!/usr/bin/env python3
"""Deterministic rebuild validator for PROG2 Step 5."""
from __future__ import annotations
import argparse,csv,tempfile,time
from pathlib import Path
from build_step5 import HERE,generate

EXPECTED_RATIO="70406080269220304893479166685119/8728637932116993396730243442760"
STEP4_RESULTS=HERE.parent/"step4_finite_continuation"/"results_step4.md"
GRADE_SENTENCE="No finiteness theorem or finite completeness bound is known; all twelve searches exceed the frozen 64-state exploration budget."

def rows(name: str):
    with (HERE/name).open(newline="",encoding="utf-8") as handle:return list(csv.DictReader(handle))

def validate() -> str:
    started=time.perf_counter()
    if GRADE_SENTENCE not in STEP4_RESULTS.read_text(encoding="utf-8"):
        raise AssertionError("Step-4 grade sentence missing")
    with tempfile.TemporaryDirectory(prefix="prog2_step5_") as temporary:
        destination=Path(temporary);rebuilt=generate(destination)
        mismatch=[name for name in sorted(rebuilt) if not (HERE/name).exists()
                  or (HERE/name).read_bytes()!=(destination/name).read_bytes()]
        if mismatch:raise AssertionError(f"artifact byte mismatch: {mismatch}")
    local=rows("local_copy_parity_step5.csv")
    if [int(r["tensor_rank"]) for r in local]!=[2,3,4,5] or not all(
        int(r["canonical_return_subset_count"])==2 and r["canonical_return_masks"]==r["expected_masks"]
        and r["passes"]=="True" for r in local):raise AssertionError("local copy parity lemma failed")
    global_rows=rows("global_copy_parity_step5.csv")
    if len(global_rows)!=6 or not all(r["connected"]=="True"
        and r["family_returning_assignment_count"]=="2"
        and r["family_returning_masks"]==r["expected_masks"] and r["passes"]=="True" for r in global_rows):
        raise AssertionError("connected global parity propagation failed")
    counter=rows("delta_y_countercheck_step5.csv")
    if len(counter)!=1 or not (counter[0]["candidate_id"]=="cand_01"
        and counter[0]["triangle"]=="I0+I1+I2"
        and counter[0]["complete_cut_fingerprint_equal_exact"]=="True"
        and counter[0]["copy_product_ratio_exact"]==EXPECTED_RATIO
        and counter[0]["copy_product_ratio_not_one_exact"]=="True"
        and counter[0]["state_gauge_admitted"]=="False" and counter[0]["passes"]=="True"):
        raise AssertionError("Delta-Y cut/state countercheck failed")
    classifications=rows("classification_step5.csv")
    if len(classifications)!=6 or {r["candidate_id"] for r in classifications}!={f"cand_{i:02d}" for i in range(1,7)}:
        raise AssertionError("classification census failed")
    if not all(r["terminal_fixed_direct_isomorphism"]=="False"
        and r["base_isomorphic_to_global_reciprocal_displaced"]=="False"
        and r["displaced_isomorphic_to_global_reciprocal_base"]=="False"
        and r["base_step1_series_reduction_count"]=="0" and r["base_step1_parallel_reduction_count"]=="0"
        and r["displaced_step1_series_reduction_count"]=="0" and r["displaced_step1_parallel_reduction_count"]=="0"
        and r["invariant_differs_exact"]=="True"
        and r["classification"]=="SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE"
        and r["example_earned"]=="True" and r["base_invariant_exact"]!=r["displaced_invariant_exact"]
        for r in classifications):raise AssertionError("exact six-pair family classification failed")
    proofs=rows("invariant_generator_proofs_step5.csv")
    if len(proofs)!=5 or not all(r["passes"]=="True" for r in proofs):
        raise AssertionError("generator-by-generator invariant proof ledger failed")
    pins=rows("dependency_pins_step5.csv")
    if len(pins)!=6 or not all(r["passes"]=="True" for r in pins):raise AssertionError("dependency pin failed")
    elapsed=time.perf_counter()-started
    return ("run_step5.py: PASS: declaration=PINNED parity_local_ranks=4/4 "
            "parity_connected_carriers=6/6 delta_y_cut_only_countercheck=PASS "
            "terminal_fixed_comparisons=6/6 global_reciprocal_comparisons=12/12 "
            "step1_merge_nonapplicability=12/12 invariant_generator_proofs=5/5 "
            f"surviving_examples=6 explicit_gauge_collapses=0 runtime_seconds={elapsed:.3f}")

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--self",action="store_true");parser.parse_args();print(validate())
