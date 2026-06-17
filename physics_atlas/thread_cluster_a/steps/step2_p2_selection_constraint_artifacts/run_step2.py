#!/usr/bin/env python3
"""Validate Cluster A Step 2 artifacts."""

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
REQUIRED_FILES = [
    "p2_selection_constraint_step2.py",
    "anomaly_pruning_step2.csv",
    "selection_collapse_step2.csv",
    "joint_codetermination_step2.csv",
    "controls_step2.csv",
    "p2_selection_constraint_output_step2.json",
    "p2_selection_constraint_output_step2.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step2.py",
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
        if path.name == "run_step2.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"overclaim pattern {pattern!r} found in {path.name}")


def validate_selection_not_field_model() -> None:
    script = (ARTIFACT_DIR / "p2_selection_constraint_step2.py").read_text(encoding="utf-8")
    for pattern in NON_SELECTION_MODEL_PATTERNS:
        if pattern in script:
            fail(f"Step 2 build script contains forbidden non-selection construction term: {pattern}")


def validate_anomaly_pruning() -> None:
    rows = read_csv("anomaly_pruning_step2.csv")
    if len(rows) <= 9:
        fail("extended candidate set must add anomalous tokens beyond Step 1")
    pruned = [row for row in rows if row["constraint_action"] == "pruned"]
    survivors = [row for row in rows if row["constraint_action"] == "survives"]
    if not pruned:
        fail("constraint must prune at least one anomalous candidate")
    if len(survivors) <= 1:
        fail("anomaly-free survivor set must contain more than one candidate")
    for row in pruned:
        if as_int(row["A_GR"]) == 0 or as_bool(row["anomaly_free_computed"]):
            fail(f"pruned row has zero anomaly or anomaly_free true: {row['world_id']}")
    for row in survivors:
        if as_int(row["A_GR"]) != 0 or not as_bool(row["anomaly_free_computed"]):
            fail(f"survivor row has nonzero anomaly or anomaly_free false: {row['world_id']}")
    selected = [row for row in rows if as_bool(row["selected_after_constraint"])]
    if len(selected) != 1 or selected[0]["world_id"] != "w_SM":
        fail(f"post-constraint selector must uniquely select w_SM, got {[row['world_id'] for row in selected]}")
    if next(row for row in rows if row["world_id"] == "w_SM")["constraint_action"] != "survives":
        fail("w_SM must survive the anomaly constraint")


def validate_selection_collapse() -> None:
    rows = read_csv("selection_collapse_step2.csv")
    if len(rows) != 1:
        fail("selection_collapse_step2.csv must contain one summary row")
    row = rows[0]
    if as_int(row["survivor_count_before_selection"]) <= 1:
        fail("survivor set must be >1 before selection")
    if as_int(row["selected_count_after_selection"]) != 1:
        fail("selection must collapse survivors to one selected world")
    if row["selected_world"] != "w_SM":
        fail("selection must pick w_SM")
    if as_int(row["non_selected_survivor_count"]) <= 0:
        fail("at least one anomaly-free survivor must remain unselected")
    if as_int(row["pruned_count"]) <= 0:
        fail("at least one candidate must be pruned")


def validate_joint_codetermination() -> None:
    rows = read_csv("joint_codetermination_step2.csv")
    by_metric = {row["metric"]: row for row in rows}
    if "survivor_support" not in by_metric or "joint_selection_fixes_facets" not in by_metric:
        fail("joint co-determination rows missing")
    support = by_metric["survivor_support"]
    if as_int(support["missing_pair_count"]) <= 0:
        fail("survivor support must miss at least one gauge-generation Cartesian pair")
    if float(support["mutual_information_bits"]) <= 0.0:
        fail("gauge_code and n_gen support must have positive mutual information")
    if not as_bool(support["correlated_among_survivors"]):
        fail("survivor support must be marked correlated")
    if support["joint_selected_pair"] != "G_SM|3":
        fail("selected joint pair must be G_SM|3")
    fixed = by_metric["joint_selection_fixes_facets"]
    if fixed["selected_world"] != "w_SM" or fixed["joint_selected_pair"] != "G_SM|3":
        fail("joint selected pair row must fix w_SM and G_SM|3")


def validate_controls() -> None:
    rows = read_csv("controls_step2.csv")
    by_id = {row["control_id"]: row for row in rows}
    required = {
        "prune_discriminates_anomalous_removed",
        "prune_discriminates_anomaly_free_survives",
        "selection_collapses_survivors_to_w_SM",
        "further_step_anomaly_free_not_selected",
        "selection_carrier_not_field_pair",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing controls: {missing}")
    for control_id in sorted(required):
        if not as_bool(by_id[control_id]["passes_guard"]):
            fail(f"control failed: {control_id}")


def validate_verdicts() -> None:
    output = json.loads((ARTIFACT_DIR / "p2_selection_constraint_output_step2.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output["verdict"]
    if verdict["type"] != "p2_selection_constraint_constructed":
        fail("wrong verdict type")
    if verdict["extended_candidate_count"] <= 9:
        fail("extended candidate count must exceed Step-1 count")
    if verdict["survivor_count_before_selection"] <= 1:
        fail("survivors before selection must be >1")
    if verdict["pruned_count"] <= 0:
        fail("pruned count must be positive")
    if verdict["selected_world"] != "w_SM":
        fail("selected world must be w_SM")
    if not verdict["selection_collapses"] or not verdict["further_step"]:
        fail("selection collapse and further-step verdict flags must be true")
    if verdict["mutual_information_bits"] <= 0:
        fail("joint co-determination mutual information must be positive")
    if verdict["missing_gauge_n_gen_pair_count"] <= 0:
        fail("joint co-determination missing-pair count must be positive")
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
        if row["grade"] != "finite-toy-diagnostic" and row["grade"] != "organizational":
            fail(f"unexpected grade for {row['output']}: {row['grade']}")


def validate_ledgers() -> None:
    checks = {
        "mode_b_target_lineage.csv": "R_cluster_a_after_step2_p2_selection_constraint",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_A_STEP2_SELECTION_COLLAPSES",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_A_STEP3_P6_SELECTION_AUDIT_BUILD",
        "findings_cluster_a.md": "Step 2 - P2 Selection/Constraint",
    }
    for relative, marker in checks.items():
        text = (THREAD_DIR / relative).read_text(encoding="utf-8")
        if marker not in text:
            fail(f"ledger/finding marker {marker!r} missing from {relative}")


def validate_step1_still_passes() -> None:
    subprocess.run([sys.executable, str(STEP1_RUNNER), "--self"], cwd=THREAD_DIR / "steps", check=True)


def run_self() -> None:
    runpy.run_path(str(ARTIFACT_DIR / "p2_selection_constraint_step2.py"), run_name="__main__")
    validate_required_files()
    validate_no_overclaim()
    validate_selection_not_field_model()
    validate_anomaly_pruning()
    validate_selection_collapse()
    validate_joint_codetermination()
    validate_controls()
    validate_verdicts()
    validate_content_classification()
    validate_ledgers()
    print("PASS Cluster A Step 2 validator")


def run_chain() -> None:
    validate_step1_still_passes()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 2 artifacts.")
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
