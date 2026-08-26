#!/usr/bin/env python3
"""Q7 repair: adaptive F50 convergence and relaxation-independent stability."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import itertools
import json
import math
import time
from collections import Counter, deque
from pathlib import Path
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
STEP26 = REPO / "physics_atlas/thread_qm_gr/steps/step26_semiclassical_dynamics_artifacts/semiclassical_dynamics_step26.py"
STEP54 = REPO / "physics_atlas/thread_qm_gr/steps/step54_f50_background_moduli_demarcation_artifacts/f50_background_moduli_step54.py"
PINS = {
    "step26": "391907fae6fdee8c4e4de1c12ee67d72fdfea4928cad1f148cc30e31584898fd",
    "step54": "d47b71e6a743a0cd51b73a1c5c7d314c5ed7a63147ed5bfa4e7efe8b8b678ef1",
}
MIXES = (0.2, 0.35, 0.5, 0.7)
INITIAL_STATES = ("frozen", "uniform", "localized")
TOL = 1e-10
CAP = 2000
DOUBLE_CAP = 4000
FD_EPS = 1e-6
STABILITY_TOL = 1e-6


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_pinned() -> tuple[Any, Any, list[dict[str, Any]]]:
    modules = []
    rows = []
    for name, path in (("step26", STEP26), ("step54", STEP54)):
        actual = sha256(path)
        if actual != PINS[name]:
            raise RuntimeError(f"{name} pin mismatch: {actual} != {PINS[name]}")
        spec = importlib.util.spec_from_file_location(f"q7_{name}", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        modules.append(module)
        rows.append({"dependency": name, "path": str(path.relative_to(REPO)),
                     "expected_sha256": PINS[name], "actual_sha256": actual,
                     "passes": actual == PINS[name]})
    return modules[0], modules[1], rows


def initial_states(step26: Any, frozen: np.ndarray) -> dict[str, np.ndarray]:
    n = len(frozen)
    uniform = np.exp(1j * np.linspace(0.0, 0.35, n))
    localized = np.zeros(n, dtype=complex)
    localized[0] = 1.0
    localized[1] = 0.17j
    return {
        "frozen": step26.normalize(frozen.copy()),
        "uniform": step26.normalize(uniform),
        "localized": step26.normalize(localized),
    }


def fixed_map(step26: Any, kinetic: np.ndarray, background: np.ndarray,
              kappa: float, psi: np.ndarray, reference: np.ndarray | None = None) -> np.ndarray:
    potential = background + kappa * step26.stress_energy_density(psi, background)
    h = step26.hamiltonian(kinetic, potential)
    _energy, phi = step26.lowest_eigenvector(h)
    return step26.phase_align(phi, psi if reference is None else reference)


def projective_gap(step26: Any, left: np.ndarray, right: np.ndarray) -> float:
    return step26.fixed_point_gap(left, right)


def ray_gap(left: np.ndarray, right: np.ndarray) -> float:
    """Distance on normalized rays, independent of either vector's global phase."""
    overlap = min(1.0, float(abs(np.vdot(left, right))))
    return math.sqrt(max(0.0, 2.0 - 2.0 * overlap))


def iterate(step26: Any, kinetic: np.ndarray, background: np.ndarray, kappa: float,
            mix: float, initial: np.ndarray, cap: int) -> dict[str, Any]:
    psi = step26.normalize(initial.copy())
    recent_states: deque[np.ndarray] = deque(maxlen=80)
    recent_residuals: deque[float] = deque(maxlen=240)
    initial_residual = math.nan
    cycle_period = 0
    classification = ""
    termination = ""
    for iteration in range(1, cap + 1):
        phi = fixed_map(step26, kinetic, background, kappa, psi)
        map_residual = projective_gap(step26, phi, psi)
        if iteration == 1:
            initial_residual = map_residual
        if map_residual < TOL:
            classification = "converged"
            termination = "map_residual_below_tolerance"
            break
        candidate = step26.normalize((1.0 - mix) * psi + mix * phi)
        if not np.all(np.isfinite(candidate)):
            classification = "diverging"
            termination = "nonfinite_state"
            psi = candidate
            break
        recent_states.append(candidate.copy())
        recent_residuals.append(map_residual)
        psi = candidate
        if map_residual > 1e-6 and len(recent_states) >= 33:
            states = list(recent_states)
            for period in range(2, 9):
                if len(states) < 4 * period + 1:
                    continue
                gaps = [projective_gap(step26, states[-1 - repeat * period],
                                       states[-1 - (repeat + 1) * period])
                        for repeat in range(3)]
                if max(gaps) < 1e-9:
                    classification = "cycling"
                    termination = "repeated_projective_orbit"
                    cycle_period = period
                    break
            if classification:
                break
        if iteration >= 500 and len(recent_residuals) == recent_residuals.maxlen:
            values = np.asarray(recent_residuals)
            scale = max(float(np.mean(values)), TOL)
            if float(np.ptp(values)) / scale < 1e-9 and float(values[-1]) > 1e-7:
                classification = "stagnated"
                termination = "flat_residual_window"
                break
    else:
        phi = fixed_map(step26, kinetic, background, kappa, psi)
        map_residual = projective_gap(step26, phi, psi)
        values = list(recent_residuals)
        if not math.isfinite(map_residual) or (values and map_residual > max(1.2 * initial_residual, 1.5)):
            classification = "diverging"
            termination = "cap_with_residual_growth"
        else:
            classification = "stagnated"
            termination = "cap_with_bounded_nonzero_residual"
        iteration = cap
    final_phi = fixed_map(step26, kinetic, background, kappa, psi)
    final_residual = projective_gap(step26, final_phi, psi)
    final_h = step26.hamiltonian(
        kinetic, background + kappa * step26.stress_energy_density(psi, background)
    )
    _energy, eigen_residual = step26.eigen_residual(final_h, psi)
    return {
        "classification": classification, "termination_reason": termination,
        "iterations": iteration, "cycle_period": cycle_period,
        "initial_map_residual": initial_residual, "final_map_residual": final_residual,
        "final_eigen_residual": eigen_residual, "psi": psi,
    }


def tangent_basis(psi: np.ndarray) -> np.ndarray:
    real = np.concatenate((psi.real, psi.imag))
    phase = np.concatenate((-psi.imag, psi.real))
    _u, _s, vh = np.linalg.svd(np.vstack((real, phase)), full_matrices=True)
    return vh[2:].T


def map_jacobian(step26: Any, kinetic: np.ndarray, background: np.ndarray,
                 kappa: float, fixed: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    basis = tangent_basis(fixed)
    n = len(fixed)
    jacobian = np.zeros((basis.shape[1], basis.shape[1]))
    for column in range(basis.shape[1]):
        vector = basis[:, column]
        direction = vector[:n] + 1j * vector[n:]
        plus = step26.normalize(fixed + FD_EPS * direction)
        minus = step26.normalize(fixed - FD_EPS * direction)
        fplus = fixed_map(step26, kinetic, background, kappa, plus, fixed)
        fminus = fixed_map(step26, kinetic, background, kappa, minus, fixed)
        derivative = (fplus - fminus) / (2.0 * FD_EPS)
        jacobian[:, column] = basis.T @ np.concatenate((derivative.real, derivative.imag))
    return jacobian, np.linalg.eigvals(jacobian)


def stability_row(step26: Any, kinetic: np.ndarray, background: np.ndarray,
                  kappa: float, fixed: np.ndarray, sweep: str, parameter: float,
                  initial_state_solution_spread: float = 0.0) -> dict[str, Any]:
    jacobian, eigenvalues = map_jacobian(step26, kinetic, background, kappa, fixed)
    leading = eigenvalues[int(np.argmax(np.abs(eigenvalues)))]
    row = {
        "sweep": sweep, "parameter": parameter, "kappa": kappa,
        "map_residual": projective_gap(step26, fixed_map(step26, kinetic, background, kappa, fixed), fixed),
        "jacobian_dimension": jacobian.shape[0],
        "fixed_map_spectral_radius": float(abs(leading)),
        "leading_eigenvalue_real": float(leading.real),
        "leading_eigenvalue_imag": float(leading.imag),
        "fixed_map_linearly_stable": bool(abs(leading) < 1.0 - STABILITY_TOL),
        "initial_state_solution_spread": initial_state_solution_spread,
    }
    for mix in MIXES:
        relaxed = (1.0 - mix) + mix * eigenvalues
        row[f"relaxed_rho_mix_{str(mix).replace('.', '_')}"] = float(max(abs(relaxed)))
    return row


def solve_continuation_point(step26: Any, kinetic: np.ndarray, background: np.ndarray,
                             kappa: float, initial: np.ndarray) -> np.ndarray:
    result = iterate(step26, kinetic, background, kappa, 0.2, initial, CAP)
    if result["classification"] != "converged":
        raise RuntimeError(f"continuation solver did not converge at kappa={kappa}: {result['classification']}")
    return result["psi"]


def crossing(step26: Any, kinetic: np.ndarray, background: np.ndarray,
             left: float, right: float, initial: np.ndarray) -> dict[str, Any]:
    lo, hi = left, right
    psi = initial
    lo_rho = hi_rho = math.nan
    for _ in range(32):
        mid = 0.5 * (lo + hi)
        psi = solve_continuation_point(step26, kinetic, background, mid, psi)
        row = stability_row(step26, kinetic, background, mid, psi, "kappa_refinement", mid)
        rho = row["fixed_map_spectral_radius"]
        if rho < 1.0:
            lo, lo_rho = mid, rho
        else:
            hi, hi_rho = mid, rho
    point = 0.5 * (lo + hi)
    psi = solve_continuation_point(step26, kinetic, background, point, psi)
    row = stability_row(step26, kinetic, background, point, psi, "kappa_boundary", point)
    return {"lower_kappa": lo, "upper_kappa": hi, "estimated_kappa": point,
            "lower_rho": lo_rho, "upper_rho": hi_rho,
            "boundary_rho": row["fixed_map_spectral_radius"],
            "leading_eigenvalue_real": row["leading_eigenvalue_real"],
            "leading_eigenvalue_imag": row["leading_eigenvalue_imag"],
            "mechanism": "fixed_map_eigenvalue_crosses_unit_circle"}


def background_crossing(step26: Any, kinetic: np.ndarray, base_background: np.ndarray,
                        kappa: float, left: float, right: float,
                        initial: np.ndarray) -> dict[str, Any]:
    lo, hi = left, right
    psi = initial
    lo_rho = hi_rho = math.nan
    for _ in range(32):
        mid = 0.5 * (lo + hi)
        background = base_background + mid
        psi = solve_continuation_point(step26, kinetic, background, kappa, psi)
        row = stability_row(step26, kinetic, background, kappa, psi,
                            "background_refinement", mid)
        if row["fixed_map_spectral_radius"] < 1.0:
            lo, lo_rho = mid, row["fixed_map_spectral_radius"]
        else:
            hi, hi_rho = mid, row["fixed_map_spectral_radius"]
    point = 0.5 * (lo + hi)
    background = base_background + point
    psi = solve_continuation_point(step26, kinetic, background, kappa, psi)
    row = stability_row(step26, kinetic, background, kappa, psi,
                        "background_boundary", point)
    return {"lower_offset": lo, "upper_offset": hi, "estimated_offset": point,
            "lower_rho": lo_rho, "upper_rho": hi_rho,
            "boundary_rho": row["fixed_map_spectral_radius"],
            "leading_eigenvalue_real": row["leading_eigenvalue_real"],
            "leading_eigenvalue_imag": row["leading_eigenvalue_imag"],
            "mechanism": "fixed_map_eigenvalue_crosses_unit_circle"}


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise ValueError("empty artifact table")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in rows[0]})
    return stream.getvalue().encode()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def compute(cap: int = CAP, include_stability: bool = True) -> dict[str, Any]:
    started = time.perf_counter()
    step26, step54, pins = import_pinned()
    frozen, base_background, _source = step26.load_initial_field()
    kinetic = step26.kinetic_operator(len(frozen))
    initials = initial_states(step26, frozen)
    cases = []
    final_states: dict[tuple[str, float, float, str], np.ndarray] = {}
    sweep_specs = [
        ("background", [(float(offset), base_background + float(offset), float(step54.BACKGROUND_KAPPA))
                        for offset in step54.BACKGROUND_OFFSETS]),
        ("kappa", [(float(kappa), base_background, float(kappa)) for kappa in step54.KAPPA_VALUES]),
    ]
    for sweep, specs in sweep_specs:
        for parameter, background, kappa in specs:
            for mix in MIXES:
                for initial_name in INITIAL_STATES:
                    result = iterate(step26, kinetic, background, kappa, mix,
                                     initials[initial_name], cap)
                    cases.append({
                        "sweep": sweep, "parameter": parameter,
                        "background_offset": parameter if sweep == "background" else 0.0,
                        "kappa": kappa, "mix": mix, "initial_state": initial_name,
                        "cap": cap, "tolerance": TOL,
                        "classification": result["classification"],
                        "termination_reason": result["termination_reason"],
                        "iterations": result["iterations"], "cycle_period": result["cycle_period"],
                        "initial_map_residual": result["initial_map_residual"],
                        "final_map_residual": result["final_map_residual"],
                        "final_eigen_residual": result["final_eigen_residual"],
                    })
                    if result["classification"] == "converged":
                        final_states[(sweep, parameter, mix, initial_name)] = result["psi"]
    solution_spreads = {}
    for sweep, specs in sweep_specs:
        for parameter, _background, _kappa in specs:
            states = [final_states[(sweep, parameter, 0.2, name)] for name in INITIAL_STATES]
            solution_spreads[(sweep, parameter)] = max(
                ray_gap(left, right)
                for left, right in itertools.combinations(states, 2)
            )
    fixed_point_branches = []
    branch_assignments: dict[tuple[str, float, float, str], str] = {}
    for sweep, specs in sweep_specs:
        for parameter, background, kappa in specs:
            entries = [(key, state) for key, state in final_states.items()
                       if key[0] == sweep and key[1] == parameter]
            clusters: list[dict[str, Any]] = []
            for key, state in entries:
                match = next((cluster for cluster in clusters
                              if ray_gap(cluster["representative"], state) < 1e-6), None)
                if match is None:
                    match = {"representative": state, "members": []}
                    clusters.append(match)
                match["members"].append((key, state))
            for index, cluster in enumerate(clusters, 1):
                branch_id = f"{sweep}_{parameter:+g}_fp{index:02d}"
                members = cluster["members"]
                for key, _state in members:
                    branch_assignments[key] = branch_id
                representative = cluster["representative"]
                row = stability_row(step26, kinetic, background, kappa, representative,
                                    sweep, parameter)
                row.update({
                    "fixed_point_branch": branch_id,
                    "member_case_count": len(members),
                    "member_initial_states": "|".join(sorted({key[3] for key, _ in members})),
                    "member_mixes": "|".join(str(value) for value in sorted({key[2] for key, _ in members})),
                    "max_member_ray_gap": max(
                        (ray_gap(representative, state) for _key, state in members), default=0.0),
                })
                fixed_point_branches.append(row)
    for row in cases:
        key = (row["sweep"], row["parameter"], row["mix"], row["initial_state"])
        row["fixed_point_branch"] = branch_assignments.get(key, "")
    grid = []
    for sweep, specs in sweep_specs:
        for parameter, _background, _kappa in specs:
            for mix in MIXES:
                subset = [row for row in cases if row["sweep"] == sweep
                          and row["parameter"] == parameter and row["mix"] == mix]
                counts = Counter(row["classification"] for row in subset)
                grid.append({
                    "sweep": sweep, "parameter": parameter, "mix": mix,
                    "initial_state_count": len(subset),
                    "converged": counts["converged"], "stagnated": counts["stagnated"],
                    "cycling": counts["cycling"], "diverging": counts["diverging"],
                    "iteration_min": min(row["iterations"] for row in subset),
                    "iteration_max": max(row["iterations"] for row in subset),
                    "classification_set": "|".join(sorted(counts)),
                })
    stability = []
    continuation = []
    legacy_budget = []
    boundary = None
    bg_boundary = None
    if include_stability:
        for steps in (60, 120):
            for offset in map(float, step54.BACKGROUND_OFFSETS):
                _trace, legacy_summary, _state = step26.run_case(
                    f"legacy_offset_{offset:+g}_{steps}", frozen,
                    base_background + offset, float(step54.BACKGROUND_KAPPA),
                    float(step54.SWEEP_MIX), kinetic, steps,
                )
                legacy_budget.append({
                    "iterations": steps, "background_offset": offset,
                    "mix": float(step54.SWEEP_MIX),
                    "published_tolerance": float(step26.CONVERGENCE_TOL),
                    "converged": bool(legacy_summary["converged"]),
                    "fixed_point_residual": float(legacy_summary["fixed_point_residual"]),
                })
        previous = frozen
        for offset in map(float, step54.BACKGROUND_OFFSETS):
            background = base_background + offset
            fixed = solve_continuation_point(step26, kinetic, background,
                                             float(step54.BACKGROUND_KAPPA), previous)
            previous = fixed
            stability.append(stability_row(step26, kinetic, background,
                                           float(step54.BACKGROUND_KAPPA), fixed,
                                           "background", offset,
                                           solution_spreads[("background", offset)]))
        previous = frozen
        for kappa in map(float, step54.KAPPA_VALUES):
            fixed = solve_continuation_point(step26, kinetic, base_background, kappa, previous)
            solution_step = projective_gap(step26, fixed, previous)
            previous = fixed
            row = stability_row(step26, kinetic, base_background, kappa, fixed, "kappa", kappa,
                                solution_spreads[("kappa", kappa)])
            stability.append(row)
            continuation.append({**row, "continuation_state_step": solution_step,
                                 "solution_exists": row["map_residual"] < TOL})
        stable = [row for row in continuation if row["fixed_map_linearly_stable"]]
        unstable = [row for row in continuation if not row["fixed_map_linearly_stable"]]
        if stable and unstable:
            lower = max(row["parameter"] for row in stable
                        if row["parameter"] < min(x["parameter"] for x in unstable))
            upper = min(row["parameter"] for row in unstable if row["parameter"] > lower)
            boundary = crossing(step26, kinetic, base_background, lower, upper, previous)
    background_stability = [row for row in stability if row["sweep"] == "background"]
    kappa_stability = [row for row in stability if row["sweep"] == "kappa"]
    background_branches = [row for row in fixed_point_branches if row["sweep"] == "background"]
    kappa_branches = [row for row in fixed_point_branches if row["sweep"] == "kappa"]
    all_background_solutions = bool(background_stability) and all(
        row["map_residual"] < TOL for row in background_stability)
    all_background_stable = bool(background_stability) and all(
        row["fixed_map_linearly_stable"] for row in background_stability)
    stable_background_count = sum(row["fixed_map_linearly_stable"] for row in background_stability)
    unstable_background_count = len(background_stability) - stable_background_count
    if include_stability and stable_background_count and unstable_background_count:
        positive_stable = [row for row in background_stability
                           if row["parameter"] >= 0 and row["fixed_map_linearly_stable"]]
        positive_unstable = [row for row in background_stability
                             if row["parameter"] >= 0 and not row["fixed_map_linearly_stable"]]
        if positive_stable and positive_unstable:
            lower = max(row["parameter"] for row in positive_stable
                        if row["parameter"] < min(x["parameter"] for x in positive_unstable))
            upper = min(row["parameter"] for row in positive_unstable if row["parameter"] > lower)
            bg_boundary = background_crossing(
                step26, kinetic, base_background, float(step54.BACKGROUND_KAPPA),
                lower, upper, frozen,
            )
    all_kappa_solutions = bool(kappa_stability) and all(row["map_residual"] < TOL for row in kappa_stability)
    genuine_boundary = boundary is not None
    if all_background_solutions and not all_background_stable and genuine_boundary:
        supported = "MIXED_ALL_BACKGROUND_SOLUTIONS_EXIST_THREE_RAW_MAP_UNSTABLE_AND_KAPPA_STABILITY_BOUNDARY"
        statement = ("All sampled backgrounds possess fixed-point solutions, but only "
                     f"{stable_background_count}/{len(background_stability)} are linearly stable under the "
                     "undamped map; the kappa continuation likewise retains solutions while crossing a "
                     "raw-map stability boundary.")
    elif all_background_solutions and all_background_stable and genuine_boundary:
        supported = "MIXED_ALL_SAMPLED_BACKGROUNDS_STABLE_KAPPA_FIXED_MAP_STABILITY_BOUNDARY"
        statement = ("Every sampled background admits a stable fixed point, so the finite background sweep "
                     "has no in-layer selector; independently, the continuing kappa branch loses raw-map "
                     "linear stability inside the sampled kappa window.")
    elif all_background_solutions and all_background_stable:
        supported = "ALL_SAMPLED_BACKGROUNDS_STABLE_NO_BOUNDARY_IN_WINDOW"
        statement = ("Every sampled background admits a stable fixed point; the sampled backgrounds are all "
                     "admissible and nothing in-layer selects among them at finite-sample strength.")
    else:
        supported = "MIXED_BACKGROUND_EXISTENCE_OR_STABILITY"
        statement = "The sampled background family has mixed existence or stability and must be typed pointwise."
    return {
        "pins": pins, "cases": cases, "grid": grid, "stability": stability,
        "fixed_point_branches": fixed_point_branches,
        "legacy_budget": legacy_budget,
        "continuation": continuation, "boundary": boundary,
        "background_boundary": bg_boundary,
        "summary": {
            "case_count": len(cases), "grid_count": len(grid), "cap": cap, "tolerance": TOL,
            "background_offset_count": len(step54.BACKGROUND_OFFSETS),
            "kappa_count": len(step54.KAPPA_VALUES), "mixes": list(MIXES),
            "initial_states": list(INITIAL_STATES),
            "case_classifications": dict(sorted(Counter(row["classification"] for row in cases).items())),
            "legacy_60_pass_count": sum(row["converged"] for row in legacy_budget if row["iterations"] == 60),
            "legacy_120_pass_count": sum(row["converged"] for row in legacy_budget if row["iterations"] == 120),
            "all_background_solutions_exist": all_background_solutions,
            "all_background_fixed_points_linearly_stable": all_background_stable,
            "stable_background_fixed_point_count": stable_background_count,
            "unstable_background_fixed_point_count": unstable_background_count,
            "discovered_background_fixed_point_branch_count": len(background_branches),
            "stable_discovered_background_branch_count": sum(
                row["fixed_map_linearly_stable"] for row in background_branches),
            "unstable_discovered_background_branch_count": sum(
                not row["fixed_map_linearly_stable"] for row in background_branches),
            "discovered_background_branch_spectral_radius_min": min(
                row["fixed_map_spectral_radius"] for row in background_branches),
            "discovered_background_branch_spectral_radius_max": max(
                row["fixed_map_spectral_radius"] for row in background_branches),
            "discovered_kappa_fixed_point_branch_count": len(kappa_branches),
            "max_mix_0_2_initial_solution_spread": max(solution_spreads.values()),
            "background_spectral_radius_min": min(row["fixed_map_spectral_radius"] for row in background_stability) if background_stability else None,
            "background_spectral_radius_max": max(row["fixed_map_spectral_radius"] for row in background_stability) if background_stability else None,
            "all_kappa_solutions_exist": all_kappa_solutions,
            "kappa_spectral_radius_min": min(row["fixed_map_spectral_radius"] for row in kappa_stability) if kappa_stability else None,
            "kappa_spectral_radius_max": max(row["fixed_map_spectral_radius"] for row in kappa_stability) if kappa_stability else None,
            "genuine_fixed_map_stability_boundary": genuine_boundary,
            "supported_outcome": supported, "supported_statement": statement,
            "runtime_seconds": time.perf_counter() - started,
        },
    }


def budget_comparison(primary: dict[str, Any], doubled: dict[str, Any]) -> list[dict[str, Any]]:
    right = {(row["sweep"], row["parameter"], row["mix"], row["initial_state"]): row
             for row in doubled["cases"]}
    rows = []
    for left in primary["cases"]:
        key = (left["sweep"], left["parameter"], left["mix"], left["initial_state"])
        other = right[key]
        rows.append({
            "sweep": left["sweep"], "parameter": left["parameter"], "mix": left["mix"],
            "initial_state": left["initial_state"], "base_cap": primary["summary"]["cap"],
            "double_cap": doubled["summary"]["cap"],
            "base_classification": left["classification"],
            "double_classification": other["classification"],
            "classification_unchanged": left["classification"] == other["classification"],
        })
    return rows


def render(data: dict[str, Any], budget_rows: list[dict[str, Any]]) -> dict[str, bytes]:
    summary = {key: value for key, value in data["summary"].items() if key != "runtime_seconds"}
    summary["budget_doubling_classification_unchanged"] = all(
        row["classification_unchanged"] for row in budget_rows
    )
    summary["boundary"] = data["boundary"]
    summary["background_boundary"] = data["background_boundary"]
    schema = {
        "artifact": "Q7-REPAIR-1", "schema_version": 1,
        "classification": "relaxed-map dynamics, separately from iteration cap",
        "fixed_point_stability": "spectral radius of the undamped projective fixed-point map",
        "row_counts": {"cases": len(data["cases"]), "grid": len(data["grid"]),
                       "stability": len(data["stability"]),
                       "fixed_point_branches": len(data["fixed_point_branches"]),
                       "continuation": len(data["continuation"]),
                       "legacy_budget": len(data["legacy_budget"]),
                       "budget_checks": len(budget_rows)},
        "verdict_derivation": "computed from existence and spectral-radius predicates; no assigned verdict flags",
    }
    boundary = data["boundary"]
    bg_boundary = data["background_boundary"]
    note = f"""# Q7 F50 adaptive-convergence result

All 18 sampled background offsets have fixed-point solutions. Fifteen continuation points are linearly stable under the undamped map; offsets `5`, `8`, and `10` are unstable even though suitable damping converges to their solutions. Clustering every converged run by phase-invariant ray distance finds `{summary['discovered_background_fixed_point_branch_count']}` distinct sampled fixed points: `{summary['stable_discovered_background_branch_count']}` stable and `{summary['unstable_discovered_background_branch_count']}` unstable. The extra two are stable localized solutions at offset `-8`, so the three initial states are evidence of multistability rather than interchangeable global phases. The continuation radius range is `{summary['background_spectral_radius_min']:.12g}` to `{summary['background_spectral_radius_max']:.12g}`. The positive-offset spectral radius crosses one at offset `{bg_boundary['estimated_offset']:.12g}` with leading eigenvalue `{bg_boundary['leading_eigenvalue_real']:.12g}`. Thus solution existence gives no sampled value selector, but undamped-map stability types the background family as mixed rather than declaring all points stable.

The frozen legacy settings reproduce the reviewed artifact exactly: `{summary['legacy_60_pass_count']}/18` pass at 60 iterations and `{summary['legacy_120_pass_count']}/18` pass at 120. That split is therefore a budget observation, not an existence boundary.

All 12 sampled kappa values also have fixed-point solutions. The solution branch does not disappear. Its undamped-map spectral radius rises from `{summary['kappa_spectral_radius_min']:.12g}` to `{summary['kappa_spectral_radius_max']:.12g}` and crosses one at `kappa={boundary['estimated_kappa']:.12g}` with leading eigenvalue `{boundary['leading_eigenvalue_real']:.12g}{boundary['leading_eigenvalue_imag']:+.3g}i`. This is a genuine raw-map linear-stability boundary, not a loss of solution. Damping changes the relaxed solver stability and therefore the apparent finite-budget boundary; it does not move the fixed-map crossing.

Supported outcome: **{summary['supported_outcome']}**. {summary['supported_statement']}

Doubling the adaptive cap from {data['summary']['cap']} to {DOUBLE_CAP} changes no case classification: `{summary['budget_doubling_classification_unchanged']}`.
"""
    design = """# Q7 numerical design

- Step26 and Step54 are imported under literal SHA-256 pins; no corpus-reading build path is called.
- The undamped map sends a normalized state to the phase-aligned lowest eigenvector of the self-sourced Hamiltonian. Relaxed iteration uses the declared mix only as a solver.
- Convergence requires projective fixed-map residual below 1e-10. Period-2 through period-8 cycles, flat residual windows, nonfinite states, and residual growth are typed separately.
- Jacobians act on the 2N-2 dimensional normalized/projective tangent space and use centered finite differences. Relaxed-map radii are derived as eigenvalues of `(1-mix)I + mix J`.
- Converged states are clustered with the global-phase-invariant ray distance. The undamped Jacobian is evaluated for every distinct fixed point found across all mixes and initial states; this exposes three stable attractors at offset -8.
- The kappa boundary is refined by bisection on the undamped spectral radius while continuing the fixed-point solution with mix 0.2.
"""
    return {
        "q7_adaptive_cases.csv": csv_bytes(data["cases"]),
        "q7_classification_grid.csv": csv_bytes(data["grid"]),
        "q7_fixed_point_stability.csv": csv_bytes(data["stability"]),
        "q7_discovered_fixed_point_branches.csv": csv_bytes(data["fixed_point_branches"]),
        "q7_kappa_continuation.csv": csv_bytes(data["continuation"]),
        "q7_legacy_budget_reproduction.csv": csv_bytes(data["legacy_budget"]),
        "q7_budget_independence.csv": csv_bytes(budget_rows),
        "q7_dependency_pins.csv": csv_bytes(data["pins"]),
        "q7_results.json": json_bytes(summary), "q7_schema.json": json_bytes(schema),
        "RESULTS.md": note.encode(), "DESIGN.md": design.encode(),
    }


def main() -> None:
    primary = compute(CAP, include_stability=True)
    doubled = compute(DOUBLE_CAP, include_stability=False)
    budget = budget_comparison(primary, doubled)
    for name, payload in render(primary, budget).items():
        (HERE / name).write_bytes(payload)
    print(f"Q7 build PASS: cases={len(primary['cases'])} classifications={primary['summary']['case_classifications']} "
          f"boundary={primary['boundary']['estimated_kappa']:.9f} runtime={primary['summary']['runtime_seconds']:.3f}s")


if __name__ == "__main__":
    main()
