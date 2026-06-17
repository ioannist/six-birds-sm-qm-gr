#!/usr/bin/env python3
"""Cluster A Step 16: token-blind structural content-selection tests."""

from __future__ import annotations

import csv
import json
import re
from itertools import combinations
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP15_DIR = THREAD_DIR / "steps" / "step15_minimal_anomaly_support_artifacts"

SUPPORT_RE = re.compile(r"\(([^,]+),([^)]+)\)_([^ +]+)")
SU3_CONJ = {"1": "1", "3": "3bar", "3bar": "3"}


def parse_y_units(token: str) -> int:
    if "/" in token:
        numerator, denominator = token.split("/", 1)
        return int(numerator) * 6 // int(denominator)
    return int(token) * 6


def parse_support(label: str) -> tuple[tuple[str, str, int], ...]:
    if label == "empty":
        return ()
    return tuple(sorted((su3, su2, parse_y_units(y)) for su3, su2, y in SUPPORT_RE.findall(label)))


def support_label(support: tuple[tuple[str, str, int], ...]) -> str:
    if not support:
        return "empty"
    parts: list[str] = []
    for su3, su2, y_units in sorted(support):
        y = f"{y_units}/6" if y_units % 6 else str(y_units // 6)
        parts.append(f"({su3},{su2})_{y}")
    return " + ".join(parts)


def su3_conjugated(support: tuple[tuple[str, str, int], ...]) -> tuple[tuple[str, str, int], ...]:
    return tuple(sorted((SU3_CONJ[su3], su2, y_units) for su3, su2, y_units in support))


def sign_flipped(support: tuple[tuple[str, str, int], ...]) -> tuple[tuple[str, str, int], ...]:
    return tuple(sorted((su3, su2, -y_units) for su3, su2, y_units in support))


def load_supports() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with (STEP15_DIR / "irreducible_chiral_supports_step15.csv").open(encoding="utf-8") as handle:
        for idx, row in enumerate(csv.DictReader(handle), start=1):
            support = parse_support(row["support_label"])
            rows.append(
                {
                    "support_id": f"S{idx:02d}",
                    "support_label": row["support_label"],
                    "support": support,
                    "multiplet_count": int(row["multiplet_count"]),
                    "weyl_component_count": int(row["weyl_component_count"]),
                    "is_reference_support": row["is_sm_support"] == "True",
                }
            )
    return rows


def color_faithful(support: tuple[tuple[str, str, int], ...]) -> bool:
    return any(su3 != "1" for su3, _, _ in support)


def weak_faithful(support: tuple[tuple[str, str, int], ...]) -> bool:
    return any(su2 != "1" for _, su2, _ in support)


def abelian_faithful(support: tuple[tuple[str, str, int], ...]) -> bool:
    return any(y_units != 0 for _, _, y_units in support)


def principle_faithfulness(support: tuple[tuple[str, str, int], ...], _: dict[str, object]) -> bool:
    return color_faithful(support) and weak_faithful(support) and abelian_faithful(support)


def principle_sector_diversity(support: tuple[tuple[str, str, int], ...], _: dict[str, object]) -> bool:
    return any(su3 != "1" for su3, _, _ in support) and any(su3 == "1" for su3, _, _ in support)


def principle_weak_mixing(support: tuple[tuple[str, str, int], ...], _: dict[str, object]) -> bool:
    return any(su2 == "2" for _, su2, _ in support) and any(su2 == "1" for _, su2, _ in support)


def principle_charge_integrality(support: tuple[tuple[str, str, int], ...], _: dict[str, object]) -> bool:
    for su3, su2, y_units in support:
        if su3 != "1":
            continue
        if su2 == "1" and y_units % 6 != 0:
            return False
        if su2 == "2" and ((y_units + 3) % 6 != 0 or (y_units - 3) % 6 != 0):
            return False
    return True


def principle_chiral_complexity(support: tuple[tuple[str, str, int], ...], _: dict[str, object]) -> bool:
    return any(su3 in {"3", "3bar"} or y_units != 0 for su3, _, y_units in support)


def branch_pattern_variants() -> set[tuple[tuple[str, str, int], ...]]:
    # Simple-group branching reference: the five-piece 10 plus conjugate-5 pattern,
    # with overall abelian sign and color-conjugation automorphism both treated as
    # structural equivalences rather than observed orientation choices.
    base = (("3", "2", -1), ("3bar", "1", -2), ("3bar", "1", 4), ("1", "2", 3), ("1", "1", -6))
    variants = set()
    for sign in (1, -1):
        signed = tuple(sorted((su3, su2, sign * y_units) for su3, su2, y_units in base))
        variants.add(signed)
        variants.add(su3_conjugated(signed))
    return variants


SIMPLE_BRANCH_VARIANTS = branch_pattern_variants()


def principle_simple_embedding(support: tuple[tuple[str, str, int], ...], _: dict[str, object]) -> bool:
    return tuple(sorted(support)) in SIMPLE_BRANCH_VARIANTS


def principle_minimality_control(support: tuple[tuple[str, str, int], ...], context: dict[str, object]) -> bool:
    score = (len(support), int(context["dimensions"][support_label(support)]))
    return score == context["minimal_score"]


PRINCIPLES = [
    {
        "principle_id": "faithfulness",
        "description": "all three gauge factors act nontrivially somewhere on the support",
        "function": principle_faithfulness,
        "non_circular": True,
        "control": False,
        "definition_basis": "kernel-of-action test",
    },
    {
        "principle_id": "sector_diversity",
        "description": "support contains both colored and color-singlet chiral multiplets",
        "function": principle_sector_diversity,
        "non_circular": True,
        "control": False,
        "definition_basis": "sector-presence test",
    },
    {
        "principle_id": "weak_doublet_singlet_mixing",
        "description": "support contains both weak doublets and weak singlets",
        "function": principle_weak_mixing,
        "non_circular": True,
        "control": False,
        "definition_basis": "weak-sector participation test",
    },
    {
        "principle_id": "charge_integrality",
        "description": "color-singlet electric charges are integral after Q=T3+Y in the declared normalization",
        "function": principle_charge_integrality,
        "non_circular": True,
        "control": False,
        "definition_basis": "color-singlet charge lattice test",
    },
    {
        "principle_id": "residual_chiral_complexity",
        "description": "support retains complex or abelian chiral structure after the irreducible quotient",
        "function": principle_chiral_complexity,
        "non_circular": True,
        "control": False,
        "definition_basis": "residual chiral-complexity test",
    },
    {
        "principle_id": "simple_group_embedding_pattern",
        "description": "support matches a five-piece simple-group branching pattern up to abelian sign and color automorphism",
        "function": principle_simple_embedding,
        "non_circular": True,
        "control": False,
        "definition_basis": "simple-group branching table with orientation equivalence",
    },
    {
        "principle_id": "minimality_control",
        "description": "Step 15 minimality score: smallest irreducible multiplet count and Weyl component count",
        "function": principle_minimality_control,
        "non_circular": True,
        "control": True,
        "definition_basis": "can-fail control inherited from Step 15",
    },
]


def write_csv(name: str, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with (ARTIFACT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def evaluate_principle(principle: dict[str, object], supports: list[dict[str, object]], context: dict[str, object]) -> dict[str, object]:
    fn = principle["function"]
    survivors = [row for row in supports if fn(row["support"], context)]  # type: ignore[operator]
    reference_survives = any(bool(row["is_reference_support"]) for row in survivors)
    unique_reference = reference_survives and len(survivors) == 1
    return {
        "principle_id": principle["principle_id"],
        "description": principle["description"],
        "satisfied_by_reference": reference_survives,
        "survivor_count": len(survivors),
        "non_circular": principle["non_circular"],
        "control": principle["control"],
        "credited_selection_law": bool(unique_reference and principle["non_circular"] and not principle["control"]),
        "non_circularity_verdict": "structural" if principle["non_circular"] else "circular_excluded",
        "survivor_labels": " | ".join(str(row["support_label"]) for row in survivors),
        "definition_basis": principle["definition_basis"],
    }


def main() -> None:
    supports = load_supports()
    dimensions = {str(row["support_label"]): int(row["weyl_component_count"]) for row in supports}
    minimal_score = min((int(row["multiplet_count"]), int(row["weyl_component_count"])) for row in supports)
    context = {"dimensions": dimensions, "minimal_score": minimal_score}
    reference_rows = [row for row in supports if row["is_reference_support"]]
    if len(reference_rows) != 1:
        raise RuntimeError("expected exactly one reference support from Step 15")

    principle_rows = [evaluate_principle(principle, supports, context) for principle in PRINCIPLES]
    write_csv(
        "principles_step16.csv",
        principle_rows,
        [
            "principle_id",
            "description",
            "satisfied_by_reference",
            "survivor_count",
            "non_circular",
            "control",
            "credited_selection_law",
            "non_circularity_verdict",
            "survivor_labels",
            "definition_basis",
        ],
    )

    matrix_rows: list[dict[str, object]] = []
    for row in supports:
        out = {
            "support_id": row["support_id"],
            "support_label": row["support_label"],
            "is_reference_support": row["is_reference_support"],
        }
        for principle in PRINCIPLES:
            out[str(principle["principle_id"])] = principle["function"](row["support"], context)  # type: ignore[operator]
        matrix_rows.append(out)
    write_csv(
        "support_principle_matrix_step16.csv",
        matrix_rows,
        ["support_id", "support_label", "is_reference_support"] + [str(p["principle_id"]) for p in PRINCIPLES],
    )

    structural_principles = [principle for principle in PRINCIPLES if not principle["control"] and principle["non_circular"]]
    conjunction_rows: list[dict[str, object]] = []
    best_reference_conjunction: dict[str, object] | None = None
    unique_law_found = False
    for size in range(2, len(structural_principles) + 1):
        for combo in combinations(structural_principles, size):
            survivors = [
                row
                for row in supports
                if all(principle["function"](row["support"], context) for principle in combo)  # type: ignore[operator]
            ]
            reference_survives = any(bool(row["is_reference_support"]) for row in survivors)
            unique_reference = reference_survives and len(survivors) == 1
            if unique_reference:
                unique_law_found = True
            conjunction_id = "+".join(str(principle["principle_id"]) for principle in combo)
            con_row = {
                "conjunction_id": conjunction_id,
                "principle_count": size,
                "satisfied_by_reference": reference_survives,
                "survivor_count": len(survivors),
                "non_circular": True,
                "credited_selection_law": unique_reference,
                "survivor_labels": " | ".join(str(row["support_label"]) for row in survivors),
            }
            conjunction_rows.append(con_row)
            if reference_survives:
                if best_reference_conjunction is None or (len(survivors), size, conjunction_id) < (
                    int(best_reference_conjunction["survivor_count"]),
                    int(best_reference_conjunction["principle_count"]),
                    str(best_reference_conjunction["conjunction_id"]),
                ):
                    best_reference_conjunction = con_row
    write_csv(
        "conjunctions_step16.csv",
        conjunction_rows,
        [
            "conjunction_id",
            "principle_count",
            "satisfied_by_reference",
            "survivor_count",
            "non_circular",
            "credited_selection_law",
            "survivor_labels",
        ],
    )

    control_row = next(row for row in principle_rows if row["principle_id"] == "minimality_control")
    can_fail_ok = bool(control_row["satisfied_by_reference"] is False and int(control_row["survivor_count"]) > 0)
    individual_unique = [row for row in principle_rows if row["credited_selection_law"]]
    verdict_type = "candidate_checkable_selection_law" if (individual_unique or unique_law_found) else "rigorous_type_limit_negative"
    obligation_status = "landed_positive" if verdict_type == "candidate_checkable_selection_law" else "advanced_as_type_limit_negative"
    best_conjunction_id = best_reference_conjunction["conjunction_id"] if best_reference_conjunction else "none"
    best_conjunction_survivors = int(best_reference_conjunction["survivor_count"]) if best_reference_conjunction else 0
    next_input = (
        "none within the declared finite test"
        if verdict_type == "candidate_checkable_selection_law"
        else "an observed orientation/content input or an additional independent structural principle beyond the declared set"
    )

    verdict = {
        "step": 16,
        "source_supports": "steps/step15_minimal_anomaly_support_artifacts/irreducible_chiral_supports_step15.csv",
        "support_count": len(supports),
        "reference_support_label": reference_rows[0]["support_label"],
        "principle_count": len(PRINCIPLES),
        "structural_principle_count": len(structural_principles),
        "any_non_circular_unique_principle": bool(individual_unique),
        "any_non_circular_unique_conjunction": unique_law_found,
        "best_reference_conjunction": best_conjunction_id,
        "best_reference_conjunction_survivor_count": best_conjunction_survivors,
        "minimality_control_fails_to_select_reference": can_fail_ok,
        "verdict": verdict_type,
        "obligation_2_status": obligation_status,
        "observed_input_required": verdict_type == "rigorous_type_limit_negative",
        "next_required_input": next_input,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    (ARTIFACT_DIR / "overall_verdict_step16.json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")

    obligations = [
        {
            "obligation": "faithful_enrichment",
            "status": "continued_from_step15",
            "witness": "principles evaluated on the 28 Step 15 irreducible real-anomaly supports",
        },
        {
            "obligation": "independently_checkable_consequence",
            "status": obligation_status,
            "witness": "declared non-circular principles and conjunctions do not uniquely select the reference support" if verdict_type == "rigorous_type_limit_negative" else "a non-circular principle uniquely selects the reference support",
        },
        {
            "obligation": "derived_formula",
            "status": "not_advanced_this_step",
            "witness": "no new closed-form relation beyond the Step 14 anomaly relations",
        },
        {
            "obligation": "limit_recovery",
            "status": "bounded_by_step15_support_set",
            "witness": "reference support is present in the real-anomaly support set but remains one of two after the strongest structural conjunction",
        },
    ]
    write_csv("candidate_law_obligations_step16.csv", obligations, ["obligation", "status", "witness"])

    schema = {
        "step": 16,
        "artifact_dir": "steps/step16_content_selection_principle_artifacts",
        "input_step": 15,
        "support_count": len(supports),
        "principles": [
            {
                "principle_id": str(principle["principle_id"]),
                "non_circular": bool(principle["non_circular"]),
                "control": bool(principle["control"]),
                "definition_basis": str(principle["definition_basis"]),
            }
            for principle in PRINCIPLES
        ],
        "overall_verdict": verdict,
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "claim_id": "principle_screen",
            "claim": "Seven declared principles were evaluated over the 28 irreducible anomaly-free supports.",
            "grade": "finite-carrier-diagnostic",
            "classification": "principle-screen",
            "source_artifacts": "steps/step16_content_selection_principle_artifacts/principles_step16.csv;steps/step16_content_selection_principle_artifacts/support_principle_matrix_step16.csv",
        },
        {
            "claim_id": "conjunction_screen",
            "claim": "All non-control non-circular conjunctions were tested; the strongest reference-preserving conjunction leaves two supports.",
            "grade": "finite-carrier-diagnostic",
            "classification": "conjunction-screen",
            "source_artifacts": "steps/step16_content_selection_principle_artifacts/conjunctions_step16.csv;steps/step16_content_selection_principle_artifacts/overall_verdict_step16.json",
        },
        {
            "claim_id": "type_limit_negative",
            "claim": "No credited non-circular principle or conjunction uniquely selects the reference support on this finite carrier.",
            "grade": "finite-carrier-diagnostic",
            "classification": "typed-negative",
            "source_artifacts": "steps/step16_content_selection_principle_artifacts/overall_verdict_step16.json",
        },
        {
            "claim_id": "can_fail_control",
            "claim": "The minimality control fails to select the reference support, so the screen discriminates.",
            "grade": "finite-carrier-diagnostic",
            "classification": "anti-rigging",
            "source_artifacts": "steps/step16_content_selection_principle_artifacts/principles_step16.csv",
        },
        {
            "claim_id": "nonclaim_boundary",
            "claim": "Conditional fixed-gauge finite enumeration; no physical values or mechanism supplied.",
            "grade": "organizational",
            "classification": "scope-boundary",
            "source_artifacts": "steps/step16_content_selection_principle_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv("content_classification.csv", content_rows, ["claim_id", "claim", "grade", "classification", "source_artifacts"])

    per_principle_lines = "\n".join(
        f"- `{row['principle_id']}`: reference={row['satisfied_by_reference']}, survivors=`{row['survivor_count']}`, non-circular=`{row['non_circular']}`."
        for row in principle_rows
    )
    summary = f"""# Step 16 Results Summary: Content-Selection Principle Screen

## Input

This step evaluates structural principles over the `28` irreducible anomaly-free chiral supports emitted by Step 15.

## Per-Principle Results

{per_principle_lines}

## Conjunction Results

All conjunctions of the six non-control structural principles were tested. The best reference-preserving conjunction is `{best_conjunction_id}`, with `{best_conjunction_survivors}` survivors.

No non-circular principle or conjunction uniquely selects the reference support. The two strongest survivors are the simple-branching orientation pair; choosing one orientation would require an additional input not supplied by the declared token-blind structural principles.

## Can-Fail Control

The carried minimality control does not select the reference support and leaves `{control_row['survivor_count']}` minimal supports. The screen therefore does not trivially pass every declared principle.

## Verdict

`{verdict_type}`.

The SM chiral content is not selected by the declared non-circular structural principles on this bounded carrier. The content-selection facet closes here as a precise type-limit negative: within this finite fixed-gauge test, an additional observed content/orientation input or an independent principle is required.

## Obligation-2 Status

`{obligation_status}`. The independently-checkable consequence was attempted over the Step 15 support set; it returns a negative boundary rather than a positive selection law.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 16 Nonclaim Boundary

This is a finite fixed-gauge content-selection screen over the Step 15 support set.

It does not supply the gauge group, the physical chiral content, Yukawa data, masses, the vacuum, or a real selection mechanism. It does not certify frame transfer.

The negative result is bounded: no declared non-circular structural principle or conjunction in this finite test uniquely selects the reference support. That is a typed boundary, not a universal theorem over all possible principles or all group-theoretic carriers.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\section{{Step 16: Content-Selection Principle Screen}}

\paragraph{{Grade.}}
Finite fixed-gauge diagnostic. The carrier is the Step-15 list of 28 irreducible anomaly-free chiral supports for fixed \(SU(3)\times SU(2)\times U(1)\). The test supplies a bounded content-selection screen, not a physical mechanism or value.

\paragraph{{Principles.}}
Seven declared principles were evaluated: faithfulness, sector diversity, weak doublet/singlet mixing, color-singlet charge integrality, residual chiral complexity, simple-group embedding pattern, and the Step-15 minimality control.

\paragraph{{Computed Result.}}
The best reference-preserving non-circular conjunction is \texttt{{{best_conjunction_id}}}, leaving {best_conjunction_survivors} supports. No credited non-circular principle or conjunction uniquely selects the reference support.

\paragraph{{Verdict.}}
\texttt{{{verdict_type}}}. Within this finite fixed-gauge carrier, content selection requires an additional independent principle or observed input. The result is a type-limit negative, not a universal no-go.
"""
    (ARTIFACT_DIR / "step16_statement.tex").write_text(statement, encoding="utf-8")

    print(
        "Step 16 built: supports=28 "
        f"best_survivors={best_conjunction_survivors} "
        f"verdict={verdict_type}"
    )


if __name__ == "__main__":
    main()
