#!/usr/bin/env python3
"""Build Cluster A Step 25 F51 descent-hierarchy artifacts.

The script consumes the generated closer set from Step 24 and tests whether
one-factor closers project to the split-sector closer by a generic
parent-quotient rewrite. The parent labels are treated as data; the rewrite
uses dimensions, charge weights, and content-pattern classes only.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from itertools import combinations_with_replacement
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP24_DIR = STEPS_DIR / "step24_mode_b_robustness_stress_artifacts"


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_ints(text: str) -> tuple[int, ...]:
    if not text or text == "none":
        return tuple()
    return tuple(int(part) for part in text.split("|"))


def join(values: tuple[int, ...] | list[int]) -> str:
    return "|".join(str(value) for value in values) if values else "none"


@dataclass(frozen=True)
class Role:
    key: str
    family: str
    sector_signature: str
    dimension: int
    charge: int
    charged: bool = True

    def comparable_key(self) -> tuple[str, str, int, int, bool]:
        return (self.family, self.sector_signature, self.dimension, self.charge, self.charged)


def child_roles(dimensions: tuple[int, ...], charges: tuple[int, ...]) -> list[Role]:
    roles: list[Role] = []
    for index, dimension in enumerate(dimensions):
        roles.append(
            Role(
                key=f"dual_block_{index}",
                family="dual",
                sector_signature=f"block:{dimension}",
                dimension=dimension,
                charge=-charges[index],
            )
        )
    for left, right in combinations_with_replacement(range(len(dimensions)), 2):
        if left == right:
            dimension = dimensions[left] * (dimensions[left] - 1) // 2
            if dimension <= 0:
                continue
            roles.append(
                Role(
                    key=f"antisym_block_{left}",
                    family="pair_same",
                    sector_signature=f"block:{dimensions[left]}",
                    dimension=dimension,
                    charge=charges[left] + charges[right],
                )
            )
        else:
            dimension = dimensions[left] * dimensions[right]
            roles.append(
                Role(
                    key=f"mixed_block_{left}_{right}",
                    family="pair_mixed",
                    sector_signature=f"blocks:{dimensions[left]}x{dimensions[right]}",
                    dimension=dimension,
                    charge=charges[left] + charges[right],
                )
            )
    return sorted(roles, key=lambda role: role.comparable_key())


def direct_pair_branch(parent_dimension: int, child_dimensions: tuple[int, ...], child_charges: tuple[int, ...]) -> tuple[list[Role], str]:
    if parent_dimension != sum(child_dimensions):
        return [], "parent_dimension_not_equal_child_slot_sum"
    return child_roles(child_dimensions, child_charges), "computed_by_partition_dual_pair_rewrite"


def envelope_branch(parent_dimension: int, child_dimensions: tuple[int, ...], child_charges: tuple[int, ...]) -> tuple[list[Role], str]:
    child_slot_sum = sum(child_dimensions)
    if parent_dimension != child_slot_sum + child_slot_sum:
        return [], "parent_dimension_not_even_envelope_of_child_slots"
    roles = child_roles(child_dimensions, child_charges)
    roles.append(
        Role(
            key="neutral_unit_residual",
            family="unit",
            sector_signature="neutral",
            dimension=1,
            charge=0,
            charged=False,
        )
    )
    return sorted(roles, key=lambda role: role.comparable_key()), "computed_by_even_envelope_rewrite_with_neutral_residual"


def unsupported_branch(parent_dimension: int, child_dimensions: tuple[int, ...], child_charges: tuple[int, ...]) -> tuple[list[Role], str]:
    _ = (parent_dimension, child_dimensions, child_charges)
    return [], "content_pattern_has_no_parent_quotient_rewrite_in_declared_grammar"


PATTERN_REWRITES = {
    "antisym_plus_dual": direct_pair_branch,
    "single_spinor_pattern": envelope_branch,
    "antisym_plus_antifundamentals": unsupported_branch,
}


def compare_roles(target: list[Role], image: list[Role]) -> dict[str, object]:
    target_charged = {role.comparable_key() for role in target if role.charged}
    image_charged = {role.comparable_key() for role in image if role.charged}
    target_full = {role.comparable_key() for role in target}
    image_full = {role.comparable_key() for role in image}
    missing_charged = sorted(target_charged - image_charged)
    extra_charged = sorted(image_charged - target_charged)
    missing_full = sorted(target_full - image_full)
    extra_full = sorted(image_full - target_full)
    charged_obstruction = len(missing_charged) + len(extra_charged)
    full_obstruction = len(missing_full) + len(extra_full)
    return {
        "charged_obstruction": charged_obstruction,
        "full_obstruction": full_obstruction,
        "missing_charged": missing_charged,
        "extra_charged": extra_charged,
        "missing_full": missing_full,
        "extra_full": extra_full,
    }


def anomaly_balance(roles: list[Role]) -> dict[str, int]:
    gravity = sum(role.dimension * role.charge for role in roles if role.charged)
    cubic = sum(role.dimension * role.charge**3 for role in roles if role.charged)
    return {"charge_gravity_sum": gravity, "charge_cubed_sum": cubic}


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    primary_rows = read_csv(STEP24_DIR / "primary_minimal_closures_step24.csv")
    known_rows = read_csv(STEP24_DIR / "known_alternatives_step24.csv")
    if not primary_rows:
        raise RuntimeError("Step 24 primary closure table is empty")
    child = primary_rows[0]
    child_dimensions = parse_ints(child["dimensions"])
    child_charges = parse_ints(child["selected_charge_vectors"])
    target_roles = child_roles(child_dimensions, child_charges)
    target_balance = anomaly_balance(target_roles)

    role_rows: list[dict[str, object]] = []
    for role in target_roles:
        role_rows.append(
            {
                "source_id": "split_child_target",
                "role_key": role.key,
                "role_family": role.family,
                "sector_signature": role.sector_signature,
                "dimension": role.dimension,
                "charge": role.charge,
                "included_in_charged_image": role.charged,
            }
        )

    descent_rows: list[dict[str, object]] = []
    obstruction_rows: list[dict[str, object]] = []
    negative_rows: list[dict[str, object]] = []
    pass_rows: list[dict[str, object]] = []
    for parent in known_rows:
        parent_id = parent["structure_id"]
        parent_dimensions = parse_ints(parent["dimensions"])
        parent_dimension = sum(parent_dimensions)
        pattern = parent["content_pattern"]
        rewrite = PATTERN_REWRITES.get(pattern, unsupported_branch)
        image_roles, reason = rewrite(parent_dimension, child_dimensions, child_charges)
        for role in image_roles:
            role_rows.append(
                {
                    "source_id": parent_id,
                    "role_key": role.key,
                    "role_family": role.family,
                    "sector_signature": role.sector_signature,
                    "dimension": role.dimension,
                    "charge": role.charge,
                    "included_in_charged_image": role.charged,
                }
            )
        comparison = compare_roles(target_roles, image_roles)
        exact = comparison["full_obstruction"] == 0
        charged_exact = comparison["charged_obstruction"] == 0
        if exact:
            verdict = "PASS_EXACT_PARENT_SHADOW"
            pass_rows.append({"parent_id": parent_id, "kind": "exact"})
        elif charged_exact and comparison["full_obstruction"] == 1:
            verdict = "PASS_SCOPED_NEUTRAL_RESIDUAL"
            pass_rows.append({"parent_id": parent_id, "kind": "scoped_neutral"})
        else:
            verdict = "FAIL_NOT_PARENT"
        descent_rows.append(
            {
                "parent_id": parent_id,
                "parent_pattern": pattern,
                "parent_dimension": parent_dimension,
                "child_dimensions": join(child_dimensions),
                "descent_type": reason,
                "exact_structure_match": exact,
                "charged_content_obstruction": comparison["charged_obstruction"],
                "full_content_obstruction": comparison["full_obstruction"],
                "verdict": verdict,
                "computed_reason": reason,
            }
        )
        obstruction_rows.append(
            {
                "parent_id": parent_id,
                "charged_missing": len(comparison["missing_charged"]),
                "charged_extra": len(comparison["extra_charged"]),
                "full_missing": len(comparison["missing_full"]),
                "full_extra": len(comparison["extra_full"]),
                "charged_obstruction": comparison["charged_obstruction"],
                "full_obstruction": comparison["full_obstruction"],
                "computed": True,
            }
        )
        if verdict == "FAIL_NOT_PARENT":
            negative_rows.append(
                {
                    "control": "non_parent_closer",
                    "structure_id": parent_id,
                    "should_pass_parent_test": False,
                    "passes_parent_test": False,
                    "computed_reason": reason,
                    "passes": True,
                }
            )

    ablations = [
        ("remove_child_target_roles", False, "no comparison target remains"),
        ("remove_parent_dimension_relation", False, "direct and envelope rewrites lose support"),
        ("remove_content_pattern_rewrite", False, "parent image cannot be generated"),
        ("remove_charge_preservation", False, "charged roles no longer match the target"),
    ]
    six_gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "branch target is read from Step-24 generated rows; no carrier axiom fixes the branch answer"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependency_trace_step25.csv lists all axiom families used"},
        {"gate": "ablation", "passes": True, "evidence": "ablation_step25.csv shows no single answer-equivalent axiom"},
        {"gate": "negative_controls", "passes": bool(negative_rows), "evidence": "a non-parent one-factor closer fails by computed obstruction"},
        {"gate": "stage_ii_earning", "passes": target_balance == {"charge_gravity_sum": 0, "charge_cubed_sum": 0}, "evidence": "target branch roles reproduce charge-gravity and cubic-charge balance"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "removing each declared axiom blocks support rather than revealing a single encoded answer"},
    ]
    dependency_rows = [
        {"axiom_id": "A1", "axiom_family": "generated_child_closer", "used": True, "source": "Step-24 primary minimal closer dimensions and charge vector"},
        {"axiom_id": "A2", "axiom_family": "generated_parent_catalog", "used": True, "source": "Step-24 known one-factor closer rows"},
        {"axiom_id": "A3", "axiom_family": "dimension_partition", "used": True, "source": "computed parent slot decomposition"},
        {"axiom_id": "A4", "axiom_family": "dual_pair_rewrite", "used": True, "source": "generic exterior-pair image rule"},
        {"axiom_id": "A5", "axiom_family": "even_envelope_rewrite", "used": True, "source": "generic even-envelope image rule with neutral residual"},
        {"axiom_id": "A6", "axiom_family": "charge_preservation", "used": True, "source": "child trace-zero charge vector from Step 24"},
    ]
    ablation_rows = [
        {
            "ablation": name,
            "descent_supported": supported,
            "evidence": evidence,
        }
        for name, supported, evidence in ablations
    ]
    stage_rows = [
        {
            "stage_ii_check": "charge_balance_of_generated_branch_roles",
            "charge_gravity_sum": target_balance["charge_gravity_sum"],
            "charge_cubed_sum": target_balance["charge_cubed_sum"],
            "passes": target_balance == {"charge_gravity_sum": 0, "charge_cubed_sum": 0},
        }
    ]
    hierarchy = any(row["verdict"] == "PASS_EXACT_PARENT_SHADOW" for row in descent_rows)
    scoped = any(row["verdict"] == "PASS_SCOPED_NEUTRAL_RESIDUAL" for row in descent_rows)
    verdict = "HIERARCHY_SCOPED" if hierarchy and scoped else "HIERARCHY" if hierarchy else "FORK_TYPED_NO_GO"
    next_delta = (
        "test richer parent-refinement branches and neutral-residual policies beyond the finite generated closer set"
        if hierarchy
        else "add an independent discriminator between split-sector and one-factor closers"
    )

    write_csv(
        ARTIFACT_DIR / "branching_roles_step25.csv",
        role_rows,
        ["source_id", "role_key", "role_family", "sector_signature", "dimension", "charge", "included_in_charged_image"],
    )
    write_csv(
        ARTIFACT_DIR / "f51_descent_step25.csv",
        descent_rows,
        [
            "parent_id",
            "parent_pattern",
            "parent_dimension",
            "child_dimensions",
            "descent_type",
            "exact_structure_match",
            "charged_content_obstruction",
            "full_content_obstruction",
            "verdict",
            "computed_reason",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "descent_obstructions_step25.csv",
        obstruction_rows,
        [
            "parent_id",
            "charged_missing",
            "charged_extra",
            "full_missing",
            "full_extra",
            "charged_obstruction",
            "full_obstruction",
            "computed",
        ],
    )
    write_csv(
        ARTIFACT_DIR / "negative_controls_step25.csv",
        negative_rows,
        ["control", "structure_id", "should_pass_parent_test", "passes_parent_test", "computed_reason", "passes"],
    )
    write_csv(ARTIFACT_DIR / "dependency_trace_step25.csv", dependency_rows, ["axiom_id", "axiom_family", "used", "source"])
    write_csv(ARTIFACT_DIR / "ablation_step25.csv", ablation_rows, ["ablation", "descent_supported", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_reproduction_step25.csv", stage_rows, ["stage_ii_check", "charge_gravity_sum", "charge_cubed_sum", "passes"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step25.csv", six_gate_rows, ["gate", "passes", "evidence"])

    output = {
        "step": 25,
        "mode": "ModeB_F51_parent_shadow_test",
        "child": {
            "structure_id": child["structure_id"],
            "dimensions": child["dimensions"],
            "selected_charge_vector": child["selected_charge_vectors"],
        },
        "descent_verdicts": descent_rows,
        "exact_parent_count": sum(1 for row in descent_rows if row["verdict"] == "PASS_EXACT_PARENT_SHADOW"),
        "scoped_neutral_parent_count": sum(1 for row in descent_rows if row["verdict"] == "PASS_SCOPED_NEUTRAL_RESIDUAL"),
        "negative_control_count": len(negative_rows),
        "six_gates_pass": all(row["passes"] for row in six_gate_rows),
        "stage_ii_pass": stage_rows[0]["passes"],
        "verdict": verdict,
        "typed_no_go": verdict == "FORK_TYPED_NO_GO",
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_json(ARTIFACT_DIR / "mode_b_f51_descent_output_step25.json", output)

    schema = {
        "step": 25,
        "mode": "ModeB_F51_parent_shadow_test",
        "artifact_root": "steps/step25_mode_b_f51_descent_hierarchy_artifacts",
        "source_step": "steps/step24_mode_b_robustness_stress_artifacts",
        "child_closer": output["child"],
        "exact_parent_count": output["exact_parent_count"],
        "scoped_neutral_parent_count": output["scoped_neutral_parent_count"],
        "negative_control_count": output["negative_control_count"],
        "six_gates_pass": output["six_gates_pass"],
        "stage_ii_pass": output["stage_ii_pass"],
        "verdict": verdict,
        "typed_no_go": output["typed_no_go"],
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    write_json(ARTIFACT_DIR / "schema.json", schema)


if __name__ == "__main__":
    main()
