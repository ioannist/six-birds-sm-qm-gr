#!/usr/bin/env python3
"""Step 48: decide ladder vs fork on the QM-GR common-carrier grammar.

Given the Step47 recognition-source common-carrier premise, this step tests the
asymmetric ladder attempt directly: can the GR readout factor through the QM
readout, even after adjoining a weak RT/QM-accessible geometry shadow computed
from the QM arm? The fork closes iff both children descend from L while neither
endpoint is a quotient of the other.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP30_DIR = THREAD_ROOT / "steps" / "step30_qg_directed_reduction_nogo_artifacts"
STEP38_DIR = THREAD_ROOT / "steps" / "step38_carrier_independence_artifacts"
STEP42_DIR = THREAD_ROOT / "steps" / "step42_faithful_holographic_rt_enrichment_artifacts"
STEP47_DIR = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
TOL = 1e-10


def rel(path: Path) -> str:
    return str(path.relative_to(THREAD_ROOT))


def selector(rows: Iterable[int], ambient_dim: int = 4) -> np.ndarray:
    rows = list(rows)
    matrix = np.zeros((len(rows), ambient_dim), dtype=float)
    for i, row_index in enumerate(rows):
        matrix[i, row_index] = 1.0
    return matrix


MODE_NAMES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]
Q_QM = selector([0, 1, 2], 4)
Q_GR = selector([0, 2, 3], 4)
Q_GR_NESTED = selector([0, 2, 1], 4)
L = np.eye(4)

COMPLETE_16 = np.array(
    [[(idx >> shift) & 1 for shift in range(4)] for idx in range(16)],
    dtype=float,
)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def values(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    return states @ readout.T


def factorization(source_map: np.ndarray, target_map: np.ndarray) -> dict[str, object]:
    """Least-squares linear quotient test: target = phi @ source."""
    phi_t, *_ = np.linalg.lstsq(source_map.T, target_map.T, rcond=None)
    phi = phi_t.T
    residual = norm(phi @ source_map - target_map) / max(norm(target_map), 1.0)
    return {"factors": residual <= TOL, "residual": float(residual), "phi": phi.tolist()}


def finite_obstruction_pairs(states: np.ndarray, source_map: np.ndarray, target_map: np.ndarray) -> list[tuple[int, int]]:
    source_values = values(states, source_map)
    target_values = values(states, target_map)
    pairs: list[tuple[int, int]] = []
    for i in range(len(states)):
        for j in range(i + 1, len(states)):
            if norm(source_values[i] - source_values[j]) <= TOL and norm(target_values[i] - target_values[j]) > TOL:
                pairs.append((i, j))
    return pairs


def conditional_mean_completion(states: np.ndarray, readout: np.ndarray) -> np.ndarray:
    readout_values = values(states, readout)
    completed = np.zeros_like(states)
    for idx, value in enumerate(readout_values):
        fiber = [j for j, other in enumerate(readout_values) if norm(value - other) <= TOL]
        completed[idx] = np.mean(states[fiber], axis=0)
    return completed


def route_mismatch(states: np.ndarray, q_left: np.ndarray, q_right: np.ndarray) -> dict[str, object]:
    left_completion = conditional_mean_completion(states, q_left)
    right_completion = conditional_mean_completion(states, q_right)
    raw = norm(left_completion - right_completion)
    normalized = raw / max(norm(states), 1.0)
    return {"raw": float(raw), "normalized": float(normalized), "commutes": normalized <= TOL}


def qm_with_rt_shadow() -> np.ndarray:
    """Adjoin a weak RT/QM-accessible area shadow to the QM arm.

    The row is intentionally a function of the QM-accessible modes only:
    A_RT = d0 + 2*d2. Any relation produced by the Batch-A RT carrier is a
    geometry/entanglement relation inside the QM-accessible arm; as a quotient
    test, it cannot split fibers that q_QM did not split.
    """
    rt_shadow = np.array([[1.0, 0.0, 2.0, 0.0]], dtype=float)
    return np.vstack([Q_QM, rt_shadow])


def attempt_row(
    attempt_id: str,
    source_map: np.ndarray,
    target_map: np.ndarray,
    states: np.ndarray,
    interpretation: str,
) -> dict[str, object]:
    fact = factorization(source_map, target_map)
    pairs = finite_obstruction_pairs(states, source_map, target_map)
    route = route_mismatch(states, source_map, target_map)
    return {
        "attempt_id": attempt_id,
        "source_readout": f"{source_map.shape[0]} rows",
        "target_readout": f"{target_map.shape[0]} rows",
        "row_factorization_residual": f"{fact['residual']:.12g}",
        "pair_defect_count": len(pairs),
        "route_mismatch_normalized": f"{route['normalized']:.12g}",
        "lawful_quotient_closes": bool(fact["factors"] and len(pairs) == 0 and route["commutes"]),
        "interpretation": interpretation,
    }


def fork_rows() -> list[dict[str, object]]:
    qm = factorization(L, Q_QM)
    gr = factorization(L, Q_GR)
    nested = factorization(Q_QM, Q_GR_NESTED)
    route_nested = route_mismatch(COMPLETE_16, Q_QM, Q_GR_NESTED)
    return [
        {
            "case_id": "fork_L_to_QM_and_GR",
            "qm_descent_residual": f"{qm['residual']:.12g}",
            "gr_descent_residual": f"{gr['residual']:.12g}",
            "fork_closes": bool(qm["factors"] and gr["factors"]),
            "description": "Both endpoint readouts descend legally from L.",
        },
        {
            "case_id": "nested_control_ladder",
            "qm_descent_residual": "0",
            "gr_descent_residual": f"{nested['residual']:.12g}",
            "fork_closes": bool(nested["factors"] and route_nested["commutes"]),
            "description": "Control where q_GR_nested=(d0,d2,d1) is genuinely nested in q_QM, so the ladder closes.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_reviewed_values() -> dict[str, object]:
    step30 = json.loads((STEP30_DIR / "step30_schema.json").read_text(encoding="utf-8"))
    step38 = json.loads((STEP38_DIR / "schema.json").read_text(encoding="utf-8"))
    step42 = json.loads((STEP42_DIR / "step42_schema.json").read_text(encoding="utf-8"))
    step47 = json.loads((STEP47_DIR / "step47_schema.json").read_text(encoding="utf-8"))
    return {
        "step30_route_mismatch": step30["track_fields"]["route_mismatch_normalized"],
        "step30_gr_through_qm_pair_defects": step30["track_fields"]["defect_count_q_GR_through_q_QM"],
        "step38_nested_control_flips": step38["final_verdict"]["nested_control_flips_no_go"],
        "step42_rt_verdict": step42["verdict"],
        "step42_min_cut_edge_count": step42["min_cut_edge_count"],
        "step42_saturation_D4": step42["saturation_trend_D4"],
        "step47_verdict": step47["verdict"],
    }


def main() -> None:
    q_qm_rt = qm_with_rt_shadow()
    ladder = attempt_row(
        "plain_ladder_GR_as_quotient_of_QM",
        Q_QM,
        Q_GR,
        COMPLETE_16,
        "Direct vertical attempt: q_GR = phi after q_QM.",
    )
    weak_rt = attempt_row(
        "weak_RT_QM_accessible_shadow_ladder",
        q_qm_rt,
        Q_GR,
        COMPLETE_16,
        "Weak-RT / QM-accessible-shadow attempt: adjoin A_RT computed from q_QM, then test q_GR factorization.",
    )
    nested = attempt_row(
        "nested_control_GR_nested_as_quotient_of_QM",
        Q_QM,
        Q_GR_NESTED,
        COMPLETE_16,
        "Can-fail control: GR readout is deliberately nested in q_QM.",
    )
    attempts = [ladder, weak_rt, nested]
    fork = fork_rows()
    reviewed = load_reviewed_values()

    strongest_defect = float(ladder["pair_defect_count"])
    weak_rt_defect = float(weak_rt["pair_defect_count"])
    nested_flips = bool(nested["lawful_quotient_closes"])
    fork_closes = bool(fork[0]["fork_closes"])
    verdict = (
        "FORK_SELECTED_OVER_LADDER"
        if strongest_defect > 0 and weak_rt_defect > 0 and fork_closes and nested_flips
        else "LADDER_CLOSES_FORK_NOT_FORCED"
    )

    schema = {
        "step": 48,
        "orientation": "Batch_B_ladder_vs_fork_resolution",
        "active_residual": "E018 ladder-vs-fork decision given common-carrier premise",
        "main_object": "directed quotient no-go vs co-sourcing fork closure",
        "verdict": verdict,
        "strongest_ladder_factorization_defect": strongest_defect,
        "strongest_ladder_row_residual": float(ladder["row_factorization_residual"]),
        "strongest_ladder_route_mismatch": float(ladder["route_mismatch_normalized"]),
        "weak_rt_ladder_defect": weak_rt_defect,
        "weak_rt_row_residual": float(weak_rt["row_factorization_residual"]),
        "fork_closes": fork_closes,
        "nested_control_flips": nested_flips,
        "nested_control_defect": float(nested["pair_defect_count"]),
        "rt_is_fork_relation": True,
        "strong_bulk_reconstruction_residual": "strong bulk reconstruction not tested here; named residual",
        "conditional_on_step47_premise": True,
        "step47_premise_verdict": reviewed["step47_verdict"],
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
    }

    write_csv(ARTIFACT_DIR / "ladder_vs_fork_sim_step48.csv", attempts)
    write_csv(ARTIFACT_DIR / "fork_closure_step48.csv", fork)
    write_csv(
        ARTIFACT_DIR / "rt_relation_frame_step48.csv",
        [
            {
                "relation": "Batch_A_RT_area_shadow_price_entanglement",
                "source": rel(STEP42_DIR / "step42_schema.json"),
                "rt_verdict": reviewed["step42_rt_verdict"],
                "min_cut_edge_count": reviewed["step42_min_cut_edge_count"],
                "D4_saturation_ratio": reviewed["step42_saturation_D4"],
                "framing_in_step48": "fork_relation_between_co_sourced_readouts_not_ladder_quotient",
                "reason": "An RT shadow computed from the QM arm does not split q_QM fibers and still leaves q_GR factorization defective.",
            }
        ],
    )
    with (ARTIFACT_DIR / "step48_schema.json").open("w", encoding="utf-8") as handle:
        json.dump(schema, handle, indent=2)

    summary = f"""# Step 48 Results Summary

## Honest Grade First

Given the Step47 recognition-source common-carrier premise, the finite grammar selects the FORK over the LADDER. The direct ladder and the weak-RT / QM-accessible-shadow ladder both fail the directed quotient test; the symmetric co-sourcing fork closes; and the nested-endpoint control flips the result. This is conditional on the common-carrier premise, finite-carrier structural, not frame-transfer, not a quantum-gravity solution, and not a metaphysical claim about reality.

Verdict: `{verdict}`.

## Strongest Ladder Attempt

The direct ladder asks whether there is a quotient map `phi` with:

```text
q_GR = phi after q_QM
```

Computed result:

- row residual: `{ladder['row_factorization_residual']}`.
- finite pair defect count: `{ladder['pair_defect_count']}`.
- route mismatch: `{ladder['route_mismatch_normalized']}`.
- ladder closes: `{ladder['lawful_quotient_closes']}`.

## Weak-RT / QM-Accessible-Shadow Ladder Attempt

Batch A makes geometry related to entanglement, so Step48 tests the weak-RT version: adjoin a source-derived RT shadow to the QM readout and retry the GR quotient test.

```text
q_QM_plus_RT = (d0,d1,d2,A_RT), with A_RT = d0 + 2 d2
```

This is the WEAK-RT / QM-accessible-shadow ladder: `A_RT = d0 + 2*d2` is a function of QM-accessible modes, so it is structurally guaranteed not to recover `d3`. It does NOT test strong bulk reconstruction, where `d3` would be recoverable from richer quantum data; that strong claim is the named residual, not refuted here.

The computation confirms the weak-RT no-go remains:

- row residual: `{weak_rt['row_factorization_residual']}`.
- finite pair defect count: `{weak_rt['pair_defect_count']}`.
- route mismatch: `{weak_rt['route_mismatch_normalized']}`.
- ladder closes: `{weak_rt['lawful_quotient_closes']}`.

This is why Batch A's RT result is a FORK relation: entanglement and geometry are related shadows of `L`, not a proof that the full GR readout is a quotient of the QM readout.

## Fork Closure

The fork closes because both children descend from `L=(d0,d1,d2,d3)`:

- `L -> q_QM` residual: `{fork[0]['qm_descent_residual']}`.
- `L -> q_GR` residual: `{fork[0]['gr_descent_residual']}`.
- fork closes: `{fork[0]['fork_closes']}`.

## Nested-Control Flip

For the can-fail control, set:

```text
q_GR_nested = (d0,d2,d1)
```

This readout is genuinely nested in `q_QM`, so the ladder should close. It does:

- row residual: `{nested['row_factorization_residual']}`.
- finite pair defect count: `{nested['pair_defect_count']}`.
- route mismatch: `{nested['route_mismatch_normalized']}`.
- ladder closes: `{nested['lawful_quotient_closes']}`.

The nested control proves the fork-selection is not an always-fire artifact. When the endpoint readouts are actually nested, the ladder verdict flips.

## Conditionality

This decision is conditional on Step47's premise verdict: `{reviewed['step47_verdict']}`. The premise is warranted by semiclassical co-sourcing, but trans-semiclassical survival remains open.
"""
    (ARTIFACT_DIR / "step48_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 48 Nonclaim Boundary

This step does not decide the ladder/fork question unconditionally. It decides it inside the finite QM-GR common-carrier grammar, given the Step47 recognition-source premise.

It does not prove a metaphysical claim about reality, does not certify frame-transfer beyond the semiclassical warrant, does not solve quantum gravity, and does not assert that geometry is physically impossible to recover from richer quantum data in every framework. Strong bulk reconstruction is a named residual. The claim here is narrower: in this common-carrier quotient grammar, the weak-RT QM-accessible shadow is a relation between co-sourced readouts, not a lawful quotient from the QM endpoint to the full GR endpoint.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step48.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\section*{Step 48: Fork Selected Over Ladder}

Assume the Step47 common-carrier recognition premise: QM and GR are readouts of
a common carrier \(L\), warranted semiclassically by one \(\psi\) sourcing both
Born and stress-energy descents.

The ladder test asks whether \(q_{\rm GR}\) is a lawful quotient of
\(q_{\rm QM}\). On the finite four-mode carrier,
\[
q_{\rm QM}=(d_0,d_1,d_2), \qquad q_{\rm GR}=(d_0,d_2,d_3).
\]
The best linear quotient has positive residual, and the finite fiber test has
eight defect pairs. Adding the weak-RT/QM-accessible shadow
\(A_{\rm RT}=d_0+2d_2\) does not change the fiber obstruction. This is the
WEAK-RT ladder only: \(A_{\rm RT}\) is a function of QM-accessible modes and is
therefore structurally unable to recover \(d_3\). It does not test strong bulk
reconstruction from richer quantum data; that stronger claim is a named
residual, not refuted here.

The fork closes because both \(q_{\rm QM}\) and \(q_{\rm GR}\) descend from
\(L=(d_0,d_1,d_2,d_3)\) with zero residual. A nested control
\(q_{\rm GR}^{\rm nested}=(d_0,d_2,d_1)\) flips the verdict: the ladder closes
there with zero defect. Therefore the fork selection tracks the non-nested
mode structure rather than an always-on obstruction.

The Batch-A RT result is consequently read as a relation between the two
co-sourced arms of the fork, not as a quotient derivation of the full GR arm
from the QM arm.
"""
    (ARTIFACT_DIR / "ladder_vs_fork_statement_step48.tex").write_text(statement, encoding="utf-8")

    write_csv(
        ARTIFACT_DIR / "content_classification_step48.csv",
        [
            {
                "artifact": "ladder_vs_fork_resolution_step48.py",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "computes ladder defects, fork closure, weak-RT framing test, and nested-control flip",
            },
            {
                "artifact": "ladder_vs_fork_sim_step48.csv",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "directed quotient attempts and nested control",
            },
            {
                "artifact": "fork_closure_step48.csv",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "common-carrier fork closure check",
            },
            {
                "artifact": "rt_relation_frame_step48.csv",
                "classification": "analytical-structural",
                "grade": "recognition-landing",
                "scope": "frames accepted RT result as fork relation rather than endpoint quotient",
            },
            {
                "artifact": "step48_results_summary.md",
                "classification": "organizational",
                "grade": "summary",
                "scope": "conditional ladder-vs-fork decision and caveats",
            },
            {
                "artifact": "ladder_vs_fork_statement_step48.tex",
                "classification": "analytical-structural",
                "grade": "finite-carrier-diagnostic",
                "scope": "statement of fork selected over ladder in the bounded grammar",
            },
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {
                "constraint_id": "C_STEP48_FORK_CONDITIONAL_ON_PREMISE",
                "status": "active",
                "description": "The fork-vs-ladder decision is conditional on Step47's common-carrier recognition premise.",
            },
            {
                "constraint_id": "C_STEP48_NESTED_CONTROL_FLIPS",
                "status": "active",
                "description": "A genuinely nested endpoint pair must make the ladder close and turn off the directed no-go.",
            },
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "ladder-vs-fork resolution",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "sub_residual",
                "authorization": "USER-AUTHORIZED Batch B #3",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_LadderVsForkResolution_v1",
                "declared_at_step": 48,
                "objects": "four-mode access quotients; source-derived RT shadow; common-carrier fork closure; nested endpoint control",
                "excluded_designs_rationale": "Excludes ladder claims that do not compute endpoint factorization or that read RT as full-GR quotient by assumption.",
                "non_triviality_argument": "The nested control flips the verdict when endpoints are actually nested.",
                "next_grammar_delta": "trans-semiclassical frame-transfer test for the common carrier",
            }
        ],
    )


if __name__ == "__main__":
    main()
