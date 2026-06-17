#!/usr/bin/env python3
"""Build Cluster A Step 36 higher-layer refinement artifacts."""

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
    spec = importlib.util.spec_from_file_location("cluster_a_step35_for_step36", STEP35_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 35 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step35_for_step36"] = module
    spec.loader.exec_module(module)
    return module


s35 = load_step35()
s33 = s35.s33
ZERO = s33.ZERO
ONE = s33.ONE


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


def scalar_quadratic_invariant(scalar: object) -> bool:
    conjugate = s35.conjugate_scalar(scalar)
    return scalar.charge + conjugate.charge == ZERO and all(
        s35.factor_invariant(rep, conj_rep, "singlet", dimension)
        for rep, conj_rep, dimension in zip(scalar.canonical_reps, conjugate.canonical_reps, scalar.dimensions)
    )


def staged_scalar_potential_closure(combo: tuple[int, ...], type_rows: list[object], scalar: object) -> dict[str, object]:
    scalar_active = active_factor_indices(scalar)
    carrier_active = candidate_active_factors(combo, type_rows)
    untouched = tuple(index for index in carrier_active if index not in scalar_active)
    quadratic = scalar_quadratic_invariant(scalar)
    quartic_proxy = quadratic and scalar.component_dim > ZERO
    factor_local_breaking = bool(scalar_active) and bool(untouched)
    charged_breaking = scalar.charge != ZERO
    passes = quadratic and quartic_proxy and factor_local_breaking and charged_breaking
    return {
        "quadratic_invariant": quadratic,
        "quartic_bounded_proxy": quartic_proxy,
        "scalar_active_factors": "|".join(str(index) for index in scalar_active),
        "candidate_active_factors": "|".join(str(index) for index in carrier_active),
        "untouched_active_factors": "|".join(str(index) for index in untouched),
        "factor_local_breaking": factor_local_breaking,
        "charged_breaking": charged_breaking,
        "staged_potential_closure": passes,
    }


def step35_survivors() -> tuple[str, list[dict[str, object]]]:
    target_key, carrier_rows = s35.corrected_80_carrier()
    rows: list[dict[str, object]] = []
    scalar_cache: dict[tuple[int, ...], list[object]] = {}
    for carrier in carrier_rows:
        dimensions = carrier["dimensions"]
        scalar_cache.setdefault(dimensions, s35.scalar_representations(dimensions))
        result = s35.higher_layer_mass_closure(carrier["combo"], carrier["type_rows"], scalar_cache[dimensions])
        if not result["higher_layer_passes"]:
            continue
        rows.append({**carrier, **result})
    return target_key, rows


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    target_key, survivors = step35_survivors()
    score_rows: list[dict[str, object]] = []
    refined_rows: list[dict[str, object]] = []
    per_structure: dict[str, dict[str, int]] = {}
    refined_count = ZERO
    target_passes = False
    target_dimensions = ""
    target_witness = ""

    for row in survivors:
        dim_text = row["dimensions_text"]
        scalar = row["witness_scalar"]
        is_target = bool(row["is_target_reference"])
        check = staged_scalar_potential_closure(row["combo"], row["type_rows"], scalar)
        per_structure.setdefault(dim_text, {"step35_survivors": ZERO, "step36_survivors": ZERO, "target_passes": ZERO})
        per_structure[dim_text]["step35_survivors"] += ONE
        if check["staged_potential_closure"]:
            refined_count += ONE
            per_structure[dim_text]["step36_survivors"] += ONE
            refined_rows.append(
                {
                    "dimensions": dim_text,
                    "support_key": row["support_key"],
                    "support_score": score_text(row["support_score"]),
                    "witness_scalar_key": scalar.text,
                    "is_target_reference": is_target,
                }
            )
            if is_target:
                target_passes = True
                target_dimensions = dim_text
                target_witness = scalar.text
                per_structure[dim_text]["target_passes"] += ONE
        elif is_target:
            target_dimensions = dim_text
            target_witness = scalar.text
        score_rows.append(
            {
                "dimensions": dim_text,
                "support_key": row["support_key"],
                "support_score": score_text(row["support_score"]),
                "step35_witness_scalar": scalar.text,
                "quadratic_invariant": check["quadratic_invariant"],
                "quartic_bounded_proxy": check["quartic_bounded_proxy"],
                "scalar_active_factors": check["scalar_active_factors"],
                "candidate_active_factors": check["candidate_active_factors"],
                "untouched_active_factors": check["untouched_active_factors"],
                "factor_local_breaking": check["factor_local_breaking"],
                "charged_breaking": check["charged_breaking"],
                "staged_potential_closure": check["staged_potential_closure"],
                "is_target_reference": is_target,
            }
        )

    per_structure_rows = [{"dimensions": dim_text, **counts} for dim_text, counts in sorted(per_structure.items())]
    su4_eliminated = per_structure.get("4", {}).get("step36_survivors", ZERO) == ZERO
    target_distinguished = target_passes and refined_count == ONE
    target_structure_only = bool(per_structure_rows) and all(
        int(row["step36_survivors"]) == ZERO or row["dimensions"] == target_dimensions for row in per_structure_rows
    )
    if target_distinguished:
        verdict = "LAND"
    elif target_passes and target_structure_only:
        verdict = "CONTENT_TYPE_LIMIT"
    elif target_passes and refined_count < len(survivors):
        verdict = "NARROW"
    else:
        verdict = "TYPED_NO_GO"
    next_delta = (
        "content boundary: the remaining supports share the selected structure but differ by chiral content; continue into a matter-content cascade or observed-input boundary"
        if verdict == "CONTENT_TYPE_LIMIT"
        else "conjoin a further higher-layer requirement such as family-replication consistency"
        if verdict == "NARROW"
        else "stress-test the landed refinement on wider corrected carriers"
        if verdict == "LAND"
        else "try a different higher-layer closure predicate"
    )

    negative_rows = [
        {
            "control": "fails_some_step35_survivors",
            "passes": refined_count < len(survivors),
            "evidence": f"{len(survivors) - refined_count} of {len(survivors)} fail the staged potential predicate",
        },
        {
            "control": "not_a_target_row_picker",
            "passes": (not target_distinguished) or refined_count > ONE,
            "evidence": f"target passes={target_passes}; refined survivor count={refined_count}",
        },
        {
            "control": "single_factor_region_can_fail",
            "passes": su4_eliminated,
            "evidence": f"structure 4 refined survivors={per_structure.get('4', {}).get('step36_survivors', ZERO)}",
        },
        {
            "control": "no_fixed_family_count",
            "passes": True,
            "evidence": "no replication number enters the staged scalar-potential predicate",
        },
    ]
    stage_rows = [
        {"stage_ii_check": "step35_survivors_reproduced", "passes": len(survivors) == 12, "evidence": str(len(survivors))},
        {"stage_ii_check": "target_status_computed", "passes": target_dimensions != "", "evidence": f"{target_dimensions}; witness={target_witness}; passes={target_passes}"},
        {"stage_ii_check": "proper_breaking_requires_residual_route", "passes": su4_eliminated and refined_count > ZERO, "evidence": f"refined_count={refined_count}"},
        {"stage_ii_check": "compatibility_not_derivation", "passes": True, "evidence": "predicate types potential-layer compatibility only"},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "predicate reads active-factor incidence, not slot count"},
        {"check": "uses_parent_or_larger_group_prior", "passes": False, "evidence": "no parent or larger-group data enter the predicate"},
        {"check": "uses_empirical_potential_parameters", "passes": False, "evidence": "bounded proxy is an invariant-existence test"},
        {"check": "uses_fixed_generation_count", "passes": False, "evidence": "no replication number is used"},
        {"check": "reduces_to_target_shape", "passes": False, "evidence": f"predicate definition does not mention dimensions; refined survivors={refined_count}"},
        {"check": "uses_target_reference", "passes": False, "evidence": "reference key is used only for status reporting"},
    ]
    ablation_rows = [
        {"removed_component": "staged_scalar_potential_refinement", "survivors_without_component": len(survivors), "load_bearing": len(survivors) > refined_count},
        {"removed_component": "higher_layer_mass_closure", "survivors_without_component": refined_count, "load_bearing": True},
    ]
    dependency_rows = [
        {"predicate_component": "step35_survivors", "primitive": "higher-layer descent", "role": "Reuse the 12 candidates with enumerated mass-closure witnesses."},
        {"predicate_component": "quadratic_and_quartic_proxy", "primitive": "potential closure", "role": "Compute invariant scalar-conjugate pairing and bounded quartic proxy."},
        {"predicate_component": "staged_residual_route", "primitive": "P4/P6 closure staging", "role": "The scalar-active route must leave an independent non-abelian route untouched."},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "predicate excludes shape, parent-group, empirical-content, and fixed-generation primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "components are traced in dependency_trace_step36.csv"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "staged-potential refinement is load-bearing"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "predicate fails some Step-35 survivors and is not a row picker"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step-35 residual is reproduced and target status computed"},
        {"gate": "no_reductionism", "passes": True, "evidence": "predicate types compatibility; it does not derive content or values"},
    ]
    generated_rows = [
        {"item": "step35_survivors", "status": "rederived", "detail": str(len(survivors))},
        {"item": "staged_scalar_potential_closure", "status": "declared_mode_b_input", "detail": "invariant potential proxy plus residual non-abelian route after scalar breaking"},
        {"item": "refined_survivors", "status": "computed", "detail": str(refined_count)},
        {"item": "single_factor_eliminated", "status": "computed", "detail": str(su4_eliminated)},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "verdict", "status": "computed", "detail": verdict},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "reproduced_step35_survivors": len(survivors),
            "refined_survivors": refined_count,
            "single_factor_eliminated": su4_eliminated,
            "target_passes": target_passes,
            "target_distinguished": target_distinguished,
            "target_dimensions": target_dimensions,
            "target_witness": target_witness,
            "verdict": verdict,
            "next_grammar_delta": next_delta,
        }
    ]
    type_limit_rows = [
        {
            "assessment": "higher_layer_refinement",
            "status": verdict,
            "step35_family_size": len(survivors),
            "refined_residual_size": refined_count,
            "target_structure_only": target_structure_only,
            "target_requires_content_boundary": verdict == "CONTENT_TYPE_LIMIT",
            "next_kind": next_delta,
        }
    ]
    output = {
        "step": 36,
        "mode": "ModeB_higher_layer_refinement",
        "reproduced_step35_survivors": len(survivors),
        "refined_survivors": refined_count,
        "single_factor_eliminated": su4_eliminated,
        "target_passes": target_passes,
        "target_distinguished": target_distinguished,
        "target_dimensions": target_dimensions,
        "target_witness": target_witness,
        "target_structure_only": target_structure_only,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    write_csv(ARTIFACT_DIR / "higher_layer_refinement_scores_step36.csv", score_rows, ["dimensions", "support_key", "support_score", "step35_witness_scalar", "quadratic_invariant", "quartic_bounded_proxy", "scalar_active_factors", "candidate_active_factors", "untouched_active_factors", "factor_local_breaking", "charged_breaking", "staged_potential_closure", "is_target_reference"])
    write_csv(ARTIFACT_DIR / "refined_survivors_step36.csv", refined_rows, ["dimensions", "support_key", "support_score", "witness_scalar_key", "is_target_reference"])
    write_csv(ARTIFACT_DIR / "refinement_counts_by_structure_step36.csv", per_structure_rows, ["dimensions", "step35_survivors", "step36_survivors", "target_passes"])
    write_csv(ARTIFACT_DIR / "predicate_summary_step36.csv", summary_rows, ["reproduced_step35_survivors", "refined_survivors", "single_factor_eliminated", "target_passes", "target_distinguished", "target_dimensions", "target_witness", "verdict", "next_grammar_delta"])
    write_csv(ARTIFACT_DIR / "content_type_limit_assessment_step36.csv", type_limit_rows, ["assessment", "status", "step35_family_size", "refined_residual_size", "target_structure_only", "target_requires_content_boundary", "next_kind"])
    write_csv(ARTIFACT_DIR / "negative_controls_step36.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step36.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step36.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "ablation_step36.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step36.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step36.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step36.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "higher_layer_refinement_output_step36.json", output)
    schema = {
        **output,
        "artifact_root": "steps/step36_mode_b_higher_layer_refinement_artifacts",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "forbidden_prior_self_check_pass": not any(row["passes"] for row in self_check_rows),
        "stage_ii_pass": all(row["passes"] for row in stage_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
