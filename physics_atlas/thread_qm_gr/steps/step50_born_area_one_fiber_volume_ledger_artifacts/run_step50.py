#!/usr/bin/env python3
"""Validate revised Step 50 Born/area shared-combiner artifacts."""

from __future__ import annotations

import csv
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP42 = THREAD_ROOT / "steps" / "step42_faithful_holographic_rt_enrichment_artifacts"
STEP44 = THREAD_ROOT / "steps" / "step44_holographic_mmi_entropy_cone_artifacts"
STEP47 = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
BUILD_SCRIPT = ARTIFACT_DIR / "born_area_one_ledger_step50.py"
TOL = 1e-9

REQUIRED_FILES = [
    "born_area_one_ledger_step50.py",
    "step50_results_summary.md",
    "step50_schema.json",
    "content_classification_step50.csv",
    "nonclaim_boundary_step50.md",
    "born_area_one_ledger_statement_step50.tex",
    "born_area_ledger_scores_step50.csv",
    "seed_invariance_step50.csv",
    "combiner_comparison_step50.csv",
    "control_divergence_step50.csv",
    "frozen_machinery_step50.csv",
    "anti_circularity_step50.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step50.py",
]

OVERCLAIM_PATTERNS = [
    r"derives\s+the\s+Born\s+rule",
    r"derives\s+Born\s+rule",
    r"derives\s+the\s+area\s+law",
    r"derives\s+holography",
    r"solves\s+quantum\s+gravity",
    r"closes\s+E018",
    r"frame\s+transfer\s+certified",
    r"new\s+measured\s+number\s+derived",
    r"exact\s+equality\s+between\s+geometric\s+area\s+and\s+Born\s+entropy\s+is\s+claimed",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step50.py: FAIL: {message}")


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
    schema = json.loads(read(ARTIFACT_DIR / "step50_schema.json"))
    expected = {
        "verdict": "BORN_AND_AREA_SHARE_ONE_MONOGAMY_COMBINER",
        "f39_source": "geometric_mincut",
        "area_geom_seed_invariant": True,
        "born_entropy_seed_varies": True,
        "all_single_region_A_strict_gap": True,
        "i3_geom_leq_zero": True,
        "i3_born_leq_zero": True,
        "ghz_breaks_combiner": True,
        "value_link_is_saturation_trend_not_identity": True,
        "conditional_on_step47_premise": True,
        "anti_tautology_f39_is_geometric_mincut": True,
        "new_measured_number": False,
        "derives_holography": False,
        "derives_born_rule": False,
        "derives_area_law": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "new_physics_claim": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    ratio = float(schema["saturation_ratio_A"])
    if not (0.0 < ratio < 1.0 - 1e-9):
        fail("representative saturation ratio must be strictly between 0 and 1")
    if abs(float(schema["area_geom_A"]) - float(schema["born_entropy_A"])) < 1e-12:
        fail("representative area and Born entropy are machine-equal; tautology signal")
    if float(schema["i3_geom"]) > TOL:
        fail("geometric I3 must be non-positive")
    if float(schema["i3_born"]) > TOL:
        fail("Born I3 must be non-positive on co-sourced carrier")
    if float(schema["ghz_i3_born"]) <= TOL:
        fail("GHZ Born I3 must be positive")
    return schema


def validate_ledger() -> None:
    rows = load_csv(ARTIFACT_DIR / "born_area_ledger_scores_step50.csv")
    if len(rows) != 21:
        fail("ledger table must include 3 seeds x 7 regions")
    for row in rows:
        if row["f39_source"] != "Step44 geometric min-cut area ledger":
            fail(f"F39 source is not geometric min-cut for {row['case_id']} {row['region']}")
        if "entropy_from_region" in row["f39_source"] or "SVD" in row["f39_source"]:
            fail("F39 ledger source mentions state spectrum path")
        if "Born" not in row["f23_source"]:
            fail("F23 source must be Born measure")
        area = float(row["f39_area_geom"])
        born = float(row["f23_born_entropy"])
        ratio = float(row["saturation_ratio"])
        if not as_bool(row["rt_bound_holds"]):
            fail(f"RT bound failed for {row['case_id']} {row['region']}")
        if area + 1e-8 < born:
            fail(f"Born entropy exceeds geometric area for {row['case_id']} {row['region']}")
        if row["region"] in {"A", "B", "C"}:
            if not (0.0 < ratio < 1.0 - 1e-9):
                fail(f"single-leg region ratio is not strict: {row['case_id']} {row['region']}")
            if abs(area - born) < 1e-12:
                fail(f"single-leg region is machine-equal: {row['case_id']} {row['region']}")
            if not as_bool(row["strict_gap_not_identity"]):
                fail(f"strict gap not recorded: {row['case_id']} {row['region']}")


def validate_seed_invariance() -> None:
    rows = load_csv(ARTIFACT_DIR / "seed_invariance_step50.csv")
    if len(rows) != 3:
        fail("seed invariance table must contain three seeds")
    areas = [float(row["area_geom_A"]) for row in rows]
    borns = [float(row["born_entropy_A"]) for row in rows]
    if max(areas) - min(areas) > TOL:
        fail("area geometry is not seed-invariant")
    if max(borns) - min(borns) <= 1e-6:
        fail("Born entropy does not vary across seeds")
    for row in rows:
        ratio = float(row["saturation_ratio_A"])
        if not (0.0 < ratio < 1.0 - 1e-9):
            fail(f"seed row has non-strict ratio: {row}")
        if not as_bool(row["shared_monogamy_class"]):
            fail(f"seed row does not share monogamy class: {row}")


def validate_combiner_and_control() -> None:
    rows = {row["combiner"]: row for row in load_csv(ARTIFACT_DIR / "combiner_comparison_step50.csv")}
    if "MMI_monogamy_class" not in rows:
        fail("missing MMI combiner row")
    mmi = rows["MMI_monogamy_class"]
    if not as_bool(mmi["geom_satisfies_monogamy"]):
        fail("geometric ledger does not satisfy monogamy")
    if not as_bool(mmi["born_satisfies_monogamy"]):
        fail("Born ledger does not satisfy monogamy")
    if not as_bool(mmi["same_combiner_class"]):
        fail("shared monogamy class not recorded")
    if as_bool(mmi["numeric_i3_equality_claimed"]):
        fail("numeric I3 equality must not be claimed")
    if float(mmi["I3_geom"]) > TOL or float(mmi["I3_born"]) > TOL:
        fail("co-sourced I3 values must be non-positive")

    control = load_csv(ARTIFACT_DIR / "control_divergence_step50.csv")[0]
    if not as_bool(control["ghz_breaks_combiner"]):
        fail("GHZ control did not break combiner")
    if float(control["ghz_i3_born"]) <= TOL:
        fail("GHZ Born I3 should be positive")
    if float(control["geom_i3_mincut"]) > TOL:
        fail("geometric min-cut I3 should stay non-positive")


def validate_anti_circularity() -> None:
    for row in load_csv(ARTIFACT_DIR / "anti_circularity_step50.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-circularity gate failed: {row['gate']}")
    frozen = load_csv(ARTIFACT_DIR / "frozen_machinery_step50.csv")
    sources = {row["source"] for row in frozen}
    required = {
        "steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py",
        "steps/step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py",
        "steps/step25_sourcing_unification_artifacts/field_carrier_step25.json",
        "steps/step47_common_carrier_door_test_artifacts/step47_schema.json",
    }
    if not required.issubset(sources):
        fail("frozen machinery sources incomplete")
    script = read(ARTIFACT_DIR / "born_area_one_ledger_step50.py")
    if "f39_source\": \"Step44 geometric min-cut area ledger\"" not in script:
        fail("build script does not write geometric min-cut F39 source")
    if "entropy_from_region(state_matrix" in script:
        fail("build script still uses entropy_from_region as an F39 ledger path")


def validate_prose_and_no_overclaim() -> None:
    combined = "\n".join(
        read(ARTIFACT_DIR / name)
        for name in [
            "step50_results_summary.md",
            "nonclaim_boundary_step50.md",
            "born_area_one_ledger_statement_step50.tex",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for needle in [
        "structural-recognition",
        "geometric min-cut",
        "strict finite-D gap",
        "shared composition combiner",
        "GHZ",
        "conditional on the Step47",
        "does not derive",
    ]:
        if needle not in combined:
            fail(f"missing required prose: {needle}")
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern: {pattern}")


def run_prior_self_validators() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    checks = [
        (STEP42, "run_step42.py"),
        (STEP44, "run_step44.py"),
        (STEP47, "run_step47.py"),
    ]
    for cwd, script in checks:
        proc = subprocess.run(
            [sys.executable, script, "--self"],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            timeout=180,
        )
        if proc.returncode != 0:
            sys.stdout.write(proc.stdout)
            sys.stderr.write(proc.stderr)
            fail(f"prior validator failed: {cwd.name}/{script} --self")


def run_chain() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=ARTIFACT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        timeout=180,
    )
    if proc.returncode != 0:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        fail("chain rebuild failed")


def main() -> None:
    if len(sys.argv) != 2 or sys.argv[1] not in {"--self", "--chain"}:
        fail("usage: run_step50.py --self|--chain")
    if sys.argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_ledger()
    validate_seed_invariance()
    validate_combiner_and_control()
    validate_anti_circularity()
    validate_prose_and_no_overclaim()
    run_prior_self_validators()
    print(f"run_step50.py: PASS {sys.argv[1]}")


if __name__ == "__main__":
    main()
