#!/usr/bin/env python3
"""Validate Cluster B Step 7 E042 earned-continuation artifacts."""

from __future__ import annotations

import csv
import json
import math
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "e042_earned_continuation_step7.py",
    "lorentzian_curvature_step7.csv",
    "earned_continuation_step7.csv",
    "controls_step7.csv",
    "e042_earned_continuation_output_step7.json",
    "e042_earned_continuation_output_step7.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step7.py",
]

FORBIDDEN_PATTERNS = [
    r"proves quantum gravity",
    r"solves quantum gravity",
    r"closes QM-GR unconditionally",
    r"discovers a new physical law",
    r"predicts a new constant",
    r"computes the cosmological constant",
    r"derives the value of lambda",
    r"solves the cosmological constant problem",
    r"resolves the singularity",
    r"quantizes gravity",
    r"root_landed[\"']?\s*:\s*true",
    r"frame_transfer_certified[\"']?\s*:\s*true",
]


def fail(message: str) -> None:
    print(f"run_step7.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def truth(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def parse_float(value: str) -> float:
    if value == "":
        return math.nan
    if value == "inf":
        return math.inf
    if value == "nan":
        return math.nan
    return float(value)


def validate_required() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step7.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_schema_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "e042_earned_continuation_output_step7.json").read_text(encoding="utf-8"))
    for name, payload in [("schema", schema), ("output", output)]:
        verdict = payload.get("final_verdict", payload.get("verdict", {}))
        if verdict.get("type") != "E042_earned_continuation_constructed_finite_toy":
            fail(f"{name} has unexpected verdict type")
        for key in [
            "lorentzian_K_diverges",
            "L_R_stabilizes",
            "GR_terminates",
            "U_good_finite_post_locus",
            "U_good_generated_by_rule",
            "U_bad_fails",
        ]:
            if verdict.get(key) is not True:
                fail(f"{name} verdict key false: {key}")
        if verdict.get("earned_continuation_grade") != "finite-toy-diagnostic":
            fail(f"{name} does not grade earned continuation as finite-toy-diagnostic")
        if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
            fail(f"{name} overstates root landing or frame transfer")


def validate_curvature() -> None:
    rows = read_csv(ARTIFACT_DIR / "lorentzian_curvature_step7.csv")
    if len(rows) < 8:
        fail("Lorentzian curvature sequence is too short")
    k_values = [parse_float(row["K_lorentzian"]) for row in rows]
    finite_ks = [value for value in k_values if math.isfinite(value)]
    pre_locus_finite_ks = [
        parse_float(row["K_lorentzian"])
        for row in rows
        if row["regime"] == "pre_locus" and row["K_lorentzian"] != "inf"
    ]
    pre_locus_finite_k_incs = [
        parse_float(row["K_increment"])
        for row in rows
        if row["regime"] == "pre_locus" and row["K_increment"] not in {"", "inf"}
    ]
    finite_r_incs = [parse_float(row["R_increment"]) for row in rows if row["R_increment"] not in {"", "inf"}]
    if not any(math.isinf(value) for value in k_values):
        fail("Lorentzian K never reaches the locus divergence")
    if finite_ks[-1] <= 1.0e10 or pre_locus_finite_ks[-1] <= 1.0e10:
        fail("finite Lorentzian K does not grow enough near the locus")
    if not (pre_locus_finite_k_incs[-1] > pre_locus_finite_k_incs[-2] > pre_locus_finite_k_incs[-3]):
        fail("pre-locus Lorentzian K increments do not grow near the locus")
    r_last = parse_float(rows[-1]["R_L"])
    if abs(r_last - 0.75) > 1.0e-7:
        fail("L resolved readout does not approach finite R_star")
    if finite_r_incs[-1] >= 1.0e-6:
        fail("L resolved readout increments do not stabilize")


def validate_earned_continuation() -> None:
    rows = read_csv(ARTIFACT_DIR / "earned_continuation_step7.csv")
    if not rows:
        fail("earned_continuation_step7.csv is empty")
    post_rows = [row for row in rows if float(row["r_out"]) < 0.0]
    if not post_rows:
        fail("no post-locus rows generated")
    if not all(truth(row["U_good_generated_by_rule"]) for row in rows):
        fail("U_good outputs are not all marked generated by rule")
    if not all(truth(row["U_good_output_finite"]) for row in post_rows):
        fail("U_good post-locus outputs are not finite")
    if any(row["U_good_rule"].strip() == "" for row in rows):
        fail("U_good rule is missing from continuation rows")
    if "L_defined" in (ARTIFACT_DIR / "earned_continuation_step7.csv").read_text(encoding="utf-8"):
        fail("continuation CSV still uses assigned L_defined field")
    if not any(truth(row["GR_terminated"]) for row in rows if float(row["r_out"]) <= 0.0):
        fail("GR does not terminate at or before the locus")
    if not any(truth(row["U_bad_terminated"]) for row in rows):
        fail("U_bad never terminates")
    if any(truth(row["U_bad_output_finite"]) for row in post_rows):
        fail("U_bad continues finitely through the post-locus rows")


def validate_controls() -> None:
    rows = {row["control_id"]: row for row in read_csv(ARTIFACT_DIR / "controls_step7.csv")}
    required = [
        "lorentzian_K_diverges",
        "L_R_stabilizes",
        "GR_terminates_at_locus",
        "U_good_earns_finite_post_locus_continuation",
        "U_bad_fails_to_continue",
        "earned_not_assigned",
    ]
    for key in required:
        if key not in rows:
            fail(f"missing control: {key}")
        if not truth(rows[key]["passes_guard"]):
            fail(f"control does not pass guard: {key}")


def validate_content_paths_and_grades() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    by_output = {row["output"]: row for row in rows}
    earned = by_output.get("earned_continuation_step7.csv")
    if not earned:
        fail("content classification missing earned_continuation_step7.csv")
    if earned["grade"] == "modeled-shape":
        fail("earned continuation is still graded modeled-shape")
    if earned["grade"] != "finite-toy-diagnostic":
        fail("earned continuation must be graded finite-toy-diagnostic")
    for row in rows:
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"content row has no source artifacts: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"absolute source path is not allowed: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_ledgers() -> None:
    checks = [
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step7_E042_earned_continuation"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_R6_E042_AFTER_STEP7"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP7_EARNED_CONTINUATION"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 7 - E042 Earned Continuation"),
    ]
    for path, needle in checks:
        if not path.exists():
            fail(f"ledger missing: {path}")
        if needle not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {needle}")


def run_prior_validators() -> None:
    validators = [
        THREAD_DIR / "steps/step1_shared_substrate_frame_artifacts/run_step1.py",
        THREAD_DIR / "steps/step2_e042_singularity_resolution_artifacts/run_step2.py",
        THREAD_DIR / "steps/step3_e021_cosmological_constant_artifacts/run_step3.py",
        THREAD_DIR / "steps/step4_consolidated_statement_artifacts/run_step4.py",
        THREAD_DIR / "steps/step5_honest_regrade_artifacts/run_step5.py",
        THREAD_DIR / "steps/step6_shared_frame_robustness_artifacts/run_step6.py",
    ]
    for validator in validators:
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=validator.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(
                f"{validator.name} failed during Step 7 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def main() -> None:
    validate_required()
    scan_overclaims()
    validate_schema_output()
    validate_curvature()
    validate_earned_continuation()
    validate_controls()
    validate_content_paths_and_grades()
    validate_ledgers()
    run_prior_validators()
    print("run_step7.py: PASS")


if __name__ == "__main__":
    main()
