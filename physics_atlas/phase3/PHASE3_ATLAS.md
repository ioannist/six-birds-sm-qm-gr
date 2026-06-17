# Physics Layer Atlas — Phase 3 Scored Atlas (all 46 edges typed)

**Status:** the full scored atlas. Every one of the 46 charted inter-theory edges now carries a
*scored* tier and primary modality, derived blind via the C.5 decision-procedure that was CALIBRATED
in Phase 1 (9 known edges, all tiers recovered) and validated by the freeze-gate in `--mode scored`
(**PASS, exit 0**).

> **Scope (binding, from the primer and SCIENCE_DIGEST §10).** SBT is a meta-mathematical *organizing
> map*; this atlas does **cartography + triage only** — no irreducible runs, no empirical claims, no
> constant derivation. `Xi = 0` certifies *adequacy/descent on a declared finite toy model under a
> declared audit*; it is **not** a derivation of one theory from another. E1 is **never summed** with
> E2/E0/E3. The reported (headline) tier of each edge contributes **exactly once** at its scored tier.

> **Tier legend.** **E1** = computable descent (a coarse-graining physics already accepts; normalized
> residual `ξ_rel → ~machine-zero` stably, no over-read). **E2** = recognition-conditional (closes only
> by a *named external import* under a stated assumption; reported separately as "conditional"). **E0**
> = run-only / computationally irreducible (a constructible non-descending run-object; deferred to the
> Run-Target Manifest, never run here). **E3** = sharpened gap / foreclosure no-go (the obstruction is
> *located and typed, not closed*). The conservatism ordering is the single
> **E1 > E2 > E0 > E3**; **E3 is the unique conservative terminal**; doubt only demotes.

**Provenance of the scored values.** Tier/modality are read from the 46 scored records (37 Phase-3
`phase3/scored/*.json` + 9 calibration `calibration/scored/*.json`), merged onto the frozen
`prereg/edge_manifest.jsonl` into `phase3/scored_run/edge_manifest.jsonl`. The `Ξ` columns are the
form-leg (descent) adequacy residuals reported in each scored record; the `named import` column is the
single frozen principle that closes each E2 edge.

---

## 1. Per-edge typed table

Columns: **id** · **source → target** · **arrow** · **scored tier** · **primary modality** ·
**secondary flag** · **Ξ (form-leg) — raw / normalized `ξ_rel` at h1→h2 (E1 only)** · **named import
(E2 only, abbreviated)** · **decision path**.

The decision-path codes: `D1`=descent passes (Ξ→0 stable, no over-read) → E1; `D2`=descent fails/over-reads,
a named import closes it → E2; `D3`=descent + recognition both fail, a constructible run-object exists → E0;
`D4`=descent + recognition + run all fail / not constructible → E3 (foreclosure); `Dstruct`=a structural
modality (duality / common-refinement / currency / holonomy) is the primary pass.

| id | source → target | arr | tier | primary modality | sec | Ξ form-leg ξ_rel h1→h2 (E1) / import (E2) | path |
|----|-----------------|-----|------|------------------|-----|--------------------------------------------|------|
| E001 | qcd → hadron-spectrum | up | **E0** | emergence-up | — | raw Ξ 7.84e8→2.25e9, **ξ_rel 0.197→0.042 stable-positive** (no machine-zero; analytic control →1e-14) | D3 |
| E002 | statistical_mechanics → thermodynamics | down | **E1** | shadow-down | — | ξ_rel 3.8e-11 → 1.5e-11 | D1 |
| E003 | special_relativity → classical_mechanics | down | **E1** | shadow-down | — | ξ_rel (trace) 1.1e-12 → 4.1e-15 | D1 |
| E004 | kinetic_theory → hydrodynamics | down | **E1** | shadow-down | — | Ξ=0 on finite-velocity-grid Chapman–Enskog toy (calibration control) | D1 |
| E005 | general_relativity → black_hole_thermodynamics | down | **E2** | currency-shadow-price | recognition-conditional | QFT-in-curved-spacetime (Hawking flux) + 1st law of BH mechanics (=E034) | Dstruct/D2 |
| E006 | quantum_mechanics → classical_mechanics | down | **E1** | shadow-down | — | ξ_rel 1.9e-16 → 4.1e-16 (over-read leg 0.44→0.062) | D1 |
| E007 | quantum_mechanics → classical-probability | down | **E2** | recognition-landing | — | Gleason's theorem (noncontextual measure, dim H ≥ 3) | D2 |
| E008 | relativistic_qft → rg_eft | down | **E1** | shadow-down | — | ξ_rel 6.5e-16 → 7.9e-15 (value leg E0, run-only) | D1 |
| E009 | rg_eft → relativistic_qft | up | **E3** | emergence-up | — | (UV-completion non-definable from the IR EFT; located, not closed) | D4 |
| E010 | general_relativity → newtonian_gravity | down | **E1** | shadow-down | — | ξ_rel 2.0e-16 → 4.0e-16 | D1 |
| E011 | classical_electromagnetism → geometrical_optics | down | **E1** | shadow-down | — | eikonal λ→0 limit: ξ_rel 4.8e-6 → 5.0e-12 (diffraction held out, ~0.38) | D1 |
| E012 | qed → classical_electromagnetism | down | **E1** | shadow-down | — | ξ_rel 1.8e-16 (coherent-state ℏ→0 leg) | D1 |
| E013 | statistical_mechanics → brownian_langevin | down | **E1** | shadow-down | — | ξ_rel 3.5e-16 → 1.0e-15 (friction-kernel value E0) | D1 |
| E014 | relativistic_qft → quantum_mechanics | down | **E1** | shadow-down | — | ξ_rel 1.1e-6 → 1.6e-8 (NR v/c→0 limit) | D1 |
| E015 | electroweak_theory → qed | down | **E1** | shadow-down | — | ξ_rel 1.2e-15 → 7.1e-14 | D1 |
| E016 | standard_model → electroweak_theory | down | **E3** | shadow-down | — | near-intra-layer **FAILED** (within-layer GSW restriction; demoted to E3) | D4 |
| E017 | standard_model → qcd | down | **E3** | shadow-down | — | near-intra-layer **FAILED** (within-layer color tensor-factor; demoted to E3) | D4 |
| E018 | quantum_mechanics ↔ general_relativity | bidir | **E3** | emergence-up | — | QM↔GR quantum-gravity gap; no faithful M / non-factorization | D4 |
| E019 | standard_model → gauge-group-origin | up | **E3** | emergence-up | — | SU(3)×SU(2)×U(1) origin (anti-control, must-not-seal-E1/E2) | D4 |
| E020 | standard_model → fermion-generations | up | **E3** | emergence-up | — | 3 generations / mass hierarchy (anti-control) | D4 |
| E021 | general_relativity → cosmological-constant | up | **E3** | emergence-up | — | Λ value (anti-control) | D4 |
| E022 | thermodynamics → general_relativity | up | **E2** | recognition-landing | — | Jacobson's "Einstein equation of state" (Clausius dQ=TdS on Rindler horizons) | D2 |
| E023 | conformal-field-theory ↔ general_relativity | bidir | **E2** | duality-equivalence | recognition-conditional | Maldacena / AdS-CFT holographic dictionary | Dstruct/D2 |
| E024 | conformal-field-theory ↔ entanglement-geometry | bidir | **E2** | currency-shadow-price | recognition-conditional | Ryu–Takayanagi formula (within AdS/CFT) | Dstruct/D2 |
| E025 | quantum_mechanics → thermodynamics | down | **E2** | recognition-landing | — | Eigenstate Thermalization Hypothesis (ETH) ansatz | D2 |
| E026 | quantum_mechanics → decoherence-pointer-basis | down | **E2** | recognition-landing | — | einselection / predictability-sieve criterion (Zurek) | D2 |
| E027a | condensed_matter_spt → spt-phases | up | **E2** | recognition-landing | — | group-cohomology / cobordism SPT classification (CGLW + Kapustin) | D2 |
| E027b | condensed_matter_spt → spt-phases | up | **E0** | emergence-up | — | protected SPT invariant as a run-readout (DMRG/ED/QMC); deferred | D3 |
| E028a | general_relativity → lambda_cdm | down | **E1** | shadow-down | — | ξ_rel 4.1e-16 → 2.8e-15 (FLRW geometric descent leg) | D1 |
| E028b | general_relativity → lambda_cdm | up | **E2** | recognition-landing | — | imported Λ + CDM sector + cosmological-measure / initial conditions | D2 |
| E029 | qcd → chiral-perturbation-theory | down | **E2** | shadow-down | recognition-conditional | run-generated LECs (f_π, chiral condensate) imported from lattice QCD | Dstruct/D2 (value_split: form E1 / value E2) |
| E030 | thermodynamics → arrow-of-time | up | **E2** | recognition-landing | — | the Past Hypothesis (low-entropy initial boundary condition) | D2 |
| E031 | hydrodynamics → turbulence | up | **E0** | emergence-up | — | inertial-range anomalous scaling as a Navier–Stokes DNS run-readout; deferred | D3 |
| E032 | quantum_mechanics → measurement-outcome | up | **E3** | emergence-up | — | single-outcome selection; non-definable from QM Σ_f (located, not closed) | D4 |
| E033 | classical_mechanics → thermodynamics | down | **E2** | recognition-landing | — | the Stosszahlansatz (molecular-chaos) | D2 |
| E034 | general_relativity → quantum-field-theory-curved | down | **E2** | shadow-down | recognition-conditional | semiclassical QFT-in-curved-spacetime construction (no back-reaction) | Dstruct/D2 |
| E035a | lattice-gauge-theory → qcd | down | **E1** | shadow-down | — | continuum-limit STRUCTURE: ξ_rel 2.7e-15 → 3.3e-14 (value leg E0=E035b/E001) | D1 (value_split: form E1 / value E0) |
| E035b | lattice-gauge-theory → qcd | up | **E0** | emergence-up | — | physical readout (spectrum, Λ_QCD) as a lattice-QCD run-readout; deferred | D3 |
| E036 | quantum_mechanics → berry-phase-holonomy | down | **E1** | holonomy | — | structural holonomy pass (ξ_rel pinned at 1 by construction; the holonomy IS the content) | Dstruct |
| E037 | string-theory → standard_model | up | **E3** | emergence-up | — | vacuum selection: ξ_rel 0.730→0.869 stable-positive; ~10^500 landscape, no named selector | D4 |
| E038 | statistical_mechanics → phase-transitions-universality | down | **E1** | shadow-down | — | universality-CLASS descent: ξ_rel 7.2e-16 → 2.0e-16 (exponent VALUES E0) | D1 (value_split: form E1 / value E0) |
| E039 | special_relativity ↔ classical_electromagnetism | bidir | **E1** | common-refinement | — | near-intra-layer **PASSED**; invariance residuals ~1e-15 (genuine common refinement) | Dstruct |
| E040 | many-body-quantum → fermi-liquid-theory | down | **E1** | shadow-down | — | IR-fixed-point STRUCTURE descent: ξ_rel 9.4e-16 → 2.0e-15 | D1 |
| E041 | qcd → confinement | up | **E3** | emergence-up | — | open Yang–Mills mass-gap theorem (Clay) E3; run-exhibited string-tension E0 carried apart | D4 (value_split: theorem E3 / run E0) |
| E042 | general_relativity → singularity-theorems | up | **E3** | emergence-up | — | singularity/initial-data obstruction; located, not closed | D4 |
| E043 | electroweak_theory → electroweak-hierarchy | up | **E3** | emergence-up | — | EW-hierarchy/naturalness: ξ_rel 0.988→0.999; no single named selector (SUSY/anthropic contested) | D4 |

**Value-split rows (no-summing within an edge; the value-leg is on a SEPARATE ledger, never summed
into the headline):**
- `form_value` — **E004, E008, E035a, E038**: the EQUATION/STRUCTURE descends **E1** (the edge's own
  closure = headline E1); the VALUE leg (transport coefficients / matched couplings / hadron spectrum /
  critical-exponent values) is **E0** run-only, carried to the Run-Target Manifest.
- `form_value_imported` — **E029**: the chiral SYMMETRY SKELETON descends E1, but the PREDICTIVE
  CONTENT (LECs) is **imported E2**; per `reported_tier_by_split_type[form_value_imported]=value_tier`,
  the headline is **E2** (the form-E1 leg is recorded but **not** counted in the E1 null).
- `theorem_run` — **E041**: the open-theorem (Yang–Mills mass gap) is **E3** (the reported/headline
  leg); the lattice run-exhibited string tension is **E0**, carried apart. E041 is **not** counted in E0.

---

## 2. Foreclosure map (scored chargeable distribution)

> **Reporting basis: 46 charted rows = 44 chargeable inter-layer edges + 2 within-layer/no-content
> rows (E016, E017, excluded); chargeable distribution E1 = 17, E2 = 13, E0 = 4, E3 = 10.**
> The `scored_registered_null` (the recorded scored verdict over the 44 chargeable edges) =
> E1 = 17, E2 = 13, E0 = 4, E3 = 10. This equals the manifest `scored_tier` chargeable headline
> counts (validator C12, `--mode scored`, which skips rows flagged
> `excluded_from_foreclosure_count`, PASS). E016/E017 retain `scored_tier:"E3"` only as a schema
> sentinel; they are NOT charged as E3 foreclosure gaps (they failed gate-E.4 and are
> within-a-layer/no-content, rubric §9).

```
SCORED foreclosure distribution (44 chargeable inter-layer edges, each counted ONCE at its headline tier):

  E1  computable descent        17  ███████████████████████████████████  38.6%
  E2  recognition-conditional   13  ███████████████████████████          29.5%
  E0  run-only (deferred)        4  ████████                             9.1%
  E3  foreclosed gap            10  █████████████████████                22.7%

  (+ 2 within-layer/no-content rows EXCLUDED from the chargeable map: E016, E017)
```

**Members.**
- **E1 (17, shadow-heavy band):** E002, E003, E004, E006, E008, E010, E011, E012, E013, E014, E015,
  E028a, E035a, E036, E038, E039, E040. Sub-structure: 14 plain `shadow-down` descents + 1 `holonomy`
  (E036) + 1 `common-refinement` (E039) + 1 form-value descent whose value leg is a separate E0
  (E035a; also E004/E008/E038 carry never-summed E0 value legs).
- **E2 (13, separate conditional band — "conditional," never summed with E1):** E005, E007, E022, E023,
  E024, E025, E026, E027a, E028b, E029, E030, E033, E034. Of these, **8 are PRIMARY
  recognition-landing** (E007, E022, E025, E026, E027a, E028b, E030, E033 = the frozen
  `affected_edges`); the other 5 land via a **structural** primary modality + a named import recorded as
  a **secondary** `recognition-conditional` flag (E005 currency-shadow-price; E023 duality-equivalence;
  E024 currency-shadow-price; E029 shadow-down/form_value_imported; E034 shadow-down).
- **E0 (4, emergence-sparse, run-only, deferred):** E001, E027b, E031, E035b. (See §4.)
- **E3 (10, foreclosed gaps — chargeable):** E009, E018, E019, E020, E021, E032, E037, E041, E042,
  E043. This includes the 4 anti-controls (E018, E019, E020, E021) which correctly did **not** seal
  E1/E2, and the open-theorem/landscape gaps (E009, E032, E037, E041, E042, E043).
- **Within-layer / no-content (2, EXCLUDED from the chargeable map):** E016, E017. Both FAILED
  gate-E.4 (near-intra-layer relabel failures: SM→electroweak GSW restriction and SM→QCD color
  tensor-factor restriction). They are within-a-layer with **no SBT content** (rubric §9), **not**
  ordinary E3 foreclosure gaps. They carry `scored_tier:"E3"` only as a schema sentinel plus
  `excluded_from_foreclosure_count:true` + `within_layer_no_content:true`, and are removed from the
  chargeable foreclosure tally (chargeable E3 = 10, not 12).

**Reading.** The scored shape is **shadow-heavy (E1 + E2 structural-descent legs dominate the
checkable band) and emergence-sparse (only 4 E0, with E3 the foreclosure terminal)** — the predicted
foreclosure-dominant shape (SCIENCE_DIGEST §8; primer §9 trap 8). Foreclosure-dominance is the
**framework working, not failing**: SBT predicts that most hard inter-theory targets do not yield to
internal derivation and land either as a named-import conditional (E2), a deferred run (E0), or a
located gap (E3). No E1 was padded: both failed near-intra-layer candidates were removed from the E1
count and demoted to E3.

---

## 3. Drift summary (scored vs. frozen-provisional)

The frozen `registered_null` was a **PRE-AUDIT prediction** (E1=19, E2=13, E0=4, E3=10). Scored tiers
are **allowed to drift**; the drift is small and entirely in the predicted direction (conservative
demotion of unresolved near-intra candidates).

**Tier drift (2 edges — both predicted by the registered_null E1 caveat / O2):**

| edge | provisional | scored | why the fresh typing changed the guess |
|------|-------------|--------|----------------------------------------|
| **E016** (standard_model → electroweak_theory) | E1 (E1-pending) | **E3*** | The near-intra-layer gate E.4/E.11 **FAILED**: electroweak ↔ SM is a *within-a-layer* GSW (broken-phase) restriction of the same theory, not a between-layer coarse-graining; the W/Z masses and Weinberg angle are measured inputs, not a descended readout. "Within-a-layer, no SBT content" ⇒ removed from the E1 count. *Carries `scored_tier:"E3"` only as a schema **sentinel** (`within_layer_no_content:true`, `excluded_from_foreclosure_count:true`); it is **NOT** charged as an E3 foreclosure gap. |
| **E017** (standard_model → qcd) | E1 (E1-pending) | **E3*** | The near-intra-layer gate **FAILED**: SM → QCD is a *within-a-layer* color tensor-factor restriction (identity on a tensor factor — deleting the relabel leaves no residual relation). The scored record's own rationale reaches the "within-a-layer, no SBT content" verdict; the genuine QCD content with SBT teeth (the GeV scale by dimensional transmutation) is the distinct E0 edge E001. Removed from E1. *Carries `scored_tier:"E3"` only as a schema **sentinel** (excluded from the chargeable foreclosure count); **NOT** an E3 foreclosure gap. |

> Both demotions are the registered_null **E1 caveat** materializing as predicted: the 3 near-intra
> candidates (E016, E017, E039) were carried as **E1-pending** and could not count as sealed E1 until
> gate E.4 passed. **E039 PASSED** (genuine common refinement, sealed E1); **E016 and E017 FAILED**
> (demoted to E3). The honest audited E1 set therefore drops 2 from the predicted 19 → 17.

**Modality drift (2 edges — tier UNCHANGED; routed to adjudication per `CONTRACT.gate_policy`, not
auto-failed):**

| edge | provisional modality | scored modality | tier | adjudication |
|------|----------------------|-----------------|------|--------------|
| **E018** (QM ↔ GR) | common-refinement | **emergence-up** | E3 (unchanged) | The quantum-gravity gap is an *upward* strict-extension obstruction (the "quantum state of the metric" predicate is non-definable from below), not a common refinement. A blind-vs-frozen PRIMARY-modality mismatch on a hard/faceted edge is adjudicated and recorded, not force-aligned (gate_policy; this is one of the two Pause-2 modality-disagreement precedents). |
| **E032** (QM → measurement-outcome) | common-refinement | **emergence-up** | E3 (unchanged) | The diagonal-ensemble → single-outcome step is a non-factorization / non-definability obstruction (upward), located and typed but not closed. Same adjudication. |

**No drift on the calibration anchors** (the firewall held): E001 → **E0** (proton mass, run-only);
the E1 controls E002/E003/E004 → **E1**; the E2 control E005 → **E2**; the 4 E3 anti-controls
E018/E019/E020/E021 → **E3** (none sealed E1/E2). 41 of 46 edges reproduced the provisional guess on
both tier and primary modality with no drift.

---

## 4. E0 run-target set (seeds the Run-Target Manifest)

The 4 run-only edges are **flagged OUT and DEFERRED** — the atlas specs the run, it does **not** run it,
does **not** predict, does **not** derive any constant (HARD SCOPE). Each sealed E0 by a *positive*
construction of a non-descending run-object (E.7), never as a doubt-haven.

| edge | source → target | run-object (non-descending) | run substrate / readout (deferred) |
|------|-----------------|-----------------------------|------------------------------------|
| **E001** | qcd → hadron-spectrum | hadron mass scale / Λ_QCD by dimensional transmutation (essential singularity exp(−1/2b₀g₀²), non-definable from any finite analytic correlator currency) | lattice QCD (physical-quark-mass SU(3) path integral, Monte-Carlo); readout = hadron-interpolator correlator decay rate; out-of-sample = spectrum after fixing quark masses + scale from ONE hadronic input |
| **E027b** | condensed_matter_spt → spt-phases | the protected SPT invariant (run-readout of a gapped symmetric phase) | DMRG / ED / QMC of a declared interacting SPT lattice model; readout = protected edge spectrum / ground-state degeneracy, out-of-sample |
| **E031** | hydrodynamics → turbulence | inertial-range anomalous scaling exponents (non-definable from the closed hydrodynamic layer) | Navier–Stokes DNS on a finite grid at high Reynolds number; readout = anomalous inertial-range scaling exponents, out-of-sample |
| **E035b** | lattice-gauge-theory → qcd | the physical QCD scale / spectrum (= E001's value leg; the run-only readout of the continuum limit) | physical-quark-mass lattice QCD path integral; readout = continuum spectrum / Λ_QCD, out-of-sample |

> Note the **never-summed E0 value-legs** that are *not* in the E0 headline count but feed the same
> Run-Target Manifest: the `form_value` value legs of **E004** (transport coefficients), **E008**
> (matched low-energy couplings), **E035a** (= E035b/E001), **E038** (critical-exponent values), and
> the `theorem_run` run-exhibited leg of **E041** (confinement string tension). These ride on separate
> ledgers and are never summed into either the E1 or E0 headline tallies.

---

## 5. Edges flagged for Pause-3 attention

**(A) Contested / adjudicated PRIMARY modality (tier settled, modality routed to adjudication):**
- **E018** (QM ↔ GR) and **E032** (QM → measurement-outcome) — primary modality drifted
  common-refinement → emergence-up. Tier E3 is firm; the modality adjudication is recorded (not
  force-aligned) per `CONTRACT.gate_policy`. These are the atlas's two genuine modality-contested rows
  (mirroring the Pause-2 E005/E018 modality disagreements). Pause-3 should confirm the emergence-up
  read.

**(B) Near-intra-layer relabel failures ("within-a-layer, no SBT content"; excluded from the
chargeable foreclosure count):**
- **E016** (standard_model → electroweak_theory) and **E017** (standard_model → qcd) — failed gate
  E.4/E.11 and were removed from the E1 count. **E017's scored record carried an internal
  inconsistency** (rationale concluded within-a-layer/removed-from-E1, but left `scored_tier=E1`);
  this was corrected. Per R1 they are now recorded as **"within-a-layer, no SBT content"**: they keep
  `scored_tier:"E3"` only as a schema **sentinel** and carry `within_layer_no_content:true` +
  `excluded_from_foreclosure_count:true`, so they are **excluded from the chargeable foreclosure
  tally** (chargeable E3 = 10, not 12) rather than charged as ordinary E3 gaps. The digest §9
  "within-a-layer, no SBT content" verdict governs; they are charted (46 rows) but not chargeable
  (44 chargeable inter-layer edges).

**(C) Value-split bookkeeping divergences (resolved against the frozen contract; flag to confirm):**
- **E008** scored record set `reported_tier=E1` while the frozen contract row sets `reported_tier=E0`
  (`form_value` ⇒ reported leg = value_tier). The merge used the **frozen contract value** (E0
  reported / E1 edge_scored_tier); the headline E1 is unchanged. Pause-3 should confirm the frozen
  contract reading governs.
- **E013, E014** scored records freelanced a `form_value` value_split not present in the frozen
  `rows_carrying_value_split`. These were **NOT** carried into the scored manifest (carrying them would
  have produced a C10 reported_tier conflict and would over-extend the frozen value-split set). The
  edges remain plain E1. Pause-3 may decide whether E013/E014 warrant a formally registered value_split
  in a future freeze.

**(D) Structural-E2 secondary-import rows (C13 hygiene — confirm single frozen imports):**
- **E005, E023, E024, E029, E034** carry a secondary `recognition-conditional` flag at E2 with a
  structural primary modality. All passed C13 import-hygiene. **E034's** import string was
  conservatively re-punctuated during the merge (parenthetical citation `/`-separators collapsed to
  "and") so the single-principle import would not be misread as a 3-way menu by the C11/C13 detector;
  the named principle (the semiclassical QFT-in-curved-spacetime construction = E005's import) is
  unchanged. **E026's** import had a second descriptive `/` ("maximal predictability / minimal entropy
  production") collapsed to "and" for the same reason. Pause-3 should confirm both re-punctuations are
  faithful.

**(E) Anti-control firewall (passed; record for audit):**
- **E018, E019, E020, E021** (QM↔GR, gauge-group origin, generations, Λ) all landed in {E3} — none
  sealed E1/E2. The firewall test that SBT does *not* secretly derive the gauge group / Λ holds.

---

## 6. Validator result

```
node phase3/scored_run/validate_freeze_gate.mjs --mode scored --dir phase3/scored_run
→ FREEZE-GATE: PASS — all checks clean (mode=scored)   exit 0
```

`--mode freeze` (the pre-scoring prediction gate) also still **PASSES** on the same bundle (exit 0):
the only behavioural change to the validator is **C12**, which now reads
`CONTRACT.scored_registered_null` in scored mode (allowing drift while still requiring the *recorded*
scored null to equal the manifest's scored headline counts) and `CONTRACT.registered_null` in freeze
mode (unchanged). Every other check is byte-identical to the frozen validator.
