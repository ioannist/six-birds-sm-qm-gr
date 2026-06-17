#!/usr/bin/env python3
"""Validate Cluster A Step 53 named competitor-structure artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "competitor_structures_step53.py"

REQUIRED_FILES = [
    "competitor_structures_step53.py",
    "competitor_table_step53.csv",
    "sm_consistency_control_step53.csv",
    "step53_results_summary.md",
    "step53_schema.json",
    "content_classification_step53.csv",
    "nonclaim_boundary_step53.md",
    "step53_statement.tex",
    "run_step53.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "generated_vs_input_step53.csv",
    "negative_controls_step53.csv",
    "anti_smuggle_self_check_step53.csv",
    "six_gate_audit_step53.csv",
]

DEPENDENCY_COMMANDS = [
    [STEPS_DIR / "step43_mode_b_window_closure_artifacts" / "run_step43.py", "--chain"],
    [STEPS_DIR / "step44_mode_b_window_closure_factor_count_artifacts" / "run_step44.py", "--chain"],
]

ALLOWED_GATES = {
    "mass-closure",
    "factor-count>=3 component-cap route-completeness bound",
    "outside SU(N)-product alphabet; fund dim 10 > cap 6",
    "outside SU(N)-product alphabet; fund dim 27 > cap 6",
}

OVERCLAIM_PATTERNS = [
    r"\bderives?\s+(?:a\s+)?constant\b",
    r"\bpredicts?\s+(?:a\s+)?constant\b",
    r"\bderives?\s+(?:a\s+)?mass\b",
    r"\bpredicts?\s+(?:a\s+)?mass\b",
    r"\bproves?\s+the\s+Standard\s+Model\b",
    r"\bSM\s+gauge\s+structure\s+generated\b",
    r"\bproven\s+unique\b",
    r"\bcloses?\s+the\s+SM\s+gap\s+unconditionally\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew physics\b",
    r"\bco-sourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step53.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_logic() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "COMPETITORS =" not in text:
        fail("declared competitor list missing")
    if "classify_competitor(" not in text or "classify_su_product(" not in text:
        fail("computed competitor classification functions missing")
    if "step43" not in text or "step44" not in text:
        fail("Step43/44 source use missing")
    forbidden_new_rule_snippets = [
        "if comp[\"name\"] == \"SU(5)\"",
        "if comp['name'] == 'SU(5)'",
        "exclude_competitor",
    ]
    for snippet in forbidden_new_rule_snippets:
        if snippet in text:
            fail(f"build logic contains competitor-specific exclusion snippet: {snippet}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step53.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step53_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 53:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_named_competitor_computation":
        fail("schema orientation mismatch")
    if schema.get("verdict") != "COMPETITORS_TABULATED_SM_SELECTED_IN_COVERED_WINDOW":
        fail("unexpected Step 53 verdict")
    if schema.get("sm_control_clean_survivors") != 8:
        fail("SM control should retain 8 clean supports")
    expected_buckets = {
        "SU(5)": "IN_WINDOW_FILTER_EXCLUDED",
        "flipped SU(5)": "IN_WINDOW_FILTER_EXCLUDED",
        "Pati-Salam SU(4)xSU(2)xSU(2)": "CAP_EXCLUDED",
        "left-right SU(3)xSU(2)xSU(2)xU(1)": "CAP_EXCLUDED",
        "trinification SU(3)xSU(3)xSU(3)": "CAP_EXCLUDED",
        "SO(10)": "OUT_OF_ALPHABET_OR_WINDOW",
        "E6": "OUT_OF_ALPHABET_OR_WINDOW",
    }
    if schema.get("competitor_buckets") != expected_buckets:
        fail("schema competitor buckets mismatch")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_smuggle_self_check_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    rows = {row["name"]: row for row in read_csv("competitor_table_step53.csv")}
    if len(rows) != 7:
        fail(f"expected 7 competitor rows, got {len(rows)}")
    expectations = {
        "SU(5)": ("IN_WINDOW_FILTER_EXCLUDED", "mass-closure", "False", "5"),
        "flipped SU(5)": ("IN_WINDOW_FILTER_EXCLUDED", "mass-closure", "False", "5"),
        "Pati-Salam SU(4)xSU(2)xSU(2)": ("CAP_EXCLUDED", "factor-count>=3 component-cap route-completeness bound", "True", "2|2|4"),
        "left-right SU(3)xSU(2)xSU(2)xU(1)": ("CAP_EXCLUDED", "factor-count>=3 component-cap route-completeness bound", "True", "2|2|3"),
        "trinification SU(3)xSU(3)xSU(3)": ("CAP_EXCLUDED", "factor-count>=3 component-cap route-completeness bound", "True", "3|3|3"),
        "SO(10)": ("OUT_OF_ALPHABET_OR_WINDOW", "outside SU(N)-product alphabet; fund dim 10 > cap 6", "True", "10"),
        "E6": ("OUT_OF_ALPHABET_OR_WINDOW", "outside SU(N)-product alphabet; fund dim 27 > cap 6", "True", "27"),
    }
    for name, (bucket, gate, cap_conditional, toy_key) in expectations.items():
        row = rows.get(name)
        if row is None:
            fail(f"missing competitor row: {name}")
        actual = (row["window_status"], row["excluding_gate"], row["cap_conditional"], row["toy_dim_key"])
        if actual != (bucket, gate, cap_conditional, toy_key):
            fail(f"competitor row mismatch for {name}: {actual}")
        if row["excluding_gate"] not in ALLOWED_GATES:
            fail(f"competitor row cites non-pre-existing gate: {row}")
    if "same single-SU(5) row" not in rows["flipped SU(5)"]["recognition_note"]:
        fail("flipped SU(5) invisibility note missing")
    if "future/not enumerated" not in rows["SO(10)"]["computed_evidence"] or "future/not enumerated" not in rows["E6"]["computed_evidence"]:
        fail("outside-alphabet future status missing")

    sm_control = read_csv("sm_consistency_control_step53.csv")[0]
    if sm_control["passes"] != "True" or sm_control["clean_survivor_count"] != "8":
        fail("SM consistency control mismatch")
    for table in ("negative_controls_step53.csv", "anti_smuggle_self_check_step53.csv", "six_gate_audit_step53.csv"):
        for row in read_csv(table):
            if row["passes"] != "True":
                fail(f"{table} row failed: {row}")


def validate_classification() -> None:
    for row in read_csv("content_classification_step53.csv"):
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        if row["artifact"].endswith("step53_statement.tex") and row["grade"] != "finite-carrier-diagnostic":
            fail("step53_statement.tex must be finite-carrier-diagnostic")
        if row["artifact"].endswith("competitor_table_step53.csv") and row["grade"] != "finite-carrier-diagnostic":
            fail("competitor table must be finite-carrier-diagnostic")
        if row["artifact"].endswith(("step53_results_summary.md", "nonclaim_boundary_step53.md")) and row["grade"] != "organizational":
            fail("summary/nonclaim files must be organizational")
        source = THREAD_DIR / row["source"]
        if not source.exists():
            fail(f"classification source missing: {row['source']}")
        if row["source"].startswith("/"):
            fail(f"classification source must be thread-relative: {row['source']}")


def run_chain() -> None:
    for command in DEPENDENCY_COMMANDS:
        runner = command[0]
        args = [str(part) for part in command]
        result = subprocess.run(
            [sys.executable, *args],
            cwd=STEPS_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{runner.name} failed during dependency chain\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=THREAD_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"Step53 rebuild failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_self() -> None:
    validate_required_files()
    validate_build_logic()
    scan_overclaims()
    validate_schema()
    validate_tables()
    validate_classification()
    print("run_step53.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 53 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 53 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate inherited window artifacts, rebuild Step 53, then validate")
    args = parser.parse_args()
    if args.chain:
        run_chain()
    validate_self()


if __name__ == "__main__":
    main()
