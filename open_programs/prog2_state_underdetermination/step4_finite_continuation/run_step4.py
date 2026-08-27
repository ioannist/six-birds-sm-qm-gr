#!/usr/bin/env python3
"""Rebuild validator for PROG2 Step-4 FIX2."""
from __future__ import annotations
import argparse, csv, hashlib, tempfile, time
from fractions import Fraction
from pathlib import Path
from build_step4 import HERE, generate

PINS = {"preregistration_step4.md": "aae1706428bf4140e26865444408cd980dabe91f3acdf7e32a77193b59c06b28",
        "preregistration_step4_corrective.md": "525bdc82a85359b1d6730e9032b0108aae0e763071909a14048d9b8cc3320b57",
        "generated_gauge_closure_fix2.md": "c19bad1691992d8ac91505c365372d998c15c997d6ae33dd46c0937d9a515850"}

def read_rows(name: str):
    with (HERE/name).open(newline="",encoding="utf-8") as handle: return list(csv.DictReader(handle))

def validate() -> str:
    started=time.perf_counter()
    for name,expected in PINS.items():
        actual=hashlib.sha256((HERE/name).read_bytes()).hexdigest()
        if actual != expected: raise AssertionError(f"frozen declaration changed: {name}: {actual}")
    with tempfile.TemporaryDirectory(prefix="prog2_step4_fix2_") as temporary:
        destination=Path(temporary); rebuilt=generate(destination)
        mismatch=[name for name in sorted(rebuilt) if not (HERE/name).exists()
                  or (HERE/name).read_bytes() != (destination/name).read_bytes()]
        if mismatch: raise AssertionError(f"artifact byte mismatch: {mismatch}")
    candidates=read_rows("candidate_outcomes_step4.csv")
    if len(candidates)!=6 or {r["candidate_id"] for r in candidates}!={f"cand_{i:02d}" for i in range(1,7)}:
        raise AssertionError("six-candidate census failed")
    if sorted(int(r["endpoint_number_field_degree"]) for r in candidates) != [2,2,2,2,2,5]:
        raise AssertionError("general number-field degree regression failed")
    if not all(
        Fraction(r["t_exact"])>0
        and Fraction(r["s_isolating_lower_exact"])<Fraction(r["s_isolating_upper_exact"])
        and Fraction(r["root_interval_width_exact"])<Fraction(1,10**70)
        and r["all_capacities_positive_rigorous"]=="True"
        and r["finite_range_coordinate_membership_rigorous"]=="True"
        and int(r["ordered_region_count"])==254 and int(r["all_cut_assignment_count"])>254
        and r["complete_fingerprint_equal_exact"]=="True" and r["unique_minimizers_displaced"]=="True"
        and Fraction(r["minimum_displaced_unique_cut_margin_lower_exact"])>0
        and float(r["dense_state_norm_difference"])<=5e-10
        and float(r["high_precision_sparse_contraction_state_difference"])<1e-70
        and r["entropy_vector_verdict"]=="COINCIDE"
        and r["connected_copy_state_equal_exact_analytic"]=="True"
        and r["boundary_state_equivalent"]=="True"
        and r["same_graph_terminal_fixed_automorphism_maps"]=="False"
        and r["combined_state_cap_per_endpoint"]=="64"
        and r["base_combined_orbit_saturated"]=="False"
        and r["displaced_combined_orbit_saturated"]=="False"
        and r["base_combined_budget_reason"]=="state_cap=64"
        and r["displaced_combined_budget_reason"]=="state_cap=64"
        and r["base_combined_orbit_state_count"]=="64"
        and r["displaced_combined_orbit_state_count"]=="64"
        and r["combined_orbit_intersection_count"]=="0"
        and r["combined_closure_verdict"]=="DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED"
        and r["capacity_invariant_status"]=="EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF"
        and r["typed_outcome"]=="PENDING_GENERATED_GAUGE_CLOSURE"
        and r["surviving_underdetermination_candidate"]=="False"
        for r in candidates):
        raise AssertionError("FIX2 candidate/combined-closure gate failed")
    canary=read_rows("reciprocal_first_canary_step4.csv")
    expected={3:(2,2),5:(4,4),6:(2,2),11:(4,4)}
    if len(canary)!=4 or {int(r["edge_index"]):(int(r["proposal_count"]),int(r["accepted_count"])) for r in canary}!=expected:
        raise AssertionError("cand_03 reciprocal-first canary failed")
    if not all(r["passes"]=="True" and "saturated_or_zero_column" in r["proposals"]
               and "inseparable_contraction" in r["proposals"] for r in canary):
        raise AssertionError("canary moves were not handled by the combined engine")
    obligations=read_rows("endpoint_obligations_step4.csv")
    pending=[r for r in obligations if r["status"]=="PENDING_GENERATED_GAUGE_CLOSURE"]
    if len(obligations)!=60 or len(pending)!=12 or not all(r["passes"]=="True" for r in obligations):
        raise AssertionError("obligation typing failed")
    if {r["obligation"] for r in pending}!={"combined_generated_gauge_closure","bulk_capacity_orbit_multiset_invariant"}:
        raise AssertionError("wrong obligations marked pending")
    attempts=read_rows("root_attempts_step4.csv")
    if len(attempts)!=6 or not all(r["attempt_index"]=="0" and r["selected"]=="True" for r in attempts):
        raise AssertionError("root selection changed")
    anti=read_rows("anti_bypass_step4.csv")
    if len(anti)!=6 or not all(r["passes"]=="True" for r in anti): raise AssertionError("anti-bypass failed")
    pins=read_rows("dependency_pins_step4.csv")
    if len(pins)!=16 or not all(r["passes"]=="True" for r in pins): raise AssertionError("pin gate failed")
    elapsed=time.perf_counter()-started
    return ("run_step4.py: PASS: declarations=PINNED exact_algebraic_endpoints=6/6 "
            "full_fingerprints=6/6 exact_copy_state_equalities=6/6 number_fields_general=6/6 "
            "combined_orbits=12/12 combined_state_caps_hit=12/12 explored_intersections=0/6 "
            "reciprocal_first_canary=4/4 pending_generated_gauge_obligations=12/12 "
            f"certified_surviving_candidates=0 runtime_seconds={elapsed:.3f}")

if __name__=="__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--self",action="store_true"); parser.parse_args()
    print(validate())
