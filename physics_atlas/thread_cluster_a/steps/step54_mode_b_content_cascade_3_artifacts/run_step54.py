#!/usr/bin/env python3
"""Validate Cluster A Step 54 third content-cascade shadow artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
BUILD_SCRIPT = ARTIFACT_DIR / "content_cascade_3_step54.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "run_step38.py",
    STEPS_DIR / "step48_mode_b_content_cascade_artifacts" / "run_step48.py",
    STEPS_DIR / "step49_mode_b_content_cascade_2_artifacts" / "run_step49.py",
]

REQUIRED_FILES = [
    "content_cascade_3_step54.py",
    "content_mass_rank_scores_step54.csv",
    "mass_rank_field_evidence_step54.csv",
    "mass_rank_edges_step54.csv",
    "shadow_distinctness_step54.csv",
    "negative_controls_step54.csv",
    "anti_smuggle_self_check_step54.csv",
    "generated_vs_input_step54.csv",
    "six_gate_audit_step54.csv",
    "step54_schema.json",
    "content_classification_step54.csv",
    "nonclaim_boundary_step54.md",
    "step54_results_summary.md",
    "step54_statement.tex",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step54.py",
]

LOGIC_FORBIDDEN_SNIPPETS = [
    "3 generations",
    "three generations",
    "observed Yukawa",
    "common-refinement-as-QMGR-cosourcing",
    "co-sourcing",
    "stress-energy",
    "field-layer",
    "amplitude(geometry)",
    "psi-as-cosourcing",
]

TARGET_CONTENT_LITERALS = [
    "rank_one_fundxfund:1",
    "rank_one_fundxsinglet:-3",
    "singletxantifund:-4",
    "singletxantifund:2",
    "singletxsinglet:6",
    "class_01",
]

OVERCLAIM_PATTERNS = [
    r"\bderives\s+the\s+SM\s+content\b",
    r"\bselects\s+the\s+standard\s+model\b",
    r"\bderives/predicts\s+a\s+constant\s+or\s+mass\b",
    r"\bselects\s+three\s+generations\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step54.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bool_text(value: str) -> bool:
    return value == "True"


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_build_logic() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    scoring_region = text.split("def build", maxsplit=1)[0]
    for snippet in LOGIC_FORBIDDEN_SNIPPETS:
        if snippet in scoring_region:
            fail(f"build scoring logic contains forbidden snippet: {snippet}")
    for literal in TARGET_CONTENT_LITERALS:
        if literal in scoring_region:
            fail(f"build scoring logic contains target content literal: {literal}")
    if "target_class" in scoring_region or "target_row" in scoring_region:
        fail("shadow scoring logic references target-class metadata")
    if "integer_charge_shadow" in scoring_region:
        fail("Step 54 shadow should be distinct from the Step 48 integer-charge shadow")
    if "full_mass_generation(" not in scoring_region or "massed_components(" not in scoring_region:
        fail("full mass generation rank computation is missing")
    if "texture_shadow(" not in scoring_region:
        fail("Step 54 should reuse Step 49 Yukawa-channel machinery")
    if "mass_rank_deficiency" not in scoring_region:
        fail("rank deficiency computation is missing")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step54.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step54_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 54:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_content_computation":
        fail("unexpected orientation")
    if schema.get("reproduced_content_classes") != 2:
        fail("expected two reproduced content classes")
    if schema.get("shadow_surviving_classes") != 2:
        fail("third shadow should be blind on this carrier")
    if schema.get("surviving_classes") != "class_00|class_01":
        fail("unexpected surviving class set")
    if schema.get("target_class_passes") is not True:
        fail("target class should pass the tested shadow")
    if schema.get("verdict") != "CONTENT_TYPE_LIMIT_3_SHADOWS_BLIND":
        fail("unexpected Step 54 verdict")
    if schema.get("three_blind_shadows") is not True:
        fail("three-shadow type-limit status missing")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_smuggle_self_check_pass") is not True:
        fail("schema gate status did not pass")


def validate_scores() -> None:
    scores = read_csv("content_mass_rank_scores_step54.csv")
    if len(scores) != 2:
        fail(f"expected 2 score rows, got {len(scores)}")
    if sum(1 for row in scores if row["target_class"] == "True") != 1:
        fail("target class should be unique")
    class_ids = {row["content_class_id"] for row in scores}
    if class_ids != {"class_00", "class_01"}:
        fail(f"unexpected content classes: {class_ids}")
    for row in scores:
        if row["full_mass_generation_passes"] != "True":
            fail(f"both residual classes should pass full mass generation: {row}")
        if row["charged_component_count"] != "6" or row["massed_charged_component_count"] != "6":
            fail(f"charged component rank mismatch: {row}")
        if row["mass_rank_deficiency"] != "0":
            fail(f"expected zero rank deficiency: {row}")
        if row["rank_edge_count"] != "3":
            fail(f"expected three rank edges per class: {row}")

    evidence = read_csv("mass_rank_field_evidence_step54.csv")
    if len(evidence) != 10:
        fail(f"expected 10 field evidence rows, got {len(evidence)}")
    field_counts: dict[str, int] = {}
    for row in evidence:
        field_counts[row["content_class_id"]] = field_counts.get(row["content_class_id"], 0) + 1
        if row["rank_full_for_field"] != "True":
            fail(f"field-level rank failure in residual class: {row}")
        if row["missing_charged_component_units"]:
            fail(f"unexpected missing charged components: {row}")
    if sorted(field_counts.values()) != [5, 5]:
        fail(f"expected five fields per class: {field_counts}")

    edges = read_csv("mass_rank_edges_step54.csv")
    if len(edges) != 6:
        fail(f"expected six rank edges, got {len(edges)}")
    edge_counts: dict[str, int] = {}
    for row in edges:
        edge_counts[row["content_class_id"]] = edge_counts.get(row["content_class_id"], 0) + 1
        if row["rank_role"] != "weak_component_to_singlet_pair":
            fail(f"unexpected rank edge role: {row}")
    if sorted(edge_counts.values()) != [3, 3]:
        fail(f"expected three rank edges per class: {edge_counts}")


def validate_distinctness_and_controls() -> None:
    distinct = read_csv("shadow_distinctness_step54.csv")
    if len(distinct) != 2:
        fail("expected two distinctness rows")
    expected = {"step48_integer_charge_shadow", "step49_connectivity_shadow"}
    if {row["comparison"] for row in distinct} != expected:
        fail("missing Step 48/49 distinctness comparisons")
    for row in distinct:
        if row["definitionally_distinct"] != "True":
            fail(f"shadow is not definitionally distinct: {row}")
        if row["extensionally_coincides_on_carrier"] != "True":
            fail(f"unexpected extensional non-coincidence on carrier: {row}")

    negative = read_csv("negative_controls_step54.csv")
    if not any(row["control"] == "rank_deficient_missing_charged_partner_fails" and bool_text(row["passes"]) for row in negative):
        fail("rank-deficient negative control did not pass")
    for row in negative:
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("anti_smuggle_self_check_step54.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle self-check failed: {row}")
    for row in read_csv("six_gate_audit_step54.csv"):
        if row["passes"] != "True":
            fail(f"gate failed: {row}")


def validate_generated_vs_input() -> None:
    rows = read_csv("generated_vs_input_step54.csv")
    statuses = {row["item"]: row["status"] for row in rows}
    if statuses.get("content_classes") != "read_from_step48":
        fail("Step 54 should read content classes from Step 48")
    if statuses.get("scalar_and_yukawa_invariants") != "imported_from_step49_step38":
        fail("Step 54 should import scalar/Yukawa machinery from Steps 49/38")
    if statuses.get("full_mass_generation_rank") != "computed":
        fail("full mass-generation rank must be computed")
    if statuses.get("verdict") != "computed":
        fail("verdict must be computed")


def validate_classification() -> None:
    rows = read_csv("content_classification_step54.csv")
    classified = {row["artifact"] for row in rows}
    expected_classified = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing_classification = sorted(expected_classified - classified)
    if missing_classification:
        fail(f"required artifacts missing from classification: {missing_classification}")
    required_artifacts = {
        f"steps/{ARTIFACT_DIR.name}/content_mass_rank_scores_step54.csv": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/mass_rank_edges_step54.csv": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step54.csv": "organizational",
        f"steps/{ARTIFACT_DIR.name}/step54_results_summary.md": "organizational",
        f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step54.md": "organizational",
        f"steps/{ARTIFACT_DIR.name}/step54_statement.tex": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv": "organizational",
        f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv": "organizational",
        f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv": "organizational",
    }
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        source = THREAD_DIR / row["source"]
        if not source.exists():
            fail(f"classification source missing: {row['source']}")
        if row["source"].startswith("/"):
            fail(f"classification source must be thread-relative: {row['source']}")
        if row["artifact"] in required_artifacts and row["grade"] != required_artifacts[row["artifact"]]:
            fail(f"misgraded artifact: {row}")


def run_dependency_chain() -> None:
    for runner in DEPENDENCY_RUNNERS:
        result = subprocess.run(
            [sys.executable, str(runner), "--self"],
            cwd=STEPS_DIR,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if result.returncode != 0:
            fail(f"{runner.name} failed during dependency chain\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")
    result = subprocess.run(
        [sys.executable, str(BUILD_SCRIPT)],
        cwd=ARTIFACT_DIR,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        fail(f"Step 54 rebuild failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_self() -> None:
    validate_required_files()
    validate_build_logic()
    scan_overclaims()
    validate_schema()
    validate_scores()
    validate_distinctness_and_controls()
    validate_generated_vs_input()
    validate_classification()
    print("run_step54.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step 54 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step 54 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate dependencies, rebuild Step 54, then validate")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
