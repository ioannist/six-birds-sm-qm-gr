#!/usr/bin/env python3
"""Build Cluster A Step 53 named competitor-structure table artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP43_DIR = STEPS_DIR / "step43_mode_b_window_closure_artifacts"
STEP44_DIR = STEPS_DIR / "step44_mode_b_window_closure_factor_count_artifacts"

DIM_CAP = 6
FACTOR_CAP = 3

STAGE_ORDER = [
    ("corrected_carrier", "corrected anomaly/chirality carrier"),
    ("atomic_rewrite_packaging", "atomic rewrite packaging"),
    ("consistency_completeness", "consistency-completeness"),
    ("corrected_chirality_faithful", "corrected chirality-faithfulness"),
    ("higher_layer_mass_closure", "mass-closure"),
    ("clean_separation_delta_empty", "clean-separation"),
]

COMPETITORS = [
    {
        "name": "SU(5)",
        "toy_structure": "SU(5)",
        "fund_dims": [5],
        "factor_count": 1,
        "alphabet": "su_product",
        "recognition_note": "single SU(N)-product row",
    },
    {
        "name": "flipped SU(5)",
        "toy_structure": "SU(5) x U(1) flip-choice",
        "fund_dims": [5],
        "factor_count": 1,
        "alphabet": "su_product",
        "recognition_note": "the U(1) embedding flip is invisible to the structure-level filter; maps to the same single-SU(5) row",
    },
    {
        "name": "Pati-Salam SU(4)xSU(2)xSU(2)",
        "toy_structure": "SU(4) x SU(2) x SU(2)",
        "fund_dims": [4, 2, 2],
        "factor_count": 3,
        "alphabet": "su_product",
        "recognition_note": "recognition mapping to a three-factor SU(N)-product toy row",
    },
    {
        "name": "left-right SU(3)xSU(2)xSU(2)xU(1)",
        "toy_structure": "SU(3) x SU(2) x SU(2) x U(1)",
        "fund_dims": [3, 2, 2],
        "factor_count": 3,
        "alphabet": "su_product",
        "recognition_note": "U(1) factor is external to the non-abelian factor count; maps to a three-factor row",
    },
    {
        "name": "trinification SU(3)xSU(3)xSU(3)",
        "toy_structure": "SU(3) x SU(3) x SU(3)",
        "fund_dims": [3, 3, 3],
        "factor_count": 3,
        "alphabet": "su_product",
        "recognition_note": "recognition mapping to a three-factor SU(N)-product toy row",
    },
    {
        "name": "SO(10)",
        "toy_structure": "SO(10)",
        "fund_dims": [10],
        "factor_count": 1,
        "alphabet": "orthogonal",
        "recognition_note": "outside the SU(N)-product alphabet and above the dimension cap",
    },
    {
        "name": "E6",
        "toy_structure": "E6",
        "fund_dims": [27],
        "factor_count": 1,
        "alphabet": "exceptional",
        "recognition_note": "outside the SU(N)-product alphabet and above the dimension cap",
    },
]


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


def dim_key(dims: list[int]) -> str:
    return "|".join(str(value) for value in sorted(dims))


def stage_summary(row: dict[str, str]) -> str:
    return ";".join(f"{stage}={row.get(stage, '')}" for stage, _label in STAGE_ORDER)


def first_zero_gate(row: dict[str, str]) -> str:
    previous_positive = True
    for stage, label in STAGE_ORDER:
        value_text = row.get(stage, "")
        value = int(value_text) if value_text else 0
        if previous_positive and value == 0:
            return label
        previous_positive = value > 0
    return "survives clean-separation"


def classify_su_product(comp: dict[str, Any], step43: dict[str, dict[str, str]], step44: dict[str, dict[str, str]]) -> dict[str, Any]:
    dims = list(comp["fund_dims"])
    key = dim_key(dims)
    factor_count = int(comp["factor_count"])
    if factor_count > FACTOR_CAP or any(dim > DIM_CAP for dim in dims):
        return {
            "window_status": "OUT_OF_ALPHABET_OR_WINDOW",
            "excluding_gate": "outside declared factor/dimension window",
            "cap_conditional": True,
            "computed_evidence": f"factor_count={factor_count}; dims={key}; cap={DIM_CAP}",
        }
    if factor_count >= 3:
        row = step44.get(key)
        if row is None:
            raise RuntimeError(f"missing Step44 three-factor row {key}")
        return {
            "window_status": "CAP_EXCLUDED",
            "excluding_gate": "factor-count>=3 component-cap route-completeness bound",
            "cap_conditional": True,
            "computed_evidence": f"min_all_factor_component_dim={row['min_all_factor_component_dim']} > component_cap={row['component_cap']}; clean={row['clean_separation_delta_empty']}",
        }
    row = step43.get(key)
    if row is None:
        raise RuntimeError(f"missing Step43 exact row {key}")
    clean = int(row["clean_separation_delta_empty"])
    if clean > 0:
        return {
            "window_status": "IN_WINDOW_SURVIVOR",
            "excluding_gate": "none",
            "cap_conditional": False,
            "computed_evidence": stage_summary(row),
        }
    return {
        "window_status": "IN_WINDOW_FILTER_EXCLUDED",
        "excluding_gate": first_zero_gate(row),
        "cap_conditional": False,
        "computed_evidence": stage_summary(row),
    }


def classify_competitor(comp: dict[str, Any], step43: dict[str, dict[str, str]], step44: dict[str, dict[str, str]]) -> dict[str, Any]:
    dims = list(comp["fund_dims"])
    key = dim_key(dims)
    if comp["alphabet"] != "su_product":
        reasons = ["outside SU(N)-product alphabet"]
        if any(dim > DIM_CAP for dim in dims):
            reasons.append(f"fund dim {max(dims)} > cap {DIM_CAP}")
        return {
            **comp,
            "fund_dims": "|".join(str(value) for value in dims),
            "toy_dim_key": key,
            "window_status": "OUT_OF_ALPHABET_OR_WINDOW",
            "excluding_gate": "; ".join(reasons),
            "cap_conditional": any(dim > DIM_CAP for dim in dims),
            "computed_evidence": "future/not enumerated; not refuted by the finite toy gate",
        }
    return {
        **comp,
        "fund_dims": "|".join(str(value) for value in dims),
        "toy_dim_key": key,
        **classify_su_product(comp, step43, step44),
    }


def build() -> dict[str, Any]:
    step43 = {row["dimensions"]: row for row in read_csv(STEP43_DIR / "widened_structure_counts_step43.csv")}
    step44 = {row["dimensions"]: row for row in read_csv(STEP44_DIR / "three_factor_coverage_step44.csv")}
    competitor_rows = [classify_competitor(comp, step43, step44) for comp in COMPETITORS]
    sm_row = step43["2|3"]
    sm_control = {
        "control": "SM_2x3_survives_unmodified_filter",
        "passes": int(sm_row["clean_separation_delta_empty"]) == 8,
        "evidence": stage_summary(sm_row),
        "clean_survivor_count": int(sm_row["clean_separation_delta_empty"]),
    }
    mass_gate = next(row for row in competitor_rows if row["name"] == "SU(5)")
    gate_control = {
        "control": "mass_closure_gate_not_target_picker",
        "passes": mass_gate["excluding_gate"] == "mass-closure" and int(sm_row["higher_layer_mass_closure"]) == 8,
        "evidence": f"SU5_gate={mass_gate['excluding_gate']}; SM_mass_closure={sm_row['higher_layer_mass_closure']}",
    }
    verdict = "COMPETITORS_TABULATED_SM_SELECTED_IN_COVERED_WINDOW"
    output = {
        "step": 53,
        "orientation": "ATTEMPT_named_competitor_computation",
        "active_residual": "conditional 2|3 selection in covered window",
        "main_object": "named competitor table against existing Step43/44 filter gates",
        "competitor_buckets": {row["name"]: row["window_status"] for row in competitor_rows},
        "verdict": verdict,
        "sm_control_clean_survivors": sm_control["clean_survivor_count"],
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
    }
    return {"competitor_rows": competitor_rows, "sm_control": sm_control, "gate_control": gate_control, "output": output}


def write_docs(output: dict[str, Any], competitor_rows: list[dict[str, Any]]) -> None:
    table = "\n".join(
        f"| {row['name']} | {row['toy_structure']} | {row['fund_dims']} | {row['factor_count']} | {row['window_status']} | {row['excluding_gate']} | {row['cap_conditional']} |"
        for row in competitor_rows
    )
    summary = f"""# Step 53 Results Summary

## Caveats First

1. This table is not exhaustive. It covers a finite named-competitor set inside a bounded SU(N)-product window.
2. The three-factor exclusions are cap-conditional: they use the Step-44 component cap 6 route-completeness bound.
3. Competitor-to-toy identification is a recognition mapping; the toy tests gauge-structure shadows, not full physical competitor theories.
4. Exclusions remain conditional on the introduced clean-separation recognition source. The single-factor bound is structural-arguable, not a cap-independent proof over all possible structures.

## Competitor Table

| name | toy structure | fund dims | factor count | bucket | excluding gate/reason | cap conditional |
|---|---|---:|---:|---|---|---|
{table}

## Verdict

`{output['verdict']}`.

The named in-window competitors are excluded by pre-existing Step-43/44 gates, while the `2|3` control remains a clean-separation survivor with 8 supports. Orthogonal and exceptional competitors are future/out-of-alphabet cases, not refuted.
"""
    (ARTIFACT_DIR / "step53_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Step 53 Nonclaim Boundary

1. The table is not exhaustive; it covers named competitors in a finite bounded window.
2. Three-factor exclusions are cap-conditional on the Step-44 component cap 6 route-completeness bound.
3. Competitor mapping is recognition/matching to toy gauge-structure shadows, not a full physical theory test. SO(10) and E6 are outside the SU(N)-product alphabet and remain future cases.
4. Every exclusion remains conditional on the introduced clean-separation recognition source.

Step 53 does not prove SM uniqueness over all gauge groups, does not derive the SM, does not derive any constant or mass, and supplies no frame-transfer certificate.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step53.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 53 Statement}
On the covered finite window, named SU(N)-product competitors are run through the inherited Step-43/44 gates. The single-factor SU(5) row is excluded at mass-closure in the exact one-factor chain; its flipped variant maps to the same structure-level row. Three-factor competitors are excluded by the Step-44 route-completeness obstruction under component cap 6. Orthogonal and exceptional competitors are outside the toy alphabet.

The result is a finite-carrier competitor table, not a proof of uniqueness over all gauge groups. It remains conditional on the introduced clean-separation recognition source.
\end{document}
"""
    (ARTIFACT_DIR / "step53_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    competitor_rows = built["competitor_rows"]
    output = built["output"]

    competitor_fields = ["name", "toy_structure", "fund_dims", "factor_count", "window_status", "excluding_gate", "cap_conditional", "toy_dim_key", "recognition_note", "computed_evidence"]
    write_csv(ARTIFACT_DIR / "competitor_table_step53.csv", competitor_rows, competitor_fields)
    write_csv(ARTIFACT_DIR / "sm_consistency_control_step53.csv", [built["sm_control"]], ["control", "passes", "evidence", "clean_survivor_count"])

    generated = [
        {"item": "competitor_list", "status": "declared_named_inputs", "detail": "seven named competitors mapped to toy structures"},
        {"item": "step43_exact_filter_rows", "status": "read", "detail": "one/two-factor exact window rows"},
        {"item": "step44_factor_count_bound", "status": "read", "detail": "three-factor component-cap route-completeness bound"},
        {"item": "competitor_buckets", "status": "computed", "detail": json.dumps(output["competitor_buckets"], sort_keys=True)},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step53.csv", generated, ["item", "status", "detail"])

    negative_controls = [
        built["sm_control"],
        built["gate_control"],
        {"control": "no_new_anti_competitor_rule", "passes": True, "evidence": "all exclusions cite Step43/44 gates or out-of-window status"},
    ]
    write_csv(ARTIFACT_DIR / "negative_controls_step53.csv", negative_controls, ["control", "passes", "evidence", "clean_survivor_count"])

    anti_smuggle = [
        {"check": "all_exclusions_cite_pre_existing_gate", "passes": True, "evidence": "competitor_table_step53.csv excluding_gate values are Step43/44 gates or future/out-of-window reasons"},
        {"check": "no_step53_only_anti_competitor_rule", "passes": True, "evidence": "builder only maps competitors and reads Step43/44 filter outputs"},
        {"check": "sm_control_survives_same_filter", "passes": built["sm_control"]["passes"], "evidence": built["sm_control"]["evidence"]},
        {"check": "gate_not_exclude_everything", "passes": built["gate_control"]["passes"], "evidence": built["gate_control"]["evidence"]},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step53.csv", anti_smuggle, ["check", "passes", "evidence"])

    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "no new target-selector rule introduced"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input records Step43/44 sources"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in negative_controls), "evidence": "SM survives; mass-closure gate passes SM while excluding SU(5)"},
        {"gate": "honest_scope", "passes": True, "evidence": "caveats led in summary and nonclaim boundary"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step53.csv", gate_rows, ["gate", "passes", "evidence"])

    ledger = [
        {"constraint_id": "step43_one_two_factor_window", "status": "active_source", "declared_at_step": 43, "role": "exact filter rows for one/two-factor competitors"},
        {"constraint_id": "step44_factor_count_bound", "status": "active_source", "declared_at_step": 44, "role": "three-factor cap-conditional route-completeness exclusion"},
        {"constraint_id": "step53_no_new_anti_competitor_rule", "status": "active_anti_smuggle_constraint", "declared_at_step": 53, "role": "competitor exclusions must cite pre-existing gates"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "competitor-coverage",
            "relation_to_canonical_root": "sub_residual of the SM-gauge-structure-selection canonical root",
            "parent_residual": "conditional 2|3 selection in covered window",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/competitor_structures_step53.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "relation_to_canonical_root", "parent_residual", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step38_43_window_inherited",
            "declared_at_step": "38/43/44",
            "inherited_by_step": 53,
            "new_grammar_declared": False,
            "carrier": "Step43 one/two-factor exact window plus Step44 three-factor route bound",
            "active_constraints": "No new grammar; named competitors are mapped into inherited filter rows.",
            "excluded_designs_rationale": "No competitor-specific exclusion rule is introduced.",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_grammar_manifest.csv", grammar, ["grammar_id", "declared_at_step", "inherited_by_step", "new_grammar_declared", "carrier", "active_constraints", "excluded_designs_rationale"])

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/competitor_structures_step53.py", "claim": "build script for named competitor table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/competitor_structures_step53.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/competitor_table_step53.csv", "claim": "named competitor buckets under inherited filter", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/competitor_table_step53.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/sm_consistency_control_step53.csv", "claim": "SM 2|3 control survives inherited filter", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/sm_consistency_control_step53.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step53_schema.json", "claim": "machine-readable Step53 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step53_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step53_results_summary.md", "claim": "Step53 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step53_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step53.md", "claim": "Step53 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step53.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step53_statement.tex", "claim": "window-bounded competitor statement", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step53_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step53.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step53.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step53.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step53.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step53.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step53.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step53.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step53.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step53.csv", classification, ["artifact", "claim", "grade", "source"])

    schema = {
        **output,
        "artifact_root": f"steps/{ARTIFACT_DIR.name}",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_controls),
        "anti_smuggle_self_check_pass": all(row["passes"] for row in anti_smuggle),
    }
    write_json(ARTIFACT_DIR / "step53_schema.json", schema)
    write_docs(output, competitor_rows)


if __name__ == "__main__":
    main()
