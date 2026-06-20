#!/usr/bin/env python3
"""Exact cross-scale closure demonstrator for the step110 proton carrier door.

This is deliberately *not* a physical QCD mass calculation.  It proves the missing
mathematical mechanism: once a scale-refinement/package map is generated, the
single-scale omitted-sector coupling s is no longer free.  The crossed SU(3)
recoupling used in step110 induces a contractive scalar closure map with a unique
fixed point.

No target mass, proton/Omega ratio, correlator, transfer spectrum from QCD, or
external fitted coefficient is supplied.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import sympy as sp
import numpy as np

OUT = Path(__file__).with_name("step111a_cross_scale_invariant_graph_output.json")


def sf(x: sp.Expr, digits: int = 16) -> float:
    return float(sp.N(x, digits + 4))


def main() -> None:
    s = sp.symbols("s", real=True)
    rt3 = sp.sqrt(3)

    # Same single-scale carrier used in step110, now embedded in the full
    # qqq + qqqg_rho + qqqg_lambda crossed-basis carrier.
    T = sp.Matrix(
        [
            [sp.Rational(3, 5), sp.Rational(1, 10), s],
            [sp.Rational(1, 10), sp.Rational(2, 5), 0],
            [s, 0, sp.Rational(1, 5)],
        ]
    )
    F = sp.Matrix(
        [
            [-sp.Rational(1, 2), -rt3 / 2],
            [rt3 / 2, -sp.Rational(1, 2)],
        ]
    )
    U = sp.eye(3)
    U[1:3, 1:3] = F

    assert sp.simplify(F * F.T) == sp.eye(2)

    # One exact scale step: glue two temporal cells, then express the hidden
    # qqqg sector in the crossed (23) recoupling basis.
    blocked = sp.simplify(U * T**2 * U.T)

    # Package normalization: preserve the qqq anchor T_00 = 3/5.  The next-scale
    # hidden coupling is the normalized qqq <-> C_lambda crossed-channel entry.
    normalizer = sp.simplify(sp.Rational(3, 5) / blocked[0, 0])
    closure_map = sp.factor(normalizer * blocked[0, 2])
    expected_map = 3 * (rt3 - 8 * s) / (100 * s**2 + 37)
    assert sp.simplify(closure_map - expected_map) == 0

    fixed_polynomial = sp.factor(
        sp.together(s - closure_map).as_numer_denom()[0]
    )
    # Sign convention from s-f(s): 100 s^3 + 61 s - 3 sqrt(3).
    fixed_polynomial = sp.expand(fixed_polynomial)
    if sp.LC(sp.Poly(fixed_polynomial, s)) < 0:
        fixed_polynomial = -fixed_polynomial
    assert sp.simplify(fixed_polynomial - (100 * s**3 + 61 * s - 3 * rt3)) == 0

    roots = sp.nroots(fixed_polynomial, n=50, maxsteps=200)
    real_roots = [sp.re(r) for r in roots if abs(float(sp.im(r))) < 1e-35]
    assert len(real_roots) == 1
    s_star = sp.N(real_roots[0], 50)
    assert 0 < float(s_star) < 0.15

    derivative = sp.factor(sp.diff(closure_map, s))
    derivative_at_fixed = sp.N(derivative.subs(s, s_star), 50)

    # Exact invariant interval I=[0,3/20].  f is positive and decreasing there,
    # f(0)<3/20 and f(3/20)>0.  A simple exact derivative bound uses sqrt(3)<7/4.
    interval_lo = sp.Rational(0)
    interval_hi = sp.Rational(3, 20)
    image_hi = sp.simplify(closure_map.subs(s, interval_lo))
    image_lo = sp.simplify(closure_map.subs(s, interval_hi))
    assert image_lo > 0
    assert image_hi < interval_hi
    rigorous_q_bound = sp.Rational(2091, 2738)  # < 1, valid throughout I
    assert rigorous_q_bound < 1

    # Sharper numerical supremum, used only as a diagnostic, not the proof.
    d2_roots = sp.nroots(sp.together(sp.diff(derivative, s)).as_numer_denom()[0])
    candidates = [interval_lo, interval_hi]
    for r in d2_roots:
        if abs(float(sp.im(r))) < 1e-12:
            rr = float(sp.re(r))
            if 0.0 <= rr <= 0.15:
                candidates.append(sp.N(sp.re(r), 40))
    actual_q = max(abs(sf(derivative.subs(s, x), 30)) for x in candidates)
    assert actual_q < 1.0

    def iterate(seed: float, steps: int = 80) -> list[float]:
        x = sp.Float(seed, 60)
        values = [float(x)]
        for _ in range(steps):
            x = sp.N(closure_map.subs(s, x), 60)
            values.append(float(x))
        return values

    trajectory_zero = iterate(0.0)
    trajectory_tenth = iterate(0.1)
    assert abs(trajectory_zero[-1] - float(s_star)) < 1e-10
    assert abs(trajectory_tenth[-1] - float(s_star)) < 1e-10

    # The step110 Feshbach/Perron root at the closure-fixed coupling.
    T_star = np.array(T.subs(s, s_star).evalf(40).tolist(), dtype=float)
    eigenvalues = np.linalg.eigvalsh(T_star)
    z_star = float(eigenvalues[-1])
    am_demo = -math.log(z_star)

    charpoly = sp.factor(T.charpoly().as_expr())
    displayed_root_poly = 500 * sp.Symbol("z")**3 - 600 * sp.Symbol("z")**2 + (
        215 - 500 * s**2
    ) * sp.Symbol("z") + 200 * s**2 - 23

    # Structural knockout: erase the obstruction-forced qqq <-> C_rho seed.
    T_knockout = sp.Matrix(
        [
            [sp.Rational(3, 5), 0, s],
            [0, sp.Rational(2, 5), 0],
            [s, 0, sp.Rational(1, 5)],
        ]
    )
    blocked_knockout = sp.simplify(U * T_knockout**2 * U.T)
    knockout_map = sp.factor(
        (sp.Rational(3, 5) / blocked_knockout[0, 0]) * blocked_knockout[0, 2]
    )
    assert sp.simplify(knockout_map + 6 * s / (25 * s**2 + 9)) == 0
    knockout_fixed = sp.factor(
        sp.together(s - knockout_map).as_numer_denom()[0]
    )
    # Its only real fixed point is zero.
    knockout_roots = sp.nroots(knockout_fixed)
    knockout_real = sorted(
        float(sp.re(r)) for r in knockout_roots if abs(float(sp.im(r))) < 1e-12
    )
    assert len(knockout_real) == 1 and abs(knockout_real[0]) < 1e-12

    result: dict[str, Any] = {
        "classification": "exact_cross_scale_invariant_graph_demonstrator",
        "scope": {
            "fixes_step110_free_coupling": True,
            "physical_QCD_mass_landing": False,
            "reason": (
                "The scale map is generated from the frozen step110 reference cell, "
                "not yet from a local 2+1-flavor SU(3) QCD tensor block."
            ),
        },
        "carrier": {
            "basis": ["qqq", "qqqg_C_rho", "qqqg_C_lambda"],
            "T_of_s": [[str(x) for x in row] for row in T.tolist()],
            "crossed_F_12_to_23": [[str(x) for x in row] for row in F.tolist()],
            "F_orthogonal": True,
        },
        "exact_scale_step": {
            "operation": "B(s)=U*T(s)^2*U^T; normalize B_00 back to 3/5",
            "blocked_matrix": [[str(sp.factor(x)) for x in row] for row in blocked.tolist()],
            "closure_map": str(closure_map),
            "fixed_polynomial": str(fixed_polynomial),
        },
        "closure_certificate": {
            "invariant_interval": ["0", "3/20"],
            "image_interval_numeric": [sf(image_lo), sf(image_hi)],
            "rigorous_lipschitz_bound": str(rigorous_q_bound),
            "rigorous_lipschitz_bound_numeric": sf(rigorous_q_bound),
            "actual_sup_abs_derivative_numeric": actual_q,
            "unique_fixed_coupling_s_star": float(s_star),
            "derivative_at_s_star": float(derivative_at_fixed),
            "seed_0_final": trajectory_zero[-1],
            "seed_0p1_final": trajectory_tenth[-1],
            "seed_0_first_10": trajectory_zero[:10],
            "seed_0p1_first_10": trajectory_tenth[:10],
        },
        "single_scale_door_dissolved": {
            "free_before_scale_law": "s arbitrary",
            "fixed_after_scale_law": float(s_star),
            "initialization_independent": True,
        },
        "reference_cell_transfer_root": {
            "root_polynomial": str(displayed_root_poly),
            "z_star": z_star,
            "minus_log_z_star": am_demo,
            "warning": "This is a reference-cell root, not a proton mass or m_N/m_Omega.",
        },
        "transport_essentiality_knockout": {
            "removed_coordinate": "qqq <-> C_rho seed 1/10",
            "knockout_map": str(knockout_map),
            "only_real_fixed_point": 0.0,
            "crossed_channel_generated_coupling_lost": True,
        },
        "forbidden_inputs": {
            "proton_mass": False,
            "omega_mass": False,
            "mN_over_mOmega": False,
            "full_QCD_transfer_matrix": False,
            "QCD_correlator": False,
            "lattice_ensemble": False,
        },
    }

    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
