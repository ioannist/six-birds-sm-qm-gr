# Consolidated Findings: QM-GR Layer Toy Model

This is the consolidated deliverable from the framework-driven cascade. It is self-contained, sourced to verified artifacts, and scoped for external review.

## Setup

E018 asks for a lawful layer above the QM-side and GR-side packages. After Step 10, the construction stopped using the literature-sector spine and let the Six Birds framework enumerate and test the missing-layer structure directly.

The original obstruction has two faces addressed here:

- P3: route mismatch / scale-descent obstruction.
- P2: problem of time, where the GR-consistent form is constrained and relational rather than externally timed.

The finite native carrier is:

- `L=(d0,d1,d2,d3)`
- `q_QM=(d0,d1,d2)`
- `q_GR=(d0,d2,d3)`

The finite physical carrier is a periodic complex field `psi` on `N=8` sites, later extended by finite clock registers.

## Native Structural Classification

1. Promotion-bridge status:
   Step 17 classifies `B_QM_to_L` as native status `candidate`, passing all eight gates. The direct-sum package is strict too, so strictness does not distinguish it; it fails `G_nosmuggle` by duplicating shared observables `d0,d2`.
   Source: [step17_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step17_native_promotion_bridge_classification_artifacts/step17_results_summary.md).

2. F37 joint quotient:
   Step 18 computes `a o j=q_QM` and `b o j=q_GR` with residual `0.0`, so an admissible joint quotient exists on the toy. Therefore `q_QM` and `q_GR` are not complementary on the toy.
   Source: [step18_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step18_f37_complementarity_f24_resolution_artifacts/step18_results_summary.md).

3. F24 resolution family:
   Step 20 constructs the eight operational selectors; Step 21 recomputes them from maps and real structures. `L_candidate_package` selects uniquely as `BridgeMediatedRole`.
   Sources: [step20_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step20_f24_predicate_construction_artifacts/step20_results_summary.md), [step21_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step21_f24_structural_predicates_artifacts/step21_results_summary.md).

4. F35 scale descent:
   Step 19 classifies the audited joint law as `renormalizes_on_toy`; the non-descending control fails.
   Source: [step19_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step19_f35_scale_descent_renormalization_artifacts/step19_results_summary.md).

5. F51 common-refinement unification:
   Step 22 verifies parent-to-child projection residuals `0.0`, strict-refinement witnesses to both children, and compatible descent statuses. Verdict: `unification_holds_on_carrier`.
   Source: [step22_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step22_f51_unification_common_refinement_artifacts/step22_results_summary.md).

## Durable Structural Constraints

- Union is not a lawful layer: the native exclusion is `G_nosmuggle`, not lack of strictness. Source: Step 17.
- A bridge currency must compress rather than staple: Step 13 builds `d_u=4<d_union=6`, with direct-sum rejected by compression. Source: [step13_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step13_build_rung2_neutral_currency_artifacts/step13_results_summary.md).
- Refinement must be a morphism of the two-access diagram. Source: [step14_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step14_rung1_on_currency_refinement_stability_artifacts/step14_results_summary.md).
- A single audit exists iff endpoint audits agree on shared modes; this recovers P3 as route-consistency on the overlap. Source: [step15_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step15_rung3_audit_on_currency_artifacts/step15_results_summary.md).

## Physical Toy Content

1. Derived audits:
   Step 24 derives `rho,j,T00,T0i` from the same field. Born and stress-energy do not form one shared audit: density proportional residual `0.5207123913178113`, transport proportional residual `0.9994686548331937`. The discovered relation is sourcing: direct `T[psi]` residual `0.0`.
   Source: [step24_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step24_derived_physical_audits_artifacts/step24_results_summary.md).

2. Co-sourcing:
   Step 25 builds `L` as a field carrier. The same `psi` sources `Born[psi]` and `T[psi]`; max residuals are `0.0`. The non-co-sourced control fails with max stress-energy residual `0.3806026603775931`.
   Source: [step25_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step25_sourcing_unification_artifacts/step25_results_summary.md).

3. Semiclassical dynamics:
   Step 26 gives the co-sourcing package finite self-sourced dynamics. The moderate coupling converges with fixed-point residual `3.4936318023019015e-16`; the over-strong control fails with fixed-point residual `1.4285712942487314`.
   Source: [step26_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step26_semiclassical_dynamics_artifacts/step26_results_summary.md).

4. Stationary relational time:
   Step 27 builds a finite clock-field constraint for the Step 26 stationary dynamic. The physical space is nonempty, with `||C Psi||=8.547035876629756e-16`, and clock conditioning recovers the stationary dynamic with max residual `9.79195701998934e-16`.
   Source: [step27_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step27_constraint_problem_of_time_artifacts/step27_results_summary.md).

5. Non-stationary relational time:
   Step 28 builds a non-eigenstate self-sourced history. The state and potential genuinely change; the generated relational constraint has `||C Psi||=4.220196766037856e-16`; the wrong-generator control fails with residual `0.0925307478333232`.
   Source: [step28_results_summary.md](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step28_nonstationary_relational_histories_artifacts/step28_results_summary.md).

## Honest Grade

Grade split:

- `native-law-verified`: the structural classifications applying repository framework laws and validators to finite carriers.
- `toy-diagnostic`: finite physical content using finite fields, finite clocks, chosen couplings, and can-fail controls.

The physical content recovers known structural patterns at toy fidelity: semiclassical sourcing and relational clock readout. It does not assert novel empirical predictions, a complete physical model, or a frame-transfer certificate.

Toy choices and adapted pieces:

- Step 23 uses chosen quadratic forms before Step 24 derives audits from a field.
- Step 26 uses a finite Hamiltonian and toy stress-energy density.
- Step 27 uses a compatible finite clock for the stationary history.
- Step 28 uses a history-adapted open-chain constraint after generating one self-sourced sequence.

## Independently Checkable Content

An external reviewer can rerun the validators and inspect the cited artifacts:

- Native gates and `G_nosmuggle`: Step 17.
- F37/F24/F35/F51 classifications: Steps 18, 19, 21, 22.
- Derived sourcing and co-sourcing: Steps 24, 25.
- Self-consistent dynamics: Step 26.
- Stationary and non-stationary relational constraints: Steps 27, 28.
- Claim-grade ledger: [content_classification_step29.csv](/home/repos/six-birds-papers/physics_atlas/thread_qm_gr/steps/step29_consolidated_statement_artifacts/content_classification_step29.csv).

## Open Obligations

- Build a less history-adapted nonlinear constraint and test it across broader history families.
- Enrich the QM-side content toward Hilbert observables, measurement records, and record stability.
- Enrich the GR-side content toward Lorentzian structure, redundancy under coordinate change, and constraint-algebra tests.
- Test robustness under different lattices, couplings, dimensions, and clock constructions.
- Perform the real physics frame-transfer review.

## Consolidated Verdict

Within the declared finite carriers and verified artifacts, `L` is a candidate common-refinement package: admissible, `BridgeMediatedRole`, scale-consistent, and F51-unifying on the toy. With finite physical content, `L` carries a field whose Born and stress-energy descents are co-sourced; it admits self-consistent semiclassical dynamics and stationary plus non-stationary relational clock-field representations. This is the construction product for external review.
