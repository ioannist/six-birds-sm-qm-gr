#!/usr/bin/env python3
"""Validate Cluster B Step 6 shared-frame robustness artifacts."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "shared_frame_robustness_step6.py",
    "readout_battery_step6.csv",
    "enrichment_step6.csv",
    "controls_step6.csv",
    "shared_frame_robustness_output_step6.json",
    "shared_frame_robustness_output_step6.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step6.py",
]

FORBIDDEN_PATTERNS = [
    r"proves quantum gravity",
    r"solves quantum gravity",
    r"closes QM-GR unconditionally",
    r"discovers a new physical law",
    r"predicts a new constant",
    r"computes the cosmological constant",
    r"derives the value of lambda",
    r"solves the cosmological constant problem",
    r"resolves the singularity",
    r"quantizes gravity",
    r"root_landed[\"']?\s*:\s*true",
    r"frame_transfer_certified[\"']?\s*:\s*true",
]


def fail(message: str) -> None:
    print(f"run_step6.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def truth(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def validate_required() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step6.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_schema_output() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "shared_frame_robustness_output_step6.json").read_text(encoding="utf-8"))
    for name, payload in [("schema", schema), ("output", output)]:
        verdict = payload.get("final_verdict", payload.get("verdict", {}))
        if verdict.get("type") != "shared_frame_robustness_established":
            fail(f"{name} has unexpected verdict type")
        for key in [
            "representation_independence_min_obstruction_d4",
            "representation_independence_min_obstruction_d5",
            "genuine_enrichment_min_obstruction_d4",
            "genuine_enrichment_min_obstruction_d5",
        ]:
            if int(verdict.get(key, 0)) <= 0:
                fail(f"{name} lost positive obstruction for {key}")
        for key in [
            "positive_detection_controls_pass",
            "smuggling_detection_controls_pass",
            "genuine_enrichment_controls_pass",
        ]:
            if verdict.get(key) is not True:
                fail(f"{name} verdict key false: {key}")
        if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
            fail(f"{name} overstates root landing or frame transfer")
    return output


def validate_readout_battery() -> None:
    rows = read_csv(ARTIFACT_DIR / "readout_battery_step6.csv")
    if len(rows) < 12:
        fail("readout battery is too small")
    map_classes = {row["map_class"] for row in rows}
    if not {"linear", "nonlinear"}.issubset(map_classes):
        fail("readout battery must include linear and nonlinear maps")
    targets = {row["target"] for row in rows}
    if targets != {"d4_subplanck", "d5_vacuum"}:
        fail(f"unexpected readout targets: {targets}")
    for row in rows:
        if int(row["obstruction_count"]) <= 0:
            fail(f"readout map made {row['target']} descend without enrichment: {row}")
        if not truth(row["non_descending"]):
            fail(f"readout row is not marked non-descending: {row}")
        if row["witness"] == "none":
            fail(f"readout row has no witness: {row}")


def validate_enrichment() -> None:
    rows = read_csv(ARTIFACT_DIR / "enrichment_step6.csv")
    if not rows:
        fail("enrichment_step6.csv is empty")
    genuine = [row for row in rows if row["enrichment_kind"] == "genuine_endpoint_internal"]
    smuggling = [row for row in rows if row["enrichment_kind"] == "smuggling_endpoint_plus_layer_content"]
    if not genuine or not smuggling:
        fail("missing genuine or smuggling enrichment rows")
    for row in genuine:
        if truth(row["uses_layer_content"]) or truth(row["flagged_smuggling"]):
            fail(f"genuine enrichment is marked as smuggling: {row}")
        if int(row["obstruction_count"]) <= 0 or truth(row["makes_definable"]):
            fail(f"genuine enrichment made target definable: {row}")
    target_smug = [
        row
        for row in smuggling
        if truth(row["uses_layer_content"]) and truth(row["flagged_smuggling"]) and truth(row["makes_definable"])
    ]
    if not any(row["target"] == "d4_subplanck" and int(row["obstruction_count"]) == 0 for row in target_smug):
        fail("smuggling enrichment did not make d4 definable while flagged")
    if not any(row["target"] == "d5_vacuum" and int(row["obstruction_count"]) == 0 for row in target_smug):
        fail("smuggling enrichment did not make d5 definable while flagged")


def validate_controls() -> None:
    rows = {row["control_id"]: row for row in read_csv(ARTIFACT_DIR / "controls_step6.csv")}
    required = [
        "positive_detection_d3_from_GR_sigma",
        "positive_detection_d0_times_d2_from_poly_GR_sigma",
        "smuggling_detection_d4_definable_when_added",
        "smuggling_detection_d5_definable_when_added",
        "genuine_enrichment_d4_still_non_descending",
        "genuine_enrichment_d5_still_non_descending",
    ]
    for key in required:
        if key not in rows:
            fail(f"missing control: {key}")
        if not truth(rows[key]["passes_guard"]):
            fail(f"control does not pass guard: {key}")
    for key in ["positive_detection_d3_from_GR_sigma", "positive_detection_d0_times_d2_from_poly_GR_sigma"]:
        if int(rows[key]["obstruction_count"]) != 0:
            fail(f"positive-detection control did not recover descendable target: {key}")
    for key in ["smuggling_detection_d4_definable_when_added", "smuggling_detection_d5_definable_when_added"]:
        if int(rows[key]["obstruction_count"]) != 0:
            fail(f"smuggling detection did not make target definable: {key}")
    for key in ["genuine_enrichment_d4_still_non_descending", "genuine_enrichment_d5_still_non_descending"]:
        if int(rows[key]["obstruction_count"]) <= 0:
            fail(f"genuine enrichment control lost non-descending target: {key}")


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
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_ledgers() -> None:
    checks = [
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step6_shared_frame_robustness"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_R6_FRAME_ROBUSTNESS_AFTER_STEP6"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP6_REPRESENTATION_INDEPENDENCE"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 6 - Shared-Frame Robustness"),
    ]
    for path, needle in checks:
        if not path.exists():
            fail(f"ledger missing: {path}")
        if needle not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {needle}")


def run_prior_validators() -> None:
    validators = [
        THREAD_DIR / "steps/step1_shared_substrate_frame_artifacts/run_step1.py",
        THREAD_DIR / "steps/step2_e042_singularity_resolution_artifacts/run_step2.py",
        THREAD_DIR / "steps/step3_e021_cosmological_constant_artifacts/run_step3.py",
        THREAD_DIR / "steps/step4_consolidated_statement_artifacts/run_step4.py",
        THREAD_DIR / "steps/step5_honest_regrade_artifacts/run_step5.py",
    ]
    for validator in validators:
        result = subprocess.run(
            [sys.executable, str(validator)],
            cwd=validator.parent,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(
                f"{validator.name} failed during Step 6 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def main() -> None:
    validate_required()
    scan_overclaims()
    validate_schema_output()
    validate_readout_battery()
    validate_enrichment()
    validate_controls()
    validate_content_paths()
    validate_ledgers()
    run_prior_validators()
    print("run_step6.py: PASS")


if __name__ == "__main__":
    main()
