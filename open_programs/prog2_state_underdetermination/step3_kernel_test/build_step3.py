#!/usr/bin/env python3
"""Render deterministic PROG2 Step-3 artifacts."""

from __future__ import annotations

import csv
import io
import json
import os
from pathlib import Path
from typing import Any


os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from conventions_step3 import CONVENTIONS
from step3_core import compute_all


HERE = Path(__file__).resolve().parent


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def schema(data: dict[str, Any]) -> dict[str, Any]:
    intersections = data["kernel_intersections"]
    classifications = data["direction_classifications"]
    return {
        "artifact": "PROG2_STEP3_STATE_LEVEL_KERNEL_TEST",
        "version": 1,
        "result_grade": "DENSE_NUMERICAL_EVIDENCE",
        "exact_evidence": "imported exact-rational active-cut kernel bases",
        "primary_census": {
            "fiber_count": 19,
            "convention_member_count": len(CONVENTIONS),
            "row_count": len(intersections),
            "all_outcomes_published": len(intersections) == 95,
        },
        "convention_members": [
            {
                "member_id": item.member_id,
                "dimension": item.dimension,
                "tensor_family": item.tensor_family,
                "spectrum_family": item.spectrum_family,
                "alpha": item.alpha,
                "beta": item.beta,
            }
            for item in CONVENTIONS
        ],
        "jacobian": {
            "shape": "2^boundary_count by edge_count",
            "state_tangent": "analytic differentiation of declared Schmidt coefficients and dense contraction",
            "entropy_tangent": "analytic reduced-density-matrix spectral derivative",
            "rank_allowance": "max(5e-8,1e-8*sigma_max)",
            "finite_difference_check": "central h0,h0/2,h0/4 along every imported cut basis vector",
            "numerical_allowance_is_certificate": False,
        },
        "headline": {
            "aggregate_verdict": data["aggregate_verdict"],
            "rows_with_nonzero_intersection": sum(
                int(row["intersection_dimension"]) > 0 for row in intersections
            ),
            "protected_direction_records": sum(
                row["classification"] == "SYMMETRY_PROTECTED"
                for row in classifications
            ),
            "distinct_protected_carrier_directions": len(
                {
                    (
                        row["carrier"],
                        row["source_seed_provenance"],
                        row["member_id"],
                        row["intersection_direction_index"],
                    )
                    for row in classifications
                    if row["classification"] == "SYMMETRY_PROTECTED"
                }
            ),
            "certified_null_direction_records": sum(
                row["classification"] == "CERTIFIED-NULL"
                for row in classifications
            ),
            "numerical_artifact_records": sum(
                row["classification"] == "NUMERICAL-ARTIFACT"
                for row in classifications
            ),
        },
        "controls": {
            "count": len(data["controls"]),
            "required_verdict": "COINCIDE and STATE_LEVEL_GAUGE",
            "distinct_capacities": "c and 1/c on one internal edge",
        },
        "files": {
            "kernel_intersections_step3.csv": "all 95 per-fiber/per-member intersection rows",
            "direction_classifications_step3.csv": "every nonzero intersection direction class",
            "direction_stability_step3.csv": "three-step check for every imported basis direction/member",
            "controls_step3.csv": "two analytically coincident distinct-capacity controls",
            "control_entropy_comparisons_step3.csv": "all subset comparisons for both controls",
            "convention_checks_step3.csv": "family normalization, derivative, and injectivity gates",
            "anti_bypass_step3.csv": "inherited and Step-3 state-construction isolation gates",
            "dependency_pins_step3.csv": "literal hashes for all imported code and data",
        },
    }


def results_markdown(data: dict[str, Any]) -> str:
    intersections = data["kernel_intersections"]
    classifications = data["direction_classifications"]
    by_fiber: dict[str, dict[str, dict[str, Any]]] = {}
    for row in intersections:
        by_fiber.setdefault(row["fiber_id"], {})[row["member_id"]] = row
    nonzero = [row for row in intersections if int(row["intersection_dimension"]) > 0]
    lines = [
        "# PROG2 Step 3 — state-level kernel test",
        "",
        "## Headline",
        "",
        f"Aggregate verdict: **{data['aggregate_verdict']}**.",
        "",
        f"All {len(intersections)} preregistered `(fiber, convention)` rows were evaluated. "
        f"{len(nonzero)} rows have a nonzero `ker J_cut ∩ ker J_state`; all such rows occur in the "
        "structured-copy member `C2_L1` and are explained by its analytic product symmetry. The four seeded-random "
        "members have trivial intersections everywhere.",
        "",
        "Everything involving dense states or entropy derivatives is graded **dense numerical evidence** under the "
        "preregistered allowance. The cut-kernel bases alone are imported exact-rational evidence.",
        "",
        "## Intersection dimensions",
        "",
        "| fiber | carrier | cut dim | R2_L1 | R2_L2 | C2_L1 | R3_S11 | R3_S21 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for fiber_id in sorted(by_fiber):
        rows = by_fiber[fiber_id]
        first = rows["R2_L1"]
        lines.append(
            f"| {fiber_id} | {first['carrier']} | {first['exact_cut_kernel_dimension']} "
            + "".join(
                f"| {rows[item.member_id]['intersection_dimension']} "
                for item in CONVENTIONS
            )
            + "|"
        )
    lines.extend(
        [
            "",
            "The repeated rows for fibers sharing a base weighting intentionally report the full exact cut-kernel "
            "intersection, not only that fiber's named basis vector. The complete Jacobian digests, singular values, "
            "rank allowances, and three-step checks are exported in the CSV artifacts.",
            "",
            "## Nonzero-direction classifications",
            "",
            "| fiber | carrier | seed provenance | member | direction | class | analytic explanation | max numerical response | Step-4 eligible |",
            "|---|---|---:|---|---:|---|---|---:|---|",
        ]
    )
    for row in classifications:
        lines.append(
            f"| {row['fiber_id']} | {row['carrier']} | {row['source_seed_provenance']} | {row['member_id']} "
            f"| {row['intersection_direction_index']} | {row['classification']} | {row['symmetry']} "
            f"| `{row['maximum_abs_state_entropy_response']}` | {row['continuation_eligible']} |"
        )
    if not classifications:
        lines.append("| — | — | — | — | — | — | no nonzero directions | — | — |")
    lines.extend(
        [
            "",
            "For `C2_L1`, connected copy tensors contract to a two-term GHZ state. Its amplitude odds depend only "
            "on `P=product_e c_e`, so exact tangents satisfying `sum_e v_e/c_e=0` are state-entropy null by an "
            "identified analytic symmetry. No finite continuation is performed here.",
            "",
            "## Distinct-capacity analytic can-fail controls",
            "",
            "| control | carrier | edge | c | 1/c | state residual | maximum entropy difference | classifier | type |",
            "|---|---|---|---:|---:|---:|---:|---|---|",
        ]
    )
    for row in data["controls"]:
        lines.append(
            f"| {row['control_id']} | {row['carrier']} | {row['edge_id']} | `{row['capacity_exact']}` "
            f"| `{row['reciprocal_capacity_exact']}` | `{row['state_l2_residual']}` "
            f"| `{row['maximum_entropy_difference_nats']}` | {row['classifier_verdict']} "
            f"| {row['state_level_classification']} |"
        )
    lines.extend(
        [
            "",
            "Both controls realize `q(1/c)=X q(c) X` by explicitly relabeling the internal Schmidt basis at both "
            "edge endpoints. They are distinct-capacity `COINCIDE` cases correctly typed as state-level gauge, not "
            "underdetermination candidates.",
            "",
            "## Aggregate reading",
            "",
            "The state-level kernel is trivial on every seeded-random member in the fixed convention grid. Protected "
            "directions do exist for the copy-tensor member on cut kernels of dimension at least two; these are Step-4 "
            "continuation candidates only. They do not establish finite entropy coincidence, state equality, or bulk "
            "inequivalence.",
            "",
        ]
    )
    return "\n".join(lines)


def content_classification() -> str:
    return """# Content classification

| object | classification | role |
|---|---|---|
| PROG3 active-cut kernel bases | IMPORTED READ-ONLY, HASH-PINNED, EXACT RATIONAL | `ker J_cut` evidence |
| Step-1 dense tensor/entropy engine | IMPORTED READ-ONLY, HASH-PINNED | state construction and entropy path |
| Step-2 comparison policy | IMPORTED READ-ONLY, HASH-PINNED | can-fail control classifier |
| five convention/tensor members | PREREGISTERED DECLARED FAMILY | finite capacity-to-state evaluation surface |
| full entropy Jacobians | GENERATED ANALYTIC-DERIVATIVE DENSE NUMERICS | `J_state` computation |
| Jacobian ranks and step sweeps | DENSE NUMERICAL EVIDENCE | intersection dimensions under allowance |
| copy-family product symmetry | ANALYTIC CONSTRUCTION, NUMERICALLY CORROBORATED | explains every nonzero intersection |
| `c` versus `1/c` controls | ANALYTIC GAUGE CONSTRUCTION, NUMERICALLY VERIFIED | coincidence can-fail direction |
| Step-4 eligibility | TYPED CANDIDATE STATUS | not finite continuation or underdetermination |
"""


def nonclaim_boundary(data: dict[str, Any]) -> str:
    protected = sum(
        row["classification"] == "SYMMETRY_PROTECTED"
        for row in data["direction_classifications"]
    )
    distinct_protected = len(
        {
            (
                row["carrier"],
                row["source_seed_provenance"],
                row["member_id"],
                row["intersection_direction_index"],
            )
            for row in data["direction_classifications"]
            if row["classification"] == "SYMMETRY_PROTECTED"
        }
    )
    return f"""# Nonclaim boundary

Step 3 makes no state-level underdetermination claim. It reports dense numerical evidence for entropy-Jacobian
intersections over exactly the preregistered five-member family and imports exact-rational cut kernels. The
preregistered numerical allowance is not a forward-error certificate.

The {protected} per-primary-row protected direction records ({distinct_protected} distinct carrier-level directions)
are infinitesimal Step-4 candidates generated by the structured-copy product symmetry. Step 3 does not continue them
to finite displacement and does not claim equality of finite entropy
vectors or boundary states. Any future `COINCIDE` result remains a candidate only until it passes state-level gauge
closure and an independent bulk-invariant test. The two present `c` versus `1/c` coincidences explicitly fail that
candidate test because they are identified internal-basis gauge transformations.

No conclusion is made for convention maps, bond dimensions, tensors, seeds, carriers, or dynamics outside the frozen
preregistration. Trivial intersections for seeded-random members do not prove that a state-level ambiguity cannot
exist elsewhere.
"""


def statement(data: dict[str, Any]) -> str:
    intersections = data["kernel_intersections"]
    nonzero = sum(int(row["intersection_dimension"]) > 0 for row in intersections)
    protected = sum(
        row["classification"] == "SYMMETRY_PROTECTED"
        for row in data["direction_classifications"]
    )
    distinct_protected = len(
        {
            (
                row["carrier"],
                row["source_seed_provenance"],
                row["member_id"],
                row["intersection_direction_index"],
            )
            for row in data["direction_classifications"]
            if row["classification"] == "SYMMETRY_PROTECTED"
        }
    )
    return f"""# Step-3 statement

For all 19 exact cut-kernel fibers and all five preregistered capacity-to-state/tensor members, the full boundary
entropy Jacobian was computed at the base weighting and intersected with the imported exact active-cut kernel. All
95 rows and every directional stability check are published at dense-numerical-evidence grade.

The four seeded-random members have trivial intersections everywhere. The structured-copy member has nonzero
intersection on {nonzero} repeated per-fiber rows, producing {protected} per-row classifications that represent
{distinct_protected} distinct carrier-level protected directions. Every such direction is explained by the analytic connected-copy symmetry in which the boundary GHZ
state depends on capacities only through their product. These directions are eligible for Step 4 but are not
continued here.

Two survivor-scale pairs with distinct capacities `c` and `1/c` produce coincident entropy vectors under an explicit
internal Schmidt-basis swap and are correctly classified as state-level gauge. No bulk-geometry underdetermination
claim is made.
"""


def render(data: dict[str, Any]) -> dict[str, str]:
    return {
        "results_step3.md": results_markdown(data),
        "schema_step3.json": json.dumps(schema(data), indent=2, sort_keys=True) + "\n",
        "content_classification.md": content_classification(),
        "nonclaim_boundary.md": nonclaim_boundary(data),
        "statement.md": statement(data),
        "kernel_intersections_step3.csv": csv_text(data["kernel_intersections"]),
        "direction_classifications_step3.csv": csv_text(data["direction_classifications"]),
        "direction_stability_step3.csv": csv_text(data["direction_stability"]),
        "controls_step3.csv": csv_text(data["controls"]),
        "control_entropy_comparisons_step3.csv": csv_text(
            data["control_entropy_comparisons"]
        ),
        "convention_checks_step3.csv": csv_text(data["convention_checks"]),
        "anti_bypass_step3.csv": csv_text(data["anti_bypass"]),
        "dependency_pins_step3.csv": csv_text(data["dependency_pins"]),
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
    print(f"build_step3.py: PASS: wrote={len(artifacts)}")


if __name__ == "__main__":
    main()
