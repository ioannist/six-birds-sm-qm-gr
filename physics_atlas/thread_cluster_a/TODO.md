# Cluster A (SM selection / gauge-structure) — open TODOs

> Track: the Standard-Model selection layer (E009·E019·E020·E037·E043) + the Mode-B gauge-structure
> discriminator hunt. Session label "Cluster A" = the atlas's "Cluster B" (see `NAMING.md`).
> This file tracks open directions so future steps can refer to them. Status: `[DOING]` / `[TODO]` / `[OPEN-Q]`.

## Settled state (as of Step 39)

The discriminator hunt is **fully scrutinized and settled** at the structure level. Honest grade (per the v4
external review, accepted): **CONDITIONAL finite shadow-uniqueness** — the framework's neutral closure+descent
principles narrow ~11,990 genuinely-chiral gauge theories (corrected window) to the small family
**{2|3, SU(4)-alone}**; then an **introduced** clean-separation condition selects the **SM structure
SU(2)×SU(3)×U(1)**. The condition is detector-clean (not shape, not minimality — Step 38) but **CHOSEN, not
derived** (Step 39: the "standardness" grounding is circular; Step 41: it = `Δ_fact=∅`, a recognition source).
So: **NOT "SM gauge structure generated"; NOT frame-transfer.** The honest publishable claim: *a bounded finite
SBT discriminator **conditionally** selects the SM-like SU(2)×SU(3)×U(1) over a single-factor SU(4)-like
alternative, **provided** one imposes clean separation between mass-breaking and confinement; the condition is
physically motivated but not derived.* Caught + rejected en route: the SU(2)-cubic bug (Step 33), the
shape-flavored `factor_local_breaking` (Step 37), the minimality `currency` rescue (Step 37). Content within
2|3 is the observed-input type-limit (8 SM-signature rosters, F26). Standing caveats: bounded window;
frame-transfer unproven; finite toy.

## Paper-ready synthesis (read first when writing up)

- **`MAIN_RESULTS.md`** — START HERE. The complete index of the track's main results (A–I), each with its
  honest grade + step pointers: the selection layer (A), content type-limit (B), F24 architecture/naturalness
  (C), conditional gauge-structure selection (D), clean-separation = recognition source (E), window-closure (F),
  the X/Y-coset unification spine (G), the GUT-problems × F-laws reframing (H), and the N_gen type-limit (I).
  Dead-ends omitted.
- **`SM_TRACK_CLOSEOUT_QUESTIONS.md`** (planned, #8 below) — the limits/scope companion to `MAIN_RESULTS.md`:
  the precise "SM-like" definition, the claim ladder, the assumption-removal ladder, and the residual open
  questions. Read it next to `MAIN_RESULTS.md` so the paper neither overclaims nor leaves scope implicit.
- **`UNIFICATION_xy_coset.md`** — result G in depth: the central through-line: ONE structural object (the X/Y colored coset =
  the Δ_fact witnesses) recurs across 5 step-records (38/41/45/46/47) as: clean-separation-violator,
  factorization-defect, proton-decay mediator, monopole coset, and GUT↔SM refinement-witness. Its **absence**
  in the SM-clean structure gives all of them. Includes the honest grade (all StructDown / conditional on
  clean-separation / none physically certified) that must travel with the result.
- **`clean_separation_corpus_findings.md`** — what SBT says about clean-separation (recognition source).
- **`gut_problems_vs_sbt_laws.md`** — the GUT-problems × F-law map.

## Open directions

### 1. [DOING] Correct record + repackage for external review (v4)
- Apply the original review's **R1–R7** to the smuggled Steps 23–26 (disclose the `total_slots=5` + exterior
  content prior as INPUTS; demote "candidate-law / un-smuggled / generated" → "recovery inside a declared
  GUT-exterior prior"; harden the validators to require constant-valued obstruction rules to be declared;
  regrade Step 25 F51 as a pattern-table audit; drop the Step 26 normalization from the landing).
- Fold in the honest, scrutinized hunt (Steps 28–39) as the genuine structure-level result.
- Rebuild the packet (`sm_selection_layer_v4`) leading with the corrected status.
- **Send the clean-separation condition's *fundamentality* to external physics judgment** — established to be
  NOT toy-derivable (Step 39), so external review is its right venue.

### 2. [DONE — Steps 48-49] Content cascade — concluded: contingent-modulus type-limit (well-supported)
- Relabeling-quotient (conjugation/rep-equivalence/charge-normalization) reduces the 8 SM-signature 2|3 rosters
  to **2 distinct content classes**: the SM + 1 SM-signature alternative.
- Two genuinely-distinct, SM-content-independent shadows tested, **each with teeth** (each rejects a degenerate
  control) but **both blind** to the SM-vs-alternative distinction: integer charge-quantization of the physical
  color-singlet spectrum (Step 48) and generic Yukawa-texture connectivity (Step 49).
- Verdict: the residual content choice is an **F26 contingent-modulus / observed-input boundary**; the final
  pick needs an **E0 emergence run, excluded by design** → a legitimate type-limit (a door to the matter/observed
  boundary, not a wall). Matches physics (content is observed-input). Caveat: 2 blind shadows is strong support,
  not a proof; more shadows could in principle distinguish (diminishing returns).
- Note: **N_gen lives in this residual** → TODO #7 is the focused continuation (and is the harder anomaly-blind door).

### 3. [MOSTLY DONE — Steps 43-44; single-factor axis UPGRADED to a `constructed_theorem`, Step 61] Window-closure theorem (robustness) — discussion point (3)
- Attacked the bounded-window caveat. Result (conditional 2|3 selection) is STABLE across the widened covered
  window (factors 1-3, dims 2-6). Axis status: **single-factor closed to ∞** (cap-independent coset argument:
  any single SU(N) broken leaves charged coset vectors → fails clean-separation, all N — Step 43); **dimension
  stable to 6** (SU(4/5/6) add 0 clean survivors); **factor-count ≥3 closed only WITHIN the cap-6 window**
  (3-factor fields need dim ≥ 8 > cap 6; cap = SM's Q dim 2×3=6 — **cap-conditional, NOT a true ∞-bound**;
  larger cap untested — Step 44).
- Honest net: a real strengthening (one genuine ∞-bound + dim/cap-6 stability), NOT a full "survives
  everywhere" theorem. Result UNCHANGED in status: conditional on clean-separation, finite toy, no
  frame-transfer. Residual (low priority, diminishing returns): cap-independent factor-count ∞-bound (enumerate
  dim≥8 all-factor rows with a larger cap) — result stays conditional regardless.

### 4. [DONE — Steps 45-46 typed the forks; RESOLVED to clean by memory-stability, Step 65] Proton decay (F27) + monopoles (F48)
- Both typed via the SAME shadow-vs-dynamical-breaking lever and the SAME object: the X/Y colored coset
  (= the Step-41 Δ_fact witnesses = exactly what clean-separation forbids). **Step 45 (F27):** clean/shadow SM
  → baryon number descends through the orbit quotient → proton stable; dynamical-breaking → X/Y enlarge orbits
  (mix q↔lepton) → B violated → decay. **Step 46 (F48):** clean/shadow → 0 gluing obstruction → no monopole;
  dynamical-breaking → charged coset → nonzero gluing obstruction → monopole.
- Honest grade: **CANDIDATE forks typed, NOT solutions.** SBT shows the two readings predict differently;
  proton-stability + no-monopole in the clean/shadow reading are **consequences of clean-separation**
  (introduced/conditional); SBT does **not** resolve which reading is physical (recognition/frame-transfer
  open). Overclaim gates forbid "solves proton decay / the monopole problem" and enforce
  `physical_reading_resolved=False`. Both validators pass; negative controls have teeth.
- Note: this is a coherent unification — the SM-clean structure evades *both* classic GUT problems by the same
  property (no realized X/Y coset, Δ_fact=∅) that gave the conditional gauge-structure selection.

### 5. [RESOLVED → recognition source; GROUNDED one layer up in memory-stability, Steps 57-59] Clean-separation fundamentality
- Is "no confining-charged broken vectors" FUNDAMENTAL or chosen? **Resolved by a wide corpus search**
  (3 independent reads; see `clean_separation_corpus_findings.md`): SBT has real machinery clean-separation
  maps onto — non-factorization `Δ_fact` (Foundations III Thm 12/13, the precise home), SDTC/F14 (the
  duality-confinement resonance), F28/Foundations-II (coexistence + no-smuggling hygiene) — but **every
  relevant law is a neutral equivalence or a supplied conditional; none forces it.** Verdict: clean-separation
  is **introduced — a *recognition source*** (a named SBT category: supplied at the formed layer, audited
  downstream, not derived). Independently confirms Step 39 (circular) from the papers.
- **Framework-native restatement** (sharper than "no confining-charged vectors"): clean-separation =
  **`Δ_fact = ∅`** between the confining-sector quotient and the mass-sector quotient; the contaminating
  confining-charged broken vectors are the Δ_fact *witnesses*. Computed/instantiated in **Step 41**.
- Corrections logged: currency–constraint duality is *vertical* (not a ledger-separation); F37 is the *dual
  polarity* (cannot-be-joint), not clean-separation. See the findings note.
- Whether the recognition source corresponds to real physics = the standing **frame-transfer** question (external).

### 6. [DOING — Step 66 opened E032 on this thread] Atlas frontier — quantum measurement (E032)
- **E032 measurement** opened 2026-06-10 on the cluster_a thread (the record/measurement layer this track climbed
  into via Steps 57–59). **Step 66: `RECORD_STABILITY_BLIND_TO_SELECTION`** — the SBT-distinctive attack (does
  record-stability *force* the single-outcome/definiteness predicate, the way it forced clean-separation?) returns
  a clean **typed no-go**: per-branch records satisfy a non-circular record requirement (MWI-like readout not
  excluded), so records do **not** force selection. Reproduces the E032 B.2 non-factorization witness faithfully.
  Sharp contrast with clean-separation (same machinery forced *that*, not *this* — the framework discriminates).
- **Step 67: `SELECTION_RECORD_IRREDUCIBLE_STRUCTURAL`** (option (a) done — the prize). Strengthened to a
  **class-level structural no-go**: no Σ_f-internal record property can force selection (records are Σ_f-internal;
  the witness gives identical Σ_f on the two readouts; any Σ_f-definable property agrees on both). Battery of 4
  stronger properties (self-location, intersubjective agreement, robustness, completeness) all blind; the
  `global_exclusivity` anti-control is the flagged smuggle line. So **measurement-selection is record-irreducible**
  — a genuine **irreducible strict extension of QM** (non-definable from Σ_f).
- **Converged deliverable:** the only ways to force selection are smuggle-uniqueness (= definiteness) or **beyond-Σ_f**:
  touch **D** (collapse / shape A) or add a **non-Σ_f indexical selector** (MWI / shape B) — the **D-vs-Σ_f
  falsifiable discriminator**, now forced as the *only* remaining move (records cannot avoid it).
- **Step 68: `BOTH_SHAPES_INSTANTIATED_DISCRIMINATOR_CLEAN`** (option (b) done — the closing deliverable). Built
  both minimal exemplars: **shape A** (collapse / D-touch: stochastic pruning, new `lambda_collapse`, idempotence
  broken) and **shape B** (MWI / Σ_f-indexical: D/E unchanged, per-copy self-locating readout) — **both reproduce
  the Born weights**, genuinely distinct, **no side picked**. The **D-vs-Σ_f discriminator cleanly + uniquely
  separates them**.
- **[DONE — E032 deliverable complete, Steps 66–68].** Honest, SBT-native, falsifiable: *measurement-selection is a
  proven irreducible strict extension of QM (non-definable from records/Σ_f), and the D-vs-Σ_f discriminator is a
  no-fitting test* — D-touch ⇒ collapse, Σ_f-only ⇒ MWI, **neither ⇒ falsified**. Does NOT solve measurement or pick
  collapse-vs-MWI (the open physical content, by design). Finite toy; no frame-transfer. Falsifiable test recorded
  in `FALSIFICATION_ROUTES.md`. A short consolidated `E032_DELIVERABLE.md` (mirroring `LANDED_vs_NOT.md`) could be
  written if a paper-ready capstone is wanted.

### 7. [DONE — Step 51] E020 — three generations / "why N_gen = 3" (specialization of the content cascade #2)
- **Result (Step 51, N_GEN_BLIND_TYPE_LIMIT):** SBT does **not** derive N_gen=3 — exactly as the harder-door
  scoping predicted. Rigorously established on a neutral N∈{0..6} carrier (no privileged 3): (a) the full
  closure chain is **N_gen-BLIND** (passes identically for every N≥1 — Witten parity 4N even, everything
  per-unit); (b) minimality picks **N=1** (wrong; also the no-rig control); (c) the only handle is a
  **recognition-source lower bound N≥3** from CP violation (phase count `(N-1)(N-2)/2 > 0 ⟺ N≥3`,
  observed-input, a bound not a selection). "Closest to exactly 3" = *minimal N consistent with CP violation = 3*,
  but **doubly conditional** (recognition [observed CP] + minimality [suspect]), NOT a derivation. So N_gen is an
  **F26 contingent modulus / observed-input** type-limit; "why exactly 3" needs observed input / an E0 run
  (excluded by design). "3"-anti-smuggle gate passed. A door to the observed-input boundary, not a wall.
- (Historical scoping retained below for context.)
- **Status (from a prior external review, still accurate):** SBT has NOT independently derived N_gen=3. It has
  *typed* it as a selection/generative missing-layer problem (F26 contingent modulus) and shown structural
  constraints don't uniquely pick the SM content (Step 16: 28 anomaly-free supports → 2 survivors → choosing
  one needs additional input). N_gen lives in our current content type-limit (the 8 SM-signature rosters in 2|3).
- **Why it is HARDER than the gauge structure (the decisive caveat — do NOT expect a derivation):**
  **anomaly-freedom is N_gen-blind** — one SM generation is anomaly-free by itself, so N copies are anomaly-free
  for any N. The ENTIRE neutral-closure machinery that narrowed the gauge structure (anomaly/chirality/packaging/
  mass-closure) is per-content-unit and therefore CANNOT see the generation count. The handles that *do* see
  N_gen (topological index = family number, compactification invariants, family/flavor anomalies) import
  geometric/topological/GUT/string structure that is NOT neutral — exactly where a "3" smuggle would hide.
- **Honest expectation (doors-not-walls, but no over-promise):** the realistic landing is a **type-limit /
  recognition-source** result — type N_gen as a contingent modulus; test whether any neutral higher-layer
  principle (family-replication consistency, a flavor-anomaly condition, a stability/run criterion) constrains
  it (expect mostly typed no-gos); and if only an index-style import *relates* 3 to topology, NAME it a
  recognition source. NOT "SBT derives three generations."
- **The bar (the prior reviewer's 7-point spec, adopted):** (1) neutral carrier with N_gen ∈ {0,1,2,3,4,…} and
  no privileged 3; (2) a real GENERATIVE principle (P2+P5+P6), not just a selection score; (3) a
  non-factorization witness against the SM — concretely a **nonempty Δ_fact** between the candidate family-layer
  readout and the SM's own Σ_f (must split an SM-degenerate pair; same Δ_fact tool as Step 41); (4) a P6
  degeneracy-collapse audit landing on 3, robust under random/adversarial refinement orders + carrier
  expansions; (5) a real-physics carrier (chiral reps, anomalies, Yukawa/mixing, neutrino sector), not toy
  codes, for any frame-transfer claim; (6) an anti-smuggle gate SPECIFICALLY for "3" (forbid literal 3 /
  "three" / target bonus / candidate-space imbalance / GUT-string labels as selectors — same discipline that
  caught total-slot-5); (7) an out-of-sample consequence (hierarchy/mixing/neutrino/4th-gen constraint) not used
  to build the carrier. Success may be **E0** (run-only) if 3 appears only by running a substrate — acceptable
  iff the run is real and 3 is not preloaded.

### 8. [DONE — Steps 52-53 + close-out doc] SM-track close-out (scope/limits hygiene — no new derivations)
- **DONE:** Step 52 (clean-sep minimality → NOT minimal, proton-stability relocation; result E sharpened),
  Step 53 (competitor table; result D extended), `SM_TRACK_CLOSEOUT_QUESTIONS.md` (the 10-section scope/limits
  companion). **v7 review packet: NOT prepared (user deferred 2026-06-08 — "do not prepare a review package yet").**
**Purpose.** The core generative loop has landed its honest results (A–I in `MAIN_RESULTS.md`). This item is
**close-out hygiene**, not new content: pin down *exactly* what is and is not claimed, the precise definition of
the thing selected, and the full assumption stack — so the paper cannot overclaim and the scope is explicit.
Most of it is a **manager document**; **two** sub-questions would be soft overclaims if merely asserted, so they
become real codex steps that *compute* the answer. Standing caveats apply throughout (finite toy; bounded window;
frame-transfer unproven; conditional on clean-separation). Doors-not-walls: each open question below is where the
scope gets pinned, not a wall.

- **Step 52 (codex) — clean-separation minimality test.** Clean-separation (`Δ_fact=∅`, "no confining-charged
  broken vectors") is the load-bearing introduced recognition source (result E). Test whether it is *minimal* or
  whether a strictly **weaker** condition already selects 2|3, by running ~**3 representative weaker variants** on
  the same ~11,990-theory carrier: (a) **no-light-X/Y** (allow the coset but require it heavy/decoupled);
  (b) **no-baryon-violating-X/Y** (forbid only the orbit-enlarging subset, F27); (c) a bare
  **proton-stability condition** (require B to descend, nothing more). For each: does the survivor family stay
  **{2|3}**, grow, or collapse? Report **collapse-or-weaker** honestly — if a weaker condition suffices, the
  result strengthens (less is assumed); if not, clean-separation is shown minimal/load-bearing. **Anti-smuggle
  gate specific to this step:** the variants must not re-encode "2|3" / colorless-breaking / the SM hypercharge
  as a selector. Expected: a typed minimality verdict, NOT "SM derived."
- **Step 53 (codex) — competitor structures in/out of window.** Run the **in-window** competitor gauge structures
  through the *actual* Step-28→38 filter and **table** the out-of-window ones with the reason. Competitors:
  Pati–Salam `SU(4)×SU(2)×SU(2)`, left–right `SU(3)×SU(2)×SU(2)×U(1)`, trinification `SU(3)³`,
  flipped `SU(5)`, `SU(5)`, `SO(10)`, `E6`. Classify each: **in-window** (and what the filter does to it),
  **cap-excluded** (factor-count/dimension cap — flag cap-conditional per result F), **filter-excluded**
  (fails clean-separation / chirality / mass-closure — say which gate), or **future** (outside the declared
  carrier). Output a single competitor table for the paper. Expected: shows the selection is *against named
  alternatives*, not just an abstract enumeration — without claiming the table is exhaustive.
- **`SM_TRACK_CLOSEOUT_QUESTIONS.md` (manager doc)** — the limits/scope companion to `MAIN_RESULTS.md`. Ten
  sections, anchored on a **precise "SM-like" definition** (#13 of the close-out list) and the **claim ladder**,
  folding in close-out points #1/#2/#5–#12 and the results of Steps 52–53:
  1. **The accepted claim** (the exact claim ladder — what *is* and *is not* asserted, copied from MAIN_RESULTS).
  2. **Precise "SM-like" definition** — what counts as "the SM structure" the discriminator selects: gauge group
     up to global quotient? hypercharge normalization fixed or free? rep content vs group only?
  3. **A/B/C assumption stack** — full provenance (A imported standard physics, B posited SBT primitives,
     C choices/stipulations); reuse the v4 `ERRATUM_v4_provenance.md` map.
  4. **Selected-vs-not-selected** (#5) — positive selection vs negative exclusion: what the filter *positively*
     picks vs what it merely *excludes*.
  5. **Competitors in/out of window** (from Step 53).
  6. **Clean-separation status / alternatives / failure-modes** (from Step 52 + result E + corpus): recognition
     source; minimality variants; what breaks it.
  7. **Content cascade F26** (#6, #2) — the 2 residual content classes; the 2 blind neutral shadows; the
     observed-input boundary.
  8. **Proton/monopole forks** (#9) — conditional diagnostic forks, NOT predictions (`physical_reading_resolved=False`).
  9. **Global-quotient (Z6) + hypercharge limits** (#1, #2) — product `SU(3)×SU(2)×U(1)` vs quotient
     `…/Z6`: what the toy can/can't see about the global structure; hypercharge normalization status. *This is
     the key new limit to state plainly* — the toy works at the Lie-algebra/product level and does not certify
     the global quotient.
  10. **Assumption-removal ladder** (#11) — which assumptions, if removed, collapse the result, ranked; plus the
      parked items: three generations (#7, result I); **Higgs sector imported** and **naturalness flatly
      "not addressed"** (#8); the 2|3-vs-3|2|1 ordering note (#12).
- **(Optional) v7 external-review packet** — bundle Steps 52–53 + the close-out doc once the above are done, only
  if an external pass on the scope statement is wanted.
- **Scope guards (binding for this item):** keep Step 52 to ~3 variants (don't enumerate all weakenings);
  naturalness = flatly **"not addressed"** (do not reframe as progress here); the doc is **scope/limits only** —
  zero new derivations; pair it with `MAIN_RESULTS.md` (results) so the two travel together.
- **Why-question resolution table added** to `SM_TRACK_CLOSEOUT_QUESTIONS.md` §0 (2026-06-08): maps each
  "why this/that?" SM question → resolution kind (conditional-discriminator / typed-fork / true-negative /
  Type-B-proven-blind / smuggle-only / door-to-E0 / walkable-now); records the Type-A-vs-Type-B "No"
  distinction, the unifying excluded-by-design E0 door, and the two walkable doors (→ #9). Folds in the
  previously-unrecorded `sin²θ_W=3/8` downgrade and the anthropic point.

### 9. [DONE — Door 1 (Step 54, blind); Door 2 (Step 55, recovered-but-blind)] Two walkable doors (no E0 run needed)
**Both doors walked; neither narrowed the residual** — confirming (as the Type-B / intentional-gap analysis
predicted) that these are genuinely the framework's observed-input boundary, not unrealized derivations.
Recorded in `SM_TRACK_CLOSEOUT_QUESTIONS.md` §0; these are the only two genuine, un-walked, within-paradigm
construction doors from the gap analysis (everything else is observed-input/Type-B-proven-blind, smuggle-only,
or a door to the deliberately-excluded E0 emergence layer). Attempt as **sequential codex steps** if pursued.
- **Door 1 — 3rd neutral content shadow (sharpens gap #11 / result B). [DONE — Step 54: `CONTENT_TYPE_LIMIT_3_SHADOWS_BLIND` — did NOT narrow; the chosen mass-matrix-rank shadow is definitionally distinct from connectivity but coincides extensionally with it on this carrier, so confirmatory not strongly-independent evidence. Type-limit holds.]** Steps 48–49 left **2** SM-signature
  content classes, blind to **two** SM-content-independent shadows (integer charge-quantization; Yukawa-texture
  connectivity). Test a **third genuinely-distinct** SM-content-independent shadow (e.g. a discrete/global anomaly
  on the full roster, B−L gauge-ability, or a Yukawa/mass-texture-rank condition); if it distinguishes the SM from
  the single alternative class it narrows **2→1 with no E0 run**. Honest expectation: likely confirms the
  type-limit. Anti-smuggle: shadow must be SM-content-independent (Steps 48–49 discipline) + a "no-target-class"
  scoring gate.
- **Door 2 — global-quotient / Z6 / hypercharge-pattern carrier (gap #8 partial; the §9 limit). [DONE — Step 55: `GLOBAL_QUOTIENT_RECOVERED_SELECTION_BLIND` — the toy now COMPUTES the global quotient (exhaustive center search, NOT posited; validator fails if "Z6" is hard-coded in the solver) and RECOVERS the SM's `Z6` as a computed property (recovery of known physics, NOT a derivation; hypercharge pattern is input); but the nontrivial-center requirement does NOT discriminate (the alternative class also computes to `Z6`). §9 computational-blindness lifted; global structure not a selector; `sin²θ_W` untouched.]** The filter is
  algebra/product-level and blind to `(SU(3)×SU(2)×U(1))/Z6`. Design a Mode-B carrier that tracks **global
  structure** (representation lattice / fundamental group / compact-U(1) charge quantization) and test whether the
  **hypercharge-quantization *pattern*** follows from compactness + anomaly + the Z6 identification — **NOT** the
  coupling normalization / `sin²θ_W` (that needs the GUT = the caught smuggle). Outcome honest either way: a
  derived pattern, or a typed no-go naming why the global structure is not closure-forced. Anti-smuggle: the six
  gates must catch a mere re-encoding of the quotient.
