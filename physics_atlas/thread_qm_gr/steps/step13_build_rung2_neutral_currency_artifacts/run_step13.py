#!/usr/bin/env python3
"""Validate Step 13 neutral-currency artifacts."""

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
    "build_neutral_currency_step13.py",
    "neutral_currency_matrices_step13.json",
    "neutral_currency_construction_step13.json",
    "currency_test_output_step13.json",
    "currency_test_output_step13.txt",
    "four_way_currency_test_step13.csv",
    "nonfactorization_step13.csv",
    "construction_gate_audit_step13.csv",
    "step13_results_summary.md",
    "step13_schema.json",
    "content_classification_step13.csv",
    "nonclaim_boundary_step13.md",
    "run_step13.py",
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
    re.compile(r"\bone_hot_set_cover_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bcircular_distance_from_u_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bliterature_program_terms_used\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\btarget_layer_inserted\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bendpoint_derivation_claimed\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bunion_control_passes\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bplaceholder_control_passes\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bcollapse_control_passes\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bd_u_ge_d_union\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bshadow_maps_equal\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step13_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 13:
        fail("schema step must be 13")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "neutral_currency_built_candidate_external_review_required":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("rung_built") is not True:
        fail("schema rung_built must be true")
    if verdict.get("external_review_required") is not True:
        fail("schema must require external review")
    if verdict.get("next_move") != "RETEST_RUNG_1_REFINE_FIXEDPOINT_ON_NEUTRAL_CURRENCY":
        fail("schema next move mismatch")
    controls = schema["carrier"]["no_smuggling_controls"]
    for key in [
        "one_hot_set_cover_used",
        "circular_distance_from_u_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
        "union_control_passes",
        "placeholder_control_passes",
        "collapse_control_passes",
        "d_u_ge_d_union",
        "shadow_maps_equal",
    ]:
        if controls.get(key) is not False:
            fail(f"no-smuggling flag must be false: {key}")
    if controls.get("step12_union_rejected") is not True:
        fail("schema must record Step-12 union rejection")
    compression = schema["track_fields"]["compression"]
    if int(compression["d_u"]) >= int(compression["d_union"]):
        fail("d_u must be strictly below d_union")
    if not compression.get("union_control_rejected"):
        fail("schema must reject union control")
    if schema["track_fields"]["distinctness"].get("shadow_maps_equal") is not False:
        fail("schema shadows must be distinct")


def check_payload() -> None:
    payload = json.loads((ARTIFACT_DIR / "currency_test_output_step13.json").read_text(encoding="utf-8"))
    verdict = payload["verdict"]
    for key in [
        "neutral_currency_built",
        "neutral_recovery_passes",
        "compression_passes",
        "distinct_shadows",
        "placeholder_fails",
        "union_fails_compression",
        "collapse_fails",
        "nonfactorizing",
    ]:
        if verdict.get(key) is not True:
            fail(f"payload verdict flag must be true: {key}")
    dims = payload["dimensions"]
    if int(dims["d_u"]) >= int(dims["d_union"]):
        fail("payload d_u must be less than d_union")
    if int(dims["d_u"]) < int(dims["d_qm"]):
        fail("payload d_u must be at least d_qm")
    residuals = payload["observed_residuals"]
    if float(residuals["neutral_recovery_max"]) > 1e-10:
        fail("neutral recovery residual too large")
    if float(residuals["placeholder_recovery_min"]) <= 0.25:
        fail("placeholder should fail recovery")
    if float(residuals["union_recovery_max"]) > 1e-10:
        fail("union should recover and be rejected only by compression")
    if float(residuals["collapse_recovery_min"]) <= 0.25:
        fail("collapse should fail recovery")
    if float(residuals["endpoint_nonfactorization_min"]) <= 0.25:
        fail("endpoint nonfactorization too small")
    checks = payload["no_smuggling_check"]
    for key in [
        "one_hot_set_cover_used",
        "circular_distance_from_u_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
        "union_control_passes",
        "placeholder_control_passes",
        "collapse_control_passes",
        "d_u_ge_d_union",
        "shadow_maps_equal",
    ]:
        if checks.get(key) is not False:
            fail(f"payload no-smuggling flag must be false: {key}")
    if checks.get("step12_union_rejected") is not True:
        fail("payload must record Step-12 union rejection")


def check_tables() -> None:
    rows = read_csv(ARTIFACT_DIR / "four_way_currency_test_step13.csv")
    by_case: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)
    for case in ["neutral_u", "placeholder", "union_direct_sum", "collapse_typed_seed"]:
        if case not in by_case:
            fail(f"missing test case {case}")
        if len(by_case[case]) != 2:
            fail(f"case {case} must have two refinement levels")
    if any(row["status"] != "passes_candidate" or row["overall_pass"] != "True" for row in by_case["neutral_u"]):
        fail("neutral_u rows must pass")
    if any(row["compression_pass"] != "False" or row["status"] != "fails_as_control_no_compression" for row in by_case["union_direct_sum"]):
        fail("union rows must fail compression")
    if any(row["overall_pass"] == "True" for row in by_case["placeholder"] + by_case["collapse_typed_seed"]):
        fail("placeholder and collapse controls must not pass")
    if any(row["distinctness_pass"] != "False" for row in by_case["collapse_typed_seed"]):
        fail("collapse shadows must be equal")

    emerg = read_csv(ARTIFACT_DIR / "nonfactorization_step13.csv")
    if len(emerg) != 2:
        fail("nonfactorization must have two refinement levels")
    if any(row["status"] != "strict_nonfactorizing" for row in emerg):
        fail("all nonfactorization rows must be strict_nonfactorizing")


def check_matrices() -> None:
    matrices = json.loads((ARTIFACT_DIR / "neutral_currency_matrices_step13.json").read_text(encoding="utf-8"))
    modes = matrices["currency_modes"]
    if len(modes["neutral"]) != 4 or len(modes["qm"]) != 3 or len(modes["gr"]) != 3:
        fail("currency dimensions mismatch")
    closures = matrices["enriched_currency_closures"]
    for name in ["f_qm_currency_on_u", "f_gr_currency_on_u", "f_neutral_currency"]:
        if name not in closures:
            fail(f"missing enriched closure {name}")
    for level in ["level_1", "level_2"]:
        if level not in matrices["levels"]:
            fail(f"missing matrix level {level}")
        shadows = matrices["levels"][level]["shadows"]
        if shadows["neutral_to_qm"] == shadows["neutral_to_gr"]:
            fail("neutral shadow maps must differ")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step13.csv")
    expected = {
        "C1_step12_union_rejected",
        "C2_enriched_endpoint_currencies",
        "C3_single_neutral_currency_declared",
        "C4_recovery_low_two_levels",
        "C5_compression_guard",
        "C6_union_control_rejected",
        "C7_placeholder_control_rejected",
        "C8_collapse_control_rejected",
        "C9_nonfactorizing_extension",
        "C10_next_move_named",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_RUNG2_NEUTRAL_CURRENCY_candidate" not in lineage_text:
        fail("lineage missing Step 13 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    for marker in [
        "G_E018_Build_RUNG_2_NEUTRAL_CURRENCY_REORDERED_STEP13",
        "G_E018_Retest_RUNG_1_ON_NEUTRAL_CURRENCY_STEP14",
    ]:
        if marker not in grammar_text:
            fail(f"grammar manifest missing {marker}")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP13_STEP12_UNION_REJECTED",
        "C_STEP13_ENRICHED_CURRENCIES",
        "C_STEP13_UNION_CONTROL_FAILS_COMPRESSION",
        "C_STEP13_NEUTRAL_CURRENCY_BUILT",
        "C_STEP13_NEXT_RUNG1_ON_U",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    for path in ARTIFACT_DIR.glob("*"):
        if path.name == "run_step13.py" or path.is_dir():
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
    check_matrices()
    check_gate_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 13 validation passed.")


if __name__ == "__main__":
    main()
