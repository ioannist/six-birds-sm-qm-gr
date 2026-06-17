#!/usr/bin/env python3
"""Validate Step 14 refinement-stability artifacts."""

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
    "refine_neutral_currency_step14.py",
    "refinement_lift_matrices_step14.json",
    "refinement_stability_step14.csv",
    "lift_nontriviality_step14.csv",
    "refinement_stability_output_step14.json",
    "refinement_stability_output_step14.txt",
    "structural_constraint_step14.md",
    "step14_results_summary.md",
    "step14_schema.json",
    "content_classification_step14.csv",
    "nonclaim_boundary_step14.md",
    "construction_gate_audit_step14.csv",
    "run_step14.py",
]


FORBIDDEN_PHRASES = [
    "proves " + "quantum gravity",
    "solves " + "quantum gravity",
    "quantum gravity solved",
    "derives " + "the proton mass",
    "closes " + "QM-GR unconditionally",
    "discovers " + "a new physical law",
    "predicts " + "a new constant",
    "cross-layer " + "DERIVATION",
    "shadow-to-source " + "promotion",
]


LITERATURE_PATTERNS = [
    ("holography", re.compile(r"\bholography\b", re.I)),
    ("AdS", re.compile(r"(?<![A-Za-z])AdS(?![A-Za-z])")),
    ("CFT", re.compile(r"(?<![A-Za-z])CFT(?![A-Za-z])")),
    ("RT/HRT", re.compile(r"\bRT/HRT\b")),
    ("LQG", re.compile(r"(?<![A-Za-z])LQG(?![A-Za-z])")),
    ("asymptotic safety", re.compile(r"\basymptotic safety\b", re.I)),
    ("spin network", re.compile(r"\bspin network\b", re.I)),
]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\broot_landed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bidentity_lift_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\btrivial_lift_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bmixing_control_passes\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bcircular_distance_from_self_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bone_hot_set_cover_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bliterature_program_terms_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\btarget_layer_inserted\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bendpoint_derivation_claimed\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step14_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 14:
        fail("schema step must be 14")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "refinement_stable_candidate_external_review_required":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("rung_coherence_passes") is not True:
        fail("schema rung_coherence_passes must be true")
    if verdict.get("external_review_required") is not True:
        fail("schema must require external review")
    if verdict.get("next_move") != "RUNG_3_AUDIT_ON_REFINEMENT_STABLE_CURRENCY":
        fail("schema next move mismatch")
    controls = schema["carrier"]["no_smuggling_controls"]
    for key in [
        "identity_lift_used",
        "trivial_lift_used",
        "mixing_control_passes",
        "circular_distance_from_self_used",
        "one_hot_set_cover_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
    ]:
        if controls.get(key) is not False:
            fail(f"no-smuggling flag must be false: {key}")
    if controls.get("step13_currency_loaded") is not True:
        fail("schema must confirm Step-13 currency loaded")
    residuals = schema["track_fields"]["commutator_residuals"]
    if float(residuals["stable_commutator_max"]) > 1e-10:
        fail("stable commutator too large")
    if float(residuals["mixing_commutator_min"]) <= 0.25:
        fail("mixing commutator too small")
    nontriv = schema["track_fields"]["lift_nontriviality"]
    if nontriv.get("identity_shape") is not False:
        fail("lift must not be identity-shaped")
    if float(nontriv["expansion_ratio"]) != 2.0:
        fail("lift expansion ratio must be 2")


def check_payload() -> None:
    payload = json.loads((ARTIFACT_DIR / "refinement_stability_output_step14.json").read_text(encoding="utf-8"))
    verdict = payload["verdict"]
    for key in [
        "refinement_stable",
        "stable_lift_passes",
        "mixing_control_fails",
        "lift_nontrivial",
        "compression_survives",
        "distinct_shadows_survive_stable",
    ]:
        if verdict.get(key) is not True:
            fail(f"payload verdict flag must be true: {key}")
    checks = payload["no_smuggling_check"]
    for key in [
        "identity_lift_used",
        "trivial_lift_used",
        "mixing_control_passes",
        "circular_distance_from_self_used",
        "one_hot_set_cover_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
    ]:
        if checks.get(key) is not False:
            fail(f"payload no-smuggling flag must be false: {key}")
    if checks.get("step13_currency_loaded") is not True:
        fail("payload must confirm Step-13 currency loaded")
    residuals = payload["observed_residuals"]
    if float(residuals["stable_commutator_max"]) > 1e-10:
        fail("payload stable residual too large")
    if float(residuals["mixing_commutator_min"]) <= 0.25:
        fail("payload mixing residual too small")
    if "two-shadow diagram" not in payload.get("structural_constraint", ""):
        fail("payload structural constraint missing commutation statement")


def check_tables() -> None:
    rows = read_csv(ARTIFACT_DIR / "refinement_stability_step14.csv")
    by_case: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)
    for case in ["stable_lift", "mixing_control"]:
        if case not in by_case:
            fail(f"missing case {case}")
        if len(by_case[case]) != 2:
            fail(f"case {case} must have two transitions")
    if any(row["status"] != "passes_candidate" or row["shadow_structure_survives"] != "True" for row in by_case["stable_lift"]):
        fail("stable lift rows must pass")
    if any(row["status"] != "fails_as_control_mixing" or row["shadow_structure_survives"] != "False" for row in by_case["mixing_control"]):
        fail("mixing control rows must fail")
    if any(float(row["combined_commutator_residual"]) <= 0.25 for row in by_case["mixing_control"]):
        fail("mixing residual must be large")

    lift_rows = read_csv(ARTIFACT_DIR / "lift_nontriviality_step14.csv")
    if len(lift_rows) != 2:
        fail("lift nontriviality must have two transitions")
    if any(row["identity_shape"] != "False" or row["nontrivial_refinement"] != "True" for row in lift_rows):
        fail("stable lift must be nontrivial and non-identity")
    if any(float(row["expansion_ratio"]) != 2.0 for row in lift_rows):
        fail("stable lift expansion ratio must be 2")


def check_matrices_and_constraint() -> None:
    matrices = json.loads((ARTIFACT_DIR / "refinement_lift_matrices_step14.json").read_text(encoding="utf-8"))
    for transition in ["1_to_2", "2_to_3"]:
        data = matrices["transitions"].get(transition)
        if data is None:
            fail(f"missing matrix transition {transition}")
        stable = data["stable_lift"]
        if len(stable) == 0 or len(stable) == len(stable[0]):
            fail("stable lift must not be square identity-shaped")
        if data["stable_lift"] == data["mixing_lift"]:
            fail("mixing lift must differ from stable lift")
    constraint = (ARTIFACT_DIR / "structural_constraint_step14.md").read_text(encoding="utf-8")
    for phrase in [
        "S_QM^{n+1} L_u = L_QM S_QM^n",
        "S_GR^{n+1} L_u = L_GR S_GR^n",
        "ker(S_QM)",
        "ker(S_GR)",
    ]:
        if phrase not in constraint:
            fail(f"structural constraint missing {phrase}")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step14.csv")
    expected = {
        "C1_step13_currency_loaded",
        "C2_nontrivial_refinement_lift",
        "C3_shadow_commutation_stable",
        "C4_compression_survives",
        "C5_distinct_shadows_survive",
        "C6_mixing_control_fails",
        "C7_no_circular_distance_test",
        "C8_structural_constraint_extracted",
        "C9_next_move_named",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_RUNG1_on_RUNG2_refinement_stability_candidate" not in lineage_text:
        fail("lineage missing Step 14 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_RUNG_3_AUDIT_ON_REFINEMENT_STABLE_CURRENCY_STEP15" not in grammar_text:
        fail("grammar manifest missing RUNG_3 row")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP14_SHADOW_COMMUTING_REFINEMENT",
        "C_STEP14_MIXING_CONTROL_FAILS",
        "C_STEP14_NONTRIVIAL_LIFT",
        "C_STEP14_NEXT_RUNG3_AUDIT",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    for path in ARTIFACT_DIR.glob("*"):
        if path.name == "run_step14.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for term, pattern in LITERATURE_PATTERNS:
            if pattern.search(text):
                fail(f"literature-program term in {path.name}: {term}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim/control pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_payload()
    check_tables()
    check_matrices_and_constraint()
    check_gate_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 14 validation passed.")


if __name__ == "__main__":
    main()
