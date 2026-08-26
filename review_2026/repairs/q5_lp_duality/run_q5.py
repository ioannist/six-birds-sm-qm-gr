#!/usr/bin/env python3
"""Validator for Q5-REPAIR-1."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
DRIVER = HERE / "q5_lp_duality.py"


def load_driver():
    spec = importlib.util.spec_from_file_location("q5_lp_duality_validator", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import Q5 driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate() -> tuple[int, float]:
    started = time.perf_counter()
    q5 = load_driver()
    data = q5.build()
    expected = q5.render(data)
    errors: list[str] = []
    for name, payload in expected.items():
        path = HERE / name
        if not path.exists():
            errors.append(f"missing artifact: {name}")
        elif path.read_bytes() != payload:
            errors.append(f"byte mismatch: {name}")
    summary = data["summary"]
    derived_checks = {
        "all cuts unique": summary["all_min_cuts_unique"],
        "primal feasibility": summary["primal_feasible_all_regions"],
        "dual feasibility": summary["dual_feasible_all_regions"],
        "strong duality": summary["strong_duality_all_regions"],
        "complementary slackness": summary["complementary_slackness_all_regions"],
        "exact sensitivity": summary["sensitivity_equals_shadow_price_all_region_edges"],
        "can-fail control": summary["linear_response"]["can_fail_control_nonmatch"],
        "area gluing rule": summary["composition"]["area_min_plus_rule_all_probes"],
        "Born rule genuinely fails": not summary["composition"]["born_same_min_plus_rule_all_probes"],
        "composition verdict derived": not summary["composition"]["shared_composition_rule_constructed"],
        "same MMI class": summary["composition"]["born_and_area_in_same_mmi_inequality_class"],
    }
    errors.extend(name for name, passed in derived_checks.items() if not passed)
    # LP-specific load-bearing checks, not merely a verdict replay.
    if len(data["region_rows"]) != 254 or len(data["dual_rows"]) != 254 * 14:
        errors.append("unexpected carrier dimensions")
    if set(int(row["y_e"]) for row in data["dual_rows"]) != {0, 1}:
        errors.append("shadow prices are not the expected integral cut variables")
    elapsed = time.perf_counter() - started
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1, elapsed
    print(
        "PASS Q5-REPAIR-1: 254 exact primal/dual regions, 3556 sensitivity checks, "
        f"response={summary['linear_response']['verdict']}, composition={summary['composition']['verdict']}; "
        f"runtime={elapsed:.3f}s"
    )
    return 0, elapsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild in memory and byte-compare all artifacts")
    args = parser.parse_args()
    if not args.self:
        parser.error("use --self")
    return validate()[0]


if __name__ == "__main__":
    sys.exit(main())
