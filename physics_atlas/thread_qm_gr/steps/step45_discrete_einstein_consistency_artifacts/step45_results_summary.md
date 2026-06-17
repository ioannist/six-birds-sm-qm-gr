# Step 45 Results Summary

## Honest Grade And Near-Wall First

This is a recognition-level finite analogue of the statement that first laws for all regions imply a linearized gravitational equation of state. The actual result here is a discrete RT-consistency constraint, not a dynamical equation, not a continuum tensor equation, and not a local bulk equation of motion. It does not derive the full continuum Einstein tensor, does not compute Newton's constant, does not certify frame transfer, and is not a quantum-gravity solution. The continuum step from this finite consistency condition to a local differential-geometry equation remains the standing frontier.

The cut-incidence matrix `M` is built from the unperturbed min-cut edge incidence. This linearization is a fixed-cut-chamber RT constraint, valid only while the active minimal surface does not change. Perturbations that change the active min-cut pattern require recomputing `M`.

## Variable-Capacity Geometry

The Step 42 graph is treated as a variable-capacity geometry with `14` edge-capacity variables. The region set has `38` equations: all singleton boundary regions, all boundary pairs, plus left-all and right-all regions. The linearized RT condition is:

`M . delta_c = delta_S`.

## Cut-Incidence Rank And Constraints

| quantity | value |
|---|---:|
| num regions | 38 |
| num edges | 14 |
| rank(M) | 10 |
| cokernel dimension | 28 |

The nonzero cokernel gives the discrete consistency condition `P_perp delta_S = 0`.

## Teeth

| perturbation | residual |
|---|---:|
| RT-preserving `delta_S=M.delta_c` | 9.2513644228e-17 |
| generic contracted-state perturbation | 0.0418931924111 |

The RT-preserving control satisfies the condition. The generic perturbation is computed independently from contracted-state entropies and violates the condition, so the constraint is non-vacuous.

## Supporting Refinement

`refinement_trend_step45.csv` carries forward the Step 42 RT saturation trend and Step 44 MMI-in-cone trend: the finite carrier approaches the holographic structure while retaining the forbidden-region signature.

## Verdict

`DISCRETE_RT_CONSISTENCY_CONSTRAINT_DERIVED`.
