# Phase 4 — external-review remediation (R1–R4)

**Verdict:** APPROVE-WITH-REQUIRED-CHANGES → all four applied; reviewer's standing condition was *"after
these corrections, I would approve closing Phase 4."* Flags 1, 4, 6, 7 ratified; 2, 3, 5 had local
bookkeeping/wording fixes. No new constant, run, experiment, or smuggling relapse was found. Each fix was
re-verified against the authoritative manifest before editing.

- **R1** — `PHYSICS_LAYER_ATLAS_FINAL.md` §2 + §4. "12 E3 gaps" / "hard frontier (12 E3)" → **"12 E3-scored
  rows, 10 foreclosure-relevant"** / **"10 foreclosure-relevant E3 gaps + 2 within-layer sentinel rows
  E016/E017."** Stops E016/E017 being read as ordinary missing layers.
- **R2** — `PHYSICS_LAYER_ATLAS_FINAL.md` §2. "each carrying an `out_of_sample_test`" →
  **"each carrying either an out-of-sample structural test or an explicit `not_yet_genuine` marker (E042 is
  the sole current failure)."** Preserves the Stage-2 firewall exception.
- **R3** — `RUN_TARGET_MANIFEST.md`. Added **Section A′ — Non-headline E0 value-split sub-targets**
  (E004 transport coefficients, E008 matched couplings, E038 critical exponents, E041 confinement string
  tension): each an **E0 *value* leg** whose headline tier is E1/E3, explicitly **not** in the 4-row E0
  count, **not** a new experiment, **deferred**, **never summed** — per the manifest's own "carried
  separately / carried into the Run-Target Manifest" stamps. E041's run leg is the same lattice-QCD family
  as E001/E035b; E004/E008/E038 add three further already-routine run methods. Section D's value-split
  parenthetical completed to list all of them.
- **R4** — `RUN_TARGET_MANIFEST.md` E001 row. Added the scale-setting precision: the readout is
  out-of-sample **"except for the single observable used to set the scale; the reported proton/hadron
  readout must not be the fitted scale-setting input"** (preserves the R8 lattice-QCD calibration wording).

**Invariants unchanged:** no tier, count, value-split boolean, or headline finding was altered; the
foreclosure map (46 rows; E0=4/E1=17/E2=13/E3=12, 10 foreclosure-relevant) and the deflationary QCD answer
stand. The fixes are bookkeeping/wording only.
