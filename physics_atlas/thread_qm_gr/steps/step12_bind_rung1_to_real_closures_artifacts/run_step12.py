#!/usr/bin/env python3
"""Validate Step 12 bound RUNG_1 artifacts."""

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
    "bind_rung1_real_closures_step12.py",
    "bound_structured_matrices_step12.json",
    "bound_rung1_construction_step12.json",
    "adequacy_output_step12.json",
    "adequacy_output_step12.txt",
    "three_way_adequacy_step12.csv",
    "nonfactorization_step12.csv",
    "construction_gate_audit_step12.csv",
    "step12_results_summary.md",
    "step12_schema.json",
    "content_classification_step12.csv",
    "nonclaim_boundary_step12.md",
    "run_step12.py",
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

LITERATURE_PATTERNS = [
    re.compile(r"\bholography\b", re.I),
    re.compile(r"\bAdS\b"),
    re.compile(r"\bCFT\b"),
    re.compile(r"\bRT/HRT\b"),
    re.compile(r"\bLQG\b"),
    re.compile(r"\basymptotic safety\b", re.I),
    re.compile(r"\bspin network\b", re.I),
]


FORBIDDEN_REGEXES = [
    re.compile(r"\bderive[sd]?\s+(?:a\s+|the\s+)?(?:new\s+)?(?:[A-Za-z-]+\s+){0,3}(?:constant|mass)\b", re.I),
    re.compile(r"\broot_landed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bone_hot_set_cover_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bliterature_program_terms_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\btarget_layer_inserted\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bendpoint_derivation_claimed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bplaceholder_passes\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bgeneric_averaging_passes\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step12_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 12:
        fail("schema step must be 12")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "bound_rung1_built_candidate_external_review_required":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("rung_built") is not True:
        fail("schema rung_built must be true")
    if verdict.get("flag_2_discharged") is not True:
        fail("schema flag_2_discharged must be true")
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
        "generic_averaging_passes",
    ]:
        if controls.get(key) is not False:
            fail(f"no-smuggling flag must be false: {key}")
    if controls.get("step10_closures_loaded") is not True:
        fail("step10_closures_loaded must be true")
    adequacy = schema["track_fields"]["adequacy_results"]
    if float(adequacy["bound_transition_1_to_2"]) != 0.0:
        fail("bound transition 1->2 should be zero")
    if float(adequacy["bound_transition_2_to_3"]) != 0.0:
        fail("bound transition 2->3 should be zero")
    if float(adequacy["placeholder_transition_1_to_2"]) < 0.25:
        fail("placeholder transition 1->2 should fail")
    if float(adequacy["generic_transition_1_to_2"]) < 0.25:
        fail("generic transition 1->2 should fail")
    if float(adequacy["endpoint_nonfactorization_min"]) < 0.25:
        fail("endpoint nonfactorization too small")


def check_matrix_and_construction() -> None:
    construction = json.loads((ARTIFACT_DIR / "bound_rung1_construction_step12.json").read_text(encoding="utf-8"))
    if "step10_qm_closed_seed" not in construction or "step10_gr_closed_seed" not in construction:
        fail("construction must record loaded Step-10 closures")
    matrices = json.loads((ARTIFACT_DIR / "bound_structured_matrices_step12.json").read_text(encoding="utf-8"))
    for name in ["qm", "gr", "bound", "generic"]:
        if name not in matrices.get("atom_matrices", {}):
            fail(f"missing atom matrix {name}")
    for level in ["level_1", "level_2", "level_3"]:
        if level not in matrices.get("level_matrices", {}):
            fail(f"missing level matrix {level}")
    for lift in ["1_to_2", "2_to_3"]:
        if lift not in matrices.get("lifts", {}):
            fail(f"missing lift {lift}")


def check_adequacy_outputs() -> None:
    payload = json.loads((ARTIFACT_DIR / "adequacy_output_step12.json").read_text(encoding="utf-8"))
    verdict = payload["verdict"]
    if verdict.get("bound_rung1_built") is not True:
        fail("bound_rung1_built must be true")
    for key in ["bound_passes", "placeholder_fails", "generic_averaging_fails", "nonfactorizing"]:
        if verdict.get(key) is not True:
            fail(f"verdict flag must be true: {key}")
    checks = payload["no_smuggling_check"]
    for key in [
        "one_hot_set_cover_used",
        "literature_program_terms_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "placeholder_passes",
        "generic_averaging_passes",
    ]:
        if checks.get(key) is not False:
            fail(f"payload no-smuggling flag must be false: {key}")
    if checks.get("step10_closures_loaded") is not True:
        fail("payload must confirm Step-10 closures loaded")
    ranges = payload["observed_residual_range"]
    if float(ranges["bound"]["max"]) > 1e-10:
        fail("bound residual too large")
    if float(ranges["placeholder"]["min"]) < 0.25:
        fail("placeholder residual too small")
    if float(ranges["generic_averaging"]["min"]) < 0.25:
        fail("generic averaging residual too small")

    rows = read_csv(ARTIFACT_DIR / "three_way_adequacy_step12.csv")
    by_case = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)
    for case in ["bound", "placeholder", "generic_averaging"]:
        if case not in by_case:
            fail(f"missing adequacy case {case}")
    if any(row["status"] != "passes" for row in by_case["bound"]):
        fail("bound rows must pass")
    for case in ["placeholder", "generic_averaging"]:
        if any(row["status"] != "fails_as_control" for row in by_case[case]):
            fail(f"{case} rows must fail as controls")

    emerg = read_csv(ARTIFACT_DIR / "nonfactorization_step12.csv")
    if any(row["status"] != "strict_nonfactorizing" for row in emerg):
        fail("all nonfactorization rows must be strict_nonfactorizing")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step12.csv")
    expected = {
        "C1_step10_closures_loaded",
        "C2_real_idempotent_operators",
        "C3_bound_commutes_with_lift",
        "C4_placeholder_fails",
        "C5_generic_averaging_fails",
        "C6_two_sided_descent",
        "C7_nonfactorizing_extension",
        "C8_next_build_named",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_bound_RUNG_1_REFINE_FIXEDPOINT_candidate" not in lineage_text:
        fail("lineage missing Step 12 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_Build_RUNG_2_NEUTRAL_CURRENCY_AFTER_BOUND_RUNG1_STEP13" not in grammar_text:
        fail("grammar manifest missing bound RUNG_2 build row")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP12_REAL_CLOSURES_BOUND",
        "C_STEP12_PLACEHOLDER_FAILS",
        "C_STEP12_GENERIC_AVERAGING_FAILS",
        "C_STEP12_NONFACTORIZING_BOUND_RUNG",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    scan_paths = list(ARTIFACT_DIR.glob("*"))
    for path in scan_paths:
        if path.name == "run_step12.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for term, pattern in zip(LITERATURE_TERMS, LITERATURE_PATTERNS):
            if pattern.search(text):
                fail(f"literature-program term in {path.name}: {term}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_matrix_and_construction()
    check_adequacy_outputs()
    check_gate_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 12 validation passed.")


if __name__ == "__main__":
    main()
