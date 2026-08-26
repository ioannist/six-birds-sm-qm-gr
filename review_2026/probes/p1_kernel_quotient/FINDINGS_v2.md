# P1-REPAIR-2: active-cut quotient and irreducibility search

## Machinery regressions

| carrier | seed | unique_all_regions | raw_edges | raw_exact_rank | raw_deficiency | reduction_moves | reduced_edges | reduced_exact_rank | residual_deficiency | all_region_values_preserved |
|---|---|---|---|---|---|---|---|---|---|---|
| published_step42_raw | 101 | True | 14 | 9 | 5 | series_bivalent|series_bivalent|series_bivalent | 9 | 9 | 0 | True |
| crosslinked_three_path | 101 | True | 17 | 9 | 8 | exact_two_terminal_module | 9 | 9 | 0 | True |
| grid_2x3_multiterminal | 101 | True | 13 | 10 | 3 | saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction | 10 | 10 | 0 | True |
| k4_well_connected_stiff_chord | 101 | True | 14 | 11 | 3 | inseparable_vertex_contraction_parallel_sum | 11 | 11 | 0 | True |
| published_step42_raw | 202 | True | 14 | 9 | 5 | series_bivalent|series_bivalent|series_bivalent | 9 | 9 | 0 | True |
| crosslinked_three_path | 202 | True | 17 | 9 | 8 | exact_two_terminal_module | 9 | 9 | 0 | True |
| grid_2x3_multiterminal | 202 | True | 13 | 10 | 3 | saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction | 10 | 10 | 0 | True |
| k4_well_connected_stiff_chord | 202 | True | 14 | 11 | 3 | inseparable_vertex_contraction_parallel_sum | 11 | 11 | 0 | True |
| published_step42_raw | 303 | True | 14 | 9 | 5 | series_bivalent|series_bivalent|series_bivalent | 9 | 9 | 0 | True |
| crosslinked_three_path | 303 | True | 17 | 9 | 8 | exact_two_terminal_module | 9 | 9 | 0 | True |
| grid_2x3_multiterminal | 303 | True | 13 | 9 | 4 | saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction|saturated_terminal_zero_column_contraction | 9 | 9 | 0 | True |
| k4_well_connected_stiff_chord | 303 | True | 14 | 11 | 3 | inseparable_vertex_contraction_parallel_sum | 11 | 11 | 0 | True |

The exact 0/1 active-cut incidence matrix uses one row for every nonempty proper boundary region and one column per edge. Each minimum cut and its runner-up are enumerated with rational capacities; tied rows are excluded. Rank is rational Gaussian-elimination rank, not a finite-difference estimate. Every reduction step is accepted only after recomputing every region and verifying identical minimum-cut values and unique minimizers.

The regressions reproduce the ruling: published ranks `9/9/9` with five series/parallel redundancies removed; the crosslinked module reduces from 17 columns to rank-nine nine-column form; grid ranks are `10/10/9` and zero-column terminal contractions leave `10/10/9` full-rank quotients; stiff K4 has rank 11 and inseparable contraction plus parallel sums leaves 11 columns of rank 11.

## Declared search family

The family contains `14` labelled interior templates and `126` topology/attachment carriers: complete and expander-like interiors, wheels, triangular prism, K5-minus variants, K2,3/K3,3, octahedral, and a crosslinked 2x3 grid. Boundary counts are 6, 7, and 8; interiors contain 3--6 nodes; attachment schemes are leaf-offset zero, leaf-offset one, and dual gateway. Three seeds give `378` weighted carriers. Base capacities lie in `[0.85,1.15]`; exact binary edge perturbations remove ties without creating a broad scale hierarchy.

| evaluated_weighted_carriers | unique_cut_carriers | raw_deficient_carriers | fully_explained_after_closure | residual_survivor_count | residual_deficiency_distribution | survivor_family_distribution |
|---|---|---|---|---|---|---|
| 378 | 378 | 366 | 343 | 35 | 0:343|1:20|2:7|3:6|4:2 | K23_bipartite:18|cycle_chord_m3:12|triangular_prism:2|wheel_W4:3 |

## Landing candidate

The selected landing candidate is `cycle_chord_m3__b6__leaf_offset0__seed17`: six boundary terminals attached in pairs to a three-node complete interior, with nine post-closure edges. Its exact active-cut matrix has rank `8` and deficiency `1`. The minimum uniqueness margin is `0.0599999818392`. No closure move fired before selection, and the independent irreducibility audit reports zero applicable objects for all four named moves.

Its exact integer column dependency is `-1*I0-I1 +1*I0-I2 +1*I1-I2`. Thus increasing `I0-I2` and `I1-I2` while decreasing `I0-I1` leaves every active-cut value fixed inside the unique-cut chamber. Exact finite checks at both signs use `delta=0.0049999984866` and preserve all 62 region values, active cuts, and uniqueness.

## Outcome ruling input

**RESIDUAL_ACTIVE_CUT_DEFICIENCY_SURVIVES_FOUR_NAMED_REDUCTIONS**. A rank-deficient active-cut carrier survives saturated-terminal/zero-column contraction, inseparable-vertex contraction with parallel sums, series reduction, and exact two-terminal-module replacement. This is the graph-level P1 landing candidate requested by the ruling. It remains finite-carrier evidence, not a universal theorem, and is explicitly handed to Eddy for a possible fifth reduction (the three-interior triangle dependency is the obvious target).
