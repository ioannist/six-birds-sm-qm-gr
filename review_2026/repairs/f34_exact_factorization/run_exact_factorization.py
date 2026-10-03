"""Recompute exact F34 rank certificates and rank-stratum controls."""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path

import sympy as sp

from exact_factorization import factorization_gauge, rank_mod_prime_float_matrix

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "physics_atlas/thread_qm_gr/steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"
EXPECTED_SHA = "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08"


def integer_frame(matrix):
    ratios = [[float(value).as_integer_ratio() for value in row] for row in matrix]
    denominator = max(den for row in ratios for _, den in row)
    # Binary float denominators are powers of two, so their maximum is an LCM.
    return [[num * (denominator // den) for num, den in row] for row in ratios], denominator


def exact_partial_control(left, right):
    """An exact complement permutation on the represented seed-101 factors.

    Swap the first two rows of R, hence the first two columns of M=LR^T.
    This preserves MM^T and its trace exactly. The right-side observable
    diag(1,-1,0,...) changes expectation from (q0-q1)/norm2 to its negative.
    Integer Gram arithmetic certifies that this difference is nonzero.
    """
    l_int, l_den = integer_frame(left)
    r_int, r_den = integer_frame(right)
    d = left.shape[1]
    gram = [[sum(row[a] * row[b] for row in l_int) for b in range(d)] for a in range(d)]
    energies = [sum(row[a] * gram[a][b] * row[b] for a in range(d) for b in range(d))
                for row in r_int]
    norm2 = sum(energies)
    if norm2 <= 0 or energies[0] == energies[1]:
        raise AssertionError("exact complement permutation failed to separate the physical readout")
    expectation = Fraction(energies[0] - energies[1], norm2)
    return dict(seed=101, unitary="swap boundary coordinates 0 and 1 on the right",
                observable="diag(1,-1,0,...,0) on the right boundary",
                arithmetic="exact integer Gram arithmetic for represented binary-rational factors",
                left_reduced_state_unchanged=True, full_normalized_rays_differ=True,
                expectation_before=str(expectation), expectation_after=str(-expectation),
                squared_norm=str(Fraction(norm2, (l_den * r_den)**2)))


def compute():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA:
        raise AssertionError("Step-42 source pin mismatch")
    spec = importlib.util.spec_from_file_location("f34_rank_source", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    prime = 2147483647
    rows = []
    partial_control = None
    for seed in (101, 202, 303):
        left, right = module.random_tensor_pair(3, seed)
        if seed == 101:
            partial_control = exact_partial_control(left, right)
        for name, matrix in (("left", left), ("right", right)):
            rank, minor_rows = rank_mod_prime_float_matrix(matrix, prime)
            if rank != 27:
                raise AssertionError("represented tensor frame is not certified full rank")
            minor_rank, _ = rank_mod_prime_float_matrix(matrix[list(minor_rows), :], prime)
            if minor_rank != 27:
                raise AssertionError("exported rank minor is singular")
            rows.append(dict(seed=seed, factor=name, shape=list(matrix.shape),
                             modular_rank=rank, rational_rank=rank, minor_rows=list(minor_rows)))

    left = sp.Matrix([[1, 0], [0, 1], [1, 2]])
    right = sp.Matrix([[1, 1], [2, 0], [0, 3], [1, -1]])
    gauge = sp.Matrix([[2, sp.I], [0, sp.Rational(1, 3)]])
    self_return = factorization_gauge(left, right, left * gauge, right * gauge.inv().T)
    if self_return != gauge:
        raise AssertionError("exact complex-rational gauge reconstruction failed")
    raw = left * right.T
    scaled = 2 * raw
    norm2 = sum(value**2 for value in raw)
    scaled_norm2 = sum(value**2 for value in scaled)
    if scaled_norm2 != 4 * norm2 or raw * raw.T / norm2 != scaled * scaled.T / scaled_norm2:
        raise AssertionError("projective readout / raw-scale distinction failed")
    try:
        factorization_gauge(sp.diag(1, 0), sp.eye(2), sp.diag(1, 0), sp.diag(1, 0))
    except ValueError as error:
        if str(error) != "full-column-rank factors required":
            raise
    else:
        raise AssertionError("rank-deficient counterexample was silently accepted")
    try:
        factorization_gauge(left, right, left, right * 2)
    except ValueError as error:
        if str(error) != "full boundary contractions differ":
            raise
    else:
        raise AssertionError("different boundary contractions were silently accepted")
    return dict(source=str(SOURCE.relative_to(ROOT)), source_sha256=digest, prime=prime,
                arithmetic="exact modular certificate for binary-rational real factor coefficients",
                readout="exact raw LR^T, fixed sizes; no rank assertion for rounded floating product",
                frames=rows, exact_partial_control=partial_control,
                exact_gauge_return=True, rank_deficient_control_rejected=True,
                projective_raw_scale_control=True,
                different_boundary_control_rejected=True,
                universal_proof="PROOF.txt; written general argument, finite Python certificate checks")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.self == args.write:
        parser.error("select exactly one of --self or --write")
    payload = json.dumps(compute(), indent=2, sort_keys=True) + "\n"
    path = HERE / "exact_rank_certificates.json"
    if args.write:
        path.write_text(payload)
    elif path.read_text() != payload:
        raise AssertionError("exact rank certificate differs from recomputation")
    print("F34 exact factorization PASS: six rank-27 certificates; exact gauge and partial-readout witness; two negative controls")


if __name__ == "__main__":
    main()
