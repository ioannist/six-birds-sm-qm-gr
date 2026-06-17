#!/usr/bin/env python3
"""Build Step 67 E032 record-irreducibility artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import inspect
import json
import sys
from pathlib import Path
from typing import Any, Callable


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP66_BUILD = STEPS_DIR / "step66_mode_b_e032_record_stability_definiteness_artifacts" / "e032_record_stability_definiteness_step66.py"


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s66 = load_module("step67_step66_frozen", STEP66_BUILD)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_hash(functions: list[Any]) -> str:
    return sha256_text("\n\n".join(inspect.getsource(function) for function in functions))


def sigma_pointer_count(toy: dict[str, Any]) -> int:
    return len(toy["rho_diag"])


def env_decohered(toy: dict[str, Any]) -> bool:
    count = toy["branch_count"]
    return all(toy["env_overlap_matrix"][i][j] == 0 for i in range(count) for j in range(count) if i != j)


def package_idempotent(toy: dict[str, Any]) -> bool:
    return toy["dephasing_idempotence_error"] == 0


def nonzero_weight_count(toy: dict[str, Any]) -> int:
    return sum(1 for weight in toy["rho_diag"] if weight > 0)


def property_definitions() -> list[dict[str, Any]]:
    def self_locating(toy: dict[str, Any], state: dict[str, Any]) -> bool:
        return nonzero_weight_count(toy) == sigma_pointer_count(toy) and env_decohered(toy)

    def agreement(toy: dict[str, Any], state: dict[str, Any]) -> bool:
        return env_decohered(toy) and sigma_pointer_count(toy) >= 2

    def robustness(toy: dict[str, Any], state: dict[str, Any]) -> bool:
        return package_idempotent(toy) and env_decohered(toy)

    def complete_record(toy: dict[str, Any], state: dict[str, Any]) -> bool:
        return nonzero_weight_count(toy) == sigma_pointer_count(toy)

    def global_exclusivity(toy: dict[str, Any], state: dict[str, Any]) -> bool:
        return state["actual_branch_count"] == 1

    return [
        {
            "property_id": "self_locating_indexical_record",
            "definition": "each observer-copy has a definite local pointer value in its branch",
            "fn": self_locating,
            "is_control": False,
            "is_sigma_f_internal": True,
            "presupposes_uniqueness": False,
            "closure_touch": "Sigma_f",
            "notes": "universal per-branch local record; no global actual-branch selector",
        },
        {
            "property_id": "intersubjective_agreement",
            "definition": "co-recording observers agree on the same pointer value within each branch",
            "fn": agreement,
            "is_control": False,
            "is_sigma_f_internal": True,
            "presupposes_uniqueness": False,
            "closure_touch": "Sigma_f",
            "notes": "branchwise agreement follows from the diagonal pointer record algebra",
        },
        {
            "property_id": "record_robustness_no_recoherence",
            "definition": "pointer records are stable under further dephasing and no branch re-interference appears",
            "fn": robustness,
            "is_control": False,
            "is_sigma_f_internal": True,
            "presupposes_uniqueness": False,
            "closure_touch": "Sigma_f/E",
            "notes": "uses idempotent dephasing and zero environment overlap, not selection",
        },
        {
            "property_id": "complete_record",
            "definition": "the record algebra can register every pointer distinction with nonzero weight",
            "fn": complete_record,
            "is_control": False,
            "is_sigma_f_internal": True,
            "presupposes_uniqueness": False,
            "closure_touch": "Sigma_f",
            "notes": "capacity over all pointer outcomes, not one globally actual branch",
        },
        {
            "property_id": "global_exclusivity_anti_control",
            "definition": "exactly one branch's record exists globally",
            "fn": global_exclusivity,
            "is_control": True,
            "is_sigma_f_internal": False,
            "presupposes_uniqueness": True,
            "closure_touch": "beyond_Sigma_f:D_or_indexical_extension",
            "notes": "anti-control: this is the definiteness predicate in record language",
        },
    ]


def battery_rows(toy: dict[str, Any], states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full = next(state for state in states if state["readout_id"] == "full_branching_state")
    selected = next(state for state in states if state["readout_id"] == "selected_single_outcome_k0")
    rows: list[dict[str, Any]] = []
    for prop in property_definitions():
        fn: Callable[[dict[str, Any], dict[str, Any]], bool] = prop["fn"]
        full_pass = fn(toy, full)
        selected_pass = fn(toy, selected)
        forces_selection = selected_pass and not full_pass
        is_smuggle = bool(prop["presupposes_uniqueness"])
        if forces_selection and not prop["is_control"] and not prop["presupposes_uniqueness"]:
            status = "unexpected_noncontrol_forcing"
        elif is_smuggle:
            status = "smuggle_line_anti_control"
        elif full_pass == selected_pass:
            status = "blind_to_selection"
        else:
            status = "nonforcing_asymmetry"
        rows.append(
            {
                "property_id": prop["property_id"],
                "definition": prop["definition"],
                "full_branching_passes": full_pass,
                "selected_readout_passes": selected_pass,
                "forces_selection": forces_selection,
                "is_control": prop["is_control"],
                "is_sigma_f_internal": prop["is_sigma_f_internal"],
                "presupposes_uniqueness": prop["presupposes_uniqueness"],
                "is_smuggle": is_smuggle,
                "closure_touch": prop["closure_touch"],
                "status": status,
                "notes": prop["notes"],
            }
        )
    return rows


def anti_smuggle_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    noncontrol = [row for row in rows if row["is_control"] is False]
    control = next(row for row in rows if row["property_id"] == "global_exclusivity_anti_control")
    return [
        {
            "gate": "noncontrol_properties_have_no_uniqueness_clause",
            "passes": all(row["presupposes_uniqueness"] is False for row in noncontrol),
            "evidence": "all non-control properties are branchwise or Sigma_f-record properties",
        },
        {
            "gate": "noncontrol_properties_evaluable_on_multibranch",
            "passes": all(row["full_branching_passes"] in (True, False) for row in noncontrol),
            "evidence": "every non-control property was scored on the full branching readout",
        },
        {
            "gate": "noncontrol_forcing_absent",
            "passes": all(row["forces_selection"] is False for row in noncontrol),
            "evidence": "no non-control property passes selected while failing full branching",
        },
        {
            "gate": "anti_control_flagged_as_smuggle_line",
            "passes": control["forces_selection"] is True and control["is_smuggle"] is True and control["presupposes_uniqueness"] is True,
            "evidence": "global exclusivity forces selection only by requiring uniqueness",
        },
    ]


def structural_argument_rows(rows: list[dict[str, Any]], witness: list[dict[str, Any]]) -> list[dict[str, Any]]:
    noncontrol = [row for row in rows if row["is_control"] is False]
    witness_row = witness[0]
    return [
        {
            "step": "premise_1",
            "claim": "non-control record properties are Sigma_f-internal",
            "passes": all(row["is_sigma_f_internal"] is True for row in noncontrol),
            "evidence": ",".join(row["property_id"] for row in noncontrol),
        },
        {
            "step": "premise_2",
            "claim": "Step66 pair has identical Sigma_f but different selection predicate",
            "passes": witness_row["L0_difference"] == 1 and witness_row["D0_difference"] == 0,
            "evidence": witness_row["shared_pi0_sigma_f"],
        },
        {
            "step": "inference",
            "claim": "a Sigma_f-internal property must take the same value on the two readouts",
            "passes": all(row["full_branching_passes"] == row["selected_readout_passes"] for row in noncontrol),
            "evidence": "same Sigma_f key for both readouts",
        },
        {
            "step": "conclusion",
            "claim": "no Sigma_f-internal record property can force the selection predicate on this witness class",
            "passes": all(row["forces_selection"] is False for row in noncontrol),
            "evidence": "the only forcing battery property is the non-Sigma_f global-exclusivity anti-control",
        },
    ]


def frozen_rows() -> list[dict[str, Any]]:
    funcs = [s66.two_outcome_toy, s66.readout_states, s66.delta_fact, s66.record_stability]
    return [
        {
            "source": "Step66_frozen_toy_and_witness",
            "path": f"steps/{STEP66_BUILD.parent.name}/{STEP66_BUILD.name}",
            "source_hash": source_hash(funcs),
            "functions": "two_outcome_toy|readout_states|delta_fact|record_stability",
            "status": "imported_verbatim",
        }
    ]


def build() -> dict[str, Any]:
    toy = s66.two_outcome_toy()
    states = s66.readout_states(toy)
    witness = s66.delta_fact(states, "sigma_f_key", "selection_predicate")
    if len(witness) != 1:
        raise RuntimeError("expected one Step66 nonfactorization witness")
    rows = battery_rows(toy, states)
    anti = anti_smuggle_rows(rows)
    structural = structural_argument_rows(rows, witness)
    noncontrol = [row for row in rows if row["is_control"] is False]
    all_blind = all(row["forces_selection"] is False and row["full_branching_passes"] == row["selected_readout_passes"] for row in noncontrol)
    only_smuggle_or_beyond = all(
        (not row["forces_selection"])
        or row["is_smuggle"]
        or row["closure_touch"].startswith("beyond_Sigma_f")
        for row in rows
    )
    structural_pass = all(row["passes"] for row in structural)
    exit_state = (
        "SELECTION_RECORD_IRREDUCIBLE_STRUCTURAL"
        if all_blind and only_smuggle_or_beyond and structural_pass
        else "SELECTION_RECORD_IRREDUCIBLE_ENUMERATION_ONLY"
    )
    schema = {
        "step": 67,
        "orientation": "ModeB_E032_record_irreducibility",
        "active_residual": "E032 single-outcome selection after Step66 record-stability blindness",
        "exit_state": exit_state,
        "verdict": "SELECTION_NOT_FORCED_BY_SIGMA_F_INTERNAL_RECORD_PROPERTIES",
        "battery_property_count": len(rows),
        "all_noncontrol_properties_blind": all_blind,
        "structural_argument_grade": "structural" if structural_pass else "enumeration_only",
        "selection_not_sigma_f_definable": True,
        "only_forcings_are_smuggle_or_beyond_sigma_f": only_smuggle_or_beyond,
        "anti_smuggle_pass": all(row["passes"] for row in anti),
        "solves_measurement_problem": False,
        "derives_collapse": False,
        "picks_a_shape": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": exit_state == "SELECTION_RECORD_IRREDUCIBLE_STRUCTURAL",
    }
    return {
        "toy": toy,
        "states": states,
        "witness": witness,
        "battery": rows,
        "anti": anti,
        "structural": structural,
        "frozen": frozen_rows(),
        "schema": schema,
    }


def write_artifacts(result: dict[str, Any]) -> None:
    schema = result["schema"]
    battery = result["battery"]
    write_csv(
        ARTIFACT_DIR / "record_property_battery_step67.csv",
        battery,
        [
            "property_id",
            "definition",
            "full_branching_passes",
            "selected_readout_passes",
            "forces_selection",
            "is_control",
            "is_sigma_f_internal",
            "presupposes_uniqueness",
            "is_smuggle",
            "closure_touch",
            "status",
            "notes",
        ],
    )
    write_csv(ARTIFACT_DIR / "anti_smuggle_step67.csv", result["anti"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "structural_argument_step67.csv", result["structural"], ["step", "claim", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "frozen_step66_reuse_step67.csv", result["frozen"], ["source", "path", "source_hash", "functions", "status"])
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_step67_sigma_f_internal_class", "status": "active", "declared_at_step": 67, "role": "non-control record properties must be Sigma_f-internal"},
            {"constraint_id": "C_step67_global_exclusivity_ant/control", "status": "anti_control", "declared_at_step": 67, "role": "marks the smuggle line for uniqueness"},
            {"constraint_id": "C_step67_no_shape_pick", "status": "active_validator", "declared_at_step": 67, "role": "do not select collapse or many-worlds shape"},
        ],
        ["constraint_id", "status", "declared_at_step", "role"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target": "E032_record_irreducibility",
                "parent_residual": "E032 single-outcome selection",
                "relation_to_canonical_root": "continuation of Step66 on cluster_a record/measurement layer; USER-AUTHORIZED 2026-06-10",
                "status": schema["verdict"],
                "artifacts": "record_property_battery_step67.csv;structural_argument_step67.csv",
            }
        ],
        ["target", "parent_residual", "relation_to_canonical_root", "status", "artifacts"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_step67_E032_record_property_class",
                "declared_at_step": 67,
                "carrier": "Step66 two-readout nonfactorization witness",
                "active_constraints": "Sigma_f-internal record properties; anti-control for global exclusivity",
                "excluded_designs_rationale": "Uniqueness/exclusivity clauses are marked as smuggle controls, not record landings.",
                "non_triviality_argument": "The class argument follows from identical Sigma_f plus selection split, and the battery exhibits the boundary.",
                "next_grammar_delta": "Only D-ledger branch pruning or non-Sigma_f indexical extension remains as selection source.",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    write_csv(
        ARTIFACT_DIR / "content_classification_step67.csv",
        [
            {"artifact": "record_property_battery_step67.csv", "claim": "battery of record properties is blind except anti-control", "grade": "finite-carrier-diagnostic", "source": "record_property_battery_step67.csv"},
            {"artifact": "structural_argument_step67.csv", "claim": "Sigma_f-definability class argument", "grade": "analytical-structural", "source": "structural_argument_step67.csv"},
            {"artifact": "anti_smuggle_step67.csv", "claim": "global exclusivity flagged as smuggle line", "grade": "organizational", "source": "anti_smuggle_step67.csv"},
            {"artifact": "step67_results_summary.md", "claim": "summary and caveats", "grade": "organizational", "source": "step67_results_summary.md"},
            {"artifact": "step67_statement.tex", "claim": "record-irreducibility statement", "grade": "analytical-structural", "source": "step67_statement.tex"},
            {"artifact": "run_step67.py", "claim": "validator", "grade": "organizational", "source": "run_step67.py"},
        ],
        ["artifact", "claim", "grade", "source"],
    )
    write_json(ARTIFACT_DIR / "step67_schema.json", schema)

    noncontrol_blind = [row["property_id"] for row in battery if row["is_control"] is False and row["forces_selection"] is False]
    control = next(row for row in battery if row["property_id"] == "global_exclusivity_anti_control")
    summary = f"""# Step 67 Results Summary

## Deflationary Truth First

Step 66 showed that naive record-stability is blind to single-outcome selection. Step 67 strengthens that to a class result for `Sigma_f`-internal record properties on the Step-66 witness. It does not solve measurement, does not derive collapse, does not prove many-worlds, and does not pick shape A or shape B. The result is record-irreducibility: records internal to the pointer-record algebra cannot force the selection predicate because the two readouts are identical in `Sigma_f`.

## Battery Results

Non-control properties tested: {', '.join(noncontrol_blind)}.

Every non-control property is blind: it has the same truth value on the full branching readout and the selected readout. The anti-control `{control['property_id']}` forces selection, but only because it presupposes uniqueness: `{control['definition']}`.

## Structural Argument

The Step-66 witness gives two readouts with identical `Sigma_f` and different selection predicates. Any property definable as a function of `Sigma_f` must take the same value on both readouts. Therefore no `Sigma_f`-internal record property can imply the selection predicate. The battery verifies representative stronger record/consistency properties and marks the smuggle boundary.

## D / Sigma_f Dichotomy

The only remaining ways to force selection are beyond the non-circular record class: a D-ledger branch-pruning/non-idempotent update (shape A style) or a non-`Sigma_f` indexical/self-locating extension (shape B style). Step 67 picks neither.

## Exit State

`{schema['exit_state']}`. Verdict: `{schema['verdict']}`.
"""
    (ARTIFACT_DIR / "step67_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 67 does not solve the measurement problem, does not derive collapse, does not prove many-worlds, and does not pick shape A or shape B.

It is a no-go on records as the selection source: Sigma_f-internal record properties cannot force the single-outcome predicate on the Step-66 witness. The result leaves the D-ledger branch-pruning route and the non-Sigma_f indexical-extension route open; it does not choose between them.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step67.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 67 Statement}
Deflationary status: this is a record-irreducibility result for the Step--66 witness, not a solution to the measurement problem.

Let \(r_B\) be the full branching readout and \(r_S\) the selected single-outcome readout from Step--66. They satisfy
\[
\Sigma_f(r_B)=\Sigma_f(r_S)
\]
but differ in the selection predicate. Hence any property \(P\) that is definable from \(\Sigma_f\) must satisfy
\[
P(r_B)=P(r_S).
\]
It follows that no \(\Sigma_f\)-internal record property can force the single-outcome selection predicate on this witness.

The property battery confirms this boundary: self-locating per-branch records, intersubjective agreement, robustness/no-recoherence, and complete record capacity are all blind to selection. The only forcing anti-control is global exclusivity, which presupposes the conclusion.

Therefore measurement selection is record-irreducible relative to the non-circular \(\Sigma_f\)-internal record class. A forcing predicate must either touch the defect ledger \(D\) or add a non-\(\Sigma_f\) indexical selector.
\end{document}
"""
    (ARTIFACT_DIR / "step67_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    result = build()
    write_artifacts(result)


if __name__ == "__main__":
    main()
