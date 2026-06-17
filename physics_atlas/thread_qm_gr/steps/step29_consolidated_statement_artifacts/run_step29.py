#!/usr/bin/env python3
"""Validate Step 29 consolidated statement artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent

REQUIRED_FILES = [
    "QM_GR_layer_toy_model_step29.tex",
    "consolidated_findings_step29.md",
    "content_classification_step29.csv",
    "nonclaim_boundary_step29.md",
    "step29_results_summary.md",
    "step29_schema.json",
    "run_step29.py",
]

FORBIDDEN_PHRASES = [
    "qg solved",
    "proves quantum gravity",
    "solves quantum gravity",
    "derives the proton mass",
    "derived proton mass",
    "closes qm-gr unconditionally",
    "discovers a new physical law",
    "predicts a new constant",
    "unconditional new-physics claim",
    "shadow-to-source promotion without an audited bridge",
    "frame-transfer certificate achieved",
]

REQUIRED_TEXT_MARKERS = [
    "native-law-verified",
    "toy-diagnostic",
    "external review",
    "Open Obligations",
    "BridgeMediatedRole",
    "G_nosmuggle",
    "F51",
    "semiclassical sourcing",
    "relational clock readout",
]

REQUIRED_STEP_MARKERS = [
    "Step 13",
    "Step 14",
    "Step 15",
    "Step 17",
    "Step 18",
    "Step 19",
    "Step 20",
    "Step 21",
    "Step 22",
    "Step 23",
    "Step 24",
    "Step 25",
    "Step 26",
    "Step 27",
    "Step 28",
]

VALID_GRADES = {
    "native-law-verified",
    "toy-diagnostic",
    "organizational/audit",
    "remaining external content",
}


def fail(message: str) -> None:
    print(f"run_step29.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step29.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def source_exists(source: str) -> bool:
    source = source.strip()
    if not source:
        return False
    return Path(source).exists()


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    schema = json.loads((ARTIFACT_DIR / "step29_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 29:
        fail("schema step is not 29")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "consolidated_statement_complete_for_external_review":
        fail("unexpected Step 29 verdict")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("new_construction_claimed") is not False:
        fail("Step 29 must not claim a new construction")

    tex = (ARTIFACT_DIR / "QM_GR_layer_toy_model_step29.tex").read_text(encoding="utf-8")
    md = (ARTIFACT_DIR / "consolidated_findings_step29.md").read_text(encoding="utf-8")
    combined = tex + "\n" + md
    for marker in REQUIRED_TEXT_MARKERS:
        if marker not in combined:
            fail(f"consolidated statement missing marker {marker!r}")
    for marker in REQUIRED_STEP_MARKERS:
        if marker not in combined:
            fail(f"consolidated statement missing citation marker {marker!r}")

    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary_step29.md").read_text(encoding="utf-8")
    for marker in ["does not", "External review", "toy", "complete physical model"]:
        if marker not in nonclaim:
            fail(f"nonclaim boundary missing scope marker {marker!r}")

    rows = read_csv(ARTIFACT_DIR / "content_classification_step29.csv")
    if len(rows) < 20:
        fail("content classification has too few claim rows")
    seen_ids = set()
    for row in rows:
        claim_id = row.get("claim_id", "")
        if not claim_id:
            fail("claim row missing claim_id")
        if claim_id in seen_ids:
            fail(f"duplicate claim_id {claim_id}")
        seen_ids.add(claim_id)
        if row.get("grade") not in VALID_GRADES:
            fail(f"claim {claim_id} has invalid grade {row.get('grade')!r}")
        if not row.get("claim") or not row.get("scope") or not row.get("source_steps"):
            fail(f"claim {claim_id} missing claim, scope, or source_steps")
        sources = [part for part in row.get("source_artifacts", "").split(";") if part.strip()]
        if not sources:
            fail(f"claim {claim_id} has no source artifact")
        missing = [source for source in sources if not source_exists(source)]
        if missing:
            fail(f"claim {claim_id} has missing source artifacts: {missing}")
    findings = Path("/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/findings_qm_gr.md").read_text(
        encoding="utf-8"
    )
    if "Step 29 — Consolidated QM-GR Layer Toy Model Statement" not in findings:
        fail("findings_qm_gr.md missing Step 29 entry")

    print("run_step29.py: PASS")


if __name__ == "__main__":
    main()
