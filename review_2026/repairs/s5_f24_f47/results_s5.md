# S5 F24 architecture verdict and F47 measure ablation

## F24 computed architecture

| Family | Forms | Admissible | Closes | Status |
|---|---:|---:|---:|---|
| MemoryLayer | True | True | True | FIRES |
| HiddenUpstreamRole | False | True | True | DOES_NOT_FIRE |
| BridgeMediatedRole | False | True | True | DOES_NOT_FIRE |
| BudgetedRole | True | True | True | FIRES |
| ScopedRole | True | True | False | DOES_NOT_FIRE |
| CoarsenedRole | False | True | False | DOES_NOT_FIRE |
| OutsideRoleScope | False | True | True | DOES_NOT_FIRE |
| BlockedNonClosure | True | True | True | DOES_NOT_FIRE |

Both `MemoryLayer` and `BudgetedRole` fire on the real 468-row admissible carrier. The MemoryLayer is not a boolean placeholder: it is the distinct Step-17 scale carrier, coupled to content by the Step-18 radiative channel, with alternating content/scale reachability iterated to a graph fixed point. **Round-23 ruling: this MemoryLayer closure gate is EXPERIMENTAL/INSUFFICIENT.** Fixed-point reachability on the finite carrier does not establish a physically sufficient independent scale-layer closure, so `MemoryLayer: FIRES` is retained as a computed finite-toy diagnostic, not foundation-grade architecture evidence. The BudgetedRole is a separate finite naturalness/readout ledger attached to the content closure and also reaches a fixed point. At this diagnostic grade the verdict remains `ARCHITECTURE_UNDERDETERMINED_MEMORY_LAYER_AND_BUDGETED_ROLE_BOTH_CLOSE`; the published unique BudgetedRole conclusion does not survive the explicit competitor construction, but the MemoryLayer leg cannot carry a stronger claim without a repaired closure gate.

## Mutation flips

- `mutation_budget_decoupled` fires: `MemoryLayer`.
- `mutation_sealed_e0_scope` fires: `ScopedRole`.

The first mutation removes the budget ledger without altering the coupled scale carrier, leaving a genuine MemoryLayer-only resolution. The second evaluates a sealed proper `e0` subcarrier with the budget disabled: the coupled closure cannot escape the declared scope, so ScopedRole fires while the multi-scale MemoryLayer no longer forms. The validator asserts both firing-set changes.

## F47 surface

| Threshold source | Threshold | Denominator | Selector mass | Fraction | Small at 0.05 | Realized in region |
|---|---:|---|---:|---:|---:|---:|
| step19_legacy | 2.70 | full_product_unweighted | 342/8640 | 0.039583333333 | True | True |
| step19_legacy | 2.70 | admissible_unweighted | 24/468 | 0.051282051282 | False | True |
| step19_legacy | 2.70 | admissible_step8_measure_weighted | 24/534 | 0.044943820225 | True | True |
| step18_upstream | 2.75 | full_product_unweighted | 234/8640 | 0.027083333333 | True | False |
| step18_upstream | 2.75 | admissible_unweighted | 12/468 | 0.025641025641 | True | False |
| step18_upstream | 2.75 | admissible_step8_measure_weighted | 12/534 | 0.022471910112 | True | False |

The legacy Step-19 cell is reproduced exactly: `342/8640 = 0.039583333333` at threshold `2.70`, full-product counting, target ratio `1e-4`, and `theta=0.05`.

The defensible headline conditions on the declared 468 admissible rows, weights them by Step-8 `measure_weight` (total measure mass 534), and uses the upstream Step-18 channel threshold `2.75` rather than Step 19's later `2.70`. Its selector mass is `12/534 = 0.022471910112`. It is positive and small at `theta=0.05`, but the realized point is **not** in the region: its score is exactly `2.75`, while the predicate is strict `score > threshold`.

Across denominators and the declared threshold sweep at target ratio `1e-4`, the selector fraction ranges from `0.000000000000` to `0.136752136752`. Including target-ratio sensitivity (`1e-4`, `1e-2`, `1`) expands the range to `0.000000000000` through `0.405982905983`. `SMALL_THETA` changes only the `small` classification, and the full sensitivity CSV reports `theta=0.01,0.025,0.05,0.10,0.15` separately.

## Honest conclusion

F47 remains a finite-toy naturalness reframe, but `3.96%` is not a stable selector number. It moves to `2.247191011236%` in the defensible weighted-admissible/upstream-threshold cell, changes discontinuously across score support points, reaches zero above the largest score, and is sensitive to both the target-ratio convention and `theta`. The realized-point statement is likewise threshold-sensitive: it holds for thresholds below `2.75` and fails at `2.75` under the published strict comparison.
