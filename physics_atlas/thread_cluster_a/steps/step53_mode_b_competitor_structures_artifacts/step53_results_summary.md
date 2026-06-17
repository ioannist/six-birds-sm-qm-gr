# Step 53 Results Summary

## Caveats First

1. This table is not exhaustive. It covers a finite named-competitor set inside a bounded SU(N)-product window.
2. The three-factor exclusions are cap-conditional: they use the Step-44 component cap 6 route-completeness bound.
3. Competitor-to-toy identification is a recognition mapping; the toy tests gauge-structure shadows, not full physical competitor theories.
4. Exclusions remain conditional on the introduced clean-separation recognition source. The single-factor bound is structural-arguable, not a cap-independent proof over all possible structures.

## Competitor Table

| name | toy structure | fund dims | factor count | bucket | excluding gate/reason | cap conditional |
|---|---|---:|---:|---|---|---|
| SU(5) | SU(5) | 5 | 1 | IN_WINDOW_FILTER_EXCLUDED | mass-closure | False |
| flipped SU(5) | SU(5) x U(1) flip-choice | 5 | 1 | IN_WINDOW_FILTER_EXCLUDED | mass-closure | False |
| Pati-Salam SU(4)xSU(2)xSU(2) | SU(4) x SU(2) x SU(2) | 4|2|2 | 3 | CAP_EXCLUDED | factor-count>=3 component-cap route-completeness bound | True |
| left-right SU(3)xSU(2)xSU(2)xU(1) | SU(3) x SU(2) x SU(2) x U(1) | 3|2|2 | 3 | CAP_EXCLUDED | factor-count>=3 component-cap route-completeness bound | True |
| trinification SU(3)xSU(3)xSU(3) | SU(3) x SU(3) x SU(3) | 3|3|3 | 3 | CAP_EXCLUDED | factor-count>=3 component-cap route-completeness bound | True |
| SO(10) | SO(10) | 10 | 1 | OUT_OF_ALPHABET_OR_WINDOW | outside SU(N)-product alphabet; fund dim 10 > cap 6 | True |
| E6 | E6 | 27 | 1 | OUT_OF_ALPHABET_OR_WINDOW | outside SU(N)-product alphabet; fund dim 27 > cap 6 | True |

## Verdict

`COMPETITORS_TABULATED_SM_SELECTED_IN_COVERED_WINDOW`.

The named in-window competitors are excluded by pre-existing Step-43/44 gates, while the `2|3` control remains a clean-separation survivor with 8 supports. Orthogonal and exceptional competitors are future/out-of-alphabet cases, not refuted.
