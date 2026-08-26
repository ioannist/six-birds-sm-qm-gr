# S6-ABLATION-2: full-residual-neutral record grammar

## Computed branch result

| dimensions | branch_scope | clean_classification | branch_count | mesonic_count_set | baryonic_count_set | mixed_count_set | total_count_set | rs_at_threshold_2 | counterexamples_at_threshold_2 |
|---|---|---|---|---|---|---|---|---|---|
| 2|3 | singleton_active_SU(2) | clean_evaluated | 4 | 2 | 2 | 0 | 4 | 4 | 0 |
| 2|3 | singleton_active_SU(3) | breaking_evaluated | 4 | 0 | 1 | 0 | 1 | 0 | 0 |
| 4 | singleton_active_SU(4) | breaking_evaluated | 4 | 0 | 0 | 1 | 1 | 0 | 0 |

Every token is first constructed in the UV mesonic/epsilon basis, then restricted to states that are exact singlets under every branch-specific residual nonabelian factor and neutral under the computed residual U(1). The U(1) coefficients are primitive integer solutions of `a q_phi + b h_phi = 0`; spectator Cartans never enter.

At the published threshold 2, `4` branches are RS, all `4` are clean, and there are `0` counterexamples. The pointwise implication therefore lands non-vacuously for this declared grammar. The ablation-1 result remains an explicit sensitivity result: adding a unit-normalized spectator Cartan manufactured four breaking RS branches.

## Quantifier readings at threshold 2

| quantifier_reading | domain_count | antecedent_count | counterexample_count | implication_passes | vacuous |
|---|---|---|---|---|---|
| branch_pointwise | 12 | 4 | 0 | True | False |
| structure_universal | 8 | 0 | 0 | True | True |
| structure_existential | 8 | 4 | 0 | True | False |

Pointwise passes non-vacuously. Structure-universal passes only vacuously because no two-branch structure has every branch RS. Structure-existential passes non-vacuously for the four `2|3` structures possessing an RS clean branch.

## eval_049 end-to-end trace

The v1 rule produced `2` tokens by adding the unbroken spectator SU(2) Cartan weight to the original U(1). The stabilizer computation instead gives `SU(2)[spectator_f0] x SU(2)[reduced_f1] x U(1)_res` and `(1)*(2) + (-1)*(2) = 0`, with zero spectator-Cartan coefficients. The spectator-doublet baryon disappears: `True`. One genuine full-residual-neutral baryonic record remains, so the token count is `1` and threshold-2 RS is `False`.

## Outcome ruling input

**IMPLICATION_RESTORED_POINTWISE_FULL_RESIDUAL_NEUTRAL_GRAMMAR**. Hence `RS(C,phi) => Clean(C,phi)` is restored pointwise at conditional finite-toy diagnostic strength only when the grammar is explicitly declared to require full residual-gauge neutrality. Threshold 1 still admits all eight breaking branches; thresholds 2--4 retain only the four clean branches on this finite carrier.
