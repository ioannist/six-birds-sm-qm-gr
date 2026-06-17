# Independent Re-Derivation Record

This manifest records the public diagnostic artifacts used to cross-check the three Section 6 predictions independently
of prose logs. The validators remain the executable source of truth; this file identifies the non-log artifacts that
carry the direct re-derivation outputs.

## Prediction 1: entanglement does not determine geometry

Track directory:
`physics_atlas/thread_qm_gr/steps/step55_f51_entanglement_underdetermines_geometry_artifacts/`

Executable checks:
- `python3 run_step55.py --self`
- `python3 entanglement_underdetermines_geometry_step55.py`

Diagnostic outputs:
- `generic_seed_summary_step55.csv`: central-difference ranks/nullities for seeds 101, 202, 303.
- `witness_pair_step55.csv`: same-fingerprint, different-geometry witness.
- `control_injectivity_step55.csv`: boundary-tree control with nullity 0.
- `step55_schema.json`: machine-readable verdict fields.

## Prediction 2: BMV-null fork-channel prediction

Track directory:
`physics_atlas/thread_qm_gr/steps/step56_gravitational_mediation_bmv_prediction_artifacts/`

Executable checks:
- `python3 run_step56.py --self`
- `python3 gravitational_mediation_bmv_prediction_step56.py`

Diagnostic outputs:
- `density_matrices_step56.csv`: initial and channel-output density-matrix diagnostics.
- `channel_outputs_step56.csv`: fork-channel and coherent-control readouts.
- `local_bound_enumeration_step56.csv`: CHSH local-bound enumeration.
- `channel_restriction_derivation_step56.csv`: derivation record for the channel restriction.
- `step56_schema.json`: machine-readable verdict fields.

## Prediction 3: record-stability, baryon conservation, and no monopole

Track directory:
`physics_atlas/thread_cluster_a/steps/step69_mode_t_record_stability_baryon_no_monopole_falsifiable_prediction_artifacts/`

Executable checks:
- `python3 run_step69.py --self`
- `python3 record_stability_prediction_step69.py`

Diagnostic outputs:
- `record_stability_branch_table_step69.csv`: the 2-by-2 record-stability/clean-branch table.
- `anti_circularity_witnesses_step69.csv`: single-conjunct counterexample witnesses.
- `f27_f48_branch_confirmation_step69.csv`: F27/F48 branch confirmation.
- `step69_schema.json`: machine-readable verdict fields.
