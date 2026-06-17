# Step 2 Results Summary

## Orientation

Step 2 builds the E042 high-curvature layer on the Step 1 carrier `L_ext`.  The construction treats the singularity as the boundary where GR's smooth geometry readout stops determining the finite `d4_subplanck` content carried by `L_ext`.

## Active Residual

`R_cluster_b_after_step1_shared_substrate_frame -> E042_high_curvature_boundary`: build the four E042 predicates on `L_ext`:

- P6 defect-stabilization.
- P4 Planck-scale staging.
- P2 geodesic/causal continuation.
- boundary non-factorization.

## P6 Defect-Stabilization

The refinement sequence uses `epsilon_n = 2^-(n-1)` for `n=1..8`.

| Sequence | Start | End | Last Increment | Verdict |
|---|---:|---:|---:|---|
| GR `K_GR` | `0.81` | `13271.04` | `9953.28` | non-stabilizing divergence |
| L `R_L` | `0.05833333333333335` | `0.749957784016927` | `0.0001266479492186834` | finite stabilizing readout |
| bad control `R_bad` | `0.9` | `115.2` | `57.6` | fails stabilization |

This is the typed P6 move: the GR-side curvature defect is non-stabilizing, while the L-side `d4`-based readout approaches the finite toy value `R*=0.75`.

## P4 Planck Staging

The toy Planck threshold is `K_P=16.0`.

The computed crossover is:

- `n*=4`
- `epsilon*=0.125`
- `K(epsilon*)=51.84`
- `K/K_P=3.24`

The staging record uses `hbar` only as the marker of the new L-stage distinction; it is not in GR's smooth access.

## P2 Continuation

The GR side terminates at `epsilon=0` in the toy continuation table.  The L side remains finite at the locus and has finite post-locus rows at negative signed epsilon values.

The post-locus continuation rows have finite `L_R_continuation` values `0.7475`, `0.745`, and `0.74`.

## Non-Factorization

The E042 boundary signature is recomputed:

- source: `GR_smooth_Sigma_f=(d0,d2,d3)`
- target: `d4_subplanck`
- high-curvature obstruction count: `3`
- witnesses: `1-2;5-6;10-11`

The smooth-regime control remains clean: `d4` through `d3` has obstruction count `0`.

## Controls

All required controls pass:

- GR `K` genuinely diverges.
- no-resolution control `R_bad` does not stabilize.
- L readout `R_L` stabilizes with shrinking increments.
- smooth-regime control has no spurious boundary activation.

## Verdict

`E042_boundary_layer_constructed_finite_toy`.

On this finite carrier, E042's typed shape is constructed: GR's non-stabilizing curvature divergence is replaced by a finite stabilizing L-readout, with a computed staging crossover, finite continuation through the boundary, and the Step 1 non-factorization signature preserved.

## Current Frontier

The result is structural and finite-carrier.  It does not identify the physical substrate behind `d4_subplanck`.  The natural next Cluster B move is Step 3: build the E021 vacuum-energy budget / selection regime on `d5_vacuum`.
