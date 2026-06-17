# External Review v1 — PAUSE 1 (Freeze Gate) — VERDICT + Required Changes

**Date:** 2026-06-04 · **Reviewer:** independent external agent (zip-only, no repo access) ·
**Verdict:** **APPROVE-WITH-REQUIRED-CHANGES** · **Integrity:** `sha256sum -c` OK on all 9 frozen targets.

> **Summary (reviewer):** Conceptually serious — hard edges present, no-derivation/no-summing explicit,
> Ξ a real finite Schur-complement diagnostic, proton-mass E0 correctly deferred. Layer-A fixes helped.
> **The dangerous weakness: the firewall is still partly *declarative*** — full closure-package castings
> are not actually frozen; several manifest labels don't match the rubric's machine-emittable modalities;
> the calibration gate is claimed programmatic but has no executable frozen validator. Fixable, not cosmetic:
> without them a later modeler can still tune castings, edge direction, named imports, or schema interpretation.

## REQUIRED CHANGES (must all be applied for freeze)

- **R1 — Freeze full closure-package cards.** Manifest holds only stubs (`provisional_Z/f/E`); rubric §A
  requires full cards with `Z, f, Σ_f, E, D, accepted_observables, lawful_layer_note, casting_justification,
  casting_alternatives`, frozen *before* edges are typed. → Add a hashed `closure_card_manifest.jsonl` with
  the full §A schema for **all 21 theory cards + any node that needs a casting**; add a hard "full-card freeze
  before any `M` declaration or Ξ computation" gate to FREEZE_NOTES + SHA256SUMS.
- **R2 — `recognition-landing` is not a canonical modality.** 7 edges (E007, E022, E025, E026, E027a, E030,
  E033) tag modality `recognition-landing`, but §B has no such modality (recognition is a *tier mechanism*).
  Breaks the machine-checkable `(modality,tier)` gate. → Either add `recognition-landing` as an explicit §B
  modality with a crisp operational test + §B.8 compatibility row, **or** retag to existing modalities and keep
  "recognition" only as the E2 landing mechanism. Add a schema check rejecting non-canonical modality strings.
- **R3 — E022 endpoints reversed.** JSON says `general_relativity → thermodynamics` but the note/rubric say
  Jacobson recovers Einstein eqs *from* thermodynamics (`thermo → GR`, the opposite-arrow recovery). The exact
  route-direction error Layer-A warned about, incompletely fixed. → Set `source=thermodynamics, target=general_relativity,
  arrow_direction=up` (or split into two edges). Update all notes + import refs.
- **R4 — E007 (Born rule) has an import *menu*.** Gate E.0 freezes one named import at declaration; E007 lists
  Gleason / envariance / decision-theoretic as alternatives in free text = tune-at-typing seam. → Freeze ONE
  named import + one closure assumption (or split into separate conditional E2 rows). No alternative menu.
- **R5 — `value_split` schema overloaded.** Schema is "form descends E1, values E0/E2"; E041 uses
  `{form_tier:E3, value_tier:E0}` (open-theorem vs run-exhibited) — good distinction, wrong schema. → Generalize
  the schema to allow non-E1 split types (e.g. add `split_type`), or add `theorem_run_split`. Keep no-summing.
- **R6 — `candidate_substructure` sourcing E1 without established status.** Rubric forbids a non-established
  candidate_substructure from sourcing an E1 descent, but the node registry has no machine-readable status.
  E035a (`lattice-gauge-theory → qcd`) and E040 (`many-body-quantum → fermi-liquid-theory`) both do this. → Add
  `established_status` / `may_source_E1` to the node registry, justified per node; promote to full cards where
  needed, or mark those E1 guesses unsealed/conservative.
- **R7 — Calibration gate is declarative, not executable.** FREEZE_NOTES/rubric claim the Assemble phase
  enforces the calibration predicate programmatically, but the workflow only prompts an agent; no computed-tier
  validator exists, and the workflow isn't in SHA256SUMS. → Add a hashed `validate_freeze_gate.mjs` that reads
  scored edge rows and checks endpoint resolution, canonical modalities, `(modality,tier)` compatibility,
  calibration known-tier rules, anti-control rules, and no-summing/value-split schema, exiting nonzero on
  failure. Add it (and the workflow) to SHA256SUMS.
- **R8 — QCD calibration slogan too blunt.** "QCD has no free mass parameter" → revise to: "no free
  proton/hadron *mass* parameter; quark masses and coupling/scale are fixed independently under the declared
  lattice-QCD protocol; the proton mass/hadron-spectrum readout is out-of-sample and not fitted." State whether
  calibration is chiral-limit, pure-gauge, or physical-quark-mass lattice QCD.

## OPTIONAL IMPROVEMENTS (adopt — honesty wins)

- **O1 — Split E028 (`lambda_cdm → general_relativity`).** Carries contradictory `shadow-down`+`arrow:up`+`E2`.
  Split into a geometry-descent (FLRW from GR, E1) row and an imported-content (Λ/DM/IC, E2) row.
- **O2 — Registered-null caveat.** E1=18 includes 3 pending near-intra-layer candidates (E016/E017/E039). The
  null table must say "audited E1 must remove any that fail gate E.4."
- **O3 — Separate Higgs/electroweak-naturalness hierarchy edge.** So "mass hierarchy" can't be read as covering
  only fermion generations.
- **O4 — Tighten the `{E3,E0}` anti-control rule.** E0 passes an anti-control only if its run-target stub was
  frozen before scoring and satisfies gate E.7 — else E0 becomes a flattering "real emergence, deferred" haven.

*(Full per-axis findings and integrity check are in the conversation record; this file is the actionable
remediation contract and the provenance record of external review v1.)*
