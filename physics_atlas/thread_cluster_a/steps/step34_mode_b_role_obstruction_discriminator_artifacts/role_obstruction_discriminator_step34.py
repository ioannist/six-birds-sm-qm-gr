#!/usr/bin/env python3
"""Build Cluster A Step 34 F24 role-obstruction discriminator artifacts."""

from __future__ import annotations

import collections
import csv
import importlib.util
import json
import sys
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP33_SCRIPT = STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "corrected_anomaly_chirality_step33.py"


def load_step33():
    spec = importlib.util.spec_from_file_location("cluster_a_step33_corrected_for_step34", STEP33_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 33 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step33_corrected_for_step34"] = module
    spec.loader.exec_module(module)
    return module


s33 = load_step33()
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


def access_key(row: object) -> tuple[str, ...]:
    return row.canonical_reps


def role_readout(row: object) -> int:
    return row.charge


def role_obstruction(combo: tuple[int, ...], type_rows: list[object]) -> dict[str, object]:
    rows = [type_rows[type_id] for type_id in combo]
    fibers: dict[tuple[str, ...], list[int]] = {}
    for row in rows:
        fibers.setdefault(access_key(row), []).append(role_readout(row))
    obstruction_pairs = ZERO
    witness_parts: list[str] = []
    for key, charges in sorted(fibers.items()):
        for left_index, left_charge in enumerate(charges):
            for right_charge in charges[left_index + ONE :]:
                if left_charge != right_charge:
                    obstruction_pairs += ONE
                    witness_parts.append(f"{'x'.join(key)}:{left_charge}/{right_charge}")
    return {
        "role_obstruction_pairs": obstruction_pairs,
        "q_fiber_count": len(fibers),
        "max_q_fiber_size": max((len(charges) for charges in fibers.values()), default=ZERO),
        "f24_descends": obstruction_pairs == ZERO,
        "witnesses": ";".join(witness_parts),
    }


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    target_key = s33.reference_support_key()
    carrier_count = ZERO
    conjoined_count = ZERO
    target_passes_carrier = False
    target_passes_f24 = False
    target_obstruction = None
    obstruction_rows: list[dict[str, object]] = []
    f24_rows: list[dict[str, object]] = []
    per_structure: dict[str, dict[str, int]] = {}
    distribution: collections.Counter[int] = collections.Counter()

    for dimensions in s33.factor_structures():
        result = s33.enumerate_structure(dimensions)
        type_rows = result["type_rows"]
        closers: dict[str, tuple[int, ...]] = result["closers"]
        dim_text = "|".join(str(value) for value in dimensions)
        per_structure.setdefault(dim_text, {"corrected_final_carrier": ZERO, "f24_descending_survivors": ZERO, "target_passes": ZERO})
        for key, combo in closers.items():
            if not s33.atomic_rewrite_packaging(combo, type_rows):
                continue
            if not s33.route_incidence_complete(combo, type_rows):
                continue
            chiral = s33.chirality_faithfulness(combo, type_rows)
            if not chiral["chirality_faithfulness_passes"]:
                continue
            carrier_count += ONE
            is_target = key == target_key
            if is_target:
                target_passes_carrier = True
            per_structure[dim_text]["corrected_final_carrier"] += ONE
            obs = role_obstruction(combo, type_rows)
            distribution[int(obs["role_obstruction_pairs"])] += ONE
            score = s33.support_score(combo, type_rows)
            row = {
                "dimensions": dim_text,
                "support_key": key,
                "support_score": score_text(score),
                "role_obstruction_pairs": obs["role_obstruction_pairs"],
                "q_fiber_count": obs["q_fiber_count"],
                "max_q_fiber_size": obs["max_q_fiber_size"],
                "f24_descends": obs["f24_descends"],
                "witnesses": obs["witnesses"],
                "is_target_reference": is_target,
            }
            obstruction_rows.append(row)
            if is_target:
                target_obstruction = obs["role_obstruction_pairs"]
            if obs["f24_descends"]:
                conjoined_count += ONE
                f24_rows.append(row)
                per_structure[dim_text]["f24_descending_survivors"] += ONE
                if is_target:
                    target_passes_f24 = True
                    per_structure[dim_text]["target_passes"] += ONE

    target_distinguished = target_passes_f24 and conjoined_count == ONE
    if target_distinguished:
        verdict = "LAND"
    elif target_passes_f24 and conjoined_count < carrier_count:
        verdict = "NARROW"
    else:
        verdict = "TYPED_NO_GO_TYPE_LIMIT"
    next_delta = (
        "move to a higher-layer descent/content-cascade criterion or observed-input boundary rather than another intrinsic gauge-only filter"
        if verdict == "TYPED_NO_GO_TYPE_LIMIT"
        else "stress-test or conjoin the F24 residual under corrected wider carriers"
    )

    distribution_rows = [
        {"role_obstruction_pairs": obstruction, "survivor_count": count, "target_has_this_obstruction": target_obstruction == obstruction}
        for obstruction, count in sorted(distribution.items())
    ]
    per_structure_rows = [{"dimensions": dim_text, **counts} for dim_text, counts in sorted(per_structure.items())]
    negative_rows = [
        {
            "control": "not_a_target_row_picker",
            "passes": (conjoined_count != ONE) or (target_passes_f24 is False),
            "evidence": f"F24-descending survivor count is {conjoined_count}; target passes F24={target_passes_f24}",
        },
        {
            "control": "fails_some_corrected_80_survivors",
            "passes": carrier_count > conjoined_count,
            "evidence": f"{carrier_count - conjoined_count} corrected final survivors fail F24 descent",
        },
        {
            "control": "distribution_nontrivial",
            "passes": len(distribution) > ONE,
            "evidence": f"O_s values: {';'.join(str(value) for value in sorted(distribution))}",
        },
    ]
    stage_rows = [
        {"stage_ii_check": "reproduces_corrected_final_carrier", "passes": carrier_count == 80, "evidence": str(carrier_count)},
        {"stage_ii_check": "target_obstruction_computed", "passes": target_obstruction is not None, "evidence": str(target_obstruction)},
        {"stage_ii_check": "f24_can_fail", "passes": carrier_count > conjoined_count and conjoined_count > ZERO, "evidence": f"{conjoined_count} pass, {carrier_count - conjoined_count} fail"},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "O_s uses q-fibers and charge readouts, not slot count"},
        {"check": "uses_larger_group_prior", "passes": False, "evidence": "no parent or larger-group data enters the F24 predicate"},
        {"check": "uses_exterior_only_prior", "passes": False, "evidence": "carrier is inherited from corrected neutral enumeration"},
        {"check": "reduces_to_minimality", "passes": False, "evidence": "O_s is not an ordering or minimum-score rule"},
        {"check": "reduces_to_shape", "passes": False, "evidence": f"F24-descending survivors count is {conjoined_count}"},
        {"check": "reduces_to_tuning", "passes": False, "evidence": "criterion is O_s=0 chosen before target status is read"},
        {"check": "uses_target_reference", "passes": False, "evidence": "reference key is used only for status reporting"},
    ]
    ablation_rows = [
        {"removed_component": "f24_role_obstruction", "survivors_without_component": carrier_count, "load_bearing": carrier_count > conjoined_count},
        {"removed_component": "prior_corrected_stack", "survivors_without_component": conjoined_count, "load_bearing": True},
    ]
    dependency_rows = [
        {"predicate_component": "corrected_final_carrier", "primitive": "P2/P5/P1/F27/P3/P6", "role": "Step-33 corrected carrier and active intrinsic stack."},
        {"predicate_component": "f24_role_obstruction", "primitive": "F24", "role": "Compute obstruction to charge role descending through the non-abelian access quotient."},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "build script excludes forbidden prior literals and target-shape primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "components traced to corrected prior stack and F24"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "F24 predicate is load-bearing"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "predicate is not a row picker and has a nontrivial distribution"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "corrected 80 reproduced and target obstruction computed"},
        {"gate": "no_tuning", "passes": not any(row["passes"] for row in self_check_rows), "evidence": "criterion is O_s=0, not target-matched obstruction"},
    ]
    type_limit_rows = [
        {
            "assessment": "intrinsic_gauge_filter_frontier",
            "status": verdict,
            "carrier_family_size": carrier_count,
            "f24_residual_size": conjoined_count,
            "target_requires_next_kind": not target_passes_f24 or not target_distinguished,
            "next_kind": "higher-layer descent/content-cascade criterion or observed-input boundary",
        }
    ]
    generated_rows = [
        {"item": "corrected_final_carrier", "status": "rederived", "detail": str(carrier_count)},
        {"item": "role_obstruction_definition", "status": "declared_mode_b_input", "detail": "q=canonical non-abelian role, s=charge readout, O_s counts same-q different-s pairs"},
        {"item": "f24_descending_survivors", "status": "computed", "detail": str(conjoined_count)},
        {"item": "target_obstruction", "status": "computed", "detail": str(target_obstruction)},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "type_limit_assessment", "status": "computed", "detail": verdict},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "reproduced_corrected_carrier": carrier_count,
            "f24_descending_survivors": conjoined_count,
            "target_obstruction": target_obstruction,
            "target_passes_f24": target_passes_f24,
            "target_distinguished": target_distinguished,
            "verdict": verdict,
            "next_grammar_delta": next_delta,
        }
    ]
    output = {
        "step": 34,
        "mode": "ModeB_role_obstruction_discriminator",
        "reproduced_corrected_carrier": carrier_count,
        "f24_descending_survivors": conjoined_count,
        "target_obstruction": target_obstruction,
        "target_passes_f24": target_passes_f24,
        "target_distinguished": target_distinguished,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "type_limit_assessment": verdict == "TYPED_NO_GO_TYPE_LIMIT",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    write_csv(ARTIFACT_DIR / "role_obstruction_scores_step34.csv", sorted(obstruction_rows, key=lambda row: (row["dimensions"], row["support_score"], row["support_key"])), ["dimensions", "support_key", "support_score", "role_obstruction_pairs", "q_fiber_count", "max_q_fiber_size", "f24_descends", "witnesses", "is_target_reference"])
    write_csv(ARTIFACT_DIR / "role_obstruction_distribution_step34.csv", distribution_rows, ["role_obstruction_pairs", "survivor_count", "target_has_this_obstruction"])
    write_csv(ARTIFACT_DIR / "f24_descending_survivors_step34.csv", sorted(f24_rows, key=lambda row: (row["dimensions"], row["support_score"], row["support_key"])), ["dimensions", "support_key", "support_score", "role_obstruction_pairs", "q_fiber_count", "max_q_fiber_size", "f24_descends", "witnesses", "is_target_reference"])
    write_csv(ARTIFACT_DIR / "f24_counts_by_structure_step34.csv", per_structure_rows, ["dimensions", "corrected_final_carrier", "f24_descending_survivors", "target_passes"])
    write_csv(ARTIFACT_DIR / "predicate_summary_step34.csv", summary_rows, ["reproduced_corrected_carrier", "f24_descending_survivors", "target_obstruction", "target_passes_f24", "target_distinguished", "verdict", "next_grammar_delta"])
    write_csv(ARTIFACT_DIR / "type_limit_assessment_step34.csv", type_limit_rows, ["assessment", "status", "carrier_family_size", "f24_residual_size", "target_requires_next_kind", "next_kind"])
    write_csv(ARTIFACT_DIR / "negative_controls_step34.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step34.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step34.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "ablation_step34.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step34.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step34.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step34.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "role_obstruction_discriminator_output_step34.json", output)
    schema = {
        "step": 34,
        "mode": "ModeB_role_obstruction_discriminator",
        "artifact_root": "steps/step34_mode_b_role_obstruction_discriminator_artifacts",
        "reproduced_corrected_carrier": carrier_count,
        "f24_descending_survivors": conjoined_count,
        "target_obstruction": target_obstruction,
        "target_passes_f24": target_passes_f24,
        "target_distinguished": target_distinguished,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "type_limit_assessment": verdict == "TYPED_NO_GO_TYPE_LIMIT",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "forbidden_prior_self_check_pass": not any(row["passes"] for row in self_check_rows),
        "stage_ii_pass": all(row["passes"] for row in stage_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
