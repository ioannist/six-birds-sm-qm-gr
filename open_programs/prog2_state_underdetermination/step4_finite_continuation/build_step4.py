#!/usr/bin/env python3
"""Render deterministic PROG2 Step-4 FIX2 artifacts."""
from __future__ import annotations
import csv, io, json
from pathlib import Path
from typing import Any
from step4_core import compute_all

HERE = Path(__file__).resolve().parent

def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows: return ""
    stream = io.StringIO(newline=""); writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
    writer.writeheader(); writer.writerows(rows); return stream.getvalue()

def results_markdown(data: dict[str, Any]) -> str:
    lines = [
        "# PROG2 Step 4 — complete-kernel continuation and generated-gauge audit", "",
        "## Certified construction", "",
        "Six exact-algebraic finite continuation candidates have identical complete cut fingerprints and identical "
        "connected-copy boundary states but distinct raw capacities. The exact endpoints, product equalities, all "
        "254 ordered-region fingerprints, positive uniqueness margins, and connected-copy state equality survive "
        "FIX2. The AM–GM statement remains only the tangent-plane lemma.", "",
        "## Combined generated-gauge closure", "",
        "The closure now uses one worklist containing all five graph moves, every single-edge reciprocal/basis swap, "
        "and terminal-fixed exact weighted canonicalization after every step. Weights are general elements of "
        "`QQ(alpha)` represented as polynomials modulo each endpoint's exported algebraic polynomial; inversion and "
        "sign decisions are exact, including the degree-five field for `cand_06`.", "",
        "No finiteness theorem is available: reciprocal and graph moves can alternate indefinitely. The frozen safety "
        "budget is 64 canonical states and 20 wall-clock seconds per endpoint. Every endpoint reaches the state cap, "
        "so every pair is honestly budget-truncated.", "",
        "| id | field degree | base states/processed | displaced states/processed | intersection | closure verdict | signature status | typed outcome |",
        "|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in data["candidate_outcomes"]:
        lines.append(
            f"| {row['candidate_id']} | {row['endpoint_number_field_degree']} | "
            f"{row['base_combined_orbit_state_count']}/{row['base_combined_processed_state_count']} | "
            f"{row['displaced_combined_orbit_state_count']}/{row['displaced_combined_processed_state_count']} | "
            f"{row['combined_orbit_intersection_count']} | {row['combined_closure_verdict']} | "
            f"{row['capacity_invariant_status']} | **{row['typed_outcome']}** |"
        )
    lines += [
        "", "No pair collapsed to gauge in the explored combined closures. This is only "
        "`DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED`, not generated-gauge inequivalence. Paths would be "
        "exported if an intersection occurred.", "", "## Reciprocal-first canary", "",
        "| base | reciprocal edge | new proposals | accepted exact moves |",
        "|---|---:|---:|---:|",
    ]
    for row in data["reciprocal_first_canary"]:
        lines.append(f"| {row['candidate_id']} | {row['edge_index']} | {row['proposal_count']} | {row['accepted_count']} |")
    lines += [
        "", "On `cand_03` base, reciprocal edges 3, 5, 6, and 11 expose the reviewer-pinned "
        "zero-column/inseparable moves. All are full-fingerprint checked and accepted by the same combined engine; "
        "the old abort behavior is gone.", "", "## Invariant status", "",
        "The earlier five-move-orbit-plus-detached-reciprocal signature is withdrawn: it was not invariant under "
        "alternating generator compositions. FIX2 records a capacity-multiset signature over the **explored combined "
        "orbit** only. The explored signatures differ for all six pairs, but because each closure is truncated this "
        "is explicitly `NOT_AN_INVARIANT_PROOF`. The two affected obligations per pair—generated gauge closure and "
        "bulk invariant—are therefore `PENDING_GENERATED_GAUGE_CLOSURE` (12 pending obligations total).", "",
        "## Outcome", "",
        "All six objects remain exact-algebraic finite continuation **candidates**. None is currently certified as "
        "bulk-inequivalent under the generated gauge relation, and no surviving underdetermination claim is made. "
        "The open obstruction is saturation or a separately proved generator-by-generator invariant.", "",
    ]
    return "\n".join(lines)

def schema(data: dict[str, Any]) -> dict[str, Any]:
    pending = sum(row["status"] == "PENDING_GENERATED_GAUGE_CLOSURE" for row in data["endpoint_obligations"])
    return {
        "artifact": "PROG2_STEP4_FIX2_GENERATED_GAUGE_CLOSURE", "version": 3,
        "aggregate_verdict": data["aggregate_verdict"],
        "exact_continuation_candidate_count": 6, "certified_surviving_candidate_count": 0,
        "combined_generator_set": ["series", "two_terminal_module", "saturated_or_zero_column",
            "inseparable_contraction", "delta_y_y_delta", "single_edge_reciprocal",
            "terminal_fixed_weighted_canonicalization"],
        "number_field_representation": "polynomial residues in QQ(alpha) modulo exported minimal polynomial",
        "number_field_degrees": sorted({row["endpoint_number_field_degree"] for row in data["candidate_outcomes"]}),
        "budgets": {"canonical_state_cap_per_endpoint": 64, "wall_seconds_per_endpoint": 20},
        "all_closures_saturated": False, "pending_generated_gauge_obligation_count": pending,
        "invariant": {"name": "explored-combined-orbit capacity multiset signature",
            "proof_status": "NOT_AN_INVARIANT_PROOF_WHILE_BUDGET_TRUNCATED"},
        "grades": {"continuation_product_fingerprint": "EXACT_ALGEBRAIC",
            "connected_copy_state_equality": "EXACT_ANALYTIC_PLUS_DENSE_NUMERICAL_RECONTRACTION",
            "generated_gauge_inequivalence": "PENDING_BUDGET_TRUNCATED",
            "bulk_invariant": "PENDING_BUDGET_TRUNCATED"},
        "files": {"candidate_outcomes_step4.csv": "six endpoints and combined-closure verdicts",
            "reciprocal_first_canary_step4.csv": "reviewer-pinned generated-move regression",
            "endpoint_obligations_step4.csv": "60 typed obligations including 12 pending",
            "root_attempts_step4.csv": "exact root selection", "anti_bypass_step4.csv": "structural gates",
            "dependency_pins_step4.csv": "read-only dependency and preregistration pins"},
    }

CONTENT = """# Content classification

| object | classification |
|---|---|
| six nonzero endpoints, products, fingerprints | exact algebraic |
| connected-copy boundary-state equality | exact analytic, independently recontracted numerically |
| `QQ(alpha)` arithmetic including inverses | exact number-field computation |
| combined generated-gauge worklists | exact but budget-truncated |
| explored capacity signatures | exact diagnostics, not invariant proofs under truncation |
| bulk inequivalence | pending generated-gauge closure |
| underdetermination objects | candidates, not certified surviving examples |
"""

NONCLAIM = """# Nonclaim boundary

Six exact-algebraic finite continuation candidates have identical complete cut fingerprints and identical connected-
copy boundary states but distinct raw capacities. The combined gauge search finds no intersection within the explored
sets, but every endpoint hits the 64-state cap. Deeper alternating reciprocal/graph-move sequences remain open.

The explored capacity signatures differ but are not proved invariants of the unsaturated generated relation. Thus no
candidate is certified bulk-inequivalent and no state-level bulk-underdetermination theorem is claimed. Other tensor
families, capacity conventions, undeclared transformations, continuum limits, and universal physical quotients also
remain outside scope.
"""

STATEMENT = """# Step-4 FIX2 statement

Six exact-algebraic finite continuation candidates have identical complete cut fingerprints and identical connected-
copy boundary states but distinct raw capacities. A general exact `QQ(alpha)` engine closes one worklist under all five
declared graph moves, every single-edge reciprocal, and terminal-fixed canonicalization. For each pair the explored
base and displaced sets are disjoint, but all twelve endpoint searches hit the 64-state budget.

The per-pair verdict is `DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED`; generated-gauge inequivalence is pending.
The explored capacity signatures differ but are not invariant proofs without saturated closure. Accordingly all six
remain candidates, with twelve obligations typed `PENDING_GENERATED_GAUGE_CLOSURE`; no surviving underdetermination
example is certified by this step.
"""

def render(data: dict[str, Any]) -> dict[str, str]:
    return {"results_step4.md": results_markdown(data),
        "schema_step4.json": json.dumps(schema(data), indent=2, sort_keys=True)+"\n",
        "content_classification.md": CONTENT, "nonclaim_boundary.md": NONCLAIM, "statement.md": STATEMENT,
        "candidate_outcomes_step4.csv": csv_text(data["candidate_outcomes"]),
        "root_attempts_step4.csv": csv_text(data["root_attempts"]),
        "endpoint_obligations_step4.csv": csv_text(data["endpoint_obligations"]),
        "reciprocal_first_canary_step4.csv": csv_text(data["reciprocal_first_canary"]),
        "anti_bypass_step4.csv": csv_text(data["anti_bypass"]),
        "dependency_pins_step4.csv": csv_text(data["dependency_pins"])}

def generate(destination: Path) -> dict[str, str]:
    artifacts = render(compute_all()); destination.mkdir(parents=True, exist_ok=True)
    for name,text in artifacts.items(): (destination/name).write_text(text,encoding="utf-8")
    return artifacts

if __name__ == "__main__":
    artifacts=generate(HERE); print(f"build_step4.py: PASS: wrote={len(artifacts)} exact_candidates=6 pending_generated_gauge_obligations=12")
