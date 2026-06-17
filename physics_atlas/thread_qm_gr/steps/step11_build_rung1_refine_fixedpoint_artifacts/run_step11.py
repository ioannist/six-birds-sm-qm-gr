#!/usr/bin/env python3
"""Validate Step 11 RUNG_1_REFINE_FIXEDPOINT build artifacts."""

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
    "rung1_refinement_lift_step11.py",
    "structured_matrices_step11.json",
    "rung1_construction_step11.json",
    "adequacy_output_step11.json",
    "adequacy_output_step11.txt",
    "adequacy_diagnostic_step11.csv",
    "emergence_check_step11.csv",
    "construction_gate_audit_step11.csv",
    "step11_results_summary.md",
    "step11_schema.json",
    "content_classification_step11.csv",
    "nonclaim_boundary_step11.md",
    "run_step11.py",
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


LITERATURE_TERMS = [
    "holography",
    "AdS",
    "CFT",
    "RT/HRT",
    "LQG",
    "asymptotic safety",
    "spin network",
]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\broot_landed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bone_hot_set_cover_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bliterature_program_terms_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\btarget_layer_inserted\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bendpoint_derivation_claimed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bplaceholder_passes\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step11_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 11:
        fail("schema step must be 11")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "rung1_built_candidate_external_review_required":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("rung_built") is not True:
        fail("schema rung_built must be true")
    if verdict.get("external_review_required") is not True:
        fail("schema must require external review")
    if verdict.get("next_build") != "RUNG_2_NEUTRAL_CURRENCY":
        fail("schema next build mismatch")
    controls = schema["carrier"]["no_smuggling_controls"]
    for key in [
        "one_hot_set_cover_used",
        "literature_program_terms_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "placeholder_passes",
    ]:
        if controls.get(key) is not False:
            fail(f"no-smuggling flag must be false: {key}")
    adequacy = schema["track_fields"]["adequacy_results"]
    if float(adequacy["built_transition_1_to_2"]) != 0.0:
        fail("built transition 1->2 should be zero")
    if float(adequacy["built_transition_2_to_3"]) != 0.0:
        fail("built transition 2->3 should be zero")
    if float(adequacy["placeholder_transition_1_to_2"]) < 0.25:
        fail("placeholder transition 1->2 should fail")
    if float(adequacy["placeholder_transition_2_to_3"]) < 0.25:
        fail("placeholder transition 2->3 should fail")
    if float(adequacy["endpoint_nonfactorization_min"]) < 0.25:
        fail("endpoint nonfactorization too small")


def check_matrix_artifact() -> None:
    matrices = json.loads((ARTIFACT_DIR / "structured_matrices_step11.json").read_text(encoding="utf-8"))
    for level in ["level_1", "level_2", "level_3"]:
        if level not in matrices.get("levels", {}):
            fail(f"missing matrix level {level}")
        for name in ["rung_closure", "placeholder_closure", "qm_endpoint_closure", "gr_endpoint_closure"]:
            if name not in matrices["levels"][level]:
                fail(f"missing {name} for {level}")
    for lift in ["1_to_2", "2_to_3"]:
        if lift not in matrices.get("lifts", {}):
            fail(f"missing lift {lift}")


def check_adequacy_outputs() -> None:
    payload = json.loads((ARTIFACT_DIR / "adequacy_output_step11.json").read_text(encoding="utf-8"))
    verdict = payload["verdict"]
    if verdict.get("candidate_built") is not True:
        fail("candidate_built must be true")
    if verdict.get("placeholder_fails") is not True:
        fail("placeholder_fails must be true")
    if payload["next_build"] != "RUNG_2_NEUTRAL_CURRENCY":
        fail("payload next build mismatch")
    ranges = payload["observed_residual_range"]
    if float(ranges["built_max"]) > 1e-10:
        fail("built residual too large")
    if float(ranges["placeholder_min"]) < 0.25:
        fail("placeholder residual too small")
    checks = payload["no_smuggling_check"]
    for key in [
        "one_hot_set_cover_used",
        "literature_program_terms_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "placeholder_passes",
    ]:
        if checks.get(key) is not False:
            fail(f"payload no-smuggling flag must be false: {key}")

    rows = read_csv(ARTIFACT_DIR / "adequacy_diagnostic_step11.csv")
    statuses = {row["status"] for row in rows}
    if "passes" not in statuses or "fails_as_control" not in statuses:
        fail("adequacy table must include built pass and placeholder failure")
    for row in rows:
        if row["case"] == "placeholder" and row["status"] != "fails_as_control":
            fail("placeholder rows must fail as control")
    emerg = read_csv(ARTIFACT_DIR / "emergence_check_step11.csv")
    if any(row["status"] != "strict_nonfactorizing" for row in emerg):
        fail("all emergence rows must be strict_nonfactorizing")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step11.csv")
    expected = {
        "B1_structured_maps_not_one_hot",
        "B2_idempotent_closures",
        "B3_lift_commutes_with_closure",
        "B4_placeholder_fails",
        "B5_two_sided_descent",
        "B6_nonfactorizing_extension",
        "B7_no_endpoint_or_target_insertion",
        "B8_next_build_named",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_RUNG_1_REFINE_FIXEDPOINT_candidate" not in lineage_text:
        fail("lineage missing Step 11 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_Build_RUNG_2_NEUTRAL_CURRENCY_STEP12" not in grammar_text:
        fail("grammar manifest missing RUNG_2 build row")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP11_STRUCTURED_MAPS_REQUIRED",
        "C_STEP11_PLACEHOLDER_FAILS",
        "C_STEP11_NONFACTORIZING_EXTENSION",
        "C_STEP11_NEXT_BUILD_RUNG2",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*"))
    for path in scan_paths:
        if path.name == "run_step11.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for term in LITERATURE_TERMS:
            if term.lower() in lower:
                fail(f"literature-program term in {path.name}: {term}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_matrix_artifact()
    check_adequacy_outputs()
    check_gate_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 11 validation passed.")


if __name__ == "__main__":
    main()
