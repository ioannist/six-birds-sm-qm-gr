#!/usr/bin/env python3
"""Validate Step 42 faithful holographic RT-enrichment artifacts."""

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
BUILD_SCRIPT = ARTIFACT_DIR / "faithful_holographic_rt_enrichment_step42.py"
TOL = 1e-8

REQUIRED_FILES = [
    "faithful_holographic_rt_enrichment_step42.py",
    "step42_results_summary.md",
    "step42_schema.json",
    "content_classification_step42.csv",
    "nonclaim_boundary_step42.md",
    "step42_rt_enrichment_statement.tex",
    "rt_enrichment_sim_step42.csv",
    "rt_enrichment_trend_step42.csv",
    "bulk_graph_edges_step42.csv",
    "contracted_state_summary_step42.csv",
    "explicit_tensors_step42.json",
    "mincut_competing_cuts_step42.csv",
    "ablation_step42.csv",
    "anti_circularity_step42.csv",
    "six_gate_audit_step42.csv",
    "generated_vs_input_step42.csv",
    "anti_hardcode_step42.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step42.py",
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
    print(f"run_step42.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_builder():
    spec = importlib.util.spec_from_file_location("step42_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    sys.modules["step42_builder"] = module
    spec.loader.exec_module(module)
    return module


def validate_presence() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required artifacts: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step42_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 42,
        "orientation": "ModeB_E018_faithful_holographic_RT_enrichment",
        "verdict": "RT_BOUND_SATURATED_MULTIEDGE_HOLOGRAPHIC",
        "tensor_kind": "random",
        "bound_holds_all_tested": True,
        "state_from_contraction": True,
        "root_landed": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "other_law_landing_legs_attempted": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if int(schema["min_cut_edge_count"]) < 2:
        fail("schema min-cut edge count is not multi-edge")
    if float(schema["strict_gap_value"]) <= 1e-6:
        fail("schema strict-gap value is too small")
    ratios = [float(schema[f"saturation_trend_D{dim}"]) for dim in (2, 3, 4)]
    if not (ratios[0] < ratios[1] < ratios[2]):
        fail(f"saturation trend is not increasing: {ratios}")
    if ratios[0] >= 0.99:
        fail("smallest-D random row is identity-like exact saturation")
    return schema


def validate_sim_and_recompute() -> None:
    rows = read_csv("rt_enrichment_sim_step42.csv")
    if len(rows) < 18:
        fail("sim artifact is too small for the random trend plus controls")
    if not all(as_bool(row["state_from_contraction"]) for row in rows):
        fail("some sim rows are not marked contraction-derived")
    if not all(as_bool(row["bound_holds"]) for row in rows):
        fail("S<=min-cut bound fails in a tested row")
    if not any(row["tensor_kind"] in {"product", "weighted_degenerate"} and as_bool(row["strict_gap"]) and float(row["area_minus_entropy_gap"]) > 1e-6 for row in rows):
        fail("no non-holographic strict-gap control")
    if all(float(row["area_minus_entropy_gap"]) <= 1e-6 for row in rows):
        fail("all rows saturate; identity/circularity signature")

    random_left_all = [row for row in rows if row["tensor_kind"] == "random_gaussian" and row["region"] == "left_all"]
    dims = {int(row["bond_dim"]) for row in random_left_all}
    if dims != {2, 3, 4}:
        fail(f"random trend missing bond dimensions: {sorted(dims)}")
    for dim in (2, 3, 4):
        seeds = {int(row["seed"]) for row in random_left_all if int(row["bond_dim"]) == dim}
        if seeds != {101, 202, 303, 404, 505}:
            fail(f"unexpected seed set for D={dim}: {sorted(seeds)}")

    builder = load_builder()
    recomputed = builder.build()["sim_rows"]
    keyed = {row["case_id"]: row for row in rows}
    for row in recomputed:
        case_id = row["case_id"]
        if case_id not in keyed:
            fail(f"missing recomputed case in CSV: {case_id}")
        csv_row = keyed[case_id]
        for key in ["entropy_S_A", "min_cut_area", "area_minus_entropy_gap", "saturation_ratio_S_over_area"]:
            if abs(float(row[key]) - float(csv_row[key])) > TOL:
                fail(f"CSV does not match recomputed {key} for {case_id}")


def validate_trend_and_min_cut() -> None:
    trend = read_csv("rt_enrichment_trend_step42.csv")
    if [int(row["bond_dim"]) for row in trend] != [2, 3, 4]:
        fail("trend table must contain D=2,3,4 in order")
    ratios = [float(row["mean_saturation_ratio"]) for row in trend]
    if not (ratios[0] < ratios[1] < ratios[2]):
        fail(f"mean saturation ratio does not trend toward one: {ratios}")
    if ratios[0] >= 0.99:
        fail("smallest-D trend is exact/identity-like")
    if not all(as_bool(row["trend_non_decreasing_from_previous"]) for row in trend):
        fail("trend table marks a non-monotone row")

    mincuts = read_csv("mincut_competing_cuts_step42.csv")
    if not mincuts:
        fail("min-cut evidence table is empty")
    witnesses = []
    for row in mincuts:
        area = float(row["min_cut_area"])
        comp = float(row["competing_cut_capacity"])
        edge_count = int(row["min_cut_edge_count"])
        boundary_count = int(row["boundary_leg_count_region_A"])
        if edge_count >= 2 and edge_count < boundary_count and comp > area + 1e-8 and as_bool(row["competing_cut_strictly_larger"]):
            witnesses.append(row)
    if not witnesses:
        fail("no genuine multi-edge minimal surface beating a larger competing cut")


def validate_ablation_and_gates() -> None:
    ablations = read_csv("ablation_step42.csv")
    by_id = {row["ablation_id"]: row for row in ablations}
    for required in [
        "baseline_random_D3_seed101",
        "swap_to_product_tensor_D3",
        "swap_to_weighted_degenerate_tensor_D3",
        "shrink_bond_dim_random_D2_seed101",
        "different_region_left_pair_D3_seed101",
    ]:
        if required not in by_id:
            fail(f"missing ablation row {required}")
    for required in ["swap_to_product_tensor_D3", "swap_to_weighted_degenerate_tensor_D3"]:
        row = by_id[required]
        if not as_bool(row["bound_holds"]) or not as_bool(row["strict_gap"]):
            fail(f"strict-gap control failed: {required}")
    if float(by_id["shrink_bond_dim_random_D2_seed101"]["saturation_ratio"]) >= float(by_id["baseline_random_D3_seed101"]["saturation_ratio"]):
        fail("shrink-bond-dimension ablation did not reduce saturation")
    if not as_bool(by_id["different_region_left_pair_D3_seed101"]["bound_holds"]):
        fail("different-region ablation violates the bound")

    for row in read_csv("anti_circularity_step42.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-circularity gate failed: {row['gate']}")
    for row in read_csv("six_gate_audit_step42.csv"):
        if not as_bool(row["passes"]):
            fail(f"six-gate audit failed: {row['gate']}")
    for row in read_csv("anti_hardcode_step42.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-hardcode failed: {row['check']}")


def validate_tensor_artifacts() -> None:
    tensors = json.loads((ARTIFACT_DIR / "explicit_tensors_step42.json").read_text(encoding="utf-8"))
    if not tensors:
        fail("explicit tensor artifact is empty")
    first = tensors[0]
    for key in ["left_tensor_flat", "right_tensor_flat", "state_matrix_shape", "state_matrix_norm"]:
        if key not in first:
            fail(f"tensor artifact lacks {key}")
    state_rows = read_csv("contracted_state_summary_step42.csv")
    if not state_rows:
        fail("contracted-state summary is empty")
    sim_ids = {row["case_id"] for row in read_csv("rt_enrichment_sim_step42.csv")}
    state_ids = {row["case_id"] for row in state_rows}
    if not sim_ids.issubset(state_ids):
        fail("not every sim row has a contracted-state summary")


def validate_content_paths_and_ledgers() -> None:
    rows = read_csv("content_classification_step42.csv")
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
    if "G_E018_TensorNetworkRT_v2" not in manifest:
        fail("grammar manifest missing G_E018_TensorNetworkRT_v2")
    if "G_E018_TensorNetworkRT_v1" not in manifest or "multi-edge minimal surface" not in manifest:
        fail("grammar manifest does not record the Step42 grammar delta")
    constraints = (ARTIFACT_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    if "C_STEP42_MULTIEDGE_MINIMAL_SURFACE" not in constraints or "C_STEP42_GENUINE_HOLOGRAPHIC_TENSOR" not in constraints:
        fail("constraint ledger missing Step42 active constraints")


def validate_hardcode_source() -> None:
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    for forbidden in ["0" + ".25", "1" + "/4G", "RT" + "_CONSTANT"]:
        if forbidden in source:
            fail(f"forbidden hardcoded selector literal in build source: {forbidden}")
    for token in ["entropy_from_region", "boundary_state_matrix", "maxflow_mincut"]:
        if token not in source:
            fail(f"build source lacks independent computation path token: {token}")


def validate_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in [
            "step42_results_summary.md",
            "nonclaim_boundary_step42.md",
            "step42_rt_enrichment_statement.tex",
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
        print("usage: run_step42.py --self|--chain", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    validate_schema()
    validate_sim_and_recompute()
    validate_trend_and_min_cut()
    validate_ablation_and_gates()
    validate_tensor_artifacts()
    validate_content_paths_and_ledgers()
    validate_hardcode_source()
    validate_overclaims()
    print(f"run_step42.py: PASS {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
