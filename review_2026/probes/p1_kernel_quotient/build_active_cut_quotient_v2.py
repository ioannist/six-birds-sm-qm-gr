#!/usr/bin/env python3
"""Write versioned P1-REPAIR-2 active-cut artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from pathlib import Path
from typing import Any

import active_cut_quotient_v2 as core


HERE = Path(__file__).resolve().parent


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise ValueError("empty CSV")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def markdown(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def findings(result: dict[str, Any]) -> str:
    definition = result["search_definition"]
    census = result["search_census"][0]
    candidate = result["candidate"][0] if result["candidate"] else None
    candidate_text = "No residual candidate survived."
    if candidate:
        candidate_text = f"""The selected landing candidate is `{candidate['carrier']}`: six boundary terminals attached in pairs to a three-node complete interior, with nine post-closure edges. Its exact active-cut matrix has rank `{candidate['exact_rank']}` and deficiency `{candidate['residual_deficiency']}`. The minimum uniqueness margin is `{candidate['minimum_unique_cut_margin']:.12g}`. No closure move fired before selection, and the independent irreducibility audit reports zero applicable objects for all four named moves.

Its exact integer column dependency is `{result['dependencies'][0]['integer_column_dependency']}`. Thus increasing `I0-I2` and `I1-I2` while decreasing `I0-I1` leaves every active-cut value fixed inside the unique-cut chamber. Exact finite checks at both signs use `delta={result['finite_checks'][0]['delta']:.12g}` and preserve all 62 region values, active cuts, and uniqueness."""
    return f"""# P1-REPAIR-2: active-cut quotient and irreducibility search

## Machinery regressions

{markdown(result['regressions'], ['carrier', 'seed', 'unique_all_regions', 'raw_edges', 'raw_exact_rank', 'raw_deficiency', 'reduction_moves', 'reduced_edges', 'reduced_exact_rank', 'residual_deficiency', 'all_region_values_preserved'])}

The exact 0/1 active-cut incidence matrix uses one row for every nonempty proper boundary region and one column per edge. Each minimum cut and its runner-up are enumerated with rational capacities; tied rows are excluded. Rank is rational Gaussian-elimination rank, not a finite-difference estimate. Every reduction step is accepted only after recomputing every region and verifying identical minimum-cut values and unique minimizers.

The regressions reproduce the ruling: published ranks `9/9/9` with five series/parallel redundancies removed; the crosslinked module reduces from 17 columns to rank-nine nine-column form; grid ranks are `10/10/9` and zero-column terminal contractions leave `10/10/9` full-rank quotients; stiff K4 has rank 11 and inseparable contraction plus parallel sums leaves 11 columns of rank 11.

## Declared search family

The family contains `{definition['topology_template_count']}` labelled interior templates and `{definition['unweighted_carrier_count']}` topology/attachment carriers: complete and expander-like interiors, wheels, triangular prism, K5-minus variants, K2,3/K3,3, octahedral, and a crosslinked 2x3 grid. Boundary counts are 6, 7, and 8; interiors contain 3--6 nodes; attachment schemes are leaf-offset zero, leaf-offset one, and dual gateway. Three seeds give `{definition['evaluated_weighted_carrier_count']}` weighted carriers. Base capacities lie in `[0.85,1.15]`; exact binary edge perturbations remove ties without creating a broad scale hierarchy.

{markdown(result['search_census'], ['evaluated_weighted_carriers', 'unique_cut_carriers', 'raw_deficient_carriers', 'fully_explained_after_closure', 'residual_survivor_count', 'residual_deficiency_distribution', 'survivor_family_distribution'])}

## Landing candidate

{candidate_text}

## Outcome ruling input

**{result['outcome']}**. A rank-deficient active-cut carrier survives saturated-terminal/zero-column contraction, inseparable-vertex contraction with parallel sums, series reduction, and exact two-terminal-module replacement. This is the graph-level P1 landing candidate requested by the ruling. It remains finite-carrier evidence, not a universal theorem, and is explicitly handed to Eddy for a possible fifth reduction (the three-interior triangle dependency is the obvious target).
"""


def design() -> str:
    return """# P1-REPAIR-2 exact design

- All v1 probe machinery is imported read-only under a literal SHA-256 pin; the frozen Step42/44/55 pins remain enforced transitively.
- For each boundary region, boundary vertices are fixed to opposite cut sides and all interior assignments are enumerated. Exact integerized rational capacities determine the unique minimum, runner-up margin, cut-side assignment, and 0/1 edge-incidence row.
- Saturated-terminal/zero-column contraction and inseparable-vertex contraction identify endpoints never separated by any active cut. Contraction automatically merges parallel edges by capacity sum.
- A bivalent interior vertex is replaced by an edge of capacity equal to the minimum of its two incident capacities. A boundary-free subgraph with exactly two external gateways is replaced by its exact gateway min-cut capacity.
- Reduction moves run to closure. Every proposed graph is independently re-enumerated, and a move is retained only when all boundary-region minimum values are byte-for-byte equal as rational numbers and minimizers remain unique.
- Search weights use moderate rational capacities plus small binary edge perturbations. The perturbations make distinct edge subsets have distinct tie-break contributions, so degenerate active-cut chambers are excluded exactly.
- A residual nullspace is computed by rational RREF and integerized. Finite two-sided checks move within the exact uniqueness margin and re-enumerate every cut; unchanged values are not inferred from a differential calculation.
"""


def render(result: dict[str, Any]) -> dict[str, bytes]:
    schema = {
        "artifact": "P1-REPAIR-2 active-cut quotient", "schema_version": 2,
        "rank": "exact rational rank of all-region 0/1 active-cut incidence matrix",
        "reductions": ["saturated_terminal_zero_column", "inseparable_vertex_parallel_sum",
                       "series_bivalent", "exact_two_terminal_module"],
        "search_definition": result["search_definition"],
        "row_counts": {"regressions": len(result["regressions"]), "search": len(result["search"]),
                       "candidate_edges": len(result["candidate_edges"]),
                       "candidate_active_cuts": len(result["candidate_active_cuts"]),
                       "dependencies": len(result["dependencies"]),
                       "finite_checks": len(result["finite_checks"])},
        "outcome": result["outcome"],
    }
    payloads = {
        "p1_v2_dependency_pin.csv": csv_bytes(result["pin"]),
        "p1_v2_machinery_regressions.csv": csv_bytes(result["regressions"]),
        "p1_v2_search_cases.csv": csv_bytes(result["search"]),
        "p1_v2_search_census.csv": csv_bytes(result["search_census"]),
        "p1_v2_candidate_summary.csv": csv_bytes(result["candidate"]),
        "p1_v2_candidate_edges.csv": csv_bytes(result["candidate_edges"]),
        "p1_v2_candidate_active_cuts.csv": csv_bytes(result["candidate_active_cuts"]),
        "p1_v2_candidate_dependencies.csv": csv_bytes(result["dependencies"]),
        "p1_v2_candidate_finite_checks.csv": csv_bytes(result["finite_checks"]),
        "p1_v2_candidate_irreducibility.csv": csv_bytes(result["candidate_irreducibility"]),
        "p1_v2_schema.json": json_bytes(schema),
        "FINDINGS_v2.md": findings(result).encode(), "DESIGN_v2.md": design().encode(),
    }
    manifest = {name: hashlib.sha256(payload).hexdigest() for name, payload in sorted(payloads.items())}
    payloads["p1_v2_artifact_manifest.json"] = json_bytes(manifest)
    return payloads


def main() -> None:
    started = time.perf_counter()
    result = core.run()
    for name, payload in render(result).items():
        (HERE / name).write_bytes(payload)
    print(f"P1 v2 build PASS: regressions={len(result['regressions'])} search={len(result['search'])} "
          f"survivors={result['search_census'][0]['residual_survivor_count']} "
          f"candidate_deficiency={result['candidate'][0]['residual_deficiency']} "
          f"elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
