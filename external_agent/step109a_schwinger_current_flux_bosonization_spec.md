# step109a reference construction — anomaly cocycle to bosonization carrier

## Finite cell

- Compact spatial circle with antiperiodic massless Dirac fermion.
- Eight half-integer momentum sites per chirality (the minimum even cutoff for which held-out mode `n=2` is central on both the sea vacuum and its first current excitation):
  `{-7/2,-5/2,-3/2,-1/2,+1/2,+3/2,+5/2,+7/2}`.
- Right sea fills negative momenta; left sea fills positive momenta.
- Fermi seam: `-1/2 | +1/2`.
- Zero global charge/flux sector; compact holonomy winding probes the current–flux closure.
- Training data: current mode `n=1`, holonomy winding `w=1`.
- Held out: `n=2`, `w=2`, and the `n=2` Euclidean continuation.

## Strict package obstruction

The lower current package retains the completed current-displacement loop but has no central coordinate. The two ordered lifts have the same closed base composite. Exact CAR recombination on the filled sea yields, per chirality,

`<Omega|J_- J_+|Omega> = 1`,
`<Omega|J_+ J_-|Omega> = 0`.

The vector–axial cocycle is therefore `c_1=2`. Independently, one compact holonomy winding gives

`Delta N_R=+1`, `Delta N_L=-1`, `Delta Q=0`, `Delta Q_5=2`.

The same compact `U(1)` period `2*pi` normalizes both obstruction registers. Their unique common closure coefficient is

`alpha_* = c_1/(L q_1) = Delta Q_5/(2*pi) = 1/pi`.

The driver realizes this as an idempotent endomap on a candidate coefficient and verifies zero residual in both registers.

## Promoted carrier

Set `beta=sqrt(alpha_*)`. The promoted current–electric-flux carrier obeys

`j^mu = beta epsilon^(mu nu) d_nu phi`,
`E = -g beta phi`,
`(box + g^2 alpha_*) phi = 0`.

Therefore its SAU scalar shadow is

`C(U_phi)=M/g=sqrt(alpha_*)=1/sqrt(pi)`.

No vacuum-polarization tensor, determinant, full transfer matrix, fitted correlator tail, or benchmark mass is used.

## Held-out checks

- Exact CAR at `n=2`: cocycle `4`; carrier prediction `4`; lower package `0`.
- Spectral flow at `w=2`: `Delta Q_5=4`; carrier prediction `4`; lower package `0`.
- At `L=2*pi`, `g=1`, `tau=1`, `n=2`:
  - promoted transfer: `exp(-sqrt(4+1/pi)) = 0.125173519144966...`;
  - lower branchwise transfer: `exp(-2) = 0.135335283236613...`.
- Erasing the filled sea while retaining the same `U(1)` period kills the cocycle, closure coefficient, and mass.
- The cocycle values are stable for 8, 10, and 12 modes per chirality.

## Scope

A finite-dimensional matrix algebra cannot realize a nonzero central commutator as a global identity. The exact finite object is therefore the stable anomaly cocycle on the frozen sea-cyclic package. Promotion to the bosonic current algebra is the strict extension; it is not a claim that the lower finite matrix package already contains the full bosonic carrier.
