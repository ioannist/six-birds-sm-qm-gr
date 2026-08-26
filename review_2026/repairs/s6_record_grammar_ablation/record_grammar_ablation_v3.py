#!/usr/bin/env python3
"""S6-ABLATION-3: bounded scalar-dressed, full-residual-neutral census."""

from __future__ import annotations

import hashlib
import itertools
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
V2_PATH = HERE / "record_grammar_ablation_v2.py"
V2_SHA256 = "1d7d7fdfa8f36f6168ac4273850391651252fb906ed514a8142246a2173237ac"
FERMION_ARITY_MIN = 2
FERMION_ARITY_MAX = 4
SCALAR_INSERTION_MAX = 2
TOTAL_CONSTITUENT_CAP = 6
THRESHOLDS = (1, 2, 3, 4)
COUNTING_CONVENTIONS = ("undressed_only", "dressed_inclusive")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if sha256(V2_PATH) != V2_SHA256:
    raise RuntimeError(f"v2 dependency pin mismatch: {sha256(V2_PATH)} != {V2_SHA256}")
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import record_grammar_ablation_v2 as v2  # noqa: E402


@dataclass(frozen=True)
class Lift:
    evaluation_id: str
    component_keys: tuple[str, ...]
    fermion_arity: int
    phi_insertions: int
    phidagger_insertions: int
    residual_charge: int
    residual_singlet_multiplicity: int
    uv_charge: int
    uv_singlet_multiplicity: int
    invariant_channel: int
    uv_lift: str

    @property
    def dressing(self) -> str:
        if not self.phi_insertions and not self.phidagger_insertions:
            return "undressed"
        pieces = []
        if self.phi_insertions:
            pieces.append(f"phi^{self.phi_insertions}")
        if self.phidagger_insertions:
            pieces.append(f"phi-dagger^{self.phidagger_insertions}")
        return "+".join(pieces)

    @property
    def operator_key(self) -> str:
        # Same residual operator and invariant channel: VEV insertions of the
        # branch scalar are quotient-equivalent by the declared convention.
        return "+".join(sorted(self.component_keys)) + f"::channel={self.invariant_channel}"

    @property
    def lift_key(self) -> str:
        return f"{self.operator_key}::{self.dressing}"


@dataclass(frozen=True)
class Operator:
    evaluation_id: str
    operator_key: str
    component_keys: tuple[str, ...]
    fermion_arity: int
    invariant_channel: int
    has_undressed_lift: bool
    has_dressed_lift: bool
    dressing_classes: tuple[str, ...]
    lift_count: int
    residual_charge: int
    residual_singlet_multiplicity: int

    @property
    def category(self) -> str:
        if self.has_undressed_lift and self.has_dressed_lift:
            return "undressed_with_vev_equivalent_dressing"
        if self.has_undressed_lift:
            return "undressed_only"
        return "scalar_dressed_new"


@lru_cache(maxsize=None)
def partitions(total: int, max_parts: int, ceiling: int | None = None) -> tuple[tuple[int, ...], ...]:
    if total == 0:
        return ((),)
    if max_parts == 0:
        return ()
    ceiling = total if ceiling is None else min(ceiling, total)
    rows = []
    for first in range(ceiling, 0, -1):
        for tail in partitions(total - first, max_parts - 1, first):
            rows.append((first,) + tail)
    return tuple(rows)


def canonical_su_partition(partition: tuple[int, ...], n: int) -> tuple[int, ...]:
    padded = partition + (0,) * (n - len(partition))
    determinant_columns = padded[n - 1]
    reduced = tuple(value - determinant_columns for value in padded)
    while reduced and reduced[-1] == 0:
        reduced = reduced[:-1]
    return reduced


@lru_cache(maxsize=None)
def tensor_product(left: tuple[int, ...], right: tuple[int, ...], n: int) -> tuple[tuple[tuple[int, ...], int], ...]:
    total = sum(left) + sum(right)
    result: Counter[tuple[int, ...]] = Counter()
    for target in partitions(total, n):
        coefficient = v2.v3.littlewood_richardson_coefficient(left, right, target)
        if coefficient:
            result[canonical_su_partition(target, n)] += coefficient
    return tuple(sorted(result.items()))


@lru_cache(maxsize=None)
def exact_singlet_multiplicity(reps: tuple[str, ...], n: int) -> int:
    states: Counter[tuple[int, ...]] = Counter({(): 1})
    for rep in reps:
        canonical = v2.rm.canonical_rep(rep, n)
        partition = tuple(v2.v3.REP_TABLE[n][canonical]["partition"])
        updated: Counter[tuple[int, ...]] = Counter()
        for left, left_multiplicity in states.items():
            for target, coefficient in tensor_product(left, partition, n):
                updated[target] += left_multiplicity * coefficient
        states = updated
    return states[()]


def conjugate_scalar_reps(branch: Any) -> tuple[str, ...]:
    scalar = branch.representative
    return tuple(v2.rm.conjugate_rep(rep, n) for rep, n in zip(scalar.reps, scalar.dimensions))


def dressing_options() -> tuple[tuple[int, int], ...]:
    return tuple((phi, dagger)
                 for total in range(SCALAR_INSERTION_MAX + 1)
                 for phi in range(total + 1)
                 for dagger in (total - phi,))


def uv_multiplicity(fields: list[Any], parent_members: tuple[int, ...], branch: Any,
                    phi_count: int, dagger_count: int) -> tuple[int, int]:
    scalar = branch.representative
    dagger_reps = conjugate_scalar_reps(branch)
    total_charge = (sum(fields[index].charge for index in parent_members)
                    + phi_count * scalar.charge - dagger_count * scalar.charge)
    if total_charge:
        return 0, total_charge
    multiplicity = 1
    for factor_index, n in enumerate(scalar.dimensions):
        reps = tuple(fields[index].reps[factor_index] for index in parent_members)
        reps += (scalar.reps[factor_index],) * phi_count
        reps += (dagger_reps[factor_index],) * dagger_count
        multiplicity *= exact_singlet_multiplicity(reps, n)
        if not multiplicity:
            break
    return multiplicity, total_charge


def residual_multiplicity(term: tuple[Any, ...], stabilizer: Any) -> int:
    result = 1
    for factor_index, factor in enumerate(stabilizer.factors):
        reps = tuple(component.residual_reps[factor_index] for component in term)
        result *= exact_singlet_multiplicity(reps, factor.dimension)
        if not result:
            break
    return result


def enumerate_lifts(evaluation: Any, catalog: tuple[Any, ...]) -> tuple[Lift, ...]:
    if evaluation.branch is None:
        return ()
    fields = [catalog[evaluation.candidate.combo[index]]
              for index in range(len(evaluation.candidate.combo))]
    by_occurrence: dict[int, list[Any]] = defaultdict(list)
    for component in evaluation.components:
        occurrence = int(component.occurrence_id.split("c", 1)[0][1:])
        by_occurrence[occurrence].append(component)
    lifts: dict[str, Lift] = {}
    parents = range(len(fields))
    for arity in range(FERMION_ARITY_MIN, FERMION_ARITY_MAX + 1):
        for parent_members in itertools.combinations_with_replacement(parents, arity):
            for term in itertools.product(*(by_occurrence[index] for index in parent_members)):
                residual_charge = sum(component.residual_charge for component in term)
                if residual_charge:
                    continue
                residual_channels = residual_multiplicity(term, evaluation.stabilizer)
                if not residual_channels:
                    continue
                component_keys = tuple(sorted(component.occurrence_id for component in term))
                for phi_count, dagger_count in dressing_options():
                    if arity + phi_count + dagger_count > TOTAL_CONSTITUENT_CAP:
                        continue
                    uv_channels, uv_charge = uv_multiplicity(
                        fields, parent_members, evaluation.branch, phi_count, dagger_count)
                    if not uv_channels:
                        continue
                    # The invariant basis is the exact common channel capacity
                    # of the UV and residual singlet spaces. Relations between
                    # different Fock contents are not imposed; VEV-equivalent
                    # dressings of one content are quotiented below.
                    channel_count = min(residual_channels, uv_channels)
                    fermions = "*".join(component_keys)
                    dressing = "*".join(
                        ["phi"] * phi_count + ["phi-dagger"] * dagger_count)
                    uv_lift = fermions + ("*" + dressing if dressing else "")
                    for channel in range(channel_count):
                        lift = Lift(
                            evaluation.evaluation_id, component_keys, arity,
                            phi_count, dagger_count, residual_charge,
                            residual_channels, uv_charge, uv_channels, channel, uv_lift,
                        )
                        lifts[lift.lift_key] = lift
    return tuple(lifts[key] for key in sorted(lifts))


def quotient_operators(lifts: tuple[Lift, ...]) -> tuple[Operator, ...]:
    groups: dict[str, list[Lift]] = defaultdict(list)
    for lift in lifts:
        groups[lift.operator_key].append(lift)
    rows = []
    for key, members in sorted(groups.items()):
        first = members[0]
        undressed = any(not row.phi_insertions and not row.phidagger_insertions for row in members)
        dressed = any(row.phi_insertions or row.phidagger_insertions for row in members)
        rows.append(Operator(
            first.evaluation_id, key, first.component_keys, first.fermion_arity,
            first.invariant_channel, undressed, dressed,
            tuple(sorted({row.dressing for row in members})), len(members),
            first.residual_charge,
            max(row.residual_singlet_multiplicity for row in members),
        ))
    return tuple(rows)


def count_for(evaluation_id: str, operators: dict[str, tuple[Operator, ...]], convention: str) -> int:
    rows = operators.get(evaluation_id, ())
    if convention == "undressed_only":
        return sum(row.has_undressed_lift for row in rows)
    if convention == "dressed_inclusive":
        return len(rows)
    raise ValueError(convention)


def score_rows(evaluations: list[Any], operators: dict[str, tuple[Operator, ...]],
               convention: str, threshold: int) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        branch = evaluation.branch is not None
        count = count_for(evaluation.evaluation_id, operators, convention)
        capacity = branch and count >= threshold
        distinguishable = branch and len({row.operator_key for row in operators.get(evaluation.evaluation_id, ())}) == len(operators.get(evaluation.evaluation_id, ()))
        rs = bool(branch and capacity and distinguishable)
        rows.append({
            "counting_convention": convention, "threshold": threshold,
            "evaluation_id": evaluation.evaluation_id, "dimensions": evaluation.dimensions,
            "structure_id": evaluation.structure_id, "branch_scope": evaluation.branch_scope,
            "scalar_branch": evaluation.scalar_branch,
            "clean_classification": evaluation.classification,
            "stable_substrate": branch, "record_token_count": count,
            "capacity_passes": capacity, "distinguishability_passes": distinguishable,
            "record_stability_passes": rs,
            "rs_implies_clean_counterexample": bool(rs and evaluation.clean is False),
        })
    return rows


def threshold_rows(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for convention in COUNTING_CONVENTIONS:
        for threshold in THRESHOLDS:
            domain = [row for row in scores if row["counting_convention"] == convention
                      and row["threshold"] == threshold and row["stable_substrate"]]
            selected = [row for row in domain if row["record_stability_passes"]]
            breaking = [row for row in selected if row["clean_classification"] == "breaking_evaluated"]
            rows.append({
                "counting_convention": convention, "threshold": threshold,
                "branch_domain_count": len(domain), "rs_branch_count": len(selected),
                "rs_clean_count": sum(row["clean_classification"] == "clean_evaluated" for row in selected),
                "rs_breaking_count": len(breaking), "counterexample_count": len(breaking),
                "counterexample_ids": "|".join(row["evaluation_id"] for row in breaking),
                "implication_passes": not breaking, "vacuous": not selected,
            })
    return rows


def structure_rows(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for convention in COUNTING_CONVENTIONS:
        for threshold in THRESHOLDS:
            selected = [row for row in scores if row["counting_convention"] == convention
                        and row["threshold"] == threshold and row["stable_substrate"]]
            groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in selected:
                groups[row["structure_id"]].append(row)
            for structure, members in sorted(groups.items()):
                rs = [row["record_stability_passes"] for row in members]
                clean = [row["clean_classification"] == "clean_evaluated" for row in members]
                rows.append({
                    "counting_convention": convention, "threshold": threshold,
                    "dimensions": members[0]["dimensions"], "structure_id": structure,
                    "branch_domain_size": len(members), "rs_branch_count": sum(rs),
                    "clean_branch_count": sum(clean),
                    "pointwise_implication": all(not a or b for a, b in zip(rs, clean)),
                    "universal_antecedent": all(rs),
                    "universal_implication": (not all(rs)) or all(clean),
                    "existential_antecedent": any(rs),
                    "existential_implication": (not any(rs)) or any(clean),
                })
    return rows


def quantifier_rows(scores: list[dict[str, Any]], structures: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for convention in COUNTING_CONVENTIONS:
        for threshold in THRESHOLDS:
            branches = [row for row in scores if row["counting_convention"] == convention
                        and row["threshold"] == threshold and row["stable_substrate"]]
            structs = [row for row in structures if row["counting_convention"] == convention
                       and row["threshold"] == threshold]
            point_ce = [row for row in branches if row["rs_implies_clean_counterexample"]]
            univ_ant = [row for row in structs if row["universal_antecedent"]]
            univ_ce = [row for row in univ_ant if not row["universal_implication"]]
            exist_ant = [row for row in structs if row["existential_antecedent"]]
            exist_ce = [row for row in exist_ant if not row["existential_implication"]]
            for reading, domain, antecedent, counterexamples in (
                ("branch_pointwise", branches,
                 [row for row in branches if row["record_stability_passes"]], point_ce),
                ("structure_universal", structs, univ_ant, univ_ce),
                ("structure_existential", structs, exist_ant, exist_ce),
            ):
                rows.append({
                    "counting_convention": convention, "threshold": threshold,
                    "quantifier_reading": reading, "domain_count": len(domain),
                    "antecedent_count": len(antecedent),
                    "counterexample_count": len(counterexamples),
                    "implication_passes": not counterexamples, "vacuous": not antecedent,
                })
    return rows


def lift_rows(lifts: Iterable[Lift]) -> list[dict[str, Any]]:
    return [{
        "evaluation_id": row.evaluation_id, "operator_key": row.operator_key,
        "lift_key": row.lift_key, "fermion_arity": row.fermion_arity,
        "component_basis": "|".join(row.component_keys),
        "phi_insertions": row.phi_insertions,
        "phidagger_insertions": row.phidagger_insertions,
        "total_constituent_count": row.fermion_arity + row.phi_insertions + row.phidagger_insertions,
        "dressing_class": row.dressing, "uv_lift": row.uv_lift,
        "uv_u1_charge": row.uv_charge, "uv_singlet_multiplicity": row.uv_singlet_multiplicity,
        "residual_u1_charge": row.residual_charge,
        "residual_singlet_multiplicity": row.residual_singlet_multiplicity,
        "invariant_channel": row.invariant_channel,
    } for row in lifts]


def operator_rows(operators: Iterable[Operator]) -> list[dict[str, Any]]:
    return [{
        "evaluation_id": row.evaluation_id, "operator_key": row.operator_key,
        "fermion_arity": row.fermion_arity, "component_basis": "|".join(row.component_keys),
        "invariant_channel": row.invariant_channel, "operator_category": row.category,
        "has_undressed_lift": row.has_undressed_lift, "has_dressed_lift": row.has_dressed_lift,
        "dressing_classes": "|".join(row.dressing_classes), "quotiented_lift_count": row.lift_count,
        "residual_u1_charge": row.residual_charge,
        "residual_singlet_multiplicity": row.residual_singlet_multiplicity,
    } for row in operators]


def census_rows(evaluations: list[Any], operators: dict[str, tuple[Operator, ...]]) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        if evaluation.branch is None:
            continue
        values = operators[evaluation.evaluation_id]
        undressed = [row for row in values if row.has_undressed_lift]
        dressed = [row for row in values if row.has_dressed_lift]
        dressed_new = [row for row in values if row.has_dressed_lift and not row.has_undressed_lift]
        rows.append({
            "evaluation_id": evaluation.evaluation_id, "dimensions": evaluation.dimensions,
            "branch_scope": evaluation.branch_scope, "clean_classification": evaluation.classification,
            "scalar_branch": evaluation.scalar_branch,
            "undressed_operator_count": len(undressed),
            "operators_with_dressed_lift_count": len(dressed),
            "dressed_new_operator_count": len(dressed_new),
            "inclusive_quotient_operator_count": len(values),
            "clean_branch_gains_dressed_tokens": bool(evaluation.clean and dressed_new),
        })
    return rows


def eval_049_regression(lifts: list[dict[str, Any]], operators: list[dict[str, Any]], old: dict[str, Any]) -> list[dict[str, Any]]:
    target = [row for row in lifts if row["evaluation_id"] == "eval_049"
              and row["component_basis"] == "o2c0|o3c0"
              and row["phi_insertions"] == 0 and row["phidagger_insertions"] == 1]
    old_eval = next(row for row in old["evaluations"] if row.evaluation_id == "eval_049")
    old_spectator = [token.token_id for token in old_eval.tokens if "w=1" in token.token_id]
    v3_eval = [row for row in operators if row["evaluation_id"] == "eval_049"]
    spectator_survives = any("w=1" in row["operator_key"] for row in v3_eval)
    return [{
        "evaluation_id": "eval_049",
        "required_component_basis": "o2c0|o3c0",
        "residual_operator_notation": "epsilon(o2c0,o3c0)",
        "required_uv_lift": "epsilon(o2c0,o3c0,phi-dagger)",
        "fermion_original_charge_sum": 2,
        "phidagger_original_charge": -2,
        "uv_charge_equation": "(-2)+(4)+(-2)=0",
        "residual_charge_equation": "(-3)+(3)=0",
        "residual_reps": "SU(2)_spectator:singlet*singlet;SU(2)_reduced:fund*fund->epsilon singlet",
        "required_operator_found": len(target) == 1,
        "enumerated_uv_lift": target[0]["uv_lift"] if target else "MISSING",
        "required_operator_uv_singlet_multiplicity": target[0]["uv_singlet_multiplicity"] if target else 0,
        "required_operator_residual_singlet_multiplicity": target[0]["residual_singlet_multiplicity"] if target else 0,
        "v1_spectator_cartan_token_ids": "|".join(old_spectator),
        "v1_spectator_cartan_token_survives_v3": spectator_survives,
        "spectator_cartan_coefficient": 0,
        "regression_passes": len(target) == 1 and not spectator_survives and bool(old_spectator),
    }]


def hash_rows(values: Iterable[str]) -> str:
    return hashlib.sha256(("\n".join(sorted(values)) + "\n").encode()).hexdigest()


def run() -> dict[str, Any]:
    evaluations, old = v2.build_evaluations()
    catalogs = old["version2"]["base"]["catalogs"]
    all_lifts: list[Lift] = []
    operators: dict[str, tuple[Operator, ...]] = {}
    for evaluation in evaluations:
        catalog = catalogs[evaluation.candidate.dimensions]
        lifts = enumerate_lifts(evaluation, catalog)
        all_lifts.extend(lifts)
        operators[evaluation.evaluation_id] = quotient_operators(lifts)
    lift_table = lift_rows(all_lifts)
    operator_table = operator_rows(row for values in operators.values() for row in values)
    scores = [row for convention in COUNTING_CONVENTIONS for threshold in THRESHOLDS
              for row in score_rows(evaluations, operators, convention, threshold)]
    thresholds = threshold_rows(scores)
    structures = structure_rows(scores)
    quantifiers = quantifier_rows(scores, structures)
    census = census_rows(evaluations, operators)
    regression = eval_049_regression(lift_table, operator_table, old)
    if not regression[0]["regression_passes"]:
        raise AssertionError(f"eval_049 regression failed: {regression[0]}")
    if any(row["uv_u1_charge"] or row["residual_u1_charge"] for row in lift_table):
        raise AssertionError("non-neutral lift entered census")
    t2 = {row["counting_convention"]: row for row in thresholds if row["threshold"] == 2}
    if t2["dressed_inclusive"]["counterexample_count"]:
        outcome = "COUNTEREXAMPLES_PERSIST_SCALAR_DRESSED_COMPLETE_BOUNDED_CENSUS"
    elif t2["dressed_inclusive"]["implication_passes"] and not t2["dressed_inclusive"]["vacuous"]:
        outcome = "IMPLICATION_HOLDS_SCALAR_DRESSED_COMPLETE_BOUNDED_CENSUS"
    else:
        outcome = "INCONCLUSIVE_VACUOUS_SCALAR_DRESSED_COMPLETE_BOUNDED_CENSUS"
    v2_reference = next(row for row in v2.threshold_rows(evaluations) if row["threshold"] == 2)
    ruling = [{
        "token_definition": "v2_restricted_UV_meson_epsilon_generators",
        "scalar_dressed_records_included": False,
        "rs_branch_count": v2_reference["rs_branch_count"],
        "rs_clean_count": v2_reference["rs_clean_count"],
        "rs_breaking_count": v2_reference["rs_breaking_count"],
        "counterexample_count": v2_reference["counterexample_count"],
        "pointwise_implication_passes": v2_reference["implication_passes"],
        "ruling": "HOLDS_NONVACUOUSLY_FOR_RESTRICTED_GENERATOR_GRAMMAR",
    }]
    for convention in COUNTING_CONVENTIONS:
        row = t2[convention]
        ruling.append({
            "token_definition": f"v3_complete_bounded_{convention}",
            "scalar_dressed_records_included": convention == "dressed_inclusive",
            "rs_branch_count": row["rs_branch_count"], "rs_clean_count": row["rs_clean_count"],
            "rs_breaking_count": row["rs_breaking_count"],
            "counterexample_count": row["counterexample_count"],
            "pointwise_implication_passes": row["implication_passes"],
            "ruling": "COUNTEREXAMPLES_PERSIST" if row["counterexample_count"] else "HOLDS_NONVACUOUSLY",
        })
    return {
        "pins": [{"dependency": V2_PATH.name, "expected_sha256": V2_SHA256,
                  "actual_sha256": sha256(V2_PATH), "passes": sha256(V2_PATH) == V2_SHA256}],
        "evaluations": evaluations, "lifts": lift_table, "operators": operator_table,
        "census": census, "scores": scores, "thresholds": thresholds,
        "structures": structures, "quantifiers": quantifiers,
        "eval_049_regression": regression, "outcome": outcome,
        "outcome_ruling": ruling,
        "bounds": {"fermion_arity_min": FERMION_ARITY_MIN,
                   "fermion_arity_max": FERMION_ARITY_MAX,
                   "scalar_insertion_max": SCALAR_INSERTION_MAX,
                   "total_constituent_cap": TOTAL_CONSTITUENT_CAP},
        "hashes": {
            "lifts": hash_rows(row["evaluation_id"] + "::" + row["lift_key"] for row in lift_table),
            "operators": hash_rows(row["evaluation_id"] + "::" + row["operator_key"] for row in operator_table),
            "scores": hash_rows(f"{row['counting_convention']}::{row['threshold']}::{row['evaluation_id']}::{row['record_stability_passes']}" for row in scores),
        },
    }


if __name__ == "__main__":
    result = run()
    t2 = [row for row in result["thresholds"] if row["threshold"] == 2]
    print(f"record_grammar_ablation_v3.py: PASS: lifts={len(result['lifts'])} "
          f"operators={len(result['operators'])} threshold2={t2} outcome={result['outcome']}")
