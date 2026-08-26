# S6 dimension-generic record-grammar ablation

## Reference-threshold generic grammar

| dimensions | branch scope | clean classification | evaluation count | stable substrate count | capacity pass count | distinguishability pass count | record stability count | counterexample count | mesonic token count set | baryonic token count set | mixed token count set | total token count set |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2|3 | no_singleton_branch | undefined_no_singleton_branch | 2 | 0 | 2 | 2 | 0 | 0 | 2 | 0 | 0 | 2 |
| 2|3 | singleton_active_SU(2) | clean_evaluated | 4 | 4 | 4 | 4 | 4 | 0 | 0 | 2 | 0 | 2 |
| 2|3 | singleton_active_SU(3) | breaking_evaluated | 4 | 4 | 4 | 4 | 4 | 4 | 0 | 2 | 0 | 2 |
| 3 | no_singleton_branch | undefined_no_singleton_branch | 28 | 0 | 2 | 28 | 0 | 0 | 0 | 0|4 | 0 | 0|4 |
| 4 | no_singleton_branch | undefined_no_singleton_branch | 14 | 0 | 14 | 14 | 0 | 0 | 0 | 2|6 | 0 | 2|6 |
| 4 | singleton_active_SU(4) | breaking_evaluated | 4 | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 1 | 1 |

At the published capacity threshold `MIN_RECORD_TOKENS=2`, eight of the 12 evaluated singleton branches are record-stable. The four `2|3`, SU(2)-active clean branches remain RS, but the four `2|3`, SU(3)-active **breaking** branches also pass all three record conjuncts. These are direct counterexamples to the pointwise generic implication:

| evaluation | family | branch | tokens | classification |
|---|---|---|---|---|
| eval_049 | 2|3 | singleton_active_SU(3) | 2 | breaking_evaluated |
| eval_051 | 2|3 | singleton_active_SU(3) | 2 | breaking_evaluated |
| eval_053 | 2|3 | singleton_active_SU(3) | 2 | breaking_evaluated |
| eval_055 | 2|3 | singleton_active_SU(3) | 2 | breaking_evaluated |

The four SU(4)-active branches each construct one neutral mixed-epsilon token, not two, so none is RS at the reference threshold. Separately, all 14 SU(4) no-singleton structures have two or more four-fold baryonic tokens but remain substrate-fail and clean-undefined; capacity alone does not make them RS.

## Three quantifier readings at threshold two

| threshold | quantifier reading | domain count | antecedent count | counterexample count | implication passes | vacuous |
|---|---|---|---|---|---|---|
| 2 | branch_pointwise | 12 | 8 | 4 | False | False |
| 2 | structure_universal | 8 | 4 | 4 | False | False |
| 2 | structure_existential | 8 | 4 | 0 | True | False |

- **Branch pointwise fails:** 4 counterexamples among 8 RS branches.
- **Structure universal fails:** all branches are RS in four `2|3` structures, but not all branches are clean.
- **Structure existential passes non-vacuously:** the same four structures have at least one RS branch and at least one clean branch. This weaker reading does not repair the pointwise counterexamples.

The 44 structures with no singleton branch are explicitly `undefined_no_singleton_branch` and are excluded from the structure quantifier domains.

## Capacity-threshold sensitivity

| threshold | branch domain count | rs branch count | rs clean count | rs breaking count | counterexample count | rs family membership | rs branch scope membership | two by three su2 active rs | su4 rs | implication passes | vacuous |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 12 | 12 | 4 | 8 | 8 | 2|3:8;4:4 | singleton_active_SU(2):4;singleton_active_SU(3):4;singleton_active_SU(4):4 | 4 | 4 | False | False |
| 2 | 12 | 8 | 4 | 4 | 4 | 2|3:8 | singleton_active_SU(2):4;singleton_active_SU(3):4 | 4 | 0 | False | False |
| 3 | 12 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | True | True |
| 4 | 12 | 0 | 0 | 0 | 0 |  |  | 0 | 0 | True | True |

At threshold one, all 12 singleton branches become RS: the four SU(4)-active breaking branches join the four SU(3)-active breaking branches, producing eight counterexamples. At thresholds three and four no branch is RS, so every implication passes only vacuously.

## Honest conclusion

The correlation is **a grammar artifact on this branch-complete finite carrier, not grammar-robust**. Replacing the SU(3)-shaped charge split and alias rules with actual weights and actual conjugacy leaves the desired `2|3`/SU(2)-active branches record-stable, but it also admits their breaking SU(3)-active sibling branches at the published threshold. SU(4) is not a threshold-two counterexample because its constructed mixed basis has capacity one; it becomes an explicit breaking RS counterexample at threshold one. Raising the threshold merely makes the result vacuous. Thus no dimension-generic implication `RS(C,phi) => Clean(C,phi)` lands from this grammar.
