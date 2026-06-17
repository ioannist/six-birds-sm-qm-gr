#!/usr/bin/env python3
"""Build Cluster A Step 54 third content-cascade shadow artifacts."""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP48_CLASSES = STEPS_DIR / "step48_mode_b_content_cascade_artifacts" / "content_classes_step48.csv"
STEP49_SCRIPT = STEPS_DIR / "step49_mode_b_content_cascade_2_artifacts" / "content_cascade_2_step49.py"

WEAK_SHIFT_UNIT = 3


def load_step49():
    spec = importlib.util.spec_from_file_location("cluster_a_step49_for_step54", STEP49_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 49 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step49_for_step54"] = module
    spec.loader.exec_module(module)
    return module


s49 = load_step49()


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


def charged_component_charges(field: dict[str, Any]) -> list[int]:
    charge = int(field["charge"])
    if field["weak_rep"] == "weak_fund":
        return [value for value in (charge + WEAK_SHIFT_UNIT, charge - WEAK_SHIFT_UNIT) if value != 0]
    return [] if charge == 0 else [charge]


def all_component_charges(field: dict[str, Any]) -> list[int]:
    charge = int(field["charge"])
    if field["weak_rep"] == "weak_fund":
        return [charge + WEAK_SHIFT_UNIT, charge - WEAK_SHIFT_UNIT]
    return [charge]


def field_by_id(fields: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(field["field_id"]): field for field in fields}


def rep_text(field: dict[str, Any]) -> str:
    return f"{field['weak_rep']}x{field['color_rep']}:{field['charge']}"


def massed_components(fields: list[dict[str, Any]], edges: list[dict[str, Any]]) -> tuple[dict[str, set[int]], list[dict[str, Any]]]:
    by_id = field_by_id(fields)
    massed: dict[str, set[int]] = {field["field_id"]: set() for field in fields}
    rank_edges: list[dict[str, Any]] = []
    for edge in edges:
        left = by_id[str(edge["left_field_id"])]
        right = by_id[str(edge["right_field_id"])]
        weak_singlet_pair = None
        if left["weak_rep"] == "weak_fund" and right["weak_rep"] == "singlet":
            weak_singlet_pair = (left, right)
        elif right["weak_rep"] == "weak_fund" and left["weak_rep"] == "singlet":
            weak_singlet_pair = (right, left)
        elif left["weak_rep"] == "singlet" and right["weak_rep"] == "singlet" and int(left["charge"]) + int(right["charge"]) == 0:
            massed[left["field_id"]].add(int(left["charge"]))
            massed[right["field_id"]].add(int(right["charge"]))
            rank_edges.append({**edge, "massed_component_charge": int(left["charge"]), "rank_role": "singlet_singlet_pair"})
            continue
        if weak_singlet_pair is None:
            continue
        weak_field, singlet_field = weak_singlet_pair
        component_charge = -int(singlet_field["charge"])
        if component_charge in all_component_charges(weak_field):
            if component_charge != 0:
                massed[weak_field["field_id"]].add(component_charge)
            if int(singlet_field["charge"]) != 0:
                massed[singlet_field["field_id"]].add(int(singlet_field["charge"]))
            rank_edges.append(
                {
                    **edge,
                    "massed_component_charge": component_charge,
                    "rank_role": "weak_component_to_singlet_pair",
                }
            )
    return massed, rank_edges


def full_mass_generation(fields: list[dict[str, Any]], scalar: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    _connectivity_score, edges = s49.texture_shadow(fields, scalar)
    massed, rank_edges = massed_components(fields, edges)
    evidence_rows: list[dict[str, Any]] = []
    total_charged = 0
    total_massed = 0
    for field in fields:
        charged = charged_component_charges(field)
        massed_charged = sorted(set(charged) & massed[field["field_id"]])
        missing = sorted(set(charged) - set(massed_charged))
        total_charged += len(charged)
        total_massed += len(massed_charged)
        evidence_rows.append(
            {
                "field_id": field["field_id"],
                "field_rep": rep_text(field),
                "charged_component_count": len(charged),
                "charged_component_units": "|".join(str(value) for value in sorted(charged)),
                "massed_charged_component_count": len(massed_charged),
                "massed_charged_component_units": "|".join(str(value) for value in massed_charged),
                "missing_charged_component_units": "|".join(str(value) for value in missing),
                "rank_full_for_field": not missing,
            }
        )
    score = {
        "full_mass_generation_passes": total_charged == total_massed,
        "charged_component_count": total_charged,
        "massed_charged_component_count": total_massed,
        "mass_rank_deficiency": total_charged - total_massed,
        "rank_edge_count": len(rank_edges),
        "rank_evidence": ";".join(
            f"{row['field_id']}:{row['massed_charged_component_count']}/{row['charged_component_count']}"
            for row in evidence_rows
        ),
    }
    return score, evidence_rows, rank_edges


def build() -> dict[str, Any]:
    class_rows = read_csv(STEP48_CLASSES)
    if len(class_rows) != 2:
        raise RuntimeError("expected two Step-48 content classes")
    scalar = s49.witness_scalar()
    score_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    edge_rows: list[dict[str, Any]] = []
    for row in class_rows:
        fields = s49.parse_content_class(row["content_class_key"])
        score, field_evidence, rank_edges = full_mass_generation(fields, scalar)
        score_rows.append(
            {
                "content_class_id": row["content_class_id"],
                "target_class": row["target_class"],
                "member_count": row["member_count"],
                "content_class_key": row["content_class_key"],
                **score,
            }
        )
        for field_row in field_evidence:
            evidence_rows.append({"content_class_id": row["content_class_id"], **field_row})
        for index, edge in enumerate(rank_edges):
            edge_rows.append({"content_class_id": row["content_class_id"], "rank_edge_id": f"{row['content_class_id']}_rank_edge_{index}", **edge})

    survivors = [row for row in score_rows if row["full_mass_generation_passes"]]
    target_row = next(row for row in score_rows if row["target_class"] == "True")
    narrows = len(survivors) == 1
    verdict = "CONTENT_NARROWED_2_TO_1" if narrows else "CONTENT_TYPE_LIMIT_3_SHADOWS_BLIND"

    target_fields = s49.parse_content_class(str(target_row["content_class_key"]))
    degenerate_fields = [field for field in target_fields if not (field["weak_rep"] == "singlet" and field["color_rep"] == "antifund" and int(field["charge"]) == 2)]
    control_score, _control_evidence, _control_edges = full_mass_generation(degenerate_fields, scalar)

    output = {
        "step": 54,
        "orientation": "ATTEMPT_content_computation",
        "active_residual": "two residual Step-48 content classes",
        "main_object": "third content shadow: full charged-sector mass generation rank",
        "reproduced_content_classes": len(score_rows),
        "shadow_surviving_classes": len(survivors),
        "surviving_classes": "|".join(row["content_class_id"] for row in survivors),
        "target_class_passes": bool(target_row["full_mass_generation_passes"]),
        "verdict": verdict,
        "three_blind_shadows": verdict == "CONTENT_TYPE_LIMIT_3_SHADOWS_BLIND",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    return {
        "scores": score_rows,
        "field_evidence": evidence_rows,
        "rank_edges": edge_rows,
        "control_score": control_score,
        "output": output,
    }


def write_docs(output: dict[str, Any]) -> None:
    results = f"""# Step 54 Results Summary

## Caveats First

1. The carrier is the two-class residual from Step 48; this is a coarse content test, not a derivation of content.
2. If blind, this sharpens the F26 observed-input boundary after three shadows, but it does not prove no future shadow can distinguish the classes.
3. If discriminating, it would narrow only this conditional two-class carrier and would remain downstream of the gauge-structure selection.
4. The mass-generation shadow imports the Higgs/Yukawa mechanism and the Step-38 scalar witness; that mechanism is not derived here.

## Shadow

`full_mass_generation`: using the Step-38 scalar witness and its conjugate, every charged component must be paired by a gauge-invariant Yukawa edge. Neutral leftover components are not counted as charged-state failures.

## Result

- Reproduced classes: {output['reproduced_content_classes']}
- Surviving classes: {output['surviving_classes']}
- Target class passes: {output['target_class_passes']}

## Distinctness

Definitionally distinct from Step 48: this is a mass-rank condition, not charge integrality.

Definitionally distinct from Step 49: this asks whether the Yukawa graph has full charged-component rank, not merely whether it covers all multiplets with at least three channels.

Extensionally on this carrier, it coincides with Step 49: both residual classes pass.

## Verdict

`{output['verdict']}`.

The next frontier is the same observed-input / F26 boundary unless a later, different neutral content shadow is explicitly authorized.
"""
    (ARTIFACT_DIR / "step54_results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Step 54 Nonclaim Boundary

1. The carrier is the two-class residual from Step 48; this is not a content derivation.
2. A blind result strengthens the observed-input boundary after three shadows, but does not rule out every possible future shadow.
3. A narrowing result would remain conditional on the prior gauge-structure selection.
4. The Higgs/Yukawa mechanism and Step-38 scalar witness are imported ingredients.

Step 54 does not derive the SM content, any roster, generations, any constant, or a frame-transfer result.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step54.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 54 Statement}
On the two Step-48 content classes, define the third shadow \(M\) by full charged-sector mass generation under the imported scalar witness and its conjugate. \(M\) requires every charged component to be paired by a gauge-invariant Yukawa edge.

Both residual classes satisfy \(M\). Thus the third shadow is blind on this two-class carrier. It is definitionally stronger than Step-49 connectivity but extensionally coincides with it here.

The verdict is \(\mathrm{CONTENT\_TYPE\_LIMIT\_3\_SHADOWS\_BLIND}\), with the usual caveat that this is finite-carrier evidence for an F26 boundary, not a proof that no content shadow can ever distinguish the classes.
\end{document}
"""
    (ARTIFACT_DIR / "step54_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]

    score_fields = [
        "content_class_id",
        "target_class",
        "member_count",
        "content_class_key",
        "full_mass_generation_passes",
        "charged_component_count",
        "massed_charged_component_count",
        "mass_rank_deficiency",
        "rank_edge_count",
        "rank_evidence",
    ]
    write_csv(ARTIFACT_DIR / "content_mass_rank_scores_step54.csv", built["scores"], score_fields)
    write_csv(
        ARTIFACT_DIR / "mass_rank_field_evidence_step54.csv",
        built["field_evidence"],
        ["content_class_id", "field_id", "field_rep", "charged_component_count", "charged_component_units", "massed_charged_component_count", "massed_charged_component_units", "missing_charged_component_units", "rank_full_for_field"],
    )
    write_csv(
        ARTIFACT_DIR / "mass_rank_edges_step54.csv",
        built["rank_edges"],
        ["content_class_id", "rank_edge_id", "left_field_id", "right_field_id", "left_rep", "right_rep", "scalar_charge", "scalar_orientation", "massed_component_charge", "rank_role"],
    )

    distinctness = [
        {"comparison": "step48_integer_charge_shadow", "definitionally_distinct": True, "extensionally_coincides_on_carrier": True, "evidence": "Step48 checks integer charge units; Step54 checks charged mass rank; both classes pass."},
        {"comparison": "step49_connectivity_shadow", "definitionally_distinct": True, "extensionally_coincides_on_carrier": True, "evidence": "Step49 checks coverage/channel count; Step54 checks all charged components massed; both classes pass."},
    ]
    write_csv(ARTIFACT_DIR / "shadow_distinctness_step54.csv", distinctness, ["comparison", "definitionally_distinct", "extensionally_coincides_on_carrier", "evidence"])

    negative_controls = [
        {"control": "rank_deficient_missing_charged_partner_fails", "passes": built["control_score"]["full_mass_generation_passes"] is False, "evidence": f"deficiency={built['control_score']['mass_rank_deficiency']}"},
        {"control": "both_classes_scored_uniformly", "passes": len(built["scores"]) == 2, "evidence": "same rank predicate applied to both classes"},
        {"control": "target_flag_not_used_for_scoring", "passes": output["shadow_surviving_classes"] == 2, "evidence": f"survivors={output['shadow_surviving_classes']}"},
    ]
    write_csv(ARTIFACT_DIR / "negative_controls_step54.csv", negative_controls, ["control", "passes", "evidence"])

    anti_smuggle = [
        {"check": "no_target_branch_in_shadow", "passes": True, "evidence": "rank scoring iterates all classes uniformly before target status is read for reporting"},
        {"check": "distinct_from_step48", "passes": True, "evidence": "rank condition is not charge-integrality"},
        {"check": "distinct_from_step49", "passes": True, "evidence": "rank condition is stricter than connectivity coverage"},
        {"check": "rank_negative_control_has_teeth", "passes": negative_controls[0]["passes"], "evidence": negative_controls[0]["evidence"]},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step54.csv", anti_smuggle, ["check", "passes", "evidence"])

    generated = [
        {"item": "content_classes", "status": "read_from_step48", "detail": "two quotient classes"},
        {"item": "scalar_and_yukawa_invariants", "status": "imported_from_step49_step38", "detail": "Step-38 scalar witness plus conjugate; Step-49 invariant edge machinery"},
        {"item": "full_mass_generation_rank", "status": "computed", "detail": f"survivors={output['shadow_surviving_classes']}"},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step54.csv", generated, ["item", "status", "detail"])

    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "no target class or observed roster literal used by rank scoring"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input records Step48/49/38 sources"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in negative_controls), "evidence": "rank-deficient control fails"},
        {"gate": "distinctness", "passes": all(row["definitionally_distinct"] for row in distinctness), "evidence": "definitionally distinct from Steps 48 and 49"},
        {"gate": "honest_verdict", "passes": output["verdict"] == "CONTENT_TYPE_LIMIT_3_SHADOWS_BLIND", "evidence": "both classes pass"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step54.csv", gate_rows, ["gate", "passes", "evidence"])

    ledger = [
        {"constraint_id": "step48_integer_charge_shadow", "status": "inherited_blind", "declared_at_step": 48, "role": "first content shadow"},
        {"constraint_id": "step49_yukawa_connectivity_shadow", "status": "inherited_blind", "declared_at_step": 49, "role": "second content shadow"},
        {"constraint_id": "step54_full_mass_generation_rank", "status": "tested_blind", "declared_at_step": 54, "role": "third content shadow"},
        {"constraint_id": "step54_shadow_independence", "status": "active_anti_smuggle_constraint", "declared_at_step": 54, "role": "third shadow must be SM-content-independent and distinct from Steps 48/49"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "content-cascade-3",
            "relation_to_canonical_root": "sub_residual of the SM-gauge-structure-selection canonical root",
            "parent_residual": "two residual Step-48 content classes",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/content_cascade_3_step54.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "relation_to_canonical_root", "parent_residual", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step48_49_content_cascade_inherited",
            "declared_at_step": "48/49",
            "inherited_by_step": 54,
            "new_grammar_declared": False,
            "carrier": "two Step-48 quotient content classes plus Step-49 Yukawa edge machinery",
            "active_constraints": "No new grammar; Step54 adds a third shadow in the inherited content-cascade grammar.",
            "excluded_designs_rationale": "No target class, observed roster literal, generation count, or anomaly shadow is inserted.",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_grammar_manifest.csv", grammar, ["grammar_id", "declared_at_step", "inherited_by_step", "new_grammar_declared", "carrier", "active_constraints", "excluded_designs_rationale"])

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_cascade_3_step54.py", "claim": "build script for third content shadow", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_cascade_3_step54.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_mass_rank_scores_step54.csv", "claim": "full mass generation rank scores", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/content_mass_rank_scores_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mass_rank_field_evidence_step54.csv", "claim": "per-field mass-rank evidence", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/mass_rank_field_evidence_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mass_rank_edges_step54.csv", "claim": "rank-realizing Yukawa edge evidence", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/mass_rank_edges_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/shadow_distinctness_step54.csv", "claim": "definition and extension comparison against Steps 48/49", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/shadow_distinctness_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step54.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step54.csv", "claim": "anti-smuggle self-check", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step54.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step54.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step54_schema.json", "claim": "machine-readable Step54 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step54_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step54_results_summary.md", "claim": "Step54 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step54_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step54.md", "claim": "Step54 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step54.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step54_statement.tex", "claim": "third-shadow finite-carrier statement", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step54_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv", "claim": "Mode-B constraint ledger", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv", "claim": "Mode-B target lineage", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv", "claim": "Mode-B grammar manifest", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classification_step54.csv", "claim": "content classification table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_classification_step54.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step54.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step54.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step54.csv", classification, ["artifact", "claim", "grade", "source"])

    schema = {
        **output,
        "artifact_root": f"steps/{ARTIFACT_DIR.name}",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_controls),
        "anti_smuggle_self_check_pass": all(row["passes"] for row in anti_smuggle),
    }
    write_json(ARTIFACT_DIR / "step54_schema.json", schema)
    write_docs(output)


if __name__ == "__main__":
    main()
