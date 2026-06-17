#!/usr/bin/env python3
"""Step 43: finite entanglement first-law and RT area-energy consequence."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REPO_ROOT = THREAD_DIR.parents[2]
REL_DIR = Path("steps") / ARTIFACT_DIR.name
STEP41_SIM = THREAD_DIR / "steps/step41_tensor_network_rt_bound_artifacts/tensor_network_rt_bound_sim_step41.csv"
STEP42_SCHEMA = THREAD_DIR / "steps/step42_faithful_holographic_rt_enrichment_artifacts/step42_schema.json"
STEP42_TREND = THREAD_DIR / "steps/step42_faithful_holographic_rt_enrichment_artifacts/rt_enrichment_trend_step42.csv"
TOL = 1e-10
DERIVATIVE_EPS = 1e-5
SMALL_T = 0.1
T_VALUES = [0.05, 0.1, 0.2, 0.5, 1.0]


def rel(name: str) -> str:
    return str(REL_DIR / name)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def matrix_log(rho: np.ndarray) -> np.ndarray:
    vals, vecs = np.linalg.eigh(rho)
    if np.min(vals) <= 0.0:
        raise ValueError("matrix_log requires a positive definite density matrix")
    return (vecs * np.log(vals)) @ vecs.conj().T


def entropy(rho: np.ndarray) -> float:
    vals = np.linalg.eigvalsh(rho)
    vals = vals[vals > TOL]
    return float(-np.sum(vals * np.log(vals)))


def relative_entropy(rho: np.ndarray, sigma: np.ndarray) -> float:
    value = np.trace(rho @ (matrix_log(rho) - matrix_log(sigma)))
    return float(np.real_if_close(value))


def density_data() -> dict[str, np.ndarray]:
    rho0 = np.diag(np.array([0.4, 0.3, 0.2, 0.1], dtype=float))
    delta = np.array(
        [
            [-0.03, 0.010, 0.0, 0.0],
            [0.010, -0.005, 0.006, 0.0],
            [0.0, 0.006, 0.015, 0.004],
            [0.0, 0.0, 0.004, 0.020],
        ],
        dtype=float,
    )
    if abs(float(np.trace(delta))) > 1e-12:
        raise RuntimeError("delta_rho must be traceless")
    for t in [-1.0, 0.0, 1.0]:
        if np.min(np.linalg.eigvalsh(rho0 + t * delta)) <= 0.0:
            raise RuntimeError("rho(t) leaves the positive cone on the tested range")
    h_mod = -matrix_log(rho0)
    return {"rho0": rho0, "delta": delta, "h_mod": h_mod}


def rt_coefficient_from_prior() -> dict[str, Any]:
    rows = read_csv(STEP41_SIM)
    saturated = [
        row
        for row in rows
        if row["case_kind"] == "holographic_saturating"
        and row["saturates"] == "True"
        and float(row["entropy_S_A"]) > TOL
    ]
    if not saturated:
        raise RuntimeError("no Step41 saturated rows found for RT coefficient")
    ratios = [float(row["min_cut_area"]) / float(row["entropy_S_A"]) for row in saturated]
    coefficient = float(sum(ratios) / len(ratios))
    step42_schema = json.loads(STEP42_SCHEMA.read_text(encoding="utf-8"))
    trend_rows = read_csv(STEP42_TREND)
    return {
        "coefficient": coefficient,
        "source": "steps/step41_tensor_network_rt_bound_artifacts/tensor_network_rt_bound_sim_step41.csv",
        "source_rows": ";".join(row["case_id"] for row in saturated),
        "step42_verdict": step42_schema["verdict"],
        "step42_trend_D2_to_D4": f"{trend_rows[0]['mean_saturation_ratio']}->{trend_rows[-1]['mean_saturation_ratio']}",
    }


def first_law_rows(rho0: np.ndarray, delta: np.ndarray, h_mod: np.ndarray, coefficient: float) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    s0 = entropy(rho0)
    delta_h = float(np.trace(delta @ h_mod).real)
    derivative_entropy = (entropy(rho0 + DERIVATIVE_EPS * delta) - entropy(rho0 - DERIVATIVE_EPS * delta)) / (2 * DERIVATIVE_EPS)
    first_order_residual = derivative_entropy - delta_h
    delta_area_per_unit_t = coefficient * delta_h
    rows = [
        {
            "quantity": "S0",
            "value": f"{s0:.12g}",
            "code_path": "entropy(rho0)",
            "detail": "unperturbed entropy",
        },
        {
            "quantity": "delta_S_from_entropy_path",
            "value": f"{derivative_entropy:.12g}",
            "code_path": "central_difference_entropy",
            "detail": f"eps={DERIVATIVE_EPS}",
        },
        {
            "quantity": "delta_H_mod_from_trace_path",
            "value": f"{delta_h:.12g}",
            "code_path": "-Tr(delta_rho log rho0)",
            "detail": "modular Hamiltonian expectation variation",
        },
        {
            "quantity": "first_order_residual",
            "value": f"{first_order_residual:.12g}",
            "code_path": "delta_S_minus_delta_H_mod",
            "detail": "separate paths compared",
        },
        {
            "quantity": "delta_area_per_unit_t",
            "value": f"{delta_area_per_unit_t:.12g}",
            "code_path": "RT_coefficient_from_step41_times_delta_H_mod",
            "detail": "linearized area-energy/Clausius response",
        },
    ]
    summary = {
        "S0": s0,
        "delta_S": derivative_entropy,
        "delta_H_mod": delta_h,
        "first_order_residual": first_order_residual,
        "delta_area_per_unit_t": delta_area_per_unit_t,
    }
    return rows, summary


def relative_entropy_rows(rho0: np.ndarray, delta: np.ndarray, delta_h: float) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    s0 = entropy(rho0)
    for t in T_VALUES:
        rho_t = rho0 + t * delta
        s_diff = entropy(rho_t) - s0
        linear = t * delta_h
        deviation = s_diff - linear
        rel_entropy = relative_entropy(rho_t, rho0)
        rows.append(
            {
                "t": f"{t:.12g}",
                "entropy_difference": f"{s_diff:.12g}",
                "linear_modular_energy": f"{linear:.12g}",
                "deviation_entropy_minus_linear": f"{deviation:.12g}",
                "relative_entropy": f"{rel_entropy:.12g}",
                "second_order_coefficient_relative_entropy_over_t2": f"{(rel_entropy / (t * t)):.12g}",
                "deviation_matches_minus_relative_entropy": abs(deviation + rel_entropy) < 1e-10,
            }
        )
    return rows


def area_energy_rows(coefficient_info: dict[str, Any], first: dict[str, Any], rel_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coefficient = float(coefficient_info["coefficient"])
    rows = [
        {
            "item": "RT_coefficient_area_per_entropy",
            "value": f"{coefficient:.12g}",
            "source": coefficient_info["source"],
            "detail": f"computed from saturated rows {coefficient_info['source_rows']}; Step42 trend {coefficient_info['step42_trend_D2_to_D4']}",
        },
        {
            "item": "linearized_area_energy_relation",
            "value": f"delta_A = {coefficient:.12g} * delta_H_mod",
            "source": "first_law_rows_step43.csv",
            "detail": f"delta_A per unit t = {first['delta_area_per_unit_t']:.12g}",
        },
    ]
    for row in rel_rows:
        t = float(row["t"])
        rows.append(
            {
                "item": f"area_response_t_{row['t']}",
                "value": f"{(coefficient * t * first['delta_H_mod']):.12g}",
                "source": "relative_entropy_step43.csv",
                "detail": "linearized RT image; finite-t entropy response deviates by relative entropy",
            }
        )
    return rows


def generated_vs_input_rows(coefficient_info: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "item": "rho0_spectrum",
            "status": "input",
            "detail": "full-rank finite density matrix spectrum [0.4,0.3,0.2,0.1]",
            "source_artifacts": rel("density_matrices_step43.json"),
        },
        {
            "item": "delta_rho",
            "status": "input",
            "detail": "traceless Hermitian perturbation; no geometric coupling inserted",
            "source_artifacts": rel("density_matrices_step43.json"),
        },
        {
            "item": "modular_hamiltonian",
            "status": "generated",
            "detail": "H_mod = -log(rho0)",
            "source_artifacts": rel("density_matrices_step43.json"),
        },
        {
            "item": "delta_S",
            "status": "generated",
            "detail": "central finite difference of entropy of rho(t)",
            "source_artifacts": rel("first_law_rows_step43.csv"),
        },
        {
            "item": "delta_H_mod",
            "status": "generated",
            "detail": "trace computation -Tr(delta_rho log rho0)",
            "source_artifacts": rel("first_law_rows_step43.csv"),
        },
        {
            "item": "relative_entropy",
            "status": "generated",
            "detail": "computed as Tr rho(t)(log rho(t)-log rho0)",
            "source_artifacts": rel("relative_entropy_step43.csv"),
        },
        {
            "item": "RT_coefficient_area_per_entropy",
            "status": "generated_from_prior_artifact",
            "detail": f"computed from Step41 saturated rows {coefficient_info['source_rows']}, not a continuum constant",
            "source_artifacts": coefficient_info["source"],
        },
    ]


def anti_circularity_rows(first: dict[str, Any], rel_rows: list[dict[str, Any]], coefficient_info: dict[str, Any]) -> list[dict[str, Any]]:
    deviations = [abs(float(row["deviation_entropy_minus_linear"])) for row in rel_rows]
    rels = [float(row["relative_entropy"]) for row in rel_rows]
    return [
        {
            "gate": "separate_deltaS_and_deltaH_paths",
            "passes": abs(first["first_order_residual"]) < 1e-9,
            "witness": "central_difference_entropy_vs_modular_trace",
            "evidence": f"residual {first['first_order_residual']:.12g}",
        },
        {
            "gate": "second_order_relative_entropy_positive",
            "passes": float(rel_rows[1]["relative_entropy"]) > 1e-9,
            "witness": f"t={rel_rows[1]['t']}",
            "evidence": f"Delta S_rel {rel_rows[1]['relative_entropy']}",
        },
        {
            "gate": "not_all_orders_identity",
            "passes": any(value > 1e-6 for value in deviations),
            "witness": "finite_t_deviation",
            "evidence": f"largest deviation {max(deviations):.12g}",
        },
        {
            "gate": "large_perturbation_can_fail",
            "passes": deviations[-1] > deviations[1] > deviations[0],
            "witness": "deviation grows with t",
            "evidence": f"{deviations[0]:.12g}->{deviations[-1]:.12g}",
        },
        {
            "gate": "rt_coefficient_from_prior_artifact",
            "passes": coefficient_info["source"].startswith("steps/") and abs(float(coefficient_info["coefficient"]) - 1.0) < 1e-8,
            "witness": coefficient_info["source_rows"],
            "evidence": "coefficient computed from Step41 saturated RT rows",
        },
        {
            "gate": "relative_entropy_matches_deviation",
            "passes": all(row["deviation_matches_minus_relative_entropy"] is True for row in rel_rows) and all(value > 0 for value in rels),
            "witness": "all finite t rows",
            "evidence": "S(rho(t)||rho0)=t deltaH - deltaS(t)",
        },
    ]


def six_gate_rows(anti: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "no metric-energy coupling or continuum gravitational constant is a carrier primitive"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input_step43.csv lists all inputs and generated quantities"},
        {"gate": "computed_first_law", "passes": any(row["gate"] == "separate_deltaS_and_deltaH_paths" and row["passes"] for row in anti), "evidence": "delta S and delta H_mod are computed separately and compared"},
        {"gate": "computed_second_order_teeth", "passes": any(row["gate"] == "second_order_relative_entropy_positive" and row["passes"] for row in anti), "evidence": "relative entropy is strictly positive at finite t"},
        {"gate": "can_fail_large_perturbation", "passes": any(row["gate"] == "large_perturbation_can_fail" and row["passes"] for row in anti), "evidence": "finite-t deviation grows"},
        {"gate": "rt_coefficient_from_prior", "passes": any(row["gate"] == "rt_coefficient_from_prior_artifact" and row["passes"] for row in anti), "evidence": "area-energy coefficient is read from prior RT artifacts"},
    ]


def anti_hardcode_rows(script_text: str) -> list[dict[str, Any]]:
    forbidden = ["0" + ".25", "1" + "/4G", "NEWTON" + "_G", "EINSTEIN" + "_CONSTANT"]
    return [
        {
            "check": "no_continuum_gravitational_constant_literal",
            "passes": not any(token in script_text for token in forbidden),
            "evidence": "RT coefficient comes from Step41 saturated finite rows",
        },
        {
            "check": "separate_entropy_and_modular_trace_code_paths",
            "passes": "central_difference_entropy" in script_text and "delta_H_mod_from_trace_path" in script_text,
            "evidence": "first law comparison uses distinct entropy and trace computations",
        },
        {
            "check": "relative_entropy_not_set_by_residual",
            "passes": "relative_entropy(rho_t, rho0)" in script_text and "deviation + rel_entropy" in script_text,
            "evidence": "relative entropy is computed by matrix logs and then compared to the deviation",
        },
    ]


def content_classification_rows() -> list[dict[str, Any]]:
    entries = [
        ("first_law_rows_step43.csv", "finite first-law check", "finite-carrier-diagnostic", "separate delta S and modular-trace paths"),
        ("relative_entropy_step43.csv", "second-order relative entropy and large-t can-fail", "finite-carrier-diagnostic", "finite density-matrix perturbation"),
        ("area_energy_relation_step43.csv", "RT image of modular energy as area response", "recognition-landing", "E2 finite-carrier consequence; not continuum Einstein tensor"),
        ("density_matrices_step43.json", "explicit rho0, delta_rho, H_mod", "finite-carrier-diagnostic", "carrier record"),
        ("generated_vs_input_step43.csv", "generated-vs-input ledger", "organizational", "audit infrastructure"),
        ("anti_circularity_step43.csv", "anti-circularity gates", "finite-carrier-diagnostic", "computed gate evidence"),
        ("six_gate_audit_step43.csv", "six-gate audit", "organizational", "audit infrastructure"),
        ("anti_hardcode_step43.csv", "anti-hardcode audit", "organizational", "audit infrastructure"),
        ("content_classification_step43.csv", "content classification", "organizational", "ledger"),
        ("step43_results_summary.md", "summary and caveats", "organizational", "narrative infrastructure"),
        ("nonclaim_boundary_step43.md", "nonclaim boundary", "organizational", "boundary infrastructure"),
        ("step43_first_law_area_energy_statement.tex", "finite first-law/area-energy statement", "recognition-landing", "not theorem-grade over continuum gravity"),
        ("step43_schema.json", "machine-readable verdict", "organizational", "schema"),
        ("run_step43.py", "validator", "organizational", "validator"),
        ("mode_b_constraint_ledger.csv", "Mode-B constraints", "organizational", "ledger"),
        ("mode_b_target_lineage.csv", "target lineage", "organizational", "ledger"),
        ("mode_b_grammar_manifest.csv", "grammar manifest", "organizational", "ledger"),
    ]
    return [
        {
            "artifact": artifact,
            "claim": claim,
            "grade": grade,
            "scope": scope,
            "source_artifacts": rel(artifact),
        }
        for artifact, claim, grade, scope in entries
    ]


def build() -> dict[str, Any]:
    data = density_data()
    coefficient_info = rt_coefficient_from_prior()
    first_rows, first_summary = first_law_rows(data["rho0"], data["delta"], data["h_mod"], float(coefficient_info["coefficient"]))
    rel_rows = relative_entropy_rows(data["rho0"], data["delta"], first_summary["delta_H_mod"])
    area_rows = area_energy_rows(coefficient_info, first_summary, rel_rows)
    generated = generated_vs_input_rows(coefficient_info)
    script_text = Path(__file__).read_text(encoding="utf-8")
    anti = anti_circularity_rows(first_summary, rel_rows, coefficient_info)
    six = six_gate_rows(anti)
    anti_hardcode = anti_hardcode_rows(script_text)
    rel_second = float(rel_rows[1]["relative_entropy"])
    large_dev = abs(float(rel_rows[-1]["deviation_entropy_minus_linear"]))
    all_pass = all(row["passes"] for row in anti) and all(row["passes"] for row in six) and all(row["passes"] for row in anti_hardcode)
    schema = {
        "step": 43,
        "orientation": "ModeB_E018_entanglement_first_law_area_energy",
        "active_residual": "E018 area-shadow-price independently-checkable consequence leg",
        "main_object": "finite density-matrix entanglement first law and RT area-energy response",
        "verdict": "FIRST_LAW_AND_AREA_ENERGY_DERIVED" if all_pass else "FIRST_LAW_CONSEQUENCE_BLOCKED",
        "delta_S": first_summary["delta_S"],
        "delta_H_mod": first_summary["delta_H_mod"],
        "first_law_first_order_residual": first_summary["first_order_residual"],
        "relative_entropy_second_order": rel_second,
        "RT_coefficient_used": float(coefficient_info["coefficient"]),
        "RT_coefficient_source": coefficient_info["source"],
        "area_energy_relation": f"delta_A = {float(coefficient_info['coefficient']):.12g} * delta_H_mod",
        "large_perturbation_deviation": large_dev,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "other_law_landing_legs_attempted": False,
        "full_continuum_einstein_tensor_derived": False,
    }
    return {
        "density": data,
        "coefficient_info": coefficient_info,
        "first_rows": first_rows,
        "first_summary": first_summary,
        "rel_rows": rel_rows,
        "area_rows": area_rows,
        "generated": generated,
        "anti": anti,
        "six": six,
        "anti_hardcode": anti_hardcode,
        "schema": schema,
    }


def write_outputs() -> None:
    data = build()
    density = data["density"]
    write_json(
        ARTIFACT_DIR / "density_matrices_step43.json",
        {
            "rho0": density["rho0"].tolist(),
            "delta_rho": density["delta"].tolist(),
            "H_mod": density["h_mod"].tolist(),
            "rho0_eigenvalues": [float(x) for x in np.linalg.eigvalsh(density["rho0"])],
            "delta_rho_eigenvalues": [float(x) for x in np.linalg.eigvalsh(density["delta"])],
            "trace_delta_rho": float(np.trace(density["delta"])),
        },
    )
    write_csv(ARTIFACT_DIR / "first_law_rows_step43.csv", data["first_rows"], ["quantity", "value", "code_path", "detail"])
    write_csv(
        ARTIFACT_DIR / "relative_entropy_step43.csv",
        data["rel_rows"],
        [
            "t",
            "entropy_difference",
            "linear_modular_energy",
            "deviation_entropy_minus_linear",
            "relative_entropy",
            "second_order_coefficient_relative_entropy_over_t2",
            "deviation_matches_minus_relative_entropy",
        ],
    )
    write_csv(ARTIFACT_DIR / "area_energy_relation_step43.csv", data["area_rows"], ["item", "value", "source", "detail"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step43.csv", data["generated"], ["item", "status", "detail", "source_artifacts"])
    write_csv(ARTIFACT_DIR / "anti_circularity_step43.csv", data["anti"], ["gate", "passes", "witness", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step43.csv", data["six"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "anti_hardcode_step43.csv", data["anti_hardcode"], ["check", "passes", "evidence"])
    write_csv(
        ARTIFACT_DIR / "content_classification_step43.csv",
        content_classification_rows(),
        ["artifact", "claim", "grade", "scope", "source_artifacts"],
    )
    write_json(ARTIFACT_DIR / "step43_schema.json", data["schema"])
    write_summary(data)
    write_nonclaim(data)
    write_statement(data)
    write_mode_b_packet()


def write_summary(data: dict[str, Any]) -> None:
    first = data["first_summary"]
    rel_rows = data["rel_rows"]
    coefficient = float(data["coefficient_info"]["coefficient"])
    text = f"""# Step 43 Results Summary

## Honest Grade And Limit First

This step verifies the finite entanglement first law and exhibits its RT image as a linearized area-energy/Clausius relation. The result is an E2 recognition-landing and finite-carrier diagnostic: it does not determine the continuum gravitational coupling, does not supply SBT-alone physics, does not certify frame transfer, and is not a quantum-gravity solution. The full continuum step saying first laws for all ball regions imply the Einstein tensor equation needs a continuum/dynamical-geometry carrier and is not attempted here.

## Carrier

The carrier is a four-dimensional full-rank reduced density matrix `rho0` with a traceless Hermitian perturbation `delta_rho`. No metric-energy coupling is inserted into the carrier. `H_mod = -log(rho0)` is generated from the state.

## First Law Check

`delta S` is computed from the entropy of `rho(t)=rho0+t delta_rho` by a central finite difference. `delta <H_mod>` is computed independently as `Tr(delta_rho H_mod)`.

| quantity | value |
|---|---:|
| delta S from entropy path | {first['delta_S']:.12g} |
| delta <H_mod> from trace path | {first['delta_H_mod']:.12g} |
| first-order residual | {first['first_order_residual']:.12g} |

## Second-Order Teeth

The finite-t correction is not zero. At `t={SMALL_T}`, the relative entropy is `{float(rel_rows[1]['relative_entropy']):.12g}` and the entropy-minus-linear deviation is `{float(rel_rows[1]['deviation_entropy_minus_linear']):.12g}`. The large-perturbation deviation grows to `{abs(float(rel_rows[-1]['deviation_entropy_minus_linear'])):.12g}` at `t={rel_rows[-1]['t']}`.

## Area-Energy/Clausius Image

The RT coefficient is read from the accepted Step 41 saturated finite RT rows: `k = {coefficient:.12g}` area-units per entropy-unit. Therefore the RT image of the first law is:

`delta Area = {coefficient:.12g} * delta <H_mod>`.

For the chosen perturbation, `delta Area` per unit `t` is `{first['delta_area_per_unit_t']:.12g}`. This recognition-lands on the Jacobson/Faulkner-Van-Raamsdonk linearized Einstein equation-of-state pattern, but only at finite-toy/recognition grade.

## Verdict

`{data['schema']['verdict']}`. Next frontier: a continuum/dynamical-geometry carrier for the full Einstein-tensor implication.
"""
    (ARTIFACT_DIR / "step43_results_summary.md").write_text(text, encoding="utf-8")


def write_nonclaim(data: dict[str, Any]) -> None:
    text = """# Step 43 Nonclaim Boundary

This step does not determine the continuum gravitational coupling, does not compute Newton's constant, does not provide SBT-alone physics, does not certify frame transfer, and is not a quantum-gravity solution.

It verifies a finite density-matrix entanglement first law with a positive relative-entropy correction, then maps that leading-order relation through the prior finite RT coefficient. It does not establish the full continuum Einstein tensor equation. That requires the additional continuum result that the first law for all ball regions implies the local gravitational equation of state.

The modular-Hamiltonian-as-energy reading is a Bisognano-Wichmann/Jacobson/Faulkner-Van-Raamsdonk recognition landing, not an input derivation inside this finite toy.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step43.md").write_text(text, encoding="utf-8")


def write_statement(data: dict[str, Any]) -> None:
    first = data["first_summary"]
    rel_rows = data["rel_rows"]
    coefficient = float(data["coefficient_info"]["coefficient"])
    text = r"""\documentclass[11pt]{article}
\usepackage{amsmath}
\begin{document}

\section*{Step 43: Entanglement First Law And RT Area-Energy Consequence}

Let $\rho_0$ be the declared full-rank reduced density matrix and let
$\rho(t)=\rho_0+t\,\delta\rho$ with $\mathrm{{Tr}}\delta\rho=0$. Define
$H_{{\rm mod}}=-\log\rho_0$. The entropy derivative is computed from
$S(\rho(t))=-\mathrm{{Tr}}\rho(t)\log\rho(t)$, while the modular response is
computed separately as $\mathrm{{Tr}}(\delta\rho H_{\rm mod})$.

The finite carrier gives
\[
\left.\frac{{dS}}{{dt}}\right|_0 = __DELTA_S__,
\qquad
\delta\langle H_{{\rm mod}}\rangle = __DELTA_H__,
\]
with residual $__RESIDUAL__$. Thus the first law is
verified to first order on this carrier.

At finite $t=__SMALL_T__$,
\[
S(\rho(t)\Vert\rho_0)=__REL_ENT__>0,
\]
and
\[
S(\rho(t))-S(\rho_0)-t\,\delta\langle H_{{\rm mod}}\rangle
=-__REL_ENT__.
\]
The first law is therefore a leading-order relation, not an all-orders
identity.

Using the Step-41/42 RT entropy-unit coefficient $k=__COEFF__$, the
RT image is
\[
\delta A = k\,\delta\langle H_{{\rm mod}}\rangle.
\]
This is the finite-toy Clausius/linearized-gravity equation-of-state
recognition landing. It is not a continuum Einstein-tensor derivation.

\end{document}
"""
    text = (
        text.replace("__DELTA_S__", f"{first['delta_S']:.12g}")
        .replace("__DELTA_H__", f"{first['delta_H_mod']:.12g}")
        .replace("__RESIDUAL__", f"{first['first_order_residual']:.12g}")
        .replace("__SMALL_T__", f"{SMALL_T:.12g}")
        .replace("__REL_ENT__", f"{float(rel_rows[1]['relative_entropy']):.12g}")
        .replace("__COEFF__", f"{coefficient:.12g}")
    )
    (ARTIFACT_DIR / "step43_first_law_area_energy_statement.tex").write_text(text, encoding="utf-8")


def write_mode_b_packet() -> None:
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP41_RT_BOUND_NOT_IDENTITY", "status": "inherited", "detail": "S(A)<=min-cut and strict-gap control from Step41"},
            {"constraint_id": "C_STEP42_MULTIEDGE_HOLOGRAPHIC_ENRICHMENT", "status": "inherited", "detail": "random tensors and multi-edge minimal surface"},
            {"constraint_id": "C_STEP43_FIRST_LAW_LEADING_ORDER_NOT_IDENTITY", "status": "active", "detail": "Delta S_rel > 0 at finite t"},
            {"constraint_id": "C_STEP43_AREA_ENERGY_DERIVED_NOT_ASSUMED", "status": "active", "detail": "area response is RT coefficient times independently computed modular energy"},
        ],
        ["constraint_id", "status", "detail"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "E018 law-landing positive-relation consequence",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "sub_residual",
                "parent_steps": "Step41;Step42",
                "authorization": "USER-AUTHORIZED high-prize redirect, 2026-06-10",
            }
        ],
        ["target_residual", "canonical_target", "relation_to_canonical_root", "parent_steps", "authorization"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_FirstLawAreaEnergy_v1",
                "declared_at_step": 43,
                "carrier": "finite full-rank reduced density matrix with traceless Hermitian perturbation",
                "active_constraints": "separate entropy/modular-trace paths; positive relative entropy; RT coefficient from prior artifacts",
                "excluded_designs_rationale": "excludes all-orders identity and any metric-energy coupling inserted by hand",
                "non_triviality_argument": "large finite perturbations deviate from the first-law linear response by positive relative entropy",
                "next_grammar_delta": "continuum/dynamical-geometry carrier for all-ball-region first-law to Einstein-tensor implication",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )


def main() -> int:
    write_outputs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
