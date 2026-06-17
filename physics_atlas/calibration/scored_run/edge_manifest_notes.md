# Edge Manifest — Notes (Physics Layer Atlas, Stage 1, FROZEN)

**Artifact:** `edge_manifest.jsonl` — **46** inter-theory edges (42 original + the E027/E035/E028 splits
required by review fixes #6 and O1 + the O3 hierarchy edge E043). **Status:** FROZEN. Tier values in
`provisional_tier_guess` are the honest
**PRE-AUDIT GUESS**, NOT the audited verdict; the audited tier of every non-calibration edge must still
be *forced* by the typing rubric's deterministic foreclosure decision-procedure (descent-test → Ξ on a
declared finite toy, refinement-stable per E.9 → recognition-search for a NAMED principle → run-only
check → else E3). Nothing here is "decisive"; everything is "conditional on the audited casting."

## 1. The FROZEN id-alias table (review fix #1 — the blocker)

The theory cards (`theory_manifest.jsonl`) are the frozen layers and use **snake_case** ids; those are
**canonical**. Every edge endpoint that names a peer theory has been rewritten to the canonical card id.
The 6 *renamed* peers (not merely re-cased) plus the EFT/Brownian reconciliations:

| edge endpoint (old kebab) | canonical card id | kind of change |
|---|---|---|
| `quantum-chromodynamics` | `qcd` | rename |
| `quantum-electrodynamics` | `qed` | rename |
| `electrodynamics` | `classical_electromagnetism` | rename |
| `navier-stokes` | `hydrodynamics` | rename |
| `condensed-matter` | `condensed_matter_spt` | rename |
| `lambda-cdm-cosmology` | `lambda_cdm` | rename |
| `effective-field-theory` | `rg_eft` | node→card promotion (fix #2(iii)/O3) |
| `brownian-motion` | `brownian_langevin` | node→card reconciliation |
| `general-relativity` → `general_relativity`, `quantum-mechanics` → `quantum_mechanics`, `statistical-mechanics` → `statistical_mechanics`, `relativistic-qft` → `relativistic_qft`, `classical-mechanics` → `classical_mechanics`, `special-relativity` → `special_relativity`, `electroweak-theory` → `electroweak_theory`, `newtonian-gravity` → `newtonian_gravity`, `kinetic-theory` → `kinetic_theory`, `geometrical-optics` → `geometrical_optics`, `black-hole-thermodynamics` → `black_hole_thermodynamics`, `standard-model` → `standard_model`, `thermodynamics`/`hydrodynamics` (already match) | (re-case only) | re-case |

**Freeze-time assertion (enforced):** every edge `source_theory_id` / `target_theory_id` is **either**
a frozen theory-card id **or** a frozen registered node id of declared `node_kind` (§2). The bundle may
not freeze while any endpoint is unresolved. (Verified: all 46 edges × 2 endpoints resolve.)

## 2. The FROZEN non-peer Node Registry (review fix #2 — the second blocker)

Non-peer endpoints are **registered, frozen nodes** with a declared `node_kind`, NOT cards. They may not
be cast on the fly (that was the smuggling surface). Each edge row also carries machine-checkable
`source_kind` / `target_kind` fields. **Three `node_kind`s** and their §C.5-STEP-0 constraints:

| `node_kind` | members | allowed role |
|---|---|---|
| `observable_readout` | `hadron-spectrum`, `confinement`, `turbulence`, `arrow-of-time`, `measurement-outcome`, `phase-transitions-universality`, `singularity-theorems`, `berry-phase-holonomy`, `entanglement-geometry`, `spt-phases` | TARGET only; **inherits the source card's frozen casting**; no fresh casting |
| `open_question` | `gauge-group-origin`, `fermion-generations`, `cosmological-constant`, `electroweak-hierarchy` | TARGET only; **forces the E0/E3 branch**; can NEVER seal E1/E2 |
| `candidate_substructure` | `conformal-field-theory`, `string-theory`, `lattice-gauge-theory`, `quantum-field-theory-curved`, `chiral-perturbation-theory`, `fermi-liquid-theory`, `decoherence-pointer-basis`, `classical-probability`, `many-body-quantum` | source or target; if NOT experimentally established, may **NOT source an E1 descent** |

> Note: `spt-phases` is classified `observable_readout` (the topological invariant / realized-phase
> readout of a `condensed_matter_spt` Hamiltonian). The former un-carded `effective-field-theory` node
> is gone — reconciled to the `rg_eft` card (E008/E009). The `electroweak-hierarchy` open_question node
> is added by review fix O3 (the Higgs-sector naturalness gap, edge E043), kept distinct from the
> fermion-generations gap `fermion-generations` (E020).

### 2.1 The FROZEN `established_status` / `may_source_E1` node registry (review fix R6)

Every registered node carries a machine-readable **`established_status` ∈ {`experimentally_established`,
`not_established`}** and the derived **`may_source_E1`** flag (rubric §A.7.1 / `CONTRACT.json`
`node_established_rule`). **Rule:** a node may be the SOURCE of an E1 (computable-descent) edge **only if**
`established_status == experimentally_established`. Theory cards are trivially `experimentally_established`
and may source E1; this table fixes the NON-card nodes. `observable_readout` and `open_question` nodes are
TARGET-only by `node_kind`, so `may_source_E1` is `false` for them regardless of status; they are marked
`not_established` because, as readouts / open questions, they are not established peer *layers* that close
and descend.

| node | `node_kind` | `established_status` | `may_source_E1` | justification |
|---|---|---|---|---|
| `lattice-gauge-theory` | candidate_substructure | **experimentally_established** | **true** | standard validated computational formulation of QCD; sources the E035a E1 continuum-limit descent (R6-cleared) |
| `many-body-quantum` | candidate_substructure | **experimentally_established** | **true** | interacting many-body quantum matter is experimentally realized; sources the E040 E1 Fermi-liquid descent (R6-cleared) |
| `fermi-liquid-theory` | candidate_substructure | experimentally_established | true (n/a — only a target here, E040) | Landau Fermi-liquid is an experimentally confirmed low-energy description of normal metals |
| `chiral-perturbation-theory` | candidate_substructure | experimentally_established | true (n/a — only a target here, E029) | ChPT is a confirmed low-energy EFT of QCD; appears only as a TARGET (E029), not an E1 source |
| `conformal-field-theory` | candidate_substructure | not_established | **false** | as a free-standing inter-layer source it is not an established peer layer; appears only in E2 duality (E023/E024) |
| `string-theory` | candidate_substructure | not_established | **false** | no accepted observables; candidate UV completion only; sources E3 (E037), never E1 |
| `quantum-field-theory-curved` | candidate_substructure | not_established | **false** | semiclassical named construction; appears as an E2 target (E034), never an E1 source |
| `decoherence-pointer-basis` | candidate_substructure | not_established | **false** | the selection criterion is itself an imported principle (E026 E2); not an E1 source |
| `classical-probability` | candidate_substructure | not_established | **false** | target of the Born-rule recognition landing (E007 E2); not an E1 source |
| `hadron-spectrum` | observable_readout | not_established | false | a run-only readout (E001/E035b), not an established peer layer; TARGET-only |
| `confinement` | observable_readout | not_established | false | run-exhibited phenomenon / open Clay theorem (E041); TARGET-only |
| `turbulence` | observable_readout | not_established | false | run-only readout (E031); TARGET-only |
| `arrow-of-time` | observable_readout | not_established | false | recognition-landing target (E030); TARGET-only |
| `measurement-outcome` | observable_readout | not_established | false | open gap target (E032); TARGET-only |
| `phase-transitions-universality` | observable_readout | not_established | false | RG-descent readout (E038); TARGET-only |
| `singularity-theorems` | observable_readout | not_established | false | self-incompleteness readout (E042); TARGET-only |
| `berry-phase-holonomy` | observable_readout | not_established | false | holonomy readout (E036); TARGET-only |
| `entanglement-geometry` | observable_readout | not_established | false | currency/shadow-price readout (E024); TARGET-only |
| `spt-phases` | observable_readout | not_established | false | SPT classification/realized-phase readout (E027a/E027b); TARGET-only |
| `gauge-group-origin` | open_question | not_established | false | open question (E019), forces E0/E3; TARGET-only |
| `fermion-generations` | open_question | not_established | false | open question (E020), forces E0/E3; TARGET-only |
| `cosmological-constant` | open_question | not_established | false | open question (E021), forces E0/E3; TARGET-only |
| `electroweak-hierarchy` | open_question | not_established | false | open question (E043, O3), forces E0/E3; TARGET-only |

**R6 outcome:** the only two `candidate_substructure` nodes that actually SOURCE an E1 descent —
`lattice-gauge-theory` (E035a) and `many-body-quantum` (E040) — are both honestly
`experimentally_established`, so **no E1 guess is demoted/unsealed on R6 grounds**. Every other
`candidate_substructure` is `not_established` and is consistently confined to E2/E0/E3 roles, matching the
edge tiers (E037 string→SM E3; E023/E024/E034 E2; E007/E026 E2 targets).

## 3. Calibration edges (`is_calibration=true`) — KNOWN answers, FREEZE-BLOCKERS (review fix #7)

**9 calibration edges**: 5 known-tier controls + 4 E3 anti-controls. Each carries a machine-checkable
`calibration_known_tier`; the anti-controls also carry `calibration_rule:"must_not_seal_E1_or_E2"`.

| id | edge | `calibration_known_tier` | rule | role |
|----|------|--------------------------|------|------|
| E001 | qcd → hadron-spectrum | **E0** | must_seal_E0 | the resolved emergent constant (proton mass); the no-shortcut anchor |
| E002 | statistical_mechanics → thermodynamics | **E1** | must_seal_E1 | textbook coarse-graining; Ξ=0 control |
| E003 | special_relativity → classical_mechanics | **E1** | must_seal_E1 | clean v/c→0 limit-descent (Wigner–İnönü) |
| E004 | kinetic_theory → hydrodynamics | **E1** | must_seal_E1 | Chapman–Enskog descent control (eqns E1; coeffs value_split E0) |
| E005 | general_relativity → black_hole_thermodynamics | **E2** | must_seal_E2 | the named-import control; FROZEN import = QFT-in-curved-spacetime + first law of BH mechanics (= E034). NOT Jacobson. |
| E018 | quantum_mechanics → general_relativity | **E3** | must_not_seal_E1_or_E2 | anti-control: any E1/E2 = "unify by deriving both" |
| E019 | standard_model → gauge-group-origin | **E3** | must_not_seal_E1_or_E2 | anti-control: any E1/E2 = "derived the gauge group" |
| E020 | standard_model → fermion-generations | **E3** | must_not_seal_E1_or_E2 | anti-control: any E1/E2 = "derived generations/hierarchy" |
| E021 | general_relativity → cosmological-constant | **E3** | must_not_seal_E1_or_E2 | anti-control: any E1/E2 = "predicted Λ" (retro R025 synthetic) |

**Freeze-gate predicate:** FREEZE iff (a) every `must_seal_*` row's computed tier == its
`calibration_known_tier`, AND (b) every `must_not_seal_E1_or_E2` anti-control's computed tier ∈ {E3, E0},
AND (c) every endpoint resolves and every (modality,tier) pair is emittable (rubric §B.8). The Assemble
phase must enforce this programmatically (review fix #7).

### 3.1 Pause-2 (calibration) remediation — E005 modality precedence (R-P2)

Pause-2 calibration **PASSED on tier** (all 9 blind tiers matched the known answers); the only block was a
**MODALITY-label ambiguity on E005** (GR → black-hole-thermodynamics). Adjudicated per
`EXTERNAL_REVIEW_PAUSE2.md`, resolution option (b) = **primary + secondary modality with a precedence
rule** (`CONTRACT.json` `modality_precedence_rule`):

- **E005 PRIMARY modality = `currency-shadow-price`** (the existing `provisional_modality_guess` field is
  the primary; **NOT renamed**), tier **E2** unchanged. The structural rubric-B.5 exemplar "surface
  gravity as the *price* in black-hole thermodynamics" passes, so the **structural** modality is primary —
  E005 is **not** a primary `recognition-landing`.
- **E005 SECONDARY flag = `recognition-conditional`** (`secondary_modalities` / `conditionality_flags`),
  recorded because classical GR's Ξ≈0 is an **over-read** (the ħ/thermal predicates are imported, not in
  GR's Σ_f). The secondary flag is a descriptive residual annotation only: **never** emittability-checked,
  **never** counted in the registered null. E005 is counted **once**, at `currency-shadow-price`/E2.
- **Named import FROZEN** at declaration (single principle, not a menu): **QFT-in-curved-spacetime
  (Hawking thermal flux) + the first law of black-hole mechanics, semiclassical no-back-reaction** (= the
  E034 construction; E005 cites E034 as its named source). Import-hygiene on the secondary
  recognition-conditional flag is enforced by validator check **C13** (the C11 parallel for secondary
  flags). Jacobson is **not** this edge (that is E022, the opposite-arrow primary recognition-landing).
- **Gate policy:** calibration hard-gates on **TIER only**; a blind-vs-frozen **primary**-modality
  mismatch is routed to **adjudication** (recorded, scored gate re-run), not auto-failed. The blind E005
  record sealed `recognition-landing`/E2 (right tier, under-applied the structural-is-primary precedence);
  this is recorded as the adjudication, not silently force-aligned.

> **DEFERRED to Phase 3:** the precedence re-exam of the **other** recognition-landing rows (E007, E022,
> E025, E026, E027a, E028b, E030, E033) — i.e. whether any carries a structural primary modality with
> recognition-conditional as a secondary flag (as E005 now does) rather than a primary
> `recognition-landing` — is **DEFERRED to Phase-3 scoring**. At this freeze those 8 rows keep their
> primary `recognition-landing` modality as-is (the Pause-2 remediation is **surgical to E005 only**).

### 3.2 Pause-2 — E001 Ξ reporting: raw vs NORMALIZED residual (R-P2)

E001 (the E0 anchor) now reports **BOTH** the **raw Ξ** and the **NORMALIZED relative residual**
`ξ_rel := ‖Ξ‖/‖K_DD‖` at each refinement (`CONTRACT.json` `normalized_xi_criterion`; scored record
`calibration/scored/E001.json` field `E0_basis_normalized_residual`):

| refinement | raw Ξ | K_DD | normalized ξ_rel |
|---|---|---|---|
| h1 (6 g0-samples, K=3) | 7.84e8 | 3.97e9 | **0.197** |
| h2 (12 g0-samples, K=6) | 2.25e9 | 5.34e10 | **0.042** |

The **raw Ξ GROWS** (7.84e8 → 2.25e9) under refinement, but the **normalized ξ_rel SHRINKS** (0.197 →
0.042) **while staying POSITIVE** — bounded away from the analytic **machine-zero control** (an analytic
polynomial target descends to ξ_rel ~ 1e-14 at both refinements). **E001's E0 seal rests on the stable
positive NORMALIZED residual + analytic machine-zero control, NOT on raw Ξ growth.** The E.9
refinement-stability check is read on **ξ_rel**, not on raw Ξ; a growing raw Ξ is not disqualifying and a
small raw Ξ is not sufficient for E1. (Contrast E005: a *small* raw Ξ with imported ħ/thermal predicates
is the canonical **over-read**, not a clean E1 — E001 is the *stable-positive-normalized-residual*
example, E005 the *over-read* example.)

## 4. The E027 and E035 splits (review fix #6 — modality/tier consistency)

The draft carried two rows whose (modality, tier) pair the deterministic procedure cannot emit; each is
split so neither violates the §B.8 emittability table or gate E.7:
- **E035** (`shadow-down E0` — NOT emittable) → **E035a** continuum-limit *structure* (`shadow-down`,
  **E1**-candidate) + **E035b** physical *readouts* (`emergence-up`, **E0**, run-only on the lattice
  carrier; the mechanism behind E001).
- **E027** (`emergence-up E0` but with a *positive* recognition candidate, violating E.7) → **E027a** SPT
  *classification* (`recognition-landing`, **E2**, named group-cohomology import) + **E027b** realized
  phase of a *specific* Hamiltonian (`emergence-up`, **E0**, run-only invariant value).

After the splits, **all four E0 rows are `emergence-up`** (E001, E027b, E031, E035b) — the non-emittable
`shadow-down E0` pair is eliminated.

## 5. New per-edge fields added by the fixes

- `source_kind` / `target_kind` (fix #2): the node_kind of each endpoint (`theory_card` or one of the
  three node_kinds).
- `calibration_known_tier` / `calibration_rule` (fix #7): machine-checkable known answer.
- `value_split` (fix #8(i), generalized by R5 with `split_type ∈ {form_value, form_value_imported,
  theorem_run}`): `{form_tier, value_tier, split_type, value_node, reported_tier}` for edges whose *form*
  and *value* (or theorem-status and run-exhibited phenomenon) close at different tiers — the
  non-reported leg is carried separately (into the Run-Target Manifest when E0, the conditional ledger
  when E2), **never summed**. Rows carrying a value_split: **E004, E008, E029, E035a, E038, E041** (6
  rows). **No current E028 value-split row** — review fix O1 superseded the old single E028
  `form_value_imported` value_split with the two-row **E028a** (shadow-down E1, FLRW geometry) / **E028b**
  (recognition-landing E2, imported Λ/dark-matter/measure) split, carried on separate ledgers, never
  summed. E029 (`form_value_imported`) reports **E2** at the edge level (reported_tier = value_tier =
  edge_scored_tier = E2; recognition-conditional on the imported run-generated LECs), its
  form-descends-E1 leg recorded but NOT counted in the E1 null; E041 (`theorem_run`)
  reports E3, its run-exhibited E0 leg the separate ledger entry.
- `near_intra_layer_check` (fix #8(ii)): for E016, E017 (SM gauge-factor restrictions) and E039 (SR↔EM
  shared Lorentz) — the E.4 relabeling test must be run and recorded; if within-layer, mark
  "within-a-layer, no SBT content" and REMOVE from the E1 count (no flattering-by-padding).
- `arrow_direction` (O2): `down`/`up`/`bidirectional` — makes the opposite arrows of E005 (down, GR→BH-
  thermo) and E022 (up, thermo→GR recovery) visible at a glance; guards route-mismatch conflation.
- `is_rg_eft_descent` (O1): true where an E1 shadow is exactly a textbook RG/EFT move physics already
  does (E008, E015, E029, E035a, E038, E040) — so FREEZE_NOTES can report "N of the E1 shadows are RG/EFT,
  not novel SBT content," pre-empting the "renormalization rebranded" charge.
- `named_import` (fix #3): the single frozen named source for each E2 edge.
- `secondary_modalities` / `conditionality_flags` (R-P2, Pause-2): OPTIONAL descriptive residual
  annotations on a STRUCTURAL-primary E2 edge whose closure leans on a named import; the only defined
  value is `recognition-conditional`. NOT canonical primary-modality strings, NEVER emittability-checked,
  NEVER counted in the registered null. Currently carried only by **E005** (primary `currency-shadow-price`
  + secondary `recognition-conditional`). Import-hygiene on the secondary flag = validator check **C13**
  (the C11 parallel for secondary flags). See §3.1.
- `run_target_stub` (O5): a Run-Target Manifest spec stub for the run-exhibited E0 phenomena E031
  (turbulence) and E041 (confinement), so the E0/E3 split (run-exhibited E0 vs open-theorem E3) is
  captured at freeze.
- `split_from` (fix #6): provenance for E027a/b and E035a/b.

## 6. The HARD / EMBARRASSING edges (mandated; firewall anchors / E3 anti-controls)

Kept deliberately at the conservative tier; the places SBT is SILENT or FORECLOSED. Any casting that
pushes one to E1/E2 is **smuggling** → calibration FAIL. Grounded in the retrodiction-atlas finding that
all decisive content here is IMPORTED or DISCLAIMED — SBT retrodicts nothing new.

| id | edge | tier | why it MUST stay there |
|----|------|------|------------------------|
| E018 | QM ↔ GR (quantum gravity) | **E3** (anti-control) | no accepted common refinement; primer trap #1; likely `no_faithful_M` E3 |
| E019 | SM → gauge-group-origin | **E3** (anti-control) | SU(3)×SU(2)×U(1) is a free input; retro: imported/disclaimed |
| E020 | SM → fermion-generations | **E3** (anti-control) | 3 generations + hierarchy free inputs; retro R024 honest negative |
| E021 | GR → cosmological-constant | **E3** (anti-control) | the Λ problem; retro R025 (Ω_Λ) SYNTHETIC/TUNABLE — never cite |
| E032 | QM → measurement-outcome | **E3** | decoherence gives the diagonal (E1) but NOT single-outcome selection |
| E037 | string-theory → SM | **E3** | landscape: vacuum selection non-definable; even the leading candidate lands E3 |
| E041 | QCD → confinement | **E3** (theorem) / E0 (run-exhibited) | mass gap is an open Clay problem; lattice exhibits, no proof |
| E042 | GR → singularity-theorems | **E3** | GR locates its own boundary; the needed extension (E018) is unsupplied |

The Born rule (E007), the pointer-basis selection (E026), and the arrow of time (E030) are the
*near-miss* anchors: each looks like it might be a clean E1 shadow but is demoted to E2 because the
decisive piece is a NAMED import (Gleason/envariance; einselection criterion; the Past Hypothesis).
Recording these E2 prevents over-reading the E1 decoherence/limit shadows next to them.

## 7. PRE-AUDIT registered-null distribution (review fix #4 / O4 / R6 — a PREDICTION, not a result)

**Source of truth: `CONTRACT.json` `registered_null`.** The counts below are recomputed from the FINAL
`edge_manifest.jsonl` (`provisional_tier_guess`, all **46** edges) and MUST equal
`CONTRACT.registered_null.per_tier`; if this prose and the contract ever disagree, the contract governs
and the prose is stale (a freeze-blocking drift). Pre-audit tier guess (**recorded so the post-audit run
cannot be tuned toward it**; this is NOT the audited verdict):

- **E1 (computable descent): 19** — the shadow-heavy bulk, as predicted (of which 5 E1 rows are flagged
  `is_rg_eft_descent` — exactly textbook RG/EFT moves physics already does: E008, E015, E035a, E038, E040;
  E028a is a further RG-type FLRW specialization — see O1). **E1 caveat:**
  this 19 INCLUDES the 3 near-intra-layer rows **E016, E017, E039** carried as **E1-pending**
  (`near_intra_layer_check:true`, `near_intra_layer_result:'pending'`); they are NEVER counted as
  **sealed** E1 (the audited E1 set must REMOVE any that fails gate E.4). Sealed-E1-eligible
  (non-pending) = **16**; E1-pending = **3**.
- **E2 (recognition-conditional): 13** — named-import landings, reported **separately**, never summed
  (8 carry the **primary** `recognition-landing` modality: E007, E022, E025, E026, E027a, E028b, E030,
  E033; the other 5 — E005, E023, E024, E029, E034 — land via a named import under a **structural** primary
  modality duality/currency/shadow-down). Of these, **E005** (primary `currency-shadow-price`)
  additionally carries the **secondary** `recognition-conditional` flag (Pause-2 R-P2, §3.1); the
  secondary flag does **not** change E005's primary modality or its place in the E2 tally — it is counted
  **once**, at `currency-shadow-price`/E2.
- **E3 (sharpened gap / foreclosure): 10** — located + typed, not closed (incl. the 4 E3 anti-controls
  E018–E021 and the O3 hierarchy gap E043).
- **E0 (run-only, deferred to the Run-Target Manifest): 4** — E001, E027b, E031, E035b (all
  `emergence-up`).

(Each edge is counted EXACTLY ONCE at its headline tier; value_split E0/E2 value-legs — E029's
form-descends-E1 leg, E041's run-exhibited-E0 leg, the E0 value-legs of E004/E008/E035a/E038 — are NOT
separately counted, per `CONTRACT.registered_null.value_split_legs_not_counted`.)

This is the **predicted shadow-heavy / emergence-sparse** shape (foreclosure-dominance), the framework
working, not failing (primer §9 #8). **E1 is never summed with E2/E0/E3.** The four tiers live on
separate ledgers.

## 8. Scope guard (what this draft does NOT do)

No computationally-irreducible runs; no empirical predictions; no constant is derived. Every E0 is
FLAGGED OUT and DEFERRED to the Run-Target Manifest (E001, E027b, E031, E035b; plus the value_split E0
sub-targets and the run_target_stub specs for E031/E041). Every "decisive"-sounding claim is conditional
on the audited casting and licensed only by the proton-mass calibration.
