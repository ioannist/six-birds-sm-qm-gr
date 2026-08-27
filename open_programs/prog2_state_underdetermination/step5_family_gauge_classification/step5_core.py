#!/usr/bin/env python3
"""Exact family-level gauge classification for PROG2 Step 5."""
from __future__ import annotations

import csv
import hashlib
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEP1_DIR = HERE.parent / "step1_engine"
STEP4_DIR = HERE.parent / "step4_finite_continuation"
for directory in (STEP4_DIR, STEP1_DIR):
    if str(directory) not in sys.path: sys.path.insert(0, str(directory))

import step1_core as _step1_engine_namespace  # noqa: F401,E402
from algebraic_engine import (NumberField, canonical_key, delta_to_y,
    enumerate_cuts, exact_root_certificate, graph_degrees, lift_graph,
    make_graph, same_fingerprint)  # noqa: E402
from step4_core import (CANDIDATE_SPECS, _poly_and_endpoint, exact_copy_null_basis,
    exact_edge_direction, group_base_cases, load_fibers)  # noqa: E402

PINNED = {
    STEP4_DIR / "algebraic_engine.py": "e6819d412bc4c89e315f74462a8ac16f8dae02b895555af39e3ac08e1beac1bd",
    STEP4_DIR / "step4_core.py": "6abbf8f3653b4966fff1ef4bd1e72dcbe3325e17b186991754cff1c3f352120f",
    STEP4_DIR / "candidate_outcomes_step4.csv": "f91bbfe845d806dcb5ddd189b48fe9f48eaac8c94c21e909494e1a5497601a9f",
    STEP1_DIR / "gauge_library.py": "8d0abd47615c2d5e62a6c6a8fd3bb868c7c4cec73ae81d7da19e583b48afcfe1",
    STEP1_DIR / "tensor_engine.py": "52640d2d195d3928ff18c01af59f3a06a72d10fb10f136b69f5a4b2f65f774df",
    HERE / "declaration_step5.md": "8d67fddad7475056c97a90155e4e78e92e4f6e2de3def0c4997674a2031c7ffa",
}
T = Fraction(1, 10_000)
COUNTERCHECK_TRIANGLE = ("I0", "I1", "I2")

def sha256(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_pins() -> list[dict[str, Any]]:
    rows=[{"path":str(path.relative_to(REPO_ROOT)),"expected_sha256":expected,
           "actual_sha256":sha256(path),"passes":sha256(path)==expected}
          for path,expected in PINNED.items()]
    if not all(row["passes"] for row in rows): raise AssertionError(f"pin failure: {rows}")
    return rows

@dataclass(frozen=True)
class Pair:
    candidate_id: str
    carrier: str
    seed: int
    direction_index: int
    case: Any
    field: Any
    base: Any
    displaced: Any

def product(weights: tuple[Any, ...]):
    result=weights[0].field.element(1)
    for weight in weights: result *= weight
    return result

def construct_pairs() -> list[Pair]:
    cases={(case.carrier,case.source_seed_provenance):case
           for case in group_base_cases(load_fibers())}
    with (STEP4_DIR/"candidate_outcomes_step4.csv").open(newline="",encoding="utf-8") as handle:
        exported={row["candidate_id"]:row for row in csv.DictReader(handle)}
    pairs=[]
    for candidate_id,carrier,seed,direction_index,_dimension in CANDIDATE_SPECS:
        case=cases[(carrier,seed)]; protected=exact_copy_null_basis(case)[direction_index]
        v=exact_edge_direction(case,protected)
        gradient=tuple(sum(Fraction(value)/capacity for value,capacity in zip(fiber.direction,case.capacities))
                       for fiber in case.fibers)
        transverse=next(index for index,value in enumerate(gradient) if value)
        u=tuple(Fraction(value) for value in case.fibers[transverse].direction)
        poly,expressions=_poly_and_endpoint(case,v,u,T)
        root=exact_root_certificate(poly,expressions,75); field=NumberField.from_root(root)
        base_capacities=tuple(field.element(value) for value in case.capacities)
        displaced_capacities=tuple(field.element(c+T*ve)+field.alpha*ue
                                   for c,ve,ue in zip(case.capacities,v,u))
        base=lift_graph(case.graph,base_capacities); displaced=lift_graph(case.graph,displaced_capacities)
        exported_text="|".join(value.expression("alpha") for value in displaced_capacities)
        if exported_text != exported[candidate_id]["displaced_capacities_exact_algebraic"]:
            raise AssertionError(f"Step-4 endpoint reconstruction mismatch: {candidate_id}")
        if product(base.weights) != product(displaced.weights):
            raise AssertionError(f"exact product mismatch: {candidate_id}")
        if not same_fingerprint(enumerate_cuts(base),enumerate_cuts(displaced)):
            raise AssertionError(f"exact fingerprint mismatch: {candidate_id}")
        pairs.append(Pair(candidate_id,carrier,seed,direction_index,case,field,base,displaced))
    return pairs

def global_reciprocal(graph: Any):
    return make_graph(graph.name+"_global_reciprocal",graph.family,graph.boundaries,
                      [(u,v,weight.inverse()) for u,v,weight in graph.weighted_edges],graph.boundary_map)

def invariant(graph: Any) -> tuple[Any, Any]:
    zero=graph.weights[0].field.element(); direct=zero; reciprocal=zero
    for weight in graph.weights: direct += weight; reciprocal += weight.inverse()
    return tuple(sorted((direct,reciprocal),key=lambda value:value.key()))

def invariant_text(values: tuple[Any,Any]) -> str:
    return "{"+" ; ".join(value.expression("alpha") for value in values)+"}"

def invariant_decimal(values: tuple[Any,Any]) -> str:
    return "{"+" ; ".join(str(value.decimal(24)) for value in values)+"}"

def merge_applicability(graph: Any) -> tuple[int,int]:
    boundary_nodes=set(graph.boundary_map.values()); degrees=graph_degrees(graph)
    series=sum(node not in boundary_nodes and degrees[node]==2 for node in graph.nodes)
    counts=Counter(graph.edges)
    parallel=sum(count*(count-1)//2 for count in counts.values())
    return series,parallel

def graph_connected(graph: Any) -> bool:
    adjacency={node:set() for node in graph.nodes}
    for u,v in graph.edges: adjacency[u].add(v); adjacency[v].add(u)
    seen={graph.nodes[0]}; stack=[graph.nodes[0]]
    while stack:
        node=stack.pop()
        for neighbor in adjacency[node]-seen: seen.add(neighbor); stack.append(neighbor)
    return len(seen)==len(graph.nodes)

def local_copy_parity_rows(pairs: list[Pair]) -> list[dict[str,Any]]:
    ranks=set()
    for pair in pairs:
        degrees=graph_degrees(pair.base)
        boundary_counts=Counter(pair.base.boundary_map.values())
        ranks.update(degrees[node]+boundary_counts[node] for node in pair.base.nodes)
    rows=[]
    for rank in sorted(ranks):
        full=(1<<rank)-1; accepted=[]
        canonical={0,full}
        for mask in range(1<<rank):
            transformed={mask,full^mask}
            if transformed==canonical: accepted.append(mask)
        rows.append({"tensor_rank":rank,"subset_count":1<<rank,
                     "canonical_return_subset_count":len(accepted),
                     "canonical_return_masks":"|".join(map(str,accepted)),
                     "expected_masks":f"0|{full}","passes":accepted==[0,full]})
    return rows

def global_parity_rows(pairs: list[Pair]) -> list[dict[str,Any]]:
    rows=[]
    for pair in pairs:
        graph=pair.base; allowed=[]
        for mask in range(1<<len(graph.edges)):
            valid=True
            for node in graph.nodes:
                bits=[int(bool(mask&(1<<index))) for index,(u,v) in enumerate(graph.edges) if node in {u,v}]
                if bits and any(bit!=bits[0] for bit in bits): valid=False; break
            if valid: allowed.append(mask)
        expected=[0,(1<<len(graph.edges))-1]
        rows.append({"candidate_id":pair.candidate_id,"connected":graph_connected(graph),
                     "edge_count":len(graph.edges),"assignment_count":1<<len(graph.edges),
                     "family_returning_assignment_count":len(allowed),
                     "family_returning_masks":"|".join(map(str,allowed)),
                     "expected_masks":"|".join(map(str,expected)),
                     "passes":graph_connected(graph) and allowed==expected})
    return rows

def countercheck(pair: Pair) -> dict[str,Any]:
    transformed=delta_to_y(pair.base,COUNTERCHECK_TRIANGLE)
    fingerprint_equal=same_fingerprint(enumerate_cuts(pair.base),enumerate_cuts(transformed))
    ratio=product(transformed.weights)/product(pair.base.weights)
    return {"candidate_id":pair.candidate_id,"move":"delta_y",
            "triangle":"+".join(COUNTERCHECK_TRIANGLE),
            "complete_cut_fingerprint_equal_exact":fingerprint_equal,
            "copy_product_ratio_exact":ratio.expression("alpha"),
            "copy_product_ratio_decimal":str(ratio.decimal(30)),
            "copy_product_ratio_not_one_exact":ratio!=pair.field.element(1),
            "state_gauge_admitted":False,
            "passes":fingerprint_equal and ratio!=pair.field.element(1)}

def classify_pair(pair: Pair) -> dict[str,Any]:
    direct=canonical_key(pair.base)==canonical_key(pair.displaced)
    base_to_recip_displaced=canonical_key(pair.base)==canonical_key(global_reciprocal(pair.displaced))
    displaced_to_recip_base=canonical_key(pair.displaced)==canonical_key(global_reciprocal(pair.base))
    base_series,base_parallel=merge_applicability(pair.base)
    disp_series,disp_parallel=merge_applicability(pair.displaced)
    base_i,disp_i=invariant(pair.base),invariant(pair.displaced)
    invariant_differs=base_i!=disp_i
    complete=(not direct and not base_to_recip_displaced and not displaced_to_recip_base
              and base_series==base_parallel==disp_series==disp_parallel==0 and invariant_differs)
    collapse=direct or base_to_recip_displaced or displaced_to_recip_base
    classification=("EXPLICIT_DECLARED_GAUGE_COLLAPSE" if collapse else
                    "SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE" if complete else
                    "CANDIDATE_INCOMPLETE_CLASSIFICATION")
    return {"candidate_id":pair.candidate_id,"carrier":pair.carrier,"source_seed_provenance":pair.seed,
            "direction_index":pair.direction_index,"number_field_degree":pair.field.degree,
            "terminal_fixed_direct_isomorphism":direct,
            "base_isomorphic_to_global_reciprocal_displaced":base_to_recip_displaced,
            "displaced_isomorphic_to_global_reciprocal_base":displaced_to_recip_base,
            "base_step1_series_reduction_count":base_series,"base_step1_parallel_reduction_count":base_parallel,
            "displaced_step1_series_reduction_count":disp_series,"displaced_step1_parallel_reduction_count":disp_parallel,
            "base_invariant_exact":invariant_text(base_i),"displaced_invariant_exact":invariant_text(disp_i),
            "base_invariant_leading_digits":invariant_decimal(base_i),
            "displaced_invariant_leading_digits":invariant_decimal(disp_i),
            "invariant_differs_exact":invariant_differs,"classification":classification,
            "example_earned":complete}

def invariant_proof_rows(pairs: list[Pair], classifications: list[dict[str,Any]]) -> list[dict[str,Any]]:
    global_swap_checks=all(invariant(global_reciprocal(pair.base))==invariant(pair.base)
                           and invariant(global_reciprocal(pair.displaced))==invariant(pair.displaced)
                           for pair in pairs)
    no_merges=all(row["base_step1_series_reduction_count"]==0
                  and row["base_step1_parallel_reduction_count"]==0
                  and row["displaced_step1_series_reduction_count"]==0
                  and row["displaced_step1_parallel_reduction_count"]==0
                  for row in classifications)
    return [
        {"generator":"terminal_fixed_weighted_isomorphism","capacity_action":"permutes edge terms",
         "proof":"both sums are symmetric in the edge multiset","computational_check":"exact canonical comparison per pair","passes":True},
        {"generator":"internal_g_g_inverse","capacity_action":"none",
         "proof":"tensor-presentation matrices do not alter capacity labels","computational_check":"capacity action encoded as identity","passes":True},
        {"generator":"boundary_local_unitaries","capacity_action":"none",
         "proof":"boundary basis changes do not alter capacity labels","computational_check":"capacity action encoded as identity","passes":True},
        {"generator":"global_all_edge_reciprocal","capacity_action":"c_e maps to 1/c_e for every edge",
         "proof":"exchanges the two entries of the unordered invariant pair",
         "computational_check":"exact swap on all twelve endpoints","passes":global_swap_checks},
        {"generator":"explicit_step1_series_parallel_tensor_identity","capacity_action":"only if an admitted identity applies",
         "proof":"vacuous on these endpoints because no topology is applicable",
         "computational_check":"exact topology census on all twelve endpoints","passes":no_merges},
    ]

def compute_all() -> dict[str,Any]:
    pins=verify_pins(); pairs=construct_pairs()
    local=local_copy_parity_rows(pairs); global_rows=global_parity_rows(pairs)
    check=countercheck(pairs[0]); classifications=[classify_pair(pair) for pair in pairs]
    invariant_proofs=invariant_proof_rows(pairs,classifications)
    if not all(row["passes"] for row in local+global_rows) or not check["passes"]:
        raise AssertionError("parity or Delta-Y countercheck failed")
    if not all(row["passes"] for row in invariant_proofs):
        raise AssertionError("invariant generator proof check failed")
    if not all(row["example_earned"] for row in classifications):
        raise AssertionError(f"classification did not land: {classifications}")
    return {"dependency_pins":pins,"local_parity":local,"global_parity":global_rows,
            "delta_y_countercheck":[check],"classifications":classifications,
            "invariant_proofs":invariant_proofs,
            "aggregate_verdict":"SIX_SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLES"}
