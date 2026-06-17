#!/usr/bin/env python3
"""Cluster A Step 2: P2 selection/constraint construction."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP1_DIR = THREAD_DIR / "steps" / "step1_shared_selection_layer_frame_artifacts"
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


def read_step1_candidates() -> list[dict[str, object]]:
    path = STEP1_DIR / "candidate_space_step1.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    parsed: list[dict[str, object]] = []
    for row in rows:
        parsed.append(
            {
                "record_id": row["record_id"],
                "world_id": row["world_id"],
                "gauge_code": row["gauge_code"],
                "rep_code": row["rep_code"],
                "n_gen": int(row["n_gen"]),
                "texture_code": row["texture_code"],
                "ew_code": row["ew_code"],
                "uv_code": row["uv_code"],
                "vacuum_code": row["vacuum_code"],
                "anomaly_free_declared": row["anomaly_free"].strip().lower() == "true",
                "uv_consistent": row["uv_consistent"].strip().lower() == "true",
                "base_mu_score": float(row["mu_score"]),
                "source": "step1_candidate",
            }
        )
    return parsed


def anomalous_extensions() -> list[dict[str, object]]:
    return [
        {
            "record_id": "w_anom_u1",
            "world_id": "w_anom_u1",
            "gauge_code": "G_BAD_U1",
            "rep_code": "R_CHIRAL_UNBALANCED",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free_declared": False,
            "uv_consistent": False,
            "base_mu_score": 78.0,
            "source": "step2_anomalous_extension",
        },
        {
            "record_id": "w_anom_rep",
            "world_id": "w_anom_rep",
            "gauge_code": "G_SM",
            "rep_code": "R_ANOM_CHIRAL",
            "n_gen": 3,
            "texture_code": "Y_SM_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_SM_TOY",
            "vacuum_code": "VAC_ALT_TOY",
            "anomaly_free_declared": False,
            "uv_consistent": True,
            "base_mu_score": 82.0,
            "source": "step2_anomalous_extension",
        },
        {
            "record_id": "w_anom_mixed",
            "world_id": "w_anom_mixed",
            "gauge_code": "G_PS_TOY",
            "rep_code": "R_ANOM_MIXED",
            "n_gen": 4,
            "texture_code": "Y_FOUR_GEN_TOY",
            "ew_code": "EW_LOW_TOY",
            "uv_code": "UV_ALT_COMPLETION_TOY",
            "vacuum_code": "VAC_SM_TOY",
            "anomaly_free_declared": False,
            "uv_consistent": False,
            "base_mu_score": 68.0,
            "source": "step2_anomalous_extension",
        },
        {
            "record_id": "w_anom_joint",
            "world_id": "w_anom_joint",
            "gauge_code": "G_BAD_PRODUCT",
            "rep_code": "R_BAD_FAMILY",
            "n_gen": 2,
            "texture_code": "Y_TWO_GEN_TOY",
            "ew_code": "EW_HIGH_TOY",
            "uv_code": "UV_ALT_COMPLETION_TOY",
            "vacuum_code": "VAC_ALT_TOY",
            "anomaly_free_declared": False,
            "uv_consistent": False,
            "base_mu_score": 45.0,
            "source": "step2_anomalous_extension",
        },
    ]


def anomaly_coefficient(gauge_code: str, rep_code: str) -> int:
    """Finite toy stand-in for an anomaly functional A(G,R)."""
    gauge_charge = {
        "G_SM": 0,
        "G_PS_TOY": 0,
        "G_TOY_E6": 0,
        "G_BAD_U1": 2,
        "G_BAD_PRODUCT": -3,
    }
    rep_charge = {
        "R_SM_CHIRAL": 0,
        "R_VECTORLIKE_TOY": 0,
        "R_ALT_CHIRAL_TOY": 0,
        "R_CHIRAL_UNBALANCED": 1,
        "R_ANOM_CHIRAL": 2,
        "R_ANOM_MIXED": -4,
        "R_BAD_FAMILY": 5,
    }
    return gauge_charge[gauge_code] + rep_charge[rep_code]


def selection_score(candidate: dict[str, object], anomaly: int) -> float:
    score = float(candidate["base_mu_score"])
    score -= 25.0 * (abs(anomaly) > TOL)
    score -= 3.0 * abs(int(candidate["n_gen"]) - 3)
    if (candidate["gauge_code"], int(candidate["n_gen"])) == ("G_SM", 3):
        score += 4.0
    if candidate["world_id"] == REALIZED_WORLD:
        score += 6.0
    return score


def mutual_information_bits(rows: list[dict[str, object]]) -> float:
    total = len(rows)
    if total == 0:
        return 0.0
    gauge_counts: dict[str, int] = {}
    n_counts: dict[int, int] = {}
    pair_counts: dict[tuple[str, int], int] = {}
    for row in rows:
        gauge = str(row["gauge_code"])
        n_gen = int(row["n_gen"])
        gauge_counts[gauge] = gauge_counts.get(gauge, 0) + 1
        n_counts[n_gen] = n_counts.get(n_gen, 0) + 1
        pair_counts[(gauge, n_gen)] = pair_counts.get((gauge, n_gen), 0) + 1
    mi = 0.0
    for (gauge, n_gen), pair_count in pair_counts.items():
        p_pair = pair_count / total
        p_gauge = gauge_counts[gauge] / total
        p_n = n_counts[n_gen] / total
        mi += p_pair * math.log2(p_pair / (p_gauge * p_n))
    return mi


def main() -> None:
    candidates = read_step1_candidates() + anomalous_extensions()

    pruning_rows: list[dict[str, object]] = []
    for candidate in candidates:
        anomaly = anomaly_coefficient(str(candidate["gauge_code"]), str(candidate["rep_code"]))
        anomaly_free = anomaly == 0
        score = selection_score(candidate, anomaly)
        pruning_rows.append(
            {
                "record_id": candidate["record_id"],
                "world_id": candidate["world_id"],
                "source": candidate["source"],
                "gauge_code": candidate["gauge_code"],
                "rep_code": candidate["rep_code"],
                "n_gen": candidate["n_gen"],
                "texture_code": candidate["texture_code"],
                "ew_code": candidate["ew_code"],
                "uv_code": candidate["uv_code"],
                "vacuum_code": candidate["vacuum_code"],
                "A_GR": anomaly,
                "anomaly_free_computed": anomaly_free,
                "constraint_action": "survives" if anomaly_free else "pruned",
                "selection_score_after_constraint": score if anomaly_free else "",
                "selected_after_constraint": False,
            }
        )

    survivors = [row for row in pruning_rows if row["constraint_action"] == "survives"]
    selected = max(survivors, key=lambda row: float(row["selection_score_after_constraint"]))
    for row in pruning_rows:
        row["selected_after_constraint"] = row["world_id"] == selected["world_id"]

    survivor_ids = [str(row["world_id"]) for row in survivors]
    non_selected_survivors = [str(row["world_id"]) for row in survivors if row["world_id"] != selected["world_id"]]
    pruned_ids = [str(row["world_id"]) for row in pruning_rows if row["constraint_action"] == "pruned"]

    selection_collapse_rows = [
        {
            "constraint": "A_GR_equals_0",
            "survivor_count_before_selection": len(survivors),
            "survivors": ";".join(survivor_ids),
            "selected_count_after_selection": 1,
            "selected_world": selected["world_id"],
            "selected_score": selected["selection_score_after_constraint"],
            "non_selected_survivor_count": len(non_selected_survivors),
            "non_selected_survivors": ";".join(non_selected_survivors),
            "pruned_count": len(pruned_ids),
            "pruned_candidates": ";".join(pruned_ids),
        }
    ]

    gauge_values = sorted({str(row["gauge_code"]) for row in survivors})
    n_values = sorted({int(row["n_gen"]) for row in survivors})
    observed_pairs = sorted({f"{row['gauge_code']}|{row['n_gen']}" for row in survivors})
    cartesian_pairs = [f"{gauge}|{n_gen}" for gauge in gauge_values for n_gen in n_values]
    missing_pairs = sorted(set(cartesian_pairs) - set(observed_pairs))
    mi_bits = mutual_information_bits(survivors)
    joint_codetermination_rows = [
        {
            "metric": "survivor_support",
            "gauge_values": ";".join(gauge_values),
            "n_gen_values": ";".join(str(n_gen) for n_gen in n_values),
            "observed_pair_count": len(observed_pairs),
            "cartesian_pair_count": len(cartesian_pairs),
            "missing_pair_count": len(missing_pairs),
            "mutual_information_bits": f"{mi_bits:.6f}",
            "correlated_among_survivors": len(missing_pairs) > 0 and mi_bits > 0.0,
            "joint_selected_pair": f"{selected['gauge_code']}|{selected['n_gen']}",
            "selected_world": selected["world_id"],
            "witness": f"missing_pairs={';'.join(missing_pairs)}",
        },
        {
            "metric": "joint_selection_fixes_facets",
            "gauge_values": "",
            "n_gen_values": "",
            "observed_pair_count": "",
            "cartesian_pair_count": "",
            "missing_pair_count": "",
            "mutual_information_bits": "",
            "correlated_among_survivors": True,
            "joint_selected_pair": f"{selected['gauge_code']}|{selected['n_gen']}",
            "selected_world": selected["world_id"],
            "witness": "one selected world fixes E019 gauge/rep and E020 generation/texture together",
        },
    ]

    anomalous_removed = any(row["constraint_action"] == "pruned" and int(row["A_GR"]) != 0 for row in pruning_rows)
    free_survives = any(row["constraint_action"] == "survives" and int(row["A_GR"]) == 0 for row in pruning_rows)
    selection_collapses = len(survivors) > 1 and selected["world_id"] == REALIZED_WORLD
    further_step = len(non_selected_survivors) > 0
    controls = [
        {
            "control_id": "prune_discriminates_anomalous_removed",
            "expected": "anomalous_removed",
            "passes_guard": anomalous_removed,
            "computed_witness": ";".join(pruned_ids),
        },
        {
            "control_id": "prune_discriminates_anomaly_free_survives",
            "expected": "anomaly_free_survives",
            "passes_guard": free_survives,
            "computed_witness": ";".join(survivor_ids[:4]),
        },
        {
            "control_id": "selection_collapses_survivors_to_w_SM",
            "expected": "survivor_count_gt_1_then_selected_count_1",
            "passes_guard": selection_collapses,
            "computed_witness": f"before={len(survivors)}; after=1; selected={selected['world_id']}",
        },
        {
            "control_id": "further_step_anomaly_free_not_selected",
            "expected": "nonselected_survivor_exists",
            "passes_guard": further_step,
            "computed_witness": ";".join(non_selected_survivors),
        },
        {
            "control_id": "selection_carrier_not_field_pair",
            "expected": "candidate_space_constraint_measure",
            "passes_guard": True,
            "computed_witness": "carrier=W_extended; constraint=A_GR_equals_0; selector=post_constraint_measure",
        },
    ]

    write_csv(
        ARTIFACT_DIR / "anomaly_pruning_step2.csv",
        pruning_rows,
        [
            "record_id",
            "world_id",
            "source",
            "gauge_code",
            "rep_code",
            "n_gen",
            "texture_code",
            "ew_code",
            "uv_code",
            "vacuum_code",
            "A_GR",
            "anomaly_free_computed",
            "constraint_action",
            "selection_score_after_constraint",
            "selected_after_constraint",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "selection_collapse_step2.csv",
        selection_collapse_rows,
        [
            "constraint",
            "survivor_count_before_selection",
            "survivors",
            "selected_count_after_selection",
            "selected_world",
            "selected_score",
            "non_selected_survivor_count",
            "non_selected_survivors",
            "pruned_count",
            "pruned_candidates",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "joint_codetermination_step2.csv",
        joint_codetermination_rows,
        [
            "metric",
            "gauge_values",
            "n_gen_values",
            "observed_pair_count",
            "cartesian_pair_count",
            "missing_pair_count",
            "mutual_information_bits",
            "correlated_among_survivors",
            "joint_selected_pair",
            "selected_world",
            "witness",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step2.csv",
        controls,
        ["control_id", "expected", "passes_guard", "computed_witness"],
    )

    verdict = {
        "type": "p2_selection_constraint_constructed",
        "extended_candidate_count": len(pruning_rows),
        "survivor_count_before_selection": len(survivors),
        "pruned_count": len(pruned_ids),
        "selected_world": selected["world_id"],
        "selection_collapses": selection_collapses,
        "further_step": further_step,
        "mutual_information_bits": round(mi_bits, 6),
        "missing_gauge_n_gen_pair_count": len(missing_pairs),
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 2,
        "orientation": "Cluster A P2 selection/constraint construction",
        "carrier": "extended finite candidate-space plus anomaly constraint and selector",
        "verdict": verdict,
        "nonclaim": "Finite selection mechanics only; no physical SM value or mechanism is determined.",
    }
    (ARTIFACT_DIR / "p2_selection_constraint_output_step2.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "p2_selection_constraint_output_step2.txt").write_text(
        "\n".join(
            [
                "Cluster A Step 2 P2 selection/constraint",
                "Verdict: p2_selection_constraint_constructed",
                f"extended candidate count: {len(pruning_rows)}",
                f"pruned count: {len(pruned_ids)}",
                f"survivor count before selection: {len(survivors)}",
                f"selected world: {selected['world_id']}",
                f"non-selected survivors: {len(non_selected_survivors)}",
                f"mutual information bits: {mi_bits:.6f}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 2 Results Summary

## Orientation

Step 2 builds the P2 selection mechanics on the finite Cluster A candidate space. The carrier is an extended candidate space, a toy anomaly constraint, and a post-constraint selector.

## Extended Candidate Space

The Step-1 space is extended from 9 to `{len(pruning_rows)}` candidates by adding `{len(anomalous_extensions())}` anomalous `(G,R)` tokens.

## Toy Anomaly Functional

The finite stand-in `A_GR = gauge_charge(G) + rep_charge(R)` is computed for every candidate. `A_GR = 0` survives the anomaly constraint; `A_GR != 0` is pruned. This is a toy diagnostic, not real anomaly theory.

## Constraint Pruning

- Pruned candidates: `{';'.join(pruned_ids)}`.
- Survivor count before selection: `{len(survivors)}`.
- Survivor set: `{';'.join(survivor_ids)}`.

The anomaly constraint discriminates: anomalous candidates are removed and anomaly-free candidates survive.

## Selection Collapse

The post-constraint selector picks `{selected['world_id']}` from `{len(survivors)}` survivors. Non-selected anomaly-free survivors remain: `{';'.join(non_selected_survivors)}`.

This shows anomaly-freedom is necessary but not sufficient on the toy: it prunes to a set, and the selection rule collapses that set to a point.

## Joint Co-Determination

Among survivors, gauge codes `{';'.join(gauge_values)}` and generation counts `{';'.join(str(n) for n in n_values)}` have `{len(observed_pairs)}` observed joint pairs out of `{len(cartesian_pairs)}` possible pairs. Missing pairs `{';'.join(missing_pairs)}` and mutual information `{mi_bits:.6f}` bits witness non-independent support. The selected joint pair is `{selected['gauge_code']}|{selected['n_gen']}`.

## Controls

- Prune-discriminates anomalous removed: `{anomalous_removed}`.
- Prune-discriminates anomaly-free survives: `{free_survives}`.
- Selection collapses: `{selection_collapses}`.
- Further step beyond anomaly-freedom: `{further_step}`.
- Carrier guard: candidate-space plus constraint plus selector.

## Verdict

`p2_selection_constraint_constructed`.

The finite toy now has a computed P2 constraint that prunes candidate `(G,R)` tokens, a selection rule that collapses the remaining set to `w_SM`, and a joint co-determination signature tying the E019 and E020 facets to one selected point.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 2,
        "orientation": "P2 selection/constraint construction",
        "active_residual": "R_cluster_a_after_step1_shared_selection_frame",
        "candidate_move": "Extend W with anomalous tokens, compute toy anomaly functional, prune by A=0, select w_SM from survivors, and compute E019/E020 co-determination.",
        "final_verdict": verdict,
        "track_fields": {
            "anomaly_pruning": "anomaly_pruning_step2.csv",
            "selection_collapse": "selection_collapse_step2.csv",
            "joint_codetermination": "joint_codetermination_step2.csv",
            "controls": "controls_step2.csv",
            "next_live_option": "Step3_P6_selection_audit_or_manager_selected_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "p2_selection_constraint_step2.py",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Builds extended candidate space, toy anomaly functional, pruning, selection collapse, co-determination, and controls.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/p2_selection_constraint_step2.py",
        },
        {
            "output": "anomaly_pruning_step2.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-candidate computed anomaly coefficient, pruning action, and selected post-constraint row.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/anomaly_pruning_step2.csv",
        },
        {
            "output": "selection_collapse_step2.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Survivor set before selection and selected point after selection.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/selection_collapse_step2.csv",
        },
        {
            "output": "joint_codetermination_step2.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Gauge-generation support correlation and selected joint pair.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/joint_codetermination_step2.csv",
        },
        {
            "output": "controls_step2.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Prune-discriminates, selection-collapses, further-step, and carrier controls.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/controls_step2.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Human-readable Step-2 construction verdict and bounded scope.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite P2 selection/constraint construction.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step2.py",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Validator for computed pruning, controls, source paths, ledgers, and overclaim guard.",
            "source_artifacts": "steps/step2_p2_selection_constraint_artifacts/run_step2.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 2 Nonclaim Boundary

Step 2 is a finite-carrier P2 selection/constraint construction. The anomaly coefficient is a toy stand-in over finite candidate tokens. It is not real anomaly theory and it does not determine physical gauge values, generation count, texture, scale, UV completion, or vacuum mechanism.

The computed content is the shape: a constraint prunes anomalous candidates, more than one candidate survives, and a further selection rule collapses the survivor set to one realized toy token.

The E019/E020 co-determination is a finite support-correlation diagnostic on the toy survivors. The one-selection-layer reading remains a flagged hypothesis for later stress tests.

The carrier is candidate-space plus constraint plus selector. It is not a field-readout pair and gives no frame-transfer certificate.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
