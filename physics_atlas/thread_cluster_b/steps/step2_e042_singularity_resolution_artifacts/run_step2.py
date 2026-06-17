#!/usr/bin/env python3
"""Validate Cluster B Step 2 artifacts."""

from __future__ import annotations

import csv
import json
import math
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8

REQUIRED_FILES = [
    "e042_singularity_resolution_step2.py",
    "refinement_sequence_step2.csv",
    "p6_ledger_step2.csv",
    "planck_staging_step2.csv",
    "geodesic_continuation_step2.csv",
    "nonfactorization_signature_step2.csv",
    "controls_step2.csv",
    "e042_singularity_resolution_output_step2.json",
    "e042_singularity_resolution_output_step2.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step2.py",
]

FORBIDDEN_PATTERNS = [
    r"proves quantum gravity",
    r"solves quantum gravity",
    r"closes QM-GR unconditionally",
    r"discovers a new physical law",
    r"predicts a new constant",
    r"computes the cosmological constant",
    r"derives the value of lambda",
    r"resolves the singularity",
    r"quantizes gravity",
    r"root_landed[\"']?\s*:\s*true",
    r"frame_transfer_certified[\"']?\s*:\s*true",
]


def fail(message: str) -> None:
    print(f"run_step2.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def truth(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def floats(rows: list[dict[str, str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def strictly_increasing(values: list[float]) -> bool:
    return all(values[i + 1] > values[i] for i in range(len(values) - 1))


def strictly_decreasing(values: list[float]) -> bool:
    return all(values[i + 1] < values[i] for i in range(len(values) - 1))


def validate_required() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def scan_overclaims() -> None:
    chunks = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step2.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_output() -> dict[str, object]:
    output = json.loads((ARTIFACT_DIR / "e042_singularity_resolution_output_step2.json").read_text(encoding="utf-8"))
    verdict = output.get("verdict", {})
    if verdict.get("type") != "E042_boundary_layer_constructed_finite_toy":
        fail("unexpected verdict type")
    for key in [
        "GR_defect_nonstabilizing",
        "L_readout_stabilizing",
        "planck_crossover_computed",
        "finite_continuation_computed",
        "nonfactorization_signature_recomputed",
        "controls_have_teeth",
    ]:
        if not verdict.get(key):
            fail(f"verdict key is false: {key}")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("verdict overstates root landing or frame transfer")
    predicates = output["predicates"]
    if predicates["P6_defect_stabilization"]["R_bad_control_stabilizes"]:
        fail("no-resolution control stabilized in output JSON")
    if predicates["nonfactorization_signature"]["high_locus_obstruction_count"] <= 0:
        fail("high-locus non-factorization is missing")
    if predicates["nonfactorization_signature"]["smooth_obstruction_count"] != 0:
        fail("smooth d4 obstruction is nonzero")
    return output


def validate_refinement_and_p6() -> None:
    rows = read_csv(ARTIFACT_DIR / "refinement_sequence_step2.csv")
    if len(rows) < 6:
        fail("refinement sequence is too short")
    k_values = floats(rows, "K_GR")
    r_values = floats(rows, "R_L")
    bad_values = floats(rows, "R_bad_no_resolution")
    k_increments = floats(rows, "K_increment")[1:]
    r_increments = floats(rows, "R_increment")[1:]
    bad_increments = floats(rows, "R_bad_increment")[1:]
    if not strictly_increasing(k_values):
        fail("GR K does not increase")
    if k_values[-1] <= 100.0 * k_values[0]:
        fail("GR K does not grow enough to witness divergence")
    if not strictly_increasing(k_increments):
        fail("GR K increments do not grow")
    if not strictly_decreasing(r_increments):
        fail("L R increments do not shrink")
    if not math.isfinite(r_values[-1]):
        fail("L R terminal value is not finite")
    if not strictly_increasing(bad_values):
        fail("no-resolution bad readout does not grow")
    if not strictly_increasing(bad_increments):
        fail("no-resolution bad increments do not grow")
    if not any(row["regime"] == "smooth_GR_valid" for row in rows):
        fail("refinement sequence has no smooth regime")
    if not any(row["regime"] == "planck_boundary_or_beyond" for row in rows):
        fail("refinement sequence never reaches Planck boundary")

    p6 = {row["ledger_row"]: row for row in read_csv(ARTIFACT_DIR / "p6_ledger_step2.csv")}
    if truth(p6["GR_K_defect"]["stabilizes"]) or not truth(p6["GR_K_defect"]["diverges"]):
        fail("P6 ledger does not record GR as non-stabilizing divergent")
    if not truth(p6["L_R_resolved_defect"]["stabilizes"]) or truth(p6["L_R_resolved_defect"]["diverges"]):
        fail("P6 ledger does not record L readout as finite stabilizing")
    if truth(p6["control_R_bad_no_resolution"]["stabilizes"]) or not truth(p6["control_R_bad_no_resolution"]["diverges"]):
        fail("P6 ledger no-resolution control did not fail stabilization")


def validate_staging_continuation_nonfact_controls() -> None:
    staging = {row["stage_id"]: row for row in read_csv(ARTIFACT_DIR / "planck_staging_step2.csv")}
    crossover = staging["crossover"]
    if not truth(crossover["computed"]):
        fail("Planck crossover row is not computed")
    if float(crossover["K_at_crossover"]) < 16.0:
        fail("Planck crossover is below K_P")
    if float(crossover["epsilon_star"]) <= 0.0:
        fail("epsilon_star is not positive")

    geodesic = read_csv(ARTIFACT_DIR / "geodesic_continuation_step2.csv")
    if not any(truth(row["GR_terminates_here"]) and not truth(row["GR_defined"]) for row in geodesic):
        fail("GR termination at the locus is not computed")
    post_rows = [row for row in geodesic if row["segment"] == "post_locus"]
    if not post_rows:
        fail("no post-locus continuation rows")
    if not all(truth(row["L_defined"]) and truth(row["L_readout_finite"]) for row in post_rows):
        fail("post-locus L continuation is not finite")

    nonfact = {row["signature_id"]: row for row in read_csv(ARTIFACT_DIR / "nonfactorization_signature_step2.csv")}
    if int(nonfact["E042_d4_boundary_nonfactorization_high_locus"]["obstruction_count"]) <= 0:
        fail("high-locus d4 non-factorization obstruction is empty")
    if not truth(nonfact["E042_d4_boundary_nonfactorization_high_locus"]["nonfactorizing"]):
        fail("high-locus d4 row is not marked nonfactorizing")
    if int(nonfact["smooth_d4_factors_through_d3"]["obstruction_count"]) != 0:
        fail("smooth d4 factor control has obstruction")
    if truth(nonfact["smooth_d4_factors_through_d3"]["nonfactorizing"]):
        fail("smooth d4 factor control is marked nonfactorizing")

    controls = {row["control_id"]: row for row in read_csv(ARTIFACT_DIR / "controls_step2.csv")}
    required = [
        "GR_K_genuinely_diverges",
        "no_resolution_R_bad_fails_stabilization",
        "L_R_resolved_stabilizes",
        "smooth_regime_no_spurious_resolution",
    ]
    for key in required:
        if key not in controls:
            fail(f"missing control row: {key}")
        if not truth(controls[key]["passes"]):
            fail(f"control did not pass: {key}")


def validate_content_paths() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"content row has no source artifacts: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"absolute source path is not allowed: {source}")
            if not source.startswith("steps/"):
                fail(f"source path is not thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_ledgers() -> None:
    checks = [
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step2_E042_boundary_constructed"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_STEP3_E021_VACUUM_BUDGET_BUILD"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP2_NO_RESOLUTION_CONTROL_FAILS"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 2 - E042 Boundary Construction"),
    ]
    for path, needle in checks:
        if not path.exists():
            fail(f"ledger missing: {path}")
        if needle not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {needle}")


def main() -> None:
    validate_required()
    scan_overclaims()
    validate_output()
    validate_refinement_and_p6()
    validate_staging_continuation_nonfact_controls()
    validate_content_paths()
    validate_ledgers()
    print("run_step2.py: PASS")


if __name__ == "__main__":
    main()
