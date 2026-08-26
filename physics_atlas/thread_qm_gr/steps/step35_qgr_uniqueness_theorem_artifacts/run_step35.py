#!/usr/bin/env python3
"""Validate Step 35 T_QGR_Unique artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REPO_ROOT = ARTIFACT_DIR.parents[3]
STEP33_DIR = THREAD_DIR / "steps" / "step33_partb_type_uniqueness_artifacts"
STEP34_DIR = THREAD_DIR / "steps" / "step34_partb_instance_uniqueness_artifacts"

REQUIRED_FILES = [
    "T_QGR_Unique.tex",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "seven_gate_audit_step35.csv",
    "nonclaim_boundary.md",
    "run_step35.py",
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

REQUIRED_THEOREM_MARKERS = [
    "Bounded grammar",
    "Lemma 3",
    "Step 33",
    "BridgeMediatedRole",
    "minimum obstruction count is \\(3\\)",
    "Lemma 4",
    "Step 34",
    "0.5773502691896258",
    "0.4472135954999579",
    "rank \\(4\\) in dimension \\(6\\)",
    "extra coordinate",
    "T\\_QG\\_NoGo",
    "G\\_E018\\_FRAME\\_TRANSFER\\_EXTERNAL\\_REVIEW\\_STEP35",
    "unique minimal admissible common refinement up to isomorphism",
    "Super-minimal admissible refinements exist",
    "interpretation/quantum\\_gravity\\_is\\_illegal.md",
    "interpretation/ladder\\_vs\\_fork.md",
]


def fail(message: str) -> None:
    print(f"run_step35.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def source_path(source: str) -> Path:
    path = Path(source.strip())
    if path.is_absolute() and "physics_atlas" in path.parts:
        atlas_index = path.parts.index("physics_atlas")
        return REPO_ROOT.joinpath(*path.parts[atlas_index:])
    if not path.is_absolute():
        return THREAD_DIR / path
    return path


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step35.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def check_source_paths(rows: list[dict[str, str]], column: str = "source_artifacts") -> None:
    for row in rows:
        if not row.get(column):
            fail(f"row missing {column}: {row}")
        for source in row[column].split(";"):
            if not source_path(source).exists():
                fail(f"missing cited source artifact: {source}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    step33 = json.loads((STEP33_DIR / "type_uniqueness_output_step33.json").read_text(encoding="utf-8"))
    if step33.get("selected_family") != "BridgeMediatedRole":
        fail("Step 33 selected family is not BridgeMediatedRole")
    if step33.get("fired_families") != ["BridgeMediatedRole"]:
        fail("Step 33 did not fire exactly one family")
    if step33.get("coarsening_search", {}).get("minimum_obstruction_count") != 3:
        fail("Step 33 coarsening minimum is not 3")
    if step33.get("excluded_families_count") != 7:
        fail("Step 33 excluded family count is not 7")

    step34 = json.loads((STEP34_DIR / "instance_uniqueness_output_step34.json").read_text(encoding="utf-8"))
    verdict34 = step34.get("verdict", {})
    if verdict34.get("type") != "instance_uniqueness_minimal_common_refinement_up_to_equivalence":
        fail("Step 34 verdict mismatch")
    if verdict34.get("L_unique_minimal") is not True:
        fail("Step 34 L_unique_minimal not true")
    if verdict34.get("superminimal_admissible_refinements_exist") is not True:
        fail("Step 34 super-minimal control missing")
    controls34 = step34.get("controls", {})
    if controls34.get("superminimal_admissible") is not True or controls34.get("superminimal_minimal") is not False:
        fail("Step 34 M control does not show admissible but non-minimal")
    if controls34.get("union_admissible") is not False:
        fail("Step 34 union should be non-admissible")
    if controls34.get("lprime_iso_to_L") is not True:
        fail("Step 34 L prime iso control failed")

    theorem = (ARTIFACT_DIR / "T_QGR_Unique.tex").read_text(encoding="utf-8")
    for marker in REQUIRED_THEOREM_MARKERS:
        if marker not in theorem:
            fail(f"theorem missing marker {marker!r}")
    if "only admissible object" in theorem and "not a claim that the minimal package is the\nonly admissible refinement" not in theorem:
        fail("theorem appears to claim only-admissible-object uniqueness")
    if "root_landed" in theorem.lower():
        fail("theorem must not assert root_landed")

    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 35:
        fail("schema step is not 35")
    final = schema.get("final_verdict", {})
    if final.get("type") != "T_QGR_Unique_bounded_theorem_written":
        fail("schema final verdict mismatch")
    if final.get("part_b_complete") is not True:
        fail("schema must mark Part B complete")
    if final.get("program_complete_in_bounded_grammar") is not True:
        fail("schema must mark bounded program complete")
    if final.get("bounded_grammar_scope") is not True:
        fail("schema must keep bounded scope")
    if final.get("root_landed") is not False:
        fail("schema root_landed must remain false")
    if final.get("only_admissible_object_claimed") is not False:
        fail("schema must reject only-admissible-object claim")

    audit_rows = read_csv(ARTIFACT_DIR / "seven_gate_audit_step35.csv")
    if len(audit_rows) != 7:
        fail("seven-gate audit must have seven rows")
    for row in audit_rows:
        if row["status"] != "pass":
            fail(f"seven-gate audit row {row['gate']} is not pass")
    check_source_paths(audit_rows)

    claim_rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(claim_rows) < 10:
        fail("content classification has too few rows")
    check_source_paths(claim_rows)

    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for marker in [
        "unique resolution family",
        "unique minimal admissible common refinement up to isomorphism",
        "does not claim `L` is the only admissible object",
        "External frame-transfer review",
    ]:
        if marker not in nonclaim:
            fail(f"nonclaim boundary missing marker {marker!r}")

    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_T_QGR_Unique_bounded_theorem" not in lineage:
        fail("target lineage missing Step 35 residual")
    grammar = (THREAD_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_FRAME_TRANSFER_EXTERNAL_REVIEW_AFTER_T_QGR_UNIQUE" not in grammar:
        fail("grammar manifest missing post-theorem external review obligation")
    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP35_LEMMA3_CITED",
        "C_STEP35_LEMMA4_CITED",
        "C_STEP35_SEVEN_GATES_PASS",
        "C_STEP35_BOUNDED_UNIQUENESS_GRADE",
        "C_STEP35_PROGRAM_COMPLETE_IN_GSTAR",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 35 — T_QGR_Unique Bounded Theorem" not in findings:
        fail("findings missing Step 35 entry")

    print("run_step35.py: PASS")


if __name__ == "__main__":
    main()
