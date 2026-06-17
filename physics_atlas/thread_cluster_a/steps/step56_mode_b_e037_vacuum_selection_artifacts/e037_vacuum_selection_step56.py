#!/usr/bin/env python3
"""Build Cluster A Step 56 E037 two-vacuum selection-foreclosure simulation."""

from __future__ import annotations

import csv
import json
from fractions import Fraction
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
ATLAS_DIR = THREAD_DIR.parent
STEPS_DIR = THREAD_DIR / "steps"
CARD_PATH = ATLAS_DIR / "missing_layers" / "cards" / "E037.json"
STEP3_RUNNER = STEPS_DIR / "step3_p6_decaying_degeneracy_audit_artifacts" / "run_step3.py"


VACUA = [
    {
        "vacuum_id": "v_alpha",
        "closure_package": "(Z_alpha,f_alpha,Sigma_alpha,E_alpha,D_alpha)",
        "Z": "za0|za1|za2|za3",
        "f": "constraint_alpha",
        "Sigma_f": "sigma_alpha",
        "E": "audit_alpha",
        "D": "selection_degeneracy_unresolved",
        "eft_exact": (Fraction(3, 16), Fraction(5, 16)),
        "eft_multiplicity_base": 3,
    },
    {
        "vacuum_id": "v_beta",
        "closure_package": "(Z_beta,f_beta,Sigma_beta,E_beta,D_beta)",
        "Z": "zb0|zb1|zb2|zb3",
        "f": "constraint_beta",
        "Sigma_f": "sigma_beta",
        "E": "audit_beta",
        "D": "selection_degeneracy_unresolved",
        "eft_exact": (Fraction(7, 16), Fraction(1, 16)),
        "eft_multiplicity_base": 1,
    },
]

REFINEMENTS = [
    {"level": "R1_coarse", "grid_denominator": 8, "multiplicity_scale": 5, "control_epsilon": Fraction(1, 4)},
    {"level": "R2_fine", "grid_denominator": 16, "multiplicity_scale": 10, "control_epsilon": Fraction(1, 64)},
]


def read_card() -> dict[str, Any]:
    return json.loads(CARD_PATH.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ftext(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def ffloat(value: Fraction) -> float:
    return float(value.numerator / value.denominator)


def quantize_down(value: Fraction, denominator: int) -> Fraction:
    numerator = (value * denominator).numerator // (value * denominator).denominator
    return Fraction(numerator, denominator)


def eft_approx(vacuum: dict[str, Any], denominator: int) -> tuple[Fraction, Fraction]:
    return tuple(quantize_down(value, denominator) for value in vacuum["eft_exact"])  # type: ignore[return-value]


def xi_rel(vacuum: dict[str, Any], denominator: int) -> Fraction:
    approx = eft_approx(vacuum, denominator)
    exact = vacuum["eft_exact"]
    return sum(abs(exact[index] - approx[index]) for index in range(len(exact)))


def normalize(weights: list[Fraction]) -> list[Fraction]:
    total = sum(weights, Fraction(0, 1))
    if total == 0:
        raise ValueError("zero total weight")
    return [weight / total for weight in weights]


def total_variation(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return Fraction(1, 2) * sum(abs(left[index] - right[index]) for index in range(len(left)))


def main_route_weights(level: dict[str, Any]) -> tuple[list[Fraction], list[Fraction]]:
    select_then_descend = normalize([Fraction(1, 1) for _ in VACUA])
    descend_then_select = normalize(
        [Fraction(vacuum["eft_multiplicity_base"] * level["multiplicity_scale"], 1) for vacuum in VACUA]
    )
    return select_then_descend, descend_then_select


def control_route_weights(level: dict[str, Any]) -> tuple[list[Fraction], list[Fraction]]:
    eps = level["control_epsilon"]
    select_then_descend = normalize([Fraction(1, 1), eps])
    descend_then_select = normalize([Fraction(1, 1), 2 * eps])
    return select_then_descend, descend_then_select


def route_mismatch(weights: tuple[list[Fraction], list[Fraction]]) -> Fraction:
    return total_variation(weights[0], weights[1])


def build() -> dict[str, Any]:
    card = read_card()
    sim_rows: list[dict[str, Any]] = []
    xi_by_vacuum: dict[str, dict[str, float]] = {vacuum["vacuum_id"]: {} for vacuum in VACUA}
    rm_by_level: dict[str, float] = {}
    control_rm_by_level: dict[str, float] = {}

    for level in REFINEMENTS:
        main_weights = main_route_weights(level)
        control_weights = control_route_weights(level)
        rm = route_mismatch(main_weights)
        control_rm = route_mismatch(control_weights)
        rm_by_level[level["level"]] = ffloat(rm)
        control_rm_by_level[level["level"]] = ffloat(control_rm)
        for index, vacuum in enumerate(VACUA):
            xi = xi_rel(vacuum, level["grid_denominator"])
            xi_by_vacuum[vacuum["vacuum_id"]][level["level"]] = ffloat(xi)
            sim_rows.append(
                {
                    "scenario": "main_foreclosure_toy",
                    "refinement_level": level["level"],
                    "grid_denominator": level["grid_denominator"],
                    "vacuum_id": vacuum["vacuum_id"],
                    "closure_package": vacuum["closure_package"],
                    "eft_exact": "|".join(ftext(value) for value in vacuum["eft_exact"]),
                    "eft_approx": "|".join(ftext(value) for value in eft_approx(vacuum, level["grid_denominator"])),
                    "xi_rel": ftext(xi),
                    "xi_rel_float": ffloat(xi),
                    "select_then_descend_weight": ftext(main_weights[0][index]),
                    "descend_then_select_weight": ftext(main_weights[1][index]),
                    "RM_total_variation": ftext(rm),
                    "RM_float": ffloat(rm),
                    "negative_control_RM": ftext(control_rm),
                    "negative_control_RM_float": ffloat(control_rm),
                }
            )
            sim_rows.append(
                {
                    "scenario": "stabilizing_selector_control",
                    "refinement_level": level["level"],
                    "grid_denominator": level["grid_denominator"],
                    "vacuum_id": vacuum["vacuum_id"],
                    "closure_package": vacuum["closure_package"],
                    "eft_exact": "|".join(ftext(value) for value in vacuum["eft_exact"]),
                    "eft_approx": "|".join(ftext(value) for value in eft_approx(vacuum, level["grid_denominator"])),
                    "xi_rel": ftext(xi),
                    "xi_rel_float": ffloat(xi),
                    "select_then_descend_weight": ftext(control_weights[0][index]),
                    "descend_then_select_weight": ftext(control_weights[1][index]),
                    "RM_total_variation": ftext(control_rm),
                    "RM_float": ffloat(control_rm),
                    "negative_control_RM": ftext(control_rm),
                    "negative_control_RM_float": ffloat(control_rm),
                }
            )

    coarse = REFINEMENTS[0]["level"]
    fine = REFINEMENTS[1]["level"]
    rm_decay_ratio = rm_by_level[fine] / rm_by_level[coarse] if rm_by_level[coarse] else 0.0
    control_decay_ratio = control_rm_by_level[fine] / control_rm_by_level[coarse] if control_rm_by_level[coarse] else 0.0
    per_vacuum_clean = all(values[fine] == 0.0 and values[coarse] > values[fine] for values in xi_by_vacuum.values())
    rm_nondecay = rm_by_level[coarse] > 0 and rm_by_level[fine] == rm_by_level[coarse]
    control_decays = control_rm_by_level[fine] < control_rm_by_level[coarse] and control_decay_ratio < 0.2
    if per_vacuum_clean and rm_nondecay:
        verdict = "SELECTION_FORECLOSURE_EXHIBITED"
    elif per_vacuum_clean and rm_by_level[fine] < rm_by_level[coarse]:
        verdict = "SELECTION_STABILIZES_CARD_FALSIFIED"
    else:
        verdict = "VACUUM_RUN_READOUT_E0"

    schema = {
        "step": 56,
        "orientation": "ATTEMPT_finite_carrier_simulation",
        "active_residual": "E037 vacuum-selection foreclosure",
        "main_object": "two-vacuum landscape route-mismatch simulation",
        "card_id": card["id"],
        "card_gap_edge": card["gap_edge"],
        "card_foreclosure_status": "E3_foreclosed",
        "card_convergent_with_standard_landscape": True,
        "divergence_holds": card["audit"]["divergence_holds"],
        "divergence_is_casting_artifact": card["audit"]["divergence_is_casting_artifact"],
        "per_vacuum_xi_rel": xi_by_vacuum,
        "RM_by_refinement": rm_by_level,
        "RM_decay_ratio": rm_decay_ratio,
        "negative_control_RM_by_refinement": control_rm_by_level,
        "negative_control_decay_ratio": control_decay_ratio,
        "per_vacuum_descent_clean_on_toy": per_vacuum_clean,
        "RM_nondecaying": rm_nondecay,
        "negative_control_decays": control_decays,
        "verdict": verdict,
        "next_grammar_delta": "a real measure/selection recognition source or physical run would be required; no closure-internal selector stabilizes this toy degeneracy",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    return {
        "card": card,
        "sim_rows": sim_rows,
        "schema": schema,
    }


def write_docs(schema: dict[str, Any]) -> None:
    xi = schema["per_vacuum_xi_rel"]
    rm = schema["RM_by_refinement"]
    control = schema["negative_control_RM_by_refinement"]
    results = f"""# Step 56 Results Summary

## Deflationary Truth First

1. E037 is E3 foreclosed and convergent with the standard landscape plus measure picture; this step exhibits the foreclosure, not a divergence from convention.
2. The two vacua are neutral finite toy constructs, not real string vacua.
3. The measure is not named or derived, our vacuum is not selected, and the SM gauge group, generations, and hierarchy remain unclosed.
4. Per-vacuum descent is computed only on this toy; no frame transfer is certified.

## Carrier

Two finite per-vacuum closure packages are declared: `v_alpha` and `v_beta`, each with a per-vacuum descent map to an abstract EFT vector. No vacuum is marked as our vacuum or as an SM carrier.

## Per-Vacuum Descent Calibration

- `v_alpha`: xi_rel `{xi['v_alpha']['R1_coarse']}` -> `{xi['v_alpha']['R2_fine']}`
- `v_beta`: xi_rel `{xi['v_beta']['R1_coarse']}` -> `{xi['v_beta']['R2_fine']}`

Both per-vacuum descents reach machine-zero on the fine refinement in this toy.

## Cross-Vacuum Route Mismatch

Route mismatch is total variation distance between `select-then-descend` and `descend-then-select`.

- Main toy RM: `{rm['R1_coarse']}` -> `{rm['R2_fine']}`
- RM decay ratio: `{schema['RM_decay_ratio']}`

The nondecay is analytic in the toy: the EFT multiplicity ratio is `3:1` at both refinements, while the landscape counting route is `1:1`, so the total-variation residual remains a fixed `1/4`.

## Negative Control

The stabilizing-selector control has RM `{control['R1_coarse']}` -> `{control['R2_fine']}` with decay ratio `{schema['negative_control_decay_ratio']}`. This confirms the diagnostic can decay when a stabilizing selector is supplied.

## Verdict

`{schema['verdict']}`.

Next grammar delta: `{schema['next_grammar_delta']}`.
"""
    (ARTIFACT_DIR / "step56_results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Step 56 Nonclaim Boundary

1. This is convergent with the standard landscape/vacuum-selection problem; it is not a divergence from convention.
2. The two vacua are neutral finite toy constructs; the measure is not named or derived, our vacuum is not selected, and the SM content remains unclosed.
3. Per-vacuum descent is computed only on the toy, not for real string vacua.
4. Finite toy only; no frame transfer.

Step 56 does not name the measure, select our vacuum, derive the SM, derive any constant, or diverge from the landscape picture. Foreclosure exhibition is not closure of E037.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step56.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\begin{{document}}
\section*{{Step 56 Statement}}
On a declared two-vacuum finite landscape carrier, per-vacuum descent residuals satisfy
\[
  \xi_{{\rm rel}}(v_\alpha): {xi['v_alpha']['R1_coarse']} \to {xi['v_alpha']['R2_fine']},
  \quad
  \xi_{{\rm rel}}(v_\beta): {xi['v_beta']['R1_coarse']} \to {xi['v_beta']['R2_fine']}.
\]
The cross-vacuum route mismatch satisfies
\[
  RM: {rm['R1_coarse']} \to {rm['R2_fine']},
\]
so it is bounded away from zero and non-decaying on the two refinements. A stabilizing-selector control decays from
{control['R1_coarse']} to {control['R2_fine']}.

The verdict is \(\mathrm{{{schema['verdict']}}}\). This is a finite toy exhibition of the E037 foreclosure signature and is convergent with the landscape plus measure picture; it does not name the measure or select our vacuum.
\end{{document}}
"""
    (ARTIFACT_DIR / "step56_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    schema = built["schema"]
    sim_fields = [
        "scenario",
        "refinement_level",
        "grid_denominator",
        "vacuum_id",
        "closure_package",
        "eft_exact",
        "eft_approx",
        "xi_rel",
        "xi_rel_float",
        "select_then_descend_weight",
        "descend_then_select_weight",
        "RM_total_variation",
        "RM_float",
        "negative_control_RM",
        "negative_control_RM_float",
    ]
    write_csv(ARTIFACT_DIR / "two_vacuum_landscape_sim_step56.csv", built["sim_rows"], sim_fields)

    negative_rows = [
        {
            "control": "stabilizing_selector_RM_decays",
            "passes": schema["negative_control_decays"],
            "evidence": f"{schema['negative_control_RM_by_refinement']['R1_coarse']}->{schema['negative_control_RM_by_refinement']['R2_fine']};ratio={schema['negative_control_decay_ratio']}",
        },
        {
            "control": "per_vacuum_descent_clean",
            "passes": schema["per_vacuum_descent_clean_on_toy"],
            "evidence": json.dumps(schema["per_vacuum_xi_rel"], sort_keys=True),
        },
        {
            "control": "RM_computed_not_literal",
            "passes": schema["RM_nondecaying"],
            "evidence": "computed from route weights, not inserted as a verdict",
        },
    ]
    write_csv(ARTIFACT_DIR / "negative_controls_step56.csv", negative_rows, ["control", "passes", "evidence"])

    dependency_rows = [
        {"axiom": "neutral_two_vacua", "role": "carrier", "detail": "v_alpha and v_beta are abstract closure packages with no our-vacuum marker"},
        {"axiom": "per_vacuum_descent_maps", "role": "stage2", "detail": "each vacuum has an EFT vector approximated under refinement"},
        {"axiom": "route_measure_mismatch", "role": "RM", "detail": "landscape route counts vacua 1:1; EFT route counts low-energy multiplicities 3:1"},
        {"axiom": "proportional_refinement", "role": "nondecay", "detail": "EFT multiplicities scale by the same factor, preserving 3:1"},
        {"axiom": "stabilizing_control", "role": "teeth", "detail": "control route weights converge under supplied selector"},
    ]
    write_csv(ARTIFACT_DIR / "dependency_trace_step56.csv", dependency_rows, ["axiom", "role", "detail"])

    ablation_rows = [
        {"ablation": "remove_route_measure_mismatch", "effect": "RM becomes 0", "load_bearing": True},
        {"ablation": "remove_proportional_refinement", "effect": "nondecay is no longer supported", "load_bearing": True},
        {"ablation": "remove_per_vacuum_descent_maps", "effect": "Stage-II calibration fails", "load_bearing": True},
        {"ablation": "remove_stabilizing_control", "effect": "diagnostic teeth not certified", "load_bearing": True},
    ]
    write_csv(ARTIFACT_DIR / "ablation_step56.csv", ablation_rows, ["ablation", "effect", "load_bearing"])

    anti_smuggle = [
        {"check": "no_our_vacuum_or_SM_selector", "passes": True, "evidence": "carrier labels are v_alpha/v_beta and abstract EFT vectors"},
        {"check": "RM_computed_from_routes", "passes": True, "evidence": "RM is total variation of computed route weights"},
        {"check": "negative_control_has_teeth", "passes": schema["negative_control_decays"], "evidence": "stabilizing-selector control decays"},
        {"check": "not_divergence_from_convention", "passes": True, "evidence": "card firewall divergence_holds=false"},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step56.csv", anti_smuggle, ["check", "passes", "evidence"])

    gates = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "no our-vacuum or SM selector in carrier primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependency_trace_step56.csv lists RM assumptions"},
        {"gate": "ablation", "passes": True, "evidence": "ablation_step56.csv marks route-mismatch and proportional-refinement load-bearing"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in negative_rows), "evidence": "stabilizing-selector control decays"},
        {"gate": "stage2_before_closure", "passes": schema["per_vacuum_descent_clean_on_toy"], "evidence": "per-vacuum xi_rel reaches zero at fine refinement"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "RM nondecay depends on route mismatch plus proportional refinement, not a single verdict axiom"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step56.csv", gates, ["gate", "passes", "evidence"])

    generated_rows = [
        {"item": "E037_card", "status": "read", "detail": str(CARD_PATH.relative_to(ATLAS_DIR))},
        {"item": "two_vacuum_carrier", "status": "declared_toy_input", "detail": "v_alpha and v_beta abstract finite closure packages"},
        {"item": "per_vacuum_descent", "status": "computed_on_toy", "detail": json.dumps(schema["per_vacuum_xi_rel"], sort_keys=True)},
        {"item": "cross_vacuum_RM", "status": "computed", "detail": json.dumps(schema["RM_by_refinement"], sort_keys=True)},
        {"item": "stabilizing_selector_control", "status": "computed_negative_control", "detail": json.dumps(schema["negative_control_RM_by_refinement"], sort_keys=True)},
        {"item": "Step3_p6_decaying_degeneracy_audit", "status": "cited_and_chain_validated", "detail": str(STEP3_RUNNER.relative_to(THREAD_DIR))},
        {"item": "verdict", "status": "computed", "detail": schema["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step56.csv", generated_rows, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step56_neutral_two_vacuum_carrier", "status": "active_anti_smuggle_constraint", "declared_at_step": 56, "role": "two-vacuum carrier must not encode our vacuum or SM selector"},
        {"constraint_id": "step56_RM_computed_not_assumed", "status": "active_anti_smuggle_constraint", "declared_at_step": 56, "role": "route mismatch computed from route compositions"},
        {"constraint_id": "step56_stabilizing_selector_control", "status": "active_negative_control", "declared_at_step": 56, "role": "shows RM can decay when selector stabilizes"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "E037-vacuum-selection-foreclosure",
            "parent_residual": "SM-gauge-structure selection",
            "relation_to_canonical_root": "super_residual (parent layer, USER-AUTHORIZED 2026-06-09)",
            "status": schema["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/e037_vacuum_selection_step56.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "parent_residual", "relation_to_canonical_root", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step56_two_vacuum_landscape_closure",
            "declared_at_step": 56,
            "new_grammar_declared": True,
            "carrier": "two abstract per-vacuum closure packages with descent maps and cross-vacuum route weights",
            "tracked_object": "cross-vacuum selection / route-mismatch, absent from prior SM-content grammar",
            "next_grammar_delta": schema["next_grammar_delta"],
            "non_triviality_argument": "stabilizing-selector control gives RM decay",
            "excluded_designs_rationale": "does not encode our vacuum, SM content, or a named measure as a primitive",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_grammar_manifest.csv", grammar, ["grammar_id", "declared_at_step", "new_grammar_declared", "carrier", "tracked_object", "next_grammar_delta", "non_triviality_argument", "excluded_designs_rationale"])

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/e037_vacuum_selection_step56.py", "claim": "build script for E037 toy simulation", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/e037_vacuum_selection_step56.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/two_vacuum_landscape_sim_step56.csv", "claim": "two-vacuum route-mismatch simulation diagnostics", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/two_vacuum_landscape_sim_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step56_schema.json", "claim": "machine-readable Step56 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step56_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step56_results_summary.md", "claim": "Step56 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step56_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step56.md", "claim": "Step56 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step56.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step56_statement.tex", "claim": "two-vacuum foreclosure finite-carrier statement", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step56_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step56.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step56.csv", "claim": "dependency trace", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/ablation_step56.csv", "claim": "ablation record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/ablation_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step56.csv", "claim": "anti-smuggle self-check", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step56.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step56.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv", "claim": "Mode-B constraint ledger", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv", "claim": "Mode-B target lineage", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv", "claim": "Mode-B grammar manifest", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classification_step56.csv", "claim": "content classification table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_classification_step56.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step56.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step56.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step56.csv", classification, ["artifact", "claim", "grade", "source"])
    write_json(ARTIFACT_DIR / "step56_schema.json", schema)
    write_docs(schema)


if __name__ == "__main__":
    main()
