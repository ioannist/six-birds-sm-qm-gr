# Preregistered capacity-to-state convention

## Convention

This step fixes one declared convention before evaluating any fiber. For every positive exact rational edge capacity
`c`, define the ordered probability `p(c)=c/(1+c)` and insert the normalized qubit-pair state

`sqrt(p(c)) |00> + sqrt(1-p(c)) |11>`.

The stored edge orientation fixes which Schmidt coefficient is first. Because `p(c)` is strictly increasing for
positive `c`, the ordered edge-state map is injective. The exact rational calculation of `p` precedes the numerical
square root. This convention has identifier `ordered_qubit_schmidt_c_over_one_plus_c_v1` and bond dimension 2. It is applied
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
complex128/SVD allowance of `5e-11` nats. The pairwise allowance is the sum of the two state
allowances. This is a comparison policy, not a propagated forward-error certificate.

- `EQUAL_WITHIN_ALLOWANCE`: absolute entropy difference is at most the pairwise allowance.
- `SPLIT_BEYOND_ALLOWANCE`: difference exceeds `4` times the pairwise allowance.
- Marginal values between those thresholds are recomputed at `80` decimal digits for the
  Schmidt-entropy evaluation. They remain `INDETERMINATE` unless they cross one of the same thresholds.
- Pair verdict: `SPLIT` if any subset splits; `COINCIDE` if every subset is equal; otherwise `INDETERMINATE`.

The high-precision path reevaluates the entropy of the fixed contracted complex128 state. It does not recreate lost
tensor-contraction digits; that limitation is covered only by the declared allowance and is stated rather than
hidden. Boundary-state equality is separately tested using an L2 allowance of `5e-10` and is
never inferred from entropy equality.

Two named witnesses are additionally reevaluated at `80` decimal digits from their fixed
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
