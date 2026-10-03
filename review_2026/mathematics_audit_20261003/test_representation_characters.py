"""Independent exact weight-character checks for the S1 representation model.

Characters are enumerated using semistandard Young tableaux, not the production
Littlewood--Richardson routine or its invariant heuristics. Singlet multiplicity
is the determinant-weight coefficient of the tensor character times the Weyl
denominator product over positive roots. The coefficient formula follows by
expanding each Schur character times the denominator into its alternating
highest-weight numerator: only the determinant representation contributes to
the equal-coordinate weight.
"""
from __future__ import annotations

from collections import Counter
from functools import lru_cache
import itertools
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "review_2026/repairs/s1_carrier_reconstruction"))
import carrier_chain_v3 as core  # noqa: E402
import representation_model as model  # noqa: E402


@lru_cache(maxsize=None)
def character(partition: tuple[int, ...], n: int):
    boxes = [(row, column) for row, width in enumerate(partition) for column in range(width)]
    entries = {}
    weights = [0] * n
    result = Counter()

    def visit(index):
        if index == len(boxes):
            result[tuple(weights)] += 1
            return
        row, column = boxes[index]
        minimum = max(entries.get((row, column - 1), 0), entries.get((row - 1, column), -1) + 1)
        for entry in range(minimum, n):
            entries[(row, column)] = entry
            weights[entry] += 1
            visit(index + 1)
            weights[entry] -= 1
            del entries[(row, column)]

    visit(0)
    return result


def multiply(left, right):
    result = Counter()
    for a, ca in left.items():
        for b, cb in right.items():
            result[tuple(x + y for x, y in zip(a, b))] += ca * cb
    return {weight: coefficient for weight, coefficient in result.items() if coefficient}


@lru_cache(maxsize=None)
def denominator(n):
    result = {tuple([0] * n): 1}
    for i, j in itertools.combinations(range(n), 2):
        root = [0] * n
        root[i], root[j] = -1, 1
        result = multiply(result, {tuple([0] * n): 1, tuple(root): -1})
    return result


def determinant_quotient(char):
    result = Counter()
    for weight, coefficient in char.items():
        result[tuple(w - weight[-1] for w in weight[:-1])] += coefficient
    return result


class RepresentationCharacterTests(unittest.TestCase):
    def test_dimensions_indices_anomalies_and_conjugates(self):
        count = 0
        for n, table in core.REP_TABLE.items():
            h = (n - 1,) + (-1,) * (n - 1)
            fundamental_second = sum(x * x for x in h)
            fundamental_third = sum(x**3 for x in h)
            for name, row in table.items():
                with self.subTest(n=n, rep=name):
                    char = character(tuple(row["partition"]), n)
                    self.assertEqual(sum(char.values()), model.rep_dim(name, n))
                    moments = [sum(m * sum(w * x for w, x in zip(weight, h))**p
                                   for weight, m in char.items()) for p in (2, 3)]
                    self.assertEqual(moments[0], fundamental_second * model.dynkin_twice(name, n))
                    self.assertEqual(moments[1], fundamental_third * model.cubic_anomaly(name, n))
                    if n == 2:
                        self.assertEqual(model.cubic_anomaly(name, n), 0)
                    conjugate = character(tuple(table[row["conjugate"]]["partition"]), n)
                    inverse_character = {tuple(-w for w in weight): m for weight, m in char.items()}
                    self.assertEqual(determinant_quotient(conjugate), determinant_quotient(inverse_character))
                    count += 1
        self.assertEqual(count, 14)

    def test_all_368_tensor_singlet_multiplicities(self):
        count = 0
        for n, table in core.REP_TABLE.items():
            for names in itertools.product(table, repeat=3):
                partitions = tuple(tuple(table[name]["partition"]) for name in names)
                degree = sum(map(sum, partitions))
                expected = 0
                if degree % n == 0:
                    product = {tuple([0] * n): 1}
                    for partition in partitions:
                        product = multiply(product, character(partition, n))
                    target = (degree // n,) * n
                    expected = sum(coefficient * product.get(tuple(t - w for t, w in zip(target, weight)), 0)
                                   for weight, coefficient in denominator(n).items())
                with self.subTest(n=n, reps=names):
                    self.assertEqual(expected, core.singlet_decomposition(*names, n)[0])
                count += 1
        self.assertEqual(count, 368)


if __name__ == "__main__":
    unittest.main()
