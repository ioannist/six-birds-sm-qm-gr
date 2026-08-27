# PROG3 Step 3 — orbit-typing floor and symmetric-closure upgrade attempt

## Mandatory floor

On 13 fixed exact-rational graph topologies,
19 kernel directions yield nondegenerate positive-capacity intervals with identical complete
terminal min-cut fingerprints and unique active minimizers. Selected endpoints have different
weights and are not related by terminal-label-fixed weighted automorphism. For each of the 19
corresponding base/perturbed pairs, a queue-exhaustive **forward** search under four directed
reduction rules and bidirectional Delta-Y/Y-Delta finds the two reachability sets disjoint.
The search admits only intermediate presentations with the unchanged complete fingerprint and
unique active minimizers and canonicalizes them modulo terminal-label-fixed exact weighted
isomorphism. This establishes forward-reachability disjointness only; it establishes no
symmetric-closure, completeness, or gauge-irreducibility claim.

| fiber | carrier | seed | basis | forward states base/perturbed | forward intersection | floor | symmetric upgrade |
|---|---|---:|---:|---:|---:|---|---|
| fiber_001 | wheel_W4__b8__leaf_offset0 | 47 | 0 | 5/5 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_002 | wheel_W4__b8__leaf_offset0 | 47 | 1 | 5/5 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_003 | wheel_W4__b8__leaf_offset0 | 47 | 2 | 5/5 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_004 | wheel_W4__b8__leaf_offset1 | 17 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_005 | wheel_W4__b8__leaf_offset1 | 17 | 1 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_006 | wheel_W4__b8__leaf_offset1 | 31 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_007 | wheel_W4__b8__leaf_offset1 | 31 | 1 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_008 | K23_bipartite__b6__leaf_offset0 | 31 | 0 | 3/3 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_009 | K23_bipartite__b6__dual_gateway | 47 | 0 | 3/3 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_010 | K23_bipartite__b7__leaf_offset1 | 47 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_011 | K23_bipartite__b8__leaf_offset0 | 17 | 0 | 5/5 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_012 | K23_bipartite__b8__leaf_offset1 | 17 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_013 | K23_bipartite__b8__leaf_offset1 | 31 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_014 | K23_bipartite__b8__leaf_offset1 | 47 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_015 | K23_bipartite__b8__dual_gateway | 17 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_016 | K23_bipartite__b8__dual_gateway | 17 | 1 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_017 | K23_bipartite__b8__dual_gateway | 31 | 0 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_018 | K23_bipartite__b8__dual_gateway | 31 | 1 | 1/1 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |
| fiber_019 | K23_bipartite__b8__dual_gateway | 47 | 0 | 6/6 | 0 | FORWARD_REACHABILITY_SETS_DISJOINT__QUEUE_EXHAUSTED | NOT_CERTIFIED__L2_SERIES_DELTA_COHERENCE_FAILED |

## Directionality census

| move class | Step-2 directionality | accepted transitions | novel states |
|---|---|---:|---:|
| series | reduction_only | 0 | 0 |
| two_terminal_module | reduction_only | 0 | 0 |
| saturated_or_zero_column | reduction_only | 0 | 0 |
| inseparable_contraction | reduction_only | 0 | 0 |
| delta_y_y_delta | bidirectional | 100 | 50 |

All 50 novel Step-2 canonical states arise from the bidirectional Delta–Y class; none of
the four reduction-only classes fires on the 38 reduced endpoints or their admitted forward
successors.

## External-witness regression, independently rebuilt

On `wheel_W4__b8__leaf_offset0`, seed 47, edge `B0--I0` has
capacity `7009386627097/6871947673600`. Replacing it by the exact path
`(7009386627097/6871947673600, 7009386627097/3435973836800)` preserves all
127 complement-reduced (254 ordered)
terminal min-cut values and leaves every minimizer unique, with exact minimum margin
`135/274877906944`. The maintained series rule recomposes the
path by `min`, exactly recovers the endpoint, and the expanded canonical presentation is
absent from the endpoint's 5-state Step-2 forward set.
This permanently reproduces the forward-versus-symmetric typing defect.

## Lemma outcomes

| lemma | outcome | exact certificates | scope |
|---|---|---:|---|
| L1_SERIES_NORMAL_FORM_ON_ADMISSIBLE_HOMEOMORPHIC_EXPANSIONS | PROVED_AND_CERTIFIED | 13 | positive exact splits of edges in the 13 pinned series-reduced carrier instances; min composition |
| L2_SERIES_DELTA_Y_COHERENCE | FAILED | 1 | subdivided leg of an accepted Y-to-Delta move on fiber_008 |
| L3_SYMMETRIC_SERIES_DELTA_ORBIT_DISJOINTNESS | NOT_REACHED_BECAUSE_L2_FAILED | 0 | all 19 fibers |

L1 lands for admissible homeomorphic expansions of the 13 pinned series-reduced carrier
instances. L2 fails at the subdivided-Y-leg case on `fiber_008`: the promoted
subdivision vertex has degree 3, the two exact normal
forms have 10 and 9 edges,
and their terminal-fixed exact weighted canonical keys differ. Both remain unique and preserve
the full exact fingerprint. The detailed graph and capacities are exported in
`l2_counterexample_step3.csv`.

Therefore the attempted projection to Delta-only paths between series normal forms is invalid,
and no symmetric `{series subdivision/removal, Delta–Y/Y–Delta}` orbit-disjointness verdict
is certified here. The exact obstruction locates the failure; it neither connects nor separates
any certified endpoint pair in that symmetric closure.

## Can-fail controls

| control | kind | expected/observed classification | expected/observed reason | metric | value | passes |
|---|---|---|---|---|---|---|
| A_SHARED_ENDPOINT_REJECTS_DISJOINT_FLOOR | CAN_FAIL_NEGATIVE | FLOOR_REJECTED / FLOOR_REJECTED | NONEMPTY_FORWARD_SET_INTERSECTION / NONEMPTY_FORWARD_SET_INTERSECTION | cross_canonical_state_count | 5 | True |
| B_L2_EDGE_MUTATION_BREAKS_FINGERPRINT | CAN_FAIL_NEGATIVE | FINGERPRINT_EQUALITY_REJECTED / FINGERPRINT_EQUALITY_REJECTED | EXACT_FINGERPRINT_CHANGED / EXACT_FINGERPRINT_CHANGED | changed_regions_after_edge_0_mutation | 2 | True |
| C_INTERIOR_RELABEL_IS_RECOGNIZED | POSITIVE_CANONICALIZATION | WEIGHTED_ISOMORPHISM_ACCEPTED / WEIGHTED_ISOMORPHISM_ACCEPTED | TERMINAL_FIXED_WEIGHTED_ISOMORPHISM_RECOGNIZED / TERMINAL_FIXED_WEIGHTED_ISOMORPHISM_RECOGNIZED | canonical_keys_equal | True | True |
| D_EQUAL_ACTIVE_SPLIT_FAILS_UNIQUENESS | CAN_FAIL_NEGATIVE | UNIQUE_MINIMIZER_ADMISSION_REJECTED / UNIQUE_MINIMIZER_ADMISSION_REJECTED | ACTIVE_CUT_HAS_TWO_SUBDIVISION_SIDE_MINIMIZERS / ACTIVE_CUT_HAS_TWO_SUBDIVISION_SIDE_MINIMIZERS | edge_0_minimum_margin_exact | 0 | True |
| E_NON_SERIES_REDUCED_BASE_REDUCES_PAST_ITSELF | HYPOTHESIS_NECESSITY | STARTING_PRESENTATION_REJECTED_AS_NORMAL_FORM / STARTING_PRESENTATION_REJECTED_AS_NORMAL_FORM | NONTERMINAL_BIVALENT_BASE_IS_NOT_ITS_NORMAL_FORM / NONTERMINAL_BIVALENT_BASE_IS_NOT_ITS_NORMAL_FORM | nodes_before_after_series_reduction | 13->12 | True |

## Literature boundary

Kalman–Krauthgamer Theorem 3.24 rules out a universal local degree-`k>3` star-to-clique
min-cut rule. It does not establish completeness of the five classes; their Open Question 4.5
leaves context-dependent and nonlocal transforms open.
