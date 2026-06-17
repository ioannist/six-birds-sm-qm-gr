#!/usr/bin/env python3
"""Validate Step 54 F50 background-moduli demarcation artifacts."""

from __future__ import annotations

import csv
import hashlib
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
STEP26_DIR = THREAD_ROOT / "steps" / "step26_semiclassical_dynamics_artifacts"
STEP26_SCRIPT = STEP26_DIR / "semiclassical_dynamics_step26.py"
BUILD_SCRIPT = ARTIFACT_DIR / "f50_background_moduli_step54.py"
EXPECTED_STEP26_SHA256 = "391907fae6fdee8c4e4de1c12ee67d72fdfea4928cad1f148cc30e31584898fd"
TOL = 1e-9


REQUIRED_FILES = [
    "f50_background_moduli_step54.py",
    "step54_results_summary.md",
    "step54_schema.json",
    "content_classification_step54.csv",
    "nonclaim_boundary_step54.md",
    "f50_background_demarcation_statement_step54.tex",
    "background_sweep_step54.csv",
    "kappa_sweep_step54.csv",
    "derived_classification_step54.csv",
    "structural_note_step54.csv",
    "frozen_machinery_step54.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step54.py",
]

OVERCLAIM_PATTERNS = [
    r"\btherefore solves the cosmological-constant problem\b",
    r"\bwe solve the cosmological-constant problem\b",
    r"\bderives Lambda\b",
    r"\bpredicts the vacuum energy\b",
    r"\bframe transfer certified\b",
    r"\bcloses E018\b",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step54.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing artifact {path.name}")
    return path.read_text(encoding="utf-8")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_build() -> object:
    spec = importlib.util.spec_from_file_location("step54_build", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def derive_background(rows: list[dict[str, str]]) -> dict[str, object]:
    pass_offsets = [float(row["background_offset"]) for row in rows if row["converged"] == "True"]
    fail_offsets = [float(row["background_offset"]) for row in rows if row["converged"] != "True"]
    pass_count = len(pass_offsets)
    total = len(rows)
    degeneracy = len(set(pass_offsets))
    if pass_count == 0:
        classification = "no_admissible_background_in_sweep"
        verdict = "BACKGROUND_SELECTION_BLOCKED_NO_ADMISSIBLE_SWEEP_POINT"
    elif degeneracy == 1:
        classification = "vacuum"
        verdict = "BACKGROUND_SINGLETON_VACUUM_ON_FINITE_SWEEP"
    elif pass_count == total:
        classification = "moduli"
        verdict = "BACKGROUND_IS_F50_MODULI_NO_INLAYER_VALUE_LAW"
    else:
        classification = "bounded_moduli"
        verdict = "BACKGROUND_IS_F50_BOUNDED_MODULI_NO_INLAYER_VALUE_LAW"
    return {
        "classification": classification,
        "verdict": verdict,
        "pass_count": pass_count,
        "fail_count": len(fail_offsets),
        "degeneracy": degeneracy,
        "pass_offsets": pass_offsets,
        "fail_offsets": fail_offsets,
        "blind": pass_count == total and degeneracy > 1,
    }


def derive_kappa(rows: list[dict[str, str]]) -> dict[str, object]:
    pass_values = [float(row["kappa"]) for row in rows if row["converged"] == "True"]
    fail_values = [float(row["kappa"]) for row in rows if row["converged"] != "True"]
    return {
        "pass_values": pass_values,
        "fail_values": fail_values,
        "boundary_found": bool(pass_values and fail_values and min(fail_values) > min(pass_values)),
        "max_pass": max(pass_values) if pass_values else None,
        "min_fail": min(fail_values) if fail_values else None,
    }


def validate_presence() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_schema_and_tables() -> dict:
    schema = json.loads(read(ARTIFACT_DIR / "step54_schema.json"))
    bg_rows = load_csv(ARTIFACT_DIR / "background_sweep_step54.csv")
    k_rows = load_csv(ARTIFACT_DIR / "kappa_sweep_step54.csv")
    if len(bg_rows) < 15:
        fail("background sweep must contain at least 15 rows")
    if len(k_rows) < 8:
        fail("kappa sweep must contain enough rows to show a boundary")
    bg = derive_background(bg_rows)
    kappa = derive_kappa(k_rows)
    expected = {
        "verdict": bg["verdict"],
        "background_sweep_count": len(bg_rows),
        "background_pass_count": bg["pass_count"],
        "background_fail_count": bg["fail_count"],
        "background_degeneracy": bg["degeneracy"],
        "f50_classification": bg["classification"],
        "kappa_sweep_count": len(k_rows),
        "kappa_boundary_found": kappa["boundary_found"],
        "closure_blind_to_background_within_sweep": bg["blind"],
        "enumeration_strength_not_theorem": True,
        "forbidden_rule": "no_inlayer_lambda_value_law",
        "cross_track_demarcation_analog": "SM_F47_F26_no_value_law_on_contingent_selection",
        "solves_cc_problem": False,
        "derives_lambda": False,
        "new_measured_number": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "conditional_on_step47_for_carrier_reading": True,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if schema["f50_classification"] in {"moduli", "bounded_moduli"} and int(schema["background_degeneracy"]) <= 1:
        fail("moduli verdict requires degeneracy > 1")
    if not kappa["boundary_found"]:
        fail("kappa boundary not found")
    if schema["f50_classification"] == "bounded_moduli" and int(schema["background_fail_count"]) <= 0:
        fail("bounded_moduli requires at least one failed background")
    if abs(float(schema["kappa_max_pass"]) - float(kappa["max_pass"])) > TOL:
        fail("schema kappa_max_pass mismatch")
    if abs(float(schema["kappa_min_fail"]) - float(kappa["min_fail"])) > TOL:
        fail("schema kappa_min_fail mismatch")

    derived = {row["table"]: row for row in load_csv(ARTIFACT_DIR / "derived_classification_step54.csv")}
    bclass = derived["background_sweep_step54.csv"]
    if bclass["classification"] != bg["classification"] or bclass["verdict"] != bg["verdict"]:
        fail("derived classification table disagrees with background table")
    if not as_bool(bclass["derived_from_table"]):
        fail("derived classification row must be marked table-derived")
    return schema


def validate_frozen_and_source() -> None:
    if sha256(STEP26_SCRIPT) != EXPECTED_STEP26_SHA256:
        fail("Step26 script sha mismatch")
    frozen = load_csv(ARTIFACT_DIR / "frozen_machinery_step54.csv")
    sources = {row["source"]: row for row in frozen}
    step26_key = "physics_atlas/thread_qm_gr/steps/step26_semiclassical_dynamics_artifacts/semiclassical_dynamics_step26.py"
    if step26_key not in sources:
        fail("missing Step26 frozen row")
    if sources[step26_key]["sha256"] != EXPECTED_STEP26_SHA256 or sources[step26_key]["expected_sha256"] != EXPECTED_STEP26_SHA256:
        fail("Step26 frozen hash mismatch")
    for row in frozen:
        if len(row["sha256"]) != 64 or not as_bool(row["imported_or_read_verbatim"]):
            fail(f"bad frozen row: {row}")

    script = read(BUILD_SCRIPT)
    for required in ["step26.run_case", "CONVERGENCE_TOL", "STEPS", "BACKGROUND_OFFSETS", "KAPPA_VALUES"]:
        if required not in script:
            fail(f"build script missing required frozen/declared element {required}")
    if "converged = " in script:
        fail("build script appears to reimplement convergence verdict")


def spot_check_rows() -> None:
    build = import_build()
    step26 = build.import_step26()
    psi0, base_background, _source = step26.load_initial_field()
    kinetic = step26.kinetic_operator(len(psi0))
    bg_rows = {float(row["background_offset"]): row for row in load_csv(ARTIFACT_DIR / "background_sweep_step54.csv")}
    for offset in [-5.0, 0.0, 10.0]:
        _trace, summary, _state = step26.run_case(
            f"spot_background_{offset:+g}",
            psi0,
            base_background + offset,
            build.BACKGROUND_KAPPA,
            build.SWEEP_MIX,
            kinetic,
            step26.STEPS,
        )
        row = bg_rows[offset]
        if str(summary["converged"]) != row["converged"]:
            fail(f"background spot-check convergence mismatch for {offset}")
        if abs(float(summary["fixed_point_residual"]) - float(row["fixed_point_residual"])) > 1e-10:
            fail(f"background spot-check residual mismatch for {offset}")

    k_rows = {float(row["kappa"]): row for row in load_csv(ARTIFACT_DIR / "kappa_sweep_step54.csv")}
    for kappa in [0.3, 20.0, 30.0]:
        _trace, summary, _state = step26.run_case(
            f"spot_kappa_{kappa:g}",
            psi0,
            base_background,
            kappa,
            build.SWEEP_MIX,
            kinetic,
            step26.STEPS,
        )
        row = k_rows[kappa]
        if str(summary["converged"]) != row["converged"]:
            fail(f"kappa spot-check convergence mismatch for {kappa}")
        if abs(float(summary["fixed_point_residual"]) - float(row["fixed_point_residual"])) > 1e-10:
            fail(f"kappa spot-check residual mismatch for {kappa}")


def validate_structural_note_and_prose() -> None:
    notes = load_csv(ARTIFACT_DIR / "structural_note_step54.csv")
    if not any("background*|psi|^2" in row["condition"] and not as_bool(row["structural_b_independence"]) for row in notes):
        fail("structural note must record absence of full b-independence theorem")
    combined = "\n".join(
        read(ARTIFACT_DIR / name)
        for name in [
            "step54_results_summary.md",
            "nonclaim_boundary_step54.md",
            "f50_background_demarcation_statement_step54.tex",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for needle in [
        "Honest Grade First",
        "bounded/swept moduli",
        "kappa",
        "no_inlayer_lambda_value_law",
        "enumeration-strength",
        "does not derive Lambda",
    ]:
        if needle not in combined:
            fail(f"missing required prose: {needle}")
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern: {pattern}")


def validate_self() -> None:
    validate_presence()
    validate_schema_and_tables()
    validate_frozen_and_source()
    spot_check_rows()
    validate_structural_note_and_prose()


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
        validate_self()
        print("run_step54.py: PASS (--chain)")
    elif mode == "--self":
        validate_self()
        print("run_step54.py: PASS (--self)")
    else:
        fail("usage: run_step54.py [--self|--chain]")


if __name__ == "__main__":
    main()
