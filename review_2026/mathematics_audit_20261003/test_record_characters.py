"""Independent weight-character audit of every S6-v3 singlet query.

This checks the separate representation-space dimensions used by the candidate
grammar. It does not construct a UV restriction map or certify physical records.
"""
from __future__ import annotations

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from test_representation_characters import character, denominator, multiply

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "review_2026/repairs/s6_record_grammar_ablation"))
import record_grammar_ablation_v3 as records  # noqa: E402


def singlet_by_character(reps, n):
    product = {tuple([0] * n): 1}
    degree = 0
    for name in reps:
        canonical = records.v2.rm.canonical_rep(name, n)
        partition = tuple(records.v2.v3.REP_TABLE[n][canonical]["partition"])
        degree += sum(partition)
        product = multiply(product, character(partition, n))
    if degree % n:
        return 0
    target = (degree // n,) * n
    return sum(coefficient * product.get(tuple(t - w for t, w in zip(target, weight)), 0)
               for weight, coefficient in denominator(n).items())


class RecordCharacterTests(unittest.TestCase):
    def test_all_singlet_queries_in_complete_bounded_census(self):
        original = records.exact_singlet_multiplicity
        queries = {}

        def collect(reps, n):
            result = original(reps, n)
            queries[(tuple(sorted(reps)), n)] = result
            return result

        with patch.object(records, "exact_singlet_multiplicity", collect):
            records.run()
        self.assertTrue(queries)
        for (reps, n), expected in queries.items():
            with self.subTest(n=n, reps=reps):
                self.assertEqual(singlet_by_character(reps, n), expected)
        print(f"S6 character audit: {len(queries)} distinct queries; candidate dimensions only")


if __name__ == "__main__":
    unittest.main()
