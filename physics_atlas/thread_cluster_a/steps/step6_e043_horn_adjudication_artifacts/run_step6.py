#!/usr/bin/env python3
"""Validate Cluster A Step 6 artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_selection_layer_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_p2_selection_constraint_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_e043_scale_selection_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_e009_uv_fiber_artifacts" / "run_step5.py",
]
REQUIRED_FILES = [
    "e043_horn_adjudication_step6.py",
    "horn_degeneracy_step6.csv",
    "adjudication_step6.csv",
    "controls_step6.csv",
    "e043_horn_adjudication_output_step6.json",
    "e043_horn_adjudication_output_step6.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step6.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bcomputes the number of generations\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy problem\b",
    r"\bpredicts the fermion masses\b",
    r"\bcomputes the cosmological constant\b",
    r"\bco-sourcing\b",
    r"\broot_landed\s*[:=]\s*true\b",
    r"\bframe_transfer_certified\s*[:=]\s*true\b",
]

NON_SELECTION_MODEL_PATTERNS = [
    "co-sourcing",
    "common-refinement",
    "common_refinement",
    "F51",
    "F37",
    "stress-energy",
    "field-layer",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: str) -> bool:
    return value.strip().lower() in {"true", "1", "yes"}


def as_int(value: str) -> int:
    return int(float(value))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_no_overclaim() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step6.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"overclaim pattern {pattern!r} found in {path.name}")


def validate_selection_not_field_model() -> None:
    script = (ARTIFACT_DIR / "e043_horn_adjudication_step6.py").read_text(encoding="utf-8")
    for pattern in NON_SELECTION_MODEL_PATTERNS:
        if pattern in script:
            fail(f"Step 6 build script contains forbidden non-selection construction term: {pattern}")
    if re.search(r"(?<![A-Za-z0-9_])psi(?![A-Za-z0-9_])|ψ", script):
        fail("Step 6 build script contains forbidden standalone field token: psi")


def validate_horn_degeneracy() -> None:
    rows = read_csv("horn_degeneracy_step6.csv")
    by_horn: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_horn.setdefault(row["horn"], []).append(row)
    required = {"derivation_attractor", "broad_anthropic_measure", "sharp_selecting_measure"}
    missing = sorted(required - set(by_horn))
    if missing:
        fail(f"missing horn degeneracy rows: {missing}")
    for horn, horn_rows in by_horn.items():
        horn_rows.sort(key=lambda row: as_int(row["level"]))
        levels = [as_int(row["level"]) for row in horn_rows]
        if levels != list(range(len(horn_rows))):
            fail(f"nonconsecutive levels for {horn}")
        sequence = [as_int(row["effective_degeneracy"]) for row in horn_rows]
        for idx in range(1, len(sequence)):
            expected = sequence[idx] - sequence[idx - 1]
            if as_int(horn_rows[idx]["increment"]) != expected:
                fail(f"increment mismatch for {horn} at level {idx}")
            if expected > 0:
                fail(f"degeneracy increased for {horn} at level {idx}")
    if [as_int(row["effective_degeneracy"]) for row in by_horn["derivation_attractor"]][-1] != 1:
        fail("derivation horn must collapse to degeneracy 1")
    if [as_int(row["effective_degeneracy"]) for row in by_horn["broad_anthropic_measure"]][-1] <= 1:
        fail("broad measure must remain multiply supported")
    if [as_int(row["effective_degeneracy"]) for row in by_horn["sharp_selecting_measure"]][-1] != 1:
        fail("sharp measure control must collapse to degeneracy 1")


def validate_adjudication() -> None:
    rows = read_csv("adjudication_step6.csv")
    by_horn = {row["horn"]: row for row in rows}
    required = {"derivation_attractor", "broad_anthropic_measure", "sharp_selecting_measure"}
    missing = sorted(required - set(by_horn))
    if missing:
        fail(f"missing adjudication rows: {missing}")
    derivation = by_horn["derivation_attractor"]
    broad = by_horn["broad_anthropic_measure"]
    sharp = by_horn["sharp_selecting_measure"]
    for row in [derivation, sharp]:
        if not as_bool(row["collapses_to_point"]) or not as_bool(row["certified_by_P6"]):
            fail(f"{row['horn']} must collapse and be certified")
        if as_int(row["final_degeneracy"]) != 1:
            fail(f"{row['horn']} final degeneracy must be 1")
    if as_bool(broad["collapses_to_point"]) or as_bool(broad["certified_by_P6"]):
        fail("broad measure must not be certified")
    if as_int(broad["final_degeneracy"]) <= 1:
        fail("broad measure final degeneracy must stay >1")
    if broad["framework_status"] != "landscape_nonclosing":
        fail("broad measure must be marked landscape_nonclosing")


def validate_controls() -> None:
    rows = read_csv("controls_step6.csv")
    by_id = {row["control_id"]: row for row in rows}
    required = {
        "broad_measure_fails_to_collapse",
        "derivation_collapses",
        "sharp_measure_also_collapses",
        "selection_carrier_not_field_pair",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing controls: {missing}")
    for control_id in sorted(required):
        if not as_bool(by_id[control_id]["passes_guard"]):
            fail(f"control failed: {control_id}")


def validate_verdicts() -> None:
    output = json.loads((ARTIFACT_DIR / "e043_horn_adjudication_output_step6.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output["verdict"]
    if verdict["type"] != "e043_horn_adjudication_constructed":
        fail("wrong verdict type")
    certified = set(verdict["certified_horns"])
    failed = set(verdict["failed_horns"])
    if certified != {"derivation_attractor", "sharp_selecting_measure"}:
        fail(f"unexpected certified horns: {certified}")
    if failed != {"broad_anthropic_measure"}:
        fail(f"unexpected failed horns: {failed}")
    if verdict["broad_measure_final_degeneracy"] <= 1:
        fail("broad measure final degeneracy must be >1")
    if verdict["criterion"] != "P6_decaying_degeneracy_collapses_to_point":
        fail("wrong adjudication criterion")
    if verdict["root_landed"] or verdict["frame_transfer_certified"]:
        fail("root_landed/frame_transfer_certified must be false")
    if schema["final_verdict"]["type"] != verdict["type"]:
        fail("schema verdict must match output verdict")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        source = row["source_artifacts"]
        if source.startswith("/") or ".." in Path(source).parts:
            fail(f"source path must be thread-root-relative and portable: {source}")
        if not (THREAD_DIR / source).exists():
            fail(f"content source artifact does not exist: {source}")
        if row["grade"] not in {"finite-toy-diagnostic", "organizational"}:
            fail(f"unexpected grade for {row['output']}: {row['grade']}")


def validate_ledgers() -> None:
    checks = {
        "mode_b_target_lineage.csv": "R_cluster_a_after_step6_e043_horn_adjudication",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_A_STEP6_BROAD_MEASURE_FAILS",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_A_STEP7_CLUSTER_A_CONSOLIDATION_OR_ROBUSTNESS",
        "findings_cluster_a.md": "Step 6 - E043 Horn Adjudication",
    }
    for relative, marker in checks.items():
        text = (THREAD_DIR / relative).read_text(encoding="utf-8")
        if marker not in text:
            fail(f"ledger/finding marker {marker!r} missing from {relative}")


def validate_previous_steps() -> None:
    for runner in STEP_RUNNERS:
        subprocess.run([sys.executable, str(runner), "--self"], cwd=STEPS_DIR, check=True)


def run_self() -> None:
    runpy.run_path(str(ARTIFACT_DIR / "e043_horn_adjudication_step6.py"), run_name="__main__")
    validate_required_files()
    validate_no_overclaim()
    validate_selection_not_field_model()
    validate_horn_degeneracy()
    validate_adjudication()
    validate_controls()
    validate_verdicts()
    validate_content_classification()
    validate_ledgers()
    print("PASS Cluster A Step 6 validator")


def run_chain() -> None:
    validate_previous_steps()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 6 artifacts.")
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
