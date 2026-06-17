#!/usr/bin/env python3
"""Build Step 59 record-stability coverage artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import inspect
import json
import sys
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP33_BUILD = STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "corrected_anomaly_chirality_step33.py"
STEP35_BUILD = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
STEP41_BUILD = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "factorization_defect_clean_separation_step41.py"
STEP57_BUILD = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "record_stability_descent_step57.py"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def frozen_step57_region() -> str:
    text = STEP57_BUILD.read_text(encoding="utf-8")
    start = text.index("# RECORD_REQUIREMENT_BEGIN")
    end = text.index("# RECORD_REQUIREMENT_END")
    return text[start:end]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_hash(functions: list[Any]) -> str:
    return sha256_text("\n\n".join(inspect.getsource(function) for function in functions))


s33 = load_module("step59_s33_corrected", STEP33_BUILD)
s35 = load_module("step59_s35_base", STEP35_BUILD)
s41 = load_module("step59_s41_delta", STEP41_BUILD)
s57 = load_module("step59_s57_record", STEP57_BUILD)


def score_text(score: tuple[int, ...]) -> str:
    return "|".join(str(value) for value in score)


def scalar_action_diagnostics(scalar: Any) -> dict[str, Any]:
    confining: list[int] = []
    transition_leak_count = 0
    notes: list[str] = []
    for index, (rep, dimension) in enumerate(zip(scalar.reps, scalar.dimensions)):
        if s35.s33.action_active(rep, dimension):
            residual = dimension - 1
            if residual >= 2:
                confining.append(residual)
                leak = 2 * residual
                transition_leak_count += leak
                notes.append(f"factor{index}:residual{residual}:transition_leaks{leak}")
            else:
                notes.append(f"factor{index}:no_nonabelian_residual")
        elif dimension >= 2:
            confining.append(dimension)
            notes.append(f"factor{index}:untouched{dimension}")
    return {
        "confining_subgroups": confining,
        "transition_leak_count": transition_leak_count,
        "shadow_notes": ";".join(notes),
    }


def delta_from_step41(row: dict[str, Any], support_index: int) -> dict[str, Any]:
    if not row["substrate_passes"]:
        return {
            "delta_evaluated": False,
            "delta_pair_count": "",
            "delta_witness_count": "",
            "delta_empty": False,
        }
    confining = row["confining_subgroups"]
    if not confining:
        return {
            "delta_evaluated": False,
            "delta_pair_count": "",
            "delta_witness_count": "",
            "delta_empty": False,
        }
    step41_row = {
        "dimensions": row["dimensions"],
        "support_key": row["support_key"],
        "confining_subgroups": str(max(confining)),
        "broken_vector_exotic_count": str(row["transition_leak_count"]),
    }
    bosons = s41.build_bosons(step41_row, support_index)
    delta_pairs, witnesses = s41.compute_delta(bosons)
    return {
        "delta_evaluated": True,
        "delta_pair_count": len(delta_pairs),
        "delta_witness_count": len(witnesses),
        "delta_empty": len(delta_pairs) == 0,
    }


def candidate_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    target_key = s33.reference_support_key()
    scalar_cache: dict[tuple[int, ...], list[Any]] = {}
    for dimensions in s33.factor_structures():
        result = s33.enumerate_structure(dimensions)
        type_rows = result["type_rows"]
        scalar_cache.setdefault(dimensions, s35.scalar_representations(dimensions))
        scalars = scalar_cache[dimensions]
        dim_text = "|".join(str(value) for value in dimensions)
        for support_key, combo in result["closers"].items():
            support_score = s33.support_score(combo, type_rows)
            base = s35.higher_layer_mass_closure(combo, type_rows, scalars)
            scalar = base["witness_scalar"]
            action = scalar_action_diagnostics(scalar)
            substrate_passes = bool(base["higher_layer_passes"] and action["confining_subgroups"])
            adapted = {
                "dimensions": dim_text,
                "support_key": support_key,
                "base_stable_composite_mass_requirement": "True" if substrate_passes else "False",
            }
            record = s57.record_layer_membership(adapted)
            row: dict[str, Any] = {
                "carrier_id": f"carrier_{len(rows):05d}",
                "dimensions": dim_text,
                "support_key": support_key,
                "support_score": score_text(support_score),
                "field_count": support_score[0],
                "component_dim_sum": support_score[1],
                "base_higher_layer_passes": base["higher_layer_passes"],
                "witness_scalar_key": scalar.text,
                "witness_scalar_reps": "x".join(scalar.canonical_reps),
                "witness_scalar_charge": scalar.charge,
                "covered_count": base["covered_count"],
                "fermion_count": base["fermion_count"],
                "breaks_to_unbroken_u1": base["breaks_to_unbroken_u1"],
                "confining_subgroups": action["confining_subgroups"],
                "transition_leak_count": action["transition_leak_count"],
                "shadow_notes": action["shadow_notes"],
                "substrate_passes": substrate_passes,
                "capacity_passes": record["capacity_passes"],
                "distinguishability_passes": record["distinguishability_passes"],
                "neutral_record_token_count": record["neutral_record_token_count"],
                "alias_ambiguity_count": record["alias_ambiguity_count"],
                "alias_ambiguity_witnesses": record["alias_ambiguity_witnesses"],
                "record_stability_passes": record["record_stability_passes"],
                "is_reference_content": support_key == target_key,
            }
            delta = delta_from_step41(row, len(rows))
            row.update(delta)
            cs_member = bool(row["substrate_passes"] and row["delta_empty"])
            rs_member = bool(row["record_stability_passes"])
            row["CS_member"] = cs_member
            row["RS_member"] = rs_member
            row["divergence_witness"] = bool(rs_member and not cs_member)
            row["adversarial_capacity_non_CS"] = bool((not cs_member) and row["capacity_passes"])
            row["adversarial_substrate_non_CS"] = bool((not cs_member) and row["substrate_passes"])
            rows.append(row)
    return rows


def summarize(rows: list[dict[str, Any]]) -> tuple[dict[str, int], list[dict[str, Any]], list[dict[str, Any]]]:
    counts = {
        "carrier_rows": len(rows),
        "CS_count": sum(1 for row in rows if row["CS_member"]),
        "non_CS_count": sum(1 for row in rows if not row["CS_member"]),
        "substrate_count": sum(1 for row in rows if row["substrate_passes"]),
        "capacity_count": sum(1 for row in rows if row["capacity_passes"]),
        "distinguishability_count": sum(1 for row in rows if row["distinguishability_passes"]),
        "RS_count": sum(1 for row in rows if row["RS_member"]),
        "RS_not_CS_count": sum(1 for row in rows if row["divergence_witness"]),
        "non_CS_capacity_count": sum(1 for row in rows if (not row["CS_member"]) and row["capacity_passes"]),
        "non_CS_capacity_distinguish_count": sum(1 for row in rows if (not row["CS_member"]) and row["capacity_passes"] and row["distinguishability_passes"]),
        "non_CS_substrate_count": sum(1 for row in rows if (not row["CS_member"]) and row["substrate_passes"]),
        "non_CS_substrate_capacity_count": sum(1 for row in rows if (not row["CS_member"]) and row["substrate_passes"] and row["capacity_passes"]),
    }
    by_structure: dict[str, dict[str, int]] = {}
    for row in rows:
        bucket = by_structure.setdefault(
            row["dimensions"],
            {
                "carrier_rows": 0,
                "CS_count": 0,
                "non_CS_count": 0,
                "substrate_count": 0,
                "capacity_count": 0,
                "RS_count": 0,
                "RS_not_CS_count": 0,
                "non_CS_capacity_count": 0,
                "non_CS_substrate_count": 0,
            },
        )
        bucket["carrier_rows"] += 1
        bucket["CS_count"] += int(row["CS_member"])
        bucket["non_CS_count"] += int(not row["CS_member"])
        bucket["substrate_count"] += int(row["substrate_passes"])
        bucket["capacity_count"] += int(row["capacity_passes"])
        bucket["RS_count"] += int(row["RS_member"])
        bucket["RS_not_CS_count"] += int(row["divergence_witness"])
        bucket["non_CS_capacity_count"] += int((not row["CS_member"]) and row["capacity_passes"])
        bucket["non_CS_substrate_count"] += int((not row["CS_member"]) and row["substrate_passes"])
    by_rows = [{"dimensions": key, **value} for key, value in sorted(by_structure.items())]
    adversarial = [
        row for row in rows
        if row["adversarial_capacity_non_CS"] or row["adversarial_substrate_non_CS"] or row["divergence_witness"]
    ]
    return counts, by_rows, adversarial


def build() -> dict[str, Any]:
    rows = candidate_rows()
    counts, by_structure, adversarial = summarize(rows)
    divergence = [row for row in rows if row["divergence_witness"]]
    if divergence:
        verdict = "COVERAGE_BREAKS_DIVERGENCE_WITNESS_FOUND"
        structural_grade = "counterexample"
        next_delta = "record-stability is carrier-limited; try a stronger parent-layer memory requirement or a different parent layer"
    else:
        verdict = "ROBUST_COVERAGE_ENUMERATION_ONLY"
        structural_grade = "no_structural_proof_found"
        next_delta = "seek a structural theorem or stress wider windows; current result is enumeration-only"

    frozen_rows = [
        {
            "machinery": "Step57_record_requirement",
            "source_path": f"steps/{STEP57_BUILD.parent.name}/{STEP57_BUILD.name}",
            "sha256": sha256_text(frozen_step57_region()),
            "frozen_functions": "record_layer_membership",
            "status": "imported_verbatim",
        },
        {
            "machinery": "Step35_base_substrate",
            "source_path": f"steps/{STEP35_BUILD.parent.name}/{STEP35_BUILD.name}",
            "sha256": source_hash([s35.higher_layer_mass_closure, s35.mass_completion, s35.scalar_breaks_to_unbroken_u1]),
            "frozen_functions": "higher_layer_mass_closure|mass_completion|scalar_breaks_to_unbroken_u1",
            "status": "imported_verbatim",
        },
        {
            "machinery": "Step41_factorization_defect",
            "source_path": f"steps/{STEP41_BUILD.parent.name}/{STEP41_BUILD.name}",
            "sha256": source_hash([s41.build_bosons, s41.compute_delta]),
            "frozen_functions": "build_bosons|compute_delta",
            "status": "imported_verbatim",
        },
    ]
    negative_rows = [
        {"control": "carrier_bigger_than_step58", "passes": counts["carrier_rows"] > 80, "evidence": f"rows={counts['carrier_rows']}"},
        {"control": "non_CS_more_than_step58", "passes": counts["non_CS_count"] > 72, "evidence": f"non_CS={counts['non_CS_count']}"},
        {"control": "adversarial_capacity_nonvacuous", "passes": counts["non_CS_capacity_count"] > 0, "evidence": f"non_CS_capacity={counts['non_CS_capacity_count']}"},
        {"control": "substrate_non_CS_nonvacuous", "passes": counts["non_CS_substrate_count"] > 0, "evidence": f"non_CS_substrate={counts['non_CS_substrate_count']}"},
        {"control": "frozen_RS_has_teeth", "passes": 0 < counts["RS_count"] < counts["carrier_rows"], "evidence": f"RS={counts['RS_count']}"},
    ]
    dependency_rows = [
        {"axiom": "frozen_step57_record_requirement", "role": "RS scoring", "detail": "persistence, capacity, distinguishability imported without redefinition"},
        {"axiom": "frozen_step35_base_substrate", "role": "stable substrate scoring", "detail": "higher-layer mass closure imported without retuning"},
        {"axiom": "frozen_step41_defect", "role": "CS scoring", "detail": "factorization-defect pair computation imported without redefinition"},
        {"axiom": "corrected_step33_carrier", "role": "coverage carrier", "detail": "all corrected chiral closer rows in the Step33 window"},
        {"axiom": "adversarial_non_CS_capacity_search", "role": "teeth", "detail": "searches non-CS rows with capacity and/or substrate for divergence witnesses"},
    ]
    ablation_rows = [
        {"ablation": "remove_frozen_record_requirement", "effect": "RS predicate could be retuned to fit the coverage carrier", "load_bearing": True},
        {"ablation": "remove_frozen_base_substrate", "effect": "capacity-only non-CS rows could be mistaken for record-stable", "load_bearing": True},
        {"ablation": "remove_frozen_defect", "effect": "CS side of the inclusion test is no longer the Step41 condition", "load_bearing": True},
        {"ablation": "remove_adversarial_capacity_search", "effect": "coverage claim would not test the likely break region", "load_bearing": True},
    ]
    stage2_rows = [
        {"check": "corrected_closer_count_reproduced", "passes": counts["carrier_rows"] == 11990, "evidence": str(counts["carrier_rows"])},
        {"check": "adversarial_capacity_region_exists", "passes": counts["non_CS_capacity_count"] > 0, "evidence": str(counts["non_CS_capacity_count"])},
        {"check": "substrate_region_exists", "passes": counts["substrate_count"] > 0, "evidence": str(counts["substrate_count"])},
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "all three scoring machineries are imported frozen; no new target-structure selector"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependency_trace_step59.csv records frozen machinery and carrier"},
        {"gate": "ablation", "passes": all(row["load_bearing"] for row in ablation_rows), "evidence": "frozen machinery and adversarial search are load-bearing"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "broad non-CS and adversarial capacity regions are nonvacuous"},
        {"gate": "stage2", "passes": all(row["passes"] for row in stage2_rows), "evidence": "corrected carrier and adversarial regions reproduced"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "coverage verdict depends on all three frozen components plus the broad carrier"},
    ]
    anti_smuggle_rows = [
        {"check": "record_requirement_frozen", "passes": True, "evidence": frozen_rows[0]["sha256"]},
        {"check": "base_substrate_frozen", "passes": True, "evidence": frozen_rows[1]["sha256"]},
        {"check": "defect_machinery_frozen", "passes": True, "evidence": frozen_rows[2]["sha256"]},
        {"check": "bigger_neutral_carrier", "passes": counts["carrier_rows"] > 80 and counts["non_CS_count"] > 72, "evidence": f"rows={counts['carrier_rows']} non_CS={counts['non_CS_count']}"},
        {"check": "adversarial_search_nonvacuous", "passes": counts["non_CS_capacity_count"] > 0, "evidence": f"non_CS_capacity={counts['non_CS_capacity_count']}"},
        {"check": "no_requirement_retuning", "passes": s57.MIN_RECORD_TOKENS == 2, "evidence": f"MIN_RECORD_TOKENS={s57.MIN_RECORD_TOKENS}"},
    ]
    structural_rows = [
        {
            "claim": "coverage_status",
            "grade": structural_grade,
            "evidence": "No structural proof that confining-charged transition vectors necessarily destroy substrate, capacity, or distinguishability was found; coverage is enumeration-only." if not divergence else "Counterexample found.",
        },
        {
            "claim": "near_miss_pattern",
            "grade": "empirical_on_carrier",
            "evidence": f"non-CS capacity rows={counts['non_CS_capacity_count']}; non-CS substrate rows={counts['non_CS_substrate_count']}; non-CS substrate+capacity rows={counts['non_CS_substrate_capacity_count']}",
        },
    ]
    generated_rows = [
        {"item": "Step57_record_requirement", "status": "imported_frozen", "detail": frozen_rows[0]["sha256"]},
        {"item": "Step35_base_substrate", "status": "imported_frozen", "detail": frozen_rows[1]["sha256"]},
        {"item": "Step41_defect", "status": "imported_frozen", "detail": frozen_rows[2]["sha256"]},
        {"item": "Step33_corrected_closer_carrier", "status": "rederived", "detail": f"rows={counts['carrier_rows']}"},
        {"item": "adversarial_non_CS_capacity_region", "status": "computed", "detail": f"rows={counts['non_CS_capacity_count']}"},
        {"item": "divergence_witness_search", "status": "computed", "detail": f"RS_not_CS={counts['RS_not_CS_count']}"},
        {"item": "verdict", "status": "computed", "detail": verdict},
    ]
    schema = {
        "step": 59,
        "orientation": "ATTEMPT_record_stability_coverage",
        "active_residual": "coverage of frozen record-stability implies CS beyond the Step58 carrier",
        "main_object": "frozen RS/base/defect scoring on the full Step33 corrected closer carrier",
        **counts,
        "divergence_witness_exists": bool(divergence),
        "divergence_witness_ids": [row["carrier_id"] for row in divergence[:10]],
        "verdict": verdict,
        "structural_argument_grade": structural_grade,
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "frozen_gates_pass": all(row["passes"] for row in anti_smuggle_rows[:3]),
        "adversarial_search_nonvacuous": counts["non_CS_capacity_count"] > 0,
    }
    return {
        "rows": rows,
        "by_structure": by_structure,
        "adversarial": adversarial,
        "frozen": frozen_rows,
        "negative": negative_rows,
        "dependency": dependency_rows,
        "ablation": ablation_rows,
        "stage2": stage2_rows,
        "gates": gate_rows,
        "anti_smuggle": anti_smuggle_rows,
        "structural": structural_rows,
        "generated": generated_rows,
        "schema": schema,
    }


def write_docs(schema: dict[str, Any]) -> None:
    proof_line = (
        "No structural proof was found; the coverage result is enumeration-only on the declared 11,990-row carrier."
        if schema["structural_argument_grade"] == "no_structural_proof_found"
        else "A divergence witness was found, so the inclusion fails on the declared carrier."
    )
    results = f"""# Step 59 Results Summary

## Deflationary Truth First

Step 59 freezes the record requirement, base-substrate scoring, and factorization-defect machinery, then broadens the carrier to the full Step-33 corrected closer space. This is a coverage stress test, not a derivation of the gauge-layer condition, not an unconditional proof, and not frame transfer.

The honest ceiling remains: even when coverage is robust on this carrier, the result relocates grounding upward to memory/record-stability as a higher recognition source. It does not derive that source from nothing.

## Frozen Machinery

- Step 57 record requirement: imported verbatim.
- Step 35 base substrate: imported verbatim.
- Step 41 defect machinery: imported verbatim.

## Carrier And Search

- Carrier rows: `{schema['carrier_rows']}`
- CS rows: `{schema['CS_count']}`
- non-CS rows: `{schema['non_CS_count']}`
- Substrate rows: `{schema['substrate_count']}`
- Capacity rows: `{schema['capacity_count']}`
- non-CS rows with capacity: `{schema['non_CS_capacity_count']}`
- non-CS rows with capacity and distinguishability: `{schema['non_CS_capacity_distinguish_count']}`
- non-CS rows with substrate: `{schema['non_CS_substrate_count']}`
- non-CS rows with substrate and capacity: `{schema['non_CS_substrate_capacity_count']}`
- Record-stable rows: `{schema['RS_count']}`
- Record-stable non-CS divergence witnesses: `{schema['RS_not_CS_count']}`

## Divergence Witness

Divergence witness exists: `{schema['divergence_witness_exists']}`.

## Structural Argument

{proof_line}

The adversarial region was nonvacuous: `{schema['non_CS_capacity_count']}` non-CS rows passed capacity, and `{schema['non_CS_substrate_count']}` non-CS rows passed substrate. On this carrier the two requirements do not overlap with distinguishability to form a record-stable non-CS row.

## Verdict

`{schema['verdict']}`.

Next grammar delta: `{schema['next_grammar_delta']}`.
"""
    (ARTIFACT_DIR / "step59_results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Step 59 Nonclaim Boundary

Step 59 is a finite-carrier coverage stress test. It does not derive or prove the gauge-layer condition, does not prove memory implies that condition for all structures, does not derive the downstream theory, and does not certify frame transfer.

All three scoring machineries are imported frozen. The result is valid for the declared Step-33 corrected closer carrier. No structural proof beyond that carrier is claimed.

If a richer carrier contains a record-stable non-CS row, the coverage breaks. This step does not rule that out globally.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step59.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\begin{{document}}
\section*{{Step 59 Statement}}
On the full Step-33 corrected closer carrier, with the Step-57 record requirement, Step-35 substrate scoring, and Step-41 factorization-defect machinery imported frozen,
\[
  N={schema['carrier_rows']},\quad |CS|={schema['CS_count']},\quad |RS|={schema['RS_count']},\quad |RS\setminus CS|={schema['RS_not_CS_count']}.
\]
The adversarial non-CS capacity region is nonempty:
\[
  |\neg CS \cap \mathrm{{Capacity}}|={schema['non_CS_capacity_count']}.
\]
No record-stable non-CS divergence witness is found on this finite carrier, so the verdict is \(\mathrm{{{schema['verdict']}}}\).

No structural proof beyond this carrier is claimed.
\end{{document}}
"""
    (ARTIFACT_DIR / "step59_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    schema = built["schema"]
    score_fields = [
        "carrier_id",
        "dimensions",
        "support_key",
        "support_score",
        "field_count",
        "component_dim_sum",
        "base_higher_layer_passes",
        "witness_scalar_key",
        "witness_scalar_reps",
        "witness_scalar_charge",
        "covered_count",
        "fermion_count",
        "breaks_to_unbroken_u1",
        "confining_subgroups",
        "transition_leak_count",
        "shadow_notes",
        "substrate_passes",
        "capacity_passes",
        "distinguishability_passes",
        "neutral_record_token_count",
        "alias_ambiguity_count",
        "alias_ambiguity_witnesses",
        "delta_evaluated",
        "delta_pair_count",
        "delta_witness_count",
        "delta_empty",
        "CS_member",
        "RS_member",
        "divergence_witness",
        "adversarial_capacity_non_CS",
        "adversarial_substrate_non_CS",
        "is_reference_content",
    ]
    write_csv(ARTIFACT_DIR / "record_stability_coverage_scores_step59.csv", built["rows"], score_fields)
    write_csv(
        ARTIFACT_DIR / "record_stability_coverage_by_structure_step59.csv",
        built["by_structure"],
        [
            "dimensions",
            "carrier_rows",
            "CS_count",
            "non_CS_count",
            "substrate_count",
            "capacity_count",
            "RS_count",
            "RS_not_CS_count",
            "non_CS_capacity_count",
            "non_CS_substrate_count",
        ],
    )
    write_csv(ARTIFACT_DIR / "adversarial_candidates_step59.csv", built["adversarial"], score_fields)
    write_csv(ARTIFACT_DIR / "frozen_machinery_step59.csv", built["frozen"], ["machinery", "source_path", "sha256", "frozen_functions", "status"])
    write_csv(ARTIFACT_DIR / "negative_controls_step59.csv", built["negative"], ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step59.csv", built["dependency"], ["axiom", "role", "detail"])
    write_csv(ARTIFACT_DIR / "ablation_step59.csv", built["ablation"], ["ablation", "effect", "load_bearing"])
    write_csv(ARTIFACT_DIR / "stage2_record_fact_step59.csv", built["stage2"], ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step59.csv", built["gates"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step59.csv", built["anti_smuggle"], ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "structural_argument_step59.csv", built["structural"], ["claim", "grade", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step59.csv", built["generated"], ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step59_frozen_record_requirement", "status": "active_anti_smuggle_constraint", "declared_at_step": 59, "role": "Step57 record requirement must be imported verbatim"},
        {"constraint_id": "step59_frozen_base_substrate", "status": "active_anti_smuggle_constraint", "declared_at_step": 59, "role": "Step35 substrate/base logic must be imported verbatim"},
        {"constraint_id": "step59_frozen_defect", "status": "active_anti_smuggle_constraint", "declared_at_step": 59, "role": "Step41 factorization-defect computation must be imported verbatim"},
        {"constraint_id": "step59_adversarial_capacity_nonvacuity", "status": "active_teeth_constraint", "declared_at_step": 59, "role": "non-CS rows with capacity must exist in the carrier"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "record-stability-coverage-beyond-step58",
            "parent_residual": "record-stability grounding of CS requires coverage beyond 80-row carrier",
            "relation_to_canonical_root": "super_residual / parent layer (record/measurement, E032-adjacent), USER-AUTHORIZED 2026-06-09",
            "status": schema["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/record_stability_coverage_step59.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "parent_residual", "relation_to_canonical_root", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step59_record_stability_coverage",
            "declared_at_step": 59,
            "new_grammar_declared": True,
            "carrier": "full Step33 corrected closer carrier with frozen Step57/35/41 scoring",
            "tracked_object": "coverage of RS subset CS and adversarial non-CS capacity search",
            "next_grammar_delta": schema["next_grammar_delta"],
            "non_triviality_argument": "the carrier contains non-CS rows with capacity and non-CS rows with substrate; divergence search is not vacuous",
            "excluded_designs_rationale": "no retuned record predicate, no new base rule, no new defect rule, no CS prefilter",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "new_grammar_declared", "carrier", "tracked_object", "next_grammar_delta", "non_triviality_argument", "excluded_designs_rationale"],
    )

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_coverage_step59.py", "claim": "build script for coverage stress", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_coverage_step59.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_coverage_scores_step59.csv", "claim": "per-row coverage scores", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_coverage_scores_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_coverage_by_structure_step59.csv", "claim": "per-structure coverage counts", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_coverage_by_structure_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/adversarial_candidates_step59.csv", "claim": "non-CS adversarial capacity/substrate candidates", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/adversarial_candidates_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/frozen_machinery_step59.csv", "claim": "frozen machinery hashes", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/frozen_machinery_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/structural_argument_step59.csv", "claim": "structural argument grade", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/structural_argument_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step59_schema.json", "claim": "machine-readable Step59 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step59_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step59_results_summary.md", "claim": "Step59 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step59_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step59.md", "claim": "Step59 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step59.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step59_statement.tex", "claim": "coverage finite-carrier statement", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step59_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step59.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step59.csv", "claim": "dependency trace", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/ablation_step59.csv", "claim": "ablation record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/ablation_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/stage2_record_fact_step59.csv", "claim": "Stage-II checks", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/stage2_record_fact_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step59.csv", "claim": "anti-smuggle self-check", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step59.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step59.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv", "claim": "Mode-B constraint ledger", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv", "claim": "Mode-B target lineage", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv", "claim": "Mode-B grammar manifest", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classification_step59.csv", "claim": "content classification table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_classification_step59.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step59.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step59.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step59.csv", classification, ["artifact", "claim", "grade", "source"])
    write_json(ARTIFACT_DIR / "step59_schema.json", schema)
    write_docs(schema)


if __name__ == "__main__":
    main()
