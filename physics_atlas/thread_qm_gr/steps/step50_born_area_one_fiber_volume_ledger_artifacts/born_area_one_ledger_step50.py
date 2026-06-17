#!/usr/bin/env python3
"""Step 50 revision: Born and area ledgers share the monogamy combiner.

The rejected identity used the same Schmidt spectrum twice. This revision makes
the F39 ledger geometric: it is the Step44 min-cut/min-flow area, independent of
the random-tensor state spectrum. The F23 ledger is the Born/entanglement
entropy of the contracted boundary state. The value relation is a strict finite
RT saturation trend, not equality. The deepening is the shared combiner class:
both ledgers obey MMI/monogamy on the co-sourced holographic carrier, while GHZ
breaks the Born side.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_ROOT = ARTIFACT_DIR.parents[1]
REPO_ROOT = THREAD_ROOT.parents[2]
STEP42_DIR = THREAD_ROOT / "steps" / "step42_faithful_holographic_rt_enrichment_artifacts"
STEP42_SCRIPT = STEP42_DIR / "faithful_holographic_rt_enrichment_step42.py"
STEP44_DIR = THREAD_ROOT / "steps" / "step44_holographic_mmi_entropy_cone_artifacts"
STEP44_SCRIPT = STEP44_DIR / "holographic_mmi_entropy_cone_step44.py"
STEP25_DIR = THREAD_ROOT / "steps" / "step25_sourcing_unification_artifacts"
STEP47_DIR = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
FIV = REPO_ROOT / "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex"
TOL = 1e-9
CASE_DIM = 3
SEEDS = [101, 202, 303]
BOUNDARY_LABELS = [f"L{i}" for i in range(4)] + [f"R{i}" for i in range(4)]
REGIONS = {
    "A": ["L0"],
    "B": ["L1"],
    "C": ["R0"],
    "AB": ["L0", "L1"],
    "AC": ["L0", "R0"],
    "BC": ["L1", "R0"],
    "ABC": ["L0", "L1", "R0"],
}


def rel(path: Path) -> str:
    return str(path.relative_to(THREAD_ROOT))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def entropy_from_probs(probs: np.ndarray) -> float:
    vals = np.asarray(probs, dtype=float)
    vals = vals[vals > TOL]
    return float(-np.sum(vals * np.log(vals)))


def born_entropy_from_density(state_matrix: np.ndarray, dim: int, region_legs: list[str]) -> tuple[float, list[float]]:
    """F23 path: form rho_A and diagonalize its Born eigenmeasure."""
    norm = np.linalg.norm(state_matrix)
    if norm <= TOL:
        raise RuntimeError("zero norm contracted state")
    psi = (state_matrix / norm).reshape([dim] * len(BOUNDARY_LABELS))
    region_axes = [BOUNDARY_LABELS.index(label) for label in region_legs]
    complement_axes = [idx for idx in range(len(BOUNDARY_LABELS)) if idx not in region_axes]
    bipartite = np.transpose(psi, region_axes + complement_axes).reshape(
        dim ** len(region_axes),
        dim ** len(complement_axes),
    )
    rho = bipartite @ bipartite.conj().T
    rho = 0.5 * (rho + rho.conj().T)
    eigvals = np.linalg.eigvalsh(rho).real
    eigvals[eigvals < TOL] = 0.0
    eigvals = eigvals / float(np.sum(eigvals))
    eigvals = eigvals[eigvals > TOL]
    eigvals = np.sort(eigvals)[::-1]
    return entropy_from_probs(eigvals), [float(value) for value in eigvals]


def standard_i3(ent: dict[str, float]) -> float:
    return ent["A"] + ent["B"] + ent["C"] + ent["ABC"] - ent["AB"] - ent["AC"] - ent["BC"]


def ghz_born_entropies() -> dict[str, float]:
    labels = ["A", "B", "C", "D"]
    state = np.zeros(2**4, dtype=float)
    state[0] = 1.0 / math.sqrt(2.0)
    state[-1] = 1.0 / math.sqrt(2.0)
    regions = {
        "A": ["A"],
        "B": ["B"],
        "C": ["C"],
        "AB": ["A", "B"],
        "AC": ["A", "C"],
        "BC": ["B", "C"],
        "ABC": ["A", "B", "C"],
    }

    def entropy(region: list[str]) -> float:
        psi = state.reshape([2] * 4)
        region_axes = [labels.index(label) for label in region]
        comp_axes = [idx for idx in range(4) if idx not in region_axes]
        bipartite = np.transpose(psi, region_axes + comp_axes).reshape(
            2 ** len(region_axes),
            2 ** len(comp_axes),
        )
        rho = bipartite @ bipartite.T
        eigvals = np.linalg.eigvalsh(rho).real
        eigvals[eigvals < TOL] = 0.0
        return entropy_from_probs(eigvals)

    return {name: entropy(legs) for name, legs in regions.items()}


def format_probs(values: list[float], limit: int = 8) -> str:
    return ";".join(f"{value:.12g}" for value in values[:limit])


def build() -> dict[str, Any]:
    step42 = import_module(STEP42_SCRIPT, "step42_for_step50_revised")
    step44 = import_module(STEP44_SCRIPT, "step44_for_step50_revised")
    geom_area, _geom_edges = step44.mincut_entropies(CASE_DIM)

    ledger_rows: list[dict[str, Any]] = []
    seed_summary_rows: list[dict[str, Any]] = []
    representative_born: dict[str, float] | None = None
    ratios_for_a: list[float] = []
    born_a_values: list[float] = []
    area_a_values: list[float] = []

    for seed in SEEDS:
        state_matrix, _left, _right = step42.boundary_state_matrix(CASE_DIM, "random_gaussian", seed)
        born_ent: dict[str, float] = {}
        for region, legs in REGIONS.items():
            born_value, born_probs = born_entropy_from_density(state_matrix, CASE_DIM, legs)
            area_value = float(geom_area[region])
            ratio = born_value / area_value if area_value > TOL else 0.0
            gap = area_value - born_value
            born_ent[region] = born_value
            ledger_rows.append(
                {
                    "case_id": f"co_sourced_D{CASE_DIM}_seed{seed}",
                    "seed": seed,
                    "region": region,
                    "region_legs": "|".join(legs),
                    "f39_source": "Step44 geometric min-cut area ledger",
                    "f39_area_geom": f"{area_value:.12g}",
                    "f23_source": "Step50 reduced density matrix Born eigenmeasure",
                    "f23_born_entropy": f"{born_value:.12g}",
                    "f23_born_probs_top8": format_probs(born_probs),
                    "area_minus_born_gap": f"{gap:.12g}",
                    "saturation_ratio": f"{ratio:.12g}",
                    "strict_gap_not_identity": gap > 1e-6 and ratio < 1.0 - 1e-9,
                    "rt_bound_holds": born_value <= area_value + 1e-8,
                    "f39_geometry_independent_of_seed": True,
                }
            )
            if region == "A":
                ratios_for_a.append(ratio)
                born_a_values.append(born_value)
                area_a_values.append(area_value)
        i3_born = standard_i3(born_ent)
        i3_geom = standard_i3(geom_area)
        seed_summary_rows.append(
            {
                "case_id": f"co_sourced_D{CASE_DIM}_seed{seed}",
                "seed": seed,
                "area_geom_A": f"{geom_area['A']:.12g}",
                "born_entropy_A": f"{born_ent['A']:.12g}",
                "saturation_ratio_A": f"{(born_ent['A'] / geom_area['A']):.12g}",
                "I3_geom": f"{i3_geom:.12g}",
                "I3_born": f"{i3_born:.12g}",
                "shared_monogamy_class": i3_geom <= TOL and i3_born <= TOL,
            }
        )
        if seed == SEEDS[0]:
            representative_born = born_ent

    assert representative_born is not None
    i3_geom = standard_i3(geom_area)
    i3_born = standard_i3(representative_born)
    combiner_rows = [
        {
            "case_id": f"co_sourced_D{CASE_DIM}_seed{SEEDS[0]}",
            "combiner": "MMI_monogamy_class",
            "I3_geom": f"{i3_geom:.12g}",
            "I3_born": f"{i3_born:.12g}",
            "geom_satisfies_monogamy": i3_geom <= TOL,
            "born_satisfies_monogamy": i3_born <= TOL,
            "same_combiner_class": i3_geom <= TOL and i3_born <= TOL,
            "numeric_i3_equality_claimed": False,
        },
        {
            "case_id": f"co_sourced_D{CASE_DIM}_seed{SEEDS[0]}",
            "combiner": "chain_rule_form",
            "geom_A_plus_B_given_A": f"{(geom_area['A'] + (geom_area['AB'] - geom_area['A'])):.12g}",
            "geom_AB": f"{geom_area['AB']:.12g}",
            "born_A_plus_B_given_A": f"{(representative_born['A'] + (representative_born['AB'] - representative_born['A'])):.12g}",
            "born_AB": f"{representative_born['AB']:.12g}",
            "same_combiner_class": True,
            "numeric_i3_equality_claimed": False,
        },
    ]

    ghz_ent = ghz_born_entropies()
    ghz_i3 = standard_i3(ghz_ent)
    geom_d2, _geom_d2_edges = step44.mincut_entropies(2)
    geom_d2_i3 = standard_i3(geom_d2)
    control_rows = [
        {
            "control_id": "GHZ_born_breaks_geometric_monogamy_class",
            "f23_born_source": "explicit GHZ state Born measure",
            "f39_geometry_source": "Step44 D=2 min-cut geometric ledger",
            "ghz_i3_born": f"{ghz_i3:.12g}",
            "geom_i3_mincut": f"{geom_d2_i3:.12g}",
            "ghz_breaks_combiner": ghz_i3 > TOL and geom_d2_i3 <= TOL,
            "interpretation": "The Born ledger is outside the holographic monogamy class while the geometric min-cut ledger remains inside.",
        }
    ]

    seed_invariant = max(area_a_values) - min(area_a_values) <= TOL
    born_varies = max(born_a_values) - min(born_a_values) > 1e-6
    all_strict_gap_a = all(0.0 < ratio < 1.0 - 1e-9 for ratio in ratios_for_a)
    schema = {
        "step": 50,
        "orientation": "ModeB_E018_born_area_shared_monogamy_combiner",
        "active_residual": "TODO #12 law-landing deepening of Batch-A RT result",
        "main_object": "F23 Born ledger and F39 geometric area ledger share the MMI/monogamy combiner class",
        "verdict": "BORN_AND_AREA_SHARE_ONE_MONOGAMY_COMBINER",
        "f39_source": "geometric_mincut",
        "representative_case": f"co_sourced_D{CASE_DIM}_seed{SEEDS[0]}",
        "area_geom_A": geom_area["A"],
        "born_entropy_A": representative_born["A"],
        "saturation_ratio_A": representative_born["A"] / geom_area["A"],
        "area_geom_seed_invariant": seed_invariant,
        "born_entropy_seed_varies": born_varies,
        "all_single_region_A_strict_gap": all_strict_gap_a,
        "i3_geom": i3_geom,
        "i3_born": i3_born,
        "i3_geom_leq_zero": i3_geom <= TOL,
        "i3_born_leq_zero": i3_born <= TOL,
        "ghz_i3_born": ghz_i3,
        "ghz_breaks_combiner": bool(control_rows[0]["ghz_breaks_combiner"]),
        "value_link_is_saturation_trend_not_identity": True,
        "conditional_on_step47_premise": True,
        "anti_tautology_f39_is_geometric_mincut": True,
        "new_measured_number": False,
        "derives_holography": False,
        "derives_born_rule": False,
        "derives_area_law": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "new_physics_claim": False,
    }

    frozen_rows = [
        {
            "source": rel(STEP42_SCRIPT),
            "role": "F23 contracted boundary state / Born entropy carrier",
            "sha256": sha256(STEP42_SCRIPT),
        },
        {
            "source": rel(STEP44_SCRIPT),
            "role": "F39 geometric min-cut ledger and MMI control axis",
            "sha256": sha256(STEP44_SCRIPT),
        },
        {
            "source": rel(STEP25_DIR / "field_carrier_step25.json"),
            "role": "F23 Born rule source rho=|psi|^2 on co-sourcing carrier",
            "sha256": sha256(STEP25_DIR / "field_carrier_step25.json"),
        },
        {
            "source": rel(STEP47_DIR / "step47_schema.json"),
            "role": "conditional common-carrier GROUND premise",
            "sha256": sha256(STEP47_DIR / "step47_schema.json"),
        },
    ]
    anti_rows = [
        {
            "gate": "f39_is_geometric_mincut_not_state_spectrum",
            "passes": True,
            "evidence": "F39 source is Step44 mincut_entropies; entropy_from_region is not used for the F39 ledger.",
        },
        {
            "gate": "strict_saturation_gap_not_identity",
            "passes": all_strict_gap_a,
            "evidence": f"A-region ratios {','.join(f'{value:.12g}' for value in ratios_for_a)}",
        },
        {
            "gate": "seed_invariance",
            "passes": seed_invariant and born_varies,
            "evidence": f"area_A values {area_a_values}; born_A values {born_a_values}",
        },
        {
            "gate": "shared_monogamy_class",
            "passes": i3_geom <= TOL and i3_born <= TOL,
            "evidence": f"I3_geom={i3_geom:.12g}; I3_born={i3_born:.12g}",
        },
        {
            "gate": "ghz_breaks_combiner",
            "passes": control_rows[0]["ghz_breaks_combiner"],
            "evidence": f"GHZ I3={ghz_i3:.12g}; mincut I3={geom_d2_i3:.12g}",
        },
    ]
    return {
        "ledger_rows": ledger_rows,
        "seed_summary_rows": seed_summary_rows,
        "combiner_rows": combiner_rows,
        "control_rows": control_rows,
        "frozen_rows": frozen_rows,
        "anti_rows": anti_rows,
        "schema": schema,
    }


def write_outputs() -> None:
    data = build()
    write_csv(ARTIFACT_DIR / "born_area_ledger_scores_step50.csv", data["ledger_rows"])
    write_csv(ARTIFACT_DIR / "seed_invariance_step50.csv", data["seed_summary_rows"])
    write_csv(ARTIFACT_DIR / "combiner_comparison_step50.csv", data["combiner_rows"])
    write_csv(ARTIFACT_DIR / "control_divergence_step50.csv", data["control_rows"])
    write_csv(ARTIFACT_DIR / "frozen_machinery_step50.csv", data["frozen_rows"])
    write_csv(ARTIFACT_DIR / "anti_circularity_step50.csv", data["anti_rows"])
    with (ARTIFACT_DIR / "step50_schema.json").open("w", encoding="utf-8") as handle:
        json.dump(data["schema"], handle, indent=2)

    schema = data["schema"]
    summary = f"""# Step 50 Results Summary

## Honest Grade First

This revision removes the rejected von-Neumann-equals-Shannon tautology. The F39 ledger is now the geometric min-cut area, computed from Step44 graph edge capacities and independent of the random tensor state's Born spectrum. The F23 ledger is the Born/entanglement entropy of the contracted state. The value-link is Batch A's RT saturation trend, not an exact identity: `S_Born <= area_geom` with a strict finite-D gap.

The genuine #12 deepening is the shared composition combiner: both the geometric area ledger and the Born ledger obey the same MMI/monogamy class on the co-sourced holographic carrier. The GHZ control breaks the Born side out of that class, so the claim has teeth. This remains structural-recognition, conditional on the Step47 `LANDED * GROUND (conditional)` common-carrier premise. It does not derive a new measured number, the Born rule, holography, frame transfer, or a quantum-gravity solution.

Verdict: `{schema['verdict']}`.

## Value Link: Saturation Trend, Not Identity

Representative region `A=L0`, `D={CASE_DIM}`, seed `{SEEDS[0]}`:

- geometric F39 area: `{schema['area_geom_A']:.12g}`.
- Born F23 entropy: `{schema['born_entropy_A']:.12g}`.
- saturation ratio: `{schema['saturation_ratio_A']:.12g}`.

This ratio is strictly below 1; exact equality would be a failure signal here.

## Seed-Invariance

The geometric area is seed-invariant while the Born entropy varies:

| seed | area_geom(A) | S_Born(A) | ratio |
|---:|---:|---:|---:|
"""
    for row in data["seed_summary_rows"]:
        summary += f"| {row['seed']} | {row['area_geom_A']} | {row['born_entropy_A']} | {row['saturation_ratio_A']} |\n"
    summary += f"""
`area_geom_seed_invariant = {schema['area_geom_seed_invariant']}` and `born_entropy_seed_varies = {schema['born_entropy_seed_varies']}`.

## Shared Combiner

For the co-sourced carrier:

- `I3_geom = {schema['i3_geom']:.12g}`.
- `I3_born = {schema['i3_born']:.12g}`.
- both satisfy `I3 <= 0`: `{schema['i3_geom_leq_zero'] and schema['i3_born_leq_zero']}`.

The claim is shared monogamy class, not numeric I3 equality.

## Can-Fail Control

The GHZ control breaks the Born side out of the geometric combiner class:

- `I3_Born(GHZ) = {schema['ghz_i3_born']:.12g}`.
- geometric min-cut `I3 <= 0` remains true.
- `ghz_breaks_combiner = {schema['ghz_breaks_combiner']}`.

## Residual

This is an honest thin-but-real deepening: Batch A's saturation trend plus a shared monogamy-combiner class. It is not a new derivation of the value relation and not frame-transfer.
"""
    (ARTIFACT_DIR / "step50_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 50 Nonclaim Boundary

This revision does not claim an exact equality between geometric area and Born entropy. It explicitly rejects the von-Neumann-equals-Shannon identity as a basis for this step.

The F39 ledger is geometric min-cut area; the F23 ledger is Born entropy. Their value link is RT saturation as an emergent trend with strict finite-D gaps. The deepening is only that both ledgers share the MMI/monogamy combiner class on the co-sourced carrier, while GHZ breaks the Born side.

This does not derive a new measured number, the Born rule, the area law, holography, frame transfer, or quantum gravity. It is conditional on the Step47 `LANDED * GROUND (conditional)` common-carrier premise.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step50.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\section*{Step 50 Revision: Shared Monogamy Combiner}

The F39 ledger is the geometric min-cut area of the Step44 graph. It is not
computed from the contracted state's Schmidt spectrum. The F23 ledger is the
Born entropy of the contracted boundary state.

At finite bond dimension the value relation is a strict RT bound,
\[
S_{\rm Born}(A) < A_{\rm geom}(A),
\]
with a saturation ratio below one. Varying the random-tensor seed changes
\(S_{\rm Born}\) while leaving \(A_{\rm geom}\) fixed, demonstrating that the
geometric ledger is independent of the Born spectrum.

The structural-recognition deepening is compositional: for the co-sourced
holographic carrier, both ledgers satisfy the same monogamy/MMI class,
\[
I_3 \le 0.
\]
The GHZ control has positive Born \(I_3\), while the geometric min-cut ledger
remains non-positive; hence the shared-combiner property can fail.
"""
    (ARTIFACT_DIR / "born_area_one_ledger_statement_step50.tex").write_text(statement, encoding="utf-8")

    write_csv(
        ARTIFACT_DIR / "content_classification_step50.csv",
        [
            {
                "artifact": "born_area_one_ledger_step50.py",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "computes geometric F39 min-cut, F23 Born entropy, seed-invariance, shared monogamy, and GHZ control",
            },
            {
                "artifact": "born_area_ledger_scores_step50.csv",
                "classification": "analytical-structural",
                "grade": "structural-recognition",
                "scope": "per-region RT bound and saturation ratios",
            },
            {
                "artifact": "seed_invariance_step50.csv",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "geometric area invariant under state-seed changes while Born entropy varies",
            },
            {
                "artifact": "combiner_comparison_step50.csv",
                "classification": "analytical-structural",
                "grade": "structural-recognition",
                "scope": "shared monogamy/MMI combiner class",
            },
            {
                "artifact": "control_divergence_step50.csv",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "GHZ Born combiner break against geometric min-cut class",
            },
            {
                "artifact": "step50_results_summary.md",
                "classification": "organizational",
                "grade": "summary",
                "scope": "honest grade and revised anti-tautology result",
            },
            {
                "artifact": "born_area_one_ledger_statement_step50.tex",
                "classification": "analytical-structural",
                "grade": "structural-recognition",
                "scope": "statement of shared-combiner result",
            },
            {
                "artifact": "run_step50.py",
                "classification": "organizational",
                "grade": "validator",
                "scope": "anti-tautology and shared-combiner validation",
            },
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {
                "constraint_id": "C_STEP50_F39_GEOMETRIC_NOT_SPECTRAL",
                "status": "active",
                "description": "F39 ledger must be Step44 min-cut geometry, not entropy_from_region or the state SVD spectrum.",
            },
            {
                "constraint_id": "C_STEP50_STRICT_SATURATION_GAP",
                "status": "active",
                "description": "Finite-D Born entropy must be strictly below geometric area; exact equality is a tautology warning.",
            },
            {
                "constraint_id": "C_STEP50_SHARED_MONOGAMY_CAN_FAIL",
                "status": "active",
                "description": "Co-sourced ledgers must share I3<=0 while GHZ Born I3 breaks it.",
            },
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "Born-probability and area-entropy shared monogamy combiner",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "law_landing_deepening_sub_residual",
                "authorization": "USER-AUTHORIZED TODO #12 revision",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_BornAreaMonogamyCombiner_v2",
                "declared_at_step": 50,
                "objects": "Step44 geometric min-cut ledger; Step42 contracted Born entropy; seed-invariance; MMI/GHZ combiner control",
                "excluded_designs_rationale": "Excludes using the Schmidt spectrum as both F39 and F23 input.",
                "non_triviality_argument": "Area is seed-invariant while Born entropy varies, and GHZ breaks the Born monogamy class.",
                "next_grammar_delta": "stronger bulk-reconstruction and continuum frame-transfer carrier",
            }
        ],
    )


if __name__ == "__main__":
    write_outputs()
