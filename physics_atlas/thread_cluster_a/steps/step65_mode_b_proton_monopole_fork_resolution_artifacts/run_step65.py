#!/usr/bin/env python3
"""Validate Step 65 proton/monopole fork-resolution artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
BUILD_SCRIPT = ARTIFACT_DIR / "proton_monopole_fork_resolution_step65.py"

REQUIRED_FILES = [
    "step65_results_summary.md",
    "step65_schema.json",
    "content_classification_step65.csv",
    "nonclaim_boundary_step65.md",
    "step65_statement.tex",
    "mapping_table_step65.csv",
    "run_step65.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "anti_circularity_step65.csv",
    "fork_object_consistency_step65.csv",
]


def fail(message: str) -> None:
    print(f"run_step65.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step65_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 65,
        "orientation": "ModeB_cross_layer_fork_resolution",
        "exit_state": "FORK_RESOLVED_TO_CLEAN_BY_MEMORY_STABILITY",
        "verdict": "MEMORY_STABILITY_SELECTS_CLEAN_BRANCH_ENUMERATION_STRENGTH",
        "mapping_exact": True,
        "breaking_reading_is_delta_fact_nonempty": True,
        "breaking_structures_all_record_incapable": True,
        "anti_circularity_pass": True,
        "conditional_on_memory_stability": True,
        "enumeration_strength": True,
        "frame_transfer_certified": False,
        "resolves_physical_proton_stability": False,
        "new_physics_claim": False,
        "root_landed": True,
        "evaluated_breaking_structure_count": 60,
        "record_stable_breaking_structure_count": 0,
        "capacity_positive_breaking_structure_count": 0,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if schema.get("L64_status", "").startswith("open") is False:
        fail("schema must record L64 as open")
    return schema


def validate_mapping() -> None:
    rows = read_csv(ARTIFACT_DIR / "mapping_table_step65.csv")
    if len(rows) != 60:
        fail(f"expected 60 breaking-reading mapping rows, got {len(rows)}")
    for row in rows:
        if row["step41_delta_fact_nonempty"] != "True":
            fail("mapping row lacks Step41 nonempty defect")
        if row["record_stability_passes"] != "False":
            fail("breaking-reading row is record-stable")
        if row["capacity_passes"] != "False":
            fail("breaking-reading row has capacity positive")
        if row["delta_witness_count"] != row["transition_leak_count"]:
            fail("delta witness count should track transition leak count")
    dims = sorted(set(row["dimensions"] for row in rows))
    if dims != ["2|4", "3|4", "4", "4|4"]:
        fail(f"unexpected breaking dimensions: {dims}")


def validate_anti_circularity() -> None:
    rows = read_csv(ARTIFACT_DIR / "anti_circularity_step65.csv")
    if len(rows) < 4:
        fail("anti-circularity audit too small")
    failing = [row for row in rows if row["passes"] != "True"]
    if failing:
        fail(f"anti-circularity failing rows: {failing}")
    checks = {row["check"] for row in rows}
    required = {
        "substrate_not_clean_reading_in_disguise",
        "capacity_not_clean_reading_in_disguise",
        "memory_branch_nonvacuous",
        "resolution_uses_conjunction",
    }
    if checks != required:
        fail(f"unexpected anti-circularity checks: {checks}")


def validate_consistency() -> None:
    rows = {row["object"]: row for row in read_csv(ARTIFACT_DIR / "fork_object_consistency_step65.csv")}
    for key in ("Step45_proton_fork", "Step46_monopole_fork"):
        row = rows.get(key)
        if row is None:
            fail(f"missing consistency row {key}")
        if row["defect_kind"] != "gauge_layer_breaking_coset" or row["used_for_resolution"] != "True":
            fail(f"{key} is not marked as gauge-layer fork object")
        if row["identity_holds"] != "True":
            fail(f"{key} witness identity failed")
    step63 = rows.get("Step63_common_refinement")
    if step63 is None:
        fail("missing Step63 consistency row")
    if step63["defect_kind"] != "inter_layer_structural_refinement" or step63["used_for_resolution"] != "False":
        fail("Step63 object must be marked separate from fork resolution")
    if step63["witness_count"] != "15":
        fail("Step63 inter-layer defect count should be 15")


def validate_nonclaims() -> None:
    summary = (ARTIFACT_DIR / "step65_results_summary.md").read_text(encoding="utf-8")
    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary_step65.md").read_text(encoding="utf-8")
    for snippet in ("conditional on requiring memory-stability", "does not prove physical proton stability", "does not solve proton decay"):
        if snippet not in summary:
            fail(f"summary missing caveat: {snippet}")
    for snippet in ("does not prove physical proton stability", "does not solve proton decay", "frame transfer"):
        if snippet not in nonclaim:
            fail(f"nonclaim missing caveat: {snippet}")
    joined = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in ("step65_results_summary.md", "nonclaim_boundary_step65.md", "step65_statement.tex", "step65_schema.json")
    )
    forbidden = [
        r"\bsolves\s+proton\s+decay\b",
        r"\bproves\s+proton\s+stable\b",
        r"\bproton\s+is\s+stable\b",
        r"\bunconditional\b",
        r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
        r"\bnew_physics_claim[\"']?\s*:\s*true\b",
        r"\bresolves_physical_proton_stability[\"']?\s*:\s*true\b",
    ]
    for pattern in forbidden:
        if re.search(pattern, joined, flags=re.IGNORECASE):
            fail(f"forbidden overclaim phrase matched: {pattern}")


def run_build() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def validate() -> None:
    validate_required_files()
    validate_schema()
    validate_mapping()
    validate_anti_circularity()
    validate_consistency()
    validate_nonclaims()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if args.chain:
        run_build()
    validate()
    print("run_step65.py: PASS")


if __name__ == "__main__":
    main()
