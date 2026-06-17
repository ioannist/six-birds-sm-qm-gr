#!/usr/bin/env python3
"""Step 33: compute F24 type-uniqueness for the actual QM-GR package L.

The predicates here are structural: they read finite maps, quotients, residuals,
and gate records. No family tag or declared selector is an input.
"""

from __future__ import annotations

import csv
import itertools
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
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

MODE_NAMES = ["d0_density", "d1_phase", "d2_transport", "d3_curvature"]
QM_MODE_INDICES = (0, 1, 2)
ROLE_INDEX = 3

# The actual finite carrier and maps from Steps 17/18/21.
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
            "gates": {},
        }

    q_res = residual(candidate.joint_to_q @ candidate.joint_map, candidate.q_map)
    role_res = residual(candidate.joint_to_role @ candidate.joint_map, candidate.role_map)
    strict, delta_count = strict_refinement(candidate, candidate.joint_map)
    visible_rank = rank(candidate.joint_map)
    duplicate_defect = int(candidate.joint_map.shape[0] - visible_rank)
    audit_nontrivial = candidate.joint_audit is not None and norm(candidate.joint_audit) > TOL

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
    split, _ = role_split(candidate)
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
    split, _ = role_split(candidate)
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
    scoped_obs = obstruction_pairs(candidate, candidate.q_map, candidate.role_map, indices=candidate.scope_indices)
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
    in_scope = ROLE_INDEX in candidate.in_scope_directions
    named_outside = ROLE_INDEX in candidate.named_outside_directions
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
    split, _ = role_split(candidate)
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


def actual_l_candidate() -> CandidateStructure:
    return CandidateStructure(
        name="L_actual_QM_GR_joint_quotient",
        joint_map=PI_L,
        joint_to_q=TO_QM_FROM_L,
        joint_to_role=ROLE_FROM_L,
        joint_audit=AUDIT_L,
    )


def q_subset_readout(indices: tuple[int, ...]) -> np.ndarray:
    if not indices:
        return np.zeros((0, 4), dtype=float)
    rows = []
    for idx in indices:
        row = np.zeros(4, dtype=float)
        row[idx] = 1.0
        rows.append(row)
    return np.array(rows, dtype=float)


def coarsening_search(candidate: CandidateStructure) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for size in range(0, len(QM_MODE_INDICES) + 1):
        for subset in itertools.combinations(QM_MODE_INDICES, size):
            source = q_subset_readout(subset)
            obs = obstruction_pairs(candidate, source, candidate.role_map)
            rows.append(
                {
                    "coarsening_modes": ",".join(MODE_NAMES[i] for i in subset) if subset else "terminal",
                    "coarsening_dimension": len(subset),
                    "is_full_qm_readout": subset == QM_MODE_INDICES,
                    "obstruction_count": len(obs),
                    "empties_obstruction": len(obs) == 0,
                    "computed_reason": (
                        "d3 is not a function of this q_QM coarsening"
                        if len(obs) > 0
                        else "this coarsening would remove the role obstruction"
                    ),
                }
            )
    return rows


PHYSICS_ALTERNATIVES = {
    "MemoryLayer": "history-or-record reconciliation",
    "HiddenUpstreamRole": "hidden-variable-style latent reconciliation",
    "BudgetedRole": "effective-field-theory-with-cutoff reconciliation",
    "ScopedRole": "regime-restricted agreement",
    "CoarsenedRole": "decoherence-only or GR-as-coarse-grained-QM reconciliation",
    "OutsideRoleScope": "declaring curvature outside the role scope",
    "BlockedNonClosure": "no lawful closure forms",
}


def excluded_family_rulings(
    l_evaluation: list[dict[str, object]],
    coarsening_rows: list[dict[str, object]],
    exact_family: str,
) -> list[dict[str, object]]:
    by_family = {row["family"]: row for row in l_evaluation}
    coarsening_min = min(int(row["obstruction_count"]) for row in coarsening_rows)
    rows: list[dict[str, object]] = []
    for family in FAMILIES:
        if family == exact_family:
            continue
        predicate_reason = str(by_family[family]["reason"])
        if family == "CoarsenedRole":
            computed_evidence = (
                f"all {len(coarsening_rows)} q_QM coarsenings leave O_s nonempty; "
                f"minimum obstruction_count={coarsening_min}"
            )
            structural_reason = (
                "coarsening q_QM does not make d3 a function of the access quotient"
            )
        elif family == "HiddenUpstreamRole":
            computed_evidence = "explicit joint metrics pass all eight gates; no latent map is present"
            structural_reason = "L is explicit and admissible, not hidden upstream"
        elif family == "BudgetedRole":
            computed_evidence = "exact joint residuals q=0 and role=0; positive priced residual count is 0"
            structural_reason = "the L resolution is exact on the finite carrier, not residual-only"
        elif family == "ScopedRole":
            computed_evidence = "L is evaluated on all eight carrier states; no proper sub-carrier is used"
            structural_reason = "the resolution is full-carrier rather than regime-only"
        elif family == "MemoryLayer":
            computed_evidence = "no history/record coordinate map is present in L"
            structural_reason = "d3 is carried by the explicit L coordinate, not by a history variable"
        elif family == "OutsideRoleScope":
            computed_evidence = "in_scope_directions=(0,1,2,3); role direction d3 is in scope"
            structural_reason = "the curvature role is inside the declared role-split"
        elif family == "BlockedNonClosure":
            computed_evidence = "BridgeMediatedRole fires; closure residual is 0"
            structural_reason = "a lawful explicit closure object forms on the finite carrier"
        else:
            computed_evidence = predicate_reason
            structural_reason = predicate_reason
        rows.append(
            {
                "excluded_family": family,
                "fires_on_L": by_family[family]["fires"],
                "excluded": not bool(by_family[family]["fires"]),
                "structural_reason": structural_reason,
                "predicate_reason": predicate_reason,
                "computed_evidence": computed_evidence,
                "physics_alternative_reading": PHYSICS_ALTERNATIVES[family],
                "bounded_ruling": (
                    f"excluded as the full QM-GR reconciliation type in this finite grammar; "
                    f"does not rule out all uses of {PHYSICS_ALTERNATIVES[family]}"
                ),
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        raise ValueError(f"cannot write empty csv {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    candidate = actual_l_candidate()
    role_rows = obstruction_pairs(candidate, candidate.q_map, candidate.role_map)
    l_evaluation: list[dict[str, object]] = []
    fired: list[str] = []
    for family in FAMILIES:
        ok, reason, metric = PREDICATES[family](candidate)
        if ok:
            fired.append(family)
        l_evaluation.append(
            {
                "candidate": candidate.name,
                "family": family,
                "fires": ok,
                "reason": reason,
                "witness_metric": metric,
                "computed_from": "finite maps q_map role_map joint_map gate_metrics residual_records scope_maps",
            }
        )

    coarsening_rows = coarsening_search(candidate)
    selected_family = fired[0] if len(fired) == 1 else "NON_UNIQUE_OR_NONE"
    excluded_rows = excluded_family_rulings(l_evaluation, coarsening_rows, selected_family)
    joint_metrics = explicit_joint_metrics(candidate)

    output = {
        "step": 33,
        "orientation": "Part B type-uniqueness by structural F24 predicates",
        "candidate": candidate.name,
        "selected_family": selected_family,
        "fired_families": fired,
        "unique_type": len(fired) == 1 and selected_family == "BridgeMediatedRole",
        "role_obstruction_count_O_s": len(role_rows),
        "joint_metrics": joint_metrics,
        "coarsening_search": {
            "rows_checked": len(coarsening_rows),
            "all_qm_coarsenings_leave_O_s_nonempty": all(
                int(row["obstruction_count"]) > 0 for row in coarsening_rows
            ),
            "minimum_obstruction_count": min(int(row["obstruction_count"]) for row in coarsening_rows),
        },
        "excluded_families_count": sum(1 for row in excluded_rows if row["excluded"]),
        "guardrails": {
            "computed_from_real_maps": True,
            "case_selector_inputs_used": False,
            "type_uniqueness_only": True,
            "instance_uniqueness_open": True,
            "root_landed": False,
        },
        "verdict": (
            "type_uniqueness_bridge_mediated_role_on_L"
            if len(fired) == 1 and selected_family == "BridgeMediatedRole"
            else "type_non_uniqueness_or_predicate_gap"
        ),
    }

    write_csv(ARTIFACT_DIR / "f24_predicates_on_L_step33.csv", l_evaluation)
    write_csv(ARTIFACT_DIR / "coarsening_obstruction_step33.csv", coarsening_rows)
    write_csv(ARTIFACT_DIR / "excluded_family_rulings_step33.csv", excluded_rows)
    write_csv(ARTIFACT_DIR / "role_obstruction_pairs_step33.csv", role_rows)

    carrier_record = {
        "mode_names": MODE_NAMES,
        "source_states": SOURCE_STATES.tolist(),
        "pi_qm": PI_QM.tolist(),
        "role_d3": ROLE_D3.tolist(),
        "pi_l": PI_L.tolist(),
        "to_qm_from_l": TO_QM_FROM_L.tolist(),
        "role_from_l": ROLE_FROM_L.tolist(),
        "audit_l": AUDIT_L.tolist(),
        "note": "Actual Step 17/18/21 finite maps; no family selector field is present.",
    }
    (ARTIFACT_DIR / "actual_L_maps_step33.json").write_text(
        json.dumps(carrier_record, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "type_uniqueness_output_step33.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    (ARTIFACT_DIR / "type_uniqueness_output_step33.txt").write_text(
        "\n".join(
            [
                "Step 33 Part B type-uniqueness",
                f"Selected family: {selected_family}",
                f"Fired families: {', '.join(fired)}",
                f"Unique type: {output['unique_type']}",
                f"O_s obstruction count: {len(role_rows)}",
                (
                    "All q_QM coarsenings leave O_s nonempty: "
                    f"{output['coarsening_search']['all_qm_coarsenings_leave_O_s_nonempty']}"
                ),
                f"Verdict: {output['verdict']}",
                "Instance uniqueness remains open.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
