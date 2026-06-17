# Step 5 Regrade Diff

This pass applies only the three accepted external-review overgrade fixes: R1, R2, and R4. It introduces no new computation.

## R1 - E042 Continuation

File: `steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex`

Before:

- Claim 5 grade: `finite-toy-diagnostic`.
- Text presented the finite post-locus continuation as part of the Step 2 P2 continuation predicate without the assigned-not-derived caveat.

After:

- Claim 5 grade: `modeled-shape`.
- Added: "The continuation is ASSIGNED by the toy (GR_defined=eps>0, L_defined=True, hand-set post-locus values), NOT derived from a constraint or evolution law; only the finite divergence/stabilization table (Claim 3) is computed."

File: `steps/step4_consolidated_statement_artifacts/content_classification.csv`

Before:

- `e042_planck_continuation` grade: `finite-toy-diagnostic`.

After:

- `e042_planck_continuation` grade: `modeled-shape`.
- Claim text now states that the post-locus continuation is assigned by the toy.

## R2 - E021 Ledger Firmness

File: `steps/step3_e021_cosmological_constant_artifacts/schema.json`

Before:

- `firm_part_missing_audit_ledger: true`.

After:

- `firm_part_missing_audit_ledger: false`.
- `modeled_p6_ledger_illustrative: true`.
- `firm_part_selected_run_readout: true` remains unchanged.

File: `steps/step3_e021_cosmological_constant_artifacts/results_summary.md`

Before:

- Firm part: selected/run readout plus missing audit ledger.

After:

- Firm part narrowed to selected/run readout on the toy: non-factorization obstruction `4` with the descending-control contrast (obstruction `0`).
- Booked UV-to-IR ledger marked as MODELED/illustrative P6 bookkeeping, hand-specified and not a firm audit computed from a coarse map, RG flow, or package dynamics.

File: `steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex`

Before:

- Claim 8 grade: `finite-toy-diagnostic`.
- Claim 10 said the firm E021 result included an audit ledger that books the UV-to-IR mismatch.

After:

- Claim 8 grade: `modeled-shape`.
- Claim 8 explicitly says the booked ledger is MODELED/illustrative P6 bookkeeping.
- Claim 10 narrows the firm result to selected/run non-factorization plus descending-control contrast.

File: `steps/step4_consolidated_statement_artifacts/content_classification.csv`

Before:

- One combined `e021_p5_p6_selection` row graded the ledger/selection bundle as `finite-toy-diagnostic`.

After:

- `e021_selected_nonfactorization` is `finite-toy-diagnostic`.
- `e021_p6_modeled_ledger` is `modeled-shape`.

## R4 - Shared-Frame Branch-Split Transparency

File: `steps/step1_shared_substrate_frame_artifacts/results_summary.md`

Before:

- The carrier construction listed the high-curvature and vacuum branch duplicates but did not explicitly call out that these instantiate the non-descending d4/d5 readouts.

After:

- Added: "The non-descending d4_subplanck / d5_vacuum readouts are deliberately INSTANTIATED by branch splits in the toy carrier (high-curvature bases split in d4; one vacuum base splits in d5); the controls (d3 factors; d4 factors through d3 in the smooth regime) show the finite test DISCRIMINATES, but do NOT certify physical frame transfer."

File: `steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex`

Before:

- The shared-frame claims cited the obstruction witnesses and controls but did not include the branch-split transparency sentence.

After:

- Added the same branch-split transparency sentence to Claim 1.

## Validator Updates

- `run_step3.py` now fails if the ledger is marked firm or if the modeled-ledger flag is absent.
- `run_step4.py` now fails if Claim 5 remains `finite-toy-diagnostic`, if the assigned-continuation disclaimer is absent, or if the E021 firm-part narrowing is absent.
- `run_step5.py` checks the regrade artifacts and re-runs `run_step1.py` through `run_step4.py`.
