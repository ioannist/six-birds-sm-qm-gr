#!/usr/bin/env python3
"""Validate Step 66 E032 record-stability/definiteness artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = ARTIFACT_DIR / "e032_record_stability_definiteness_step66.py"

REQUIRED_FILES = [
    "step66_results_summary.md",
    "step66_schema.json",
    "content_classification_step66.csv",
    "nonclaim_boundary_step66.md",
    "step66_statement.tex",
    "run_step66.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "anti_smuggle_step66.csv",
    "qm_measurement_toy_step66.csv",
    "closure_package_step66.csv",
    "readout_states_step66.csv",
    "nonfactorization_witness_step66.csv",
    "record_stability_scores_step66.csv",
    "D_vs_Sigma_location_step66.csv",
    "source_readings_step66.csv",
]


def fail(message: str) -> None:
    print(f"run_step66.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step66_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 66,
        "orientation": "ModeB_E032_record_stability_definiteness",
        "active_residual": "E032 single-outcome selection",
        "exit_state": "RECORD_STABILITY_BLIND_TO_SELECTION",
        "verdict": "NAIVE_RECORD_STABILITY_DOES_NOT_FORCE_SINGLE_OUTCOME",
        "nonfactorization_witness_reproduced": True,
        "record_stability_on_diagonal_ensemble": True,
        "record_stability_on_selected_only": False,
        "anti_smuggle_pass": True,
        "forcing_touches_D_or_Sigma_f": "none",
        "solves_measurement_problem": False,
        "derives_collapse": False,
        "picks_a_shape": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    return schema


def validate_nonfactorization() -> None:
    rows = read_csv(ARTIFACT_DIR / "nonfactorization_witness_step66.csv")
    if len(rows) != 1:
        fail(f"expected one nonfactorization witness, got {len(rows)}")
    row = rows[0]
    if row["left_readout"] != "full_branching_state" or row["right_readout"] != "selected_single_outcome_k0":
        fail("unexpected nonfactorization readout pair")
    if row["left_pi1_selection"] == row["right_pi1_selection"]:
        fail("selection predicate did not distinguish witness pair")
    if row["L0_difference"] != "1" or row["D0_difference"] != "0":
        fail("B.2 witness L0/D0 differences incorrect")


def validate_record_scores() -> None:
    rows = {row["readout_id"]: row for row in read_csv(ARTIFACT_DIR / "record_stability_scores_step66.csv")}
    for key in ("full_branching_state", "selected_single_outcome_k0"):
        row = rows.get(key)
        if row is None:
            fail(f"missing record score {key}")
        for col in ("persistence_passes", "distinguishability_passes", "capacity_passes", "record_stability_passes"):
            if row[col] != "True":
                fail(f"{key} expected {col}=True")
        if row["requires_single_outcome"] != "False":
            fail(f"{key} record predicate smuggles single outcome")
    if rows["full_branching_state"]["actual_branch_count"] != "2":
        fail("full branching readout should have two actual branches")
    if rows["selected_single_outcome_k0"]["actual_branch_count"] != "1":
        fail("selected readout should have one actual branch")


def validate_anti_smuggle() -> None:
    rows = read_csv(ARTIFACT_DIR / "anti_smuggle_step66.csv")
    if len(rows) < 4:
        fail("anti-smuggle audit too small")
    failing = [row for row in rows if row["passes"] != "True"]
    if failing:
        fail(f"anti-smuggle failing rows: {failing}")
    checks = {row["gate"] for row in rows}
    required = {
        "record_requirement_has_no_uniqueness_clause",
        "diagonal_ensemble_evaluable",
        "component_conditions_satisfied_by_multibranch",
        "single_outcome_not_presupposed",
    }
    if checks != required:
        fail(f"unexpected anti-smuggle gates: {checks}")


def validate_D_vs_Sigma() -> None:
    rows = {row["property"]: row for row in read_csv(ARTIFACT_DIR / "D_vs_Sigma_location_step66.csv")}
    blind = rows.get("nonselective_record_stability")
    if blind is None:
        fail("missing nonselective_record_stability location row")
    if blind["forces_definiteness"] != "False" or blind["closure_slot"] != "Sigma_f":
        fail("nonselective record stability should be blind and Sigma_f-local")
    selector = rows.get("single_outcome_selection")
    if selector is None:
        fail("missing single_outcome_selection location row")
    if selector["forces_definiteness"] != "True":
        fail("single outcome row should mark definiteness forcing as external to naive records")


def validate_docs_and_overclaims() -> None:
    summary = (ARTIFACT_DIR / "step66_results_summary.md").read_text(encoding="utf-8")
    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary_step66.md").read_text(encoding="utf-8")
    for snippet in ("does not solve measurement", "record-stability is blind to selection", "picks neither"):
        if snippet not in summary:
            fail(f"summary missing caveat/result snippet: {snippet}")
    for snippet in ("does not solve the measurement problem", "Records alone do not force selection", "does not derive collapse"):
        if snippet not in nonclaim:
            fail(f"nonclaim missing snippet: {snippet}")
    joined = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in ("step66_results_summary.md", "step66_schema.json", "step66_statement.tex", "nonclaim_boundary_step66.md")
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


def validate_sources() -> None:
    rows = read_csv(ARTIFACT_DIR / "source_readings_step66.csv")
    names = {row["source"] for row in rows}
    if names != {"E032_card", "QM_record_stability_paper"}:
        fail(f"unexpected source readings: {names}")


def run_build() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def validate() -> None:
    validate_required_files()
    validate_schema()
    validate_nonfactorization()
    validate_record_scores()
    validate_anti_smuggle()
    validate_D_vs_Sigma()
    validate_docs_and_overclaims()
    validate_sources()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if args.chain:
        run_build()
    validate()
    print("run_step66.py: PASS")


if __name__ == "__main__":
    main()
