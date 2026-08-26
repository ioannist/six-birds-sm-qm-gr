#!/usr/bin/env python3
"""Validate Step 56 gravitational-mediation prediction artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_ROOT = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_ROOT / "steps"

BUILD_SCRIPT = ARTIFACT_DIR / "gravitational_mediation_bmv_prediction_step56.py"
STEP47_SCRIPT = STEPS_DIR / "step47_common_carrier_door_test_artifacts" / "common_carrier_door_test_step47.py"
STEP48_SCRIPT = STEPS_DIR / "step48_ladder_vs_fork_resolution_artifacts" / "ladder_vs_fork_resolution_step48.py"
STEP30_SCRIPT = STEPS_DIR / "step30_qg_directed_reduction_nogo_artifacts" / "directed_reduction_nogo_step30.py"
STEP31_SCRIPT = STEPS_DIR / "step31_qg_fused_object_nogo_artifacts" / "fused_object_nogo_step31.py"
STEP32_TEX = STEPS_DIR / "step32_qg_nogo_theorem_artifacts" / "T_QG_NoGo.tex"
STEP52_SCRIPT = STEPS_DIR / "step52_f49_bell_nonlocal_residual_artifacts" / "f49_bell_nonlocal_residual_step52.py"

EXPECTED_HASHES = {
    "step47_script": "815f68448a5f88f4a6b739fda55a4786c1a314237a184cdf82fb0dd7568af47a",
    "step48_script": "cea0a1531dfa060a8fda2bab685ef73f28a6afb9086d54c7379f9104268e40d5",
    "step30_script": "8fa9a05a32a408b570c1e6f45d2103c05ff3a7d34078eafad75433cf076b0a26",
    "step31_script": "5b2ba3addad33d077a4c89eaa8fd60c3e69d1646f947ad2da7526dfee100a7bd",
    "step32_tex": "f2324e4c568e25e3f37fab9b8437c5e5fe37a3c002720f3bc6ad8fa12a5e8bd3",
    "step52_script": "60c36c517d7bd10306f7059ebfb43ac69083f32cc1dcaf7a7dc3dea9ad8a5bc9",
}
# The published Step 56 artifacts derive from the EXPECTED_HASHES versions.
# The step52_script entry changed on 2026-08-26 by a path-portability-only
# edit, with no behavioral change to any computed number. The published
# frozen_machinery_step56.csv intentionally retains the historical hashes.
CURRENT_HASHES = {
    **EXPECTED_HASHES,
    "step52_script": "aa0dfaf495883891eee2db013e88e8937deeff522e0399ccddfd28bb6ce1baad",
}

REQUIRED_FILES = [
    "gravitational_mediation_bmv_prediction_step56.py",
    "step56_results_summary.md",
    "step56_schema.json",
    "content_classification_step56.csv",
    "nonclaim_boundary_step56.md",
    "gravitational_mediation_statement_step56.tex",
    "channel_outputs_step56.csv",
    "local_bound_enumeration_step56.csv",
    "model_parameters_step56.csv",
    "density_matrices_step56.csv",
    "channel_restriction_derivation_step56.csv",
    "frozen_machinery_step56.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step56.py",
]

OVERCLAIM_PATTERNS = [
    r"\bgravity is classical, period\b",
    r"\bdisproves quantum gravity\b",
    r"\bproves gravity is classical\b",
    r"\bsolves quantum gravity\b",
    r"\bframe transfer certified\b",
    r"\bcloses E018\b",
    r"\bunconditional proof about nature\b",
]

MEAN_FIELD_BAKEIN_PATTERNS = [
    r"\bT00\b",
    r"\bV\[",
    r"\bkappa\s*\*",
    r"\bbackground\s*\+\s*kappa\b",
    r"\bexpectation-value channel\b",
    r"\bexpectation value channel\b",
]

TOL = 1e-9
CONTROL_PHASE = math.pi / 2.0


def fail(message: str) -> None:
    raise SystemExit(f"run_step56.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing artifact {path.name}")
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
    out = np.zeros_like(rho)
    for idx in range(4):
        projector = np.zeros((4, 4), dtype=complex)
        projector[idx, idx] = 1.0
        out += projector @ rho @ projector
    return out


def fused_control_channel(rho: np.ndarray) -> np.ndarray:
    unitary = np.diag([1.0, 1.0, 1.0, complex(math.cos(CONTROL_PHASE), math.sin(CONTROL_PHASE))])
    return unitary @ rho @ unitary.conjugate().T


def partial_transpose_b(rho: np.ndarray) -> np.ndarray:
    return np.transpose(rho.reshape(2, 2, 2, 2), (0, 3, 2, 1)).reshape(4, 4)


def negativity(rho: np.ndarray) -> float:
    evals = np.linalg.eigvalsh(partial_transpose_b(rho))
    return float(np.sum(np.maximum(0.0, -evals)))


def reduced_a(rho: np.ndarray) -> np.ndarray:
    return np.einsum("abcb->ac", rho.reshape(2, 2, 2, 2))


def reduced_b(rho: np.ndarray) -> np.ndarray:
    return np.einsum("abac->bc", rho.reshape(2, 2, 2, 2))


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
    eigs = np.sort(np.maximum(np.linalg.eigvalsh(t_matrix.T @ t_matrix), 0.0))
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


def recompute_metrics() -> dict[str, dict[str, float]]:
    rho0 = density(initial_state())
    initial_coh = local_coherence_abs(rho0)[2]
    cases = {
        "initial_product": rho0,
        "fork_admissible_record_channel": fork_admissible_channel(rho0),
        "forbidden_fused_control": fused_control_channel(rho0),
    }
    result: dict[str, dict[str, float]] = {}
    for case_id, rho in cases.items():
        coh = local_coherence_abs(rho)[2]
        result[case_id] = {
            "negativity": negativity(rho),
            "chsh": chsh_horodecki(rho),
            "coherence_mean": coh,
            "coherence_damping": 1.0 - coh / initial_coh,
            "purity": float(np.real_if_close(np.trace(rho @ rho))),
        }
    return result


def validate_presence() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_hashes() -> None:
    paths = {
        "step47_script": STEP47_SCRIPT,
        "step48_script": STEP48_SCRIPT,
        "step30_script": STEP30_SCRIPT,
        "step31_script": STEP31_SCRIPT,
        "step32_tex": STEP32_TEX,
        "step52_script": STEP52_SCRIPT,
    }
    for key, path in paths.items():
        if sha256(path) != CURRENT_HASHES[key]:
            fail(f"frozen hash mismatch for {key}")
    rows = load_csv(ARTIFACT_DIR / "frozen_machinery_step56.csv")
    row_map = {row["frozen_input"]: row for row in rows}
    for key, expected in EXPECTED_HASHES.items():
        row = row_map.get(key)
        if row is None:
            fail(f"frozen machinery ledger missing {key}")
        if "historical_sha256" in row and "current_sha256" in row:
            if (
                row["historical_sha256"] != expected
                or row["current_sha256"] != CURRENT_HASHES[key]
                or row["matches"] != "True"
            ):
                fail(f"rebuilt frozen machinery ledger mismatch for {key}")
        elif (
            row.get("expected_sha256") != expected
            or row.get("actual_sha256") != expected
            or row.get("matches") != "True"
        ):
            # The committed artifact is frozen publication evidence and retains
            # the original five-column historical ledger.  A fresh rebuild uses
            # the dual-hash branch above.
            fail(f"published frozen machinery ledger mismatch for {key}")


def validate_schema() -> dict:
    schema = json.loads(read(ARTIFACT_DIR / "step56_schema.json"))
    metrics = recompute_metrics()
    count, bound = enumerate_local_bound()
    if schema.get("lhv_strategy_count") != count:
        fail("schema LHV strategy count mismatch")
    if abs(float(schema["local_bound_enumerated"]) - bound) > TOL:
        fail("schema local bound mismatch")
    expected_static = {
        "channel_restriction_derived_from": ["step48_access_tuple", "T_QG_NoGo"],
        "mean_field_channel_used": False,
        "conditional_on_step47_step48": True,
        "gravity_proven_classical": False,
        "disproves_quantum_gravity": False,
        "frame_transfer_certified": False,
        "root_landed": False,
    }
    for key, value in expected_static.items():
        if schema.get(key) != value:
            fail(f"schema {key!r} expected {value!r}, got {schema.get(key)!r}")
    if abs(float(schema["initial_entanglement"]) - metrics["initial_product"]["negativity"]) > TOL:
        fail("initial entanglement does not recompute to schema")
    checks = [
        ("fork_channel_negativity", "fork_admissible_record_channel", "negativity"),
        ("fork_channel_chsh", "fork_admissible_record_channel", "chsh"),
        ("fork_channel_local_coherence_damping", "fork_admissible_record_channel", "coherence_damping"),
        ("control_negativity", "forbidden_fused_control", "negativity"),
        ("control_chsh", "forbidden_fused_control", "chsh"),
        ("control_local_coherence_damping", "forbidden_fused_control", "coherence_damping"),
    ]
    for schema_key, case_id, metric_key in checks:
        if abs(float(schema[schema_key]) - metrics[case_id][metric_key]) > TOL:
            fail(f"schema {schema_key} mismatch")
    fork_entangles = metrics["fork_admissible_record_channel"]["negativity"] > 1e-9
    expected_verdict = (
        "FORK_CHANNEL_MEDIATES_BMV_POSITIVE_COMPATIBLE"
        if fork_entangles
        else "FORK_CHANNEL_DECOHERES_WITHOUT_ENTANGLING_BMV_NULL_PREDICTED"
    )
    if schema.get("verdict") != expected_verdict:
        fail("schema verdict is not derived from fork-channel negativity")
    if schema.get("fork_channel_entangles") != fork_entangles:
        fail("fork_channel_entangles mismatch")
    if metrics["initial_product"]["negativity"] > TOL:
        fail("initial state must be product")
    if metrics["forbidden_fused_control"]["negativity"] <= 1e-9:
        fail("forbidden fused control must entangle")
    if metrics["forbidden_fused_control"]["chsh"] <= bound + 1e-9:
        fail("forbidden fused control must violate the local CHSH bound")
    if metrics["fork_admissible_record_channel"]["negativity"] > 1e-9:
        fail("current schema expects no entanglement for fork channel, but recomputation entangles")
    if metrics["fork_admissible_record_channel"]["chsh"] > bound + 1e-9:
        fail("fork channel should not violate local bound")
    return schema


def validate_channel_table() -> None:
    metrics = recompute_metrics()
    rows = load_csv(ARTIFACT_DIR / "channel_outputs_step56.csv")
    if len(rows) != 3:
        fail("channel output table must contain initial, fork, and control rows")
    for row in rows:
        case_id = row["case_id"]
        if case_id not in metrics:
            fail(f"unexpected channel row {case_id}")
        if abs(float(row["negativity"]) - metrics[case_id]["negativity"]) > TOL:
            fail(f"channel table negativity mismatch for {case_id}")
        if abs(float(row["optimized_CHSH"]) - metrics[case_id]["chsh"]) > TOL:
            fail(f"channel table CHSH mismatch for {case_id}")
        if abs(float(row["coherence_damping_fraction"]) - metrics[case_id]["coherence_damping"]) > TOL:
            fail(f"channel table coherence mismatch for {case_id}")


def validate_local_bound_table() -> None:
    rows = load_csv(ARTIFACT_DIR / "local_bound_enumeration_step56.csv")
    if len(rows) != 16:
        fail("must enumerate exactly 16 deterministic strategies")
    max_abs = max(float(row["abs_CHSH"]) for row in rows)
    _count, bound = enumerate_local_bound()
    if abs(max_abs - bound) > TOL:
        fail("local bound table does not match enumeration")


def validate_derivation_rows() -> None:
    rows = load_csv(ARTIFACT_DIR / "channel_restriction_derivation_step56.csv")
    sources = {row["source"] for row in rows}
    required = {"Step48_access_tuple", "Step31_fused_object_no_go", "Step32_T_QG_NoGo", "Step52_entanglement_certificate"}
    if not required.issubset(sources):
        fail("channel restriction derivation does not cite all frozen structural inputs")
    text = "\n".join(",".join(row.values()) for row in rows)
    for phrase in ["q_GR=(d0,d2,d3)", "excluding d1", "fused routes fail", "local_bound"]:
        if phrase not in text:
            fail(f"derivation rows missing load-bearing phrase {phrase!r}")


def validate_no_bakein_or_overclaim() -> None:
    scan_files = [
        BUILD_SCRIPT,
        ARTIFACT_DIR / "step56_results_summary.md",
        ARTIFACT_DIR / "nonclaim_boundary_step56.md",
        ARTIFACT_DIR / "gravitational_mediation_statement_step56.tex",
        ARTIFACT_DIR / "content_classification_step56.csv",
        ARTIFACT_DIR / "channel_restriction_derivation_step56.csv",
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
    ]
    for path in scan_files:
        text = read(path)
        lower = text.lower()
        for pattern in OVERCLAIM_PATTERNS:
            if re.search(pattern, lower):
                fail(f"overclaim phrase {pattern!r} found in {path.name}")
        for pattern in MEAN_FIELD_BAKEIN_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                fail(f"mean-field bake-in token {pattern!r} found in {path.name}")


def run_prior_self_checks() -> None:
    commands = [
        [sys.executable, str(STEPS_DIR / "step47_common_carrier_door_test_artifacts" / "run_step47.py"), "--self"],
        [sys.executable, str(STEPS_DIR / "step48_ladder_vs_fork_resolution_artifacts" / "run_step48.py"), "--self"],
        [sys.executable, str(STEPS_DIR / "step52_f49_bell_nonlocal_residual_artifacts" / "run_step52.py"), "--self"],
    ]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for command in commands:
        proc = subprocess.run(command, cwd=THREAD_ROOT, env=env, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            fail(f"prior validator failed: {' '.join(command)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")


def validate_self() -> None:
    validate_presence()
    validate_hashes()
    validate_schema()
    validate_channel_table()
    validate_local_bound_table()
    validate_derivation_rows()
    validate_no_bakein_or_overclaim()


def main() -> None:
    mode = "--self"
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    if mode not in {"--self", "--chain"}:
        fail("usage: run_step56.py [--self|--chain]")
    validate_self()
    if mode == "--chain":
        run_prior_self_checks()
    print(f"run_step56.py: PASS ({mode})")


if __name__ == "__main__":
    main()
