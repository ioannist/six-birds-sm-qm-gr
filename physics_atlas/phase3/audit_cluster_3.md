# Phase-3 Adversarial Audit — Cluster 3

**Auditor role:** adversarial auditor for Phase-3 edge typings.
**Edges audited:** E009, E015, E025, E029, E035a, E040.
**Date:** 2026-06-04.
**Frozen authorities consulted:** anti-reductionism primer (§6 up/down asymmetry, §9 trap-checklist),
SCIENCE_DIGEST (Ξ = Schur complement, normalized relative residual `ξ_rel`, foreclosure v5,
recognition-landing), TYPING_RUBRIC §B (modality + precedence B.7a), §C (deterministic procedure,
C.7), §D.1.1 (`ξ_rel`), §E gates (E.3/E.4/E.7/E.8/E.9/E.11), §F calibration, and `CONTRACT.json`
(`recognition_resolution.affected_edges`, `value_split_schema.rows_carrying_value_split`,
`reported_tier_rule`, `headline_tier_invariant`/C10, `secondary_modality_schema`).

---

## Attack axes applied to every edge
(1) tier FORCED vs fitted; (2) for E1: Ξ computation REAL (toy declared, two refinements, normalized
residual → ~0) vs asserted/over-read; (3) PRIMARY modality correct per the B.7a precedence rule
(structural beats residual recognition); (4) §9 reductionist relapse (derive-across-layers,
score-within-a-layer, up/down symmetry); (5) E2 recognition: exactly ONE non-menu named_import frozen;
(6) near-intra E.4 honesty.

---

## Per-edge verdicts

### E009  rg_eft → relativistic_qft  (up; E3 / emergence-up) — **OK**
- **Tier FORCED.** The descent-test is correctly run as the *up-factorization* (can the UV readout be
  rebuilt from the IR lens?). `ξ_rel` is STABLE POSITIVE (0.372 → 0.063), pinned analytically on the
  UV-only / irrelevant block at full unit currency ~1.0 — a known nonzero lower bound, i.e. genuine
  non-factorization (two UV states with identical IR shadow differ in `g_irr`). Not E1.
- **Recognition honestly negative:** swampland (conjectures, not a selection principle) and the
  landscape (non-unique multiplicity) are correctly rejected as *not* a single named selector; no
  duality/common-refinement/currency/holonomy closes it. Not E2.
- **Run-search honestly negative and correctly demoting:** the UV completion is non-unique (many UV →
  one IR), so NO constructible run-object determines "the" completion. E0 is therefore *unavailable*
  (E.7: E0 needs a positively-constructed run-object); doubt at Step 3 demotes to E3 — exactly the
  conservative-default rule, and a sharp contrast with E001 (where the substrate *does* determine the
  value). Lands E3.
- **No §9 relapse.** Gate E.8 honored (no E1 via an up computation). The reverse control
  (Ξ(IR|UV) ~ machine-zero) confirms the legal arrow is the DOWN edge E008 — the up/down asymmetry is
  respected, not inverted. `value_split=null` matches the frozen manifest; the record's drift note
  honestly flags the stale `route.json has_value_split=true` as an over-eager mirror of E008.
- `(emergence-up, E3)` is emittable (B.8). No fix.

### E015  electroweak_theory → qed  (down; E1 / shadow-down) — **OK**
- **Ξ is REAL.** Declared finite Wilsonian-integrate-out toy M (heavy W/Z/H integrated out below
  v=246 GeV; photon = cos θ_W·B + sin θ_W·W³ as the kept unbroken U(1)_em). Two refinements,
  `ξ_rel = 1.17e-15 → 7.07e-14`, exact factorization `D0 = A·L0` verified True at both. Clean,
  refinement-stable descent (E.9 pass).
- **No over-read (E.3).** Recovered content is the unbroken-U(1)_em QED structure, in qed.Σ_f /
  accepted_observables; no ħ/thermal/external predicate imported (the E005 contrast is correctly
  invoked).
- **value_split=null is correct and matches frozen.** The only candidate value-leg (α via θ_W, v) is a
  DECLARED MEASURED INPUT on both cards → out of scope as an edge readout per C.7, not a fake E0/E2
  leg. The record even tested a candidate α value-leg (`ξ_rel ~ 5e-3..8e-3`, NOT a stable-positive
  run-only obstruction) and correctly declined to fence it.
- **PRIMARY modality correct:** structural descent passes → shadow-down primary (B.7a). E.4 passes
  (removing the RG relabeling leaves the computed heavy-mode-elimination + Weinberg-rotation relation).
  Both endpoints experimentally_established. No §9 relapse. No fix.

### E025  quantum_mechanics → thermodynamics  (down; E2 / recognition-landing) — **FIX:value_split → null (applied)**
- **Tier + primary modality CORRECT and FORCED.** Descent-test on the declared non-integrable Ising
  spin-chain toy gives `ξ_rel = 0.201 → 0.066` (stable positive, not machine-zero) → not E1. All
  structural modality tests (duality, common-refinement, currency/shadow-price, holonomy, emergence)
  are explicitly run and FAIL — so by B.7a step (2) recognition-landing is PRIMARY (residual), and it
  is tier-locked to E2. E025 is in `recognition_resolution.affected_edges`; this matches.
- **E2 recognition hygiene PASS:** exactly ONE non-menu named import frozen — the ETH ansatz on
  energy-eigenbasis matrix elements — matching the contract's frozen import for E025 (C11).
- **§9 over-read guard PASS:** S, T, k_B-as-physical are thermo-Σ_f predicates absent from QM-Σ_f; the
  record correctly refuses to read the small finite raw Ξ as a clean descent (the E005-style trap).
- **THE FLAW (fixed):** the record ADDED a `value_split` (`split_type=form_value_imported`, asserting
  an **E1 form-descent leg**) that is **not** sanctioned. (a) E025 is a PRIMARY recognition-landing
  edge; per rubric B.6a test (i) a recognition-landing requires that *no internal descent closes the
  edge*, so asserting an E1 "form descends" leg mis-characterizes a residual-by-construction
  recognition-landing as a structural form-descent — internal tension with its own modality. (b) E025
  is NOT in `CONTRACT value_split_schema.rows_carrying_value_split` (frozen list:
  E004/E008/E029/E035a/E038/E041; the canonical form_value_imported row is **E029 only**); the frozen
  edge_manifest row carries `value_split=null`. (c) the field even used a non-schema key `reported_leg`
  instead of `reported_tier`.
- **Resolution (does not weaken honesty):** reverted `value_split` to `null` (matching frozen) and
  recorded a `value_split_audit_note`. **Headline tier UNCHANGED (E2)** — the entire content of E025 IS
  the ETH import; there is no separate form-leg to fence. No tier correction.

### E029  qcd → chiral-perturbation-theory  (down; E2 / shadow-down + recognition-conditional secondary) — **OK**
- **Canonical R3 `form_value_imported` row, correctly executed.** FORM leg `ξ_rel → ~machine-zero`
  stably (6.9e-16, 2.2e-15) = clean symmetry-skeleton descent (E1). VALUE leg `ξ_rel` stable-positive
  (0.121 → 0.509) with analytic control (LEC magnitude on a block orthogonal to the symmetry span) →
  E1 BLOCKED for the predictive edge (E.3: f_π / condensate not closed-form QCD predicates). The raw Ξ
  growth (0.38 → 1.7) is correctly subordinated to `ξ_rel` (E001-anchor lesson).
- **PRIMARY modality correct per B.7a:** a STRUCTURAL test (descent) passes on the form leg →
  `primary_modality = shadow-down`; `recognition-conditional` is recorded as a SECONDARY flag (valid
  `secondary_modalities` value) because the E2 headline leans on a named import. Correctly NOT a
  primary recognition-landing — E029 is explicitly OUTSIDE `affected_edges` (confirmed). This is the
  precise discriminator the precedence rule encodes.
- **value_split matches frozen EXACTLY:** `form_tier E1 / value_tier E2 / form_value_imported /
  reported_tier E2`; `reported_tier = value_tier = scored_tier = E2` satisfies the headline_tier_invariant
  (C10). Exactly ONE named import frozen (run-generated LECs from lattice QCD), satisfying the C13
  secondary-flag hygiene. No §9 relapse (LECs explicitly imported, not derived; arrow DOWN). No fix.

### E035a  lattice-gauge-theory → qcd  (down; E1 / shadow-down) — **OK**
- **Ξ is REAL.** Declared finite lattice→continuum (a→0 line of constant physics) toy. FORM leg
  `ξ_rel = 2.7e-15 → 3.3e-14` stably → clean structural descent (E1), refinement-stable (E.9). No
  over-read: recovered content is gauge-invariant correlator STRUCTURE in qcd.accepted_observables.
- **`form_value` value_split matches the contract carve-out EXACTLY:** `form_tier E1 / value_tier E0 /
  form_value / reported_tier E0 / edge_scored_tier E1`. E035a IS on the frozen
  `rows_carrying_value_split` list; per the carve-out the edge's OWN closure is the structure descent
  (scored E1) while the run-only spectrum/Λ_QCD value-leg (= E035b/E001) is reported_tier E0, carried
  separately on the Run-Target ledger, never summed. This is the correct, contract-sanctioned use of
  `reported_tier ≠ edge_scored_tier`.
- Source `lattice-gauge-theory` is experimentally_established (gate R6 → may source an E1). Up/down
  asymmetry respected (E.8): the run-only scale is certified as an E0 gap, never derived. No fix.

### E040  many-body-quantum → fermi-liquid-theory  (down; E1 / shadow-down) — **FIX:value_split → null (applied)**
- **Tier + primary modality CORRECT and FORCED.** FORM leg `ξ_rel = 9.4e-16 → 2.0e-15` stably →
  clean RG-fixed-point quasiparticle structure descent (E1), refinement-stable (E.9). No over-read
  (m*, Landau parameters, zero sound, near-Fermi-surface transport in fermi-liquid-theory.accepted_observables).
  Source experimentally_established (R6). Structural descent passes → shadow-down PRIMARY (B.7a). E.4
  passes (O(ε²) irrelevant-coupling decay is the residual relation). The clean E1 is honest.
- **THE FLAW (fixed):** the record FABRICATED a `value_split` (`split_type=form_value`,
  `value_node=superconducting-gap-instability-order-parameter`) with **`reported_tier=E1`** — and
  mis-stated the carve-out membership as "E004/E008/E035a/E038/**E040**". This is invalid on two
  counts. (a) E040 is **not** in `CONTRACT value_split_schema.rows_carrying_value_split` (frozen list:
  E004/E008/E029/E035a/E038/E041); its frozen edge_manifest row carries `value_split=null`. (b) Even if
  a value_split were admitted, `reported_tier_by_split_type[form_value] = value_tier = E0`, so
  `reported_tier=E1` **violates the frozen reported_tier_rule** and would fail validator C10 (it
  silently reports the form-leg as the closure).
- **Resolution (does not weaken honesty):** reverted `value_split` to `null` (matching the frozen
  manifest) and recorded a `value_split_audit_note`. **Headline tier UNCHANGED (E1)** — the clean
  structural form-descent is the edge's audited closure. The run-only BCS/Pomeranchuk instability
  content is genuinely E0/E3, but it is a SEPARATE edge's concern (the record itself notes "a separate
  E3+E0 edge"), not a within-E040 value_split sanctioned by the contract; it remains described in the
  diagnostic prose, not double-counted. No tier correction.

---

## Cluster summary

| Edge | scored tier | primary modality | verdict |
|------|-------------|------------------|---------|
| E009  | E3 | emergence-up         | OK |
| E015  | E1 | shadow-down          | OK |
| E025  | E2 | recognition-landing  | FIX:value_split→null (applied) |
| E029  | E2 | shadow-down (+rec-cond secondary) | OK |
| E035a | E1 | shadow-down          | OK |
| E040  | E1 | shadow-down          | FIX:value_split→null (applied) |

- **Flag count: 2** (E025, E040) — both `value_split` hygiene fixes, applied in place.
- **Tier corrections: 0.** No headline tier changed; no modality changed. Both flags were fabricated /
  non-contract `value_split` fields that did not affect the edges' headline tiers (E025 stays E2 by the
  ETH import regardless; E040 stays E1 by the clean structural descent regardless).
- **No reductionist relapse found** in any of the six: no derive-across-layer, no score-within-a-layer,
  no up/down symmetry violation; the up edge (E009) correctly forecloses to E3 rather than being run as
  a derivation, and the recognition edge (E025) carries exactly one frozen non-menu named import.
- **Calibration consistency intact:** none of these six are calibration rows; the fixes touched only
  non-headline annotation fields, so no `calibration_known_tier` gate is disturbed.

**Files edited:**
`/home/repos/six-birds-papers/physics_atlas/phase3/scored/E025.json`,
`/home/repos/six-birds-papers/physics_atlas/phase3/scored/E040.json`.
