# Step 3 Results Summary

## Orientation

Step 3 builds the E021 vacuum-energy side of Cluster B on the Step 1 carrier `L_ext`.  The firm claim is structural and narrow: `Lambda` is represented by a finite selected/run readout `d5_vacuum`, with non-factorization obstruction `4` and a descending-control contrast with obstruction `0`.  The UV-to-IR ledger is MODELED/illustrative P6 bookkeeping: the monotone `[12.0, 8.0, 4.0, 0.0]` is hand-specified, not a firm audit computed from a coarse map, RG flow, or package dynamics.  The distinct-audit-currency interpretation is recorded as contested and casting-dependent.

## Active Residual

`R_cluster_b_after_step2_E042_boundary_constructed -> E021_vacuum_budget`: construct the E021 predicates on `L_ext`:

- P5 vacuum-energy currency.
- P6 UV-to-IR audit ledger.
- P2 vacuum selection.
- non-factorization against clean UV descent.

## P5 Vacuum Currency

The selected toy IR readout is the Step 1 `d5_vacuum` value:

- selected state: `3`
- `rho_IR = 0.0010400000000000001`
- `psi_stress_proxy = 0.25`
- `budget_weight = 0.0041600000000000005`

The alternate branch at the same GR smooth readout has:

- alternate state: `4`
- `rho = 0.00604`

Both are tracked L-readouts; GR's role is recorded as receiving an input parameter rather than generating the value.

## P6 UV-to-IR Ledger

The UV/IR mismatch is deliberately modeled as a toy ratio:

- `rho_UV = 1040000000.0000001`
- `rho_IR = 0.0010400000000000001`
- modeled ratio = `1000000000000.0`
- `log10(ratio) = 12.0`

This is not the physical 120-order number.

The unaudited cancellation row has:

- `counterterm = 1039999999.9989601`
- `tracked = False`
- `unaudited_cancellation = True`

The booked ledger tracks the mismatch by a monotone finite audit sequence:

`12.0 -> 8.0 -> 4.0 -> 0.0`

This booked sequence is a MODELED/illustrative P6 bookkeeping shape.  It is hand-specified and is not a firm audit computed from a coarse map, RG flow, or package dynamics.

## P2 Selection

The toy vacuum ensemble has `5` candidates.  The selected candidate is `vac_A_selected`, chosen by the explicit predicate `minimum_selection_score`.

The selection is not a clean function of UV Sigma alone: the ensemble contains configurations with identical UV readout and different vacuum scales.

## Non-Factorization And Controls

Computed signatures:

- `UV_Sigma -> rho_Lambda_candidate`: obstruction count `4`, witnesses `0-1;0-2;1-2;3-4`.
- Step 1 `GR_smooth_Sigma_f -> d5_vacuum`: obstruction count `1`, witness `3-4`.
- descending control `UV_Sigma -> uv_determined_coupling`: obstruction count `0`.

Controls:

- clean UV-to-Lambda derivation control fails as required.
- UV-determined descending control factors.
- booked ledger is non-vacuous and monotone.
- mismatch ratio is marked as a toy model.

## Dissolution

Within this finite grammar, the clean-descent demand hides the mismatch in an untracked counterterm.  The lawful construction keeps the mismatch visible in the P6 ledger and treats the IR vacuum scale as a selected/run L-readout.

This is a structural dissolution of the clean-descent framing on the toy, not a physical value calculation.

## Verdict

`E021_audited_vacuum_readout_constructed_finite_toy`.

Firm part: selected/run readout on the toy: non-factorization obstruction `4` with the descending-control contrast (obstruction `0`).  
Modeled part: the booked UV-to-IR ledger is illustrative P6 bookkeeping, not a firm audit computed from a coarse map, RG flow, or package dynamics.  
Contested part: interpreting the bookkeeping as a distinct audited vacuum currency beyond the conservative classical-GR casting.

## Current Frontier

The next natural step is to consolidate Cluster B: E042 supplies the high-curvature boundary construction, E021 supplies the vacuum-budget construction, and both sit as regime restrictions of `L_ext`.
