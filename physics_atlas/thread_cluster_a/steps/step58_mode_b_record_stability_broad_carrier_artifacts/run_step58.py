#!/usr/bin/env python3
"""Validate Cluster A Step 58 broad-carrier record-stability stress artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "record_stability_broad_carrier_step58.py"
STEP57_BUILD = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "record_stability_descent_step57.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "run_step35.py",
    STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "run_step57.py",
]

REQUIRED_FILES = [
    "record_stability_broad_carrier_step58.py",
    "record_stability_broad_carrier_scores_step58.csv",
    "record_stability_by_structure_step58.csv",
    "frozen_requirement_step58.csv",
    "negative_controls_step58.csv",
    "dependency_trace_step58.csv",
    "ablation_step58.csv",
    "stage2_record_fact_step58.csv",
    "anti_smuggle_self_check_step58.csv",
    "six_gate_audit_step58.csv",
    "generated_vs_input_step58.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "step58_schema.json",
    "content_classification_step58.csv",
    "nonclaim_boundary_step58.md",
    "step58_results_summary.md",
    "step58_statement.tex",
    "run_step58.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives\s+clean\s+separation\b",
    r"\bproves\s+clean\s+separation\b",
    r"\bgrounds\s+clean\s+separation\s+unconditionally\b",
    r"\bSBT\s+derives\s+the\s+SM\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bpsi-as-cosourcing\b",
    r"\bcommon-refinement-as-QMGR-cosourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step58.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def step57_requirement_hash() -> str:
    text = STEP57_BUILD.read_text(encoding="utf-8")
    start = text.index("# RECORD_REQUIREMENT_BEGIN")
    end = text.index("# RECORD_REQUIREMENT_END")
    return hashlib.sha256(text[start:end].encode("utf-8")).hexdigest()


def validate_frozen_requirement_gate() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "spec_from_file_location" not in text or "record_layer_membership" not in text:
        fail("Step58 must import and call Step57 record_layer_membership")
    if "def record_layer_membership" in text:
        fail("Step58 must not reimplement record_layer_membership")
    forbidden_reimplementation_terms = [
        "record_tokens.add",
        "combinations_with_replacement",
        "alias_pairs =",
    ]
    for token in forbidden_reimplementation_terms:
        if token in text:
            fail(f"Step58 appears to reimplement or retune the record requirement: {token}")
    if re.search(r"(?m)^\s*MIN_RECORD_TOKENS\s*=", text):
        fail("Step58 must not assign MIN_RECORD_TOKENS")
    frozen_rows = read_csv("frozen_requirement_step58.csv")
    if len(frozen_rows) != 1:
        fail("expected exactly one frozen requirement row")
    row = frozen_rows[0]
    if row["status"] != "imported_verbatim":
        fail("frozen requirement must be recorded as imported_verbatim")
    if row["sha256"] != step57_requirement_hash():
        fail("frozen Step57 requirement hash mismatch")
    if row["MIN_RECORD_TOKENS"] != "2":
        fail("frozen threshold changed")
    anti = {row["check"]: row for row in read_csv("anti_smuggle_self_check_step58.csv")}
    for check in (
        "frozen_requirement_imported",
        "no_record_requirement_reimplementation",
        "neutral_carrier_not_prefiltered",
        "teeth_divergence_search_nonvacuous",
        "no_requirement_retuning",
    ):
        if anti.get(check, {}).get("passes") != "True":
            fail(f"anti-smuggle check failed: {check}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step58.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step58_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 58:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_broad_carrier_record_stability_stress":
        fail("unexpected orientation")
    if schema.get("carrier_rows") != 80:
        fail(f"expected 80 broad carrier rows, got {schema.get('carrier_rows')}")
    if schema.get("carrier_rows") <= 12:
        fail("carrier must be broader than Step57")
    if schema.get("CS_count") != 8:
        fail(f"expected CS_count=8, got {schema.get('CS_count')}")
    if schema.get("non_CS_count") != 72:
        fail(f"expected non_CS_count=72, got {schema.get('non_CS_count')}")
    if schema.get("RS_count") != 4:
        fail(f"expected RS_count=4, got {schema.get('RS_count')}")
    if schema.get("RS_not_CS_count") != 0:
        fail("expected no record-stable non-CS witness on this carrier")
    if schema.get("divergence_witness_exists") is not False:
        fail("divergence witness flag should be false")
    if schema.get("RS_subset_CS") is not True:
        fail("RS should be subset of CS on the broad carrier")
    if schema.get("verdict") != "ROBUST_DESCENT_FROZEN_RS_SUBSET_CS_ON_BROAD_CARRIER":
        fail("unexpected verdict")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True:
        fail("schema gate flags did not pass")
    if schema.get("frozen_requirement_gate_pass") is not True or schema.get("neutral_carrier_gate_pass") is not True:
        fail("schema frozen/neutral carrier gates did not pass")


def validate_scores() -> None:
    rows = read_csv("record_stability_broad_carrier_scores_step58.csv")
    if len(rows) != 80:
        fail(f"expected 80 score rows, got {len(rows)}")
    cs = [row for row in rows if row["cs_member"] == "True"]
    rs = [row for row in rows if row["rs_member"] == "True"]
    div = [row for row in rows if row["divergence_witness"] == "True"]
    if len(cs) != 8 or len(rs) != 4 or div:
        fail(f"unexpected CS/RS/divergence counts: {len(cs)} {len(rs)} {len(div)}")
    if any(row["dimensions"] != "2|3" for row in cs):
        fail("CS rows should be the eight 2|3 rows in this carrier")
    if any(row["cs_member"] != "True" for row in rs):
        fail("all RS rows should lie in CS")
    non_cs = [row for row in rows if row["cs_member"] != "True"]
    if len(non_cs) <= 0:
        fail("carrier must include non-CS rows")
    structure_rows = {row["dimensions"]: row for row in read_csv("record_stability_by_structure_step58.csv")}
    expected = {
        "2|3": ("15", "8", "4", "0"),
        "3": ("49", "0", "0", "0"),
        "4": ("16", "0", "0", "0"),
    }
    for dim, counts in expected.items():
        row = structure_rows.get(dim)
        if row is None:
            fail(f"missing structure row: {dim}")
        observed = (row["carrier_rows"], row["CS_count"], row["RS_count"], row["RS_not_CS_count"])
        if observed != counts:
            fail(f"unexpected structure counts for {dim}: {observed}")


def validate_controls_and_gates() -> None:
    for row in read_csv("negative_controls_step58.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("stage2_record_fact_step58.csv"):
        if row["passes"] != "True":
            fail(f"stage2 row failed: {row}")
    for row in read_csv("six_gate_audit_step58.csv"):
        if row["passes"] != "True":
            fail(f"six-gate row failed: {row}")
    ablation = read_csv("ablation_step58.csv")
    if not ablation or any(row["load_bearing"] != "True" for row in ablation):
        fail("all Step58 ablations should be marked load-bearing")
    deps = {row["axiom"] for row in read_csv("dependency_trace_step58.csv")}
    for required in ("frozen_step57_record_requirement", "broad_step35_carrier", "divergence_search"):
        if required not in deps:
            fail(f"dependency trace missing {required}")


def validate_generated_vs_input() -> None:
    rows = read_csv("generated_vs_input_step58.csv")
    statuses = {row["item"]: row["status"] for row in rows}
    expected = {
        "Step57_record_requirement": "imported_frozen",
        "Step35_broad_carrier": "read",
        "CS_extension": "computed",
        "RS_extension": "computed_with_imported_requirement",
        "divergence_witness_search": "computed",
        "verdict": "computed",
    }
    for item, status in expected.items():
        if statuses.get(item) != status:
            fail(f"generated-vs-input mismatch for {item}: {statuses.get(item)}")


def validate_ledgers() -> None:
    lineage = read_csv("mode_b_target_lineage.csv")
    if len(lineage) != 1:
        fail("expected one lineage row")
    relation = lineage[0]["relation_to_canonical_root"]
    if "super_residual" not in relation or "USER-AUTHORIZED 2026-06-09" not in relation:
        fail("lineage must record user-authorized parent-layer move")
    grammar = read_csv("mode_b_grammar_manifest.csv")
    if len(grammar) != 1 or grammar[0]["new_grammar_declared"] != "True":
        fail("Step58 should declare the broad-carrier stress grammar")
    if "80-row" not in grammar[0]["carrier"] or "divergence" not in grammar[0]["tracked_object"]:
        fail("grammar manifest should track broad-carrier divergence search")


def validate_classification() -> None:
    rows = read_csv("content_classification_step58.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"required artifacts missing from classification: {missing}")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"unknown classification grade: {row}")
    statement = f"steps/{ARTIFACT_DIR.name}/step58_statement.tex"
    for row in rows:
        if row["artifact"] == statement and row["grade"] != "finite-carrier-diagnostic":
            fail("Step58 statement must be finite-carrier-diagnostic")


def run_build() -> None:
    result = subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), text=True, capture_output=True)
    if result.returncode != 0:
        fail(f"build failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def run_chain_dependencies() -> None:
    for runner in DEPENDENCY_RUNNERS:
        if runner.exists():
            result = subprocess.run([sys.executable, str(runner), "--self"], cwd=str(runner.parent), text=True, capture_output=True)
            if result.returncode != 0:
                fail(f"dependency validator failed for {runner}:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def validate_all() -> None:
    validate_required_files()
    validate_frozen_requirement_gate()
    validate_schema()
    validate_scores()
    validate_controls_and_gates()
    validate_generated_vs_input()
    validate_ledgers()
    validate_classification()
    scan_overclaims()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="validate Step58 only")
    parser.add_argument("--chain", action="store_true", help="rebuild and validate dependencies")
    args = parser.parse_args()
    if args.chain:
        run_chain_dependencies()
        run_build()
    elif not args.self:
        args.self = True
    if args.self:
        validate_all()
    print("run_step58.py: PASS")


if __name__ == "__main__":
    main()
