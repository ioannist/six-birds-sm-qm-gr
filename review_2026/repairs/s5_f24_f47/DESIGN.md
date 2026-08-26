# S5 F24/F47 repair design

## Frozen sources

This repair imports the five requested Cluster-A build scripts read-only and checks each complete file against a literal SHA-256 constant before import:

- Step 8: neutral carrier, admissibility predicates, naturalness cost, and declared vacuum `measure_weight` at `physics_atlas/thread_cluster_a/steps/step8_structural_token_blind_selection_artifacts/structural_token_blind_selection_step8.py:29-68,71-188`.
- Step 9: facet entropy, mutual information, and component graph at `physics_atlas/thread_cluster_a/steps/step9_facet_factorization_test_artifacts/facet_factorization_test_step9.py:18-106`.
- Step 17: explicit eight-state scale carrier and product-layer construction at `physics_atlas/thread_cluster_a/steps/step17_two_layer_test_artifacts/two_layer_test_step17.py:18-120`.
- Step 18: content-dependent radiative channel and upstream strict threshold `2.75` at `physics_atlas/thread_cluster_a/steps/step18_two_layer_stress_test_artifacts/two_layer_stress_test_step18.py:18-98`.
- Step 19: `q`, radiative score, strict selector predicate, obstruction computation, and the literal family table being replaced at `physics_atlas/thread_cluster_a/steps/step19_layer_multiplicity_F24_artifacts/layer_multiplicity_f24_step19.py:17-135,137-238`.

No artifact CSV is used as computational input. Step 8's 8,640-row product and 468 admissible rows are regenerated in memory.

## Common F24 interface

Each of the eight named families is a constructed object with four reported predicates:

- `forms`: the family-defining carrier/closure object exists, not merely its label;
- `admissible`: every operative row passes the declared Step-8 gates;
- `closes`: alternating reachability or the relevant descent map reaches a consistent fixed point;
- `status`: computed from those predicates. The usual rule is `forms AND admissible AND closes`; `BlockedNonClosure` necessarily uses `forms AND admissible AND NOT closes`.

The real architecture carrier is the 468-row admissible subset. The full-product Step-19 role obstruction is still reproduced as 5,760 pairs; applying the same obstruction to the admissible carrier gives 307 pairs. Architecture formation is judged on the admissible carrier so inadmissible worlds cannot provide closure witnesses.

### Family constructions

- `MemoryLayer`: the Step-17 eight-state scale carrier, with the Step-8 realized scale states coupled to content through Step-18 radiative channel nodes. Content/scale reachability is iterated from the realized component to a fixed point.
- `BudgetedRole`: a finite bipartite ledger of `(naturalness_cost, s_readout)` budget states attached to content states; its closure is independently iterated.
- `HiddenUpstreamRole`: the actual `(uv_code, vacuum_code)` upstream carrier is materialized. It fails to form a *hidden* family because both coordinates are already explicit in `q`.
- `BridgeMediatedRole`: the actual radiative driver tuple is materialized. It fails strict bridge formation because every driver coordinate is a projection of `q`, not a third mediator.
- `ScopedRole`: the proper `e0` target-ratio subcarrier is constructed and its closure is tested against the full coupling graph. It fails on the real graph when closure escapes the scope.
- `CoarsenedRole`: all nontrivial set partitions of the finite `s` alphabet are enumerated and tested for constancy on every `q` fiber.
- `OutsideRoleScope`: the scale-deleting projection is materialized, then rejected because `ew_code` and naturalness are explicit tested coordinates.
- `BlockedNonClosure`: the coupled closure is run; this family fires only if the role split exists but the closure fails to reach a consistent fixed point.

The constructions are not declared mutually exclusive. If more than one closes, the verdict is architecture underdetermination.

## Mutation controls

Two mutated carriers are rebuilt through the same interface:

1. `mutation_budget_decoupled` removes the budget ledger but leaves the coupled multi-scale carrier unchanged. It must fire `MemoryLayer` alone.
2. `mutation_sealed_e0_scope` disables the budget and evaluates the declared `e0` proper subcarrier with cross-scope edges absent. It must fire `ScopedRole` alone.

The validator asserts the complete firing sets, not just one boolean.

## F47 measures and thresholds

The selector predicate remains exactly

`BASE_SCALE_RATIO[ew_code] <= TARGET_RATIO and radiative_score(row) > threshold`.

The strict inequality is load-bearing. The realized point has computed score exactly `2.75`, so it is included exactly when the threshold is below `2.75` and excluded at `2.75`.

The primary surface crosses thresholds `2.00..3.50` in exact `0.05` display steps with three denominators:

- all 8,640 product rows, unweighted;
- 468 admissible rows, unweighted;
- the same 468 admissible support rows weighted by Step-8 vacuum `measure_weight`, total measure mass 534.

The sensitivity surface additionally crosses `TARGET_RATIO in {1e-4,1e-2,1}` and `SMALL_THETA in {0.01,0.025,0.05,0.10,0.15}`. Zero-weight Step-8 vacuum rows remain in the 468-row support but contribute zero measure, exactly as the declared measure specifies.

The headline cell uses the weighted admissible denominator, `TARGET_RATIO=1e-4`, `SMALL_THETA=0.05`, and the upstream Step-18 threshold `2.75`. This avoids using inadmissible worlds, honors the declared measure, and does not lower the upstream threshold after observing that the realized score is 2.75.

## Validation

`run_s5.py --self` rebuilds the carrier, all eight family objects, both mutation firing sets, and the complete F47 surfaces in memory. It asserts source pins and load-bearing controls, writes to a temporary directory, and byte-compares every generated artifact.
