#!/usr/bin/env python3
"""Validate Step 38 artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-9

REQUIRED_FILES = [
    "carrier_independence_step38.py",
    "carrier_independence_step38.csv",
    "nested_control_step38.csv",
    "second_carrier_states_step38.csv",
    "carrier_independence_output_step38.json",
    "carrier_independence_output_step38.txt",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step38.py",
]

FORBIDDEN_PATTERNS = [
    r"proves quantum gravity",
    r"solves quantum gravity",
    r"derives the proton mass",
    r"derives [a-z0-9_ -]*(?:mass|constant)",
    r"closes QM-GR unconditionally",
    r"discovers a new physical law",
    r"predicts a new constant",
    r"quantum gravity is impossible",
    r"QG impossible",
    r"proven impossible",
    r"frame-transfer certified",
    r"root_landed[\"']?\s*:\s*true",
]


def fail(message: str) -> None:
    print(f"run_step38.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def truth(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def scan_overclaims() -> None:
    combined = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step38.py":
            continue
        if path.is_file() and path.suffix in {".py", ".md", ".csv", ".json", ".txt", ".tex"}:
            combined.append(path.read_text(encoding="utf-8"))
    text = "\n".join(combined)
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern found: {pattern}")


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_output_json() -> dict[str, object]:
    output = json.loads((ARTIFACT_DIR / "carrier_independence_output_step38.json").read_text(encoding="utf-8"))
    verdict = output.get("verdict", {})
    if verdict.get("type") != "carrier_independence_mode_grammar_stable_R2_resolved":
        fail("unexpected verdict type")
    if not verdict.get("all_four_stable_on_complete_16"):
        fail("complete-16 did not keep all four decisive verdicts stable")
    if not verdict.get("nested_control_has_teeth"):
        fail("nested control did not register as a live can-fail control")
    if verdict.get("root_landed") or verdict.get("frame_transfer_certified"):
        fail("schema overstates root landing or frame-transfer certification")

    stable = output.get("stable_verdicts", {})
    if not stable.get("complete_16_all_four_stable"):
        fail("stable_verdicts.complete_16_all_four_stable is false")
    if not stable.get("nested_control_flips_no_go"):
        fail("nested control did not flip the no-go")

    complete = output["second_carrier_witnesses"]
    directed = complete["directed"]
    if directed["q_GR_through_q_QM_pair_defect_count"] != 8:
        fail("complete-16 q_GR through q_QM pair defect count is not 8")
    if directed["q_QM_through_q_GR_pair_defect_count"] != 8:
        fail("complete-16 q_QM through q_GR pair defect count is not 8")
    if directed["q_GR_through_q_QM_row_residual"] <= TOL or directed["q_QM_through_q_GR_row_residual"] <= TOL:
        fail("complete-16 directed row-span residuals are not positive")
    if not directed["directed_no_go_fires_by_rowspan"]:
        fail("directed no-go was not recomputed as firing by row-span on complete-16")

    fused = complete["fused"]
    if fused["union_rank"] != 4 or fused["union_dimension"] != 6 or fused["union_extra_coordinate_count"] != 2:
        fail("complete-16 fused no-go witness does not show rank 4, dimension 6, defect 2")
    if fused["union_passes_g_nosmuggle"]:
        fail("union unexpectedly passes G_nosmuggle")

    typed = complete["type"]
    if typed["fired_families"] != ["BridgeMediatedRole"]:
        fail("complete-16 type uniqueness did not select exactly BridgeMediatedRole")
    if typed["coarsening_min_obstruction_count"] <= 0:
        fail("complete-16 coarsening search empties O_s")
    if typed["gate_pass_count"] != 8:
        fail("complete-16 explicit L does not pass 8 gate proxy")

    instance = complete["instance"]
    if instance["L_qm_residual"] > TOL or instance["L_gr_residual"] > TOL:
        fail("complete-16 L does not factor to both endpoints")
    if not instance["all_drop_one_fail"]:
        fail("a drop-one-mode sub-minimal object carried both endpoints")
    if instance["drop_one_min_positive_linear_residual"] <= TOL:
        fail("drop-one-mode failures lack positive linear obstruction")
    if not instance["union_nonadmissible"] or not instance["L_prime_iso"]:
        fail("instance controls failed on complete-16")

    nested = output["nested_control"]
    if nested["directed_no_go_fires"]:
        fail("nested-endpoints control still fires the directed no-go")
    if not nested["vertical_reduction_closes"]:
        fail("nested-endpoints vertical reduction did not close")
    if nested["O_s_count"] != 0:
        fail("nested-endpoints control has nonempty O_s")
    if nested["q_GR_nested_through_q_QM_pair_defect_count"] != 0:
        fail("nested q_GR through q_QM has finite-pair defects")
    if nested["q_QM_through_q_GR_nested_pair_defect_count"] != 0:
        fail("nested q_QM through q_GR has finite-pair defects")
    return output


def validate_csvs() -> None:
    states = read_csv(ARTIFACT_DIR / "second_carrier_states_step38.csv")
    if len(states) != 16:
        fail("second carrier does not have 16 states")
    distinct_states = {tuple(row[key] for key in ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]) for row in states}
    if len(distinct_states) != 16:
        fail("second carrier states are not 16 distinct four-mode values")

    rows = read_csv(ARTIFACT_DIR / "carrier_independence_step38.csv")
    if len(rows) != 8:
        fail("carrier_independence_step38.csv should have two carriers times four lemmas")
    complete_rows = [row for row in rows if row["carrier_id"] == "complete_16_second_carrier"]
    custom_rows = [row for row in rows if row["carrier_id"] == "custom_8_first_reference"]
    if len(complete_rows) != 4 or len(custom_rows) != 4:
        fail("expected four rows per carrier")
    for row in complete_rows:
        if not truth(row["verdict_stable"]):
            fail(f"lemma changed verdict on complete carrier: {row['lemma']}")
    for row in rows:
        if not row["computed_witness"] or not row["mode_grammar_basis"]:
            fail(f"row missing computed witness or mode-grammar basis: {row}")

    nested = read_csv(ARTIFACT_DIR / "nested_control_step38.csv")
    if len(nested) != 1:
        fail("nested_control_step38.csv must have one control row")
    if truth(nested[0]["directed_no_go_fires"]):
        fail("nested CSV records directed_no_go_fires=True")
    if not truth(nested[0]["vertical_reduction_closes"]):
        fail("nested CSV does not record vertical_reduction_closes=True")


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
                fail(f"source path is absolute, not portable: {source}")
            if not source.startswith("steps/"):
                fail(f"source path is not thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source artifact does not exist: {source}")


def validate_ledgers() -> None:
    checks = [
        (
            THREAD_DIR / "mode_b_target_lineage.csv",
            "R_child_E018_after_carrier_independence_R2_resolved",
        ),
        (
            THREAD_DIR / "mode_b_grammar_manifest.csv",
            "G_E018_FRAME_TRANSFER_EXTERNAL_REVIEW_AFTER_CARRIER_INDEPENDENCE",
        ),
        (
            THREAD_DIR / "mode_b_constraint_ledger.csv",
            "C_STEP38_NESTED_CONTROL_FLIPS",
        ),
        (
            THREAD_DIR / "findings_qm_gr.md",
            "Step 38 - Carrier Independence / R2 Resolution",
        ),
    ]
    for path, needle in checks:
        if not path.exists():
            fail(f"ledger missing: {path}")
        if needle not in path.read_text(encoding="utf-8"):
            fail(f"ledger marker missing: {needle}")


def main() -> None:
    validate_required_files()
    scan_overclaims()
    validate_output_json()
    validate_csvs()
    validate_content_paths()
    validate_ledgers()
    print("run_step38.py: PASS")


if __name__ == "__main__":
    main()
