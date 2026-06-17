# Step 25 Results Summary

## Orientation

Mode B physical-content construction.  Step 25 builds the sourcing form of `L`: a parent package carrying a finite complex field `ψ` from which both child descents are read.

## Active Residual

`R_child_E018_after_derived_physical_audit_sourcing`: Step 24 discovered that Born and stress-energy audits do not form one shared audit.  The positive reconciliation is sourcing `T[ψ]`.  Step 25 builds that sourcing-unification package and tests it against a non-co-sourced control.

## Carrier

`L` carries the same periodic finite toy field samples from Step 24:

- `N=8` sites.
- `26` sampled fields.
- fixed potential inherited from Step 24.

## Descents

QM descent:

- `ρ = |ψ|²`
- `j = Im(conj(ψ) * grad ψ)`

GR descent:

- `T00 = |grad ψ|² + V |ψ|²`
- `T0i = Re(conj(grad ψ) * shift ψ)`

## Co-Sourcing Criterion

`L` passes iff the same field `ψ` sources both child descents:

- `Born[L.ψ] = QM descent`
- `T[L.ψ] = GR descent`

## Computation

`L_co_sourced`:

- max Born descent residual: `0.0`
- max stress-energy descent residual: `0.0`
- all samples single-field sourced: `true`

`non_co_sourced_control`:

- QM descent still reads `Born[ψ]`
- GR descent reads `T[ψ']` from an independent shifted sample
- max stress-energy residual: `0.3806026603775931`
- all samples single-field sourced: `false`

## Verdict

`co_sourcing_verdict = L_is_co_sourcing_unification`.

On this toy, `L` is the co-sourcing unification: one field `ψ` on `L` sources both the QM Born descent and the GR stress-energy descent.  The non-co-sourced control fails.

## Grade

Finite-carrier diagnostic construction.  This is toy semiclassical sourcing content, not a full physical model.
