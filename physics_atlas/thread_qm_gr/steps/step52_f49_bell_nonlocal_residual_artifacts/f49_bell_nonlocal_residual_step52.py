#!/usr/bin/env python3
"""Step 52: Bell/EPR as F49 statused nonlocal residual.

The computation is deliberately elementary and finite:
* Bell correlations are computed from a two-qubit Bell state and CHSH settings.
* The local bound is computed by enumerating all 16 deterministic local
  strategies.
* The classical control includes an explicit 16-row LHV mixture that is checked
  against its quantum correlation table.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[3]
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEP47_DIR = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
CORPUS_ROOT_ENV = "SIX_BIRDS_PAPERS_ROOT"
FOUNDATIONS_IV_NAME = "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex"
FOUNDATIONS_III_NAME = "Tsiokos_2026_Six_Birds_Foundations_III_A_Finite_Audited_Interaction_Calculus_for_SBT.tex"
TOL = 1e-10


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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def pauli() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    identity = np.eye(2, dtype=complex)
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return identity, sx, sy, sz


def settings() -> dict[str, dict[str, np.ndarray]]:
    _identity, sx, _sy, sz = pauli()
    root2 = math.sqrt(2.0)
    return {
        "A": {
            "a0": sz,
            "a1": sx,
        },
        "B": {
            "b0": (sz + sx) / root2,
            "b1": (sz - sx) / root2,
        },
    }


def bell_phi_plus_density() -> np.ndarray:
    state = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / math.sqrt(2.0)
    return np.outer(state, np.conjugate(state))


def classical_mixture_density() -> np.ndarray:
    ket00 = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    ket11 = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    return 0.5 * np.outer(ket00, ket00.conjugate()) + 0.5 * np.outer(ket11, ket11.conjugate())


def expectation(rho: np.ndarray, obs_a: np.ndarray, obs_b: np.ndarray) -> float:
    value = np.trace(rho @ np.kron(obs_a, obs_b))
    return float(np.real_if_close(value))


def correlation_table(rho: np.ndarray, case_id: str) -> tuple[list[dict[str, Any]], dict[tuple[str, str], float]]:
    obs = settings()
    rows = []
    values: dict[tuple[str, str], float] = {}
    for a_name in ["a0", "a1"]:
        for b_name in ["b0", "b1"]:
            value = expectation(rho, obs["A"][a_name], obs["B"][b_name])
            values[(a_name, b_name)] = value
            rows.append(
                {
                    "case_id": case_id,
                    "a_setting": a_name,
                    "b_setting": b_name,
                    "correlation_E": f"{value:.12g}",
                    "computed_from": "Tr(rho * A_i tensor B_j)",
                }
            )
    return rows, values


def chsh(values: dict[tuple[str, str], float]) -> float:
    return values[("a0", "b0")] + values[("a0", "b1")] + values[("a1", "b0")] - values[("a1", "b1")]


def deterministic_strategies() -> list[dict[str, Any]]:
    rows = []
    for a0 in [-1, 1]:
        for a1 in [-1, 1]:
            for b0 in [-1, 1]:
                for b1 in [-1, 1]:
                    value = a0 * b0 + a0 * b1 + a1 * b0 - a1 * b1
                    rows.append(
                        {
                            "strategy_id": f"a0{a0:+d}_a1{a1:+d}_b0{b0:+d}_b1{b1:+d}",
                            "a0": a0,
                            "a1": a1,
                            "b0": b0,
                            "b1": b1,
                            "CHSH_value": f"{value:.12g}",
                            "abs_CHSH": f"{abs(value):.12g}",
                        }
                    )
    return rows


def local_bound_from_strategies(rows: list[dict[str, Any]]) -> float:
    return max(float(row["abs_CHSH"]) for row in rows)


def classical_lhv_table() -> list[dict[str, Any]]:
    c = 1.0 / math.sqrt(2.0)
    p_same = (1.0 + c) / 2.0
    p_flip = (1.0 - c) / 2.0
    rows = []
    for a0 in [-1, 1]:
        for a1 in [-1, 1]:
            for b0 in [-1, 1]:
                for b1 in [-1, 1]:
                    p_b0 = p_same if b0 == a0 else p_flip
                    p_b1 = p_same if b1 == a0 else p_flip
                    weight = 0.25 * p_b0 * p_b1
                    rows.append(
                        {
                            "strategy_id": f"a0{a0:+d}_a1{a1:+d}_b0{b0:+d}_b1{b1:+d}",
                            "weight": f"{weight:.15g}",
                            "a0": a0,
                            "a1": a1,
                            "b0": b0,
                            "b1": b1,
                        }
                    )
    return rows


def lhv_correlations(rows: list[dict[str, Any]]) -> dict[tuple[str, str], float]:
    corr: dict[tuple[str, str], float] = {("a0", "b0"): 0.0, ("a0", "b1"): 0.0, ("a1", "b0"): 0.0, ("a1", "b1"): 0.0}
    for row in rows:
        weight = float(row["weight"])
        for a_name in ["a0", "a1"]:
            for b_name in ["b0", "b1"]:
                corr[(a_name, b_name)] += weight * int(row[a_name]) * int(row[b_name])
    return corr


def control_lhv_check_rows(control_values: dict[tuple[str, str], float], lhv_values: dict[tuple[str, str], float]) -> list[dict[str, Any]]:
    rows = []
    for a_name in ["a0", "a1"]:
        for b_name in ["b0", "b1"]:
            q_value = control_values[(a_name, b_name)]
            lhv_value = lhv_values[(a_name, b_name)]
            rows.append(
                {
                    "a_setting": a_name,
                    "b_setting": b_name,
                    "control_quantum_E": f"{q_value:.12g}",
                    "lhv_reproduced_E": f"{lhv_value:.12g}",
                    "abs_error": f"{abs(q_value - lhv_value):.12g}",
                    "matches": abs(q_value - lhv_value) <= 1e-9,
                }
            )
    return rows


def setting_commutators() -> list[dict[str, Any]]:
    obs = settings()
    rows = []
    for party, first, second in [("A", "a0", "a1"), ("B", "b0", "b1")]:
        comm = obs[party][first] @ obs[party][second] - obs[party][second] @ obs[party][first]
        fro = float(np.linalg.norm(comm, ord="fro"))
        rows.append(
            {
                "party": party,
                "setting_1": first,
                "setting_2": second,
                "commutator_frobenius_norm": f"{fro:.12g}",
                "normalized_commutator_residual": f"{(fro / 4.0):.12g}",
                "nonzero": fro > TOL,
            }
        )
    return rows


def delta_fact_witness_rows(quantum_values: dict[tuple[str, str], float]) -> list[dict[str, Any]]:
    return [
        {
            "witness_id": "source_only_Bell_state_context_pair",
            "pi0_source_value_h": "Bell_phi_plus_source",
            "pi0_source_value_h_prime": "Bell_phi_plus_source",
            "same_pi0_source": True,
            "history_h": "setting_context_a0_b0",
            "history_h_prime": "setting_context_a1_b1",
            "pi1_correlation_value_h": f"{quantum_values[('a0', 'b0')]:.12g}",
            "pi1_correlation_value_h_prime": f"{quantum_values[('a1', 'b1')]:.12g}",
            "pi1_values_differ": abs(quantum_values[("a0", "b0")] - quantum_values[("a1", "b1")]) > TOL,
            "delta_fact_nonempty": True,
            "interpretation": "Source-only quotient cannot factor the contextual correlation readout; CHSH enumeration supplies the stronger no-local-mixture certificate.",
        },
        {
            "witness_id": "bell_polytope_facet_witness",
            "pi0_source_value_h": "convex_hull_of_16_deterministic_strategies",
            "pi0_source_value_h_prime": "Bell_phi_plus_correlation_table",
            "same_pi0_source": False,
            "history_h": "all_local_source_mixtures_have_abs_CHSH_leq_local_bound",
            "history_h_prime": "Bell_state_has_CHSH_above_local_bound",
            "pi1_correlation_value_h": "abs_CHSH<=local_bound",
            "pi1_correlation_value_h_prime": "abs_CHSH>local_bound",
            "pi1_values_differ": True,
            "delta_fact_nonempty": True,
            "interpretation": "Finite Bell facet separates the quantum table from all common-source mixtures.",
        },
    ]


def f49_status_rows(quantum_chsh: float, control_chsh: float, local_bound: float) -> list[dict[str, Any]]:
    return [
        {
            "case_id": "Bell_phi_plus",
            "common_source_factors": quantum_chsh <= local_bound + TOL,
            "interface_factorization_factors": quantum_chsh <= local_bound + TOL,
            "locally_explainable": quantum_chsh <= local_bound + TOL,
            "f49_status": "statused_nonlocal_residual",
            "evidence": f"CHSH={quantum_chsh:.12g} exceeds enumerated local bound {local_bound:.12g}",
        },
        {
            "case_id": "classical_correlated_mixture",
            "common_source_factors": control_chsh <= local_bound + TOL,
            "interface_factorization_factors": control_chsh <= local_bound + TOL,
            "locally_explainable": control_chsh <= local_bound + TOL,
            "f49_status": "common_source_success",
            "evidence": "explicit LHV table reproduces all four control correlations",
        },
    ]


def require_corpus_files(names: list[str]) -> list[Path]:
    root_value = os.environ.get(CORPUS_ROOT_ENV)
    if not root_value:
        raise SystemExit(f"{CORPUS_ROOT_ENV} is required; missing corpus file(s): {', '.join(names)}")
    root = Path(root_value).expanduser().resolve()
    paths = [root / name for name in names]
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"{CORPUS_ROOT_ENV} missing required corpus file: {path}")
    return paths


def frozen_machinery_rows(foundations: list[Path]) -> list[dict[str, Any]]:
    sources = [
        STEP47_DIR / "step47_schema.json",
        STEP47_DIR / "common_carrier_controls_step47.csv",
        STEP47_DIR / "common_carrier_door_test_step47.py",
    ]
    rows = [
        {"source": path.name, "sha256": sha256(path), "imported_or_read_verbatim": True}
        for path in foundations
    ]
    rows.extend(
        {"source": repo_rel(path), "sha256": sha256(path), "imported_or_read_verbatim": True}
        for path in sources
    )
    return rows


def write_summary(schema: dict[str, Any]) -> None:
    text = f"""# Step 52 Results Summary

## Honest Grade First

Bell nonlocality is recovered-known physics. This step recovers it as the F49 common-source / nonlocal-correlation normal form on the QM-GR co-sourcing carrier and adds the SBT-native reconciliation: the common carrier is not a local hidden variable. F49 local explainability requires an accessible source or interface quotient through which readouts factor; F37 complementary non-joint-access forecloses that move for the Bell settings. This is a yes/no structural discriminator and falsification route, not a new measured number, not frame transfer, and not a closure of E018.

## Bell Correlations

The QM arm uses the Bell state `(|00>+|11>)/sqrt(2)` with settings `a0=Z`, `a1=X`, `b0=(Z+X)/sqrt(2)`, `b1=(Z-X)/sqrt(2)`. The correlations are computed from `Tr(rho A_i tensor B_j)`.

Computed quantum CHSH: `{schema['chsh_quantum']:.12g}`.

## Local Bound by Enumeration

All 16 deterministic local strategies were enumerated. The computed maximum absolute CHSH value is `{schema['local_bound_enumerated']:.12g}`. The Bell violation gap is `{schema['violation_gap']:.12g}`.

## F49 Verdict

Since the quantum CHSH value exceeds the enumerated local bound, no probability mixture of the deterministic common-source strategies reproduces the Bell table. The F49 verdict is `{schema['f49_verdict']}`: CommonSource fails, InterfaceFactorization fails, and the correlation is a statused nonlocal residual.

## FIII Delta-Fact Witness

`delta_fact_witness_pair_step52.csv` records a source-only witness pair: the same Bell source under contexts `a0,b0` and `a1,b1` has different correlation readouts. The Bell-polytope row records the stronger finite facet separation: every local-source mixture has `abs(CHSH)<=2`, while the Bell table exceeds it.

## F37 Carrier-Not-Hidden-Variable Tie

The setting commutators are nonzero. Normalized commutator residuals are `{schema['setting_commutators']}`. Step 47's frozen complementary-pair control gives residual `{schema['step47_complementary_commutator_residual']:.12g}` with no admissible joint quotient. Therefore the common carrier cannot be used as an admissible local hidden-variable source for complementary co-readouts.

## Classical Control

The separable mixture `0.5|00><00|+0.5|11><11|` has CHSH `{schema['chsh_classical_control']:.12g}` and is locally explainable. The explicit 16-row LHV table in `classical_control_lhv_table_step52.csv` reproduces all four control correlations exactly within tolerance.

## Forbidden Rule

The forbidden rule is `{schema['forbidden_rule']}`: SBT forbids reading the common carrier as a local hidden variable. A common carrier above the access structure is consistent with Bell experiments; an admissible local common source below complementary accesses is not.
"""
    (ARTIFACT_DIR / "step52_results_summary.md").write_text(text, encoding="utf-8")


def write_nonclaim() -> None:
    (ARTIFACT_DIR / "nonclaim_boundary_step52.md").write_text(
        """# Step 52 Nonclaim Boundary

This step does not discover Bell nonlocality, does not make a new measured prediction, does not certify frame transfer, does not solve quantum gravity, and does not close E018.

The Bell calculation is premise-independent QM. The SBT-specific claim is structural: the QM-GR common-carrier premise does not entail local hidden-variable explainability because F49 local explainability requires an admissible source/interface quotient, and F37 forecloses joint access for complementary settings.

The carrier reading remains conditional on Step 47's LANDED * GROUND common-carrier premise.
""",
        encoding="utf-8",
    )


def write_statement(schema: dict[str, Any]) -> None:
    (ARTIFACT_DIR / "f49_bell_statement_step52.tex").write_text(
        r"""\section*{Step 52: Bell Nonlocality as F49 Residual}

For the Bell state \(|\Phi^+\rangle=(|00\rangle+|11\rangle)/\sqrt2\)
and settings
\[
a_0=Z,\quad a_1=X,\quad b_0=(Z+X)/\sqrt2,\quad b_1=(Z-X)/\sqrt2,
\]
the computed correlations give
\[
\mathrm{CHSH}= """ + f"{schema['chsh_quantum']:.12g}" + r""" .
\]
Enumeration of all 16 deterministic local strategies gives the local bound
\[
\max_\lambda |\mathrm{CHSH}(\lambda)| = """ + f"{schema['local_bound_enumerated']:.12g}" + r""" .
\]
Therefore the Bell table is not reproducible by a local common-source mixture.
In F49 terms, CommonSource and InterfaceFactorization fail, so the Bell
correlation is a statused nonlocal residual.

The classical control \(0.5|00\rangle\langle00|+0.5|11\rangle\langle11|\)
has
\[
\mathrm{CHSH}_{\rm ctl}= """ + f"{schema['chsh_classical_control']:.12g}" + r"""\le """ + f"{schema['local_bound_enumerated']:.12g}" + r""",
\]
and an explicit deterministic-strategy mixture reproduces its correlations.
Thus the F49 test discriminates.

The common QM--GR carrier is not a hidden variable: F49 requires an accessible
source/interface quotient, while F37 non-joint access blocks such a quotient
for complementary Bell settings.
""",
        encoding="utf-8",
    )


def write_classification() -> None:
    write_csv(
        ARTIFACT_DIR / "content_classification_step52.csv",
        [
            {"artifact": "step52_results_summary.md", "classification": "organizational + structural-recognition", "scope": "Summarizes Bell/F49 computation and caveats."},
            {"artifact": "bell_correlations_step52.csv", "classification": "finite-carrier-diagnostic", "scope": "Computed Bell and control correlation tables."},
            {"artifact": "lhv_strategy_enumeration_step52.csv", "classification": "finite-carrier-diagnostic", "scope": "Enumerates all 16 deterministic local strategies and local bound."},
            {"artifact": "classical_control_lhv_table_step52.csv", "classification": "finite-carrier-diagnostic", "scope": "Explicit local common-source mixture for control."},
            {"artifact": "delta_fact_witness_pair_step52.csv", "classification": "finite-carrier-diagnostic", "scope": "FIII witness-pair and Bell-facet records."},
            {"artifact": "f37_commutator_tie_step52.csv", "classification": "finite-carrier-diagnostic", "scope": "Computed setting commutators plus imported Step47 control."},
            {"artifact": "f49_bell_statement_step52.tex", "classification": "analytical-structural finite-carrier-diagnostic", "scope": "F49 normal-form statement; not new physics."},
            {"artifact": "run_step52.py", "classification": "organizational validator", "scope": "Self/chain validation with recomputation teeth."},
        ],
    )


def write_mode_packet() -> None:
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP52_LOCAL_BOUND_ENUMERATED", "status": "active", "description": "The local CHSH bound must come from all 16 deterministic strategies."},
            {"constraint_id": "C_STEP52_CONTROL_LHV_EXPLICIT", "status": "active", "description": "The classical control must have a checked explicit LHV table."},
            {"constraint_id": "C_STEP52_CARRIER_NOT_HIDDEN_VARIABLE", "status": "active", "description": "The F37 non-joint-access tie must block reading L as a local hidden variable."},
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "Bell/EPR nonlocality as F49 normal form and carrier-not-hidden-variable reconciliation",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "structural_discriminator_sub_residual",
                "authorization": "USER-AUTHORIZED promoted reserve item F49",
                "conditional_source": "carrier reading conditional on Step47; Bell computation premise-independent",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_F49BellNonlocalResidual_v1",
                "declared_at_step": 52,
                "objects": "two-qubit Bell state; CHSH settings; 16 local strategies; F49 common-source status; F37 non-joint-access tie",
                "excluded_designs_rationale": "Excludes treating the common carrier as an admissible hidden variable without a source/interface quotient.",
                "non_triviality_argument": "Bell state violates the enumerated local bound while the classical control has an explicit LHV table.",
                "next_grammar_delta": "embed Bell-test access constraints into the broader QM-GR frame-transfer falsification route",
            }
        ],
    )


def write_outputs() -> None:
    foundations = require_corpus_files([FOUNDATIONS_IV_NAME, FOUNDATIONS_III_NAME])
    step47_schema = load_json(STEP47_DIR / "step47_schema.json")
    step47_controls = {row["control"]: row for row in load_csv(STEP47_DIR / "common_carrier_controls_step47.csv")}
    bell_rows, bell_values = correlation_table(bell_phi_plus_density(), "Bell_phi_plus")
    control_rows, control_values = correlation_table(classical_mixture_density(), "classical_correlated_mixture")
    all_corr_rows = bell_rows + control_rows
    strategy_rows = deterministic_strategies()
    local_bound = local_bound_from_strategies(strategy_rows)
    quantum_chsh = chsh(bell_values)
    control_chsh = chsh(control_values)
    lhv_rows = classical_lhv_table()
    lhv_values = lhv_correlations(lhv_rows)
    lhv_check = control_lhv_check_rows(control_values, lhv_values)
    comm_rows = setting_commutators()
    step47_comm = float(step47_controls["complementary_noncommuting_pair"]["value"])
    setting_comm_nonzero = all(row["nonzero"] for row in comm_rows)
    common_source_fails = quantum_chsh > local_bound + TOL
    control_locally_explainable = control_chsh <= local_bound + TOL and all(row["matches"] for row in lhv_check)
    violation_gap = quantum_chsh - local_bound

    schema = {
        "step": 52,
        "orientation": "ModeB_F49_Bell_nonlocal_residual",
        "active_residual": "E018 common-carrier versus Bell local-hidden-variable concern",
        "main_object": "Bell/EPR nonlocality as F49 statused nonlocal residual",
        "verdict": "BELL_NONLOCAL_RESIDUAL_RECOVERED_CARRIER_NOT_HIDDEN_VARIABLE",
        "chsh_quantum": quantum_chsh,
        "local_bound_enumerated": local_bound,
        "strategy_count_enumerated": len(strategy_rows),
        "violation_gap": violation_gap,
        "common_source_fails": common_source_fails,
        "interface_factorization_fails": common_source_fails,
        "f49_verdict": "statused_nonlocal_residual",
        "delta_fact_witness_pair_exhibited": True,
        "f37_carrier_source_foreclosed": bool(step47_schema["complementary_pair_no_carrier"] and setting_comm_nonzero),
        "step47_complementary_commutator_residual": step47_comm,
        "setting_commutators_nonzero": setting_comm_nonzero,
        "setting_commutators": ";".join(f"{row['party']}={row['normalized_commutator_residual']}" for row in comm_rows),
        "chsh_classical_control": control_chsh,
        "classical_control_locally_explainable": control_locally_explainable,
        "classical_control_lhv_table_rows": len(lhv_rows),
        "forbidden_rule": "common_carrier_cannot_be_local_hidden_variable",
        "new_measured_number": False,
        "novel_physics_discovery": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "conditional_on_step47_for_carrier_reading": True,
    }

    write_csv(ARTIFACT_DIR / "bell_correlations_step52.csv", all_corr_rows)
    write_csv(ARTIFACT_DIR / "lhv_strategy_enumeration_step52.csv", strategy_rows)
    write_csv(ARTIFACT_DIR / "classical_control_lhv_table_step52.csv", lhv_rows)
    write_csv(ARTIFACT_DIR / "classical_control_lhv_check_step52.csv", lhv_check)
    write_csv(ARTIFACT_DIR / "f49_factorization_tests_step52.csv", f49_status_rows(quantum_chsh, control_chsh, local_bound))
    write_csv(ARTIFACT_DIR / "delta_fact_witness_pair_step52.csv", delta_fact_witness_rows(bell_values))
    write_csv(ARTIFACT_DIR / "f37_commutator_tie_step52.csv", comm_rows + [
        {
            "party": "Step47_control",
            "setting_1": "complementary_noncommuting_pair",
            "setting_2": "admissible_joint_control",
            "commutator_frobenius_norm": "not_recomputed_here",
            "normalized_commutator_residual": f"{step47_comm:.12g}",
            "nonzero": step47_comm > TOL,
        }
    ])
    write_csv(ARTIFACT_DIR / "frozen_machinery_step52.csv", frozen_machinery_rows(foundations))
    (ARTIFACT_DIR / "step52_schema.json").write_text(json.dumps(schema, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_summary(schema)
    write_nonclaim()
    write_statement(schema)
    write_classification()
    write_mode_packet()


if __name__ == "__main__":
    write_outputs()
