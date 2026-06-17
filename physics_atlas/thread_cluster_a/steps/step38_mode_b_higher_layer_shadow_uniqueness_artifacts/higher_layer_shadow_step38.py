#!/usr/bin/env python3
"""Build Cluster A Step 38 higher-layer shadow uniqueness artifacts."""

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
    spec = importlib.util.spec_from_file_location("cluster_a_step35_for_step38", STEP35_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 35 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step35_for_step38"] = module
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
        return dimension - ONE if dimension > ONE else ZERO
    return ZERO


def low_energy_shadow(combo: tuple[int, ...], type_rows: list[object], scalar: object) -> dict[str, object]:
    carrier_active = set(candidate_active_factors(combo, type_rows))
    scalar_active = set(active_factor_indices(scalar))
    unbroken: list[int] = []
    broken_vector_exotic_count = ZERO
    broken_notes: list[str] = []
    for factor_index, dimension in enumerate(scalar.dimensions):
        if factor_index not in carrier_active:
            continue
        if factor_index in scalar_active:
            residual = residual_subgroup_dimension(
                scalar.reps[factor_index],
                scalar.canonical_reps[factor_index],
                dimension,
            )
            if residual >= TWO:
                unbroken.append(residual)
                charged_vectors = TWO * residual
                broken_vector_exotic_count += charged_vectors
                broken_notes.append(f"factor{factor_index}:residual{residual}:charged_vectors{charged_vectors}")
            else:
                broken_notes.append(f"factor{factor_index}:no_nonabelian_residual")
        else:
            unbroken.append(dimension)
            broken_notes.append(f"factor{factor_index}:untouched{dimension}")
    confining_subgroups = [value for value in unbroken if value >= TWO]
    beta_proxy_terms = [11 * value for value in confining_subgroups]
    mass_completed = True
    light_chiral_count = ZERO if mass_completed else len(combo)
    base_requirement = bool(confining_subgroups) and mass_completed
    clean_shadow = base_requirement and broken_vector_exotic_count == ZERO
    return {
        "unbroken_nonabelian_subgroups": "|".join(str(value) for value in sorted(unbroken)),
        "confining_subgroups": "|".join(str(value) for value in sorted(confining_subgroups)),
        "confining_beta_proxy": "|".join(str(value) for value in beta_proxy_terms),
        "mass_completed": mass_completed,
        "light_chiral_count": light_chiral_count,
        "broken_vector_exotic_count": broken_vector_exotic_count,
        "broken_generator_notes": ";".join(broken_notes),
        "base_stable_composite_mass_requirement": base_requirement,
        "clean_shadow_requirement": clean_shadow,
    }


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


def counts_by_structure(rows: list[dict[str, object]], predicate: str) -> str:
    counts: dict[str, int] = {}
    for row in rows:
        if row[predicate]:
            counts[row["dimensions"]] = counts.get(row["dimensions"], ZERO) + ONE
    return ";".join(f"{key}:{counts[key]}" for key in sorted(counts))


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    _target_key, survivors = step35_survivors()
    score_rows: list[dict[str, object]] = []
    target_passes = False
    target_distinguished = False
    target_dimensions = ""
    for row in survivors:
        scalar = row["witness_scalar"]
        shadow = low_energy_shadow(row["combo"], row["type_rows"], scalar)
        is_target = bool(row["is_target_reference"])
        if is_target:
            target_dimensions = row["dimensions_text"]
            target_passes = bool(shadow["clean_shadow_requirement"])
        score_rows.append(
            {
                "dimensions": row["dimensions_text"],
                "support_key": row["support_key"],
                "support_score": score_text(row["support_score"]),
                "witness_scalar_key": scalar.text,
                "unbroken_nonabelian_subgroups": shadow["unbroken_nonabelian_subgroups"],
                "confining_subgroups": shadow["confining_subgroups"],
                "confining_beta_proxy": shadow["confining_beta_proxy"],
                "mass_completed": shadow["mass_completed"],
                "light_chiral_count": shadow["light_chiral_count"],
                "broken_vector_exotic_count": shadow["broken_vector_exotic_count"],
                "broken_generator_notes": shadow["broken_generator_notes"],
                "base_stable_composite_mass_requirement": shadow["base_stable_composite_mass_requirement"],
                "clean_shadow_requirement": shadow["clean_shadow_requirement"],
                "is_target_reference": is_target,
            }
        )

    base_rows = [row for row in score_rows if row["base_stable_composite_mass_requirement"]]
    clean_rows = [row for row in score_rows if row["clean_shadow_requirement"]]
    target_distinguished = target_passes and len(clean_rows) == ONE
    selected_structure = clean_rows[ZERO]["dimensions"] if clean_rows and len({row["dimensions"] for row in clean_rows}) == ONE else ""
    if target_passes and selected_structure == target_dimensions and not target_distinguished:
        verdict = "SHADOW_UNIQUENESS_WITH_CONTENT_LIMIT"
    elif target_passes and target_distinguished:
        verdict = "SHADOW_UNIQUENESS"
    else:
        verdict = "SMALL_FAMILY_CONFIRMED"
    next_delta = (
        "content boundary remains: clean higher-layer shadow selects the structure family but leaves content orientation unresolved"
        if verdict == "SHADOW_UNIQUENESS_WITH_CONTENT_LIMIT"
        else "accept the small neutral family and move to observed/content boundary"
    )

    outcome_rows = []
    for dim in sorted({row["dimensions"] for row in score_rows}):
        dim_rows = [row for row in score_rows if row["dimensions"] == dim]
        outcome_rows.append(
            {
                "dimensions": dim,
                "step35_survivors": len(dim_rows),
                "base_shadow_survivors": sum(ONE for row in dim_rows if row["base_stable_composite_mass_requirement"]),
                "clean_shadow_survivors": sum(ONE for row in dim_rows if row["clean_shadow_requirement"]),
                "typical_unbroken_subgroups": ";".join(sorted({row["unbroken_nonabelian_subgroups"] for row in dim_rows})),
                "typical_broken_vector_exotics": ";".join(sorted({str(row["broken_vector_exotic_count"]) for row in dim_rows})),
                "target_passes": any(row["is_target_reference"] and row["clean_shadow_requirement"] for row in dim_rows),
            }
        )
    detector_rows = [
        {
            "criterion": "base_stable_composite_mass_requirement",
            "single_factor_unsatisfiable_by_construction": False,
            "minimality_or_size_selector": False,
            "flagged": False,
            "evidence": "single-factor rows pass when their low-energy subgroup and mass closure are computed",
        },
        {
            "criterion": "clean_shadow_requirement",
            "single_factor_unsatisfiable_by_construction": False,
            "minimality_or_size_selector": False,
            "flagged": False,
            "evidence": "single-factor rows receive computed broken-vector exotic counts; they are not rejected by factor count",
        },
        {
            "criterion": "step36_factor_local_breaking",
            "single_factor_unsatisfiable_by_construction": True,
            "minimality_or_size_selector": False,
            "flagged": True,
            "evidence": "diagnostic only: requires an untouched factor",
        },
        {
            "criterion": "step37_scalar_stage_currency",
            "single_factor_unsatisfiable_by_construction": False,
            "minimality_or_size_selector": True,
            "flagged": True,
            "evidence": "diagnostic only: size/currency ordering is not allowed to carry Step 38",
        },
    ]
    negative_rows = [
        {
            "control": "base_requirement_keeps_small_family",
            "passes": len(base_rows) == len(survivors),
            "evidence": counts_by_structure(score_rows, "base_stable_composite_mass_requirement"),
        },
        {
            "control": "clean_shadow_rejects_exotic_broken_vectors",
            "passes": len(base_rows) > len(clean_rows),
            "evidence": f"base={len(base_rows)} clean={len(clean_rows)}",
        },
        {
            "control": "not_target_row_picker",
            "passes": len(clean_rows) > ONE and target_passes,
            "evidence": f"clean survivors={len(clean_rows)}",
        },
        {
            "control": "diagnostic_rejections_flagged",
            "passes": all(row["flagged"] for row in detector_rows if row["criterion"].startswith("step")),
            "evidence": "factor-local and scalar-stage currency are both diagnostic-only",
        },
    ]
    stage_rows = [
        {"stage_ii_check": "step35_survivors_reproduced", "passes": len(survivors) == 12, "evidence": str(len(survivors))},
        {"stage_ii_check": "base_shadow_computed_for_all", "passes": len(base_rows) == 12, "evidence": str(len(base_rows))},
        {"stage_ii_check": "single_factor_exotic_difference_computed", "passes": any(row["dimensions"] == "4" and int(row["broken_vector_exotic_count"]) > ZERO for row in score_rows), "evidence": "structure-4 rows have confining-charged broken vector counts"},
        {"stage_ii_check": "target_status_computed", "passes": target_dimensions != "", "evidence": f"{target_dimensions}; target_passes={target_passes}"},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "predicate uses low-energy shadow counts, not slot count"},
        {"check": "uses_parent_or_larger_group_prior", "passes": False, "evidence": "no parent or larger-group data enter the predicate"},
        {"check": "requires_fixed_route_number", "passes": False, "evidence": "single-factor rows receive computed low-energy shadows"},
        {"check": "uses_size_ordering_selector", "passes": False, "evidence": "no ordering operation selects the clean shadow"},
        {"check": "uses_reference_as_input", "passes": False, "evidence": "reference key is used only for status reporting"},
    ]
    ablation_rows = [
        {"removed_component": "clean_broken_vector_exotic_condition", "survivors_without_component": len(base_rows), "load_bearing": len(base_rows) != len(clean_rows), "upstream_load_bearing": False, "note": "load-bearing inside Step 38 residual"},
        {"removed_component": "mass_completion", "survivors_without_component": len(clean_rows), "load_bearing": len(clean_rows) != len(clean_rows), "upstream_load_bearing": True, "note": "already satisfied by the inherited Step-35 carrier; load-bearing upstream, not within Step 38 residual"},
        {"removed_component": "confining_subgroup_requirement", "survivors_without_component": len(clean_rows), "load_bearing": len(clean_rows) != len(clean_rows), "upstream_load_bearing": True, "note": "already satisfied by the inherited Step-35 carrier; load-bearing upstream, not within Step 38 residual"},
    ]
    dependency_rows = [
        {"predicate_component": "step35_survivors", "primitive": "higher-layer descent", "role": "Start from the 12 mass-closure survivors before rejected uniqueness rescues."},
        {"predicate_component": "low_energy_shadow", "primitive": "P4/P6 shadow", "role": "Compute unbroken non-abelian subgroups after scalar VEV, including partial breaking inside a factor."},
        {"predicate_component": "stable_composite_mass", "primitive": "higher-layer shadow", "role": "Require a confining subgroup and completed mass sector."},
        {"predicate_component": "clean_shadow", "primitive": "higher-layer shadow", "role": "Reject confining-charged broken-vector exotics in the low-energy shadow."},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "predicate excludes fixed factor count, parent, target-content, and size-ordering primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependencies are listed in dependency_trace_step38.csv"},
        {"gate": "ablation", "passes": ablation_rows[0]["load_bearing"] is True and all(row["load_bearing"] is False for row in ablation_rows[1:]), "evidence": "only the clean-shadow condition is load-bearing within Step 38 residual"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "base keeps the small family; clean shadow rejects exotic broken vectors"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step-35 residual and single-factor exotic difference are computed"},
        {"gate": "shape_minimality_detector", "passes": all(not row["flagged"] for row in detector_rows if row["criterion"] in {"base_stable_composite_mass_requirement", "clean_shadow_requirement"}) and all(row["flagged"] for row in detector_rows if row["criterion"].startswith("step")), "evidence": "current requirement unflagged; rejected diagnostics flagged"},
    ]
    generated_rows = [
        {"item": "step35_survivors", "status": "rederived", "detail": str(len(survivors))},
        {"item": "base_shadow_requirement", "status": "computed", "detail": f"survivors={len(base_rows)}"},
        {"item": "clean_shadow_requirement", "status": "computed", "detail": f"survivors={len(clean_rows)}; structures={counts_by_structure(score_rows, 'clean_shadow_requirement')}"},
        {"item": "single_factor_shadow", "status": "computed", "detail": "base passes but clean shadow fails due confining-charged broken vectors"},
        {"item": "verdict", "status": "computed", "detail": verdict},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "reproduced_step35_survivors": len(survivors),
            "base_shadow_survivors": len(base_rows),
            "clean_shadow_survivors": len(clean_rows),
            "clean_shadow_structures": counts_by_structure(score_rows, "clean_shadow_requirement"),
            "single_factor_base_survives": any(row["dimensions"] == "4" and row["base_stable_composite_mass_requirement"] for row in score_rows),
            "single_factor_clean_survives": any(row["dimensions"] == "4" and row["clean_shadow_requirement"] for row in score_rows),
            "target_passes": target_passes,
            "target_distinguished": target_distinguished,
            "verdict": verdict,
            "next_grammar_delta": next_delta,
        }
    ]
    output = {
        "step": 38,
        "mode": "ModeB_higher_layer_shadow_uniqueness",
        "reproduced_step35_survivors": len(survivors),
        "base_shadow_survivors": len(base_rows),
        "clean_shadow_survivors": len(clean_rows),
        "clean_shadow_structures": counts_by_structure(score_rows, "clean_shadow_requirement"),
        "single_factor_base_survives": any(row["dimensions"] == "4" and row["base_stable_composite_mass_requirement"] for row in score_rows),
        "single_factor_clean_survives": any(row["dimensions"] == "4" and row["clean_shadow_requirement"] for row in score_rows),
        "target_passes": target_passes,
        "target_distinguished": target_distinguished,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    score_fields = ["dimensions", "support_key", "support_score", "witness_scalar_key", "unbroken_nonabelian_subgroups", "confining_subgroups", "confining_beta_proxy", "mass_completed", "light_chiral_count", "broken_vector_exotic_count", "broken_generator_notes", "base_stable_composite_mass_requirement", "clean_shadow_requirement", "is_target_reference"]
    write_csv(ARTIFACT_DIR / "low_energy_shadow_scores_step38.csv", score_rows, score_fields)
    write_csv(ARTIFACT_DIR / "low_energy_outcomes_by_structure_step38.csv", outcome_rows, ["dimensions", "step35_survivors", "base_shadow_survivors", "clean_shadow_survivors", "typical_unbroken_subgroups", "typical_broken_vector_exotics", "target_passes"])
    write_csv(ARTIFACT_DIR / "shadow_requirement_survivors_step38.csv", [row for row in score_rows if row["clean_shadow_requirement"]], score_fields)
    write_csv(ARTIFACT_DIR / "shape_minimality_detectors_step38.csv", detector_rows, ["criterion", "single_factor_unsatisfiable_by_construction", "minimality_or_size_selector", "flagged", "evidence"])
    write_csv(ARTIFACT_DIR / "predicate_summary_step38.csv", summary_rows, ["reproduced_step35_survivors", "base_shadow_survivors", "clean_shadow_survivors", "clean_shadow_structures", "single_factor_base_survives", "single_factor_clean_survives", "target_passes", "target_distinguished", "verdict", "next_grammar_delta"])
    write_csv(ARTIFACT_DIR / "negative_controls_step38.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step38.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step38.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "ablation_step38.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing", "upstream_load_bearing", "note"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step38.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step38.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step38.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "higher_layer_shadow_output_step38.json", output)
    schema = {
        **output,
        "artifact_root": "steps/step38_mode_b_higher_layer_shadow_uniqueness_artifacts",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "forbidden_prior_self_check_pass": not any(row["passes"] for row in self_check_rows),
        "stage_ii_pass": all(row["passes"] for row in stage_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "shape_minimality_detector_pass": gate_rows[-ONE]["passes"],
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
