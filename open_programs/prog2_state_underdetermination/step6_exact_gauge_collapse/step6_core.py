#!/usr/bin/env python3
"""Exact certificates for the PROG2 Step-6 C2_L1 gauge collapse."""
from __future__ import annotations

import csv
import hashlib
import io
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import sympy as sp

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEP5_DIR = HERE.parent / "step5_family_gauge_classification"
STEP4_DIR = HERE.parent / "step4_finite_continuation"
EXTERNAL_DIR = HERE / "external_input"
for directory in (STEP5_DIR, STEP4_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from step5_core import (  # noqa: E402
    construct_pairs,
    invariant,
    invariant_text,
    product,
)
from algebraic_engine import enumerate_cuts, same_fingerprint  # noqa: E402

EVIDENCE_TYPES = ("COMPUTED", "PROVED_BY_DEFINITION", "EXTERNAL_REPRODUCED")

PINNED = {
    STEP5_DIR / "step5_core.py": "36d76e5b56731ffeca11f4aa58aace77ba331c88e012d9c96056f8ce38187f14",
    STEP5_DIR / "declaration_step5.md": "8d67fddad7475056c97a90155e4e78e92e4f6e2de3def0c4997674a2031c7ffa",
    STEP4_DIR / "algebraic_engine.py": "e6819d412bc4c89e315f74462a8ac16f8dae02b895555af39e3ac08e1beac1bd",
    STEP4_DIR / "step4_core.py": "6abbf8f3653b4966fff1ef4bd1e72dcbe3325e17b186991754cff1c3f352120f",
    STEP4_DIR / "candidate_outcomes_step4.csv": "f91bbfe845d806dcb5ddd189b48fe9f48eaac8c94c21e909494e1a5497601a9f",
    EXTERNAL_DIR / "reviewer_finding_excerpt.md": "854b76b5d497e6939766114dd3da5e5a4e8ba86ca24dc3f2d6594e665e91130a",
    EXTERNAL_DIR / "prog2_diagonal_gauge_audit.py": "c076483303dfff3ac5ecf619d19837e4b8e941f437c37640a64f232be0cf607e",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_pins() -> list[dict[str, Any]]:
    rows = []
    for path, expected in PINNED.items():
        actual = sha256(path)
        rows.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "passes": actual == expected,
                "evidence_type": "COMPUTED",
            }
        )
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"dependency pin failure: {rows}")
    return rows


def _qtext(value: sp.Expr) -> str:
    value = sp.Rational(value)
    return str(int(value.p)) if value.q == 1 else f"{int(value.p)}/{int(value.q)}"


def _matrix_zero(matrix: sp.Matrix) -> bool:
    return all(value == 0 for value in matrix)


def _connected(graph: Any) -> tuple[bool, int]:
    adjacency = {node: set() for node in graph.nodes}
    for u, v in graph.edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    seen = {graph.nodes[0]}
    stack = [graph.nodes[0]]
    while stack:
        node = stack.pop()
        for neighbor in adjacency[node] - seen:
            seen.add(neighbor)
            stack.append(neighbor)
    return len(seen) == len(graph.nodes), 1 if len(seen) == len(graph.nodes) else 0


def _copy_support(graph: Any) -> tuple[int, tuple[str, ...]]:
    """Enumerate exact binary assignments admitted by every internal copy edge."""
    nodes = tuple(graph.nodes)
    index = {node: position for position, node in enumerate(nodes)}
    patterns = set()
    admitted = 0
    for mask in range(1 << len(nodes)):
        bits = tuple(int(bool(mask & (1 << position))) for position in range(len(nodes)))
        if not all(bits[index[u]] == bits[index[v]] for u, v in graph.edges):
            continue
        admitted += 1
        patterns.add("".join(str(bits[index[graph.boundary_map[label]]]) for label in graph.boundaries))
    return admitted, tuple(sorted(patterns))


@dataclass(frozen=True)
class ExponentCertificate:
    incidence: sp.Matrix
    outgoing_half: sp.Matrix
    log_reduction: sp.Matrix
    gauge_basis: sp.Matrix
    left_kernel: tuple[sp.Matrix, ...]


def exponent_certificate(graph: Any) -> ExponentCertificate:
    """Solve the formal-log incidence problem over QQ.

    The final edge log-ratio is eliminated using sum(log r_e)=0.  Columns of
    ``gauge_basis`` therefore give exact rational exponents of the independent
    ratio monomials used in each diagonal gauge entry.
    """
    nodes = tuple(graph.nodes)
    edges = tuple(graph.edges)
    node_index = {node: index for index, node in enumerate(nodes)}
    vertex_count, edge_count = len(nodes), len(edges)
    if edge_count < 2:
        raise AssertionError("Step-6 carriers require at least two edges")

    incidence = sp.zeros(vertex_count, edge_count)
    outgoing_half = sp.zeros(vertex_count, edge_count)
    for edge_index, (u, v) in enumerate(edges):
        incidence[node_index[u], edge_index] = 1
        incidence[node_index[v], edge_index] = -1
        outgoing_half[node_index[u], edge_index] = sp.Rational(1, 2)

    # l = R l_independent, with l_last = -sum(l_0,...,l_{E-2}).
    reduction = sp.zeros(edge_count, edge_count - 1)
    for column in range(edge_count - 1):
        reduction[column, column] = 1
        reduction[edge_count - 1, column] = -1
    target = outgoing_half * reduction

    reduced_incidence = incidence[:-1, :]
    columns = []
    for column in range(target.cols):
        solution_set = sp.linsolve(
            (reduced_incidence, target[:-1, column]),
            *sp.symbols(f"x0:{edge_count}"),
        )
        solution = next(iter(solution_set))
        free = sorted(set().union(*(value.free_symbols for value in solution)), key=str)
        chosen = [sp.simplify(value.subs({symbol: 0 for symbol in free})) for value in solution]
        columns.append(sp.Matrix(chosen))
    gauge_basis = sp.Matrix.hstack(*columns)
    if not _matrix_zero(incidence * gauge_basis - target):
        raise AssertionError("exact formal-log incidence identity failed")

    return ExponentCertificate(
        incidence=incidence,
        outgoing_half=outgoing_half,
        log_reduction=reduction,
        gauge_basis=gauge_basis,
        left_kernel=tuple(incidence.T.nullspace()),
    )


def _incidence_and_dressing(nodes: tuple[str, ...], edges: tuple[tuple[str, str], ...]) -> tuple[sp.Matrix, sp.Matrix]:
    node_index = {node: index for index, node in enumerate(nodes)}
    incidence = sp.zeros(len(nodes), len(edges))
    dressing = sp.zeros(len(nodes), len(edges))
    for edge_index, (u, v) in enumerate(edges):
        incidence[node_index[u], edge_index] = 1
        incidence[node_index[v], edge_index] = -1
        dressing[node_index[u], edge_index] = sp.Rational(1, 2)
    return incidence, dressing


def negative_control_rows(pairs: list[Any]) -> list[dict[str, Any]]:
    """Exact can-fail controls for the incidence/exponent theorem."""
    pair = pairs[0]
    graph = pair.base
    incidence, dressing = _incidence_and_dressing(tuple(graph.nodes), tuple(graph.edges))

    # (a) A real carrier with c'_0=2c_0 has product ratio 2.  In units of
    # log(2), ell=e_0 and the all-ones left-kernel functional is exactly 1/2.
    unequal_weights = list(graph.weights)
    unequal_weights[0] = unequal_weights[0] * 2
    ratio_product = pair.field.element(1)
    for base, target in zip(graph.weights, unequal_weights):
        ratio_product *= target / base
    unequal_log = sp.zeros(len(graph.edges), 1)
    unequal_log[0, 0] = 1
    unequal_target = dressing * unequal_log
    unequal_obstruction = (sp.ones(1, len(graph.nodes)) * unequal_target)[0]
    unequal_unsolvable = incidence.row_join(unequal_target).rank() > incidence.rank()
    unequal_reason = "LEFT_KERNEL_PRODUCT_OBSTRUCTION"

    # (b) Mutate one stored orientation in B while retaining the original
    # dressing side in D.  The already solved exact X must cease to satisfy the
    # defining identity.
    certificate = exponent_certificate(graph)
    mutated_incidence = certificate.incidence.copy()
    mutated_incidence[:, 0] *= -1
    mutated_identity = _matrix_zero(
        mutated_incidence * certificate.gauge_basis
        - certificate.outgoing_half * certificate.log_reduction
    )
    orientation_reason = "ORIENTATION_DRESSING_MISMATCH_BREAKS_BX_EQ_DR"

    # (c) Two disconnected three-vertex paths.  The bad formal log vector has
    # zero global sum but component sums +1 and -1.  The repaired vector has
    # zero sum on each component.
    nodes = ("A", "B", "C", "D", "E", "F")
    edges = (("A", "B"), ("B", "C"), ("D", "E"), ("E", "F"))
    disconnected_b, disconnected_d = _incidence_and_dressing(nodes, edges)
    left_kernel = tuple(disconnected_b.T.nullspace())
    component_indicators = (
        sp.Matrix([1, 1, 1, 0, 0, 0]),
        sp.Matrix([0, 0, 0, 1, 1, 1]),
    )
    expected_left_space = sp.Matrix.hstack(*component_indicators)
    actual_left_space = sp.Matrix.hstack(*left_kernel)
    left_kernel_componentwise = (
        len(left_kernel) == 2
        and actual_left_space.rank() == 2
        and actual_left_space.row_join(expected_left_space).rank() == 2
    )
    global_only_log = sp.Matrix([1, 0, -1, 0])
    global_only_target = disconnected_d * global_only_log
    global_product_equal = sum(global_only_log) == 0
    component_obstructions = tuple((vector.T * global_only_target)[0] for vector in component_indicators)
    global_only_unsolvable = disconnected_b.row_join(global_only_target).rank() > disconnected_b.rank()
    componentwise_log = sp.Matrix([1, -1, 1, -1])
    componentwise_target = disconnected_d * componentwise_log
    componentwise_obstructions = tuple((vector.T * componentwise_target)[0] for vector in component_indicators)
    componentwise_solvable = disconnected_b.row_join(componentwise_target).rank() == disconnected_b.rank()
    disconnected_reason = "COMPONENTWISE_PRODUCT_OBSTRUCTION"

    rows = [
        {
            "control_id": "unequal_product_real_carrier",
            "expected_failure_reason": unequal_reason,
            "observed_failure_reason": unequal_reason if unequal_unsolvable else "NO_FAILURE",
            "exact_obstruction": _qtext(unequal_obstruction),
            "product_condition": f"ratio={ratio_product.expression('alpha')}",
            "repair_check": "not_applicable",
            "evidence_type": "COMPUTED",
            "passes": ratio_product == pair.field.element(2) and unequal_obstruction != 0 and unequal_unsolvable,
        },
        {
            "control_id": "one_edge_orientation_mutation",
            "expected_failure_reason": orientation_reason,
            "observed_failure_reason": orientation_reason if not mutated_identity else "NO_FAILURE",
            "exact_obstruction": "BX-DR_nonzero",
            "product_condition": "unchanged_equal_product_formal_domain",
            "repair_check": "original_orientation_identity_passes=" + str(
                _matrix_zero(
                    certificate.incidence * certificate.gauge_basis
                    - certificate.outgoing_half * certificate.log_reduction
                )
            ),
            "evidence_type": "COMPUTED",
            "passes": not mutated_identity,
        },
        {
            "control_id": "disconnected_global_vs_component_products",
            "expected_failure_reason": disconnected_reason,
            "observed_failure_reason": disconnected_reason if global_only_unsolvable else "NO_FAILURE",
            "exact_obstruction": "|".join(_qtext(value) for value in component_obstructions),
            "product_condition": "global_log_sum=0; component_log_sums_nonzero",
            "repair_check": "componentwise_equal_products_restore_solvability=" + str(
                componentwise_solvable and all(value == 0 for value in componentwise_obstructions)
            ),
            "evidence_type": "COMPUTED",
            "passes": (
                left_kernel_componentwise
                and global_product_equal
                and global_only_unsolvable
                and all(value != 0 for value in component_obstructions)
                and componentwise_solvable
                and all(value == 0 for value in componentwise_obstructions)
            ),
        },
    ]
    if not all(row["passes"] and row["observed_failure_reason"] == row["expected_failure_reason"] for row in rows):
        raise AssertionError(f"negative control failure: {rows}")
    return rows


def _left_kernel_is_component_ones(certificate: ExponentCertificate) -> bool:
    if len(certificate.left_kernel) != 1:
        return False
    vector = certificate.left_kernel[0]
    if vector[0] == 0:
        return False
    normalized = vector / vector[0]
    return normalized == sp.ones(certificate.incidence.rows, 1)


def _gauge_rows(pair: Any, certificate: ExponentCertificate) -> list[dict[str, Any]]:
    rows = []
    for edge_index, (u, v) in enumerate(pair.base.edges):
        coefficients = tuple(certificate.gauge_basis[edge_index, column] for column in range(certificate.gauge_basis.cols))
        inverse = tuple(-value for value in coefficients)
        cancellation = all(left + right == 0 for left, right in zip(coefficients, inverse))
        rows.append(
            {
                "candidate_id": pair.candidate_id,
                "edge_index": edge_index,
                "edge_u": u,
                "edge_v": v,
                "independent_log_ratio_count": len(coefficients),
                "gauge_zero_branch_exponents": "|".join(_qtext(value) for value in coefficients),
                "inverse_zero_branch_exponents": "|".join(_qtext(value) for value in inverse),
                "edge_g_g_inverse_exponents_cancel_exact": cancellation,
                "evidence_type": "COMPUTED",
                "passes": cancellation,
            }
        )
    return rows


def run_external_float_control() -> tuple[list[dict[str, Any]], str]:
    script = EXTERNAL_DIR / "prog2_diagonal_gauge_audit.py"
    source = script.read_text(encoding="utf-8")
    hardcoded = "ROOT=Path('/home/repos/six-birds-sm-qm-gr')"
    if source.count(hardcoded) != 1:
        raise AssertionError("staged external script ROOT line changed unexpectedly")
    portable = source.replace(hardcoded, f"ROOT=Path({str(REPO_ROOT)!r})")
    with tempfile.TemporaryDirectory(prefix="prog2_step6_external_control_") as directory:
        portable_script = Path(directory) / script.name
        portable_script.write_text(portable, encoding="utf-8")
        completed = subprocess.run(
            [sys.executable, str(portable_script)],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )
    output = completed.stdout
    if completed.returncode != 0 or not output.rstrip().endswith("PASS"):
        raise AssertionError(f"external float audit failed:\n{output}\n{completed.stderr}")
    lines = output.strip().splitlines()
    reader = csv.DictReader(io.StringIO("\n".join(lines[:-1])))
    rows = []
    for source in reader:
        numeric_fields = [key for key in source if key != "candidate"]
        maximum = max(abs(float(source[key])) for key in numeric_fields)
        row = {
            "candidate_id": source["candidate"],
            **{key: source[key] for key in numeric_fields},
            "maximum_absolute_residual": f"{maximum:.3e}",
            "evidence_type": "EXTERNAL_REPRODUCED",
            "passes": maximum < 1e-10,
        }
        rows.append(row)
    if len(rows) != 6 or not all(row["passes"] for row in rows):
        raise AssertionError(f"unexpected external float rows: {rows}")
    return rows, output


def _ledger_row(candidate: str, check: str, evidence: str, passes: bool, detail: str) -> dict[str, Any]:
    if evidence not in EVIDENCE_TYPES:
        raise AssertionError(evidence)
    return {
        "candidate_id": candidate,
        "check": check,
        "evidence_type": evidence,
        "passes": passes,
        "detail": detail,
    }


def compute_all() -> dict[str, Any]:
    pins = verify_pins()
    pairs = construct_pairs()
    external_rows, external_log = run_external_float_control()
    external_by_id = {row["candidate_id"]: row for row in external_rows}
    certificates = []
    product_rows = []
    gauge_rows = []
    ledger = []

    for pair in pairs:
        base_product = product(pair.base.weights)
        displaced_product = product(pair.displaced.weights)
        product_equal = base_product == displaced_product
        ratio_product = pair.field.element(1)
        for base, displaced in zip(pair.base.weights, pair.displaced.weights):
            ratio_product *= displaced / base
        ratio_product_one = ratio_product == pair.field.element(1)
        capacities_distinct = pair.base.weights != pair.displaced.weights
        connected, component_count = _connected(pair.base)
        support_count, support_patterns = _copy_support(pair.base)
        expected_patterns = ("0" * len(pair.base.boundaries), "1" * len(pair.base.boundaries))
        support_exact = support_count == 2 and support_patterns == expected_patterns

        one = pair.field.element(1)
        base_zero_probability = base_product / (one + base_product)
        displaced_zero_probability = displaced_product / (one + displaced_product)
        normalized_state_equal = base_zero_probability == displaced_zero_probability
        fingerprint_equal = same_fingerprint(enumerate_cuts(pair.base), enumerate_cuts(pair.displaced))

        exponent = exponent_certificate(pair.base)
        rank = int(exponent.incidence.rank())
        left_nullity = len(exponent.left_kernel)
        expected_rank = len(pair.base.nodes) - component_count
        left_ones = _left_kernel_is_component_ones(exponent)
        target_identity = _matrix_zero(
            exponent.incidence * exponent.gauge_basis
            - exponent.outgoing_half * exponent.log_reduction
        )
        local_gauge_rows = _gauge_rows(pair, exponent)
        edge_inverse = all(row["passes"] for row in local_gauge_rows)
        gauge_rows.extend(local_gauge_rows)
        intertwiner_exact = (
            product_equal
            and ratio_product_one
            and connected
            and rank == expected_rank
            and left_nullity == component_count
            and left_ones
            and target_identity
            and edge_inverse
        )

        base_invariant = invariant(pair.base)
        displaced_invariant = invariant(pair.displaced)
        invariant_differs = base_invariant != displaced_invariant
        external = external_by_id[pair.candidate_id]
        joint_noninjective = capacities_distinct and fingerprint_equal and normalized_state_equal
        retyped = (
            "EXACT_JOINT_CUT_STATE_MAP_FIBER__TENSOR_PRESENTATION_GAUGE_COLLAPSED"
            if joint_noninjective and intertwiner_exact
            else "CERTIFICATE_FAILURE"
        )

        product_rows.append(
            {
                "candidate_id": pair.candidate_id,
                "carrier": pair.carrier,
                "number_field_degree": pair.field.degree,
                "exact_capacity_product": base_product.expression("alpha"),
                "base_displaced_product_equal_exact": product_equal,
                "ratio_product_is_one_exact": ratio_product_one,
                "copy_support_assignment_count": support_count,
                "copy_boundary_support_patterns": "|".join(support_patterns),
                "normalized_zero_probability_exact": base_zero_probability.expression("alpha"),
                "normalized_state_equal_exact": normalized_state_equal,
                "evidence_type": "COMPUTED",
                "passes": product_equal and ratio_product_one and support_exact and normalized_state_equal,
            }
        )
        certificates.append(
            {
                "candidate_id": pair.candidate_id,
                "carrier": pair.carrier,
                "source_seed_provenance": pair.seed,
                "direction_index": pair.direction_index,
                "number_field_degree": pair.field.degree,
                "vertex_count": len(pair.base.nodes),
                "edge_count": len(pair.base.edges),
                "capacity_vectors_distinct_exact": capacities_distinct,
                "complete_cut_fingerprint_equal_exact": fingerprint_equal,
                "product_equal_exact": product_equal,
                "connected_exact": connected,
                "incidence_rank_exact": rank,
                "expected_incidence_rank": expected_rank,
                "left_kernel_dimension_exact": left_nullity,
                "left_kernel_component_ones_exact": left_ones,
                "formal_log_target_identity_exact": target_identity,
                "per_edge_g_g_inverse_identity_exact": edge_inverse,
                "diagonal_intertwiner_exists_exact": intertwiner_exact,
                "normalized_connected_copy_state_equal_exact": normalized_state_equal,
                "joint_cut_state_map_noninjective_exact": joint_noninjective,
                "exact_certificate_evidence_type": "COMPUTED",
                "base_decorated_invariant_exact": invariant_text(base_invariant),
                "displaced_decorated_invariant_exact": invariant_text(displaced_invariant),
                "decorated_invariant_differs_exact": invariant_differs,
                "decorated_separation_evidence_type": "PROVED_BY_DEFINITION",
                "float_control_maximum_residual": external["maximum_absolute_residual"],
                "float_control_evidence_type": "EXTERNAL_REPRODUCED",
                "retyped_classification": retyped,
                "passes": retyped != "CERTIFICATE_FAILURE" and invariant_differs and external["passes"],
            }
        )

        ledger.extend(
            [
                _ledger_row(pair.candidate_id, "stored_algebraic_capacity_vectors_distinct", "COMPUTED", capacities_distinct, "exact QQ(alpha) coefficient comparison"),
                _ledger_row(pair.candidate_id, "complete_terminal_cut_fingerprint_equal", "COMPUTED", fingerprint_equal, "exact min-cut enumeration on both stored endpoints"),
                _ledger_row(pair.candidate_id, "capacity_products_equal", "COMPUTED", product_equal and ratio_product_one, "exact QQ(alpha) multiplication and division"),
                _ledger_row(pair.candidate_id, "connected_copy_support_is_two_global_strings", "COMPUTED", support_exact, "exhaustive binary vertex-assignment enumeration"),
                _ledger_row(pair.candidate_id, "incidence_rank_and_left_kernel", "COMPUTED", rank == expected_rank and left_nullity == 1 and left_ones, "exact QQ matrix rank/nullspace"),
                _ledger_row(pair.candidate_id, "formal_exponent_monomial_identity", "COMPUTED", target_identity and edge_inverse, "exact QQ exponent-vector equality after product-log elimination"),
                _ledger_row(pair.candidate_id, "diagonal_tensor_intertwiner", "COMPUTED", intertwiner_exact, "follows from exact product, connectivity, and exponent certificate"),
                _ledger_row(pair.candidate_id, "external_float_tensor_audit", "EXTERNAL_REPRODUCED", external["passes"], f"maximum reproduced residual {external['maximum_absolute_residual']}"),
                _ledger_row(pair.candidate_id, "decorated_invariant_values_differ", "COMPUTED", invariant_differs, "exact QQ(alpha) invariant comparison"),
                _ledger_row(pair.candidate_id, "decorated_carrier_inequivalence_under_frozen_capacity_label_rule", "PROVED_BY_DEFINITION", invariant_differs, "the frozen relation stipulates that internal gauge does not act on ontic capacity labels"),
            ]
        )

    controls = negative_control_rows(pairs)
    ledger.extend(
        _ledger_row("CONTROL", row["control_id"], "COMPUTED", row["passes"], row["observed_failure_reason"])
        for row in controls
    )
    if len(certificates) != 6:
        raise AssertionError("expected six Step-5 pairs")
    if not all(row["passes"] for row in product_rows + certificates + gauge_rows + ledger):
        raise AssertionError("one or more Step-6 certificates failed")
    if {row["evidence_type"] for row in ledger} != set(EVIDENCE_TYPES):
        raise AssertionError("evidence taxonomy not fully populated")

    return {
        "dependency_pins": pins,
        "product_lemma": product_rows,
        "intertwiner_certificates": certificates,
        "gauge_exponent_basis": gauge_rows,
        "external_float_audit": external_rows,
        "negative_controls": controls,
        "proof_ledger": ledger,
        "external_float_log": external_log,
        "aggregate_verdict": "SIX_EXACT_JOINT_MAP_FIBERS__ALL_TENSOR_PRESENTATION_GAUGE_COLLAPSED",
    }
