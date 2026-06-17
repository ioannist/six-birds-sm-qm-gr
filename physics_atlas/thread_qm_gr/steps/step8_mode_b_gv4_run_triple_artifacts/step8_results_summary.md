# Step 8 Results Summary: Mode B G_v4 Run-Generated Triple Mechanism

## Orientation

Step 8 tests the structurally different obligation from Step 7:

`G_E018_RunGeneratedTripleMechanism_v4`

Active residual:

`R_child_E018_after_Gv3_triple_no_go`

The attempt is E0-style: a finite substrate is actually simulated, then the sector readouts and witness are measured from the run.

## Bounded Grammar Declared First

The grammar declaration was appended before simulation:

`G_E018_RunGeneratedTripleMechanism_v4_DECLARED_STEP8`

Allowed:

- finite stochastic substrate;
- sector readouts measured after the run;
- out-of-sample witness measured from held-out trajectory windows.

Excluded:

- triple objective in the update rule;
- triple target row as substrate input;
- pairwise-union witness;
- post-run diagonal forcing;
- substrate definition that makes sector coherence primitive.

## Substrate and Readouts

Substrate:

- binary periodic ring;
- stochastic nearest-neighbor parallel update;
- refinements `N=32` and `N=64`;
- `steps=720`, `burn_in=120`, `replicas=64`.

Measured sector proxies:

- area-entanglement: boundary mutual information;
- amplitude-geometry: first Fourier-mode amplitude;
- P3-route: coarse/evolve route-closure proxy.

Independent witness:

- held-out `R^2` gain from adding an interaction term beyond pairwise predictors.

Completion audit:

- Schur residual of the final sector plateau against the diagonal common fixed-point subspace.

## Run Results

| refinement | completion Xi | threshold | held-out interaction gain | threshold | candidate pass |
|---:|---:|---:|---:|---:|---|
| `N=32` | `0.4947207905172907` | `0.02` | `-0.02326224393247789` | `0.05` | false |
| `N=64` | `0.5371910513210945` | `0.02` | `-0.08539192789918792` | `0.05` | false |

Rejected controls:

- pairwise-union statistic is measured but not accepted as a witness;
- rigged diagonal completion gives near-zero Xi only by forcing equal sector plateaus after the run.

## Verdict

**Run-level no-go / obstruction.**

The declared substrate does not exhibit a non-rigged triple mechanism:

- the common fixed-point residual stays large at both refinements;
- the held-out interaction witness is negative at both refinements;
- the only near-zero completion control is post-run forcing and is rejected.

The triple shared-package residual therefore survives this G_v4 run attempt.

## Next Grammar Delta

`G_E018_IndependentDynamicsOrRecognition_v5`

Required shape:

`A genuinely different dynamics class or a named recognition import with independent records that generate the triple package without a target-row input, pairwise-union witness, or post-run forcing.`

## Framework Output Classification

- Predictive structural: bounded G_v4 run grammar and no-rigging thresholds.
- Analytical structural: two-refinement stochastic run, Schur residual, and held-out witness.
- Organizational/audit: schema, nonclaim boundary, gate tables, lineage, grammar, and constraint-ledger updates.
- Remaining external content: a substrate/dynamics class or recognition source with independent triple records.

## Completion Status

Step 8 completes the requested G_v4 run attempt with a typed run-level obstruction:

`R_child_E018_after_Gv4_run_obstruction`
