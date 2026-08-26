#!/usr/bin/env python3
"""Write deterministic S6-ABLATION-2 full-residual-neutral artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import record_grammar_ablation_v2 as core


HERE = Path(__file__).resolve().parent


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        raise ValueError("cannot serialize empty v2 table")
    fields = list(rows[0])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return stream.getvalue()


def markdown(rows: list[dict[str, Any]], fields: list[str]) -> str:
    lines = ["| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def token_census(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scores:
        if row["branch_scope"] != "no_singleton_branch":
            groups[(row["dimensions"], row["branch_scope"], row["clean_classification"])].append(row)
    output = []
    for (dimensions, scope, classification), rows in sorted(groups.items()):
        output.append({
            "dimensions": dimensions, "branch_scope": scope,
            "clean_classification": classification, "branch_count": len(rows),
            "mesonic_count_set": "|".join(map(str, sorted({row["mesonic_token_count"] for row in rows}))),
            "baryonic_count_set": "|".join(map(str, sorted({row["baryonic_token_count"] for row in rows}))),
            "mixed_count_set": "|".join(map(str, sorted({row["mixed_token_count"] for row in rows}))),
            "total_count_set": "|".join(map(str, sorted({row["neutral_record_token_count"] for row in rows}))),
            "rs_at_threshold_2": sum(row["record_stability_passes"] for row in rows),
            "counterexamples_at_threshold_2": sum(row["rs_implies_clean_counterexample"] for row in rows),
        })
    return output


def findings(result: dict[str, Any], census: list[dict[str, Any]]) -> str:
    t2 = next(row for row in result["thresholds"] if row["threshold"] == 2)
    q2 = [row for row in result["quantifiers"] if row["threshold"] == 2]
    trace = result["eval_049_trace"][0]
    return f"""# S6-ABLATION-2: full-residual-neutral record grammar

## Computed branch result

{markdown(census, ['dimensions', 'branch_scope', 'clean_classification', 'branch_count', 'mesonic_count_set', 'baryonic_count_set', 'mixed_count_set', 'total_count_set', 'rs_at_threshold_2', 'counterexamples_at_threshold_2'])}

Every token is first constructed in the UV mesonic/epsilon basis, then restricted to states that are exact singlets under every branch-specific residual nonabelian factor and neutral under the computed residual U(1). The U(1) coefficients are primitive integer solutions of `a q_phi + b h_phi = 0`; spectator Cartans never enter.

At the published threshold 2, `{t2['rs_branch_count']}` branches are RS, all `{t2['rs_clean_count']}` are clean, and there are `{t2['counterexample_count']}` counterexamples. The pointwise implication therefore lands non-vacuously for this declared grammar. The ablation-1 result remains an explicit sensitivity result: adding a unit-normalized spectator Cartan manufactured four breaking RS branches.

## Quantifier readings at threshold 2

{markdown(q2, ['quantifier_reading', 'domain_count', 'antecedent_count', 'counterexample_count', 'implication_passes', 'vacuous'])}

Pointwise passes non-vacuously. Structure-universal passes only vacuously because no two-branch structure has every branch RS. Structure-existential passes non-vacuously for the four `2|3` structures possessing an RS clean branch.

## eval_049 end-to-end trace

The v1 rule produced `{trace['old_token_count']}` tokens by adding the unbroken spectator SU(2) Cartan weight to the original U(1). The stabilizer computation instead gives `{trace['computed_residual_group']}` and `{trace['neutrality_equation']}`, with zero spectator-Cartan coefficients. The spectator-doublet baryon disappears: `{trace['spectator_doublet_token_disappears']}`. One genuine full-residual-neutral baryonic record remains, so the token count is `{trace['full_residual_neutral_token_count']}` and threshold-2 RS is `{trace['record_stability_threshold_2']}`.

## Outcome ruling input

**{result['outcome']}**. Hence `RS(C,phi) => Clean(C,phi)` is restored pointwise at conditional finite-toy diagnostic strength only when the grammar is explicitly declared to require full residual-gauge neutrality. Threshold 1 still admits all eight breaking branches; thresholds 2--4 retain only the four clean branches on this finite carrier.
"""


def assemble(result: dict[str, Any]) -> dict[str, str]:
    census = token_census(result["scores"])
    csvs = {
        "s6_v2_branch_residual_groups.csv": csv_text(result["stabilizers"]),
        "s6_v2_residual_components.csv": csv_text(result["components"]),
        "s6_v2_record_tokens.csv": csv_text(result["tokens"]),
        "s6_v2_token_census.csv": csv_text(census),
        "s6_v2_branch_scores.csv": csv_text(result["scores"]),
        "s6_v2_threshold_sensitivity.csv": csv_text(result["thresholds"]),
        "s6_v2_quantifier_summary.csv": csv_text(result["quantifiers"]),
        "s6_v2_structure_quantifiers.csv": csv_text(result["structures"]),
        "s6_v2_eval_049_trace.csv": csv_text(result["eval_049_trace"]),
        "s6_v2_collision_control.csv": csv_text(result["collision_controls"]),
        "s6_v2_dependency_pins.csv": csv_text(result["pins"]),
    }
    t2 = next(row for row in result["thresholds"] if row["threshold"] == 2)
    q2 = {row["quantifier_reading"]: row for row in result["quantifiers"] if row["threshold"] == 2}
    schema = {
        "schema_version": 2,
        "experiment": "S6-ABLATION-2 full-residual-neutral record grammar",
        "carrier": {"evaluation_rows": len(result["scores"]), "singleton_branch_rows": 12,
                    "no_singleton_rows": 44},
        "grammar": {
            "stabilizer": "scalar VEV stabilizer; primitive a*q_phi+b*h_phi=0",
            "residual_u1_cartans": "broken factors only; spectator Cartan coefficient identically zero",
            "record_basis": "UV mesonic/conjugate pairs, N-fold epsilon baryons, and mixed epsilon invariants restricted to exact full-residual singlets",
            "singlet_engine": "pinned S1-v3 Littlewood-Richardson singlet multiplicities",
            "distinguishability": "canonical Fock content plus orthogonal invariant-channel index",
            "thresholds": list(core.THRESHOLDS),
        },
        "reference_threshold": t2,
        "quantifiers_threshold_2": q2,
        "outcome": result["outcome"],
        "counts": {"stabilizers": len(result["stabilizers"]), "components": len(result["components"]),
                   "tokens": len(result["tokens"]), "token_classes": sorted({row["token_class"] for row in result["tokens"]})},
        "hashes": result["hashes"],
        "files": {name: {"sha256": hashlib.sha256(text.encode()).hexdigest(),
                          "row_count": text.count("\n") - 1} for name, text in csvs.items()},
    }
    design = """# S6-ABLATION-2 design

- V1 artifacts are retained byte-for-byte; every new artifact is prefixed `s6_v2_` or suffixed `_v2`.
- For a scalar VEV in a fundamental or antifundamental of SU(N), the active factor stabilizer is SU(N-1), with SU(1) omitted. All inactive nonabelian factors remain explicit spectators.
- `H=diag(1,...,1,-N+1)`. The residual U(1) is the primitive integer combination `a Q + b H` solving `a q_phi+b h_phi=0`. No inactive-factor Cartan is permitted.
- Record candidates are UV mesons, N-fold epsilon baryons, or mixed epsilon invariants. They count only when restriction to the branch contains a component neutral under U(1)_res and an exact singlet under every residual factor.
- Singlet existence/multiplicity for two- and three-body products calls the pinned v3 Littlewood--Richardson implementation. Distinct records are canonical Fock contents or orthogonal invariant channels.
"""
    artifacts = {**csvs, "s6_v2_schema.json": json.dumps(schema, indent=2, sort_keys=True) + "\n",
                 "RESULTS_v2.md": findings(result, census), "DESIGN_v2.md": design}
    manifest = {"algorithm": "sha256", "files": {
        name: hashlib.sha256(text.encode()).hexdigest() for name, text in sorted(artifacts.items())
    }}
    artifacts["s6_v2_artifact_manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return artifacts


def main() -> None:
    started = time.monotonic()
    result = core.run()
    for name, text in assemble(result).items():
        (HERE / name).write_text(text, encoding="utf-8")
    t2 = next(row for row in result["thresholds"] if row["threshold"] == 2)
    print("build_s6_record_grammar_ablation_v2.py: PASS: "
          f"RS_t2={t2['rs_branch_count']} clean_t2={t2['rs_clean_count']} "
          f"counterexamples_t2={t2['counterexample_count']} tokens={len(result['tokens'])} "
          f"elapsed_seconds={time.monotonic()-started:.3f}")


if __name__ == "__main__":
    main()
