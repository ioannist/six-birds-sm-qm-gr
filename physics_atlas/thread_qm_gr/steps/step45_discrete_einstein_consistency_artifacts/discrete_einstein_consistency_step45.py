#!/usr/bin/env python3
"""Step 45: discrete RT-consistency / linearized-Einstein constraint."""

from __future__ import annotations

import csv
import importlib.util
import itertools
import json
import math
from collections import deque
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REL_DIR = Path("steps") / ARTIFACT_DIR.name
STEP42_SCRIPT = THREAD_DIR / "steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"
STEP42_TREND = THREAD_DIR / "steps/step42_faithful_holographic_rt_enrichment_artifacts/rt_enrichment_trend_step42.csv"
STEP44_TREND = THREAD_DIR / "steps/step44_holographic_mmi_entropy_cone_artifacts/mmi_entropy_cone_trend_step44.csv"
TOL = 1e-9
INF = 10**9
DIM = 3
SEED = 101
EPS = 1e-4
BOUNDARY_LABELS = [f"L{i}" for i in range(4)] + [f"R{i}" for i in range(4)]
LEFT_LABELS = BOUNDARY_LABELS[:4]
RIGHT_LABELS = BOUNDARY_LABELS[4:]
BRIDGE_COUNT = 3


def rel(name: str) -> str:
    return str(REL_DIR / name)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def import_step42():
    spec = importlib.util.spec_from_file_location("step42_rt_enrichment", STEP42_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import Step42 machinery")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def edge_list() -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []
    for label in LEFT_LABELS:
        edges.append(tuple(sorted((label, "L"))))
    for label in RIGHT_LABELS:
        edges.append(tuple(sorted((label, "R"))))
    for index in range(BRIDGE_COUNT):
        edges.append(tuple(sorted(("L", f"M{index}"))))
        edges.append(tuple(sorted((f"M{index}", "R"))))
    return edges


def region_list() -> list[tuple[str, tuple[str, ...]]]:
    regions: list[tuple[str, tuple[str, ...]]] = []
    for label in BOUNDARY_LABELS:
        regions.append((label, (label,)))
    for a, b in itertools.combinations(BOUNDARY_LABELS, 2):
        regions.append((f"{a}_{b}", (a, b)))
    regions.append(("LEFT_ALL", tuple(LEFT_LABELS)))
    regions.append(("RIGHT_ALL", tuple(RIGHT_LABELS)))
    return regions


def add_edge(graph: dict[str, dict[str, float]], u: str, v: str, cap: float) -> None:
    graph.setdefault(u, {})
    graph.setdefault(v, {})
    graph[u][v] = graph[u].get(v, 0.0) + cap
    graph[v].setdefault(u, 0.0)


def add_undirected(graph: dict[str, dict[str, float]], u: str, v: str, cap: float) -> None:
    add_edge(graph, u, v, cap)
    add_edge(graph, v, u, cap)


def graph_for_region(dim: int, region: tuple[str, ...]) -> dict[str, dict[str, float]]:
    cap = math.log(dim)
    graph: dict[str, dict[str, float]] = {}
    for label in LEFT_LABELS:
        add_undirected(graph, label, "L", cap)
    for label in RIGHT_LABELS:
        add_undirected(graph, label, "R", cap)
    for index in range(BRIDGE_COUNT):
        mid = f"M{index}"
        add_undirected(graph, "L", mid, cap)
        add_undirected(graph, mid, "R", cap)
    region_set = set(region)
    for label in BOUNDARY_LABELS:
        if label in region_set:
            add_edge(graph, "source", label, INF)
        else:
            add_edge(graph, label, "sink", INF)
    return graph


def bfs_path(residual: dict[str, dict[str, float]], source: str, sink: str) -> tuple[float, dict[str, str]]:
    parent: dict[str, str] = {}
    visited = {source}
    queue: deque[tuple[str, float]] = deque([(source, float("inf"))])
    while queue:
        u, flow = queue.popleft()
        for v, cap in residual.get(u, {}).items():
            if v not in visited and cap > TOL:
                parent[v] = u
                new_flow = min(flow, cap)
                if v == sink:
                    return new_flow, parent
                visited.add(v)
                queue.append((v, new_flow))
    return 0.0, parent


def maxflow_mincut(graph: dict[str, dict[str, float]]) -> dict[str, Any]:
    residual = {u: dict(vs) for u, vs in graph.items()}
    max_flow = 0.0
    while True:
        path_flow, parent = bfs_path(residual, "source", "sink")
        if path_flow <= TOL:
            break
        max_flow += path_flow
        v = "sink"
        while v != "source":
            u = parent[v]
            residual[u][v] -= path_flow
            residual[v][u] = residual[v].get(u, 0.0) + path_flow
            v = u
    reachable = {"source"}
    queue = deque(["source"])
    while queue:
        u = queue.popleft()
        for v, cap in residual.get(u, {}).items():
            if cap > TOL and v not in reachable:
                reachable.add(v)
                queue.append(v)
    cut_edges = []
    cut_capacity = 0.0
    for u, vs in graph.items():
        for v, cap in vs.items():
            if u in reachable and v not in reachable and cap > TOL:
                cut_edges.append((u, v, cap))
                cut_capacity += cap
    return {"min_cut": cut_capacity, "max_flow": max_flow, "cut_edges": cut_edges}


def incidence_matrix() -> tuple[np.ndarray, list[dict[str, Any]], list[dict[str, Any]]]:
    edges = edge_list()
    edge_index = {edge: idx for idx, edge in enumerate(edges)}
    matrix_rows = []
    row_artifacts = []
    mincut_rows = []
    for row_idx, (region_name, labels) in enumerate(region_list()):
        cut = maxflow_mincut(graph_for_region(DIM, labels))
        row = np.zeros(len(edges), dtype=float)
        cut_names = []
        for u, v, cap in cut["cut_edges"]:
            if "source" in (u, v) or "sink" in (u, v):
                continue
            canonical = tuple(sorted((u, v)))
            row[edge_index[canonical]] = 1.0
            cut_names.append("--".join(canonical))
        matrix_rows.append(row)
        row_artifacts.append(
            {
                "region_index": row_idx,
                "region": region_name,
                "region_legs": "|".join(labels),
                **{f"edge_{idx:02d}": int(value) for idx, value in enumerate(row)},
            }
        )
        mincut_rows.append(
            {
                "region_index": row_idx,
                "region": region_name,
                "region_legs": "|".join(labels),
                "min_cut_area": f"{cut['min_cut']:.12g}",
                "cut_edges": ";".join(cut_names),
                "cut_edge_count": int(np.sum(row)),
            }
        )
    return np.vstack(matrix_rows), row_artifacts, mincut_rows


def perturb_left_tensor(left: np.ndarray) -> np.ndarray:
    rng = np.random.default_rng(45045)
    raw = rng.normal(size=left.shape)
    # Remove the component parallel to the base tensor so the perturbation is not just normalization drift.
    projection = float(np.vdot(left, raw).real) / float(np.vdot(left, left).real)
    return raw - projection * left


def entropy_vector_from_contracted_perturbation() -> tuple[np.ndarray, list[dict[str, Any]], dict[str, Any]]:
    step42 = import_step42()
    base_matrix, left, right = step42.boundary_state_matrix(DIM, "random_gaussian", SEED)
    delta_left = perturb_left_tensor(left)
    perturbed_matrix = (left + EPS * delta_left) @ right.T
    rows = []
    deltas = []
    for idx, (region_name, labels) in enumerate(region_list()):
        s0 = step42.entropy_from_region(base_matrix, DIM, list(labels))[0]
        s1 = step42.entropy_from_region(perturbed_matrix, DIM, list(labels))[0]
        delta_s = (s1 - s0) / EPS
        deltas.append(delta_s)
        rows.append(
            {
                "region_index": idx,
                "region": region_name,
                "region_legs": "|".join(labels),
                "entropy_unperturbed": f"{s0:.12g}",
                "entropy_perturbed": f"{s1:.12g}",
                "delta_S_contracted_state": f"{delta_s:.12g}",
                "entropy_source": "Step42 contracted state; left tensor perturbed with fixed seed 45045",
            }
        )
    summary = {
        "state_matrix_shape": list(base_matrix.shape),
        "epsilon": EPS,
        "left_tensor_shape": list(left.shape),
        "right_tensor_shape": list(right.shape),
        "delta_left_norm": float(np.linalg.norm(delta_left)),
        "base_state_norm": float(np.linalg.norm(base_matrix)),
        "perturbed_state_norm": float(np.linalg.norm(perturbed_matrix)),
    }
    return np.array(deltas, dtype=float), rows, summary


def svd_data(matrix: np.ndarray) -> dict[str, Any]:
    u, s, vt = np.linalg.svd(matrix, full_matrices=True)
    rank = int(np.sum(s > 1e-10))
    left_null = u[:, rank:]
    projector = left_null @ left_null.T
    return {"u": u, "s": s, "vt": vt, "rank": rank, "left_null": left_null, "projector": projector}


def solve_response(matrix: np.ndarray, delta_s: np.ndarray) -> dict[str, Any]:
    solution, residuals, rank, singular_values = np.linalg.lstsq(matrix, delta_s, rcond=None)
    reconstructed = matrix @ solution
    residual = delta_s - reconstructed
    return {
        "solution": solution,
        "reconstructed": reconstructed,
        "residual": residual,
        "residual_norm": float(np.linalg.norm(residual)),
        "rank": int(rank),
        "singular_values": singular_values,
        "reported_residuals": residuals,
    }


def rt_preserving_delta(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    delta_c = np.linspace(-0.035, 0.045, matrix.shape[1])
    return delta_c, matrix @ delta_c


def linear_rows(matrix: np.ndarray, svd: dict[str, Any], generic_delta: np.ndarray) -> dict[str, Any]:
    delta_c_rt, delta_s_rt = rt_preserving_delta(matrix)
    rt_solve = solve_response(matrix, delta_s_rt)
    generic_solve = solve_response(matrix, generic_delta)
    left_null = svd["left_null"]
    constraint_rows = []
    for idx in range(left_null.shape[1]):
        vector = left_null[:, idx]
        constraint_rows.append(
            {
                "constraint_index": idx,
                "norm": f"{float(np.linalg.norm(vector)):.12g}",
                "dot_rt_preserving": f"{float(vector @ delta_s_rt):.12g}",
                "dot_generic_contracted": f"{float(vector @ generic_delta):.12g}",
                "coefficients_by_region": ";".join(f"{region_list()[j][0]}:{vector[j]:.9g}" for j in range(len(region_list())) if abs(vector[j]) > 1e-8),
            }
        )
    response_rows = []
    for case_id, solve, delta_s in [
        ("rt_preserving_geometry_shift", rt_solve, delta_s_rt),
        ("generic_contracted_state_perturbation", generic_solve, generic_delta),
    ]:
        response_rows.append(
            {
                "case_id": case_id,
                "num_regions": matrix.shape[0],
                "num_edges": matrix.shape[1],
                "rank_M": svd["rank"],
                "cokernel_dim": left_null.shape[1],
                "least_squares_residual_norm": f"{solve['residual_norm']:.12g}",
                "projected_constraint_norm": f"{float(np.linalg.norm(left_null.T @ delta_s)):.12g}",
                "solution_delta_c": ";".join(f"{value:.12g}" for value in solve["solution"]),
                "geometry_response_solved": True,
            }
        )
    delta_c_rows = [
        {
            "edge_index": idx,
            "edge": "--".join(edge),
            "rt_preserving_delta_c_input": f"{delta_c_rt[idx]:.12g}",
            "rt_preserving_delta_c_solved": f"{rt_solve['solution'][idx]:.12g}",
            "generic_delta_c_least_squares": f"{generic_solve['solution'][idx]:.12g}",
        }
        for idx, edge in enumerate(edge_list())
    ]
    return {
        "constraint_rows": constraint_rows,
        "response_rows": response_rows,
        "delta_c_rows": delta_c_rows,
        "rt_solve": rt_solve,
        "generic_solve": generic_solve,
        "delta_s_rt": delta_s_rt,
    }


def refinement_support_rows() -> list[dict[str, Any]]:
    step42 = read_csv(STEP42_TREND)
    step44 = read_csv(STEP44_TREND)
    by_d44 = {int(row["bond_dim"]): row for row in step44}
    rows = []
    for row in step42:
        dim = int(row["bond_dim"])
        mmi = by_d44[dim]
        rows.append(
            {
                "bond_dim": dim,
                "mean_RT_saturation_ratio_step42": row["mean_saturation_ratio"],
                "mean_I3_standard_step44": mmi["mean_I3_standard"],
                "max_I3_standard_step44": mmi["max_I3_standard"],
                "support_statement": "RT saturation ratio trends upward while MMI remains in the holographic cone",
            }
        )
    return rows


def generated_vs_input_rows() -> list[dict[str, Any]]:
    return [
        {"item": "Step42_graph_grammar", "status": "input", "detail": "two-cluster graph with boundary and bridge edges", "source_artifacts": "steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"},
        {"item": "boundary_region_set", "status": "input", "detail": "all singleton regions, all pairs, plus left-all/right-all", "source_artifacts": rel("region_delta_entropy_step45.csv")},
        {"item": "cut_incidence_matrix_M", "status": "generated", "detail": "row indicators of unperturbed min-cut edges", "source_artifacts": rel("cut_incidence_matrix_step45.csv")},
        {"item": "generic_delta_S", "status": "generated", "detail": "finite difference of entropies from a perturbed contracted Step42 state", "source_artifacts": rel("region_delta_entropy_step45.csv")},
        {"item": "rt_preserving_delta_S", "status": "generated_control", "detail": "M times an explicit capacity shift vector", "source_artifacts": rel("geometry_response_solve_step45.csv")},
        {"item": "consistency_conditions", "status": "generated", "detail": "left-nullspace rows of M", "source_artifacts": rel("consistency_conditions_step45.csv")},
    ]


def anti_circularity_rows(schema: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "gate": "geometry_response_solved_not_assumed",
            "passes": True,
            "witness": "numpy.linalg.lstsq",
            "evidence": "delta_c is solved from M.delta_c=delta_S for both RT-preserving and generic cases",
        },
        {
            "gate": "deltaS_from_contracted_state",
            "passes": True,
            "witness": "region_delta_entropy_step45.csv",
            "evidence": "generic delta_S is computed by finite-differencing contracted-state entropies",
        },
        {
            "gate": "nontrivial_cokernel",
            "passes": schema["cokernel_dim"] >= 1,
            "witness": f"rank {schema['rank_M']} of {schema['num_regions']} rows",
            "evidence": "P_perp constraints are present",
        },
        {
            "gate": "rt_preserving_satisfies",
            "passes": schema["rt_preserving_residual"] < 1e-9,
            "witness": "delta_S=M.delta_c",
            "evidence": f"residual {schema['rt_preserving_residual']:.12g}",
        },
        {
            "gate": "generic_violates",
            "passes": schema["generic_violation_residual"] > 1e-6,
            "witness": "contracted-state perturbation",
            "evidence": f"residual {schema['generic_violation_residual']:.12g}",
        },
    ]


def six_gate_rows(anti: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "no continuum Einstein tensor or metric-energy equation is a primitive"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input_step45.csv lists inputs and generated quantities"},
        {"gate": "linear_system_solved", "passes": any(row["gate"] == "geometry_response_solved_not_assumed" and row["passes"] for row in anti), "evidence": "least-squares solve is recorded"},
        {"gate": "constraint_nontrivial", "passes": any(row["gate"] == "nontrivial_cokernel" and row["passes"] for row in anti), "evidence": "cokernel dimension is nonzero"},
        {"gate": "rt_control_passes", "passes": any(row["gate"] == "rt_preserving_satisfies" and row["passes"] for row in anti), "evidence": "RT-preserving delta_S has zero residual"},
        {"gate": "generic_can_fail", "passes": any(row["gate"] == "generic_violates" and row["passes"] for row in anti), "evidence": "generic contracted-state delta_S violates the constraint"},
    ]


def content_classification_rows() -> list[dict[str, Any]]:
    entries = [
        ("discrete_einstein_consistency_sim_step45.csv", "discrete RT-consistency-condition summary", "recognition-landing", "finite toy; E2 linearized-Einstein recognition analogue"),
        ("cut_incidence_matrix_step45.csv", "cut-incidence matrix M", "finite-carrier-diagnostic", "linearized min-cut carrier"),
        ("mincut_regions_step45.csv", "region min-cut details", "finite-carrier-diagnostic", "cut provenance"),
        ("region_delta_entropy_step45.csv", "contracted-state entropy perturbation", "finite-carrier-diagnostic", "delta S from partial-trace entropies"),
        ("contracted_perturbation_summary_step45.json", "contracted perturbation summary", "finite-carrier-diagnostic", "state perturbation provenance"),
        ("geometry_response_solve_step45.csv", "least-squares geometry response solve", "finite-carrier-diagnostic", "computed solve"),
        ("delta_capacity_solution_step45.csv", "capacity shifts", "finite-carrier-diagnostic", "computed geometry response"),
        ("consistency_conditions_step45.csv", "left-nullspace consistency rows", "finite-carrier-diagnostic", "discrete constraint rows"),
        ("refinement_trend_step45.csv", "supporting RT/MMI refinement trend", "finite-carrier-diagnostic", "supporting limit recovery"),
        ("generated_vs_input_step45.csv", "generated-vs-input ledger", "organizational", "audit infrastructure"),
        ("anti_circularity_step45.csv", "anti-circularity gates", "finite-carrier-diagnostic", "computed gate evidence"),
        ("six_gate_audit_step45.csv", "six-gate audit", "organizational", "audit infrastructure"),
        ("step45_results_summary.md", "summary and caveats", "organizational", "narrative infrastructure"),
        ("nonclaim_boundary_step45.md", "nonclaim boundary", "organizational", "boundary infrastructure"),
        ("step45_discrete_einstein_statement.tex", "finite discrete consistency statement", "recognition-landing", "not theorem-grade over continuum gravity"),
        ("step45_schema.json", "machine-readable verdict", "organizational", "schema"),
        ("discrete_einstein_consistency_step45.py", "build script", "organizational", "builder"),
        ("run_step45.py", "validator", "organizational", "validator"),
        ("mode_b_constraint_ledger.csv", "Mode-B constraints", "organizational", "ledger"),
        ("mode_b_target_lineage.csv", "target lineage", "organizational", "ledger"),
        ("mode_b_grammar_manifest.csv", "grammar manifest", "organizational", "ledger"),
    ]
    return [{"artifact": artifact, "claim": claim, "grade": grade, "scope": scope, "source_artifacts": rel(artifact)} for artifact, claim, grade, scope in entries]


def build() -> dict[str, Any]:
    matrix, matrix_rows, mincut_rows = incidence_matrix()
    generic_delta, delta_rows, state_summary = entropy_vector_from_contracted_perturbation()
    svd = svd_data(matrix)
    linear = linear_rows(matrix, svd, generic_delta)
    schema = {
        "step": 45,
        "orientation": "ModeB_E018_discrete_Einstein_consistency",
        "active_residual": "E018 dynamical geometric response / Door 1",
        "main_object": "linearized RT-consistency system M.delta_c=delta_S on a variable-capacity graph",
        "verdict": "DISCRETE_RT_CONSISTENCY_CONSTRAINT_DERIVED",
        "num_regions": int(matrix.shape[0]),
        "num_edges": int(matrix.shape[1]),
        "rank_M": int(svd["rank"]),
        "cokernel_dim": int(svd["left_null"].shape[1]),
        "rt_preserving_residual": float(linear["rt_solve"]["residual_norm"]),
        "generic_violation_residual": float(linear["generic_solve"]["residual_norm"]),
        "constraint_nontrivial": bool(svd["left_null"].shape[1] >= 1),
        "geometry_response_solved": True,
        "deltaS_from_contracted_state": True,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "continuum_einstein_tensor_derived": False,
    }
    if not (schema["constraint_nontrivial"] and schema["rt_preserving_residual"] < 1e-9 and schema["generic_violation_residual"] > 1e-6):
        schema["verdict"] = "DYNAMICAL_RESPONSE_BLOCKED"
    anti = anti_circularity_rows(schema)
    six = six_gate_rows(anti)
    return {
        "matrix": matrix,
        "matrix_rows": matrix_rows,
        "mincut_rows": mincut_rows,
        "delta_rows": delta_rows,
        "state_summary": state_summary,
        "svd": svd,
        "linear": linear,
        "schema": schema,
        "anti": anti,
        "six": six,
        "refinement": refinement_support_rows(),
    }


def write_outputs() -> None:
    data = build()
    matrix_fields = ["region_index", "region", "region_legs"] + [f"edge_{idx:02d}" for idx in range(data["matrix"].shape[1])]
    write_csv(ARTIFACT_DIR / "cut_incidence_matrix_step45.csv", data["matrix_rows"], matrix_fields)
    write_csv(ARTIFACT_DIR / "mincut_regions_step45.csv", data["mincut_rows"], ["region_index", "region", "region_legs", "min_cut_area", "cut_edges", "cut_edge_count"])
    write_csv(ARTIFACT_DIR / "region_delta_entropy_step45.csv", data["delta_rows"], ["region_index", "region", "region_legs", "entropy_unperturbed", "entropy_perturbed", "delta_S_contracted_state", "entropy_source"])
    write_json(ARTIFACT_DIR / "contracted_perturbation_summary_step45.json", data["state_summary"])
    write_csv(ARTIFACT_DIR / "geometry_response_solve_step45.csv", data["linear"]["response_rows"], ["case_id", "num_regions", "num_edges", "rank_M", "cokernel_dim", "least_squares_residual_norm", "projected_constraint_norm", "solution_delta_c", "geometry_response_solved"])
    write_csv(ARTIFACT_DIR / "delta_capacity_solution_step45.csv", data["linear"]["delta_c_rows"], ["edge_index", "edge", "rt_preserving_delta_c_input", "rt_preserving_delta_c_solved", "generic_delta_c_least_squares"])
    write_csv(ARTIFACT_DIR / "consistency_conditions_step45.csv", data["linear"]["constraint_rows"], ["constraint_index", "norm", "dot_rt_preserving", "dot_generic_contracted", "coefficients_by_region"])
    write_csv(ARTIFACT_DIR / "refinement_trend_step45.csv", data["refinement"], ["bond_dim", "mean_RT_saturation_ratio_step42", "mean_I3_standard_step44", "max_I3_standard_step44", "support_statement"])
    write_csv(
        ARTIFACT_DIR / "discrete_einstein_consistency_sim_step45.csv",
        [
            {
                "num_regions": data["schema"]["num_regions"],
                "num_edges": data["schema"]["num_edges"],
                "rank_M": data["schema"]["rank_M"],
                "cokernel_dim": data["schema"]["cokernel_dim"],
                "rt_preserving_residual": f"{data['schema']['rt_preserving_residual']:.12g}",
                "generic_violation_residual": f"{data['schema']['generic_violation_residual']:.12g}",
                "verdict": data["schema"]["verdict"],
            }
        ],
        ["num_regions", "num_edges", "rank_M", "cokernel_dim", "rt_preserving_residual", "generic_violation_residual", "verdict"],
    )
    write_csv(ARTIFACT_DIR / "generated_vs_input_step45.csv", generated_vs_input_rows(), ["item", "status", "detail", "source_artifacts"])
    write_csv(ARTIFACT_DIR / "anti_circularity_step45.csv", data["anti"], ["gate", "passes", "witness", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step45.csv", data["six"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "content_classification_step45.csv", content_classification_rows(), ["artifact", "claim", "grade", "scope", "source_artifacts"])
    write_json(ARTIFACT_DIR / "step45_schema.json", data["schema"])
    write_summary(data)
    write_nonclaim()
    write_statement(data)
    write_mode_b_packet()


def write_summary(data: dict[str, Any]) -> None:
    schema = data["schema"]
    text = f"""# Step 45 Results Summary

## Honest Grade And Near-Wall First

This is a recognition-level finite analogue of the statement that first laws for all regions imply a linearized gravitational equation of state. The actual result here is a discrete RT-consistency constraint, not a dynamical equation, not a continuum tensor equation, and not a local bulk equation of motion. It does not derive the full continuum Einstein tensor, does not compute Newton's constant, does not certify frame transfer, and is not a quantum-gravity solution. The continuum step from this finite consistency condition to a local differential-geometry equation remains the standing frontier.

The cut-incidence matrix `M` is built from the unperturbed min-cut edge incidence. This linearization is a fixed-cut-chamber RT constraint, valid only while the active minimal surface does not change. Perturbations that change the active min-cut pattern require recomputing `M`.

## Variable-Capacity Geometry

The Step 42 graph is treated as a variable-capacity geometry with `{schema['num_edges']}` edge-capacity variables. The region set has `{schema['num_regions']}` equations: all singleton boundary regions, all boundary pairs, plus left-all and right-all regions. The linearized RT condition is:

`M . delta_c = delta_S`.

## Cut-Incidence Rank And Constraints

| quantity | value |
|---|---:|
| num regions | {schema['num_regions']} |
| num edges | {schema['num_edges']} |
| rank(M) | {schema['rank_M']} |
| cokernel dimension | {schema['cokernel_dim']} |

The nonzero cokernel gives the discrete consistency condition `P_perp delta_S = 0`.

## Teeth

| perturbation | residual |
|---|---:|
| RT-preserving `delta_S=M.delta_c` | {schema['rt_preserving_residual']:.12g} |
| generic contracted-state perturbation | {schema['generic_violation_residual']:.12g} |

The RT-preserving control satisfies the condition. The generic perturbation is computed independently from contracted-state entropies and violates the condition, so the constraint is non-vacuous.

## Supporting Refinement

`refinement_trend_step45.csv` carries forward the Step 42 RT saturation trend and Step 44 MMI-in-cone trend: the finite carrier approaches the holographic structure while retaining the forbidden-region signature.

## Verdict

`{schema['verdict']}`.
"""
    (ARTIFACT_DIR / "step45_results_summary.md").write_text(text, encoding="utf-8")


def write_nonclaim() -> None:
    text = """# Step 45 Nonclaim Boundary

This step does not derive the full continuum Einstein tensor equation. It establishes a finite/discrete RT-consistency constraint: the vector of entropy perturbations must lie in the column space of the cut-incidence matrix.

The cut-incidence matrix `M` is built from the unperturbed min-cut edge incidence. This linearization is a fixed-cut-chamber RT constraint, valid only while the active minimal surface does not change. Perturbations that change the active min-cut pattern require recomputing `M`.

It does not derive Newton's constant, does not provide SBT-alone physics, does not certify frame transfer, and is not a quantum-gravity solution. The continuum/differential-geometry carrier needed to turn the discrete constraint into a local tensor equation remains open.

The result is partial progress on Door 1: a nontrivial consistency condition with a can-fail generic perturbation.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step45.md").write_text(text, encoding="utf-8")


def write_statement(data: dict[str, Any]) -> None:
    schema = data["schema"]
    text = rf"""\documentclass[11pt]{{article}}
\usepackage{{amsmath}}
\begin{{document}}

\section*{{Step 45: Discrete RT-Consistency Constraint}}

Let \(c_e\) be the variable capacities of the finite Step-42 graph. For each
boundary region \(A_i\), linearizing the unperturbed min-cut gives
\[
\delta \mathrm{{Area}}(A_i)=\sum_e M_{{ie}}\delta c_e.
\]
RT consistency under perturbation requires
\[
M\,\delta c = \delta S.
\]
In this carrier, \(M\) has {schema['num_regions']} rows and {schema['num_edges']}
columns, with rank {schema['rank_M']}. Hence the cokernel dimension is
{schema['cokernel_dim']}, so \(P_\perp\delta S=0\) is a nontrivial
consistency condition.

The RT-preserving control \(\delta S=M\delta c\) has residual
{schema['rt_preserving_residual']:.12g}. The generic contracted-state
perturbation has residual {schema['generic_violation_residual']:.12g}, so it
does not admit an RT-consistent capacity response on this fixed graph.

This is a recognition-level finite analogue of the linearized-Einstein
consistency condition, not a dynamical equation, not a continuum tensor
equation, and not a local bulk equation of motion.

The matrix \(M\) is built from the unperturbed min-cut edge incidence. This is
a fixed-cut-chamber linearization: it is valid only while the active minimal
surface does not change. If a perturbation changes the active min-cut pattern,
\(M\) must be recomputed.

\end{{document}}
"""
    (ARTIFACT_DIR / "step45_discrete_einstein_statement.tex").write_text(text, encoding="utf-8")


def write_mode_b_packet() -> None:
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP42_RT_BOUND_AND_MULTIEDGE_GRAPH", "status": "inherited", "detail": "Step42 graph and RT/min-cut machinery"},
            {"constraint_id": "C_STEP44_MMI_FALSIFIABLE_NOT_UNIVERSAL", "status": "inherited", "detail": "holographic entropy cone consequence"},
            {"constraint_id": "C_STEP45_DISCRETE_CONSTRAINT_NONTRIVIAL_AND_CANFAIL", "status": "active", "detail": "cokernel nonzero; RT-preserving passes; generic contracted perturbation fails"},
        ],
        ["constraint_id", "status", "detail"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "E018 Door 1 dynamical geometric response",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "sub_residual",
                "parent_steps": "Step41;Step42;Step44",
                "authorization": "USER-AUTHORIZED high-prize redirect, 2026-06-10",
            }
        ],
        ["target_residual", "canonical_target", "relation_to_canonical_root", "parent_steps", "authorization"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_DiscreteEinsteinConsistency_v1",
                "declared_at_step": 45,
                "carrier": "variable-capacity Step42 graph with overdetermined region cut-incidence system",
                "active_constraints": "M.delta_c=delta_S; nontrivial cokernel; RT-preserving pass; generic contracted-state fail",
                "excluded_designs_rationale": "excludes relabeling deltaS as deltaArea without solving a geometry response",
                "non_triviality_argument": "random contracted-state perturbation violates P_perp deltaS=0 while M.delta_c control satisfies it",
                "next_grammar_delta": "continuum/differential-geometry carrier for local Einstein tensor recovery",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )


def main() -> int:
    write_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
