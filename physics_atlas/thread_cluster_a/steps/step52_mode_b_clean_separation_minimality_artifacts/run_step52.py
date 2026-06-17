#!/usr/bin/env python3
"""Validate Cluster A Step 52 clean-separation minimality artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "clean_separation_minimality_step52.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "run_step38.py",
    STEPS_DIR / "step45_mode_b_proton_decay_F27_artifacts" / "run_step45.py",
]

REQUIRED_FILES = [
    "clean_separation_minimality_step52.py",
    "per_support_predicates_step52.csv",
    "predicate_survivor_counts_step52.csv",
    "logical_strength_ordering_step52.csv",
    "witness_identity_step52.csv",
    "variant_definitions_step52.csv",
    "step52_results_summary.md",
    "step52_schema.json",
    "content_classification_step52.csv",
    "nonclaim_boundary_step52.md",
    "step52_statement.tex",
    "run_step52.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "generated_vs_input_step52.csv",
    "negative_controls_step52.csv",
    "anti_smuggle_self_check_step52.csv",
    "six_gate_audit_step52.csv",
]

TARGET_SELECTOR_FORBIDDEN = [
    "2|3",
    "SU(2)",
    "SU(3)",
    "U(1)",
    "hypercharge",
    "colorless",
    "is_target_reference",
]

OVERCLAIM_PATTERNS = [
    r"\bderives?\s+(?:a\s+)?constant\b",
    r"\bpredicts?\s+(?:a\s+)?constant\b",
    r"\bderives?\s+(?:a\s+)?mass\b",
    r"\bpredicts?\s+(?:a\s+)?mass\b",
    r"\bproves?\s+the\s+Standard\s+Model\b",
    r"\bcloses?\s+the\s+SM\s+gap\s+unconditionally\b",
    r"\bSM\s+gauge\s+structure\s+generated\b",
    r"\bclean-separation\s+derived\b",
    r"\bclean\s+separation\s+derived\b",
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
    print(f"run_step52.py: FAIL: {message}", file=sys.stderr)
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
    start = text.index("def predicate_base")
    end = text.index("PREDICATES")
    predicate_region = text[start:end]
    for snippet in TARGET_SELECTOR_FORBIDDEN:
        if snippet in predicate_region:
            fail(f"variant predicate references forbidden target selector: {snippet}")
    if "broken_vector_exotic_count" not in predicate_region:
        fail("clean-separation predicate does not use broken-vector count")
    if "baryon_orbit_enlarging_count" not in predicate_region or "baryon_descent_obstruction_count" not in predicate_region:
        fail("baryon variants do not use computed F27 quantities")
    if "light_forced_broken_vector_count" not in predicate_region:
        fail("no-light variant does not use computed light-vector quantity")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step52.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step52_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 52:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_minimality_computation":
        fail("schema orientation mismatch")
    if schema.get("carrier_total") != 12 or schema.get("carrier_2x3") != 8 or schema.get("carrier_su4") != 4:
        fail("carrier counts mismatch")
    expected = {
        "base_shadow": {"total": 12, "2x3": 8, "su4": 4},
        "no_light_xy": {"total": 12, "2x3": 8, "su4": 4},
        "no_baryon_violating_xy": {"total": 8, "2x3": 8, "su4": 0},
        "bare_proton_stability": {"total": 8, "2x3": 8, "su4": 0},
        "clean_separation": {"total": 8, "2x3": 8, "su4": 0},
    }
    if schema.get("per_predicate_survivor_counts") != expected:
        fail("schema survivor counts mismatch")
    if schema.get("verdict") != "MINIMALITY_MIXED":
        fail("unexpected Step 52 verdict")
    if schema.get("sufficient_weaker_predicates") != ["no_baryon_violating_xy", "bare_proton_stability"]:
        fail("sufficient weaker predicate list mismatch")
    if schema.get("insufficient_weaker_predicates") != ["no_light_xy"]:
        fail("insufficient weaker predicate list mismatch")
    if schema.get("all_su4_vectors_baryon_orbit_enlargers") is not True:
        fail("SU4 witness identity did not pass")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_smuggle_self_check_pass") is not True:
        fail("schema gate status did not pass")


def validate_tables() -> None:
    counts = {row["predicate_id"]: row for row in read_csv("predicate_survivor_counts_step52.csv")}
    expected_counts = {
        "base_shadow": ("12", "8", "4", "False"),
        "no_light_xy": ("12", "8", "4", "False"),
        "no_baryon_violating_xy": ("8", "8", "0", "True"),
        "bare_proton_stability": ("8", "8", "0", "True"),
        "clean_separation": ("8", "8", "0", "True"),
    }
    for predicate_id, expected in expected_counts.items():
        row = counts.get(predicate_id)
        if row is None:
            fail(f"missing count row for {predicate_id}")
        actual = (row["total_survivors"], row["survivors_2x3"], row["survivors_su4"], row["selection_matches_clean_cut"])
        if actual != expected:
            fail(f"count mismatch for {predicate_id}: {actual}")

    support_rows = read_csv("per_support_predicates_step52.csv")
    if len(support_rows) != 12:
        fail("expected 12 per-support rows")
    if sum(1 for row in support_rows if row["dimensions"] == "2|3") != 8:
        fail("expected eight 2|3 rows")
    if sum(1 for row in support_rows if row["dimensions"] == "4") != 4:
        fail("expected four 4 rows")
    for row in support_rows:
        if row["dimensions"] == "2|3":
            if row["broken_vector_exotic_count"] != "0" or row["baryon_orbit_enlarging_count"] != "0":
                fail(f"clean-row witness mismatch: {row}")
            if not all(row[pred] == "True" for pred in ("base_shadow", "no_light_xy", "no_baryon_violating_xy", "bare_proton_stability", "clean_separation")):
                fail(f"2|3 row should pass all predicates: {row}")
        if row["dimensions"] == "4":
            if row["broken_vector_exotic_count"] != "6" or row["baryon_orbit_enlarging_count"] != "6":
                fail(f"4-family witness mismatch: {row}")
            if row["base_shadow"] != "True" or row["no_light_xy"] != "True":
                fail(f"4-family row should pass base/no-light: {row}")
            if any(row[pred] != "False" for pred in ("no_baryon_violating_xy", "bare_proton_stability", "clean_separation")):
                fail(f"4-family row should fail baryon/clean predicates: {row}")

    identities = read_csv("witness_identity_step52.csv")
    if len(identities) != 12:
        fail("expected 12 witness identity rows")
    support_08 = next(row for row in identities if row["support_id"] == "support_08")
    expected_ids = "|".join(f"s08_broken_confining_charged_{index:02d}" for index in range(6))
    if support_08["witness_ids"] != expected_ids:
        fail("support_08 witness ids do not match the Step45 orbit-enlarger ids")
    for row in identities:
        if row["witness_count_matches_broken_vectors"] != "True" or row["orbit_enlargers_match_delta_witnesses"] != "True":
            fail(f"witness identity row failed: {row}")
        if row["step45_dynamic_identity_asserted"] != "True":
            fail("Step45 dynamic identity was not asserted")

    definitions = read_csv("variant_definitions_step52.csv")
    if any(row["uses_target_structure_literal"] != "False" for row in definitions):
        fail("variant definition uses target structure literal")
    bases = {row["predicate_id"]: row["computed_quantity_basis"] for row in definitions}
    if bases.get("no_baryon_violating_xy") != "baryon_orbit_enlarging_count":
        fail("baryon-violating predicate basis mismatch")
    if bases.get("bare_proton_stability") != "baryon_descent_obstruction_count":
        fail("proton-stability predicate basis mismatch")

    ordering = read_csv("logical_strength_ordering_step52.csv")
    def has_order(left: str, right: str, implication: str, equivalent: str) -> bool:
        return any(
            row["antecedent"] == left
            and row["consequent"] == right
            and row["implication_holds_on_carrier"] == implication
            and row["extensionally_equivalent_on_carrier"] == equivalent
            for row in ordering
        )

    if not has_order("clean_separation", "no_baryon_violating_xy", "True", "True"):
        fail("ordering missing clean => no-baryon equivalence on carrier")
    if not has_order("no_baryon_violating_xy", "bare_proton_stability", "True", "True"):
        fail("ordering missing no-baryon => proton equivalence on carrier")
    if not has_order("no_light_xy", "clean_separation", "False", "False"):
        fail("ordering should show no-light does not imply clean")

    for table in ("negative_controls_step52.csv", "anti_smuggle_self_check_step52.csv", "six_gate_audit_step52.csv"):
        for row in read_csv(table):
            if row["passes"] != "True":
                fail(f"{table} row failed: {row}")


def validate_classification() -> None:
    for row in read_csv("content_classification_step52.csv"):
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        source = THREAD_DIR / row["source"]
        if not source.exists():
            fail(f"classification source missing: {row['source']}")
        if row["source"].startswith("/"):
            fail(f"classification source must be thread-relative: {row['source']}")


def run_chain() -> None:
    for runner in DEPENDENCY_RUNNERS:
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
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
        fail(f"Step52 rebuild failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_self() -> None:
    validate_required_files()
    validate_build_logic()
    scan_overclaims()
    validate_schema()
    validate_tables()
    validate_classification()
    print("run_step52.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 52 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 52 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step 38/45, rebuild Step 52, then validate")
    args = parser.parse_args()
    if args.chain:
        run_chain()
    validate_self()


if __name__ == "__main__":
    main()
