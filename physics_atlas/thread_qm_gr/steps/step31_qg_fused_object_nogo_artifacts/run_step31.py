#!/usr/bin/env python3
"""Validate Step 31 fused-object no-go artifacts."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

REQUIRED_FILES = [
    "fused_object_nogo_step31.py",
    "union_g_nosmuggle_step31.csv",
    "shared_audit_overlap_step31.csv",
    "directed_route_citation_step31.csv",
    "fused_object_carrier_step31.json",
    "fused_object_nogo_output_step31.json",
    "fused_object_nogo_output_step31.txt",
    "lemma2_fused_object_statement_step31.tex",
    "step31_results_summary.md",
    "step31_schema.json",
    "content_classification_step31.csv",
    "nonclaim_boundary_step31.md",
    "run_step31.py",
]

FORBIDDEN_PHRASES = [
    "qg impossible",
    "proven impossible",
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
    print(f"run_step31.py: FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def scan_forbidden() -> None:
    for path in ARTIFACT_DIR.iterdir():
        if (
            path.is_file()
            and path.name != "run_step31.py"
            and path.suffix.lower() in {".md", ".tex", ".json", ".csv", ".txt", ".py"}
        ):
            text = path.read_text(encoding="utf-8").lower()
            for phrase in FORBIDDEN_PHRASES:
                if phrase in text:
                    fail(f"forbidden phrase {phrase!r} found in {path.name}")


def main() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")

    scan_forbidden()

    schema = json.loads((ARTIFACT_DIR / "step31_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 31:
        fail("schema step is not 31")
    verdict = schema.get("final_verdict", {})
    if verdict.get("type") != "lemma2_fused_object_blocked_in_bounded_grammar":
        fail("unexpected Step 31 verdict")
    if verdict.get("root_landed") is not False:
        fail("schema must keep root_landed false")
    if verdict.get("bounded_grammar_scope") is not True:
        fail("bounded grammar scope missing")

    output = json.loads((ARTIFACT_DIR / "fused_object_nogo_output_step31.json").read_text(encoding="utf-8"))
    out_verdict = output.get("verdict", {})
    if out_verdict.get("lemma_verdict") != "lemma2_fused_object_blocked_in_bounded_grammar":
        fail("output verdict mismatch")
    if out_verdict.get("union_route_passes") is not False:
        fail("union route unexpectedly passes")
    if out_verdict.get("shared_audit_route_passes") is not False:
        fail("shared-audit route unexpectedly passes")
    if out_verdict.get("directed_route_passes") is not False:
        fail("directed route unexpectedly passes")
    if out_verdict.get("nonduplicating_refinement_control_passes") is not True:
        fail("nonduplicating refinement control fails")
    if out_verdict.get("agreeing_audit_control_passes") is not True:
        fail("agreeing audit control fails")

    union_rows = {row["case"]: row for row in read_csv(ARTIFACT_DIR / "union_g_nosmuggle_step31.csv")}
    union = union_rows["union_direct_sum"]
    control = union_rows["nonduplicating_refinement_control"]
    if union["G_nosmuggle_pass"] != "False":
        fail("union G_nosmuggle row passes")
    if int(union["extra_coordinate_count"]) <= 0:
        fail("union extra coordinate count is not positive")
    if int(union["row_rank"]) >= int(union["target_dimension"]):
        fail("union is not rank deficient")
    if control["G_nosmuggle_pass"] != "True":
        fail("nonduplicating refinement control does not pass")
    if int(control["extra_coordinate_count"]) != 0:
        fail("nonduplicating control has extra coordinates")

    audit_rows = read_csv(ARTIFACT_DIR / "shared_audit_overlap_step31.csv")
    audit = {
        (row["case"], row["mode"]): row
        for row in audit_rows
    }
    joint = audit[("derived_physical_audits", "joint_density_transport")]
    density = audit[("derived_physical_audits", "density_d0")]
    transport = audit[("derived_physical_audits", "transport_d2")]
    agree = audit[("agreeing_audit_control", "joint_density_transport")]
    if float(joint["equal_residual"]) <= 1e-2:
        fail("derived shared-audit joint residual too small")
    if float(density["proportional_residual"]) <= 1e-2:
        fail("density proportional residual too small")
    if float(transport["proportional_residual"]) <= 1e-2:
        fail("transport proportional residual too small")
    if agree["shared_audit_exists"] != "True" or float(agree["equal_residual"]) != 0.0:
        fail("agreeing-audit control does not pass exactly")

    directed = read_csv(ARTIFACT_DIR / "directed_route_citation_step31.csv")[0]
    if directed["lemma_verdict"] != "lemma1_directed_reduction_blocked_in_bounded_grammar":
        fail("directed route does not cite Step 30 Lemma 1")
    if directed["directed_route_blocked"] != "True":
        fail("directed route is not marked blocked")
    if float(directed["route_mismatch_normalized"]) <= 1e-2:
        fail("directed route mismatch from Step 30 too small")

    script_text = (ARTIFACT_DIR / "fused_object_nogo_step31.py").read_text(encoding="utf-8")
    for pattern in [
        r"union_gate_diagnostic",
        r"shared_audit_diagnostic",
        r"directed_route_citation",
        r"column_duplicate_pairs",
    ]:
        if not re.search(pattern, script_text):
            fail(f"script missing computation pattern {pattern}")

    ledger = (THREAD_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    for marker in [
        "C_STEP31_UNION_ROUTE_COMPUTED",
        "C_STEP31_SHARED_AUDIT_ROUTE_COMPUTED",
        "C_STEP31_FUSION_CONTROL_PASSES",
    ]:
        if marker not in ledger:
            fail(f"constraint ledger missing {marker}")
    lineage = (THREAD_DIR / "mode_b_target_lineage.csv").read_text(encoding="utf-8")
    if "R_child_E018_after_fused_object_nogo_lemma2" not in lineage:
        fail("target lineage missing Step 31 residual")
    findings = (THREAD_DIR / "findings_qm_gr.md").read_text(encoding="utf-8")
    if "Step 31 — Fused Object No-Go Lemma 2" not in findings:
        fail("findings_qm_gr.md missing Step 31 entry")

    print("run_step31.py: PASS")


if __name__ == "__main__":
    main()
