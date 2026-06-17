#!/usr/bin/env python3
"""Validate Step 1 artifacts for the QM-GR Mode A recognition-import audit."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
LINEAGE = THREAD_DIR / "mode_b_target_lineage.csv"


REQUIRED_FILES = [
    "step1_results_summary.md",
    "step1_schema.json",
    "content_classification_step1.csv",
    "nonclaim_boundary_step1.md",
    "step1_structural_statement.tex",
    "simulate_step1_holographic_xi.py",
    "simulation_output_step1.json",
    "simulation_output_step1.txt",
    "xi_diagnostic_step1.csv",
    "candidate_imports_step1.csv",
    "recognition_audit_step1.csv",
    "no_smuggling_gates_step1.csv",
]


def forbidden_phrases() -> list[str]:
    return [
        "proves " + "quantum gravity",
        "solves " + "quantum gravity",
        "derives " + "the proton mass",
        "closes " + "QM-GR unconditionally",
        "discovers " + "a new physical law",
        "predicts " + "a new constant",
        "cross-layer " + "DERIVATION",
        "shadow-to-source " + "promotion",
    ]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\bE2\s*(?:->|to)\s*E1\b", re.I),
    re.compile(r"\bE3\s*(?:->|to)\s*E2\b", re.I),
]


def fail(message: str) -> None:
    print(f"VALIDATION FAILED: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def check_required_files() -> None:
    for name in REQUIRED_FILES:
        path = ARTIFACT_DIR / name
        if not path.exists():
            fail(f"missing artifact {name}")
        if path.stat().st_size == 0:
            fail(f"empty artifact {name}")
    if not LINEAGE.exists():
        fail("missing mode_b_target_lineage.csv")


def check_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step1_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 1:
        fail("schema step is not 1")
    if schema["active_residual"] != "R_root_E018":
        fail("schema active_residual mismatch")
    verdict = schema["final_verdict"]
    if verdict.get("type") not in {"typed_obstruction", "E2_conditional_recognition_landing", "smuggling_reject"}:
        fail("schema final_verdict.type not allowed")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false for this Step 1 verdict")
    xi = schema["track_fields"].get("xi_results", {})
    full = xi.get("full_joint_target_normalized", {})
    if abs(float(full.get("level_2", -1)) - float(full.get("level_4", -2))) > 1e-12:
        fail("schema refinement stability mismatch")


def check_gate_statuses() -> None:
    rows = read_csv(ARTIFACT_DIR / "no_smuggling_gates_step1.csv")
    if len(rows) < 6:
        fail("no_smuggling_gates_step1.csv has fewer than six gates")
    for row in rows:
        if not row.get("gate") or not row.get("status"):
            fail("gate row missing gate or status")
    gate_names = {row["gate"] for row in rows}
    expected = {
        "G1_named_source_declared",
        "G2_target_lineage_non_equivalence",
        "G3_typed_carrier_and_lens",
        "G4_no_silent_status_upgrade",
        "G5_shadow_source_boundary",
        "G6_no_answer_row_overread",
    }
    missing = expected - gate_names
    if missing:
        fail(f"missing gate rows: {sorted(missing)}")


def check_simulation_output() -> None:
    payload = json.loads((ARTIFACT_DIR / "simulation_output_step1.json").read_text(encoding="utf-8"))
    stability = payload.get("refinement_stability", {})
    if stability.get("ratio_level_4_over_level_2") != 1.0:
        fail("simulation refinement ratio is not exactly 1.0")
    for result in payload.get("results", []):
        area_norm = float(result["rt_area_sector"]["normalized_trace"])
        if abs(area_norm) > 1e-12:
            fail("RT area sector residual is not numerically zero")
        full_norm = float(result["full_joint_target"]["normalized_trace"])
        if full_norm <= 0:
            fail("full joint residual should remain positive")
        checks = result.get("no_overread_check", {})
        if checks.get("bulk_geometry_amplitude_used_as_native_probe") is not False:
            fail("bulk amplitude overread check failed")
        if checks.get("p3_route_mismatch_used_as_native_probe") is not False:
            fail("P3 overread check failed")


def check_lineage() -> None:
    text = LINEAGE.read_text(encoding="utf-8")
    for residual in ["R_child_E018_HED_AdS_semiclassical", "R_child_E018_after_HED_full_joint_P3"]:
        if residual not in text:
            fail(f"lineage missing {residual}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE]
    phrases = forbidden_phrases()
    for path in scan_paths:
        if path.name == "run_step1.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in phrases:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_gate_statuses()
    check_simulation_output()
    check_lineage()
    check_forbidden_text()
    print("Step 1 validation passed.")


if __name__ == "__main__":
    main()
