#!/usr/bin/env python3
"""Validate Step 36 adversarial F24 competitor artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8

REQUIRED_FILES = [
    "adversarial_f24_competitors_step36.py",
    "competitor_defeats_step36.csv",
    "coarsening_fits_step36.csv",
    "controls_step36.csv",
    "adversarial_competitors_output_step36.json",
    "adversarial_competitors_output_step36.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step36.py",
]

EXPECTED_FAMILIES = {
    "HiddenUpstreamRole",
    "CoarsenedRole",
    "BudgetedRole",
    "ScopedRole",
    "MemoryLayer",
}

EXPECTED_DEFEATS = {
    "HiddenUpstreamRole": "inadmissible_or_collapses_to_L",
    "CoarsenedRole": "positive_residual_even_nonlinear",
    "BudgetedRole": "positive_cutoff_residual",
    "ScopedRole": "fails_off_scope",
    "MemoryLayer": "inadmissible_or_collapses_to_L",
}

FORBIDDEN_PHRASES = [
    "qg impossible",
    "proven impossible",
    "quantum gravity is impossible",
    "metaphysically impossible",
    "proves quantum gravity",
    "solves quantum gravity",
    "derives the proton mass",
    "derived proton mass",
    "closes qm-gr unconditionally",
    "discovers a new physical law",
    "predicts a new constant",
    "unconditional new-physics claim",
    "shadow-to-source promotion without an audited bridge",
]


def fail(message: str) -> None:
    print(f"run_step36.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bool_cell(value: str) -> bool:
    return str(value).strip().lower() == "true"


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step36.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def resolve_source(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        fail(f"content source path must be thread-root-relative, got absolute path {path_text}")
    if path_text.startswith("steps/") or path_text.startswith("interpretation/"):
        return THREAD_DIR / path
    return ARTIFACT_DIR / path


def check_source_paths(rows: list[dict[str, str]], column: str = "source_artifacts") -> None:
    for row in rows:
        if not row.get(column):
            fail(f"row missing {column}: {row}")
        for source in row[column].split(";"):
            resolved = resolve_source(source)
            if not resolved.exists():
                fail(f"missing cited source artifact: {source} -> {resolved}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    output = json.loads((ARTIFACT_DIR / "adversarial_competitors_output_step36.json").read_text(encoding="utf-8"))
    if output.get("step") != 36:
        fail("output step is not 36")
    if output.get("all_defining_structures_present") is not True:
        fail("not all defining structures are present")
    if output.get("all_competitors_defeated") is not True:
        fail("a competitor passed or was not defeated")
    if output.get("all_controls_pass") is not True:
        fail("not all controls pass")
    verdict = output.get("verdict", {})
    if verdict.get("type") != "type_uniqueness_by_adversarial_defeat":
        fail("unexpected verdict type")
    if verdict.get("root_landed") is not False or verdict.get("frame_transfer_certified") is not False:
        fail("root landing or frame transfer certification must remain false")

    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 36:
        fail("schema step is not 36")
    final = schema.get("final_verdict", {})
    if final.get("type") != "type_uniqueness_by_adversarial_defeat":
        fail("schema verdict mismatch")
    if final.get("all_defining_structures_present") is not True:
        fail("schema missing defining-structure guard")
    if final.get("all_competitors_defeated") is not True:
        fail("schema missing competitor defeat")
    if final.get("all_controls_pass") is not True:
        fail("schema missing controls pass")

    competitor_rows = read_csv(ARTIFACT_DIR / "competitor_defeats_step36.csv")
    if len(competitor_rows) != 5:
        fail("expected five adversarial competitors")
    families = {row["family"] for row in competitor_rows}
    if families != EXPECTED_FAMILIES:
        fail(f"unexpected competitor families {families}")
    for row in competitor_rows:
        family = row["family"]
        if not bool_cell(row["defining_structure_present"]):
            fail(f"{family} lacks defining structure")
        if row["defeat_mechanism"] != EXPECTED_DEFEATS[family]:
            fail(f"{family} defeat mechanism mismatch")
        if not row["computed_witness"]:
            fail(f"{family} lacks computed witness")
        if bool_cell(row["passes_full_reconciliation"]):
            fail(f"{family} unexpectedly passes as full reconciliation")
        if not row["L_comparison"]:
            fail(f"{family} lacks L comparison")

    fit_rows = read_csv(ARTIFACT_DIR / "coarsening_fits_step36.csv")
    d3_rows = [row for row in fit_rows if row["target"] == "d3_curvature"]
    d2_rows = [row for row in fit_rows if row["target"] == "d2_transport_control"]
    if {int(row["degree"]) for row in d3_rows} != {1, 2, 3, 4}:
        fail("d3 fits must include degrees 1 through 4")
    if {int(row["degree"]) for row in d2_rows} != {1, 2, 3, 4}:
        fail("d2 control fits must include degrees 1 through 4")
    if not all(float(row["heldout_residual"]) > TOL and not bool_cell(row["passes_as_function"]) for row in d3_rows):
        fail("d3 nonlinear coarsening defeat is not positive for every degree")
    if not all(float(row["heldout_residual"]) <= TOL and bool_cell(row["passes_as_function"]) for row in d2_rows):
        fail("genuine d2 coarsening control does not pass")

    control_rows = read_csv(ARTIFACT_DIR / "controls_step36.csv")
    if len(control_rows) < 5:
        fail("controls table too short")
    for row in control_rows:
        if not bool_cell(row["passes"]):
            fail(f"control {row['control']} does not pass")
        if not row["computed_witness"]:
            fail(f"control {row['control']} lacks computed witness")

    claim_rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(claim_rows) < 10:
        fail("content classification has too few rows")
    check_source_paths(claim_rows)

    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for marker in [
        "full exact QM-GR reconciliation types in `G*`",
        "does not say those methods are universally invalid",
        "External frame-transfer review",
    ]:
        if marker not in nonclaim:
            fail(f"nonclaim missing marker {marker!r}")

    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_adversarial_F24_defeat" not in lineage:
        fail("target lineage missing Step 36 residual")
    grammar = (THREAD_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_FRAME_TRANSFER_EXTERNAL_REVIEW_AFTER_ADVERSARIAL_DEFEAT" not in grammar:
        fail("grammar manifest missing post-Step36 review obligation")
    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP36_COMPETITORS_BUILT",
        "C_STEP36_HIDDEN_DEFEATED",
        "C_STEP36_COARSENING_NONLINEAR_DEFEATED",
        "C_STEP36_BUDGET_DEFEATED",
        "C_STEP36_SCOPED_DEFEATED",
        "C_STEP36_CONTROLS_PASS",
        "C_STEP36_BOUNDED_SCOPE",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 36 — Adversarial F24 Competitor Defeat" not in findings:
        fail("findings missing Step 36 entry")

    print("run_step36.py: PASS")


if __name__ == "__main__":
    main()
