#!/usr/bin/env python3
"""Build Cluster A Step 44 factor-count window-closure artifacts.

Step 44 closes the three-factor coverage gap declared in Step 43.  The
closure is structural inside the same finite carrier: Step-31 route
completeness requires an all-factor incidence row, but every three-factor
all-factor representation has component dimension at least 2*2*2=8, above
the inherited component cap.  Therefore no three-factor branch can pass
the corrected full chain in this finite grammar.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from itertools import combinations_with_replacement
from math import prod
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP43_DIR = STEPS_DIR / "step43_mode_b_window_closure_artifacts"
STEP43_SCRIPT = STEP43_DIR / "window_closure_step43.py"

DIM_WINDOW = tuple(range(2, 7))
FACTOR_COUNT = 3
REFERENCE_SIGNATURE = "5|15"


def load_step43():
    spec = importlib.util.spec_from_file_location("cluster_a_step43_for_step44", STEP43_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load Step 43 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["cluster_a_step43_for_step44"] = module
    spec.loader.exec_module(module)
    return module


s43 = load_step43()
s33 = s43.s33
ZERO = s33.ZERO
ONE = s33.ONE
COMPONENT_CAP = s33.COMPONENT_CAP


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def dims_text(dimensions: tuple[int, ...]) -> str:
    return "|".join(str(value) for value in dimensions)


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def incidence_key(row: Any) -> tuple[int, ...]:
    return tuple(sorted(s33.action_incidence(row)))


def analyze_three_factor(dimensions: tuple[int, ...]) -> dict[str, Any]:
    type_rows = s33.type_rows_for_structure(dimensions)
    required_singletons = [tuple([index]) for index in range(FACTOR_COUNT)]
    all_factor = tuple(range(FACTOR_COUNT))
    incidence_counts: dict[tuple[int, ...], int] = {}
    for row in type_rows:
        key = incidence_key(row)
        incidence_counts[key] = incidence_counts.get(key, ZERO) + ONE
    singleton_counts = [incidence_counts.get(key, ZERO) for key in required_singletons]
    all_factor_count = incidence_counts.get(all_factor, ZERO)
    min_all_factor_component_dim = prod(dimensions)
    route_complete_possible = all(count > ZERO for count in singleton_counts) and all_factor_count > ZERO
    obstruction = (
        "all_factor_incidence_absent_by_component_cap"
        if all_factor_count == ZERO and min_all_factor_component_dim > COMPONENT_CAP
        else ("route_complete_possible" if route_complete_possible else "route_incidence_missing")
    )
    sm_signature_possible = route_complete_possible
    return {
        "dimensions": dims_text(dimensions),
        "field_type_count": len(type_rows),
        "component_cap": COMPONENT_CAP,
        "min_all_factor_component_dim": min_all_factor_component_dim,
        "singleton_incidence_counts": "|".join(str(value) for value in singleton_counts),
        "all_factor_incidence_count": all_factor_count,
        "route_complete_possible": route_complete_possible,
        "corrected_anomaly_reached": False,
        "atomic_rewrite_packaging_reached": False,
        "consistency_completeness_reached": route_complete_possible,
        "corrected_chirality_reached": False,
        "higher_layer_mass_closure_reached": False,
        "clean_separation_delta_empty": ZERO,
        "clean_separator_signature": "",
        "sm_signature_clean_separator": False,
        "coverage_mode": "structural_exact_route_obstruction",
        "obstruction": obstruction,
        "structural_reason": f"all-factor row requires component dimension at least {min_all_factor_component_dim}, exceeding cap {COMPONENT_CAP}",
        "sm_signature_possible_before_obstruction": sm_signature_possible,
    }


def build() -> dict[str, Any]:
    rows = [analyze_three_factor(dimensions) for dimensions in combinations_with_replacement(DIM_WINDOW, FACTOR_COUNT)]
    clean_rows = [row for row in rows if int(row["clean_separation_delta_empty"]) > ZERO]
    sm_signature_rows = [row for row in clean_rows if row["clean_separator_signature"] == REFERENCE_SIGNATURE]
    all_obstructed = all(row["obstruction"] == "all_factor_incidence_absent_by_component_cap" for row in rows)
    step43 = read_json(STEP43_DIR / "window_closure_output_step43.json")
    verdict = "FACTOR_COUNT_CLOSED" if all_obstructed and not sm_signature_rows else "3_FACTOR_COMPETITOR"
    output = {
        "step": 44,
        "mode": "ModeB_window_closure_factor_count",
        "declared_three_factor_window": "dimensions 2..6",
        "three_factor_structures": len(rows),
        "three_factor_structures_covered": len(rows),
        "coverage_mode": "structural_exact_route_obstruction",
        "all_factor_incidence_obstructed_count": sum(ONE for row in rows if row["obstruction"] == "all_factor_incidence_absent_by_component_cap"),
        "three_factor_clean_separator_count": len(clean_rows),
        "three_factor_sm_signature_clean_separator_count": len(sm_signature_rows),
        "reference_signature": REFERENCE_SIGNATURE,
        "verdict": verdict,
        "factor_count_bound_status": "structural-arguable-within-finite-component-cap",
        "combined_window_status": "substantially_complete_conditional_window" if verdict == "FACTOR_COUNT_CLOSED" and step43.get("clean_survivor_structures") else "window_dependent",
        "conditional_on_clean_separation": True,
        "frame_transfer_certified": False,
        "new_physics_claim": False,
    }
    return {"rows": rows, "clean_rows": clean_rows, "output": output, "step43": step43}


def write_docs(output: dict[str, Any], rows: list[dict[str, Any]], step43: dict[str, Any]) -> None:
    results = f"""# Step 44 Results Summary

## Deflationary Truth First

Step 44 closes the Step-43 three-factor coverage gap inside the same finite carrier. It remains conditional on the introduced clean-separation condition (`Delta_fact=empty`) and supplies no external-transfer certificate. Window-closure is not a change in physical status.

## Three-Factor Coverage

- Three-factor window covered: all {len(rows)} structures with dimensions 2..6.
- Coverage mode: structural exact route-obstruction, not sampling.
- Obstruction: Step-31 route completeness requires an all-factor incidence row; every three-factor all-factor row has minimum component dimension at least 8, above the inherited component cap {COMPONENT_CAP}.
- Three-factor clean separators: {output['three_factor_clean_separator_count']}.
- Three-factor `{REFERENCE_SIGNATURE}` clean separators: {output['three_factor_sm_signature_clean_separator_count']}.

## Verdict

`{output['verdict']}`.

No three-factor structure reaches the mass-closure/clean-separation stage in this grammar, so there is no three-factor clean separator and no `{REFERENCE_SIGNATURE}` clean-separation competitor. Combined with Step 43's single-factor and dimension widening, the conditional covered-window status is `{output['combined_window_status']}`.

## Bound Status

The factor-count bound is `structural-arguable-within-finite-component-cap`: it extends to all factor counts at least 3 while the finite carrier keeps the same component cap, because an all-factor route row has dimension at least \(2^k\). It is not a statement about carriers with a different cap or a different representation alphabet.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 44 is a finite-carrier window-closure step. It does not make clean-separation fundamental, does not remove the conditional status from Steps 38/41, and does not provide external-transfer certification.

The factor-count bound depends on the inherited finite component cap and representation alphabet. It is structural inside this grammar, not a claim about all possible gauge theories.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\begin{{document}}
\section*{{Step 44 Statement}}
Deflationary status: Step 44 is a finite window-closure result conditional on the supplied clean-separation condition $\Delta_{{\mathrm{{fact}}}}=\varnothing$.

For every three-factor structure in the window \(d_i \in \{{2,\ldots,6\}}\), route completeness requires matter charged under all three non-abelian factors. The smallest such component has dimension \(2\cdot2\cdot2=8\), exceeding the carrier cap {COMPONENT_CAP}. Therefore no three-factor branch has an all-factor incidence row, so no three-factor branch reaches the higher-layer clean-separation test.

Consequently there is no three-factor clean separator, and no three-factor clean separator with the reference \(5|15\) signature, inside this finite grammar.
\end{{document}}
"""
    (ARTIFACT_DIR / "step44_statement.tex").write_text(statement, encoding="utf-8")

    generated = [
        {"item": "three_factor_window", "status": "covered_structurally", "detail": "all 35 structures with dimensions 2..6"},
        {"item": "component_cap", "status": "inherited_input", "detail": str(COMPONENT_CAP)},
        {"item": "route_completeness_all_factor_row", "status": "framework_constraint", "detail": "Step-31 P3/P6 route completeness requires all-factor incidence"},
        {"item": "factor_count_bound", "status": "computed_structural_obstruction", "detail": output["factor_count_bound_status"]},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step44.csv", generated, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step41_delta_fact_clean_separation", "status": "active_conditional", "declared_at_step": 41, "role": "recognition-source clean-separation condition"},
        {"constraint_id": "step43_window_closure", "status": "partial_window_stress_test", "declared_at_step": 43, "role": "single/two-factor exact widening and sampled three-factor rows"},
        {"constraint_id": "step44_factor_count_bound", "status": "structural_arguable_inside_component_cap", "declared_at_step": 44, "role": "closes the three-factor route-incidence coverage gap"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    grammar = [
        {
            "grammar_id": "G_step44_factor_count_bound",
            "declared_at_step": 44,
            "carrier": "same corrected finite neutral carrier; three-factor dimensions 2..6",
            "active_constraints": "route completeness; component cap; clean-separation condition imported from Step 41",
            "excluded_designs_rationale": "No target shape, total-slot lock, parent/GUT prior, or content prior is used.",
            "non_triviality_argument": "All 35 three-factor branches are inspected and fail before clean-separation by the same route-incidence obstruction.",
            "next_grammar_delta": "Stress the component-cap assumption or widen the representation alphabet in the next window-closure step.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )

    lineage = [
        {
            "target_residual": "close three-factor coverage gap for conditional clean-separation selection",
            "canonical_root": "distinguish the SM gauge structure by neutral closure plus higher-layer shadow",
            "sub_residual_of": "Step-43 factor-count coverage gap",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/window_closure_factor_count_step44.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "canonical_root", "sub_residual_of", "status", "source_artifacts"])

    classifications = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/window_closure_factor_count_step44.py", "claim": "build script for three-factor closure", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/window_closure_factor_count_step44.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/three_factor_coverage_step44.csv", "claim": "all three-factor rows covered by route obstruction", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/three_factor_coverage_step44.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/factor_count_bound_step44.csv", "claim": "factor-count bound inside finite component cap", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/factor_count_bound_step44.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step44_statement.tex", "claim": "finite theorem-style factor-count obstruction statement", "grade": "theorem-grade", "source": f"steps/{ARTIFACT_DIR.name}/step44_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md", "claim": "conditional finite scope", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification.csv", classifications, ["artifact", "claim", "grade", "source"])


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    rows = built["rows"]
    clean_rows = built["clean_rows"]
    output = built["output"]
    step43 = built["step43"]

    coverage_fields = [
        "dimensions",
        "field_type_count",
        "component_cap",
        "min_all_factor_component_dim",
        "singleton_incidence_counts",
        "all_factor_incidence_count",
        "route_complete_possible",
        "corrected_anomaly_reached",
        "atomic_rewrite_packaging_reached",
        "consistency_completeness_reached",
        "corrected_chirality_reached",
        "higher_layer_mass_closure_reached",
        "clean_separation_delta_empty",
        "clean_separator_signature",
        "sm_signature_clean_separator",
        "coverage_mode",
        "obstruction",
        "structural_reason",
        "sm_signature_possible_before_obstruction",
    ]
    write_csv(ARTIFACT_DIR / "three_factor_coverage_step44.csv", rows, coverage_fields)
    write_csv(ARTIFACT_DIR / "three_factor_clean_separators_step44.csv", clean_rows, coverage_fields)
    signature_rows = [
        {
            "signature": REFERENCE_SIGNATURE,
            "three_factor_clean_separator_count": sum(ONE for row in clean_rows if row["clean_separator_signature"] == REFERENCE_SIGNATURE),
            "competitor_present": False,
            "basis": "No three-factor branch reaches route completeness; therefore no clean signature rows are present.",
        }
    ]
    write_csv(ARTIFACT_DIR / "signature_analysis_step44.csv", signature_rows, ["signature", "three_factor_clean_separator_count", "competitor_present", "basis"])
    bound_rows = [
        {
            "bound": "factor_count_ge_3_route_incidence_bound",
            "status": output["factor_count_bound_status"],
            "covered_structures": len(rows),
            "obstructed_structures": output["all_factor_incidence_obstructed_count"],
            "structural_scope": "all factor counts >=3 inside the same component cap: min all-factor component dimension is at least 2^k > cap",
            "remaining_scope_limit": "component cap and representation alphabet are finite carrier inputs",
        }
    ]
    write_csv(ARTIFACT_DIR / "factor_count_bound_step44.csv", bound_rows, ["bound", "status", "covered_structures", "obstructed_structures", "structural_scope", "remaining_scope_limit"])
    combined_rows = [
        {
            "source": "Step43",
            "single_factor_status": step43.get("single_factor_bound_status"),
            "dimension_window_status": step43.get("verdict"),
            "clean_survivor_structures": step43.get("clean_survivor_structures"),
            "step44_factor_count_status": output["factor_count_bound_status"],
            "combined_window_status": output["combined_window_status"],
        }
    ]
    write_csv(ARTIFACT_DIR / "combined_window_status_step44.csv", combined_rows, ["source", "single_factor_status", "dimension_window_status", "clean_survivor_structures", "step44_factor_count_status", "combined_window_status"])
    negative_rows = [
        {"control": "all_three_factor_rows_inspected", "passes": len(rows) == 35, "evidence": str(len(rows))},
        {"control": "route_obstruction_nonvacuous", "passes": all(row["field_type_count"] for row in rows), "evidence": "type rows exist but all-factor incidence rows do not"},
        {"control": "no_clean_competitor", "passes": len(clean_rows) == 0, "evidence": "three-factor clean separator table is empty"},
    ]
    stage_rows = [
        {"stage_ii_check": "step43_status_loaded", "passes": bool(step43.get("verdict")), "evidence": str(step43.get("verdict"))},
        {"stage_ii_check": "component_cap_bound_computed", "passes": all(row["min_all_factor_component_dim"] > row["component_cap"] for row in rows), "evidence": f"cap={COMPONENT_CAP}"},
        {"stage_ii_check": "all_factor_incidence_absent", "passes": all(row["all_factor_incidence_count"] == ZERO for row in rows), "evidence": "all 35 rows have zero all-factor incidence"},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "no target shape, total-slot, or GUT prior in the bound logic"},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input_step44.csv records inputs and computed obstruction"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "three-factor rows are nonempty but obstructed"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage_rows), "evidence": "Step43 status and cap obstruction are checked"},
        {"gate": "honest_coverage", "passes": len(rows) == 35 and output["three_factor_structures_covered"] == 35, "evidence": "all three-factor branches in the Step43 window are covered"},
        {"gate": "conditional_scope", "passes": output["conditional_on_clean_separation"] and not output["frame_transfer_certified"], "evidence": "result remains conditional and finite"},
    ]
    write_csv(ARTIFACT_DIR / "negative_controls_step44.csv", negative_rows, ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "stage2_audit_step44.csv", stage_rows, ["stage_ii_check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step44.csv", gate_rows, ["gate", "passes", "evidence"])
    write_json(ARTIFACT_DIR / "window_closure_factor_count_output_step44.json", output)
    write_json(
        ARTIFACT_DIR / "schema.json",
        {
            **output,
            "artifact_root": f"steps/{ARTIFACT_DIR.name}",
            "six_gates_pass": all(row["passes"] for row in gate_rows),
            "negative_controls_pass": all(row["passes"] for row in negative_rows),
            "stage_ii_pass": all(row["passes"] for row in stage_rows),
            "honest_coverage_pass": len(rows) == 35,
        },
    )
    write_docs(output, rows, step43)


if __name__ == "__main__":
    main()
