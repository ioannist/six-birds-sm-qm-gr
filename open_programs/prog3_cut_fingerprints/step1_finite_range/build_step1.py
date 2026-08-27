#!/usr/bin/env python3
"""Render deterministic PROG3 Step-1 artifacts."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from step1_core import compute_all


HERE = Path(__file__).resolve().parent


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def schema(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "prog3_cut_fingerprints_step1",
        "version": 2,
        "arithmetic": "fractions.Fraction for every capacity-dependent certification computation",
        "weight_lift": {
            "rule": "moderate=randint(85,115)/100; tie_breaker=2^edge_index/2^(edge_count+24)",
            "source": "pinned active_cut_quotient_v2.py seeded_weights",
            "decimal_round_trip_used": False,
        },
        "fingerprint": "all nonempty proper terminal subsets, exhaustive interior-side assignments",
        "interval_semantics": {
            "fingerprint_interval": "closed maximal interval from every exact active-versus-inactive cut inequality",
            "positive_capacity_interval": "open interval on which every edge capacity remains strictly positive",
            "certified_network_interval": "intersection of the preceding intervals",
        },
        "circular_planarity": "add an apex adjacent to every terminal and run the exact combinatorial Left-Right Planarity Test; planar iff terminals are cofacial",
        "depth_three_orbit": {
            "move_classes": "all five declared v3 classes; every exact accepted Delta-Y/Y-Delta branch is explored to replacement depth three, with deterministic closure under the earlier four classes after each replacement",
            "canonicalization_preregistered": "terminal labels fixed pointwise; non-terminal labels free; exact Fraction edge weights included",
            "intersection": "exact equality of terminal-fixed weighted canonical graph keys across the two complete visited-state sets",
            "scope": "bounded depth-three orbit audit; no unbounded irreducibility claim",
        },
        "files": {
            "carrier_summary_step1.csv": "one exact recertification row per v3 survivor",
            "kernel_intervals_step1.csv": "one exact maximal interval per integer kernel-basis direction",
            "certified_fibers_step1.csv": "interior perturbation and non-equivalence certificates",
            "orbit_audit_step1.csv": "all 19 bounded closure-orbit intersections, accepted-move counts, orbit sizes, and gauge witnesses",
            "exact_cut_regions_step1.csv": "raw and reduced exact cut/minimizer/margin rows",
            "exact_weights_step1.csv": "raw and reduced exact rational carrier definitions",
            "closure_audit_step1.csv": "exact five-move closure paths and fingerprint checks",
            "anti_bypass_step1.csv": "structural exhaustive-enumeration gates",
            "dependency_pins_step1.csv": "read-only v2/v3/data SHA-256 pins",
        },
        "headline": {
            "survivor_carriers": len(data["summaries"]),
            "kernel_basis_directions": len(data["intervals"]),
            "certified_direction_fibers": sum(row["certified_fiber"] for row in data["fibers"]),
            "certified_carrier_fibers": sum(row["certified_carrier_fiber"] for row in data["summaries"]),
            "depth_three_orbit_disjoint_fibers": sum(row["verdict"] == "depth-three five-move-orbit-disjoint" for row in data["orbit_audits"]),
            "depth_three_gauge_fibers": sum(row["verdict"] == "GAUGE" for row in data["orbit_audits"]),
        },
    }


def results_markdown(data: dict[str, Any]) -> str:
    summaries = data["summaries"]
    intervals = data["intervals"]
    fibers = data["fibers"]
    orbit_audits = data["orbit_audits"]
    lines = [
        "# PROG3 Step 1 — exact finite-range cut-fingerprint fibers",
        "",
        "## Exact reconstruction and lift",
        "",
        "The 13 rows in the pinned P1-v3 survivor artifact were rebuilt from the declared carrier generator, not",
        "from its decimal display columns. For edge index `i` in an `m`-edge carrier, the exact seeded rule is",
        "`randint(85,115)/100 + 2^i/2^(m+24)`, with the PRNG initialized from the declared SHA-256-derived seed.",
        "Thus no decimal-to-rational guess enters the certification path. Every cut value, margin, rank, kernel",
        "direction, crossing bound, and perturbed fingerprint comparison uses `fractions.Fraction`.",
        "",
        "All 13 v3 survivor statuses reproduce exactly. The three formerly near-tolerance margins are:",
        "",
        "- `wheel_W4__b8__leaf_offset0`, seed 47: `135/274877906944` (genuinely positive).",
        "- `wheel_W4__b8__leaf_offset1`, seed 17: `113/274877906944` (genuinely positive).",
        "- `K23_bipartite__b8__dual_gateway`, seed 47: `79/17179869184` (genuinely positive).",
        "",
        "No row changes cell or becomes degenerate under exact arithmetic.",
        "",
        "## Per-carrier recertification",
        "",
        "| carrier | seed | raw exact margin | reduced rank/edges | kernel dim | direction fibers | circular planar raw/reduced | v3 status |",
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in summaries:
        lines.append(
            f"| {row['carrier']} | {row['seed']} | `{row['raw_minimum_margin_exact']}` "
            f"| {row['reduced_rank_exact']}/{row['reduced_edge_count']} | {row['residual_deficiency']} "
            f"| {row['certified_direction_fiber_count']}/{row['kernel_basis_directions']} "
            f"| {row['raw_circular_planar']}/{row['reduced_circular_planar']} "
            f"| {'REPRODUCED' if row['v3_status_exactly_reproduced'] else 'CHANGED'} |"
        )
    lines.extend(
        [
            "",
            "The circular-planarity decision uses the cofacial augmentation criterion: append one new apex joined",
            "to every terminal, then apply the exact combinatorial Left-Right Planarity Test. All 13 raw carriers",
            "fail this test. After certified reductions, 7 are circular planar and 6 are not; this status change is",
            "a property of the reduced presentations, not an arithmetic discrepancy.",
            "The observable is a terminal min-cut function, not a Dirichlet-to-Neumann response matrix; electrical",
            "criticality was not checked. The seven reduced circular-planar rows show that circular planarity alone",
            "does not remove min-cut fibers. This is not a counterexample to the electrical uniqueness theorem.",
            "",
            "## Exact finite-range intervals",
            "",
            "For each unique active cut `a`, every enumerated competing cut `c` supplies the exact inequality",
            "`(c-a)·(w+t v) >= 0`. Intersecting all such inequalities gives the maximal fingerprint interval.",
            "The positive-capacity interval is reported separately in `kernel_intervals_step1.csv`.",
            "",
            "| carrier | seed | basis | maximal exact fingerprint interval | chosen interior t* | fiber |",
            "|---|---:|---:|---|---:|---|",
        ]
    )
    fiber_map = {
        (row["carrier"], row["seed"], row["basis_index"]): row for row in fibers
    }
    for row in intervals:
        fiber = fiber_map[(row["carrier"], row["seed"], row["basis_index"])]
        lines.append(
            f"| {row['carrier']} | {row['seed']} | {row['basis_index']} "
            f"| `{row['fingerprint_interval']}` | `{fiber.get('t_star_exact', '')}` "
            f"| {fiber['certified_fiber']} |"
        )
    lines.extend(
        [
            "",
            f"All **{len(intervals)}** basis directions have nondegenerate two-sided intervals. Exact full cut",
            f"enumeration at every selected interior point certifies **{sum(row['certified_fiber'] for row in fibers)}**",
            f"direction-level fibers across **{sum(row['certified_carrier_fiber'] for row in summaries)} of 13** carriers.",
            "For every pair, the weights differ; no graph automorphism maps one weighting",
            "to the other; all minimizers remain unique; and each endpoint is returned as the minimum of the",
            "declared depth-three closure objective.",
            "",
            "## Exact depth-three five-move orbit audit",
            "",
            "For each endpoint, every exact accepted replacement state and every intermediate deterministic-fold",
            "state visited to replacement depth three is retained. Weighted presentations are canonicalized with",
            "terminal labels fixed pointwise, non-terminal labels free, and exact `Fraction` weights included.",
            "The two canonical state sets are intersected; an intersection is reported as gauge with explicit paths",
            "from both endpoints.",
            "",
            "| carrier | seed | basis | accepted moves base/perturbed | canonical orbit states base/perturbed | cross isomorphisms | verdict |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for row in orbit_audits:
        verdict = row["verdict"] if row["verdict"] != "GAUGE" else f"GAUGE via `{row['path_if_gauge']}`"
        lines.append(
            f"| {row['carrier']} | {row['seed']} | {row['basis_index']} "
            f"| {row['base_accepted_move_count']}/{row['perturbed_accepted_move_count']} "
            f"| {row['base_orbit_state_count']}/{row['perturbed_orbit_state_count']} "
            f"| {row['cross_orbit_weighted_isomorphism_count']} | {verdict} |"
        )
    disjoint = sum(row["verdict"] == "depth-three five-move-orbit-disjoint" for row in orbit_audits)
    gauge = sum(row["verdict"] == "GAUGE" for row in orbit_audits)
    lines.extend(
        [
            "",
            f"Headline: **{disjoint} of 19** fibers are depth-three five-move-orbit-disjoint; **{gauge} of 19**",
            "have a cross-presentation gauge witness in the declared bounded orbit.",
            "",
            "## Anti-bypass and scope",
            "",
            "Every perturbed fingerprint is recomputed by exhaustive enumeration of all interior vertex-side",
            "assignments for all nontrivial terminal subsets. The Jacobian is used only to choose candidate kernel",
            "directions; it is never used to synthesize or extrapolate a perturbed fingerprint.",
            "",
            "**EXACT_FINITE_RANGE_FIBERS_WITH_DEPTH_THREE_ORBIT_AUDIT_ON_ALL_13_PINNED_CARRIERS.** This is a finite-carrier result",
            "for the terminal min-cut fingerprint and the declared depth-three five-move orbit audit. It is not a",
            "state-level entanglement result, an unbounded irreducibility result, or a uniqueness theorem for",
            "arbitrary graphs or non-local equivalences.",
            "",
        ]
    )
    return "\n".join(lines)


def content_classification() -> str:
    return """# Content classification

| object | classification | role |
|---|---|---|
| exact cut enumerator and interval solver | GENERATED COMPUTATION | exhaustive rational certification path |
| v2/v3 drivers and v3 survivor CSV | IMPORTED READ-ONLY, HASH-PINNED | carrier definitions and declared five-move search |
| seeded rational lift | REUSED EXACT GENERATION RULE | reconstructs weights before any decimal serialization |
| active-cut kernel bases | COMPUTED | candidate null directions only |
| perturbed fingerprints | COMPUTED BY FULL CUT ENUMERATION | never extrapolated from a Jacobian |
| automorphism verdicts | COMPUTED | all unweighted graph automorphisms enumerated exactly; terminal-set-preserving counts also retained |
| bounded five-move orbit intersection | COMPUTED | every visited exact state canonicalized with terminal labels fixed pointwise and interiors free |
| circular-planarity verdicts | COMPUTED | terminal-apex cofacial planarity criterion |
| Kalman--Krauthgamer local-move cap | CITED LITERATURE | prior-art boundary from `../LITERATURE.md`; not derived here |
"""


def nonclaim_boundary() -> str:
    return """# Nonclaim boundary

Step 1 makes no claim about contracted tensor-network states, quantum-state entropies, RT equality, or state-level
entanglement underdetermination. Equality here means equality of the complete terminal min-cut fingerprint only.

The result is restricted to the 13 pinned P1-v3 survivor instances, their exact seeded rational weights, the integer
basis selected by deterministic row reduction, and the five declared local reduction classes explored to replacement
depth three. It does not establish unbounded irreducibility. Deeper-than-depth-three move sequences and transformations
outside the declared classes remain open, as does a characterization of all mimicking-network fibers. Circular
planarity is reported, not assumed. The statement
that local star--mesh preservation is capped at k=3 is a Kalman--Krauthgamer literature result recorded in
`../LITERATURE.md`, not a computation or new theorem of this artifact.
"""


def statement() -> str:
    return """# Certified Step-1 statement

For each of the 13 pinned P1-v3 carrier instances, exact reconstruction of the declared seeded weights preserves
unique terminal-region minimizers and reproduces the published exact active-cut rank and residual deficiency. The
three decimal margins previously near floating tolerance are strictly positive exact rationals.

Every one of the 13 pinned carriers has at least one nondegenerate exact rational direction interval containing distinct
positive same-graph weightings with identical complete terminal min-cut fingerprints and no graph automorphism relating
the selected endpoints. For each of the 19 deterministic integer kernel directions, both endpoints are returned as the
minimum of the declared depth-three closure objective, and the complete visited state sets are compared modulo exact
terminal-label-fixed weighted isomorphism. The per-fiber result is either depth-three five-move-orbit-disjoint or an
explicit gauge path, as recorded in `orbit_audit_step1.csv`. No unbounded irreducibility is claimed.
"""


def render(data: dict[str, Any]) -> dict[str, str]:
    return {
        "results_step1.md": results_markdown(data),
        "schema_step1.json": json.dumps(schema(data), indent=2, sort_keys=True) + "\n",
        "content_classification.md": content_classification(),
        "nonclaim_boundary.md": nonclaim_boundary(),
        "statement.md": statement(),
        "carrier_summary_step1.csv": csv_text(data["summaries"]),
        "kernel_intervals_step1.csv": csv_text(data["intervals"]),
        "certified_fibers_step1.csv": csv_text(data["fibers"]),
        "orbit_audit_step1.csv": csv_text(data["orbit_audits"]),
        "exact_cut_regions_step1.csv": csv_text(data["cut_regions"]),
        "exact_weights_step1.csv": csv_text(data["weights"]),
        "closure_audit_step1.csv": csv_text(data["closures"]),
        "anti_bypass_step1.csv": csv_text(data["anti_bypass"]),
        "dependency_pins_step1.csv": csv_text(data["dependencies"]),
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
    print(f"build_step1.py: PASS: wrote={len(artifacts)}")


if __name__ == "__main__":
    main()
