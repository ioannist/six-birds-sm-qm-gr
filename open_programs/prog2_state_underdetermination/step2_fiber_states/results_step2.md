# PROG2 Step 2 — state evaluation of exact cut-fingerprint fibers

## Headline

Under the preregistered `ordered_qubit_schmidt_c_over_one_plus_c_v1` convention, the 19 exact PROG3 fibers classify as:

- **SPLIT: 19**
- **COINCIDE: 0**
- **INDETERMINATE: 0**

This result is graded **dense numerical evidence**. The comparison thresholds are preregistered numerical
allowances, not propagated forward-error bounds.

| fiber | carrier | seed | basis | subsets split/equal/indeterminate | max difference (nats) | allowance at witness | verdict |
|---|---|---:|---:|---:|---:|---:|---|
| fiber_001 | wheel_W4__b8__leaf_offset0 | 47 | 0 | 254/2/0 | `0.052856569834453138` | `1e-10` | **SPLIT** |
| fiber_002 | wheel_W4__b8__leaf_offset0 | 47 | 1 | 254/2/0 | `0.072432625522665772` | `1e-10` | **SPLIT** |
| fiber_003 | wheel_W4__b8__leaf_offset0 | 47 | 2 | 254/2/0 | `0.032621396697760374` | `1e-10` | **SPLIT** |
| fiber_004 | wheel_W4__b8__leaf_offset1 | 17 | 0 | 254/2/0 | `0.069840478589280663` | `1e-10` | **SPLIT** |
| fiber_005 | wheel_W4__b8__leaf_offset1 | 17 | 1 | 254/2/0 | `0.11053552257400856` | `1e-10` | **SPLIT** |
| fiber_006 | wheel_W4__b8__leaf_offset1 | 31 | 0 | 254/2/0 | `0.027103070615464242` | `1e-10` | **SPLIT** |
| fiber_007 | wheel_W4__b8__leaf_offset1 | 31 | 1 | 254/2/0 | `0.035949541359241` | `1e-10` | **SPLIT** |
| fiber_008 | K23_bipartite__b6__leaf_offset0 | 31 | 0 | 62/2/0 | `0.031463231334145969` | `1e-10` | **SPLIT** |
| fiber_009 | K23_bipartite__b6__dual_gateway | 47 | 0 | 62/2/0 | `0.13508981139252918` | `1e-10` | **SPLIT** |
| fiber_010 | K23_bipartite__b7__leaf_offset1 | 47 | 0 | 126/2/0 | `0.033562157324373454` | `1e-10` | **SPLIT** |
| fiber_011 | K23_bipartite__b8__leaf_offset0 | 17 | 0 | 254/2/0 | `0.0019187597503522724` | `1e-10` | **SPLIT** |
| fiber_012 | K23_bipartite__b8__leaf_offset1 | 17 | 0 | 254/2/0 | `0.077977303401607634` | `1e-10` | **SPLIT** |
| fiber_013 | K23_bipartite__b8__leaf_offset1 | 31 | 0 | 254/2/0 | `0.10468952010326066` | `1e-10` | **SPLIT** |
| fiber_014 | K23_bipartite__b8__leaf_offset1 | 47 | 0 | 254/2/0 | `0.078040038723277028` | `1e-10` | **SPLIT** |
| fiber_015 | K23_bipartite__b8__dual_gateway | 17 | 0 | 254/2/0 | `0.013774575970591951` | `1e-10` | **SPLIT** |
| fiber_016 | K23_bipartite__b8__dual_gateway | 17 | 1 | 254/2/0 | `0.0093944519398354576` | `1e-10` | **SPLIT** |
| fiber_017 | K23_bipartite__b8__dual_gateway | 31 | 0 | 254/2/0 | `0.045807543126742623` | `1e-10` | **SPLIT** |
| fiber_018 | K23_bipartite__b8__dual_gateway | 31 | 1 | 254/2/0 | `0.0068300103286363933` | `1e-10` | **SPLIT** |
| fiber_019 | K23_bipartite__b8__dual_gateway | 47 | 0 | 254/2/0 | `0.044629577194555292` | `1e-10` | **SPLIT** |

Every subset-level entropy, discarded probability mass, numerical rank, numerical allowance, and classification
is exported in `entropy_comparisons_step2.csv`. Boundary-state residuals and state digests are recorded
separately from entropy-vector verdicts.

## Controls

| control | exact cut change | state residual | max entropy difference | verdict | pass |
|---|---|---:|---:|---|---|
| control_nonkernel_edge0 | True | `0.084043896620266165` | `0.063925997949762392` | SPLIT | True |
| control_step1_internal_gauge | False | `3.7955178808716638e-16` | `1.0408340855860843e-16` | COINCIDE | True |

The preregistered non-kernel edge-0 perturbation has nonzero active-cut Jacobian image, changes the exact
cut fingerprint, and splits the contracted-state entropy vector. The Step-1 internal `g,g^-1` gauge pair
was dressed first by the new capacity convention and still coincides in state and entropy within the allowance.

## High-precision consistency checks

These checks reevaluate entropy at 80 decimal digits from the fixed complex128 contracted states. They
strengthen numerical consistency but are not forward-error certificates for the contraction.

| fiber | region | float difference (nats) | 80-dps difference (nats) | absolute agreement |
|---|---|---:|---:|---:|
| fiber_004 | B1|B4|B5|B6 | `4.0039617538178973e-06` | `0.0000040039617538752956583687075964306245623447466641665` | `5.739834063774040817662581e-17` |
| fiber_011 | B1|B3|B5|B6 | `0.0019187597503522724` | `0.0019187597503521945738885756682634564640466123819351` | `7.784571598445921836173511e-17` |

## Interpretation

For this declared convention and tensor family, the computed contracted-state entropies provide
dense numerical evidence of strict refinement of the complete terminal min-cut fingerprint on every
tested direction fiber. Accordingly, none of the 19 graph-level fibers supplies a numerical
state-level underdetermination candidate in this evaluation. This is a convention-scoped negative
search result, not a proof that no other capacity-to-state map or state family can yield one.

No marginal subset was accepted without the preregistered precision policy. The convention remains the
load-bearing import: it is injective and non-vacuous, but it is not claimed to be uniquely physical.
