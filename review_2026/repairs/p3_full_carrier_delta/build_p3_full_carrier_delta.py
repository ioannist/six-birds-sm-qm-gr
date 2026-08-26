#!/usr/bin/env python3
"""Evaluate Step 41's factorization defect on the full Step 59 carrier."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[2]
STEPS_DIR = REPO_ROOT / "physics_atlas" / "thread_cluster_a" / "steps"

STEP28_BUILD = STEPS_DIR / "step28_mode_b_neutral_representation_desmuggle_artifacts" / "mode_b_neutral_representation_desmuggle_step28.py"
STEP33_BUILD = STEPS_DIR / "step33_mode_b_corrected_anomaly_chirality_artifacts" / "corrected_anomaly_chirality_step33.py"
STEP35_BUILD = STEPS_DIR / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
STEP41_BUILD = STEPS_DIR / "step41_mode_b_factorization_defect_clean_separation_artifacts" / "factorization_defect_clean_separation_step41.py"
STEP57_BUILD = STEPS_DIR / "step57_mode_b_record_stability_descent_artifacts" / "record_stability_descent_step57.py"

# Literal pins are intentional: the experiment must stop if frozen machinery moves.
EXPECTED_BUILD_HASHES = {
    STEP28_BUILD: "3dea42ae8232b3f3653391bab28766b609e9cd5fd89f0d30c1ffd1ad353ee780",
    STEP33_BUILD: "75fff25f5820a7bc62e8fbfe0b62a7f14dd76531b3d3094be9bfcb2e380a990f",
    STEP35_BUILD: "dad4c8793a8c32d47cc4d29cebfe2425f7821e61044024f7be22a33bcf21222d",
    STEP41_BUILD: "cadc5bf72d100accd4c2cd687373edf4592c19f89c34aaa3c8838ae976d0fdee",
    STEP57_BUILD: "f6ca35d7c3eaccad3a8f6cc42bd311818bf171da150e7e3384f980863addb2a2",
}

SCORES_NAME = "p3_full_carrier_delta_scores.csv"
SCHEMA_NAME = "p3_full_carrier_delta_schema.json"
FINDINGS_NAME = "p3_full_carrier_delta_findings.md"
VALIDATION_SAMPLE_SEED = 20260826
VALIDATION_SAMPLE_SIZE = 32
DELTA_CLEAN = "clean_evaluated"
DELTA_BREAKING = "breaking_evaluated"
DELTA_UNDEFINED = "delta_undefined_no_confinement"

SCORE_FIELDS = [
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
    "max_confining_subgroup",
    "transition_leak_count",
    "shadow_notes",
    "substrate_passes",
    "capacity_passes",
    "distinguishability_passes",
    "neutral_record_token_count",
    "alias_ambiguity_count",
    "alias_ambiguity_witnesses",
    "record_stability_passes",
    "delta_status",
    "delta_evaluated",
    "delta_pair_count",
    "delta_witness_count",
    "delta_empty",
    "prediction_counterexample",
    "is_reference_content",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_frozen_builds() -> None:
    for path, expected in EXPECTED_BUILD_HASHES.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen build hash mismatch: {path}: {actual} != {expected}")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Hashes are checked before any frozen build script is imported.
verify_frozen_builds()
s33 = load_module("p3_full_delta_s33", STEP33_BUILD)
s35 = load_module("p3_full_delta_s35", STEP35_BUILD)
s41 = load_module("p3_full_delta_s41", STEP41_BUILD)
s57 = load_module("p3_full_delta_s57", STEP57_BUILD)


def score_text(score: tuple[int, ...]) -> str:
    return "|".join(str(value) for value in score)


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def scalar_action_diagnostics(scalar: Any) -> dict[str, Any]:
    """Exact Step 59 adapter from a Step 35 scalar to confinement inputs."""
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


def evaluate_delta(row: dict[str, Any], support_index: int) -> dict[str, Any]:
    """Evaluate Delta whenever Step 41's confinement-defined input type exists."""
    confining = row["confining_subgroups"]
    if not confining:
        return {
            "max_confining_subgroup": "",
            "delta_status": DELTA_UNDEFINED,
            "delta_evaluated": False,
            "delta_pair_count": "",
            "delta_witness_count": "",
            "delta_empty": "",
        }
    step41_row = {
        "dimensions": row["dimensions"],
        "support_key": row["support_key"],
        "confining_subgroups": str(max(confining)),
        "broken_vector_exotic_count": str(row["transition_leak_count"]),
    }
    bosons = s41.build_bosons(step41_row, support_index)
    delta_pairs, witnesses = s41.compute_delta(bosons)
    delta_empty = len(delta_pairs) == 0
    return {
        "max_confining_subgroup": max(confining),
        "delta_status": DELTA_CLEAN if delta_empty else DELTA_BREAKING,
        "delta_evaluated": True,
        "delta_pair_count": len(delta_pairs),
        "delta_witness_count": len(witnesses),
        "delta_empty": delta_empty,
    }


def candidate_rows() -> list[dict[str, Any]]:
    """Rebuild the full corrected-closer carrier in Step 59's declared order."""
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
                "base_stable_composite_mass_requirement": bool_text(substrate_passes),
            }
            record = s57.record_layer_membership(adapted)
            row: dict[str, Any] = {
                "carrier_id": f"carrier_{len(rows):05d}",
                "dimensions": dim_text,
                "support_key": support_key,
                "support_score": score_text(support_score),
                "field_count": support_score[0],
                "component_dim_sum": support_score[1],
                "base_higher_layer_passes": bool(base["higher_layer_passes"]),
                "witness_scalar_key": scalar.text,
                "witness_scalar_reps": "x".join(scalar.canonical_reps),
                "witness_scalar_charge": scalar.charge,
                "covered_count": base["covered_count"],
                "fermion_count": base["fermion_count"],
                "breaks_to_unbroken_u1": bool(base["breaks_to_unbroken_u1"]),
                "confining_subgroups": action["confining_subgroups"],
                "transition_leak_count": action["transition_leak_count"],
                "shadow_notes": action["shadow_notes"],
                "substrate_passes": substrate_passes,
                "capacity_passes": bool(record["capacity_passes"]),
                "distinguishability_passes": bool(record["distinguishability_passes"]),
                "neutral_record_token_count": record["neutral_record_token_count"],
                "alias_ambiguity_count": record["alias_ambiguity_count"],
                "alias_ambiguity_witnesses": record["alias_ambiguity_witnesses"],
                "record_stability_passes": bool(record["record_stability_passes"]),
                "is_reference_content": support_key == target_key,
            }
            row.update(evaluate_delta(row, len(rows)))
            row["prediction_counterexample"] = bool(
                row["record_stability_passes"] and row["delta_status"] == DELTA_BREAKING
            )
            rows.append(row)
    return rows


def corrected_table(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    table: dict[str, dict[str, int]] = {}
    for rs_value, label in ((False, "RS_false"), (True, "RS_true")):
        selected = [row for row in rows if row["record_stability_passes"] is rs_value]
        table[label] = {
            DELTA_CLEAN: sum(row["delta_status"] == DELTA_CLEAN for row in selected),
            DELTA_BREAKING: sum(row["delta_status"] == DELTA_BREAKING for row in selected),
            DELTA_UNDEFINED: sum(row["delta_status"] == DELTA_UNDEFINED for row in selected),
            "total": len(selected),
        }
    return table


def conjunct_witnesses(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    conjuncts = {
        "substrate": "substrate_passes",
        "capacity": "capacity_passes",
        "distinguishability": "distinguishability_passes",
    }
    result: dict[str, dict[str, Any]] = {}
    for label, field in conjuncts.items():
        other_fields = [candidate for candidate in conjuncts.values() if candidate != field]
        breaking = [
            row for row in rows
            if row[field] and row["delta_status"] == DELTA_BREAKING
        ]
        exclusive = [row for row in breaking if not any(row[other] for other in other_fields)]
        result[label] = {
            "satisfying_and_breaking_count": len(breaking),
            "exclusive_only_breaking_count": len(exclusive),
            "witnesses": [
                {
                    "carrier_id": row["carrier_id"],
                    "delta_pair_count": row["delta_pair_count"],
                }
                for row in breaking[:5]
            ],
            "exclusive_only_witnesses": [
                {
                    "carrier_id": row["carrier_id"],
                    "delta_pair_count": row["delta_pair_count"],
                }
                for row in exclusive[:5]
            ],
        }
    return result


def csv_value(value: Any) -> Any:
    if isinstance(value, bool):
        return bool_text(value)
    if isinstance(value, list):
        return json.dumps(value)
    return value


def write_scores(rows: list[dict[str, Any]]) -> Path:
    path = ARTIFACT_DIR / SCORES_NAME
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SCORE_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field, "")) for field in SCORE_FIELDS})
    return path


def build_schema(rows: list[dict[str, Any]], scores_hash: str) -> dict[str, Any]:
    table = corrected_table(rows)
    rs_count = table["RS_true"]["total"]
    rs_breaking = table["RS_true"][DELTA_BREAKING]
    clean_total = sum(row["delta_status"] == DELTA_CLEAN for row in rows)
    breaking_total = sum(row["delta_status"] == DELTA_BREAKING for row in rows)
    undefined_total = sum(row["delta_status"] == DELTA_UNDEFINED for row in rows)
    imported = [
        {
            "path": str(path.relative_to(REPO_ROOT)),
            "sha256": expected,
            "role": role,
        }
        for path, expected, role in (
            (STEP28_BUILD, EXPECTED_BUILD_HASHES[STEP28_BUILD], "transitive Step 33 representation machinery"),
            (STEP33_BUILD, EXPECTED_BUILD_HASHES[STEP33_BUILD], "corrected closer carrier"),
            (STEP35_BUILD, EXPECTED_BUILD_HASHES[STEP35_BUILD], "higher-layer substrate and scalar machinery"),
            (STEP41_BUILD, EXPECTED_BUILD_HASHES[STEP41_BUILD], "build_bosons and compute_delta"),
            (STEP57_BUILD, EXPECTED_BUILD_HASHES[STEP57_BUILD], "record-stability conjuncts"),
        )
    ]
    return {
        "schema_version": 1,
        "experiment": "P3-REPAIR-1 full-carrier Delta_fact evaluation",
        "carrier_definition": "all Step 33 corrected chiral closer rows in Step 59 order",
        "carrier_rows": len(rows),
        "delta_status_values": [DELTA_CLEAN, DELTA_BREAKING, DELTA_UNDEFINED],
        "corrected_table": table,
        "headline": {
            "RS_count": rs_count,
            "RS_and_breaking_count": rs_breaking,
            "prediction_fails": rs_breaking > 0,
            "breaking_total": breaking_total,
            "clean_total": clean_total,
            "delta_undefined_total": undefined_total,
        },
        "conjunct_breaking_witnesses": conjunct_witnesses(rows),
        "undefined_semantics": "delta_undefined_no_confinement is neither clean nor breaking",
        "validation_sample_seed": VALIDATION_SAMPLE_SEED,
        "validation_sample_size": VALIDATION_SAMPLE_SIZE,
        "imported_build_scripts": imported,
        "scores_csv": SCORES_NAME,
        "scores_csv_columns": SCORE_FIELDS,
        "scores_csv_sha256": scores_hash,
        "score_column_types": {
            **{
                field: "string"
                for field in (
                    "carrier_id",
                    "dimensions",
                    "support_key",
                    "support_score",
                    "witness_scalar_key",
                    "witness_scalar_reps",
                    "shadow_notes",
                    "alias_ambiguity_witnesses",
                    "delta_status",
                )
            },
            **{
                field: "integer"
                for field in (
                    "field_count",
                    "component_dim_sum",
                    "witness_scalar_charge",
                    "covered_count",
                    "fermion_count",
                    "transition_leak_count",
                    "neutral_record_token_count",
                    "alias_ambiguity_count",
                )
            },
            "confining_subgroups": "array[integer]",
            "max_confining_subgroup": "integer|null",
            "delta_pair_count": "integer|null",
            "delta_witness_count": "integer|null",
            "delta_empty": "boolean|null",
            **{
                field: "boolean"
                for field in (
                    "base_higher_layer_passes",
                    "breaks_to_unbroken_u1",
                    "substrate_passes",
                    "capacity_passes",
                    "distinguishability_passes",
                    "record_stability_passes",
                    "delta_evaluated",
                    "prediction_counterexample",
                    "is_reference_content",
                )
            },
        },
        "columns": {
            "carrier_id": "unique Step 59-order row identifier",
            "dimensions": "pipe-delimited factor dimensions",
            "support_key": "Step 33 support key",
            "substrate_passes": "Step 59 substrate conjunct",
            "capacity_passes": "Step 57 capacity conjunct",
            "distinguishability_passes": "Step 57 distinguishability conjunct",
            "record_stability_passes": "conjunction of substrate, capacity, and distinguishability",
            "confining_subgroups": "JSON array of confinement factors inferred by Step 59's adapter",
            "max_confining_subgroup": "factor supplied to Step 41; blank when Delta is undefined",
            "transition_leak_count": "Step 59 broken-vector input to Step 41",
            "delta_status": "one of delta_status_values",
            "delta_evaluated": "true exactly for clean_evaluated or breaking_evaluated",
            "delta_pair_count": "Step 41 defect-pair cardinality; blank when undefined",
            "delta_witness_count": "Step 41 defect-witness cardinality; blank when undefined",
            "delta_empty": "true exactly for clean_evaluated; blank when undefined",
            "prediction_counterexample": "RS and breaking_evaluated",
        },
    }


def table_markdown(table: dict[str, dict[str, int]]) -> str:
    return "\n".join(
        [
            "| RS status | clean (evaluated) | breaking (evaluated) | Delta undefined | Total |",
            "|---|---:|---:|---:|---:|",
            *[
                f"| {label} | {values[DELTA_CLEAN]} | {values[DELTA_BREAKING]} | {values[DELTA_UNDEFINED]} | {values['total']} |"
                for label, values in table.items()
            ],
        ]
    )


def witness_markdown(witnesses: dict[str, dict[str, Any]]) -> str:
    lines = [
        "| Conjunct | Satisfying conjunct and breaking | Exclusive-only breaking | Example carrier:pair-count |",
        "|---|---:|---:|---|",
    ]
    for label, data in witnesses.items():
        examples = ", ".join(
            f"{row['carrier_id']}:{row['delta_pair_count']}" for row in data["witnesses"]
        ) or "none"
        lines.append(
            f"| {label} | {data['satisfying_and_breaking_count']} | "
            f"{data['exclusive_only_breaking_count']} | {examples} |"
        )
    return "\n".join(lines)


def write_findings(schema: dict[str, Any]) -> None:
    headline = schema["headline"]
    conclusion = (
        "The strong finite-carrier implication fails: at least one record-stable row has an evaluated nonempty Delta_fact."
        if headline["prediction_fails"]
        else "The strong finite-carrier implication survives: every record-stable row has an evaluated empty Delta_fact, and no record-stable row is Delta-undefined."
    )
    text = f"""# P3-REPAIR-1: Full-carrier Delta_fact findings

## Corrected table

{table_markdown(schema['corrected_table'])}

Headline counts: RS = {headline['RS_count']}; RS and breaking = {headline['RS_and_breaking_count']}; breaking total = {headline['breaking_total']}; clean total = {headline['clean_total']}; Delta undefined = {headline['delta_undefined_total']}.

{conclusion}

## Anti-circularity witnesses

“Satisfying conjunct and breaking” means the named RS conjunct is true without requiring either of the other conjuncts. “Exclusive-only” is the stricter subset for which both other conjuncts are false.

{witness_markdown(schema['conjunct_breaking_witnesses'])}

## No-confinement semantics — declaration for reviewer ruling

A structure with no confining factor is not honestly classifiable as either clean or breaking under this Delta_fact construction. Step 41 defines its interference sectors relative to a selected confining subgroup, so without such a factor there is no typed pi_conf projection and therefore no Delta_fact proposition to evaluate. Calling the empty set “clean” would manufacture a vacuous success by extending the function outside its declared domain; calling it “breaking” would manufacture a defect with no interference-sector comparison. This repair therefore records `delta_undefined_no_confinement` as a third outcome. The physically honest reading is that “clean separation” requires confinement as a domain prerequisite; whether the prediction should explicitly include that prerequisite is a semantics declaration reserved for reviewer ruling.

## Determinism and integrity

The carrier order and all RS inputs follow Step 59. Delta_fact is evaluated with Step 41 for every row having a confining subgroup, irrespective of substrate or higher-layer pass status. All five direct or transitive imported build scripts are checked against literal SHA-256 pins before import. `{SCORES_NAME}` has SHA-256 `{schema['scores_csv_sha256']}`. The validator uses seed {VALIDATION_SAMPLE_SEED} to rederive {VALIDATION_SAMPLE_SIZE} evaluated rows.
"""
    (ARTIFACT_DIR / FINDINGS_NAME).write_text(text, encoding="utf-8")


def main() -> None:
    started = time.monotonic()
    rows = candidate_rows()
    if len(rows) != 11990:
        raise RuntimeError(f"full carrier changed: expected 11990 rows, got {len(rows)}")
    scores_path = write_scores(rows)
    schema = build_schema(rows, sha256_file(scores_path))
    (ARTIFACT_DIR / SCHEMA_NAME).write_text(
        json.dumps(schema, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_findings(schema)
    elapsed = time.monotonic() - started
    print(
        f"build_p3_full_carrier_delta.py: PASS: rows={len(rows)} "
        f"RS={schema['headline']['RS_count']} "
        f"RS_breaking={schema['headline']['RS_and_breaking_count']} "
        f"elapsed_seconds={elapsed:.3f}"
    )


if __name__ == "__main__":
    main()
