# Phase-3 Adversarial Audit — Cluster 2

> **SUPERSEDED-BY-MERGE NOTE:** where this pre-merge audit advice conflicts with the authoritative
> `phase3/scored_run/edge_manifest.jsonl` (esp. value-split handling and E017 status), the merged
> manifest governs. Specifically: the **E008** "manifest is inconsistent" flag this cluster relayed
> is WITHDRAWN — the frozen contract governs (`value_split.reported_tier:"E0"` for the run-only
> value-leg AND headline `edge_scored_tier:"E1"` for the form-descent closure are the two distinct,
> non-conflicting schema fields per R3 / validator C10); the raw E008 record has been corrected to
> match. The fresh `value_split` this cluster noted for **E014** is NOT registered in this atlas
> (E014 is not in `CONTRACT.value_split_schema.rows_carrying_value_split`); the raw record renames it
> to `future_freeze_candidate_value_split` (a new freeze + Run-Target ledger entry would be needed).
> For E017's status, see the merged manifest: within-a-layer/no-content, `scored_tier:"E3"` sentinel,
> excluded from the chargeable foreclosure count.

**Auditor role:** adversarial auditor for Phase-3 edge typings.
**Records audited:** E008, E014, E024, E028b, E034, E039 (E014 read for cross-consistency; it
was not in the assigned fix-list but is consistent — see note).
**References:** anti-reductionism primer, SCIENCE_DIGEST, TYPING_RUBRIC (§B.5–B.8, §C, §D.1.1,
§E.0–E.13, §F), route.json provisional flags.
**Independent spot-checks performed (finite linear algebra, no irreducible run):** E028b
block-orthogonal Schur complement (xi_rel=1.0 + over-read collapse to 0); E034 two-leg
form/value split (form→1e-15, value stable-positive, geom-only control→1e-15); E039 Lorentz
covariance residuals (SR scalar invariance, EM field-invariant, EM antisymmetry all ~1e-15).
All reproduced the records' qualitative claims.

**Attack vectors applied to each edge:** (1) tier forced/honest vs fitted; (2) for E1: is the Xi
computation real (declared toy, two refinements, normalized residual → ~0) or asserted/over-read;
(3) primary modality correct per the precedence rule (structural beats residual recognition);
(4) any §9 reductionist relapse (derive-across-layers, score-within-a-layer, up/down symmetry);
(5) E2 recognition: exactly one non-menu named_import frozen; (6) near-intra E.4 honesty.

---

## Per-edge verdicts

### E008 — relativistic_qft → rg_eft — scored E1 / shadow-down — **OK**
- **Tier forced:** Yes. The Wilsonian RG / EFT down-shadow; FORM-leg xi_rel ~1e-15 stable across
  both refinements (exact factorization D0 = A·L0, geometric series in E/Λ); VALUE-leg
  (strong-coupling matched coupling) xi_rel ~0.53 stable-positive, correctly fenced OUT to an E0
  value-leg, never summed into the E1 count. Honest.
- **Xi real:** Yes. Toy declared (light/heavy mode split), two refinements, both raw Ξ and xi_rel
  reported, FORM→0 / VALUE stable-positive. Not over-read.
- **Primary modality:** shadow-down (structural descent passes) — correct per precedence; not a
  recognition-landing (no named import needed for the form descent).
- **§9 relapse:** None. Run-only values deferred to E0, not derived; UP direction is the separate
  E009 edge; asymmetry held; E.4 relabeling-residual non-vacuous.
- **E2 recognition / named import:** N/A (E1 edge).
- **near-intra:** N/A (near_intra=false, genuine RG quotient).
- **Note (not a scored-record defect):** the record correctly flags an inconsistency in the FROZEN
  `edge_manifest.jsonl` E008 `value_split` block (manifest sets `reported_tier='E0'` while its own
  `headline_tier='E1'`). Per rubric §E.3, the `form_value` rows (E004/E008/E035a/E038) are the
  explicit carve-out whose edge-level closure IS the structure descent ⇒ reported leg = the E1
  form-descent. The record sets `value_split.reported_tier='E1'` (= scored_tier=E1, so C10
  headline==reported_tier passes) and flags the manifest for correction. Correct handling.

### E014 — relativistic_qft → quantum_mechanics — scored E1 / shadow-down — **OK (cross-consistency)**
- Direct NRQED/NRQCD sibling of E008. FORM-leg (NR limit, v/c→0) xi_rel 1.14e-6 → 1.59e-8 stable;
  no-over-read gate (E.3) is the decisive discipline and passes — QFT's source-only sector
  (pair creation/antiparticles/variable particle number) is correctly left as a positive
  obstruction, not claimed as descended. Matched NR low-energy constants fenced to an E0 value-leg.
  Same `form_value` carve-out reasoning as E008. Honest; modality/tier consistent. (Outside my
  hard-fix scope; recorded for cluster cross-consistency.)

### E024 — conformal-field-theory → entanglement-geometry — scored E2 / currency-shadow-price (+recognition-conditional secondary) — **OK**
- **Tier forced:** Yes, and over-determined. Source `conformal-field-theory` is
  `established_status=not_established` ⇒ `may_source_E1=false`, so E1 is structurally forbidden
  regardless of Ξ. The small numeric xi_rel (2.3e-5 → 1e-6) is correctly read as an **OVER-READ**
  (the E005 pattern): the readout S=Area/4G_N imports G_N + a bulk metric/minimal-surface notion
  not in CFT's Σ_f. The named RT import is load-bearing (E.4: remove RT ⇒ no relation) ⇒ E2 over E3.
- **Xi real / not over-read:** Yes. The record explicitly REFUSES to read the small Ξ as E1 (the
  decisive E005 lesson), reading xi_rel against the full target readout map including the imported
  predicates.
- **Primary modality (the adversarially hardest call):** currency-shadow-price PRIMARY is correct.
  The CFT-side currency (boundary entanglement entropy, Cardy–Calabrese) is genuinely structural and
  in CFT's Σ_f (NOT imported); the positive residual read as currency is the located obstruction;
  the shadow-price (bulk area) is what needs the named RT import. Rubric §B.5 explicitly routes a
  currency-shadow-price edge "whose price needs a named principle" to E2 — this is the E005 template
  exactly (structural-currency-E2 + recognition-conditional secondary). The "verified by construction"
  phrase refers to the RT identity *coupling* (the secondary import), not to the CFT-side currency.
  Consistent with route.json `is_recognition=false` and with E024's EXCLUSION from the frozen 8-row
  recognition-landing set {E007,E022,E025,E026,E027a,E028b,E030,E033} — a primary recognition-landing
  typing would contradict both.
- **§9 relapse:** None. No "derive spacetime"; the join is a named top-down currency coupling,
  conditional, not a reduction.
- **E2 named import:** single coherent frozen principle (RT formula + holographic-entanglement
  program within AdS/CFT, E023); `import_hygiene_C13` asserts single principle / no menu. Acceptable
  (same structure as E005's two-part-but-single frozen import).
- **near-intra:** N/A.

### E028b — general_relativity → lambda_cdm (imported-content leg) — scored E2 / recognition-landing — **OK**
- **Tier forced:** Yes. Independently reproduced: with D0 (λCDM predictive content) on a block
  orthogonal to L0 (GR geometry), the Schur complement equals K_DD exactly ⇒ **xi_rel = 1.0**
  maximal and stable at both refinements; the over-read counterfactual (smuggle Λ/DM/measure into
  the source range) collapses xi_rel 1.0 → 0. Explicit non-factorization witness. All structural
  tests fail; a single named import closes it ⇒ recognition-landing tier-locked E2. E028b IS a
  frozen member of the 8-row set, so recognition-landing PRIMARY is required AND correct.
- **Xi real:** Yes — toy declared, two refinements, witness + counterfactual, both raw Ξ and xi_rel
  reported.
- **Primary modality:** recognition-landing (no structural test passes; required by membership and
  by the §B.7a residual clause). The §B.5 discriminator vs E005 is correctly applied: this is the UP
  arrow, so there is no GR-source-side shadow-price that descends and closes the imported content.
- **§9 relapse:** None — the load-bearing anti-reductionism check. The value of Λ is NOT derived
  (that is the E021 open gap); it is IMPORTED as named content. Only the DOWN descent is computed
  (and it fails, xi_rel=1.0); the UP arrow is certified as a gap, never run as a derivation.
  Asymmetry held. Bare-FLRW geometry descent is the SEPARATE E028a leg, never summed.
- **E2 named import:** "value of Λ + cold-dark-matter sector + initial-conditions/measure" —
  explicitly frozen as ONE import package, no menu; matches the CONTRACT import for E028b.
- **near-intra:** N/A.

### E034 — general_relativity → quantum-field-theory-curved — scored E2 / shadow-down (+recognition-conditional secondary) — **OK**
- **Tier forced:** Yes. Independently reproduced the two-leg structure: FORM leg (background
  geometry GR supplies to QFT-CS) xi_rel → ~machine-zero stable; VALUE leg (full semiclassical
  hbar/quantum readout: renormalized ⟨T_μν⟩, Hawking/Unruh flux) xi_rel stable-positive (~0.29 in
  the record) with analytic control; positive control (value-leg restricted to its geometry shadow)
  → machine-zero. Gate E.3 over-read discipline blocks E1; named QFT-in-curved-spacetime import
  closes it ⇒ E2. Refinement-stable, no flip.
- **Xi real:** Yes — declared two-block toy, two refinements, raw Ξ + xi_rel for both legs plus a
  positive control. Not asserted.
- **Primary modality:** shadow-down (the background geometry genuinely descends as a down-shadow) ⇒
  structural primary per precedence; recognition-conditional secondary because the E2 headline leans
  on the named import. E034 is correctly OUTSIDE the frozen 8-row recognition-landing set — typing it
  as a primary recognition-landing would break frozen CONTRACT membership. The (shadow-down, E2) cell
  is emittable per §B.8.
- **Arrow scrutiny:** QFT-CS is richer than classical GR, so one might suspect an up/down category
  error. Resolved correctly: the FORM that descends is the background GEOMETRY (GR → the fixed-
  background input layer of QFT-CS) — a genuine down-shadow; the hbar content is IMPORTED (E2), never
  claimed to descend and never run UP. No relapse.
- **§9 relapse:** None — arrow DOWN, form descends (runnable), quantum content named-imported and
  certified as gap, not derived. The full quantum-gravity boundary (E018) is not crossed.
- **E2 named import:** single frozen principle (the semiclassical QFT-in-curved-spacetime construction
  under no-back-reaction) — the same import E005 cites; C13-style hygiene noted.
- **near-intra:** N/A (`near_intra_layer_result=null`, correct — not a near-intra candidate).

### E039 — special_relativity → classical_electromagnetism — scored E1 / common-refinement — **OK**
- **Tier forced:** Yes. The structural common-third (F51) test passes — both layers' own readouts
  are machine-zero covariant (~1e-15, independently reproduced) under a shared third W = the
  Lorentz/Poincaré group; the bidirectional descent test confirms NEITHER layer coarse-grains to the
  other (xi_rel bounded away from zero and GROWING both ways). ⇒ common-refinement / E1 ("both legs
  descend" emittable cell). No named import needed (Maxwell covariance is internally checkable), so
  correctly NO recognition-conditional flag.
- **Xi real:** Yes — common-refinement covariance audit + bidirectional Schur descent, two
  refinements, machine-zero covariance residuals and stable-positive descent residuals both ways.
- **Primary modality:** common-refinement (structural) — correct.
- **§9 relapse (the load-bearing trap-1 check):** None. The record performs the LICENSED F51 move —
  locates the common THIRD (Lorentz group as a P2 covariance constraint) and AUDITS compatibility —
  rather than the forbidden "derive both from shared math" factorization. Both readouts are
  independently covariant; neither descends from the other. A join/recognition, not a reduction.
- **near-intra E.4 honesty (this edge's decisive gate):** route.json flags `near_intra=true`. The
  record RAN gate E.4/E.11 explicitly: SR Σ_f (interval/proper-time/invariant-mass/rapidity/causal-
  ordering/Lorentz tensors) and EM Σ_f (field strengths/radiation/Lorentz-force/polarization/
  impedance/refraction) are DISJOINT, accepted-observable sets DISJOINT, the only shared structure is
  the Lorentz GROUP (a covariance CONSTRAINT, not a shared readout), and removing the shared "Lorentz"
  name leaves a NON-VACUOUS residual relation ⇒ `near_intra_layer_result="passed"`. This honestly
  promotes the frozen E1-pending row to a sealed E1 (C9 satisfied). The "passed" is run, not asserted,
  and matches the F51 exemplar "SR as the common refinement under which E and B unify." OK.
- **E2 recognition:** N/A (E1, no import). Correct that no flag is carried.

---

## Cluster summary

| edge | scored tier | primary modality | verdict |
|---|---|---|---|
| E008  | E1 | shadow-down            | OK |
| E014  | E1 | shadow-down            | OK (cross-consistency) |
| E024  | E2 | currency-shadow-price | OK |
| E028b | E2 | recognition-landing   | OK |
| E034  | E2 | shadow-down           | OK |
| E039  | E1 | common-refinement     | OK |

**Hard fixes (records edited in place):** 0.
**Tier corrections:** 0.
**Modality corrections:** 0.

**Flag count (soft observations, no record edit):** 1 —
- **F1 (E008, mirrored at E014):** the FROZEN `edge_manifest.jsonl` carries a self-inconsistent
  `value_split` block for E008 (`reported_tier='E0'` alongside `headline_tier='E1'`). The scored
  record is CORRECT (reports E1 per the rubric §E.3 `form_value` carve-out for E004/E008/E035a/E038,
  with `value_split.reported_tier='E1'` = scored_tier) and already flags the manifest for correction.
  This is a **manifest** defect, not a scored-record defect; no edit to the scored record is
  warranted. (E014 derives the same `form_value` split fresh, consistent.)

**Honesty assessment:** all six typings are forced by audited tests, not fitted. The three E2 edges
each freeze exactly one non-menu named import and correctly distinguish primary recognition-landing
(E028b, in the frozen 8-row set) from structural-primary + recognition-conditional-secondary
(E024 currency, E034 descent — both correctly OUTSIDE the 8-row set, mirroring the E005 calibration
template). The E1 edges report real, declared, two-refinement Ξ computations with normalized
residuals (E008/E014 form→~0 with run-only values fenced to E0; E039 common-third covariance→~0 with
descent ruled out both ways). No §9 reductionist relapse found: no derive-across-a-boundary
(λ-value, RT geometry, hbar content, and matched couplings are all deferred/imported, never derived),
no within-a-layer scoring, and the up/down asymmetry is held on every edge (notably E028b's UP arrow
is certified as a gap and never run as a derivation). E039's near-intra E.4 gate is honestly run and
passed (disjoint Σ_f, non-vacuous residual), not asserted.
