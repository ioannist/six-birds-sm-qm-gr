#!/usr/bin/env python3
"""Write deterministic PROG2 Step-1 artifacts from pure computations."""

from __future__ import annotations

import csv
import json
import os
from collections import Counter
from io import StringIO
from pathlib import Path
from typing import Any

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from step1_core import (
    CONTROL_TOL,
    SCHMIDT_PROBABILITY_TOL,
    SURVIVOR_DIMS,
    TENSOR_SEED_NAMESPACE,
    compute_all,
)


HERE = Path(__file__).resolve().parent


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        raise ValueError("cannot render empty CSV")
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def schema() -> dict[str, Any]:
    return {
        "artifact": "PROG2_STEP1_EXPLICIT_DENSE_NUMERICAL_CONTRACTED_STATE_ENTROPY_ENGINE",
        "version": 2,
        "numerical_scope": "complex128 dense contraction and SVD; not exact arithmetic",
        "entropy_unit": "natural_logarithm_nats",
        "control_tolerance": CONTROL_TOL,
        "schmidt_probability_tolerance": SCHMIDT_PROBABILITY_TOL,
        "entropy_policy": {
            "reported_entropy": "includes every strictly positive numerical Schmidt probability",
            "tolerance_role": "diagnostic numerical rank and hypothetical truncation accountability only",
            "accountability": "discarded mass, numerical rank, tolerance sweep, and Audenaert-style classical entropy continuity bound",
            "error_bound_scope": "bounds hypothetical probability truncation only; does not certify floating-point SVD roundoff",
        },
        "tensor_seed_namespace": {
            "name": TENSOR_SEED_NAMESPACE,
            "payload": ["namespace", "carrier_name_without_P1_seed", "bond_dimension", "replicate"],
            "source_capacity_seed_in_payload": False,
        },
        "certified_survivor_bond_dimensions": list(SURVIVOR_DIMS),
        "tensor_families": {
            "structured_copy": "deterministic equality/copy tensor; equal incident dimensions required",
            "seeded_random_complex": "independent normalized complex Gaussian tensor at every vertex, deterministic SHA-derived local seeds",
        },
        "carrier": {
            "vertices": "labelled tensor vertices",
            "edges": "edge_id,u,v,positive integer bond dimension,optional source-weight provenance",
            "boundaries": "ordered label,vertex,positive integer physical dimension",
        },
        "entropy_vector": {
            "domain": "all 2^|T| boundary subsets including empty and full",
            "method": "dense numerical SVD of the normalized contracted boundary state",
            "anti_bypass": "complete reachable entropy call graph imports no graph/cut module and accepts no graph/capacity/cut argument",
        },
        "files": {
            "control_summary_step1.csv": "injective and degeneracy control verdicts",
            "control_entropy_vectors_step1.csv": "all four subset entropies for both injective cases and the gauge-related case",
            "gauge_verifications_step1.csv": "state and entropy residuals for every certified presentation move",
            "survivor_tractability_step1.csv": "full-vector contraction census on all 13 P1-v3 survivors",
            "resource_envelope_step1.csv": "declared dense-runtime envelope",
            "anti_bypass_step1.csv": "structural isolation checks",
            "dependency_pins_step1.csv": "literal source/data pins",
            "engine_checks_step1.csv": "heterogeneous per-edge bond-dimension contraction check",
            "seed_namespace_change_step1.csv": "legacy coupled versus independent tensor seeds and entropy digests",
            "legacy_seed_history_step1.csv": "pinned pre-fix digests; read as history only and never used to construct tensors",
            "entropy_numerical_accountability_step1.csv": "small-Schmidt tolerance sweep, discarded mass, ranks, and error bounds",
            "survivor_scale_control_step1.csv": "same-boundary-space D=2 survivor mutation control",
            "seed_independence_regression_step1.csv": "source-seed/source-weight provenance mutation",
            "review_regressions_step1.csv": "three reviewer-required regression verdicts",
            "step2_contract_requirements.md": "verbatim reviewer contract for the next step",
        },
    }


def results_markdown(data: dict[str, Any]) -> str:
    headline = data["controls"]["headline"]
    gauge_rows = data["controls"]["gauge_rows"]
    census = data["survivor_census"]
    counts = Counter((row["tensor_family"], row["bond_dimension"]) for row in census)
    unique_carriers = {(row["carrier"], row["source_seed"]) for row in census}
    maximum_complement = max(float(row["complement_symmetry_residual"]) for row in census)
    heterogeneous = data["engine_checks"][0]
    lines = [
        "# PROG2 Step 1 — explicit dense numerical contracted-state entropy engine",
        "",
        "## What was computed",
        "",
        "A labelled finite tensor network is built from explicit dense vertex tensors and contracted over every internal",
        "bond. The normalized result is an explicit tensor on the ordered boundary Hilbert space. The entropy module then",
        "computes numerical reduced-state spectra from that tensor alone, for all boundary subsets. It has no graph, capacity,",
        "area, or cut input. The deterministic family uses copy tensors; the random family uses fixed seeded complex",
        "Gaussian tensors. Natural logarithms and complex128/SVD numerics are used throughout; this is not exact arithmetic.",
        "",
        "The continuous weights of the P1-v3 cut carriers are retained as provenance, not coerced into Hilbert-space",
        "dimensions. Every tensor edge instead carries an explicit positive integer bond dimension. The survivor census",
        "uses uniform D=2,3,4 so topology is held fixed while state-space size changes.",
        f"Random survivor tensors use the independent namespace `{TENSOR_SEED_NAMESPACE}` with payload",
        "`(namespace, carrier_name, D, replicate)`. The P1 capacity seed remains provenance and is absent from that payload.",
        f"A separate heterogeneous check contracts edge dimensions `{heterogeneous['edge_dimensions']}` to a boundary",
        f"state of shape `{heterogeneous['contracted_state_shape']}` and computes all `{heterogeneous['entropy_subset_count']}` subsets.",
        "",
        "## Calibration controls",
        "",
        "Boundary order below is `[EMPTY, A, B, AB]`.",
        "",
        f"- Entangled-edge structured contraction: `{[f'{x:.15g}' for x in headline['entangled_vector']]}` nats.",
        f"- Disconnected structured contraction: `{[f'{x:.15g}' for x in headline['product_vector']]}` nats.",
        f"- Internal-gauge transformed contraction: `{[f'{x:.15g}' for x in headline['gauged_vector']]}` nats.",
        f"- `ln(2) = {headline['ln2']:.15g}`. The entangled and product Schmidt ranks across A|B are 2 and 1.",
        f"- Maximum injective-control entropy difference: `{float(data['controls']['control_summary'][0]['max_entropy_vector_difference']):.15g}` nats.",
        f"- Gauge-pair state residual: `{headline['gauge_state_residual']:.15g}`; entropy-vector residual: `{data['controls']['control_summary'][1]['max_entropy_vector_difference']}`.",
        "",
        "The different Schmidt ranks prove that the injective pair cannot be related by the implemented internal gauge,",
        "algebraic tensor merges, or single-boundary local unitaries. Thus the engine does distinguish at least one bulk",
            "difference. Conversely, the explicit g/g^-1 pair is a certified degeneracy control.",
            "",
            "## Reviewer-fix regressions",
            "",
            f"- Seed namespace: all `{len(data['seed_namespace_changes'])}` random survivor rows changed state and entropy",
            "  digests relative to the legacy source-seed-coupled tensors, both against the actual pre-fix entropy policy",
            "  and with both tensor families evaluated under the corrected policy. This is expected because the tensors are new. Mutating the stored P1",
            "  seed provenance and every frozen carrier `source_weight` while holding topology and tensor seed fixed leaves",
            f"  state and entropy digests unchanged (`{data['seed_independence'][0]['baseline_state_sha256']}` and",
            f"  `{data['seed_independence'][0]['baseline_entropy_sha256']}`).",
            "- Small Schmidt weight: the state with probabilities `(1-1e-14, 1e-14)` reports entropy",
            f"  `{data['numerical_accountability'][3]['reported_untruncated_entropy_nats']}` nats at tolerance `1e-13`,",
            f"  numerical rank `{data['numerical_accountability'][3]['numerical_rank']}`, discarded diagnostic mass",
            f"  `{data['numerical_accountability'][3]['discarded_probability_mass']}`, and truncation-error bound",
            f"  `{data['numerical_accountability'][3]['truncation_entropy_error_bound_nats']}` nats. The reported entropy",
            "  includes the small probability; the tolerance only diagnoses a hypothetical truncation. The bound covers",
            "  truncation error, not floating-point SVD roundoff.",
            "- Boundary unitary: a nonsymmetric complex unitary is applied conventionally as `U|psi>`. The network",
            "  contraction agrees with the independently written `np.einsum('ij,jb->ib', U, psi)` expectation.",
            "",
            "The complete tolerance sweep is in `entropy_numerical_accountability_step1.csv`; all legacy/new entropy",
            "digests are in `seed_namespace_change_step1.csv`.",
        "",
        "## State-level gauge library",
        "",
        "| move | certified relation | state residual | entropy residual |",
        "|---|---|---:|---:|",
    ]
    lines.extend(
        f"| {row['move']} | {row['relation']} | {row['state_residual']} | {row['entropy_vector_residual']} |"
        for row in gauge_rows
    )
    lines.extend(
        [
            "",
            "Internal g/g^-1 cancellation, a boundary-free bivalent series merge, and a parallel-index product merge",
            "leave the contracted boundary state invariant to machine precision. The fourth move applies an explicit",
            "unitary to one boundary leg; the recomputed state equals that local-unitary action and the full entropy vector",
            "is unchanged.",
            "",
            "## Survivor-scale same-boundary control",
            "",
            f"On `{data['survivor_scale_control'][0]['carrier']}` at D=2 with `{data['survivor_scale_control'][0]['boundary_count']}`",
            f"boundary legs, the explicit mutation `{data['survivor_scale_control'][0]['mutation']}` changes the entropy",
            f"vector by `{data['survivor_scale_control'][0]['maximum_entropy_vector_difference']}` nats at witness region",
            f"`{data['survivor_scale_control'][0]['witness_region']}`. The base/mutated entropy digests are",
            f"`{data['survivor_scale_control'][0]['base_entropy_sha256']}` /",
            f"`{data['survivor_scale_control'][0]['mutated_entropy_sha256']}`. Since every implemented gauge-library move",
            "preserves the full entropy vector, this difference is a gauge-invariant obstruction to library equivalence.",
            "",
            "## P1-v3 survivor tractability",
            "",
            f"All `{len(unique_carriers)}` certified graph-level survivors were reconstructed after the five-move closure.",
            "Every listed case contracted to a nonzero explicit boundary state and produced all 2^|T| entropies.",
            "",
            "| tensor family | bond dimension | survivor cases passed |",
            "|---|---:|---:|",
        ]
    )
    for family, dimension in sorted(counts):
        lines.append(f"| {family} | {dimension} | {counts[(family, dimension)]}/13 |")
    lines.extend(
        [
            "",
            f"The largest complement-symmetry residual across the census is `{maximum_complement:.15g}`. Boundary counts",
            "are 6–8; D=4 therefore reaches 65,536 explicit amplitudes and a largest balanced Schmidt side of 256.",
            "No carrier-specific obstruction occurs through D=4.",
            "",
            "The certified all-13 runtime envelope stops at D=4. D=5 and D=6 are typed",
            "`OUTSIDE_STEP1_RUNTIME_ENVELOPE_NOT_A_FAILURE`: for eight boundaries the state sizes are 390,625 and",
            "1,679,616 amplitudes, while the full-vector dense-SVD leading cost scales as 2^8 O(D^12). Thus the operational",
            "full-census wall begins at D=5 in this step; it is a declared validation budget, not a mathematical or",
            "topology-specific non-tractability result.",
            "",
            "## Anti-bypass result",
            "",
            "`state_entropy.py` imports only standard-library iteration/typing/dataclass support and NumPy. The audit traverses the complete",
            "reachable entropy call graph, including normalization and Schmidt-spectrum routines. Structural dataflow and",
            "mutation gates verify that cut-derived values cannot enter tensors, dimensions, entropy tolerances, or",
            "post-processing; cut machinery selects the frozen topology and supplies provenance only.",
            "",
            "## Obstruction / semantic finding",
            "",
            "The P1-v3 source weights are generic rational capacities and generally are not logarithms of integers. There",
            "is therefore no canonical exact map from those cut weights to tensor bond dimensions. Step 1 does not invent",
            "one: it records the weights and evaluates explicitly declared integer dimensions. Any later state-level search",
            "must declare its capacity-to-Hilbert-space convention or work directly with integer bond dimensions.",
            "",
            "## Step-1 disposition",
            "",
            "**DENSE_NUMERICAL_ENGINE_AND_CALIBRATION_CONTROLS_CERTIFIED.** This is infrastructure only. No pair of physically",
            "quotiented bulk geometries with equal contracted-state entropy vectors is claimed or searched for here.",
            "",
        ]
    )
    return "\n".join(lines)


def content_classification() -> str:
    return """# Content classification

| object | classification | role |
|---|---|---|
| `state_entropy.py` | GENERATED NUMERICAL ENGINE | state-only complex128/SVD reduced-density-matrix entropy path with truncation accountability |
| `tensor_engine.py` | GENERATED ENGINE | explicit dense tensor construction and contraction |
| `gauge_library.py` | GENERATED ENGINE | certified state-preserving/local-unitary presentation moves |
| P1-v3 survivor topology and weights | IMPORTED, HASH-PINNED | topology selection and source provenance only |
| Step41/42/44 scripts | READ-ONLY, HASH-PINNED REFERENCES | sound contraction/entropy/MMI patterns inspected; not executed by the engine |
| integer bond dimensions D=2,3,4 | DECLARED STEP-1 PARAMETERS | tractability census; not inferred from generic cut capacities |
| heterogeneous edge dimensions 2 and 3 | DECLARED STEP-1 CHECK | verifies that bond dimensions need not be uniform |
| control tensor seeds 7101/7102/7201 | DECLARED DETERMINISTIC PARAMETERS | small controls only |
| survivor tensor namespace `prog2_step2_tensor_seed_v1` | DECLARED INDEPENDENT PARAMETER | hash payload excludes P1 capacity seed |
| `legacy_seed_history_step1.csv` | FROZEN, HASH-PINNED HISTORY | before-fix digests only; never feeds tensor construction |
| entropy vectors and residuals | COMPUTED | derived exclusively from contracted boundary states |
| min-cut values | NOT USED / NOT PRODUCED | deliberately absent from the entropy path |
"""


def nonclaim_boundary() -> str:
    return """# Nonclaim boundary

Step 1 makes **no state-level entanglement-underdetermination claim**. It does not search for, exhibit, or imply two
physically inequivalent bulk geometries with the same contracted boundary state or the same full entropy vector. It
does not promote any of the 13 P1-v3 graph survivors to a state-level counterexample. It also does not equate entropy
with a min-cut, derive an RT equality, infer continuum geometry, or define a canonical map from generic cut capacities
to integer bond dimensions.

The certified content is limited to: an explicit dense numerical contraction engine; a state-only numerical all-subset
entropy engine with reported tolerance accountability; a verified presentation-gauge library; one distinguishable-bulk
calibration; one gauge-degeneracy calibration; a survivor-scale same-boundary mutation control; and a bounded tractability
census on the 13 survivor topologies. Numerical
entropy equality is not certified beyond the reported tolerances and error accounting. Searching for the underdetermination pair is reserved for a
later PROG2 step.
"""


def statement() -> str:
    return """# Certified Step-1 statement

For finite labelled tensor networks with explicitly declared positive integer bond and boundary dimensions, the explicit
dense numerical Step-1 engine constructs deterministic copy-tensor or independently seeded random-complex vertex tensors,
contracts every internal index, and numerically computes the von Neumann entropy of every boundary subset solely from the resulting normalized boundary state. The entropy includes every strictly positive numerical Schmidt probability; the declared tolerance reports numerical rank, discarded diagnostic mass, and a truncation-error bound rather than altering the reported entropy.

On concrete instances, internal g/g^-1 transformations, bivalent-series absorption, and parallel-index fusion
preserve the boundary state to machine precision; an explicit one-leg boundary unitary produces the predicted
local-unitary-related state and preserves every entropy. The full entropy vector distinguishes a contracted Bell-edge
network from a disconnected product network by ln(2), while agreeing for the internal-gauge pair. A six-boundary survivor-scale tensor mutation also changes the entropy vector, providing a gauge-invariant obstruction to library equivalence. Survivor random-tensor seeds are hashes of `(namespace, carrier_name, D, replicate)` and exclude P1 capacity seeds; provenance mutation leaves states and entropies unchanged. All 13 P1-v3 reduced
survivor carriers are computationally tractable for the declared random family at D=2,3,4 and the structured family at
D=2, with all 2^|T| entropies computed. This certifies the engine and controls only, not underdetermination.
"""


def step2_contract_requirements() -> str:
    return """# STEP2 contract requirements

independent declared capacity-to-state convention; independent tensor seeds and a pairing rule; fixed boundary labels and Hilbert-space identifications; preregistered entropy-equality policy with precision escalation and certified error bounds; bounded-complete gauge-closure procedure or gauge-invariant obstruction — failure to find a library move is not proof of inequivalence; explicit separation of boundary-state equality from entropy-vector equality; survivor-scale injective and gauge-degeneracy controls
"""


def render_artifacts(data: dict[str, Any]) -> dict[str, str]:
    return {
        "control_summary_step1.csv": csv_text(data["controls"]["control_summary"]),
        "control_entropy_vectors_step1.csv": csv_text(data["controls"]["entropy_rows"]),
        "gauge_verifications_step1.csv": csv_text(data["controls"]["gauge_rows"]),
        "engine_checks_step1.csv": csv_text(data["engine_checks"]),
        "seed_namespace_change_step1.csv": csv_text(data["seed_namespace_changes"]),
        "entropy_numerical_accountability_step1.csv": csv_text(data["numerical_accountability"]),
        "survivor_scale_control_step1.csv": csv_text(data["survivor_scale_control"]),
        "seed_independence_regression_step1.csv": csv_text(data["seed_independence"]),
        "review_regressions_step1.csv": csv_text(data["review_regressions"]),
        "survivor_tractability_step1.csv": csv_text(data["survivor_census"]),
        "resource_envelope_step1.csv": csv_text(data["resource_envelope"]),
        "anti_bypass_step1.csv": csv_text(data["anti_bypass"]),
        "dependency_pins_step1.csv": csv_text(data["dependency_pins"]),
        "schema_step1.json": json.dumps(schema(), indent=2, sort_keys=True) + "\n",
        "results_step1.md": results_markdown(data),
        "content_classification.md": content_classification(),
        "nonclaim_boundary.md": nonclaim_boundary(),
        "statement.md": statement(),
        "step2_contract_requirements.md": step2_contract_requirements(),
    }


def generate(output_dir: Path = HERE) -> dict[str, str]:
    data = compute_all()
    artifacts = render_artifacts(data)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, text in artifacts.items():
        (output_dir / name).write_text(text, encoding="utf-8")
    return artifacts


if __name__ == "__main__":
    generated = generate()
    print(f"build_step1.py: PASS: wrote={len(generated)}")
