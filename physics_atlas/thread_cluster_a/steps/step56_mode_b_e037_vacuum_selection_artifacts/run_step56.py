#!/usr/bin/env python3
"""Validate Cluster A Step 56 E037 vacuum-selection simulation artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "e037_vacuum_selection_step56.py"
CARD_PATH = THREAD_DIR.parent / "missing_layers" / "cards" / "E037.json"

DEPENDENCY_RUNNERS = [
    STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py",
]

REQUIRED_FILES = [
    "e037_vacuum_selection_step56.py",
    "two_vacuum_landscape_sim_step56.csv",
    "step56_schema.json",
    "content_classification_step56.csv",
    "nonclaim_boundary_step56.md",
    "step56_results_summary.md",
    "step56_statement.tex",
    "run_step56.py",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "generated_vs_input_step56.csv",
    "negative_controls_step56.csv",
    "six_gate_audit_step56.csv",
    "anti_smuggle_self_check_step56.csv",
    "dependency_trace_step56.csv",
    "ablation_step56.csv",
]

OVERCLAIM_PATTERNS = [
    r"\bselects\s+our\s+vacuum\b",
    r"\bnames\s+the\s+measure\b",
    r"\bderives\s+the\s+SM\b",
    r"\bderives/predicts\s+a\s+constant\b",
    r"\bdiverges\s+from\s+the\s+landscape\b",
    r"\bnew_physics_claim[\"']?\s*:\s*true\b",
    r"\broot_landed[\"']?\s*:\s*true\b",
    r"\bframe_transfer_certified[\"']?\s*:\s*true\b",
    r"\bco-sourcing\b",
    r"\bstress-energy\b",
    r"\bfield-layer\b",
    r"\bamplitude\(geometry\)\b",
]

ALLOWED_GRADES = {"theorem-grade", "finite-carrier-diagnostic", "organizational", "remaining-external"}


def fail(message: str) -> None:
    print(f"run_step56.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str) -> float:
    return float(value)


def validate_required_files() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required files: {missing}")


def validate_card() -> None:
    card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    if card.get("id") != "E037":
        fail("wrong card id")
    audit = card.get("audit", {})
    if audit.get("divergence_holds") is not False or audit.get("divergence_is_casting_artifact") is not True:
        fail("E037 firewall convergence flags are not as expected")


def validate_build_logic() -> None:
    text = BUILD_SCRIPT.read_text(encoding="utf-8")
    carrier_region = text.split("def read_card", maxsplit=1)[0]
    forbidden_carrier_literals = ["standard_model", "our vacuum", "SM carrier", "selected_vacuum"]
    for literal in forbidden_carrier_literals:
        if literal in carrier_region:
            fail(f"carrier primitives contain forbidden selector literal: {literal}")
    for term in ("main_route_weights(", "control_route_weights(", "total_variation(", "route_mismatch("):
        if term not in text:
            fail(f"route-mismatch computation missing: {term}")
    if "verdict = \"SELECTION_FORECLOSURE_EXHIBITED\"" not in text:
        fail("verdict branch missing")
    if "RM_nondecaying" not in text:
        fail("RM nondecay status should be computed")


def scan_overclaims() -> None:
    chunks: list[str] = []
    for path in ARTIFACT_DIR.iterdir():
        if path.name == "run_step56.py":
            continue
        if path.is_file() and path.suffix.lower() in {".py", ".md", ".csv", ".json", ".tex", ".txt"}:
            chunks.append(path.read_text(encoding="utf-8"))
    text = "\n".join(chunks)
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim found: {pattern}")


def validate_schema() -> None:
    schema = json.loads((ARTIFACT_DIR / "step56_schema.json").read_text(encoding="utf-8"))
    if schema.get("step") != 56:
        fail("schema step mismatch")
    if schema.get("orientation") != "ATTEMPT_finite_carrier_simulation":
        fail("unexpected orientation")
    if schema.get("active_residual") != "E037 vacuum-selection foreclosure":
        fail("active residual mismatch")
    if schema.get("card_id") != "E037" or schema.get("card_foreclosure_status") != "E3_foreclosed":
        fail("card status mismatch")
    if schema.get("card_convergent_with_standard_landscape") is not True:
        fail("convergent-with-landscape flag missing")
    if schema.get("divergence_holds") is not False or schema.get("divergence_is_casting_artifact") is not True:
        fail("firewall flags missing")
    xi = schema.get("per_vacuum_xi_rel", {})
    for vacuum in ("v_alpha", "v_beta"):
        if xi.get(vacuum, {}).get("R1_coarse") != 0.125 or xi.get(vacuum, {}).get("R2_fine") != 0.0:
            fail(f"unexpected xi_rel for {vacuum}: {xi.get(vacuum)}")
    rm = schema.get("RM_by_refinement", {})
    if rm.get("R1_coarse") != 0.25 or rm.get("R2_fine") != 0.25:
        fail(f"unexpected RM values: {rm}")
    if schema.get("RM_decay_ratio") != 1.0 or schema.get("RM_nondecaying") is not True:
        fail("RM should be nondecaying")
    control = schema.get("negative_control_RM_by_refinement", {})
    if not (control.get("R2_fine", 1.0) < control.get("R1_coarse", 0.0)):
        fail("negative-control RM should decay")
    if schema.get("negative_control_decays") is not True:
        fail("negative control decay flag missing")
    if schema.get("per_vacuum_descent_clean_on_toy") is not True:
        fail("per-vacuum descent should be clean on the toy")
    if schema.get("verdict") != "SELECTION_FORECLOSURE_EXHIBITED":
        fail("unexpected verdict")
    if schema.get("new_physics_claim") or schema.get("root_landed") or schema.get("frame_transfer_certified"):
        fail("schema overstates status")


def validate_sim_table() -> None:
    rows = read_csv("two_vacuum_landscape_sim_step56.csv")
    if len(rows) != 8:
        fail(f"expected 8 simulation rows, got {len(rows)}")
    scenarios = {row["scenario"] for row in rows}
    if scenarios != {"main_foreclosure_toy", "stabilizing_selector_control"}:
        fail(f"unexpected scenarios: {scenarios}")
    for scenario in scenarios:
        subset = [row for row in rows if row["scenario"] == scenario]
        if len(subset) != 4:
            fail(f"expected 4 rows for {scenario}, got {len(subset)}")
        if {row["vacuum_id"] for row in subset} != {"v_alpha", "v_beta"}:
            fail(f"unexpected vacua for {scenario}")
        if {row["refinement_level"] for row in subset} != {"R1_coarse", "R2_fine"}:
            fail(f"unexpected refinements for {scenario}")
    main = [row for row in rows if row["scenario"] == "main_foreclosure_toy"]
    for row in main:
        expected_xi = 0.125 if row["refinement_level"] == "R1_coarse" else 0.0
        if as_float(row["xi_rel_float"]) != expected_xi:
            fail(f"xi mismatch: {row}")
        if as_float(row["RM_float"]) != 0.25:
            fail(f"main RM should remain fixed at 0.25: {row}")
    control = [row for row in rows if row["scenario"] == "stabilizing_selector_control"]
    coarse_rm = {as_float(row["RM_float"]) for row in control if row["refinement_level"] == "R1_coarse"}
    fine_rm = {as_float(row["RM_float"]) for row in control if row["refinement_level"] == "R2_fine"}
    if len(coarse_rm) != 1 or len(fine_rm) != 1:
        fail("control RM should be level-wise constant across vacua")
    if not next(iter(fine_rm)) < next(iter(coarse_rm)):
        fail("control RM should decay")


def validate_controls_and_gates() -> None:
    for row in read_csv("negative_controls_step56.csv"):
        if row["passes"] != "True":
            fail(f"negative control failed: {row}")
    for row in read_csv("anti_smuggle_self_check_step56.csv"):
        if row["passes"] != "True":
            fail(f"anti-smuggle self-check failed: {row}")
    gates = read_csv("six_gate_audit_step56.csv")
    if len(gates) < 6:
        fail("expected six gate rows")
    for row in gates:
        if row["passes"] != "True":
            fail(f"gate failed: {row}")
    ablations = read_csv("ablation_step56.csv")
    if not any(row["ablation"] == "remove_route_measure_mismatch" and row["load_bearing"] == "True" for row in ablations):
        fail("route-measure ablation should be load-bearing")
    deps = read_csv("dependency_trace_step56.csv")
    if not any(row["axiom"] == "route_measure_mismatch" for row in deps):
        fail("dependency trace should include route_measure_mismatch")


def validate_generated_vs_input() -> None:
    rows = read_csv("generated_vs_input_step56.csv")
    statuses = {row["item"]: row["status"] for row in rows}
    expected = {
        "E037_card": "read",
        "two_vacuum_carrier": "declared_toy_input",
        "per_vacuum_descent": "computed_on_toy",
        "cross_vacuum_RM": "computed",
        "stabilizing_selector_control": "computed_negative_control",
        "Step3_p6_decaying_degeneracy_audit": "cited_and_chain_validated",
        "verdict": "computed",
    }
    for item, status in expected.items():
        if statuses.get(item) != status:
            fail(f"generated-vs-input mismatch for {item}")


def validate_ledgers() -> None:
    lineage = read_csv("mode_b_target_lineage.csv")
    if len(lineage) != 1:
        fail("expected one lineage row")
    row = lineage[0]
    if row["target"] != "E037-vacuum-selection-foreclosure":
        fail("lineage target mismatch")
    if "super_residual" not in row["relation_to_canonical_root"] or "USER-AUTHORIZED 2026-06-09" not in row["relation_to_canonical_root"]:
        fail("lineage must record user-authorized super-residual relation")
    grammar = read_csv("mode_b_grammar_manifest.csv")
    if len(grammar) != 1 or grammar[0]["new_grammar_declared"] != "True":
        fail("Step56 should declare a new two-vacuum landscape grammar")
    if "cross-vacuum" not in grammar[0]["tracked_object"]:
        fail("grammar must track cross-vacuum route-mismatch")


def validate_classification() -> None:
    rows = read_csv("content_classification_step56.csv")
    classified = {row["artifact"] for row in rows}
    expected = {f"steps/{ARTIFACT_DIR.name}/{name}" for name in REQUIRED_FILES}
    missing = sorted(expected - classified)
    if missing:
        fail(f"required artifacts missing from classification: {missing}")
    required_grades = {
        f"steps/{ARTIFACT_DIR.name}/two_vacuum_landscape_sim_step56.csv": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/step56_statement.tex": "finite-carrier-diagnostic",
        f"steps/{ARTIFACT_DIR.name}/step56_results_summary.md": "organizational",
        f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step56.md": "organizational",
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
        fail(f"Step56 rebuild failed\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}")


def validate_self() -> None:
    validate_required_files()
    validate_card()
    validate_build_logic()
    scan_overclaims()
    validate_schema()
    validate_sim_table()
    validate_controls_and_gates()
    validate_generated_vs_input()
    validate_ledgers()
    validate_classification()
    print("run_step56.py: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate Step56 artifacts")
    parser.add_argument("--self", action="store_true", help="validate only Step56 artifacts")
    parser.add_argument("--chain", action="store_true", help="validate Step3, rebuild Step56, then validate")
    args = parser.parse_args()
    if args.chain:
        run_dependency_chain()
    validate_self()


if __name__ == "__main__":
    main()
