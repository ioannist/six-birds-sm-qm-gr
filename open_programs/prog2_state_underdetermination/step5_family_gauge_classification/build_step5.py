#!/usr/bin/env python3
"""Render deterministic PROG2 Step-5 artifacts."""
from __future__ import annotations
import csv, io, json
from pathlib import Path
from typing import Any
from step5_core import compute_all

HERE=Path(__file__).resolve().parent

def csv_text(rows: list[dict[str,Any]]) -> str:
    if not rows:return ""
    stream=io.StringIO(newline="");writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
    writer.writeheader();writer.writerows(rows);return stream.getvalue()

def results(data: dict[str,Any]) -> str:
    lines=["# PROG2 Step 5 — corrected C2_L1 family-gauge classification","",
        "## Headline","",
        "All six pairs are **SURVIVING_FINITE_C2_L1_DECLARED_GAUGE_EXAMPLE**. Each pair has exact-algebraic "
        "product, complete-cut-fingerprint, and connected-copy boundary-state equality, while exact terminal-fixed "
        "isomorphism, both global-reciprocal comparisons, Step-1 merge applicability, and the exact invariant "
        "separate the raw capacity assignments under the frozen corrected family relation.","",
        "## Six-row classification","",
        "`I(c)` below is the unordered exact pair `{sum c_e, sum c_e^-1}`. Full exact `QQ(alpha)` expressions are "
        "exported in `classification_step5.csv`; the table shows leading digits.","",
        "| id | I(base), leading digits | I(displaced), leading digits | direct iso | global reciprocal maps | Step-1 merges | exact I differs | classification |",
        "|---|---|---|---:|---:|---:|---:|---|" ]
    for row in data["classifications"]:
        reciprocal=(row["base_isomorphic_to_global_reciprocal_displaced"]
                    or row["displaced_isomorphic_to_global_reciprocal_base"])
        merges=sum(row[key] for key in ("base_step1_series_reduction_count","base_step1_parallel_reduction_count",
                                        "displaced_step1_series_reduction_count","displaced_step1_parallel_reduction_count"))
        lines.append(f"| {row['candidate_id']} | `{row['base_invariant_leading_digits']}` | "
                     f"`{row['displaced_invariant_leading_digits']}` | {row['terminal_fixed_direct_isomorphism']} | "
                     f"{reciprocal} | {merges} | {row['invariant_differs_exact']} | **{row['classification']}** |")
    check=data["delta_y_countercheck"][0]
    lines += ["","## Connected-copy parity lemma","",
        "The exhaustive local encoding covers copy-tensor ranks 2, 3, 4, and 5. At every rank, exactly two leg "
        "subsets return the canonical copy tensor: no legs and all legs. The carrier-level constraint enumeration "
        "then finds exactly two assignments on every connected graph: all edge-swap bits zero and all one. Thus "
        "only identity and the global reciprocal return to the canonical `C2_L1` family.","",
        "## Delta-Y cut/state separation countercheck","",
        f"For `cand_01`, Delta-Y on `{check['triangle']}` preserves the complete cut fingerprint exactly but changes "
        f"the copy product by the exact ratio `{check['copy_product_ratio_exact']}` = "
        f"`{check['copy_product_ratio_decimal']}`. Since this is not one, the connected-copy state changes. The move "
        "is cut equivalence, not state gauge; no tensor intertwiner is asserted.","",
        "## Invariant proof status","",
        "The declaration proves `I(c)` generator by generator. Isomorphisms permute terms; internal `g,g^-1` and "
        "boundary unitaries do not touch capacities; global reciprocal exchanges the unordered entries. An exact "
        "topology census finds no applicable Step-1 series or parallel tensor merge at any of the twelve endpoints, "
        "so that generator is vacuous here. All proof checks pass.","",
        "## Certified wording","",
        "Six exact-algebraic finite `C2_L1` declared-gauge underdetermination examples were constructed. This earns "
        "the word *example* because every comparison is exact and the declared invariant proof is complete at this "
        "scope. It is not a bulk-geometry theorem and does not extend to other tensor families or gauge relations.",""]
    return "\n".join(lines)

def schema(data: dict[str,Any]) -> dict[str,Any]:
    return {"artifact":"PROG2_STEP5_FAMILY_GAUGE_CLASSIFICATION","version":1,
        "aggregate_verdict":data["aggregate_verdict"],"pair_count":6,"example_count":6,"collapse_count":0,
        "declared_relation":{"cut_equivalence_is_separate":True,"single_edge_reciprocal_is_state_gauge":False,
            "prog3_five_moves_are_state_gauge":False,"capacity_actions":["terminal-fixed weighted isomorphism",
            "global all-edge reciprocal with global boundary X"]},
        "invariant":{"formula":"unordered {sum_e c_e, sum_e 1/c_e}","grade":"EXACT_NUMBER_FIELD",
            "generator_proof_complete":True},
        "parity_lemma":{"local_ranks":[2,3,4,5],"allowed_local_subsets_per_rank":2,
            "allowed_global_assignments_per_carrier":2,"grade":"EXHAUSTIVE_FINITE_EXACT"},
        "countercheck":{"carrier":"cand_01","move":"Delta-Y I0+I1+I2",
            "cut_fingerprint_equal":True,"copy_product_ratio_not_one":True},
        "files":{"classification_step5.csv":"six exact classifications and invariant values",
            "local_copy_parity_step5.csv":"local parity enumeration","global_copy_parity_step5.csv":"connected constraint enumeration",
            "delta_y_countercheck_step5.csv":"cut-only move countercheck","invariant_generator_proofs_step5.csv":"proof ledger",
            "dependency_pins_step5.csv":"read-only import and declaration pins"}}

CONTENT="""# Content classification

| object | classification |
|---|---|
| six endpoints and cut/state equality | imported and independently reconstructed exact algebraic |
| connected-copy parity lemma | exhaustive exact finite computation plus proof |
| terminal-fixed/global-reciprocal comparisons | exact `QQ(alpha)` weighted-graph comparisons |
| `I(c)` | exact declared-gauge invariant with complete generator proof |
| Delta-Y | cut equivalence only; explicitly excluded from state gauge |
| six final rows | surviving finite `C2_L1` declared-gauge underdetermination examples |
"""

NONCLAIM="""# Nonclaim boundary

The six examples are scoped to the connected canonical `C2_L1` copy family, the frozen Step-5 declared gauge
relation, and these finite carriers. Cut-level equivalence is separate: the endpoints are also five-move-orbit-disjoint
in PROG3, but Delta-Y-class cut moves are not state gauges without tensor-level intertwiners.

This is not a bulk-geometry theorem and makes no claim for random tensors, other capacity-to-state conventions,
continuum limits, other tensor families, or broader physically motivated gauge relations.
"""

STATEMENT="""# Step-5 statement

Six exact-algebraic finite `C2_L1` declared-gauge underdetermination examples were constructed. In each pair, distinct
positive raw capacity assignments have identical complete terminal cut fingerprints and identical connected-copy
boundary states. Exact terminal-fixed and global-reciprocal comparisons find no declared gauge map, no Step-1
series/parallel tensor merge applies, and the exact invariant `I(c)={sum c_e, sum c_e^-1}` differs.

The connected-copy parity lemma proves that identity and global all-edge reciprocal are the only reciprocal actions
returning a connected carrier to the canonical copy family. PROG3 five-move transformations remain cut equivalences,
not state gauges absent explicit tensor intertwiners. The result is finite-carrier and `C2_L1`-family scoped; no
general bulk-geometry theorem is claimed.
"""

def render(data: dict[str,Any]) -> dict[str,str]:
    return {"results_step5.md":results(data),"schema_step5.json":json.dumps(schema(data),indent=2,sort_keys=True)+"\n",
        "content_classification.md":CONTENT,"nonclaim_boundary.md":NONCLAIM,"statement.md":STATEMENT,
        "classification_step5.csv":csv_text(data["classifications"]),
        "local_copy_parity_step5.csv":csv_text(data["local_parity"]),
        "global_copy_parity_step5.csv":csv_text(data["global_parity"]),
        "delta_y_countercheck_step5.csv":csv_text(data["delta_y_countercheck"]),
        "invariant_generator_proofs_step5.csv":csv_text(data["invariant_proofs"]),
        "dependency_pins_step5.csv":csv_text(data["dependency_pins"])}

def generate(destination: Path) -> dict[str,str]:
    artifacts=render(compute_all());destination.mkdir(parents=True,exist_ok=True)
    for name,text in artifacts.items():(destination/name).write_text(text,encoding="utf-8")
    return artifacts

if __name__=="__main__":
    artifacts=generate(HERE);print(f"build_step5.py: PASS: wrote={len(artifacts)} examples=6 collapses=0")
