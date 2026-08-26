#!/usr/bin/env python3
"""Full in-memory and byte validator for Q7-REPAIR-1."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent


def load_core():
    path = HERE / "q7_f50_convergence.py"
    spec = importlib.util.spec_from_file_location("q7_validator_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import Q7 core")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fail(message: str) -> None:
    print(f"run_q7.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def validate() -> tuple[dict, list[dict]]:
    q7 = load_core()
    primary = q7.compute(q7.CAP, include_stability=True)
    doubled = q7.compute(q7.DOUBLE_CAP, include_stability=False)
    budget = q7.budget_comparison(primary, doubled)
    expected = q7.render(primary, budget)
    for name, payload in expected.items():
        path = HERE / name
        if not path.is_file() or path.read_bytes() != payload:
            fail(f"full rebuild byte mismatch: {name}")
    if not all(row["passes"] and row["expected_sha256"] == row["actual_sha256"]
               for row in primary["pins"]):
        fail("frozen dependency pin failure")
    if len(primary["cases"]) != 360 or len(primary["grid"]) != 120:
        fail("adaptive grid dimensions changed")
    if not all(row["classification_unchanged"] for row in budget):
        fail("doubling the iteration cap changes a classification")
    summary = primary["summary"]
    if summary["case_classifications"] != {"converged": 335, "cycling": 24, "stagnated": 1}:
        fail(f"classification census changed: {summary['case_classifications']}")
    if (summary["legacy_60_pass_count"], summary["legacy_120_pass_count"]) != (15, 18):
        fail("legacy budget regression was not reproduced")
    if not summary["all_background_solutions_exist"] or summary["all_background_fixed_points_linearly_stable"]:
        fail("background existence/stability typing changed")
    backgrounds = [row for row in primary["stability"] if row["sweep"] == "background"]
    unstable_offsets = {row["parameter"] for row in backgrounds if not row["fixed_map_linearly_stable"]}
    if unstable_offsets != {5.0, 8.0, 10.0}:
        fail(f"unexpected unstable background offsets: {unstable_offsets}")
    branches = primary["fixed_point_branches"]
    background_branches = [row for row in branches if row["sweep"] == "background"]
    minus_eight = [row for row in background_branches if row["parameter"] == -8.0]
    if len(branches) != 32 or len(background_branches) != 20 or len(minus_eight) != 3:
        fail("phase-invariant fixed-point branch census changed")
    if not all(row["map_residual"] < q7.TOL and row["max_member_ray_gap"] < 1e-6
               for row in branches):
        fail("a discovered fixed-point branch lacks a converged representative")
    if not all(row["fixed_map_linearly_stable"] for row in minus_eight):
        fail("offset -8 multistability result changed")
    if summary["max_mix_0_2_initial_solution_spread"] < 1.3:
        fail("three-initial-state probe no longer resolves the offset -8 attractors")
    if not summary["all_kappa_solutions_exist"] or not summary["genuine_fixed_map_stability_boundary"]:
        fail("kappa existence/stability result changed")
    boundary = primary["boundary"]
    if not (5.8674 < boundary["estimated_kappa"] < 5.8676
            and abs(boundary["boundary_rho"] - 1.0) < 2e-8
            and abs(boundary["leading_eigenvalue_real"] + 1.0) < 2e-8):
        fail(f"kappa boundary evidence changed: {boundary}")
    bg_boundary = primary["background_boundary"]
    if not (3.6534 < bg_boundary["estimated_offset"] < 3.6537
            and abs(bg_boundary["boundary_rho"] - 1.0) < 2e-8):
        fail(f"background boundary evidence changed: {bg_boundary}")
    mix02 = [row for row in primary["cases"] if row["mix"] == 0.2]
    if len(mix02) != 90 or any(row["classification"] != "converged" for row in mix02):
        fail("mix=0.2 does not remove the solver convergence boundary")
    if summary["supported_outcome"] != "MIXED_ALL_BACKGROUND_SOLUTIONS_EXIST_THREE_RAW_MAP_UNSTABLE_AND_KAPPA_STABILITY_BOUNDARY":
        fail(f"outcome derivation changed: {summary['supported_outcome']}")
    return primary, budget


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    started = time.perf_counter()
    primary, budget = validate()
    print("run_q7.py: PASS: pins=2/2 cases=360 grid=120 legacy=15/18@60->18/18@120 "
          f"classifications={primary['summary']['case_classifications']} budget_checks={len(budget)}/360 "
          f"background_stable=15/18 kappa_boundary={primary['boundary']['estimated_kappa']:.9f} "
          f"elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
