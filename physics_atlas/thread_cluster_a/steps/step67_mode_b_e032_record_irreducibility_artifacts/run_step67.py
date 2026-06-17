#!/usr/bin/env python3
"""Validate Step 67 E032 record-irreducibility artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = ARTIFACT_DIR / "e032_record_irreducibility_step67.py"

REQUIRED_FILES = [
    "step67_results_summary.md",
    "step67_schema.json",
    "content_classification_step67.csv",
    "nonclaim_boundary_step67.md",
    "step67_statement.tex",
    "run_step67.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "record_property_battery_step67.csv",
    "anti_smuggle_step67.csv",
    "structural_argument_step67.csv",
    "frozen_step66_reuse_step67.csv",
]


def fail(message: str) -> None:
    print(f"run_step67.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step67_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 67,
        "orientation": "ModeB_E032_record_irreducibility",
        "exit_state": "SELECTION_RECORD_IRREDUCIBLE_STRUCTURAL",
        "verdict": "SELECTION_NOT_FORCED_BY_SIGMA_F_INTERNAL_RECORD_PROPERTIES",
        "battery_property_count": 5,
        "all_noncontrol_properties_blind": True,
        "structural_argument_grade": "structural",
        "selection_not_sigma_f_definable": True,
        "only_forcings_are_smuggle_or_beyond_sigma_f": True,
        "anti_smuggle_pass": True,
        "solves_measurement_problem": False,
        "derives_collapse": False,
        "picks_a_shape": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": True,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    return schema


def validate_battery() -> None:
    rows = read_csv(ARTIFACT_DIR / "record_property_battery_step67.csv")
    if len(rows) != 5:
        fail(f"expected 5 battery properties, got {len(rows)}")
    controls = [row for row in rows if row["is_control"] == "True"]
    noncontrols = [row for row in rows if row["is_control"] == "False"]
    if len(controls) != 1 or controls[0]["property_id"] != "global_exclusivity_anti_control":
        fail("expected one global-exclusivity anti-control")
    for row in noncontrols:
        if row["presupposes_uniqueness"] != "False":
            fail(f"non-control property presupposes uniqueness: {row['property_id']}")
        if row["is_sigma_f_internal"] != "True":
            fail(f"non-control property is not Sigma_f-internal: {row['property_id']}")
        if row["forces_selection"] != "False":
            fail(f"non-control property forces selection: {row['property_id']}")
        if row["full_branching_passes"] != row["selected_readout_passes"]:
            fail(f"non-control property not blind: {row['property_id']}")
    control = controls[0]
    if control["forces_selection"] != "True" or control["is_smuggle"] != "True" or control["presupposes_uniqueness"] != "True":
        fail("global exclusivity anti-control is not flagged as smuggle forcing")


def validate_anti_smuggle() -> None:
    rows = read_csv(ARTIFACT_DIR / "anti_smuggle_step67.csv")
    if len(rows) < 4:
        fail("anti-smuggle audit too small")
    failing = [row for row in rows if row["passes"] != "True"]
    if failing:
        fail(f"anti-smuggle failing rows: {failing}")
    checks = {row["gate"] for row in rows}
    required = {
        "noncontrol_properties_have_no_uniqueness_clause",
        "noncontrol_properties_evaluable_on_multibranch",
        "noncontrol_forcing_absent",
        "anti_control_flagged_as_smuggle_line",
    }
    if checks != required:
        fail(f"unexpected anti-smuggle gates: {checks}")


def validate_structural_argument() -> None:
    rows = read_csv(ARTIFACT_DIR / "structural_argument_step67.csv")
    by_step = {row["step"]: row for row in rows}
    required = {"premise_1", "premise_2", "inference", "conclusion"}
    if set(by_step) != required:
        fail(f"unexpected structural argument rows: {set(by_step)}")
    failing = [row for row in rows if row["passes"] != "True"]
    if failing:
        fail(f"structural argument failing rows: {failing}")
    if "pointer_basis" not in by_step["premise_2"]["evidence"]:
        fail("premise_2 does not cite shared Sigma_f key")


def validate_frozen_reuse() -> None:
    rows = read_csv(ARTIFACT_DIR / "frozen_step66_reuse_step67.csv")
    if len(rows) != 1:
        fail("expected one Step66 frozen reuse row")
    row = rows[0]
    if row["status"] != "imported_verbatim":
        fail("Step66 source not marked imported_verbatim")
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "STEP66_BUILD" not in source or "load_module" not in source:
        fail("build script does not import Step66 module")


def validate_docs_and_overclaims() -> None:
    summary = (ARTIFACT_DIR / "step67_results_summary.md").read_text(encoding="utf-8")
    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary_step67.md").read_text(encoding="utf-8")
    for snippet in ("record-irreducibility", "global_exclusivity_anti_control", "picks neither"):
        if snippet not in summary:
            fail(f"summary missing snippet: {snippet}")
    for snippet in ("does not solve the measurement problem", "does not derive collapse", "does not pick shape"):
        if snippet not in nonclaim:
            fail(f"nonclaim missing snippet: {snippet}")
    joined = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in ("step67_results_summary.md", "step67_schema.json", "step67_statement.tex", "nonclaim_boundary_step67.md")
    )
    forbidden = [
        r"\bsolves\s+the\s+measurement\s+problem\b",
        r"\bderives\s+collapse\b",
        r"\bproves\s+many-worlds\b",
        r"\bsingle\s+outcome\s+derived\b",
        r"\bmeasurement\s+problem\s+solved\b",
        r"\bunconditional\b",
        r"\bsolves_measurement_problem[\"']?\s*:\s*true\b",
        r"\bderives_collapse[\"']?\s*:\s*true\b",
        r"\bpicks_a_shape[\"']?\s*:\s*true\b",
        r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    ]
    for pattern in forbidden:
        if re.search(pattern, joined, flags=re.IGNORECASE):
            fail(f"forbidden overclaim matched: {pattern}")


def run_build() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def validate() -> None:
    validate_required_files()
    validate_schema()
    validate_battery()
    validate_anti_smuggle()
    validate_structural_argument()
    validate_frozen_reuse()
    validate_docs_and_overclaims()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if args.chain:
        run_build()
    validate()
    print("run_step67.py: PASS")


if __name__ == "__main__":
    main()
