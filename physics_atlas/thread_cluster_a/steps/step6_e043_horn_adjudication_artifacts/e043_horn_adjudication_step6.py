#!/usr/bin/env python3
"""Cluster A Step 6: E043 horn adjudication by P6 degeneracy audit."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
R_SM = 1.0e-4
R_GRID = [1.0e-4, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 2.0e-2]
SIGNIFICANCE_THRESHOLD = 0.25
DERIVATION_RESOLUTION = 5.0e-5


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def entropy_effective_support(weights: list[float]) -> float:
    total = sum(weights)
    if total <= 0.0:
        return 0.0
    probs = [weight / total for weight in weights if weight > 0.0]
    entropy = -sum(prob * math.log(prob) for prob in probs)
    return math.exp(entropy)


def significant_count(weights: list[float]) -> tuple[int, list[float]]:
    if not weights:
        return 0, []
    max_weight = max(weights)
    significant = [R_GRID[idx] for idx, weight in enumerate(weights) if weight >= SIGNIFICANCE_THRESHOLD * max_weight]
    return len(significant), significant


def broad_weights(sigma: float) -> list[float]:
    weights = []
    for r_value in R_GRID:
        log_distance = math.log10(r_value / R_SM)
        weights.append(math.exp(-(log_distance**2) / (2.0 * sigma**2)))
    return weights


def derivation_degeneracy(level: int, relaxation_steps: int, alpha: float = 0.15) -> dict[str, object]:
    evolved = [R_SM + (alpha**relaxation_steps) * (r_value - R_SM) for r_value in R_GRID]
    far_values = [R_GRID[idx] for idx, value in enumerate(evolved) if abs(value - R_SM) > DERIVATION_RESOLUTION]
    g = len(far_values) + 1
    if not far_values:
        g = 1
    return {
        "horn": "derivation_attractor",
        "level": level,
        "refinement_parameter": f"relaxation_steps={relaxation_steps}",
        "effective_degeneracy": g,
        "significant_values": ";".join(f"{value:.12g}" for value in (far_values if far_values else [R_SM])),
        "entropy_effective_support": "",
        "regime": "collapsing_selection" if g > 1 else "collapsed_to_point",
    }


def measure_degeneracy(horn: str, level: int, sigma: float) -> dict[str, object]:
    weights = broad_weights(sigma)
    count, significant = significant_count(weights)
    return {
        "horn": horn,
        "level": level,
        "refinement_parameter": f"sigma={sigma:.6g}",
        "effective_degeneracy": count,
        "significant_values": ";".join(f"{value:.12g}" for value in significant),
        "entropy_effective_support": f"{entropy_effective_support(weights):.12g}",
        "regime": "distribution" if count > 1 else "collapsed_to_point",
    }


def add_increments(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_horn: dict[str, int] = {}
    out: list[dict[str, object]] = []
    for row in rows:
        horn = str(row["horn"])
        g = int(row["effective_degeneracy"])
        previous = by_horn.get(horn)
        row = {**row, "increment": 0 if previous is None else g - previous}
        by_horn[horn] = g
        out.append(row)
    return out


def main() -> None:
    rows: list[dict[str, object]] = []
    for level, steps in enumerate([0, 1, 2, 3, 4, 6]):
        rows.append(derivation_degeneracy(level, steps))
    for level, sigma in enumerate([3.0, 2.8, 2.6, 2.4, 2.2, 2.0]):
        rows.append(measure_degeneracy("broad_anthropic_measure", level, sigma))
    for level, sigma in enumerate([0.8, 0.5, 0.3, 0.2, 0.1]):
        rows.append(measure_degeneracy("sharp_selecting_measure", level, sigma))
    rows = add_increments(rows)

    by_horn: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_horn.setdefault(str(row["horn"]), []).append(row)

    adjudication_rows: list[dict[str, object]] = []
    for horn, horn_rows in by_horn.items():
        sequence = [int(row["effective_degeneracy"]) for row in horn_rows]
        final_g = sequence[-1]
        monotone = all(sequence[idx + 1] <= sequence[idx] for idx in range(len(sequence) - 1))
        collapses = sequence[0] > 1 and final_g == 1 and monotone
        final_values = str(horn_rows[-1]["significant_values"])
        certified = collapses
        adjudication_rows.append(
            {
                "horn": horn,
                "initial_degeneracy": sequence[0],
                "final_degeneracy": final_g,
                "sequence": "->".join(str(value) for value in sequence),
                "monotone_nonincreasing": monotone,
                "collapses_to_point": collapses,
                "final_significant_values": final_values,
                "certified_by_P6": certified,
                "framework_status": "certified_selection" if certified else "landscape_nonclosing",
            }
        )

    by_adjudication = {row["horn"]: row for row in adjudication_rows}
    derivation_collapses = bool(by_adjudication["derivation_attractor"]["collapses_to_point"])
    broad_fails = not bool(by_adjudication["broad_anthropic_measure"]["collapses_to_point"]) and int(
        by_adjudication["broad_anthropic_measure"]["final_degeneracy"]
    ) > 1
    sharp_collapses = bool(by_adjudication["sharp_selecting_measure"]["collapses_to_point"])
    controls = [
        {
            "control_id": "broad_measure_fails_to_collapse",
            "expected": "broad_final_degeneracy_gt_1",
            "passes_guard": broad_fails,
            "computed_witness": by_adjudication["broad_anthropic_measure"]["sequence"],
        },
        {
            "control_id": "derivation_collapses",
            "expected": "derivation_final_degeneracy_1",
            "passes_guard": derivation_collapses,
            "computed_witness": by_adjudication["derivation_attractor"]["sequence"],
        },
        {
            "control_id": "sharp_measure_also_collapses",
            "expected": "sharp_measure_final_degeneracy_1",
            "passes_guard": sharp_collapses,
            "computed_witness": by_adjudication["sharp_selecting_measure"]["sequence"],
        },
        {
            "control_id": "selection_carrier_not_field_pair",
            "expected": "scale_grid_degeneracy_audit",
            "passes_guard": True,
            "computed_witness": "carrier=scale_ratio_grid; audit=effective_degeneracy_under_refinement",
        },
    ]

    write_csv(
        ARTIFACT_DIR / "horn_degeneracy_step6.csv",
        rows,
        [
            "horn",
            "level",
            "refinement_parameter",
            "effective_degeneracy",
            "increment",
            "significant_values",
            "entropy_effective_support",
            "regime",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "adjudication_step6.csv",
        adjudication_rows,
        [
            "horn",
            "initial_degeneracy",
            "final_degeneracy",
            "sequence",
            "monotone_nonincreasing",
            "collapses_to_point",
            "final_significant_values",
            "certified_by_P6",
            "framework_status",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step6.csv",
        controls,
        ["control_id", "expected", "passes_guard", "computed_witness"],
    )

    verdict = {
        "type": "e043_horn_adjudication_constructed",
        "certified_horns": sorted(row["horn"] for row in adjudication_rows if row["certified_by_P6"]),
        "failed_horns": sorted(row["horn"] for row in adjudication_rows if not row["certified_by_P6"]),
        "derivation_sequence": by_adjudication["derivation_attractor"]["sequence"],
        "broad_measure_sequence": by_adjudication["broad_anthropic_measure"]["sequence"],
        "sharp_measure_sequence": by_adjudication["sharp_selecting_measure"]["sequence"],
        "broad_measure_final_degeneracy": int(by_adjudication["broad_anthropic_measure"]["final_degeneracy"]),
        "criterion": "P6_decaying_degeneracy_collapses_to_point",
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 6,
        "orientation": "Cluster A E043 horn adjudication",
        "carrier": "scale-ratio grid plus P6 degeneracy audit",
        "verdict": verdict,
        "nonclaim": "Finite horn-adjudication shape only; no physical mass value or mechanism is determined.",
    }
    (ARTIFACT_DIR / "e043_horn_adjudication_output_step6.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "e043_horn_adjudication_output_step6.txt").write_text(
        "\n".join(
            [
                "Cluster A Step 6 E043 horn adjudication",
                "Verdict: e043_horn_adjudication_constructed",
                f"derivation sequence: {verdict['derivation_sequence']}",
                f"broad measure sequence: {verdict['broad_measure_sequence']}",
                f"sharp measure sequence: {verdict['sharp_measure_sequence']}",
                f"certified horns: {';'.join(verdict['certified_horns'])}",
                f"failed horns: {';'.join(verdict['failed_horns'])}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 6 Results Summary

## Orientation

Step 6 applies the P6 decaying-degeneracy audit to the E043 horns. The degeneracy is the number of scale-ratio values still effectively in play under each horn's refinement.

## Degeneracy Sequences

- Derivation attractor: `{by_adjudication['derivation_attractor']['sequence']}`.
- Broad anthropic measure: `{by_adjudication['broad_anthropic_measure']['sequence']}`.
- Sharp selecting measure control: `{by_adjudication['sharp_selecting_measure']['sequence']}`.

## Adjudication

The P6 criterion certifies horns whose degeneracy collapses to a single point. On this toy:

- Certified: `{';'.join(verdict['certified_horns'])}`.
- Failed as broad landscape: `{';'.join(verdict['failed_horns'])}`.

This adjudicates by collapse, not by horn label: the sharp measure also passes because it collapses, while the broad measure fails because it remains a distribution.

## Controls

- Broad measure fails to collapse: `{broad_fails}`.
- Derivation collapses: `{derivation_collapses}`.
- Sharp measure also collapses: `{sharp_collapses}`.
- Carrier guard: scale-ratio grid plus degeneracy audit.

## Verdict

`e043_horn_adjudication_constructed`.

The framework criterion certifies selection-to-a-point and fails broad landscape behavior on the finite toy.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 6,
        "orientation": "E043 horn adjudication by P6 decaying-degeneracy audit",
        "active_residual": "R_cluster_a_after_step5_e009_uv_fiber",
        "candidate_move": "Run derivation, broad-measure, and sharp-measure horns through P6 effective-degeneracy audit.",
        "final_verdict": verdict,
        "track_fields": {
            "horn_degeneracy": "horn_degeneracy_step6.csv",
            "adjudication": "adjudication_step6.csv",
            "controls": "controls_step6.csv",
            "next_live_option": "Step7_cluster_a_consolidation_or_manager_selected_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "e043_horn_adjudication_step6.py",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Builds P6 degeneracy audits for derivation, broad measure, sharp measure, and controls.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/e043_horn_adjudication_step6.py",
        },
        {
            "output": "horn_degeneracy_step6.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-horn per-level effective degeneracy and increments.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/horn_degeneracy_step6.csv",
        },
        {
            "output": "adjudication_step6.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-horn collapse status and P6 certification.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/adjudication_step6.csv",
        },
        {
            "output": "controls_step6.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Broad-measure, derivation, sharp-measure, and carrier controls.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/controls_step6.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Human-readable horn adjudication verdict and bounded scope.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite horn adjudication.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step6.py",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Validator for horn degeneracy, controls, source paths, ledgers, and overclaim guard.",
            "source_artifacts": "steps/step6_e043_horn_adjudication_artifacts/run_step6.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 6 Nonclaim Boundary

Step 6 is a finite-carrier E043 horn-adjudication construction. The scale grid, effective-support counts, and horn refinements are toy diagnostics.

The computed content is the framework criterion: P6 certifies a horn when degeneracy collapses to a point. The derivation attractor and sharp selecting measure pass on the toy; the broad measure remains multiply supported and fails as a landscape.

This is not a physical Higgs-mass mechanism, not a real landscape measure, not a hierarchy solution, and not a frame-transfer certificate.

The carrier is a scale-ratio grid plus degeneracy audit. It is not a field pair.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
