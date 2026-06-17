# Step 52 Results Summary

## Honest Grade First

Bell nonlocality is recovered-known physics. This step recovers it as the F49 common-source / nonlocal-correlation normal form on the QM-GR co-sourcing carrier and adds the SBT-native reconciliation: the common carrier is not a local hidden variable. F49 local explainability requires an accessible source or interface quotient through which readouts factor; F37 complementary non-joint-access forecloses that move for the Bell settings. This is a yes/no structural discriminator and falsification route, not a new measured number, not frame transfer, and not a closure of E018.

## Bell Correlations

The QM arm uses the Bell state `(|00>+|11>)/sqrt(2)` with settings `a0=Z`, `a1=X`, `b0=(Z+X)/sqrt(2)`, `b1=(Z-X)/sqrt(2)`. The correlations are computed from `Tr(rho A_i tensor B_j)`.

Computed quantum CHSH: `2.82842712475`.

## Local Bound by Enumeration

All 16 deterministic local strategies were enumerated. The computed maximum absolute CHSH value is `2`. The Bell violation gap is `0.828427124746`.

## F49 Verdict

Since the quantum CHSH value exceeds the enumerated local bound, no probability mixture of the deterministic common-source strategies reproduces the Bell table. The F49 verdict is `statused_nonlocal_residual`: CommonSource fails, InterfaceFactorization fails, and the correlation is a statused nonlocal residual.

## FIII Delta-Fact Witness

`delta_fact_witness_pair_step52.csv` records a source-only witness pair: the same Bell source under contexts `a0,b0` and `a1,b1` has different correlation readouts. The Bell-polytope row records the stronger finite facet separation: every local-source mixture has `abs(CHSH)<=2`, while the Bell table exceeds it.

## F37 Carrier-Not-Hidden-Variable Tie

The setting commutators are nonzero. Normalized commutator residuals are `A=0.707106781187;B=0.707106781187`. Step 47's frozen complementary-pair control gives residual `0.707106781187` with no admissible joint quotient. Therefore the common carrier cannot be used as an admissible local hidden-variable source for complementary co-readouts.

## Classical Control

The separable mixture `0.5|00><00|+0.5|11><11|` has CHSH `1.41421356237` and is locally explainable. The explicit 16-row LHV table in `classical_control_lhv_table_step52.csv` reproduces all four control correlations exactly within tolerance.

## Forbidden Rule

The forbidden rule is `common_carrier_cannot_be_local_hidden_variable`: SBT forbids reading the common carrier as a local hidden variable. A common carrier above the access structure is consistent with Bell experiments; an admissible local common source below complementary accesses is not.
