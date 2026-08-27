# PROG2 Step 6 results — exact gauge collapse

## Evidence taxonomy

`COMPUTED` rows are rebuilt from the stored Step-4/Step-5 algebraic endpoints by exact arithmetic or explicit finite enumeration. `PROVED_BY_DEFINITION` rows are consequences of the Step-5 stipulation that capacity labels remain ontic under internal tensor gauge; `EXTERNAL_REPRODUCED` rows rerun the staged external floating-point audit and are controls, not the exact certificate.

## Per-pair certificate table

| pair | carrier | field degree | V/E | product equal | connected | rank / left nullity | exponent identities | float control max | retyped result |
|---|---|---:|---:|---|---|---|---|---:|---|
| cand_01 | `wheel_W4__b8__leaf_offset0` | 2 | 12/14 | yes (`COMPUTED`) | yes (`COMPUTED`) | 11/1, ones=yes (`COMPUTED`) | target=yes, edge=yes (`COMPUTED`) | 1.569e-16 (`EXTERNAL_REPRODUCED`) | `EXACT_JOINT_MAP_FIBER; TENSOR_GAUGE_COLLAPSED` |
| cand_02 | `wheel_W4__b8__leaf_offset0` | 2 | 12/14 | yes (`COMPUTED`) | yes (`COMPUTED`) | 11/1, ones=yes (`COMPUTED`) | target=yes, edge=yes (`COMPUTED`) | 3.331e-16 (`EXTERNAL_REPRODUCED`) | `EXACT_JOINT_MAP_FIBER; TENSOR_GAUGE_COLLAPSED` |
| cand_03 | `wheel_W4__b8__leaf_offset1` | 2 | 12/12 | yes (`COMPUTED`) | yes (`COMPUTED`) | 11/1, ones=yes (`COMPUTED`) | target=yes, edge=yes (`COMPUTED`) | 4.441e-16 (`EXTERNAL_REPRODUCED`) | `EXACT_JOINT_MAP_FIBER; TENSOR_GAUGE_COLLAPSED` |
| cand_04 | `wheel_W4__b8__leaf_offset1` | 2 | 12/12 | yes (`COMPUTED`) | yes (`COMPUTED`) | 11/1, ones=yes (`COMPUTED`) | target=yes, edge=yes (`COMPUTED`) | 2.776e-16 (`EXTERNAL_REPRODUCED`) | `EXACT_JOINT_MAP_FIBER; TENSOR_GAUGE_COLLAPSED` |
| cand_05 | `K23_bipartite__b8__dual_gateway` | 2 | 12/12 | yes (`COMPUTED`) | yes (`COMPUTED`) | 11/1, ones=yes (`COMPUTED`) | target=yes, edge=yes (`COMPUTED`) | 2.220e-16 (`EXTERNAL_REPRODUCED`) | `EXACT_JOINT_MAP_FIBER; TENSOR_GAUGE_COLLAPSED` |
| cand_06 | `K23_bipartite__b8__dual_gateway` | 5 | 12/13 | yes (`COMPUTED`) | yes (`COMPUTED`) | 11/1, ones=yes (`COMPUTED`) | target=yes, edge=yes (`COMPUTED`) | 3.456e-16 (`EXTERNAL_REPRODUCED`) | `EXACT_JOINT_MAP_FIBER; TENSOR_GAUGE_COLLAPSED` |

All six graphs have 12 vertices; the exact oriented-incidence rank is 11 and the left kernel is the component-wise all-ones vector. The exact product relation eliminates one formal log-ratio, after which the exported rational gauge-exponent basis satisfies `B X = D R` identically and every edge's `g,g^-1` exponent vectors cancel.

## Product lemma

On any fixed connected `C2_L1` carrier under the declared convention, copy constraints admit only the all-zero and all-one global assignments, so the normalized state factors through the total edge-capacity product. For every stored instance, exhaustive binary assignment enumeration finds exactly those two supports, and exact endpoint arithmetic gives the same product and normalized squared amplitudes `P/(1+P)` and `1/(1+P)`.

## Retyped outcomes

1. **JOINT-MAP NONINJECTIVITY — exact and unconditional for the six fixed graphs.** Distinct positive algebraic capacity vectors have identical complete terminal cut fingerprints and identical normalized connected-copy boundary states.
2. **GAUGE-COLLAPSE THEOREM — exact and general within `C2_L1`.** On any fixed connected carrier with positive capacities, every equal-product pair admits a diagonal internal-bond gauge up to vertex-wise nonzero scalars. The six stored pairs are exact instances and are tensor-presentation gauge equivalent under Step 5's own intertwiner-admission rule.
3. **DECORATED-CARRIER SEPARATION — conditional.** The exact invariant values `I(c)` differ (`COMPUTED`), but treating that difference as object inequivalence under a relation that forbids internal gauge from acting on capacity labels is `PROVED_BY_DEFINITION`.

The former headline “declared-gauge underdetermination examples” is retired. The honest description is: **exact fibers of the joint cut/state map, gauge-collapsible at the tensor level, separated by `I(c)` only under the frozen decorated-carrier relation.**

## Numerical cross-check

The staged external audit was rerun unchanged. Its largest residual over all reported balance, local proportionality, raw-state, normalized-state, and scalar-consistency checks is `4.441e-16`; all six rows pass its `1e-10` control threshold. This is `EXTERNAL_REPRODUCED` evidence and is not used to establish exactness.

## Can-fail controls

| control | required failure | exact outcome |
|---|---|---|
| `unequal_product_real_carrier` | `LEFT_KERNEL_PRODUCT_OBSTRUCTION` | PASS (`COMPUTED`); not_applicable |
| `one_edge_orientation_mutation` | `ORIENTATION_DRESSING_MISMATCH_BREAKS_BX_EQ_DR` | PASS (`COMPUTED`); original_orientation_identity_passes=True |
| `disconnected_global_vs_component_products` | `COMPONENTWISE_PRODUCT_OBSTRUCTION` | PASS (`COMPUTED`); componentwise_equal_products_restore_solvability=True |

## Aggregate verdict

`SIX_EXACT_JOINT_MAP_FIBERS__ALL_TENSOR_PRESENTATION_GAUGE_COLLAPSED`

No obstruction was found in the exact certificate route.
