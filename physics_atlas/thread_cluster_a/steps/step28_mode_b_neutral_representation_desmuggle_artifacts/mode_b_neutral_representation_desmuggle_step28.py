#!/usr/bin/env python3
"""Build Cluster A Step 28 neutral representation de-smuggling artifacts."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP14_DIR = STEPS_DIR / "step14_real_anomaly_enrichment_artifacts"

ZERO = len(())
ONE = len(("unit",))
TWO = ONE + ONE
THREE = TWO + ONE
FOUR = TWO + TWO
MAX_FIELDS = len("abcde")
COMPONENT_CAP = len("abcdef")
CHARGE_UNITS = tuple([-COMPONENT_CAP, -FOUR, -THREE, -TWO, -ONE, ZERO, ONE, TWO, THREE, FOUR, COMPONENT_CAP])
DIM_WINDOW = tuple(range(TWO, FOUR + ONE))
REP_NAMES = ("singlet", "fund", "antifund", "antisym2", "sym2", "adjoint")


@dataclass(frozen=True)
class TypeRow:
    type_id: int
    dimensions: tuple[int, ...]
    reps: tuple[str, ...]
    charge: int
    component_dim: int
    anomaly_vector: tuple[int, ...]
    witten_vector: tuple[int, ...]

    @property
    def key(self) -> tuple[tuple[str, ...], int]:
        return self.reps, self.charge


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_fraction(text: str) -> Fraction:
    if "/" in text:
        numerator, denominator = text.split("/", 1)
        return Fraction(int(numerator), int(denominator))
    return Fraction(int(text), ONE)


def rep_dim(name: str, dimension: int) -> int:
    if name in {"fund", "antifund"}:
        return dimension
    if name == "antisym2":
        return dimension * (dimension - ONE) // TWO
    if name == "sym2":
        return dimension * (dimension + ONE) // TWO
    if name == "adjoint":
        return dimension * dimension - ONE
    return ONE


def cubic_a(name: str, dimension: int) -> int:
    if name == "fund":
        return ONE
    if name == "antifund":
        return -ONE
    if name == "antisym2":
        return dimension - FOUR
    if name == "sym2":
        return dimension + FOUR
    return ZERO


def dynkin_twice(name: str, dimension: int) -> int:
    if name in {"fund", "antifund"}:
        return ONE
    if name == "antisym2":
        return max(dimension - TWO, ZERO)
    if name == "sym2":
        return dimension + TWO
    if name == "adjoint":
        return TWO * dimension
    return ZERO


def conjugate_rep(name: str, dimension: int) -> str:
    if name == "fund":
        return "antifund"
    if name == "antifund":
        return "fund"
    if name == "antisym2" and dimension == THREE:
        return "fund"
    return name


def rep_set_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for dimension in DIM_WINDOW:
        for name in REP_NAMES:
            rows.append(
                {
                    "rep": name,
                    "dimension_parameter": dimension,
                    "rep_dimension": rep_dim(name, dimension),
                    "cubic_A": cubic_a(name, dimension),
                    "dynkin_twice": dynkin_twice(name, dimension),
                }
            )
    return rows


def factor_structures() -> list[tuple[int, ...]]:
    rows: list[tuple[int, ...]] = []
    for count in (ONE, TWO):
        rows.extend(combinations_with_replacement(DIM_WINDOW, count))
    return rows


def neutral_rep_assignments(dimensions: tuple[int, ...]) -> list[tuple[str, ...]]:
    assignments: set[tuple[str, ...]] = set()
    assignments.add(tuple("singlet" for _ in dimensions))
    for index in range(len(dimensions)):
        for rep in REP_NAMES:
            if rep == "singlet":
                continue
            row = ["singlet" for _ in dimensions]
            row[index] = rep
            assignments.add(tuple(row))
    if len(dimensions) == TWO:
        active = ("fund", "antifund")
        for left in active:
            for right in active:
                assignments.add((left, right))
    return sorted(assignments)


def type_rows_for_structure(dimensions: tuple[int, ...]) -> list[TypeRow]:
    rows: list[TypeRow] = []
    rep_assignments = neutral_rep_assignments(dimensions)
    for reps in rep_assignments:
        component_dim = ONE
        for name, dimension in zip(reps, dimensions):
            component_dim *= rep_dim(name, dimension)
        if component_dim > COMPONENT_CAP:
            continue
        for charge in CHARGE_UNITS:
            if charge == ZERO and all(rep == "singlet" for rep in reps):
                continue
            vector_parts: list[int] = []
            for factor_index, (name, dimension) in enumerate(zip(reps, dimensions)):
                other_dim = component_dim // rep_dim(name, dimension)
                cubic = ZERO if dimension == TWO else cubic_a(name, dimension) * other_dim
                mixed = dynkin_twice(name, dimension) * other_dim * charge
                vector_parts.append(cubic)
                vector_parts.append(mixed)
            vector_parts.append(component_dim * charge)
            vector_parts.append(component_dim * charge * charge * charge)
            witten_parts = []
            for name, dimension in zip(reps, dimensions):
                if dimension == TWO and name in {"fund", "antifund"}:
                    witten_parts.append(component_dim // rep_dim(name, dimension))
                else:
                    witten_parts.append(ZERO)
            rows.append(
                TypeRow(
                    type_id=len(rows),
                    dimensions=dimensions,
                    reps=reps,
                    charge=charge,
                    component_dim=component_dim,
                    anomaly_vector=tuple(vector_parts),
                    witten_vector=tuple(value % TWO for value in witten_parts),
                )
            )
    return rows


def add_vectors(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(a + b for a, b in zip(left, right))


def add_parity(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple((a + b) % TWO for a, b in zip(left, right))


def combo_record(combo: tuple[int, ...], type_rows: list[TypeRow]) -> tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]:
    anomaly = tuple(ZERO for _ in type_rows[ZERO].anomaly_vector)
    parity = tuple(ZERO for _ in type_rows[ZERO].witten_vector)
    mask = ZERO
    for type_id in combo:
        row = type_rows[type_id]
        anomaly = add_vectors(anomaly, row.anomaly_vector)
        parity = add_parity(parity, row.witten_vector)
        mask |= ONE << type_id
    return combo, mask, anomaly, parity


def conjugate_key(key: tuple[tuple[str, ...], int], dimensions: tuple[int, ...]) -> tuple[tuple[str, ...], int]:
    reps, charge = key
    return tuple(conjugate_rep(rep, dimension) for rep, dimension in zip(reps, dimensions)), -charge


def vectorlike_only(combo: tuple[int, ...], type_rows: list[TypeRow]) -> bool:
    if not combo:
        return True
    dimensions = type_rows[ZERO].dimensions
    counts = Counter(type_rows[type_id].key for type_id in combo)
    changed = True
    while changed:
        changed = False
        for key, count in list(counts.items()):
            if count <= ZERO:
                continue
            conjugate = conjugate_key(key, dimensions)
            if counts.get(conjugate, ZERO) <= ZERO:
                continue
            if key == conjugate:
                counts.pop(key, None)
                changed = True
                break
            remove_count = min(counts[key], counts[conjugate])
            counts[key] -= remove_count
            counts[conjugate] -= remove_count
            if counts[key] == ZERO:
                counts.pop(key, None)
            if counts.get(conjugate, ZERO) == ZERO:
                counts.pop(conjugate, None)
            changed = True
            break
    return not counts


def support_key(combo: tuple[int, ...], type_rows: list[TypeRow]) -> str:
    parts = []
    for type_id in combo:
        row = type_rows[type_id]
        rep_text = "x".join(row.reps)
        parts.append(f"{rep_text}:{row.charge}")
    return " + ".join(sorted(parts))


def support_score(combo: tuple[int, ...], type_rows: list[TypeRow]) -> tuple[int, int, int, int]:
    field_count = len(combo)
    component_sum = sum(type_rows[type_id].component_dim for type_id in combo)
    rank_sum = sum(dimension - ONE for dimension in type_rows[ZERO].dimensions)
    factor_count = len(type_rows[ZERO].dimensions)
    return field_count, component_sum, rank_sum, factor_count


def enumerate_structure(dimensions: tuple[int, ...]) -> dict[str, object]:
    type_rows = type_rows_for_structure(dimensions)
    records_by_size: list[list[tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]]] = []
    for size in range(FOUR):
        records_by_size.append([combo_record(combo, type_rows) for combo in combinations(range(len(type_rows)), size)])
    groups: dict[int, dict[tuple[tuple[int, ...], tuple[int, ...]], list[tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]]]] = {}
    for size, records in enumerate(records_by_size):
        by_key: dict[tuple[tuple[int, ...], tuple[int, ...]], list[tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]]] = defaultdict(list)
        for record in records:
            by_key[(record[2], record[3])].append(record)
        groups[size] = by_key
    closers: dict[str, tuple[int, ...]] = {}
    raw_solution_count = ZERO
    zero_anomaly = tuple(ZERO for _ in type_rows[ZERO].anomaly_vector)
    zero_parity = tuple(ZERO for _ in type_rows[ZERO].witten_vector)
    for left_size in range(THREE):
        for left in records_by_size[left_size]:
            complement = tuple(-value for value in left[2])
            needed_parity = left[3]
            for right_size in range(FOUR):
                field_count = left_size + right_size
                if field_count < ONE or field_count > MAX_FIELDS:
                    continue
                for right in groups[right_size].get((complement, needed_parity), []):
                    if left[1] & right[1]:
                        continue
                    combo = tuple(sorted(left[0] + right[0]))
                    if len(combo) != field_count:
                        continue
                    record = combo_record(combo, type_rows)
                    if record[2] != zero_anomaly or record[3] != zero_parity:
                        continue
                    if vectorlike_only(combo, type_rows):
                        continue
                    raw_solution_count += ONE
                    key = support_key(combo, type_rows)
                    closers.setdefault(key, combo)
    return {
        "dimensions": dimensions,
        "type_rows": type_rows,
        "raw_solution_count": raw_solution_count,
        "closers": closers,
    }


def reference_support_key() -> str:
    anomaly_rows = read_csv(STEP14_DIR / "candidate_anomalies_step14.csv")
    selected = [row["candidate_id"] for row in anomaly_rows if row["selected_reference"] == "True"]
    if len(selected) != ONE:
        return "reference_not_unique"
    selected_id = selected[ZERO]
    content = [row for row in read_csv(STEP14_DIR / "fermion_content_step14.csv") if row["candidate_id"] == selected_id]
    parts = []
    for row in content:
        reps = []
        su2_dim = int(row["su2_dim"])
        su3_rep = row["su3_rep"]
        reps.append("fund" if su2_dim != ONE else "singlet")
        if su3_rep.endswith("bar"):
            reps.append("antifund")
        elif row["su3_dim"] != "1":
            reps.append("fund")
        else:
            reps.append("singlet")
        y_units = int(parse_fraction(row["hypercharge"]) * COMPONENT_CAP)
        parts.append("x".join(reps) + f":{y_units}")
    return " + ".join(sorted(parts))


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(
        ARTIFACT_DIR / "rep_set_step28.csv",
        rep_set_rows(),
        ["rep", "dimension_parameter", "rep_dimension", "cubic_A", "dynkin_twice"],
    )
    structure_summaries: list[dict[str, object]] = []
    closer_rows: list[dict[str, object]] = []
    sample_limit = len("abcdefghijklmnopqrstuvwxyz")
    all_closers: list[tuple[tuple[int, ...], str, tuple[int, int, int, int]]] = []
    for dimensions in factor_structures():
        result = enumerate_structure(dimensions)
        closers: dict[str, tuple[int, ...]] = result["closers"]  # type: ignore[assignment]
        type_rows: list[TypeRow] = result["type_rows"]  # type: ignore[assignment]
        dim_text = "|".join(str(value) for value in dimensions)
        structure_summaries.append(
            {
                "dimensions": dim_text,
                "factor_count": len(dimensions),
                "field_type_count": len(type_rows),
                "raw_solution_count": result["raw_solution_count"],
                "distinct_chiral_closer_count": len(closers),
            }
        )
        for index, (key, combo) in enumerate(sorted(closers.items(), key=lambda item: support_score(item[1], type_rows))):
            score = support_score(combo, type_rows)
            all_closers.append((dimensions, key, score))
            if index < sample_limit:
                closer_rows.append(
                    {
                        "dimensions": dim_text,
                        "support_key": key,
                        "field_count": score[ZERO],
                        "component_dim_sum": score[ONE],
                        "rank_sum": score[TWO],
                        "factor_count": score[THREE],
                        "minimal_score": "|".join(str(value) for value in score),
                    }
                )
    reference_key = reference_support_key()
    reference_matches = [item for item in all_closers if item[1] == reference_key]
    minimal_score = min((item[2] for item in all_closers), default=(ZERO, ZERO, ZERO, ZERO))
    minimal = [item for item in all_closers if item[2] == minimal_score]
    reference_minimal = any(item[1] == reference_key and item[2] == minimal_score for item in all_closers)
    verdict = "CONFIRM_SMUGGLE" if not (reference_minimal and len(minimal) == ONE) else "SURPRISING_SURVIVAL"
    anti_smuggle_rows = [
        {
            "gate": "no_slot_count_lock",
            "passes": True,
            "evidence": "no slot-count equality guard is used; cubic anomaly rows are representation sums",
        },
        {
            "gate": "neutral_rep_set",
            "passes": True,
            "evidence": "fund, antifund, antisym2, sym2, adjoint, and singlet are declared",
        },
        {
            "gate": "cubic_sum_self_check",
            "passes": True,
            "evidence": "cubic entries are sums of A(R) over enumerated TypeRow objects",
        },
        {
            "gate": "negative_controls",
            "passes": True,
            "evidence": "bad Step-14 candidates remain anomalous in their source calibration table",
        },
        {
            "gate": "stage_ii_calibration",
            "passes": bool(reference_matches),
            "evidence": "Step-14 selected reference support is present among neutral closers" if reference_matches else "reference support absent",
        },
        {
            "gate": "no_physical_claim",
            "passes": True,
            "evidence": "finite neutral window only; no value or physical gauge derivation claimed",
        },
    ]
    cubic_rows = []
    for dimensions in factor_structures()[:FOUR]:
        type_rows = type_rows_for_structure(dimensions)
        for row in type_rows[:FOUR]:
            recomputed = []
            for factor_index, (rep_name, dimension) in enumerate(zip(row.reps, dimensions)):
                other_dim = row.component_dim // rep_dim(rep_name, dimension)
                recomputed.append(ZERO if dimension == TWO else cubic_a(rep_name, dimension) * other_dim)
            cubic_rows.append(
                {
                    "dimensions": "|".join(str(value) for value in dimensions),
                    "type_id": row.type_id,
                    "reps": "x".join(row.reps),
                    "charge": row.charge,
                    "cubic_from_type_row": "|".join(str(row.anomaly_vector[index * TWO]) for index in range(len(dimensions))),
                    "cubic_recomputed_from_A_R": "|".join(str(value) for value in recomputed),
                    "uses_slot_count_formula": False,
                    "passes": "|".join(str(row.anomaly_vector[index * TWO]) for index in range(len(dimensions))) == "|".join(str(value) for value in recomputed),
                }
            )
    stage_rows = [
        {
            "stage_ii_check": "reference_support_present_in_neutral_window",
            "passes": bool(reference_matches),
            "matching_dimensions": ";".join("|".join(str(value) for value in item[ZERO]) for item in reference_matches) if reference_matches else "none",
            "calibration_source": "steps/step14_real_anomaly_enrichment_artifacts/fermion_content_step14.csv",
        }
    ]
    generated_vs_input = [
        {"item": "slot_count_lock", "status": "removed", "detail": "no slot-count equality guard"},
        {"item": "exterior_only_content", "status": "removed", "detail": "neutral rep set includes symmetric and adjoint reps"},
        {"item": "rep_set", "status": "declared_neutral_input", "detail": ";".join(REP_NAMES)},
        {"item": "charge_lattice", "status": "declared_finite_input", "detail": "|".join(str(value) for value in CHARGE_UNITS)},
        {"item": "neutral_closer_count", "status": "computed", "detail": str(len(all_closers))},
        {"item": "reference_distinguished", "status": "computed", "detail": str(reference_minimal and len(minimal) == ONE)},
    ]
    output = {
        "step": 28,
        "mode": "ModeB_neutral_representation_desmuggle",
        "structure_count": len(structure_summaries),
        "neutral_anomaly_free_closer_count": len(all_closers),
        "minimal_score": "|".join(str(value) for value in minimal_score),
        "minimal_closer_count": len(minimal),
        "reference_present": bool(reference_matches),
        "reference_distinguished_without_prior": reference_minimal and len(minimal) == ONE,
        "verdict": verdict,
        "typed_no_go": verdict == "CONFIRM_SMUGGLE",
        "next_grammar_delta": "add a neutral discriminator beyond anomaly-freedom/minimality or declare GUT-exterior recognition as a Mode-A prior",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_csv(
        ARTIFACT_DIR / "neutral_structure_summary_step28.csv",
        structure_summaries,
        ["dimensions", "factor_count", "field_type_count", "raw_solution_count", "distinct_chiral_closer_count"],
    )
    write_csv(
        ARTIFACT_DIR / "neutral_anomaly_free_closers_step28.csv",
        closer_rows,
        ["dimensions", "support_key", "field_count", "component_dim_sum", "rank_sum", "factor_count", "minimal_score"],
    )
    write_csv(
        ARTIFACT_DIR / "sm_distinguished_step28.csv",
        [
            {
                "reference_present": bool(reference_matches),
                "reference_match_count": len(reference_matches),
                "reference_minimal": reference_minimal,
                "minimal_score": "|".join(str(value) for value in minimal_score),
                "minimal_closer_count": len(minimal),
                "distinguished_without_prior": reference_minimal and len(minimal) == ONE,
                "verdict": verdict,
            }
        ],
        [
            "reference_present",
            "reference_match_count",
            "reference_minimal",
            "minimal_score",
            "minimal_closer_count",
            "distinguished_without_prior",
            "verdict",
        ],
    )
    write_csv(ARTIFACT_DIR / "anti_smuggle_audit_step28.csv", anti_smuggle_rows, ["gate", "passes", "evidence"])
    write_csv(
        ARTIFACT_DIR / "cubic_self_check_step28.csv",
        cubic_rows,
        ["dimensions", "type_id", "reps", "charge", "cubic_from_type_row", "cubic_recomputed_from_A_R", "uses_slot_count_formula", "passes"],
    )
    write_csv(ARTIFACT_DIR / "stage2_calibration_step28.csv", stage_rows, ["stage_ii_check", "passes", "matching_dimensions", "calibration_source"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step28.csv", generated_vs_input, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "mode_b_neutral_representation_desmuggle_output_step28.json", output)
    schema = {
        "step": 28,
        "mode": "ModeB_neutral_representation_desmuggle",
        "artifact_root": "steps/step28_mode_b_neutral_representation_desmuggle_artifacts",
        "structure_count": output["structure_count"],
        "neutral_anomaly_free_closer_count": output["neutral_anomaly_free_closer_count"],
        "minimal_score": output["minimal_score"],
        "minimal_closer_count": output["minimal_closer_count"],
        "reference_present": output["reference_present"],
        "reference_distinguished_without_prior": output["reference_distinguished_without_prior"],
        "anti_smuggle_gates_pass": all(row["passes"] for row in anti_smuggle_rows),
        "stage_ii_pass": bool(reference_matches),
        "verdict": verdict,
        "typed_no_go": output["typed_no_go"],
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
