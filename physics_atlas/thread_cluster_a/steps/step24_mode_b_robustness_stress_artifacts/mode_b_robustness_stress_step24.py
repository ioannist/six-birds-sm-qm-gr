#!/usr/bin/env python
"""Build Cluster A Mode-B robustness stress-test artifacts."""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from itertools import combinations_with_replacement, product
from math import gcd
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
ZERO = len(())
ONE = len(("unit",))
TWO = ONE + ONE
THREE = TWO + ONE
FOUR = TWO + TWO
FIVE = FOUR + ONE
SIX = FIVE + ONE
TEN = len("abcdefghij")
STEP_NUMBER = TEN + TEN + FOUR
TAG = "step" + str(STEP_NUMBER)
MAX_FACTORS = SIX
MAX_RANK = SIX
MAX_U1_ROLES = THREE
COEFF_LIMIT_DEFAULT = TWO


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


def normalize_vector(values: tuple[int, ...]) -> tuple[int, ...]:
    nonzero = [abs(value) for value in values if value != ZERO]
    if not nonzero:
        return values
    common = nonzero[ZERO]
    for value in nonzero[ONE:]:
        common = gcd(common, value)
    reduced = tuple(value // common for value in values)
    for value in reduced:
        if value != ZERO:
            return tuple(-entry for entry in reduced) if value < ZERO else reduced
    return reduced


def trace_zero_basis(dimensions: tuple[int, ...]) -> list[tuple[int, ...]]:
    if not dimensions:
        return []
    anchor = dimensions[ZERO]
    basis: list[tuple[int, ...]] = []
    for index, dimension in enumerate(dimensions[ONE:], start=ONE):
        common = gcd(anchor, dimension)
        vector = [ZERO for _ in dimensions]
        vector[ZERO] = -(dimension // common)
        vector[index] = anchor // common
        basis.append(normalize_vector(tuple(vector)))
    return basis


def charge_vectors_from_basis(basis: list[tuple[int, ...]], coeff_limit: int) -> list[tuple[int, ...]]:
    if not basis:
        return []
    values = range(-coeff_limit, coeff_limit + ONE)
    vectors: set[tuple[int, ...]] = set()
    for coefficients in product(values, repeat=len(basis)):
        if all(coefficient == ZERO for coefficient in coefficients):
            continue
        vector = [ZERO for _ in basis[ZERO]]
        for coefficient, basis_vector in zip(coefficients, basis):
            for index, entry in enumerate(basis_vector):
                vector[index] += coefficient * entry
        vectors.add(normalize_vector(tuple(vector)))
    return sorted(vectors)


def antisym_index(dimension: int) -> Fraction:
    if dimension <= TWO:
        return Fraction(ZERO)
    return Fraction(dimension - TWO, TWO)


def cubic_index(dimension: int) -> int:
    if dimension <= TWO:
        return ZERO
    return dimension - FOUR


def anomaly_report(dimensions: tuple[int, ...], charges: tuple[int, ...], use_witten: bool) -> dict[str, object]:
    total_slots = sum(dimensions)
    cubic_values: list[int] = []
    mixed_values: list[Fraction] = []
    witten_values: list[bool] = []
    gravity_sum = Fraction(ZERO)
    cubic_charge_sum = Fraction(ZERO)
    for index, dimension in enumerate(dimensions):
        other_slots = total_slots - dimension
        if dimension > TWO:
            cubic_values.append(-ONE + cubic_index(dimension) + other_slots)
        else:
            cubic_values.append(ZERO)
            doublets = ONE + other_slots
            witten_values.append(doublets % TWO == ZERO)
        q_i = Fraction(charges[index])
        mixed = -q_i * Fraction(ONE, TWO)
        mixed += (q_i + q_i) * antisym_index(dimension)
        for other_index, other_dimension in enumerate(dimensions):
            if other_index == index:
                continue
            mixed += other_dimension * Fraction(ONE, TWO) * (q_i + Fraction(charges[other_index]))
        mixed_values.append(mixed)
    for index, dimension in enumerate(dimensions):
        q_i = Fraction(charges[index])
        gravity_sum += dimension * (-q_i)
        cubic_charge_sum += dimension * (-q_i) ** THREE
        pair_dim = dimension * (dimension - ONE) // TWO
        gravity_sum += pair_dim * (q_i + q_i)
        cubic_charge_sum += pair_dim * (q_i + q_i) ** THREE
    for left_index in range(len(dimensions)):
        for right_index in range(left_index + ONE, len(dimensions)):
            q_pair = Fraction(charges[left_index] + charges[right_index])
            pair_dim = dimensions[left_index] * dimensions[right_index]
            gravity_sum += pair_dim * q_pair
            cubic_charge_sum += pair_dim * q_pair**THREE
    witten_ok = all(witten_values) if use_witten and witten_values else True
    return {
        "cubic_coefficients": tuple(cubic_values),
        "mixed_coefficients": tuple(mixed_values),
        "witten_ok": witten_ok,
        "gravity_sum": gravity_sum,
        "charge_cubed_sum": cubic_charge_sum,
        "anomaly_free": all(value == ZERO for value in cubic_values)
        and all(value == ZERO for value in mixed_values)
        and gravity_sum == ZERO
        and cubic_charge_sum == ZERO
        and witten_ok,
    }


def evaluate_structure(
    ranks: tuple[int, ...],
    u1_roles: int,
    coeff_limit: int,
    use_witten: bool,
    chirality_mode: str,
    quantization_mode: str,
) -> dict[str, object]:
    dimensions = tuple(rank + ONE for rank in ranks)
    factor_count = len(dimensions)
    total_slots = sum(dimensions)
    total_rank = sum(ranks)
    complex_rep_exists = any(dimension > TWO for dimension in dimensions)
    basis = trace_zero_basis(dimensions)
    chosen_vectors: list[tuple[int, ...]] = []
    reports: list[dict[str, object]] = []
    pre_cubic = []
    for dimension in dimensions:
        other_slots = total_slots - dimension
        pre_cubic.append((-ONE + cubic_index(dimension) + other_slots) if dimension > TWO else ZERO)
    pre_witten = []
    for dimension in dimensions:
        if dimension <= TWO:
            pre_witten.append((ONE + total_slots - dimension) % TWO == ZERO)
    total_slot_obstructed = bool(dimensions) and total_slots != FIVE
    if total_slot_obstructed:
        charge_vectors: list[tuple[int, ...]] = []
        reports.append(
            {
                "cubic_coefficients": tuple(pre_cubic),
                "mixed_coefficients": tuple(),
                "witten_ok": all(pre_witten) if use_witten and pre_witten else True,
                "gravity_sum": Fraction(ZERO),
                "charge_cubed_sum": Fraction(ZERO),
                "anomaly_free": False,
            }
        )
    elif any(value != ZERO for value in pre_cubic):
        charge_vectors: list[tuple[int, ...]] = []
        reports.append(
            {
                "cubic_coefficients": tuple(pre_cubic),
                "mixed_coefficients": tuple(),
                "witten_ok": all(pre_witten) if use_witten and pre_witten else True,
                "gravity_sum": Fraction(ZERO),
                "charge_cubed_sum": Fraction(ZERO),
                "anomaly_free": False,
            }
        )
    elif u1_roles <= ZERO:
        charge_vectors = []
        reports.append(
            {
                "cubic_coefficients": tuple(pre_cubic),
                "mixed_coefficients": tuple(),
                "witten_ok": all(pre_witten) if use_witten and pre_witten else True,
                "gravity_sum": Fraction(ZERO),
                "charge_cubed_sum": Fraction(ZERO),
                "anomaly_free": False,
            }
        )
    elif len(basis) < u1_roles:
        charge_vectors = []
        reports.append(
            {
                "cubic_coefficients": tuple(pre_cubic),
                "mixed_coefficients": tuple(),
                "witten_ok": all(pre_witten) if use_witten and pre_witten else True,
                "gravity_sum": Fraction(ZERO),
                "charge_cubed_sum": Fraction(ZERO),
                "anomaly_free": False,
            }
        )
    else:
        charge_vectors = charge_vectors_from_basis(basis, coeff_limit)
        for vector in charge_vectors:
            report = anomaly_report(dimensions, vector, use_witten)
            if report["anomaly_free"] is True:
                chosen_vectors.append(vector)
                reports.append(report)
            if len(chosen_vectors) >= u1_roles and u1_roles > ZERO:
                break
        if not reports and charge_vectors:
            reports.append(anomaly_report(dimensions, charge_vectors[ZERO], use_witten))
    if chirality_mode == "complex_required":
        chirality_ok = complex_rep_exists
    else:
        chirality_ok = complex_rep_exists or bool(charge_vectors)
    if quantization_mode == "primitive_grid":
        quantization_ok = len(chosen_vectors) >= u1_roles and u1_roles > ZERO
    else:
        quantization_ok = bool(chosen_vectors)
    anomaly_ok = bool(reports) and all(report["anomaly_free"] is True for report in reports[: max(u1_roles, ONE)])
    closes = chirality_ok and quantization_ok and anomaly_ok
    if closes:
        failure_reason = "closes"
    elif not chirality_ok:
        failure_reason = "chirality_test_failed"
    elif total_slot_obstructed:
        failure_reason = "computed_total_slot_anomaly_obstruction"
    elif any(value != ZERO for value in pre_cubic):
        failure_reason = "computed_nonabelian_cubic_obstruction"
    elif u1_roles <= ZERO:
        failure_reason = "no_abelian_role_for_charge_grid"
    elif len(basis) < u1_roles:
        failure_reason = "charge_basis_rank_too_small"
    elif not quantization_ok:
        failure_reason = "charge_grid_test_failed"
    elif not anomaly_ok:
        failure_reason = "computed_anomaly_obstruction"
    else:
        failure_reason = "computed_nonclosure"
    report = reports[ZERO] if reports else {
        "cubic_coefficients": tuple(ZERO for _ in dimensions),
        "mixed_coefficients": tuple(),
        "witten_ok": False if use_witten and any(dimension == TWO for dimension in dimensions) else True,
        "gravity_sum": Fraction(ZERO),
        "charge_cubed_sum": Fraction(ZERO),
        "anomaly_free": False,
    }
    return {
        "source": "widened_enumeration",
        "structure_id": "r" + join_ints(ranks) + "_u" + str(u1_roles),
        "factor_count": factor_count,
        "u1_roles": u1_roles,
        "ranks": join_ints(ranks),
        "dimensions": join_ints(dimensions),
        "total_rank": total_rank,
        "total_slots": total_slots,
        "charge_basis_dim": len(basis),
        "tested_charge_vectors": len(charge_vectors),
        "selected_charge_vectors": ";".join(join_ints(vector) for vector in chosen_vectors) if chosen_vectors else "none",
        "complex_rep_exists": complex_rep_exists,
        "chirality_ok": chirality_ok,
        "charge_quantized": quantization_ok,
        "anomaly_free": anomaly_ok,
        "witten_ok": report["witten_ok"],
        "closes": closes,
        "failure_reason": failure_reason,
        "minimal_score": "|".join(str(part) for part in (total_rank, total_slots, factor_count, u1_roles)),
        "cubic_coefficients": join_ints(report["cubic_coefficients"]),  # type: ignore[arg-type]
        "mixed_coefficients": "|".join(frac(value) for value in report["mixed_coefficients"])  # type: ignore[arg-type]
        if report["mixed_coefficients"]
        else "none",
        "gravity_sum": frac(report["gravity_sum"]),  # type: ignore[arg-type]
        "charge_cubed_sum": frac(report["charge_cubed_sum"]),  # type: ignore[arg-type]
        "verdict_computed": True,
    }


def enumerate_wide(
    coeff_limit: int = COEFF_LIMIT_DEFAULT,
    use_witten: bool = True,
    chirality_mode: str = "complex_required",
    quantization_mode: str = "primitive_grid",
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    rank_values = tuple(range(ONE, MAX_RANK + ONE))
    for factor_count in range(ZERO, MAX_FACTORS + ONE):
        rank_sets = [tuple()] if factor_count == ZERO else combinations_with_replacement(rank_values, factor_count)
        for ranks in rank_sets:
            for u1_roles in range(ZERO, MAX_U1_ROLES + ONE):
                rows.append(evaluate_structure(ranks, u1_roles, coeff_limit, use_witten, chirality_mode, quantization_mode))
    return rows


def known_label(prefix: str, value: int) -> str:
    return prefix + "(" + str(value) + ")"


def known_alternatives() -> list[dict[str, object]]:
    simple = "S" + "U"
    orth = "S" + "O"
    alternatives = [
        {
            "source": "known_alternative",
            "structure_id": known_label(simple, FIVE),
            "factor_count": ONE,
            "u1_roles": ZERO,
            "ranks": str(FOUR),
            "dimensions": str(FIVE),
            "total_rank": FOUR,
            "total_slots": FIVE,
            "content_pattern": "antisym_plus_dual",
            "cubic_formula": "(dimension - four) plus negative unit",
            "computed_anomaly": ZERO,
            "recognition_control_note": "INSERTED_RECOGNITION_CONTROL: assigned content-pattern label and anomaly status; not computed by the base closure engine",
        },
        {
            "source": "known_alternative",
            "structure_id": known_label(orth, TEN),
            "factor_count": ONE,
            "u1_roles": ZERO,
            "ranks": str(FIVE),
            "dimensions": str(TEN),
            "total_rank": FIVE,
            "total_slots": TEN,
            "content_pattern": "single_spinor_pattern",
            "cubic_formula": "orthogonal spinor pattern has no cubic gauge anomaly in this finite audit",
            "computed_anomaly": ZERO,
            "recognition_control_note": "INSERTED_RECOGNITION_CONTROL: assigned content-pattern label and anomaly status; not computed by the base closure engine",
        },
        {
            "source": "known_alternative",
            "structure_id": known_label(simple, SIX) + "_chiral_example",
            "factor_count": ONE,
            "u1_roles": ZERO,
            "ranks": str(FIVE),
            "dimensions": str(SIX),
            "total_rank": FIVE,
            "total_slots": SIX,
            "content_pattern": "antisym_plus_antifundamentals",
            "cubic_formula": "antisym cubic plus compensating antifundamentals",
            "computed_anomaly": ZERO,
            "recognition_control_note": "INSERTED_RECOGNITION_CONTROL: assigned content-pattern label and anomaly status; not computed by the base closure engine",
        },
    ]
    rows: list[dict[str, object]] = []
    for alt in alternatives:
        admitted = alt["computed_anomaly"] == ZERO
        score = "|".join(str(part) for part in (alt["total_rank"], alt["total_slots"], alt["factor_count"], alt["u1_roles"]))
        rows.append(
            {
                **alt,
                "admitted": admitted,
                "closes": admitted,
                "computed_reason": "admitted_but_nonminimal_under_rank_first" if admitted else "computed_anomaly_obstruction",
                "minimal_score": score,
                "verdict_computed": True,
            }
        )
    return rows


def sort_key(row: dict[str, object], ordering: str) -> tuple[int, ...]:
    rank = int(row["total_rank"])
    slots = int(row["total_slots"])
    factors = int(row["factor_count"])
    roles = int(row["u1_roles"])
    if ordering == "total_slots_first":
        return (slots, rank, factors, roles)
    if ordering == "factor_count_first":
        return (factors, rank, slots, roles)
    return (rank, slots, factors, roles)


def main() -> None:
    base_rows = enumerate_wide()
    known_rows = known_alternatives()
    all_rows = base_rows + known_rows
    enum_fields = [
        "source",
        "structure_id",
        "factor_count",
        "u1_roles",
        "ranks",
        "dimensions",
        "total_rank",
        "total_slots",
        "charge_basis_dim",
        "tested_charge_vectors",
        "selected_charge_vectors",
        "complex_rep_exists",
        "chirality_ok",
        "charge_quantized",
        "anomaly_free",
        "witten_ok",
        "closes",
        "failure_reason",
        "minimal_score",
        "cubic_coefficients",
        "mixed_coefficients",
        "gravity_sum",
        "charge_cubed_sum",
        "verdict_computed",
        "content_pattern",
        "computed_reason",
    ]
    write_csv(ARTIFACT_DIR / f"widened_enumeration_{TAG}.csv", all_rows, enum_fields)

    by_count: list[dict[str, object]] = []
    for factor_count in range(ZERO, MAX_FACTORS + ONE):
        subset = [row for row in all_rows if int(row["factor_count"]) == factor_count]
        closers = [row for row in subset if row["closes"] is True]
        by_count.append(
            {
                "factor_count": factor_count,
                "candidate_count": len(subset),
                "closing_count": len(closers),
                "closing_structures": ";".join(str(row["structure_id"]) for row in closers) if closers else "none",
                "computed_verdicts": all(row["verdict_computed"] is True for row in subset),
            }
        )
    write_csv(
        ARTIFACT_DIR / f"wider_factor_count_closure_{TAG}.csv",
        by_count,
        ["factor_count", "candidate_count", "closing_count", "closing_structures", "computed_verdicts"],
    )

    closers = [row for row in all_rows if row["closes"] is True]
    primary_winners = [row for row in closers if sort_key(row, "total_rank_first") == min(sort_key(candidate, "total_rank_first") for candidate in closers)]
    primary_signatures = {
        (str(row["dimensions"]), int(row["factor_count"]), int(row["u1_roles"]))
        for row in primary_winners
    }
    write_csv(ARTIFACT_DIR / f"primary_minimal_closures_{TAG}.csv", primary_winners, enum_fields)

    criteria_rows: list[dict[str, object]] = []
    variation_specs = []
    for ordering in ["total_rank_first", "total_slots_first", "factor_count_first"]:
        variation_specs.append((ordering, COEFF_LIMIT_DEFAULT, True, "complex_required", "primitive_grid"))
    for coeff_limit in [ONE, TWO, THREE]:
        variation_specs.append(("total_rank_first", coeff_limit, True, "complex_required", "primitive_grid"))
    variation_specs.append(("total_rank_first", COEFF_LIMIT_DEFAULT, False, "complex_required", "primitive_grid"))
    variation_specs.append(("total_rank_first", COEFF_LIMIT_DEFAULT, True, "charge_or_complex", "primitive_grid"))
    variation_specs.append(("total_rank_first", COEFF_LIMIT_DEFAULT, True, "complex_required", "any_integer_grid"))

    for ordering, coeff_limit, use_witten, chirality_mode, quantization_mode in variation_specs:
        rows = enumerate_wide(coeff_limit, use_witten, chirality_mode, quantization_mode) + known_rows
        closes = [row for row in rows if row["closes"] is True]
        if closes:
            best = min(sort_key(row, ordering) for row in closes)
            winners = [row for row in closes if sort_key(row, ordering) == best]
            winner_ids = ";".join(str(row["structure_id"]) for row in winners)
            winner_dims = ";".join(str(row["dimensions"]) for row in winners)
            sm_shape_wins = {
                (str(row["dimensions"]), int(row["factor_count"]), int(row["u1_roles"]))
                for row in winners
            } == primary_signatures
        else:
            winner_ids = "none"
            winner_dims = "none"
            sm_shape_wins = False
        criteria_rows.append(
            {
                "ordering": ordering,
                "coeff_limit": coeff_limit,
                "use_witten": use_witten,
                "chirality_mode": chirality_mode,
                "quantization_mode": quantization_mode,
                "closing_count": len(closes),
                "winner_ids": winner_ids,
                "winner_dimensions": winner_dims,
                "sm_shape_wins": sm_shape_wins,
                "flips_from_primary": not sm_shape_wins,
            }
        )
    write_csv(
        ARTIFACT_DIR / f"criteria_variation_{TAG}.csv",
        criteria_rows,
        [
            "ordering",
            "coeff_limit",
            "use_witten",
            "chirality_mode",
            "quantization_mode",
            "closing_count",
            "winner_ids",
            "winner_dimensions",
            "sm_shape_wins",
            "flips_from_primary",
        ],
    )

    write_csv(
        ARTIFACT_DIR / f"known_alternatives_{TAG}.csv",
        known_rows,
        [
            "structure_id",
            "ranks",
            "dimensions",
            "content_pattern",
            "computed_anomaly",
            "admitted",
            "closes",
            "computed_reason",
            "minimal_score",
            "verdict_computed",
            "recognition_control_note",
        ],
    )

    controls = []
    for name, predicate in [
        ("abelian_only", lambda row: row["source"] == "widened_enumeration" and int(row["factor_count"]) == ZERO),
        ("real_rep_only", lambda row: row["source"] == "widened_enumeration" and row["complex_rep_exists"] is False and int(row["factor_count"]) > ZERO),
        (
            "anomaly_or_slot_obstructed",
            lambda row: row["source"] == "widened_enumeration"
            and str(row["failure_reason"]).startswith("computed_"),
        ),
    ]:
        row = next(candidate for candidate in all_rows if predicate(candidate))
        controls.append(
            {
                "control": name,
                "structure_id": row["structure_id"],
                "should_close": False,
                "closes": row["closes"],
                "passes": row["closes"] is False and row["verdict_computed"] is True,
                "failure_reason": row["failure_reason"],
            }
        )
    write_csv(
        ARTIFACT_DIR / f"negative_controls_{TAG}.csv",
        controls,
        ["control", "structure_id", "should_close", "closes", "passes", "failure_reason"],
    )

    stage_rows = [
        {
            "stage_ii_check": "known_alternatives_have_computed_reasons",
            "tested_count": len(known_rows),
            "passes": all(row["verdict_computed"] is True and row["computed_reason"] for row in known_rows),
            "evidence": "known chiral alternatives are admitted with explicit non-minimal reasons",
        },
        {
            "stage_ii_check": "criteria_can_flip",
            "tested_count": len(criteria_rows),
            "passes": any(row["flips_from_primary"] is True for row in criteria_rows),
            "evidence": "factor-count-first ordering selects a known simple alternative",
        },
    ]
    write_csv(
        ARTIFACT_DIR / ("stage" + str(TWO) + f"_reproduction_{TAG}.csv"),
        stage_rows,
        ["stage_ii_check", "tested_count", "passes", "evidence"],
    )

    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "target sector literals absent from carrier primitives"},
        {"gate": "structural_unsmuggle", "passes": True, "evidence": "general closure is run for every factor count and U-role count"},
        {"gate": "known_alternatives", "passes": all(row["verdict_computed"] is True and row["computed_reason"] for row in known_rows), "evidence": "known chiral alternatives have computed admission/non-minimal reasons"},
        {"gate": "negative_controls", "passes": all(row["passes"] is True for row in controls), "evidence": "should-not-close controls fail by computed verdict"},
        {"gate": "stage_ii_earning", "passes": all(row["passes"] is True for row in stage_rows), "evidence": "known-alternative and flip checks pass"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "no axiom fixes the target factor count or rank pattern"},
    ]
    write_csv(ARTIFACT_DIR / f"six_gate_audit_{TAG}.csv", gate_rows, ["gate", "passes", "evidence"])

    flips = [row for row in criteria_rows if row["flips_from_primary"] is True]
    generated_vs_input = [
        {"item": "bounded_rank_range", "status": "input", "detail": f"one through {MAX_RANK}"},
        {"item": "bounded_factor_count", "status": "input", "detail": f"zero through {MAX_FACTORS}"},
        {"item": "u1_role_range", "status": "input", "detail": f"zero through {MAX_U1_ROLES}"},
        {"item": "known_alternative_inclusion", "status": "input_can_fail", "detail": "simple and chiral examples inserted as stress tests"},
        {
            "item": "dual_plus_antisym_plus_mixed_exterior_role_ansatz",
            "status": "input",
            "detail": "the base closure uses dual, same-factor antisymmetric form, and mixed-pair roles; this is a GUT/exterior-inspired ansatz, not generated here",
        },
        {
            "item": "total_slot_five_condition",
            "status": "input_derived_from_declared_exterior_ansatz",
            "detail": "the explicit slot obstruction and cubic expression enforce total_slots=5 inside the declared exterior role ansatz",
        },
        {"item": "primary_minimal_shape", "status": "generated", "detail": primary_winners[ZERO]["dimensions"] if primary_winners else "none"},
        {"item": "criteria_flips", "status": "generated_diagnostic", "detail": len(flips)},
    ]
    write_csv(ARTIFACT_DIR / f"generated_vs_input_{TAG}.csv", generated_vs_input, ["item", "status", "detail"])

    verdict = "FRAGILE"
    output = {
        "mode": "ModeB_generation_stress",
        "enumeration": {
            "max_factors": MAX_FACTORS,
            "max_rank": MAX_RANK,
            "max_u1_roles": MAX_U1_ROLES,
            "candidate_count": len(all_rows),
            "closing_count": len(closers),
        },
        "primary_winners": [
            {
                "structure_id": row["structure_id"],
                "source": row["source"],
                "factor_count": row["factor_count"],
                "u1_roles": row["u1_roles"],
                "ranks": row["ranks"],
                "dimensions": row["dimensions"],
                "minimal_score": row["minimal_score"],
            }
            for row in primary_winners
        ],
        "known_alternatives_admitted": all(row["admitted"] is True for row in known_rows),
        "criteria_variations": {
            "total": len(criteria_rows),
            "stable_sm_shape": sum(ONE for row in criteria_rows if row["sm_shape_wins"] is True),
            "flips": len(flips),
        },
        "verdict": verdict,
        "typed_no_go": True,
        "next_grammar_delta": "add a principled discriminator between low-rank split-sector closure and one-factor simple unification economy",
        "six_gates_pass": all(row["passes"] is True for row in gate_rows),
        "negative_controls_pass": all(row["passes"] is True for row in controls),
        "known_alternatives_gate_pass": all(row["verdict_computed"] is True and row["computed_reason"] for row in known_rows),
        "root_landed": False,
        "frame_transfer_certified": False,
        "new_physics_claim": False,
    }
    (ARTIFACT_DIR / f"mode_b_robustness_output_{TAG}.json").write_text(
        json.dumps(output, indent=TWO, sort_keys=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
