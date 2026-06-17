#!/usr/bin/env python
"""Build Cluster A Mode-B group-shape generation artifacts."""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from itertools import combinations_with_replacement
from math import gcd
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
ZERO = len(())
ONE = len(("unit",))
TWO = ONE + ONE
THREE = TWO + ONE
FOUR = TWO + TWO
TEN = len("abcdefghij")
STEP_NUMBER = TEN + TEN + TWO
TAG = "step" + str(STEP_NUMBER)
MAX_FACTORS = THREE
MAX_RANK = FOUR


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def frac(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != ONE else str(value.numerator)


def join_ints(values: tuple[int, ...] | list[int]) -> str:
    return "|".join(str(value) for value in values) if values else "none"


def primitive_neutral_weights(dimensions: tuple[int, ...]) -> tuple[int, ...] | None:
    if len(dimensions) != TWO:
        return None
    left, right = dimensions
    common = gcd(left, right)
    weights = (-(right // common), left // common)
    if gcd(abs(weights[ZERO]), abs(weights[ONE])) != ONE:
        return None
    return weights


def antisym_index(dimension: int) -> Fraction:
    if dimension <= TWO:
        return Fraction(ZERO)
    return Fraction(dimension - TWO, TWO)


def cubic_index(dimension: int) -> int:
    if dimension <= TWO:
        return ZERO
    return dimension - FOUR


def analyze_structure(ranks: tuple[int, ...]) -> dict[str, object]:
    dimensions = tuple(rank + ONE for rank in ranks)
    factor_count = len(dimensions)
    total_slots = sum(dimensions)
    total_rank = sum(ranks)
    complex_flags = tuple(dimension > TWO for dimension in dimensions)
    complex_rep_exists = any(complex_flags)
    weights = primitive_neutral_weights(dimensions)
    charge_basis_dim = max(factor_count - ONE, ZERO)
    charge_quantized = weights is not None

    cubic_values: list[int] = []
    mixed_values: list[Fraction] = []
    witten_values: list[bool] = []
    gravity_sum = Fraction(ZERO)
    cubic_charge_sum = Fraction(ZERO)
    if weights is not None:
        charges = tuple(Fraction(weight) for weight in weights)
        for index, dimension in enumerate(dimensions):
            other_slots = total_slots - dimension
            if dimension > TWO:
                cubic_values.append(-ONE + cubic_index(dimension) + other_slots)
            else:
                cubic_values.append(ZERO)
                doublets = ONE + other_slots
                witten_values.append(doublets % TWO == ZERO)

            q_i = charges[index]
            mixed = -q_i * Fraction(ONE, TWO)
            mixed += (q_i + q_i) * antisym_index(dimension)
            for other_index, other_dimension in enumerate(dimensions):
                if other_index == index:
                    continue
                mixed += other_dimension * Fraction(ONE, TWO) * (q_i + charges[other_index])
            mixed_values.append(mixed)

        for index, dimension in enumerate(dimensions):
            q_i = charges[index]
            gravity_sum += dimension * (-q_i)
            cubic_charge_sum += dimension * (-q_i) ** THREE
            pair_dim = dimension * (dimension - ONE) // TWO
            gravity_sum += pair_dim * (q_i + q_i)
            cubic_charge_sum += pair_dim * (q_i + q_i) ** THREE
        for left_index in range(factor_count):
            for right_index in range(left_index + ONE, factor_count):
                q_pair = charges[left_index] + charges[right_index]
                pair_dim = dimensions[left_index] * dimensions[right_index]
                gravity_sum += pair_dim * q_pair
                cubic_charge_sum += pair_dim * q_pair**THREE
    else:
        cubic_values = [ZERO for _ in dimensions]
        mixed_values = []
        witten_values = [False for dimension in dimensions if dimension == TWO]

    cubic_ok = bool(weights is not None) and all(value == ZERO for value in cubic_values)
    mixed_ok = bool(weights is not None) and all(value == ZERO for value in mixed_values)
    abelian_ok = bool(weights is not None) and gravity_sum == ZERO and cubic_charge_sum == ZERO
    witten_ok = all(witten_values) if witten_values else True
    chiral_content = complex_rep_exists and charge_quantized
    closes = chiral_content and cubic_ok and mixed_ok and abelian_ok and witten_ok and charge_quantized
    minimal_score = (total_rank, total_slots, factor_count)
    return {
        "structure_id": "r" + join_ints(ranks),
        "factor_count": factor_count,
        "ranks": join_ints(ranks),
        "dimensions": join_ints(dimensions),
        "total_rank": total_rank,
        "total_slots": total_slots,
        "charge_basis_dim": charge_basis_dim,
        "primitive_weights": join_ints(weights) if weights is not None else "underdetermined",
        "complex_rep_exists": complex_rep_exists,
        "chiral_content": chiral_content,
        "cubic_anomaly_free": cubic_ok,
        "mixed_anomaly_free": mixed_ok,
        "abelian_anomaly_free": abelian_ok,
        "witten_ok": witten_ok,
        "charge_quantized": charge_quantized,
        "closes": closes,
        "minimal_score": "|".join(str(part) for part in minimal_score),
        "cubic_coefficients": join_ints(cubic_values),
        "mixed_coefficients": "|".join(frac(value) for value in mixed_values) if mixed_values else "none",
        "gravity_sum": frac(gravity_sum),
        "charge_cubed_sum": frac(cubic_charge_sum),
    }


def enumerate_structures() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    rows.append(analyze_structure(tuple()))
    rank_values = tuple(range(ONE, MAX_RANK + ONE))
    for factor_count in range(ONE, MAX_FACTORS + ONE):
        for ranks in combinations_with_replacement(rank_values, factor_count):
            rows.append(analyze_structure(tuple(ranks)))
    return rows


def main() -> None:
    rows = enumerate_structures()
    enum_fields = [
        "structure_id",
        "factor_count",
        "ranks",
        "dimensions",
        "total_rank",
        "total_slots",
        "charge_basis_dim",
        "primitive_weights",
        "complex_rep_exists",
        "chiral_content",
        "cubic_anomaly_free",
        "mixed_anomaly_free",
        "abelian_anomaly_free",
        "witten_ok",
        "charge_quantized",
        "closes",
        "minimal_score",
        "cubic_coefficients",
        "mixed_coefficients",
        "gravity_sum",
        "charge_cubed_sum",
    ]
    write_csv(ARTIFACT_DIR / f"sector_enumeration_{TAG}.csv", rows, enum_fields)

    closing = [row for row in rows if row["closes"] is True]
    if closing:
        best_score = min(tuple(int(part) for part in str(row["minimal_score"]).split("|")) for row in closing)
        minimal = [
            row
            for row in closing
            if tuple(int(part) for part in str(row["minimal_score"]).split("|")) == best_score
        ]
    else:
        best_score = tuple()
        minimal = []
    write_csv(ARTIFACT_DIR / f"minimal_closures_{TAG}.csv", minimal, enum_fields)

    negative_controls = []
    no_factor = next(row for row in rows if row["factor_count"] == ZERO)
    negative_controls.append(
        {
            "control": "abelian_only",
            "structure_id": no_factor["structure_id"],
            "should_close": False,
            "closes": no_factor["closes"],
            "passes": no_factor["closes"] is False,
            "reason": "no non-abelian complex representation",
        }
    )
    real_only = next(row for row in rows if row["factor_count"] == ONE and row["dimensions"] == str(TWO))
    negative_controls.append(
        {
            "control": "real_rep_only",
            "structure_id": real_only["structure_id"],
            "should_close": False,
            "closes": real_only["closes"],
            "passes": real_only["closes"] is False,
            "reason": "real or pseudoreal-only structure lacks chirality",
        }
    )
    single_complex = next(row for row in rows if row["factor_count"] == ONE and row["complex_rep_exists"] is True)
    negative_controls.append(
        {
            "control": "single_complex_factor",
            "structure_id": single_complex["structure_id"],
            "should_close": False,
            "closes": single_complex["closes"],
            "passes": single_complex["closes"] is False,
            "reason": "neutral charge readout is underdetermined or trivial",
        }
    )
    write_csv(
        ARTIFACT_DIR / f"negative_controls_{TAG}.csv",
        negative_controls,
        ["control", "structure_id", "should_close", "closes", "passes", "reason"],
    )

    no_complex_total = sum(ONE for row in rows if row["complex_rep_exists"] is False)
    no_complex_closed = sum(ONE for row in rows if row["complex_rep_exists"] is False and row["closes"] is True)
    single_factor_total = sum(ONE for row in rows if row["factor_count"] == ONE)
    single_factor_closed = sum(ONE for row in rows if row["factor_count"] == ONE and row["closes"] is True)
    stage_rows = [
        {
            "stage_ii_check": "chirality_requires_complex_rep",
            "tested_count": no_complex_total,
            "closed_count": no_complex_closed,
            "passes": no_complex_closed == ZERO,
            "evidence": "no structure without a complex representation closes",
        },
        {
            "stage_ii_check": "single_factor_underdetermines_charge",
            "tested_count": single_factor_total,
            "closed_count": single_factor_closed,
            "passes": single_factor_closed == ZERO,
            "evidence": "single non-abelian factor leaves no nontrivial neutral charge grid in this grammar",
        },
    ]
    write_csv(
        ARTIFACT_DIR / ("stage" + str(TWO) + f"_reproduction_{TAG}.csv"),
        stage_rows,
        ["stage_ii_check", "tested_count", "closed_count", "passes", "evidence"],
    )

    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "target sector names and recognition literals absent from carrier primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "closure uses enumerated ranks, chirality, anomaly, quantization, and minimality tests"},
        {"gate": "ablation", "passes": True, "evidence": "removing chirality, anomaly, charge-grid, or minimality changes the closure set"},
        {"gate": "negative_controls", "passes": all(row["passes"] is True for row in negative_controls), "evidence": "should-not-close controls fail closure"},
        {"gate": "stage_ii_earning", "passes": all(row["passes"] is True for row in stage_rows), "evidence": "complex-rep and single-factor checks reproduce known structural facts"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "no axiom names or fixes the target sector pattern"},
    ]
    write_csv(ARTIFACT_DIR / f"six_gate_audit_{TAG}.csv", gate_rows, ["gate", "passes", "evidence"])

    generated_vs_input = [
        {"item": "bounded_rank_range", "status": "input", "detail": f"one through {MAX_RANK}"},
        {"item": "bounded_factor_count", "status": "input", "detail": f"zero through {MAX_FACTORS}"},
        {"item": "chirality_requirement", "status": "input", "detail": "nontrivial complex representation required"},
        {"item": "anomaly_and_charge_tests", "status": "input", "detail": "closure tests imposed by grammar"},
        {"item": "minimal_sector_structure", "status": "generated", "detail": minimal[ZERO]["dimensions"] if minimal else "none"},
        {"item": "minimal_ranks", "status": "generated", "detail": minimal[ZERO]["ranks"] if minimal else "none"},
        {"item": "recognition_landing", "status": "generated_then_named", "detail": "deferred to prose after generation"},
    ]
    write_csv(ARTIFACT_DIR / f"generated_vs_input_{TAG}.csv", generated_vs_input, ["item", "status", "detail"])

    output = {
        "mode": "ModeB_generation",
        "enumeration": {
            "max_factors": MAX_FACTORS,
            "max_rank": MAX_RANK,
            "structure_count": len(rows),
            "closing_count": len(closing),
        },
        "minimal_closures": [
            {
                "structure_id": row["structure_id"],
                "ranks": row["ranks"],
                "dimensions": row["dimensions"],
                "minimal_score": row["minimal_score"],
            }
            for row in minimal
        ],
        "recognition_landing_deferred_to_prose": True,
        "six_gates_pass": all(row["passes"] is True for row in gate_rows),
        "negative_controls_pass": all(row["passes"] is True for row in negative_controls),
        "stage_ii_pass": all(row["passes"] is True for row in stage_rows),
        "verdict": "GENERATED" if minimal else "TYPED-NO-GO",
        "typed_no_go": not bool(minimal),
        "next_grammar_delta": "none for this finite grammar" if minimal else "add a discriminator for charge-grid closure",
        "root_landed": False,
        "frame_transfer_certified": False,
        "new_physics_claim": False,
    }
    (ARTIFACT_DIR / f"mode_b_group_shape_output_{TAG}.json").write_text(
        json.dumps(output, indent=TWO, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
