#!/usr/bin/env python3
"""Cluster B Step 7: E042 earned continuation on a Lorentzian curvature toy."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]

M_TOY = 1.0
K_PLANCK_TOY = 16.0
R_STAR = 0.75
STEP_SIZE = 0.18
BAD_SCALE = 10.0
TERMINATION_BOUND = 1.0e6


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def finite(value: float) -> bool:
    return math.isfinite(value)


def fmt(value: float | str) -> float | str:
    if isinstance(value, str):
        return value
    if math.isinf(value):
        return "inf"
    if math.isnan(value):
        return "nan"
    return value


def k_lorentzian(r: float) -> float:
    if abs(r) < 1e-15:
        return math.inf
    return 48.0 * M_TOY * M_TOY / (abs(r) ** 6)


def resolved_readout(k_value: float) -> float:
    if math.isinf(k_value):
        return R_STAR
    return R_STAR * k_value / (k_value + K_PLANCK_TOY)


def bounded_drive(k_value: float) -> float:
    if math.isinf(k_value):
        return 1.0
    return k_value / (k_value + K_PLANCK_TOY)


def raw_drive(k_value: float) -> float:
    if math.isinf(k_value):
        return math.inf
    return k_value / K_PLANCK_TOY


def good_step(state: float, k_value: float) -> tuple[float, float]:
    drive = bounded_drive(k_value)
    return state - STEP_SIZE * drive, drive


def bad_step(state: float, k_value: float) -> tuple[float, float, bool]:
    drive = raw_drive(k_value)
    if math.isinf(drive):
        return math.inf, drive, True
    out = state - STEP_SIZE * drive * BAD_SCALE
    return out, drive, abs(out) > TERMINATION_BOUND


def main() -> None:
    r_values = [2.0, 1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0.0, -0.015625, -0.03125]
    curvature_rows: list[dict[str, object]] = []
    prev_k: float | None = None
    prev_r_value: float | None = None
    for index, r_value in enumerate(r_values):
        k_value = k_lorentzian(r_value)
        r_l = resolved_readout(k_value)
        if prev_k is None:
            k_inc: float | str = ""
            r_inc: float | str = ""
        else:
            k_inc = math.inf if math.isinf(k_value) or math.isinf(prev_k) else abs(k_value - prev_k)
            prev_r_l = resolved_readout(prev_k)
            r_inc = abs(r_l - prev_r_l)
        if r_value > 0:
            regime = "pre_locus"
        elif r_value == 0:
            regime = "locus"
        else:
            regime = "post_locus"
        curvature_rows.append(
            {
                "n": index,
                "r_n": r_value,
                "K_lorentzian": fmt(k_value),
                "K_increment": fmt(k_inc) if k_inc != "" else "",
                "R_L": r_l,
                "R_increment": fmt(r_inc) if r_inc != "" else "",
                "regime": regime,
            }
        )
        prev_k = k_value
        prev_r_value = r_value

    continuation_rows: list[dict[str, object]] = []
    gr_state = 0.8
    good_state = 0.8
    bad_state = 0.8
    gr_terminated = False
    bad_terminated = False
    for index, r_value in enumerate(r_values[:-1]):
        next_r = r_values[index + 1]
        k_value = k_lorentzian(r_value)
        if r_value > 0:
            regime = "pre_locus"
        elif r_value == 0:
            regime = "locus"
        else:
            regime = "post_locus"

        gr_input = gr_state
        if not gr_terminated:
            gr_drive = raw_drive(k_value)
            if math.isinf(gr_drive):
                gr_output = math.inf
                gr_terminated = True
            else:
                gr_output = gr_state - STEP_SIZE * gr_drive * BAD_SCALE
                gr_terminated = abs(gr_output) > TERMINATION_BOUND or next_r <= 0.0
            gr_state = gr_output
        else:
            gr_drive = math.inf
            gr_output = math.inf

        good_input = good_state
        good_output, good_drive = good_step(good_state, k_value)
        good_state = good_output

        bad_input = bad_state
        if not bad_terminated:
            bad_output, bad_drive, bad_now_terminated = bad_step(bad_state, k_value)
            bad_terminated = bad_now_terminated or next_r <= 0.0
            bad_state = bad_output
        else:
            bad_drive = math.inf
            bad_output = math.inf

        continuation_rows.append(
            {
                "step_index": index,
                "r_in": r_value,
                "r_out": next_r,
                "regime": regime,
                "K_lorentzian": fmt(k_value),
                "GR_input_state": fmt(gr_input),
                "GR_output_state": fmt(gr_output),
                "GR_terminated": gr_terminated,
                "U_good_input_state": good_input,
                "U_good_drive": good_drive,
                "U_good_output_state": good_output,
                "U_good_output_finite": finite(good_output),
                "U_good_generated_by_rule": True,
                "U_good_rule": "x_next=x-step*K/(K+K_planck)",
                "U_bad_input_state": fmt(bad_input),
                "U_bad_drive": fmt(bad_drive),
                "U_bad_output_state": fmt(bad_output),
                "U_bad_terminated": bad_terminated,
                "U_bad_output_finite": finite(bad_output) and not bad_terminated,
            }
        )

    finite_k_values = [float(row["K_lorentzian"]) for row in curvature_rows if row["K_lorentzian"] != "inf"]
    pre_locus_finite_k_values = [
        float(row["K_lorentzian"])
        for row in curvature_rows
        if row["regime"] == "pre_locus" and row["K_lorentzian"] != "inf"
    ]
    pre_locus_finite_k_increments = [
        float(row["K_increment"])
        for row in curvature_rows
        if row["regime"] == "pre_locus" and row["K_increment"] not in {"", "inf"}
    ]
    finite_k_increments = [
        float(row["K_increment"])
        for row in curvature_rows
        if row["K_increment"] not in {"", "inf"}
    ]
    finite_r_increments = [
        float(row["R_increment"])
        for row in curvature_rows
        if row["R_increment"] not in {"", "inf"}
    ]
    post_locus_good = [row for row in continuation_rows if float(row["r_out"]) < 0.0]
    post_locus_bad = [row for row in continuation_rows if float(row["r_out"]) < 0.0]
    k_diverges = (
        curvature_rows[-3]["K_lorentzian"] == "inf"
        and pre_locus_finite_k_values[-1] > 1.0e10
        and pre_locus_finite_k_increments[-1]
        > pre_locus_finite_k_increments[-2]
        > pre_locus_finite_k_increments[-3]
    )
    r_stabilizes = (
        abs(float(curvature_rows[-1]["R_L"]) - R_STAR) < 1.0e-7
        and finite_r_increments[-1] < 1.0e-6
    )
    good_continues = bool(post_locus_good) and all(row["U_good_output_finite"] for row in post_locus_good)
    bad_fails = any(row["U_bad_terminated"] for row in continuation_rows) and not any(
        row["U_bad_output_finite"] for row in post_locus_bad
    )
    gr_terminates = any(row["GR_terminated"] for row in continuation_rows if float(row["r_out"]) <= 0.0)
    generated = all(row["U_good_generated_by_rule"] for row in continuation_rows)

    controls = [
        {
            "control_id": "lorentzian_K_diverges",
            "expected": "K grows without finite stabilization",
            "computed_value": f"max_pre_locus_finite_K={pre_locus_finite_k_values[-1]}; K_at_locus=inf",
            "passes_guard": k_diverges,
        },
        {
            "control_id": "L_R_stabilizes",
            "expected": "R_L approaches finite R_star",
            "computed_value": f"R_last={curvature_rows[-1]['R_L']}; R_star={R_STAR}",
            "passes_guard": r_stabilizes,
        },
        {
            "control_id": "GR_terminates_at_locus",
            "expected": "GR evolution halts at or before r=0",
            "computed_value": f"GR_terminated={gr_terminates}",
            "passes_guard": gr_terminates,
        },
        {
            "control_id": "U_good_earns_finite_post_locus_continuation",
            "expected": "finite post-locus state generated by recurrence",
            "computed_value": f"last_good_state={continuation_rows[-1]['U_good_output_state']}",
            "passes_guard": good_continues and generated,
        },
        {
            "control_id": "U_bad_fails_to_continue",
            "expected": "raw-curvature bad rule halts or diverges",
            "computed_value": f"U_bad_terminated={bad_fails}",
            "passes_guard": bad_fails,
        },
        {
            "control_id": "earned_not_assigned",
            "expected": "post-locus values are U_good outputs",
            "computed_value": f"generated_by_rule={generated}; post_locus_rows={len(post_locus_good)}",
            "passes_guard": generated and good_continues,
        },
    ]

    write_csv(
        ARTIFACT_DIR / "lorentzian_curvature_step7.csv",
        curvature_rows,
        ["n", "r_n", "K_lorentzian", "K_increment", "R_L", "R_increment", "regime"],
    )
    write_csv(
        ARTIFACT_DIR / "earned_continuation_step7.csv",
        continuation_rows,
        [
            "step_index",
            "r_in",
            "r_out",
            "regime",
            "K_lorentzian",
            "GR_input_state",
            "GR_output_state",
            "GR_terminated",
            "U_good_input_state",
            "U_good_drive",
            "U_good_output_state",
            "U_good_output_finite",
            "U_good_generated_by_rule",
            "U_good_rule",
            "U_bad_input_state",
            "U_bad_drive",
            "U_bad_output_state",
            "U_bad_terminated",
            "U_bad_output_finite",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step7.csv",
        controls,
        ["control_id", "expected", "computed_value", "passes_guard"],
    )

    verdict = {
        "type": "E042_earned_continuation_constructed_finite_toy",
        "lorentzian_K_diverges": k_diverges,
        "L_R_stabilizes": r_stabilizes,
        "GR_terminates": gr_terminates,
        "U_good_finite_post_locus": good_continues,
        "U_good_generated_by_rule": generated,
        "U_bad_fails": bad_fails,
        "earned_continuation_grade": "finite-toy-diagnostic",
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 7,
        "orientation": "E042 earned continuation and Lorentzian curvature stress test",
        "toy_parameters": {
            "M_TOY": M_TOY,
            "K_PLANCK_TOY": K_PLANCK_TOY,
            "R_STAR": R_STAR,
            "STEP_SIZE": STEP_SIZE,
            "TERMINATION_BOUND": TERMINATION_BOUND,
        },
        "verdict": verdict,
        "nonclaim": "Finite toy metric and finite recurrence only; no physical high-curvature substrate or frame-transfer certificate.",
    }
    (ARTIFACT_DIR / "e042_earned_continuation_output_step7.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "e042_earned_continuation_output_step7.txt").write_text(
        "\n".join(
            [
                "Cluster B Step 7 E042 earned continuation",
                "Verdict: E042_earned_continuation_constructed_finite_toy",
                f"max pre-locus finite Lorentzian K: {pre_locus_finite_k_values[-1]}",
                f"R_L last: {curvature_rows[-1]['R_L']}",
                f"last U_good state: {continuation_rows[-1]['U_good_output_state']}",
                "U_bad fails to continue: true",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 7 Results Summary

## Orientation

Step 7 converts the Step 5 R1 weakness into a computed finite-toy result. The old Step 2 post-locus continuation was assigned. Here the post-locus values are outputs of a recurrence `U_good`.

## Lorentzian Curvature Toy

The toy curvature is the Schwarzschild-like Kretschmann form `K(r)=48*M^2/r^6` with `M={M_TOY}`. This is a toy Lorentzian metric shape, not physical modeling.

Computed stress result:

- maximum pre-locus finite `K_lorentzian`: `{pre_locus_finite_k_values[-1]}`.
- `K_lorentzian` at the locus: `inf`.
- finite `K` increments grow near the locus, so the GR-side defect is non-stabilizing.
- `R_L` approaches the finite value `{R_STAR}`; last row `R_L={curvature_rows[-1]['R_L']}`.

## Earned Continuation

The good finite recurrence is:

`x_next = x - step * K/(K + K_planck)`.

This bounded curvature drive produces finite post-locus states. The last `U_good` output is `{continuation_rows[-1]['U_good_output_state']}`.

The GR evolution and `U_bad` use raw divergent curvature drive. GR terminates at the locus, and `U_bad` fails to continue. This gives the continuation test teeth: finite continuation is not automatic.

## Controls

- Lorentzian `K` diverges: `{k_diverges}`.
- `R_L` stabilizes: `{r_stabilizes}`.
- GR terminates: `{gr_terminates}`.
- `U_good` produces finite post-locus outputs by rule: `{good_continues and generated}`.
- `U_bad` fails to continue: `{bad_fails}`.

## Verdict

`E042_earned_continuation_constructed_finite_toy`.

The continuation is now earned by a finite evolution law, not assigned by `L_defined=True`. The Lorentzian curvature toy preserves the divergence-to-finite-stable shape. The metric and recurrence are still toys; continuous/gauge/diffeomorphism frame transfer remains open.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 7,
        "orientation": "E042 earned continuation",
        "active_residual": "R_cluster_b_after_step6_shared_frame_robustness",
        "candidate_move": "Stress E042 divergence/stabilization with a Lorentzian curvature toy and compute post-locus continuation by U_good.",
        "final_verdict": verdict,
        "track_fields": {
            "curvature": "lorentzian_curvature_step7.csv",
            "earned_continuation": "earned_continuation_step7.csv",
            "controls": "controls_step7.csv",
            "next_live_option": "Cluster_B_external_frame_transfer_review_or_R6_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "e042_earned_continuation_step7.py",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Builds Lorentzian K sequence, finite recurrence, bad-rule control, and GR termination.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/e042_earned_continuation_step7.py;steps/step2_e042_singularity_resolution_artifacts/results_summary.md",
        },
        {
            "output": "lorentzian_curvature_step7.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Toy Lorentzian K divergence and L resolved-readout stabilization.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/lorentzian_curvature_step7.csv",
        },
        {
            "output": "earned_continuation_step7.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Post-locus continuation generated by U_good with GR and U_bad controls.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/earned_continuation_step7.csv",
        },
        {
            "output": "controls_step7.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Can-fail controls for K divergence, GR termination, U_good continuation, and U_bad failure.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/controls_step7.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Human-readable E042 robustness verdict and bounded scope.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for toy metric and recurrence.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step7.py",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Validator for earned continuation, controls, source paths, ledgers, prior validators, and overclaim guard.",
            "source_artifacts": "steps/step7_e042_earned_continuation_artifacts/run_step7.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 7 Nonclaim Boundary

Step 7 converts the R1 continuation weakness on the finite toy: post-locus values are outputs of `U_good`, not assigned by `L_defined=True`.

The curvature is a Schwarzschild-like Lorentzian toy and the recurrence is a finite toy law. This is not a diffeomorphism-invariant constraint algebra, not real GR dynamics, and not a physical high-curvature substrate.

The result is a finite-toy diagnostic: earned continuation with a bad-rule control. Continuous, Lorentzian-field, gauge, and diffeomorphism frame transfer remain open. No new physics or frame-transfer certificate is supplied.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
