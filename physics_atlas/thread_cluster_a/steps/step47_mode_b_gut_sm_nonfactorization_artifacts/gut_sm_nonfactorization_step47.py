#!/usr/bin/env python3
"""Build Cluster A Step 47 GUT-SM nonfactorization artifacts.

This step decides only the descriptive StructDown question.  It compares
finite readouts of the SM interaction/generator lens and the GUT
interaction/generator lens with the Foundations III factorization defect.
It does not certify a physical emergence channel.
"""

from __future__ import annotations

import csv
import json
from itertools import combinations
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP41_DIR = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts"
STEP46_DIR = STEPS_DIR / "step46_mode_b_monopole_F48_artifacts"


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


def step41_dynamic_witnesses() -> list[dict[str, str]]:
    rows = read_csv(STEP41_DIR / "delta_fact_witnesses_step41.csv")
    selected = [row for row in rows if row["support_id"] == "support_08"]
    if len(selected) != 6:
        raise RuntimeError("expected six Step-41 witnesses for support_08")
    return selected


def build_states(witnesses: list[dict[str, str]]) -> list[dict[str, Any]]:
    states: list[dict[str, Any]] = [
        {
            "state_id": "sm_confining_subalgebra",
            "state_kind": "shared_sm_generator",
            "step41_witness_id": "",
            "pi_sm": "SM:realized_confining_generator",
            "pi_gut": "GUT:shared_sm_confining_generator",
        },
        {
            "state_id": "sm_weak_subalgebra",
            "state_kind": "shared_sm_generator",
            "step41_witness_id": "",
            "pi_sm": "SM:realized_weak_generator",
            "pi_gut": "GUT:shared_sm_weak_generator",
        },
        {
            "state_id": "sm_abelian_generator",
            "state_kind": "shared_sm_generator",
            "step41_witness_id": "",
            "pi_sm": "SM:realized_abelian_generator",
            "pi_gut": "GUT:shared_sm_abelian_generator",
        },
    ]
    for index, witness in enumerate(witnesses):
        pair_id = index // 2
        orientation = "plus" if index % 2 == 0 else "minus"
        states.append(
            {
                "state_id": f"xy_coset_{index}",
                "state_kind": "colored_coset_generator",
                "step41_witness_id": witness["witness_boson_id"],
                "pi_sm": "SM:not_realized_colored_coset",
                "pi_gut": f"GUT:colored_coset_pair_{pair_id}:{orientation}",
            }
        )
    return states


def delta_fact(states: list[dict[str, Any]], pi0: str, pi1: str, label: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for left, right in combinations(states, 2):
        if left[pi0] == right[pi0] and left[pi1] != right[pi1]:
            rows.append(
                {
                    "delta_id": f"{label}_{len(rows)}",
                    "left_state_id": left["state_id"],
                    "right_state_id": right["state_id"],
                    "shared_pi0": left[pi0],
                    "left_pi1": left[pi1],
                    "right_pi1": right[pi1],
                    "left_step41_witness_id": left["step41_witness_id"],
                    "right_step41_witness_id": right["step41_witness_id"],
                }
            )
    return rows


def witness_set_from_delta(rows: list[dict[str, Any]]) -> set[str]:
    witnesses: set[str] = set()
    for row in rows:
        for key in ("left_step41_witness_id", "right_step41_witness_id"):
            value = str(row[key])
            if value:
                witnesses.add(value)
    return witnesses


def build() -> dict[str, Any]:
    witnesses = step41_dynamic_witnesses()
    states = build_states(witnesses)
    delta_sm_to_gut = delta_fact(states, "pi_sm", "pi_gut", "sm_to_gut")
    delta_gut_to_sm = delta_fact(states, "pi_gut", "pi_sm", "gut_to_sm")
    step41_witness_ids = {row["witness_boson_id"] for row in witnesses}
    delta_witness_ids = witness_set_from_delta(delta_sm_to_gut)
    witness_identity = delta_witness_ids == step41_witness_ids and not witness_set_from_delta(delta_gut_to_sm)
    if delta_sm_to_gut and not delta_gut_to_sm:
        verdict = "GENUINE_STRUCTURAL_REFINEMENT"
    elif not delta_sm_to_gut and not delta_gut_to_sm:
        verdict = "REDUNDANT_RE_LENSING"
    elif delta_sm_to_gut and delta_gut_to_sm:
        verdict = "INCOMPARABLE"
    else:
        verdict = "SM_REFINES_GUT_DESCRIPTOR"
    step46_identity = read_csv(STEP46_DIR / "coset_delta_witness_identity_step46.csv")
    dynamic_step46 = next(row for row in step46_identity if row["reading_id"] == "dynamical_breaking_reading")
    output = {
        "step": 47,
        "mode": "ModeB_GUT_SM_nonfactorization",
        "structdown_only": True,
        "physical_reading_resolved": False,
        "topdown_channel_certified": False,
        "state_count": len(states),
        "delta_sm_to_gut_count": len(delta_sm_to_gut),
        "delta_gut_to_sm_count": len(delta_gut_to_sm),
        "structural_verdict": verdict,
        "xy_witness_identity": witness_identity,
        "step46_identity_consistent": dynamic_step46["coset_equals_delta_witnesses"] == "True",
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    return {
        "states": states,
        "delta_sm_to_gut": delta_sm_to_gut,
        "delta_gut_to_sm": delta_gut_to_sm,
        "output": output,
        "step41_witness_ids": sorted(step41_witness_ids),
        "delta_witness_ids": sorted(delta_witness_ids),
    }


def write_docs(output: dict[str, Any]) -> None:
    results = f"""# Step 47 Results Summary

## Deflationary Truth First

Step 47 decides only the descriptive StructDown question: whether the GUT interaction/generator readout is structurally redundant with the SM readout. It does not certify a physical two-stage history, does not supply a TopDownChannel, and does not resolve the physical shadow-vs-breaking fork from Steps 45-46.

## Chosen Readouts

The state space is the finite interaction/generator content of the SU(5)-style parent-shadow relation: shared SM subalgebra generators plus the colored coset generators read from Step 41. `pi_SM` records what the SM interaction lens realizes; it lumps colored coset generators as not-realized. `pi_GUT` records the GUT interaction lens; it distinguishes the colored coset generator pairs. This readout choice directly tests whether the GUT description adds generator/interaction structure over the SM lens.

## Delta Fact Results

- `Delta_fact(pi_SM, pi_GUT)` count: {output['delta_sm_to_gut_count']}
- `Delta_fact(pi_GUT, pi_SM)` count: {output['delta_gut_to_sm_count']}
- Structural verdict: `{output['structural_verdict']}`
- X/Y witness identity: `{output['xy_witness_identity']}`

## Status-Family Caveat

Structurally distinct description is not the same as a physically distinct layer. The result is `structdown_only=True`; `physical_reading_resolved=False`; `topdown_channel_certified=False`.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 47 is StructDown-only. It compares finite readouts and decides descriptive non-redundancy, not physical emergence.

It does not establish that a GUT layer is physically realized, does not close the shadow-vs-dynamical-breaking fork, and does not provide TopDownChannel evidence. The proton/monopole fork from Steps 45-46 remains physically open.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 47 Statement}
Deflationary status: this is a StructDown nonfactorization computation only.

On the finite interaction/generator state space, the SM readout \(\pi_{\rm SM}\) lumps the colored coset generators as not realized, while the GUT readout \(\pi_{\rm GUT}\) distinguishes them. Therefore \(\Delta_{\rm fact}(\pi_{\rm SM},\pi_{\rm GUT})\) is nonempty. Conversely, \(\Delta_{\rm fact}(\pi_{\rm GUT},\pi_{\rm SM})\) is empty in this finite readout choice.

The descriptive verdict is genuine structural refinement: the GUT description is not a redundant re-lensing of the SM description. This does not certify a physical layer or a top-down emergence channel.
\end{document}
"""
    (ARTIFACT_DIR / "step47_statement.tex").write_text(statement, encoding="utf-8")

    generated = [
        {"item": "state_space", "status": "constructed_from_step41", "detail": "shared SM generator states plus Step-41 colored coset witnesses"},
        {"item": "pi_sm", "status": "declared_readout", "detail": "SM interaction lens; colored coset not realized"},
        {"item": "pi_gut", "status": "declared_readout", "detail": "GUT interaction lens; colored coset generators distinguished"},
        {"item": "delta_fact_both_directions", "status": "computed", "detail": f"{output['delta_sm_to_gut_count']}|{output['delta_gut_to_sm_count']}"},
        {"item": "structural_verdict", "status": "computed", "detail": output["structural_verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step47.csv", generated, ["item", "status", "detail"])

    readouts = [
        {"readout": "pi_SM", "definition": "SM interaction/generator lens", "justification": "captures what the SM description realizes and intentionally does not resolve the parent coset"},
        {"readout": "pi_GUT", "definition": "GUT interaction/generator lens", "justification": "captures the additional colored coset generator distinctions responsible for the Step-41/45/46 witnesses"},
    ]
    write_csv(ARTIFACT_DIR / "chosen_readouts_step47.csv", readouts, ["readout", "definition", "justification"])

    ledger = [
        {"constraint_id": "step41_delta_fact_witnesses", "status": "active_source", "declared_at_step": 41, "role": "colored-coset witness set"},
        {"constraint_id": "step47_gut_sm_nonfactorization", "status": "structdown_only", "declared_at_step": 47, "role": "descriptive one-vs-two readout test"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    grammar = [
        {
            "grammar_id": "G_step47_GUT_SM_nonfactorization",
            "declared_at_step": 47,
            "carrier": "finite interaction/generator states from Step41 colored coset witnesses",
            "active_constraints": "Foundations III Delta_fact both directions",
            "excluded_designs_rationale": "No physical channel is inferred from the structural readout comparison.",
            "non_triviality_argument": "The computation can distinguish refinement, equivalence, or incomparability; it returns one directional defect.",
            "next_grammar_delta": "Physical two-stage status would need independent TopDownChannel evidence outside this finite readout comparison.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )

    lineage = [
        {
            "target_residual": "descriptive GUT-vs-SM one/two-layer question",
            "canonical_root": "status-family separation for GUT/SM readouts",
            "sub_residual_of": "physical fork remains open after Steps 45-46",
            "status": output["structural_verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/gut_sm_nonfactorization_step47.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "canonical_root", "sub_residual_of", "status", "source_artifacts"])

    classifications = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/gut_sm_nonfactorization_step47.py", "claim": "build script for GUT-SM nonfactorization", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/gut_sm_nonfactorization_step47.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/delta_fact_sm_to_gut_step47.csv", "claim": "SM readout does not determine GUT readout", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/delta_fact_sm_to_gut_step47.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/delta_fact_gut_to_sm_step47.csv", "claim": "GUT readout determines SM readout in selected finite readouts", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/delta_fact_gut_to_sm_step47.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/xy_witness_identity_step47.csv", "claim": "nonfactorization witnesses equal Step-41 X/Y coset", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/xy_witness_identity_step47.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md", "claim": "StructDown-only scope", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step47_statement.tex", "claim": "descriptive nonfactorization statement", "grade": "theorem-grade", "source": f"steps/{ARTIFACT_DIR.name}/step47_statement.tex"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification.csv", classifications, ["artifact", "claim", "grade", "source"])


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]
    state_fields = ["state_id", "state_kind", "step41_witness_id", "pi_sm", "pi_gut"]
    delta_fields = ["delta_id", "left_state_id", "right_state_id", "shared_pi0", "left_pi1", "right_pi1", "left_step41_witness_id", "right_step41_witness_id"]
    write_csv(ARTIFACT_DIR / "readout_states_step47.csv", built["states"], state_fields)
    write_csv(ARTIFACT_DIR / "delta_fact_sm_to_gut_step47.csv", built["delta_sm_to_gut"], delta_fields)
    write_csv(ARTIFACT_DIR / "delta_fact_gut_to_sm_step47.csv", built["delta_gut_to_sm"], delta_fields)
    identity_rows = [
        {
            "identity": "delta_sm_to_gut_witnesses_equal_step41_xy",
            "step41_witness_count": len(built["step41_witness_ids"]),
            "delta_witness_count": len(built["delta_witness_ids"]),
            "identity_holds": output["xy_witness_identity"],
            "step41_witness_ids": "|".join(built["step41_witness_ids"]),
            "delta_witness_ids": "|".join(built["delta_witness_ids"]),
            "step46_identity_consistent": output["step46_identity_consistent"],
        }
    ]
    write_csv(ARTIFACT_DIR / "xy_witness_identity_step47.csv", identity_rows, ["identity", "step41_witness_count", "delta_witness_count", "identity_holds", "step41_witness_ids", "delta_witness_ids", "step46_identity_consistent"])
    relationship_rows = [
        {
            "structural_verdict": output["structural_verdict"],
            "delta_sm_to_gut_count": output["delta_sm_to_gut_count"],
            "delta_gut_to_sm_count": output["delta_gut_to_sm_count"],
            "structdown_only": output["structdown_only"],
            "physical_reading_resolved": output["physical_reading_resolved"],
            "topdown_channel_certified": output["topdown_channel_certified"],
        }
    ]
    write_csv(ARTIFACT_DIR / "structural_relationship_step47.csv", relationship_rows, ["structural_verdict", "delta_sm_to_gut_count", "delta_gut_to_sm_count", "structdown_only", "physical_reading_resolved", "topdown_channel_certified"])
    negative_rows = [
        {"control": "gut_to_sm_can_be_empty", "passes": output["delta_gut_to_sm_count"] == 0, "evidence": "reverse defect is empty in the selected refinement readouts"},
        {"control": "sm_to_gut_nonempty", "passes": output["delta_sm_to_gut_count"] > 0, "evidence": f"count={output['delta_sm_to_gut_count']}"},
        {"control": "not_physical_status", "passes": output["structdown_only"] and not output["physical_reading_resolved"], "evidence": "status-family separation recorded"},
    ]
    write_csv(ARTIFACT_DIR / "negative_controls_step47.csv", negative_rows, ["control", "passes", "evidence"])
    gate_rows = [
        {"gate": "delta_fact_computed", "passes": output["delta_sm_to_gut_count"] > 0 and output["delta_gut_to_sm_count"] == 0, "evidence": "one directional nonfactorization"},
        {"gate": "witness_identity", "passes": output["xy_witness_identity"], "evidence": "Delta witnesses equal Step-41 colored coset witness set"},
        {"gate": "structdown_only", "passes": output["structdown_only"] and not output["topdown_channel_certified"], "evidence": "physical status not inferred"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_rows), "evidence": "empty reverse and nonempty forward both checked"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step47.csv", gate_rows, ["gate", "passes", "evidence"])
    write_json(ARTIFACT_DIR / "gut_sm_nonfactorization_output_step47.json", output)
    write_json(
        ARTIFACT_DIR / "schema.json",
        {
            **output,
            "artifact_root": f"steps/{ARTIFACT_DIR.name}",
            "six_gates_pass": all(row["passes"] for row in gate_rows),
            "negative_controls_pass": all(row["passes"] for row in negative_rows),
            "status_family_separation_pass": output["structdown_only"] and not output["physical_reading_resolved"] and not output["topdown_channel_certified"],
        },
    )
    write_docs(output)


if __name__ == "__main__":
    main()
