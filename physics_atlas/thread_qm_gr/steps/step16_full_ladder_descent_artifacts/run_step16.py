#!/usr/bin/env python3
"""Validate Step 16 full-ladder descent artifacts."""

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
    "assemble_full_ladder_step16.py",
    "assembled_ladder_matrices_step16.json",
    "full_ladder_descent_step16.csv",
    "five_constraint_checklist_step16.csv",
    "full_ladder_output_step16.json",
    "full_ladder_output_step16.txt",
    "step16_results_summary.md",
    "step16_schema.json",
    "content_classification_step16.csv",
    "nonclaim_boundary_step16.md",
    "construction_gate_audit_step16.csv",
    "run_step16.py",
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
    "self-certified as a lawful physical layer",
    "root landing",
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
    re.compile(r"\bcontrol_passes\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bd_L_ge_d_union\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bcircular_test_used\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step16_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 16:
        fail("schema step must be 16")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "candidate_bridge_structure_external_review_required":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("candidate_bridge_structure") is not True:
        fail("schema candidate_bridge_structure must be true")
    if verdict.get("external_review_required") is not True:
        fail("schema must require external review")
    if verdict.get("external_review_flag") != "EXTERNAL_REVIEW_FRAME_TRANSFER_GATE":
        fail("schema external review flag mismatch")
    controls = schema["carrier"]["no_smuggling_controls"]
    for key in [
        "control_passes",
        "d_L_ge_d_union",
        "circular_test_used",
        "one_hot_set_cover_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
        "root_landed",
    ]:
        if controls.get(key) is not False:
            fail(f"no-smuggling flag must be false: {key}")
    if controls.get("prior_rungs_loaded") is not True:
        fail("schema must confirm prior rungs loaded")
    dims = schema["carrier"]["dimension"]
    if int(dims["d_L"]) >= int(dims["d_union"]):
        fail("d_L must be less than d_union")
    residuals = schema["track_fields"]["adequacy_residuals"]
    if float(residuals["candidate_L_adequacy_max"]) > 1e-10:
        fail("candidate L residual too large")
    for key in ["qm_alone_adequacy_min", "gr_alone_adequacy_min", "union_adequacy_min"]:
        if float(residuals[key]) <= 0.25:
            fail(f"control residual too small: {key}")
    if not all(schema["track_fields"]["five_constraints"].values()):
        fail("all five constraints must be true")


def check_payload() -> None:
    payload = json.loads((ARTIFACT_DIR / "full_ladder_output_step16.json").read_text(encoding="utf-8"))
    verdict = payload["verdict"]
    for key in [
        "candidate_bridge_structure",
        "candidate_L_passes",
        "qm_alone_fails",
        "gr_alone_fails",
        "union_fails_compression",
        "five_constraints_satisfied",
        "external_review_required",
    ]:
        if verdict.get(key) is not True:
            fail(f"payload verdict flag must be true: {key}")
    dims = payload["dimensions"]
    if int(dims["d_L"]) >= int(dims["d_union"]):
        fail("payload d_L must be less than d_union")
    checks = payload["no_smuggling_check"]
    for key in [
        "control_passes",
        "d_L_ge_d_union",
        "circular_test_used",
        "one_hot_set_cover_used",
        "target_layer_inserted",
        "endpoint_derivation_claimed",
        "literature_program_terms_used",
        "root_landed",
    ]:
        if checks.get(key) is not False:
            fail(f"payload no-smuggling flag must be false: {key}")
    if checks.get("prior_rungs_loaded") is not True:
        fail("payload must confirm prior rungs loaded")
    residuals = payload["observed_residuals"]
    if float(residuals["candidate_L_adequacy_max"]) > 1e-10:
        fail("payload candidate residual too large")
    for key in ["qm_alone_adequacy_min", "gr_alone_adequacy_min", "union_adequacy_min"]:
        if float(residuals[key]) <= 0.25:
            fail(f"payload control residual too small: {key}")
    if payload.get("external_review_flag") != "EXTERNAL_REVIEW_FRAME_TRANSFER_GATE":
        fail("payload external review flag mismatch")


def check_tables() -> None:
    rows = read_csv(ARTIFACT_DIR / "full_ladder_descent_step16.csv")
    by_case: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        by_case.setdefault(row["case"], []).append(row)
    for case in ["candidate_L", "qm_alone", "gr_alone", "union_direct_sum"]:
        if case not in by_case:
            fail(f"missing case {case}")
        if len(by_case[case]) != 2:
            fail(f"case {case} must have two levels")
    if any(row["status"] != "passes_candidate" for row in by_case["candidate_L"]):
        fail("candidate_L rows must pass")
    if any(row["status"] != "fails_as_control_endpoint_missing_mode" for row in by_case["qm_alone"] + by_case["gr_alone"]):
        fail("endpoint-alone rows must fail")
    if any(row["status"] != "fails_as_control_no_compression" for row in by_case["union_direct_sum"]):
        fail("union rows must fail compression")
    if any(row["compression_pass"] != "False" or row["single_layer_pass"] != "False" for row in by_case["union_direct_sum"]):
        fail("union must fail compression and single-layer checks")

    checklist = read_csv(ARTIFACT_DIR / "five_constraint_checklist_step16.csv")
    expected = {
        "C1_no_union",
        "C2_compression",
        "C3_currency_before_refinement",
        "C4_refinement_morphism",
        "C5_audit_route_consistency",
    }
    names = {row["constraint_id"] for row in checklist}
    missing = expected - names
    if missing:
        fail(f"missing checklist rows: {sorted(missing)}")
    if any(row["verified"] != "True" for row in checklist):
        fail("all five constraints must be verified")


def check_matrices() -> None:
    matrices = json.loads((ARTIFACT_DIR / "assembled_ladder_matrices_step16.json").read_text(encoding="utf-8"))
    if int(matrices["dimension"]) >= int(matrices["union_dimension"]):
        fail("assembled matrix dimension must be compressed")
    for level in ["level_1", "level_2"]:
        if level not in matrices["levels"]:
            fail(f"missing matrix level {level}")
        data = matrices["levels"][level]
        for key in ["S_QM", "S_GR", "E_QM", "E_GR", "A_u", "A_QM", "A_GR", "stable_lift_from_step14", "audit_lift_from_step15"]:
            if key not in data:
                fail(f"missing matrix {key} at {level}")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step16.csv")
    expected = {
        "C1_prior_rungs_loaded",
        "C2_candidate_L_recovers_audited_shadows",
        "C3_qm_alone_control_fails",
        "C4_gr_alone_control_fails",
        "C5_union_control_fails",
        "C6_compression_guard",
        "C7_five_constraints_verified",
        "C8_no_circular_test",
        "C9_external_review_flag_named",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_full_ladder_candidate_external_review" not in lineage_text:
        fail("lineage missing Step 16 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_EXTERNAL_REVIEW_FRAME_TRANSFER_STEP17" not in grammar_text:
        fail("grammar manifest missing external review row")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP16_FULL_LADDER_ASSEMBLED",
        "C_STEP16_QM_ALONE_FAILS",
        "C_STEP16_GR_ALONE_FAILS",
        "C_STEP16_UNION_FAILS_COMPRESSION",
        "C_STEP16_FIVE_CONSTRAINTS_SATISFIED",
        "C_STEP16_EXTERNAL_REVIEW_FLAG",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    for path in ARTIFACT_DIR.glob("*"):
        if path.name == "run_step16.py" or path.is_dir():
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
    print("Step 16 validation passed.")


if __name__ == "__main__":
    main()
