#!/usr/bin/env python3
"""Validate Cluster A Step 5 artifacts."""

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
]
REALIZED_UV = "U_SM"
REALIZED_IR = "IR_SM_TOY"
REQUIRED_FILES = [
    "e009_uv_fiber_step5.py",
    "uv_fiber_step5.csv",
    "uv_nonfactorization_step5.csv",
    "consistency_selection_step5.csv",
    "controls_step5.csv",
    "e009_uv_fiber_output_step5.json",
    "e009_uv_fiber_output_step5.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step5.py",
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
        if path.name == "run_step5.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"overclaim pattern {pattern!r} found in {path.name}")


def validate_selection_not_field_model() -> None:
    script = (ARTIFACT_DIR / "e009_uv_fiber_step5.py").read_text(encoding="utf-8")
    for pattern in NON_SELECTION_MODEL_PATTERNS:
        if pattern in script:
            fail(f"Step 5 build script contains forbidden non-selection construction term: {pattern}")


def validate_uv_fiber() -> None:
    rows = read_csv("uv_fiber_step5.csv")
    if len(rows) < 8:
        fail("UV fiber toy must contain several UV theories")
    realized_fiber = [row for row in rows if row["IR_EFT_code"] == REALIZED_IR]
    if len(realized_fiber) <= 1:
        fail("realized IR fiber must contain multiple UV theories")
    if len({row["UV_content"] for row in realized_fiber}) <= 1:
        fail("realized IR fiber must have distinct UV contents")
    selected = [row for row in rows if as_bool(row["selected_in_realized_fiber"])]
    if len(selected) != 1 or selected[0]["uv_id"] != REALIZED_UV:
        fail(f"selector must uniquely choose U_SM, got {[row['uv_id'] for row in selected]}")
    if not as_bool(selected[0]["C_consistent"]):
        fail("selected UV must be consistent")
    inconsistent = [row for row in rows if not as_bool(row["C_consistent"])]
    consistent = [row for row in rows if as_bool(row["C_consistent"])]
    if not inconsistent or not consistent:
        fail("need both inconsistent and consistent UV candidates")
    for row in inconsistent:
        if row["constraint_action"] != "pruned" or row["consistency_defect"] == "none":
            fail(f"inconsistent UV not properly pruned: {row['uv_id']}")
    for row in consistent:
        if row["constraint_action"] != "survives" or row["consistency_defect"] != "none":
            fail(f"consistent UV not properly surviving: {row['uv_id']}")
    for row in rows:
        if row["IR_EFT_code"] not in row["P4_UV_to_IR_staging"]:
            fail(f"P4 staging does not end at IR code for {row['uv_id']}")


def validate_nonfactorization() -> None:
    rows = read_csv("uv_nonfactorization_step5.csv")
    by_id = {row["test_id"]: row for row in rows}
    required = {"UV_completion_from_IR_EFT", "derived_IR_observable_from_IR_EFT"}
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing nonfactorization rows: {missing}")
    uv_row = by_id["UV_completion_from_IR_EFT"]
    derived_row = by_id["derived_IR_observable_from_IR_EFT"]
    if as_int(uv_row["obstruction_count"]) <= 0 or not as_bool(uv_row["non_descending"]):
        fail("UV completion must be non-descending from IR")
    if uv_row["witness"] == "none":
        fail("UV non-descending row must include witness")
    if as_int(derived_row["obstruction_count"]) != 0 or as_bool(derived_row["non_descending"]):
        fail("derived IR observable must factor with obstruction 0")


def validate_consistency_selection() -> None:
    rows = read_csv("consistency_selection_step5.csv")
    if len(rows) != 1:
        fail("consistency_selection_step5.csv must contain one summary row")
    row = rows[0]
    if row["IR_EFT_code"] != REALIZED_IR:
        fail("summary must be for realized IR")
    if as_int(row["realized_fiber_size"]) <= 1:
        fail("realized fiber must be many-to-one")
    if as_int(row["admissible_fiber_size_before_selection"]) <= 1:
        fail("admissible fiber must remain >1 before selection")
    if as_int(row["selected_count_after_selection"]) != 1 or row["selected_UV"] != REALIZED_UV:
        fail("selector must collapse admissible fiber to U_SM")
    if as_int(row["nonselected_admissible_count"]) <= 0:
        fail("must have at least one non-selected admissible UV")
    if not row["pruned_in_realized_fiber"]:
        fail("realized fiber must include pruned inconsistent candidates")


def validate_controls() -> None:
    rows = read_csv("controls_step5.csv")
    by_id = {row["control_id"]: row for row in rows}
    required = {
        "many_to_one_realized_IR_fiber",
        "UV_non_descending_positive",
        "derived_IR_observable_factors",
        "consistency_prune_discriminates",
        "selection_collapses_admissible_fiber_to_U_SM",
        "selection_carrier_not_field_pair",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing controls: {missing}")
    for control_id in sorted(required):
        if not as_bool(by_id[control_id]["passes_guard"]):
            fail(f"control failed: {control_id}")


def validate_verdicts() -> None:
    output = json.loads((ARTIFACT_DIR / "e009_uv_fiber_output_step5.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output["verdict"]
    if verdict["type"] != "e009_uv_fiber_facet_constructed":
        fail("wrong verdict type")
    if verdict["realized_IR"] != REALIZED_IR:
        fail("wrong realized IR")
    if verdict["realized_fiber_size"] <= 1:
        fail("realized fiber must be many-to-one")
    if verdict["uv_non_descending_obstruction"] <= 0:
        fail("UV obstruction must be positive")
    if verdict["derived_IR_observable_obstruction"] != 0:
        fail("derived IR observable obstruction must be 0")
    if verdict["admissible_fiber_size_before_selection"] <= 1:
        fail("admissible fiber must remain >1 before selection")
    if verdict["selected_UV"] != REALIZED_UV:
        fail("selected UV must be U_SM")
    if verdict["nonselected_admissible_count"] <= 0:
        fail("must have a non-selected admissible UV")
    if not verdict["many_to_one"] or not verdict["selection_collapses"]:
        fail("many-to-one and selection-collapse flags must be true")
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
        "mode_b_target_lineage.csv": "R_cluster_a_after_step5_e009_uv_fiber",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_A_STEP5_SELECTION_COLLAPSES",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_A_STEP6_CLUSTER_A_CONSOLIDATION_OR_ROBUSTNESS",
        "findings_cluster_a.md": "Step 5 - E009 UV-Fiber Facet",
    }
    for relative, marker in checks.items():
        text = (THREAD_DIR / relative).read_text(encoding="utf-8")
        if marker not in text:
            fail(f"ledger/finding marker {marker!r} missing from {relative}")


def validate_previous_steps() -> None:
    for runner in STEP_RUNNERS:
        subprocess.run([sys.executable, str(runner), "--self"], cwd=STEPS_DIR, check=True)


def run_self() -> None:
    runpy.run_path(str(ARTIFACT_DIR / "e009_uv_fiber_step5.py"), run_name="__main__")
    validate_required_files()
    validate_no_overclaim()
    validate_selection_not_field_model()
    validate_uv_fiber()
    validate_nonfactorization()
    validate_consistency_selection()
    validate_controls()
    validate_verdicts()
    validate_content_classification()
    validate_ledgers()
    print("PASS Cluster A Step 5 validator")


def run_chain() -> None:
    validate_previous_steps()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 5 artifacts.")
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
