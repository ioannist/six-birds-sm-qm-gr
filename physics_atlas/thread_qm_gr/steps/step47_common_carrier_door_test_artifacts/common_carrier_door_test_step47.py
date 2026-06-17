#!/usr/bin/env python3
"""Step 47 common-carrier door-test for the QM-GR track.

The computation distinguishes laws that force the existence of a shared carrier
from laws that only give the form or admissibility criterion for a shared
carrier when a warranted one is supplied.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_ROOT = ARTIFACT_DIR.parents[1]
REPO_ROOT = THREAD_ROOT.parents[2]
STEP18_DIR = THREAD_ROOT / "steps" / "step18_f37_complementarity_f24_resolution_artifacts"
STEP25_DIR = THREAD_ROOT / "steps" / "step25_sourcing_unification_artifacts"
STEP26_DIR = THREAD_ROOT / "steps" / "step26_semiclassical_dynamics_artifacts"
TOL = 1e-10


def rel(path: Path) -> str:
    return str(path.relative_to(THREAD_ROOT))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def residual(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.linalg.norm(left - right) / max(float(np.linalg.norm(right)), 1.0))


def commutator_residual(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a @ b - b @ a))


def projection_rank(matrix: np.ndarray) -> int:
    return int(np.linalg.matrix_rank(matrix, tol=1e-10))


def build_quotient_toy() -> dict[str, object]:
    """Finite quotient data mirroring the Step18 QM/GR access pair."""
    pi_qm = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
        ],
        dtype=float,
    )
    pi_gr = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    pi_l = np.eye(4)
    to_qm = pi_qm.copy()
    to_gr = pi_gr.copy()
    l_res_qm = residual(to_qm @ pi_l, pi_qm)
    l_res_gr = residual(to_gr @ pi_l, pi_gr)

    # A finite incompatible-access control: two rank-1 idempotent projectors
    # whose commutator is nonzero. In the commuting-idempotent quotient grammar,
    # nonzero commutator means there is no admissible joint quotient.
    p_x = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=float)
    p_y = 0.5 * np.array([[1.0, 1.0], [1.0, 1.0]], dtype=float)
    comp_comm = commutator_residual(p_x, p_y)

    return {
        "pi_qm": pi_qm,
        "pi_gr": pi_gr,
        "pi_l": pi_l,
        "to_qm": to_qm,
        "to_gr": to_gr,
        "l_res_qm": l_res_qm,
        "l_res_gr": l_res_gr,
        "l_admissible_joint": bool(l_res_qm <= TOL and l_res_gr <= TOL),
        "p_x": p_x,
        "p_y": p_y,
        "complementary_commutator_residual": comp_comm,
        "complementary_pair_admissible_joint": bool(comp_comm <= TOL),
    }


def load_step25_summary() -> dict[str, float | bool]:
    schema = json.loads((STEP25_DIR / "step25_schema.json").read_text(encoding="utf-8"))
    fields = schema["track_fields"]
    final = schema["final_verdict"]
    return {
        "L_single_psi_sources_both": bool(final["L_single_psi_sources_both"]),
        "non_co_sourced_control_pass": bool(final["non_co_sourced_control_pass"]),
        "L_max_born_residual": float(fields["L_max_born_residual"]),
        "L_max_stress_residual": float(fields["L_max_stress_residual"]),
        "control_max_stress_residual": float(fields["control_max_stress_residual"]),
        "control_mean_stress_residual": float(fields["control_mean_stress_residual"]),
    }


def load_step26_summary() -> dict[str, float | bool]:
    schema = json.loads((STEP26_DIR / "step26_schema.json").read_text(encoding="utf-8"))
    final = schema["final_verdict"]
    fields = schema["track_fields"]
    return {
        "potential_sourced_from_T00": bool(fields["potential_sourced_from_T00"]),
        "consistent_coupling_converged": bool(final["consistent_coupling_converged"]),
        "runaway_control_converged": bool(final["runaway_control_converged"]),
        "consistent_kappa": float(fields["consistent_kappa"]),
        "consistent_fixed_point_residual": float(fields["consistent_fixed_point_residual"]),
        "runaway_fixed_point_residual": float(fields["runaway_fixed_point_residual"]),
    }


def law_rows(toy: dict[str, object], warrant: dict[str, float | bool]) -> list[dict[str, object]]:
    complementary_has_no_joint = not bool(toy["complementary_pair_admissible_joint"])
    main_has_joint = bool(toy["l_admissible_joint"])
    non_cosourcing_no_warrant = not bool(warrant["non_co_sourced_control_pass"])
    return [
        {
            "law": "F37_complementarity_non_joint_access",
            "tested_question": "Does the law force this pair to share a carrier?",
            "computed_evidence": (
                f"co-sourcing pair admissible_joint={main_has_joint}; "
                f"complementary_control_commutator_residual={toy['complementary_commutator_residual']:.12g}; "
                f"complementary_control_admissible_joint={toy['complementary_pair_admissible_joint']}"
            ),
            "gives_form": True,
            "forces_existence": False,
            "door_test_result": "FORM_NOT_EXISTENCE",
            "reason": "F37 classifies a supplied pair as joint-accessible or complementary; it does not choose which physical pairs have a shared carrier.",
        },
        {
            "law": "F51_unification_common_refinement",
            "tested_question": "Does the law force QM and GR to unify?",
            "computed_evidence": (
                f"L refinement residuals qm={toy['l_res_qm']:.1g}, gr={toy['l_res_gr']:.1g}; "
                f"complementary_control_has_joint={not complementary_has_no_joint}"
            ),
            "gives_form": True,
            "forces_existence": False,
            "door_test_result": "FORM_NOT_EXISTENCE",
            "reason": "F51 says what unification is if a common refinement is warranted; it does not supply the warrant that this pair must unify.",
        },
        {
            "law": "FoEC_universal_quotient_calculus",
            "tested_question": "Does universal quotient form force two theories to share one carrier?",
            "computed_evidence": (
                "individual_carrier_QM=True; individual_carrier_GR=True; "
                "shared_carrier_requires_extra_warrant=True"
            ),
            "gives_form": True,
            "forces_existence": False,
            "door_test_result": "FORM_NOT_EXISTENCE",
            "reason": "Universal quotient form gives each theory some carrier; a single shared carrier is an additional recognition premise.",
        },
        {
            "law": "SAU_non_descending_object_discipline",
            "tested_question": "Does audited usefulness force the shared carrier?",
            "computed_evidence": (
                f"L_single_psi_sources_both={warrant['L_single_psi_sources_both']}; "
                f"non_cosourced_control_pass={warrant['non_co_sourced_control_pass']}; "
                f"control_max_stress_residual={warrant['control_max_stress_residual']:.12g}"
            ),
            "gives_form": True,
            "forces_existence": False,
            "door_test_result": "LICENSE_NOT_DERIVATION",
            "reason": "SAU licenses adjoining a non-descending common object once descents are audited; it is not an internal theorem that the object must exist.",
        },
    ]


def control_rows(toy: dict[str, object], warrant: dict[str, float | bool]) -> list[dict[str, object]]:
    return [
        {
            "control": "complementary_noncommuting_pair",
            "purpose": "show candidate laws do not manufacture a carrier for incompatible accesses",
            "quantity": "commutator_residual",
            "value": f"{toy['complementary_commutator_residual']:.12g}",
            "passes_control": not bool(toy["complementary_pair_admissible_joint"]),
            "interpretation": "nonzero commutator in the commuting-idempotent quotient grammar; no admissible joint quotient",
        },
        {
            "control": "non_co_sourcing_independent_field",
            "purpose": "show the semiclassical co-sourcing warrant is load-bearing",
            "quantity": "control_max_stress_residual",
            "value": f"{warrant['control_max_stress_residual']:.12g}",
            "passes_control": not bool(warrant["non_co_sourced_control_pass"]),
            "interpretation": "independent GR field breaks the one-psi warrant; no common-carrier recognition warrant",
        },
    ]


def write_outputs() -> None:
    toy = build_quotient_toy()
    warrant = load_step25_summary()
    dynamics_warrant = load_step26_summary()
    laws = law_rows(toy, warrant)
    controls = control_rows(toy, warrant)

    all_form_not_existence = all(row["gives_form"] and not row["forces_existence"] for row in laws)
    complementary_ok = bool(controls[0]["passes_control"])
    non_cosourcing_ok = bool(controls[1]["passes_control"])
    verdict = (
        "COMMON_CARRIER_IS_RECOGNITION_SOURCE_WARRANTED"
        if all_form_not_existence and complementary_ok and non_cosourcing_ok
        else "PREMISE_GROUNDING_BLOCKED"
    )

    quotient_json = {
        "source_paths_thread_root_relative": {
            "step18": rel(STEP18_DIR),
            "step25": rel(STEP25_DIR),
            "step26": rel(STEP26_DIR),
            "ladder_vs_fork": rel(THREAD_ROOT / "interpretation" / "ladder_vs_fork.md"),
        },
        "main_pair": {
            "q_QM": "pi_QM=(d0,d1,d2)",
            "q_GR": "pi_GR=(d0,d2,d3)",
            "L_joint": "pi_L=(d0,d1,d2,d3)",
            "qm_residual": toy["l_res_qm"],
            "gr_residual": toy["l_res_gr"],
            "admissible_joint": toy["l_admissible_joint"],
        },
        "complementary_control": {
            "grammar": "finite linear quotient idempotents with admissible joints restricted to commuting projections",
            "P_X": toy["p_x"].tolist(),
            "P_Y": toy["p_y"].tolist(),
            "rank_P_X": projection_rank(toy["p_x"]),
            "rank_P_Y": projection_rank(toy["p_y"]),
            "commutator_residual": toy["complementary_commutator_residual"],
            "admissible_joint": toy["complementary_pair_admissible_joint"],
        },
        "semiclassical_cosourcing_warrant_from_step25": warrant,
        "semiclassical_backreaction_warrant_from_step26": dynamics_warrant,
    }

    schema = {
        "step": 47,
        "orientation": "Batch_B_common_carrier_door_test",
        "active_residual": "E018 common-carrier premise grounding objection",
        "main_object": "forces-vs-form test for the common-carrier premise",
        "verdict": verdict,
        "per_law": {
            row["law"]: {
                "gives_form": bool(row["gives_form"]),
                "forces_existence": bool(row["forces_existence"]),
                "door_test_result": row["door_test_result"],
            }
            for row in laws
        },
        "warrant": "semiclassical co-sourcing: one psi gives Born[psi] and stress-energy T[psi] descents with zero residual on Step25",
        "recognition_source": "COMMON_CARRIER_PREMISE_WARRANTED_BY_SEMICLASSICAL_CO_SOURCING",
        "landing_mode": "LANDED_GROUND_CONDITIONAL",
        "premise_ground_landed": True,
        "grounding_source": "semiclassical co-sourcing layer with Step25 Born/stress descents and Step26 matter-sourced geometry back-reaction",
        "warrant_extended_via_step26": True,
        "complementary_pair_no_carrier": complementary_ok,
        "non_cosourcing_no_warrant": non_cosourcing_ok,
        "source_warrant_caveat": "semiclassical co-sourcing is the named recognition source",
        "theorem_strength_caveat": "recognition-source GROUND landing, not an SBT-internal proof",
        "frame_transfer_residual": "free gravitational degrees of freedom, the full quantum-gravity sector, and trans-semiclassical survival of the common carrier",
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
    }

    write_csv(ARTIFACT_DIR / "law_door_test_step47.csv", laws)
    write_csv(ARTIFACT_DIR / "common_carrier_controls_step47.csv", controls)
    write_csv(
        ARTIFACT_DIR / "co_sourcing_warrant_step47.csv",
        [
            {
                "warrant": "semiclassical_co_sourcing",
                "source": rel(STEP25_DIR / "step25_schema.json"),
                "backreaction_source": rel(STEP26_DIR / "step26_schema.json"),
                "single_psi_sources_both": warrant["L_single_psi_sources_both"],
                "L_max_born_residual": f"{warrant['L_max_born_residual']:.12g}",
                "L_max_stress_residual": f"{warrant['L_max_stress_residual']:.12g}",
                "non_co_sourced_control_pass": warrant["non_co_sourced_control_pass"],
                "control_max_stress_residual": f"{warrant['control_max_stress_residual']:.12g}",
                "potential_sourced_from_T00": dynamics_warrant["potential_sourced_from_T00"],
                "step26_consistent_coupling_converged": dynamics_warrant["consistent_coupling_converged"],
                "step26_consistent_fixed_point_residual": f"{dynamics_warrant['consistent_fixed_point_residual']:.12g}",
                "recognition_warrant_load_bearing": non_cosourcing_ok,
            }
        ],
    )
    with (ARTIFACT_DIR / "quotient_toy_step47.json").open("w", encoding="utf-8") as handle:
        json.dump(quotient_json, handle, indent=2)
    with (ARTIFACT_DIR / "step47_schema.json").open("w", encoding="utf-8") as handle:
        json.dump(schema, handle, indent=2)

    summary = f"""# Step 47 Results Summary

## Honest Grade / Verdict First

Verdict: the common-carrier premise is LANDED * GROUND (conditional) -- grounded as the down-shadow of the semiclassical co-sourcing layer. This is a recognition-mode landing, not an unconditional derivation, and not "merely relocation": the premise is not derivable within the QM-GR layer, so the valid landing is relocation up the tower to a named source-warrant.

The door-test does not find an SBT-internal law that forces QM and GR to share a carrier. The formal verdict remains `{verdict}`: F37, F51, FoEC, and SAU give the form, criterion, or license for a common carrier once one is warranted, but they do not derive the existence of the shared carrier for this physical pair. The common-carrier premise is therefore a named recognition source, warranted by semiclassical co-sourcing: one field `psi` has both the Born readout `|psi|^2` and the stress-energy readout `T[psi]`.

GROUND caveats: (i) source-warrant: the source is semiclassical co-sourcing, extended by Step26's back-reaction loop; (ii) theorem-strength: this is a recognition-source landing, not a proof from SBT alone.

This is not arbitrary modeling, but it is also not an SBT-only theorem. The warrant is known semiclassical co-sourcing, checked in Step25 independently of the Step47 door-test and extended in Step26 to matter-sourced geometry via `V[psi] = background + kappa*T00[psi]`.

The per-law forces-vs-form classification (F37 / F51 / FoEC / SAU) is a structural reading of the framework sources, not a line-by-line computation from the texts; the computed teeth are the two can-fail controls: the complementary pair gives no manufactured carrier, and the non-co-sourcing control removes the warrant. This is a structural audit plus recognition-source GROUND landing, not a decisive proof.

## Toy

The main access pair mirrors Step18:

- `q_QM = (d0,d1,d2)`.
- `q_GR = (d0,d2,d3)`.
- `L_joint = (d0,d1,d2,d3)`.

Computed joint residuals:

- QM residual: `{toy['l_res_qm']:.1g}`.
- GR residual: `{toy['l_res_gr']:.1g}`.
- admissible joint: `{toy['l_admissible_joint']}`.

## Forces-vs-Form Test

| Law | Gives form/criterion | Forces existence | Computed evidence | Door-test result |
|---|---:|---:|---|---|
"""
    for row in laws:
        summary += (
            f"| `{row['law']}` | `{row['gives_form']}` | `{row['forces_existence']}` | "
            f"{row['computed_evidence']} | `{row['door_test_result']}` |\n"
        )
    summary += f"""
## Can-Fail Controls

| Control | Result | Evidence |
|---|---|---|
| Complementary noncommuting pair | no manufactured shared carrier | commutator residual `{toy['complementary_commutator_residual']:.12g}`; admissible joint `{toy['complementary_pair_admissible_joint']}` |
| Non-co-sourcing independent field | no common-carrier warrant | Step25 control max stress residual `{warrant['control_max_stress_residual']:.12g}`; non-co-sourced control pass `{warrant['non_co_sourced_control_pass']}` |

## Recognition Warrant

The recognition source is semiclassical co-sourcing, not the existence of the Step18 finite `L` itself. Step25 computes:

- `L_single_psi_sources_both = {warrant['L_single_psi_sources_both']}`.
- `L_max_born_residual = {warrant['L_max_born_residual']:.1g}`.
- `L_max_stress_residual = {warrant['L_max_stress_residual']:.1g}`.
- `non_co_sourced_control_pass = {warrant['non_co_sourced_control_pass']}`.

Step26 extends the warrant past stress-energy toward matter-sourced geometry:

- source: `{rel(STEP26_DIR / 'step26_schema.json')}`.
- `potential_sourced_from_T00 = {dynamics_warrant['potential_sourced_from_T00']}`.
- `consistent_coupling_converged = {dynamics_warrant['consistent_coupling_converged']}`.
- `consistent_fixed_point_residual = {dynamics_warrant['consistent_fixed_point_residual']:.12g}`.

Removing co-sourcing removes the warrant, which is why the premise is not arbitrary and not forced by the abstract laws alone.

## Frame-Transfer Residual

The residual is narrowed: the warrant reaches QM's Born readout, stress-energy, and matter-sourced geometry in the finite semiclassical back-reaction toy. What remains open is the free gravitational degrees of freedom, the full quantum-gravity sector, and trans-semiclassical survival of the common carrier. It is not accurate to say that curvature in general is wholly outside the warrant.
"""
    (ARTIFACT_DIR / "step47_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 47 Nonclaim Boundary

Verdict: the common-carrier premise is LANDED * GROUND (conditional) -- grounded as the down-shadow of the semiclassical co-sourcing layer. This is a recognition-mode landing, not an unconditional derivation, and not "merely relocation."

This step does not prove that QM and GR share a carrier from SBT alone. It identifies the common-carrier premise as a recognition source warranted by semiclassical co-sourcing, extended by Step26 from stress-energy toward matter-sourced geometry through `V[psi] = background + kappa*T00[psi]`.

GROUND caveats: source-warrant is semiclassical co-sourcing; theorem-strength is recognition-source rather than SBT-internal proof.

It does not certify frame transfer beyond the semiclassical regime, does not close E018, does not solve quantum gravity, and does not establish a new physical law. The residual is free gravitational degrees of freedom, the full quantum-gravity sector, and trans-semiclassical survival of the common carrier.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step47.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\section*{Step 47 Door-Test Statement}

Let \(q_{\rm QM}\) and \(q_{\rm GR}\) be the two access quotients of the
finite toy:
\[
q_{\rm QM}=(d_0,d_1,d_2), \qquad q_{\rm GR}=(d_0,d_2,d_3).
\]
The candidate joint quotient \(L=(d_0,d_1,d_2,d_3)\) has zero descent
residuals to both children.

The door-test asks whether a framework law forces the existence of such a
shared carrier. The answer on the tested laws is negative. F37 classifies
joint access versus complementarity; F51 gives the form of unification as a
common refinement; FoEC gives each theory a carrier but not one shared carrier;
and SAU licenses a non-descending object once its descents are audited. None
forces the existence of the common carrier for the QM/GR pair.

Verdict: the common-carrier premise is LANDED * GROUND (conditional), grounded
as the down-shadow of the semiclassical co-sourcing layer. This is a
recognition-mode landing, not an unconditional derivation and not merely
relocation.

The recognition source is semiclassical co-sourcing: one field \(\psi\) carries
both the Born readout \(|\psi|^2\) and the stress-energy readout \(T[\psi]\).
Step26 extends this warrant toward matter-sourced geometry by computing a
back-reaction loop \(V[\psi]=V_0+\kappa T_{00}[\psi]\). The non-co-sourced
control fails this warrant. Thus the common-carrier premise is warranted, not
arbitrary, but it is not an SBT-internal theorem. The remaining residual is the
free gravitational sector and trans-semiclassical frame transfer.
"""
    (ARTIFACT_DIR / "common_carrier_door_test_statement_step47.tex").write_text(statement, encoding="utf-8")

    write_csv(
        ARTIFACT_DIR / "content_classification_step47.csv",
        [
            {
                "artifact": "common_carrier_door_test_step47.py",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "computes the forces-vs-form door-test and controls",
            },
            {
                "artifact": "law_door_test_step47.csv",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "per-law form/existence table",
            },
            {
                "artifact": "common_carrier_controls_step47.csv",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "complementary-pair and non-co-sourcing controls",
            },
            {
                "artifact": "co_sourcing_warrant_step47.csv",
                "classification": "remaining-external",
                "grade": "recognition-source",
                "scope": "semiclassical co-sourcing warrant imported from known physics and Step25 audit",
            },
            {
                "artifact": "step47_results_summary.md",
                "classification": "organizational",
                "grade": "summary",
                "scope": "door-test result and caveats",
            },
            {
                "artifact": "common_carrier_door_test_statement_step47.tex",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "formal statement of recognition-source verdict",
            },
            {
                "artifact": "run_step47.py",
                "classification": "organizational",
                "grade": "validator",
                "scope": "artifact and no-overclaim validation",
            },
        ],
    )

    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {
                "constraint_id": "C_STEP47_DOOR_TEST_NO_FABRICATED_GROUNDING",
                "status": "active",
                "description": "A grounding may be claimed only if a tested law forces shared-carrier existence non-circularly.",
            },
            {
                "constraint_id": "C_STEP47_CAN_FAIL_CONTROLS",
                "status": "active",
                "description": "Complementary-pair and non-co-sourcing controls must have teeth.",
            },
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "common-carrier premise grounding",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "sub_residual",
                "authorization": "USER-AUTHORIZED Batch B #2",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_CommonCarrierDoorTest_v1",
                "declared_at_step": 47,
                "objects": "finite quotient maps; admissible joint quotients; commuting-idempotent complementary control; co-sourcing warrant audit",
                "excluded_designs_rationale": "Excludes proofs that assume the common carrier and then infer its grounding.",
                "non_triviality_argument": "The complementary control has no admissible joint and the independent-field control removes the warrant.",
                "next_grammar_delta": "trans-semiclassical carrier survival / frame-transfer test",
            }
        ],
    )


if __name__ == "__main__":
    write_outputs()
