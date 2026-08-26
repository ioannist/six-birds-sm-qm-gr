#!/usr/bin/env python3
"""Full in-memory and byte validator for Q1-REPAIR-1."""

from __future__ import annotations

import argparse
import time
from pathlib import Path
from typing import Any

import build_q1_access_provenance as build
import q1_access_provenance as core


HERE = Path(__file__).resolve().parent


def find_key(value: Any, forbidden: str) -> bool:
    if isinstance(value, dict):
        return forbidden in value or any(find_key(item, forbidden) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(find_key(item, forbidden) for item in value)
    return False


def validate() -> dict[str, Any]:
    result = core.run()
    for name, payload in build.render(result).items():
        path = HERE / name
        if not path.is_file() or path.read_bytes() != payload:
            raise AssertionError(f"full rebuild byte mismatch: {name}")
    if len(result["pins"]) != 7 or any(not row["passes"] for row in result["pins"]):
        raise AssertionError("dependency pin failure")

    provenance = result["provenance"]
    if provenance["population_size"] != 54 or not provenance["access_split_realized"]:
        raise AssertionError(f"field provenance changed: {provenance}")
    if provenance["d0_observed_values"] != [1]:
        raise AssertionError("normalization-sector declaration changed")
    if provenance["step28_potential_recompute_max_residual"] > 1e-12:
        raise AssertionError("Step28 potential provenance residual too large")
    checks = {row.get("check", row.get("control")): row for row in result["provenance_checks"]}
    expected_factorization = {
        "born_audit_determines_d1": True,
        "born_audit_determines_d3": False,
        "q_QM_determines_d1": True,
        "q_QM_determines_d3": False,
        "geometry_readout_determines_d3": True,
        "q_GR_determines_d3": True,
        "q_GR_determines_d1": False,
        "q_QM_determines_q_GR": False,
        "q_GR_determines_q_QM": False,
    }
    for name, expected in expected_factorization.items():
        if checks[name]["factors"] is not expected:
            raise AssertionError(f"provenance factorization changed: {checks[name]}")
    phase = checks["complex_conjugate_phase_only"]
    if not (phase["same_density_mode"] and phase["same_geometry_mode"]
            and phase["phase_mode_differs"] and phase["same_q_GR_fiber"]):
        raise AssertionError(f"phase-only control failed: {phase}")
    potential = checks["potential_only"]
    if not (potential["same_density_mode"] and potential["same_q_QM_fiber"]
            and potential["geometry_mode_differs"]):
        raise AssertionError(f"potential-only control failed: {potential}")

    partitions = result["partition_summary"]
    expected_partitions = {
        "carrier_state_count": 16,
        "partition_count": 16,
        "distinct_unordered_pair_count": 120,
        "incomparable_pair_count": 55,
        "nested_pair_count": 65,
        "meet_join_closure_count": 16,
        "q_QM_q_GR_relation": "incomparable",
        "q_QM_q_GR_directed_defects": [8, 8],
    }
    for name, expected in expected_partitions.items():
        if partitions[name] != expected:
            raise AssertionError(f"partition exhaustion changed: {name}={partitions[name]}")
    if len(result["partition_pairs"]) != 120:
        raise AssertionError("partition pair table incomplete")
    if any(row["meet"] not in {item["partition_id"] for item in result["partitions"]}
           or row["join"] not in {item["partition_id"] for item in result["partitions"]}
           for row in result["partition_pairs"]):
        raise AssertionError("meet/join closure table invalid")

    competitors = {row["family"]: row for row in result["competitors"]}
    expected_status = {
        "MemoryLayer": (True, "reconciles_but_partition_equivalent_to_L"),
        "HiddenUpstreamRole": (False, "fails_endpoint_control"),
        "BridgeMediatedRole": (True, "reconciles_but_partition_equivalent_to_L"),
        "BudgetedRole": (False, "fails_endpoint_control"),
        "ScopedRole": (False, "fails_endpoint_control"),
        "CoarsenedRole": (False, "fails_endpoint_control"),
        "OutsideRoleScope": (False, "fails_endpoint_control"),
        "BlockedNonClosure": (False, "blocked_nonclosure"),
        "FusedDuplicateControl": (False, "fails_no_smuggle"),
    }
    if set(competitors) != set(expected_status):
        raise AssertionError("generated competitor class incomplete")
    for family, (reconciles, status) in expected_status.items():
        row = competitors[family]
        recomputed = row["G_stability"] and row["G_control_QM"] and row["G_control_GR"] and row["G_audit"] and row["G_nosmuggle"]
        if row["reconciles"] != recomputed or row["reconciles"] != reconciles or row["computed_status"] != status:
            raise AssertionError(f"competitor verdict not load-bearing: {row}")
    if competitors["FusedDuplicateControl"]["duplicate_column_pairs"] != "0-3;2-4":
        raise AssertionError("fused duplicate control lost its duplicate witnesses")
    if result["competitor_summary"]["distinct_reconciling_families"]:
        raise AssertionError("unexpected distinct reconciling map")
    if find_key(result, "verdict"):
        raise AssertionError("literal verdict field introduced; statuses must derive from maps")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        raise SystemExit("run_q1.py: FAIL: use --self")
    started = time.perf_counter()
    result = validate()
    elapsed = time.perf_counter() - started
    print(
        "run_q1.py: PASS: "
        "pins=7/7 population=54 access_split=REALIZED "
        "phase_control=pass potential_control=pass "
        "partitions=16 pairs=120 incomparable=55 nested=65 closure=16 "
        "qQM_qGR=INCOMPARABLE defects=8/8 "
        "competitors=9 reconciles=2 distinct=0 fused_duplicate=detected "
        f"elapsed_seconds={elapsed:.3f}"
    )


if __name__ == "__main__":
    main()
