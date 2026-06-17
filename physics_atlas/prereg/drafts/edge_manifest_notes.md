# Edge Manifest — Drafter 4 Notes (Physics Layer Atlas, Stage 1)

**Artifact:** `edge_manifest.jsonl` — 42 candidate inter-theory edges (target was ~35–45).
**Status:** DRAFT for the Layer-A adversarial review. Tier guesses are PROVISIONAL: they are the
honest pre-audit guess, NOT the audited verdict. Every non-calibration tier must still be *forced* by
the typing rubric's deterministic foreclosure decision-procedure (descent-test → Xi on a declared
finite toy → recognition-search for a NAMED principle → run-only check → else E3). Nothing here is
"decisive"; everything is "conditional on the audited casting."

## 1. What an edge is, and the ID/node scheme

Each row is a *directed candidate relation* between two closure-layers:
`source_theory_id --(known_physics_relation)--> target_theory_id`, with a guessed SBT modality and a
guessed edge-tier. Edge ids are `E001…E042`.

Node ids are conventional kebab-case and chosen to JOIN against drafter 3's theory manifest (the
mandated list: classical mechanics, special relativity, general relativity, Newtonian gravity,
quantum mechanics, relativistic QFT, Standard Model, QED, QCD, electroweak theory, statistical
mechanics, thermodynamics, kinetic theory, hydrodynamics/Navier-Stokes, condensed matter/SPT,
Lambda-CDM, black-hole thermodynamics, + geometrical optics, EM, Brownian/Langevin, RG/EFT).
I standardized QCD to `quantum-chromodynamics` everywhere (E001/E017/E029/E035/E041).

**Reconciliation flag for the assembler:** I introduced several *non-peer-theory* nodes that are
either (a) observable-readout targets or (b) named open-question targets, because the most important
edges are precisely theory→observable or theory→open-gap. These are flagged in-notes so they are NOT
mistaken for missing theory cards:
- observable / phenomenon readout nodes: `hadron-spectrum`, `confinement`, `turbulence`,
  `arrow-of-time`, `measurement-outcome`, `phase-transitions-universality`, `singularity-theorems`,
  `berry-phase-holonomy`, `entanglement-geometry`.
- open-question / "why this?" nodes: `gauge-group-origin`, `fermion-generations`,
  `cosmological-constant`.
- candidate-UV / sub-structure nodes drafter 3 may or may not card: `effective-field-theory`,
  `conformal-field-theory`, `string-theory`, `lattice-gauge-theory`, `quantum-field-theory-curved`,
  `chiral-perturbation-theory`, `fermi-liquid-theory`, `spt-phases`, `decoherence-pointer-basis`,
  `classical-probability`, `many-body-quantum`, `brownian-motion`, `geometrical-optics`.

If drafter 3 used a different spelling for any peer theory (e.g. `qed` vs
`quantum-electrodynamics`, `navier-stokes` vs `hydrodynamics`), the assembler should reconcile to
drafter 3's frozen ids; the relations are spelling-agnostic.

## 2. Calibration edges (is_calibration=true) — KNOWN answers, FREEZE-BLOCKERS

Per the rubric's calibration protocol (Erdős APN-9 rule): if any of these does NOT come out as its
recorded known answer under the audited procedure, the calibration FAILS and the scored run cannot
freeze.

| id | edge | KNOWN answer | role |
|----|------|--------------|------|
| E001 | QCD → hadron-spectrum | **E0** run-only (lattice QCD) | the canonical resolved emergent constant (proton mass); the no-shortcut anchor |
| E002 | statistical-mechanics → thermodynamics | **E1** descent | textbook coarse-graining; Xi=0 control |
| E003 | special-relativity → classical-mechanics | **E1** limit (Wigner–İnönü) | clean v/c→0 limit-descent control |
| E004 | kinetic-theory → hydrodynamics | **E1** descent (Chapman–Enskog) | second clean descent control (eqns E1; transport coeffs flagged toward E0) |
| E005 | GR → black-hole-thermodynamics | **E2** recognition | the named-import control (imports QFT-in-curved-spacetime); a clean E2 anchor |

Two E1 descent controls (E002, E004), one E1 limit control (E003), the E0 anchor (E001), and the
E2 recognition control (E005). This spans every tier *except* E3 in the calibration set; E3 has no
"known answer" by definition (an open gap), so it is calibrated indirectly via the firewall anchors
in §4.

## 3. Modality usage (the SBT inter-layer vocabulary I drew on)

- **shadow-down** (19): the dominant, expected modality — computable descent / coarse-graining /
  limit. Most are E1; several are demoted to E2 (imported content) or carry an E0 sub-flag (values
  need a run): E008 (couplings), E028 (cosmological content), E029 (LECs), E038 (exponent values).
- **emergence-up** (10): strict extensions / non-definable-from-below. These are E3 (gaps:
  E009, E019, E020, E021, E037, E041, E042) or E0 (run-only emergence: E027, E031) — and the E0
  calibration anchor E001. Per the primer §6, the up arrow is NEVER run as a derivation; none is E1.
- **recognition-landing** (6): lands only via a NAMED external import → all E2 (E007, E022, E025,
  E026, E030, E033).
- **common-refinement** (F51, 3): a sought common third (E018 QM↔GR, E032 measurement) → E3 gaps;
  E039 (SR↔EM shared Lorentz structure) → E1 compatibility check.
- **currency-shadow-price** (2): E005 (BH thermo), E024 (entanglement→area) → E2.
- **duality-equivalence** (F41, 1): E023 AdS/CFT → E2 (conjectured equivalence).
- **holonomy** (1): E036 Berry phase → E1 (computable route-mismatch witness).

## 4. The HARD / EMBARRASSING edges (mandated; firewall anchors)

These are kept deliberately and recorded at the conservative tier. They are the places SBT is SILENT
or FORECLOSED, and they double as elasticity-firewall tripwires: any casting that pushes one of them
to E1/E2 is **smuggling** and should be rejected by the no-smuggling gates. Grounded in the
retrodiction-atlas finding that all decisive content here is IMPORTED or DISCLAIMED — SBT retrodicts
nothing new.

| id | edge | tier | why it MUST stay there |
|----|------|------|------------------------|
| E018 | QM → GR (quantum gravity) | **E3** | no accepted common refinement; primer trap #1 forbids "unify by deriving both" |
| E019 | SM → gauge-group-origin | **E3** | SU(3)×SU(2)×U(1) is a free input; retro atlas: gauge group imported/disclaimed |
| E020 | SM → fermion-generations | **E3** | 3 generations + hierarchy are free inputs; retro R024 is the honest negative that survived skeptics best |
| E021 | GR → cosmological-constant | **E3** | the Λ problem; retro R025 (Ω_Λ) is SYNTHETIC/TUNABLE — never cite as a retrodiction |
| E032 | QM → measurement-outcome | **E3** | decoherence gives the diagonal (E1) but NOT single-outcome selection |
| E037 | string-theory → SM | **E3** | landscape: vacuum selection non-definable; even the leading candidate lands E3 |
| E041 | QCD → confinement | **E3** (theorem) / E0 (run-exhibited) | mass gap is an open Clay problem; lattice exhibits, no proof |
| E042 | GR → singularity-theorems | **E3** | GR locates its own boundary; the needed extension (E018) is unsupplied |

The Born rule (E007), the pointer-basis selection (E026), and the arrow of time (E030) are the
*near-miss* anchors: each looks like it might be a clean E1 shadow but is demoted to E2 because the
decisive piece is a NAMED import (Gleason/envariance; einselection criterion; the Past Hypothesis).
Recording these E2 prevents over-reading the E1 decoherence/limit shadows next to them.

## 5. Honest distribution (the registered null shape)

Pre-audit tier distribution over 42 edges:
- **E1 (computable descent): 17** — the shadow-heavy bulk, as predicted.
- **E2 (recognition-conditional): 12** — named-import landings, reported separately, never summed.
- **E3 (sharpened gap / foreclosure): 9** — located + typed, not closed.
- **E0 (run-only, deferred to the Run-Target Manifest): 4** — E001, E027, E031, E035.

This is the **predicted shadow-heavy / emergence-sparse** shape: downward shadows dominate (E1),
upward emergences and gaps are sparse and land E0/E3 (NEVER E1). E2 is a substantial but separate
band (deep reframings conditional on named imports). **E1 is never summed with E2/E0/E3.** This
distribution was produced edge-by-edge on the physics, NOT tuned to hit a target — but it does match
the foreclosure-dominance prediction, which is the framework working, not failing (primer §9 #8).

## 6. Sub-edge / over-read flags (anti-smuggling, recorded per row)

Several edges carry an explicit "the equations descend (E1) but the VALUES need a run (E0/E2)" split,
so the auditor cannot collapse the two and over-read an E1:
- E004 hydro: equations E1, transport coefficients toward E0.
- E008 EFT: RG structure E1, matched coupling values toward E0.
- E028 Λ-CDM: FLRW geometry E1, Λ + dark-matter content imported → whole edge E2.
- E029 ChPT: symmetry skeleton E1-like, LECs (f_π, condensate) E0 → whole edge E2.
- E038 universality: class assignment E1, precise exponent values toward E0.
- E040 Fermi liquid: stable case E1, breakdown (non-Fermi liquids) → E3 gap.
- E041 confinement: phenomenon run-exhibited E0, proof open-external E3.
- E027 SPT: realized-phase invariant E0 (run), classification side possibly E2 (named cohomology).

## 7. What this draft does NOT do (scope guard)

No computationally-irreducible runs are performed; no empirical predictions; no constant is derived.
Every E0 is FLAGGED OUT and DEFERRED to the Run-Target Manifest. Every "decisive"-sounding claim is
conditional on the audited casting and licensed only by the proton-mass calibration. The edges are
candidates for typing; the typing itself is the rubric's and the auditor's job.
