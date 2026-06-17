#!/usr/bin/env python3
"""Validate Step 10 framework-driven rung map artifacts."""

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
    "build_step10_framework_rungs.py",
    "closure_packages_step10.json",
    "gap_diagnostic_step10.json",
    "gap_diagnostic_step10.txt",
    "xi_diagnostic_step10.csv",
    "rung_map_step10.csv",
    "role_currency_gap_step10.csv",
    "framework_generation_audit_step10.csv",
    "step10_results_summary.md",
    "step10_schema.json",
    "content_classification_step10.csv",
    "nonclaim_boundary_step10.md",
    "run_step10.py",
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
    "target layer inserted",
    "direct QM-to-GR descent source",
]


LITERATURE_SPINE_TERMS = [
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
    re.compile(r"\bliterature_decomposition_imported\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\btarget_layer_inserted_as_source\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bqm_to_gr_descent_inserted_as_source\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step10_schema.json").read_text(encoding="utf-8"))
    for key in ["step", "orientation", "active_residual", "carrier", "candidate_move", "final_verdict", "track_fields"]:
        if key not in schema:
            fail(f"schema missing {key}")
    if schema["step"] != 10:
        fail("schema step must be 10")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "framework_generated_rung_map":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("rung_count") != 3:
        fail("schema rung count must be 3")
    if verdict.get("first_rung_to_build") != "RUNG_1_REFINE_FIXEDPOINT":
        fail("schema first rung mismatch")
    controls = schema["carrier"].get("no_smuggling_controls", {})
    for key in [
        "literature_decomposition_imported",
        "target_layer_inserted_as_source",
        "qm_to_gr_descent_inserted_as_source",
        "single_rung_closes_full_gap",
    ]:
        if controls.get(key) is not False:
            fail(f"no-smuggling flag must be false: {key}")
    if controls.get("rungs_generated_from_residual_blocks") is not True:
        fail("rungs_generated_from_residual_blocks must be true")
    xi = schema["track_fields"]["xi_results"]
    if abs(float(xi["direct_qm_to_gr_plus_framework_witness"]["raw_trace"]) - 10.0) > 1e-12:
        fail("direct raw Xi mismatch")
    if abs(float(xi["currency_mismatch"]["normalized_trace"]) - 1.0) > 1e-12:
        fail("currency mismatch Xi mismatch")


def check_package_and_gap_outputs() -> None:
    packages = json.loads((ARTIFACT_DIR / "closure_packages_step10.json").read_text(encoding="utf-8"))
    for key in ["qm_package", "gr_package", "roles", "atoms"]:
        if key not in packages:
            fail(f"closure package output missing {key}")
    if packages["qm_package"]["currency"] == packages["gr_package"]["currency"]:
        fail("QM and GR currencies should differ in this diagnostic")

    gap = json.loads((ARTIFACT_DIR / "gap_diagnostic_step10.json").read_text(encoding="utf-8"))
    direct = gap["direct_qm_to_gr_plus_framework_witness_gap"]
    if abs(float(direct["raw_trace"]) - 10.0) > 1e-12:
        fail("gap direct raw trace mismatch")
    if abs(float(direct["normalized_trace"]) - (10.0 / 12.0)) > 1e-12:
        fail("gap direct normalized trace mismatch")
    if gap["currency_mismatch"]["gr_currency_factors_through_qm"] is not False:
        fail("currency factorization should fail")
    if gap["first_rung_to_build"] != "RUNG_1_REFINE_FIXEDPOINT":
        fail("gap first rung mismatch")


def check_rung_map() -> None:
    rows = read_csv(ARTIFACT_DIR / "rung_map_step10.csv")
    if len(rows) != 3:
        fail("rung map must have three rows")
    expected_order = [
        "RUNG_1_REFINE_FIXEDPOINT",
        "RUNG_2_NEUTRAL_CURRENCY",
        "RUNG_3_AUDIT_COMMUTATOR",
    ]
    if [row["id"] for row in rows] != expected_order:
        fail("rung order mismatch")
    for row in rows:
        if abs(float(row["xi_contribution_raw"]) - 2.0) > 1e-12:
            fail(f"rung contribution mismatch for {row['id']}")
        if abs(float(row["own_rung_vs_endpoints_normalized_xi"]) - 1.0) > 1e-12:
            fail(f"rung endpoint nonfactorization mismatch for {row['id']}")
        if row["strict_extension"] != "True":
            fail(f"rung strict extension flag mismatch for {row['id']}")
        if row["clean_emergence"] != "yes":
            fail(f"rung clean emergence flag mismatch for {row['id']}")


def check_generation_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "framework_generation_audit_step10.csv")
    expected = {
        "F1_framework_only_spine",
        "F2_no_named_program_decomposition",
        "F3_no_target_layer_source",
        "F4_no_single_rung_full_gap",
        "F5_endpoint_nonclosure",
        "F6_clean_emergence_candidate",
        "F7_next_build_named",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing framework audit gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all framework audit gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_framework_rung_map_v1" not in lineage_text:
        fail("lineage missing framework rung map residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    for marker in [
        "G_E018_FrameworkRungMap_v1_STEP10",
        "G_E018_Build_RUNG_1_REFINE_FIXEDPOINT_STEP11",
    ]:
        if marker not in grammar_text:
            fail(f"grammar manifest missing {marker}")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP10_NO_IMPORTED_SPINE",
        "C_STEP10_DIRECT_GAP_STRUCTURED",
        "C_STEP10_FIRST_RUNG_REFINE_FIXEDPOINT",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    # Scan Step 10 artifacts fully.  Historical ledgers contain earlier
    # literature-import rows, so only Step 10 artifact content is scanned for
    # named-program decomposition terms.
    scan_paths = list(ARTIFACT_DIR.glob("*"))
    for path in scan_paths:
        if path.name == "run_step10.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for term in LITERATURE_SPINE_TERMS:
            if term.lower() in lower:
                fail(f"literature decomposition term in {path.name}: {term}")
        for regex in FORBIDDEN_REGEXES:
            if regex.search(text):
                fail(f"forbidden overclaim pattern in {path.name}: {regex.pattern}")


def main() -> None:
    check_required_files()
    check_schema()
    check_package_and_gap_outputs()
    check_rung_map()
    check_generation_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 10 validation passed.")


if __name__ == "__main__":
    main()
