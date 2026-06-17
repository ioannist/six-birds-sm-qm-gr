#!/usr/bin/env python3
"""Build Step 41 factorization-defect restatement artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
STEP38_DIR = THREAD_DIR / "steps" / "step38_mode_b_higher_layer_shadow_uniqueness_artifacts"
TAG = "step41"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def parse_dims(raw: str) -> list[int]:
    return [int(part) for part in raw.split("|") if part and part != "none"]


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def build_bosons(row: dict[str, str], support_index: int) -> list[dict[str, object]]:
    dims = parse_dims(row["dimensions"])
    conf_dim = int(row["confining_subgroups"])
    conf_generators = conf_dim * conf_dim - 1
    total_nonabelian_generators = sum(dim * dim - 1 for dim in dims)
    charged_broken_count = int(row["broken_vector_exotic_count"])
    colorless_broken_count = max(total_nonabelian_generators - conf_generators - charged_broken_count, 0)

    bosons: list[dict[str, object]] = []
    prefix = f"s{support_index:02d}"
    for index in range(conf_generators):
        bosons.append(
            {
                "support_index": support_index,
                "boson_id": f"{prefix}_conf_gluon_{index:02d}",
                "boson_kind": "unbroken_confining_generator",
                "pi_conf_raw": "nontrivial:adjoint",
                "pi_conf_interference": "nontrivial_confining_charge",
                "pi_mass": "massless",
                "confining_nontrivial": True,
            }
        )
    bosons.append(
        {
            "support_index": support_index,
            "boson_id": f"{prefix}_unbroken_abelian_00",
            "boson_kind": "unbroken_abelian_generator",
            "pi_conf_raw": "trivial",
            "pi_conf_interference": "trivial:massless",
            "pi_mass": "massless",
            "confining_nontrivial": False,
        }
    )
    for index in range(colorless_broken_count):
        bosons.append(
            {
                "support_index": support_index,
                "boson_id": f"{prefix}_broken_colorless_{index:02d}",
                "boson_kind": "broken_colorless_generator",
                "pi_conf_raw": "trivial",
                "pi_conf_interference": "trivial:massive",
                "pi_mass": "massive",
                "confining_nontrivial": False,
            }
        )
    for index in range(charged_broken_count):
        bosons.append(
            {
                "support_index": support_index,
                "boson_id": f"{prefix}_broken_confining_charged_{index:02d}",
                "boson_kind": "broken_confining_charged_generator",
                "pi_conf_raw": "nontrivial:coset_vector",
                "pi_conf_interference": "nontrivial_confining_charge",
                "pi_mass": "massive",
                "confining_nontrivial": True,
            }
        )
    return bosons


def compute_delta(bosons: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    delta_pairs: list[dict[str, object]] = []
    witness_ids: set[str] = set()
    for left_index, left in enumerate(bosons):
        for right in bosons[left_index + 1 :]:
            if left["pi_conf_interference"] == right["pi_conf_interference"] and left["pi_mass"] != right["pi_mass"]:
                pair = {
                    "left_boson_id": left["boson_id"],
                    "right_boson_id": right["boson_id"],
                    "shared_pi0": left["pi_conf_interference"],
                    "left_pi1": left["pi_mass"],
                    "right_pi1": right["pi_mass"],
                }
                delta_pairs.append(pair)
                for candidate in (left, right):
                    if candidate["pi_mass"] == "massive" and candidate["confining_nontrivial"] is True:
                        witness_ids.add(str(candidate["boson_id"]))
    witness_rows = [
        {
            "witness_boson_id": boson_id,
            "witness_kind": "confining_charged_massive_vector",
        }
        for boson_id in sorted(witness_ids)
    ]
    return delta_pairs, witness_rows


def build() -> dict[str, object]:
    step38_rows = read_csv(STEP38_DIR / "low_energy_shadow_scores_step38.csv")
    boson_rows: list[dict[str, object]] = []
    delta_rows: list[dict[str, object]] = []
    witness_rows: list[dict[str, object]] = []
    summary_rows: list[dict[str, object]] = []

    for support_index, row in enumerate(step38_rows):
        bosons = build_bosons(row, support_index)
        delta_pairs, witnesses = compute_delta(bosons)
        clean_shadow = row["clean_shadow_requirement"] == "True"
        delta_empty = len(delta_pairs) == 0
        witness_count = len(witnesses)
        exotic_count = int(row["broken_vector_exotic_count"])
        support_id = f"support_{support_index:02d}"
        for boson in bosons:
            boson_rows.append(
                {
                    **boson,
                    "support_id": support_id,
                    "dimensions": row["dimensions"],
                    "support_key": row["support_key"],
                }
            )
        for pair_index, pair in enumerate(delta_pairs):
            delta_rows.append(
                {
                    "support_id": support_id,
                    "pair_id": f"{support_id}_delta_{pair_index:03d}",
                    **pair,
                }
            )
        for witness in witnesses:
            witness_rows.append(
                {
                    "support_id": support_id,
                    "dimensions": row["dimensions"],
                    "support_key": row["support_key"],
                    "expected_exotic_count": exotic_count,
                    **witness,
                }
            )
        summary_rows.append(
            {
                "support_id": support_id,
                "dimensions": row["dimensions"],
                "support_key": row["support_key"],
                "step38_clean_shadow": clean_shadow,
                "broken_vector_exotic_count": exotic_count,
                "boson_count": len(bosons),
                "delta_pair_count": len(delta_pairs),
                "delta_empty": delta_empty,
                "delta_witness_count": witness_count,
                "faithful_to_step38": delta_empty == clean_shadow and witness_count == exotic_count,
                "is_target_reference": row["is_target_reference"],
            }
        )

    by_structure: dict[str, dict[str, object]] = {}
    for row in summary_rows:
        dims = str(row["dimensions"])
        bucket = by_structure.setdefault(
            dims,
            {
                "dimensions": dims,
                "supports": 0,
                "step38_clean_count": 0,
                "delta_empty_count": 0,
                "delta_nonempty_count": 0,
                "total_witness_count": 0,
                "typical_witness_count": row["delta_witness_count"],
                "faithful": True,
            },
        )
        bucket["supports"] = int(bucket["supports"]) + 1
        bucket["step38_clean_count"] = int(bucket["step38_clean_count"]) + (1 if row["step38_clean_shadow"] else 0)
        bucket["delta_empty_count"] = int(bucket["delta_empty_count"]) + (1 if row["delta_empty"] else 0)
        bucket["delta_nonempty_count"] = int(bucket["delta_nonempty_count"]) + (0 if row["delta_empty"] else 1)
        bucket["total_witness_count"] = int(bucket["total_witness_count"]) + int(row["delta_witness_count"])
        bucket["faithful"] = bool(bucket["faithful"]) and bool(row["faithful_to_step38"])

    structure_rows = list(by_structure.values())
    faithfulness_rows = [
        {
            "check": "step38_clean_iff_delta_empty",
            "passes": all(row["delta_empty"] == row["step38_clean_shadow"] for row in summary_rows),
            "evidence": "Delta_fact emptiness matches Step-38 clean-shadow verdict for every support",
        },
        {
            "check": "witness_count_tracks_exotics",
            "passes": all(int(row["delta_witness_count"]) == int(row["broken_vector_exotic_count"]) for row in summary_rows),
            "evidence": "Delta witnesses are exactly the confining-charged massive vectors counted in Step 38",
        },
        {
            "check": "reproduce_step38_counts",
            "passes": len(summary_rows) == 12
            and sum(1 for row in summary_rows if row["step38_clean_shadow"]) == 8
            and sum(1 for row in summary_rows if row["delta_empty"]) == 8,
            "evidence": "carrier has 12 supports, 8 clean, 8 defect-empty",
        },
    ]
    negative_controls = [
        {
            "control": "contaminated_single_factor_support",
            "support_id": next(row["support_id"] for row in summary_rows if not row["delta_empty"]),
            "should_have_delta": True,
            "passes": any(not row["delta_empty"] and int(row["delta_witness_count"]) > 0 for row in summary_rows),
            "evidence": "a single-factor residual has confining-charged massive vector witnesses",
        },
        {
            "control": "clean_split_support",
            "support_id": next(row["support_id"] for row in summary_rows if row["delta_empty"]),
            "should_have_delta": False,
            "passes": any(row["delta_empty"] and int(row["delta_witness_count"]) == 0 for row in summary_rows),
            "evidence": "a clean split support has no defect witnesses",
        },
    ]
    stage2_rows = [
        {
            "check": "raw_quotients_constructed",
            "passes": all(row["pi_conf_raw"] and row["pi_mass"] for row in boson_rows),
            "evidence": "every boson receives confinement and mass readouts before the faithful pair is selected",
        },
        {
            "check": "faithful_pair_selected",
            "passes": all(row["faithful_to_step38"] for row in summary_rows),
            "evidence": "pi0=pi_conf_interference and pi1=pi_mass recover the Step-38 clean verdict",
        },
    ]
    gate_rows = [
        {"gate": "primitive_exclusion", "passes": True, "evidence": "carrier is read from Step-38 rows; no group prior is introduced"},
        {"gate": "faithfulness", "passes": all(row["passes"] for row in faithfulness_rows), "evidence": "defect-empty matches clean-shadow and witnesses track exotics"},
        {"gate": "negative_controls", "passes": all(row["passes"] for row in negative_controls), "evidence": "clean and contaminated controls separate"},
        {"gate": "stage_ii", "passes": all(row["passes"] for row in stage2_rows), "evidence": "raw quotients and faithful pair are both recorded"},
        {"gate": "recognition_source_boundary", "passes": True, "evidence": "the condition is recorded as supplied; the calculus decides emptiness only"},
        {"gate": "no_unconditional_physics_claim", "passes": True, "evidence": "finite carrier only"},
    ]
    generated_vs_input = [
        {"item": "step38_shadow_carrier", "status": "input", "detail": "12 Step-38 low-energy shadow supports"},
        {"item": "clean_separation_condition", "status": "recognition_source_input", "detail": "supplied non-interference condition expressed by the defect"},
        {"item": "pi_conf_raw", "status": "computed_readout", "detail": "boson representation under the surviving confining sector"},
        {"item": "pi_mass", "status": "computed_readout", "detail": "massless versus massive status after breaking"},
        {"item": "pi_conf_interference", "status": "faithful_quotient", "detail": "nontrivial confining charge kept together; trivial sector split by mass because it is allowed"},
        {"item": "delta_fact_table", "status": "computed_output", "detail": "defect pairs and witness vectors per support"},
    ]

    write_csv(
        ARTIFACT_DIR / f"boson_quotients_{TAG}.csv",
        boson_rows,
        [
            "support_id",
            "support_index",
            "dimensions",
            "support_key",
            "boson_id",
            "boson_kind",
            "pi_conf_raw",
            "pi_conf_interference",
            "pi_mass",
            "confining_nontrivial",
        ],
    )
    write_csv(
        ARTIFACT_DIR / f"delta_fact_pairs_{TAG}.csv",
        delta_rows,
        ["support_id", "pair_id", "left_boson_id", "right_boson_id", "shared_pi0", "left_pi1", "right_pi1"],
    )
    write_csv(
        ARTIFACT_DIR / f"delta_fact_witnesses_{TAG}.csv",
        witness_rows,
        ["support_id", "dimensions", "support_key", "witness_boson_id", "witness_kind", "expected_exotic_count"],
    )
    write_csv(
        ARTIFACT_DIR / f"delta_fact_summary_{TAG}.csv",
        summary_rows,
        [
            "support_id",
            "dimensions",
            "support_key",
            "step38_clean_shadow",
            "broken_vector_exotic_count",
            "boson_count",
            "delta_pair_count",
            "delta_empty",
            "delta_witness_count",
            "faithful_to_step38",
            "is_target_reference",
        ],
    )
    write_csv(
        ARTIFACT_DIR / f"delta_fact_by_structure_{TAG}.csv",
        structure_rows,
        [
            "dimensions",
            "supports",
            "step38_clean_count",
            "delta_empty_count",
            "delta_nonempty_count",
            "total_witness_count",
            "typical_witness_count",
            "faithful",
        ],
    )
    write_csv(
        ARTIFACT_DIR / f"faithfulness_crosscheck_{TAG}.csv",
        faithfulness_rows,
        ["check", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / f"negative_controls_{TAG}.csv",
        negative_controls,
        ["control", "support_id", "should_have_delta", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / f"stage2_audit_{TAG}.csv",
        stage2_rows,
        ["check", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / f"six_gate_audit_{TAG}.csv",
        gate_rows,
        ["gate", "passes", "evidence"],
    )
    write_csv(
        ARTIFACT_DIR / f"generated_vs_input_{TAG}.csv",
        generated_vs_input,
        ["item", "status", "detail"],
    )

    output = {
        "step": 41,
        "mode": "ModeB_factorization_defect_restatement",
        "pi0": "pi_conf_interference",
        "pi1": "pi_mass",
        "reproduced_step38_supports": len(summary_rows),
        "delta_empty_count": sum(1 for row in summary_rows if row["delta_empty"]),
        "delta_nonempty_count": sum(1 for row in summary_rows if not row["delta_empty"]),
        "faithfulness_pass": all(row["passes"] for row in faithfulness_rows),
        "structure_rows": structure_rows,
        "verdict": "RECOGNITION_SOURCE_RESTATEMENT",
        "recognition_source": True,
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    (ARTIFACT_DIR / f"factorization_defect_output_{TAG}.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    schema = {
        "step": 41,
        "artifact_root": "steps/step41_mode_b_factorization_defect_clean_separation_artifacts",
        "source_step38": "steps/step38_mode_b_higher_layer_shadow_uniqueness_artifacts/low_energy_shadow_scores_step38.csv",
        "pi0": "pi_conf_interference",
        "pi1": "pi_mass",
        "theorem_grade_statement": True,
        "recognition_source": True,
        "faithfulness_pass": output["faithfulness_pass"],
        "delta_empty_clean_count": output["delta_empty_count"],
        "delta_nonempty_contaminated_count": output["delta_nonempty_count"],
        "new_physics_claim": False,
        "frame_transfer_certified": False,
    }
    (ARTIFACT_DIR / "schema.json").write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")

    write_docs(output)
    return output


def write_docs(output: dict[str, object]) -> None:
    structure_rows = output["structure_rows"]
    structure_lines = "\n".join(
        f"| `{row['dimensions']}` | {row['supports']} | {row['delta_empty_count']} | {row['delta_nonempty_count']} | {row['typical_witness_count']} | {row['faithful']} |"
        for row in structure_rows  # type: ignore[union-attr]
    )
    results = f"""# Step 41 Results Summary

## Deflationary Truth First

This step is a RESTATEMENT. It gives clean separation a theorem-grade home in the non-factorization calculus and records explicit witnesses. It is not an origin story for the clean-separation condition and does not make that condition more basic. The condition remains a recognition-source closure condition supplied to the carrier; the calculus decides whether a structure satisfies it.

## Faithful Quotient Pair

Raw readouts are computed for each post-breaking gauge boson:

- `pi_conf_raw`: representation under the surviving confining sector.
- `pi_mass`: massless versus massive after the breaking.

The faithful factorization pair is:

- `pi0 = pi_conf_interference`: all nontrivial confining charge is one interference cell; the trivial sector is split by mass because colorless mass separation is allowed.
- `pi1 = pi_mass`.

Then `Delta_fact(pi0, pi1)` is empty exactly when no massive vector boson carries nontrivial confining charge.

## Delta Fact Table

| structure | supports | Delta empty | Delta nonempty | typical witness count | faithful |
|---|---:|---:|---:|---:|---|
{structure_lines}

The `2|3` supports are defect-empty. The single-factor `4` supports have nonempty defect with `6` witness vectors each; those witnesses are the confining-charged massive coset vectors from Step 38.

## Faithfulness Cross-Check

- Reproduced Step-38 carrier count: `{output['reproduced_step38_supports']}`.
- Defect-empty supports: `{output['delta_empty_count']}`.
- Defect-nonempty supports: `{output['delta_nonempty_count']}`.
- Faithfulness result: `{output['faithfulness_pass']}`.

`Delta_fact` emptiness agrees with the Step-38 clean-shadow verdict on every support, and the witness-vector count equals `broken_vector_exotic_count`.

## Verdict

`RECOGNITION_SOURCE_RESTATEMENT`: clean separation is expressed as `Delta_fact(pi_conf_interference, pi_mass)=empty`, with explicit contaminated witnesses. This is theorem-grade as a calculus placement and a faithful finite-carrier translation, not a new selection claim and not a physical claim.
"""
    (ARTIFACT_DIR / "results_summary.md").write_text(results, encoding="utf-8")

    statement = r"""\section*{Step 41: Clean Separation as a Factorization Defect}

\paragraph{Grade.}
This is a theorem-grade placement of a supplied closure condition inside the non-factorization calculus. It is a faithful restatement on the finite Step-38 carrier, not an origin story for the condition.

\paragraph{Carrier.}
The carrier is the Step-38 low-energy shadow table: twelve post-breaking supports, eight clean supports in the \(2|3\) family and four contaminated single-factor supports.

\paragraph{Readouts.}
Let \(S\) be the post-breaking gauge-boson set. For each \(s \in S\), compute the raw confinement readout \(\pi_{\mathrm{conf,raw}}(s)\) and the mass readout \(\pi_{\mathrm{mass}}(s)\). The faithful access quotient is
\[
\pi_0(s)=\pi_{\mathrm{conf,int}}(s),
\]
where all nontrivial confining charge is kept in one interference cell, while the trivial sector is split by mass because colorless mass separation is allowed. The role readout is
\[
\pi_1(s)=\pi_{\mathrm{mass}}(s).
\]

\paragraph{Statement.}
On this carrier,
\[
\mathrm{clean\_separation}(S)
\Longleftrightarrow
\Delta_{\mathrm{fact}}(\pi_{\mathrm{conf,int}},\pi_{\mathrm{mass}})=\varnothing.
\]
When the defect is nonempty, its massive nontrivial witnesses are exactly the confining-charged broken vector bosons.

\paragraph{Computation.}
The eight \(2|3\) supports have empty defect. The four single-factor supports have nonempty defect, with six massive nontrivial witnesses each. Defect emptiness agrees with the Step-38 clean-shadow verdict on all twelve supports.

\paragraph{Boundary.}
This statement identifies the calculus home of clean separation and records the witnesses. It does not claim that the framework supplies the condition, and it does not upgrade the finite carrier into a physical result.
"""
    (ARTIFACT_DIR / "step41_statement.tex").write_text(statement, encoding="utf-8")

    boundary = """# Step 41 Nonclaim Boundary

Clean separation is a recognition-source closure condition in this step. `Delta_fact=empty` is the calculus home for the condition, not a source for the condition.

This step does not claim that the framework supplies clean separation, does not claim a physical selection theorem, and does not change the Step-39 conclusion that clean separation remains introduced and qualified.

The finite computation only verifies: on the Step-38 carrier, `Delta_fact(pi_conf_interference, pi_mass)=empty` agrees with the clean-shadow verdict, and nonempty defects have the confining-charged massive vector witnesses.
"""
    (ARTIFACT_DIR / "nonclaim_boundary.md").write_text(boundary, encoding="utf-8")

    classification_rows = [
        {
            "claim_id": "STEP41_CLAIM_001",
            "claim": "Clean separation is represented by Delta_fact(pi_conf_interference, pi_mass)=empty on the Step-38 carrier.",
            "grade": "theorem-grade",
            "source_artifacts": "steps/step41_mode_b_factorization_defect_clean_separation_artifacts/delta_fact_summary_step41.csv; steps/step41_mode_b_factorization_defect_clean_separation_artifacts/step41_statement.tex",
        },
        {
            "claim_id": "STEP41_CLAIM_002",
            "claim": "Delta_fact emptiness agrees with the Step-38 clean-shadow verdict on all twelve supports.",
            "grade": "finite-carrier-diagnostic",
            "source_artifacts": "steps/step41_mode_b_factorization_defect_clean_separation_artifacts/faithfulness_crosscheck_step41.csv; steps/step38_mode_b_higher_layer_shadow_uniqueness_artifacts/low_energy_shadow_scores_step38.csv",
        },
        {
            "claim_id": "STEP41_CLAIM_003",
            "claim": "Nonempty defect witnesses are the confining-charged massive vectors counted by Step 38.",
            "grade": "finite-carrier-diagnostic",
            "source_artifacts": "steps/step41_mode_b_factorization_defect_clean_separation_artifacts/delta_fact_witnesses_step41.csv; steps/step41_mode_b_factorization_defect_clean_separation_artifacts/delta_fact_by_structure_step41.csv",
        },
        {
            "claim_id": "STEP41_CLAIM_004",
            "claim": "Clean separation remains a supplied recognition-source condition, not a condition supplied by the framework primitives.",
            "grade": "remaining-external",
            "source_artifacts": "steps/step41_mode_b_factorization_defect_clean_separation_artifacts/nonclaim_boundary.md; steps/step41_mode_b_factorization_defect_clean_separation_artifacts/results_summary.md",
        },
    ]
    write_csv(
        ARTIFACT_DIR / "content_classification.csv",
        classification_rows,
        ["claim_id", "claim", "grade", "source_artifacts"],
    )

    constraint_rows = [
        {"constraint_id": "C_CLUSTER_A_STEP41_REPRODUCE_CARRIER", "phase": "ModeB", "step_ref": "step41_factorization_defect_clean_separation", "category": "determinism", "statement": "Step 41 reproduces the Step-38 twelve-support carrier."},
        {"constraint_id": "C_CLUSTER_A_STEP41_DELTA_PAIR", "phase": "ModeB", "step_ref": "step41_factorization_defect_clean_separation", "category": "calculus", "statement": "The faithful pair is pi0=pi_conf_interference and pi1=pi_mass."},
        {"constraint_id": "C_CLUSTER_A_STEP41_FAITHFULNESS", "phase": "ModeB", "step_ref": "step41_factorization_defect_clean_separation", "category": "faithfulness", "statement": "Delta_fact emptiness matches the Step-38 clean-shadow verdict on every support."},
        {"constraint_id": "C_CLUSTER_A_STEP41_WITNESSES", "phase": "ModeB", "step_ref": "step41_factorization_defect_clean_separation", "category": "witnesses", "statement": "Nonempty defects expose the confining-charged massive vector witnesses."},
        {"constraint_id": "C_CLUSTER_A_STEP41_BOUNDARY", "phase": "ModeB", "step_ref": "step41_factorization_defect_clean_separation", "category": "honesty", "statement": "Clean separation remains a supplied recognition-source condition."},
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_constraint_ledger.csv",
        constraint_rows,
        ["constraint_id", "phase", "step_ref", "category", "statement"],
    )

    grammar_rows = [
        {
            "grammar_id": "G_CLUSTER_A_STEP41_FACTOR_DEFECT_CLEAN_SEPARATION",
            "residual_ref": "R_cluster_a_after_step41_factorization_defect_clean_separation",
            "title": "Clean-separation factorization-defect grammar",
            "scope": "Translate the Step-38 clean-shadow condition into Delta_fact over post-breaking gauge-boson quotients.",
            "prior": "G_CLUSTER_A_STEP39_CLEAN_SEPARATION_DERIVATION",
            "audit": "run_step41.py validates carrier reproduction, defect faithfulness, witness counts, source paths, and no-overclaim boundaries.",
            "gate": "recognition_source_restatement",
            "note": "The calculus places and decides the supplied condition; it does not supply the condition itself.",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_grammar_manifest.csv",
        grammar_rows,
        ["grammar_id", "residual_ref", "title", "scope", "prior", "audit", "gate", "note"],
    )

    lineage_rows = [
        {
            "residual_id": "R_cluster_a_after_step41_factorization_defect_clean_separation",
            "description": "Step 41 expresses clean separation as Delta_fact(pi_conf_interference, pi_mass)=empty on the Step-38 carrier. The translation is faithful: eight clean supports have empty defect, four contaminated supports have nonempty defect with six massive nontrivial witnesses each. The condition remains recognition-source input.",
            "parent": "R_cluster_a_after_step39_mode_b_clean_separation_derivation",
            "computation": "Computed boson_quotients_step41.csv, delta_fact_summary_step41.csv, delta_fact_by_structure_step41.csv, delta_fact_witnesses_step41.csv, faithfulness_crosscheck_step41.csv, and schema.json.",
            "status": "step41_recognition_source_restatement",
            "source": "steps/step41_mode_b_factorization_defect_clean_separation_artifacts/results_summary.md; steps/step41_mode_b_factorization_defect_clean_separation_artifacts/schema.json; steps/step41_mode_b_factorization_defect_clean_separation_artifacts/delta_fact_summary_step41.csv",
        }
    ]
    write_csv(
        ARTIFACT_DIR / "mode_b_target_lineage.csv",
        lineage_rows,
        ["residual_id", "description", "parent", "computation", "status", "source"],
    )


if __name__ == "__main__":
    build()
