# Findings — Cluster A (the shared SM selection/measure layer L*)

(Manager-maintained pre-corpus holding area. Per-step findings appended as the cascade proceeds.)

## Frame
- Atlas convergent hypothesis (E009/E019/E020/E037/E043 cards): the five "why THIS?" selection gaps are facets of ONE missing SELECTION/MEASURE layer L* above the SM (P2-dominant) that makes the SM free inputs a joint variable and selects the realized point. The single-layer coincidence is a STRONG but flagged hypothesis (non-load-bearing for the per-edge structural verdict).

## Step 1 - Shared Selection-Layer Frame
- Built the finite candidate-space+measure frame `L*`: 9 toy SM-structure worlds, with `w_SM` the computed argmax of `mu_score` (`106.0`).
- Modeled the SM's `Sigma_f` as a selection-forgetting shadow: it reads the realized inputs as fixed and carries no predicate over `W` and no measure over alternatives.
- Computed non-descending signatures from that SM shadow: joint structure obstruction `36`; E019 gauge/rep `21`; E020 generations/texture `21`; E043 EW-scale `14`; E009 UV-completion `14`; E037 vacuum `14`.
- Computed selection underdetermination: two different measures select the same realized world but differ away from it, obstruction `1`.
- Control teeth: a toy derived observable from the realized inputs factors with obstruction `0`, and `w_SM` is selected by the measure rather than hand-tagged.
- Honest grade: finite-carrier selection-layer shape only. The toy does not derive the gauge group, number of generations, Yukawa texture, electroweak scale, UV completion, or vacuum mechanism; the one-layer coincidence remains flagged for later stress tests.

## Step 2 - P2 Selection/Constraint
- Extended the Step-1 finite candidate space from 9 to 13 toy worlds by adding 4 anomalous `(G,R)` tokens.
- Computed a finite toy anomaly coefficient `A(G,R)` for every candidate. The constraint `A=0` pruned all 4 anomalous candidates and left 9 anomaly-free survivors.
- Verified anomaly-freedom is necessary but not sufficient on the toy: the survivor set has size `9`, and 8 anomaly-free survivors remain unselected.
- Applied the post-constraint selection rule: it collapses the survivor set to `w_SM` with selected score `116.0`.
- Computed E019/E020 joint co-determination: survivor support has 5 observed gauge-generation pairs out of 9 Cartesian possibilities, 4 missing pairs, and mutual information `0.330856` bits; the selected pair is `G_SM|3`.
- Control teeth passed: anomalous candidates are removed, anomaly-free candidates survive, selection collapses a >1 survivor set, and there is a further-step witness.
- Honest grade: finite toy P2 selection mechanics. The anomaly functional and selector are stand-ins for the selection-layer shape, not physical anomaly coefficients or an actual SM-selection mechanism.

## Step 3 - P6 Decaying-Degeneracy Audit
- Built the P6 audit over the Step-2 anomaly-free survivors, with degeneracy defined as the number of candidates still in play at refinement level `n`.
- Genuine selection refinement decays monotonically: `9 -> 5 -> 4 -> 2 -> 1 -> 1`.
- The final selected survivor is `w_SM`; the final increment is `0`, so the sequence stabilizes at the selected point.
- Unselected landscape control stays multiply degenerate: `9 -> 9 -> 9 -> 9 -> 9 -> 9`.
- Control teeth passed: decays-vs-not, monotone non-increase, landing on `w_SM`, and landscape not secretly selecting.
- Honest grade: finite toy P6 degeneracy-audit shape. The refinement predicates and degeneracy ledger are stand-ins for the selection-layer audit, not a real measure or physical vacuum mechanism.

## Step 4 - E043 Scale-Selection Facet
- Built a finite EW scale toy with `r = m_H2/M_cutoff2` and realized target `r_SM = 0.0001`.
- Computed that `r` is non-descending from the EW `Sigma_f`: same broken-phase EW readout with different cutoff gives obstruction `3`.
- Control teeth: a derived EW observable factors through EW `Sigma_f` with obstruction `0`.
- Derivation horn: an attractor-style recurrence reaches `r_SM` with final residual `6.64073830647e-19`.
- Measure horn: a peaked toy measure uniquely selects `r = 0.0001`.
- No-selection control: no-attractor final residual remains `0.0199`, and a flat measure has selected count `0`; the ratio remains unfixed without a horn.
- Honest grade: finite toy scale-selection shape. The scale values, recurrence, and measure are stand-ins for the slot structure; the result does not provide a physical Higgs-mass value, real cutoff mechanism, or horn choice.

## Step 5 - E009 UV-Fiber Facet
- Built a finite UV-fiber toy where the realized IR code `IR_SM_TOY` has 6 UV candidates with distinct UV content.
- Computed UV-content non-descending from the IR readout: obstruction `16`.
- Control teeth: a derived IR observable factors through `IR_EFT_code` with obstruction `0`.
- Computed a toy consistency functional over unitarity/causality/positivity/anomaly stand-ins. It prunes `U_bad_unitarity`, `U_bad_positivity`, `U_bad_anomaly`, and `U_alt_IR_A_bad`, while consistent UV candidates survive.
- In the realized IR fiber, the consistency constraint leaves 3 admissible UV candidates before selection: `U_SM`, `U_alt_GUT`, and `U_alt_stringy`.
- The selector collapses the admissible realized fiber to `U_SM`; 2 admissible UV candidates remain non-selected.
- P4 staging is recorded for every UV row as a finite UV-to-threshold-to-IR down-shadow string.
- Honest grade: finite toy UV-fiber selection shape. The UV theories, consistency checks, and staging strings are stand-ins; the result does not provide a physical UV completion or real consistency criterion.

## Step 6 - E043 Horn Adjudication
- Ran the E043 horns through the P6 decaying-degeneracy criterion from Step 3.
- Derivation horn: degeneracy collapses `6 -> 5 -> 4 -> 2 -> 1 -> 1`; certified by P6.
- Broad anthropic measure: degeneracy remains `6 -> 6 -> 6 -> 6 -> 6 -> 6`; fails as a non-closing landscape.
- Sharp selecting measure control: degeneracy collapses `3 -> 2 -> 2 -> 1 -> 1`; certified by P6.
- The criterion is collapse-to-point, not the horn label: sharp measure passes because it collapses, broad measure fails because it stays a distribution.
- Honest grade: finite toy horn adjudication. The scale grid and effective-support counts are stand-ins for the framework criterion, not a physical mass mechanism or real landscape measure.

## Step 7 - Consolidated SM Selection-Layer Statement
- Consolidated Steps 1-6 into `cluster_a_consolidated_statement.tex` and `consolidated_findings_clustera.md`.
- Deliverable claim: one finite candidate-space+measure selection layer `L*` with five facets: E019 gauge/rep, E020 generations/texture, E037 vacuum-selection degeneracy, E043 scale ratio, and E009 UV-completion fiber.
- Step 1 frame carried forward: joint obstruction `36`; facet obstructions E019 `21`, E020 `21`, E043 `14`, E009 `14`, E037 `14`; selection-underdetermination `1`; derived-observable control obstruction `0`.
- Step 2 P2 carried forward: anomaly pruning removes `4` anomalous candidates, leaves `9` anomaly-free survivors, and selection collapses to `w_SM`; gauge-generation mutual information `0.330856` bits.
- Step 3 P6 carried forward: genuine selection `9 -> 5 -> 4 -> 2 -> 1 -> 1`; landscape control `9 -> 9 -> 9 -> 9 -> 9 -> 9`.
- Step 4/6 E043 carried forward: scale-ratio obstruction `3`; derivation horn `6 -> 5 -> 4 -> 2 -> 1 -> 1` certifies; broad measure `6 -> 6 -> 6 -> 6 -> 6 -> 6` fails; sharp measure `3 -> 2 -> 2 -> 1 -> 1` certifies.
- Step 5 E009 carried forward: realized IR fiber has `6` UV candidates; consistency leaves `3`; selection collapses to `U_SM`.
- Unified result: the decaying-degeneracy criterion adjudicates selection type consistently across E037/E043 and the E021 parallel in Cluster B Step 10. Collapse-to-point certifies; broad landscape behavior remains unclosed.
- Honest grade: consolidation only, no new computation. Shape not values; no physical SM value or mechanism is derived; the single-layer coincidence remains a flagged hypothesis; frame transfer remains open.

## Step 14 - Real Anomaly Enrichment
- Replaced the prior toy anomaly score with exact rational anomaly coefficients over a finite curated set of `10` real chiral-content candidates.
- Computed coefficients for the one-generation SM chiral content: `[SU(3)]^3=0`, `[SU(3)]^2U(1)=0`, `[SU(2)]^2U(1)=0`, `U(1)^3=0`, `U(1)-grav=0`, `SU(5)-style cubic=0`, and `su2_witten_even=True`.
- Solved the fixed-representation anomaly equations to the known relation family: `Y_L=-3Y_Q`, `Y_e_c=6Y_Q`, `{Y_u_c,Y_d_c}={-4Y_Q,2Y_Q}`. With the usual up/down labeling and `Y_Q=1/6`, this recovers `Q_proton=-Q_e`.
- Necessary-not-sufficient shape survives the real anomaly enrichment: `7` anomaly-free survivors, `6` of them non-reference survivors (`SM_plus_vectorlike_lepton`, `SM_plus_vectorlike_down`, `SM_plus_sterile_neutrino`, `hypercharge_label_swapped`, `scaled_hypercharge_x2`, `SU5_10_plus_5bar_decomposition`).
- Scoped next consequence: `minimal irreducible anomaly-cancellation support`, to be checked by broader real-rep enumeration, vector-like-pair removal, and minimal-support comparison.
- Law-landing obligations advanced: faithful enrichment, closed-form relation, and limit recovery are computed; the independently-checkable consequence is scoped for Step 15.
- Honest grade: finite curated candidate-space enrichment and known-physics calibration. It supplies no physical SM value or real selection mechanism, and frame transfer remains open.

## Step 15 - Minimal Anomaly-Support Test
- Enumerated a bounded fixed-gauge spectrum space over `66` SU(3)xSU(2)xU(1) multiplet types and `9705619` raw supports with up to `5` distinct Weyl multiplet types.
- Exact anomaly filtering leaves `1161` raw anomaly-free supports.
- Quotienting vector-like pairs, neutral singlets, and overall hypercharge normalization leaves `28` irreducible anomaly-free chiral supports.
- Declared minimality measure: irreducible chiral multiplet count, tie-broken by total Weyl component count.
- The one-generation SM support is present and anomaly-free, but it is not selected by this measure: SM score `5` multiplets / `15` Weyl components, rank `28` of `28`; the minimum score is `4` / `12`.
- Can-fail control passes: there are `27` non-SM irreducible anomaly-free competitors at or below the SM score, so the enumeration genuinely contained alternatives.
- Verdict: `honest_no_go_minimality_insufficient`. Minimality alone does not single out the SM chiral content on this bounded carrier; the next door is an additional principle such as electroweak quark-lepton participation or an observed-charge sector condition.
- Law-landing obligation 2 is advanced as a typed no-go rather than a candidate-law close. The result is conditional on the fixed gauge group and finite bounded enumeration, and frame transfer remains open.

## Step 16 - Content-Selection Principle Screen
- Reused the `28` irreducible anomaly-free chiral supports from Step 15 and tested a declared token-blind structural principle set over them.
- Per-principle survivor counts: faithfulness `16`; sector diversity `4`; weak doublet/singlet mixing `4`; charge integrality `26`; residual chiral complexity `28`; simple-group embedding pattern `2`; minimality control `12`.
- The reference support satisfies every structural principle except the carried minimality control. The minimality control is the required can-fail witness: it does not select the reference support.
- All non-control non-circular conjunctions were computed. The strongest reference-preserving conjunction is `charge_integrality+simple_group_embedding_pattern`, and it leaves `2` supports.
- No credited non-circular principle or conjunction uniquely selects the reference support. Choosing between the two strongest survivors requires an additional orientation/content input or a new independent structural principle not present in the declared set.
- Verdict: `rigorous_type_limit_negative`. The content-selection question closes, within this finite fixed-gauge test, as a bounded negative rather than a candidate selection law.
- Law-landing obligation 2 status: `advanced_as_type_limit_negative`. The independent consequence was attempted and returned a precise boundary.

## Step 17 - Two-Layer Selection Architecture Test
- Built a light E043 scale carrier with `r=m_H^2/M_cutoff^2`, quadratic cutoff sensitivity, continuous tuning cost, and a relaxation trajectory. This is structural enrichment only.
- Carrier-disjointness holds: content variables are `gauge_code`, `rep_code`, `n_gen`, `texture_code`, `uv_code`, and `vacuum_code`; scale variables are `scale_ratio`, `cutoff_sensitivity`, `naturalness_cost`, `relaxation_state`, and `landscape_state`.
- Measure-kind distinction holds: content uses discrete anomaly/structural constraints, while scale uses continuous tuning cost plus relaxation.
- Coupling numbers: scale-vs-content product MI `0.000000000000` bits; inherited Step-8 EW-vs-content residual `0.035998916880` bits.
- Can-fail control: the same information measure detects the known gauge-generation coupling, `MI=0.466203233486` bits, above the declared control threshold.
- Verdict: `two_selection_layers`. The finite toy supports a content/anomaly-selection layer plus a separate scale/naturalness-selection layer.
- Framing revision: the old single-layer `L*` shorthand is narrowed. Cluster A remains P2 selection/measure architecture, but the toy evidence supports two P2 selection layers rather than one monolithic layer.
- Honest grade: toy-structural architecture only. The hierarchy remains open, no physical scale value or mechanism is supplied, and frame transfer remains open.

## Step 18 - Two-Layer Stress Test
- Added an adversarial content-dependent radiative channel to the E043 scale facet: a dominant fermion proxy plus subdominant gauge/representation terms drives the scale naturalness bin.
- The active channel raises content-scale coupling from the Step-17 inherited residual `0.035998916880` bits to `0.391243563629` bits.
- Gauge-generation reference remains `0.466203233486` bits, so the active channel is non-negligible but below the known content-coupling control.
- Coupling-strength can-fail passes: MI is `0` with the channel off, `0.391243563629` bits at active strength, and `0.974342959327` bits under stronger injected coupling. The measure responds and can break the split.
- Robustness sweep: `36` cells over thresholds, estimators, and groupings; `12` classify as two-layer and `24` as coupled-but-distinct; active-strength one-layer-break fraction is `0`.
- Verdict: `coupled_but_distinct`. The clean Step-17 two-layer independence claim is not robust once the radiative channel is included.
- Architecture revision: the scale facet is coupled to content through radiative sensitivity, but remains a distinct kind of selection problem because its measure is naturalness/tuning rather than anomaly/content consistency.
- Honest grade: toy-structural stress test. The hierarchy remains open; no physical Higgs-scale value, dominant Yukawa value, or real mechanism is supplied; frame transfer remains open.

## Step 19 - F24/F47 Layer Multiplicity
- Re-grounded the architecture question in the exact F24/F47 test.
- Defined `q` as the content-selection access quotient over content coordinates and content checks, excluding the EW scale coordinate.
- Defined `s` as the F47 scale/naturalness readout from the scale ratio and radiative sensitivity.
- Computed the exact role obstruction: `|O_s| = 5760` unordered q-fiber pairs. Therefore `s` does not descend through `q`; the result is `RoleSplit`.
- Can-fail controls pass: known-descending role obstruction `0`; known-splitting role obstruction `8640`.
- F24 classification: `BudgetedRole` is the only firing family. `MemoryLayer` is ruled out because no independently closed scale-only access quotient forms; the scale role is priced as a naturalness budget on the same closure.
- F47 selector region: `mu_total=8640`, `mu(Sigma)=342`, fraction `0.039583333333`, `theta=0.05`, `Small=true`, `Realized=true`.
- Structural-dependency note: Step-18 MI is not treated as a top-down cause claim; no TDGate intervention/control/effect-threshold audit was run.
- Verdict: `RoleSplit -> BudgetedRole`, with F47 small-selector-region fine-tuning. This is one closure with a budgeted scale role, not an independent closed scale layer.

## Step 20 - GUT Recognition Value-Relations
- Took the Mode A / E2 recognition route: imported SU(5) `10 + 5bar` embedding as the named external principle motivated by the closure's GUT-embeddability filter.
- Trace computation over one generation gives `Tr(Y^2)=10/3`, `Tr(T3^2)=2`, hypercharge normalization `5/3`, and `sin^2(theta_W)=0.375=3/8` at the recognition scale.
- Recognition value-relations recorded: `g1=g2=g3` with `g1=sqrt(5/3)gY`, and minimal SU(5) `m_b=m_tau` at `M_GUT`.
- One-loop non-SUSY SM RG test is a near-miss/failure: pair crossing log10 scales `13.013559`, `14.393117`, `17.008278`; best-fit log10 scale `14.212640`; inverse-coupling spread `3.927293`; `clean_unification=false`.
- Best-fit SM-running weak-angle comparison: `sin^2(theta_W)(M_Z)=0.214358251521` versus measured `0.231220000000`, difference `-0.016861748479`.
- SUSY coefficient comparison: best-fit log10 scale `16.333716`, inverse-coupling spread `0.069699`, much tighter than the non-SUSY coefficient result.
- Honest grade: value-relations via E2 recognition import, recovering known GUT physics. Absolute values remain residual; this is not an SBT-alone value derivation and frame transfer remains open.

> **⚠ SUPERSEDED — Steps 21-26 are demoted.** The "generated SM gauge shape" arc (Steps 21-26) carried a hidden
> `total_slots=5` + exterior-algebra (GUT) prior (v3 review + Step-28 confirmation). Corrected grade: **finite
> GUT/exterior recognition recovery, NOT neutral generation**; Step 27 normalization is convention-relative. The
> honest, un-smuggled result is the neutral hunt (Steps 28-39) + Step 41. See per-step `SUPERSEDED.md`.

## Step 21 - Mode-B Unifying Carrier
- Corrected the Step-20 shortcut by building a finite Mode-B generation kernel rather than importing the recognition structure as a primitive.
- Carrier signature: five operational slots split by the SM-sector lens `q`, bridge operators forgotten by `q`, a primitive trace-neutral integer generator, trace metric, and dual/pair rewrites.
- `U` is non-descending through `q`: `U_a` and `U_b` share `q=color3|weak2|trace0` but differ in bridge readout, obstruction count `1`.
- `C(U)` descends through `q`: the same witness pair has identical audited expression, obstruction count `0`.
- Generated weights and charge grid: color weight `-2`, weak weight `3`, charge unit `1/6`.
- Generated trace audit: `Tr(charge^2)=5/6`, `Tr(T3^2)=1/2`, normalization ratio `5/3`, and weak-mixing relation `3/8`.
- Recognition landing: the generated relation matches the SU(5)-shaped value after the audit; it was not a carrier primitive.
- Stage II earning: generated dual/pair rewrite content has zero mixed color-charge, mixed weak-charge, cubic-charge, and charge-gravity anomaly sums.
- Six no-smuggling gates pass: primitive exclusion, dependency trace, ablation, negative controls, Stage II earning, and no-single-axiom-equivalence.
- Negative controls reject two nearby false ratios (`28/15`, `3/2`) and a non-grid charge (`13/42`).
- Verdict: `PASS-with-recognition` on the finite kernel. This is generated finite-carrier evidence, not physical unification closure; the Step-20 non-SUSY one-loop near-miss remains binding.

> **⚠ SUPERSEDED — read before citing Steps 21-26 below.** The "GENERATED SM gauge shape" framing in Steps
> 21-26 (incl. the `GENERATED` verdicts in Steps 22-23) is **superseded** by the v3 external review and the
> Step-28 confirmation: Steps 22-26 carried a hidden **`total_slots=5` + exterior-algebra (GUT) prior**, so the
> `2|3` shape was **forced by the prior, not neutrally generated**. Corrected grade for Steps 22-26: **finite
> GUT/exterior recognition recovery**, NOT generation. The honest, un-smuggled result is the *separate* neutral
> hunt in Steps 28-39 (conditional shadow-uniqueness via the **introduced** clean-separation condition; see the
> per-step `SUPERSEDED.md`, `manager_log.md` STEP 28-42, `TODO.md`, and `clean_separation_corpus_findings.md`).

## Step 22 - Mode-B Group-Shape Generation
- Went below Step 21 by enumerating the gauge-sector shape rather than using the `3+2` slot split as a primitive.
- Inputs are explicit and bounded: non-abelian factor count `0..3`, factor ranks `1..4`, one abelian charge role, chirality requirement, anomaly/charge-grid closure tests, and minimality by total rank, total slots, then factor count.
- Enumeration size: `35` candidate sector structures.
- Closing structures: `1`.
- Minimal generated closure: `structure_id=r1|2`, ranks `1|2`, dimensions `2|3`, total rank `3`, total slots `5`, primitive weights `-3|2`.
- The generated dimensions `2|3` recognition-land on the SM gauge-sector shape `SU(3) x SU(2) x U(1)` up to factor order, after the audit.
- Negative controls pass: `abelian_only`, `real_rep_only`, and `single_complex_factor` do not close.
- Stage II checks pass: no structure without a complex representation closes, and single-factor structures do not close because the neutral charge grid is trivial or underdetermined in this grammar.
- Six no-smuggling gates pass, including primitive exclusion: the build script contains no target group literals or standalone `2`/`3` constants.
- Verdict: `GENERATED` within the finite grammar. This is not physical E019 closure; it names a next stress gate over richer factor ranges, representation families, and closure measures.

## Step 23 - Factor-Count Unsmuggling
- Audited and fixed the Step-22 smuggle: Step 22's neutral-weight solver refused all non-two-factor structures, so the two-factor result had been structurally forced.
- Replaced that solver with a general trace-zero charge lattice over factor counts `0..4`; every candidate now receives a computed charge-vector search and anomaly/closure verdict.
- Enumeration size: `70` structures.
- Per-factor-count closure results:
  - `n=0`: `1` candidate, `0` close.
  - `n=1`: `4` candidates, `0` close.
  - `n=2`: `10` candidates, `1` closes.
  - `n=3`: `20` candidates, `0` close.
  - `n=4`: `35` candidates, `0` close.
- Unique minimal generated closure: factor count `2`, ranks `1|2`, dimensions `2|3`, total rank `3`, total slots `5`, selected charge vector `3|-2`.
- Strengthened structural-smuggle gate passes: the validator scans the closure-function region for factor-count/rank short-circuit patterns and `return None`; none are present.
- Literal primitive exclusion still passes: no target group literals and no standalone `2`/`3` constants appear in the build script.
- Negative controls pass by computed verdict: `abelian_only`, `real_rep_only`, and `single_complex_factor` do not close.
- Stage II passes: no structure without complex representations closes, and all `70` candidates have computed verdicts.
- Verdict: `GENERATED` after unsmuggling. Factor count `2` genuinely emerges within this generalized finite grammar, but this remains finite grammar generation, not physical E019 closure; the cascade continues through richer representation families, wider charge searches, and alternate closure measures.

## Step 24 - Robustness Stress of Group-Shape Generation
- Stress-tested Step 23 against wider range, criteria variation, and known chiral alternatives.
- Inputs widened to factor count `0..6`, ranks `1..6`, U(1)-role count `0..3`, with known alternatives inserted as can-fail competitors.
- Total candidates including known alternatives: `3699`.
- Total closers: `4`.
- Wider factor-count closure table:
  - `n=0`: `4` candidates, `0` close.
  - `n=1`: `27` candidates, `3` close: `SU(5)`, `SO(10)`, `SU(6)_chiral_example`.
  - `n=2`: `84` candidates, `1` closes: `r1|2_u1`.
  - `n=3`: `224` candidates, `0` close.
  - `n=4`: `504` candidates, `0` close.
  - `n=5`: `1008` candidates, `0` close.
  - `n=6`: `1848` candidates, `0` close.
- Primary total-rank-first winner remains `r1|2_u1` with dimensions `2|3`, factor count `2`, U(1)-role count `1`.
- Known alternatives can-fail passes: `SU(5)`, `SO(10)`, and `SU(6)_chiral_example` are admitted with computed anomaly `0` and non-minimal reasons, not silently excluded.
- Criteria variation: `8/9` settings preserve the split-sector `2|3` winner; `factor_count_first` flips to `SU(5)`.
- Negative controls pass by computed verdict.
- Verdict: `FRAGILE` typed no-go for parameter-independent uniqueness. Step 23 survives primary ordering but is criteria-dependent once known alternatives are admitted.
- Next grammar delta: add a principled discriminator between low-rank split-sector closure and one-factor simple unification economy.

## Step 25 - F51 Descent Hierarchy
- Walked the Step-24 next grammar delta by testing whether the one-factor closers are finite F51 parent-shadow structures for the split-sector closer.
- Child closer reused from Step 24: `r1|2_u1`, dimensions `2|3`, charge vector `3|-2`.
- Computed per-parent descent:
  - `SU(5)`: generic partition dual/pair rewrite gives charged obstruction `0` and full obstruction `0`; verdict `PASS_EXACT_PARENT_SHADOW`.
  - `SO(10)`: generic even-envelope rewrite gives charged obstruction `0` and full obstruction `1` because of one neutral residual; verdict `PASS_SCOPED_NEUTRAL_RESIDUAL`.
  - `SU(6)_chiral_example`: no parent-quotient rewrite in the declared grammar, charged/full obstruction `5/5`; verdict `FAIL_NOT_PARENT`.
- Negative control passes: the non-parent one-factor closer fails by computed obstruction rather than by silent exclusion.
- Stage II passes: generated branch roles reproduce charge-gravity and cubic-charge balance, both zero.
- Six gates pass: primitive exclusion, dependency trace, ablation, negative control, Stage II, and no-single-axiom equivalence.
- Verdict: `HIERARCHY_SCOPED`. The Step-24 fork is refined into a finite parent-shadow hierarchy, exact for `SU(5)` and charged-content scoped for `SO(10)`. This is finite-grammar structure only, not a theorem of physical unification or frame-transfer status upgrade.

## Step 26 - Integrated Normalization on the Generated Closer
- Removed the Step-21 hardcoded-shape partial by computing the trace normalization directly on the Step-23 generated minimal closer.
- Generated-vs-input breakdown: Step 26 reads `r1|2` from Step 23 (`ranks=1|2`, `dimensions=2|3`, `selected_charge_vector=3|-2`) and supplies the trace-zero balance plus dimension-weighted trace rule.
- Computed normalization on the generated structure:
  - charge unit `1/6`
  - `Tr(Y^2)=5/6`
  - `Tr(T3^2)=1/2`
  - normalization ratio `5/3`
  - `sin^2(theta_W)=3/8`
- Negative controls pass:
  - `r1|3` computes a different relation, `8/11`;
  - `r1|1` fails because the rank-one readout is not unique;
  - `rnone` fails because dimensions/charge data are absent.
- Stage II passes: charge quantization is reproduced on the generated structure with integer role charge weights `-3|2|6|1|-4`.
- Six gates pass: primitive exclusion, dependency trace, ablation, negative controls, Stage II, and no-single-axiom equivalence.
- Verdict (as recorded at Step 26): `INTEGRATED`. **[SUPERSEDED + CORRECTED — see Steps 28-40 and external review R1-R7]** The "un-smuggled construction" claim here is WRONG: the Step-23 gauge shape carried a `total_slots=5` + exterior-algebra (GUT) prior (external review R1-R2; confirmed by construction Step 28). Corrected grade for Steps 23-26: **finite GUT-exterior closure audit / recognition recovery**, NOT neutral generation. The normalization (3/8) is convention-relative recovery (Step 27), NOT part of any landing (R7). The honest, un-smuggled result is the scrutinized hunt (Steps 28-39): qualified shadow-uniqueness of the SM gauge structure resting on the introduced clean-separation condition. **[Step 63 update: `sin²θ_W=3/8` was later RE-established via a DIFFERENT, non-circular route — the embedding trace-ratio `Tr(T3²)/Tr(Q²)=2/(16/3)=3/8` computed from the SM charge pattern, conditional on a declared minimal-simple common-refinement source (a product control gives 3/23, so the source does real work) = a GROUND-conditional landing of the EMBEDDING ratio (NOT the measured low-energy value, which needs RG running = E0/experiment). This is distinct from, and supersedes the status of, the demoted Step-26/27 convention-recovery above. See `MAIN_RESULTS.md` J4 / `LANDED_vs_NOT.md` / `SM_TRACK_CLOSEOUT_QUESTIONS.md` §9.]**

## Step 27 - Normalization Robustness Stress
- Led with the deflationary truth: Step 26's `3/8` is a toy sector-trace result, not a physical chiral-fermion-multiplet trace.
- Ran six trace/readout conventions on the same Step-23 generated structure:
  - `product_charge__rank_one_t3`: `3/8` (matches).
  - `lattice_lcm_charge__rank_one_t3`: `3/8` (matches).
  - `total_slots_charge__rank_one_t3`: `5/17` (flips).
  - `integer_weight_charge__rank_one_t3`: `1/61` (flips).
  - `product_charge__alternate_t3`: `9/19` (flips).
  - `product_charge__all_factor_t3`: `3/5` (flips).
- Residual-smuggle hunt result: charge-unit denominator and rank-one readout selection are load-bearing convention choices. No hidden all-structure forcing was found: non-generated controls never reproduce the Step-21 target across the convention family.
- F51 consequence consistency survives on the same structure: Step-25 `SU(5)` exact parent-shadow obstruction `0/0`; Step-25 `SO(10)` scoped parent obstruction `0/1`.
- Negative controls pass; Stage II charge quantization persists; all six gates pass.
- Verdict: `FRAGILE_CONVENTION_DEPENDENT`. The gauge-shape/F51 hierarchy remains, but the toy-trace normalization is not convention-independent. Next grammar delta: replace the toy sector trace with a physical chiral-multiplet trace or add a principled trace-convention selector.

## Step 28 - Neutral Representation De-Smuggling
- Led with the deflationary truth from the external review: Steps 23-26 carried a slot-count-five lock and an exterior-content prior, so the earlier gauge-shape landing is demoted to a finite GUT-exterior closure audit / recognition recovery.
- Removed both priors in the Step 28 build: no slot-count equality guard, and the representation alphabet is neutral over `singlet`, `fund`, `antifund`, `antisym2`, `sym2`, and `adjoint`.
- Computed neutral anomaly-free chiral closers in the declared window: `280983` across `9` structures.
- Per-structure closer counts: `2`: `5400`; `3`: `85`; `4`: `56`; `2|2`: `242328`; `2|3`: `23076`; `2|4`: `9482`; `3|3`: `170`; `3|4`: `226`; `4|4`: `160`.
- The Step-14 reference support is present once in the neutral window, but it is not minimal and is not uniquely distinguished without the removed prior.
- Anti-smuggle gates pass: no slot-count equality guard in the build, neutral representation set present, cubic anomaly rows self-check as sums over `A(R)`, and Stage II calibration passes.
- Verdict: `CONFIRM_SMUGGLE`. Neutral anomaly closure plus the declared minimality criterion does not generate a distinguished SM-reference support in this finite window.
- Next grammar delta: add a neutral discriminator beyond anomaly-freedom/minimality, or explicitly treat the exterior/GUT structure as a Mode-A recognition prior rather than a neutral Mode-B output.

## Step 29 - Neutral Intrinsic Closure Discriminator Hunt
- Reframed Step 28 as the P2-only closer space, not as terminal: the next test is an intrinsic closure principle drawn from the framework primitives.
- Designed and computed `atomic_rewrite_packaging`: P5 atomic package, P1 no spectator action, and F27 primitive charge orbit.
- Carrier: `280983` neutral P2 closers from Step 28.
- Predicate survivors: `1851`.
- Component counts: atomic package `4293`; no-spectator action `258819`; primitive charge orbit `136323`.
- The Step-14 reference support passes the predicate exactly once, but is not uniquely distinguished.
- Per-structure predicate survivors: `2`: `6`; `3`: `49`; `4`: `20`; `2|2`: `1454`; `2|3`: `304`; `2|4`: `18`; `3|3`, `3|4`, `4|4`: `0`.
- Ablations pass: removing atomic package leaves `124751`, removing no-spectator action leaves `2151`, and removing primitive charge orbit leaves `3705`, so every component is load-bearing.
- Negative controls and Stage II pass: the predicate is not a row picker, many P2 closers fail it, reducible packages are detected, and the reference support survives.
- Verdict: `NARROW`. This is genuine intrinsic progress, not a unique landing.
- Next grammar delta: conjoin the next neutral intrinsic predicate, most likely a budgeted closure currency or F24/F47 role-obstruction audit on the atomic rewrite packages.

## Step 30 - Conjoined Intrinsic Discriminator
- Reproduced the Step-29 atomic rewrite-packaging survivor count: `1851`.
- Added the second neutral intrinsic predicate: `strict_closure_currency_minimum`, a C1/C4 audit shadow-price tuple `(active audit axes, L1 shadow price, nonzero audit terms, charge span)`.
- The predicate is intrinsic to each support's audit-vector cancellation work and is not a multiplet-count criterion.
- Strict minimum currency: `2|4|4|2`.
- Conjoined survivors: `4`, all non-reference.
- The Step-14 reference support passes Step 29 but has currency `6|546|20|10`, so it fails the strict currency minimum.
- Ablations pass: without atomic package the minimum pool has `1414`; without no-spectator action it has `12`; without primitive charge orbit it changes identity and exposes zero-currency neutral packages.
- Negative controls and Stage II pass: currency is not a target row picker, excludes `1847` Step-29 survivors, reproduces the Step-29 count, and exposes the zero-price degeneracy when primitive charge orbit is removed.
- Verdict: `TYPED_NO_GO`. Strict closure-currency minimum over-rewards tiny low-price packages and excludes the reference support.
- Next grammar delta: try F24/F47 role-obstruction or P3 protocol-holonomy on the Step-29 atomic packages.

## Step 31 - Consistency/Completeness Discriminator
- Reproduced the Step-29 atomic rewrite-packaging survivor count: `1851`.
- Dropped the Step-30 strict closure-currency minimum to diagnostic-only because it excludes the reference support.
- Added the next neutral intrinsic predicate: `closure_consistency_completeness`, a P3/P6 action-faithful route-incidence completeness test.
- Predicate definition: every activated factor must have an actual action-bearing route, bridge routes must close where multiple factors are active, and at most one audit-only route may remain.
- The rank-one global chirality check is retained as a Stage II diagnostic, not as the selector.
- Conjoined survivors: `513`.
- The Step-14 reference support passes the conjoined predicate but is not uniquely distinguished.
- Per-structure conjoined counts: `2`: `4`; `3`: `49`; `4`: `16`; `2|2`: `384`; `2|3`: `60`; `2|4`: `0`.
- Ablations pass: without `atomic_rewrite_packaging`, the route-complete P2 pool has `27101`; without `closure_consistency_completeness`, the pool returns to `1851`.
- Negative controls and Stage II pass: the predicate is not a target row picker, fails `1338` Step-29 survivors, reproduces the Step-29 count, and detects zero-action labels plus rank-one conjugacy artifacts.
- Verdict: `NARROW`. The consistency predicate supplies real finite-carrier progress but does not land a unique discriminator.
- Next grammar delta: add a stronger P6 audit-completeness ledger or an F24 role-obstruction selector over the consistency-complete atomic packages.

## Step 32 - Chirality-Faithful Intrinsic Discriminator
- Reproduced the Step-31 consistency-complete atomic survivor count: `513`.
- Added the next neutral intrinsic predicate: `chirality_faithfulness`, a P3 action predicate requiring residual chirality to be carried by a genuinely complex non-abelian action channel after vectorlike cancellation.
- The predicate is defined by residual conjugacy and nonzero cubic action entries inside each candidate support; it is not a minimality rule and does not use target dimensions or content.
- Conjoined survivors: `399`.
- Rejected Step-31 survivors: `114`.
- The Step-14 reference support passes the conjoined predicate but is not uniquely distinguished.
- Per-structure conjoined counts: `2`: `2`; `2|2`: `272`; `2|3`: `60`; `3`: `49`; `4`: `16`; `2|4`: `0`.
- Dominance test: the dominant structure remains `2|2`, reduced from `384` to `272`; the target structure remains at `60`.
- Ablations pass: without `atomic_rewrite_packaging`, the pool has `8955`; without `closure_consistency_completeness`, it has `1421`; without `chirality_faithfulness`, it returns to `513`.
- Negative controls and Stage II pass: the predicate is not a target row picker, fails some Step-31 survivors, computes the dominance test, reproduces the Step-31 count, and detects both pass and fail channels.
- Verdict: `NARROW`. Chirality-faithfulness supplies finite-carrier progress but does not break the 2|2 dominance or land a unique discriminator.
- Next grammar delta: conjoin an F24 role-obstruction selector or a stronger P6 audit-saturation ledger inside the chirality-faithful consistency-complete pool.

## Step 33 - Corrected Anomaly and Chirality Re-Derivation
- Led with the audit correction: Step 32 used the formal cubic-anomaly proxy for complexness, which is physically wrong for rank-one non-abelian factors.
- Corrected bookkeeping:
  - rank-one cubic anomaly is zero for all reps;
  - Witten parity is retained;
  - higher-rank cubic coefficients are unchanged;
  - chirality complexness is tested by self-conjugacy, not by cubic-anomaly value.
- Corrected carrier count: `11990`, versus the old Step-28 carrier count `280983`.
- Corrected trajectory: `11990 -> 156 -> 130 -> 80`.
- The Step-14 reference support passes all corrected stages but is not uniquely distinguished.
- Final per-structure counts: `2`: `0`; `2|2`: `0`; `2|3`: `15`; `3`: `49`; `4`: `16`.
- The old Step-32 `2|2` dominance is broken: old `2|2` final count `272`, corrected final count `0`.
- The final dominant structure is `3` with `49` survivors, not the target structure.
- Correctness self-checks pass: rank-one fund/sym cubic zero; higher-rank fund/antifund cubic intact; dimension-4 antisym2 zero; complexness uses self-conjugacy.
- Negative controls and Stage II pass: the predicate is not a target row picker, fails some corrected consistency survivors, and keeps the reference in the corrected carrier.
- Verdict: `NARROW`. Corrected physics bookkeeping is load-bearing and improves the discriminator, but does not land a unique selection.
- Next grammar delta: conjoin an F24 role-obstruction selector or P6 audit-saturation ledger over the corrected chirality-faithful pool.

## Step 34 - F24 Role-Obstruction Discriminator
- Reproduced the corrected Step-33 final carrier: `80`.
- Instantiated F24 with access quotient `q` as canonical non-abelian representation role and role readout `s` as abelian charge role.
- Obstruction definition: `O_s` counts same-`q` pairs with different `s`.
- Principled predicate: `O_s=0`, meaning the charge role descends through the non-abelian access quotient.
- O_s distribution over the 80: `0`: `10`; `1`: `34`; `2`: `36`.
- The Step-14 reference support has `O_s=1`, so it fails the principled `O_s=0` cut.
- F24-descending survivors: `10`, with `6` in the target structure and `4` in the rank-two single-factor structure; the reference is not among them.
- The reference's obstruction value is shared by `34` survivors, so selecting `O_s=1` would be tuning rather than an intrinsic law.
- Negative controls and Stage II pass: F24 is not a target row picker, fails `70` of `80`, has a nontrivial distribution, reproduces the corrected carrier, and computes the target obstruction.
- Verdict: `TYPED_NO_GO_TYPE_LIMIT`. Intrinsic gauge-closure filters narrow to a small family but do not provide the final reference selection.
- Next grammar delta: move to a higher-layer descent/content-cascade criterion or observed-input boundary, rather than another intrinsic gauge-only filter.

## Step 35 - Higher-Layer Descent Compatibility
- Reproduced the corrected Step-33 final carrier: `80`.
- Added the new grammar kind requested by Step 34: a neutral higher-layer descent compatibility predicate.
- Predicate definition: an enumerated scalar representative must supply gauge-invariant fermion-fermion-scalar mass-closure witnesses for every chiral fermion type and also satisfy a finite proper-breaking proxy with an abelian remainder.
- No observed scalar, observed masses, observed Yukawa values, generation count, or target support is inserted; this is a compatibility test, not a derivation of the next layer.
- Higher-layer survivors: `12`.
- Per-structure survivors: `2|3`: `8`; `3`: `0`; `4`: `4`.
- The Step-14 reference support passes with witness `rank_one_fundxsinglet:-3`, but is not uniquely distinguished.
- The predicate breaks the corrected single-factor `3` dominance by rejecting all `49` structure-`3` survivors.
- Negative controls and Stage II pass: the corrected `80` are reproduced, some survivors fail, the scalar witness is enumerated, and the predicate is not a target-row picker.
- Verdict: `NARROW`. The higher-layer descent criterion gives real progress but does not land a unique discriminator.
- Next grammar delta: conjoin a stricter higher-layer requirement, such as scalar-potential closure or family-replication consistency.

## Step 36 - Higher-Layer Refinement
- Reproduced the Step-35 higher-layer residual: `12`.
- Added the further higher-layer predicate: `staged_scalar_potential_closure`.
- Predicate definition: the Step-35 scalar witness must admit an invariant scalar-conjugate pairing, a bounded quartic proxy, and a staged residual route in which at least one independent non-abelian route remains untouched after scalar-active breaking.
- No empirical potential parameters, empirical mass values, empirical coupling values, fixed family count, or target support is inserted.
- Refined survivors: `8`.
- Per-structure survivors: `2|3`: `8`; `4`: `0`.
- The single-factor `4` family is eliminated.
- The Step-14 reference support passes with witness `rank_one_fundxsinglet:-3`, but is not uniquely distinguished.
- Negative controls and Stage II pass: the Step-35 residual is reproduced, four of twelve survivors fail, and the predicate is not a target-row picker.
- Verdict: `CONTENT_TYPE_LIMIT`. The higher-layer descent grammar narrows to the target structure family in this finite carrier, but unique content selection remains unresolved.
- Next grammar delta: continue into a matter-content cascade or observed-input boundary.

## Step 37 - Uniqueness Stress-Test
- Reproduced the Step-35 higher-layer residual: `12`.
- Stress-tested the Step-36 uniqueness criterion by dropping `factor_local_breaking`.
- Deflationary correction: the old factor-local rule is shape-flavored because it rejects single-factor structures by construction; it is now diagnostic-only.
- Precise replacement: compute unbroken non-abelian subgroups after scalar breaking, including partial breaking inside a factor.
- Precise unbroken-subgroup survivors: `12`; the single-factor `4` family survives.
- Non-shape principles tested:
  - precise unbroken subgroup: `12` survivors (`2|3:8;4:4`);
  - unbroken low-energy consistency: `12` survivors (`2|3:8;4:4`);
  - full cascade consistency: `12` survivors (`2|3:8;4:4`);
  - scalar-stage currency minimum: `8` diagnostic survivors (`2|3:8`), but this rescue is rejected.
- Manager override: scalar-stage currency minimum is diagnostic-only/rejected because it reduces to a smallest-broken-factor/minimality-like rescue.
- No Step-37 structure uniqueness is accepted; the accepted Step-37 residual is the small neutral family `{2|3, 4}`.
- Negative controls and Stage II pass: precise subgroup admits single-factor partial breaking, currency is not a target-row picker, and the old rule is flagged by the shape detector.
- Verdict: `SMALL_NEUTRAL_FAMILY_currency_rescue_REJECTED`.
- Next grammar delta: continue to Step 38's introduced clean-separation condition or to the matter-content boundary.

## Step 38 - Higher-Layer Shadow Uniqueness
- Reproduced the Step-35 higher-layer residual: `12`.
- Rejected the prior rescue criteria as verdict carriers: Step-36 factor-local breaking is shape-flavored, and Step-37 scalar-stage currency is a size/currency ordering.
- Computed the low-energy shadow after each mass-completing scalar VEV, including partial breaking inside a factor.
- Base shadow requirement: confining unbroken non-abelian subgroup plus completed mass sector.
- Base shadow survivors: `12` (`2|3:8;4:4`), confirming the small family before the clean-shadow test.
- Clean shadow requirement: base shadow plus no confining-charged broken-vector exotics.
- Clean shadow survivors: `8`, all in `2|3`.
- The single-factor `4` family leaves a confining `3` subgroup but also `6` confining-charged broken-vector exotics, so it fails the clean shadow.
- The `2|3` family leaves an unbroken confining `3` route with `0` confining-charged broken-vector exotics.
- The Step-14 reference support passes but is not unique among the `8`.
- Verdict: `SHADOW_UNIQUENESS_WITH_CONTENT_LIMIT`.
- Next grammar delta: content boundary remains; continue into a matter-content cascade or observed-input boundary.

## Step 39 - Clean-Separation Derivation Test
- Reproduced the Step-35 higher-layer residual: `12`.
- Tested the standard confining-sector requirement: confining charged matter is fermionic only, while confining-charged massive vector content is non-standard.
- Standardness survivors: `8` (`2|3`: `8`; `4`: `0`).
- Relaxed survivors when confining-charged massive vector content is allowed: `12` (`2|3`: `8`; `4`: `4`).
- Standardness implies clean separation on this carrier, but clean separation also implies standardness; the two conditions are extensionally equivalent here.
- Circularity is detected: the standardness phrasing does not provide a more basic independent basis for the Step-38 clean-separation cut.
- Relaxing the vector exclusion brings the single-factor `4` family back, so the condition is load-bearing and not vacuous.
- Verdict: `INDEPENDENT_INTRODUCED_CIRCULAR`.
- Next grammar delta: clean separation remains a qualified introduced standardness condition; continue to the content cascade or seek a richer confining-layer grammar.

## Step 41 - Factorization-Defect Restatement
- Reproduced the Step-38 carrier: `12` supports.
- Faithful quotient pair: `pi0 = pi_conf_interference`, `pi1 = pi_mass`.
- `pi_conf_interference` keeps all nontrivial confining charge in one interference cell and splits the trivial sector by mass, because colorless mass separation is allowed.
- Defect table by structure:
  - `2|3`: `8` supports, `8` defect-empty, `0` nonempty, `0` witnesses.
  - `4`: `4` supports, `0` defect-empty, `4` nonempty, `6` witnesses per support.
- Faithfulness: `Delta_fact(pi_conf_interference, pi_mass)=empty` agrees with the Step-38 clean-shadow verdict on all `12` supports.
- Witnesses: the nonempty defects expose exactly the confining-charged massive vector content counted by Step 38.
- Verdict: `RECOGNITION_SOURCE_RESTATEMENT`.
- Boundary: this gives clean separation a theorem-grade calculus home and explicit witnesses, but the condition remains supplied rather than generated by the framework.
