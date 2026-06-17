# Step 26 Results Summary

## Orientation

Mode B physical-content continuation: add finite semiclassical dynamics to the Step 25 co-sourcing package. The layer content is still the shared toy field `psi`; the new question is whether `psi` can source a potential and then remain stationary in the potential it sources.

## Active Residual

`R_child_E018_after_sourcing_unification`: Step 25 supplied co-sourcing at the audit/readout level. Step 26 tests the dynamical back-reaction loop on the same finite field carrier.

## Carrier

- Periodic 1D lattice with `N=8` sites, loaded from Step 24 field samples.
- Field: complex vector `psi`.
- Background potential: Step 24 `potential`.
- Stress-energy density:
  `T00[psi] = |central_difference(psi)|^2 + background_potential * |psi|^2`.
- Sourced potential:
  `V[psi] = background_potential + kappa * T00[psi]`.
- Hamiltonian:
  `H[V] = 0.5 * periodic_laplacian + diag(V)`.

## Candidate Move

Iterate a Hartree-like self-consistency map:

1. source `V_k = background + kappa*T00[psi_k]`;
2. build Hermitian `H[V_k]`;
3. take the lowest stationary vector of `H[V_k]`;
4. damp toward it for the moderate coupling case;
5. re-source the potential and repeat.

The Schrödinger step `exp(-i H[V] dt) psi` is separately checked for norm preservation at every iteration.

## Verdict

Typed verdict: `self_consistent_dynamics_converges_on_toy`.

The moderate coupling case (`kappa=0.3`, `mix=0.5`) converges:

- final update residual: `8.165089184416358e-17`
- fixed-point residual: `3.4936318023019015e-16`
- final eigen residual: `6.377748916558787e-16`
- sourced-potential residual: `0.0`
- max unitary norm error: `1.4432899320127035e-15`

The over-strong control (`kappa=30.0`, `mix=1.0`) fails:

- final update residual: `1.398997140116586`
- fixed-point residual: `1.4285712942487314`
- final eigen residual: `0.6766429242147017`
- sourced-potential residual: `0.0`
- max unitary norm error: `1.2212453270876722e-15`

## Framework Outputs

| output | classification | grade | scope |
|---|---|---|---|
| coupled self-consistency map | predictive structural | finite-carrier diagnostic | Step 24/25 toy field carrier |
| convergence of moderate coupling | analytical structural | finite-carrier diagnostic | one finite lattice, one initial sample |
| over-strong control failure | analytical structural | finite-carrier diagnostic | can-fail control for same carrier |
| unitary norm check | organizational/audit | finite-carrier diagnostic | every iteration of both cases |
| external physical adequacy | remaining external content | external review | richer dynamics and physical frame transfer |

## Current Frontier

The toy co-sourcing package now has a self-consistent finite semiclassical dynamic for a moderate coupling and a failing over-strong control. This is a toy dynamical coherence result, not a broad physical adequacy result.

Next live option: external-review the dynamical toy for frame-transfer content, or enrich the carrier with multi-field / higher-dimensional / constraint-compatible dynamics before repeating the self-consistency test.
