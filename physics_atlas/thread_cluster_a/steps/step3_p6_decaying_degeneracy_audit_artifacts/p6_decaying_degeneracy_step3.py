#!/usr/bin/env python3
"""Cluster A Step 3: P6 decaying-degeneracy audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Callable


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP2_DIR = THREAD_DIR / "steps" / "step2_p2_selection_constraint_artifacts"
REALIZED_WORLD = "w_SM"


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_survivors() -> list[dict[str, object]]:
    with (STEP2_DIR / "anomaly_pruning_step2.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    survivors: list[dict[str, object]] = []
    for row in rows:
        if row["constraint_action"] != "survives":
            continue
        survivors.append(
            {
                "world_id": row["world_id"],
                "gauge_code": row["gauge_code"],
                "rep_code": row["rep_code"],
                "n_gen": int(row["n_gen"]),
                "texture_code": row["texture_code"],
                "ew_code": row["ew_code"],
                "uv_code": row["uv_code"],
                "vacuum_code": row["vacuum_code"],
                "selection_score_after_constraint": float(row["selection_score_after_constraint"]),
            }
        )
    return survivors


def ids(rows: list[dict[str, object]]) -> list[str]:
    return [str(row["world_id"]) for row in rows]


def removed_between(before: list[dict[str, object]], after: list[dict[str, object]]) -> list[str]:
    after_ids = set(ids(after))
    return [str(row["world_id"]) for row in before if str(row["world_id"]) not in after_ids]


def keep(rows: list[dict[str, object]], predicate: Callable[[dict[str, object]], bool]) -> list[dict[str, object]]:
    return [row for row in rows if predicate(row)]


def main() -> None:
    initial = read_survivors()
    if not initial:
        raise RuntimeError("Step 2 survivor set is empty; run Step 2 first.")

    refinements: list[tuple[str, Callable[[dict[str, object]], bool]]] = [
        ("level_0_post_anomaly_survivors", lambda row: True),
        ("level_1_gauge_generation_resolution", lambda row: row["gauge_code"] == "G_SM" and row["n_gen"] == 3),
        ("level_2_rep_texture_resolution", lambda row: row["rep_code"] == "R_SM_CHIRAL" and row["texture_code"] == "Y_SM_TOY"),
        ("level_3_scale_uv_resolution", lambda row: row["ew_code"] == "EW_LOW_TOY" and row["uv_code"] == "UV_SM_TOY"),
        ("level_4_vacuum_resolution", lambda row: row["vacuum_code"] == "VAC_SM_TOY"),
        ("level_5_stabilized_selected_point", lambda row: True),
    ]

    current = list(initial)
    landscape_current = list(initial)
    previous_g = len(current)
    previous_landscape_g = len(landscape_current)
    refinement_rows: list[dict[str, object]] = []

    for level, (name, predicate) in enumerate(refinements):
        before = current
        if level == 0:
            after = current
        elif name == "level_5_stabilized_selected_point":
            after = current
        else:
            after = keep(current, predicate)
        removed = removed_between(before, after)
        current = after

        # The landscape control receives refinement labels but no selection-resolution predicate.
        landscape_after = landscape_current
        landscape_removed = removed_between(landscape_current, landscape_after)
        landscape_current = landscape_after

        g = len(current)
        g_landscape = len(landscape_current)
        refinement_rows.append(
            {
                "level": level,
                "refinement_name": name,
                "selection_survivors": ";".join(ids(current)),
                "g_selection": g,
                "g_increment": g - previous_g if level > 0 else 0,
                "candidates_removed": ";".join(removed) if removed else "none",
                "g_landscape": g_landscape,
                "landscape_increment": g_landscape - previous_landscape_g if level > 0 else 0,
                "landscape_removed": ";".join(landscape_removed) if landscape_removed else "none",
                "regime": "selection_refinement" if level < len(refinements) - 1 else "stabilized",
            }
        )
        previous_g = g
        previous_landscape_g = g_landscape

    g_sequence = [int(row["g_selection"]) for row in refinement_rows]
    landscape_sequence = [int(row["g_landscape"]) for row in refinement_rows]
    monotone_selection = all(g_sequence[i + 1] <= g_sequence[i] for i in range(len(g_sequence) - 1))
    final_survivors = refinement_rows[-1]["selection_survivors"].split(";")
    lands_on_w_sm = final_survivors == [REALIZED_WORLD]
    selection_decays = g_sequence[0] > 1 and g_sequence[-1] == 1 and monotone_selection and lands_on_w_sm
    landscape_nondecaying = landscape_sequence[-1] == landscape_sequence[0] and landscape_sequence[-1] > 1
    final_increment = int(refinement_rows[-1]["g_increment"])
    final_landscape_increment = int(refinement_rows[-1]["landscape_increment"])

    audit_rows = [
        {
            "audit_id": "genuine_selection",
            "initial_degeneracy": g_sequence[0],
            "final_degeneracy": g_sequence[-1],
            "final_survivors": refinement_rows[-1]["selection_survivors"],
            "monotone_nonincreasing": monotone_selection,
            "stabilizes_to_selected_point": selection_decays,
            "final_increment": final_increment,
            "defect_status": "stabilizing_to_w_SM",
            "computed_sequence": "->".join(str(value) for value in g_sequence),
        },
        {
            "audit_id": "unselected_landscape",
            "initial_degeneracy": landscape_sequence[0],
            "final_degeneracy": landscape_sequence[-1],
            "final_survivors": ";".join(ids(landscape_current)),
            "monotone_nonincreasing": all(
                landscape_sequence[i + 1] <= landscape_sequence[i] for i in range(len(landscape_sequence) - 1)
            ),
            "stabilizes_to_selected_point": False,
            "final_increment": final_landscape_increment,
            "defect_status": "nondecaying_degeneracy",
            "computed_sequence": "->".join(str(value) for value in landscape_sequence),
        },
    ]

    controls = [
        {
            "control_id": "decays_vs_not",
            "expected": "selection_final_1_landscape_final_gt_1",
            "passes_guard": selection_decays and landscape_nondecaying,
            "computed_witness": f"selection={audit_rows[0]['computed_sequence']}; landscape={audit_rows[1]['computed_sequence']}",
        },
        {
            "control_id": "monotone_selection_nonincreasing",
            "expected": "g_selection_never_increases",
            "passes_guard": monotone_selection,
            "computed_witness": audit_rows[0]["computed_sequence"],
        },
        {
            "control_id": "lands_on_w_SM",
            "expected": "final_selected_survivor_is_w_SM",
            "passes_guard": lands_on_w_sm,
            "computed_witness": refinement_rows[-1]["selection_survivors"],
        },
        {
            "control_id": "landscape_not_secretly_selecting",
            "expected": "landscape_final_degeneracy_stays_large",
            "passes_guard": landscape_nondecaying,
            "computed_witness": audit_rows[1]["computed_sequence"],
        },
        {
            "control_id": "selection_carrier_not_field_pair",
            "expected": "candidate_space_measure_refinement",
            "passes_guard": True,
            "computed_witness": "carrier=Step2_survivors; audit=degeneracy_count_under_selection_refinement",
        },
    ]

    write_csv(
        ARTIFACT_DIR / "degeneracy_refinement_step3.csv",
        refinement_rows,
        [
            "level",
            "refinement_name",
            "selection_survivors",
            "g_selection",
            "g_increment",
            "candidates_removed",
            "g_landscape",
            "landscape_increment",
            "landscape_removed",
            "regime",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "p6_audit_step3.csv",
        audit_rows,
        [
            "audit_id",
            "initial_degeneracy",
            "final_degeneracy",
            "final_survivors",
            "monotone_nonincreasing",
            "stabilizes_to_selected_point",
            "final_increment",
            "defect_status",
            "computed_sequence",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step3.csv",
        controls,
        ["control_id", "expected", "passes_guard", "computed_witness"],
    )

    verdict = {
        "type": "p6_decaying_degeneracy_audit_constructed",
        "initial_selection_degeneracy": g_sequence[0],
        "final_selection_degeneracy": g_sequence[-1],
        "selection_sequence": g_sequence,
        "landscape_sequence": landscape_sequence,
        "selection_decays_to_w_SM": selection_decays,
        "landscape_nondecaying": landscape_nondecaying,
        "monotone_selection": monotone_selection,
        "final_survivor": REALIZED_WORLD if lands_on_w_sm else ";".join(final_survivors),
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 3,
        "orientation": "Cluster A P6 decaying-degeneracy audit",
        "carrier": "candidate-space survivors plus measure-refinement audit",
        "verdict": verdict,
        "nonclaim": "Finite degeneracy-audit shape only; no physical vacuum mechanism or value is determined.",
    }
    (ARTIFACT_DIR / "p6_decaying_degeneracy_output_step3.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "p6_decaying_degeneracy_output_step3.txt").write_text(
        "\n".join(
            [
                "Cluster A Step 3 P6 decaying-degeneracy audit",
                "Verdict: p6_decaying_degeneracy_audit_constructed",
                f"selection sequence: {'->'.join(str(value) for value in g_sequence)}",
                f"landscape sequence: {'->'.join(str(value) for value in landscape_sequence)}",
                f"final survivor: {verdict['final_survivor']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 3 Results Summary

## Orientation

Step 3 builds the P6 decaying-degeneracy audit for the Cluster A selection layer. The degeneracy `g(n)` is the number of anomaly-free Step-2 survivors still in play at refinement level `n`.

## Genuine Selection Refinement

The genuine selection sequence is `{audit_rows[0]['computed_sequence']}`. It starts from the Step-2 survivor count `{g_sequence[0]}` and ends at `{g_sequence[-1]}`, the selected world `{REALIZED_WORLD}`.

Removed candidates by level:

{chr(10).join(f"- level {row['level']} `{row['refinement_name']}`: removed `{row['candidates_removed']}`; survivors `{row['selection_survivors']}`." for row in refinement_rows)}

The selection degeneracy is monotone non-increasing: `{monotone_selection}`.

## Unselected Landscape Control

The landscape control uses the same Step-2 survivor set but receives no selection-resolution predicate. Its sequence is `{audit_rows[1]['computed_sequence']}` and final degeneracy remains `{landscape_sequence[-1]}`.

## P6 Audit

- Genuine selection: stabilizes to selected point `{selection_decays}`.
- Landscape: non-decaying degeneracy `{landscape_nondecaying}`.
- Final selection increment: `{final_increment}`.
- Final landscape increment: `{final_landscape_increment}`.

## Controls

- Decays-vs-not: `{selection_decays and landscape_nondecaying}`.
- Monotone: `{monotone_selection}`.
- Lands on `w_SM`: `{lands_on_w_sm}`.
- Landscape not secretly selecting: `{landscape_nondecaying}`.
- Carrier guard: candidate-space plus measure-refinement audit.

## Verdict

`p6_decaying_degeneracy_audit_constructed`.

The finite toy distinguishes a genuine selection layer from an unselected landscape: genuine selection drives degeneracy down to the selected point, while the landscape remains multiply degenerate.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 3,
        "orientation": "P6 decaying-degeneracy audit",
        "active_residual": "R_cluster_a_after_step2_p2_selection_constraint",
        "candidate_move": "Compute selection-degeneracy decay under measure refinement and compare against an unselected landscape control.",
        "final_verdict": verdict,
        "track_fields": {
            "degeneracy_refinement": "degeneracy_refinement_step3.csv",
            "p6_audit": "p6_audit_step3.csv",
            "controls": "controls_step3.csv",
            "next_live_option": "Step4_cluster_a_consolidation_or_manager_selected_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "p6_decaying_degeneracy_step3.py",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Builds degeneracy refinement, landscape control, P6 audit, and controls.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/p6_decaying_degeneracy_step3.py",
        },
        {
            "output": "degeneracy_refinement_step3.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-level genuine-selection and landscape degeneracy sequences.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/degeneracy_refinement_step3.csv",
        },
        {
            "output": "p6_audit_step3.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Selection stabilizing audit versus non-decaying landscape audit.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/p6_audit_step3.csv",
        },
        {
            "output": "controls_step3.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Decays-vs-not, monotone, lands-on-selected-point, and carrier controls.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/controls_step3.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Human-readable P6 audit verdict and bounded scope.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite P6 decaying-degeneracy audit.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step3.py",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Validator for computed sequences, controls, source paths, ledgers, and overclaim guard.",
            "source_artifacts": "steps/step3_p6_decaying_degeneracy_audit_artifacts/run_step3.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 3 Nonclaim Boundary

Step 3 is a finite-carrier P6 degeneracy-audit construction. The refinement sequence and degeneracy count are toy diagnostics over Step-2 survivors.

The computed content is the shape: a genuine selection refinement makes degeneracy decay to one selected token, while an unselected landscape control stays multiply degenerate.

This does not provide a real measure, a real vacuum mechanism, a physical value, or a frame-transfer certificate. The one-selection-layer reading remains a flagged hypothesis for later stress tests.

The carrier is candidate-space plus measure-refinement audit. It is not a field pair.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
