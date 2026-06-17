# Cluster A Step 11 Results: Refinement-Order Battery

## Inputs

Step 11 runs the collapse-vs-landscape audit on the Step 8 structural survivor carrier:

- Structural survivor count: `468`.
- Facets: `gauge_code`, `rep_code`, `n_gen`, `texture_code`, `ew_code`, `uv_code`, `vacuum_code`.
- Partial refinement depth: `4` facets revealed.
- Significance threshold: `0.25`.
- Sharp rank width: `0.55`.
- Random orders: `200`.
- Random seed: `20260606`.

The genuine-selection case is a sharp structural measure centered on the token-blind structural argmax. The landscape case is a broad flat support over the same partial-refinement cylinder.

## Random-Order Distribution

| case | random orders | collapse fraction | non-collapse fraction | final degeneracy range | histogram |
| --- | ---: | ---: | ---: | --- | --- |
| genuine selection | 200 | 1.000000000000 | 0.000000000000 | 1 to 1 | `1:200` |
| landscape measure | 200 | 0.000000000000 | 1.000000000000 | 6 to 27 | `6:4;9:15;12:23;13:9;14:17;15:5;16:10;18:73;21:31;27:13` |

The random-order ensemble cleanly separates the two cases.

## Adversarial Orders

Two adversarial orders were computed:

- `adversarial_delay_genuine`: tries to delay collapse of the genuine case. Outcome: genuine final degeneracy `1`; landscape final degeneracy `27`.
- `adversarial_force_landscape`: tries to force the landscape to collapse. Outcome: genuine final degeneracy `1`; landscape final degeneracy `6`.

The adversarial battery therefore does not flip either verdict on this finite carrier.

## Separation

Across all 204 orders (canonical, reverse, two adversarial, and 200 random):

- Max genuine final degeneracy: `1`.
- Min landscape final degeneracy: `6`.
- Separation margin: `5`.
- Flipping order count: `0`.

## Verdict

The collapse-vs-landscape verdict is order-invariant on the declared token-blind finite battery. The result tracks the measure structure rather than a hand-aimed order: the sharp structural selection collapses under every tested order, and the broad landscape remains multiply supported even under the order designed to force collapse.

Honest grade: finite-grammar order-invariance on the declared toy. It is not a parameter-free physical theorem, does not compute physical values, and does not settle real mechanisms.

## Validator Interface

`python3 run_step11.py` runs this step's self-check only. `python3 run_step11.py --chain` runs Steps 1-10 once each in self mode, then runs this step's self-check.
