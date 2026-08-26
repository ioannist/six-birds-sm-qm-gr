#!/usr/bin/env python3
"""S1-REPAIR-3 typed singleton gate, charge census, and scalar-pair appendix."""

from __future__ import annotations

import hashlib
import itertools
import math
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Iterable

import carrier_chain as v1
import carrier_chain_v2 as v2


# Independent declared table.  This gate intentionally does not call the
# production neutral_rep_assignments(), yukawa_invariant(), factor_invariant(),
# scalar_representations(), or representation_model formula functions.
# Partitions are polynomial SU(N) Young diagrams; determinant-height columns
# are removed when representations are compared.
REP_TABLE: dict[int, dict[str, dict[str, Any]]] = {
    2: {
        "singlet": {"partition": (), "dimension": 1, "conjugate": "singlet"},
        "fund": {"partition": (1,), "dimension": 2, "conjugate": "fund"},
        "sym2": {"partition": (2,), "dimension": 3, "conjugate": "sym2"},
    },
    3: {
        "singlet": {"partition": (), "dimension": 1, "conjugate": "singlet"},
        "fund": {"partition": (1,), "dimension": 3, "conjugate": "antifund"},
        "antifund": {"partition": (1, 1), "dimension": 3, "conjugate": "fund"},
        "sym2": {"partition": (2,), "dimension": 6, "conjugate": "conj_sym2"},
        "conj_sym2": {"partition": (2, 2), "dimension": 6, "conjugate": "sym2"},
    },
    4: {
        "singlet": {"partition": (), "dimension": 1, "conjugate": "singlet"},
        "fund": {"partition": (1,), "dimension": 4, "conjugate": "antifund"},
        "antifund": {"partition": (1, 1, 1), "dimension": 4, "conjugate": "fund"},
        "sym2": {"partition": (2,), "dimension": 10, "conjugate": "conj_sym2"},
        "conj_sym2": {"partition": (2, 2, 2), "dimension": 10, "conjugate": "sym2"},
        "antisym2": {"partition": (1, 1), "dimension": 6, "conjugate": "antisym2"},
    },
}
DECLARED_CHARGES = (-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6)
DECLARED_COMPONENT_CAP = 6


@dataclass(frozen=True)
class IndependentScalar:
    dimensions: tuple[int, ...]
    reps: tuple[str, ...]
    charge: int
    component_dim: int

    @property
    def text(self) -> str:
        return f"{'x'.join(self.reps)}:{self.charge}"


@dataclass(frozen=True)
class PairBranch:
    candidate: v1.Candidate
    scalar_a: IndependentScalar
    scalar_b: IndependentScalar
    coverage_mask: int
    shadow: dict[str, Any]

    @property
    def dimensions(self) -> tuple[int, ...]:
        return self.candidate.dimensions

    @property
    def structure_id(self) -> str:
        return f"{'|'.join(map(str, self.dimensions))}::{self.candidate.support_key}"

    @property
    def scalar_a_branch(self) -> str:
        return singleton_branch_key(self.scalar_a)

    @property
    def scalar_b_branch(self) -> str:
        return singleton_branch_key(self.scalar_b)

    @property
    def pair_branch(self) -> str:
        return " + ".join(sorted((self.scalar_a_branch, self.scalar_b_branch)))

    @property
    def clean(self) -> bool:
        return bool(self.shadow["clean_shadow_requirement"] and self.shadow["delta_empty"])


def conjugate_rep(rep: str, n: int) -> str:
    return str(REP_TABLE[n][rep]["conjugate"])


def rep_dimension(rep: str, n: int) -> int:
    return int(REP_TABLE[n][rep]["dimension"])


def independent_rep_assignments(dimensions: tuple[int, ...]) -> tuple[tuple[str, ...], ...]:
    assignments: set[tuple[str, ...]] = {tuple("singlet" for _ in dimensions)}
    for factor_index, n in enumerate(dimensions):
        for rep in REP_TABLE[n]:
            if rep == "singlet":
                continue
            row = ["singlet" for _ in dimensions]
            row[factor_index] = rep
            assignments.add(tuple(row))
    if len(dimensions) == 2:
        left = tuple(rep for rep in ("fund", "antifund") if rep in REP_TABLE[dimensions[0]])
        right = tuple(rep for rep in ("fund", "antifund") if rep in REP_TABLE[dimensions[1]])
        # SU(2) fund is pseudoreal, so the declared table contains no alias row.
        if dimensions[0] == 2:
            left = ("fund",)
        if dimensions[1] == 2:
            right = ("fund",)
        assignments.update(itertools.product(left, right))
    return tuple(sorted(assignments))


def independent_scalar_alphabet(dimensions: tuple[int, ...]) -> tuple[IndependentScalar, ...]:
    rows = []
    for reps in independent_rep_assignments(dimensions):
        component_dim = math.prod(rep_dimension(rep, n) for rep, n in zip(reps, dimensions))
        if component_dim > DECLARED_COMPONENT_CAP:
            continue
        for charge in DECLARED_CHARGES:
            if charge == 0 and all(rep == "singlet" for rep in reps):
                continue
            rows.append(IndependentScalar(dimensions, reps, charge, component_dim))
    return tuple(rows)


def conjugate_scalar(scalar: IndependentScalar) -> IndependentScalar:
    return IndependentScalar(
        scalar.dimensions,
        tuple(conjugate_rep(rep, n) for rep, n in zip(scalar.reps, scalar.dimensions)),
        -scalar.charge,
        scalar.component_dim,
    )


def scalar_signature(scalar: IndependentScalar) -> tuple[tuple[str, ...], int]:
    return scalar.reps, scalar.charge


def signature_text(signature: tuple[tuple[str, ...], int]) -> str:
    return f"{'x'.join(signature[0])}:{signature[1]}"


def singleton_branch_key(scalar: IndependentScalar) -> str:
    signature = scalar_signature(scalar)
    conjugate = scalar_signature(conjugate_scalar(scalar))
    return " <> ".join(sorted((signature_text(signature), signature_text(conjugate))))


def independent_scalar_branch_representatives(
    dimensions: tuple[int, ...],
) -> tuple[IndependentScalar, ...]:
    by_key: dict[str, IndependentScalar] = {}
    for scalar in independent_scalar_alphabet(dimensions):
        representative = min((scalar, conjugate_scalar(scalar)), key=lambda item: item.text)
        by_key.setdefault(singleton_branch_key(representative), representative)
    return tuple(by_key[key] for key in sorted(by_key))


@lru_cache(maxsize=None)
def littlewood_richardson_coefficient(
    lam: tuple[int, ...], mu: tuple[int, ...], nu: tuple[int, ...]
) -> int:
    """Count LR tableaux of skew shape nu/lam and content mu exactly."""
    row_count = max(len(lam), len(nu))
    padded_lam = lam + (0,) * (row_count - len(lam))
    padded_nu = nu + (0,) * (row_count - len(nu))
    if any(left > right for left, right in zip(padded_lam, padded_nu)):
        return 0
    if sum(padded_nu) - sum(padded_lam) != sum(mu):
        return 0
    boxes = [
        (row, column)
        for row in range(row_count)
        for column in range(padded_nu[row] - 1, padded_lam[row] - 1, -1)
    ]
    values: dict[tuple[int, int], int] = {}
    used = [0] * len(mu)
    total = 0

    def visit(index: int) -> None:
        nonlocal total
        if index == len(boxes):
            total += 1
            return
        row, column = boxes[index]
        for entry in range(1, len(mu) + 1):
            if used[entry - 1] >= mu[entry - 1]:
                continue
            right = values.get((row, column + 1))
            above = values.get((row - 1, column))
            if right is not None and entry > right:
                continue
            if above is not None and entry <= above:
                continue
            used[entry - 1] += 1
            if all(used[position] >= used[position + 1] for position in range(len(used) - 1)):
                values[(row, column)] = entry
                visit(index + 1)
                del values[(row, column)]
            used[entry - 1] -= 1

    visit(0)
    return total


@lru_cache(maxsize=None)
def singlet_decomposition(rep_a: str, rep_b: str, rep_c: str, n: int) -> tuple[int, int, tuple[int, ...]]:
    """Return singlet multiplicity and the exact determinant-shifted target diagram."""
    lam = tuple(REP_TABLE[n][rep_a]["partition"])
    mu = tuple(REP_TABLE[n][rep_b]["partition"])
    target = tuple(REP_TABLE[n][conjugate_rep(rep_c, n)]["partition"])
    difference = sum(lam) + sum(mu) - sum(target)
    if difference < 0 or difference % n:
        return 0, -1, ()
    determinant_shift = difference // n
    nu = tuple(
        (target[index] if index < len(target) else 0) + determinant_shift
        for index in range(n)
    )
    while nu and nu[-1] == 0:
        nu = nu[:-1]
    return littlewood_richardson_coefficient(lam, mu, nu), determinant_shift, nu


def tensor_gate_rows() -> list[dict[str, Any]]:
    rows = []
    for n, table in REP_TABLE.items():
        for rep_a, rep_b, rep_c in itertools.product(table, repeat=3):
            multiplicity, shift, target = singlet_decomposition(rep_a, rep_b, rep_c, n)
            rows.append({
                "dimension": n,
                "rep_a": rep_a,
                "rep_b": rep_b,
                "rep_c": rep_c,
                "conjugate_c_partition": str(tuple(table[conjugate_rep(rep_c, n)]["partition"])),
                "determinant_column_shift": shift,
                "lr_target_partition": str(target),
                "singlet_multiplicity": multiplicity,
            })
    return rows


def tensor_golden_rows() -> list[dict[str, Any]]:
    # Known small decompositions: 2x2=1+3; 3x3=6+3bar;
    # 4x4=10+6, plus conjugate-pair and cubic-invariant checks.
    known = (
        (2, "fund", "fund", "singlet", 1),
        (2, "fund", "fund", "sym2", 1),
        (2, "sym2", "sym2", "sym2", 1),
        (2, "fund", "sym2", "singlet", 0),
        (3, "fund", "antifund", "singlet", 1),
        (3, "fund", "fund", "fund", 1),
        (3, "antifund", "antifund", "antifund", 1),
        (3, "sym2", "antifund", "antifund", 1),
        (3, "sym2", "sym2", "sym2", 1),
        (4, "fund", "antifund", "singlet", 1),
        (4, "fund", "fund", "conj_sym2", 1),
        (4, "fund", "fund", "antisym2", 1),
        (4, "antisym2", "antisym2", "singlet", 1),
        (4, "sym2", "sym2", "sym2", 0),
    )
    rows = []
    for n, rep_a, rep_b, rep_c, expected in known:
        actual = singlet_decomposition(rep_a, rep_b, rep_c, n)[0]
        rows.append({"dimension": n, "rep_a": rep_a, "rep_b": rep_b, "rep_c": rep_c,
                     "expected_singlet_multiplicity": expected,
                     "actual_singlet_multiplicity": actual, "passes": actual == expected})
    if not all(row["passes"] for row in rows):
        raise AssertionError("independent tensor-product golden table failed")
    return rows


def independent_yukawa_allowed(left: v1.TypeRow, right: v1.TypeRow,
                               scalar: IndependentScalar) -> bool:
    return left.charge + right.charge + scalar.charge == 0 and all(
        singlet_decomposition(rep_a, rep_b, rep_c, n)[0] > 0
        for rep_a, rep_b, rep_c, n in zip(left.reps, right.reps, scalar.reps, left.dimensions)
    )


def scalar_coverage_mask(candidate: v1.Candidate, catalog: tuple[v1.TypeRow, ...],
                         scalar: IndependentScalar) -> int:
    occurrences = [catalog[type_id] for type_id in candidate.combo]
    orientations = (scalar, conjugate_scalar(scalar))
    mask = 0
    for left_index, left in enumerate(occurrences):
        for right_index, right in enumerate(occurrences):
            if left_index == right_index and len(occurrences) > 1:
                continue
            if any(independent_yukawa_allowed(left, right, orientation) for orientation in orientations):
                mask |= 1 << left_index
                break
    return mask


def jointly_breaks(pair: tuple[IndependentScalar, IndependentScalar]) -> bool:
    has_nonzero_charge = any(scalar.charge != 0 for scalar in pair)
    has_nonabelian_action = any(
        rep != "singlet"
        for scalar in pair
        for rep in scalar.reps
    )
    return has_nonzero_charge and has_nonabelian_action


def pair_shadow(candidate: v1.Candidate, catalog: tuple[v1.TypeRow, ...],
                pair: tuple[IndependentScalar, IndependentScalar]) -> dict[str, Any]:
    carrier_active = {
        factor_index
        for type_id in candidate.combo
        for factor_index, rep in enumerate(catalog[type_id].reps)
        if rep != "singlet"
    }
    scalar_active = {
        factor_index
        for scalar in pair
        for factor_index, rep in enumerate(scalar.reps)
        if rep != "singlet"
    }
    unbroken = []
    broken_vector_exotic_count = 0
    for factor_index, n in enumerate(candidate.dimensions):
        if factor_index not in carrier_active:
            continue
        if factor_index in scalar_active:
            # This is the inherited low-energy proxy applied jointly: every
            # admitted nontrivial alphabet rep has residual-rank label N-1.
            residual = n - 1
            if residual >= 2:
                unbroken.append(residual)
                broken_vector_exotic_count += 2 * residual
        else:
            unbroken.append(n)
    confining = tuple(sorted(value for value in unbroken if value >= 2))
    if confining:
        conf_generators = max(confining) ** 2 - 1
        delta_pair_count = conf_generators * broken_vector_exotic_count
    else:
        delta_pair_count = 0
    clean_shadow = bool(confining) and broken_vector_exotic_count == 0
    return {
        "active_factor_indices": tuple(sorted(scalar_active)),
        "unbroken_nonabelian_subgroups": tuple(sorted(unbroken)),
        "confining_subgroups": confining,
        "broken_vector_exotic_count": broken_vector_exotic_count,
        "delta_pair_count": delta_pair_count,
        "delta_empty": delta_pair_count == 0,
        "clean_shadow_requirement": clean_shadow,
    }


def enumerate_pair_branches(
    faithful_rows: Iterable[v1.Candidate],
    catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]],
) -> list[PairBranch]:
    pools = {dimensions: independent_scalar_branch_representatives(dimensions) for dimensions in catalogs}
    branches = []
    for candidate in faithful_rows:
        catalog = catalogs[candidate.dimensions]
        pool = pools[candidate.dimensions]
        masks = {scalar: scalar_coverage_mask(candidate, catalog, scalar) for scalar in pool}
        full_mask = (1 << len(candidate.combo)) - 1
        for scalar_a, scalar_b in itertools.combinations_with_replacement(pool, 2):
            pair = (scalar_a, scalar_b)
            coverage = masks[scalar_a] | masks[scalar_b]
            if coverage != full_mask or not jointly_breaks(pair):
                continue
            branches.append(PairBranch(candidate, scalar_a, scalar_b, coverage,
                                       pair_shadow(candidate, catalog, pair)))
    return sorted(branches, key=lambda row: (row.dimensions, row.candidate.support_key, row.pair_branch))


def independent_singleton_branch_keys(
    faithful_rows: Iterable[v1.Candidate],
    catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]],
) -> set[tuple[str, str]]:
    keys = set()
    for candidate in faithful_rows:
        catalog = catalogs[candidate.dimensions]
        full_mask = (1 << len(candidate.combo)) - 1
        for scalar in independent_scalar_branch_representatives(candidate.dimensions):
            if scalar_coverage_mask(candidate, catalog, scalar) != full_mask:
                continue
            if not jointly_breaks((scalar, scalar)):
                continue
            structure_id = f"{'|'.join(map(str, candidate.dimensions))}::{candidate.support_key}"
            keys.add((structure_id, singleton_branch_key(scalar)))
    return keys


def primitive_normalized_signatures(
    signatures: Iterable[tuple[tuple[str, ...], int]],
) -> tuple[tuple[tuple[str, ...], int], ...]:
    values = tuple(signatures)
    nonzero = [abs(charge) for _, charge in values if charge]
    divisor = math.gcd(*nonzero) if nonzero else 1
    return tuple((reps, charge // divisor) for reps, charge in values)


def primitive_candidate_orbit_key(candidate: v1.Candidate, catalog: tuple[v1.TypeRow, ...]) -> str:
    signatures = v2.candidate_signatures(candidate, catalog)
    images = []
    for spec in v2.transformation_specs(candidate.dimensions):
        transformed = [v2.transform_signature(signature, candidate.dimensions, spec)
                       for signature in signatures]
        normalized = primitive_normalized_signatures(transformed)
        images.append(v2.content_text_from_signatures(normalized))
    return f"{'|'.join(map(str, candidate.dimensions))}::{min(images)}"


def charge_normalization_census(base: dict[str, Any]) -> list[dict[str, Any]]:
    stages = ("genuinely_chiral", "atomic_packaging", "closure_consistency", "chirality_faithfulness")
    rows = []
    previous = None
    first = None
    for stage in stages:
        candidates = base["stage_rows"][stage]
        labelled = len(candidates)
        declared = len({v2.candidate_orbit_key(row, base["catalogs"][row.dimensions]) for row in candidates})
        primitive = len({primitive_candidate_orbit_key(row, base["catalogs"][row.dimensions]) for row in candidates})
        counts = (labelled, declared, primitive)
        if first is None:
            first = counts
        input_counts = counts if previous is None else previous
        rows.append({
            "stage": stage,
            "labelled_count": labelled,
            "declared_orbit_count": declared,
            "primitive_normalized_orbit_count": primitive,
            "labelled_stage_exclusion_percent": percent(input_counts[0], labelled),
            "declared_orbit_stage_exclusion_percent": percent(input_counts[1], declared),
            "primitive_stage_exclusion_percent": percent(input_counts[2], primitive),
            "labelled_cumulative_exclusion_percent": percent(first[0], labelled),
            "declared_orbit_cumulative_exclusion_percent": percent(first[1], declared),
            "primitive_cumulative_exclusion_percent": percent(first[2], primitive),
        })
        previous = counts
    expected = [(1066, 419, 195), (84, 37, 37), (62, 27, 27), (52, 24, 24)]
    actual = [(row["labelled_count"], row["declared_orbit_count"],
               row["primitive_normalized_orbit_count"]) for row in rows]
    if actual != expected:
        raise AssertionError(f"charge-normalization census changed: {actual}")
    return rows


def percent(input_count: int, output_count: int) -> str:
    if not input_count:
        return ""
    return f"{100 * (input_count - output_count) / input_count:.6f}"


def pair_orbit_key(branch: PairBranch, catalog: tuple[v1.TypeRow, ...]) -> str:
    content = v2.candidate_signatures(branch.candidate, catalog)
    scalar_signatures = (scalar_signature(branch.scalar_a), scalar_signature(branch.scalar_b))
    images = []
    for spec in v2.transformation_specs(branch.dimensions):
        transformed_content = v2.content_text_from_signatures(
            v2.transform_signature(signature, branch.dimensions, spec) for signature in content
        )
        transformed_branches = []
        for signature in scalar_signatures:
            transformed = v2.transform_signature(signature, branch.dimensions, spec)
            conjugate = (tuple(conjugate_rep(rep, n) for rep, n in zip(transformed[0], branch.dimensions)),
                         -transformed[1])
            transformed_branches.append(" <> ".join(sorted((signature_text(transformed), signature_text(conjugate)))))
        images.append(f"{transformed_content}::{' + '.join(sorted(transformed_branches))}")
    return f"{'|'.join(map(str, branch.dimensions))}::{min(images)}"


def hash_values(values: Iterable[str]) -> str:
    payload = "\n".join(sorted(values)) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def run_v3() -> dict[str, Any]:
    version2 = v2.run_v2()
    base = version2["base"]
    faithful = base["stage_rows"]["chirality_faithfulness"]
    catalogs = base["catalogs"]

    alphabet_rows = []
    for dimensions in v1.factor_structures():
        alphabet = independent_scalar_alphabet(dimensions)
        representatives = independent_scalar_branch_representatives(dimensions)
        conjugate_closed = all(conjugate_scalar(row) in alphabet for row in alphabet)
        alphabet_rows.append({
            "dimensions": "|".join(map(str, dimensions)),
            "declared_rep_assignment_count": len(independent_rep_assignments(dimensions)),
            "cap_filtered_scalar_count": len(alphabet),
            "scalar_conjugacy_branch_count": len(representatives),
            "component_cap_per_scalar": DECLARED_COMPONENT_CAP,
            "charge_count": len(DECLARED_CHARGES),
            "conjugation_closed": conjugate_closed,
        })
    if not all(row["conjugation_closed"] for row in alphabet_rows):
        raise AssertionError("independent scalar alphabet is not conjugation closed")

    exact_singleton = independent_singleton_branch_keys(faithful, catalogs)
    production_singleton = {(row.structure_id, row.scalar_branch) for row in version2["branches"]}
    if exact_singleton != production_singleton:
        raise AssertionError(
            f"independent singleton gate differs: missing={sorted(exact_singleton-production_singleton)} "
            f"extra={sorted(production_singleton-exact_singleton)}"
        )
    tensor_rows = tensor_gate_rows()
    tensor_golden = tensor_golden_rows()
    for row in tensor_rows:
        permutations = set(itertools.permutations((row["rep_a"], row["rep_b"], row["rep_c"])))
        multiplicities = {singlet_decomposition(*permutation, row["dimension"])[0]
                          for permutation in permutations}
        if len(multiplicities) != 1:
            raise AssertionError(f"singlet multiplicity is not permutation invariant: {row}")

    pairs = enumerate_pair_branches(faithful, catalogs)
    clean_pairs = [row for row in pairs if row.clean]
    singleton_structures = {structure_id for structure_id, _ in exact_singleton}
    pair_structures = {row.structure_id for row in pairs}
    newly_admissible = pair_structures - singleton_structures
    if len(pairs) != 2824 or len(pair_structures) != 52 or len(newly_admissible) != 44:
        raise AssertionError(
            f"unexpected pair census: pairs={len(pairs)} structures={len(pair_structures)} "
            f"new={len(newly_admissible)}"
        )
    if len(clean_pairs) != 68:
        raise AssertionError(f"unexpected clean pair count: {len(clean_pairs)}")
    if any(row.dimensions != (2, 3) or row.shadow["active_factor_indices"] != (0,)
           for row in clean_pairs):
        raise AssertionError("a clean pair lies outside 2|3 with SU(2)-only scalar action")

    charge_rows = charge_normalization_census(base)
    pair_orbits = len({pair_orbit_key(row, catalogs[row.dimensions]) for row in pairs})
    clean_pair_orbits = len({pair_orbit_key(row, catalogs[row.dimensions]) for row in clean_pairs})
    return {
        "version2": version2,
        "alphabet_rows": alphabet_rows,
        "tensor_rows": tensor_rows,
        "tensor_golden_rows": tensor_golden,
        "exact_singleton_keys": exact_singleton,
        "charge_census": charge_rows,
        "pair_branches": pairs,
        "clean_pair_branches": clean_pairs,
        "singleton_structures": singleton_structures,
        "pair_structures": pair_structures,
        "newly_pair_admissible_structures": newly_admissible,
        "pair_branch_orbits": pair_orbits,
        "clean_pair_branch_orbits": clean_pair_orbits,
        "hashes": {
            "singleton_gate": hash_values(f"{structure}::{branch}" for structure, branch in exact_singleton),
            "pair_branches": hash_values(f"{row.structure_id}::{row.pair_branch}" for row in pairs),
            "clean_pair_branches": hash_values(f"{row.structure_id}::{row.pair_branch}" for row in clean_pairs),
        },
    }


if __name__ == "__main__":
    result = run_v3()
    print("carrier_chain_v3.py: PASS: "
          f"singleton_gate={len(result['exact_singleton_keys'])} "
          f"pair_branches={len(result['pair_branches'])} "
          f"pair_structures={len(result['pair_structures'])} "
          f"new_pair_structures={len(result['newly_pair_admissible_structures'])} "
          f"clean_pairs={len(result['clean_pair_branches'])}")
