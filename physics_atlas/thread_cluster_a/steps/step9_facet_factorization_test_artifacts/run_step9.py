#!/usr/bin/env python3
"""Validate Cluster A Step 9 artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import runpy
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP8_DIR = THREAD_DIR / "steps" / "step8_structural_token_blind_selection_artifacts"
STEPS_DIR = THREAD_DIR / "steps"
STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_selection_layer_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_p2_selection_constraint_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_e043_scale_selection_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_e009_uv_fiber_artifacts" / "run_step5.py",
    STEPS_DIR / "step6_e043_horn_adjudication_artifacts" / "run_step6.py",
    STEPS_DIR / "step7_consolidated_statement_artifacts" / "run_step7.py",
    STEPS_DIR / "step8_structural_token_blind_selection_artifacts" / "run_step8.py",
]

FACETS = ["gauge_code", "rep_code", "n_gen", "texture_code", "ew_code", "uv_code", "vacuum_code"]
THRESHOLD = 0.01
TOL = 1e-9

REQUIRED_FILES = [
    "facet_factorization_test_step9.py",
    "total_correlation_step9.csv",
    "pairwise_mi_matrix_step9.csv",
    "coupling_graph_step9.csv",
    "components_step9.csv",
    "block_decomposition_step9.csv",
    "robustness_step9.csv",
    "facet_factorization_output_step9.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step9_statement.tex",
]

STEP8_SOURCES = [
    STEP8_DIR / "neutral_candidate_space_step8.csv",
    STEP8_DIR / "structural_survivors_step8.csv",
]

FORBIDDEN_PATTERNS = [
    r"derives the gauge group",
    r"derives the standard model",
    r"computes the number of generations",
    r"selects the vacuum",
    r"solves the hierarchy problem",
    r"predicts the fermion masses",
    r"computes the cosmological constant",
    r"rejects anthropic",
    r"disproves anthropic",
    r"frame-transfer certificate",
    r"cross-layer derivation",
    r"\bpsi\b",
    r"co-sourcing",
    r"common-refinement",
    r"stress-energy",
    r"field-layer",
    r"amplitude\(geometry\)",
]


def fail(message: str) -> None:
    print(f"STEP9 VALIDATION FAILED: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str) -> float:
    return float(value)


def almost_equal(left: float, right: float, tol: float = TOL) -> bool:
    return math.isclose(left, right, rel_tol=0.0, abs_tol=tol)


def require_file(path: Path) -> None:
    if not path.exists():
        fail(f"missing required artifact: {path}")


def scan_forbidden_text() -> None:
    checked_suffixes = {".md", ".tex", ".json", ".csv", ".py"}
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step9.py" or path.suffix not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"forbidden phrase/pattern {pattern!r} found in {path.name}")


def validate_total_correlation() -> None:
    rows = {row["variation"]: row for row in read_csv(ARTIFACT_DIR / "total_correlation_step9.csv")}
    required = {"neutral_product", "structural_survivors", "strict_naturalness_le_1", "subsample_80_seed_20260606"}
    if set(rows) != required:
        fail(f"unexpected total-correlation variations: {sorted(rows)}")

    neutral = rows["neutral_product"]
    neutral_c = as_float(neutral["total_correlation_bits"])
    if abs(neutral_c) > TOL:
        fail(f"neutral baseline total correlation is not zero: {neutral_c}")
    if neutral["verdict"] != "independent_neutral_control":
        fail("neutral baseline verdict is not independent_neutral_control")

    survivor = rows["structural_survivors"]
    survivor_c = as_float(survivor["total_correlation_bits"])
    survivor_sum = as_float(survivor["sum_marginal_entropy_bits"])
    survivor_joint = as_float(survivor["joint_entropy_bits"])
    if survivor_c <= 0.0:
        fail("structural survivor total correlation is not positive")
    if not almost_equal(survivor_sum - survivor_joint, survivor_c):
        fail("structural survivor total correlation does not equal sumH - jointH")
    if survivor["verdict"] != "block_structured_coupling":
        fail("structural survivor total-correlation verdict is inconsistent")


def validate_pairwise_matrix() -> None:
    rows = read_csv(ARTIFACT_DIR / "pairwise_mi_matrix_step9.csv")
    by_key = {(row["variation"], row["left_facet"], row["right_facet"]): row for row in rows}
    variations = {row["variation"] for row in rows}
    for variation in variations:
        for left in FACETS:
            for right in FACETS:
                key = (variation, left, right)
                if key not in by_key:
                    fail(f"missing matrix entry {key}")
                value = as_float(by_key[key]["mi_bits"])
                if left == right and value < -TOL:
                    fail(f"negative diagonal entropy for {variation} {left}")
                if left != right:
                    reverse = as_float(by_key[(variation, right, left)]["mi_bits"])
                    if not almost_equal(value, reverse):
                        fail(f"MI matrix is not symmetric for {variation} {left}/{right}")
                    expected_flag = value > THRESHOLD
                    actual_flag = by_key[key]["edge_above_threshold"] == "True"
                    if expected_flag != actual_flag:
                        fail(f"threshold flag mismatch for {variation} {left}/{right}")


def validate_graph_and_blocks() -> None:
    blocks = {row["variation"]: row for row in read_csv(ARTIFACT_DIR / "block_decomposition_step9.csv")}
    components = read_csv(ARTIFACT_DIR / "components_step9.csv")
    component_counts = {}
    for row in components:
        component_counts[row["variation"]] = component_counts.get(row["variation"], 0) + 1

    survivor = blocks["structural_survivors"]
    expected_partition = "gauge_code+n_gen+rep_code+texture_code+uv_code+vacuum_code / ew_code"
    if survivor["block_partition"] != expected_partition:
        fail(f"unexpected survivor block partition: {survivor['block_partition']}")
    if int(survivor["component_count"]) != 2 or component_counts.get("structural_survivors") != 2:
        fail("structural survivor graph does not have two components")
    if not almost_equal(as_float(survivor["inter_block_residual_bits"]), 0.035998916880):
        fail("structural survivor block residual changed unexpectedly")
    if survivor["separability_verdict"] != "block_structured_coupling":
        fail("structural survivor separability verdict is inconsistent")

    neutral = blocks["neutral_product"]
    if neutral["separability_verdict"] != "independent_neutral_control":
        fail("neutral block verdict is not independent_neutral_control")
    if int(neutral["component_count"]) != 7:
        fail("neutral product should have seven singleton components")

    strict = blocks["strict_naturalness_le_1"]
    if int(strict["component_count"]) != 1 or strict["separability_verdict"] != "coupled_single_component":
        fail("strict naturalness robustness row is inconsistent")

    subsample = blocks["subsample_80_seed_20260606"]
    if int(subsample["component_count"]) != 2 or subsample["block_partition"] != expected_partition:
        fail("deterministic subsample robustness row is inconsistent")


def validate_json_schema_outputs() -> None:
    summary = json.loads((ARTIFACT_DIR / "facet_factorization_output_step9.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = summary.get("verdict", {})
    if verdict.get("type") != "facet_factorization_test_constructed":
        fail("JSON verdict type is wrong")
    if abs(float(verdict.get("neutral_total_correlation_bits", 1.0))) > TOL:
        fail("JSON neutral total correlation is not zero")
    if not almost_equal(float(verdict.get("survivor_total_correlation_bits")), 2.229304481463):
        fail("JSON survivor total correlation changed")
    if verdict.get("component_count") != 2:
        fail("JSON component count is wrong")
    if verdict.get("separability_verdict") != "block_structured_coupling":
        fail("JSON separability verdict is wrong")
    if verdict.get("root_landed") is not False or verdict.get("frame_transfer_certified") is not False:
        fail("JSON must keep root_landed and frame_transfer_certified false")

    if schema.get("artifact_type") != "facet_factorization_test":
        fail("schema artifact_type is wrong")
    schema_verdict = schema.get("verdict", {})
    if schema_verdict.get("separability") != "block_structured_coupling":
        fail("schema separability verdict is wrong")
    if schema_verdict.get("one_physical_layer_proven") is not False:
        fail("schema must not mark one physical layer as proven")
    if schema_verdict.get("physical_values_inferred") is not False:
        fail("schema must not mark physical values as inferred")


def validate_content_classification() -> None:
    allowed_grades = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if not rows:
        fail("content_classification.csv has no rows")
    for row in rows:
        if not row.get("claim"):
            fail("content classification row has empty claim")
        if row.get("grade") not in allowed_grades:
            fail(f"bad content grade: {row.get('grade')}")
        source_field = row.get("source_artifacts", "")
        if "/home/" in source_field or source_field.startswith("/"):
            fail("content source path is absolute")
        for source in [part.strip() for part in source_field.split(";") if part.strip()]:
            source_path = THREAD_DIR / source
            if not source_path.exists():
                fail(f"content source does not exist: {source}")


def run_prior_validators() -> None:
    for runner in STEP_RUNNERS:
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
            cwd=STEPS_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(
                f"{runner.name} failed during Step 9 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def run_self() -> None:
    for path in STEP8_SOURCES:
        require_file(path)
    for filename in REQUIRED_FILES:
        require_file(ARTIFACT_DIR / filename)

    runpy.run_path(str(ARTIFACT_DIR / "facet_factorization_test_step9.py"), run_name="__main__")

    scan_forbidden_text()
    validate_total_correlation()
    validate_pairwise_matrix()
    validate_graph_and_blocks()
    validate_json_schema_outputs()
    validate_content_classification()

    print("STEP9 VALIDATION PASSED")


def run_chain() -> None:
    run_prior_validators()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 9 artifacts.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--self", action="store_true", help="validate only this step's own artifacts (default)")
    mode.add_argument("--chain", action="store_true", help="validate prior steps once, then this step")
    args = parser.parse_args(argv)
    if args.chain:
        run_chain()
    else:
        run_self()


if __name__ == "__main__":
    main()
