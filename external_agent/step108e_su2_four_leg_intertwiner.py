#!/usr/bin/env python3
"""Exact four-leg SU(2) multiple-intertwiner witness.

External legs: four copies of j=1/2.
B  = s-channel intermediate spin k=0.
B' = s-channel intermediate spin k=1, coupled to total J=0.
Readout/continuation: t-channel (legs 1 and 3) heat-kernel weights
w_0=1, w_1=1/3, corresponding to alpha=log(3)/2 in exp[-alpha*j(j+1)].

All reported reduced matrices and responses are exact rationals.
"""
from __future__ import annotations

import json
from pathlib import Path
import sympy as sp

OUT = Path('/mnt/data/step108e_su2_four_leg_intertwiner_output.json')
SQRT = sp.sqrt


def ket(bits: tuple[int, int, int, int]) -> sp.Matrix:
    v = sp.zeros(16, 1)
    v[int(''.join(map(str, bits)), 2)] = 1
    return v


# |0_s> = |S_12> |S_34>
B0 = (
    ket((0, 1, 0, 1))
    - ket((0, 1, 1, 0))
    - ket((1, 0, 0, 1))
    + ket((1, 0, 1, 0))
) / 2

# |1_s> = (|T+_12 T-_34> + |T-_12 T+_34> - |T0_12 T0_34>)/sqrt(3)
B1 = (
    ket((0, 0, 1, 1))
    + ket((1, 1, 0, 0))
    - (
        ket((0, 1, 0, 1))
        + ket((0, 1, 1, 0))
        + ket((1, 0, 0, 1))
        + ket((1, 0, 1, 0))
    ) / 2
) / SQRT(3)


def reduced_pair(v: sp.Matrix, keep: tuple[int, int]) -> sp.Matrix:
    """Partial trace of |v><v|, retaining two qubits in the given order."""
    rho = v * v.T
    traced = tuple(i for i in range(4) if i not in keep)
    out = sp.zeros(4, 4)
    for a in range(4):
        abits = [(a >> 1) & 1, a & 1]
        for b in range(4):
            bbits = [(b >> 1) & 1, b & 1]
            total = 0
            for t in range(4):
                tbits = [(t >> 1) & 1, t & 1]
                bra_bits = [0, 0, 0, 0]
                ket_bits = [0, 0, 0, 0]
                for pos, q in enumerate(keep):
                    bra_bits[q] = abits[pos]
                    ket_bits[q] = bbits[pos]
                for pos, q in enumerate(traced):
                    bra_bits[q] = tbits[pos]
                    ket_bits[q] = tbits[pos]
                i = int(''.join(map(str, bra_bits)), 2)
                j = int(''.join(map(str, ket_bits)), 2)
                total += rho[i, j]
            out[a, b] = sp.simplify(total)
    return out


def reduced_one(v: sp.Matrix, keep: int) -> sp.Matrix:
    rho = v * v.T
    out = sp.zeros(2, 2)
    others = tuple(i for i in range(4) if i != keep)
    for a in (0, 1):
        for b in (0, 1):
            total = 0
            for t in range(8):
                tbits = [(t >> 2) & 1, (t >> 1) & 1, t & 1]
                ibits = [0, 0, 0, 0]
                jbits = [0, 0, 0, 0]
                ibits[keep] = a
                jbits[keep] = b
                for pos, q in enumerate(others):
                    ibits[q] = tbits[pos]
                    jbits[q] = tbits[pos]
                i = int(''.join(map(str, ibits)), 2)
                j = int(''.join(map(str, jbits)), 2)
                total += rho[i, j]
            out[a, b] = sp.simplify(total)
    return out


rho13_B0 = reduced_pair(B0, (0, 2))
rho13_B1 = reduced_pair(B1, (0, 2))

singlet13 = sp.Matrix([0, 1, -1, 0]) / SQRT(2)
P0 = singlet13 * singlet13.T
P1 = sp.eye(4) - P0
rho_product = sp.eye(4) / 4
Gamma_B0 = sp.simplify(rho13_B0 - rho_product)
Gamma_B1 = sp.simplify(rho13_B1 - rho_product)

w0 = sp.Rational(1, 1)
w1 = sp.Rational(1, 3)
T = w0 * P0 + w1 * P1


def expect(rho: sp.Matrix, op: sp.Matrix) -> sp.Expr:
    return sp.simplify(sp.trace(rho * op))


# t-channel basis overlaps, giving the F matrix up to harmless basis signs.
# |0_t> = |S_13>|S_24>.
B0_t = (
    ket((0, 0, 1, 1))
    - ket((0, 1, 1, 0))
    - ket((1, 0, 0, 1))
    + ket((1, 1, 0, 0))
) / 2
# Orthogonal total-singlet t-channel state chosen by Gram-Schmidt/sign convention.
B1_t_candidate = B1 - (B0_t.T * B1)[0] * B0_t
B1_t = sp.simplify(B1_t_candidate / sp.sqrt((B1_t_candidate.T * B1_t_candidate)[0]))
F = sp.Matrix([
    [sp.simplify((B0_t.T * B0)[0]), sp.simplify((B0_t.T * B1)[0])],
    [sp.simplify((B1_t.T * B0)[0]), sp.simplify((B1_t.T * B1)[0])],
])


def expr_str(x: sp.Expr) -> str:
    return str(sp.simplify(x))


def matrix_json(m: sp.Matrix) -> list[list[str]]:
    return [[expr_str(m[i, j]) for j in range(m.cols)] for i in range(m.rows)]


one_leg_B0 = [reduced_one(B0, i) for i in range(4)]
one_leg_B1 = [reduced_one(B1, i) for i in range(4)]

assert sp.simplify((B0.T * B0)[0]) == 1
assert sp.simplify((B1.T * B1)[0]) == 1
assert sp.simplify((B0.T * B1)[0]) == 0
assert all(m == sp.eye(2) / 2 for m in one_leg_B0)
assert all(m == sp.eye(2) / 2 for m in one_leg_B1)
assert expect(rho13_B0, P0) == sp.Rational(1, 4)
assert expect(rho13_B1, P0) == sp.Rational(3, 4)
assert expect(rho13_B0, T) == sp.Rational(1, 2)
assert expect(rho13_B1, T) == sp.Rational(5, 6)
assert Gamma_B0 == sp.zeros(4)

payload = {
    'lattice_cell': {
        'gauge_group': 'SU(2)',
        'external_legs': ['j=1/2', 'j=1/2', 'j=1/2', 'j=1/2'],
        'representation_cutoff': 'j_max=1',
        'intertwiner_dimension': 2,
        'B': 's-channel k=0 total singlet',
        'B_prime': 's-channel k=1 total singlet',
    },
    'state_vectors_basis_0000_to_1111': {
        'B': [expr_str(x) for x in B0],
        'B_prime': [expr_str(x) for x in B1],
    },
    'K_sat': {
        'one_leg_representation_multiset': ['1/2', '1/2', '1/2', '1/2'],
        'one_leg_kernel_each_B': matrix_json(one_leg_B0[0]),
        'one_leg_kernel_each_B_prime': matrix_json(one_leg_B1[0]),
        'equal': True,
    },
    'recoupling_F_s_to_t': matrix_json(F),
    'A2_pair_13': {
        'B': matrix_json(rho13_B0),
        'B_prime': matrix_json(rho13_B1),
        'branchwise_product_baseline': matrix_json(rho_product),
    },
    't_channel_singlet_response': {
        'B': expr_str(expect(rho13_B0, P0)),
        'B_prime': expr_str(expect(rho13_B1, P0)),
        'difference': expr_str(expect(rho13_B1, P0) - expect(rho13_B0, P0)),
    },
    'connected_residue_Gamma2': {
        'B': matrix_json(Gamma_B0),
        'B_prime': matrix_json(Gamma_B1),
    },
    'held_out_continuation': {
        'operator': 'T = P_(13,j=0) + (1/3) P_(13,j=1)',
        'heat_kernel_alpha': 'log(3)/2',
        'B_response': expr_str(expect(rho13_B0, T)),
        'B_prime_response': expr_str(expect(rho13_B1, T)),
        'difference': expr_str(expect(rho13_B1, T) - expect(rho13_B0, T)),
        'branchwise_product_response': expr_str(expect(rho_product, T)),
    },
}
OUT.write_text(json.dumps(payload, indent=2) + '\n')
print(json.dumps(payload, indent=2))
