#!/usr/bin/env python3
"""Validate Step 6 Mode B G_v2 artifacts."""

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
    "step6_results_summary.md",
    "step6_schema.json",
    "content_classification_step6.csv",
    "nonclaim_boundary_step6.md",
    "step6_structural_statement.tex",
    "simulate_step6_gv2_xi.py",
    "simulation_output_step6.json",
    "simulation_output_step6.txt",
    "xi_diagnostic_step6.csv",
    "bounded_grammar_step6.csv",
    "gv2_design_step6.csv",
    "bridge_closure_step6.csv",
    "no_smuggling_gates_step6.csv",
    "source_anchors_step6.csv",
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
        "G_v2 closes all bridges",
        "G_v2 lands E018",
        "triple bridge inserted",
        "assume all three sectors compatible",
    ]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\bE2\s*(?:->|to)\s*E1\b", re.I),
    re.compile(r"\bE3\s*(?:->|to)\s*E2\b", re.I),
    re.compile(r"\b(?:primitive|bare)\s+(?:global\s+)?compatibility\b.{0,120}\b(?:closes|closure|landing|landed)\b", re.I | re.S),
    re.compile(r"\b(?:free|native)\s+bridge\s+rows?\b.{0,120}\b(?:close|closes|closure|landing|landed)\b", re.I | re.S),
    re.compile(r"\btriple\s+(?:row|bridge)\b.{0,100}\b(?:native|source)\b.{0,100}\b(?:close|closes|closure|landing|landed)\b", re.I | re.S),
    re.compile(r"\b(?:full|root)\s+(?:closure|landing)\b.{0,100}\b(?:self-certified|certified)\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step6_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 6:
        fail("schema step is not 6")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "candidate_G_v2_design_partial":
        fail("schema final_verdict.type must be candidate_G_v2_design_partial")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("next_grammar_delta") != "G_E018_TriplePackageAudit_v3":
        fail("schema missing G_v3 next grammar delta")
    if len(verdict.get("bridges_closed", [])) != 3:
        fail("schema must list three closed bridges")
    if verdict.get("bridges_survive") != ["Bridge_triple_joint_package"]:
        fail("schema surviving bridge must be the triple package")
    xi = schema["track_fields"].get("xi_results", {})
    coupled = xi.get("coupled_joint_normalized", {})
    if abs(float(coupled.get("level_2", -1)) - (1.0 / 7.0)) > 1e-12:
        fail("schema coupled level_2 normalized residual mismatch")
    if abs(float(coupled.get("level_4", -1)) - (1.0 / 7.0)) > 1e-12:
        fail("schema coupled level_4 normalized residual mismatch")


def check_bounded_grammar() -> None:
    rows = read_csv(ARTIFACT_DIR / "bounded_grammar_step6.csv")
    if len(rows) != 1:
        fail("bounded_grammar_step6.csv must have exactly one grammar row")
    row = rows[0]
    if row.get("grammar_id") != "G_E018_BoundaryContinuumTripleBridge_v2":
        fail("bounded grammar id mismatch")
    if "holographic-RG boundary/continuum flow row w" not in row.get("new_source_atoms", ""):
        fail("bounded grammar missing w source atom")
    if "native triple row insertion" not in row.get("excluded_designs", ""):
        fail("bounded grammar exclusions missing triple-row exclusion")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    for marker in [
        "G_E018_BoundaryContinuumTripleBridge_v2_DECLARED_STEP6",
        "G_E018_TriplePackageAudit_v3",
    ]:
        if marker not in grammar_text:
            fail(f"grammar manifest missing {marker}")


def check_gate_statuses() -> None:
    rows = read_csv(ARTIFACT_DIR / "no_smuggling_gates_step6.csv")
    if len(rows) < 6:
        fail("no_smuggling_gates_step6.csv has fewer than six gates")
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
    if any(row.get("status") != "pass" for row in rows):
        fail("all no-smuggling gates must be pass or explicitly blocked; Step 6 expects pass")


def check_simulation_output() -> None:
    payload = json.loads((ARTIFACT_DIR / "simulation_output_step6.json").read_text(encoding="utf-8"))
    stability = payload.get("refinement_stability", {})
    for key in ["coupled_absolute_delta", "all_bridges_absolute_delta", "step5_survivor_pair_absolute_delta"]:
        if abs(float(stability.get(key, -1))) > 1e-12:
            fail(f"{key} refinement stability failed")
    for result in payload.get("results", []):
        coupled = float(result["coupled_joint"]["normalized_trace"])
        if abs(coupled - (1.0 / 7.0)) > 1e-12:
            fail("coupled residual mismatch")
        raw = float(result["coupled_joint"]["raw_trace"])
        if abs(raw - 1.0) > 1e-12:
            fail("coupled raw residual mismatch")
        bridge_results = result["bridge_results"]
        for name in [
            "Bridge_HED_LQG_area_geometry",
            "Bridge_LQG_AS_discrete_continuum",
            "Bridge_HED_AS_boundary_continuum",
        ]:
            if abs(float(bridge_results[name]["normalized_trace"])) > 1e-12:
                fail(f"{name} should close in G_v2")
        if abs(float(bridge_results["Bridge_triple_joint_package"]["normalized_trace"]) - 1.0) > 1e-12:
            fail("triple bridge should survive in G_v2")
        checks = result.get("no_overread_check", {})
        if checks.get("residual_bridge_rows_used_as_native_probes") is not False:
            fail("residual bridge rows must not be native probes")
        if checks.get("bridge_rows_inserted_as_free_source_facts") is not False:
            fail("bridge rows inserted as source facts")
        if checks.get("triple_row_inserted_as_native_probe") is not False:
            fail("triple row must not be native")
        if checks.get("gv2_is_not_primitive_global_compatibility") is not True:
            fail("anti-tautology flag missing")
        overread = result.get("target_equivalent_overread_control", {})
        if abs(float(overread.get("normalized_trace", -1))) > 1e-12:
            fail("overread control should show zero residual only as rejected control")


def check_bridge_table() -> None:
    rows = read_csv(ARTIFACT_DIR / "bridge_closure_step6.csv")
    by_name = {row["bridge"]: row for row in rows}
    if by_name["Bridge_HED_AS_boundary_continuum"]["status"] != "closed_by_G_v2_generation":
        fail("HED-AS bridge status mismatch")
    if by_name["Bridge_triple_joint_package"]["status"] != "survives_G_v2":
        fail("triple bridge status mismatch")


def check_lineage_grammar_constraints() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_Gv2_triple_package_residual" not in lineage_text:
        fail("lineage missing Step 6 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_TriplePackageAudit_v3" not in grammar_text:
        fail("grammar manifest missing G_v3")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in ["C_STEP6_HED_AS_CLOSED_BY_GV2", "C_STEP6_TRIPLE_SURVIVES"]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE, GRAMMAR, CONSTRAINTS]
    phrases = forbidden_phrases()
    for path in scan_paths:
        if path.name == "run_step6.py" or path.is_dir():
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
    check_bridge_table()
    check_lineage_grammar_constraints()
    check_forbidden_text()
    print("Step 6 validation passed.")


if __name__ == "__main__":
    main()
