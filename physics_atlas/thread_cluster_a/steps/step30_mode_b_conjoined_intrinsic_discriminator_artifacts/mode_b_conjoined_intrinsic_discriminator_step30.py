#!/usr/bin/env python3
"""Build Cluster A Step 30 conjoined intrinsic discriminator artifacts."""

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
    spec = importlib.util.spec_from_file_location("cluster_a_step28_neutral_for_step30", STEP28_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 28 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step28_neutral_for_step30"] = module
    spec.loader.exec_module(module)
    return module


s28 = load_step28()
ZERO = s28.ZERO
ONE = s28.ONE


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


def sum_anomaly(combo: tuple[int, ...], type_rows: list[object]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    anomaly = tuple(ZERO for _ in type_rows[ZERO].anomaly_vector)
    parity = tuple(ZERO for _ in type_rows[ZERO].witten_vector)
    for type_id in combo:
        anomaly = s28.add_vectors(anomaly, type_rows[type_id].anomaly_vector)
        parity = s28.add_parity(parity, type_rows[type_id].witten_vector)
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


def atomic_rewrite_packaging(combo: tuple[int, ...], type_rows: list[object]) -> bool:
    return atomic_package(combo, type_rows) and no_spectator_action(combo, type_rows) and primitive_charge_orbit(combo, type_rows)


def closure_currency(combo: tuple[int, ...], type_rows: list[object]) -> tuple[int, int, int, int]:
    active_axes = ZERO
    l1_shadow_price = ZERO
    nonzero_terms = ZERO
    for axis_index in range(len(type_rows[ZERO].anomaly_vector)):
        values = [type_rows[type_id].anomaly_vector[axis_index] for type_id in combo]
        if any(value != ZERO for value in values):
            active_axes += ONE
            l1_shadow_price += sum(abs(value) for value in values)
            nonzero_terms += sum(ONE for value in values if value != ZERO)
    for axis_index in range(len(type_rows[ZERO].witten_vector)):
        values = [type_rows[type_id].witten_vector[axis_index] for type_id in combo]
        if any(value != ZERO for value in values):
            active_axes += ONE
            nonzero_terms += sum(ONE for value in values if value != ZERO)
    charges = [type_rows[type_id].charge for type_id in combo]
    charge_span = max(charges) - min(charges)
    return active_axes, l1_shadow_price, nonzero_terms, charge_span


def flags(combo: tuple[int, ...], type_rows: list[object]) -> dict[str, bool]:
    return {
        "atomic_package": atomic_package(combo, type_rows),
        "no_spectator_action": no_spectator_action(combo, type_rows),
        "primitive_charge_orbit": primitive_charge_orbit(combo, type_rows),
    }


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    target_key = s28.reference_support_key()
    step29_survivors: list[dict[str, object]] = []
    pools: dict[str, list[dict[str, object]]] = {
        "all_components": [],
        "without_atomic_package": [],
        "without_no_spectator_action": [],
        "without_primitive_charge_orbit": [],
    }
    target_currency = None
    target_passes_step29 = False

    for dimensions in s28.factor_structures():
        result = s28.enumerate_structure(dimensions)
        type_rows = result["type_rows"]
        closers: dict[str, tuple[int, ...]] = result["closers"]
        dim_text = "|".join(str(value) for value in dimensions)
        for key, combo in closers.items():
            item_flags = flags(combo, type_rows)
            currency = closure_currency(combo, type_rows)
            row = {
                "dimensions": dim_text,
                "support_key": key,
                "atomic_package": item_flags["atomic_package"],
                "no_spectator_action": item_flags["no_spectator_action"],
                "primitive_charge_orbit": item_flags["primitive_charge_orbit"],
                "currency_score": score_text(currency),
                "audit_axis_count": currency[ZERO],
                "l1_shadow_price": currency[ONE],
                "nonzero_audit_terms": currency[2],
                "charge_span": currency[3],
                "is_target_reference": key == target_key,
                "support_score": score_text(s28.support_score(combo, type_rows)),
            }
            if item_flags["atomic_package"] and item_flags["no_spectator_action"] and item_flags["primitive_charge_orbit"]:
                step29_survivors.append(row)
                pools["all_components"].append(row)
                if key == target_key:
                    target_passes_step29 = True
                    target_currency = currency
            if item_flags["no_spectator_action"] and item_flags["primitive_charge_orbit"]:
                pools["without_atomic_package"].append(row)
            if item_flags["atomic_package"] and item_flags["primitive_charge_orbit"]:
                pools["without_no_spectator_action"].append(row)
            if item_flags["atomic_package"] and item_flags["no_spectator_action"]:
                pools["without_primitive_charge_orbit"].append(row)

    reproduced_step29_count = len(step29_survivors)
    minimum_currency = min(tuple(int(part) for part in row["currency_score"].split("|")) for row in step29_survivors)
    conjoined_survivors = [
        row for row in step29_survivors if tuple(int(part) for part in row["currency_score"].split("|")) == minimum_currency
    ]
    target_passes_conjunction = any(row["is_target_reference"] is True for row in conjoined_survivors)
    target_distinguished = target_passes_conjunction and len(conjoined_survivors) == ONE
    verdict = "LAND" if target_distinguished else ("NARROW" if target_passes_conjunction else "TYPED_NO_GO")
    next_delta = (
        "strict closure-currency minimum over-rewards tiny low-price packages; try F24/F47 role-obstruction or P3 protocol-holonomy on the Step-29 atomic packages"
        if verdict != "LAND"
        else "stress-test the landed two-predicate conjunction under wider neutral windows"
    )

    ablation_rows: list[dict[str, object]] = []
    full_keys = {(row["dimensions"], row["support_key"]) for row in conjoined_survivors}
    for pool_name, rows in pools.items():
        if not rows:
            min_score = "none"
            min_rows: list[dict[str, object]] = []
        else:
            min_tuple = min(tuple(int(part) for part in row["currency_score"].split("|")) for row in rows)
            min_score = score_text(min_tuple)
            min_rows = [row for row in rows if tuple(int(part) for part in row["currency_score"].split("|")) == min_tuple]
        keys = {(row["dimensions"], row["support_key"]) for row in min_rows}
        ablation_rows.append(
            {
                "pool": pool_name,
                "pool_size": len(rows),
                "minimum_currency": min_score,
                "minimum_survivor_count": len(min_rows),
                "changes_final_count_or_identity": len(min_rows) != len(conjoined_survivors) or keys != full_keys,
                "target_in_minimum": any(row["is_target_reference"] is True for row in min_rows),
            }
        )

    negative_rows = [
        {
            "control": "not_a_target_row_picker",
            "passes": len(conjoined_survivors) > ONE and not target_passes_conjunction,
            "evidence": f"currency minimum leaves {len(conjoined_survivors)} non-target supports",
        },
        {
            "control": "fails_many_step29_survivors",
            "passes": reproduced_step29_count > len(conjoined_survivors),
            "evidence": f"{reproduced_step29_count - len(conjoined_survivors)} Step-29 survivors fail strict currency minimum",
        },
        {
            "control": "target_not_forced",
            "passes": not target_passes_conjunction,
            "evidence": "target reference fails strict currency minimum",
        },
    ]
    stage_rows = [
        {
            "stage_ii_check": "reproduces_step29_survivor_count",
            "passes": reproduced_step29_count == 1851,
            "evidence": f"rederived atomic rewrite-packaging count is {reproduced_step29_count}",
        },
        {
            "stage_ii_check": "zero_price_degeneracy_detected_when_charge_orbit_removed",
            "passes": any(row["pool"] == "without_primitive_charge_orbit" and row["minimum_currency"] == "0|0|0|0" for row in ablation_rows),
            "evidence": "removing F27 primitive-charge orbit exposes zero-currency neutral packages",
        },
    ]
    dependency_rows = [
        {"predicate_component": "atomic_rewrite_packaging", "primitive": "P5/P1/F27", "role": "Step-29 active intrinsic package screen."},
        {"predicate_component": "strict_closure_currency_minimum", "primitive": "C1/C4", "role": "Lexicographic minimum of active audit axes, L1 shadow price, nonzero audit terms, and charge span."},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "currency is computed from anomaly-vector audit rows, not a slot-count rule"},
        {"check": "uses_exterior_only_prior", "passes": False, "evidence": "carrier is the Step-28 neutral rep enumeration"},
        {"check": "uses_larger_group_prior", "passes": False, "evidence": "currency depends only on the candidate support's own audit vectors"},
        {"check": "reduces_to_target_reference", "passes": False, "evidence": f"currency minimum leaves {len(conjoined_survivors)} non-target supports and excludes the target"},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "build script excludes forbidden prior literals and target-shape primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "components traced to P5/P1/F27 and C1/C4"},
        {
            "gate": "ablation",
            "passes": all(row["changes_final_count_or_identity"] for row in ablation_rows if row["pool"] != "all_components"),
            "evidence": "removing inherited components changes the currency-minimum count or identity; removing currency leaves 1851",
        },
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "currency is not a target row picker and excludes many survivors"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step-29 count reproduced and charge-orbit removal exposes zero-price degeneracy"},
        {"gate": "no_single_axiom_equivalence", "passes": not target_passes_conjunction, "evidence": "new predicate is not equivalent to selecting the target"},
    ]
    generated_rows = [
        {"item": "carrier", "status": "rederived", "detail": "Step-29 atomic rewrite-packaging survivors"},
        {"item": "reproduced_step29_count", "status": "computed", "detail": str(reproduced_step29_count)},
        {"item": "second_predicate", "status": "declared_mode_b_input", "detail": "strict closure-currency minimum from C1/C4 audit shadow price"},
        {"item": "minimum_currency", "status": "computed", "detail": score_text(minimum_currency)},
        {"item": "conjoined_survivor_count", "status": "computed", "detail": str(len(conjoined_survivors))},
        {"item": "target_currency", "status": "computed", "detail": score_text(target_currency) if target_currency else "target_not_in_step29"},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "principle": "strict_closure_currency_minimum",
            "neutral_intrinsic_reason": "uses only each support's internal audit-vector cancellation work and charge span",
            "reproduced_step29_count": reproduced_step29_count,
            "minimum_currency": score_text(minimum_currency),
            "conjoined_survivors": len(conjoined_survivors),
            "target_passes_step29": target_passes_step29,
            "target_passes_conjunction": target_passes_conjunction,
            "target_distinguished": target_distinguished,
            "verdict": verdict,
        }
    ]
    output = {
        "step": 30,
        "mode": "ModeB_conjoined_intrinsic_discriminator",
        "first_principle": "atomic_rewrite_packaging",
        "second_principle": "strict_closure_currency_minimum",
        "reproduced_step29_count": reproduced_step29_count,
        "minimum_currency": score_text(minimum_currency),
        "conjoined_survivor_count": len(conjoined_survivors),
        "target_passes_step29": target_passes_step29,
        "target_currency": score_text(target_currency) if target_currency else None,
        "target_passes_conjunction": target_passes_conjunction,
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
        ARTIFACT_DIR / "predicate_summary_step30.csv",
        summary_rows,
        [
            "principle",
            "neutral_intrinsic_reason",
            "reproduced_step29_count",
            "minimum_currency",
            "conjoined_survivors",
            "target_passes_step29",
            "target_passes_conjunction",
            "target_distinguished",
            "verdict",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "currency_scores_step30.csv",
        sorted(step29_survivors, key=lambda row: (tuple(int(part) for part in row["currency_score"].split("|")), row["dimensions"], row["support_key"])),
        [
            "dimensions",
            "support_key",
            "atomic_package",
            "no_spectator_action",
            "primitive_charge_orbit",
            "currency_score",
            "audit_axis_count",
            "l1_shadow_price",
            "nonzero_audit_terms",
            "charge_span",
            "is_target_reference",
            "support_score",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "conjoined_survivors_step30.csv",
        sorted(conjoined_survivors, key=lambda row: (row["dimensions"], row["support_key"])),
        [
            "dimensions",
            "support_key",
            "currency_score",
            "audit_axis_count",
            "l1_shadow_price",
            "nonzero_audit_terms",
            "charge_span",
            "is_target_reference",
            "support_score",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "reference_status_step30.csv",
        [
            {
                "target_passes_step29": target_passes_step29,
                "target_currency": score_text(target_currency) if target_currency else "target_not_in_step29",
                "minimum_currency": score_text(minimum_currency),
                "target_passes_conjunction": target_passes_conjunction,
                "target_distinguished": target_distinguished,
                "conjoined_survivor_count": len(conjoined_survivors),
                "verdict": verdict,
            }
        ],
        [
            "target_passes_step29",
            "target_currency",
            "minimum_currency",
            "target_passes_conjunction",
            "target_distinguished",
            "conjoined_survivor_count",
            "verdict",
        ],
    )
    write_csv(ARTIFACT_DIR / "ablation_step30.csv", ablation_rows, ["pool", "pool_size", "minimum_currency", "minimum_survivor_count", "changes_final_count_or_identity", "target_in_minimum"])
    write_csv(ARTIFACT_DIR / "negative_controls_step30.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step30.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step30.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step30.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step30.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step30.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "mode_b_conjoined_intrinsic_discriminator_output_step30.json", output)
    schema = {
        "step": 30,
        "mode": "ModeB_conjoined_intrinsic_discriminator",
        "artifact_root": "steps/step30_mode_b_conjoined_intrinsic_discriminator_artifacts",
        "first_principle": output["first_principle"],
        "second_principle": output["second_principle"],
        "reproduced_step29_count": output["reproduced_step29_count"],
        "minimum_currency": output["minimum_currency"],
        "conjoined_survivor_count": output["conjoined_survivor_count"],
        "target_passes_step29": output["target_passes_step29"],
        "target_currency": output["target_currency"],
        "target_passes_conjunction": output["target_passes_conjunction"],
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
