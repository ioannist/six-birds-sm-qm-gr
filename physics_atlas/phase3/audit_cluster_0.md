# Phase-3 Adversarial Audit — Cluster 0

Edges audited: E006, E012, E022, E027b, E032, E037, E043.
Auditor stance: adversarial; default to the more conservative tier on doubt; honesty never weakened.
Cross-checked against: TYPING_RUBRIC.md (frozen), SCIENCE_DIGEST.md, anti-reductionism primer, CONTRACT.json
(registered_null tier_members, modality_tier_compat, recognition_resolution.affected_edges,
value_split_schema.rows_carrying_value_split + C10 reported_tier rule), edge_manifest.jsonl, route.json.

All 7 scored tiers agree with the frozen registered-null tier_members
(E006=E1, E012=E1, E022=E2, E027b=E0, E032=E3, E037=E3, E043=E3) and every (primary_modality, tier)
pair is emittable per modality_tier_compat. No reductionist relapse found in any record: every UP edge
runs only the DOWN/descent arrow as a computation and certifies the up arrow as a gap; no constant is
derived; no E1 is sealed by an up-computation; banned language avoided.

The single systematic defect in this cluster was **schema-illegal added `value_split` objects** on three
records (E006, E012, E027b). The frozen CONTRACT enumerates EXACTLY six value_split-bearing rows
{E004, E008, E029, E035a, E038, E041}; none of this cluster's edges is among them, and the frozen
edge_manifest.jsonl carries `value_split: null` for all seven. Two of the three added splits also violate
validator check **C10** (scored_tier must equal the split-type-computed reported_tier). All three were
fixed in place by setting `value_split` to null (matching the frozen contract/manifest) — no tier changed.

---

## E006 — quantum_mechanics -> classical_mechanics (DOWN, shadow-down, E1)

**Verdict: FIX (applied) — value_split removed; tier/modality OK.**

- (1) Tier forced/honest: **honest.** The descent test is real: declared finite dephasing toy model
  (density operators on d-dim Hilbert space, pointer-diagonal lens), two refinements (d=3, d=6), FORM-leg
  normalized residual xi_rel ~1e-16 at both with kernel-containment (D0=A·L0). E1 matches registered null.
- (2) Xi real: **yes.** Toy model declared, two refinements, normalized residual ->~0 stably on the form
  leg. The E.3 over-read guard is genuine (appending an off-diagonal coherence observable breaks
  containment; kernel_containment=false at both refinements). Minor non-blocking note: the over-read leg's
  xi_rel DECAYS 0.44->0.062 rather than holding a stable-positive floor — but that leg is only the E.3
  containment-break demonstration (the boolean kernel-containment failure is what gates E.3), not the
  descent verdict, so it does not affect the E1 seal.
- (3) Primary modality correct: **yes.** Structural DESCENT (B.1) passes, so shadow-down is primary by the
  §B.7a precedence rule; no recognition-conditional secondary is warranted (the Born-weight/basis/outcome
  imports live on SEPARATE edges, not on E006).
- (4) §9 relapse: **none.** Only the down arrow is run; no derivation of QM from classical mechanics.
- (6) near-intra: route.json near_intra=false; record marks E.11 N/A — correct (distinct lenses, distinct
  Sigma_f: interference present in QM, absent classically).
- **DEFECT (fixed):** carried `value_split{split_type:form_value_imported, reported_tier:E1}`. C10 computes
  reported_tier for form_value_imported = value_tier = **E2**, so scored_tier E1 != computed reported E2 — a
  C10 freeze-block. The record's own note conceded it was "deviat[ing] ... from the generic
  form_value_imported->value_tier rule," which is exactly the silently-non-reported-leg failure C10 forbids.
  The Born-weight content is genuinely an externalized SEPARATE edge (E007), not an intra-E006 split.
  **Fix: value_split -> null** (matches frozen manifest + the 6-row frozen set); E1 headline unchanged;
  prose reconciled.

## E012 — qed -> classical_electromagnetism (DOWN, shadow-down, E1)

**Verdict: FIX (applied) — value_split removed; tier/modality OK.**

- (1)(2) Tier honest, Xi real: single-mode coherent-state toy model, two refinements (N=8/hbar=1.0,
  N=40/hbar=0.25), FORM-leg xi_rel 1.01e-5 -> 1.78e-16 (the 1e-5 is a Fock-truncation tail, not a stuck
  floor) -> clean hbar->0/coherent-state descent. Isolated radiative over-read test gives STABLE-POSITIVE
  xi_rel~0.64 at both refinements — correctly shows g-2/running-alpha do NOT descend. E1 matches null.
- (3) Primary modality: shadow-down correct (structural descent passes; no named import for the form leg).
- (4) §9 relapse: none; only the down arrow computed; alpha/g-2 explicitly NOT derived (flagged run/measure).
- (6) near-intra=false, correctly N/A.
- **DEFECT (fixed):** carried `value_split{split_type:form_value, reported_tier:E1}`. C10 computes
  form_value reported_tier = value_tier = **E0**, so scored E1 != computed E0 — C10 freeze-block. (The frozen
  form_value rows E004/E008/E035a/E038 pass C10 only because the CONTRACT pre-declares their
  edge_scored_tier=E1 AND reported_tier=E0; E012 is NOT a frozen value_split row, so no such exception
  exists.) The radiative readouts are an EXCLUDED over-read the descent correctly does not claim — not an
  intra-edge value-split. **Fix: value_split -> null**; E1 headline unchanged; prose reconciled.

## E022 — thermodynamics -> general_relativity (UP, recognition-landing, E2)

**Verdict: OK.**

- (1) Tier forced/honest: **honest.** Descent fails maximally (xi_rel=1.0 stably at both refinements; the
  entire GR geometric currency lies outside thermodynamics' Sigma_f), recognition-search returns a single
  named principle. E2 matches null; E022 is a frozen recognition_resolution.affected_edge.
- (2) N/A for E1 (this is E2): the descent-fail Xi is real and the over-read counterfactual (xi_rel
  collapses 1->0 ONLY when the Bekenstein-Hawking area-entropy + Rindler-thermality predicates are imported)
  correctly demonstrates the E.3 over-read, mirroring the E005 lesson.
- (3) Primary modality: **correct and well-discriminated.** All structural tests (B.1/B.3/B.4/B.5/B.6) fail;
  crucially B.5 currency/shadow-price is correctly refused as a SOURCE-side structural primary because this
  is the UP/recovery arrow (the discriminator vs E005, where surface gravity is the GR-side price on the
  DOWN arrow). With no structural test passing and the named import the entire landing mechanism,
  recognition-landing is primary by §B.7a — residual-by-construction, tier-locked E2.
- (5) Recognition: **exactly one non-menu named_import frozen** — Jacobson's "Einstein equation of state"
  (Clausius dQ=TdS on local Rindler horizons + S=A/4 + Unruh thermality), "no menu," frozen, and explicitly
  NOT substitutable into E005 (route-direction discipline honored — the up/down asymmetry trap is refused).
- (4) §9 relapse: none. Einstein equations are REFRAMED/RECOVERED under named assumptions, not derived;
  banned "derive/reduce" avoided for this UP edge; value_split correctly null.

## E027b — condensed_matter_spt -> spt-phases (UP, emergence-up, E0)

**Verdict: FIX (applied) — value_split removed; tier/modality OK.**

- (1) Tier forced/honest: **honest, and E.7-compliant.** This is a genuine E0 (not a doubt-haven): the
  E.7 interlock is satisfied with all required positives — descent logged negative (xi_rel=0.5 stable
  analytic floor), recognition logged negative for the realized VALUE, a constructible non-descending
  run-object POSITIVELY exhibited (discretely-jumping realized invariant; DMRG/ED/QMC), run_target stub
  present + deferred. E0 matches null.
- (2)/over-read: **decisive and correct.** The B.2 non-factorization witness is explicit (topological vs
  trivial SSH chains with identical symmetry-invariant local data to machine precision, different realized
  invariant). The over-read check is the strongest in the cluster: a naive orientation-bearing local probe
  gives a spuriously small (and GROWING) xi_rel by smuggling the symmetry-forbidden bond-orientation datum;
  reading against the protected symmetry-invariant Sigma_f restores the honest 0.5 floor — exactly the E005
  over-read discipline, applied correctly.
- (3) Primary modality: emergence-up correct (structural B.2 passes -> primary by §B.7a; is_recognition
  false; recognition-landing not applicable). (emergence-up, E0) is emittable; emergence-up E1 forbidden,
  consistent with not sealing E1.
- (4) §9 relapse: none — up/down asymmetry rigorously kept; no number claimed; run treated as irreducible.
- **DEFECT (fixed):** carried `value_split{form_tier:E2(cohomology), value_tier:E0, reported_leg:value_tier}`.
  This is C10-consistent (E0=E0) but is still NOT a frozen value_split row, and it CONFLATES the sibling
  edge E027a (the cohomology CLASSIFICATION, a SEPARATE recognition-landing E2) with an intra-E027b
  form-leg — the same conflation E006 made. The E027a/E027b separation is an INTER-edge split (already
  documented in diagnostic.e027a_vs_e027b_split), not a within-edge form/value split. **Fix: value_split
  -> null** (matches frozen manifest + 6-row set); E0 headline unchanged; prose reconciled.

## E032 — quantum_mechanics -> measurement-outcome (UP, emergence-up, E3)

**Verdict: OK (informative justified modality drift).**

- (1) Tier forced/honest: **honest.** Faithful finite descent test (native = QM ensemble functionals incl.
  Born weights; dissolving = single-outcome selectors): xi_rel=1.0 stable at d=3,d=5 (d-1 of d selectors
  outside the ensemble range). Recognition-search returns a MENU of mutually-incompatible interpretations
  (many-worlds / objective-collapse / Bohmian / QBism), NOT a single frozen import -> not E2. Run-search
  negative (unitary QM yields the ensemble, never a single label) -> not E0 (and E0 is not a doubt-haven).
  Foreclosure -> E3. Matches null. Correctly kept distinct from E007 (Born-WEIGHTS, single Gleason import)
  and E006 (decoherence shadow) — the record explicitly refuses to over-read E007's import as closing the
  SELECTION.
- (3) Primary modality: **drift OK.** Frozen provisional modality was common-refinement; scored is
  emergence-up. The B.4 common-third test genuinely FAILS (measurement-outcome is an observable_readout OF
  QM, not a sibling layer with a common refinement W), the arrow is up, and (emergence-up, E3) is emittable.
  E032 is NOT a calibration row, so the drift is the audited structural verdict, not subject to the
  calibration adjudication route; it is recorded, not silently force-aligned. The honest structural verdict.
- (4) §9 relapse: none — only the factorization (down) arrow computed; SBT explicitly SILENT on which
  interpretation is correct; E3 = foreclosure working. value_split correctly null.

## E037 — string-theory -> standard_model (UP, emergence-up, E3)

**Verdict: OK.**

- (1) Tier forced/honest: **honest, doubly so.** Independent of the numeric residual, the source
  (string-theory, candidate_substructure, not_established) MAY NOT source an E1 (may_source_E1 rule), so E1
  is structurally unavailable. Descent test still run: xi_rel stable-positive 0.730 -> 0.869 (vacuum-
  selection coordinate in ker(L0) not ker(D0); ~10^500 degeneracy does not decay). B.2 non-factorization
  exhibited. Recognition-search negative (swampland prunes but does not select; anthropic contested/non-
  predictive — no single named load-bearing principle). Run-search negative (no accepted vacuum-selecting
  run; contrast E001). Foreclosure -> E3. Matches null.
- (3) Primary modality emergence-up correct; emittable at E3.
- (4) §9 relapse: none — refused to manufacture a factorization phi; xi_rel is large so no small-Xi
  over-read; the gap is the source's OWN declared-discarded selection coordinate. value_split correctly null
  (the not_established source has no E1 form-leg to split off).

## E043 — electroweak_theory -> electroweak-hierarchy (UP, emergence-up, E3)

**Verdict: OK.**

- (1) Tier forced/honest: **honest, doubly so.** Target electroweak-hierarchy is an open_question node ->
  STEP-0 forces the E0/E3 branch ONLY (can never seal E1/E2), independent of numerics. Descent test still
  run: forward xi_rel 0.988 -> 0.999, reverse blind-spot xi_rel 0.948 -> 0.999 as tuning leakage eps -> 0
  (scale-selection coordinate outside the EW knobs' span; quadratic cutoff-sensitivity does not decay). B.2
  non-factorization exhibited. Recognition-search negative (SUSY/compositeness/anthropic are contested
  candidates, not a frozen single import). Run-search negative (m_H/v are free MEASURED INPUTS; no accepted
  run selects the scale; no run_target_stub frozen; E.7 unsatisfiable -> E0 not a doubt-haven). Foreclosure
  -> E3. Matches null. Correctly kept DISTINCT from E020 (fermion generations).
- (3) Primary modality emergence-up correct; emittable at E3.
- (4) §9 relapse: none — refused any casting that would "explain" the hierarchy; xi_rel large so no
  small-Xi over-read; no constant derived. value_split correctly null.

---

## Summary

- **Edges OK as scored:** E022, E032, E037, E043 (4).
- **Edges hard-fixed in place:** E006, E012, E027b (3) — illegal added `value_split` removed (set to null),
  reconciling each to the frozen edge_manifest (value_split:null) and the frozen 6-row
  rows_carrying_value_split set, and clearing the C10 reported_tier freeze-blocks on E006 and E012.
- **Tier corrections: NONE.** All seven scored tiers were already correct and unchanged
  (E006=E1, E012=E1, E022=E2, E027b=E0, E032=E3, E037=E3, E043=E3); the fixes were schema-legality only and
  did not weaken honesty or alter any headline tier.
- **Modality corrections: NONE** beyond E032's already-recorded justified drift (common-refinement ->
  emergence-up), which is correct and emittable.
- Post-fix re-validation: registered-null match, B.8 emittability, recognition-landing<->E2<->affected_edges
  with single non-menu named_import (E022), C10 reported_tier consistency, and JSON validity — all pass with
  **0 hard failures**.

**Flag count: 3** (E006, E012, E027b — illegal/added value_split, all fixed in place; of these E006 and
E012 were also active C10 freeze-blocks).
