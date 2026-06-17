# Physics Layer Atlas — The Typing Rubric (Stage 1, FROZEN)

**Status:** FROZEN (Layer-A review fixes 1–8 applied by the assembler). This is the *elasticity firewall* of the atlas: the
deterministic procedure that FORCES every closure-package casting and every edge-tier from an audited
test, so that no casting can be tuned to flatter Six Birds Theory (SBT). Where this rubric and a frozen
SBT paper disagree, **the paper governs** — flag the discrepancy.

> **What this rubric is, and is not.** It is cartography + triage of the *currently-known* physics
> theories as closure-layers, and a typed audit of the *relations* between them. It is **not** a
> derivation engine, **not** a predictor, and **not** a reducer. Per the anti-reductionism primer §3,
> SBT has content *only between layers*; within a layer this rubric is silent (it is "textbook in
> costume" and we say so). Per §6, **up (emergence) and down (shadow) are not symmetric** — you may
> *run* a shadow as a derivation; you may **never** run an emergence as one. The rubric encodes that
> asymmetry as a hard gate, not a convention.

---

## 0. Orientation: what we type, and the predicted shape

We chart ~18–22 physics theories (the Theory Manifest) as **closure-package cards** (§A) and type
~35–45 inter-theory **edges** (the Edge Manifest). Each edge gets exactly one **modality** (§B) and
exactly one **edge-tier** (§C), assigned by the deterministic foreclosure decision-procedure (§C.5),
gated by the no-smuggling rules (§E), and licensed by the proton-mass calibration (§F).

**The registered null (the predicted shape).** The honest prediction is **foreclosure-dominance**: the
map should come out **shadow-heavy and emergence-sparse** — mostly E1 downward shadows (coarse-grainings
physics already accepts), with **sparse** E0 (run-only) and E3 (sharpened-gap) upward edges, and a thin
band of E2 (recognition-conditional) cross-edges. This shape is the **predicted result of SBT working,
not a failure** (primer §9.8). The rubric must be capable of returning *any* shape; the firewall
forbids steering toward this one. If the run comes out emergence-heavy, that is a finding, not a bug.

---

## A. The Closure-Package Card Schema (a physics theory as a layer)

A physics theory is cast as a closure package `T = (Z, f, Σ_f, E, D)` (digest §1). The card freezes
that casting **before** any edge touching it is typed. **HARD GATE E.12 (review fix R1):** the FULL card
(every field below) must be frozen and hashed in `closure_card_manifest.jsonl` for **every theory id and
every casting-bearing node** *before* any toy model `M` is declared or any `Ξ`/`RM`/`ID` is computed —
the `provisional_Z/f/E` **stubs in `theory_manifest.jsonl` are NOT sufficient for scoring**; a stub-only
casting at scoring time voids the incident edges' tiers and blocks the freeze. **Card field schema** (one
card per theory; this is the long form of the `theory_manifest.jsonl` stub fields, which a card must
expand and not contradict):

| Field | Type | Meaning / what it must contain |
|---|---|---|
| `id` | string | stable theory id (matches `theory_manifest.jsonl`). |
| `name` | string | human name (e.g. "Classical statistical mechanics"). |
| `Z` (carrier) | text | the **discrete/staged protocol objects** at a chosen stage: microstates on a lattice, truncated mode expansions, finite ensembles, Cauchy sequences of grid functions, finite operator algebras. Must be a *carrier*, not the macroscopic answer. |
| `f` (lens) | text | the **coarse-description map** `f : Z → X` — what the theory keeps / coarse-grains to (e.g. ensemble average → macroscopic field; trace-out of environment → reduced density matrix; block-spin map; RG step). |
| `Σ_f` (definability) | text | the predicates/observables **visible through `f`** — what is *expressible* in this layer's vocabulary. This is the field that decides non-definability claims later: an object is non-descending iff it is not in any source `Σ_f`. |
| `E` (packaging/completion) | text | the **completion endomap** (often idempotent) whose fixed points are the layer's "internally complete" objects (Cauchy completion, thermodynamic limit, decoherence-selected pointer basis, RG fixed point, Wilsonian integration-out). |
| `D` (defect ledger) | text | the **nonnegative diagnostics** with a monotonicity-under-refinement principle: error bounds, residual norms, route-mismatch, gradient-expansion remainder, `1/N` or `ℏ` or `v/c` or Knudsen-number control parameters. Names the small parameter(s). |
| `accepted_observables` | list | the layer's **own** accepted readouts (entropy, pressure; cross-section; metric in weak field; hadron mass spectrum). Used to forbid over-reading (§E.3). |
| `lawful_layer_note` | text | one line attesting the layer **closes**: its defects stabilize under refinement (digest §2). A non-closing candidate is not a layer and gets no card. |
| `casting_justification` | text | **REQUIRED.** Why THIS casting is *faithful to standard physics practice*, not chosen to make a downstream edge come out a desired tier. Must cite the standard coarse-graining/limit the casting tracks (e.g. "Z = microstates, f = ensemble average is the standard Gibbs construction"). Subject to gate E.0. |
| `casting_alternatives` | text | **REQUIRED.** At least one *plausible alternative casting* of `Z`/`f`/`E` that a competent physicist might choose, and a note on whether it would change any incident edge's tier. If an alternative would flip a tier, that edge is **tier-fragile** and must be flagged (§E.6). |
| `status` | enum | `frozen` / `provisional` / `excluded` (with reason). |

**Faithfulness over flattery (the card-level firewall).** The card is frozen first; the edges are
typed against the frozen card. You may not revise a card to change an edge tier after seeing the edge's
Ξ. If physics genuinely admits two standard castings, you pick the **more conservative** for the edge
per the **single conservative-default rule of §E.5** (`E1 > E2 > E0 > E3`, conservative = retreat
toward the unique terminal **E3**), and you record the alternative in `casting_alternatives`.
*(Review fix #4: the earlier "E0 < E3 < E2 < E1" string is deleted; it contradicted §E.5 and was a
tunability seam. There is now exactly ONE ordering, stated in §E.5.)*

### A.7 The Non-Peer Node Registry (review fix #2 — every edge endpoint must be typed)
Not every edge endpoint is a closure-package card. The most important edges are theory→observable and
theory→open-gap. Such endpoints are **registered, frozen nodes** with a declared `node_kind`, NOT
cards — and a node may not be cast on the fly (that was a smuggling surface). **Three node_kinds:**

| `node_kind` | meaning | allowed role in §C.5 |
|---|---|---|
| `observable_readout` | a measurable readout/phenomenon OF a source card (e.g. `hadron-spectrum`, `confinement`, `turbulence`, `arrow-of-time`, `measurement-outcome`, `phase-transitions-universality`, `singularity-theorems`, `berry-phase-holonomy`, `entanglement-geometry`, `spt-phases`) | TARGET only; **inherits the source card's frozen casting**; no fresh casting |
| `open_question` | a "why this?" question-node (e.g. `gauge-group-origin`, `fermion-generations`, `cosmological-constant`) | TARGET only; **forces the E0/E3 branch**; can NEVER seal E1/E2 |
| `candidate_substructure` | a sub-structure / candidate theory with no card (e.g. `conformal-field-theory`, `string-theory`, `lattice-gauge-theory`, `quantum-field-theory-curved`, `chiral-perturbation-theory`, `fermi-liquid-theory`, `decoherence-pointer-basis`, `classical-probability`, `many-body-quantum`) | may be source or target; if NOT experimentally established it may **NOT be the source of an E1 descent** (see the `established_status` field below) |

#### A.7.1 The `established_status` node field and the `may_source_E1` rule (review fix R6)
Every registered node (and, by extension, every theory card, which is trivially established) carries a
**machine-readable `established_status` ∈ {`experimentally_established`, `not_established`}**, justified
per node in the registry. The binding rule:

> **`may_source_E1` rule:** a node may be the **SOURCE of an E1 (computable-descent) edge ONLY IF its
> `established_status == experimentally_established`.** A `not_established` node has no
> accepted-observables set to descend *to from*, so an E1 descent sourced from it would be descending
> from a layer that is not known to close — a smuggling surface. A `not_established` node may still be a
> **target** of any edge, or the **source** of an E2/E0/E3 relation (recognition-landing, emergence, or
> sharpened gap), where no clean-descent claim is made.

This is enforced at freeze: for any edge whose `source_kind == candidate_substructure`, the freeze
validator looks up the source node's `established_status`; if it is `not_established` AND the edge's
sealed tier is E1, the bundle is **rejected** (the edge must be re-typed to E2/E0/E3 or the node promoted
to a full card with a justified established status). **Frozen node statuses (the relevant E1-sourcing
cases the review caught — E035a `lattice-gauge-theory → qcd` and E040 `many-body-quantum →
fermi-liquid-theory`):** `lattice-gauge-theory` and `many-body-quantum` are marked
`experimentally_established` (lattice gauge theory is a standard, validated computational formulation of
QCD; interacting many-body quantum systems are experimentally realized matter), so they MAY source the
E035a / E040 E1 descents — justified per node in `CONTRACT.json` `node_established_rule.frozen_statuses`.
Nodes such as `string-theory`, `conformal-field-theory` (as a free-standing layer), and
`quantum-field-theory-curved` are `not_established` and may NOT source an E1 (consistent with E037
string→SM sealing E3 and E023/E034 sealing E2, never E1).

The frozen `(node_id, node_kind, established_status)` registry lives in `edge_manifest_notes.md` and
machine-readably in `CONTRACT.json` (and each edge row also carries machine-checkable `source_kind` /
`target_kind` fields). The freeze-time assertion (enforced by the assembler): **every edge
`source_theory_id` / `target_theory_id` is EITHER a frozen theory-card id OR a frozen registered node id
of declared `node_kind`**, and **every `candidate_substructure` source of an E1 edge is
`experimentally_established`.** The bundle may not freeze while any endpoint is unresolved or any E1 is
sourced from a `not_established` node.

> **`effective-field-theory` ⇒ `rg_eft` (review fix #2(iii) / O3).** The former un-carded
> `effective-field-theory` node and the orphan card `rg_eft` are the SAME physics (EFT as the
> scale-organization layer). They are reconciled to the **single canonical card `rg_eft`**; edges E008
> (`relativistic_qft → rg_eft`) and E009 (`rg_eft → relativistic_qft`) use the card. No un-carded
> EFT node remains.

> **`brownian-motion` ⇒ `brownian_langevin`** and the peer renames (`quantum-chromodynamics → qcd`,
> `quantum-electrodynamics → qed`, `electrodynamics → classical_electromagnetism`,
> `navier-stokes → hydrodynamics`, `condensed-matter → condensed_matter_spt`,
> `lambda-cdm-cosmology → lambda_cdm`) are applied per the frozen alias table (review fix #1; full table
> in `edge_manifest_notes.md` and `FREEZE_NOTES.md`).

---

## B. The Edge-Modality Taxonomy (one modality per edge, with a crisp operational test)

The **modality** is *what kind of inter-layer relation* the edge is — independent of, and assigned
before, the edge-tier. Each modality has a CRISP OPERATIONAL TEST. An edge carries exactly one primary
modality; if two tests pass, see §B.7 (precedence) and flag it.

### B.1 Descent / Shadow (DOWN) — "what can be cast over what"
- **Direction:** higher (source) → lower (target). A projection / coarse-graining / limit.
- **Operational test (DESCENT-LEGALITY):** there exists a quotient map `q` such that the source readout,
  pushed through `q`, lands in the target's `Σ_f`, **and** the descent does **not over-read** the source
  (the recovered answer is in `target.accepted_observables`, §E.3). Operationally: declare the finite
  toy model (§D.4), set `L` = native (target) probe family, `D` = dissolving (source) probe family, and
  test factorization via **Ξ** (§D.1). **Ξ = 0 / kernel-containment / `D₀ = A·L₀` ⇒ the descent is
  exact and computable.** This is the *runnable* arrow (primer §6): a shadow is computable from its
  source.
- **Physics exemplars:** statistical-mechanics → thermodynamics; kinetic theory → hydrodynamics
  (Chapman–Enskog); QFT → low-energy EFT (Wilsonian RG); GR → Newtonian weak-field; QM+decoherence →
  classical; EM → geometrical optics (eikonal).

### B.2 Strict-extension / Emergence (UP) — "what can come from what"
- **Direction:** lower (source/substrate) → higher (emergent). A **package change**, not iteration.
- **Operational test (NON-FACTORIZATION):** the emergent layer's object map `π₁` does **not** factor
  through the base object map `π₀` — there is **no** `φ` with `π₁ = φ∘π₀` (primer §4). Operationally, on
  the declared toy model: exhibit two base states identified by `π₀` (same in `source.Σ_f`) that the
  candidate emergent readout **distinguishes**. If such a pair exists, the readout is **non-definable
  from below** — emergence. **You may NOT run this arrow as a derivation.** The test only *certifies the
  gap*; it never closes it. (This is the load-bearing asymmetry; see §C.6.)
- **Physics exemplars:** the QCD mass scale / proton mass born by dimensional transmutation (run-only —
  the canonical E0 anchor); a thermodynamic-limit phase transition non-analyticity unreachable from any
  finite system; the arrow-of-time / second law as a strict-extension content.

### B.3 F41 Duality-equivalence — "two faces of one content"
- **Operational test (DUALITY-EQUIVALENCE):** a *bijective, structure-preserving, observable-matching*
  correspondence between the two layers' accepted observables, **invertible both ways** with audited
  dictionaries. Test on the toy model: the two probe families generate the **same** `Σ_f` up to the
  dictionary (Ξ = 0 in *both* directions, `D|L` and `L|D`). This is symmetric — neither layer is the
  "source." Relabeling that fails invertibility-with-content is **not** a duality (§E.4).
- **Physics exemplars:** Kramers–Wannier / order–disorder; particle–wave / position–momentum bases;
  AdS/CFT as a *candidate* duality (typically lands **conditional**, since the full dictionary is not
  proven — see E2). T-duality. Electric–magnetic (Montonen–Olive) duality.

### B.4 F51 Common-refinement — "unification as a join, never a reduction"
- **Operational test (COMMON-THIRD):** there is a *third* layer `W` that **both** A and B descend from
  by legal shadows (B.1) — `W → A` and `W → B` each pass DESCENT-LEGALITY — and A, B do **not** descend
  from each other. The edge is recorded as the pair of shadows plus the join `W`. This is the **only**
  licensed form of "unification" in SBT (primer §9.1): a join/recognition, **never** a factorization of
  one layer into the other.
- **Physics exemplars:** special relativity as the common refinement under which E and B unify (the
  field tensor); electroweak theory as the common refinement of (low-energy) EM and weak interactions;
  thermodynamics + mechanics jointly refined by statistical mechanics.

### B.5 Currency / Shadow-price — "top-down coupling without reduction"
- **Operational test (SHADOW-PRICE):** a higher-layer constraint induces, on the lower layer, a
  **dual/price variable** that couples back *down* (a Lagrange-multiplier / control-currency, "To Spend
  a Stone"). Operationally: the constraint defines a budgeted positive obstruction whose **dual** is a
  finite shadow-price computable on the toy model (the residual Ξ ≻ 0 read as currency, digest §5). The
  edge is typed by *whether the price descends* (E1) or *needs a named principle / run* (E2/E0).
- **Physics exemplars:** temperature/chemical-potential as shadow-prices of energy/particle constraints;
  surface gravity as the "price" in black-hole thermodynamics; effective couplings as RG shadow-prices
  of the cutoff.

### B.6 Holonomy / Anti-localization — "the answer depends on the route"
- **Operational test (ROUTE-MISMATCH):** two admissible closure/evolution routes from the same start to
  the same end give **different** results; the diagnostic `RM` (§D.2) is **nonzero and does not decay**
  under refinement. The content is *non-local in the layer-graph* — it cannot be localized to either
  endpoint layer. (If `RM → 0` under refinement, there is no holonomy; the routes agree.)
- **Physics exemplars:** Berry phase / geometric phase; Aharonov–Bohm; anomaly inflow (a bulk route vs a
  boundary route disagree by the anomaly); path-dependence of adiabatic invariants.

### B.6a Recognition-landing — "the edge closes ONLY by importing a named external principle" (review fix R2)
This is the canonical modality for the framework's core honest move (primer §7, **recognition-mode
landing**): a hard edge that **no framework-internal route closes**, and whose entire content is the
**named external import** that lands it conditionally. It is its own modality precisely because the
edges that carry it span **both arrow directions** (up *and* down) and **different underlying physical
mechanisms** (a failed descent, a top-down currency, a located emergence) — what unifies them is **not**
the arrow or the mechanism but the single fact that *the only thing that closes the edge is an imported
named principle*. Folding them back into descent/currency/emergence would scatter them inconsistently and
**erase** that defining fact, which is exactly the seam review fix R2 closes.

> **Membership is rule-driven, not a hard count (review fix R2 re-review).** The set of recognition-landing
> edges is **defined as "every edge row in `edge_manifest.jsonl` whose audited modality ==
> `recognition-landing`"** — the validator enumerates them from the manifest and asserts the set equals
> `CONTRACT.json` `recognition_resolution.affected_edges`; it does **not** trust a frozen integer. At this
> freeze that set has **8 rows: E007, E022, E025, E026, E027a, E028b, E030, E033** (E028b — the
> imported-Λ/dark-matter/measure leg of the E028 split — is a full recognition-landing row and is included;
> the v2 list of 7 that omitted it is corrected). **Named-import check (enforced at freeze, validator check
> C11):** every recognition-landing row must carry **exactly one** non-empty `named_import`, and the
> `CONTRACT.json` import for that row must be a **single frozen principle, not a menu**. In particular
> **E007's frozen import is Gleason's theorem ONLY**; envariance (Zurek) and the decision-theoretic
> axiom set (Deutsch–Wallace) are recorded only as `alternatives_not_used` on the E007 edge row and are
> **not** contract imports and **not** substitutable at typing time (gate E.0).
- **Direction:** either (`up` or `down`); arrow is recorded but is *not* what types the edge.
- **Operational test (RECOGNITION-ONLY):** ALL THREE must hold on the declared toy model `M`:
  **(i)** no internal **descent** closes it — the descent-test fails (Ξ ≠ 0 stably, §D.1/Step 1);
  **(ii)** no internal **duality** (B.3) and no internal **refinement/common-third** (B.4) closes it —
  neither stricter structural test passes; **(iii)** the edge is characterized **only** by a single,
  **named, citable external principle** (a theorem, a physical principle, a stated ansatz/assumption)
  imported under an **explicitly stated closure assumption** — remove that named import and **no**
  inter-layer relation remains (the §E.4 relabeling residual test, applied to the *import*). If (i)–(iii)
  all hold, the edge is a **recognition-landing**. *This modality NEVER seals E1 and NEVER seals E0:* a
  recognition-landing IS the import, so its only emittable tier is **E2** (recognition-conditional); if no
  named principle is found, it is not a recognition-landing at all but a **sharpened gap E3** (and must be
  re-typed under whichever modality its arrow indicates — emergence-up or descent-down — before sealing).
- **Why not E1/E0/E3 under this modality:** E1 would be an internal computable descent (then it is B.1,
  not recognition); E0 would be a constructible run-object (then it is B.2 emergence-up, deferred); E3 is
  reached only when recognition-search returns **nothing named** — at which point the edge is, by
  definition, no longer a recognition-landing. The modality and its sole tier E2 are therefore locked
  together: **recognition-landing ⟺ E2.**
- **Physics exemplars (the 8 frozen recognition-landing edges):** E007 (Born rule — single frozen import:
  **Gleason's theorem** only; envariance / decision-theoretic axioms are `alternatives_not_used`, see §E.0
  frozen-single-import); E022 (thermo → GR recovery — Jacobson's "Einstein equation of state"); E025 (QM →
  thermo — the ETH ansatz); E026 (QM → pointer-basis — the einselection / predictability-sieve criterion);
  E027a (SPT classification — the group-cohomology / cobordism classification); E028b (GR → ΛCDM
  predictive content — the imported value of Λ + dark-matter sector + initial-conditions/measure); E030
  (thermo → arrow-of-time — the Past Hypothesis); E033 (classical mechanics → thermo, H-theorem — the
  Stosszahlansatz / molecular-chaos assumption).

### B.7 Modality precedence + multi-modality flag
If more than one operational test passes, assign in this precedence (most-constraining first) and
**flag the edge as multi-modal** in notes: Duality (B.3) > Common-refinement (B.4) > Holonomy (B.6) >
Currency (B.5) > Descent (B.1) > Emergence (B.2). **Recognition-landing (B.6a) is NOT in this precedence
chain because it is residual-by-construction:** an edge is a recognition-landing precisely when the
descent (B.1), duality (B.3), and common-refinement (B.4) tests have *all failed* internally and only a
named import remains — so it is assigned *after* those tests fail, never in competition with them. (If a
structural test passes, the edge is that structural modality, not a recognition-landing.) Rationale:
duality/common-refinement are the strongest structural claims and must be *earned*, so they are tested
first and demoted to descent/emergence if their stricter test fails. **Demotion is one-directional**: you
may demote a claimed duality to a mere descent on test failure; you may **never** promote a descent to a
duality to flatter symmetry.

### B.7a Primary vs. secondary modality — the MODALITY PRECEDENCE RULE (Pause-2 calibration, review fix R-P2)
The external Pause-2 review (`EXTERNAL_REVIEW_PAUSE2.md`) adjudicated a MODALITY-label ambiguity on the
recognition control **E005** (GR → black-hole-thermodynamics) and resolved it by **option (b): a
primary + secondary modality with an explicit precedence rule.** This subsection encodes that rule. It
**does not rename** the existing per-edge `modality` field: that field **IS the `primary_modality`**.

> **MODALITY PRECEDENCE RULE.** Each edge has exactly **one** `primary_modality` — the existing
> `modality` field — and that primary modality is the **only** one used for `(modality, tier)`
> emittability (§B.8) and for headline reporting / the registered-null tally. An edge MAY additionally
> carry an **optional** `secondary_modalities` array and/or `conditionality_flags` array, which are
> **descriptive residual annotations only** and are **never** used for emittability or counting.
>
> **The precedence:**
> 1. **A STRUCTURAL modality is PRIMARY.** If any *structural* test passes —
>    **duality (B.3), common-refinement (B.4), holonomy (B.6), currency/shadow-price (B.5),
>    descent (B.1), or emergence (B.2)** — that structural modality is the `primary_modality`
>    (resolved among themselves by the §B.7 precedence chain when more than one passes).
> 2. **`recognition-landing` (B.6a) is PRIMARY ONLY as a residual** — only when **NO** structural
>    modality closes the edge **AND** the imported named principle is the *entire* landing mechanism
>    (the §B.6a RECOGNITION-ONLY test (i)–(iii) all hold). This is unchanged from §B.6a / §B.7.
> 3. **`recognition-conditional` is a SECONDARY FLAG, not primary recognition-landing.** If a
>    **structural** modality is primary but the edge is at tier **E2** and still **requires a named
>    external import** to close (an E2 structural edge whose closure leans on an imported principle),
>    record **`recognition-conditional`** in the edge's `conditionality_flags` (equivalently as a
>    `secondary_modalities` entry). This is **distinct** from primary `recognition-landing`: the edge's
>    structural test *passed* (so it is NOT residual), but its E2 closure is conditional on a named
>    import. The primary modality stays the structural one; the secondary flag records the import
>    conditionality.
>
> **The discriminator (why this is not primary recognition-landing).** Primary `recognition-landing`
> requires that NO structural test passes (§B.6a test (i)–(iii)); a `recognition-conditional` SECONDARY
> flag is used precisely when a structural test **did** pass but the edge nevertheless lands at E2 via a
> named import. Structural-test-passed ⇒ structural primary + `recognition-conditional` secondary;
> structural-test-failed-and-only-a-named-import-remains ⇒ primary `recognition-landing`. The two are
> mutually exclusive on a given edge: an edge is **either** primary `recognition-landing` (residual)
> **or** a structural primary carrying a `recognition-conditional` secondary flag, never both.

**Worked exemplar — E005 (GR → black-hole-thermodynamics).** The currency/shadow-price test **passes**:
the rubric's currency def (§B.5, this file, the **"surface gravity as the 'price' in black-hole
thermodynamics"** exemplar) is the structural relation here. So **`primary_modality = currency-shadow-price`**
(B.5), tier **E2** (the price needs a named principle — §B.8 currency/E2 cell). Because classical GR alone
does not close the *thermal* content (its toy-model Ξ≈0 is an **over-read**: the `ħ` coefficients and the
thermal reinterpretation are not in GR's `Σ_f`), the E2 closure imports a named principle and the edge
therefore carries **`conditionality_flags = ["recognition-conditional"]`** as a SECONDARY flag. The
frozen named import is **QFT-in-curved-spacetime (Hawking thermal flux) + the first law of black-hole
mechanics, under the semiclassical no-back-reaction assumption (= the E034 construction)** — frozen at
declaration, NOT substitutable (gate E.0). E005 is therefore a **structural-currency-E2 edge with a
recognition-conditional secondary flag**, NOT a primary `recognition-landing`. (Contrast E022, the
opposite-arrow thermo → GR *recovery*, which IS a primary `recognition-landing` because no structural GR
test closes it and Jacobson's "Einstein equation of state" is the entire landing mechanism — see §B.6a.)

**Import-hygiene parity (cross-reference to gate E.0; new validator check C13).** The named-import
freeze that gate E.0 / validator check **C11** enforces for primary `recognition-landing` rows applies
**in parallel** (the new validator check **C13**) to a **secondary** `recognition-conditional` flag:
any E2 edge carrying `recognition-conditional` MUST still freeze its `named_import` to a **single**
principle (no menu), frozen at declaration and not substituted at typing time. The check is the same
hygiene, applied to the secondary flag rather than the primary modality (see §E.0 and `CONTRACT.json`
`secondary_modality_schema.import_hygiene_parallel_check`). (C12 is the pre-existing registered-null /
stale-prose guard and is unchanged; this parallel hygiene check is C13.)

### B.8 The modality ↔ tier compatibility table (review fix #6 — enforced at freeze)
Modality and tier are orthogonal, but **not every pair is emittable by the deterministic procedure
(§C.5)**. A row whose `(modality, tier)` pair is **not** in the table below is **rejected at freeze**.
This kills the two specific inconsistencies the review caught (`shadow-down E0` and `emergence-up E1`)
and any future one. **The `modality` used in this table is the `primary_modality` (§B.7a)** — the
existing per-edge `modality` field. **`secondary_modalities` / `conditionality_flags` (e.g. a
`recognition-conditional` flag) do NOT enter the emittability check and are NEVER counted in the
registered null;** they are descriptive residual annotations. E005 is emittable as
`(currency-shadow-price, E2)` — its PRIMARY pair — and its `recognition-conditional` secondary flag is
not tested against this table.

| modality \ tier | E1 | E2 | E0 | E3 |
|---|---|---|---|---|
| **B.1 Descent / shadow-down** | ✅ (Ξ=0 descent) | ✅ (descent fails, named import) | ❌ **NOT emittable** — a descent that *passes* is E1; one that *fails* falls to E2/E3, never E0 | ✅ (descent fails, no import, no run) |
| **B.2 Emergence / up** | ❌ **NOT emittable** — the up arrow is *never run as a derivation* (gate E.8); E1 is a down-descent only | ✅ (classification via named math, e.g. SPT cohomology) | ✅ (run-only non-descending readout) | ✅ (sharpened gap / no-go) |
| **B.3 Duality (F41)** | ✅ (Ξ=0 both ways) | ✅ (conjectured dictionary, named) | ❌ | ✅ (dictionary fails / unproven-and-unnamed) |
| **B.4 Common-refinement (F51)** | ✅ (both legs descend) | ✅ (a leg needs a named import) | ❌ | ✅ (no common third) |
| **B.5 Currency / shadow-price** | ✅ (price descends) | ✅ (price needs a named principle) | ✅ (price is a run-readout) | ✅ (price is an open gap) |
| **B.6 Holonomy** | ✅ (computable RM) | ✅ (closure needs a named import) | ❌ | ✅ (irreducible non-decaying RM, open) |
| **B.6a Recognition-landing** | ❌ **NOT emittable** — a closing computable descent is B.1 E1, not recognition | ✅ **ONLY emittable tier** — closes solely by one named external import, conditional | ❌ **NOT emittable** — a constructible run-object is B.2 emergence-up E0, not recognition | ❌ **NOT emittable** — if recognition-search returns nothing named it is no longer a recognition-landing; re-type by arrow (emergence-up / descent-down) and seal E3 there |

> **Why `shadow-down E0` and `emergence-up E1` are forbidden.** A *descent* (B.1) is the **down** arrow:
> if it passes it is E1, if it fails it falls to recognition/gap — its physical content is never
> "run-only emergence," because emergence is the **up** arrow. A row where the *physical readouts are
> run-generated non-descending content* must carry modality **emergence-up** (B.2), even if a *formal*
> continuum limit exists (record that formal limit as a separate `shadow-down E1`-candidate row, or in
> the row's `value_split`). Conversely **no** `emergence-up` row may be E1: the up arrow is certified as
> a *gap* (non-factorization), never **run** as a derivation (primer §6; gate E.8). The two split rows
> E035a/E035b and E027a/E027b in the edge manifest are exactly this correction.

> **Recognition-landing is tier-locked to E2 (review fix R2).** The modality `recognition-landing` (B.6a)
> has **exactly one** emittable tier, **E2** — it *is* the imported named principle, so it can be neither
> a computable descent (E1, then it is B.1), nor a constructible run-object (E0, then it is B.2
> emergence-up), nor a no-named-import gap (E3, then it is not a recognition-landing). The 8 frozen
> recognition-landing edges — E007, E022, E025, E026, E027a, E028b, E030, E033 — therefore all carry tier
> **E2**.
> **Schema check (enforced at freeze, R2):** every edge's `provisional_modality_guess` (and any audited
> modality) MUST be one of the canonical modality strings of §B — i.e. exactly one of
> {`shadow-down`, `emergence-up`, `duality-equivalence`, `common-refinement`, `currency-shadow-price`,
> `holonomy`, `recognition-landing`}. Any other string (e.g. a free-text label) is **rejected at freeze**.
> The canonical list and the per-modality allowed-tier sets are frozen machine-readably in
> `CONTRACT.json` (`canonical_modalities`, `modality_tier_compat`); the freeze validator reads that file,
> not this prose.

---

## C. The Edge-Tier Definitions (E0/E1/E2/E3) and the deterministic foreclosure decision-procedure

The **edge-tier** is the *closure status* of the edge — orthogonal to the modality. Four tiers, adapted
from the Erdős tier map (`enums.md` §III) to physics edges. **Tiers are NEVER summed** (E1 with E2/E0 is
forbidden, §G).

### C.1 E1 — Computable descent (the runnable shadow)
A **coarse-graining physics already accepts**, checkable *now* on a finite toy model.
- **Sealing condition:** the modality is Descent/Shadow (B.1) **or** a Duality both-ways (B.3), and on
  the **declared finite toy model** the **NORMALIZED (relative) residual `ξ_rel → ~machine-zero
  STABLY`** across both declared refinements `h₁ ⊏ h₂` (§D.1.1; equivalently `Ξ = 0` /
  kernel-containment `ker L₀ ⊆ ker D₀` / a factorization `D₀ = A·L₀`; §D.1), with **no over-reading**
  (§E.3). **A small RAW Ξ is NOT sufficient and a large raw Ξ is NOT disqualifying — the verdict is read
  off `ξ_rel`, not the raw Ξ norm** (Pause-2, review fix R-P2). Report both raw Ξ and `ξ_rel`.
- **Reading:** the target readout *descends* (is computable) from the source. The arrow is runnable.
- **Calibration controls (must come out E1):** statistical-mechanics → thermodynamics; special
  relativity → Galilean/Newtonian limit; kinetic theory → hydrodynamics.

### C.2 E2 — Recognition-conditional (lands only by importing a NAMED external principle)
The edge does **not** seal as a computable descent, but a **named, citable external principle** closes
it **under a stated assumption** (Attack-Foreclosure v5 + recognition-mode landing, digest §6).
- **Sealing condition:** descent-test fails (Ξ ≠ 0), AND a *named, load-bearing external source* (cite
  it: a theorem, a physical principle, a conjectured correspondence) closes the edge **conditionally**,
  with the closure assumption stated explicitly. Reported **separately** and labeled "conditional under
  the named assumption." Never merged with E1 (§G).
- **Reading:** SBT *recognizes* and *names* what would close it; it does not derive it. The landing is a
  **conditional peer**, not a collapse, of the (foreclosed) internal-derivation route.
- **Calibration control (must come out E2):** the **single frozen** recognition case is **E005 (GR →
  black-hole thermodynamics)**, named import = **QFT in curved spacetime (Hawking thermal flux) + the
  first law of black-hole mechanics**, under the semiclassical no-back-reaction assumption (= the E034
  construction). It lands **conditional on that named principle**, not as a derivation. *(Review fix
  #3: the named import is frozen to this one principle and may NOT be substituted at typing time. Do
  NOT use "Jacobson" for E005 — Jacobson's "Einstein equation of state" is the opposite-arrow edge
  **E022** (thermo → GR recovery), a separate E2 edge; conflating the two is a route-direction error
  the up/down asymmetry forbids.)*

### C.3 E3 — Sharpened gap / foreclosure no-go (located + typed, NOT closed)
The edge **cannot** be sealed as descent, **no** named external principle closes it, and **no**
constructible non-descending object whose generation needs a run is on offer. SBT's job here is to
**locate and sharpen** the gap (which `Σ_f` predicate is missing; which route mismatches; where
factorization provably fails), **not** to close it.
- **Sealing condition:** descent-test fails; recognition-search returns nothing named; the run-search
  (C.4) finds no constructible run-generated object. Emit a **sharpened restatement** of the obligation
  and/or a **bounded no-go** (no member of a declared bounded grammar discharges it).
- **Reading:** a *typed open problem*. The hard/embarrassing edges live here.
- **Exemplars (predicted):** QM ↔ GR (the quantum-gravity gap); SM gauge-group origin
  SU(3)×SU(2)×U(1); three-generations / mass hierarchy; cosmological-constant value as a *cross-layer
  consistency* gap (its *generation* as a run is E0; its *naturalness/why-this-value* sharpened gap is
  E3 — see §C.7 on the E0/E3 split).

### C.4 E0 — Run-only / computationally irreducible (FLAGGED OUT, DEFERRED → Run-Target Manifest)
A **constant or scale born only by running a substrate** — no shortcut, no descent, no named principle
*derives* it; it is the readout of an irreducible run (primer §5, §1).
- **Sealing condition:** descent-test fails; recognition-search returns no principle that *derives* it
  (a principle that *names the run* is fine and expected); AND there is a **constructible non-descending
  object** (B.2 non-factorization holds) whose generation provably **requires a run** (e.g. dimensional
  transmutation generating a scale a finite truncation cannot hold).
- **HARD SCOPE GATE:** E0 edges are **flagged out and deferred** to the *Run-Target Manifest*. **We do
  NOT run them.** We spec the run (substrate, lens, the out-of-sample observable that would validate it
  per primer §8); we never execute it, never derive the constant, never claim the number. This is the
  scope boundary the whole atlas stops at.
- **Calibration anchor (must come out E0):** QCD → hadron masses / proton mass. The spec must match
  **physical-quark-mass lattice QCD**: there is **no free proton/hadron MASS parameter**; the quark
  masses and the coupling/scale are **fixed independently under the declared lattice-QCD protocol**
  (physical-quark-mass lattice QCD, with the scale set by **one hadronic input** and the running generated
  by dimensional transmutation). The **proton-mass / hadron-spectrum readout is out-of-sample and NOT
  fitted** — it is the readout of an irreducible run, not a tuned quantity. This is the canonical
  already-resolved E0 case (§F).

### C.5 THE DETERMINISTIC FORECLOSURE DECISION-PROCEDURE (run in this exact order; log every branch)

```
INPUT: a source endpoint S, a target endpoint T (each EITHER a frozen theory card §A OR a frozen
       registered node §A.7 of declared node_kind), a declared finite toy model M (declared BEFORE any
       computation — gate E.1), and the edge's assigned modality (§B).

STEP 0  PRECONDITION (review fix #1 + #2). Confirm:
        (0a) BOTH endpoints RESOLVE: each is either a frozen theory-card id (§A) or a frozen registered
             node id of declared node_kind ∈ {observable_readout, open_question, candidate_substructure}
             (§A.7). If any endpoint is unresolved → HALT (the bundle may not freeze with an unresolved
             endpoint).
        (0b) NODE-KIND CONSTRAINTS:
             • an `open_question` target forces the E0/E3 branch ONLY — it can NEVER seal E1/E2
               (there is no `accepted_observables` set to descend to / no named principle is being
               imported INTO it; cf §C.7 and the E3 anti-controls);
             • an `observable_readout` target is the READOUT of its source card and INHERITS the source
               card's frozen casting (Z,f,Σ_f,accepted_observables) — NO fresh casting is allowed (this
               closes the §A smuggling surface);
             • a `candidate_substructure` node that is NOT experimentally established may NOT be the
               SOURCE of an E1 descent (it has no accepted_observables to descend to); it may be a
               target, or the source of an E2/E0/E3 relation.
        (0c) M is declared + hashed (E.1), refinement-stable-checkable (E.9), second-annotator-faithful
             (E.10), AND the (modality, tier-to-be-sealed) pair is in the §B.8 emittability table.
        (0d) IF the theory-pair admits NO honest finite toy model M (no faithful finite stand-in exists,
             E.10 fails for faithfulness-by-construction) → the descent-test is VACUOUS; SEAL E3 by the
             distinct "no faithful M" sub-reason (record it as `e3_subreason: no_faithful_M`, NOT folded
             into a run-and-failed descent E3). HALT the numeric branches. (Review fix #5(iii).)

STEP 1  DESCENT-TEST (down arrow, runnable). On M, build L = native(target) and D = dissolving(source)
        probe families and the audit energy C (§D.4). Compute Ξ_C(D|L) AND the NORMALIZED residual
        ξ_rel = ‖Ξ‖/‖K_DD‖ (§D.1.1) at TWO refinements h₁ ⊏ h₂ (gate E.9). Log BOTH raw Ξ and ξ_rel;
        read the verdict off ξ_rel (a small raw Ξ is NOT sufficient — review fix R-P2).
          • If ξ_rel → ~machine-zero STABLY AT BOTH refinements (equiv. Ξ = 0, ker L₀ ⊆ ker D₀,
            D₀ = A·L₀) AND no-over-read (E.3) passes:
                ───────────────────────────────────────────────► SEAL  E1.   STOP.
            (If the form descends but the numeric VALUES are run-only/imported, record a generalized
             `value_split` {form_tier, value_tier, split_type, value_node} with split_type ∈
             {form_value, form_value_imported, theorem_run}. The **reported (headline) leg is
             split-type-dependent (review fix R3, see §E.3):** for `form_value`/`form_value_imported`
             the reported leg is the **value_tier** (the edge's PRIMARY claim is the predictive
             connection, which needs the imported/run-generated value); for `theorem_run` the reported
             leg is the **form_tier** (the primary claim is the analytic theorem). The NON-reported leg
             is carried into the Run-Target Manifest (E0) or conditional ledger (E2), NEVER summed —
             review fix #8(i), generalized by R5/R3. The `theorem_run` split (open-theorem E3 vs
             run-exhibited E0, e.g. E041) is recorded at STEP 4 when the analytic status is a foreclosed
             gap.)
          • If the verdict FLIPS between h₁ and h₂ (tier-fragile, E.6/E.9): do NOT seal E1; demote toward
            E3 (the conservative terminal).
          • Else (ξ_rel stays bounded away from zero — a stable positive normalized residual with
            analytic control; equiv. Ξ ≠ 0 stably): record Ξ and ξ_rel (the residual is the located
            obstruction); continue.

STEP 2  RECOGNITION-SEARCH (must ACTUALLY be run and logged — gate E.7). Search for a NAMED, citable
        external principle/theorem/correspondence that closes the edge UNDER A STATED ASSUMPTION.
          • If found AND the smuggle-audit (E.4) + no-over-read (E.3) pass AND the assumption is stated:
                ───────────────────────────────────────────────► SEAL  E2 (conditional). STOP.
            (Record: the named source, the closure assumption, "conditional on <assumption>". Reported
             separately; never summed with E1.)
          • Else: continue.

STEP 3  RUN-SEARCH (constructible non-descending object). Ask: is there a CONSTRUCTIBLE non-descending
        object (B.2 non-factorization holds on M) whose generation provably REQUIRES a run (a scale/
        constant the substrate generates only by running, no finite shortcut)?
          • If yes:
                ───────────────────────────────────────────────► SEAL  E0 (run-only). DEFER.
            (Flag out to the Run-Target Manifest: spec the substrate + lens + out-of-sample validator.
             DO NOT run. DO NOT derive the constant.)
          • Else: continue.

STEP 4  FORECLOSURE. Descent failed, no named principle, no constructible run-object:
                ───────────────────────────────────────────────► SEAL  E3 (sharpened gap / no-go).
            (Emit the sharpened restatement and/or bounded no-go; type WHICH Σ_f predicate is missing
             and WHERE factorization fails. Locate, do not close.)

INVARIANT (no-smuggling): an edge may not be sealed E0 until BOTH the descent-test (Step 1) AND the
recognition-search (Step 2) have ACTUALLY been run and logged (gate E.7). On ANY doubt at a branch,
take the CONSERVATIVE tier (§E.5), never the more flattering one.
```

This procedure is **deterministic**: given frozen `(S, T, M, modality)`, the same tier is produced every
time. The only inputs are audited tests; there is no free tier knob.

### C.6 The up/down asymmetry as a hard gate (primer §6, the load-bearing rule)
The decision-procedure **only ever runs the DOWN arrow** (Step 1, the descent-test) as a computation.
Steps 2–4 **never run the UP arrow**: emergence is certified by *non-factorization* (a gap), never
closed by a derivation. Concretely: **no edge may be sealed E1 by an UP-direction computation.** If a
modeler tries to "derive" an emergent readout from below, the rubric rejects it at gate E.8
(anti-emergence-derivation). E0 *records* that a run would produce the object; it does **not** run it,
and E0 is never re-labeled E1.

### C.7 The E0/E3 split rule (a recurring confusion — fix it explicitly)
For a hard target with a definite numerical value (cosmological constant, a mass ratio, a coupling):
- the **generation** of the value by a substrate run is **E0** (run-only; deferred), **iff** Step 3's
  constructible-run-object exists;
- the **"why this value / naturalness / selection"** question — when there is *no* constructible run
  whose readout is *that* value within the known substrate — is **E3** (sharpened gap).
- A value that is simply *measured input* to a theory (not generated by any modeled substrate and not
  claimed derivable) is **out of scope** as an edge readout; record it on the card as an
  `accepted_observable` input, not as a typed edge. (This prevents smuggling "the SM has 19 parameters"
  into a pile of fake E0 edges.)

---

## D. Diagnostic Definitions (computed on DECLARED FINITE toy models ONLY)

> **Binding rule for all of §D.** Every diagnostic is computed as **finite linear algebra on a declared
> finite toy model** — never by an irreducible run, never on the full theory, never on real data. The
> toy model is declared and hashed **before** computation (gate E.1). The diagnostic *certifies the
> casting relation on the toy model*; it is **not** an empirical claim about the world (primer §10;
> digest §9). A toy-model Ξ = 0 licenses the *tier*, not a physical prediction.

### D.1 The adequacy residual Ξ (Schur complement) — the descent diagnostic
Source: *Adequacy Residuals and Blind-Spot Currency* (def. of every Ξ symbol). On the finite toy model,
with finite matrices `L₀` (native/target probe), `D₀` (dissolving/source probe), and a PSD **audit
energy** `C` with `C₀ = C` (legal-energy quotient; null-mode legality assumed), the **block
currencies** are
```
  K_LL = L₀ C₀⁻¹ L₀*,   K_DL = D₀ C₀⁻¹ L₀*,   K_LD = K_DL* = L₀ C₀⁻¹ D₀*,   K_DD = D₀ C₀⁻¹ D₀*,
```
and the **adequacy residual** is the (2,2) Schur complement
```
  Ξ_C(D | L) = K_DD − K_DL · K_LL† · K_LD      (†  = Moore–Penrose pseudoinverse).
```
**Exact-adequacy equivalence (the E1 sealing condition):**
```
  Ξ_C(D|L) = 0   ⟺   ker L₀ ⊆ ker D₀ (on the legal quotient)   ⟺   ∃ A : D₀ = A · L₀.
```
- `Ξ = 0` ⇒ the source readout *factors through* the target lens ⇒ a clean, computable **descent**
  (E1). `Ξ ≻ 0` ⇒ a **budgeted positive obstruction** = the **blind-spot currency**: what the target
  layer cannot see that the source reveals; this is the located obstruction that pushes the edge to
  Step 2+ (E2/E0/E3). **Orientation matters:** for a *descent* claim we want `Ξ → 0`; for an
  *obstruction/emergence* claim the residual `Ξ ≻ 0` **is** the evidence (digest §5).
- **Computability:** `L₀, D₀, C₀` are finite matrices on the declared toy carrier; `Ξ` is a finite Schur
  complement with a pseudoinverse — pure finite linear algebra, deterministic, replayable.
- **No-over-read coupling:** `Ξ = 0` is necessary but not sufficient for E1; the recovered answer must
  also lie in `target.accepted_observables` (gate E.3).

#### D.1.1 The NORMALIZED Ξ residual (relative residual) — the descent criterion (Pause-2, review fix R-P2)
**The raw Ξ norm is NOT scale-invariant** and may not be compared against an absolute threshold: the
Pause-2 review found a case (the E001 anchor) where the **raw** Ξ *grows* under refinement
(7.84e8 → 2.25e9) while the edge is plainly NOT a clean descent — the raw growth is a *units/normalization*
artifact, not evidence. The descent verdict must therefore be read off the **NORMALIZED (relative)
residual**, not the raw Ξ. Define, on the declared finite toy model at refinement `h`, the **relative
residual**

```
  ξ_rel(h)  :=  ‖ Ξ_C(D|L; h) ‖ / ‖ K_DD(h) ‖           (a dimensionless ratio in [0, 1])
```

i.e. the located obstruction normalized by the total source-readout currency `K_DD` (the part of the
dissolving readout *not* explained by the native probe range, as a fraction of the whole). Equivalently,
in the projection form `Ξ = T_D (I − P_L) T_D*`, `ξ_rel` is the fraction of `T_D`'s energy lying outside
the native range `P_L`. `ξ_rel = 0 ⟺ Ξ = 0` (the exact-adequacy equivalence is preserved), but `ξ_rel`
is **scale-invariant** and is the quantity the descent test reads.

- **CLEAN DESCENT (E1) requires `ξ_rel → ~machine-zero STABLY`:** the normalized residual must fall to
  machine-zero (within the declared numerical tolerance) **and stay there across both declared refinements
  `h₁ ⊏ h₂`** (gate E.9). A small **raw** Ξ is **NOT** sufficient and a large raw Ξ is **NOT**
  disqualifying — only `ξ_rel → ~0` stably seals E1.
- **E0 / E3 (obstruction / gap):** the normalized residual **stays bounded away from zero** under
  refinement (`ξ_rel ⊁ 0`, a stable positive relative residual) — equivalently the obstruction is a
  fixed *fraction* of the source readout, with **analytic control** of that fraction (a known nonzero
  lower bound, not a numerical accident). A stable positive `ξ_rel` is the located obstruction that
  pushes the edge to Step 2+ (E2/E0/E3); it is the **normalized** analogue of `Ξ ≻ 0`.
- **Refinement-stability is on `ξ_rel`, not raw Ξ (gate E.9 binding):** the verdict that may flip
  tier-fragile is the **`ξ_rel → ~0` vs `ξ_rel` stable-positive** verdict, evaluated at `h₁` and `h₂`.
  **Report BOTH the raw Ξ and the normalized `ξ_rel` at each refinement** in the edge log; the **descent
  verdict is taken from `ξ_rel`**, never from raw Ξ alone.

> **Worked example — E001 (QCD → hadron-spectrum, the E0 anchor): STABLE POSITIVE NORMALIZED RESIDUAL +
> ANALYTIC CONTROL.** The raw Ξ *grows* (7.84e8 → 2.25e9) under refinement, but the **normalized**
> residual *shrinks toward a stable positive floor* (`ξ_rel`: 0.197 → 0.042) and **stays positive** — it
> does NOT go to machine-zero. The E0/E3 signal is exactly this: a **stable positive normalized residual
> with analytic control**, NOT monotone raw growth. (The proton mass is run-only — no `D₀ = A·L₀` shortcut
> exists; the positive `ξ_rel` floor is the blind-spot currency of the missing run.) This is why E001 seals
> **E0** (its modality is emergence; see §C.4), not a clean descent.

> **Worked example — E005 (GR → black-hole-thermodynamics): NUMERIC Ξ SMALL IS AN OVER-READ.** Classical
> GR's toy-model Ξ comes out *numerically small* (`ξ_rel ≈ 0` on a GR-only probe family) — but this is an
> **OVER-READ (gate E.3 fail), NOT a clean descent.** The `ħ`-coefficients and the thermal reinterpretation
> (temperature `T = κ/2π`, entropy `S = A/4`) are **NOT in GR's `Σ_f`**: a GR-only probe family literally
> cannot express the thermal predicates, so its small Ξ certifies adequacy *only for the non-thermal
> content* and silently drops the imported `ħ`/thermal predicates. Once the thermal observables are
> included in the readout map (D.4.v) the descent **over-reads its source** (E.3) and is blocked; the edge
> then lands **E2** via the named import. The lesson: **a small numeric Ξ when `ħ`/thermal predicates are
> imported is an OVER-READ, not an E1** — read the normalized residual *against the full target readout map
> including the imported predicates*, and apply gate E.3.

### D.2 Route-mismatch `RM` — the holonomy / protocol diagnostic
On the toy model, take two admissible closure/evolution routes `R₁, R₂` from the same staged start to
the same staged end (e.g. coarse-grain-then-evolve vs evolve-then-coarse-grain). Define
```
  RM(R₁, R₂; h) = ‖ Π_{R₁}(h) − Π_{R₂}(h) ‖    (a nonnegative defect, finite matrices at stage h).
```
- `RM → 0` as the refinement parameter `h ↓ 0` ⇒ the routes agree in the limit ⇒ **no holonomy** (the
  relation is route-independent; descent-style). `RM ↛ 0` (bounded below under refinement) ⇒ **holonomy
  / anti-localization** (B.6): the content depends on the route and cannot be localized to an endpoint.
- **Not a directionality certificate** (digest §3): `RM` records *feasibility / route-agreement under
  refinement*, not a time-arrow. Computed only on the declared finite toy model.

### D.3 Idempotence defect `ID` — the packaging / closure diagnostic
For the packaging endomap `E` (often idempotent) on the toy carrier, define
```
  ID(E; h) = ‖ E²(·) − E(·) ‖   on the staged carrier at refinement h.
```
- `ID → 0` under refinement ⇒ `E` **saturates** (a fixed-package closure; one step then no growth,
  digest §5) ⇒ the layer is closed and *iteration yields nothing new* (primer §4). A genuine new layer
  is reached only by a **package change** (`E ≠ E′`), never by driving `ID` further down.
- Use: `ID ≈ 0` on both endpoints confirms both cards are lawful layers (the `lawful_layer_note`); a
  persistent `ID ↛ 0` means the candidate is **not a closed layer** and should not get a card. It also
  guards against faking emergence by mere iteration: if a claimed "emergent" readout is reachable by
  iterating `E` (`ID → 0` regime), it is **not** emergence (§E.8).

### D.4 The declared finite toy model `M` (the object all diagnostics run on)
A toy model is the minimal finite stand-in for the theory-pair on which Ξ/RM/ID are computable. It
must declare, **before computation** (gate E.1): (i) the finite carrier (dimensions of `Z` at the
chosen stage); (ii) the finite `L₀` (target probe family) and `D₀` (source probe family) as explicit
matrices or an explicit generating rule; (iii) the PSD audit energy `C₀`; (iv) the refinement chain
`h ↓ 0` (a finite ladder of stages) used for `RM`/`ID`; (v) the map from toy-model readouts to the
real layers' `accepted_observables` (so over-reading is checkable). `M` is hashed at declaration; its
hash is logged with the tier. **A tier computed on an undeclared or post-hoc-edited `M` is void**
(gate E.1).

---

## E. The No-Smuggling Gates (the firewall proper)

Each gate is a binary pass/fail logged with the edge. A gate failure **blocks the seal** at the
attempted tier and forces a fallback per the gate. These are adapted from the Erdős no-smuggling /
anti-tautology discipline (digest §4 field 6; §6 smuggle-audit).

- **E.0 — Casting-not-tuned-to-outcome (and the named source is frozen).** A card's `Z/f/Σ_f/E` may
  **not** be chosen to make a downstream edge hit a desired tier. *Test:* the `casting_justification`
  must cite a standard physics coarse-graining/limit that exists *independently* of this atlas; and the
  `casting_alternatives` field must list a competing standard casting. If swapping to the alternative
  flips a tier, the edge is **tier-fragile** (E.6) and the **conservative** tier is recorded.
  **Frozen-named-import clause (review fix #3):** for any E2 edge, the `named_import` is **frozen at
  declaration and may NOT be substituted at typing time** to make the casting land a desired tier — in
  particular the E2 calibration control **E005** has the single frozen import named in §F. *Fail* ⇒
  card/edge rejected, re-cast.
  **Secondary-flag import-hygiene parallel (Pause-2, review fix R-P2):** the frozen-named-import clause
  applies **in parallel** to any E2 edge carrying a SECONDARY `recognition-conditional` flag (§B.7a),
  even though its PRIMARY modality is structural (not `recognition-landing`). Such an edge MUST freeze a
  **single** `named_import` principle (no menu), frozen at declaration and not substituted at typing
  time — the same hygiene the C11 check (`CONTRACT.json`) enforces for primary `recognition-landing`
  rows, here enforced by the new parallel check **C13**. For **E005** this is the QFT-in-curved-spacetime
  (Hawking thermal flux) + first-law-of-BH-mechanics import (semiclassical no-back-reaction; = E034),
  frozen and non-substitutable. *Fail* (an E2 edge with a `recognition-conditional` flag and a missing /
  multiple / menu-style `named_import`) ⇒ edge rejected.

- **E.1 — Toy-model-declared-before-computation.** `M` (§D.4) is declared and hashed **before** any
  Ξ/RM/ID is computed. No editing `M` after seeing a residual. *Fail* (post-hoc or undeclared `M`) ⇒
  the tier is **void**; re-declare and recompute.

- **E.2 — Modality-test-actually-passed.** The assigned modality's operational test (§B) must have
  actually returned PASS on `M`, logged. A modality assigned by *physics intuition* without its test is
  **provisional only** and may not seal a tier. *Fail* ⇒ demote to "untyped modality," edge un-sealed.

- **E.3 — No-over-read (descent must not over-read its source).** A descent's recovered answer must lie
  in `target.accepted_observables`; it may **not** claim a source-only observable as descended. *Test:*
  the toy-readout map (D.4.v) lands inside the target's accepted set. *Fail* ⇒ E1 blocked; the
  over-read part is the *located obstruction* and the edge proceeds to Step 2 (E2/E0/E3).
  **Value-split hook (review fix #8(i), generalized by review fix R5):** when an edge's *form* and its
  *value/numbers* (or its *theorem-status* and its *run-exhibited phenomenon*) close at **different
  tiers**, the edge MUST carry a structured `value_split:{form_tier, value_tier, split_type, value_node}`.
  The schema is **generalized** so the two tiers need not be the E1/E0 pair: `form_tier` and `value_tier`
  may each be any of {E1, E2, E0, E3}, and a required **`split_type`** enum names which kind of split it
  is:
  - **`form_value`** — the *form* of a relation descends (or lands) at `form_tier` (typically E1) while
    its *numerical values* are run-only (`value_tier` E0). (Rows: E004 form E1 /
    transport-coeff values E0; E008 form E1 / matched-coupling values E0;
    E035a form E1 / spectrum values E0; E038 form E1 / exponent values E0.)
  - **`form_value_imported`** — a sub-case of `form_value` where the *geometry/form* descends (E1) but the
    *predictive content* is an imported named external principle (`value_tier` E2). **The canonical R3
    single-semantics row is E029** (ChPT): the chiral symmetry skeleton descends from QCD (`form_tier` **E1**,
    recorded but NOT counted in the E1 null) while the predictive LECs (f_π, the chiral condensate) are the
    **imported** run-generated low-energy constants from lattice QCD (`value_tier` **E2**), so
    reported_tier = value_tier = edge_scored_tier = **E2** (the strong headline invariant, no nuance
    exception). The old single **E028** `form_value_imported` value-split row was separately **superseded
    (review fix O1)** by the two-row E028 split — **E028a** (`general_relativity → lambda_cdm`, shadow-down,
    **E1**, the bare FLRW geometry/form) and **E028b** (`general_relativity → lambda_cdm`,
    recognition-landing, **E2**, the imported Λ/dark-matter/measure content) — carried on **separate ledgers
    and never summed**.
  - **`theorem_run`** — the analytic **open-theorem** status is `form_tier` E3 (no proof; an open named
    external problem) while the **run-exhibited phenomenon** is `value_tier` E0 (a substrate run exhibits
    it). (Row: E041 — Yang-Mills mass-gap / confinement *proof* E3 vs lattice-*exhibited* string tension
    E0.)
  **The reported (headline) tier is SPLIT-TYPE-DEPENDENT (review fix R3 — `CONTRACT.value_split_schema.reported_tier_rule`):**
  - for `split_type` ∈ {`form_value`, `form_value_imported`} the **reported leg is the `value_tier`** —
    the edge's PRIMARY claim is the predictive inter-layer connection, which is incomplete without the
    imported / run-generated value (a symmetry skeleton without its run-generated constants is not
    predictive). **Consequence: E029 (ChPT, `form_value_imported`) reports E2** — reported_tier =
    value_tier = edge_scored_tier = **E2** (recognition-conditional on the imported run-generated LECs); the
    form-descends-**E1** leg is **recorded but NOT counted in the E1 null**, and the two legs are never
    summed. (The `form_value` rows E004/E008/E035a/E038 differ: their edge's own closure IS the
    EQUATION/STRUCTURE descent, so their edge-level **E1** descent is the scored tier while their **E0**
    run-only value-legs sit on the Run-Target ledger, never summed into the E1 count.)
  - for `split_type` == `theorem_run` the **reported leg is the `form_tier`** — the primary claim is the
    analytic theorem; the run-exhibited leg is a separate, never-summed **E0** ledger entry. **Consequence:
    E041 (confinement) STAYS E3** (the open Yang-Mills mass-gap proof, Clay Millennium); the
    lattice-run-exhibited string tension is the E0 ledger leg, carried separately, never summed.

  **A row's headline (scored) tier MUST EQUAL `value_split.reported_tier`** (the leg selected by the
  split-type rule above). This is enforced at freeze (**validator check C10**): a row may **not** silently
  report a *non-reported* `value_split` leg as its closure — in particular **E029 may not be counted as an
  E1** (its form-descent E1 leg is not the edge's closure) and **E041 may not be counted as an E0** (its
  run-exhibited E0 leg is not the edge's headline). The non-reported leg is carried separately (Run-Target
  Manifest when E0, conditional ledger when E2) and is **NEVER summed** with the reported leg (the
  no-summing rule applied *within a single edge*). (Edge rows carrying a `value_split`: **E004, E008, E029,
  E035a, E038, E041** — note: **no current E028 value-split row**; E028 is the two-row E028a/E028b split.)

- **E.4 — Relabeling-is-not-a-connection (anti-tautology / smuggle-audit).** A mere change of notation,
  a definitional restatement, or asserting `A = B` because their symbols match is **NOT** an edge. *Test
  for duality (B.3):* the dictionary must be invertible **both ways** with **content matching**
  (observables map to observables, not names to names); for *any* edge: removing the relabeling must
  leave a residual relation (if deleting the renaming makes the "connection" vanish, it was a relabel).
  *Fail* ⇒ edge rejected (not an inter-layer relation; this is the primer §9.1 / §9.4 trap).

- **E.5 — Conservative-default-on-doubt (THE single ordering; review fix #4).** There is exactly ONE
  conservatism/informativeness order, and it lives here:
  **E1 (most-flattering) > E2 > E0 > E3 (least-flattering).** **E3 is the unique conservative
  terminal.** "Conservative" = retreat *toward E3*. The §C.5 fall-through is **monotone in this order**:
  doubt at Step 1 ⇒ NOT E1, fall through; doubt at Step 2 ⇒ NOT E2, fall through; doubt at Step 3 ⇒ NOT
  E0, **land E3**. **Doubt never promotes; it always demotes strictly toward E3.**
  - **E0 is NOT a safe haven for a doubtful edge.** Sealing E0 requires the *positive* construction of a
    constructible non-descending run-object (Step 3 + gate E.7), never a fallback. A run-only-*looking*
    edge that cannot positively construct that object lands **E3**, not E0. (This closes the review's
    exploit: a doubtful edge could otherwise be routed to E0 — flattering, "real emergence, deferred" —
    or to E3 — unflattering — at the modeler's discretion. It can only go to E3.)
  - Ambiguity that triggers this gate includes: Ξ numerically near but not provably zero; a verdict that
    flips between refinements (E.9); a "principle" not clearly named/citable; a run-object not clearly
    constructible; a casting whose standard alternative flips the tier (E.6).

- **E.6 — Tier-fragility flag.** If any *standard alternative casting* (E.0 / card
  `casting_alternatives`) would change the tier, the edge is **tier-fragile**: record **both** tiers,
  seal the **conservative** one (E.5), and flag for the reviewer. A fragile edge may not be reported as
  "decisive" without the conditional rider (§G).

- **E.7 — E0-double-run requirement (the hard interlock; anti-control clause added by O4, machine-enforced
  by R5).** An edge may be sealed **E0 only after BOTH** the descent-test (Step 1) **and** the
  recognition-search (Step 2) have **actually been executed and logged** with their negative results. An E0
  seal lacking *either* logged negative is **void** — you may not "jump to E0" because the edge *feels*
  run-only. (Mirrors digest §6: foreclosure must be demonstrated, not assumed.) **Anti-control E0 clause
  (O4):** an `is_calibration` E3 anti-control may satisfy its `must_not_seal_E1_or_E2` rule *via* E0 **only
  if** its `run_target_stub` was **frozen before scoring** and this E.7 double-run interlock is logged;
  otherwise the E0 is demoted to E3 (§E.5) and the anti-control passes only as E3. This stops E0 from
  becoming a flattering "real emergence, deferred" haven for an edge that should foreclose to E3.
  **Machine fields (review fix R5 — `CONTRACT.anti_control_rules.e7_interlock_schema`; closes the
  reviewer's mutation test 2).** An anti-control edge sealed at `scored_tier` E0 must carry **all four
  booleans**, all present and **true**:
  - **`descent_test_logged_negative`** — the Step-1 descent-test ran and logged a negative (Ξ ≠ 0 stably);
  - **`recognition_search_logged_negative`** — the Step-2 recognition-search ran and logged *no* named principle;
  - **`non_descending_run_object_exhibited`** — a constructible non-descending run-object (B.2) was *positively* exhibited (E0 is not a doubt-haven);
  - **`run_target_stub_frozen_pre_scoring`** — the (non-empty) `run_target_stub` was frozen *before* the scored run.

  **Rule (enforced at freeze, hardened validator check C5):** **an anti-control edge may carry
  `scored_tier == "E0"` only if ALL FOUR booleans are present and true** (and a non-empty `run_target_stub`
  is present). If any is absent or false, the bare E0 is a conservative-default failure and the edge is
  **demoted to E3** (§E.5); it does **not** pass on the strength of an E0 label. The four current
  anti-controls **E018/E019/E020/E021** are all expected at **E3**; none carries an E0 seal at this freeze.

- **E.8 — Anti-emergence-derivation (the up/down firewall).** No edge may be sealed **E1 via an
  UP-direction computation**, and no claimed "emergence" may be sealed that is actually reachable by
  iterating `E` (the `ID → 0` regime, D.3) — that is iteration, not a package change (primer §4).
  *Test:* an E1 seal must be a DOWN descent (Ξ on `D|L` with source=higher); an emergence claim must
  exhibit non-factorization (B.2) that survives iteration. *Fail* ⇒ reject the claim; emergence is
  certified as a gap (E0/E3), never derived. **Also enforced via the §B.8 modality↔tier table:** a
  `shadow-down E0` or `emergence-up E1` row is rejected at freeze.

- **E.9 — Refinement-stability (review fix #5(i); the `M`-tuning fence).** An edge's descent verdict —
  **the NORMALIZED residual `ξ_rel → ~machine-zero` vs `ξ_rel` stable-positive** (§D.1.1; **NOT** the raw
  `Ξ` norm, which is not scale-invariant — Pause-2 review fix R-P2) — must be **stable across at least two
  declared finite refinements `h₁ ⊏ h₂`** of `M` (a coarser and a finer finite stage), with the **same
  qualitative verdict at both**. A verdict that **flips** between refinements is **tier-fragile** (E.6)
  and seals at the conservative terminal **E3** (E.5). *Why in scope:* two finite refinements is still
  **finite linear algebra**, NOT an irreducible run — it does not cross the hard-scope boundary.
  *Purpose:* a single hand-picked finite stage can no longer fix the answer; the `M`-choice tunability
  surface drafter 2 flagged (§H) is fenced. **Note:** the raw `Ξ` may legitimately *grow* under
  refinement while the edge is foreclosed (the E001 anchor: raw Ξ 7.84e8→2.25e9, `ξ_rel` 0.197→0.042,
  stable-positive) — so the stability check is on `ξ_rel`, and **both** raw Ξ and `ξ_rel` are logged at
  each refinement.

- **E.10 — Second-annotator `M`-faithfulness (review fix #5(ii); the Erdős two-annotator rule, ported).**
  `M`'s full declaration — carrier, `L₀,D₀,C₀`, and the toy→`accepted_observables` readout map (D.4.v) —
  must be **certified faithful by a second independent annotator BEFORE the hash**, on the standard
  *"this is a minimal faithful finite stand-in for the theory-pair, not reverse-engineered from a desired
  Ξ."* **Both annotators are logged with the edge.** *Fail* (no second annotator, or it certifies the `M`
  as reverse-engineered) ⇒ `M` rejected; re-declare. **No-faithful-`M` corollary (review fix #5(iii)):**
  if no honest finite `M` exists for the pair (candidate: QM↔GR), the descent-test is **vacuous** and the
  edge seals **E3 by the distinct sub-reason `e3_subreason: no_faithful_M`** — recorded separately from a
  *run-and-failed* descent E3, so the reader can see the descent-test was **never constructible**, not
  *built and failed*. This prevents the rubric over-producing undifferentiated E3 verdicts.

- **E.11 — Near-intra-layer check (review fix #8(ii), machine-enforced by R4; the primer §3 / §9 guard).**
  An edge whose "descent" is a *restriction to a tensor factor of the SAME theory* (e.g. SM → its
  SU(2)×U(1) or SU(3) factor) must pass the **E.4 relabeling test explicitly, with the result recorded**.
  If restricting to the factor is a **genuine quotient with its own `Σ_f`** (and own
  `accepted_observables`), keep E1 and *say why it is not intra-layer*. If it is a **within-layer
  restriction** (deleting the renaming leaves no residual relation), mark it `within-a-layer, no SBT
  content` (§9) and **REMOVE it from the E1 count** — a trivial factorization may not pad the
  shadow-heavy distribution (flattering-by-padding). (Rows under this gate: **E016, E017**; also flagged
  near-intra-layer: **E039**.)
  **Machine fields (review fix R4 — `CONTRACT.near_intra_layer_schema`; closes the reviewer's mutation
  test 1).** Each near-intra-layer edge carries two machine-checkable fields the validator reads (the
  legacy free-text `PENDING_E4: …` string is superseded by these and kept only as a human note):
  - **`near_intra_layer_check: true`** — flags the edge as subject to this gate.
  - **`near_intra_layer_result ∈ {pending, passed, failed}`** — `pending` = E.4 not yet run/recorded;
    `passed` = E.4 confirmed a genuine inter-layer quotient (own `Σ_f`/`accepted_observables`; removing
    the renaming leaves a residual relation); `failed` = within-layer restriction (no residual relation).

  **Rule (enforced at freeze, validator check C9):** **`scored_tier` E1 is FORBIDDEN for a
  `near_intra_layer_check:true` edge unless `near_intra_layer_result == "passed"`.** A `pending` result
  ⇒ the edge may be carried only as **E1-pending**, never counted as a sealed E1. **A failed gate-E.4
  (`near_intra_layer_result == "failed"`) ⇒ the edge is REMOVED from the E1 count and marked
  `within-a-layer, no SBT content`.** At this freeze **E016, E017, E039** all carry
  `near_intra_layer_check:true, near_intra_layer_result:"pending"` and none may count as a sealed E1.

- **E.12 — Full closure-package card freeze BEFORE any `M` declaration or Ξ computation (HARD GATE;
  review fix R1).** The single most dangerous remaining elasticity is that the manifests currently hold
  only `provisional_Z/f/E` **stubs**, not full §A cards — leaving a modeler free to tune a card's
  `Z/f/Σ_f/E/accepted_observables/casting_*` *after* seeing an edge's `M` or `Ξ`, which would let the
  casting be steered to a flattering tier. This gate forbids that ordering absolutely:
  > **No `M` may be declared (gate E.1) and no `Ξ`/`RM`/`ID` may be computed for ANY edge until the FULL
  > closure-package card (every §A field: `Z, f, Σ_f, E, D, accepted_observables, lawful_layer_note,
  > casting_justification, casting_alternatives, status`) is frozen and hashed for EVERY theory id AND for
  > EVERY node that bears a casting (every endpoint that contributes a `Z/f/Σ_f` to any incident edge).**
  The full-card freeze is recorded in a hashed `closure_card_manifest.jsonl` (the long form of the
  `theory_manifest.jsonl` stubs) and added to `SHA256SUMS`; the freeze validator asserts **(a)** every
  theory id and every casting-bearing node has a complete frozen card, and **(b)** the card hash predates
  the first `M` hash and the first `Ξ` computation for every incident edge. *Fail* (any `M`/`Ξ` whose
  incident cards were not all frozen-first, or any stub-only casting at scoring time) ⇒ the affected
  edges' tiers are **void**; freeze **BLOCKED** until the full cards are frozen and the edges recomputed
  against them. This converts the "declarative firewall" the external reviewer flagged into an
  ordering-enforced one: **cards first, always, before any number.**

- **E.13 — Registered-null E1 honesty caveat (review fix O2).** The pre-audit registered-null E1 count
  (**19**, per `CONTRACT.json` `registered_null.per_tier.E1` — the single source of truth) INCLUDES the 3
  near-intra-layer candidates still PENDING the gate E.4 / E.11 relabeling test (E016, E017, E039), carried
  as E1-pending (sealed-E1-eligible = 16). Any reported E1 count — pre- or post-audit — MUST carry the
  caveat: **"the audited E1 set
  must REMOVE any near-intra-layer candidate that fails gate E.4 (within-a-layer restriction, no residual
  relation)."** An E1 total quoted *without* this caveat, or one that silently keeps an E.4-failing
  near-intra-layer row, is a **flattering-by-padding** violation and is rejected. The caveat is recorded
  in `FREEZE_NOTES.md` (registered-null section) and carried as a machine-readable flag on the pending
  rows; the freeze validator checks that no edge with an unresolved `near_intra_layer_check` is counted as
  a *sealed* E1 (it may be carried as `E1-pending`, never as a clean E1) — see `CONTRACT.json`
  `full_card_freeze_rule` and the registered-null caveat.

---

## F. The Calibration Protocol (the freeze-blocker; Erdős APN-9 rule)

Before the scored run may be **frozen**, the rubric is run on a fixed set of **known-answer calibration
edges** (flagged `is_calibration=true` in `edge_manifest.jsonl`). The atlas freezes **only if every
calibration edge comes out at its known tier.** A calibration FAIL **blocks the freeze** (it is the
APN-9 freeze-blocker): a rubric that cannot reproduce the textbook answers on the controls is not
trustworthy on the unknowns.

**The required calibration set and their known answers.** Every calibration row carries a
**machine-checkable** `calibration_known_tier` (and the anti-controls a `calibration_rule`), so the
freeze gate compares **computed-tier to known-tier programmatically**, not by reading prose (review fix
#7). There are **9 calibration edges**: 5 known-tier controls + 4 E3 anti-controls.

*Known-tier controls (computed tier must EQUAL `calibration_known_tier`):*

| id | Calibration edge | Known modality | `calibration_known_tier` | Spec the rubric must reproduce |
|---|---|---|---|---|
| **E001** | QCD → hadron-spectrum (proton mass) | Emergence (B.2) | **E0** | Must match **physical-quark-mass lattice QCD** (gauge-field path integral on a finite grid): **no free proton/hadron MASS parameter**; the quark masses and the coupling/scale are **fixed independently under the declared lattice-QCD protocol** (scale set by **one hadronic input**, running generated by **dimensional transmutation**); the **proton-mass / hadron-spectrum readout is out-of-sample and NOT fitted** — it is the readout of an irreducible run (primer §5, §8). Deferred to Run-Target Manifest; **NOT run, NOT derived**. This is THE anchor. |
| **E002** | Statistical mechanics → thermodynamics | Descent (B.1) | **E1** | Ξ = 0 on the declared ensemble→macrostate toy model; entropy/pressure descend; runnable; refinement-stable (E.9). |
| **E003** | Special relativity → classical mechanics | Descent (B.1) | **E1** | Ξ = 0 in the `v/c → 0` toy limit (Wigner–İnönü); a clean computable limit-descent. |
| **E004** | Kinetic theory → hydrodynamics | Descent (B.1) | **E1** | Ξ = 0 on the Chapman–Enskog gradient-expansion toy model (Knudsen → 0), for the EQUATIONS; transport-coefficient VALUES carried as a `value_split` E0 sub-target, never summed. |
| **E005** | **PRIMARY: Currency / shadow-price (B.5)**; SECONDARY flag: `recognition-conditional` (§B.7a) | **E2** | Lands **conditional** on the **single frozen named import = QFT in curved spacetime (Hawking thermal flux) + the first law of BH mechanics** (semiclassical no-back-reaction; = the E034 construction). Must come out **E2-conditional**, NOT E1 and NOT a derivation. **`primary_modality = currency-shadow-price`** (the structural test passes — the §B.5 "surface gravity as the price in BH thermodynamics" exemplar — so the structural modality is PRIMARY, §B.7a precedence rule, NOT a primary `recognition-landing`); `conditionality_flags = ["recognition-conditional"]` as a SECONDARY flag because classical GR's Ξ≈0 is an over-read (the ħ/thermal predicates are imported). The named import is **frozen, not chosen at typing time** (E.0 + secondary-flag import-hygiene parallel); **Jacobson is NOT this edge** (that is E022, the opposite arrow, a *primary* `recognition-landing`). *(Review fix #3 + Pause-2 R-P2.)* |

*E3 anti-controls (computed tier must satisfy `calibration_rule:"must_not_seal_E1_or_E2"`, i.e. land in
{E3, E0} — these test that SBT does NOT secretly derive structure; review fix #7):*

| id | Anti-control edge | `calibration_known_tier` | `calibration_rule` | What an E1/E2 here would mean |
|---|---|---|---|---|
| **E018** | QM ↔ GR (quantum gravity) | **E3** | `must_not_seal_E1_or_E2` | someone "unified by deriving both from shared math" (primer trap #1) |
| **E019** | SM → gauge-group-origin | **E3** | `must_not_seal_E1_or_E2` | someone "derived" SU(3)×SU(2)×U(1) — smuggling |
| **E020** | SM → fermion-generations | **E3** | `must_not_seal_E1_or_E2` | someone "derived" the generation count / mass hierarchy — smuggling |
| **E021** | GR → cosmological-constant | **E3** | `must_not_seal_E1_or_E2` | someone "predicted" Λ — tuning (retro R025 is synthetic) |

> **The {E3, E0} anti-control rule, TIGHTENED (review fix O4).** An anti-control is satisfied when its
> computed tier lands in {E3, E0} — but **E0 is not a free pass**. Without a fence, a modeler could route
> an anti-control to E0 ("real emergence, deferred") to dodge the unflattering E3 while still passing the
> gate — making E0 a flattering haven. So: **an anti-control passes via E0 ONLY IF its run-target stub was
> frozen BEFORE scoring AND the E0 seal satisfies gate E.7** (both the descent-test and the
> recognition-search logged negative, plus a constructible non-descending run-object positively exhibited
> per §E.7 / §E.5). Concretely, the freeze validator requires, for any anti-control with computed tier
> E0: (i) a non-empty `run_target_stub` present at freeze-time (frozen before the scored run, not added
> post-hoc), and (ii) the E.7 double-run interlock logged. An anti-control that "lands E0" **without** a
> pre-frozen run-target stub satisfying E.7 is treated as a **conservative-default failure** and demoted
> to E3 (§E.5); it does **not** pass on the strength of a bare E0 label. (The four current anti-controls
> E018/E019/E020/E021 are all expected at E3, not E0; this rule fences the E0 escape hatch for any future
> anti-control or any re-typing of these.)

**The freeze-gate predicate (wired; review fix #7, tightened by O4):**

> **FREEZE iff** *(a)* every `is_calibration` row with a `must_seal_*` rule has **computed tier ==
> `calibration_known_tier`**, **AND** *(b)* every E3 anti-control (`must_not_seal_E1_or_E2`) has
> **computed tier ∈ {E3, E0}, and any anti-control computed E0 carries a pre-frozen `run_target_stub`
> AND a logged E.7 double-run interlock (review fix O4)** — else it is demoted to E3, **AND** *(c)* every
> edge endpoint resolves (A.7), every `(modality,tier)` pair is emittable (B.8), every modality string is
> canonical (§B / R2), and every E1 sourced from a `candidate_substructure` has that node
> `experimentally_established` (§A.7.1 / R6). The workflow's **Assemble phase must enforce this
> programmatically** (compare the machine-checkable fields against `CONTRACT.json`; do not read prose). An
> un-wired freeze-blocker is decorative.

**Calibration verdicts and the freeze gate:**
- **PASS** = the freeze-gate predicate holds (the 5 known-tier controls match; the 4 E3 anti-controls
  stay in {E3, E0}). ⇒ the scored run may be frozen.
- **FAIL** = any known-tier control lands at the wrong tier (e.g. the proton mass comes out E1
  "derived", or an E1 control comes out E2), **or** any E3 anti-control seals E1/E2. ⇒ **FREEZE
  BLOCKED.** Diagnose: a wrong-tier proton mass means a
  reductionist relapse (someone tried to derive a run-only constant) — the most serious failure; a
  control flip means the toy model or the casting is mis-specified. Fix and re-run calibration before
  any scoring is reported.
- **Calibration is run with the SAME frozen rubric, cards, and decision-procedure as the unknown
  edges** — no special-casing the controls (else the calibration is itself smuggled).

---

## G. Non-Claims and Banned Language (binding)

**Non-claims (binding, primer §10; digest §9):**
- **No derivation across a layer boundary.** The atlas never derives/reduces/factors one lawful theory
  into another. Edges are *typed and audited*, never *reduced*.
- **No empirical claim.** Every Ξ/RM/ID is a statement about a **declared finite toy model**, on the
  closure-algebraic side; the bridge to a measured observable is a *separate, un-realized* assertion.
  A toy-model E1 is **not** a physical prediction.
- **No constant is derived.** E0 edges are *deferred*, never executed; the atlas specs the run, it does
  not run it and does not report a number.
- **Conditional results are reported separately.** E2 (recognition-conditional) edges are labeled
  "conditional under the named principle" and are **NEVER summed with E1** (accepted descent). E0 edges
  are **never summed with E1** either. The four tiers are kept on separate ledgers.
- **Using the map is not asserting the territory.** Casting physics through SBT does not presuppose SBT
  is "true"; it is an organizing instrument judged by what it usefully charts and audits.
- **Within-a-layer silence.** Where an "edge" is actually intra-layer, the rubric declares itself silent
  ("textbook in costume") rather than manufacturing content (primer §3).

**Banned language (a use of any banned term blocks the seal until rephrased):**
- **"derive / derivation / reduce / reduces to / factor through"** applied to an **UP/emergence** edge
  or any **E0** edge. (Down-descent edges may say "descends to / is computable from / coarse-grains to";
  never "the higher reduces to the lower.")
- **"solved / solves / closed / proven"** for any **E2 / E3 / E0** edge. (E2 = "lands conditional on
  <named principle>"; E3 = "sharpened gap / located open problem / bounded no-go"; E0 = "run-only,
  deferred / spec'd, not run".) Only an **E1** edge may be called a "computable descent," and even then
  not "solved."
- **"decisive / conclusive"** *unqualified*. Any use of "decisive" must carry the rider **"conditional
  on the audited casting; licensed by the proton-mass calibration"** — and may not be applied to a
  tier-fragile edge (E.6) at all.
- **"unify / unifies"** meaning *factorization* (primer §9.1). Unification is **only** F51
  common-refinement (a join, B.4) or F41 duality (B.3); never "A reduces to B."
- **"emergent constant we computed / our derivation of the scale"** — emergence has no shortcut; banned
  outright (primer §5).
- Summing tiers in any total, table, or score that places **E1 alongside E2/E0/E3** as if commensurable.
  Counts are reported **per tier**, never pooled.

---

## H. Key design decisions and the toy-model-adequacy tension (RESOLVED by the Layer-A fixes)

**Key design decisions:**
1. **Modality ⟂ tier.** I separated *what kind of relation* (modality, §B) from *its closure status*
   (tier, §C). This prevents conflating "it's a duality" (a structural claim) with "it's E1" (a
   computability verdict), and lets the firewall gate them independently.
2. **The decision-procedure runs ONLY the down arrow as a computation** (§C.6, gate E.8). The up arrow
   is never executed; emergence is certified as a *gap* (non-factorization), enforcing primer §6's
   asymmetry as code, not custom.
3. **Ξ is the single, finite, deterministic descent oracle** (§D.1), with the exact block-currency
   definitions and the `Ξ = 0 ⟺ kernel-containment ⟺ factorization` equivalence taken verbatim from the
   adequacy paper — so "computable descent" has one precise meaning, on a declared finite toy model only.
4. **Conservative-default is downward** (E.5): doubt always demotes toward E3 (least flattering), never
   promotes toward E1. Combined with the E0-double-run interlock (E.7), this makes flattering tiers
   *expensive* and unflattering ones *cheap* — the firewall's intended bias.
5. **Calibration is a hard freeze-blocker** (§F) run with the *same* frozen rubric as the unknowns, with
   the proton mass as the immovable E0 anchor; a wrong-tier proton mass is defined as the worst failure
   (a reductionist relapse) and blocks the freeze.
6. **The E0/E3 split rule** (§C.7) is stated explicitly because it is the most likely place to either
   smuggle fake E0 edges (every SM input parameter) or to mislabel a genuine run-only scale as a
   sharpened gap.

**The toy-model adequacy problem — drafter 2 flagged it; Layer-A HARDENED it (review fix #5).**
The whole firewall rests on Ξ computed on a *declared finite toy model* `M`, and the *choice of `M`*
(carrier, probe families `L₀, D₀`, audit energy `C₀`) is itself a modeling act that could drive Ξ→0
(force E1) or Ξ≻0 (force E3) — the elasticity the firewall must kill, one level down. The draft fenced
this only with E.1 (declare+hash before computing) and E.0 (casting tied to standard physics), which a
*hand-picked-then-hashed* `M` defeats. **The Layer-A review converted drafter 2's three open questions
into hard gates — all three are now CLOSED in this frozen rubric:**
- **(i) refinement-stability ⇒ gate E.9.** Ξ's zero/nonzero verdict must be **stable across two declared
  finite refinements `h₁ ⊏ h₂`**; a flip is tier-fragile and seals **E3**. This is still **finite linear
  algebra, not an irreducible run** — so it stays inside hard scope (the worry that motivated leaving it
  out is explicitly answered: two finite stages ≠ a run).
- **(ii) second-annotator faithfulness ⇒ gate E.10.** `M`'s declaration must be certified a *minimal
  faithful finite stand-in, not reverse-engineered from a desired Ξ* by a **second independent annotator
  before the hash**; both annotators are logged.
- **(iii) no-faithful-`M` ⇒ the `e3_subreason: no_faithful_M` route (E.10 corollary, §C.5 STEP 0d).** A
  pair with no honest finite `M` (candidate: QM↔GR) has a **vacuous** descent-test and seals **E3 by a
  DISTINCT sub-reason**, recorded separately from a run-and-failed descent E3 — so the reader sees the
  test was *never constructible*, not *built and failed*, and the rubric does **not** over-produce
  undifferentiated E3 verdicts. *(This is the correct behavior the reviewer confirmed: vacuous-test E3 is
  a real, but distinctly-labeled, located gap.)*

This was "the single most important thing to harden, where a determined modeler would attack the
firewall." It is now hardened: a single hand-picked finite stage can no longer fix the answer, and a
"we couldn't even build the test" E3 is no longer hidden among genuine run-and-failed gaps.

---

*This rubric is a faithful operationalization of the frozen bootstrap, not a substitute for it. Where it
and a frozen SBT paper disagree, the paper governs — flag the discrepancy for correction.*
