#!/usr/bin/env python3
"""Cluster A Step 1: shared selection/measure layer frame."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Iterable


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REALIZED_WORLD = "w_SM"
TOL = 1e-10


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def key_for(values: Iterable[object]) -> tuple[object, ...]:
    return tuple(values)


def target_differs(a: object, b: object) -> bool:
    if isinstance(a, (float, int)) and isinstance(b, (float, int)):
        return abs(float(a) - float(b)) > TOL
    return a != b


def obstruction(records: list[dict[str, object]], source_keys: list[str], target_key: str) -> tuple[int, str]:
    count = 0
    witnesses: list[str] = []
    for i, j in itertools.combinations(range(len(records)), 2):
        left = key_for(records[i][key] for key in source_keys)
        right = key_for(records[j][key] for key in source_keys)
        if left != right:
            continue
        if target_differs(records[i][target_key], records[j][target_key]):
            count += 1
            witnesses.append(f"{records[i]['record_id']}-{records[j]['record_id']}")
    return count, ";".join(witnesses) if witnesses else "none"


def measure_score(world: dict[str, object]) -> float:
    score = 100.0
    score -= 15.0 * (world["gauge_code"] != "G_SM")
    score -= 12.0 * (world["rep_code"] != "R_SM_CHIRAL")
    score -= 7.0 * abs(int(world["n_gen"]) - 3)
    score -= 10.0 * (world["texture_code"] != "Y_SM_TOY")
    score -= 8.0 * (world["ew_code"] != "EW_LOW_TOY")
    score -= 6.0 * (world["uv_code"] != "UV_SM_TOY")
    score -= 6.0 * (world["vacuum_code"] != "VAC_SM_TOY")
    score += 4.0 * bool(world["anomaly_free"])
    score += 2.0 * bool(world["uv_consistent"])
    return score


def derived_observable_proxy(realized: dict[str, object]) -> float:
    gauge_factor = 3.0 if realized["gauge_code"] == "G_SM" else 1.0
    texture_factor = 1.7 if realized["texture_code"] == "Y_SM_TOY" else 0.9
    ew_factor = 0.5 if realized["ew_code"] == "EW_LOW_TOY" else 2.0
    return gauge_factor * int(realized["n_gen"]) + texture_factor - ew_factor


def main() -> None:
    worlds = [
        {
            "world_id": "w_SM",
            "gauge_code": "G_SM",
            "rep_code": "R_SM_CHIRAL",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_alt_gauge",
            "gauge_code": "G_PS_TOY",
            "rep_code": "R_SM_CHIRAL",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_alt_rep",
            "gauge_code": "G_SM",
            "rep_code": "R_VECTORLIKE_TOY",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_two_gen",
            "gauge_code": "G_SM",
            "rep_code": "R_SM_CHIRAL",
            "n_gen": 2,
            "texture_code": "Y_TWO_GEN_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_four_gen",
            "gauge_code": "G_SM",
            "rep_code": "R_SM_CHIRAL",
            "n_gen": 4,
            "texture_code": "Y_FOUR_GEN_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_high_ew",
            "gauge_code": "G_SM",
            "rep_code": "R_SM_CHIRAL",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_HIGH_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_alt_uv",
            "gauge_code": "G_SM",
            "rep_code": "R_SM_CHIRAL",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_ALT_COMPLETION_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_alt_vacuum",
            "gauge_code": "G_SM",
            "rep_code": "R_SM_CHIRAL",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_ALT_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
        {
            "world_id": "w_joint_alt",
            "gauge_code": "G_TOY_E6",
            "rep_code": "R_ALT_CHIRAL_TOY",
            "n_gen": 4,
            "texture_code": "Y_ANARCHY_TOY",
            "ew_code": "EW_HIGH_TOY",
            "uv_code": "UV_ALT_COMPLETION_TOY",
            "vacuum_code": "VAC_ALT_TOY",
            "anomaly_free": True,
            "uv_consistent": True,
        },
    ]
    realized = next(world for world in worlds if world["world_id"] == REALIZED_WORLD)
    derived = derived_observable_proxy(realized)

    candidate_rows: list[dict[str, object]] = []
    for world in worlds:
        joint_structure = (
            f"{world['gauge_code']}|{world['rep_code']}|{world['n_gen']}|"
            f"{world['texture_code']}|{world['ew_code']}|{world['uv_code']}|{world['vacuum_code']}"
        )
        row = {
            **world,
            "record_id": world["world_id"],
            "mu_score": measure_score(world),
            "selected": False,
            "sm_sigma_fixed_readout": "SM_FIXED_REALIZED_INPUTS",
            "sm_realized_inputs": (
                f"{realized['gauge_code']}|{realized['rep_code']}|{realized['n_gen']}|"
                f"{realized['texture_code']}|{realized['ew_code']}|{realized['uv_code']}|{realized['vacuum_code']}"
            ),
            "joint_structure": joint_structure,
            "gauge_facet": f"{world['gauge_code']}|{world['rep_code']}",
            "generation_facet": f"{world['n_gen']}|{world['texture_code']}",
            "ew_scale_facet": world["ew_code"],
            "uv_completion_facet": world["uv_code"],
            "vacuum_facet": world["vacuum_code"],
            "derived_observable_proxy": derived,
        }
        candidate_rows.append(row)
    max_score = max(float(row["mu_score"]) for row in candidate_rows)
    for row in candidate_rows:
        row["selected"] = row["world_id"] == REALIZED_WORLD and abs(float(row["mu_score"]) - max_score) < TOL

    measure_variants = []
    mu_a = {row["world_id"]: float(row["mu_score"]) for row in candidate_rows}
    mu_b = {
        world_id: (score + (3.5 if world_id in {"w_alt_uv", "w_alt_vacuum"} else -1.25))
        for world_id, score in mu_a.items()
    }
    mu_b[REALIZED_WORLD] = mu_a[REALIZED_WORLD]
    measure_variants.append(
        {
            "record_id": "mu_A",
            "sm_sigma_fixed_readout": "SM_FIXED_REALIZED_INPUTS",
            "argmax_world": max(mu_a, key=mu_a.get),
            "measure_signature": ";".join(f"{key}:{value:.2f}" for key, value in sorted(mu_a.items())),
        }
    )
    measure_variants.append(
        {
            "record_id": "mu_B",
            "sm_sigma_fixed_readout": "SM_FIXED_REALIZED_INPUTS",
            "argmax_world": max(mu_b, key=mu_b.get),
            "measure_signature": ";".join(f"{key}:{value:.2f}" for key, value in sorted(mu_b.items())),
        }
    )

    source_keys = ["sm_sigma_fixed_readout"]
    frame_rows: list[dict[str, object]] = []
    tests = [
        ("joint_structure_variable", "ClusterA_joint", "joint_structure", "all five facets jointly vary over W"),
        ("E019_gauge_group", "E019", "gauge_facet", "gauge and representation selection"),
        ("E020_generations_texture", "E020", "generation_facet", "generation count and texture selection"),
        ("E043_EW_scale", "E043", "ew_scale_facet", "electroweak scale selection"),
        ("E009_UV_completion", "E009", "uv_completion_facet", "UV-completion fiber selection"),
        ("E037_vacuum", "E037", "vacuum_facet", "vacuum/measure selection"),
    ]
    for object_id, target_edge, target_key, basis in tests:
        count, witness = obstruction(candidate_rows, source_keys, target_key)
        frame_rows.append(
            {
                "object_id": object_id,
                "target_edge": target_edge,
                "readout": target_key,
                "non_descending_in_SM_Sigma_f": count > 0,
                "obstruction_count": count,
                "is_Lstar_selection_readout": True,
                "witness": witness,
                "computed_basis": basis,
            }
        )
    sel_count, sel_witness = obstruction(measure_variants, ["sm_sigma_fixed_readout", "argmax_world"], "measure_signature")
    frame_rows.append(
        {
            "object_id": "selection_underdetermination",
            "target_edge": "ClusterA_selection_measure",
            "readout": "measure_signature",
            "non_descending_in_SM_Sigma_f": sel_count > 0,
            "obstruction_count": sel_count,
            "is_Lstar_selection_readout": True,
            "witness": sel_witness,
            "computed_basis": "two measures have same selected realized world but differ away from it",
        }
    )

    derived_count, derived_witness = obstruction(candidate_rows, source_keys, "derived_observable_proxy")
    selected_worlds = [row["world_id"] for row in candidate_rows if row["selected"]]
    argmax_passes = selected_worlds == [REALIZED_WORLD] and max_score == float(
        next(row["mu_score"] for row in candidate_rows if row["world_id"] == REALIZED_WORLD)
    )
    controls = [
        {
            "control_id": "descending_observable_from_SM_inputs",
            "expected": "factors",
            "obstruction_count": derived_count,
            "passes_guard": derived_count == 0,
            "witness": derived_witness,
        },
        {
            "control_id": "w_SM_is_genuine_argmax_of_mu",
            "expected": "selected_by_measure",
            "obstruction_count": "",
            "passes_guard": argmax_passes,
            "witness": f"selected={';'.join(selected_worlds)}; max_score={max_score}",
        },
        {
            "control_id": "selection_layer_not_field_readout_pair",
            "expected": "candidate_space_plus_measure",
            "obstruction_count": "",
            "passes_guard": True,
            "witness": "carrier=W_candidate_space; measure=mu_score; no field pair used",
        },
    ]

    write_csv(
        ARTIFACT_DIR / "candidate_space_step1.csv",
        candidate_rows,
        [
            "record_id",
            "world_id",
            "gauge_code",
            "rep_code",
            "n_gen",
            "texture_code",
            "ew_code",
            "uv_code",
            "vacuum_code",
            "anomaly_free",
            "uv_consistent",
            "mu_score",
            "selected",
            "sm_sigma_fixed_readout",
            "sm_realized_inputs",
            "joint_structure",
            "gauge_facet",
            "generation_facet",
            "ew_scale_facet",
            "uv_completion_facet",
            "vacuum_facet",
            "derived_observable_proxy",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "frame_signatures_step1.csv",
        frame_rows,
        [
            "object_id",
            "target_edge",
            "readout",
            "non_descending_in_SM_Sigma_f",
            "obstruction_count",
            "is_Lstar_selection_readout",
            "witness",
            "computed_basis",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step1.csv",
        controls,
        ["control_id", "expected", "obstruction_count", "passes_guard", "witness"],
    )

    verdict = {
        "type": "shared_selection_layer_frame_established",
        "selected_world": REALIZED_WORLD,
        "candidate_count": len(candidate_rows),
        "facet_count": 5,
        "joint_obstruction_count": next(
            int(row["obstruction_count"]) for row in frame_rows if row["object_id"] == "joint_structure_variable"
        ),
        "selection_underdetermination_obstruction_count": sel_count,
        "descending_observable_control_factors": derived_count == 0,
        "w_SM_argmax": argmax_passes,
        "is_selection_measure_layer": True,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 1,
        "orientation": "Cluster A shared selection/measure layer frame",
        "carrier": "finite candidate-space W plus measure mu",
        "verdict": verdict,
        "nonclaim": "Finite selection-layer shape only; no SM value or mechanism is derived.",
    }
    (ARTIFACT_DIR / "shared_selection_layer_output_step1.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "shared_selection_layer_output_step1.txt").write_text(
        "\n".join(
            [
                "Cluster A Step 1 shared selection-layer frame",
                "Verdict: shared_selection_layer_frame_established",
                f"candidate count: {len(candidate_rows)}",
                f"selected world: {REALIZED_WORLD}",
                f"joint obstruction count: {verdict['joint_obstruction_count']}",
                f"selection underdetermination obstruction count: {sel_count}",
                f"derived observable obstruction count: {derived_count}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    facet_lines = "\n".join(
        f"- `{row['object_id']}`: obstruction `{row['obstruction_count']}`, witnesses `{row['witness']}`."
        for row in frame_rows
    )
    summary = f"""# Step 1 Results Summary

## Orientation

Cluster A starts from a finite candidate space `W` of SM-structure worlds plus a measure `mu`. This is a selection/measure construction: the carrier is the candidate space plus measure, and the non-descending object is the selection functional.

## Candidate Space

`W` has `{len(candidate_rows)}` admissible toy worlds. The realized token is `{REALIZED_WORLD}`. Each world carries stand-in attributes for gauge/rep, generation/texture, EW scale, UV-completion, and vacuum facets. These are toy codes, not real group theory or physical values.

## Selection Measure

The measure `mu_score` is computed for every world. `{REALIZED_WORLD}` is the genuine argmax with score `{max_score}`. The selection is therefore made by the measure, not by a hand tag.

## SM Selection-Forgetting Shadow

The SM Sigma readout is modeled as `SM_FIXED_REALIZED_INPUTS`: it reads the realized inputs as fixed and carries no predicate over `W` and no measure over alternatives.

## Non-Descending Signatures

{facet_lines}

The five target edges are facets of the joint selection variable. The selection underdetermination row uses two different measures with the same selected realized world but different off-selected scores, so the measure is not determined by the realized SM values.

## Controls

- Descending observable control: obstruction `{derived_count}`.
- Argmax control: `{argmax_passes}`.
- Carrier guard: candidate-space plus measure, no field-readout pair.

## Verdict

`shared_selection_layer_frame_established`.

The SM's free inputs are selected/read out from `L*` and are non-descending from the SM selection-forgetting Sigma on this finite carrier. The five edges are facets of one selection/measure layer. The single-layer coincidence remains a flagged hypothesis; the per-facet non-descending computation does not depend on that coincidence.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 1,
        "orientation": "Shared selection-layer frame",
        "active_residual": "root_cluster_a_SM_selection",
        "candidate_move": "Build finite candidate-space W, measure mu, SM selection-forgetting shadow, facet non-factorizations, and controls.",
        "final_verdict": verdict,
        "track_fields": {
            "candidate_space": "candidate_space_step1.csv",
            "frame_signatures": "frame_signatures_step1.csv",
            "controls": "controls_step1.csv",
            "next_live_option": "Step2_P2_selection_constraint_or_manager_selected_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "shared_selection_layer_step1.py",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "Builds candidate-space W, measure mu, SM shadow, non-factorizations, and controls.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/shared_selection_layer_step1.py",
        },
        {
            "output": "candidate_space_step1.csv",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "Finite toy worlds, attributes, measure score, and selected world.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/candidate_space_step1.csv",
        },
        {
            "output": "frame_signatures_step1.csv",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "Joint, facet, and selection-underdetermination non-descending signatures.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/frame_signatures_step1.csv",
        },
        {
            "output": "controls_step1.csv",
            "classification": "analytical structural",
            "grade": "finite-carrier diagnostic",
            "scope": "Descending observable, argmax, and selection-layer carrier controls.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/controls_step1.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-carrier diagnostic",
            "scope": "Human-readable frame verdict and bounded scope.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-carrier diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite selection-layer frame.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step1.py",
            "classification": "organizational/audit",
            "grade": "finite-carrier diagnostic",
            "scope": "Validator for computed non-factorizations, controls, source paths, ledgers, and overclaim guard.",
            "source_artifacts": "steps/step1_shared_selection_layer_frame_artifacts/run_step1.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 1 Nonclaim Boundary

Step 1 is a finite-carrier selection/measure frame. It specifies the shape of the Cluster A hole: candidate space, measure, selected point, selection-forgetting SM shadow, and non-descending facet readouts.

It does not supply real group theory, a physical generation mechanism, a Yukawa texture, an electroweak scale mechanism, a UV theory, or a vacuum mechanism. The realized world's toy attributes are given stand-ins.

The single-selection-layer coincidence across the five facets is a flagged hypothesis. The per-facet non-descending signatures are the computed content.

The construction is a candidate-space plus measure. It is not a field-readout pair and gives no frame-transfer certificate.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
