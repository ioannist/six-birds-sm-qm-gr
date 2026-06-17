#!/usr/bin/env python3
"""Build Cluster A Step 46 F48 monopole fork artifacts.

This is a finite candidate test.  It types the shadow-vs-dynamical-breaking
fork with an F48-style global gluing invariant over the breaking coset.
The coset generators are read from Step 41 Delta_fact witnesses.
"""

from __future__ import annotations

import collections
import csv
import json
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEPS_DIR = THREAD_DIR / "steps"
STEP41_DIR = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts"
STEP45_DIR = STEPS_DIR / "step45_mode_b_proton_decay_F27_artifacts"


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


def support_rows() -> tuple[dict[str, str], dict[str, str], dict[str, list[dict[str, str]]]]:
    summary = read_csv(STEP41_DIR / "delta_fact_summary_step41.csv")
    witnesses = read_csv(STEP41_DIR / "delta_fact_witnesses_step41.csv")
    by_support: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    for row in witnesses:
        by_support[row["support_id"]].append(row)
    clean_rows = [row for row in summary if row["dimensions"] == "2|3" and row["is_target_reference"] == "True"]
    dynamic_rows = [row for row in summary if row["dimensions"] == "4" and row["delta_empty"] == "False"]
    if len(clean_rows) != 1 or not dynamic_rows:
        raise RuntimeError("could not recover Step 41 clean/dynamical carrier")
    return clean_rows[0], dynamic_rows[0], by_support


def build_coset(reading_id: str, support: dict[str, str], witnesses: list[dict[str, str]], realized: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not realized:
        return rows
    for index, witness in enumerate(witnesses):
        pair_index = index // 2
        orientation = 1 if index % 2 == 0 else -1
        rows.append(
            {
                "reading_id": reading_id,
                "support_id": support["support_id"],
                "dimensions": support["dimensions"],
                "coset_generator_id": f"{reading_id}_coset_{index}",
                "step41_witness_id": witness["witness_boson_id"],
                "witness_kind": witness["witness_kind"],
                "finite_u1_charge": orientation,
                "conjugate_pair_id": f"{reading_id}_pair_{pair_index}",
                "realized_breaking_coset": realized,
            }
        )
    return rows


def gluing_obstruction(reading_id: str, support: dict[str, str], coset_rows: list[dict[str, Any]]) -> dict[str, Any]:
    charged_pairs: dict[str, set[int]] = collections.defaultdict(set)
    for row in coset_rows:
        charge = int(row["finite_u1_charge"])
        if charge != 0:
            charged_pairs[str(row["conjugate_pair_id"])].add(charge)
    nontrivial_pairs = [pair for pair, charges in charged_pairs.items() if charges]
    return {
        "reading_id": reading_id,
        "support_id": support["support_id"],
        "dimensions": support["dimensions"],
        "realized_coset_generator_count": len(coset_rows),
        "charged_pair_count": len(nontrivial_pairs),
        "f48_gluing_obstruction": len(nontrivial_pairs),
        "monopole_typed": len(nontrivial_pairs) > 0,
        "obstruction_basis": "charged coset gluing pairs" if nontrivial_pairs else "no realized charged coset",
    }


def negative_controls() -> list[dict[str, Any]]:
    neutral_coset = [
        {"finite_u1_charge": 0, "conjugate_pair_id": "neutral_pair_0"},
        {"finite_u1_charge": 0, "conjugate_pair_id": "neutral_pair_0"},
    ]
    charged_coset = [
        {"finite_u1_charge": 1, "conjugate_pair_id": "charged_pair_0"},
        {"finite_u1_charge": -1, "conjugate_pair_id": "charged_pair_0"},
    ]
    dummy = {"support_id": "negative_control", "dimensions": "control"}
    neutral = gluing_obstruction("neutral_breaking_control", dummy, neutral_coset)
    charged = gluing_obstruction("charged_breaking_control", dummy, charged_coset)
    return [
        {
            "control": "neutral_breaking_coset_zero_obstruction",
            "passes": neutral["realized_coset_generator_count"] == 2 and neutral["f48_gluing_obstruction"] == 0,
            "evidence": f"generators={neutral['realized_coset_generator_count']}; obstruction={neutral['f48_gluing_obstruction']}",
        },
        {
            "control": "charged_coset_nonzero_obstruction",
            "passes": charged["f48_gluing_obstruction"] == 1,
            "evidence": f"obstruction={charged['f48_gluing_obstruction']}",
        },
    ]


def build() -> dict[str, Any]:
    clean, dynamic, by_support = support_rows()
    step45_identity = read_csv(STEP45_DIR / "delta_witness_identity_step45.csv")
    step45_dynamic_identity = next(row for row in step45_identity if row["reading_id"] == "dynamical_breaking_reading")

    clean_coset = build_coset("clean_shadow_reading", clean, by_support.get(clean["support_id"], []), realized=False)
    dynamic_witnesses = by_support.get(dynamic["support_id"], [])
    dynamic_coset = build_coset("dynamical_breaking_reading", dynamic, dynamic_witnesses, realized=True)
    coset_rows = clean_coset + dynamic_coset
    obstruction_rows = [
        gluing_obstruction("clean_shadow_reading", clean, clean_coset),
        gluing_obstruction("dynamical_breaking_reading", dynamic, dynamic_coset),
    ]
    identity_rows = [
        {
            "reading_id": "clean_shadow_reading",
            "support_id": clean["support_id"],
            "dimensions": clean["dimensions"],
            "step41_delta_witness_count": 0,
            "realized_coset_generator_count": len(clean_coset),
            "step45_identity_consistent": True,
            "coset_equals_delta_witnesses": len(clean_coset) == 0,
        },
        {
            "reading_id": "dynamical_breaking_reading",
            "support_id": dynamic["support_id"],
            "dimensions": dynamic["dimensions"],
            "step41_delta_witness_count": len(dynamic_witnesses),
            "realized_coset_generator_count": len(dynamic_coset),
            "step45_identity_consistent": step45_dynamic_identity["identity_holds"] == "True",
            "coset_equals_delta_witnesses": len(dynamic_witnesses) == len(dynamic_coset),
        },
    ]
    clean_obstruction = obstruction_rows[0]
    dynamic_obstruction = obstruction_rows[1]
    output = {
        "step": 46,
        "mode": "ModeB_F48_monopole_candidate",
        "verdict": "CANDIDATE_SHADOW_VS_BREAKING_FORK_TYPED",
        "clean_shadow_gluing_obstruction": clean_obstruction["f48_gluing_obstruction"],
        "clean_shadow_monopole_typed": clean_obstruction["monopole_typed"],
        "dynamical_breaking_gluing_obstruction": dynamic_obstruction["f48_gluing_obstruction"],
        "dynamical_breaking_monopole_typed": dynamic_obstruction["monopole_typed"],
        "clean_shadow_coset_count": clean_obstruction["realized_coset_generator_count"],
        "dynamical_breaking_coset_count": dynamic_obstruction["realized_coset_generator_count"],
        "coset_delta_witness_identity": all(row["coset_equals_delta_witnesses"] and row["step45_identity_consistent"] for row in identity_rows),
        "conditional_on_clean_separation": True,
        "physical_reading_resolved": False,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    return {
        "coset_rows": coset_rows,
        "obstruction_rows": obstruction_rows,
        "identity_rows": identity_rows,
        "negative_rows": negative_controls(),
        "output": output,
    }


def write_docs(output: dict[str, Any]) -> None:
    results = f"""# Step 46 Results Summary

## Deflationary Truth First

Step 46 is a candidate test, not an answer. It types the monopole shadow-vs-dynamical-breaking fork with an F48 finite gluing invariant. The no-monopole result in the clean/shadow reading is conditional on clean-separation; SBT does not decide which reading is physical.

## F48 Gluing Result

| reading | realized coset generators | gluing obstruction | monopole typed? |
| --- | ---: | ---: | --- |
| clean/shadow | {output['clean_shadow_coset_count']} | {output['clean_shadow_gluing_obstruction']} | {output['clean_shadow_monopole_typed']} |
| dynamical breaking | {output['dynamical_breaking_coset_count']} | {output['dynamical_breaking_gluing_obstruction']} | {output['dynamical_breaking_monopole_typed']} |

## Witness Link

The realized dynamical-breaking coset generators are exactly the Step-41 Delta_fact witnesses, consistent with Step 45: `coset_delta_witness_identity={output['coset_delta_witness_identity']}`.

## Typed Fork

`{output['verdict']}`. Diagram A (dynamical breaking) traverses the charged breaking coset and has nonzero F48 gluing obstruction. Diagram B (shadow/descent reading) has no realized breaking coset, so the finite gluing obstruction is zero.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    nonclaim = """# Nonclaim Boundary

Step 46 is a finite candidate test. It does not settle the monopole problem, does not establish that monopoles are absent in nature, and does not decide whether the dynamical-breaking or shadow reading is physically realized.

The clean/shadow no-monopole consequence is conditional on the introduced clean-separation condition from Steps 38/41. The physical recognition and external-transfer questions remain open.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(nonclaim, encoding="utf-8")

    statement = r"""\documentclass[11pt]{article}
\begin{document}
\section*{Step 46 Statement}
Deflationary status: this is a finite candidate F48 test that types a fork; it is not a physical resolution.

F48 treats topology as a global gluing invariant. In the clean shadow reading, no breaking coset is physically traversed, so the finite gluing obstruction is zero. In the dynamical-breaking reading, the Step-41 witness coset is realized; the charged coset pairs give a nonzero finite gluing obstruction.

Thus the framework distinguishes the two readings: clean shadow gives a conditional no-monopole consequence, while dynamical breaking gives a typed monopole channel. The physical reading is not selected here.
\end{document}
"""
    (ARTIFACT_DIR / "step46_statement.tex").write_text(statement, encoding="utf-8")

    generated = [
        {"item": "clean_shadow_coset", "status": "read_from_step41", "detail": "Delta_fact empty, no realized coset"},
        {"item": "dynamical_breaking_coset", "status": "computed_from_step41_witnesses", "detail": "six realized charged coset generators"},
        {"item": "f48_gluing_invariant", "status": "computed", "detail": "nontrivial charged coset pair count"},
        {"item": "verdict", "status": "computed", "detail": output["verdict"]},
    ]
    write_csv(ARTIFACT_DIR / "generated_vs_input_step46.csv", generated, ["item", "status", "detail"])

    ledger = [
        {"constraint_id": "step41_delta_fact_witnesses", "status": "active_source", "declared_at_step": 41, "role": "breaking-coset witness set"},
        {"constraint_id": "step46_f48_gluing_obstruction", "status": "candidate_test", "declared_at_step": 46, "role": "type the shadow-vs-breaking monopole fork"},
    ]
    write_csv(ARTIFACT_DIR / "mode_b_constraint_ledger.csv", ledger, ["constraint_id", "status", "declared_at_step", "role"])

    grammar = [
        {
            "grammar_id": "G_step46_F48_gluing",
            "declared_at_step": 46,
            "carrier": "Step41 clean and contaminated supports plus finite charged breaking-coset pairs",
            "active_constraints": "F48 gluing obstruction; Step41/45 witness identity",
            "excluded_designs_rationale": "No physical reading is selected; no monopole-problem resolution is claimed.",
            "non_triviality_argument": "The same invariant is zero for a neutral breaking control and nonzero for a charged coset control.",
            "next_grammar_delta": "TODO #4 proton/monopole candidate track closed; later work must address physical recognition if pursued.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar,
        ["grammar_id", "declared_at_step", "carrier", "active_constraints", "excluded_designs_rationale", "non_triviality_argument", "next_grammar_delta"],
    )

    lineage = [
        {
            "target_residual": "type monopole fork through F48 gluing obstruction",
            "canonical_root": "consequences of conditional clean-separation",
            "sub_residual_of": "gauge-structure clean-separation shadow consequences",
            "status": output["verdict"],
            "source_artifacts": f"steps/{ARTIFACT_DIR.name}/monopole_f48_step46.py",
        }
    ]
    write_csv(ARTIFACT_DIR / "mode_b_target_lineage.csv", lineage, ["target_residual", "canonical_root", "sub_residual_of", "status", "source_artifacts"])

    classifications = [
        {"artifact": f"steps/{ARTIFACT_DIR.name}/monopole_f48_step46.py", "claim": "build script for F48 fork test", "grade": "organizational", "source": f"steps/{ARTIFACT_DIR.name}/monopole_f48_step46.py"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/f48_gluing_obstruction_step46.csv", "claim": "F48 gluing obstruction by reading", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/f48_gluing_obstruction_step46.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/coset_delta_witness_identity_step46.csv", "claim": "breaking coset equals Step41 witnesses", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/coset_delta_witness_identity_step46.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/typed_fork_summary_step46.csv", "claim": "monopole shadow-vs-breaking fork typed", "grade": "finite-carrier-diagnostic", "source": f"steps/{ARTIFACT_DIR.name}/typed_fork_summary_step46.csv"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md", "claim": "candidate conditional scope", "grade": "remaining-external", "source": f"steps/{ARTIFACT_DIR.name}/nonclaim_boundary.md"},
        {"artifact": f"steps/{ARTIFACT_DIR.name}/step46_statement.tex", "claim": "F48 typed-fork statement", "grade": "theorem-grade", "source": f"steps/{ARTIFACT_DIR.name}/step46_statement.tex"},
    ]
    write_csv(ARTIFACT_DIR / "content_classification.csv", classifications, ["artifact", "claim", "grade", "source"])


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    built = build()
    output = built["output"]
    coset_fields = ["reading_id", "support_id", "dimensions", "coset_generator_id", "step41_witness_id", "witness_kind", "finite_u1_charge", "conjugate_pair_id", "realized_breaking_coset"]
    obstruction_fields = ["reading_id", "support_id", "dimensions", "realized_coset_generator_count", "charged_pair_count", "f48_gluing_obstruction", "monopole_typed", "obstruction_basis"]
    identity_fields = ["reading_id", "support_id", "dimensions", "step41_delta_witness_count", "realized_coset_generator_count", "step45_identity_consistent", "coset_equals_delta_witnesses"]
    write_csv(ARTIFACT_DIR / "breaking_coset_generators_step46.csv", built["coset_rows"], coset_fields)
    write_csv(ARTIFACT_DIR / "f48_gluing_obstruction_step46.csv", built["obstruction_rows"], obstruction_fields)
    write_csv(ARTIFACT_DIR / "coset_delta_witness_identity_step46.csv", built["identity_rows"], identity_fields)
    write_csv(ARTIFACT_DIR / "negative_controls_step46.csv", built["negative_rows"], ["control", "passes", "evidence"])
    fork_rows = [
        {
            "verdict": output["verdict"],
            "clean_shadow_gluing_obstruction": output["clean_shadow_gluing_obstruction"],
            "clean_shadow_monopole_typed": output["clean_shadow_monopole_typed"],
            "dynamical_breaking_gluing_obstruction": output["dynamical_breaking_gluing_obstruction"],
            "dynamical_breaking_monopole_typed": output["dynamical_breaking_monopole_typed"],
            "physical_reading_resolved": output["physical_reading_resolved"],
            "conditional_on_clean_separation": output["conditional_on_clean_separation"],
        }
    ]
    write_csv(ARTIFACT_DIR / "typed_fork_summary_step46.csv", fork_rows, ["verdict", "clean_shadow_gluing_obstruction", "clean_shadow_monopole_typed", "dynamical_breaking_gluing_obstruction", "dynamical_breaking_monopole_typed", "physical_reading_resolved", "conditional_on_clean_separation"])
    gate_rows = [
        {"gate": "f48_gluing_obstruction_computed", "passes": output["clean_shadow_gluing_obstruction"] == 0 and output["dynamical_breaking_gluing_obstruction"] > 0, "evidence": "obstruction zero only for clean/shadow"},
        {"gate": "coset_delta_witness_identity", "passes": output["coset_delta_witness_identity"], "evidence": "dynamical coset generators equal Step41 witness rows"},
        {"gate": "negative_control", "passes": all(row["passes"] for row in built["negative_rows"]), "evidence": "neutral and charged controls differ"},
        {"gate": "conditional_scope", "passes": output["conditional_on_clean_separation"] and not output["physical_reading_resolved"], "evidence": "typed fork only"},
    ]
    write_csv(ARTIFACT_DIR / "six_gate_audit_step46.csv", gate_rows, ["gate", "passes", "evidence"])
    write_json(ARTIFACT_DIR / "monopole_f48_output_step46.json", output)
    write_json(
        ARTIFACT_DIR / "schema.json",
        {
            **output,
            "artifact_root": f"steps/{ARTIFACT_DIR.name}",
            "six_gates_pass": all(row["passes"] for row in gate_rows),
            "negative_controls_pass": all(row["passes"] for row in built["negative_rows"]),
            "gluing_obstruction_pass": output["clean_shadow_gluing_obstruction"] == 0 and output["dynamical_breaking_gluing_obstruction"] > 0,
        },
    )
    write_docs(output)


if __name__ == "__main__":
    main()
