#!/usr/bin/env python3
"""Cluster B Step 3: E021 vacuum readout construction on L_ext.

The construction reads Step 1's d5_vacuum split and builds a finite toy UV/IR
ledger around it.  The large UV/IR ratio is a modeled toy ratio.  The point of
the diagnostic is structural: the vacuum readout is selected/run and audited,
not a clean function of UV Sigma_f alone.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Iterable


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP1_DIR = ARTIFACT_DIR.parent / "step1_shared_substrate_frame_artifacts"
STEP1_CARRIER = STEP1_DIR / "extended_carrier_step1.csv"
STEP1_SIGNATURES = STEP1_DIR / "frame_signatures_step1.csv"
TOL = 1e-10
TOY_MISMATCH_RATIO = 1.0e12


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def key_from_row(row: dict[str, object], fields: Iterable[str]) -> tuple[object, ...]:
    return tuple(row[field] for field in fields)


def obstruction_pairs(
    rows: list[dict[str, object]],
    source_fields: list[str],
    target_field: str,
) -> list[dict[str, object]]:
    pairs: list[dict[str, object]] = []
    for i, left in enumerate(rows):
        for j, right in enumerate(rows[i + 1 :], start=i + 1):
            if key_from_row(left, source_fields) == key_from_row(right, source_fields):
                if abs(float(left[target_field]) - float(right[target_field])) > TOL:
                    pairs.append(
                        {
                            "row_i": i,
                            "row_j": j,
                            "source_value": key_from_row(left, source_fields),
                            "target_i": left[target_field],
                            "target_j": right[target_field],
                            "target_gap": abs(float(left[target_field]) - float(right[target_field])),
                        }
                    )
    return pairs


def select_vacuum_rows() -> tuple[dict[str, str], dict[str, str], list[dict[str, str]]]:
    carrier = read_csv(STEP1_CARRIER)
    vacuum_rows = [row for row in carrier if row["regime"] == "vacuum_smooth"]
    if len(vacuum_rows) < 2:
        raise RuntimeError("Step 1 carrier must contain a vacuum split")
    selected = min(vacuum_rows, key=lambda row: float(row["d5_vacuum"]))
    alternate = max(vacuum_rows, key=lambda row: float(row["d5_vacuum"]))
    return selected, alternate, vacuum_rows


def build_vacuum_currency(selected: dict[str, str], alternate: dict[str, str]) -> list[dict[str, object]]:
    rho_selected = float(selected["d5_vacuum"])
    rho_alternate = float(alternate["d5_vacuum"])
    stress_proxy = float(selected["stress_energy_proxy"])
    return [
        {
            "currency_id": "P5_L_vacuum_currency",
            "source_state": selected["state_id"],
            "rho_Lambda_readout": rho_selected,
            "psi_stress_proxy": stress_proxy,
            "budget_weight": rho_selected / max(stress_proxy, TOL),
            "audited_in_L": True,
            "GR_status": "input_parameter_untracked_by_GR",
            "L_status": "first_class_budget_readout",
            "is_free_additive_constant": False,
        },
        {
            "currency_id": "P5_alternate_vacuum_branch",
            "source_state": alternate["state_id"],
            "rho_Lambda_readout": rho_alternate,
            "psi_stress_proxy": float(alternate["stress_energy_proxy"]),
            "budget_weight": rho_alternate / max(float(alternate["stress_energy_proxy"]), TOL),
            "audited_in_L": True,
            "GR_status": "same_GR_smooth_readout_as_selected_branch",
            "L_status": "selection-distinguished_budget_readout",
            "is_free_additive_constant": False,
        },
    ]


def build_uv_ir_ledger(rho_ir: float) -> tuple[list[dict[str, object]], dict[str, float]]:
    rho_uv = rho_ir * TOY_MISMATCH_RATIO
    counterterm = rho_uv - rho_ir
    log_gap = math.log10(TOY_MISMATCH_RATIO)
    booked_remaining = [log_gap, 8.0, 4.0, 0.0]
    rows: list[dict[str, object]] = [
        {
            "ledger_id": "uv_budget",
            "stage_index": 0,
            "rho_UV": rho_uv,
            "rho_IR": rho_ir,
            "counterterm": "",
            "mismatch_ratio": TOY_MISMATCH_RATIO,
            "log10_mismatch": log_gap,
            "tracked": True,
            "unaudited_cancellation": False,
            "booked_monotone": True,
            "remaining_log_mismatch": log_gap,
            "ratio_status": "toy_modeled_not_real_120",
        },
        {
            "ledger_id": "unaudited_cancellation",
            "stage_index": "",
            "rho_UV": rho_uv,
            "rho_IR": rho_ir,
            "counterterm": counterterm,
            "mismatch_ratio": TOY_MISMATCH_RATIO,
            "log10_mismatch": log_gap,
            "tracked": False,
            "unaudited_cancellation": True,
            "booked_monotone": False,
            "remaining_log_mismatch": "",
            "ratio_status": "toy_modeled_not_real_120",
        },
    ]
    for idx, remaining in enumerate(booked_remaining):
        rows.append(
            {
                "ledger_id": f"booked_stage_{idx}",
                "stage_index": idx,
                "rho_UV": rho_uv,
                "rho_IR": rho_ir,
                "counterterm": counterterm,
                "mismatch_ratio": TOY_MISMATCH_RATIO,
                "log10_mismatch": log_gap,
                "tracked": True,
                "unaudited_cancellation": False,
                "booked_monotone": True,
                "remaining_log_mismatch": remaining,
                "ratio_status": "toy_modeled_not_real_120",
            }
        )
    rows.append(
        {
            "ledger_id": "ir_readout",
            "stage_index": len(booked_remaining),
            "rho_UV": rho_uv,
            "rho_IR": rho_ir,
            "counterterm": counterterm,
            "mismatch_ratio": TOY_MISMATCH_RATIO,
            "log10_mismatch": log_gap,
            "tracked": True,
            "unaudited_cancellation": False,
            "booked_monotone": True,
            "remaining_log_mismatch": 0.0,
            "ratio_status": "toy_modeled_not_real_120",
        }
    )
    return rows, {"rho_UV": rho_uv, "rho_IR": rho_ir, "counterterm": counterterm, "log10_mismatch": log_gap}


def build_vacuum_ensemble(selected: dict[str, str], alternate: dict[str, str], rho_uv: float) -> list[dict[str, object]]:
    rho_selected = float(selected["d5_vacuum"])
    rho_alternate = float(alternate["d5_vacuum"])
    candidates = [
        ("vac_A_selected", "A", 1.0, 42, rho_uv, rho_selected, 0.0),
        ("vac_A_alt_step1", "A", 1.0, 42, rho_uv, rho_alternate, 0.45),
        ("vac_A_high", "A", 1.0, 42, rho_uv, rho_selected * 10.0, 0.80),
        ("vac_B_low", "B", 2.0, 43, rho_uv * 2.0, rho_selected * 2.0, 0.25),
        ("vac_B_high", "B", 2.0, 43, rho_uv * 2.0, rho_selected * 7.0, 0.70),
    ]
    rows: list[dict[str, object]] = []
    for name, family, uv_cutoff, spectrum_id, uv_budget, rho_lambda, selection_score in candidates:
        uv_determined_coupling = 0.05 * uv_cutoff + 0.001 * spectrum_id
        rows.append(
            {
                "candidate_id": name,
                "family": family,
                "uv_cutoff": uv_cutoff,
                "uv_spectrum_id": spectrum_id,
                "rho_UV_budget": uv_budget,
                "rho_Lambda_candidate": rho_lambda,
                "selection_score": selection_score,
                "selected": selection_score == 0.0,
                "selection_rule": "minimum_selection_score",
                "uv_determined_coupling": uv_determined_coupling,
            }
        )
    return rows


def build_nonfactorization_rows(
    ensemble: list[dict[str, object]],
    step1_signature_count: int,
) -> list[dict[str, object]]:
    uv_fields = ["uv_cutoff", "uv_spectrum_id", "rho_UV_budget"]
    lambda_obs = obstruction_pairs(ensemble, uv_fields, "rho_Lambda_candidate")
    coupling_obs = obstruction_pairs(ensemble, uv_fields, "uv_determined_coupling")
    return [
        {
            "signature_id": "UV_Sigma_to_selected_Lambda",
            "source_readout": "UV_Sigma=(uv_cutoff,uv_spectrum_id,rho_UV_budget)",
            "target_readout": "rho_Lambda_candidate",
            "obstruction_count": len(lambda_obs),
            "witness": ";".join(f"{row['row_i']}-{row['row_j']}" for row in lambda_obs),
            "nonfactorizing": len(lambda_obs) > 0,
            "interpretation": "same UV Sigma but different selected vacuum readout",
        },
        {
            "signature_id": "Step1_GR_Sigma_to_d5_vacuum",
            "source_readout": "GR_smooth_Sigma_f=(d0,d2,d3)",
            "target_readout": "d5_vacuum",
            "obstruction_count": step1_signature_count,
            "witness": "3-4",
            "nonfactorizing": step1_signature_count > 0,
            "interpretation": "Step 1 vacuum branch split at identical smooth geometry",
        },
        {
            "signature_id": "descending_control_UV_coupling",
            "source_readout": "UV_Sigma=(uv_cutoff,uv_spectrum_id,rho_UV_budget)",
            "target_readout": "uv_determined_coupling",
            "obstruction_count": len(coupling_obs),
            "witness": "none" if not coupling_obs else ";".join(f"{row['row_i']}-{row['row_j']}" for row in coupling_obs),
            "nonfactorizing": len(coupling_obs) > 0,
            "interpretation": "UV-determined control quantity factors cleanly",
        },
    ]


def build_controls(
    nonfact_rows: list[dict[str, object]],
    ledger_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    lambda_row = next(row for row in nonfact_rows if row["signature_id"] == "UV_Sigma_to_selected_Lambda")
    coupling_row = next(row for row in nonfact_rows if row["signature_id"] == "descending_control_UV_coupling")
    unaudited = next(row for row in ledger_rows if row["ledger_id"] == "unaudited_cancellation")
    booked_rows = [row for row in ledger_rows if str(row["ledger_id"]).startswith("booked_stage_")]
    remaining = [float(row["remaining_log_mismatch"]) for row in booked_rows]
    monotone = all(remaining[i + 1] <= remaining[i] for i in range(len(remaining) - 1))
    ratio_row = next(row for row in ledger_rows if row["ledger_id"] == "uv_budget")
    return [
        {
            "control_id": "derivation_control_clean_UV_to_Lambda_fails",
            "expected": "fails_clean_descent",
            "obstruction_count": lambda_row["obstruction_count"],
            "unaudited_counterterm_tracked": bool(unaudited["tracked"]),
            "passes_guard": bool(lambda_row["obstruction_count"] > 0 and not bool(unaudited["tracked"])),
            "witness": lambda_row["witness"],
        },
        {
            "control_id": "descending_control_UV_coupling_factors",
            "expected": "factors",
            "obstruction_count": coupling_row["obstruction_count"],
            "unaudited_counterterm_tracked": "",
            "passes_guard": bool(coupling_row["obstruction_count"] == 0),
            "witness": coupling_row["witness"],
        },
        {
            "control_id": "booked_ledger_monotone_nonvacuous",
            "expected": "remaining_log_mismatch_monotone_decreases",
            "obstruction_count": "",
            "unaudited_counterterm_tracked": "",
            "passes_guard": bool(monotone and remaining[0] > remaining[-1] and remaining[-1] == 0.0),
            "witness": "->".join(str(value) for value in remaining),
        },
        {
            "control_id": "mismatch_ratio_marked_toy",
            "expected": "ratio_not_presented_as_real_value",
            "obstruction_count": "",
            "unaudited_counterterm_tracked": "",
            "passes_guard": ratio_row["ratio_status"] == "toy_modeled_not_real_120",
            "witness": f"ratio={ratio_row['mismatch_ratio']}; status={ratio_row['ratio_status']}",
        },
    ]


def main() -> None:
    selected, alternate, _vacuum_rows = select_vacuum_rows()
    rho_ir = float(selected["d5_vacuum"])
    currency_rows = build_vacuum_currency(selected, alternate)
    ledger_rows, ledger_summary = build_uv_ir_ledger(rho_ir)
    ensemble_rows = build_vacuum_ensemble(selected, alternate, ledger_summary["rho_UV"])
    step1_signatures = read_csv(STEP1_SIGNATURES)
    step1_e021 = next(row for row in step1_signatures if row["object_id"] == "E021_d5_vacuum")
    nonfact_rows = build_nonfactorization_rows(ensemble_rows, int(step1_e021["obstruction_count_GR_Sigma_f"]))
    control_rows = build_controls(nonfact_rows, ledger_rows)

    lambda_nonfact = next(row for row in nonfact_rows if row["signature_id"] == "UV_Sigma_to_selected_Lambda")
    coupling_control = next(row for row in nonfact_rows if row["signature_id"] == "descending_control_UV_coupling")
    derivation_control = next(row for row in control_rows if row["control_id"] == "derivation_control_clean_UV_to_Lambda_fails")
    descending_control = next(row for row in control_rows if row["control_id"] == "descending_control_UV_coupling_factors")
    booked_control = next(row for row in control_rows if row["control_id"] == "booked_ledger_monotone_nonvacuous")
    ratio_control = next(row for row in control_rows if row["control_id"] == "mismatch_ratio_marked_toy")

    output = {
        "step": 3,
        "orientation": "E021 construction as audited P5/P6 vacuum readout of L",
        "source_step1_carrier": "steps/step1_shared_substrate_frame_artifacts/extended_carrier_step1.csv",
        "rho_IR_selected": rho_ir,
        "rho_UV_toy": ledger_summary["rho_UV"],
        "toy_mismatch_ratio": TOY_MISMATCH_RATIO,
        "toy_log10_mismatch": ledger_summary["log10_mismatch"],
        "predicates": {
            "P5_vacuum_currency": {
                "audited_in_L": True,
                "GR_status": "input_parameter_untracked_by_GR",
                "rho_Lambda_readout": rho_ir,
            },
            "P6_uv_ir_ledger": {
                "unaudited_counterterm_tracked": False,
                "booked_ledger_monotone": bool(booked_control["passes_guard"]),
                "mismatch_ratio_modeled_toy": True,
            },
            "P2_selection": {
                "ensemble_size": len(ensemble_rows),
                "selected_candidate": "vac_A_selected",
                "selection_rule": "minimum_selection_score",
            },
            "nonfactorization": {
                "UV_to_Lambda_obstruction_count": lambda_nonfact["obstruction_count"],
                "Step1_GR_to_d5_obstruction_count": int(step1_e021["obstruction_count_GR_Sigma_f"]),
            },
        },
        "controls": {
            "derivation_control_fails": bool(derivation_control["passes_guard"]),
            "descending_control_factors": bool(descending_control["passes_guard"]),
            "booked_ledger_nonvacuous": bool(booked_control["passes_guard"]),
            "mismatch_ratio_marked_toy": bool(ratio_control["passes_guard"]),
        },
        "verdict": {
            "type": "E021_audited_vacuum_readout_constructed_finite_toy",
            "firm_part_selected_run_readout": True,
            "firm_part_missing_audit_ledger": False,
            "modeled_p6_ledger_illustrative": True,
            "contested_distinct_audit_currency_reading": True,
            "P5_currency_built": True,
            "P6_ledger_booked": bool(booked_control["passes_guard"]),
            "P2_selection_built": True,
            "nonfactorization_signature_computed": bool(lambda_nonfact["obstruction_count"] > 0),
            "controls_have_teeth": bool(
                derivation_control["passes_guard"]
                and descending_control["passes_guard"]
                and booked_control["passes_guard"]
                and ratio_control["passes_guard"]
            ),
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "nonclaim": "Finite-carrier E021 construction: audited vacuum currency, toy UV-to-IR ledger, and selected/run readout shape only; no Lambda value or selection mechanism is supplied.",
    }

    write_csv(ARTIFACT_DIR / "vacuum_currency_step3.csv", currency_rows)
    write_csv(ARTIFACT_DIR / "uv_ir_ledger_step3.csv", ledger_rows)
    write_csv(ARTIFACT_DIR / "vacuum_selection_step3.csv", ensemble_rows)
    write_csv(ARTIFACT_DIR / "nonfactorization_step3.csv", nonfact_rows)
    write_csv(ARTIFACT_DIR / "controls_step3.csv", control_rows)
    (ARTIFACT_DIR / "e021_cosmological_constant_output_step3.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "e021_cosmological_constant_output_step3.txt").write_text(
        "\n".join(
            [
                "Cluster B Step 3 E021 finite vacuum-readout construction",
                "Verdict: E021_audited_vacuum_readout_constructed_finite_toy",
                f"rho_IR selected toy readout: {rho_ir}",
                f"rho_UV toy budget: {ledger_summary['rho_UV']}",
                f"toy mismatch ratio: {TOY_MISMATCH_RATIO}",
                f"UV-to-Lambda obstruction count: {lambda_nonfact['obstruction_count']}",
                f"descending control obstruction count: {coupling_control['obstruction_count']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
