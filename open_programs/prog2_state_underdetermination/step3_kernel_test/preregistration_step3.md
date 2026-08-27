# PROG2 Step 3 preregistration

Frozen before the first Step-3 fiber computation on 2026-08-27. This document fixes the complete evaluation family, aggregation rule, and stopping rule. Outcomes will not be filtered or silently dropped.

## Convention and tensor family

Every member maps each positive exact-rational capacity independently to an ordered Schmidt spectrum. No cut value, active-cut direction, fiber identifier, or result may enter the map. Capacity-independent tensors and boundary labels are transported unchanged across derivative evaluations.

| member | bond dimension | tensor family | ordered edge probability spectrum |
|---|---:|---|---|
| `R2_L1` | 2 | Step-1 `seeded_random_complex` | `q=(c,1)/(c+1)`; this is the Step-2 convention |
| `R2_L2` | 2 | Step-1 `seeded_random_complex` | `q=(c^2,1)/(c^2+1)` |
| `C2_L1` | 2 | Step-1 `structured_copy` | `q=(c,1)/(c+1)` |
| `R3_S11` | 3 | Step-1 `seeded_random_complex` | normalize `(c^alpha,1,c^-beta)` at `(alpha,beta)=(1,1)` |
| `R3_S21` | 3 | Step-1 `seeded_random_complex` | normalize `(c^alpha,1,c^-beta)` at `(alpha,beta)=(2,1)` |

The corresponding edge-state coefficients are the positive square roots of the ordered probabilities. Each ordered map is injective on `c>0`: for `L` members the first/second probability ratio is `c^alpha`; for `S` members it is also `c^alpha`. The `L` family is a logistic odds encoding; the three-level `S` family adds an independently varying inverse-capacity tail while retaining an explicit reference component. These are declared finite-dimensional encodings, not canonical physics.

The finite parameter grid is exactly `L: alpha in {1,2}` where listed and `S: (alpha,beta) in {(1,1),(2,1)}`. No parameter value will be added or removed in response to an outcome. The tensor families are the Step-1 seeded-random family at `D in {2,3}` and the Step-1 copy family at `D=2`.

## Seeds and identifications

Random tensors use the closed Step-1 namespace and rule `sha256("prog2_step2_tensor_namespace_v1|carrier|D|replicate=0")[:8]`, with the same `(carrier,D,replicate)` for every convention member and every cut-kernel direction on that carrier. The P1/PROG3 capacity seed remains provenance only. Copy tensors are deterministic and have seed `NONE`. Boundary labels, Hilbert-space dimensions, edge orientations, vertex order, and tensor entries not supplied by the capacity convention are fixed across all derivatives of a case.

## Jacobian and numerical policy

For every one of the 19 pinned fibers and all five members (95 published rows), compute the full `2^|T| by |E|` entropy Jacobian at the exact-rational base weighting. The implementation differentiates the declared Schmidt coefficients analytically, contracts the corresponding boundary-state tangent analytically, and evaluates the von Neumann entropy directional derivative from the reduced-density-matrix tangent. Empty/full-subset rows are retained.

The imported active-cut kernel basis is exact rational/integer evidence. For each distinct `(carrier, PROG3 provenance seed, member)` base case, form `R=J_state V_cut`; its singular rank is assessed with preregistered allowance

`tau = max(5e-8, 1e-8 * sigma_max(R))`.

The analytic projected derivative is checked by central differences along every imported cut-kernel basis vector at three steps `h0`, `h0/2`, `h0/4`, where `h0=min(2^-12, 0.05*min(c_e/|v_e| for v_e!=0))`. A column is stable when the last two finite-difference vectors differ by at most `max(2e-7, 2e-5*max_norm)`. These are preregistered numerical allowances, not forward-error certificates.

A nonzero intersection direction is classified:

- `SYMMETRY_PROTECTED` only when an identified analytic state symmetry supplies the null direction and the numerical Jacobian corroborates it. For `C2_L1`, a connected copy network is a two-term GHZ state whose amplitude odds depend only on `P=product_e c_e`; exact tangent directions satisfying `sum_e v_e/c_e=0` are protected by this product-level-set symmetry.
- `CERTIFIED-NULL` only if a genuine interval/forward-error certificate is supplied. No finite-difference result alone receives this label.
- `NUMERICAL-ARTIFACT` when apparent nullity fails the step sweep or precision/allowance checks. It is not a continuation candidate.

All numerical state/entropy conclusions are graded `DENSE_NUMERICAL_EVIDENCE`. The word “certified” applies in this step only to the imported exact-rational cut-kernel computation or to a future genuine numerical certificate, not to an allowance.

## Aggregation and continuation eligibility

The primary unit is `(fiber, convention member)`. Results are also summarized by member and carrier family without reweighting: each of the 95 primary rows receives equal count. The aggregate verdict is:

1. `TRIVIAL-INTERSECTION-EVERYWHERE` only if all 95 rows have dimension zero.
2. Otherwise `STEP4-CANDIDATES-PRESENT` iff at least one nonzero direction is `SYMMETRY_PROTECTED` or `CERTIFIED-NULL`.
3. If all apparent nonzero directions are `NUMERICAL-ARTIFACT`, report `NO-ELIGIBLE-CANDIDATE` and list every artifact row.

Only protected or genuinely certified-null directions are eligible for Step 4. Step 3 performs no finite continuation and makes no full finite-displacement entropy comparison for those directions.

## Analytically coincident can-fail controls

Two survivor-scale `R2_L1` controls are fixed before evaluation: the first internal edge of `wheel_W4__b8__leaf_offset0` at provenance seed 47 and the first internal edge of `K23_bipartite__b6__leaf_offset0` at provenance seed 31. For each, replace its exact capacity `c` by `1/c`. Because `q(1/c)` swaps the two Schmidt probabilities, apply the explicit Pauli-X Schmidt-basis relabeling on both endpoints of that internal edge. The resulting contraction is the same state after an internal basis relabeling. The Step-2 comparison policy must return `COINCIDE`, and the pair must be typed `STATE_LEVEL_GAUGE`, never as an underdetermination candidate.

## Stopping rule

Stop after all 95 rows, all imported basis directions, three derivative-check step sizes, and both controls have been evaluated and published. Do not add conventions, dimensions, tensor replicates, seeds, or carriers after seeing results. Do not continue any surviving direction to finite displacement in this step. A runtime obstruction is reported as `UNEVALUATED_RESOURCE_OBSTRUCTION` with the affected rows retained; it does not authorize a replacement case or silent omission.
