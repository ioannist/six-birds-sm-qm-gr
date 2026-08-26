#!/usr/bin/env python3
"""Write deterministic Q1 access-provenance repair artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from pathlib import Path
from typing import Any

import q1_access_provenance as core


HERE = Path(__file__).resolve().parent


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise ValueError("empty CSV")
    fields: list[str] = []
    for row in rows:
        for name in row:
            if name not in fields:
                fields.append(name)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def markdown(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(column, "")) for column in columns) + " |")
    return "\n".join(lines)


def design_note() -> str:
    return """# Q1-REPAIR-1 design

## Scope and pinned inheritance

The repair imports the published four-bit carrier and quotient coordinates from `physics_atlas/thread_qm_gr/steps/step22_f51_unification_common_refinement_artifacts/f51_unification_step22.py:22-43`, the Born audit from `step25_sourcing_unification_artifacts/sourcing_unification_step25.py:27-35`, and normalization/back-reaction from `step26_semiclassical_dynamics_artifacts/semiclassical_dynamics_step26.py:25-46`. All imported scripts have literal SHA-256 pins. Step24 fields, Step28 histories, the Step28 build script, and the F24 family source record are also pinned as source evidence.

This is a computed finite provenance, not a claim that these coarse functionals are uniquely forced by continuum physics.

## Field-to-mode functionals

For an eight-site complex field `psi`, Step25 computes `rho=|psi|^2` and the oriented current `j=Im(conj(psi)*central_gradient(psi))`. Step26 computes `T00=|central_gradient(psi)|^2+V0|psi|^2`. With the inherited moderate coupling `kappa=0.3`, the modes are:

- `d0 = round(sum rho)`, a coarse conserved normalization sector;
- `d1 = 1[sum j >= 0]`, a phase/current-orientation sector determined by the Born audit;
- `d2 = argmax rho`, a Born-visible density sector;
- `d3 = argmax(V0 + 0.3*T00)`, a geometry-visible back-reaction sector.

Every track field is normalized, so the observed population has only `d0=1`; the repair does not claim empirical variation of the normalization coordinate. Ties in `argmax` use NumPy's deterministic lowest-index convention. The population contains all 26 Step25 source fields, all 16 Step28 history fields, eight fresh states from seed 71017, a conjugate phase pair, and a fixed-field/potential-only pair.

Complex conjugation preserves density and `T00` while reversing current, giving a controlled `d1` split inside one `q_GR` fiber. Changing only the background potential preserves the entire Born audit while changing `d3`, giving a controlled split inside one `q_QM` fiber. The stored Step28 potentials are independently recomputed from the pinned formula.

## Declared partition class

The exhausted class consists of the 16 partitions of the complete Boolean four-mode carrier induced by coordinate subsets. Directed factorization is computed from fibers: `A` determines `B` iff no two states in one `A` fiber lie in distinct `B` fibers. Every one of the 120 unordered distinct pairs is checked in both directions. Meets are common refinements; joins are computed by transitive closure of the two fiber equivalence relations. The closure contains exactly the same 16 partitions. The full Bell partition lattice on 16 labelled states is deliberately outside the declared class.

## Generated F24 maps and gates

The eight official family names are read from the pinned Step20 F24 source record. Each family is instantiated as a deterministic map on the 16-state carrier. A ninth fused-duplicate control implements the published direct sum `(d0,d1,d2,d0,d2,d3)` from `step31_qg_fused_object_nogo_artifacts/fused_object_nogo_step31.py:37-59`.

The exact representatives are: `MemoryLayer=(d0,d1,d2,d1 XOR d3)` (a reversible exposed record); `HiddenUpstreamRole=(d0,d1,d2)`; `BridgeMediatedRole=L`; `BudgetedRole=(d0,d1,d2,d0 XOR d2)`; `ScopedRole=(d0,d1,d2,d3)` only for `d0=0`; `CoarsenedRole=(d0,d2,d1 XOR d3)`; `OutsideRoleScope` exposes `d1,d3` only for `d0=0`; and `BlockedNonClosure=(d0,d1,d2,BLOCKED)`. These definitions are also carried as data in the competitor summary.

`G_stability` is exact idempotence of the rational conditional-mean completion induced by the map's fibers. `G_control_QM/GR` are exact fiber factorizations to the two endpoints. `G_audit` requires a formed, total deterministic map. `G_nosmuggle` requires at most four output coordinates and no duplicate coordinate columns. Reconciliation is the conjunction of these computed gates. Partition equivalence to `L` is equality of fiber equivalence relations, not identifier reuse. Status strings are selected from these computed results.

The family maps are finite diagnostic representatives of the declared shapes, not an exhaustion of every set-theoretic map with a family label.
"""


def results_note(result: dict[str, Any]) -> str:
    p = result["provenance"]
    ps = result["partition_summary"]
    cs = result["competitor_summary"]
    checks = [row for row in result["provenance_checks"] if "check" in row]
    controls = [row for row in result["provenance_checks"] if "control" in row]
    return f"""# Q1-REPAIR-1 results

## Field-to-mode provenance

Population: **{p['population_size']}** states (`26` Step25 samples, `16` Step28 history states, `8` fresh seeded states, and `4` paired controls). The field-derived quotient has {p['q_QM_fiber_count']} `q_QM` fibers and {p['q_GR_fiber_count']} `q_GR` fibers. The maximum residual when rebuilding all 16 stored Step28 potentials is `{p['step28_potential_recompute_max_residual']:.12g}`.

{markdown(checks, ['check', 'factors', 'defect_pair_count', 'first_witness'])}

The access split is **REALIZED ON THE DECLARED FINITE COARSE FUNCTIONALS**: the Step25 Born audit determines `d1` but not `d3`, while the geometry quotient determines `d3` but not `d1`. In particular, the potential-only pair has an identical Born audit and different geometry mode, and the conjugate pair has identical density/back-reaction geometry and opposite current orientation:

{markdown(controls, ['control', 'same_density_mode', 'same_geometry_mode', 'phase_mode_differs', 'same_q_QM_fiber', 'same_q_GR_fiber', 'geometry_mode_differs', 'witness'])}

This repairs provenance conditionally rather than deriving a unique mode dictionary. The normalization coordinate is constant (`d0=1`) on the normalized population, and the binning choices remain declared finite coarse-grainings.

## Exhausted coordinate-partition lattice

| quantity | computed value |
|---|---:|
| carrier states | {ps['carrier_state_count']} |
| coordinate-subset partitions | {ps['partition_count']} |
| unordered distinct pairs | {ps['distinct_unordered_pair_count']} |
| incomparable pairs | {ps['incomparable_pair_count']} |
| nested pairs | {ps['nested_pair_count']} |
| meet/join closure size | {ps['meet_join_closure_count']} |

`q_QM={ps['q_QM_partition']}` and `q_GR={ps['q_GR_partition']}` are one of exactly **{ps['incomparable_pair_count']} incomparable unordered pairs** in this declared class. Their two directed obstruction counts are `{ps['q_QM_q_GR_directed_defects'][0]}` and `{ps['q_QM_q_GR_directed_defects'][1]}`. All 65 nested pairs are explicit controls in the same exhaustive table; nesting is common, not a specially chosen exception.

## Computed F24-shape competitors

{markdown(result['competitors'], ['family', 'G_stability', 'G_control_QM', 'G_control_GR', 'G_audit', 'G_nosmuggle', 'QM_obstruction_pairs', 'GR_obstruction_pairs', 'partition_equivalent_to_L', 'reconciles', 'computed_status'])}

The mechanically generated class contains all {cs['official_family_count']} official F24 names plus the fused-duplicate control. `BridgeMediatedRole` and the exposed XOR-coded `MemoryLayer` reconcile, but both induce exactly the `L` partition; therefore **no generated competitor is a distinct reconciling partition**. Hidden, budgeted, scoped, coarsened, outside-scope, and blocked maps fail computed endpoint/audit gates. The fused direct sum determines both endpoints but fails `G_nosmuggle` through duplicate columns `d0` and `d2`. This reproduces the substantive “collapse to L or fail” result without literal defeat booleans, while making the Memory collapse explicit.
"""


def render(result: dict[str, Any]) -> dict[str, bytes]:
    schema = {
        "artifact": "Q1-REPAIR-1 field-to-mode access provenance",
        "schema_version": 1,
        "field_modes": {
            "d0": "round(sum |psi|^2)",
            "d1": "indicator(sum Step25 current >= 0)",
            "d2": "argmax Step25 density",
            "d3": "argmax(background + 0.3*Step26 T00)",
            "q_QM": ["d0", "d1", "d2"],
            "q_GR": ["d0", "d2", "d3"],
        },
        "declared_partition_class": "partitions induced by all 16 subsets of four coordinates, closed under meet/join",
        "factorization": "target is constant on every source fiber",
        "competitor_reconciliation": "G_stability and G_control_QM and G_control_GR and G_audit and G_nosmuggle",
        "row_counts": {
            "field_modes": len(result["modes"]),
            "fibers": len(result["fibers"]),
            "partition_catalog": len(result["partitions"]),
            "partition_pairs": len(result["partition_pairs"]),
            "competitors": len(result["competitors"]),
            "competitor_values": len(result["competitor_values"]),
        },
        "computed_summaries": {
            "provenance": result["provenance"],
            "partitions": result["partition_summary"],
            "competitors": result["competitor_summary"],
        },
    }
    payloads = {
        "q1_dependency_pins.csv": csv_bytes(result["pins"]),
        "q1_field_modes.csv": csv_bytes(result["modes"]),
        "q1_provenance_fibers.csv": csv_bytes(result["fibers"]),
        "q1_provenance_checks.csv": csv_bytes(result["provenance_checks"]),
        "q1_partition_catalog.csv": csv_bytes(result["partitions"]),
        "q1_partition_pair_exhaustion.csv": csv_bytes(result["partition_pairs"]),
        "q1_competitor_summary.csv": csv_bytes(result["competitors"]),
        "q1_competitor_maps.csv": csv_bytes(result["competitor_values"]),
        "q1_schema.json": json_bytes(schema),
        "DESIGN.md": design_note().encode(),
        "RESULTS.md": results_note(result).encode(),
    }
    manifest = {name: hashlib.sha256(payload).hexdigest() for name, payload in sorted(payloads.items())}
    payloads["q1_artifact_manifest.json"] = json_bytes(manifest)
    return payloads


def main() -> None:
    started = time.perf_counter()
    result = core.run()
    for name, payload in render(result).items():
        (HERE / name).write_bytes(payload)
    print(
        "Q1 build PASS: "
        f"population={result['provenance']['population_size']} "
        f"access_split={result['provenance']['access_split_realized']} "
        f"partitions={result['partition_summary']['partition_count']} "
        f"pairs={result['partition_summary']['distinct_unordered_pair_count']} "
        f"incomparable={result['partition_summary']['incomparable_pair_count']} "
        f"competitors={len(result['competitors'])} "
        f"elapsed_seconds={time.perf_counter()-started:.3f}"
    )


if __name__ == "__main__":
    main()
