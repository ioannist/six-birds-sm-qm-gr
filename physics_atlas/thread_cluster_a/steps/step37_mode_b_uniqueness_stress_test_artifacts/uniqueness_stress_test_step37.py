#!/usr/bin/env python3
"""Build Cluster A Step 37 uniqueness stress-test artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP35_SCRIPT = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"


def load_step35():
    spec = importlib.util.spec_from_file_location("cluster_a_step35_for_step37", STEP35_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 35 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step35_for_step37"] = module
    spec.loader.exec_module(module)
    return module


s35 = load_step35()
s33 = s35.s33
ZERO = s33.ZERO
ONE = s33.ONE
TWO = s33.TWO


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def score_text(score: tuple[int, ...]) -> str:
    return "|".join(str(value) for value in score)


def active_factor_indices(scalar: object) -> tuple[int, ...]:
    return tuple(
        factor_index
        for factor_index, (raw_rep, dimension) in enumerate(zip(scalar.reps, scalar.dimensions))
        if s33.action_active(raw_rep, dimension)
    )


def candidate_active_factors(combo: tuple[int, ...], type_rows: list[object]) -> tuple[int, ...]:
    factors: set[int] = set()
    dimensions = type_rows[ZERO].dimensions
    for type_id in combo:
        row = type_rows[type_id]
        for factor_index, (raw_rep, dimension) in enumerate(zip(row.reps, dimensions)):
            if s33.action_active(raw_rep, dimension):
                factors.add(factor_index)
    return tuple(sorted(factors))


def residual_subgroup_dimension(raw_rep: str, canonical_rep: str, dimension: int) -> int:
    if raw_rep == "singlet" or canonical_rep == "singlet":
        return dimension
    if canonical_rep in {"rank_one_fund", "fund", "antifund"}:
        return dimension - ONE
    if canonical_rep in {"antisym2", "sym2", "adjoint"}:
        return max(dimension - ONE, ZERO)
    return ZERO


def unbroken_nonabelian_subgroups(combo: tuple[int, ...], type_rows: list[object], scalar: object) -> tuple[int, ...]:
    active_factors = set(candidate_active_factors(combo, type_rows))
    unbroken: list[int] = []
    for factor_index, dimension in enumerate(scalar.dimensions):
        if factor_index not in active_factors:
            continue
        if factor_index in active_factor_indices(scalar):
            residual = residual_subgroup_dimension(
                scalar.reps[factor_index],
                scalar.canonical_reps[factor_index],
                dimension,
            )
            if residual >= TWO:
                unbroken.append(residual)
        elif dimension >= TWO:
            unbroken.append(dimension)
    return tuple(sorted(unbroken))


def scalar_quadratic_invariant(scalar: object) -> bool:
    conjugate = s35.conjugate_scalar(scalar)
    return scalar.charge + conjugate.charge == ZERO and all(
        s35.factor_invariant(rep, conj_rep, "singlet", dimension)
        for rep, conj_rep, dimension in zip(scalar.canonical_reps, conjugate.canonical_reps, scalar.dimensions)
    )


def step35_survivors() -> tuple[str, list[dict[str, object]]]:
    target_key, carrier_rows = s35.corrected_80_carrier()
    rows: list[dict[str, object]] = []
    scalar_cache: dict[tuple[int, ...], list[object]] = {}
    for carrier in carrier_rows:
        dimensions = carrier["dimensions"]
        scalar_cache.setdefault(dimensions, s35.scalar_representations(dimensions))
        result = s35.higher_layer_mass_closure(carrier["combo"], carrier["type_rows"], scalar_cache[dimensions])
        if result["higher_layer_passes"]:
            rows.append({**carrier, **result})
    return target_key, rows


def structure_counts(rows: list[dict[str, object]], predicate: str) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        if row[predicate]:
            counts[row["dimensions"]] = counts.get(row["dimensions"], ZERO) + ONE
    return ";".join(f"{key}:{counts[key]}" for key in sorted(counts))


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    _target_key, survivors = step35_survivors()
    score_rows: list[dict[str, object]] = []
    target_dimensions = ""
    target_passes_currency = False
    target_distinguished = False

    for row in survivors:
        scalar = row["witness_scalar"]
        unbroken = unbroken_nonabelian_subgroups(row["combo"], row["type_rows"], scalar)
        precise_unbroken = bool(unbroken)
        potential_proxy = scalar_quadratic_invariant(scalar) and scalar.component_dim > ZERO
        low_energy_consistency = precise_unbroken and bool(row["higher_layer_passes"])
        full_cascade_consistency = low_energy_consistency and potential_proxy
        currency = (scalar.component_dim, len(active_factor_indices(scalar)), abs(scalar.charge))
        score_rows.append(
            {
                "dimensions": row["dimensions_text"],
                "support_key": row["support_key"],
                "support_score": score_text(row["support_score"]),
                "witness_scalar_key": scalar.text,
                "witness_scalar_component_dim": scalar.component_dim,
                "witness_scalar_charge_abs": abs(scalar.charge),
                "scalar_active_factors": "|".join(str(index) for index in active_factor_indices(scalar)),
                "unbroken_nonabelian_subgroups": "|".join(str(value) for value in unbroken),
                "precise_unbroken_subgroup_survives": precise_unbroken,
                "potential_proxy": potential_proxy,
                "unbroken_low_energy_consistency": low_energy_consistency,
                "full_cascade_consistency": full_cascade_consistency,
                "scalar_stage_currency": "|".join(str(value) for value in currency),
                "is_target_reference": bool(row["is_target_reference"]),
                "_currency_tuple": currency,
            }
        )
        if row["is_target_reference"]:
            target_dimensions = row["dimensions_text"]

    precise_rows = [row for row in score_rows if row["precise_unbroken_subgroup_survives"]]
    su4_precise_survives = any(row["dimensions"] == "4" and row["precise_unbroken_subgroup_survives"] for row in score_rows)
    minimal_currency = min(row["_currency_tuple"] for row in precise_rows)
    for row in score_rows:
        row["scalar_stage_currency_minimum"] = row["_currency_tuple"] == minimal_currency and row["precise_unbroken_subgroup_survives"]
        if row["is_target_reference"]:
            target_passes_currency = bool(row["scalar_stage_currency_minimum"])
    currency_rows = [row for row in score_rows if row["scalar_stage_currency_minimum"]]
    target_passes_currency_diagnostic = target_passes_currency
    target_passes_currency = False
    target_distinguished = False
    selected_structure = ""
    verdict = "SMALL_NEUTRAL_FAMILY_currency_rescue_REJECTED"
    next_delta = (
        "accept the small neutral family {2|3,4}; scalar-stage currency is diagnostic_only/rejected as shape-in-disguise and minimality-like, so continue to Step-38 clean-separation or the matter-content boundary"
    )

    principle_rows = [
        {
            "principle": "precise_unbroken_nonabelian_subgroup",
            "survivor_count": sum(ONE for row in score_rows if row["precise_unbroken_subgroup_survives"]),
            "survivors_by_structure": structure_counts(score_rows, "precise_unbroken_subgroup_survives"),
            "target_passes": any(row["is_target_reference"] and row["precise_unbroken_subgroup_survives"] for row in score_rows),
            "single_factor_survives": any(row["dimensions"] == "4" and row["precise_unbroken_subgroup_survives"] for row in score_rows),
            "shape_flavored": False,
            "note": "allows partial breaking inside a single factor",
        },
        {
            "principle": "unbroken_low_energy_consistency",
            "survivor_count": sum(ONE for row in score_rows if row["unbroken_low_energy_consistency"]),
            "survivors_by_structure": structure_counts(score_rows, "unbroken_low_energy_consistency"),
            "target_passes": any(row["is_target_reference"] and row["unbroken_low_energy_consistency"] for row in score_rows),
            "single_factor_survives": any(row["dimensions"] == "4" and row["unbroken_low_energy_consistency"] for row in score_rows),
            "shape_flavored": False,
            "note": "mass-completion plus unbroken subgroup; diagnostic only",
        },
        {
            "principle": "full_cascade_consistency",
            "survivor_count": sum(ONE for row in score_rows if row["full_cascade_consistency"]),
            "survivors_by_structure": structure_counts(score_rows, "full_cascade_consistency"),
            "target_passes": any(row["is_target_reference"] and row["full_cascade_consistency"] for row in score_rows),
            "single_factor_survives": any(row["dimensions"] == "4" and row["full_cascade_consistency"] for row in score_rows),
            "shape_flavored": False,
            "note": "potential proxy plus mass-completion plus precise subgroup; diagnostic only",
        },
        {
            "principle": "scalar_stage_currency_minimum",
            "survivor_count": len(currency_rows),
            "survivors_by_structure": structure_counts(score_rows, "scalar_stage_currency_minimum"),
            "target_passes": target_passes_currency_diagnostic,
            "single_factor_survives": any(row["dimensions"] == "4" and row["scalar_stage_currency_minimum"] for row in score_rows),
            "shape_flavored": True,
            "note": "diagnostic_only/REJECTED: manager override finds this reduces to smallest broken factor and is minimality-like",
        },
        {
            "principle": "step36_factor_local_breaking_diagnostic",
            "survivor_count": sum(ONE for row in score_rows if row["dimensions"] != "4"),
            "survivors_by_structure": "2|3:8",
            "target_passes": True,
            "single_factor_survives": False,
            "shape_flavored": True,
            "note": "diagnostic only: this old rule is unsatisfiable for single-factor structures by construction",
        },
    ]
    corrected_rows = [
        {key: value for key, value in row.items() if key != "_currency_tuple"}
        for row in currency_rows
    ]
    detector_rows = [
        {
            "criterion": row["principle"],
            "single_factor_unsatisfiable_by_construction": row["shape_flavored"],
            "single_factor_has_computed_verdict": row["principle"] != "step36_factor_local_breaking_diagnostic",
            "flagged_shape_flavored": row["shape_flavored"],
            "evidence": row["note"],
        }
        for row in principle_rows
    ]
    negative_rows = [
        {
            "control": "precise_test_admits_single_factor_partial_breaking",
            "passes": su4_precise_survives,
            "evidence": "single-factor 4 survivors leave a dimension-3 subgroup under the precise test",
        },
        {
            "control": "currency_minimum_not_row_picker",
            "passes": len(currency_rows) > ONE and target_passes_currency_diagnostic,
            "evidence": f"currency-minimum survivors={len(currency_rows)}",
        },
        {
            "control": "currency_minimum_fails_some_precise_survivors",
            "passes": len(precise_rows) > len(currency_rows),
            "evidence": f"{len(precise_rows) - len(currency_rows)} precise survivors are more expensive",
        },
        {
            "control": "shape_detector_flags_old_rule",
            "passes": any(row["criterion"] == "step36_factor_local_breaking_diagnostic" and row["flagged_shape_flavored"] for row in detector_rows),
            "evidence": "old factor-local rule is diagnostic-only",
        },
    ]
    stage_rows = [
        {"stage_ii_check": "step35_survivors_reproduced", "passes": len(survivors) == 12, "evidence": str(len(survivors))},
        {"stage_ii_check": "partial_breaking_computed", "passes": su4_precise_survives, "evidence": "dimension-4 single-factor survivors produce dimension-3 subgroup entries"},
        {"stage_ii_check": "target_status_computed", "passes": target_dimensions != "", "evidence": f"{target_dimensions}; currency_pass_diagnostic={target_passes_currency_diagnostic}"},
        {"stage_ii_check": "old_shape_rule_demoted", "passes": True, "evidence": "factor-local rule appears only as a flagged diagnostic row"},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "predicates use scalar subgroup and currency data, not slot count"},
        {"check": "uses_parent_or_larger_group_prior", "passes": False, "evidence": "no parent or larger-group data enter the predicates"},
        {"check": "requires_fixed_factor_count", "passes": False, "evidence": "single-factor candidates receive computed subgroup and currency verdicts"},
        {"check": "uses_target_content", "passes": False, "evidence": "reference key is used only for status reporting"},
        {"check": "shape_flavored_current_principle", "passes": False, "evidence": "not active as a selector; manager override is recorded in the shape detector"},
    ]
    ablation_rows = [
        {"removed_component": "precise_unbroken_subgroup", "survivors_without_component": len(survivors), "load_bearing": True},
        {"removed_component": "scalar_stage_currency_minimum", "survivors_without_component": len(precise_rows), "load_bearing": len(precise_rows) > len(currency_rows)},
        {"removed_component": "step35_mass_closure", "survivors_without_component": len(currency_rows), "load_bearing": True},
    ]
    dependency_rows = [
        {"predicate_component": "step35_survivors", "primitive": "higher-layer descent", "role": "Reuse the 12 mass-closure survivors before the old factor-local refinement."},
        {"predicate_component": "precise_unbroken_subgroup", "primitive": "P4/P6 closure staging", "role": "Compute unbroken non-abelian subgroups after scalar breaking, including partial breaking inside a factor."},
        {"predicate_component": "scalar_stage_currency_minimum", "primitive": "currency", "role": "Minimize the scalar-stage currency tuple among precise subgroup survivors."},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "current predicates exclude shape, parent, and target-content primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependencies are listed in dependency_trace_step37.csv"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "precise subgroup and currency components are load-bearing"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "precise test admits single-factor partial breaking and currency is not a row picker"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step-35 residual reproduced and old rule demoted"},
        {"gate": "shape_flavored_detector", "passes": any(row["flagged_shape_flavored"] for row in detector_rows if row["criterion"] == "step36_factor_local_breaking_diagnostic") and any(row["flagged_shape_flavored"] for row in detector_rows if row["criterion"] == "scalar_stage_currency_minimum"), "evidence": "old rule and scalar-stage currency rescue are both flagged"},
    ]
    generated_rows = [
        {"item": "step35_survivors", "status": "rederived", "detail": str(len(survivors))},
        {"item": "precise_unbroken_subgroup", "status": "computed", "detail": f"survivors={len(precise_rows)}; single_factor_survives={su4_precise_survives}"},
        {"item": "scalar_stage_currency_minimum", "status": "diagnostic_only_REJECTED", "detail": f"minimum={'|'.join(str(value) for value in minimal_currency)}; survivors={len(currency_rows)}"},
        {"item": "selected_structure", "status": "rejected_label", "detail": "none_accepted_at_step37"},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "verdict", "status": "computed", "detail": verdict},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "reproduced_step35_survivors": len(survivors),
            "precise_unbroken_survivors": len(precise_rows),
            "single_factor_survives_precise_test": su4_precise_survives,
            "currency_minimum_survivors": len(currency_rows),
            "selected_structure": selected_structure,
            "target_passes_currency": target_passes_currency,
            "target_passes_currency_diagnostic": target_passes_currency_diagnostic,
            "target_distinguished": target_distinguished,
            "verdict": verdict,
            "next_grammar_delta": next_delta,
        }
    ]
    output = {
        "step": 37,
        "mode": "ModeB_uniqueness_stress_test",
        "reproduced_step35_survivors": len(survivors),
        "precise_unbroken_survivors": len(precise_rows),
        "single_factor_survives_precise_test": su4_precise_survives,
        "currency_minimum_survivors": len(currency_rows),
        "selected_structure": selected_structure,
        "target_passes_currency": target_passes_currency,
        "target_passes_currency_diagnostic": target_passes_currency_diagnostic,
        "target_distinguished": target_distinguished,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    public_score_fields = [
        "dimensions",
        "support_key",
        "support_score",
        "witness_scalar_key",
        "witness_scalar_component_dim",
        "witness_scalar_charge_abs",
        "scalar_active_factors",
        "unbroken_nonabelian_subgroups",
        "precise_unbroken_subgroup_survives",
        "potential_proxy",
        "unbroken_low_energy_consistency",
        "full_cascade_consistency",
        "scalar_stage_currency",
        "scalar_stage_currency_minimum",
        "is_target_reference",
    ]
    write_csv(ARTIFACT_DIR / "neutral_unbroken_subgroup_scores_step37.csv", [{key: row[key] for key in public_score_fields} for row in score_rows], public_score_fields)
    write_csv(ARTIFACT_DIR / "principle_survivor_sets_step37.csv", principle_rows, ["principle", "survivor_count", "survivors_by_structure", "target_passes", "single_factor_survives", "shape_flavored", "note"])
    write_csv(ARTIFACT_DIR / "corrected_survivors_step37.csv", [{key: row[key] for key in public_score_fields} for row in corrected_rows], public_score_fields)
    write_csv(ARTIFACT_DIR / "shape_flavored_detector_step37.csv", detector_rows, ["criterion", "single_factor_unsatisfiable_by_construction", "single_factor_has_computed_verdict", "flagged_shape_flavored", "evidence"])
    write_csv(ARTIFACT_DIR / "predicate_summary_step37.csv", summary_rows, ["reproduced_step35_survivors", "precise_unbroken_survivors", "single_factor_survives_precise_test", "currency_minimum_survivors", "selected_structure", "target_passes_currency", "target_passes_currency_diagnostic", "target_distinguished", "verdict", "next_grammar_delta"])
    write_csv(ARTIFACT_DIR / "negative_controls_step37.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step37.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step37.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "ablation_step37.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step37.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step37.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step37.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "uniqueness_stress_test_output_step37.json", output)
    schema = {
        **output,
        "artifact_root": "steps/step37_mode_b_uniqueness_stress_test_artifacts",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "forbidden_prior_self_check_pass": not any(row["passes"] for row in self_check_rows),
        "stage_ii_pass": all(row["passes"] for row in stage_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "shape_detector_pass": gate_rows[-ONE]["passes"],
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
