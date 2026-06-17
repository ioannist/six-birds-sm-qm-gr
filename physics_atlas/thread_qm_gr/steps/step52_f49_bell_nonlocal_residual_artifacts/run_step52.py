#!/usr/bin/env python3
"""Validate Step 52 F49 Bell/nonlocal-residual artifacts."""

from __future__ import annotations

import csv
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
STEP47_DIR = THREAD_ROOT / "steps" / "step47_common_carrier_door_test_artifacts"
BUILD_SCRIPT = ARTIFACT_DIR / "f49_bell_nonlocal_residual_step52.py"
TOL = 1e-9


REQUIRED_FILES = [
    "f49_bell_nonlocal_residual_step52.py",
    "step52_results_summary.md",
    "step52_schema.json",
    "content_classification_step52.csv",
    "nonclaim_boundary_step52.md",
    "f49_bell_statement_step52.tex",
    "bell_correlations_step52.csv",
    "lhv_strategy_enumeration_step52.csv",
    "classical_control_lhv_table_step52.csv",
    "classical_control_lhv_check_step52.csv",
    "f49_factorization_tests_step52.csv",
    "delta_fact_witness_pair_step52.csv",
    "f37_commutator_tie_step52.csv",
    "frozen_machinery_step52.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
    "run_step52.py",
]


OVERCLAIM_PATTERNS = [
    r"\btherefore a new measured prediction\b",
    r"\bwe make a new measured prediction\b",
    r"\bnovel physics discovery\b",
    r"\bsolves quantum gravity\b",
    r"\bcloses E018\b",
    r"\bframe transfer certified\b",
    r"\bproves quantum gravity\b",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step52.py: FAIL: {message}")


def read(path: Path) -> str:
    if not path.exists():
        fail(f"missing artifact {path.name}")
    return path.read_text(encoding="utf-8")


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def as_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def pauli() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    identity = np.eye(2, dtype=complex)
    sx = np.array([[0, 1], [1, 0]], dtype=complex)
    sy = np.array([[0, -1j], [1j, 0]], dtype=complex)
    sz = np.array([[1, 0], [0, -1]], dtype=complex)
    return identity, sx, sy, sz


def settings() -> dict[str, dict[str, np.ndarray]]:
    _identity, sx, _sy, sz = pauli()
    root2 = math.sqrt(2.0)
    return {"A": {"a0": sz, "a1": sx}, "B": {"b0": (sz + sx) / root2, "b1": (sz - sx) / root2}}


def bell_density() -> np.ndarray:
    state = np.array([1.0, 0.0, 0.0, 1.0], dtype=complex) / math.sqrt(2.0)
    return np.outer(state, state.conjugate())


def control_density() -> np.ndarray:
    ket00 = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    ket11 = np.array([0.0, 0.0, 0.0, 1.0], dtype=complex)
    return 0.5 * np.outer(ket00, ket00.conjugate()) + 0.5 * np.outer(ket11, ket11.conjugate())


def expectation(rho: np.ndarray, obs_a: np.ndarray, obs_b: np.ndarray) -> float:
    return float(np.real_if_close(np.trace(rho @ np.kron(obs_a, obs_b))))


def correlations(rho: np.ndarray) -> dict[tuple[str, str], float]:
    obs = settings()
    return {
        (a, b): expectation(rho, obs["A"][a], obs["B"][b])
        for a in ["a0", "a1"]
        for b in ["b0", "b1"]
    }


def chsh(vals: dict[tuple[str, str], float]) -> float:
    return vals[("a0", "b0")] + vals[("a0", "b1")] + vals[("a1", "b0")] - vals[("a1", "b1")]


def enumerate_local_bound() -> tuple[int, float]:
    max_abs = 0.0
    count = 0
    for a0 in [-1, 1]:
        for a1 in [-1, 1]:
            for b0 in [-1, 1]:
                for b1 in [-1, 1]:
                    count += 1
                    value = a0 * b0 + a0 * b1 + a1 * b0 - a1 * b1
                    max_abs = max(max_abs, abs(float(value)))
    return count, max_abs


def validate_presence() -> None:
    for name in REQUIRED_FILES:
        if not (ARTIFACT_DIR / name).exists():
            fail(f"missing required artifact {name}")


def validate_schema() -> dict:
    schema = json.loads(read(ARTIFACT_DIR / "step52_schema.json"))
    expected = {
        "verdict": "BELL_NONLOCAL_RESIDUAL_RECOVERED_CARRIER_NOT_HIDDEN_VARIABLE",
        "common_source_fails": True,
        "interface_factorization_fails": True,
        "f49_verdict": "statused_nonlocal_residual",
        "delta_fact_witness_pair_exhibited": True,
        "f37_carrier_source_foreclosed": True,
        "setting_commutators_nonzero": True,
        "classical_control_locally_explainable": True,
        "forbidden_rule": "common_carrier_cannot_be_local_hidden_variable",
        "new_measured_number": False,
        "novel_physics_discovery": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "conditional_on_step47_for_carrier_reading": True,
    }
    for key, value in expected.items():
        if schema.get(key) != value:
            fail(f"schema field {key!r} expected {value!r}, got {schema.get(key)!r}")
    count, bound = enumerate_local_bound()
    if schema["strategy_count_enumerated"] != count:
        fail("schema strategy count does not match recomputation")
    if abs(float(schema["local_bound_enumerated"]) - bound) > TOL:
        fail("schema local bound does not match recomputation")
    bell_chsh = chsh(correlations(bell_density()))
    control_chsh = chsh(correlations(control_density()))
    if abs(float(schema["chsh_quantum"]) - bell_chsh) > TOL:
        fail("schema quantum CHSH does not match recomputation")
    if abs(float(schema["chsh_classical_control"]) - control_chsh) > TOL:
        fail("schema control CHSH does not match recomputation")
    if bell_chsh <= bound + TOL:
        fail("Bell state should violate enumerated local bound")
    if control_chsh > bound + TOL:
        fail("classical control should not violate local bound")
    if abs(float(schema["violation_gap"]) - (bell_chsh - bound)) > TOL:
        fail("schema violation gap does not match recomputation")
    if abs(float(schema["step47_complementary_commutator_residual"]) - 0.707106781187) > 1e-12:
        fail("Step47 imported commutator residual changed")
    return schema


def validate_correlation_table() -> None:
    rows = load_csv(ARTIFACT_DIR / "bell_correlations_step52.csv")
    table = {(row["case_id"], row["a_setting"], row["b_setting"]): float(row["correlation_E"]) for row in rows}
    for case_id, rho in [("Bell_phi_plus", bell_density()), ("classical_correlated_mixture", control_density())]:
        vals = correlations(rho)
        for key, value in vals.items():
            if abs(table[(case_id, key[0], key[1])] - value) > TOL:
                fail(f"correlation table mismatch for {case_id} {key}")


def validate_lhv_enumeration() -> None:
    rows = load_csv(ARTIFACT_DIR / "lhv_strategy_enumeration_step52.csv")
    if len(rows) != 16:
        fail("must enumerate exactly 16 deterministic strategies")
    max_abs = max(float(row["abs_CHSH"]) for row in rows)
    _count, recomputed = enumerate_local_bound()
    if abs(max_abs - recomputed) > TOL:
        fail("LHV table local bound mismatch")
    seen = {(row["a0"], row["a1"], row["b0"], row["b1"]) for row in rows}
    if len(seen) != 16:
        fail("strategy enumeration contains duplicates")


def validate_control_lhv() -> None:
    rows = load_csv(ARTIFACT_DIR / "classical_control_lhv_table_step52.csv")
    if len(rows) != 16:
        fail("control LHV table must contain 16 deterministic rows")
    weights = [float(row["weight"]) for row in rows]
    if any(weight < -TOL for weight in weights):
        fail("control LHV has negative weight")
    if abs(sum(weights) - 1.0) > TOL:
        fail("control LHV weights do not sum to 1")
    corr = {("a0", "b0"): 0.0, ("a0", "b1"): 0.0, ("a1", "b0"): 0.0, ("a1", "b1"): 0.0}
    for row in rows:
        weight = float(row["weight"])
        for a in ["a0", "a1"]:
            for b in ["b0", "b1"]:
                corr[(a, b)] += weight * int(row[a]) * int(row[b])
    target = correlations(control_density())
    for key, value in target.items():
        if abs(corr[key] - value) > 1e-9:
            fail(f"control LHV does not reproduce {key}: {corr[key]} vs {value}")
    checks = load_csv(ARTIFACT_DIR / "classical_control_lhv_check_step52.csv")
    if not all(as_bool(row["matches"]) and float(row["abs_error"]) <= 1e-9 for row in checks):
        fail("control LHV check rows do not all pass")


def validate_f49_and_delta() -> None:
    rows = {row["case_id"]: row for row in load_csv(ARTIFACT_DIR / "f49_factorization_tests_step52.csv")}
    if not rows:
        fail("missing F49 test rows")
    bell = rows["Bell_phi_plus"]
    control = rows["classical_correlated_mixture"]
    if as_bool(bell["locally_explainable"]) or as_bool(bell["common_source_factors"]) or as_bool(bell["interface_factorization_factors"]):
        fail("Bell row must not be locally explainable")
    if not as_bool(control["locally_explainable"]) or not as_bool(control["common_source_factors"]):
        fail("control row must be locally explainable")

    witnesses = {row["witness_id"]: row for row in load_csv(ARTIFACT_DIR / "delta_fact_witness_pair_step52.csv")}
    source_pair = witnesses.get("source_only_Bell_state_context_pair")
    facet = witnesses.get("bell_polytope_facet_witness")
    if source_pair is None or facet is None:
        fail("missing delta-fact witness rows")
    if not as_bool(source_pair["same_pi0_source"]) or not as_bool(source_pair["pi1_values_differ"]) or not as_bool(source_pair["delta_fact_nonempty"]):
        fail("source-only delta-fact witness does not pass")
    if not as_bool(facet["delta_fact_nonempty"]):
        fail("Bell facet witness must record nonempty defect")


def validate_f37_tie() -> None:
    rows = load_csv(ARTIFACT_DIR / "f37_commutator_tie_step52.csv")
    own = [row for row in rows if row["party"] in {"A", "B"}]
    if len(own) != 2:
        fail("must record A and B setting commutators")
    for row in own:
        if not as_bool(row["nonzero"]):
            fail(f"setting commutator should be nonzero: {row}")
        if float(row["normalized_commutator_residual"]) <= TOL:
            fail(f"setting commutator residual should be positive: {row}")
    step47 = [row for row in rows if row["party"] == "Step47_control"]
    if len(step47) != 1:
        fail("missing Step47 F37 control row")
    if abs(float(step47[0]["normalized_commutator_residual"]) - 0.707106781187) > 1e-12:
        fail("Step47 F37 residual mismatch")


def validate_frozen_and_prose() -> None:
    frozen = load_csv(ARTIFACT_DIR / "frozen_machinery_step52.csv")
    sources = {row["source"] for row in frozen}
    required = {
        "Tsiokos_2026_Six_Birds_Foundations_IV_A_Catalog_of_Layer_Agnostic_Structural_Laws.tex",
        "Tsiokos_2026_Six_Birds_Foundations_III_A_Finite_Audited_Interaction_Calculus_for_SBT.tex",
        "physics_atlas/thread_qm_gr/steps/step47_common_carrier_door_test_artifacts/step47_schema.json",
        "physics_atlas/thread_qm_gr/steps/step47_common_carrier_door_test_artifacts/common_carrier_controls_step47.csv",
    }
    if not required.issubset(sources):
        fail("frozen machinery sources incomplete")
    for row in frozen:
        if len(row["sha256"]) != 64 or not as_bool(row["imported_or_read_verbatim"]):
            fail(f"bad frozen source row: {row}")

    combined = "\n".join(
        read(ARTIFACT_DIR / name)
        for name in [
            "step52_results_summary.md",
            "nonclaim_boundary_step52.md",
            "f49_bell_statement_step52.tex",
            "mode_b_grammar_manifest.csv",
        ]
    )
    for needle in [
        "recovered-known",
        "common carrier is not a local hidden variable",
        "statused nonlocal residual",
        "16 deterministic",
        "explicit LHV table",
        "F37",
        "forbidden",
    ]:
        if needle not in combined:
            fail(f"missing required prose: {needle}")
    for pattern in OVERCLAIM_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            fail(f"forbidden overclaim pattern: {pattern}")

    script = read(ARTIFACT_DIR / "f49_bell_nonlocal_residual_step52.py")
    if "2.828" in script or "2*sqrt" in script or "2 * sqrt" in script:
        fail("build script appears to contain a hardcoded Tsirelson value")


def run_step47_self() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "run_step47.py", "--self"],
        cwd=STEP47_DIR,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        fail(f"Step47 self-validator failed:\n{result.stdout}")


def validate_self(run_prior: bool = True) -> None:
    validate_presence()
    validate_schema()
    validate_correlation_table()
    validate_lhv_enumeration()
    validate_control_lhv()
    validate_f49_and_delta()
    validate_f37_tie()
    validate_frozen_and_prose()
    if run_prior:
        run_step47_self()


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--self"
    if mode == "--chain":
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        result = subprocess.run(
            [sys.executable, str(BUILD_SCRIPT)],
            cwd=ARTIFACT_DIR,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            fail(f"build script failed:\n{result.stdout}")
        validate_self(run_prior=True)
        print("run_step52.py: PASS (--chain)")
    elif mode == "--self":
        validate_self(run_prior=True)
        print("run_step52.py: PASS (--self)")
    else:
        fail("usage: run_step52.py [--self|--chain]")


if __name__ == "__main__":
    main()
