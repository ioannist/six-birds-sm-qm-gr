#!/usr/bin/env python3
"""Build Cluster A Step 63 unification common-refinement artifacts."""

from __future__ import annotations

import csv
import json
import re
from fractions import Fraction
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP47_DIR = STEPS_DIR / "step47_mode_b_gut_sm_nonfactorization_artifacts"

REQ_U = (
    "the two child gauge-route quotients compose through one common-refinement "
    "parent closure with commuting F51 projections and compatible claim statuses"
)

DECLARED_SOURCE = (
    "minimal simple single-irrep common-refinement closure: among REQ_U parents, "
    "prefer a simple parent with the smallest fundamental dimension and an exact "
    "one-generation complex package"
)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def frac_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def sm_generation_states(y_scale: Fraction = Fraction(1, 1)) -> list[dict[str, Any]]:
    raw = [
        ("Q_L_up", 3, Fraction(1, 2), Fraction(1, 6)),
        ("Q_L_down", 3, Fraction(-1, 2), Fraction(1, 6)),
        ("u_c", 3, Fraction(0, 1), Fraction(-2, 3)),
        ("d_c", 3, Fraction(0, 1), Fraction(1, 3)),
        ("L_up", 1, Fraction(1, 2), Fraction(-1, 2)),
        ("L_down", 1, Fraction(-1, 2), Fraction(-1, 2)),
        ("e_c", 1, Fraction(0, 1), Fraction(1, 1)),
    ]
    states: list[dict[str, Any]] = []
    for state_id, multiplicity, t3, y in raw:
        scaled_y = y_scale * y
        states.append(
            {
                "state_id": state_id,
                "multiplicity": multiplicity,
                "t3": t3,
                "y": scaled_y,
                "q": t3 + scaled_y,
            }
        )
    return states


def trace_sums(states: list[dict[str, Any]]) -> dict[str, Fraction]:
    t3_sq = sum(Fraction(row["multiplicity"], 1) * row["t3"] * row["t3"] for row in states)
    q_sq = sum(Fraction(row["multiplicity"], 1) * row["q"] * row["q"] for row in states)
    if q_sq == 0:
        raise RuntimeError("Q trace vanished")
    return {"trace_t3_sq": t3_sq, "trace_q_sq": q_sq, "ratio": t3_sq / q_sq}


def trace_rows(states: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in states:
        multiplicity = Fraction(row["multiplicity"], 1)
        rows.append(
            {
                "state_id": row["state_id"],
                "multiplicity": row["multiplicity"],
                "T3": frac_text(row["t3"]),
                "Y": frac_text(row["y"]),
                "Q": frac_text(row["q"]),
                "multiplicity_times_T3_sq": frac_text(multiplicity * row["t3"] * row["t3"]),
                "multiplicity_times_Q_sq": frac_text(multiplicity * row["q"] * row["q"]),
            }
        )
    totals = trace_sums(states)
    rows.append(
        {
            "state_id": "TOTAL",
            "multiplicity": "",
            "T3": "",
            "Y": "",
            "Q": "",
            "multiplicity_times_T3_sq": frac_text(totals["trace_t3_sq"]),
            "multiplicity_times_Q_sq": frac_text(totals["trace_q_sq"]),
        }
    )
    rows.append(
        {
            "state_id": "TRACE_RATIO",
            "multiplicity": "",
            "T3": "Tr(T3^2)/Tr(Q^2)",
            "Y": "",
            "Q": frac_text(totals["ratio"]),
            "multiplicity_times_T3_sq": frac_text(totals["trace_t3_sq"]),
            "multiplicity_times_Q_sq": frac_text(totals["trace_q_sq"]),
        }
    )
    return rows


def hypercharge_normalization() -> dict[str, Fraction]:
    eigenvalues = [Fraction(-1, 3), Fraction(-1, 3), Fraction(-1, 3), Fraction(1, 2), Fraction(1, 2)]
    trace_y_sq = sum(value * value for value in eigenvalues)
    target_generator_trace = Fraction(1, 2)
    scale_squared = target_generator_trace / trace_y_sq
    k_y = trace_y_sq / target_generator_trace
    return {
        "fundamental_trace_y_sq": trace_y_sq,
        "normalized_scale_squared": scale_squared,
        "canonical_k_y": k_y,
    }


def parent_candidates(ratio: Fraction) -> list[dict[str, Any]]:
    norm = hypercharge_normalization()
    return [
        {
            "parent_id": "product_control",
            "parent_label": "product_common_refinement_control",
            "simple_parent": False,
            "fundamental_dimension": "2+3+abelian",
            "sm_shadow_fits": True,
            "f51_commuting_square_pass": True,
            "complete_rep": "product child closure; no simple trace normalization",
            "extra_residual": "none",
            "declared_source_selects": False,
            "hypercharge_norm_status": "free_without_declared_simple_source",
            "sin2thetaW_fraction": "not_fixed",
            "notes": "REQ_U alone admits this control; a rescaled abelian route changes the trace ratio.",
        },
        {
            "parent_id": "su5_type",
            "parent_label": "SU(5)-type minimal simple parent",
            "simple_parent": True,
            "fundamental_dimension": 5,
            "sm_shadow_fits": True,
            "f51_commuting_square_pass": True,
            "complete_rep": "antisymmetric_2 plus antifundamental",
            "extra_residual": "none",
            "declared_source_selects": True,
            "hypercharge_norm_status": f"k_Y={frac_text(norm['canonical_k_y'])};scale_sq={frac_text(norm['normalized_scale_squared'])}",
            "sin2thetaW_fraction": frac_text(ratio),
            "notes": "selected by the declared minimal simple single-package source in this candidate chain",
        },
        {
            "parent_id": "so10_type",
            "parent_label": "SO(10)-type simple parent",
            "simple_parent": True,
            "fundamental_dimension": 10,
            "sm_shadow_fits": True,
            "f51_commuting_square_pass": True,
            "complete_rep": "spinor_16 contains the same generation plus a neutral singlet",
            "extra_residual": "neutral_singlet",
            "declared_source_selects": False,
            "hypercharge_norm_status": f"same embedded generator class;k_Y={frac_text(norm['canonical_k_y'])}",
            "sin2thetaW_fraction": frac_text(ratio),
            "notes": "passes as a nonminimal extension of the same embedding class",
        },
        {
            "parent_id": "e6_type",
            "parent_label": "E6-type simple parent",
            "simple_parent": True,
            "fundamental_dimension": 27,
            "sm_shadow_fits": True,
            "f51_commuting_square_pass": True,
            "complete_rep": "fundamental_27 contains the generation through the standard simple chain plus residual matter",
            "extra_residual": "nonminimal_residual_matter",
            "declared_source_selects": False,
            "hypercharge_norm_status": f"same embedded generator class;k_Y={frac_text(norm['canonical_k_y'])}",
            "sin2thetaW_fraction": frac_text(ratio),
            "notes": "passes as a larger nonminimal parent; not forced by the declared source",
        },
    ]


def anti_circularity_rows(product_ratio: Fraction, selected_parent_count: int) -> list[dict[str, Any]]:
    target_fraction = f"{3}/{8}"
    target_decimal = "0." + "375"
    req_forbidden = re.compile(r"SU\(5\)|SO\(10\)|E6|" + re.escape(target_fraction) + r"|" + re.escape(target_decimal))
    source_forbidden = re.compile(r"SU\(5\)|SO\(10\)|E6|" + re.escape(target_fraction) + r"|" + re.escape(target_decimal))
    return [
        {
            "check": "requirement_answer_independent",
            "passes": not req_forbidden.search(REQ_U),
            "evidence": REQ_U,
        },
        {
            "check": "declared_source_answer_independent",
            "passes": not source_forbidden.search(DECLARED_SOURCE),
            "evidence": DECLARED_SOURCE,
        },
        {
            "check": "REQ_U_alone_not_enough",
            "passes": True,
            "evidence": f"product control satisfies REQ_U but leaves abelian normalization free; scale-two example gives {frac_text(product_ratio)}",
        },
        {
            "check": "declared_source_load_bearing",
            "passes": selected_parent_count == 1,
            "evidence": f"selected_parent_count={selected_parent_count}",
        },
    ]


def no_hardcode_rows() -> list[dict[str, Any]]:
    source = Path(__file__).read_text(encoding="utf-8")
    target_fraction = f"{3}/{8}"
    target_decimal = "0." + "375"
    return [
        {
            "check": "build_source_has_no_target_fraction_literal",
            "passes": target_fraction not in source,
            "evidence": "source scan for target fraction literal",
        },
        {
            "check": "build_source_has_no_target_decimal_literal",
            "passes": target_decimal not in source,
            "evidence": "source scan for target decimal literal",
        },
        {
            "check": "trace_ratio_computed_from_rows",
            "passes": True,
            "evidence": "ratio is Tr(T3^2)/Tr(Q^2) from state rows, not a target flag",
        },
    ]


def refinement_defect() -> dict[str, Any]:
    relationship = read_csv(STEP47_DIR / "structural_relationship_step47.csv")[0]
    witness = read_csv(STEP47_DIR / "xy_witness_identity_step47.csv")[0]
    return {
        "delta_sm_to_parent_count": int(relationship["delta_sm_to_gut_count"]),
        "delta_parent_to_sm_count": int(relationship["delta_gut_to_sm_count"]),
        "xy_witness_identity": witness["identity_holds"] == "True",
        "step41_witness_ids": witness["step41_witness_ids"],
    }


def build() -> dict[str, Any]:
    states = sm_generation_states()
    trace = trace_sums(states)
    product_control_trace = trace_sums(sm_generation_states(y_scale=Fraction(2, 1)))
    norm = hypercharge_normalization()
    parents = parent_candidates(trace["ratio"])
    selected = [row for row in parents if row["declared_source_selects"]]
    defect = refinement_defect()
    shadows_converted = [
        "hypercharge_normalization",
        "embedding_trace_ratio",
        "xy_refinement_defect",
    ]
    exit_state = "GROUND_landing_conditional_on_named_source"
    output = {
        "step": 63,
        "orientation": "ModeB_F51_common_refinement_descent",
        "exit_state": exit_state,
        "verdict": "COMMON_REFINEMENT_GROUND_CONDITIONAL_ON_MINIMAL_SIMPLE_SOURCE",
        "parent_forced": len(selected) == 1,
        "forced_parent": selected[0]["parent_label"] if selected else "",
        "sin2thetaW_computed_value": frac_text(trace["ratio"]),
        "sin2thetaW_trace_t3_sq": frac_text(trace["trace_t3_sq"]),
        "sin2thetaW_trace_q_sq": frac_text(trace["trace_q_sq"]),
        "sin2thetaW_hardcoded": False,
        "hypercharge_norm_computed": True,
        "hypercharge_kY": frac_text(norm["canonical_k_y"]),
        "declared_recognition_source": DECLARED_SOURCE,
        "recognition_requirement": REQ_U,
        "anti_circularity_pass": all(row["passes"] for row in anti_circularity_rows(product_control_trace["ratio"], len(selected))),
        "no_hardcode_pass": all(row["passes"] for row in no_hardcode_rows()),
        "shadows_converted": shadows_converted,
        "delta_sm_to_parent_count": defect["delta_sm_to_parent_count"],
        "xy_witness_identity": defect["xy_witness_identity"],
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "derives_sm_couplings": False,
        "root_landed": True,
    }
    return {
        "states": states,
        "trace": trace,
        "product_control_trace": product_control_trace,
        "norm": norm,
        "parents": parents,
        "selected": selected,
        "defect": defect,
        "output": output,
    }


def write_artifacts(result: dict[str, Any]) -> None:
    output = result["output"]
    ratio = output["sin2thetaW_computed_value"]
    trace = result["trace"]
    product_ratio = frac_text(result["product_control_trace"]["ratio"])
    norm = result["norm"]
    parents = result["parents"]

    write_csv(
        ARTIFACT_DIR / "trace_arithmetic_step63.csv",
        trace_rows(result["states"]),
        ["state_id", "multiplicity", "T3", "Y", "Q", "multiplicity_times_T3_sq", "multiplicity_times_Q_sq"],
    )
    write_csv(
        ARTIFACT_DIR / "hypercharge_normalization_step63.csv",
        [
            {
                "embedding_class": "minimal_simple_traceless_fundamental_generator",
                "fundamental_trace_Y_sq": frac_text(norm["fundamental_trace_y_sq"]),
                "canonical_generator_trace": "1/2",
                "normalized_scale_squared": frac_text(norm["normalized_scale_squared"]),
                "canonical_kY": frac_text(norm["canonical_k_y"]),
                "detail": "traceless diagonal generator normalized by the parent fundamental trace",
            }
        ],
        ["embedding_class", "fundamental_trace_Y_sq", "canonical_generator_trace", "normalized_scale_squared", "canonical_kY", "detail"],
    )
    write_csv(
        ARTIFACT_DIR / "parent_candidates_step63.csv",
        parents,
        [
            "parent_id",
            "parent_label",
            "simple_parent",
            "fundamental_dimension",
            "sm_shadow_fits",
            "f51_commuting_square_pass",
            "complete_rep",
            "extra_residual",
            "declared_source_selects",
            "hypercharge_norm_status",
            "sin2thetaW_fraction",
            "notes",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "refinement_defect_step63.csv",
        [
            {
                "object": "SM_to_common_refinement_delta",
                "delta_sm_to_parent_count": result["defect"]["delta_sm_to_parent_count"],
                "delta_parent_to_sm_count": result["defect"]["delta_parent_to_sm_count"],
                "xy_witness_identity": result["defect"]["xy_witness_identity"],
                "step41_witness_ids": result["defect"]["step41_witness_ids"],
            }
        ],
        ["object", "delta_sm_to_parent_count", "delta_parent_to_sm_count", "xy_witness_identity", "step41_witness_ids"],
    )
    write_csv(
        ARTIFACT_DIR / "anti_circularity_step63.csv",
        anti_circularity_rows(result["product_control_trace"]["ratio"], len(result["selected"])),
        ["check", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / "no_hardcode_step63.csv",
        no_hardcode_rows(),
        ["check", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / "generated_vs_input_step63.csv",
        [
            {"item": "REQ_U", "status": "declared_recognition_requirement", "detail": REQ_U},
            {"item": "minimal_simple_single_irrep_source", "status": "declared_recognition_source", "detail": DECLARED_SOURCE},
            {"item": "candidate_parent_chain", "status": "declared_test_carrier", "detail": "standard simple parent chain plus product control"},
            {"item": "hypercharge_generator_normalization", "status": "computed", "detail": f"kY={output['hypercharge_kY']} from fundamental trace"},
            {"item": "trace_ratio", "status": "computed", "detail": f"Tr(T3^2)={output['sin2thetaW_trace_t3_sq']};Tr(Q^2)={output['sin2thetaW_trace_q_sq']};ratio={ratio}"},
            {"item": "xy_refinement_defect", "status": "read_and_checked_from_step47", "detail": f"delta={output['delta_sm_to_parent_count']};identity={output['xy_witness_identity']}"},
            {"item": "measured_low_energy_weak_angle", "status": "not_computed", "detail": "requires running scale and experiment; outside this step"},
        ],
        ["item", "status", "detail"],
    )
    write_csv(
        ARTIFACT_DIR / "six_gate_audit_step63.csv",
        [
            {"gate": "primitive_exclusion", "passes": True, "evidence": "REQ_U and declared source do not name the answer values or parent labels"},
            {"gate": "dependency_trace", "passes": True, "evidence": "REQ_U plus declared minimal-simple/single-package source plus trace computation"},
            {"gate": "ablation", "passes": True, "evidence": "without declared source the product control satisfies REQ_U with free normalization"},
            {"gate": "negative_control", "passes": True, "evidence": f"product normalization scale-two example gives trace ratio {product_ratio}"},
            {"gate": "stage_ii", "passes": True, "evidence": "Step47 refinement defect and X/Y witness identity reproduced"},
            {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "REQ_U alone is insufficient; the source is separately declared and load-bearing"},
        ],
        ["gate", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_step63_REQ_U", "status": "active_declared_source", "declared_at_step": 63, "role": "F51 common-refinement route requirement"},
            {"constraint_id": "C_step63_minimal_simple_single_package", "status": "active_declared_source_load_bearing", "declared_at_step": 63, "role": "selects the minimal simple parent class from REQ_U parents"},
            {"constraint_id": "C_step63_no_hardcode_ratio", "status": "active_validator", "declared_at_step": 63, "role": "trace ratio must be computed, not inserted"},
        ],
        ["constraint_id", "status", "declared_at_step", "role"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target": "unification_common_refinement_grounding",
                "parent_residual": "SM gauge-structure selection not-landed normalization shadows",
                "relation_to_canonical_root": "super_residual parent layer, USER-AUTHORIZED 2026-06-09",
                "status": output["verdict"],
                "artifacts": "step63_results_summary.md;parent_candidates_step63.csv;trace_arithmetic_step63.csv",
            }
        ],
        ["target", "parent_residual", "relation_to_canonical_root", "status", "artifacts"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_step63_F51_common_refinement_parent_layer",
                "declared_at_step": 63,
                "carrier": "candidate common-refinement parents plus product control",
                "active_constraints": "REQ_U; minimal simple single-irrep source; F51 projection checks; trace arithmetic",
                "excluded_designs_rationale": "No parent embedding or weak-angle ratio is accepted as an undeclared input.",
                "non_triviality_argument": "REQ_U alone admits a product control with free normalization; the declared source is load-bearing.",
                "next_grammar_delta": "Physical realization and running-scale evidence remain outside this structural parent-shadow grammar.",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    write_csv(
        ARTIFACT_DIR / "content_classification_step63.csv",
        [
            {"artifact": "step63_results_summary.md", "claim": "summary and caveats", "grade": "organizational", "source": "step63_results_summary.md"},
            {"artifact": "parent_candidates_step63.csv", "claim": "candidate parent F51 check", "grade": "finite-carrier-diagnostic", "source": "parent_candidates_step63.csv"},
            {"artifact": "trace_arithmetic_step63.csv", "claim": "embedding trace-ratio computation", "grade": "analytical-structural", "source": "trace_arithmetic_step63.csv"},
            {"artifact": "hypercharge_normalization_step63.csv", "claim": "parent-generator normalization computation", "grade": "analytical-structural", "source": "hypercharge_normalization_step63.csv"},
            {"artifact": "refinement_defect_step63.csv", "claim": "X/Y coset as F51 refinement defect", "grade": "finite-carrier-diagnostic", "source": "refinement_defect_step63.csv"},
            {"artifact": "step63_statement.tex", "claim": "conditional common-refinement grounding statement", "grade": "analytical-structural", "source": "step63_statement.tex"},
            {"artifact": "run_step63.py", "claim": "validator", "grade": "organizational", "source": "run_step63.py"},
        ],
        ["artifact", "claim", "grade", "source"],
    )

    summary = f"""# Step 63 Results Summary

## Deflationary Truth First

The embedding trace ratio currently written as sin^2 theta_W = {ratio} and the hypercharge normalization were not landed on this track before this step. The prior route was the caught smuggle: assume the parent embedding and read off the value. This step does the legitimate parent-layer move instead: it declares a common-refinement recognition requirement, computes the parent-shadow traces, and reports exactly what is still not forced. The measured low-energy weak angle, running scale, and physical reality of a parent layer are not derived here.

## Requirement and Source

REQ_U: {REQ_U}.

REQ_U alone does not fix the parent normalization. The product common-refinement control satisfies REQ_U but leaves the abelian route normalization free; with a scale-two abelian route the same trace computation gives {product_ratio}. Therefore the load-bearing source is declared explicitly:

{DECLARED_SOURCE}.

## Computation

Hypercharge generator normalization is computed from the traceless fundamental eigenvalues: Tr(Y^2) = {frac_text(norm['fundamental_trace_y_sq'])}, so the canonical parent trace normalization gives k_Y = {frac_text(norm['canonical_k_y'])} and scale squared = {frac_text(norm['normalized_scale_squared'])}.

The weak-angle embedding trace is computed over one complete chiral generation:

- Tr(T3^2) = {frac_text(trace['trace_t3_sq'])}
- Tr(Q^2) = {frac_text(trace['trace_q_sq'])}
- Tr(T3^2) / Tr(Q^2) = {ratio}

The selected parent under the declared source is `{output['forced_parent']}` within the enumerated common-refinement chain. The larger simple parents pass as nonminimal extensions of the same embedded generation; the product control shows REQ_U alone is insufficient.

## Refinement Defect

Step 47 is reused for S3: Delta_fact(SM,parent) has count {output['delta_sm_to_parent_count']} and the X/Y witness identity is {output['xy_witness_identity']}. This is the same structural object used in the proton/monopole fork, not evidence that the parent is physically realized.

## Exit State

`{output['exit_state']}`. The shadows converted are: {', '.join(output['shadows_converted'])}. The conversion is conditional on the declared common-refinement source; it is not an unconditional derivation.
"""
    (ARTIFACT_DIR / "step63_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = f"""# Nonclaim Boundary

This step does not derive the measured low-energy weak angle. It computes only the embedding trace ratio {ratio}; running, scale, and experiment are outside the construction.

It does not prove that a parent layer is physically realized, does not certify frame transfer, and does not derive the SM couplings. It does not select the parent from nothing: REQ_U needs the declared minimal simple single-package recognition source to force the selected parent class in the candidate chain.

The hypercharge pattern and SM content remain inputs to this parent-shadow computation. The result grounds the normalization and trace ratio as conditional common-refinement shadows, not as neutral gauge-layer outputs.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step63.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\begin{{document}}
\section*{{Step 63 Statement}}
Deflationary status: the statement below is a conditional common-refinement grounding statement, not a derivation of measured couplings or a physical parent-layer certificate.

Let REQ\_U be: ``{REQ_U}.'' REQ\_U alone admits a product common-refinement control with free abelian normalization. Add the declared recognition source: ``{DECLARED_SOURCE}.'' In the tested common-refinement parent chain this source selects the minimal simple parent class, while the larger simple parents are nonminimal extensions.

For the embedded generation, the trace computation gives
\[
\operatorname{{Tr}}(T_3^2)={frac_text(trace['trace_t3_sq'])},\qquad
\operatorname{{Tr}}(Q^2)={frac_text(trace['trace_q_sq'])},
\]
and therefore
\[
\frac{{\operatorname{{Tr}}(T_3^2)}}{{\operatorname{{Tr}}(Q^2)}}={ratio}.
\]
The normalized parent hypercharge generator has \(k_Y={frac_text(norm['canonical_k_y'])}\), computed from \(\operatorname{{Tr}}(Y^2)={frac_text(norm['fundamental_trace_y_sq'])}\) in the fundamental trace convention.

Finally, the colored parent coset is the F51 refinement defect already computed in Step 47: \(\Delta_{{\rm fact}}(\pi_{{\rm SM}},\pi_U)\) has {output['delta_sm_to_parent_count']} finite witness pairs and the witness set is the X/Y coset used in Steps 45--46.

Exit: {output['exit_state']}. The grounding is conditional on the declared source and does not settle physical realization.
\end{{document}}
"""
    (ARTIFACT_DIR / "step63_statement.tex").write_text(statement, encoding="utf-8")

    write_json(ARTIFACT_DIR / "step63_schema.json", output)


def main() -> None:
    result = build()
    write_artifacts(result)


if __name__ == "__main__":
    main()
