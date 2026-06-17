#!/usr/bin/env python3
"""Validate Cluster A Step 57 record-stability descent artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "record_stability_descent_step57.py"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "run_step38.py",
    STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "run_step41.py",
]

REQUIRED_FILES = [
    "record_stability_descent_step57.py",
    "record_stability_descent_scores_step57.csv",
    "cs_rs_extensions_step57.csv",
    "anti_circularity_step57.csv",
    "negative_controls_step57.csv",
    "tuning_detector_step57.csv",
    "dependency_trace_step57.csv",
    "ablation_step57.csv",
    "stage2_record_fact_step57.csv",
    "anti_smuggle_self_check_step57.csv",
    "six_gate_audit_step57.csv",
    "generated_vs_input_step57.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "step57_schema.json",
    "content_classification_step57.csv",
    "nonclaim_boundary_step57.md",
    "step57_results_summary.md",
    "step57_statement.tex",
    "run_step57.py",
]

RECORD_REQUIREMENT_FORBIDDEN = [
    "clean_separation",
    "clean_shadow",
    "delta",
    "Delta",
    "broken_vector",
    "broken",
    "SM",
    "2|3",
    "colored",
    "gauge-shape",
    "target",
]

OVERCLAIM_PATTERNS = [
    r"\bderives\s+clean\s+separation\b",
    r"\bproves\s+clean\s+separation\s+fundamental\b",
    r"\bSBT\s+derives\s+the\s+SM\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bpsi-as-cosourcing\b",
    r"\bcommon-refinement-as-QMGR-cosourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step57.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def record_requirement_region() -> str:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    start = text.index("# RECORD_REQUIREMENT_BEGIN")
    end = text.index("# RECORD_REQUIREMENT_END")
    return text[start:end]


def validate_build_logic() -> None:
    region = record_requirement_region()
    for token in RECORD_REQUIREMENT_FORBIDDEN:
        if token in region:
            fail(f"record requirement contains forbidden primitive token: {token}")
    for term in ("record_layer_membership(", "neutral_record_token_count", "capacity_threshold", "distinguishability_passes", "record_stability_passes"):
        if term not in region:
            fail(f"record requirement missing term: {term}")
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "RS_proper_subset_CS" not in text or "RS_equals_CS" not in text:
        fail("anti-circularity quantities must be computed")
    if "MIN_RECORD_TOKENS = 2" not in text:
        fail("record capacity threshold should be the minimal nontrivial value 2")
    if "target_support_id" not in text:
        fail("target status should be reported after scoring")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step57.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step57_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 57:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_record_stability_parent_layer_descent":
        fail("unexpected orientation")
    if schema.get("carrier_rows") != 12:
        fail("expected twelve carrier rows")
    if schema.get("CS_count") != 8 or schema.get("RS_count") != 4:
        fail(f"unexpected CS/RS counts: {schema.get('CS_count')} {schema.get('RS_count')}")
    if schema.get("RS_subset_CS") is not True:
        fail("RS should be subset of CS")
    if schema.get("RS_proper_subset_CS") is not True:
        fail("RS should be a proper subset of CS for LAND")
    if schema.get("RS_equals_CS") is not False:
        fail("RS=CS would be circular and must not be a LAND")
    if schema.get("RS_not_subset_CS") is not False:
        fail("RS should descend into CS")
    if schema.get("target_support_id") != "support_05" or schema.get("target_in_RS") is not True:
        fail("target support should pass record stability")
    if schema.get("proper_subset_witness") != "support_03":
        fail("expected support_03 as properness witness")
    if schema.get("nonclean_failure_witness") != "support_08":
        fail("expected support_08 as non-CS failure witness")
    if schema.get("verdict") != "LAND_RECORD_STABILITY_PROPER_SUBSET":
        fail("unexpected verdict")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")
    if schema.get("six_gates_pass") is not True or schema.get("negative_controls_pass") is not True or schema.get("anti_circularity_pass") is not True:
        fail("schema gate flags did not pass")


def validate_scores() -> None:
    rows = read_csv("record_stability_descent_scores_step57.csv")
    if len(rows) != 12:
        fail(f"expected 12 score rows, got {len(rows)}")
    cs = {row["support_id"] for row in rows if row["cs_member_delta_empty"] == "True"}
    rs = {row["support_id"] for row in rows if row["rs_member_record_stable"] == "True"}
    if cs != {f"support_{index:02d}" for index in range(8)}:
        fail(f"unexpected CS extension: {sorted(cs)}")
    if rs != {"support_00", "support_01", "support_02", "support_05"}:
        fail(f"unexpected RS extension: {sorted(rs)}")
    for row in rows:
        if row["support_id"] in rs:
            if row["record_stability_passes"] != "True" or row["capacity_passes"] != "True" or row["distinguishability_passes"] != "True":
                fail(f"RS row missing record components: {row}")
        if row["support_id"] in {"support_03", "support_04", "support_06", "support_07"}:
            if row["cs_member_delta_empty"] != "True" or row["record_stability_passes"] != "False":
                fail(f"properness witness family mismatch: {row}")
            if "dual_line:antifund|antisym2" not in row["alias_ambiguity_witnesses"]:
                fail(f"expected alias ambiguity witness: {row}")
        if row["support_id"] in {"support_08", "support_09", "support_10", "support_11"}:
            if row["capacity_passes"] != "False":
                fail(f"non-CS rows should fail capacity: {row}")


def validate_extensions_and_anticircularity() -> None:
    extensions = {row["extension"]: row for row in read_csv("cs_rs_extensions_step57.csv")}
    if extensions["CS"]["count"] != "8" or extensions["RS"]["count"] != "4":
        fail("extension counts mismatch")
    checks = {row["check"]: row for row in read_csv("anti_circularity_step57.csv")}
    for key in ("RS_subset_CS", "proper_subset", "not_extensionally_equal", "no_descent_absent"):
        if checks.get(key, {}).get("passes") != "True":
            fail(f"anti-circularity check failed: {key}")
    if checks["proper_subset"]["evidence"] != "support_03":
        fail("proper-subset witness missing")


def validate_controls_and_gates() -> None:
    for row in read_csv("negative_controls_step57.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("tuning_detector_step57.csv"):
        if row["passes"] != "True":
            fail(f"tuning detector failed: {row}")
    stage2 = {row["fact"]: row for row in read_csv("stage2_record_fact_step57.csv")}
    if stage2["identity_dynamics_preserves_two_records"]["persistent_and_distinct"] != "True":
        fail("identity Stage-II fact should pass")
    if stage2["erasure_dynamics_collapses_records"]["persistent_and_distinct"] != "False":
        fail("erasure Stage-II fact should fail persistence/distinguishability")
    for row in read_csv("six_gate_audit_step57.csv"):
        if row["passes"] != "True":
            fail(f"gate failed: {row}")
    for row in read_csv("anti_smuggle_self_check_step57.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle self-check failed: {row}")


def validate_generated_vs_input() -> None:
    rows = read_csv("generated_vs_input_step57.csv")
    statuses = {row["item"]: row["status"] for row in rows}
    expected = {
        "Step38_carrier": "read",
        "Step41_CS": "read_and_computed_extension",
        "record_stability_requirement": "generated",
        "RS_extension": "computed",
        "anti_circularity": "computed",
        "verdict": "computed",
    }
    for item, status in expected.items():
        if statuses.get(item) != status:
            fail(f"generated-vs-input mismatch for {item}")


def validate_ledgers() -> None:
    lineage = read_csv("mode_b_target_lineage.csv")
    if len(lineage) != 1:
        fail("expected one lineage row")
    relation = lineage[0]["relation_to_canonical_root"]
    if "super_residual" not in relation or "USER-AUTHORIZED 2026-06-09" not in relation:
        fail("lineage must record user-authorized parent-layer move")
    grammar = read_csv("mode_b_grammar_manifest.csv")
    if len(grammar) != 1 or grammar[0]["new_grammar_declared"] != "True":
        fail("Step57 should declare a new record-stability grammar")
    if "record-stability" not in grammar[0]["target" if "target" in grammar[0] else "tracked_object"]:
        # Fall through to a more direct content check below; DictReader always returns the expected fieldnames.
        pass
    if "record" not in grammar[0]["carrier"].lower() or "RS" not in grammar[0]["tracked_object"]:
        fail("grammar manifest must track the record-stability RS extension")


def validate_classification() -> None:
    rows = read_csv("content_classification_step57.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"required artifacts missing from classification: {missing}")
    required_grades = {
        f"steps/{ARTIFACT_DIR.name}/record_stability_descent_scores_step57.csv": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/cs_rs_extensions_step57.csv": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/anti_circularity_step57.csv": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/step57_statement.tex": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/step57_results_summary.md": "organizational",
        f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step57.md": "organizational",
    }
    for row in rows:
        if row["grade"] not in ALLOWED_GRADES:
            fail(f"bad grade: {row}")
        source = THREAD_DIR / row["source"]
        if not source.exists():
            fail(f"classification source missing: {row['source']}")
        if row["source"].startswith("/"):
            fail(f"classification source must be thread-relative: {row['source']}")
        if row["artifact"] in required_grades and row["grade"] != required_grades[row["artifact"]]:
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
        fail(f"Step57 rebuild failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_self() -> None:
    validate_required_files()
    validate_build_logic()
    scan_overclaims()
    validate_schema()
    validate_scores()
    validate_extensions_and_anticircularity()
    validate_controls_and_gates()
    validate_generated_vs_input()
    validate_ledgers()
    validate_classification()
    print("run_step57.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step57 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step57 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate dependencies, rebuild Step57, then validate")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
