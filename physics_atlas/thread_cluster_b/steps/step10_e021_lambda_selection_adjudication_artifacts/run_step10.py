#!/usr/bin/env python3
"""Validate Cluster B Step 10 E021 Lambda-selection adjudication artifacts."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_substrate_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_e042_singularity_resolution_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_e021_cosmological_constant_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_consolidated_statement_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_honest_regrade_artifacts" / "run_step5.py",
    STEPS_DIR / "step6_shared_frame_robustness_artifacts" / "run_step6.py",
    STEPS_DIR / "step7_e042_earned_continuation_artifacts" / "run_step7.py",
    STEPS_DIR / "step8_e021_rg_measure_robustness_artifacts" / "run_step8.py",
    STEPS_DIR / "step9_r6_consolidation_artifacts" / "run_step9.py",
]

REQUIRED_FILES = [
    "e021_lambda_selection_adjudication_step10.py",
    "lambda_degeneracy_step10.csv",
    "adjudication_step10.csv",
    "controls_step10.csv",
    "e021_lambda_selection_adjudication_output_step10.json",
    "e021_lambda_selection_adjudication_output_step10.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step10.py",
]

OVERCLAIM_PATTERNS = [
    r"\bproves quantum gravity\b",
    r"\bsolves quantum gravity\b",
    r"\bcloses QM-GR unconditionally\b",
    r"\bdiscovers a new physical law\b",
    r"\bpredicts a new constant\b",
    r"\bcomputes the cosmological constant\b",
    r"\bderives the value of lambda\b",
    r"\bsolves the cosmological constant problem\b",
    r"\bresolves the singularity\b",
    r"\bquantizes gravity\b",
    r"\bco-sourcing\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
]

NON_SELECTION_MODEL_PATTERNS = [
    "co-sourcing",
    "common-refinement",
    "common_refinement",
    "F51",
    "F37",
    "stress-energy",
    "Born",
]


def fail(message: str) -> None:
    print(f"run_step10.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def as_int(value: object) -> int:
    return int(float(str(value)))


def run_builder() -> None:
    builder = ARTIFACT_DIR / "e021_lambda_selection_adjudication_step10.py"
    result = subprocess.run(
        [sys.executable, str(builder)],
        cwd=ARTIFACT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"builder failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_no_overclaim() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step10.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".csv", ".tex"}:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"overclaim pattern {pattern!r} found in {path.name}")


def validate_selection_not_field_model() -> None:
    script = (ARTIFACT_DIR / "e021_lambda_selection_adjudication_step10.py").read_text(encoding="utf-8")
    for pattern in NON_SELECTION_MODEL_PATTERNS:
        if pattern in script:
            fail(f"build script contains forbidden non-selection construction term: {pattern}")
    if re.search(r"(?<![A-Za-z0-9_])psi(?![A-Za-z0-9_])|ψ", script):
        fail("build script contains forbidden standalone psi token")


def validate_degeneracy_rows() -> None:
    rows = read_csv("lambda_degeneracy_step10.csv")
    by_horn: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_horn.setdefault(row["horn"], []).append(row)
    required = {"relaxation_attractor", "broad_anthropic_landscape", "sharp_selecting_measure"}
    missing = sorted(required - set(by_horn))
    if missing:
        fail(f"missing horn degeneracy rows: {missing}")
    for horn, horn_rows in by_horn.items():
        horn_rows.sort(key=lambda row: as_int(row["level"]))
        levels = [as_int(row["level"]) for row in horn_rows]
        if levels != list(range(len(horn_rows))):
            fail(f"nonconsecutive levels for {horn}")
        sequence = [as_int(row["effective_Lambda_degeneracy"]) for row in horn_rows]
        for idx in range(1, len(sequence)):
            expected = sequence[idx] - sequence[idx - 1]
            if as_int(horn_rows[idx]["increment"]) != expected:
                fail(f"increment mismatch for {horn} at level {idx}")
            if expected > 0:
                fail(f"degeneracy increased for {horn} at level {idx}")
    if [as_int(row["effective_Lambda_degeneracy"]) for row in by_horn["relaxation_attractor"]][-1] != 1:
        fail("relaxation horn must collapse to degeneracy 1")
    if [as_int(row["effective_Lambda_degeneracy"]) for row in by_horn["broad_anthropic_landscape"]][-1] <= 1:
        fail("broad anthropic landscape must remain multiply supported")
    if [as_int(row["effective_Lambda_degeneracy"]) for row in by_horn["sharp_selecting_measure"]][-1] != 1:
        fail("sharp measure control must collapse to degeneracy 1")


def validate_adjudication() -> None:
    rows = read_csv("adjudication_step10.csv")
    by_horn = {row["horn"]: row for row in rows}
    required = {"relaxation_attractor", "broad_anthropic_landscape", "sharp_selecting_measure"}
    missing = sorted(required - set(by_horn))
    if missing:
        fail(f"missing adjudication rows: {missing}")
    for horn in ["relaxation_attractor", "sharp_selecting_measure"]:
        row = by_horn[horn]
        if not as_bool(row["collapses_to_point"]) or not as_bool(row["certified_by_P6"]):
            fail(f"{horn} must collapse and be certified")
        if as_int(row["final_degeneracy"]) != 1:
            fail(f"{horn} final degeneracy must be 1")
        if row["framework_status"] != "certified_selection":
            fail(f"{horn} must be marked certified_selection")
    broad = by_horn["broad_anthropic_landscape"]
    if as_bool(broad["collapses_to_point"]) or as_bool(broad["certified_by_P6"]):
        fail("broad anthropic landscape must not be certified")
    if as_int(broad["final_degeneracy"]) <= 1:
        fail("broad anthropic landscape final degeneracy must stay >1")
    if broad["framework_status"] != "landscape_nonclosing":
        fail("broad anthropic landscape must be marked landscape_nonclosing")


def validate_controls() -> None:
    rows = read_csv("controls_step10.csv")
    by_id = {row["control_id"]: row for row in rows}
    required = {
        "broad_landscape_fails_to_collapse",
        "relaxation_collapses",
        "sharp_measure_collapses",
        "selection_carrier_not_field_pair",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing controls: {missing}")
    for control_id in sorted(required):
        if not as_bool(by_id[control_id]["passes_guard"]):
            fail(f"control failed: {control_id}")


def validate_verdicts() -> None:
    output = json.loads((ARTIFACT_DIR / "e021_lambda_selection_adjudication_output_step10.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output["verdict"]
    schema_verdict = schema["final_verdict"]
    if verdict["type"] != "e021_lambda_selection_adjudication_constructed":
        fail("wrong output verdict type")
    if schema_verdict["type"] != verdict["type"]:
        fail("schema verdict must match output verdict")
    certified = set(verdict["certified_horns"])
    failed = set(verdict["failed_horns"])
    if certified != {"relaxation_attractor", "sharp_selecting_measure"}:
        fail(f"unexpected certified horns: {certified}")
    if failed != {"broad_anthropic_landscape"}:
        fail(f"unexpected failed horns: {failed}")
    if verdict["broad_landscape_final_degeneracy"] <= 1:
        fail("broad landscape final degeneracy must be >1")
    if verdict["criterion"] != "P6_decaying_degeneracy_collapses_to_point":
        fail("wrong adjudication criterion")
    if verdict["root_landed"] or verdict["frame_transfer_certified"]:
        fail("root_landed/frame_transfer_certified must be false")
    nonclaim = schema["nonclaim"]
    for key in [
        "computes_lambda_value",
        "physical_anthropic_disproof",
        "solves_cosmological_constant_problem",
        "frame_transfer_certified",
    ]:
        if nonclaim[key] is not False:
            fail(f"schema nonclaim key must be false: {key}")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        if not row.get("grade"):
            fail(f"ungraded content row: {row}")
        if row["grade"] not in {"finite-toy-diagnostic", "organizational"}:
            fail(f"unexpected grade: {row}")
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"content row has no source artifacts: {row}")
        for source in sources:
            if source.startswith("/") or ".." in Path(source).parts:
                fail(f"source path must be thread-root-relative and portable: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_ledgers() -> None:
    checks = {
        "mode_b_target_lineage.csv": "R_cluster_b_after_step10_E021_lambda_selection_adjudication",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_B_STEP10_BROAD_LANDSCAPE_FAILS",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_B_STEP11_CLUSTER_B_CONSOLIDATION_OR_REVIEW",
        "findings_cluster_b.md": "Step 10 - E021 Lambda-Selection Adjudication",
    }
    for relative, marker in checks.items():
        path = THREAD_DIR / relative
        if not path.exists():
            fail(f"ledger missing: {relative}")
        if marker not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {marker}")


def run_prior_validators() -> None:
    for validator in STEP_RUNNERS:
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
                f"{validator.name} failed during Step 10 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def main() -> None:
    run_builder()
    validate_required_files()
    validate_no_overclaim()
    validate_selection_not_field_model()
    validate_degeneracy_rows()
    validate_adjudication()
    validate_controls()
    validate_verdicts()
    validate_content_classification()
    validate_ledgers()
    run_prior_validators()
    print("run_step10.py: PASS")


if __name__ == "__main__":
    main()
