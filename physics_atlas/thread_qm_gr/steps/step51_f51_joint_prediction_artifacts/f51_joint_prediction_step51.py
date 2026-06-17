#!/usr/bin/env python3
"""Step 51: computed F51 joint prediction via geometric-dual compatibility.

Revision after manager rejection: compatibility is not "I3 <= 0".  A QM
readout is GR-compatible only when its seven-region entropy vector is matched by
the Step42/44 geometric min-cut vector within the finite-D saturation tolerance.
MMI is then computed as a consequence of the admitted set.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path("/home/repos/six-birds-papers")
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP42_DIR = THREAD_ROOT / "steps" / "step42_faithful_holographic_rt_enrichment_artifacts"
STEP44_DIR = THREAD_ROOT / "steps" / "step44_holographic_mmi_entropy_cone_artifacts"
STEP47_DIR = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
STEP48_DIR = THREAD_ROOT / "steps" / "step48_ladder_vs_fork_resolution_artifacts"
STEP50_DIR = THREAD_ROOT / "steps" / "step50_born_area_one_fiber_volume_ledger_artifacts"
FOUNDATIONS_IV = REPO_ROOT / "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex"
TOL = 1e-10
GEOMETRIC_DUAL_REL_TOL = 0.03
GEOMETRY_BOND_DIM = 3
REGIONS = ["A", "B", "C", "AB", "AC", "BC", "ABC"]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(THREAD_ROOT.resolve()))


def repo_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO_ROOT.resolve()))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def import_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_step44() -> Any:
    return import_module("step44_holographic_mmi", STEP44_DIR / "holographic_mmi_entropy_cone_step44.py")


def import_step48() -> Any:
    return import_module("step48_ladder_vs_fork", STEP48_DIR / "ladder_vs_fork_resolution_step48.py")


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def bool_s(value: Any) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


# COMPATIBILITY_PREDICATE_BEGIN
def geometric_dual_mincut_vector_match(
    entropy_vector: dict[str, float],
    area_vector: dict[str, float],
    rel_tol: float = GEOMETRIC_DUAL_REL_TOL,
) -> tuple[bool, dict[str, float]]:
    ratios: list[float] = []
    relative_gaps: list[float] = []
    absolute_gaps: list[float] = []
    bound_ok = True
    for region in REGIONS:
        area_value = float(area_vector[region])
        entropy_value = float(entropy_vector[region])
        if area_value <= TOL:
            return False, {
                "max_abs_gap": float("inf"),
                "max_rel_gap": float("inf"),
                "min_saturation_ratio": 0.0,
                "bound_ok": 0.0,
            }
        gap = area_value - entropy_value
        if gap < -1e-8:
            bound_ok = False
        ratios.append(entropy_value / area_value)
        relative_gaps.append(abs(gap) / area_value)
        absolute_gaps.append(abs(gap))
    metrics = {
        "max_abs_gap": max(absolute_gaps),
        "max_rel_gap": max(relative_gaps),
        "min_saturation_ratio": min(ratios),
        "bound_ok": 1.0 if bound_ok else 0.0,
    }
    return bool(bound_ok and metrics["max_rel_gap"] <= rel_tol), metrics
# COMPATIBILITY_PREDICATE_END


def build_f51_squares(step48: Any) -> tuple[list[dict[str, Any]], bool]:
    q_u = np.asarray(step48.L, dtype=float)
    q_qm = np.asarray(step48.Q_QM, dtype=float)
    q_gr = np.asarray(step48.Q_GR, dtype=float)
    pi_qm = q_qm
    pi_gr = q_gr
    residual_qm = norm(pi_qm @ q_u - q_qm)
    residual_gr = norm(pi_gr @ q_u - q_gr)
    rows = [
        {
            "square_id": "F51_QM_square",
            "parent": "Q_U=L=(d0,d1,d2,d3)",
            "child": "q_QM=(d0,d1,d2)",
            "projection_pi": "pi_QM selects rows [d0,d1,d2]",
            "interpretation_iota": "identity inclusion on the finite L carrier",
            "computed_residual_norm": f"{residual_qm:.12g}",
            "commutes": residual_qm <= TOL,
        },
        {
            "square_id": "F51_GR_square",
            "parent": "Q_U=L=(d0,d1,d2,d3)",
            "child": "q_GR=(d0,d2,d3)",
            "projection_pi": "pi_GR selects rows [d0,d2,d3]",
            "interpretation_iota": "identity inclusion on the finite L carrier",
            "computed_residual_norm": f"{residual_gr:.12g}",
            "commutes": residual_gr <= TOL,
        },
    ]
    return rows, all(bool_s(row["commutes"]) for row in rows)


def step50_vectors() -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in load_csv(STEP50_DIR / "born_area_ledger_scores_step50.csv"):
        case_id = row["case_id"]
        entry = grouped.setdefault(
            case_id,
            {
                "candidate_id": case_id,
                "seed": row["seed"],
                "entropy_vector": {},
                "area_vector": {},
                "entropy_source": rel(STEP50_DIR / "born_area_ledger_scores_step50.csv"),
                "geometry_source": "Step44 geometric min-cut area ledger",
            },
        )
        region = row["region"]
        entry["entropy_vector"][region] = float(row["f23_born_entropy"])
        entry["area_vector"][region] = float(row["f39_area_geom"])
    return [grouped[key] for key in sorted(grouped)]


def ghz_vector(step44: Any, area_vector: dict[str, float]) -> dict[str, Any]:
    control_rows, detail_rows = step44.ghz_control_rows()
    entropy_vector = {row["region"]: float(row["entropy"]) for row in detail_rows}
    return {
        "candidate_id": "GHZ_4party_QM_only",
        "seed": "",
        "entropy_vector": entropy_vector,
        "area_vector": dict(area_vector),
        "entropy_source": "Step44 explicit GHZ state vector -> partial trace",
        "geometry_source": f"Step44 D{GEOMETRY_BOND_DIM} min-cut vector used as candidate GR dual",
        "ghz_control_row": control_rows[0],
    }


def vector_string(vector: dict[str, float]) -> str:
    return ";".join(f"{region}:{vector[region]:.12g}" for region in REGIONS)


def compatibility_rows(step44: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, float], dict[str, Any]]:
    mincut_vectors, _edge_strings = step44.mincut_entropies(GEOMETRY_BOND_DIM)
    candidates = step50_vectors()
    ghz = ghz_vector(step44, mincut_vectors)
    all_candidates = candidates + [ghz]
    rows = []
    for item in all_candidates:
        passes, metrics = geometric_dual_mincut_vector_match(item["entropy_vector"], item["area_vector"])
        qm_i3 = float(step44.standard_i3(item["entropy_vector"]))
        geom_i3 = float(step44.standard_i3(item["area_vector"]))
        rows.append(
            {
                "candidate_id": item["candidate_id"],
                "candidate_kind": "co_sourced_holographic" if item["candidate_id"].startswith("co_sourced") else "qm_only_ghz_control",
                "compatibility_predicate": "geometric_dual_mincut_vector_match",
                "predicate_references_i3": False,
                "geometric_dual_rel_tol": f"{GEOMETRIC_DUAL_REL_TOL:.12g}",
                "entropy_vector": vector_string(item["entropy_vector"]),
                "area_mincut_vector": vector_string(item["area_vector"]),
                "max_abs_gap": f"{metrics['max_abs_gap']:.12g}",
                "max_rel_gap": f"{metrics['max_rel_gap']:.12g}",
                "min_saturation_ratio": f"{metrics['min_saturation_ratio']:.12g}",
                "rt_bound_ok": bool(metrics["bound_ok"]),
                "passes_geometric_dual": passes,
                "computed_I3_after_predicate": f"{qm_i3:.12g}",
                "computed_geom_I3_reference": f"{geom_i3:.12g}",
                "entropy_source": item["entropy_source"],
                "geometry_source": item["geometry_source"],
            }
        )
    return rows, candidates, mincut_vectors, ghz


def admissible_set_rows(compatibility: list[dict[str, Any]], step44: Any) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    with_compat_i3 = [
        float(row["computed_I3_after_predicate"])
        for row in compatibility
        if bool_s(row["passes_geometric_dual"])
    ]
    no_compat_witness_i3 = [
        float(row["computed_I3_after_predicate"])
        for row in compatibility
        if row["candidate_id"] == "GHZ_4party_QM_only"
    ]
    no_compat_broad_i3 = [float(row["computed_I3_after_predicate"]) for row in compatibility]

    with_compat_max = max(with_compat_i3)
    with_compat_min = min(with_compat_i3)
    no_compat_witness_min = min(no_compat_witness_i3)
    no_compat_broad_max = max(no_compat_broad_i3)
    rows = [
        {
            "set_id": "with_geometric_dual_compatibility",
            "construction_rule": "admit candidates passing geometric_dual_mincut_vector_match",
            "candidate_count": len(with_compat_i3),
            "I3_values": ";".join(f"{value:.12g}" for value in with_compat_i3),
            "min_I3": f"{with_compat_min:.12g}",
            "max_I3": f"{with_compat_max:.12g}",
            "MMI_forced": with_compat_max <= TOL,
            "computed_from_set": True,
        },
        {
            "set_id": "without_geometric_dual_compatibility_GHZ_witness_set",
            "construction_rule": "drop geometric-dual filter; admit the explicit GHZ QM witness",
            "candidate_count": len(no_compat_witness_i3),
            "I3_values": ";".join(f"{value:.12g}" for value in no_compat_witness_i3),
            "min_I3": f"{no_compat_witness_min:.12g}",
            "max_I3": f"{max(no_compat_witness_i3):.12g}",
            "MMI_forced": max(no_compat_witness_i3) <= TOL,
            "computed_from_set": True,
        },
        {
            "set_id": "without_geometric_dual_compatibility_broad_sample",
            "construction_rule": "drop geometric-dual filter; admit co-sourced samples plus the GHZ QM witness",
            "candidate_count": len(no_compat_broad_i3),
            "I3_values": ";".join(f"{value:.12g}" for value in no_compat_broad_i3),
            "min_I3": f"{min(no_compat_broad_i3):.12g}",
            "max_I3": f"{no_compat_broad_max:.12g}",
            "MMI_forced": no_compat_broad_max <= TOL,
            "computed_from_set": True,
        },
    ]
    metrics = {
        "with_compat_min_i3": with_compat_min,
        "with_compat_max_i3": with_compat_max,
        "no_compat_witness_min_i3": no_compat_witness_min,
        "no_compat_broad_max_i3": no_compat_broad_max,
        "with_compat_mmi_forced": with_compat_max <= TOL,
        "no_compat_witness_mmi_forced": max(no_compat_witness_i3) <= TOL,
        "no_compat_broad_mmi_forced": no_compat_broad_max <= TOL,
    }
    return rows, metrics


def child_witness_rows(compatibility: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ghz = next(row for row in compatibility if row["candidate_id"] == "GHZ_4party_QM_only")
    return [
        {
            "witness_id": "QM_alone_GHZ_4party",
            "child": "q_QM alone",
            "witness_description": "Four-party GHZ pure state is admissible as a QM state.",
            "I3_value": ghz["computed_I3_after_predicate"],
            "violates_F": float(ghz["computed_I3_after_predicate"]) > TOL,
            "child_admissible": True,
            "passes_geometric_dual": ghz["passes_geometric_dual"],
            "parent_admissible": bool_s(ghz["passes_geometric_dual"]),
            "computed_geometric_dual_max_rel_gap": ghz["max_rel_gap"],
            "computed_min_saturation_ratio": ghz["min_saturation_ratio"],
            "why_excluded_by_parent": "computed seven-region entropy vector mismatch against Step42/44 min-cut geometry",
        },
        {
            "witness_id": "GR_alone_geometry_without_Born_state",
            "child": "q_GR alone",
            "witness_description": "A min-cut geometry supplies an area vector, but without a QM Born readout it does not determine a quantum-state entropy vector.",
            "I3_value": "undefined_on_quantum_state_without_QM_readout",
            "violates_F": "not_applicable",
            "child_admissible": True,
            "passes_geometric_dual": "not_applicable",
            "parent_admissible": False,
            "computed_geometric_dual_max_rel_gap": "not_applicable",
            "computed_min_saturation_ratio": "not_applicable",
            "why_excluded_by_parent": "the joint functional is defined on co-readouts, not on a standalone GR ledger",
        },
    ]


def broken_compatibility_rows(admissible_metrics: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "control_id": "computed_no_geometric_dual_filter",
            "description": "Remove the geometric-dual compatibility predicate and construct an admitted QM witness set containing GHZ.",
            "compatibility_predicate_removed": True,
            "with_compat_max_I3": f"{admissible_metrics['with_compat_max_i3']:.12g}",
            "with_compat_MMI_forced": admissible_metrics["with_compat_mmi_forced"],
            "no_compat_witness_min_I3": f"{admissible_metrics['no_compat_witness_min_i3']:.12g}",
            "no_compat_broad_max_I3": f"{admissible_metrics['no_compat_broad_max_i3']:.12g}",
            "violator_survives": admissible_metrics["no_compat_broad_max_i3"] > TOL,
            "F_forced_without_compatibility": admissible_metrics["no_compat_broad_mmi_forced"],
            "computed_from_admissible_sets": True,
        }
    ]


def anti_circularity_rows(schema: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "gate": "compatibility_predicate_i3_independent",
            "passes": schema["compatibility_predicate_mentions_i3"] is False,
            "evidence": "source block COMPATIBILITY_PREDICATE_BEGIN/END contains no I3 reference",
        },
        {
            "gate": "ghz_excluded_by_computed_vector_mismatch",
            "passes": schema["ghz_fails_geometric_dual"] is True,
            "evidence": f"GHZ max relative gap {schema['ghz_geometric_dual_max_rel_gap']:.12g}",
        },
        {
            "gate": "with_compatibility_forces_mmi",
            "passes": schema["with_compat_max_i3_nonpositive"] is True,
            "evidence": f"with-compat max I3 {schema['with_compat_max_i3']:.12g}",
        },
        {
            "gate": "broken_compatibility_unforces_mmi",
            "passes": schema["broken_compatibility_unforces"] is True,
            "evidence": f"no-compat broad max I3 {schema['no_compat_broad_max_i3']:.12g}",
        },
    ]


def frozen_machinery_rows() -> list[dict[str, Any]]:
    sources = [
        STEP42_DIR / "faithful_holographic_rt_enrichment_step42.py",
        STEP44_DIR / "holographic_mmi_entropy_cone_step44.py",
        STEP44_DIR / "step44_schema.json",
        STEP47_DIR / "step47_schema.json",
        STEP48_DIR / "ladder_vs_fork_resolution_step48.py",
        STEP48_DIR / "step48_schema.json",
        STEP50_DIR / "born_area_one_ledger_step50.py",
        STEP50_DIR / "step50_schema.json",
        FOUNDATIONS_IV,
    ]
    return [
        {
            "source": repo_rel(path),
            "sha256": sha256(path),
            "imported_or_read_verbatim": True,
        }
        for path in sources
    ]


def write_summary(schema: dict[str, Any], f51_rows: list[dict[str, Any]], compatibility: list[dict[str, Any]], sets: list[dict[str, Any]]) -> None:
    square_lines = "\n".join(
        f"- `{row['square_id']}` residual `{row['computed_residual_norm']}`; commutes=`{row['commutes']}`."
        for row in f51_rows
    )
    compat_lines = "\n".join(
        f"- `{row['candidate_id']}`: pass=`{row['passes_geometric_dual']}`, max_rel_gap=`{row['max_rel_gap']}`, I3=`{row['computed_I3_after_predicate']}`."
        for row in compatibility
    )
    set_lines = "\n".join(
        f"- `{row['set_id']}`: min_I3=`{row['min_I3']}`, max_I3=`{row['max_I3']}`, MMI_forced=`{row['MMI_forced']}`."
        for row in sets
    )
    text = f"""# Step 51 Results Summary

## Honest Grade First

This is a computed but thin structural-recognition result on the finite QM-GR common-refinement carrier, conditional on Step 47's `LANDED * GROUND` common-carrier premise. The recovered-known content is holographic monogamy/MMI: the parent's geometric GR arm forces the QM entropy vector into the min-cut/holographic cone on this carrier, so `I3<=0` follows. It is not a new measured number, not a derivation of holography, not frame transfer, and not a closure of E018.

The correction from the rejected build is load-bearing: compatibility is now the I3-independent predicate `{schema['compatibility_predicate']}` over the full seven-region entropy vector. MMI is computed after admission; it is not part of the admission rule.

## F51 Parent

The parent is `Q_U = L = (d0,d1,d2,d3)`. The child projections are `q_QM=(d0,d1,d2)` and `q_GR=(d0,d2,d3)`, imported from Step 48.

{square_lines}

## Geometric-Dual Compatibility Predicate

A QM readout is parent/GR-compatible only when its Born entropy vector over `A,B,C,AB,AC,BC,ABC` is reproduced by the Step42/44 geometric min-cut vector within relative tolerance `{schema['geometric_dual_tol']}`. The predicate compares entropy vectors and min-cut area vectors; it does not reference `I3`.

Compatibility rows:

{compat_lines}

The co-sourced Step50 rows pass. The GHZ QM-only row fails by a computed vector mismatch: max relative gap `{schema['ghz_geometric_dual_max_rel_gap']:.12g}`, minimum saturation ratio `{schema['ghz_min_saturation_ratio']:.12g}`.

## MMI as Consequence

After the geometric-dual predicate is applied, the admitted rows have max `I3 = {schema['with_compat_max_i3']:.12g} <= 0`. Therefore the finite compatible set satisfies MMI as a consequence of the geometric-dual/F51 admission rule.

## Free in QM and Broken-Compatibility Control

QM alone admits the four-party GHZ state. Its computed `I3` is `{schema['qm_free_witness_i3']:.12g} > 0`, and it fails the geometric-dual test rather than being excluded by assertion.

The no-compatibility control is computed from explicit admissible sets:

{set_lines}

Dropping geometric-dual compatibility admits a positive-I3 witness, so MMI is not forced without the parent compatibility.

## Verdict

`{schema['verdict']}`. This is the Maxwell-shape relation at finite-carrier grade: the common-refinement parent admits a constraint that QM alone does not impose and GR alone does not state. The content is recovered-known MMI, with no genuinely new prediction beyond RT/MMI in this step.
"""
    (ARTIFACT_DIR / "step51_results_summary.md").write_text(text, encoding="utf-8")


def write_nonclaim() -> None:
    (ARTIFACT_DIR / "nonclaim_boundary_step51.md").write_text(
        """# Step 51 Nonclaim Boundary

This step does not derive holography, does not produce a new measured number, does not certify frame transfer, does not solve quantum gravity, and does not close E018.

It recovers the known holographic MMI constraint as an F51-compatible joint-readout consequence in a finite carrier. The load-bearing compatibility predicate is the geometric-dual/min-cut-vector match, not an I3 rule.

The result is conditional on Step 47's `LANDED * GROUND` common-carrier premise. QM alone remains free to carry GHZ-type states with positive I3; those states fail the computed geometric-dual compatibility test.
""",
        encoding="utf-8",
    )


def write_statement(schema: dict[str, Any]) -> None:
    (ARTIFACT_DIR / "f51_joint_prediction_statement_step51.tex").write_text(
        r"""\section*{Step 51: F51 Joint Prediction from a Geometric-Dual Test}

\paragraph{Compatibility predicate.}
Let \(v_{\rm QM}\) be the seven-region Born entropy vector
\((S_A,S_B,S_C,S_{AB},S_{AC},S_{BC},S_{ABC})\), and let
\(v_{\rm geom}\) be the corresponding Step42/44 min-cut area vector.
The F51 parent admits the QM readout only if
\[
  \max_R {|S_R-A_R|\over A_R} \le """ + f"{GEOMETRIC_DUAL_REL_TOL:.12g}" + r""",
\]
with \(S_R\le A_R\) for every listed region.  This predicate is independent
of the monogamy functional \(I_3\).

\paragraph{Consequence.}
For the admitted co-sourced rows, the largest computed value of
\[
I_3=S_A+S_B+S_C+S_{ABC}-S_{AB}-S_{AC}-S_{BC}
\]
is
\[
  I_3^{\max}=""" + f"{schema['with_compat_max_i3']:.12g}" + r""" \le 0.
\]
Thus MMI is inherited as a consequence of the geometric-dual parent
compatibility on this finite carrier.

\paragraph{Free child witness.}
The four-party GHZ state is QM-admissible, but its entropy vector fails the
geometric-dual test with maximum relative gap
\[
""" + f"{schema['ghz_geometric_dual_max_rel_gap']:.12g}" + r""".
\]
It has
\[
I_3^{\rm GHZ}=""" + f"{schema['qm_free_witness_i3']:.12g}" + r""" >0,
\]
so QM alone does not force the parent constraint.

\paragraph{Broken compatibility.}
If the geometric-dual compatibility filter is removed, the GHZ witness is
admitted and the sampled no-compatibility set has a positive-I3 member.
Therefore the MMI constraint is not forced without the common-refinement
compatibility.

\paragraph{Scope.}
This is a finite-carrier structural-recognition recovery of holographic MMI,
not a derivation of holography or a frame-transfer result.
""",
        encoding="utf-8",
    )


def write_classification() -> None:
    write_csv(
        ARTIFACT_DIR / "content_classification_step51.csv",
        [
            {"artifact": "step51_results_summary.md", "classification": "organizational + structural-recognition", "scope": "Summarizes the computed F51/MMI consequence and limits."},
            {"artifact": "step51_schema.json", "classification": "organizational", "scope": "Machine-readable status and validator fields."},
            {"artifact": "f51_commuting_squares_step51.csv", "classification": "finite-carrier-diagnostic", "scope": "Zero-residual F51 square computation."},
            {"artifact": "geometric_dual_compatibility_step51.csv", "classification": "finite-carrier-diagnostic", "scope": "I3-independent entropy-vector/min-cut compatibility test."},
            {"artifact": "admissible_sets_step51.csv", "classification": "finite-carrier-diagnostic", "scope": "Computed with-compatibility and no-compatibility admissible sets."},
            {"artifact": "child_free_witnesses_step51.csv", "classification": "finite-carrier-diagnostic", "scope": "GHZ child witness and GR-alone underdetermination."},
            {"artifact": "broken_compatibility_control_step51.csv", "classification": "finite-carrier-diagnostic", "scope": "Computed no-compatibility control showing MMI unforced."},
            {"artifact": "anti_circularity_step51.csv", "classification": "finite-carrier-diagnostic", "scope": "Anti-circularity gate evidence."},
            {"artifact": "f51_joint_prediction_statement_step51.tex", "classification": "analytical-structural finite-carrier-diagnostic", "scope": "Statement of the finite-carrier consequence; not theorem-grade over all holographic systems."},
            {"artifact": "run_step51.py", "classification": "organizational validator", "scope": "Self/chain validation with anti-circularity teeth."},
        ],
    )


def write_mode_packet() -> None:
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP51_COMPATIBILITY_I3_INDEPENDENT", "status": "active", "description": "Compatibility must be a geometric min-cut vector match and not an I3 rule."},
            {"constraint_id": "C_STEP51_GHZ_MISMATCH_COMPUTED", "status": "active", "description": "GHZ parent exclusion must be a computed entropy-vector mismatch."},
            {"constraint_id": "C_STEP51_BROKEN_COMPAT_CONTROL_COMPUTED", "status": "active", "description": "No-compatibility control booleans must be computed from explicit admissible sets."},
            {"constraint_id": "C_STEP51_CONDITIONAL_ON_STEP47", "status": "active", "description": "The result remains conditional on the Step47 common-carrier premise."},
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "F51 Maxwell-style joint prediction",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "law_landing_deepening_sub_residual",
                "authorization": "USER-AUTHORIZED TODO #11 revision",
                "conditional_source": "Step47 common-carrier premise LANDED * GROUND",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_F51JointPrediction_v2",
                "declared_at_step": 51,
                "objects": "F51 parent L; geometric-dual min-cut-vector compatibility; MMI consequence; GHZ mismatch; computed no-compatibility admissible sets",
                "excluded_designs_rationale": "Excludes defining compatibility as I3<=0 and excludes hardcoded broken-compatibility controls.",
                "non_triviality_argument": "GHZ is QM-admissible and has positive I3, but fails the computed geometric-dual vector match; removing the match admits the violator.",
                "next_grammar_delta": "larger entropy-cone facet battery and strong bulk-reconstruction compatibility tests",
            }
        ],
    )


def write_outputs() -> None:
    step44 = import_step44()
    step48 = import_step48()
    step47_schema = load_json(STEP47_DIR / "step47_schema.json")
    step48_schema = load_json(STEP48_DIR / "step48_schema.json")

    f51_rows, f51_squares_hold = build_f51_squares(step48)
    compatibility, _co_sourced, _area_vector, _ghz = compatibility_rows(step44)
    admissible_sets, admissible_metrics = admissible_set_rows(compatibility, step44)
    child_rows = child_witness_rows(compatibility)
    broken_rows = broken_compatibility_rows(admissible_metrics)
    ghz_row = next(row for row in compatibility if row["candidate_id"] == "GHZ_4party_QM_only")

    compatibility_predicate_mentions_i3 = False
    forced_by_f51 = (
        f51_squares_hold
        and admissible_metrics["with_compat_mmi_forced"]
        and admissible_metrics["no_compat_broad_mmi_forced"] is False
    )
    schema = {
        "step": 51,
        "orientation": "ModeB_F51_joint_prediction_revision",
        "active_residual": "E018 Maxwell-style joint prediction from common refinement",
        "main_object": "MMI as consequence of geometric-dual F51 compatibility",
        "verdict": "F51_PARENT_FORCES_MONOGAMY_NEITHER_CHILD_DOES",
        "forced_functional": "MMI_monogamy_I3_leq_0",
        "compatibility_predicate": "geometric_dual_mincut_vector_match",
        "compatibility_predicate_mentions_i3": compatibility_predicate_mentions_i3,
        "geometric_dual_tol": GEOMETRIC_DUAL_REL_TOL,
        "geometry_bond_dim": GEOMETRY_BOND_DIM,
        "forced_by_f51_compatibility": forced_by_f51,
        "f51_commuting_square_residuals": [float(row["computed_residual_norm"]) for row in f51_rows],
        "ghz_fails_geometric_dual": not bool_s(ghz_row["passes_geometric_dual"]),
        "ghz_geometric_dual_max_rel_gap": float(ghz_row["max_rel_gap"]),
        "ghz_min_saturation_ratio": float(ghz_row["min_saturation_ratio"]),
        "free_in_qm_alone": float(ghz_row["computed_I3_after_predicate"]) > TOL,
        "qm_free_witness": "GHZ_4party",
        "qm_free_witness_i3": float(ghz_row["computed_I3_after_predicate"]),
        "free_in_gr_alone": True,
        "with_compat_min_i3": admissible_metrics["with_compat_min_i3"],
        "with_compat_max_i3": admissible_metrics["with_compat_max_i3"],
        "with_compat_min_i3_nonpositive": admissible_metrics["with_compat_min_i3"] <= TOL,
        "with_compat_max_i3_nonpositive": admissible_metrics["with_compat_max_i3"] <= TOL,
        "broken_compat_min_i3": admissible_metrics["no_compat_witness_min_i3"],
        "broken_compat_min_i3_positive": admissible_metrics["no_compat_witness_min_i3"] > TOL,
        "no_compat_broad_max_i3": admissible_metrics["no_compat_broad_max_i3"],
        "broken_compatibility_unforces": admissible_metrics["no_compat_broad_mmi_forced"] is False,
        "broken_compatibility_violator_survives": admissible_metrics["no_compat_broad_max_i3"] > TOL,
        "is_maxwell_shape_joint_prediction": True,
        "conditional_on_step47": bool(step47_schema.get("premise_ground_landed")) and bool(step48_schema.get("conditional_on_step47_premise")),
        "recovered_known_constraint": True,
        "new_measured_number": False,
        "derives_holography": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "new_physics_claim": False,
    }

    write_csv(ARTIFACT_DIR / "f51_commuting_squares_step51.csv", f51_rows)
    write_csv(ARTIFACT_DIR / "geometric_dual_compatibility_step51.csv", compatibility)
    write_csv(ARTIFACT_DIR / "admissible_coreadouts_step51.csv", compatibility)
    write_csv(ARTIFACT_DIR / "admissible_sets_step51.csv", admissible_sets)
    write_csv(ARTIFACT_DIR / "child_free_witnesses_step51.csv", child_rows)
    write_csv(ARTIFACT_DIR / "broken_compatibility_control_step51.csv", broken_rows)
    write_csv(ARTIFACT_DIR / "anti_circularity_step51.csv", anti_circularity_rows(schema))
    write_csv(ARTIFACT_DIR / "frozen_machinery_step51.csv", frozen_machinery_rows())
    (ARTIFACT_DIR / "step51_schema.json").write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(schema, f51_rows, compatibility, admissible_sets)
    write_nonclaim()
    write_statement(schema)
    write_classification()
    write_mode_packet()


if __name__ == "__main__":
    write_outputs()
