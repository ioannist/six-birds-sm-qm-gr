#!/usr/bin/env python3
"""Build Step 66 E032 record-stability/definiteness artifacts."""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
CARD_PATH = THREAD_DIR.parents[0] / "missing_layers" / "cards" / "E032.json"
PAPER_PATH = THREAD_DIR.parents[1] / "Tsiokos_2026_A_Six_Birds_Eye_View_of_Quantum_Theory_Operational_Closure_Semantics_for_Measurement_Contextuality_and_Record_Stability.tex"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def frac_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def two_outcome_toy() -> dict[str, Any]:
    weights = [Fraction(1, 3), Fraction(2, 3)]
    amplitudes = ["sqrt(1/3)", "sqrt(2/3)"]
    branches = [
        {
            "branch_id": f"k{index}",
            "system": f"s{index}",
            "apparatus": f"a{index}",
            "environment": f"env{index}",
            "amplitude": amplitudes[index],
            "born_weight": weights[index],
        }
        for index in range(2)
    ]
    return {
        "branch_count": len(branches),
        "branches": branches,
        "env_overlap_matrix": [[Fraction(1, 1), Fraction(0, 1)], [Fraction(0, 1), Fraction(1, 1)]],
        "rho_diag": tuple(weights),
        "dephasing_idempotence_error": Fraction(0, 1),
    }


def sigma_f_key(toy: dict[str, Any]) -> str:
    weights = "|".join(frac_text(value) for value in toy["rho_diag"])
    return f"pointer_basis=a0|a1;born_weights={weights};rho_diag={weights};expectation_pointer={frac_text(toy['rho_diag'][1])}"


def readout_states(toy: dict[str, Any]) -> list[dict[str, Any]]:
    sigma = sigma_f_key(toy)
    return [
        {
            "readout_id": "full_branching_state",
            "shape_reading": "B_QM_substrate_many_worlds_like",
            "sigma_f_key": sigma,
            "selection_predicate": "no_single_global_actual_branch",
            "selected_outcome": "none",
            "actual_branch_count": toy["branch_count"],
            "D_touch": "none",
            "Sigma_f_touch": "none",
        },
        {
            "readout_id": "selected_single_outcome_k0",
            "shape_reading": "A_or_indexical_selected_readout",
            "sigma_f_key": sigma,
            "selection_predicate": "selected:k0",
            "selected_outcome": "k0",
            "actual_branch_count": 1,
            "D_touch": "D_if_branch_pruning_or_Sigma_f_if_indexical_only",
            "Sigma_f_touch": "selection_index_added_if_shape_B",
        },
    ]


def delta_fact(states: list[dict[str, Any]], pi0: str, pi1: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in combinations(states, 2):
        if left[pi0] == right[pi0] and left[pi1] != right[pi1]:
            rows.append(
                {
                    "witness_id": f"w{len(rows)}",
                    "left_readout": left["readout_id"],
                    "right_readout": right["readout_id"],
                    "shared_pi0_sigma_f": left[pi0],
                    "left_pi1_selection": left[pi1],
                    "right_pi1_selection": right[pi1],
                    "L0_difference": 1,
                    "D0_difference": 0,
                }
            )
    return rows


def record_stability(toy: dict[str, Any], state: dict[str, Any]) -> dict[str, Any]:
    # This requirement is intentionally nonselective: it asks whether the pointer
    # value records are stable and distinguishable in the record algebra. It does
    # not ask that exactly one pointer value is globally actual.
    env = toy["env_overlap_matrix"]
    branch_count = toy["branch_count"]
    persistence = toy["dephasing_idempotence_error"] == 0 and all(env[i][i] == 1 for i in range(branch_count))
    distinguishability = all(env[i][j] == 0 for i in range(branch_count) for j in range(branch_count) if i != j)
    capacity = branch_count >= 2
    per_branch_records = [
        f"{branch['apparatus']}:{'persistent' if persistence else 'unstable'}:{'distinguishable' if distinguishability else 'aliased'}"
        for branch in toy["branches"]
    ]
    return {
        "readout_id": state["readout_id"],
        "selection_predicate": state["selection_predicate"],
        "persistence_passes": persistence,
        "distinguishability_passes": distinguishability,
        "capacity_passes": capacity,
        "record_stability_passes": persistence and distinguishability and capacity,
        "actual_branch_count": state["actual_branch_count"],
        "record_tokens": "|".join(per_branch_records),
        "requires_single_outcome": False,
        "closure_slot_touched_by_record_requirement": "Sigma_f",
    }


def d_vs_sigma_location(record_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    diagonal_pass = next(row for row in record_rows if row["readout_id"] == "full_branching_state")
    selected_pass = next(row for row in record_rows if row["readout_id"] == "selected_single_outcome_k0")
    if diagonal_pass["record_stability_passes"] and selected_pass["record_stability_passes"]:
        return [
            {
                "property": "nonselective_record_stability",
                "forces_definiteness": False,
                "closure_slot": "Sigma_f",
                "evidence": "uses pointer record algebra and diagonal weights only; full branching and selected readouts both pass",
            },
            {
                "property": "single_outcome_selection",
                "forces_definiteness": True,
                "closure_slot": "D_or_Sigma_f depending on shape",
                "evidence": "branch pruning would touch D; indexical selection would enrich Sigma_f; not forced by record-stability",
            },
        ]
    return [
        {
            "property": "record_stability_forcing_candidate",
            "forces_definiteness": True,
            "closure_slot": "D",
            "evidence": "would require a nonselective-to-selective update; scrutinize for smuggle",
        }
    ]


def anti_smuggle_rows(record_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    diagonal = next(row for row in record_rows if row["readout_id"] == "full_branching_state")
    return [
        {
            "gate": "record_requirement_has_no_uniqueness_clause",
            "passes": all(row["requires_single_outcome"] is False for row in record_rows),
            "evidence": "record predicate checks persistence/distinguishability/capacity only",
        },
        {
            "gate": "diagonal_ensemble_evaluable",
            "passes": diagonal["record_stability_passes"],
            "evidence": "full branching state has persistent distinguishable pointer records",
        },
        {
            "gate": "component_conditions_satisfied_by_multibranch",
            "passes": diagonal["persistence_passes"] and diagonal["distinguishability_passes"] and diagonal["capacity_passes"],
            "evidence": "persistence, distinguishability, and capacity all pass before selecting one outcome",
        },
        {
            "gate": "single_outcome_not_presupposed",
            "passes": diagonal["actual_branch_count"] > 1 and diagonal["record_stability_passes"],
            "evidence": "multi-branch readout passes the record requirement",
        },
    ]


def source_rows() -> list[dict[str, Any]]:
    card = json.loads(CARD_PATH.read_text(encoding="utf-8"))
    return [
        {
            "source": "E032_card",
            "path": "physics_atlas/missing_layers/cards/E032.json",
            "used_for": "non-descending selection object and B.2 witness",
            "detail": card["edge_tier"] + ":" + card["summary_verdict"][:120],
        },
        {
            "source": "QM_record_stability_paper",
            "path": PAPER_PATH.name,
            "used_for": "QM closure package and record-stability packaging treatment",
            "detail": "dephasing as idempotent nonselective record packaging; selected outcome as conditioning/refinement",
        },
    ]


def build() -> dict[str, Any]:
    toy = two_outcome_toy()
    states = readout_states(toy)
    witness = delta_fact(states, "sigma_f_key", "selection_predicate")
    record_rows = [record_stability(toy, state) for state in states]
    anti = anti_smuggle_rows(record_rows)
    location = d_vs_sigma_location(record_rows)
    diagonal_pass = next(row for row in record_rows if row["readout_id"] == "full_branching_state")["record_stability_passes"]
    selected_pass = next(row for row in record_rows if row["readout_id"] == "selected_single_outcome_k0")["record_stability_passes"]
    exit_state = "RECORD_STABILITY_BLIND_TO_SELECTION" if diagonal_pass and selected_pass else "RECORD_STABILITY_FORCES_DEFINITENESS"
    schema = {
        "step": 66,
        "orientation": "ModeB_E032_record_stability_definiteness",
        "active_residual": "E032 single-outcome selection",
        "exit_state": exit_state,
        "verdict": "NAIVE_RECORD_STABILITY_DOES_NOT_FORCE_SINGLE_OUTCOME" if exit_state == "RECORD_STABILITY_BLIND_TO_SELECTION" else "RECORD_STABILITY_FORCES_SELECTION_ON_TOY",
        "nonfactorization_witness_reproduced": len(witness) == 1,
        "record_stability_on_diagonal_ensemble": bool(diagonal_pass),
        "record_stability_on_selected_only": bool(selected_pass and not diagonal_pass),
        "anti_smuggle_pass": all(row["passes"] for row in anti),
        "forcing_touches_D_or_Sigma_f": "none" if exit_state == "RECORD_STABILITY_BLIND_TO_SELECTION" else "D",
        "solves_measurement_problem": False,
        "derives_collapse": False,
        "picks_a_shape": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
    }
    return {
        "toy": toy,
        "states": states,
        "witness": witness,
        "record_rows": record_rows,
        "anti": anti,
        "location": location,
        "schema": schema,
        "sources": source_rows(),
    }


def write_artifacts(result: dict[str, Any]) -> None:
    toy = result["toy"]
    schema = result["schema"]
    write_csv(
        ARTIFACT_DIR / "qm_measurement_toy_step66.csv",
        [
            {
                "branch_id": branch["branch_id"],
                "system": branch["system"],
                "apparatus": branch["apparatus"],
                "environment": branch["environment"],
                "amplitude": branch["amplitude"],
                "born_weight": frac_text(branch["born_weight"]),
                "env_overlap_with_other": frac_text(toy["env_overlap_matrix"][index][1 - index]),
            }
            for index, branch in enumerate(toy["branches"])
        ],
        ["branch_id", "system", "apparatus", "environment", "amplitude", "born_weight", "env_overlap_with_other"],
    )
    write_csv(
        ARTIFACT_DIR / "closure_package_step66.csv",
        [
            {"slot": "Z", "definition": "density matrices/readout fibers over a two-branch system-apparatus-environment toy", "computed_value": "two decohered branches"},
            {"slot": "f", "definition": "diagonal pointer-basis lens", "computed_value": "pointer_basis=a0|a1"},
            {"slot": "Sigma_f", "definition": "Born weights, diagonal distribution, pointer expectation values; no selected index", "computed_value": sigma_f_key(toy)},
            {"slot": "E", "definition": "idempotent dephasing channel on pointer basis", "computed_value": f"idempotence_error={frac_text(toy['dephasing_idempotence_error'])}"},
            {"slot": "D", "definition": "defect ledger for non-idempotent/branch-pruning changes", "computed_value": "unchanged in nonselective packaging"},
        ],
        ["slot", "definition", "computed_value"],
    )
    write_csv(
        ARTIFACT_DIR / "readout_states_step66.csv",
        result["states"],
        ["readout_id", "shape_reading", "sigma_f_key", "selection_predicate", "selected_outcome", "actual_branch_count", "D_touch", "Sigma_f_touch"],
    )
    write_csv(
        ARTIFACT_DIR / "nonfactorization_witness_step66.csv",
        result["witness"],
        ["witness_id", "left_readout", "right_readout", "shared_pi0_sigma_f", "left_pi1_selection", "right_pi1_selection", "L0_difference", "D0_difference"],
    )
    write_csv(
        ARTIFACT_DIR / "record_stability_scores_step66.csv",
        result["record_rows"],
        ["readout_id", "selection_predicate", "persistence_passes", "distinguishability_passes", "capacity_passes", "record_stability_passes", "actual_branch_count", "record_tokens", "requires_single_outcome", "closure_slot_touched_by_record_requirement"],
    )
    write_csv(
        ARTIFACT_DIR / "D_vs_Sigma_location_step66.csv",
        result["location"],
        ["property", "forces_definiteness", "closure_slot", "evidence"],
    )
    write_csv(ARTIFACT_DIR / "anti_smuggle_step66.csv", result["anti"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "source_readings_step66.csv", result["sources"], ["source", "path", "used_for", "detail"])
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_step66_no_single_outcome_smuggle", "status": "active", "declared_at_step": 66, "role": "record predicate cannot require uniqueness"},
            {"constraint_id": "C_step66_nonfactorization_witness", "status": "active", "declared_at_step": 66, "role": "Sigma_f-identical readouts split by selection predicate"},
            {"constraint_id": "C_step66_D_vs_Sigma_location", "status": "active", "declared_at_step": 66, "role": "forcing selection must locate in D or Sigma_f; naive record stability touches neither"},
        ],
        ["constraint_id", "status", "declared_at_step", "role"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target": "E032_record_stability_definiteness",
                "parent_residual": "E032 single-outcome selection",
                "relation_to_canonical_root": "NEW residual on Cluster A track; record/measurement layer reached by Steps57-59; USER-AUTHORIZED 2026-06-10",
                "status": schema["verdict"],
                "artifacts": "record_stability_scores_step66.csv;nonfactorization_witness_step66.csv",
            }
        ],
        ["target", "parent_residual", "relation_to_canonical_root", "status", "artifacts"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_step66_E032_record_outcome_toy",
                "declared_at_step": 66,
                "carrier": "finite two-outcome system-apparatus-environment measurement toy",
                "active_constraints": "QM closure package; nonselective dephasing; record persistence/distinguishability/capacity; selection predicate fiber",
                "excluded_designs_rationale": "No single-outcome uniqueness clause is allowed inside record-stability.",
                "non_triviality_argument": "The toy can distinguish Sigma_f-identical readouts by selection while record stability remains blind.",
                "next_grammar_delta": "Add a non-circular global fact/indexical or branch-pruning predicate if definiteness is to be selected.",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    write_csv(
        ARTIFACT_DIR / "content_classification_step66.csv",
        [
            {"artifact": "nonfactorization_witness_step66.csv", "claim": "E032 B.2 witness reproduced on finite toy", "grade": "finite-carrier-diagnostic", "source": "nonfactorization_witness_step66.csv"},
            {"artifact": "record_stability_scores_step66.csv", "claim": "record-stability blind to selection on both readouts", "grade": "finite-carrier-diagnostic", "source": "record_stability_scores_step66.csv"},
            {"artifact": "D_vs_Sigma_location_step66.csv", "claim": "forcing definiteness would need D or Sigma_f enrichment; naive record property touches neither", "grade": "analytical-structural", "source": "D_vs_Sigma_location_step66.csv"},
            {"artifact": "step66_results_summary.md", "claim": "summary and caveats", "grade": "organizational", "source": "step66_results_summary.md"},
            {"artifact": "step66_statement.tex", "claim": "typed no-go statement for naive record stability", "grade": "finite-carrier-diagnostic", "source": "step66_statement.tex"},
            {"artifact": "run_step66.py", "claim": "validator", "grade": "organizational", "source": "run_step66.py"},
        ],
        ["artifact", "claim", "grade", "source"],
    )
    write_json(ARTIFACT_DIR / "step66_schema.json", schema)

    summary = f"""# Step 66 Results Summary

## Deflationary Truth First

E032 is the quantum measurement problem. This step does not solve measurement, does not derive collapse, does not prove many-worlds right or wrong, and does not pick shape A or shape B. It makes one construction move continuous with Steps 57-59: test whether record-stability forces the definiteness / single-outcome predicate. It does not. The finite toy shows record-stability is blind to selection: the full branching diagonal ensemble and the selected single-outcome readout both carry stable records.

## Toy and Closure Package

The toy has two decohered branches with Born weights `1/3` and `2/3`: `|Psi> = sqrt(1/3)|s0 a0 env0> + sqrt(2/3)|s1 a1 env1>`, with environment overlaps zero off diagonal. The closure package is:

- `Z`: density/readout-fiber descriptions on the finite system-apparatus-environment toy.
- `f`: diagonal pointer-basis lens.
- `Sigma_f`: diagonal distribution, Born weights, pointer expectation; no selected branch index.
- `E`: idempotent dephasing, idempotence error `0`.
- `D`: unchanged for nonselective packaging.

## Nonfactorization Witness

The full branching readout and the selected `k0` readout have identical `Sigma_f`: `{sigma_f_key(toy)}`. The selection predicate distinguishes them. The witness has `L0_difference=1` and `D0_difference=0`, reproducing the E032 B.2 nonfactorization pattern.

## Record-Stability Test

Record-stability checks persistence, distinguishability, and capacity over pointer-value records. It deliberately contains no single-outcome clause.

- Full branching / diagonal ensemble: record-stability `True`.
- Selected single outcome: record-stability `True`.

Therefore record-stability does not force definiteness. Per-branch records satisfy the naive record requirement, so the many-worlds-like readout is not excluded by records alone.

## D vs Sigma_f Location

The blind record property touches `Sigma_f` only as a nonselective pointer-record algebra. Any property that actually forces definiteness must add something else: either a D-ledger branch-pruning/non-idempotent update (shape A) or a Sigma_f indexical/self-locating selector (shape B). This step picks neither.

## Exit State

`{schema['exit_state']}`. Verdict: `{schema['verdict']}`.
"""
    (ARTIFACT_DIR / "step66_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 66 does not solve the measurement problem, does not derive collapse, does not refute or confirm many-worlds, and does not pick shape A versus shape B.

It shows only that a non-circular record-stability requirement over pointer records is blind to single-outcome selection on the finite E032 toy. If selection is to be forced, a stronger predicate is needed: either a D-ledger branch-pruning update or a Sigma_f indexical/self-locating selector. Records alone do not force selection here.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step66.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 66 Statement}
Deflationary status: this finite construction does not solve the measurement problem or select an interpretation.

On the two-outcome measurement toy, the full branching readout and the selected single-outcome readout have the same \(\Sigma_f\): the same diagonal pointer distribution and Born weights. They differ only by the selection predicate. Hence the E032 nonfactorization witness is reproduced: the selection predicate does not factor through \(\Sigma_f\).

Define record-stability without a uniqueness clause: persistence of the pointer records, distinguishability of the pointer values, and capacity for at least two pointer-value records. This predicate is true on the full branching diagonal ensemble and true on the selected readout. Therefore record-stability is blind to single-outcome selection and does not force definiteness.

Any future forcing predicate must touch either the defect ledger \(D\) (branch pruning / non-idempotent update) or enrich \(\Sigma_f\) with an indexical selector. This step picks neither shape.
\end{document}
"""
    (ARTIFACT_DIR / "step66_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    result = build()
    write_artifacts(result)


if __name__ == "__main__":
    main()
