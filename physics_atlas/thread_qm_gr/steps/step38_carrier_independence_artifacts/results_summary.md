# Step 38 Results Summary

## Orientation

Step 38 addresses the R2 carrier-consistency objection by rerunning the four decisive bounded-grammar computations on a second declared carrier.  The endpoint mode grammar is held fixed:

- `q_QM = (d0_density, d1_phase, d2_transport)`
- `q_GR = (d0_density, d2_transport, d3_curvature)`
- `L = (d0_density, d1_phase, d2_transport, d3_curvature)`

The first reference carrier is the sparse 8-state carrier used in Steps 33-34.  The second carrier is the complete 16-state binary carrier over the same four modes, written in `second_carrier_states_step38.csv`.

## Active Residual

`R2_carrier_consistency_for_QM_GR_no_go_and_uniqueness`: determine whether the directed no-go, fused no-go, type-uniqueness, and instance-uniqueness verdicts are artifacts of one state set or stable properties of the four-mode grammar.

## Computed Side-By-Side

| Lemma | Sparse 8-state reference | Complete 16-state rerun | Stability |
|---|---:|---:|---|
| Directed no-go | row residuals `0.577350/0.577350`; pair defects `3/0` | row residuals `0.577350/0.577350`; pair defects `8/8` | stable by row-span mode grammar; complete carrier supplies both finite pair witnesses |
| Fused no-go | union rank `4`, dim `6`, defect `2` | union rank `4`, dim `6`, defect `2` | stable |
| Type-uniqueness | only `BridgeMediatedRole`; coarsening min `O_s=3` | only `BridgeMediatedRole`; coarsening min `O_s=8` | stable |
| Instance-uniqueness | `L` residual `0/0`; drop-min `0.577350`; union rank `4/6`; relabel iso | same | stable |

The sparse first carrier is not a complete finite-pair witness carrier for every missing direction: it has no pair with equal `q_GR` and different `d1`.  This is why the directed pair counts are `3/0` there even though the row-span residuals are positive in both directions.  The complete 16-state carrier realizes every fiber witness and gives pair defects `8/8`.

## Can-Fail Control

The nested-endpoint control changes the endpoint pair so `d3_nested = d1`, making `q_GR_nested = (d0,d2,d1)` a function of `q_QM`.  On that control:

- `q_GR_nested` through `q_QM` residual = `0`
- `q_QM` through `q_GR_nested` residual = `0`
- finite pair defects = `0/0`
- role obstruction `O_s = 0`
- directed no-go fires = `False`

This flips the no-go when the endpoint grammar genuinely nests.

## Verdict

`carrier_independence_mode_grammar_stable_R2_resolved`.

The four decisive verdicts are stable across the declared carriers, so the Step 32/35 no-go-and-uniqueness program is best stated as a property of the QM/GR four-mode grammar over a finite-carrier family, not as a claim tied to a single 8-state set.  R2 is resolved by recording `G*` as a family of declared finite carriers over the four modes.

## Current Frontier

The standing next gate is external frame-transfer review: continuous carriers, Lorentzian structure, gauge/diffeomorphism quotienting, and richer physical field content remain outside this finite-carrier check.
