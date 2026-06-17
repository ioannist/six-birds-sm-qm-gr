#!/usr/bin/env python3
"""Validate Cluster A Step 4 artifacts."""

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
]
R_SM = 1.0e-4
TOL = 1.0e-8
REQUIRED_FILES = [
    "e043_scale_selection_step4.py",
    "scale_configs_step4.csv",
    "scale_nonfactorization_step4.csv",
    "two_horns_step4.csv",
    "controls_step4.csv",
    "e043_scale_selection_output_step4.json",
    "e043_scale_selection_output_step4.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step4.py",
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
        if path.name == "run_step4.py":
            continue
        if path.suffix.lower() not in {".py", ".md", ".txt", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"overclaim pattern {pattern!r} found in {path.name}")


def validate_selection_not_field_model() -> None:
    script = (ARTIFACT_DIR / "e043_scale_selection_step4.py").read_text(encoding="utf-8")
    for pattern in NON_SELECTION_MODEL_PATTERNS:
        if pattern in script:
            fail(f"Step 4 build script contains forbidden non-selection construction term: {pattern}")


def validate_scale_configs() -> None:
    rows = read_csv("scale_configs_step4.csv")
    if len(rows) < 6:
        fail("scale config toy must contain several configurations")
    realized = [row for row in rows if as_bool(row["realized"])]
    if len(realized) != 1 or realized[0]["config_id"] != "scale_SM":
        fail("scale_SM must be the unique realized scale config")
    if abs(float(realized[0]["r"]) - R_SM) > TOL:
        fail("realized r must equal r_SM")
    sigma_groups: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        sigma_groups.setdefault(row["EW_Sigma"], []).append(row)
    if not any(len(group) >= 3 and len({row["r"] for row in group}) >= 3 for group in sigma_groups.values()):
        fail("need same EW Sigma with multiple different r values")


def validate_nonfactorization() -> None:
    rows = read_csv("scale_nonfactorization_step4.csv")
    by_id = {row["test_id"]: row for row in rows}
    required = {"r_scale_ratio_from_EW_Sigma", "derived_EW_observable_from_EW_Sigma"}
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing nonfactorization rows: {missing}")
    r_row = by_id["r_scale_ratio_from_EW_Sigma"]
    derived_row = by_id["derived_EW_observable_from_EW_Sigma"]
    if as_int(r_row["obstruction_count"]) <= 0 or not as_bool(r_row["non_descending"]):
        fail("scale ratio must be non-descending with positive obstruction")
    if r_row["witness"] == "none":
        fail("scale-ratio obstruction must include a witness")
    if as_int(derived_row["obstruction_count"]) != 0 or as_bool(derived_row["non_descending"]):
        fail("derived EW observable must factor with obstruction 0")


def validate_two_horns() -> None:
    rows = read_csv("two_horns_step4.csv")
    by_horn: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_horn.setdefault(row["horn"], []).append(row)
    for horn in ["derivation_attractor", "measure_selection", "no_selection_no_attractor", "no_selection_flat_measure"]:
        if horn not in by_horn:
            fail(f"missing horn rows: {horn}")
    attractor = sorted(by_horn["derivation_attractor"], key=lambda row: as_int(row["step"]))
    if float(attractor[-1]["residual"]) > TOL or attractor[-1]["status"] != "reached_r_SM":
        fail("derivation attractor must reach r_SM within tolerance")
    attractor_residuals = [float(row["residual"]) for row in attractor]
    if not all(attractor_residuals[i + 1] <= attractor_residuals[i] + 1e-15 for i in range(len(attractor_residuals) - 1)):
        fail("attractor residuals must be non-increasing")
    measure_selected = [row for row in by_horn["measure_selection"] if as_bool(row["selected"])]
    if len(measure_selected) != 1 or abs(float(measure_selected[0]["r_value"]) - R_SM) > TOL:
        fail("measure horn must uniquely peak at r_SM")
    no_attr = sorted(by_horn["no_selection_no_attractor"], key=lambda row: as_int(row["step"]))
    if float(no_attr[-1]["residual"]) <= 1.0e-3:
        fail("no-attractor control must remain far from r_SM")
    flat = by_horn["no_selection_flat_measure"]
    if any(as_bool(row["selected"]) for row in flat):
        fail("flat-measure control must not select a unique r")
    if len({row["weight"] for row in flat}) != 1:
        fail("flat-measure control must have equal weights")


def validate_controls() -> None:
    rows = read_csv("controls_step4.csv")
    by_id = {row["control_id"]: row for row in rows}
    required = {
        "r_non_descending_positive",
        "derived_EW_observable_factors",
        "derivation_attractor_reaches_r_SM",
        "measure_peaks_at_r_SM",
        "no_selection_control_unfixed",
        "selection_carrier_not_field_pair",
    }
    missing = sorted(required - set(by_id))
    if missing:
        fail(f"missing controls: {missing}")
    for control_id in sorted(required):
        if not as_bool(by_id[control_id]["passes_guard"]):
            fail(f"control failed: {control_id}")


def validate_verdicts() -> None:
    output = json.loads((ARTIFACT_DIR / "e043_scale_selection_output_step4.json").read_text(encoding="utf-8"))
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = output["verdict"]
    if verdict["type"] != "e043_scale_selection_facet_constructed":
        fail("wrong verdict type")
    if abs(verdict["r_SM"] - R_SM) > TOL:
        fail("wrong r_SM")
    if verdict["r_non_descending_obstruction"] <= 0:
        fail("r obstruction must be positive")
    if verdict["derived_observable_obstruction"] != 0:
        fail("derived observable obstruction must be 0")
    if verdict["attractor_final_residual"] > TOL:
        fail("attractor final residual must be <= tolerance")
    if abs(verdict["measure_selected_r"] - R_SM) > TOL:
        fail("measure selected r must be r_SM")
    if not verdict["both_horns_select"] or not verdict["no_selection_unfixed"]:
        fail("both horns must select and no-selection must remain unfixed")
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
        "mode_b_target_lineage.csv": "R_cluster_a_after_step4_e043_scale_selection",
        "mode_b_constraint_ledger.csv": "C_CLUSTER_A_STEP4_NO_SELECTION_FAILS",
        "mode_b_grammar_manifest.csv": "G_CLUSTER_A_STEP5_CLUSTER_A_CONSOLIDATION_OR_ROBUSTNESS",
        "findings_cluster_a.md": "Step 4 - E043 Scale-Selection Facet",
    }
    for relative, marker in checks.items():
        text = (THREAD_DIR / relative).read_text(encoding="utf-8")
        if marker not in text:
            fail(f"ledger/finding marker {marker!r} missing from {relative}")


def validate_previous_steps() -> None:
    for runner in STEP_RUNNERS:
        subprocess.run([sys.executable, str(runner), "--self"], cwd=STEPS_DIR, check=True)


def run_self() -> None:
    runpy.run_path(str(ARTIFACT_DIR / "e043_scale_selection_step4.py"), run_name="__main__")
    validate_required_files()
    validate_no_overclaim()
    validate_selection_not_field_model()
    validate_scale_configs()
    validate_nonfactorization()
    validate_two_horns()
    validate_controls()
    validate_verdicts()
    validate_content_classification()
    validate_ledgers()
    print("PASS Cluster A Step 4 validator")


def run_chain() -> None:
    validate_previous_steps()
    run_self()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 4 artifacts.")
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
