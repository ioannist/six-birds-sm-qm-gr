# P1-HYGIENE v3: five-move active-cut closure

## Certified fifth move

The maintained closure now includes exact `Delta-Y` and `Y-Delta` replacement. For a triangle with capacities `w01,w02,w12`, the replacement star has legs `a0=w01+w02`, `a1=w01+w12`, and `a2=w02+w12`; the inverse uses the exact half-sum formulas. Every proposal is accepted only after re-enumerating every nonempty proper boundary region, checking exact equality of all rational minimum-cut values, and confirming continued unique minimizers. The declared three-round search includes equal/intermediate presentations and prevents inverse-move oscillation by its finite depth.

The 378-carrier search reproduces the required transition: **22 of the 35 four-move survivors are explained**, leaving **13**. Their residual-deficiency histogram is **1:8|2:4|3:1** (`1^8, 2^4, 3^1`). The maintained finite search exhausts three replacement rounds, sufficient for this declared family and including the named two-replacement regression.

| carrier | seed | unique_all_regions | raw_exact_rank | raw_deficiency | reduction_moves | fifth_move_count | reduced_exact_rank | residual_deficiency | all_region_values_preserved |
|---|---|---|---|---|---|---|---|---|---|
| published_step42_raw | 101 | True | 9 | 5 | series_bivalent|series_bivalent|series_bivalent | 0 | 9 | 0 | True |
| crosslinked_three_path | 101 | True | 9 | 8 | exact_two_terminal_module | 0 | 9 | 0 | True |
| grid_2x3_multiterminal | 101 | True | 10 | 3 | saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction | 0 | 10 | 0 | True |
| k4_well_connected_stiff_chord | 101 | True | 11 | 3 | inseparable_vertex_contraction_parallel_sum | 0 | 11 | 0 | True |
| published_step42_raw | 202 | True | 9 | 5 | series_bivalent|series_bivalent|series_bivalent | 0 | 9 | 0 | True |
| crosslinked_three_path | 202 | True | 9 | 8 | exact_two_terminal_module | 0 | 9 | 0 | True |
| grid_2x3_multiterminal | 202 | True | 10 | 3 | saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction | 0 | 10 | 0 | True |
| k4_well_connected_stiff_chord | 202 | True | 11 | 3 | inseparable_vertex_contraction_parallel_sum | 0 | 11 | 0 | True |
| published_step42_raw | 303 | True | 9 | 5 | series_bivalent|series_bivalent|series_bivalent | 0 | 9 | 0 | True |
| crosslinked_three_path | 303 | True | 9 | 8 | exact_two_terminal_module | 0 | 9 | 0 | True |
| grid_2x3_multiterminal | 303 | True | 9 | 4 | saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction | 0 | 9 | 0 | True |
| k4_well_connected_stiff_chord | 303 | True | 11 | 3 | inseparable_vertex_contraction_parallel_sum | 0 | 11 | 0 | True |

## Named K2,3 regression

`K23_bipartite__b6__leaf_offset0__seed31` retains all 62 exact cut values and unique minimizers after every accepted move. Its path is inseparable contraction, `Y-Delta`, `Delta-Y`, and series reduction. Rank is re-enumerated after each step and finishes at rank 8 on 9 edges, residual deficiency 1:

| move_index | move | object | region_count | all_region_values_preserved | unique_after_move | rank_recomputed_after_move | residual_deficiency_after_move |
|---|---|---|---|---|---|---|---|
| 0 | inseparable_vertex_contraction_parallel_sum | I1+I2 | 62 | True | True | 8 | 3 |
| 1 | y_delta | I4 | 62 | True | True | 8 | 2 |
| 2 | delta_y | <I1+I2>+I0+I3 | 62 | True | True | 8 | 2 |
| 3 | series_bivalent | I3 | 62 | True | True | 8 | 1 |
| final | closure_result | named_regression | 62 | True | True | 8 | 1 |

## Experimental sixth-move frontier

The two named candidate moves are tested but explicitly excluded from the certified closure:

| experimental_rule | certified_closure_member | five_move_survivors_tested | candidate_directions | accepted_exact_finite_directions | survivors_fully_explained | outcome |
|---|---|---|---|---|---|---|
| EXPERIMENTAL_K23_FOUR_CYCLE_TRANSPORT | False | 13 | 25 | 0 | 0 | EXPLAINS_NONE |
| EXPERIMENTAL_K4_OPPOSITE_PERFECT_MATCHING | False | 13 | 3 | 0 | 0 | EXPLAINS_NONE |

Neither four-cycle/transportation redistribution nor K4 opposite-perfect-matching redistribution is an exact active-cut null direction on any of the 13 remaining carriers. Thus neither explains a survivor under the same exact-incidence plus two-sided finite-invariance bar. This is the recorded open frontier; no further move is pursued in this campaign.

## Outcome

**FIVE_MOVE_CLOSURE_LEAVES_13_RESIDUAL_SURVIVORS_EXPERIMENTAL_SIXTH_MOVES_EXPLAIN_NONE**. The fifth move materially contracts the frontier from 35 to 13 carriers, but it does not close the graph-level question completely.
