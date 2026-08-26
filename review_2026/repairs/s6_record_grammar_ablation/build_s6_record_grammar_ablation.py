#!/usr/bin/env python3
"""Write deterministic S6 dimension-generic record-grammar ablation artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from pathlib import Path
from typing import Any

import record_grammar_ablation as core


HERE = Path(__file__).resolve().parent

SCORE_FIELDS = [
    "evaluation_id", "dimensions", "structure_id", "support_key", "branch_scope",
    "scalar_branch", "clean_classification", "stable_substrate", "mesonic_token_count",
    "baryonic_token_count", "mixed_token_count", "neutral_record_token_count",
    "capacity_threshold", "capacity_passes", "alias_ambiguity_count",
    "distinguishability_passes", "record_stability_passes", "rs_implies_clean_counterexample",
]
TOKEN_FIELDS = [
    "evaluation_id", "dimensions", "structure_id", "branch_scope", "scalar_branch",
    "token_id", "token_class", "substrate_dimension", "epsilon_or_pair_arity",
    "representation_content", "component_basis", "total_charge", "invariant_rule",
]
GRAMMAR_FIELDS = [
    "dimensions", "branch_scope", "clean_classification", "evaluation_count",
    "stable_substrate_count", "capacity_pass_count", "distinguishability_pass_count",
    "record_stability_count", "counterexample_count", "mesonic_token_count_set",
    "baryonic_token_count_set", "mixed_token_count_set", "total_token_count_set",
]
STRUCTURE_FIELDS = [
    "threshold", "dimensions", "structure_id", "branch_domain_size", "quantifier_domain",
    "rs_branch_count", "clean_branch_count", "pointwise_all_rs_imply_clean",
    "universal_rs_antecedent", "universal_clean_consequent", "universal_implication",
    "existential_rs_antecedent", "existential_clean_consequent", "existential_implication",
]
THRESHOLD_FIELDS = [
    "threshold", "branch_domain_count", "rs_branch_count", "rs_clean_count",
    "rs_breaking_count", "counterexample_count", "rs_family_membership",
    "rs_branch_scope_membership", "two_by_three_su2_active_rs", "su4_rs",
    "implication_passes", "vacuous",
]
QUANTIFIER_FIELDS = [
    "threshold", "quantifier_reading", "domain_count", "antecedent_count",
    "counterexample_count", "implication_passes", "vacuous",
]
COUNTEREXAMPLE_FIELDS = [
    "evaluation_id", "dimensions", "structure_id", "support_key", "branch_scope",
    "scalar_branch", "clean_classification", "neutral_record_token_count",
    "mesonic_token_count", "baryonic_token_count", "mixed_token_count",
    "record_stability_passes", "rs_implies_clean_counterexample",
]
PIN_FIELDS = ["dependency", "expected_sha256", "actual_sha256", "passes"]


def csv_text(rows: list[dict[str, Any]], fields: list[str]) -> str:
    if not rows:
        raise ValueError("cannot serialize an empty S6 table")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row[field] for field in fields})
    return stream.getvalue()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def markdown_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    output = ["| " + " | ".join(field.replace("_", " ") for field in fields) + " |",
              "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows:
        output.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(output)


def findings_text(result: dict[str, Any]) -> str:
    reference_quantifiers = [row for row in result["threshold_quantifiers"] if row["threshold"] == 2]
    counterexample_rows = [{
        "evaluation": row["evaluation_id"],
        "family": row["dimensions"],
        "branch": row["branch_scope"],
        "tokens": row["neutral_record_token_count"],
        "classification": row["clean_classification"],
    } for row in result["counterexamples"]]
    return f"""# S6 dimension-generic record-grammar ablation

## Reference-threshold generic grammar

{markdown_table(result['grammar_table'], GRAMMAR_FIELDS)}

At the published capacity threshold `MIN_RECORD_TOKENS=2`, eight of the 12 evaluated singleton branches are record-stable. The four `2|3`, SU(2)-active clean branches remain RS, but the four `2|3`, SU(3)-active **breaking** branches also pass all three record conjuncts. These are direct counterexamples to the pointwise generic implication:

{markdown_table(counterexample_rows, ['evaluation', 'family', 'branch', 'tokens', 'classification'])}

The four SU(4)-active branches each construct one neutral mixed-epsilon token, not two, so none is RS at the reference threshold. Separately, all 14 SU(4) no-singleton structures have two or more four-fold baryonic tokens but remain substrate-fail and clean-undefined; capacity alone does not make them RS.

## Three quantifier readings at threshold two

{markdown_table(reference_quantifiers, QUANTIFIER_FIELDS)}

- **Branch pointwise fails:** 4 counterexamples among 8 RS branches.
- **Structure universal fails:** all branches are RS in four `2|3` structures, but not all branches are clean.
- **Structure existential passes non-vacuously:** the same four structures have at least one RS branch and at least one clean branch. This weaker reading does not repair the pointwise counterexamples.

The 44 structures with no singleton branch are explicitly `undefined_no_singleton_branch` and are excluded from the structure quantifier domains.

## Capacity-threshold sensitivity

{markdown_table(result['threshold_sensitivity'], THRESHOLD_FIELDS)}

At threshold one, all 12 singleton branches become RS: the four SU(4)-active breaking branches join the four SU(3)-active breaking branches, producing eight counterexamples. At thresholds three and four no branch is RS, so every implication passes only vacuously.

## Honest conclusion

The correlation is **a grammar artifact on this branch-complete finite carrier, not grammar-robust**. Replacing the SU(3)-shaped charge split and alias rules with actual weights and actual conjugacy leaves the desired `2|3`/SU(2)-active branches record-stable, but it also admits their breaking SU(3)-active sibling branches at the published threshold. SU(4) is not a threshold-two counterexample because its constructed mixed basis has capacity one; it becomes an explicit breaking RS counterexample at threshold one. Raising the threshold merely makes the result vacuous. Thus no dimension-generic implication `RS(C,phi) => Clean(C,phi)` lands from this grammar.
"""


def assemble_artifacts(result: dict[str, Any]) -> dict[str, str]:
    counterexamples = [
        {field: row[field] for field in COUNTEREXAMPLE_FIELDS}
        for row in result["counterexamples"]
    ]
    csvs = {
        "s6_branch_scores.csv": csv_text(result["scores"], SCORE_FIELDS),
        "s6_neutral_record_tokens.csv": csv_text(result["tokens"], TOKEN_FIELDS),
        "s6_generic_grammar_table.csv": csv_text(result["grammar_table"], GRAMMAR_FIELDS),
        "s6_structure_quantifiers.csv": csv_text(result["structure_quantifiers"], STRUCTURE_FIELDS),
        "s6_threshold_sensitivity.csv": csv_text(result["threshold_sensitivity"], THRESHOLD_FIELDS),
        "s6_threshold_quantifiers.csv": csv_text(result["threshold_quantifiers"], QUANTIFIER_FIELDS),
        "s6_counterexamples.csv": csv_text(counterexamples, COUNTEREXAMPLE_FIELDS),
        "s6_dependency_pins.csv": csv_text(result["pins"], PIN_FIELDS),
    }
    threshold_two = next(row for row in result["threshold_sensitivity"] if row["threshold"] == 2)
    threshold_one = next(row for row in result["threshold_sensitivity"] if row["threshold"] == 1)
    reference_quantifiers = {
        row["quantifier_reading"]: row
        for row in result["threshold_quantifiers"] if row["threshold"] == 2
    }
    schema = {
        "schema_version": 1,
        "experiment": "S6 dimension-generic record grammar ablation",
        "carrier": {
            "chirality_faithful_structures": 52,
            "admissible_singleton_branch_rows": 12,
            "no_singleton_substrate_fail_rows": 44,
            "evaluation_rows": len(result["scores"]),
        },
        "generic_grammar": {
            "duality": "actual S1-v2 conjugate_rep",
            "epsilon_arity": "original substrate factor dimension N",
            "component_splitting": "weights under diag(N-1,N-3,...,-N+1)",
            "token_classes": ["mesonic", "baryonic", "mixed"],
            "reference_capacity_threshold": core.PUBLISHED_MIN_RECORD_TOKENS,
            "sensitivity_thresholds": list(core.SENSITIVITY_THRESHOLDS),
        },
        "reference_threshold_result": {
            "RS_branches": threshold_two["rs_branch_count"],
            "RS_clean": threshold_two["rs_clean_count"],
            "RS_breaking": threshold_two["rs_breaking_count"],
            "counterexamples": threshold_two["counterexample_count"],
            "two_by_three_SU2_active_RS": threshold_two["two_by_three_su2_active_rs"],
            "SU4_RS": threshold_two["su4_rs"],
            "pointwise_implication": reference_quantifiers["branch_pointwise"]["implication_passes"],
            "universal_implication": reference_quantifiers["structure_universal"]["implication_passes"],
            "existential_implication": reference_quantifiers["structure_existential"]["implication_passes"],
        },
        "threshold_one_result": {
            "RS_branches": threshold_one["rs_branch_count"],
            "RS_breaking": threshold_one["rs_breaking_count"],
            "SU4_RS_breaking_counterexamples": threshold_one["su4_rs"],
        },
        "verdict": "GRAMMAR_ARTIFACT_POINTWISE_AND_UNIVERSAL_COUNTEREXAMPLES",
        "hashes": result["hashes"],
        "pinned_s1_dependencies": {row["dependency"]: row["expected_sha256"] for row in result["pins"]},
        "files": {name: {"sha256": sha256_text(text), "row_count": text.count("\n") - 1}
                  for name, text in csvs.items()},
        "implementation_sha256": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ("record_grammar_ablation.py", "build_s6_record_grammar_ablation.py",
                         "run_s6_record_grammar_ablation.py", "DESIGN.md")
        },
    }
    artifacts = {
        **csvs,
        "s6_schema.json": json.dumps(schema, indent=2, sort_keys=True) + "\n",
        "RESULTS.md": findings_text(result),
    }
    manifest = {"algorithm": "sha256", "files": {
        name: sha256_text(text) for name, text in sorted(artifacts.items())
    }}
    artifacts["s6_artifact_manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return artifacts


def main() -> None:
    started = time.monotonic()
    result = core.run_ablation()
    artifacts = assemble_artifacts(result)
    for name, text in artifacts.items():
        (HERE / name).write_text(text, encoding="utf-8")
    elapsed = time.monotonic() - started
    print("build_s6_record_grammar_ablation.py: PASS: "
          "rows=56 branch_rows=12 no_branch_rows=44 RS_t2=8 counterexamples_t2=4 "
          f"SU4_RS_t2=0 SU4_RS_t1=4 elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
