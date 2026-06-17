# Consolidated Findings - Cluster B

## Grade

Grade: finite-carrier bounded-grammar consolidation.

This synthesis consolidates verified Steps 1-3. It states the shape of the E021/E042 holes on the declared finite carrier. It does not supply physical content: no Lambda value, no high-curvature substrate, no unconditional atlas closure, and no frame-transfer certificate.

Sources: `steps/step1_shared_substrate_frame_artifacts/results_summary.md`, `steps/step2_e042_singularity_resolution_artifacts/results_summary.md`, `steps/step3_e021_cosmological_constant_artifacts/results_summary.md`.

## Shared Frame

Grade: frame-signature.

Step 1 establishes `L_ext=(d0,d1,d2,d3,d4_subplanck,d5_vacuum)`. E042 `d4_subplanck` and E021 `d5_vacuum` are non-descending L-readouts:

- E042 `d4`: GR obstruction `3`, q_QM obstruction `11`, witnesses `1-2;5-6;10-11`.
- E021 `d5`: GR obstruction `1`, q_QM obstruction `3`, witness `3-4`.
- smooth GR descent residual `0.0`.
- controls: descending `d3` factors; smooth `d4` factors through `d3`; `d4` tears only at high curvature.

The non-descending `d4_subplanck` / `d5_vacuum` readouts are deliberately INSTANTIATED by branch splits in the toy carrier (high-curvature bases split in `d4`; one vacuum base splits in `d5`); the controls (`d3` factors; `d4` factors through `d3` in the smooth regime) show the finite test DISCRIMINATES, but do NOT certify physical frame transfer.

Sources: `steps/step1_shared_substrate_frame_artifacts/frame_signatures_step1.csv`, `steps/step1_shared_substrate_frame_artifacts/shadow_descent_step1.csv`, `steps/step1_shared_substrate_frame_artifacts/controls_step1.csv`.

## E042 Boundary

Grade: finite-toy-diagnostic.

Step 2 constructs E042 as a typed boundary of L's geometry readout:

- GR `K_GR`: `0.81 -> 13271.04`, last increment `9953.28`, non-stabilizing.
- L `R_L`: `0.05833333333333335 -> 0.749957784016927`, last increment `0.0001266479492186834`, finite stabilizing toy readout with `R*=0.75`.
- bad control `R_bad`: `0.9 -> 115.2`, non-stabilizing.
- toy Planck crossover: `K_P=16.0`, `n*=4`, `epsilon*=0.125`, `K=51.84`.
- finite L continuation through post-locus rows, assigned by the toy rather than derived from a constraint or evolution law.
- high-curvature d4 non-factorization count `3`.

Grade: modeled-shape.

This structurally matches the conventional high-curvature-repair candidate, but the saturating form is modeled. It is not a derived substrate.

Sources: `steps/step2_e042_singularity_resolution_artifacts/refinement_sequence_step2.csv`, `steps/step2_e042_singularity_resolution_artifacts/p6_ledger_step2.csv`, `steps/step2_e042_singularity_resolution_artifacts/planck_staging_step2.csv`, `steps/step2_e042_singularity_resolution_artifacts/geodesic_continuation_step2.csv`, `steps/step2_e042_singularity_resolution_artifacts/nonfactorization_signature_step2.csv`, `steps/step2_e042_singularity_resolution_artifacts/controls_step2.csv`.

## E021 Vacuum Readout

Grade: finite-toy-diagnostic.

Step 3 constructs E021 as an audited selected/run vacuum readout:

- selected toy `rho_IR=0.0010400000000000001`.
- toy `rho_UV=1040000000.0000001`.
- modeled ratio `10^12`, marked `toy_modeled_not_real_120`.
- unaudited cancellation row: counterterm `1039999999.9989601`, tracked `False`.
- booked ledger: `12.0->8.0->4.0->0.0`.
- selection: `vac_A_selected` selected from five candidates by `minimum_selection_score`.
- UV-to-Lambda obstruction count `4`, witnesses `0-1;0-2;1-2;3-4`.
- descending UV coupling control obstruction count `0`.

Grade: modeled-shape.

The booked UV-to-IR ledger is MODELED/illustrative P6 bookkeeping, not a firm audit computed from a coarse map, RG flow, or package dynamics.

Grade: contested-reading.

Firm: selected/run readout with non-factorization obstruction `4` and the descending-control contrast (obstruction `0`). Contested: the distinct audited-currency interpretation; it is casting-dependent and remains a flagged hypothesis.

Sources: `steps/step3_e021_cosmological_constant_artifacts/vacuum_currency_step3.csv`, `steps/step3_e021_cosmological_constant_artifacts/uv_ir_ledger_step3.csv`, `steps/step3_e021_cosmological_constant_artifacts/vacuum_selection_step3.csv`, `steps/step3_e021_cosmological_constant_artifacts/nonfactorization_step3.csv`, `steps/step3_e021_cosmological_constant_artifacts/controls_step3.csv`.

## Unifying Reading

Grade: modeled-shape.

E018, E042, and E021 share one framework shape: a clean cross-layer descent is the wrong demand; the lawful object is a readout/audit on L. E018 supplies the co-sourcing common-refinement precedent, E042 supplies finite stabilization at the high-curvature boundary, and E021 supplies an audited selected/run vacuum readout.

This is a finite-toy framework reading, not a physical theory.

Sources: `../thread_qm_gr/interpretation/ladder_vs_fork.md`, `../thread_qm_gr/interpretation/quantum_gravity_is_illegal.md`.

## Open Obligations

Grade: organizational.

Open: external frame-transfer review; richer carriers; E042 substrate identity; Lambda value and selection mechanism; contested E021 distinct-currency reading; consolidation review against the Step 1-3 validators.
