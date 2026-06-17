# Physics Layer Atlas — The Typing Rubric (Stage 1, drafter 2 of 4)

**Status:** DRAFT for Layer-A adversarial review. This is the *elasticity firewall* of the atlas: the
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
that casting **before** any edge touching it is typed. **Card field schema** (one card per theory; this
is the long form of the `theory_manifest.jsonl` stub fields, which a card must expand and not contradict):

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
(the one yielding the *higher-numbered, less-flattering* tier in the E0 < E3 < E2 < E1 informativeness
order is **not** the rule — see §E.5 for the actual conservative-default rule), and you record the
alternative in `casting_alternatives`.

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

### B.7 Modality precedence + multi-modality flag
If more than one operational test passes, assign in this precedence (most-constraining first) and
**flag the edge as multi-modal** in notes: Duality (B.3) > Common-refinement (B.4) > Holonomy (B.6) >
Currency (B.5) > Descent (B.1) > Emergence (B.2). Rationale: duality/common-refinement are the strongest
structural claims and must be *earned*, so they are tested first and demoted to descent/emergence if
their stricter test fails. **Demotion is one-directional**: you may demote a claimed duality to a mere
descent on test failure; you may **never** promote a descent to a duality to flatter symmetry.

---

## C. The Edge-Tier Definitions (E0/E1/E2/E3) and the deterministic foreclosure decision-procedure

The **edge-tier** is the *closure status* of the edge — orthogonal to the modality. Four tiers, adapted
from the Erdős tier map (`enums.md` §III) to physics edges. **Tiers are NEVER summed** (E1 with E2/E0 is
forbidden, §G).

### C.1 E1 — Computable descent (the runnable shadow)
A **coarse-graining physics already accepts**, checkable *now* on a finite toy model.
- **Sealing condition:** the modality is Descent/Shadow (B.1) **or** a Duality both-ways (B.3), and on
  the **declared finite toy model** the adequacy residual **Ξ = 0** (equivalently kernel-containment
  `ker L₀ ⊆ ker D₀`, equivalently a factorization `D₀ = A·L₀`; §D.1), with **no over-reading** (§E.3).
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
- **Calibration control (must come out E2):** a clean recognition case (e.g. GR ↔ thermodynamics via the
  *named* Jacobson "Einstein equation of state" derivation, or black-hole thermodynamics via the *named*
  Bekenstein–Hawking area law) — landing **conditional on the named principle**, not as a derivation.

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
  **lattice QCD** (gauge-field path integral on a grid; scale set by dimensional transmutation; mass is
  a run readout, no free mass parameter). This is the canonical already-resolved E0 case (§F).

### C.5 THE DETERMINISTIC FORECLOSURE DECISION-PROCEDURE (run in this exact order; log every branch)

```
INPUT: a frozen source card S, a frozen target card T, a declared finite toy model M (declared
       BEFORE any computation — gate E.1), and the edge's assigned modality (§B).

STEP 0  PRECONDITION. Confirm S and T are frozen cards (§A) and M is declared+hashed. If not → HALT,
        edge not typeable yet (do NOT guess a tier).

STEP 1  DESCENT-TEST (down arrow, runnable). On M, build L = native(target) and D = dissolving(source)
        probe families and the audit energy C (§D.4). Compute Ξ_C(D|L) (§D.1).
          • If Ξ = 0 (equiv. ker L₀ ⊆ ker D₀, equiv. D₀ = A·L₀) AND no-over-read (E.3) passes:
                ───────────────────────────────────────────────► SEAL  E1.   STOP.
          • Else (Ξ ≠ 0): record Ξ (the residual is the located obstruction); continue.

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

- **E.0 — Casting-not-tuned-to-outcome.** A card's `Z/f/Σ_f/E` may **not** be chosen to make a
  downstream edge hit a desired tier. *Test:* the `casting_justification` must cite a standard physics
  coarse-graining/limit that exists *independently* of this atlas; and the `casting_alternatives` field
  must list a competing standard casting. If swapping to the alternative flips a tier, the edge is
  **tier-fragile** (E.6) and the **conservative** tier is recorded. *Fail* ⇒ card rejected, re-cast.

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

- **E.4 — Relabeling-is-not-a-connection (anti-tautology / smuggle-audit).** A mere change of notation,
  a definitional restatement, or asserting `A = B` because their symbols match is **NOT** an edge. *Test
  for duality (B.3):* the dictionary must be invertible **both ways** with **content matching**
  (observables map to observables, not names to names); for *any* edge: removing the relabeling must
  leave a residual relation (if deleting the renaming makes the "connection" vanish, it was a relabel).
  *Fail* ⇒ edge rejected (not an inter-layer relation; this is the primer §9.1 / §9.4 trap).

- **E.5 — Conservative-default-on-doubt.** At any branch of §C.5 where the test is *ambiguous* (Ξ
  numerically near but not provably zero; a "principle" that is not clearly named/citable; a run-object
  that is not clearly constructible), take the **more conservative tier**, defined by *informativeness*:
  **E1 is the strongest/most-flattering claim, then E2, then E0, then E3 the weakest.** "Conservative"
  = retreat *toward E3* (the sharpened-gap, least-flattering verdict). Concretely: doubt at Step 1 ⇒ do
  **not** seal E1, fall through to Step 2; doubt at Step 2 ⇒ do **not** seal E2, fall through; doubt at
  Step 3 ⇒ do **not** seal E0, fall to E3. **Doubt never promotes; it always demotes.**

- **E.6 — Tier-fragility flag.** If any *standard alternative casting* (E.0 / card
  `casting_alternatives`) would change the tier, the edge is **tier-fragile**: record **both** tiers,
  seal the **conservative** one (E.5), and flag for the reviewer. A fragile edge may not be reported as
  "decisive" without the conditional rider (§G).

- **E.7 — E0-double-run requirement (the hard interlock).** An edge may be sealed **E0 only after BOTH**
  the descent-test (Step 1) **and** the recognition-search (Step 2) have **actually been executed and
  logged** with their negative results. An E0 seal lacking *either* logged negative is **void** — you
  may not "jump to E0" because the edge *feels* run-only. (Mirrors digest §6: foreclosure must be
  demonstrated, not assumed.)

- **E.8 — Anti-emergence-derivation (the up/down firewall).** No edge may be sealed **E1 via an
  UP-direction computation**, and no claimed "emergence" may be sealed that is actually reachable by
  iterating `E` (the `ID → 0` regime, D.3) — that is iteration, not a package change (primer §4).
  *Test:* an E1 seal must be a DOWN descent (Ξ on `D|L` with source=higher); an emergence claim must
  exhibit non-factorization (B.2) that survives iteration. *Fail* ⇒ reject the claim; emergence is
  certified as a gap (E0/E3), never derived.

---

## F. The Calibration Protocol (the freeze-blocker; Erdős APN-9 rule)

Before the scored run may be **frozen**, the rubric is run on a fixed set of **known-answer calibration
edges** (flagged `is_calibration=true` in `edge_manifest.jsonl`). The atlas freezes **only if every
calibration edge comes out at its known tier.** A calibration FAIL **blocks the freeze** (it is the
APN-9 freeze-blocker): a rubric that cannot reproduce the textbook answers on the controls is not
trustworthy on the unknowns.

**The required calibration set and their known answers:**

| Calibration edge | Known modality | Known tier | Spec the rubric must reproduce |
|---|---|---|---|
| **QCD → hadron masses / proton mass** | Emergence (B.2) | **E0** | Must match **lattice QCD**: gauge-field path integral on a finite grid; **no free mass parameter**; scale set by **dimensional transmutation**; mass is a **run readout**, validated out-of-sample (primer §5, §8). Deferred to Run-Target Manifest; **NOT run, NOT derived**. This is THE anchor. |
| **Statistical mechanics → thermodynamics** | Descent (B.1) | **E1** | Ξ = 0 on the declared ensemble→macrostate toy model; entropy/pressure descend; runnable. |
| **Special relativity → Galilean/Newtonian** | Descent (B.1) | **E1** | Ξ = 0 in the `v/c → 0` toy limit; the limit is a clean, computable descent. |
| **Kinetic theory → hydrodynamics** | Descent (B.1) | **E1** | Ξ = 0 on the Chapman–Enskog gradient-expansion toy model (Knudsen → 0). |
| **A named recognition control (E2)** | Currency/Duality | **E2** | Lands **conditional** on a NAMED principle (e.g. GR↔thermodynamics via *Jacobson's equation of state*, or BH-thermo via the *Bekenstein–Hawking area law*) — must come out E2 *conditional*, **not** E1 and **not** a derivation. |

**Calibration verdicts and the freeze gate:**
- **PASS** = every calibration edge's computed tier equals its known tier (E0 stays E0, the E1 controls
  stay E1, the E2 control lands E2-conditional). ⇒ the scored run may be frozen.
- **FAIL** = any calibration edge lands at the wrong tier (e.g. the proton mass comes out E1 "derived",
  or an E1 control comes out E2). ⇒ **FREEZE BLOCKED.** Diagnose: a wrong-tier proton mass means a
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

## H. Key design decisions (for the reviewer) and the tension I could NOT fully resolve

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

**Tension I could NOT fully resolve (please target this):**
The **toy-model adequacy problem.** The entire firewall rests on Ξ computed on a *declared finite toy
model* `M`. But the *choice of `M`* (which finite carrier, which probe families `L₀, D₀`, which audit
energy `C₀`) is itself a modeling act that could, in principle, be tuned to drive Ξ to 0 (force E1) or
away from 0 (force E3) — re-importing the elasticity the firewall is meant to kill, one level down. I
have partly fenced this with gate E.1 (declare+hash `M` before computing) and gate E.0 (casting tied to
standard physics), and with the calibration controls (if a tuned `M` were possible, the controls should
expose it). But I have **not** given a *constructive adequacy criterion* for "this `M` is a faithful
finite stand-in for the theory-pair, and not a gerrymandered one." Open questions for the reviewer:
(i) Should there be a **mandatory minimal-`M` / refinement-stability requirement** — e.g. Ξ's
zero/nonzero verdict must be *stable across at least two declared refinements* `h₁, h₂` of `M`, so a
single hand-picked finite stage cannot fix the answer? (I lean yes; I did not make it a hard gate
because I'm unsure what minimal refinement depth is fair without sliding toward an irreducible run,
which scope forbids.) (ii) Should `M` declaration require a **second independent annotator** to certify
faithfulness *before* the hash, mirroring the Erdős two-annotator rule? (iii) Is there a residual risk
that a theory-pair has **no honest finite toy model** at all (e.g. QM↔GR), in which case the
descent-test is *vacuously* non-passing and the edge auto-falls to E2/E0/E3 — is that the correct
behavior, or does it over-produce E3 verdicts by construction? I flag this as the single most important
thing for Layer-A to harden, because it is where a determined modeler would attack the firewall.

---

*This rubric is a faithful operationalization of the frozen bootstrap, not a substitute for it. Where it
and a frozen SBT paper disagree, the paper governs — flag the discrepancy for correction.*
