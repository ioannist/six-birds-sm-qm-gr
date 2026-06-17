#!/usr/bin/env python3
"""Validate Step 37 non-coordinate/nonlinear mediator robustness artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8

REQUIRED_FILES = [
    "noncoordinate_nonlinear_mediator_step37.py",
    "linear_mediators_step37.csv",
    "nonlinear_mediators_step37.csv",
    "positive_detection_control_step37.csv",
    "mediator_robustness_output_step37.json",
    "mediator_robustness_output_step37.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step37.py",
]

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
    print(f"run_step37.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bool_cell(value: str) -> bool:
    return str(value).strip().lower() == "true"


def f(value: str) -> float:
    return float(value)


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step37.py"
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

    output = json.loads((ARTIFACT_DIR / "mediator_robustness_output_step37.json").read_text(encoding="utf-8"))
    if output.get("step") != 37:
        fail("output step is not 37")
    if output.get("linear_sample_count") != 14:
        fail("unexpected linear sample count")
    if output.get("nonlinear_sample_count") != 6:
        fail("unexpected nonlinear sample count")
    if output.get("all_actual_admissible_minimal_iso_to_L") is not True:
        fail("not all admissible-minimal actual mediators are iso to L")
    if output.get("actual_inequivalent_minimal_count") != 0:
        fail("actual inequivalent minimal mediator appeared")
    if output.get("positive_detection_control", {}).get("positive_detection_detected") is not True:
        fail("positive-detection control did not detect planted non-uniqueness")
    verdict = output.get("verdict", {})
    if verdict.get("type") != "instance_uniqueness_robust_general_linear_nonlinear_tested":
        fail("unexpected verdict type")
    if verdict.get("root_landed") is not False or verdict.get("frame_transfer_certified") is not False:
        fail("root landing or frame transfer must remain false")

    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 37:
        fail("schema step is not 37")
    final = schema.get("final_verdict", {})
    if final.get("type") != "instance_uniqueness_robust_general_linear_nonlinear_tested":
        fail("schema verdict mismatch")
    if final.get("positive_detection_detected") is not True:
        fail("schema missing positive detection")
    if final.get("actual_inequivalent_minimal_count") != 0:
        fail("schema should report no actual inequivalent minimal mediator")

    linear_rows = read_csv(ARTIFACT_DIR / "linear_mediators_step37.csv")
    if len(linear_rows) != 14:
        fail("linear mediator table must have 14 rows")
    minimal_linear = [row for row in linear_rows if bool_cell(row["admissible"]) and bool_cell(row["minimal"])]
    if not minimal_linear:
        fail("no admissible-minimal linear mediator sampled")
    for row in minimal_linear:
        if row["relation_to_L"] != "iso_to_L" or f(row["iso_residual"]) > TOL:
            fail(f"linear minimal mediator not iso to L: {row['mediator']}")
    rank3_rows = [row for row in linear_rows if "rank3" in row["mediator"]]
    if len(rank3_rows) != 5:
        fail("expected five rank3 controls")
    for row in rank3_rows:
        if bool_cell(row["carries_both"]):
            fail(f"rank3 mediator carries both endpoints: {row['mediator']}")
        if max(f(row["qm_residual"]), f(row["gr_residual"])) <= TOL:
            fail(f"rank3 mediator lacks positive obstruction: {row['mediator']}")
    super_rows = [row for row in linear_rows if row["relation_to_L"] == "super_minimal_nonminimal"]
    if not super_rows:
        fail("no linear super-minimal nonminimal control")
    for row in super_rows:
        if bool_cell(row["minimal"]):
            fail(f"super-minimal mediator recorded as minimal: {row['mediator']}")

    nonlinear_rows = read_csv(ARTIFACT_DIR / "nonlinear_mediators_step37.csv")
    if len(nonlinear_rows) != 6:
        fail("nonlinear mediator table must have 6 rows")
    for row in nonlinear_rows:
        if row["relation_to_L"] == "inequivalent_minimal":
            fail(f"actual nonlinear inequivalent minimal found: {row['mediator']}")
        if bool_cell(row["admissible"]) and bool_cell(row["minimal"]):
            if row["relation_to_L"] != "iso_to_L" or f(row["iso_residual"]) > TOL:
                fail(f"admissible-minimal nonlinear mediator not iso to L: {row['mediator']}")
        if row["relation_to_L"] == "sub_minimal_fails" and bool_cell(row["carries_both"]):
            fail(f"sub-minimal nonlinear mediator recorded as carrying both: {row['mediator']}")

    control_rows = read_csv(ARTIFACT_DIR / "positive_detection_control_step37.csv")
    if len(control_rows) < 2:
        fail("positive detection control must have at least two mediators")
    if not all(bool_cell(row["carries_endpoints"]) and bool_cell(row["strict"]) and bool_cell(row["minimal"]) for row in control_rows):
        fail("positive detection mediators must carry endpoints, be strict, and be minimal")
    if not all(bool_cell(row["inequivalent_to_other"]) for row in control_rows):
        fail("positive detection mediators must be inequivalent")

    claim_rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(claim_rows) < 8:
        fail("content classification has too few rows")
    check_source_paths(claim_rows)

    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for marker in [
        "non-axis-aligned linear mediators",
        "nonlinear equivalence notion",
        "positive-detection control",
        "External frame-transfer review",
    ]:
        if marker not in nonclaim:
            fail(f"nonclaim missing marker {marker!r}")

    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_noncoordinate_nonlinear_robustness" not in lineage:
        fail("target lineage missing Step 37 residual")
    grammar = (THREAD_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_FRAME_TRANSFER_EXTERNAL_REVIEW_AFTER_NONCOORDINATE_ROBUSTNESS" not in grammar:
        fail("grammar manifest missing post-Step37 review obligation")
    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP37_LINEAR_ROBUSTNESS",
        "C_STEP37_NONLINEAR_ROBUSTNESS",
        "C_STEP37_POSITIVE_DETECTION",
        "C_STEP37_SUB_SUPER_CONTROLS",
        "C_STEP37_BOUNDED_SCOPE",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 37 — Non-Coordinate and Nonlinear Mediator Robustness" not in findings:
        fail("findings missing Step 37 entry")

    print("run_step37.py: PASS")


if __name__ == "__main__":
    main()
