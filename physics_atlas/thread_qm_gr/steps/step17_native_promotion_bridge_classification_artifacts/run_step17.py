#!/usr/bin/env python3
"""Validate Step 17 native promotion-bridge classification artifacts."""

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
    "native_promotion_bridge_step17.py",
    "object_maps_step17.json",
    "promotion_bridge_tuples_step17.json",
    "eight_gate_classification_step17.csv",
    "defect_records_step17.json",
    "delta_fact_step17.csv",
    "native_status_step17.csv",
    "native_classification_output_step17.json",
    "native_classification_output_step17.txt",
    "distinguishing_gate_step17.md",
    "step17_results_summary.md",
    "step17_schema.json",
    "content_classification_step17.csv",
    "nonclaim_boundary_step17.md",
    "construction_gate_audit_step17.csv",
    "run_step17.py",
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
    "candidate bridge structure",
    "bridge layer",
    "intermediate layer",
    "bridge-as-layer",
]


NATIVE_FORBIDDEN_PATTERNS = [
    ("shadow", re.compile(r"\bshadow\b", re.I)),
    ("compression", re.compile(r"\bcompression\b", re.I)),
    ("bridge_as_layer", re.compile(r"\bbridge_as_layer\b", re.I)),
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
    re.compile(r"\bpackage_promotion_bridge_confused\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bunion_non_strict_asserted\b.{0,20}\btrue\b", re.I | re.S),
    re.compile(r"\bliterature_program_terms_used\b.{0,20}\btrue\b", re.I | re.S),
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
    schema = json.loads((ARTIFACT_DIR / "step17_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 17:
        fail("schema step must be 17")
    verdict = schema["final_verdict"]
    if verdict.get("type") != "native_classification_complete":
        fail("schema verdict type mismatch")
    if verdict.get("root_landed") is not False:
        fail("schema root_landed must be false")
    if verdict.get("L_status") != "candidate":
        fail("L status must be candidate")
    if verdict.get("union_status") != "failed_G_nosmuggle":
        fail("union status must be failed_G_nosmuggle")
    if verdict.get("distinguishing_gate") != "G_nosmuggle":
        fail("distinguishing gate must be G_nosmuggle")
    if verdict.get("external_review_required") is not True:
        fail("external review must be required")
    controls = schema["carrier"]["no_smuggling_controls"]
    for key in ["package_promotion_bridge_confused", "union_non_strict_asserted", "literature_program_terms_used", "root_landed"]:
        if controls.get(key) is not False:
            fail(f"schema control flag must be false: {key}")
    strict = schema["track_fields"]["strictness"]
    if strict.get("L_strict") is not True or strict.get("union_strict") is not True:
        fail("both targets must be strict")
    if int(strict["L_Delta_fact_count"]) <= 0 or int(strict["union_Delta_fact_count"]) <= 0:
        fail("Delta_fact must be nonempty for both")
    if strict.get("strictness_distinguishes") is not False:
        fail("strictness must not distinguish the targets")
    defect = schema["track_fields"]["G_nosmuggle_defect"]
    if int(defect["L_extra_coordinate_count"]) != 0:
        fail("L G_nosmuggle defect must be zero")
    if int(defect["union_extra_coordinate_count"]) != 2:
        fail("union G_nosmuggle defect must be 2")


def check_payload() -> None:
    payload = json.loads((ARTIFACT_DIR / "native_classification_output_step17.json").read_text(encoding="utf-8"))
    if payload.get("native_vocabulary") is not True:
        fail("payload must mark native vocabulary true")
    classes = payload["classifications"]
    if classes["L"]["status"] != "candidate":
        fail("payload L status mismatch")
    if classes["union"]["status"] != "failed_G_nosmuggle":
        fail("payload union status mismatch")
    if classes["L"]["strict"] is not True or classes["union"]["strict"] is not True:
        fail("payload must mark both strict")
    if classes["union"]["failed_gates"] != ["G_nosmuggle"]:
        fail("payload union failed gates mismatch")
    gate = payload["distinguishing_gate"]
    if gate.get("gate") != "G_nosmuggle":
        fail("payload distinguishing gate mismatch")
    if int(gate["union_extra_coordinate_count"]) != 2:
        fail("payload union extra coordinate count mismatch")
    checks = payload["no_smuggling_check"]
    for key in ["package_promotion_bridge_confused", "union_non_strict_asserted", "literature_program_terms_used", "root_landed"]:
        if checks.get(key) is not False:
            fail(f"payload control flag must be false: {key}")


def check_tables() -> None:
    status_rows = read_csv(ARTIFACT_DIR / "native_status_step17.csv")
    status = {row["target_package"]: row for row in status_rows}
    if status["L"]["native_status"] != "candidate":
        fail("status table L mismatch")
    if status["union"]["native_status"] != "failed_G_nosmuggle":
        fail("status table union mismatch")
    if status["L"]["strict"] != "True" or status["union"]["strict"] != "True":
        fail("status table must mark both strict")
    if int(status["L"]["Delta_fact_count"]) <= 0 or int(status["union"]["Delta_fact_count"]) <= 0:
        fail("status table Delta_fact counts must be positive")
    if status["union"]["native_status"] == "non_strict":
        fail("union must not be marked non_strict")

    gate_rows = read_csv(ARTIFACT_DIR / "eight_gate_classification_step17.csv")
    by_target_gate = {(row["target_package"], row["gate"]): row for row in gate_rows}
    gates = ["G_suff", "G_desc", "G_stab", "G_ctrl", "G_nosmuggle", "G_vis", "G_audit", "G_strict"]
    for gate in gates:
        if by_target_gate[("L", gate)]["status"] != "pass":
            fail(f"L must pass {gate}")
    for gate in gates:
        expected = "fail" if gate == "G_nosmuggle" else "pass"
        if by_target_gate[("union", gate)]["status"] != expected:
            fail(f"union {gate} status mismatch")

    delta_rows = read_csv(ARTIFACT_DIR / "delta_fact_step17.csv")
    counts = {"L": 0, "union": 0}
    for row in delta_rows:
        counts[row["target_package"]] += 1
        if float(row["qm_gap"]) > 1e-10:
            fail("Delta_fact witness must have zero QM gap")
        if float(row["target_gap"]) <= 1e-10:
            fail("Delta_fact witness target gap must be positive")
    if counts["L"] != 3 or counts["union"] != 3:
        fail("Delta_fact witness counts must be 3 for both")


def check_json_artifacts() -> None:
    maps = json.loads((ARTIFACT_DIR / "object_maps_step17.json").read_text(encoding="utf-8"))
    if len(maps["source_carrier_S"]) != 8:
        fail("source carrier must have 8 states")
    for key in ["pi_QM", "pi_GR", "pi_L", "pi_union"]:
        if key not in maps["object_maps"]:
            fail(f"missing object map {key}")
    tuples = json.loads((ARTIFACT_DIR / "promotion_bridge_tuples_step17.json").read_text(encoding="utf-8"))
    if tuples["L"]["status"] != "candidate":
        fail("tuple L status mismatch")
    if tuples["union"]["status"] != "failed_G_nosmuggle":
        fail("tuple union status mismatch")
    defects = json.loads((ARTIFACT_DIR / "defect_records_step17.json").read_text(encoding="utf-8"))
    if defects["L"]["G_nosmuggle"]["defect"]["extra_coordinate_count"] != 0:
        fail("L defect record mismatch")
    if defects["union"]["G_nosmuggle"]["defect"]["extra_coordinate_count"] != 2:
        fail("union defect record mismatch")


def check_gate_audit() -> None:
    rows = read_csv(ARTIFACT_DIR / "construction_gate_audit_step17.csv")
    expected = {
        "C1_native_vocabulary",
        "C2_object_maps_built",
        "C3_L_strict_computed",
        "C4_union_strict_computed",
        "C5_L_eight_gates_pass",
        "C6_union_g_nosmuggle_fails",
        "C7_distinguishing_gate_identified",
        "C8_status_assigned",
        "C9_no_root_landing",
    }
    names = {row.get("gate", "") for row in rows}
    missing = expected - names
    if missing:
        fail(f"missing construction gates: {sorted(missing)}")
    if any(row.get("status") != "pass" for row in rows):
        fail("all construction gates must pass")


def check_ledgers() -> None:
    lineage_text = LINEAGE.read_text(encoding="utf-8")
    if "R_child_E018_after_native_promotion_bridge_classification" not in lineage_text:
        fail("lineage missing Step 17 residual")
    grammar_text = GRAMMAR.read_text(encoding="utf-8")
    if "G_E018_NATIVE_EXTERNAL_REVIEW_STEP18" not in grammar_text:
        fail("grammar manifest missing native review row")
    constraint_text = CONSTRAINTS.read_text(encoding="utf-8")
    for marker in [
        "C_STEP17_NATIVE_VOCABULARY_LOCK",
        "C_STEP17_STRICTNESS_NOT_DISTINGUISHING",
        "C_STEP17_G_NOSMUGGLE_DISTINGUISHES",
        "C_STEP17_L_STATUS_CANDIDATE",
        "C_STEP17_UNION_STATUS_FAILED_NOSMUGGLE",
        "C_STEP17_NATIVE_EXTERNAL_REVIEW",
    ]:
        if marker not in constraint_text:
            fail(f"constraint ledger missing {marker}")


def check_forbidden_text() -> None:
    for path in ARTIFACT_DIR.glob("*"):
        if path.name == "run_step17.py" or path.is_dir():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        lower = text.lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase.lower() in lower:
                fail(f"forbidden phrase in {path.name}: {phrase}")
        for label, pattern in NATIVE_FORBIDDEN_PATTERNS:
            if pattern.search(text):
                fail(f"non-native vocabulary in {path.name}: {label}")
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
    check_json_artifacts()
    check_gate_audit()
    check_ledgers()
    check_forbidden_text()
    print("Step 17 validation passed.")


if __name__ == "__main__":
    main()
