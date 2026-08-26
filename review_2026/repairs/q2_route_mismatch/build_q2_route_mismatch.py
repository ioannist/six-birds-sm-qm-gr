#!/usr/bin/env python3
"""Write deterministic Q2 route-mismatch repair artifacts."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
from pathlib import Path
from typing import Any

import q2_route_mismatch as core


HERE = Path(__file__).resolve().parent


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    if not rows:
        raise ValueError("empty CSV")
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def markdown(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def claim_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    by_id = {row["pair_id"]: row for row in result["candidates"]}
    return [
        {"claim": "published E_QM and E_GR do not commute", "status": "REFUTED_ON_PUBLISHED_CARRIER",
         "evidence": "exact commutator zero; defect set empty; 0.5 is table distance"},
        {"claim": "nonlinear source-projection repair candidate", "status": "COMPUTED_NONCOMMUTING_MOTIVATION_SUBJECT_TO_EDDY",
         "evidence": f"defects={by_id['conditional_mean_vs_nonlinear_source_projection']['defect_set_cardinality']}; spectral_norm={by_id['conditional_mean_vs_nonlinear_source_projection']['commutator_spectral_norm']}"},
        {"claim": "nonfactorizing-access repair candidate", "status": "COMPUTED_NONCOMMUTING_COARSE_GRAINING_IMPORTED",
         "evidence": f"defects={by_id['nonfactorizing_conditional_means']['defect_set_cardinality']}; spectral_norm={by_id['nonfactorizing_conditional_means']['commutator_spectral_norm']}"},
        {"claim": "completion algebra can detect commuting cases", "status": "LANDED_BY_CONTROL",
         "evidence": "nested coordinate control exact commutator zero"},
    ]


def results_note(result: dict[str, Any]) -> str:
    reproduction = result["published"]
    claims = claim_rows(result)
    return f"""# Q2-REPAIR-1: route-mismatch repair

## Published result reproduced and corrected

{markdown(reproduction, ['encoding', 'completion_table_distance_raw', 'completion_table_distance_normalized', 'commutator_defect_cardinality', 'commutator_spectral_norm', 'commutator_on_encoded_table_norm'])}

The published `0.5` is `||E_QM(C)-E_GR(C)||_F/||C||_F` on the 0/1 table, not a commutator. Re-encoding the same states as plus/minus one changes that distance to `1/sqrt(2)`. Both completions are exactly idempotent, while `E_QM E_GR = E_GR E_QM` exactly: the defect set is empty and the commutator norm is zero in both encodings.

The reason is structural. On a uniform product cube, conditional expectation onto coordinates `A` followed by conditional expectation onto coordinates `B` averages over the union of their hidden coordinates. Order is irrelevant, and both compositions equal conditional expectation onto `A intersect B`. Here `A={{d0,d1,d2}}`, `B={{d0,d2,d3}}`, and the common result is the completion visible on `{{d0,d2}}`. Coordinate overlap alone does not create non-commutativity; nonfactorizing access structures or a genuinely different completion operation are required.

## Candidate table

{markdown(result['candidates'], ['pair_id', 'family', 'left_idempotent', 'right_idempotent', 'commutes', 'defect_set_cardinality', 'commutator_spectral_norm', 'normalized_hilbert_schmidt_norm'])}

The defect set is the exact finite set of carrier rows at which the two composition distributions differ; all rows and exact rational distributions are exported. The primary magnitude is the spectral norm of the exact commutator matrix. It is independent of coordinate value encoding and invariant under carrier relabeling by permutation conjugacy. All 24 coordinate permutations were checked for every pair.

The nonlinear candidate makes the operations genuinely different: the first completion averages over the curvature bit, whereas the second retracts onto `d3 = d0 OR d2`, a thresholded source-consistency constraint motivated by Step26's density and gradient/transport contributions. Its non-commutativity is exact on all 16 states. What remains imported is the Boolean threshold and the finite identification of the transport bit with the gradient source term.

The second candidate keeps both operations as conditional means but uses aggregate access partitions `(d0,d1+d2)` and `(d0,d2+d3)`. Their fibers do not form a product, and the exact commutator is nonzero on 12 states. The aggregate readouts are an explicit coarse-graining ansatz, not a frozen track prediction.

## Claim ledger and outcome

{markdown(claims, ['claim', 'status', 'evidence'])}

**{result['outcome']}**. A genuine non-commuting finite completion pair exists, so there is a mathematically valid repaired-Q2 candidate. It does not rescue the published calculation: the published pair commutes, and its claimed mismatch was a mislabeled, encoding-dependent table distance. Whether the nonlinear candidate faithfully represents “quantize then curve versus curve then quantize” remains a motivation ruling for Eddy; absent that ruling, the paper must retract the claim for its stated carrier and operators.
"""


def design_note() -> str:
    return """# Q2-REPAIR-1 design

## Endomorphisms and defect

A completion is a 16-by-16 rational row-stochastic matrix `E` acting on any state table `T` by `T -> E T`. Conditional means average uniformly over partition fibers. A deterministic constrained projection is represented by the pullback matrix of an idempotent carrier retraction. Idempotence is tested exactly as `E^2 == E` using rational arithmetic.

For a pair `(E1,E2)`, the exact defect matrix is `[E1,E2] = E1 E2 - E2 E1`. The finite defect set contains precisely those carrier rows whose commutator row is nonzero. The reported primary magnitude is the spectral norm of this matrix; normalized Hilbert--Schmidt norm is supplied as a second invariant diagnostic.

## Invariance

The operator norm does not use numeric state labels, so affine recoding 0/1 to plus/minus one leaves it unchanged. Coordinate permutations induce a permutation matrix `S` and transform every completion as `E -> S E S^-1`; spectral and Hilbert--Schmidt norms and defect cardinality are conjugacy invariant. The implementation checks every one of the 24 coordinate permutations, exact idempotence after conjugation, and both encodings.

## Physical typing

The Step48 Boolean mode carrier and conditional-mean implementation and the Step26 stress-energy machinery are imported under literal SHA-256 pins. The nonlinear constraint uses Step26's two source types but declares its Boolean threshold as an imported finite discretization. The nonfactorizing partitions are motivated coarse access structures but remain an ansatz. These declarations prevent computed non-commutativity from being silently promoted to a continuum quantum-gravity theorem.
"""


def render(result: dict[str, Any]) -> dict[str, bytes]:
    claims = claim_rows(result)
    schema = {
        "artifact": "Q2-REPAIR-1 route-mismatch repair", "schema_version": 1,
        "carrier": {"states": 16, "coordinates": list(core.STATE_NAMES), "encoding": "operator algebra independent of labels"},
        "completion": "rational row-stochastic endomorphism E acting by T -> E T",
        "defect": "exact nonzero rows of E1E2-E2E1",
        "invariant_magnitude": "spectral norm of commutator; normalized Hilbert-Schmidt also reported",
        "row_counts": {"candidate_pairs": len(result["candidates"]), "defect_rows": len(result["defects"]),
                       "matrix_rows": len(result["matrices"]), "invariance_rows": len(result["invariance"])},
        "outcome": result["outcome"], "hashes": result["hashes"],
    }
    payloads = {
        "q2_dependency_pins.csv": csv_bytes(result["pins"]),
        "q2_candidate_pairs.csv": csv_bytes(result["candidates"]),
        "q2_exact_defect_set.csv": csv_bytes(result["defects"]),
        "q2_completion_matrices.csv": csv_bytes(result["matrices"]),
        "q2_published_reproduction.csv": csv_bytes(result["published"]),
        "q2_invariance_checks.csv": csv_bytes(result["invariance"]),
        "q2_step26_source_evidence.csv": csv_bytes(result["source_evidence"]),
        "q2_claim_ledger.csv": csv_bytes(claims),
        "q2_schema.json": json_bytes(schema),
        "RESULTS.md": results_note(result).encode(), "DESIGN.md": design_note().encode(),
    }
    manifest = {name: hashlib.sha256(payload).hexdigest() for name, payload in sorted(payloads.items())}
    payloads["q2_artifact_manifest.json"] = json_bytes(manifest)
    return payloads


def main() -> None:
    started = time.perf_counter()
    result = core.run()
    for name, payload in render(result).items():
        (HERE / name).write_bytes(payload)
    noncommuting = sum(not row["commutes"] for row in result["candidates"])
    print(f"Q2 build PASS: pairs={len(result['candidates'])} noncommuting={noncommuting} "
          f"defect_rows={len(result['defects'])} outcome={result['outcome']} "
          f"elapsed_seconds={time.perf_counter()-started:.3f}")


if __name__ == "__main__":
    main()
