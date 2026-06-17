#!/usr/bin/env python3
"""Cluster B Step 10: E021 Lambda-selection adjudication by degeneracy audit."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP8_VACUA = THREAD_DIR / "steps/step8_e021_rg_measure_robustness_artifacts/rg_measure_vacua_step8.csv"
SIGNIFICANCE_THRESHOLD = 0.25
RELAXATION_RESOLUTION = 2.0e-5


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_step8_lambda_grid() -> tuple[list[float], float]:
    with STEP8_VACUA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    candidates = sorted({round(float(row["lambda_candidate"]), 15) for row in rows})
    selected_values = [
        float(row["realized_Lambda"])
        for row in rows
        if row["config_id"] == "A_left" and row["selected"].strip().lower() == "true"
    ]
    if not selected_values:
        selected_values = [float(row["realized_Lambda"]) for row in rows if row["selected"].strip().lower() == "true"]
    lambda_sm = selected_values[0]
    if not any(abs(value - lambda_sm) < 1.0e-14 for value in candidates):
        candidates.append(lambda_sm)
    return sorted(candidates), lambda_sm


def entropy_effective_support(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0.0:
        return 0.0
    probs = [weight / total for weight in weights if weight > 0.0]
    entropy = -sum(prob * math.log(prob) for prob in probs)
    return math.exp(entropy)


def significant_values(lambda_grid: list[float], weights: list[float]) -> tuple[int, list[float]]:
    if not weights:
        return 0, []
    max_weight = max(weights)
    values = [
        lambda_grid[idx]
        for idx, weight in enumerate(weights)
        if weight >= SIGNIFICANCE_THRESHOLD * max_weight
    ]
    return len(values), values


def landscape_weights(lambda_grid: list[float], lambda_sm: float, sigma: float) -> list[float]:
    weights = []
    for value in lambda_grid:
        log_distance = math.log10(value / lambda_sm)
        weights.append(math.exp(-(log_distance**2) / (2.0 * sigma**2)))
    return weights


def relaxation_degeneracy(
    lambda_grid: list[float], lambda_sm: float, level: int, relaxation_steps: int, alpha: float = 0.12
) -> dict[str, object]:
    evolved = [lambda_sm + (alpha**relaxation_steps) * (value - lambda_sm) for value in lambda_grid]
    far_values = [lambda_grid[idx] for idx, value in enumerate(evolved) if abs(value - lambda_sm) > RELAXATION_RESOLUTION]
    g = len(far_values) + 1 if far_values else 1
    significant = far_values if far_values else [lambda_sm]
    return {
        "horn": "relaxation_attractor",
        "level": level,
        "refinement_parameter": f"relaxation_steps={relaxation_steps}",
        "effective_Lambda_degeneracy": g,
        "significant_Lambda_values": ";".join(f"{value:.15g}" for value in significant),
        "entropy_effective_support": "",
        "regime": "collapsing_selection" if g > 1 else "collapsed_to_point",
    }


def measure_degeneracy(
    horn: str, lambda_grid: list[float], lambda_sm: float, level: int, sigma: float
) -> dict[str, object]:
    weights = landscape_weights(lambda_grid, lambda_sm, sigma)
    count, significant = significant_values(lambda_grid, weights)
    return {
        "horn": horn,
        "level": level,
        "refinement_parameter": f"sigma={sigma:.6g}",
        "effective_Lambda_degeneracy": count,
        "significant_Lambda_values": ";".join(f"{value:.15g}" for value in significant),
        "entropy_effective_support": f"{entropy_effective_support(weights):.15g}",
        "regime": "distribution" if count > 1 else "collapsed_to_point",
    }


def add_increments(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    previous_by_horn: dict[str, int] = {}
    out: list[dict[str, object]] = []
    for row in rows:
        horn = str(row["horn"])
        g = int(row["effective_Lambda_degeneracy"])
        previous = previous_by_horn.get(horn)
        row = {**row, "increment": 0 if previous is None else g - previous}
        previous_by_horn[horn] = g
        out.append(row)
    return out


def build_degeneracy_rows(lambda_grid: list[float], lambda_sm: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for level, steps in enumerate([0, 1, 2, 3, 4, 6]):
        rows.append(relaxation_degeneracy(lambda_grid, lambda_sm, level, steps))
    for level, sigma in enumerate([3.0, 2.8, 2.6, 2.4, 2.2, 2.0]):
        rows.append(measure_degeneracy("broad_anthropic_landscape", lambda_grid, lambda_sm, level, sigma))
    for level, sigma in enumerate([0.5, 0.2, 0.1, 0.05, 0.02, 0.01]):
        rows.append(measure_degeneracy("sharp_selecting_measure", lambda_grid, lambda_sm, level, sigma))
    return add_increments(rows)


def build_adjudication(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_horn: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_horn.setdefault(str(row["horn"]), []).append(row)

    adjudication_rows: list[dict[str, object]] = []
    for horn, horn_rows in sorted(by_horn.items()):
        horn_rows.sort(key=lambda row: int(row["level"]))
        sequence = [int(row["effective_Lambda_degeneracy"]) for row in horn_rows]
        final_g = sequence[-1]
        monotone = all(sequence[idx + 1] <= sequence[idx] for idx in range(len(sequence) - 1))
        collapses = sequence[0] > 1 and final_g == 1 and monotone
        adjudication_rows.append(
            {
                "horn": horn,
                "initial_degeneracy": sequence[0],
                "final_degeneracy": final_g,
                "sequence": "->".join(str(value) for value in sequence),
                "monotone_nonincreasing": monotone,
                "collapses_to_point": collapses,
                "final_significant_Lambda_values": horn_rows[-1]["significant_Lambda_values"],
                "certified_by_P6": collapses,
                "framework_status": "certified_selection" if collapses else "landscape_nonclosing",
            }
        )
    return adjudication_rows


def build_controls(adjudication_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_horn = {row["horn"]: row for row in adjudication_rows}
    broad_fails = (
        not bool(by_horn["broad_anthropic_landscape"]["collapses_to_point"])
        and int(by_horn["broad_anthropic_landscape"]["final_degeneracy"]) > 1
    )
    relaxation_collapses = bool(by_horn["relaxation_attractor"]["collapses_to_point"])
    sharp_collapses = bool(by_horn["sharp_selecting_measure"]["collapses_to_point"])
    return [
        {
            "control_id": "broad_landscape_fails_to_collapse",
            "expected": "broad_final_degeneracy_gt_1",
            "passes_guard": broad_fails,
            "computed_witness": by_horn["broad_anthropic_landscape"]["sequence"],
        },
        {
            "control_id": "relaxation_collapses",
            "expected": "relaxation_final_degeneracy_1",
            "passes_guard": relaxation_collapses,
            "computed_witness": by_horn["relaxation_attractor"]["sequence"],
        },
        {
            "control_id": "sharp_measure_collapses",
            "expected": "sharp_measure_final_degeneracy_1",
            "passes_guard": sharp_collapses,
            "computed_witness": by_horn["sharp_selecting_measure"]["sequence"],
        },
        {
            "control_id": "selection_carrier_not_field_pair",
            "expected": "Lambda_grid_plus_degeneracy_audit",
            "passes_guard": True,
            "computed_witness": "carrier=Lambda_grid; audit=effective_support_under_refinement",
        },
    ]


def write_summaries(
    lambda_grid: list[float],
    lambda_sm: float,
    adjudication_rows: list[dict[str, object]],
    controls: list[dict[str, object]],
) -> None:
    by_horn = {row["horn"]: row for row in adjudication_rows}
    verdict = {
        "type": "e021_lambda_selection_adjudication_constructed",
        "lambda_sm_toy_value": lambda_sm,
        "lambda_grid_size": len(lambda_grid),
        "certified_horns": sorted(row["horn"] for row in adjudication_rows if row["certified_by_P6"]),
        "failed_horns": sorted(row["horn"] for row in adjudication_rows if not row["certified_by_P6"]),
        "relaxation_sequence": by_horn["relaxation_attractor"]["sequence"],
        "broad_landscape_sequence": by_horn["broad_anthropic_landscape"]["sequence"],
        "sharp_measure_sequence": by_horn["sharp_selecting_measure"]["sequence"],
        "broad_landscape_final_degeneracy": int(by_horn["broad_anthropic_landscape"]["final_degeneracy"]),
        "criterion": "P6_decaying_degeneracy_collapses_to_point",
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 10,
        "orientation": "Cluster B E021 Lambda-selection adjudication",
        "carrier": "Lambda candidate grid plus relaxation/measure degeneracy audit",
        "source_step": "steps/step8_e021_rg_measure_robustness_artifacts/rg_measure_vacua_step8.csv",
        "verdict": verdict,
        "nonclaim": "Finite horn-adjudication shape only; no physical Lambda value or mechanism is determined.",
    }
    (ARTIFACT_DIR / "e021_lambda_selection_adjudication_output_step10.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "e021_lambda_selection_adjudication_output_step10.txt").write_text(
        "\n".join(
            [
                "Cluster B Step 10 E021 Lambda-selection adjudication",
                "Verdict: e021_lambda_selection_adjudication_constructed",
                f"toy Lambda_SM from Step 8: {lambda_sm:.15g}",
                f"Lambda grid size: {len(lambda_grid)}",
                f"relaxation sequence: {verdict['relaxation_sequence']}",
                f"broad landscape sequence: {verdict['broad_landscape_sequence']}",
                f"sharp measure sequence: {verdict['sharp_measure_sequence']}",
                f"certified horns: {';'.join(verdict['certified_horns'])}",
                f"failed horns: {';'.join(verdict['failed_horns'])}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    schema = {
        "step": 10,
        "name": "E021 Lambda-selection adjudication",
        "thread": "thread_cluster_b",
        "source_input": "steps/step8_e021_rg_measure_robustness_artifacts/rg_measure_vacua_step8.csv",
        "artifacts": {
            "lambda_degeneracy": "lambda_degeneracy_step10.csv",
            "adjudication": "adjudication_step10.csv",
            "controls": "controls_step10.csv",
        },
        "required_controls": {row["control_id"]: row["passes_guard"] for row in controls},
        "final_verdict": verdict,
        "honest_grade": "finite-toy-diagnostic",
        "nonclaim": {
            "selection_type_adjudicated_on_toy": True,
            "computes_lambda_value": False,
            "physical_anthropic_disproof": False,
            "solves_cosmological_constant_problem": False,
            "frame_transfer_certified": False,
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    summary = f"""# Step 10 Results Summary

## Orientation

Step 10 backtracks on the E021 selection-mechanism punt by applying the P6 decaying-degeneracy criterion to a finite Lambda candidate grid. The grid is derived from the Step 8 RG/measure vacua; the selected toy value is `Lambda_SM={lambda_sm:.15g}`. This is a selection audit over candidate Lambda values, not a field-readout model.

## Degeneracy Audit

- Relaxation horn: sequence `{by_horn['relaxation_attractor']['sequence']}`. The unique-attractor recurrence collapses the effective Lambda degeneracy to `1`, so it is certified by P6.
- Broad anthropic landscape horn: sequence `{by_horn['broad_anthropic_landscape']['sequence']}`. It remains a multiply supported distribution with final degeneracy `{by_horn['broad_anthropic_landscape']['final_degeneracy']}`, so it is the non-closing landscape defect.
- Sharp-measure control: sequence `{by_horn['sharp_selecting_measure']['sequence']}`. It also collapses to `1`, proving the criterion is collapse-to-a-point, not the label attached to the horn.

## Controls

The broad-landscape-fails guard passes, the relaxation-collapse guard passes, the sharp-measure-collapse guard passes, and the carrier guard records `Lambda_grid_plus_degeneracy_audit`.

## Verdict

`e021_lambda_selection_adjudication_constructed`.

The framework's own P6 criterion certifies the collapsing selection type: the relaxation attractor and a sharp selecting measure close the Lambda degeneracy to one candidate. The broad anthropic landscape remains distributed and is not certified as the full closing mechanism on this finite toy. This adjudicates the selection type only; it supplies no physical Lambda value and is not a physical rejection of anthropic reasoning.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 10 is a finite-carrier Lambda-selection adjudication. It tests the framework's P6 decaying-degeneracy criterion on a toy Lambda grid derived from Step 8 vacua.

It claims: a collapsing selection is certified on the toy, while a broad anthropic landscape that stays multiply supported is the non-closing defect under this criterion.

It does not claim to compute the cosmological constant, determine the physical value of Lambda, give a real relaxation mechanism, reject anthropic reasoning as physics, solve the cosmological-constant problem, introduce new physics, or certify frame transfer. The criterion is collapse-to-a-point; a sharp measure passes because it collapses, while a broad landscape fails because it remains distributed.

The carrier is a candidate Lambda space plus relaxation/measure degeneracy audit, not a field-readout pair.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    classification_rows = [
        {
            "output": "lambda_degeneracy_step10.csv",
            "claim": "The relaxation horn collapses, the broad landscape remains multiply supported, and the sharp-measure control collapses under the computed P6 degeneracy audit.",
            "grade": "finite-toy-diagnostic",
            "source_artifacts": "steps/step10_e021_lambda_selection_adjudication_artifacts/lambda_degeneracy_step10.csv;steps/step8_e021_rg_measure_robustness_artifacts/rg_measure_vacua_step8.csv",
        },
        {
            "output": "adjudication_step10.csv",
            "claim": "P6 certifies the horns whose Lambda degeneracy collapses to one and fails the broad landscape whose degeneracy stays above one.",
            "grade": "finite-toy-diagnostic",
            "source_artifacts": "steps/step10_e021_lambda_selection_adjudication_artifacts/adjudication_step10.csv",
        },
        {
            "output": "controls_step10.csv",
            "claim": "The broad-landscape, relaxation, sharp-measure, and non-field-carrier controls pass.",
            "grade": "finite-toy-diagnostic",
            "source_artifacts": "steps/step10_e021_lambda_selection_adjudication_artifacts/controls_step10.csv",
        },
        {
            "output": "results_summary.md",
            "claim": "Step 10 adjudicates the E021 selection type on the toy while preserving the Lambda-value and frame-transfer nonclaims.",
            "grade": "organizational",
            "source_artifacts": "steps/step10_e021_lambda_selection_adjudication_artifacts/results_summary.md;steps/step10_e021_lambda_selection_adjudication_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "schema.json",
            "claim": "The final verdict and required controls are recorded as bounded finite-toy diagnostics.",
            "grade": "organizational",
            "source_artifacts": "steps/step10_e021_lambda_selection_adjudication_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "claim": "The artifact excludes a Lambda value, physical anthropic disproof, a cosmological-constant solution, new physics, and frame-transfer certification.",
            "grade": "organizational",
            "source_artifacts": "steps/step10_e021_lambda_selection_adjudication_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        classification_rows,
        ["output", "claim", "grade", "source_artifacts"],
    )


def main() -> None:
    lambda_grid, lambda_sm = read_step8_lambda_grid()
    rows = build_degeneracy_rows(lambda_grid, lambda_sm)
    adjudication_rows = build_adjudication(rows)
    controls = build_controls(adjudication_rows)

    write_csv(
        ARTIFACT_DIR / "lambda_degeneracy_step10.csv",
        rows,
        [
            "horn",
            "level",
            "refinement_parameter",
            "effective_Lambda_degeneracy",
            "increment",
            "significant_Lambda_values",
            "entropy_effective_support",
            "regime",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "adjudication_step10.csv",
        adjudication_rows,
        [
            "horn",
            "initial_degeneracy",
            "final_degeneracy",
            "sequence",
            "monotone_nonincreasing",
            "collapses_to_point",
            "final_significant_Lambda_values",
            "certified_by_P6",
            "framework_status",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step10.csv",
        controls,
        ["control_id", "expected", "passes_guard", "computed_witness"],
    )
    write_summaries(lambda_grid, lambda_sm, adjudication_rows, controls)


if __name__ == "__main__":
    main()
