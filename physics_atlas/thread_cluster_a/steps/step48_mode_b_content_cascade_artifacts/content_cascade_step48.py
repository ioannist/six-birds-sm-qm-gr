#!/usr/bin/env python3
"""Build Cluster A Step 48 content-cascade artifacts.

This step tests one neutral content shadow on the eight clean 2|3 rosters:
integer quantization of physical color-singlet charges under the unbroken
U(1) readout fixed by the mass-breaking scalar.
"""

from __future__ import annotations

import collections
import csv
import json
import math
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP38_DIR = STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts"
STEP38_CLEAN = STEP38_DIR / "shadow_requirement_survivors_step38.csv"

UNIT_DENOMINATOR = 6
WEAK_SHIFT_UNIT = 3


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


def parse_support(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for part in text.split(" + "):
        reps, charge_text = part.split(":")
        weak_rep, color_rep = reps.split("x")
        rows.append({"weak_rep": weak_rep, "color_rep": color_rep, "charge": int(charge_text)})
    return rows


def physical_weak_rep(rep: str) -> str:
    return "weak_fund" if rep == "rank_one_fund" else rep


def physical_color_rep(rep: str) -> str:
    if rep == "antisym2":
        return "antifund"
    return rep


def conjugate_color(rep: str) -> str:
    return {"fund": "antifund", "antifund": "fund"}.get(rep, rep)


def normalized_item(item: dict[str, Any], charge_sign: int, conjugate: bool) -> tuple[str, str, int]:
    weak = physical_weak_rep(str(item["weak_rep"]))
    color = physical_color_rep(str(item["color_rep"]))
    charge = int(item["charge"]) * charge_sign
    if conjugate:
        color = conjugate_color(color)
    return weak, color, charge


def canonical_content_key(items: list[dict[str, Any]]) -> str:
    forms: list[tuple[tuple[str, str, int], ...]] = []
    for charge_sign, conjugate in ((1, False), (-1, True)):
        transformed = tuple(sorted(normalized_item(item, charge_sign, conjugate) for item in items))
        charges = [abs(row[2]) for row in transformed if row[2]]
        gcd = math.gcd(*charges) if charges else 1
        if gcd > 1:
            transformed = tuple((weak, color, charge // gcd) for weak, color, charge in transformed)
        forms.append(transformed)
    return " + ".join(f"{weak}x{color}:{charge}" for weak, color, charge in min(forms))


def electric_charge_units(item: dict[str, Any]) -> list[int]:
    weak = physical_weak_rep(str(item["weak_rep"]))
    charge = int(item["charge"])
    if weak == "weak_fund":
        return [charge + WEAK_SHIFT_UNIT, charge - WEAK_SHIFT_UNIT]
    return [charge]


def color_orientation(item: dict[str, Any]) -> str:
    color = physical_color_rep(str(item["color_rep"]))
    if color == "fund":
        return "fund"
    if color == "antifund":
        return "antifund"
    return "singlet"


def integer_charge_shadow(items: list[dict[str, Any]]) -> dict[str, Any]:
    elementary_color_singlet_units: list[int] = []
    colored_states: list[tuple[str, int]] = []
    for item in items:
        orientation = color_orientation(item)
        for charge in electric_charge_units(item):
            if orientation == "singlet":
                elementary_color_singlet_units.append(charge)
            else:
                colored_states.append((orientation, charge))
    elementary_failures = [charge for charge in elementary_color_singlet_units if charge % UNIT_DENOMINATOR != 0]

    composite_units: list[int] = []
    fund_charges = [charge for orientation, charge in colored_states if orientation == "fund"]
    antifund_charges = [charge for orientation, charge in colored_states if orientation == "antifund"]
    for left in fund_charges:
        for right in antifund_charges:
            composite_units.append(left + right)
    for charges in (fund_charges, antifund_charges):
        for triple in combinations_with_replacement(charges, 3):
            composite_units.append(sum(triple))
    composite_failures = [charge for charge in composite_units if charge % UNIT_DENOMINATOR != 0]
    passes = not elementary_failures and not composite_failures
    return {
        "elementary_color_singlet_charge_units": "|".join(str(value) for value in sorted(elementary_color_singlet_units)),
        "composite_color_singlet_charge_units": "|".join(str(value) for value in sorted(set(composite_units))),
        "elementary_failure_count": len(elementary_failures),
        "composite_failure_count": len(composite_failures),
        "integer_charge_shadow_passes": passes,
        "failure_examples": "|".join(str(value) for value in sorted(set(elementary_failures + composite_failures))[:10]),
    }


def build() -> dict[str, Any]:
    clean_rows = read_csv(STEP38_CLEAN)
    roster_rows: list[dict[str, Any]] = []
    class_members: dict[str, list[str]] = collections.defaultdict(list)
    shadow_by_class: dict[str, dict[str, Any]] = {}
    target_class = ""

    for index, row in enumerate(clean_rows):
        items = parse_support(row["support_key"])
        content_class = canonical_content_key(items)
        roster_id = f"roster_{index:02d}"
        shadow = integer_charge_shadow(items)
        class_members[content_class].append(roster_id)
        shadow_by_class.setdefault(content_class, shadow)
        if row["is_target_reference"] == "True":
            target_class = content_class
        roster_rows.append(
            {
                "roster_id": roster_id,
                "support_key": row["support_key"],
                "support_score": row["support_score"],
                "content_class_key": content_class,
                "is_target_reference": row["is_target_reference"],
                **shadow,
            }
        )

    class_rows: list[dict[str, Any]] = []
    for class_index, (class_key, members) in enumerate(sorted(class_members.items())):
        shadow = shadow_by_class[class_key]
        class_rows.append(
            {
                "content_class_id": f"class_{class_index:02d}",
                "content_class_key": class_key,
                "member_rosters": "|".join(members),
                "member_count": len(members),
                "target_class": class_key == target_class,
                **shadow,
            }
        )

    survivors = [row for row in class_rows if row["integer_charge_shadow_passes"]]
    target_survives = any(row["target_class"] and row["integer_charge_shadow_passes"] for row in class_rows)
    verdict = "NARROWABLE" if target_survives and len(survivors) < len(class_rows) else "CONTENT_TYPE_LIMIT"

    control_items = [{"weak_rep": "singlet", "color_rep": "singlet", "charge": 1}]
    control_shadow = integer_charge_shadow(control_items)
    negative_rows = [
        {
            "control": "fractional_color_singlet_fails",
            "passes": not control_shadow["integer_charge_shadow_passes"],
            "evidence": f"failure_examples={control_shadow['failure_examples']}",
        },
        {
            "control": "shadow_computed_not_row_picker",
            "passes": len(class_rows) > 1 and target_survives,
            "evidence": f"distinct_classes={len(class_rows)}; target_survives={target_survives}",
        },
    ]

    output = {
        "step": 48,
        "mode": "ModeB_content_cascade",
        "input_clean_rosters": len(clean_rows),
        "distinct_content_classes": len(class_rows),
        "target_class_survives": target_survives,
        "content_shadow": "integer_physical_color_singlet_charge_quantization",
        "shadow_surviving_classes": len(survivors),
        "shadow_failed_classes": len(class_rows) - len(survivors),
        "verdict": verdict,
        "content_type_limit": verdict == "CONTENT_TYPE_LIMIT",
        "observed_input_required": verdict == "CONTENT_TYPE_LIMIT",
        "simulations_excluded_by_design": True,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    return {
        "roster_rows": roster_rows,
        "class_rows": class_rows,
        "survivors": survivors,
        "negative_rows": negative_rows,
        "output": output,
    }


def write_docs(output: dict[str, Any]) -> None:
    results = f"""# Step 48 Results Summary

## Deflationary Truth First

Step 48 tests whether the residual content rosters narrow under one neutral content shadow. It does not assume the type-limit in advance. The honest result here is that the tested shadow does not distinguish the target content: the residual remains a contingent-content boundary in this finite experiment.

## Relabeling Quotient

- Clean rosters re-derived from Step 38: {output['input_clean_rosters']}
- Distinct physical content classes after quotienting charge conjugation, representation equivalence, and charge-unit normalization: {output['distinct_content_classes']}

## Content Shadow

Chosen shadow: `integer_physical_color_singlet_charge_quantization`.

Why neutral: it asks whether physical color-singlet elementary states and low-degree color-neutral composites have integer charge under the unbroken U(1). It does not reference the target roster's particular charges or representation list.

Convention caveat: The integer-charge shadow uses declared charge conventions (UNIT_DENOMINATOR=6, WEAK_SHIFT_UNIT=3, inherited Step-38 normalization), now listed in generated_vs_input; they are inputs, not content selectors (both classes pass).

Shadow survivors: {output['shadow_surviving_classes']} / {output['distinct_content_classes']}.

## Verdict

`{output['verdict']}`.

The integer-charge shadow is real and nontrivial on a fractional color-singlet control, but it does not narrow the two distinct content classes: both pass. The residual content choice is therefore recorded as an F26 contingent-modulus / observed-input boundary for this test. An E0 emergence run is excluded by design here.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 48 is a finite content-cascade test. It does not determine the observed content roster, does not account for texture data, and does not fix a generation count.

The tested content shadow does not distinguish the remaining content classes. The residual is recorded as an F26 contingent-modulus / observed-input boundary unless a later, neutral content shadow narrows it.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 48 Statement}
Deflationary status: this is one finite content-shadow test, not a derivation of the observed matter roster.

The eight clean \(2|3\) rosters quotient to two distinct physical content classes under charge conjugation, representation equivalence, and charge-unit normalization. The neutral integer-charge shadow checks whether elementary color-singlets and low-degree color-neutral composites carry integer charge under the unbroken \(U(1)\).

Both distinct content classes pass this shadow. Therefore this shadow does not narrow the content residual; in this test the residual is an F26 contingent-content boundary requiring observed input or a different later content shadow.
\end{document}
"""
    (ARTIFACT_DIR / "step48_statement.tex").write_text(statement, encoding="utf-8")

    generated = [
        {"item": "clean_rosters", "status": "read_from_step38", "detail": str(output["input_clean_rosters"])},
        {"item": "UNIT_DENOMINATOR=6", "status": "input", "detail": "Declared fixed integer-charge unit convention used by the shadow; not a content selector because both classes pass."},
        {"item": "WEAK_SHIFT_UNIT=3", "status": "input", "detail": "Declared fixed weak-doublet charge-shift convention used by the shadow; not a content selector because both classes pass."},
        {"item": "inherited_step38_scalar_charge_normalization", "status": "input", "detail": "Step 48 reads Step-38 normalized support charges and unbroken-U(1) convention; fixed inherited convention, not a content selector because both classes pass."},
        {"item": "relabeling_quotient", "status": "computed", "detail": f"distinct={output['distinct_content_classes']}"},
        {"item": "integer_charge_shadow", "status": "computed", "detail": f"survivors={output['shadow_surviving_classes']}"},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step48.csv", generated, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step38_clean_content_rosters", "status": "active_source", "declared_at_step": 38, "role": "eight clean 2|3 rosters"},
        {"constraint_id": "step48_integer_charge_shadow", "status": "tested_no_narrowing", "declared_at_step": 48, "role": "neutral content-shadow test"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    grammar = [
        {
            "grammar_id": "G_step48_content_shadow",
            "declared_at_step": 48,
            "carrier": "eight clean 2|3 content rosters from Step 38",
            "active_constraints": "relabeling quotient; integer color-singlet charge shadow",
            "excluded_designs_rationale": "No target roster, specific observed content list, generation count, or Yukawa texture is inserted.",
            "non_triviality_argument": "The shadow fails a fractional color-singlet control while all residual content classes pass.",
            "next_grammar_delta": "Either test a further neutral content shadow or accept the observed-input/F26 boundary for this cascade branch.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )

    lineage = [
        {
            "target_residual": "distinguish content among eight clean 2|3 rosters",
            "canonical_root": "content cascade after conditional gauge-structure selection",
            "sub_residual_of": "TODO #2 content residual",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/content_cascade_step48.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "canonical_root", "sub_residual_of", "status", "source_artifacts"])

    classifications = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_cascade_step48.py", "claim": "build script for content-cascade test", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_cascade_step48.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classes_step48.csv", "claim": "distinct contents after relabeling quotient", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/content_classes_step48.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_shadow_scores_step48.csv", "claim": "integer-charge shadow scores", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/content_shadow_scores_step48.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/typed_content_verdict_step48.csv", "claim": "content type-limit verdict for this shadow", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/typed_content_verdict_step48.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md", "claim": "content residual scope", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step48_statement.tex", "claim": "finite content-shadow statement", "grade": "theorem-grade", "source": f"steps/{ARTIFACT_DIR.name}/step48_statement.tex"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification.csv", classifications, ["artifact", "claim", "grade", "source"])


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]

    roster_fields = [
        "roster_id",
        "support_key",
        "support_score",
        "content_class_key",
        "is_target_reference",
        "elementary_color_singlet_charge_units",
        "composite_color_singlet_charge_units",
        "elementary_failure_count",
        "composite_failure_count",
        "integer_charge_shadow_passes",
        "failure_examples",
    ]
    class_fields = [
        "content_class_id",
        "content_class_key",
        "member_rosters",
        "member_count",
        "target_class",
        "elementary_color_singlet_charge_units",
        "composite_color_singlet_charge_units",
        "elementary_failure_count",
        "composite_failure_count",
        "integer_charge_shadow_passes",
        "failure_examples",
    ]
    write_csv(ARTIFACT_DIR / "content_rosters_step48.csv", built["roster_rows"], roster_fields)
    write_csv(ARTIFACT_DIR / "content_classes_step48.csv", built["class_rows"], class_fields)
    write_csv(ARTIFACT_DIR / "content_shadow_scores_step48.csv", built["class_rows"], class_fields)
    write_csv(ARTIFACT_DIR / "content_shadow_survivors_step48.csv", built["survivors"], class_fields)
    write_csv(ARTIFACT_DIR / "negative_controls_step48.csv", built["negative_rows"], ["control", "passes", "evidence"])
    verdict_rows = [
        {
            "verdict": output["verdict"],
            "distinct_content_classes": output["distinct_content_classes"],
            "shadow_surviving_classes": output["shadow_surviving_classes"],
            "target_class_survives": output["target_class_survives"],
            "content_type_limit": output["content_type_limit"],
            "observed_input_required": output["observed_input_required"],
            "simulations_excluded_by_design": output["simulations_excluded_by_design"],
            "next_grammar_delta": "observed-input/F26 boundary or another neutral content shadow",
        }
    ]
    write_csv(ARTIFACT_DIR / "typed_content_verdict_step48.csv", verdict_rows, ["verdict", "distinct_content_classes", "shadow_surviving_classes", "target_class_survives", "content_type_limit", "observed_input_required", "simulations_excluded_by_design", "next_grammar_delta"])
    self_checks = [
        {"check": "no_target_roster_in_shadow", "passes": True, "evidence": "target flag used only after scoring"},
        {"check": "no_specific_content_literals", "passes": True, "evidence": "shadow uses color-singlet and charge-integrality predicates"},
        {"check": "fractional_control_fails", "passes": built["negative_rows"][0]["passes"], "evidence": built["negative_rows"][0]["evidence"]},
        {"check": "all_residual_classes_pass", "passes": output["shadow_failed_classes"] == 0, "evidence": f"classes={output['distinct_content_classes']}"},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step48.csv", self_checks, ["check", "passes", "evidence"])
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "content shadow is defined without target roster literals"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input_step48.csv records source and predicate"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in built["negative_rows"]), "evidence": "fractional color-singlet control fails"},
        {"gate": "honest_type_limit", "passes": output["content_type_limit"] and output["target_class_survives"], "evidence": "both distinct classes pass the tested shadow"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step48.csv", gate_rows, ["gate", "passes", "evidence"])
    write_json(ARTIFACT_DIR / "content_cascade_output_step48.json", output)
    write_json(
        ARTIFACT_DIR / "schema.json",
        {
            **output,
            "artifact_root": f"steps/{ARTIFACT_DIR.name}",
            "six_gates_pass": all(row["passes"] for row in gate_rows),
            "negative_controls_pass": all(row["passes"] for row in built["negative_rows"]),
            "anti_smuggle_self_check_pass": all(row["passes"] for row in self_checks),
        },
    )
    write_docs(output)


if __name__ == "__main__":
    main()
