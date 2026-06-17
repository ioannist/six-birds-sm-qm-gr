#!/usr/bin/env python3
"""Validator for Step 55 final generic frozen-carrier kernel test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


ARTIFACT_DIR = Path(__file__).resolve().parent
THREAD_DIR = ARTIFACT_DIR.parents[1]
BUILD_SCRIPT = ARTIFACT_DIR / "entanglement_underdetermines_geometry_step55.py"
STEP42_SCRIPT = THREAD_DIR / "steps/step42_faithful_holographic_rt_enrichment_artifacts/faithful_holographic_rt_enrichment_step42.py"
STEP44_SCRIPT = THREAD_DIR / "steps/step44_holographic_mmi_entropy_cone_artifacts/holographic_mmi_entropy_cone_step44.py"
EXPECTED_STEP42_SHA256 = "4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08"
EXPECTED_STEP44_SHA256 = "61f28d10e8170a9f37ac71a711b6d30c3dac9b4f014b8e634c70ba2166a47052"

REQUIRED = [
    "step55_results_summary.md",
    "step55_schema.json",
    "content_classification_step55.csv",
    "nonclaim_boundary_step55.md",
    "entanglement_underdetermines_geometry_statement_step55.tex",
    "run_step55.py",
    "entanglement_underdetermines_geometry_step55.py",
    "edge_weights_step55.csv",
    "fingerprint_summary_step55.csv",
    "generic_seed_summary_step55.csv",
    "clean_shadow_edges_step55.csv",
    "invisible_modes_characterization_step55.csv",
    "witness_pair_step55.csv",
    "control_injectivity_step55.csv",
    "frozen_machinery_step55.csv",
    "mode_b_constraint_ledger.csv",
    "mode_b_target_lineage.csv",
    "mode_b_grammar_manifest.csv",
]

STALE = [
    "shadow_recovery_example_step55.csv",
    "named_bulk_invariants_step55.csv",
    "geometric_quantities_step55.csv",
    "jacobian_kernel_step55.csv",
]

OVERCLAIM_PHRASES = [
    "disproves it-from-qubit in nature",
    "solves reconstruction",
    "derives holography",
    "frame transfer certified",
    "solves quantum gravity",
]


def fail(message: str) -> None:
    raise SystemExit(f"run_step55.py: FAIL: {message}")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def import_build():
    spec = importlib.util.spec_from_file_location("step55_build", BUILD_SCRIPT)
    if spec is None or spec.loader is None:
        fail("could not import build script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_required() -> None:
    missing = [name for name in REQUIRED if not (ARTIFACT_DIR / name).exists()]
    if missing:
        fail(f"missing artifacts: {', '.join(missing)}")
    stale_present = [name for name in STALE if (ARTIFACT_DIR / name).exists()]
    if stale_present:
        fail(f"stale artifacts present: {', '.join(stale_present)}")


def check_overclaims() -> None:
    text = "\n".join(
        (ARTIFACT_DIR / name).read_text(encoding="utf-8").lower()
        for name in [
            "step55_results_summary.md",
            "nonclaim_boundary_step55.md",
            "entanglement_underdetermines_geometry_statement_step55.tex",
        ]
    )
    for phrase in OVERCLAIM_PHRASES:
        if phrase in text:
            fail(f"overclaim phrase present: {phrase}")


def check_hashes() -> None:
    if sha256(STEP42_SCRIPT) != EXPECTED_STEP42_SHA256:
        fail("Step42 sha mismatch")
    if sha256(STEP44_SCRIPT) != EXPECTED_STEP44_SHA256:
        fail("Step44 sha mismatch")
    for row in read_csv(ARTIFACT_DIR / "frozen_machinery_step55.csv"):
        if row["sha256"] != row["expected_sha256"] or row["imported_verbatim"] != "True":
            fail("frozen machinery ledger mismatch")


def check_static() -> None:
    source = BUILD_SCRIPT.read_text(encoding="utf-8")
    if "forward_jacobian" in source:
        fail("one-sided forward Jacobian remains in build script")
    for snippet in ["central_jacobian", "generic_weights", "extract_step42_edges", "s42.bulk_graph"]:
        if snippet not in source:
            fail(f"missing required computation snippet: {snippet}")
    forbidden = ["bottle" + "neck", "hid" + "den", "par" + "allel", "chan" + "nel"]
    for row in read_csv(ARTIFACT_DIR / "edge_weights_step55.csv"):
        if row["edge_source"] != "step42_frozen_import":
            fail("edge source is not Step42 import")
        joined = " ".join(row.values()).lower()
        for token in forbidden:
            if token in joined:
                fail(f"answer-coded edge token present: {token}")


def recompute(build):
    s42 = build.import_module(build.STEP42_SCRIPT, "step42_recompute")
    s44 = build.import_module(build.STEP44_SCRIPT, "step44_recompute")
    labels = build.frozen_boundary_labels(s42)
    edge_pairs, base = build.extract_step42_edges(s42)
    spec = build.precompute_feature_spec(len(labels))
    seed_rows = []
    clean_counts = []
    for seed in build.GENERIC_SEEDS:
        weights = build.generic_weights(base, seed)
        if float(np.max(weights) - np.min(weights)) <= 1e-6:
            fail("generic geometry is degenerate")
        jacobian = build.central_jacobian(edge_pairs, weights, labels, spec, s44)
        rank, nullity, _s = build.rank_nullity(jacobian)
        shadows = build.clean_shadow_edges(edge_pairs, weights, labels, spec, s44)
        seed_rows.append((seed, rank, nullity, len(shadows)))
        clean_counts.append(len(shadows))
        for shadow in shadows:
            if float(shadow["max_both_direction_residual"]) >= build.FINGERPRINT_TOL:
                fail("clean shadow residual exceeds tolerance")
    control_labels, control_edges, control_weights = build.control_carrier()
    control_spec = build.precompute_feature_spec(len(control_labels))
    control_j = build.central_jacobian(control_edges, control_weights, control_labels, control_spec, s44)
    control_rank, control_nullity, _cs = build.rank_nullity(control_j)
    return {
        "seed_rows": seed_rows,
        "ranks": [row[1] for row in seed_rows],
        "nullities": [row[2] for row in seed_rows],
        "clean_counts": [row[3] for row in seed_rows],
        "control_rank": control_rank,
        "control_nullity": control_nullity,
        "feature_count": len(build.feature_vector(np.zeros(len(spec["region_masks"])), spec)),
        "region_count": len(spec["region_masks"]),
        "mi_count": len(spec["mi_pairs"]),
        "i3_count": len(spec["i3_triples"]),
    }


def check_schema(build) -> None:
    schema = load_json(ARTIFACT_DIR / "step55_schema.json")
    rec = recompute(build)
    if schema["carrier_source"] != "step42_frozen_perturbed_generic":
        fail("carrier source is not generic Step42 perturbation")
    if not schema["degenerate_point_rejected"]:
        fail("degenerate point not rejected")
    if not schema["central_difference"]:
        fail("central_difference flag not true")
    if schema["central_diff_rank"] != rec["ranks"]:
        fail("rank list mismatch")
    if schema["central_diff_nullity"] != rec["nullities"]:
        fail("nullity list mismatch")
    if schema["clean_shadow_edge_count_both_direction"] != rec["clean_counts"]:
        fail("clean shadow count mismatch")
    if schema["fingerprint_feature_count"] != rec["feature_count"]:
        fail("feature count mismatch")
    if schema["control_nullity"] != 0 or rec["control_nullity"] != 0:
        fail("control nullity is not zero")
    expected = "ENTANGLEMENT_DOES_NOT_DETERMINE_GEOMETRY_ITFROMQUBIT_FAILS" if min(rec["nullities"]) > 0 and min(rec["clean_counts"]) > 0 else "ENTANGLEMENT_DETERMINES_GEOMETRY_FORK_SHARP_FORM_FAILS"
    if schema["verdict"] != expected:
        fail("verdict not derived from nullity and clean-shadow count")
    witness = schema["witness"]
    if expected.endswith("FAILS"):
        if witness is None:
            fail("positive verdict lacks witness")
        if float(witness["plus_residual"]) >= 1e-9 or float(witness["minus_residual"]) >= 1e-9:
            fail("witness is not both-direction clean")
        if float(witness["geometric_gap"]) <= 1e-6:
            fail("witness geometric gap too small")


def check_tables() -> None:
    seed_rows = read_csv(ARTIFACT_DIR / "generic_seed_summary_step55.csv")
    if len(seed_rows) != 3:
        fail("expected three generic seeds")
    for row in seed_rows:
        if row["nondegenerate"] != "True" or row["central_difference"] != "True":
            fail("seed row missing nondegenerate central-difference flags")
        if int(row["jacobian_nullity"]) <= 0:
            fail("seed nullity not positive")
        if int(row["clean_shadow_edge_count_both_direction"]) <= 0:
            fail("seed clean-shadow count not positive")
    for row in read_csv(ARTIFACT_DIR / "invisible_modes_characterization_step55.csv"):
        if float(row["fingerprint_residual_plus"]) >= 1e-9:
            fail("invisible mode residual not clean")


def run_prior_self_checks() -> None:
    for rel_path in [
        "steps/step42_faithful_holographic_rt_enrichment_artifacts/run_step42.py",
        "steps/step44_holographic_mmi_entropy_cone_artifacts/run_step44.py",
    ]:
        cmd = [sys.executable, str(THREAD_DIR / rel_path), "--self"]
        result = subprocess.run(cmd, cwd=THREAD_DIR.parents[0], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if result.returncode != 0:
            fail(f"prior validator failed: {rel_path}\n{result.stdout}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--chain", action="store_true")
    args = parser.parse_args()
    if not args.self and not args.chain:
        parser.error("use --self or --chain")
    check_required()
    check_overclaims()
    check_hashes()
    check_static()
    build = import_build()
    check_schema(build)
    check_tables()
    if args.chain:
        run_prior_self_checks()
    print(f"run_step55.py: PASS ({'--chain' if args.chain else '--self'})")


if __name__ == "__main__":
    main()
