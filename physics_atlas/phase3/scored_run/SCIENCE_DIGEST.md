# Physics Layer Atlas — Science Digest

**Status:** a self-contained working digest of the SBT machinery a drafter / reviewer / assembler
needs for the **Physics Layer Atlas (Stage 1)**, framed throughout with concrete inter-theory physics
examples, so nobody must open the raw `.tex` papers mid-run. It is a **faithful condensation, not a
substitute** for the papers; where this digest and a paper would disagree, **the paper governs** —
flag the discrepancy. Frozen into the bootstrap at pre-registration.

> **Provenance & nonclaims govern this whole file** — see §10. SBT is a meta-mathematical *organizing
> map*, **not** a black-box prover and **not** a physical theory competing inside any layer. We are
> doing **cartography + triage**, calibrated on the proton mass. **HARD SCOPE (never crossed):** no
> computationally-irreducible runs, no empirical predictions, no derivation of any constant. We **map
> and audit** inter-theory relations; we **never** reduce, derive, or factor one lawful theory into
> another across a layer boundary.

> **Orienting fact you must hold the whole way (primer §3).** SBT has distinctive content **only
> between layers**. *Within* a single physics theory — QM solved inside QM, GR solved inside GR — SBT
> is "textbook in costume" and adds only vocabulary; if an analysis keeps concluding "this is just
> ⟨standard limit⟩ relabeled," it was almost certainly posed within a layer. This atlas types **edges
> between** theories. That is the only axis on which the framework is not silent.

---

## 1. Core idea — "a physics is a theory" (the closure package in physics)

To introduce a stable physics layer is to **specify a theory you stage and audit**: pass from a
detailed micro-description to a macro layer that behaves coherently on its own scale, treating the
discarded high-frequency degrees of freedom as completed by a canonical rule. This is the **closure
move** (To Become a Stone — A Physics is A Theory; To Spend a Stone §2). A **physics theory package**
is a tuple

> **T = (Z, f, Σ_f, E, D).**

- **Z** — the **carrier**: the micro state space of the finer description. *Physics examples:* density
  matrices ρ on a finite-dim Hilbert space (quantum); discrete kinetic densities f(x,v) on a lattice
  (Boltzmann/BGK); fine-scale fields u(x) (turbulence); a heterogeneous micro-ensemble (averaging/
  backreaction); the gauge-field path-integral configurations (QCD). A state of knowledge is a
  distribution / convex state μ ∈ Δ(Z).
- **f : Z → X** — the **lens** (coarse description map): *what macro information is retained*. It
  induces the **definability algebra Σ_f** = the predicates/observables visible *through* f (the
  fiber-constant predicates). *Physics examples:* "keep only the diagonal in a chosen basis"
  (dephasing); "keep low-order velocity moments ρ, u, e" (hydrodynamics); "spatial filter / keep
  scales > σ" (LES); "keep mean (and variance)" (cosmological averaging); "keep thermodynamic
  potentials" (statistical mechanics → thermodynamics). The induced coarse-graining /
  pushforward is `Q_f : Δ(Z) → Δ(X)`, `(Q_f μ)(x) = Σ_{z∈f⁻¹(x)} μ(z)`.
- **E** — the **packaging / completion endomap** (often approximately idempotent): how the discarded
  information is reconstructed, and the resulting fixed points are the states "internally complete at
  this scale." Built from a **completion** `U_f : Δ(X) → Δ(Z)` (a canonical *least-commitment* lift —
  diagonal embedding, local-equilibrium/Maxwellian, max-entropy, uniform-on-fibers) via
  `E = E_f := U_f ∘ Q_f`. The objects of the layer are the image of E (e.g. diagonal density matrices
  = "classical states"; the local-equilibrium manifold = "fluid states").
- **D** — the **defect ledger** (a.k.a. the audit 𝒜): nonnegative diagnostics — idempotence defect,
  route-mismatch, residual norms, an audit divergence (KL / relative entropy / TV) — with a
  **monotonicity principle under refinement**. D records *feasibility under refinement*, **not a
  time-arrow**.

Only operators whose **defects stabilize under refinement** become admissible "laws" at the packaged
layer. A layer is *lawful* exactly when its defects shrink and route-mismatch decays under refinement;
it fails to close when an obstruction persists. *(A Physics is A Theory §§2–3; To Spend a Stone §2;
A Mathematics is A Theory.)*

> **Naming reconciliation (paper governs):** the audit/ledger slot is written `D` in the math digest,
> `𝒜` in *To Spend a Stone*, and tracked as concrete diagnostics in *A Physics is A Theory*. They are
> the same role (P6). This atlas writes the package `T = (Z, f, Σ_f, E, D)` and reads `D` as the
> defect/audit ledger.

### The timescale packaging operator (dynamics enter here)
Let `T_τ : Δ(Z) → Δ(Z)` be micro-evolution over a timescale τ (a quantum channel, a BGK step, a PDE
time-stepper, a Markov step). The **timescale packaging operator** is

> **E_{τ,f}(μ) := U_f( Q_f( T_τ(μ) ) ) = (E_f ∘ T_τ)(μ)** — "evolve micro for τ, then re-express in
> the macro description."

This is the object on which the finite diagnostics of §3 are evaluated.

---

## 2. Closure, the closure ladder, and the six roles (P1–P6) in physics

A **closure** is an equivalence under *vanishing defect*: `{z_h} ~ {z'_h} ⟺ Def(h) → 0` as the
refinement parameter `h ↓ 0`; the packaged object is the class `[{z_h}]`. This is the same move that
builds ℝ from ℚ. Stack physics closures and you get the **closure ladder** — the layered structure of
our theories: gauge fields → hadrons → nuclei → atoms → molecules → condensed matter; particle
mechanics → kinetic theory → hydrodynamics; quantum → (decoherence) → classical; full QFT → EFT (via
RG); full GR → Newtonian weak-field. *(A Physics is A Theory §3; A Mathematics is A Theory.)*

The **six primitives P1–P6 are roles** played by concrete objects in an instantiation, **not topics**
(A Physics is A Theory §2.2):

- **P1 Operator rewrite** — does a micro-update *descend* to the quotient (`p ~ q ⟹ F(p) ~ F(q)`)?
  When the macro evolution is *not* closed, the route-mismatch diagnoses the needed correction/rewrite
  term. *Physics:* the LES **subgrid stress** `τ_sgs`; the kinetic **collision-moment** correction.
- **P2 Constraints** — the macro-consistent family selected by the completion U_f: which states count
  as admissible at the layer (invariance, locality, algebra-compatibility, the equilibrium manifold).
  In physics this is also the slot where a *lower-layer currency becomes a higher-layer constraint*
  (§6).
- **P3 Protocol / holonomy** — **route-mismatch** between two admissible routes (evolve-then-close vs
  close-then-evolve); a diagnostic `RM` that should decay in stable regimes (it is **not** a
  directionality certificate by itself). *Physics:* dephasing-vs-unitary noncommutation; filtering-vs-
  nonlinear-flux; averaging-vs-nonlinear-evolution (backreaction).
- **P4 Staging** — the scale parameter (time τ, filter width σ, collision strength ω, refinement
  level, Knudsen number) at which packaging is evaluated; `h ↓ 0` makes "infinite composition" a
  limit question.
- **P5 Packaging** — the closure `E_f = U_f ∘ Q_f` and `E_{τ,f}`; idempotent saturation.
- **P6 Accounting / audit** — monotone defect / audit quantities (KL, relative entropy, TV, RMS
  mismatch); provenance, replay, checkability. **Audit monotonicity** = a data-processing inequality:
  `A(Q_f μ, Q_f μ') ≤ A(μ, μ')` — coarse-graining cannot *create* distinguishability.

*(A Physics is A Theory §2; Foundations II — the exact-six program; To Spend a Stone §2.)*

---

## 3. The finite diagnostics — how an edge is tested **on a declared finite toy model**

**Everything in this atlas is computed on a *declared finite* toy model of a theory-pair: finite
linear algebra on small finite-dimensional state spaces. NEVER an irreducible run.** A toy model is
**declared before computation** (no tuning the model to the desired tier) and consists of: a finite Z
and X, an explicit lens `f` (hence `Q_f` as a stochastic/partition matrix), an explicit completion
`U_f`, an explicit finite micro-evolution `T_τ` where dynamics are relevant, and a chosen audit. From
these, three finite, checkable numbers:

### 3a. Idempotence defect (is the layer coherent as a self-contained theory?)
The **section axiom** `Q_f(U_f ν) = ν` makes `E_f = U_f ∘ Q_f` an exact projection: `E_f(E_f μ) =
E_f μ`. When it holds only approximately we track the **idempotence defect**
`δ(μ) := ‖ E_{τ,f}(E_{τ,f} μ) − E_{τ,f} μ ‖` (TV or trace distance). *Physics calibration of the
diagnostic:* dephasing has δ = 0 exactly (a perfect projection onto diagonal states); discrete BGK
has δ ↓ 0 as collision strength ω ↑ (the fluid layer stabilizes). *Interpretation:* δ ≈ 0 ⟺ the macro
family is a coherent autonomous layer on timescale τ.

### 3b. Route-mismatch (does the closure commute with dynamics? = is the macro layer dynamically
closed, or is an effective term forced?)
The two routes from μ are **(A)** `E_f(T_τ μ) = E_{τ,f}(μ)` and **(B)** `T_τ(E_f μ)`. Their
difference is the **route-mismatch**; exact equality is the commutation condition
`E_f ∘ T_τ = T_τ ∘ E_f`. A **sufficient condition for commutation is factorization through the macro
layer**: ∃ macro evolution `S_τ : Δ(X) → Δ(X)` with `Q_f T_τ = S_τ Q_f` and `T_τ U_f = U_f S_τ`. When
the routes do *not* commute, the structured mismatch **is the forced effective term**. *Physics:* in
LES the mismatch *is* the subgrid stress `τ_sgs = (u²)‾ − (ū)²`, identically zero for linear dynamics,
generically nonzero for nonlinear; in cosmological averaging it is the backreaction term; in quantum
it is the regenerated-then-erased coherence. *Null gates (calibrate the diagnostic):* σ = 0 ⇒
mismatch ≈ 0; heterogeneity s = 0 ⇒ mismatch ≈ 0; H diagonal in the dephasing basis ⇒ mismatch = 0.

### 3c. The Ξ adequacy residual (the *decisive* finite descent test) — Schur complement
For a theory-pair, declare on the finite toy model a **native probe family L** (the macro layer's
observables / readouts — the *target* layer that "wants to explain") and a **dissolving family D**
(the source layer's observables — what is to be explained / dissolved), as **finite-rank response
operators** under an audit energy `C`. With block "currencies"
`K_LL`, `K_DD`, `K_DL`, `K_LD` (finite PSD matrices), the **adequacy residual** is the **Schur
complement**:

> **Ξ_C(D | L) = K_DD − K_DL · K_LL^† · K_LD** ⪰ 0
> (Moore–Penrose pseudoinverse keeps this meaningful when K_LL is rank-deficient.)
> Equivalently (projection identity), in energy-scaled coordinates `Ξ_C(D|L) = T_D (I − P_L) T_D^*` —
> the dissolving readout *after projecting away* the part already explained by the native probe range.

**The exact-adequacy theorem** — the atlas's finite "no-leftover" test — says the following four are
**equivalent** on the finite model:

> **Ξ_C(D | L) = 0 ⟺ D₀ = A_* L₀ ⟺ ∃ linear A with D₀ = A·L₀ ⟺ ker L₀ ⊆ ker D₀.**

In words: **zero residual ⟺ the source readout factorizes through the native (target) layer ⟺ a clean
descent exists.** This is the finite, checkable certificate that the higher description **adequately
explains** the lower probe under the chosen audit — *a coarse-graining physics already accepts*. The
**same residual, read as a positive obstruction**, is **blind-spot currency**: what the native layer
*cannot* see that the enriched layer reveals; its failure produces an explicit recombination witness
with positive excess. **Orientation matters:** *adequacy* wants `Ξ → 0`; *obstruction* wants `Ξ ≻ 0`
(the residual **is** the evidence). *(Adequacy Residuals and Blind-Spot Currency — Defs. 3.x,
Thm. exact-adequacy, projection identity; this is the paper that defines every `Ξ` symbol.)*

> **DISCIPLINE.** `Ξ = 0` certifies *adequacy/descent on the declared finite toy model under the
> declared audit C* — it is **not** a derivation of the source theory from the target, and **not** an
> empirical claim. Exact adequacy is **a hypothesis to be verified, not a default**; the paper does
> **not** claim `Ξ = 0` generically. A nonzero Ξ **locates and types** a gap; it does not "fail."

> **The descent verdict reads the NORMALIZED (relative) residual, NOT the raw Ξ norm (Pause-2, review
> fix R-P2).** The raw `Ξ` norm is **not scale-invariant** and may *grow* under refinement even on a
> foreclosed (non-descending) edge — a units/normalization artifact, not evidence. Define the **relative
> residual** `ξ_rel(h) := ‖Ξ_C(D|L; h)‖ / ‖K_DD(h)‖` (a dimensionless ratio in `[0,1]` — the located
> obstruction as a *fraction* of the total source-readout currency `K_DD`; equivalently the fraction of
> `T_D`'s energy outside the native range `P_L`). `ξ_rel = 0 ⟺ Ξ = 0` (the exact-adequacy equivalence is
> preserved) but `ξ_rel` is scale-invariant. **CLEAN DESCENT (E1) requires `ξ_rel → ~machine-zero
> STABLY` across both declared refinements `h₁ ⊏ h₂`** (a small *raw* Ξ is NOT sufficient; a large/growing
> raw Ξ is NOT disqualifying). **E0/E3 (obstruction/gap)** is the **normalized residual staying bounded
> away from zero with analytic control** (a known nonzero lower bound on the fraction, not a numerical
> accident). **Report BOTH** the raw Ξ and `ξ_rel` at each refinement; the verdict is taken from `ξ_rel`.
> - **E001 (QCD → hadron-spectrum, the E0 anchor) — STABLE POSITIVE NORMALIZED RESIDUAL + ANALYTIC
>   CONTROL:** raw Ξ *grows* (7.84e8 → 2.25e9) while the **normalized** residual shrinks toward a stable
>   positive floor (`ξ_rel`: 0.197 → 0.042) and **stays positive** (never machine-zero). The E0/E3 signal
>   is this stable positive `ξ_rel` with analytic control — NOT monotone raw growth (no `D₀=A·L₀`
>   shortcut; the positive floor is the blind-spot currency of the missing run). Hence E001 = **E0**.
> - **E005 (GR → black-hole-thermodynamics) — NUMERIC Ξ SMALL IS AN OVER-READ:** classical GR's Ξ is
>   *numerically small* (`ξ_rel ≈ 0` on a GR-only probe family), but this is an **OVER-READ** (no-over-read
>   gate fail), NOT a clean descent — the `ħ`-coefficients and the thermal reinterpretation
>   (`T = κ/2π`, `S = A/4`) are **not in GR's `Σ_f`**, so a GR-only probe cannot express them and its small
>   Ξ silently drops the imported thermal predicates. Including the thermal observables in the readout map
>   makes the descent over-read its source; the edge lands **E2** via the named import. Lesson: **a small
>   numeric Ξ when `ħ`/thermal predicates are imported is an OVER-READ, not an E1** — read `ξ_rel` against
>   the full target readout map including the imported predicates.

> **The toy-model `M` is itself fenced (review fix #5; gates E.9, E.10 in the rubric).** The single
> largest tunability surface is the *choice* of the finite toy model `M` (carrier, probe families
> `L₀,D₀`, audit energy `C₀`): a hand-picked `M` could drive `Ξ→0` (force E1) or `Ξ≻0` (force E3) even
> after being declared-and-hashed. So `M` is fenced three ways, all still finite linear algebra (NOT an
> irreducible run): **(E.9 refinement-stability)** the `Ξ=0`/`Ξ≻0` verdict must be **stable across at
> least two declared finite refinements `h₁ ⊏ h₂`** — a verdict that flips between refinements is
> tier-fragile and seals at the conservative terminal **E3**; **(E.10 second-annotator faithfulness)**
> `M`'s declaration must be certified a minimal faithful finite stand-in by a **second independent
> annotator before the hash**; **(no-faithful-`M` route)** a theory-pair with **no honest finite toy
> model** (candidate: QM↔GR) seals **E3 by the distinct "no faithful M" sub-reason** — recorded as a
> *vacuous* (test-not-buildable) E3, never silently folded into a *run-and-failed* descent E3, so the
> reader sees whether the descent-test was even constructible.

---

## 4. The up/down asymmetry, made concrete in physics (the content, not a detail)

Inter-layer relations come in two flavors that are **not** mirror images (primer §6):

- **DOWN — shadow / descent / coarse-graining.** A higher layer casts a lawful shadow on a lower one.
  **Definable, provable, checkable, runnable as a derivation.** Its law is **descent legality**: the
  shadow must factor through the right quotient (`Ξ = 0` / `ker L₀ ⊆ ker D₀`) and must **not
  over-read** its source. *Physics shadows (the bulk of the atlas):* statistical mechanics →
  thermodynamics; kinetic theory → hydrodynamics (Chapman–Enskog/moment closure); QM + decoherence →
  classical (dephasing); full QFT → EFT (RG / "Scale Descent" — integrate out high modes); full GR →
  Newtonian weak-field limit; EM → geometrical optics (eikonal). These are the **E1** edges (§5): a
  computable descent physics already accepts, checkable now via Ξ on a finite toy model.

- **UP — emergence / strict extension.** Climbing from a lower lawful theory to a strictly richer one.
  **Non-definable from below, generative, run-only; NO shortcut.** Its signature is **non-factorization**:
  the extended object map `π₁` does not factor through the base `π₀` (no `φ` with `π₁ = φ ∘ π₀`); two
  states identical in the base differ in the extension; the new distinctions are exponentially rare in
  the base vocabulary. **You can run the DOWN arrow as a derivation; you can NEVER run the UP arrow as
  one.** *Physics emergence (sparse, the E0/E3 edges):* the hadron mass scale / Λ_QCD generated by
  *running* the gauge path integral (dimensional transmutation — there is **no free proton/hadron mass
  parameter**; under physical-quark-mass lattice QCD the quark masses and coupling/scale are fixed
  independently and the spectrum readout is out-of-sample, not fitted); an SPT phase's protected
  invariant; the value of a coupling/scale that exists only as the readout of a substrate run.

> **The no-shortcut law (primer §5, and "Irreducibility / No Short Closed Description," Foundations
> IV).** *A derivable constant is, by definition, not an emergent one.* If a closed form could
> shortcut the run, that form would already contain every strict extension along the way — so those
> extensions were definable from below — so they were never strict extensions. **The non-existence of
> the shortcut IS the genuineness of the emergence.** This is *the proof of concept in physics*: the
> proton mass is read only by running lattice QCD; validated not by a formula but by predicting what
> it was never tuned to.

> **Reductionist traps to refuse (primer §9), in physics terms:**
> (1) "Unify A and B by deriving both from shared math" ✗ → ask for the **common refinement** (F51,
> §6) they both project from, or how one casts a **shadow** on the other, and **audit** it.
> (2) "Derive the emergent constant / find its formula" ✗ → identify the **run** that generates it →
> **E0**, deferred to the Run-Target Manifest.
> (5) "The higher layer reduces to the lower" ✗ → reduction runs **down** (shadow), never **up**; keep
> the asymmetry.
> (8) "A foreclosure/no-go means SBT failed" ✗ → SBT **predicts** foreclosure-dominance; a foreclosed
> edge is the framework working. The predicted atlas shape is **shadow-heavy (E1), emergence-sparse
> (E0/E3).**

---

## 5. Edge-tiers as a deterministic foreclosure decision-procedure (E1 / E2 / E3 / E0)

Every charted edge gets **exactly one** edge-tier, **forced by audited tests**, never tuned to flatter
SBT. The procedure (full operational form lives in the **Typing Rubric**; the science behind it is
here). For an edge `source → target` (does the *target/native* layer adequately account for the
*source/dissolving* readout?):

1. **Run the descent test.** Declare the finite toy model; compute **Ξ_C(D | L)** AND the **NORMALIZED
   residual `ξ_rel = ‖Ξ‖/‖K_DD‖`** at two refinements (§3c; the verdict reads `ξ_rel`, not raw Ξ).
   - **`ξ_rel → ~machine-zero STABLY`** (equiv. `Ξ = 0` / factorization `ker L₀ ⊆ ker D₀`, a
     coarse-graining physics already accepts), with **no over-read** ⇒
     **E1 = computable descent.** Checkable *now*. *Examples:* stat-mech → thermo; kinetic → hydro;
     QM+decoherence → classical; SR → Newtonian/Galilean limit; QFT → EFT (RG). (A small *raw* Ξ alone is
     NOT sufficient; a stable positive `ξ_rel` with analytic control is the E0/E3 obstruction signal.)
2. **Else, run the recognition-search** (it is **logged**; an edge is **never** sealed until *both*
   the descent test and the recognition-search have actually been run and recorded).
   - Is there a **NAMED external principle** (cite it) that closes the edge **under a stated closure
     assumption**, imported as a named source, **not** derived internally? ⇒ **E2 =
     recognition-conditional.** Reported **separately**, always labeled **"conditional."** *Candidate
     physics:* GR → black-hole thermodynamics (**E005**, named import = **QFT in curved spacetime
     (Hawking thermal flux) + the first law of black-hole mechanics**, under the semiclassical
     no-back-reaction assumption — this is the E034 construction); the **opposite-arrow** recovery
     thermodynamics → GR (**E022**, named import = **Jacobson's "Einstein equation of state"**:
     Clausius dQ=TdS + the Bekenstein–Hawking entropy ansatz + local Rindler thermality); AdS/CFT
     (F41 duality-equivalence, the *Maldacena holographic dictionary* imported as the named source);
     gravity ↔ entanglement (Ryu–Takayanagi).

> **Frozen named-import discipline (review fix #3).** A calibration anchor's "named import" must be
> **frozen, not chosen at typing time** (gate E.0). The E2 calibration control is **E005 (GR →
> black-hole thermodynamics)** and its named import is **fixed** to QFT-in-curved-spacetime + the
> first law of BH mechanics (= E034); it may **not** be substituted with Jacobson at audit time.
> **Jacobson's equation of state is a separate, opposite-direction edge (E022, thermo → GR
> *recovery*)** and must never be conflated with E005 — conflating them is a route-direction error of
> exactly the kind the up/down asymmetry forbids (§4).
3. **Else, is there a constructible non-descending object whose generation needs a RUN?** ⇒ **E0 =
   run-only / computationally irreducible.** **FLAGGED OUT and DEFERRED** to the **Run-Target
   Manifest** (we do *not* run it — hard scope). *Canonical example:* QCD → hadron masses (§7).
4. **Else** ⇒ **E3 = sharpened gap / foreclosure no-go.** The obstruction is **located and typed**,
   **not closed.** *Candidate physics:* QM ↔ GR (the quantum-gravity gap); the SM gauge group
   SU(3)×SU(2)×U(1) origin; three generations / mass hierarchy; the cosmological-constant value.

> **NEVER sum E1 with E2 / E0.** E1 is accepted-physics descent (Tier-1-like); E2 is conditional on a
> named import (Tier-2-like, reported apart); E0 is deferred run-only; E3 is an open typed gap. The
> word **"solved" is forbidden** for E2/E3/E0; **"decisive"** always carries **"conditional on the
> audited casting, licensed by the proton-mass calibration."** *(Maps the Erdős E0/1/2/3 ↔ Tier
> 0/1/2/3 vocabulary in `enums.md`, ported to edges.)*

> **The single conservatism/informativeness ordering (review fix #4 — there is exactly ONE).**
> **E1 (most-flattering) > E2 > E0 > E3 (least-flattering).** **E3 is the unique conservative
> terminal**, and every "doubt" demotes **strictly toward E3**: doubt at the descent test → not E1;
> doubt at the recognition search → not E2; doubt at the run-search → not E0, land E3. **E0 is NOT a
> safe haven for a doubtful edge** — sealing E0 requires the *positive* construction of a
> non-descending run-object (gate E.7), never a fallback. Doubt never promotes; it only demotes. (Any
> earlier draft string ordering E0 below E3, e.g. "E0 < E3 < E2 < E1," is deleted as contradictory.)

---

## 6. Foreclosure, recognition-mode landing, and the cross-layer structural laws (F41 / F51 /
currency–shadow-price / holonomy)

**Attack-Foreclosure v5 (primer §7; One Meta-Theory; specialized to physics edges).** Framework-
**internal derivation** routes **foreclose** — SBT cannot advance a *hard* inter-theory edge to a
"derived" relation by its own machinery without **named external content**. This is the no-shortcut
law operationalized for edges. The honest consequence: **hard closures land only conditionally**, by
**recognition-mode landing** — *importing a NAMED, load-bearing external source* (a physical
principle, an accepted duality, an established correspondence) under a **stated closure assumption** —
**never** as an unconditional derivation. Such landings are **conditional peers (E2)**, reported
separately, **not** collapses of the descent (E1) edges.

> **`recognition-landing` is a canonical edge MODALITY (review fix R2).** Recognition-mode landing is not
> only the E2 mechanism — it is promoted to a first-class **modality** (`recognition-landing`, rubric
> §B.6a) for the **8** edges (= `CONTRACT.json` `recognition_resolution.affected_edges`) whose entire
> content is the named import: **E007** (Born rule — the single frozen import is Gleason's theorem;
> envariance / decision-theoretic are `alternatives_not_used`, not contract imports), **E022** (thermo →
> GR — Jacobson's equation of state), **E025** (QM → thermo — ETH ansatz), **E026** (QM → pointer-basis —
> einselection criterion), **E027a** (SPT classification — group-cohomology), **E028b** (GR → ΛCDM — the
> imported Λ / dark-matter / cosmological-measure content), **E030** (thermo → arrow-of-time — the Past
> Hypothesis), **E033** (classical mechanics → thermo — the Stosszahlansatz). It is its own modality
> because these 8 span **both arrow directions** and **different mechanisms** — what unifies them is solely
> that *no internal
> descent/duality/refinement closes the edge; it is characterized only by an imported named principle*.
> **Operational test:** (i) the descent-test fails, (ii) no duality / common-refinement test passes, and
> (iii) a single named external principle, under a stated assumption, is what closes it (remove the import
> and no relation remains). **It is tier-locked to E2** (rubric §B.8): it can be neither E1 (that is a
> computable descent, B.1), nor E0 (that is a constructible run-object, B.2 emergence-up), nor E3 (if
> recognition-search returns nothing named, the edge is no longer a recognition-landing and is re-typed by
> its arrow before sealing E3). The frozen canonical modality strings are
> {`shadow-down`, `emergence-up`, `duality-equivalence`, `common-refinement`, `currency-shadow-price`,
> `holonomy`, `recognition-landing`}; any non-canonical modality string is rejected at freeze
> (`CONTRACT.json`).

> **PRIMARY vs SECONDARY modality — the MODALITY PRECEDENCE RULE (Pause-2, review fix R-P2).** The
> external Pause-2 review resolved a modality-label ambiguity on **E005** (GR → black-hole-thermodynamics)
> by **primary + secondary modality with a precedence rule** (rubric §B.7a; `CONTRACT.json`
> `modality_precedence_rule` / `secondary_modality_schema`). The existing per-edge `modality` field is
> **NOT renamed**: it **is the `primary_modality`**, the only one used for `(modality,tier)` emittability
> and headline / registered-null reporting. An edge may also carry an **optional** `secondary_modalities`
> array / `conditionality_flags` (descriptive residual annotations, never counted). **Precedence:**
> **(1)** if any **structural** test passes (duality, common-refinement, holonomy, currency/shadow-price,
> descent, emergence) that **structural modality is PRIMARY**; **(2)** `recognition-landing` is primary
> **only** as a residual — when **no** structural modality closes the edge and the imported named
> principle is the **entire** landing mechanism; **(3)** if a **structural** E2 edge still needs a named
> import, record **`recognition-conditional` as a SECONDARY flag**, not as primary `recognition-landing`.
> **E005** is the worked case: the structural **currency/shadow-price** test passes (the §6 / rubric §B.5
> exemplar **"surface gravity as the 'price' in black-hole thermodynamics"**), so `primary_modality =
> currency-shadow-price`, tier **E2**; it carries `conditionality_flags = ["recognition-conditional"]` as a
> secondary flag because classical GR's `Ξ≈0` is an over-read (the `ħ`/thermal predicates are imported).
> E005 is therefore a **structural-currency-E2 edge with a recognition-conditional secondary flag**, NOT a
> primary `recognition-landing` (contrast E022, the opposite-arrow thermo → GR recovery, which IS a primary
> recognition-landing — Jacobson's equation of state is its entire landing mechanism). The named-import
> hygiene that check **C11** enforces for primary recognition-landing rows applies **in parallel** (new
> check **C13**) to a secondary `recognition-conditional` flag: E005's import (QFT-in-curved-spacetime +
> first law of BH mechanics) is frozen to a single principle, not substitutable at typing time. (C12 is
> the pre-existing R6 registered-null/stale-prose guard and is unchanged.)

> **GATE POLICY (Pause-2, review fix R-P2; `CONTRACT.json` `gate_policy`).** Calibration **hard-gates on
> TIER**: every `is_calibration` `must_seal_*` row's computed tier must equal its `calibration_known_tier`
> and every anti-control must land in `{E3, E0}`. **Modality checks hard-gate** on (i) canonical primary
> modality strings, (ii) primary-modality/tier emittability, and (iii) recognition-import hygiene (C11 for
> primary recognition-landing rows, **C13** for secondary recognition-conditional flags). A **blind-vs-frozen
> PRIMARY-modality mismatch** is **routed to adjudication and the scored gate re-run, NOT auto-failed** —
> modality is empirically less deterministic than tier on hard/faceted edges (two of nine Pause-2 blind
> edges, E005 and E018, disagreed on modality while getting tier right). The adjudication is recorded, not
> silently force-aligned.

The cross-layer modalities an edge may carry (from **Foundations IV — Catalog of Layer-Agnostic
Structural Laws**), each used here as a **typing tool, not a reduction**:

- **F41 Duality Equivalence** — two formed closures `C_A, C_B` are role-preservingly dual iff their
  descended quotient maps are mutually inverse and route/status structure is preserved. *Physics
  instantiations in the catalog:* Pontryagin / Stone / Gelfand dualities; **AdS/CFT** (typed against
  the *accepted holographic dictionary* — note the open Hamiltonian/global-symmetry questions are
  acknowledged, so AdS/CFT is **recognition-conditional E2**, not a free descent). A duality is a
  **bidirectional shadow**, not a reduction of either side to the other.
- **F51 Unification as Common Refinement** — a parent closure `C_U` is a **common refinement** whose
  quotient projects compatibly onto two children `C_A, C_B` (objects, routes, *and* claim-statuses).
  **Unification in SBT is a join / recognition, never a reduction** (primer §9, trap 1). *Catalog
  physics instantiations:* **Maxwell** unifying electrostatics + magnetostatics; **electroweak**
  unification (Weinberg) of EM + weak. Ask "what common third do A and B both project from?" — never
  "derive both from shared math."
- **Currency → shadow-price (P5–P6–P2 chain; To Spend a Stone).** A **lower-layer currency** (what a
  layer must spend to stay closed — an audited budget) becomes a **higher-layer constraint**; the
  higher layer's own currency appears as the **shadow price** (dual multiplier) of that budget. This
  is **top-down coupling** that is lawful, not a reduction. *Physics:* inverse temperature β as the
  dual of a mean-energy constraint (stat-mech → thermo); pressure/chemical potential as shadow prices;
  a constrained-max-entropy closure yielding dual prices. Use this to type edges where a **constraint
  at the macro layer is the priced shadow of a micro budget**.
- **Holonomy / route-mismatch / anti-localization (P3).** Path-dependence of closure routes; the
  route-mismatch `RM` of §3b is the finite diagnostic. A nonzero, non-decaying holonomy types an edge
  as carrying an *irreducible* protocol obstruction (candidate E3), distinct from a forced rewrite
  term that *does* close the macro evolution.

---

## 7. The worked E0 example — proton mass / lattice QCD (the calibration anchor)

This is the **canonical, already-resolved E0 edge** that calibrates the whole atlas (HARD SCOPE: we
spec it, we do **not** run it).

- **Edge:** QCD (gauge-field substrate) → hadron masses (proton mass, the GeV scale).
- **Why not E1 (descent fails the no-overread / no-shortcut test):** **there is no free proton/hadron
  MASS parameter.** Under the declared lattice-QCD protocol — **physical-quark-mass lattice QCD** — the
  quark masses and the coupling/scale are **fixed independently** (the scale is set by **one hadronic
  input**, and the running is generated by **dimensional transmutation**, Λ_QCD); the **proton-mass /
  hadron-spectrum readout is out-of-sample and NOT fitted**. There is **no closed form**, no
  factorization `D₀ = A·L₀` that shortcuts the gauge-field path integral to the proton mass. By the
  no-shortcut law (§4), the absence of the shortcut **is** the genuineness of the emergence: the proton
  mass is a **strict extension** (non-definable from a shortcut over the bare-coupling layer), read off
  the run rather than tuned.
- **Why not E2:** there is **no named external principle** that *closes* the number under an
  assumption; the only honest route to the value is to **run**.
- **Therefore E0 = run-only / computationally irreducible.** The constant is the **readout of an
  irreducible run**: lattice QCD, the gauge-field path integral on a supercomputer. It is lawful,
  reproducible, and accessible **only by running**.
- **How it is validated (primer §8) — and why the atlas STOPS here:** not by deriving and checking
  (there is no derivation), but by **reproducible runs + out-of-sample prediction of observables not
  fit**. This atlas **flags the edge OUT** into the **Run-Target Manifest** and **does not perform the
  run, does not predict, does not derive the constant** — that is the hard scope boundary. A formal
  checker could certify that *a run was performed correctly* and *each inter-layer step was lawful*; it
  can **never** certify that the substrate is faithful to the world or that the readout matches a
  measurement. Those bridges are un-realized assertions, kept on the formal side.

> **Calibration as a freeze-blocker (Erdős APN-9 rule, ported; wired by review fix #7, tightened by
> O4).** The proton-mass edge (**E001**) **must** come out **E0** with a spec matching
> **physical-quark-mass lattice QCD** (no free proton/hadron MASS parameter; quark masses and
> coupling/scale fixed independently under the declared protocol, scale set by one hadronic input; the
> proton-mass / hadron-spectrum readout out-of-sample and NOT fitted); the named E1 controls (**E002**
> stat-mech → thermo; **E003** SR → Newtonian; **E004** kinetic → hydro) **must** come out **E1**; the
> recognition control (**E005** GR → BH-thermo) **must** come out **E2**. And the four **E3
> anti-controls** (**E018** QM↔GR, **E019** gauge group, **E020** generations, **E021** Λ) **must NOT**
> come out E1 or E2 (they must land in {E3, E0}) — this is the firewall test that SBT does **not**
> secretly derive the gauge group / Λ. **O4 tightening:** an anti-control may land **E0 only if** its
> `run_target_stub` was frozen **before** scoring **and** the E.7 double-run interlock is logged; else its
> E0 is demoted to E3 (so E0 is not a flattering "real emergence, deferred" haven). Every calibration row
> carries a machine-checkable `calibration_known_tier` (and the anti-controls a
> `calibration_rule:"must_not_seal_E1_or_E2"`). The **freeze-gate predicate**: *freeze iff every
> `is_calibration` row's computed tier equals its `calibration_known_tier`, every E3 anti-control's
> computed tier is in {E3, E0} (E0 only with a pre-frozen run-target stub + logged E.7), and every
> casting-bearing card was frozen in full before any `M`/`Ξ` (gate E.12 / R1).* **A calibration
> FAIL blocks the freeze** of the scored run; the workflow's Assemble phase must enforce this
> programmatically (not by reading prose). The calibration proves the decision-procedure measures
> closure-structure, not the modeler's wishes.

---

## 8. The elasticity firewall (honesty discipline, binding)

The bundle must be an **elasticity firewall**: castings and tiers are **forced by audited tests**,
never tunable to flatter SBT. Concretely (enforced in detail by the Typing Rubric's no-smuggling
gates):

- **Full closure-package cards are frozen BEFORE any number (HARD GATE E.12 / review fix R1).** No toy
  model `M` may be declared and no `Ξ`/`RM`/`ID` may be computed until the FULL §A card (every field) is
  frozen and hashed in `closure_card_manifest.jsonl` for **every theory id and every casting-bearing
  node**; the `provisional_Z/f/E` stubs are not sufficient for scoring. This makes the firewall
  ordering-enforced rather than declarative: cards first, always, before any tier or `Ξ`.
- The **toy model is declared before computation**; you may not re-pick Z, f, U_f, C, or T_τ to hit a
  target tier. **Relabeling is NOT a connection.** And the toy model is **refinement-stable** (gate
  E.9, two finite stages) and **second-annotator-faithful** (gate E.10) before it is hashed.
- **A `not_established` node may not source an E1 descent (review fix R6).** Every registered node carries
  a machine-readable `established_status ∈ {experimentally_established, not_established}`; the
  `may_source_E1` rule allows a node to be the SOURCE of an E1 (computable-descent) edge **only if** it is
  `experimentally_established`. (E035a `lattice-gauge-theory → qcd` and E040 `many-body-quantum →
  fermi-liquid-theory` source E1 only because those nodes are marked `experimentally_established`;
  `string-theory` etc. are `not_established` and may not.)
- A **descent must not over-read its source** (no-smuggle): `Ξ = 0` licenses *only* the audited
  lower-layer answer, never literalizing a hidden object. Where an edge's **form and value (or
  theorem-status and run-exhibited phenomenon) close at different tiers**, the edge carries a generalized
  `value_split {form_tier, value_tier, split_type, value_node}` (review fix R5), with `split_type` ∈
  {**`form_value`** (form descends E1, values run-only E0 — E004/E008/E035a/E038), **`form_value_imported`**
  (form descends E1, predictive content imported E2 — **E029** ChPT, the canonical R3 row),
  **`theorem_run`** (open-theorem E3 vs run-exhibited E0 — E041)}. The **reported (headline) tier is
  SPLIT-TYPE-DEPENDENT (review fix R3):** for `form_value`/`form_value_imported` the reported leg is the
  **`value_tier`** (E029 reports E2 = value_tier = edge_scored_tier; the form-descends-E1 leg is recorded
  but NOT counted in the E1 null), and for `theorem_run` the reported leg is the **`form_tier`** (E041 stays
  E3). The non-reported leg is carried separately (into the Run-Target Manifest when E0, the conditional
  ledger when E2) and **NEVER summed** with the reported leg — the no-summing rule applied within a single
  edge.
- **Default to the CONSERVATIVE tier on doubt — and the conservative terminal is the unique E3.** An
  edge is **never sealed E0** until **both** the descent test (Ξ) **and** the recognition-search have
  actually been run and **logged** (E.7); E0 is **not** a doubt-haven (sealing it needs the *positive*
  construction of a run-object). Doubt demotes strictly toward E3.
- **Never sum E1 with E2 / E0.** Report E2 separately as "conditional." Banned language: "derive(d)"
  for an inter-layer relation, any empirical claim, "solved" for E2/E3/E0.
- A **modality↔tier compatibility table** (rubric §B.8) is enforced at freeze: a `shadow-down E0`,
  `emergence-up E1`, or off-tier `recognition-landing` (anything but E2) row is **rejected** — these pairs
  are not emittable by the deterministic procedure; and every modality string must be one of the 7
  canonical strings (review fix R2).
- **Foreclosure-dominance is the PREDICTED result, not a failure:** an honestly shadow-heavy (E1),
  emergence-sparse (E0/E3) distribution, with E2 a substantial but **separate** conditional band. This
  is the **registered null** — a *prediction recorded before the audit*, **not** a target to steer
  toward, and **not** the audited verdict (see FREEZE_NOTES; **source of truth =
  `CONTRACT.json` `registered_null`**). The pre-audit guess over the **46** edges is **E1=19, E2=13, E3=10,
  E0=4** (these MUST equal `CONTRACT.registered_null.per_tier`; the contract governs on any drift); the
  post-audit run must not be tuned toward it. **Registered-null E1 caveat (review fix O2):** the E1=19
  count INCLUDES the 3 near-intra-layer candidates (E016, E017, E039) still PENDING the gate E.4 / E.11
  relabeling test, carried as E1-pending (sealed-E1-eligible = 16); the audited E1 set **must REMOVE any
  such candidate that fails gate E.4** (within-a-layer restriction, no residual relation). An E1 count
  quoted without this caveat is a flattering-by-padding violation.

---

## 9. Within-vs-between, restated as an operating rule

Before typing any edge, confirm it is **between** two distinct lawful layers (different lens `f`,
different definability algebra `Σ_f`, a genuine quotient). If the "edge" is actually intra-layer
(same theory, free re-parametrization, a modeling choice inside one closure), **SBT is silent** —
record it as "within-a-layer, no SBT content," do **not** manufacture a tier. Scoring SBT inside a
layer always looks empty *by design* (primer §3); it is not evidence against the framework, and it is
not a chargeable edge.

---

## 10. Nonclaims (binding) and paper → concept map

**SBT does NOT claim:** to be a black-box prover; that any inter-theory edge is an unconditional
derivation (E2 closures are conditional under a stated closure assumption, reported separately); to
**derive any physical constant** (forbidden — E0 edges are deferred run-only); to make any **empirical
prediction** (the bridge from the formal/closure-algebraic side to a measured observable is a
separate, **un-realized** assertion); that the up arrow can be run as a derivation; nor that results
generalize beyond the declared finite toy models actually computed. **Using the map is not asserting
the territory** — typing physics through SBT's lens does not presuppose SBT is "true"; it is an
organizing instrument judged by what it usefully charts and audits.

| Concept (physics atlas use) | Primary paper (in `../../`) |
|---|---|
| Physics theory package `(Z,f,Σ_f,E,D)`, lens/completion/closure, the operator template `E_{τ,f}`, idempotence defect, route-mismatch, audit monotonicity, the four worked instantiations (quantum/dephasing, kinetic/BGK, LES, gravity/averaging) | `…To_Become_a_Stone…A_Physics_is_A_Theory.tex` |
| Closure, closure ladder, P1–P6 (intro), "a mathematics/physics is a theory" | `…To_Count_a_Stone…A_Mathematics_is_A_Theory.tex` |
| **Ξ adequacy residual** (Schur complement), block currencies, projection identity, **exact-adequacy theorem** (Ξ=0 ⟺ factorization ⟺ ker-containment), blind-spot currency / witness | `…Adequacy_Residuals_and_Blind_Spot_Currency.tex` |
| **F41 Duality Equivalence** (AdS/CFT, Pontryagin/Stone/Gelfand), **F51 Unification as Common Refinement** (Maxwell, electroweak), Scale Descent / RG, Holographic compression, **Irreducibility / No-Short-Closed-Description** (the E0 law), entropy as fiber volume | `…Six_Birds_Foundations_IV…Catalog_of_Layer_Agnostic_Structural_Laws.tex` |
| Strict extension = **non-factorization** in a lawful continuous setting (the up-arrow signature) | `…Strict_Theory_Extension_on_a_Lawful_Continuous_Cantor_Shell.tex` |
| Fixed packages, package change, Gödel as the fixed-package failure mode (no-shortcut, internal) | `…Six_Birds_for_Incompleteness…` |
| **Currency → constraint → shadow-price** (P5–P6–P2 top-down coupling) | `…To_Spend_a_Stone…Currency_Constraint_Duality_and_Shadow_Prices…` |
| **Attack-Foreclosure v5**, recognition-mode landing, conditional closures (the E2 mechanism) | `…One_Meta_Theory_Three_Clay_Problem_Closures.tex` |
| SAU / non-descending objects, audited descent, Theorems A–G, profile transfer (the "imaginary-number move") | `…The_Usefulness_of_Non_Descending_Objects.tex` / `…Why_Mathematics_Even_Works.tex` |
| Route-mismatch / holonomy without entropy production (P3 protocol traps); dark-energy as route-mismatch | `…Six_Birds_Protocol_Trap…` ; `…A_Six_Birds_Eye_View_of_Dark_Energy…` |
| Erdős mode / exit-state / tier vocabulary adapted to edge-tiers E0/E1/E2/E3 | `six-birds-erdos/docs/methodology/enums.md` |

> Where this digest and a paper disagree, **the paper governs** — flag the discrepancy for correction.
