#!/usr/bin/env python3
"""Validator for Step 69 SM record-stability prediction packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP59_DIR = THREAD_DIR / "steps/step59_mode_b_record_stability_coverage_artifacts"
STEP41_DIR = THREAD_DIR / "steps/step41_mode_b_factorization_defect_clean_separation_artifacts"
STEP45_DIR = THREAD_DIR / "steps/step45_mode_b_proton_decay_F27_artifacts"
STEP46_DIR = THREAD_DIR / "steps/step46_mode_b_monopole_F48_artifacts"
STEP65_DIR = THREAD_DIR / "steps/step65_mode_b_proton_monopole_fork_resolution_artifacts"

STEP59_BUILD = STEP59_DIR / "record_stability_coverage_step59.py"
STEP59_SCORES = STEP59_DIR / "record_stability_coverage_scores_step59.csv"
STEP41_BUILD = STEP41_DIR / "factorization_defect_clean_separation_step41.py"
STEP65_BUILD = STEP65_DIR / "proton_monopole_fork_resolution_step65.py"

STEP59_BUILD_SHA256 = "29dfae0b9ad223926487cdf71a6b44458f0b7b3126895f5927ae2a43574c1669"
STEP41_BUILD_SHA256 = "cadc5bf72d100accd4c2cd687373edf4592c19f89c34aaa3c8838ae976d0fdee"
STEP65_BUILD_SHA256 = "739e7c9a16bd3593283f6979f4294ff59fb333db3d5fc62c71688f236110cd63"

REQUIRED = [
    "step69_results_summary.md",
    "step69_schema.json",
    "content_classification_step69.csv",
    "nonclaim_boundary_step69.md",
    "record_stability_prediction_statement_step69.tex",
    "record_stability_branch_table_step69.csv",
    "anti_circularity_witnesses_step69.csv",
    "f27_f48_branch_confirmation_step69.csv",
    "frozen_machinery_step69.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "record_stability_prediction_step69.py",
    "run_step69.py",
]

OVERCLAIMS = [
    "proves the proton is stable",
    "proves proton stable",
    "proton is stable",
    "derives baryon conservation",
    "rules out all guts in nature",
    "rules out all grand-unified models in nature",
]

CONTAMINATION = ["psi", "field", "stress_energy", "metric"]


def fail(message: str) -> None:
    raise SystemExit(f"run_step69.py: FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truth(value: Any) -> bool:
    return str(value) == "True" or value is True


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compute_table() -> tuple[list[dict[str, str]], dict[str, int]]:
    rows = read_csv(STEP59_SCORES)
    table = {
        "record_stable_clean": 0,
        "record_stable_breaking": 0,
        "not_record_stable_clean": 0,
        "not_record_stable_breaking": 0,
    }
    for row in rows:
        rs = truth(row["RS_member"])
        clean = truth(row["CS_member"])
        if rs and clean:
            table["record_stable_clean"] += 1
        elif rs and not clean:
            table["record_stable_breaking"] += 1
        elif (not rs) and clean:
            table["not_record_stable_clean"] += 1
        else:
            table["not_record_stable_breaking"] += 1
    return rows, table


def expected_verdict(count: int) -> str:
    return (
        "RECORD_STABILITY_FORBIDS_PROTON_DECAY_AND_MONOPOLES_ENUMERATION_STRENGTH"
        if count == 0
        else "RECORD_STABILITY_BARYON_MONOPOLE_LINK_FALSIFIED_ON_CARRIER"
    )


def check_required() -> None:
    missing = [name for name in REQUIRED if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing artifacts: {', '.join(missing)}")


def check_hashes() -> None:
    if sha256(STEP59_BUILD) != STEP59_BUILD_SHA256:
        fail("Step59 build sha mismatch")
    if sha256(STEP41_BUILD) != STEP41_BUILD_SHA256:
        fail("Step41 build sha mismatch")
    if sha256(STEP65_BUILD) != STEP65_BUILD_SHA256:
        fail("Step65 build sha mismatch")
    rows = read_csv(ARTIFACT_DIR / "frozen_machinery_step69.csv")
    if len(rows) != 4:
        fail("frozen machinery ledger must have four rows")
    for row in rows:
        if row["sha256"] != row["expected_sha256"] or row["imported_verbatim"] != "True":
            fail(f"frozen machinery mismatch for {row['source']}")


def check_schema() -> None:
    scores, table = compute_table()
    schema = load_json(ARTIFACT_DIR / "step69_schema.json")
    record_stable_count = table["record_stable_clean"] + table["record_stable_breaking"]
    clean_count = table["record_stable_clean"] + table["not_record_stable_clean"]
    breaking_count = table["record_stable_breaking"] + table["not_record_stable_breaking"]
    verdict_count = table["record_stable_breaking"]
    expected = {
        "carrier_source": "step59_frozen_import",
        "carrier_size": len(scores),
        "record_stable_count": record_stable_count,
        "clean_branch_count": clean_count,
        "breaking_branch_count": breaking_count,
        "record_stable_breaking_count": verdict_count,
        "prediction_holds": verdict_count == 0,
        "verdict": expected_verdict(verdict_count),
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema mismatch for {key}: {schema.get(key)} != {value}")
    if not schema["enumeration_strength_not_theorem"]:
        fail("enumeration caveat missing")
    if not schema["conditional_on_memory_stability"]:
        fail("conditional-on-memory-stability flag missing")
    if not schema["selection_construction_not_cosourcing"]:
        fail("selection construction guard missing")


def check_branch_table() -> None:
    _scores, table = compute_table()
    rows = read_csv(ARTIFACT_DIR / "record_stability_branch_table_step69.csv")
    found = {(row["record_stability"], row["branch"]): int(row["count"]) for row in rows}
    expected = {
        ("record_stable", "clean"): table["record_stable_clean"],
        ("record_stable", "breaking"): table["record_stable_breaking"],
        ("not_record_stable", "clean"): table["not_record_stable_clean"],
        ("not_record_stable", "breaking"): table["not_record_stable_breaking"],
    }
    if found != expected:
        fail(f"branch table mismatch: {found} != {expected}")


def check_anti_circularity() -> None:
    rows, _table = compute_table()
    by_id = {row["carrier_id"]: row for row in rows}
    controls = {row["control"]: row for row in read_csv(ARTIFACT_DIR / "anti_circularity_witnesses_step69.csv")}
    for name in ["substrate_only_breaking", "capacity_only_breaking", "conjunction_clean_nonvacuous"]:
        if name not in controls or controls[name]["passes"] != "True":
            fail(f"missing anti-circularity control: {name}")
    sub = by_id[controls["substrate_only_breaking"]["carrier_id"]]
    cap = by_id[controls["capacity_only_breaking"]["carrier_id"]]
    conj = by_id[controls["conjunction_clean_nonvacuous"]["carrier_id"]]
    if truth(sub["CS_member"]) or not truth(sub["substrate_passes"]) or truth(sub["capacity_passes"]):
        fail("substrate-only breaking witness does not fire")
    if truth(cap["CS_member"]) or not truth(cap["capacity_passes"]) or truth(cap["substrate_passes"]):
        fail("capacity-only breaking witness does not fire")
    if not truth(conj["CS_member"]) or not truth(conj["RS_member"]):
        fail("record-stable clean nonvacuity witness does not fire")


def check_f27_f48() -> None:
    schema = load_json(ARTIFACT_DIR / "step69_schema.json")
    if not schema["f27_clean_no_decay"] or not schema["f48_clean_no_monopole"]:
        fail("clean branch F27/F48 confirmation missing")
    step45 = load_json(STEP45_DIR / "schema.json")
    step46 = load_json(STEP46_DIR / "schema.json")
    if int(step45["clean_shadow_baryon_obstruction_count"]) != 0:
        fail("Step45 clean obstruction not zero")
    if int(step46["clean_shadow_gluing_obstruction"]) != 0:
        fail("Step46 clean obstruction not zero")
    if int(step45["dynamical_breaking_baryon_obstruction_count"]) <= 0:
        fail("Step45 breaking obstruction missing")
    if int(step46["dynamical_breaking_gluing_obstruction"]) <= 0:
        fail("Step46 breaking obstruction missing")


def check_text_guards() -> None:
    text_names = [
        "step69_results_summary.md",
        "step69_schema.json",
        "content_classification_step69.csv",
        "nonclaim_boundary_step69.md",
        "record_stability_prediction_statement_step69.tex",
        "record_stability_branch_table_step69.csv",
        "anti_circularity_witnesses_step69.csv",
        "f27_f48_branch_confirmation_step69.csv",
        "mode_b_constraint_ledger.csv",
        "mode_b_target_lineage.csv",
        "mode_b_grammar_manifest.csv",
    ]
    combined = "\n".join((ARTIFACT_DIR / name).read_text(encoding="utf-8").lower() for name in text_names)
    for phrase in OVERCLAIMS:
        if phrase in combined:
            fail(f"overclaim phrase present: {phrase}")
    for token in CONTAMINATION:
        if token in combined:
            fail(f"cross-track token present: {token}")


def run_prior_self_checks() -> None:
    for path in [STEP59_DIR / "run_step59.py", STEP65_DIR / "run_step65.py"]:
        result = subprocess.run([sys.executable, str(path), "--self"], cwd=THREAD_DIR.parents[0], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            fail(f"prior validator failed: {path}\n{result.stdout}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if not args.self and not args.chain:
        parser.error("use --self or --chain")
    check_required()
    check_hashes()
    check_schema()
    check_branch_table()
    check_anti_circularity()
    check_f27_f48()
    check_text_guards()
    if args.chain:
        run_prior_self_checks()
    print(f"run_step69.py: PASS ({'--chain' if args.chain else '--self'})")


if __name__ == "__main__":
    main()
