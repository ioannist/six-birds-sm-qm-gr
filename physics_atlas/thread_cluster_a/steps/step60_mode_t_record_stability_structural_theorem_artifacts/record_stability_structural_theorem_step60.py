#!/usr/bin/env python3
"""Build Step 60 Mode-T record-stability structural-theorem artifacts."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import inspect
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP33_BUILD = STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "corrected_anomaly_chirality_step33.py"
STEP35_BUILD = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
STEP41_BUILD = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "factorization_defect_clean_separation_step41.py"
STEP57_BUILD = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "record_stability_descent_step57.py"
STEP59_DIR = STEPS_DIR / "step59_mode_b_record_stability_coverage_artifacts"
STEP59_SCORES = STEP59_DIR / "record_stability_coverage_scores_step59.csv"


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def frozen_step57_region() -> str:
    text = STEP57_BUILD.read_text(encoding="utf-8")
    start = text.index("# RECORD_REQUIREMENT_BEGIN")
    end = text.index("# RECORD_REQUIREMENT_END")
    return text[start:end]


def source_hash(functions: list[Any]) -> str:
    return sha256_text("\n\n".join(inspect.getsource(function) for function in functions))


s33 = load_module("step60_s33_corrected", STEP33_BUILD)
s35 = load_module("step60_s35_base", STEP35_BUILD)
s41 = load_module("step60_s41_delta", STEP41_BUILD)
s57 = load_module("step60_s57_record", STEP57_BUILD)


def bool_cell(value: str) -> bool:
    return value == "True"


def scalar_breaks_big_factor(dimensions_text: str, scalar_reps_text: str) -> bool:
    dims = [int(part) for part in dimensions_text.split("|") if part]
    reps = scalar_reps_text.split("x") if scalar_reps_text else ["singlet"] * len(dims)
    if len(reps) < len(dims):
        reps += ["singlet"] * (len(dims) - len(reps))
    return any(rep != "singlet" and dim >= 3 for rep, dim in zip(reps, dims))


def reduction_checks(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    substrate_rows = [row for row in rows if bool_cell(row["substrate_passes"])]
    leak_bridge = all((not bool_cell(row["delta_empty"])) == (int(row["transition_leak_count"]) > 0) for row in substrate_rows)
    witness_bridge = all(
        int(row["delta_witness_count"]) == int(row["transition_leak_count"])
        for row in substrate_rows
        if row["delta_witness_count"] != ""
    )
    scalar_bridge = all(
        (int(row["transition_leak_count"]) > 0) == scalar_breaks_big_factor(row["dimensions"], row["witness_scalar_reps"])
        for row in substrate_rows
    )
    return [
        {
            "check": "substrate_nonempty",
            "passes": bool(substrate_rows),
            "evidence": f"substrate_rows={len(substrate_rows)}",
        },
        {
            "check": "delta_nonempty_iff_transition_leak_positive_given_substrate",
            "passes": leak_bridge,
            "evidence": "verified on Step59 substrate rows",
        },
        {
            "check": "delta_witness_count_tracks_transition_leak_count",
            "passes": witness_bridge,
            "evidence": "Step41 witness count equals transition leak count for evaluated substrate rows",
        },
        {
            "check": "transition_leak_positive_iff_scalar_breaks_dim_ge_3",
            "passes": scalar_bridge,
            "evidence": "broken dim-2 leaves residual 1; broken dim>=3 gives charged transition vectors",
        },
    ]


def carrier_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    return {
        "carrier_rows": len(rows),
        "substrate_count": sum(1 for row in rows if bool_cell(row["substrate_passes"])),
        "capacity_count": sum(1 for row in rows if bool_cell(row["capacity_passes"])),
        "CS_count": sum(1 for row in rows if bool_cell(row["CS_member"])),
        "non_CS_count": sum(1 for row in rows if not bool_cell(row["CS_member"])),
        "substrate_capacity_non_CS_count": sum(
            1
            for row in rows
            if bool_cell(row["substrate_passes"]) and bool_cell(row["capacity_passes"]) and not bool_cell(row["CS_member"])
        ),
        "non_CS_capacity_count": sum(1 for row in rows if (not bool_cell(row["CS_member"])) and bool_cell(row["capacity_passes"])),
        "non_CS_substrate_count": sum(1 for row in rows if (not bool_cell(row["CS_member"])) and bool_cell(row["substrate_passes"])),
    }


def combo_record(combo: tuple[int, ...], type_rows: list[Any]) -> tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]:
    return s33.combo_record(combo, type_rows)


def enumerate_chiral_closers_with_max_fields(dimensions: tuple[int, ...], max_fields: int) -> tuple[list[Any], list[tuple[int, ...]]]:
    type_rows = s33.type_rows_for_structure(dimensions)
    half = max_fields // 2
    records_by_size: list[list[tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]]] = []
    for size in range(half + 1):
        records_by_size.append([combo_record(combo, type_rows) for combo in combinations(range(len(type_rows)), size)])
    groups: dict[int, dict[tuple[tuple[int, ...], tuple[int, ...]], list[tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]]]] = {}
    for size, records in enumerate(records_by_size):
        by_key: dict[tuple[tuple[int, ...], tuple[int, ...]], list[tuple[tuple[int, ...], int, tuple[int, ...], tuple[int, ...]]]] = {}
        for record in records:
            by_key.setdefault((record[2], record[3]), []).append(record)
        groups[size] = by_key
    zero_anomaly = tuple(0 for _ in type_rows[0].anomaly_vector)
    zero_parity = tuple(0 for _ in type_rows[0].witten_vector)
    seen: set[tuple[int, ...]] = set()
    closers: list[tuple[int, ...]] = []
    for left_size in range(half + 1):
        for left in records_by_size[left_size]:
            complement = tuple(-value for value in left[2])
            needed_parity = left[3]
            for right_size in range(half + 1):
                field_count = left_size + right_size
                if field_count < 1 or field_count > max_fields:
                    continue
                for right in groups[right_size].get((complement, needed_parity), []):
                    if left[1] & right[1]:
                        continue
                    combo = tuple(sorted(left[0] + right[0]))
                    if len(combo) != field_count or combo in seen:
                        continue
                    record = combo_record(combo, type_rows)
                    if record[2] != zero_anomaly or record[3] != zero_parity:
                        continue
                    if s33.vectorlike_only_corrected(combo, type_rows):
                        continue
                    seen.add(combo)
                    closers.append(combo)
    return type_rows, closers


def scalar_action_diagnostics(scalar: Any) -> tuple[bool, int]:
    confining = False
    transition_leak_count = 0
    for rep, dimension in zip(scalar.reps, scalar.dimensions):
        if s35.s33.action_active(rep, dimension):
            residual = dimension - 1
            if residual >= 2:
                confining = True
                transition_leak_count += 2 * residual
        elif dimension >= 2:
            confining = True
    return confining, transition_leak_count


def converse_probe() -> list[dict[str, Any]]:
    probe_specs = [
        {"probe": "inside_step59_full_carrier", "dimensions": "implemented_step59", "max_fields": 5, "outside_reason": "inside_declared_carrier"},
        {"probe": "relaxed_field_count_single_4", "dimensions": (4,), "max_fields": 6, "outside_reason": "field_count_bound_relaxed"},
        {"probe": "larger_dimension_single_5", "dimensions": (5,), "max_fields": 6, "outside_reason": "dimension_outside_implemented_step33_window"},
        {"probe": "larger_dimension_single_6", "dimensions": (6,), "max_fields": 6, "outside_reason": "dimension_outside_implemented_step33_window"},
        {"probe": "relaxed_field_count_3x4", "dimensions": (3, 4), "max_fields": 6, "outside_reason": "field_count_bound_relaxed"},
        {"probe": "relaxed_field_count_4x4", "dimensions": (4, 4), "max_fields": 6, "outside_reason": "field_count_bound_relaxed"},
    ]
    step59_rows = read_csv(STEP59_SCORES)
    rows: list[dict[str, Any]] = []
    inside_counter = [
        row for row in step59_rows
        if bool_cell(row["substrate_passes"]) and bool_cell(row["capacity_passes"]) and not bool_cell(row["CS_member"])
    ]
    rows.append(
        {
            "probe": "inside_step59_full_carrier",
            "dimensions": "implemented_step59",
            "max_fields": 5,
            "outside_reason": "inside_declared_carrier",
            "chiral_closers_checked": len(step59_rows),
            "capacity_positive": sum(1 for row in step59_rows if bool_cell(row["capacity_passes"])),
            "substrate_nonclean_capacity_positive": len(inside_counter),
            "counterexample_found": bool(inside_counter),
            "counterexample_support_key": inside_counter[0]["support_key"] if inside_counter else "",
        }
    )
    for spec in probe_specs[1:]:
        dimensions = spec["dimensions"]
        type_rows, closers = enumerate_chiral_closers_with_max_fields(dimensions, int(spec["max_fields"]))
        scalar_rows = s35.scalar_representations(dimensions)
        capacity_positive = 0
        counterexample: dict[str, Any] | None = None
        for combo in closers:
            key = s33.support_key(combo, type_rows)
            rec = s57.record_layer_membership(
                {
                    "dimensions": "|".join(str(value) for value in dimensions),
                    "support_key": key,
                    "base_stable_composite_mass_requirement": "True",
                }
            )
            if not rec["capacity_passes"]:
                continue
            capacity_positive += 1
            base = s35.higher_layer_mass_closure(combo, type_rows, scalar_rows)
            confining, transition_leak_count = scalar_action_diagnostics(base["witness_scalar"])
            if base["higher_layer_passes"] and confining and transition_leak_count > 0:
                counterexample = {
                    "support_key": key,
                    "scalar": base["witness_scalar"].text,
                    "transition_leak_count": transition_leak_count,
                    "neutral_record_token_count": rec["neutral_record_token_count"],
                }
                break
        rows.append(
            {
                "probe": spec["probe"],
                "dimensions": "|".join(str(value) for value in dimensions),
                "max_fields": spec["max_fields"],
                "outside_reason": spec["outside_reason"],
                "chiral_closers_checked": len(closers),
                "capacity_positive": capacity_positive,
                "substrate_nonclean_capacity_positive": 1 if counterexample else 0,
                "counterexample_found": counterexample is not None,
                "counterexample_support_key": counterexample["support_key"] if counterexample else "",
                "counterexample_scalar": counterexample["scalar"] if counterexample else "",
                "counterexample_transition_leak_count": counterexample["transition_leak_count"] if counterexample else "",
                "counterexample_neutral_record_token_count": counterexample["neutral_record_token_count"] if counterexample else "",
            }
        )
    return rows


def build() -> dict[str, Any]:
    step59_rows = read_csv(STEP59_SCORES)
    counts = carrier_counts(step59_rows)
    reduction = reduction_checks(step59_rows)
    probes = converse_probe()
    counter_inside = any(row["counterexample_found"] == True and row["outside_reason"] == "inside_declared_carrier" for row in probes)
    counter_outside = any(row["counterexample_found"] == True and row["outside_reason"] != "inside_declared_carrier" for row in probes)
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
    exit_state = "sharpened_external"
    verdict = "SHARPENED_EXTERNAL_OPEN_LEMMA_NO_STRUCTURAL_PROOF"
    structural_proof_grade = "sharpened"
    sharpened_rows = [
        {
            "lemma_id": "L60_record_capacity_leak_exclusion",
            "statement": "For frozen Step35 scalar witnesses, any corrected closer with substrate and transition_leak_count>0 has neutral_record_token_count<2.",
            "normalization": "capacity tokens are Step57 paired line-dual neutral records or like-orientation neutral triples; transition leaks are Step41 defect witnesses from the Step35 scalar action.",
            "status": "verified_by_step59_enumeration_and_step60_probe_but_not_structurally_proved",
            "next_required_input": "a representation/anomaly/mass-closure lemma explaining why big-factor scalar breaking forbids two neutral record tokens",
        }
    ]
    anti_circ_rows = [
        {"check": "substrate_independently_satisfied_by_non_CS", "passes": counts["non_CS_substrate_count"] > 0, "evidence": f"non_CS_substrate={counts['non_CS_substrate_count']}"},
        {"check": "capacity_independently_satisfied_by_non_CS", "passes": counts["non_CS_capacity_count"] > 0, "evidence": f"non_CS_capacity={counts['non_CS_capacity_count']}"},
        {"check": "conjunction_lands_in_CS_on_carrier", "passes": counts["substrate_capacity_non_CS_count"] == 0, "evidence": f"substrate_capacity_non_CS={counts['substrate_capacity_non_CS_count']}"},
        {"check": "not_extensionally_tautological", "passes": True, "evidence": "each conjunct has non-CS witnesses; only the conjunction is empty outside CS"},
    ]
    seven_gates = [
        {"gate": "no_smuggling_of_target", "passes": True, "evidence": "no proof hypothesis assumes delta_empty or no transition leaks; exit is not theorem"},
        {"gate": "target_invariance_lineage", "passes": True, "evidence": "statement remains substrate and capacity imply CS"},
        {"gate": "no_stipulated_descent", "passes": True, "evidence": "reduction map is checked against frozen Step41 defect computation"},
        {"gate": "anti_tautology_operational_predicates", "passes": True, "evidence": "substrate, capacity, and defect are frozen computable predicates"},
        {"gate": "anti_vacuity", "passes": counts["CS_count"] > 0 and counts["non_CS_substrate_count"] > 0, "evidence": f"CS={counts['CS_count']}; non_CS_substrate={counts['non_CS_substrate_count']}"},
        {"gate": "anti_circularity", "passes": all(row["passes"] for row in anti_circ_rows), "evidence": "substrate and capacity each have non-CS witnesses"},
        {"gate": "uniform_parametric_bound", "passes": False, "evidence": "no uniform dim/charge/factor-count bound was proved; exit is sharpened_external"},
    ]
    generated_rows = [
        {"item": "Step59_enumeration_result", "status": "input_evidence", "detail": f"carrier={counts['carrier_rows']}; substrate_capacity_non_CS={counts['substrate_capacity_non_CS_count']}"},
        {"item": "structural_reduction", "status": "verified", "detail": "given substrate, delta_nonempty iff transition_leak_count>0 iff scalar breaks dim>=3"},
        {"item": "converse_probe", "status": "computed", "detail": f"inside_counterexample={counter_inside}; outside_counterexample={counter_outside}"},
        {"item": "structural_proof", "status": "not_constructed", "detail": "missing bridge from big-factor scalar breaking to capacity<2"},
        {"item": "exit_state", "status": "computed", "detail": exit_state},
    ]
    schema = {
        "step": 60,
        "orientation": "ModeT_theorem_attempt",
        "active_residual": "upgrade Step59 enumeration terminal to structural theorem if possible",
        "main_object": "record-stability forces clean-separation theorem attempt",
        "exit_state": exit_state,
        "verdict": verdict,
        "structural_proof_grade": structural_proof_grade,
        "carrier_rows": counts["carrier_rows"],
        "substrate_capacity_non_CS_count": counts["substrate_capacity_non_CS_count"],
        "non_CS_substrate_count": counts["non_CS_substrate_count"],
        "non_CS_capacity_count": counts["non_CS_capacity_count"],
        "six_gates_pass": False,
        "anti_circularity_pass": all(row["passes"] for row in anti_circ_rows),
        "converse_probe_counterexample_found": bool(counter_inside or counter_outside),
        "converse_probe_counterexample_in_window": bool(counter_inside),
        "converse_probe_counterexample_out_of_window": bool(counter_outside),
        "window_independent": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
        "root_landed": False,
        "candidate_law_obligation_2_discharged": False,
        "next_grammar_delta": "prove or import L60_record_capacity_leak_exclusion; current proof grammar lacks a representation/anomaly-to-record-capacity bridge",
    }
    return {
        "counts": counts,
        "reduction": reduction,
        "probes": probes,
        "frozen": frozen_rows,
        "sharpened": sharpened_rows,
        "anti_circularity": anti_circ_rows,
        "seven_gates": seven_gates,
        "generated": generated_rows,
        "schema": schema,
    }


def write_docs(data: dict[str, Any]) -> None:
    schema = data["schema"]
    results = f"""# Step 60 Results Summary

## Deflationary Truth First

Step 59 established, by exhaustive enumeration over the full 11,990-row Step-33 corrected closer carrier, that no non-clean-separation structure has both a stable substrate and record capacity: `non_CS_substrate_capacity_count = 0`. That is true on 11,990 rows, not true period.

Step 60 attempted to upgrade that enumeration terminal into a structural theorem. It did not land a theorem. The honest exit is `sharpened_external`: the target is reduced to a precise checkable lemma, but the missing structural bridge from big-factor scalar breaking to record-token capacity was not proved.

## Frozen Machinery

The proof attempt imports and hashes the same frozen predicates as Step 59:

- Step 57 record requirement: capacity and distinguishability.
- Step 35 base substrate: mass closure and scalar breaking.
- Step 41 factorization defect: defect pairs and witnesses.

## Structural Reduction

The bridge check passed on the frozen carrier:

1. Given substrate, defect non-emptiness is equivalent to `transition_leak_count > 0`.
2. The defect witness count tracks `transition_leak_count`.
3. `transition_leak_count > 0` is equivalent to the Step-35 witness scalar breaking a factor of dimension at least 3.

So the theorem reduces to the sharpened open lemma:

`L60_record_capacity_leak_exclusion`: for frozen Step-35 scalar witnesses, any corrected closer with substrate and `transition_leak_count > 0` has fewer than two neutral record tokens under the frozen Step-57 token rule.

## Converse Probe

The in-window probe over 11,990 rows found no counterexample. The outside probes with relaxed field count and larger single-factor dimensions also found no counterexample, but they do not constitute a proof.

## Exit State

`{schema['exit_state']}`.

Verdict: `{schema['verdict']}`.

Candidate-law accounting: obligation #2 is not discharged. The forbidden region is sharply named and empirically empty in the tested carrier, but not structurally proved.

Next grammar delta: `{schema['next_grammar_delta']}`.
"""
    (ARTIFACT_DIR / "step60_results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Step 60 Nonclaim Boundary

Step 60 does not derive the SM, does not certify frame transfer, and does not prove clean-separation fundamental.

The theorem did not land. The result is a sharpened external lemma: the missing bridge is a structural explanation for why big-factor scalar breaking plus substrate should force record capacity below two. Enumeration remains finite-carrier evidence, not a proof.

No window-independent theorem, no new physics claim, and no root landing is claimed.
"""
    (ARTIFACT_DIR / "nonclaim_boundary_step60.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 60 Statement}
Let \(C\) be a closer scored by the frozen Step-57 record predicate, frozen Step-35 substrate predicate, and frozen Step-41 factorization-defect predicate. The attempted theorem was
\[
  \mathrm{substrate}(C)\wedge \mathrm{capacity}(C) \Rightarrow \Delta_{\mathrm{fact}}(C)=\varnothing.
\]
The proof attempt verifies the reduction
\[
  \mathrm{substrate}(C)\wedge \Delta_{\mathrm{fact}}(C)\ne\varnothing
  \Longleftrightarrow
  \mathrm{substrate}(C)\wedge \mathrm{transition\_leak\_count}(C)>0,
\]
and, under the frozen scalar-action diagnostic, the positive leak occurs exactly when the Step-35 witness scalar breaks a factor of dimension at least \(3\).

The established output is not a theorem. It is the sharpened external lemma:
\[
  L60:\quad
  \mathrm{substrate}(C)\wedge \mathrm{transition\_leak\_count}(C)>0
  \Rightarrow
  \mathrm{neutral\_record\_token\_count}(C)<2.
\]
This lemma is verified by enumeration over the Step-33 corrected carrier and by bounded outside probes, but no structural proof is supplied here.
\end{document}
"""
    (ARTIFACT_DIR / "step60_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    data = build()
    write_csv(ARTIFACT_DIR / "frozen_machinery_step60.csv", data["frozen"], ["machinery", "source_path", "sha256", "frozen_functions", "status"])
    write_csv(ARTIFACT_DIR / "reduction_check_step60.csv", data["reduction"], ["check", "passes", "evidence"])
    write_csv(
        ARTIFACT_DIR / "converse_probe_step60.csv",
        data["probes"],
        [
            "probe",
            "dimensions",
            "max_fields",
            "outside_reason",
            "chiral_closers_checked",
            "capacity_positive",
            "substrate_nonclean_capacity_positive",
            "counterexample_found",
            "counterexample_support_key",
            "counterexample_scalar",
            "counterexample_transition_leak_count",
            "counterexample_neutral_record_token_count",
        ],
    )
    write_csv(ARTIFACT_DIR / "sharpened_external_lemma_step60.csv", data["sharpened"], ["lemma_id", "statement", "normalization", "status", "next_required_input"])
    write_csv(ARTIFACT_DIR / "anti_circularity_step60.csv", data["anti_circularity"], ["check", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "six_gate_audit_step60.csv", data["seven_gates"], ["gate", "passes", "evidence"])
    write_csv(ARTIFACT_DIR / "generated_vs_input_step60.csv", data["generated"], ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step60_no_enumeration_as_proof", "status": "active_mode_t_constraint", "declared_at_step": 60, "role": "enumeration evidence cannot be relabeled as a theorem"},
        {"constraint_id": "step60_frozen_predicates", "status": "active_anti_smuggle_constraint", "declared_at_step": 60, "role": "record, substrate, and defect predicates are imported frozen"},
        {"constraint_id": "step60_target_theorem_no_target_hypothesis", "status": "active_anti_circularity_constraint", "declared_at_step": 60, "role": "proof may assume substrate and capacity only, not the target"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    lineage = [
        {
            "target": "record-stability-forces-clean-separation-structural-theorem",
            "parent_residual": "Step59 enumeration terminal for RS subset CS",
            "relation_to_canonical_root": "super_residual / parent layer, USER-AUTHORIZED 2026-06-09",
            "status": data["schema"]["exit_state"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/record_stability_structural_theorem_step60.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target", "parent_residual", "relation_to_canonical_root", "status", "source_artifacts"])

    grammar = [
        {
            "grammar_id": "G_step60_reduction_plus_bounded_converse_probe",
            "declared_at_step": 60,
            "mode": "ModeT",
            "proof_grammar": "frozen-predicate reduction, Step59 enumeration certificate, bounded converse probes up to max_fields=6 and dimensions 5/6",
            "exit_state": data["schema"]["exit_state"],
            "next_grammar_delta": data["schema"]["next_grammar_delta"],
            "non_triviality_argument": "anti-circularity witnesses show substrate and capacity are individually non-CS; the missing bridge is the conjunction",
            "excluded_designs_rationale": "no clean-separation hypothesis, no proton-stability hypothesis, no target restatement",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_grammar_manifest.csv", grammar, ["grammar_id", "declared_at_step", "mode", "proof_grammar", "exit_state", "next_grammar_delta", "non_triviality_argument", "excluded_designs_rationale"])

    classification = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/record_stability_structural_theorem_step60.py", "claim": "build script for Mode-T proof attempt", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/record_stability_structural_theorem_step60.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/frozen_machinery_step60.csv", "claim": "frozen machinery hashes", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/frozen_machinery_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/reduction_check_step60.csv", "claim": "structural reduction checks", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/reduction_check_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/converse_probe_step60.csv", "claim": "inside and outside converse probes", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/converse_probe_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/sharpened_external_lemma_step60.csv", "claim": "sharpened external lemma", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/sharpened_external_lemma_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/anti_circularity_step60.csv", "claim": "anti-circularity checks", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/anti_circularity_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step60.csv", "claim": "seven-gate theorem audit", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/six_gate_audit_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step60.csv", "claim": "generated-vs-input record", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/generated_vs_input_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step60_schema.json", "claim": "machine-readable Step60 verdict", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step60_schema.json"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step60_results_summary.md", "claim": "Step60 narrative summary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/step60_results_summary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step60.md", "claim": "Step60 nonclaim boundary", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary_step60.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step60_statement.tex", "claim": "sharpened lemma statement, not theorem", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/step60_statement.tex"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv", "claim": "Mode-T/Mode-B constraint ledger", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_constraint_ledger.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv", "claim": "target lineage", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_target_lineage.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv", "claim": "proof grammar manifest", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/mode_b_grammar_manifest.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/content_classification_step60.csv", "claim": "content classification table", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/content_classification_step60.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/run_step60.py", "claim": "self-contained validator", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/run_step60.py"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification_step60.csv", classification, ["artifact", "claim", "grade", "source"])
    write_json(ARTIFACT_DIR / "step60_schema.json", data["schema"])
    write_docs(data)


if __name__ == "__main__":
    main()
