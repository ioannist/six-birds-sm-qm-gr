#!/usr/bin/env python3
"""S6-ABLATION-2: records neutral under the full branch residual group."""

from __future__ import annotations

import hashlib
import itertools
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
S1 = HERE.parent / "s1_carrier_reconstruction"
PINS = {
    S1 / "representation_model.py": "3a22babf413c0175a52763d67f1b7deb02e9694bc58769fa0356250b1f9beb75",
    S1 / "carrier_chain.py": "ab7a07cd82d8aa82c19476177ed3b99f9ca6d8af315f25f3616e646012d23586",
    S1 / "carrier_chain_v2.py": "ba3d227e8dbaf4a64465146d3e073bec957857b2a41749addf7d786b4de5e209",
    S1 / "carrier_chain_v3.py": "fe85f2db6df935bff93670be60c8968ebad776bba3d7f6b59f2994311bb8a89d",
    HERE / "record_grammar_ablation.py": "bce7eeba263e7a4df60e7c38e52a94e0171eefebe60158e4462df12bee73b2f3",
}
PUBLISHED_MIN_RECORD_TOKENS = 2
THRESHOLDS = (1, 2, 3, 4)


def verify_pins() -> list[dict[str, Any]]:
    rows = []
    for path, expected in PINS.items():
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"dependency pin mismatch for {path.name}: {actual} != {expected}")
        rows.append({"dependency": path.name, "expected_sha256": expected,
                     "actual_sha256": actual, "passes": actual == expected})
    return rows


PIN_ROWS = verify_pins()
for directory in (S1, HERE):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import carrier_chain as carrier  # noqa: E402
import carrier_chain_v3 as v3  # noqa: E402
import record_grammar_ablation as v1_s6  # noqa: E402
import representation_model as rm  # noqa: E402


@dataclass(frozen=True)
class ResidualFactor:
    label: str
    dimension: int
    source_factor_index: int
    origin: str


@dataclass(frozen=True)
class Stabilizer:
    active_factor_index: int
    scalar_rep: str
    scalar_charge: int
    vev_cartan_weight: int
    original_u1_coefficient: int
    broken_cartan_coefficient: int
    factors: tuple[ResidualFactor, ...]

    @property
    def equation(self) -> str:
        return (f"({self.original_u1_coefficient})*({self.scalar_charge}) + "
                f"({self.broken_cartan_coefficient})*({self.vev_cartan_weight}) = 0")

    @property
    def residual_group(self) -> str:
        nonabelian = " x ".join(f"SU({factor.dimension})[{factor.label}]" for factor in self.factors)
        return f"{nonabelian} x U(1)_res" if nonabelian else "U(1)_res"


@dataclass(frozen=True)
class ResidualComponent:
    occurrence_id: str
    field_text: str
    residual_reps: tuple[str, ...]
    original_charge: int
    broken_cartan_weight: int
    residual_charge: int

    @property
    def key(self) -> str:
        reps = "x".join(self.residual_reps) if self.residual_reps else "all_singlet"
        return (f"{self.occurrence_id}[{self.field_text}]"
                f"{{res={reps};q={self.original_charge};h={self.broken_cartan_weight};"
                f"qres={self.residual_charge}}}")


@dataclass(frozen=True)
class Token:
    token_class: str
    component_keys: tuple[str, ...]
    reps_by_factor: tuple[tuple[str, ...], ...]
    residual_charge: int
    singlet_multiplicity: int
    invariant_channel: int
    rule: str

    @property
    def state_key(self) -> str:
        return "+".join(sorted(self.component_keys)) + f"::channel={self.invariant_channel}"

    @property
    def token_id(self) -> str:
        return f"{self.token_class}:{self.state_key}"


@dataclass(frozen=True)
class Evaluation:
    evaluation_id: str
    candidate: Any
    branch: Any | None
    classification: str
    branch_scope: str
    stabilizer: Stabilizer | None
    components: tuple[ResidualComponent, ...]
    tokens: tuple[Token, ...]
    distinguishability_passes: bool
    collision_count: int

    @property
    def dimensions(self) -> str:
        return "|".join(map(str, self.candidate.dimensions))

    @property
    def structure_id(self) -> str:
        return f"{self.dimensions}::{self.candidate.support_key}"

    @property
    def scalar_branch(self) -> str:
        return self.branch.scalar_branch if self.branch is not None else "NO_SINGLETON_BRANCH"

    @property
    def clean(self) -> bool | None:
        if self.classification == "clean_evaluated":
            return True
        if self.classification == "breaking_evaluated":
            return False
        return None

    def rs(self, threshold: int) -> bool:
        return bool(self.branch is not None and self.distinguishability_passes and len(self.tokens) >= threshold)


def primitive_neutrality(charge: int, vev_weight: int) -> tuple[int, int]:
    divisor = math.gcd(abs(charge), abs(vev_weight))
    a, b = vev_weight // divisor, -charge // divisor
    if a < 0:
        a, b = -a, -b
    if a * charge + b * vev_weight != 0 or math.gcd(abs(a), abs(b)) != 1:
        raise AssertionError("non-primitive neutrality solution")
    return a, b


def scalar_vev_weight(rep: str, n: int) -> int:
    canonical = rm.canonical_rep(rep, n)
    if canonical == "fund":
        return -(n - 1)
    if canonical == "antifund":
        return n - 1
    raise ValueError(f"singleton carrier branch has unsupported VEV rep SU({n}) {rep}")


def solve_stabilizer(branch: Any) -> Stabilizer:
    scalar = branch.representative
    active = carrier.active_factor_indices(scalar)
    if len(active) != 1:
        raise AssertionError(f"expected one active factor, got {active}")
    active_index = active[0]
    n = scalar.dimensions[active_index]
    rep = rm.canonical_rep(scalar.reps[active_index], n)
    weight = scalar_vev_weight(rep, n)
    a, b = primitive_neutrality(scalar.charge, weight)
    factors = []
    for index, dimension in enumerate(scalar.dimensions):
        if index != active_index:
            factors.append(ResidualFactor(f"spectator_f{index}", dimension, index, "unbroken_spectator"))
        elif dimension - 1 >= 2:
            factors.append(ResidualFactor(f"reduced_f{index}", dimension - 1, index, "VEV_stabilizer"))
    result = Stabilizer(active_index, rep, scalar.charge, weight, a, b, tuple(factors))
    if result.original_u1_coefficient * scalar.charge + result.broken_cartan_coefficient * weight:
        raise AssertionError("VEV is not neutral under computed residual U(1)")
    return result


def active_branching(rep: str, n: int) -> tuple[tuple[str, int], ...]:
    """SU(N) -> SU(N-1) x H, H=diag(1,...,1,-N+1)."""
    rep = rm.canonical_rep(rep, n)
    trivial = "singlet"
    if rep == "singlet":
        return ((trivial, 0),)
    if rep == "fund":
        return (("fund" if n > 2 else trivial, 1), (trivial, -(n - 1)))
    if rep == "antifund":
        return (("antifund" if n > 2 else trivial, -1), (trivial, n - 1))
    if rep == "antisym2":
        return ((rm.canonical_rep("antisym2", n - 1), 2), ("fund", 2 - n))
    if rep == "conj_antisym2":
        return ((rm.canonical_rep("conj_antisym2", n - 1), -2), ("antifund", n - 2))
    if rep == "sym2":
        return ((rm.canonical_rep("sym2", n - 1), 2), ("fund", 2 - n), (trivial, -2 * (n - 1)))
    if rep == "conj_sym2":
        return ((rm.canonical_rep("conj_sym2", n - 1), -2), ("antifund", n - 2), (trivial, 2 * (n - 1)))
    raise AssertionError(rep)


def residual_components(evaluation: Any, stabilizer: Stabilizer,
                        catalog: tuple[Any, ...]) -> tuple[ResidualComponent, ...]:
    rows = []
    active = stabilizer.active_factor_index
    for occurrence, type_id in enumerate(evaluation.candidate.combo):
        field = catalog[type_id]
        pieces = active_branching(field.reps[active], field.dimensions[active])
        for piece_index, (active_rep, weight) in enumerate(pieces):
            reps = []
            for factor in stabilizer.factors:
                if factor.source_factor_index == active:
                    reps.append(rm.canonical_rep(active_rep, factor.dimension))
                else:
                    reps.append(rm.canonical_rep(field.reps[factor.source_factor_index], factor.dimension))
            qres = (stabilizer.original_u1_coefficient * field.charge
                    + stabilizer.broken_cartan_coefficient * weight)
            rows.append(ResidualComponent(
                f"o{occurrence}c{piece_index}", f"{'x'.join(field.reps)}:{field.charge}",
                tuple(reps), field.charge, weight, qres,
            ))
    return tuple(rows)


def singlet_multiplicity(reps: tuple[str, ...], n: int) -> int:
    if len(reps) == 2:
        return v3.singlet_decomposition(reps[0], reps[1], "singlet", n)[0]
    if len(reps) == 3:
        return v3.singlet_decomposition(reps[0], reps[1], reps[2], n)[0]
    raise ValueError(f"unsupported exact invariant arity {len(reps)}")


def exterior_rank(rep: str, n: int) -> int | None:
    rep = rm.canonical_rep(rep, n)
    if rep == "fund":
        return 1
    if rep == "antifund":
        return n - 1
    if rep == "antisym2":
        return 2
    if rep == "conj_antisym2":
        return n - 2
    return None


def uv_token_candidates(evaluation: Any, catalog: tuple[Any, ...]) -> list[tuple[str, tuple[int, ...], str]]:
    """Construct the UV meson/epsilon basis, then restrict it branch by branch."""
    parents = list(range(len(evaluation.candidate.combo)))
    fields = [catalog[evaluation.candidate.combo[index]] for index in parents]
    n = evaluation.candidate.dimensions[-1]
    substrate = [rm.canonical_rep(field.reps[-1], n) for field in fields]
    candidates: dict[tuple[str, tuple[int, ...]], str] = {}
    for left, right in itertools.combinations_with_replacement(parents, 2):
        if substrate[left] != "singlet" and rm.conjugate_rep(substrate[left], n) == substrate[right]:
            members = tuple(sorted((left, right)))
            candidates[("mesonic", members)] = "UV_r_tensor_conjugate_r_restricted_to_residual"
    for rep in ("fund", "antifund"):
        family = [index for index in parents if substrate[index] == rep]
        for members in itertools.combinations_with_replacement(family, n):
            candidates[("baryonic", tuple(sorted(members)))] = f"UV_epsilon_rank_{n}_restricted_to_residual"
    exterior = [index for index in parents if exterior_rank(substrate[index], n) is not None]
    for arity in range(2, n + 1):
        for members in itertools.combinations_with_replacement(exterior, arity):
            ranks = [int(exterior_rank(substrate[index], n)) for index in members]
            reps = [substrate[index] for index in members]
            covariant = sum(ranks) == n
            contravariant = sum(n - rank for rank in ranks) == n
            if not (covariant or contravariant):
                continue
            if arity == 2 and rm.conjugate_rep(reps[0], n) == reps[1]:
                continue
            if arity == n and len(set(reps)) == 1 and reps[0] in {"fund", "antifund"}:
                continue
            rule = "UV_mixed_epsilon_covariant" if covariant else "UV_mixed_epsilon_contravariant"
            candidates[("mixed", tuple(sorted(members)))] = rule + "_restricted_to_residual"
    return [(kind, members, rule) for (kind, members), rule in sorted(candidates.items())]


def exact_term_singlet_multiplicity(term: tuple[ResidualComponent, ...], stabilizer: Stabilizer) -> tuple[int, tuple[tuple[str, ...], ...]]:
    reps_by_factor = tuple(
        tuple(member.residual_reps[index] for member in term)
        for index in range(len(stabilizer.factors))
    )
    multiplicity = 1
    for reps, factor in zip(reps_by_factor, stabilizer.factors):
        if len(reps) <= 3:
            multiplicity *= singlet_multiplicity(reps, factor.dimension)
            if not multiplicity:
                return 0, reps_by_factor
        else:
            # The only arity-four UV class in this carrier is an SU(4)
            # epsilon. Its candidate charge is nonzero and is rejected before
            # this path. Keep this explicit instead of an approximate test.
            raise AssertionError("unexpected neutral arity-four residual term")
    return multiplicity, reps_by_factor


def construct_tokens(evaluation: Any, components: tuple[ResidualComponent, ...],
                     stabilizer: Stabilizer, catalog: tuple[Any, ...]) -> tuple[Token, ...]:
    by_occurrence: dict[int, list[ResidualComponent]] = defaultdict(list)
    for component in components:
        occurrence = int(component.occurrence_id.split("c", 1)[0][1:])
        by_occurrence[occurrence].append(component)
    tokens = {}
    fields = [catalog[evaluation.candidate.combo[index]] for index in range(len(evaluation.candidate.combo))]
    n = evaluation.candidate.dimensions[-1]
    for token_class, parent_members, rule in uv_token_candidates(evaluation, catalog):
        # A full SU(N) epsilon or conjugate pair has zero broken-factor H
        # charge when the last factor is active. Then nonzero total original
        # U(1) charge cannot be rescued by selecting components.
        if stabilizer.active_factor_index == len(evaluation.candidate.dimensions) - 1:
            if sum(fields[index].charge for index in parent_members):
                continue
        surviving_terms = []
        for term in itertools.product(*(by_occurrence[index] for index in parent_members)):
            if sum(member.residual_charge for member in term):
                continue
            multiplicity, reps_by_factor = exact_term_singlet_multiplicity(term, stabilizer)
            if multiplicity:
                surviving_terms.append((tuple(term), reps_by_factor, multiplicity))
        if not surviving_terms:
            continue
        term, reps_by_factor, _term_multiplicity = min(
            surviving_terms, key=lambda item: tuple(row.key for row in item[0])
        )
        residual_multiplicity = sum(item[2] for item in surviving_terms)
        parent_keys = tuple(sorted(
            f"o{index}[{'x'.join(fields[index].reps)}:{fields[index].charge}]"
            for index in parent_members
        ))
        original_reps = tuple(rm.canonical_rep(fields[index].reps[-1], n) for index in parent_members)
        if len(original_reps) == 2:
            uv_multiplicity = v3.singlet_decomposition(original_reps[0], original_reps[1], "singlet", n)[0]
        elif len(original_reps) == 3:
            uv_multiplicity = v3.singlet_decomposition(*original_reps, n)[0]
        else:
            uv_multiplicity = 1  # determinant epsilon, after the exact charge gate above
        for channel in range(uv_multiplicity):
            token = Token(token_class, parent_keys, reps_by_factor, 0, residual_multiplicity,
                          channel, rule + f";surviving_terms={len(surviving_terms)}")
            tokens[token.state_key] = token
    return tuple(tokens[key] for key in sorted(tokens))


def distinguishability(tokens: tuple[Token, ...]) -> tuple[bool, int]:
    counts = Counter(token.state_key for token in tokens)
    collisions = sum(count - 1 for count in counts.values())
    return collisions == 0, collisions


def build_evaluations() -> tuple[list[Evaluation], dict[str, Any]]:
    old = v1_s6.run_ablation()
    catalogs = old["version2"]["base"]["catalogs"]
    rows = []
    for source in old["evaluations"]:
        if source.branch is None:
            rows.append(Evaluation(source.evaluation_id, source.candidate, None,
                                   source.classification, source.branch_scope, None, (), (), True, 0))
            continue
        stabilizer = solve_stabilizer(source.branch)
        components = residual_components(source, stabilizer, catalogs[source.candidate.dimensions])
        tokens = construct_tokens(source, components, stabilizer, catalogs[source.candidate.dimensions])
        distinct, collisions = distinguishability(tokens)
        rows.append(Evaluation(source.evaluation_id, source.candidate, source.branch,
                               source.classification, source.branch_scope, stabilizer,
                               components, tokens, distinct, collisions))
    return rows, old


def score_rows(evaluations: list[Evaluation], threshold: int = 2) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        counts = Counter(token.token_class for token in evaluation.tokens)
        rs = evaluation.rs(threshold)
        rows.append({
            "evaluation_id": evaluation.evaluation_id, "dimensions": evaluation.dimensions,
            "structure_id": evaluation.structure_id, "support_key": evaluation.candidate.support_key,
            "branch_scope": evaluation.branch_scope, "scalar_branch": evaluation.scalar_branch,
            "clean_classification": evaluation.classification,
            "residual_group": evaluation.stabilizer.residual_group if evaluation.stabilizer else "UNDEFINED_NO_SINGLETON_BRANCH",
            "mesonic_token_count": counts["mesonic"], "baryonic_token_count": counts["baryonic"],
            "mixed_token_count": counts["mixed"], "neutral_record_token_count": len(evaluation.tokens),
            "capacity_threshold": threshold, "capacity_passes": len(evaluation.tokens) >= threshold,
            "distinguishability_passes": evaluation.distinguishability_passes,
            "collision_count": evaluation.collision_count, "record_stability_passes": rs,
            "rs_implies_clean_counterexample": bool(rs and evaluation.clean is False),
        })
    return rows


def stabilizer_rows(evaluations: list[Evaluation]) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        if evaluation.stabilizer is None:
            continue
        s = evaluation.stabilizer
        rows.append({
            "evaluation_id": evaluation.evaluation_id, "dimensions": evaluation.dimensions,
            "branch_scope": evaluation.branch_scope, "scalar_branch": evaluation.scalar_branch,
            "active_factor_index": s.active_factor_index, "scalar_rep": s.scalar_rep,
            "scalar_charge": s.scalar_charge, "vev_cartan_weight": s.vev_cartan_weight,
            "u1_coefficient": s.original_u1_coefficient, "broken_cartan_coefficient": s.broken_cartan_coefficient,
            "neutrality_equation": s.equation, "neutrality_lhs": s.original_u1_coefficient * s.scalar_charge + s.broken_cartan_coefficient * s.vev_cartan_weight,
            "residual_group": s.residual_group,
            "spectator_cartans_in_u1": 0,
        })
    return rows


def component_rows(evaluations: list[Evaluation]) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        for component in evaluation.components:
            rows.append({
                "evaluation_id": evaluation.evaluation_id, "component_id": component.occurrence_id,
                "field": component.field_text, "residual_reps": "|".join(component.residual_reps),
                "original_u1_charge": component.original_charge,
                "broken_factor_cartan_weight": component.broken_cartan_weight,
                "residual_u1_charge": component.residual_charge,
            })
    return rows


def token_rows(evaluations: list[Evaluation]) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        for token in evaluation.tokens:
            rows.append({
                "evaluation_id": evaluation.evaluation_id, "dimensions": evaluation.dimensions,
                "branch_scope": evaluation.branch_scope, "scalar_branch": evaluation.scalar_branch,
                "residual_group": evaluation.stabilizer.residual_group,
                "token_id": token.token_id, "token_class": token.token_class,
                "arity": len(token.component_keys), "component_basis": " || ".join(token.component_keys),
                "reps_by_residual_factor": " || ".join("x".join(reps) for reps in token.reps_by_factor),
                "residual_u1_charge": token.residual_charge,
                "residual_singlet_multiplicity": token.singlet_multiplicity,
                "uv_invariant_channel": token.invariant_channel, "invariant_rule": token.rule,
            })
    return rows


def structure_quantifiers(evaluations: list[Evaluation], threshold: int) -> list[dict[str, Any]]:
    groups: dict[str, list[Evaluation]] = defaultdict(list)
    for evaluation in evaluations:
        groups[evaluation.structure_id].append(evaluation)
    rows = []
    for structure, members in sorted(groups.items()):
        branches = [row for row in members if row.branch is not None]
        if not branches:
            rows.append({"threshold": threshold, "dimensions": members[0].dimensions,
                         "structure_id": structure, "branch_domain_size": 0,
                         "quantifier_domain": "undefined_no_singleton_branch",
                         "rs_branch_count": 0, "clean_branch_count": 0,
                         "pointwise_implication": "undefined", "universal_implication": "undefined",
                         "existential_implication": "undefined"})
            continue
        rs = [row.rs(threshold) for row in branches]
        clean = [bool(row.clean) for row in branches]
        rows.append({"threshold": threshold, "dimensions": members[0].dimensions,
                     "structure_id": structure, "branch_domain_size": len(branches),
                     "quantifier_domain": "evaluated_singleton_branches",
                     "rs_branch_count": sum(rs), "clean_branch_count": sum(clean),
                     "pointwise_implication": all(not a or b for a, b in zip(rs, clean)),
                     "universal_implication": (not all(rs)) or all(clean),
                     "existential_implication": (not any(rs)) or any(clean)})
    return rows


def quantifier_summary(evaluations: list[Evaluation], threshold: int) -> list[dict[str, Any]]:
    branches = [row for row in evaluations if row.branch is not None]
    structures = [row for row in structure_quantifiers(evaluations, threshold)
                  if row["quantifier_domain"] == "evaluated_singleton_branches"]
    point_ce = [row for row in branches if row.rs(threshold) and row.clean is False]
    universal_ant = [row for row in structures if row["rs_branch_count"] == row["branch_domain_size"]]
    universal_ce = [row for row in universal_ant if row["clean_branch_count"] != row["branch_domain_size"]]
    existential_ant = [row for row in structures if row["rs_branch_count"] > 0]
    existential_ce = [row for row in existential_ant if row["clean_branch_count"] == 0]
    return [
        {"threshold": threshold, "quantifier_reading": "branch_pointwise", "domain_count": len(branches),
         "antecedent_count": sum(row.rs(threshold) for row in branches), "counterexample_count": len(point_ce),
         "implication_passes": not point_ce, "vacuous": not any(row.rs(threshold) for row in branches)},
        {"threshold": threshold, "quantifier_reading": "structure_universal", "domain_count": len(structures),
         "antecedent_count": len(universal_ant), "counterexample_count": len(universal_ce),
         "implication_passes": not universal_ce, "vacuous": not universal_ant},
        {"threshold": threshold, "quantifier_reading": "structure_existential", "domain_count": len(structures),
         "antecedent_count": len(existential_ant), "counterexample_count": len(existential_ce),
         "implication_passes": not existential_ce, "vacuous": not existential_ant},
    ]


def threshold_rows(evaluations: list[Evaluation]) -> list[dict[str, Any]]:
    rows = []
    branches = [row for row in evaluations if row.branch is not None]
    for threshold in THRESHOLDS:
        rs = [row for row in branches if row.rs(threshold)]
        breaking = [row for row in rs if row.clean is False]
        rows.append({
            "threshold": threshold, "branch_domain_count": len(branches), "rs_branch_count": len(rs),
            "rs_clean_count": sum(row.clean is True for row in rs), "rs_breaking_count": len(breaking),
            "counterexample_count": len(breaking),
            "rs_family_membership": ";".join(f"{k}:{v}" for k, v in sorted(Counter(row.dimensions for row in rs).items())),
            "rs_branch_scope_membership": ";".join(f"{k}:{v}" for k, v in sorted(Counter(row.branch_scope for row in rs).items())),
            "implication_passes": not breaking, "vacuous": not rs,
        })
    return rows


def collision_control(evaluations: list[Evaluation]) -> list[dict[str, Any]]:
    source = next((row for row in evaluations if row.tokens), None)
    if source is None:
        raise AssertionError("no in-carrier token available for collision control")
    token = source.tokens[0]
    constructed = (token, Token(token.token_class, tuple(reversed(token.component_keys)),
                                token.reps_by_factor, token.residual_charge,
                                token.singlet_multiplicity, token.invariant_channel, token.rule))
    passes, count = distinguishability(constructed)
    return [{
        "control_id": "in_carrier_reversed_description_collision",
        "source_evaluation_id": source.evaluation_id, "source_token_id": token.token_id,
        "constructed_description_a": "+".join(token.component_keys),
        "constructed_description_b": "+".join(reversed(token.component_keys)),
        "canonical_state_key_a": constructed[0].state_key,
        "canonical_state_key_b": constructed[1].state_key,
        "invariant_inner_product": 1, "collision_count": count,
        "distinguishability_passes": passes, "expected_to_fail": True,
        "control_passes": (not passes and count == 1),
    }]


def eval_049_trace(evaluations: list[Evaluation], old: dict[str, Any]) -> list[dict[str, Any]]:
    current = next(row for row in evaluations if row.evaluation_id == "eval_049")
    old_eval = next(row for row in old["evaluations"] if row.evaluation_id == "eval_049")
    old_tokens = list(old_eval.tokens)
    old_spectator = [token for token in old_tokens if "w=1" in token.token_id]
    current_spectator_triple = [
        token for token in current.tokens
        if len(token.component_keys) == 3
        and all(key.startswith("o0[") for key in token.component_keys)
    ]
    return [{
        "evaluation_id": "eval_049", "branch_scope": current.branch_scope,
        "old_component_rule": "q_old = original_U1 + spectator_SU2_Cartan_weight",
        "old_token_count": len(old_tokens),
        "old_token_ids": " || ".join(token.token_id for token in old_tokens),
        "old_spectator_doublet_token_count": len(old_spectator),
        "computed_residual_group": current.stabilizer.residual_group,
        "neutrality_equation": current.stabilizer.equation,
        "spectator_cartans_in_residual_u1": 0,
        "residual_component_count": len(current.components),
        "full_residual_neutral_token_count": len(current.tokens),
        "remaining_token_ids": " || ".join(token.token_id for token in current.tokens),
        "spectator_doublet_token_disappears": bool(old_spectator) and not current_spectator_triple,
        "record_stability_threshold_2": current.rs(2),
        "clean_classification": current.classification,
    }]


def hash_rows(values: Iterable[str]) -> str:
    return hashlib.sha256(("\n".join(sorted(values)) + "\n").encode()).hexdigest()


def run() -> dict[str, Any]:
    evaluations, old = build_evaluations()
    scores = score_rows(evaluations)
    stabilizers = stabilizer_rows(evaluations)
    components = component_rows(evaluations)
    tokens = token_rows(evaluations)
    thresholds = threshold_rows(evaluations)
    quantifiers = [row for threshold in THRESHOLDS for row in quantifier_summary(evaluations, threshold)]
    structures = structure_quantifiers(evaluations, PUBLISHED_MIN_RECORD_TOKENS)
    controls = collision_control(evaluations)
    trace = eval_049_trace(evaluations, old)
    if any(row["neutrality_lhs"] or row["spectator_cartans_in_u1"] for row in stabilizers):
        raise AssertionError("stabilizer neutrality assertion failed")
    if not all(row["control_passes"] for row in controls):
        raise AssertionError("collision control failed to fail")
    reference = next(row for row in thresholds if row["threshold"] == 2)
    outcome = ("IMPLICATION_RESTORED_POINTWISE_FULL_RESIDUAL_NEUTRAL_GRAMMAR"
               if reference["implication_passes"] and not reference["vacuous"]
               else "COUNTEREXAMPLES_PERSIST_FULL_RESIDUAL_NEUTRAL_GRAMMAR")
    return {
        "pins": PIN_ROWS, "evaluations": evaluations, "scores": scores,
        "stabilizers": stabilizers, "components": components, "tokens": tokens,
        "thresholds": thresholds, "quantifiers": quantifiers, "structures": structures,
        "collision_controls": controls, "eval_049_trace": trace, "outcome": outcome,
        "hashes": {
            "scores": hash_rows(f"{row['evaluation_id']}::{row['record_stability_passes']}" for row in scores),
            "tokens": hash_rows(f"{row['evaluation_id']}::{row['token_id']}" for row in tokens),
            "stabilizers": hash_rows(f"{row['evaluation_id']}::{row['neutrality_equation']}" for row in stabilizers),
        },
    }


if __name__ == "__main__":
    result = run()
    t2 = next(row for row in result["thresholds"] if row["threshold"] == 2)
    print(f"record_grammar_ablation_v2.py: PASS: RS_t2={t2['rs_branch_count']} "
          f"counterexamples_t2={t2['counterexample_count']} outcome={result['outcome']}")
