#!/usr/bin/env python3
"""Validate Step 8 Mode B G_v4 run-generated triple artifacts."""

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
    "step8_results_summary.md",
    "step8_schema.json",
    "content_classification_step8.csv",
    "nonclaim_boundary_step8.md",
    "step8_structural_statement.tex",
    "simulate_step8_gv4_run.py",
    "simulation_output_step8.json",
    "simulation_output_step8.txt",
    "run_diagnostic_step8.csv",
    "bounded_grammar_step8.csv",
    "substrate_design_step8.csv",
    "witness_audit_step8.csv",
    "no_rigging_gates_step8.csv",
    "no_smuggling_gates_step8.csv",
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
        "G_v4 lands E018",
        "G_v4 closes all bridges",
        "triple_objective_in_substrate\": true",
        "triple_target_row_input\": true",
        "pairwise_union_used_as_witness\": true",
        "substrate is defined to make it cohere",
    ]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\bE2\s*(?:->|to)\s*E1\b", re.I),
    re.compile(r"\bE3\s*(?:->|to)\s*E2\b", re.I),
    re.compile(r"\broot_landed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bcandidate_pass\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step8_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 8:
        fail("schema step is not 8")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "run_level_no_go_obstruction":
        fail("schema final_verdict.type must be run_level_no_go_obstruction")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("candidate_pass") is not False:
        fail("schema must keep candidate_pass false")
    if verdict.get("next_grammar_delta") != "G_E018_IndependentDynamicsOrRecognition_v5":
        fail("schema missing G_v5 next grammar")
    controls = schema["carrier"].get("no_rigging_controls", {})
    for key in ["triple_objective_in_substrate", "triple_target_row_input", "pairwise_union_used_as_witness", "sector_readouts_used_in_update_rule"]:
        if controls.get(key) is not False:
            fail(f"no-rigging flag must be false: {key}")
    for key in ["witness_measured_after_run", "witness_heldout"]:
        if controls.get(key) is not True:
            fail(f"witness flag must be true: {key}")


def check_bounded_grammar() -> None:
    rows = read_csv(ARTIFACT_DIR / "bounded_grammar_step8.csv")
    if len(rows) != 1:
        fail("bounded_grammar_step8.csv must have exactly one grammar row")
    row = rows[0]
    if row.get("grammar_id") != "G_E018_RunGeneratedTripleMechanism_v4":
        fail("bounded grammar id mismatch")
    excluded = row.get("excluded_designs", "")
    for marker in ["triple objective", "triple target row", "pairwise-union witness", "post-hoc diagonal forcing"]:
        if marker not in excluded:
            fail(f"bounded grammar missing exclusion: {marker}")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    for marker in [
        "G_E018_RunGeneratedTripleMechanism_v4_DECLARED_STEP8",
        "G_E018_IndependentDynamicsOrRecognition_v5",
    ]:
        if marker not in grammar_text:
            fail(f"grammar manifest missing {marker}")


def check_gate_statuses() -> None:
    for csv_name, expected in [
        (
            "no_rigging_gates_step8.csv",
            {
                "R1_no_triple_objective_in_substrate",
                "R2_no_target_row_input",
                "R3_witness_measured_after_run",
                "R4_witness_not_pairwise_union",
                "R5_no_posthoc_diagonal_forcing",
                "R6_two_refinement_audit",
            },
        ),
        (
            "no_smuggling_gates_step8.csv",
            {
                "G1_bounded_run_grammar_declared_first",
                "G2_no_built_in_triple",
                "G3_witness_independence",
                "G4_target_lineage_non_equivalence",
                "G5_two_refinement_run_audit",
                "G6_rejected_controls_fenced",
            },
        ),
    ]:
        rows = read_csv(ARTIFACT_DIR / csv_name)
        names = {row.get("gate", "") for row in rows}
        missing = expected - names
        if missing:
            fail(f"{csv_name} missing gates: {sorted(missing)}")
        if any(row.get("status") != "pass" for row in rows):
            fail(f"{csv_name} must have pass statuses")


def check_simulation_output() -> None:
    payload = json.loads((ARTIFACT_DIR / "simulation_output_step8.json").read_text(encoding="utf-8"))
    if payload.get("verdict_from_run") != "run-level obstruction":
        fail("simulation verdict mismatch")
    stability = payload["refinement_stability"]
    if stability.get("candidate_pass_all_levels") is not False:
        fail("candidate pass should be false")
    expected = {
        32: {
            "xi": 0.4947207905172907,
            "gain": -0.02326224393247789,
        },
        64: {
            "xi": 0.5371910513210945,
            "gain": -0.08539192789918792,
        },
    }
    for result in payload.get("results", []):
        n = int(result["n_cells"])
        if n not in expected:
            fail(f"unexpected refinement level {n}")
        xi = float(result["completion_fixed_point_xi"]["normalized_trace"])
        gain = float(result["independent_witness"]["heldout_interaction_gain"])
        if abs(xi - expected[n]["xi"]) > 1e-12:
            fail(f"completion xi mismatch for N={n}")
        if abs(gain - expected[n]["gain"]) > 1e-12:
            fail(f"witness gain mismatch for N={n}")
        if result.get("candidate_pass") is not False:
            fail(f"N={n} candidate_pass should be false")
        checks = result.get("no_rigging_check", {})
        for key in ["triple_objective_in_substrate", "triple_target_row_input", "pairwise_union_used_as_witness", "sector_readouts_used_in_update_rule"]:
            if checks.get(key) is not False:
                fail(f"N={n} rigging flag should be false: {key}")
        for key in ["witness_measured_after_run", "witness_heldout"]:
            if checks.get(key) is not True:
                fail(f"N={n} witness flag should be true: {key}")
        rigged = float(result["rejected_controls"]["rigged_diagonal_completion"]["normalized_trace"])
        if rigged > 1e-10:
            fail(f"N={n} rigged control should be near zero")


def check_diagnostic_tables() -> None:
    rows = read_csv(ARTIFACT_DIR / "witness_audit_step8.csv")
    if len(rows) != 2:
        fail("witness audit must have two refinement rows")
    for row in rows:
        if row["candidate_pass"].lower() != "false":
            fail("witness audit candidate_pass must be false")
        if row["verdict"] != "run_level_obstruction":
            fail("witness audit verdict mismatch")
    diag = read_csv(ARTIFACT_DIR / "run_diagnostic_step8.csv")
    statuses = {row["status"] for row in diag}
    if "fails_candidate_threshold" not in statuses:
        fail("run diagnostic must include failed candidate thresholds")
    if "rejected_control" not in statuses:
        fail("run diagnostic must include rejected controls")


def check_lineage_grammar_constraints() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_Gv4_run_obstruction" not in lineage_text:
        fail("lineage missing Step 8 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_IndependentDynamicsOrRecognition_v5" not in grammar_text:
        fail("grammar manifest missing G_v5")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP8_NO_BUILT_IN_TRIPLE",
        "C_STEP8_PAIRWISE_UNION_WITNESS_REJECTED",
        "C_STEP8_RIGGED_DIAGONAL_REJECTED",
        "C_STEP8_RUN_OBSTRUCTION",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE, GRAMMAR, CONSTRAINTS]
    phrases = forbidden_phrases()
    for path in scan_paths:
        if path.name == "run_step8.py" or path.is_dir():
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
    check_diagnostic_tables()
    check_lineage_grammar_constraints()
    check_forbidden_text()
    print("Step 8 validation passed.")


if __name__ == "__main__":
    main()
