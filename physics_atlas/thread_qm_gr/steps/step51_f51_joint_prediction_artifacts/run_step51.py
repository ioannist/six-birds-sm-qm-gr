#!/usr/bin/env python3
"""Validate revised Step 51 F51 joint-prediction artifacts."""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP44_DIR = THREAD_ROOT / "steps" / "step44_holographic_mmi_entropy_cone_artifacts"
STEP48_DIR = THREAD_ROOT / "steps" / "step48_ladder_vs_fork_resolution_artifacts"
STEP50_DIR = THREAD_ROOT / "steps" / "step50_born_area_one_fiber_volume_ledger_artifacts"
BUILD_SCRIPT = ARTIFACT_DIR / "f51_joint_prediction_step51.py"
TOL = 1e-9


REQUIRED_FILES = [
    "f51_joint_prediction_step51.py",
    "step51_results_summary.md",
    "step51_schema.json",
    "content_classification_step51.csv",
    "nonclaim_boundary_step51.md",
    "f51_joint_prediction_statement_step51.tex",
    "f51_commuting_squares_step51.csv",
    "geometric_dual_compatibility_step51.csv",
    "admissible_coreadouts_step51.csv",
    "admissible_sets_step51.csv",
    "child_free_witnesses_step51.csv",
    "broken_compatibility_control_step51.csv",
    "anti_circularity_step51.csv",
    "frozen_machinery_step51.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step51.py",
]


OVERCLAIM_PATTERNS = [
    r"\bnew measured prediction\b",
    r"\bsolves quantum gravity\b",
    r"\bcloses E018\b",
    r"\bframe transfer certified\b",
    r"\bunconditional derivation\b",
    r"\btherefore derives holography\b",
    r"\bwe derive holography\b",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step51.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing artifact {path.name}")
    return path.read_text(encoding="utf-8")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def validate_presence() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_schema() -> dict:
    schema = json.loads(read(ARTIFACT_DIR / "step51_schema.json"))
    expected = {
        "verdict": "F51_PARENT_FORCES_MONOGAMY_NEITHER_CHILD_DOES",
        "forced_functional": "MMI_monogamy_I3_leq_0",
        "compatibility_predicate": "geometric_dual_mincut_vector_match",
        "compatibility_predicate_mentions_i3": False,
        "forced_by_f51_compatibility": True,
        "ghz_fails_geometric_dual": True,
        "free_in_qm_alone": True,
        "free_in_gr_alone": True,
        "with_compat_min_i3_nonpositive": True,
        "with_compat_max_i3_nonpositive": True,
        "broken_compat_min_i3_positive": True,
        "broken_compatibility_unforces": True,
        "broken_compatibility_violator_survives": True,
        "is_maxwell_shape_joint_prediction": True,
        "conditional_on_step47": True,
        "recovered_known_constraint": True,
        "new_measured_number": False,
        "derives_holography": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "new_physics_claim": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if float(schema["geometric_dual_tol"]) <= 0:
        fail("geometric dual tolerance must be positive")
    if float(schema["qm_free_witness_i3"]) <= TOL:
        fail("QM free witness must have positive I3")
    if float(schema["with_compat_max_i3"]) > TOL:
        fail("with-compatibility set must satisfy MMI")
    if float(schema["broken_compat_min_i3"]) <= TOL:
        fail("broken-compatibility witness set must have positive minimum I3")
    if float(schema["no_compat_broad_max_i3"]) <= TOL:
        fail("broad no-compatibility sample must contain a positive-I3 witness")
    if float(schema["ghz_geometric_dual_max_rel_gap"]) <= float(schema["geometric_dual_tol"]):
        fail("GHZ should fail geometric-dual compatibility by exceeding tolerance")
    residuals = schema.get("f51_commuting_square_residuals", [])
    if len(residuals) != 2 or any(float(x) > TOL for x in residuals):
        fail("F51 commuting-square residuals must be two near-zero values")
    return schema


def validate_predicate_source() -> None:
    script = read(ARTIFACT_DIR / "f51_joint_prediction_step51.py")
    start = "# COMPATIBILITY_PREDICATE_BEGIN"
    end = "# COMPATIBILITY_PREDICATE_END"
    if start not in script or end not in script:
        fail("compatibility predicate markers missing")
    block = script.split(start, 1)[1].split(end, 1)[0].lower()
    forbidden = ["i3", "monogamy", "mmi", "standard_i3"]
    for token in forbidden:
        if token in block:
            fail(f"compatibility predicate block references forbidden token {token!r}")
    for required in ["entropy_vector", "area_vector", "max_rel_gap", "min_saturation_ratio"]:
        if required not in block:
            fail(f"compatibility predicate block missing {required}")
    if "passes_geometric_dual" not in script or "computed_I3_after_predicate" not in script:
        fail("script must compute I3 only after geometric-dual predicate rows are built")


def validate_commuting_squares() -> None:
    rows = load_csv(ARTIFACT_DIR / "f51_commuting_squares_step51.csv")
    if len(rows) != 2:
        fail("expected exactly two F51 commuting-square rows")
    for row in rows:
        if float(row["computed_residual_norm"]) > TOL:
            fail(f"commuting square residual not zero: {row}")
        if not as_bool(row["commutes"]):
            fail(f"commuting square not marked as commuting: {row}")


def validate_geometric_dual_rows(schema: dict) -> None:
    rows = load_csv(ARTIFACT_DIR / "geometric_dual_compatibility_step51.csv")
    if len(rows) < 4:
        fail("expected three co-sourced rows plus GHZ control in compatibility table")
    pass_rows = [row for row in rows if as_bool(row["passes_geometric_dual"])]
    ghz_rows = [row for row in rows if row["candidate_id"] == "GHZ_4party_QM_only"]
    if len(pass_rows) < 3:
        fail("expected at least three co-sourced rows to pass geometric-dual compatibility")
    if len(ghz_rows) != 1:
        fail("expected exactly one GHZ compatibility row")
    for row in rows:
        if row["compatibility_predicate"] != "geometric_dual_mincut_vector_match":
            fail(f"bad compatibility predicate label: {row}")
        if as_bool(row["predicate_references_i3"]):
            fail("compatibility predicate row says it references I3")
        if "I3" in row["compatibility_predicate"] or "i3" in row["compatibility_predicate"]:
            fail("compatibility predicate name must not be I3-based")
        if as_bool(row["passes_geometric_dual"]):
            if float(row["max_rel_gap"]) > float(schema["geometric_dual_tol"]) + 1e-12:
                fail(f"passing row exceeds geometric-dual tolerance: {row}")
            if float(row["computed_I3_after_predicate"]) > TOL:
                fail(f"passing row violates MMI after admission: {row}")
    ghz = ghz_rows[0]
    if as_bool(ghz["passes_geometric_dual"]):
        fail("GHZ must fail geometric-dual compatibility")
    if float(ghz["max_rel_gap"]) <= float(schema["geometric_dual_tol"]):
        fail("GHZ max relative gap must exceed tolerance")
    if float(ghz["computed_I3_after_predicate"]) <= TOL:
        fail("GHZ must have positive I3")


def validate_admissible_sets() -> None:
    rows = {row["set_id"]: row for row in load_csv(ARTIFACT_DIR / "admissible_sets_step51.csv")}
    required = {
        "with_geometric_dual_compatibility",
        "without_geometric_dual_compatibility_GHZ_witness_set",
        "without_geometric_dual_compatibility_broad_sample",
    }
    if not required.issubset(rows):
        fail("admissible-set table missing required rows")
    with_compat = rows["with_geometric_dual_compatibility"]
    ghz_set = rows["without_geometric_dual_compatibility_GHZ_witness_set"]
    broad = rows["without_geometric_dual_compatibility_broad_sample"]
    if not as_bool(with_compat["MMI_forced"]):
        fail("with-compatibility set must force MMI")
    if float(with_compat["max_I3"]) > TOL:
        fail("with-compatibility max I3 must be nonpositive")
    if as_bool(ghz_set["MMI_forced"]):
        fail("GHZ no-compatibility witness set must not force MMI")
    if float(ghz_set["min_I3"]) <= TOL:
        fail("GHZ no-compatibility witness-set min I3 must be positive")
    if as_bool(broad["MMI_forced"]):
        fail("broad no-compatibility sample must not force MMI")
    if float(broad["max_I3"]) <= TOL:
        fail("broad no-compatibility sample must contain positive-I3 witness")


def validate_child_witnesses() -> None:
    rows = {row["witness_id"]: row for row in load_csv(ARTIFACT_DIR / "child_free_witnesses_step51.csv")}
    if "QM_alone_GHZ_4party" not in rows:
        fail("missing GHZ QM-only witness")
    ghz = rows["QM_alone_GHZ_4party"]
    if float(ghz["I3_value"]) <= TOL:
        fail("GHZ witness must violate MMI with positive I3")
    if not as_bool(ghz["violates_F"]):
        fail("GHZ row must be marked as violating F")
    if not as_bool(ghz["child_admissible"]):
        fail("GHZ row must be child-admissible")
    if as_bool(ghz["passes_geometric_dual"]):
        fail("GHZ row must fail computed geometric-dual predicate")
    if as_bool(ghz["parent_admissible"]):
        fail("GHZ row must be excluded from parent by computed mismatch")
    if float(ghz["computed_geometric_dual_max_rel_gap"]) <= 0:
        fail("GHZ mismatch must record a positive max relative gap")
    if "computed seven-region entropy vector mismatch" not in ghz["why_excluded_by_parent"]:
        fail("GHZ exclusion reason must cite computed vector mismatch")

    if "GR_alone_geometry_without_Born_state" not in rows:
        fail("missing GR-alone underdetermination row")
    gr = rows["GR_alone_geometry_without_Born_state"]
    if "undefined" not in gr["I3_value"]:
        fail("GR-alone row must record quantum-state I3 as undefined without QM readout")


def validate_broken_compatibility() -> None:
    rows = load_csv(ARTIFACT_DIR / "broken_compatibility_control_step51.csv")
    if len(rows) != 1:
        fail("expected one broken-compatibility control")
    row = rows[0]
    if not as_bool(row["compatibility_predicate_removed"]):
        fail("broken-compatibility control must remove the predicate")
    if float(row["with_compat_max_I3"]) > TOL:
        fail("with-compatibility control max I3 must be nonpositive")
    if not as_bool(row["with_compat_MMI_forced"]):
        fail("with-compatibility set must force MMI")
    if float(row["no_compat_witness_min_I3"]) <= TOL:
        fail("no-compatibility witness-set minimum I3 must be positive")
    if float(row["no_compat_broad_max_I3"]) <= TOL:
        fail("no-compatibility broad sample must contain positive I3")
    if not as_bool(row["violator_survives"]):
        fail("violator must survive when compatibility is removed")
    if as_bool(row["F_forced_without_compatibility"]):
        fail("F must not remain forced when compatibility is removed")
    if not as_bool(row["computed_from_admissible_sets"]):
        fail("broken-compatibility booleans must be computed from admissible sets")


def validate_anti_circularity() -> None:
    for row in load_csv(ARTIFACT_DIR / "anti_circularity_step51.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-circularity gate failed: {row['gate']}")


def validate_frozen_and_prose() -> None:
    frozen = load_csv(ARTIFACT_DIR / "frozen_machinery_step51.csv")
    sources = {row["source"] for row in frozen}
    required = {
        "physics_atlas/thread_qm_gr/steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py",
        "physics_atlas/thread_qm_gr/steps/step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py",
        "physics_atlas/thread_qm_gr/steps/step47_common_carrier_door_test_artifacts/step47_schema.json",
        "physics_atlas/thread_qm_gr/steps/step48_ladder_vs_fork_resolution_artifacts/ladder_vs_fork_resolution_step48.py",
        "physics_atlas/thread_qm_gr/steps/step50_born_area_one_fiber_volume_ledger_artifacts/born_area_one_ledger_step50.py",
    }
    if not required.issubset(sources):
        fail("frozen machinery sources incomplete")
    for row in frozen:
        if len(row["sha256"]) != 64 or not as_bool(row["imported_or_read_verbatim"]):
            fail(f"bad frozen source row: {row}")

    combined = "\n".join(
        read(ARTIFACT_DIR / name)
        for name in [
            "step51_results_summary.md",
            "nonclaim_boundary_step51.md",
            "f51_joint_prediction_statement_step51.tex",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for needle in [
        "geometric-dual",
        "I3-independent",
        "seven-region entropy vector",
        "GHZ",
        "computed vector mismatch",
        "no-compatibility",
        "recovered-known",
        "not a new measured number",
    ]:
        if needle not in combined:
            fail(f"missing required prose: {needle}")
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern: {pattern}")


def run_prior_self_validators() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for directory, script in [
        (STEP44_DIR, "run_step44.py"),
        (STEP48_DIR, "run_step48.py"),
        (STEP50_DIR, "run_step50.py"),
    ]:
        result = subprocess.run(
            [sys.executable, script, "--self"],
            cwd=directory,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{directory.name}/{script} --self failed:\n{result.stdout}")


def validate_self(run_prior: bool = True) -> None:
    validate_presence()
    schema = validate_schema()
    validate_predicate_source()
    validate_commuting_squares()
    validate_geometric_dual_rows(schema)
    validate_admissible_sets()
    validate_child_witnesses()
    validate_broken_compatibility()
    validate_anti_circularity()
    validate_frozen_and_prose()
    if run_prior:
        run_prior_self_validators()


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
        validate_self(run_prior=True)
        print("run_step51.py: PASS (--chain)")
    elif mode == "--self":
        validate_self(run_prior=True)
        print("run_step51.py: PASS (--self)")
    else:
        fail("usage: run_step51.py [--self|--chain]")


if __name__ == "__main__":
    main()
