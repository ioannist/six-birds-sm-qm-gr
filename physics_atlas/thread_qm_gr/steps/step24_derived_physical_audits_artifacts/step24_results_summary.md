# Step 24 Results Summary

## Orientation

Physical audit derivation from a shared toy field.  Step 24 computes both the QM-side Born audit and the GR-side stress-energy audit from the same finite complex field `ψ`, then measures whether their shared density/transport modes cohere.

## Active Residual

`R_child_E018_after_physical_audit_enrichment`: Step 23 used chosen quadratic forms with matching shared sub-blocks.  Step 24 derives the audits from a shared field so the overlap relation is discovered by computation.

## Carrier

Periodic one-dimensional lattice with `N=8` sites and `26` sampled complex fields.

Derived finite-difference structures:

- `grad ψ = (ψ[i+1] - ψ[i-1]) / 2`
- `shift ψ = ψ[i+1] - ψ[i]`
- fixed potential `V = 0.25 + 0.10 cos(2πx/N)`

## Derived Audits

QM/Born audit:

- `ρ = |ψ|²`
- `j = Im(conj(ψ) * grad ψ)`

GR/stress-energy audit:

- `T00 = |grad ψ|² + V |ψ|²`
- `T0i = Re(conj(grad ψ) * shift ψ)`

## Computed Coherence

The audits do not agree as one shared density/transport audit:

- density equal residual: `0.6944644768578695`
- density proportional residual: `0.5207123913178113`
- transport equal residual: `1.2894307568321801`
- transport proportional residual: `0.9994686548331937`

A linear prediction of stress-energy from the shared Born audit `(ρ,j)` still has positive held-out residuals:

- `T00` test residual: `0.401568901271731`
- `T0i` test residual: `0.5443048422989993`

## Sourcing Check

The GR audit is deterministic from the shared field `ψ`:

- direct sourcing residual: `0.0`

## Verdict

`derived_audit_verdict = derived_audits_differ_reconciliation_is_sourcing_T_of_psi`.

The physical reconciliation found by this toy is not a single shared overlap audit.  It is a sourcing relation: the GR-side stress-energy audit is a functional `T[ψ]` of the shared QM field.

## Grade

Finite-carrier diagnostic construction.  This is toy physics and does not claim full physical adequacy.
