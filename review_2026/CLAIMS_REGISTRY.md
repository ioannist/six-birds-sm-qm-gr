# Authoritative claims registry

Generated from `review_2026/CLAIMS_REGISTRY.json`; edit the JSON and rerun
`python3 review_2026/build_claims_registry.py` rather than editing this view.

## Status summary

| status | count |
|---|---:|
| CERTIFIED | 7 |
| OPEN | 3 |
| RETYPED | 23 |
| WITHDRAWN | 9 |
| **TOTAL** | **42** |

## Registry

| id | status | evidence | controlling source | validators |
|---|---|---|---|---|
| `paper_foundational_strength_headline` | RETYPED | STIPULATED | `paper/submission/claim-audit.md#foundational-strength-headline` | — |
| `paper_three_forcing_headlines` | WITHDRAWN | COMPUTED | `paper/submission/claim-audit.md#three-forcing-headlines` | — |
| `paper_external_review_settled` | RETYPED | EXTERNAL_REPRODUCED | `paper/submission/claim-audit.md#external-review-settled` | — |
| `paper_su5_ratios` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#su5-ratios` | `review_2026/repairs/s3_generator_construction/run_s3_generator_construction_v2.py --self` |
| `paper_five_xy_roles` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#five-xy-roles` | `review_2026/repairs/s3_generator_construction/run_s3_generator_construction_v2.py --self` |
| `paper_carrier_exclusion` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#11990-carrier-exclusion` | `review_2026/repairs/s1_carrier_reconstruction/run_s1_carrier_reconstruction_v3.py --self` |
| `paper_gauge_structure_selection` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#gauge-structure-selection` | `review_2026/repairs/s1_carrier_reconstruction/run_s1_carrier_reconstruction_v3.py --self` |
| `paper_window_closure` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#window-closure` | `review_2026/repairs/s1_carrier_reconstruction/run_s1_carrier_reconstruction_v3.py --self` |
| `paper_content_blindness` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#content-blindness` | `review_2026/repairs/s4_content_quotient/run_s4.py --self` |
| `paper_generation_blindness` | WITHDRAWN | COMPUTED | `paper/submission/claim-audit.md#generation-blindness` | `review_2026/repairs/s4_content_quotient/run_s4.py --self` |
| `paper_mass_matrix_rank` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#mass-matrix-rank` | `review_2026/repairs/s4_content_quotient/run_s4.py --self` |
| `paper_record_stability_grounding` | OPEN | STIPULATED | `paper/submission/claim-audit.md#record-stability-grounding` | `review_2026/repairs/s6_record_grammar_ablation/run_s6_record_grammar_ablation_v3.py --self` |
| `paper_lstar_layer` | CERTIFIED | COMPUTED | `paper/submission/claim-audit.md#lstar-layer` | — |
| `paper_budgetedrole_f47` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#budgetedrole-f47` | `review_2026/repairs/s5_f24_f47/run_s5.py --self` |
| `paper_route_noncommutation` | WITHDRAWN | COMPUTED | `paper/submission/claim-audit.md#route-non-commutation` | `review_2026/repairs/q2_route_mismatch/run_q2.py --self` |
| `paper_qg_directed_nogo` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#qg-directed-no-go` | `review_2026/repairs/q1_access_provenance/run_q1.py --self` |
| `paper_access_uniqueness` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#access-uniqueness` | `review_2026/repairs/q1_access_provenance/run_q1.py --self` |
| `paper_fork_over_ladder` | CERTIFIED | COMPUTED | `paper/submission/claim-audit.md#fork-over-ladder` | `review_2026/repairs/q1_access_provenance/run_q1.py --self` |
| `paper_common_carrier_grounding` | WITHDRAWN | STIPULATED | `paper/submission/claim-audit.md#common-carrier-grounding` | — |
| `paper_area_shadow_price_identity` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#area-shadow-price-identity` | `review_2026/repairs/q5_lp_duality/run_q5.py --self` |
| `paper_linearized_einstein_response` | WITHDRAWN | COMPUTED | `paper/submission/claim-audit.md#linearized-einstein-response` | `review_2026/repairs/q5_lp_duality/run_q5.py --self` |
| `paper_one_born_area_ledger` | WITHDRAWN | COMPUTED | `paper/submission/claim-audit.md#one-born-area-ledger` | `review_2026/repairs/q5_lp_duality/run_q5.py --self` |
| `paper_cosmological_background_boundary` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#cosmological-background-boundary` | `review_2026/repairs/q7_f50_convergence/run_q7.py --self` |
| `paper_strict_extension_discriminator` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#strict-extension-discriminator` | — |
| `paper_g1_lambda_adjudication` | WITHDRAWN | COMPUTED | `paper/submission/claim-audit.md#g1-lambda-adjudication` | — |
| `paper_g2_singularity_boundary` | CERTIFIED | STIPULATED | `paper/submission/claim-audit.md#g2-singularity-boundary` | — |
| `paper_prediction_p1` | RETYPED | COMPUTED | `paper/submission/claim-audit.md#p1-controlling-summary-2026-08-27-post-external-review` | `open_programs/prog2_state_underdetermination/step6_exact_gauge_collapse/run_step6.py --self`<br>`open_programs/prog3_cut_fingerprints/step3_symmetric_closure/run_step3.py --self` |
| `paper_prediction_p2` | RETYPED | STIPULATED | `paper/submission/claim-audit.md#p2` | — |
| `paper_prediction_p3` | OPEN | STIPULATED | `paper/submission/claim-audit.md#p3` | `review_2026/repairs/s6_record_grammar_ablation/run_s6_record_grammar_ablation_v3.py --self` |
| `paper_method_anti_contamination` | RETYPED | STIPULATED | `paper/submission/claim-audit.md#method-anti-contamination` | — |
| `paper_one_grammar` | RETYPED | STIPULATED | `paper/submission/claim-audit.md#one-grammar` | — |
| `paper_support_surfaces` | RETYPED | STIPULATED | `paper/submission/claim-audit.md#support-surfaces` | — |
| `prog2_step6_controlling_outcome` | RETYPED | COMPUTED | `open_programs/prog2_state_underdetermination/CLOSURE.md#step-6-retyping-controlling-terminal-wording` | `open_programs/prog2_state_underdetermination/step6_exact_gauge_collapse/run_step6.py --self` |
| `prog3_step3_controlling_floor` | RETYPED | COMPUTED | `open_programs/prog3_cut_fingerprints/CLOSURE.md#step-3-retyping-controlling-track-wording` | `open_programs/prog3_cut_fingerprints/step3_symmetric_closure/run_step3.py --self` |
| `prog3_symmetric_closure_open` | OPEN | STIPULATED | `open_programs/prog3_cut_fingerprints/CLOSURE.md#successor-construction-target-open-door` | — |
| `s1v3_charge_normalization_census` | CERTIFIED | COMPUTED | `review_2026/repairs/s1_carrier_reconstruction/RESULTS_v3.md#charge-normalization-census` | `review_2026/repairs/s1_carrier_reconstruction/run_s1_carrier_reconstruction_v3.py --self` |
| `s1v3_branch_typed_selection` | CERTIFIED | COMPUTED | `review_2026/repairs/s1_carrier_reconstruction/RESULTS_v3.md#two-scalar-appendix` | `review_2026/repairs/s1_carrier_reconstruction/run_s1_carrier_reconstruction_v3.py --self` |
| `s3v2_su5_ratios` | CERTIFIED | COMPUTED | `review_2026/repairs/s3_generator_construction/RESULTS_v2.md#updated-claim-ledger-ky-and-weak-angle-ratio` | `review_2026/repairs/s3_generator_construction/run_s3_generator_construction_v2.py --self` |
| `s3v2_product_parent_control` | WITHDRAWN | COMPUTED | `review_2026/repairs/s3_generator_construction/RESULTS_v2.md#product-parent-control` | `review_2026/repairs/s3_generator_construction/run_s3_generator_construction_v2.py --self` |
| `q5_exact_lp_identity` | CERTIFIED | COMPUTED | `review_2026/repairs/q5_lp_duality/RESULTS.md#q5-lp-duality-repair-results` | `review_2026/repairs/q5_lp_duality/run_q5.py --self` |
| `q5_linearized_response` | WITHDRAWN | COMPUTED | `review_2026/repairs/q5_lp_duality/RESULTS.md#linearized-response` | `review_2026/repairs/q5_lp_duality/run_q5.py --self` |
| `q5_shared_mmi_class` | RETYPED | COMPUTED | `review_2026/repairs/q5_lp_duality/RESULTS.md#composition--step50` | `review_2026/repairs/q5_lp_duality/run_q5.py --self` |

## Controlling wordings

### `paper_foundational_strength_headline`

Status: **RETYPED**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#foundational-strength-headline`.

> RESTATE: finite constructions, recognition landings, two toy theorems

Superseded wordings:
- None recorded.

### `paper_three_forcing_headlines`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#three-forcing-headlines`.

> RETRACT / OPEN-PROGRAM

Superseded wordings:
- None recorded.

### `paper_external_review_settled`

Status: **RETYPED**. Evidence: **EXTERNAL_REPRODUCED**. Source: `paper/submission/claim-audit.md#external-review-settled`.

> RESTATE: v7 changes, v8 open, v9 unanswered

Superseded wordings:
- None recorded.

### `paper_su5_ratios`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#su5-ratios`.

> RESTATE with embedding, package, and weak-pair convention

Superseded wordings:
- None recorded.

### `paper_five_xy_roles`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#five-xy-roles`.

> RESTATE inside constructed SU(5) frame; step41 identity refuted

Superseded wordings:
- None recorded.

### `paper_carrier_exclusion`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#11990-carrier-exclusion`.

> RESTATE: 1,066 labelled / 419 declared-orbit / 195 primitive-orbit

Superseded wordings:
- None recorded.

### `paper_gauge_structure_selection`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#gauge-structure-selection`.

> RESTATE as branch-typed uniqueness under singleton/two-scalar caps

Superseded wordings:
- None recorded.

### `paper_window_closure`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#window-closure`.

> RESTATE with toy-grammar and validator caveats

Superseded wordings:
- None recorded.

### `paper_content_blindness`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#content-blindness`.

> RETRACT favorably: one selected content orbit under template

Superseded wordings:
- None recorded.

### `paper_generation_blindness`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#generation-blindness`.

> RETRACT; materialized N=1..4 predicates reported

Superseded wordings:
- None recorded.

### `paper_mass_matrix_rank`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#mass-matrix-rank`.

> RESTATE as generic symbolic ranks 14/28/42/56 with deficiencies 1/2/3/4

Superseded wordings:
- None recorded.

### `paper_record_stability_grounding`

Status: **OPEN**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#record-stability-grounding`.

> RETRACT / OPEN-PROGRAM

Superseded wordings:
- None recorded.

### `paper_lstar_layer`

Status: **CERTIFIED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#lstar-layer`.

> KEEP at coherent-finite-construction grade with caveats

Superseded wordings:
- None recorded.

### `paper_budgetedrole_f47`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#budgetedrole-f47`.

> RESTATE as underdetermined/convention-sensitive

Superseded wordings:
- None recorded.

### `paper_route_noncommutation`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#route-non-commutation`.

> RETRACT: published completions commute exactly

Superseded wordings:
- `review_2026/repairs/q2_route_mismatch/RESULTS.md` — “published E_QM and E_GR do not commute” (retained historical quote)

### `paper_qg_directed_nogo`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#qg-directed-no-go`.

> RESTATE: only two special routes tested

Superseded wordings:
- None recorded.

### `paper_access_uniqueness`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#access-uniqueness`.

> RESTATE as conditional provenance plus abstract partition theorem

Superseded wordings:
- None recorded.

### `paper_fork_over_ladder`

Status: **CERTIFIED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#fork-over-ladder`.

> KEEP narrowly on declared carrier and access assumptions

Superseded wordings:
- None recorded.

### `paper_common_carrier_grounding`

Status: **WITHDRAWN**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#common-carrier-grounding`.

> RETRACT GROUND; RESTATE as named hypothesis

Superseded wordings:
- None recorded.

### `paper_area_shadow_price_identity`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#area-shadow-price-identity`.

> RESTATE as exact finite-graph LP identity with edge dual variables

Superseded wordings:
- None recorded.

### `paper_linearized_einstein_response`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#linearized-einstein-response`.

> RETRACT

Superseded wordings:
- `paper/submission/claim-audit.md` — “linearized Einstein response” (retained historical quote)

### `paper_one_born_area_ledger`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#one-born-area-ledger`.

> RETRACT; retain shared MMI inequality class only

Superseded wordings:
- `paper/submission/claim-audit.md` — “one Born–area ledger” (retained historical quote)

### `paper_cosmological_background_boundary`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#cosmological-background-boundary`.

> RESTATE: solver artifact; sample-bounded fixed points/stability

Superseded wordings:
- None recorded.

### `paper_strict_extension_discriminator`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#strict-extension-discriminator`.

> RESTATE as conditional lemma/two exemplars

Superseded wordings:
- None recorded.

### `paper_g1_lambda_adjudication`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#g1-lambda-adjudication`.

> RETRACT as circular archived exploration

Superseded wordings:
- None recorded.

### `paper_g2_singularity_boundary`

Status: **CERTIFIED**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#g2-singularity-boundary`.

> KEEP at contested finite-toy grade

Superseded wordings:
- None recorded.

### `paper_prediction_p1`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `paper/submission/claim-audit.md#p1-controlling-summary-2026-08-27-post-external-review`.

> At graph level, for each of the 19 corresponding base/perturbed pairs, a queue-exhaustive forward search under four directed reduction rules and bidirectional Delta-Y/Y-Delta finds the two reachability sets disjoint; this establishes forward-reachability disjointness only, and symmetric-closure orbit disjointness remains open. At state level, the six constructed positive-algebraic same-graph pairs are exact noninjective fibers of the joint complete-cut/state map and exact instances of the gauge-collapse lemma: on any fixed connected binary-copy `C2_L1` carrier with positive capacities, equal-product assignments admit an exact diagonal internal-bond intertwiner up to vertex-wise scalars, so those six fibers collapse under the constructed exact diagonal tensor gauge and are not inequivalent tensor-network presentations. No physically complete bulk gauge relation or bulk-geometry underdetermination theorem is established.

Superseded wordings:
- `paper/submission/claim-audit.md` — “two finite routes RESOLVED within declared scope” (already edited from source)

### `paper_prediction_p2`

Status: **RETYPED**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#p2`.

> RETRACT forcing; KEEP conditional LOCC channel

Superseded wordings:
- None recorded.

### `paper_prediction_p3`

Status: **OPEN**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#p3`.

> RETRACT forcing; OPEN-PROGRAM dynamics

Superseded wordings:
- None recorded.

### `paper_method_anti_contamination`

Status: **RETYPED**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#method-anti-contamination`.

> RESTATE as heterogeneous audit and procedural self-report

Superseded wordings:
- None recorded.

### `paper_one_grammar`

Status: **RETYPED**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#one-grammar`.

> RETRACT forcing/universality; RESTATE as shared vocabulary on two carriers

Superseded wordings:
- None recorded.

### `paper_support_surfaces`

Status: **RETYPED**. Evidence: **STIPULATED**. Source: `paper/submission/claim-audit.md#support-surfaces`.

> State integrity caveats; do not claim uniform self-verification

Superseded wordings:
- None recorded.

### `prog2_step6_controlling_outcome`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `open_programs/prog2_state_underdetermination/CLOSURE.md#step-6-retyping-controlling-terminal-wording`.

> On any fixed connected binary-copy `C2_L1` carrier with positive capacities, the normalized boundary state depends only on the total edge-capacity product, and any two equal-product assignments admit an exact diagonal internal-bond intertwiner up to vertex-wise scalars. The six constructed positive-algebraic same-graph pairs are exact noninjective fibers of the joint complete-cut/state map and exact instances of this gauge-collapse lemma. They are therefore not inequivalent tensor-network presentations. Their exact `I(c)` separation survives only for the frozen capacity-label-preserving decorated-carrier relation; the literal Step-5 classification remains correct under that stipulation, while Step 6 retypes the tensor presentations after constructing the previously missing intertwiner. No physically complete bulk gauge relation or bulk-geometry underdetermination theorem is established.

Superseded wordings:
- `open_programs/prog2_state_underdetermination/CLOSURE.md` — “six exact finite declared-gauge underdetermination examples” (retained historical quote)

### `prog3_step3_controlling_floor`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `open_programs/prog3_cut_fingerprints/CLOSURE.md#step-3-retyping-controlling-track-wording`.

> On 13 fixed exact-rational graph topologies, 19 kernel directions yield nondegenerate positive-capacity intervals with identical complete terminal min-cut fingerprints and unique active minimizers. Selected endpoints have different weights and are not related by terminal-label-fixed weighted automorphism. For each of the 19 corresponding base/perturbed pairs, a queue-exhaustive forward search under four directed reduction rules and bidirectional Delta-Y/Y-Delta finds the two reachability sets disjoint. The search admits only intermediate presentations with the unchanged complete fingerprint and unique active minimizers and canonicalizes them modulo terminal-label-fixed exact weighted isomorphism. This establishes forward-reachability disjointness only; it establishes no symmetric-closure, completeness, or gauge-irreducibility claim.
>
> An exact inverse-series witness proves that the symmetric closure is strictly larger than the computed forward sets. Series removal has a unique normal form on admissible homeomorphic subdivisions of the 13 pinned series-reduced carriers. However, an exact subdivided-Y-leg counterexample refutes the attempted series/Delta-Y projection lemma. It neither connects nor separates any certified endpoint pair; symmetric-closure orbit disjointness remains open. Kalman-Krauthgamer exclude only universal local degree-k>3 star-to-clique rules, not undeclared, inverse, context-dependent, nonlocal, or degenerate-intermediate transformations.

Provenance: An external adversarial review supplied the exact inverse-series witness; it was reproduced on this tree, and Step 3 computed the controlling retype and failed upgrade attempt.

Superseded wordings:
- `open_programs/prog3_cut_fingerprints/CLOSURE.md` — “complete five-move-orbit-disjoint” (retained historical quote)
- `open_programs/prog3_cut_fingerprints/CLOSURE.md` — “complete queue-exhaustive closure ... orbits disjoint” (retained historical quote)

### `prog3_symmetric_closure_open`

Status: **OPEN**. Evidence: **STIPULATED**. Source: `open_programs/prog3_cut_fingerprints/CLOSURE.md#successor-construction-target-open-door`.

> **Successor construction target (open door):** symmetric-closure orbit disjointness under the declared moves.

Superseded wordings:
- None recorded.

### `s1v3_charge_normalization_census`

Status: **CERTIFIED**. Evidence: **COMPUTED**. Source: `review_2026/repairs/s1_carrier_reconstruction/RESULTS_v3.md#charge-normalization-census`.

> The cumulative chiral-to-faithful comparisons are therefore `1,066 -> 52 = 95.121951%` labelled, `419 -> 24 = 94.272076%` under declared-charge orbits, and `195 -> 24 = 87.692308%` under primitive-normalized orbits. Primitive-normalized orbits are preferred for the community-facing denominator because overall U(1) scale is conventional; declared-charge orbits remain the exact bounded-enumeration comparison.

Superseded wordings:
- None recorded.

### `s1v3_branch_typed_selection`

Status: **CERTIFIED**. Evidence: **COMPUTED**. Source: `review_2026/repairs/s1_carrier_reconstruction/RESULTS_v3.md#two-scalar-appendix`.

> There are 68 clean pair branches (17 declared pair orbits), but **no clean pair occurs outside `2|3` with SU(2)-only scalar action**. Thus the two-scalar extension removes the “no admissible branch” obstruction for all 44 structures while sharpening, rather than broadening, the clean-family statement. These appendix counts do not replace the singleton headline.

Superseded wordings:
- None recorded.

### `s3v2_su5_ratios`

Status: **CERTIFIED**. Evidence: **COMPUTED**. Source: `review_2026/repairs/s3_generator_construction/RESULTS_v2.md#updated-claim-ledger-ky-and-weak-angle-ratio`.

> k_Y=5/3; sin2(theta_W)=3/8

Superseded wordings:
- None recorded.

### `s3v2_product_parent_control`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `review_2026/repairs/s3_generator_construction/RESULTS_v2.md#product-parent-control`.

> No well-posed `3/23` product parent was found, so the paper's product-parent statement remains an unsupported import and requires correction; this does not prove that every exotic product embedding is impossible.

Superseded wordings:
- `review_2026/repairs/s3_generator_construction/RESULTS_v2.md` — “product parent yields 3/23” (retained historical quote)

### `q5_exact_lp_identity`

Status: **CERTIFIED**. Evidence: **COMPUTED**. Source: `review_2026/repairs/q5_lp_duality/RESULTS.md#q5-lp-duality-repair-results`.

> Corrected identity: **Area(min cut) = dual optimum = sum_e c_e y_e; y_e is the per-edge shadow price (the 0/1 cut-incidence variable in this chamber).** The optimum is a scalar; the shadow prices are the separate edge-indexed variables `y_e`.

Superseded wordings:
- None recorded.

### `q5_linearized_response`

Status: **WITHDRAWN**. Evidence: **COMPUTED**. Source: `review_2026/repairs/q5_lp_duality/RESULTS.md#linearized-response`.

> Thus the frozen Step45 conclusion is not recovered at an honest generic base point when the deformation is specified independently.

Superseded wordings:
- None recorded.

### `q5_shared_mmi_class`

Status: **RETYPED**. Evidence: **COMPUTED**. Source: `review_2026/repairs/q5_lp_duality/RESULTS.md#composition--step50`.

> The actual boundary contraction obeys the computed min-plus rule on the area side, but the Born values do not obey that same rule on all probes. Verdict: **DOWNGRADED_SHARED_MMI_CLASS_DIFFERENT_DEPENDENCIES**. What survives is the weaker computed statement that the co-sourced Born and area ledgers satisfy the same MMI inequality class for the tested triple (`I3_Born=-0.0363459273725`, `I3_area=-4.4408920985e-16`), while depending on state amplitudes and graph capacities respectively.

Superseded wordings:
- None recorded.

