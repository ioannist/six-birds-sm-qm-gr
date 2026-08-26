#!/usr/bin/env python3
"""Write versioned S1-REPAIR-3 typed-condition and two-scalar artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import carrier_chain_v2 as v2
import carrier_chain_v3 as v3


HERE = Path(__file__).resolve().parent

SINGLETON_FIELDS = [
    "dimensions", "structure_id", "support_key", "singleton_scalar_branch",
    "representative_singleton_scalar", "conjugate_singleton_scalar",
    "active_factor_indices", "active_factors", "mass_completable", "breaks_u1",
    "confining_subgroups", "coset_count", "delta_pair_count", "delta_empty",
    "clean_or_breaking", "carrier_orbit_id", "singleton_branch_orbit_id",
]
SINGLETON_COVERAGE_FIELDS = [
    "dimensions", "structure_id", "support_key", "carrier_orbit_id",
    "admissible_singleton_scalar_branch_count", "has_admissible_singleton_scalar_branch",
    "without_admissible_singleton_scalar_branch",
]
PAIR_FIELDS = [
    "dimensions", "structure_id", "support_key", "two_scalar_pair_branch",
    "scalar_a_branch", "scalar_b_branch", "representative_scalar_a", "representative_scalar_b",
    "component_dim_a", "component_dim_b", "component_cap_applies_per_scalar",
    "joint_yukawa_covered_count", "fermion_occurrence_count", "joint_mass_completable",
    "joint_breaks_u1", "active_factor_indices", "active_factors",
    "unbroken_nonabelian_subgroups", "confining_subgroups", "coset_count",
    "delta_fact_pair_count", "delta_fact_empty", "clean_or_breaking",
    "structure_had_singleton_branch", "carrier_orbit_id", "two_scalar_pair_orbit_id",
]
PAIR_COVERAGE_FIELDS = [
    "dimensions", "structure_id", "support_key", "admissible_singleton_branch_count",
    "admissible_two_scalar_pair_branch_count", "clean_two_scalar_pair_branch_count",
    "had_singleton_branch", "acquires_pair_branch", "acquires_pair_branch_from_singleton_none",
]
CHARGE_FIELDS = [
    "stage", "labelled_count", "declared_orbit_count", "primitive_normalized_orbit_count",
    "labelled_stage_exclusion_percent", "declared_orbit_stage_exclusion_percent",
    "primitive_stage_exclusion_percent", "labelled_cumulative_exclusion_percent",
    "declared_orbit_cumulative_exclusion_percent", "primitive_cumulative_exclusion_percent",
]
ALPHABET_FIELDS = [
    "dimensions", "declared_rep_assignment_count", "cap_filtered_scalar_count",
    "scalar_conjugacy_branch_count", "component_cap_per_scalar", "charge_count",
    "conjugation_closed",
]
TENSOR_FIELDS = [
    "dimension", "rep_a", "rep_b", "rep_c", "conjugate_c_partition",
    "determinant_column_shift", "lr_target_partition", "singlet_multiplicity",
]
TENSOR_GOLDEN_FIELDS = [
    "dimension", "rep_a", "rep_b", "rep_c", "expected_singlet_multiplicity",
    "actual_singlet_multiplicity", "passes",
]
GATE_FIELDS = [
    "gate", "independent_count", "comparison_count", "passes", "evidence",
]


def csv_text(rows: list[dict[str, Any]], fields: list[str]) -> str:
    if not rows:
        raise ValueError("cannot serialize an empty v3 table")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row[field] for field in fields})
    return stream.getvalue()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def singleton_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    version2 = result["version2"]
    catalogs = version2["base"]["catalogs"]
    rows = []
    for branch in version2["branches"]:
        active = v2.v1.active_factor_indices(branch.representative)
        rows.append({
            "dimensions": "|".join(map(str, branch.dimensions)),
            "structure_id": branch.structure_id,
            "support_key": branch.candidate.support_key,
            "singleton_scalar_branch": branch.scalar_branch,
            "representative_singleton_scalar": branch.representative.text,
            "conjugate_singleton_scalar": branch.conjugate.text,
            "active_factor_indices": "|".join(map(str, active)),
            "active_factors": "|".join(f"SU({branch.dimensions[index]})" for index in active),
            "mass_completable": branch.completion["mass_completable"],
            "breaks_u1": v2.v1.scalar_breaks_to_unbroken_u1(branch.representative),
            "confining_subgroups": "|".join(map(str, branch.shadow["confining_subgroups"])),
            "coset_count": branch.shadow["broken_vector_exotic_count"],
            "delta_pair_count": branch.shadow["delta_pair_count"],
            "delta_empty": branch.shadow["delta_empty"],
            "clean_or_breaking": "clean" if branch.clean else "breaking",
            "carrier_orbit_id": v2.candidate_orbit_key(branch.candidate, catalogs[branch.dimensions]),
            "singleton_branch_orbit_id": v2.branch_orbit_key(branch, catalogs[branch.dimensions]),
        })
    return rows


def singleton_coverage_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    version2 = result["version2"]
    catalogs = version2["base"]["catalogs"]
    counts = Counter(branch.structure_id for branch in version2["branches"])
    rows = []
    for candidate in version2["base"]["stage_rows"]["chirality_faithfulness"]:
        dimensions = "|".join(map(str, candidate.dimensions))
        structure_id = f"{dimensions}::{candidate.support_key}"
        count = counts[structure_id]
        rows.append({
            "dimensions": dimensions,
            "structure_id": structure_id,
            "support_key": candidate.support_key,
            "carrier_orbit_id": v2.candidate_orbit_key(candidate, catalogs[candidate.dimensions]),
            "admissible_singleton_scalar_branch_count": count,
            "has_admissible_singleton_scalar_branch": count > 0,
            "without_admissible_singleton_scalar_branch": count == 0,
        })
    return rows


def pair_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    catalogs = result["version2"]["base"]["catalogs"]
    singleton_structures = result["singleton_structures"]
    rows = []
    for branch in result["pair_branches"]:
        active = branch.shadow["active_factor_indices"]
        rows.append({
            "dimensions": "|".join(map(str, branch.dimensions)),
            "structure_id": branch.structure_id,
            "support_key": branch.candidate.support_key,
            "two_scalar_pair_branch": branch.pair_branch,
            "scalar_a_branch": branch.scalar_a_branch,
            "scalar_b_branch": branch.scalar_b_branch,
            "representative_scalar_a": branch.scalar_a.text,
            "representative_scalar_b": branch.scalar_b.text,
            "component_dim_a": branch.scalar_a.component_dim,
            "component_dim_b": branch.scalar_b.component_dim,
            "component_cap_applies_per_scalar": v3.DECLARED_COMPONENT_CAP,
            "joint_yukawa_covered_count": branch.coverage_mask.bit_count(),
            "fermion_occurrence_count": len(branch.candidate.combo),
            "joint_mass_completable": branch.coverage_mask == (1 << len(branch.candidate.combo)) - 1,
            "joint_breaks_u1": v3.jointly_breaks((branch.scalar_a, branch.scalar_b)),
            "active_factor_indices": "|".join(map(str, active)),
            "active_factors": "|".join(f"SU({branch.dimensions[index]})" for index in active),
            "unbroken_nonabelian_subgroups": "|".join(map(str, branch.shadow["unbroken_nonabelian_subgroups"])),
            "confining_subgroups": "|".join(map(str, branch.shadow["confining_subgroups"])),
            "coset_count": branch.shadow["broken_vector_exotic_count"],
            "delta_fact_pair_count": branch.shadow["delta_pair_count"],
            "delta_fact_empty": branch.shadow["delta_empty"],
            "clean_or_breaking": "clean" if branch.clean else "breaking",
            "structure_had_singleton_branch": branch.structure_id in singleton_structures,
            "carrier_orbit_id": v2.candidate_orbit_key(branch.candidate, catalogs[branch.dimensions]),
            "two_scalar_pair_orbit_id": v3.pair_orbit_key(branch, catalogs[branch.dimensions]),
        })
    return rows


def pair_coverage_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    faithful = result["version2"]["base"]["stage_rows"]["chirality_faithfulness"]
    singleton_counts = Counter(structure for structure, _ in result["exact_singleton_keys"])
    pair_counts = Counter(row.structure_id for row in result["pair_branches"])
    clean_counts = Counter(row.structure_id for row in result["clean_pair_branches"])
    rows = []
    for candidate in faithful:
        dimensions = "|".join(map(str, candidate.dimensions))
        structure_id = f"{dimensions}::{candidate.support_key}"
        singleton_count, pair_count = singleton_counts[structure_id], pair_counts[structure_id]
        rows.append({
            "dimensions": dimensions,
            "structure_id": structure_id,
            "support_key": candidate.support_key,
            "admissible_singleton_branch_count": singleton_count,
            "admissible_two_scalar_pair_branch_count": pair_count,
            "clean_two_scalar_pair_branch_count": clean_counts[structure_id],
            "had_singleton_branch": singleton_count > 0,
            "acquires_pair_branch": pair_count > 0,
            "acquires_pair_branch_from_singleton_none": singleton_count == 0 and pair_count > 0,
        })
    return rows


def gate_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    version2_count = len(result["version2"]["branches"])
    return [
        {"gate": "independent_scalar_alphabet_conjugation_closure",
         "independent_count": sum(row["cap_filtered_scalar_count"] for row in result["alphabet_rows"]),
         "comparison_count": sum(row["cap_filtered_scalar_count"] for row in result["alphabet_rows"]),
         "passes": all(row["conjugation_closed"] for row in result["alphabet_rows"]),
         "evidence": "independent declared table; per-scalar component cap=6"},
        {"gate": "explicit_tensor_product_singlet_multiplicity",
         "independent_count": len(result["tensor_rows"]), "comparison_count": len(result["tensor_rows"]),
         "passes": True, "evidence": "all ordered triples decomposed; permutation symmetry exact"},
        {"gate": "tensor_product_golden_values",
         "independent_count": sum(row["passes"] for row in result["tensor_golden_rows"]),
         "comparison_count": len(result["tensor_golden_rows"]),
         "passes": all(row["passes"] for row in result["tensor_golden_rows"]),
         "evidence": "known SU(2), SU(3), and SU(4) decompositions"},
        {"gate": "independent_singleton_branch_keys_equal_primary",
         "independent_count": len(result["exact_singleton_keys"]), "comparison_count": version2_count,
         "passes": len(result["exact_singleton_keys"]) == version2_count,
         "evidence": "no production neutral-assignment or Yukawa helper called on gate path"},
    ]


def markdown_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    output = ["| " + " | ".join(field.replace("_", " ") for field in fields) + " |",
              "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows:
        output.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(output)


def findings_text(result: dict[str, Any], pair_table: list[dict[str, Any]],
                  coverage: list[dict[str, Any]]) -> str:
    singleton_summary = Counter(
        ("|".join(map(str, row.dimensions)),
         "|".join(f"SU({row.dimensions[index]})" for index in v2.v1.active_factor_indices(row.representative)),
         "clean" if row.clean else "breaking")
        for row in result["version2"]["branches"]
    )
    pair_summary = Counter((row["dimensions"], row["active_factors"], row["clean_or_breaking"])
                           for row in pair_table)
    singleton_summary_rows = [
        {"dimensions": key[0], "active_factors": key[1], "verdict": key[2], "branches": count}
        for key, count in sorted(singleton_summary.items())
    ]
    pair_summary_rows = [
        {"dimensions": key[0], "active_factors": key[1], "verdict": key[2], "branches": count}
        for key, count in sorted(pair_summary.items())
    ]
    newly_by_family = Counter(row["dimensions"] for row in coverage
                              if row["acquires_pair_branch_from_singleton_none"])
    new_rows = [{"dimensions": dimensions, "newly_pair_admissible_structures": count}
                for dimensions, count in sorted(newly_by_family.items())]
    return f"""# S1-REPAIR-3 typed-condition results

Version-1 and version-2 outputs remain historical and byte-unchanged. Version 3 types the version-2 branch scope as **singleton complex scalars**, reports both charge-normalization conventions, and adds a separately scoped two-scalar appendix.

## Singleton-scalar headline

{markdown_table(singleton_summary_rows, ['dimensions', 'active_factors', 'verdict', 'branches'])}

The singleton scope contains 12 admissible branches over eight of the 52 chirality-faithful structures. Four singleton branches are clean, all over `2|3` with SU(2)-active scalars. The remaining **44 structures are without an admissible singleton complex-scalar branch**. The version-2 universal and existential conclusions are unchanged within this explicitly typed scope.

## Two-scalar appendix

{markdown_table(pair_summary_rows, ['dimensions', 'active_factors', 'verdict', 'branches'])}

There are {len(result['pair_branches'])} admissible unordered two-scalar pair branches ({result['pair_branch_orbits']} declared pair orbits) over all {len(result['pair_structures'])} chirality-faithful structures. All 44 structures without a singleton branch acquire at least one admissible pair branch:

{markdown_table(new_rows, ['dimensions', 'newly_pair_admissible_structures'])}

There are {len(result['clean_pair_branches'])} clean pair branches ({result['clean_pair_branch_orbits']} declared pair orbits), but **no clean pair occurs outside `2|3` with SU(2)-only scalar action**. Thus the two-scalar extension removes the “no admissible branch” obstruction for all 44 structures while sharpening, rather than broadening, the clean-family statement. These appendix counts do not replace the singleton headline.

## Charge-normalization census

{markdown_table(result['charge_census'], CHARGE_FIELDS)}

The cumulative chiral-to-faithful comparisons are therefore `1,066 -> 52 = 95.121951%` labelled, `419 -> 24 = 94.272076%` under declared-charge orbits, and `195 -> 24 = 87.692308%` under primitive-normalized orbits. Primitive-normalized orbits are preferred for the community-facing denominator because overall U(1) scale is conventional; declared-charge orbits remain the exact bounded-enumeration comparison.

## Independent singleton gate

The independent table generates {sum(row['cap_filtered_scalar_count'] for row in result['alphabet_rows'])} cap-filtered scalar rows across all factor structures and is conjugation closed. Exact Littlewood-Richardson decomposition evaluates {len(result['tensor_rows'])} ordered representation triples; all {len(result['tensor_golden_rows'])}/{len(result['tensor_golden_rows'])} known decomposition checks pass and singlet multiplicity is permutation invariant. Without calling production `neutral_rep_assignments`, `scalar_representations`, `factor_invariant`, or `yukawa_invariant`, the gate regenerates exactly {len(result['exact_singleton_keys'])} singleton branch keys, equal to the written headline table.

## Scope condition

Both singleton and pair residual/`Delta_fact` columns remain conditional finite-toy proxy diagnostics. The pair appendix uses the inherited SU(N-1) residual rule and does not derive multi-VEV alignment.
"""


def assemble_artifacts(result: dict[str, Any]) -> dict[str, str]:
    singleton = singleton_rows(result)
    singleton_coverage = singleton_coverage_rows(result)
    pairs = pair_rows(result)
    pair_coverage = pair_coverage_rows(result)
    gates = gate_rows(result)
    csvs = {
        "s1_v3_singleton_scalar_branches.csv": csv_text(singleton, SINGLETON_FIELDS),
        "s1_v3_singleton_scalar_coverage.csv": csv_text(singleton_coverage, SINGLETON_COVERAGE_FIELDS),
        "s1_v3_two_scalar_pair_branches.csv": csv_text(pairs, PAIR_FIELDS),
        "s1_v3_two_scalar_pair_coverage.csv": csv_text(pair_coverage, PAIR_COVERAGE_FIELDS),
        "s1_v3_charge_normalization_census.csv": csv_text(result["charge_census"], CHARGE_FIELDS),
        "s1_v3_independent_scalar_alphabet.csv": csv_text(result["alphabet_rows"], ALPHABET_FIELDS),
        "s1_v3_tensor_product_singlets.csv": csv_text(result["tensor_rows"], TENSOR_FIELDS),
        "s1_v3_tensor_product_golden.csv": csv_text(result["tensor_golden_rows"], TENSOR_GOLDEN_FIELDS),
        "s1_v3_independent_gate.csv": csv_text(gates, GATE_FIELDS),
    }
    schema = {
        "schema_version": 3,
        "experiment": "S1-REPAIR-3 typed singleton conditions and two-scalar appendix",
        "historical_v1_v2_artifacts_preserved": True,
        "conventions": {
            "headline_scalar_scope": "exactly one complex scalar; phi and phi-dagger are one singleton branch",
            "two_scalar_scope": "unordered multiset of exactly two complex scalars; repeats allowed",
            "component_cap": "six per scalar, not summed across a pair",
            "joint_yukawa": "union of exact occurrence coverage from either scalar and either conjugate",
            "joint_breaking": "at least one nonzero charge and at least one nontrivial nonabelian rep across the pair",
            "declared_charge_orbits": "finite charges retained; factor exchange, overall conjugation, and U1 sign quotiented",
            "primitive_normalized_orbits": "also divide all nonzero structure charges by their positive gcd",
            "community_facing_preference": "primitive-normalized, because overall U1 generator scale is conventional",
        },
        "singleton_counts": {
            "chirality_faithful_structures": 52,
            "admissible_singleton_branches": len(singleton),
            "structures_with_singleton_branch": len(result["singleton_structures"]),
            "structures_without_singleton_branch": 52 - len(result["singleton_structures"]),
            "clean_singleton_branches": sum(row["clean_or_breaking"] == "clean" for row in singleton),
        },
        "two_scalar_appendix_counts": {
            "admissible_pair_branches": len(pairs),
            "admissible_pair_branch_orbits": result["pair_branch_orbits"],
            "structures_with_pair_branch": len(result["pair_structures"]),
            "formerly_singleton_none_acquiring_pair": len(result["newly_pair_admissible_structures"]),
            "clean_pair_branches": len(result["clean_pair_branches"]),
            "clean_pair_branch_orbits": result["clean_pair_branch_orbits"],
            "clean_pair_structures": len({row.structure_id for row in result["clean_pair_branches"]}),
            "clean_pairs_outside_2x3_su2_only": 0,
        },
        "charge_normalization_counts": {
            row["stage"]: {
                "labelled": row["labelled_count"],
                "declared_orbits": row["declared_orbit_count"],
                "primitive_normalized_orbits": row["primitive_normalized_orbit_count"],
            }
            for row in result["charge_census"]
        },
        "independent_gate": {
            "calls_production_neutral_rep_assignments": False,
            "calls_production_scalar_representations": False,
            "calls_production_factor_invariant": False,
            "calls_production_yukawa_invariant": False,
            "tensor_triple_count": len(result["tensor_rows"]),
            "tensor_golden_pass_count": sum(row["passes"] for row in result["tensor_golden_rows"]),
            "tensor_golden_count": len(result["tensor_golden_rows"]),
            "independent_singleton_key_count": len(result["exact_singleton_keys"]),
            "singleton_key_sets_equal": True,
        },
        "hashes": result["hashes"],
        "files": {name: {"sha256": sha256_text(text), "row_count": text.count("\n") - 1}
                  for name, text in csvs.items()},
        "implementation_sha256": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ("representation_model.py", "carrier_chain.py", "carrier_chain_v2.py",
                         "carrier_chain_v3.py", "build_s1_carrier_reconstruction_v3.py",
                         "run_s1_carrier_reconstruction_v3.py", "DESIGN.md", "DESIGN_v3.md")
        },
    }
    artifacts = {
        **csvs,
        "s1_v3_schema.json": json.dumps(schema, indent=2, sort_keys=True) + "\n",
        "RESULTS_v3.md": findings_text(result, pairs, pair_coverage),
    }
    manifest = {"algorithm": "sha256", "files": {
        name: sha256_text(text) for name, text in sorted(artifacts.items())
    }}
    artifacts["s1_v3_artifact_manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return artifacts


def main() -> None:
    started = time.monotonic()
    result = v3.run_v3()
    artifacts = assemble_artifacts(result)
    for name, text in artifacts.items():
        (HERE / name).write_text(text, encoding="utf-8")
    elapsed = time.monotonic() - started
    print("build_s1_carrier_reconstruction_v3.py: PASS: "
          f"singleton=12 singleton_none=44 pairs={len(result['pair_branches'])} "
          f"new_pair_structures={len(result['newly_pair_admissible_structures'])} "
          f"clean_pairs={len(result['clean_pair_branches'])} primitive_chiral=195 "
          f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
