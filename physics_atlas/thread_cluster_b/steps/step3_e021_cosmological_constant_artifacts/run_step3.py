#!/usr/bin/env python3
"""Validate Cluster B Step 3 artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-10

REQUIRED_FILES = [
    "e021_cosmological_constant_step3.py",
    "vacuum_currency_step3.csv",
    "uv_ir_ledger_step3.csv",
    "vacuum_selection_step3.csv",
    "nonfactorization_step3.csv",
    "controls_step3.csv",
    "e021_cosmological_constant_output_step3.json",
    "e021_cosmological_constant_output_step3.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step3.py",
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
    print(f"run_step3.py: FAIL: {message}", file=sys.stderr)
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
        if path.name == "run_step3.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_output() -> dict[str, object]:
    output = json.loads((ARTIFACT_DIR / "e021_cosmological_constant_output_step3.json").read_text(encoding="utf-8"))
    verdict = output.get("verdict", {})
    if verdict.get("type") != "E021_audited_vacuum_readout_constructed_finite_toy":
        fail("unexpected verdict type")
    for key in [
        "firm_part_selected_run_readout",
        "modeled_p6_ledger_illustrative",
        "P5_currency_built",
        "P6_ledger_booked",
        "P2_selection_built",
        "nonfactorization_signature_computed",
        "controls_have_teeth",
    ]:
        if not verdict.get(key):
            fail(f"verdict key is false: {key}")
    if verdict.get("firm_part_missing_audit_ledger") is not False:
        fail("ledger is still marked as a firm missing-audit result")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("verdict overstates root landing or frame transfer")
    if abs(float(output["toy_mismatch_ratio"]) - 1.0e12) > 1.0:
        fail("toy mismatch ratio changed unexpectedly")
    if output["predicates"]["P6_uv_ir_ledger"]["mismatch_ratio_modeled_toy"] is not True:
        fail("mismatch ratio is not marked as modeled toy")
    if output["predicates"]["nonfactorization"]["UV_to_Lambda_obstruction_count"] <= 0:
        fail("UV-to-Lambda non-factorization is empty")
    return output


def validate_schema_regrade() -> None:
    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    verdict = schema.get("final_verdict", {})
    if verdict.get("firm_part_selected_run_readout") is not True:
        fail("schema lost the firm selected/run readout")
    if verdict.get("firm_part_missing_audit_ledger") is not False:
        fail("schema still marks the missing audit ledger as firm")
    if verdict.get("modeled_p6_ledger_illustrative") is not True:
        fail("schema does not mark the P6 ledger as modeled/illustrative")

    summary = (ARTIFACT_DIR / "results_summary.md").read_text(encoding="utf-8")
    required = [
        "Firm part: selected/run readout on the toy",
        "non-factorization obstruction `4`",
        "descending-control contrast (obstruction `0`)",
        "MODELED/illustrative P6 bookkeeping",
        "not a firm audit computed from a coarse map, RG flow, or package dynamics",
    ]
    for snippet in required:
        if snippet not in summary:
            fail(f"Step 3 regrade wording missing from results_summary.md: {snippet}")


def validate_currency_ledger_selection() -> None:
    currency = read_csv(ARTIFACT_DIR / "vacuum_currency_step3.csv")
    selected = next((row for row in currency if row["currency_id"] == "P5_L_vacuum_currency"), None)
    if selected is None:
        fail("missing P5_L_vacuum_currency row")
    if not truth(selected["audited_in_L"]):
        fail("P5 vacuum currency is not audited in L")
    if truth(selected["is_free_additive_constant"]):
        fail("P5 vacuum currency is marked as a free additive constant")
    if selected["GR_status"] != "input_parameter_untracked_by_GR":
        fail("GR status for selected vacuum row is unexpected")

    ledger = read_csv(ARTIFACT_DIR / "uv_ir_ledger_step3.csv")
    uv = next(row for row in ledger if row["ledger_id"] == "uv_budget")
    unaudited = next(row for row in ledger if row["ledger_id"] == "unaudited_cancellation")
    if float(uv["mismatch_ratio"]) < 1.0e6:
        fail("toy mismatch ratio is not large")
    if uv["ratio_status"] != "toy_modeled_not_real_120":
        fail("UV row does not mark ratio as toy")
    if truth(unaudited["tracked"]):
        fail("unaudited cancellation row is tracked")
    if not truth(unaudited["unaudited_cancellation"]):
        fail("unaudited cancellation row is not marked")
    booked = [row for row in ledger if row["ledger_id"].startswith("booked_stage_")]
    remaining = [float(row["remaining_log_mismatch"]) for row in booked]
    if remaining != sorted(remaining, reverse=True):
        fail("booked remaining mismatch is not monotone decreasing")
    if remaining[0] <= remaining[-1] or remaining[-1] != 0.0:
        fail("booked ledger is vacuous or does not reach zero")
    if not all(truth(row["tracked"]) for row in booked):
        fail("booked rows are not tracked")

    selection = read_csv(ARTIFACT_DIR / "vacuum_selection_step3.csv")
    if len(selection) < 5:
        fail("vacuum ensemble is too small")
    selected_rows = [row for row in selection if truth(row["selected"])]
    if len(selected_rows) != 1:
        fail("vacuum ensemble should have exactly one selected row")
    min_score = min(float(row["selection_score"]) for row in selection)
    if abs(float(selected_rows[0]["selection_score"]) - min_score) > TOL:
        fail("selected row is not the minimum selection score")


def validate_nonfactor_controls() -> None:
    nonfact = {row["signature_id"]: row for row in read_csv(ARTIFACT_DIR / "nonfactorization_step3.csv")}
    uv_lambda = nonfact["UV_Sigma_to_selected_Lambda"]
    step1 = nonfact["Step1_GR_Sigma_to_d5_vacuum"]
    coupling = nonfact["descending_control_UV_coupling"]
    if int(uv_lambda["obstruction_count"]) <= 0 or not truth(uv_lambda["nonfactorizing"]):
        fail("UV-to-Lambda row does not non-factorize")
    if int(step1["obstruction_count"]) <= 0 or not truth(step1["nonfactorizing"]):
        fail("Step 1 GR-to-d5 row is not preserved")
    if int(coupling["obstruction_count"]) != 0 or truth(coupling["nonfactorizing"]):
        fail("descending UV coupling control does not factor")

    controls = {row["control_id"]: row for row in read_csv(ARTIFACT_DIR / "controls_step3.csv")}
    required = [
        "derivation_control_clean_UV_to_Lambda_fails",
        "descending_control_UV_coupling_factors",
        "booked_ledger_monotone_nonvacuous",
        "mismatch_ratio_marked_toy",
    ]
    for key in required:
        if key not in controls:
            fail(f"missing control: {key}")
        if not truth(controls[key]["passes_guard"]):
            fail(f"control does not pass guard: {key}")
    if int(controls["derivation_control_clean_UV_to_Lambda_fails"]["obstruction_count"]) <= 0:
        fail("derivation control has no obstruction")
    if truth(controls["derivation_control_clean_UV_to_Lambda_fails"]["unaudited_counterterm_tracked"]):
        fail("derivation control's unaudited counterterm is tracked")
    if int(controls["descending_control_UV_coupling_factors"]["obstruction_count"]) != 0:
        fail("descending control obstruction count is nonzero")


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
        (THREAD_DIR / "mode_b_target_lineage.csv", "R_cluster_b_after_step3_E021_vacuum_constructed"),
        (THREAD_DIR / "mode_b_grammar_manifest.csv", "G_CLUSTER_B_CONSOLIDATE_E021_E042_AFTER_STEP3"),
        (THREAD_DIR / "mode_b_constraint_ledger.csv", "C_CLUSTER_B_STEP3_DERIVATION_CONTROL_FAILS"),
        (THREAD_DIR / "findings_cluster_b.md", "Step 3 - E021 Vacuum Readout Construction"),
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
    validate_schema_regrade()
    validate_currency_ledger_selection()
    validate_nonfactor_controls()
    validate_content_paths()
    validate_ledgers()
    print("run_step3.py: PASS")


if __name__ == "__main__":
    main()
