#!/usr/bin/env python3
"""Validate Cluster A Step 1 artifacts."""

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
REQUIRED_FILES = [
    "shared_selection_layer_step1.py",
    "candidate_space_step1.csv",
    "frame_signatures_step1.csv",
    "controls_step1.csv",
    "shared_selection_layer_output_step1.json",
    "shared_selection_layer_output_step1.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step1.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderives the standard model\b",
    r"\bcomputes the number of generations\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy problem\b",
    r"\bpredicts the fermion masses\b",
    r"\bderives new physics\b",
    r"\broot_landed\s*[:=]\s*true\b",
    r"\bframe_transfer_certified\s*[:=]\s*true\b",
]

COSOURCING_GUARD_PATTERNS = [
    "co-sourcing",
    "common-refinement",
    "common_refinement",
    "F51",
    "F37",
    "psi",
    "field-layer",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    path = ARTIFACT_DIR / name
    with path.open(newline="", encoding="utf-8") as handle:
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
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".csv"}:
            continue
        if path.name == "run_step1.py":
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"overclaim pattern {pattern!r} found in {path.name}")


def validate_not_cosourcing_model() -> None:
    script = (ARTIFACT_DIR / "shared_selection_layer_step1.py").read_text(encoding="utf-8")
    for pattern in COSOURCING_GUARD_PATTERNS:
        if pattern in script:
            fail(f"selection frame script contains forbidden non-selection-layer term: {pattern}")
    candidates = read_csv("candidate_space_step1.csv")
    if not candidates:
        fail("candidate space is empty")
    headers = set(candidates[0].keys())
    forbidden_headers = {"psi", "field", "stress_energy", "born_audit", "metric"}
    if headers & forbidden_headers:
        fail(f"candidate space has field-layer columns: {sorted(headers & forbidden_headers)}")


def validate_candidate_space() -> None:
    rows = read_csv("candidate_space_step1.csv")
    if len(rows) < 8:
        fail("candidate space must contain realized world plus several alternatives")
    selected = [row for row in rows if as_bool(row["selected"])]
    if len(selected) != 1 or selected[0]["world_id"] != "w_SM":
        fail(f"w_SM must be the unique selected world, got {[row['world_id'] for row in selected]}")
    max_score = max(float(row["mu_score"]) for row in rows)
    w_sm_score = float(next(row["mu_score"] for row in rows if row["world_id"] == "w_SM"))
    if abs(max_score - w_sm_score) > 1e-10:
        fail("w_SM is not the genuine argmax of mu_score")
    if len({row["sm_sigma_fixed_readout"] for row in rows}) != 1:
        fail("SM Sigma_f shadow must be selection-forgetting and fixed across candidate worlds")
    facet_columns = ["gauge_facet", "generation_facet", "ew_scale_facet", "uv_completion_facet", "vacuum_facet"]
    for column in facet_columns:
        if len({row[column] for row in rows}) < 2:
            fail(f"facet {column} does not vary over W")


def validate_frame_signatures() -> None:
    rows = read_csv("frame_signatures_step1.csv")
    by_id = {row["object_id"]: row for row in rows}
    required = {
        "joint_structure_variable",
        "E019_gauge_group",
        "E020_generations_texture",
        "E043_EW_scale",
        "E009_UV_completion",
        "E037_vacuum",
        "selection_underdetermination",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing frame signature rows: {missing}")
    for object_id in sorted(required):
        row = by_id[object_id]
        count = as_int(row["obstruction_count"])
        if count <= 0:
            fail(f"{object_id} must have positive non-factorization obstruction")
        if not as_bool(row["non_descending_in_SM_Sigma_f"]):
            fail(f"{object_id} must be marked non-descending")
        if not as_bool(row["is_Lstar_selection_readout"]):
            fail(f"{object_id} must be marked as an L* selection readout")
        if row["witness"] == "none":
            fail(f"{object_id} must include an obstruction witness")


def validate_controls() -> None:
    rows = read_csv("controls_step1.csv")
    by_id = {row["control_id"]: row for row in rows}
    required = {
        "descending_observable_from_SM_inputs",
        "w_SM_is_genuine_argmax_of_mu",
        "selection_layer_not_field_readout_pair",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing control rows: {missing}")
    descending = by_id["descending_observable_from_SM_inputs"]
    if as_int(descending["obstruction_count"]) != 0 or not as_bool(descending["passes_guard"]):
        fail("descending-observable control must factor with obstruction 0")
    for control_id in ["w_SM_is_genuine_argmax_of_mu", "selection_layer_not_field_readout_pair"]:
        if not as_bool(by_id[control_id]["passes_guard"]):
            fail(f"{control_id} guard must pass")


def validate_verdicts() -> None:
    output = json.loads((ARTIFACT_DIR / "shared_selection_layer_output_step1.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output["verdict"]
    if verdict["type"] != "shared_selection_layer_frame_established":
        fail("wrong final verdict type")
    if verdict["selected_world"] != "w_SM":
        fail("selected world must be w_SM")
    if verdict["facet_count"] != 5:
        fail("facet count must be 5")
    if verdict["joint_obstruction_count"] <= 0:
        fail("joint obstruction must be positive")
    if verdict["selection_underdetermination_obstruction_count"] <= 0:
        fail("selection-underdetermination obstruction must be positive")
    if not verdict["descending_observable_control_factors"]:
        fail("descending observable control must factor")
    if not verdict["w_SM_argmax"]:
        fail("w_SM argmax must be true")
    if not verdict["is_selection_measure_layer"]:
        fail("schema must mark this as a selection/measure layer")
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
        if not row["grade"].strip():
            fail(f"missing grade for {row['output']}")


def validate_ledgers() -> None:
    checks = {
        "mode_b_target_lineage.csv": "R_cluster_a_after_step1_shared_selection_frame",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_A_STEP1_DESCENDING_CONTROL_FACTORS",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_A_STEP2_P2_SELECTION_CONSTRAINT_BUILD",
        "findings_cluster_a.md": "Step 1 - Shared Selection-Layer Frame",
    }
    for relative, marker in checks.items():
        text = (THREAD_DIR / relative).read_text(encoding="utf-8")
        if marker not in text:
            fail(f"ledger/finding marker {marker!r} missing from {relative}")


def run_self() -> None:
    runpy.run_path(str(ARTIFACT_DIR / "shared_selection_layer_step1.py"), run_name="__main__")
    validate_required_files()
    validate_no_overclaim()
    validate_not_cosourcing_model()
    validate_candidate_space()
    validate_frame_signatures()
    validate_controls()
    validate_verdicts()
    validate_content_classification()
    validate_ledgers()
    print("PASS Cluster A Step 1 validator")


def run_chain() -> None:
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 1 artifacts.")
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
