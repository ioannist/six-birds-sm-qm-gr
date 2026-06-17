# QM-GR (E018) — PENDING STRUCTURAL PROOFS (self-contained specs for a separate proof-attack session)

> **Purpose.** This track has verdicts that are **true by finite-carrier / saturation-trend / recognition-source /
> conditional evidence but are NOT yet structural theorems or frame-transfer.** Each such claim is a *door*: a
> precisely-stated lemma whose proof would upgrade "true on the toy / true as a trend / warranted" → "true, period."
> This file records each as a **self-contained spec** so a future session (or external mathematician/physicist) can
> attack it cold. Mirrors the SM track's `thread_cluster_a/PENDING_PROOFS.md`.
>
> **The standing meta-limit (applies to every item below).** This is a **finite-toy** program; **frame-transfer is
> unproven**. A "proof" here means a structural theorem *in the declared toy grammar* (or a recognition-landing under a
> named external source), NOT a derivation of physical nature. Continuous / Lorentzian / gauge / diffeomorphism-quotient
> carriers remain the external gate (TODO #4). Read every item with that ceiling.
>
> **Status legend:** `OPEN` (no proof, recorded here) · `ATTEMPTED→sharpened` (attempt reduced it to a smaller named
> lemma) · `CONDITIONAL` (landed under a named external/recognition source; the source-warrant is the residual) ·
> `LANDED` (a structural theorem was proved — moved to MAIN_RESULTS / manager_log).

## How to attack one of these (binding discipline — read first)

- **Sequential codex only.** One named step per codex dispatch (Mode T = theorem-writing, or Mode B for a new
  construction). NO sub-agents, NO workflows, NO batching. Manager (Claude) reviews; codex constructs. (See the
  construction memories.)
- **Freeze the machinery.** Any predicate the proof refers to (the contracted-state entropy, the min-cut/area, I3/MMI,
  the fork/common-refinement, the GROUND premise) must be imported **verbatim** from its source step via `importlib` +
  a **sha256 gate**. Retuning a frozen predicate = automatic smuggle-reject. **Frozen hashes (stable accepted steps):**
  - Step 42 RT carrier (`boundary_state_matrix` / `entropy_from_region` / min-cut): `4e204c0eae2df9a88b426c07e4bcf04ad308a3b1d18e05eac769bb64594b2d08`
  - Step 44 MMI (`mincut_entropies` / `standard_i3`): `61f28d10e8170a9f37ac71a711b6d30c3dac9b4f014b8e634c70ba2166a47052`
  - Step 45 discrete-Einstein (`discrete_einstein_consistency_step45.py`): `2348078115c839d2e4ee1fb66a99e620cb3644181befd5374a2f532cc83a4f35`
  - Step 47 GROUND premise (`common_carrier_door_test_step47.py`): `815f68448a5f88f4a6b739fda55a4786c1a314237a184cdf82fb0dd7568af47a`
  - Step 48 fork/common-refinement (`ladder_vs_fork_resolution_step48.py`): `cea0a1531dfa060a8fda2bab685ef73f28a6afb9086d54c7379f9104268e40d5`
  - Step 50 (Born+area one combiner) and Step 51 (F51 joint prediction): **pin at attack time** — Step 50 just accepted,
    Step 51 in manager audit; recompute their sha256 once settled before importing.
- **Five Mode-T exit states** (terminate in exactly one): `constructed_theorem` (carrier/window-independent, zero
  imports) · `conditional_theorem_with_named_imports` · `sharpened_external` (reduce to a smaller named lemma) ·
  `bounded_grammar_saturation_no_go` (prove no argument in a declared proof-grammar discharges it) · `smuggling_reject`.
- **Seven-gate + anti-circularity audit.** No-smuggling of the target (the proof may NOT assume the conclusion or
  anything extensionally equal to it — **the Step 39/40/50 lesson: a definitional identity dressed as a coincidence is a
  reject**); anti-circularity (each hypothesis independently satisfiable by a structure that fails the conclusion);
  anti-vacuity (exhibit a populated exemplar class); uniform-parametric-bound (make the D / bond-dim / region-count
  dependence explicit — a finite-D bound masquerading as a limit theorem is a reject).
- **Converse / can-fail probe (mandatory).** Before claiming any proof, actively try to *break* it — a counterexample,
  a seed where the trend reverses, a broken-compatibility control that still forces the conclusion. A counterexample is
  a first-class result (the claim is conditional, not a theorem), not a failure.
- **Lead with the deflationary truth.** A finite-D trend is NOT a limit theorem; a recognition-source warrant is NOT a
  proof; an analogy is NOT a structural tie. If you cannot prove it, say so and record the sharpened residual here.
  Hiding "still a trend / still recognition-source" is the worst outcome.

## Status table

| id | claim (one line) | source | landability | status |
|---|---|---|---|---|
| **Q1** | RT saturation `S(A)/area → 1` exactly in the large-bond / continuum limit (not just a finite-D trend) | Steps 41–42, 50 | medium (known holographic large-N result; the work is proving it in this grammar) | `OPEN` |
| **Q2** | the common-carrier premise is **uniquely** grounded by semiclassical co-sourcing (no competitor grounding) — warranted → forced | Step 47 | hard (it is a recognition source; uniqueness needs the grounding space characterized) | `CONDITIONAL` (GROUND-landed; uniqueness open) |
| **Q3** | the **continuum** Einstein tensor emerges from the discrete RT-consistency tower (the four F43 conditions hold) | Step 45 | low–medium (the standing continuum frontier; done in real AdS/CFT, not in this toy) | `OPEN` = TODO #13 |
| **Q4** | non-renormalizability **is** the route-mismatch defect `Δ₃^comp` (FIII Thm 9/10), quantitatively — not an analogy | Step 48 + FIII | medium-structural (FIII T9/T10 proved; the tie to *physical* non-renormalizability is frame-transfer-limited) | `OPEN` = TODO #14 |
| **Q5** | the F51 common-refinement compatibility forces the monogamy joint-prediction for **all** admissible co-readouts (not just the finite carrier) | Step 51 | TBD (pending the Step-51 audit) | `OPEN` (provisional) |

**Named residual (NOT a pending proof — it may go the other way):** **strong bulk reconstruction.** Step 48's fork is
conditional on the access structure that models *weak* RT (`A_RT=d0+2·d2`, a function of QM-accessible modes, cannot
recover `d3`). Strong emergent spacetime claims `d3` *is* recoverable from richer quantum data. This is **not** a lemma
to prove in our favor; it is an honestly-named open frontier whose resolution could *contradict* the fork reading. Track
it as a falsification route (TODO #5), not a pending proof.

---

## Q1 — RT saturation is exact in the large-bond / continuum limit

**Status:** `OPEN`. **Honest landability: medium.**

**Formal claim (the version that WOULD be a theorem).** For the contracted holographic carrier, the saturation ratio
`S(A)/area_mincut(A) → 1` as the bond dimension `D → ∞` (and/or under refinement of the tensor network toward the
continuum), for every boundary region `A` — i.e. the Batch-A *bound* `S(A) ≤ area` is *asymptotically tight*, not merely
a finite-D trend.

**What is established.** Step 42: the saturation ratio is an *emergent trend* — seed-averaged `S/min-cut` rises
`0.729 → 0.904 → 0.941` across `D = 2,3,4` (random Gaussian tensors, not imposed). Step 50: at `D=3`, strict gaps
`0.997–0.999` with `area_mincut` seed-invariant while `S_Born` varies (the bound is genuine, non-circular). So the bound
holds and saturation *increases* with `D` — but only across three points, with no limit proof.

**What is missing.** A proof that the ratio's limit is exactly 1 (and a rate / uniform-in-region bound). This is the toy
analog of the known holographic large-`N` / large-bond saturation; the work is a structural argument in *this* grammar
(why the competing non-minimal cuts' contributions vanish relative to the min-cut as `D→∞`), with the `D`-dependence made
explicit (anti-uniform-bound gate). A reversing seed or region at higher `D` would be a first-class counterexample.

**Exit criteria.** `constructed_theorem` (limit proof with an explicit rate) discharges the Batch-A "saturation is
emergent, not exact" caveat. A `sharpened_external` naming the precise spectral condition on the contracted state that
forces tightness is also a real landing. **Pointers:** `steps/step41_*`, `steps/step42_*`, `steps/step50_*`; the Batch-A
packet `review_packets/qm_gr_area_entanglement_v2/`. **Connects to Q3** (both are continuum-limit questions; F43).

---

## Q2 — the common-carrier premise is *uniquely* grounded (warranted → forced)

**Status:** `CONDITIONAL` (the premise is GROUND-landed; *uniqueness* of the grounding is open). **Honest landability: hard.**

**Formal claim (the version that WOULD strengthen the landing).** Among admissible recognition sources that ground "QM
and GR are co-readouts of one carrier," **semiclassical co-sourcing is the unique one** (no structurally-distinct
competitor grounding warrants the premise) — moving Step 47 from `LANDED · GROUND (warranted)` toward
`LANDED · GROUND (forced)`, the QM-GR analog of the SM track's `T_QGR_Unique` (minimal-admissible uniqueness by
adversarial *defeat*, not absence).

**What is established (Step 47, externally SETTLED Batch B).** The SBT laws (F37/F51/FoEC/SAU) give *form/license* but do
**not** force the shared carrier; the premise is warranted by semiclassical co-sourcing (one `ψ → Born[ψ] + T[ψ]`,
extended via Step 26's back-reaction `V[ψ]=background+κ·T00` to matter-sourced geometry). The two can-fail controls fire
(complementary pair → no manufactured carrier; non-co-sourcing → no warrant). Theorem-strength is tagged
**recognition-source, not proved.** The reviewer accepted this as a genuine GROUND landing.

**What is missing.** An adversarial *defeat* of alternative groundings: enumerate candidate recognition sources that
could warrant the premise, and show each either (a) reduces to semiclassical co-sourcing, or (b) fails the can-fail
controls. Anti-circularity: the uniqueness argument may not assume co-sourcing is the grounding. Honest caveat: even a
uniqueness result stays **GROUND mode** (the physical fundamentality of the source is the external top-of-tower question)
— it would forge "warranted → forced," not "recognition → derivation."

**Exit criteria.** `conditional_theorem_with_named_imports` (uniqueness modulo a named admissibility condition on
groundings) is the realistic landing; a full `constructed_theorem` is unlikely (the grounding space is open). A
`bounded_grammar_saturation_no_go` (no toy-internal argument can force uniqueness) is also a valid, honest terminal.
**Pointers:** `steps/step47_*`, `steps/step25_*`, `steps/step26_*`; `review_packets/qm_gr_common_carrier_v2/`;
`LANDED_vs_NOT.md` GROUND mode. Folded under TODO #2 as the warrant-uniqueness arc.

---

## Q3 — the continuum Einstein tensor emerges from the discrete RT-consistency tower (F43)

**Status:** `OPEN`. **Honest landability: low–medium. This is the standing continuum frontier.** = TODO #13.

**Formal claim.** The discrete linearized-Einstein consistency condition (Step 45) is the finite rung of a coherent
approximation tower whose **F43 continuum-emergence conditions** hold — tower-coherence (`φ_ij∘p_j=p_i`), cofinality,
residual-vanishing (`ξ_i→0`), and limit-quotient completion — so the **continuum** Einstein tensor emerges as the stable
limit, not merely the discrete analog.

**What is established (Step 45).** A discrete linearized-Einstein consistency *constraint* is **derived**: treating bulk
capacities as a variable geometry and demanding RT-consistency under a perturbation across all regions overdetermines the
response into a non-trivial condition (38 regions, 14 edges, rank 10, cokernel 28); a geometry-shift `δS` satisfies it
(residual `9e-17`), a generic contracted-state `δS` violates it (residual `0.042`). Graded a *discrete/finite analog* —
the full continuum Einstein tensor is **not** completed.

**What is missing.** Run the F43 audit (TODO #13): build a *directed sequence* of finer carriers refining the Step-45
cut-incidence construction; check the four F43 conditions on the tower. Outcome is a verdict either way — the conditions
hold ⟹ continuum Einstein is *structurally licensed* (`constructed_theorem` / `conditional_theorem`); a condition fails
⟹ a **typed obstruction** naming exactly which F43 condition blocks the continuum (a `sharpened_external` / a precise
door). Frame-transfer ceiling stands regardless (this is a toy tower, not real AdS/CFT — cf. Faulkner et al for the real
result this toy gestures at).

**Exit criteria.** Per the four F43 conditions above. **Pointers:** `steps/step45_*`
(`discrete_einstein_consistency_step45.py`, hash above); Foundations IV F43 (`Continuum Emergence`, ~line 7429);
TODO #13.

---

## Q4 — non-renormalizability IS the route-mismatch defect `Δ₃^comp` (FIII Thm 9/10)

**Status:** `OPEN`. **Honest landability: medium-structural** (the structural half is proved in FIII; the physical tie is
frame-transfer-limited). = TODO #14.

**Formal claim.** The quantize/curve completions on the QM-GR carrier are explicit finite idempotents `E₁,E₂`
(`E₁²=E₁, E₂²=E₂`) with `E₁E₂ ≠ E₂E₁`, whose route-mismatch defect `Δ₃^comp = {c : E₁E₂(c)≠E₂E₁(c)} ≠ ∅` is the
structural content of non-renormalizability — tied *quantitatively* to Step 48's `route_mismatch = 0.5`, not asserted as
an analogy.

**What is established.** FIII **Theorem 9 (Noncommuting Completions)** + **Theorem 10 (Completion-Pasting Defect)** prove,
at theorem-grade, that idempotent completions can fail to commute and that the mismatch is a finite typed record
`Δ₃^comp` — *a real defect even though each completion is individually exact*. Step 48 computed the directed-ladder
`route_mismatch = 0.5` and the defect count 8. The interpretation docs *claim* route-mismatch = non-renormalizability —
but as an analogy, not a construction.

**What is missing.** Construct the quantize/curve idempotents explicitly on the QM-GR carrier, exhibit the non-empty
`Δ₃^comp`, and tie it to the Step-48 numbers — turning the analogy into a law-grounded structural fact (the
quantize-then-curve ≠ curve-then-quantize obstruction *is* FIII's `Δ₃^comp`). **Honest ceiling:** this lands the
*structural* identity (toy route-mismatch instantiates `Δ₃^comp`); the tie to *physical* continuum-QFT
non-renormalizability stays the frame-transfer gate.

**Exit criteria.** `constructed_theorem` (the two completions + the non-empty defect + the quantitative tie) discharges
the analogy into a recognition. **Pointers:** `steps/step48_*` (hash above); FIII Theorems 9/10 (`Noncommuting
Completions` / `Completion-Pasting Defect`, ~lines 3158/3216); TODO #14, falsification route (e) in TODO #5.

---

## Q5 — the F51 monogamy joint-prediction is forced for all admissible co-readouts

**Status:** `OPEN` (the Step-51 forcing is **landed on the finite carrier**, accepted; the all-co-readout generalization
is the open upgrade). **Honest landability: medium** (it is the holographic-entropy-cone monogamy facet; proving it for
all geometric-dual states is the work).

**Formal claim.** Step 51 (accepted) established, *computed and load-bearing*, that the F51 common-refinement
compatibility — defined as a geometric-dual min-cut-vector match, I3-independent — forces the monogamy constraint
(`I3 ≤ 0`) on the admissible co-readouts, that QM-alone violates it (GHZ, geometric-dual fails, `I3=+log2>0`), and that a
broken-compatibility control un-forces it. The **upgrade**: prove the F51 compatibility forces `I3 ≤ 0` for **all**
geometric-dual co-readouts (an all-states theorem), not just the constructed exemplars + the GHZ/broken controls.

**What is established (Step 51, accepted).** The Maxwell-shape forcing is genuine and computed (compatibility is the
geometric-dual vector match; MMI follows as a consequence; the broken control un-forces). **Honest grade: the content is
RECOVERED holographic MMI** (`recovered_known_constraint=true`) — a recognition-landing, not a new prediction.

**What is missing.** The all-geometric-dual-state generalization: that every entropy vector reproduced by a graph min-cut
satisfies `I3 ≤ 0` (the holographic entropy cone's MMI facet) is a *known* result in the literature; landing it as a
`constructed_theorem` *in this toy grammar* (over the declared carrier family) would upgrade Step 51 from "shown on
exemplars" to "forced for all admissible co-readouts."

**Exit criteria.** `constructed_theorem` (the MMI facet for all min-cut-realizable entropy vectors on the carrier family),
or a `conditional_theorem` citing the holographic-entropy-cone result as a named import. **Pointers:** `steps/step51_*`,
`steps/step50_*`, `steps/step44_*`; Foundations IV F51 (`Unification as Common Refinement`, ~line 8528); TODO #11.

---

## Status note — the F49/F34/F50 forbidden-rule classifications are NOT pending proofs (2026-06-10)

Steps 52–54 (Bell / black-hole-information / Λ, accepted) are **computed classifications, not enumeration-true-but-unproven
claims** — they do not belong in this file as pending lemmas. Their honest residuals are *scope*, not *proof-strength*: each
is finite-toy and conditional on the Step-47 premise for the carrier reading (F49's Bell computation is itself
premise-independent QM); F50 is enumeration-strength over its sweep (a sweep, not an all-backgrounds theorem — the closest
analog to a pending item, but its verdict *bounded-moduli / no value-law* is the kind of negative the framework predicts,
not a lemma awaiting proof). They are recorded in `MAIN_RESULTS.md` (H) and `LANDED_vs_NOT.md`, and feed the falsification
routes (TODO #5 / the E005 black-hole arena), not this proof-attack file.

---

## Session note (doc created 2026-06-10)

Created to mirror the SM track's `PENDING_PROOFS.md`. The QM-GR track had no consolidated pending-proofs spec; this fills
that reader-doc gap (alongside the still-pending `MAIN_RESULTS.md` + `LANDED_vs_NOT.md`, TODO #6). No item is `LANDED`
yet — the two Batch-settled results (area=shadow-price; common-carrier GROUND + fork) are *accepted landings*, and the
items above are their open *theorem-strength / continuum / uniqueness* upgrades. Q5 is provisional pending the Step-51
audit; finalize it then.
