# Cluster A Step 9 Results: Facet Factorization Test

## Inputs

This step reads the Step 8 neutral product carrier and the Step 8 structural survivors:

- Neutral candidate space: 8640 worlds.
- Structural survivor set: 468 worlds.
- Facets tested: `gauge_code`, `rep_code`, `n_gen`, `texture_code`, `ew_code`, `uv_code`, `vacuum_code`.
- Pairwise graph threshold: 0.01 bits of mutual information.
- Robustness checks: stricter naturalness cut `naturalness_cost <= 1`; deterministic 80 percent survivor subsample with seed `20260606`.

## Total Correlation

| population | size | total correlation C (bits) | sum marginal entropies (bits) | joint entropy (bits) | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| neutral product | 8640 | 0.000000000000 | 13.076815597051 | 13.076815597053 | independent neutral control |
| structural survivors | 468 | 2.229304481463 | 11.099669201047 | 8.870364719583 | block-structured coupling |
| stricter naturalness cut | 341 | 2.053633293812 | 10.467261222836 | 8.413627929024 | coupled single component |
| deterministic 80 percent subsample | 374 | 2.512274397383 | 11.059168857271 | 8.546894459888 | block-structured coupling |

The neutral baseline gives C = 0, so the metric is not producing coupling on an independent product population. The survivor population has C = 2.229304481463 bits, so the structural pruning from Step 8 induces cross-facet dependence.

## Coupling Graph

On the 468 structural survivors, the coupling graph has two connected components:

1. `gauge_code+n_gen+rep_code+texture_code+uv_code+vacuum_code`
2. `ew_code`

The best graph-induced block product therefore separates the EW facet from a six-facet block. The within-block correlation is 2.193305564583 bits, and the inter-block residual lost by using this block product is 0.035998916880 bits.

The strongest pairwise links in the survivor set are `gauge_code--rep_code` (0.984822868985 bits), `rep_code--n_gen` (0.466365555634 bits), and `gauge_code--n_gen` (0.466203233486 bits). This is consistent with Step 8: gauge-generation coupling is absent on the neutral product and induced by the structural constraints.

## Robustness

The stricter naturalness cut yields one connected component across all seven facets, with C = 2.053633293812 bits. The deterministic 80 percent subsample preserves the main block split, with C = 2.512274397383 bits and the same six-facet block plus `ew_code`.

This means the verdict is not a zero-coupling result, but it is also not a clean monolithic single-component result on the main declared survivor set. The honest conclusion is block-structured coupling: Step 8's structural constraints support a coupled selection block, while the EW facet is only weakly connected in the main survivor graph.

## Verdict

Facet factorization test constructed. The neutral product is independent, while the Step 8 survivor set is non-factorizing with C = 2.229304481463 bits. The survivor coupling graph splits into two blocks: `{gauge, rep, n_gen, texture, uv, vacuum}` and `{ew}`, with an inter-block residual of 0.035998916880 bits. The toy supports a coupled selection structure with a weak EW separation, not a proof of one physical selection layer.

## Validator Interface

`python3 run_step9.py` runs this step's self-check only. `python3 run_step9.py --chain` runs Steps 1-8 once each in self mode, then runs this step's self-check.
