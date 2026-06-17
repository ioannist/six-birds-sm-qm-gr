#!/usr/bin/env python3
"""Cluster A Step 20: GUT recognition value-relations and one-loop tests."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent

MZ_GEV = 91.1876
ALPHA_EM_INV_MZ = 127.955
SIN2_MZ_MEASURED = 0.23122
ALPHA_S_MZ = 0.1184
SM_BETA = {"alpha1": 41 / 10, "alpha2": -19 / 6, "alpha3": -7}
SUSY_BETA = {"alpha1": 33 / 5, "alpha2": 1, "alpha3": -3}
COUPLING_KEYS = ["alpha1", "alpha2", "alpha3"]


def write_csv(name: str, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0]) if rows else []
    with (ARTIFACT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def low_energy_couplings() -> dict[str, float]:
    alpha_em = 1 / ALPHA_EM_INV_MZ
    cos2 = 1 - SIN2_MZ_MEASURED
    alpha_y = alpha_em / cos2
    alpha1 = (5 / 3) * alpha_y
    alpha2 = alpha_em / SIN2_MZ_MEASURED
    return {"alpha1": alpha1, "alpha2": alpha2, "alpha3": ALPHA_S_MZ}


def inverse_running(alpha_inv_mz: float, beta: float, log_mu_over_mz: float) -> float:
    return alpha_inv_mz - beta * log_mu_over_mz / (2 * math.pi)


def pair_crossing(alpha_inv: dict[str, float], beta: dict[str, float], left: str, right: str) -> dict[str, object]:
    log_mu = 2 * math.pi * (alpha_inv[left] - alpha_inv[right]) / (beta[left] - beta[right])
    scale = MZ_GEV * math.exp(log_mu)
    return {
        "pair": f"{left}-{right}",
        "log_mu_over_mz": f"{log_mu:.12f}",
        "scale_GeV": f"{scale:.12e}",
        "log10_scale_GeV": f"{math.log10(scale):.12f}",
    }


def least_squares_fit(alpha_inv: dict[str, float], beta: dict[str, float]) -> dict[str, object]:
    # Fit alpha_i^{-1}(MZ) = alpha_G^{-1} + b_i * L / (2*pi).
    xs = [beta[key] / (2 * math.pi) for key in COUPLING_KEYS]
    ys = [alpha_inv[key] for key in COUPLING_KEYS]
    n = len(xs)
    sx = sum(xs)
    sy = sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    log_mgut_over_mz = (n * sxy - sx * sy) / denom
    alpha_g_inv = (sy - log_mgut_over_mz * sx) / n
    pred_low = {
        key: alpha_g_inv + beta[key] * log_mgut_over_mz / (2 * math.pi)
        for key in COUPLING_KEYS
    }
    high_inverses = {
        key: alpha_inv[key] - beta[key] * log_mgut_over_mz / (2 * math.pi)
        for key in COUPLING_KEYS
    }
    spread = max(high_inverses.values()) - min(high_inverses.values())
    scale = MZ_GEV * math.exp(log_mgut_over_mz)
    alpha1_pred = 1 / pred_low["alpha1"]
    alpha2_pred = 1 / pred_low["alpha2"]
    alpha_y_pred = (3 / 5) * alpha1_pred
    sin2_pred = alpha_y_pred / (alpha2_pred + alpha_y_pred)
    return {
        "alpha_g_inv": alpha_g_inv,
        "log_mgut_over_mz": log_mgut_over_mz,
        "mgut_GeV": scale,
        "log10_mgut_GeV": math.log10(scale),
        "high_inverses": high_inverses,
        "spread_inverse_coupling": spread,
        "relative_spread": spread / (sum(high_inverses.values()) / len(high_inverses)),
        "pred_low_inverse": pred_low,
        "sin2_mz_pred": sin2_pred,
    }


def trace_rows() -> tuple[list[dict[str, object]], dict[str, float]]:
    multiplets = [
        {"multiplet": "Q", "states": 6, "hypercharge": 1 / 6, "doublet_copies": 3},
        {"multiplet": "u_c", "states": 3, "hypercharge": -2 / 3, "doublet_copies": 0},
        {"multiplet": "d_c", "states": 3, "hypercharge": 1 / 3, "doublet_copies": 0},
        {"multiplet": "L", "states": 2, "hypercharge": -1 / 2, "doublet_copies": 1},
        {"multiplet": "e_c", "states": 1, "hypercharge": 1.0, "doublet_copies": 0},
    ]
    rows: list[dict[str, object]] = []
    total_y2 = 0.0
    total_t3_2 = 0.0
    for row in multiplets:
        y2 = row["states"] * row["hypercharge"] ** 2
        t3_2 = row["doublet_copies"] * 0.5
        total_y2 += y2
        total_t3_2 += t3_2
        rows.append(
            {
                "multiplet": row["multiplet"],
                "state_count": row["states"],
                "hypercharge": f"{row['hypercharge']:.12f}",
                "Tr_Y2_contribution": f"{y2:.12f}",
                "Tr_T3_2_contribution": f"{t3_2:.12f}",
            }
        )
    normalization = total_y2 / total_t3_2
    g_y_over_g2_sq = 1 / normalization
    sin2 = g_y_over_g2_sq / (1 + g_y_over_g2_sq)
    totals = {
        "Tr_Y2": total_y2,
        "Tr_T3_2": total_t3_2,
        "hypercharge_normalization": normalization,
        "gY2_over_g2_2": g_y_over_g2_sq,
        "sin2_gut": sin2,
    }
    rows.append(
        {
            "multiplet": "total",
            "state_count": "",
            "hypercharge": "",
            "Tr_Y2_contribution": f"{total_y2:.12f}",
            "Tr_T3_2_contribution": f"{total_t3_2:.12f}",
        }
    )
    return rows, totals


def sampled_running(alpha_inv: dict[str, float], beta: dict[str, float], label: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for log10_scale in [3, 6, 9, 12, 13, 14, 15, 16, 17, 18]:
        scale = 10**log10_scale
        log_mu = math.log(scale / MZ_GEV)
        rows.append(
            {
                "model": label,
                "log10_scale_GeV": log10_scale,
                "alpha1_inv": f"{inverse_running(alpha_inv['alpha1'], beta['alpha1'], log_mu):.12f}",
                "alpha2_inv": f"{inverse_running(alpha_inv['alpha2'], beta['alpha2'], log_mu):.12f}",
                "alpha3_inv": f"{inverse_running(alpha_inv['alpha3'], beta['alpha3'], log_mu):.12f}",
            }
        )
    return rows


def main() -> None:
    trace, trace_totals = trace_rows()
    write_csv(
        "gut_trace_step20.csv",
        trace,
        ["multiplet", "state_count", "hypercharge", "Tr_Y2_contribution", "Tr_T3_2_contribution"],
    )

    alpha = low_energy_couplings()
    alpha_inv = {key: 1 / value for key, value in alpha.items()}
    sm_pair_rows = [pair_crossing(alpha_inv, SM_BETA, left, right) for left, right in [("alpha1", "alpha2"), ("alpha1", "alpha3"), ("alpha2", "alpha3")]]
    sm_fit = least_squares_fit(alpha_inv, SM_BETA)
    susy_pair_rows = [pair_crossing(alpha_inv, SUSY_BETA, left, right) for left, right in [("alpha1", "alpha2"), ("alpha1", "alpha3"), ("alpha2", "alpha3")]]
    susy_fit = least_squares_fit(alpha_inv, SUSY_BETA)

    write_csv("rg_running_step20.csv", sampled_running(alpha_inv, SM_BETA, "SM_one_loop") + sampled_running(alpha_inv, SUSY_BETA, "SUSY_one_loop_comparison"))

    pair_log10 = [float(row["log10_scale_GeV"]) for row in sm_pair_rows]
    pair_spread_decades = max(pair_log10) - min(pair_log10)
    clean_unification = sm_fit["spread_inverse_coupling"] < 0.5 and pair_spread_decades < 0.5
    unification_rows = []
    for row in sm_pair_rows:
        entry = {"test": "pair_crossing", **row}
        unification_rows.append(entry)
    unification_rows.append(
        {
            "test": "least_squares_best_fit",
            "pair": "all_three",
            "log_mu_over_mz": f"{sm_fit['log_mgut_over_mz']:.12f}",
            "scale_GeV": f"{sm_fit['mgut_GeV']:.12e}",
            "log10_scale_GeV": f"{sm_fit['log10_mgut_GeV']:.12f}",
            "spread_inverse_coupling": f"{sm_fit['spread_inverse_coupling']:.12f}",
            "relative_spread": f"{sm_fit['relative_spread']:.12f}",
            "clean_unification": clean_unification,
        }
    )
    write_csv(
        "unification_test_step20.csv",
        unification_rows,
        ["test", "pair", "log_mu_over_mz", "scale_GeV", "log10_scale_GeV", "spread_inverse_coupling", "relative_spread", "clean_unification"],
    )

    susy_spread_decades = max(float(row["log10_scale_GeV"]) for row in susy_pair_rows) - min(float(row["log10_scale_GeV"]) for row in susy_pair_rows)
    susy_rows = []
    for row in susy_pair_rows:
        susy_rows.append({"test": "pair_crossing", **row})
    susy_rows.append(
        {
            "test": "least_squares_best_fit",
            "pair": "all_three",
            "log_mu_over_mz": f"{susy_fit['log_mgut_over_mz']:.12f}",
            "scale_GeV": f"{susy_fit['mgut_GeV']:.12e}",
            "log10_scale_GeV": f"{susy_fit['log10_mgut_GeV']:.12f}",
            "spread_inverse_coupling": f"{susy_fit['spread_inverse_coupling']:.12f}",
            "pair_scale_spread_decades": f"{susy_spread_decades:.12f}",
        }
    )
    write_csv("susy_comparison_step20.csv", susy_rows, ["test", "pair", "log_mu_over_mz", "scale_GeV", "log10_scale_GeV", "spread_inverse_coupling", "pair_scale_spread_decades"])

    sin2_diff = sm_fit["sin2_mz_pred"] - SIN2_MZ_MEASURED
    value_rows = [
        {
            "relation": "sin2_thetaW_GUT",
            "value": f"{trace_totals['sin2_gut']:.12f}",
            "derivation": "TrY2/TrT3sq=5/3 so gY^2/g2^2=3/5 and sin2=3/8",
            "status": "recognition_relation",
        },
        {
            "relation": "gauge_coupling_unification_condition",
            "value": "g1=g2=g3 with g1=sqrt(5/3) gY",
            "derivation": "single simple-group gauge coupling under SU5 recognition",
            "status": "recognition_relation_tested_by_rg",
        },
        {
            "relation": "bottom_tau_relation",
            "value": "m_b=m_tau at M_GUT in minimal SU5",
            "derivation": "down-quark and charged-lepton Yukawa terms share the 5bar matter placement in the minimal recognition",
            "status": "recognition_relation",
        },
        {
            "relation": "sin2_thetaW_MZ_from_best_fit_SM_running",
            "value": f"{sm_fit['sin2_mz_pred']:.12f}",
            "derivation": "one-loop SM running from best-fit high-scale unification condition",
            "status": "near_miss_discrepancy",
        },
    ]
    write_csv("value_relations_step20.csv", value_rows, ["relation", "value", "derivation", "status"])

    sin2_rows = [
        {
            "prediction_source": "SM_one_loop_best_fit_high_scale",
            "sin2_thetaW_MZ_pred": f"{sm_fit['sin2_mz_pred']:.12f}",
            "sin2_thetaW_MZ_measured": f"{SIN2_MZ_MEASURED:.12f}",
            "difference": f"{sin2_diff:.12f}",
            "absolute_difference": f"{abs(sin2_diff):.12f}",
        }
    ]
    write_csv("sin2_running_comparison_step20.csv", sin2_rows, ["prediction_source", "sin2_thetaW_MZ_pred", "sin2_thetaW_MZ_measured", "difference", "absolute_difference"])

    schema = {
        "step": 20,
        "artifact_dir": "steps/step20_gut_recognition_value_relations_artifacts",
        "route": "Mode A / E2 recognition import",
        "imported_principle": "SU5 embedding of 10 plus 5bar matter; SO10 16 optional recognition envelope",
        "trace_relation": trace_totals,
        "inputs_at_MZ": {
            "MZ_GeV": MZ_GEV,
            "alpha_em_inverse": ALPHA_EM_INV_MZ,
            "sin2_thetaW_measured": SIN2_MZ_MEASURED,
            "alpha_s": ALPHA_S_MZ,
        },
        "sm_one_loop_unification": {
            "pair_crossing_log10_scales": pair_log10,
            "pair_scale_spread_decades": pair_spread_decades,
            "best_fit_log10_scale_GeV": sm_fit["log10_mgut_GeV"],
            "spread_inverse_coupling": sm_fit["spread_inverse_coupling"],
            "relative_spread": sm_fit["relative_spread"],
            "clean_unification": clean_unification,
            "sin2_mz_pred": sm_fit["sin2_mz_pred"],
            "sin2_mz_measured": SIN2_MZ_MEASURED,
            "sin2_difference": sin2_diff,
        },
        "susy_one_loop_comparison": {
            "best_fit_log10_scale_GeV": susy_fit["log10_mgut_GeV"],
            "spread_inverse_coupling": susy_fit["spread_inverse_coupling"],
            "pair_scale_spread_decades": susy_spread_decades,
        },
        "sbt_value_derivation": False,
        "absolute_values_residual": True,
        "frame_transfer_certified": False,
        "root_landed": False,
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "claim_id": "gut_trace_relation",
            "claim": "The SU5 recognition trace gives hypercharge normalization 5/3 and sin2 theta_W=3/8 at the high scale.",
            "grade": "recognition-import-derived-relation",
            "classification": "ModeA_E2",
            "source_artifacts": "steps/step20_gut_recognition_value_relations_artifacts/gut_trace_step20.csv;steps/step20_gut_recognition_value_relations_artifacts/value_relations_step20.csv",
        },
        {
            "claim_id": "gauge_running_test",
            "claim": "One-loop non-SUSY SM running does not cleanly unify the three couplings.",
            "grade": "finite-carrier-diagnostic",
            "classification": "can-fail-rg-test",
            "source_artifacts": "steps/step20_gut_recognition_value_relations_artifacts/unification_test_step20.csv;steps/step20_gut_recognition_value_relations_artifacts/rg_running_step20.csv",
        },
        {
            "claim_id": "sin2_running_comparison",
            "claim": "Running from the best-fit high scale predicts sin2 theta_W(MZ)=0.214358, differing from 0.23122.",
            "grade": "finite-carrier-diagnostic",
            "classification": "experimental-comparison",
            "source_artifacts": "steps/step20_gut_recognition_value_relations_artifacts/sin2_running_comparison_step20.csv",
        },
        {
            "claim_id": "susy_comparison",
            "claim": "The SUSY one-loop coefficient comparison gives a much tighter meeting than the non-SUSY SM coefficients.",
            "grade": "organizational",
            "classification": "comparison-note",
            "source_artifacts": "steps/step20_gut_recognition_value_relations_artifacts/susy_comparison_step20.csv",
        },
        {
            "claim_id": "nonclaim_boundary",
            "claim": "Value-relations use recognition import; absolute values remain residual.",
            "grade": "organizational",
            "classification": "scope-boundary",
            "source_artifacts": "steps/step20_gut_recognition_value_relations_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv("content_classification.csv", content_rows, ["claim_id", "claim", "grade", "classification", "source_artifacts"])

    summary = f"""# Step 20 Results Summary: GUT Recognition Value-Relations

## Recognition Import

Mode A / E2 import: SU(5) embedding of the one-generation content into `10 + 5bar` (with SO(10) `16` as the optional recognition envelope). This is an external recognition principle motivated by the closure narrowing, not an SBT-alone value derivation.

## Trace Computation

Over the one-generation multiplet:

- `Tr(Y^2) = {trace_totals['Tr_Y2']:.12f}`.
- `Tr(T_3^2) = {trace_totals['Tr_T3_2']:.12f}`.
- `Tr(Y^2)/Tr(T_3^2) = {trace_totals['hypercharge_normalization']:.12f}`.
- Therefore `g_Y^2/g_2^2 = {trace_totals['gY2_over_g2_2']:.12f}` and `sin^2(theta_W) = {trace_totals['sin2_gut']:.12f} = 3/8` at the recognition scale.

## Value-Relations

- `g1 = g2 = g3` at the recognition scale, with `g1 = sqrt(5/3) gY`.
- Minimal SU(5) bottom-tau relation: `m_b = m_tau` at the recognition scale.

## One-Loop Non-SUSY SM Running

Inputs at `M_Z={MZ_GEV}` GeV: `alpha_em^-1={ALPHA_EM_INV_MZ}`, `sin^2(theta_W)={SIN2_MZ_MEASURED}`, `alpha_s={ALPHA_S_MZ}`.

Pair crossing log10 scales:

- alpha1-alpha2: `{pair_log10[0]:.12f}`.
- alpha1-alpha3: `{pair_log10[1]:.12f}`.
- alpha2-alpha3: `{pair_log10[2]:.12f}`.

Best-fit common scale: `log10(M/Gev)={sm_fit['log10_mgut_GeV']:.12f}`. High-scale inverse-coupling spread: `{sm_fit['spread_inverse_coupling']:.12f}`.

Verdict: minimal non-SUSY SU(5) does not cleanly unify at one loop; it is a near-miss, not a pass.

## Sin-Squared Comparison

Running the recognition condition down with the best-fit one-loop SM scale gives `sin^2(theta_W)(M_Z)={sm_fit['sin2_mz_pred']:.12f}` versus measured `{SIN2_MZ_MEASURED:.12f}`, difference `{sin2_diff:.12f}`.

## SUSY Comparison Note

Using SUSY one-loop beta coefficients gives best-fit `log10(M/Gev)={susy_fit['log10_mgut_GeV']:.12f}` and inverse-coupling spread `{susy_fit['spread_inverse_coupling']:.12f}`, much tighter than the non-SUSY SM coefficient result. This is a comparison note, not an added model claim.

## Grade

Value-relations via E2 recognition import. Absolute values remain residual; this recovers known GUT physics and reports the non-SUSY unification failure honestly.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 20 Nonclaim Boundary

This step uses a Mode A / E2 recognition import: SU(5) embedding. The value-relations are recognition-import relations, not SBT-alone value derivations.

The step does not supply the gauge group, generation count, orientation among the remaining content supports, absolute coupling values, the electroweak scale, Yukawa values, or frame transfer.

The one-loop non-SUSY SM unification test is a real can-fail computation and it fails clean unification. This is known GUT physics recovered as a calibrated recognition test, not new physics.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\section{{Step 20: GUT Recognition Value-Relations}}

\paragraph{{Recognition Import.}}
The imported Mode-A/E2 principle is the \(SU(5)\) embedding \(10+\bar{{5}}\). This is a recognition import, not an SBT-alone value derivation.

\paragraph{{Trace Relation.}}
The trace computation gives \(\mathrm{{Tr}}(Y^2)={trace_totals['Tr_Y2']:.12f}\) and \(\mathrm{{Tr}}(T_3^2)={trace_totals['Tr_T3_2']:.12f}\), hence \(k_Y=5/3\) and \(\sin^2\theta_W=3/8\) at the recognition scale.

\paragraph{{RG Test.}}
One-loop non-SUSY SM running gives pair crossing log-scales {pair_log10[0]:.6f}, {pair_log10[1]:.6f}, and {pair_log10[2]:.6f}. The best-fit inverse-coupling spread is {sm_fit['spread_inverse_coupling']:.6f}, so minimal non-SUSY \(SU(5)\) is a near-miss rather than clean unification.

\paragraph{{Comparison.}}
The best-fit SM-running prediction is \(\sin^2\theta_W(M_Z)={sm_fit['sin2_mz_pred']:.6f}\), compared with {SIN2_MZ_MEASURED:.6f}.
"""
    (ARTIFACT_DIR / "step20_statement.tex").write_text(statement, encoding="utf-8")

    print(
        "Step 20 built: "
        f"sin2_gut={trace_totals['sin2_gut']:.12f} "
        f"sm_clean_unification={clean_unification} "
        f"sm_spread={sm_fit['spread_inverse_coupling']:.12f} "
        f"sin2_mz_pred={sm_fit['sin2_mz_pred']:.12f}"
    )


if __name__ == "__main__":
    main()
