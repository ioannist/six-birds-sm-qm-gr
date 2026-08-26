# S1-REPAIR-3 typed-condition results

Version-1 and version-2 outputs remain historical and byte-unchanged. Version 3 types the version-2 branch scope as **singleton complex scalars**, reports both charge-normalization conventions, and adds a separately scoped two-scalar appendix.

## Singleton-scalar headline

| dimensions | active factors | verdict | branches |
|---|---|---|---|
| 2|3 | SU(2) | clean | 4 |
| 2|3 | SU(3) | breaking | 4 |
| 4 | SU(4) | breaking | 4 |

The singleton scope contains 12 admissible branches over eight of the 52 chirality-faithful structures. Four singleton branches are clean, all over `2|3` with SU(2)-active scalars. The remaining **44 structures are without an admissible singleton complex-scalar branch**. The version-2 universal and existential conclusions are unchanged within this explicitly typed scope.

## Two-scalar appendix

| dimensions | active factors | verdict | branches |
|---|---|---|---|
| 2|3 | SU(2) | clean | 68 |
| 2|3 | SU(2)|SU(3) | breaking | 264 |
| 2|3 | SU(3) | breaking | 158 |
| 3 | SU(3) | breaking | 1706 |
| 4 | SU(4) | breaking | 628 |

There are 2824 admissible unordered two-scalar pair branches (829 declared pair orbits) over all 52 chirality-faithful structures. All 44 structures without a singleton branch acquire at least one admissible pair branch:

| dimensions | newly pair admissible structures |
|---|---|
| 2|3 | 2 |
| 3 | 28 |
| 4 | 14 |

There are 68 clean pair branches (17 declared pair orbits), but **no clean pair occurs outside `2|3` with SU(2)-only scalar action**. Thus the two-scalar extension removes the “no admissible branch” obstruction for all 44 structures while sharpening, rather than broadening, the clean-family statement. These appendix counts do not replace the singleton headline.

## Charge-normalization census

| stage | labelled count | declared orbit count | primitive normalized orbit count | labelled stage exclusion percent | declared orbit stage exclusion percent | primitive stage exclusion percent | labelled cumulative exclusion percent | declared orbit cumulative exclusion percent | primitive cumulative exclusion percent |
|---|---|---|---|---|---|---|---|---|---|
| genuinely_chiral | 1066 | 419 | 195 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| atomic_packaging | 84 | 37 | 37 | 92.120075 | 91.169451 | 81.025641 | 92.120075 | 91.169451 | 81.025641 |
| closure_consistency | 62 | 27 | 27 | 26.190476 | 27.027027 | 27.027027 | 94.183865 | 93.556086 | 86.153846 |
| chirality_faithfulness | 52 | 24 | 24 | 16.129032 | 11.111111 | 11.111111 | 95.121951 | 94.272076 | 87.692308 |

The cumulative chiral-to-faithful comparisons are therefore `1,066 -> 52 = 95.121951%` labelled, `419 -> 24 = 94.272076%` under declared-charge orbits, and `195 -> 24 = 87.692308%` under primitive-normalized orbits. Primitive-normalized orbits are preferred for the community-facing denominator because overall U(1) scale is conventional; declared-charge orbits remain the exact bounded-enumeration comparison.

## Independent singleton gate

The independent table generates 618 cap-filtered scalar rows across all factor structures and is conjugation closed. Exact Littlewood-Richardson decomposition evaluates 368 ordered representation triples; all 14/14 known decomposition checks pass and singlet multiplicity is permutation invariant. Without calling production `neutral_rep_assignments`, `scalar_representations`, `factor_invariant`, or `yukawa_invariant`, the gate regenerates exactly 12 singleton branch keys, equal to the written headline table.

## Scope condition

Both singleton and pair residual/`Delta_fact` columns remain conditional finite-toy proxy diagnostics. The pair appendix uses the inherited SU(N-1) residual rule and does not derive multi-VEV alignment.
