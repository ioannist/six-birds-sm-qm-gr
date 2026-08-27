# PROG2 Step 4 — complete-kernel continuation and generated-gauge audit

## Certified construction

Six exact-algebraic finite continuation candidates have identical complete cut fingerprints and identical connected-copy boundary states but distinct raw capacities. The exact endpoints, product equalities, all 254 ordered-region fingerprints, positive uniqueness margins, and connected-copy state equality survive FIX2. The AM–GM statement remains only the tangent-plane lemma.

## Combined generated-gauge closure

The closure now uses one worklist containing all five graph moves, every single-edge reciprocal/basis swap, and terminal-fixed exact weighted canonicalization after every step. Weights are general elements of `QQ(alpha)` represented as polynomials modulo each endpoint's exported algebraic polynomial; inversion and sign decisions are exact, including the degree-five field for `cand_06`.

No finiteness theorem or finite completeness bound is known; all twelve searches exceed the frozen 64-state exploration budget. Every endpoint reaches the state cap, so every pair is honestly budget-truncated.

| id | field degree | base states/processed | displaced states/processed | intersection | closure verdict | signature status | typed outcome |
|---|---:|---:|---:|---:|---|---|---|
| cand_01 | 2 | 64/5 | 64/5 | 0 | DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED | EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF | **PENDING_GENERATED_GAUGE_CLOSURE** |
| cand_02 | 2 | 64/5 | 64/5 | 0 | DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED | EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF | **PENDING_GENERATED_GAUGE_CLOSURE** |
| cand_03 | 2 | 64/7 | 64/7 | 0 | DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED | EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF | **PENDING_GENERATED_GAUGE_CLOSURE** |
| cand_04 | 2 | 64/7 | 64/7 | 0 | DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED | EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF | **PENDING_GENERATED_GAUGE_CLOSURE** |
| cand_05 | 2 | 64/8 | 64/8 | 0 | DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED | EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF | **PENDING_GENERATED_GAUGE_CLOSURE** |
| cand_06 | 5 | 64/7 | 64/7 | 0 | DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED | EXPLORED_SIGNATURE_DIFFERS__NOT_AN_INVARIANT_PROOF | **PENDING_GENERATED_GAUGE_CLOSURE** |

No pair collapsed to gauge in the explored combined closures. This is only `DISJOINT_WITHIN_EXPLORED_CLOSURE_BUDGET_TRUNCATED`, not generated-gauge inequivalence. Paths would be exported if an intersection occurred.

## Reciprocal-first canary

| base | reciprocal edge | new proposals | accepted exact moves |
|---|---:|---:|---:|
| cand_03 | 3 | 2 | 2 |
| cand_03 | 5 | 4 | 4 |
| cand_03 | 6 | 2 | 2 |
| cand_03 | 11 | 4 | 4 |

On `cand_03` base, reciprocal edges 3, 5, 6, and 11 expose the reviewer-pinned zero-column/inseparable moves. All are full-fingerprint checked and accepted by the same combined engine; the old abort behavior is gone.

## Invariant status

The earlier five-move-orbit-plus-detached-reciprocal signature is withdrawn: it was not invariant under alternating generator compositions. FIX2 records a capacity-multiset signature over the **explored combined orbit** only. The explored signatures differ for all six pairs, but because each closure is truncated this is explicitly `NOT_AN_INVARIANT_PROOF`. The two affected obligations per pair—generated gauge closure and bulk invariant—are therefore `PENDING_GENERATED_GAUGE_CLOSURE` (12 pending obligations total).

## Outcome

All six objects remain exact-algebraic finite continuation **candidates**. None is currently certified as bulk-inequivalent under the generated gauge relation, and no surviving underdetermination claim is made. The open obstruction is saturation or a separately proved generator-by-generator invariant.
