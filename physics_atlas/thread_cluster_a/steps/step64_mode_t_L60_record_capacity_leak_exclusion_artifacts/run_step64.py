#!/usr/bin/env python3
"""Validate Step 64 L60 record-capacity leak-exclusion artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = ARTIFACT_DIR / "L60_record_capacity_leak_exclusion_step64.py"

REQUIRED_FILES = [
    "step64_results_summary.md",
    "step64_schema.json",
    "content_classification_step64.csv",
    "nonclaim_boundary_step64.md",
    "step64_statement.tex",
    "near_miss_table_step64.csv",
    "near_miss_pattern_step64.csv",
    "run_step64.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "frozen_machinery_step64.csv",
    "converse_probe_step64.csv",
    "anti_circularity_step64.csv",
    "six_gate_audit_step64.csv",
    "sharpened_external_lemma_step64.csv",
]

EXPECTED_HASHES = {
    "Step57_record_requirement": "8068ff17d5ca911ae12f09cc303c8e67ee47c8c92affd0fad9ca28b61fe2e75f",
    "Step35_base_substrate": "6a378357c3dea96d4e7a51e54c8dbb94af9785d39cb9622c3469d2f6a6462c06",
    "Step41_factorization_defect": "ed5be4969244ae18279a9b6fc5ba73977fc9bc47fcec81ff3c25e8ad076e19c0",
}


def fail(message: str) -> None:
    print(f"run_step64.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step64_schema.json").read_text(encoding="utf-8"))
    required = {
        "step": 64,
        "orientation": "ModeT_L60_record_capacity_leak_exclusion_attempt",
        "exit_state": "sharpened_external",
        "verdict": "L60_SHARPENED_TO_CHARGE_ORIENTATION_CAP_NO_STRUCTURAL_PROOF",
        "structural_proof_grade": "sharpened",
        "window_independent": False,
        "six_gates_pass": False,
        "anti_circularity_pass": True,
        "converse_counterexample_found": False,
        "non_CS_substrate_count": 60,
        "max_record_count_among_them": 1,
        "discharges_L60": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
    }
    for key, expected in required.items():
        if schema.get(key) != expected:
            fail(f"schema field {key!r} expected {expected!r}, got {schema.get(key)!r}")
    if schema.get("sharpened_sublemma") != "L64_charge_orientation_cap":
        fail("sharpened_sublemma should be L64_charge_orientation_cap")
    return schema


def validate_frozen_hashes() -> None:
    rows = read_csv(ARTIFACT_DIR / "frozen_machinery_step64.csv")
    by_name = {row["machinery"]: row for row in rows}
    for name, expected in EXPECTED_HASHES.items():
        row = by_name.get(name)
        if row is None:
            fail(f"missing frozen machinery row {name}")
        if row["sha256"] != expected or row["expected_sha256"] != expected:
            fail(f"hash mismatch for {name}")
        if row["status"] != "imported_verbatim":
            fail(f"frozen machinery not imported verbatim: {name}")


def validate_near_misses() -> None:
    rows = read_csv(ARTIFACT_DIR / "near_miss_table_step64.csv")
    if len(rows) != 60:
        fail(f"expected 60 near-miss rows, got {len(rows)}")
    max_tokens = max(int(row["neutral_record_token_count"]) for row in rows)
    if max_tokens != 1:
        fail(f"expected max neutral_record_token_count 1, got {max_tokens}")
    if any(int(row["transition_leak_count"]) <= 0 for row in rows):
        fail("near-miss table contains non-positive leak row")
    if any(int(row["line_dual_mirror_charge_count"]) != 0 for row in rows):
        fail("near-miss table found a line-dual mirror charge pair")
    pattern = {row["pattern"]: int(row["count"]) for row in read_csv(ARTIFACT_DIR / "near_miss_pattern_step64.csv")}
    if pattern.get("token_count_0") != 28 or pattern.get("token_count_1") != 32:
        fail(f"unexpected token pattern: {pattern}")


def validate_converse() -> None:
    rows = read_csv(ARTIFACT_DIR / "converse_probe_step64.csv")
    if not rows:
        fail("empty converse probe")
    failing = [row for row in rows if row["counterexample_found"] == "True"]
    if failing:
        fail(f"converse counterexample found: {failing[:1]}")
    inside = next((row for row in rows if row["probe"] == "inside_step59_full_carrier"), None)
    if inside is None:
        fail("missing inside_step59_full_carrier probe")
    if inside["substrate_nonclean_capacity_positive"] != "0":
        fail("inside carrier has substrate/nonclean/capacity counterexample")


def validate_audits() -> None:
    anti = read_csv(ARTIFACT_DIR / "anti_circularity_step64.csv")
    if any(row["passes"] != "True" for row in anti):
        fail("anti-circularity audit has failing rows")
    gates = {row["gate"]: row for row in read_csv(ARTIFACT_DIR / "six_gate_audit_step64.csv")}
    for gate in ("no_smuggling", "target_invariance", "anti_vacuity", "anti_circularity"):
        if gates.get(gate, {}).get("passes") != "True":
            fail(f"six-gate audit expected {gate} to pass")
    if gates.get("uniform_parametric_bound", {}).get("passes") != "False":
        fail("uniform parametric bound should fail for sharpened exit")
    if gates.get("proof_constructed", {}).get("passes") != "False":
        fail("proof_constructed should be false")


def validate_nonclaims() -> None:
    summary = (ARTIFACT_DIR / "step64_results_summary.md").read_text(encoding="utf-8")
    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary_step64.md").read_text(encoding="utf-8")
    required_summary = [
        "does not construct a proof",
        "Enumeration remains evidence, not theorem",
        "L64_charge_orientation_cap",
    ]
    for snippet in required_summary:
        if snippet not in summary:
            fail(f"summary missing snippet: {snippet}")
    for snippet in ("does not prove L60", "does not derive the SM", "frame transfer"):
        if snippet not in nonclaim:
            fail(f"nonclaim missing snippet: {snippet}")
    forbidden_positive = [
        r"\bconstructed_theorem\b",
        r"\bdischarges_L60[\"']?\s*:\s*true\b",
        r"\broot_landed[\"']?\s*:\s*true\b",
        r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
        r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    ]
    joined = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in ("step64_results_summary.md", "step64_schema.json", "step64_statement.tex", "nonclaim_boundary_step64.md")
    )
    for pattern in forbidden_positive:
        if re.search(pattern, joined):
            fail(f"forbidden positive overclaim matched: {pattern}")


def run_build() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def validate() -> None:
    validate_required_files()
    validate_schema()
    validate_frozen_hashes()
    validate_near_misses()
    validate_converse()
    validate_audits()
    validate_nonclaims()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if args.chain:
        run_build()
    validate()
    print("run_step64.py: PASS")


if __name__ == "__main__":
    main()
