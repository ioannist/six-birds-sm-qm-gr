# Step 28 Results Summary

## Orientation

Mode B physical-content continuation: extend the Step 27 timeless construction from a stationary fixed point to a genuinely non-stationary relational history. The clock-field state is built from an evolving field sequence whose sourced potential changes along the internal clock.

## Active Residual

`R_child_E018_after_problem_of_time_constraint`: Step 27 represented the stationary Step 26 fixed point as a constrained clock-field state. Step 28 tests whether a non-eigenstate field with time-dependent self-sourced potentials can be encoded as a timeless relational history.

## Carrier

- Clock register: `M=16` clock values.
- Field register: Step 24 finite complex field, `N=8`.
- Initial state: Step 24 sample `2`, selected because it is not an eigenstate of its sourced Hamiltonian.
- Evolution:
  `psi_{t+1} = U_t psi_t`,
  `U_t = exp(-i H[V_t] dt)`,
  `V_t = background + kappa*T00[psi_t]`.
- Constraint map:
  rows encode `psi_{t+1} - U_t psi_t = 0` for `t=0..M-2`.

This is an open-chain discrete relational constraint map. The positive object for the physical-space test is the kernel of that map, equivalently the zero-space of `C^dagger C`.

## Candidate Move

Generate the non-stationary history by the self-sourced dynamics, then build the Page-Wootters-style history state

`Psi = (1/sqrt(M)) sum_t |t> tensor |psi_t>`.

The generated constraint `C_generated` is built from the same `U_t` sequence that is computed from the sourced potentials. A wrong-generator control replaces `U_t` by identity in the constraint rows while testing the same non-stationary history.

## Verdict

Typed verdict: `nonstationary_relational_history_constraint_consistent_on_toy`.

The history is genuinely non-stationary:

- minimum eigen residual across clock values: `0.35409006012453015`
- maximum phase-invariant state change: `0.18847313451682898`
- mean phase-invariant state change: `0.1884437583083705`
- maximum potential change: `0.001673580612625418`
- mean potential change: `0.0016580345734354176`

The generated relational constraint is consistent:

- generated constraint residual `||C Psi||`: `4.220196766037856e-16`
- generated null dimension at tolerance `1e-8`: `8`
- field readout residual: `2.2131155843786806e-16`
- relational potential residual: `9.205483015737869e-17`

The wrong-generator control fails:

- control residual: `0.0925307478333232`
- control passes: `False`

## Framework Outputs

| output | classification | grade | scope |
|---|---|---|---|
| non-stationary self-sourced field history | predictive structural | finite-carrier diagnostic | Step 24 field carrier |
| generated relational constraint map | analytical structural | finite-carrier diagnostic | open-chain clock-field history |
| wrong-generator control failure | analytical structural | finite-carrier diagnostic | identity-generator control |
| relational field and potential readouts | analytical structural | finite-carrier diagnostic | all 16 clock values |
| saved matrices and traces | organizational/audit | diagnostic-complete | NPZ/CSV/JSON artifacts |
| physical frame transfer | remaining external content | external review | beyond declared finite toy |

## Current Frontier

The toy package now has a genuinely non-stationary relational history whose internal clock readout recovers both the evolving field and the changing sourced potential. The next live option is external review of the history-adapted constraint, or construction of a less history-adapted nonlinear constraint that tests broader families of histories.
