#!/usr/bin/env python3
"""Validate Step 34 instance-uniqueness artifacts."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
TOL = 1e-8

REQUIRED_FILES = [
    "instance_uniqueness_step34.py",
    "instance_uniqueness_maps_step34.json",
    "instance_uniqueness_output_step34.json",
    "instance_uniqueness_output_step34.txt",
    "mediator_candidates_step34.csv",
    "descent_residuals_step34.csv",
    "isomorphism_check_step34.csv",
    "instance_uniqueness_statement_step34.tex",
    "results_summary.md",
    "schema.json",
    "content_classification.csv",
    "nonclaim_boundary.md",
    "run_step34.py",
]

FORBIDDEN_PHRASES = [
    "qg impossible",
    "proven impossible",
    "quantum gravity is impossible",
    "metaphysically impossible",
    "proves quantum gravity",
    "solves quantum gravity",
    "derives the proton mass",
    "derived proton mass",
    "closes qm-gr unconditionally",
    "discovers a new physical law",
    "predicts a new constant",
    "unconditional new-physics claim",
    "shadow-to-source promotion without an audited bridge",
]


def fail(message: str) -> None:
    print(f"run_step34.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bool_cell(value: str) -> bool:
    return str(value).strip().lower() == "true"


def f(value: str) -> float:
    return float(value)


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step34.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def by_candidate(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row["candidate"]: row for row in rows}


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    output = json.loads((ARTIFACT_DIR / "instance_uniqueness_output_step34.json").read_text(encoding="utf-8"))
    if output.get("step") != 34:
        fail("output step is not 34")
    verdict = output.get("verdict", {})
    if verdict.get("type") != "instance_uniqueness_minimal_common_refinement_up_to_equivalence":
        fail("unexpected verdict type")
    if verdict.get("L_unique_minimal") is not True:
        fail("L_unique_minimal must be true")
    if verdict.get("superminimal_admissible_refinements_exist") is not True:
        fail("super-minimal admissible refinement control missing")
    if verdict.get("root_landed") is not False:
        fail("root_landed must remain false")

    schema = json.loads((ARTIFACT_DIR / "schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 34:
        fail("schema step is not 34")
    schema_verdict = schema.get("final_verdict", {})
    if schema_verdict.get("type") != "instance_uniqueness_minimal_common_refinement_up_to_equivalence":
        fail("schema verdict mismatch")
    if schema_verdict.get("superminimal_admissible_refinements_exist") is not True:
        fail("schema must record super-minimal admissible refinements")

    mediator_rows = read_csv(ARTIFACT_DIR / "mediator_candidates_step34.csv")
    descent_rows = read_csv(ARTIFACT_DIR / "descent_residuals_step34.csv")
    mediator = by_candidate(mediator_rows)
    descent = by_candidate(descent_rows)

    required_candidates = {
        "L_join",
        "drop_d0_density",
        "drop_d1_phase",
        "drop_d2_transport",
        "drop_d3_curvature",
        "M_super_5mode",
        "union_direct_sum",
        "L_prime_relabel",
    }
    if set(mediator) != required_candidates:
        fail("mediator table does not contain the required exhaustion candidates")
    if set(descent) != required_candidates:
        fail("descent table does not contain the required exhaustion candidates")

    l_row = mediator["L_join"]
    if not (bool_cell(l_row["both_endpoints_factor"]) and bool_cell(l_row["admissible"]) and bool_cell(l_row["minimal"])):
        fail("L_join must factor both endpoints and be admissible minimal")
    if l_row["relation_to_L"] != "is_join":
        fail("L_join relation_to_L must be is_join")

    for name in ["drop_d0_density", "drop_d1_phase", "drop_d2_transport", "drop_d3_curvature"]:
        row = mediator[name]
        desc = descent[name]
        if row["relation_to_L"] != "sub_minimal_fails":
            fail(f"{name} must be relation sub_minimal_fails")
        if bool_cell(row["both_endpoints_factor"]) or bool_cell(row["admissible"]):
            fail(f"{name} unexpectedly carries both endpoints or is admissible")
        if max(f(desc["qm_linear_residual"]), f(desc["gr_linear_residual"])) <= TOL:
            fail(f"{name} lacks a positive computed linear obstruction")
        if row.get("computed_witness", "") == "":
            fail(f"{name} lacks computed witness")

    m_row = mediator["M_super_5mode"]
    m_desc = descent["M_super_5mode"]
    if m_row["relation_to_L"] != "super_minimal_nonminimal":
        fail("M relation_to_L mismatch")
    if not (bool_cell(m_row["both_endpoints_factor"]) and bool_cell(m_row["admissible"])):
        fail("M must be admissible")
    if bool_cell(m_row["minimal"]):
        fail("M must be non-minimal")
    if f(m_desc["L_from_candidate_residual"]) > TOL:
        fail("L must factor through M with residual 0")
    if f(m_desc["candidate_from_L_residual"]) <= TOL:
        fail("M must not factor through L")
    if bool_cell(m_desc["equivalent_to_L"]):
        fail("M must not be equivalent to L")

    union = mediator["union_direct_sum"]
    union_desc = descent["union_direct_sum"]
    if union["relation_to_L"] != "nonadmissible_union":
        fail("union relation_to_L mismatch")
    if not bool_cell(union["both_endpoints_factor"]):
        fail("union should carry both endpoints before admissibility check")
    if bool_cell(union["admissible"]):
        fail("union must be non-admissible")
    if int(union_desc["dimension"]) != 6 or int(union_desc["rank"]) != 4:
        fail("union rank/dimension recomputation mismatch")
    if int(union_desc["extra_coordinate_count"]) != 2:
        fail("union duplicate-coordinate defect must be 2")

    lprime = mediator["L_prime_relabel"]
    if lprime["relation_to_L"] != "iso_to_L":
        fail("L prime relation_to_L mismatch")
    if not (bool_cell(lprime["both_endpoints_factor"]) and bool_cell(lprime["admissible"]) and bool_cell(lprime["minimal"])):
        fail("L prime must be admissible minimal iso")
    iso_rows = read_csv(ARTIFACT_DIR / "isomorphism_check_step34.csv")
    if len(iso_rows) != 2:
        fail("isomorphism check must have two directions")
    for row in iso_rows:
        if not bool_cell(row["is_iso_half"]):
            fail("isomorphism half does not pass")
        if f(row["residual"]) > TOL:
            fail("isomorphism residual must be zero")
        if not row["permutation_matrix"]:
            fail("isomorphism row lacks permutation matrix")

    claim_rows = read_csv(ARTIFACT_DIR / "content_classification.csv")
    if len(claim_rows) < 8:
        fail("content classification has too few rows")
    for row in claim_rows:
        if not row.get("claim_id") or not row.get("source_artifacts"):
            fail("content classification row missing id or source")
        for source in row["source_artifacts"].split(";"):
            if not (THREAD_DIR / source).exists():
                fail(f"missing cited source artifact: {source}")

    nonclaim = (ARTIFACT_DIR / "nonclaim_boundary.md").read_text(encoding="utf-8")
    for marker in ["unique minimal", "super-minimal", "finite coordinate-lattice", "external review"]:
        if marker not in nonclaim:
            fail(f"nonclaim boundary missing marker {marker!r}")

    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_partb_instance_uniqueness" not in lineage:
        fail("target lineage missing Step 34 residual")
    grammar = (THREAD_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_FRAME_TRANSFER_EXTERNAL_REVIEW_STEP35" not in grammar:
        fail("grammar manifest missing Step 35 external-review obligation")
    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP34_JOIN_COMPUTED",
        "C_STEP34_SUBMINIMAL_FAILS",
        "C_STEP34_SUPERMINIMAL_NONMINIMAL",
        "C_STEP34_UNION_NONADMISSIBLE",
        "C_STEP34_ISO_UP_TO_EQUIVALENCE",
        "C_STEP34_BOUNDED_SCOPE",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 34 — Part B Instance-Uniqueness" not in findings:
        fail("findings missing Step 34 entry")

    print("run_step34.py: PASS")


if __name__ == "__main__":
    main()
