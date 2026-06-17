# Step 6 Results Summary

## Orientation

Step 6 tests whether the Step 1 shared-frame non-descending readouts survive non-coordinate readouts, nonlinear readouts, and adversarial endpoint enrichment on the declared finite carrier.

Source carrier: `steps/step1_shared_substrate_frame_artifacts/extended_carrier_step1.csv`.

## Readout Battery

The battery applies `5` general-linear readouts and `3` nonlinear readouts to GR's smooth Sigma source `(d0,d2,d3)` and recomputes factorization for `d4_subplanck` and `d5_vacuum`.

Minimum obstruction counts across the readout battery:

- `d4_subplanck`: `3`.
- `d5_vacuum`: `1`.

Both stay positive. The branch-pair obstruction is preserved because states identical in the source remain identical under any readout of that source.

## Endpoint Enrichment

Genuine endpoint-internal enrichments use only `(d0,d1,d2,d3)` content and nonlinear functions of it. Minimum obstruction counts:

- `d4_subplanck`: `3`.
- `d5_vacuum`: `1`.

Both stay positive. Smuggling enrichments that add `d4` or `d5` as endpoint content make the corresponding readout definable with obstruction `0`, and those rows are flagged as using layer content.

## Controls

Positive detection passes:

- `d3_curvature` factors through GR Sigma with obstruction `0`.
- `d0*d2` factors through polynomial GR Sigma with obstruction `0`.

Smuggling detection passes:

- adding `d4` makes `d4_subplanck` definable with obstruction `0` and is flagged.
- adding `d5` makes `d5_vacuum` definable with obstruction `0` and is flagged.

## Verdict

`shared_frame_robustness_established`.

On this finite carrier, `d4_subplanck` and `d5_vacuum` remain non-descending under the declared general-linear and nonlinear readout battery and under genuine endpoint-internal enrichment. They become definable only when layer content is added to the endpoint, which the audit flags as smuggling. This is robustness on the declared finite carrier, not a continuous/gauge/diffeomorphism frame-transfer certificate.
