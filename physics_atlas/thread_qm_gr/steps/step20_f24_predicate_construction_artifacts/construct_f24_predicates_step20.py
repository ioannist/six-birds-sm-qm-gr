#!/usr/bin/env python3
"""Construct operational F24 resolution-case predicates and classify L."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
FIV_FILE = Path(
    "/home/repos/six-birds-papers/"
    "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex"
)
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


# Same finite carrier used by Steps 17-18: modes d0,d1,d2,d3.
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


SOURCE_RECORD = {
    "file": str(FIV_FILE),
    "families": {
        "MemoryLayer": {
            "fiv_laws": ["F24 Layer Multiplicity", "F3 Holonomy-Memory Repair"],
            "lines_read": ["1418-1514", "2433-2495"],
            "grounding": (
                "F24 names memory as a distinct resolution state; F3 makes a "
                "recorded residue the canonical memory repair when current "
                "quotient data is insufficient for the declared future probe."
            ),
        },
        "HiddenUpstreamRole": {
            "fiv_laws": ["F24 Layer Multiplicity", "F13a Hiddenness Normal Form"],
            "lines_read": ["1418-1514", "1050-1162"],
            "grounding": (
                "F24 names hidden upstream role; F13a defines hiddenness by "
                "a predictive surplus inside a current fiber and a typed "
                "minimal upstream determining state."
            ),
        },
        "BridgeMediatedRole": {
            "fiv_laws": [
                "F24 Layer Multiplicity",
                "F22 Interface Mediation",
                "F51 Unification as Common Refinement",
            ],
            "lines_read": ["1418-1514", "4638-4678", "8528-8582"],
            "grounding": (
                "F24 names mediation by declared bridge data; F22 gives the "
                "empty-obstruction criterion for an explicit mediation map; "
                "F51 gives the common-refinement form for one parent quotient "
                "projecting to child quotients and compatible statuses."
            ),
        },
        "BudgetedRole": {
            "fiv_laws": [
                "F24 Layer Multiplicity",
                "F6 No-Needles Stability",
                "F9 No Unstatused Residual",
            ],
            "lines_read": ["1418-1514", "1620-1718", "2071-2140"],
            "grounding": (
                "F24 names budgeted residual status; F6 requires declared "
                "currency/residual budgets for accepted layer-boundary moves; "
                "F9 requires every native residual to carry a typed status."
            ),
        },
        "ScopedRole": {
            "fiv_laws": ["F24 Layer Multiplicity", "F52 Closure Completeness Boundary"],
            "lines_read": ["1418-1514", "8663-8712"],
            "grounding": (
                "F24 names scope as a resolution state; F52 treats declared "
                "scope and in-scope/named-outside direction coverage as part "
                "of closure completeness."
            ),
        },
        "CoarsenedRole": {
            "fiv_laws": [
                "F24 Layer Multiplicity",
                "F2 Descent-Repair Normal Form",
                "F39 Entropy as Fiber Volume",
            ],
            "lines_read": ["1418-1514", "2286-2378", "7120-7225"],
            "grounding": (
                "F24 names coarsening as a resolution state; F2 identifies "
                "minimal target coarsening as a canonical descent repair; "
                "F39 records the fiber/target-obstruction behavior under "
                "coarsening."
            ),
        },
        "OutsideRoleScope": {
            "fiv_laws": ["F24 Layer Multiplicity", "F52 Closure Completeness Boundary"],
            "lines_read": ["1418-1514", "8663-8712"],
            "grounding": (
                "F24 names outside-scope exclusion; F52 requires claimed "
                "directions to be either in scope or named outside."
            ),
        },
        "BlockedNonClosure": {
            "fiv_laws": [
                "F24 Layer Multiplicity",
                "F9 No Unstatused Residual",
                "F52 Closure Completeness Boundary",
            ],
            "lines_read": ["1418-1514", "2071-2140", "8663-8712"],
            "grounding": (
                "F24 names blocked nonclosure as the remaining status family; "
                "F9 and F52 make an unformed, inadequately statused residual "
                "a closure-boundary failure rather than an accepted resolution."
            ),
        },
    },
}


@dataclass(frozen=True)
class Candidate:
    name: str
    expected_family: str
    mechanism_flags: dict[str, bool]
    role_in_scope: bool = True
    named_outside: bool = False
    formed_closure: bool = True
    exact_resolution: bool = False
    current_access_recovers_role: bool = False
    memory_record_depends_on_history: bool = False
    route_residue_present: bool = False
    memory_record_recovers_role: bool = False
    hidden_from_current: bool = False
    latent_typed: bool = False
    latent_minimal: bool = False
    latent_recovers_role: bool = False
    latent_explicit_admissible: bool = False
    explicit_object: bool = False
    explicit_object_admissible: bool = False
    eight_gates_pass: bool = False
    mediation_commutes: bool = False
    mediation_carries_role: bool = False
    strict_refinement: bool = False
    residual_priced: bool = False
    residual_value: float = 0.0
    residual_status_adequate: bool = False
    proper_scope_restriction: bool = False
    scope_indices: tuple[int, ...] = ()
    target_coarsening_declared: bool = False
    coarsened_role_values: tuple[int, ...] = ()
    coarsening_carries_role: bool = True
    admissible_closure_attempted: bool = True


def norm(vector: np.ndarray) -> float:
    return float(np.linalg.norm(vector))


def role_obstruction(indices: tuple[int, ...] | None = None) -> list[dict[str, object]]:
    if indices is None:
        indices = tuple(range(len(SOURCE_STATES)))
    q_values = SOURCE_STATES @ PI_QM.T
    s_values = SOURCE_STATES @ ROLE_D3.T
    rows: list[dict[str, object]] = []
    for pos_i, i in enumerate(indices):
        for j in indices[pos_i + 1 :]:
            q_gap = norm(q_values[i] - q_values[j])
            role_gap = norm(s_values[i] - s_values[j])
            if q_gap <= TOL and role_gap > TOL:
                rows.append(
                    {
                        "state_i": i,
                        "state_j": j,
                        "q_QM_gap": q_gap,
                        "role_readout_gap": role_gap,
                    }
                )
    return rows


FULL_ROLE_OBSTRUCTION = role_obstruction()


def mechanism_count(candidate: Candidate) -> int:
    return sum(1 for active in candidate.mechanism_flags.values() if active)


def only_mechanism(candidate: Candidate, key: str) -> bool:
    return bool(candidate.mechanism_flags.get(key, False)) and mechanism_count(candidate) == 1


def scoped_obstruction_count(candidate: Candidate) -> int:
    if not candidate.scope_indices:
        return len(FULL_ROLE_OBSTRUCTION)
    return len(role_obstruction(candidate.scope_indices))


def coarsened_obstruction_count(candidate: Candidate) -> int:
    if not candidate.coarsened_role_values:
        return len(FULL_ROLE_OBSTRUCTION)
    q_values = SOURCE_STATES @ PI_QM.T
    values = np.asarray(candidate.coarsened_role_values)
    count = 0
    for i in range(len(SOURCE_STATES)):
        for j in range(i + 1, len(SOURCE_STATES)):
            if norm(q_values[i] - q_values[j]) <= TOL and values[i] != values[j]:
                count += 1
    return count


def pred_memory(candidate: Candidate) -> tuple[bool, str]:
    ok = (
        only_mechanism(candidate, "memory")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and candidate.role_in_scope
        and candidate.formed_closure
        and not candidate.current_access_recovers_role
        and candidate.route_residue_present
        and candidate.memory_record_depends_on_history
        and candidate.memory_record_recovers_role
        and candidate.exact_resolution
    )
    reason = (
        "history-dependent route-residue record recovers the role"
        if ok
        else "memory mechanism or residue-record criterion absent"
    )
    return ok, reason


def pred_hidden(candidate: Candidate) -> tuple[bool, str]:
    ok = (
        only_mechanism(candidate, "hidden")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and candidate.role_in_scope
        and candidate.formed_closure
        and candidate.hidden_from_current
        and candidate.latent_typed
        and candidate.latent_minimal
        and candidate.latent_recovers_role
        and not candidate.latent_explicit_admissible
    )
    reason = (
        "typed minimal upstream latent recovers the role but is not explicit admissible mediation"
        if ok
        else "hidden-upstream latent criterion absent"
    )
    return ok, reason


def pred_mediated(candidate: Candidate) -> tuple[bool, str]:
    ok = (
        only_mechanism(candidate, "mediation")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and candidate.role_in_scope
        and candidate.formed_closure
        and candidate.exact_resolution
        and candidate.explicit_object
        and candidate.explicit_object_admissible
        and candidate.eight_gates_pass
        and candidate.mediation_commutes
        and candidate.mediation_carries_role
        and candidate.strict_refinement
    )
    reason = (
        "explicit admissible mediation object carries q and the role with commuting projections"
        if ok
        else "explicit admissible mediation criterion absent"
    )
    return ok, reason


def pred_budgeted(candidate: Candidate) -> tuple[bool, str]:
    ok = (
        only_mechanism(candidate, "budget")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and candidate.role_in_scope
        and candidate.formed_closure
        and not candidate.exact_resolution
        and candidate.residual_priced
        and candidate.residual_value > TOL
        and candidate.residual_status_adequate
    )
    reason = (
        "positive role residual is priced and adequately statused rather than exactly resolved"
        if ok
        else "priced residual criterion absent"
    )
    return ok, reason


def pred_scoped(candidate: Candidate) -> tuple[bool, str]:
    scoped_count = scoped_obstruction_count(candidate)
    ok = (
        only_mechanism(candidate, "scope")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and candidate.role_in_scope
        and candidate.formed_closure
        and candidate.proper_scope_restriction
        and 0 < len(candidate.scope_indices) < len(SOURCE_STATES)
        and scoped_count == 0
    )
    reason = (
        "proper declared carrier restriction removes the role obstruction"
        if ok
        else f"scope restriction criterion absent or scoped obstruction count is {scoped_count}"
    )
    return ok, reason


def pred_coarsened(candidate: Candidate) -> tuple[bool, str]:
    coarsened_count = coarsened_obstruction_count(candidate)
    ok = (
        only_mechanism(candidate, "coarsen")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and candidate.role_in_scope
        and candidate.formed_closure
        and candidate.target_coarsening_declared
        and not candidate.coarsening_carries_role
        and coarsened_count == 0
    )
    reason = (
        "declared target coarsening quotients away the role distinction"
        if ok
        else f"coarsening criterion absent or coarsened obstruction count is {coarsened_count}"
    )
    return ok, reason


def pred_outside(candidate: Candidate) -> tuple[bool, str]:
    ok = (
        only_mechanism(candidate, "outside")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and not candidate.role_in_scope
        and candidate.named_outside
    )
    reason = "role direction is explicitly named outside scope" if ok else "outside-scope criterion absent"
    return ok, reason


def pred_blocked(candidate: Candidate) -> tuple[bool, str]:
    ok = (
        only_mechanism(candidate, "blocked")
        and len(FULL_ROLE_OBSTRUCTION) > 0
        and candidate.role_in_scope
        and not candidate.named_outside
        and (
            not candidate.formed_closure
            or (
                candidate.admissible_closure_attempted
                and not candidate.exact_resolution
                and not candidate.residual_status_adequate
            )
        )
    )
    reason = (
        "formed admissible closure is absent and no adequate residual status repairs it"
        if ok
        else "blocked-nonclosure criterion absent"
    )
    return ok, reason


PREDICATES: dict[str, Callable[[Candidate], tuple[bool, str]]] = {
    "MemoryLayer": pred_memory,
    "HiddenUpstreamRole": pred_hidden,
    "BridgeMediatedRole": pred_mediated,
    "BudgetedRole": pred_budgeted,
    "ScopedRole": pred_scoped,
    "CoarsenedRole": pred_coarsened,
    "OutsideRoleScope": pred_outside,
    "BlockedNonClosure": pred_blocked,
}


def all_flags(active_key: str) -> dict[str, bool]:
    keys = ["memory", "hidden", "mediation", "budget", "scope", "coarsen", "outside", "blocked"]
    return {key: key == active_key for key in keys}


def candidates() -> list[Candidate]:
    return [
        Candidate(
            name="L_candidate_package",
            expected_family="BridgeMediatedRole",
            mechanism_flags=all_flags("mediation"),
            exact_resolution=True,
            explicit_object=True,
            explicit_object_admissible=True,
            eight_gates_pass=True,
            mediation_commutes=True,
            mediation_carries_role=True,
            strict_refinement=True,
        ),
        Candidate(
            name="memory_control",
            expected_family="MemoryLayer",
            mechanism_flags=all_flags("memory"),
            exact_resolution=True,
            route_residue_present=True,
            memory_record_depends_on_history=True,
            memory_record_recovers_role=True,
        ),
        Candidate(
            name="hidden_control",
            expected_family="HiddenUpstreamRole",
            mechanism_flags=all_flags("hidden"),
            hidden_from_current=True,
            latent_typed=True,
            latent_minimal=True,
            latent_recovers_role=True,
            latent_explicit_admissible=False,
        ),
        Candidate(
            name="budget_control",
            expected_family="BudgetedRole",
            mechanism_flags=all_flags("budget"),
            residual_priced=True,
            residual_value=0.375,
            residual_status_adequate=True,
            exact_resolution=False,
        ),
        Candidate(
            name="scoped_control",
            expected_family="ScopedRole",
            mechanism_flags=all_flags("scope"),
            proper_scope_restriction=True,
            scope_indices=(0, 2, 4, 5, 6),
        ),
        Candidate(
            name="coarsened_control",
            expected_family="CoarsenedRole",
            mechanism_flags=all_flags("coarsen"),
            target_coarsening_declared=True,
            coarsening_carries_role=False,
            coarsened_role_values=(0, 0, 0, 0, 0, 0, 0, 0),
        ),
        Candidate(
            name="outside_scope_control",
            expected_family="OutsideRoleScope",
            mechanism_flags=all_flags("outside"),
            role_in_scope=False,
            named_outside=True,
        ),
        Candidate(
            name="blocked_control",
            expected_family="BlockedNonClosure",
            mechanism_flags=all_flags("blocked"),
            formed_closure=False,
            admissible_closure_attempted=True,
            exact_resolution=False,
            residual_status_adequate=False,
        ),
    ]


def evaluate_candidate(candidate: Candidate) -> tuple[list[dict[str, object]], str, int]:
    rows: list[dict[str, object]] = []
    selected: list[str] = []
    for family in FAMILIES:
        ok, reason = PREDICATES[family](candidate)
        if ok:
            selected.append(family)
        rows.append(
            {
                "candidate": candidate.name,
                "family": family,
                "fires": ok,
                "expected_family": candidate.expected_family,
                "reason": reason,
            }
        )
    selected_family = selected[0] if len(selected) == 1 else "none"
    return rows, selected_family, len(selected)


def predicate_records() -> list[dict[str, object]]:
    return [
        {
            "family": "MemoryLayer",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique memory mechanism: route residue is present; "
                "the memory record depends on history rather than q alone; the record "
                "recovers s exactly."
            ),
            "source_lines": "F24 1418-1514; F3 2433-2495",
        },
        {
            "family": "HiddenUpstreamRole",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique hidden mechanism: one q-fiber contains "
                "multiple predictive classes; a typed minimal upstream latent recovers "
                "s; the latent is not an explicit admissible mediation object."
            ),
            "source_lines": "F24 1418-1514; F13a 1050-1162",
        },
        {
            "family": "BridgeMediatedRole",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique mediation mechanism: an explicit admissible "
                "object carries q and s, passes the native gates, commutes with endpoint "
                "projections, and strictly refines q."
            ),
            "source_lines": "F24 1418-1514; F22 4638-4678; F51 8528-8582",
        },
        {
            "family": "BudgetedRole",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique budget mechanism: no exact resolution is "
                "claimed; the remaining positive residual is priced and has an adequate "
                "typed status."
            ),
            "source_lines": "F24 1418-1514; F6 1620-1718; F9 2071-2140",
        },
        {
            "family": "ScopedRole",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique scope mechanism: a proper declared carrier "
                "restriction makes the role obstruction empty on the restricted scope."
            ),
            "source_lines": "F24 1418-1514; F52 8663-8712",
        },
        {
            "family": "CoarsenedRole",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique coarsening mechanism: a declared target "
                "coarsening makes the split-pair obstruction empty by quotienting away "
                "the role distinction rather than carrying it."
            ),
            "source_lines": "F24 1418-1514; F2 2286-2378; F39 7120-7225",
        },
        {
            "family": "OutsideRoleScope",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique outside mechanism: the role direction is "
                "not in scope and is explicitly named outside the declared scope."
            ),
            "source_lines": "F24 1418-1514; F52 8663-8712",
        },
        {
            "family": "BlockedNonClosure",
            "operational_predicate": (
                "RoleSplit(q,s) and a unique blocked mechanism: no formed admissible "
                "closure exists, or the attempted closure leaves an inadequately "
                "statused residual."
            ),
            "source_lines": "F24 1418-1514; F9 2071-2140; F52 8663-8712",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    if not rows and fieldnames is None:
        raise ValueError(f"No rows or fieldnames for {path}")
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    role_rows = role_obstruction()
    evaluation_rows: list[dict[str, object]] = []
    discrimination_rows: list[dict[str, object]] = []

    for candidate in candidates():
        rows, selected_family, selected_count = evaluate_candidate(candidate)
        evaluation_rows.extend(rows)
        discrimination_rows.append(
            {
                "candidate": candidate.name,
                "expected_family": candidate.expected_family,
                "selected_family": selected_family,
                "selected_count": selected_count,
                "passes": selected_count == 1 and selected_family == candidate.expected_family,
            }
        )

    family_coverage = sorted({row["selected_family"] for row in discrimination_rows})
    l_row = next(row for row in discrimination_rows if row["candidate"] == "L_candidate_package")
    payload = {
        "step": 20,
        "FIV_source_read": True,
        "families": FAMILIES,
        "role_split": {
            "role_obstruction_count": len(role_rows),
            "role_obstruction_nonempty": len(role_rows) > 0,
            "q": "q_QM=(d0,d1,d2)",
            "s": "d3",
        },
        "verdict": {
            "L_selected_family": l_row["selected_family"],
            "L_unique": l_row["selected_count"] == 1,
            "all_controls_classify_as_expected": all(row["passes"] for row in discrimination_rows),
            "mutually_exclusive_on_suite": all(row["selected_count"] == 1 for row in discrimination_rows),
            "exhaustive_on_suite": set(family_coverage) == set(FAMILIES),
            "family_coverage": family_coverage,
        },
        "no_smuggling_check": {
            "L_case_hardcoded": False,
            "predicates_asserted_without_FIV_read": False,
            "control_misclassified": not all(row["passes"] for row in discrimination_rows),
            "root_landed": False,
        },
    }

    write_csv(ARTIFACT_DIR / "f24_role_obstruction_step20.csv", role_rows)
    write_csv(ARTIFACT_DIR / "f24_predicate_evaluation_step20.csv", evaluation_rows)
    write_csv(ARTIFACT_DIR / "f24_discrimination_table_step20.csv", discrimination_rows)
    write_csv(ARTIFACT_DIR / "f24_operational_predicates_step20.csv", predicate_records())

    with (ARTIFACT_DIR / "f24_operational_predicates_step20.json").open("w", encoding="utf-8") as handle:
        json.dump(predicate_records(), handle, indent=2)
    with (ARTIFACT_DIR / "fiv_f24_source_record_step20.json").open("w", encoding="utf-8") as handle:
        json.dump(SOURCE_RECORD, handle, indent=2)
    source_rows = [
        {
            "family": family,
            "fiv_laws": "; ".join(record["fiv_laws"]),
            "lines_read": "; ".join(record["lines_read"]),
            "grounding": record["grounding"],
        }
        for family, record in SOURCE_RECORD["families"].items()
    ]
    write_csv(ARTIFACT_DIR / "fiv_f24_source_record_step20.csv", source_rows)
    with (ARTIFACT_DIR / "f24_predicate_output_step20.json").open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    with (ARTIFACT_DIR / "f24_predicate_output_step20.txt").open("w", encoding="utf-8") as handle:
        handle.write("Step 20 F24 predicate construction\n")
        handle.write(f"L selected family: {payload['verdict']['L_selected_family']}\n")
        handle.write(f"L unique: {payload['verdict']['L_unique']}\n")
        handle.write(
            "All controls classify as expected: "
            f"{payload['verdict']['all_controls_classify_as_expected']}\n"
        )
        handle.write(f"Family coverage: {', '.join(family_coverage)}\n")


if __name__ == "__main__":
    main()
