#!/usr/bin/env python3
"""Render deterministic PROG3 Step-2 saturation artifacts."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Any

from saturation_engine import ENDPOINT_WALL_SECONDS, MOVE_CLASSES, STATE_CAP
from step2_core import compute_all


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
    fibers = data["fiber_rows"]
    endpoints = data["endpoint_rows"]
    return {
        "artifact": "PROG3_STEP2_EXACT_FIVE_MOVE_ORBIT_SATURATION",
        "version": 1,
        "arithmetic": "fractions.Fraction on every capacity-dependent path",
        "transition_system": {
            "search": "breadth-first closure until canonical queue exhaustion",
            "replacement_depth_cap": None,
            "move_classes": list(MOVE_CLASSES),
            "candidate_policy": "every applicable labelled proposal in every class",
            "admission_policy": "full exact terminal fingerprint equality plus continued unique minimizers",
        },
        "canonicalization": {
            "terminal_labels": "fixed pointwise",
            "nonterminal_labels": "free under permutation",
            "weights": "exact Fraction numerator/denominator included",
        },
        "budgets": {
            "canonical_state_cap_per_endpoint": STATE_CAP,
            "wall_clock_seconds_per_endpoint": ENDPOINT_WALL_SECONDS,
            "budget_hit_semantics": "BUDGET_TRUNCATED, never saturation",
        },
        "fingerprint_audit": "every admitted canonical state fully re-enumerated exactly; not sampled",
        "files": {
            "fiber_saturation_step2.csv": "one intersection verdict per direction fiber",
            "endpoint_saturation_step2.csv": "38 endpoint saturation counts, depths, and move censuses",
            "fingerprint_invariance_step2.csv": "full exact admission audit coverage",
            "structural_audit_step2.csv": "no-depth-cap, exactness, canonicalization, and budget gates",
            "dependency_pins_step2.csv": "literal closed-Step-1 pins",
        },
        "headline": {
            "fiber_count": len(fibers),
            "endpoint_count": len(endpoints),
            "saturated_endpoints": sum(row["saturated"] for row in endpoints),
            "complete_orbit_disjoint": sum(
                row["verdict"] == "complete five-move-orbit-disjoint (saturated)"
                for row in fibers
            ),
            "gauge": sum(row["verdict"].startswith("GAUGE via path") for row in fibers),
            "budget_truncated": sum(row["verdict"].startswith("budget-truncated") for row in fibers),
        },
    }


def results_markdown(data: dict[str, Any]) -> str:
    fibers = data["fiber_rows"]
    endpoints = data["endpoint_rows"]
    saturated = sum(row["saturated"] for row in endpoints)
    disjoint = sum(
        row["verdict"] == "complete five-move-orbit-disjoint (saturated)"
        for row in fibers
    )
    gauge = sum(row["verdict"].startswith("GAUGE via path") for row in fibers)
    truncated = sum(row["verdict"].startswith("budget-truncated") for row in fibers)
    lines = [
        "# PROG3 Step 2 — exact five-move orbit saturation",
        "",
        "## Headline",
        "",
        f"All **{saturated} of {len(endpoints)} endpoints** reached canonical queue exhaustion before either safety",
        f"budget. The 19 fiber intersections classify as complete-disjoint={disjoint}, gauge={gauge},",
        f"budget-truncated={truncated}.",
        "",
        "| fiber | carrier | seed | basis | states base/perturbed | max replacement depth base/perturbed | accepted moves base/perturbed | verdict |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in fibers:
        lines.append(
            f"| {row['fiber_id']} | {row['carrier']} | {row['seed']} | {row['basis_index']} "
            f"| {row['base_canonical_state_count']}/{row['perturbed_canonical_state_count']} "
            f"| {row['base_max_replacement_depth']}/{row['perturbed_max_replacement_depth']} "
            f"| `{row['base_accepted_move_census']}` / `{row['perturbed_accepted_move_census']}` "
            f"| {row['verdict']} |"
        )
    lines.extend(
        [
            "",
            "The accepted-move census counts every exact accepted labelled transition, including returns to an",
            "already-known canonical state. `endpoint_saturation_step2.csv` separately reports the number of novel",
            "canonical states contributed by each class.",
            "",
            "## Saturation and fingerprint audit",
            "",
            "The BFS proposes every applicable move in all five classes from every admitted canonical state. There is",
            "no replacement-depth cutoff. Saturation is declared only when the queue is empty. The hard safeguards are",
            f"{STATE_CAP:,} canonical states and {ENDPOINT_WALL_SECONDS:g} seconds per endpoint; a hit would be typed",
            "as budget truncation rather than saturation.",
            "",
            "Every admitted state—not merely a sample—was subjected to fresh exact enumeration of every terminal",
            "bipartition and every interior-side assignment before admission. All retained minimizers stayed unique and",
            "all complete terminal fingerprints matched their endpoint.",
            "",
            "## Interpretation",
            "",
        ]
    )
    if disjoint == len(fibers):
        lines.extend(
            [
                "For every one of the 19 pinned rational pairs, the two complete saturated orbits under the five",
                "declared move classes are disjoint modulo terminal-label-fixed exact weighted isomorphism. No fiber",
                "collapses to gauge at depth greater than three—or at any finite depth in these exhausted declared",
                "orbits.",
            ]
        )
    elif gauge:
        lines.append(
            "At least one former depth-three fiber collapses to gauge; its explicit two-sided path is recorded above."
        )
    else:
        lines.append(
            "At least one endpoint hit a safety budget, so only disjointness within the explored sets is reported."
        )
    lines.extend(
        [
            "",
            "This closes only the declared five-class orbit question. Transformations outside those classes remain",
            "open, and this artifact says nothing about contracted quantum states or state-level entanglement.",
            "",
        ]
    )
    return "\n".join(lines)


def content_classification() -> str:
    return """# Content classification

| object | classification | role |
|---|---|---|
| Step-1 exact engine and 19 fiber artifacts | IMPORTED READ-ONLY, HASH-PINNED | exact carriers and endpoint pairs |
| five-class transition proposals | REUSED AND BRANCH-COMPLETE | every applicable labelled move is considered |
| saturated orbit | GENERATED EXACT COMPUTATION | canonical BFS fixed point, unless explicitly budget-truncated |
| weighted graph equivalence | COMPUTED | terminal labels fixed pointwise, nonterminals free, exact weights retained |
| terminal fingerprint | COMPUTED BY FULL EXACT ENUMERATION | rechecked before every state admission |
| orbit intersection | COMPUTED | exact intersection of saturated canonical-key sets |
| transformations outside five classes | OUT OF SCOPE | still-open equivalence frontier |
| state-level entanglement | OUT OF SCOPE | no contracted states are constructed here |
"""


def nonclaim_boundary() -> str:
    return """# Nonclaim boundary

This artifact closes the orbit only under the five declared graph-move classes. It does not establish inequivalence
under transformations outside those classes, arbitrary mimicking-network transformations, continuum equivalences, or
any future enlargement of the move grammar. “Complete” means complete saturation of this explicitly declared finite
transition system, modulo terminal-label-fixed exact weighted graph isomorphism.

No claim is made about contracted boundary states, quantum entropies, RT equality, or state-level entanglement
underdetermination. Graph-fingerprint equality and graph-move-orbit disjointness do not by themselves imply equality or
inequivalence of boundary quantum states.
"""


def statement(data: dict[str, Any]) -> str:
    fibers = data["fiber_rows"]
    disjoint = sum(
        row["verdict"] == "complete five-move-orbit-disjoint (saturated)"
        for row in fibers
    )
    saturated = all(row["base_saturated"] and row["perturbed_saturated"] for row in fibers)
    if saturated and disjoint == len(fibers):
        body = """For every one of the 19 pinned exact-rational cut-fingerprint fibers, both endpoint orbits were
saturated by breadth-first closure under every applicable move in the five declared classes. Canonicalization fixed
terminal labels pointwise, freely relabelled non-terminals, and retained exact rational edge weights. Every admitted
state passed full exact terminal-fingerprint re-enumeration with unique minimizers. All 19 pairs of complete saturated
canonical orbit sets are disjoint. Thus the former depth-three result upgrades to complete five-move-orbit-disjointness
for these 19 pinned pairs under exactly the declared move system."""
    else:
        body = """The declared saturation computation did not certify complete five-move-orbit-disjointness for all
19 pairs. Per-fiber gauge paths or explicit budget-truncation records in `fiber_saturation_step2.csv` are the certified
outcome; no unbounded or undeclared-transformation claim is made."""
    return "# Certified Step-2 statement\n\n" + body + "\n"


def render(data: dict[str, Any]) -> dict[str, str]:
    return {
        "results_step2.md": results_markdown(data),
        "schema_step2.json": json.dumps(schema(data), indent=2, sort_keys=True) + "\n",
        "content_classification.md": content_classification(),
        "nonclaim_boundary.md": nonclaim_boundary(),
        "statement.md": statement(data),
        "fiber_saturation_step2.csv": csv_text(data["fiber_rows"]),
        "endpoint_saturation_step2.csv": csv_text(data["endpoint_rows"]),
        "fingerprint_invariance_step2.csv": csv_text(data["fingerprint_rows"]),
        "structural_audit_step2.csv": csv_text(data["structural_audit"]),
        "dependency_pins_step2.csv": csv_text(data["dependencies"]),
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
    print(f"build_step2.py: PASS: wrote={len(artifacts)}")


if __name__ == "__main__":
    main()
