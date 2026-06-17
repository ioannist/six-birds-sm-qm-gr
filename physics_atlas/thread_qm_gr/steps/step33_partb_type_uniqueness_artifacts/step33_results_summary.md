# Step 33 Results Summary

## Orientation

Step 33 is Part B type-uniqueness for the QM-GR role split.  It applies the structural F24 predicates from Step 21 to the actual finite maps of the candidate package `L`, rather than to controls or declared selectors.

## Active Residual

`R_child_E018_after_T_QG_NoGo_bounded_theorem`: after Program A blocks directed and fused single-object routes in the bounded grammar, the remaining Part B question is whether the lawful reconciliation type is unique.

## Carrier and Maps

The carrier has eight finite states over modes `(d0_density, d1_phase, d2_transport, d3_curvature)`.

- `q_QM = (d0,d1,d2)`.
- `s = d3`.
- `pi_L = (d0,d1,d2,d3)`.
- `to_qm pi_L = q_QM` and `to_role pi_L = s`.
- The native gate proxy for `L` passes all eight gates used by Step 21.

## Computation

`type_uniqueness_step33.py` computes all eight F24 predicates from the actual maps.

Result on `L`:

- `MemoryLayer`: false, no history/record coordinate map is present.
- `HiddenUpstreamRole`: false, no latent coordinate map is present and `L` is explicit/admissible.
- `BridgeMediatedRole`: true, explicit joint quotient passes the eight native gates and carries `q_QM` and `s`.
- `BudgetedRole`: false, exact resolution exists and positive priced residual count is zero.
- `ScopedRole`: false, no proper sub-carrier restriction is used.
- `CoarsenedRole`: false, no coarsened role readout is present.
- `OutsideRoleScope`: false, `d3` is inside the declared scope.
- `BlockedNonClosure`: false, closure forms and `BridgeMediatedRole` fires.

The coarsening search checks every quotient obtained by retaining any subset of `q_QM` modes.  All eight coarsenings leave the role obstruction nonempty; the minimum obstruction count is `3`.  Thus a coarse-graining of `q_QM` does not remove the curvature-role split on this carrier.

## Verdict

Typed verdict: `type_uniqueness_bridge_mediated_role_on_L`.

By the structural F24 predicates, the actual QM-GR package `L` uniquely selects `BridgeMediatedRole` as its resolution family on this finite carrier.  The other seven families are computed-excluded as full reconciliation types in the bounded grammar:

- hidden-latent reconciliation is excluded because `L` is explicit and admissible;
- decoherence-only or GR-as-coarse-grained-QM reconciliation is excluded because coarsening `q_QM` does not empty `O_s`;
- cutoff/residual-only reconciliation is excluded because `L` gives exact finite-map descent residuals;
- regime-only reconciliation is excluded because `L` works on the full carrier;
- memory/record, outside-scope, and blocked-nonclosure alternatives fail their structural predicates.

## Frontier

This closes type-uniqueness only.  Instance-uniqueness remains open: the next step must test whether the co-sourcing common-refinement field package is the unique object inside `BridgeMediatedRole`, or whether multiple mediated packages exist in the bounded grammar.
