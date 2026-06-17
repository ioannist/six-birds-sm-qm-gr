# Layer-A Adversarial Review — Physics Layer Atlas, Phase-0 Bundle

**VERDICT: freeze-with-required-fixes**

Reviewer: Layer-A adversarial. Scope of audit: the four Phase-0 drafts + notes in
`physics_atlas/prereg/drafts/` (`SCIENCE_DIGEST.md`, `TYPING_RUBRIC.md`, `theory_manifest.jsonl`,
`edge_manifest.jsonl`, `theory_manifest_notes.md`, `edge_manifest_notes.md`).

**Bottom line.** The conceptual spine is sound and unusually honest: the up/down asymmetry is encoded
as a hard gate (rubric §C.6, E.8), Ξ is defined as finite linear algebra on declared toy models, the
hard/embarrassing edges (QM↔GR, gauge group, generations, Λ) are all present and pinned at E3 as
firewall anchors, foreclosure-dominance is registered as the *predicted* shape (not a target), and
the banned-language / no-summing discipline is correctly stated. **It is not freeze-ready as written**
because of one structural defect that breaks the artifacts' join integrity (the manifests do not link),
several real elasticity holes a determined modeler can exploit, one reductionist relapse in the
calibration set, and two modality/tier inconsistencies the deterministic procedure cannot actually
produce. These are fixable without weakening the framework; the fixes below *add* honesty, they do not
soften any verdict. The honest default on every doubt is to demand the more conservative casting.

---

## REQUIRED FIXES

### 1. (BLOCKER) The two manifests do not join — id scheme mismatch breaks every cross-reference.
**Target:** `theory_manifest.jsonl` and `edge_manifest.jsonl` (and both notes files).
**What is wrong:** The theory manifest uses `snake_case` ids (`quantum_mechanics`, `qcd`,
`classical_electromagnetism`, `lambda_cdm`, `condensed_matter_spt`, `hydrodynamics`). The edge
manifest uses `kebab-case` and *different spellings* (`quantum-mechanics`,
`quantum-chromodynamics`, `electrodynamics`, `lambda-cdm-cosmology`, `condensed-matter`,
`navier-stokes`). Programmatic join: **only 2 of 21 theory cards** (`hydrodynamics`, `thermodynamics`)
match an edge node id exactly; **40 of 42 edges** point at nodes with no theory card; **19 of 21
cards are orphans** referenced by no edge. After a naive `kebab→snake` normalization, 14 nodes would
join, but **6 peer-theory nodes still will not** because they are renamed, not just re-cased:
`quantum-chromodynamics`→`qcd`, `quantum-electrodynamics`→`qed`,
`electrodynamics`→`classical_electromagnetism`, `navier-stokes`→`hydrodynamics`,
`condensed-matter`→`condensed_matter_spt`, `lambda-cdm-cosmology`→`lambda_cdm`. This is a freeze
blocker: a frozen bundle whose edges cannot be resolved to its cards cannot be audited or replayed.
The drafter-4 notes even admit "If drafter 3 used a different spelling … the assembler should
reconcile" — punting reconciliation past the freeze is exactly what a freeze must not do.
**Exact fix:** Pick ONE id convention (recommend the snake_case theory-card ids as canonical, since
the cards are the frozen layers) and rewrite every `source_theory_id`/`target_theory_id` in
`edge_manifest.jsonl` to the canonical card id for the 14 peer-theory nodes that have a card. For the
6 renamed peers, add the explicit alias mapping above and apply it. Then add to BOTH notes files a
frozen alias/id table. Add a freeze-time assertion (to be enforced by the assembler): *every edge
`source_theory_id`/`target_theory_id` is either (a) a frozen theory-card id, or (b) a member of the
explicitly enumerated non-peer-node list (fix #2).* The bundle may not freeze while any edge node is
unresolved.

### 2. (BLOCKER) Non-peer "nodes" are introduced ad hoc and never given a typed status.
**Target:** `edge_manifest.jsonl`, `edge_manifest_notes.md`, and `TYPING_RUBRIC.md` §A/§C.7.
**What is wrong:** 25+ edge endpoints are not theory cards at all but three different *kinds* of node
mixed without a schema: (a) observable/phenomenon readouts (`hadron-spectrum`, `confinement`,
`turbulence`, `arrow-of-time`, `measurement-outcome`, `phase-transitions-universality`,
`singularity-theorems`, `berry-phase-holonomy`, `entanglement-geometry`); (b) "why this?"
question-nodes (`gauge-group-origin`, `fermion-generations`, `cosmological-constant`); (c)
candidate/sub-structure theories with no card (`effective-field-theory`, `conformal-field-theory`,
`string-theory`, `lattice-gauge-theory`, `quantum-field-theory-curved`, `chiral-perturbation-theory`,
`fermi-liquid-theory`, `spt-phases`, `decoherence-pointer-basis`, `classical-probability`,
`many-body-quantum`, `brownian-motion`). The rubric's decision-procedure (§C.5) requires **frozen
source card S and target card T** as a precondition (STEP 0: "Confirm S and T are frozen cards… If not
→ HALT"). As written, **40 of 42 edges fail STEP 0 and are un-typeable**, which contradicts the whole
exercise. This is also a smuggling surface: an un-carded node lets a modeler assert a casting (Z, f,
Σ_f, accepted_observables) on the fly to push a tier, defeating gate E.0 (which only bites carded
theories).
**Exact fix:** (i) Add a `node_kind` field to a node registry (either a new `node_manifest.jsonl` or
an enumerated, frozen list in `edge_manifest_notes.md`) classifying every non-peer node as exactly one
of `{observable_readout, open_question, candidate_substructure}`. (ii) In rubric §C.5 STEP 0, replace
the strict "S and T must both be frozen cards" with: a typed edge endpoint must be **either** a frozen
theory card **or** a frozen registered node of declared `node_kind`; an `open_question` target forces
the E0/E3 branch only (it can never seal E1/E2 — see fix #6); an `observable_readout` target is the
*readout* of its source card and inherits the source card's frozen casting (no fresh casting allowed);
a `candidate_substructure` node that is not experimentally established may not be the *source* of an
E1 descent (it has no accepted_observables to descend to). (iii) Promote `effective-field-theory` to
use the existing `rg_eft` card, or give it a card — it is currently the target of E008 and source of
E009 with no card, while `rg_eft` (a card) is an orphan. Resolve that overlap explicitly.

### 3. (REDUCTIONIST RELAPSE) The E2 calibration anchor mislabels its named import — the BH-thermo edge as written imports the wrong principle and risks an over-read.
**Target:** `edge_manifest.jsonl` E005; cross-check `TYPING_RUBRIC.md` §F and §C.2; `SCIENCE_DIGEST.md`
§5/§6.
**What is wrong:** E005 (GR → black-hole-thermodynamics) is the *required E2 calibration control*, and
its known answer must be unambiguous or the freeze-blocker is itself soft. Its notes say it "lands
only by IMPORTING a NAMED external source -- quantum field theory in curved spacetime (Hawking's
calculation)". But the rubric §F calibration table names the E2 control as "GR↔thermodynamics via
*Jacobson's equation of state*, or BH-thermo via the *Bekenstein–Hawking area law*", and §C.2 names
"Jacobson … or … Bekenstein–Hawking". Three *different* named principles (Hawking QFT-in-curved-
spacetime; Jacobson's equation of state; the Bekenstein–Hawking area law) are floated across the three
documents for the *same* calibration slot. A calibration anchor whose "named import" is not itself
frozen is gameable: a modeler can pick whichever named principle makes the casting land E2. Worse,
Jacobson's "Einstein equation of state" (E022) runs the *opposite* arrow (it *recovers Einstein's
equations* from thermodynamics) and is **not** the same edge as E005 (GR → BH-thermo). Conflating them
in the calibration table is a route-direction error of exactly the kind the up/down asymmetry forbids.
**Exact fix:** Freeze E005's named import to ONE principle and state it identically in all three
documents. Recommended: E005's named import = **QFT in curved spacetime (Hawking thermal flux) +
the first law of black-hole mechanics**, conditional on the no-back-reaction (semiclassical)
assumption — this is exactly the E034 edge, so make E005 explicitly cite E034 as the named source.
Remove "Jacobson" from the E005/§F slot entirely; Jacobson belongs only to E022 (a *separate*,
opposite-direction E2 edge). In §F, name the single frozen E2-control principle and forbid substitution
at audit time (add it to gate E.0's "named source must be frozen, not chosen at typing time").

### 4. (ELASTICITY HOLE) The conservative-default ordering is internally contradictory — "conservative" points in two different directions.
**Target:** `TYPING_RUBRIC.md` §A (last paragraph) vs §E.5 vs §D.1/§C.5.
**What is wrong:** §A states the informativeness order as "**E0 < E3 < E2 < E1**" while §E.5 states it
as "**E1 … then E2, then E0, then E3 the weakest**" (i.e. `E1 > E2 > E0 > E3`). These disagree on the
relative rank of **E0 vs E3**: §A ranks E0 as *least* informative (most conservative), §E.5 ranks E3
as least informative (most conservative). The decision-procedure §C.5 separately says "doubt at Step 3
⇒ fall to E3" (treating E3 as the conservative fallback below E0). So the bundle simultaneously asserts
E0 is the most-conservative tier (§A) and E3 is the most-conservative tier (§E.5/§C.5). A determined
modeler exploits this to route a doubtful run-only-looking edge either to E0 (deferred, no verdict —
flattering: "this is real emergence, just deferred") or to E3 (open gap — unflattering) depending on
which clause they cite. That is precisely the tunability the firewall must kill.
**Exact fix:** Delete the "E0 < E3 < E2 < E1" string in §A (it is acknowledged there as "not the rule"
anyway and only sows confusion). Adopt §E.5's single ordering everywhere: **conservatism/informativeness
= E1 (most-flattering) > E2 > E0 > E3 (least-flattering, the sharpened-gap default)**, and make §C.5's
fall-through monotone in it: doubt at Step 1 → not E1; doubt at Step 2 → not E2; doubt at Step 3 → not
E0, land E3. State once, in §E.5, that **E3 is the unique conservative terminal** and every "doubt"
demotes strictly toward it. (Note for the assembler: this also means E0 is NOT a safe haven for a
doubtful edge — sealing E0 requires the *positive* construction of a non-descending run-object per E.7,
never a fallback.)

### 5. (ELASTICITY HOLE) The toy-model adequacy problem is unfenced — drafter 2 flagged it and did not gate it; it is the single largest tunability surface.
**Target:** `TYPING_RUBRIC.md` §D.4, §E.1, §H; `SCIENCE_DIGEST.md` §3.
**What is wrong:** Drafter 2 explicitly states (rubric §H) the firewall's biggest unresolved hole: the
*choice* of the finite toy model `M` (carrier, probe families `L₀,D₀`, audit energy `C₀`) is itself a
modeling act that can drive Ξ→0 (force E1) or Ξ≻0 (force E3). Gate E.1 only requires `M` be declared
and hashed *before* computing — it does nothing to stop a *hand-picked* `M` that is declared up front
but gerrymandered. A determined modeler picks `L₀,D₀,C₀` at declaration time to get the tier they want,
hashes it, and passes E.1 cleanly. The calibration controls only catch this if the controls happen to
exercise the same gerrymander, which is not guaranteed.
**Exact fix (adopt drafter 2's own proposals (i)+(ii) as HARD gates):**
(i) Add gate **E.9 — refinement-stability**: an edge's Ξ=0/Ξ≻0 verdict must be **stable across at
least two declared refinements `h₁ ⊏ h₂` of `M`** (a coarser and a finer finite stage), with the same
qualitative verdict at both. A verdict that flips between refinements is **tier-fragile** (E.6) and
seals at the conservative tier (E3 per fix #4). This stops a single hand-picked finite stage from
fixing the answer, and — crucially — it stays inside scope because two finite refinements is still
finite linear algebra, NOT an irreducible run (state this explicitly to pre-empt the §H worry).
(ii) Add gate **E.10 — second-annotator `M`-faithfulness** (mirror the Erdős two-annotator rule): `M`'s
declaration (carrier, `L₀,D₀,C₀`, and the toy→`accepted_observables` readout map of §D.4.v) must be
certified faithful by a **second independent annotator before the hash**, on the standard of "this is a
minimal faithful finite stand-in for the theory-pair, not reverse-engineered from a desired Ξ." Log
both annotators with the edge.
(iii) Resolve drafter 2's open question (iii) in the rubric text, not in a footnote: a theory-pair with
**no honest finite toy model** (candidate: QM↔GR) must seal **E3 by the "no faithful M" route**, and
this must be recorded as a *distinct* E3 sub-reason ("no faithful finite stand-in exists") — NOT
silently folded into the descent-failed E3, so the reader can see the descent-test was *vacuous*, not
*run-and-failed*. Without this, the rubric over-produces ordinary E3 verdicts and hides which ones are
genuine located gaps vs. which are "we couldn't even build the test."

### 6. (DETERMINISM / MODALITY HOLE) Two edges carry a modality/tier pair the deterministic procedure cannot produce, and one E0 lacks its mandatory double-run interlock evidence.
**Target:** `edge_manifest.jsonl` E035, E027; `TYPING_RUBRIC.md` §C.5, §C.7, gate E.7.
**What is wrong:**
(a) **E035** (lattice-gauge-theory → quantum-chromodynamics) is tagged `modality: shadow-down` but
`tier: E0`. The §C.5 procedure can only seal E0 at STEP 3, which requires a **constructible
non-descending object** (a *non-factorization*/emergence finding, B.2). A `shadow-down` (descent,
B.1) edge that *passes* its descent test is E1; one that *fails* falls to recognition/run/gap. A
"shadow-down E0" is not a state the deterministic procedure emits — so either the modality is wrong
(the continuum limit's *readouts* are run-only emergence, modality should reflect that the physical
content is non-descending) or the tier is wrong. The notes even say "The continuum LIMIT is a descent
in principle, BUT every physical readout … is generated by RUNNING" — which is exactly the E0/E3 split
problem of §C.7, unresolved on this row.
(b) **E027** (condensed-matter → spt-phases) is `emergence-up / E0` but its notes also say the
classification side "may be E2 (named cohomology import)". Per gate E.7, an E0 seal requires BOTH the
descent-test AND recognition-search to have been *run and logged negative*. E027's own notes admit a
*positive* recognition candidate (group-cohomology classification as a named math import) exists —
which means recognition-search would NOT return negative, so E027 cannot seal E0 under E.7 as written;
it splits into an E2 (classification) part and an E0 (realized-phase-of-a-given-Hamiltonian) part.
**Exact fix:** (i) For E035: set `modality: emergence-up` for the *readout* content (the spectrum/scale
is non-descending and run-generated) and keep `tier: E0`, OR split the row into E035a (continuum-limit
*structure*, shadow-down, E1-candidate) and E035b (physical readouts, emergence-up, E0). State which in
the notes. (ii) For E027: split into E027a (SPT *classification* via named cohomology → E2-candidate,
recognition) and E027b (realized phase of a specific Hamiltonian, the invariant's value → E0-candidate,
run), so neither row violates E.7. (iii) Add to §C.5 an explicit **modality↔tier compatibility table**
naming which (modality, tier) pairs are emittable by the procedure, and require every edge row to
satisfy it at freeze (a `shadow-down E0` or `emergence-up E1` row is rejected at freeze).

### 7. (CALIBRATION ADEQUACY) The calibration set under-covers and the freeze-blocker is asserted but not wired.
**Target:** `TYPING_RUBRIC.md` §F; `edge_manifest.jsonl` (`is_calibration` flags); `edge_manifest_notes.md` §2.
**What is wrong:** (a) Only 5 edges are `is_calibration:true` (E001 E0, E002/E003/E004 E1, E005 E2);
**there is no calibration anchor for E3**. The notes argue "E3 has no known answer by definition," but
that is the wrong standard: E3 *is* checkable as a freeze-blocker by requiring that the four mandated
hard edges (E018 QM↔GR, E019 gauge group, E020 generations, E021 Λ) **must NOT come out E1 or E2** —
i.e. an E3 *anti-control* ("these must stay foreclosed"). Without an E3 freeze-blocker, the most
important firewall claim (SBT does not secretly derive the gauge group / Λ) is untested by the
calibration. (b) §F asserts a calibration FAIL "blocks the freeze" but nothing in the bundle *wires*
the block: the freeze workflow (`wf_phase0_freeze.mjs`) has no calibration-gate step, and the manifests
carry no machine-checkable "known_tier" field for the calibration rows (the known answer lives only in
free-text `notes`). An un-wired freeze-blocker is decorative.
**Exact fix:** (i) Add an **E3 anti-control** to the calibration protocol: the four hard anchors (E018,
E019, E020, E021) get `is_calibration:true` with a new field `calibration_known_tier:"E3"` and
`calibration_rule:"must_not_seal_E1_or_E2"`. Any of them sealing E1/E2 is a calibration FAIL (a
reductionist relapse — someone derived the gauge group / Λ). (ii) Add a machine-checkable
`calibration_known_tier` field to ALL five existing calibration rows (E001=E0, E002=E1, E003=E1,
E004=E1, E005=E2), so the freeze gate compares computed-tier to known-tier programmatically rather than
reading prose. (iii) State in §F (and have the assembler add to `FREEZE_NOTES.md`) the explicit
freeze-gate predicate: *freeze iff every `is_calibration` row's computed tier equals its
`calibration_known_tier` (or, for the E3 anti-controls, is in {E3, E0})* — and note that the workflow's
Assemble phase must enforce it.

### 8. (REDUCTIONISM / SCOPE) Several E1 "descent" edges are at risk of over-reading the source; the sub-edge value-splits are recorded in prose but not enforced.
**Target:** `edge_manifest.jsonl` E004, E008, E016, E017, E028, E029, E038; gate E.3.
**What is wrong:** Multiple edges seal (or guess) E1 for "the equations / structure" while admitting in
free-text that "the VALUES need a run (E0/E2)" (E004 transport coefficients, E008 matched couplings,
E029 LECs, E038 exponent values). This is the correct instinct, but it is **only in the notes** — the
E1 tier guess stands alone on the row. Gate E.3 (no-over-read) is supposed to catch this, but it has no
hook to the value-split: a downstream consumer reading only the tier sees "E1" and over-reads the edge
as a clean computable descent of the *physics*, when only the *form* descends and the *numbers* are
run-only. Also E016/E017 (SM→electroweak / SM→QCD) are called "Xi=0 trivially (direct-product
factorization)" and "kinematic factorization" — these are dangerously close to *within-a-layer*
restrictions (selecting a tensor factor of the same theory), i.e. the primer §3 "textbook in costume"
case, not a genuine inter-layer descent; if so they should be flagged "near-intra-layer, confirm
genuine quotient" (the rubric §9 / E.4 move), not counted as clean E1 descents that pad the shadow-heavy
total.
**Exact fix:** (i) Add a structured `value_split` field to any edge whose form descends but whose
numbers are run-only: `value_split:{form_tier:"E1", value_tier:"E0"|"E2", value_node:"<run-target>"}`,
and require the tier reported in any count to be the **form_tier**, with the value_tier carried
separately into the Run-Target Manifest — never summed (this is just the no-summing rule applied within
a single edge). (ii) For E016/E017, run the E.4 relabeling test explicitly and record the result: if
restricting SM to a gauge factor is a genuine quotient with its own Σ_f, keep E1 and say why it is not
intra-layer; if it is a within-layer restriction, mark it "within-a-layer, no SBT content" per
rubric §9 and **remove it from the E1 count** (do not let trivial factorizations inflate the
shadow-heavy distribution — that would be flattering-by-padding).

---

## OPTIONAL IMPROVEMENTS (not freeze-blocking, but they raise honesty)

- **O1. RG/EFT double-counting guard.** The `rg_eft` card is the explicit "textbook in costume"
  comparator, yet many E1 edges (E008, E038, E040, and arguably E002/E004) *are* RG/EFT descents. Add a
  per-edge boolean `is_rg_eft_descent` so the FREEZE_NOTES can report "N of the E1 shadows are exactly
  RG/EFT moves physics already does," pre-empting the charge that the atlas rebrands renormalization as
  novel SBT content.

- **O2. Directionality of E022 vs E005.** Beyond fix #3, add a one-line `arrow_direction`
  (`down`/`up`/`bidirectional`) to every edge so a reader can see at a glance that E022 (thermo→GR
  *recovery*) and E005 (GR→BH-thermo) run opposite arrows; this makes accidental route-mismatch
  conflation visible.

- **O3. Drop or card the orphan `rg_eft` vs `effective-field-theory` overlap** (touched in fix #2) —
  pick one canonical name; having both a card (`rg_eft`) and an un-carded node
  (`effective-field-theory`) for the same physics is an avoidable seam.

- **O4. State the registered-null numbers as a prediction, not a result.** Edge notes §5 reports a
  pre-audit distribution (E1:17, E2:12, E3:9, E0:4). Label these explicitly "PRE-AUDIT GUESS, not the
  audited verdict; recorded so the post-audit run cannot be tuned toward it" (the notes nearly say this;
  make it a frozen one-liner in FREEZE_NOTES so the count is a registered null, not a claimed finding).

- **O5. Add `confinement`/`mass-gap` and `turbulence` to the Run-Target Manifest spec stub now** (E041,
  E031), so the E0/E3 split (run-exhibited E0 vs open-theorem E3) is captured at freeze rather than
  deferred — these are the cleanest non-QCD demonstrations that the E0/E3 machinery is
  substrate-agnostic, and specifying them up front strengthens the calibration story.

- **O6. Fairness — consider one more genuinely-emergence-up candidate** beyond SPT/turbulence (e.g.
  superconductivity / BCS gap as a run-generated order parameter, already half-present via E040's
  Fermi-liquid breakdown) so the emergence-sparse side is not carried almost entirely by condensed
  matter; this guards against the appearance that emergence was confined to one comfortable corner.

---

## What I checked and found ACCEPTABLE (so the assembler does not "fix" what is right)

- **Hard/embarrassing edges are all present** and pinned at E3 as firewall anchors: QM↔GR (E018), SM
  gauge group (E019), three generations / mass hierarchy (E020), cosmological constant (E021), plus
  honest extras (measurement problem E032, string landscape E037, confinement E041, singularity
  theorems E042). The notes correctly tie these to the retrodiction-atlas finding that all decisive
  content is imported or disclaimed. **Do not soften any of these.**
- **The up/down asymmetry is correctly encoded as a hard gate** (rubric §C.6, E.8): no edge may seal E1
  via an up-direction computation; emergence is certified as a *gap*, never derived. This is the
  load-bearing primer §6 rule and it is implemented, not just stated.
- **Ξ is operational** — finite Schur complement on declared finite carriers, with the
  `Ξ=0 ⟺ ker-containment ⟺ factorization` equivalence taken verbatim from the adequacy paper. The
  computability claim is honest (subject to fix #5's M-choice hole).
- **No constant is derived; the run is correctly deferred.** The proton-mass E0 anchor (E001/E035) is
  spec'd, not run; "derive the proton mass" never appears; the hard-scope boundary (no irreducible runs,
  no empirical claims) is respected throughout. The banned-language and no-summing rules (rubric §G) are
  correct and complete.
- **Within-a-layer silence is stated** (rubric §9, digest §9, every theory card's notes) — SBT scores
  nothing inside a layer. (Fix #8(ii) only asks that two *specific* edges be checked against this rule,
  not that the rule be changed.)

---

**Return:** verdict = freeze-with-required-fixes; required fixes = 8.
