# Step 36 Results Summary

## Orientation

Step 36 strengthens Step 33 type-uniqueness by adversarial construction.  Instead of excluding non-`BridgeMediatedRole` F24 families by absent fields in `L`, it builds genuine competitors carrying their defining structures and computes why each fails as a full exact QM-GR reconciliation type in `G*`.

## Carrier

The computation reuses the Step 33/34 carrier and maps:

- 8 states in `R^4`;
- `q_QM=(d0_density,d1_phase,d2_transport)`;
- `q_GR=(d0_density,d2_transport,d3_curvature)`;
- `L=eye(4)`.

## Adversarial Competitors

Five competitors were constructed and defeated:

- `HiddenUpstreamRole`: `H_latent_lambda_d3` carries a real latent `lambda=d3`.  Hidden horn fails `G_vis` and `G_audit` among other gates; exposed horn passes only by becoming isomorphic to `L`.
- `CoarsenedRole`: `C_best_linear_and_polynomial_d3_from_qQM` fits `d3` from `q_QM` with linear and polynomial degrees 1-4.  The minimum held-out residual remains `1.1220677985658054`; `O_s` has count `3`.
- `BudgetedRole`: `B_rank_reduced_cutoff_d3_hat` carries a priced cutoff residual.  The GR descent residual is `0.5773502691896258`, while `L` has residual `0.0`.
- `ScopedRole`: `S_proper_scope_no_duplicate_fibers` resolves the split on a proper subcarrier with `scope_O_s=0`, but the full carrier still has `full_O_s=3`.
- `MemoryLayer`: `Mem_history_record_d3` carries a real history/record coordinate.  Hidden history fails visibility/audit gates; exposed history collapses to `L`.

## Controls

All controls passed:

- `L_positive_anchor`: `L` passes the gate proxy and has `O_s_under_L=0`.
- `genuine_coarsening_d2_from_qQM`: reconstructing `d2` from `q_QM` passes with maximum held-out residual `6.304854800243424e-16`.
- `coarsening_d3_fails_even_nonlinear`: polynomial degrees 1-4 all leave positive held-out residual.
- `equivalent_L_prime_not_rejected`: relabeled `L` has isomorphism residual `0`.
- `no_adversarial_competitor_passes_full_reconciliation`: passing competitor count is `0`.

## Verdict

Typed verdict: `type_uniqueness_by_adversarial_defeat`.

The reviewer objection is answered inside the bounded grammar: the physically interesting competitor families are not merely absent from `L`; they are constructed with their strongest finite defining structures and computationally defeated as full exact reconciliation types.

## Nonclaim

The defeat is bounded.  Hidden-variable, decoherence/coarsening, EFT/cutoff, scoped, and memory/history methods may remain useful as approximations, local descriptions, or separate programs.  Step 36 says only that the constructed competitors do not supply the full exact lawful reconciliation type in `G*` on this finite carrier.
