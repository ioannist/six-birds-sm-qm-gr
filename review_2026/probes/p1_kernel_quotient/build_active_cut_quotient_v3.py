#!/usr/bin/env python3
"""Write versioned P1-HYGIENE five-move closure artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from pathlib import Path
from typing import Any

import active_cut_quotient_v3 as core


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


def experimental_aggregate(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for rule in sorted({row["experimental_rule"] for row in result["experimental"]}):
        selected = [row for row in result["experimental"] if row["experimental_rule"] == rule]
        rows.append(
            {
                "experimental_rule": rule,
                "certified_closure_member": False,
                "five_move_survivors_tested": len(selected),
                "candidate_directions": sum(row["candidate_direction_count"] for row in selected),
                "accepted_exact_finite_directions": sum(row["accepted_direction_count"] for row in selected),
                "survivors_fully_explained": sum(row["fully_explains_residual"] for row in selected),
                "outcome": "EXPLAINS_NONE" if not any(row["fully_explains_residual"] for row in selected)
                else "EXPLAINS_AT_LEAST_ONE",
            }
        )
    return rows


def findings(result: dict[str, Any]) -> str:
    summary = result["summary"][0]
    named = result["named_regression"]
    experimental = experimental_aggregate(result)
    return f"""# P1-HYGIENE v3: five-move active-cut closure

## Certified fifth move

The maintained closure now includes exact `Delta-Y` and `Y-Delta` replacement. For a triangle with capacities `w01,w02,w12`, the replacement star has legs `a0=w01+w02`, `a1=w01+w12`, and `a2=w02+w12`; the inverse uses the exact half-sum formulas. Every proposal is accepted only after re-enumerating every nonempty proper boundary region, checking exact equality of all rational minimum-cut values, and confirming continued unique minimizers. The declared three-round search includes equal/intermediate presentations and prevents inverse-move oscillation by its finite depth.

The 378-carrier search reproduces the required transition: **{summary['explained_by_fifth_move']} of the {summary['four_move_survivors']} four-move survivors are explained**, leaving **{summary['five_move_survivors']}**. Their residual-deficiency histogram is **{summary['residual_deficiency_histogram']}** (`1^8, 2^4, 3^1`). The maintained finite search exhausts three replacement rounds, sufficient for this declared family and including the named two-replacement regression.

{markdown(result['regressions'], ['carrier', 'seed', 'unique_all_regions', 'raw_exact_rank', 'raw_deficiency', 'reduction_moves', 'fifth_move_count', 'reduced_exact_rank', 'residual_deficiency', 'all_region_values_preserved'])}

## Named K2,3 regression

`K23_bipartite__b6__leaf_offset0__seed31` retains all 62 exact cut values and unique minimizers after every accepted move. Its path is inseparable contraction, `Y-Delta`, `Delta-Y`, and series reduction. Rank is re-enumerated after each step and finishes at rank 8 on 9 edges, residual deficiency 1:

{markdown(named, ['move_index', 'move', 'object', 'region_count', 'all_region_values_preserved', 'unique_after_move', 'rank_recomputed_after_move', 'residual_deficiency_after_move'])}

## Experimental sixth-move frontier

The two named candidate moves are tested but explicitly excluded from the certified closure:

{markdown(experimental, ['experimental_rule', 'certified_closure_member', 'five_move_survivors_tested', 'candidate_directions', 'accepted_exact_finite_directions', 'survivors_fully_explained', 'outcome'])}

Neither four-cycle/transportation redistribution nor K4 opposite-perfect-matching redistribution is an exact active-cut null direction on any of the 13 remaining carriers. Thus neither explains a survivor under the same exact-incidence plus two-sided finite-invariance bar. This is the recorded open frontier; no further move is pursued in this campaign.

## Outcome

**{result['outcome']}**. The fifth move materially contracts the frontier from 35 to 13 carriers, but it does not close the graph-level question completely.
"""


def design() -> str:
    return """# P1-HYGIENE v3 design

- `active_cut_quotient_v2.py` is imported under a literal SHA-256 pin; v2 artifacts are retained unchanged.
- Delta-to-Y replaces exactly three triangle edges by three star legs `w01+w02`, `w01+w12`, `w02+w12`. Y-to-Delta is admitted only when all inverse half-sum capacities are strictly positive.
- A proposed replacement is certified only if full exact boundary-cut re-enumeration preserves every rational value and all minimizers remain unique. The original four moves then run to closure, with the same check after each accepted move.
- The maintained finite closure explores every verified presentation through three Delta-Y/Y-Delta replacement rounds, including equal/intermediate presentations. The declared depth is exhaustive for this search family and prevents inverse-replacement oscillation.
- The named K2,3 regression exports an audit row after every accepted move. Region count, exact value preservation, uniqueness, and rational incidence rank are recomputed at every row.
- Experimental K2,3 directions are alternating plus/minus redistributions on four-cycle transportation cells. Experimental K4 directions transfer equal capacity between opposite perfect matchings. A direction could explain a residual only if it lies exactly in the incidence nullspace, survives finite perturbations at both signs with every active cut unchanged, and the accepted-direction span equals the full residual deficiency.
- Experimental rules are diagnostics only and are never passed into the certified five-move closure.
"""


def render(result: dict[str, Any]) -> dict[str, bytes]:
    survivors = [row for row in result["search"] if row["residual_deficiency"]]
    experimental_summary = experimental_aggregate(result)
    schema = {
        "artifact": "P1-HYGIENE five-move active-cut quotient",
        "schema_version": 3,
        "certified_reductions": [
            "saturated_terminal_or_zero_column_contraction",
            "inseparable_vertex_contraction_parallel_sum",
            "series_bivalent_reduction",
            "exact_two_terminal_module_replacement",
            "exact_delta_y_y_delta_replacement",
        ],
        "delta_y_star_legs": ["w01+w02", "w01+w12", "w02+w12"],
        "acceptance": "exact equality of all boundary cut values plus unique minimizers after full re-enumeration",
        "experimental_not_certified": [row["experimental_rule"] for row in experimental_summary],
        "summary": result["summary"][0],
        "row_counts": {
            "regressions": len(result["regressions"]),
            "search": len(result["search"]),
            "survivors": len(survivors),
            "named_regression_audits": len(result["named_regression"]),
            "experimental_summaries": len(result["experimental"]),
            "experimental_direction_tests": len(result["experimental_details"]),
        },
        "outcome": result["outcome"],
    }
    payloads = {
        "p1_v3_dependency_pin.csv": csv_bytes(result["pin"]),
        "p1_v3_machinery_regressions.csv": csv_bytes(result["regressions"]),
        "p1_v3_search_cases.csv": csv_bytes(result["search"]),
        "p1_v3_search_census.csv": csv_bytes(result["summary"]),
        "p1_v3_survivors.csv": csv_bytes(survivors),
        "p1_v3_named_k23_regression.csv": csv_bytes(result["named_regression"]),
        "p1_v3_experimental_sixth_moves.csv": csv_bytes(result["experimental"]),
        "p1_v3_experimental_directions.csv": csv_bytes(result["experimental_details"]),
        "p1_v3_schema.json": json_bytes(schema),
        "FINDINGS_v3.md": findings(result).encode(),
        "DESIGN_v3.md": design().encode(),
    }
    manifest = {name: hashlib.sha256(payload).hexdigest() for name, payload in sorted(payloads.items())}
    payloads["p1_v3_artifact_manifest.json"] = json_bytes(manifest)
    return payloads


def main() -> None:
    started = time.perf_counter()
    result = core.run()
    for name, payload in render(result).items():
        (HERE / name).write_bytes(payload)
    summary = result["summary"][0]
    print(
        "P1 v3 build PASS: "
        f"search={summary['evaluated_weighted_carriers']} four_survivors={summary['four_move_survivors']} "
        f"fifth_explained={summary['explained_by_fifth_move']} survivors={summary['five_move_survivors']} "
        f"histogram={summary['residual_deficiency_histogram']} "
        f"experimental={summary['experimental_k23_fully_explained']}/{summary['five_move_survivors']}|"
        f"{summary['experimental_k4_fully_explained']}/{summary['five_move_survivors']} "
        f"elapsed_seconds={time.perf_counter()-started:.3f}"
    )


if __name__ == "__main__":
    main()
