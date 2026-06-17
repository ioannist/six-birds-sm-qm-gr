# Theory Manifest — inclusion/exclusion notes (FROZEN)

**Artifact:** `theory_manifest.jsonl` — 21 closure-package cards for the Physics Layer Atlas (Stage 1).
**Scope of this file:** the frozen list of currently-known physics theories to chart, each as a *within-layer* closure
package `T = (Z, f, Σ_f, E, D)`. This file lists the LAYERS only. The EDGES between them (typing + tiers) live in
`edge_manifest.jsonl`. Where a card mentions a relation to another layer it does so only to FLAG it as edge material,
never to assert a reduction.

## FROZEN canonical id convention + alias table (review fix #1)

The **21 theory-card ids are CANONICAL** and use **snake_case**. The edge manifest has been rewritten to
these ids. The renames (kebab edge-endpoint → canonical card) are: `quantum-chromodynamics`→`qcd`,
`quantum-electrodynamics`→`qed`, `electrodynamics`→`classical_electromagnetism`,
`navier-stokes`→`hydrodynamics`, `condensed-matter`→`condensed_matter_spt`,
`lambda-cdm-cosmology`→`lambda_cdm`, `effective-field-theory`→`rg_eft` (node→card promotion, fix #2(iii)),
`brownian-motion`→`brownian_langevin`; all other peers are re-casings (e.g. `general-relativity`→
`general_relativity`). The full table and the non-peer **node registry** (`observable_readout` /
`open_question` / `candidate_substructure`) are in `edge_manifest_notes.md` §§1–2. **Freeze assertion:**
every edge endpoint resolves to a frozen card id OR a frozen registered node id, or the bundle does not freeze.

The 21 canonical card ids: `classical_mechanics`, `newtonian_gravity`, `special_relativity`,
`general_relativity`, `quantum_mechanics`, `relativistic_qft`, `qed`, `qcd`, `electroweak_theory`,
`standard_model`, `thermodynamics`, `statistical_mechanics`, `kinetic_theory`, `hydrodynamics`,
`condensed_matter_spt`, `lambda_cdm`, `black_hole_thermodynamics`, `classical_electromagnetism`,
`geometrical_optics`, `brownian_langevin`, `rg_eft`.

## Guardrails honored (primer + digest)

- **Each card is a faithful within-layer description.** Per primer §3, within a layer SBT is "textbook in costume,"
  so these cards are ordinary textbook accounts cast into the closure vocabulary (Z = carrier, f = lens, E = packaging;
  the defect ledger D is implied by each layer's stated regime-of-validity and is made explicit per-edge by drafter 4).
  No card scores SBT inside a layer (trap 4), and no card derives a constant (trap 2) — every layer constant
  (`G`, `c`, `ħ`, `α`, `α_s`, the Higgs vev, `Λ`, `k_B`) is explicitly flagged as a *measured/input* quantity.
- **No cross-boundary reduction.** Cards never claim layer A "reduces to" or "is derived from" layer B. Relations are
  named only as *shadow / descent / emergence candidates* to be AUDITED later, preserving the up/down asymmetry (§6).
- **`status` field** is conservative: every phenomenological layer is `lawful_closed_layer`; `rg_eft` is
  `lawful_meta_layer` (it is physics' own scale-organization machinery, not a single phenomenology).
- **Fairness over flattery.** The list is built to cover the spread, INCLUDING the hard cases that embarrass any
  "SBT explains structure" overreach. The cards for `standard_model`, `electroweak_theory`, `lambda_cdm`,
  `general_relativity`, and `condensed_matter_spt` explicitly point at the hard/foreclosed edges drafter 4 must keep
  honest (gauge-group origin, three generations / mass hierarchy, cosmological constant, QM↔GR, asserted-vs-audited
  emergence).

## The 17 required theories (all present)

classical_mechanics · special_relativity · general_relativity · newtonian_gravity · quantum_mechanics ·
relativistic_qft · standard_model · qed · qcd · electroweak_theory · statistical_mechanics · thermodynamics ·
kinetic_theory (Boltzmann) · hydrodynamics (Navier–Stokes) · condensed_matter_spt · lambda_cdm ·
black_hole_thermodynamics.

## The 4 honest additions (and why)

1. **classical_electromagnetism (Maxwell).** Needed as the lawful *source* layer for the cleanest textbook
   coarse-graining in physics (geometrical optics) and as the classical limit of QED. Without it those edges would
   dangle. It is SR-covariant by construction, so it does not add a spurious "SR descent."
2. **geometrical_optics.** Included precisely because it is a TRANSPARENT, checkable `λ → 0` / eikonal shadow of wave
   optics — a fair, non-flattering **known-E1 descent control**. Good calibration material that does NOT advantage SBT.
3. **brownian_langevin (Langevin / Fokker–Planck).** A clean mesoscopic downward-shadow with a recognized
   fluctuation–dissipation grounding; supplies honest E1-style descent-test material and a stochastic-layer datapoint
   so the atlas is not purely deterministic-mechanics-shaped.
4. **rg_eft (Renormalization Group / EFT as a layer-generating principle).** The single most important HONEST
   comparator. RG/EFT is physics' own native lens/coarse-graining/inter-scale-descent machinery. Including it as an
   explicit (meta-)layer is the **"textbook in costume" guardrail made structural**: many "shadow down" edges in this
   atlas literally ARE RG/EFT descents, and naming RG/EFT up front prevents the atlas from re-badging as novel
   SBT-content what physics already does as renormalization. This is an anti-flattery inclusion.

## Deliberate exclusions (and why) — kept off to avoid padding or scope-creep

- **String theory / loop quantum gravity / other quantum-gravity programs.** Not currently-established theories with
  accepted observables; including them would let an emergence/foreclosure verdict ride on a non-lawful layer. The
  QM↔GR gap is charted as a HARD EDGE (drafter 4) WITHOUT promoting any candidate UV completion to a layer.
- **AdS/CFT as a standalone "theory."** It is a *relation* (a duality), not a closed phenomenological layer with its
  own accepted observables; it belongs in the edge manifest (F41 duality / recognition-conditional), not here.
- **Supersymmetry / GUTs / axion / inflaton models.** Beyond-Standard-Model and not experimentally established;
  excluded to keep `status` honest. (Inflation is folded into `lambda_cdm` only via its accepted primordial-spectrum
  observables, not as a separate confirmed layer.)
- **Nuclear / atomic / molecular / chemistry layers, plasma physics, optics-of-media, elasticity, acoustics.**
  Genuine lawful effective layers, but they would inflate the count without adding a distinct SBT-relevant edge TYPE
  beyond what condensed_matter_spt, hydrodynamics, kinetic_theory, and the EM→optics chain already exercise. Omitted
  to keep the chart at the requested ~18–22 and avoid stacking the deck with easy E1 descents.
- **Information theory / computation / "it-from-qubit."** Cross-cutting and partly meta; engaged only where it shows up
  as an edge principle (e.g. gravity↔entanglement at `black_hole_thermodynamics`), not as a physics layer.
- **General "quantum field theory" vs its instances.** Kept `relativistic_qft` as the FRAMEWORK layer and listed
  `qed`/`qcd`/`electroweak`/`standard_model` as instances/sectors. Their containment relations are EDGES (overlaps),
  flagged in each card, not asserted here.

## Calibration alignment (for drafter 4 / the rubric)

- **`qcd` is the canonical E0 / run-only anchor.** Its card states plainly: the proton mass has no closed-form
  derivation; it is the readout of an irreducible lattice run. There is **no free proton/hadron MASS parameter**;
  quark masses and coupling/scale are fixed independently under the declared physical-quark-mass lattice-QCD
  protocol (scale set by one hadronic input; running by dimensional transmutation / Λ_QCD); the proton-mass /
  hadron-spectrum readout is out-of-sample and not fitted. Nothing in the manifest derives it. The QCD→hadron-masses
  edge is the worked E0 calibration.
- **Known-E1 descent controls available from these layers:** statistical_mechanics→thermodynamics,
  kinetic_theory→hydrodynamics, special_relativity→Galilean limit, classical_electromagnetism→geometrical_optics,
  microscopic→brownian_langevin.
- **Recognition-conditional (E2) control material:** black_hole_thermodynamics sits at the GR/QFT/thermodynamics
  junction (horizon thermodynamics, gravity↔entanglement) — lands only by importing a named external principle.
- **Hard / foreclosed (E3) and gap material is pre-flagged in the cards:** QM↔GR (quantum gravity), SM gauge-group
  origin, three generations / mass hierarchy, the cosmological-constant value. The manifest exposes these as the
  places the atlas must remain SILENT or report a sharpened gap — never a "solve."

## Predicted shape (registered expectation, not a target)

These 21 layers are intentionally **shadow-heavy and emergence-sparse**: most live downstream of a richer layer by a
coarse-graining physics already accepts (E1 descents), a few sit at recognition-conditional junctions (E2), the
structural-origin questions are foreclosed gaps (E3), and exactly one well-understood scale (the proton mass) is a
run-only E0 anchor. That distribution is the *predicted* result of an honest chart, recorded here so a later run cannot
be tuned toward it.
