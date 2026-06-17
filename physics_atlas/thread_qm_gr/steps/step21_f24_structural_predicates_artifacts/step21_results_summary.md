# Step 21 Results Summary

## Orientation

Mode B native structuralization.  Step 21 reimplements the Step 20 F24 selector predicates so that each family criterion is computed from a candidate's actual maps, quotients, records, residuals, scope declarations, or closure matrix.

## Active Residual

`R_child_E018_after_F24_predicate_construction_classification`: Step 20 classified `L` by operational predicates, but its implementation still used selector records.  Step 21 removes that shortcut and recomputes the classification structurally.

## Carrier

Finite carrier `H` with eight states over modes `(d0,d1,d2,d3)`.

- Current quotient: `q_QM=(d0,d1,d2)`.
- Role readout: `s=d3`.
- Full role obstruction count: `3`.

## Structural Predicates

Each predicate is computed from maps:

- `MemoryLayer`: `s` factors through a history coordinate, and that coordinate does not factor through `q`.
- `HiddenUpstreamRole`: `s` factors through a latent coordinate outside `q`, and no passing explicit joint object carries it.
- `BridgeMediatedRole`: an explicit joint object has `a∘j=q`, carries `s`, passes native gate checks, and strictly refines `q`.
- `BudgetedRole`: a positive residual is priced and adequately statused while no exact resolution exists.
- `ScopedRole`: a proper sub-carrier makes the role obstruction empty.
- `CoarsenedRole`: a changed coarsened readout makes the split-pair obstruction empty.
- `OutsideRoleScope`: `d3` is outside the declared access scope and named outside.
- `BlockedNonClosure`: closure formation or residual status fails after the other predicates do not fire.

## Verdict

`L_candidate_package` selects uniquely as `BridgeMediatedRole`, recomputed from the maps `π_L`, `to_qm`, `role_from_L`, the native gate checks, and strict-refinement witnesses.

The real-structure controls also separate cleanly:

- `memory_control -> MemoryLayer`
- `hidden_control -> HiddenUpstreamRole`
- `budget_control -> BudgetedRole`
- `scoped_control -> ScopedRole`
- `coarsened_control -> CoarsenedRole`
- `outside_scope_control -> OutsideRoleScope`
- `blocked_control -> BlockedNonClosure`

All eight families are covered, and every candidate fires exactly one predicate.

## Grade

Finite-carrier diagnostic construction.  The structural predicates are candidate operational selectors grounded in the Step 20 FIV source record.

## Current Frontier

The native finding is strengthened: `L` is `BridgeMediatedRole` by structural map computation, not by selector declaration.  Robustness beyond the finite suite remains external review.
