#!/usr/bin/env python3
"""Validate Step 9 Mode T triple no-go theorem artifacts."""

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
    "T_E018_TripleNoGo.tex",
    "step9_results_summary.md",
    "step9_schema.json",
    "content_classification_step9.csv",
    "nonclaim_boundary_step9.md",
    "seven_gate_audit_step9.csv",
    "route_audit_step9.csv",
    "run_step9.py",
]


FORBIDDEN_PHRASES = [
    "proves " + "quantum gravity",
    "solves " + "quantum gravity",
    "derives " + "the proton mass",
    "closes " + "QM-GR unconditionally",
    "discovers " + "a new physical law",
    "predicts " + "a new constant",
    "quantum gravity is impossible",
    "qg is impossible",
    "no triple mechanism can ever exist",
    "all future mechanisms are impossible",
    "unbounded theorem",
    "absolute no-go beyond g*",
]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\broot_landed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bmode_t_exit_state\b.{0,20}\b(?:1|2|3)\b", re.I | re.S),
    re.compile(r"\b(?:unconditional|absolute)\s+(?:analytic\s+)?theorem\b.{0,120}\bE018\b", re.I | re.S),
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
    for path, label in [(LINEAGE, "lineage"), (GRAMMAR, "grammar")]:
        if not path.exists():
            fail(f"missing {label}")


def check_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step9_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 9:
        fail("schema step must be 9")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "bounded_grammar_no_go_theorem":
        fail("schema final verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("mode_t_exit_state") != 4:
        fail("schema mode_t_exit_state must be 4")
    if verdict.get("theorem_artifact") != "T_E018_TripleNoGo.tex":
        fail("schema theorem artifact mismatch")
    if verdict.get("next_grammar_delta") != "G_E018_IndependentDynamicsOrRecognition_v5":
        fail("schema next grammar mismatch")
    if schema["carrier"].get("grade") != "finite-carrier diagnostic theorem":
        fail("schema grade mismatch")
    evidence = schema["track_fields"].get("evidence_summary", {})
    expected = {
        "step4_coupled_normalized_xi": 0.5714285714285714,
        "step7_triple_normalized_xi": 1.0,
        "step7_coupled_normalized_xi": 0.14285714285714285,
        "step8_completion_xi_level_32": 0.4947207905172907,
        "step8_completion_xi_level_64": 0.5371910513210945,
        "step8_witness_gain_level_32": -0.02326224393247789,
        "step8_witness_gain_level_64": -0.08539192789918792,
    }
    for key, value in expected.items():
        if abs(float(evidence.get(key, 999)) - value) > 1e-12:
            fail(f"schema evidence mismatch for {key}")


def check_theorem_text() -> None:
    text = (ARTIFACT_DIR / "T_E018_TripleNoGo.tex").read_text(encoding="utf-8")
    required_markers = [
        "The bounded grammar",
        "Triple shared-completion bridge",
        "Non-circular generation",
        "Rejected smuggling routes",
        "Bounded triple-bridge no-go",
        "finite-carrier diagnostic theorem",
        "G_E018_IndependentDynamicsOrRecognition_v5",
    ]
    for marker in required_markers:
        if marker not in text:
            fail(f"theorem missing marker: {marker}")
    for value in [
        "0.5714285714285714",
        "0.14285714285714285",
        "0.4947207905172907",
        "0.5371910513210945",
        "-0.02326224393247789",
        "-0.08539192789918792",
    ]:
        if value not in text:
            fail(f"theorem missing evidence value {value}")


def check_gate_and_route_tables() -> None:
    gates = read_csv(ARTIFACT_DIR / "seven_gate_audit_step9.csv")
    expected_gates = {
        "T1_bounded_grammar_scope",
        "T2_typed_triple_bridge",
        "T3_non_circularity",
        "T4_finite_carrier_evidence",
        "T5_target_lineage_non_equivalence",
        "T6_nonclaim_boundary",
        "T7_next_grammar_obligation",
    }
    names = {row.get("gate", "") for row in gates}
    missing = expected_gates - names
    if missing:
        fail(f"missing seven-gate rows: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in gates):
        fail("all seven gates must pass")

    routes = read_csv(ARTIFACT_DIR / "route_audit_step9.csv")
    route_names = {row.get("route", "") for row in routes}
    for route in [
        "recognition_recombination",
        "pairwise_union",
        "orthogonal_witness_without_map",
        "native_triple_insertion",
        "local_stochastic_run",
        "rigged_diagonal_run",
    ]:
        if route not in route_names:
            fail(f"missing route audit row: {route}")
    verdicts = {row["route"]: row["verdict"] for row in routes}
    if verdicts["native_triple_insertion"] != "smuggling_reject":
        fail("native insertion route must be smuggling_reject")
    if verdicts["rigged_diagonal_run"] != "smuggling_reject":
        fail("rigged diagonal route must be smuggling_reject")
    if verdicts["local_stochastic_run"] != "run_level_obstruction":
        fail("run route verdict mismatch")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_ModeT_triple_nogo_theorem" not in lineage_text:
        fail("lineage missing Mode T residual")
    if "T_E018_TripleNoGo.tex" not in lineage_text:
        fail("lineage missing theorem artifact path")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "T_E018_TripleNoGo_MODE_T_STEP9" not in grammar_text:
        fail("grammar manifest missing theorem row")
    if "G_E018_IndependentDynamicsOrRecognition_v5" not in grammar_text:
        fail("grammar manifest missing G_v5")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*")) + [LINEAGE, GRAMMAR]
    for path in scan_paths:
        if path.name == "run_step9.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_theorem_text()
    check_gate_and_route_tables()
    check_ledgers()
    check_forbidden_text()
    print("Step 9 validation passed.")


if __name__ == "__main__":
    main()
