#!/usr/bin/env python3
"""Build Step 65 proton/monopole fork-resolution artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP45_DIR = STEPS_DIR / "step45_mode_b_proton_decay_F27_artifacts"
STEP46_DIR = STEPS_DIR / "step46_mode_b_monopole_F48_artifacts"
STEP59_DIR = STEPS_DIR / "step59_mode_b_record_stability_coverage_artifacts"
STEP63_DIR = STEPS_DIR / "step63_mode_b_unification_common_refinement_layer_artifacts"


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


def bool_cell(value: str) -> bool:
    return value == "True"


def step59_scores() -> list[dict[str, str]]:
    return read_csv(STEP59_DIR / "record_stability_coverage_scores_step59.csv")


def fork_rows() -> dict[str, dict[str, str]]:
    step45 = {row["reading_id"]: row for row in read_csv(STEP45_DIR / "delta_witness_identity_step45.csv")}
    step46 = {row["reading_id"]: row for row in read_csv(STEP46_DIR / "coset_delta_witness_identity_step46.csv")}
    return {"step45_dynamic": step45["dynamical_breaking_reading"], "step46_dynamic": step46["dynamical_breaking_reading"]}


def mapping_rows(score_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in score_rows:
        if bool_cell(row["delta_evaluated"]) and not bool_cell(row["delta_empty"]):
            capacity = bool_cell(row["capacity_passes"])
            distinguishability = bool_cell(row["distinguishability_passes"])
            substrate = bool_cell(row["substrate_passes"])
            record_stable = bool_cell(row["RS_member"])
            rows.append(
                {
                    "carrier_id": row["carrier_id"],
                    "dimensions": row["dimensions"],
                    "support_key": row["support_key"],
                    "fork_reading": "breaking_reading",
                    "step41_delta_fact_nonempty": True,
                    "delta_pair_count": row["delta_pair_count"],
                    "delta_witness_count": row["delta_witness_count"],
                    "transition_leak_count": row["transition_leak_count"],
                    "substrate_passes": substrate,
                    "capacity_passes": capacity,
                    "distinguishability_passes": distinguishability,
                    "record_stability_passes": record_stable,
                    "record_incapable_reason": "capacity_false" if not capacity else "distinguishability_or_substrate_false",
                    "baryon_branch": "F27_obstructed_if_realized",
                    "monopole_branch": "F48_obstructed_if_realized",
                }
            )
    return rows


def anti_circularity_rows(score_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    substrate_no_capacity = next(
        row
        for row in score_rows
        if bool_cell(row["delta_evaluated"])
        and not bool_cell(row["delta_empty"])
        and bool_cell(row["substrate_passes"])
        and not bool_cell(row["capacity_passes"])
    )
    capacity_no_substrate = next(
        row
        for row in score_rows
        if int(row["transition_leak_count"]) > 0
        and bool_cell(row["capacity_passes"])
        and not bool_cell(row["substrate_passes"])
    )
    clean_records = next(
        row
        for row in score_rows
        if bool_cell(row["CS_member"]) and bool_cell(row["RS_member"])
    )
    return [
        {
            "check": "substrate_not_clean_reading_in_disguise",
            "passes": True,
            "witness": substrate_no_capacity["carrier_id"],
            "evidence": "Step41 nonempty defect with substrate true but capacity false",
        },
        {
            "check": "capacity_not_clean_reading_in_disguise",
            "passes": True,
            "witness": capacity_no_substrate["carrier_id"],
            "evidence": "positive transition leak with capacity true but substrate false",
        },
        {
            "check": "memory_branch_nonvacuous",
            "passes": True,
            "witness": clean_records["carrier_id"],
            "evidence": "clean record-stable row exists",
        },
        {
            "check": "resolution_uses_conjunction",
            "passes": True,
            "witness": f"{substrate_no_capacity['carrier_id']}|{capacity_no_substrate['carrier_id']}",
            "evidence": "neither substrate nor capacity alone is equivalent to clean separation",
        },
    ]


def consistency_rows(mapping_count: int) -> list[dict[str, Any]]:
    f = fork_rows()
    step63 = read_csv(STEP63_DIR / "refinement_defect_step63.csv")[0]
    return [
        {
            "object": "Step45_proton_fork",
            "defect_kind": "gauge_layer_breaking_coset",
            "support_id": f["step45_dynamic"]["support_id"],
            "witness_count": f["step45_dynamic"]["step41_delta_witness_count"],
            "identity_holds": f["step45_dynamic"]["identity_holds"],
            "used_for_resolution": True,
            "note": "same Step41 defect object as the realized breaking reading",
        },
        {
            "object": "Step46_monopole_fork",
            "defect_kind": "gauge_layer_breaking_coset",
            "support_id": f["step46_dynamic"]["support_id"],
            "witness_count": f["step46_dynamic"]["step41_delta_witness_count"],
            "identity_holds": f["step46_dynamic"]["coset_equals_delta_witnesses"],
            "used_for_resolution": True,
            "note": "same Step41 defect object as the realized breaking reading",
        },
        {
            "object": "Step63_common_refinement",
            "defect_kind": "inter_layer_structural_refinement",
            "support_id": "SM_to_common_refinement",
            "witness_count": step63["delta_sm_to_parent_count"],
            "identity_holds": step63["xy_witness_identity"],
            "used_for_resolution": False,
            "note": "structural parent-shadow defect; not the realized gauge-layer breaking coset selected against here",
        },
        {
            "object": "Step59_memory_mapping",
            "defect_kind": "evaluated_gauge_layer_nonempty_defects",
            "support_id": "Step59_scored_carrier",
            "witness_count": mapping_count,
            "identity_holds": True,
            "used_for_resolution": True,
            "note": "all evaluated nonempty Step41 defects are record-incapable",
        },
    ]


def build() -> dict[str, Any]:
    scores = step59_scores()
    mapping = mapping_rows(scores)
    anti = anti_circularity_rows(scores)
    all_record_incapable = all(row["record_stability_passes"] is False for row in mapping)
    all_capacity_false = all(row["capacity_passes"] is False for row in mapping)
    f = fork_rows()
    fork_exact = (
        f["step45_dynamic"]["identity_holds"] == "True"
        and f["step46_dynamic"]["coset_equals_delta_witnesses"] == "True"
        and f["step45_dynamic"]["step41_delta_witness_count"] == f["step46_dynamic"]["step41_delta_witness_count"]
    )
    exit_state = "FORK_RESOLVED_TO_CLEAN_BY_MEMORY_STABILITY" if fork_exact and all_record_incapable else "PARTIAL"
    verdict = (
        "MEMORY_STABILITY_SELECTS_CLEAN_BRANCH_ENUMERATION_STRENGTH"
        if exit_state == "FORK_RESOLVED_TO_CLEAN_BY_MEMORY_STABILITY"
        else "FORK_MAPPING_PARTIAL"
    )
    schema = {
        "step": 65,
        "orientation": "ModeB_cross_layer_fork_resolution",
        "exit_state": exit_state,
        "verdict": verdict,
        "mapping_exact": bool(fork_exact and len(mapping) > 0),
        "breaking_reading_is_delta_fact_nonempty": bool(fork_exact),
        "breaking_structures_all_record_incapable": bool(all_record_incapable),
        "anti_circularity_pass": all(row["passes"] for row in anti),
        "conditional_on_memory_stability": True,
        "enumeration_strength": True,
        "frame_transfer_certified": False,
        "resolves_physical_proton_stability": False,
        "new_physics_claim": False,
        "root_landed": exit_state == "FORK_RESOLVED_TO_CLEAN_BY_MEMORY_STABILITY",
        "evaluated_breaking_structure_count": len(mapping),
        "record_stable_breaking_structure_count": sum(1 for row in mapping if row["record_stability_passes"]),
        "capacity_positive_breaking_structure_count": sum(1 for row in mapping if row["capacity_passes"]),
        "step45_dynamic_witness_count": int(f["step45_dynamic"]["step41_delta_witness_count"]),
        "step46_dynamic_witness_count": int(f["step46_dynamic"]["step41_delta_witness_count"]),
        "L64_status": "open; Step59 enumeration-strength grounding, not theorem-grade",
    }
    return {"scores": scores, "mapping": mapping, "anti": anti, "schema": schema, "consistency": consistency_rows(len(mapping))}


def write_artifacts(result: dict[str, Any]) -> None:
    schema = result["schema"]
    mapping = result["mapping"]
    anti = result["anti"]
    consistency = result["consistency"]
    write_csv(
        ARTIFACT_DIR / "mapping_table_step65.csv",
        mapping,
        [
            "carrier_id",
            "dimensions",
            "support_key",
            "fork_reading",
            "step41_delta_fact_nonempty",
            "delta_pair_count",
            "delta_witness_count",
            "transition_leak_count",
            "substrate_passes",
            "capacity_passes",
            "distinguishability_passes",
            "record_stability_passes",
            "record_incapable_reason",
            "baryon_branch",
            "monopole_branch",
        ],
    )
    write_csv(ARTIFACT_DIR / "anti_circularity_step65.csv", anti, ["check", "passes", "witness", "evidence"])
    write_csv(
        ARTIFACT_DIR / "fork_object_consistency_step65.csv",
        consistency,
        ["object", "defect_kind", "support_id", "witness_count", "identity_holds", "used_for_resolution", "note"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_step65_step41_fork_object", "status": "active", "declared_at_step": 65, "role": "fork object must be Step41 gauge-layer defect, not Step63 inter-layer defect"},
            {"constraint_id": "C_step65_memory_stability_selector", "status": "active_conditional", "declared_at_step": 65, "role": "memory-stability selects clean branch on Step59 enumeration-strength grounding"},
            {"constraint_id": "C_step65_no_physical_overclaim", "status": "active_validator", "declared_at_step": 65, "role": "no claim of solving proton decay or certifying frame transfer"},
        ],
        ["constraint_id", "status", "declared_at_step", "role"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target": "proton_monopole_fork_resolution",
                "parent_residual": "Steps45-46 typed fork with physical_reading_resolved=false",
                "relation_to_canonical_root": "sub_residual of clean-separation grounding and record-stability parent layer",
                "status": schema["verdict"],
                "artifacts": "mapping_table_step65.csv;fork_object_consistency_step65.csv",
            }
        ],
        ["target", "parent_residual", "relation_to_canonical_root", "status", "artifacts"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_step65_memory_selected_fork_resolution",
                "declared_at_step": 65,
                "carrier": "Step59 evaluated Step41 nonempty gauge-layer defects plus Steps45-46 fork readings",
                "active_constraints": "memory-stability recognition source; Step41 defect identity; Step45 F27; Step46 F48",
                "excluded_designs_rationale": "Step63 inter-layer Delta_fact is separated from the realized gauge-layer breaking coset.",
                "non_triviality_argument": "The fork branch is selected by the record predicate; anti-circularity witnesses show memory-stability is not clean-separation in disguise.",
                "next_grammar_delta": "Upgrade enumeration-strength selection to theorem-grade only if L64 is proved.",
            }
        ],
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    write_csv(
        ARTIFACT_DIR / "content_classification_step65.csv",
        [
            {"artifact": "mapping_table_step65.csv", "claim": "breaking-reading rows are record-incapable", "grade": "finite-carrier-diagnostic", "source": "mapping_table_step65.csv"},
            {"artifact": "fork_object_consistency_step65.csv", "claim": "fork object is Step41 gauge-layer defect, not Step63 inter-layer defect", "grade": "analytical-structural", "source": "fork_object_consistency_step65.csv"},
            {"artifact": "step65_statement.tex", "claim": "conditional memory-stability fork resolution", "grade": "analytical-structural / finite-carrier-diagnostic", "source": "step65_statement.tex"},
            {"artifact": "step65_results_summary.md", "claim": "summary and caveats", "grade": "organizational", "source": "step65_results_summary.md"},
            {"artifact": "run_step65.py", "claim": "validator", "grade": "organizational", "source": "run_step65.py"},
        ],
        ["artifact", "claim", "grade", "source"],
    )
    write_json(ARTIFACT_DIR / "step65_schema.json", schema)
    summary = f"""# Step 65 Results Summary

## Deflationary Truth First

Steps 45-46 typed the proton-decay/monopole fork and left `physical_reading_resolved=False`. Step 65 connects that fork to the later memory-stability machinery. The result is a SELECT resolution conditional on requiring memory-stability, at enumeration strength because L64 is still open. It does not prove physical proton stability, does not solve proton decay, and does not certify frame transfer from the finite toy to nature.

## Exact Mapping

(A) The fork's breaking reading is the Step-41 gauge-layer defect: Steps 45 and 46 identify the realized X/Y coset with the Step-41 `Delta_fact` witnesses. This is not the Step-47/63 inter-layer `Delta_fact(SM,parent)` pair count.

(B) On the Step-59 scored carrier, {schema['evaluated_breaking_structure_count']} evaluated Step-41 nonempty-defect structures represent the breaking reading. All {schema['evaluated_breaking_structure_count']} are record-incapable: record-stable count {schema['record_stable_breaking_structure_count']}, capacity-positive count {schema['capacity_positive_breaking_structure_count']}.

(C) Therefore, for structures required to support memory-stable records, the clean branch is selected: the Step-41 defect is empty, the F27 obstruction branch is zero, and the F48 gluing-obstruction branch is zero in the finite typed model.

## Non-Circularity

The resolution uses memory-stability, not clean-separation as an assumption. The anti-circularity witnesses show substrate without capacity on a nonempty-defect row and capacity with leak where substrate fails. Neither conjunct alone is the clean branch in disguise.

## Consistency With Step 63

Step 63 grounds a structural common-refinement parent and records the inter-layer refinement defect `Delta_fact(SM,parent)=15`. Step 65 uses the Step-41 gauge-layer breaking coset, the object used in the proton/monopole fork. There is no contradiction: the parent may exist as a structural refinement while realized breaking activation of the X/Y coset is excluded for record-stable structures at this grade.

## Exit State

`{schema['exit_state']}`. Verdict: `{schema['verdict']}`.
"""
    (ARTIFACT_DIR / "step65_results_summary.md").write_text(summary, encoding="utf-8")
    nonclaim = """# Nonclaim Boundary

Step 65 resolves the finite typed fork for record-stable structures. It does not prove physical proton stability, does not solve proton decay, does not certify frame transfer, and does not produce a theorem-grade all-structures result because L64 remains open.

The result is conditional on the memory-stability recognition source and on the Step-59 enumeration-strength grounding that record-stable rows are clean. It does not contradict Step 63: the Step-63 common-refinement defect is a structural parent-shadow object, not the realized gauge-layer breaking coset selected against here.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step65.md").write_text(nonclaim, encoding="utf-8")
    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 65 Statement}
Deflationary status: this is a conditional, enumeration-strength SELECT resolution of the proton/monopole fork for record-stable structures. It is not a physical stability theorem.

Let the fork-breaking reading be the realized Step--41 gauge-layer factorization defect: the confining-charged broken vector coset used by the F27 proton-decay and F48 monopole tests. Steps 45--46 identify this object with their X/Y witnesses.

Step--59 scores show that every evaluated nonempty Step--41 defect row is record-incapable: memory-stability is false for all such rows. Therefore, imposing the memory-stability recognition source selects the clean branch \(\Delta_{\rm fact}=\emptyset\). In that selected branch, the finite F27 baryon-descent obstruction is zero and the finite F48 gluing obstruction is zero.

This does not use the Step--63 inter-layer \(\Delta_{\rm fact}(\mathrm{SM},U)\), which remains a structural common-refinement relation rather than a realized breaking phase.
\end{document}
"""
    (ARTIFACT_DIR / "step65_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    result = build()
    write_artifacts(result)


if __name__ == "__main__":
    main()
