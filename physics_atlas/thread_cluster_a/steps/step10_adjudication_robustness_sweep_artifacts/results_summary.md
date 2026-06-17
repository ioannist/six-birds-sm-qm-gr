# Cluster A Step 10 Results: E043 Adjudication Robustness Sweep

## Inputs

This step sweeps the Step 6 E043 collapse-vs-landscape adjudication over:

- 10 significance thresholds: `0.02` through `0.80`.
- 7 broad final widths: `1.00` through `4.00`.
- 8 sharp final widths: `0.02` through `1.00`.
- 17 grid configurations: the exact Step 6 grid plus log/linear grids at 6, 12, 24, and 48 points over two ranges.

Total swept cells: `9520`.

The qualitative verdict holds when the broad family remains multiply supported and the sharp family collapses to one significant scale point.

## Hold Fraction

- Hold cells: `4922`.
- Flip cells: `4598`.
- Hold fraction: `0.517016806723`.

The sweep is deliberately wide enough to include flips. That is the can-fail control: the adjudication is not treated as parameter-free or automatic.

## Step 6 Operating Point

The Step 6 operating point is:

- Grid: `step6_exact`.
- Threshold: `0.25`.
- Broad final sigma: `2.00`.
- Sharp final sigma: `0.10`.

It is classified as `VERDICT_HOLDS`.

Sequences:

- Broad: `6->6->6->6->6->6`.
- Sharp: `3->2->2->1->1`.

Nearest same-grid flip:

- Flip kind: `sharp_noncollapse`.
- Threshold: `0.25`.
- Broad final sigma: `2.00`.
- Sharp final sigma: `0.40`.
- Normalized margin: `0.306122448980`.

So the Step 6 point is not a one-cell knife-edge: the nearest same-grid flip requires widening the sharp family from `0.10` to `0.40` at the same threshold and broad width.

## Flip Boundaries

Two flip families were found:

1. `sharp_noncollapse`: `3990` cells.
   This is the wide-sharp or low-threshold regime where the sharp family remains multiply supported.

2. `broad_false_collapse`: `608` cells.
   This is the high-threshold, coarse-grid, or narrow-broad regime where the broad family is counted as a singleton.

These flips are the scope boundary of the finite criterion. The Step 6 setting sits inside the hold region, but the sweep also maps where the qualitative judgment breaks.

## Verdict

The collapse-vs-landscape adjudication is stable across a broad declared region of the finite toy parameter space, and the Step 6 operating point lies inside that region. The result is still bounded: it is a finite-grammar robustness map, not a parameter-free physical theorem and not a physical verdict about anthropic arguments.

## Validator Interface

`python3 run_step10.py` runs this step's self-check only. `python3 run_step10.py --chain` runs Steps 1-9 once each in self mode, then runs this step's self-check.
