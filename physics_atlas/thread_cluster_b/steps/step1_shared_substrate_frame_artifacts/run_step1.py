#!/usr/bin/env python3
"""Validate Cluster B Step 1 artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8

REQUIRED_FILES = [
    "shared_substrate_frame_step1.py",
    "extended_carrier_step1.csv",
    "frame_signatures_step1.csv",
    "shadow_descent_step1.csv",
    "controls_step1.csv",
    "shared_substrate_frame_output_step1.json",
    "shared_substrate_frame_output_step1.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step1.py",
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
    print(f"run_step1.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def truth(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step1.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_required() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_output() -> dict[str, object]:
    output = json.loads((ARTIFACT_DIR / "shared_substrate_frame_output_step1.json").read_text(encoding="utf-8"))
    verdict = output.get("verdict", {})
    if verdict.get("type") != "shared_substrate_frame_established":
        fail("unexpected verdict type")
    for key in [
        "E021_non_descending_readout_of_L",
        "E042_non_descending_readout_of_L",
        "smooth_shadow_descent_holds",
        "controls_have_teeth",
    ]:
        if not verdict.get(key):
            fail(f"verdict key is not true: {key}")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("verdict overstates root landing or frame-transfer certification")
    if output.get("carrier_state_count") != 12:
        fail("extended carrier should have 12 lifted states")
    shadow = output.get("shadow_descent", {})
    if shadow.get("d4_smooth_obstruction_count") != 0:
        fail("d4 is non-descending in the smooth regime")
    if shadow.get("d4_high_obstruction_count", 0) <= 0:
        fail("d4 has no high-curvature obstruction")
    if float(shadow.get("smooth_descent_residual", 1.0)) > TOL:
        fail("smooth GR descent residual is not zero")
    return output


def validate_frame_csvs() -> None:
    frame = read_csv(ARTIFACT_DIR / "frame_signatures_step1.csv")
    if len(frame) != 2:
        fail("frame_signatures_step1.csv must contain E021 and E042 rows")
    by_id = {row["object_id"]: row for row in frame}
    for object_id in ["E042_d4_subplanck", "E021_d5_vacuum"]:
        if object_id not in by_id:
            fail(f"missing frame row: {object_id}")
        row = by_id[object_id]
        if not truth(row["non_descending_in_GR_Sigma_f"]):
            fail(f"{object_id} is not recorded as non-descending in GR Sigma_f")
        if int(row["obstruction_count_GR_Sigma_f"]) <= 0:
            fail(f"{object_id} lacks GR obstruction witnesses")
        if not truth(row["non_descending_in_QM_Sigma_f"]):
            fail(f"{object_id} is not recorded as non-descending in QM Sigma_f")
        if int(row["obstruction_count_QM_Sigma_f"]) <= 0:
            fail(f"{object_id} lacks QM obstruction witnesses")
        if not truth(row["is_L_readout"]):
            fail(f"{object_id} is not recorded as an L readout")
        if row["witness"] == "none":
            fail(f"{object_id} has no witness string")

    shadow = {row["test_id"]: row for row in read_csv(ARTIFACT_DIR / "shadow_descent_step1.csv")}
    smooth = shadow.get("GR_smooth_sigma_from_L_on_smooth_regime")
    d4_smooth = shadow.get("d4_through_d3_on_smooth_regime")
    boundary = shadow.get("singularity_locus_boundary")
    if not smooth or not d4_smooth or not boundary:
        fail("shadow_descent_step1.csv missing required rows")
    if float(smooth["descent_residual"]) > TOL or not truth(smooth["factors"]):
        fail("GR smooth descent row does not factor")
    if int(d4_smooth["obstruction_count"]) != 0 or float(d4_smooth["descent_residual"]) > TOL:
        fail("d4 smooth-regime control fails")
    if truth(boundary["factors"]) or int(boundary["obstruction_count"]) <= 0:
        fail("high-curvature boundary did not tear the smooth d4 descent")

    controls = {row["control_id"]: row for row in read_csv(ARTIFACT_DIR / "controls_step1.csv")}
    if not truth(controls["descending_readout_d3_from_GR_Sigma_f"]["passes"]):
        fail("descending d3 control does not pass")
    if int(controls["descending_readout_d3_from_GR_Sigma_f"]["obstruction_count"]) != 0:
        fail("descending d3 control has obstruction witnesses")
    if not truth(controls["d4_factors_through_d3_on_smooth_regime"]["passes"]):
        fail("d4 smooth-regime factor control does not pass")
    if not truth(controls["d4_nonfactorization_only_at_high_curvature_boundary"]["passes"]):
        fail("d4 high-curvature boundary control does not pass")

    carrier = read_csv(ARTIFACT_DIR / "extended_carrier_step1.csv")
    if len(carrier) != 12:
        fail("extended carrier CSV should have 12 rows")
    if not any(row["regime"] == "vacuum_smooth" for row in carrier):
        fail("extended carrier has no vacuum_smooth regime")
    if not any(row["regime"] == "high_curvature" for row in carrier):
        fail("extended carrier has no high_curvature regime")


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
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step1_shared_substrate_frame"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_STEP2_E042_HIGH_CURVATURE_BUILD"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP1_DESCENDING_CONTROL_FACTORS"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 1 - Shared-Substrate Frame"),
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
    validate_frame_csvs()
    validate_content_paths()
    validate_ledgers()
    print("run_step1.py: PASS")


if __name__ == "__main__":
    main()
