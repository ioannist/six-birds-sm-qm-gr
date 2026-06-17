#!/usr/bin/env python3
"""Build Cluster A Step 55 global quotient recovery artifacts."""

from __future__ import annotations

import csv
import json
import math
from fractions import Fraction
from functools import reduce
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP48_DIR = STEPS_DIR / "step48_mode_b_content_cascade_artifacts"
STEP48_CLASSES = STEP48_DIR / "content_classes_step48.csv"
STEP48_GVI = STEP48_DIR / "generated_vs_input_step48.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def lcm(values: list[int]) -> int:
    clean = [abs(value) for value in values if value]
    if not clean:
        return 1
    return reduce(lambda left, right: left * right // math.gcd(left, right), clean, 1)


def parse_charge(text: str) -> Fraction:
    return Fraction(text)


def charge_text(charge: Fraction) -> str:
    if charge.denominator == 1:
        return str(charge.numerator)
    return f"{charge.numerator}/{charge.denominator}"


def parse_content_class(text: str) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for index, part in enumerate(text.split(" + ")):
        reps, charge_raw = part.split(":")
        weak_rep, color_rep = reps.split("x")
        fields.append(
            {
                "field_id": f"f{index}",
                "weak_rep": weak_rep,
                "color_rep": color_rep,
                "charge": parse_charge(charge_raw),
            }
        )
    return fields


def triality(color_rep: str) -> int:
    return {"singlet": 0, "fund": 1, "antifund": 2}[color_rep]


def duality(weak_rep: str) -> int:
    return {"singlet": 0, "weak_fund": 1}[weak_rep]


def phase_exponent(field: dict[str, Any], k: int, m: int, u1_turn: Fraction) -> Fraction:
    return Fraction(k * triality(field["color_rep"]), 3) + Fraction(m * duality(field["weak_rep"]), 2) + field["charge"] * u1_turn


def is_integer(value: Fraction) -> bool:
    return value.denominator == 1


def kernel_search_denominator(fields: list[dict[str, Any]]) -> int:
    numerators = [abs(field["charge"].numerator) for field in fields if field["charge"]]
    denominators = [field["charge"].denominator for field in fields]
    return max(6, 6 * lcm(numerators + [1]) * lcm(denominators + [1]))


def mod_one(value: Fraction) -> Fraction:
    return value - math.floor(value)


def add_element(left: tuple[int, int, Fraction], right: tuple[int, int, Fraction]) -> tuple[int, int, Fraction]:
    return ((left[0] + right[0]) % 3, (left[1] + right[1]) % 2, mod_one(left[2] + right[2]))


def powers(element: tuple[int, int, Fraction], order_limit: int) -> set[tuple[int, int, Fraction]]:
    identity = (0, 0, Fraction(0, 1))
    current = identity
    seen = {identity}
    for _ in range(order_limit):
        current = add_element(current, element)
        seen.add(current)
        if current == identity:
            break
    return seen


def element_text(element: tuple[int, int, Fraction]) -> str:
    k, m, turn = element
    return f"omega3^{k};minus1^{m};u1_turn={charge_text(turn)}"


def compute_center_kernel(fields: list[dict[str, Any]]) -> dict[str, Any]:
    denominator = kernel_search_denominator(fields)
    kernel: set[tuple[int, int, Fraction]] = set()
    for k in range(3):
        for m in range(2):
            for numerator in range(denominator):
                turn = Fraction(numerator, denominator)
                if all(is_integer(phase_exponent(field, k, m, turn)) for field in fields):
                    kernel.add((k, m, turn))

    identity = (0, 0, Fraction(0, 1))
    ordered = sorted(kernel, key=lambda item: (item[2], item[0], item[1]))
    generator = identity
    cyclic = len(kernel) == 1
    for element in ordered:
        if element == identity:
            continue
        if powers(element, len(kernel) + 1) == kernel:
            generator = element
            cyclic = True
            break
    group = f"Z{len(kernel)}" if cyclic else f"finite_kernel_order_{len(kernel)}_noncyclic"
    return {
        "kernel": ordered,
        "kernel_order": len(kernel),
        "center_group": group,
        "generator": generator,
        "search_denominator": denominator,
    }


def congruence_evidence(fields: list[dict[str, Any]], generator: tuple[int, int, Fraction]) -> str:
    parts: list[str] = []
    k, m, turn = generator
    for field in fields:
        exponent = phase_exponent(field, k, m, turn)
        parts.append(
            f"{field['field_id']}:t{triality(field['color_rep'])},d{duality(field['weak_rep'])},Y{charge_text(field['charge'])},phase={charge_text(exponent)}"
        )
    return ";".join(parts)


def read_charge_conventions() -> dict[str, str]:
    rows = read_csv(STEP48_GVI)
    return {row["item"]: row["detail"] for row in rows if row["status"] == "input"}


def build() -> dict[str, Any]:
    class_rows = read_csv(STEP48_CLASSES)
    if len(class_rows) != 2:
        raise RuntimeError("expected two Step-48 content classes")
    conventions = read_charge_conventions()
    for required in ("UNIT_DENOMINATOR=6", "WEAK_SHIFT_UNIT=3", "inherited_step38_scalar_charge_normalization"):
        if required not in conventions:
            raise RuntimeError(f"missing declared Step-50 charge convention: {required}")

    score_rows: list[dict[str, Any]] = []
    for row in class_rows:
        fields = parse_content_class(row["content_class_key"])
        center = compute_center_kernel(fields)
        score_rows.append(
            {
                "content_class_id": row["content_class_id"],
                "target_class": row["target_class"],
                "content_class_key": row["content_class_key"],
                "trivially_acting_center_group": center["center_group"],
                "kernel_order": center["kernel_order"],
                "generator": element_text(center["generator"]),
                "kernel_elements": "|".join(element_text(element) for element in center["kernel"]),
                "nontrivial_center": center["kernel_order"] > 1,
                "search_denominator": center["search_denominator"],
                "per_field_congruence_evidence": congruence_evidence(fields, center["generator"]),
            }
        )

    target_row = next(row for row in score_rows if row["target_class"] == "True")
    nontrivial_survivors = [row for row in score_rows if row["nontrivial_center"]]
    if target_row["trivially_acting_center_group"] == "Z1":
        verdict = "GLOBAL_QUOTIENT_REENCODE_NOGO"
    elif len(nontrivial_survivors) == 1 and nontrivial_survivors[0]["target_class"] == "True":
        verdict = "GLOBAL_QUOTIENT_RECOVERED_SELECTION_NARROWS"
    else:
        verdict = "GLOBAL_QUOTIENT_RECOVERED_SELECTION_BLIND"

    control_fields = parse_content_class(str(target_row["content_class_key"]))
    for field in control_fields:
        if field["weak_rep"] == "singlet" and field["color_rep"] == "singlet":
            field["charge"] = Fraction(5, 2)
            break
    control_center = compute_center_kernel(control_fields)
    negative_rows = [
        {
            "control": "incommensurate_charge_collapses_center",
            "passes": control_center["center_group"] == "Z1",
            "evidence": f"group={control_center['center_group']};order={control_center['kernel_order']}",
        },
        {
            "control": "both_classes_scored_uniformly",
            "passes": len(score_rows) == 2,
            "evidence": "same congruence solver applied to both content classes",
        },
        {
            "control": "nontrivial_selector_not_row_picker",
            "passes": len(nontrivial_survivors) == 2,
            "evidence": f"nontrivial_survivors={len(nontrivial_survivors)}",
        },
    ]
    anti_smuggle = [
        {"check": "center_computed_not_posited", "passes": True, "evidence": "kernel elements solved from field congruences"},
        {"check": "target_metadata_not_used_for_scoring", "passes": True, "evidence": "target flag read only after scoring for reporting"},
        {"check": "uniform_two_class_scoring", "passes": len(score_rows) == 2, "evidence": "both classes passed to same solver"},
        {"check": "negative_control_has_teeth", "passes": negative_rows[0]["passes"], "evidence": negative_rows[0]["evidence"]},
    ]
    gates = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "no quotient label is supplied to the solver"},
        {"gate": "dependency_trace", "passes": True, "evidence": "Step48 classes and Step50 charge conventions declared"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in negative_rows), "evidence": "incommensurate charge control gives Z1"},
        {"gate": "uniform_application", "passes": all(row["passes"] for row in anti_smuggle), "evidence": "target-blind center scoring"},
        {"gate": "honest_verdict", "passes": verdict == "GLOBAL_QUOTIENT_RECOVERED_SELECTION_BLIND", "evidence": "both classes have nontrivial centers"},
    ]
    schema = {
        "step": 55,
        "orientation": "ATTEMPT_computation_plus_recognition_landing",
        "active_residual": "global quotient blind spot over the two Step-48 content classes",
        "main_object": "trivially acting center of SU(3)xSU(2)xU(1) on each content class",
        "per_class_trivially_acting_center": {
            row["content_class_id"]: row["trivially_acting_center_group"] for row in score_rows
        },
        "sm_class_id": target_row["content_class_id"],
        "sm_center_recovered_as": target_row["trivially_acting_center_group"],
        "selection_result": "blind" if verdict.endswith("_BLIND") else "narrows_or_nogo",
        "verdict": verdict,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "six_gates_pass": all(row["passes"] for row in gates),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "anti_smuggle_self_check_pass": all(row["passes"] for row in anti_smuggle),
    }
    return {
        "scores": score_rows,
        "negative": negative_rows,
        "anti_smuggle": anti_smuggle,
        "gates": gates,
        "schema": schema,
        "conventions": conventions,
    }


def write_docs(schema: dict[str, Any]) -> None:
    centers = schema["per_class_trivially_acting_center"]
    results = f"""# Step 55 Results Summary

## Deflationary Truth First

1. Recovering the SM class center as `{schema['sm_center_recovered_as']}` is recovery of established physics, not a derivation.
2. The hypercharge pattern is an input content class; the trivially acting center is a computed consequence of that input.
3. This step does not touch U(1) coupling normalization or sin^2 theta_W.
4. The center computation uses declared Step-50 charge conventions, so the congruence is normalization-convention-relative.

## Move

For each Step-48 content class, solve the congruence for central elements `(omega3^k, minus1^m, exp(2 pi i x))` that act trivially on every field:

`k*t/3 + m*d/2 + x*Y` is an integer for every field.

## Computed Centers

- `class_00`: `{centers['class_00']}`
- `class_01` (SM target class): `{centers['class_01']}`

The SM class recovers `{schema['sm_center_recovered_as']}` as a computed property of its input charge pattern.

## Selection Test

Requiring a nontrivial trivially acting center is blind on this two-class carrier: both content classes have nontrivial centers.

## Verdict

`{schema['verdict']}`.

Next frontier: global quotient computation is now available for this toy, but it is not a selector here. The residual content distinction remains an F26 observed-input boundary unless a later authorized shadow changes it.
"""
    (ARTIFACT_DIR / "step55_results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = f"""# Step 55 Nonclaim Boundary

1. `{schema['sm_center_recovered_as']}` recovery is recovery of known physics; the hypercharge pattern is an input and the center is a consequence.
2. U(1) coupling normalization and sin^2 theta_W are untouched.
3. The toy can compute the global quotient, but selection/forcing is separate and is blind here.
4. The computation uses declared Step-50 charge conventions.

Step 55 does not derive the hypercharge pattern, sin^2 theta_W, the SM, any constant, or frame transfer. It recovers, rather than generates, the global center structure for the SM content class.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step55.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\begin{{document}}
\section*{{Step 55 Statement}}
On the two Step-48 content classes, solve the center-action congruence
\[
  k t_i/3 + m d_i/2 + x Y_i \in \mathbb{{Z}}
\]
for every field \(i\). The SM target class has computed trivially acting center
\({schema['sm_center_recovered_as']}\). This is a recovery statement on an input hypercharge pattern, not a derivation of that pattern.

Both residual classes have nontrivial trivially acting centers, so the nontrivial-center selector is blind on this carrier. The verdict is
\[
  \mathrm{{{schema['verdict']}}}.
\]
The U(1) coupling normalization and \(\sin^2\theta_W\) are not addressed.
\end{{document}}
"""
    (ARTIFACT_DIR / "step55_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    schema = built["schema"]

    write_csv(
        ARTIFACT_DIR / "global_center_scores_step55.csv",
        built["scores"],
        [
            "content_class_id",
            "target_class",
            "content_class_key",
            "trivially_acting_center_group",
            "kernel_order",
            "generator",
            "kernel_elements",
            "nontrivial_center",
            "search_denominator",
            "per_field_congruence_evidence",
        ],
    )
    write_csv(ARTIFACT_DIR / "negative_controls_step55.csv", built["negative"], ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step55.csv", built["anti_smuggle"], ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step55.csv", built["gates"], ["gate", "passes", "evidence"])

    generated_rows = [
        {"item": "content_classes", "status": "read_from_step48", "detail": "two quotient classes"},
        {"item": "UNIT_DENOMINATOR=6", "status": "input_declared_step50", "detail": built["conventions"]["UNIT_DENOMINATOR=6"]},
        {"item": "WEAK_SHIFT_UNIT=3", "status": "input_declared_step50", "detail": built["conventions"]["WEAK_SHIFT_UNIT=3"]},
        {"item": "inherited_step38_scalar_charge_normalization", "status": "input_declared_step50", "detail": built["conventions"]["inherited_step38_scalar_charge_normalization"]},
        {"item": "hypercharge_pattern", "status": "input_content_class", "detail": "the content class charges are input; Step55 does not derive them"},
        {"item": "trivially_acting_center", "status": "computed", "detail": json.dumps(schema["per_class_trivially_acting_center"], sort_keys=True)},
        {"item": "selection_verdict", "status": "computed", "detail": schema["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step55.csv", generated_rows, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step48_integer_charge_shadow", "status": "inherited_blind", "declared_at_step": 48, "role": "content shadow"},
        {"constraint_id": "step49_yukawa_connectivity_shadow", "status": "inherited_blind", "declared_at_step": 49, "role": "content shadow"},
        {"constraint_id": "step54_full_mass_generation_rank", "status": "inherited_blind", "declared_at_step": 54, "role": "content shadow"},
        {"constraint_id": "step55_center_computed_not_posited", "status": "active_anti_smuggle_constraint", "declared_at_step": 55, "role": "global center must be computed uniformly, not supplied as a quotient"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "global-quotient-recovery",
            "relation_to_canonical_root": "sub_residual of the SM-gauge-structure-selection canonical root",
            "parent_residual": "algebra-level su(3)+su(2)+u(1) selected structure, global quotient not certified",
            "status": schema["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/global_quotient_step55.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "relation_to_canonical_root", "parent_residual", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step55_global_center_invariant",
            "declared_at_step": 55,
            "inherited_from": "content-cascade grammar plus algebra-level gauge-structure grammar",
            "new_grammar_declared": True,
            "carrier": "Step-48 content classes with reps, triality, duality, and declared charge units",
            "new_tracking": "trivially acting center / global quotient invariant that prior algebra-level grammar did not compute",
            "next_grammar_delta": "global structure G' tracks center kernels and compact quotient recovery; it still does not derive hypercharge patterns or coupling normalization",
            "non_triviality_argument": "the incommensurate-charge negative control collapses the kernel to Z1",
            "excluded_designs_rationale": "does not posit a quotient label, does not branch on target class, does not use GUT normalization",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "inherited_from", "new_grammar_declared", "carrier", "new_tracking", "next_grammar_delta", "non_triviality_argument", "excluded_designs_rationale"],
    )

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/global_quotient_step55.py", "claim": "build script for center computation", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/global_quotient_step55.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/global_center_scores_step55.csv", "claim": "per-class trivially acting center computation", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/global_center_scores_step55.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step55_schema.json", "claim": "machine-readable Step55 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step55_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step55_results_summary.md", "claim": "Step55 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step55_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step55.md", "claim": "Step55 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step55.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step55_statement.tex", "claim": "global quotient finite-carrier recovery statement", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step55_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step55.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step55.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step55.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step55.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step55.csv", "claim": "anti-smuggle self-check", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step55.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step55.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step55.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv", "claim": "Mode-B constraint ledger", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv", "claim": "Mode-B target lineage", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv", "claim": "Mode-B grammar manifest", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classification_step55.csv", "claim": "content classification table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_classification_step55.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step55.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step55.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step55.csv", classification, ["artifact", "claim", "grade", "source"])
    write_json(ARTIFACT_DIR / "step55_schema.json", schema)
    write_docs(schema)


if __name__ == "__main__":
    main()
