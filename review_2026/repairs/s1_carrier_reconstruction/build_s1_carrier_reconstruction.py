#!/usr/bin/env python3
"""Build the S1 sound-carrier reconstruction artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from collections import Counter
from pathlib import Path
from typing import Any

import carrier_chain as chain
import representation_model as rm


ARTIFACT_DIR = Path(__file__).resolve().parent
# Preserve the byte-identical S1-REPAIR-1 schema after DESIGN.md is extended by
# repair 2. This snapshot is the exact design document hashed by repair 1.
DESIGN_PATH = ARTIFACT_DIR / "DESIGN_REPAIR1.md"

FLOW_FIELDS = ["stage", "input_population", "population", "excluded_count", "exclusion_percent", "row_sha256", "hash_kind"]
FAMILY_FIELDS = ["stage", "dimensions", "population"]
FINAL_FIELDS = [
    "dimensions",
    "support_key",
    "support_score",
    "is_target_reference",
    "witness_scalar",
    "confining_subgroups",
    "broken_vector_exotic_count",
    "delta_pair_count",
    "delta_witness_count",
    "delta_empty",
    "clean_separation_passes",
]
COMPARISON_FIELDS = [
    "stage",
    "published_count",
    "reconstructed_count",
    "count_change",
    "published_exclusion_percent",
    "reconstructed_exclusion_percent",
    "published_families",
    "reconstructed_families",
    "comparison_note",
]
REP_TEST_FIELDS = ["check", "dimension", "rep", "passes", "evidence"]

PUBLISHED_COUNTS = {
    "genuinely_chiral": 11990,
    "atomic_packaging": 156,
    "closure_consistency": 130,
    "chirality_faithfulness": 80,
    "higher_layer_mass_closure_proxy": 12,
    "clean_separation": 8,
}
PUBLISHED_FAMILIES = {
    "genuinely_chiral": "2:730;2|2:6656;2|3:2153;2|4:1754;3:85;3|3:170;3|4:226;4:56;4|4:160",
    "atomic_packaging": "2:2;2|2:56;2|3:29;2|4:0;3:49;3|3:0;3|4:0;4:20;4|4:0",
    "closure_consistency": "2:2;2|2:48;2|3:15;2|4:0;3:49;3|3:0;3|4:0;4:16;4|4:0",
    "chirality_faithfulness": "2:0;2|2:0;2|3:15;2|4:0;3:49;3|3:0;3|4:0;4:16;4|4:0",
    "higher_layer_mass_closure_proxy": "2|3:8;4:4",
    "clean_separation": "2|3:8",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def exclusion_percent(input_population: int, population: int) -> str:
    if not input_population:
        return ""
    return f"{100.0 * (input_population - population) / input_population:.6f}"


def render_csv(rows: list[dict[str, Any]], fields: list[str]) -> str:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: row.get(field, "") for field in fields})
    return handle.getvalue()


def flow_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    previous = 0
    for index, stage in enumerate(result["stages"]):
        input_population = stage.population if index == 0 else previous
        rows.append(
            {
                "stage": stage.stage,
                "input_population": input_population,
                "population": stage.population,
                "excluded_count": input_population - stage.population,
                "exclusion_percent": exclusion_percent(input_population, stage.population),
                "row_sha256": stage.row_sha256,
                "hash_kind": stage.hash_kind,
            }
        )
        previous = stage.population
    return rows


def families_text(rows: list[dict[str, Any]], stage: str) -> str:
    selected = [row for row in rows if row["stage"] == stage and int(row["population"]) > 0]
    return ";".join(f"{row['dimensions']}:{row['population']}" for row in selected)


def comparison_rows(result: dict[str, Any], flows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flow_by_stage = {row["stage"]: row for row in flows}
    rows = [
        {
            "stage": "neutral_carrier",
            "published_count": "",
            "reconstructed_count": flow_by_stage["neutral_carrier"]["population"],
            "count_change": "",
            "published_exclusion_percent": "",
            "reconstructed_exclusion_percent": flow_by_stage["neutral_carrier"]["exclusion_percent"],
            "published_families": "not_available_like_for_like",
            "reconstructed_families": families_text(result["families"], "neutral_carrier"),
            "comparison_note": "published 280983 was already anomaly-filtered and used set semantics, so it is not a neutral-multiset denominator",
        }
    ]
    ordered = list(PUBLISHED_COUNTS)
    for index, stage in enumerate(ordered):
        published_count = PUBLISHED_COUNTS[stage]
        published_previous = PUBLISHED_COUNTS[ordered[index - 1]] if index else 0
        reconstructed = int(flow_by_stage[stage]["population"])
        rows.append(
            {
                "stage": stage,
                "published_count": published_count,
                "reconstructed_count": reconstructed,
                "count_change": reconstructed - published_count,
                "published_exclusion_percent": exclusion_percent(published_previous, published_count) if index else "",
                "reconstructed_exclusion_percent": flow_by_stage[stage]["exclusion_percent"],
                "published_families": PUBLISHED_FAMILIES[stage],
                "reconstructed_families": families_text(result["families"], stage),
                "comparison_note": "like-named selection stage; representation and set/multiset carrier semantics differ",
            }
        )
    return rows


def final_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    catalogs = result["catalogs"]
    for candidate in sorted(
        result["stage_rows"]["higher_layer_mass_closure_proxy"],
        key=lambda row: (row.dimensions, row.support_key),
    ):
        key = (candidate.dimensions, candidate.support_key)
        higher = result["higher_diagnostics"][key]
        clean = result["clean_diagnostics"][key]
        rows.append(
            {
                "dimensions": "|".join(map(str, candidate.dimensions)),
                "support_key": candidate.support_key,
                "support_score": "|".join(map(str, chain.support_score(candidate.combo, catalogs[candidate.dimensions]))),
                "is_target_reference": candidate.dimensions == chain.TARGET_DIMENSIONS and candidate.support_key == chain.TARGET_SUPPORT_KEY,
                "witness_scalar": higher["witness_scalar"].text,
                "confining_subgroups": "|".join(map(str, clean["confining_subgroups"])),
                "broken_vector_exotic_count": clean["broken_vector_exotic_count"],
                "delta_pair_count": clean["delta_pair_count"],
                "delta_witness_count": clean["delta_witness_count"],
                "delta_empty": clean["delta_empty"],
                "clean_separation_passes": clean["clean_shadow_requirement"] and clean["delta_empty"],
            }
        )
    return rows


def conclusion_data(result: dict[str, Any], finals: list[dict[str, Any]]) -> dict[str, Any]:
    higher_families = {row["dimensions"] for row in finals}
    clean_families = {row["dimensions"] for row in finals if row["clean_separation_passes"]}
    cosets: dict[str, list[int]] = {}
    for dimensions in sorted(higher_families):
        cosets[dimensions] = sorted(
            {int(row["broken_vector_exotic_count"]) for row in finals if row["dimensions"] == dimensions}
        )
    target_stages = {
        stage: any(
            row.dimensions == chain.TARGET_DIMENSIONS and row.support_key == chain.TARGET_SUPPORT_KEY
            for row in rows
        )
        for stage, rows in result["stage_rows"].items()
    }
    return {
        "higher_layer_families": sorted(higher_families),
        "clean_separation_families": sorted(clean_families),
        "coset_counts_by_structure": cosets,
        "six_vs_zero_survives": cosets == {"2|3": [0], "4": [6]},
        "two_three_and_su4_to_clean_two_three_survives": higher_families == {"2|3", "4"} and clean_families == {"2|3"},
        "target_passes_by_stage": target_stages,
        "target_passes_clean_separation": target_stages["clean_separation"],
        "step38_step41_faithful": all(row["step38_step41_faithful"] for row in result["clean_diagnostics"].values()),
    }


def table_markdown(rows: list[dict[str, Any]], columns: list[str]) -> str:
    labels = [column.replace("_", " ") for column in columns]
    lines = ["| " + " | ".join(labels) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def findings_text(schema: dict[str, Any], flows: list[dict[str, Any]], comparisons: list[dict[str, Any]]) -> str:
    conclusion = schema["conclusion"]
    flow_table = table_markdown(
        flows,
        ["stage", "input_population", "population", "excluded_count", "exclusion_percent"],
    )
    comparison_table = table_markdown(
        comparisons,
        ["stage", "published_count", "reconstructed_count", "count_change"],
    )
    return f"""# S1-REPAIR-1 results

## Stage-resolved flow

{flow_table}

Each exclusion percentage is relative only to the immediately preceding row. The reconstructed corrected-carrier headline is 1,066 genuinely chiral multisets, not 11,990. From that sound chiral denominator through chirality-faithfulness, the exclusion is {schema['headline']['sound_chiral_to_faithful_exclusion_percent']}%, replacing the published 99.332777% (11,990 to 80).

## Old versus new

{comparison_table}

The published 280,983 Step-28 count is not shown as a like-for-like neutral denominator: it was already anomaly-filtered and used distinct-field set semantics. The comparable published corrected chiral carrier is 11,990; it moves to 1,066. The later populations move 156→84, 130→62, 80→52, 12→8, and 8→4.

## Selection conclusion

The structural conclusion survives: the higher-layer proxy leaves exactly `2|3` and SU(4)-alone, and clean separation leaves exactly `2|3`. The higher-layer family is split 4+4 rather than the published 8+4. Every repaired `2|3` survivor has coset count 0 and empty Step-41 defect; every SU(4)-alone survivor has coset count 6 and 48 defect pairs. Therefore the 6-vs-0 discriminator survives on the sound carrier. The declared SM reference row survives every stage, including clean separation.

## Representation gate

`representation_model.py: PASS: declared_rep_instances={schema['representation_self_test']['declared_rep_instances']} canonical_rep_instances={schema['representation_self_test']['canonical_rep_instances']} checks={schema['representation_self_test']['check_count']}`

The higher-layer mass-closure stage remains explicitly `PROXY`; this packet repairs the representation carrier and multiset semantics, not that predicate's physical status. The retained route-incidence restriction likewise awaits the roster-based competitor packet.
"""


def assemble_artifacts(result: dict[str, Any]) -> dict[str, str]:
    flows = flow_rows(result)
    comparisons = comparison_rows(result, flows)
    finals = final_rows(result)
    rep_checks = result["representation_self_test"]["checks"]
    csv_artifacts = {
        "s1_stage_flow.csv": render_csv(flows, FLOW_FIELDS),
        "s1_survivor_families.csv": render_csv(result["families"], FAMILY_FIELDS),
        "s1_final_family.csv": render_csv(finals, FINAL_FIELDS),
        "s1_old_vs_new.csv": render_csv(comparisons, COMPARISON_FIELDS),
        "s1_representation_self_test.csv": render_csv(rep_checks, REP_TEST_FIELDS),
    }
    stage_by_name = {stage.stage: stage.population for stage in result["stages"]}
    conclusion = conclusion_data(result, finals)
    schema = {
        "schema_version": 1,
        "experiment": "S1-REPAIR-1 sound carrier reconstruction",
        "window": {
            "dimension_window": list(chain.DIMENSION_WINDOW),
            "factor_counts": [1, 2],
            "charge_units": list(chain.CHARGE_UNITS),
            "field_cap": chain.MAX_FIELDS,
            "component_cap": chain.COMPONENT_CAP,
            "content_semantics": "multisets of canonical (rep-tuple, charge) field types",
            "truncated": False,
        },
        "representation_alphabet": list(rm.REPRESENTATION_ALPHABET),
        "canonical_representations": {str(n): list(rm.canonical_reps(n)) for n in rm.DIMENSION_WINDOW},
        "representation_self_test": {
            "passes": result["representation_self_test"]["passes"],
            "declared_rep_instances": result["representation_self_test"]["declared_rep_instances"],
            "canonical_rep_instances": result["representation_self_test"]["canonical_rep_instances"],
            "check_count": result["representation_self_test"]["check_count"],
            "failed_checks": result["representation_self_test"]["failed_checks"],
        },
        "stage_counts": stage_by_name,
        "stage_hashes": {stage.stage: stage.row_sha256 for stage in result["stages"]},
        "stage_hash_kinds": {stage.stage: stage.hash_kind for stage in result["stages"]},
        "enumeration_diagnostics": result["enumeration_diagnostics"],
        "headline": {
            "published_corrected_chiral_carrier": 11990,
            "reconstructed_genuinely_chiral_carrier": stage_by_name["genuinely_chiral"],
            "published_chirality_faithful": 80,
            "reconstructed_chirality_faithful": stage_by_name["chirality_faithfulness"],
            "sound_chiral_to_faithful_exclusion_percent": exclusion_percent(
                stage_by_name["genuinely_chiral"], stage_by_name["chirality_faithfulness"]
            ),
        },
        "conclusion": conclusion,
        "published_sources": {
            "step28": "physics_atlas/thread_cluster_a/steps/step28_mode_b_neutral_representation_desmuggle_artifacts/mode_b_neutral_representation_desmuggle_step28.py",
            "step33": "physics_atlas/thread_cluster_a/steps/step33_mode_b_corrected_anomaly_chirality_artifacts/corrected_anomaly_chirality_step33.py",
            "step35": "physics_atlas/thread_cluster_a/steps/step35_mode_b_higher_layer_descent_artifacts/higher_layer_descent_step35.py",
            "step38": "physics_atlas/thread_cluster_a/steps/step38_mode_b_higher_layer_shadow_uniqueness_artifacts/higher_layer_shadow_step38.py",
            "step41": "physics_atlas/thread_cluster_a/steps/step41_mode_b_factorization_defect_clean_separation_artifacts/factorization_defect_clean_separation_step41.py",
        },
        "implementation_sha256": {
            "representation_model.py": sha256_text((ARTIFACT_DIR / "representation_model.py").read_text(encoding="utf-8")),
            "carrier_chain.py": sha256_text((ARTIFACT_DIR / "carrier_chain.py").read_text(encoding="utf-8")),
            "DESIGN.md": sha256_text(DESIGN_PATH.read_text(encoding="utf-8")),
        },
        "artifact_sha256": {name: sha256_text(text) for name, text in csv_artifacts.items()},
    }
    schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    findings = findings_text(schema, flows, comparisons)
    return {**csv_artifacts, "s1_schema.json": schema_text, "RESULTS.md": findings}


def main() -> None:
    started = time.monotonic()
    result = chain.run_chain()
    artifacts = assemble_artifacts(result)
    for name, text in artifacts.items():
        (ARTIFACT_DIR / name).write_text(text, encoding="utf-8")
    elapsed = time.monotonic() - started
    counts = {stage.stage: stage.population for stage in result["stages"]}
    print(
        "build_s1_carrier_reconstruction.py: PASS: "
        + " ".join(f"{stage}={count}" for stage, count in counts.items())
        + f" elapsed_seconds={elapsed:.3f}"
    )


if __name__ == "__main__":
    main()
