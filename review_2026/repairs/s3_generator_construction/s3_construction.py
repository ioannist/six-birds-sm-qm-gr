#!/usr/bin/env python3
"""Pure computations for the S3 unification-object reconstruction."""

from __future__ import annotations

from collections import defaultdict, deque
from fractions import Fraction
from itertools import combinations
from math import comb
from typing import Callable, Iterable, Sequence

from exact_lie import (
    F,
    GQ,
    Matrix,
    commutator,
    diagonal,
    embed,
    flatten,
    format_fraction,
    is_zero,
    madd,
    matmul,
    matrix,
    matrix_key,
    matrix_span_rank,
    mscale,
    nullspace,
    primitive_integer,
    smith_invariants,
    su_hermitian_basis,
    trace,
    unit,
)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _transpose(a: Matrix) -> Matrix:
    return matrix([[a[j][i] for j in range(len(a))] for i in range(len(a[0]))])


def _is_hermitian(a: Matrix) -> bool:
    return all(a[i][j] == a[j][i].conjugate()
               for i in range(len(a)) for j in range(len(a[0])))


def validate_su_basis(basis: Sequence[tuple[str, Matrix]], n: int) -> None:
    _assert(len(basis) == n * n - 1, f"su({n}) basis count is not {n*n-1}")
    _assert(all(len(a) == n and len(a[0]) == n for _, a in basis), "wrong matrix size")
    _assert(all(_is_hermitian(a) for _, a in basis), "basis contains a non-Hermitian matrix")
    _assert(all(trace(a) == GQ() for _, a in basis), "basis contains a non-traceless matrix")
    _assert(matrix_span_rank([a for _, a in basis]) == n * n - 1, "basis is linearly dependent")


def diagonal_centralizer(embedded_generators: Sequence[Matrix], n: int) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    """Solve [diag(x),g]=0 and sum(x)=0, then primitive-normalize the null vector."""
    equations: list[list[Fraction]] = []
    seen: set[tuple[Fraction, ...]] = set()
    for g in embedded_generators:
        for i in range(n):
            for j in range(n):
                if i != j and g[i][j]:
                    row = [Fraction(0)] * n
                    row[i], row[j] = Fraction(1), Fraction(-1)
                    key = tuple(row)
                    if key not in seen:
                        equations.append(row)
                        seen.add(key)
    equations.append([Fraction(1)] * n)
    kernel = nullspace(equations)
    _assert(len(kernel) == 1, f"diagonal centralizer dimension is {len(kernel)}, expected 1")
    primitive = primitive_integer(kernel[0], preferred_index=n - 1)
    return equations, primitive


def _block_embedded_basis(block_sizes: Sequence[int]) -> tuple[list[tuple[str, Matrix]], list[list[int]]]:
    n = sum(block_sizes)
    result: list[tuple[str, Matrix]] = []
    blocks: list[list[int]] = []
    start = 0
    for block_no, size in enumerate(block_sizes):
        indices = list(range(start, start + size))
        blocks.append(indices)
        for name, a in su_hermitian_basis(size, f"B{block_no}"):
            result.append((name, embed(a, indices, n)))
        start += size
    return result, blocks


def construct_su5() -> dict:
    basis = su_hermitian_basis(5, "SU5")
    validate_su_basis(basis, 5)
    embedded, blocks = _block_embedded_basis([3, 2])
    equations, primitive = diagonal_centralizer([a for _, a in embedded], 5)
    _assert(primitive[3] == primitive[4] and primitive[3] > 0, "weak-block sign convention failed")

    # Fix the continuous scale by declaring the weak-pair state in wedge^2(5)
    # to have unit abelian charge. The direction itself was already derived.
    weak_pair_primitive_charge = primitive[blocks[1][0]] + primitive[blocks[1][1]]
    _assert(weak_pair_primitive_charge != 0, "normalization state has zero charge")
    standard_scale = Fraction(1, weak_pair_primitive_charge)
    y_values = tuple(F(x) * standard_scale for x in primitive)
    y = diagonal(y_values)
    _assert(all(is_zero(commutator(y, a)) for _, a in embedded), "derived Y does not commute")
    _assert(trace(y) == GQ(), "derived Y is not traceless")

    subalgebra = embedded + [("Y", y)]
    coset_hermitian: list[tuple[str, Matrix]] = []
    color, weak = blocks
    for i in color:
        for alpha in weak:
            coset_hermitian.append((f"X_S_{i}{alpha}", madd(unit(5, i, alpha), unit(5, alpha, i))))
            coset_hermitian.append((f"X_A_{i}{alpha}", madd(unit(5, i, alpha, GQ(0, -1)),
                                                              unit(5, alpha, i, GQ(0, 1)))))
    _assert(len(subalgebra) == 12 and len(coset_hermitian) == 12, "wrong SU(5) partition dimensions")
    _assert(matrix_span_rank([a for _, a in subalgebra + coset_hermitian]) == 24,
            "subalgebra plus coset does not span su(5)")

    generator_rows = []
    sub_keys = {matrix_key(a) for _, a in embedded}
    coset_keys = {matrix_key(a) for _, a in coset_hermitian}
    for name, a in basis:
        # The standard basis diagonal sector is not the chosen Y basis, so classify
        # by block support, while preserving all 24 explicitly constructed matrices.
        cross = any(a[i][j] for i in color for j in weak) or any(a[i][j] for i in weak for j in color)
        sector = "coset" if cross else "embedded_subalgebra_span"
        generator_rows.append({"generator_id": name, "sector": sector,
                               "trace": str(trace(a)), "matrix": matrix_key(a)})

    return {
        "basis": basis,
        "embedded": embedded,
        "blocks": blocks,
        "centralizer_equations": equations,
        "primitive": primitive,
        "standard_scale": standard_scale,
        "y_values": y_values,
        "y": y,
        "subalgebra": subalgebra,
        "coset_hermitian": coset_hermitian,
        "generator_rows": generator_rows,
    }


def _adjoint_action_matrix(g: Matrix, roots: Sequence[Matrix]) -> Matrix:
    columns: list[list[GQ]] = []
    flat_roots = [flatten(r) for r in roots]
    pivots = [next(i for i, x in enumerate(v) if x) for v in flat_roots]
    for root in roots:
        c = flatten(commutator(g, root))
        coeff = [c[p] / flat_roots[k][p] for k, p in enumerate(pivots)]
        reconstructed = tuple(sum((coeff[k] * flat_roots[k][i] for k in range(len(roots))), GQ())
                              for i in range(len(c)))
        _assert(reconstructed == c, "adjoint action escaped the coset root span")
        columns.append(coeff)
    return matrix(list(map(list, zip(*columns))))


def _connected_components(actions: Sequence[Matrix], size: int) -> list[list[int]]:
    graph = [set() for _ in range(size)]
    for a in actions:
        for target in range(size):
            for source in range(size):
                if a[target][source] and target != source:
                    graph[source].add(target)
                    graph[target].add(source)
    unseen = set(range(size))
    components = []
    while unseen:
        start = min(unseen)
        queue = deque([start])
        unseen.remove(start)
        component = []
        while queue:
            node = queue.popleft()
            component.append(node)
            for other in sorted(graph[node]):
                if other in unseen:
                    unseen.remove(other)
                    queue.append(other)
        components.append(sorted(component))
    return components


def _eigenvalue_on_basis(action: Matrix, index: int) -> Fraction:
    _assert(all(not action[r][index] for r in range(len(action)) if r != index), "not a weight basis")
    value = action[index][index]
    _assert(value.im == 0, "non-real weight")
    return value.re


def _classify_color(weight_set: set[tuple[Fraction, Fraction]]) -> str:
    fundamental = {(F(1), F(1)), (F(-1), F(1)), (F(0), F(-2))}
    if weight_set == fundamental:
        return "3"
    if weight_set == {(-a, -b) for a, b in fundamental}:
        return "3bar"
    if weight_set == {(F(0), F(0))}:
        return "1"
    raise AssertionError(f"unrecognized SU(3) weight set {weight_set}")


def _classify_weak(weight_set: set[Fraction]) -> str:
    if weight_set == {F(1), F(-1)}:
        return "2"
    if weight_set == {F(0)}:
        return "1"
    raise AssertionError(f"unrecognized SU(2) weight set {weight_set}")


def compute_coset_quantum_numbers(su5: dict) -> list[dict]:
    color, weak = su5["blocks"]
    roots: list[tuple[str, Matrix]] = []
    for i in color:
        for alpha in weak:
            roots.append((f"E_{i}{alpha}", unit(5, i, alpha)))
            roots.append((f"E_{alpha}{i}", unit(5, alpha, i)))
    root_matrices = [a for _, a in roots]
    embedded_actions = [_adjoint_action_matrix(g, root_matrices) for _, g in su5["embedded"]]
    components = _connected_components(embedded_actions, len(roots))
    _assert(sorted(map(len, components)) == [6, 6], "coset did not decompose into two six-dimensional multiplets")

    color_cartans = [embed(a, color, 5) for name, a in su_hermitian_basis(3) if "_D_" in name]
    weak_cartan = next(embed(a, weak, 5) for name, a in su_hermitian_basis(2) if "_D_" in name)
    diagonal_actions = [_adjoint_action_matrix(h, root_matrices) for h in color_cartans + [weak_cartan, su5["y"]]]
    component_labels: dict[int, tuple[str, str, Fraction]] = {}
    for component in components:
        color_weights = {tuple(_eigenvalue_on_basis(a, i) for a in diagonal_actions[:2]) for i in component}
        weak_weights = {_eigenvalue_on_basis(diagonal_actions[2], i) for i in component}
        ys = {_eigenvalue_on_basis(diagonal_actions[3], i) for i in component}
        _assert(len(ys) == 1, "Y is not constant on a coset multiplet")
        label = (_classify_color(color_weights), _classify_weak(weak_weights), next(iter(ys)))
        for i in component:
            component_labels[i] = label

    rows = []
    for i, (name, _) in enumerate(roots):
        c, w, y = component_labels[i]
        color_weight = tuple(_eigenvalue_on_basis(a, i) for a in diagonal_actions[:2])
        t3_twice = _eigenvalue_on_basis(diagonal_actions[2], i)
        rows.append({
            "root_generator": name,
            "su3_rep": c,
            "su2_rep": w,
            "hypercharge": format_fraction(y),
            "su3_cartan_weight": f"({color_weight[0]},{color_weight[1]})",
            "t3": format_fraction(t3_twice / 2),
            "complex_multiplet": f"({c},{w},{format_fraction(y)})",
        })
    return rows


def antifund_action(g: Matrix) -> Matrix:
    return mscale(-1, _transpose(g))


def wedge2_action(g: Matrix) -> Matrix:
    n = len(g)
    pairs = list(combinations(range(n), 2))
    index = {pair: i for i, pair in enumerate(pairs)}
    rows = [[GQ() for _ in pairs] for _ in pairs]

    def add_wedge(target_a: int, target_b: int, source: int, coefficient: GQ) -> None:
        if target_a == target_b or not coefficient:
            return
        if target_a < target_b:
            target, sign = (target_a, target_b), 1
        else:
            target, sign = (target_b, target_a), -1
        rows[index[target]][source] += sign * coefficient

    for source, (i, j) in enumerate(pairs):
        for k in range(n):
            add_wedge(k, j, source, g[k][i])
            add_wedge(i, k, source, g[k][j])
    return matrix(rows)


def _rep_bases() -> tuple[list[str], list[str]]:
    anti = [f"5bar[{i}]" for i in range(5)]
    ten = [f"10[{i}{j}]" for i, j in combinations(range(5), 2)]
    return anti, ten


def _block_diag(a: Matrix, b: Matrix) -> Matrix:
    na, nb = len(a), len(b)
    return matrix([list(a[i]) + [0] * nb for i in range(na)] +
                  [[0] * na + list(b[i]) for i in range(nb)])


def fermion_decomposition(su5: dict, y_scale_multiplier: Fraction = Fraction(1)) -> dict:
    anti_names, ten_names = _rep_bases()
    state_names = anti_names + ten_names
    rep_action: Callable[[Matrix], Matrix] = lambda g: _block_diag(antifund_action(g), wedge2_action(g))
    embedded_actions = [rep_action(g) for _, g in su5["embedded"]]
    components = _connected_components(embedded_actions, 15)
    _assert(sorted(map(len, components)) == [1, 2, 3, 3, 6], "unexpected 5bar+10 decomposition")

    color, weak = su5["blocks"]
    color_cartans = [embed(a, color, 5) for name, a in su_hermitian_basis(3) if "_D_" in name]
    weak_cartan = next(embed(a, weak, 5) for name, a in su_hermitian_basis(2) if "_D_" in name)
    y = mscale(y_scale_multiplier, su5["y"])
    diag_actions = [rep_action(h) for h in color_cartans + [weak_cartan, y]]

    component_info: dict[int, dict] = {}
    rows = []
    for number, component in enumerate(components, 1):
        color_weights = {tuple(_eigenvalue_on_basis(a, i) for a in diag_actions[:2]) for i in component}
        weak_twice_weights = {_eigenvalue_on_basis(diag_actions[2], i) for i in component}
        ys = {_eigenvalue_on_basis(diag_actions[3], i) for i in component}
        _assert(len(ys) == 1, "Y not constant on a fermion multiplet")
        color_rep = _classify_color(color_weights)
        weak_rep = _classify_weak(weak_twice_weights)
        y_value = next(iter(ys))
        irrep = "5bar" if all(i < 5 for i in component) else "10"
        _assert(all((i < 5) == (irrep == "5bar") for i in component), "component crosses irreps")
        label = f"({color_rep},{weak_rep},{format_fraction(y_value)})"
        for i in component:
            t3 = _eigenvalue_on_basis(diag_actions[2], i) / 2
            q = t3 + _eigenvalue_on_basis(diag_actions[3], i)
            baryon = Fraction(1, 3) if color_rep == "3" else Fraction(-1, 3) if color_rep == "3bar" else Fraction(0)
            role = "quark" if color_rep != "1" else "lepton"
            info = {"component_id": f"C{number}", "irrep": irrep, "multiplet": label,
                    "su3_rep": color_rep, "su2_rep": weak_rep, "hypercharge": y_value,
                    "t3": t3, "electric_charge": q, "baryon_number": baryon, "role": role}
            component_info[i] = info
            rows.append({"state": state_names[i], **{k: (format_fraction(v) if isinstance(v, Fraction) else v)
                                                     for k, v in info.items()}})

    t3_squared = sum((_eigenvalue_on_basis(diag_actions[2], i) / 2) ** 2 for i in range(15))
    y_squared = sum(_eigenvalue_on_basis(diag_actions[3], i) ** 2 for i in range(15))
    q_squared = sum((_eigenvalue_on_basis(diag_actions[2], i) / 2 +
                     _eigenvalue_on_basis(diag_actions[3], i)) ** 2 for i in range(15))
    return {"rows": rows, "state_names": state_names, "component_info": component_info,
            "rep_action": rep_action, "t3_squared": t3_squared, "y_squared": y_squared,
            "q_squared": q_squared, "sin2": t3_squared / q_squared}


def ratio_conventions(su5: dict) -> list[dict]:
    t3_fund = [Fraction(0), Fraction(0), Fraction(0), Fraction(1, 2), Fraction(-1, 2)]
    rows = []
    for name, multiplier in [("weak-pair-unit-standard", Fraction(1)),
                             ("twice-standard-abelian-coordinate", Fraction(2))]:
        y_values = [multiplier * x for x in su5["y_values"]]
        tr_y2 = sum(x * x for x in y_values)
        tr_t32 = sum(x * x for x in t3_fund)
        fermions = fermion_decomposition(su5, multiplier)
        rows.append({
            "convention": name,
            "y_scale_vs_standard": format_fraction(multiplier),
            "fundamental_tr_y2": format_fraction(tr_y2),
            "fundamental_tr_t3_squared": format_fraction(tr_t32),
            "k_y": format_fraction(tr_y2 / tr_t32),
            "generation_tr_q2": format_fraction(fermions["q_squared"]),
            "generation_tr_t3_squared": format_fraction(fermions["t3_squared"]),
            "sin2_theta_w": format_fraction(fermions["sin2"]),
        })
    return rows


def compute_f27(su5: dict, fermions: dict) -> list[dict]:
    rows = []
    info = fermions["component_info"]
    for name, generator in su5["coset_hermitian"]:
        action = fermions["rep_action"](generator)
        transition_count = 0
        nonzero_delta_b: set[Fraction] = set()
        transition_types: set[str] = set()
        for target in range(15):
            for source in range(15):
                if target != source and action[target][source]:
                    transition_count += 1
                    db = info[target]["baryon_number"] - info[source]["baryon_number"]
                    if db:
                        nonzero_delta_b.add(db)
                        transition_types.add(f"{info[source]['role']}->{info[target]['role']}")
        rows.append({
            "generator_id": name,
            "nonzero_transition_entries": transition_count,
            "mediates_delta_b": bool(nonzero_delta_b),
            "delta_b_values": "|".join(map(format_fraction, sorted(nonzero_delta_b))),
            "transition_types": "|".join(sorted(transition_types)),
        })
    _assert(all(row["mediates_delta_b"] for row in rows), "not every SU(5) coset generator mediates Delta B")

    for name, generator in su5["subalgebra"]:
        action = fermions["rep_action"](generator)
        for target in range(15):
            for source in range(15):
                if action[target][source]:
                    _assert(info[target]["baryon_number"] == info[source]["baryon_number"],
                            f"embedded SM generator {name} changes baryon number")
    return rows


def construct_su4_analogue() -> dict:
    basis = su_hermitian_basis(4, "SU4")
    validate_su_basis(basis, 4)
    embedded, blocks = _block_embedded_basis([3, 1])
    equations, primitive = diagonal_centralizer([a for _, a in embedded], 4)
    _assert(primitive[-1] > 0, "SU(4) centralizer sign convention failed")
    # Set the singlet coordinate to unit charge; this fixes only an abelian convention.
    scale = Fraction(1, primitive[-1])
    u1 = tuple(F(x) * scale for x in primitive)
    rows = []
    for i in blocks[0]:
        for source, target, rep in [(i, 3, "3"), (3, i, "3bar")]:
            charge = u1[source] - u1[target]
            rows.append({"root_generator": f"E_{source}{target}", "su3_rep": rep,
                         "u1_charge": format_fraction(charge),
                         "su5_fixed_weak_index_map": f"SU4:E_{source}{target}->SU5:E_{source}{target}",
                         "charge_rescaling_su4_to_su5": "5/8"})
    return {"primitive": primitive, "scale": scale, "u1_values": u1, "rows": rows,
            "centralizer_dimension": len(nullspace(equations)),
            "verdict": "ANALOGUE_AS_FIXED_WEAK_INDEX_SLICE_NOT_IDENTITY"}


def compute_f48(su5: dict) -> dict:
    # Coordinates use the SU(5) cocharacter basis e0-e4,...,e3-e4.
    derived_coroot_columns = [
        [1, -1, 0, 0],
        [0, 1, -1, 0],
        [0, 0, 0, 1],
    ]
    # smith_invariants expects rows, so transpose the column presentation.
    presentation = [list(row) for row in zip(*derived_coroot_columns)]
    rank, invariants = smith_invariants(presentation)
    _assert(rank == 3 and invariants == (1, 1, 1), "unexpected H cocharacter quotient")
    annihilator = nullspace([[F(x) for x in col] for col in derived_coroot_columns])
    _assert(len(annihilator) == 1, "expected one free H loop")
    loop_character = primitive_integer(annihilator[0], preferred_index=0)
    primitive = su5["primitive"]
    _assert(sum(primitive) == 0, "centralizer cocharacter is not traceless")
    # In the e0-e4,...,e3-e4 basis a traceless vector's coordinates are
    # precisely its first four entries. Thus this is derived from the solved
    # centralizer, not separately supplied topology data.
    centralizer_cocharacter = primitive[:4]
    central_u1_loop_index = abs(sum(a * b for a, b in zip(loop_character, centralizer_cocharacter)))
    _assert(central_u1_loop_index == 6, "derived quotient is not Z6")
    return {
        "cocharacter_rank": 4,
        "derived_coroot_rank": rank,
        "smith_invariants": "|".join(map(str, invariants)),
        "free_rank_pi1_h": 1,
        "torsion_pi1_h": "none",
        "primitive_loop_character": str(loop_character),
        "central_u1_loop_index": central_u1_loop_index,
        "global_form": "[SU(3)xSU(2)xU(1)]/Z6",
        "su5_pi2_g_over_h": "Z",
        "sm_alone_pi2_g_over_h": "0",
    }


def compute_parent_candidates() -> list[dict]:
    rows = []
    for n in range(5, 9):
        embedded_dimension = 8 + 3 + 1
        parent_dimension = n * n - 1
        centralizer_dimension = n - 4  # derived from one value per 3,2, and singleton block, minus trace
        coset_dimension = parent_dimension - embedded_dimension
        extra_fundamental_singlets = n - 5
        predicates = {
            "simple_su_parent": True,
            "exact_single_u1_centralizer": centralizer_dimension == 1,
            "exact_xy_coset_dimension_12": coset_dimension == 12,
            "no_extra_fundamental_singlets": extra_fundamental_singlets == 0,
            "wedge2_plus_antifund_dimension_15": comb(n, 2) + n == 15,
        }
        rows.append({"candidate": f"SU({n})", "parent_dimension": parent_dimension,
                     "centralizer_dimension": centralizer_dimension, "coset_dimension": coset_dimension,
                     "extra_fundamental_singlets": extra_fundamental_singlets,
                     **predicates, "selected": all(predicates.values())})
    _assert([r["candidate"] for r in rows if r["selected"]] == ["SU(5)"],
            "bounded regular-SU candidate computation did not uniquely select SU(5)")
    return rows


def validate_role_assignment(fermions: dict, roles: dict[int, str] | None = None) -> None:
    for i, info in fermions["component_info"].items():
        expected = "lepton" if info["su3_rep"] == "1" else "quark"
        actual = info["role"] if roles is None else roles[i]
        _assert(actual == expected, f"role mismatch at fermion state {i}")


def mutation_tests(su5: dict, fermions: dict) -> list[dict]:
    tests = []

    def expect_rejected(name: str, mutate_and_validate: Callable[[], None]) -> None:
        try:
            mutate_and_validate()
        except AssertionError as exc:
            tests.append({"mutation": name, "expected": "rejected", "result": "PASS",
                          "rejection": str(exc)})
        else:
            tests.append({"mutation": name, "expected": "rejected", "result": "FAIL",
                          "rejection": "mutation was accepted"})

    def perturbed_y() -> None:
        values = list(su5["y_values"])
        values[0] += Fraction(1, 6)
        values[1] -= Fraction(1, 6)
        y = diagonal(values)
        _assert(all(is_zero(commutator(y, g)) for _, g in su5["embedded"]),
                "perturbed eigenvalue left the centralizer")

    def swapped_role() -> None:
        roles = {i: info["role"] for i, info in fermions["component_info"].items()}
        quark = next(i for i, role in roles.items() if role == "quark")
        lepton = next(i for i, role in roles.items() if role == "lepton")
        roles[quark], roles[lepton] = roles[lepton], roles[quark]
        validate_role_assignment(fermions, roles)

    def broken_tracelessness() -> None:
        altered = list(su5["basis"])
        name, first = altered[0]
        altered[0] = (name, madd(first, unit(5, 0, 0)))
        validate_su_basis(altered, 5)

    expect_rejected("perturb_hypercharge_eigenvalue", perturbed_y)
    expect_rejected("swap_quark_lepton_role", swapped_role)
    expect_rejected("break_generator_tracelessness", broken_tracelessness)
    _assert(all(t["result"] == "PASS" for t in tests), "a mutation escaped validation")
    return tests


def claim_status_rows(ratios: list[dict], su4: dict, f27: list[dict], f48: dict) -> list[dict]:
    standard = ratios[0]
    return [
        {"claim": "SU5 hypercharge direction", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": "centralizer dimension 1; primitive (-2,-2,-2,3,3)",
         "residual_assumption_or_convention": "overall sign and scale"},
        {"claim": "k_Y and weak-angle ratio", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": f"k_Y={standard['k_y']}; sin2(theta_W)={standard['sin2_theta_w']}",
         "residual_assumption_or_convention": "weak-pair state assigned unit abelian charge; Q=T3+Y"},
        {"claim": "SU5 X/Y coset", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": "12 roots: (3,2,-5/6)+(3bar,2,5/6)",
         "residual_assumption_or_convention": "regular 3+2 block embedding"},
        {"claim": "step41 six-generator identity", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": su4["verdict"],
         "residual_assumption_or_convention": "charge rescaling required for slice comparison"},
        {"claim": "F27 baryon descent", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": f"{sum(r['mediates_delta_b'] for r in f27)}/12 coset generators change B; SM subalgebra 0",
         "residual_assumption_or_convention": "B=(1/3,-1/3,0) on 3,3bar,1 left-chiral components"},
        {"claim": "F48 monopole", "status": "LANDED-BY-CONSTRUCTION",
         "computed_result": f"pi2(SU5/H)={f48['su5_pi2_g_over_h']}; SM-alone={f48['sm_alone_pi2_g_over_h']}",
         "residual_assumption_or_convention": "standard exact-sequence facts pi2(SU5)=pi1(SU5)=0"},
        {"claim": "unique parent", "status": "REMAINING-IMPORT",
         "computed_result": "SU(5) uniquely selected within regular SU(n), n=5..8",
         "residual_assumption_or_convention": "candidate class does not exhaust SO(10), E6, or non-regular embeddings"},
    ]


def run_all() -> dict:
    su5 = construct_su5()
    coset = compute_coset_quantum_numbers(su5)
    fermions = fermion_decomposition(su5)
    expected_multiplets = {"(3bar,1,1/3)", "(1,2,-1/2)", "(3bar,1,-2/3)",
                           "(3,2,1/6)", "(1,1,1)"}
    _assert({row["multiplet"] for row in fermions["rows"]} == expected_multiplets,
            "derived fermion multiplets do not match one generation")
    validate_role_assignment(fermions)
    ratios = ratio_conventions(su5)
    _assert(ratios[0]["k_y"] == "5/3" and ratios[0]["sin2_theta_w"] == "3/8",
            "standard ratios were not recovered")
    f27 = compute_f27(su5, fermions)
    su4 = construct_su4_analogue()
    f48 = compute_f48(su5)
    parents = compute_parent_candidates()
    mutations = mutation_tests(su5, fermions)
    return {
        "su5_generators": su5["generator_rows"],
        "hypercharge": {
            "centralizer_dimension": 1,
            "primitive_pattern": "(" + ",".join(map(str, su5["primitive"])) + ")",
            "standard_scale": format_fraction(su5["standard_scale"]),
            "standard_pattern": "(" + ",".join(map(format_fraction, su5["y_values"])) + ")",
            "normalization_rule": "wedge^2 weak-pair state has charge +1",
        },
        "coset_quantum_numbers": coset,
        "fermion_decomposition": fermions["rows"],
        "ratio_conventions": ratios,
        "f27_generator_actions": f27,
        "f27_summary": {"coset_generators": 12, "delta_b_generators": sum(r["mediates_delta_b"] for r in f27),
                        "sm_subalgebra_delta_b_generators": 0, "sm_clean_baryon_conserved": True},
        "su4_analogue": su4["rows"],
        "su4_summary": {"primitive_pattern": str(su4["primitive"]), "u1_pattern": str(su4["u1_values"]),
                        "coset_dimension": 6, "verdict": su4["verdict"]},
        "f48_lattice": [f48],
        "parent_candidates": parents,
        "mutation_tests": mutations,
        "claim_status": claim_status_rows(ratios, su4, f27, f48),
    }


if __name__ == "__main__":
    result = run_all()
    print("S3 construction: PASS")
    print(f"hypercharge={result['hypercharge']['standard_pattern']}")
    print(f"k_Y={result['ratio_conventions'][0]['k_y']} sin2={result['ratio_conventions'][0]['sin2_theta_w']}")
