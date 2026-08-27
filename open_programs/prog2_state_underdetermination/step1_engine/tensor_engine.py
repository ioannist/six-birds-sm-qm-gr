#!/usr/bin/env python3
"""Explicit dense numerical tensor-network contraction for finite carriers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Mapping

import numpy as np


@dataclass(frozen=True)
class Edge:
    edge_id: str
    u: str
    v: str
    dimension: int
    source_weight: str = ""


@dataclass(frozen=True)
class BoundaryLeg:
    label: str
    vertex: str
    dimension: int


@dataclass(frozen=True)
class Carrier:
    name: str
    vertices: tuple[str, ...]
    edges: tuple[Edge, ...]
    boundaries: tuple[BoundaryLeg, ...]

    def validate(self) -> None:
        vertices = set(self.vertices)
        if len(vertices) != len(self.vertices):
            raise ValueError("duplicate vertex")
        if len({edge.edge_id for edge in self.edges}) != len(self.edges):
            raise ValueError("duplicate edge id")
        if len({leg.label for leg in self.boundaries}) != len(self.boundaries):
            raise ValueError("duplicate boundary label")
        for edge in self.edges:
            if edge.u not in vertices or edge.v not in vertices or edge.u == edge.v:
                raise ValueError(f"bad edge {edge}")
            if edge.dimension < 1:
                raise ValueError(f"bad edge dimension {edge}")
        for leg in self.boundaries:
            if leg.vertex not in vertices or leg.dimension < 1:
                raise ValueError(f"bad boundary leg {leg}")


@dataclass
class TensorNetwork:
    carrier: Carrier
    tensors: dict[str, np.ndarray]
    leg_orders: dict[str, tuple[str, ...]]
    family: str
    seed: int | None

    def copy(self) -> "TensorNetwork":
        return TensorNetwork(
            self.carrier,
            {name: value.copy() for name, value in self.tensors.items()},
            dict(self.leg_orders),
            self.family,
            self.seed,
        )


def physical_leg_id(label: str) -> str:
    return f"physical::{label}"


def leg_dimensions(carrier: Carrier) -> dict[str, int]:
    result = {edge.edge_id: edge.dimension for edge in carrier.edges}
    result.update({physical_leg_id(leg.label): leg.dimension for leg in carrier.boundaries})
    return result


def vertex_leg_orders(carrier: Carrier) -> dict[str, tuple[str, ...]]:
    edge_ids = {
        vertex: tuple(edge.edge_id for edge in carrier.edges if vertex in (edge.u, edge.v))
        for vertex in carrier.vertices
    }
    boundary_ids = {
        vertex: tuple(
            physical_leg_id(leg.label) for leg in carrier.boundaries if leg.vertex == vertex
        )
        for vertex in carrier.vertices
    }
    return {vertex: edge_ids[vertex] + boundary_ids[vertex] for vertex in carrier.vertices}


def _copy_tensor(shape: tuple[int, ...]) -> np.ndarray:
    if not shape:
        return np.array(1.0, dtype=np.complex128)
    if len(set(shape)) != 1:
        raise ValueError("structured copy tensors require equal incident dimensions")
    tensor = np.zeros(shape, dtype=np.complex128)
    for index in range(shape[0]):
        tensor[(index,) * len(shape)] = 1.0
    return tensor


def _random_tensor(shape: tuple[int, ...], seed: int, vertex: str) -> np.ndarray:
    digest = hashlib.sha256(f"{seed}:{vertex}".encode("utf-8")).digest()
    local_seed = int.from_bytes(digest[:8], "big")
    rng = np.random.default_rng(local_seed)
    tensor = rng.normal(size=shape) + 1j * rng.normal(size=shape)
    norm = float(np.linalg.norm(tensor.ravel()))
    if norm == 0:
        raise RuntimeError("random tensor unexpectedly has zero norm")
    return np.asarray(tensor / norm, dtype=np.complex128)


def build_network(carrier: Carrier, family: str, seed: int | None = None) -> TensorNetwork:
    carrier.validate()
    orders = vertex_leg_orders(carrier)
    dimensions = leg_dimensions(carrier)
    tensors: dict[str, np.ndarray] = {}
    for vertex in carrier.vertices:
        shape = tuple(dimensions[leg] for leg in orders[vertex])
        if family == "structured_copy":
            tensors[vertex] = _copy_tensor(shape)
        elif family == "seeded_random_complex":
            if seed is None:
                raise ValueError("seeded random tensors require a seed")
            tensors[vertex] = _random_tensor(shape, seed, vertex)
        else:
            raise ValueError(f"unknown tensor family {family}")
    return TensorNetwork(carrier, tensors, orders, family, seed)


def validate_network(network: TensorNetwork) -> None:
    network.carrier.validate()
    dimensions = leg_dimensions(network.carrier)
    for vertex in network.carrier.vertices:
        if vertex not in network.tensors or vertex not in network.leg_orders:
            raise ValueError(f"missing tensor or leg order at {vertex}")
        order = network.leg_orders[vertex]
        expected = tuple(dimensions[leg] for leg in order)
        if tuple(network.tensors[vertex].shape) != expected:
            raise ValueError(f"tensor shape mismatch at {vertex}: {network.tensors[vertex].shape} != {expected}")
    counts: dict[str, int] = {}
    for order in network.leg_orders.values():
        for leg in order:
            counts[leg] = counts.get(leg, 0) + 1
    for edge in network.carrier.edges:
        if counts.get(edge.edge_id) != 2:
            raise ValueError(f"internal edge {edge.edge_id} occurs {counts.get(edge.edge_id)} times")
    for boundary in network.carrier.boundaries:
        leg = physical_leg_id(boundary.label)
        if counts.get(leg) != 1:
            raise ValueError(f"physical leg {leg} occurs {counts.get(leg)} times")


def contract_boundary_state(network: TensorNetwork) -> np.ndarray:
    """Contract every internal index and return only the ordered boundary state."""
    validate_network(network)
    internal_labels = {edge.edge_id: index for index, edge in enumerate(network.carrier.edges)}
    offset = len(internal_labels)
    physical_labels = {
        physical_leg_id(boundary.label): offset + index
        for index, boundary in enumerate(network.carrier.boundaries)
    }
    labels = {**internal_labels, **physical_labels}
    operands: list[object] = []
    for vertex in network.carrier.vertices:
        operands.extend(
            [network.tensors[vertex], [labels[leg] for leg in network.leg_orders[vertex]]]
        )
    operands.append(
        [physical_labels[physical_leg_id(boundary.label)] for boundary in network.carrier.boundaries]
    )
    state = np.einsum(*operands, optimize="greedy")
    norm = float(np.linalg.norm(np.asarray(state).ravel()))
    if not np.isfinite(norm) or norm <= 1e-14:
        raise RuntimeError(f"contracted state for {network.carrier.name} has zero/non-finite norm")
    return np.asarray(state / norm, dtype=np.complex128)


def uniform_carrier(
    name: str,
    vertices: Iterable[str],
    edges: Iterable[tuple[str, str, str]],
    boundaries: Iterable[tuple[str, str]],
    dimension: int,
    source_weights: Mapping[str, str] | None = None,
) -> Carrier:
    weights = dict(source_weights or {})
    return Carrier(
        name=name,
        vertices=tuple(vertices),
        edges=tuple(
            Edge(edge_id, u, v, dimension, weights.get(edge_id, ""))
            for edge_id, u, v in edges
        ),
        boundaries=tuple(BoundaryLeg(label, vertex, dimension) for label, vertex in boundaries),
    )
