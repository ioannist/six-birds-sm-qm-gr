#!/usr/bin/env python3
"""Verification-closure computations for S3-REPAIR-1b."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Iterable, Sequence

import s3_construction as v1
from exact_lie import (
    F, GQ, Matrix, commutator, dagger, diagonal, flatten, format_fraction, is_zero,
    madd, matmul, matrix, matrix_key, matrix_span_rank, mscale, msub, nullspace,
    primitive_integer, rational_matrix_rank, smith_invariants, su_hermitian_basis,
    trace, unit,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def linear_combination(coefficients: Sequence[Fraction], matrices: Sequence[Matrix]) -> Matrix:
    result = mscale(0, matrices[0])
    for coefficient, source in zip(coefficients, matrices):
        result = madd(result, mscale(coefficient, source))
    return result


def proportional(a: Matrix, b: Matrix) -> tuple[bool, GQ | None]:
    av, bv = flatten(a), flatten(b)
    pivot = next((index for index, value in enumerate(bv) if value), None)
    if pivot is None:
        return is_zero(a), None
    scale = av[pivot] / bv[pivot]
    return all(left == scale * right for left, right in zip(av, bv)), scale


def full_commutant(su_basis: Sequence[tuple[str, Matrix]], generators: Sequence[Matrix]) -> dict[str, Any]:
    """Solve [sum_a c_a T_a,g]=0 over all traceless Hermitian directions."""
    matrices = [source for _, source in su_basis]
    equations: list[list[Fraction]] = []
    for generator in generators:
        columns = [flatten(commutator(source, generator)) for source in matrices]
        for entry in range(len(columns[0])):
            real_row = [column[entry].re for column in columns]
            imag_row = [column[entry].im for column in columns]
            if any(real_row):
                equations.append(real_row)
            if any(imag_row):
                equations.append(imag_row)
    rank = rational_matrix_rank(equations)
    kernel = nullspace(equations, ncols=len(matrices))
    _assert(rank == 23 and len(kernel) == 1, f"full commutant rank/nullity is {rank}/{len(kernel)}")
    centralizer = linear_combination(kernel[0], matrices)
    _assert(not is_zero(centralizer), "full commutant returned the zero direction")
    _assert(all(is_zero(commutator(centralizer, generator)) for generator in generators),
            "full commutant vector does not commute")
    diagonal_values = []
    off_diagonal_zero = True
    for i in range(len(centralizer)):
        _assert(centralizer[i][i].im == 0, "centralizer diagonal is not real")
        diagonal_values.append(centralizer[i][i].re)
        for j in range(len(centralizer)):
            if i != j and centralizer[i][j]:
                off_diagonal_zero = False
    primitive = primitive_integer(diagonal_values, preferred_index=3) if off_diagonal_zero else None
    return {
        "equation_count": len(equations), "coefficient_count": len(matrices), "rank": rank,
        "nullity": len(kernel), "kernel_coefficients": kernel[0], "centralizer_matrix": centralizer,
        "off_diagonal_zero": off_diagonal_zero, "primitive_diagonal": primitive,
    }


def commutator_eigenvalue(h: Matrix, root: Matrix) -> Fraction:
    result = commutator(h, root)
    root_flat, result_flat = flatten(root), flatten(result)
    pivot = next(index for index, value in enumerate(root_flat) if value)
    eigenvalue = result_flat[pivot] / root_flat[pivot]
    _assert(eigenvalue.im == 0, "commutator eigenvalue is not real")
    _assert(all(value == eigenvalue * basis for value, basis in zip(result_flat, root_flat)),
            "matrix is not an adjoint eigenvector")
    return eigenvalue.re


def diagonal_vector(source: Matrix) -> tuple[Fraction, ...]:
    values = []
    for i in range(len(source)):
        _assert(source[i][i].im == 0, "Cartan has an imaginary diagonal entry")
        values.append(source[i][i].re)
        for j in range(len(source)):
            if i != j:
                _assert(not source[i][j], "Cartan is not diagonal in the extraction frame")
    _assert(sum(values) == 0, "extracted Cartan is not traceless")
    return tuple(values)


def cocharacter_coordinates(source: Matrix) -> tuple[int, ...]:
    values = diagonal_vector(source)
    _assert(all(value.denominator == 1 for value in values), "coroot is not integral")
    # For sum_i v_i=0, coordinates in e0-e4,...,e3-e4 are v0,...,v3.
    return tuple(int(value) for value in values[:-1])


def extract_coroot_columns(embedded: Sequence[tuple[str, Matrix]], frame: Matrix | None = None) -> list[dict[str, Any]]:
    cartans = {name: source for name, source in embedded if "_D_" in name}
    required = {"B0_D_1", "B0_D_2", "B1_D_1"}
    _assert(required <= set(cartans), f"missing constructed Cartans: {required-set(cartans)}")

    def pullback(source: Matrix) -> Matrix:
        return matmul(matmul(dagger(frame), source), frame) if frame is not None else source

    d1 = pullback(cartans["B0_D_1"])
    d2 = pullback(cartans["B0_D_2"])
    weak = pullback(cartans["B1_D_1"])
    extracted = [
        ("su3_simple_01", "B0_D_1", d1),
        ("su3_simple_12", "(B0_D_2-B0_D_1)/2", mscale(Fraction(1, 2), msub(d2, d1))),
        ("su2_simple_34", "B1_D_1", weak),
    ]
    return [{"coroot_id": name, "extraction": source, "matrix": root,
             "coordinates": cocharacter_coordinates(root)} for name, source, root in extracted]


def f48_from_extracted_columns(coroot_rows: list[dict[str, Any]], centralizer_matrix: Matrix) -> dict[str, Any]:
    columns = [tuple(row["coordinates"]) for row in coroot_rows]
    presentation = [list(row) for row in zip(*columns)]
    rank, invariants = smith_invariants(presentation)
    annihilator_basis = nullspace([[F(value) for value in column] for column in columns])
    _assert(len(annihilator_basis) == 1, "extracted coroots do not have a rank-one annihilator")
    annihilator = primitive_integer(annihilator_basis[0], preferred_index=0)
    centralizer_values = diagonal_vector(centralizer_matrix)
    centralizer_primitive = primitive_integer(centralizer_values, preferred_index=3)
    centralizer_coordinates = centralizer_primitive[:-1]
    index = abs(sum(left * right for left, right in zip(annihilator, centralizer_coordinates)))
    cocharacter_rank = len(presentation)
    free_rank = cocharacter_rank - rank

    # Explicit topology inputs to the exact-sequence inference.
    h_connected = True
    pi1_su5_rank = 0
    pi2_su5_rank = 0
    kernel_free_rank = free_rank if h_connected and pi1_su5_rank == 0 else None
    pi2_result = "Z" if kernel_free_rank == 1 and pi2_su5_rank == 0 else "UNRESOLVED"
    return {
        "columns": columns, "derived_coroot_rank": rank, "smith_invariants": invariants,
        "annihilator": annihilator, "free_rank_pi1_h": free_rank,
        "centralizer_primitive": centralizer_primitive, "central_u1_loop_index": index,
        "H_connected": h_connected, "pi1_SU5": "0", "pi2_SU5": "0",
        "kernel_free_rank": kernel_free_rank, "pi2_SU5_over_H": pi2_result,
    }


def validate_f48(result: dict[str, Any]) -> None:
    _assert(result["derived_coroot_rank"] == 3, "F48 derived-coroot rank changed")
    _assert(result["smith_invariants"] == (1, 1, 1), "F48 Smith invariants changed")
    _assert(result["free_rank_pi1_h"] == 1, "F48 free rank changed")
    _assert(result["central_u1_loop_index"] == 6, "F48 centralizer-loop index changed")
    _assert(result["pi2_SU5_over_H"] == "Z", "F48 pi2 conclusion changed")


def construct_su4_slice(su5: dict, slice_extra: Matrix | None = None) -> dict[str, Any]:
    embedded4, blocks4 = v1._block_embedded_basis([3, 1])
    _, primitive4 = v1.diagonal_centralizer([source for _, source in embedded4], 4)
    scale4 = Fraction(1, primitive4[-1])
    u1_4 = diagonal([F(value) * scale4 for value in primitive4])
    roots4 = []
    mapped = []
    scale_values = set()
    for color in blocks4[0]:
        for source, target in ((color, 3), (3, color)):
            root4 = unit(4, source, target)
            root5 = unit(5, source, target)
            q4 = commutator_eigenvalue(u1_4, root4)
            q5 = commutator_eigenvalue(su5["y"], root5)
            ratio = q5 / q4
            scale_values.add(ratio)
            roots4.append(root4)
            mapped.append({
                "su4_root": f"E_{source}{target}", "su5_root": f"E_{source}{target}",
                "su4_charge": q4, "su5_charge": q5, "charge_rescale": ratio,
                "su4_matrix": root4, "su5_matrix": root5,
            })
    _assert(len(mapped) == 6 and scale_values == {Fraction(5, 8)},
            "SU4 fixed-slice map or computed charge rescale changed")

    slice_matrices = [row["su5_matrix"] for row in mapped]
    if slice_extra is not None:
        slice_matrices.append(slice_extra)
    weak_operator = unit(5, 3, 4)
    source = unit(5, 0, 3)
    target = unit(5, 0, 4)
    witness = commutator(weak_operator, source)
    target_relation, target_coefficient = proportional(witness, target)
    outside_slice = matrix_span_rank(slice_matrices + [witness]) > matrix_span_rank(slice_matrices)
    verdict = (
        "ANALOGUE_AS_FIXED_WEAK_INDEX_SLICE_NOT_IDENTITY"
        if len(mapped) == 6 and scale_values == {Fraction(5, 8)} and target_relation and outside_slice
        else "ANALOGUE_VERDICT_FAILED"
    )
    return {
        "mapped_roots": mapped, "charge_rescale": next(iter(scale_values)),
        "weak_operator": "E_34", "source_slice_element": "E_03",
        "commutator_target": "E_04", "commutator_coefficient": target_coefficient.re,
        "target_relation_exact": target_relation, "target_outside_slice": outside_slice,
        "verdict": verdict,
    }


def validate_su4_slice(result: dict[str, Any]) -> None:
    _assert(len(result["mapped_roots"]) == 6, "SU4 slice does not map all six roots")
    _assert(result["charge_rescale"] == Fraction(5, 8), "SU4 charge rescale changed")
    _assert(result["target_relation_exact"] and result["target_outside_slice"],
            "SU2 action no longer proves fixed-slice non-invariance")
    _assert(result["verdict"] == "ANALOGUE_AS_FIXED_WEAK_INDEX_SLICE_NOT_IDENTITY",
            "SU4 analogue verdict changed")


def rational_givens(n: int, left: int, right: int) -> Matrix:
    rows = [[GQ(int(i == j)) for j in range(n)] for i in range(n)]
    rows[left][left] = GQ(Fraction(3, 5))
    rows[right][right] = GQ(Fraction(3, 5))
    rows[left][right] = GQ(Fraction(4, 5))
    rows[right][left] = GQ(Fraction(-4, 5))
    return matrix(rows)


def generic_so5() -> Matrix:
    result = rational_givens(5, 0, 1)
    for left, right in ((1, 2), (2, 3), (3, 4), (0, 4), (1, 3)):
        result = matmul(rational_givens(5, left, right), result)
    _assert(matmul(result, dagger(result)) == diagonal([1] * 5), "generic SO(5) matrix is not unitary")
    return result


def conjugate_matrix(frame: Matrix, source: Matrix) -> Matrix:
    return matmul(matmul(frame, source), dagger(frame))


def exterior_square_group_action(frame: Matrix) -> Matrix:
    """Construct the group action on wedge^2 directly from a fundamental frame."""
    from itertools import combinations

    pairs = list(combinations(range(len(frame)), 2))
    rows = [[GQ() for _ in pairs] for _ in pairs]
    for target, (a, b) in enumerate(pairs):
        for source, (i, j) in enumerate(pairs):
            rows[target][source] = frame[a][i] * frame[b][j] - frame[a][j] * frame[b][i]
    return matrix(rows)


def conjugated_embedding_invariance(su5: dict, fermions: dict[str, Any],
                                    full: dict[str, Any], f48: dict[str, Any]) -> dict[str, Any]:
    frame = generic_so5()
    embedded = [(name, conjugate_matrix(frame, source)) for name, source in su5["embedded"]]
    conjugated_full = full_commutant(su5["basis"], [source for _, source in embedded])
    expected_centralizer = conjugate_matrix(frame, full["centralizer_matrix"])
    centralizer_equivariant, _ = proportional(conjugated_full["centralizer_matrix"], expected_centralizer)

    conjugated_y = conjugate_matrix(frame, su5["y"])
    original_roots = [unit(5, source, target) for source in su5["blocks"][0]
                      for target in su5["blocks"][1]]
    original_roots += [unit(5, target, source) for source in su5["blocks"][0]
                       for target in su5["blocks"][1]]
    original_charges = [commutator_eigenvalue(su5["y"], root) for root in original_roots]
    conjugated_charges = [commutator_eigenvalue(conjugated_y, conjugate_matrix(frame, root))
                           for root in original_roots]
    extracted = extract_coroot_columns(embedded, frame=frame)
    pulled_back_centralizer = conjugate_matrix(dagger(frame), conjugated_full["centralizer_matrix"])
    conjugated_f48 = f48_from_extracted_columns(extracted, pulled_back_centralizer)
    trace_norm_invariant = trace(matmul(conjugated_y, conjugated_y)) == trace(matmul(su5["y"], su5["y"]))

    # Check the full 5bar+10 representation functor, then use invariant traces
    # and the transformed baryon operator to cover the ratio and F27 outputs.
    rep_frame = v1._block_diag(frame, exterior_square_group_action(frame))
    rep_action = fermions["rep_action"]
    rep_equivariant = all(
        rep_action(conjugate_matrix(frame, source))
        == conjugate_matrix(rep_frame, rep_action(source))
        for _, source in su5["basis"]
    )
    embedded_by_name = dict(su5["embedded"])
    t3 = mscale(Fraction(1, 2), embedded_by_name["B1_D_1"])
    conjugated_t3 = conjugate_matrix(frame, t3)
    q_rep = madd(rep_action(t3), rep_action(su5["y"]))
    conjugated_q_rep = madd(rep_action(conjugated_t3), rep_action(conjugated_y))
    ratio_traces_invariant = (
        trace(matmul(rep_action(t3), rep_action(t3)))
        == trace(matmul(rep_action(conjugated_t3), rep_action(conjugated_t3)))
        and trace(matmul(q_rep, q_rep))
        == trace(matmul(conjugated_q_rep, conjugated_q_rep))
    )
    baryon = diagonal([fermions["component_info"][index]["baryon_number"] for index in range(15)])
    conjugated_baryon = conjugate_matrix(rep_frame, baryon)
    f27_invariant = True
    for _, source in su5["coset_hermitian"]:
        original_action = rep_action(source)
        conjugated_action = rep_action(conjugate_matrix(frame, source))
        original_changes_b = not is_zero(commutator(baryon, original_action))
        conjugated_changes_b = not is_zero(commutator(conjugated_baryon, conjugated_action))
        f27_invariant &= original_changes_b and conjugated_changes_b

    invariant = (
        conjugated_full["rank"] == full["rank"] == 23
        and conjugated_full["nullity"] == full["nullity"] == 1
        and centralizer_equivariant
        and trace_norm_invariant
        and rep_equivariant
        and ratio_traces_invariant
        and f27_invariant
        and conjugated_charges == original_charges
        and conjugated_f48["columns"] == f48["columns"]
        and conjugated_f48["central_u1_loop_index"] == f48["central_u1_loop_index"]
    )
    _assert(invariant, "generic conjugated embedding changed a derived invariant")
    return {"frame": "six rational SO(5) Givens rotations", "commutant_rank": 23,
            "commutant_nullity": 1, "centralizer_equivariant": centralizer_equivariant,
            "trace_norm_invariant": trace_norm_invariant,
            "coset_charges_invariant": conjugated_charges == original_charges,
            "fermion_representation_equivariant": rep_equivariant,
            "ratio_traces_invariant": ratio_traces_invariant,
            "F27_delta_B_invariant": f27_invariant,
            "extracted_lattice_invariant": conjugated_f48["columns"] == f48["columns"],
            "result": "PASS"}


def pati_salam_control() -> dict[str, Any]:
    # Derive B-L from the constructed SU4->SU3 centralizer direction.
    embedded4, _ = v1._block_embedded_basis([3, 1])
    _, primitive4 = v1.diagonal_centralizer([source for _, source in embedded4], 4)
    # Orient and scale by the declared physical embedding condition B-L(lepton)=-1.
    bl_scale = Fraction(-1, primitive4[3])
    bl_fund = tuple(F(value) * bl_scale for value in primitive4)
    bl_antifund = tuple(-value for value in bl_fund)
    t3_weights = (Fraction(1, 2), Fraction(-1, 2))
    # Require one colorless right-doublet state to be neutral: T3_R+c(B-L)=0.
    neutral_t3r = Fraction(-1, 2)
    bl_right_lepton = bl_antifund[3]
    bl_coefficient = -neutral_t3r / bl_right_lepton
    _assert(bl_coefficient == Fraction(1, 2), "Pati-Salam hypercharge coefficient changed")

    states = []
    for su4_index, bl in enumerate(bl_fund):
        for weak_index, t3_left in enumerate(t3_weights):
            y = bl_coefficient * bl
            states.append({"parent_rep": "(4,2,1)", "su4_weight": su4_index,
                           "doublet_weight": weak_index, "B_minus_L": bl, "T3_L": t3_left,
                           "T3_R": Fraction(0), "Y": y, "Q": t3_left + y})
    for su4_index, bl in enumerate(bl_antifund):
        for right_index, t3_right in enumerate(t3_weights):
            y = t3_right + bl_coefficient * bl
            states.append({"parent_rep": "(4bar,1,2)", "su4_weight": su4_index,
                           "doublet_weight": right_index, "B_minus_L": bl, "T3_L": Fraction(0),
                           "T3_R": t3_right, "Y": y, "Q": y})
    tr_t3_sq = sum(row["T3_L"] ** 2 for row in states)
    tr_y_sq = sum(row["Y"] ** 2 for row in states)
    tr_q_sq = sum(row["Q"] ** 2 for row in states)
    ratio = tr_t3_sq / tr_q_sq
    _assert(len(states) == 16 and ratio == Fraction(3, 8), "Pati-Salam control trace changed")
    return {
        "states": states, "B_minus_L_fund": bl_fund, "hypercharge_formula": "Y=T3_R+(B-L)/2",
        "tr_T3L_squared": tr_t3_sq, "tr_Y_squared": tr_y_sq, "tr_Q_squared": tr_q_sq,
        "sin2_trace_ratio": ratio, "semisimple_parent": "SU(4)xSU(2)_LxSU(2)_R",
        "well_posed_trace_control": True,
        "physical_coupling_caveat": "product factors have independent couplings unless equality is separately imposed",
    }


def product_parent_attempts(pati: dict[str, Any], fermions: dict[str, Any]) -> list[dict[str, Any]]:
    component_info = fermions["component_info"]
    tr_t3_squared = sum(row["t3"] ** 2 for row in component_info.values())
    tr_y_squared = sum(row["hypercharge"] ** 2 for row in component_info.values())
    tr_t3_y = sum(row["t3"] * row["hypercharge"] for row in component_info.values())
    reductive_scale = Fraction(2)
    reductive_q_squared = (
        tr_t3_squared + 2 * reductive_scale * tr_t3_y
        + reductive_scale ** 2 * tr_y_squared
    )
    reductive_ratio = tr_t3_squared / reductive_q_squared
    _assert(reductive_ratio == Fraction(3, 23), "scale-two reductive trace changed")
    return [
        {"control_id": "pati_salam_semisimple", "parent": pati["semisimple_parent"],
         "semisimple": True, "embedding": pati["hypercharge_formula"],
         "representation": "(4,2,1)+(4bar,1,2)", "trace_state_count": len(pati["states"]),
         "computed_ratio": format_fraction(pati["sin2_trace_ratio"]), "well_posed": True,
         "trace_inputs": "TrT3^2=2;TrY^2=10/3;TrT3Y=0",
         "outcome": "BUILT_RATIO_3/8_NOT_3/23",
         "diagnosis": pati["physical_coupling_caveat"]},
        {"control_id": "direct_sm_reductive_scale_free", "parent": "SU(3)xSU(2)xU(1)",
         "semisimple": False, "embedding": "Y_lambda=lambda*Y_SM",
         "representation": "derived SM generation", "trace_state_count": 15,
         "computed_ratio": format_fraction(reductive_ratio), "well_posed": False,
         "trace_inputs": (
             f"lambda={format_fraction(reductive_scale)};"
             f"TrT3^2={format_fraction(tr_t3_squared)};"
             f"TrY^2={format_fraction(tr_y_squared)};"
             f"TrT3Y={format_fraction(tr_t3_y)}"
         ),
         "outcome": "3/23_REQUIRES_ARBITRARY_SCALE_INSERTION",
         "diagnosis": "the U(1) normalization is free and the parent is reductive, not semisimple"},
    ]


def validate_f27_rows(rows: list[dict[str, Any]]) -> None:
    _assert(len(rows) == 12, "F27 coset action is incomplete")
    _assert(all(row["mediates_delta_b"] for row in rows), "F27 contains an action with no Delta-B transition")


def mutation_suite(su5: dict, fermions: dict, full: dict[str, Any], f48: dict[str, Any],
                   coroot_rows: list[dict[str, Any]], su4: dict[str, Any], f27: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [{"mutation": row["mutation"], "expected": row["expected"], "result": row["result"],
             "evidence": row["rejection"]} for row in v1.mutation_tests(su5, fermions)]

    invariance = conjugated_embedding_invariance(su5, fermions, full, f48)
    rows.append({"mutation": "generic_SO5_conjugated_embedding", "expected": "all invariants unchanged",
                 "result": invariance["result"],
                 "evidence": "commutant/coset/fermion ratios/F27/F48 invariant"})

    def expect_rejected(name: str, callback: Any) -> None:
        try:
            callback()
        except AssertionError as exc:
            rows.append({"mutation": name, "expected": "rejected", "result": "PASS", "evidence": str(exc)})
        else:
            rows.append({"mutation": name, "expected": "rejected", "result": "FAIL",
                         "evidence": "mutation was accepted"})

    def corrupt_coroot() -> None:
        corrupted = [dict(row) for row in coroot_rows]
        corrupted[1]["matrix"] = mscale(2, corrupted[1]["matrix"])
        corrupted[1]["coordinates"] = cocharacter_coordinates(corrupted[1]["matrix"])
        validate_f48(f48_from_extracted_columns(corrupted, full["centralizer_matrix"]))

    def alter_coset_action() -> None:
        mutated = dict(su5)
        mutated["coset_hermitian"] = list(su5["coset_hermitian"])
        name, source = mutated["coset_hermitian"][0]
        mutated["coset_hermitian"][0] = (name, mscale(0, source))
        validate_f27_rows(v1.compute_f27(mutated, fermions))

    def mutate_slice() -> None:
        validate_su4_slice(construct_su4_slice(su5, slice_extra=unit(5, 0, 4)))

    expect_rejected("corrupt_extracted_coroot", corrupt_coroot)
    expect_rejected("zero_one_coset_action", alter_coset_action)
    expect_rejected("enlarge_SU4_fixed_slice_with_E04", mutate_slice)
    _assert(all(row["result"] == "PASS" for row in rows), "a verification mutation escaped")
    return rows


def claim_ledger(full: dict[str, Any], f48: dict[str, Any], su4: dict[str, Any],
                 pati: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {"claim": "SU5 hypercharge direction", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": f"full commutant rank={full['rank']} nullity={full['nullity']}; primitive {full['primitive_diagonal']}",
         "residual_assumption_or_convention": "regular 3+2 embedding; overall sign and charge unit"},
        {"claim": "k_Y and weak-angle ratio", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": "k_Y=5/3; sin2(theta_W)=3/8",
         "residual_assumption_or_convention": "weak-pair unit; Q=T3+Y"},
        {"claim": "SU5 X/Y coset", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": "12 roots: (3,2,-5/6)+(3bar,2,5/6)",
         "residual_assumption_or_convention": "regular block embedding"},
        {"claim": "step41 six-generator identity", "status": "REFUTED-BY-CONSTRUCTION",
         "computed_result": "six-root slice is not SU2-invariant and is not the 12-root X/Y coset",
         "residual_assumption_or_convention": "none within constructed embeddings"},
        {"claim": "step41 fixed-slice analogue relation", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": f"6/6 roots mapped; charge rescale={format_fraction(su4['charge_rescale'])}; [E_34,E_03]=-E_04 outside slice",
         "residual_assumption_or_convention": "chosen fixed weak index"},
        {"claim": "F27 baryon descent", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": "12/12 coset actions change B; SM subalgebra preserves B",
         "residual_assumption_or_convention": "left-chiral baryon assignment from color type"},
        {"claim": "F48 monopole", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": f"extracted coroot rank=3; free rank={f48['free_rank_pi1_h']}; index={f48['central_u1_loop_index']}; pi2={f48['pi2_SU5_over_H']}",
         "residual_assumption_or_convention": "H connected; pi1(SU5)=0; pi2(SU5)=0"},
        {"claim": "product parent yields 3/23", "status": "REMAINING-IMPORT",
         "computed_result": f"constructed Pati-Salam trace ratio={format_fraction(pati['sin2_trace_ratio'])}; 3/23 only from arbitrary Y->2Y",
         "residual_assumption_or_convention": "no well-posed 3/23 parent found; exotic product embeddings not exhausted"},
        {"claim": "unique parent", "status": "REMAINING-IMPORT",
         "computed_result": "SU(5) selected only in bounded regular-SU diagnostic",
         "residual_assumption_or_convention": "SO(10), E6, and arbitrary embeddings not exhausted"},
    ]


def run_v2() -> dict[str, Any]:
    base = v1.run_all()
    su5 = v1.construct_su5()
    full = full_commutant(su5["basis"], [source for _, source in su5["embedded"]])
    _assert(full["primitive_diagonal"] == (-2, -2, -2, 3, 3), "full commutant direction changed")
    coroot_rows = extract_coroot_columns(su5["embedded"])
    f48 = f48_from_extracted_columns(coroot_rows, full["centralizer_matrix"])
    validate_f48(f48)
    su4 = construct_su4_slice(su5)
    validate_su4_slice(su4)
    fermions = v1.fermion_decomposition(su5)
    f27 = v1.compute_f27(su5, fermions)
    validate_f27_rows(f27)
    pati = pati_salam_control()
    attempts = product_parent_attempts(pati, fermions)
    mutations = mutation_suite(su5, fermions, full, f48, coroot_rows, su4, f27)
    return {
        "base": base, "full_commutant": full, "coroot_rows": coroot_rows, "f48": f48,
        "su4_slice": su4, "f27": f27, "pati_salam": pati,
        "product_parent_attempts": attempts, "mutation_tests": mutations,
        "claim_status": claim_ledger(full, f48, su4, pati),
    }


if __name__ == "__main__":
    result = run_v2()
    print("s3_construction_v2.py: PASS: "
          f"commutant={result['full_commutant']['rank']}/{result['full_commutant']['nullity']} "
          f"pi2={result['f48']['pi2_SU5_over_H']} "
          f"mutations={len(result['mutation_tests'])}/{len(result['mutation_tests'])}")
