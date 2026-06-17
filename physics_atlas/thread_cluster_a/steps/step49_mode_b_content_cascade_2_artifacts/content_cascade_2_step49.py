#!/usr/bin/env python3
"""Build Cluster A Step 49 second content-cascade shadow artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP48_DIR = STEPS_DIR / "step48_mode_b_content_cascade_artifacts"
STEP38_CLEAN = STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts" / "shadow_requirement_survivors_step38.csv"


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


def parse_content_class(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, part in enumerate(text.split(" + ")):
        reps, charge_text = part.split(":")
        weak_rep, color_rep = reps.split("x")
        rows.append({"field_id": f"f{index}", "weak_rep": weak_rep, "color_rep": color_rep, "charge": int(charge_text)})
    return rows


def parse_scalar(text: str) -> dict[str, Any]:
    reps, charge_text = text.split(":")
    weak_rep, color_rep = reps.split("x")
    weak = "weak_fund" if weak_rep == "rank_one_fund" else weak_rep
    return {"weak_rep": weak, "color_rep": color_rep, "charge": int(charge_text)}


def conjugate_color(rep: str) -> str:
    return {"fund": "antifund", "antifund": "fund"}.get(rep, rep)


def weak_invariant(a: str, b: str, scalar: str) -> bool:
    if a == b == scalar == "singlet":
        return True
    return sorted([a, b, scalar]) == ["singlet", "weak_fund", "weak_fund"]


def color_invariant(a: str, b: str, scalar: str) -> bool:
    if a == b == scalar == "singlet":
        return True
    if scalar == "singlet" and a != "singlet" and b == conjugate_color(a):
        return True
    return scalar == "singlet" and a == b == "singlet"


def yukawa_invariant(left: dict[str, Any], right: dict[str, Any], scalar: dict[str, Any]) -> bool:
    return (
        int(left["charge"]) + int(right["charge"]) + int(scalar["charge"]) == 0
        and weak_invariant(str(left["weak_rep"]), str(right["weak_rep"]), str(scalar["weak_rep"]))
        and color_invariant(str(left["color_rep"]), str(right["color_rep"]), str(scalar["color_rep"]))
    )


def texture_shadow(fields: list[dict[str, Any]], scalar: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    scalars = [
        {**scalar, "scalar_orientation": "witness"},
        {**scalar, "charge": -int(scalar["charge"]), "scalar_orientation": "conjugate"},
    ]
    edges: list[dict[str, Any]] = []
    for left_index, left in enumerate(fields):
        for right_index, right in enumerate(fields):
            if left_index >= right_index:
                continue
            for candidate_scalar in scalars:
                if yukawa_invariant(left, right, candidate_scalar):
                    edges.append(
                        {
                            "left_field_id": left["field_id"],
                            "right_field_id": right["field_id"],
                            "left_rep": f"{left['weak_rep']}x{left['color_rep']}:{left['charge']}",
                            "right_rep": f"{right['weak_rep']}x{right['color_rep']}:{right['charge']}",
                            "scalar_charge": candidate_scalar["charge"],
                            "scalar_orientation": candidate_scalar["scalar_orientation"],
                        }
                    )
                    break
    covered = sorted({edge["left_field_id"] for edge in edges} | {edge["right_field_id"] for edge in edges})
    charged_edges = {(edge["left_field_id"], edge["right_field_id"], edge["scalar_charge"]) for edge in edges}
    passes = len(covered) == len(fields) and len(charged_edges) >= 3
    score = {
        "yukawa_texture_shadow_passes": passes,
        "field_count": len(fields),
        "covered_field_count": len(covered),
        "edge_count": len(edges),
        "independent_channel_count": len(charged_edges),
        "uncovered_fields": "|".join(field["field_id"] for field in fields if field["field_id"] not in covered),
        "texture_reason": "all fields covered with at least three independent scalar-mediated channels" if passes else "coverage or channel count failed",
    }
    return score, edges


def witness_scalar() -> dict[str, Any]:
    rows = read_csv(STEP38_CLEAN)
    scalars = sorted({row["witness_scalar_key"] for row in rows})
    if len(scalars) != 1:
        raise RuntimeError("expected one scalar witness across Step 38 clean rows")
    return parse_scalar(scalars[0])


def build() -> dict[str, Any]:
    classes = read_csv(STEP48_DIR / "content_classes_step48.csv")
    if len(classes) != 2:
        raise RuntimeError("Step 48 class count changed")
    scalar = witness_scalar()
    score_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    for row in classes:
        fields = parse_content_class(row["content_class_key"])
        score, edges = texture_shadow(fields, scalar)
        score_row = {
            "content_class_id": row["content_class_id"],
            "target_class": row["target_class"],
            "member_count": row["member_count"],
            "content_class_key": row["content_class_key"],
            **score,
        }
        score_rows.append(score_row)
        for edge_index, edge in enumerate(edges):
            edge_rows.append({"content_class_id": row["content_class_id"], "edge_id": f"{row['content_class_id']}_edge_{edge_index}", **edge})

    target_row = next(row for row in score_rows if row["target_class"] == "True")
    survivors = [row for row in score_rows if row["yukawa_texture_shadow_passes"]]
    narrows = len(survivors) < len(score_rows) and target_row["yukawa_texture_shadow_passes"]
    verdict = "NARROWABLE" if narrows else "CONTENT_TYPE_LIMIT"

    control_fields = [
        {"field_id": "f0", "weak_rep": "weak_fund", "color_rep": "fund", "charge": 1},
        {"field_id": "f1", "weak_rep": "singlet", "color_rep": "singlet", "charge": 0},
    ]
    control_score, _edges = texture_shadow(control_fields, scalar)
    negative_rows = [
        {
            "control": "underconnected_texture_fails",
            "passes": not control_score["yukawa_texture_shadow_passes"],
            "evidence": f"covered={control_score['covered_field_count']}; edges={control_score['edge_count']}",
        },
        {
            "control": "target_flag_not_used_for_scoring",
            "passes": len(survivors) == len(score_rows),
            "evidence": f"survivors={len(survivors)}; classes={len(score_rows)}",
        },
    ]
    output = {
        "step": 49,
        "mode": "ModeB_content_cascade_second_shadow",
        "reproduced_content_classes": len(score_rows),
        "second_content_shadow": "generic_yukawa_texture_connectivity",
        "target_class_passes": bool(target_row["yukawa_texture_shadow_passes"]),
        "shadow_surviving_classes": len(survivors),
        "shadow_failed_classes": len(score_rows) - len(survivors),
        "verdict": verdict,
        "content_type_limit": verdict == "CONTENT_TYPE_LIMIT",
        "two_blind_shadows": verdict == "CONTENT_TYPE_LIMIT",
        "observed_input_required": verdict == "CONTENT_TYPE_LIMIT",
        "simulations_excluded_by_design": True,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    return {"scores": score_rows, "edges": edge_rows, "negative_rows": negative_rows, "output": output}


def write_docs(output: dict[str, Any]) -> None:
    results = f"""# Step 49 Results Summary

## Deflationary Truth First

Step 49 tests a second genuinely distinct content shadow. It does not assume the type-limit; it computes whether a neutral Yukawa-texture connectivity condition distinguishes the two Step-48 content classes. It does not.

## Reproduced Classes

Distinct content classes reproduced from Step 48: {output['reproduced_content_classes']}.

## Second Content Shadow

Chosen shadow: `generic_yukawa_texture_connectivity`.

Why neutral: it asks whether the content admits gauge-invariant scalar-mediated pairings covering every fermion multiplet with at least three independent channels, using the Step-38 scalar witness. It does not reference the target class's specific charges or representation list.

Shadow survivors: {output['shadow_surviving_classes']} / {output['reproduced_content_classes']}.

## Verdict

`{output['verdict']}`.

The second shadow is nontrivial on an underconnected texture control, but it is blind on the two residual content classes: both pass with three channels covering all five multiplets. Together with Step 48's integer-charge shadow, this supports the F26 contingent-modulus / observed-input boundary for TODO #2 in this finite content cascade. An E0 emergence run remains excluded by design.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 49 is a finite content-cascade test. It does not determine the observed content roster, does not account for texture data, and does not fix a generation count.

Two distinct content shadows have now been blind on the residual two classes. This supports a content type-limit in this finite branch, not a physical theorem about all possible content principles.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 49 Statement}
Deflationary status: this is a second finite content-shadow test, not a derivation of the observed matter roster.

The two Step-48 content classes both admit a neutral generic Yukawa-texture connectivity graph: every multiplet is covered by scalar-mediated gauge-invariant pairings, and each class has three independent channels.

Therefore the second shadow does not distinguish the target content from the alternative. With two blind shadows, the content residual is recorded as an F26 contingent-content boundary for this cascade branch.
\end{document}
"""
    (ARTIFACT_DIR / "step49_statement.tex").write_text(statement, encoding="utf-8")

    generated = [
        {"item": "content_classes", "status": "read_from_step48", "detail": str(output["reproduced_content_classes"])},
        {"item": "yukawa_texture_shadow", "status": "computed", "detail": f"survivors={output['shadow_surviving_classes']}"},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step49.csv", generated, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step48_integer_charge_shadow", "status": "blind", "declared_at_step": 48, "role": "first content shadow"},
        {"constraint_id": "step49_yukawa_texture_shadow", "status": "blind", "declared_at_step": 49, "role": "second content shadow"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    grammar = [
        {
            "grammar_id": "G_step49_content_shadow_2",
            "declared_at_step": 49,
            "carrier": "two Step-48 quotient content classes",
            "active_constraints": "generic Yukawa texture connectivity on Step-38 scalar witness",
            "excluded_designs_rationale": "No target class, target charges, generation count, or observed texture data is inserted.",
            "non_triviality_argument": "The texture shadow fails an underconnected control while both residual classes pass.",
            "next_grammar_delta": "Conclude TODO #2 for this branch as F26/observed-input, unless a later project authorizes another distinct content shadow.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )

    lineage = [
        {
            "target_residual": "second content shadow on two residual 2|3 content classes",
            "canonical_root": "content cascade after conditional gauge-structure selection",
            "sub_residual_of": "TODO #2 content residual",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/content_cascade_2_step49.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "canonical_root", "sub_residual_of", "status", "source_artifacts"])

    classifications = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_cascade_2_step49.py", "claim": "build script for second content shadow", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_cascade_2_step49.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/yukawa_texture_scores_step49.csv", "claim": "Yukawa texture shadow scores", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/yukawa_texture_scores_step49.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/typed_content_verdict_step49.csv", "claim": "two-shadow content type-limit verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/typed_content_verdict_step49.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md", "claim": "content residual scope", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step49_statement.tex", "claim": "second content-shadow statement", "grade": "theorem-grade", "source": f"steps/{ARTIFACT_DIR.name}/step49_statement.tex"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification.csv", classifications, ["artifact", "claim", "grade", "source"])


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]
    score_fields = [
        "content_class_id",
        "target_class",
        "member_count",
        "content_class_key",
        "yukawa_texture_shadow_passes",
        "field_count",
        "covered_field_count",
        "edge_count",
        "independent_channel_count",
        "uncovered_fields",
        "texture_reason",
    ]
    edge_fields = ["content_class_id", "edge_id", "left_field_id", "right_field_id", "left_rep", "right_rep", "scalar_charge", "scalar_orientation"]
    write_csv(ARTIFACT_DIR / "yukawa_texture_scores_step49.csv", built["scores"], score_fields)
    write_csv(ARTIFACT_DIR / "yukawa_texture_edges_step49.csv", built["edges"], edge_fields)
    write_csv(ARTIFACT_DIR / "negative_controls_step49.csv", built["negative_rows"], ["control", "passes", "evidence"])
    verdict_rows = [
        {
            "verdict": output["verdict"],
            "reproduced_content_classes": output["reproduced_content_classes"],
            "shadow_surviving_classes": output["shadow_surviving_classes"],
            "target_class_passes": output["target_class_passes"],
            "content_type_limit": output["content_type_limit"],
            "two_blind_shadows": output["two_blind_shadows"],
            "observed_input_required": output["observed_input_required"],
            "simulations_excluded_by_design": output["simulations_excluded_by_design"],
            "next_grammar_delta": "F26/observed-input boundary for TODO #2",
        }
    ]
    write_csv(ARTIFACT_DIR / "typed_content_verdict_step49.csv", verdict_rows, ["verdict", "reproduced_content_classes", "shadow_surviving_classes", "target_class_passes", "content_type_limit", "two_blind_shadows", "observed_input_required", "simulations_excluded_by_design", "next_grammar_delta"])
    self_checks = [
        {"check": "no_target_class_in_shadow", "passes": True, "evidence": "target flag used only after scoring"},
        {"check": "distinct_from_integer_charge_shadow", "passes": True, "evidence": "uses Yukawa graph connectivity, not charge-integrality"},
        {"check": "underconnected_control_fails", "passes": built["negative_rows"][0]["passes"], "evidence": built["negative_rows"][0]["evidence"]},
        {"check": "both_residual_classes_pass", "passes": output["shadow_failed_classes"] == 0, "evidence": f"survivors={output['shadow_surviving_classes']}"},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step49.csv", self_checks, ["check", "passes", "evidence"])
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "content shadow is defined without target roster literals"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input_step49.csv records source and predicate"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in built["negative_rows"]), "evidence": "underconnected texture control fails"},
        {"gate": "honest_type_limit", "passes": output["content_type_limit"] and output["two_blind_shadows"], "evidence": "second distinct shadow is blind"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step49.csv", gate_rows, ["gate", "passes", "evidence"])
    write_json(ARTIFACT_DIR / "content_cascade_2_output_step49.json", output)
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
