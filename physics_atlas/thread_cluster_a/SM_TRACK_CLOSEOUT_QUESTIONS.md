# Cluster A (SM selection / gauge-structure track) — CLOSE-OUT QUESTIONS (scope & limits companion)

> **Purpose.** The limits/scope companion to `MAIN_RESULTS.md`. Where MAIN_RESULTS lists the *results* (A–I) with
> their grades, this doc pins down *exactly what is and is not claimed*, the precise definition of the thing
> selected, the full assumption stack, and the residual open questions — so the paper neither overclaims nor
> leaves its scope implicit. **Read the two together.** This doc contains **zero new derivations**; it is scope
> hygiene only, plus the results of the two close-out computations (Step 52 minimality, Step 53 competitors).
>
> **Deflationary frame (binding).** This is a **finite-toy** program. There is **no** derivation of any SM value,
> **no** frame-transfer certificate, and the central selection is **conditional on an introduced recognition
> source**. The substantive content is **typings, type-limits, conditional selections, reframings**, plus (new)
> a **minimality relocation** and a **named-competitor table**. Provenance is mixed (see §3); nothing here is
> "derivation from nothing."

---

## 0. Why-question resolution — what the framework resolves, and how (read first)

A compact map of the "why this / why not that?" questions about the SM and **how this track resolves each**. The
detail lives in §1–§10 below and in `MAIN_RESULTS.md`; this table is the index. **Resolution kinds:**

- **conditional-discriminator** — answered, but *conditional* on imported physics (A) + the introduced
  clean-separation / proton-stability condition (C) + the bounded window. Not "nature must."
- **typed-fork → resolved-by-source** — SBT types two readings; the proton/monopole fork is now **resolved to the
  clean branch by memory-stability** (Step 65, SELECT-conditional; §8), *not* left undecided. (The earlier
  "physical_reading_resolved=False" punt was superseded — the framework's own memory law selects the structural
  branch; it still does not certify the *physical* proton.)
- **true-negative** — a correct "no" result, not a gap (e.g., anomaly-freedom alone does not pick the SM).
- **Type-B (proven-blind)** — the framework **proved** closure is *blind* to it ⇒ observed-input by a demonstrated
  type-limit. "Filling" it would require **smuggling** the answer back in. *This is a positive result, not a failure.*
- **smuggle-only** — derivable **only** by re-importing the answer (the route already caught + demoted).
- **door-to-E0** — observed-input *at this layer*; the door beyond is the deliberately-**excluded** emergence (E0) run.
- **walkable-now** — a genuine, un-walked, within-paradigm construction door that needs **no** E0 run.

| "Why …?" question | resolution kind | one-line answer | where |
|---|---|---|---|
| SM-like `SU(2)×SU(3)×U(1)` rather than `SU(4)`-single-factor? | conditional-discriminator | clean separation (≡ proton stability, Step 52) excludes the confining-charged X/Y coset; `SU(4)` has it, `2|3` does not | §1,§4,§6; MAIN_RESULTS D/E |
| color stays separate from electroweak breaking? | conditional-discriminator | the clean shadow has no X/Y coset contaminating the confining sector | §6; UNIFICATION |
| no X/Y bosons in the SM shadow? | conditional (by the condition) | X/Y colored vectors are exactly what clean separation forbids (`Δ_fact=∅`) | §6,§8; UNIFICATION |
| proton decay in GUT-like but not the clean SM shadow? | **fork RESOLVED to clean** (SELECT, Step 65) | memory-stability ⟹ clean-sep ⟹ baryon descends (F27=0, no decay); breaking reading excluded for record-bearing structures. Conditional/enumeration/frame-transfer-limited | §8 |
| monopoles in GUT-like but not the clean SM shadow? | **fork RESOLVED to clean** (SELECT, Step 65) | same memory-stability selection → clean reading → F48 gluing obstruction 0 (no monopole); breaking reading excluded | §8 |
| GUT is not just a relabeling of the SM? | answered descriptively (StructDown-only) | `Δ_fact(SM,GUT)=15`, `(GUT,SM)=0` ⇒ genuine refinement; **not** a physical two-layer | MAIN_RESULTS H; UNIFICATION (Step 47) |
| do anomaly cancellation + chirality **alone** derive the SM? | **true-negative** | no — candidates are abundant; closure+descent+clean-sep narrow further | MAIN_RESULTS B/D |
| hypercharge **normalization**? | Type-B (coupling); **Door 2 walked → recovered, not a selector** | coupling normalization is observed-input (needs GUT); the global quotient is now *computable* (Step 55) and **recovers** the SM `Z6`, but does not *select* it (alternative class also `Z6`) | §9; Door 2 |
| `sin²θ_W = 3/8`? | **old route smuggle-only · new route (Step 63) GROUND-conditional** | The **measured low-energy** value stays **not derived** (needs RG running = E0/experiment). The old "assume su(5), read 3/8" was the caught smuggle. **Step 63** instead **computes the embedding trace-ratio** `Tr(T3²)/Tr(Q²)=2/(16/3)=3/8` from the **input** SM charge pattern, **conditional** on a declared minimal-simple common-refinement source (non-circular: a product control computes 3/23) — a GROUND-conditional recovery of the *embedding ratio*, **not** the measured value. | §9; `LANDED_vs_NOT.md`; step63 |
| three generations (`N_gen = 3`)? | **Type-B (proven-blind)** | Step 51: closure is per-generation-blind; only a recognition-source bound `N≥3` (CP), no derivation of 3 | §10; MAIN_RESULTS I |
| full fermion **content**? | door-to-E0 (full); **Door 1 walked → blind** | 2 residual classes; now **3** neutral shadows blind (Door 1 = mass-rank, Step 54, did not narrow). Full pin needs E0; further shadows = diminishing returns | §7; Door 1 |
| hierarchy / EW scale? | **door-to-E0** | reframed as an F47 small-selector region; the value is not derived; naturalness flatly **not addressed** | §10; MAIN_RESULTS C |
| anthropic vs dynamical selection? | toy-criterion only | the P6 collapse-to-point criterion is **formal**, not a physical disproof of anthropic reasoning | here + gut_problems |
| why **exactly this full** SM? | intentional meta (factorization) | not one derivable thing — the SM factors into [few closure-forced features] + [many observed-input moduli]; **the gaps ARE that factorization** | §1,§4,§10 |

**The distinction that matters (Type-A vs Type-B "No").** A "no" here is one of two very different things: (A) a
genuine **open door** ("we have not yet derived X"), or (B) a **proven-blind type-limit** ("we *proved* closure
cannot determine X"). **Most of this track's "No"s are Type-B** — positive results that *locate a boundary*, not
failures. `N_gen` (Step 51) is the cleanest example: closure is demonstrably blind to it, so it is observed-input
by proof, and any "3" must come from non-neutral structure (a smuggle). Reading Type-B as "failed to derive"
misreads the result.

**The unifying door.** Almost every intentional gap — full content, generations, the EW scale, and *resolving*
(not just typing) the proton/monopole fork — points at the **same** door: the **E0 emergence run** (actually
running the substrate of the layer *above* the gauge structure, from which these would be read off rather than
imposed). This track **excludes E0 by design**. So these are **doors to the emergence layer, not walls** —
deliberately outside this track's scope, not failures within it. (Clean-separation's *fundamentality* was one more
item on this list until **Steps 57–59 walked it a different way** — not *down* to E0 but *up* one layer, to a
**memory-stability** recognition source that forces it: see **Door 3** below and §6.)

**The three walkable-now doors (all now walked — Steps 54, 55, 57–59).**

- **Door 1 — a 3rd neutral content shadow (gap #11). [WALKED — Step 54: BLIND; the content type-limit holds.]**
  Steps 48–49 quotient the 8 SM-signature rosters to **2 classes** and tested **two** SM-content-independent
  shadows (integer charge-quantization; Yukawa-texture connectivity), both blind. Step 54 tested a **third**:
  **full mass generation / fermion mass-matrix rank** (every charged component paired by a charge-matched Yukawa
  edge — definitionally distinct from connectivity). Result: **both classes pass → blind** (`CONTENT_TYPE_LIMIT_
  3_SHADOWS_BLIND`); the door did **not** narrow 2→1. Honest nuance: the rank shadow coincides **extensionally**
  with Step-49 connectivity on this carrier, so it is confirmatory, not strongly-independent, evidence — 3
  *definitionally*-distinct shadows, the 3rd coinciding with the 2nd here. The type-limit is genuine physics
  (content = observed-input, F26). Further shadows are diminishing returns; the full content pin needs E0.
- **Door 2 — the global-quotient / Z6 / hypercharge-pattern carrier (gap #8 partial; the §9 limit). [WALKED —
  Step 55: `GLOBAL_QUOTIENT_RECOVERED_SELECTION_BLIND`.]** The filter runs at the **algebra/product** level and is
  blind to the global quotient `(SU(3)×SU(2)×U(1))/Z6`. Step 55 EXTENDED the toy to **compute** the maximal
  trivially-acting center (the global quotient) per content class by exhaustive congruence search
  (`k·t/3 + m·d/2 + Y·turn ∈ ℤ` for every field) — genuinely **computed, not posited** (the validator fails if
  `Z6` is hard-coded in the solver or if the solver reads the target flag). Result: it **recovers the SM's `Z6`**
  as a computed property of the input charge pattern (`2t+3d+Y ≡ 0 mod 6`), but the alternative class **also**
  computes to `Z6` (different generator), so requiring a nontrivial center **does not discriminate** (blind). So
  the §9 *computational* blindness is **lifted** (the toy can now compute the quotient + recovers the SM `Z6`),
  but: (i) this is **recovery, not derivation** — the hypercharge pattern is the input, the center the
  consequence; (ii) the global structure is **not a closure-selector** on the content classes; (iii) the coupling
  normalization / `sin²θ_W` remain **untouched** (need the GUT). Honest negative on the "could it *select*?"
  question; honest recovery on the "can the toy *see* it?" question.
- **Door 3 — the *fundamentality* of clean-separation (the §6 / Step-39 limit). [WALKED — Steps 57–59:
  `RECORD_STABILITY_FORCES_CLEAN_SEPARATION`, grade `ROBUST_COVERAGE_ENUMERATION_ONLY`.]** Step 39 showed
  clean-separation is **not derivable *within* the gauge layer** (its "standard confining sector" grounding was
  extensionally equal to clean-sep ⇒ circular). Steps 57–59 ground it **one layer up** instead: requiring a
  **memory-stability** layer — stable substrate (unbroken confining non-abelian sector + mass-completability,
  Step 35) ∧ capacity for **≥2 neutral (color-singlet, charge-sum-0) record tokens** ∧ distinguishability (no
  aliased reps) — **forces** `Δ_fact=∅`. **Non-circular** (each of the three memory-properties is independently
  satisfied by some **¬clean-sep** structure — verified by counterexample — so only their *conjunction* lands in
  clean-sep), and **robust across the full 11,990-structure corrected space** (incl. **311 adversarial
  ¬clean-sep-with-capacity** structures; **0 counterexamples**). Two honest qualifications: (i) this **relocates,
  does not derive** — clean-sep is now the gauge-shadow of memory-stability, itself a *higher* recognition source,
  not derived from nothing; physical fundamentality of memory-stability is the external-physics judgment; (ii) it
  is **enumeration, not a structural proof** — verified by exhaustive search over the bounded window, not proven
  for *all* chiral structures (the structural theorem "`substrate ∧ capacity ∧ Δ_fact≠∅ = ∅` for every chiral
  structure" is the open upgrade). Driving fact: **no ¬clean-sep structure has *both* substrate AND capacity**
  (`non_CS_substrate_capacity_count = 0`). The **structural-theorem attempt (Step 60, Mode T)** did **not** prove
  it — exit `sharpened_external`: it reduced the theorem to one precisely-named open lemma **L60**
  (`substrate ∧ leak>0 ⟹ <2 neutral records`, the gauge→matter bridge) and **extended the empirical base** beyond
  the 11,990-structure carrier with **bounded outside probes** (Step 60/64; larger dims + two-factor big-factor
  structures — distinct windows; still **0 counterexamples**), so the open upgrade is now one lemma, not a diffuse
  gap. See §6.

---

## 1. The accepted claim (the claim ladder)

**What IS claimed** (strongest honest form, copied from the v4-accepted grade + Steps 43–53):

> On a bounded finite window over the SU(N)-product representation alphabet (non-abelian factor counts 1–3,
> fundamental dimensions 2–6, charge units −6..6), the framework's **neutral closure + descent** principles
> narrow ~**11,990** genuinely-chiral gauge theories to the small family **{`2|3`, single-factor `SU(4)`}**; an
> **introduced clean-separation recognition source** (`Δ_fact = ∅` — no confining-charged broken vectors)
> **conditionally selects** the SM-like structure **SU(2)×SU(3)×U(1)**. The selection is **window-stable**
> (single-factor axis closed by a structural-arguable coset bound; dimension/factor-count axes stable but
> **cap-conditional**), holds **against named competitor structures** (§5), and the load-bearing condition is
> **not minimal** — a strictly weaker, more physical **proton-stability** condition performs the same cut (§6).

**What is NOT claimed** (the forbidden rungs — never assert these):

- ✗ "SBT **generates / derives** the SM gauge structure." (It conditionally *selects* it from a small family.)
- ✗ "Clean-separation is **derived / fundamental** (from nothing)." (It is an introduced recognition source, **not
  toy-derivable within the gauge layer** — Step 39's within-layer grounding is circular. Steps 57–59 **relocate** it
  one layer *up* — it is the gauge-shadow of a **memory-stability** source that forces it (non-circular, robust on
  all 11,990 by enumeration) — but that **relocates, does not derive**: memory-stability is itself a higher
  recognition source whose physical fundamentality is external. §6, Door 3.)
- ✗ "**Frame-transfer**" / any certificate the toy result transfers to physical reality.
- ✗ "The SM **content / matter** is selected." (2 residual content classes; observed-input; §7.)
- ✗ "**N_gen = 3** is derived." (N_gen-blind closure; recognition-source bound only; §10.)
- ✗ Any **SM constant, mass, coupling, or mixing** is derived. (None is.)
- ✗ The **global gauge group** (the Z6 quotient) or the **hypercharge normalization** is certified. (§9.)
- ✗ "**Unconditional** closure of the SM selection foreclosure."

The honest one-line: *a bounded finite SBT discriminator conditionally selects the SM-like algebra
su(2)⊕su(3)⊕u(1) over named alternatives, provided one imposes clean separation (equivalently, proton
stability); the condition is physically motivated but not derived, and the result is structure-level only.*

---

## 2. Precise "SM-like" definition (what the discriminator actually selects)

The object selected is the **gauge Lie algebra / product structure** `su(2) ⊕ su(3) ⊕ u(1)` carrying the SM
chiral signature (support_05: 5 multiplets / 15 Weyl per generation — quark doublet `Q`, lepton doublet `L`,
`u`, `d`, `e`), whose mass-breaking shadow is **colorless** (the unbroken confining sector is the untouched
`SU(3)`; the breaking leaves an unbroken `U(1)`). "`2|3`" is just the `(dim SU(2) | dim SU(3))` labelling
convention (see §10 on ordering — no physics in the order).

**It is selected only up to:**
- the **global quotient** — the toy sees the *algebra* / *product*, not whether the global group is
  `SU(3)×SU(2)×U(1)` or `(SU(3)×SU(2)×U(1))/Z6` (the physical SM). **Not certified.** (§9)
- the **hypercharge normalization** — the `U(1)` is the unbroken-U(1) of the breaking; its charge normalization
  is a **convention** (toy units `UNIT_DENOMINATOR=6`, `WEAK_SHIFT_UNIT=3`, declared Step 50). **Not derived.** (§9)
- the **content** — 2 distinct SM-signature content classes survive (SM + 1 alternative). **Not pinned.** (§7)

So "SM-like" in this track = *the product gauge algebra with a clean (colorless-breaking) confining shadow and
the 5|15 chiral signature*, at the structure level, modulo global structure, hypercharge normalization, and content.

---

## 3. The A/B/C assumption stack (full provenance)

(From `review_packets/sm_selection_layer_v4/ERRATUM_v4_provenance.md`; the result is a selection conditional on
**all three**.)

- **(A) Imported standard physics** — anomaly cancellation (local + Witten global); chirality / self-conjugacy;
  group-theory coefficients (Dynkin indices, cubic anomaly `A(R)`); the **Higgs/Yukawa mass mechanism +
  spontaneous symmetry breaking**; **baryon-number assignment** (used by the Step-52 proton-stability variants).
  *These are not SBT-derived; they are the substrate.*
- **(B) Posited SBT primitives** — P1–P6 (operator rewrite / constraints / route holonomy / sectors / packaging
  / audit); the F-laws invoked (F24 BudgetedRole, F26 Moduli, F27 Orbit-Descent, F47 Small-Selector, F48 Gluing,
  F51 Common-Refinement); the descent / shadow machinery; non-factorization `Δ_fact`. *Axioms, not derived.*
- **(C) Choices / stipulations** — the **bounded window** (factors 1–3, dims 2–6, charges −6..6); the
  **SU(N)-product alphabet**; the **clean-separation** condition (or its weaker proton-stability relocation);
  **single-Higgs minimality** (one neutral scalar witness for mass-closure); the **neutral carrier** construction.

**SBT's genuine contribution = (B) applied to the (A)-space under (C).** It is not derivation-from-nothing, and
the imports (A) are load-bearing (remove them and the carrier dissolves — §10).

---

## 4. Selected-vs-not-selected (positive selection vs negative exclusion)

- **Negative exclusion does most of the work.** The chain 11,990 → 156 → 130 → 80 → 12 is **~99.3% exclusion**
  (closure / consistency / corrected chirality / mass-closure rule things *out*). This is robust and largely
  un-smuggled (the SU(2)-cubic bug and the shape/minimality rescues were caught and removed, Steps 33/37).
- **The positive pick rests on one introduced condition.** Going from the small family {`2|3`, `SU(4)`-alone}
  to *`2|3` specifically* is the **positive** step, and it is carried by the introduced clean-separation /
  proton-stability condition (§6) — not by the neutral machinery.

So "selection" = **strong neutral negative narrowing + one introduced positive condition**. Honest framing: the
framework powerfully *excludes*; the final *positive* identification of the SM structure is conditional.

---

## 5. Competitors in / out of window (Step 53)

Named competitor gauge structures run through the **actual** Step-28→38 filter + Step-43/44 bounds:

| competitor | toy structure | window status | excluding gate / reason | cap-conditional? |
|---|---|---|---|---|
| SU(5) | single `SU(5)` | in-window, **filter-excluded** | **mass-closure** (no consistent colorless-breaking mass shadow; step43 row `5`: higher-layer mass-closure = 0) | no |
| flipped SU(5) | `SU(5)×U(1)` | in-window, **filter-excluded** | same single-`SU(5)` row (the U(1) flip is invisible to the structure-level filter) | no |
| Pati–Salam | `SU(4)×SU(2)×SU(2)` | in-window, **cap-excluded** | factor-count≥3 route-completeness: all-factor row dim ≥ 16 > cap 6 | **yes** |
| left–right | `SU(3)×SU(2)×SU(2)×U(1)` | in-window, **cap-excluded** | all-factor row dim ≥ 12 > cap 6 | **yes** |
| trinification | `SU(3)×SU(3)×SU(3)` | in-window, **cap-excluded** | all-factor row dim ≥ 27 > cap 6 | **yes** |
| SO(10) | `SO(10)` | **out-of-alphabet** | outside the SU(N)-product alphabet (orthogonal group) — a **cap-independent representation-alphabet boundary**; also fund dim 10 > cap 6 | n/a* |
| E6 | `E6` | **out-of-alphabet** | outside the SU(N)-product alphabet (exceptional group) — **cap-independent**; also fund dim 27 > cap 6 | n/a* |

\* The Step-53 artifact marks SO(10)/E6 `cap_conditional=True` under a literal "fund dim exceeds cap" reading.
**The precise statement (this doc):** SO(10)/E6 are excluded **primarily because they are outside the declared
SU(N)-product alphabet — a modeling-choice boundary that does NOT depend on the cap** (a larger cap would not
admit them); they additionally exceed the dim cap. They are **future / not enumerated, not refuted** by the toy.

**Caveats:** the table is **not exhaustive** (finite named set, bounded window); the 3-factor exclusions are
**cap-conditional** (they ride on component cap 6 = the SM's own all-factor-row dim = `Q` under SU(2)×SU(3) = 6,
which *just* fits — Step 44); the competitor→toy mapping is a **recognition/identification** (the toy tests the
gauge-structure *shadow*, not the full physical competitor theory). The SM `2|3` **survives the same unmodified
filter** (8 clean supports) — verified as a consistency control, and the mass-closure gate passes the SM (8)
while excluding SU(5) (0), so it is not a "exclude-everything-but-2|3" rule.

---

## 6. Clean-separation: status, alternatives, failure-modes (Steps 38/39/41/52 + corpus)

- **Status:** an **introduced recognition source** — `clean_separation ≔ broken_vector_exotic_count = 0` =
  `Δ_fact = ∅` (no confining-charged broken vectors = no X/Y colored coset). **Not toy-derivable** (Step 39: the
  "standard confining sector" grounding is circular); a wide corpus search confirms it is a recognition source,
  not a derived law (`clean_separation_corpus_findings.md`). **[Now GROUNDED one layer up in a memory-stability
  layer (Steps 57–59) — see the grounding bullet below; introduced *at the gauge layer*, grounded *from above*.]**
- **Minimality (Step 52):** clean-separation is **NOT minimal**. On the 12-row carrier, three weaker variants:
  - **no-light-X/Y** — degenerate (the toy has no mass scale forcing a coset vector light → collapses to the
    base shadow → keeps all 12, selects nothing);
  - **no-baryon-violating-X/Y** (forbid only the F27 orbit-enlarging subset) and **bare proton-stability**
    (require baryon number to descend, F27 obstruction 0) — **each makes the identical `2|3`-vs-`SU(4)` cut**
    (12 → 8) as full clean-separation.

  So the load-bearing condition can be **relocated** from the abstract "no confining-charged broken vectors at
  all" to the physically-transparent "**the proton is stable / baryon number descends**." **This is a
  relocation, not a derivation** — baryon number is itself an observed-input recognition source, and the
  coincidence (the weaker condition matching clean-separation) is a **computed property of this carrier** (all
  six `SU(4)` coset vectors are baryon-orbit-enlargers); on a richer carrier with B-conserving confining-charged
  broken vectors the conditions would **separate**. (Verdict label in the artifact: `MINIMALITY_MIXED`, because
  the degenerate no-light variant fails; substantively the result is "a weaker physical condition suffices.")
- **Failure modes:** relaxing the condition returns `SU(4)`-alone (the family grows back to 12 → the selection
  is lost); the 2-family carrier ({`2|3`, `SU(4)`}) makes this a **coarse 2-class** discrimination, not
  fine-grained uniqueness over all structures.
- **Alternatives that DON'T derive it:** proton-stability (Step 52, weaker but still observed-input); SDTC/F14
  (corpus — but itself a recognition source, and its "mass"/"confinement" are measure-theoretic homonyms). None
  makes it fundamental. **Its physical fundamentality is the standing frame-transfer / external-review question.**
- **Grounding one layer up (Steps 57–59, Door 3) — the record/memory-stability layer.** Step 39 closed the
  *within-gauge-layer* derivation of clean-separation (circular). Steps 57–59 take the SBT move for a not-provided
  quantity — **get it from another layer** — and ground clean-separation in the layer *above* it: a
  **memory-stability** layer **forces** `Δ_fact=∅`. Define memory-stability ≔ **stable substrate** (unbroken
  confining non-abelian sector + mass-completability, the Step-35 base) ∧ **record capacity** (≥2 neutral —
  color-singlet, charge-sum-0 — composite record tokens, from `line(fund)`+`dual_line(antifund)` pairs and
  same-family triples) ∧ **distinguishability** (no aliased reps — e.g. for SU(3), antifund and Λ²(fund) both alias
  to `dual_line` at dim 3, since `3̄ ≅ Λ²(3)`). Three honest facts:
  - **Non-circular (a decidable math fact, not a wording choice).** Each of the three conjuncts is independently
    satisfied by some **¬clean-sep** structure (explicit counterexamples found), so no single conjunct is
    clean-separation in disguise; **only the conjunction** lands in clean-sep. This is exactly the anti-circularity
    test Step 39 failed (there the grounding was *extensionally equal* to clean-sep).
  - **Robust, but enumeration — not yet a structural proof.** Checked across the **full 11,990-structure corrected
    closer space** (Steps 58–59), including **311 adversarial ¬clean-sep structures that DO have capacity**: **0
    counterexamples**. The load-bearing quantity is `non_CS_substrate_capacity_count = 0` — **no ¬clean-sep
    structure has *both* a stable substrate AND record capacity**. This is verified by exhaustive search over the
    bounded window; the **structural theorem** (`substrate ∧ capacity ∧ Δ_fact≠∅ = ∅` for *every* chiral structure,
    not only the 11,990) is the open upgrade — driving "true on 11,990" toward "true, period." **The
    structural-theorem attempt (Step 60, Mode T) returned `sharpened_external`, not a proof:** it *verified the
    reduction* (given substrate, `Δ_fact≠∅ ⟺ the witness scalar breaks a dim≥3 factor`), reducing the theorem to a
    single precisely-named open lemma **L60** (`substrate ∧ leak>0 ⟹ neutral-record-count < 2` — a *gauge-breaking*
    fact forcing a *matter-content* fact), and a mandatory converse probe **extended the empirical base beyond the
    11,990-structure carrier with bounded outside probes** (single SU(4)/SU(5)/SU(6) relaxed-field + two-factor
    3|4, 4|4 — distinct windows; hundreds capacity-positive) with **0 counterexamples** — but supplied **no
    structural proof**. So the gap is now one
    named lemma, not diffuse.
  - **Relocation, not derivation — and a law-landing consequence.** clean-sep is now the **gauge-shadow of
    memory-stability**, a *higher* recognition source — not derived from nothing. Physical fundamentality of
    memory-stability is the external-physics judgment (the standing frame-transfer question, now pushed up one
    layer). The grounding **emits an independently-checkable consequence** (law-landing obligation #2): the region
    "`substrate ∧ capacity ∧ Δ_fact≠∅`" is **forbidden** (empty) — a falsifiable structural prediction over the
    representation alphabet, checkable without assuming the construction.

---

## 7. Content cascade — the F26 contingent-modulus boundary (Steps 48–49, 54)

*Within* the selected `2|3` structure: the 8 SM-signature rosters relabeling-quotient to **2 distinct physical
content classes** (the SM + 1 SM-signature alternative). **Three genuinely-(definitionally)-distinct neutral
shadows** — integer charge-quantization of the physical color-singlet spectrum (Step 48), generic Yukawa-texture
connectivity (Step 49), and **full mass generation / fermion mass-matrix rank (Step 54, Door 1)** — each with
teeth (each rejects a degenerate control), are **all blind** to the SM-vs-alternative distinction. (Honest
nuance: the Step-54 rank shadow is definitionally *stronger* than Step-49 connectivity but coincides
**extensionally** with it on this 2-class carrier — confirmatory, not strongly-independent, evidence.) So the
final content pick is an **F26 contingent-modulus / observed-input** boundary; pinning it needs an E0 emergence
run, **excluded by design**. (Caveat: 3 blind shadows is strong but not a proof; more shadows could in principle
distinguish — diminishing returns, and it matches the physics expectation that content is observed-input.)
**N_gen lives in this residual** (§10).

---

## 8. Proton decay / monopoles — fork RESOLVED to the clean branch by memory-stability (Steps 45–46 typed; Step 65 resolved)

The **X/Y colored coset** (= the Step-41 `Δ_fact` witnesses; **absent** in the SM-clean `2|3` structure) is the
single object behind both. Two readings, both typed by SBT (Steps 45–46):
- **clean / shadow reading** (`Δ_fact = ∅`): baryon number **descends** (F27 obstruction 0 → no proton decay in
  this reading); finite gluing obstruction **0** (F48 → no monopole in this reading);
- **dynamical-breaking reading**: the coset is realized → baryon orbits enlarge (B violated) + nonzero gluing
  obstruction (monopole).

**Steps 45–46 typed the fork and left it `physical_reading_resolved = False` ("experiment decides").** That punt
**failed to use the framework**: Steps 57–59 had since established that **memory-stability ⟹ clean-separation**.
**Step 65 makes the connection and RESOLVES the fork — by the framework, not experiment.** The chain: the fork's
breaking reading is the **Step-41** gauge-layer `Δ_fact` (verified — *not* the Step-47/63 inter-layer
`Δ_fact(SM,GUT)`); Step 59's `non_CS_substrate_capacity_count = 0` ⇒ **no ¬clean-sep structure has both a stable
substrate and record capacity**; so **memory-stability** (substrate ∧ capacity ∧ distinguishability) ⇒ any
**record-bearing** structure is clean-sep = the **clean reading**. The breaking reading (proton decay / monopole)
is **excluded** for record-stable structures. **Non-circular** (neither substrate nor capacity alone is the clean
reading; only the conjunction). **Grade (honest):** `FORK_RESOLVED_TO_CLEAN_BY_MEMORY_STABILITY` — a **SELECT**
resolution **conditional on requiring memory-stability** (relocates up the tower), **enumeration-strength** (rests
on Step 59; the all-structures theorem **L64** is open), and **frame-transfer-limited** (toy → physical actuality).
So **not** "the proton is stable, period" / not a solution to the physical proton-decay problem — the framework
**selects** the no-decay/no-monopole branch for any record-bearing structure, by its own memory law.

---

## 9. Global-quotient (Z6) + hypercharge limits — the key new scope limit

State this plainly; it is the main "what the toy cannot see":

- **Algebra/product-level only.** The filter operates on the gauge **Lie algebra** / **product** structure
  `su(2) ⊕ su(3) ⊕ u(1)`. It does **not** certify the **global gauge group**. The physical SM is
  `(SU(3)×SU(2)×U(1)) / Z6`; the Z6 identification is a **global-topology fact** (which representations actually
  occur / the fundamental group), and the toy's gates (anomaly, chirality, mass-closure, clean-separation as
  implemented) are **blind** to it. So the result selects the **algebra**, not the global quotient.
- **Hypercharge normalization is a convention.** The `U(1)` is the unbroken-U(1) from the breaking; its charge
  normalization is fixed by the toy's unit conventions (`UNIT_DENOMINATOR=6`, `WEAK_SHIFT_UNIT=3`, Step 50), not
  derived. The only charge structure the toy *checks* is **integer charge-quantization of color singlets**
  (Step 48), which **both** content classes pass. So hypercharge assignments/normalization are **observed-input**.

This is the honest scope ceiling: **structure-level, algebra-level, product-level** — global quotient and
hypercharge normalization **not certified**.

**[Step 55 update — Door 2.]** The *computational* half of this blindness is now lifted: Step 55 extends the toy
to **compute** the maximal trivially-acting center (the global quotient) of a content class by exhaustive
congruence search, and it **recovers the SM's `Z6`** as a computed property of the input charge pattern
(`2t+3d+Y ≡ 0 mod 6`). Two honest qualifications stand: (i) this is **recovery, not derivation** — the
hypercharge pattern is the input and the center is the consequence (the toy still does not *derive* the pattern,
and `sin²θ_W` / coupling normalization remain GUT-input, untouched); (ii) requiring a nontrivial center is **not a
selector** — the alternative content class also computes to `Z6`, so the global structure does not narrow the
content residual. Net: the toy can now *see* the global quotient (and correctly recovers the SM's), but it neither
*derives* the hypercharge pattern nor *selects* the SM by the global structure.

---

## 10. Assumption-removal ladder + parked items

**Removal ladder** (which assumptions, removed, collapse the result — most load-bearing first):

1. **Clean-separation / proton-stability (§6)** — remove it and `SU(4)`-alone returns; the positive pick of
   `2|3` collapses to the small family. **Most load-bearing single condition.**
2. **The bounded window / component cap (C)** — the factor-count closure is **cap-conditional** (Step 44 rides on
   cap 6 = the SM's all-factor-row dim); a different cap is **untested** (3-factor structures could re-enter).
3. **The SU(N)-product alphabet (C)** — remove it and orthogonal/exceptional competitors (SO(10), E6, …) re-enter
   the comparison; they are currently **out-of-alphabet, not refuted** (§5).
4. **Single-Higgs minimality / the mass-closure proxy (A+C)** — the Step-35/36 narrowing depends on it.
5. **Imported (A) physics (anomaly-freedom, the Higgs mechanism)** — these are the **substrate**; remove them and
   there is no carrier at all.

**Parked items** (flatly stated, no spin):

- **Three generations (result I, Step 51):** **not derived.** The closure chain is **N_gen-blind** (passes
  identically for every N≥1); minimality picks N=1 (wrong); the only handle is a **recognition-source lower
  bound N≥3** from CP violation (`(N−1)(N−2)/2 > 0 ⟺ N≥3`, observed-input). N_gen is an **F26 contingent
  modulus / observed-input** (§7).
- **Higgs sector:** **imported (A).** The toy uses a single neutral scalar *witness* for mass-closure; the
  physical Higgs sector is not derived.
- **Naturalness / hierarchy:** **flatly not addressed.** Result C *reframes* the EW scale as an F47 small-selector
  region (≈3.96%) — a **reframe, not a solution**; the EW-scale value is **not derived**.
- **`2|3`-vs-`3|2|1` ordering:** the `2|3` label is just the `(dim SU(2) | dim SU(3))` ordering **convention**;
  there is **no physics in the ordering** (it is not a claim about a `3|2|1` hierarchy).

---

## Pointers

`MAIN_RESULTS.md` (the results A–I + grades — read first); `UNIFICATION_xy_coset.md` (the X/Y-coset spine);
`clean_separation_corpus_findings.md` (corpus on clean-separation); `gut_problems_vs_sbt_laws.md` (GUT-problem
× F-law map); `review_packets/sm_selection_layer_v4/ERRATUM_v4_provenance.md` (the A/B/C map); the step artifact
dirs — `step52_…_clean_separation_minimality` (§6), `step53_…_competitor_structures` (§5), and the **record /
memory-stability grounding** of clean-separation `step57_…_record_stability_descent` /
`step58_…_record_stability_broad_carrier` / `step59_…_record_stability_coverage` (§6 / Door 3); `LANDED_vs_NOT.md`
(the flat one-page verdict); `manager_log.md` (full audit trail incl. Steps 52–59); `TODO.md` #8 (this close-out's
plan).
