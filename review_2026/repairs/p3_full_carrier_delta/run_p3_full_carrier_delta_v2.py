#!/usr/bin/env python3
"""Exhaustive validator for P3-REPAIR-1b product-confinement artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import build_p3_full_carrier_delta_v2 as build


HERE = Path(__file__).resolve().parent
SCORES = HERE / build.V2_SCORES_NAME
FACTORS = HERE / build.V2_FACTORS_NAME
SCHEMA = HERE / build.V2_SCHEMA_NAME
FINDINGS = HERE / build.V2_FINDINGS_NAME
MANIFEST = HERE / build.V2_MANIFEST_NAME
REQUIRED = (SCORES, FACTORS, SCHEMA, FINDINGS, MANIFEST)


def fail(message: str) -> None:
    print(f"run_p3_full_carrier_delta_v2.py: FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path, expected_fields: list[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_fields:
            fail(f"unexpected CSV columns: {path.name}")
        return list(reader)


def parse_bool(value: str, field: str, carrier_id: str) -> bool:
    if value not in {"True", "False"}:
        fail(f"{carrier_id}: invalid {field}={value!r}")
    return value == "True"


def independent_factor_rows(dimensions: tuple[int, ...], reps: tuple[str, ...]) -> list[dict[str, Any]]:
    rows = []
    residual_labels = []
    raw = []
    for index, (dimension, rep) in enumerate(zip(dimensions, reps)):
        active = rep != "singlet"
        if active and dimension - 1 >= 2:
            residual = dimension - 1
            transitions = 2 * residual
            state = "active_broken_to_residual"
        elif active:
            residual = None
            transitions = 0
            state = "active_no_nonabelian_residual"
        else:
            residual = dimension
            transitions = 0
            state = "untouched"
        label = f"factor{index}"
        raw.append((index, label, dimension, rep, state, residual, transitions))
        if residual is not None:
            residual_labels.append(label)
    for index, label, dimension, rep, state, residual, transitions in raw:
        if residual is None:
            continue
        generators = residual * residual - 1
        projection = json.dumps(tuple("nontrivial_confining_charge" if other == label else "trivial"
                                      for other in residual_labels))
        rows.append({
            "factor_label": label,
            "factor_index": index,
            "original_dimension": dimension,
            "scalar_rep": rep,
            "factor_state": state,
            "residual_dimension": residual,
            "massless_generator_count": generators,
            "transition_vector_count": transitions,
            "interference_projection": projection,
            "delta_pair_count": generators * transitions,
            "delta_witness_count": transitions if generators and transitions else 0,
        })
    return rows


def validate() -> None:
    started = time.monotonic()
    missing = [path.name for path in REQUIRED if not path.is_file()]
    if missing:
        fail(f"missing files: {missing}")
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    if schema["input_pins"] != {
        str(build.STEP35_BUILD.relative_to(build.REPO_ROOT)): build.EXPECTED_STEP35_SHA256,
        build.V1_SCORES.name: build.EXPECTED_V1_SCORES_SHA256,
        build.V1_SCHEMA.name: build.EXPECTED_V1_SCHEMA_SHA256,
    }:
        fail("input pins differ from validator constants")
    build_hash = sha256_file(HERE / "build_p3_full_carrier_delta_v2.py")
    if schema["implementation_sha256"] != {"build_p3_full_carrier_delta_v2.py": build_hash}:
        fail("version-2 build implementation hash mismatch")

    expected_artifacts, expected_schema = build.build_artifacts()
    if expected_schema != schema:
        fail("schema differs from deterministic full recomputation")
    for name, data in expected_artifacts.items():
        if (HERE / name).read_bytes() != data:
            fail(f"artifact differs from deterministic full recomputation: {name}")

    scores = read_csv(SCORES, build.V2_SCORE_FIELDS)
    factor_rows = read_csv(FACTORS, build.FACTOR_FIELDS)
    historical = build.read_v1_rows()
    if len(scores) != 11990 or len(historical) != 11990:
        fail("carrier row count changed")
    expected_ids = [f"carrier_{index:05d}" for index in range(11990)]
    if [row["carrier_id"] for row in scores] != expected_ids:
        fail("version-2 carrier order changed")

    factors_by_id: dict[str, list[dict[str, str]]] = {}
    for row in factor_rows:
        factors_by_id.setdefault(row["carrier_id"], []).append(row)

    coverage = Counter()
    moved_ids = []
    for old, row in zip(historical, scores):
        carrier_id = row["carrier_id"]
        if old["carrier_id"] != carrier_id:
            fail(f"historical alignment changed at {carrier_id}")
        dimensions = tuple(int(value) for value in row["dimensions"].split("|"))
        reps = tuple(old["witness_scalar_reps"].split("x"))
        independent = independent_factor_rows(dimensions, reps)
        defined = bool(independent)
        pairs = sum(item["delta_pair_count"] for item in independent)
        witnesses = sum(item["delta_witness_count"] for item in independent)
        expected_status = build.DELTA_UNDEFINED if not defined else (
            build.DELTA_CLEAN if pairs == 0 else build.DELTA_BREAKING
        )
        if row["product_delta_status"] != expected_status:
            fail(f"{carrier_id}: independently rederived status changed")
        if parse_bool(row["product_delta_evaluated"], "product_delta_evaluated", carrier_id) != defined:
            fail(f"{carrier_id}: domain/evaluated flag mismatch")
        if defined:
            coverage["delta_defined"] += 1
            if int(row["product_delta_pair_count"]) != pairs:
                fail(f"{carrier_id}: independently rederived pair count changed")
            if int(row["product_delta_witness_count"]) != witnesses:
                fail(f"{carrier_id}: independently rederived witness count changed")
            if parse_bool(row["product_delta_empty"], "product_delta_empty", carrier_id) != (pairs == 0):
                fail(f"{carrier_id}: product delta_empty mismatch")
        else:
            coverage["no_confinement"] += 1
            if any(row[field] for field in ("product_delta_pair_count", "product_delta_witness_count",
                                            "product_delta_empty")):
                fail(f"{carrier_id}: undefined row fabricates Delta values")
        if old["record_stability_passes"] == "True":
            coverage["RS"] += 1
            if not defined or pairs != 0:
                fail(f"{carrier_id}: record-stable row is outside domain or breaking")
        if expected_status == build.DELTA_BREAKING:
            coverage["breaking"] += 1
        multi = len(independent) > 1
        if multi:
            coverage["multi"] += 1
            written = factors_by_id.get(carrier_id, [])
            if len(written) != len(independent):
                fail(f"{carrier_id}: missing per-factor rows")
            for expected, actual in zip(independent, sorted(written, key=lambda item: int(item["factor_index"]))):
                for field, value in expected.items():
                    if actual[field] != str(value):
                        fail(f"{carrier_id}: per-factor {field} mismatch: {actual[field]} != {value}")
        elif carrier_id in factors_by_id:
            fail(f"{carrier_id}: single/no-confinement row appears in multi-factor table")
        moved = build.binary_class(old["delta_status"]) != build.binary_class(expected_status)
        if parse_bool(row["binary_moved"], "binary_moved", carrier_id) != moved:
            fail(f"{carrier_id}: binary movement flag mismatch")
        if moved:
            moved_ids.append(carrier_id)

    expected_coverage = {"delta_defined": 10164, "no_confinement": 1826, "RS": 24,
                         "breaking": 918, "multi": 1203}
    if dict(coverage) != expected_coverage:
        fail(f"coverage census changed: {dict(coverage)}")
    if moved_ids or schema["binary_stability"] != {
        "moved_carrier_ids": [], "moved_count": 0, "stable": True,
    }:
        fail(f"binary stability failed: {moved_ids}")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for name, digest in manifest["files"].items():
        if sha256_file(HERE / name) != digest:
            fail(f"manifest hash mismatch: {name}")

    elapsed = time.monotonic() - started
    print("run_p3_full_carrier_delta_v2.py: PASS: "
          "rows=11990 delta_rederived=10164 RS_rederived=24 breaking_rederived=918 "
          "multi_rederived=1203 no_confinement_controls=1826 binary_moved=0 "
          f"elapsed_seconds={elapsed:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="exhaustively validate version-2 artifacts")
    args = parser.parse_args()
    if not args.self:
        fail("use --self")
    validate()


if __name__ == "__main__":
    main()
