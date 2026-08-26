# Q2-REPAIR-1: route-mismatch repair

## Published result reproduced and corrected

| encoding | completion_table_distance_raw | completion_table_distance_normalized | commutator_defect_cardinality | commutator_spectral_norm | commutator_on_encoded_table_norm |
|---|---|---|---|---|---|
| zero_one | 2.8284271247461903 | 0.5 | 0 | 0.0 | 0.0 |
| plus_minus_one | 5.656854249492381 | 0.7071067811865476 | 0 | 0.0 | 0.0 |

The published `0.5` is `||E_QM(C)-E_GR(C)||_F/||C||_F` on the 0/1 table, not a commutator. Re-encoding the same states as plus/minus one changes that distance to `1/sqrt(2)`. Both completions are exactly idempotent, while `E_QM E_GR = E_GR E_QM` exactly: the defect set is empty and the commutator norm is zero in both encodings.

The reason is structural. On a uniform product cube, conditional expectation onto coordinates `A` followed by conditional expectation onto coordinates `B` averages over the union of their hidden coordinates. Order is irrelevant, and both compositions equal conditional expectation onto `A intersect B`. Here `A={d0,d1,d2}`, `B={d0,d2,d3}`, and the common result is the completion visible on `{d0,d2}`. Coordinate overlap alone does not create non-commutativity; nonfactorizing access structures or a genuinely different completion operation are required.

## Candidate table

| pair_id | family | left_idempotent | right_idempotent | commutes | defect_set_cardinality | commutator_spectral_norm | normalized_hilbert_schmidt_norm |
|---|---|---|---|---|---|---|---|
| published_coordinate_pair | published_reproduction | True | True | True | 0 | 0.0 | 0.0 |
| conditional_mean_vs_nonlinear_source_projection | repair_candidate_nonlinear | True | True | False | 16 | 1.0 | 0.7071067811865476 |
| nonfactorizing_conditional_means | repair_candidate_nonfactor_partitions | True | True | False | 12 | 0.4330127018922193 | 0.21650635094610965 |
| nested_coordinate_control | commuting_control | True | True | True | 0 | 0.0 | 0.0 |

The defect set is the exact finite set of carrier rows at which the two composition distributions differ; all rows and exact rational distributions are exported. The primary magnitude is the spectral norm of the exact commutator matrix. It is independent of coordinate value encoding and invariant under carrier relabeling by permutation conjugacy. All 24 coordinate permutations were checked for every pair.

The nonlinear candidate makes the operations genuinely different: the first completion averages over the curvature bit, whereas the second retracts onto `d3 = d0 OR d2`, a thresholded source-consistency constraint motivated by Step26's density and gradient/transport contributions. Its non-commutativity is exact on all 16 states. What remains imported is the Boolean threshold and the finite identification of the transport bit with the gradient source term.

The second candidate keeps both operations as conditional means but uses aggregate access partitions `(d0,d1+d2)` and `(d0,d2+d3)`. Their fibers do not form a product, and the exact commutator is nonzero on 12 states. The aggregate readouts are an explicit coarse-graining ansatz, not a frozen track prediction.

## Claim ledger and outcome

| claim | status | evidence |
|---|---|---|
| published E_QM and E_GR do not commute | REFUTED_ON_PUBLISHED_CARRIER | exact commutator zero; defect set empty; 0.5 is table distance |
| nonlinear source-projection repair candidate | COMPUTED_NONCOMMUTING_MOTIVATION_SUBJECT_TO_EDDY | defects=16; spectral_norm=1.0 |
| nonfactorizing-access repair candidate | COMPUTED_NONCOMMUTING_COARSE_GRAINING_IMPORTED | defects=12; spectral_norm=0.4330127018922193 |
| completion algebra can detect commuting cases | LANDED_BY_CONTROL | nested coordinate control exact commutator zero |

**GENUINE_NONCOMMUTING_FINITE_CANDIDATES_EXIST_MOTIVATION_SUBJECT_TO_REVIEW**. A genuine non-commuting finite completion pair exists, so there is a mathematically valid repaired-Q2 candidate. It does not rescue the published calculation: the published pair commutes, and its claimed mismatch was a mislabeled, encoding-dependent table distance. Whether the nonlinear candidate faithfully represents “quantize then curve versus curve then quantize” remains a motivation ruling for Eddy; absent that ruling, the paper must retract the claim for its stated carrier and operators.
