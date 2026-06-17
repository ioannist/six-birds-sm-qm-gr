#!/usr/bin/env python3
"""Validate Step 53 F34 information-loss artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP42_DIR = THREAD_ROOT / "steps" / "step42_faithful_holographic_rt_enrichment_artifacts"
STEP42_SCRIPT = STEP42_DIR / "faithful_holographic_rt_enrichment_step42.py"
BUILD_SCRIPT = ARTIFACT_DIR / "f34_information_loss_step53.py"
EXPECTED_STEP42_SHA256 = "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08"
TOL = 1e-10


REQUIRED_FILES = [
    "f34_information_loss_step53.py",
    "step53_results_summary.md",
    "step53_schema.json",
    "content_classification_step53.csv",
    "nonclaim_boundary_step53.md",
    "f34_information_loss_statement_step53.tex",
    "rank_reconstruction_step53.csv",
    "gauge_orbit_step53.csv",
    "invariant_functionals_step53.csv",
    "nongauge_perturbation_step53.csv",
    "partial_readout_witness_step53.csv",
    "f34_obstruction_witnesses_step53.csv",
    "frozen_machinery_step53.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step53.py",
]


OVERCLAIM_PATTERNS = [
    r"\btherefore resolves the information paradox\b",
    r"\bwe resolve the information paradox\b",
    r"\bderives the Page curve\b",
    r"\bproves black-hole unitarity\b",
    r"\bframe transfer certified\b",
    r"\bcloses E018\b",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step53.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing artifact {path.name}")
    return path.read_text(encoding="utf-8")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def import_build() -> object:
    spec = importlib.util.spec_from_file_location("step53_build", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_presence() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_schema() -> dict:
    schema = json.loads(read(ARTIFACT_DIR / "step53_schema.json"))
    expected = {
        "verdict": "INFO_LOSS_GAUGE_ONLY_AT_FULL_BOUNDARY_REAL_AT_PARTIAL_READOUT",
        "rank_equals_internal_dim": True,
        "nongauge_perturbation_changes_state": True,
        "full_boundary_sigma_phys_obstruction_empty": True,
        "raw_sigma_obstruction_nonempty": True,
        "partial_readout_obstruction_nonempty": True,
        "f34_full_verdict": "legitimate_loss_gauge_only",
        "f34_partial_verdict": "illegitimate_loss",
        "forbidden_rule": "holographic_carrier_forbids_physical_info_loss_at_full_boundary",
        "resolves_information_paradox": False,
        "page_curve_derived": False,
        "new_measured_number": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "conditional_on_step47_for_carrier_reading": True,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if int(schema["state_rank_computed"]) != int(schema["internal_dim"]):
        fail("rank must equal internal dimension")
    if float(schema["gauge_invariance_residual"]) >= 1e-10:
        fail("gauge invariance residual too large")
    if float(schema["explicit_G_reconstruction_residual"]) >= 1e-8:
        fail("explicit G reconstruction residual too large")
    if float(schema["partial_reduced_state_residual"]) >= 1e-10:
        fail("partial reduced-state residual too large")
    if float(schema["partial_full_state_change_residual"]) <= 1e-3:
        fail("partial witness does not change full boundary state enough")
    if float(schema["partial_observable_gap"]) <= 1e-4:
        fail("partial witness observable gap too small")
    if float(schema["partial_observable_gauge_invariance_residual"]) >= 1e-10:
        fail("partial observable is not gauge-invariant enough")
    return schema


def validate_source_blocks() -> None:
    script = read(BUILD_SCRIPT)
    start = "# GAUGE_INVARIANT_FUNCTIONALS_BEGIN"
    end = "# GAUGE_INVARIANT_FUNCTIONALS_END"
    if start not in script or end not in script:
        fail("gauge-invariant functional source block missing")
    block = script.split(start, 1)[1].split(end, 1)[0]
    forbidden = ["boundary_state_matrix", "entropy_from_region", "state_matrix", "def boundary"]
    for token in forbidden:
        if token in block:
            fail(f"gauge-invariant functional block uses forbidden boundary shortcut {token!r}")
    for token in ["left", "right", "gram_left", "gram_right"]:
        if token not in block:
            fail(f"gauge-invariant functional block missing interior token {token!r}")


def validate_rank_and_gauge_rows() -> None:
    rank_rows = load_csv(ARTIFACT_DIR / "rank_reconstruction_step53.csv")
    if len(rank_rows) < 3:
        fail("rank table must contain several seeds")
    for row in rank_rows:
        if int(row["state_rank_computed"]) != int(row["internal_dim"]):
            fail(f"rank mismatch: {row}")
        for key in ["explicit_G_left_residual", "explicit_G_right_residual", "explicit_G_state_residual"]:
            if float(row[key]) >= 1e-8:
                fail(f"explicit G residual too large: {key} {row}")

    gauge_rows = load_csv(ARTIFACT_DIR / "gauge_orbit_step53.csv")
    if len(gauge_rows) < 9:
        fail("gauge table should include several seeds and gauges")
    for row in gauge_rows:
        if float(row["gauge_state_residual"]) >= 1e-10:
            fail(f"gauge state residual too large: {row}")
        if float(row["raw_left_difference_norm"]) <= 1e-6 and float(row["raw_right_difference_norm"]) <= 1e-6:
            fail(f"raw gauge witness did not change raw coordinates: {row}")
        if float(row["spectrum_invariant_residual"]) >= 1e-8:
            fail(f"gauge invariant spectrum changed: {row}")
        if not as_bool(row["gauge_obstruction_raw_nonempty"]):
            fail(f"raw obstruction not recorded: {row}")
        if not as_bool(row["gauge_obstruction_phys_empty"]):
            fail(f"physical gauge obstruction not empty: {row}")


def validate_invariants_and_partial() -> None:
    inv_rows = load_csv(ARTIFACT_DIR / "invariant_functionals_step53.csv")
    if len(inv_rows) < 3:
        fail("invariant table must contain several rows")
    for row in inv_rows:
        if "interior tensors" not in row["definition_source"]:
            fail("invariant functional must be sourced from interior tensors")
        if float(row["boundary_recovery_residual"]) >= 1e-8:
            fail(f"boundary recovery residual too large: {row}")
        if not as_bool(row["gauge_invariant_checked"]):
            fail(f"invariant row not checked: {row}")

    partial_rows = load_csv(ARTIFACT_DIR / "partial_readout_witness_step53.csv")
    if len(partial_rows) != 1:
        fail("expected one partial witness row")
    row = partial_rows[0]
    if float(row["reduced_state_residual"]) >= 1e-10:
        fail("partial reduced states must match")
    if float(row["full_boundary_state_change_residual"]) <= 1e-3:
        fail("partial witness must change full state")
    if float(row["observable_gap"]) <= 1e-4:
        fail("partial witness observable gap too small")
    if float(row["observable_gauge_invariance_residual"]) >= 1e-10:
        fail("partial observable must be gauge-invariant")
    if not as_bool(row["partial_obstruction_nonempty"]) or not as_bool(row["not_gauge_transform"]):
        fail("partial witness verdict booleans must pass")


def validate_obstruction_rows() -> None:
    rows = {row["case_id"]: row for row in load_csv(ARTIFACT_DIR / "f34_obstruction_witnesses_step53.csv")}
    for key in ["rho_full_sigma_raw", "rho_full_sigma_phys", "rho_partial_sigma_phys"]:
        if key not in rows:
            fail(f"missing obstruction case {key}")
    if as_bool(rows["rho_full_sigma_raw"]["obstruction_empty"]):
        fail("raw full-boundary obstruction should be nonempty")
    if not as_bool(rows["rho_full_sigma_phys"]["obstruction_empty"]):
        fail("physical full-boundary obstruction should be empty")
    if as_bool(rows["rho_partial_sigma_phys"]["obstruction_empty"]):
        fail("partial physical obstruction should be nonempty")


def recompute_teeth() -> None:
    build = import_build()
    if sha256(STEP42_SCRIPT) != build.EXPECTED_STEP42_SHA256:
        fail("Step42 sha256 mismatch on recompute")
    step42 = build.import_step42()
    rank_rows, cache = build.rank_reconstruction_rows(step42)
    if not all(row["rank_equals_internal_dim"] for row in rank_rows):
        fail("recomputed rank check failed")
    max_recon = max(
        max(float(row["explicit_G_left_residual"]), float(row["explicit_G_right_residual"]), float(row["explicit_G_state_residual"]))
        for row in rank_rows
    )
    if max_recon >= 1e-8:
        fail("recomputed explicit-G reconstruction too large")
    gauge_rows, _invariant_rows = build.gauge_orbit_rows(cache)
    if max(float(row["gauge_state_residual"]) for row in gauge_rows) >= 1e-10:
        fail("recomputed gauge invariance failed")
    partial = build.partial_witness_rows(cache)[0]
    if float(partial["reduced_state_residual"]) >= 1e-10:
        fail("recomputed partial reduced-state equality failed")
    if float(partial["observable_gap"]) <= 1e-4:
        fail("recomputed partial observable gap too small")


def validate_frozen_and_prose() -> None:
    frozen = load_csv(ARTIFACT_DIR / "frozen_machinery_step53.csv")
    sources = {row["source"]: row for row in frozen}
    step42_key = "physics_atlas/thread_qm_gr/steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"
    if step42_key not in sources:
        fail("missing Step42 frozen source")
    if sources[step42_key]["sha256"] != EXPECTED_STEP42_SHA256 or sources[step42_key]["expected_sha256"] != EXPECTED_STEP42_SHA256:
        fail("Step42 frozen sha mismatch")
    for row in frozen:
        if len(row["sha256"]) != 64 or not as_bool(row["imported_or_read_verbatim"]):
            fail(f"bad frozen machinery row: {row}")

    combined = "\n".join(
        read(ARTIFACT_DIR / name)
        for name in [
            "step53_results_summary.md",
            "nonclaim_boundary_step53.md",
            "f34_information_loss_statement_step53.tex",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for needle in [
        "finite static",
        "no evaporation dynamics",
        "gauge-only",
        "partial readout",
        "forbids physical information loss at full-boundary",
        "generic full-rank stratum",
    ]:
        if needle not in combined:
            fail(f"missing required prose: {needle}")
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern: {pattern}")


def validate_presence_and_artifacts() -> None:
    validate_presence()
    validate_schema()
    validate_source_blocks()
    validate_rank_and_gauge_rows()
    validate_invariants_and_partial()
    validate_obstruction_rows()
    validate_frozen_and_prose()
    recompute_teeth()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--self"
    if mode == "--chain":
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT)],
            cwd=ARTIFACT_DIR,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            fail(f"build script failed:\n{result.stdout}")
        validate_presence_and_artifacts()
        print("run_step53.py: PASS (--chain)")
    elif mode == "--self":
        validate_presence_and_artifacts()
        print("run_step53.py: PASS (--self)")
    else:
        fail("usage: run_step53.py [--self|--chain]")


if __name__ == "__main__":
    main()
