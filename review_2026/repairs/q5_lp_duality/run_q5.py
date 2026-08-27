#!/usr/bin/env python3
"""Validator for Q5-REPAIR-1 with exact/float replay contracts."""

from __future__ import annotations

import argparse
import csv
import importlib.util
import io
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DRIVER = HERE / "q5_lp_duality.py"

ARTIFACT_CONTRACTS = {
    "q5_carrier_edges.csv": "EXACT",
    "q5_region_duality.csv": "EXACT",
    "q5_edge_shadow_prices.csv": "EXACT",
    "q5_linear_response.csv": "FLOAT",
    "q5_composition_probe.csv": "FLOAT",
    "q5_lp_matrices.json": "EXACT",
    "q5_results.json": "FLOAT",
    "q5_schema.json": "EXACT",
    "RESULTS.md": "FLOAT",
    "DESIGN.md": "EXACT",
}

# Only these CSV columns are solver/contraction floats. Rational strings,
# integer flags, headers, text, and row order remain exact.
CSV_FLOAT_TOLERANCES = {
    "q5_linear_response.csv": {
        "recontracted_state_delta_S": (5e-10, 1e-10),
        "response_error": (5e-10, 1e-10),
        "can_fail_control_delta_S": (5e-10, 1e-10),
    },
    "q5_composition_probe.csv": {
        "glued_born_direct": (5e-10, 1e-10),
        "born_min_plus_components": (5e-10, 1e-10),
    },
}

# JSON pointer -> (absolute tolerance, relative tolerance). Unlisted numbers
# remain exact even inside a FLOAT-class artifact.
JSON_FLOAT_TOLERANCES = {
    "/linear_response/max_absolute_error": (5e-10, 1e-10),
    "/composition/born_i3": (5e-12, 1e-10),
    "/composition/area_i3": (5e-12, 1e-10),
}

MARKDOWN_FLOAT_TOLERANCE = (5e-10, 1e-10)
NUMBER_TOKEN = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?")
INTEGER_TOKEN = re.compile(r"[-+]?\d+")


def load_driver():
    spec = importlib.util.spec_from_file_location("q5_lp_duality_validator", DRIVER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import Q5 driver")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def close_enough(actual: float, expected: float, tolerance: tuple[float, float]) -> bool:
    absolute, relative = tolerance
    return math.isclose(actual, expected, abs_tol=absolute, rel_tol=relative)


def compare_float_csv(name: str, actual: bytes, expected: bytes) -> list[str]:
    tolerances = CSV_FLOAT_TOLERANCES[name]
    actual_rows = list(csv.reader(io.StringIO(actual.decode("utf-8"), newline="")))
    expected_rows = list(csv.reader(io.StringIO(expected.decode("utf-8"), newline="")))
    if not actual_rows or not expected_rows:
        return [] if actual_rows == expected_rows else [f"{name}: empty/shape mismatch"]
    if actual_rows[0] != expected_rows[0]:
        return [f"{name}: header mismatch"]
    if len(actual_rows) != len(expected_rows):
        return [f"{name}: row-count mismatch {len(actual_rows)-1} != {len(expected_rows)-1}"]
    header = expected_rows[0]
    errors = []
    for row_index, (actual_row, expected_row) in enumerate(
        zip(actual_rows[1:], expected_rows[1:]), start=1
    ):
        if len(actual_row) != len(header) or len(expected_row) != len(header):
            errors.append(f"{name}: row {row_index} width mismatch")
            continue
        for column, actual_value, expected_value in zip(header, actual_row, expected_row):
            if column in tolerances:
                try:
                    passed = close_enough(
                        float(actual_value), float(expected_value), tolerances[column]
                    )
                except ValueError:
                    passed = False
                if not passed:
                    errors.append(
                        f"{name}: row {row_index} field {column} numeric mismatch "
                        f"{actual_value} != {expected_value}"
                    )
            elif actual_value != expected_value:
                errors.append(
                    f"{name}: row {row_index} field {column} exact mismatch "
                    f"{actual_value!r} != {expected_value!r}"
                )
    return errors


def compare_json_value(actual: Any, expected: Any, pointer: str, errors: list[str]) -> None:
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or list(actual) != list(expected):
            errors.append(f"q5_results.json: key/order mismatch at {pointer or '/'}")
            return
        for key in expected:
            compare_json_value(actual[key], expected[key], f"{pointer}/{key}", errors)
        return
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            errors.append(f"q5_results.json: list shape mismatch at {pointer}")
            return
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            compare_json_value(actual_item, expected_item, f"{pointer}/{index}", errors)
        return
    tolerance = JSON_FLOAT_TOLERANCES.get(pointer)
    if tolerance is not None:
        if (
            isinstance(actual, bool)
            or not isinstance(actual, (int, float))
            or not close_enough(float(actual), float(expected), tolerance)
        ):
            errors.append(
                f"q5_results.json: numeric mismatch at {pointer}: {actual!r} != {expected!r}"
            )
    elif actual != expected or type(actual) is not type(expected):
        errors.append(
            f"q5_results.json: exact mismatch at {pointer}: {actual!r} != {expected!r}"
        )


def compare_float_json(actual: bytes, expected: bytes) -> list[str]:
    try:
        actual_value = json.loads(actual)
        expected_value = json.loads(expected)
    except json.JSONDecodeError as error:
        return [f"q5_results.json: parse failure: {error}"]
    errors: list[str] = []
    compare_json_value(actual_value, expected_value, "", errors)
    return errors


def numeric_tokens(text: str) -> tuple[list[str], list[str]]:
    numbers = []
    separators = []
    cursor = 0
    for match in NUMBER_TOKEN.finditer(text):
        separators.append(text[cursor : match.start()])
        numbers.append(match.group())
        cursor = match.end()
    separators.append(text[cursor:])
    return numbers, separators


def compare_float_markdown(actual: bytes, expected: bytes) -> list[str]:
    actual_numbers, actual_text = numeric_tokens(actual.decode("utf-8"))
    expected_numbers, expected_text = numeric_tokens(expected.decode("utf-8"))
    if actual_text != expected_text:
        return ["RESULTS.md: non-numeric text or numeric-token placement mismatch"]
    if len(actual_numbers) != len(expected_numbers):
        return ["RESULTS.md: numeric-token count mismatch"]
    errors = []
    for index, (actual_token, expected_token) in enumerate(
        zip(actual_numbers, expected_numbers)
    ):
        if INTEGER_TOKEN.fullmatch(actual_token) and INTEGER_TOKEN.fullmatch(expected_token):
            passed = actual_token == expected_token
        else:
            passed = close_enough(
                float(actual_token), float(expected_token), MARKDOWN_FLOAT_TOLERANCE
            )
        if not passed:
            errors.append(
                f"RESULTS.md: numeric token {index} mismatch {actual_token} != {expected_token}"
            )
    return errors


def compare_artifact(name: str, actual: bytes, expected: bytes) -> list[str]:
    contract = ARTIFACT_CONTRACTS[name]
    if contract == "EXACT":
        return [] if actual == expected else [f"{name}: byte mismatch"]
    if name in CSV_FLOAT_TOLERANCES:
        return compare_float_csv(name, actual, expected)
    if name == "q5_results.json":
        return compare_float_json(actual, expected)
    if name == "RESULTS.md":
        return compare_float_markdown(actual, expected)
    raise AssertionError(f"FLOAT artifact lacks comparator: {name}")


def mutated_results(payload: bytes, delta: float, section: str, field: str) -> bytes:
    value = json.loads(payload)
    value[section][field] += delta
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def mutated_csv_field(payload: bytes, field: str, delta: float) -> bytes:
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    rows = list(reader)
    if not rows or reader.fieldnames is None:
        raise AssertionError("cannot mutate empty CSV control payload")
    rows[0][field] = format(float(rows[0][field]) + delta, ".17g")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=reader.fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def validate() -> tuple[int, float]:
    started = time.perf_counter()
    q5 = load_driver()
    data = q5.build()
    expected = q5.render(data)
    errors: list[str] = []
    if set(expected) != set(ARTIFACT_CONTRACTS):
        errors.append(
            "artifact classification coverage mismatch: "
            f"render={sorted(expected)} policy={sorted(ARTIFACT_CONTRACTS)}"
        )
    for name, payload in expected.items():
        path = HERE / name
        if not path.exists():
            errors.append(f"missing artifact: {name}")
            continue
        artifact_errors = compare_artifact(name, path.read_bytes(), payload)
        errors.extend(artifact_errors)
        if not artifact_errors:
            print(f"CHECK {ARTIFACT_CONTRACTS[name]}: {name}: PASS")

    # Force controls use a verdict-adjacent FLOAT field. The reviewer's
    # observed scale (<=1.78e-10) must pass; a 1e-6 mutation must fail.
    observed_csv_errors = compare_artifact(
        "q5_linear_response.csv",
        mutated_csv_field(
            expected["q5_linear_response.csv"],
            "recontracted_state_delta_S",
            1.78e-10,
        ),
        expected["q5_linear_response.csv"],
    )
    observed_json_errors = compare_artifact(
        "q5_results.json",
        mutated_results(
            expected["q5_results.json"],
            4.44e-16,
            "composition",
            "born_i3",
        ),
        expected["q5_results.json"],
    )
    if observed_csv_errors or observed_json_errors:
        errors.append("can-fail control: reviewer-observed numerical drift was rejected")
    else:
        print(
            "CONTROL FLOAT-DRIFT PASS: linear-response +1.78e-10 and "
            "born_i3 +4.44e-16 accepted"
        )
    regression_errors = compare_artifact(
        "q5_results.json",
        mutated_results(
            expected["q5_results.json"],
            1e-6,
            "linear_response",
            "max_absolute_error",
        ),
        expected["q5_results.json"],
    )
    if not regression_errors:
        errors.append("can-fail control: verdict-adjacent 1e-6 regression was accepted")
    else:
        print("CONTROL FLOAT-REGRESSION PASS: verdict-adjacent +1e-6 rejected")

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
    if len(data["region_rows"]) != 254 or len(data["dual_rows"]) != 254 * 14:
        errors.append("unexpected carrier dimensions")
    if set(int(row["y_e"]) for row in data["dual_rows"]) != {0, 1}:
        errors.append("shadow prices are not the expected integral cut variables")
    elapsed = time.perf_counter() - started
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1, elapsed
    exact_count = sum(contract == "EXACT" for contract in ARTIFACT_CONTRACTS.values())
    float_count = sum(contract == "FLOAT" for contract in ARTIFACT_CONTRACTS.values())
    print(
        "PASS Q5-REPAIR-1: 254 exact primal/dual regions, 3556 sensitivity checks, "
        f"artifact_contracts=EXACT:{exact_count},FLOAT:{float_count}, "
        f"response={summary['linear_response']['verdict']}, composition={summary['composition']['verdict']}; "
        f"runtime={elapsed:.3f}s"
    )
    return 0, elapsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and validate all artifacts")
    args = parser.parse_args()
    if not args.self:
        parser.error("use --self")
    return validate()[0]


if __name__ == "__main__":
    sys.exit(main())
