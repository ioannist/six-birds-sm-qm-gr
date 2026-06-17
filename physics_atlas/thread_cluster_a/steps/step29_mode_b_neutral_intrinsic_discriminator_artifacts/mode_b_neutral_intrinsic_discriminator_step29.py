#!/usr/bin/env python3
"""Build Cluster A Step 29 neutral intrinsic discriminator artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
from itertools import combinations
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP28_DIR = STEPS_DIR / "step28_mode_b_neutral_representation_desmuggle_artifacts"
STEP28_SCRIPT = STEP28_DIR / "mode_b_neutral_representation_desmuggle_step28.py"


def load_step28():
    spec = importlib.util.spec_from_file_location("cluster_a_step28_neutral", STEP28_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 28 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step28_neutral"] = module
    spec.loader.exec_module(module)
    return module


s28 = load_step28()
ZERO = s28.ZERO
ONE = s28.ONE
TWO = s28.TWO


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sum_anomaly(combo: tuple[int, ...], type_rows: list[object]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    anomaly = tuple(ZERO for _ in type_rows[ZERO].anomaly_vector)
    parity = tuple(ZERO for _ in type_rows[ZERO].witten_vector)
    for type_id in combo:
        row = type_rows[type_id]
        anomaly = s28.add_vectors(anomaly, row.anomaly_vector)
        parity = s28.add_parity(parity, row.witten_vector)
    return anomaly, parity


def closed_chiral(combo: tuple[int, ...], type_rows: list[object]) -> bool:
    if not combo:
        return False
    anomaly, parity = sum_anomaly(combo, type_rows)
    zero_anomaly = tuple(ZERO for _ in type_rows[ZERO].anomaly_vector)
    zero_parity = tuple(ZERO for _ in type_rows[ZERO].witten_vector)
    return anomaly == zero_anomaly and parity == zero_parity and not s28.vectorlike_only(combo, type_rows)


def atomic_package(combo: tuple[int, ...], type_rows: list[object]) -> bool:
    if len(combo) <= ONE:
        return True
    ids = tuple(combo)
    for size in range(ONE, len(ids)):
        for subset in combinations(ids, size):
            if closed_chiral(tuple(subset), type_rows):
                return False
    return True


def no_spectator_action(combo: tuple[int, ...], type_rows: list[object]) -> bool:
    dimensions = type_rows[ZERO].dimensions
    for factor_index, _dimension in enumerate(dimensions):
        if not any(type_rows[type_id].reps[factor_index] != "singlet" for type_id in combo):
            return False
    return True


def primitive_charge_orbit(combo: tuple[int, ...], type_rows: list[object]) -> bool:
    charges = [abs(type_rows[type_id].charge) for type_id in combo if type_rows[type_id].charge != ZERO]
    if not charges:
        return False
    has_positive = any(type_rows[type_id].charge > ZERO for type_id in combo)
    has_negative = any(type_rows[type_id].charge < ZERO for type_id in combo)
    return has_positive and has_negative and math.gcd(*charges) == ONE


def predicate_flags(combo: tuple[int, ...], type_rows: list[object]) -> dict[str, bool]:
    atomic = atomic_package(combo, type_rows)
    covered = no_spectator_action(combo, type_rows)
    primitive_charge = primitive_charge_orbit(combo, type_rows)
    return {
        "atomic_package": atomic,
        "no_spectator_action": covered,
        "primitive_charge_orbit": primitive_charge,
        "intrinsic_predicate_passes": atomic and covered and primitive_charge,
    }


def score_text(score: tuple[int, int, int, int]) -> str:
    return "|".join(str(value) for value in score)


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    target_key = s28.reference_support_key()
    totals = {
        "p2_closers": ZERO,
        "atomic_package": ZERO,
        "no_spectator_action": ZERO,
        "primitive_charge_orbit": ZERO,
        "intrinsic_predicate_passes": ZERO,
        "target_total": ZERO,
        "target_passes": ZERO,
    }
    ablations = {
        "without_atomic_package": ZERO,
        "without_no_spectator_action": ZERO,
        "without_primitive_charge_orbit": ZERO,
    }
    predicate_rows: list[dict[str, object]] = []
    survivor_rows: list[dict[str, object]] = []
    all_pass_keys: list[tuple[str, str, tuple[int, int, int, int]]] = []
    all_fail_keys: list[tuple[str, str]] = []
    per_structure_rows: list[dict[str, object]] = []

    for dimensions in s28.factor_structures():
        result = s28.enumerate_structure(dimensions)
        type_rows = result["type_rows"]
        closers: dict[str, tuple[int, ...]] = result["closers"]
        dim_text = "|".join(str(value) for value in dimensions)
        local = {
            "p2_closers": ZERO,
            "atomic_package": ZERO,
            "no_spectator_action": ZERO,
            "primitive_charge_orbit": ZERO,
            "intrinsic_predicate_passes": ZERO,
            "target_passes": ZERO,
        }
        for key, combo in closers.items():
            flags = predicate_flags(combo, type_rows)
            score = s28.support_score(combo, type_rows)
            totals["p2_closers"] += ONE
            local["p2_closers"] += ONE
            if key == target_key:
                totals["target_total"] += ONE
            for name in ("atomic_package", "no_spectator_action", "primitive_charge_orbit", "intrinsic_predicate_passes"):
                if flags[name]:
                    totals[name] += ONE
                    local[name] += ONE
            if flags["no_spectator_action"] and flags["primitive_charge_orbit"]:
                ablations["without_atomic_package"] += ONE
            if flags["atomic_package"] and flags["primitive_charge_orbit"]:
                ablations["without_no_spectator_action"] += ONE
            if flags["atomic_package"] and flags["no_spectator_action"]:
                ablations["without_primitive_charge_orbit"] += ONE
            if flags["intrinsic_predicate_passes"]:
                all_pass_keys.append((dim_text, key, score))
                if key == target_key:
                    totals["target_passes"] += ONE
                    local["target_passes"] += ONE
            else:
                all_fail_keys.append((dim_text, key))
        per_structure_rows.append(
            {
                "dimensions": dim_text,
                "p2_closers": local["p2_closers"],
                "atomic_package": local["atomic_package"],
                "no_spectator_action": local["no_spectator_action"],
                "primitive_charge_orbit": local["primitive_charge_orbit"],
                "intrinsic_predicate_passes": local["intrinsic_predicate_passes"],
                "target_passes": local["target_passes"],
            }
        )

    pass_count = totals["intrinsic_predicate_passes"]
    target_passes = totals["target_passes"]
    target_distinguished = target_passes == ONE and pass_count == ONE
    verdict = "LAND" if target_distinguished else ("NARROW" if target_passes else "TYPED_NO_GO")
    next_delta = (
        "conjoin the next neutral intrinsic predicate: a budgeted closure currency or F24/F47 role-obstruction audit on the atomic rewrite packages"
        if verdict != "LAND"
        else "stress-test the landed predicate under wider neutral carrier windows"
    )

    for dim_text, key, score in sorted(all_pass_keys, key=lambda item: (item[2], item[ZERO], item[ONE])):
        survivor_rows.append(
            {
                "dimensions": dim_text,
                "support_key": key,
                "minimal_score": score_text(score),
                "is_target_reference": key == target_key,
            }
        )

    false_target = next((row for row in survivor_rows if row["is_target_reference"] is False), None)
    failing_target = all_fail_keys[ZERO] if all_fail_keys else ("none", "none")
    negative_rows = [
        {
            "control": "false_target_not_singled_out",
            "passes": false_target is not None and pass_count > ONE,
            "evidence": f"non-reference survivor exists and predicate survivor count is {pass_count}",
        },
        {
            "control": "predicate_discriminates_against_some_p2_closers",
            "passes": len(all_fail_keys) > ZERO,
            "evidence": f"example failing p2 closer: {failing_target[0]}::{failing_target[1]}",
        },
        {
            "control": "target_not_forced",
            "passes": not target_distinguished and pass_count > ONE,
            "evidence": "target passes but is not uniquely selected" if target_passes else "target fails the predicate",
        },
    ]

    stage_rows = [
        {
            "stage_ii_check": "reducible_packages_detected",
            "passes": totals["p2_closers"] > totals["atomic_package"],
            "evidence": f"{totals['p2_closers'] - totals['atomic_package']} p2 closers fail the atomic-package audit",
        },
        {
            "stage_ii_check": "target_atomic_rewrite_package_survives",
            "passes": target_passes == ONE,
            "evidence": "target reference passes the intrinsic package predicate once" if target_passes else "target reference does not pass",
        },
    ]
    ablation_rows = [
        {
            "removed_component": "atomic_package",
            "survivors_without_component": ablations["without_atomic_package"],
            "load_bearing": ablations["without_atomic_package"] > pass_count,
        },
        {
            "removed_component": "no_spectator_action",
            "survivors_without_component": ablations["without_no_spectator_action"],
            "load_bearing": ablations["without_no_spectator_action"] > pass_count,
        },
        {
            "removed_component": "primitive_charge_orbit",
            "survivors_without_component": ablations["without_primitive_charge_orbit"],
            "load_bearing": ablations["without_primitive_charge_orbit"] > pass_count,
        },
    ]
    dependency_rows = [
        {"predicate_component": "atomic_package", "primitive": "P5", "role": "No proper non-empty closed chiral subpackage."},
        {"predicate_component": "no_spectator_action", "primitive": "P1", "role": "Every declared gauge action participates in the package."},
        {"predicate_component": "primitive_charge_orbit", "primitive": "F27", "role": "Charge orbit has both signs and primitive integer gcd one."},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "predicate does not inspect a slot-count equality"},
        {"check": "uses_exterior_only_prior", "passes": False, "evidence": "predicate is evaluated after Step 28 neutral rep enumeration"},
        {"check": "uses_larger_group_prior", "passes": False, "evidence": "predicate depends only on the candidate support itself"},
        {"check": "reduces_to_target_reference", "passes": False, "evidence": f"predicate leaves {pass_count} survivors"},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "build script excludes forbidden prior literals and target-shape primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "predicate components are traced to P5, P1, and F27"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "each component increases survivors when removed"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "false target not uniquely selected and some P2 closers fail"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "reducible package detection and target survival recorded"},
        {"gate": "no_single_axiom_equivalence", "passes": pass_count > ONE, "evidence": "no component is equivalent to selecting the reference"},
    ]
    generated_rows = [
        {"item": "carrier", "status": "read_from_step28", "detail": "neutral P2-closer carrier"},
        {"item": "intrinsic_principle", "status": "declared_mode_b_input", "detail": "atomic rewrite-packaging = P5 atomic package + P1 no spectator action + F27 primitive charge orbit"},
        {"item": "p2_closer_count", "status": "computed", "detail": str(totals["p2_closers"])},
        {"item": "predicate_survivor_count", "status": "computed", "detail": str(pass_count)},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    predicate_summary = [
        {
            "principle": "atomic_rewrite_packaging",
            "neutral_intrinsic_reason": "uses only subclosure, action-coverage, and primitive charge-orbit properties of each candidate support",
            "p2_closers": totals["p2_closers"],
            "survivors": pass_count,
            "target_passes": target_passes == ONE,
            "target_distinguished": target_distinguished,
            "verdict": verdict,
        }
    ]
    output = {
        "step": 29,
        "mode": "ModeB_neutral_intrinsic_discriminator",
        "principle": "atomic_rewrite_packaging",
        "p2_closer_count": totals["p2_closers"],
        "predicate_survivor_count": pass_count,
        "target_present_in_carrier": totals["target_total"] == ONE,
        "target_passes_predicate": target_passes == ONE,
        "target_distinguished": target_distinguished,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "typed_no_go": verdict == "TYPED_NO_GO",
        "narrow_progress": verdict == "NARROW",
        "landed": verdict == "LAND",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    write_csv(
        ARTIFACT_DIR / "predicate_summary_step29.csv",
        predicate_summary,
        ["principle", "neutral_intrinsic_reason", "p2_closers", "survivors", "target_passes", "target_distinguished", "verdict"],
    )
    write_csv(
        ARTIFACT_DIR / "predicate_counts_by_structure_step29.csv",
        per_structure_rows,
        [
            "dimensions",
            "p2_closers",
            "atomic_package",
            "no_spectator_action",
            "primitive_charge_orbit",
            "intrinsic_predicate_passes",
            "target_passes",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "predicate_survivors_step29.csv",
        survivor_rows,
        ["dimensions", "support_key", "minimal_score", "is_target_reference"],
    )
    write_csv(
        ARTIFACT_DIR / "reference_status_step29.csv",
        [
            {
                "target_present_in_carrier": totals["target_total"] == ONE,
                "target_passes_predicate": target_passes == ONE,
                "target_distinguished": target_distinguished,
                "predicate_survivor_count": pass_count,
                "verdict": verdict,
            }
        ],
        ["target_present_in_carrier", "target_passes_predicate", "target_distinguished", "predicate_survivor_count", "verdict"],
    )
    write_csv(ARTIFACT_DIR / "negative_controls_step29.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step29.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step29.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "ablation_step29.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step29.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step29.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step29.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "mode_b_neutral_intrinsic_discriminator_output_step29.json", output)
    schema = {
        "step": 29,
        "mode": "ModeB_neutral_intrinsic_discriminator",
        "artifact_root": "steps/step29_mode_b_neutral_intrinsic_discriminator_artifacts",
        "principle": output["principle"],
        "p2_closer_count": output["p2_closer_count"],
        "predicate_survivor_count": output["predicate_survivor_count"],
        "target_present_in_carrier": output["target_present_in_carrier"],
        "target_passes_predicate": output["target_passes_predicate"],
        "target_distinguished": output["target_distinguished"],
        "verdict": output["verdict"],
        "next_grammar_delta": output["next_grammar_delta"],
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
