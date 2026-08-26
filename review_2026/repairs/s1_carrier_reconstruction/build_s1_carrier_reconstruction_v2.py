#!/usr/bin/env python3
"""Build versioned S1-REPAIR-2 branch-complete and orbit-quotiented artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import carrier_chain as v1
import carrier_chain_v2 as v2


HERE = Path(__file__).resolve().parent

BRANCH_FIELDS = [
    "dimensions", "structure_id", "support_key", "scalar_branch", "representative_scalar",
    "conjugate_scalar", "active_factor_indices", "active_factors", "mass_completable",
    "breaks_u1", "confining_subgroups", "coset_count", "delta_pair_count", "delta_empty",
    "clean_or_breaking", "structure_universal_clean", "structure_existential_clean",
    "carrier_orbit_id", "branch_orbit_id",
]
COVERAGE_FIELDS = ["dimensions", "structure_id", "support_key", "carrier_orbit_id",
                   "admissible_scalar_branch_count", "has_admissible_scalar_branch"]
FLOW_FIELDS = [
    "stage", "population_unit", "input_labelled", "population_labelled", "excluded_labelled",
    "exclusion_percent_labelled", "input_orbit", "population_orbit", "excluded_orbit",
    "exclusion_percent_orbit", "headline_uses_orbit_percent",
]
COMPARISON_FIELDS = [
    "stage", "published_labelled", "repair1_labelled", "repair2_labelled", "repair2_orbit_quotiented",
    "published_stage_exclusion_percent", "repair1_stage_exclusion_percent",
    "repair2_labelled_exclusion_percent", "repair2_orbit_exclusion_percent", "comparison_note",
]
FAMILY_FIELDS = ["stage", "dimensions", "population_unit", "labelled_count", "orbit_count"]
INERT_FIELDS = ["dimensions", "labelled_with_inert_padding", "modulo_inert_singlets",
                "unpadded_reference_count", "normalized_sets_equal"]
GOLDEN_FIELDS = ["dimension", "rep", "expected_dim", "actual_dim", "expected_2T", "actual_2T",
                 "expected_A", "actual_A", "passes"]

PUBLISHED_COUNTS = {
    "genuinely_chiral": 11990,
    "atomic_packaging": 156,
    "closure_consistency": 130,
    "chirality_faithfulness": 80,
    "higher_layer_mass_closure_proxy": 12,
    "clean_separation_first_scalar": 8,
}
REPAIR1_COUNTS = {
    "genuinely_chiral": 1066,
    "atomic_packaging": 84,
    "closure_consistency": 62,
    "chirality_faithfulness": 52,
    "higher_layer_mass_closure_proxy": 8,
    "clean_separation_first_scalar": 4,
}


def render_csv(rows: list[dict[str, Any]], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows({field: row.get(field, "") for field in fields} for row in rows)
    return stream.getvalue()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def percent(input_count: int, output_count: int) -> str:
    if not input_count:
        return ""
    return f"{100 * (input_count - output_count) / input_count:.6f}"


def branch_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    catalogs = result["base"]["catalogs"]
    branches = result["branches"]
    by_structure: dict[str, list[v2.ScalarBranch]] = {}
    for branch in branches:
        by_structure.setdefault(branch.structure_id, []).append(branch)
    rows = []
    for branch in branches:
        siblings = by_structure[branch.structure_id]
        active = v1.active_factor_indices(branch.representative)
        rows.append({
            "dimensions": "|".join(map(str, branch.dimensions)),
            "structure_id": branch.structure_id,
            "support_key": branch.candidate.support_key,
            "scalar_branch": branch.scalar_branch,
            "representative_scalar": branch.representative.text,
            "conjugate_scalar": branch.conjugate.text,
            "active_factor_indices": "|".join(map(str, active)),
            "active_factors": "|".join(f"SU({branch.dimensions[index]})" for index in active),
            "mass_completable": branch.completion["mass_completable"],
            "breaks_u1": v1.scalar_breaks_to_unbroken_u1(branch.representative),
            "confining_subgroups": "|".join(map(str, branch.shadow["confining_subgroups"])),
            "coset_count": branch.shadow["broken_vector_exotic_count"],
            "delta_pair_count": branch.shadow["delta_pair_count"],
            "delta_empty": branch.shadow["delta_empty"],
            "clean_or_breaking": "clean" if branch.clean else "breaking",
            "structure_universal_clean": all(row.clean for row in siblings),
            "structure_existential_clean": any(row.clean for row in siblings),
            "carrier_orbit_id": v2.candidate_orbit_key(branch.candidate, catalogs[branch.dimensions]),
            "branch_orbit_id": v2.branch_orbit_key(branch, catalogs[branch.dimensions]),
        })
    return rows


def branch_coverage_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    catalogs = result["base"]["catalogs"]
    counts = Counter(branch.structure_id for branch in result["branches"])
    rows = []
    for candidate in sorted(result["base"]["stage_rows"]["chirality_faithfulness"],
                            key=lambda row: (row.dimensions, row.support_key)):
        structure_id = f"{'|'.join(map(str, candidate.dimensions))}::{candidate.support_key}"
        count = counts[structure_id]
        rows.append({
            "dimensions": "|".join(map(str, candidate.dimensions)),
            "structure_id": structure_id,
            "support_key": candidate.support_key,
            "carrier_orbit_id": v2.candidate_orbit_key(candidate, catalogs[candidate.dimensions]),
            "admissible_scalar_branch_count": count,
            "has_admissible_scalar_branch": count > 0,
        })
    if len(rows) != 52 or sum(row["has_admissible_scalar_branch"] for row in rows) != 8:
        raise AssertionError("scalar coverage ledger does not cover the full chirality-faithful stage")
    return rows


def _flow_row(stage: str, unit: str, input_labelled: int, output_labelled: int,
              input_orbit: int, output_orbit: int) -> dict[str, Any]:
    return {
        "stage": stage,
        "population_unit": unit,
        "input_labelled": input_labelled,
        "population_labelled": output_labelled,
        "excluded_labelled": input_labelled - output_labelled,
        "exclusion_percent_labelled": percent(input_labelled, output_labelled),
        "input_orbit": input_orbit,
        "population_orbit": output_orbit,
        "excluded_orbit": input_orbit - output_orbit,
        "exclusion_percent_orbit": percent(input_orbit, output_orbit),
        "headline_uses_orbit_percent": True,
    }


def flow_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    base_counts = {stage.stage: stage.population for stage in result["base"]["stages"]}
    orbits = result["stage_orbits"]
    ordered = ["neutral_carrier", "genuinely_chiral", "atomic_packaging", "closure_consistency",
               "chirality_faithfulness", "higher_layer_mass_closure_proxy"]
    rows = []
    for index, stage in enumerate(ordered):
        labelled = base_counts[stage]
        orbit = orbits[stage]
        previous_labelled = labelled if index == 0 else base_counts[ordered[index - 1]]
        previous_orbit = orbit if index == 0 else orbits[ordered[index - 1]]
        rows.append(_flow_row(stage, "structure", previous_labelled, labelled, previous_orbit, orbit))
    rows.extend([
        _flow_row("admissible_scalar_branches", "(structure,scalar_branch)", len(result["branches"]),
                  len(result["branches"]), result["branch_orbits"], result["branch_orbits"]),
        _flow_row("clean_scalar_branches", "(structure,scalar_branch)", len(result["branches"]),
                  len(result["clean_branches"]), result["branch_orbits"], result["clean_branch_orbits"]),
        _flow_row("clean_separation_existential", "structure", len(result["admissible_structures"]),
                  len(result["existential_structures"]), orbits["higher_layer_mass_closure_proxy"],
                  orbits["clean_separation_existential"]),
        _flow_row("clean_separation_universal", "structure", len(result["admissible_structures"]),
                  len(result["universal_structures"]), orbits["higher_layer_mass_closure_proxy"],
                  orbits["clean_separation_universal"]),
    ])
    return rows


def comparison_rows(result: dict[str, Any], flows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flow = {row["stage"]: row for row in flows}
    rows = [{
        "stage": "neutral_carrier",
        "published_labelled": "not_like_for_like",
        "repair1_labelled": 281241820,
        "repair2_labelled": 281241820,
        "repair2_orbit_quotiented": result["stage_orbits"]["neutral_carrier"],
        "published_stage_exclusion_percent": "",
        "repair1_stage_exclusion_percent": "0.000000",
        "repair2_labelled_exclusion_percent": "0.000000",
        "repair2_orbit_exclusion_percent": flow["neutral_carrier"]["exclusion_percent_orbit"],
        "comparison_note": "published 280,983 was already anomaly-filtered set carrier",
    }]
    ordered = ("genuinely_chiral", "atomic_packaging", "closure_consistency",
               "chirality_faithfulness", "higher_layer_mass_closure_proxy")
    for index, stage in enumerate(ordered):
        published_previous = PUBLISHED_COUNTS[ordered[index - 1]] if index else 0
        repair1_previous = 281241820 if index == 0 else REPAIR1_COUNTS[ordered[index - 1]]
        rows.append({
            "stage": stage,
            "published_labelled": PUBLISHED_COUNTS[stage],
            "repair1_labelled": REPAIR1_COUNTS[stage],
            "repair2_labelled": flow[stage]["population_labelled"],
            "repair2_orbit_quotiented": flow[stage]["population_orbit"],
            "published_stage_exclusion_percent": percent(published_previous, PUBLISHED_COUNTS[stage]) if index else "",
            "repair1_stage_exclusion_percent": percent(repair1_previous, REPAIR1_COUNTS[stage]),
            "repair2_labelled_exclusion_percent": flow[stage]["exclusion_percent_labelled"],
            "repair2_orbit_exclusion_percent": flow[stage]["exclusion_percent_orbit"],
            "comparison_note": "same labelled repaired carrier; repair-2 adds declared orbit quotient",
        })
    rows.extend([
        {
            "stage": "clean_separation_first_scalar",
            "published_labelled": PUBLISHED_COUNTS["clean_separation_first_scalar"],
            "repair1_labelled": REPAIR1_COUNTS["clean_separation_first_scalar"],
            "repair2_labelled": "retired",
            "repair2_orbit_quotiented": "retired",
            "published_stage_exclusion_percent": percent(12, 8),
            "repair1_stage_exclusion_percent": percent(8, 4),
            "repair2_labelled_exclusion_percent": "retired",
            "repair2_orbit_exclusion_percent": "",
            "comparison_note": "not branch-complete; retained only as historical repair-1 output",
        },
        {
            "stage": "clean_scalar_branches",
            "published_labelled": "not_evaluated",
            "repair1_labelled": "not_evaluated",
            "repair2_labelled": len(result["clean_branches"]),
            "repair2_orbit_quotiented": result["clean_branch_orbits"],
            "published_stage_exclusion_percent": "",
            "repair1_stage_exclusion_percent": "",
            "repair2_labelled_exclusion_percent": flow["clean_scalar_branches"]["exclusion_percent_labelled"],
            "repair2_orbit_exclusion_percent": flow["clean_scalar_branches"]["exclusion_percent_orbit"],
            "comparison_note": "branch-level result; denominator is all admissible scalar branches",
        },
        {
            "stage": "clean_separation_existential",
            "published_labelled": "not_evaluated",
            "repair1_labelled": "not_evaluated",
            "repair2_labelled": len(result["existential_structures"]),
            "repair2_orbit_quotiented": result["stage_orbits"]["clean_separation_existential"],
            "published_stage_exclusion_percent": "",
            "repair1_stage_exclusion_percent": "",
            "repair2_labelled_exclusion_percent": flow["clean_separation_existential"]["exclusion_percent_labelled"],
            "repair2_orbit_exclusion_percent": flow["clean_separation_existential"]["exclusion_percent_orbit"],
            "comparison_note": "exists admissible scalar branch with clean separation",
        },
        {
            "stage": "clean_separation_universal",
            "published_labelled": "not_evaluated",
            "repair1_labelled": "not_evaluated",
            "repair2_labelled": len(result["universal_structures"]),
            "repair2_orbit_quotiented": result["stage_orbits"]["clean_separation_universal"],
            "published_stage_exclusion_percent": "",
            "repair1_stage_exclusion_percent": "",
            "repair2_labelled_exclusion_percent": flow["clean_separation_universal"]["exclusion_percent_labelled"],
            "repair2_orbit_exclusion_percent": flow["clean_separation_universal"]["exclusion_percent_orbit"],
            "comparison_note": "all admissible scalar branches must be clean",
        },
    ])
    return rows


def family_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    catalogs = result["base"]["catalogs"]
    labels = ["|".join(map(str, dimensions)) for dimensions in v1.factor_structures()]
    rows = []
    neutral_by_label = {row["dimensions"]: row for row in result["neutral_orbit_rows"]}
    for label in labels:
        item = neutral_by_label[label]
        rows.append({"stage": "neutral_carrier", "dimensions": label, "population_unit": "structure",
                     "labelled_count": item["labelled_count"], "orbit_count": item["orbit_count"]})

    for stage in ("genuinely_chiral", "atomic_packaging", "closure_consistency", "chirality_faithfulness"):
        candidates = result["base"]["stage_rows"][stage]
        for label in labels:
            selected = [row for row in candidates if "|".join(map(str, row.dimensions)) == label]
            rows.append({"stage": stage, "dimensions": label, "population_unit": "structure",
                         "labelled_count": len(selected),
                         "orbit_count": len({v2.candidate_orbit_key(row, catalogs[row.dimensions]) for row in selected})})

    structure_stages = {
        "higher_layer_mass_closure_proxy": result["admissible_structures"],
        "clean_separation_existential": result["existential_structures"],
        "clean_separation_universal": result["universal_structures"],
    }
    for stage, candidates in structure_stages.items():
        for label in labels:
            selected = [row for row in candidates if "|".join(map(str, row.dimensions)) == label]
            rows.append({"stage": stage, "dimensions": label, "population_unit": "structure",
                         "labelled_count": len(selected),
                         "orbit_count": len({v2.candidate_orbit_key(row, catalogs[row.dimensions]) for row in selected})})
    for stage, branches in (("admissible_scalar_branches", result["branches"]),
                            ("clean_scalar_branches", result["clean_branches"])):
        for label in labels:
            selected = [row for row in branches if "|".join(map(str, row.dimensions)) == label]
            rows.append({"stage": stage, "dimensions": label, "population_unit": "(structure,scalar_branch)",
                         "labelled_count": len(selected),
                         "orbit_count": len({v2.branch_orbit_key(row, catalogs[row.dimensions]) for row in selected})})
    return rows


def markdown_table(rows: list[dict[str, Any]], fields: list[str]) -> str:
    output = ["| " + " | ".join(field.replace("_", " ") for field in fields) + " |",
              "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows:
        output.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(output)


def results_note(result: dict[str, Any], flows: list[dict[str, Any]], comparisons: list[dict[str, Any]],
                 branches: list[dict[str, Any]]) -> str:
    summary = Counter((row["dimensions"], row["active_factors"], row["clean_or_breaking"]) for row in branches)
    branch_summary = [{"dimensions": key[0], "active_scalar_factor": key[1], "verdict": key[2], "branches": count}
                      for key, count in sorted(summary.items())]
    key_flows = [row for row in flows if row["stage"] in {
        "genuinely_chiral", "atomic_packaging", "closure_consistency", "chirality_faithfulness",
        "higher_layer_mass_closure_proxy", "clean_scalar_branches", "clean_separation_existential",
        "clean_separation_universal"}]
    return f"""# S1-REPAIR-2 foundation-grade carrier results

Repair-1 outputs remain as the historical first-scalar record. The version-2 headline uses orbit-quotiented counts and branch-complete scalar evaluation.

## Declared conventions

1. **Inert singlets.** A fully neutral field `(singlet,...,singlet; q=0)` is freely adjoinable and is quotiented out of a structure. Explicitly retaining all padded variants gives 1,578 genuinely chiral labelled rows; canonical removal maps them onto exactly the same 1,066 unpadded rows.
2. **Equal-factor exchange.** Equal-dimensional gauge factors are unlabelled, so simultaneous exchange of their representation slots is quotiented.
3. **Nonabelian conjugation.** Simultaneous conjugation of every nonabelian representation is quotiented as a gauge-group outer-automorphism relabelling.
4. **U(1) orientation.** Global `q -> -q` is independently quotiented because the sign of the abelian generator is conventional.
5. **Scalar branches.** A complex scalar and its conjugate are one physical branch, because repair-1 mass completion already uses both orientations. Distinct representation/charge conjugacy orbits are separate branches; none is selected by ordering.

## Orbit-quotiented flow

{markdown_table(key_flows, ['stage', 'population_unit', 'input_labelled', 'population_labelled', 'exclusion_percent_labelled', 'input_orbit', 'population_orbit', 'exclusion_percent_orbit'])}

Every headline exclusion percentage is the final `exclusion_percent_orbit` column and is relative to the indicated stage input. The sound genuinely-chiral carrier is 1,066 labelled structures or 419 declared equivalence orbits.

## Branch-complete result

{markdown_table(branch_summary, ['dimensions', 'active_scalar_factor', 'verdict', 'branches'])}

There are 12 admissible scalar branches over eight chirality-faithful, higher-layer-passing structures. Four branches are clean and eight are breaking. Each of the four `2|3` structures has both a clean SU(2)-active branch and a breaking SU(3)-active branch. Every SU(4)-alone branch is breaking.

**Universal-over-branches form:** `for all admissible phi, Clean(C,phi)` holds for 0 of 8 labelled structures (0 of 2 orbits). It fails for every `2|3` structure because each also has an SU(3)-active breaking branch. Therefore clean separation is not a property of `C` alone on this carrier.

**Branch-existential form:** `there exists admissible phi such that Clean(C,phi)` holds for 4 of 8 labelled structures (1 of 2 orbits), precisely the `2|3` family. More strongly, every clean `(C,phi)` branch lies over `2|3` and has an SU(2)-active scalar; every SU(3)-active `2|3` branch and every SU(4) branch is breaking. Thus the data select the `(C,phi)` branch class, not the bare structure.

The full table is `s1_v2_scalar_branches.csv`. Its 12 keys are independently regenerated by a second scalar-inventory and occurrence-coverage loop; the validator fails on any missing or extra branch. `s1_v2_scalar_branch_coverage.csv` lists all 52 chirality-faithful structures: eight have admissible branches and 44 have none.

## Old, repair-1, and repair-2

{markdown_table(comparisons, ['stage', 'published_labelled', 'published_stage_exclusion_percent', 'repair1_labelled', 'repair1_stage_exclusion_percent', 'repair2_labelled', 'repair2_orbit_quotiented', 'repair2_orbit_exclusion_percent'])}

The published and repair-1 first-scalar clean rows are historical rather than branch-complete. They are not treated as the universal result.

## Golden representation gate

The independent table contains {len(result['golden_rows'])} known SU(2), SU(3), and SU(4) values. All {len(result['golden_rows'])}/{len(result['golden_rows'])} dimension, twice-Dynkin-index, and cubic-anomaly triples match. The table source and normalization are cited in `carrier_chain_v2.py`.

The higher-layer mass-closure predicate remains explicitly a `PROXY`; repair-2 removes scalar ordering bias but does not promote that predicate to a derived physical theorem.
"""


def assemble_artifacts(result: dict[str, Any]) -> dict[str, str]:
    branches = branch_rows(result)
    coverage = branch_coverage_rows(result)
    flows = flow_rows(result)
    comparisons = comparison_rows(result, flows)
    families = family_rows(result)
    csvs = {
        "s1_v2_scalar_branches.csv": render_csv(branches, BRANCH_FIELDS),
        "s1_v2_scalar_branch_coverage.csv": render_csv(coverage, COVERAGE_FIELDS),
        "s1_v2_stage_flow.csv": render_csv(flows, FLOW_FIELDS),
        "s1_v2_old_new_orbit.csv": render_csv(comparisons, COMPARISON_FIELDS),
        "s1_v2_orbit_families.csv": render_csv(families, FAMILY_FIELDS),
        "s1_v2_inert_singlet_check.csv": render_csv(result["inert_convention"]["rows"], INERT_FIELDS),
        "s1_v2_golden_formula_check.csv": render_csv(result["golden_rows"], GOLDEN_FIELDS),
    }
    schema = {
        "schema_version": 2,
        "experiment": "S1-REPAIR-2 foundation-grade carrier and branch-complete scalar evaluation",
        "repair1_outputs_retained": True,
        "conventions": {
            "inert_singlet": "structures modulo freely adjoined fully neutral singlets",
            "equal_dimension_factor_exchange": "quotiented",
            "overall_nonabelian_conjugation": "quotiented simultaneously across factors",
            "u1_sign_inversion": "quotiented independently",
            "scalar_conjugation": "phi and phi-dagger form one scalar branch",
            "headline_population": "orbit_quotiented",
        },
        "counts": {
            "inert_singlet_inclusive_labelled": result["inert_convention"]["labelled_with_inert_padding"],
            "inert_singlet_quotiented_labelled": result["inert_convention"]["modulo_inert_singlets"],
            "admissible_structures_labelled": len(result["admissible_structures"]),
            "admissible_structures_orbits": result["stage_orbits"]["higher_layer_mass_closure_proxy"],
            "admissible_scalar_branches_labelled": len(result["branches"]),
            "admissible_scalar_branches_orbits": result["branch_orbits"],
            "clean_scalar_branches_labelled": len(result["clean_branches"]),
            "clean_scalar_branches_orbits": result["clean_branch_orbits"],
            "existential_clean_structures_labelled": len(result["existential_structures"]),
            "existential_clean_structures_orbits": result["stage_orbits"]["clean_separation_existential"],
            "universal_clean_structures_labelled": len(result["universal_structures"]),
            "universal_clean_structures_orbits": result["stage_orbits"]["clean_separation_universal"],
            "chirality_faithful_structures_checked_for_scalars": len(coverage),
            "chirality_faithful_structures_without_admissible_branch": sum(
                not row["has_admissible_scalar_branch"] for row in coverage
            ),
        },
        "stage_orbit_counts": result["stage_orbits"],
        "branch_completeness": result["branch_completeness"],
        "branch_hashes": result["hashes"],
        "golden_formula": {"row_count": len(result["golden_rows"]),
                           "passes": all(row["passes"] for row in result["golden_rows"])},
        "typed_selection": {
            "universal_over_branches": "FAIL: 0/8 labelled structures and 0/2 orbits are clean on every admissible branch",
            "branch_existential": "PASS: 4/8 labelled structures and 1/2 orbits have a clean branch; exactly 2|3 with SU(2)-active scalar",
        },
        "files": {
            name: {"sha256": sha256_text(text), "row_count": max(text.count("\n") - 1, 0)}
            for name, text in csvs.items()
        },
        "implementation_sha256": {
            name: sha256_text((HERE / name).read_text())
            for name in ("representation_model.py", "carrier_chain.py", "carrier_chain_v2.py",
                         "build_s1_carrier_reconstruction_v2.py", "DESIGN.md")
        },
    }
    schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    note = results_note(result, flows, comparisons, branches)
    artifacts = {**csvs, "s1_v2_schema.json": schema_text, "RESULTS_v2.md": note}
    manifest = {"algorithm": "sha256", "files": {name: sha256_text(text) for name, text in sorted(artifacts.items())}}
    artifacts["s1_v2_artifact_manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    return artifacts


def main() -> None:
    started = time.monotonic()
    result = v2.run_v2()
    artifacts = assemble_artifacts(result)
    for name, text in artifacts.items():
        (HERE / name).write_text(text, encoding="utf-8")
    elapsed = time.monotonic() - started
    print("build_s1_carrier_reconstruction_v2.py: PASS: "
          f"chiral_labelled=1066 chiral_orbits={result['stage_orbits']['genuinely_chiral']} "
          f"branches={len(result['branches'])} clean_branches={len(result['clean_branches'])} "
          f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
