# Step 37 Results Summary

## Orientation

Step 37 tests the external reviewer's carrier objection: Step 34's instance-uniqueness might be an axis-aligned coordinate-row artifact.  The mediator space is widened to general-linear non-coordinate readouts and nonlinear polynomial readouts on the same finite carrier.

## Carrier

The computation reuses the Step 34 finite carrier:

- 8 states in `R^4`;
- `q_QM=(d0,d1,d2)`;
- `q_GR=(d0,d2,d3)`;
- `L=eye(4)`.

## General-Linear Mediators

`linear_mediators_step37.csv` records 14 sampled linear mediators:

- 8 random invertible non-axis-aligned `4x4` readouts;
- 5 random rank-3 too-small readouts;
- 1 overcomplete 5-row linear readout.

Results:

- every admissible-minimal linear mediator is `iso_to_L`;
- every rank-3 mediator fails to carry both endpoints;
- the overcomplete mediator carries both but is non-minimal.

## Nonlinear Mediators

`nonlinear_mediators_step37.csv` records 6 polynomial readouts tested with degree-3 polynomial descent/equivalence.

Results:

- every admissible-minimal nonlinear mediator is `iso_to_L`;
- no actual nonlinear mediator is `inequivalent_minimal`;
- some nonlinear presentations have fewer or more coordinates than `L`, but because they are mutually recoverable with `L` on the finite carrier, they are equivalent presentations rather than new mediators.

This is the key finite-carrier point: nonlinear presentation dimension is not the equivalence criterion; mutual recoverability preserving endpoint descents is.

## Positive-Detection Control

The planted strict-degenerate control has two inequivalent minimal mediators:

- `control_mediator_x_partition`;
- `control_mediator_y_partition`.

Both carry the control endpoints, both are strict/minimal, and neither factors through the other (`to_other_res=0.866025`, `from_other_res=0.866025`).  The search reports `positive_detection_detected=True`, so the robustness screen can return non-uniqueness when non-uniqueness is present in the tested grammar.

## Verdict

Typed verdict: `instance_uniqueness_robust_general_linear_nonlinear_tested`.

On the declared finite carrier, all sampled admissible-minimal general-linear mediators and all constructed admissible-minimal nonlinear polynomial mediators are equivalent to `L`.  No inequivalent minimal mediator appears.  The positive-detection control passes, so the uniqueness-survives verdict is not rigged to always return uniqueness.

## Nonclaim

This strengthens Step 34 from coordinate-only to general-linear plus nonlinear-tested on the declared finite carrier.  It is not a proof for all continuous, Lorentzian, gauge, diffeomorphism-quotient, or richer physical carriers.  External frame-transfer review remains the standing gate.
