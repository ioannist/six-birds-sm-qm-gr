"""Boundary and orientation checks for the carrier-general gauge constructor.

These finite tests exercise the mechanism; the general theorem still uses the
written connected-incidence image argument in the Step-6 design note.
"""
from __future__ import annotations

import itertools
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "open_programs/prog2_state_underdetermination/step6_exact_gauge_collapse"))
from step6_core import exponent_certificate  # noqa: E402


def connected(nodes, edges):
    seen = {nodes[0]}
    while True:
        enlarged = seen | {v for u, v in edges if u in seen} | {u for u, v in edges if v in seen}
        if enlarged == seen:
            return len(seen) == len(nodes)
        seen = enlarged


class GaugeCertificateTests(unittest.TestCase):
    def test_all_connected_labelled_graphs_through_four_vertices(self):
        count = 0
        for size in range(1, 5):
            nodes = tuple(range(size))
            possible = tuple(itertools.combinations(nodes, 2))
            for mask in range(1 << len(possible)):
                edges = tuple(edge for i, edge in enumerate(possible) if mask & (1 << i))
                if not connected(nodes, edges):
                    continue
                count += 1
                orientations = {edges, tuple((v, u) for u, v in edges)}
                if edges:
                    orientations.add(((edges[0][1], edges[0][0]),) + edges[1:])
                for oriented in orientations:
                    with self.subTest(nodes=nodes, edges=oriented):
                        cert = exponent_certificate(SimpleNamespace(nodes=nodes, edges=oriented))
                        self.assertEqual(cert.incidence.rank(), size - 1)
                        self.assertEqual(len(cert.left_kernel), 1)
                        self.assertEqual(cert.left_kernel[0], sp.ones(size, 1))
                        self.assertEqual(cert.gauge_basis.shape, (len(edges), max(len(edges) - 1, 0)))
                        self.assertEqual(cert.incidence * cert.gauge_basis,
                                         cert.outgoing_half * cert.log_reduction)
        self.assertEqual(count, 44)

    def test_disconnected_global_product_condition_rejected(self):
        graph = SimpleNamespace(nodes=(0, 1, 2, 3), edges=((0, 1), (2, 3)))
        with self.assertRaisesRegex(ValueError, "connected carriers"):
            exponent_certificate(graph)

    def test_empty_or_malformed_carriers_rejected(self):
        for graph in (
            SimpleNamespace(nodes=(), edges=()),
            SimpleNamespace(nodes=(0, 0), edges=()),
            SimpleNamespace(nodes=(0,), edges=((0, 0),)),
            SimpleNamespace(nodes=(0, 1), edges=((0, 2),)),
        ):
            with self.subTest(graph=graph), self.assertRaises(ValueError):
                exponent_certificate(graph)


if __name__ == "__main__":
    unittest.main()
