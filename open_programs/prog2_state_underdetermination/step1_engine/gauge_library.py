#!/usr/bin/env python3
"""Tensor-network presentation moves with dense numerical certificates."""

from __future__ import annotations

from dataclasses import replace

import numpy as np

from tensor_engine import BoundaryLeg, Carrier, Edge, TensorNetwork, physical_leg_id, validate_network


def _axis_transform_right(tensor: np.ndarray, axis: int, matrix: np.ndarray) -> np.ndarray:
    transformed = np.tensordot(tensor, matrix, axes=(axis, 0))
    return np.moveaxis(transformed, -1, axis)


def _axis_transform_left(tensor: np.ndarray, axis: int, matrix: np.ndarray) -> np.ndarray:
    transformed = np.tensordot(matrix, tensor, axes=(1, axis))
    return np.moveaxis(transformed, 0, axis)


def apply_internal_gauge(
    network: TensorNetwork, edge_id: str, matrix: np.ndarray
) -> TensorNetwork:
    """Insert ``g`` and ``g^-1`` on the two ends of one contracted edge."""
    edge = next(edge for edge in network.carrier.edges if edge.edge_id == edge_id)
    matrix = np.asarray(matrix, dtype=np.complex128)
    if matrix.shape != (edge.dimension, edge.dimension):
        raise ValueError(f"gauge matrix shape {matrix.shape} != {(edge.dimension,) * 2}")
    inverse = np.linalg.inv(matrix)
    result = network.copy()
    axis_u = result.leg_orders[edge.u].index(edge_id)
    axis_v = result.leg_orders[edge.v].index(edge_id)
    result.tensors[edge.u] = _axis_transform_right(result.tensors[edge.u], axis_u, matrix)
    result.tensors[edge.v] = _axis_transform_left(result.tensors[edge.v], axis_v, inverse)
    validate_network(result)
    return result


def apply_boundary_local_unitary(
    network: TensorNetwork, boundary_label: str, unitary: np.ndarray
) -> TensorNetwork:
    boundary = next(leg for leg in network.carrier.boundaries if leg.label == boundary_label)
    unitary = np.asarray(unitary, dtype=np.complex128)
    if unitary.shape != (boundary.dimension, boundary.dimension):
        raise ValueError("boundary unitary has wrong shape")
    if np.linalg.norm(unitary.conj().T @ unitary - np.eye(boundary.dimension)) > 1e-12:
        raise ValueError("matrix is not unitary")
    result = network.copy()
    leg = physical_leg_id(boundary_label)
    axis = result.leg_orders[boundary.vertex].index(leg)
    result.tensors[boundary.vertex] = _axis_transform_left(
        result.tensors[boundary.vertex], axis, unitary
    )
    validate_network(result)
    return result


def apply_unitary_to_boundary_state(
    state: np.ndarray, boundary_axis: int, unitary: np.ndarray
) -> np.ndarray:
    return _axis_transform_left(np.asarray(state), boundary_axis, np.asarray(unitary))


def merge_series_vertex(network: TensorNetwork, vertex: str) -> TensorNetwork:
    """Absorb a boundary-free bivalent tensor by direct dense contraction."""
    if any(leg.vertex == vertex for leg in network.carrier.boundaries):
        raise ValueError("series merge requires a boundary-free vertex")
    incident = [edge for edge in network.carrier.edges if vertex in (edge.u, edge.v)]
    if len(incident) != 2:
        raise ValueError("series merge requires degree two")
    first, second = incident
    neighbor = first.v if first.u == vertex else first.u
    other = second.v if second.u == vertex else second.u
    if neighbor == other:
        raise ValueError("two-edge loop is a parallel, not series, merge")

    axis_neighbor = network.leg_orders[neighbor].index(first.edge_id)
    axis_vertex = network.leg_orders[vertex].index(first.edge_id)
    merged_tensor = np.tensordot(
        network.tensors[neighbor], network.tensors[vertex], axes=(axis_neighbor, axis_vertex)
    )
    neighbor_order = tuple(leg for leg in network.leg_orders[neighbor] if leg != first.edge_id)
    vertex_order = tuple(leg for leg in network.leg_orders[vertex] if leg != first.edge_id)
    merged_order = neighbor_order + vertex_order

    redirected_second = replace(
        second,
        u=neighbor if second.u == vertex else second.u,
        v=neighbor if second.v == vertex else second.v,
    )
    carrier = Carrier(
        name=network.carrier.name + f"__series_merge_{vertex}",
        vertices=tuple(value for value in network.carrier.vertices if value != vertex),
        edges=tuple(
            redirected_second if edge.edge_id == second.edge_id else edge
            for edge in network.carrier.edges
            if edge.edge_id != first.edge_id
        ),
        boundaries=network.carrier.boundaries,
    )
    tensors = {
        name: value.copy()
        for name, value in network.tensors.items()
        if name not in (neighbor, vertex)
    }
    tensors[neighbor] = merged_tensor
    orders = {
        name: value
        for name, value in network.leg_orders.items()
        if name not in (neighbor, vertex)
    }
    orders[neighbor] = merged_order
    result = TensorNetwork(carrier, tensors, orders, network.family + "+series_merged", network.seed)
    validate_network(result)
    return result


def _fuse_two_axes(
    tensor: np.ndarray, order: tuple[str, ...], first: str, second: str, fused: str
) -> tuple[np.ndarray, tuple[str, ...]]:
    remaining = tuple(leg for leg in order if leg not in (first, second))
    permutation = tuple(order.index(leg) for leg in remaining + (first, second))
    transposed = np.transpose(tensor, permutation)
    fused_tensor = transposed.reshape(transposed.shape[:-2] + (transposed.shape[-2] * transposed.shape[-1],))
    return fused_tensor, remaining + (fused,)


def merge_parallel_edges(
    network: TensorNetwork, first_id: str, second_id: str, fused_id: str
) -> TensorNetwork:
    """Fuse two parallel contracted indices into their product index."""
    first = next(edge for edge in network.carrier.edges if edge.edge_id == first_id)
    second = next(edge for edge in network.carrier.edges if edge.edge_id == second_id)
    if {first.u, first.v} != {second.u, second.v}:
        raise ValueError("edges are not parallel")
    if any(edge.edge_id == fused_id for edge in network.carrier.edges):
        raise ValueError("fused edge id already exists")
    result = network.copy()
    for vertex in (first.u, first.v):
        result.tensors[vertex], result.leg_orders[vertex] = _fuse_two_axes(
            result.tensors[vertex], result.leg_orders[vertex], first_id, second_id, fused_id
        )
    new_edge = Edge(fused_id, first.u, first.v, first.dimension * second.dimension, "exact_product")
    carrier = Carrier(
        name=network.carrier.name + f"__parallel_merge_{first_id}_{second_id}",
        vertices=network.carrier.vertices,
        edges=tuple(
            edge for edge in network.carrier.edges if edge.edge_id not in (first_id, second_id)
        ) + (new_edge,),
        boundaries=network.carrier.boundaries,
    )
    result.carrier = carrier
    result.family += "+parallel_merged"
    validate_network(result)
    return result


def state_residual(left: np.ndarray, right: np.ndarray) -> float:
    if left.shape != right.shape:
        return float("inf")
    return float(np.linalg.norm(np.asarray(left) - np.asarray(right)))
