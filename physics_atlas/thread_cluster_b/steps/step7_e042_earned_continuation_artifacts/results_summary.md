# Step 7 Results Summary

## Orientation

Step 7 converts the Step 5 R1 weakness into a computed finite-toy result. The old Step 2 post-locus continuation was assigned. Here the post-locus values are outputs of a recurrence `U_good`.

## Lorentzian Curvature Toy

The toy curvature is the Schwarzschild-like Kretschmann form `K(r)=48*M^2/r^6` with `M=1.0`. This is a toy Lorentzian metric shape, not physical modeling.

Computed stress result:

- maximum pre-locus finite `K_lorentzian`: `3298534883328.0`.
- `K_lorentzian` at the locus: `inf`.
- finite `K` increments grow near the locus, so the GR-side defect is non-stabilizing.
- `R_L` approaches the finite value `0.75`; last row `R_L=0.7499999997671694`.

## Earned Continuation

The good finite recurrence is:

`x_next = x - step * K/(K + K_planck)`.

This bounded curvature drive produces finite post-locus states. The last `U_good` output is `-0.7821121792445374`.

The GR evolution and `U_bad` use raw divergent curvature drive. GR terminates at the locus, and `U_bad` fails to continue. This gives the continuation test teeth: finite continuation is not automatic.

## Controls

- Lorentzian `K` diverges: `True`.
- `R_L` stabilizes: `True`.
- GR terminates: `True`.
- `U_good` produces finite post-locus outputs by rule: `True`.
- `U_bad` fails to continue: `True`.

## Verdict

`E042_earned_continuation_constructed_finite_toy`.

The continuation is now earned by a finite evolution law, not assigned by `L_defined=True`. The Lorentzian curvature toy preserves the divergence-to-finite-stable shape. The metric and recurrence are still toys; continuous/gauge/diffeomorphism frame transfer remains open.
