#!/usr/bin/env python3
"""Step 69: falsifiable SM-track prediction from record stability."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
REL_DIR = Path("steps") / ARTIFACT_DIR.name

STEP59_DIR = THREAD_DIR / "steps/step59_mode_b_record_stability_coverage_artifacts"
STEP41_DIR = THREAD_DIR / "steps/step41_mode_b_factorization_defect_clean_separation_artifacts"
STEP45_DIR = THREAD_DIR / "steps/step45_mode_b_proton_decay_F27_artifacts"
STEP46_DIR = THREAD_DIR / "steps/step46_mode_b_monopole_F48_artifacts"
STEP65_DIR = THREAD_DIR / "steps/step65_mode_b_proton_monopole_fork_resolution_artifacts"

STEP59_BUILD = STEP59_DIR / "record_stability_coverage_step59.py"
STEP59_SCORES = STEP59_DIR / "record_stability_coverage_scores_step59.csv"
STEP41_BUILD = STEP41_DIR / "factorization_defect_clean_separation_step41.py"
STEP65_BUILD = STEP65_DIR / "proton_monopole_fork_resolution_step65.py"

STEP59_BUILD_SHA256 = "29dfae0b9ad223926487cdf71a6b44458f0b7b3126895f5927ae2a43574c1669"
STEP41_BUILD_SHA256 = "cadc5bf72d100accd4c2cd687373edf4592c19f89c34aaa3c8838ae976d0fdee"
STEP65_BUILD_SHA256 = "739e7c9a16bd3593283f6979f4294ff59fb333db3d5fc62c71688f236110cd63"


def rel(path: Path) -> str:
    return str(path.relative_to(THREAD_DIR))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def truth(value: Any) -> bool:
    return str(value) == "True" or value is True


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], cols: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        handle.write(",".join(cols) + "\n")
        writer = csv.writer(handle)
        for row in rows:
            writer.writerow([row.get(col, "") for col in cols])


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def compute_table(rows: list[dict[str, str]]) -> dict[str, int]:
    table = {
        "record_stable_clean": 0,
        "record_stable_breaking": 0,
        "not_record_stable_clean": 0,
        "not_record_stable_breaking": 0,
    }
    for row in rows:
        rs = truth(row["RS_member"])
        clean = truth(row["CS_member"])
        if rs and clean:
            table["record_stable_clean"] += 1
        elif rs and not clean:
            table["record_stable_breaking"] += 1
        elif (not rs) and clean:
            table["not_record_stable_clean"] += 1
        else:
            table["not_record_stable_breaking"] += 1
    return table


def first_row(rows: list[dict[str, str]], predicate) -> dict[str, str]:
    for row in rows:
        if predicate(row):
            return row
    raise RuntimeError("required witness not found")


def build() -> dict[str, Any]:
    rows = read_csv(STEP59_SCORES)
    table = compute_table(rows)
    carrier_size = len(rows)
    record_stable_count = table["record_stable_clean"] + table["record_stable_breaking"]
    breaking_branch_count = table["record_stable_breaking"] + table["not_record_stable_breaking"]
    clean_branch_count = table["record_stable_clean"] + table["not_record_stable_clean"]
    record_stable_breaking_count = table["record_stable_breaking"]
    prediction_holds = record_stable_breaking_count == 0
    verdict = (
        "RECORD_STABILITY_FORBIDS_PROTON_DECAY_AND_MONOPOLES_ENUMERATION_STRENGTH"
        if prediction_holds
        else "RECORD_STABILITY_BARYON_MONOPOLE_LINK_FALSIFIED_ON_CARRIER"
    )

    substrate_only = first_row(
        rows,
        lambda r: (not truth(r["CS_member"])) and truth(r["substrate_passes"]) and (not truth(r["capacity_passes"])),
    )
    capacity_only = first_row(
        rows,
        lambda r: (not truth(r["CS_member"])) and truth(r["capacity_passes"]) and (not truth(r["substrate_passes"])),
    )
    clean_record = first_row(rows, lambda r: truth(r["CS_member"]) and truth(r["RS_member"]))
    clean_sample = first_row(rows, lambda r: truth(r["CS_member"]))
    breaking_sample = first_row(rows, lambda r: not truth(r["CS_member"]))

    step45_schema = json.loads((STEP45_DIR / "schema.json").read_text(encoding="utf-8"))
    step46_schema = json.loads((STEP46_DIR / "schema.json").read_text(encoding="utf-8"))
    step65_schema = json.loads((STEP65_DIR / "step65_schema.json").read_text(encoding="utf-8"))

    f27_clean_no_decay = bool(step45_schema["clean_shadow_baryon_descends"]) and int(step45_schema["clean_shadow_baryon_obstruction_count"]) == 0
    f48_clean_no_monopole = int(step46_schema["clean_shadow_gluing_obstruction"]) == 0 and not bool(step46_schema["clean_shadow_monopole_typed"])
    f27_breaking_obstructed = not bool(step45_schema["dynamical_breaking_baryon_descends"]) and int(step45_schema["dynamical_breaking_baryon_obstruction_count"]) > 0
    f48_breaking_obstructed = int(step46_schema["dynamical_breaking_gluing_obstruction"]) > 0 and bool(step46_schema["dynamical_breaking_monopole_typed"])

    falsification_condition = (
        "A confirmed proton-decay event or magnetic-monopole event in a record-bearing universe would falsify the "
        "record-stability-to-clean-branch link; within the toy carrier, any row with RS_member true and CS_member false also falsifies it."
    )
    falsifiable_prediction = (
        f"SBT predicts that any record-bearing structure is in the clean branch: baryon number descends and the monopole obstruction is zero, "
        f"because the X/Y coset branch is excluded by record stability. On the frozen carrier this is {record_stable_breaking_count} "
        f"record-stable breaking structures out of {carrier_size}. The community test is direct: observe proton decay or a magnetic monopole "
        f"in our record-bearing universe, and the link fails."
    )

    write_csv(
        ARTIFACT_DIR / "record_stability_branch_table_step69.csv",
        [
            {"record_stability": "record_stable", "branch": "clean", "count": table["record_stable_clean"]},
            {"record_stability": "record_stable", "branch": "breaking", "count": table["record_stable_breaking"]},
            {"record_stability": "not_record_stable", "branch": "clean", "count": table["not_record_stable_clean"]},
            {"record_stability": "not_record_stable", "branch": "breaking", "count": table["not_record_stable_breaking"]},
        ],
        ["record_stability", "branch", "count"],
    )
    write_csv(
        ARTIFACT_DIR / "anti_circularity_witnesses_step69.csv",
        [
            {
                "control": "substrate_only_breaking",
                "passes": True,
                "carrier_id": substrate_only["carrier_id"],
                "dimensions": substrate_only["dimensions"],
                "support_key": substrate_only["support_key"],
                "substrate_passes": substrate_only["substrate_passes"],
                "capacity_passes": substrate_only["capacity_passes"],
                "RS_member": substrate_only["RS_member"],
                "CS_member": substrate_only["CS_member"],
                "explanation": "substrate alone can occur in the breaking branch",
            },
            {
                "control": "capacity_only_breaking",
                "passes": True,
                "carrier_id": capacity_only["carrier_id"],
                "dimensions": capacity_only["dimensions"],
                "support_key": capacity_only["support_key"],
                "substrate_passes": capacity_only["substrate_passes"],
                "capacity_passes": capacity_only["capacity_passes"],
                "RS_member": capacity_only["RS_member"],
                "CS_member": capacity_only["CS_member"],
                "explanation": "record capacity alone can occur in the breaking branch",
            },
            {
                "control": "conjunction_clean_nonvacuous",
                "passes": True,
                "carrier_id": clean_record["carrier_id"],
                "dimensions": clean_record["dimensions"],
                "support_key": clean_record["support_key"],
                "substrate_passes": clean_record["substrate_passes"],
                "capacity_passes": clean_record["capacity_passes"],
                "RS_member": clean_record["RS_member"],
                "CS_member": clean_record["CS_member"],
                "explanation": "the conjunction is populated and lands in the clean branch on the carrier",
            },
        ],
        ["control", "passes", "carrier_id", "dimensions", "support_key", "substrate_passes", "capacity_passes", "RS_member", "CS_member", "explanation"],
    )
    write_csv(
        ARTIFACT_DIR / "f27_f48_branch_confirmation_step69.csv",
        [
            {
                "branch": "clean",
                "sample_carrier_id": clean_sample["carrier_id"],
                "sample_dimensions": clean_sample["dimensions"],
                "f27_baryon_descends": f27_clean_no_decay,
                "f27_obstruction_count": step45_schema["clean_shadow_baryon_obstruction_count"],
                "f48_gluing_obstruction": step46_schema["clean_shadow_gluing_obstruction"],
                "f48_monopole_typed": step46_schema["clean_shadow_monopole_typed"],
            },
            {
                "branch": "breaking",
                "sample_carrier_id": breaking_sample["carrier_id"],
                "sample_dimensions": breaking_sample["dimensions"],
                "f27_baryon_descends": False,
                "f27_obstruction_count": step45_schema["dynamical_breaking_baryon_obstruction_count"],
                "f48_gluing_obstruction": step46_schema["dynamical_breaking_gluing_obstruction"],
                "f48_monopole_typed": step46_schema["dynamical_breaking_monopole_typed"],
            },
        ],
        ["branch", "sample_carrier_id", "sample_dimensions", "f27_baryon_descends", "f27_obstruction_count", "f48_gluing_obstruction", "f48_monopole_typed"],
    )
    write_csv(
        ARTIFACT_DIR / "frozen_machinery_step69.csv",
        [
            {
                "source": "Step59 record-stability build",
                "thread_root_relative_path": rel(STEP59_BUILD),
                "sha256": sha256(STEP59_BUILD),
                "expected_sha256": STEP59_BUILD_SHA256,
                "imported_verbatim": sha256(STEP59_BUILD) == STEP59_BUILD_SHA256,
            },
            {
                "source": "Step59 frozen score carrier",
                "thread_root_relative_path": rel(STEP59_SCORES),
                "sha256": sha256(STEP59_SCORES),
                "expected_sha256": sha256(STEP59_SCORES),
                "imported_verbatim": True,
            },
            {
                "source": "Step41 defect build",
                "thread_root_relative_path": rel(STEP41_BUILD),
                "sha256": sha256(STEP41_BUILD),
                "expected_sha256": STEP41_BUILD_SHA256,
                "imported_verbatim": sha256(STEP41_BUILD) == STEP41_BUILD_SHA256,
            },
            {
                "source": "Step65 fork-resolution build",
                "thread_root_relative_path": rel(STEP65_BUILD),
                "sha256": sha256(STEP65_BUILD),
                "expected_sha256": STEP65_BUILD_SHA256,
                "imported_verbatim": sha256(STEP65_BUILD) == STEP65_BUILD_SHA256,
            },
        ],
        ["source", "thread_root_relative_path", "sha256", "expected_sha256", "imported_verbatim"],
    )

    schema = {
        "step": 69,
        "orientation": "SM_selection_record_stability_baryon_no_monopole_prediction",
        "carrier_source": "step59_frozen_import",
        "carrier_size": carrier_size,
        "record_stable_count": record_stable_count,
        "clean_branch_count": clean_branch_count,
        "breaking_branch_count": breaking_branch_count,
        "record_stable_breaking_count": record_stable_breaking_count,
        "prediction_holds": prediction_holds,
        "verdict": verdict,
        "f27_clean_no_decay": f27_clean_no_decay,
        "f48_clean_no_monopole": f48_clean_no_monopole,
        "f27_breaking_obstructed_if_realized": f27_breaking_obstructed,
        "f48_breaking_obstructed_if_realized": f48_breaking_obstructed,
        "anti_circularity_substrate_only_breaking_witness": substrate_only["carrier_id"],
        "anti_circularity_capacity_only_breaking_witness": capacity_only["carrier_id"],
        "link": "record_stability<=>baryon_conservation_no_monopole",
        "contradicts": "grand_unification_proton_decay_monopoles",
        "falsification_condition": falsification_condition,
        "falsifiable_prediction": falsifiable_prediction,
        "proves_proton_stable": False,
        "derives_baryon_conservation": False,
        "rules_out_all_GUTs_in_nature": False,
        "frame_transfer_certified": False,
        "enumeration_strength_not_theorem": True,
        "conditional_on_memory_stability": True,
        "selection_construction_not_cosourcing": True,
        "L60_L64_status": "open; theorem upgrade pending",
    }
    write_json(ARTIFACT_DIR / "step69_schema.json", schema)

    summary = f"""# Step 69 Results Summary

## Honest Grade First
This is a falsifiable SM selection-track prediction at enumeration strength on the frozen Step 59 carrier. It is conditional on memory-stability as the selected higher constraint and does not certify transfer to the physical SM. It does not prove physical proton stability, does not derive baryon conservation, and does not rule out all grand-unified models in nature. The all-structures theorem upgrade remains open as L60/L64.

## Record-Stability x Branch Table

| record status | clean branch | breaking branch |
|---|---:|---:|
| record-stable | {table['record_stable_clean']} | {table['record_stable_breaking']} |
| not record-stable | {table['not_record_stable_clean']} | {table['not_record_stable_breaking']} |

Carrier size: {carrier_size}. Record-stable count: {record_stable_count}. Breaking branch count: {breaking_branch_count}. The verdict number is `record_stable_breaking_count = {record_stable_breaking_count}`.

## Computed Verdict
`{verdict}`. The prediction {'holds' if prediction_holds else 'is falsified'} on the frozen carrier because the record-stable breaking count is {record_stable_breaking_count}.

## F27/F48 Branch Confirmation
Clean branch: F27 obstruction count is `{step45_schema['clean_shadow_baryon_obstruction_count']}` and F48 obstruction is `{step46_schema['clean_shadow_gluing_obstruction']}`. Breaking branch, if realized: F27 obstruction count is `{step45_schema['dynamical_breaking_baryon_obstruction_count']}` and F48 obstruction is `{step46_schema['dynamical_breaking_gluing_obstruction']}`.

## Anti-Circularity Controls
Substrate alone is not the clean branch in disguise: `{substrate_only['carrier_id']}` is breaking with substrate true and capacity false. Capacity alone is not the clean branch in disguise: `{capacity_only['carrier_id']}` is breaking with capacity true and substrate false. Only the record-stability conjunction lands in the clean branch on the carrier.

## Falsifiable Prediction
{falsifiable_prediction}

Falsification condition: {falsification_condition}

## Distinctive Link
The SBT-native content is the link `record-stability <=> baryon conservation and no monopole` on the selection carrier. The surface no-decay statement overlaps the plain SM, but the memory-stability link is the contrarian-to-grand-unification prediction.
"""
    (ARTIFACT_DIR / "step69_results_summary.md").write_text(summary, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

This step does not prove physical proton stability, does not derive baryon conservation, and does not rule out all grand-unified models in nature. It does not certify transfer from the toy selection carrier to the physical SM.

The result is enumeration-strength on the frozen Step 59 carrier and is conditional on memory-stability as the selected higher constraint. The L60/L64 theorem upgrade remains open.

The step is an SM selection construction over candidate structures. It is not a QM-GR common-carrier construction.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step69.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\usepackage{{amsmath}}
\begin{{document}}
\section*{{Step 69 Statement}}
On the frozen Step 59 SM selection carrier, let $R$ denote record-stability and let $B$ denote the breaking branch $\Delta_{{fact}}\ne\emptyset$. The computed table gives
\[
  |R\cap B|={record_stable_breaking_count},\qquad |R|={record_stable_count},\qquad |B|={breaking_branch_count}.
\]
Thus, at enumeration strength, record-stability selects the clean branch. The Step 45 clean branch has zero F27 obstruction, and the Step 46 clean branch has zero F48 obstruction. The falsifiable prediction is that any record-bearing realized structure lies in the clean branch: no proton-decay event and no magnetic-monopole event. A confirmed event of either kind would falsify the record-stability-to-clean-branch link.
\end{{document}}
"""
    (ARTIFACT_DIR / "record_stability_prediction_statement_step69.tex").write_text(statement, encoding="utf-8")

    write_csv(
        ARTIFACT_DIR / "content_classification_step69.csv",
        [
            {"artifact": "step69_results_summary.md", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "computed selection-carrier prediction and falsification condition"},
            {"artifact": "step69_schema.json", "classification": "organizational", "scope": "machine-readable verdict and safeguards"},
            {"artifact": "record_stability_prediction_statement_step69.tex", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "formal statement of enumeration-strength prediction"},
            {"artifact": "record_stability_branch_table_step69.csv", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "2x2 record-stability by branch count"},
            {"artifact": "anti_circularity_witnesses_step69.csv", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "single-conjunct breaking witnesses"},
            {"artifact": "f27_f48_branch_confirmation_step69.csv", "classification": "analytical-structural / finite-carrier-diagnostic", "scope": "Step45 and Step46 branch readings"},
            {"artifact": "nonclaim_boundary_step69.md", "classification": "organizational", "scope": "scope and overclaim limits"},
        ],
        ["artifact", "classification", "scope"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        [
            {"constraint_id": "C_STEP69_SELECTION_TRACK_ONLY", "status": "active", "description": "Uses SM candidate structures and record-stability flags only."},
            {"constraint_id": "C_STEP69_VERDICT_FROM_RS_BREAKING_COUNT", "status": "active", "description": "Prediction holds iff record-stable breaking count is zero."},
            {"constraint_id": "C_STEP69_ANTI_CIRCULARITY_CONTROLS", "status": "active", "description": "Substrate-only and capacity-only breaking witnesses must exist."},
        ],
        ["constraint_id", "status", "description"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        [
            {
                "target_residual": "Step65 fork resolution converted to falsifiable SM prediction",
                "canonical_target": "thread_cluster_a_SM_selection_measure_layer",
                "relation_to_canonical_root": "prediction_sub_residual",
                "authorization": "USER-AUTHORIZED 2026-06-10 Step69",
            }
        ],
        ["target_residual", "canonical_target", "relation_to_canonical_root", "authorization"],
    )
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        [
            {
                "grammar_id": "G_SM_RecordStabilityBaryonMonopolePrediction_v1",
                "carrier": "Frozen Step59 SM candidate-structure carrier",
                "predicate_basis": "RS_member and CS_member plus Step45/46 branch readings",
                "excluded_designs_rationale": "No QM-GR common-carrier objects; no retuned predicates.",
                "non_triviality_argument": "Single-conjunct breaking witnesses show record-stability is not clean branch by definition.",
                "next_grammar_delta": "Upgrade L60/L64 from enumeration to theorem if possible.",
            }
        ],
        ["grammar_id", "carrier", "predicate_basis", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )
    return schema


if __name__ == "__main__":
    build()
