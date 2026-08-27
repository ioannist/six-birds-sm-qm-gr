#!/usr/bin/env python3
"""Render deterministic PROG3 Step-3 artifacts."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from step3_core import FLOOR_VERDICT, UPGRADE_VERDICT, compute_all


HERE = Path(__file__).resolve().parent


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def design_note(data: dict[str, Any]) -> str:
    l2 = data["l2_counterexample"][0]
    return f"""# PROG3 Step 3 design note

## Corrected transition-system typing

Step 2 drains a finite queue under five proposal classes, but it does not compute an
undirected orbit. Series removal, exact two-terminal module replacement, zero/saturated
contraction, and inseparable contraction are proposed only in their reducing direction.
Delta–Y and Y–Delta are proposed in both directions. Its computed object is therefore a
**queue-exhaustive forward reachability set under four directed reductions and bidirectional
Delta–Y/Y–Delta**, restricted at every admission to presentations with unique active
minimizers and the unchanged complete terminal min-cut fingerprint. Disjoint forward sets do
not imply disjoint symmetric-closure orbits.

## L1 — series normal form on the admissible expansion family

The maintained `transform_series` replaces the two incident capacities `a,b` by
`min(a,b)`; `make_graph` sums that edge with an already-present parallel edge. The inverse
family used here replaces an edge of capacity `c` by a positive path with edge capacities
whose minimum is exactly `c`. For a fixed loopless simple series-reduced presentation and its homeomorphic
edge subdivisions, removal terminates because every rewrite deletes one nonterminal vertex.
Each maximal subdivided path contracts to the minimum of its capacities. Associativity and
commutativity of `min` make removals on one path order-independent, while removals on
different paths have disjoint interiors and commute. Thus this admissible subdivision family
has the original presentation as its unique terminal-fixed weighted series normal form.
The 13 actual carrier-level certificates independently expand the first edge as
`(c,2c,3c)`, remove the two new vertices in both orders, and recover the same endpoint.

For every terminal cut, a two-edge expansion contributes zero when its endpoints lie on the
same side and `min(a,b)=c` when they differ, so the complete fingerprint is unchanged. If the
original minimizer cuts that edge, its lift is unique exactly when `a != b`; for an edge never
used by an active cut, equality `a=b=c` can only tie inactive lifts and does not spoil active
uniqueness. Therefore the exact condition is: `min(a,b)=c`, and either `a != b` or the edge's
active-cut incidence column is zero. The certified `(c,2c)` and `(c,2c,3c)` splits satisfy
the strict case.

This proof is deliberately scoped to genuine homeomorphic subdivisions. It does not assert
confluence for arbitrary simple graphs containing a pendant cycle whose suppression would
require a self-loop representation absent from the maintained graph type.

## L2 — failed subdivided-Y-leg coherence case

The proposed projection fails on the stored `{l2['carrier']}`, seed {l2['seed']}
endpoint (`{l2['fiber_id']}`). The lexicographically first admissible case subdivides
`{l2['subdivided_edge']}` with exact capacities `{l2['split_capacities_exact']}`. Applying
Y–Delta at `{l2['y_center']}` gives the former subdivision vertex two new triangle edges, so
its degree becomes {l2['subdivision_degree_after_y_delta']}. There are no removable internal
bivalent vertices afterward. The two routes are

1. `{l2['move_sequence_expanded']}`; and
2. `{l2['move_sequence_reduced']}`.

Both endpoints have the same complete exact fingerprint as the starting endpoint, unique
minimizers, and minimum margin `{l2['post_move_minimum_margin_exact']}`. Yet their normal forms
have respectively {l2['expanded_normal_form_node_count']}/{l2['expanded_normal_form_edge_count']}
and {l2['direct_normal_form_node_count']}/{l2['direct_normal_form_edge_count']} nodes/edges and
are not terminal-fixed weighted isomorphic. A Delta–Y/Y–Delta move replaces three edges by
three edges; exact parallel merging can only lower, never raise, edge count. Hence a
Delta-only path starting from the {l2['direct_normal_form_edge_count']}-edge reduced route
cannot reach the {l2['expanded_normal_form_edge_count']}-edge normal form. This is the exact
local coherence obstruction requested by the dispatch. The CSV exports all three complete exact
weighted-edge presentations, not merely their carrier identifier and differing local capacities.

Because L2 fails, the L3 projection theorem is not invoked. This artifact stops the upgrade
rather than treating the failure of that proof route as evidence for or against the full
symmetric closure.

## Corrected literature reading

Kalman and Krauthgamer, [arXiv:2112.06916, Theorem 3.24](https://arxiv.org/abs/2112.06916),
exclude a universal local degree-`k>3` star-to-clique transformation preserving the terminal
min-cut metric. Their Open Question 4.5 leaves context-dependent and nonlocal transformation
systems open. The result supports only the statement that Delta–Y is the available universal
local star-mesh rule below degree four; it does not prove completeness of this repository's
five-class repertoire.
"""


def results(data: dict[str, Any]) -> str:
    witness = data["external_witness"][0]
    l2 = data["l2_counterexample"][0]
    lines = [
        "# PROG3 Step 3 — orbit-typing floor and symmetric-closure upgrade attempt",
        "",
        "## Mandatory floor",
        "",
        "On 13 fixed exact-rational graph topologies,",
        "19 kernel directions yield nondegenerate positive-capacity intervals with identical complete",
        "terminal min-cut fingerprints and unique active minimizers. Selected endpoints have different",
        "weights and are not related by terminal-label-fixed weighted automorphism. For each of the 19",
        "corresponding base/perturbed pairs, a queue-exhaustive **forward** search under four directed",
        "reduction rules and bidirectional Delta-Y/Y-Delta finds the two reachability sets disjoint.",
        "The search admits only intermediate presentations with the unchanged complete fingerprint and",
        "unique active minimizers and canonicalizes them modulo terminal-label-fixed exact weighted",
        "isomorphism. This establishes forward-reachability disjointness only; it establishes no",
        "symmetric-closure, completeness, or gauge-irreducibility claim.",
        "",
        "| fiber | carrier | seed | basis | forward states base/perturbed | forward intersection | floor | symmetric upgrade |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in data["floor_rows"]:
        lines.append(
            f"| {row['fiber_id']} | {row['carrier']} | {row['seed']} | {row['basis_index']} "
            f"| {row['base_forward_canonical_state_count']}/{row['perturbed_forward_canonical_state_count']} "
            f"| {row['forward_cross_isomorphism_count']} | {row['floor_verdict']} "
            f"| {row['symmetric_series_delta_upgrade_verdict']} |"
        )
    lines.extend(
        [
            "",
            "## Directionality census",
            "",
            "| move class | Step-2 directionality | accepted transitions | novel states |",
            "|---|---|---:|---:|",
        ]
    )
    for row in data["transition_census"]:
        lines.append(
            f"| {row['move_class']} | {row['directionality_in_step2']} "
            f"| {row['accepted_transition_count']} | {row['novel_canonical_state_count']} |"
        )
    lines.extend(
        [
            "",
            "All 50 novel Step-2 canonical states arise from the bidirectional Delta–Y class; none of",
            "the four reduction-only classes fires on the 38 reduced endpoints or their admitted forward",
            "successors.",
            "",
            "## External-witness regression, independently rebuilt",
            "",
            f"On `{witness['carrier']}`, seed {witness['seed']}, edge `{witness['expanded_edge']}` has",
            f"capacity `{witness['original_capacity_exact']}`. Replacing it by the exact path",
            f"`({witness['split_capacities_exact'].replace('|', ', ')})` preserves all",
            f"{witness['complement_reduced_region_count']} complement-reduced ({witness['ordered_region_count']} ordered)",
            "terminal min-cut values and leaves every minimizer unique, with exact minimum margin",
            f"`{witness['expanded_minimum_margin_exact']}`. The maintained series rule recomposes the",
            "path by `min`, exactly recovers the endpoint, and the expanded canonical presentation is",
            f"absent from the endpoint's {witness['forward_endpoint_state_count']}-state Step-2 forward set.",
            "This permanently reproduces the forward-versus-symmetric typing defect.",
            "",
            "## Lemma outcomes",
            "",
            "| lemma | outcome | exact certificates | scope |",
            "|---|---|---:|---|",
        ]
    )
    for row in data["lemma_rows"]:
        lines.append(
            f"| {row['lemma']} | {row['outcome']} | {row['certificate_count']} | {row['scope']} |"
        )
    lines.extend(
        [
            "",
            "L1 lands for admissible homeomorphic expansions of the 13 pinned series-reduced carrier",
            "instances. L2 fails at the subdivided-Y-leg case on `fiber_008`: the promoted",
            f"subdivision vertex has degree {l2['subdivision_degree_after_y_delta']}, the two exact normal",
            f"forms have {l2['expanded_normal_form_edge_count']} and {l2['direct_normal_form_edge_count']} edges,",
            "and their terminal-fixed exact weighted canonical keys differ. Both remain unique and preserve",
            "the full exact fingerprint. The detailed graph and capacities are exported in",
            "`l2_counterexample_step3.csv`.",
            "",
            "Therefore the attempted projection to Delta-only paths between series normal forms is invalid,",
            "and no symmetric `{series subdivision/removal, Delta–Y/Y–Delta}` orbit-disjointness verdict",
            "is certified here. The exact obstruction locates the failure; it neither connects nor separates",
            "any certified endpoint pair in that symmetric closure.",
            "",
            "## Can-fail controls",
            "",
            "| control | kind | expected/observed classification | expected/observed reason | metric | value | passes |",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in data["negative_controls"]:
        lines.append(
            f"| {row['control_id']} | {row['control_kind']} "
            f"| {row['expected_classification']} / {row['observed_classification']} "
            f"| {row['expected_reason']} / {row['observed_reason']} "
            f"| {row['metric']} | {row['value']} | {row['passes']} |"
        )
    lines.extend(
        [
            "",
            "## Literature boundary",
            "",
            "Kalman–Krauthgamer Theorem 3.24 rules out a universal local degree-`k>3` star-to-clique",
            "min-cut rule. It does not establish completeness of the five classes; their Open Question 4.5",
            "leaves context-dependent and nonlocal transforms open.",
            "",
        ]
    )
    return "\n".join(lines)


def statement() -> str:
    return """# PROG3 Step 3 statement

## Certified floor-only wording

On 13 fixed exact-rational graph topologies, 19 kernel directions yield nondegenerate positive-capacity intervals with identical complete terminal min-cut fingerprints and unique active minimizers. Selected endpoints have different weights and are not related by terminal-label-fixed weighted automorphism. For each of the 19 corresponding base/perturbed pairs, a queue-exhaustive forward search under four directed reduction rules and bidirectional Delta-Y/Y-Delta finds the two reachability sets disjoint. The search admits only intermediate presentations with the unchanged complete fingerprint and unique active minimizers and canonicalizes them modulo terminal-label-fixed exact weighted isomorphism. This establishes forward-reachability disjointness only; it establishes no symmetric-closure, completeness, or gauge-irreducibility claim.

An exact inverse-series witness proves that the symmetric closure is strictly larger than the computed forward sets. Series removal has a unique normal form on admissible homeomorphic subdivisions of the 13 pinned series-reduced carriers. However, an exact subdivided-Y-leg counterexample refutes the attempted series/Delta-Y projection lemma. It neither connects nor separates any certified endpoint pair; symmetric-closure orbit disjointness remains open. Kalman-Krauthgamer exclude only universal local degree-k>3 star-to-clique rules, not undeclared, inverse, context-dependent, nonlocal, or degenerate-intermediate transformations.

## Proposed upgraded wording — not certified

The proposed upgrade would have asserted orbit disjointness under the symmetric closure of
series subdivision/removal and Delta–Y/Y–Delta, modulo terminal-label-fixed exact weighted
isomorphism and with unique-minimizer intermediates. It is **not certified**: L2 fails exactly
when a subdivided Y leg undergoes Y–Delta on `fiber_008`. The resulting subdivision vertex is
degree three, its series normal form is distinct from the direct reduced route, and an edge-count
invariant excludes the required Delta-only projection. L3 is therefore not reached.
This counterexample proves neither connection nor disconnection of any certified endpoint pair.

The corrected literature result excludes a universal local degree-`k>3` star-to-clique rule;
it does not make the declared move repertoire complete.
"""


def nonclaim_boundary() -> str:
    return """# Nonclaim boundary

For each of the 19 base/perturbed pairs, this step certifies only disjointness of its two **forward**
reachability sets under four directed reductions and bidirectional Delta–Y/Y–Delta. It does not certify disjointness under
the symmetric closure of all five Step-2 classes. In particular, inverse module replacement,
inverse saturated/zero-column contraction, inverse inseparable contraction, and arbitrary inverse
series presentations are not exhausted.

The attempted symmetric upgrade is restricted to `{series subdivision/removal, Delta–Y/Y–Delta}`
and fails at its L2 projection lemma. Thus even that two-class symmetric orbit question remains
open. The counterexample neither connects nor separates any certified endpoint pair. Paths through
tied-minimizer presentations, nonlocal or context-dependent moves, and every
undeclared transformation remain open. Kalman–Krauthgamer Theorem 3.24 supplies no repertoire-
completeness claim.

Nothing here concerns contracted boundary states or state-level entanglement, and no bulk-geometry
inequivalence claim is made.
"""


def content_classification() -> str:
    return """# Content classification

| object | classification | role |
|---|---|---|
| Step-1 exact carrier and fingerprint machinery | IMPORTED READ-ONLY, HASH-PINNED TRANSITIVELY | exact rational reconstruction and complete cut enumeration |
| Step-2 saturation implementation and artifacts | IMPORTED READ-ONLY, HASH-PINNED | forward transition system being retyped |
| 19 forward reachability intersections | RECOMPUTED EXACT | certified floor |
| inverse-series witness | EXTERNAL FINDING, INDEPENDENTLY REPRODUCED EXACT | permanent regression for the typing defect |
| L1 series rule and expansion family | PROVED; COMPUTATIONALLY CERTIFIED ON 13 ACTUAL SERIES-REDUCED CARRIERS | scoped normal-form lemma |
| L2 subdivided-Y-leg case | COMPUTED EXACT COUNTEREXAMPLE TO THE PROPOSED COHERENCE LEMMA | blocks L3 |
| L3 symmetric-closure conclusion | NOT REACHED | no upgraded orbit verdict |
| five can-fail controls | COMPUTED EXACT | force the floor, fingerprint, canonicalization, uniqueness, and L1-hypothesis boundaries |
| Kalman–Krauthgamer theorem | LITERATURE INPUT | narrow local-star-mesh limitation only |
| inverse module/contraction moves and tied intermediates | OUT OF SCOPE / OPEN | not searched |
| state-level entanglement | OUT OF SCOPE | no state construction |
"""


def schema(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "artifact": "PROG3_STEP3_FORWARD_FLOOR_AND_SYMMETRIC_CLOSURE_UPGRADE_ATTEMPT",
        "version": 1,
        "arithmetic": "fractions.Fraction on every capacity and fingerprint path",
        "canonicalization": "terminal labels fixed pointwise; interiors freely relabelled; exact weights retained",
        "step2_retyping": {
            "transition_system": "four directed reductions plus bidirectional Delta-Y/Y-Delta",
            "closure": "queue-exhaustive forward reachability",
            "admission": "complete exact fingerprint equality and unique active minimizers",
            "floor_verdict": FLOOR_VERDICT,
            "fiber_count": len(data["floor_rows"]),
        },
        "upgrade": {
            "classes": ["series subdivision/removal", "Delta-Y/Y-Delta"],
            "L1": "PROVED_AND_CERTIFIED on admissible homeomorphic subdivisions of fixed loopless simple series-reduced presentations",
            "L2": "FAILED on stored fiber_008 subdivided-Y-leg case",
            "L3": "NOT_REACHED_BECAUSE_L2_FAILED",
            "verdict": UPGRADE_VERDICT,
        },
        "can_fail_controls": {
            "count": len(data["negative_controls"]),
            "all_pass": all(row["passes"] for row in data["negative_controls"]),
            "required_boundaries": [
                "forward-set intersection rejects disjoint floor",
                "capacity mutation breaks exact fingerprint equality",
                "terminal-fixed weighted-isomorphic relabeling is accepted",
                "equal active-edge split fails unique-minimizer admission",
                "non-series-reduced starting presentation reduces past itself",
            ],
        },
        "anti_bypass": "all witness and lemma fingerprints freshly recomputed by exact terminal-cut enumeration",
        "files": {
            "fiber_forward_floor_step3.csv": "19 corrected forward-closure verdict rows",
            "transition_census_step3.csv": "directionality and accepted/novel transition census",
            "external_witness_step3.csv": "independently rebuilt inverse-series witness",
            "l1_series_certificates_step3.csv": "13 actual series-reduced-carrier order-independence checks",
            "l2_counterexample_step3.csv": "exact subdivided-Y-leg obstruction",
            "lemma_outcomes_step3.csv": "typed L1/L2/L3 outcomes",
            "negative_controls_step3.csv": "five exact can-fail and hypothesis-necessity controls",
            "dependency_pins_step3.csv": "literal read-only dependency and evidence pins",
        },
        "literature_scope": "KK Theorem 3.24 excludes universal local degree-k>3 star-to-clique rules; no repertoire completeness",
    }


def render(data: dict[str, Any]) -> dict[str, str]:
    return {
        "design_note_step3.md": design_note(data),
        "results_step3.md": results(data),
        "schema_step3.json": json.dumps(schema(data), indent=2, sort_keys=True) + "\n",
        "content_classification.md": content_classification(),
        "nonclaim_boundary.md": nonclaim_boundary(),
        "statement.md": statement(),
        "fiber_forward_floor_step3.csv": csv_text(data["floor_rows"]),
        "transition_census_step3.csv": csv_text(data["transition_census"]),
        "external_witness_step3.csv": csv_text(data["external_witness"]),
        "l1_series_certificates_step3.csv": csv_text(data["l1_certificates"]),
        "l2_counterexample_step3.csv": csv_text(data["l2_counterexample"]),
        "lemma_outcomes_step3.csv": csv_text(data["lemma_rows"]),
        "negative_controls_step3.csv": csv_text(data["negative_controls"]),
        "dependency_pins_step3.csv": csv_text(data["dependencies"]),
    }


def generate(destination: Path) -> dict[str, str]:
    data = compute_all()
    artifacts = render(data)
    destination.mkdir(parents=True, exist_ok=True)
    for name, text in artifacts.items():
        (destination / name).write_text(text, encoding="utf-8")
    return artifacts


def main() -> None:
    artifacts = generate(HERE)
    print(f"build_step3.py: PASS: wrote={len(artifacts)}")


if __name__ == "__main__":
    main()
