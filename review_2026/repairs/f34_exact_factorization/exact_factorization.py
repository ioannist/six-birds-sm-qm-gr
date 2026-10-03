"""Exact rank-stratum tensor-factorization certificates over Q(i).

The full boundary readout here is the unnormalized matrix L R^T. Transpose
is intentional: a tensor contraction is bilinear, not a Hermitian pairing.
"""
from __future__ import annotations

import sympy as sp


def _exact_matrix(value) -> sp.Matrix:
    matrix = sp.Matrix(value)
    if any(not entry.is_number or entry.has(sp.Float) for entry in matrix):
        raise ValueError("use exact numerical coefficients")
    return matrix


def factorization_gauge(left, right, target_left, target_right) -> sp.Matrix:
    """Construct the unique G with L'=LG, R'=RG^{-T} on the full-rank stratum.

    Preconditions: both pairs have the same internal dimension d>0 and the
    same raw contraction, and rank(L)=rank(R)=d. The target ranks then follow
    from rank(LR^T)=d. Every returned identity is checked exactly.
    """
    left, right, target_left, target_right = map(
        _exact_matrix, (left, right, target_left, target_right)
    )
    dimension = left.cols
    if not dimension or right.cols != dimension:
        raise ValueError("positive common internal dimension required")
    if target_left.shape != left.shape or target_right.shape != right.shape:
        raise ValueError("factorization dimensions differ")
    if left.rank() != dimension or right.rank() != dimension:
        raise ValueError("full-column-rank factors required")
    if left * right.T != target_left * target_right.T:
        raise ValueError("full boundary contractions differ")
    rows = list(left.T.rref()[1])
    square = left.extract(rows, range(dimension))
    gauge = square.inv() * target_left.extract(rows, range(dimension))
    if gauge.det() == 0:
        raise AssertionError("full-rank contraction produced a singular gauge")
    if left * gauge != target_left or right * gauge.inv().T != target_right:
        raise AssertionError("exact intertwiner identity failed")
    return gauge


def rank_mod_prime_float_matrix(matrix, prime: int) -> tuple[int, tuple[int, ...]]:
    """Certify rank of real float coefficients viewed as exact binary rationals.

    A nonzero minor modulo a prime has nonzero rational determinant. This
    certifies the represented factors, not a rounded matrix multiplication or
    an ideal Gaussian draw. All input denominators must be invertible mod p.
    """
    if not sp.isprime(prime):
        raise ValueError("prime modulus required")
    rows = []
    for source_row in matrix:
        row = []
        for value in source_row:
            numerator, denominator = float(value).as_integer_ratio()
            if denominator % prime == 0:
                raise ValueError("coefficient denominator not invertible modulo prime")
            row.append(numerator * pow(denominator, -1, prime) % prime)
        rows.append(row)
    if not rows:
        return 0, ()
    if any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("ragged matrix")
    original_indices = list(range(len(rows)))
    selected = []
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        original_indices[rank], original_indices[pivot] = original_indices[pivot], original_indices[rank]
        selected.append(original_indices[rank])
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [entry * inverse % prime for entry in rows[rank]]
        for i in range(rank + 1, len(rows)):
            coefficient = rows[i][column]
            if coefficient:
                rows[i] = [(a - coefficient * b) % prime for a, b in zip(rows[i], rows[rank])]
        rank += 1
        if rank == min(len(rows), len(rows[0])):
            break
    return rank, tuple(selected)
