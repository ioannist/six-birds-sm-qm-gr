#!/usr/bin/env python3
"""Dimension-generic record grammar over the branch-complete S1-v2 carrier."""

from __future__ import annotations

import hashlib
import itertools
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
S1_DIR = HERE.parent / "s1_carrier_reconstruction"
PINNED_S1_SHA256 = {
    "representation_model.py": "3a22babf413c0175a52763d67f1b7deb02e9694bc58769fa0356250b1f9beb75",
    "carrier_chain.py": "ab7a07cd82d8aa82c19476177ed3b99f9ca6d8af315f25f3616e646012d23586",
    "carrier_chain_v2.py": "ba3d227e8dbaf4a64465146d3e073bec957857b2a41749addf7d786b4de5e209",
}
PUBLISHED_MIN_RECORD_TOKENS = 2
SENSITIVITY_THRESHOLDS = (1, 2, 3, 4)


def verify_import_pins() -> list[dict[str, Any]]:
    rows = []
    for name, expected in PINNED_S1_SHA256.items():
        path = S1_DIR / name
        if not path.is_file():
            raise RuntimeError(f"missing pinned S1-v2 dependency: {path}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(
                f"S1-v2 dependency hash mismatch for {name}: expected {expected}, got {actual}"
            )
        rows.append({"dependency": name, "expected_sha256": expected,
                     "actual_sha256": actual, "passes": True})
    return rows


PIN_ROWS = verify_import_pins()
if str(S1_DIR) not in sys.path:
    sys.path.insert(0, str(S1_DIR))

import carrier_chain as v1  # noqa: E402
import carrier_chain_v2 as v2  # noqa: E402
import representation_model as rm  # noqa: E402


@dataclass(frozen=True)
class Component:
    occurrence_id: str
    field_text: str
    substrate_rep: str
    base_charge: int
    spectator_weight: tuple[int, ...]
    component_charge: int

    @property
    def key(self) -> str:
        weight = ",".join(map(str, self.spectator_weight)) or "none"
        return (
            f"{self.occurrence_id}[{self.field_text}]"
            f"{{rep={self.substrate_rep};w={weight};q={self.component_charge}}}"
        )


@dataclass(frozen=True)
class RecordToken:
    token_class: str
    substrate_dimension: int
    component_keys: tuple[str, ...]
    representation_content: tuple[str, ...]
    total_charge: int
    invariant_rule: str

    @property
    def token_id(self) -> str:
        return (
            f"{self.token_class}:SU{self.substrate_dimension}:"
            + "+".join(self.component_keys)
        )


@dataclass(frozen=True)
class Evaluation:
    evaluation_id: str
    candidate: v1.Candidate
    branch: v2.ScalarBranch | None
    branch_scope: str
    classification: str
    stable_substrate: bool
    distinguishability_passes: bool
    alias_ambiguity_count: int
    tokens: tuple[RecordToken, ...]

    @property
    def dimensions_text(self) -> str:
        return "|".join(map(str, self.candidate.dimensions))

    @property
    def structure_id(self) -> str:
        return f"{self.dimensions_text}::{self.candidate.support_key}"

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

    def capacity_passes(self, threshold: int) -> bool:
        return len(self.tokens) >= threshold

    def record_stability_passes(self, threshold: int) -> bool:
        return bool(
            self.stable_substrate
            and self.distinguishability_passes
            and self.capacity_passes(threshold)
        )


def projected_representation_weights(rep: str, n: int) -> tuple[int, ...]:
    """Weights under diag(N-1,N-3,...,-N+1), with multiplicity."""
    rep = rm.canonical_rep(rep, n)
    fundamental = tuple(n - 1 - 2 * index for index in range(n))
    if rep == "singlet":
        return (0,)
    if rep == "fund":
        return fundamental
    if rep == "antifund":
        return tuple(-value for value in fundamental)
    if rep == "sym2":
        return tuple(sorted(
            fundamental[left] + fundamental[right]
            for left in range(n)
            for right in range(left, n)
        ))
    if rep == "conj_sym2":
        return tuple(-value for value in projected_representation_weights("sym2", n))
    if rep == "antisym2":
        return tuple(sorted(
            fundamental[left] + fundamental[right]
            for left in range(n)
            for right in range(left + 1, n)
        ))
    if rep == "conj_antisym2":
        return tuple(-value for value in projected_representation_weights("antisym2", n))
    raise AssertionError(f"unhandled representation weight system: SU({n}) {rep}")


def component_basis(candidate: v1.Candidate, catalog: tuple[v1.TypeRow, ...]) -> tuple[Component, ...]:
    dimensions = candidate.dimensions
    components = []
    for occurrence, type_id in enumerate(candidate.combo):
        field = catalog[type_id]
        spectator_weight_sets = [
            projected_representation_weights(rep, n)
            for rep, n in zip(field.reps[:-1], dimensions[:-1])
        ]
        weight_products = itertools.product(*spectator_weight_sets) if spectator_weight_sets else [()]
        for weight_index, weights in enumerate(weight_products):
            components.append(Component(
                occurrence_id=f"o{occurrence}c{weight_index}",
                field_text=f"{'x'.join(field.reps)}:{field.charge}",
                substrate_rep=rm.canonical_rep(field.reps[-1], dimensions[-1]),
                base_charge=field.charge,
                spectator_weight=tuple(weights),
                component_charge=field.charge + sum(weights),
            ))
    return tuple(components)


def exterior_rank(rep: str, n: int) -> int | None:
    """Covariant exterior-tensor rank used by one epsilon contraction."""
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


def _token(token_class: str, n: int, components: Iterable[Component], rule: str) -> RecordToken:
    members = tuple(sorted(components, key=lambda row: row.key))
    return RecordToken(
        token_class=token_class,
        substrate_dimension=n,
        component_keys=tuple(row.key for row in members),
        representation_content=tuple(row.substrate_rep for row in members),
        total_charge=sum(row.component_charge for row in members),
        invariant_rule=rule,
    )


def neutral_record_tokens(components: tuple[Component, ...], n: int) -> tuple[RecordToken, ...]:
    tokens: dict[str, RecordToken] = {}

    # Mesonic basis: a nontrivial representation and its actual conjugate.
    for left, right in itertools.combinations_with_replacement(components, 2):
        if left.substrate_rep == "singlet":
            continue
        if rm.conjugate_rep(left.substrate_rep, n) != right.substrate_rep:
            continue
        candidate = _token("mesonic", n, (left, right), "r_tensor_conjugate_r")
        if candidate.total_charge == 0:
            tokens[candidate.token_id] = candidate

    # Baryonic basis: the epsilon tensor takes exactly N fundamentals or N
    # antifundamentals. N is the actual substrate dimension, never literal 3.
    for rep, rule in (("fund", "epsilon_N_fund"), ("antifund", "epsilon_N_antifund")):
        family = [row for row in components if row.substrate_rep == rep]
        for members in itertools.combinations_with_replacement(family, n):
            candidate = _token("baryonic", n, members, rule)
            if candidate.total_charge == 0:
                tokens[candidate.token_id] = candidate

    # Mixed epsilon basis: exterior-power ranks can jointly saturate one
    # epsilon tensor. Pure N-fold fundamentals and two-body conjugate mesons
    # have already been classified above and are excluded here.
    exterior_components = [row for row in components if exterior_rank(row.substrate_rep, n) is not None]
    for arity in range(2, n + 1):
        for members in itertools.combinations_with_replacement(exterior_components, arity):
            ranks = tuple(exterior_rank(row.substrate_rep, n) for row in members)
            assert all(rank is not None for rank in ranks)
            reps = tuple(row.substrate_rep for row in members)
            covariant_saturation = sum(int(rank) for rank in ranks) == n
            contravariant_saturation = sum(n - int(rank) for rank in ranks) == n
            if not (covariant_saturation or contravariant_saturation):
                continue
            if arity == 2 and rm.conjugate_rep(reps[0], n) == reps[1]:
                continue
            if arity == n and len(set(reps)) == 1 and reps[0] in {"fund", "antifund"}:
                continue
            rule = "mixed_epsilon_covariant" if covariant_saturation else "mixed_epsilon_contravariant"
            candidate = _token("mixed", n, members, rule)
            if candidate.total_charge == 0:
                tokens[candidate.token_id] = candidate
    return tuple(tokens[key] for key in sorted(tokens))


def distinguishability(candidate: v1.Candidate, catalog: tuple[v1.TypeRow, ...]) -> tuple[bool, int]:
    """Exact canonical representations remain distinct; only true aliases fail."""
    n = candidate.dimensions[-1]
    spellings: dict[str, set[str]] = defaultdict(set)
    for type_id in candidate.combo:
        raw = catalog[type_id].reps[-1]
        spellings[rm.canonical_rep(raw, n)].add(raw)
    ambiguity_count = sum(len(raw_set) - 1 for raw_set in spellings.values())
    return ambiguity_count == 0, ambiguity_count


def branch_scope(branch: v2.ScalarBranch | None, dimensions: tuple[int, ...]) -> str:
    if branch is None:
        return "no_singleton_branch"
    active = v1.active_factor_indices(branch.representative)
    labels = "+".join(f"SU({dimensions[index]})" for index in active)
    return f"singleton_active_{labels}"


def build_evaluations(version2: dict[str, Any]) -> list[Evaluation]:
    base = version2["base"]
    catalogs = base["catalogs"]
    by_structure: dict[str, list[v2.ScalarBranch]] = defaultdict(list)
    for branch in version2["branches"]:
        by_structure[branch.structure_id].append(branch)
    evaluations = []
    serial = 0
    for candidate in base["stage_rows"]["chirality_faithfulness"]:
        dimensions_text = "|".join(map(str, candidate.dimensions))
        structure_id = f"{dimensions_text}::{candidate.support_key}"
        catalog = catalogs[candidate.dimensions]
        components = component_basis(candidate, catalog)
        tokens = neutral_record_tokens(components, candidate.dimensions[-1])
        distinguishable, ambiguity_count = distinguishability(candidate, catalog)
        branches = by_structure.get(structure_id)
        if not branches:
            evaluations.append(Evaluation(
                evaluation_id=f"eval_{serial:03d}", candidate=candidate, branch=None,
                branch_scope=branch_scope(None, candidate.dimensions),
                classification="undefined_no_singleton_branch", stable_substrate=False,
                distinguishability_passes=distinguishable,
                alias_ambiguity_count=ambiguity_count, tokens=tokens,
            ))
            serial += 1
            continue
        for branch in sorted(branches, key=lambda row: row.scalar_branch):
            evaluations.append(Evaluation(
                evaluation_id=f"eval_{serial:03d}", candidate=candidate, branch=branch,
                branch_scope=branch_scope(branch, candidate.dimensions),
                classification="clean_evaluated" if branch.clean else "breaking_evaluated",
                stable_substrate=True, distinguishability_passes=distinguishable,
                alias_ambiguity_count=ambiguity_count, tokens=tokens,
            ))
            serial += 1
    if len(evaluations) != 56:
        raise AssertionError(f"expected 12 branch plus 44 no-branch evaluations, got {len(evaluations)}")
    return evaluations


def score_rows(evaluations: list[Evaluation], threshold: int = PUBLISHED_MIN_RECORD_TOKENS) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        counts = Counter(token.token_class for token in evaluation.tokens)
        rs = evaluation.record_stability_passes(threshold)
        counterexample = bool(rs and evaluation.clean is False)
        rows.append({
            "evaluation_id": evaluation.evaluation_id,
            "dimensions": evaluation.dimensions_text,
            "structure_id": evaluation.structure_id,
            "support_key": evaluation.candidate.support_key,
            "branch_scope": evaluation.branch_scope,
            "scalar_branch": evaluation.scalar_branch,
            "clean_classification": evaluation.classification,
            "stable_substrate": evaluation.stable_substrate,
            "mesonic_token_count": counts["mesonic"],
            "baryonic_token_count": counts["baryonic"],
            "mixed_token_count": counts["mixed"],
            "neutral_record_token_count": len(evaluation.tokens),
            "capacity_threshold": threshold,
            "capacity_passes": evaluation.capacity_passes(threshold),
            "alias_ambiguity_count": evaluation.alias_ambiguity_count,
            "distinguishability_passes": evaluation.distinguishability_passes,
            "record_stability_passes": rs,
            "rs_implies_clean_counterexample": counterexample,
        })
    return rows


def token_rows(evaluations: list[Evaluation]) -> list[dict[str, Any]]:
    rows = []
    for evaluation in evaluations:
        for token in evaluation.tokens:
            rows.append({
                "evaluation_id": evaluation.evaluation_id,
                "dimensions": evaluation.dimensions_text,
                "structure_id": evaluation.structure_id,
                "branch_scope": evaluation.branch_scope,
                "scalar_branch": evaluation.scalar_branch,
                "token_id": token.token_id,
                "token_class": token.token_class,
                "substrate_dimension": token.substrate_dimension,
                "epsilon_or_pair_arity": len(token.component_keys),
                "representation_content": "|".join(token.representation_content),
                "component_basis": " || ".join(token.component_keys),
                "total_charge": token.total_charge,
                "invariant_rule": token.invariant_rule,
            })
    return rows


def grammar_table(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in scores:
        groups[(row["dimensions"], row["branch_scope"], row["clean_classification"])].append(row)
    output = []
    for (dimensions, scope, classification), rows in sorted(groups.items()):
        output.append({
            "dimensions": dimensions,
            "branch_scope": scope,
            "clean_classification": classification,
            "evaluation_count": len(rows),
            "stable_substrate_count": sum(row["stable_substrate"] for row in rows),
            "capacity_pass_count": sum(row["capacity_passes"] for row in rows),
            "distinguishability_pass_count": sum(row["distinguishability_passes"] for row in rows),
            "record_stability_count": sum(row["record_stability_passes"] for row in rows),
            "counterexample_count": sum(row["rs_implies_clean_counterexample"] for row in rows),
            "mesonic_token_count_set": "|".join(map(str, sorted({row["mesonic_token_count"] for row in rows}))),
            "baryonic_token_count_set": "|".join(map(str, sorted({row["baryonic_token_count"] for row in rows}))),
            "mixed_token_count_set": "|".join(map(str, sorted({row["mixed_token_count"] for row in rows}))),
            "total_token_count_set": "|".join(map(str, sorted({row["neutral_record_token_count"] for row in rows}))),
        })
    return output


def structure_quantifier_rows(evaluations: list[Evaluation], threshold: int) -> list[dict[str, Any]]:
    by_structure: dict[str, list[Evaluation]] = defaultdict(list)
    for evaluation in evaluations:
        by_structure[evaluation.structure_id].append(evaluation)
    rows = []
    for structure_id, members in sorted(by_structure.items()):
        branch_members = [row for row in members if row.branch is not None]
        if not branch_members:
            rows.append({
                "threshold": threshold, "dimensions": members[0].dimensions_text,
                "structure_id": structure_id, "branch_domain_size": 0,
                "quantifier_domain": "undefined_no_singleton_branch",
                "rs_branch_count": 0, "clean_branch_count": 0,
                "pointwise_all_rs_imply_clean": "undefined",
                "universal_rs_antecedent": "undefined", "universal_clean_consequent": "undefined",
                "universal_implication": "undefined", "existential_rs_antecedent": "undefined",
                "existential_clean_consequent": "undefined", "existential_implication": "undefined",
            })
            continue
        rs_values = [row.record_stability_passes(threshold) for row in branch_members]
        clean_values = [bool(row.clean) for row in branch_members]
        pointwise = all(not rs or clean for rs, clean in zip(rs_values, clean_values))
        universal_rs = all(rs_values)
        universal_clean = all(clean_values)
        existential_rs = any(rs_values)
        existential_clean = any(clean_values)
        rows.append({
            "threshold": threshold, "dimensions": members[0].dimensions_text,
            "structure_id": structure_id, "branch_domain_size": len(branch_members),
            "quantifier_domain": "evaluated_singleton_branches",
            "rs_branch_count": sum(rs_values), "clean_branch_count": sum(clean_values),
            "pointwise_all_rs_imply_clean": pointwise,
            "universal_rs_antecedent": universal_rs,
            "universal_clean_consequent": universal_clean,
            "universal_implication": (not universal_rs) or universal_clean,
            "existential_rs_antecedent": existential_rs,
            "existential_clean_consequent": existential_clean,
            "existential_implication": (not existential_rs) or existential_clean,
        })
    return rows


def quantifier_summary(evaluations: list[Evaluation], threshold: int) -> list[dict[str, Any]]:
    branch_members = [row for row in evaluations if row.branch is not None]
    structures = structure_quantifier_rows(evaluations, threshold)
    defined = [row for row in structures if row["quantifier_domain"] == "evaluated_singleton_branches"]
    branch_antecedent = [row for row in branch_members if row.record_stability_passes(threshold)]
    branch_counterexamples = [row for row in branch_antecedent if row.clean is False]
    universal_antecedent = [row for row in defined if row["universal_rs_antecedent"]]
    universal_counterexamples = [row for row in universal_antecedent if not row["universal_clean_consequent"]]
    existential_antecedent = [row for row in defined if row["existential_rs_antecedent"]]
    existential_counterexamples = [row for row in existential_antecedent if not row["existential_clean_consequent"]]
    return [
        {"threshold": threshold, "quantifier_reading": "branch_pointwise",
         "domain_count": len(branch_members), "antecedent_count": len(branch_antecedent),
         "counterexample_count": len(branch_counterexamples),
         "implication_passes": not branch_counterexamples,
         "vacuous": not branch_antecedent},
        {"threshold": threshold, "quantifier_reading": "structure_universal",
         "domain_count": len(defined), "antecedent_count": len(universal_antecedent),
         "counterexample_count": len(universal_counterexamples),
         "implication_passes": not universal_counterexamples,
         "vacuous": not universal_antecedent},
        {"threshold": threshold, "quantifier_reading": "structure_existential",
         "domain_count": len(defined), "antecedent_count": len(existential_antecedent),
         "counterexample_count": len(existential_counterexamples),
         "implication_passes": not existential_counterexamples,
         "vacuous": not existential_antecedent},
    ]


def threshold_rows(evaluations: list[Evaluation]) -> list[dict[str, Any]]:
    rows = []
    for threshold in SENSITIVITY_THRESHOLDS:
        branch_members = [row for row in evaluations if row.branch is not None]
        rs = [row for row in branch_members if row.record_stability_passes(threshold)]
        clean_rs = [row for row in rs if row.clean is True]
        breaking_rs = [row for row in rs if row.clean is False]
        family_counts = Counter(row.dimensions_text for row in rs)
        scope_counts = Counter(row.branch_scope for row in rs)
        rows.append({
            "threshold": threshold,
            "branch_domain_count": len(branch_members),
            "rs_branch_count": len(rs),
            "rs_clean_count": len(clean_rs),
            "rs_breaking_count": len(breaking_rs),
            "counterexample_count": len(breaking_rs),
            "rs_family_membership": ";".join(f"{key}:{value}" for key, value in sorted(family_counts.items())),
            "rs_branch_scope_membership": ";".join(f"{key}:{value}" for key, value in sorted(scope_counts.items())),
            "two_by_three_su2_active_rs": sum(
                row.dimensions_text == "2|3" and row.branch_scope == "singleton_active_SU(2)"
                for row in rs
            ),
            "su4_rs": sum(row.dimensions_text == "4" for row in rs),
            "implication_passes": not breaking_rs,
            "vacuous": not rs,
        })
    return rows


def hash_rows(values: Iterable[str]) -> str:
    payload = "\n".join(sorted(values)) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def run_ablation() -> dict[str, Any]:
    version2 = v2.run_v2()
    evaluations = build_evaluations(version2)
    scores = score_rows(evaluations)
    tokens = token_rows(evaluations)
    grammar = grammar_table(scores)
    structures = structure_quantifier_rows(evaluations, PUBLISHED_MIN_RECORD_TOKENS)
    threshold = threshold_rows(evaluations)
    threshold_quantifiers = [
        row for value in SENSITIVITY_THRESHOLDS for row in quantifier_summary(evaluations, value)
    ]

    reference_counterexamples = [row for row in scores if row["rs_implies_clean_counterexample"]]
    if len(reference_counterexamples) != 4:
        raise AssertionError(f"expected four threshold-2 counterexamples, got {len(reference_counterexamples)}")
    if any(row["dimensions"] != "2|3" or row["branch_scope"] != "singleton_active_SU(3)"
           for row in reference_counterexamples):
        raise AssertionError("threshold-2 counterexample family changed")
    if sum(row["record_stability_passes"] and row["branch_scope"] == "singleton_active_SU(2)"
           for row in scores) != 4:
        raise AssertionError("not every 2|3 SU(2)-active branch remains record stable")
    if any(row["record_stability_passes"] and row["dimensions"] != "2|3" for row in scores):
        raise AssertionError("a non-2|3 branch unexpectedly passes threshold 2")
    threshold_one = next(row for row in threshold if row["threshold"] == 1)
    if threshold_one["su4_rs"] != 4 or threshold_one["rs_breaking_count"] != 8:
        raise AssertionError("threshold-1 SU4 counterexample sensitivity changed")

    return {
        "version2": version2,
        "pins": PIN_ROWS,
        "evaluations": evaluations,
        "scores": scores,
        "tokens": tokens,
        "grammar_table": grammar,
        "structure_quantifiers": structures,
        "threshold_sensitivity": threshold,
        "threshold_quantifiers": threshold_quantifiers,
        "counterexamples": reference_counterexamples,
        "hashes": {
            "scores": hash_rows(
                f"{row['evaluation_id']}::{row['scalar_branch']}::{row['record_stability_passes']}"
                for row in scores
            ),
            "tokens": hash_rows(f"{row['evaluation_id']}::{row['token_id']}" for row in tokens),
        },
    }


if __name__ == "__main__":
    result = run_ablation()
    print("record_grammar_ablation.py: PASS: "
          f"evaluations={len(result['scores'])} tokens={len(result['tokens'])} "
          f"RS_t2={sum(row['record_stability_passes'] for row in result['scores'])} "
          f"counterexamples_t2={len(result['counterexamples'])}")
