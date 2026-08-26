#!/usr/bin/env python3
"""Pure carrier and selection-chain computations for S1-REPAIR-1."""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any, Iterable

import representation_model as rm


MAX_FIELDS = 5
COMPONENT_CAP = 6
CHARGE_UNITS = (-6, -4, -3, -2, -1, 0, 1, 2, 3, 4, 6)
DIMENSION_WINDOW = (2, 3, 4)
TARGET_DIMENSIONS = (2, 3)
TARGET_SUPPORT_KEY = (
    "fundxfund:1 + fundxsinglet:-3 + singletxantifund:-4 + "
    "singletxantifund:2 + singletxsinglet:6"
)


@dataclass(frozen=True)
class TypeRow:
    type_id: int
    dimensions: tuple[int, ...]
    reps: tuple[str, ...]
    charge: int
    component_dim: int
    anomaly_vector: tuple[int, ...]
    witten_mask: int

    @property
    def key(self) -> tuple[tuple[str, ...], int]:
        return self.reps, self.charge


@dataclass(frozen=True)
class Candidate:
    dimensions: tuple[int, ...]
    combo: tuple[int, ...]
    support_key: str


@dataclass(frozen=True)
class ScalarRep:
    scalar_id: int
    dimensions: tuple[int, ...]
    reps: tuple[str, ...]
    charge: int
    component_dim: int

    @property
    def text(self) -> str:
        return f"{'x'.join(self.reps)}:{self.charge}"


@dataclass(frozen=True)
class StageResult:
    stage: str
    population: int
    row_sha256: str
    hash_kind: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage,
            "population": self.population,
            "row_sha256": self.row_sha256,
            "hash_kind": self.hash_kind,
        }


def factor_structures() -> tuple[tuple[int, ...], ...]:
    rows: list[tuple[int, ...]] = []
    for count in (1, 2):
        rows.extend(itertools.combinations_with_replacement(DIMENSION_WINDOW, count))
    return tuple(rows)


def neutral_rep_assignments(dimensions: tuple[int, ...]) -> tuple[tuple[str, ...], ...]:
    """Published support pattern, canonicalized and conjugation-closed."""
    assignments: set[tuple[str, ...]] = {tuple("singlet" for _ in dimensions)}
    for factor_index, n in enumerate(dimensions):
        for rep in rm.canonical_reps(n):
            if rep == "singlet":
                continue
            row = ["singlet" for _ in dimensions]
            row[factor_index] = rep
            assignments.add(tuple(row))
    if len(dimensions) == 2:
        left = tuple(dict.fromkeys(rm.canonical_rep(rep, dimensions[0]) for rep in ("fund", "antifund")))
        right = tuple(dict.fromkeys(rm.canonical_rep(rep, dimensions[1]) for rep in ("fund", "antifund")))
        assignments.update(itertools.product(left, right))
    return tuple(sorted(assignments))


def type_rows_for_structure(dimensions: tuple[int, ...]) -> tuple[TypeRow, ...]:
    rows: list[TypeRow] = []
    for reps in neutral_rep_assignments(dimensions):
        component_dim = math.prod(rm.rep_dim(rep, n) for rep, n in zip(reps, dimensions))
        if component_dim > COMPONENT_CAP:
            continue
        for charge in CHARGE_UNITS:
            if charge == 0 and all(rep == "singlet" for rep in reps):
                continue
            vector_parts: list[int] = []
            witten_mask = 0
            for factor_index, (rep, n) in enumerate(zip(reps, dimensions)):
                other_dim = component_dim // rm.rep_dim(rep, n)
                vector_parts.extend(
                    [
                        rm.cubic_anomaly(rep, n) * other_dim,
                        rm.dynkin_twice(rep, n) * other_dim * charge,
                    ]
                )
                if n == 2 and rep == "fund" and other_dim % 2:
                    witten_mask |= 1 << factor_index
            vector_parts.extend([component_dim * charge, component_dim * charge**3])
            rows.append(
                TypeRow(
                    type_id=len(rows),
                    dimensions=dimensions,
                    reps=reps,
                    charge=charge,
                    component_dim=component_dim,
                    anomaly_vector=tuple(vector_parts),
                    witten_mask=witten_mask,
                )
            )
    keys = [row.key for row in rows]
    if len(keys) != len(set(keys)):
        raise AssertionError(f"duplicate canonical field keys for {dimensions}")
    key_set = set(keys)
    for row in rows:
        if conjugate_key(row.key, dimensions) not in key_set:
            raise AssertionError(f"field alphabet not conjugation-closed: {dimensions} {row.key}")
    return tuple(rows)


def build_catalogs() -> dict[tuple[int, ...], tuple[TypeRow, ...]]:
    return {dimensions: type_rows_for_structure(dimensions) for dimensions in factor_structures()}


def conjugate_key(
    key: tuple[tuple[str, ...], int], dimensions: tuple[int, ...]
) -> tuple[tuple[str, ...], int]:
    reps, charge = key
    return tuple(rm.conjugate_rep(rep, n) for rep, n in zip(reps, dimensions)), -charge


def support_key(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> str:
    return " + ".join(
        sorted(f"{'x'.join(type_rows[type_id].reps)}:{type_rows[type_id].charge}" for type_id in combo)
    )


def support_score(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> tuple[int, int, int, int]:
    return (
        len(combo),
        sum(type_rows[type_id].component_dim for type_id in combo),
        sum(n - 1 for n in type_rows[0].dimensions),
        len(type_rows[0].dimensions),
    )


def rows_hash(rows: Iterable[Candidate]) -> str:
    canonical = sorted(f"{'|'.join(map(str, row.dimensions))}\t{row.support_key}" for row in rows)
    return hashlib.sha256(("\n".join(canonical) + ("\n" if canonical else "")).encode()).hexdigest()


def neutral_carrier(catalogs: dict[tuple[int, ...], tuple[TypeRow, ...]]) -> tuple[StageResult, dict[str, int]]:
    counts: dict[str, int] = {}
    specification: list[dict[str, Any]] = []
    for dimensions, type_rows in catalogs.items():
        count = sum(math.comb(len(type_rows) + size - 1, size) for size in range(1, MAX_FIELDS + 1))
        label = "|".join(map(str, dimensions))
        counts[label] = count
        specification.append(
            {
                "dimensions": label,
                "field_keys": [f"{'x'.join(row.reps)}:{row.charge}" for row in type_rows],
                "multiset_sizes": [1, 2, 3, 4, 5],
            }
        )
    payload = json.dumps(specification, separators=(",", ":"), sort_keys=True)
    return (
        StageResult(
            stage="neutral_carrier",
            population=sum(counts.values()),
            row_sha256=hashlib.sha256(payload.encode()).hexdigest(),
            hash_kind="canonical_generating_specification",
        ),
        counts,
    )


def combo_signature(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> tuple[tuple[int, ...], int]:
    anomaly = [0] * len(type_rows[0].anomaly_vector)
    witten = 0
    for type_id in combo:
        row = type_rows[type_id]
        for index, value in enumerate(row.anomaly_vector):
            anomaly[index] += value
        witten ^= row.witten_mask
    return tuple(anomaly), witten


def vectorlike_only(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> bool:
    counts = Counter(type_rows[type_id].key for type_id in combo)
    for key in list(counts):
        if counts.get(key, 0) <= 0:
            continue
        conjugate = conjugate_key(key, type_rows[0].dimensions)
        if conjugate == key:
            counts.pop(key, None)
            continue
        remove = min(counts.get(key, 0), counts.get(conjugate, 0))
        if remove:
            counts[key] -= remove
            counts[conjugate] -= remove
    return not any(value > 0 for value in counts.values())


def enumerate_structure_chiral(
    dimensions: tuple[int, ...], type_rows: tuple[TypeRow, ...]
) -> tuple[list[Candidate], int]:
    zero_anomaly = tuple(0 for _ in type_rows[0].anomaly_vector)
    anomaly_closed_count = 0
    survivors: list[Candidate] = []

    right_three_by_signature: dict[tuple[tuple[int, ...], int], list[tuple[int, ...]]] = defaultdict(list)
    for combo in itertools.combinations_with_replacement(range(len(type_rows)), 3):
        signature = combo_signature(combo, type_rows)
        right_three_by_signature[signature].append(combo)
        if signature == (zero_anomaly, 0):
            anomaly_closed_count += 1
            if not vectorlike_only(combo, type_rows):
                survivors.append(Candidate(dimensions, combo, support_key(combo, type_rows)))

    for size in (1, 2):
        for combo in itertools.combinations_with_replacement(range(len(type_rows)), size):
            if combo_signature(combo, type_rows) != (zero_anomaly, 0):
                continue
            anomaly_closed_count += 1
            if not vectorlike_only(combo, type_rows):
                survivors.append(Candidate(dimensions, combo, support_key(combo, type_rows)))

    for total_size, left_size in ((4, 1), (5, 2)):
        del total_size
        for left in itertools.combinations_with_replacement(range(len(type_rows)), left_size):
            anomaly, witten = combo_signature(left, type_rows)
            needed = (tuple(-value for value in anomaly), witten)
            for right in right_three_by_signature.get(needed, ()):
                if left[-1] > right[0]:
                    continue
                combo = left + right
                anomaly_closed_count += 1
                if not vectorlike_only(combo, type_rows):
                    survivors.append(Candidate(dimensions, combo, support_key(combo, type_rows)))

    if len({row.support_key for row in survivors}) != len(survivors):
        raise AssertionError(f"multiset enumeration produced duplicate canonical rows for {dimensions}")
    return survivors, anomaly_closed_count


def genuinely_chiral_filter(
    catalogs: dict[tuple[int, ...], tuple[TypeRow, ...]]
) -> tuple[StageResult, list[Candidate], dict[str, dict[str, int]]]:
    rows: list[Candidate] = []
    diagnostics: dict[str, dict[str, int]] = {}
    for dimensions, type_rows in catalogs.items():
        survivors, anomaly_closed = enumerate_structure_chiral(dimensions, type_rows)
        label = "|".join(map(str, dimensions))
        diagnostics[label] = {
            "anomaly_closed_multisets": anomaly_closed,
            "vectorlike_excluded": anomaly_closed - len(survivors),
            "genuinely_chiral": len(survivors),
        }
        rows.extend(survivors)
    return StageResult("genuinely_chiral", len(rows), rows_hash(rows), "materialized_membership"), rows, diagnostics


def sum_anomaly(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> tuple[tuple[int, ...], int]:
    return combo_signature(combo, type_rows)


def closed_chiral(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> bool:
    anomaly, witten = sum_anomaly(combo, type_rows)
    return bool(combo) and not any(anomaly) and witten == 0 and not vectorlike_only(combo, type_rows)


def atomic_package(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> bool:
    for size in range(1, len(combo)):
        if any(closed_chiral(tuple(subset), type_rows) for subset in itertools.combinations(combo, size)):
            return False
    return True


def action_active(rep: str, n: int) -> bool:
    return rep != "singlet" and rm.dynkin_twice(rep, n) > 0


def no_spectator_action(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> bool:
    dimensions = type_rows[0].dimensions
    return all(
        any(action_active(type_rows[type_id].reps[index], n) for type_id in combo)
        for index, n in enumerate(dimensions)
    )


def primitive_charge_orbit(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> bool:
    signed = [type_rows[type_id].charge for type_id in combo if type_rows[type_id].charge]
    return bool(signed) and any(q > 0 for q in signed) and any(q < 0 for q in signed) and math.gcd(*(abs(q) for q in signed)) == 1


def atomic_rewrite_packaging(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> bool:
    return atomic_package(combo, type_rows) and no_spectator_action(combo, type_rows) and primitive_charge_orbit(combo, type_rows)


def filter_atomic(
    rows: list[Candidate], catalogs: dict[tuple[int, ...], tuple[TypeRow, ...]]
) -> tuple[StageResult, list[Candidate]]:
    survivors = [row for row in rows if atomic_rewrite_packaging(row.combo, catalogs[row.dimensions])]
    return StageResult("atomic_packaging", len(survivors), rows_hash(survivors), "materialized_membership"), survivors


def action_incidence(row: TypeRow) -> frozenset[int]:
    return frozenset(
        index for index, (rep, n) in enumerate(zip(row.reps, row.dimensions)) if action_active(rep, n)
    )


def route_incidence_complete(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> bool:
    incidence = [action_incidence(type_rows[type_id]) for type_id in combo]
    all_factors = frozenset(range(len(type_rows[0].dimensions)))
    if not incidence or frozenset().union(*incidence) != all_factors:
        return False
    if any(frozenset([factor]) not in incidence for factor in all_factors):
        return False
    if len(all_factors) > 1 and all_factors not in incidence:
        return False
    return sum(1 for item in incidence if not item) <= 1


def filter_closure_consistency(
    rows: list[Candidate], catalogs: dict[tuple[int, ...], tuple[TypeRow, ...]]
) -> tuple[StageResult, list[Candidate]]:
    survivors = [row for row in rows if route_incidence_complete(row.combo, catalogs[row.dimensions])]
    return StageResult("closure_consistency", len(survivors), rows_hash(survivors), "materialized_membership"), survivors


def residual_counts(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> Counter:
    counts = Counter(type_rows[type_id].key for type_id in combo)
    for key in list(counts):
        if counts.get(key, 0) <= 0:
            continue
        conjugate = conjugate_key(key, type_rows[0].dimensions)
        if conjugate == key:
            counts.pop(key, None)
            continue
        remove = min(counts.get(key, 0), counts.get(conjugate, 0))
        if remove:
            counts[key] -= remove
            counts[conjugate] -= remove
    return Counter({key: value for key, value in counts.items() if value > 0})


def chirality_faithfulness(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> dict[str, Any]:
    counts = residual_counts(combo, type_rows)
    complex_keys = [
        key
        for key in counts
        if any(
            action_active(rep, n) and not rm.is_self_conjugate(rep, n)
            for rep, n in zip(key[0], type_rows[0].dimensions)
        )
    ]
    return {
        "residual_chiral_key_count": len(counts),
        "complex_nonabelian_residual_key_count": len(complex_keys),
        "chirality_faithfulness_passes": bool(complex_keys),
    }


def filter_chirality_faithful(
    rows: list[Candidate], catalogs: dict[tuple[int, ...], tuple[TypeRow, ...]]
) -> tuple[StageResult, list[Candidate]]:
    survivors = [
        row for row in rows if chirality_faithfulness(row.combo, catalogs[row.dimensions])["chirality_faithfulness_passes"]
    ]
    return StageResult("chirality_faithfulness", len(survivors), rows_hash(survivors), "materialized_membership"), survivors


def scalar_representations(dimensions: tuple[int, ...]) -> tuple[ScalarRep, ...]:
    rows: list[ScalarRep] = []
    for reps in neutral_rep_assignments(dimensions):
        component_dim = math.prod(rm.rep_dim(rep, n) for rep, n in zip(reps, dimensions))
        if component_dim > COMPONENT_CAP:
            continue
        for charge in CHARGE_UNITS:
            if charge == 0 and all(rep == "singlet" for rep in reps):
                continue
            rows.append(ScalarRep(len(rows), dimensions, reps, charge, component_dim))
    return tuple(rows)


def conjugate_scalar(scalar: ScalarRep) -> ScalarRep:
    return ScalarRep(
        -scalar.scalar_id - 1,
        scalar.dimensions,
        tuple(rm.conjugate_rep(rep, n) for rep, n in zip(scalar.reps, scalar.dimensions)),
        -scalar.charge,
        scalar.component_dim,
    )


def one_singlet_pair(rep_a: str, rep_b: str, rep_c: str, n: int) -> bool:
    for left, right, spectator in ((rep_a, rep_b, rep_c), (rep_a, rep_c, rep_b), (rep_b, rep_c, rep_a)):
        if spectator == "singlet" and right == rm.conjugate_rep(left, n):
            return True
    return False


def rank_two_epsilon(rep_a: str, rep_b: str, rep_c: str, n: int) -> bool:
    return n == 3 and ({rep_a, rep_b, rep_c} == {"fund"} or {rep_a, rep_b, rep_c} == {"antifund"})


def two_index_coupling(rep_a: str, rep_b: str, rep_c: str, n: int) -> bool:
    reps = [rep_a, rep_b, rep_c]
    cases = (
        ("sym2", "antifund"),
        ("conj_sym2", "fund"),
        ("antisym2", "antifund"),
        ("conj_antisym2", "fund"),
    )
    for two_index, fundamental in cases:
        canonical_two = rm.canonical_rep(two_index, n)
        if canonical_two not in reps:
            continue
        others = list(reps)
        others.remove(canonical_two)
        if others == [fundamental, fundamental]:
            return True
        conjugate_fundamental = rm.conjugate_rep(fundamental, n)
        if rm.is_self_conjugate(canonical_two, n) and others == [conjugate_fundamental, conjugate_fundamental]:
            return True
    return False


def factor_invariant(rep_a: str, rep_b: str, rep_c: str, n: int) -> bool:
    if rep_a == rep_b == rep_c == "singlet":
        return True
    return one_singlet_pair(rep_a, rep_b, rep_c, n) or rank_two_epsilon(rep_a, rep_b, rep_c, n) or two_index_coupling(rep_a, rep_b, rep_c, n)


def yukawa_invariant(left: TypeRow, right: TypeRow, scalar: ScalarRep) -> bool:
    return left.charge + right.charge + scalar.charge == 0 and all(
        factor_invariant(a, b, c, n)
        for a, b, c, n in zip(left.reps, right.reps, scalar.reps, left.dimensions)
    )


def scalar_breaks_to_unbroken_u1(scalar: ScalarRep) -> bool:
    return scalar.charge != 0 and any(action_active(rep, n) for rep, n in zip(scalar.reps, scalar.dimensions))


def mass_completion(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...], scalar: ScalarRep) -> dict[str, Any]:
    occurrences = [type_rows[type_id] for type_id in combo]
    tested_scalars = (scalar, conjugate_scalar(scalar))
    covered = [False] * len(occurrences)
    witnesses: list[str] = []
    for left_index, left in enumerate(occurrences):
        for right_index, right in enumerate(occurrences):
            if left_index == right_index and len(occurrences) > 1:
                continue
            for candidate_scalar in tested_scalars:
                if yukawa_invariant(left, right, candidate_scalar):
                    covered[left_index] = True
                    if len(witnesses) < 12:
                        witnesses.append(f"o{left_index}-o{right_index}@{candidate_scalar.text}")
                    break
            if covered[left_index]:
                break
    return {
        "covered_count": sum(covered),
        "fermion_count": len(occurrences),
        "mass_completable": all(covered),
        "coupling_witnesses": ";".join(witnesses),
        "uncovered_occurrences": ";".join(f"o{index}" for index, value in enumerate(covered) if not value),
    }


def higher_layer_mass_closure(
    combo: tuple[int, ...], type_rows: tuple[TypeRow, ...], scalar_rows: tuple[ScalarRep, ...]
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for scalar in sorted(scalar_rows, key=lambda row: (row.component_dim, abs(row.charge), row.text)):
        completion = mass_completion(combo, type_rows, scalar)
        breaks = scalar_breaks_to_unbroken_u1(scalar)
        record = {"witness_scalar": scalar, "breaks_to_unbroken_u1": breaks, **completion}
        if best is None or (
            record["covered_count"], int(breaks), -scalar.component_dim, -abs(scalar.charge)
        ) > (
            best["covered_count"], int(best["breaks_to_unbroken_u1"]), -best["witness_scalar"].component_dim, -abs(best["witness_scalar"].charge)
        ):
            best = record
        if completion["mass_completable"] and breaks:
            return {"higher_layer_passes": True, **record}
    assert best is not None
    return {"higher_layer_passes": False, **best}


def filter_higher_layer_mass_closure(
    rows: list[Candidate], catalogs: dict[tuple[int, ...], tuple[TypeRow, ...]]
) -> tuple[StageResult, list[Candidate], dict[tuple[tuple[int, ...], str], dict[str, Any]]]:
    scalar_cache = {dimensions: scalar_representations(dimensions) for dimensions in catalogs}
    diagnostics: dict[tuple[tuple[int, ...], str], dict[str, Any]] = {}
    survivors: list[Candidate] = []
    for row in rows:
        result = higher_layer_mass_closure(row.combo, catalogs[row.dimensions], scalar_cache[row.dimensions])
        diagnostics[(row.dimensions, row.support_key)] = result
        if result["higher_layer_passes"]:
            survivors.append(row)
    return StageResult("higher_layer_mass_closure_proxy", len(survivors), rows_hash(survivors), "materialized_membership"), survivors, diagnostics


def active_factor_indices(scalar: ScalarRep) -> tuple[int, ...]:
    return tuple(index for index, (rep, n) in enumerate(zip(scalar.reps, scalar.dimensions)) if action_active(rep, n))


def candidate_active_factors(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...]) -> tuple[int, ...]:
    return tuple(
        sorted(
            {
                index
                for type_id in combo
                for index, (rep, n) in enumerate(zip(type_rows[type_id].reps, type_rows[type_id].dimensions))
                if action_active(rep, n)
            }
        )
    )


def residual_subgroup_dimension(rep: str, n: int) -> int:
    if rep == "singlet":
        return n
    if rep in rm.canonical_reps(n):
        return n - 1
    return 0


def low_energy_shadow(combo: tuple[int, ...], type_rows: tuple[TypeRow, ...], scalar: ScalarRep) -> dict[str, Any]:
    carrier_active = set(candidate_active_factors(combo, type_rows))
    scalar_active = set(active_factor_indices(scalar))
    unbroken: list[int] = []
    broken_vector_exotic_count = 0
    notes: list[str] = []
    for factor_index, n in enumerate(scalar.dimensions):
        if factor_index not in carrier_active:
            continue
        if factor_index in scalar_active:
            residual = residual_subgroup_dimension(scalar.reps[factor_index], n)
            if residual >= 2:
                unbroken.append(residual)
                charged_vectors = 2 * residual
                broken_vector_exotic_count += charged_vectors
                notes.append(f"factor{factor_index}:residual{residual}:charged_vectors{charged_vectors}")
            else:
                notes.append(f"factor{factor_index}:no_nonabelian_residual")
        else:
            unbroken.append(n)
            notes.append(f"factor{factor_index}:untouched{n}")
    confining = [value for value in unbroken if value >= 2]
    base = bool(confining)
    return {
        "unbroken_nonabelian_subgroups": tuple(sorted(unbroken)),
        "confining_subgroups": tuple(sorted(confining)),
        "broken_vector_exotic_count": broken_vector_exotic_count,
        "broken_generator_notes": ";".join(notes),
        "base_stable_composite_mass_requirement": base,
        "clean_shadow_requirement": base and broken_vector_exotic_count == 0,
    }


def delta_counts(dimensions: tuple[int, ...], conf_dim: int, charged_broken_count: int) -> tuple[int, int]:
    conf_generators = conf_dim * conf_dim - 1
    total_nonabelian_generators = sum(n * n - 1 for n in dimensions)
    colorless_broken_count = max(total_nonabelian_generators - conf_generators - charged_broken_count, 0)
    del colorless_broken_count
    return conf_generators * charged_broken_count, charged_broken_count


def filter_clean_separation(
    rows: list[Candidate],
    catalogs: dict[tuple[int, ...], tuple[TypeRow, ...]],
    higher_diagnostics: dict[tuple[tuple[int, ...], str], dict[str, Any]],
) -> tuple[StageResult, list[Candidate], dict[tuple[tuple[int, ...], str], dict[str, Any]]]:
    diagnostics: dict[tuple[tuple[int, ...], str], dict[str, Any]] = {}
    survivors: list[Candidate] = []
    for row in rows:
        scalar = higher_diagnostics[(row.dimensions, row.support_key)]["witness_scalar"]
        shadow = low_energy_shadow(row.combo, catalogs[row.dimensions], scalar)
        confining = shadow["confining_subgroups"]
        if confining:
            pair_count, witness_count = delta_counts(
                row.dimensions, max(confining), shadow["broken_vector_exotic_count"]
            )
        else:
            pair_count = witness_count = 0
        shadow.update(
            {
                "delta_pair_count": pair_count,
                "delta_witness_count": witness_count,
                "delta_empty": pair_count == 0,
                "step38_step41_faithful": (pair_count == 0) == shadow["clean_shadow_requirement"],
            }
        )
        diagnostics[(row.dimensions, row.support_key)] = shadow
        if shadow["clean_shadow_requirement"] and pair_count == 0:
            survivors.append(row)
    return StageResult("clean_separation", len(survivors), rows_hash(survivors), "materialized_membership"), survivors, diagnostics


def family_counts(stage: str, rows: Iterable[Candidate]) -> list[dict[str, Any]]:
    counts = Counter("|".join(map(str, row.dimensions)) for row in rows)
    return [
        {
            "stage": stage,
            "dimensions": "|".join(map(str, dimensions)),
            "population": counts.get("|".join(map(str, dimensions)), 0),
        }
        for dimensions in sorted(factor_structures(), key=lambda item: "|".join(map(str, item)))
    ]


def run_chain() -> dict[str, Any]:
    rep_test = rm.self_test()
    if not rep_test["passes"]:
        raise RuntimeError(f"representation self-test failed: {rep_test['failed_checks']}")
    catalogs = build_catalogs()
    neutral, neutral_families = neutral_carrier(catalogs)
    chiral, chiral_rows, enumeration = genuinely_chiral_filter(catalogs)
    atomic, atomic_rows = filter_atomic(chiral_rows, catalogs)
    closure, closure_rows = filter_closure_consistency(atomic_rows, catalogs)
    faithful, faithful_rows = filter_chirality_faithful(closure_rows, catalogs)
    higher, higher_rows, higher_diagnostics = filter_higher_layer_mass_closure(faithful_rows, catalogs)
    clean, clean_rows, clean_diagnostics = filter_clean_separation(higher_rows, catalogs, higher_diagnostics)
    stages = [neutral, chiral, atomic, closure, faithful, higher, clean]
    families = [
        *[{"stage": "neutral_carrier", "dimensions": key, "population": value} for key, value in sorted(neutral_families.items())],
        *family_counts("genuinely_chiral", chiral_rows),
        *family_counts("atomic_packaging", atomic_rows),
        *family_counts("closure_consistency", closure_rows),
        *family_counts("chirality_faithfulness", faithful_rows),
        *family_counts("higher_layer_mass_closure_proxy", higher_rows),
        *family_counts("clean_separation", clean_rows),
    ]
    return {
        "representation_self_test": rep_test,
        "catalogs": catalogs,
        "stages": stages,
        "families": families,
        "enumeration_diagnostics": enumeration,
        "stage_rows": {
            "genuinely_chiral": chiral_rows,
            "atomic_packaging": atomic_rows,
            "closure_consistency": closure_rows,
            "chirality_faithfulness": faithful_rows,
            "higher_layer_mass_closure_proxy": higher_rows,
            "clean_separation": clean_rows,
        },
        "higher_diagnostics": higher_diagnostics,
        "clean_diagnostics": clean_diagnostics,
    }
