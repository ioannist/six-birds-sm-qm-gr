#!/usr/bin/env python3
"""Validate Step 40 min-cut area/entanglement shadow-price artifacts."""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
BUILD_SCRIPT = ARTIFACT_DIR / "mincut_area_entanglement_shadow_price_step40.py"
TOL = 1e-8

REQUIRED_FILES = [
    "mincut_area_entanglement_shadow_price_step40.py",
    "step40_results_summary.md",
    "step40_schema.json",
    "content_classification_step40.csv",
    "nonclaim_boundary_step40.md",
    "step40_mincut_shadow_price_statement.tex",
    "mincut_shadow_price_sim_step40.csv",
    "bulk_graph_edges_step40.csv",
    "structural_can_fail_step40.csv",
    "anti_tautology_step40.csv",
    "computed_ablation_step40.csv",
    "six_gate_audit_step40.csv",
    "generated_vs_input_step40.csv",
    "anti_hardcode_step40.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step40.py",
]

OVERCLAIM_PATTERNS = [
    r"derives\s+1/4G",
    r"derives\s+(?:a\s+)?(?:constant|mass)",
    r"proves\s+quantum\s+gravity",
    r"solves\s+quantum\s+gravity",
    r"closes\s+E018",
    r"unconditional\s+new[- ]physics",
]


def fail(message: str) -> None:
    print(f"run_step40.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def validate_presence() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required artifacts: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step40_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 40,
        "orientation": "ModeB_E018_min_cut_area_entanglement_shadow_price",
        "verdict": "SHADOW_PRICE_RELATION_DERIVED",
        "area_is_optimization_output": True,
        "entanglement_area_independent_functionals": True,
        "anti_tautology_disagreement_witness": True,
        "rt_recognition_landed": True,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "other_law_landing_legs_attempted": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if float(schema["can_fail_gap"]) <= TOL:
        fail("schema can_fail_gap has no teeth")
    if float(schema["coefficient_refinement_abs_drift"]) > TOL:
        fail("coefficient drift is not stable")
    return schema


def validate_sim_rows() -> None:
    rows = read_csv("mincut_shadow_price_sim_step40.csv")
    holo = [row for row in rows if row["case_kind"] == "holographic"]
    controls = [row for row in rows if row["case_kind"] != "holographic"]
    if len(holo) != 2:
        fail("expected two holographic refinement rows")
    if len(controls) < 2:
        fail("expected at least two non-holographic controls")
    coeffs = []
    for row in holo:
        if not as_bool(row["relation_holds"]):
            fail(f"holographic relation did not hold: {row['case_id']}")
        if abs(float(row["min_cut_area_dual"]) - float(row["max_flow_entanglement_capacity"])) > TOL:
            fail(f"max-flow/min-cut duality gap in {row['case_id']}")
        if abs(float(row["min_cut_area_dual"]) - float(row["entanglement_entropy_S"])) > TOL:
            fail(f"entropy does not saturate min-cut in {row['case_id']}")
        if float(row["optimization_dual_gap"]) > TOL:
            fail(f"optimization dual gap too large in {row['case_id']}")
        coeffs.append(float(row["coefficient_area_over_entropy"]))
    if max(coeffs) - min(coeffs) > TOL:
        fail("holographic coefficient is not refinement-stable")
    for row in controls:
        if as_bool(row["relation_holds"]):
            fail(f"non-holographic control unexpectedly satisfies relation: {row['case_id']}")
        if float(row["abs_area_entropy_gap"]) <= TOL:
            fail(f"non-holographic control lacks disagreement gap: {row['case_id']}")


def validate_can_fail_and_antitautology() -> None:
    can_fail = read_csv("structural_can_fail_step40.csv")
    if len(can_fail) < 2:
        fail("can-fail table is too small")
    for row in can_fail:
        if not as_bool(row["relation_collapses"]):
            fail(f"can-fail row did not collapse: {row['control_id']}")
        if abs(float(row["computed_gap"])) <= TOL:
            fail(f"can-fail gap is zero: {row['control_id']}")

    anti = read_csv("anti_tautology_step40.csv")
    required = {
        "different_functionals",
        "disagreement_witness_extra_entropy",
        "disagreement_witness_decoupled_bulk",
        "holographic_agreement_not_universal",
    }
    seen = {row["gate"]: row for row in anti}
    missing = required - set(seen)
    if missing:
        fail(f"missing anti-tautology gates: {sorted(missing)}")
    for gate in required:
        if not as_bool(seen[gate]["passes"]):
            fail(f"anti-tautology gate failed: {gate}")


def validate_ablation_and_gates() -> None:
    ablations = read_csv("computed_ablation_step40.csv")
    by_id = {row["ablation_id"]: row for row in ablations}
    for required_id in [
        "baseline_holo_refinement_1",
        "remove_min_cut_optimization",
        "swap_to_non_holographic_extra_entropy",
        "decouple_boundary_state_from_bulk",
    ]:
        if required_id not in by_id:
            fail(f"missing ablation row: {required_id}")
    if as_bool(by_id["remove_min_cut_optimization"]["relation_holds"]):
        fail("remove-min-cut ablation should not hold")
    if by_id["remove_min_cut_optimization"]["min_cut_area_dual"] != "undefined":
        fail("remove-min-cut ablation should have undefined area")
    for required_id in ["swap_to_non_holographic_extra_entropy", "decouple_boundary_state_from_bulk"]:
        if as_bool(by_id[required_id]["relation_holds"]):
            fail(f"ablation unexpectedly holds: {required_id}")
        if abs(float(by_id[required_id]["computed_gap"])) <= TOL:
            fail(f"ablation gap missing: {required_id}")

    gates = read_csv("six_gate_audit_step40.csv")
    for row in gates:
        if not as_bool(row["passes"]):
            fail(f"six-gate audit failed: {row['gate']}")
    for row in read_csv("anti_hardcode_step40.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-hardcode failed: {row['check']}")


def validate_content_paths_and_ledgers() -> None:
    rows = read_csv("content_classification_step40.csv")
    if not rows:
        fail("content classification is empty")
    for row in rows:
        sources = [source.strip() for source in row["source_artifacts"].split(";") if source.strip()]
        if not sources:
            fail(f"classification row lacks source path: {row}")
        for source in sources:
            if source.startswith("/"):
                fail(f"source path is absolute: {source}")
            if not source.startswith("steps/"):
                fail(f"source path is not thread-root-relative: {source}")
            if not (THREAD_DIR / source).exists():
                fail(f"source path does not exist: {source}")
    manifest = (ARTIFACT_DIR / "mode_b_grammar_manifest.csv").read_text(encoding="utf-8")
    if "G_E018_MinCutShadowPrice_v1" not in manifest:
        fail("grammar manifest missing G_E018_MinCutShadowPrice_v1")
    if "G_E018_CurrencyConstraint_v1" not in manifest or "tautology" not in manifest:
        fail("grammar manifest does not record Step39 tautology exclusion")


def validate_hardcode_source() -> None:
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ["0" + ".25", "1" + "/4G", "RT" + "_CONSTANT"]:
        if forbidden in source:
            fail(f"forbidden hardcoded selector literal in build source: {forbidden}")
    if "max_flow_min_cut" not in source or "bell_entropy_from_dimensions" not in source:
        fail("build source does not contain distinct area and entropy functionals")


def validate_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in [
            "step40_results_summary.md",
            "nonclaim_boundary_step40.md",
            "step40_mincut_shadow_price_statement.tex",
            "mode_b_target_lineage.csv",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            fail(f"forbidden overclaim phrase: {pattern}")


def run_chain() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=str(ARTIFACT_DIR), check=True)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in {"--self", "--chain"}:
        print("usage: run_step40.py --self|--chain", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_sim_rows()
    validate_can_fail_and_antitautology()
    validate_ablation_and_gates()
    validate_content_paths_and_ledgers()
    validate_hardcode_source()
    validate_overclaims()
    print(f"run_step40.py: PASS {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
