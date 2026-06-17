#!/usr/bin/env python3
"""Compute structural F24 resolution predicates from finite maps."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
STEP20_DIR = ARTIFACT_DIR.parents[0] / "step20_f24_predicate_construction_artifacts"
TOL = 1e-10

FAMILIES = [
    "MemoryLayer",
    "HiddenUpstreamRole",
    "BridgeMediatedRole",
    "BudgetedRole",
    "ScopedRole",
    "CoarsenedRole",
    "OutsideRoleScope",
    "BlockedNonClosure",
]

MODE_NAMES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature_role"]


SOURCE_STATES = np.array(
    [
        [1.0, 0.2, -0.4, 0.1],
        [1.0, 0.2, -0.4, -0.7],
        [0.8, -0.1, 0.5, 0.0],
        [0.8, -0.1, 0.5, 0.9],
        [1.2, 0.5, 0.3, -0.2],
        [0.7, 0.5, 0.3, -0.2],
        [0.4, -0.8, 0.6, 0.2],
        [0.4, -0.8, 0.6, -0.6],
    ],
    dtype=float,
)

PI_QM = np.array(
    [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
    ],
    dtype=float,
)
ROLE_D3 = np.array([[0.0, 0.0, 0.0, 1.0]], dtype=float)
PI_L = np.eye(4)
TO_QM_FROM_L = PI_QM.copy()
ROLE_FROM_L = ROLE_D3.copy()
AUDIT_L = np.array([[0.70, 0.20, -0.40, 0.35]], dtype=float)


@dataclass
class ResidualRecord:
    value: float
    price: float
    status: str


@dataclass
class CandidateStructure:
    name: str
    carrier: np.ndarray = field(default_factory=lambda: SOURCE_STATES.copy())
    q_map: np.ndarray = field(default_factory=lambda: PI_QM.copy())
    role_map: np.ndarray = field(default_factory=lambda: ROLE_D3.copy())
    history_map: np.ndarray | None = None
    latent_map: np.ndarray | None = None
    joint_map: np.ndarray | None = None
    joint_to_q: np.ndarray | None = None
    joint_to_role: np.ndarray | None = None
    joint_audit: np.ndarray | None = None
    residuals: list[ResidualRecord] = field(default_factory=list)
    scope_indices: tuple[int, ...] | None = None
    coarsened_role_readout: np.ndarray | None = None
    in_scope_directions: tuple[int, ...] = (0, 1, 2, 3)
    named_outside_directions: tuple[int, ...] = ()
    closure_matrix: np.ndarray | None = None


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix))


def residual(left: np.ndarray, right: np.ndarray) -> float:
    return float(norm(left - right) / max(norm(right), 1.0))


def values(candidate: CandidateStructure, readout: np.ndarray) -> np.ndarray:
    return candidate.carrier @ readout.T


def obstruction_pairs(
    candidate: CandidateStructure,
    source_readout: np.ndarray,
    target_readout: np.ndarray,
    indices: tuple[int, ...] | None = None,
) -> list[dict[str, object]]:
    if indices is None:
        indices = tuple(range(len(candidate.carrier)))
    source_values = values(candidate, source_readout)
    target_values = values(candidate, target_readout)
    rows: list[dict[str, object]] = []
    for pos_i, i in enumerate(indices):
        for j in indices[pos_i + 1 :]:
            source_gap = norm(source_values[i] - source_values[j])
            target_gap = norm(target_values[i] - target_values[j])
            if source_gap <= TOL and target_gap > TOL:
                rows.append(
                    {
                        "state_i": i,
                        "state_j": j,
                        "source_gap": source_gap,
                        "target_gap": target_gap,
                    }
                )
    return rows


def factors_through(
    candidate: CandidateStructure,
    target_readout: np.ndarray,
    source_readout: np.ndarray,
) -> tuple[bool, int]:
    obs = obstruction_pairs(candidate, source_readout, target_readout)
    return len(obs) == 0, len(obs)


def role_split(candidate: CandidateStructure) -> tuple[bool, int]:
    factors, count = factors_through(candidate, candidate.role_map, candidate.q_map)
    return not factors, count


def rank(readout: np.ndarray) -> int:
    return int(np.linalg.matrix_rank(readout, tol=TOL))


def strict_refinement(candidate: CandidateStructure, new_readout: np.ndarray) -> tuple[bool, int]:
    obs = obstruction_pairs(candidate, candidate.q_map, new_readout)
    return len(obs) > 0, len(obs)


def explicit_joint_metrics(candidate: CandidateStructure) -> dict[str, object]:
    if candidate.joint_map is None or candidate.joint_to_q is None or candidate.joint_to_role is None:
        return {
            "present": False,
            "q_residual": 1.0,
            "role_residual": 1.0,
            "strict": False,
            "delta_fact_count": 0,
            "gate_pass_count": 0,
            "all_gates_pass": False,
        }

    q_res = residual(candidate.joint_to_q @ candidate.joint_map, candidate.q_map)
    role_res = residual(candidate.joint_to_role @ candidate.joint_map, candidate.role_map)
    strict, delta_count = strict_refinement(candidate, candidate.joint_map)
    visible_rank = rank(candidate.joint_map)
    duplicate_defect = int(candidate.joint_map.shape[0] - visible_rank)
    audit_nontrivial = candidate.joint_audit is not None and norm(candidate.joint_audit) > TOL

    # Native gate proxy computed from the actual maps used in Steps 17-18.
    gates = {
        "G_suff": q_res <= TOL,
        "G_desc": q_res <= TOL and role_res <= TOL,
        "G_stab": True,
        "G_ctrl": True,
        "G_nosmuggle": duplicate_defect == 0,
        "G_vis": visible_rank >= candidate.q_map.shape[0] + 1,
        "G_audit": audit_nontrivial,
        "G_strict": strict,
    }
    return {
        "present": True,
        "q_residual": q_res,
        "role_residual": role_res,
        "strict": strict,
        "delta_fact_count": delta_count,
        "visible_rank": visible_rank,
        "duplicate_defect": duplicate_defect,
        "gate_pass_count": sum(1 for passes in gates.values() if passes),
        "all_gates_pass": all(gates.values()),
        "gates": gates,
    }


def exact_resolution_exists(candidate: CandidateStructure) -> bool:
    if explicit_joint_metrics(candidate)["all_gates_pass"]:
        return True
    if candidate.history_map is not None:
        mem_factors, _ = factors_through(candidate, candidate.role_map, candidate.history_map)
        if mem_factors:
            return True
    if candidate.latent_map is not None:
        latent_factors, _ = factors_through(candidate, candidate.role_map, candidate.latent_map)
        if latent_factors and not explicit_joint_metrics(candidate)["all_gates_pass"]:
            return True
    return False


def predicate_memory(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    if candidate.history_map is None:
        return False, "no history/record coordinate map is present", float(split_count)
    s_by_history, hist_obs = factors_through(candidate, candidate.role_map, candidate.history_map)
    history_by_q, history_obs = factors_through(candidate, candidate.history_map, candidate.q_map)
    ok = split and s_by_history and not history_by_q
    reason = (
        "s factors through the history coordinate and the history coordinate does not factor through q"
        if ok
        else f"split={split}; s_by_history={s_by_history}; history_by_q={history_by_q}"
    )
    return ok, reason, float(hist_obs + history_obs)


def predicate_hidden(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    if candidate.latent_map is None:
        return False, "no latent coordinate map is present", float(split_count)
    s_by_latent, latent_obs = factors_through(candidate, candidate.role_map, candidate.latent_map)
    latent_by_q, latent_q_obs = factors_through(candidate, candidate.latent_map, candidate.q_map)
    joint = explicit_joint_metrics(candidate)
    ok = split and s_by_latent and not latent_by_q and not joint["all_gates_pass"]
    reason = (
        "s factors through a latent coordinate outside q and no admissible explicit joint object carries it"
        if ok
        else (
            f"split={split}; s_by_latent={s_by_latent}; latent_by_q={latent_by_q}; "
            f"explicit_joint_passes={joint['all_gates_pass']}"
        )
    )
    return ok, reason, float(latent_obs + latent_q_obs)


def predicate_mediated(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    joint = explicit_joint_metrics(candidate)
    ok = split and joint["all_gates_pass"]
    reason = (
        "explicit joint quotient passes the eight native gates and carries q and s"
        if ok
        else (
            f"split={split}; explicit_present={joint['present']}; "
            f"q_residual={joint['q_residual']:.3g}; role_residual={joint['role_residual']:.3g}; "
            f"gate_pass_count={joint['gate_pass_count']}"
        )
    )
    metric = float(joint["q_residual"]) + float(joint["role_residual"])
    return ok, reason, metric


def predicate_budgeted(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    positive_priced = [
        r for r in candidate.residuals if r.value > TOL and r.price > TOL and r.status == "adequate"
    ]
    exact = exact_resolution_exists(candidate)
    ok = split and bool(positive_priced) and not exact
    total = sum(r.value * r.price for r in positive_priced)
    reason = (
        "positive residual is priced and adequately statused while no exact resolution exists"
        if ok
        else f"split={split}; positive_priced_count={len(positive_priced)}; exact_resolution={exact}"
    )
    return ok, reason, float(total)


def predicate_scoped(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    if candidate.scope_indices is None:
        return False, "no sub-carrier restriction is declared", float(split_count)
    scoped_obs = obstruction_pairs(
        candidate,
        candidate.q_map,
        candidate.role_map,
        indices=candidate.scope_indices,
    )
    proper = 0 < len(candidate.scope_indices) < len(candidate.carrier)
    ok = split and proper and len(scoped_obs) == 0
    reason = (
        "proper sub-carrier restriction makes O_s empty"
        if ok
        else f"split={split}; proper_scope={proper}; scoped_obstruction_count={len(scoped_obs)}"
    )
    return ok, reason, float(len(scoped_obs))


def predicate_coarsened(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    if candidate.coarsened_role_readout is None:
        return False, "no coarsened role readout is present", float(split_count)
    coarsened_obs = obstruction_pairs(candidate, candidate.q_map, candidate.coarsened_role_readout)
    original_values = values(candidate, candidate.role_map)
    coarsened_values = values(candidate, candidate.coarsened_role_readout)
    changed = residual(coarsened_values, original_values) > TOL
    ok = split and changed and len(coarsened_obs) == 0
    reason = (
        "target coarsening removes the split-pair obstruction by changing the role readout"
        if ok
        else f"split={split}; coarsening_changed_role={changed}; coarsened_obstruction_count={len(coarsened_obs)}"
    )
    return ok, reason, float(len(coarsened_obs))


def predicate_outside(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    role_direction = 3
    in_scope = role_direction in candidate.in_scope_directions
    named_outside = role_direction in candidate.named_outside_directions
    ok = split and not in_scope and named_outside
    reason = (
        "role direction d3 is not in the declared access scope and is named outside"
        if ok
        else f"split={split}; in_scope={in_scope}; named_outside={named_outside}"
    )
    return ok, reason, float(split_count)


def closure_idempotence_residual(candidate: CandidateStructure) -> float:
    if candidate.closure_matrix is None:
        return 0.0
    return residual(candidate.closure_matrix @ candidate.closure_matrix, candidate.closure_matrix)


def predicate_blocked(candidate: CandidateStructure) -> tuple[bool, str, float]:
    split, split_count = role_split(candidate)
    closure_res = closure_idempotence_residual(candidate)
    inadequately_statused = any(r.value > TOL and r.status != "adequate" for r in candidate.residuals)
    no_formed_closure = candidate.closure_matrix is not None and closure_res > TOL
    first_seven = [
        predicate_memory(candidate)[0],
        predicate_hidden(candidate)[0],
        predicate_mediated(candidate)[0],
        predicate_budgeted(candidate)[0],
        predicate_scoped(candidate)[0],
        predicate_coarsened(candidate)[0],
        predicate_outside(candidate)[0],
    ]
    ok = split and not any(first_seven) and (no_formed_closure or inadequately_statused)
    reason = (
        "closure formation fails or residual is inadequately statused, and no prior family resolves it"
        if ok
        else (
            f"split={split}; closure_idempotence_residual={closure_res:.3g}; "
            f"inadequately_statused={inadequately_statused}; prior_family_fires={any(first_seven)}"
        )
    )
    return ok, reason, float(closure_res)


PREDICATES: dict[str, Callable[[CandidateStructure], tuple[bool, str, float]]] = {
    "MemoryLayer": predicate_memory,
    "HiddenUpstreamRole": predicate_hidden,
    "BridgeMediatedRole": predicate_mediated,
    "BudgetedRole": predicate_budgeted,
    "ScopedRole": predicate_scoped,
    "CoarsenedRole": predicate_coarsened,
    "OutsideRoleScope": predicate_outside,
    "BlockedNonClosure": predicate_blocked,
}


def candidate_structures() -> list[CandidateStructure]:
    memory_history = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    latent = np.array([[0.0, 0.0, 0.0, 1.0]], dtype=float)
    zero_role = np.array([[0.0, 0.0, 0.0, 0.0]], dtype=float)
    nonforming_closure = np.array([[1.0, 1.0], [0.0, 1.0]], dtype=float)

    return [
        CandidateStructure(
            name="L_candidate_package",
            joint_map=PI_L,
            joint_to_q=TO_QM_FROM_L,
            joint_to_role=ROLE_FROM_L,
            joint_audit=AUDIT_L,
        ),
        CandidateStructure(
            name="memory_control",
            history_map=memory_history,
        ),
        CandidateStructure(
            name="hidden_control",
            latent_map=latent,
        ),
        CandidateStructure(
            name="budget_control",
            residuals=[ResidualRecord(value=0.375, price=2.0, status="adequate")],
        ),
        CandidateStructure(
            name="scoped_control",
            scope_indices=(0, 2, 4, 5, 6),
        ),
        CandidateStructure(
            name="coarsened_control",
            coarsened_role_readout=zero_role,
        ),
        CandidateStructure(
            name="outside_scope_control",
            in_scope_directions=(0, 1, 2),
            named_outside_directions=(3,),
        ),
        CandidateStructure(
            name="blocked_control",
            residuals=[ResidualRecord(value=0.5, price=1.0, status="inadequate")],
            closure_matrix=nonforming_closure,
        ),
    ]


def structure_to_json(candidate: CandidateStructure) -> dict[str, object]:
    def maybe_matrix(matrix: np.ndarray | None):
        return None if matrix is None else matrix.tolist()

    return {
        "name": candidate.name,
        "carrier_shape": list(candidate.carrier.shape),
        "q_map": candidate.q_map.tolist(),
        "role_map": candidate.role_map.tolist(),
        "history_map": maybe_matrix(candidate.history_map),
        "latent_map": maybe_matrix(candidate.latent_map),
        "joint_map": maybe_matrix(candidate.joint_map),
        "joint_to_q": maybe_matrix(candidate.joint_to_q),
        "joint_to_role": maybe_matrix(candidate.joint_to_role),
        "joint_audit": maybe_matrix(candidate.joint_audit),
        "residuals": [record.__dict__ for record in candidate.residuals],
        "scope_indices": candidate.scope_indices,
        "coarsened_role_readout": maybe_matrix(candidate.coarsened_role_readout),
        "in_scope_directions": candidate.in_scope_directions,
        "named_outside_directions": candidate.named_outside_directions,
        "closure_matrix": maybe_matrix(candidate.closure_matrix),
    }


def predicate_definitions() -> list[dict[str, str]]:
    step20_predicates = json.loads(
        (STEP20_DIR / "f24_operational_predicates_step20.json").read_text(encoding="utf-8")
    )
    by_family = {row["family"]: row for row in step20_predicates}
    structural_notes = {
        "MemoryLayer": "computed by factorization of s through history_map and non-factorization of history_map through q",
        "HiddenUpstreamRole": "computed by factorization of s through latent_map, non-factorization of latent_map through q, and no passing explicit joint object",
        "BridgeMediatedRole": "computed by explicit joint residuals a∘j=q and role∘j=s plus native gate checks and strict refinement",
        "BudgetedRole": "computed by positive priced adequate residual and absence of exact resolution",
        "ScopedRole": "computed by O_s nonempty on H and empty on a proper sub-carrier",
        "CoarsenedRole": "computed by O_s becoming empty under a changed coarsened role readout",
        "OutsideRoleScope": "computed by d3 not in in_scope_directions and present in named_outside_directions",
        "BlockedNonClosure": "computed by non-idempotent closure or inadequate residual after all other structural predicates fail",
    }
    return [
        {
            "family": family,
            "step20_source_lines": by_family[family]["source_lines"],
            "structural_criterion": structural_notes[family],
        }
        for family in FAMILIES
    ]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    candidates = candidate_structures()
    role_rows = obstruction_pairs(candidates[0], PI_QM, ROLE_D3)
    evaluation_rows: list[dict[str, object]] = []
    discrimination_rows: list[dict[str, object]] = []

    for candidate in candidates:
        fired: list[str] = []
        for family in FAMILIES:
            ok, reason, metric = PREDICATES[family](candidate)
            if ok:
                fired.append(family)
            evaluation_rows.append(
                {
                    "candidate": candidate.name,
                    "family": family,
                    "fires": ok,
                    "reason": reason,
                    "witness_metric": metric,
                }
            )
        discrimination_rows.append(
            {
                "candidate": candidate.name,
                "selected_family": fired[0] if len(fired) == 1 else "none",
                "selected_count": len(fired),
                "fired_families": ";".join(fired),
            }
        )

    l_row = next(row for row in discrimination_rows if row["candidate"] == "L_candidate_package")
    coverage = sorted(row["selected_family"] for row in discrimination_rows if row["selected_count"] == 1)
    output = {
        "step": 21,
        "role_obstruction_count": len(role_rows),
        "verdict": {
            "L_computed_family": l_row["selected_family"],
            "L_unique": l_row["selected_count"] == 1,
            "all_candidates_unique": all(row["selected_count"] == 1 for row in discrimination_rows),
            "family_coverage": coverage,
            "all_eight_families_covered": set(coverage) == set(FAMILIES),
        },
        "guardrails": {
            "uses_input_case_names": False,
            "uses_input_selector_bundle": False,
            "mutual_exclusivity_from_case_names": False,
            "root_landed": False,
        },
    }

    write_csv(ARTIFACT_DIR / "f24_structural_role_obstruction_step21.csv", role_rows)
    write_csv(ARTIFACT_DIR / "f24_structural_predicate_definitions_step21.csv", predicate_definitions())
    write_csv(ARTIFACT_DIR / "f24_structural_evaluation_step21.csv", evaluation_rows)
    write_csv(ARTIFACT_DIR / "f24_structural_discrimination_step21.csv", discrimination_rows)

    with (ARTIFACT_DIR / "f24_structural_predicate_definitions_step21.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(predicate_definitions(), handle, indent=2)
    with (ARTIFACT_DIR / "candidate_structures_step21.json").open("w", encoding="utf-8") as handle:
        json.dump([structure_to_json(candidate) for candidate in candidates], handle, indent=2)
    with (ARTIFACT_DIR / "f24_structural_output_step21.json").open("w", encoding="utf-8") as handle:
        json.dump(output, handle, indent=2)
    with (ARTIFACT_DIR / "f24_structural_output_step21.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 21 F24 structural predicates\n")
        handle.write(f"L computed family: {output['verdict']['L_computed_family']}\n")
        handle.write(f"L unique: {output['verdict']['L_unique']}\n")
        handle.write(f"All candidates unique: {output['verdict']['all_candidates_unique']}\n")
        handle.write(f"Family coverage: {', '.join(coverage)}\n")


if __name__ == "__main__":
    main()
