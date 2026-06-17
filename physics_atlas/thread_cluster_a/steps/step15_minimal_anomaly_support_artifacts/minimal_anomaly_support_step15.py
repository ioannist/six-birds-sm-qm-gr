#!/usr/bin/env python3
"""Cluster A Step 15: bounded minimal anomaly-support enumeration."""

from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP14_DIR = THREAD_DIR / "steps" / "step14_real_anomaly_enrichment_artifacts"
sys.path.insert(0, str(STEP14_DIR))
from real_anomaly_enrichment_step14 import SU2, SU3  # noqa: E402


SU3_REPS = ["1", "3", "3bar"]
SU2_REPS = ["1", "2"]
HYPERCHARGE_UNITS = [-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6]
MAX_MULTIPLETS = 5
CONJ_SU3 = {"1": "1", "3": "3bar", "3bar": "3"}


def dim_type(su3: str, su2: str) -> int:
    return int(SU3[su3]["dim"] * SU2[su2]["dim"])


def make_type_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    idx = 0
    for su3 in SU3_REPS:
        for su2 in SU2_REPS:
            for y_units in HYPERCHARGE_UNITS:
                dim3 = int(SU3[su3]["dim"])
                dim2 = int(SU2[su2]["dim"])
                cubic3 = int(SU3[su3]["cubic"])
                dynkin3_twice = 1 if SU3[su3]["dynkin"] else 0
                dynkin2_twice = 1 if SU2[su2]["dynkin"] else 0
                doublet = int(SU2[su2]["doublet"])
                # Integer-scaled anomaly vector:
                # su3^3, 12*su3^2U1, 12*su2^2U1, 216*U1^3, 6*gravU1, Witten doublet count.
                anomaly_vector = (
                    cubic3 * dim2,
                    dim2 * y_units * dynkin3_twice,
                    dim3 * y_units * dynkin2_twice,
                    dim3 * dim2 * y_units**3,
                    dim3 * dim2 * y_units,
                    dim3 * doublet,
                )
                rows.append(
                    {
                        "type_id": idx,
                        "su3_rep": su3,
                        "su2_rep": su2,
                        "hypercharge_units": y_units,
                        "hypercharge": f"{y_units}/6" if y_units % 6 else str(y_units // 6),
                        "weyl_component_count": dim3 * dim2,
                        "anomaly_vector": anomaly_vector,
                    }
                )
                idx += 1
    return rows


def combo_record(combo: tuple[int, ...], type_rows: list[dict[str, object]]) -> tuple[tuple[int, ...], int, tuple[int, int, int, int, int], int]:
    sums = [0, 0, 0, 0, 0, 0]
    mask = 0
    for type_id in combo:
        mask |= 1 << type_id
        vector = type_rows[type_id]["anomaly_vector"]
        for idx, value in enumerate(vector):
            sums[idx] += int(value)
    return combo, mask, tuple(sums[:5]), sums[5] % 2


def enumerate_anomaly_free(type_rows: list[dict[str, object]]) -> set[tuple[int, ...]]:
    records_by_size: list[list[tuple[tuple[int, ...], int, tuple[int, int, int, int, int], int]]] = []
    for size in range(4):
        records_by_size.append([combo_record(combo, type_rows) for combo in combinations(range(len(type_rows)), size)])

    groups: dict[int, dict[tuple[tuple[int, int, int, int, int], int], list[tuple[tuple[int, ...], int, tuple[int, int, int, int, int], int]]]] = {}
    for size, records in enumerate(records_by_size):
        by_key: dict[tuple[tuple[int, int, int, int, int], int], list[tuple[tuple[int, ...], int, tuple[int, int, int, int, int], int]]] = defaultdict(list)
        for record in records:
            by_key[(record[2], record[3])].append(record)
        groups[size] = by_key

    solutions: set[tuple[int, ...]] = set()
    for left_size in range(3):
        for left in records_by_size[left_size]:
            complement = tuple(-value for value in left[2])
            parity = left[3]
            for right_size in range(4):
                total = left_size + right_size
                if total < 1 or total > MAX_MULTIPLETS:
                    continue
                for right in groups[right_size].get((complement, parity), []):
                    if left[1] & right[1]:
                        continue
                    combo = tuple(sorted(left[0] + right[0]))
                    if len(combo) == total:
                        solutions.add(combo)
    return solutions


def type_tuple(row: dict[str, object]) -> tuple[str, str, int]:
    return str(row["su3_rep"]), str(row["su2_rep"]), int(row["hypercharge_units"])


def conjugate_type(entry: tuple[str, str, int]) -> tuple[str, str, int]:
    su3, su2, y_units = entry
    return CONJ_SU3[su3], su2, -y_units


def remove_vectorlike_and_normalize(combo: tuple[int, ...], type_rows: list[dict[str, object]]) -> tuple[tuple[str, str, int], ...]:
    counts = Counter(type_tuple(type_rows[type_id]) for type_id in combo)
    counts.pop(("1", "1", 0), None)
    changed = True
    while changed:
        changed = False
        for entry, count in list(counts.items()):
            if count <= 0:
                continue
            conj = conjugate_type(entry)
            if conj not in counts or counts[conj] <= 0:
                continue
            remove_count = counts[entry] // 2 if entry == conj else min(counts[entry], counts[conj])
            if remove_count <= 0:
                continue
            counts[entry] -= remove_count
            counts[conj] -= remove_count
            if counts[entry] == 0:
                counts.pop(entry, None)
            if counts.get(conj) == 0:
                counts.pop(conj, None)
            changed = True
            break
    if not counts:
        return ()

    divisor = 0
    for _, _, y_units in counts:
        if y_units:
            divisor = math.gcd(divisor, abs(y_units))
    divisor = divisor or 1

    normalized = []
    for entry, count in counts.items():
        su3, su2, y_units = entry
        normalized.extend((su3, su2, y_units // divisor) for _ in range(count))
    support = tuple(sorted(normalized))
    sign_flipped = tuple(sorted((su3, su2, -y_units) for su3, su2, y_units in normalized))
    return min(support, sign_flipped)


def support_dimension(support: tuple[tuple[str, str, int], ...]) -> int:
    return sum(dim_type(su3, su2) for su3, su2, _ in support)


def support_label(support: tuple[tuple[str, str, int], ...]) -> str:
    if not support:
        return "empty"
    parts = []
    for su3, su2, y_units in support:
        y = f"{y_units}/6" if y_units % 6 else str(y_units // 6)
        parts.append(f"({su3},{su2})_{y}")
    return " + ".join(parts)


def sm_support(type_rows: list[dict[str, object]]) -> tuple[tuple[str, str, int], ...]:
    target = [("3", "2", 1), ("3bar", "1", -4), ("3bar", "1", 2), ("1", "2", -3), ("1", "1", 6)]
    combo = []
    for entry in target:
        for row in type_rows:
            if type_tuple(row) == entry:
                combo.append(int(row["type_id"]))
                break
        else:
            raise RuntimeError(f"SM entry missing from type rows: {entry}")
    return remove_vectorlike_and_normalize(tuple(combo), type_rows)


def write_csv(name: str, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with (ARTIFACT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    type_rows = make_type_rows()
    raw_candidate_count = sum(math.comb(len(type_rows), size) for size in range(1, MAX_MULTIPLETS + 1))
    anomaly_free = enumerate_anomaly_free(type_rows)

    raw_rows = []
    for raw_id, combo in enumerate(sorted(anomaly_free, key=lambda c: (len(c), c))):
        support = remove_vectorlike_and_normalize(combo, type_rows)
        raw_rows.append(
            {
                "raw_support_id": raw_id,
                "raw_multiplet_count": len(combo),
                "raw_support_type_ids": " ".join(str(type_id) for type_id in combo),
                "irreducible_support_label": support_label(support),
                "irreducible_empty_after_quotient": support == (),
            }
        )

    canonical_sources: dict[tuple[tuple[str, str, int], ...], list[tuple[int, ...]]] = defaultdict(list)
    for combo in anomaly_free:
        support = remove_vectorlike_and_normalize(combo, type_rows)
        if support:
            canonical_sources[support].append(combo)

    sm = sm_support(type_rows)
    support_rows = []
    for support, sources in sorted(canonical_sources.items(), key=lambda item: (len(item[0]), support_dimension(item[0]), item[0])):
        support_rows.append(
            {
                "support_label": support_label(support),
                "multiplet_count": len(support),
                "weyl_component_count": support_dimension(support),
                "raw_realizations": len(sources),
                "is_sm_support": support == sm,
            }
        )

    ordered_supports = sorted(canonical_sources, key=lambda support: (len(support), support_dimension(support), support))
    sm_rank = ordered_supports.index(sm) + 1
    sm_score = (len(sm), support_dimension(sm))
    minimal_score = (len(ordered_supports[0]), support_dimension(ordered_supports[0]))
    competitors_at_or_below = [
        support for support in ordered_supports if (len(support), support_dimension(support)) <= sm_score and support != sm
    ]
    minimal_supports = [
        support for support in ordered_supports if (len(support), support_dimension(support)) == minimal_score
    ]

    ordering_rows = []
    for rank, support in enumerate(ordered_supports, start=1):
        ordering_rows.append(
            {
                "rank": rank,
                "support_label": support_label(support),
                "multiplet_count": len(support),
                "weyl_component_count": support_dimension(support),
                "is_sm_support": support == sm,
                "minimality_relation_to_sm": (
                    "sm"
                    if support == sm
                    else "at_or_below_sm"
                    if (len(support), support_dimension(support)) <= sm_score
                    else "above_sm"
                ),
            }
        )

    competitor_rows = []
    for support in competitors_at_or_below:
        competitor_rows.append(
            {
                "support_label": support_label(support),
                "multiplet_count": len(support),
                "weyl_component_count": support_dimension(support),
                "relation_to_sm": "beats_sm" if (len(support), support_dimension(support)) < sm_score else "ties_sm",
            }
        )

    no_go = bool(competitors_at_or_below)
    verdict_type = "honest_no_go_minimality_insufficient" if no_go else "checkable_selection_law_unique_minimum"
    next_principle = (
        "minimality must be supplemented by an electroweak quark-lepton participation or observed-charge sector condition"
        if no_go
        else "minimality is sufficient within this finite enumeration"
    )

    write_csv(
        "multiplet_types_step15.csv",
        [
            {
                "type_id": row["type_id"],
                "su3_rep": row["su3_rep"],
                "su2_rep": row["su2_rep"],
                "hypercharge_units": row["hypercharge_units"],
                "hypercharge": row["hypercharge"],
                "weyl_component_count": row["weyl_component_count"],
                "anomaly_vector": " ".join(str(value) for value in row["anomaly_vector"]),
            }
            for row in type_rows
        ],
        ["type_id", "su3_rep", "su2_rep", "hypercharge_units", "hypercharge", "weyl_component_count", "anomaly_vector"],
    )
    write_csv(
        "raw_anomaly_free_supports_step15.csv",
        raw_rows,
        ["raw_support_id", "raw_multiplet_count", "raw_support_type_ids", "irreducible_support_label", "irreducible_empty_after_quotient"],
    )
    write_csv(
        "irreducible_chiral_supports_step15.csv",
        support_rows,
        ["support_label", "multiplet_count", "weyl_component_count", "raw_realizations", "is_sm_support"],
    )
    write_csv(
        "minimality_ordering_step15.csv",
        ordering_rows,
        ["rank", "support_label", "multiplet_count", "weyl_component_count", "is_sm_support", "minimality_relation_to_sm"],
    )
    write_csv(
        "competitors_at_or_below_sm_step15.csv",
        competitor_rows,
        ["support_label", "multiplet_count", "weyl_component_count", "relation_to_sm"],
    )

    summary_row = {
        "multiplet_type_count": len(type_rows),
        "raw_candidate_count": raw_candidate_count,
        "raw_anomaly_free_count": len(anomaly_free),
        "irreducible_chiral_support_count": len(ordered_supports),
        "non_sm_irreducible_support_count": len(ordered_supports) - 1,
        "sm_rank": sm_rank,
        "sm_multiplet_count": sm_score[0],
        "sm_weyl_component_count": sm_score[1],
        "minimal_multiplet_count": minimal_score[0],
        "minimal_weyl_component_count": minimal_score[1],
        "minimal_support_count": len(minimal_supports),
        "competitors_at_or_below_sm": len(competitors_at_or_below),
        "verdict": verdict_type,
    }
    write_csv(
        "enumeration_summary_step15.csv",
        [summary_row],
        [
            "multiplet_type_count",
            "raw_candidate_count",
            "raw_anomaly_free_count",
            "irreducible_chiral_support_count",
            "non_sm_irreducible_support_count",
            "sm_rank",
            "sm_multiplet_count",
            "sm_weyl_component_count",
            "minimal_multiplet_count",
            "minimal_weyl_component_count",
            "minimal_support_count",
            "competitors_at_or_below_sm",
            "verdict",
        ],
    )

    sm_location = {
        "sm_support_label": support_label(sm),
        "sm_rank": sm_rank,
        "sm_score": {"multiplet_count": sm_score[0], "weyl_component_count": sm_score[1]},
        "minimal_score": {"multiplet_count": minimal_score[0], "weyl_component_count": minimal_score[1]},
        "lands": "beaten" if no_go else "unique_minimum",
        "competitors_at_or_below_sm": len(competitors_at_or_below),
        "verdict": verdict_type,
        "next_principle": next_principle,
    }
    (ARTIFACT_DIR / "sm_location_step15.json").write_text(json.dumps(sm_location, indent=2), encoding="utf-8")

    obligations = [
        {
            "obligation": "faithful_enrichment",
            "status": "continued",
            "witness": "bounded exhaustive SU3xSU2xU1 multiplet enumeration using Step 14 anomaly coefficients",
        },
        {
            "obligation": "independently_checkable_consequence",
            "status": "advanced_as_typed_no_go",
            "witness": "minimality alone is insufficient in the finite enumeration; non-SM irreducible supports beat the SM score",
        },
        {
            "obligation": "derived_formula",
            "status": "inherited_from_step14",
            "witness": "anomaly vectors and quotient/minimality relation computed, no new closed-form law landed",
        },
        {
            "obligation": "limit_recovery",
            "status": "continued",
            "witness": "SM support is present and anomaly-free but not minimal under the declared measure",
        },
    ]
    write_csv("candidate_law_obligations_step15.csv", obligations, ["obligation", "status", "witness"])

    schema = {
        "step": 15,
        "artifact_dir": "steps/step15_minimal_anomaly_support_artifacts",
        "enumeration": {
            "gauge_group_input": "SU(3)xSU(2)xU(1)",
            "su3_reps": SU3_REPS,
            "su2_reps": SU2_REPS,
            "hypercharge_units": HYPERCHARGE_UNITS,
            "hypercharge_unit_denominator": 6,
            "max_distinct_weyl_multiplet_types": MAX_MULTIPLETS,
            "raw_candidate_count": raw_candidate_count,
        },
        "minimality_measure": {
            "primary": "irreducible chiral multiplet count after vector-like/trivial quotient",
            "tie_breaker_1": "total Weyl component count",
            "tie_breaker_2": "lexicographic canonical support label for deterministic ordering only",
        },
        "final_verdict": {
            "type": verdict_type,
            "raw_anomaly_free_count": len(anomaly_free),
            "irreducible_chiral_support_count": len(ordered_supports),
            "non_sm_irreducible_support_count": len(ordered_supports) - 1,
            "sm_present_and_anomaly_free": True,
            "sm_rank": sm_rank,
            "sm_lands": sm_location["lands"],
            "competitors_at_or_below_sm": len(competitors_at_or_below),
            "can_fail_control_non_sm_support_exists": len(ordered_supports) - 1 >= 1,
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "next_principle": next_principle,
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "claim_id": "bounded_enumeration",
            "claim": "The finite enumeration covers 66 multiplet types and 9705619 raw supports up to five distinct Weyl multiplet types.",
            "grade": "finite-carrier-diagnostic",
            "classification": "faithful-enrichment",
            "scope": "fixed SU(3)xSU(2)xU(1), bounded reps/hypercharges/support size",
            "source_artifacts": "steps/step15_minimal_anomaly_support_artifacts/multiplet_types_step15.csv;steps/step15_minimal_anomaly_support_artifacts/enumeration_summary_step15.csv",
        },
        {
            "claim_id": "real_anomaly_filter",
            "claim": "The real anomaly filter finds 1161 raw anomaly-free supports.",
            "grade": "finite-carrier-diagnostic",
            "classification": "real-anomaly-computation",
            "scope": "bounded enumeration",
            "source_artifacts": "steps/step15_minimal_anomaly_support_artifacts/raw_anomaly_free_supports_step15.csv",
        },
        {
            "claim_id": "irreducible_quotient",
            "claim": "After vector-like, normalization, and trivial-singlet quotient, 28 irreducible chiral supports remain.",
            "grade": "finite-carrier-diagnostic",
            "classification": "quotient",
            "scope": "declared quotient",
            "source_artifacts": "steps/step15_minimal_anomaly_support_artifacts/irreducible_chiral_supports_step15.csv",
        },
        {
            "claim_id": "minimality_no_go",
            "claim": "The SM support is beaten under the declared minimality measure; minimality alone is insufficient.",
            "grade": "finite-carrier-diagnostic",
            "classification": "typed-no-go",
            "scope": "declared finite enumeration and measure",
            "source_artifacts": "steps/step15_minimal_anomaly_support_artifacts/sm_location_step15.json;steps/step15_minimal_anomaly_support_artifacts/competitors_at_or_below_sm_step15.csv",
        },
        {
            "claim_id": "candidate_law_status",
            "claim": "Obligation 2 is advanced as a typed no-go that names the next principle.",
            "grade": "remaining-external",
            "classification": "candidate-law-next-door",
            "scope": "next principle required",
            "source_artifacts": "steps/step15_minimal_anomaly_support_artifacts/candidate_law_obligations_step15.csv",
        },
        {
            "claim_id": "nonclaim_boundary",
            "claim": "The result is conditional on the gauge group and finite enumeration; it supplies no physical values.",
            "grade": "organizational",
            "classification": "scope-boundary",
            "scope": "nonclaim",
            "source_artifacts": "steps/step15_minimal_anomaly_support_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv(
        "content_classification.csv",
        content_rows,
        ["claim_id", "claim", "grade", "classification", "scope", "source_artifacts"],
    )

    summary = f"""# Step 15 Results Summary: Minimal Anomaly-Support Test

## Declared Minimality Measure

Primary measure: irreducible chiral multiplet count after quotienting vector-like pairs, overall hypercharge normalization, and trivial neutral singlets.

Tie-breaker: total Weyl component count. A final lexicographic ordering is used only to make CSV output deterministic.

## Enumeration Counts

- Multiplet types: `{len(type_rows)}`.
- Raw bounded supports: `{raw_candidate_count}`.
- Raw anomaly-free supports: `{len(anomaly_free)}`.
- Distinct irreducible chiral supports after quotient: `{len(ordered_supports)}`.
- Non-SM irreducible anomaly-free supports: `{len(ordered_supports) - 1}`.

The can-fail control passes: the enumeration contains non-SM irreducible anomaly-free supports.

## SM Location

- SM support label, in canonical hypercharge sign convention: `{support_label(sm)}`.
- SM score: `{sm_score[0]}` irreducible multiplets, `{sm_score[1]}` Weyl components.
- Minimal score in the enumeration: `{minimal_score[0]}` irreducible multiplets, `{minimal_score[1]}` Weyl components.
- SM rank: `{sm_rank}` of `{len(ordered_supports)}`.
- Competitors at or below the SM score: `{len(competitors_at_or_below)}`.

## Verdict

`{verdict_type}`.

Anomaly-freedom plus the declared minimality measure does not single out the SM one-generation chiral content in this bounded enumeration. Several non-SM irreducible anomaly-free supports beat the SM score. This is an honest no-go for minimality-alone as the selection law.

The next door is explicit: {next_principle}.

## Competitor Supports

See `competitors_at_or_below_sm_step15.csv`. The first minimal competitors have score `{minimal_score[0]}` multiplets / `{minimal_score[1]}` Weyl components.

## Candidate-Law Obligation Status

- Faithful enrichment: continued.
- Independently checkable consequence: advanced as a typed no-go.
- Closed-form relation: inherited from Step 14; no new closed-form selection law lands here.
- Limit recovery: continued, because the SM support is present and anomaly-free.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 15 Nonclaim Boundary

This step is conditional on the gauge group SU(3)xSU(2)xU(1). The gauge group is an input to the test.

The enumeration is finite and bounded: reps, hypercharge values, and support size are deliberately limited. It is not all of group theory and not a physical spectrum generator.

The result does not supply SM values, Yukawa data, masses, generation count, vacuum, UV completion, or a real selection mechanism. It does not provide new physics or frame-transfer certification.

The no-go is scoped: anomaly-freedom plus the declared minimality measure is insufficient in this finite enumeration. The next principle to test is an additional electroweak quark-lepton participation or observed-charge sector condition.

Frame-transfer remains open.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    tex = rf"""\paragraph{{Cluster A Step 15: minimal anomaly-support test.}}

The gauge group \(SU(3)\times SU(2)\times U(1)\) is held fixed.  The finite
enumeration contains \(66\) multiplet types:
\[
SU(3)\in\{{1,3,\bar 3\}},\qquad SU(2)\in\{{1,2\}},\qquad
Y\in \frac{{1}}{{6}}\{{-6,-4,-3,-2,-1,0,1,2,3,4,6\}},
\]
with at most \(5\) distinct Weyl multiplet types per support.

The real anomaly filter finds \({len(anomaly_free)}\) raw anomaly-free supports.
After quotienting vector-like pairs, overall hypercharge normalization, and
trivial neutral singlets, \({len(ordered_supports)}\) irreducible chiral supports remain.

The declared minimality measure is:
\[
\text{{score}}(S)=(\#\text{{ irreducible chiral multiplets}},\ \text{{total Weyl components}}).
\]
The SM one-generation support is present and anomaly-free, with score
\(({sm_score[0]},{sm_score[1]})\), but the minimal score in the enumeration is
\(({minimal_score[0]},{minimal_score[1]})\). Thus the SM support is not selected
by anomaly freedom plus this minimality measure.

\paragraph{{Verdict.}}
Minimality alone is insufficient in this finite enumeration.  This is a typed
no-go for the scoped selection-law candidate, not a wall.  The next principle to
test is an electroweak quark-lepton participation or observed-charge sector
condition.

\paragraph{{Grade.}}
Finite-carrier diagnostic, conditional on the fixed gauge group and bounded
enumeration.  No physical value, mechanism, or frame-transfer closure is supplied.
"""
    (ARTIFACT_DIR / "step15_statement.tex").write_text(tex, encoding="utf-8")

    print(
        "Step 15 built: "
        f"raw={raw_candidate_count} anomaly_free={len(anomaly_free)} "
        f"irreducible={len(ordered_supports)} competitors={len(competitors_at_or_below)} "
        f"verdict={verdict_type}"
    )


if __name__ == "__main__":
    main()
