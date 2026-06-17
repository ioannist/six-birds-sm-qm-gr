#!/usr/bin/env python3
"""Validate Cluster A Step 3 artifacts."""

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
STEP1_RUNNER = THREAD_DIR / "steps" / "step1_shared_selection_layer_frame_artifacts" / "run_step1.py"
STEP2_RUNNER = THREAD_DIR / "steps" / "step2_p2_selection_constraint_artifacts" / "run_step2.py"
REALIZED_WORLD = "w_SM"
REQUIRED_FILES = [
    "p6_decaying_degeneracy_step3.py",
    "degeneracy_refinement_step3.csv",
    "p6_audit_step3.csv",
    "controls_step3.csv",
    "p6_decaying_degeneracy_output_step3.json",
    "p6_decaying_degeneracy_output_step3.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step3.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bcomputes the number of generations\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy problem\b",
    r"\bpredicts the fermion masses\b",
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
    "psi",
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
        if path.name == "run_step3.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"overclaim pattern {pattern!r} found in {path.name}")


def validate_selection_not_field_model() -> None:
    script = (ARTIFACT_DIR / "p6_decaying_degeneracy_step3.py").read_text(encoding="utf-8")
    for pattern in NON_SELECTION_MODEL_PATTERNS:
        if pattern in script:
            fail(f"Step 3 build script contains forbidden non-selection construction term: {pattern}")


def validate_degeneracy_refinement() -> None:
    rows = read_csv("degeneracy_refinement_step3.csv")
    if len(rows) < 5:
        fail("refinement sequence must include several levels")
    levels = [as_int(row["level"]) for row in rows]
    if levels != list(range(len(rows))):
        fail("refinement levels must be consecutive from 0")
    g_selection = [as_int(row["g_selection"]) for row in rows]
    g_landscape = [as_int(row["g_landscape"]) for row in rows]
    if g_selection[0] <= 1:
        fail("initial selection degeneracy must be >1")
    if g_selection[-1] != 1:
        fail("selection degeneracy must decay to 1")
    if g_landscape[-1] <= 1:
        fail("landscape control must remain multiply degenerate")
    if g_landscape != [g_landscape[0]] * len(g_landscape):
        fail("landscape degeneracy must remain constant in this unselected control")
    for idx in range(1, len(rows)):
        expected = g_selection[idx] - g_selection[idx - 1]
        if as_int(rows[idx]["g_increment"]) != expected:
            fail(f"selection increment mismatch at level {idx}")
        if expected > 0:
            fail(f"selection degeneracy increased at level {idx}")
        expected_landscape = g_landscape[idx] - g_landscape[idx - 1]
        if as_int(rows[idx]["landscape_increment"]) != expected_landscape:
            fail(f"landscape increment mismatch at level {idx}")
    if rows[-1]["selection_survivors"] != REALIZED_WORLD:
        fail("final selection survivor must be w_SM")
    removed_nonempty = [row for row in rows if row["candidates_removed"] != "none"]
    if not removed_nonempty:
        fail("selection refinement must remove candidates at some levels")


def validate_p6_audit() -> None:
    rows = read_csv("p6_audit_step3.csv")
    by_id = {row["audit_id"]: row for row in rows}
    if "genuine_selection" not in by_id or "unselected_landscape" not in by_id:
        fail("P6 audit rows missing")
    selection = by_id["genuine_selection"]
    landscape = by_id["unselected_landscape"]
    if as_int(selection["initial_degeneracy"]) <= 1 or as_int(selection["final_degeneracy"]) != 1:
        fail("selection audit must start >1 and end at 1")
    if selection["final_survivors"] != REALIZED_WORLD:
        fail("selection audit must stabilize on w_SM")
    if not as_bool(selection["monotone_nonincreasing"]) or not as_bool(selection["stabilizes_to_selected_point"]):
        fail("selection audit must be monotone and stabilize to selected point")
    if as_int(selection["final_increment"]) != 0:
        fail("selection audit must have final stabilized increment 0")
    if as_int(landscape["final_degeneracy"]) <= 1:
        fail("landscape audit must remain multiply degenerate")
    if as_bool(landscape["stabilizes_to_selected_point"]):
        fail("landscape audit must not stabilize to selected point")
    if landscape["computed_sequence"].split("->")[-1] == "1":
        fail("landscape control secretly selected")


def validate_controls() -> None:
    rows = read_csv("controls_step3.csv")
    by_id = {row["control_id"]: row for row in rows}
    required = {
        "decays_vs_not",
        "monotone_selection_nonincreasing",
        "lands_on_w_SM",
        "landscape_not_secretly_selecting",
        "selection_carrier_not_field_pair",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing controls: {missing}")
    for control_id in sorted(required):
        if not as_bool(by_id[control_id]["passes_guard"]):
            fail(f"control failed: {control_id}")


def validate_verdicts() -> None:
    output = json.loads((ARTIFACT_DIR / "p6_decaying_degeneracy_output_step3.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output["verdict"]
    if verdict["type"] != "p6_decaying_degeneracy_audit_constructed":
        fail("wrong verdict type")
    if verdict["initial_selection_degeneracy"] <= 1:
        fail("initial selection degeneracy must be >1")
    if verdict["final_selection_degeneracy"] != 1:
        fail("final selection degeneracy must be 1")
    if not verdict["selection_decays_to_w_SM"]:
        fail("selection must decay to w_SM")
    if not verdict["landscape_nondecaying"]:
        fail("landscape must remain non-decaying")
    if not verdict["monotone_selection"]:
        fail("selection sequence must be monotone")
    if verdict["final_survivor"] != REALIZED_WORLD:
        fail("final survivor must be w_SM")
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
        "mode_b_target_lineage.csv": "R_cluster_a_after_step3_p6_decaying_degeneracy_audit",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_A_STEP3_DECAYS_VS_NOT",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_A_STEP4_CONSOLIDATE_SELECTION_LAYER_FRAME",
        "findings_cluster_a.md": "Step 3 - P6 Decaying-Degeneracy Audit",
    }
    for relative, marker in checks.items():
        text = (THREAD_DIR / relative).read_text(encoding="utf-8")
        if marker not in text:
            fail(f"ledger/finding marker {marker!r} missing from {relative}")


def validate_previous_steps() -> None:
    subprocess.run([sys.executable, str(STEP1_RUNNER), "--self"], cwd=THREAD_DIR / "steps", check=True)
    subprocess.run([sys.executable, str(STEP2_RUNNER), "--self"], cwd=THREAD_DIR / "steps", check=True)


def run_self() -> None:
    runpy.run_path(str(ARTIFACT_DIR / "p6_decaying_degeneracy_step3.py"), run_name="__main__")
    validate_required_files()
    validate_no_overclaim()
    validate_selection_not_field_model()
    validate_degeneracy_refinement()
    validate_p6_audit()
    validate_controls()
    validate_verdicts()
    validate_content_classification()
    validate_ledgers()
    print("PASS Cluster A Step 3 validator")


def run_chain() -> None:
    validate_previous_steps()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 3 artifacts.")
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
