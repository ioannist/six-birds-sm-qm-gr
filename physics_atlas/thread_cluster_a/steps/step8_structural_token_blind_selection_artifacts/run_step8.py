#!/usr/bin/env python3
"""Validate Cluster A Step 8 structural token-blind selection artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import runpy
import subprocess
import sys
from collections import Counter
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
BUILD_SCRIPT = ARTIFACT_DIR / "structural_token_blind_selection_step8.py"
STEPS_DIR = THREAD_DIR / "steps"
STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_selection_layer_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_p2_selection_constraint_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_e043_scale_selection_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_e009_uv_fiber_artifacts" / "run_step5.py",
    STEPS_DIR / "step6_e043_horn_adjudication_artifacts" / "run_step6.py",
    STEPS_DIR / "step7_consolidated_statement_artifacts" / "run_step7.py",
]

REQUIRED_FILES = [
    "structural_token_blind_selection_step8.py",
    "neutral_candidate_space_step8.csv",
    "structural_survivors_step8.csv",
    "admissibility_breakdown_step8.csv",
    "mi_comparison_step8.csv",
    "neutral_generation_procedure_step8.csv",
    "structural_summary_step8.csv",
    "structural_token_blind_output_step8.json",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step8_statement.tex",
    "run_step8.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bcomputes the number of generations\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy\b",
    r"\bsolves the hierarchy problem\b",
    r"\bpredicts the fermion masses\b",
    r"\bcomputes the cosmological constant\b",
    r"\brejects anthropic\b",
    r"\bdisproves anthropic\b",
    r"\bnew physics prediction\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\\(geometry\\)\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
]

FORBIDDEN_BUILD_SNIPPETS = [
    "G_SM",
    "R_SM_CHIRAL",
    "Y_SM_TOY",
    "EW_LOW_TOY",
    "UV_SM_TOY",
    "VAC_SM_TOY",
    "REALIZED_WORLD",
    "world_id == REALIZED_WORLD",
    "world_id==REALIZED_WORLD",
    "co-sourcing",
    "common-refinement",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step8.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def run_build_script() -> None:
    runpy.run_path(str(BUILD_SCRIPT), run_name="__main__")


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
                f"{runner.name} failed during Step 8 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_token_blind() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for snippet in FORBIDDEN_BUILD_SNIPPETS:
        if snippet in text:
            fail(f"build script contains forbidden circularity/model term: {snippet}")
    regexes = [
        r"n_gen\s*==\s*3",
        r"n_gen==3",
        r"realized[\w\s.-]{0,40}bonus",
        r"bonus[\w\s.-]{0,40}realized",
        r"!=\s*[\"']?[A-Z][A-Z0-9_]*SM[A-Z0-9_]*",
        r"(?<![A-Za-z0-9_])psi(?![A-Za-z0-9_])|ψ",
    ]
    for pattern in regexes:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"build script matches forbidden anti-circularity regex: {pattern}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step8.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_generation_procedure() -> None:
    generation = read_csv("neutral_generation_procedure_step8.csv")
    sizes = {row["facet"]: int(row["alphabet_size"]) for row in generation}
    expected = {
        "gauge_code": 4,
        "rep_code": 4,
        "n_gen": 5,
        "texture_code": 4,
        "ew_code": 3,
        "uv_code": 3,
        "vacuum_code": 3,
    }
    if sizes != expected:
        fail(f"unexpected alphabet sizes: {sizes}")
    product = math.prod(sizes.values())
    if product != 8640:
        fail(f"neutral product size should be 8640, got {product}")


def validate_neutral_space() -> None:
    rows = read_csv("neutral_candidate_space_step8.csv")
    if len(rows) != 8640:
        fail(f"neutral candidate space has wrong size: {len(rows)}")
    source_counts = Counter(row["source"] for row in rows)
    if source_counts != {"full_product": 8640}:
        fail(f"neutral space is not a full-product source: {source_counts}")
    realized = [row for row in rows if as_bool(row["is_realized_point"])]
    if len(realized) != 1:
        fail("exactly one realized point must be present in the neutral product")
    balance_checks = {
        "gauge_code": 2160,
        "rep_code": 2160,
        "n_gen": 1728,
        "texture_code": 2160,
        "ew_code": 2880,
        "uv_code": 2880,
        "vacuum_code": 2880,
    }
    for key, expected_count in balance_checks.items():
        counts = Counter(row[key] for row in rows)
        if set(counts.values()) != {expected_count}:
            fail(f"facet {key} is overrepresented or underrepresented: {counts}")


def validate_survivors_and_summary() -> None:
    survivors = read_csv("structural_survivors_step8.csv")
    summary_rows = read_csv("structural_summary_step8.csv")
    if len(survivors) != 468:
        fail(f"unexpected survivor count: {len(survivors)}")
    if len(summary_rows) != 1:
        fail("structural_summary_step8.csv must have one row")
    summary = summary_rows[0]
    if int(summary["neutral_space_size"]) != 8640 or int(summary["structural_survivor_count"]) != 468:
        fail("summary counts mismatch")
    if summary["realized_point_status"] != "among_structural_survivors_not_unique":
        fail(f"unexpected realized point status: {summary['realized_point_status']}")
    if int(float(summary["realized_point_structural_rank"])) != 2:
        fail("realized point should have structural rank 2")
    if int(float(summary["max_score_tie_count"])) <= 1:
        fail("realized point is being treated as unique; expected non-unique top tier")
    realized_survivors = [row for row in survivors if as_bool(row["is_realized_point"])]
    if len(realized_survivors) != 1:
        fail("realized point must be among survivors exactly once")
    if int(realized_survivors[0]["structural_rank"]) != 2:
        fail("realized survivor rank mismatch")


def validate_breakdown_and_mi() -> None:
    breakdown = read_csv("admissibility_breakdown_step8.csv")
    sequence = [int(row["survivor_count"]) for row in breakdown]
    if sequence != [8640, 3240, 3240, 1836, 1134, 549, 468]:
        fail(f"unexpected pruning sequence: {sequence}")
    if any(sequence[idx + 1] > sequence[idx] for idx in range(len(sequence) - 1)):
        fail("pruning sequence is not monotone non-increasing")
    mi_rows = {row["population"]: row for row in read_csv("mi_comparison_step8.csv")}
    neutral = float(mi_rows["neutral_product"]["gauge_generation_mi_bits"])
    survivors = float(mi_rows["structural_survivors"]["gauge_generation_mi_bits"])
    if abs(neutral) > 1e-10:
        fail(f"neutral product MI should vanish, got {neutral}")
    if survivors <= 0.1:
        fail(f"survivor MI should be positive and nontrivial, got {survivors}")
    if int(mi_rows["neutral_product"]["missing_pair_count"]) != 0:
        fail("neutral product should have no missing gauge-generation pairs")
    if int(mi_rows["structural_survivors"]["missing_pair_count"]) <= 0:
        fail("survivors should have induced missing gauge-generation pairs")


def validate_schema_and_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "structural_token_blind_output_step8.json").read_text(encoding="utf-8"))
    for name, payload in [("schema", schema), ("output", output)]:
        verdict = payload.get("final_verdict", payload.get("verdict", {}))
        if verdict.get("type") != "structural_token_blind_selection_constructed":
            fail(f"{name} has wrong verdict type")
        if verdict.get("neutral_space_size") != 8640:
            fail(f"{name} neutral size mismatch")
        if verdict.get("structural_survivor_count") != 468:
            fail(f"{name} survivor count mismatch")
        if verdict.get("realized_point_status") != "among_structural_survivors_not_unique":
            fail(f"{name} realized status mismatch")
        if verdict.get("token_blind_structural_functional") is not True:
            fail(f"{name} does not mark token-blind functional")
        if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
            fail(f"{name} overstates root landing/frame transfer")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if len(rows) < 7:
        fail("content_classification.csv has too few rows")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unexpected grade: {row}")
        if not row.get("claim") or not row.get("source_artifacts"):
            fail(f"claim row missing content: {row}")
        for source in [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]:
            if source.startswith("/") or ".." in Path(source).parts:
                fail(f"source path must be thread-root-relative and portable: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_statement_text() -> None:
    text = (
        (ARTIFACT_DIR / "results_summary.md").read_text(encoding="utf-8")
        + "\n"
        + (ARTIFACT_DIR / "step8_statement.tex").read_text(encoding="utf-8")
        + "\n"
        + (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    )
    required = [
        "Neutral product size: `8640`",
        "Final structural survivor count: `468`",
        "among_structural_survivors_not_unique",
        "max-score tie count: `6`",
        "0.000000000000",
        "0.466203233486",
        "does not derive the gauge group",
        "does not derive the realized SM values",
        "does not choose the real world",
        "frame transfer",
    ]
    for snippet in required:
        if snippet not in text:
            fail(f"required Step 8 prose snippet missing: {snippet}")


def run_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_token_blind()
    scan_overclaims()
    validate_generation_procedure()
    validate_neutral_space()
    validate_survivors_and_summary()
    validate_breakdown_and_mi()
    validate_schema_and_output()
    validate_content_classification()
    validate_statement_text()
    print("run_step8.py: PASS")


def run_chain() -> None:
    run_prior_validators()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 8 artifacts.")
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
