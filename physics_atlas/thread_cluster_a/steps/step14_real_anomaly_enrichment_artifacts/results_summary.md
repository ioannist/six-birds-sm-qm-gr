# Step 14 Results Summary: Real Anomaly Enrichment

## Verdict

`real_anomaly_enrichment_limit_recovery_constructed`.

This step replaces the prior toy anomaly score with exact rational anomaly coefficients on a finite curated candidate set of real chiral multiplets. It advances law-landing obligations by faithful enrichment, known-physics limit recovery, a closed-form anomaly-equation relation, and a scoped independently checkable consequence. It remains below law grade.

## SM Limit Recovery

The one-generation SM chiral content is verified anomaly-free:

```text
su3_cubic=0, su3_sq_u1=0, su2_sq_u1=0, u1_cubic=0, grav_u1=0, su5_cubic=0; su2_witten_even=True
```

This is known physics recovered as a calibration of the enriched carrier.

## Closed-Form Relations

For the fixed one-generation representations with variables `Y_Q, Y_u_c, Y_d_c, Y_L, Y_e_c`, the anomaly equations are:

- `2 Y_Q + Y_u_c + Y_d_c = 0`
- `3 Y_Q + Y_L = 0`
- `6 Y_Q + 3 Y_u_c + 3 Y_d_c + 2 Y_L + Y_e_c = 0`
- `6 Y_Q^3 + 3 Y_u_c^3 + 3 Y_d_c^3 + 2 Y_L^3 + Y_e_c^3 = 0`

Solving gives:

- `Y_L = -3 Y_Q`
- `Y_e_c = 6 Y_Q`
- `{Y_u_c, Y_d_c} = {-4 Y_Q, 2 Y_Q}`

Choosing the usual up/down labeling and normalization `Y_Q=1/6` gives the familiar pattern `Y_u_c=-2/3`, `Y_d_c=1/3`, `Y_L=-1/2`, `Y_e_c=1`. With `Q_em=T3+Y`, this recovers `Q_proton = - Q_electron`.

## Necessary Not Sufficient

Anomaly-free survivor count: `7`.

Unselected anomaly-free survivor count: `6`.

Survivors:

```text
SM_one_generation, SM_plus_vectorlike_lepton, SM_plus_vectorlike_down, SM_plus_sterile_neutrino, hypercharge_label_swapped, scaled_hypercharge_x2, SU5_10_plus_5bar_decomposition
```

Real anomaly-freedom prunes the finite candidate space but does not uniquely single out the reference content. Non-reference survivors include vector-like refinements, a sterile extension, a normalization-equivalent copy, a label-swapped anomaly solution, and a decomposed SU(5)-style candidate.

## Scoped New Consequence

Most promising next consequence: `minimal irreducible anomaly-cancellation support`.

How to check it: Enumerate chiral spectra over SU(3)xSU(2)xU(1) reps with bounded denominator hypercharges, compute the same anomalies, remove vector-like pairs, and check whether the reference one-generation support is minimal among non-equivalent anomaly-free chiral supports while vector-like exotics are non-minimal refinements.

This is scoped for Step 15. It is not forced in this step.

## Candidate-Law Obligation Status

- Faithful enrichment: advanced.
- Independently checkable consequence: scoped for Step 15.
- Closed-form relation: advanced.
- Limit recovery: advanced.
