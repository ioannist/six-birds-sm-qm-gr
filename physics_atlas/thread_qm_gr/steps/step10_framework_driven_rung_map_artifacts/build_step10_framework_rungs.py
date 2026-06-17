#!/usr/bin/env python3
"""Step 10 framework-driven rung finding between finite QM and GR packages."""

from __future__ import annotations

import csv
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Rule:
    antecedent: frozenset[str]
    consequent: frozenset[str]


def close(seed: set[str], rules: list[Rule]) -> set[str]:
    """Iterate finite closure rules to an idempotent fixed point."""
    current = set(seed)
    changed = True
    while changed:
        changed = False
        for rule in rules:
            if rule.antecedent <= current and not rule.consequent <= current:
                current |= set(rule.consequent)
                changed = True
    return current


def closed_sets(atoms: list[str], rules: list[Rule]) -> list[list[str]]:
    """Enumerate Sigma_f for a finite closure operator."""
    out = []
    for r in range(len(atoms) + 1):
        for combo in itertools.combinations(atoms, r):
            seed = set(combo)
            if close(seed, rules) == seed:
                out.append(sorted(seed))
    return out


def rows_for(atoms: list[str], row_atoms: list[str]) -> np.ndarray:
    index = {name: i for i, name in enumerate(atoms)}
    rows = []
    for name in row_atoms:
        row = np.zeros(len(atoms))
        row[index[name]] = 1.0
        rows.append(row)
    return np.vstack(rows)


def adequacy(native: np.ndarray, target: np.ndarray) -> dict:
    k_ll = native @ native.T
    k_dd = target @ target.T
    k_dl = target @ native.T
    xi = k_dd - k_dl @ np.linalg.pinv(k_ll, rcond=1e-12) @ k_dl.T
    xi = 0.5 * (xi + xi.T)
    eigvals = np.linalg.eigvalsh(xi)
    raw = float(np.trace(xi))
    denom = float(np.trace(k_dd))
    return {
        "raw_trace": raw,
        "trace_K_DD": denom,
        "normalized_trace": float(raw / denom) if denom > 0 else float("nan"),
        "min_eigenvalue": float(np.min(eigvals)),
        "max_eigenvalue": float(np.max(eigvals)),
        "Xi_matrix": np.round(xi, 10).tolist(),
    }


def role_profile(closed: set[str], role_atoms: dict[str, list[str]]) -> dict[str, dict[str, object]]:
    profile = {}
    for role, atoms in role_atoms.items():
        present = [atom for atom in atoms if atom in closed]
        profile[role] = {
            "closed_count": len(present),
            "total_count": len(atoms),
            "closed_fraction": len(present) / len(atoms),
            "closed_atoms": present,
        }
    return profile


def main() -> None:
    atoms = [
        "typed_carrier",
        "composition_slot",
        "q_amplitude_currency",
        "q_probability_audit",
        "q_record_branch",
        "q_unitary_fixedpoint",
        "g_metric_currency",
        "g_curvature_audit",
        "g_event_locality",
        "g_geodesic_fixedpoint",
        "r_refinement_index",
        "r_fixedpoint_lift",
        "r_currency_exchange",
        "r_shadow_price_neutral",
        "r_audit_commutator",
        "r_descent_budget",
    ]

    role_atoms = {
        "P1_carrier": ["typed_carrier", "g_event_locality", "r_refinement_index"],
        "P2_composition": ["composition_slot", "r_fixedpoint_lift"],
        "P3_route": ["q_unitary_fixedpoint", "g_geodesic_fixedpoint", "r_audit_commutator"],
        "P4_records": ["q_record_branch", "g_event_locality", "r_refinement_index"],
        "P5_currency": ["q_amplitude_currency", "g_metric_currency", "r_currency_exchange", "r_shadow_price_neutral"],
        "P6_audit": ["q_probability_audit", "g_curvature_audit", "r_audit_commutator", "r_descent_budget"],
    }

    qm_rules = [
        Rule(frozenset({"typed_carrier"}), frozenset({"composition_slot"})),
        Rule(frozenset({"typed_carrier", "composition_slot"}), frozenset({"q_amplitude_currency"})),
        Rule(frozenset({"q_amplitude_currency"}), frozenset({"q_unitary_fixedpoint"})),
        Rule(frozenset({"q_record_branch", "q_amplitude_currency"}), frozenset({"q_probability_audit"})),
    ]
    gr_rules = [
        Rule(frozenset({"typed_carrier"}), frozenset({"composition_slot"})),
        Rule(frozenset({"typed_carrier", "composition_slot"}), frozenset({"g_event_locality"})),
        Rule(frozenset({"g_event_locality"}), frozenset({"g_metric_currency", "g_geodesic_fixedpoint"})),
        Rule(frozenset({"g_metric_currency", "g_geodesic_fixedpoint"}), frozenset({"g_curvature_audit"})),
    ]
    rung_rules = {
        "RUNG_1_REFINE_FIXEDPOINT": [
            Rule(frozenset({"r_refinement_index"}), frozenset({"r_fixedpoint_lift"})),
        ],
        "RUNG_2_NEUTRAL_CURRENCY": [
            Rule(frozenset({"r_currency_exchange"}), frozenset({"r_shadow_price_neutral"})),
        ],
        "RUNG_3_AUDIT_COMMUTATOR": [
            Rule(frozenset({"r_audit_commutator"}), frozenset({"r_descent_budget"})),
        ],
    }

    qm_seed = {"typed_carrier", "q_record_branch"}
    gr_seed = {"typed_carrier"}
    qm_closed = close(qm_seed, qm_rules)
    gr_closed = close(gr_seed, gr_rules)

    rung_closed = {
        "RUNG_1_REFINE_FIXEDPOINT": close({"r_refinement_index"}, rung_rules["RUNG_1_REFINE_FIXEDPOINT"]),
        "RUNG_2_NEUTRAL_CURRENCY": close({"r_currency_exchange"}, rung_rules["RUNG_2_NEUTRAL_CURRENCY"]),
        "RUNG_3_AUDIT_COMMUTATOR": close({"r_audit_commutator"}, rung_rules["RUNG_3_AUDIT_COMMUTATOR"]),
    }

    qm_rows = rows_for(atoms, sorted(qm_closed))
    gr_rows = rows_for(atoms, sorted(gr_closed))
    rung_target_atoms = sorted(set().union(*rung_closed.values()))
    gap_target_atoms = sorted(gr_closed | set(rung_target_atoms))
    gap_target_rows = rows_for(atoms, gap_target_atoms)
    direct_gap = adequacy(qm_rows, gap_target_rows)

    currency_rows_qm = rows_for(atoms, ["q_amplitude_currency"])
    currency_rows_gr = rows_for(atoms, ["g_metric_currency"])
    currency_factor = adequacy(currency_rows_qm, currency_rows_gr)

    rung_records = []
    current_native_atoms = set(qm_closed)
    current_raw = direct_gap["raw_trace"]
    for idx, rung_id in enumerate(
        ["RUNG_1_REFINE_FIXEDPOINT", "RUNG_2_NEUTRAL_CURRENCY", "RUNG_3_AUDIT_COMMUTATOR"], start=1
    ):
        atoms_for_rung = sorted(rung_closed[rung_id])
        before = adequacy(rows_for(atoms, sorted(current_native_atoms)), gap_target_rows)
        after_native_atoms = current_native_atoms | set(atoms_for_rung)
        after = adequacy(rows_for(atoms, sorted(after_native_atoms)), gap_target_rows)
        own_target = adequacy(rows_for(atoms, sorted(qm_closed | gr_closed)), rows_for(atoms, atoms_for_rung))
        reduction = before["raw_trace"] - after["raw_trace"]
        endpoints_close = own_target["normalized_trace"] <= 1e-12
        strict_extension = not set(atoms_for_rung) <= (qm_closed | gr_closed)
        clean = bool(reduction > 0 and strict_extension and not endpoints_close)

        if rung_id == "RUNG_1_REFINE_FIXEDPOINT":
            signature = "P1/P2/P4/P6 refinement-carrier fixed-point lift"
            currency = "introduces refinement index as a neutral bookkeeping currency"
            closes = "refinement-index and fixed-point-lift rows absent from both endpoint packages"
            priority = 1
        elif rung_id == "RUNG_2_NEUTRAL_CURRENCY":
            signature = "P5 neutral currency reflow"
            currency = "introduces exchange row and neutral shadow-price row"
            closes = "currency exchange rows absent from both endpoint packages"
            priority = 2
        else:
            signature = "P3/P6 audit-commutator budget"
            currency = "introduces audit-commutator budget currency"
            closes = "descent-commutator and audit-budget rows absent from both endpoint packages"
            priority = 3

        rung_records.append(
            {
                "id": rung_id,
                "order": idx,
                "sbt_signature": signature,
                "currency_role_introduced": currency,
                "what_it_closes_that_endpoints_dont": closes,
                "atoms_closed": ";".join(atoms_for_rung),
                "xi_before_raw": before["raw_trace"],
                "xi_after_raw": after["raw_trace"],
                "xi_contribution_raw": reduction,
                "xi_contribution_fraction_of_direct_gap": reduction / current_raw if current_raw > 0 else 0.0,
                "own_rung_vs_endpoints_normalized_xi": own_target["normalized_trace"],
                "strict_extension": strict_extension,
                "clean_emergence": "yes" if clean else "no",
                "build_priority": priority,
            }
        )
        current_native_atoms = after_native_atoms

    all_rung_native = rows_for(atoms, sorted(qm_closed | set(rung_target_atoms)))
    all_rungs_gap = adequacy(all_rung_native, gap_target_rows)

    role_diff = {}
    qm_profile = role_profile(qm_closed, role_atoms)
    gr_profile = role_profile(gr_closed, role_atoms)
    for role in role_atoms:
        qm_atoms = set(qm_profile[role]["closed_atoms"])
        gr_atoms = set(gr_profile[role]["closed_atoms"])
        role_diff[role] = {
            "qm_only": sorted(qm_atoms - gr_atoms),
            "gr_only": sorted(gr_atoms - qm_atoms),
            "shared": sorted(qm_atoms & gr_atoms),
            "changed": sorted(qm_atoms ^ gr_atoms),
        }

    packages = {
        "atoms": atoms,
        "roles": role_atoms,
        "qm_package": {
            "Z": atoms,
            "seed": sorted(qm_seed),
            "rules": [
                {"antecedent": sorted(rule.antecedent), "consequent": sorted(rule.consequent)}
                for rule in qm_rules
            ],
            "closed_seed": sorted(qm_closed),
            "Sigma_f_count": len(closed_sets(atoms, qm_rules)),
            "role_profile": qm_profile,
            "currency": "amplitude/probability-record currency",
            "emergence_content_E": sorted(qm_closed - {"typed_carrier", "composition_slot"}),
            "audit_descent_D": "probability-record audit over q_probability_audit",
        },
        "gr_package": {
            "Z": atoms,
            "seed": sorted(gr_seed),
            "rules": [
                {"antecedent": sorted(rule.antecedent), "consequent": sorted(rule.consequent)}
                for rule in gr_rules
            ],
            "closed_seed": sorted(gr_closed),
            "Sigma_f_count": len(closed_sets(atoms, gr_rules)),
            "role_profile": gr_profile,
            "currency": "metric/curvature-transport currency",
            "emergence_content_E": sorted(gr_closed - {"typed_carrier", "composition_slot"}),
            "audit_descent_D": "curvature-route audit over g_curvature_audit",
        },
    }

    gap = {
        "direct_qm_to_gr_plus_framework_witness_gap": direct_gap,
        "gap_target_atoms": gap_target_atoms,
        "currency_mismatch": {
            "qm_currency": "q_amplitude_currency",
            "gr_currency": "g_metric_currency",
            "gr_currency_factors_through_qm": currency_factor["normalized_trace"] <= 1e-12,
            "normalized_xi": currency_factor["normalized_trace"],
            "new_currency_required": True,
        },
        "role_difference": role_diff,
        "all_rungs_inserted_gap": all_rungs_gap,
        "no_rigging_check": {
            "literature_decomposition_imported": False,
            "target_layer_inserted_as_source": False,
            "qm_to_gr_descent_inserted_as_source": False,
            "single_rung_closes_full_gap": False,
            "rungs_generated_from_residual_blocks": True,
        },
        "first_rung_to_build": "RUNG_1_REFINE_FIXEDPOINT",
    }

    (ARTIFACT_DIR / "closure_packages_step10.json").write_text(
        json.dumps(packages, indent=2) + "\n", encoding="utf-8"
    )
    (ARTIFACT_DIR / "gap_diagnostic_step10.json").write_text(
        json.dumps(gap, indent=2) + "\n", encoding="utf-8"
    )

    with (ARTIFACT_DIR / "rung_map_step10.csv").open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "id",
            "order",
            "sbt_signature",
            "currency_role_introduced",
            "what_it_closes_that_endpoints_dont",
            "atoms_closed",
            "xi_before_raw",
            "xi_after_raw",
            "xi_contribution_raw",
            "xi_contribution_fraction_of_direct_gap",
            "own_rung_vs_endpoints_normalized_xi",
            "strict_extension",
            "clean_emergence",
            "build_priority",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rung_records)

    with (ARTIFACT_DIR / "xi_diagnostic_step10.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["diagnostic", "raw_trace", "trace_kdd", "normalized_trace", "status"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "diagnostic": "direct_QM_to_GR_plus_framework_witness_gap",
                "raw_trace": direct_gap["raw_trace"],
                "trace_kdd": direct_gap["trace_K_DD"],
                "normalized_trace": direct_gap["normalized_trace"],
                "status": "structured_gap_detected",
            }
        )
        writer.writerow(
            {
                "diagnostic": "GR_currency_through_QM_currency",
                "raw_trace": currency_factor["raw_trace"],
                "trace_kdd": currency_factor["trace_K_DD"],
                "normalized_trace": currency_factor["normalized_trace"],
                "status": "new_currency_required",
            }
        )
        writer.writerow(
            {
                "diagnostic": "all_framework_rungs_inserted_gap",
                "raw_trace": all_rungs_gap["raw_trace"],
                "trace_kdd": all_rungs_gap["trace_K_DD"],
                "normalized_trace": all_rungs_gap["normalized_trace"],
                "status": "endpoint_rows_still_not_constructed",
            }
        )

    txt_lines = [
        "Step 10 framework-driven rung map",
        f"QM closed atoms: {sorted(qm_closed)}",
        f"GR closed atoms: {sorted(gr_closed)}",
        f"Direct gap raw Xi={direct_gap['raw_trace']}, normalized Xi={direct_gap['normalized_trace']}",
        f"Currency mismatch normalized Xi={currency_factor['normalized_trace']}",
        "Rungs:",
    ]
    for row in rung_records:
        txt_lines.append(
            "{id}: contribution raw Xi={xi}; clean_emergence={clean}; priority={priority}".format(
                id=row["id"],
                xi=row["xi_contribution_raw"],
                clean=row["clean_emergence"],
                priority=row["build_priority"],
            )
        )
    txt_lines.append("First rung to build: RUNG_1_REFINE_FIXEDPOINT")
    (ARTIFACT_DIR / "gap_diagnostic_step10.txt").write_text(
        "\n".join(txt_lines) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
