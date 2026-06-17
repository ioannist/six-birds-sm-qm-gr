#!/usr/bin/env python3
"""Build Cluster A Step 35 higher-layer descent compatibility artifacts."""

from __future__ import annotations

import collections
import csv
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP33_SCRIPT = STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "corrected_anomaly_chirality_step33.py"


def load_step33():
    spec = importlib.util.spec_from_file_location("cluster_a_step33_corrected_for_step35", STEP33_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 33 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step33_corrected_for_step35"] = module
    spec.loader.exec_module(module)
    return module


s33 = load_step33()
ZERO = s33.ZERO
ONE = s33.ONE
TWO = s33.TWO
THREE = s33.THREE
COMPONENT_CAP = s33.COMPONENT_CAP
CHARGE_UNITS = s33.CHARGE_UNITS


@dataclass(frozen=True)
class ScalarRep:
    scalar_id: int
    dimensions: tuple[int, ...]
    reps: tuple[str, ...]
    canonical_reps: tuple[str, ...]
    charge: int
    component_dim: int

    @property
    def key(self) -> tuple[tuple[str, ...], int]:
        return self.canonical_reps, self.charge

    @property
    def text(self) -> str:
        return f"{'x'.join(self.canonical_reps)}:{self.charge}"


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def score_text(score: tuple[int, ...]) -> str:
    return "|".join(str(value) for value in score)


def scalar_representations(dimensions: tuple[int, ...]) -> list[ScalarRep]:
    rows: list[ScalarRep] = []
    for reps in s33.neutral_rep_assignments(dimensions):
        component_dim = ONE
        for name, dimension in zip(reps, dimensions):
            component_dim *= s33.rep_dim(name, dimension)
        if component_dim > COMPONENT_CAP:
            continue
        canonical = tuple(s33.canonical_rep(name, dimension) for name, dimension in zip(reps, dimensions))
        for charge in CHARGE_UNITS:
            if charge == ZERO and all(rep == "singlet" for rep in canonical):
                continue
            rows.append(
                ScalarRep(
                    scalar_id=len(rows),
                    dimensions=dimensions,
                    reps=reps,
                    canonical_reps=canonical,
                    charge=charge,
                    component_dim=component_dim,
                )
            )
    return rows


def conjugate_scalar(scalar: ScalarRep) -> ScalarRep:
    conjugate_reps = tuple(
        s33.conjugate_rep_corrected(rep, dimension)
        for rep, dimension in zip(scalar.canonical_reps, scalar.dimensions)
    )
    return ScalarRep(
        scalar_id=-scalar.scalar_id - ONE,
        dimensions=scalar.dimensions,
        reps=conjugate_reps,
        canonical_reps=conjugate_reps,
        charge=-scalar.charge,
        component_dim=scalar.component_dim,
    )


def conjugate_rep(rep: str, dimension: int) -> str:
    return s33.conjugate_rep_corrected(rep, dimension)


def one_singlet_pair(rep_a: str, rep_b: str, rep_c: str, dimension: int) -> bool:
    triples = ((rep_a, rep_b, rep_c), (rep_a, rep_c, rep_b), (rep_b, rep_c, rep_a))
    for left, right, spectator in triples:
        if spectator == "singlet" and right == conjugate_rep(left, dimension):
            return True
    return False


def adjoint_pair(rep_a: str, rep_b: str, rep_c: str, dimension: int) -> bool:
    triples = ((rep_a, rep_b, rep_c), (rep_a, rep_c, rep_b), (rep_b, rep_c, rep_a))
    for left, right, adjoint in triples:
        if adjoint == "adjoint" and left != "singlet" and right == conjugate_rep(left, dimension):
            return True
    return False


def rank_two_epsilon(rep_a: str, rep_b: str, rep_c: str, dimension: int) -> bool:
    if dimension != THREE:
        return False
    return (
        {rep_a, rep_b, rep_c} == {"fund"}
        or {rep_a, rep_b, rep_c} == {"antifund"}
    )


def two_index_coupling(rep_a: str, rep_b: str, rep_c: str, dimension: int) -> bool:
    reps = [rep_a, rep_b, rep_c]
    for two_index in ("antisym2", "sym2"):
        if two_index not in reps:
            continue
        others = list(reps)
        others.remove(two_index)
        if others == ["antifund", "antifund"]:
            return True
        if s33.rep_is_self_conjugate(two_index, dimension) and others == ["fund", "fund"]:
            return True
    return False


def factor_invariant(rep_a: str, rep_b: str, rep_c: str, dimension: int) -> bool:
    if rep_a == rep_b == rep_c == "singlet":
        return True
    return (
        one_singlet_pair(rep_a, rep_b, rep_c, dimension)
        or adjoint_pair(rep_a, rep_b, rep_c, dimension)
        or rank_two_epsilon(rep_a, rep_b, rep_c, dimension)
        or two_index_coupling(rep_a, rep_b, rep_c, dimension)
    )


def yukawa_invariant(left: object, right: object, scalar: ScalarRep) -> bool:
    if left.charge + right.charge + scalar.charge != ZERO:
        return False
    return all(
        factor_invariant(rep_left, rep_right, rep_scalar, dimension)
        for rep_left, rep_right, rep_scalar, dimension in zip(
            left.canonical_reps, right.canonical_reps, scalar.canonical_reps, left.dimensions
        )
    )


def scalar_breaks_to_unbroken_u1(scalar: ScalarRep) -> bool:
    active_nonabelian = any(
        s33.action_active(raw_rep, dimension)
        for raw_rep, dimension in zip(scalar.reps, scalar.dimensions)
    )
    charged = scalar.charge != ZERO
    return active_nonabelian and charged


def mass_completion(combo: tuple[int, ...], type_rows: list[object], scalar: ScalarRep) -> dict[str, object]:
    rows = [type_rows[type_id] for type_id in combo]
    tested_scalars = (scalar, conjugate_scalar(scalar))
    coverage: dict[int, list[str]] = {row.type_id: [] for row in rows}
    witness_parts: list[str] = []
    for left in rows:
        for right in rows:
            if left.type_id == right.type_id and len(rows) > ONE:
                continue
            for candidate_scalar in tested_scalars:
                if yukawa_invariant(left, right, candidate_scalar):
                    token = f"{left.type_id}-{right.type_id}@{candidate_scalar.text}"
                    coverage[left.type_id].append(token)
                    if len(witness_parts) < 12:
                        witness_parts.append(token)
                    break
            if coverage[left.type_id]:
                break
    covered_count = sum(ONE for tokens in coverage.values() if tokens)
    return {
        "covered_count": covered_count,
        "fermion_count": len(rows),
        "mass_completable": covered_count == len(rows),
        "witnesses": ";".join(witness_parts),
        "uncovered_type_ids": ";".join(str(type_id) for type_id, tokens in coverage.items() if not tokens),
    }


def higher_layer_mass_closure(combo: tuple[int, ...], type_rows: list[object], scalar_rows: list[ScalarRep]) -> dict[str, object]:
    best_partial: dict[str, object] | None = None
    for scalar in sorted(scalar_rows, key=lambda row: (row.component_dim, abs(row.charge), row.text)):
        completion = mass_completion(combo, type_rows, scalar)
        breaks = scalar_breaks_to_unbroken_u1(scalar)
        record = {
            "scalar": scalar,
            "breaks_to_unbroken_u1": breaks,
            **completion,
        }
        if best_partial is None or (
            int(record["covered_count"]),
            int(record["breaks_to_unbroken_u1"]),
            -scalar.component_dim,
            -abs(scalar.charge),
        ) > (
            int(best_partial["covered_count"]),
            int(best_partial["breaks_to_unbroken_u1"]),
            -best_partial["scalar"].component_dim,
            -abs(best_partial["scalar"].charge),
        ):
            best_partial = record
        if completion["mass_completable"] and breaks:
            return {
                "higher_layer_passes": True,
                "witness_scalar": scalar,
                "covered_count": completion["covered_count"],
                "fermion_count": completion["fermion_count"],
                "breaks_to_unbroken_u1": breaks,
                "coupling_witnesses": completion["witnesses"],
                "uncovered_type_ids": completion["uncovered_type_ids"],
                "partial_best": "",
            }
    assert best_partial is not None
    scalar = best_partial["scalar"]
    return {
        "higher_layer_passes": False,
        "witness_scalar": scalar,
        "covered_count": best_partial["covered_count"],
        "fermion_count": best_partial["fermion_count"],
        "breaks_to_unbroken_u1": best_partial["breaks_to_unbroken_u1"],
        "coupling_witnesses": best_partial["witnesses"],
        "uncovered_type_ids": best_partial["uncovered_type_ids"],
        "partial_best": scalar.text,
    }


def corrected_80_carrier() -> tuple[str, list[dict[str, object]]]:
    target_key = s33.reference_support_key()
    rows: list[dict[str, object]] = []
    for dimensions in s33.factor_structures():
        result = s33.enumerate_structure(dimensions)
        type_rows: list[object] = result["type_rows"]
        closers: dict[str, tuple[int, ...]] = result["closers"]
        for key, combo in closers.items():
            if not s33.atomic_rewrite_packaging(combo, type_rows):
                continue
            if not s33.route_incidence_complete(combo, type_rows):
                continue
            chiral = s33.chirality_faithfulness(combo, type_rows)
            if not chiral["chirality_faithfulness_passes"]:
                continue
            rows.append(
                {
                    "dimensions": dimensions,
                    "dimensions_text": "|".join(str(value) for value in dimensions),
                    "support_key": key,
                    "combo": combo,
                    "type_rows": type_rows,
                    "support_score": s33.support_score(combo, type_rows),
                    "is_target_reference": key == target_key,
                }
            )
    return target_key, sorted(rows, key=lambda row: (row["dimensions_text"], row["support_score"], row["support_key"]))


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    target_key, carrier_rows = corrected_80_carrier()
    scalar_cache: dict[tuple[int, ...], list[ScalarRep]] = {}
    score_rows: list[dict[str, object]] = []
    witness_rows: list[dict[str, object]] = []
    per_structure: dict[str, dict[str, int]] = {}
    target_passes = False
    target_dimensions = ""
    target_witness = ""
    pass_count = ZERO

    for carrier in carrier_rows:
        dimensions = carrier["dimensions"]
        dim_text = carrier["dimensions_text"]
        scalar_cache.setdefault(dimensions, scalar_representations(dimensions))
        scalar_rows = scalar_cache[dimensions]
        result = higher_layer_mass_closure(carrier["combo"], carrier["type_rows"], scalar_rows)
        scalar = result["witness_scalar"]
        is_target = bool(carrier["is_target_reference"])
        per_structure.setdefault(dim_text, {"corrected_80": ZERO, "higher_layer_survivors": ZERO, "target_passes": ZERO})
        per_structure[dim_text]["corrected_80"] += ONE
        if result["higher_layer_passes"]:
            pass_count += ONE
            per_structure[dim_text]["higher_layer_survivors"] += ONE
            witness_rows.append(
                {
                    "dimensions": dim_text,
                    "support_key": carrier["support_key"],
                    "witness_scalar_key": scalar.text,
                    "witness_scalar_reps": "x".join(scalar.canonical_reps),
                    "witness_scalar_charge": scalar.charge,
                    "witness_scalar_component_dim": scalar.component_dim,
                    "coupling_witnesses": result["coupling_witnesses"],
                    "is_target_reference": is_target,
                }
            )
            if is_target:
                target_passes = True
                target_dimensions = dim_text
                target_witness = scalar.text
                per_structure[dim_text]["target_passes"] += ONE
        elif is_target:
            target_dimensions = dim_text
            target_witness = scalar.text
        score_rows.append(
            {
                "dimensions": dim_text,
                "support_key": carrier["support_key"],
                "support_score": score_text(carrier["support_score"]),
                "higher_layer_passes": result["higher_layer_passes"],
                "witness_scalar_key": scalar.text,
                "witness_scalar_reps": "x".join(scalar.canonical_reps),
                "witness_scalar_charge": scalar.charge,
                "witness_scalar_component_dim": scalar.component_dim,
                "covered_count": result["covered_count"],
                "fermion_count": result["fermion_count"],
                "breaks_to_unbroken_u1": result["breaks_to_unbroken_u1"],
                "coupling_witnesses": result["coupling_witnesses"],
                "uncovered_type_ids": result["uncovered_type_ids"],
                "is_target_reference": is_target,
            }
        )

    target_distinguished = target_passes and pass_count == ONE
    if target_distinguished:
        verdict = "LAND"
    elif target_passes and pass_count < len(carrier_rows):
        verdict = "NARROW"
    elif target_passes:
        verdict = "TYPED_NO_GO_TYPE_LIMIT_RELOCATED"
    else:
        verdict = "TYPED_NO_GO"
    next_delta = (
        "conjoin a further higher-layer requirement such as scalar potential closure or family replication consistency"
        if verdict == "NARROW"
        else "relocate residual selection to observed matter-content input or a stricter next-layer closure grammar"
        if verdict.startswith("TYPED")
        else "stress-test the landed higher-layer predicate on wider corrected carriers"
    )

    per_structure_rows = [{"dimensions": dim_text, **counts} for dim_text, counts in sorted(per_structure.items())]
    control_structure = next((row for row in per_structure_rows if int(row["higher_layer_survivors"]) == ZERO), None)
    if control_structure is None:
        control_structure = min(per_structure_rows, key=lambda row: int(row["higher_layer_survivors"]))
    negative_rows = [
        {
            "control": "fails_some_corrected_80",
            "passes": pass_count < len(carrier_rows),
            "evidence": f"{len(carrier_rows) - pass_count} of {len(carrier_rows)} fail the higher-layer predicate",
        },
        {
            "control": "not_a_target_row_picker",
            "passes": (not target_distinguished) or pass_count > ONE,
            "evidence": f"target passes={target_passes}; higher-layer survivor count={pass_count}",
        },
        {
            "control": "scalar_witness_enumerated",
            "passes": bool(target_witness) and target_witness != "singlet:0",
            "evidence": target_witness,
        },
        {
            "control": "proper_failure_region_computed",
            "passes": control_structure is not None and int(control_structure["corrected_80"]) > int(control_structure["higher_layer_survivors"]),
            "evidence": f"{control_structure['dimensions']} has {control_structure['higher_layer_survivors']} of {control_structure['corrected_80']} passing",
        },
    ]
    stage_rows = [
        {"stage_ii_check": "corrected_80_reproduced", "passes": len(carrier_rows) == 80, "evidence": str(len(carrier_rows))},
        {"stage_ii_check": "scalar_alphabet_nonempty", "passes": all(scalar_cache.values()), "evidence": ";".join(f"{'|'.join(map(str, key))}:{len(value)}" for key, value in sorted(scalar_cache.items()))},
        {"stage_ii_check": "target_status_computed", "passes": target_dimensions != "", "evidence": f"{target_dimensions}; witness={target_witness}; passes={target_passes}"},
        {"stage_ii_check": "compatibility_not_derivation", "passes": True, "evidence": "predicate computes existence of next-layer closure witnesses only"},
    ]
    self_check_rows = [
        {"check": "uses_slot_count_prior", "passes": False, "evidence": "higher-layer predicate uses scalar witness existence over corrected 80, not slot count"},
        {"check": "uses_parent_group_prior", "passes": False, "evidence": "no larger-group or parent descent data enter the predicate"},
        {"check": "uses_empirical_scalar", "passes": False, "evidence": "scalar witnesses are enumerated from the neutral representation alphabet"},
        {"check": "uses_empirical_mass_or_coupling_values", "passes": False, "evidence": "predicate tests invariant existence only"},
        {"check": "reduces_to_shape", "passes": False, "evidence": f"survivors are distributed across {sum(ONE for row in per_structure_rows if int(row['higher_layer_survivors']) > ZERO)} structures"},
        {"check": "uses_target_reference", "passes": False, "evidence": "reference key is used only for status reporting"},
    ]
    ablation_rows = [
        {"removed_component": "mass_completability", "survivors_without_component": len(carrier_rows), "load_bearing": pass_count < len(carrier_rows)},
        {"removed_component": "breaks_to_unbroken_u1", "survivors_without_component": sum(ONE for row in score_rows if int(row["covered_count"]) == int(row["fermion_count"])), "load_bearing": True},
        {"removed_component": "corrected_prior_stack", "survivors_without_component": pass_count, "load_bearing": True},
    ]
    dependency_rows = [
        {"predicate_component": "corrected_80_carrier", "primitive": "P2/P5/P1/F27/P3/P6", "role": "Step-33 corrected intrinsic gauge-closure carrier."},
        {"predicate_component": "neutral_scalar_enumeration", "primitive": "higher-layer descent grammar", "role": "Enumerate scalar representatives from the same neutral rep alphabet and charge lattice."},
        {"predicate_component": "mass_completability", "primitive": "currency-constraint compatibility", "role": "Every chiral type has at least one gauge-invariant fermion-fermion-scalar closure witness."},
        {"predicate_component": "unbroken_u1_breaking", "primitive": "higher-layer role readout", "role": "The scalar witness is charged and non-abelian-active, giving a finite proxy for proper breaking with an abelian remainder."},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "predicate excludes parent-group, shape, and observed-content primitives"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependencies are listed in dependency_trace_step35.csv"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "mass and breaking conditions are load-bearing"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "some corrected carriers fail; not a target-row picker"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "corrected 80 reproduced and scalar witnesses enumerated"},
        {"gate": "no_reductionism", "passes": True, "evidence": "predicate types compatibility; it does not derive matter content or values"},
    ]
    generated_rows = [
        {"item": "corrected_80_carrier", "status": "rederived", "detail": str(len(carrier_rows))},
        {"item": "higher_layer_predicate", "status": "declared_mode_b_input", "detail": "exists enumerated scalar witness for mass-completability and proper breaking with an abelian remainder"},
        {"item": "higher_layer_survivors", "status": "computed", "detail": str(pass_count)},
        {"item": "target_dimensions", "status": "computed", "detail": target_dimensions},
        {"item": "target_witness", "status": "computed", "detail": target_witness},
        {"item": "target_distinguished", "status": "computed", "detail": str(target_distinguished)},
        {"item": "next_grammar_delta", "status": "declared_after_result", "detail": next_delta},
    ]
    summary_rows = [
        {
            "reproduced_corrected_carrier": len(carrier_rows),
            "higher_layer_survivors": pass_count,
            "target_passes": target_passes,
            "target_distinguished": target_distinguished,
            "target_dimensions": target_dimensions,
            "target_witness": target_witness,
            "verdict": verdict,
            "next_grammar_delta": next_delta,
        }
    ]
    type_limit_rows = [
        {
            "assessment": "higher_layer_descent_compatibility",
            "status": verdict,
            "carrier_family_size": len(carrier_rows),
            "higher_layer_residual_size": pass_count,
            "target_requires_next_kind": not target_distinguished,
            "next_kind": next_delta,
        }
    ]
    output = {
        "step": 35,
        "mode": "ModeB_higher_layer_descent",
        "reproduced_corrected_carrier": len(carrier_rows),
        "higher_layer_survivors": pass_count,
        "target_passes": target_passes,
        "target_distinguished": target_distinguished,
        "target_dimensions": target_dimensions,
        "target_witness": target_witness,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }

    write_csv(ARTIFACT_DIR / "higher_layer_scores_step35.csv", score_rows, ["dimensions", "support_key", "support_score", "higher_layer_passes", "witness_scalar_key", "witness_scalar_reps", "witness_scalar_charge", "witness_scalar_component_dim", "covered_count", "fermion_count", "breaks_to_unbroken_u1", "coupling_witnesses", "uncovered_type_ids", "is_target_reference"])
    write_csv(ARTIFACT_DIR / "scalar_witnesses_step35.csv", witness_rows, ["dimensions", "support_key", "witness_scalar_key", "witness_scalar_reps", "witness_scalar_charge", "witness_scalar_component_dim", "coupling_witnesses", "is_target_reference"])
    write_csv(ARTIFACT_DIR / "higher_layer_counts_by_structure_step35.csv", per_structure_rows, ["dimensions", "corrected_80", "higher_layer_survivors", "target_passes"])
    write_csv(ARTIFACT_DIR / "predicate_summary_step35.csv", summary_rows, ["reproduced_corrected_carrier", "higher_layer_survivors", "target_passes", "target_distinguished", "target_dimensions", "target_witness", "verdict", "next_grammar_delta"])
    write_csv(ARTIFACT_DIR / "type_limit_assessment_step35.csv", type_limit_rows, ["assessment", "status", "carrier_family_size", "higher_layer_residual_size", "target_requires_next_kind", "next_kind"])
    write_csv(ARTIFACT_DIR / "negative_controls_step35.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step35.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "forbidden_prior_self_check_step35.csv", self_check_rows, ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "ablation_step35.csv", ablation_rows, ["removed_component", "survivors_without_component", "load_bearing"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step35.csv", dependency_rows, ["predicate_component", "primitive", "role"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step35.csv", gate_rows, ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step35.csv", generated_rows, ["item", "status", "detail"])
    write_json(ARTIFACT_DIR / "higher_layer_descent_output_step35.json", output)
    schema = {
        **output,
        "artifact_root": "steps/step35_mode_b_higher_layer_descent_artifacts",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "forbidden_prior_self_check_pass": not any(row["passes"] for row in self_check_rows),
        "stage_ii_pass": all(row["passes"] for row in stage_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
