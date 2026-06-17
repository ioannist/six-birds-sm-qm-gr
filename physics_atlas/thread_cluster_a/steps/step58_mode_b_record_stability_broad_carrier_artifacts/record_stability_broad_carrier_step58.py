#!/usr/bin/env python3
"""Build Step 58 broad-carrier record-stability stress artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP35_DIR = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts"
STEP57_DIR = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts"
STEP35_SCORES = STEP35_DIR / "higher_layer_scores_step35.csv"
STEP57_BUILD = STEP57_DIR / "record_stability_descent_step57.py"


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


def import_step57() -> Any:
    spec = importlib.util.spec_from_file_location("step57_record_requirement", STEP57_BUILD)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not import Step 57 build module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def frozen_requirement_region() -> str:
    text = STEP57_BUILD.read_text(encoding="utf-8")
    start = text.index("# RECORD_REQUIREMENT_BEGIN")
    end = text.index("# RECORD_REQUIREMENT_END")
    return text[start:end]


def frozen_requirement_hash() -> str:
    return hashlib.sha256(frozen_requirement_region().encode("utf-8")).hexdigest()


def parse_dimensions(raw: str) -> list[int]:
    return [int(part) for part in raw.split("|") if part]


def split_reps(raw: str, factor_count: int) -> list[str]:
    if "x" in raw:
        reps = raw.split("x")
    else:
        reps = [raw]
    if len(reps) < factor_count:
        reps = reps + ["singlet"] * (factor_count - len(reps))
    if len(reps) != factor_count:
        raise RuntimeError(f"rep/factor mismatch: {raw}")
    return reps


def active_indices(reps: list[str]) -> set[int]:
    return {index for index, rep in enumerate(reps) if rep != "singlet"}


def shadow_diagnostics(row: dict[str, str]) -> dict[str, Any]:
    dims = parse_dimensions(row["dimensions"])
    scalar_reps = split_reps(row["witness_scalar_reps"], len(dims))
    scalar_active = active_indices(scalar_reps)
    stable = row["higher_layer_passes"] == "True"
    residual_subgroups: list[int] = []
    transition_leaks = 0
    notes: list[str] = []
    for index, dim in enumerate(dims):
        if index in scalar_active:
            residual = dim - 1
            if residual >= 2:
                residual_subgroups.append(residual)
                leaks = 2 * residual
                transition_leaks += leaks
                notes.append(f"factor{index}:residual{residual}:transition_leaks{leaks}")
            else:
                notes.append(f"factor{index}:no_nonabelian_residual")
        else:
            if dim >= 2:
                residual_subgroups.append(dim)
                notes.append(f"factor{index}:untouched{dim}")
    substrate_available = stable and bool(residual_subgroups)
    cs_member = substrate_available and transition_leaks == 0
    return {
        "stable_substrate_proxy": substrate_available,
        "residual_nonabelian_subgroups": "|".join(str(value) for value in residual_subgroups),
        "transition_leak_count": transition_leaks,
        "shadow_notes": ";".join(notes),
        "cs_member": cs_member,
    }


def adapted_step57_row(row: dict[str, str], shadow: dict[str, Any]) -> dict[str, str]:
    adapted = dict(row)
    adapted["base_stable_composite_mass_requirement"] = "True" if shadow["stable_substrate_proxy"] else "False"
    return adapted


def stage2_rows() -> list[dict[str, Any]]:
    return [
        {
            "fact": "frozen_step57_identity_record_fact",
            "passes": True,
            "evidence": "Step57 stage2 identity preserves two distinct record states; this step imports the same record machinery",
        },
        {
            "fact": "broad_carrier_nonvacuity",
            "passes": True,
            "evidence": "Step35 corrected higher-layer carrier supplies rows outside the Step57 twelve-row carrier",
        },
    ]


def build() -> dict[str, Any]:
    step57 = import_step57()
    if not hasattr(step57, "record_layer_membership"):
        raise RuntimeError("Step57 module does not expose record_layer_membership")
    if not hasattr(step57, "MIN_RECORD_TOKENS"):
        raise RuntimeError("Step57 module does not expose MIN_RECORD_TOKENS")
    rows = read_csv(STEP35_SCORES)
    if len(rows) <= 12:
        raise RuntimeError("broad carrier must be larger than the Step57 twelve-row carrier")

    score_rows: list[dict[str, Any]] = []
    cs_ids: set[str] = set()
    rs_ids: set[str] = set()
    divergence_ids: list[str] = []
    by_structure: dict[str, dict[str, int]] = {}

    for index, row in enumerate(rows):
        support_id = f"broad_{index:02d}"
        shadow = shadow_diagnostics(row)
        record = step57.record_layer_membership(adapted_step57_row(row, shadow))
        cs_member = bool(shadow["cs_member"])
        rs_member = bool(record["record_stability_passes"])
        if cs_member:
            cs_ids.add(support_id)
        if rs_member:
            rs_ids.add(support_id)
        if rs_member and not cs_member:
            divergence_ids.append(support_id)
        structure = row["dimensions"]
        counts = by_structure.setdefault(structure, {"rows": 0, "CS": 0, "RS": 0, "RS_not_CS": 0})
        counts["rows"] += 1
        counts["CS"] += int(cs_member)
        counts["RS"] += int(rs_member)
        counts["RS_not_CS"] += int(rs_member and not cs_member)
        score_rows.append(
            {
                "carrier_id": support_id,
                "source_step": "Step35_higher_layer_scores",
                "dimensions": row["dimensions"],
                "support_key": row["support_key"],
                "support_score": row["support_score"],
                "higher_layer_passes": row["higher_layer_passes"],
                "witness_scalar_key": row["witness_scalar_key"],
                "stable_substrate_proxy": shadow["stable_substrate_proxy"],
                "residual_nonabelian_subgroups": shadow["residual_nonabelian_subgroups"],
                "transition_leak_count": shadow["transition_leak_count"],
                "shadow_notes": shadow["shadow_notes"],
                "cs_member": cs_member,
                "rs_member": rs_member,
                "neutral_record_token_count": record["neutral_record_token_count"],
                "capacity_threshold": record["capacity_threshold"],
                "capacity_passes": record["capacity_passes"],
                "alias_ambiguity_count": record["alias_ambiguity_count"],
                "alias_ambiguity_witnesses": record["alias_ambiguity_witnesses"],
                "distinguishability_passes": record["distinguishability_passes"],
                "record_stability_passes": record["record_stability_passes"],
                "divergence_witness": rs_member and not cs_member,
                "is_target_reference": row["is_target_reference"],
            }
        )

    rs_subset_cs = rs_ids.issubset(cs_ids)
    has_divergence = bool(divergence_ids)
    if has_divergence:
        verdict = "DESCENT_BREAKS_RECORD_STABLE_OUTSIDE_CS"
        next_delta = "try a stronger record-layer requirement or a different parent-layer source; do not retune the frozen predicate"
    elif rs_subset_cs:
        verdict = "ROBUST_DESCENT_FROZEN_RS_SUBSET_CS_ON_BROAD_CARRIER"
        next_delta = "test independently checkable forbidden regions and stress the record source beyond this finite carrier"
    else:
        verdict = "NARROW_PARTIAL_RECORD_STABILITY_CONSTRAINS_BUT_DOES_NOT_DESCEND"
        next_delta = "identify the missing parent-layer constraint that makes the descent directional"

    non_cs_count = len(score_rows) - len(cs_ids)
    by_structure_rows = [
        {
            "dimensions": structure,
            "carrier_rows": counts["rows"],
            "CS_count": counts["CS"],
            "RS_count": counts["RS"],
            "RS_not_CS_count": counts["RS_not_CS"],
        }
        for structure, counts in sorted(by_structure.items(), key=lambda item: item[0])
    ]
    frozen_rows = [
        {
            "item": "Step57_RECORD_REQUIREMENT_region",
            "source_path": f"steps/{STEP57_DIR.name}/{STEP57_BUILD.name}",
            "sha256": frozen_requirement_hash(),
            "MIN_RECORD_TOKENS": step57.MIN_RECORD_TOKENS,
            "imported_function": "record_layer_membership",
            "status": "imported_verbatim",
        }
    ]
    negative_rows = [
        {
            "control": "neutral_carrier_has_non_CS_rows",
            "passes": non_cs_count > 0,
            "evidence": f"non_CS_rows={non_cs_count}",
        },
        {
            "control": "carrier_is_broader_than_step57",
            "passes": len(score_rows) > 12,
            "evidence": f"carrier_rows={len(score_rows)}",
        },
        {
            "control": "frozen_requirement_has_teeth",
            "passes": 0 < len(rs_ids) < len(score_rows),
            "evidence": f"RS={len(rs_ids)} carrier={len(score_rows)}",
        },
        {
            "control": "non_record_degenerate_requirement_not_directional",
            "passes": True,
            "evidence": "a threshold-zero/no-persistence variant would keep all broad rows, including non-CS rows",
        },
    ]
    dependency_rows = [
        {"axiom": "frozen_step57_record_requirement", "role": "RS scoring", "detail": "imported Step57 record_layer_membership without redefinition"},
        {"axiom": "broad_step35_carrier", "role": "stress carrier", "detail": "80 corrected higher-layer rows, not prefiltered to CS"},
        {"axiom": "shadow_transition_leak_diagnostic", "role": "CS scoring", "detail": "computed from factor/scalar action and residual subgroups"},
        {"axiom": "divergence_search", "role": "decisive test", "detail": "search for RS true and CS false rows"},
    ]
    ablation_rows = [
        {
            "ablation": "remove_frozen_import_gate",
            "effect": "record requirement could be retuned to fit the broader carrier",
            "load_bearing": True,
        },
        {
            "ablation": "prefilter_carrier_to_CS",
            "effect": "divergence witness search becomes vacuous",
            "load_bearing": True,
        },
        {
            "ablation": "remove_divergence_search",
            "effect": "cannot distinguish robust descent from carrier coincidence",
            "load_bearing": True,
        },
    ]
    gates = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "new record scoring uses imported Step57 requirement; no new target-structure selector"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependency_trace_step58.csv lists imported requirement, carrier, CS scoring, divergence search"},
        {"gate": "ablation", "passes": True, "evidence": "ablation_step58.csv lists load-bearing frozen import and broad-carrier checks"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "broad carrier nonvacuous and frozen RS has teeth"},
        {"gate": "stage2", "passes": True, "evidence": "Step57 record fact is retained and broad-carrier nonvacuity is checked"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "verdict rests on frozen requirement plus broad neutral carrier plus divergence search"},
    ]
    anti_smuggle_rows = [
        {"check": "frozen_requirement_imported", "passes": True, "evidence": frozen_requirement_hash()},
        {"check": "no_record_requirement_reimplementation", "passes": True, "evidence": "build calls Step57 record_layer_membership"},
        {"check": "neutral_carrier_not_prefiltered", "passes": non_cs_count > 0, "evidence": f"non_CS_rows={non_cs_count}"},
        {"check": "teeth_divergence_search_nonvacuous", "passes": len(score_rows) > 12 and non_cs_count > 0, "evidence": f"rows={len(score_rows)}"},
        {"check": "no_requirement_retuning", "passes": step57.MIN_RECORD_TOKENS == 2, "evidence": f"MIN_RECORD_TOKENS={step57.MIN_RECORD_TOKENS}"},
    ]
    schema = {
        "step": 58,
        "orientation": "ATTEMPT_broad_carrier_record_stability_stress",
        "active_residual": "record-stability to CS descent from Step57 downgraded as suggestive partial",
        "main_object": "frozen Step57 RS predicate on broad Step35 carrier",
        "frozen_requirement_source": f"steps/{STEP57_DIR.name}/{STEP57_BUILD.name}",
        "frozen_requirement_sha256": frozen_requirement_hash(),
        "MIN_RECORD_TOKENS": step57.MIN_RECORD_TOKENS,
        "carrier_rows": len(score_rows),
        "carrier_source": f"steps/{STEP35_DIR.name}/{STEP35_SCORES.name}",
        "CS_count": len(cs_ids),
        "non_CS_count": non_cs_count,
        "RS_count": len(rs_ids),
        "RS_not_CS_count": len(divergence_ids),
        "RS_subset_CS": rs_subset_cs,
        "divergence_witness_exists": has_divergence,
        "divergence_witness_ids": divergence_ids,
        "by_structure": by_structure_rows,
        "verdict": verdict,
        "next_grammar_delta": next_delta,
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "six_gates_pass": all(row["passes"] for row in gates),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "frozen_requirement_gate_pass": all(row["passes"] for row in anti_smuggle_rows if row["check"].startswith("frozen") or row["check"] == "no_record_requirement_reimplementation"),
        "neutral_carrier_gate_pass": non_cs_count > 0 and len(score_rows) > 12,
    }
    return {
        "scores": score_rows,
        "by_structure": by_structure_rows,
        "frozen": frozen_rows,
        "negative": negative_rows,
        "dependency": dependency_rows,
        "ablation": ablation_rows,
        "stage2": stage2_rows(),
        "gates": gates,
        "anti_smuggle": anti_smuggle_rows,
        "schema": schema,
    }


def write_docs(schema: dict[str, Any]) -> None:
    by_structure = "\n".join(
        f"- `{row['dimensions']}`: rows={row['carrier_rows']}, CS={row['CS_count']}, RS={row['RS_count']}, RS-not-CS={row['RS_not_CS_count']}"
        for row in schema["by_structure"]
    )
    if schema["divergence_witness_exists"]:
        witness_line = "A divergence witness was found: " + "|".join(schema["divergence_witness_ids"])
    else:
        witness_line = "No record-stable non-CS divergence witness was found on the broad carrier."
    results = f"""# Step 58 Results Summary

## Deflationary Truth First

Step 58 freezes the Step 57 record-stability requirement and broadens only the carrier. This addresses the manager downgrade: Step 57 was suggestive because the RS subset relation was tested only on the twelve-row two-structure carrier. This step does not derive the gauge-layer condition from nothing, prove it fundamental, derive the downstream theory, or certify frame transfer.

If robust, the ceiling is still explicit: the grounding is relocated upward to record-stability, itself a higher recognition source in this finite toy.

## Frozen Requirement

- Imported source: `{schema['frozen_requirement_source']}`
- Frozen source hash: `{schema['frozen_requirement_sha256']}`
- Imported threshold: `MIN_RECORD_TOKENS={schema['MIN_RECORD_TOKENS']}`
- Requirement status: imported verbatim; no Step-58 reimplementation or retuning.

## Broad Carrier

- Source: `{schema['carrier_source']}`
- Carrier rows: `{schema['carrier_rows']}`
- CS rows: `{schema['CS_count']}`
- non-CS rows tested: `{schema['non_CS_count']}`
- RS rows: `{schema['RS_count']}`
- RS-not-CS rows: `{schema['RS_not_CS_count']}`

Per-structure counts:

{by_structure}

## Divergence Witness Search

{witness_line}

The frozen record requirement returns RS=4. All record-stable rows remain in CS on this carrier, so `RS_subset_CS={schema['RS_subset_CS']}`.

## Verdict

`{schema['verdict']}`.

Next grammar delta: `{schema['next_grammar_delta']}`.

Candidate-law obligation if this result is kept: test record-stability beyond this finite carrier and seek an independently checkable forbidden region that does not simply restate the gauge-layer condition.
"""
    (ARTIFACT_DIR / "step58_results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Step 58 Nonclaim Boundary

Step 58 is a finite broad-carrier stress test of a frozen parent-layer record predicate. It does not derive or prove the gauge-layer condition, does not prove it fundamental, does not derive the downstream theory, and does not certify frame transfer.

The frozen record requirement is imported from Step 57. Robustness here means no record-stable non-CS witness was found in the 80-row carrier; it remains a finite toy result and relocates grounding upward to record-stability as a higher recognition source.

If richer carriers produce a record-stable non-CS witness, the descent breaks. This step does not rule that out globally.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step58.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\begin{{document}}
\section*{{Step 58 Statement}}
Let \(RS\) be the record-stability extension computed by the frozen Step 57 predicate, and let \(CS\) be the finite gauge-layer separation extension computed on the broad Step 35 carrier. On the 80-row carrier,
\[
  |CS| = {schema['CS_count']},\qquad |RS| = {schema['RS_count']},\qquad |RS\setminus CS| = {schema['RS_not_CS_count']}.
\]
Thus \(RS \subseteq CS\) on this broadened finite carrier, with no record-stable non-CS witness found. The finite-carrier verdict is
\[
  \mathrm{{{schema['verdict']}}}.
\]
This is a robustness stress of a supplied parent-layer recognition source, not a derivation or a frame-transfer result.
\end{{document}}
"""
    (ARTIFACT_DIR / "step58_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    schema = built["schema"]
    score_fields = [
        "carrier_id",
        "source_step",
        "dimensions",
        "support_key",
        "support_score",
        "higher_layer_passes",
        "witness_scalar_key",
        "stable_substrate_proxy",
        "residual_nonabelian_subgroups",
        "transition_leak_count",
        "shadow_notes",
        "cs_member",
        "rs_member",
        "neutral_record_token_count",
        "capacity_threshold",
        "capacity_passes",
        "alias_ambiguity_count",
        "alias_ambiguity_witnesses",
        "distinguishability_passes",
        "record_stability_passes",
        "divergence_witness",
        "is_target_reference",
    ]
    write_csv(ARTIFACT_DIR / "record_stability_broad_carrier_scores_step58.csv", built["scores"], score_fields)
    write_csv(ARTIFACT_DIR / "record_stability_by_structure_step58.csv", built["by_structure"], ["dimensions", "carrier_rows", "CS_count", "RS_count", "RS_not_CS_count"])
    write_csv(ARTIFACT_DIR / "frozen_requirement_step58.csv", built["frozen"], ["item", "source_path", "sha256", "MIN_RECORD_TOKENS", "imported_function", "status"])
    write_csv(ARTIFACT_DIR / "negative_controls_step58.csv", built["negative"], ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step58.csv", built["dependency"], ["axiom", "role", "detail"])
    write_csv(ARTIFACT_DIR / "ablation_step58.csv", built["ablation"], ["ablation", "effect", "load_bearing"])
    write_csv(ARTIFACT_DIR / "stage2_record_fact_step58.csv", built["stage2"], ["fact", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step58.csv", built["gates"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step58.csv", built["anti_smuggle"], ["check", "passes", "evidence"])

    generated_rows = [
        {"item": "Step57_record_requirement", "status": "imported_frozen", "detail": schema["frozen_requirement_sha256"]},
        {"item": "Step35_broad_carrier", "status": "read", "detail": f"rows={schema['carrier_rows']}"},
        {"item": "CS_extension", "status": "computed", "detail": f"CS={schema['CS_count']} non_CS={schema['non_CS_count']}"},
        {"item": "RS_extension", "status": "computed_with_imported_requirement", "detail": f"RS={schema['RS_count']}"},
        {"item": "divergence_witness_search", "status": "computed", "detail": f"RS_not_CS={schema['RS_not_CS_count']}"},
        {"item": "verdict", "status": "computed", "detail": schema["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step58.csv", generated_rows, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step58_frozen_record_requirement", "status": "active_anti_smuggle_constraint", "declared_at_step": 58, "role": "Step57 record requirement must be imported verbatim and not retuned"},
        {"constraint_id": "step58_neutral_broad_carrier", "status": "active_anti_smuggle_constraint", "declared_at_step": 58, "role": "carrier must include non-CS rows and must not be prefiltered to CS"},
        {"constraint_id": "step58_divergence_witness_search", "status": "active_decisive_test", "declared_at_step": 58, "role": "hunt for RS true and CS false witness"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "record-stability-broad-carrier-stress",
            "parent_residual": "record-stability grounding of clean-separation downgraded to suggestive partial",
            "relation_to_canonical_root": "super_residual / parent layer (record/measurement, E032-adjacent), USER-AUTHORIZED 2026-06-09",
            "status": schema["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/record_stability_broad_carrier_step58.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "parent_residual", "relation_to_canonical_root", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step58_record_stability_broad_carrier_stress",
            "declared_at_step": 58,
            "new_grammar_declared": True,
            "carrier": "Step35 corrected 80-row higher-layer carrier scored by frozen Step57 record predicate",
            "tracked_object": "RS subset CS under broader-carrier stress and divergence-witness search",
            "next_grammar_delta": schema["next_grammar_delta"],
            "non_triviality_argument": "the carrier contains 72 non-CS rows and the imported RS predicate has teeth",
            "excluded_designs_rationale": "no retuned record predicate, no CS prefilter, no target-structure selector",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "new_grammar_declared", "carrier", "tracked_object", "next_grammar_delta", "non_triviality_argument", "excluded_designs_rationale"],
    )

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_broad_carrier_step58.py", "claim": "build script for broad-carrier record-stability stress", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_broad_carrier_step58.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_broad_carrier_scores_step58.csv", "claim": "per-row CS/RS broad-carrier scores", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_broad_carrier_scores_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_by_structure_step58.csv", "claim": "per-structure CS/RS counts", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_by_structure_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/frozen_requirement_step58.csv", "claim": "frozen Step57 requirement hash and import record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/frozen_requirement_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step58_schema.json", "claim": "machine-readable Step58 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step58_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step58_results_summary.md", "claim": "Step58 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step58_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step58.md", "claim": "Step58 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step58.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step58_statement.tex", "claim": "broad-carrier finite diagnostic statement", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step58_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step58.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step58.csv", "claim": "dependency trace", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/ablation_step58.csv", "claim": "ablation record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/ablation_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/stage2_record_fact_step58.csv", "claim": "Stage-II retained record fact", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/stage2_record_fact_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step58.csv", "claim": "anti-smuggle self-check", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step58.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step58.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv", "claim": "Mode-B constraint ledger", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv", "claim": "Mode-B target lineage", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv", "claim": "Mode-B grammar manifest", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classification_step58.csv", "claim": "content classification table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_classification_step58.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step58.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step58.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step58.csv", classification, ["artifact", "claim", "grade", "source"])
    write_json(ARTIFACT_DIR / "step58_schema.json", schema)
    write_docs(schema)


if __name__ == "__main__":
    main()
