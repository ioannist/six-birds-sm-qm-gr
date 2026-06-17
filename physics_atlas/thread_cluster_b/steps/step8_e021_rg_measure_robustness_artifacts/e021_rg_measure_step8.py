#!/usr/bin/env python3
"""Cluster B Step 8: E021 RG/measure robustness toy."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Iterable


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
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
    out: list[object] = []
    for value in values:
        if isinstance(value, float):
            out.append(round(value, 10))
        else:
            out.append(value)
    return tuple(out)


def obstruction(records: list[dict[str, object]], source_keys: list[str], target_key: str) -> tuple[int, str]:
    count = 0
    witnesses: list[str] = []
    for i, j in itertools.combinations(range(len(records)), 2):
        left = key_for(records[i][key] for key in source_keys)
        right = key_for(records[j][key] for key in source_keys)
        if left != right:
            continue
        a = records[i][target_key]
        b = records[j][target_key]
        differs = abs(float(a) - float(b)) > TOL if isinstance(a, (float, int)) else a != b
        if differs:
            count += 1
            witnesses.append(f"{records[i]['config_id']}-{records[j]['config_id']}")
    return count, ";".join(witnesses) if witnesses else "none"


def rg_flow(g_uv: float, beta0: float, steps: int = 4) -> list[float]:
    values = [g_uv]
    g = g_uv
    for _ in range(steps - 1):
        g = g - beta0 * g**3
        values.append(g)
    return values


def lambda_candidate(phi: float, g_ir: float, cutoff: float, spectrum_code: int) -> float:
    base = 0.000001 * cutoff + 0.0002 * spectrum_code + 0.0007 * g_ir
    return base + 0.00035 * phi * phi + 0.00011 * phi


def no_selection_lambda(g_ir: float, cutoff: float, spectrum_code: int) -> float:
    return 0.000001 * cutoff + 0.0002 * spectrum_code + 0.0007 * g_ir


def main() -> None:
    phi_grid = [-2.0, -1.0, 0.0, 1.0, 2.0]
    configs = [
        {
            "config_id": "A_left",
            "uv_id": "UV_A",
            "cutoff": 1000.0,
            "spectrum_code": 7,
            "g_uv": 0.82,
            "beta0": 0.045,
            "measure_center": -1.35,
            "measure_width": 1.0,
        },
        {
            "config_id": "A_right",
            "uv_id": "UV_A",
            "cutoff": 1000.0,
            "spectrum_code": 7,
            "g_uv": 0.82,
            "beta0": 0.045,
            "measure_center": 1.25,
            "measure_width": 1.0,
        },
        {
            "config_id": "A_far_right",
            "uv_id": "UV_A",
            "cutoff": 1000.0,
            "spectrum_code": 7,
            "g_uv": 0.82,
            "beta0": 0.045,
            "measure_center": 2.2,
            "measure_width": 1.0,
        },
        {
            "config_id": "B_center",
            "uv_id": "UV_B",
            "cutoff": 1700.0,
            "spectrum_code": 11,
            "g_uv": 0.68,
            "beta0": 0.035,
            "measure_center": 0.1,
            "measure_width": 1.2,
        },
        {
            "config_id": "B_left",
            "uv_id": "UV_B",
            "cutoff": 1700.0,
            "spectrum_code": 11,
            "g_uv": 0.68,
            "beta0": 0.035,
            "measure_center": -1.8,
            "measure_width": 1.2,
        },
    ]

    vacua_rows: list[dict[str, object]] = []
    config_records: list[dict[str, object]] = []
    for cfg in configs:
        flow = rg_flow(float(cfg["g_uv"]), float(cfg["beta0"]))
        g_ir = flow[-1]
        running = ";".join(f"mu{idx}:{value:.10f}" for idx, value in enumerate(flow))
        scored: list[tuple[float, float, float]] = []
        for phi in phi_grid:
            score = ((phi - float(cfg["measure_center"])) / float(cfg["measure_width"])) ** 2
            lam = lambda_candidate(phi, g_ir, float(cfg["cutoff"]), int(cfg["spectrum_code"]))
            scored.append((score, phi, lam))
        score_star, phi_star, lambda_star = min(scored, key=lambda item: (item[0], abs(item[1])))
        no_select = no_selection_lambda(g_ir, float(cfg["cutoff"]), int(cfg["spectrum_code"]))
        config_record = {
            "config_id": cfg["config_id"],
            "uv_id": cfg["uv_id"],
            "cutoff": cfg["cutoff"],
            "spectrum_code": cfg["spectrum_code"],
            "g_uv": cfg["g_uv"],
            "beta0": cfg["beta0"],
            "g_IR": g_ir,
            "measure_center": cfg["measure_center"],
            "selected_phi_star": phi_star,
            "realized_Lambda": lambda_star,
            "no_selection_Lambda": no_select,
        }
        config_records.append(config_record)
        for score, phi, lam in scored:
            vacua_rows.append(
                {
                    "config_id": cfg["config_id"],
                    "uv_id": cfg["uv_id"],
                    "cutoff": cfg["cutoff"],
                    "spectrum_code": cfg["spectrum_code"],
                    "g_uv": cfg["g_uv"],
                    "beta0": cfg["beta0"],
                    "g_running": running,
                    "g_IR": g_ir,
                    "modulus_phi": phi,
                    "measure_center": cfg["measure_center"],
                    "selection_score": score,
                    "selected": phi == phi_star,
                    "selected_phi_star": phi_star,
                    "lambda_candidate": lam,
                    "realized_Lambda": lambda_star,
                    "no_selection_Lambda": no_select,
                }
            )

    bare_uv_keys = ["cutoff", "spectrum_code", "g_uv", "beta0"]
    lambda_bare_count, lambda_bare_witness = obstruction(config_records, bare_uv_keys, "realized_Lambda")
    lambda_enriched_count, lambda_enriched_witness = obstruction(
        config_records, [*bare_uv_keys, "selected_phi_star"], "realized_Lambda"
    )
    phi_bare_count, phi_bare_witness = obstruction(config_records, bare_uv_keys, "selected_phi_star")
    g_bare_count, g_bare_witness = obstruction(config_records, bare_uv_keys, "g_IR")
    no_select_count, no_select_witness = obstruction(config_records, bare_uv_keys, "no_selection_Lambda")

    nonfact_rows = [
        {
            "test_id": "Lambda_from_bare_UV",
            "source_sigma": "cutoff,spectrum_code,g_uv,beta0",
            "target": "realized_Lambda",
            "obstruction_count": lambda_bare_count,
            "nonfactorizing": lambda_bare_count > 0,
            "witness": lambda_bare_witness,
            "verdict": "non_descending_from_bare_UV",
        },
        {
            "test_id": "Lambda_from_UV_selected_phi",
            "source_sigma": "cutoff,spectrum_code,g_uv,beta0,selected_phi_star",
            "target": "realized_Lambda",
            "obstruction_count": lambda_enriched_count,
            "nonfactorizing": lambda_enriched_count > 0,
            "witness": lambda_enriched_witness,
            "verdict": "descends_after_selection_included",
        },
        {
            "test_id": "phi_star_from_bare_UV",
            "source_sigma": "cutoff,spectrum_code,g_uv,beta0",
            "target": "selected_phi_star",
            "obstruction_count": phi_bare_count,
            "nonfactorizing": phi_bare_count > 0,
            "witness": phi_bare_witness,
            "verdict": "selection_non_descending_from_bare_UV",
        },
        {
            "test_id": "g_IR_from_bare_UV",
            "source_sigma": "cutoff,spectrum_code,g_uv,beta0",
            "target": "g_IR",
            "obstruction_count": g_bare_count,
            "nonfactorizing": g_bare_count > 0,
            "witness": g_bare_witness,
            "verdict": "RG_derived_descending",
        },
        {
            "test_id": "no_selection_Lambda_from_bare_UV",
            "source_sigma": "cutoff,spectrum_code,g_uv,beta0",
            "target": "no_selection_Lambda",
            "obstruction_count": no_select_count,
            "nonfactorizing": no_select_count > 0,
            "witness": no_select_witness,
            "verdict": "no_selection_control_descending",
        },
    ]

    controls = [
        {
            "control_id": "RG_derived_g_IR_descends",
            "expected": "descendable",
            "obstruction_count": g_bare_count,
            "passes_guard": g_bare_count == 0,
            "witness": g_bare_witness,
        },
        {
            "control_id": "no_selection_Lambda_descends",
            "expected": "descendable",
            "obstruction_count": no_select_count,
            "passes_guard": no_select_count == 0,
            "witness": no_select_witness,
        },
        {
            "control_id": "selection_relocation",
            "expected": "Lambda_descends_with_phi_but_phi_not_from_bare_UV",
            "obstruction_count": phi_bare_count,
            "passes_guard": lambda_enriched_count == 0 and phi_bare_count > 0,
            "witness": phi_bare_witness,
        },
        {
            "control_id": "realized_Lambda_not_RG_derived_from_bare_UV",
            "expected": "selection_residue",
            "obstruction_count": lambda_bare_count,
            "passes_guard": lambda_bare_count > 0,
            "witness": lambda_bare_witness,
        },
    ]

    write_csv(
        ARTIFACT_DIR / "rg_measure_vacua_step8.csv",
        vacua_rows,
        [
            "config_id",
            "uv_id",
            "cutoff",
            "spectrum_code",
            "g_uv",
            "beta0",
            "g_running",
            "g_IR",
            "modulus_phi",
            "measure_center",
            "selection_score",
            "selected",
            "selected_phi_star",
            "lambda_candidate",
            "realized_Lambda",
            "no_selection_Lambda",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "nonfactorization_step8.csv",
        nonfact_rows,
        ["test_id", "source_sigma", "target", "obstruction_count", "nonfactorizing", "witness", "verdict"],
    )
    write_csv(
        ARTIFACT_DIR / "controls_step8.csv",
        controls,
        ["control_id", "expected", "obstruction_count", "passes_guard", "witness"],
    )

    verdict = {
        "type": "E021_rg_measure_robustness_established",
        "Lambda_non_descending_from_bare_UV": lambda_bare_count > 0,
        "Lambda_descends_when_selection_included": lambda_enriched_count == 0,
        "selection_non_descending_from_bare_UV": phi_bare_count > 0,
        "RG_control_descends": g_bare_count == 0,
        "no_selection_control_descends": no_select_count == 0,
        "selection_relocation": lambda_enriched_count == 0 and phi_bare_count > 0,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    output = {
        "step": 8,
        "orientation": "E021 RG/measure robustness",
        "toy_fields": {
            "moduli_grid": phi_grid,
            "config_count": len(configs),
            "bare_UV_sigma": bare_uv_keys,
        },
        "verdict": verdict,
        "nonclaim": "Finite toy RG/measure/moduli construction only; no Lambda value or real selection mechanism.",
    }
    (ARTIFACT_DIR / "e021_rg_measure_output_step8.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "e021_rg_measure_output_step8.txt").write_text(
        "\n".join(
            [
                "Cluster B Step 8 E021 RG/measure robustness",
                "Verdict: E021_rg_measure_robustness_established",
                f"Lambda from bare UV obstruction: {lambda_bare_count}",
                f"Lambda from UV+selected_phi obstruction: {lambda_enriched_count}",
                f"phi_star from bare UV obstruction: {phi_bare_count}",
                f"g_IR from bare UV obstruction: {g_bare_count}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    summary = f"""# Step 8 Results Summary

## Orientation

Step 8 replaces the hand-built Step 3 selection pair with a structured finite toy: a moduli grid, deterministic toy RG flow, and a measure/relaxation score that selects a realized modulus.

## RG / Measure Toy

The bare UV Sigma is `(cutoff, spectrum_code, g_uv, beta0)`. The RG flow computes `g_IR` by a beta-function recurrence. The measure score selects `selected_phi_star` from the moduli grid `{phi_grid}`. The realized `Lambda` is a function of the bare UV and the selected modulus.

## Non-Factorization

- `Lambda_from_bare_UV`: obstruction `{lambda_bare_count}`, witnesses `{lambda_bare_witness}`.
- `Lambda_from_UV_selected_phi`: obstruction `{lambda_enriched_count}`.
- `phi_star_from_bare_UV`: obstruction `{phi_bare_count}`, witnesses `{phi_bare_witness}`.
- `g_IR_from_bare_UV`: obstruction `{g_bare_count}`.
- `no_selection_Lambda_from_bare_UV`: obstruction `{no_select_count}`.

## Controls

The RG-derived control passes: `g_IR` descends from the bare UV with obstruction `{g_bare_count}`.

The no-selection control passes: a Lambda-like readout with no modulus/measure residue descends from the bare UV with obstruction `{no_select_count}`.

Selection relocation passes: once `selected_phi_star` is included in Sigma, `Lambda` descends with obstruction `{lambda_enriched_count}`, while `selected_phi_star` itself remains non-descending from bare UV with obstruction `{phi_bare_count}`.

## Verdict

`E021_rg_measure_robustness_established`.

On this finite RG/measure toy, `Lambda` stays non-descending from the bare UV. The adversarial Sigma that includes the selected modulus makes `Lambda` descend, but the non-descendingness relocates to the selection. The RG running is genuinely UV-derived, so the test has teeth. The toy supplies no physical value or real selection mechanism.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    schema = {
        "step": 8,
        "orientation": "E021 RG/measure robustness",
        "active_residual": "R_cluster_b_after_step7_E042_earned_continuation",
        "candidate_move": "Build toy RG flow plus measure-selected moduli, test bare-UV and enriched-Sigma factorization, and run controls.",
        "final_verdict": verdict,
        "track_fields": {
            "vacua": "rg_measure_vacua_step8.csv",
            "nonfactorization": "nonfactorization_step8.csv",
            "controls": "controls_step8.csv",
            "next_live_option": "Cluster_B_external_frame_transfer_review_or_manager_selected_followup",
        },
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "output": "e021_rg_measure_step8.py",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Builds moduli grid, toy RG flow, measure selection, Lambda readout, obstructions, and controls.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/e021_rg_measure_step8.py;steps/step3_e021_cosmological_constant_artifacts/results_summary.md",
        },
        {
            "output": "rg_measure_vacua_step8.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Vacuum candidates, RG running, selection score, selected modulus, and realized Lambda.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/rg_measure_vacua_step8.csv",
        },
        {
            "output": "nonfactorization_step8.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "Bare-UV, enriched-Sigma, selection-relocation, RG-derived, and no-selection obstruction recomputes.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/nonfactorization_step8.csv",
        },
        {
            "output": "controls_step8.csv",
            "classification": "analytical structural",
            "grade": "finite-toy-diagnostic",
            "scope": "RG-derived, no-selection, and selection-relocation controls.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/controls_step8.csv",
        },
        {
            "output": "results_summary.md",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Human-readable E021 robustness verdict and bounded scope.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/results_summary.md",
        },
        {
            "output": "schema.json",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Per-step schema and final verdict.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/schema.json",
        },
        {
            "output": "nonclaim_boundary.md",
            "classification": "organizational/audit",
            "grade": "organizational",
            "scope": "Scope boundary for finite RG/measure toy.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/nonclaim_boundary.md",
        },
        {
            "output": "run_step8.py",
            "classification": "organizational/audit",
            "grade": "finite-toy-diagnostic",
            "scope": "Validator for RG/measure selection, factorization, controls, source paths, ledgers, prior validators, and overclaim guard.",
            "source_artifacts": "steps/step8_e021_rg_measure_robustness_artifacts/run_step8.py",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        content_rows,
        ["output", "classification", "grade", "scope", "source_artifacts"],
    )

    nonclaim = """# Step 8 Nonclaim Boundary

Step 8 is a finite RG/measure/moduli toy. It is not a real RG, landscape, or vacuum-selection computation.

On this toy, Lambda stays non-descending from the bare UV. When the selected modulus is included in Sigma, Lambda descends and the non-descendingness relocates to the selection.

This specifies the structural shape only. It supplies no Lambda value, no physical selection mechanism, no new physics, and no frame-transfer certificate. Real RG/landscape carriers remain open.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")


if __name__ == "__main__":
    main()
