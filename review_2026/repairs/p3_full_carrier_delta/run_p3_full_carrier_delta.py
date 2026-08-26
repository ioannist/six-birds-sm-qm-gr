#!/usr/bin/env python3
"""Validate the P3 full-carrier Delta_fact repair artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path(__file__).resolve().parent
REPO_ROOT = ARTIFACT_DIR.parents[2]
SCORES_PATH = ARTIFACT_DIR / "p3_full_carrier_delta_scores.csv"
SCHEMA_PATH = ARTIFACT_DIR / "p3_full_carrier_delta_schema.json"
FINDINGS_PATH = ARTIFACT_DIR / "p3_full_carrier_delta_findings.md"
BUILD_PATH = ARTIFACT_DIR / "build_p3_full_carrier_delta.py"
STEP41_BUILD = REPO_ROOT / "physics_atlas/thread_cluster_a/steps/step41_mode_b_factorization_defect_clean_separation_artifacts/factorization_defect_clean_separation_step41.py"

EXPECTED_BUILD_HASHES = {
    "physics_atlas/thread_cluster_a/steps/step28_mode_b_neutral_representation_desmuggle_artifacts/mode_b_neutral_representation_desmuggle_step28.py": "3dea42ae8232b3f3653391bab28766b609e9cd5fd89f0d30c1ffd1ad353ee780",
    "physics_atlas/thread_cluster_a/steps/step33_mode_b_corrected_anomaly_chirality_artifacts/corrected_anomaly_chirality_step33.py": "75fff25f5820a7bc62e8fbfe0b62a7f14dd76531b3d3094be9bfcb2e380a990f",
    "physics_atlas/thread_cluster_a/steps/step35_mode_b_higher_layer_descent_artifacts/higher_layer_descent_step35.py": "dad4c8793a8c32d47cc4d29cebfe2425f7821e61044024f7be22a33bcf21222d",
    "physics_atlas/thread_cluster_a/steps/step41_mode_b_factorization_defect_clean_separation_artifacts/factorization_defect_clean_separation_step41.py": "cadc5bf72d100accd4c2cd687373edf4592c19f89c34aaa3c8838ae976d0fdee",
    "physics_atlas/thread_cluster_a/steps/step57_mode_b_record_stability_descent_artifacts/record_stability_descent_step57.py": "f6ca35d7c3eaccad3a8f6cc42bd311818bf171da150e7e3384f980863addb2a2",
}
DELTA_CLEAN = "clean_evaluated"
DELTA_BREAKING = "breaking_evaluated"
DELTA_UNDEFINED = "delta_undefined_no_confinement"


def fail(message: str) -> None:
    print(f"run_p3_full_carrier_delta.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        fail(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def parse_bool(text: str, field: str, carrier_id: str) -> bool:
    if text not in {"True", "False"}:
        fail(f"{carrier_id} has invalid {field}: {text!r}")
    return text == "True"


def read_rows(schema: dict[str, Any]) -> list[dict[str, str]]:
    with SCORES_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != schema["scores_csv_columns"]:
            fail("scores CSV header does not match the declared schema")
        rows = list(reader)
    if set(schema["score_column_types"]) != set(schema["scores_csv_columns"]):
        fail("score-column type schema is incomplete")
    return rows


def verify_files_and_hashes(schema: dict[str, Any]) -> None:
    for path in (BUILD_PATH, SCORES_PATH, SCHEMA_PATH, FINDINGS_PATH):
        if not path.is_file():
            fail(f"missing required file: {path.name}")
    pinned = {row["path"]: row["sha256"] for row in schema["imported_build_scripts"]}
    if pinned != EXPECTED_BUILD_HASHES:
        fail("schema imported-build pins do not match validator constants")
    for relative, expected in EXPECTED_BUILD_HASHES.items():
        actual = sha256_file(REPO_ROOT / relative)
        if actual != expected:
            fail(f"frozen build hash mismatch: {relative}: {actual} != {expected}")
    actual_scores_hash = sha256_file(SCORES_PATH)
    if actual_scores_hash != schema["scores_csv_sha256"]:
        fail(f"scores CSV hash mismatch: {actual_scores_hash} != {schema['scores_csv_sha256']}")


def derive_table(rows: list[dict[str, str]]) -> dict[str, dict[str, int]]:
    table: dict[str, dict[str, int]] = {}
    for rs_text, label in (("False", "RS_false"), ("True", "RS_true")):
        selected = [row for row in rows if row["record_stability_passes"] == rs_text]
        table[label] = {
            DELTA_CLEAN: sum(row["delta_status"] == DELTA_CLEAN for row in selected),
            DELTA_BREAKING: sum(row["delta_status"] == DELTA_BREAKING for row in selected),
            DELTA_UNDEFINED: sum(row["delta_status"] == DELTA_UNDEFINED for row in selected),
            "total": len(selected),
        }
    return table


def derive_witness_counts(rows: list[dict[str, str]]) -> dict[str, tuple[int, int]]:
    fields = {
        "substrate": "substrate_passes",
        "capacity": "capacity_passes",
        "distinguishability": "distinguishability_passes",
    }
    counts: dict[str, tuple[int, int]] = {}
    for label, field in fields.items():
        others = [candidate for candidate in fields.values() if candidate != field]
        breaking = [row for row in rows if row[field] == "True" and row["delta_status"] == DELTA_BREAKING]
        exclusive = [row for row in breaking if all(row[other] == "False" for other in others)]
        counts[label] = (len(breaking), len(exclusive))
    return counts


def verify_rows(rows: list[dict[str, str]], schema: dict[str, Any]) -> None:
    if len(rows) != 11990 or schema["carrier_rows"] != 11990:
        fail(f"expected 11990 carrier rows, got CSV={len(rows)} schema={schema['carrier_rows']}")
    expected_ids = [f"carrier_{index:05d}" for index in range(len(rows))]
    if [row["carrier_id"] for row in rows] != expected_ids:
        fail("carrier IDs are not unique and sequential in Step 59 order")

    for row in rows:
        carrier_id = row["carrier_id"]
        substrate = parse_bool(row["substrate_passes"], "substrate_passes", carrier_id)
        capacity = parse_bool(row["capacity_passes"], "capacity_passes", carrier_id)
        distinguishability = parse_bool(
            row["distinguishability_passes"], "distinguishability_passes", carrier_id
        )
        rs = parse_bool(row["record_stability_passes"], "record_stability_passes", carrier_id)
        if rs != (substrate and capacity and distinguishability):
            fail(f"{carrier_id} has inconsistent record-stability conjunction")
        confining = json.loads(row["confining_subgroups"])
        status = row["delta_status"]
        if status == DELTA_UNDEFINED:
            if confining or row["delta_evaluated"] != "False":
                fail(f"{carrier_id} undefined Delta has confinement or is marked evaluated")
            if any(row[field] for field in ("delta_pair_count", "delta_witness_count", "delta_empty")):
                fail(f"{carrier_id} undefined Delta has fabricated value fields")
        elif status in {DELTA_CLEAN, DELTA_BREAKING}:
            if not confining or row["delta_evaluated"] != "True":
                fail(f"{carrier_id} evaluated Delta lacks confinement or evaluated flag")
            pair_count = int(row["delta_pair_count"])
            if (status == DELTA_CLEAN) != (pair_count == 0):
                fail(f"{carrier_id} Delta status disagrees with pair count")
            if (row["delta_empty"] == "True") != (pair_count == 0):
                fail(f"{carrier_id} delta_empty disagrees with pair count")
        else:
            fail(f"{carrier_id} has unknown delta_status: {status}")
        counterexample = parse_bool(
            row["prediction_counterexample"], "prediction_counterexample", carrier_id
        )
        if counterexample != (rs and status == DELTA_BREAKING):
            fail(f"{carrier_id} has inconsistent prediction_counterexample")

    table = derive_table(rows)
    if table != schema["corrected_table"]:
        fail(f"corrected table mismatch: {table} != {schema['corrected_table']}")
    headline = schema["headline"]
    derived_headline = {
        "RS_count": table["RS_true"]["total"],
        "RS_and_breaking_count": table["RS_true"][DELTA_BREAKING],
        "prediction_fails": table["RS_true"][DELTA_BREAKING] > 0,
        "breaking_total": sum(row["delta_status"] == DELTA_BREAKING for row in rows),
        "clean_total": sum(row["delta_status"] == DELTA_CLEAN for row in rows),
        "delta_undefined_total": sum(row["delta_status"] == DELTA_UNDEFINED for row in rows),
    }
    if headline != derived_headline:
        fail(f"headline mismatch: {derived_headline} != {headline}")

    for label, (all_count, exclusive_count) in derive_witness_counts(rows).items():
        recorded = schema["conjunct_breaking_witnesses"][label]
        if recorded["satisfying_and_breaking_count"] != all_count:
            fail(f"{label} conjunct breaking count mismatch")
        if recorded["exclusive_only_breaking_count"] != exclusive_count:
            fail(f"{label} exclusive-only breaking count mismatch")
        by_id = {row["carrier_id"]: row for row in rows}
        for key in ("witnesses", "exclusive_only_witnesses"):
            for witness in recorded[key]:
                row = by_id.get(witness["carrier_id"])
                if row is None or int(row["delta_pair_count"]) != witness["delta_pair_count"]:
                    fail(f"{label} {key} entry is not backed by the scores CSV: {witness}")
                field = {
                    "substrate": "substrate_passes",
                    "capacity": "capacity_passes",
                    "distinguishability": "distinguishability_passes",
                }[label]
                if row[field] != "True" or row["delta_status"] != DELTA_BREAKING:
                    fail(f"{label} {key} entry is not a breaking conjunct witness: {witness}")
                if key == "exclusive_only_witnesses":
                    other_fields = {
                        "substrate_passes",
                        "capacity_passes",
                        "distinguishability_passes",
                    } - {field}
                    if any(row[other] == "True" for other in other_fields):
                        fail(f"{label} exclusive-only witness satisfies another conjunct: {witness}")


def rederive_delta_exhaustive(rows: list[dict[str, str]]) -> dict[str, int]:
    evaluated = [row for row in rows if row["delta_evaluated"] == "True"]
    s41 = load_module("p3_full_delta_validate_s41", STEP41_BUILD)
    for row in evaluated:
        step41_row = {
            "dimensions": row["dimensions"],
            "support_key": row["support_key"],
            "confining_subgroups": row["max_confining_subgroup"],
            "broken_vector_exotic_count": row["transition_leak_count"],
        }
        support_index = int(row["carrier_id"].split("_")[-1])
        bosons = s41.build_bosons(step41_row, support_index)
        delta_pairs, witnesses = s41.compute_delta(bosons)
        if len(delta_pairs) != int(row["delta_pair_count"]):
            fail(f"{row['carrier_id']} exhaustive Delta pair count changed")
        if len(witnesses) != int(row["delta_witness_count"]):
            fail(f"{row['carrier_id']} exhaustive Delta witness count changed")
    undefined = [row for row in rows if row["delta_status"] == DELTA_UNDEFINED]
    if any(json.loads(row["confining_subgroups"]) for row in undefined):
        fail("a no-confinement negative control acquired a confinement factor")
    return {
        "delta_defined": len(evaluated),
        "RS": sum(row["record_stability_passes"] == "True" for row in evaluated),
        "breaking": sum(row["delta_status"] == DELTA_BREAKING for row in evaluated),
        "multi_confinement": sum(len(json.loads(row["confining_subgroups"])) > 1 for row in evaluated),
        "no_confinement_controls": len(undefined),
    }


def validate() -> None:
    if not SCHEMA_PATH.is_file():
        fail(f"missing required file: {SCHEMA_PATH.name}")
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    verify_files_and_hashes(schema)
    rows = read_rows(schema)
    verify_rows(rows, schema)
    coverage = rederive_delta_exhaustive(rows)
    expected_coverage = {
        "delta_defined": 10164,
        "RS": 24,
        "breaking": 918,
        "multi_confinement": 1203,
        "no_confinement_controls": 1826,
    }
    if coverage != expected_coverage:
        fail(f"unexpected exhaustive coverage: {coverage}")
    headline = schema["headline"]
    print(
        f"run_p3_full_carrier_delta.py: PASS: rows={len(rows)} "
        f"RS={headline['RS_count']} RS_breaking={headline['RS_and_breaking_count']} "
        f"delta_rederived={coverage['delta_defined']} "
        f"breaking_rederived={coverage['breaking']} "
        f"multi_rederived={coverage['multi_confinement']} "
        f"no_confinement_controls={coverage['no_confinement_controls']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="validate written artifacts")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    validate()


if __name__ == "__main__":
    main()
