#!/usr/bin/env python3
"""Validate Step 47 common-carrier door-test artifacts."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
EXPECTED_VERDICT = "COMMON_CARRIER_IS_RECOGNITION_SOURCE_WARRANTED"
EXPECTED_LAWS = {
    "F37_complementarity_non_joint_access",
    "F51_unification_common_refinement",
    "FoEC_universal_quotient_calculus",
    "SAU_non_descending_object_discipline",
}
REQUIRED_FILES = [
    "common_carrier_door_test_step47.py",
    "step47_results_summary.md",
    "step47_schema.json",
    "content_classification_step47.csv",
    "nonclaim_boundary_step47.md",
    "common_carrier_door_test_statement_step47.tex",
    "law_door_test_step47.csv",
    "common_carrier_controls_step47.csv",
    "co_sourcing_warrant_step47.csv",
    "quotient_toy_step47.json",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step47.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing artifact {path.name}")
    return path.read_text(encoding="utf-8")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_presence() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_schema() -> None:
    schema = json.loads(read(ARTIFACT_DIR / "step47_schema.json"))
    if schema.get("verdict") != EXPECTED_VERDICT:
        fail(f"unexpected verdict {schema.get('verdict')!r}")
    if schema.get("new_physics_claim") is not False:
        fail("new_physics_claim must be false")
    if schema.get("frame_transfer_certified") is not False:
        fail("frame_transfer_certified must be false")
    if schema.get("root_landed") is not False:
        fail("root_landed must be false")
    if schema.get("landing_mode") != "LANDED_GROUND_CONDITIONAL":
        fail("Step47 must be framed as LANDED_GROUND_CONDITIONAL")
    if schema.get("premise_ground_landed") is not True:
        fail("common-carrier premise must be marked ground-landed")
    if schema.get("warrant_extended_via_step26") is not True:
        fail("Step26 warrant extension must be recorded")
    if schema.get("complementary_pair_no_carrier") is not True:
        fail("complementary-pair control did not show no carrier")
    if schema.get("non_cosourcing_no_warrant") is not True:
        fail("non-co-sourcing control did not remove warrant")
    per_law = schema.get("per_law", {})
    if set(per_law) != EXPECTED_LAWS:
        fail(f"law set mismatch: {sorted(per_law)}")
    for law, row in per_law.items():
        if row.get("gives_form") is not True:
            fail(f"{law} must give form/criterion")
        if row.get("forces_existence") is not False:
            fail(f"{law} must not be recorded as forcing existence")


def validate_tables() -> None:
    laws = load_csv(ARTIFACT_DIR / "law_door_test_step47.csv")
    if len(laws) != 4:
        fail("law_door_test_step47.csv must contain four law rows")
    for row in laws:
        if row["law"] not in EXPECTED_LAWS:
            fail(f"unexpected law row {row['law']}")
        if row["gives_form"] != "True":
            fail(f"{row['law']} does not give form")
        if row["forces_existence"] != "False":
            fail(f"{row['law']} incorrectly forces existence")

    controls = {row["control"]: row for row in load_csv(ARTIFACT_DIR / "common_carrier_controls_step47.csv")}
    comp = controls.get("complementary_noncommuting_pair")
    if comp is None or comp["passes_control"] != "True":
        fail("complementary-pair control missing or failed")
    if float(comp["value"]) <= 0.0:
        fail("complementary-pair commutator residual must be positive")
    non_cosource = controls.get("non_co_sourcing_independent_field")
    if non_cosource is None or non_cosource["passes_control"] != "True":
        fail("non-co-sourcing control missing or failed")
    if float(non_cosource["value"]) <= 0.0:
        fail("non-co-sourcing residual must be positive")

    warrant = load_csv(ARTIFACT_DIR / "co_sourcing_warrant_step47.csv")[0]
    if warrant["single_psi_sources_both"] != "True":
        fail("Step25 co-sourcing warrant not recorded")
    if warrant["non_co_sourced_control_pass"] != "False":
        fail("non-co-sourced control should not pass")
    if "steps/step26_semiclassical_dynamics_artifacts/step26_schema.json" not in warrant.get("backreaction_source", ""):
        fail("Step26 back-reaction source not recorded in warrant table")
    if warrant.get("potential_sourced_from_T00") != "True":
        fail("Step26 matter-sourced-geometry warrant not recorded")


def validate_required_prose() -> None:
    summary = read(ARTIFACT_DIR / "step47_results_summary.md")
    nonclaim = read(ARTIFACT_DIR / "nonclaim_boundary_step47.md")
    statement = read(ARTIFACT_DIR / "common_carrier_door_test_statement_step47.tex")
    required = [
        "recognition source",
        "semiclassical co-sourcing",
        "LANDED * GROUND (conditional)",
        "Step26",
        "matter-sourced geometry",
        "structural reading of the framework sources",
        "trans-semiclassical frame transfer",
        "F37",
        "F51",
        "FoEC",
        "SAU",
    ]
    combined = "\n".join([summary, nonclaim, statement])
    for needle in required:
        if needle not in combined:
            fail(f"missing required prose: {needle}")


def validate_no_overclaim() -> None:
    forbidden = [
        "SBT derives the common carrier",
        "SBT proves the common carrier",
        "the common carrier is unconditional",
        "common carrier is unconditional",
        "closes E018",
        "quantum gravity solved",
        "quantum-gravity solution",
        "QG solve",
        "frame transfer certified",
    ]
    scan_files = [
        "step47_results_summary.md",
        "step47_schema.json",
        "nonclaim_boundary_step47.md",
        "common_carrier_door_test_statement_step47.tex",
        "law_door_test_step47.csv",
        "mode_b_grammar_manifest.csv",
    ]
    for filename in scan_files:
        text = read(ARTIFACT_DIR / filename)
        lowered = text.lower()
        for phrase in forbidden:
            if phrase.lower() in lowered:
                fail(f"overclaim phrase in {filename}: {phrase}")


def run_chain() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "common_carrier_door_test_step47.py"],
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
        fail("usage: run_step47.py --self|--chain")
    if sys.argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_tables()
    validate_required_prose()
    validate_no_overclaim()
    print(f"run_step47.py: PASS {sys.argv[1]}")


if __name__ == "__main__":
    main()
