#!/usr/bin/env python3
"""Deterministic serialization for the S3 construction results."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from typing import Any


TABLES = {
    "su5_generators.csv": "su5_generators",
    "su5_coset_quantum_numbers.csv": "coset_quantum_numbers",
    "fermion_decomposition.csv": "fermion_decomposition",
    "ratio_conventions.csv": "ratio_conventions",
    "f27_generator_actions.csv": "f27_generator_actions",
    "su4_analogue.csv": "su4_analogue",
    "f48_lattice.csv": "f48_lattice",
    "parent_candidates.csv": "parent_candidates",
    "mutation_tests.csv": "mutation_tests",
    "claim_status.csv": "claim_status",
}


def csv_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        raise ValueError("refusing to write a table with no rows")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def _column_type(values: list[Any]) -> str:
    if all(isinstance(v, bool) for v in values):
        return "boolean"
    if all(isinstance(v, int) and not isinstance(v, bool) for v in values):
        return "integer"
    return "string"


def schema_for(result: dict) -> dict:
    tables = {}
    for filename, key in TABLES.items():
        rows = result[key]
        tables[filename] = {
            "row_count": len(rows),
            "primary_key": {
                "su5_generators.csv": ["generator_id"],
                "su5_coset_quantum_numbers.csv": ["root_generator"],
                "fermion_decomposition.csv": ["state"],
                "ratio_conventions.csv": ["convention"],
                "f27_generator_actions.csv": ["generator_id"],
                "su4_analogue.csv": ["root_generator"],
                "f48_lattice.csv": ["global_form"],
                "parent_candidates.csv": ["candidate"],
                "mutation_tests.csv": ["mutation"],
                "claim_status.csv": ["claim"],
            }[filename],
            "columns": [{"name": column,
                         "type": _column_type([row[column] for row in rows]),
                         "exact_arithmetic": column not in {"matrix", "rejection", "computed_result",
                                                             "residual_assumption_or_convention"}}
                        for column in rows[0]],
        }
    return {
        "schema_version": "1.0",
        "packet": "S3-REPAIR-1",
        "construction_mode": "from-first-principles exact Gaussian-rational matrices and integer lattices",
        "physics_atlas_imports": [],
        "external_file_dependencies": [],
        "summary_file": "s3_results.json",
        "tables": tables,
    }


def results_note(result: dict) -> str:
    hyper = result["hypercharge"]
    standard, alternative = result["ratio_conventions"]
    f27 = result["f27_summary"]
    su4 = result["su4_summary"]
    f48 = result["f48_lattice"][0]
    claims = result["claim_status"]
    claim_lines = "\n".join(
        f"| {row['claim']} | {row['status']} | {row['computed_result']} | {row['residual_assumption_or_convention']} |"
        for row in claims
    )
    return f"""# S3 generator-construction results

## Outcome

The regular block embedding on indices `(0,1,2)|(3,4)` has a one-dimensional diagonal centralizer. Exact row reduction gives the primitive direction `{hyper['primitive_pattern']}`. Giving the weak-pair state of `wedge^2(5)` unit charge fixes the displayed convention and produces

`Y = {hyper['standard_pattern']}`.

This is a derivation of the direction from the embedding. Its overall sign and scale remain coordinate conventions; the standard scale is `{hyper['standard_scale']}`.

## Ratios and fermions

Acting with the embedded algebra on `5bar + wedge^2(5)` splits its 15 basis states into the computed multiplets `(3bar,1,1/3)`, `(1,2,-1/2)`, `(3bar,1,-2/3)`, `(3,2,1/6)`, and `(1,1,1)`. No SM roster is supplied to the trace computation. In the weak-pair-unit convention,

- `Tr_5(Y^2)={standard['fundamental_tr_y2']}` and `Tr_5(T3^2)={standard['fundamental_tr_t3_squared']}`, hence `k_Y={standard['k_y']}`;
- `Tr_generation(T3^2)={standard['generation_tr_t3_squared']}` and `Tr_generation(Q^2)={standard['generation_tr_q2']}`, hence `sin^2(theta_W)={standard['sin2_theta_w']}` for `Q=T3+Y`.

As an explicit alternative admissible abelian coordinate, `Y'=2Y` gives `k_Y={alternative['k_y']}` and, with the correspondingly stated `Q'=T3+Y'`, `sin^2(theta_W)={alternative['sin2_theta_w']}`. Thus the celebrated values are computed once the standard charge unit and `Q=T3+Y` convention are fixed; that normalization is not forced by the Lie-algebra centralizer alone. Reversing the sign of `Y` is the other harmless direction convention.

## Coset and the step41 object

The 12-dimensional real Hermitian coset is displayed in the CSV through its 12 one-dimensional complex root spaces. Direct commutator eigenvalues group them as six `(3,2,-5/6)` roots and six `(3bar,2,5/6)` roots.

The same construction for `SU(4) -> SU(3)xU(1)` gives primitive centralizer `(-1,-1,-1,3)` and six coset roots `3 + 3bar`. Its computed verdict is `{su4['verdict']}`: mapping `E_i3` and `E_3i` into a fixed weak-index slice of the SU(5) roots is an explicit vector-space analogue after a `5/8` charge rescaling, but that slice is not invariant under the full embedded SU(2). The step41 object is therefore not identical to the SU(5) X/Y coset.

## F27: baryon descent

Color representations are read from computed SU(3) weights. On left-chiral fields the assigned physical baryon charges are `B=1/3` for `3`, `B=-1/3` for `3bar`, and `B=0` for singlets. Matrix action, rather than role labels, finds `{f27['delta_b_generators']}/{f27['coset_generators']}` real SU(5) coset generators with nonzero-Delta-B transitions. Every embedded `su(3)+su(2)+u(1)` generator preserves B. Removing the coset therefore leaves the SM-clean structure B-conserving at this algebraic vertex level. This does not compute a proton-decay rate or establish that a heavy parent is physically realized.

## F48: monopole lattice

In the SU(5) cocharacter lattice, quotienting by the three embedded SU(3) and SU(2) coroot columns has Smith invariants `{f48['smith_invariants']}`: one free primitive loop and no torsion. The computed centralizer loop pairs with that primitive loop with index `{f48['central_u1_loop_index']}`, yielding the global form `{f48['global_form']}`. With the standard exact-sequence inputs `pi_1(SU(5))=0` and `pi_2(SU(5))=0`, the result is `pi_2(SU(5)/H)={f48['su5_pi2_g_over_h']}`. For an SM-alone structure modeled with no larger broken parent (`G=H`), `G/H` is a point and the corresponding required charge is `{f48['sm_alone_pi2_g_over_h']}`. The exact-sequence facts and the choice of global form are stated mathematical assumptions, not outputs of the finite matrix computation.

## Claim ledger

| Claim | Status | Computed result | Residual assumption or convention |
|---|---|---|---|
{claim_lines}

The computed parent selector uniquely chooses SU(5) only inside the declared diagnostic family of regular `SU(n)` embeddings for `n=5..8`. A global uniqueness claim across other simple groups remains an import.
"""


def render_artifacts(result: dict) -> dict[str, bytes]:
    rendered: dict[str, bytes] = {}
    for filename, key in TABLES.items():
        rendered[filename] = csv_text(result[key]).encode("utf-8")
    rendered["s3_results.json"] = (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
    rendered["schema.json"] = (json.dumps(schema_for(result), indent=2, sort_keys=True) + "\n").encode("utf-8")
    rendered["RESULTS.md"] = results_note(result).encode("utf-8")
    manifest = {
        "algorithm": "sha256",
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(rendered.items())},
    }
    rendered["artifact_manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return rendered
