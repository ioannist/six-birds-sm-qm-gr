#!/usr/bin/env python3
"""Small exact Gaussian-rational linear-algebra toolkit for the S3 repair."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import gcd
from typing import Iterable, Sequence


def F(value: int | str | Fraction) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


@dataclass(frozen=True, order=True)
class GQ:
    """A Gaussian rational, represented exactly as re + i im."""

    re: Fraction = Fraction(0)
    im: Fraction = Fraction(0)

    def __init__(self, re: int | str | Fraction = 0, im: int | str | Fraction = 0):
        object.__setattr__(self, "re", F(re))
        object.__setattr__(self, "im", F(im))

    def __add__(self, other: object) -> "GQ":
        z = gq(other)
        return GQ(self.re + z.re, self.im + z.im)

    __radd__ = __add__

    def __neg__(self) -> "GQ":
        return GQ(-self.re, -self.im)

    def __sub__(self, other: object) -> "GQ":
        return self + (-gq(other))

    def __rsub__(self, other: object) -> "GQ":
        return gq(other) - self

    def __mul__(self, other: object) -> "GQ":
        z = gq(other)
        return GQ(self.re * z.re - self.im * z.im, self.re * z.im + self.im * z.re)

    __rmul__ = __mul__

    def __truediv__(self, other: object) -> "GQ":
        z = gq(other)
        norm = z.re * z.re + z.im * z.im
        if not norm:
            raise ZeroDivisionError
        return GQ((self.re * z.re + self.im * z.im) / norm,
                  (self.im * z.re - self.re * z.im) / norm)

    def conjugate(self) -> "GQ":
        return GQ(self.re, -self.im)

    def __bool__(self) -> bool:
        return bool(self.re or self.im)

    def __str__(self) -> str:
        if not self.im:
            return str(self.re)
        if not self.re:
            return f"{self.im}i"
        sign = "+" if self.im > 0 else "-"
        return f"{self.re}{sign}{abs(self.im)}i"


def gq(value: object) -> GQ:
    if isinstance(value, GQ):
        return value
    if isinstance(value, (int, str, Fraction)):
        return GQ(value)
    raise TypeError(f"cannot convert {type(value).__name__} to GQ")


Matrix = tuple[tuple[GQ, ...], ...]


def matrix(rows: Iterable[Iterable[object]]) -> Matrix:
    out = tuple(tuple(gq(x) for x in row) for row in rows)
    if out and any(len(row) != len(out[0]) for row in out):
        raise ValueError("ragged matrix")
    return out


def zeros(n: int, m: int | None = None) -> Matrix:
    m = n if m is None else m
    return matrix([[0] * m for _ in range(n)])


def eye(n: int) -> Matrix:
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def unit(n: int, i: int, j: int, value: object = 1) -> Matrix:
    rows = [[GQ() for _ in range(n)] for _ in range(n)]
    rows[i][j] = gq(value)
    return matrix(rows)


def diagonal(values: Sequence[object]) -> Matrix:
    return matrix([[gq(values[i]) if i == j else GQ() for j in range(len(values))]
                   for i in range(len(values))])


def madd(a: Matrix, b: Matrix) -> Matrix:
    return matrix([[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))])


def msub(a: Matrix, b: Matrix) -> Matrix:
    return matrix([[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))])


def mscale(c: object, a: Matrix) -> Matrix:
    z = gq(c)
    return matrix([[z * x for x in row] for row in a])


def matmul(a: Matrix, b: Matrix) -> Matrix:
    if len(a[0]) != len(b):
        raise ValueError("matrix dimensions do not match")
    return matrix([[sum((a[i][k] * b[k][j] for k in range(len(b))), GQ())
                    for j in range(len(b[0]))] for i in range(len(a))])


def dagger(a: Matrix) -> Matrix:
    return matrix([[a[j][i].conjugate() for j in range(len(a))] for i in range(len(a[0]))])


def trace(a: Matrix) -> GQ:
    return sum((a[i][i] for i in range(min(len(a), len(a[0])))), GQ())


def commutator(a: Matrix, b: Matrix) -> Matrix:
    return msub(matmul(a, b), matmul(b, a))


def is_zero(a: Matrix) -> bool:
    return not any(x for row in a for x in row)


def flatten(a: Matrix) -> tuple[GQ, ...]:
    return tuple(x for row in a for x in row)


def rational_matrix_rank(rows: Sequence[Sequence[Fraction]]) -> int:
    _, pivots = rref(rows)
    return len(pivots)


def gaussian_matrix_rank(rows: Sequence[Sequence[GQ]]) -> int:
    work = [list(row) for row in rows]
    if not work:
        return 0
    nr, nc = len(work), len(work[0])
    rank = 0
    for col in range(nc):
        pivot = next((r for r in range(rank, nr) if work[r][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        p = work[rank][col]
        work[rank] = [x / p for x in work[rank]]
        for r in range(nr):
            if r != rank and work[r][col]:
                q = work[r][col]
                work[r] = [work[r][c] - q * work[rank][c] for c in range(nc)]
        rank += 1
        if rank == nr:
            break
    return rank


def matrix_span_rank(matrices: Sequence[Matrix]) -> int:
    if not matrices:
        return 0
    vectors = [flatten(a) for a in matrices]
    return gaussian_matrix_rank(list(map(list, zip(*vectors))))


def rref(rows: Sequence[Sequence[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    work = [[F(x) for x in row] for row in rows]
    if not work:
        return work, []
    nr, nc = len(work), len(work[0])
    pivots: list[int] = []
    row = 0
    for col in range(nc):
        pivot = next((r for r in range(row, nr) if work[r][col]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        p = work[row][col]
        work[row] = [x / p for x in work[row]]
        for r in range(nr):
            if r != row and work[r][col]:
                q = work[r][col]
                work[r] = [work[r][c] - q * work[row][c] for c in range(nc)]
        pivots.append(col)
        row += 1
        if row == nr:
            break
    return work, pivots


def nullspace(rows: Sequence[Sequence[Fraction]], ncols: int | None = None) -> list[tuple[Fraction, ...]]:
    if rows:
        ncols = len(rows[0])
    elif ncols is None:
        raise ValueError("ncols is required for an empty system")
    reduced, pivots = rref(rows)
    free = [c for c in range(ncols) if c not in pivots]
    basis = []
    for f in free:
        vector = [Fraction(0)] * ncols
        vector[f] = Fraction(1)
        for r, p in enumerate(pivots):
            vector[p] = -reduced[r][f]
        basis.append(tuple(vector))
    return basis


def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def primitive_integer(vector: Sequence[Fraction], preferred_index: int | None = None) -> tuple[int, ...]:
    denominator = 1
    for x in vector:
        denominator = lcm(denominator, x.denominator)
    values = [int(x * denominator) for x in vector]
    common = 0
    for x in values:
        common = gcd(common, abs(x))
    if common:
        values = [x // common for x in values]
    first = preferred_index if preferred_index is not None else next((i for i, x in enumerate(values) if x), 0)
    if values[first] < 0:
        values = [-x for x in values]
    return tuple(values)


def determinant(a: Sequence[Sequence[int | Fraction]]) -> Fraction:
    n = len(a)
    if any(len(row) != n for row in a):
        raise ValueError("determinant requires a square matrix")
    work = [[F(x) for x in row] for row in a]
    det = Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if work[r][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            det = -det
        p = work[col][col]
        det *= p
        for r in range(col + 1, n):
            if work[r][col]:
                q = work[r][col] / p
                for c in range(col, n):
                    work[r][c] -= q * work[col][c]
    return det


def smith_invariants(a: Sequence[Sequence[int]]) -> tuple[int, tuple[int, ...]]:
    """Return rank and nonzero SNF invariants via gcds of exact minors."""
    nr = len(a)
    nc = len(a[0]) if nr else 0
    rank = rational_matrix_rank([[Fraction(x) for x in row] for row in a])
    determinantal_divisors = [1]
    for size in range(1, rank + 1):
        divisor = 0
        for rs in combinations(range(nr), size):
            for cs in combinations(range(nc), size):
                minor = [[a[r][c] for c in cs] for r in rs]
                divisor = gcd(divisor, abs(int(determinant(minor))))
        determinantal_divisors.append(divisor)
    invariants = tuple(determinantal_divisors[i] // determinantal_divisors[i - 1]
                       for i in range(1, rank + 1))
    return rank, invariants


def su_hermitian_basis(n: int, prefix: str = "T") -> list[tuple[str, Matrix]]:
    out: list[tuple[str, Matrix]] = []
    for i in range(n):
        for j in range(i + 1, n):
            out.append((f"{prefix}_S_{i}{j}", madd(unit(n, i, j), unit(n, j, i))))
            out.append((f"{prefix}_A_{i}{j}", madd(unit(n, i, j, GQ(0, -1)), unit(n, j, i, GQ(0, 1)))))
    for k in range(1, n):
        values = [1] * k + [-k] + [0] * (n - k - 1)
        out.append((f"{prefix}_D_{k}", diagonal(values)))
    return out


def embed(a: Matrix, indices: Sequence[int], n: int) -> Matrix:
    rows = [[GQ() for _ in range(n)] for _ in range(n)]
    for i, ii in enumerate(indices):
        for j, jj in enumerate(indices):
            rows[ii][jj] = a[i][j]
    return matrix(rows)


def format_fraction(x: Fraction | int) -> str:
    return str(F(x))


def matrix_key(a: Matrix) -> str:
    return ";".join(",".join(str(x) for x in row) for row in a)
