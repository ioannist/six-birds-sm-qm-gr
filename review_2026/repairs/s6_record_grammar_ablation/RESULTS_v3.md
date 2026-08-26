# S6-ABLATION-3: token-completeness probe

## Bounded census

| evaluation_id | dimensions | branch_scope | clean_classification | undressed_operator_count | operators_with_dressed_lift_count | dressed_new_operator_count | inclusive_quotient_operator_count | clean_branch_gains_dressed_tokens |
|---|---|---|---|---|---|---|---|---|
| eval_034 | 4 | singleton_active_SU(4) | breaking_evaluated | 11 | 29 | 18 | 29 | False |
| eval_042 | 4 | singleton_active_SU(4) | breaking_evaluated | 11 | 29 | 18 | 29 | False |
| eval_044 | 4 | singleton_active_SU(4) | breaking_evaluated | 11 | 29 | 18 | 29 | False |
| eval_045 | 4 | singleton_active_SU(4) | breaking_evaluated | 11 | 29 | 18 | 29 | False |
| eval_048 | 2|3 | singleton_active_SU(2) | clean_evaluated | 11 | 29 | 18 | 29 | True |
| eval_049 | 2|3 | singleton_active_SU(3) | breaking_evaluated | 16 | 43 | 27 | 43 | False |
| eval_050 | 2|3 | singleton_active_SU(2) | clean_evaluated | 11 | 29 | 18 | 29 | True |
| eval_051 | 2|3 | singleton_active_SU(3) | breaking_evaluated | 16 | 43 | 27 | 43 | False |
| eval_052 | 2|3 | singleton_active_SU(2) | clean_evaluated | 11 | 29 | 18 | 29 | True |
| eval_053 | 2|3 | singleton_active_SU(3) | breaking_evaluated | 16 | 43 | 27 | 43 | False |
| eval_054 | 2|3 | singleton_active_SU(2) | clean_evaluated | 11 | 29 | 18 | 29 | True |
| eval_055 | 2|3 | singleton_active_SU(3) | breaking_evaluated | 16 | 43 | 27 | 43 | False |

The declared search has fermion arity `2..4`, at most `2` total `phi`/`phi-dagger` insertions, and total constituent count at most `6`. Four covers the largest residual epsilon arity (SU(3)) plus one. Every row is an exact LR singlet under every residual factor, has zero computed residual U(1) charge, and possesses an exact UV-gauge-invariant lift. Lifts with identical residual component content and invariant channel that differ only by insertions of the same branch VEV are one quotient operator.

`operators_with_dressed_lift_count` includes quotient classes also possessing an undressed lift; `dressed_new_operator_count` is the disjoint increment, and `inclusive_quotient_operator_count` is the union. All four clean branches gain 18 dressed-new operators, so dressing is applied symmetrically rather than only to breaking branches.

## Mandatory eval_049 regression

The operator `epsilon(o2c0,o3c0)` is present with UV lift `epsilon(o2c0,o3c0,phi-dagger)` (enumerated constituent lift `o2c0*o3c0*phi-dagger`). Its original-charge equation is `(-2)+(4)+(-2)=0` and its residual-charge equation is `(-3)+(3)=0`. The UV and residual exact singlet multiplicities are `1` and `1`. The v1 spectator-Cartan token survives: `False`; the residual-U(1) spectator coefficient remains `0`. Regression passes: `True`.

## Threshold-two results

| counting_convention | branch_domain_count | rs_branch_count | rs_clean_count | rs_breaking_count | counterexample_count | counterexample_ids | implication_passes | vacuous |
|---|---|---|---|---|---|---|---|---|
| undressed_only | 12 | 12 | 4 | 8 | 8 | eval_034|eval_042|eval_044|eval_045|eval_049|eval_051|eval_053|eval_055 | False | False |
| dressed_inclusive | 12 | 12 | 4 | 8 | 8 | eval_034|eval_042|eval_044|eval_045|eval_049|eval_051|eval_053|eval_055 | False | False |

The complete bounded undressed census already selects every branch because higher-arity UV-invariant operator monomials add capacity beyond v2's chosen meson/epsilon token generators. Scalar dressing then adds further operators but does not change the threshold-2 binary. For comparison, frozen v2's restricted undressed generator basis selected 4 clean branches and no breaking branch. Consequently the data do **not** support the narrower phrase “holds iff scalar-dressed composites are excluded”: completeness of the undressed operator definition also matters.

## Quantifier readings at threshold two

| counting_convention | quantifier_reading | domain_count | antecedent_count | counterexample_count | implication_passes | vacuous |
|---|---|---|---|---|---|---|
| undressed_only | branch_pointwise | 12 | 12 | 8 | False | False |
| undressed_only | structure_universal | 8 | 8 | 8 | False | False |
| undressed_only | structure_existential | 8 | 8 | 4 | False | False |
| dressed_inclusive | branch_pointwise | 12 | 12 | 8 | False | False |
| dressed_inclusive | structure_universal | 8 | 8 | 8 | False | False |
| dressed_inclusive | structure_existential | 8 | 8 | 4 | False | False |

## Outcome ruling input

| token_definition | scalar_dressed_records_included | rs_branch_count | rs_clean_count | rs_breaking_count | counterexample_count | pointwise_implication_passes | ruling |
|---|---|---|---|---|---|---|---|
| v2_restricted_UV_meson_epsilon_generators | False | 4 | 4 | 0 | 0 | True | HOLDS_NONVACUOUSLY_FOR_RESTRICTED_GENERATOR_GRAMMAR |
| v3_complete_bounded_undressed_only | False | 12 | 4 | 8 | 8 | False | COUNTEREXAMPLES_PERSIST |
| v3_complete_bounded_dressed_inclusive | True | 12 | 4 | 8 | 8 | False | COUNTEREXAMPLES_PERSIST |

**COUNTEREXAMPLES_PERSIST_SCALAR_DRESSED_COMPLETE_BOUNDED_CENSUS**. Under both complete bounded conventions, all three readings fail. The existential failures are the four SU(4)-alone structures, which have selected breaking branches and no clean branch; the four selected `2|3` structures do retain a clean sibling. The certified conclusion is therefore stronger than scalar-dressing sensitivity alone: `RS => clean` is token-definition-sensitive, and on this bounded complete operator census it is false both without and with scalar dressings. The restricted v2 generator grammar is the convention under which it held. Deciding which algebraic operators persist as actual records requires dynamical record stability under the branch dynamics, beyond token counting.
