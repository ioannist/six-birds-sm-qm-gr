#!/usr/bin/env python3
"""Validate Step 41 tensor-network RT-bound artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
BUILD_SCRIPT = ARTIFACT_DIR / "tensor_network_rt_bound_step41.py"
TOL = 1e-8

REQUIRED_FILES = [
    "tensor_network_rt_bound_step41.py",
    "step41_results_summary.md",
    "step41_schema.json",
    "content_classification_step41.csv",
    "nonclaim_boundary_step41.md",
    "step41_rt_bound_statement.tex",
    "tensor_network_rt_bound_sim_step41.csv",
    "tensor_network_tensors_step41.json",
    "contracted_boundary_state_step41.csv",
    "tensor_network_graph_edges_step41.csv",
    "ablation_step41.csv",
    "anti_circularity_step41.csv",
    "six_gate_audit_step41.csv",
    "generated_vs_input_step41.csv",
    "anti_hardcode_step41.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step41.py",
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
    print(f"run_step41.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def load_builder():
    spec = importlib.util.spec_from_file_location("step41_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    sys.modules["step41_builder"] = module
    spec.loader.exec_module(module)
    return module


def validate_presence() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required artifacts: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step41_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 41,
        "orientation": "ModeB_E018_tensor_network_RT_bound",
        "verdict": "RT_BOUND_SATURATED_STRUCTURALLY",
        "entropy_computed_from_contracted_state": True,
        "bound_holds_all_tested": True,
        "strict_gap_exists": True,
        "root_landed": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "other_law_landing_legs_attempted": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if float(schema["strict_gap_witness_value"]) <= 1e-6:
        fail("strict gap witness is too small")
    if not schema.get("min_cut_nontrivial_witness"):
        fail("schema lacks nontrivial min-cut witness")
    if abs(float(schema["saturation_ratio_refinement_1"]) - 1.0) > TOL:
        fail("refinement 1 does not saturate")
    if abs(float(schema["saturation_ratio_refinement_2"]) - 1.0) > TOL:
        fail("refinement 2 does not saturate")
    return schema


def validate_sim_rows_against_builder() -> None:
    rows = read_csv("tensor_network_rt_bound_sim_step41.csv")
    if len(rows) < 4:
        fail("sim artifact must include holographic and control rows")
    if not all(as_bool(row["state_from_contraction"]) for row in rows):
        fail("some sim rows are not marked as contraction-derived")
    if not all(as_bool(row["bound_holds"]) for row in rows):
        fail("S<=min-cut bound fails in a tested row")
    if not any(as_bool(row["strict_gap"]) and float(row["area_minus_entropy_gap"]) > 1e-6 for row in rows):
        fail("no strict-gap row with gap > 1e-6")
    if all(as_bool(row["saturates"]) for row in rows):
        fail("all rows saturate; identity/circularity signature")
    holo = [row for row in rows if row["case_kind"] == "holographic_saturating"]
    if len(holo) != 2:
        fail("expected two holographic refinements")
    for row in holo:
        if not as_bool(row["saturates"]):
            fail(f"holographic row does not saturate: {row['case_id']}")
        if abs(float(row["saturation_ratio_S_over_area"]) - 1.0) > TOL:
            fail(f"holographic row ratio not one: {row['case_id']}")
    nontrivial = [row for row in rows if as_bool(row["min_cut_nontrivial"])]
    if not nontrivial:
        fail("no nontrivial min-cut witness")
    for row in nontrivial:
        if int(row["min_cut_edge_count"]) >= int(row["region_A_leg_count"]):
            fail(f"min-cut witness is just boundary-leg count: {row['case_id']}")
        if "source" in row["min_cut_edges"] or "sink" in row["min_cut_edges"]:
            fail(f"min-cut witness cuts terminal edges: {row['case_id']}")

    builder = load_builder()
    recomputed = builder.build()["sim_rows"]
    keyed = {row["case_id"]: row for row in rows}
    for row in recomputed:
        case_id = row["case_id"]
        if case_id not in keyed:
            fail(f"missing recomputed case in CSV: {case_id}")
        csv_row = keyed[case_id]
        for key in ["entropy_S_A", "min_cut_area", "area_minus_entropy_gap"]:
            if abs(float(row[key]) - float(csv_row[key])) > TOL:
                fail(f"CSV does not match recomputed {key} for {case_id}")


def validate_ablation_and_gates() -> None:
    ablations = read_csv("ablation_step41.csv")
    by_id = {row["ablation_id"]: row for row in ablations}
    for required in [
        "baseline_holo_D3",
        "remove_contraction_product_state",
        "use_degenerate_weighted_tensor",
        "shrink_bond_dimension",
    ]:
        if required not in by_id:
            fail(f"missing ablation row {required}")
    for required in ["remove_contraction_product_state", "use_degenerate_weighted_tensor"]:
        row = by_id[required]
        if as_bool(row["saturates"]) or float(row["area_minus_entropy_gap"]) <= 1e-6:
            fail(f"strict-gap ablation failed: {required}")
    if not as_bool(by_id["shrink_bond_dimension"]["saturates"]):
        fail("shrink-bond-dimension ablation should produce changed saturation, not failure")

    anti = read_csv("anti_circularity_step41.csv")
    required_anti = {
        "entropy_from_contracted_state",
        "strict_gap_exists",
        "holographic_saturation_exists",
        "min_cut_nontrivial",
        "not_identity_all_rows",
    }
    seen = {row["gate"]: row for row in anti}
    missing = required_anti - set(seen)
    if missing:
        fail(f"missing anti-circularity gates: {sorted(missing)}")
    for gate in required_anti:
        if not as_bool(seen[gate]["passes"]):
            fail(f"anti-circularity gate failed: {gate}")
    for row in read_csv("six_gate_audit_step41.csv"):
        if not as_bool(row["passes"]):
            fail(f"six-gate audit failed: {row['gate']}")
    for row in read_csv("anti_hardcode_step41.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-hardcode failed: {row['check']}")


def validate_tensor_and_amplitude_artifacts() -> None:
    specs = json.loads((ARTIFACT_DIR / "tensor_network_tensors_step41.json").read_text(encoding="utf-8"))
    if not specs:
        fail("tensor specification artifact is empty")
    for spec in specs:
        if "vertices" not in spec or not spec["vertices"]:
            fail(f"tensor spec lacks vertices: {spec.get('case_id')}")
        if "left_boundary_region_A" not in spec:
            fail(f"tensor spec lacks region record: {spec.get('case_id')}")
    amplitudes = read_csv("contracted_boundary_state_step41.csv")
    if not amplitudes:
        fail("contracted amplitude artifact is empty")
    case_ids = {row["case_id"] for row in read_csv("tensor_network_rt_bound_sim_step41.csv")}
    amp_case_ids = {row["case_id"] for row in amplitudes}
    if not case_ids.issubset(amp_case_ids):
        fail("not every sim case has contracted amplitudes")


def validate_content_paths_and_ledgers() -> None:
    rows = read_csv("content_classification_step41.csv")
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
    if "G_E018_TensorNetworkRT_v1" not in manifest:
        fail("grammar manifest missing G_E018_TensorNetworkRT_v1")
    if "G_E018_MinCutShadowPrice_v1" not in manifest or "dimension matching" not in manifest:
        fail("grammar manifest does not record Step40 dimension-matching exclusion")


def validate_hardcode_source() -> None:
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ["0" + ".25", "1" + "/4G", "RT" + "_CONSTANT"]:
        if forbidden in source:
            fail(f"forbidden hardcoded selector literal in build source: {forbidden}")
    if "contract_boundary_state" not in source or "entropy_for_region" not in source or "maxflow_mincut" not in source:
        fail("build source lacks separated contraction/entropy/min-cut paths")


def validate_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in [
            "step41_results_summary.md",
            "nonclaim_boundary_step41.md",
            "step41_rt_bound_statement.tex",
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
        print("usage: run_step41.py --self|--chain", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_sim_rows_against_builder()
    validate_ablation_and_gates()
    validate_tensor_and_amplitude_artifacts()
    validate_content_paths_and_ledgers()
    validate_hardcode_source()
    validate_overclaims()
    print(f"run_step41.py: PASS {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
