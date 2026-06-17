# Step 15 Results Summary

## Orientation

Step 15 builds `RUNG_3`, the audit rung, on the refinement-stable neutral currency from Steps 13-14. The active question is whether one nontrivial audit functional on `u` can consistently price both endpoint shadows and commute with refinement.

This is a framework-side route-consistency test, not a root closure.

## Audit Construction

Neutral currency:

```text
u = (d0 density, d1 phase, d2 transport, d3 curvature)
QM shadow = (d0, d1, d2)
GR shadow = (d0, d2, d3)
shared modes = {d0, d2}
```

Consistent endpoint audits:

```text
A_QM = (0.70, 0.20, -0.40)
A_GR = (0.70, -0.40, 0.35)
A_u  = (0.70, 0.20, -0.40, 0.35)
```

The coefficients agree on the shared modes `d0` and `d2`, so `A_u` restricts to both endpoint audits.

Route-mismatch control:

```text
A_QM_bad = (0.70, 0.20, -0.40)
A_GR_bad = (0.90, -0.10, 0.35)
```

The shared-mode prices disagree, so no single audit on `u` restricts to both.

## Audit-Consistency Results

| case | level | shared residual | refinement commutator | single audit | verdict |
|---|---:|---:|---:|---:|---|
| `consistent_audit` | 1 | `0.0` | `0.0` | yes | passes |
| `route_mismatch_control` | 1 | `0.4472135954999581` | `0.0` | no | rejected |
| `consistent_audit` | 2 | `0.0` | `0.0` | yes | passes |
| `route_mismatch_control` | 2 | `0.4472135954999581` | `0.0` | no | rejected |

The audit is nontrivial:

- coefficient norm: `0.9013878188659973`.
- coefficient spread: `0.3974528273896162`.

## Structural Constraint

The durable output is:

`A single bridge audit exists iff the two endpoint audits agree on the shared currency modes {d0,d2}; this is the route-consistency condition on the overlap.`

The audit must also commute with the Step-14 refinement lift.

## Verdict

`AUDIT COHERES`: the single audit prices both endpoint descents, commutes with refinement, and the route-mismatch control fails.

This finite-carrier result requires external review. The three framework rungs now cohere on the declared toy carrier:

- `RUNG_2_NEUTRAL_CURRENCY`.
- `RUNG_1_REFINE_FIXEDPOINT_ON_CURRENCY`.
- `RUNG_3_AUDIT_ON_REFINEMENT_STABLE_CURRENCY`.

Next move: `STEP16_FULL_LADDER_DESCENT`.

