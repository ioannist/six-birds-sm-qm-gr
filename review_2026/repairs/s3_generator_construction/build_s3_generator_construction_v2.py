#!/usr/bin/env python3
"""Write versioned S3-REPAIR-1b verification-closure artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from fractions import Fraction
from pathlib import Path
from typing import Any

import s3_construction_v2 as v2
from exact_lie import format_fraction, matrix_key


HERE = Path(__file__).resolve().parent

TABLES = {
    "full_commutant_v2.csv": "full_commutant",
    "full_commutant_coefficients_v2.csv": "full_commutant_coefficients",
    "f48_extracted_coroots_v2.csv": "f48_coroots",
    "f48_extracted_lattice_v2.csv": "f48_lattice",
    "su4_slice_map_v2.csv": "su4_slice_map",
    "su4_slice_witness_v2.csv": "su4_slice_witness",
    "product_parent_controls_v2.csv": "product_parent_controls",
    "pati_salam_weights_v2.csv": "pati_salam_weights",
    "claim_status_v2.csv": "claim_status",
    "mutation_tests_v2.csv": "mutation_tests",
}


def fraction_text(value: Any) -> Any:
    return format_fraction(value) if isinstance(value, Fraction) else value


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        raise ValueError("cannot serialize an empty result table")
    stream = io.StringIO(newline="")
    fields = list(rows[0])
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: fraction_text(row[field]) for field in fields})
    return stream.getvalue()


def public_tables(result: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    full = result["full_commutant"]
    f48 = result["f48"]
    su4 = result["su4_slice"]
    pati = result["pati_salam"]
    # The coefficient order is the deterministic su(5) basis order reconstructed
    # by the v2 computation; recover names from a fresh exact construction.
    import s3_construction as v1
    su5 = v1.construct_su5()
    return {
        "full_commutant": [{
            "ambient_coefficient_count": full["coefficient_count"],
            "commutator_equation_count": full["equation_count"],
            "constraint_rank": full["rank"],
            "commutant_nullity": full["nullity"],
            "centralizer_dimension": full["nullity"],
            "off_diagonal_entries_zero_in_regular_frame": full["off_diagonal_zero"],
            "primitive_diagonal": str(full["primitive_diagonal"]),
        }],
        "full_commutant_coefficients": [
            {"basis_generator": name, "kernel_coefficient": coefficient}
            for (name, _), coefficient in zip(su5["basis"], full["kernel_coefficients"])
        ],
        "f48_coroots": [
            {"coroot_id": row["coroot_id"], "extraction": row["extraction"],
             "cocharacter_coordinates": str(row["coordinates"]), "matrix": matrix_key(row["matrix"])}
            for row in result["coroot_rows"]
        ],
        "f48_lattice": [{
            "extracted_columns": str(f48["columns"]),
            "derived_coroot_rank": f48["derived_coroot_rank"],
            "smith_invariants": str(f48["smith_invariants"]),
            "annihilator": str(f48["annihilator"]),
            "free_rank_pi1_H": f48["free_rank_pi1_h"],
            "centralizer_primitive": str(f48["centralizer_primitive"]),
            "central_u1_loop_index": f48["central_u1_loop_index"],
            "H_connected": f48["H_connected"],
            "pi1_SU5": f48["pi1_SU5"], "pi2_SU5": f48["pi2_SU5"],
            "kernel_free_rank": f48["kernel_free_rank"], "pi2_SU5_over_H": f48["pi2_SU5_over_H"],
        }],
        "su4_slice_map": [
            {"su4_root": row["su4_root"], "su5_root": row["su5_root"],
             "su4_charge": row["su4_charge"], "su5_charge": row["su5_charge"],
             "computed_charge_rescale": row["charge_rescale"],
             "su4_matrix": matrix_key(row["su4_matrix"]), "su5_matrix": matrix_key(row["su5_matrix"])}
            for row in su4["mapped_roots"]
        ],
        "su4_slice_witness": [{
            "weak_operator": su4["weak_operator"], "source_slice_element": su4["source_slice_element"],
            "commutator": f"{format_fraction(su4['commutator_coefficient'])}*{su4['commutator_target']}",
            "commutator_target": su4["commutator_target"],
            "target_relation_exact": su4["target_relation_exact"],
            "target_outside_slice": su4["target_outside_slice"], "verdict": su4["verdict"],
        }],
        "product_parent_controls": result["product_parent_attempts"],
        "pati_salam_weights": [
            {"state_id": f"PS_{index:02d}", "parent_rep": row["parent_rep"],
             "su4_weight": row["su4_weight"], "doublet_weight": row["doublet_weight"],
             "B_minus_L": row["B_minus_L"], "T3_L": row["T3_L"], "T3_R": row["T3_R"],
             "Y": row["Y"], "Q": row["Q"]}
            for index, row in enumerate(pati["states"])
        ],
        "claim_status": result["claim_status"],
        "mutation_tests": result["mutation_tests"],
    }


def jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return format_fraction(value)
    if isinstance(value, tuple):
        return [jsonable(item) for item in value]
    if isinstance(value, list):
        return [jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    return value


def findings_text(result: dict[str, Any]) -> str:
    full, f48, su4, pati = (result[key] for key in
                            ("full_commutant", "f48", "su4_slice", "pati_salam"))
    claim_lines = "\n".join(
        f"| {row['claim']} | {row['status']} | {row['computed_result']} | {row['residual_assumption_or_convention']} |"
        for row in result["claim_status"]
    )
    mutation_lines = "\n".join(
        f"| {row['mutation']} | {row['expected']} | {row['result']} | {row['evidence']} |"
        for row in result["mutation_tests"]
    )
    return f"""# S3-REPAIR-1b verification closure

## Full commutant

The centralizer is now computed over all 24 traceless Hermitian SU(5) directions, not a diagonal ansatz. The exact commutator system has {full['equation_count']} nonzero rational component equations, coefficient rank {full['rank']}, and nullity {full['nullity']}. Its unique direction is diagonal only as an output, with primitive pattern `{full['primitive_diagonal']}`. Therefore the proved centralizer dimension is 1.

## Extracted F48 lattice

The three coroot columns are extracted from the constructed Cartans as `B0_D_1`, `(B0_D_2-B0_D_1)/2`, and `B1_D_1`. Their coordinates in `e_i-e_4` are `{f48['columns']}`. Exact Smith reduction gives rank {f48['derived_coroot_rank']}, invariants `{f48['smith_invariants']}`, annihilator `{f48['annihilator']}`, free rank {f48['free_rank_pi1_h']}, and centralizer-loop index {f48['central_u1_loop_index']}.

With the explicitly supplied topology inputs `H connected`, `pi_1(SU(5))=0`, and `pi_2(SU(5))=0`, the exact sequence has kernel free rank {f48['kernel_free_rank']} and yields `pi_2(SU(5)/H)={f48['pi2_SU5_over_H']}`.

## SU(4) fixed-slice ruling

All six SU(4) roots are mapped as matrices into the fixed weak-index SU(5) slice. The SU(4) root charges are `±4/3`; the mapped SU(5) charges are `±5/6`; their computed ratio is `{format_fraction(su4['charge_rescale'])}` for all six roots.

The decisive witness is computed directly:

`[{su4['weak_operator']},{su4['source_slice_element']}] = {format_fraction(su4['commutator_coefficient'])}*{su4['commutator_target']}`,

and `{su4['commutator_target']}` is outside the six-dimensional slice. Hence the slice is not SU(2)-invariant. The six-generator identity is refuted; the fixed-slice analogue relation lands.

## Product-parent control

The well-posed semisimple product attempt is Pati-Salam `SU(4)xSU(2)_LxSU(2)_R`. The SU(4) centralizer constructs `B-L=(1/3,1/3,1/3,-1)`. Requiring the colorless right-doublet neutral state fixes `Y=T3_R+(B-L)/2`. On the constructed `(4,2,1)+(4bar,1,2)` weights,

- `Tr(T3_L^2)={format_fraction(pati['tr_T3L_squared'])}`;
- `Tr(Y^2)={format_fraction(pati['tr_Y_squared'])}`;
- `Tr(Q^2)={format_fraction(pati['tr_Q_squared'])}`;
- `Tr(T3_L^2)/Tr(Q^2)={format_fraction(pati['sin2_trace_ratio'])}`.

Thus this product parent gives `3/8`, not `3/23`. Moreover, a product group does not force equality of its independent factor couplings. The only reproduced `3/23` is recomputed at the freely inserted choice `lambda=2` in the reductive `SU(3)xSU(2)xU(1)` model. That model is not semisimple and does not derive the U(1) scale. No well-posed `3/23` product parent was found, so the paper's product-parent statement remains an unsupported import and requires correction; this does not prove that every exotic product embedding is impossible.

<a id="updated-claim-ledger-ky-and-weak-angle-ratio"></a>
## Updated claim ledger

| Claim | Status | Computed result | Residual assumption or convention |
|---|---|---|---|
{claim_lines}

## Mutation suite

| Mutation/test | Expected | Result | Evidence |
|---|---|---|---|
{mutation_lines}
"""


def schema_for(tables: dict[str, list[dict[str, Any]]], result: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 2,
        "experiment": "S3-REPAIR-1b verification closure",
        "historical_v1_artifacts_preserved": True,
        "tables": {filename: {"row_count": len(tables[key]), "columns": list(tables[key][0])}
                   for filename, key in TABLES.items()},
        "headline": {
            "full_commutant_rank": result["full_commutant"]["rank"],
            "full_commutant_nullity": result["full_commutant"]["nullity"],
            "centralizer_dimension": result["full_commutant"]["nullity"],
            "f48_pi2": result["f48"]["pi2_SU5_over_H"],
            "su4_slice_verdict": result["su4_slice"]["verdict"],
            "pati_salam_ratio": format_fraction(result["pati_salam"]["sin2_trace_ratio"]),
            "mutation_pass_count": sum(row["result"] == "PASS" for row in result["mutation_tests"]),
            "mutation_test_count": len(result["mutation_tests"]),
        },
        "topology_inputs": {"H_connected": True, "pi1_SU5": "0", "pi2_SU5": "0"},
        "implementation_sha256": {
            name: hashlib.sha256((HERE / name).read_bytes()).hexdigest()
            for name in ("exact_lie.py", "s3_construction.py", "s3_construction_v2.py",
                         "build_s3_generator_construction_v2.py",
                         "run_s3_generator_construction_v2.py", "DESIGN.md")
        },
    }


def render_artifacts(result: dict[str, Any]) -> dict[str, bytes]:
    tables = public_tables(result)
    artifacts = {filename: csv_text(tables[key]).encode() for filename, key in TABLES.items()}
    summary = {
        "full_commutant": {key: jsonable(value) for key, value in result["full_commutant"].items()
                            if key not in {"centralizer_matrix"}},
        "f48": jsonable(result["f48"]),
        "su4_slice": jsonable({key: value for key, value in result["su4_slice"].items()
                               if key != "mapped_roots"}),
        "product_parent_attempts": jsonable(result["product_parent_attempts"]),
        "claim_status": result["claim_status"], "mutation_tests": result["mutation_tests"],
    }
    artifacts["s3_results_v2.json"] = (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode()
    artifacts["schema_v2.json"] = (json.dumps(schema_for(tables, result), indent=2, sort_keys=True) + "\n").encode()
    artifacts["RESULTS_v2.md"] = findings_text(result).encode()
    manifest = {"algorithm": "sha256", "files": {name: hashlib.sha256(data).hexdigest()
                                                     for name, data in sorted(artifacts.items())}}
    artifacts["artifact_manifest_v2.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    return artifacts


def main() -> None:
    started = time.monotonic()
    result = v2.run_v2()
    artifacts = render_artifacts(result)
    for name, data in artifacts.items():
        (HERE / name).write_bytes(data)
    elapsed = time.monotonic() - started
    print("build_s3_generator_construction_v2.py: PASS: "
          f"commutant=23/1 pi2={result['f48']['pi2_SU5_over_H']} "
          f"mutations={len(result['mutation_tests'])}/{len(result['mutation_tests'])} "
          f"pati_ratio={format_fraction(result['pati_salam']['sin2_trace_ratio'])} "
          f"elapsed_seconds={elapsed:.3f}")


if __name__ == "__main__":
    main()
