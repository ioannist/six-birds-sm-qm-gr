#!/usr/bin/env python3
"""Validate Step 32 bounded theorem artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "T_QG_NoGo.tex",
    "step32_results_summary.md",
    "step32_schema.json",
    "content_classification.csv",
    "seven_gate_audit_step32.csv",
    "nonclaim_boundary.md",
    "run_step32.py",
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
    "Directed route",
    "Fused route",
    "Step 30",
    "Step 31",
    "G_{nosmuggle}",
    "Part B",
    "co-sourcing",
    "interpretation/quantum\\_gravity\\_is\\_illegal.md",
    "interpretation/ladder\\_vs\\_fork.md",
]


def fail(message: str) -> None:
    print(f"run_step32.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step32.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    schema = json.loads((ARTIFACT_DIR / "step32_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 32:
        fail("schema step is not 32")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "T_QG_NoGo_bounded_theorem_written":
        fail("unexpected Step 32 verdict")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("bounded_grammar_scope") is not True:
        fail("bounded grammar scope missing")
    if verdict.get("part_b_uniqueness_obligation_open") is not True:
        fail("Part-B uniqueness obligation must remain open")

    theorem = (ARTIFACT_DIR / "T_QG_NoGo.tex").read_text(encoding="utf-8")
    for marker in REQUIRED_THEOREM_MARKERS:
        if marker not in theorem:
            fail(f"theorem missing marker {marker!r}")
    for route_marker in ["Step 30", "Step 31"]:
        if theorem.count(route_marker) < 1:
            fail(f"route failure stated without {route_marker} citation")

    audit_rows = read_csv(ARTIFACT_DIR / "seven_gate_audit_step32.csv")
    if len(audit_rows) != 7:
        fail("seven-gate audit must have exactly 7 rows")
    for row in audit_rows:
        if row["status"] != "pass":
            fail(f"seven-gate audit row {row['gate']} is not pass")

    claim_rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(claim_rows) < 10:
        fail("content classification has too few claims")
    for row in claim_rows:
        if not row.get("claim_id") or not row.get("source_artifacts"):
            fail("claim classification row missing id or source")
        for source in row["source_artifacts"].split(";"):
            if not (THREAD_DIR / source).exists():
                fail(f"missing cited source artifact: {source}")

    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for marker in ["does not", "Part-B uniqueness", "external review", "finite-carrier"]:
        if marker not in nonclaim:
            fail(f"nonclaim boundary missing marker {marker!r}")

    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_T_QG_NoGo_bounded_theorem" not in lineage:
        fail("target lineage missing Step 32 residual")
    grammar = (THREAD_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_PART_B_UNIQUENESS_STEP33" not in grammar:
        fail("grammar manifest missing Part-B obligation")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 32 — T_QG_NoGo Bounded Theorem" not in findings:
        fail("findings_qm_gr.md missing Step 32 entry")

    print("run_step32.py: PASS")


if __name__ == "__main__":
    main()
