#!/usr/bin/env python3
"""Validate Step 48 ladder-vs-fork resolution artifacts."""

from __future__ import annotations

import csv
import json
import math
import os
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
TOL = 1e-10
EXPECTED_VERDICT = "FORK_SELECTED_OVER_LADDER"
OLD_WEAK_RT_PREFIX = "emergent_" + "spacetime_ladder"
REQUIRED = [
    "ladder_vs_fork_resolution_step48.py",
    "step48_results_summary.md",
    "step48_schema.json",
    "content_classification_step48.csv",
    "nonclaim_boundary_step48.md",
    "ladder_vs_fork_statement_step48.tex",
    "ladder_vs_fork_sim_step48.csv",
    "fork_closure_step48.csv",
    "rt_relation_frame_step48.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step48.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing artifact {path.name}")
    return path.read_text(encoding="utf-8")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def close(value: float, expected: float, tol: float = 1e-10) -> bool:
    return math.isclose(value, expected, rel_tol=0.0, abs_tol=tol)


def validate_presence() -> None:
    for name in REQUIRED:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_schema() -> None:
    schema = json.loads(read(ARTIFACT_DIR / "step48_schema.json"))
    if schema.get("verdict") != EXPECTED_VERDICT:
        fail(f"unexpected verdict {schema.get('verdict')!r}")
    if schema.get("conditional_on_step47_premise") is not True:
        fail("Step48 must be conditional on Step47 premise")
    if schema.get("step47_premise_verdict") != "COMMON_CARRIER_IS_RECOGNITION_SOURCE_WARRANTED":
        fail("Step47 premise verdict not recorded")
    if schema.get("fork_closes") is not True:
        fail("fork must close")
    if schema.get("nested_control_flips") is not True:
        fail("nested control must flip")
    if schema.get("rt_is_fork_relation") is not True:
        fail("RT must be framed as a fork relation")
    if float(schema.get("strongest_ladder_factorization_defect", 0.0)) <= 0.0:
        fail("strongest ladder defect must be positive")
    if OLD_WEAK_RT_PREFIX + "_defect" in schema:
        fail("old weak-RT predecessor schema field is still present")
    if float(schema.get("weak_rt_ladder_defect", 0.0)) <= 0.0:
        fail("weak-RT ladder defect must be positive")
    if "weak_rt_row_residual" not in schema:
        fail("weak-RT row residual missing from schema")
    if "strong bulk reconstruction" not in str(schema.get("strong_bulk_reconstruction_residual", "")):
        fail("strong bulk reconstruction residual not named")
    if not close(float(schema["strongest_ladder_route_mismatch"]), 0.5):
        fail("strongest ladder route mismatch changed from accepted value 0.5")
    if not close(float(schema["nested_control_defect"]), 0.0):
        fail("nested control defect must be zero")
    if schema.get("new_physics_claim") is not False:
        fail("new_physics_claim must be false")
    if schema.get("frame_transfer_certified") is not False:
        fail("frame_transfer_certified must be false")


def validate_tables() -> None:
    attempts = {row["attempt_id"]: row for row in load_csv(ARTIFACT_DIR / "ladder_vs_fork_sim_step48.csv")}
    for key in [
        "plain_ladder_GR_as_quotient_of_QM",
        "weak_RT_QM_accessible_shadow_ladder",
        "nested_control_GR_nested_as_quotient_of_QM",
    ]:
        if key not in attempts:
            fail(f"missing ladder attempt row {key}")
    direct = attempts["plain_ladder_GR_as_quotient_of_QM"]
    weak_rt = attempts["weak_RT_QM_accessible_shadow_ladder"]
    nested = attempts["nested_control_GR_nested_as_quotient_of_QM"]
    if any(OLD_WEAK_RT_PREFIX in key for key in attempts):
        fail("old weak-RT predecessor attempt id still present")
    for row in [direct, weak_rt]:
        if row["lawful_quotient_closes"] != "False":
            fail(f"{row['attempt_id']} should fail as quotient")
        if int(row["pair_defect_count"]) <= 0:
            fail(f"{row['attempt_id']} must have positive pair defects")
        if float(row["row_factorization_residual"]) <= TOL:
            fail(f"{row['attempt_id']} must have positive row residual")
    if nested["lawful_quotient_closes"] != "True":
        fail("nested control must close")
    if int(nested["pair_defect_count"]) != 0:
        fail("nested control must have zero pair defects")
    if float(nested["route_mismatch_normalized"]) > TOL:
        fail("nested control route mismatch must be zero")

    fork = {row["case_id"]: row for row in load_csv(ARTIFACT_DIR / "fork_closure_step48.csv")}
    if fork["fork_L_to_QM_and_GR"]["fork_closes"] != "True":
        fail("fork closure row must close")
    rt = load_csv(ARTIFACT_DIR / "rt_relation_frame_step48.csv")[0]
    if rt["framing_in_step48"] != "fork_relation_between_co_sourced_readouts_not_ladder_quotient":
        fail("RT framing row does not state fork relation")


def validate_prose() -> None:
    combined = "\n".join(
        read(ARTIFACT_DIR / name)
        for name in [
            "step48_results_summary.md",
            "nonclaim_boundary_step48.md",
            "ladder_vs_fork_statement_step48.tex",
        ]
    )
    for needle in [
        "conditional on",
        "Step47",
        "FORK relation",
        "WEAK-RT / QM-accessible-shadow ladder",
        "strong bulk reconstruction",
        "not a lawful quotient",
        "nested control",
    ]:
        if needle not in combined:
            fail(f"missing required prose: {needle}")


def validate_no_overclaim() -> None:
    forbidden = [
        "ladder/fork resolved unconditionally",
        "derives quantum gravity",
        "GR proven emergent as metaphysics",
        "GR proven not-emergent as metaphysics",
        "closes E018",
        "frame transfer certified",
        "solves quantum gravity",
    ]
    for path in ARTIFACT_DIR.iterdir():
        if path.suffix not in {".md", ".tex", ".json", ".csv"}:
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in forbidden:
            if phrase.lower() in text:
                fail(f"overclaim phrase in {path.name}: {phrase}")


def run_chain() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "ladder_vs_fork_resolution_step48.py"],
        cwd=ARTIFACT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        timeout=60,
    )
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        fail("chain rebuild failed")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"--self", "--chain"}:
        fail("usage: run_step48.py --self|--chain")
    if sys.argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_tables()
    validate_prose()
    validate_no_overclaim()
    print(f"run_step48.py: PASS {sys.argv[1]}")


if __name__ == "__main__":
    main()
