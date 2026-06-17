# Phase-3 Adversarial Audit — Cluster 1

> **SUPERSEDED-BY-MERGE NOTE:** where this pre-merge audit advice conflicts with the authoritative
> `phase3/scored_run/edge_manifest.jsonl` (esp. value-split handling and E017 status), the merged
> manifest governs. Specifically: the unregistered `value_split` objects this cluster discussed for
> **E013** (and any other row not in `CONTRACT.value_split_schema.rows_carrying_value_split`) are
> NOT authoritative — the merged manifest carries `value_split:null` for them, and the raw scored
> record has been renamed to `future_freeze_candidate_value_split` (a new freeze + Run-Target ledger
> entry would be required to register it). **E038**'s `value_split` is governed by the frozen contract
> (`reported_tier:"E0"`, headline `edge_scored_tier:"E1"` — non-conflicting per R3). For E017's
> status, see the merged manifest: it is within-a-layer/no-content, `scored_tier:"E3"` sentinel,
> excluded from the chargeable foreclosure count.

**Edges:** E007, E013, E023, E028a, E033, E038
**Auditor stance:** adversarial. Attack axes per task: (1) tier forced/honest vs fitted; (2) E1 Ξ real (toy declared, two refinements, normalized residual→~0); (3) primary modality correct per the precedence rule (structural beats residual recognition); (4) §9 reductionist relapse; (5) E2 recognition: exactly one non-menu named_import frozen; (6) near-intra E.4 honest.
**Cross-references used:** TYPING_RUBRIC §B.6a/§B.7/§B.7a (precedence), §B.8 (modality↔tier emittability), §C.5 (decision procedure), §D.1.1 (normalized ξ_rel), §E.3 (no-over-read / value_split / R3 reported_tier_rule), §E.4 (relabeling smuggle-audit), §E.9 (refinement stability), §E.11 (near-intra); CONTRACT.json `recognition_resolution.affected_edges` (the 8 frozen recognition-landing rows = {E007,E022,E025,E026,E027a,E028b,E030,E033}), `value_split_schema.rows_carrying_value_split` (= {E004,E008,E029,E035a,E038,E041}), `modality_tier_compat`; node registry (`classical-probability`, `conformal-field-theory` = candidate_substructure / not_established; `phase-transitions-universality` = observable_readout).

---

## E007 — quantum_mechanics → classical-probability (Born rule) — **VERDICT: OK**

- **Tier forced/honest (E2).** Frozen recognition-landing row (in CONTRACT affected_edges). Descent test run on a faithful finite M (d=3,4; Gleason needs dim≥3 so d=3 is the minimal stage). ξ_rel = 1.0000 *stable* at both refinements — a *maximal* stable-positive normalized residual with analytic control: (d−1)/d of the outcome-weight currency lies outside the pre-measure native range, only the normalization-fixed weight is captured. Descent honestly fails → not E1. Explicit non-factorization witness (ρ_a, ρ_b diagonal, identical on every pre-measure source probe, different Born weights) confirms B.2 non-definability. **Forced, not fitted.**
- **Over-read discipline (the load-bearing check).** The record builds the over-read counterfactual: importing the diagonal-projector/Gleason functionals into L0 collapses ξ_rel 1.0→~0 (raw Ξ ~5e-16). It correctly reads this as the E005-lesson over-read (the E1 "success" is unavailable without smuggling Gleason in), so E1 is refused. Honest.
- **Primary modality (recognition-landing) correct per precedence.** All structural tests (B.1 descent / B.3 duality / B.4 common-refinement / B.5 currency / B.6 holonomy) are explicitly run and FAIL/NA; with no structural test passing and the named import being the entire landing mechanism, B.7a clause (2) makes recognition-landing PRIMARY (residual-by-construction). tier-locked to E2 per B.8. Correct.
- **E2 named import (exactly one, non-menu).** Single frozen import = **Gleason's theorem** under noncontextuality + dim(H)≥3. envariance (Zurek) and decision-theoretic (Deutsch–Wallace) recorded as `alternatives_not_used`, NOT contract imports, not substitutable at typing time (gate E.0). Matches the frozen edge_manifest single import. C11 hygiene clean.
- **§9 relapse?** None. No cross-layer derivation (named the import, not a factorization); Born weights confirmed non-definable, not derived; asymmetry respected (only the DOWN descent run, it failed); near_intra=false correctly (distinct Σ_f). Self-audit runs the full checklist.
- **value_split.** null. E007 is NOT in rows_carrying_value_split — correct (the decoherence/dephasing form leg is a *separate* edge, not an intra-edge split). The record correctly supersedes route.json's coarse `has_value_split=true` pre-flag.

**No fix.**

---

## E013 — statistical_mechanics → brownian_langevin (Mori-Zwanzig / Caldeira-Leggett) — **VERDICT: OK**

- **E1 Ξ real.** Toy declared before computation (finite Caldeira-Leggett linear system–bath, slow heavy-particle + Nb oscillators). FORM-leg ξ_rel → ~machine-zero stably (Nb=6: 3.5e-16; Nb=24: 1.0e-15) with explicit ker-containment (form probe norm outside slow span = 0.00). Two genuine refinements (more bath modes). Real computation, not asserted.
- **No-over-read.** E.3 honest: the recovered answer (slow velocity/position response, MSD/diffusion structure) lies in `brownian_langevin.accepted_observables`; the non-descending bath-spectral combination Σ c_j x_j is fenced OUT to the E0 value-leg, not claimed by the E1 leg. The VALUE-leg over-read toy is independently run (ξ_rel ~4.2e-4 stable-positive, raw Ξ grows 0.59→1.85 while normalized stays a positive floor) — a correct E001-style demonstration that the verdict reads ξ_rel, and that the friction-kernel/diffusion VALUE is genuinely run-only (E0).
- **Primary modality (shadow-down) correct.** Structural descent (B.1) passes on the form leg → PRIMARY by B.7a clause (1). Not a recognition-landing (fluctuation-dissipation is the layer's own stated closure premise, not an imported external principle). is_recognition=false. (shadow-down, E1) emittable per B.8. Correct.
- **§9 relapse?** None. One-directional DOWN shadow, not a peer-factorization; the run-only value is fenced/deferred, never derived; asymmetry held. near_intra=false honest (distinct lens/Σ_f, genuine slow-variable quotient — E.4 residual present).
- **value_split — ENRICHMENT, NOT a firewall violation.** E013 is NOT in CONTRACT `rows_carrying_value_split`, and the frozen edge_manifest E013 row has `value_split:null`. The scored record ADDS a `{form_tier:E1, value_tier:E0, split_type:form_value, value_node:friction-kernel-diffusion-coefficient}` split. Checked against the validator: CHECK 6 only cross-checks rows present in `frozenRows`; E013 is absent there, so the added split is not rejected, and it avoids the forbidden E1+E1 collapse (form E1 / value E0). The headline tier stays E1; the E0 leg is a separate never-summed Run-Target entry. route.json carried `has_value_split=true`, and the record discloses the divergence from the manifest row transparently in drift_vs_provisional. This is a positively-exhibited, schema-conforming, never-summed value-split — honest, not flattering (it ADDS an E0 deferral, it does not pad E1). **Permitted.**

**No fix.** (Note for the assembler: E013 now carries a value_split absent from the frozen CONTRACT `rows_carrying_value_split` set. It is schema-valid and never-summed, but if the assembler enforces `rows_carrying_value_split` as a *closed* set, E013 should be added to it OR the split dropped to a Run-Target note. Soft flag, not a tier issue.)

---

## E023 — conformal-field-theory ↔ general_relativity (AdS/CFT) — **VERDICT: OK**

- **Tier forced/honest (E2).** Duality test (B.3: Ξ=0 required in BOTH directions) run on a declared finite toy (dimZ 10→20). ξ_rel stays stably POSITIVE both ways (D|L: 0.82→0.74; L|D: 0.66→0.64) — the conjectured dictionary is NOT a both-ways Ξ=0 bijection on the full finite content. Positive control (restrict both sides to the shared dictionary block) closes to ~1e-15 both ways, certifying the cross-residual is the genuinely unmatched content, not a numerical artifact, and that WITH the named import the relation lands → the exact E2 signature. Refinement-stable, no flip. Forced. CFT is not_established and may not source E1 regardless — a second independent reason E1 is barred.
- **Primary modality (duality-equivalence) correct per precedence — and correctly NOT placed in the recognition-landing set.** A structural test is *identified* as primary (duality-equivalence, the rubric's own AdS/CFT exemplar) even though the closure lands E2 via a named import; per B.7a clause (3), `recognition-conditional` is recorded as a SECONDARY flag, not as primary recognition-landing. This is the E005-template (structural primary + recognition-conditional secondary). The record explicitly refuses to put E023 in the frozen primary recognition-landing set {E007,E022,...,E033} — correct, since CONTRACT membership does not include E023, and mis-typing a structurally-identified duality as residual recognition would violate the frozen contract. (duality-equivalence, E2) is an emittable cell per modality_tier_compat. Correct.
- **E2 named import (exactly one, non-menu).** Single frozen import = the **Maldacena holographic dictionary** (gauge-gravity duality), under the stated closure assumption that AdS/CFT holds. "Proven only in special cases" is a *descriptive qualifier of the one principle*, not an alternation (C13 hygiene noted). Clean.
- **§9 relapse?** None. Unification treated as a join/recognition, no factorization φ claimed; duality is symmetric, neither arrow run as a derivation; near_intra=false honest (distinct Σ_f, deleting the dictionary leaves a positive residual both ways → E.4 passes); foreclosure-as-working held.
- **value_split.** null — correct. E023 is NOT in rows_carrying_value_split; form and value close at the SAME E2 tier via the SAME single import; no clean E1 form-descent leg and no pre-frozen E0 run-target stub, so none of the three split_types applies. Reasoning explicit and correct.

**No fix.**

---

## E028a — general_relativity → lambda_cdm (FLRW form leg of the O1 split) — **VERDICT: OK**

- **E1 Ξ real.** Toy declared (cosmological-principle quotient on a finite GR curvature carrier; iso/FLRW sector vs aniso/shear/GW sector). FORM-leg ξ_rel → ~machine-zero stably (h1 4.11e-16, h2 2.84e-15) AND seed-robust (1e-15 across 4 seeds → structural, not numerical accident). Two refinements (nmodes_aniso 4→16). Real.
- **No-over-read (the load-bearing self-audit).** E.3 honest and explicitly stress-tested: the dissolving probe is scoped to the FLRW geometric form ONLY (background a(t), Hubble, Friedmann combination), all in `lambda_cdm.accepted_observables`. The Λ value, dark-matter sector, initial-conditions/measure, and anisotropic-shear/GW curvature are EXCLUDED, and an explicit over-read CONTRAST probe (full GR curvature) correctly REFUSES to descend (ξ_rel 0.29→0.99 stable-positive, growing). This is exactly the demonstration that distinguishes a true form-descent from a silent drop of imported predicates. Honest.
- **No smuggle of the imported content.** The Λ/dark-matter/measure content lives on the SEPARATE sibling row **E028b** (recognition-landing, E2, the frozen named import), carried on a separate ledger and never summed. The O1 two-row split is respected; E028a does not over-read.
- **Primary modality (shadow-down) correct.** Structural descent (B.1) passes → PRIMARY per B.7a clause (1). named_import=null, no recognition-conditional secondary flag (correct: this leg imports nothing; the import is E028b's job). (shadow-down, E1) emittable. Correct.
- **§9 relapse?** None. Single DOWN descent (not a unification); NO constant derived (Λ value explicitly excluded, deferred to E028b/E021); asymmetry held (GR casts the FLRW shadow, not FLRW reducing up to GR); near_intra=false honest (distinct Σ_f, genuine quotient, E.4 passes).
- **value_split.** null — correct. The O1 split already separates form (E028a/E1) from content (E028b/E2) as two rows rather than an intra-row split.

**No fix.**

---

## E033 — classical_mechanics → thermodynamics (H-theorem) — **VERDICT: OK**

- **Tier forced/honest (E2).** Frozen recognition-landing row (in CONTRACT affected_edges). Descent test run on a declared finite reversible toy (volume-preserving invertible permutation = finite Liouville/symplectic analogue). The decisive 2nd-law test: under the reversible flow the fine Gibbs entropy is EXACTLY conserved and the coarse entropy is NON-monotone / Poincaré-recurrent (2nd-law violation 0.65→0.57) — the monotone dS≥0 predicate is NOT in classical_mechanics.Σ_f and does not factor through the reversible lens. Importing molecular chaos → doubly-stochastic Markov step → H-theorem (violation→0 at both refinements). Stable, no flip. Forced.
- **Over-read discipline (excellent).** A naive linear-Schur ξ_rel on the {fine,coarse}-entropy family is SMALL and SHRINKING (0.060→0.0012) — the record explicitly flags this as an OVER-READ (E005 lesson): it captures only the conserved fine entropy and the non-monotone coarse entropy while silently dropping the monotone 2nd-law predicate that is the entire point of the edge. It correctly reads the descent verdict against the FULL target content (monotonicity), where the descent plainly fails, and refuses E1. This is the most important honesty move in the cluster and it is handled correctly.
- **Primary modality (recognition-landing) correct per precedence.** All structural tests run and fail: descent (Step 1), B.3 duality (thermo strictly coarser/irreversible), B.4 common-third (none without the very import), B.5 currency (missing thing is a statistical-independence assumption, not a dual price), B.6 holonomy (canonical transforms preserve the bracket, RM=0). With NO structural modality and the named import as the entire mechanism, B.7a clause (2) → recognition-landing PRIMARY, tier-locked E2. Correct.
- **E2 named import (exactly one, non-menu).** Single frozen import = the **Stosszahlansatz** (molecular chaos / pre-collision independence) under the dilute-gas closure assumption. Matches the frozen edge_manifest single import. Load-bearing (E.4 removal test: remove it → monotone relation vanishes). C11 hygiene clean.
- **§9 relapse?** None. Did not derive thermo from reversible mechanics (located the gap, named the import); asymmetry held (foreclosed DOWN-descent landing by recognition, not a run UP-arrow); near_intra=false honest.
- **value_split.** null — correct. E033 is NOT in rows_carrying_value_split; the entire edge content IS the import (recognition-landing), no genuine form/value tier split. route.json `has_value_split=true` correctly not realized.

**No fix.**

---

## E038 — statistical_mechanics → phase-transitions-universality (RG / universality) — **VERDICT: FIX (applied) — schema-conformance + false-accusation correction; tier UNCHANGED (E1)**

- **E1 Ξ real.** Toy declared (finite block-spin / linearized-RG; 2 relevant directions fixed, irrelevant directions wash out; relevant subspace non-axis-aligned via fixed orthogonal mixing). FORM-leg framing B ξ_rel → ~machine-zero stably (7.2e-16 → 2.0e-16) across two refinements (irrelevant couplings 3→8). Over-read control framing A (reconstruct ALL microscopic couplings) gives ξ_rel=1.0 stably — universality genuinely does NOT over-read the microdata; irrelevant couplings are its blind spot. E.3 honest. Real computation. Source `statistical_mechanics` is experimentally_established (may source E1); target `phase-transitions-universality` is observable_readout (target-only, inherits casting) — E1 licensing correct.
- **Primary modality (shadow-down) correct.** Structural descent (B.1) passes → PRIMARY per B.7a clause (1); no named import for the form leg. (shadow-down, E1) emittable. Correct.
- **value_split — was NON-CONFORMING; FIXED.** The frozen CONTRACT row registers E038 with `{split_type:form_value, reported_tier:"E0", edge_scored_tier:"E1"}`. Under the R3 `reported_tier_rule`, `reported_tier_by_split_type[form_value]=value_tier` → reported_tier names the value-leg (E0, the run-only exponent values on the Run-Target ledger), while `edge_scored_tier` (E1) is the edge's audited headline closure. **These are not in conflict** — they are the two distinct fields the schema requires, and validator CHECK 10 enforces exactly this pairing.
  - **The error:** the scored record (a) replaced the schema field `reported_tier` with a non-schema field `reported_leg:"form_tier (E1)"`, omitting `reported_tier`/`edge_scored_tier`; and (b) **falsely accused the frozen manifest/CONTRACT of an "internal inconsistency" / "stale/erroneous carry-over"** (in both the value_split note and drift_vs_provisional). The frozen row is correct; the record mis-read the schema. The headline tier itself (E1) was already right, so this is a schema/interpretation fix, not a tier change.
  - **Fix applied (in place):** value_split now carries the schema-conforming `reported_tier:"E0"` + `edge_scored_tier:"E1"`, with a note explaining the two fields are non-conflicting per R3; drift_vs_provisional rewritten to retract the false accusation and confirm the frozen value_split is reproduced verbatim. No weakening of honesty — the E0 value-leg deferral and the never-summed discipline are preserved; the headline E1 form-descent is unchanged.

**FIX: value_split schema-conformance (reported_tier='E0', edge_scored_tier='E1') + retract false "stale/erroneous" accusation against the frozen CONTRACT row. Tier UNCHANGED at E1.**

---

## Cluster summary

| Edge | scored_tier | primary modality | Verdict |
|------|-------------|------------------|---------|
| E007 | E2 | recognition-landing | OK |
| E013 | E1 | shadow-down | OK (soft note: value_split not in frozen rows_carrying_value_split set; schema-valid, never-summed) |
| E023 | E2 | duality-equivalence (+ recognition-conditional secondary) | OK |
| E028a | E1 | shadow-down | OK |
| E033 | E2 | recognition-landing | OK |
| E038 | E1 | shadow-down | FIX applied (value_split schema-conformance + false-accusation retraction); tier UNCHANGED |

- **Hard fixes applied:** 1 record (E038) edited in place. **No tier corrections** — all six scored tiers were forced/honest and survive the attack; the E038 fix is schema-conformance + an honesty correction (the record had wrongly impugned the frozen contract), not a tier demotion.
- **Soft flags (no edit, for assembler):** 1 — E013 carries a value_split absent from the frozen CONTRACT `rows_carrying_value_split` set (E004/E008/E029/E035a/E038/E041). It is schema-valid (form E1 / value E0, never summed) and disclosed; the assembler should decide whether to register E013 in that set or demote the split to a Run-Target note.
- **E1↔E2/E0/E3 summing:** clean throughout. Every E0 value-leg (E013, E038) is on a separate never-summed ledger; every E2 is reported as conditional and never summed with E1.
- **Over-read discipline (the cluster's central honesty axis):** correctly handled on all three edges where it is load-bearing — E007 (Gleason import collapses Ξ → over-read refused), E033 (small naive ξ_rel drops the monotone 2nd-law predicate → over-read refused), E028a (over-read contrast probe refuses to descend). No E005-style silent predicate-drop survives.

**Flag count for the cluster: 2** (1 hard fix applied = E038; 1 soft flag = E013 value_split membership). **Tier corrections: 0.**
