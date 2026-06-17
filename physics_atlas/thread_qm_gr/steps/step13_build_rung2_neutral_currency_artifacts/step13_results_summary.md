# Step 13 Results Summary

## Orientation

Step 13 re-orders the framework cascade after the Step-12 rejection. The active residual is the Step-10 currency mismatch: the QM-side amplitude currency and GR-side metric currency do not factor through one another, and a refinement rung is not meaningful until a shared currency exists.

This step builds `RUNG_2_NEUTRAL_CURRENCY` as a compressed single source currency `u`, not as a direct sum of endpoint currencies.

## Carrier And Candidate Move

The enriched endpoint currencies are real finite matrices at two refinement levels:

- QM-side currency: `q_amplitude_density`, `q_phase_order`, `q_coherence_transport`.
- GR-side currency: `g_metric_density`, `g_transport_flux`, `g_curvature_scale`.
- Neutral source currency `u`: `u_neutral_density`, `u_phase_order`, `u_transport_flux`, `u_curvature_scale`.

The two shadows are distinct:

- `S_QM : u -> (neutral_density, phase_order, transport_flux)`.
- `S_GR : u -> (neutral_density, transport_flux, curvature_scale)`.

The source dimension is compressed below the direct-sum control:

`d_QM = 3`, `d_GR = 3`, `d_u = 4`, `d_union = 6`.

## Four-Way Audit

| case | recovery | compression | distinct shadows | verdict |
|---|---:|---:|---:|---|
| `neutral_u` | max `9.916641414829509e-17` | pass, `4 < 6` | pass | candidate passes |
| `placeholder` | min `1.4142135623730951` | fail | fail | rejected control |
| `union_direct_sum` | max `9.916641414829509e-17` | fail, `6 = 6` | pass | rejected by compression |
| `collapse_typed_seed` | min `1.8808144464156678` | fail | fail | rejected control |

The direct-sum control is intentionally allowed to recover both endpoint evolutions; it is rejected because it does not compress. That is the anti-union guard.

## Non-Factorization

The neutral source is not recoverable from either endpoint currency alone:

- min QM-only-to-`u` residual: `0.37808491927495375`.
- min GR-only-to-`u` residual: `0.39075176108115167`.
- shared compression fraction: `0.3333333333333333`.

This is a strict extension on the finite carrier: each endpoint shadow omits one source mode needed by the other endpoint.

## Verdict

`NEUTRAL CURRENCY BUILT` as a finite-carrier candidate requiring external review. The build passes recovery, compression, distinctness, control rejection, and non-factorization audits at both refinement levels.

This does not close the root target. It builds one framework rung under the declared finite carrier and leaves the next move:

`RETEST_RUNG_1_REFINE_FIXEDPOINT_ON_NEUTRAL_CURRENCY`.

