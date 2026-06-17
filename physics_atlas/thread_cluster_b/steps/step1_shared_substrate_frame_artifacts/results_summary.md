# Step 1 Results Summary

## Orientation

Cluster B starts from the QM-GR co-sourcing package `L` and extends its carrier with two readouts:

- `d4_subplanck`: E042 trans-Planckian / resolved-curvature content.
- `d5_vacuum`: E021 selected vacuum-energy scale slot.

The extended carrier is `L_ext=(d0,d1,d2,d3,d4,d5)`, with `q_QM=(d0,d1,d2)` and GR's smooth access `Sigma_GR_smooth=(d0,d2,d3)`.

## Active Residual

`root_cluster_b_E021_E042`: ground E021 and E042 as regime restrictions of the shared parent package `L`, and compute that their typed non-descending objects are L-readouts not present in either endpoint access.

## Computed Frame

The carrier has `12` lifted states over the prior 8-state toy:

- `6` smooth or vacuum-smooth states.
- `6` high-curvature lifted states.
- high-curvature rows are duplicated above the same smooth GR readout but carry different finite `d4_subplanck`.
- one vacuum-smooth row is duplicated above the same smooth GR readout but carries different finite `d5_vacuum`.

The non-descending `d4_subplanck` / `d5_vacuum` readouts are deliberately INSTANTIATED by branch splits in the toy carrier (high-curvature bases split in `d4`; one vacuum base splits in `d5`); the controls (`d3` factors; `d4` factors through `d3` in the smooth regime) show the finite test DISCRIMINATES, but do NOT certify physical frame transfer.

## Non-Factorization Signatures

| Object | GR obstruction | QM obstruction | Witness | Verdict |
|---|---:|---:|---|---|
| E042 `d4_subplanck` | `3` | `11` | `1-2;5-6;10-11` | non-descending L-readout |
| E021 `d5_vacuum` | `1` | `3` | `3-4` | non-descending L-readout |

The GR obstruction means there are pairs of L-states identical in `Sigma_GR_smooth=(d0,d2,d3)` but different in the target readout.  The QM obstruction is the analogous check against `q_QM`.

## Smooth Descent And Boundary

The smooth-regime GR readout descends from `L_ext` by projection with residual `0.0`.

The required anti-rigging control also passes:

- `d3` factors through GR's smooth access: obstruction `0`.
- `d4_subplanck` factors through `d3` in the smooth regime: obstruction `0`, residual `5.0148676901037195e-17`.
- `d4_subplanck` becomes non-factorizing only at the high-curvature boundary: obstruction `3`.

The singularity locus in this toy is the high-curvature subset `{1,2,5,6,10,11}`, where the smooth GR shadow no longer determines the finite `d4` readout.

## Verdict

`shared_substrate_frame_established`.

E021 and E042 are grounded as computed non-descending readouts of `L_ext`: E021 is the finite vacuum-scale slot `d5_vacuum`, and E042 is the finite sub-Planckian curvature slot `d4_subplanck`.  The smooth GR shadow holds where it should, and the descending-readout controls show the non-factorization test is discriminating.

## Next Live Options

The natural next steps are:

- Step 2: build the E042 high-curvature/singularity regime more fully.
- Step 3: build the E021 vacuum-energy budget/selection regime more fully.
