#!/usr/bin/env python3
"""Validate Cluster B Step 8 E021 RG/measure robustness artifacts."""

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
    "e021_rg_measure_step8.py",
    "rg_measure_vacua_step8.csv",
    "nonfactorization_step8.csv",
    "controls_step8.csv",
    "e021_rg_measure_output_step8.json",
    "e021_rg_measure_output_step8.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step8.py",
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
    print(f"run_step8.py: FAIL: {message}", file=sys.stderr)
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
        if path.name == "run_step8.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_schema_output() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    output = json.loads((ARTIFACT_DIR / "e021_rg_measure_output_step8.json").read_text(encoding="utf-8"))
    for name, payload in [("schema", schema), ("output", output)]:
        verdict = payload.get("final_verdict", payload.get("verdict", {}))
        if verdict.get("type") != "E021_rg_measure_robustness_established":
            fail(f"{name} has unexpected verdict type")
        for key in [
            "Lambda_non_descending_from_bare_UV",
            "Lambda_descends_when_selection_included",
            "selection_non_descending_from_bare_UV",
            "RG_control_descends",
            "no_selection_control_descends",
            "selection_relocation",
        ]:
            if verdict.get(key) is not True:
                fail(f"{name} verdict key false: {key}")
        if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
            fail(f"{name} overstates root landing or frame transfer")


def validate_vacua_structure() -> None:
    rows = read_csv(ARTIFACT_DIR / "rg_measure_vacua_step8.csv")
    if len(rows) < 20:
        fail("vacua grid is too small")
    config_ids = sorted({row["config_id"] for row in rows})
    if len(config_ids) < 5:
        fail("too few configurations")
    for config_id in config_ids:
        selected = [row for row in rows if row["config_id"] == config_id and truth(row["selected"])]
        if len(selected) != 1:
            fail(f"config {config_id} must have exactly one selected vacuum")
        if not selected[0]["g_running"]:
            fail(f"config {config_id} has no RG running signature")
    uv_to_selected = {}
    for row in rows:
        if not truth(row["selected"]):
            continue
        uv_key = (row["cutoff"], row["spectrum_code"], row["g_uv"], row["beta0"])
        uv_to_selected.setdefault(uv_key, set()).add(row["selected_phi_star"])
    if not any(len(values) > 1 for values in uv_to_selected.values()):
        fail("no same-bare-UV configurations with different selected phi")


def validate_nonfactorization() -> None:
    rows = {row["test_id"]: row for row in read_csv(ARTIFACT_DIR / "nonfactorization_step8.csv")}
    required = [
        "Lambda_from_bare_UV",
        "Lambda_from_UV_selected_phi",
        "phi_star_from_bare_UV",
        "g_IR_from_bare_UV",
        "no_selection_Lambda_from_bare_UV",
    ]
    for key in required:
        if key not in rows:
            fail(f"missing nonfactorization row: {key}")
    if int(rows["Lambda_from_bare_UV"]["obstruction_count"]) <= 0 or not truth(
        rows["Lambda_from_bare_UV"]["nonfactorizing"]
    ):
        fail("Lambda unexpectedly descends from bare UV")
    if int(rows["Lambda_from_UV_selected_phi"]["obstruction_count"]) != 0 or truth(
        rows["Lambda_from_UV_selected_phi"]["nonfactorizing"]
    ):
        fail("Lambda does not descend after selected phi is included")
    if int(rows["phi_star_from_bare_UV"]["obstruction_count"]) <= 0 or not truth(
        rows["phi_star_from_bare_UV"]["nonfactorizing"]
    ):
        fail("selection no longer carries the non-descending obstruction")
    if int(rows["g_IR_from_bare_UV"]["obstruction_count"]) != 0 or truth(rows["g_IR_from_bare_UV"]["nonfactorizing"]):
        fail("RG-derived g_IR does not descend from bare UV")
    if int(rows["no_selection_Lambda_from_bare_UV"]["obstruction_count"]) != 0 or truth(
        rows["no_selection_Lambda_from_bare_UV"]["nonfactorizing"]
    ):
        fail("no-selection Lambda control does not descend")


def validate_controls() -> None:
    rows = {row["control_id"]: row for row in read_csv(ARTIFACT_DIR / "controls_step8.csv")}
    required = [
        "RG_derived_g_IR_descends",
        "no_selection_Lambda_descends",
        "selection_relocation",
        "realized_Lambda_not_RG_derived_from_bare_UV",
    ]
    for key in required:
        if key not in rows:
            fail(f"missing control: {key}")
        if not truth(rows[key]["passes_guard"]):
            fail(f"control does not pass guard: {key}")
    if int(rows["RG_derived_g_IR_descends"]["obstruction_count"]) != 0:
        fail("RG-derived control has nonzero obstruction")
    if int(rows["no_selection_Lambda_descends"]["obstruction_count"]) != 0:
        fail("no-selection control has nonzero obstruction")
    if int(rows["selection_relocation"]["obstruction_count"]) <= 0:
        fail("selection-relocation obstruction is empty")


def validate_content_paths() -> None:
    rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if not rows:
        fail("content_classification.csv is empty")
    for row in rows:
        if row["grade"] != "finite-toy-diagnostic" and row["output"] != "nonclaim_boundary.md":
            fail(f"unexpected non-finite-toy grade: {row}")
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
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step8_E021_rg_measure_robustness"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_R6_E021_AFTER_STEP8"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP8_SELECTION_RELOCATION"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 8 - E021 RG/Measure Robustness"),
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
        THREAD_DIR / "steps/step6_shared_frame_robustness_artifacts/run_step6.py",
        THREAD_DIR / "steps/step7_e042_earned_continuation_artifacts/run_step7.py",
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
                f"{validator.name} failed during Step 8 chain\n"
                f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
            )


def main() -> None:
    validate_required()
    scan_overclaims()
    validate_schema_output()
    validate_vacua_structure()
    validate_nonfactorization()
    validate_controls()
    validate_content_paths()
    validate_ledgers()
    run_prior_validators()
    print("run_step8.py: PASS")


if __name__ == "__main__":
    main()
