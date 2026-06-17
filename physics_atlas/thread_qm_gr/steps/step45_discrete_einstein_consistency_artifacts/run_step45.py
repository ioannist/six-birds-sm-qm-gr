#!/usr/bin/env python3
"""Validate Step 45 discrete Einstein-consistency artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
BUILD_SCRIPT = ARTIFACT_DIR / "discrete_einstein_consistency_step45.py"
TOL = 1e-9

REQUIRED_FILES = [
    "discrete_einstein_consistency_step45.py",
    "step45_results_summary.md",
    "step45_schema.json",
    "content_classification_step45.csv",
    "nonclaim_boundary_step45.md",
    "step45_discrete_einstein_statement.tex",
    "discrete_einstein_consistency_sim_step45.csv",
    "cut_incidence_matrix_step45.csv",
    "mincut_regions_step45.csv",
    "region_delta_entropy_step45.csv",
    "contracted_perturbation_summary_step45.json",
    "geometry_response_solve_step45.csv",
    "delta_capacity_solution_step45.csv",
    "consistency_conditions_step45.csv",
    "refinement_trend_step45.csv",
    "generated_vs_input_step45.csv",
    "anti_circularity_step45.csv",
    "six_gate_audit_step45.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step45.py",
]

OVERCLAIM_PATTERNS = [
    r"derives\s+Einstein\s+equation\s+unconditionally",
    r"derives\s+Newton'?s?\s+G",
    r"proves\s+quantum\s+gravity",
    r"solves\s+quantum\s+gravity",
    r"closes\s+E018",
    r"continuum\s+Einstein\s+tensor\s+derived",
    r"unconditional\s+new[- ]physics",
]


def fail(message: str) -> None:
    print(f"run_step45.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_csv(name: str) -> list[dict[str, str]]:
    with (ARTIFACT_DIR / name).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_builder():
    spec = importlib.util.spec_from_file_location("step45_builder", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    sys.modules["step45_builder"] = module
    spec.loader.exec_module(module)
    return module


def validate_presence() -> None:
    missing = [name for name in REQUIRED_FILES if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing required artifacts: {missing}")


def validate_schema() -> dict[str, object]:
    schema = json.loads((ARTIFACT_DIR / "step45_schema.json").read_text(encoding="utf-8"))
    expected = {
        "step": 45,
        "orientation": "ModeB_E018_discrete_Einstein_consistency",
        "verdict": "DISCRETE_RT_CONSISTENCY_CONSTRAINT_DERIVED",
        "constraint_nontrivial": True,
        "geometry_response_solved": True,
        "deltaS_from_contracted_state": True,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "continuum_einstein_tensor_derived": False,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    if int(schema["num_regions"]) <= int(schema["num_edges"]):
        fail("system is not overdetermined")
    if int(schema["cokernel_dim"]) < 1:
        fail("cokernel is trivial")
    if int(schema["rank_M"]) >= int(schema["num_regions"]):
        fail("rank leaves no row-space constraint")
    if float(schema["rt_preserving_residual"]) > 1e-9:
        fail("RT-preserving residual is not machine-small")
    if float(schema["generic_violation_residual"]) <= 1e-6:
        fail("generic contracted-state perturbation does not violate the constraint")
    return schema


def validate_matrix_and_rank(schema: dict[str, object]) -> None:
    rows = read_csv("cut_incidence_matrix_step45.csv")
    if len(rows) != int(schema["num_regions"]):
        fail("cut-incidence matrix row count mismatch")
    edge_fields = [field for field in rows[0] if field.startswith("edge_")]
    if len(edge_fields) != int(schema["num_edges"]):
        fail("cut-incidence matrix edge count mismatch")
    matrix = np.array([[float(row[field]) for field in edge_fields] for row in rows])
    rank = int(np.linalg.matrix_rank(matrix))
    if rank != int(schema["rank_M"]):
        fail(f"matrix rank mismatch: CSV rank {rank}, schema {schema['rank_M']}")
    if len(rows) - rank != int(schema["cokernel_dim"]):
        fail("cokernel dimension mismatch")
    if not any(float(row["cut_edge_count"]) >= 3 for row in read_csv("mincut_regions_step45.csv")):
        fail("no internal multi-edge cut row in min-cut regions")


def validate_solves_and_constraints(schema: dict[str, object]) -> None:
    solves = {row["case_id"]: row for row in read_csv("geometry_response_solve_step45.csv")}
    for case_id in ["rt_preserving_geometry_shift", "generic_contracted_state_perturbation"]:
        if case_id not in solves:
            fail(f"missing solve row: {case_id}")
        if not as_bool(solves[case_id]["geometry_response_solved"]):
            fail(f"geometry response not marked solved for {case_id}")
    if float(solves["rt_preserving_geometry_shift"]["least_squares_residual_norm"]) > 1e-9:
        fail("RT-preserving solve residual too large")
    if float(solves["generic_contracted_state_perturbation"]["least_squares_residual_norm"]) <= 1e-6:
        fail("generic solve residual does not violate")
    if abs(float(solves["generic_contracted_state_perturbation"]["least_squares_residual_norm"]) - float(schema["generic_violation_residual"])) > 1e-10:
        fail("generic residual mismatch between schema and solve table")
    constraints = read_csv("consistency_conditions_step45.csv")
    if len(constraints) != int(schema["cokernel_dim"]):
        fail("constraint row count does not match cokernel dimension")
    if not all(abs(float(row["dot_rt_preserving"])) < 1e-8 for row in constraints):
        fail("RT-preserving perturbation violates at least one consistency row")
    if not any(abs(float(row["dot_generic_contracted"])) > 1e-4 for row in constraints):
        fail("generic contracted perturbation does not visibly violate any consistency row")


def validate_deltaS_and_recompute(schema: dict[str, object]) -> None:
    delta_rows = read_csv("region_delta_entropy_step45.csv")
    if len(delta_rows) != int(schema["num_regions"]):
        fail("delta-S table row count mismatch")
    if not all("contracted" in row["entropy_source"] for row in delta_rows):
        fail("delta-S rows do not cite contracted-state entropy source")
    summary = json.loads((ARTIFACT_DIR / "contracted_perturbation_summary_step45.json").read_text(encoding="utf-8"))
    if float(summary["epsilon"]) <= 0.0:
        fail("perturbation epsilon is invalid")
    builder = load_builder()
    recomputed = builder.build()["schema"]
    for key in ["num_regions", "num_edges", "rank_M", "cokernel_dim"]:
        if int(recomputed[key]) != int(schema[key]):
            fail(f"recomputed schema mismatch for {key}")
    for key in ["rt_preserving_residual", "generic_violation_residual"]:
        if abs(float(recomputed[key]) - float(schema[key])) > 1e-10:
            fail(f"recomputed residual mismatch for {key}")


def validate_gates_and_refinement() -> None:
    for row in read_csv("anti_circularity_step45.csv"):
        if not as_bool(row["passes"]):
            fail(f"anti-circularity gate failed: {row['gate']}")
    for row in read_csv("six_gate_audit_step45.csv"):
        if not as_bool(row["passes"]):
            fail(f"six-gate audit failed: {row['gate']}")
    trend = read_csv("refinement_trend_step45.csv")
    if len(trend) != 3:
        fail("refinement trend should carry D=2,3,4")
    ratios = [float(row["mean_RT_saturation_ratio_step42"]) for row in trend]
    if not (ratios[0] < ratios[1] < ratios[2]):
        fail("RT saturation support trend is not increasing")
    if not all(float(row["max_I3_standard_step44"]) <= 1e-8 for row in trend):
        fail("MMI support trend leaves holographic cone")


def validate_content_paths_and_ledgers() -> None:
    rows = read_csv("content_classification_step45.csv")
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
    if "G_E018_DiscreteEinsteinConsistency_v1" not in manifest:
        fail("grammar manifest missing G_E018_DiscreteEinsteinConsistency_v1")
    if "continuum/differential-geometry carrier" not in manifest:
        fail("grammar manifest missing continuum frontier")
    constraints = (ARTIFACT_DIR / "mode_b_constraint_ledger.csv").read_text(encoding="utf-8")
    if "C_STEP45_DISCRETE_CONSTRAINT_NONTRIVIAL_AND_CANFAIL" not in constraints:
        fail("constraint ledger missing Step45 can-fail constraint")


def validate_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8")
        for name in [
            "step45_results_summary.md",
            "nonclaim_boundary_step45.md",
            "step45_discrete_einstein_statement.tex",
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
        print("usage: run_step45.py --self|--chain", file=sys.stderr)
        return 2
    if argv[1] == "--chain":
        run_chain()
    validate_presence()
    schema = validate_schema()
    validate_matrix_and_rank(schema)
    validate_solves_and_constraints(schema)
    validate_deltaS_and_recompute(schema)
    validate_gates_and_refinement()
    validate_content_paths_and_ledgers()
    validate_overclaims()
    print(f"run_step45.py: PASS {argv[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
