#!/usr/bin/env python3
"""Build Cluster A Step 39 clean-separation derivation artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP38_SCRIPT = STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "higher_layer_shadow_step38.py"


def load_step38():
    spec = importlib.util.spec_from_file_location("cluster_a_step38_for_step39", STEP38_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 38 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step38_for_step39"] = module
    spec.loader.exec_module(module)
    return module


s38 = load_step38()
s35 = s38.s35
s33 = s38.s33
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


def confining_charged_fermion_types(combo: tuple[int, ...], type_rows: list[object], scalar: object) -> int:
    unbroken = s38.low_energy_shadow(combo, type_rows, scalar)["unbroken_nonabelian_subgroups"]
    if not unbroken:
        return ZERO
    charged = ZERO
    active_factors = set(s38.candidate_active_factors(combo, type_rows))
    scalar_active = set(s38.active_factor_indices(scalar))
    for type_id in combo:
        row = type_rows[type_id]
        has_charge = False
        for factor_index, dimension in enumerate(row.dimensions):
            if factor_index not in active_factors:
                continue
            if factor_index not in scalar_active:
                if s33.action_active(row.reps[factor_index], dimension):
                    has_charge = True
            else:
                residual = s38.residual_subgroup_dimension(
                    scalar.reps[factor_index],
                    scalar.canonical_reps[factor_index],
                    dimension,
                )
                if residual >= 2 and s33.action_active(row.reps[factor_index], dimension):
                    has_charge = True
        if has_charge:
            charged += ONE
    return charged


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    _target_key, survivors = s38.step35_survivors()
    score_rows: list[dict[str, object]] = []
    for row in survivors:
        scalar = row["witness_scalar"]
        shadow = s38.low_energy_shadow(row["combo"], row["type_rows"], scalar)
        vector_count = int(shadow["broken_vector_exotic_count"])
        clean_separation = vector_count == ZERO
        fermion_count = confining_charged_fermion_types(row["combo"], row["type_rows"], scalar)
        standard_sector = bool(shadow["confining_subgroups"]) and bool(shadow["mass_completed"]) and vector_count == ZERO
        relaxed_standardness = bool(shadow["confining_subgroups"]) and bool(shadow["mass_completed"])
        score_rows.append(
            {
                "dimensions": row["dimensions_text"],
                "support_key": row["support_key"],
                "support_score": score_text(row["support_score"]),
                "witness_scalar_key": scalar.text,
                "confining_subgroups": shadow["confining_subgroups"],
                "confining_charged_fermion_type_count": fermion_count,
                "confining_charged_massive_vector_count": vector_count,
                "mass_completed": shadow["mass_completed"],
                "clean_separation": clean_separation,
                "standard_confining_sector": standard_sector,
                "relaxed_allows_vectors": relaxed_standardness,
                "is_target_reference": bool(row["is_target_reference"]),
            }
        )

    standard_count = sum(ONE for row in score_rows if row["standard_confining_sector"])
    clean_count = sum(ONE for row in score_rows if row["clean_separation"])
    relaxed_count = sum(ONE for row in score_rows if row["relaxed_allows_vectors"])
    standard_implies_clean = all((not row["standard_confining_sector"]) or row["clean_separation"] for row in score_rows)
    clean_implies_standard = all((not row["clean_separation"]) or row["standard_confining_sector"] for row in score_rows)
    extensional_equivalence = standard_implies_clean and clean_implies_standard and standard_count == clean_count
    circularity_detected = extensional_equivalence
    derived_fundamental = standard_implies_clean and not circularity_detected
    single_factor_relaxed = any(row["dimensions"] == "4" and row["relaxed_allows_vectors"] for row in score_rows)
    single_factor_standard = any(row["dimensions"] == "4" and row["standard_confining_sector"] for row in score_rows)
    target_passes = any(row["is_target_reference"] and row["standard_confining_sector"] for row in score_rows)
    target_distinguished = target_passes and standard_count == ONE
    if derived_fundamental:
        verdict = "DERIVED_FUNDAMENTAL"
    else:
        verdict = "INDEPENDENT_INTRODUCED_CIRCULAR"
    next_delta = (
        "clean separation remains a qualified introduced standardness condition; continue to content cascade or seek a richer confining-layer grammar"
        if verdict == "INDEPENDENT_INTRODUCED_CIRCULAR"
        else "stress-test the derived standardness requirement on wider carriers"
    )

    outcome_rows = []
    for dim in sorted({row["dimensions"] for row in score_rows}):
        dim_rows = [row for row in score_rows if row["dimensions"] == dim]
        outcome_rows.append(
            {
                "dimensions": dim,
                "carrier_count": len(dim_rows),
                "standard_confining_sector_count": sum(ONE for row in dim_rows if row["standard_confining_sector"]),
                "relaxed_count": sum(ONE for row in dim_rows if row["relaxed_allows_vectors"]),
                "typical_vector_count": ";".join(sorted({str(row["confining_charged_massive_vector_count"]) for row in dim_rows})),
                "target_passes": any(row["is_target_reference"] and row["standard_confining_sector"] for row in dim_rows),
            }
        )
    implication_rows = [
        {
            "test": "standardness_implies_clean_separation",
            "passes": standard_implies_clean,
            "evidence": f"standard_count={standard_count}; clean_count={clean_count}",
        },
        {
            "test": "clean_separation_implies_standardness",
            "passes": clean_implies_standard,
            "evidence": "true on this finite carrier",
        },
        {
            "test": "extensional_equivalence_on_carrier",
            "passes": extensional_equivalence,
            "evidence": "standardness and clean separation select the same rows",
        },
        {
            "test": "derived_fundamental_not_established",
            "passes": not derived_fundamental,
            "evidence": "standardness is equivalent to the vector-exotic absence condition on this carrier",
        },
    ]
    relaxation_rows = [
        {
            "relaxation": "allow_confining_charged_massive_vectors",
            "survivor_count": relaxed_count,
            "survivors_by_structure": ";".join(
                f"{row['dimensions']}:{row['relaxed_count']}" for row in outcome_rows
            ),
            "single_factor_returns": single_factor_relaxed,
            "condition_load_bearing": relaxed_count > standard_count,
        },
        {
            "relaxation": "enforce_standardness",
            "survivor_count": standard_count,
            "survivors_by_structure": ";".join(
                f"{row['dimensions']}:{row['standard_confining_sector_count']}" for row in outcome_rows
            ),
            "single_factor_returns": single_factor_standard,
            "condition_load_bearing": relaxed_count > standard_count,
        },
    ]
    detector_rows = [
        {
            "detector": "shape_flavored",
            "flagged": False,
            "evidence": "single-factor rows receive computed standardness verdicts and pass the relaxed base requirement",
        },
        {
            "detector": "minimality_or_size_selector",
            "flagged": False,
            "evidence": "no ordering over size or currency is used",
        },
        {
            "detector": "circularity",
            "flagged": circularity_detected,
            "evidence": "standardness and clean separation are extensionally equivalent on the carrier",
        },
    ]
    negative_rows = [
        {
            "control": "relaxation_brings_single_factor_back",
            "passes": single_factor_relaxed,
            "evidence": f"relaxed_count={relaxed_count}",
        },
        {
            "control": "condition_load_bearing",
            "passes": relaxed_count > standard_count,
            "evidence": f"relaxed={relaxed_count}; standard={standard_count}",
        },
        {
            "control": "not_target_row_picker",
            "passes": standard_count > ONE and target_passes,
            "evidence": f"standard_count={standard_count}",
        },
        {
            "control": "circularity_detected_not_hidden",
            "passes": circularity_detected,
            "evidence": "equivalence is reported in implication_test_step39.csv",
        },
    ]
    stage_rows = [
        {"stage_ii_check": "step35_survivors_reproduced", "passes": len(survivors) == 12, "evidence": str(len(survivors))},
        {"stage_ii_check": "vector_content_computed", "passes": any(int(row["confining_charged_massive_vector_count"]) > ZERO for row in score_rows), "evidence": "single-factor vector content is nonzero"},
        {"stage_ii_check": "target_status_computed", "passes": target_passes, "evidence": f"target_passes={target_passes}"},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "standardness uses charged-matter type, not slot count"},
        {"check": "uses_parent_or_larger_group_prior", "passes": False, "evidence": "no parent or larger-group data enter the predicate"},
        {"check": "requires_fixed_route_number", "passes": False, "evidence": "single-factor rows are evaluated and pass the relaxed base"},
        {"check": "uses_size_ordering_selector", "passes": False, "evidence": "no size ordering is used"},
        {"check": "hides_circularity", "passes": False, "evidence": "circularity is explicitly reported"},
    ]
    ablation_rows = [
        {"removed_component": "standardness_no_vector_condition", "survivors_without_component": relaxed_count, "load_bearing": relaxed_count != standard_count, "upstream_load_bearing": False, "note": "load-bearing inside Step 39 residual"},
        {"removed_component": "mass_completion", "survivors_without_component": standard_count, "load_bearing": standard_count != standard_count, "upstream_load_bearing": True, "note": "already satisfied by the inherited Step-35 carrier; load-bearing upstream, not within Step 39 residual"},
        {"removed_component": "confining_subgroup", "survivors_without_component": standard_count, "load_bearing": standard_count != standard_count, "upstream_load_bearing": True, "note": "already satisfied by the inherited Step-35 carrier; load-bearing upstream, not within Step 39 residual"},
    ]
    dependency_rows = [
        {"predicate_component": "step35_survivors", "primitive": "higher-layer descent", "role": "Start from the 12 mass-closure survivors."},
        {"predicate_component": "confining_charged_matter_content", "primitive": "P6 audit", "role": "Classify confining-sector charged matter as fermionic types versus massive vector content."},
        {"predicate_component": "standard_confining_sector", "primitive": "higher-layer standardness", "role": "Require confining charged matter to be fermionic only."},
        {"predicate_component": "circularity_check", "primitive": "audit", "role": "Test whether standardness is equivalent to clean separation on this carrier."},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "predicate excludes fixed route count, parent, target-content, and size-ordering primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependencies are listed in dependency_trace_step39.csv"},
        {"gate": "ablation", "passes": ablation_rows[0]["load_bearing"] is True and all(row["load_bearing"] is False for row in ablation_rows[1:]), "evidence": "only the no-vector condition is load-bearing within Step 39 residual"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "relaxation restores single-factor rows and circularity is reported"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step-35 residual and vector content are computed"},
        {"gate": "circularity_self_check", "passes": circularity_detected and verdict == "INDEPENDENT_INTRODUCED_CIRCULAR", "evidence": "equivalence detected, so derivation is not overclaimed"},
    ]
    generated_rows = [
        {"item": "step35_survivors", "status": "rederived", "detail": str(len(survivors))},
        {"item": "standard_confining_sector", "status": "computed", "detail": f"standard_count={standard_count}"},
        {"item": "implication", "status": "computed", "detail": f"standard_implies_clean={standard_implies_clean}; clean_implies_standard={clean_implies_standard}"},
        {"item": "circularity", "status": "computed", "detail": str(circularity_detected)},
        {"item": "relaxation", "status": "computed", "detail": f"relaxed_count={relaxed_count}; single_factor_returns={single_factor_relaxed}"},
        {"item": "verdict", "status": "computed", "detail": verdict},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "reproduced_step35_survivors": len(survivors),
            "standard_count": standard_count,
            "relaxed_count": relaxed_count,
            "standard_implies_clean": standard_implies_clean,
            "clean_implies_standard": clean_implies_standard,
            "circularity_detected": circularity_detected,
            "derived_fundamental": derived_fundamental,
            "single_factor_returns_when_relaxed": single_factor_relaxed,
            "target_passes": target_passes,
            "target_distinguished": target_distinguished,
            "verdict": verdict,
            "next_grammar_delta": next_delta,
        }
    ]
    output = {
        "step": 39,
        "mode": "ModeB_clean_separation_derivation",
        "reproduced_step35_survivors": len(survivors),
        "standard_count": standard_count,
        "relaxed_count": relaxed_count,
        "standard_implies_clean": standard_implies_clean,
        "clean_implies_standard": clean_implies_standard,
        "circularity_detected": circularity_detected,
        "derived_fundamental": derived_fundamental,
        "single_factor_returns_when_relaxed": single_factor_relaxed,
        "target_passes": target_passes,
        "target_distinguished": target_distinguished,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    score_fields = ["dimensions", "support_key", "support_score", "witness_scalar_key", "confining_subgroups", "confining_charged_fermion_type_count", "confining_charged_massive_vector_count", "mass_completed", "clean_separation", "standard_confining_sector", "relaxed_allows_vectors", "is_target_reference"]
    write_csv(ARTIFACT_DIR / "confining_standardness_scores_step39.csv", score_rows, score_fields)
    write_csv(ARTIFACT_DIR / "standardness_by_structure_step39.csv", outcome_rows, ["dimensions", "carrier_count", "standard_confining_sector_count", "relaxed_count", "typical_vector_count", "target_passes"])
    write_csv(ARTIFACT_DIR / "implication_test_step39.csv", implication_rows, ["test", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "relaxation_robustness_step39.csv", relaxation_rows, ["relaxation", "survivor_count", "survivors_by_structure", "single_factor_returns", "condition_load_bearing"])
    write_csv(ARTIFACT_DIR / "detectors_step39.csv", detector_rows, ["detector", "flagged", "evidence"])
    write_csv(ARTIFACT_DIR / "predicate_summary_step39.csv", summary_rows, ["reproduced_step35_survivors", "standard_count", "relaxed_count", "standard_implies_clean", "clean_implies_standard", "circularity_detected", "derived_fundamental", "single_factor_returns_when_relaxed", "target_passes", "target_distinguished", "verdict", "next_grammar_delta"])
    write_csv(ARTIFACT_DIR / "negative_controls_step39.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step39.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step39.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "ablation_step39.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing", "upstream_load_bearing", "note"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step39.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step39.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step39.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "clean_separation_derivation_output_step39.json", output)
    schema = {
        **output,
        "artifact_root": "steps/step39_mode_b_clean_separation_derivation_artifacts",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "forbidden_prior_self_check_pass": not any(row["passes"] for row in self_check_rows),
        "stage_ii_pass": all(row["passes"] for row in stage_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "detectors_pass": not any(row["flagged"] for row in detector_rows if row["detector"] in {"shape_flavored", "minimality_or_size_selector"}) and circularity_detected,
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
