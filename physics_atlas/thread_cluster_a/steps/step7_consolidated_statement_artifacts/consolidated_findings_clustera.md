# Cluster A Consolidated Findings v2

## Grade

Finite-carrier bounded-grammar consolidation, updated after the v1 external review. Cluster A is a selection/measure construction over a candidate space, not a field-readout pair. It specifies the shape of the SM-selection-layer hole and does not derive physical SM values or mechanisms.

The v2 update folds in Steps 8-12. It narrows the one-layer claim, strengthens circularity/order/parameter robustness, and hardens validation infrastructure. No new physical values are inferred.

## Review Response Map

| review item | v2 response |
| --- | --- |
| R1 | repackaging / manager-handled scope item |
| R2 | Step 8 shows MI is induced by structural constraints; Step 9 shows non-factorizing but block-structured coupling |
| R3 | Step 8 builds a mechanically guarded token-blind selection on an 8640-world neutral carrier |
| R4 | Step 10 maps a 9520-cell robustness region and flip boundaries |
| R5 | Step 11 runs a refinement-order battery over 204 orders |
| R6 | Step 12 makes validators self-only by default with explicit chain mode |

## Baseline Frame

Step 1 builds \(L^\ast\) as a 9-world candidate space plus measure. `w_SM` is the computed argmax with score `106.0`. The SM shadow is selection-forgetting.

Computed non-descending signatures:

- joint structure: obstruction `36`;
- E019 gauge/rep: `21`;
- E020 generations/texture: `21`;
- E043 EW-scale: `14`;
- E009 UV completion: `14`;
- E037 vacuum: `14`;
- selection underdetermination: `1`.

The derived-observable control factors with obstruction `0`.

Grade: frame-signature. Sources: `steps/step1_shared_selection_layer_frame_artifacts/frame_signatures_step1.csv`, `steps/step1_shared_selection_layer_frame_artifacts/controls_step1.csv`.

## P2/P6 Mechanics

Step 2 extends the space to 13 candidates, prunes 4 anomalous tokens, leaves 9 anomaly-free survivors, and then collapses the survivors to `w_SM`. Eight anomaly-free survivors remain unselected before the selector, so anomaly-freedom is necessary but not sufficient. Gauge and generation are co-determined with mutual information `0.330856` bits.

Step 3 computes genuine selection degeneracy `9->5->4->2->1->1`, landing on `w_SM`. The unselected landscape remains `9->9->9->9->9->9`. This is the E037 distinguishing audit on the finite toy.

Grade: finite-toy-diagnostic. Sources: Step 2 pruning/collapse/codetermination CSVs and Step 3 degeneracy/P6/control CSVs.

## Facets

Step 4 shows the scale ratio is non-descending from EW Sigma with obstruction `3`; a derived EW observable factors with obstruction `0`. Both a toy attractor and a toy peaked measure reach `r_SM=0.0001`; the no-selection control remains unfixed.

Step 5 builds the UV-completion fiber. The realized IR fiber has 6 UV candidates; UV content is non-descending from IR with obstruction `16`; a derived IR observable factors with obstruction `0`. Consistency pruning leaves 3 admissible UV candidates, and selection collapses the fiber to one UV candidate.

Step 6 adjudicates E043 by P6 collapse:

- attractor: `6->5->4->2->1->1`, certified;
- broad anthropic measure: `6->6->6->6->6->6`, not certified;
- sharp measure: `3->2->2->1->1`, certified.

The criterion is collapse-to-point, not horn label. The framework is not agnostic on this finite selection type; this is not a physical rejection of anthropic reasoning.

## Step 8: Token-Blind Structural Selection

Step 8 answers the circularity objection. It generates an 8640-world neutral product over generic-coded facets and applies a structural, token-blind functional with mechanical guards against SM tokens, `n_gen==3`, and realized-world bonuses.

Result:

- neutral candidate space: `8640`;
- structural survivors: `468`;
- realized SM-analog point: among survivors, not unique;
- structural rank of realized analog: `2`;
- max-score tie count: `6`.

Grade: finite-carrier-diagnostic. Sources: `steps/step8_structural_token_blind_selection_artifacts/neutral_candidate_space_step8.csv`, `steps/step8_structural_token_blind_selection_artifacts/structural_survivors_step8.csv`, `steps/step8_structural_token_blind_selection_artifacts/schema.json`.

## Step 8/9: MI and Facet Factorization

Gauge-generation mutual information is `0.000` bits on the neutral product and `0.466` bits on the structural survivors. The coupling is induced by structural constraints, not by a curated population.

Step 9 narrows the old one-layer claim:

- total correlation on neutral product: `0.000000000000` bits;
- total correlation on structural survivors: `2.229304481463` bits;
- block split: `{gauge, rep, n_gen, texture, uv, vacuum}` plus `{ew}`;
- inter-block residual: `0.035998916880` bits;
- stricter naturalness cut: one connected component.

So the facets are not independent separable problems in the toy, but the main coupling graph is block-structured rather than cleanly monolithic. Whether real SM selection is one physical layer or several remains open.

Grade: finite-carrier-diagnostic. Sources: Step 8 MI CSV and Step 9 total-correlation/block/robustness CSVs.

## Step 10: Parameter Robustness

Step 10 sweeps the E043 collapse-vs-landscape criterion over 9520 parameter cells.

- hold cells: `4922`;
- flip cells: `4598`;
- Step 6 operating point: `VERDICT_HOLDS`;
- nearest same-grid flip margin: `0.306122448980`;
- flip families: `sharp_noncollapse` and `broad_false_collapse`.

The Step 6 point is inside a mapped hold region. The flip families are the explicit scope boundaries.

Grade: finite-carrier-diagnostic. Sources: `steps/step10_adjudication_robustness_sweep_artifacts/sweep_cells_step10.csv`, `steps/step10_adjudication_robustness_sweep_artifacts/flip_boundaries_step10.csv`, `steps/step10_adjudication_robustness_sweep_artifacts/operating_point_margin_step10.csv`.

## Step 11: Refinement-Order Battery

Step 11 tests whether collapse depends on a hand-aimed refinement order.

- total orders: `204`;
- random orders: `200`;
- genuine selection collapse fraction over random orders: `1.000000000000`;
- landscape non-collapse fraction over random orders: `1.000000000000`;
- adversarial delay-genuine: genuine final `1`, landscape final `27`;
- adversarial force-landscape: genuine final `1`, landscape final `6`;
- separation margin: `5`;
- flipping order count: `0`.

The verdict tracks the selection/measure structure, not the refinement order, on this finite battery.

Grade: finite-carrier-diagnostic. Sources: Step 11 order, adversarial, and separation CSVs.

## Step 12: Validator Hardening

Step 12 makes validator default mode non-recursive (`--self`) and adds explicit `--chain` mode. `steps/run_all_selfcheck.py` reports PASS for Steps 1-11. This is organizational only; no scientific artifact, computed number, claim, or grade changed.

Grade: organizational. Source: `steps/step12_validator_hardening_note.md`.

## Unified Criterion

The decaying-degeneracy criterion adjudicates selection type consistently: E037 and E043 here, and E021 in Cluster B Step 10. Collapse-to-point certifies; broad landscape behavior remains unclosed. This is a finite-toy shape result, not a derivation of physical values and not a physical rejection of anthropic reasoning.

## Interpretation, Not a Result

The borderline facet in Step 9 is the electroweak scale facet. In the toy it couples weakly because it is governed by a naturalness/tuning cost rather than the hard consistency constraints that bind the other facets. This resonates with the familiar status of the hierarchy/naturalness problem as the odd one out among the SM's why-this puzzles.

This is interpretation only. It is not a physics result, not a prediction, and not evidence about the real SM.

## Open Obligations

Open obligations remain: external frame-transfer review; richer carriers; the physical values and mechanisms for gauge group, generation count, Yukawa texture, electroweak scale, vacuum, and UV completion; and whether the real selection problem is one physical layer, several coupled blocks, or another richer structure.
