# Step 14 Results Summary

## Orientation

Step 14 tests `RUNG_1_REFINE_FIXEDPOINT` on the Step-13 neutral currency. The active question is whether the compressed currency and its two distinct shadows survive genuine refinement.

This is a rung-coherence test. It does not claim root closure.

## Carrier And Lift

The carrier is the Step-13 currency `u = (d0, d1, d2, d3)` with:

- QM-side shadow: `(d0, d1, d2)`.
- GR-side shadow: `(d0, d2, d3)`.
- Dimensions: `d_QM=3`, `d_GR=3`, `d_u=4`, `d_union=6`.

The stable lift `L_u` is a real non-identity refinement map from level `n` to level `n+1`, duplicating each currency mode block from `N` cells to `2N` cells. The tested transitions are:

- `1->2`: `16` source coordinates to `32` refined coordinates.
- `2->3`: `32` source coordinates to `64` refined coordinates.

The mixing control applies a fine-level mode mixer after the same duplication, mixing shared modes with endpoint-distinct modes.

## Stability Audit

The tested constraint is:

```text
S_QM^{n+1} L_u = L_QM S_QM^n
S_GR^{n+1} L_u = L_GR S_GR^n
```

| case | transition | combined commutator residual | compression | distinct shadows | verdict |
|---|---:|---:|---:|---:|---|
| `stable_lift` | `1->2` | `0.0` | pass | pass | passes |
| `mixing_control` | `1->2` | `0.5612486080160912` | pass | pass | rejected |
| `stable_lift` | `2->3` | `0.0` | pass | pass | passes |
| `mixing_control` | `2->3` | `0.5612486080160912` | pass | pass | rejected |

Observed commutator range: `0.0` to `0.5612486080160912`.

The control fails because compression and distinctness alone are insufficient; the lift must also commute with both shadows.

## Structural Constraint

The durable output is:

`A refinement compatible with the compressed currency must preserve the shared modes {d0,d2}, preserve the two shadow kernels span{d3} and span{d1}, and commute with both endpoint shadows.`

This is recorded in `structural_constraint_step14.md`.

## Verdict

`REFINEMENT-STABLE`: the Step-13 currency survives the tested nontrivial refinement, and the mixing control fails the same commutator test.

This remains a finite-carrier candidate requiring external review. Next move:

`RUNG_3_AUDIT_ON_REFINEMENT_STABLE_CURRENCY`.

