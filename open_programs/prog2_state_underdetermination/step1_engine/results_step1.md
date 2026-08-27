# PROG2 Step 1 — explicit dense numerical contracted-state entropy engine

## What was computed

A labelled finite tensor network is built from explicit dense vertex tensors and contracted over every internal
bond. The normalized result is an explicit tensor on the ordered boundary Hilbert space. The entropy module then
computes numerical reduced-state spectra from that tensor alone, for all boundary subsets. It has no graph, capacity,
area, or cut input. The deterministic family uses copy tensors; the random family uses fixed seeded complex
Gaussian tensors. Natural logarithms and complex128/SVD numerics are used throughout; this is not exact arithmetic.

The continuous weights of the P1-v3 cut carriers are retained as provenance, not coerced into Hilbert-space
dimensions. Every tensor edge instead carries an explicit positive integer bond dimension. The survivor census
uses uniform D=2,3,4 so topology is held fixed while state-space size changes.
Random survivor tensors use the independent namespace `prog2_step2_tensor_seed_v1` with payload
`(namespace, carrier_name, D, replicate)`. The P1 capacity seed remains provenance and is absent from that payload.
A separate heterogeneous check contracts edge dimensions `2|3` to a boundary
state of shape `2x3` and computes all `4` subsets.

## Calibration controls

Boundary order below is `[EMPTY, A, B, AB]`.

- Entangled-edge structured contraction: `['0', '0.693147180559945', '0.693147180559945', '0']` nats.
- Disconnected structured contraction: `['0', '0', '0', '0']` nats.
- Internal-gauge transformed contraction: `['0', '0.693147180559945', '0.693147180559945', '0']` nats.
- `ln(2) = 0.693147180559945`. The entangled and product Schmidt ranks across A|B are 2 and 1.
- Maximum injective-control entropy difference: `0.693147180559945` nats.
- Gauge-pair state residual: `1.18898674219135e-16`; entropy-vector residual: `1.11022302462516e-16`.

The different Schmidt ranks prove that the injective pair cannot be related by the implemented internal gauge,
algebraic tensor merges, or single-boundary local unitaries. Thus the engine does distinguish at least one bulk
difference. Conversely, the explicit g/g^-1 pair is a certified degeneracy control.

## Reviewer-fix regressions

- Seed namespace: all `39` random survivor rows changed state and entropy
  digests relative to the legacy source-seed-coupled tensors, both against the actual pre-fix entropy policy
  and with both tensor families evaluated under the corrected policy. This is expected because the tensors are new. Mutating the stored P1
  seed provenance and every frozen carrier `source_weight` while holding topology and tensor seed fixed leaves
  state and entropy digests unchanged (`b27a0ae75a10f9fe81e01e3aad492c83decbe825b966d4f1f5436c2c9618019e` and
  `dd4f6eed09a3eef0f5d8e107b8fd437c45f6ad6f8c6892916f1aa09734a14fc7`).
- Small Schmidt weight: the state with probabilities `(1-1e-14, 1e-14)` reports entropy
  `3.323539202407927e-13` nats at tolerance `1e-13`,
  numerical rank `1`, discarded diagnostic mass
  `9.9999999999999984e-15`, and truncation-error bound
  `3.323619130191663e-13` nats. The reported entropy
  includes the small probability; the tolerance only diagnoses a hypothetical truncation. The bound covers
  truncation error, not floating-point SVD roundoff.
- Boundary unitary: a nonsymmetric complex unitary is applied conventionally as `U|psi>`. The network
  contraction agrees with the independently written `np.einsum('ij,jb->ib', U, psi)` expectation.

The complete tolerance sweep is in `entropy_numerical_accountability_step1.csv`; all legacy/new entropy
digests are in `seed_namespace_change_step1.csv`.

## State-level gauge library

| move | certified relation | state residual | entropy residual |
|---|---|---:|---:|
| internal_leg_g_g_inverse | boundary_state_equal | 1.18898674219135e-16 | 1.11022302462516e-16 |
| series_tensor_merge | boundary_state_equal | 0 | 0 |
| parallel_index_product_merge | boundary_state_equal | 0 | 0 |
| single_boundary_local_unitary | state_related_by_explicit_local_unitary | 0 | 0 |

Internal g/g^-1 cancellation, a boundary-free bivalent series merge, and a parallel-index product merge
leave the contracted boundary state invariant to machine precision. The fourth move applies an explicit
unitary to one boundary leg; the recomputed state equals that local-unitary action and the full entropy vector
is unchanged.

## Survivor-scale same-boundary control

On `K23_bipartite__b6__leaf_offset0` at D=2 with `6`
boundary legs, the explicit mutation `<I1+I2>.flat[0] += 0.75+0.25j; renormalize vertex tensor` changes the entropy
vector by `0.2844096505956` nats at witness region
`B0|B2|B4`. The base/mutated entropy digests are
`dd4f6eed09a3eef0f5d8e107b8fd437c45f6ad6f8c6892916f1aa09734a14fc7` /
`28023cab151ec03f77f1177296b9c9ad95f0d7cfe3e511ff5608df18a6efef81`. Since every implemented gauge-library move
preserves the full entropy vector, this difference is a gauge-invariant obstruction to library equivalence.

## P1-v3 survivor tractability

All `13` certified graph-level survivors were reconstructed after the five-move closure.
Every listed case contracted to a nonzero explicit boundary state and produced all 2^|T| entropies.

| tensor family | bond dimension | survivor cases passed |
|---|---:|---:|
| seeded_random_complex | 2 | 13/13 |
| seeded_random_complex | 3 | 13/13 |
| seeded_random_complex | 4 | 13/13 |
| structured_copy | 2 | 13/13 |

The largest complement-symmetry residual across the census is `2.77555756156289e-15`. Boundary counts
are 6–8; D=4 therefore reaches 65,536 explicit amplitudes and a largest balanced Schmidt side of 256.
No carrier-specific obstruction occurs through D=4.

The certified all-13 runtime envelope stops at D=4. D=5 and D=6 are typed
`OUTSIDE_STEP1_RUNTIME_ENVELOPE_NOT_A_FAILURE`: for eight boundaries the state sizes are 390,625 and
1,679,616 amplitudes, while the full-vector dense-SVD leading cost scales as 2^8 O(D^12). Thus the operational
full-census wall begins at D=5 in this step; it is a declared validation budget, not a mathematical or
topology-specific non-tractability result.

## Anti-bypass result

`state_entropy.py` imports only standard-library iteration/typing/dataclass support and NumPy. The audit traverses the complete
reachable entropy call graph, including normalization and Schmidt-spectrum routines. Structural dataflow and
mutation gates verify that cut-derived values cannot enter tensors, dimensions, entropy tolerances, or
post-processing; cut machinery selects the frozen topology and supplies provenance only.

## Obstruction / semantic finding

The P1-v3 source weights are generic rational capacities and generally are not logarithms of integers. There
is therefore no canonical exact map from those cut weights to tensor bond dimensions. Step 1 does not invent
one: it records the weights and evaluates explicitly declared integer dimensions. Any later state-level search
must declare its capacity-to-Hilbert-space convention or work directly with integer bond dimensions.

## Step-1 disposition

**DENSE_NUMERICAL_ENGINE_AND_CALIBRATION_CONTROLS_CERTIFIED.** This is infrastructure only. No pair of physically
quotiented bulk geometries with equal contracted-state entropy vectors is claimed or searched for here.
