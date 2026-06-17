# Step 4 Results Summary

## Orientation

Step 4 builds the E043 continuous scale-selection facet on a finite toy. The scale readout is `r = m_H2 / M_cutoff2`. The EW Sigma readout keeps broken-phase inputs and omits cutoff sensitivity.

## Scale Configurations

The toy contains `7` EW configurations. The realized configuration has `r_SM = 0.0001`. The repeated EW Sigma rows have the same broken-phase inputs but different cutoffs.

## Non-Descending Test

- Scale-ratio obstruction from EW Sigma: `3`, witness `scale_SM-scale_same_EW_midcut;scale_SM-scale_same_EW_lowcut;scale_same_EW_midcut-scale_same_EW_lowcut`.
- Derived EW observable obstruction: `0`, witness `none`.

The scale ratio needs cross-scale data not present in the EW Sigma readout, while the derived EW observable factors through that readout.

## Two Horns

- Derivation horn: attractor recurrence final `r = 0.0001`, residual `6.64073830647e-19`.
- Measure horn: unique peak at `r = 0.0001`.
- No-selection control: no-attractor final residual `0.0199` and flat measure has no unique selected point.

## Controls

- Non-descending scale ratio: `True`.
- Derived observable factors: `True`.
- Derivation horn reaches target: `True`.
- Measure horn peaks at target: `True`.
- No-selection control remains unfixed: `True`.
- Carrier guard: finite scale configs plus attractor-or-measure slot.

## Verdict

`e043_scale_selection_facet_constructed`.

The finite toy shows the scale-ratio as a non-descending selection coordinate. The slot can be filled by either an attractor-style derivation or a measure; without either, the ratio remains unfixed.
