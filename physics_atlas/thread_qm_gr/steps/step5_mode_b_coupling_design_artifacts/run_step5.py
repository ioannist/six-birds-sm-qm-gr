#!/usr/bin/env python3
"""Validate Step 5 Mode B coupling-design artifacts."""

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
CONSTRAINTS = THREAD_DIR / "mode_b_constraint_ledger.csv"


REQUIRED_FILES = [
    "step5_results_summary.md",
    "step5_schema.json",
    "content_classification_step5.csv",
    "nonclaim_boundary_step5.md",
    "step5_structural_statement.tex",
    "simulate_step5_pstar_xi.py",
    "simulation_output_step5.json",
    "simulation_output_step5.txt",
    "xi_diagnostic_step5.csv",
    "bounded_grammar_step5.csv",
    "pstar_design_step5.csv",
    "bridge_closure_step5.csv",
    "no_smuggling_gates_step5.csv",
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
        "P* closes all bridges",
        "P* lands E018",
    ]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\bE2\s*(?:->|to)\s*E1\b", re.I),
    re.compile(r"\bE3\s*(?:->|to)\s*E2\b", re.I),
    re.compile(r"\b(?:assume|assumes|assuming)\s+compatibility\b.{0,80}\b(?:closes|closure|landing|landed)\b", re.I | re.S),
    re.compile(r"\b(?:free|native)\s+bridge\s+rows\b.{0,80}\b(?:close|closes|closure|landing|landed)\b", re.I | re.S),
    re.compile(r"\b(?:full|root)\s+(?:closure|landing)\b.{0,80}\b(?:self-certified|certified)\b", re.I | re.S),
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
    for path, label in [(LINEAGE, "lineage"), (GRAMMAR, "grammar"), (CONSTRAINTS, "constraint ledger")]:
        if not path.exists():
            fail(f"missing {label}")


def check_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step5_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 5:
        fail("schema step is not 5")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "candidate_Mode_B_design_partial":
        fail("schema final_verdict.type must be candidate_Mode_B_design_partial")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("next_grammar_delta") != "G_E018_BoundaryContinuumTripleBridge_v2":
        fail("schema missing G_v2 next grammar delta")
    if len(verdict.get("bridges_closed", [])) != 2 or len(verdict.get("bridges_survive", [])) != 2:
        fail("schema bridge closure counts incorrect")
    xi = schema["track_fields"].get("xi_results", {})
    coupled = xi.get("coupled_joint_normalized", {})
    if abs(float(coupled.get("level_2", -1)) - (2.0 / 7.0)) > 1e-12:
        fail("schema coupled level_2 normalized residual mismatch")
    if abs(float(coupled.get("level_4", -1)) - (2.0 / 7.0)) > 1e-12:
        fail("schema coupled level_4 normalized residual mismatch")


def check_bounded_grammar() -> None:
    rows = read_csv(ARTIFACT_DIR / "bounded_grammar_step5.csv")
    if len(rows) != 1:
        fail("bounded_grammar_step5.csv must have exactly one grammar row")
    row = rows[0]
    if row.get("grammar_id") != "G_E018_CoupledQGBridge_v1":
        fail("bounded grammar id mismatch")
    if "free compatibility bridge rows" not in row.get("excluded_designs", ""):
        fail("bounded grammar exclusions missing bridge-row exclusion")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    for marker in ["G_E018_CoupledQGBridge_v1_DECLARED_STEP5", "G_E018_BoundaryContinuumTripleBridge_v2"]:
        if marker not in grammar_text:
            fail(f"grammar manifest missing {marker}")


def check_gate_statuses() -> None:
    rows = read_csv(ARTIFACT_DIR / "no_smuggling_gates_step5.csv")
    if len(rows) < 6:
        fail("no_smuggling_gates_step5.csv has fewer than six gates")
    expected = {
        "G1_bounded_grammar_declared_first",
        "G2_no_bridge_smuggling",
        "G3_target_lineage_non_equivalence",
        "G4_typed_carrier_completion_audit",
        "G5_no_silent_full_landing",
        "G6_no_overread_controls",
    }
    gate_names = {row.get("gate", "") for row in rows}
    missing = expected - gate_names
    if missing:
        fail(f"missing gate rows: {sorted(missing)}")


def check_simulation_output() -> None:
    payload = json.loads((ARTIFACT_DIR / "simulation_output_step5.json").read_text(encoding="utf-8"))
    stability = payload.get("refinement_stability", {})
    if abs(float(stability.get("coupled_absolute_delta", -1))) > 1e-12:
        fail("coupled residual refinement stability failed")
    if abs(float(stability.get("all_bridges_absolute_delta", -1))) > 1e-12:
        fail("bridge residual refinement stability failed")
    for result in payload.get("results", []):
        coupled = float(result["coupled_joint"]["normalized_trace"])
        if abs(coupled - (2.0 / 7.0)) > 1e-12:
            fail("coupled residual mismatch")
        raw = float(result["coupled_joint"]["raw_trace"])
        if abs(raw - 2.0) > 1e-12:
            fail("coupled raw residual mismatch")
        bridge_results = result["bridge_results"]
        for name in ["Bridge_HED_LQG_area_geometry", "Bridge_LQG_AS_discrete_continuum"]:
            if abs(float(bridge_results[name]["normalized_trace"])) > 1e-12:
                fail(f"{name} should close in G_v1")
        for name in ["Bridge_HED_AS_boundary_continuum", "Bridge_triple_joint_package"]:
            if abs(float(bridge_results[name]["normalized_trace"]) - 1.0) > 1e-12:
                fail(f"{name} should survive in G_v1")
        checks = result.get("no_overread_check", {})
        if checks.get("residual_bridge_rows_used_as_native_probes") is not False:
            fail("residual bridge rows must not be native probes")
        if checks.get("bridge_rows_inserted_as_free_source_facts") is not False:
            fail("bridge rows inserted as source facts")
        if checks.get("pstar_is_not_assume_compatibility") is not True:
            fail("P* anti-tautology flag missing")


def check_lineage_grammar_constraints() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_Pstar_v1_boundary_triple_residual" not in lineage_text:
        fail("lineage missing Step 5 residual")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in ["C_STEP5_HED_AS_SURVIVES", "C_STEP5_TRIPLE_SURVIVES"]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE, GRAMMAR, CONSTRAINTS]
    phrases = forbidden_phrases()
    for path in scan_paths:
        if path.name == "run_step5.py" or path.is_dir():
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
    check_bounded_grammar()
    check_gate_statuses()
    check_simulation_output()
    check_lineage_grammar_constraints()
    check_forbidden_text()
    print("Step 5 validation passed.")


if __name__ == "__main__":
    main()
