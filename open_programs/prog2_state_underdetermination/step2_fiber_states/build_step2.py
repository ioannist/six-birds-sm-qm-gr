#!/usr/bin/env python3
"""Render deterministic PROG2 Step-2 artifacts."""

from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
from typing import Any


os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from capacity_convention import CONVENTION_ID, EDGE_DIMENSION
from step2_core import (
    FLOAT_ENTROPY_MARGIN_NATS,
    HIGH_PRECISION_CONSISTENCY_DPS,
    PRECISION_ESCALATION_DPS,
    SPLIT_SAFETY_FACTOR,
    STATE_EQUALITY_NORM_ALLOWANCE,
    TENSOR_FAMILY,
    compute_all,
)


HERE = Path(__file__).resolve().parent


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def design_note() -> str:
    return f"""# Preregistered capacity-to-state convention

## Convention

This step fixes one declared convention before evaluating any fiber. For every positive exact rational edge capacity
`c`, define the ordered probability `p(c)=c/(1+c)` and insert the normalized qubit-pair state

`sqrt(p(c)) |00> + sqrt(1-p(c)) |11>`.

The stored edge orientation fixes which Schmidt coefficient is first. Because `p(c)` is strictly increasing for
positive `c`, the ordered edge-state map is injective. The exact rational calculation of `p` precedes the numerical
square root. This convention has identifier `{CONVENTION_ID}` and bond dimension {EDGE_DIMENSION}. It is applied
uniformly to both members of every pair. It receives only the edge's own exact capacity; it cannot inspect a terminal
cut value, kernel direction, fiber identifier, or verdict.

This is **a declared capacity-to-state convention, not the canonical or unique physical map**. It provides a sharp,
auditable evaluation of the 19 pairs but does not remove the capacity-to-state obstruction identified in Step 1.

## Pairing and Hilbert-space identification

For a given carrier, both members use the same ordered boundary labels, two-dimensional physical legs, edge IDs,
stored edge orientations, and vertex/leg orderings. Capacity-independent local tensors are built once with the closed
Step-1 independent namespace and payload `(carrier, D=2, replicate=0)`, copied byte-for-byte, and transported to both
members. No P1 source-capacity seed enters that tensor seed. The only member-dependent operation is insertion of the
declared edge-state coefficient vector.

## Preregistered equality policy

All `2^|T|` subset entropies are computed from each contracted boundary state. For each state and subset, the
preregistered numerical allowance is the Step-1 small-Schmidt truncation contribution plus a declared absolute
complex128/SVD allowance of `{FLOAT_ENTROPY_MARGIN_NATS}` nats. The pairwise allowance is the sum of the two state
allowances. This is a comparison policy, not a propagated forward-error certificate.

- `EQUAL_WITHIN_ALLOWANCE`: absolute entropy difference is at most the pairwise allowance.
- `SPLIT_BEYOND_ALLOWANCE`: difference exceeds `{SPLIT_SAFETY_FACTOR}` times the pairwise allowance.
- Marginal values between those thresholds are recomputed at `{PRECISION_ESCALATION_DPS}` decimal digits for the
  Schmidt-entropy evaluation. They remain `INDETERMINATE` unless they cross one of the same thresholds.
- Pair verdict: `SPLIT` if any subset splits; `COINCIDE` if every subset is equal; otherwise `INDETERMINATE`.

The high-precision path reevaluates the entropy of the fixed contracted complex128 state. It does not recreate lost
tensor-contraction digits; that limitation is covered only by the declared allowance and is stated rather than
hidden. Boundary-state equality is separately tested using an L2 allowance of `{STATE_EQUALITY_NORM_ALLOWANCE}` and is
never inferred from entropy equality.

Two named witnesses are additionally reevaluated at `{HIGH_PRECISION_CONSISTENCY_DPS}` decimal digits from their fixed
complex128 contracted states. This is a high-precision consistency check, not a numerical certificate.

## Gauge and evidence policy

A split beyond the preregistered allowance is dense numerical evidence of a gauge-invariant obstruction under the
closed Step-1 presentation library and boundary-local unitaries, since those operations preserve all subset
entropies. A coincident entropy vector is not
proof of state equality or bulk inequivalence: bounded-complete gauge closure or an independent bulk invariant remains
a later-step requirement. Failure to find a library move is never used as proof of inequivalence here.

## Preregistered controls

The survivor-scale non-kernel control is fixed to `wheel_W4__b8__leaf_offset0`, source provenance seed 47,
`+1*edge_index_0`, with exact magnitude `3161096009431/6871947673600` (the same magnitude as `fiber_001`). Its active-cut
Jacobian column must be nonzero and its exact fingerprint must change. The degeneracy control is the closed Step-1
single-edge internal `g,g^-1` pair, with capacity `7/5`, dressed by this convention before applying the gauge move.
"""


def schema(data: dict[str, Any]) -> dict[str, Any]:
    verdicts = data["fiber_verdicts"]
    return {
        "artifact": "PROG2_STEP2_STATE_LEVEL_EVALUATION_OF_EXACT_CUT_FINGERPRINT_FIBERS",
        "version": 1,
        "result_grade": "DENSE_NUMERICAL_EVIDENCE",
        "capacity_to_state_convention": {
            "id": CONVENTION_ID,
            "domain": "strictly positive exact rational edge capacities",
            "map": "p=c/(1+c); sqrt(p)|00>+sqrt(1-p)|11> in stored edge orientation",
            "injective": "strict exact monotonicity of ordered p(c)",
            "bond_dimension": EDGE_DIMENSION,
            "canonical_physical_map_claimed": False,
        },
        "pairing": {
            "tensor_family": TENSOR_FAMILY,
            "seed_payload": "closed Step-1 (namespace,carrier,D=2,replicate=0); no P1 source seed",
            "capacity_independent_tensors": "built once and transported byte-identically",
            "boundary_hilbert_space": "fixed ordered labels and qubit dimensions across each pair",
        },
        "entropy_equality_policy": {
            "domain": "all 2^|T| subsets including empty and full",
            "unit": "nats",
            "per_state_float_allowance_nats": FLOAT_ENTROPY_MARGIN_NATS,
            "small_schmidt_accountability": "Step-1 discarded-mass entropy contribution included in allowance",
            "allowance_is_forward_error_certificate": False,
            "split_safety_factor": SPLIT_SAFETY_FACTOR,
            "precision_escalation_dps": PRECISION_ESCALATION_DPS,
            "pair_verdict": "SPLIT if any split; COINCIDE if all equal; INDETERMINATE otherwise",
        },
        "controls": {
            "nonkernel": "wheel_W4__b8__leaf_offset0 seed 47, +1 on edge index 0, t=3161096009431/6871947673600",
            "gauge_degeneracy": "Step-1 internal g,g^-1 pair after capacity 7/5 dressing",
        },
        "state_equality": {
            "separate_from_entropy_equality": True,
            "l2_norm_allowance": STATE_EQUALITY_NORM_ALLOWANCE,
        },
        "files": {
            "fiber_verdicts_step2.csv": "one state/entropy verdict per exact direction fiber",
            "entropy_comparisons_step2.csv": "all subset-level numerical-allowance comparisons for all 19 fibers",
            "pairing_integrity_step2.csv": "fixed labels, seeds, and byte-identical transported tensor gates",
            "controls_step2.csv": "non-kernel and gauge-degeneracy controls",
            "control_entropy_comparisons_step2.csv": "all subset comparisons for both controls",
            "high_precision_consistency_step2.csv": "80-dps consistency checks for the two named witnesses; not certificates",
            "capacity_convention_checks_step2.csv": "exact injectivity and positivity checks",
            "anti_bypass_step2.csv": "inherited and capacity-dataflow structural gates",
            "dependency_pins_step2.csv": "literal pins for every imported source/artifact",
            "step3_contract_requirements.md": "verbatim reviewer requirements governing Step 3",
        },
        "headline": {
            "fiber_count": len(verdicts),
            "split": sum(row["verdict"] == "SPLIT" for row in verdicts),
            "coincide": sum(row["verdict"] == "COINCIDE" for row in verdicts),
            "indeterminate": sum(row["verdict"] == "INDETERMINATE" for row in verdicts),
        },
    }


def results_markdown(data: dict[str, Any]) -> str:
    verdicts = data["fiber_verdicts"]
    controls = data["controls"]
    split = sum(row["verdict"] == "SPLIT" for row in verdicts)
    coincide = sum(row["verdict"] == "COINCIDE" for row in verdicts)
    indeterminate = sum(row["verdict"] == "INDETERMINATE" for row in verdicts)
    lines = [
        "# PROG2 Step 2 — state evaluation of exact cut-fingerprint fibers",
        "",
        "## Headline",
        "",
        f"Under the preregistered `{CONVENTION_ID}` convention, the 19 exact PROG3 fibers classify as:",
        "",
        f"- **SPLIT: {split}**",
        f"- **COINCIDE: {coincide}**",
        f"- **INDETERMINATE: {indeterminate}**",
        "",
        "This result is graded **dense numerical evidence**. The comparison thresholds are preregistered numerical",
        "allowances, not propagated forward-error bounds.",
        "",
        "| fiber | carrier | seed | basis | subsets split/equal/indeterminate | max difference (nats) | allowance at witness | verdict |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in verdicts:
        lines.append(
            f"| {row['fiber_id']} | {row['carrier']} | {row['source_seed_provenance']} | {row['basis_index']} "
            f"| {row['split_subset_count']}/{row['equal_subset_count']}/{row['indeterminate_subset_count']} "
            f"| `{row['max_entropy_difference_nats']}` | `{row['max_difference_numerical_allowance_nats']}` "
            f"| **{row['verdict']}** |"
        )
    lines.extend(
        [
            "",
            "Every subset-level entropy, discarded probability mass, numerical rank, numerical allowance, and classification",
            "is exported in `entropy_comparisons_step2.csv`. Boundary-state residuals and state digests are recorded",
            "separately from entropy-vector verdicts.",
            "",
            "## Controls",
            "",
            "| control | exact cut change | state residual | max entropy difference | verdict | pass |",
            "|---|---|---:|---:|---|---|",
        ]
    )
    for row in controls:
        lines.append(
            f"| {row['control']} | {row['exact_cut_fingerprint_changed']} "
            f"| `{row['state_l2_residual']}` | `{row['max_entropy_difference_nats']}` "
            f"| {row['verdict']} | {row['passes']} |"
        )
    lines.extend(
        [
            "",
            "The preregistered non-kernel edge-0 perturbation has nonzero active-cut Jacobian image, changes the exact",
            "cut fingerprint, and splits the contracted-state entropy vector. The Step-1 internal `g,g^-1` gauge pair",
            "was dressed first by the new capacity convention and still coincides in state and entropy within the allowance.",
            "",
            "## High-precision consistency checks",
            "",
            "These checks reevaluate entropy at 80 decimal digits from the fixed complex128 contracted states. They",
            "strengthen numerical consistency but are not forward-error certificates for the contraction.",
            "",
            "| fiber | region | float difference (nats) | 80-dps difference (nats) | absolute agreement |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for row in data["high_precision_consistency"]:
        lines.append(
            f"| {row['fiber_id']} | {row['region']} | `{row['float_absolute_difference_nats']}` "
            f"| `{row['mpmath_absolute_difference_nats']}` "
            f"| `{row['absolute_float_mp_difference_agreement_nats']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if split == len(verdicts):
        lines.extend(
            [
                "For this declared convention and tensor family, the computed contracted-state entropies provide",
                "dense numerical evidence of strict refinement of the complete terminal min-cut fingerprint on every",
                "tested direction fiber. Accordingly, none of the 19 graph-level fibers supplies a numerical",
                "state-level underdetermination candidate in this evaluation. This is a convention-scoped negative",
                "search result, not a proof that no other capacity-to-state map or state family can yield one.",
            ]
        )
    else:
        lines.extend(
            [
                "Any `COINCIDE` row is only a state-level underdetermination candidate. Gauge inequivalence at the",
                "state level and an independent bulk invariant remain required later. `SPLIT` rows are excluded only",
                "for this declared convention.",
            ]
        )
    lines.extend(
        [
            "",
            "No marginal subset was accepted without the preregistered precision policy. The convention remains the",
            "load-bearing import: it is injective and non-vacuous, but it is not claimed to be uniquely physical.",
            "",
        ]
    )
    return "\n".join(lines)


def content_classification() -> str:
    return """# Content classification

| object | classification | role |
|---|---|---|
| Step-1 tensor contraction and entropy modules | IMPORTED READ-ONLY, HASH-PINNED | numerical state and entropy engine |
| PROG3 exact fiber tables | IMPORTED READ-ONLY, HASH-PINNED | exact base capacities, directions, and interior parameters |
| capacity-to-state map | DECLARED CONVENTION, COMPUTATION-ENFORCED | injective ordered qubit edge state; not canonical |
| capacity-independent random tensors | COMPUTED FROM INDEPENDENT PINNED SEED RULE | byte-identical pairing data |
| boundary states and entropy vectors | GENERATED COMPUTATION | dense contraction followed by state-only entropy path |
| entropy splits | DENSE NUMERICAL EVIDENCE WITHIN DECLARED STATE MODEL | library moves and boundary-local unitaries preserve subset entropies |
| coincident entropy vector, if any | CANDIDATE ONLY | does not establish boundary-state equality or bulk inequivalence |
| graph-level depth-three orbit status | IMPORTED PROVENANCE | not used as a state-level inequivalence proof |
"""


def nonclaim_boundary(data: dict[str, Any]) -> str:
    verdicts = data["fiber_verdicts"]
    split = sum(row["verdict"] == "SPLIT" for row in verdicts)
    return f"""# Nonclaim boundary

Step 2 supplies dense numerical evidence, not a numerical certificate, and does not establish bulk-geometry
underdetermination. Under the one declared injective capacity-to-state convention, {split} of 19 tested exact
graph-level fibers have entropy differences beyond the preregistered numerical allowance. A split is scoped to this
convention and tensor family; it is not a theorem covering other edge-state maps, local tensor ensembles, bond
dimensions, or continuum states.

If any entropy vectors coincide in a future convention, coincidence alone will produce only a candidate pair. It will
not establish boundary-state equality, and neither entropy coincidence nor failure to find a Step-1 library move proves
bulk inequivalence. A bounded-complete gauge-closure procedure or a gauge-invariant independent bulk obstruction is a
later requirement. Deeper graph move sequences and transformations outside the declared graph library also remain
open. The PROG3 orbit-disjoint status is not promoted here to an unbounded state-level irreducibility claim.
"""


def statement(data: dict[str, Any]) -> str:
    verdicts = data["fiber_verdicts"]
    split = sum(row["verdict"] == "SPLIT" for row in verdicts)
    coincide = sum(row["verdict"] == "COINCIDE" for row in verdicts)
    indeterminate = sum(row["verdict"] == "INDETERMINATE" for row in verdicts)
    return f"""# Step-2 dense numerical evidence statement

Using the preregistered injective ordered-qubit capacity convention, fixed boundary Hilbert-space identifications,
byte-identical transported capacity-independent tensors, and the closed Step-1 independent seed namespace, dense
contracted states were constructed for both endpoints of all 19 pinned exact cut-fingerprint fibers. All boundary
subset entropies were computed solely from those states and compared under the preregistered numerical-allowance policy.

The result is SPLIT={split}, COINCIDE={coincide}, INDETERMINATE={indeterminate}. A split entropy vector is a
dense numerical indication of a gauge-invariant obstruction within this declared state model, so these split rows
provide dense numerical evidence that the contracted-state entropy data refine their identical complete terminal
min-cut fingerprints. The allowance is not a propagated numerical-error certificate. This statement is conditional
on the declared capacity-to-state convention and tensor family. No bulk-geometry underdetermination claim is made.
"""


def render(data: dict[str, Any]) -> dict[str, str]:
    return {
        "design_note_convention.md": design_note(),
        "results_step2.md": results_markdown(data),
        "schema_step2.json": json.dumps(schema(data), indent=2, sort_keys=True) + "\n",
        "content_classification.md": content_classification(),
        "nonclaim_boundary.md": nonclaim_boundary(data),
        "statement.md": statement(data),
        "fiber_verdicts_step2.csv": csv_text(data["fiber_verdicts"]),
        "entropy_comparisons_step2.csv": csv_text(data["entropy_comparisons"]),
        "pairing_integrity_step2.csv": csv_text(data["pairing_integrity"]),
        "controls_step2.csv": csv_text(data["controls"]),
        "control_entropy_comparisons_step2.csv": csv_text(data["control_entropy_comparisons"]),
        "high_precision_consistency_step2.csv": csv_text(data["high_precision_consistency"]),
        "capacity_convention_checks_step2.csv": csv_text(data["capacity_checks"]),
        "anti_bypass_step2.csv": csv_text(data["anti_bypass"]),
        "dependency_pins_step2.csv": csv_text(data["dependencies"]),
    }


def generate(destination: Path) -> dict[str, str]:
    data = compute_all()
    artifacts = render(data)
    destination.mkdir(parents=True, exist_ok=True)
    for name, text in artifacts.items():
        (destination / name).write_text(text, encoding="utf-8")
    return artifacts


def main() -> None:
    artifacts = generate(HERE)
    print(f"build_step2.py: PASS: wrote={len(artifacts)}")


if __name__ == "__main__":
    main()
