#!/usr/bin/env python3
"""S1-REPAIR-2 conventions, quotienting, and branch-complete scalar chain."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from dataclasses import dataclass, replace
from typing import Any, Iterable

import carrier_chain as v1
import representation_model as rm


@dataclass(frozen=True)
class ScalarBranch:
    dimensions: tuple[int, ...]
    candidate: v1.Candidate
    representative: v1.ScalarRep
    conjugate: v1.ScalarRep
    completion: dict[str, Any]
    shadow: dict[str, Any]

    @property
    def structure_id(self) -> str:
        return f"{'|'.join(map(str, self.dimensions))}::{self.candidate.support_key}"

    @property
    def scalar_branch(self) -> str:
        return scalar_branch_key(self.representative)

    @property
    def clean(self) -> bool:
        return bool(self.shadow["clean_shadow_requirement"] and self.shadow["delta_empty"])


def golden_formula_rows() -> list[dict[str, Any]]:
    """Independent known-value table; values are intentionally not formula-generated.

    Source: R. Slansky, "Group Theory for Unified Model Building",
    Physics Reports 79 (1981) 1-128, doi:10.1016/0370-1573(81)90092-2,
    SU(N) representation tables.  Normalizations are A(fund)=1 and 2T(fund)=1.
    SU(2) cubic entries additionally use pseudoreality (all local cubic anomalies zero).
    """
    known = (
        (2, "singlet", 1, 0, 0),
        (2, "fund", 2, 1, 0),
        (2, "sym2", 3, 4, 0),
        (3, "fund", 3, 1, 1),
        (3, "antifund", 3, 1, -1),
        (3, "sym2", 6, 5, 7),
        (3, "conj_sym2", 6, 5, -7),
        (3, "antisym2", 3, 1, -1),
        (4, "fund", 4, 1, 1),
        (4, "antifund", 4, 1, -1),
        (4, "sym2", 10, 6, 8),
        (4, "conj_sym2", 10, 6, -8),
        (4, "antisym2", 6, 2, 0),
    )
    rows = []
    for n, rep, expected_dim, expected_dynkin, expected_cubic in known:
        actual = (rm.rep_dim(rep, n), rm.dynkin_twice(rep, n), rm.cubic_anomaly(rep, n))
        expected = (expected_dim, expected_dynkin, expected_cubic)
        rows.append({
            "dimension": n,
            "rep": rep,
            "expected_dim": expected_dim,
            "actual_dim": actual[0],
            "expected_2T": expected_dynkin,
            "actual_2T": actual[1],
            "expected_A": expected_cubic,
            "actual_A": actual[2],
            "passes": actual == expected,
        })
    if not all(row["passes"] for row in rows):
        raise AssertionError("representation model failed the independent golden-value table")
    return rows


def neutral_singlet_key(dimensions: tuple[int, ...]) -> tuple[tuple[str, ...], int]:
    return tuple("singlet" for _ in dimensions), 0


def catalog_with_inert_singlet(
    dimensions: tuple[int, ...], rows: tuple[v1.TypeRow, ...]
) -> tuple[v1.TypeRow, ...]:
    inert = v1.TypeRow(
        type_id=0,
        dimensions=dimensions,
        reps=neutral_singlet_key(dimensions)[0],
        charge=0,
        component_dim=1,
        anomaly_vector=tuple(0 for _ in rows[0].anomaly_vector),
        witten_mask=0,
    )
    return (inert,) + tuple(replace(row, type_id=row.type_id + 1) for row in rows)


def normalized_support_from_combo(combo: tuple[int, ...], rows: tuple[v1.TypeRow, ...]) -> str:
    inert_key = neutral_singlet_key(rows[0].dimensions)
    fields = [rows[type_id] for type_id in combo if rows[type_id].key != inert_key]
    return " + ".join(sorted(f"{'x'.join(row.reps)}:{row.charge}" for row in fields))


def inert_singlet_convention_check(
    catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]], base_chiral: list[v1.Candidate]
) -> dict[str, Any]:
    base_keys = {(row.dimensions, row.support_key) for row in base_chiral}
    padded_count = 0
    normalized_keys: set[tuple[tuple[int, ...], str]] = set()
    rows = []
    for dimensions, catalog in catalogs.items():
        padded_catalog = catalog_with_inert_singlet(dimensions, catalog)
        padded_survivors, _ = v1.enumerate_structure_chiral(dimensions, padded_catalog)
        normalized = {(dimensions, normalized_support_from_combo(row.combo, padded_catalog))
                      for row in padded_survivors}
        padded_count += len(padded_survivors)
        normalized_keys.update(normalized)
        expected = {(d, support) for d, support in base_keys if d == dimensions}
        rows.append({
            "dimensions": "|".join(map(str, dimensions)),
            "labelled_with_inert_padding": len(padded_survivors),
            "modulo_inert_singlets": len(normalized),
            "unpadded_reference_count": len(expected),
            "normalized_sets_equal": normalized == expected,
        })
    if padded_count != 1578:
        raise AssertionError(f"unexpected inert-singlet-inclusive count: {padded_count}")
    if normalized_keys != base_keys:
        raise AssertionError("inert-singlet quotient does not recover the 1,066-row carrier")
    if not all(row["normalized_sets_equal"] for row in rows):
        raise AssertionError("a padded family failed canonical normalization")
    return {
        "rows": rows,
        "labelled_with_inert_padding": padded_count,
        "modulo_inert_singlets": len(normalized_keys),
        "all_padded_variants_map_to_unpadded_carrier": True,
    }


def scalar_signature(scalar: v1.ScalarRep) -> tuple[tuple[str, ...], int]:
    return scalar.reps, scalar.charge


def scalar_text(signature: tuple[tuple[str, ...], int]) -> str:
    reps, charge = signature
    return f"{'x'.join(reps)}:{charge}"


def conjugate_scalar_signature(
    signature: tuple[tuple[str, ...], int], dimensions: tuple[int, ...]
) -> tuple[tuple[str, ...], int]:
    reps, charge = signature
    return tuple(rm.conjugate_rep(rep, n) for rep, n in zip(reps, dimensions)), -charge


def scalar_branch_key(scalar: v1.ScalarRep) -> str:
    signature = scalar_signature(scalar)
    conjugate = conjugate_scalar_signature(signature, scalar.dimensions)
    return " <> ".join(sorted((scalar_text(signature), scalar_text(conjugate))))


def _shadow_with_delta(
    combo: tuple[int, ...], type_rows: tuple[v1.TypeRow, ...], scalar: v1.ScalarRep
) -> dict[str, Any]:
    shadow = v1.low_energy_shadow(combo, type_rows, scalar)
    confining = shadow["confining_subgroups"]
    if confining:
        pairs, witnesses = v1.delta_counts(
            scalar.dimensions, max(confining), shadow["broken_vector_exotic_count"]
        )
    else:
        pairs = witnesses = 0
    return {
        **shadow,
        "delta_pair_count": pairs,
        "delta_witness_count": witnesses,
        "delta_empty": pairs == 0,
        "step38_step41_faithful": (pairs == 0) == shadow["clean_shadow_requirement"],
    }


def enumerate_admissible_scalar_branches(
    faithful_rows: Iterable[v1.Candidate],
    catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]],
) -> list[ScalarBranch]:
    scalar_cache = {dimensions: v1.scalar_representations(dimensions) for dimensions in catalogs}
    branches: list[ScalarBranch] = []
    for candidate in faithful_rows:
        catalog = catalogs[candidate.dimensions]
        seen: set[str] = set()
        for scalar in scalar_cache[candidate.dimensions]:
            completion = v1.mass_completion(candidate.combo, catalog, scalar)
            if not completion["mass_completable"] or not v1.scalar_breaks_to_unbroken_u1(scalar):
                continue
            branch_key = scalar_branch_key(scalar)
            if branch_key in seen:
                continue
            seen.add(branch_key)
            conjugate = v1.conjugate_scalar(scalar)
            representative = min((scalar, conjugate), key=lambda item: item.text)
            conjugate = v1.conjugate_scalar(representative)
            shadow = _shadow_with_delta(candidate.combo, catalog, representative)
            # A scalar and its conjugate must define the same low-energy census.
            conjugate_shadow = _shadow_with_delta(candidate.combo, catalog, conjugate)
            invariant_fields = ("unbroken_nonabelian_subgroups", "confining_subgroups",
                                "broken_vector_exotic_count", "delta_pair_count", "delta_empty")
            if any(shadow[field] != conjugate_shadow[field] for field in invariant_fields):
                raise AssertionError(f"scalar-conjugate branch disagreement: {branch_key}")
            branches.append(ScalarBranch(candidate.dimensions, candidate, representative, conjugate,
                                         completion, shadow))
    return sorted(branches, key=lambda row: (row.dimensions, row.candidate.support_key, row.scalar_branch))


def independently_enumerated_branch_keys(
    faithful_rows: Iterable[v1.Candidate],
    catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]],
) -> set[tuple[str, str]]:
    """Second scalar inventory/coverage loop, independent of scalar_representations/mass_completion."""
    found: set[tuple[str, str]] = set()
    for candidate in faithful_rows:
        dimensions = candidate.dimensions
        catalog = catalogs[dimensions]
        occurrences = [catalog[type_id] for type_id in candidate.combo]
        for reps in v1.neutral_rep_assignments(dimensions):
            component_dim = math.prod(rm.rep_dim(rep, n) for rep, n in zip(reps, dimensions))
            if component_dim > v1.COMPONENT_CAP:
                continue
            for charge in v1.CHARGE_UNITS:
                if charge == 0 and all(rep == "singlet" for rep in reps):
                    continue
                scalar = v1.ScalarRep(-1, dimensions, reps, charge, component_dim)
                if charge == 0 or not any(v1.action_active(rep, n) for rep, n in zip(reps, dimensions)):
                    continue
                orientations = (scalar, v1.conjugate_scalar(scalar))
                covered = []
                for left_index, left in enumerate(occurrences):
                    hit = False
                    for right_index, right in enumerate(occurrences):
                        if left_index == right_index and len(occurrences) > 1:
                            continue
                        if any(v1.yukawa_invariant(left, right, orientation) for orientation in orientations):
                            hit = True
                            break
                    covered.append(hit)
                if all(covered):
                    structure_id = f"{'|'.join(map(str, dimensions))}::{candidate.support_key}"
                    found.add((structure_id, scalar_branch_key(scalar)))
    return found


def branch_completeness_check(
    branches: list[ScalarBranch], faithful_rows: Iterable[v1.Candidate],
    catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]],
) -> dict[str, Any]:
    primary = {(row.structure_id, row.scalar_branch) for row in branches}
    independent = independently_enumerated_branch_keys(faithful_rows, catalogs)
    if primary != independent:
        missing = sorted(independent - primary)
        extra = sorted(primary - independent)
        raise AssertionError(f"scalar branch table incomplete: missing={missing} extra={extra}")
    return {"primary_count": len(primary), "independent_count": len(independent),
            "sets_equal": True, "missing_count": 0, "extra_count": 0}


def transformation_specs(dimensions: tuple[int, ...]) -> tuple[tuple[bool, bool, bool], ...]:
    swaps = (False, True) if len(dimensions) == 2 and dimensions[0] == dimensions[1] else (False,)
    return tuple(itertools.product(swaps, (False, True), (False, True)))


def transform_signature(
    signature: tuple[tuple[str, ...], int], dimensions: tuple[int, ...],
    spec: tuple[bool, bool, bool],
) -> tuple[tuple[str, ...], int]:
    swap, conjugate_reps, invert_u1 = spec
    reps, charge = signature
    transformed = tuple(rm.conjugate_rep(rep, n) if conjugate_reps else rep
                        for rep, n in zip(reps, dimensions))
    if swap:
        transformed = tuple(reversed(transformed))
    return transformed, -charge if invert_u1 else charge


def content_text_from_signatures(signatures: Iterable[tuple[tuple[str, ...], int]]) -> str:
    return " + ".join(sorted(scalar_text(signature) for signature in signatures))


def candidate_signatures(candidate: v1.Candidate, catalog: tuple[v1.TypeRow, ...]) -> tuple[tuple[tuple[str, ...], int], ...]:
    return tuple(catalog[type_id].key for type_id in candidate.combo)


def candidate_orbit_key(candidate: v1.Candidate, catalog: tuple[v1.TypeRow, ...]) -> str:
    signatures = candidate_signatures(candidate, catalog)
    images = []
    for spec in transformation_specs(candidate.dimensions):
        transformed = [transform_signature(signature, candidate.dimensions, spec) for signature in signatures]
        images.append(content_text_from_signatures(transformed))
    return f"{'|'.join(map(str, candidate.dimensions))}::{min(images)}"


def branch_orbit_key(branch: ScalarBranch, catalog: tuple[v1.TypeRow, ...]) -> str:
    signatures = candidate_signatures(branch.candidate, catalog)
    scalar = scalar_signature(branch.representative)
    images = []
    for spec in transformation_specs(branch.dimensions):
        transformed_content = content_text_from_signatures(
            transform_signature(signature, branch.dimensions, spec) for signature in signatures
        )
        transformed_scalar = transform_signature(scalar, branch.dimensions, spec)
        transformed_conjugate = conjugate_scalar_signature(transformed_scalar, branch.dimensions)
        scalar_orbit = " <> ".join(sorted((scalar_text(transformed_scalar), scalar_text(transformed_conjugate))))
        images.append(f"{transformed_content}::{scalar_orbit}")
    return f"{'|'.join(map(str, branch.dimensions))}::{min(images)}"


def effective_type_permutations(
    dimensions: tuple[int, ...], catalog: tuple[v1.TypeRow, ...]
) -> tuple[tuple[int, ...], ...]:
    index = {row.key: row.type_id for row in catalog}
    permutations = set()
    for spec in transformation_specs(dimensions):
        image = tuple(index[transform_signature(row.key, dimensions, spec)] for row in catalog)
        permutations.add(image)
    return tuple(sorted(permutations))


def fixed_multisets_through_cap(permutation: tuple[int, ...], cap: int) -> int:
    unseen = set(range(len(permutation)))
    cycles = []
    while unseen:
        start = min(unseen)
        node = start
        length = 0
        while node in unseen:
            unseen.remove(node)
            node = permutation[node]
            length += 1
        cycles.append(length)
    coefficients = [0] * (cap + 1)
    coefficients[0] = 1
    for length in cycles:
        updated = coefficients[:]
        for degree in range(cap + 1):
            if not coefficients[degree]:
                continue
            for multiplicity in range(1, (cap - degree) // length + 1):
                updated[degree + multiplicity * length] += coefficients[degree]
        coefficients = updated
    return sum(coefficients[1:])


def neutral_orbit_count(catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]]) -> tuple[int, list[dict[str, Any]]]:
    rows = []
    total = 0
    for dimensions, catalog in catalogs.items():
        group = effective_type_permutations(dimensions, catalog)
        fixed_sum = sum(fixed_multisets_through_cap(permutation, v1.MAX_FIELDS) for permutation in group)
        if fixed_sum % len(group):
            raise AssertionError("Burnside average is not integral")
        orbit_count = fixed_sum // len(group)
        labelled = sum(math.comb(len(catalog) + size - 1, size) for size in range(1, v1.MAX_FIELDS + 1))
        rows.append({"dimensions": "|".join(map(str, dimensions)), "labelled_count": labelled,
                     "effective_group_order": len(group), "orbit_count": orbit_count})
        total += orbit_count
    return total, rows


def materialized_orbit_count(
    rows: Iterable[v1.Candidate], catalogs: dict[tuple[int, ...], tuple[v1.TypeRow, ...]],
    require_closed: bool = True,
) -> int:
    candidates = list(rows)
    keys = {("|".join(map(str, row.dimensions)), row.support_key) for row in candidates}
    if require_closed:
        for row in candidates:
            signatures = candidate_signatures(row, catalogs[row.dimensions])
            for spec in transformation_specs(row.dimensions):
                image = content_text_from_signatures(
                    transform_signature(signature, row.dimensions, spec) for signature in signatures
                )
                if ("|".join(map(str, row.dimensions)), image) not in keys:
                    raise AssertionError(f"stage is not closed under declared quotient: {row.support_key} -> {image}")
    return len({candidate_orbit_key(row, catalogs[row.dimensions]) for row in candidates})


def hash_rows(values: Iterable[str]) -> str:
    payload = "\n".join(sorted(values)) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def run_v2() -> dict[str, Any]:
    base = v1.run_chain()
    catalogs = base["catalogs"]
    golden = golden_formula_rows()
    inert = inert_singlet_convention_check(catalogs, base["stage_rows"]["genuinely_chiral"])
    faithful = base["stage_rows"]["chirality_faithfulness"]
    branches = enumerate_admissible_scalar_branches(faithful, catalogs)
    completeness = branch_completeness_check(branches, faithful, catalogs)
    by_structure: dict[str, list[ScalarBranch]] = {}
    for branch in branches:
        by_structure.setdefault(branch.structure_id, []).append(branch)
    admissible_structures = [rows[0].candidate for rows in by_structure.values()]
    existential = [rows[0].candidate for rows in by_structure.values() if any(row.clean for row in rows)]
    universal = [rows[0].candidate for rows in by_structure.values() if all(row.clean for row in rows)]
    clean_branches = [row for row in branches if row.clean]

    neutral_orbits, neutral_orbit_rows = neutral_orbit_count(catalogs)
    stage_orbits = {"neutral_carrier": neutral_orbits}
    for stage in ("genuinely_chiral", "atomic_packaging", "closure_consistency", "chirality_faithfulness"):
        stage_orbits[stage] = materialized_orbit_count(base["stage_rows"][stage], catalogs)
    stage_orbits["higher_layer_mass_closure_proxy"] = materialized_orbit_count(admissible_structures, catalogs)
    stage_orbits["clean_separation_existential"] = materialized_orbit_count(existential, catalogs)
    stage_orbits["clean_separation_universal"] = materialized_orbit_count(universal, catalogs)
    branch_orbits = len({branch_orbit_key(row, catalogs[row.dimensions]) for row in branches})
    clean_branch_orbits = len({branch_orbit_key(row, catalogs[row.dimensions]) for row in clean_branches})

    if len(branches) != 12 or len(clean_branches) != 4:
        raise AssertionError(f"unexpected branch census: all={len(branches)} clean={len(clean_branches)}")
    if len(admissible_structures) != 8 or len(existential) != 4 or universal:
        raise AssertionError("unexpected quantified clean-separation result")
    if any(row.dimensions != (2, 3) or v1.active_factor_indices(row.representative) != (0,)
           for row in clean_branches):
        raise AssertionError("a clean branch is not SU(2)-active over 2|3")
    if any(row.clean for row in branches if row.dimensions == (4,)):
        raise AssertionError("an SU(4) branch unexpectedly passed clean separation")

    return {
        "base": base,
        "golden_rows": golden,
        "inert_convention": inert,
        "branches": branches,
        "branch_completeness": completeness,
        "admissible_structures": admissible_structures,
        "clean_branches": clean_branches,
        "existential_structures": existential,
        "universal_structures": universal,
        "neutral_orbit_rows": neutral_orbit_rows,
        "stage_orbits": stage_orbits,
        "branch_orbits": branch_orbits,
        "clean_branch_orbits": clean_branch_orbits,
        "hashes": {
            "all_branches": hash_rows(f"{row.structure_id}::{row.scalar_branch}" for row in branches),
            "clean_branches": hash_rows(f"{row.structure_id}::{row.scalar_branch}" for row in clean_branches),
        },
    }


if __name__ == "__main__":
    result = run_v2()
    print("carrier_chain_v2.py: PASS: "
          f"padded={result['inert_convention']['labelled_with_inert_padding']} "
          f"branches={len(result['branches'])} clean_branches={len(result['clean_branches'])}")
