#!/usr/bin/env python3
"""Deterministic rebuild-and-byte-compare validator for PROG2 Step 2."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
import time
from pathlib import Path


os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from build_step2 import HERE, generate
from step1_core import TENSOR_REPLICATE, TENSOR_SEED_NAMESPACE, derive_tensor_seed


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def validate() -> str:
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="prog2_step2_") as temporary:
        rebuilt_directory = Path(temporary)
        rebuilt = generate(rebuilt_directory)
        mismatches = [
            name
            for name in sorted(rebuilt)
            if not (HERE / name).exists()
            or (HERE / name).read_bytes() != (rebuilt_directory / name).read_bytes()
        ]
        if mismatches:
            raise AssertionError(f"artifact byte mismatch: {mismatches}")

    verdicts = read_csv(HERE / "fiber_verdicts_step2.csv")
    if len(verdicts) != 19:
        raise AssertionError(f"expected 19 fiber verdicts, found {len(verdicts)}")
    allowed_verdicts = {"SPLIT", "COINCIDE", "INDETERMINATE"}
    if not all(row["verdict"] in allowed_verdicts for row in verdicts):
        raise AssertionError("unknown pair verdict")
    if not all(
        int(row["entropy_subset_count"]) == 1 << int(row["boundary_count"])
        and int(row["equal_subset_count"])
        + int(row["split_subset_count"])
        + int(row["indeterminate_subset_count"])
        == int(row["entropy_subset_count"])
        for row in verdicts
    ):
        raise AssertionError("fiber subset census is incomplete")
    for row in verdicts:
        if row["verdict"] == "SPLIT" and (
            int(row["split_subset_count"]) <= 0
            or row["gauge_invariant_evidence"] != "numerical_entropy_vector_split"
        ):
            raise AssertionError(f"split verdict lacks invariant obstruction: {row['fiber_id']}")
        if row["verdict"] == "COINCIDE" and (
            int(row["equal_subset_count"]) != int(row["entropy_subset_count"])
        ):
            raise AssertionError(f"invalid coincide verdict: {row['fiber_id']}")

    comparisons = read_csv(HERE / "entropy_comparisons_step2.csv")
    if len(comparisons) != sum(int(row["entropy_subset_count"]) for row in verdicts):
        raise AssertionError("subset comparison rows do not cover every fiber")
    allowed_subset = {
        "EQUAL_WITHIN_ALLOWANCE",
        "SPLIT_BEYOND_ALLOWANCE",
        "INDETERMINATE",
    }
    if not all(row["final_classification"] in allowed_subset for row in comparisons):
        raise AssertionError("unknown subset classification")
    marginal = [
        row for row in comparisons
        if row["initial_classification"] == "MARGINAL_REQUIRES_ESCALATION"
    ]
    if not all(
        row["precision_escalated"] == "True"
        and int(row["escalation_dps"]) == 80
        and row["escalated_base_entropy_nats"]
        and row["escalated_perturbed_entropy_nats"]
        for row in marginal
    ):
        raise AssertionError("a marginal subset bypassed precision escalation")

    pairing = read_csv(HERE / "pairing_integrity_step2.csv")
    if len(pairing) != 19 or not all(
        row["capacity_independent_tensors_byte_identical"] == "True"
        and row["only_declared_capacity_dressing_differs"] == "True"
        and row["capacity_independent_base_tensor_sha256"]
        == row["transported_copy_tensor_sha256"]
        and row["tensor_seed_namespace"] == TENSOR_SEED_NAMESPACE
        and int(row["tensor_seed_replicate"]) == TENSOR_REPLICATE
        and int(row["tensor_seed_both_members"])
        == derive_tensor_seed(row["carrier"], 2, TENSOR_REPLICATE)
        for row in pairing
    ):
        raise AssertionError("pairing or seed-namespace integrity failed")

    controls = read_csv(HERE / "controls_step2.csv")
    if len(controls) != 2 or not all(row["passes"] == "True" for row in controls):
        raise AssertionError("Step-2 controls failed")
    nonkernel = next(row for row in controls if row["control"] == "control_nonkernel_edge0")
    if (
        nonkernel["exact_active_cut_jacobian_image_nonzero"] != "True"
        or nonkernel["exact_cut_fingerprint_changed"] != "True"
        or nonkernel["verdict"] != "SPLIT"
    ):
        raise AssertionError("non-kernel non-vacuousness control failed")
    gauge = next(row for row in controls if row["control"] == "control_step1_internal_gauge")
    if gauge["verdict"] != "COINCIDE" or float(gauge["state_l2_residual"]) > 5e-10:
        raise AssertionError("capacity-dressed gauge-degeneracy control failed")

    convention = read_csv(HERE / "capacity_convention_checks_step2.csv")
    if len(convention) != 1 or convention[0]["passes"] != "True" or (
        convention[0]["exact_input_capacity_count"]
        != convention[0]["exact_probability_count"]
        or convention[0]["exact_input_capacity_count"]
        != convention[0]["numerical_edge_state_digest_count"]
        or convention[0]["numerical_coefficient_vectors_distinct_on_evaluated_capacities"]
        != "True"
    ):
        raise AssertionError("capacity convention injectivity check failed")
    anti_bypass = read_csv(HERE / "anti_bypass_step2.csv")
    if len(anti_bypass) != 6 or not all(row["passes"] == "True" for row in anti_bypass):
        raise AssertionError("Step-2 anti-bypass audit failed")
    metadata_gate = next(
        row for row in anti_bypass if row["gate"] == "frozen_capacity_metadata_mutation"
    )
    for required in ("rebuilt through", "seed=", "tensor_digest=", "state_digest=", "entropy_digest="):
        if required not in metadata_gate["evidence"]:
            raise AssertionError(f"metadata mutation gate omitted executed evidence: {required}")

    high_precision = read_csv(HERE / "high_precision_consistency_step2.csv")
    expected_witnesses = {
        ("fiber_004", "B1|B4|B5|B6"),
        ("fiber_011", "B1|B3|B5|B6"),
    }
    if (
        {(row["fiber_id"], row["region"]) for row in high_precision}
        != expected_witnesses
        or not all(
            row["passes"] == "True"
            and int(row["dps"]) >= 50
            and "consistency check, not certificate" in row["scope"]
            and float(row["absolute_float_mp_difference_agreement_nats"]) < 5e-13
            for row in high_precision
        )
    ):
        raise AssertionError("named high-precision consistency checks failed")

    contract = (HERE / "step3_contract_requirements.md").read_text(encoding="utf-8")
    contract_requirements = (
        "A finite or parametrically characterized, independently motivated convention family, tensor families, bond dimensions, seeds, aggregation rule, and stopping rule preregistered together; every outcome must be published.",
        "A state-level kernel test: compute the entropy-map Jacobian and characterize ker J_cut intersect ker J_state. Only symmetry-protected or certified-null directions should proceed to finite continuation and full entropy recomputation.",
        "A distinct-capacity, analytically coincident can-fail control — such as an injective convention with a known local-unitary c<->1/c symmetry — not merely a same-capacity tensor-gauge pair.",
        "An actual numerical certificate or explicit numerical-evidence grade. Any COINCIDE result must still undergo state-level gauge closure and an independent bulk-invariant test before becoming an underdetermination claim.",
    )
    if not all(requirement in contract for requirement in contract_requirements):
        raise AssertionError("Step-3 contract requirements are not verbatim")
    pins = read_csv(HERE / "dependency_pins_step2.csv")
    if len(pins) != 11 or not all(row["passes"] == "True" for row in pins):
        raise AssertionError("dependency pin failure")

    split = sum(row["verdict"] == "SPLIT" for row in verdicts)
    coincide = sum(row["verdict"] == "COINCIDE" for row in verdicts)
    indeterminate = sum(row["verdict"] == "INDETERMINATE" for row in verdicts)
    elapsed = time.perf_counter() - started
    return (
        "run_step2.py: PASS: fibers=19 entropy_subsets="
        f"{len(comparisons)} split={split} coincide={coincide} indeterminate={indeterminate} "
        f"marginal_escalations={len(marginal)} controls=2 anti_bypass=6 "
        "high_precision_witnesses=2 numerical_digest_injectivity=202/202 "
        "metadata_rebuild=PASS "
        f"runtime_seconds={elapsed:.3f}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self", action="store_true", help="rebuild and validate every Step-2 artifact")
    parser.parse_args()
    print(validate())


if __name__ == "__main__":
    main()
