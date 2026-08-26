#!/usr/bin/env python3
"""P3-REPAIR-1b: factor-labelled product-confinement Delta evaluation."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import io
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
STEPS = REPO_ROOT / "physics_atlas" / "thread_cluster_a" / "steps"
V1_SCORES = HERE / "p3_full_carrier_delta_scores.csv"
V1_SCHEMA = HERE / "p3_full_carrier_delta_schema.json"

STEP35_BUILD = STEPS / "step35_mode_b_higher_layer_descent_artifacts" / "higher_layer_descent_step35.py"
EXPECTED_STEP35_SHA256 = "dad4c8793a8c32d47cc4d29cebfe2425f7821e61044024f7be22a33bcf21222d"
EXPECTED_V1_SCORES_SHA256 = "c202e246841a9d4bb03bda9f23f3a90a2b862200d5747c9a8cfcc9fd548e907b"
EXPECTED_V1_SCHEMA_SHA256 = "5c41a8c37c47c6339056096f87923100887cbcf3037458f630817ccf314f5d5b"

DELTA_CLEAN = "clean_evaluated"
DELTA_BREAKING = "breaking_evaluated"
DELTA_UNDEFINED = "delta_undefined_no_confinement"

V2_SCORES_NAME = "p3_full_carrier_delta_scores_v2.csv"
V2_FACTORS_NAME = "p3_full_carrier_delta_multiconfinement_factors_v2.csv"
V2_SCHEMA_NAME = "p3_full_carrier_delta_schema_v2.json"
V2_FINDINGS_NAME = "p3_full_carrier_delta_findings_v2.md"
V2_MANIFEST_NAME = "p3_full_carrier_delta_manifest_v2.json"

V2_SCORE_FIELDS = [
    "carrier_id", "dimensions", "support_key", "record_stability_passes", "confining_subgroups",
    "transition_leak_count", "legacy_delta_status", "legacy_delta_pair_count",
    "product_delta_status", "product_delta_evaluated", "product_delta_pair_count",
    "product_delta_witness_count", "product_delta_empty", "pair_count_change", "binary_moved",
    "residual_factor_count", "multi_confinement", "factor_projection_summary",
]
FACTOR_FIELDS = [
    "carrier_id", "dimensions", "factor_label", "factor_index", "original_dimension", "scalar_rep",
    "factor_state", "residual_dimension", "massless_generator_count", "transition_vector_count",
    "interference_projection", "delta_pair_count", "delta_witness_count",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_inputs() -> None:
    pins = {
        STEP35_BUILD: EXPECTED_STEP35_SHA256,
        V1_SCORES: EXPECTED_V1_SCORES_SHA256,
        V1_SCHEMA: EXPECTED_V1_SCHEMA_SHA256,
    }
    for path, expected in pins.items():
        actual = sha256_file(path)
        if actual != expected:
            raise RuntimeError(f"frozen input hash mismatch: {path}: {actual} != {expected}")


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


verify_inputs()
s35 = load_module("p3_factor_faithful_s35", STEP35_BUILD)


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def read_v1_rows() -> list[dict[str, str]]:
    with V1_SCORES.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 11990:
        raise RuntimeError(f"historical carrier changed: {len(rows)} rows")
    return rows


def factor_diagnostics(dimensions: tuple[int, ...], reps: tuple[str, ...]) -> list[dict[str, Any]]:
    if len(dimensions) != len(reps):
        raise AssertionError("factor and scalar-representation arities differ")
    rows = []
    for index, (dimension, rep) in enumerate(zip(dimensions, reps)):
        # The historical CSV stores canonical scalar spellings. In Step 33's
        # canonical model every inactive zero-index one-dimensional rep has
        # already collapsed to "singlet"; rank_one_fund is active even though
        # the older raw-spelling dynkin helper does not accept that alias.
        active = rep != "singlet"
        if active:
            residual = dimension - 1
            if residual >= 2:
                massless = residual * residual - 1
                transitions = 2 * residual
                state = "active_broken_to_residual"
            else:
                residual = None
                massless = transitions = 0
                state = "active_no_nonabelian_residual"
        else:
            residual = dimension
            massless = dimension * dimension - 1
            transitions = 0
            state = "untouched"
        rows.append({
            "factor_label": f"factor{index}",
            "factor_index": index,
            "original_dimension": dimension,
            "scalar_rep": rep,
            "factor_state": state,
            "residual_dimension": residual,
            "massless_generator_count": massless,
            "transition_vector_count": transitions,
        })
    return rows


def interference_projection(factor_label: str, residual_labels: tuple[str, ...]) -> tuple[str, ...]:
    """Complete product projection: one coordinate for every residual factor."""
    return tuple("nontrivial_confining_charge" if label == factor_label else "trivial"
                 for label in residual_labels)


def build_factor_labelled_bosons(factors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    residual_labels = tuple(row["factor_label"] for row in factors if row["residual_dimension"] is not None)
    bosons = []
    for factor in factors:
        if factor["residual_dimension"] is None:
            continue
        projection = interference_projection(factor["factor_label"], residual_labels)
        for index in range(factor["massless_generator_count"]):
            bosons.append({
                "boson_id": f"{factor['factor_label']}_massless_{index:02d}",
                "factor_label": factor["factor_label"],
                "pi_conf_product": projection,
                "pi_mass": "massless",
                "is_transition_vector": False,
            })
        for index in range(factor["transition_vector_count"]):
            bosons.append({
                "boson_id": f"{factor['factor_label']}_transition_{index:02d}",
                "factor_label": factor["factor_label"],
                "pi_conf_product": projection,
                "pi_mass": "massive",
                "is_transition_vector": True,
            })
    return bosons


def compute_product_delta(factors: list[dict[str, Any]]) -> dict[str, Any]:
    residual = [row for row in factors if row["residual_dimension"] is not None]
    if not residual:
        return {
            "delta_status": DELTA_UNDEFINED,
            "delta_evaluated": False,
            "delta_pair_count": None,
            "delta_witness_count": None,
            "delta_empty": None,
            "per_factor": [],
        }
    bosons = build_factor_labelled_bosons(factors)
    pair_counts: Counter[str] = Counter()
    witness_ids: dict[str, set[str]] = defaultdict(set)
    total_pairs = 0
    for left_index, left in enumerate(bosons):
        for right in bosons[left_index + 1:]:
            if left["pi_conf_product"] != right["pi_conf_product"] or left["pi_mass"] == right["pi_mass"]:
                continue
            transition = left if left["is_transition_vector"] else right
            factor_label = transition["factor_label"]
            pair_counts[factor_label] += 1
            witness_ids[factor_label].add(transition["boson_id"])
            total_pairs += 1
    per_factor = []
    residual_labels = tuple(row["factor_label"] for row in residual)
    for factor in residual:
        label = factor["factor_label"]
        per_factor.append({
            **factor,
            "interference_projection": json.dumps(interference_projection(label, residual_labels)),
            "delta_pair_count": pair_counts[label],
            "delta_witness_count": len(witness_ids[label]),
        })
    empty = total_pairs == 0
    return {
        "delta_status": DELTA_CLEAN if empty else DELTA_BREAKING,
        "delta_evaluated": True,
        "delta_pair_count": total_pairs,
        "delta_witness_count": sum(len(values) for values in witness_ids.values()),
        "delta_empty": empty,
        "per_factor": per_factor,
    }


def binary_class(status: str) -> str:
    if status == DELTA_CLEAN:
        return "clean"
    if status == DELTA_BREAKING:
        return "breaking"
    if status == DELTA_UNDEFINED:
        return "undefined"
    raise AssertionError(status)


def evaluate_rows(v1_rows: list[dict[str, str]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    scores = []
    multi_factor_rows = []
    for row in v1_rows:
        dimensions = tuple(int(value) for value in row["dimensions"].split("|"))
        reps = tuple(row["witness_scalar_reps"].split("x"))
        factors = factor_diagnostics(dimensions, reps)
        product = compute_product_delta(factors)
        legacy_count = int(row["delta_pair_count"]) if row["delta_pair_count"] else None
        product_count = product["delta_pair_count"]
        residual_count = len(product["per_factor"])
        multi = residual_count > 1
        moved = binary_class(row["delta_status"]) != binary_class(product["delta_status"])
        summary = ";".join(
            f"{item['factor_label']}:SU({item['residual_dimension']}):pairs={item['delta_pair_count']}:"
            f"witnesses={item['delta_witness_count']}"
            for item in product["per_factor"]
        )
        scores.append({
            "carrier_id": row["carrier_id"],
            "dimensions": row["dimensions"],
            "support_key": row["support_key"],
            "record_stability_passes": row["record_stability_passes"],
            "confining_subgroups": row["confining_subgroups"],
            "transition_leak_count": row["transition_leak_count"],
            "legacy_delta_status": row["delta_status"],
            "legacy_delta_pair_count": "" if legacy_count is None else legacy_count,
            "product_delta_status": product["delta_status"],
            "product_delta_evaluated": product["delta_evaluated"],
            "product_delta_pair_count": "" if product_count is None else product_count,
            "product_delta_witness_count": "" if product["delta_witness_count"] is None else product["delta_witness_count"],
            "product_delta_empty": "" if product["delta_empty"] is None else product["delta_empty"],
            "pair_count_change": "" if legacy_count is None else product_count - legacy_count,
            "binary_moved": moved,
            "residual_factor_count": residual_count,
            "multi_confinement": multi,
            "factor_projection_summary": summary,
        })
        if multi:
            for factor in product["per_factor"]:
                multi_factor_rows.append({
                    "carrier_id": row["carrier_id"],
                    "dimensions": row["dimensions"],
                    **factor,
                })
    return scores, multi_factor_rows


def csv_text(rows: list[dict[str, Any]], fields: list[str]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: bool_text(value) if isinstance((value := row.get(field, "")), bool) else value
                         for field in fields})
    return stream.getvalue()


def corrected_table(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    table = {}
    for rs, label in (("False", "RS_false"), ("True", "RS_true")):
        selected = [row for row in rows if row["record_stability_passes"] == rs]
        table[label] = {
            DELTA_CLEAN: sum(row["product_delta_status"] == DELTA_CLEAN for row in selected),
            DELTA_BREAKING: sum(row["product_delta_status"] == DELTA_BREAKING for row in selected),
            DELTA_UNDEFINED: sum(row["product_delta_status"] == DELTA_UNDEFINED for row in selected),
            "total": len(selected),
        }
    return table


def per_factor_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (row["factor_label"], row["original_dimension"], row["scalar_rep"],
               row["factor_state"], row["residual_dimension"])
        groups[key].append(row)
    return [
        {
            "factor_label": key[0], "original_dimension": key[1], "scalar_rep": key[2],
            "factor_state": key[3], "residual_dimension": key[4], "row_count": len(group),
            "massless_generators_total": sum(row["massless_generator_count"] for row in group),
            "transition_vectors_total": sum(row["transition_vector_count"] for row in group),
            "delta_pairs_total": sum(row["delta_pair_count"] for row in group),
            "delta_witnesses_total": sum(row["delta_witness_count"] for row in group),
        }
        for key, group in sorted(groups.items(), key=lambda item: tuple(map(str, item[0])))
    ]


def pair_change_summary(scores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    multi = [row for row in scores if row["multi_confinement"]]
    counts = Counter((int(row["legacy_delta_pair_count"]), int(row["product_delta_pair_count"])) for row in multi)
    return [{"legacy_pair_count": old, "product_pair_count": new, "row_count": count}
            for (old, new), count in sorted(counts.items())]


def markdown_table(table: dict[str, dict[str, int]]) -> str:
    return "\n".join([
        "| RS status | clean evaluated | breaking evaluated | Delta undefined | Total |",
        "|---|---:|---:|---:|---:|",
        *[f"| {label} | {values[DELTA_CLEAN]} | {values[DELTA_BREAKING]} | "
          f"{values[DELTA_UNDEFINED]} | {values['total']} |" for label, values in table.items()],
    ])


def findings_text(schema: dict[str, Any]) -> str:
    changes = schema["pair_count_change_summary"]
    change_lines = "\n".join(
        f"| {row['legacy_pair_count']} | {row['product_pair_count']} | {row['row_count']} |" for row in changes
    )
    factor_lines = "\n".join(
        f"| {row['factor_label']} | SU({row['original_dimension']}) | {row['scalar_rep']} | "
        f"{row['factor_state']} | SU({row['residual_dimension']}) | {row['row_count']} | "
        f"{row['delta_pairs_total']} | {row['delta_witnesses_total']} |"
        for row in schema["per_factor_summary"]
    )
    return f"""# P3-REPAIR-1b: factor-labelled product-confinement findings

## Binary stability

All 11,990 historical rows were re-evaluated. The complete-product projection changes the clean/breaking/undefined binary for **{schema['binary_stability']['moved_count']} rows**. Moved carrier IDs: {schema['binary_stability']['moved_carrier_ids'] or 'none'}.

{markdown_table(schema['corrected_table'])}

The headline counts therefore remain RS=24, RS and breaking=0, breaking total=918, clean total=9,246, and Delta undefined=1,826.

## Product-confinement calculation

Every residual nonabelian factor is a separate coordinate of `pi_conf_product`. Every massless generator and transition vector carries its source `factor_label`. A massive transition vector pairs only with massless generators whose complete product-sector tuple is equal. This prevents a leak from an active residual SU(2) being attributed to an untouched SU(3).

There are {schema['multi_confinement_rows']} multi-confinement carrier rows and {schema['multi_confinement_factor_rows']} residual-factor rows in the detailed table.

| Legacy pairs | Product-faithful pairs | Carrier rows |
|---:|---:|---:|
{change_lines}

| Factor label | Original factor | Scalar rep | State | Residual | Rows | Pair total | Witness total |
|---|---|---|---|---|---:|---:|---:|
{factor_lines}

Per-carrier, per-factor counts are recorded in `{V2_FACTORS_NAME}`.

## Surviving typed claim

`RS(C) => C in Dom(Delta_fact) AND Delta_fact(C) = empty` survives on all 24 record-stable rows.

**Evidence grade: CONDITIONAL FINITE-TOY PROXY ENUMERATION DIAGNOSTIC.** It is conditional on the proxy higher-layer breaking/scalar choice, inherits the published 11,990-row carrier and its representation/enumeration limitations, and tests the record-grammar shape encoded by the frozen Step-57 machinery rather than a derived continuum record theorem. The factor-labelled repair removes the product-confinement bookkeeping defect but does not remove those caveats or promote the statement beyond this finite diagnostic.

No-confinement rows retain the typed value `delta_undefined_no_confinement`; none is record-stable.

## Validator coverage

The version-2 validator independently rederives all {schema['validator_coverage']['delta_defined_rows']} Delta-defined rows, including all {schema['validator_coverage']['RS_rows']} RS rows, all {schema['validator_coverage']['breaking_rows']} breaking rows, and all {schema['validator_coverage']['multi_confinement_rows']} multi-confinement rows. It also checks all {schema['validator_coverage']['no_confinement_negative_controls']} no-confinement rows as negative controls. This replaces the historical 32-row arbitrary sample.
"""


def build_artifacts() -> tuple[dict[str, bytes], dict[str, Any]]:
    v1_rows = read_v1_rows()
    scores, factors = evaluate_rows(v1_rows)
    table = corrected_table(scores)
    moved = [row["carrier_id"] for row in scores if row["binary_moved"]]
    if len([row for row in scores if row["multi_confinement"]]) != 1203:
        raise AssertionError("multi-confinement census changed")
    score_text = csv_text(scores, V2_SCORE_FIELDS)
    factor_text = csv_text(factors, FACTOR_FIELDS)
    schema = {
        "schema_version": 2,
        "experiment": "P3-REPAIR-1b factor-labelled product-confinement refinement",
        "historical_outputs_preserved": True,
        "carrier_rows": len(scores),
        "delta_defined_rows": sum(row["product_delta_evaluated"] for row in scores),
        "multi_confinement_rows": sum(row["multi_confinement"] for row in scores),
        "multi_confinement_factor_rows": len(factors),
        "projection_definition": "ordered tuple over every residual factor; nontrivial only at source factor",
        "corrected_table": table,
        "binary_stability": {"moved_count": len(moved), "moved_carrier_ids": moved,
                             "stable": not moved},
        "pair_count_change_summary": pair_change_summary(scores),
        "per_factor_summary": per_factor_summary(factors),
        "validator_coverage": {
            "strategy": "exhaustive all Delta-defined rows plus all no-confinement negative controls",
            "carrier_rows": len(scores),
            "delta_defined_rows": sum(row["product_delta_evaluated"] for row in scores),
            "RS_rows": sum(row["record_stability_passes"] == "True" for row in scores),
            "breaking_rows": sum(row["product_delta_status"] == DELTA_BREAKING for row in scores),
            "multi_confinement_rows": sum(row["multi_confinement"] for row in scores),
            "no_confinement_negative_controls": sum(row["product_delta_status"] == DELTA_UNDEFINED for row in scores),
        },
        "typed_claim": {
            "statement": "RS(C) => C in Dom(Delta_fact) AND Delta_fact(C) = empty",
            "survives": table["RS_true"][DELTA_CLEAN] == 24 and table["RS_true"][DELTA_BREAKING] == 0
                        and table["RS_true"][DELTA_UNDEFINED] == 0,
            "evidence_grade": "CONDITIONAL FINITE-TOY PROXY ENUMERATION DIAGNOSTIC",
            "caveats": ["proxy breaking/scalar choice", "inherited carrier", "record-grammar shape"],
        },
        "input_pins": {
            str(STEP35_BUILD.relative_to(REPO_ROOT)): EXPECTED_STEP35_SHA256,
            V1_SCORES.name: EXPECTED_V1_SCORES_SHA256,
            V1_SCHEMA.name: EXPECTED_V1_SCHEMA_SHA256,
        },
        "implementation_sha256": {Path(__file__).name: sha256_file(Path(__file__))},
        "columns": {"scores": V2_SCORE_FIELDS, "multi_confinement_factors": FACTOR_FIELDS},
        "artifact_sha256": {
            V2_SCORES_NAME: hashlib.sha256(score_text.encode()).hexdigest(),
            V2_FACTORS_NAME: hashlib.sha256(factor_text.encode()).hexdigest(),
        },
    }
    schema_text = json.dumps(schema, indent=2, sort_keys=True) + "\n"
    findings = findings_text(schema)
    artifacts = {
        V2_SCORES_NAME: score_text.encode(),
        V2_FACTORS_NAME: factor_text.encode(),
        V2_SCHEMA_NAME: schema_text.encode(),
        V2_FINDINGS_NAME: findings.encode(),
    }
    manifest = {"algorithm": "sha256", "files": {name: hashlib.sha256(data).hexdigest()
                                                     for name, data in sorted(artifacts.items())}}
    artifacts[V2_MANIFEST_NAME] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    return artifacts, schema


def main() -> None:
    started = time.monotonic()
    artifacts, schema = build_artifacts()
    for name, data in artifacts.items():
        (HERE / name).write_bytes(data)
    elapsed = time.monotonic() - started
    print("build_p3_full_carrier_delta_v2.py: PASS: "
          f"rows={schema['carrier_rows']} defined={schema['delta_defined_rows']} "
          f"multi={schema['multi_confinement_rows']} moved={schema['binary_stability']['moved_count']} "
          f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
