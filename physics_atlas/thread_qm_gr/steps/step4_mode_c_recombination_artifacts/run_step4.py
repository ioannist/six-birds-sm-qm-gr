#!/usr/bin/env python3
"""Validate Step 4 Mode C recombination artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
LINEAGE = THREAD_DIR / "mode_b_target_lineage.csv"
GRAMMAR = THREAD_DIR / "mode_b_grammar_manifest.csv"


REQUIRED_FILES = [
    "step4_results_summary.md",
    "step4_schema.json",
    "content_classification_step4.csv",
    "nonclaim_boundary_step4.md",
    "step4_structural_statement.tex",
    "simulate_step4_recombination_xi.py",
    "simulation_output_step4.json",
    "simulation_output_step4.txt",
    "xi_diagnostic_step4.csv",
    "compatibility_conflicts_step4.csv",
    "recombination_audit_step4.csv",
    "no_smuggling_gates_step4.csv",
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
        "union spans " + "the basis",
        "span-union " + "trivially covers",
        "combine the lenses " + "-> Xi=0",
    ]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\bE2\s*(?:->|to)\s*E1\b", re.I),
    re.compile(r"\bE3\s*(?:->|to)\s*E2\b", re.I),
    re.compile(r"\b(?:union|span[- ]union)\b.{0,80}\b(?:therefore|implies|=>)\b.{0,60}\b(?:closes|closure|landing)\b", re.I | re.S),
    re.compile(r"\bXi\s*=\s*0\b.{0,80}\b(?:recombination|coupling)\b.{0,40}\b(?:closes|landing)\b", re.I | re.S),
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
    if not GRAMMAR.exists():
        fail("missing mode_b_grammar_manifest.csv")


def check_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step4_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 4:
        fail("schema step is not 4")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "bounded_grammar_no_go":
        fail("schema final_verdict.type must be bounded_grammar_no_go")
    if verdict.get("lawful_recombination_landed") is not False:
        fail("schema must keep lawful_recombination_landed false")
    if verdict.get("next_grammar_delta") != "G_E018_CoupledQGBridge_v1":
        fail("schema missing mandatory next grammar delta")
    xi = schema["track_fields"].get("xi_results", {})
    coupled = xi.get("coupled_joint_with_constraints_normalized", {})
    if abs(float(coupled.get("level_2", -1)) - (4.0 / 7.0)) > 1e-12:
        fail("schema coupled level_2 normalized residual mismatch")
    if abs(float(coupled.get("level_4", -1)) - (4.0 / 7.0)) > 1e-12:
        fail("schema coupled level_4 normalized residual mismatch")


def check_gate_statuses() -> None:
    rows = read_csv(ARTIFACT_DIR / "no_smuggling_gates_step4.csv")
    if len(rows) < 6:
        fail("no_smuggling_gates_step4.csv has fewer than six gates")
    expected = {
        "G1_source_profiles_declared",
        "G2_union_control_rejected",
        "G3_constraint_rows_declared",
        "G4_target_lineage_non_equivalence",
        "G5_no_unaudited_bridge",
        "G6_no_silent_status_upgrade",
    }
    gate_names = {row.get("gate", "") for row in rows}
    missing = expected - gate_names
    if missing:
        fail(f"missing gate rows: {sorted(missing)}")
    for row in rows:
        if not row.get("status"):
            fail("gate row missing status")


def check_simulation_output() -> None:
    payload = json.loads((ARTIFACT_DIR / "simulation_output_step4.json").read_text(encoding="utf-8"))
    stability = payload.get("refinement_stability", {})
    if abs(float(stability.get("coupled_absolute_delta", -1))) > 1e-12:
        fail("coupled residual refinement stability failed")
    if abs(float(stability.get("compatibility_absolute_delta", -1))) > 1e-12:
        fail("compatibility residual refinement stability failed")
    for result in payload.get("results", []):
        sector = float(result["sector_only_control_rejected"]["normalized_trace"])
        if abs(sector) > 1e-12:
            fail("sector-only control should be zero")
        coupled = float(result["coupled_joint_with_constraints"]["normalized_trace"])
        if abs(coupled - (4.0 / 7.0)) > 1e-12:
            fail("coupled constrained residual mismatch")
        raw = float(result["coupled_joint_with_constraints"]["raw_trace"])
        if abs(raw - 4.0) > 1e-12:
            fail("coupled constrained raw residual mismatch")
        checks = result.get("no_overread_check", {})
        if checks.get("sector_only_control_used_as_verdict") is not False:
            fail("sector-only control must not be used as verdict")
        if checks.get("compatibility_bridge_rows_used_as_native_probes") is not False:
            fail("bridge rows must not be native probes")


def check_lineage_and_grammar() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_ModeC_no_go_bridge_delta" not in lineage_text:
        fail("lineage missing Mode C no-go residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_CoupledQGBridge_v1" not in grammar_text:
        fail("grammar manifest missing required grammar delta")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE, GRAMMAR]
    phrases = forbidden_phrases()
    for path in scan_paths:
        if path.name == "run_step4.py" or path.is_dir():
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
    check_lineage_and_grammar()
    check_forbidden_text()
    print("Step 4 validation passed.")


if __name__ == "__main__":
    main()
