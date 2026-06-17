# Step 43 Results Summary

## Deflationary Truth First

Step 43 attacks only the bounded-window caveat. It does not change the conditional status of the Step-38/41 clean-separation result: clean-separation remains an introduced recognition-source closure condition, expressed as Delta_fact=empty, and this step supplies no external-transfer certificate.

## Covered Window

- Declared widened target window: factor counts 1..3, dimensions 2..6, charge units -6..6.
- Exact full-chain coverage: 27 structures.
- Skipped dense three-factor branches: 28 structures, recorded explicitly in `coverage_statement_step43.csv`.
- Tractable exact rule: all one- and two-factor structures are exact; three-factor branches are exact when field-type count <= 90.

## Verdict

`WINDOW_STABLE_BOUND_CANDIDATE_PARTIAL`.

The exact widened rows preserve the Step-38/41 clean result: the only clean-separation structure found is `2|3` with 8 clean supports. No new clean competitor appears in the exact one/two-factor widened window or in the sampled three-factor high-dimension corner. This is window-closure progress, not an unconditional theorem.

## Candidate Bounds

| candidate bound | status | evidence |
| --- | --- | --- |
| single_factor_N_ge_3_clean_separation_bound | structural-arguable | 3:higher=0:clean=0;4:higher=4:clean=0;5:higher=0:clean=0;6:higher=0:clean=0 |
| factor_count_ge_3_bound | empirical-partial | exact_samples=7; skipped_dense_branches=28; exact_sample_clean=0 |
| charge_lattice_bound | empirical-only | charge_units=-6..6 in units inherited from the corrected Step-28/33 carrier; clean set is unchanged inside this lattice. |

## Honest Scope

The single-factor bound is structurally arguable because partial breaking of a single non-abelian factor leaves coset vectors charged under the surviving confining subgroup, producing a nonempty Delta_fact. The factor-count and charge bounds are not closed here; they are empirical or partial and remain the next window-closure targets.
