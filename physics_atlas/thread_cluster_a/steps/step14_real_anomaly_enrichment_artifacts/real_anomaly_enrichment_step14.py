#!/usr/bin/env python3
"""Cluster A Step 14: real anomaly-theory enrichment.

This is a finite candidate-space computation over real SM anomaly
coefficients. It is a selection/measure construction over candidates and
constraints, not a readout-pair model.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]


@dataclass(frozen=True)
class Fermion:
    name: str
    su3: str
    su2: str
    y: Fraction
    note: str = ""


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    group: str
    description: str
    fermions: tuple[Fermion, ...]
    selected_reference: bool = False
    su5_reps: tuple[str, ...] = ()
    equivalent_by_normalization: bool = False


SU3 = {
    "1": {"dim": 1, "cubic": Fraction(0), "dynkin": Fraction(0)},
    "3": {"dim": 3, "cubic": Fraction(1), "dynkin": Fraction(1, 2)},
    "3bar": {"dim": 3, "cubic": Fraction(-1), "dynkin": Fraction(1, 2)},
}

SU2 = {
    "1": {"dim": 1, "dynkin": Fraction(0), "doublet": 0},
    "2": {"dim": 2, "dynkin": Fraction(1, 2), "doublet": 1},
}

SU5_CUBIC = {
    "5": Fraction(1),
    "5bar": Fraction(-1),
    "10": Fraction(1),
    "10bar": Fraction(-1),
    "1": Fraction(0),
}


def sm_generation(scale: Fraction = Fraction(1)) -> tuple[Fermion, ...]:
    return (
        Fermion("Q", "3", "2", scale * Fraction(1, 6), "left quark doublet"),
        Fermion("u_c", "3bar", "1", scale * Fraction(-2, 3), "left conjugate up singlet"),
        Fermion("d_c", "3bar", "1", scale * Fraction(1, 3), "left conjugate down singlet"),
        Fermion("L", "1", "2", scale * Fraction(-1, 2), "left lepton doublet"),
        Fermion("e_c", "1", "1", scale * Fraction(1), "left conjugate electron singlet"),
    )


def candidates() -> list[Candidate]:
    base = sm_generation()
    swapped = (
        Fermion("Q", "3", "2", Fraction(1, 6), "left quark doublet"),
        Fermion("u_c_swapped", "3bar", "1", Fraction(1, 3), "label-swapped singlet"),
        Fermion("d_c_swapped", "3bar", "1", Fraction(-2, 3), "label-swapped singlet"),
        Fermion("L", "1", "2", Fraction(-1, 2), "left lepton doublet"),
        Fermion("e_c", "1", "1", Fraction(1), "left conjugate electron singlet"),
    )
    return [
        Candidate(
            "SM_one_generation",
            "SU3xSU2xU1",
            "Actual one-generation chiral SM content in left-handed convention",
            base,
            selected_reference=True,
        ),
        Candidate(
            "bad_u_hypercharge",
            "SU3xSU2xU1",
            "Alternative hypercharge assignment changing only u_c",
            (
                Fermion("Q", "3", "2", Fraction(1, 6)),
                Fermion("u_c_bad", "3bar", "1", Fraction(-1, 3)),
                Fermion("d_c", "3bar", "1", Fraction(1, 3)),
                Fermion("L", "1", "2", Fraction(-1, 2)),
                Fermion("e_c", "1", "1", Fraction(1)),
            ),
        ),
        Candidate(
            "quark_sector_only",
            "SU3xSU2xU1",
            "Quark multiplets without the correlated lepton sector",
            base[:3],
        ),
        Candidate(
            "missing_e_c",
            "SU3xSU2xU1",
            "SM reps with the charged lepton singlet removed",
            base[:4],
        ),
        Candidate(
            "SM_plus_vectorlike_lepton",
            "SU3xSU2xU1",
            "SM plus a vector-like electroweak doublet pair",
            base
            + (
                Fermion("X_L", "1", "2", Fraction(-1, 2), "extra vector-like doublet"),
                Fermion("X_L_c", "1", "2", Fraction(1, 2), "extra vector-like doublet conjugate"),
            ),
        ),
        Candidate(
            "SM_plus_vectorlike_down",
            "SU3xSU2xU1",
            "SM plus a vector-like colored singlet pair",
            base
            + (
                Fermion("D", "3", "1", Fraction(-1, 3), "extra vector-like color triplet"),
                Fermion("D_c", "3bar", "1", Fraction(1, 3), "extra vector-like conjugate"),
            ),
        ),
        Candidate(
            "SM_plus_sterile_neutrino",
            "SU3xSU2xU1",
            "SM plus one gauge-sterile right-neutrino conjugate",
            base + (Fermion("N_c", "1", "1", Fraction(0), "sterile singlet"),),
        ),
        Candidate(
            "hypercharge_label_swapped",
            "SU3xSU2xU1",
            "Anomaly-free solution with the two color singlet hypercharges exchanged",
            swapped,
        ),
        Candidate(
            "scaled_hypercharge_x2",
            "SU3xSU2xU1",
            "Overall U(1) normalization scaled by two",
            sm_generation(Fraction(2)),
            equivalent_by_normalization=True,
        ),
        Candidate(
            "SU5_10_plus_5bar_decomposition",
            "SU5_style_decomposed_to_SU3xSU2xU1",
            "SU(5)-style 10 plus 5bar decomposed into one SM generation",
            base,
            su5_reps=("10", "5bar"),
        ),
    ]


def anomaly_coefficients(candidate: Candidate) -> dict[str, Fraction | int | bool | str]:
    su3_cubic = Fraction(0)
    su3_sq_u1 = Fraction(0)
    su2_sq_u1 = Fraction(0)
    u1_cubic = Fraction(0)
    grav_u1 = Fraction(0)
    su2_doublet_count = 0
    for fermion in candidate.fermions:
        s3 = SU3[fermion.su3]
        s2 = SU2[fermion.su2]
        dim3 = s3["dim"]
        dim2 = s2["dim"]
        su3_cubic += s3["cubic"] * dim2
        su3_sq_u1 += s3["dynkin"] * dim2 * fermion.y
        su2_sq_u1 += s2["dynkin"] * dim3 * fermion.y
        u1_cubic += dim3 * dim2 * fermion.y**3
        grav_u1 += dim3 * dim2 * fermion.y
        su2_doublet_count += dim3 * s2["doublet"]
    su5_cubic = sum(SU5_CUBIC[rep] for rep in candidate.su5_reps)
    return {
        "su3_cubic": su3_cubic,
        "su3_sq_u1": su3_sq_u1,
        "su2_sq_u1": su2_sq_u1,
        "u1_cubic": u1_cubic,
        "grav_u1": grav_u1,
        "su2_doublet_count": su2_doublet_count,
        "su2_witten_even": su2_doublet_count % 2 == 0,
        "su5_cubic": su5_cubic,
    }


def is_anomaly_free(coeffs: dict[str, Fraction | int | bool | str]) -> bool:
    return (
        coeffs["su3_cubic"] == 0
        and coeffs["su3_sq_u1"] == 0
        and coeffs["su2_sq_u1"] == 0
        and coeffs["u1_cubic"] == 0
        and coeffs["grav_u1"] == 0
        and coeffs["su2_witten_even"] is True
        and coeffs["su5_cubic"] == 0
    )


def fstr(value: Fraction | int | bool | str) -> str:
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return str(value.numerator)
        return f"{value.numerator}/{value.denominator}"
    return str(value)


def write_csv(name: str, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with (ARTIFACT_DIR / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def hypercharge_solution() -> dict[str, object]:
    q = "Y_Q"
    return {
        "variables": ["Y_Q", "Y_u_c", "Y_d_c", "Y_L", "Y_e_c"],
        "constraints": [
            "2 Y_Q + Y_u_c + Y_d_c = 0",
            "3 Y_Q + Y_L = 0",
            "6 Y_Q + 3 Y_u_c + 3 Y_d_c + 2 Y_L + Y_e_c = 0",
            "6 Y_Q^3 + 3 Y_u_c^3 + 3 Y_d_c^3 + 2 Y_L^3 + Y_e_c^3 = 0",
        ],
        "closed_form_family": {
            "Y_L": "-3 Y_Q",
            "Y_e_c": "6 Y_Q",
            "{Y_u_c,Y_d_c}": "{-4 Y_Q, 2 Y_Q}",
            "label_choice": "choosing the usual up/down Yukawa labels gives Y_u_c=-4 Y_Q and Y_d_c=2 Y_Q",
        },
        "normalization": {
            "choose": f"{q}=1/6",
            "SM_values": {
                "Y_Q": "1/6",
                "Y_u_c": "-2/3",
                "Y_d_c": "1/3",
                "Y_L": "-1/2",
                "Y_e_c": "1",
            },
        },
        "electric_charge_check": {
            "Q_em": "T3 + Y",
            "Q_u": "1/2 + Y_Q = 2/3",
            "Q_d": "-1/2 + Y_Q = -1/3",
            "Q_e": "-1/2 + Y_L = -1",
            "Q_proton": "2 Q_u + Q_d = 1",
            "relation": "Q_proton = - Q_e",
        },
        "grade": "known-physics limit-recovery and closed-form calibration",
    }


def main() -> None:
    cands = candidates()
    anomaly_rows: list[dict[str, object]] = []
    fermion_rows: list[dict[str, object]] = []
    survivor_rows: list[dict[str, object]] = []
    for candidate in cands:
        coeffs = anomaly_coefficients(candidate)
        free = is_anomaly_free(coeffs)
        anomaly_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "group": candidate.group,
                "description": candidate.description,
                "su3_cubic": fstr(coeffs["su3_cubic"]),
                "su3_sq_u1": fstr(coeffs["su3_sq_u1"]),
                "su2_sq_u1": fstr(coeffs["su2_sq_u1"]),
                "u1_cubic": fstr(coeffs["u1_cubic"]),
                "grav_u1": fstr(coeffs["grav_u1"]),
                "su2_doublet_count": coeffs["su2_doublet_count"],
                "su2_witten_even": coeffs["su2_witten_even"],
                "su5_cubic": fstr(coeffs["su5_cubic"]),
                "anomaly_free": free,
                "selected_reference": candidate.selected_reference,
                "equivalent_by_normalization": candidate.equivalent_by_normalization,
            }
        )
        if free:
            survivor_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "group": candidate.group,
                    "selected_reference": candidate.selected_reference,
                    "equivalent_by_normalization": candidate.equivalent_by_normalization,
                    "survivor_status": "reference" if candidate.selected_reference else "unselected_survivor",
                    "description": candidate.description,
                }
            )
        for fermion in candidate.fermions:
            fermion_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "field": fermion.name,
                    "su3_rep": fermion.su3,
                    "su2_rep": fermion.su2,
                    "hypercharge": fstr(fermion.y),
                    "su3_dim": SU3[fermion.su3]["dim"],
                    "su2_dim": SU2[fermion.su2]["dim"],
                    "note": fermion.note,
                }
            )

    solution = hypercharge_solution()
    consequence = {
        "most_promising_step15_consequence": "minimal irreducible anomaly-cancellation support",
        "statement": (
            "In a bounded real-rep enumeration, anomaly-free candidates with the SM chiral reps "
            "must correlate quark and lepton hypercharges by the solved relations; remaining "
            "non-reference survivors are vector-like/exotic refinements, sterile extensions, "
            "normalization equivalents, or label-swapped variants. Step 15 should test a "
            "minimality/irreducibility selector over a broader candidate set."
        ),
        "independent_check": (
            "Enumerate chiral spectra over SU(3)xSU(2)xU(1) reps with bounded denominator "
            "hypercharges, compute the same anomalies, remove vector-like pairs, and check "
            "whether the reference one-generation support is minimal among non-equivalent "
            "anomaly-free chiral supports while vector-like exotics are non-minimal refinements."
        ),
        "not_claimed_here": "This step scopes the consequence; it does not certify it.",
    }
    obligations = [
        {
            "obligation": "faithful_enrichment",
            "status": "advanced",
            "witness": "real SU(3), SU(2), U(1), gravitational, Witten, and SU(5)-style anomaly coefficients computed exactly",
        },
        {
            "obligation": "independently_checkable_consequence",
            "status": "scoped_for_step15",
            "witness": consequence["most_promising_step15_consequence"],
        },
        {
            "obligation": "derived_formula",
            "status": "advanced",
            "witness": "closed-form anomaly-equation family Y_L=-3Y_Q, Y_e=6Y_Q, {Y_u,Y_d}={-4Y_Q,2Y_Q}",
        },
        {
            "obligation": "limit_recovery",
            "status": "advanced",
            "witness": "SM one-generation anomaly coefficients all vanish; Q_proton=-Q_e recovered under Y_Q=1/6 normalization",
        },
    ]

    write_csv(
        "candidate_anomalies_step14.csv",
        anomaly_rows,
        [
            "candidate_id",
            "group",
            "description",
            "su3_cubic",
            "su3_sq_u1",
            "su2_sq_u1",
            "u1_cubic",
            "grav_u1",
            "su2_doublet_count",
            "su2_witten_even",
            "su5_cubic",
            "anomaly_free",
            "selected_reference",
            "equivalent_by_normalization",
        ],
    )
    write_csv(
        "fermion_content_step14.csv",
        fermion_rows,
        ["candidate_id", "field", "su3_rep", "su2_rep", "hypercharge", "su3_dim", "su2_dim", "note"],
    )
    write_csv(
        "anomaly_free_survivors_step14.csv",
        survivor_rows,
        ["candidate_id", "group", "selected_reference", "equivalent_by_normalization", "survivor_status", "description"],
    )
    write_csv(
        "candidate_law_obligations_step14.csv",
        obligations,
        ["obligation", "status", "witness"],
    )
    (ARTIFACT_DIR / "hypercharge_solution_step14.json").write_text(json.dumps(solution, indent=2), encoding="utf-8")
    (ARTIFACT_DIR / "scoped_consequence_step14.json").write_text(json.dumps(consequence, indent=2), encoding="utf-8")

    sm_row = next(row for row in anomaly_rows if row["candidate_id"] == "SM_one_generation")
    survivor_count = len(survivor_rows)
    unselected_count = sum(1 for row in survivor_rows if row["survivor_status"] == "unselected_survivor")
    anomaly_free_ids = [row["candidate_id"] for row in survivor_rows]

    schema = {
        "step": 14,
        "artifact_dir": "steps/step14_real_anomaly_enrichment_artifacts",
        "final_verdict": {
            "type": "real_anomaly_enrichment_limit_recovery_constructed",
            "candidate_count": len(cands),
            "anomaly_free_survivor_count": survivor_count,
            "unselected_anomaly_free_survivor_count": unselected_count,
            "sm_coefficients_all_zero": all(
                sm_row[key] == "0"
                for key in ["su3_cubic", "su3_sq_u1", "su2_sq_u1", "u1_cubic", "grav_u1", "su5_cubic"]
            )
            and sm_row["su2_witten_even"] is True,
            "necessary_not_sufficient": unselected_count >= 1,
            "candidate_law_grade": "not_landed_obligations_advanced",
            "root_landed": False,
            "frame_transfer_certified": False,
        },
        "anomaly_free_candidate_ids": anomaly_free_ids,
        "known_physics_limit_recovery": True,
        "new_consequence_only_scoped": True,
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")

    content_rows = [
        {
            "claim_id": "real_anomaly_coefficients",
            "claim": "Exact rational anomaly coefficients are computed for a finite real candidate set.",
            "grade": "finite-carrier-diagnostic",
            "classification": "faithful-enrichment",
            "scope": "finite curated real-rep candidates",
            "source_artifacts": "steps/step14_real_anomaly_enrichment_artifacts/candidate_anomalies_step14.csv;steps/step14_real_anomaly_enrichment_artifacts/fermion_content_step14.csv",
        },
        {
            "claim_id": "sm_limit_recovery",
            "claim": "The one-generation SM chiral content is verified anomaly-free with all listed coefficients zero.",
            "grade": "finite-carrier-diagnostic",
            "classification": "limit-recovery-known-physics",
            "scope": "known anomaly cancellation recovered",
            "source_artifacts": "steps/step14_real_anomaly_enrichment_artifacts/candidate_anomalies_step14.csv",
        },
        {
            "claim_id": "closed_form_hypercharge_relations",
            "claim": "Solving the anomaly equations for fixed SM reps gives the known hypercharge-ratio family up to normalization.",
            "grade": "finite-carrier-diagnostic",
            "classification": "derived-formula-known-physics",
            "scope": "fixed-representation anomaly equations",
            "source_artifacts": "steps/step14_real_anomaly_enrichment_artifacts/hypercharge_solution_step14.json",
        },
        {
            "claim_id": "necessary_not_sufficient",
            "claim": "Real anomaly-freedom prunes but leaves anomaly-free non-reference survivors.",
            "grade": "finite-carrier-diagnostic",
            "classification": "selection-shape",
            "scope": "finite candidate set",
            "source_artifacts": "steps/step14_real_anomaly_enrichment_artifacts/anomaly_free_survivors_step14.csv",
        },
        {
            "claim_id": "scoped_checkable_consequence",
            "claim": "A minimal irreducible anomaly-cancellation support consequence is scoped for the next step.",
            "grade": "remaining-external",
            "classification": "candidate-law-next-obligation",
            "scope": "scoped only, not certified here",
            "source_artifacts": "steps/step14_real_anomaly_enrichment_artifacts/scoped_consequence_step14.json",
        },
        {
            "claim_id": "nonclaim_boundary",
            "claim": "The step is a finite candidate-space enrichment and known-physics calibration, not a value-supplying result.",
            "grade": "organizational",
            "classification": "scope-boundary",
            "scope": "nonclaim",
            "source_artifacts": "steps/step14_real_anomaly_enrichment_artifacts/nonclaim_boundary.md",
        },
    ]
    write_csv(
        "content_classification.csv",
        content_rows,
        ["claim_id", "claim", "grade", "classification", "scope", "source_artifacts"],
    )

    coeff_summary = ", ".join(
        f"{key}={sm_row[key]}"
        for key in ["su3_cubic", "su3_sq_u1", "su2_sq_u1", "u1_cubic", "grav_u1", "su5_cubic"]
    )
    summary = f"""# Step 14 Results Summary: Real Anomaly Enrichment

## Verdict

`real_anomaly_enrichment_limit_recovery_constructed`.

This step replaces the prior toy anomaly score with exact rational anomaly coefficients on a finite curated candidate set of real chiral multiplets. It advances law-landing obligations by faithful enrichment, known-physics limit recovery, a closed-form anomaly-equation relation, and a scoped independently checkable consequence. It remains below law grade.

## SM Limit Recovery

The one-generation SM chiral content is verified anomaly-free:

```text
{coeff_summary}; su2_witten_even={sm_row['su2_witten_even']}
```

This is known physics recovered as a calibration of the enriched carrier.

## Closed-Form Relations

For the fixed one-generation representations with variables `Y_Q, Y_u_c, Y_d_c, Y_L, Y_e_c`, the anomaly equations are:

- `2 Y_Q + Y_u_c + Y_d_c = 0`
- `3 Y_Q + Y_L = 0`
- `6 Y_Q + 3 Y_u_c + 3 Y_d_c + 2 Y_L + Y_e_c = 0`
- `6 Y_Q^3 + 3 Y_u_c^3 + 3 Y_d_c^3 + 2 Y_L^3 + Y_e_c^3 = 0`

Solving gives:

- `Y_L = -3 Y_Q`
- `Y_e_c = 6 Y_Q`
- `{{Y_u_c, Y_d_c}} = {{-4 Y_Q, 2 Y_Q}}`

Choosing the usual up/down labeling and normalization `Y_Q=1/6` gives the familiar pattern `Y_u_c=-2/3`, `Y_d_c=1/3`, `Y_L=-1/2`, `Y_e_c=1`. With `Q_em=T3+Y`, this recovers `Q_proton = - Q_electron`.

## Necessary Not Sufficient

Anomaly-free survivor count: `{survivor_count}`.

Unselected anomaly-free survivor count: `{unselected_count}`.

Survivors:

```text
{', '.join(anomaly_free_ids)}
```

Real anomaly-freedom prunes the finite candidate space but does not uniquely single out the reference content. Non-reference survivors include vector-like refinements, a sterile extension, a normalization-equivalent copy, a label-swapped anomaly solution, and a decomposed SU(5)-style candidate.

## Scoped New Consequence

Most promising next consequence: `{consequence['most_promising_step15_consequence']}`.

How to check it: {consequence['independent_check']}

This is scoped for Step 15. It is not forced in this step.

## Candidate-Law Obligation Status

- Faithful enrichment: advanced.
- Independently checkable consequence: scoped for Step 15.
- Closed-form relation: advanced.
- Limit recovery: advanced.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 14 Nonclaim Boundary

This step is a finite candidate-space enrichment using real anomaly-coefficient formulas.

It recovers known anomaly cancellation and the known hypercharge-ratio family as a calibration of the enriched carrier. This is known physics limit recovery, not a new value-supplying result.

The candidate set is curated and finite. It is not all possible gauge groups, all possible chiral spectra, all possible UV completions, or a physical selection mechanism.

The result does not supply the gauge group, the hypercharge values, generation count, Yukawa texture, electroweak scale, vacuum, or UV completion. It does not provide a law-grade external-review closure, new physics, or frame-transfer certification.

The law-landing obligations are advanced but not complete: the independently checkable consequence is scoped for the next construction step.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    tex = r"""\paragraph{Cluster A Step 14: real anomaly enrichment.}

This step replaces the toy additive anomaly score with exact rational anomaly
coefficients on a finite curated set of real chiral multiplet candidates.  The
reference one-generation content is
\[
Q:(3,2)_{1/6},\quad u^c:(\bar 3,1)_{-2/3},\quad
d^c:(\bar 3,1)_{1/3},\quad L:(1,2)_{-1/2},\quad e^c:(1,1)_1 .
\]

The computed coefficients for this content are all zero:
\[
[SU(3)]^3=0,\quad [SU(3)]^2U(1)=0,\quad [SU(2)]^2U(1)=0,\quad
U(1)^3=0,\quad U(1)\text{-grav}=0 ,
\]
and the number of \(SU(2)\) doublets is even, so the Witten global anomaly is
absent. This is known physics limit recovery, used here as a faithfulness
calibration.

For fixed one-generation representations, the anomaly equations are
\[
2Y_Q+Y_{u^c}+Y_{d^c}=0,\qquad 3Y_Q+Y_L=0,
\]
\[
6Y_Q+3Y_{u^c}+3Y_{d^c}+2Y_L+Y_{e^c}=0,
\]
\[
6Y_Q^3+3Y_{u^c}^3+3Y_{d^c}^3+2Y_L^3+Y_{e^c}^3=0 .
\]
Solving gives
\[
Y_L=-3Y_Q,\qquad Y_{e^c}=6Y_Q,\qquad
\{Y_{u^c},Y_{d^c}\}=\{-4Y_Q,2Y_Q\}.
\]
With the usual up/down labeling and \(Y_Q=1/6\), this recovers the familiar
hypercharge pattern and \(Q_{\mathrm{proton}}=-Q_e\).

The finite candidate space contains anomaly-free non-reference survivors, so
real anomaly freedom remains necessary but not sufficient.  The scoped next
consequence is a minimal irreducible anomaly-cancellation support test over a
larger real candidate enumeration.

\paragraph{Grade.}
Finite-carrier diagnostic and known-physics limit recovery.  No physical SM
value or mechanism is supplied, and frame-transfer remains open.
"""
    (ARTIFACT_DIR / "step14_statement.tex").write_text(tex, encoding="utf-8")

    print(
        "Step 14 built: "
        f"candidates={len(cands)} anomaly_free={survivor_count} unselected={unselected_count}"
    )


if __name__ == "__main__":
    main()
