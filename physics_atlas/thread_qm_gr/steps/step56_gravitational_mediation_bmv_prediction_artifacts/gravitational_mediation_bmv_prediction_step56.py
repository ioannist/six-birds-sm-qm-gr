#!/usr/bin/env python3
"""Step 56: gravitational mediation prediction from the frozen QM-GR fork.

The computation is intentionally small and explicit. Two matter parties start
in local path superpositions. The fork-admissible geometry arm can read and
record only geometry-visible path classes; the coherent phase mediator is built
only as the forbidden fused-object control.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path("/home/repos/six-birds-papers")
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_ROOT / "steps"

STEP47_SCRIPT = STEPS_DIR / "step47_common_carrier_door_test_artifacts" / "common_carrier_door_test_step47.py"
STEP48_SCRIPT = STEPS_DIR / "step48_ladder_vs_fork_resolution_artifacts" / "ladder_vs_fork_resolution_step48.py"
STEP48_SCHEMA = STEPS_DIR / "step48_ladder_vs_fork_resolution_artifacts" / "step48_schema.json"
STEP30_SCRIPT = STEPS_DIR / "step30_qg_directed_reduction_nogo_artifacts" / "directed_reduction_nogo_step30.py"
STEP31_SCRIPT = STEPS_DIR / "step31_qg_fused_object_nogo_artifacts" / "fused_object_nogo_step31.py"
STEP31_SCHEMA = STEPS_DIR / "step31_qg_fused_object_nogo_artifacts" / "step31_schema.json"
STEP32_TEX = STEPS_DIR / "step32_qg_nogo_theorem_artifacts" / "T_QG_NoGo.tex"
STEP32_SCHEMA = STEPS_DIR / "step32_qg_nogo_theorem_artifacts" / "step32_schema.json"
STEP52_SCRIPT = STEPS_DIR / "step52_f49_bell_nonlocal_residual_artifacts" / "f49_bell_nonlocal_residual_step52.py"
STEP52_SCHEMA = STEPS_DIR / "step52_f49_bell_nonlocal_residual_artifacts" / "step52_schema.json"

EXPECTED_HASHES = {
    "step47_script": "815f68448a5f88f4a6b739fda55a4786c1a314237a184cdf82fb0dd7568af47a",
    "step48_script": "cea0a1531dfa060a8fda2bab685ef73f28a6afb9086d54c7379f9104268e40d5",
    "step30_script": "8fa9a05a32a408b570c1e6f45d2103c05ff3a7d34078eafad75433cf076b0a26",
    "step31_script": "5b2ba3addad33d077a4c89eaa8fd60c3e69d1646f947ad2da7526dfee100a7bd",
    "step32_tex": "f2324e4c568e25e3f37fab9b8437c5e5fe37a3c002720f3bc6ad8fa12a5e8bd3",
    "step52_script": "60c36c517d7bd10306f7059ebfb43ac69083f32cc1dcaf7a7dc3dea9ad8a5bc9",
}

TOL = 1e-10
CONTROL_PHASE = math.pi / 2.0


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(THREAD_ROOT.resolve()))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    if fieldnames is None:
        if not rows:
            raise ValueError(f"no rows for {path}")
        fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pauli() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    identity = np.eye(2, dtype=complex)
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return identity, sx, sy, sz


def ket_plus() -> np.ndarray:
    return np.array([1.0, 1.0], dtype=complex) / math.sqrt(2.0)


def initial_state() -> np.ndarray:
    return np.kron(ket_plus(), ket_plus())


def density(state: np.ndarray) -> np.ndarray:
    return np.outer(state, state.conjugate())


def fork_admissible_channel(rho: np.ndarray) -> np.ndarray:
    """Geometry-visible record channel: complete path-class dephasing."""
    out = np.zeros_like(rho)
    for idx in range(4):
        projector = np.zeros((4, 4), dtype=complex)
        projector[idx, idx] = 1.0
        out += projector @ rho @ projector
    return out


def fused_control_channel(rho: np.ndarray, phase: float = CONTROL_PHASE) -> np.ndarray:
    """Forbidden coherent phase control: no record is left in the mediator."""
    unitary = np.diag([1.0, 1.0, 1.0, complex(math.cos(phase), math.sin(phase))])
    return unitary @ rho @ unitary.conjugate().T


def partial_transpose_b(rho: np.ndarray) -> np.ndarray:
    reshaped = rho.reshape(2, 2, 2, 2)
    return np.transpose(reshaped, (0, 3, 2, 1)).reshape(4, 4)


def negativity(rho: np.ndarray) -> float:
    evals = np.linalg.eigvalsh(partial_transpose_b(rho))
    return float(np.sum(np.maximum(0.0, -evals)))


def reduced_a(rho: np.ndarray) -> np.ndarray:
    reshaped = rho.reshape(2, 2, 2, 2)
    return np.einsum("abcb->ac", reshaped)


def reduced_b(rho: np.ndarray) -> np.ndarray:
    reshaped = rho.reshape(2, 2, 2, 2)
    return np.einsum("abac->bc", reshaped)


def local_coherence_abs(rho: np.ndarray) -> tuple[float, float, float]:
    coh_a = abs(reduced_a(rho)[0, 1])
    coh_b = abs(reduced_b(rho)[0, 1])
    return float(coh_a), float(coh_b), float((coh_a + coh_b) / 2.0)


def chsh_horodecki(rho: np.ndarray) -> float:
    _identity, sx, sy, sz = pauli()
    sigmas = [sx, sy, sz]
    t_matrix = np.zeros((3, 3), dtype=float)
    for i, op_a in enumerate(sigmas):
        for j, op_b in enumerate(sigmas):
            value = np.trace(rho @ np.kron(op_a, op_b))
            t_matrix[i, j] = float(np.real_if_close(value))
    eigs = np.linalg.eigvalsh(t_matrix.T @ t_matrix)
    eigs = np.sort(np.maximum(eigs, 0.0))
    return float(2.0 * math.sqrt(eigs[-1] + eigs[-2]))


def enumerate_local_bound() -> tuple[int, float]:
    count = 0
    max_abs = 0.0
    for a0 in [-1, 1]:
        for a1 in [-1, 1]:
            for b0 in [-1, 1]:
                for b1 in [-1, 1]:
                    count += 1
                    value = a0 * b0 + a0 * b1 + a1 * b0 - a1 * b1
                    max_abs = max(max_abs, abs(float(value)))
    return count, max_abs


def channel_rows() -> tuple[list[dict[str, Any]], dict[str, dict[str, float]]]:
    rho0 = density(initial_state())
    initial_coh = local_coherence_abs(rho0)[2]
    local_count, local_bound = enumerate_local_bound()
    cases = [
        ("initial_product", "none", rho0),
        ("fork_admissible_record_channel", "geometry_visible_record_dephasing", fork_admissible_channel(rho0)),
        ("forbidden_fused_control", "coherent_phase_no_record", fused_control_channel(rho0)),
    ]
    rows: list[dict[str, Any]] = []
    metrics: dict[str, dict[str, float]] = {}
    for case_id, channel_class, rho in cases:
        coh_a, coh_b, coh_mean = local_coherence_abs(rho)
        damp = 0.0 if initial_coh <= 0 else 1.0 - coh_mean / initial_coh
        neg = negativity(rho)
        chsh = chsh_horodecki(rho)
        purity = float(np.real_if_close(np.trace(rho @ rho)))
        metrics[case_id] = {
            "negativity": neg,
            "chsh": chsh,
            "coherence_a": coh_a,
            "coherence_b": coh_b,
            "coherence_mean": coh_mean,
            "coherence_damping": damp,
            "purity": purity,
            "local_bound": local_bound,
            "strategy_count": float(local_count),
        }
        rows.append(
            {
                "case_id": case_id,
                "channel_class": channel_class,
                "negativity": f"{neg:.15g}",
                "optimized_CHSH": f"{chsh:.15g}",
                "enumerated_local_bound": f"{local_bound:.15g}",
                "CHSH_violates_local_bound": chsh > local_bound + TOL,
                "local_coherence_A_abs": f"{coh_a:.15g}",
                "local_coherence_B_abs": f"{coh_b:.15g}",
                "mean_local_coherence_abs": f"{coh_mean:.15g}",
                "coherence_damping_fraction": f"{damp:.15g}",
                "purity": f"{purity:.15g}",
                "entangles": neg > 1e-9,
            }
        )
    return rows, metrics


def local_bound_rows() -> list[dict[str, Any]]:
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
                            "CHSH_value": f"{value:.15g}",
                            "abs_CHSH": f"{abs(float(value)):.15g}",
                        }
                    )
    return rows


def model_parameter_rows() -> list[dict[str, Any]]:
    return [
        {
            "object": "party_A",
            "dimension": 2,
            "visible_basis": "path bit a in {0,1}",
            "qm_only_mode": "relative phase in local superposition",
        },
        {
            "object": "party_B",
            "dimension": 2,
            "visible_basis": "path bit b in {0,1}",
            "qm_only_mode": "relative phase in local superposition",
        },
        {
            "object": "fork_admissible_mediator_record",
            "dimension": 4,
            "visible_basis": "record label (a,b)",
            "qm_only_mode": "absent by fork access tuple and fused-route no-go",
        },
        {
            "object": "forbidden_control_phase",
            "dimension": 1,
            "visible_basis": "not a record channel",
            "qm_only_mode": f"coherent conditional phase phi={CONTROL_PHASE:.12g}",
        },
    ]


def frozen_rows() -> list[dict[str, Any]]:
    paths = {
        "step47_script": STEP47_SCRIPT,
        "step48_script": STEP48_SCRIPT,
        "step30_script": STEP30_SCRIPT,
        "step31_script": STEP31_SCRIPT,
        "step32_tex": STEP32_TEX,
        "step52_script": STEP52_SCRIPT,
    }
    rows = []
    for key, path in paths.items():
        actual = sha256(path)
        rows.append(
            {
                "frozen_input": key,
                "thread_relative_path": rel(path),
                "expected_sha256": EXPECTED_HASHES[key],
                "actual_sha256": actual,
                "matches": actual == EXPECTED_HASHES[key],
            }
        )
    return rows


def derivation_rows() -> list[dict[str, Any]]:
    step48 = load_json(STEP48_SCHEMA)
    step31 = load_json(STEP31_SCHEMA)
    step32 = load_json(STEP32_SCHEMA)
    step52 = load_json(STEP52_SCHEMA)
    return [
        {
            "source": "Step48_access_tuple",
            "frozen_path": rel(STEP48_SCHEMA),
            "used_fact": "L=(d0,d1,d2,d3); q_QM=(d0,d1,d2); q_GR=(d0,d2,d3)",
            "computed_status": f"fork_closes={step48['fork_closes']}; weak_rt_ladder_defect={step48['weak_rt_ladder_defect']}",
            "channel_consequence": "geometry arm cannot access the d1 phase mode of either path qubit; q_GR excluding d1 is load-bearing",
        },
        {
            "source": "Step31_fused_object_no_go",
            "frozen_path": rel(STEP31_SCHEMA),
            "used_fact": "union, shared-audit, and directed fused routes fail",
            "computed_status": f"union_route_passes={step31['final_verdict']['union_route_passes']}; shared_audit_route_passes={step31['final_verdict']['shared_audit_route_passes']}",
            "channel_consequence": "coherent amplitude-over-geometry mediator is not fork-admissible",
        },
        {
            "source": "Step32_T_QG_NoGo",
            "frozen_path": rel(STEP32_SCHEMA),
            "used_fact": "directed and fused routes blocked in bounded grammar",
            "computed_status": f"directed_route_blocked={step32['final_verdict']['directed_route_blocked']}; union_route_blocked={step32['final_verdict']['union_route_blocked']}",
            "channel_consequence": "the allowed mediator is classically indexed by geometry-visible records",
        },
        {
            "source": "Step52_entanglement_certificate",
            "frozen_path": rel(STEP52_SCHEMA),
            "used_fact": "local bound enumerated over 16 deterministic strategies",
            "computed_status": f"local_bound={step52['local_bound_enumerated']}; Bell_CHSH={step52['chsh_quantum']}",
            "channel_consequence": "output CHSH is compared to the same finite local certificate",
        },
    ]


def density_matrix_rows() -> list[dict[str, Any]]:
    rho0 = density(initial_state())
    rows = []
    matrices = [
        ("initial_product", rho0),
        ("fork_admissible_record_channel", fork_admissible_channel(rho0)),
        ("forbidden_fused_control", fused_control_channel(rho0)),
    ]
    for case_id, rho in matrices:
        for i in range(4):
            for j in range(4):
                value = rho[i, j]
                rows.append(
                    {
                        "case_id": case_id,
                        "row": i,
                        "col": j,
                        "real": f"{float(value.real):.15g}",
                        "imag": f"{float(value.imag):.15g}",
                    }
                )
    return rows


def write_results_summary(schema: dict[str, Any]) -> None:
    text = f"""# Step 56 Results Summary

## Honest Grade First
This is a finite static toy computation of the QM-GR fork grammar's mediation verdict. It is conditional on the Step-47 `LANDED_GROUND_CONDITIONAL` common-carrier premise and the Step-48 fork decision; it is not frame transfer, not a proof about nature, and not a solution of quantum gravity. The standard part is that classically indexed channels do not create entanglement; the SBT-native content is that the frozen fork/no-go machinery places the geometry arm on that side of the channel dichotomy.

## Model
Two matter parties are two path qubits, initially `|+>_A |+>_B`, so the initial negativity is `{schema['initial_entanglement']:.12g}`. The geometry-visible data are the path labels `(a,b)`. The QM-only mode is the relative phase carried by the path superposition.

The fork-admissible mediator is a four-label record channel over `(a,b)`. It dephases the two-party state in the path basis because Step 48 gives `q_GR=(d0,d2,d3)`, excluding `d1`, and Step 31/32 block the fused amplitude-over-geometry object. The coherent phase mediator is included only as the forbidden control.

## Computed Table
| channel | negativity | optimized CHSH | local coherence damping |
|---|---:|---:|---:|
| fork-admissible record channel | `{schema['fork_channel_negativity']:.12g}` | `{schema['fork_channel_chsh']:.12g}` | `{schema['fork_channel_local_coherence_damping']:.12g}` |
| forbidden fused control | `{schema['control_negativity']:.12g}` | `{schema['control_chsh']:.12g}` | `{schema['control_local_coherence_damping']:.12g}` |

The enumerated local CHSH bound is `{schema['local_bound_enumerated']:.12g}` from `{schema['lhv_strategy_count']}` deterministic strategies. The fork channel remains separable and below the local bound while damping local path coherence. The forbidden coherent control entangles and exceeds the local bound, so the test discriminates.

## Verdict
`{schema['verdict']}`.

The computed fork-channel output has zero negativity, CHSH no larger than the enumerated local bound, and full local coherence damping. The control has positive negativity and CHSH above the local bound.

## Falsifiable Prediction
{schema['prediction']}

Falsification condition: {schema['falsification_condition']}

## Overlap And Contrast
This overlaps the LOCC theorem and Kafri-Taylor-Milburn-style classical-channel expectations. It contrasts with the mainstream expectation that a BMV-positive result would indicate a coherent gravitational mediator. In this grammar, a confirmed BMV-positive result would refute the fork/co-sourcing reading used here.
"""
    (ARTIFACT_DIR / "step56_results_summary.md").write_text(text, encoding="utf-8")


def write_nonclaim_boundary() -> None:
    text = """# Step 56 Nonclaim Boundary

This step does not prove that gravity is classical in nature, does not disprove quantum gravity, does not certify frame transfer, and does not solve quantum gravity.

It is a finite toy computation inside the QM-GR fork grammar. The BMV-facing prediction is conditional on the Step-47 common-carrier premise and the Step-48 fork decision.

The result is not obtained from the Step-26 semiclassical update. The mediation channel is fixed by the access tuple and the fused-object no-go, then tested by explicit two-qubit output states.

The coherent phase channel is a can-fail control, not an admitted model in this grammar.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step56.md").write_text(text, encoding="utf-8")


def write_statement(schema: dict[str, Any]) -> None:
    text = r"""\section*{Step 56: Gravitational Mediation in the Fork Grammar}

\paragraph{Statement.}
In the bounded QM--GR fork grammar with parent carrier
$L=(d_0,d_1,d_2,d_3)$, the endpoint readouts are
$q_{\rm QM}=(d_0,d_1,d_2)$ and $q_{\rm GR}=(d_0,d_2,d_3)$.
Thus the geometry arm does not access the $d_1$ phase mode. Together
with the bounded no-go against a fused amplitude-over-geometry object,
the admissible mediator is a geometry-visible record channel.

\paragraph{Finite carrier.}
Let the two matter systems be path qubits initially in
$|+\rangle_A|+\rangle_B$. The admissible mediator records the path
class $(a,b)$ and the forbidden control applies a coherent conditional
phase $\phi=\pi/2$ without leaving a record.

\paragraph{Computation.}
For the fork-admissible channel the output negativity is
@FORK_NEG@, the optimized CHSH value is
@FORK_CHSH@, and the local coherence damping is
@FORK_DAMPING@. For the forbidden
coherent control the output negativity is @CONTROL_NEG@
and the optimized CHSH value is @CONTROL_CHSH@.

\paragraph{Prediction.}
Within this grammar, gravitational mediation is predicted to decohere
path superpositions without generating matter--matter entanglement.
A confirmed gravitationally mediated entanglement signal would falsify
this fork-channel reading.
"""
    text = (
        text.replace("@FORK_NEG@", f"{schema['fork_channel_negativity']:.12g}")
        .replace("@FORK_CHSH@", f"{schema['fork_channel_chsh']:.12g}")
        .replace("@FORK_DAMPING@", f"{schema['fork_channel_local_coherence_damping']:.12g}")
        .replace("@CONTROL_NEG@", f"{schema['control_negativity']:.12g}")
        .replace("@CONTROL_CHSH@", f"{schema['control_chsh']:.12g}")
    )
    (ARTIFACT_DIR / "gravitational_mediation_statement_step56.tex").write_text(text, encoding="utf-8")


def write_classification() -> None:
    rows = [
        {
            "artifact": "step56_results_summary.md",
            "classification": "finite-carrier-diagnostic",
            "scope": "computed fork-channel mediation verdict and falsifiable BMV-facing prediction",
        },
        {
            "artifact": "channel_outputs_step56.csv",
            "classification": "finite-carrier-diagnostic",
            "scope": "negativity, optimized CHSH, and local coherence metrics",
        },
        {
            "artifact": "channel_restriction_derivation_step56.csv",
            "classification": "structural-recognition",
            "scope": "frozen fork and no-go inputs used to classify the admissible channel",
        },
        {
            "artifact": "nonclaim_boundary_step56.md",
            "classification": "organizational",
            "scope": "scope limits and forbidden overclaims",
        },
        {
            "artifact": "gravitational_mediation_statement_step56.tex",
            "classification": "analytical-structural",
            "scope": "formal statement of the toy prediction",
        },
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step56.csv", rows)


def write_mode_packet() -> None:
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {
                "constraint_id": "C_STEP56_FORK_CHANNEL_FROM_ACCESS_TUPLE",
                "status": "active",
                "description": "mediator access restricted by Step48 q_GR excluding d1",
            },
            {
                "constraint_id": "C_STEP56_FUSED_CONTROL_CANFAIL",
                "status": "active",
                "description": "forbidden coherent control must entangle or the discriminator fails",
            },
            {
                "constraint_id": "C_STEP56_NO_MEAN_FIELD_BAKEIN",
                "status": "active",
                "description": "mediation channel is not the Step26 update channel",
            },
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "BMV gravitational mediation prediction",
                "canonical_target": "R_root_E018",
                "relation_to_canonical_root": "user_authorized_falsifiable_prediction_from_fork",
                "source_steps": "47;48;30;31;32;52",
            }
        ],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_E018_ForkMediationBMV_v1",
                "carrier": "two path qubits plus geometry-visible record mediator",
                "admitted_channel": "classically indexed path-record channel",
                "forbidden_control": "coherent conditional phase mediator",
                "non_triviality_argument": "the forbidden control entangles while the admitted channel does not",
                "next_grammar_delta": "frame-transfer to a physical BMV platform or rejection by BMV-positive observation",
            }
        ],
    )


def main() -> None:
    channel_table, metrics = channel_rows()
    local_count, local_bound = enumerate_local_bound()
    fork = metrics["fork_admissible_record_channel"]
    control = metrics["forbidden_fused_control"]
    initial = metrics["initial_product"]

    fork_entangles = fork["negativity"] > 1e-9
    if fork_entangles:
        verdict = "FORK_CHANNEL_MEDIATES_BMV_POSITIVE_COMPATIBLE"
        prediction = (
            "The fork-admissible mediation channel generates entanglement on the finite carrier; "
            "a BMV-positive result would not by itself imply the forbidden fused object in this grammar."
        )
        falsifier = "A robust BMV-null result with only decoherence would falsify this computed channel verdict on the toy reading."
    else:
        verdict = "FORK_CHANNEL_DECOHERES_WITHOUT_ENTANGLING_BMV_NULL_PREDICTED"
        prediction = (
            "Gravitationally induced entanglement is not expected in BMV-type experiments under the fork grammar: "
            "the geometry arm behaves as a classically indexed record channel, producing decoherence without matter-matter entanglement."
        )
        falsifier = (
            "A confirmed BMV-positive observation of gravitationally mediated entanglement between masses would falsify "
            "the fork-channel reading; a direct confirmed free-gravitational quantum would also reject it."
        )

    schema = {
        "step": 56,
        "orientation": "QM_GR_fork_gravitational_mediation_BMV_prediction",
        "active_residual": "E018 gravitational mediation prediction from fork grammar",
        "verdict": verdict,
        "initial_entanglement": initial["negativity"],
        "party_dimension_A": 2,
        "party_dimension_B": 2,
        "mediator_record_dimension": 4,
        "control_phase_radians": CONTROL_PHASE,
        "local_bound_enumerated": local_bound,
        "lhv_strategy_count": local_count,
        "fork_channel_negativity": fork["negativity"],
        "fork_channel_chsh": fork["chsh"],
        "fork_channel_local_coherence_abs": fork["coherence_mean"],
        "fork_channel_local_coherence_damping": fork["coherence_damping"],
        "fork_channel_entangles": fork_entangles,
        "control_negativity": control["negativity"],
        "control_chsh": control["chsh"],
        "control_local_coherence_abs": control["coherence_mean"],
        "control_local_coherence_damping": control["coherence_damping"],
        "control_entangles": control["negativity"] > 1e-9,
        "control_violates_local_bound": control["chsh"] > local_bound + 1e-9,
        "channel_restriction_derived_from": ["step48_access_tuple", "T_QG_NoGo"],
        "mean_field_channel_used": False,
        "prediction": prediction,
        "falsification_condition": falsifier,
        "overlaps": ["LOCC_theorem", "KTM_classical_channel"],
        "contradicts": "mainstream_expectation_BMV_positive",
        "conditional_on_step47_step48": True,
        "gravity_proven_classical": False,
        "disproves_quantum_gravity": False,
        "frame_transfer_certified": False,
        "root_landed": False,
    }

    write_csv(ARTIFACT_DIR / "channel_outputs_step56.csv", channel_table)
    write_csv(ARTIFACT_DIR / "local_bound_enumeration_step56.csv", local_bound_rows())
    write_csv(ARTIFACT_DIR / "model_parameters_step56.csv", model_parameter_rows())
    write_csv(ARTIFACT_DIR / "density_matrices_step56.csv", density_matrix_rows())
    write_csv(ARTIFACT_DIR / "channel_restriction_derivation_step56.csv", derivation_rows())
    write_csv(ARTIFACT_DIR / "frozen_machinery_step56.csv", frozen_rows())
    write_json(ARTIFACT_DIR / "step56_schema.json", schema)
    write_results_summary(schema)
    write_nonclaim_boundary()
    write_statement(schema)
    write_classification()
    write_mode_packet()


if __name__ == "__main__":
    main()
