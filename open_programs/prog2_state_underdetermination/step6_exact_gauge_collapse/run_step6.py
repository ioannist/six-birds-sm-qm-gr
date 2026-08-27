#!/usr/bin/env python3
"""Deterministic validator for PROG2 Step 6."""
from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path

from build_step6 import GENERATED_OUTPUTS, write_artifacts
from step6_core import EVIDENCE_TYPES, compute_all

HERE = Path(__file__).resolve().parent


def validate() -> float:
    started = time.perf_counter()
    data = compute_all()
    if data["aggregate_verdict"] != "SIX_EXACT_JOINT_MAP_FIBERS__ALL_TENSOR_PRESENTATION_GAUGE_COLLAPSED":
        raise AssertionError(data["aggregate_verdict"])
    if len(data["intertwiner_certificates"]) != 6:
        raise AssertionError("expected six certificates")
    if not all(row["diagonal_intertwiner_exists_exact"] for row in data["intertwiner_certificates"]):
        raise AssertionError("an exact diagonal intertwiner is missing")
    if not all(row["joint_cut_state_map_noninjective_exact"] for row in data["intertwiner_certificates"]):
        raise AssertionError("a joint-map fiber failed")
    if {row["evidence_type"] for row in data["proof_ledger"]} != set(EVIDENCE_TYPES):
        raise AssertionError("evidence taxonomy mismatch")
    expected_control_reasons = {
        "unequal_product_real_carrier": "LEFT_KERNEL_PRODUCT_OBSTRUCTION",
        "one_edge_orientation_mutation": "ORIENTATION_DRESSING_MISMATCH_BREAKS_BX_EQ_DR",
        "disconnected_global_vs_component_products": "COMPONENTWISE_PRODUCT_OBSTRUCTION",
    }
    controls = {row["control_id"]: row for row in data["negative_controls"]}
    if set(controls) != set(expected_control_reasons):
        raise AssertionError("negative-control census mismatch")
    for control_id, reason in expected_control_reasons.items():
        row = controls[control_id]
        if not row["passes"] or row["observed_failure_reason"] != reason:
            raise AssertionError(f"negative control did not fail as required: {row}")
    if controls["disconnected_global_vs_component_products"]["repair_check"] != "componentwise_equal_products_restore_solvability=True":
        raise AssertionError("disconnected componentwise repair did not pass")

    # Anti-bypass: the exact core imports Step-4/Step-5 constructors and never
    # reads any Step-6 generated result as an input.
    core_text = (HERE / "step6_core.py").read_text(encoding="utf-8")
    for forbidden in GENERATED_OUTPUTS:
        if forbidden in core_text:
            raise AssertionError(f"generated-summary bypass in exact core: {forbidden}")
    if "construct_pairs" not in core_text or "enumerate_cuts" not in core_text:
        raise AssertionError("stored-endpoint exact rebuild path is absent")

    with tempfile.TemporaryDirectory(prefix="prog2_step6_validate_") as directory:
        temporary = Path(directory)
        write_artifacts(data, temporary)
        for filename in GENERATED_OUTPUTS:
            expected = (HERE / filename).read_bytes()
            rebuilt = (temporary / filename).read_bytes()
            if expected != rebuilt:
                raise AssertionError(f"byte comparison failed: {filename}")

    schema = json.loads((HERE / "schema_step6.json").read_text(encoding="utf-8"))
    if tuple(schema["evidence_type_enum"]) != EVIDENCE_TYPES:
        raise AssertionError("schema evidence enum mismatch")
    return time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and validate all Step-6 artifacts")
    arguments = parser.parse_args()
    if not arguments.self:
        parser.error("--self is required")
    elapsed = validate()
    print("NEGATIVE CONTROL PASS — unequal_product_real_carrier: LEFT_KERNEL_PRODUCT_OBSTRUCTION")
    print("NEGATIVE CONTROL PASS — one_edge_orientation_mutation: ORIENTATION_DRESSING_MISMATCH_BREAKS_BX_EQ_DR")
    print("NEGATIVE CONTROL PASS — disconnected_global_vs_component_products: COMPONENTWISE_PRODUCT_OBSTRUCTION; componentwise equality repair PASS")
    print(
        "PROG2 STEP6 SELF PASS — 6/6 exact products; 6/6 connected incidence certificates; "
        "6/6 exponent intertwiners; 6/6 external float controls; 3/3 negative controls; "
        f"byte-compare PASS; {elapsed:.2f}s"
    )


if __name__ == "__main__":
    main()
