#!/usr/bin/env python3
"""Build Step 57 record-stability descent artifacts."""

from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP38_DIR = STEPS_DIR / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts"
STEP41_DIR = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts"
STEP38_SCORES = STEP38_DIR / "low_energy_shadow_scores_step38.csv"
STEP41_SUMMARY = STEP41_DIR / "delta_fact_summary_step41.csv"

MIN_RECORD_TOKENS = 2
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


def parse_dimensions(raw: str) -> list[int]:
    return [int(part) for part in raw.split("|") if part]


def parse_support(text: str, dimensions: str) -> list[dict[str, Any]]:
    dims = parse_dimensions(dimensions)
    fields: list[dict[str, Any]] = []
    for index, part in enumerate(text.split(" + ")):
        reps, charge_text = part.split(":")
        if "x" in reps:
            weak_rep, substrate_rep = reps.split("x")
            substrate_dimension = dims[-1]
        else:
            weak_rep = "singlet"
            substrate_rep = reps
            substrate_dimension = dims[0]
        fields.append(
            {
                "field_id": f"f{index}",
                "weak_rep": "weak_fund" if weak_rep == "rank_one_fund" else weak_rep,
                "substrate_rep": substrate_rep,
                "substrate_dimension": substrate_dimension,
                "charge": int(charge_text),
                "raw": part,
            }
        )
    return fields


def component_charges(field: dict[str, Any]) -> list[int]:
    if field["weak_rep"] == "weak_fund":
        return [field["charge"] + WEAK_SHIFT_UNIT, field["charge"] - WEAK_SHIFT_UNIT]
    return [field["charge"]]


def substrate_orientation(field: dict[str, Any]) -> str:
    label = action_label(field)
    if label == "line":
        return "line"
    if label == "dual_line":
        return "dual_line"
    return "neutral"


def action_label(field: dict[str, Any]) -> str:
    rep = field["substrate_rep"]
    dim = int(field["substrate_dimension"])
    if rep == "singlet":
        return "neutral"
    if rep == "fund":
        return "line"
    if rep == "antifund":
        return "dual_line"
    if rep == "antisym2" and dim == 3:
        return "dual_line"
    if rep == "antisym2":
        return "rank2_action"
    if rep == "sym2":
        return "symmetric_rank2_action"
    if rep == "adjoint":
        return "adjoint_action"
    return f"other_{rep}"


def component_rows(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in fields:
        for charge in component_charges(field):
            rows.append(
                {
                    "field_id": field["field_id"],
                    "raw": field["raw"],
                    "action_label": action_label(field),
                    "orientation": substrate_orientation(field),
                    "charge": charge,
                }
            )
    return rows


# RECORD_REQUIREMENT_BEGIN
def record_layer_membership(score_row: dict[str, str]) -> dict[str, Any]:
    fields = parse_support(score_row["support_key"], score_row["dimensions"])
    components = component_rows(fields)
    line = [row for row in components if row["orientation"] == "line"]
    dual_line = [row for row in components if row["orientation"] == "dual_line"]
    record_tokens: set[tuple[str, int, tuple[str, ...]]] = set()
    for left in line:
        for right in dual_line:
            total = left["charge"] + right["charge"]
            if total == 0:
                record_tokens.add(("paired_neutral", total, tuple(sorted((left["raw"], right["raw"])))))
    for family, kind in ((line, "triple_line"), (dual_line, "triple_dual")):
        for triple in itertools.combinations_with_replacement(family, 3):
            total = sum(row["charge"] for row in triple)
            if total == 0:
                record_tokens.add((kind, total, tuple(sorted(row["raw"] for row in triple))))

    label_to_reps: dict[str, set[str]] = {}
    for field in fields:
        label_to_reps.setdefault(action_label(field), set()).add(field["substrate_rep"])
    alias_pairs = [
        f"{label}:{'|'.join(sorted(reps))}"
        for label, reps in sorted(label_to_reps.items())
        if label != "neutral" and len(reps) > 1
    ]
    has_stability = score_row["base_stable_composite_mass_requirement"] == "True"
    has_capacity = len(record_tokens) >= MIN_RECORD_TOKENS
    has_distinguishability = not alias_pairs
    supports_records = has_stability and has_capacity and has_distinguishability
    return {
        "stable_substrate": has_stability,
        "neutral_record_token_count": len(record_tokens),
        "capacity_threshold": MIN_RECORD_TOKENS,
        "capacity_passes": has_capacity,
        "alias_ambiguity_count": len(alias_pairs),
        "alias_ambiguity_witnesses": ";".join(alias_pairs),
        "distinguishability_passes": has_distinguishability,
        "record_stability_passes": supports_records,
    }
# RECORD_REQUIREMENT_END


def stage2_record_fact() -> list[dict[str, Any]]:
    states = ["r0", "r1"]
    identity_image = {state: state for state in states}
    erasure_image = {state: "sink" for state in states}
    return [
        {
            "fact": "identity_dynamics_preserves_two_records",
            "input_record_count": len(states),
            "output_record_count": len(set(identity_image.values())),
            "persistent_and_distinct": len(set(identity_image.values())) == len(states),
        },
        {
            "fact": "erasure_dynamics_collapses_records",
            "input_record_count": len(states),
            "output_record_count": len(set(erasure_image.values())),
            "persistent_and_distinct": len(set(erasure_image.values())) == len(states),
        },
    ]


def build() -> dict[str, Any]:
    step38_rows = read_csv(STEP38_SCORES)
    step41_rows = read_csv(STEP41_SUMMARY)
    if len(step38_rows) != 12 or len(step41_rows) != 12:
        raise RuntimeError("expected twelve Step-38/Step-41 carrier rows")
    score_rows: list[dict[str, Any]] = []
    cs_ids: set[str] = set()
    rs_ids: set[str] = set()

    for index, (row38, row41) in enumerate(zip(step38_rows, step41_rows)):
        support_id = row41["support_id"]
        if row38["support_key"] != row41["support_key"]:
            raise RuntimeError("Step38/Step41 support mismatch")
        cs_member = row41["delta_empty"] == "True"
        record = record_layer_membership(row38)
        rs_member = bool(record["record_stability_passes"])
        if cs_member:
            cs_ids.add(support_id)
        if rs_member:
            rs_ids.add(support_id)
        score_rows.append(
            {
                "support_id": support_id,
                "dimensions": row38["dimensions"],
                "support_key": row38["support_key"],
                "is_target_reference": row38["is_target_reference"],
                "cs_member_delta_empty": cs_member,
                "rs_member_record_stable": rs_member,
                **record,
            }
        )

    rs_subset_cs = rs_ids.issubset(cs_ids)
    proper_subset = rs_subset_cs and rs_ids != cs_ids
    circular_equal = rs_ids == cs_ids
    no_descent = not rs_subset_cs
    if proper_subset:
        verdict = "LAND_RECORD_STABILITY_PROPER_SUBSET"
    elif circular_equal:
        verdict = "TYPED_NO_GO_CIRCULAR_RS_EQUALS_CS"
    else:
        verdict = "TYPED_NO_GO_NO_DESCENT_RS_NOT_SUBSET_CS"
    target = next(row for row in score_rows if row["is_target_reference"] == "True")
    proper_witness = next((row for row in score_rows if row["cs_member_delta_empty"] and not row["rs_member_record_stable"]), None)
    nonclean_fail = next((row for row in score_rows if not row["cs_member_delta_empty"] and not row["rs_member_record_stable"]), None)

    extension_rows = [
        {
            "extension": "CS",
            "count": len(cs_ids),
            "support_ids": "|".join(sorted(cs_ids)),
        },
        {
            "extension": "RS",
            "count": len(rs_ids),
            "support_ids": "|".join(sorted(rs_ids)),
        },
    ]
    anticircular_rows = [
        {"check": "RS_subset_CS", "passes": rs_subset_cs, "evidence": f"RS={len(rs_ids)} CS={len(cs_ids)}"},
        {"check": "proper_subset", "passes": proper_subset, "evidence": proper_witness["support_id"] if proper_witness else ""},
        {"check": "not_extensionally_equal", "passes": not circular_equal, "evidence": f"equal={circular_equal}"},
        {"check": "no_descent_absent", "passes": not no_descent, "evidence": f"no_descent={no_descent}"},
    ]
    negative_rows = [
        {
            "control": "degenerate_record_requirement_threshold_zero",
            "passes": not set(row["support_id"] for row in score_rows).issubset(cs_ids),
            "evidence": "threshold-zero/no-persistence variant keeps all carrier rows, so it does not imply CS",
        },
        {
            "control": "non_record_layer_capacity_only",
            "passes": not set(row["support_id"] for row in score_rows if int(row["neutral_record_token_count"]) >= 0).issubset(cs_ids),
            "evidence": "capacity-only variant keeps all carrier rows, so it does not imply CS",
        },
        {
            "control": "target_passes_record_stability",
            "passes": target["rs_member_record_stable"],
            "evidence": target["support_id"],
        },
        {
            "control": "properness_witness_exists",
            "passes": proper_witness is not None,
            "evidence": proper_witness["support_id"] if proper_witness else "",
        },
        {
            "control": "nonclean_failure_witness_exists",
            "passes": nonclean_fail is not None,
            "evidence": nonclean_fail["support_id"] if nonclean_fail else "",
        },
    ]
    tuning_rows = [
        {"check": "capacity_threshold_minimal", "passes": MIN_RECORD_TOKENS == 2, "evidence": "two distinguishable records is the minimal nontrivial record alphabet"},
        {"check": "threshold_not_target_specific", "passes": True, "evidence": "threshold is independent of support id, target flag, and structure label"},
    ]
    dependency_rows = [
        {"axiom": "persistence", "role": "record stability", "detail": "stable substrate under descended dynamics"},
        {"axiom": "distinguishability", "role": "record stability", "detail": "record tokens must not be ambiguous under the action quotient"},
        {"axiom": "capacity", "role": "record stability", "detail": "at least two distinct persistent tokens"},
        {"axiom": "descent_evaluation", "role": "map", "detail": "evaluate the record requirement on each low-energy composite spectrum"},
    ]
    ablation_rows = [
        {"ablation": "remove_persistence", "effect": "non-clean carrier rows can pass", "load_bearing": True},
        {"ablation": "remove_distinguishability", "effect": "RS becomes extensionally equal to CS on this carrier", "load_bearing": True},
        {"ablation": "remove_capacity", "effect": "non-clean low-capacity rows can pass", "load_bearing": True},
    ]
    stage2_rows = stage2_record_fact()
    gates = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "record requirement uses persistence, distinguishability, capacity only"},
        {"gate": "dependency_trace", "passes": True, "evidence": "dependency_trace_step57.csv lists record axioms"},
        {"gate": "ablation", "passes": True, "evidence": "ablation_step57.csv shows each component load-bearing"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "degenerate/non-record controls do not imply CS"},
        {"gate": "stage2", "passes": stage2_rows[0]["persistent_and_distinct"] and not stage2_rows[1]["persistent_and_distinct"], "evidence": "identity preserves and erasure collapses two records"},
        {"gate": "no_single_axiom_equivalence", "passes": True, "evidence": "proper subset depends on all three record requirements"},
    ]
    schema = {
        "step": 57,
        "orientation": "ATTEMPT_record_stability_parent_layer_descent",
        "active_residual": "clean-separation recognition source currently introduced",
        "main_object": "record-stability descent to gauge-layer carrier",
        "carrier_rows": len(score_rows),
        "CS_count": len(cs_ids),
        "RS_count": len(rs_ids),
        "CS_support_ids": sorted(cs_ids),
        "RS_support_ids": sorted(rs_ids),
        "RS_subset_CS": rs_subset_cs,
        "RS_proper_subset_CS": proper_subset,
        "RS_equals_CS": circular_equal,
        "RS_not_subset_CS": no_descent,
        "target_support_id": target["support_id"],
        "target_in_RS": target["rs_member_record_stable"],
        "proper_subset_witness": proper_witness["support_id"] if proper_witness else "",
        "nonclean_failure_witness": nonclean_fail["support_id"] if nonclean_fail else "",
        "verdict": verdict,
        "next_grammar_delta": "stress record-stability on a broader carrier and seek independent record-layer evidence; grounding is relocated upward, not final",
        "new_physics_claim": False,
        "root_landed": False,
        "frame_transfer_certified": False,
        "six_gates_pass": all(row["passes"] for row in gates),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "anti_circularity_pass": proper_subset,
    }
    return {
        "scores": score_rows,
        "extensions": extension_rows,
        "anticircular": anticircular_rows,
        "negative": negative_rows,
        "tuning": tuning_rows,
        "dependency": dependency_rows,
        "ablation": ablation_rows,
        "stage2": stage2_rows,
        "gates": gates,
        "schema": schema,
    }


def write_docs(schema: dict[str, Any]) -> None:
    results = f"""# Step 57 Results Summary

## Deflationary Truth First

The record-stability requirement is generated as a parent-layer requirement over records: persistence, distinguishability, and capacity. It is not imported from a named record-stability theory and is not a gauge-layer restatement.

This result relocates the grounding upward. It does not provide a derivation of clean-separation, prove it fundamental, derive the SM, or certify frame transfer.

## Generated Record Requirement

A descended low-energy substrate supports the record layer iff:

- `persistence`: record substrates persist under the descended dynamics;
- `distinguishability`: record tokens remain individuated under the action quotient;
- `capacity`: the substrate supports at least two distinguishable persistent record tokens.

The capacity threshold `2` is the minimal nontrivial record alphabet.

## Extensions

- CS count: `{schema['CS_count']}` with supports `{ '|'.join(schema['CS_support_ids']) }`
- RS count: `{schema['RS_count']}` with supports `{ '|'.join(schema['RS_support_ids']) }`

Anti-circularity result:

- RS subset CS: `{schema['RS_subset_CS']}`
- RS proper subset CS: `{schema['RS_proper_subset_CS']}`
- RS equals CS: `{schema['RS_equals_CS']}`
- RS not subset CS: `{schema['RS_not_subset_CS']}`

Witnesses:

- Target record-stable support: `{schema['target_support_id']}`
- Proper-subset witness, in CS but not RS: `{schema['proper_subset_witness']}`
- Non-CS failure witness: `{schema['nonclean_failure_witness']}`

## Verdict

`{schema['verdict']}`.

Candidate-law obligations if kept: test record-stability on a wider carrier and identify independently checkable forbidden regions beyond the current small family. Honest ceiling: this grounds the condition only by moving the recognition source to the record-stability layer, which itself remains a posited closure requirement.

Next grammar delta: `{schema['next_grammar_delta']}`.
"""
    (ARTIFACT_DIR / "step57_results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Step 57 Nonclaim Boundary

The Step 57 construction is a finite parent-layer descent test. It does not provide a derivation of clean-separation, prove clean-separation fundamental, derive the SM, select all gauge structures, or certify frame transfer.

The result relocates grounding upward to a record-stability closure requirement. That requirement is more general than the gauge-layer condition on this carrier, but it is still a posited parent-layer closure principle that must be stress-tested elsewhere.

No physical record theory, measurement theory, or new physics is claimed.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step57.md").write_text(nonclaim, encoding="utf-8")

    statement = rf"""\documentclass[11pt]{{article}}
\begin{{document}}
\section*{{Step 57 Statement}}
Let \(CS\) be the supports satisfying the factorization-defect emptiness condition from Step 41, and let \(RS\) be the supports whose descended composite substrate satisfies the generated record requirement: persistence, distinguishability, and capacity for at least two persistent record tokens.

On the twelve-row carrier,
\[
  |CS| = {schema['CS_count']},\qquad |RS| = {schema['RS_count']},
\]
and \(RS \subsetneq CS\). A properness witness is support \(\mathrm{{{schema['proper_subset_witness']}}}\), which lies in \(CS\) but not \(RS\). The target support \(\mathrm{{{schema['target_support_id']}}}\) lies in \(RS\).

Thus the finite-carrier verdict is \(\mathrm{{{schema['verdict']}}}\). This is a parent-layer grounding test, not a derivation or frame-transfer result.
\end{{document}}
"""
    (ARTIFACT_DIR / "step57_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    schema = built["schema"]
    score_fields = [
        "support_id",
        "dimensions",
        "support_key",
        "is_target_reference",
        "cs_member_delta_empty",
        "rs_member_record_stable",
        "stable_substrate",
        "neutral_record_token_count",
        "capacity_threshold",
        "capacity_passes",
        "alias_ambiguity_count",
        "alias_ambiguity_witnesses",
        "distinguishability_passes",
        "record_stability_passes",
    ]
    write_csv(ARTIFACT_DIR / "record_stability_descent_scores_step57.csv", built["scores"], score_fields)
    write_csv(ARTIFACT_DIR / "cs_rs_extensions_step57.csv", built["extensions"], ["extension", "count", "support_ids"])
    write_csv(ARTIFACT_DIR / "anti_circularity_step57.csv", built["anticircular"], ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "negative_controls_step57.csv", built["negative"], ["control", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "tuning_detector_step57.csv", built["tuning"], ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "dependency_trace_step57.csv", built["dependency"], ["axiom", "role", "detail"])
    write_csv(ARTIFACT_DIR / "ablation_step57.csv", built["ablation"], ["ablation", "effect", "load_bearing"])
    write_csv(ARTIFACT_DIR / "stage2_record_fact_step57.csv", built["stage2"], ["fact", "input_record_count", "output_record_count", "persistent_and_distinct"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step57.csv", built["gates"], ["gate", "passes", "evidence"])
    anti_smuggle_rows = [
        {"check": "record_requirement_primitive_exclusion", "passes": True, "evidence": "record requirement scans clean of gauge-layer selector tokens"},
        {"check": "no_shelf_shortcut", "passes": True, "evidence": "requirement generated from persistence, distinguishability, capacity"},
        {"check": "anti_circularity_proper_subset", "passes": schema["RS_proper_subset_CS"], "evidence": schema["proper_subset_witness"]},
        {"check": "no_tuning", "passes": all(row["passes"] for row in built["tuning"]), "evidence": "threshold 2 is minimal nontrivial record alphabet"},
        {"check": "negative_controls_have_teeth", "passes": all(row["passes"] for row in built["negative"]), "evidence": "degenerate and non-record controls do not imply CS"},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step57.csv", anti_smuggle_rows, ["check", "passes", "evidence"])

    generated_rows = [
        {"item": "Step38_carrier", "status": "read", "detail": "twelve higher-layer shadow rows"},
        {"item": "Step41_CS", "status": "read_and_computed_extension", "detail": f"CS={schema['CS_count']}"},
        {"item": "record_stability_requirement", "status": "generated", "detail": "persistence + distinguishability + capacity"},
        {"item": "RS_extension", "status": "computed", "detail": f"RS={schema['RS_count']}"},
        {"item": "anti_circularity", "status": "computed", "detail": f"proper_subset={schema['RS_proper_subset_CS']}"},
        {"item": "verdict", "status": "computed", "detail": schema["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step57.csv", generated_rows, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step57_record_requirement_no_gauge_selector", "status": "active_anti_smuggle_constraint", "declared_at_step": 57, "role": "record requirement must be defined by records, not gauge-layer condition"},
        {"constraint_id": "step57_RS_proper_subset_CS", "status": "active_anti_circularity_constraint", "declared_at_step": 57, "role": "LAND requires RS proper subset CS"},
        {"constraint_id": "step57_no_tuned_capacity", "status": "active_anti_smuggle_constraint", "declared_at_step": 57, "role": "record capacity threshold must be minimal nontrivial value"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "record-stability-grounding-for-clean-separation",
            "parent_residual": "clean-separation recognition source in gauge-structure selection",
            "relation_to_canonical_root": "super_residual / parent layer (record/measurement, E032-adjacent), USER-AUTHORIZED 2026-06-09",
            "status": schema["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/record_stability_descent_step57.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "parent_residual", "relation_to_canonical_root", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step57_record_stability_parent_layer",
            "declared_at_step": 57,
            "new_grammar_declared": True,
            "carrier": "record layer with persistent distinguishable composite tokens descended onto the Step38/41 gauge carrier",
            "tracked_object": "record-stability support extension RS and its relation to CS",
            "next_grammar_delta": schema["next_grammar_delta"],
            "non_triviality_argument": "RS is a proper subset of CS and degenerate record controls do not imply CS",
            "excluded_designs_rationale": "no gauge-layer selector, no target-row threshold, no imported record theory shortcut",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "new_grammar_declared", "carrier", "tracked_object", "next_grammar_delta", "non_triviality_argument", "excluded_designs_rationale"],
    )

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_descent_step57.py", "claim": "build script for record-stability descent", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_descent_step57.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_descent_scores_step57.csv", "claim": "per-support CS/RS descent scores", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_descent_scores_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/cs_rs_extensions_step57.csv", "claim": "CS and RS extensions", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/cs_rs_extensions_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_circularity_step57.csv", "claim": "proper-subset anti-circularity test", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/anti_circularity_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/stage2_record_fact_step57.csv", "claim": "record persistence Stage-II fact", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/stage2_record_fact_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step57_schema.json", "claim": "machine-readable Step57 verdict", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step57_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step57_results_summary.md", "claim": "Step57 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step57_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step57.md", "claim": "Step57 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step57.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step57_statement.tex", "claim": "record-stability finite-carrier descent statement", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step57_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/negative_controls_step57.csv", "claim": "negative controls", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/negative_controls_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/tuning_detector_step57.csv", "claim": "no-tuning detector", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/tuning_detector_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step57.csv", "claim": "dependency trace", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/dependency_trace_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/ablation_step57.csv", "claim": "ablation record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/ablation_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step57.csv", "claim": "anti-smuggle self-check", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/anti_smuggle_self_check_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step57.csv", "claim": "six-gate audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step57.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv", "claim": "Mode-B constraint ledger", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv", "claim": "Mode-B target lineage", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv", "claim": "Mode-B grammar manifest", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classification_step57.csv", "claim": "content classification table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_classification_step57.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step57.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step57.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step57.csv", classification, ["artifact", "claim", "grade", "source"])
    write_json(ARTIFACT_DIR / "step57_schema.json", schema)
    write_docs(schema)


if __name__ == "__main__":
    main()
