#!/usr/bin/env python3
"""Write deterministic S6-ABLATION-3 token-completeness artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from pathlib import Path
from typing import Any

import record_grammar_ablation_v3 as core


HERE = Path(__file__).resolve().parent


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise ValueError("refusing to write headerless CSV")
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


def results_note(result: dict[str, Any]) -> str:
    t2 = [row for row in result["thresholds"] if row["threshold"] == 2]
    q2 = [row for row in result["quantifiers"] if row["threshold"] == 2]
    regression = result["eval_049_regression"][0]
    return f"""# S6-ABLATION-3: token-completeness probe

## Bounded census

{markdown(result['census'], ['evaluation_id', 'dimensions', 'branch_scope', 'clean_classification', 'undressed_operator_count', 'operators_with_dressed_lift_count', 'dressed_new_operator_count', 'inclusive_quotient_operator_count', 'clean_branch_gains_dressed_tokens'])}

The declared search has fermion arity `{core.FERMION_ARITY_MIN}..{core.FERMION_ARITY_MAX}`, at most `{core.SCALAR_INSERTION_MAX}` total `phi`/`phi-dagger` insertions, and total constituent count at most `{core.TOTAL_CONSTITUENT_CAP}`. Four covers the largest residual epsilon arity (SU(3)) plus one. Every row has zero computed UV and residual U(1) charge and positive exact LR singlet multiplicities in both representation products. These are candidate channels under the declared token grammar. The channel count `min(dim UV singlets, dim residual singlets)` is an upper bound on a restriction-map rank, not its computation. No map from UV invariants to the selected residual component content, nonzero VEV image, or linearly independent invariant-operator basis is certified. Candidate lifts with identical residual component content and channel index that differ only by insertions of the same branch VEV are identified by convention.

`operators_with_dressed_lift_count` includes quotient classes also possessing an undressed lift; `dressed_new_operator_count` is the disjoint increment, and `inclusive_quotient_operator_count` is the union. All four clean branches gain 18 dressed-new operators, so dressing is applied symmetrically rather than only to breaking branches.

## Mandatory eval_049 regression

The operator `{regression['residual_operator_notation']}` is present with UV lift `{regression['required_uv_lift']}` (enumerated constituent lift `{regression['enumerated_uv_lift']}`). Its original-charge equation is `{regression['uv_charge_equation']}` and its residual-charge equation is `{regression['residual_charge_equation']}`. The UV and residual exact singlet multiplicities are `{regression['required_operator_uv_singlet_multiplicity']}` and `{regression['required_operator_residual_singlet_multiplicity']}`. The v1 spectator-Cartan token survives: `{regression['v1_spectator_cartan_token_survives_v3']}`; the residual-U(1) spectator coefficient remains `{regression['spectator_cartan_coefficient']}`. Regression passes: `{regression['regression_passes']}`.

## Threshold-two results

{markdown(t2, ['counting_convention', 'branch_domain_count', 'rs_branch_count', 'rs_clean_count', 'rs_breaking_count', 'counterexample_count', 'counterexample_ids', 'implication_passes', 'vacuous'])}

The complete bounded undressed candidate census already selects every branch because higher-arity candidate monomials add tokens beyond v2's chosen meson/epsilon generators. Scalar dressing then adds further candidate labels but does not change the threshold-2 binary. For comparison, frozen v2's restricted undressed generator grammar selected 4 clean branches and no breaking branch. Consequently the data do **not** support the narrower phrase “holds iff scalar-dressed composites are excluded”: completeness of the undressed candidate definition also matters.

## Quantifier readings at threshold two

{markdown(q2, ['counting_convention', 'quantifier_reading', 'domain_count', 'antecedent_count', 'counterexample_count', 'implication_passes', 'vacuous'])}

## Outcome ruling input

{markdown(result['outcome_ruling'], ['token_definition', 'scalar_dressed_records_included', 'rs_branch_count', 'rs_clean_count', 'rs_breaking_count', 'counterexample_count', 'pointwise_implication_passes', 'ruling'])}

**{result['outcome']}**. Under both complete bounded candidate conventions, all three readings fail. The existential failures are the four SU(4)-alone structures, which have selected breaking branches and no clean branch; the four selected `2|3` structures do retain a clean sibling. The certified conclusion is therefore stronger than scalar-dressing sensitivity alone: `RS => clean` is token-definition-sensitive, and on this bounded complete candidate census it is false both without and with scalar dressings. The restricted v2 generator grammar is the convention under which it held. Constructing nonzero invariant operators and deciding which persist as actual records requires restriction maps and dynamical record stability beyond token counting.
"""


def design_note() -> str:
    return """# S6-ABLATION-3 design

This version keeps every v1/v2 artifact unchanged and imports the accepted v2 residual stabilizer under a literal SHA-256 pin. `physics_atlas/` is not imported or modified by v3.

## Search bound and exact gates

- Fermion arity is 2 through 4. The largest residual factor is SU(3), whose epsilon arity is three; the requested “largest epsilon plus one” bound is therefore four.
- Up to two insertions total of the singleton branch scalar `phi` and its conjugate `phi-dagger` are allowed. Total constituent count is capped at six.
- Repeated field occurrences follow the inherited Fock-content convention. Grassmann, derivative, equations-of-motion, and dynamical-decay relations are not silently imposed.
- Tensor products are decomposed by the pinned S1-v3 Littlewood--Richardson coefficient implementation. Determinant-height columns are removed algorithmically for SU(N). A candidate enters only if its UV U(1) charge is zero, every UV factor has nonzero exact singlet multiplicity, every residual factor has nonzero exact singlet multiplicity, and its computed residual U(1) charge is zero.
- The candidate channel count is the minimum of the exact UV and residual singlet-space dimensions. It is a declared token count and only an upper bound on the rank of any UV-to-residual restriction map. The map, its nonzero VEV images, and an independent invariant-operator basis have not been constructed.

## VEV quotient and counting conventions

A scalar-dressed candidate token is admissible iff both separately computed singlet/charge gates pass. This does not prove that a UV invariant restricts nontrivially to that token's selected residual component content. Candidate lifts with the same residual component multiset and channel index, differing only by insertions of the same branch VEV, are identified by convention. Distinct Fock contents are retained; further invariant-ring syzygies are not available in the inherited machinery.

Two capacity conventions are reported: `undressed_only` counts quotient operators possessing a zero-scalar lift; `dressed_inclusive` counts the union of undressed and scalar-dressed quotient operators. The census also reports the overlap and the dressed-new increment, preventing the trivial gauge-singlet `phi*phi-dagger` dressing from being double-counted.
"""


def render(result: dict[str, Any]) -> dict[str, bytes]:
    schema = {
        "artifact": "S6-ABLATION-3 token-completeness probe", "schema_version": 3,
        "bounds": result["bounds"], "counting_conventions": list(core.COUNTING_CONVENTIONS),
        "vev_quotient": "same residual component multiset and invariant channel modulo insertions of the same branch VEV",
        "uv_lift_gate": "separate positive UV singlet dimensions and original U(1) neutrality; candidate only",
        "residual_gate": "exact LR singlet under every residual factor and computed residual-U(1) neutral",
        "realization_status": "candidate channels only; UV-to-residual restriction map and nonzero VEV images uncomputed",
        "channel_count_status": "min(UV singlet dimension, residual singlet dimension); upper bound, not certified map rank",
        "row_counts": {"lifts": len(result["lifts"]), "operators": len(result["operators"]),
                       "branch_census": len(result["census"]), "scores": len(result["scores"]),
                       "thresholds": len(result["thresholds"]), "quantifiers": len(result["quantifiers"])},
        "outcome": result["outcome"], "hashes": result["hashes"],
    }
    payloads = {
        "s6_v3_dependency_pins.csv": csv_bytes(result["pins"]),
        "s6_v3_operator_lifts.csv": csv_bytes(result["lifts"]),
        "s6_v3_record_operators.csv": csv_bytes(result["operators"]),
        "s6_v3_branch_token_census.csv": csv_bytes(result["census"]),
        "s6_v3_branch_scores.csv": csv_bytes(result["scores"]),
        "s6_v3_threshold_sensitivity.csv": csv_bytes(result["thresholds"]),
        "s6_v3_structure_quantifiers.csv": csv_bytes(result["structures"]),
        "s6_v3_quantifier_summary.csv": csv_bytes(result["quantifiers"]),
        "s6_v3_eval_049_regression.csv": csv_bytes(result["eval_049_regression"]),
        "s6_v3_outcome_ruling.csv": csv_bytes(result["outcome_ruling"]),
        "s6_v3_schema.json": json_bytes(schema),
        "RESULTS_v3.md": results_note(result).encode(), "DESIGN_v3.md": design_note().encode(),
    }
    manifest = {name: hashlib.sha256(value).hexdigest() for name, value in sorted(payloads.items())}
    payloads["s6_v3_artifact_manifest.json"] = json_bytes(manifest)
    return payloads


def main() -> None:
    started = time.perf_counter()
    result = core.run()
    for name, payload in render(result).items():
        (HERE / name).write_bytes(payload)
    t2 = {row["counting_convention"]: row for row in result["thresholds"] if row["threshold"] == 2}
    print(f"S6 v3 build PASS: lifts={len(result['lifts'])} operators={len(result['operators'])} "
          f"undressed_RS={t2['undressed_only']['rs_branch_count']} "
          f"inclusive_RS={t2['dressed_inclusive']['rs_branch_count']} "
          f"counterexamples={t2['dressed_inclusive']['counterexample_count']} "
          f"elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
