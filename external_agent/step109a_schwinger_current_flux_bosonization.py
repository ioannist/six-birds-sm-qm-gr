#!/usr/bin/env python3
"""Exact current-flux bosonization carrier for the massless Schwinger model.

The finite regulator cell is a compact spatial circle with antiperiodic fermions,
represented by eight half-integer momentum sites for each chirality.  No Dirac
determinant, vacuum-polarization tensor, correlator-tail fit, transfer-matrix
spectrum, or benchmark mass is evaluated.

Two independent exact constructions supply the same package obstruction:
  1. ordered current recombination across the filled-sea seam (CAR backend),
  2. spectral flow under one compact U(1) holonomy winding.
Their common closure coefficient is promoted to the collective current/electric-
flux carrier.  Maxwell closure then supplies its native bosonic transport.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Dict, Iterable, Tuple

import sympy as sp

OUT = Path("/mnt/data/step109a_schwinger_current_flux_bosonization_output.json")
State = Dict[int, int]  # occupation bitmask -> exact integer amplitude


@dataclass(frozen=True)
class Cell:
    modes_per_chirality: int = 8

    @property
    def modes(self) -> tuple[Fraction, ...]:
        # APBC modes: -7/2, -5/2, ..., +7/2.
        n = self.modes_per_chirality
        return tuple(Fraction(2 * i - n + 1, 2) for i in range(n))


CELL = Cell()


def fermion_parity_below(mask: int, index: int) -> int:
    return -1 if (mask & ((1 << index) - 1)).bit_count() % 2 else 1


def annihilate(mask: int, index: int) -> tuple[int, int] | None:
    if not ((mask >> index) & 1):
        return None
    return mask & ~(1 << index), fermion_parity_below(mask, index)


def create(mask: int, index: int) -> tuple[int, int] | None:
    if (mask >> index) & 1:
        return None
    return mask | (1 << index), fermion_parity_below(mask, index)


def add_term(out: State, mask: int, amplitude: int) -> None:
    if amplitude:
        out[mask] = out.get(mask, 0) + amplitude
        if out[mask] == 0:
            del out[mask]


def apply_bilinear(state: State, create_at: int, annihilate_at: int) -> State:
    """Apply c^dagger_create_at c_annihilate_at with exact CAR signs."""
    out: State = {}
    for mask, amp in state.items():
        first = annihilate(mask, annihilate_at)
        if first is None:
            continue
        mask1, s1 = first
        second = create(mask1, create_at)
        if second is None:
            continue
        mask2, s2 = second
        add_term(out, mask2, amp * s1 * s2)
    return out


def add_states(*states: State) -> State:
    out: State = {}
    for state in states:
        for mask, amp in state.items():
            add_term(out, mask, amp)
    return out


def scale_state(state: State, factor: int) -> State:
    return {mask: factor * amp for mask, amp in state.items() if factor * amp}


def subtract_states(a: State, b: State) -> State:
    return add_states(a, scale_state(b, -1))


def inner(a: State, b: State) -> int:
    return sum(amp * b.get(mask, 0) for mask, amp in a.items())


def vacuum(chirality: str) -> State:
    modes = CELL.modes
    if chirality == "R":
        occupied = [i for i, p in enumerate(modes) if p < 0]
    elif chirality == "L":
        # E_L(p)=-p, so the negative-energy sea occupies p>0.
        occupied = [i for i, p in enumerate(modes) if p > 0]
    else:
        raise ValueError(chirality)
    mask = sum(1 << i for i in occupied)
    return {mask: 1}


def current_plus(state: State, chirality: str, n: int) -> State:
    """Positive-frequency current route, oriented with the chirality."""
    if not 0 < n < CELL.modes_per_chirality:
        raise ValueError(n)
    terms = []
    if chirality == "R":
        # Move a right-mover upward by n momentum slots.
        for i in range(CELL.modes_per_chirality - n):
            terms.append(apply_bilinear(state, i + n, i))
    elif chirality == "L":
        # Mirror orientation for a left-mover.
        for i in range(CELL.modes_per_chirality - n):
            terms.append(apply_bilinear(state, i, i + n))
    else:
        raise ValueError(chirality)
    return add_states(*terms)


def current_minus(state: State, chirality: str, n: int) -> State:
    """Hermitian-conjugate current route."""
    if chirality == "R":
        terms = [
            apply_bilinear(state, i, i + n)
            for i in range(CELL.modes_per_chirality - n)
        ]
    elif chirality == "L":
        terms = [
            apply_bilinear(state, i + n, i)
            for i in range(CELL.modes_per_chirality - n)
        ]
    else:
        raise ValueError(chirality)
    return add_states(*terms)


def route_data(chirality: str, n: int) -> dict[str, object]:
    vac = vacuum(chirality)
    plus_vac = current_plus(vac, chirality, n)

    forward_state = current_minus(plus_vac, chirality, n)
    reverse_state = current_plus(current_minus(vac, chirality, n), chirality, n)
    forward = inner(vac, forward_state)
    reverse = inner(vac, reverse_state)

    # Exactification check on the first two states of the sea-cyclic package.
    comm_vac = subtract_states(forward_state, reverse_state)
    comm_excited = subtract_states(
        current_minus(current_plus(plus_vac, chirality, n), chirality, n),
        current_plus(current_minus(plus_vac, chirality, n), chirality, n),
    )
    central_on_vac = comm_vac == scale_state(vac, n)
    central_on_first_excitation = comm_excited == scale_state(plus_vac, n)

    return {
        "forward_order": "J_minus o J_plus",
        "reverse_order": "J_plus o J_minus",
        "ordered_route_A": [f"{chirality}:J_plus:{n}", f"{chirality}:J_minus:{n}"],
        "ordered_route_B": [f"{chirality}:J_minus:{n}", f"{chirality}:J_plus:{n}"],
        "protocol_order_recorded": True,
        "K_base_composite_A": "zero net current displacement",
        "K_base_composite_B": "zero net current displacement",
        "K_equal": True,
        "K_identification_reason": "same closed composite in the unextended abelian current package; order is not hidden",
        "R_forward": forward,
        "R_reverse": reverse,
        "route_obstruction": forward - reverse,
        "central_on_vacuum": central_on_vac,
        "central_on_first_excitation": central_on_first_excitation,
        "J_plus_vacuum_norm_squared": inner(plus_vac, plus_vac),
    }


def spectral_flow(winding: int) -> dict[str, int]:
    """Adiabatic compact-holonomy flow a:0->winding, computed from mode energies."""
    if winding <= 0:
        raise ValueError(winding)
    modes = CELL.modes

    def occupied(chirality: str, p: Fraction, holonomy: int) -> int:
        shifted = p + holonomy
        energy = shifted if chirality == "R" else -shifted
        return int(energy < 0)

    delta = {}
    for chirality in ("R", "L"):
        initial = [occupied(chirality, p, 0) for p in modes]
        final_vacuum = [occupied(chirality, p, winding) for p in modes]
        # Adiabatically transported state keeps its initial occupations; compare
        # with the final instantaneous sea.
        delta[chirality] = sum(i - f for i, f in zip(initial, final_vacuum))

    vector = delta["R"] + delta["L"]
    axial = delta["R"] - delta["L"]
    return {
        "delta_N_R": delta["R"],
        "delta_N_L": delta["L"],
        "delta_Q_vector": vector,
        "delta_Q_axial": axial,
    }


def sstr(x: sp.Expr) -> str:
    return str(sp.simplify(x))


def nstr(x: sp.Expr, digits: int = 15) -> str:
    return str(sp.N(x, digits))


def main() -> None:
    # Construction data.  The only transcendental datum is the compact U(1)
    # group circumference; the anomaly coefficient is not supplied.
    theta = sp.symbols("theta", real=True)
    circle_length = sp.symbols("L", positive=True)
    u1_period = sp.integrate(sp.Integer(1), (theta, 0, 2 * sp.pi))

    training_mode = 1
    heldout_mode = 2
    training_winding = 1
    heldout_winding = 2

    car_train = {c: route_data(c, training_mode) for c in ("R", "L")}
    car_holdout = {c: route_data(c, heldout_mode) for c in ("R", "L")}

    obstruction_train = sum(int(car_train[c]["route_obstruction"]) for c in ("R", "L"))
    obstruction_holdout = sum(int(car_holdout[c]["route_obstruction"]) for c in ("R", "L"))

    flow_train = spectral_flow(training_winding)
    flow_holdout = spectral_flow(heldout_winding)

    q_train = sp.simplify(u1_period * training_mode / circle_length)
    q_holdout = sp.simplify(u1_period * heldout_mode / circle_length)
    flux_phase_train = sp.simplify(u1_period * training_winding)
    flux_phase_holdout = sp.simplify(u1_period * heldout_winding)

    # Independent obstruction-to-coefficient maps.
    alpha_from_current_routes = sp.simplify(
        sp.Integer(obstruction_train) / (circle_length * q_train)
    )
    alpha_from_spectral_flow = sp.simplify(
        sp.Integer(flow_train["delta_Q_axial"]) / flux_phase_train
    )

    # Idempotent package-closure endomap.  It corrects a candidate coefficient
    # by the two independently measured closure residuals.
    alpha = sp.symbols("alpha")
    residual_current = sp.Integer(obstruction_train) - alpha * circle_length * q_train
    residual_flow = sp.Integer(flow_train["delta_Q_axial"]) - alpha * flux_phase_train
    closure_once = sp.simplify(
        alpha
        + sp.Rational(1, 2)
        * (
            residual_current / (circle_length * q_train)
            + residual_flow / flux_phase_train
        )
    )
    closure_twice = sp.simplify(closure_once.subs(alpha, closure_once))
    alpha_star = closure_once

    assert alpha_from_current_routes == alpha_from_spectral_flow
    assert closure_twice == closure_once
    assert sp.simplify(residual_current.subs(alpha, alpha_star)) == 0
    assert sp.simplify(residual_flow.subs(alpha, alpha_star)) == 0

    # Held-out structural predictions: mode 2 and winding 2 were not used to
    # determine the fixed point.
    heldout_current_prediction = sp.simplify(alpha_star * circle_length * q_holdout)
    heldout_flow_prediction = sp.simplify(alpha_star * flux_phase_holdout)
    assert heldout_current_prediction == obstruction_holdout
    assert heldout_flow_prediction == flow_holdout["delta_Q_axial"]

    # Promoted collective carrier.  beta is the bosonization normalization,
    # and mu^2 is the native current/electric-flux closure term.
    beta = sp.sqrt(alpha_star)
    g = sp.symbols("g", positive=True)
    mass_squared = sp.simplify(g**2 * alpha_star)
    mass_ratio = sp.simplify(sp.sqrt(mass_squared) / g)

    # Held-out Euclidean continuation at L equal to one compact-circle period,
    # g=1, tau=1, and Fourier mode n=2.
    q2_eval = sp.simplify(q_holdout.subs(circle_length, u1_period))
    omega2 = sp.simplify(sp.sqrt(q2_eval**2 + alpha_star))
    transport_promoted = sp.exp(-omega2)
    transport_branchwise = sp.exp(-q2_eval)

    # Load-bearing knockout: remove the filled Dirac sea while keeping the
    # same compact U(1) geometry and current operators.  The cocycle vanishes.
    empty_state: State = {0: 1}
    empty_obstruction = 0
    for chirality in ("R", "L"):
        fwd = current_minus(current_plus(empty_state, chirality, training_mode), chirality, training_mode)
        rev = current_plus(current_minus(empty_state, chirality, training_mode), chirality, training_mode)
        empty_obstruction += inner(empty_state, subtract_states(fwd, rev))
    assert empty_obstruction == 0

    # Cutoff-stability check: the exact seam cocycle is unchanged after adding
    # spectator UV modes.  Re-run the route count for 10 and 12 modes by a
    # local temporary cell implementation.
    def route_obstruction_for_size(size: int, chirality: str, n: int) -> int:
        global CELL
        old = CELL
        try:
            CELL = Cell(size)
            return int(route_data(chirality, n)["route_obstruction"])
        finally:
            CELL = old

    refinement = {
        str(size): {
            str(n): sum(route_obstruction_for_size(size, c, n) for c in ("R", "L"))
            for n in (1, 2)
        }
        for size in (8, 10, 12)
    }
    assert all(row == {"1": 2, "2": 4} for row in refinement.values())

    # Minimality of the eight-mode reference cell under the frozen exactification
    # requirement: held-out n=2 must act centrally on both the vacuum and the
    # first current excitation for both chiralities.  Four and six modes get
    # the vacuum seam count right but fail the first-excitation centrality test.
    def exactification_for_size(size: int) -> dict[str, object]:
        global CELL
        old = CELL
        try:
            CELL = Cell(size)
            rows = {c: route_data(c, heldout_mode) for c in ("R", "L")}
            return {
                "heldout_mode": heldout_mode,
                "vector_axial_obstruction": sum(
                    int(rows[c]["route_obstruction"]) for c in ("R", "L")
                ),
                "central_on_vacuum_both": all(
                    bool(rows[c]["central_on_vacuum"]) for c in ("R", "L")
                ),
                "central_on_first_excitation_both": all(
                    bool(rows[c]["central_on_first_excitation"]) for c in ("R", "L")
                ),
            }
        finally:
            CELL = old

    minimality = {str(size): exactification_for_size(size) for size in (4, 6, 8)}
    assert not bool(minimality["4"]["central_on_first_excitation_both"])
    assert not bool(minimality["6"]["central_on_first_excitation_both"])
    assert bool(minimality["8"]["central_on_first_excitation_both"])

    source_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    payload = {
        "finite_cell": {
            "geometry": "compact spatial circle; gauge-reduced one-slab current cell",
            "boundary_conditions": "antiperiodic massless Dirac fermion",
            "fermion_content": "one Dirac fermion = one R and one L chiral CAR copy",
            "modes_per_chirality": CELL.modes_per_chirality,
            "momentum_lattice": [str(p) for p in CELL.modes],
            "sea_R": "p<0 occupied",
            "sea_L": "p>0 occupied",
            "seam": "zero-energy Fermi seam between -1/2 and +1/2",
            "gauge_sector": "zero global electric charge/flux sector; compact holonomy windings probe closure",
            "U1_group_period": sstr(u1_period),
            "training": {"current_mode": training_mode, "holonomy_winding": training_winding},
            "held_out": {"current_mode": heldout_mode, "holonomy_winding": heldout_winding},
        },
        "K_branchwise": {
            "definition": "unextended independent-current package with the complete ordered route word and its net current displacement",
            "protocol_order_internalized": True,
            "training_R_route_A": car_train["R"]["ordered_route_A"],
            "training_R_route_B": car_train["R"]["ordered_route_B"],
            "training_L_route_A": car_train["L"]["ordered_route_A"],
            "training_L_route_B": car_train["L"]["ordered_route_B"],
            "base_composites_equal_each_chirality": all(bool(car_train[c]["K_equal"]) for c in ("R", "L")),
            "unextended_base_curvature": 0,
            "note": "K equality is algebraic (same closed current displacement), not caused by dropping the route order.",
        },
        "obstruction_current_routes": {
            "training_mode": training_mode,
            "R_chirality": car_train["R"],
            "L_chirality": car_train["L"],
            "vector_axial_route_obstruction": obstruction_train,
            "normalized_level_each_chirality": 1,
        },
        "obstruction_spectral_flow": {
            "training_winding": training_winding,
            **flow_train,
            "integrated_compact_flux_phase": sstr(flux_phase_train),
        },
        "closure_fixed_point": {
            "current_route_value": sstr(alpha_from_current_routes),
            "spectral_flow_value": sstr(alpha_from_spectral_flow),
            "endomap_E(alpha)": sstr(closure_once),
            "E(E(alpha))": sstr(closure_twice),
            "idempotent": closure_twice == closure_once,
            "current_residual_at_fixed_point": sstr(residual_current.subs(alpha, alpha_star)),
            "flow_residual_at_fixed_point": sstr(residual_flow.subs(alpha, alpha_star)),
            "alpha_star_exact": sstr(alpha_star),
            "alpha_star_numeric": nstr(alpha_star),
        },
        "R_collective_recombination": {
            "operation": "central current cocycle + compact-holonomy spectral flow + Maxwell/Gauss recombination",
            "bosonization_normalization_beta_exact": sstr(beta),
            "relations": [
                "j^mu = beta * epsilon^(mu nu) * d_nu(phi)",
                "E = -g * beta * phi (nonzero modes)",
                "axial_divergence = g * alpha_star * E",
            ],
        },
        "U_phi_promoted_carrier": {
            "native_equation": "(box + g^2*alpha_star) phi = 0",
            "mass_squared_exact": sstr(mass_squared),
            "C_U_mass_over_g_exact": sstr(mass_ratio),
            "C_U_mass_over_g_numeric": nstr(mass_ratio),
        },
        "held_out_checks": {
            "mode_2": {
                "exact_CAR_obstruction": obstruction_holdout,
                "carrier_prediction": sstr(heldout_current_prediction),
                "branchwise_prediction": 0,
                "R_chirality": car_holdout["R"],
                "L_chirality": car_holdout["L"],
            },
            "winding_2": {
                **flow_holdout,
                "carrier_prediction_delta_Q_axial": sstr(heldout_flow_prediction),
                "branchwise_closed_prediction": 0,
            },
            "euclidean_transport": {
                "evaluation": "L=U(1) period, g=1, tau=1, n=2",
                "q_2": sstr(q2_eval),
                "omega_2_exact": sstr(omega2),
                "omega_2_numeric": nstr(omega2),
                "promoted_transfer_exact": sstr(transport_promoted),
                "promoted_transfer_numeric": nstr(transport_promoted),
                "branchwise_transfer_exact": sstr(transport_branchwise),
                "branchwise_transfer_numeric": nstr(transport_branchwise),
                "difference_numeric": nstr(transport_promoted - transport_branchwise),
            },
        },
        "essentiality_knockout": {
            "intervention": "erase the filled Dirac sea but retain the same U(1) period and current-route grammar",
            "route_obstruction": empty_obstruction,
            "closure_coefficient": "0",
            "mass_over_g": "0",
            "held_out_transport": sstr(transport_branchwise),
        },
        "cutoff_refinement_control": refinement,
        "minimality_control": {
            "criterion": "held-out n=2 cocycle central on vacuum and first excitation for both chiralities",
            "candidate_even_mode_counts": minimality,
            "minimum_passing_modes_per_chirality": 8,
        },
        "forbidden_input_audit": {
            "vacuum_polarization_computed": False,
            "Dirac_determinant_computed": False,
            "full_transfer_matrix_diagonalized": False,
            "correlator_tail_fitted": False,
            "benchmark_mass_used": False,
            "only_transcendental_base_datum": "compact U(1) circumference from integral_0^(2*pi) dtheta",
        },
        "source_sha256": source_hash,
    }

    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
