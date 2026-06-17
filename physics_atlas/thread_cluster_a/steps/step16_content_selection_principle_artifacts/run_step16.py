#!/usr/bin/env python3
"""Validate Cluster A Step 16 content-selection principle artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "content_selection_principle_step16.py"

STEP_RUNNERS = [
    STEPS_DIR / "step1_shared_selection_layer_frame_artifacts" / "run_step1.py",
    STEPS_DIR / "step2_p2_selection_constraint_artifacts" / "run_step2.py",
    STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py",
    STEPS_DIR / "step4_e043_scale_selection_artifacts" / "run_step4.py",
    STEPS_DIR / "step5_e009_uv_fiber_artifacts" / "run_step5.py",
    STEPS_DIR / "step6_e043_horn_adjudication_artifacts" / "run_step6.py",
    STEPS_DIR / "step7_consolidated_statement_artifacts" / "run_step7.py",
    STEPS_DIR / "step8_structural_token_blind_selection_artifacts" / "run_step8.py",
    STEPS_DIR / "step9_facet_factorization_test_artifacts" / "run_step9.py",
    STEPS_DIR / "step10_adjudication_robustness_sweep_artifacts" / "run_step10.py",
    STEPS_DIR / "step11_refinement_order_battery_artifacts" / "run_step11.py",
    STEPS_DIR / "step14_real_anomaly_enrichment_artifacts" / "run_step14.py",
    STEPS_DIR / "step15_minimal_anomaly_support_artifacts" / "run_step15.py",
]

REQUIRED_FILES = [
    "content_selection_principle_step16.py",
    "principles_step16.csv",
    "conjunctions_step16.csv",
    "support_principle_matrix_step16.csv",
    "overall_verdict_step16.json",
    "candidate_law_obligations_step16.csv",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "step16_statement.tex",
    "run_step16.py",
]

OVERCLAIM_PATTERNS = [
    r"\bderives the gauge group\b",
    r"\bderive the gauge group\b",
    r"\bderives the SM content\b",
    r"\bderive the SM content\b",
    r"\bderives the SM\b",
    r"\bderive the SM\b",
    r"\bderives the standard model\b",
    r"\bselects the vacuum\b",
    r"\bsolves the hierarchy\b",
    r"\bpredicts the fermion masses\b",
    r"\bcomputes the cosmological constant\b",
    r"\bcross-layer derivation\b",
    r"\bframe-transfer certificate\b",
    r"\bco-sourcing\b",
    r"\bcommon-refinement\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
]

BUILD_FORBIDDEN = [
    "psi",
    "ψ",
    "co-sourcing",
    "common-refinement",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
]

TOKEN_BLIND_FORBIDDEN = [
    "G_SM",
    "R_SM_CHIRAL",
    "Y_SM_TOY",
    "EW_LOW_TOY",
    "UV_SM_TOY",
    "VAC_SM_TOY",
    "n_gen == 3",
    "n_gen==3",
    "REALIZED_WORLD",
    "world_id ==",
]

ALLOWED_GRADES = {"finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step16.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def run_build_script() -> None:
    runpy.run_path(str(BUILD_SCRIPT), run_name="__main__")


def run_prior_validators() -> None:
    for runner in STEP_RUNNERS:
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
            cwd=STEPS_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(
                f"{runner.name} failed during Step 16 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_script_guards() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    for snippet in BUILD_FORBIDDEN + TOKEN_BLIND_FORBIDDEN:
        if snippet in text:
            fail(f"build script contains forbidden token or construction term: {snippet}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step16.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim/model pattern found: {pattern}")


def validate_principles() -> None:
    rows = {row["principle_id"]: row for row in read_csv("principles_step16.csv")}
    expected = {
        "faithfulness": (True, 16, True, False),
        "sector_diversity": (True, 4, True, False),
        "weak_doublet_singlet_mixing": (True, 4, True, False),
        "charge_integrality": (True, 26, True, False),
        "residual_chiral_complexity": (True, 28, True, False),
        "simple_group_embedding_pattern": (True, 2, True, False),
        "minimality_control": (False, 12, True, True),
    }
    if set(rows) != set(expected):
        fail(f"principle ids mismatch: {sorted(rows)}")
    for principle_id, (sm_ok, survivor_count, non_circular, control) in expected.items():
        row = rows[principle_id]
        if (row["satisfied_by_reference"] == "True") is not sm_ok:
            fail(f"{principle_id} reference satisfaction mismatch")
        if int(row["survivor_count"]) != survivor_count:
            fail(f"{principle_id} survivor count expected {survivor_count}, got {row['survivor_count']}")
        if (row["non_circular"] == "True") is not non_circular:
            fail(f"{principle_id} non-circular flag mismatch")
        if (row["control"] == "True") is not control:
            fail(f"{principle_id} control flag mismatch")
        if row["credited_selection_law"] == "True" and row["non_circular"] != "True":
            fail(f"{principle_id} credits a circular principle")
    if rows["minimality_control"]["satisfied_by_reference"] != "False":
        fail("can-fail control failed: minimality control unexpectedly selects the reference support")
    if int(rows["minimality_control"]["survivor_count"]) < 1:
        fail("can-fail control failed: minimality control has no survivors")


def validate_conjunctions_and_verdict() -> None:
    conjunctions = read_csv("conjunctions_step16.csv")
    if not conjunctions:
        fail("conjunctions_step16.csv is empty")
    credited = [row for row in conjunctions if row["credited_selection_law"] == "True"]
    if credited:
        fail(f"unexpected credited selection-law conjunctions: {credited[:3]}")
    best = [
        row
        for row in conjunctions
        if row["conjunction_id"] == "charge_integrality+simple_group_embedding_pattern"
    ]
    if len(best) != 1 or best[0]["satisfied_by_reference"] != "True" or int(best[0]["survivor_count"]) != 2:
        fail("best reference-preserving conjunction mismatch")
    verdict = json.loads((ARTIFACT_DIR / "overall_verdict_step16.json").read_text(encoding="utf-8"))
    checks = {
        "support_count": 28,
        "principle_count": 7,
        "structural_principle_count": 6,
        "best_reference_conjunction_survivor_count": 2,
    }
    for key, expected in checks.items():
        if int(verdict.get(key, -1)) != expected:
            fail(f"overall verdict {key} expected {expected}, got {verdict.get(key)}")
    if verdict.get("verdict") != "rigorous_type_limit_negative":
        fail(f"unexpected verdict: {verdict.get('verdict')}")
    if verdict.get("obligation_2_status") != "advanced_as_type_limit_negative":
        fail("obligation-2 status mismatch")
    if verdict.get("any_non_circular_unique_principle") is not False:
        fail("unexpected unique principle")
    if verdict.get("any_non_circular_unique_conjunction") is not False:
        fail("unexpected unique conjunction")
    if verdict.get("minimality_control_fails_to_select_reference") is not True:
        fail("minimality can-fail control not recorded")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame transfer")


def validate_schema_and_obligations() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("overall_verdict", {}).get("verdict") != "rigorous_type_limit_negative":
        fail("schema verdict mismatch")
    rows = {row["obligation"]: row["status"] for row in read_csv("candidate_law_obligations_step16.csv")}
    expected = {
        "faithful_enrichment": "continued_from_step15",
        "independently_checkable_consequence": "advanced_as_type_limit_negative",
        "derived_formula": "not_advanced_this_step",
        "limit_recovery": "bounded_by_step15_support_set",
    }
    for key, status in expected.items():
        if rows.get(key) != status:
            fail(f"obligation {key} expected {status}, got {rows.get(key)}")


def validate_content_classification() -> None:
    rows = read_csv("content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"claim lacks source artifacts: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"source path must be thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact missing: {source}")


def validate_required_prose() -> None:
    summary = (ARTIFACT_DIR / "results_summary.md").read_text(encoding="utf-8")
    for snippet in [
        "rigorous_type_limit_negative",
        "No non-circular principle or conjunction uniquely selects",
        "The carried minimality control does not select",
        "advanced_as_type_limit_negative",
    ]:
        if snippet not in summary:
            fail(f"results summary missing snippet: {snippet}")
    boundary = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    if "finite fixed-gauge" not in boundary or "typed boundary" not in boundary:
        fail("nonclaim boundary missing finite/scope language")


def validate_self() -> None:
    run_build_script()
    validate_required_files()
    validate_build_script_guards()
    scan_overclaims()
    validate_principles()
    validate_conjunctions_and_verdict()
    validate_schema_and_obligations()
    validate_content_classification()
    validate_required_prose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Cluster A Step 16 artifacts.")
    parser.add_argument("--self", action="store_true", help="validate only Step 16 artifacts")
    parser.add_argument("--chain", action="store_true", help="run prior validators once, then Step 16")
    args = parser.parse_args()
    if args.self and args.chain:
        fail("choose either --self or --chain, not both")
    if args.chain:
        run_prior_validators()
    validate_self()
    print("run_step16.py: PASS")


if __name__ == "__main__":
    main()
