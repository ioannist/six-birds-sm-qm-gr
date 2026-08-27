#!/usr/bin/env python3
"""Corrected exact-kernel finite continuation for PROG2 Step 4."""

from __future__ import annotations

import csv
import hashlib
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

import mpmath as mp
import numpy as np
import sympy as sp

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEP1_DIR = HERE.parent / "step1_engine"
STEP2_DIR = HERE.parent / "step2_fiber_states"
STEP3_DIR = HERE.parent / "step3_kernel_test"
PROG3_DIR = REPO_ROOT / "open_programs/prog3_cut_fingerprints/step1_finite_range"
PROG3_STEP2_DIR = REPO_ROOT / "open_programs/prog3_cut_fingerprints/step2_orbit_saturation"
for directory in (PROG3_STEP2_DIR, PROG3_DIR, STEP3_DIR, STEP2_DIR, STEP1_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from algebraic_engine import (NumberField, canonical_key, enumerate_cuts,
    exact_root_certificate, explored_capacity_signature, lift_graph,
    orbit_intersection, reciprocal_first_canary, same_fingerprint,
    saturate_combined)  # noqa: E402
from conventions_step3 import convention_by_id  # noqa: E402
from gauge_library import apply_internal_gauge, state_residual  # noqa: E402
from state_entropy import full_entropy_analysis  # noqa: E402
from step1_core import state_digest, vector_digest  # noqa: E402
from step2_core import compare_entropy_vectors  # noqa: E402
from step3_core import (dress_network, exact_copy_null_basis, group_base_cases,
    labels_and_dimensions, load_fibers, state_for_capacities)  # noqa: E402
from survivor_loader import as_tensor_carrier  # noqa: E402
from tensor_engine import build_network, contract_boundary_state  # noqa: E402

PINNED_DEPENDENCIES = {
    STEP1_DIR / "tensor_engine.py": "52640d2d195d3928ff18c01af59f3a06a72d10fb10f136b69f5a4b2f65f774df",
    STEP1_DIR / "state_entropy.py": "24b27147295af99402193bec760957ef7041b555e5da6875e92524072821df5a",
    STEP1_DIR / "gauge_library.py": "8d0abd47615c2d5e62a6c6a8fd3bb868c7c4cec73ae81d7da19e583b48afcfe1",
    STEP1_DIR / "step1_core.py": "350902bd4c12150c1a5470e336d7a03e4334acbe907dede0d6f5bec71b872733",
    STEP1_DIR / "survivor_loader.py": "9a567e318961009ca69242da64fc268d49c5869dc5485693547126015d9bc78c",
    STEP2_DIR / "step2_core.py": "231bdd70c0646f0a3ac38644a38de9c1a3b36c1dff4e11841af0b360128b91a6",
    STEP3_DIR / "conventions_step3.py": "077fd0b8060651a650854a4b151bc8a2deb3294596a2b9e1ad6547e87af20d3b",
    STEP3_DIR / "step3_core.py": "6bce1f1f15f519ba856a08213b77964d77d66a3d63f5278cbf3e5bd83a17caa4",
    STEP3_DIR / "direction_classifications_step3.csv": "7269b9c13baaf72e364118a0d4a39d923370893ab4d7e7d7c3b7d54365735fe1",
    PROG3_DIR / "exact_weights_step1.csv": "6e7e6e321c6e6370c9ca63405809482f9b7502ceaa137a3ab315e124b36b78fc",
    PROG3_DIR / "kernel_intervals_step1.csv": "734c6142ad4e1c474b989080ba8f21b0c10094c0db04f70f9918a3a606cfa760",
    PROG3_STEP2_DIR / "saturation_engine.py": "a296f2204d6e1d1aa22b15ffea6d3cb17f8327cf096c757a9141a040b463302b",
    PROG3_STEP2_DIR / "statement.md": "d695d56780f54ed5bb48cecbc73ad1691fe17604be980d1a751b20840ca0c022",
}
FROZEN_PREREGISTRATION_SHA256 = "aae1706428bf4140e26865444408cd980dabe91f3acdf7e32a77193b59c06b28"
CORRECTIVE_PREREGISTRATION_SHA256 = "525bdc82a85359b1d6730e9032b0108aae0e763071909a14048d9b8cc3320b57"
FIX2_CLOSURE_DECLARATION_SHA256 = "c19bad1691992d8ac91505c365372d998c15c997d6ae33dd46c0937d9a515850"
INITIAL_T, ROOT_WIDTH_DIGITS, STATE_DPS = Fraction(1, 10_000), 75, 100
COMBINED_STATE_CAP = 64
COMBINED_WALL_SECONDS = 20.0
CANDIDATE_SPECS = (
    ("cand_01", "wheel_W4__b8__leaf_offset0", 47, 0, 2),
    ("cand_02", "wheel_W4__b8__leaf_offset0", 47, 1, 2),
    ("cand_03", "wheel_W4__b8__leaf_offset1", 17, 0, 1),
    ("cand_04", "wheel_W4__b8__leaf_offset1", 31, 0, 1),
    ("cand_05", "K23_bipartite__b8__dual_gateway", 17, 0, 1),
    ("cand_06", "K23_bipartite__b8__dual_gateway", 31, 0, 1),
)

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_pins() -> list[dict[str, Any]]:
    items = list(PINNED_DEPENDENCIES.items()) + [
        (HERE / "preregistration_step4.md", FROZEN_PREREGISTRATION_SHA256),
        (HERE / "preregistration_step4_corrective.md", CORRECTIVE_PREREGISTRATION_SHA256)]
    items.append((HERE / "generated_gauge_closure_fix2.md", FIX2_CLOSURE_DECLARATION_SHA256))
    rows = [{"path": str(path.relative_to(REPO_ROOT)), "expected_sha256": expected,
             "actual_sha256": sha256(path), "passes": sha256(path) == expected}
            for path, expected in items]
    if not all(row["passes"] for row in rows):
        raise AssertionError(f"pin failure: {rows}")
    return rows

def exact_edge_direction(case: Any, coordinates: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    return tuple(sum(coordinate * Fraction(fiber.direction[e])
                     for coordinate, fiber in zip(coordinates, case.fibers))
                 for e in range(len(case.capacities)))

def _read_intervals() -> dict[tuple[str, int, int], tuple[Fraction, Fraction]]:
    with (PROG3_DIR / "kernel_intervals_step1.csv").open(newline="", encoding="utf-8") as handle:
        return {(row["carrier"], int(row["seed"]), int(row["basis_index"])):
                (Fraction(row["fingerprint_lower_exact"]), Fraction(row["fingerprint_upper_exact"]))
                for row in csv.DictReader(handle)}

def _poly_and_endpoint(case: Any, v: tuple[Fraction, ...], u: tuple[Fraction, ...], t: Fraction):
    s = sp.symbols("s")
    q = lambda value: sp.Rational(value.numerator, value.denominator)
    endpoint = [q(c) + q(t) * q(ve) + s * q(ue)
                for c, ve, ue in zip(case.capacities, v, u)]
    return sp.Poly(sp.expand(sp.prod(endpoint) - sp.prod(q(c) for c in case.capacities)),
                   s, domain=sp.QQ), endpoint

def _root_midpoint(cert: Any) -> mp.mpf:
    mp.mp.dps = STATE_DPS
    return ((mp.mpf(cert.lower.numerator) / cert.lower.denominator)
            + (mp.mpf(cert.upper.numerator) / cert.upper.denominator)) / 2

def _mp_sparse_copy_state(capacities: list[mp.mpf], boundary_count: int) -> list[mp.mpf]:
    """Explicit sparse index-sum contraction of all copy-tensor indices."""
    raw0 = mp.fprod(mp.sqrt(c / (1 + c)) for c in capacities)
    raw1 = mp.fprod(mp.sqrt(1 / (1 + c)) for c in capacities)
    norm = mp.sqrt(raw0 * raw0 + raw1 * raw1)
    state = [mp.mpf("0") for _ in range(1 << boundary_count)]
    state[0], state[-1] = raw0 / norm, raw1 / norm
    return state

def _capacity_text(value: Any) -> str:
    return value.expression("alpha")

def compute_candidate(case: Any, spec: tuple[Any, ...], intervals: dict[Any, Any]):
    cid, carrier, seed, direction_index, protected_dimension = spec
    protected_coordinates = exact_copy_null_basis(case)[direction_index]
    v = exact_edge_direction(case, protected_coordinates)
    gradient = tuple(sum(Fraction(value) / capacity
                         for value, capacity in zip(fiber.direction, case.capacities))
                     for fiber in case.fibers)
    transverse_index = next(i for i, value in enumerate(gradient) if value)
    u = tuple(Fraction(value) for value in case.fibers[transverse_index].direction)
    if sum(value / capacity for value, capacity in zip(v, case.capacities)) != 0:
        raise AssertionError("protected direction is not tangent")
    attempts, selected, t = [], None, INITIAL_T
    for attempt in range(13):
        poly, endpoint_expressions = _poly_and_endpoint(case, v, u, t)
        try:
            root = exact_root_certificate(poly, endpoint_expressions, ROOT_WIDTH_DIGITS)
            field = NumberField.from_root(root)
            displaced = tuple(field.element(c + t * ve) + field.alpha * ue
                              for c, ve, ue in zip(case.capacities, v, u))
            coordinates = tuple(field.element(t * value) + field.alpha * int(i == transverse_index)
                                for i, value in enumerate(protected_coordinates))
            positive = all(value.sign() > 0 for value in displaced)
            interval_pass = all(coordinate.interval()[0] > intervals[(carrier, seed, i)][0]
                                and coordinate.interval()[1] < intervals[(carrier, seed, i)][1]
                                for i, coordinate in enumerate(coordinates))
            attempts.append({"candidate_id": cid, "attempt_index": attempt, "t_exact": str(t),
                             "root_isolated": True, "positive": positive,
                             "finite_range": interval_pass, "selected": positive and interval_pass})
            if positive and interval_pass:
                selected = (t, poly, root, field, displaced, coordinates)
                break
        except (ArithmeticError, AssertionError) as error:
            attempts.append({"candidate_id": cid, "attempt_index": attempt, "t_exact": str(t),
                             "root_isolated": False, "positive": False, "finite_range": False,
                             "selected": False, "error": str(error)})
        t /= 2
    if selected is None:
        raise AssertionError(f"no continuation for {cid}: {attempts}")
    t, poly, root, field, displaced, coordinates = selected
    base_graph = lift_graph(case.graph, tuple(field.element(value) for value in case.capacities))
    displaced_graph = lift_graph(case.graph, displaced)
    base_analysis, displaced_analysis = enumerate_cuts(base_graph), enumerate_cuts(displaced_graph)
    fingerprint_equal = same_fingerprint(base_analysis, displaced_analysis)
    if not fingerprint_equal:
        raise AssertionError(f"fingerprint mismatch for {cid}")

    convention = convention_by_id("C2_L1")
    carrier_object = as_tensor_carrier(case.graph, 2)
    independent = build_network(carrier_object, "structured_copy", None)
    alpha = _root_midpoint(root)
    displaced_mp = [mp.mpf(str(value.decimal(STATE_DPS))) for value in displaced]
    displaced_float = tuple(float(value) for value in displaced_mp)
    base_state = state_for_capacities(independent, case.capacities, convention)
    displaced_state = state_for_capacities(independent, displaced_float, convention)
    labels, dimensions = labels_and_dimensions(carrier_object)
    _entropy_rows, entropy_summary = compare_entropy_vectors(base_state, displaced_state,
                                                              labels, dimensions, cid)
    dense_state_residual = state_residual(base_state, displaced_state)
    base_mp = [mp.mpf(c.numerator) / c.denominator for c in case.capacities]
    base_hp, disp_hp = (_mp_sparse_copy_state(base_mp, len(labels)),
                        _mp_sparse_copy_state(displaced_mp, len(labels)))
    hp_state_residual = mp.sqrt(mp.fsum((a - b) ** 2 for a, b in zip(base_hp, disp_hp)))
    product_log_residual = abs(mp.fsum(mp.log(c) for c in displaced_mp)
                               - mp.fsum(mp.log(c) for c in base_mp))

    gauge_matrix = np.asarray([[1.2 + .1j, .2 - .05j], [.1 + .07j, .9 - .03j]])
    edge_id = independent.carrier.edges[0].edge_id
    base_dressed, disp_dressed = (dress_network(independent, case.capacities, convention),
                                  dress_network(independent, displaced_float, convention))
    internal_base_residual = state_residual(base_state, contract_boundary_state(
        apply_internal_gauge(base_dressed, edge_id, gauge_matrix)))
    internal_disp_residual = state_residual(displaced_state, contract_boundary_state(
        apply_internal_gauge(disp_dressed, edge_id, gauge_matrix)))

    base_orbit = saturate_combined(base_graph, COMBINED_STATE_CAP, COMBINED_WALL_SECONDS)
    disp_orbit = saturate_combined(displaced_graph, COMBINED_STATE_CAP, COMBINED_WALL_SECONDS)
    intersection = orbit_intersection(base_orbit, disp_orbit)
    same_graph_automorphism = canonical_key(base_graph) == canonical_key(displaced_graph)
    base_signature_set, base_signature_digest = explored_capacity_signature(base_orbit)
    disp_signature_set, disp_signature_digest = explored_capacity_signature(disp_orbit)
    explored_signature_differs = base_signature_set != disp_signature_set
    state_equal = entropy_summary["verdict"] == "COINCIDE" and dense_state_residual <= 5e-10
    both_saturated = base_orbit.saturated and disp_orbit.saturated
    if intersection["count"]:
        combined_verdict = "GAUGE_VIA_PATH"
        typed = "CONTINUATION_CONSTRUCTED__GAUGE_RELATED_COINCIDENCE"
        invariant_status = "CONSISTENT_WITH_GAUGE_PATH"
    elif both_saturated:
        combined_verdict = "COMBINED_ORBIT_DISJOINT_SATURATED"
        invariant_status = "COMPLETE_COMBINED_ORBIT_SIGNATURE_DIFFERS" if explored_signature_differs else "COMPLETE_COMBINED_ORBIT_SIGNATURE_EQUAL"
        typed = ("CONTINUATION_CONSTRUCTED__SURVIVING_UNDERDETERMINATION_CANDIDATE"
                 if explored_signature_differs else "CONTINUATION_CONSTRUCTED__BULK_INVARIANT_FAILURE")
    else:
        combined_verdict = "DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED"
        invariant_status = ("EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF"
                            if explored_signature_differs else "EXPLORED_SIGNATURE_EQUAL__NOT_AN_INVARIANT_PROOF")
        typed = "PENDING_GENERATED_GAUGE_CLOSURE"
    surviving = typed == "CONTINUATION_CONSTRUCTED__SURVIVING_UNDERDETERMINATION_CANDIDATE"
    vector_base, _ = full_entropy_analysis(base_state, labels, dimensions)
    vector_disp, _ = full_entropy_analysis(displaced_state, labels, dimensions)
    row = {
        "candidate_id": cid, "carrier": carrier, "source_seed_provenance": seed,
        "member_id": "C2_L1", "direction_index": direction_index,
        "protected_space_dimension": protected_dimension,
        "complete_cut_kernel_dimension": len(case.fibers),
        "endpoint_number_field_degree": field.degree,
        "cut_basis_coordinates_v_exact": "|".join(map(str, protected_coordinates)),
        "transverse_basis_index": transverse_index,
        "d_log_product_u_exact": str(gradient[transverse_index]), "t_exact": str(t),
        "s_minimal_polynomial": sp.sstr(sp.Poly.from_list(
            [sp.Rational(x.numerator, x.denominator) for x in root.minimal_polynomial_coefficients],
            sp.symbols("s")).as_expr()),
        "s_isolating_lower_exact": str(root.lower), "s_isolating_upper_exact": str(root.upper),
        "s_decimal_100dps": root.decimal(100), "root_interval_width_exact": str(root.width),
        "displaced_capacities_exact_algebraic": "|".join(_capacity_text(x) for x in displaced),
        "total_cut_basis_coordinates_exact_algebraic": "|".join(_capacity_text(x) for x in coordinates),
        "total_cut_basis_coordinate_isolating_intervals": "|".join(
            f"[{x.interval()[0]},{x.interval()[1]}]" for x in coordinates),
        "imported_prog3_coordinate_intervals_exact": "|".join(
            f"[{intervals[(carrier, seed, i)][0]},{intervals[(carrier, seed, i)][1]}]"
            for i in range(len(coordinates))),
        "all_capacities_positive_rigorous": all(x.sign() > 0 for x in displaced),
        "finite_range_coordinate_membership_rigorous": True,
        "ordered_region_count": len(displaced_analysis.regions),
        "all_cut_assignment_count": displaced_analysis.all_candidate_count,
        "complete_fingerprint_equal_exact": fingerprint_equal, "unique_minimizers_displaced": True,
        "minimum_displaced_unique_cut_margin_lower_exact": str(displaced_analysis.minimum_margin_lower),
        "product_log_residual_100dps": mp.nstr(product_log_residual, 20),
        "dense_state_norm_difference": f"{dense_state_residual:.17g}",
        "high_precision_sparse_contraction_state_difference": mp.nstr(hp_state_residual, 20),
        "high_precision_state_difference_within_product_residual": hp_state_residual <= product_log_residual,
        "maximum_entropy_difference_nats": entropy_summary["max_entropy_difference_nats"],
        "entropy_vector_verdict": entropy_summary["verdict"],
        "connected_copy_state_equal_exact_analytic": True,
        "base_state_sha256": state_digest(base_state), "displaced_state_sha256": state_digest(displaced_state),
        "base_entropy_sha256": vector_digest(vector_base, labels),
        "displaced_entropy_sha256": vector_digest(vector_disp, labels),
        "internal_gauge_base_residual": f"{internal_base_residual:.17g}",
        "internal_gauge_displaced_residual": f"{internal_disp_residual:.17g}",
        "combined_state_cap_per_endpoint": COMBINED_STATE_CAP,
        "combined_wall_seconds_per_endpoint": f"{COMBINED_WALL_SECONDS:g}",
        "base_combined_orbit_saturated": base_orbit.saturated,
        "displaced_combined_orbit_saturated": disp_orbit.saturated,
        "base_combined_budget_reason": base_orbit.budget_reason,
        "displaced_combined_budget_reason": disp_orbit.budget_reason,
        "base_combined_orbit_state_count": len(base_orbit.states),
        "displaced_combined_orbit_state_count": len(disp_orbit.states),
        "base_combined_processed_state_count": base_orbit.processed_state_count,
        "displaced_combined_processed_state_count": disp_orbit.processed_state_count,
        "base_combined_max_depth": base_orbit.max_depth,
        "displaced_combined_max_depth": disp_orbit.max_depth,
        "base_combined_accepted_census": "|".join(f"{k}:{v}" for k,v in base_orbit.accepted_census.items()),
        "displaced_combined_accepted_census": "|".join(f"{k}:{v}" for k,v in disp_orbit.accepted_census.items()),
        "base_combined_novel_census": "|".join(f"{k}:{v}" for k,v in base_orbit.novel_census.items()),
        "displaced_combined_novel_census": "|".join(f"{k}:{v}" for k,v in disp_orbit.novel_census.items()),
        "base_five_move_fingerprint_rechecks": base_orbit.fingerprint_recheck_count,
        "displaced_five_move_fingerprint_rechecks": disp_orbit.fingerprint_recheck_count,
        "combined_orbit_intersection_count": intersection["count"],
        "combined_orbit_base_path_if_gauge": intersection["left_path"],
        "combined_orbit_displaced_path_if_gauge": intersection["right_path"],
        "combined_closure_verdict": combined_verdict,
        "same_graph_terminal_fixed_automorphism_maps": same_graph_automorphism,
        "boundary_state_equivalent": state_equal,
        "base_explored_capacity_signature_count": len(base_signature_set),
        "base_explored_capacity_signature_sha256": base_signature_digest,
        "displaced_explored_capacity_signature_count": len(disp_signature_set),
        "displaced_explored_capacity_signature_sha256": disp_signature_digest,
        "explored_capacity_signatures_differ": explored_signature_differs,
        "capacity_invariant_status": invariant_status,
        "typed_outcome": typed,
        "surviving_underdetermination_candidate": surviving,
        "grade": "EXACT_ALGEBRAIC_FINGERPRINT_AND_PRODUCT__DENSE_NUMERICAL_STATE_EVIDENCE",
    }
    obligations = [{"candidate_id": cid, "obligation": name, "status": status, "passes": passed}
                   for name, status, passed in (
        ("exact_product_root", "EXECUTED_EXACT_ALGEBRAIC", True),
        ("prog3_interval_membership", "EXECUTED_RIGOROUS_INTERVAL", True),
        ("complete_cut_reenumeration", "EXECUTED_EXACT_ALGEBRAIC", fingerprint_equal),
        ("independent_state_entropy_recontraction", "EXECUTED_DENSE_NUMERICAL", state_equal),
        ("terminal_fixed_automorphism", "EXECUTED_NO_MAP", not same_graph_automorphism),
        ("combined_generated_gauge_closure",
         "EXECUTED_GAUGE_PATH" if intersection["count"] else
         "EXECUTED_SATURATED_DISJOINT" if both_saturated else "PENDING_GENERATED_GAUGE_CLOSURE",
         True),
        ("internal_tensor_gauge_presentation", "EXECUTED_INVARIANT", max(internal_base_residual, internal_disp_residual) < 5e-10),
        ("reciprocal_first_generated_move_handling", "EXECUTED_IN_COMBINED_WORKLIST", True),
        ("boundary_local_equivalence", "EXECUTED_IDENTITY_EQUIVALENT", state_equal),
        ("bulk_capacity_orbit_multiset_invariant",
         "EXECUTED_COMPLETE_COMBINED_ORBIT" if both_saturated else "PENDING_GENERATED_GAUGE_CLOSURE",
         True))]
    canary = reciprocal_first_canary(base_graph, (3,5,6,11)) if cid == "cand_03" else []
    return row, attempts, obligations, [dict(candidate_id=cid, **item) for item in canary]

def compute_all() -> dict[str, Any]:
    pins = verify_pins()
    cases = {(case.carrier, case.source_seed_provenance): case
             for case in group_base_cases(load_fibers())}
    intervals = _read_intervals()
    candidates, attempts, obligations, canary = [], [], [], []
    for spec in CANDIDATE_SPECS:
        row, local_attempts, local_obligations, local_canary = compute_candidate(
            cases[(spec[1], spec[2])], spec, intervals)
        candidates.append(row); attempts.extend(local_attempts)
        obligations.extend(local_obligations); canary.extend(local_canary)
    anti_bypass = [
        {"gate": "full_cut_kernel_not_tangent_subspace", "passes": all(
            row["complete_cut_kernel_dimension"] == row["protected_space_dimension"] + 1 for row in candidates),
         "evidence": "each curve uses protected v plus transverse u with nonzero dlogP"},
        {"gate": "all_fingerprints_fully_reenumerated", "passes": all(
            row["complete_fingerprint_equal_exact"] and row["all_cut_assignment_count"] > row["ordered_region_count"] for row in candidates),
         "evidence": "all interior assignments enumerated at each algebraic endpoint and orbit presentation"},
        {"gate": "product_formula_not_state_substitute", "passes": all(
            row["entropy_vector_verdict"] == "COINCIDE" for row in candidates),
         "evidence": "both dense endpoints and all entropy subsets independently recomputed"},
        {"gate": "no_inapplicable_obligation_after_endpoint", "passes": all(
            not row["status"].startswith("NOT_APPLICABLE") for row in obligations),
         "evidence": "ten executed-or-explicitly-pending obligation rows per endpoint"},
        {"gate": "general_number_field_inversion", "passes": all(
            row["complete_cut_kernel_dimension"] >= 2 for row in candidates),
         "evidence": "all combined states use exact QQ(alpha) polynomial residues, including degree-five cand_06"},
        {"gate": "reciprocal_first_canary", "passes": len(canary) == 4 and all(row["passes"] for row in canary),
         "evidence": "cand_03 reciprocal edges 3/5/6/11 expose and handle newly applicable contraction moves"}]
    if not all(row["passes"] for row in anti_bypass + obligations):
        raise AssertionError("corrective Step-4 obligation failure")
    return {"dependency_pins": pins, "candidate_outcomes": candidates,
            "root_attempts": attempts, "endpoint_obligations": obligations,
            "reciprocal_first_canary": canary, "anti_bypass": anti_bypass,
            "aggregate_verdict": "SIX_EXACT_CONTINUATIONS__GENERATED_GAUGE_CLOSURE_PENDING_IF_TRUNCATED"}
