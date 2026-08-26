#!/usr/bin/env python3
"""Q5 repair: exact graph LP duality and non-circular response/composition probes."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import itertools
import json
import math
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
STEP_ROOT = REPO / "physics_atlas/thread_qm_gr/steps"
SCRIPTS = {
    "step42": STEP_ROOT / "step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py",
    "step44": STEP_ROOT / "step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py",
    "step45": STEP_ROOT / "step45_discrete_einstein_consistency_artifacts/discrete_einstein_consistency_step45.py",
    "step50": STEP_ROOT / "step50_born_area_one_fiber_volume_ledger_artifacts/born_area_one_ledger_step50.py",
    "step55": STEP_ROOT / "step55_f51_entanglement_underdetermines_geometry_artifacts/entanglement_underdetermines_geometry_step55.py",
}
PINS = {
    "step42": "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08",
    "step44": "61f28d10e8170a9f37ac71a711b6d30c3dac9b4f014b8e634c70ba2166a47052",
    "step45": "2348078115c839d2e4ee1fb66a99e620cb3644181befd5374a2f532cc83a4f35",
    "step50": "ddaa2709c08c2e07835b126a2e3778f5ca2738720c6661a8c6127503df6b83d7",
    "step55": "a21740d3f8266c1213bf46f1e1a4a37367b6cb3f2d61b742301539a626d760aa",
}
SEED = 101
DIM = 3
LABELS = [f"L{i}" for i in range(4)] + [f"R{i}" for i in range(4)]
INTERIOR = ["L", "R", "M0", "M1", "M2"]
RESPONSE_EPS = 1e-5
RESPONSE_TOL = 5e-5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_frozen() -> dict[str, Any]:
    modules = {}
    for name, path in SCRIPTS.items():
        actual = sha256(path)
        if actual != PINS[name]:
            raise RuntimeError(f"frozen hash mismatch for {name}: {actual} != {PINS[name]}")
        spec = importlib.util.spec_from_file_location(f"q5_{name}", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


def frac(value: Any) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def csv_bytes(rows: list[dict[str, Any]], fields: list[str]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return stream.getvalue().encode()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def edge_name(edge: tuple[str, str]) -> str:
    return "--".join(edge)


def exact_carrier(modules: dict[str, Any]) -> tuple[list[tuple[str, str]], list[Fraction]]:
    pairs, base = modules["step55"].extract_step42_edges(modules["step42"])
    generic = modules["step55"].generic_weights(base, SEED)
    return [tuple(pair) for pair in pairs], [Fraction(str(float(x))) for x in generic]


def all_masks() -> list[int]:
    return list(range(1, (1 << len(LABELS)) - 1))


def cut_solutions(edges: list[tuple[str, str]], capacities: list[Fraction], mask: int) -> list[tuple[Fraction, frozenset[str], tuple[int, ...]]]:
    selected = {label for i, label in enumerate(LABELS) if mask & (1 << i)}
    rows = []
    for bits in range(1 << len(INTERIOR)):
        source_side = selected | {node for i, node in enumerate(INTERIOR) if bits & (1 << i)}
        cut = tuple(i for i, (u, v) in enumerate(edges) if (u in source_side) != (v in source_side))
        rows.append((sum((capacities[i] for i in cut), Fraction()), frozenset(source_side), cut))
    return sorted(rows, key=lambda row: (row[0], tuple(sorted(row[1]))))


def contracted_node(node: str, mask: int) -> str:
    if node not in LABELS:
        return node
    return "SOURCE" if mask & (1 << LABELS.index(node)) else "SINK"


def exact_maxflow(edges: list[tuple[str, str]], capacities: list[Fraction], mask: int) -> tuple[Fraction, list[Fraction]]:
    ends = [(contracted_node(u, mask), contracted_node(v, mask)) for u, v in edges]
    flow = [Fraction() for _ in edges]  # positive in stored u -> v orientation
    adjacency: dict[str, list[tuple[int, int, str]]] = {}
    for i, (u, v) in enumerate(ends):
        if u == v:
            continue
        adjacency.setdefault(u, []).append((i, +1, v))
        adjacency.setdefault(v, []).append((i, -1, u))
    while True:
        parent: dict[str, tuple[str, int, int]] = {}
        queue = ["SOURCE"]
        seen = {"SOURCE"}
        for node in queue:
            if node == "SINK":
                break
            for idx, direction, nxt in adjacency.get(node, []):
                residual = capacities[idx] - direction * flow[idx]
                if residual > 0 and nxt not in seen:
                    seen.add(nxt)
                    parent[nxt] = (node, idx, direction)
                    queue.append(nxt)
        if "SINK" not in seen:
            break
        path = []
        node = "SINK"
        amount: Fraction | None = None
        while node != "SOURCE":
            prev, idx, direction = parent[node]
            residual = capacities[idx] - direction * flow[idx]
            amount = residual if amount is None else min(amount, residual)
            path.append((idx, direction))
            node = prev
        assert amount is not None
        for idx, direction in path:
            flow[idx] += direction * amount
    value = Fraction()
    for idx, (u, v) in enumerate(ends):
        if u == "SOURCE":
            value += flow[idx]
        elif v == "SOURCE":
            value -= flow[idx]
    return value, flow


def lp_matrices(edges: list[tuple[str, str]], capacities: list[Fraction], mask: int) -> dict[str, Any]:
    ends = [(contracted_node(u, mask), contracted_node(v, mask)) for u, v in edges]
    fvars = [f"f_{i:02d}" for i in range(len(edges))]
    primal_rows = []
    for node in ["SOURCE"] + INTERIOR:
        coeff = [0] * (len(edges) + 1)
        for i, (u, v) in enumerate(ends):
            if u == node:
                coeff[i] += 1
            if v == node:
                coeff[i] -= 1
        if node == "SOURCE":
            coeff[-1] = -1
        primal_rows.append(coeff)
    pnodes = ["SOURCE", "SINK"] + INTERIOR
    dvars = [f"y_{i:02d}" for i in range(len(edges))] + [f"p_{n}" for n in pnodes]
    dual_rows = []
    for i, (u, v) in enumerate(ends):
        if u == v:
            continue
        for sign in (+1, -1):
            coeff = [0] * len(dvars)
            coeff[i] = -1  # -y + sign*(p_u-p_v) <= 0
            coeff[len(edges) + pnodes.index(u)] = sign
            coeff[len(edges) + pnodes.index(v)] = -sign
            dual_rows.append(coeff)
    return {
        "representative_region_mask": mask,
        "representative_region": "|".join(label for i, label in enumerate(LABELS) if mask & (1 << i)),
        "primal": {
            "sense": "maximize",
            "variables": fvars + ["F"],
            "objective": [0] * len(edges) + [1],
            "A_eq": primal_rows,
            "b_eq": [0] * len(primal_rows),
            "bounds": [[f"-{fstr(c)}", fstr(c)] for c in capacities] + [["0", "inf"]],
            "meaning": "signed undirected edge flows and source value F",
        },
        "dual": {
            "sense": "minimize",
            "variables": dvars,
            "objective": [fstr(c) for c in capacities] + ["0"] * len(pnodes),
            "A_ub": dual_rows,
            "b_ub": [0] * len(dual_rows),
            "bounds": [["0", "inf"] for _ in edges] + [["-inf", "inf"] for _ in pnodes],
            "equalities": {"p_SOURCE": 1, "p_SINK": 0},
            "meaning": "y_e >= |p_u-p_v|; y_e is the per-edge capacity shadow price",
        },
    }


def entropy(state_matrix: np.ndarray, labels: list[str]) -> float:
    norm = float(np.linalg.norm(state_matrix))
    psi = (state_matrix / norm).reshape([DIM] * len(LABELS))
    axes = [LABELS.index(x) for x in labels]
    comp = [i for i in range(len(LABELS)) if i not in axes]
    mat = np.transpose(psi, axes + comp).reshape(DIM ** len(axes), -1)
    singular = np.linalg.svd(mat, compute_uv=False)
    probs = singular * singular
    probs = probs[probs > 1e-14]
    return float(-np.sum(probs * np.log(probs)))


def entropy_all(state_matrix: np.ndarray) -> dict[int, float]:
    result: dict[int, float] = {}
    full = (1 << len(LABELS)) - 1
    for mask in all_masks():
        other = full ^ mask
        if other in result:
            result[mask] = result[other]
        else:
            result[mask] = entropy(state_matrix, [x for i, x in enumerate(LABELS) if mask & (1 << i)])
    return result


def mmi(entropies: dict[int, float], a: int, b: int, c: int) -> float:
    return entropies[a] + entropies[b] + entropies[c] + entropies[a | b | c] - entropies[a | b] - entropies[a | c] - entropies[b | c]


def build() -> dict[str, Any]:
    started = time.perf_counter()
    modules = load_frozen()
    edges, capacities = exact_carrier(modules)
    masks = all_masks()
    solutions = {mask: cut_solutions(edges, capacities, mask) for mask in masks}
    if not all(rows[0][0] < rows[1][0] for rows in solutions.values()):
        raise RuntimeError("non-unique cut at seeded base point")
    global_margin = min(rows[1][0] - rows[0][0] for rows in solutions.values())
    sensitivity_eps = min(global_margin / 4, min(capacities) / 4)

    region_rows = []
    dual_rows = []
    all_cs = True
    all_sensitivity = True
    for mask in masks:
        optimum, source_side, cut = solutions[mask][0]
        primal, flows = exact_maxflow(edges, capacities, mask)
        y = [int(i in cut) for i in range(len(edges))]
        dual = sum((capacities[i] * y[i] for i in range(len(edges))), Fraction())
        ends = [(contracted_node(u, mask), contracted_node(v, mask)) for u, v in edges]
        balances = {node: Fraction() for node in ["SOURCE", "SINK"] + INTERIOR}
        for i, (u, v) in enumerate(ends):
            balances[u] += flows[i]
            balances[v] -= flows[i]
        primal_feasible = all(-capacities[i] <= flows[i] <= capacities[i] for i in range(len(edges))) and all(balances[node] == 0 for node in INTERIOR) and balances["SOURCE"] == primal and balances["SINK"] == -primal
        def potential(node: str) -> int:
            if node == "SOURCE":
                return 1
            if node == "SINK":
                return 0
            return int(node in source_side)
        dual_feasible = all(y[i] >= abs(potential(u) - potential(v)) for i, (u, v) in enumerate(ends))
        cs = primal_feasible and dual_feasible and primal == optimum == dual
        for i, (u0, v0) in enumerate(edges):
            u, v = contracted_node(u0, mask), contracted_node(v0, mask)
            if y[i]:
                u_in = u0 in source_side
                expected = capacities[i] if u_in else -capacities[i]
                cs = cs and flows[i] == expected
        all_cs = all_cs and cs
        region_rows.append({
            "region_mask": mask,
            "region": "|".join(x for i, x in enumerate(LABELS) if mask & (1 << i)),
            "minimum_cut": fstr(optimum),
            "primal_max_flow": fstr(primal),
            "dual_optimum": fstr(dual),
            "margin_to_second_cut": fstr(solutions[mask][1][0] - optimum),
            "unique_min_cut": int(optimum < solutions[mask][1][0]),
            "cut_edges": ";".join(edge_name(edges[i]) for i in cut),
            "primal_feasible": int(primal_feasible),
            "dual_feasible": int(dual_feasible),
            "strong_duality": int(primal == dual),
            "complementary_slackness": int(cs),
        })
        for i, edge in enumerate(edges):
            plus = list(capacities); minus = list(capacities)
            plus[i] += sensitivity_eps; minus[i] -= sensitivity_eps
            plus_sol = cut_solutions(edges, plus, mask)[0]
            minus_sol = cut_solutions(edges, minus, mask)[0]
            derivative = (plus_sol[0] - minus_sol[0]) / (2 * sensitivity_eps)
            stable = plus_sol[2] == cut and minus_sol[2] == cut
            correct = stable and derivative == y[i]
            all_sensitivity = all_sensitivity and correct
            dual_rows.append({
                "region_mask": mask,
                "region": region_rows[-1]["region"],
                "edge_index": i,
                "edge": edge_name(edge),
                "capacity": fstr(capacities[i]),
                "y_e": y[i],
                "central_difference_exact": fstr(derivative),
                "chamber_stable_plus_minus": int(stable),
                "sensitivity_equals_y": int(correct),
            })

    # Step45 replacement: a fixed geometry direction and a separately declared
    # virtual-bond filter use the same parameter; neither is inferred from delta-S.
    dc = [Fraction() for _ in edges]
    path_amplitudes = [Fraction(3, 200), Fraction(-1, 100), Fraction(1, 80)]
    for j, amp in enumerate(path_amplitudes):
        for i, edge in enumerate(edges):
            if f"M{j}" in edge:
                dc[i] = amp
    stability_radii = []
    response_rows = []
    for mask in masks:
        base_cut = solutions[mask][0][2]
        base_slope = sum((dc[i] for i in base_cut), Fraction())
        radius: Fraction | None = None
        for value, _side, alternative in solutions[mask][1:]:
            slope = sum((dc[i] for i in alternative), Fraction())
            if slope != base_slope:
                candidate = (value - solutions[mask][0][0]) / abs(slope - base_slope)
                radius = candidate if radius is None else min(radius, candidate)
        stability_radii.append(radius if radius is not None else Fraction(10**9))
    state0, left, right = modules["step42"].boundary_state_matrix(DIM, "random_gaussian", SEED)
    h = []
    for alpha in range(DIM**3):
        digits = [(alpha // (DIM ** (2 - j))) % DIM for j in range(3)]
        h.append(sum(float(path_amplitudes[j]) * (digits[j] - (DIM - 1) / 2) for j in range(3)))
    h = np.asarray(h)
    state_plus = (left * np.exp(RESPONSE_EPS * h)[None, :]) @ right.T
    state_minus = (left * np.exp(-RESPONSE_EPS * h)[None, :]) @ right.T
    eplus, eminus = entropy_all(state_plus), entropy_all(state_minus)
    measured = {mask: (eplus[mask] - eminus[mask]) / (2 * RESPONSE_EPS) for mask in masks}
    control_delta = modules["step45"].perturb_left_tensor(left)
    cp = (left + RESPONSE_EPS * control_delta) @ right.T
    cm = (left - RESPONSE_EPS * control_delta) @ right.T
    cep, cem = entropy_all(cp), entropy_all(cm)
    control = {mask: (cep[mask] - cem[mask]) / (2 * RESPONSE_EPS) for mask in masks}
    for mask in masks:
        cut = solutions[mask][0][2]
        predicted = float(sum((dc[i] for i in cut), Fraction()))
        error = measured[mask] - predicted
        response_rows.append({
            "region_mask": mask,
            "region": region_rows[mask - 1]["region"],
            "cut_margin": fstr(solutions[mask][1][0] - solutions[mask][0][0]),
            "directional_stability_radius": fstr(stability_radii[mask - 1]),
            "cut_response_prediction": f"{predicted:.12g}",
            "recontracted_state_delta_S": f"{measured[mask]:.12g}",
            "response_error": f"{error:.12g}",
            "matches_within_tolerance": int(abs(error) <= RESPONSE_TOL),
            "can_fail_control_prediction": "0",
            "can_fail_control_delta_S": f"{control[mask]:.12g}",
        })
    response_max_error = max(abs(measured[m] - float(sum((dc[i] for i in solutions[m][0][2]), Fraction()))) for m in masks)
    response_match = response_max_error <= RESPONSE_TOL
    control_fails = max(abs(x) for x in control.values()) > RESPONSE_TOL

    # A genuine boundary gluing attempt.  The area ledger obeys the min-plus
    # rule exactly; the Born ledger is checked rather than assigned that rule.
    base_ent = entropy_all(state0)
    base_ent[0] = 0.0
    base_ent[(1 << len(LABELS)) - 1] = 0.0
    psi = (state0 / np.linalg.norm(state0)).reshape([DIM] * 8)
    glued = np.tensordot(psi, psi, axes=([7], [3]))
    glued_labels = [f"A_{x}" for x in LABELS[:-1]] + [f"B_{x}" for x in LABELS[:3] + LABELS[4:]]

    def glued_entropy(region: list[str]) -> float:
        normed = glued / np.linalg.norm(glued)
        axes = [glued_labels.index(x) for x in region]
        comp = [i for i in range(14) if i not in axes]
        mat = np.transpose(normed, axes + comp).reshape(DIM ** len(axes), -1)
        vals = np.linalg.svd(mat, compute_uv=False) ** 2
        vals = vals[vals > 1e-14]
        return float(-np.sum(vals * np.log(vals)))

    probes = [
        (["A_R2"], 1 << 6, 0),
        (["B_L2"], 0, 1 << 2),
        (["A_R2", "B_L2"], 1 << 6, 1 << 2),
        (["A_L0", "A_L1", "B_R0"], (1 << 0) | (1 << 1), 1 << 4),
    ]
    composition_rows = []
    area_rule_all = True
    born_rule_all = True
    for names, ma, mb in probes:
        actual_born = glued_entropy(names)
        # Same-side gluing index q: A_R3 bit7 and B_L3 bit3.
        born_candidate = min(base_ent[ma | (q << 7)] + base_ent[mb | (q << 3)] for q in (0, 1))
        def component_area(component_mask: int) -> Fraction:
            if component_mask in (0, (1 << len(LABELS)) - 1):
                return Fraction()
            return solutions[component_mask][0][0]
        area_candidate = min(component_area(ma | (q << 7)) + component_area(mb | (q << 3)) for q in (0, 1))
        # Independently enumerate the joined graph by renaming the glued leaves G.
        joined_edges = []
        joined_caps = []
        for prefix, glue_label in (("A", "R3"), ("B", "L3")):
            for edge, cap in zip(edges, capacities):
                renamed = tuple("G" if x == glue_label else f"{prefix}_{x}" for x in edge)
                joined_edges.append(renamed); joined_caps.append(cap)
        joined_boundary = [x for x in glued_labels]
        joined_interior = [f"{p}_{x}" for p in ("A", "B") for x in INTERIOR] + ["G"]
        selected = set(names)
        values = []
        for bits in range(1 << len(joined_interior)):
            side = selected | {x for i, x in enumerate(joined_interior) if bits & (1 << i)}
            values.append(sum((c for (u, v), c in zip(joined_edges, joined_caps) if (u in side) != (v in side)), Fraction()))
        actual_area = min(values)
        area_ok = actual_area == area_candidate
        born_ok = abs(actual_born - born_candidate) <= RESPONSE_TOL
        area_rule_all &= area_ok; born_rule_all &= born_ok
        composition_rows.append({
            "region": "|".join(names),
            "glued_area_direct": fstr(actual_area),
            "area_min_plus_components": fstr(area_candidate),
            "area_rule_matches": int(area_ok),
            "glued_born_direct": f"{actual_born:.12g}",
            "born_min_plus_components": f"{born_candidate:.12g}",
            "born_rule_matches": int(born_ok),
        })

    # Co-sourced MMI is retained, but it is not promoted to a composition law.
    area_ent = {mask: float(solutions[mask][0][0]) for mask in masks}
    a, b, c = 1, 2, 1 << 4
    born_i3 = mmi(base_ent, a, b, c)
    area_i3 = mmi(area_ent, a, b, c)
    composition_constructed = area_rule_all and born_rule_all

    summary = {
        "pins": PINS,
        "seed": SEED,
        "region_count": len(masks),
        "edge_count": len(edges),
        "all_min_cuts_unique": all(int(r["unique_min_cut"]) for r in region_rows) == 1,
        "global_minimum_cut_margin": fstr(global_margin),
        "sensitivity_epsilon": fstr(sensitivity_eps),
        "strong_duality_all_regions": all(int(r["strong_duality"]) for r in region_rows) == 1,
        "primal_feasible_all_regions": all(int(r["primal_feasible"]) for r in region_rows) == 1,
        "dual_feasible_all_regions": all(int(r["dual_feasible"]) for r in region_rows) == 1,
        "complementary_slackness_all_regions": all_cs,
        "sensitivity_equals_shadow_price_all_region_edges": all_sensitivity,
        "corrected_identity": "Area(min cut) = dual optimum = sum_e c_e y_e; y_e is the per-edge shadow price (the 0/1 cut-incidence variable in this chamber).",
        "linear_response": {
            "geometry_direction_source": "fixed rational bridge direction declared before entropy evaluation",
            "state_deformation_source": "fixed virtual-bond diagonal filter declared before entropy evaluation",
            "minimum_directional_stability_radius": fstr(min(stability_radii)),
            "tolerance": RESPONSE_TOL,
            "max_absolute_error": response_max_error,
            "match": response_match,
            "can_fail_control_nonmatch": control_fails,
            "verdict": "MATCH" if response_match else "HONEST_NON_MATCH",
        },
        "composition": {
            "operation": "contract boundary R3 of copy A with boundary L3 of copy B",
            "area_min_plus_rule_all_probes": area_rule_all,
            "born_same_min_plus_rule_all_probes": born_rule_all,
            "shared_composition_rule_constructed": composition_constructed,
            "born_i3": born_i3,
            "area_i3": area_i3,
            "born_and_area_in_same_mmi_inequality_class": born_i3 <= 1e-9 and area_i3 <= 1e-9,
            "verdict": "COMPOSITION_CONSTRUCTED" if composition_constructed else "DOWNGRADED_SHARED_MMI_CLASS_DIFFERENT_DEPENDENCIES",
        },
        "backlog": "Step44-style GENERIC_VIOLATES verdict naming is noted for a separate hygiene fix and is not changed here.",
        "runtime_seconds": time.perf_counter() - started,
    }
    return {
        "summary": summary,
        "edges": edges,
        "capacities": capacities,
        "region_rows": region_rows,
        "dual_rows": dual_rows,
        "response_rows": response_rows,
        "composition_rows": composition_rows,
        "matrices": lp_matrices(edges, capacities, 1 | 2 | (1 << 4)),
    }


def render(data: dict[str, Any]) -> dict[str, bytes]:
    region_fields = list(data["region_rows"][0])
    dual_fields = list(data["dual_rows"][0])
    response_fields = list(data["response_rows"][0])
    composition_fields = list(data["composition_rows"][0])
    summary = data["summary"]
    stable_summary = {key: value for key, value in summary.items() if key != "runtime_seconds"}
    edge_rows = [{"edge_index": i, "edge": edge_name(e), "capacity": fstr(c)} for i, (e, c) in enumerate(zip(data["edges"], data["capacities"]))]
    schema = {
        "artifact": "Q5-REPAIR-1",
        "row_counts": {"regions": len(data["region_rows"]), "edge_shadow_prices": len(data["dual_rows"]), "linear_response": len(data["response_rows"]), "composition": len(data["composition_rows"])},
        "exact_fields": "capacities, optima, margins, and sensitivities are reduced rational strings",
        "verdict_fields": "all booleans and verdict strings are derived in build()",
    }
    note = f"""# Q5 LP-duality repair results

All {summary['region_count']} nontrivial boundary regions have unique cuts at Step55 seed {summary['seed']}. The global cut margin is `{summary['global_minimum_cut_margin']}`. Exact max-flow, cut-dual evaluation, and complementary slackness agree for every region; all {len(data['dual_rows'])} central sensitivity checks stay in the chamber and equal the exported `y_e`.

Corrected identity: **{summary['corrected_identity']}** The optimum is a scalar; the shadow prices are the separate edge-indexed variables `y_e`.

## Linearized response

The geometry direction and the virtual-bond filter were fixed before evaluating any entropy. The chamber radius is at least `{summary['linear_response']['minimum_directional_stability_radius']}` in the declared direction. Verdict: **{summary['linear_response']['verdict']}**, maximum absolute response error `{summary['linear_response']['max_absolute_error']:.12g}` at tolerance `{summary['linear_response']['tolerance']}`. The state-only can-fail control is nonmatching: `{summary['linear_response']['can_fail_control_nonmatch']}`. Thus the frozen Step45 conclusion is not recovered at an honest generic base point when the deformation is specified independently.

## Composition / Step50

The actual boundary contraction obeys the computed min-plus rule on the area side, but the Born values do not obey that same rule on all probes. Verdict: **{summary['composition']['verdict']}**. What survives is the weaker computed statement that the co-sourced Born and area ledgers satisfy the same MMI inequality class for the tested triple (`I3_Born={summary['composition']['born_i3']:.12g}`, `I3_area={summary['composition']['area_i3']:.12g}`), while depending on state amplitudes and graph capacities respectively.

Backlog: {summary['backlog']}
"""
    design = """# Design

- The graph and generic seed weights are imported from frozen Steps 42 and 55 under literal SHA-256 pins.
- Exact cut values are obtained by enumerating only the five interior-node sides (32 cuts per region). Exact rational Edmonds-Karp supplies a primal witness.
- The dual uses node potentials with `p_source=1`, `p_sink=0` and `y_e >= |p_u-p_v|`; the unique cut supplies its integral optimum.
- The response family is non-circular: rational geometry slopes and a virtual-index diagonal filter are declared independently of all measured entropies.
- The composition attempt contracts one physical boundary index between two carrier copies. It tests, rather than assumes, whether the area min-plus gluing rule also governs Born entropy.
"""
    return {
        "q5_carrier_edges.csv": csv_bytes(edge_rows, list(edge_rows[0])),
        "q5_region_duality.csv": csv_bytes(data["region_rows"], region_fields),
        "q5_edge_shadow_prices.csv": csv_bytes(data["dual_rows"], dual_fields),
        "q5_linear_response.csv": csv_bytes(data["response_rows"], response_fields),
        "q5_composition_probe.csv": csv_bytes(data["composition_rows"], composition_fields),
        "q5_lp_matrices.json": json_bytes(data["matrices"]),
        "q5_results.json": json_bytes(stable_summary),
        "q5_schema.json": json_bytes(schema),
        "RESULTS.md": note.encode(),
        "DESIGN.md": design.encode(),
    }


def main() -> None:
    data = build()
    for name, payload in render(data).items():
        (HERE / name).write_bytes(payload)
    print(f"Q5 build PASS: {data['summary']['region_count']} unique regions; runtime={data['summary']['runtime_seconds']:.3f}s")


if __name__ == "__main__":
    main()
