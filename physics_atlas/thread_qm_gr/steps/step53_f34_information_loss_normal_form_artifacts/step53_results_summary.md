# Step 53 Results Summary

## Honest Grade First

This is a computed F34 normal-form classification on a finite static holographic toy. There is no evaporation dynamics, no Page curve, and no real black hole here. It does not resolve the physical information paradox and does not certify frame transfer. The recovered-known content is the holographic-unitarity narrative in F34 form: full boundary recovery loses only gauge redundancy, while a partial/thermal-style readout loses physical information.

## F34 Data

- `H0`: Step42 interior random tensor pairs `(left,right)` at `D=3`, seeds `[101, 202, 303]`.
- `tau`: contraction to the boundary state `left @ right.T`.
- `H1`: full boundary state matrices.
- `rho_full`: full normalized boundary state.
- `rho_partial`: left-boundary reduced density matrix.
- `sigma_raw`: raw interior tensors.
- `sigma_phys`: gauge-invariant physical interior class.

## Gauge and Rank Computation

The computed rank is `27` with internal dimension `27`. Rank equals the internal dimension: `True`.

Gauge invariance residual: `4.10994385471e-16`. Non-gauge perturbation changes the boundary state: `True`. Explicit SVD/GL reconstruction residual: `3.02052592925e-15`.

This supports the generic-stratum statement used here: full-boundary preimages are GL gauge orbits, not extra physical copies.

## Full-Boundary F34 Verdict

For `sigma_raw`, `O_rho` is nonempty: a gauge-transformed tensor pair has the same full boundary state and different raw tensors. For `sigma_phys`, the checked obstruction is empty on the generic full-rank stratum: the gauge-invariant functionals are constant on gauge orbits and recoverable from the full boundary singular data.

F34 full-boundary verdict: `legitimate_loss_gauge_only`.

## Partial-Readout F34 Verdict

The partial witness applies a right-complement unitary. The left reduced state residual is `5.33021563527e-16`, while the full state changes by `1.4167122627` and a gauge-invariant physical observable changes by `0.00973952587724`.

F34 partial-readout verdict: `illegitimate_loss`.

## Forbidden Rule

`holographic_carrier_forbids_physical_info_loss_at_full_boundary`: the holographic carrier forbids physical information loss at full-boundary recovery; information loss appears only after choosing a partial/coarse readout. In this toy, the paradox is a property of the readout, not of the carrier.
