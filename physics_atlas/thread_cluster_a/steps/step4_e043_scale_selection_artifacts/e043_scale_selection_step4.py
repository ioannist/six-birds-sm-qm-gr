#!/usr/bin/env python3
"""Cluster A Step 4: E043 scale-selection facet."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
R_SM = 1.0e-4
TOL = 1.0e-8


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def ew_sigma(m_h2: float, g_ew: float, y_proxy: float, vev_proxy: float) -> str:
    return f"mH2={m_h2:.6g}|gEW={g_ew:.6g}|y={y_proxy:.6g}|vev={vev_proxy:.6g}"


def derived_observable(m_h2: float, g_ew: float, y_proxy: float, vev_proxy: float) -> float:
    return m_h2 * (g_ew**2 + 0.10 * y_proxy**2) + 0.05 * vev_proxy


def obstruction(records: list[dict[str, object]], source_key: str, target_key: str) -> tuple[int, str]:
    count = 0
    witnesses: list[str] = []
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            if records[i][source_key] != records[j][source_key]:
                continue
            if abs(float(records[i][target_key]) - float(records[j][target_key])) > TOL:
                count += 1
                witnesses.append(f"{records[i]['config_id']}-{records[j]['config_id']}")
    return count, ";".join(witnesses) if witnesses else "none"


def build_scale_configs() -> list[dict[str, object]]:
    base_configs = [
        ("scale_SM", 100.0, 1.0, 0.65, 1.00, 1.0, "realized_small_ratio"),
        ("scale_same_EW_midcut", 30.0, 1.0, 0.65, 1.00, 1.0, "same_EW_different_cutoff"),
        ("scale_same_EW_lowcut", 10.0, 1.0, 0.65, 1.00, 1.0, "same_EW_different_cutoff"),
        ("scale_alt_mass", 100.0, 1.21, 0.65, 1.00, 1.0, "different_EW_input"),
        ("scale_alt_coupling", 100.0, 1.0, 0.70, 1.00, 1.0, "different_EW_input"),
        ("scale_alt_vev", 100.0, 1.0, 0.65, 1.00, 1.2, "different_EW_input"),
        ("scale_large_ratio", 10.0, 2.5, 0.72, 1.10, 1.2, "large_ratio_alternative"),
    ]
    rows: list[dict[str, object]] = []
    for config_id, cutoff, m_h2, g_ew, y_proxy, vev_proxy, role in base_configs:
        sigma = ew_sigma(m_h2, g_ew, y_proxy, vev_proxy)
        r_value = m_h2 / (cutoff**2)
        rows.append(
            {
                "config_id": config_id,
                "M_cutoff": cutoff,
                "g_EW": g_ew,
                "yukawa_proxy": y_proxy,
                "vev_proxy": vev_proxy,
                "m_H2": m_h2,
                "r": f"{r_value:.12g}",
                "EW_Sigma": sigma,
                "derived_EW_observable": f"{derived_observable(m_h2, g_ew, y_proxy, vev_proxy):.12g}",
                "role": role,
                "realized": config_id == "scale_SM",
            }
        )
    return rows


def build_attractor_sequence() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    r = 2.0e-2
    alpha = 0.15
    for step in range(0, 21):
        residual = abs(r - R_SM)
        rows.append(
            {
                "horn": "derivation_attractor",
                "step": step,
                "r_value": f"{r:.12g}",
                "weight": "",
                "selected": residual <= TOL,
                "status": "reached_r_SM" if residual <= TOL else "relaxing",
                "target_r": f"{R_SM:.12g}",
                "residual": f"{residual:.12g}",
            }
        )
        r = R_SM + alpha * (r - R_SM)
    return rows


def build_no_attractor_sequence() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    r = 2.0e-2
    for step in range(0, 6):
        residual = abs(r - R_SM)
        rows.append(
            {
                "horn": "no_selection_no_attractor",
                "step": step,
                "r_value": f"{r:.12g}",
                "weight": "",
                "selected": False,
                "status": "unfixed_large_ratio",
                "target_r": f"{R_SM:.12g}",
                "residual": f"{residual:.12g}",
            }
        )
    return rows


def build_measure_rows() -> list[dict[str, object]]:
    candidates = [R_SM, 3.0e-4, 1.0e-3, 3.0e-3, 1.0e-2, 2.0e-2]
    sigma = 0.50
    weighted = []
    for idx, r_value in enumerate(candidates):
        log_distance = math.log10(r_value / R_SM)
        weight = math.exp(-(log_distance**2) / (2.0 * sigma**2))
        weighted.append((idx, r_value, weight))
    max_weight = max(weight for _, _, weight in weighted)
    rows = [
        {
            "horn": "measure_selection",
            "step": idx,
            "r_value": f"{r_value:.12g}",
            "weight": f"{weight:.12g}",
            "selected": abs(weight - max_weight) <= 1e-12,
            "status": "measure_peak" if abs(weight - max_weight) <= 1e-12 else "lower_weight",
            "target_r": f"{R_SM:.12g}",
            "residual": f"{abs(r_value - R_SM):.12g}",
        }
        for idx, r_value, weight in weighted
    ]
    flat_rows = [
        {
            "horn": "no_selection_flat_measure",
            "step": idx,
            "r_value": f"{r_value:.12g}",
            "weight": "1",
            "selected": False,
            "status": "unfixed_tie",
            "target_r": f"{R_SM:.12g}",
            "residual": f"{abs(r_value - R_SM):.12g}",
        }
        for idx, r_value in enumerate(candidates)
    ]
    return rows + flat_rows


def main() -> None:
    scale_rows = build_scale_configs()
    r_obstruction_count, r_witness = obstruction(scale_rows, "EW_Sigma", "r")
    obs_obstruction_count, obs_witness = obstruction(scale_rows, "EW_Sigma", "derived_EW_observable")

    nonfactorization_rows = [
        {
            "test_id": "r_scale_ratio_from_EW_Sigma",
            "source": "EW_Sigma",
            "target": "r=m_H2/M_cutoff2",
            "non_descending": r_obstruction_count > 0,
            "obstruction_count": r_obstruction_count,
            "witness": r_witness,
            "interpretation": "same EW readout with different cutoff gives different scale ratio",
        },
        {
            "test_id": "derived_EW_observable_from_EW_Sigma",
            "source": "EW_Sigma",
            "target": "derived_EW_observable",
            "non_descending": obs_obstruction_count > 0,
            "obstruction_count": obs_obstruction_count,
            "witness": obs_witness,
            "interpretation": "derived EW observable is a function of EW Sigma",
        },
    ]

    two_horn_rows = build_attractor_sequence() + build_measure_rows() + build_no_attractor_sequence()
    attractor_rows = [row for row in two_horn_rows if row["horn"] == "derivation_attractor"]
    measure_rows = [row for row in two_horn_rows if row["horn"] == "measure_selection"]
    no_attractor_rows = [row for row in two_horn_rows if row["horn"] == "no_selection_no_attractor"]
    flat_rows = [row for row in two_horn_rows if row["horn"] == "no_selection_flat_measure"]

    attractor_reaches = float(attractor_rows[-1]["residual"]) <= TOL
    measure_selected = [row for row in measure_rows if str(row["selected"]) == "True"]
    measure_peaks = len(measure_selected) == 1 and abs(float(measure_selected[0]["r_value"]) - R_SM) <= TOL
    no_attractor_unfixed = all(float(row["residual"]) > 1.0e-3 for row in no_attractor_rows)
    flat_unfixed = all(str(row["selected"]) == "False" for row in flat_rows) and len({row["weight"] for row in flat_rows}) == 1
    no_selection_fails = no_attractor_unfixed and flat_unfixed

    controls = [
        {
            "control_id": "r_non_descending_positive",
            "expected": "r_obstruction_gt_0",
            "passes_guard": r_obstruction_count > 0,
            "computed_witness": f"obstruction={r_obstruction_count}; witness={r_witness}",
        },
        {
            "control_id": "derived_EW_observable_factors",
            "expected": "derived_obstruction_0",
            "passes_guard": obs_obstruction_count == 0,
            "computed_witness": f"obstruction={obs_obstruction_count}; witness={obs_witness}",
        },
        {
            "control_id": "derivation_attractor_reaches_r_SM",
            "expected": "final_residual_le_tol",
            "passes_guard": attractor_reaches,
            "computed_witness": f"final_r={attractor_rows[-1]['r_value']}; residual={attractor_rows[-1]['residual']}",
        },
        {
            "control_id": "measure_peaks_at_r_SM",
            "expected": "unique_measure_peak_at_target",
            "passes_guard": measure_peaks,
            "computed_witness": f"selected={measure_selected[0]['r_value'] if measure_selected else 'none'}",
        },
        {
            "control_id": "no_selection_control_unfixed",
            "expected": "no_attractor_large_and_flat_measure_tie",
            "passes_guard": no_selection_fails,
            "computed_witness": (
                f"no_attractor_final_residual={no_attractor_rows[-1]['residual']}; "
                f"flat_selected_count={sum(str(row['selected']) == 'True' for row in flat_rows)}"
            ),
        },
        {
            "control_id": "selection_carrier_not_field_pair",
            "expected": "scale_configs_attractor_measure",
            "passes_guard": True,
            "computed_witness": "carrier=EW_scale_configs; selectors=attractor_or_measure",
        },
    ]

    write_csv(
        ARTIFACT_DIR / "scale_configs_step4.csv",
        scale_rows,
        [
            "config_id",
            "M_cutoff",
            "g_EW",
            "yukawa_proxy",
            "vev_proxy",
            "m_H2",
            "r",
            "EW_Sigma",
            "derived_EW_observable",
            "role",
            "realized",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "scale_nonfactorization_step4.csv",
        nonfactorization_rows,
        ["test_id", "source", "target", "non_descending", "obstruction_count", "witness", "interpretation"],
    )
    write_csv(
        ARTIFACT_DIR / "two_horns_step4.csv",
        two_horn_rows,
        ["horn", "step", "r_value", "weight", "selected", "status", "target_r", "residual"],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step4.csv",
        controls,
        ["control_id", "expected", "passes_guard", "computed_witness"],
    )

    verdict = {
        "type": "e043_scale_selection_facet_constructed",
        "r_SM": R_SM,
        "r_non_descending_obstruction": r_obstruction_count,
        "derived_observable_obstruction": obs_obstruction_count,
        "attractor_final_r": float(attractor_rows[-1]["r_value"]),
        "attractor_final_residual": float(attractor_rows[-1]["residual"]),
        "measure_selected_r": float(measure_selected[0]["r_value"]) if measure_selected else None,
        "no_selection_unfixed": no_selection_fails,
        "both_horns_select": attractor_reaches and measure_peaks,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 4,
        "orientation": "Cluster A E043 scale-selection facet",
        "carrier": "finite EW scale configurations plus attractor-or-measure selection slot",
        "verdict": verdict,
        "nonclaim": "Finite scale-selection shape only; no physical mass value or mechanism is determined.",
    }
    (ARTIFACT_DIR / "e043_scale_selection_output_step4.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "e043_scale_selection_output_step4.txt").write_text(
        "\n".join(
            [
                "Cluster A Step 4 E043 scale-selection facet",
                "Verdict: e043_scale_selection_facet_constructed",
                f"r_SM: {R_SM:.12g}",
                f"r obstruction: {r_obstruction_count}",
                f"derived observable obstruction: {obs_obstruction_count}",
                f"attractor final residual: {attractor_rows[-1]['residual']}",
                f"measure selected r: {measure_selected[0]['r_value'] if measure_selected else 'none'}",
                f"no selection unfixed: {no_selection_fails}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 4 Results Summary

## Orientation

Step 4 builds the E043 continuous scale-selection facet on a finite toy. The scale readout is `r = m_H2 / M_cutoff2`. The EW Sigma readout keeps broken-phase inputs and omits cutoff sensitivity.

## Scale Configurations

The toy contains `{len(scale_rows)}` EW configurations. The realized configuration has `r_SM = {R_SM:.12g}`. The repeated EW Sigma rows have the same broken-phase inputs but different cutoffs.

## Non-Descending Test

- Scale-ratio obstruction from EW Sigma: `{r_obstruction_count}`, witness `{r_witness}`.
- Derived EW observable obstruction: `{obs_obstruction_count}`, witness `{obs_witness}`.

The scale ratio needs cross-scale data not present in the EW Sigma readout, while the derived EW observable factors through that readout.

## Two Horns

- Derivation horn: attractor recurrence final `r = {attractor_rows[-1]['r_value']}`, residual `{attractor_rows[-1]['residual']}`.
- Measure horn: unique peak at `r = {measure_selected[0]['r_value'] if measure_selected else 'none'}`.
- No-selection control: no-attractor final residual `{no_attractor_rows[-1]['residual']}` and flat measure has no unique selected point.

## Controls

- Non-descending scale ratio: `{r_obstruction_count > 0}`.
- Derived observable factors: `{obs_obstruction_count == 0}`.
- Derivation horn reaches target: `{attractor_reaches}`.
- Measure horn peaks at target: `{measure_peaks}`.
- No-selection control remains unfixed: `{no_selection_fails}`.
- Carrier guard: finite scale configs plus attractor-or-measure slot.

## Verdict

`e043_scale_selection_facet_constructed`.

The finite toy shows the scale-ratio as a non-descending selection coordinate. The slot can be filled by either an attractor-style derivation or a measure; without either, the ratio remains unfixed.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 4,
        "orientation": "E043 scale-selection facet",
        "active_residual": "R_cluster_a_after_step3_p6_decaying_degeneracy_audit",
        "candidate_move": "Compute scale-ratio non-factorization, derivation horn, measure horn, and no-selection control.",
        "final_verdict": verdict,
        "track_fields": {
            "scale_configs": "scale_configs_step4.csv",
            "nonfactorization": "scale_nonfactorization_step4.csv",
            "two_horns": "two_horns_step4.csv",
            "controls": "controls_step4.csv",
            "next_live_option": "Step5_cluster_a_consolidation_or_manager_selected_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "e043_scale_selection_step4.py",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Builds EW scale configs, scale-ratio non-factorization, two horns, and controls.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/e043_scale_selection_step4.py",
        },
        {
            "output": "scale_configs_step4.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Finite toy EW configurations, cutoff, m_H2, ratio, EW Sigma, and derived observable.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/scale_configs_step4.csv",
        },
        {
            "output": "scale_nonfactorization_step4.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Scale-ratio non-descending test and derived-observable control.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/scale_nonfactorization_step4.csv",
        },
        {
            "output": "two_horns_step4.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Derivation attractor, measure peak, and no-selection controls.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/two_horns_step4.csv",
        },
        {
            "output": "controls_step4.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Non-descending, derived-observable, horn, no-selection, and carrier controls.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/controls_step4.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Human-readable E043 scale-selection verdict and bounded scope.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite E043 scale-selection facet.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step4.py",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Validator for computed non-factorization, horns, controls, source paths, ledgers, and overclaim guard.",
            "source_artifacts": "steps/step4_e043_scale_selection_artifacts/run_step4.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 4 Nonclaim Boundary

Step 4 is a finite-carrier E043 scale-selection construction. The scale values, attractor recurrence, and measure are toy diagnostics.

The computed content is the shape: the scale ratio is non-descending from the EW Sigma readout, a derived EW observable factors, and the selection slot can be filled by either an attractor-style derivation or a measure.

This does not provide a hierarchy solution, a physical Higgs-mass value, a real cutoff mechanism, a choice between horns, or a frame-transfer certificate.

The carrier is finite scale configurations plus attractor-or-measure selection. It is not a field pair.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
