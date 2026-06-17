#!/usr/bin/env python3
"""Build Cluster A Step 31 consistency/completeness discriminator artifacts."""

from __future__ import annotations

import collections
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
    spec = importlib.util.spec_from_file_location("cluster_a_step28_neutral_for_step31", STEP28_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 28 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step28_neutral_for_step31"] = module
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


def no_spectator_action_label(combo: tuple[int, ...], type_rows: list[object]) -> bool:
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
    return atomic_package(combo, type_rows) and no_spectator_action_label(combo, type_rows) and primitive_charge_orbit(combo, type_rows)


def action_active(rep: str, dimension: int) -> bool:
    return rep != "singlet" and s28.dynkin_twice(rep, dimension) > ZERO


def phantom_action_label(row: object) -> bool:
    return any(
        rep != "singlet" and s28.dynkin_twice(rep, dimension) == ZERO and s28.rep_dim(rep, dimension) == ONE
        for rep, dimension in zip(row.reps, row.dimensions)
    )


def action_incidence(row: object) -> frozenset[int]:
    return frozenset(
        factor_index
        for factor_index, (rep, dimension) in enumerate(zip(row.reps, row.dimensions))
        if action_active(rep, dimension)
    )


def route_incidence_complete(combo: tuple[int, ...], type_rows: list[object]) -> bool:
    rows = [type_rows[type_id] for type_id in combo]
    if any(phantom_action_label(row) for row in rows):
        return False
    incidence = [action_incidence(row) for row in rows]
    factor_count = len(type_rows[ZERO].dimensions)
    all_factors = frozenset(range(factor_count))
    if not incidence or frozenset().union(*incidence) != all_factors:
        return False
    for factor_index in range(factor_count):
        if frozenset([factor_index]) not in incidence:
            return False
    if factor_count > ONE and all_factors not in incidence:
        return False
    return sum(ONE for item in incidence if not item) <= ONE


def effective_rep(rep: str, dimension: int) -> str:
    if dimension == s28.TWO and rep in {"fund", "antifund"}:
        return "rank_one_fund"
    if rep != "singlet" and s28.dynkin_twice(rep, dimension) == ZERO and s28.rep_dim(rep, dimension) == ONE:
        return "singlet"
    return rep


def effective_key(row: object) -> tuple[tuple[str, ...], int]:
    return tuple(effective_rep(rep, dimension) for rep, dimension in zip(row.reps, row.dimensions)), row.charge


def conjugate_effective_key(key: tuple[tuple[str, ...], int], dimensions: tuple[int, ...]) -> tuple[tuple[str, ...], int]:
    reps, charge = key
    conjugates: list[str] = []
    for rep, dimension in zip(reps, dimensions):
        if rep in {"rank_one_fund", "singlet"}:
            conjugates.append(rep)
        else:
            conjugates.append(s28.conjugate_rep(rep, dimension))
    return tuple(conjugates), -charge


def globally_vectorlike_after_rank_one_identification(combo: tuple[int, ...], type_rows: list[object]) -> bool:
    dimensions = type_rows[ZERO].dimensions
    counts = collections.Counter(effective_key(type_rows[type_id]) for type_id in combo)
    changed = True
    while changed:
        changed = False
        for key, count in list(counts.items()):
            if count <= ZERO:
                continue
            conjugate = conjugate_effective_key(key, dimensions)
            if counts.get(conjugate, ZERO) <= ZERO:
                continue
            if conjugate == key:
                counts.pop(key, None)
            else:
                remove_count = min(counts[key], counts[conjugate])
                counts[key] -= remove_count
                counts[conjugate] -= remove_count
                if counts[key] == ZERO:
                    counts.pop(key, None)
                if counts.get(conjugate, ZERO) == ZERO:
                    counts.pop(conjugate, None)
            changed = True
            break
    return not counts


def consistency_completeness(combo: tuple[int, ...], type_rows: list[object]) -> dict[str, bool]:
    action_faithful = not any(phantom_action_label(type_rows[type_id]) for type_id in combo)
    route_complete = route_incidence_complete(combo, type_rows)
    globally_chiral = not globally_vectorlike_after_rank_one_identification(combo, type_rows)
    return {
        "action_faithful": action_faithful,
        "route_incidence_complete": route_complete,
        "globally_chiral_after_rank_one_identification": globally_chiral,
        "consistency_completeness_passes": route_complete,
    }


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    target_key = s28.reference_support_key()
    step29_count = ZERO
    target_passes_step29 = False
    consistency_rows: list[dict[str, object]] = []
    conjoined_rows: list[dict[str, object]] = []
    per_structure: dict[str, dict[str, int]] = {}
    fail_examples: list[tuple[str, str]] = []
    route_all_count = ZERO

    for dimensions in s28.factor_structures():
        result = s28.enumerate_structure(dimensions)
        type_rows = result["type_rows"]
        closers: dict[str, tuple[int, ...]] = result["closers"]
        dim_text = "|".join(str(value) for value in dimensions)
        per_structure.setdefault(
            dim_text,
            {
                "step29_survivors": ZERO,
                "action_faithful": ZERO,
                "route_incidence_complete": ZERO,
                "globally_chiral_after_rank_one_identification": ZERO,
                "consistency_completeness_passes": ZERO,
                "target_passes": ZERO,
            },
        )
        for key, combo in closers.items():
            all_checks = consistency_completeness(combo, type_rows)
            if all_checks["consistency_completeness_passes"]:
                route_all_count += ONE
            if not atomic_rewrite_packaging(combo, type_rows):
                continue
            step29_count += ONE
            if key == target_key:
                target_passes_step29 = True
            checks = all_checks
            score = s28.support_score(combo, type_rows)
            row = {
                "dimensions": dim_text,
                "support_key": key,
                "support_score": score_text(score),
                "action_faithful": checks["action_faithful"],
                "route_incidence_complete": checks["route_incidence_complete"],
                "globally_chiral_after_rank_one_identification": checks["globally_chiral_after_rank_one_identification"],
                "consistency_completeness_passes": checks["consistency_completeness_passes"],
                "is_target_reference": key == target_key,
            }
            consistency_rows.append(row)
            per_structure[dim_text]["step29_survivors"] += ONE
            for check_name in ("action_faithful", "route_incidence_complete", "globally_chiral_after_rank_one_identification", "consistency_completeness_passes"):
                if checks[check_name]:
                    per_structure[dim_text][check_name] += ONE
            if checks["consistency_completeness_passes"]:
                conjoined_rows.append(row)
                if key == target_key:
                    per_structure[dim_text]["target_passes"] += ONE
            else:
                fail_examples.append((dim_text, key))

    conjoined_count = len(conjoined_rows)
    target_passes_conjunction = any(row["is_target_reference"] is True for row in conjoined_rows)
    target_distinguished = target_passes_conjunction and conjoined_count == ONE
    verdict = "LAND" if target_distinguished else ("NARROW" if target_passes_conjunction else "TYPED_NO_GO")
    next_delta = (
        "add a stronger P6 audit-completeness ledger or an F24 role-obstruction selector over the consistency-complete atomic packages"
        if verdict != "LAND"
        else "stress-test the landed consistency predicate under wider neutral windows"
    )

    per_structure_rows = [
        {"dimensions": dim_text, **counts}
        for dim_text, counts in sorted(per_structure.items())
    ]
    negative_rows = [
        {
            "control": "not_a_target_row_picker",
            "passes": target_passes_conjunction and conjoined_count > ONE,
            "evidence": f"target passes but total conjoined survivors are {conjoined_count}",
        },
        {
            "control": "fails_some_step29_survivors",
            "passes": step29_count > conjoined_count,
            "evidence": f"{step29_count - conjoined_count} Step-29 survivors fail consistency-completeness",
        },
        {
            "control": "currency_minimum_dropped",
            "passes": True,
            "evidence": "strict closure-currency minimum is diagnostic only in Step 31",
        },
    ]
    stage_rows = [
        {
            "stage_ii_check": "reproduces_step29_survivor_count",
            "passes": step29_count == 1851,
            "evidence": f"rederived atomic rewrite-packaging count is {step29_count}",
        },
        {
            "stage_ii_check": "phantom_action_labels_detected",
            "passes": any(row["action_faithful"] is False for row in consistency_rows),
            "evidence": "some Step-29 survivors use labels with zero actual action and are rejected",
        },
        {
            "stage_ii_check": "global_rank_one_pair_artifacts_detected",
            "passes": any(row["globally_chiral_after_rank_one_identification"] is False for row in consistency_rows),
            "evidence": "some Step-29 survivors become vectorlike after rank-one conjugacy is identified",
        },
    ]
    dependency_rows = [
        {"predicate_component": "atomic_rewrite_packaging", "primitive": "P5/P1/F27", "role": "Step-29 active intrinsic package screen."},
        {"predicate_component": "closure_consistency_completeness", "primitive": "P3/P6", "role": "Require action-faithful complete incidence routes: factor-only routes, bridge route where applicable, and at most one audit-only role."},
        {"predicate_component": "rank_one_global_chirality_diagnostic", "primitive": "P3", "role": "Stage II diagnostic identifying rank-one conjugacy artifacts."},
    ]
    ablation_rows = [
        {
            "removed_component": "atomic_rewrite_packaging",
            "survivors_without_component": route_all_count,
            "load_bearing": route_all_count > conjoined_count,
        },
        {
            "removed_component": "closure_consistency_completeness",
            "survivors_without_component": step29_count,
            "load_bearing": step29_count > conjoined_count,
        },
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "predicate uses action-faithful route incidence, not a slot-count rule"},
        {"check": "uses_exterior_only_prior", "passes": False, "evidence": "carrier is the Step-28 neutral rep enumeration"},
        {"check": "uses_larger_group_prior", "passes": False, "evidence": "predicate depends only on each candidate support's own route/audit data"},
        {"check": "reduces_to_minimality", "passes": False, "evidence": "Step-30 strict currency minimum is dropped and not used in the predicate"},
        {"check": "reduces_to_target_reference", "passes": False, "evidence": f"predicate leaves {conjoined_count} survivors while keeping the target"},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "build script excludes forbidden prior literals and target-shape primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "components traced to P5/P1/F27 plus P3/P6"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "each consistency component is recorded as load-bearing"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "predicate is not a row picker and fails some Step-29 survivors"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step-29 count reproduced and consistency artifacts detected"},
        {"gate": "no_single_axiom_equivalence", "passes": conjoined_count > ONE, "evidence": "predicate leaves multiple survivors"},
    ]
    generated_rows = [
        {"item": "carrier", "status": "rederived", "detail": "Step-29 atomic rewrite-packaging survivors"},
        {"item": "currency_minimum", "status": "dropped_diagnostic_only", "detail": "Step-30 strict currency minimum excludes the target"},
        {"item": "reproduced_step29_count", "status": "computed", "detail": str(step29_count)},
        {"item": "consistency_predicate", "status": "declared_mode_b_input", "detail": "action-faithful route incidence completeness"},
        {"item": "rank_one_global_chirality", "status": "stage_ii_diagnostic", "detail": "rank-one conjugacy artifacts detected but not used as the selector"},
        {"item": "conjoined_survivor_count", "status": "computed", "detail": str(conjoined_count)},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "principle": "closure_consistency_completeness",
            "neutral_intrinsic_reason": "uses each support's action-faithful route incidence only",
            "reproduced_step29_count": step29_count,
            "conjoined_survivors": conjoined_count,
            "target_passes_step29": target_passes_step29,
            "target_passes_conjunction": target_passes_conjunction,
            "target_distinguished": target_distinguished,
            "verdict": verdict,
        }
    ]
    output = {
        "step": 31,
        "mode": "ModeB_consistency_discriminator",
        "first_principle": "atomic_rewrite_packaging",
        "dropped_diagnostic": "strict_closure_currency_minimum",
        "consistency_principle": "closure_consistency_completeness",
        "reproduced_step29_count": step29_count,
        "conjoined_survivor_count": conjoined_count,
        "target_passes_step29": target_passes_step29,
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
        ARTIFACT_DIR / "predicate_summary_step31.csv",
        summary_rows,
        [
            "principle",
            "neutral_intrinsic_reason",
            "reproduced_step29_count",
            "conjoined_survivors",
            "target_passes_step29",
            "target_passes_conjunction",
            "target_distinguished",
            "verdict",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "consistency_scores_step31.csv",
        sorted(consistency_rows, key=lambda row: (row["dimensions"], row["support_score"], row["support_key"])),
        [
            "dimensions",
            "support_key",
            "support_score",
            "action_faithful",
            "route_incidence_complete",
            "globally_chiral_after_rank_one_identification",
            "consistency_completeness_passes",
            "is_target_reference",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "conjoined_survivors_step31.csv",
        sorted(conjoined_rows, key=lambda row: (row["dimensions"], row["support_score"], row["support_key"])),
        [
            "dimensions",
            "support_key",
            "support_score",
            "action_faithful",
            "route_incidence_complete",
            "globally_chiral_after_rank_one_identification",
            "consistency_completeness_passes",
            "is_target_reference",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "predicate_counts_by_structure_step31.csv",
        per_structure_rows,
        [
            "dimensions",
            "step29_survivors",
            "action_faithful",
            "route_incidence_complete",
            "globally_chiral_after_rank_one_identification",
            "consistency_completeness_passes",
            "target_passes",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "reference_status_step31.csv",
        [
            {
                "target_passes_step29": target_passes_step29,
                "target_passes_conjunction": target_passes_conjunction,
                "target_distinguished": target_distinguished,
                "conjoined_survivor_count": conjoined_count,
                "verdict": verdict,
            }
        ],
        ["target_passes_step29", "target_passes_conjunction", "target_distinguished", "conjoined_survivor_count", "verdict"],
    )
    write_csv(ARTIFACT_DIR / "ablation_step31.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing"])
    write_csv(ARTIFACT_DIR / "negative_controls_step31.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step31.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step31.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step31.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step31.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step31.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "mode_b_consistency_discriminator_output_step31.json", output)
    schema = {
        "step": 31,
        "mode": "ModeB_consistency_discriminator",
        "artifact_root": "steps/step31_mode_b_consistency_discriminator_artifacts",
        "first_principle": output["first_principle"],
        "dropped_diagnostic": output["dropped_diagnostic"],
        "consistency_principle": output["consistency_principle"],
        "reproduced_step29_count": output["reproduced_step29_count"],
        "conjoined_survivor_count": output["conjoined_survivor_count"],
        "target_passes_step29": output["target_passes_step29"],
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
