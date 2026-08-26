#!/usr/bin/env python3
"""Q1 repair: field-derived access modes and exhaustive finite quotients."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
STEP22 = REPO / "physics_atlas/thread_qm_gr/steps/step22_f51_unification_common_refinement_artifacts/f51_unification_step22.py"
STEP25 = REPO / "physics_atlas/thread_qm_gr/steps/step25_sourcing_unification_artifacts/sourcing_unification_step25.py"
STEP26 = REPO / "physics_atlas/thread_qm_gr/steps/step26_semiclassical_dynamics_artifacts/semiclassical_dynamics_step26.py"
STEP28 = REPO / "physics_atlas/thread_qm_gr/steps/step28_nonstationary_relational_histories_artifacts/nonstationary_relational_history_step28.py"
FIELDS24 = REPO / "physics_atlas/thread_qm_gr/steps/step24_derived_physical_audits_artifacts/toy_field_samples_step24.json"
HISTORY28 = REPO / "physics_atlas/thread_qm_gr/steps/step28_nonstationary_relational_histories_artifacts/nonstationary_history_step28.json"
F24_SOURCE = REPO / "physics_atlas/thread_qm_gr/steps/step20_f24_predicate_construction_artifacts/fiv_f24_source_record_step20.json"

PINS = {
    "step22_script": "ca230f443bbdb63cbee7dd652fac1288e06dcf6ad7f102269e97aab37abadd9a",
    "step25_script": "8f541685d8e0e475107d1b5c26186d612c91f55d1b95b345bc0635f14d25c2a7",
    "step26_script": "391907fae6fdee8c4e4de1c12ee67d72fdfea4928cad1f148cc30e31584898fd",
    "step28_script": "412f31da54e8ec6f63d1bde125cd4f318a9eab3f8fc1834438a14745c5c0dac3",
    "step24_fields": "130b8906149be1048a602f27110bbf2c56fea08f800aa237f95d1eceff29e286",
    "step28_history": "547c8ba4d391523de0e3e4cf0647ba96e4ba529387426fea4738f63cec247954",
    "f24_source_record": "024b15c65f5044567683527c9a1be7b6f333616783469eadc5004c6b43cdded5",
}
PATHS = {
    "step22_script": STEP22,
    "step25_script": STEP25,
    "step26_script": STEP26,
    "step28_script": STEP28,
    "step24_fields": FIELDS24,
    "step28_history": HISTORY28,
    "f24_source_record": F24_SOURCE,
}
MODE_NAMES = ("d0_norm", "d1_current_orientation", "d2_density_peak", "d3_geometry_peak")
QM_DIMS = (0, 1, 2)
GR_DIMS = (0, 2, 3)
TOL = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(f"q1_{name}", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def pinned_dependencies() -> tuple[Any, Any, Any, list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    for name, path in PATHS.items():
        actual = sha256(path)
        if actual != PINS[name]:
            raise RuntimeError(f"{name} pin mismatch: {actual} != {PINS[name]}")
        rows.append({
            "dependency": name,
            "kind": "imported_script" if name in {"step22_script", "step25_script", "step26_script"} else "source_evidence",
            "path": str(path.relative_to(REPO)),
            "expected_sha256": PINS[name],
            "actual_sha256": actual,
            "passes": actual == PINS[name],
        })
    return (
        load_module("step22", STEP22),
        load_module("step25", STEP25),
        load_module("step26", STEP26),
        rows,
    )


def complex_field(record: dict[str, Any]) -> np.ndarray:
    return np.asarray(record["psi_re"], dtype=float) + 1j * np.asarray(record["psi_im"], dtype=float)


def population(step26: Any) -> tuple[list[dict[str, Any]], np.ndarray, list[dict[str, Any]]]:
    fields = json.loads(FIELDS24.read_text(encoding="utf-8"))
    history = json.loads(HISTORY28.read_text(encoding="utf-8"))
    background = np.asarray(fields["potential"], dtype=float)
    rows: list[dict[str, Any]] = []
    for record in fields["fields"]:
        rows.append({
            "state_id": f"step25_{int(record['sample']):03d}",
            "source_class": "step25_field_sample",
            "psi": step26.normalize(complex_field(record)),
            "background": background.copy(),
        })
    for record in history["states"]:
        rows.append({
            "state_id": f"step28_t{int(record['clock_t']):02d}",
            "source_class": "step28_history_state",
            "psi": step26.normalize(complex_field(record)),
            "background": background.copy(),
        })
    rng = np.random.default_rng(71017)
    for index in range(8):
        psi = rng.normal(size=8) + 1j * rng.normal(size=8)
        rows.append({
            "state_id": f"fresh_seeded_{index:02d}",
            "source_class": "fresh_seeded",
            "psi": step26.normalize(psi),
            "background": background.copy(),
        })

    phase = step26.normalize(rng.normal(size=8) + 1j * rng.normal(size=8))
    rows.extend([
        {"state_id": "control_phase_original", "source_class": "phase_only_control", "psi": phase,
         "background": background.copy()},
        {"state_id": "control_phase_conjugate", "source_class": "phase_only_control", "psi": np.conjugate(phase),
         "background": background.copy()},
    ])
    potential_psi = step26.normalize(rng.normal(size=8) + 1j * rng.normal(size=8))
    base_effective = background + 0.3 * step26.stress_energy_density(potential_psi, background)
    target = (int(np.argmax(base_effective)) + 3) % len(background)
    perturbed = background.copy()
    perturbed[target] += 5.0
    rows.extend([
        {"state_id": "control_potential_base", "source_class": "potential_only_control", "psi": potential_psi,
         "background": background.copy()},
        {"state_id": "control_potential_perturbed", "source_class": "potential_only_control", "psi": potential_psi,
         "background": perturbed},
    ])
    return rows, background, history["potentials"]


def evaluate_modes(record: dict[str, Any], step25: Any, step26: Any) -> dict[str, Any]:
    psi = record["psi"]
    background = record["background"]
    rho, current = step25.born_audit(psi)
    t00 = step26.stress_energy_density(psi, background)
    sourced_potential = background + 0.3 * t00
    norm2 = float(np.sum(rho))
    current_total = float(np.sum(current))
    modes = (
        int(round(norm2)),
        int(current_total >= 0.0),
        int(np.argmax(rho)),
        int(np.argmax(sourced_potential)),
    )
    return {
        "state_id": record["state_id"],
        "source_class": record["source_class"],
        "d0_norm": modes[0],
        "d1_current_orientation": modes[1],
        "d2_density_peak": modes[2],
        "d3_geometry_peak": modes[3],
        "norm_squared": norm2,
        "current_total": current_total,
        "density_peak_value": float(rho[modes[2]]),
        "sourced_potential_peak_value": float(sourced_potential[modes[3]]),
        "sourced_potential_min": float(np.min(sourced_potential)),
        "sourced_potential_max": float(np.max(sourced_potential)),
        "mode_tuple": modes,
        "born_signature": tuple(np.round(np.concatenate([rho, current]), 14)),
        "geometry_signature": tuple(np.round(np.concatenate([rho, sourced_potential]), 14)),
    }


def key(rows: list[dict[str, Any]], dims: tuple[int, ...]) -> list[tuple[Any, ...]]:
    return [tuple(row["mode_tuple"][dim] for dim in dims) for row in rows]


def factorization(source: list[Any], target: list[Any]) -> tuple[bool, list[tuple[int, int]]]:
    defects: list[tuple[int, int]] = []
    for left in range(len(source)):
        for right in range(left + 1, len(source)):
            if source[left] == source[right] and target[left] != target[right]:
                defects.append((left, right))
    return not defects, defects


def first_witness(defects: list[tuple[int, int]], rows: list[dict[str, Any]]) -> str:
    if not defects:
        return ""
    left, right = defects[0]
    return f"{rows[left]['state_id']}|{rows[right]['state_id']}"


def provenance(step25: Any, step26: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    raw, _, history_potentials = population(step26)
    evaluated = [evaluate_modes(row, step25, step26) for row in raw]
    qm = key(evaluated, QM_DIMS)
    gr = key(evaluated, GR_DIMS)
    d1 = [row["d1_current_orientation"] for row in evaluated]
    d3 = [row["d3_geometry_peak"] for row in evaluated]
    born = [row["born_signature"] for row in evaluated]
    geometry = [row["geometry_signature"] for row in evaluated]
    checks = []
    for check_id, source, target in [
        ("born_audit_determines_d1", born, d1),
        ("born_audit_determines_d3", born, d3),
        ("q_QM_determines_d1", qm, d1),
        ("q_QM_determines_d3", qm, d3),
        ("geometry_readout_determines_d3", geometry, d3),
        ("q_GR_determines_d3", gr, d3),
        ("q_GR_determines_d1", gr, d1),
        ("q_QM_determines_q_GR", qm, gr),
        ("q_GR_determines_q_QM", gr, qm),
    ]:
        factors, defects = factorization(source, target)
        checks.append({
            "check": check_id,
            "factors": factors,
            "defect_pair_count": len(defects),
            "first_witness": first_witness(defects, evaluated),
        })

    by_id = {row["state_id"]: row for row in evaluated}
    phase_a = by_id["control_phase_original"]
    phase_b = by_id["control_phase_conjugate"]
    pot_a = by_id["control_potential_base"]
    pot_b = by_id["control_potential_perturbed"]
    control_rows = [
        {
            "control": "complex_conjugate_phase_only",
            "same_density_mode": phase_a["d2_density_peak"] == phase_b["d2_density_peak"],
            "same_geometry_mode": phase_a["d3_geometry_peak"] == phase_b["d3_geometry_peak"],
            "phase_mode_differs": phase_a["d1_current_orientation"] != phase_b["d1_current_orientation"],
            "same_q_GR_fiber": tuple(phase_a["mode_tuple"][i] for i in GR_DIMS) == tuple(phase_b["mode_tuple"][i] for i in GR_DIMS),
            "witness": "control_phase_original|control_phase_conjugate",
        },
        {
            "control": "potential_only",
            "same_density_mode": pot_a["d2_density_peak"] == pot_b["d2_density_peak"],
            "same_geometry_mode": pot_a["d3_geometry_peak"] == pot_b["d3_geometry_peak"],
            "phase_mode_differs": pot_a["d1_current_orientation"] != pot_b["d1_current_orientation"],
            "same_q_GR_fiber": tuple(pot_a["mode_tuple"][i] for i in GR_DIMS) == tuple(pot_b["mode_tuple"][i] for i in GR_DIMS),
            "same_q_QM_fiber": tuple(pot_a["mode_tuple"][i] for i in QM_DIMS) == tuple(pot_b["mode_tuple"][i] for i in QM_DIMS),
            "geometry_mode_differs": pot_a["d3_geometry_peak"] != pot_b["d3_geometry_peak"],
            "witness": "control_potential_base|control_potential_perturbed",
        },
    ]

    fiber_rows: list[dict[str, Any]] = []
    for quotient, values in (("q_QM", qm), ("q_GR", gr)):
        groups: dict[tuple[Any, ...], list[int]] = {}
        for index, value in enumerate(values):
            groups.setdefault(value, []).append(index)
        for fiber_id, (value, members) in enumerate(sorted(groups.items())):
            fiber_rows.append({
                "quotient": quotient,
                "fiber_id": fiber_id,
                "key": json.dumps(value, separators=(",", ":")),
                "size": len(members),
                "members": ";".join(evaluated[index]["state_id"] for index in members),
                "d1_values": ";".join(map(str, sorted({d1[index] for index in members}))),
                "d3_values": ";".join(map(str, sorted({d3[index] for index in members}))),
            })

    public_rows = [{k: v for k, v in row.items() if k not in {"mode_tuple", "born_signature", "geometry_signature"}}
                   for row in evaluated]
    check_map = {row["check"]: row for row in checks}
    history_residuals = []
    for clock, potential_record in enumerate(history_potentials):
        history_row = next(row for row in raw if row["state_id"] == f"step28_t{clock:02d}")
        recomputed = history_row["background"] + 0.3 * step26.stress_energy_density(history_row["psi"], history_row["background"])
        history_residuals.append(float(np.linalg.norm(recomputed - np.asarray(potential_record["potential"]))))
    summary = {
        "population_size": len(evaluated),
        "source_class_counts": {name: sum(row["source_class"] == name for row in evaluated)
                                for name in sorted({row["source_class"] for row in evaluated})},
        "q_QM_fiber_count": len({value for value in qm}),
        "q_GR_fiber_count": len({value for value in gr}),
        "born_determines_d1": check_map["born_audit_determines_d1"]["factors"],
        "born_determines_d3": check_map["born_audit_determines_d3"]["factors"],
        "geometry_determines_d3": check_map["geometry_readout_determines_d3"]["factors"],
        "geometry_determines_d1": check_map["q_GR_determines_d1"]["factors"],
        "access_split_realized": (
            check_map["born_audit_determines_d1"]["factors"]
            and not check_map["born_audit_determines_d3"]["factors"]
            and check_map["geometry_readout_determines_d3"]["factors"]
            and not check_map["q_GR_determines_d1"]["factors"]
        ),
        "step28_potential_recompute_max_residual": max(history_residuals),
        "d0_observed_values": sorted({row["d0_norm"] for row in evaluated}),
    }
    return public_rows, fiber_rows, checks + control_rows, summary


def subset_id(subset: tuple[int, ...]) -> str:
    return "P_empty" if not subset else "P_" + "_".join(f"d{index}" for index in subset)


def partition_signature(keys: list[tuple[Any, ...]]) -> tuple[int, ...]:
    labels: dict[tuple[Any, ...], int] = {}
    result = []
    for value in keys:
        if value not in labels:
            labels[value] = len(labels)
        result.append(labels[value])
    return tuple(result)


def join_signature(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    parent = list(range(len(left)))

    def find(value: int) -> int:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def union(a: int, b: int) -> None:
        a, b = find(a), find(b)
        if a != b:
            parent[b] = a

    for i in range(len(left)):
        for j in range(i + 1, len(left)):
            if left[i] == left[j] or right[i] == right[j]:
                union(i, j)
    return partition_signature([(find(i),) for i in range(len(left))])


def partition_exhaustion(step22: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    states = [tuple(map(int, row)) for row in np.asarray(step22.complete_mode_carrier())]
    catalog: dict[tuple[int, ...], dict[str, Any]] = {}
    signatures: dict[str, tuple[int, ...]] = {}
    keys_by_id: dict[str, list[tuple[Any, ...]]] = {}
    for mask in range(16):
        subset = tuple(index for index in range(4) if mask & (1 << index))
        name = subset_id(subset)
        keys = [tuple(state[index] for index in subset) for state in states]
        signature = partition_signature(keys)
        signatures[name] = signature
        keys_by_id[name] = keys
        catalog[signature] = {
            "partition_id": name,
            "coordinate_subset": ";".join(f"d{index}" for index in subset) or "empty",
            "coordinate_count": len(subset),
            "block_count": len(set(signature)),
            "fiber_size": 2 ** (4 - len(subset)),
        }
    catalog_rows = sorted(catalog.values(), key=lambda row: (row["coordinate_count"], row["partition_id"]))
    ids = sorted(keys_by_id)
    pair_rows: list[dict[str, Any]] = []
    closure_signatures = set(signatures.values())
    for left_index, left_id in enumerate(ids):
        for right_id in ids[left_index + 1:]:
            left_to_right, left_defects = factorization(keys_by_id[left_id], keys_by_id[right_id])
            right_to_left, right_defects = factorization(keys_by_id[right_id], keys_by_id[left_id])
            meet = partition_signature(list(zip(keys_by_id[left_id], keys_by_id[right_id])))
            join = join_signature(signatures[left_id], signatures[right_id])
            if meet not in catalog or join not in catalog:
                raise AssertionError("coordinate partition class not closed under meet/join")
            relation = (
                "equivalent" if left_to_right and right_to_left
                else "left_finer" if left_to_right
                else "right_finer" if right_to_left
                else "incomparable"
            )
            pair_rows.append({
                "partition_A": left_id,
                "partition_B": right_id,
                "A_determines_B": left_to_right,
                "B_determines_A": right_to_left,
                "A_to_B_defect_pairs": len(left_defects),
                "B_to_A_defect_pairs": len(right_defects),
                "relation": relation,
                "meet": catalog[meet]["partition_id"],
                "join": catalog[join]["partition_id"],
            })
            closure_signatures.update((meet, join))
    qm_id, gr_id = subset_id(QM_DIMS), subset_id(GR_DIMS)
    published = next(row for row in pair_rows if {row["partition_A"], row["partition_B"]} == {qm_id, gr_id})
    summary = {
        "carrier_state_count": len(states),
        "partition_count": len(catalog_rows),
        "distinct_unordered_pair_count": len(pair_rows),
        "incomparable_pair_count": sum(row["relation"] == "incomparable" for row in pair_rows),
        "nested_pair_count": sum(row["relation"] in {"left_finer", "right_finer"} for row in pair_rows),
        "meet_join_closure_count": len(closure_signatures),
        "q_QM_partition": qm_id,
        "q_GR_partition": gr_id,
        "q_QM_q_GR_relation": published["relation"],
        "q_QM_q_GR_directed_defects": [published["A_to_B_defect_pairs"], published["B_to_A_defect_pairs"]],
    }
    return catalog_rows, pair_rows, summary


def conditional_mean_matrix(keys: list[tuple[Any, ...]]) -> tuple[tuple[Fraction, ...], ...]:
    groups: dict[tuple[Any, ...], list[int]] = {}
    for index, value in enumerate(keys):
        groups.setdefault(value, []).append(index)
    matrix = [[Fraction(0) for _ in keys] for _ in keys]
    for members in groups.values():
        weight = Fraction(1, len(members))
        for row in members:
            for column in members:
                matrix[row][column] = weight
    return tuple(tuple(row) for row in matrix)


def matmul(left: tuple[tuple[Fraction, ...], ...], right: tuple[tuple[Fraction, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    size = len(left)
    return tuple(tuple(sum((left[i][k] * right[k][j] for k in range(size)), Fraction(0))
                       for j in range(size)) for i in range(size))


def candidate_map(family: str, state: tuple[int, ...]) -> tuple[Any, ...]:
    d0, d1, d2, d3 = state
    maps = {
        "MemoryLayer": (d0, d1, d2, d1 ^ d3),
        "HiddenUpstreamRole": (d0, d1, d2),
        "BridgeMediatedRole": (d0, d1, d2, d3),
        "BudgetedRole": (d0, d1, d2, d0 ^ d2),
        "ScopedRole": (d0, d1, d2, d3 if d0 == 0 else "OUT"),
        "CoarsenedRole": (d0, d2, d1 ^ d3),
        "OutsideRoleScope": (d0, d1 if d0 == 0 else "OUT", d2, d3 if d0 == 0 else "OUT"),
        "BlockedNonClosure": (d0, d1, d2, "BLOCKED"),
        "FusedDuplicateControl": (d0, d1, d2, d0, d2, d3),
    }
    return maps[family]


def generated_competitors(step22: Any) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    f24 = json.loads(F24_SOURCE.read_text(encoding="utf-8"))["families"]
    official = list(f24)
    families = official + ["FusedDuplicateControl"]
    states = [tuple(map(int, row)) for row in np.asarray(step22.complete_mode_carrier())]
    qm = [tuple(state[index] for index in QM_DIMS) for state in states]
    gr = [tuple(state[index] for index in GR_DIMS) for state in states]
    identity_signature = partition_signature([tuple(state) for state in states])
    definitions = {
        "MemoryLayer": "(d0,d1,d2,m=d1 XOR d3); exposed reversible memory code",
        "HiddenUpstreamRole": "(d0,d1,d2); d3 remains latent",
        "BridgeMediatedRole": "(d0,d1,d2,d3); explicit common refinement L",
        "BudgetedRole": "(d0,d1,d2,d3_hat=d0 XOR d2); no independent d3 budget",
        "ScopedRole": "(d0,d1,d2,d3 if d0=0 else OUT); resolves a proper scope",
        "CoarsenedRole": "(d0,d2,d1 XOR d3); quotient merges endpoint distinctions",
        "OutsideRoleScope": "(d0,d1,d2,d3) on d0=0 and OUT on d1,d3 otherwise",
        "BlockedNonClosure": "(d0,d1,d2,BLOCKED); unresolved coordinate is unformed",
        "FusedDuplicateControl": "(d0,d1,d2,d0,d2,d3); direct-sum duplicate",
    }
    rows: list[dict[str, Any]] = []
    values_rows: list[dict[str, Any]] = []
    for family in families:
        values = [candidate_map(family, state) for state in states]
        matrix = conditional_mean_matrix(values)
        stability = matmul(matrix, matrix) == matrix
        qm_control, qm_defects = factorization(values, qm)
        gr_control, gr_defects = factorization(values, gr)
        control = qm_control and gr_control
        formed = all("BLOCKED" not in value for value in values)
        audit = formed and len(values) == len(states) and len({len(value) for value in values}) == 1
        columns = [tuple(value[column] for value in values) for column in range(len(values[0]))]
        duplicates = [(left, right) for left in range(len(columns)) for right in range(left + 1, len(columns))
                      if columns[left] == columns[right]]
        no_smuggle = not duplicates and len(columns) <= 4
        collapse = partition_signature(values) == identity_signature
        reconciles = stability and control and audit and no_smuggle
        if reconciles and collapse:
            status = "reconciles_but_partition_equivalent_to_L"
        elif reconciles:
            status = "reconciles_as_distinct_partition"
        elif not audit:
            status = "blocked_nonclosure"
        elif not control:
            status = "fails_endpoint_control"
        elif not no_smuggle:
            status = "fails_no_smuggle"
        else:
            status = "fails_stability"
        rows.append({
            "family": family,
            "declared_f24_family": family in f24,
            "map_definition": definitions[family],
            "output_arity": len(columns),
            "image_size": len(set(values)),
            "G_stability": stability,
            "G_control_QM": qm_control,
            "G_control_GR": gr_control,
            "G_control": control,
            "G_audit": audit,
            "G_nosmuggle": no_smuggle,
            "duplicate_column_pairs": ";".join(f"{a}-{b}" for a, b in duplicates),
            "QM_obstruction_pairs": len(qm_defects),
            "GR_obstruction_pairs": len(gr_defects),
            "partition_equivalent_to_L": collapse,
            "reconciles": reconciles,
            "computed_status": status,
        })
        for index, (state, value) in enumerate(zip(states, values)):
            values_rows.append({
                "family": family,
                "state_index": index,
                "state": "".join(map(str, state)),
                "map_value": json.dumps(value, separators=(",", ":")),
                "q_QM": json.dumps(qm[index], separators=(",", ":")),
                "q_GR": json.dumps(gr[index], separators=(",", ":")),
            })
    summary = {
        "official_family_count": len(official),
        "generated_map_count": len(rows),
        "official_names_match_source": set(official) == set(f24),
        "reconciling_families": [row["family"] for row in rows if row["reconciles"]],
        "distinct_reconciling_families": [row["family"] for row in rows if row["reconciles"] and not row["partition_equivalent_to_L"]],
        "fused_duplicate_detected": next(row for row in rows if row["family"] == "FusedDuplicateControl")["G_nosmuggle"] is False,
    }
    return rows, values_rows, summary


def run() -> dict[str, Any]:
    step22, step25, step26, pins = pinned_dependencies()
    mode_rows, fiber_rows, provenance_checks, provenance_summary = provenance(step25, step26)
    partition_rows, partition_pairs, partition_summary = partition_exhaustion(step22)
    competitor_rows, competitor_values, competitor_summary = generated_competitors(step22)
    return {
        "pins": pins,
        "modes": mode_rows,
        "fibers": fiber_rows,
        "provenance_checks": provenance_checks,
        "provenance": provenance_summary,
        "partitions": partition_rows,
        "partition_pairs": partition_pairs,
        "partition_summary": partition_summary,
        "competitors": competitor_rows,
        "competitor_values": competitor_values,
        "competitor_summary": competitor_summary,
    }
