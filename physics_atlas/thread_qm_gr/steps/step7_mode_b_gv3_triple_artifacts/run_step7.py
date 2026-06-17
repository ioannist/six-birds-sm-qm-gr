#!/usr/bin/env python3
"""Validate Step 7 Mode B G_v3 triple-audit artifacts."""

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
    "step7_results_summary.md",
    "step7_schema.json",
    "content_classification_step7.csv",
    "nonclaim_boundary_step7.md",
    "step7_structural_statement.tex",
    "simulate_step7_gv3_xi.py",
    "simulation_output_step7.json",
    "simulation_output_step7.txt",
    "xi_diagnostic_step7.csv",
    "bounded_grammar_step7.csv",
    "triple_audit_search_step7.csv",
    "bridge_closure_step7.csv",
    "target_equivalence_audit_step7.csv",
    "no_smuggling_gates_step7.csv",
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
        "G_v3 closes all bridges",
        "G_v3 lands E018",
        "pairwise union closes triple",
        "native triple insertion closes triple",
        "triple row insertion accepted",
        "primitive package coherence closes",
    ]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\bE2\s*(?:->|to)\s*E1\b", re.I),
    re.compile(r"\bE3\s*(?:->|to)\s*E2\b", re.I),
    re.compile(r"\bpairwise\s+u/v/w\s+union\b.{0,120}\b(?:accepted|verdict|landing)\b", re.I | re.S),
    re.compile(r"\bprimitive\s+package[- ]coherence\b.{0,120}\b(?:accepted|verdict|landing)\b", re.I | re.S),
    re.compile(r"\broot_landed\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step7_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 7:
        fail("schema step is not 7")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "bounded_grammar_saturation_no_go":
        fail("schema final_verdict.type must be bounded_grammar_saturation_no_go")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("next_structural_obligation") != "G_E018_RunGeneratedTripleMechanism_v4":
        fail("schema missing G_v4 structural obligation")
    if verdict.get("bridges_survive") != ["Bridge_triple_joint_package"]:
        fail("schema surviving bridge must be the triple package")
    xi = schema["track_fields"].get("xi_results", {})
    accepted = xi.get("accepted_search_coupled_joint_normalized", {})
    if abs(float(accepted.get("level_2", -1)) - (1.0 / 7.0)) > 1e-12:
        fail("schema accepted coupled level_2 residual mismatch")
    if abs(float(accepted.get("level_4", -1)) - (1.0 / 7.0)) > 1e-12:
        fail("schema accepted coupled level_4 residual mismatch")
    triple = xi.get("accepted_search_triple_normalized", {})
    if abs(float(triple.get("level_2", -1)) - 1.0) > 1e-12:
        fail("schema accepted triple level_2 residual mismatch")
    if abs(float(triple.get("level_4", -1)) - 1.0) > 1e-12:
        fail("schema accepted triple level_4 residual mismatch")


def check_bounded_grammar() -> None:
    rows = read_csv(ARTIFACT_DIR / "bounded_grammar_step7.csv")
    if len(rows) != 1:
        fail("bounded_grammar_step7.csv must have exactly one grammar row")
    row = rows[0]
    if row.get("grammar_id") != "G_E018_TriplePackageAudit_v3":
        fail("bounded grammar id mismatch")
    excluded = row.get("excluded_designs", "")
    for marker in ["native triple row insertion", "pairwise u/v/w union", "primitive package coherence"]:
        if marker not in excluded:
            fail(f"bounded grammar missing exclusion: {marker}")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    for marker in [
        "G_E018_TriplePackageAudit_v3_DECLARED_STEP7",
        "G_E018_RunGeneratedTripleMechanism_v4",
    ]:
        if marker not in grammar_text:
            fail(f"grammar manifest missing {marker}")


def check_gate_statuses() -> None:
    rows = read_csv(ARTIFACT_DIR / "no_smuggling_gates_step7.csv")
    expected = {
        "G1_bounded_grammar_declared_first",
        "G2_no_bridge_smuggling",
        "G3_target_lineage_non_equivalence",
        "G4_pairwise_union_reject",
        "G5_typed_carrier_completion_audit",
        "G6_no_silent_landing",
    }
    gate_names = {row.get("gate", "") for row in rows}
    missing = expected - gate_names
    if missing:
        fail(f"missing gate rows: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all no-smuggling gates must pass for the no-go audit")


def check_simulation_output() -> None:
    payload = json.loads((ARTIFACT_DIR / "simulation_output_step7.json").read_text(encoding="utf-8"))
    stability = payload.get("refinement_stability", {})
    for key in ["triple_absolute_delta", "coupled_absolute_delta"]:
        if abs(float(stability.get(key, -1))) > 1e-12:
            fail(f"{key} refinement stability failed")
    if payload.get("verdict_from_toy") != "bounded-grammar saturation no-go on G_v3":
        fail("simulation verdict mismatch")
    for result in payload.get("results", []):
        accepted = result["accepted_G_v3_search_result"]
        if accepted.get("candidate_type") != "no_admissible_independent_triple_atom":
            fail("accepted search candidate type mismatch")
        if abs(float(accepted["triple_bridge"]["normalized_trace"]) - 1.0) > 1e-12:
            fail("accepted triple residual should be one")
        if abs(float(accepted["coupled_joint"]["normalized_trace"]) - (1.0 / 7.0)) > 1e-12:
            fail("accepted coupled residual mismatch")
        controls = result["rejected_controls"]
        if abs(float(controls["pairwise_union_as_triple_completion"]["triple_bridge"]["normalized_trace"]) - 1.0) > 1e-12:
            fail("pairwise union control must leave triple residual")
        if abs(float(controls["native_triple_row_insertion"]["coupled_joint"]["normalized_trace"])) > 1e-12:
            fail("native triple control should zero only as rejected control")
        checks = result.get("no_overread_check", {})
        for key in [
            "pairwise_union_treated_as_triple_package",
            "triple_row_inserted_as_native_probe",
            "primitive_package_coherence_used",
        ]:
            if checks.get(key) is not False:
                fail(f"overread flag must be false: {key}")


def check_search_tables() -> None:
    rows = read_csv(ARTIFACT_DIR / "triple_audit_search_step7.csv")
    by_candidate = {row["candidate"]: row for row in rows}
    if by_candidate["accepted_G_v3_search"]["status"] != "bounded_saturation_no_go":
        fail("accepted search must be no-go")
    for candidate in [
        "pairwise_union_as_triple_completion",
        "independent_witness_without_bridge_map",
        "native_triple_row_insertion",
    ]:
        if by_candidate[candidate]["status"] != "rejected_control":
            fail(f"{candidate} must be rejected_control")
    bridge_rows = read_csv(ARTIFACT_DIR / "bridge_closure_step7.csv")
    triple = {row["bridge"]: row for row in bridge_rows}["Bridge_triple_joint_package"]
    if triple["status"] != "survives_G_v3_no_go":
        fail("triple bridge status mismatch")


def check_lineage_grammar_constraints() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_Gv3_triple_no_go" not in lineage_text:
        fail("lineage missing Step 7 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_RunGeneratedTripleMechanism_v4" not in grammar_text:
        fail("grammar manifest missing structurally different next obligation")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP7_PAIRWISE_UNION_REJECTED",
        "C_STEP7_NATIVE_TRIPLE_REJECTED",
        "C_STEP7_GV3_SATURATION_NO_GO",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE, GRAMMAR, CONSTRAINTS]
    phrases = forbidden_phrases()
    for path in scan_paths:
        if path.name == "run_step7.py" or path.is_dir():
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
    check_search_tables()
    check_lineage_grammar_constraints()
    check_forbidden_text()
    print("Step 7 validation passed.")


if __name__ == "__main__":
    main()
