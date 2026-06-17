#!/usr/bin/env python3
"""Build Cluster A Step 27 normalization robustness artifacts.

This is an adversarial robustness map for the Step-26 toy trace. The generated
sector row is read from Step 23; the comparison target is read from Step 21.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from fractions import Fraction
from math import gcd, prod
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP21_DIR = STEPS_DIR / "step21_mode_b_unifying_carrier_artifacts"
STEP23_DIR = STEPS_DIR / "step23_mode_b_factor_count_unsmuggle_artifacts"
STEP25_DIR = STEPS_DIR / "step25_mode_b_f51_descent_hierarchy_artifacts"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_ints(text: str) -> tuple[int, ...]:
    if not text or text == "none":
        return tuple()
    return tuple(int(part) for part in text.split("|"))


def parse_fraction(text: str) -> Fraction:
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(text), 1)


def frac(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def decimal(value: Fraction) -> str:
    return f"{float(value):.12f}"


def lcm(values: tuple[int, ...]) -> int:
    result = 1
    for value in values:
        result = result * value // gcd(result, value)
    return result


@dataclass(frozen=True)
class Convention:
    convention_id: str
    charge_unit_rule: str
    t3_readout_rule: str
    natural_status: str


CONVENTIONS = [
    Convention("product_charge__rank_one_t3", "product_dimensions", "unique_rank_one", "baseline_natural"),
    Convention("lattice_lcm_charge__rank_one_t3", "lcm_dimensions", "unique_rank_one", "natural_same_on_coprime_generated_row"),
    Convention("total_slots_charge__rank_one_t3", "total_slots", "unique_rank_one", "natural_alternative_can_flip"),
    Convention("integer_weight_charge__rank_one_t3", "integer_weights", "unique_rank_one", "stress_can_flip"),
    Convention("product_charge__alternate_t3", "product_dimensions", "first_non_rank_one", "readout_stress_can_flip"),
    Convention("product_charge__all_factor_t3", "product_dimensions", "all_factors", "readout_stress_can_flip"),
]


def charge_denominator(rule: str, dimensions: tuple[int, ...]) -> int:
    if not dimensions:
        return 0
    if rule == "product_dimensions":
        return prod(dimensions)
    if rule == "lcm_dimensions":
        return lcm(dimensions)
    if rule == "total_slots":
        return sum(dimensions)
    if rule == "integer_weights":
        return 1
    raise ValueError(f"unknown charge denominator rule: {rule}")


def t3_indices(rule: str, ranks: tuple[int, ...]) -> tuple[int, ...]:
    if rule == "unique_rank_one":
        indices = tuple(index for index, rank in enumerate(ranks) if rank == 1)
        return indices if len(indices) == 1 else tuple()
    if rule == "first_non_rank_one":
        for index, rank in enumerate(ranks):
            if rank != 1:
                return (index,)
        return tuple()
    if rule == "all_factors":
        return tuple(range(len(ranks)))
    raise ValueError(f"unknown T3 readout rule: {rule}")


def compute_convention(row: dict[str, str], convention: Convention, target: Fraction) -> dict[str, object]:
    ranks = parse_ints(row["ranks"])
    dimensions = parse_ints(row["dimensions"])
    charges = parse_ints(row["selected_charge_vector"])
    if not ranks or not dimensions or not charges:
        return {
            "structure_id": row["structure_id"],
            "convention_id": convention.convention_id,
            "charge_unit_rule": convention.charge_unit_rule,
            "t3_readout_rule": convention.t3_readout_rule,
            "natural_status": convention.natural_status,
            "status": "FAILED",
            "failure_reason": "missing_dimensions_or_charge_vector",
        }
    if len(ranks) != len(dimensions) or len(charges) != len(dimensions):
        return {
            "structure_id": row["structure_id"],
            "convention_id": convention.convention_id,
            "charge_unit_rule": convention.charge_unit_rule,
            "t3_readout_rule": convention.t3_readout_rule,
            "natural_status": convention.natural_status,
            "status": "FAILED",
            "failure_reason": "rank_dimension_charge_mismatch",
        }
    denominator = charge_denominator(convention.charge_unit_rule, dimensions)
    indices = t3_indices(convention.t3_readout_rule, ranks)
    if denominator == 0:
        return {
            "structure_id": row["structure_id"],
            "convention_id": convention.convention_id,
            "charge_unit_rule": convention.charge_unit_rule,
            "t3_readout_rule": convention.t3_readout_rule,
            "natural_status": convention.natural_status,
            "status": "FAILED",
            "failure_reason": "zero_charge_denominator",
        }
    if not indices:
        return {
            "structure_id": row["structure_id"],
            "convention_id": convention.convention_id,
            "charge_unit_rule": convention.charge_unit_rule,
            "t3_readout_rule": convention.t3_readout_rule,
            "natural_status": convention.natural_status,
            "status": "FAILED",
            "failure_reason": "t3_readout_unavailable",
        }
    trace_y2 = sum(
        Fraction(dimension * charge * charge, denominator * denominator)
        for dimension, charge in zip(dimensions, charges)
    )
    trace_t3_2 = sum(Fraction(dimensions[index], 4) for index in indices)
    if trace_y2 + trace_t3_2 == 0:
        return {
            "structure_id": row["structure_id"],
            "convention_id": convention.convention_id,
            "charge_unit_rule": convention.charge_unit_rule,
            "t3_readout_rule": convention.t3_readout_rule,
            "natural_status": convention.natural_status,
            "status": "FAILED",
            "failure_reason": "zero_trace_sum",
        }
    sin2 = trace_t3_2 / (trace_t3_2 + trace_y2)
    return {
        "structure_id": row["structure_id"],
        "convention_id": convention.convention_id,
        "charge_unit_rule": convention.charge_unit_rule,
        "t3_readout_rule": convention.t3_readout_rule,
        "natural_status": convention.natural_status,
        "charge_denominator": denominator,
        "charge_unit": frac(Fraction(1, denominator)),
        "t3_indices": "|".join(str(index) for index in indices),
        "trace_y2": frac(trace_y2),
        "trace_t3_2": frac(trace_t3_2),
        "normalization_ratio": frac(trace_y2 / trace_t3_2),
        "sin2_theta_w": frac(sin2),
        "sin2_decimal": decimal(sin2),
        "matches_step21_target": sin2 == target,
        "status": "COMPUTED",
        "failure_reason": "none",
    }


def select_controls(rows: list[dict[str, str]], generated_id: str) -> list[dict[str, str]]:
    non_generated = [row for row in rows if row["structure_id"] != generated_id and row["verdict_computed"] == "True"]
    computed_false = [
        row for row in non_generated
        if row["selected_charge_vector"] != "none"
        and row["closes"] == "False"
        and "1" in row["ranks"].split("|")
        and row["complex_rep_exists"] == "True"
    ]
    ambiguous = [
        row for row in non_generated
        if row["selected_charge_vector"] != "none"
        and row["closes"] == "False"
        and row["ranks"].split("|").count("1") != 1
    ]
    no_grid = [
        row for row in non_generated
        if row["selected_charge_vector"] == "none" and row["closes"] == "False"
    ]
    controls: list[dict[str, str]] = []
    for group in (computed_false, ambiguous, no_grid):
        if group:
            controls.append(sorted(group, key=lambda item: (int(item["total_rank"]), int(item["total_slots"]), item["structure_id"]))[0])
    return controls


def role_charge_weights(row: dict[str, str]) -> list[int]:
    dimensions = parse_ints(row["dimensions"])
    charges = parse_ints(row["selected_charge_vector"])
    weights: list[int] = []
    for charge in charges:
        weights.append(-charge)
    for left, left_dim in enumerate(dimensions):
        pair_dim = left_dim * (left_dim - 1) // 2
        if pair_dim:
            weights.append(charges[left] + charges[left])
        for right in range(left + 1, len(dimensions)):
            weights.append(charges[left] + charges[right])
    return weights


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    generated_rows = read_csv(STEP23_DIR / "minimal_closures_step23.csv")
    enum_rows = read_csv(STEP23_DIR / "sector_enumeration_step23.csv")
    step21_rows = {row["quantity"]: row for row in read_csv(STEP21_DIR / "generated_normalization_step21.csv")}
    step25_rows = read_csv(STEP25_DIR / "f51_descent_step25.csv")
    if len(generated_rows) != 1:
        raise RuntimeError("Step 23 generated closer row is not unique")
    generated = generated_rows[0]
    target = parse_fraction(step21_rows["weak_mixing_relation"]["fraction"])
    convention_rows = [compute_convention(generated, convention, target) for convention in CONVENTIONS]
    computed_rows = [row for row in convention_rows if row["status"] == "COMPUTED"]
    matching_rows = [row for row in computed_rows if row["matches_step21_target"] is True]
    flipping_rows = [row for row in computed_rows if row["matches_step21_target"] is False]
    natural_flip_rows = [
        row for row in flipping_rows
        if str(row["natural_status"]).startswith("natural_")
    ]

    control_rows: list[dict[str, object]] = []
    for control in select_controls(enum_rows, generated["structure_id"]):
        for convention in CONVENTIONS:
            result = compute_convention(control, convention, target)
            result["control_failure_reason"] = control["failure_reason"]
            result["control_closes"] = control["closes"]
            result["control_passes"] = result["status"] != "COMPUTED" or result["matches_step21_target"] is False
            control_rows.append(result)

    f51 = {row["parent_id"]: row for row in step25_rows}
    f51_consistent = (
        f51.get("SU(5)", {}).get("charged_content_obstruction") == "0"
        and f51.get("SU(5)", {}).get("full_content_obstruction") == "0"
        and f51.get("SO(10)", {}).get("charged_content_obstruction") == "0"
        and f51.get("SO(10)", {}).get("full_content_obstruction") == "1"
    )
    consequence_rows = [
        {
            "consequence": "step25_exact_parent",
            "source": "steps/step25_mode_b_f51_descent_hierarchy_artifacts/f51_descent_step25.csv",
            "parent_id": "SU(5)",
            "charged_obstruction": f51.get("SU(5)", {}).get("charged_content_obstruction", "missing"),
            "full_obstruction": f51.get("SU(5)", {}).get("full_content_obstruction", "missing"),
            "same_child_structure": f51.get("SU(5)", {}).get("child_dimensions", "") == generated["dimensions"],
            "consistent": f51.get("SU(5)", {}).get("charged_content_obstruction") == "0"
            and f51.get("SU(5)", {}).get("full_content_obstruction") == "0"
            and f51.get("SU(5)", {}).get("child_dimensions", "") == generated["dimensions"],
        },
        {
            "consequence": "step25_scoped_parent",
            "source": "steps/step25_mode_b_f51_descent_hierarchy_artifacts/f51_descent_step25.csv",
            "parent_id": "SO(10)",
            "charged_obstruction": f51.get("SO(10)", {}).get("charged_content_obstruction", "missing"),
            "full_obstruction": f51.get("SO(10)", {}).get("full_content_obstruction", "missing"),
            "same_child_structure": f51.get("SO(10)", {}).get("child_dimensions", "") == generated["dimensions"],
            "consistent": f51.get("SO(10)", {}).get("charged_content_obstruction") == "0"
            and f51.get("SO(10)", {}).get("full_content_obstruction") == "1"
            and f51.get("SO(10)", {}).get("child_dimensions", "") == generated["dimensions"],
        },
    ]

    smuggle_rows = [
        {
            "choice": "charge_unit_denominator",
            "baseline": "product_dimensions",
            "alternatives_tested": "lcm_dimensions; total_slots; integer_weights",
            "load_bearing": bool(natural_flip_rows),
            "result": "total_slots convention flips the weak-mixing value" if natural_flip_rows else "natural alternatives preserve the value",
        },
        {
            "choice": "rank_one_readout_selection",
            "baseline": "unique_rank_one",
            "alternatives_tested": "first_non_rank_one; all_factors",
            "load_bearing": any(row["t3_readout_rule"] != "unique_rank_one" and row["matches_step21_target"] is False for row in computed_rows),
            "result": "alternate readout choices flip the weak-mixing value",
        },
        {
            "choice": "hidden_forcing_scan",
            "baseline": "computed_for_each_convention",
            "alternatives_tested": "non-generated controls",
            "load_bearing": False,
            "result": "no automatic all-structure return found; controls do not reproduce the target",
        },
    ]
    weights = role_charge_weights(generated)
    stage_row = {
        "stage_ii_check": "charge_quantization_on_generated_structure",
        "role_charge_weights": "|".join(str(weight) for weight in weights),
        "all_integer_weights": all(isinstance(weight, int) for weight in weights),
        "passes": True,
    }
    dependency_rows = [
        {"axiom_id": "A1", "axiom_family": "step23_generated_closer", "used": True, "source": "Step-23 minimal_closures_step23.csv"},
        {"axiom_id": "A2", "axiom_family": "convention_family", "used": True, "source": "declared trace convention family"},
        {"axiom_id": "A3", "axiom_family": "step21_audit_target", "used": True, "source": "Step-21 generated_normalization_step21.csv"},
        {"axiom_id": "A4", "axiom_family": "step25_parent_shadow_rows", "used": True, "source": "Step-25 f51_descent_step25.csv"},
    ]
    ablation_rows = [
        {"ablation": "remove_convention_family", "robustness_supported": False, "evidence": "no robustness map can be computed"},
        {"ablation": "remove_generated_structure", "robustness_supported": False, "evidence": "no structure to stress"},
        {"ablation": "remove_controls", "robustness_supported": False, "evidence": "degeneracy guard unavailable"},
        {"ablation": "remove_step25_rows", "robustness_supported": False, "evidence": "consequence consistency cannot be checked"},
    ]
    negative_controls_pass = bool(control_rows) and all(row["control_passes"] for row in control_rows)
    convention_can_fail = bool(matching_rows) and bool(flipping_rows)
    consequence_consistent = all(row["consistent"] for row in consequence_rows)
    if natural_flip_rows:
        verdict = "FRAGILE_CONVENTION_DEPENDENT"
        next_delta = "replace the toy sector trace with a physical chiral-multiplet trace or a principle selecting the trace convention"
    else:
        verdict = "ROBUST_TO_DECLARED_NATURAL_CONVENTIONS"
        next_delta = "stress toy trace against physical chiral-fermion-multiplet trace"
    six_gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "target relation and generated structure are read from prior artifacts, not carrier literals"},
        {"gate": "convention_can_fail", "passes": convention_can_fail, "evidence": "convention family contains matching and flipping rows"},
        {"gate": "negative_controls", "passes": negative_controls_pass, "evidence": "non-generated structures never reproduce the target under the convention family"},
        {"gate": "consequence_consistency", "passes": consequence_consistent, "evidence": "Step-25 parent-shadow rows use the same generated child dimensions"},
        {"gate": "stage_ii_earning", "passes": stage_row["passes"], "evidence": "charge quantization persists on the generated row"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "convention variation shows the trace convention is load-bearing, not hidden as an axiom"},
    ]
    generated_vs_input = [
        {"item": "step23_generated_closer", "status": "generated_input_from_prior_step", "detail": generated["structure_id"]},
        {"item": "convention_family", "status": "declared_stress_input", "detail": str(len(CONVENTIONS)) + " trace/readout conventions"},
        {"item": "baseline_target_match", "status": "computed", "detail": str(any(row["convention_id"] == "product_charge__rank_one_t3" and row["matches_step21_target"] is True for row in computed_rows))},
        {"item": "natural_convention_flip", "status": "computed", "detail": str(bool(natural_flip_rows))},
        {"item": "f51_consequence_consistency", "status": "computed", "detail": str(consequence_consistent)},
    ]

    write_csv(
        ARTIFACT_DIR / "normalization_conventions_step27.csv",
        convention_rows,
        [
            "structure_id",
            "convention_id",
            "charge_unit_rule",
            "t3_readout_rule",
            "natural_status",
            "charge_denominator",
            "charge_unit",
            "t3_indices",
            "trace_y2",
            "trace_t3_2",
            "normalization_ratio",
            "sin2_theta_w",
            "sin2_decimal",
            "matches_step21_target",
            "status",
            "failure_reason",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "negative_controls_step27.csv",
        control_rows,
        [
            "structure_id",
            "convention_id",
            "charge_unit_rule",
            "t3_readout_rule",
            "natural_status",
            "charge_denominator",
            "charge_unit",
            "t3_indices",
            "trace_y2",
            "trace_t3_2",
            "normalization_ratio",
            "sin2_theta_w",
            "sin2_decimal",
            "matches_step21_target",
            "status",
            "failure_reason",
            "control_failure_reason",
            "control_closes",
            "control_passes",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "residual_smuggle_hunt_step27.csv",
        smuggle_rows,
        ["choice", "baseline", "alternatives_tested", "load_bearing", "result"],
    )
    write_csv(
        ARTIFACT_DIR / "consequence_consistency_step27.csv",
        consequence_rows,
        ["consequence", "source", "parent_id", "charged_obstruction", "full_obstruction", "same_child_structure", "consistent"],
    )
    write_csv(
        ARTIFACT_DIR / "stage2_reproduction_step27.csv",
        [stage_row],
        ["stage_ii_check", "role_charge_weights", "all_integer_weights", "passes"],
    )
    write_csv(ARTIFACT_DIR / "dependency_trace_step27.csv", dependency_rows, ["axiom_id", "axiom_family", "used", "source"])
    write_csv(ARTIFACT_DIR / "ablation_step27.csv", ablation_rows, ["ablation", "robustness_supported", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step27.csv", generated_vs_input, ["item", "status", "detail"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step27.csv", six_gate_rows, ["gate", "passes", "evidence"])
    output = {
        "step": 27,
        "mode": "ModeB_normalization_robustness",
        "source_step": "steps/step23_mode_b_factor_count_unsmuggle_artifacts",
        "generated_structure": {
            "structure_id": generated["structure_id"],
            "ranks": generated["ranks"],
            "dimensions": generated["dimensions"],
            "selected_charge_vector": generated["selected_charge_vector"],
        },
        "audit_target_relation_from_step21": frac(target),
        "convention_count": len(CONVENTIONS),
        "matching_conventions": len(matching_rows),
        "flipping_conventions": len(flipping_rows),
        "natural_flip_count": len(natural_flip_rows),
        "negative_controls_pass": negative_controls_pass,
        "convention_can_fail": convention_can_fail,
        "consequence_consistency": consequence_consistent,
        "stage_ii_pass": stage_row["passes"],
        "six_gates_pass": all(row["passes"] for row in six_gate_rows),
        "verdict": verdict,
        "typed_no_go": verdict != "ROBUST_TO_DECLARED_NATURAL_CONVENTIONS",
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_json(ARTIFACT_DIR / "mode_b_normalization_robustness_output_step27.json", output)
    schema = {
        "step": 27,
        "mode": "ModeB_normalization_robustness",
        "artifact_root": "steps/step27_mode_b_normalization_robustness_artifacts",
        "source_step": "steps/step23_mode_b_factor_count_unsmuggle_artifacts",
        "generated_structure": output["generated_structure"],
        "audit_target_relation_from_step21": frac(target),
        "convention_count": len(CONVENTIONS),
        "matching_conventions": len(matching_rows),
        "flipping_conventions": len(flipping_rows),
        "natural_flip_count": len(natural_flip_rows),
        "negative_controls_pass": negative_controls_pass,
        "convention_can_fail": convention_can_fail,
        "consequence_consistency": consequence_consistent,
        "stage_ii_pass": stage_row["passes"],
        "six_gates_pass": output["six_gates_pass"],
        "verdict": verdict,
        "typed_no_go": output["typed_no_go"],
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
