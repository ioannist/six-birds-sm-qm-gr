# Findings — Cluster B (E021 + E042)

(Manager-maintained pre-corpus holding area. Per-step findings appended below as the cascade proceeds.)

## Frame
- Atlas hint (E018/E021/E042 cards): the three are GR's upper-boundary foreclosures; W (the E018 common refinement) is the superset; L(E021)=W|vacuum-energy, L(E042)=W|high-curvature. Cluster B reuses the co-sourcing field-layer L.

## Step 1 - Shared-Substrate Frame

Status: finite-carrier frame established; deeper E042/E021 constructions remain open.

Constructed content:

- `L_ext=(d0,d1,d2,d3,d4_subplanck,d5_vacuum)` is built as a 12-state lifted carrier over the prior E018 8-state toy.
- E042 `d4_subplanck` is computed as a non-descending L-readout: GR smooth Sigma_f obstruction count `3`, q_QM obstruction count `11`, with witnesses `1-2;5-6;10-11`.
- E021 `d5_vacuum` is computed as a non-descending L-readout: GR smooth Sigma_f obstruction count `1`, q_QM obstruction count `3`, with witness `3-4`.
- The smooth GR shadow descends from L_ext with residual `0.0`.
- Controls pass: `d3` factors through GR smooth Sigma_f with obstruction count `0`; `d4_subplanck` factors through `d3` in the smooth regime with obstruction count `0`; `d4_subplanck` tears only at the high-curvature boundary with obstruction count `3`.
- Transparency: the non-descending `d4_subplanck` / `d5_vacuum` readouts are deliberately instantiated by branch splits in the toy carrier; the controls show the finite test discriminates, but do not certify physical frame transfer.

Finding: `step1_verdict = shared_substrate_frame_established`.

Nonclaim: Step 1 only frames the structural slots for E021 and E042 on a finite carrier. It does not compute a Lambda value, identify the physical singularity substrate, or certify frame transfer.

## Step 2 - E042 Boundary Construction

Status: finite-carrier E042 typed boundary built; physical substrate remains open.

Constructed content:

- The refinement sequence has `epsilon_n=2^-(n-1)` for `n=1..8`.
- GR's smooth curvature diagnostic `K_GR` grows from `0.81` to `13271.04`; its last increment is `9953.28`, so it is a non-stabilizing defect.
- L's resolved readout `R_L` approaches the finite toy limit `R*=0.75`; its last increment is `0.0001266479492186834`, so it stabilizes on the refinement.
- The no-resolution control `R_bad` grows from `0.9` to `115.2` and does not stabilize.
- The toy Planck threshold `K_P=16.0` is crossed at `n*=4`, `epsilon*=0.125`, with `K=51.84`.
- The continuation table has GR terminate at `epsilon=0`, while L remains finite at the locus and on post-locus rows.
- The high-curvature non-factorization signature is recomputed with obstruction count `3`, witnesses `1-2;5-6;10-11`.
- The smooth-regime guard passes: no spurious boundary activation, and smooth `d4` still factors through `d3`.

Finding: `step2_verdict = E042_boundary_layer_constructed_finite_toy`.

Nonclaim: Step 2 constructs the finite-carrier E042 shape: divergence-to-stabilization, staging, continuation, and boundary non-factorization. It does not identify the physical high-curvature substrate or certify frame transfer.

## Step 3 - E021 Vacuum Readout Construction

Status: finite-carrier E021 construction; firm/contested split recorded.

Constructed content:

- P5 currency: L carries `d5_vacuum` as an audited readout with selected toy `rho_IR=0.0010400000000000001`; GR status is `input_parameter_untracked_by_GR`.
- P6 ledger: the toy UV budget is `rho_UV=1040000000.0000001`; the modeled mismatch ratio is `1000000000000.0` with `log10=12.0`, explicitly marked `toy_modeled_not_real_120`.
- The unaudited cancellation row has counterterm `1039999999.9989601`, `tracked=False`, and `unaudited_cancellation=True`.
- The booked ledger tracks the remaining log mismatch as `12.0->8.0->4.0->0.0`; this is modeled/illustrative P6 bookkeeping, hand-specified rather than computed from a coarse map, RG flow, or package dynamics.
- P2 selection: the ensemble has five candidates and selects `vac_A_selected` by `minimum_selection_score`.
- Non-factorization: `UV_Sigma -> rho_Lambda_candidate` obstruction count is `4`, witnesses `0-1;0-2;1-2;3-4`; Step 1 `GR_smooth_Sigma_f -> d5_vacuum` obstruction count `1` is preserved.
- Controls pass: clean UV-to-Lambda descent fails; UV-determined coupling factors with obstruction count `0`; booked ledger is non-vacuous; toy ratio is marked as modeled.

Finding: `step3_verdict = E021_audited_vacuum_readout_constructed_finite_toy`.

Nonclaim: Firm content is the selected/run readout on the toy: non-factorization obstruction `4` with the descending-control contrast (obstruction `0`). The booked ledger is modeled/illustrative P6 bookkeeping, not a firm audit computed from a coarse map, RG flow, or package dynamics. The distinct audited-currency reading remains contested and casting-dependent. The toy supplies no Lambda value, no physical selection mechanism, and no frame-transfer certificate.

## Step 4 - Consolidated Cluster B Statement

Status: consolidation deliverable written; external review required.

Constructed content:

- `cluster_b_consolidated_statement.tex` assembles the Cluster B statement with explicit grades: frame-signature, finite-toy-diagnostic, modeled-shape, contested-reading, and organizational.
- `consolidated_findings_clusterb.md` summarizes the same findings in review prose.
- Step 1 frame is cited for d4/d5 non-descending signatures and smooth-shadow controls.
- Step 2 is cited for E042 P6 stabilization, Planck staging, assigned continuation, non-factorization, and controls.
- Step 3 is cited for E021 P5 currency, modeled P6 toy ledger, P2 selection, non-factorization, and controls.
- The unifying reading cites the QM-GR interpretation documents as precedent while remaining graded as modeled-shape.
- Nonclaim boundaries remain active: no Lambda value, no physical high-curvature substrate, no unconditional atlas closure, and no frame-transfer certificate.

Finding: `step4_verdict = cluster_b_deliverable_consolidated_for_external_review`.

Open obligations: external frame-transfer review; richer carriers; physical E042 substrate; physical E021 value and selection mechanism; review of the contested E021 distinct-currency reading.

## Step 5 - Honest Regrade

Status: accepted external-review regrade applied to Cluster B artifacts without new computation.

Regrade content:

- R1: E042 continuation is regraded as modeled-shape. The finite post-locus continuation is assigned by the toy, not derived from a constraint or evolution law.
- R2: E021 firm content is narrowed to selected/run non-factorization plus the descending-control contrast. The booked UV-to-IR ledger is modeled/illustrative P6 bookkeeping, not a firm audit computed from a coarse map, RG flow, or package dynamics.
- R4: the shared frame now states that the d4/d5 non-descending readouts are deliberately instantiated by branch splits; the controls show discrimination but not physical frame transfer.

Finding: `step5_verdict = honest_regrade_applied_validators_pass`.

Nonclaim: Step 5 is a transparency and grading correction only. It does not add computation, frame transfer, a Lambda value, or a physical high-curvature substrate.

## Step 6 - Shared-Frame Robustness

Status: finite-carrier R6 robustness test passed.

Constructed content:

- Readout battery: `5` general-linear and `3` nonlinear readouts of GR smooth Sigma `(d0,d2,d3)` were applied and factorization was recomputed.
- Representation-independence result: `d4_subplanck` stays non-descending with minimum obstruction `3`; `d5_vacuum` stays non-descending with minimum obstruction `1`.
- Genuine endpoint-internal enrichment using only `(d0,d1,d2,d3)` and nonlinear functions of those modes still does not make `d4` or `d5` definable: minimum obstructions remain `3` and `1`.
- Smuggling enrichment that adds `d4` or `d5` as endpoint content makes the corresponding target definable with obstruction `0`, and the audit flags those rows as using layer content.
- Positive-detection controls pass: `d3` factors through GR Sigma with obstruction `0`, and `d0*d2` factors through polynomial GR Sigma with obstruction `0`.

Finding: `step6_verdict = shared_frame_robustness_established`.

Nonclaim: Step 6 shows robustness under the declared finite-carrier readout/enrichment battery only. It is not a proof for continuous, Lorentzian, gauge, or diffeomorphism carriers and does not certify frame transfer.

## Step 7 - E042 Earned Continuation

Status: finite-toy E042 R1 conversion passed.

Constructed content:

- Lorentzian curvature toy: `K(r)=48*M^2/r^6` with `M=1.0`.
- `K_lorentzian` reaches max pre-locus finite value `3298534883328.0` and `inf` at the locus; pre-locus increments grow.
- L's resolved readout stabilizes to `R*=0.75`, with final listed `R_L=0.7499999997671694`.
- `U_good` computes finite post-locus states with recurrence `x_next=x-step*K/(K+K_planck)`; the final `U_good` output is `-0.7821121792445374`.
- GR's raw-curvature evolution terminates at or before the locus.
- `U_bad` inherits the raw divergent drive and fails to continue; this is the can-fail control.

Finding: `step7_verdict = E042_earned_continuation_constructed_finite_toy`.

Nonclaim: Step 7 converts the assigned-continuation weakness on the finite toy only. The Lorentzian metric and recurrence are toys, not a physical high-curvature substrate, not a diffeomorphism-invariant constraint algebra, and not a frame-transfer certificate.

## Step 8 - E021 RG/Measure Robustness

Status: finite-toy E021 R6 robustness test passed.

Constructed content:

- Structured toy: moduli grid `[-2,-1,0,1,2]`, deterministic beta-function RG flow for `g_IR`, and a measure score selecting `selected_phi_star`.
- `Lambda_from_bare_UV` has obstruction count `4`, witnesses `A_left-A_right;A_left-A_far_right;A_right-A_far_right;B_center-B_left`.
- `Lambda_from_UV_selected_phi` has obstruction count `0`.
- `phi_star_from_bare_UV` has obstruction count `4`, with the same witnesses as the Lambda bare-UV obstruction.
- RG-derived control: `g_IR_from_bare_UV` has obstruction count `0`.
- No-selection control: `no_selection_Lambda_from_bare_UV` has obstruction count `0`.

Finding: `step8_verdict = E021_rg_measure_robustness_established`.

Nonclaim: Step 8 is a finite RG/measure/moduli toy, not a real RG or landscape computation. It supplies no Lambda value, no physical selection mechanism, no new physics, and no frame-transfer certificate.

## Step 9 - R6 Robustness Consolidation

Status: R6 battery consolidated; no new computation.

Constructed content:

- `cluster_b_robustness_r6.tex` assembles the robustness section for the Cluster B v2 packet.
- `findings_r6_clusterb.md` provides the sourced prose synthesis.
- Step 6 is consolidated as shared-frame representation-independence: d4/d5 obstruction minima `3/1`, smuggling detected, positive controls factor.
- Step 7 is consolidated as E042 earned continuation: U_good post-locus output `-0.7821121792445374`, U_bad fails, GR terminates, Lorentzian toy K diverges and R_L stabilizes.
- Step 8 is consolidated as E021 selection relocation: Lambda bare-UV obstruction `4`, Lambda with selected phi obstruction `0`, phi_star bare-UV obstruction `4`, RG/no-selection controls obstruction `0`.

Finding: `step9_verdict = R6_robustness_battery_consolidated`.

Nonclaim: Step 9 consolidates only. The structural claims are robust under the declared finite battery, modeled forms remain bounded, and frame-transfer remains open.

## Step 10 - E021 Lambda-Selection Adjudication

Status: finite-toy Lambda-selection horn adjudication passed.

Constructed content:

- Carrier: a candidate Lambda grid derived from the Step 8 RG/measure vacua, with toy `Lambda_SM=0.0031662683693406`.
- Relaxation horn: the effective Lambda degeneracy sequence is `10->10->5->1->1->1`; it collapses to one candidate and is certified by the P6 decaying-degeneracy criterion.
- Broad anthropic landscape horn: the effective Lambda degeneracy sequence is `10->10->10->10->10->10`; it remains a multiply supported distribution and is not certified as the full closing mechanism on this finite toy.
- Sharp-measure control: the effective Lambda degeneracy sequence is `10->10->7->3->2->1`; it also collapses, proving the criterion is collapse-to-a-point rather than the label attached to a horn.
- Carrier guard: the construction is a Lambda candidate-space plus relaxation/measure audit, not a field-pair construction.

Finding: `step10_verdict = e021_lambda_selection_adjudication_constructed`.

Nonclaim: Step 10 adjudicates the selection type on the finite toy only. It supplies no Lambda value, no real selection mechanism, no physical rejection of anthropic reasoning, no new physics, and no frame-transfer certificate.

## Step 11 - E021 Adjudication Update

Status: targeted update/regrade applied; no new computation.

Updated content:

- `steps/step4_consolidated_statement_artifacts/cluster_b_consolidated_statement.tex` now contains Claim 10a, citing Step 10's E021 Lambda-selection adjudication.
- The deliverable now says the selection type is adjudicated: relaxation `10->10->5->1->1->1` and sharp measure `10->10->7->3->2->1` collapse and certify; broad anthropic landscape `10->10->10->10->10->10` stays distributed and is not certified.
- The update states collapse-not-label: a sharp measure passes because it collapses, while a broad landscape fails because it remains distributed.
- The open obligation is narrowed: the Lambda value and the real physical mechanism remain open; the selection type is no longer punted.
- A unified note connects E037, E043, and E021 under the same decaying-degeneracy criterion on the finite toys.

Finding: `step11_verdict = e021_adjudication_update_applied`.

Nonclaim: Step 11 is an update only. It does not determine Lambda, identify the real physical mechanism, reject anthropic reasoning as physics, add new computation, or certify frame transfer.
