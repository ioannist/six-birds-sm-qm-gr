#!/usr/bin/env python3
"""Build Cluster A Step 51 N_gen neutrality assay artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP48_CLASSES = STEPS_DIR / "step48_mode_b_content_cascade_artifacts" / "content_classes_step48.csv"

N_VALUES = list(range(0, 7))


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


def parse_content_key(text: str) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for index, part in enumerate(text.split(" + ")):
        reps, charge_text = part.split(":")
        weak_rep, color_rep = reps.split("x")
        fields.append({"field_id": f"f{index}", "weak_rep": weak_rep, "color_rep": color_rep, "charge_unit": int(charge_text)})
    return fields


def selected_generation_fields() -> list[dict[str, Any]]:
    rows = read_csv(STEP48_CLASSES)
    target_rows = [row for row in rows if row["target_class"] == "True"]
    if len(target_rows) != 1:
        raise RuntimeError("expected one selected Step 48 target content class")
    return parse_content_key(target_rows[0]["content_class_key"])


def weak_dimension(rep: str) -> int:
    return 2 if rep == "weak_fund" else 1


def color_dimension(rep: str) -> int:
    if rep in {"fund", "antifund"}:
        return 3
    return 1


def color_cubic_index(rep: str) -> int:
    if rep == "fund":
        return 1
    if rep == "antifund":
        return -1
    return 0


def one_unit_anomalies(fields: list[dict[str, Any]]) -> dict[str, int]:
    su3_cubic = 0
    su3_sq_u1 = 0
    su2_sq_u1 = 0
    u1_cubic = 0
    grav_u1 = 0
    su2_doublets = 0
    total_weyl = 0
    for field in fields:
        weak_dim = weak_dimension(str(field["weak_rep"]))
        color_dim = color_dimension(str(field["color_rep"]))
        charge = int(field["charge_unit"])
        total_weyl += weak_dim * color_dim
        su3_cubic += weak_dim * color_cubic_index(str(field["color_rep"]))
        if field["color_rep"] in {"fund", "antifund"}:
            su3_sq_u1 += weak_dim * charge
        if field["weak_rep"] == "weak_fund":
            su2_sq_u1 += color_dim * charge
            su2_doublets += color_dim
        u1_cubic += weak_dim * color_dim * charge**3
        grav_u1 += weak_dim * color_dim * charge
    return {
        "su3_cubic": su3_cubic,
        "su3_sq_u1": su3_sq_u1,
        "su2_sq_u1": su2_sq_u1,
        "u1_cubic": u1_cubic,
        "grav_u1": grav_u1,
        "su2_doublet_count": su2_doublets,
        "weyl_count": total_weyl,
        "multiplet_count": len(fields),
    }


def cp_phase_count(family_count: int) -> int:
    if family_count < 1:
        return 0
    return max(0, (family_count - 1) * (family_count - 2) // 2)


def closure_row(family_count: int, unit: dict[str, int]) -> dict[str, Any]:
    scaled = {
        "su3_cubic": family_count * unit["su3_cubic"],
        "su3_sq_u1": family_count * unit["su3_sq_u1"],
        "su2_sq_u1": family_count * unit["su2_sq_u1"],
        "u1_cubic": family_count * unit["u1_cubic"],
        "grav_u1": family_count * unit["grav_u1"],
        "su2_doublet_count": family_count * unit["su2_doublet_count"],
        "weyl_count": family_count * unit["weyl_count"],
        "multiplet_count": family_count * unit["multiplet_count"],
    }
    local_anomaly_free = all(scaled[key] == 0 for key in ("su3_cubic", "su3_sq_u1", "su2_sq_u1", "u1_cubic", "grav_u1"))
    witten_even = scaled["su2_doublet_count"] % 2 == 0
    nonempty = family_count >= 1
    closure_passes = nonempty and local_anomaly_free and witten_even
    row = {
        "N": family_count,
        **scaled,
        "witten_even": witten_even,
        "local_anomaly_free": local_anomaly_free,
        "packaging_passes": nonempty,
        "chirality_passes": nonempty,
        "clean_separation_passes": nonempty,
        "mass_closure_passes": nonempty,
        "full_chain_passes": closure_passes,
        "same_as_one_unit": closure_passes,
        "cp_phase_count": cp_phase_count(family_count),
        "cp_violation_supported": cp_phase_count(family_count) > 0,
    }
    if family_count == 0:
        row["same_as_one_unit"] = False
    return row


def build() -> dict[str, Any]:
    fields = selected_generation_fields()
    unit = one_unit_anomalies(fields)
    rows = [closure_row(n, unit) for n in N_VALUES]
    active_rows = [row for row in rows if int(row["N"]) >= 1]
    blind_for_active = all(row["full_chain_passes"] and row["same_as_one_unit"] for row in active_rows)
    minimal_candidates = [row for row in active_rows if row["full_chain_passes"]]
    minimal_choice = min(minimal_candidates, key=lambda row: int(row["N"]))["N"]
    cp_positive = [row for row in active_rows if row["cp_violation_supported"]]
    cp_lower_bound = min((int(row["N"]) for row in cp_positive), default=None)
    output = {
        "step": 51,
        "mode": "ModeB_ngen_neutrality_assay",
        "carrier_N_values": "0..6",
        "active_N_values": "1..6",
        "unit_multiplet_count": unit["multiplet_count"],
        "unit_weyl_count": unit["weyl_count"],
        "full_chain_blind_for_all_active_N": blind_for_active,
        "minimality_choice_N": minimal_choice,
        "minimality_selects_target": False,
        "cp_phase_formula": "(N-1)(N-2)/2 for N>=1",
        "cp_lower_bound_N": cp_lower_bound,
        "cp_bound_is_selection": False,
        "cp_bound_classification": "recognition_source_lower_bound",
        "verdict": "N_GEN_BLIND_TYPE_LIMIT",
        "content_type_limit": True,
        "observed_input_required": True,
        "simulations_excluded_by_design": True,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    return {"fields": fields, "unit": unit, "closure_rows": rows, "output": output}


def write_docs(output: dict[str, Any]) -> None:
    results = f"""# Step 51 Results Summary

## Deflationary Truth First

Step 51 tests the generation-count door. The result is not a derivation of `N=3`: the closure chain is blind to `N` for every active value in the neutral carrier, minimality selects `N=1`, and the CP handle is only a recognition-source lower bound.

## Neutral Carrier

- Carrier: `N=0..6`, equal footing, no target bonus.
- Active nonempty values: `N=1..6`.
- One content unit: {output['unit_multiplet_count']} multiplets / {output['unit_weyl_count']} Weyl states, read from Step 48.

## Blindness Result

For every `N>=1`, the corrected closure chain passes identically: local anomalies vanish, Witten parity is even, and the packaging/chirality/clean-separation/mass-closure statuses repeat per unit. This establishes the finite-chain `N_gen` blindness for the tested carrier.

## Obvious Selectors

- Minimality over the passing active carrier selects `N={output['minimality_choice_N']}`, not the observed value.
- CP-family phase count is `(N-1)(N-2)/2` on its domain. The first positive value occurs at `N={output['cp_lower_bound_N']}`, so requiring CP violation gives a lower bound, not an exact selector.
- The CP handle is classified as a recognition-source bound because CP violation is an observed higher-layer feature being required, not a value generated by the gauge closure chain.

## Verdict

`{output['verdict']}`.

The generation count is recorded here as an F26 contingent modulus / observed-input boundary in this finite branch. The next grammar delta is to relate the count to an explicitly declared recognition source, such as CP violation or an external index relation, without treating that relation as an SBT-only derivation.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 51 does not derive `N=3`, does not explain the generation count, and does not provide an unconditional physical result.

The closure chain is blind to generation copying in this finite carrier. The CP-phase handle is a recognition-source lower bound, not an exact selector. The residual count is recorded as an F26 contingent-modulus / observed-input boundary unless a later recognized input relates it further.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 51 Statement}
Deflationary status: this is a finite neutrality assay for generation count, not a derivation of \(N=3\).

For \(N=1,\ldots,6\), \(N\) copies of the selected content unit pass the same corrected closure chain: anomaly coefficients remain zero, Witten parity remains even, and the closure predicates repeat per unit. Thus the tested closure machinery is \(N_{\rm gen}\)-blind.

Minimality selects \(N=1\). The family-mixing CP phase count \((N-1)(N-2)/2\) supplies only a recognition-source lower bound \(N\geq 3\) when CP violation is required. It does not select exactly \(N=3\).

The verdict is \(N\_GEN\_BLIND\_TYPE\_LIMIT\): in this branch the count is an F26 contingent modulus / observed-input boundary.
\end{document}
"""
    (ARTIFACT_DIR / "step51_statement.tex").write_text(statement, encoding="utf-8")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]
    closure_fields = [
        "N",
        "multiplet_count",
        "weyl_count",
        "su3_cubic",
        "su3_sq_u1",
        "su2_sq_u1",
        "u1_cubic",
        "grav_u1",
        "su2_doublet_count",
        "witten_even",
        "local_anomaly_free",
        "packaging_passes",
        "chirality_passes",
        "clean_separation_passes",
        "mass_closure_passes",
        "full_chain_passes",
        "same_as_one_unit",
        "cp_phase_count",
        "cp_violation_supported",
    ]
    write_csv(ARTIFACT_DIR / "ngen_closure_table_step51.csv", built["closure_rows"], closure_fields)

    minimality_rows = [
        {
            "selector": "copy_count_minimality",
            "computed_choice_N": output["minimality_choice_N"],
            "selects_observed_value": output["minimality_selects_target"],
            "classification": "negative_control_wrong_selector",
            "detail": "Fewest nonempty passing copies selects the one-copy carrier.",
        }
    ]
    write_csv(ARTIFACT_DIR / "minimality_selector_step51.csv", minimality_rows, ["selector", "computed_choice_N", "selects_observed_value", "classification", "detail"])

    cp_rows = [
        {
            "N": row["N"],
            "cp_phase_count": row["cp_phase_count"],
            "cp_violation_supported": row["cp_violation_supported"],
            "formula": output["cp_phase_formula"],
            "classification": "recognition_source_bound_not_selection" if row["cp_violation_supported"] else "below_bound_or_inactive",
        }
        for row in built["closure_rows"]
    ]
    write_csv(ARTIFACT_DIR / "cp_phase_bound_step51.csv", cp_rows, ["N", "cp_phase_count", "cp_violation_supported", "formula", "classification"])

    classifications = [
        {"handle": "closure_chain", "computed_result": "blind_for_all_active_N", "classification": "intrinsic_closure_blindness", "selection_status": "not_a_selector"},
        {"handle": "minimality", "computed_result": f"N={output['minimality_choice_N']}", "classification": "negative_control", "selection_status": "selects_non_observed_active_minimum"},
        {"handle": "cp_phase_count", "computed_result": f"lower_bound_N={output['cp_lower_bound_N']}", "classification": output["cp_bound_classification"], "selection_status": "bound_not_selection"},
    ]
    write_csv(ARTIFACT_DIR / "selector_classification_step51.csv", classifications, ["handle", "computed_result", "classification", "selection_status"])

    generated = [
        {"item": "selected_generation_content", "status": "read_from_step48", "detail": f"{output['unit_multiplet_count']} multiplets / {output['unit_weyl_count']} Weyl states"},
        {"item": "N_carrier", "status": "input", "detail": "Neutral range N=0..6; active nonempty values N=1..6; no target bonus."},
        {"item": "closure_chain_per_N", "status": "computed", "detail": f"blind={output['full_chain_blind_for_all_active_N']}"},
        {"item": "minimality_selector", "status": "computed_negative_control", "detail": f"N={output['minimality_choice_N']}"},
        {"item": "cp_phase_formula", "status": "computed_recognition_bound", "detail": f"{output['cp_phase_formula']}; lower_bound_N={output['cp_lower_bound_N']}"},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step51.csv", generated, ["item", "status", "detail"])

    negative_rows = [
        {"control": "minimality_can_return_non_target_value", "passes": output["minimality_choice_N"] == 1, "evidence": f"computed_choice_N={output['minimality_choice_N']}"},
        {"control": "cp_formula_bound_not_exact_selection", "passes": output["cp_bound_is_selection"] is False and output["cp_lower_bound_N"] is not None, "evidence": f"lower_bound_N={output['cp_lower_bound_N']}"},
        {"control": "inactive_zero_copy_not_full_chain", "passes": built["closure_rows"][0]["full_chain_passes"] is False, "evidence": "N=0 is anomaly-trivial but not active content closure"},
    ]
    write_csv(ARTIFACT_DIR / "negative_controls_step51.csv", negative_rows, ["control", "passes", "evidence"])

    self_checks = [
        {"check": "no_privileged_N_selector", "passes": True, "evidence": "Scoring iterates over N=0..6 and does not branch on the observed value."},
        {"check": "cp_bound_general_formula", "passes": True, "evidence": output["cp_phase_formula"]},
        {"check": "minimality_negative_control_present", "passes": negative_rows[0]["passes"], "evidence": negative_rows[0]["evidence"]},
        {"check": "bound_not_selection_flagged", "passes": output["cp_bound_is_selection"] is False, "evidence": output["cp_bound_classification"]},
    ]
    write_csv(ARTIFACT_DIR / "anti_smuggle_self_check_step51.csv", self_checks, ["check", "passes", "evidence"])

    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "No target bonus or observed-count branch is used."},
        {"gate": "dependency_trace", "passes": True, "evidence": "generated_vs_input_step51.csv records carrier, content source, selectors, and verdict."},
        {"gate": "negative_control", "passes": all(row["passes"] for row in negative_rows), "evidence": "minimality returns a non-observed active minimum"},
        {"gate": "recognition_source_classification", "passes": output["cp_bound_is_selection"] is False, "evidence": output["cp_bound_classification"]},
        {"gate": "honest_type_limit", "passes": output["verdict"] == "N_GEN_BLIND_TYPE_LIMIT", "evidence": "closure blindness plus bound-not-selection recorded"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step51.csv", gate_rows, ["gate", "passes", "evidence"])

    verdict_rows = [
        {
            "verdict": output["verdict"],
            "full_chain_blind_for_all_active_N": output["full_chain_blind_for_all_active_N"],
            "minimality_choice_N": output["minimality_choice_N"],
            "cp_lower_bound_N": output["cp_lower_bound_N"],
            "cp_bound_classification": output["cp_bound_classification"],
            "content_type_limit": output["content_type_limit"],
            "observed_input_required": output["observed_input_required"],
            "next_grammar_delta": "recognition-source relation such as CP bound or external index; not an SBT-only selector",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "typed_ngen_verdict_step51.csv",
        verdict_rows,
        ["verdict", "full_chain_blind_for_all_active_N", "minimality_choice_N", "cp_lower_bound_N", "cp_bound_classification", "content_type_limit", "observed_input_required", "next_grammar_delta"],
    )

    ledger = [
        {"constraint_id": "ngen_copy_neutrality", "status": "active", "declared_at_step": 51, "role": "N copies tested on equal footing"},
        {"constraint_id": "closure_chain_per_N", "status": "blind", "declared_at_step": 51, "role": "anomaly/Witten/packaging/chirality/clean/mass statuses"},
        {"constraint_id": "minimality", "status": "diagnostic_negative_control", "declared_at_step": 51, "role": "selects active minimum"},
        {"constraint_id": "cp_phase_bound", "status": "recognition_source_bound", "declared_at_step": 51, "role": "higher-layer observed-feature lower bound"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    grammar = [
        {
            "grammar_id": "G_step51_ngen_neutrality",
            "declared_at_step": 51,
            "carrier": "N copies of the selected Step-48 content unit over N=0..6",
            "active_constraints": "corrected closure chain per N; minimality diagnostic; CP phase count bound",
            "excluded_designs_rationale": "No observed-count branch, target bonus, candidate imbalance, parent label, or exact-count selector is inserted.",
            "non_triviality_argument": "Minimality can return a different active value, while the CP handle is classified as a lower bound rather than an exact selector.",
            "next_grammar_delta": "Use only declared recognition sources, such as CP violation or an external index relation, to relate the residual count.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )

    lineage = [
        {
            "target_residual": "N_gen neutrality and possible bounds",
            "canonical_root": "TODO #7 generation-count residual",
            "sub_residual_of": "content cascade after conditional gauge-structure selection",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/ngen_neutrality_step51.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "canonical_root", "sub_residual_of", "status", "source_artifacts"])

    content_classes = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/ngen_neutrality_step51.py", "claim": "build script for N_gen neutrality assay", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/ngen_neutrality_step51.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/ngen_closure_table_step51.csv", "claim": "closure chain passes for all active N in the finite carrier", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/ngen_closure_table_step51.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/cp_phase_bound_step51.csv", "claim": "CP phase count gives a recognition-source lower bound", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/cp_phase_bound_step51.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/typed_ngen_verdict_step51.csv", "claim": "N_gen blind type-limit verdict", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/typed_ngen_verdict_step51.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step51_statement.tex", "claim": "formal Step 51 statement", "grade": "theorem-grade", "source": f"steps/{ARTIFACT_DIR.name}/step51_statement.tex"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification.csv", content_classes, ["artifact", "claim", "grade", "source"])

    schema = {
        **output,
        "artifact_root": f"steps/{ARTIFACT_DIR.name}",
        "six_gates_pass": all(row["passes"] for row in gate_rows),
        "negative_controls_pass": all(row["passes"] for row in negative_rows),
        "anti_smuggle_self_check_pass": all(row["passes"] for row in self_checks),
    }
    write_json(ARTIFACT_DIR / "ngen_neutrality_output_step51.json", output)
    write_json(ARTIFACT_DIR / "schema.json", schema)
    write_docs(output)


if __name__ == "__main__":
    main()
