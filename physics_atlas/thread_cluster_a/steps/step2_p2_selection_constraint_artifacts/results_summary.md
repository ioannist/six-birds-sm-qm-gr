# Step 2 Results Summary

## Orientation

Step 2 builds the P2 selection mechanics on the finite Cluster A candidate space. The carrier is an extended candidate space, a toy anomaly constraint, and a post-constraint selector.

## Extended Candidate Space

The Step-1 space is extended from 9 to `13` candidates by adding `4` anomalous `(G,R)` tokens.

## Toy Anomaly Functional

The finite stand-in `A_GR = gauge_charge(G) + rep_charge(R)` is computed for every candidate. `A_GR = 0` survives the anomaly constraint; `A_GR != 0` is pruned. This is a toy diagnostic, not real anomaly theory.

## Constraint Pruning

- Pruned candidates: `w_anom_u1;w_anom_rep;w_anom_mixed;w_anom_joint`.
- Survivor count before selection: `9`.
- Survivor set: `w_SM;w_alt_gauge;w_alt_rep;w_two_gen;w_four_gen;w_high_ew;w_alt_uv;w_alt_vacuum;w_joint_alt`.

The anomaly constraint discriminates: anomalous candidates are removed and anomaly-free candidates survive.

## Selection Collapse

The post-constraint selector picks `w_SM` from `9` survivors. Non-selected anomaly-free survivors remain: `w_alt_gauge;w_alt_rep;w_two_gen;w_four_gen;w_high_ew;w_alt_uv;w_alt_vacuum;w_joint_alt`.

This shows anomaly-freedom is necessary but not sufficient on the toy: it prunes to a set, and the selection rule collapses that set to a point.

## Joint Co-Determination

Among survivors, gauge codes `G_PS_TOY;G_SM;G_TOY_E6` and generation counts `2;3;4` have `5` observed joint pairs out of `9` possible pairs. Missing pairs `G_PS_TOY|2;G_PS_TOY|4;G_TOY_E6|2;G_TOY_E6|3` and mutual information `0.330856` bits witness non-independent support. The selected joint pair is `G_SM|3`.

## Controls

- Prune-discriminates anomalous removed: `True`.
- Prune-discriminates anomaly-free survives: `True`.
- Selection collapses: `True`.
- Further step beyond anomaly-freedom: `True`.
- Carrier guard: candidate-space plus constraint plus selector.

## Verdict

`p2_selection_constraint_constructed`.

The finite toy now has a computed P2 constraint that prunes candidate `(G,R)` tokens, a selection rule that collapses the remaining set to `w_SM`, and a joint co-determination signature tying the E019 and E020 facets to one selected point.
