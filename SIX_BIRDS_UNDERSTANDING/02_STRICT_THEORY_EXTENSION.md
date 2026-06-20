# Strict Theory Extension — the grounded synthesis

> ⚠️ **READ-ORDER (2026-06-20, post external audit).** The CURRENT, typed canon is `../CLAUDE.md` §3–4 — prefer it + the papers over this file. This file is a chronological ACCRETION: later parts contain round-by-round project history and a few superseded proposals (e.g. an obsolete `U_pkg ×_Q M_H` fiber-product and its later self-correction) sitting next to current content. Treat Parts 1–5 (theory spine) as canon; treat the round-by-round adjudication sections as ARCHIVE (history, not current truth). Typing fixes already in CLAUDE.md: the obstruction registers are typed FACES of one phenomenon (cross-register *equivalences* need bridge hypotheses — not a flat global equivalence); the Cantor saturation→forcing→obstruction route is the `[SCOPED]` audited-shell theorem's mechanism, not the universal recipe; SAU essentiality = deletion/replacement failure (projective MBO is a `[PROJECT HYP]` gate); the finite rarity result is scoped to uniformly-sampled Boolean predicates. (Thesis NOT in doubt — SBT is map AND engine; universality holds; see CLAUDE.md §2/§5.)

This is the document the project turns on. Every claim here is grounded in a specific paper passage or pica
code location. Where a claim is not yet grounded by a deep read, it is marked **[PENDING DEEP READ]** —
do not treat those as understood. Authority = the papers + the running code; this synthesis is secondary.

Status 2026-06-18: **Parts 1–5 ALL grounded** — Part 1 (Foundations I + primer), Part 2 (Cantor), Part 3 (SAU/Why-Math),
Part 4 (No-Go Theorems + Foundations III, the guards), Part 5 (Adequacy_Residuals + Needle-Killer, the Ξ register).
All read directly by the manager (not codex). The remaining open work is in `04` (resolve the A/B/C tension; then the
lattice construction); codex is reserved for the construction/implementation loop, not paper reading.

---

## Part 1 — What strict theory extension IS (grounded in Foundations I + the primer)

### 1.1 A theory/layer is a closure (a fixed point of an idempotent operator)

A theory = a **lens** `f: Z → X` (what distinctions you keep) + a **completion/packaging** (how you
reconstruct) + an **audit** (monotone defect bookkeeping). "Objects" are the **fixed points** of the
resulting (approximately) idempotent operator.
*Source: `SIX_BIRDS_ANTI_REDUCTIONISM_PRIMER.md` §2; Foundations I `def:tk-theory-package` (line 263),
§"Idempotent endomaps and induced closures" (line 460).*

The lens `f:Z→X` induces the **partition** `Π_f = {B_x}, B_x = f⁻¹(x)` — *"the distinctions expressible in
the current theory."* (Foundations I, forcing §, lines 993–997.)

### 1.2 Definability = FACTORIZATION through the lens (the load-bearing equation)

A predicate `h: Z → {0,1}` is **definable from theory `f`** (Π_f-measurable) iff it is constant on every
block, i.e.
> **there exists `h̃: X → {0,1}` with `h = h̃ ∘ f`.**
*Source: Foundations I, `Definition [Predicates and definability]`, lines 999–1006.*

**Definable ⟺ factors through `f`.** This is the single most important equation in the whole project.
A quantity that factors through the base lens is *already in the base theory* — it is **not** new content.

### 1.3 Strict extension = a distinction that does NOT factor (non-definability / non-factorization)

Adjoining a predicate `h` refines the theory to the joint lens `(f,h): Z → X×{0,1}`. The extension is
**trivial** exactly when `h` was already definable from `f` (i.e. factored). It is a **STRICT** extension
when `h` is **not** definable from `f`:

> **Corollary [Generic extension is strict] (Foundations I, lines 1082–1092):** with probability
> `1 − 2^{-(N-K)}`, the refined lens `(f,h)` is a *strict* refinement of `f` — it distinguishes at least
> one pair of microstates previously indistinguishable under `f`. *"If the refinement were not strict,
> then `h` would be constant on each block, i.e. definable from `f`."*

Equivalent phrasings of the SAME thing across the corpus:
- **Non-factorization** (primer §4; Cantor paper): the extended object map `π₁` does **not** factor through
  the base object map `π₀` — there is **no** `φ` with `π₁ = φ∘π₀`. Two base-identical states differ above.
- **Current-equivalent but future-distinct** (Holonomy w/ Memory): the predictive quotient strictly refines
  the current quotient. *[grounded by abstract; deep read PENDING]*
- **Non-definable from the game** (Institutions Are Strict Extensions): institutional state priced by a
  conditional mutual information, no low-complexity shortcut transfers. *[abstract; deep read PENDING]*
- **No admissible global packaging** (Locally Boolean, Globally Obstructed / `sixbirds_event`): a family of
  locally-Boolean contexts whose joint realization does not factor through any single global package.

### 1.4 Why iteration cannot produce it — saturation forces PACKAGE CHANGE

A fixed closure operator `c` is idempotent, so **`c^(n)(x) = c(x)` for all n ≥ 1** — iterating a fixed
completion rule **stabilizes after one step** ("the Box is the Thing").
> *"Thus strict ladder growth requires changing the completion rule (equivalently, passing to a stronger
> theory)."* — Foundations I, `lem:closure-iterate-stabilizes` + `cor:closure-saturates` + Remark, lines 398–424.

So **emergence = package change, NOT iteration** (primer §4). Doing more of the same saturates; a new layer
requires changing the operator itself. Gödel is the canonical fixed-package failure mode (Incompleteness paper).
**A closure ladder** is `c_n ≺ c_{n+1}` (each strictly stronger), with fixed-point sets nested decreasing
(Foundations I `def:closure-ladder`, lines 426–438).

### 1.5 Why it can't be derived — the no-shortcut law IS the genuineness certificate

Definable predicates number exactly `2^K` out of `2^N` total ⇒ `P(definable) = 2^{-(N-K)}`, exponentially
rare (Foundations I `lem:count-definable`, lines 1027–1034). So a generic new distinction is overwhelmingly
**not reconstructible from the old distinctions** (Remark, lines 1094–1098).

Primer §5 turns this into the certificate:
> **"A derivable constant is, by definition, not an emergent one... The non-existence of the shortcut *is*
> the genuineness of the emergence."**

Emergence escapes **math-as-reduction** (proof/formula/shortcut, which lives inside one fixed theory), NOT
**math-as-mechanism** (the run). A run can produce a new lawful fact unreachable by any proof from the start
theory, because *doing is package-change and proving is package-fixed* (primer §1, §4).

### 1.6 How you VALIDATE a run-only result (no fitting — out-of-sample only)

Because a strict-extension value has no derivation, it **cannot** be validated by deriving-and-checking. The
only honest validation (primer §8):
> **Reproducible runs + out-of-sample prediction of observables you did not fit.** In-sample fitting is
> circular and forbidden.

Worked precedent: **Institutions** validates its strict-extension constants out-of-sample on human data, and
shows no low-complexity shortcut transfers across families. The proton mass is the canonical case (primer §5):
QCD has **no free proton-mass parameter**; the mass is the **out-of-sample readout of an irreducible run**
(lattice QCD), scale set by one hadronic input, the spectrum not fitted.

### 1.7 The two directions are NOT symmetric (emergence up vs shadow down)

- **Up = emergence**: strict extension, non-definable, **run-only** (no shortcut). Law: non-factorization +
  no-free-content (nothing emerges that the substrate+audit didn't license).
- **Down = shadow**: projection/coarse-graining, **definable, derivable, checkable**. Law: descent legality
  (must factor through the right quotient; must not over-read).
You can run the down arrow as a derivation; you can **never** run the up arrow as one. Inverting an emergence
into a derivation is the category error. *Source: primer §6.*

### 1.8 What Six Birds itself is — the MAP *and* the ENGINE (critical scope)

> ⚠️ **CORRECTED (author-binding; `../CLAUDE.md` §2):** SBT is **both** the meta-map over the ladder **and** the
> generative engine — it supplies **P1–P6, the closure mechanics that CONSTRUCT emergence and layer formation.** The
> primer §7 quote below ("neither engine") scopes ONLY to the two *climbing methods* (the mechanical run vs
> imagination); it is NOT a denial that the primitives are the generative mechanics. Read the quote as the
> map/triage aspect, not as a ceiling on what SBT is.

> *"Six Birds is neither engine. It is the meta-map over the ladder. It does not generate the content and it
> is not a black-box prover. Its job is to triage, decompose, translate, name the right non-descending object,
> and audit each landing."* — primer §7.

Two meta-theorems of the map (primer §7; One-Meta-Theory paper):
- **Foreclosure:** framework-internal *derivation* routes foreclose — they cannot advance a hard target
  without named external content.
- **Recognition-mode landing:** a hard closure lands only *conditionally*, by importing a named external
  source under a stated closure assumption — never as an unconditional derivation.

> ⚠️ **CENTRAL OPEN TENSION (do not assume away):** if SBT is the map and the proton-mass *run* is lattice
> QCD itself, what exactly does this project's "compute lattice values via a six-birds layer on commodity
> hardware" mean? Is the six-primitives PICA run a *cheaper genuine run* that still climbs the ladder, or is
> the project asking the map to be an engine (which the primer forecloses)? **Resolve from the papers
> (To_Kill_Three_Stones, To_Create, One-Meta-Theory) — see `04_THIS_PROJECT_AND_OPEN_QUESTIONS.md`.**

---

## 1.9 How this indicts the failed approach (steps 99–102) — the litmus, concretely

The inject-a-known-operator-and-read-its-gap-back toy read a quantity that **factored through the operator
I injected** (`gap = h̃ ∘ f`): by §1.2 that is **definable**, hence by §1.3 a **trivial, non-strict**
"extension." And I "validated" it by matching a gap I had injected — **in-sample fitting**, forbidden by §1.6.
Both errors are named failure modes in primer §9 (#2 "derive the emergent constant," #3 "shortcut the run").
The litmus going forward: **does the step produce a distinction/value that provably does NOT factor through
the base lens, validated out-of-sample?** If it factors, or is checked in-sample, it is not strict extension.

---

## Part 2 — How a strict extension is CONSTRUCTED (grounded in the Cantor Shell paper)

*Deep-read of `Strict_Theory_Extension_on_a_Lawful_Continuous_Cantor_Shell.tex`, §"Strict theory extension"
(lines 649–768) + §"Definability as factorization" (364–377).*

### 2.1 The packaging endomap (THE engine object — same across paper, Rust, closurelab)

The completion theory `T_1` is built from the **evolve–forget–reinstantiate** packaging endomap (line 683):
> `E_{τ,ℓ}(μ) = U_ℓ( Q_ℓ( μ K^τ ) )`

where `μK^τ` = evolve τ steps, `Q_ℓ` = pushforward/forget under lens `ℓ`, `U_ℓ` = lift/reinstantiate. This is
**byte-for-byte the same object** as:
- Rust `Substrate::packaging_endomap`: `E(μ)=lift(pushforward(evolve(μ,τ)))` (`six_primitives_core/src/substrate.rs:381`);
- closurelab `numeric.empirical_endomap`: `E = P^τ Q U`.
So the packaging closure `E_{τ,f}` (= **P5**) is the SAME object in the theory and in every code lineage.
Its fixed points (small TV idempotence defect) are the packaged "objects". (Foundations I `D-IC-01/02`.)

### 2.2 The three ingredients that make the extension STRICT (lines 676–693)

1. **Saturation.** For fixed lens `ℓ`, timescale `τ`, repeated `E_{τ,ℓ}` stops producing new packaged objects —
   "the current object vocabulary has stabilized." (= Foundations I saturation.) Saturation is the SIGNAL, not the end.
2. **Material `P4 ← P5` forcing.** *"Once saturation occurs, packaging feeds back into the lens layer. Material
   P4←P5 forcing changes the active lens and reveals new packaged strata not visible at the previous theory depth.
   This is the mechanism by which the extension moves from the base theory to the packaged-object theory."* — i.e.
   the packaging (P5) FORCES a change of lens (P4). **This is package-change in action** — the operator changing
   itself, which §1.4 says is the only route to strict growth.
3. **Macro-admissibility OBSTRUCTION.** *"The cocycle-level theory is too coarse to support closed macro-dynamics
   on the packaged future... a failure of admissible aggregation or lumpability at the macro level."*

### 2.3 The theorem: strict extension ⟺ non-factorization (lines 695–718)

Under (base `T_0` closed; completion well-defined; **saturation**; **P4←P5 forcing produces new strata after
saturation**; **macro-admissibility obstruction on the packaged future**), `T_1` is a strict theory extension of
`T_0`, **equivalently: there is NO factorization `π_1 = φ ∘ π_0`** for any `φ: O_0 → O_1`.

Proof step 4 (non-definability, line 736): *"If `π_1` factored through `π_0`, the packaged strata revealed after
forcing would already be reconstructible from the cocycle object map. ... shell states with the same `T_0`-object
can carry different packaged-object strata in `T_1`."*
Proof step 5 (line 740): *"The failure of macro-admissibility at the cocycle level shows that `T_0` is too coarse
to support closed macro-dynamics on the same packaged future. This obstruction is therefore a **positive
certificate** that the packaged-object theory is not already contained in the base theory."*

Evidence table (lines 746–764): non-factorization rate **0.833**, P4←P5 forcing **36/36**, **Inadmissibility 36/36**,
saturation panels 8/9 (shell). The obstruction being global is the SUCCESS condition.

### 2.4 ⚠️ THE INVERSION — this corrects BOTH my toy and my relic spec

- **The macro-admissibility OBSTRUCTION is the CERTIFICATE, not a "bust".** My quarantined relic spec
  (`TRUE_STRICT_EXTENSION_SPEC.md`) read "Inadmiss. 36/36" as a **bust** ("distinguishes nothing", to be
  *overcome*). The paper says the exact opposite: that inadmissibility is the **positive certificate** that the
  base cannot express the packaged structure. The relic inverted the success signal into a failure. (Another
  reason it is quarantined.)
- **My inject-and-recover toy chased the literal NEGATION of strict extension.** Recovery (`macro_gap` matches the
  known gap) = the base CAN express the packaged value = **lumpability = admissibility = factorization** = the
  opposite of the certificate. A strict extension requires the macro **NOT** to lump/recover from the base. I was
  computing the anti-certificate and calling it a milestone.

### 2.5 Honest scope of even the cleanest case (load-bearing for the proton question)

The Cantor paper's *consequence* of the strict extension is **NOT a clean scalar value separation** — it is a
**conditional pressure disintegration** over packaging fibers (theoremlet iv, §769+), and the discussion records
that *direct stratumwise root/value separation is NOT achieved* (parked as future work). So even the cleanest
proven strict extension yields **structural** non-factorization + a thermodynamic deficit object, **not** a clean
emergent scalar. ⇒ Reading a scalar VALUE (a mass) off a strict extension is *beyond what the corpus proves*.
This sharpens the central open question for the lattice/proton goal → `04_THIS_PROJECT_AND_OPEN_QUESTIONS.md`.

---

## Part 3 — How a VALUE legitimately descends from a strict extension (grounded in SAU / Why Mathematics Even Works)

*Deep-read of `Why_Mathematics_Even_Works.tex` §"Descent, non-descent, strictness" + §"The SAU certificate"
(lines 522–660).* This is the THIRD pillar: the landing discipline — the only register in the corpus that
produces a **lower-layer answer (a value)** out of a strict extension. Exactly what the proton goal needs.

### 3.1 The two arrows as defects (descent vs strictness)

- **Descent** `F↓_q`: the promoted update `F` has a lower shadow `F^♯` with `qF = F^♯q` (commuting square, line 533) —
  the "down/shadow" arrow, derivable/checkable (primer §6).
- **Strictness** `δ_fact(π_0,π_1) ≠ ∅` (lines 550–554): *"pairs of compared states with the same lower view under
  `π_0` but different promoted views under `π_1`. A promotion is STRICT when this set is nonempty."* = the
  non-factorization of Parts 1–2, as a concrete defect set.
- **Non-descent** `U ↛_q` (Def, line 563): the promoted datum `U` itself is **not** acceptable as a lower-layer
  object (`ε∉ℝ`, `α∉K`, a datum that fails to glue — or for us, a full packaged macro object/wavefunction).

### 3.2 The SAU certificate, shortest form:  `U ↛_q ,  C(U) ↓_B a^♯`

Posit a **non-descending object `U`** (the "imaginary-number move"); a **selected expression `C(U)`** formed from
it **descends, with audit, to a lower answer `a^♯`** (Def, lines 584–650). Six typed fields (lines 609–650):
1. **Saturation** of the lower profile;
2. **Strictness** `δ_fact(π_0,π_1) ≠ ∅` (genuine non-factorization);
3. **Non-descent** `U ↛_q`;
4. **Audited descent** `C(U) ↓_B a^♯` (coefficient / standard-part / invariant / **trace · norm · root** /
   obstruction-class descent);
5. **Problem-resolution** `a^♯ ∈ Ans_0(P)` (valid lower answer, passes the defect threshold);
6. **Audit / no-overread / no-smuggle**: `δ_overread = ∅`, `δ_nosmuggle = ∅`, `δ_audit = ∅`, gate passes, explicit
   nonclaim record.
Witnesses: `i` (`iz` non-descends, `(iz)²` descends), dual numbers/jets (`[ε]f(x+ε)=f'(x)`), Galois (`α∉K`,
`Tr/Nm∈K`), graph cohomology (`[a]∈H¹`).

### 3.3 THIS is how a mass could legitimately be a six-birds value — and why my toy was illegal

A mass-gap value would be the **descended answer `a^♯ = C(U)`**, where `U` = the non-descending packaged macro
object (which you do NOT literalize), and `C(U)` = the selected invariant that descends — a **decay-rate root /
mass gap** (audited-descent type "trace/norm/root"). Lawful only if ALL six fields hold — crucially **strictness**
(`δ_fact ≠ ∅`, Part 2's non-factorization) **and no-smuggle/no-overread**.

> **My inject-and-recover toy violated field 6 (no-smuggle) and field 2 (strictness):** injecting a known operator
> and reading its gap back **smuggles** the answer through the bridge (`δ_nosmuggle ≠ ∅`), and the gap **factored**
> through the operator (`δ_fact = ∅`, not strict). That is a **counterfeit SAU** (the paper names "Counterfeit SAU
> patterns", line 1442). A real landing needs a genuinely non-descending `U` and a `C(U)` whose value is NOT
> inserted by the construction, validated out-of-sample (§1.6).

---

## Part 4 — The guards (what makes a claimed strict extension HONEST)

*Grounded by my own direct reads (2026-06-18) of `Six_Birds_No_Go_Theorems_for_Audited_Emergence.tex` (8 theorems,
§Main-Results lines 364–465; proofs §closure 671–810, §bounded-interface 898–965) and
`Six_Birds_Foundations_III...tex` (Thm 8 line 3099, Thm 9 3158, Thm 12 3290, Thm 13 3338, Thm 14 3372, Thm 19 4102,
Thm 23 4396). These are the theorems that stop a non-emergent thing being called emergent, or a non-strict extension
being called strict. A strict-extension claim is HONEST only if it clears every guard below.*

### 4.1 The POSITIVE guard — strictness IS a finite, exhibitable non-factorization defect (Found III Thm 12–13)

**Thm 12 (StrictExtensionNonfactorization), line 3290:** for finite object maps `π₀:S→O₀`, `π₁:S→O₁`,
> `π₁ ⋪ π₀` (no `φ` with `π₁=φ∘π₀`)  ⟺  `∃ s,s'∈S : π₀(s)=π₀(s') ∧ π₁(s)≠π₁(s')`.

**Thm 13 (FactorizationDefectEquivalence), line 3338:** with `Δ_fact(π₀,π₁) = {(s,s') : π₀(s)=π₀(s') ∧ π₁(s)≠π₁(s')}`,
> `Δ_fact ≠ ∅  ⟺  π₁ ⋪ π₀`, and the **strictness gate `G_strict = strict_pass` exactly when `Δ_fact ≠ ∅`**.

This is the exact `δ_fact` of Part 3 (SAU) and the non-factorization of Parts 1–2, now as a **finite check on `S×S`**.
**The guard:** a strict-extension claim is honest only when you can EXHIBIT a witness pair `(s,s')` — same base view,
different extended view. No witness pair ⇒ it factors ⇒ not strict. (My dead toy had `Δ_fact=∅`: the gap factored.)

### 4.2 The crux caveat — strictness is NECESSARY, NOT SUFFICIENT (Thm 12 Consequence, line 3334)

> *"Strictness does not imply closure (NC-10) or drive (NC-11); the theorem records only the nonfactorization
> equivalence ... and the no-go countermodels of Section 9 supply finite explicit instances in which strictness
> coexists with absent macro closure or absent drive certificates."*

**Load-bearing for this project:** a `Δ_fact` witness alone gives you a *strict distinction*, NOT a closed macro law,
NOT a directed arrow, and **NOT a value**. Closure, drive, and any landed scalar each need their OWN separate
certificate. So "we found an obstruction/non-factorization" is the *first* gate, never the whole result.

### 4.3 The closure-deficit obstruction — the exact, computable macro-admissibility quantity (No-Go NG_MACRO_CLOSURE_DEFICIT; Found III Thm 8, line 3099)

For micro chain on `X`, packaging `Π:X→Y`, lag `τ`, with macro loss `L_τ(K)=Σ_x μ(x) D_KL(p_x^τ ‖ K(Π(x),·))`:
> `CD_τ(Π) = min_K L_τ(K) = I(X_t ; Y_{t+τ} | Y_t)`, attained by the best macro kernel `K*(y,·)=Law(Y_{t+τ}|Y_t=y)`;
> and `CD_τ(Π) > 0` **iff** two positive-mass micro states in the same fiber have different future laws
> (`p_x^τ ≠ p_{x'}^τ`).

This is the **macro-admissibility OBSTRUCTION of Part 2 made a computable number**: the base lens is too coarse to
close the packaged future *exactly when* `CD_τ>0`. It is the same object as the event-package's structural deficit
and the Cantor inadmissibility certificate. **The guard:** a *fitted* macro kernel is a diagnostic, never theorem
evidence for closure (No-Go remark, line 422); closure holds only at `CD_τ=0`, and `CD_τ>0` is the positive
obstruction certificate — NOT a defect to drive to zero (driving it to zero = recovery = the negation of strict
extension, the §2.4 inversion).

### 4.4 Saturation + bounded interface — why a FIXED lens cannot ladder (No-Go NG_LADDER_IDEM / NG_LADDER_BOUNDED_INTERFACE; Found III Thm 11, Thm 14 line 3372)

- **Idempotent saturation:** `e∘e=e ⇒ e^{∘n}=e` — a fixed package stabilizes after ONE step (No-Go Lemma 911–913).
- **Definability = factorization, and it is finite:** `Def(f)={g∘f}` and **`|Def(f)| = 2^{|im(f)|}`** (No-Go 347–357;
  Found III Thm 14, bijection proof 3388–3400). Hence **no infinite strictly-increasing ladder on a fixed interface**.

**The guard:** open-ended strict growth REQUIRES changing the interface / package / host — it cannot come from
iterating a fixed completion or "looking harder" at the same lens (Found III Thm 14 Consequence, 3408: *"strict
promotion is recorded as an interface change rather than as theory growth at fixed interface"*). This is the
code-level statement of Part 1 §1.4 (emergence = package change, not iteration).

### 4.5 The arrow / drive guards — no manufactured directionality (No-Go theorems 1–4)

- **NG_ARROW_DPI** (line 367): observed arrow `A_T(μ,K;f) ≤ A_T(μ,K)` — deterministic coarse-graining/observation
  **cannot increase** the forward–reverse path-KL. No manufacturing an arrow by coarse-graining.
- **NG_PROTOCOL_TRAP** (line 379): stationary + detailed balance ⇒ `P_T = P_T^rev` ⇒ **observed arrow = 0 even with
  hidden protocol coordinates**. Hidden protocol/order structure alone is not entropy production. *(This IS the
  protocol-trap false-positive control.)*
- **NG_FORCE_FOREST / NG_FORCE_NULL** (391, 403): on forest support every antisymmetric edge form is
  potential-generated and all closed-walk sums vanish; an exact log-ratio 1-form has zero cycle affinity. **No
  force-like drive without genuine cycle support / non-exactness.**

### 4.6 The audit guards — sound promotion, no over-reading, no self-certification (Found III Thm 19–25)

- **Thm 19 (PromotionGateSoundness), 4102:** an `accepted`/`strict`/`non_strict` verdict ⟺ **every required core gate
  exists and passes**. A promotion verdict is *exactly* the gate-passing condition, never informal. (Thm 20/21: strict
  promotion ⟹ nonfactorization; non-strict ⟹ factorization.)
- **Thm 23 (NoOverreadingSuppression), 4396:** an accepted claim has `δ_overread=∅` — it may use only
  instrument-visible content, or suppressed content **bridged** by an admissible visibility bridge. No leaning on
  hidden/suppressed content (even if that content is correct). This is the `δ_overread`/no-overread guard of SAU field 6.
- **Thm 24/25 (same-level self-audit failure / finite rotating audit):** no instrument certifies its OWN complete
  soundness; auditing needs a strictly higher instrument, and there is **no self-certifying top**. Guards against
  circular self-validation (the in-sample-circularity failure mode, Part 1 §1.6, in typed form).

### 4.7 The negative-form guards — the countermodel atlas CM1–CM12 (Found III §9)

Twelve explicit finite countermodels, each blocking one overclaim: package⇒closure (CM1), holonomy⇒drive (CM2),
local⇒global (CM3), cell⇒pair-realness (CM4), finer⇒better-closure (CM5), self-audit-circularity (CM6),
strictness⇒closure (CM9), strictness⇒drive (CM10), fallback-as-real-source (CM11), gating-removes-only-irrelevant
(CM12), … . These are the concrete witnesses behind §4.2: each is a finite scenario where a tempting inference fails.

### 4.8 How these realize the event-package false-positive controls (the applied guards)

The genuine worked example (`03 §D`) runs exactly these as interventions on a candidate obstruction (Locally-Boolean
paper Thm 6, protocol-trap exclusion): **protocol-trap** ↔ §4.5 NG_PROTOCOL_TRAP (+Thm 23); **flattening/completion**
↔ is the obstruction a removable confluence/holonomy defect; **hidden-record** ↔ §4.6 no-overread (does it vanish when
hidden residue is made record-admissible); **noise** ↔ object-preserving robustness. An obstruction counts only if it
SURVIVES all four (`interventions/{flattening,hidden_record}.py`, `robustness/noise_runner.py`).

> **Part 4 bottom line:** an honest strict-extension claim must (1) EXHIBIT `Δ_fact≠∅` (a non-factorization witness),
> (2) carry its own closure/drive/value certificates separately (strictness alone gives none — §4.2), (3) show the
> obstruction is a real `CD_τ>0` (not a fitted-kernel artifact), (4) not rest on a fixed-lens iterate ladder, a
> manufactured arrow, suppressed content, or self-certification, and (5) SURVIVE the four false-positive controls.

---

## Part 5 — The Ξ adequacy register and its TRUE role (measuring/dissolving, NOT value-generation)

*Grounded by my own direct reads (2026-06-18) of `Adequacy_Residuals_and_Blind_Spot_Currency.tex`
(def:adequacy-residual line 436, thm:exact-adequacy 628, thm:chain-rule 793, cor:same-family-saturation 846,
thm:blind-spot-witness 1135) and `Emergence_IS_the_Needle_Killer.tex` (thm:layer-dissolving-master 975,
thm:strict-extension-repair-contraction 1619). NOT via codex — I read these.*

### 5.1 What Ξ is — the factorization residual in the currency register

`Ξ_C(D∣L) = K_DD − K_DL K_LL^† K_LD` — the **Schur complement** of the native block in the joint currency matrix,
where `K_FF = F₀ C₀⁻¹ F₀*` is the audit-energy Gram ("currency") of a probe family, `L` = measurements at the
**original/lower** layer, `D` = measurements at the **richer/higher** layer. Ξ is the leftover dissolving currency `D`
that `L` **cannot explain**. (def 436.)

### 5.2 Ξ = 0 is EXACTLY factorization (the unifying identity)

**Exact adequacy (Thm, line 628):** the following are equivalent: `Ξ_C(D∣L)=0` ⟺ `D₀ = A·L₀` for some linear `A`
⟺ `Ker L₀ ⊆ Ker D₀` ⟺ `D` factors through `L` (Douglas range-inclusion). So **Ξ is the linear/currency-register
measure of NON-FACTORIZATION** — the very same phenomenon as `Δ_fact≠∅` (Found III Thm 13, §4.1), `CD_τ>0` (closure
deficit, §4.3), and `δ_fact≠∅` (SAU, Part 3). Four registers, one obstruction: set-maps, information, currency, SAU.

### 5.3 Ξ's direction is DOWNWARD: it prices a lower obstruction and tracks its DISSOLUTION

- **Chain rule (Thm 793):** enlarging the native family `L→L⁺=[L;M]` can only **shrink** Ξ:
  `Ξ(D∣L⁺) = Ξ(D∣L) − K_{DM∣L}K_{MM∣L}^†K_{MD∣L} ⪯ Ξ(D∣L)`, with strict contraction "exactly in the directions seen
  by the new probes."
- **Same-family saturation (Cor 846):** if the added probes are redundant (`M=BL`), **Ξ is unchanged**. Only a
  **genuine** enlargement (`K_{MM∣L}≻0`) contracts Ξ — the no-smuggling guard.
- **Layer-dissolving master theorem (Needle-Killer, 975):** a lower-layer "needle" (obstruction) is **priced** by
  native + residual currencies (`K^L_j`, `Ξ_j`) and that price is **transported** upward; if the higher-layer budget
  covers it, the obstruction **dissolves** — "no layer-dissolving predictive needles within the declared scope."

So Ξ is an **audit/pricing instrument in the descending direction**: "can the richer layer account for / dissolve the
lower obstruction?" Its output is a **PSD residual operator (a budget/price)** — *never a scalar physics value*.

### 5.4 How Ξ certifies a GENUINE obstruction — the blind-spot witness

**Blind-spot witness (Thm 1135):** given a declared residual budget `Ω⪰0`, `Ξ_C(D∣L) ⋠ Ω` ⟺ there is an explicit
vector `z` with `z*(Ξ−Ω)z > 0` (max violation `= λ_max(Ξ−Ω)`). An **irreducible** residual — one that cannot be
dissolved within budget by any lawful repair — is a **certified blind spot / genuine obstruction**. The only lawful
repairs (1173, 1604): add genuine native probes (strict native extension), improve the bridge, change the legal
carrier, complete missing transport, or narrow the claim. **"Same-package repetition saturates"** — re-running with no
new probe/audit/transport content cannot change Ξ (the saturation guard again).

This is the discriminator Part 4 §4.2 demanded: Ξ ≠ 0 alone is necessary-not-sufficient. If Ξ **dissolves** under a
genuine bounded enlargement → it was a *dissolvable needle* (under-resolution artifact). If Ξ **stays positive**
(blind-spot witness, irreducible without changing the theory) → a *genuine strict obstruction*.

### 5.5 The verdict — Ξ does NOT generate the value, and this re-indicts my dead toy

**Ξ is a measuring / pricing / dissolution-audit register, not a value-generation engine.** It quantifies
non-factorization and audits whether an obstruction is irreducible; it produces a budget operator, not a mass. A
**value still lands only via SAU (Part 3)**, under the Part 4 guards. Ξ belongs to the AUDIT half (alongside §4.6),
not the value half.

> **This nails why my quarantined step97 Ξ-toy was a false positive:** it used Ξ *as a value-recoverer* (drive Ξ→0,
> read the mass gap back), enlarging the lens to **full rank / the identity** to force `Ξ→3e-16`. But (a) Ξ doesn't
> generate values — it prices obstructions; (b) enlarging to the identity is exactly same-family/descending
> resolution, not a genuine bounded enlargement (`K_{MM∣L}≻0`, `k≪dim`) — the no-smuggling violation; (c) `Ξ→0` means
> the extension **DISSOLVED**, i.e. was *not* strict. Three guards tripped at once. Ξ contraction to zero is the
> ANTI-certificate, exactly as recovery/lumpability is in §2.4.

---

> **Operational understanding now (Parts 1–5 grounded):** strict extension = a non-factoring, non-definable, run-only
> distinction validated out-of-sample (Part 1), constructed via saturation→material P4←P5 forcing→macro-admissibility
> OBSTRUCTION-as-certificate (Part 2), from which a value may descend ONLY via an audited SAU landing (Part 3); a claim
> is HONEST only if it clears every Part-4 guard (strictness is necessary, not sufficient — §4.2); and Ξ is the
> downward audit/pricing register that measures the obstruction and its dissolution (Part 5), NOT a value engine.
> **The four registers of the one obstruction:** `Δ_fact≠∅` (set), `CD_τ>0` (information), `Ξ⋠Ω` (currency),
> `δ_fact≠∅` (SAU). Six Birds maps and audits the rung; it does not derive the content.

> Operational understanding now (Parts 1–4 grounded): **strict extension = a non-factoring, non-definable, run-only
> distinction validated out-of-sample (Part 1), constructed via saturation→P4←P5 forcing→obstruction-as-certificate
> (Part 2), from which a value may descend ONLY via an audited SAU landing (Part 3) — and a claim is HONEST only if it
> clears every Part-4 guard, remembering strictness is necessary, not sufficient (§4.2). Six Birds maps and audits it;
> it does not derive it.**

---

## Part 4 addendum — the hidden-record / no-overread control discipline (adjudicated 2026-06-19)

A hidden-record control may expose ONLY records that **factor through the context's own carrier** — it may NOT inject a
quantity from a richer context. For the branchwise quotient `K`, a record is admissible only if it is **branch-local**
(≤1 branch, pre-recombination, stable under the branch predictive equivalence; NO loop-closure / singlet / joint-pairing
/ slab-composition / holonomy). Exposing a **joint / recombination-level** quantity (e.g. a Wilson loop) to the
branchwise `K` is **CURRENTIZATION** (`K → K^W=(K,W)`), **NOT** artifact removal: it tautologically separates the
witness because `W` is the very observable that distinguishes the `R`-classes. (Holonomy paper distinguishes
currentization — a real predictive distinction becoming current-visible under a richer interface, still genuine — from
artifact removal, where the distinction was never there.)

**"Physically accessible on a finite classical substrate" is NOT the criterion.** Every function of a finite microstate
is mathematically accessible, but that does not make it a current observable of every context (the substrate-omniscience
reduction is excluded; Hiddenness: current observables are *declared, stage-available, audited*). The criterion is
whether the quantity **factors through the admissible package** of the context exposing it. No-overread (primer): do not
read an `R`-level joint observable as a `K`-level independent-branch record.

So a `K`-equal/`R`-distinct obstruction collapses LEGITIMATELY only if the recombination distinction *factors through a
SATURATED branch-local `K`* (admissible per-branch transporters jointly determine it) — proven by factorization, never
by inserting the joint answer into `K`. *(This corrected step107c's invalid `artifact` verdict — the implemented
hidden-record control exposed the joint ℤ₂ holonomy to the branchwise `K`, i.e. currentization. See manager_log; the
repaired test is step107d's K-saturation crux.)*

**Refinement (round-3 adjudication, 2026-06-19): admissibility is EQUIVARIANT, not gauge-invariant-only.** A gauge-
COVARIANT branch object (e.g. an open transport `u_a` transforming as `u_a ↦ g_out·u_a·g_in⁻¹`) MAY enter the branchwise
`K` — but only carried as a `G_∂`-typed (boundary-gauge-groupoid) object with its representation explicit, NEVER as an
untyped gauge-fixed scalar or a hashed frame coordinate. The legitimacy test for a recombination factorization is an
EQUIVARIANT map `Φ: K_cov → R` whose commuting square holds for EVERY admissible boundary frame (a chosen frame may be
used to compute, but the result must be frame-INDEPENDENT). Three record types: **gauge-invariant scalar** (enters `K`,
ordinary equality); **gauge-covariant branch state** (enters `K`, carry its boundary representation); **frame-coordinate
value** (NOT an intrinsic class — quotient by frame changes or prove equivariance). *(step107d hashed a post-freeze
`frozen_boundary_frame` coordinate + organizational labels ⇒ it proved factorization through a FRAMED `K^F`, not the
gauge-invariant package; a frame-reorientation + label-erasure audit is owed = gate 0 of step108b.)*

**THE SATURATED-K RULE (round-4 adjudication, 2026-06-19) — define K EXTENSIONALLY, not from a field list.** The
permanent fix for the recurring "what's admissible in K" family: `K` is the **exact one-branch predictive quotient `M`**
(Holonomy `≡pred`, restricted to ONE-branch continuations/events), computed by **partition refinement to a fixed point**
— NEVER a hand-chosen tuple of fields. (Marking: `K` = the label-erased weighted multiset of those `M`-classes.) The
implementation encoding `E_a` is admissible iff **`ker E_a = ker q_{M_a}`** — BOTH directions: no **under-saturation**
(`E equal ⇒ M equal`; else `K` too coarse — e.g. step108b omitting the per-line current) AND no **overread** (`M equal
⇒ E equal`; else a distinction not licensed by independent branch prediction — e.g. step107d's frame coordinate). A
field `r_a` may encode `M_a` only if: (1) stage before recombination/slab; (2) dependency cone touches ≤1 branch; (3) no
dependency on a joint pairing / loop closure / singlet / `R`-class / `T`-composition; (4) predictive-measurable
(`r_a = r̄_a∘q_{M_a}`); (5) gauge-natural (invariant, or covariant in a declared rep `ρ_a` — NOT a raw frame
coordinate); (6) permutation-natural; (7) licensed provenance (frozen grammar / one-branch bridge, in-budget, no
`R`/held-out/scalar taint). A joint `Φ: K_sat → R` may then TEST factorization; its output is NEVER inserted back into
`K`. **This single rule `ker E = ker M` would have caught all four of 107c / 107d / 108 / 108b.**

**THE CONDITIONAL-GAUSSIAN NO-GO (round-5 adjudication, 2026-06-19) — a bilinear carrier cannot host a two-line
obstruction above a complete one-body kernel.** A structural strict-extension theorem, not a toy failure: for any
**bilinear** (Gaussian) fermion action `S_F = ψ̄ D[U] ψ`, the fixed-background generating functional is
`det D[U] · exp(η̄ G[U] η)` with `G[U] = D[U]⁻¹`, so EVERY fixed-background `2r`-fermion boundary tensor is a
determinant/minor of the COMPLETE one-line kernel `G[U]` (Wick). Hence if two configs share the complete per-background
one-line kernel — `A¹_U(B) = A¹_U(B')` for every `U` — then `A²_U(B) = det A¹_U(B) = det A¹_U(B') = A²_U(B')` for every
`U`, and the gauge averages coincide too. **No `(B,B')` can be saturated-`K`-equal yet two-line-distinct when the carrier
is bilinear.** This holds for U(1), SU(2), SU(3) — any bilinear action (step108d hit it). The only "evasions" all change
the construction (average `A¹` before `K` = coarse-`K`; keep selected entries = under-saturation; change the gauge
measure/topology between `B`,`B'`; add a four-fermion interaction = change the theory; omit a boundary mode). **The
consequence is a typing fact about where strict extension can live:** a genuine `K`-equal/`R`-distinct obstruction needs
a carrier whose joint response is NOT a function of the complete one-branch kernel — i.e. **multiple recombination
channels at identical one-branch content** (gauge intertwiner recoupling), which is the Marking-paper `R≄K` structure, not
a fermion determinant. A determinant residue is never a witness; a multi-channel intertwiner residue can be.

## Part 4 addendum — the genuine-ENGINE gates (round-5-redo adjudication, 2026-06-19): running the real engine is necessary, NOT sufficient

Context: the whole step107–111 line hand-coded bespoke K/R quotient drivers and **never invoked the real `sixbirds_event`
engine** (the *Locally Boolean, Globally Obstructed* worked example, 03 §D), drifting into a determinant → intertwiner →
bosonization → cross-scale toy cascade that reframed KNOWN results (standard SU(N) recoupling; standard bosonization
1/√π). The reset re-anchors on the real engine. The adjudication that resolves it: a real `sixbirds_event` verdict
(`accepted_proposal_obstruction` from `audits/quotient_feasibility.py` — quotient classes from common-trajectory joint
signatures across contexts; surviving classes must respect every accepted shared-event identification AND cover every
atom) establishes a genuine global-packaging obstruction **only relative to the supplied support + accepted identities**.
Being the real engine does NOT certify any of the following — each is a SEPARATE gate, and a claimed mass landing must
clear all of them (this is §4.2 "strictness necessary-not-sufficient", made operational for the engine run):

1. **Non-descending support (CRUX 1).** The engine's "trajectories" must be canonical UNFINISHED boundary-record
   histories — interior integrated EXACTLY by *local compositional* rules (Berezin + character/Weingarten), fibers ERASED
   (no context, shared-event inference, or quotient backend may query an interior/worldline/contraction-graph/
   gauge-background/solver-branch representative). "Exact local elimination" and "full-resolution traversal then forget"
   can return the same boundary table — only the former is non-descending. Full enumeration is allowed ONLY as a tiny
   comparator, never as the support producer. Mandatory provenance statement in the run artifact, mechanically enforced.
   Also: `quotient_feasibility` bare-INTERSECTS trajectory IDs, so contexts must share a canonical COMMON support
   (`S_K=S_G=S_R=S_T`; cross-depth `c_T` needs a genuine projective/cylinder support, not coincidental ID collision) or
   the quotient classes are not candidate global atoms of one package.

2. **Lawful shared-event identities.** Each accepted identity must carry an EXACT bridge-law certificate (`L_read` /
   `L_quad` (Osterwalder–Schrader reflection positivity) / `L_trans`), and exact coefficient/weight disagreement must
   VETO an identity even when probe-image atom-sets coincide — else a false empirical identity manufactures the
   infeasible quotient. (Verify-during-impl: the engine's `structural_primary` policy may accept on probe-image match
   without requiring exact consistency; if so, harden it.) Probe-family separation: `P_EI ∩ P_MBO = ∅` (identity-inference
   probes ≠ the held-out continuations used for mass-bearingness).

3. **Non-vacuous controls.** Every applicable false-positive control (decoupled / `R=K` / protocol-trap / flatten /
   hidden-record / noise; §4.8) must RERUN the full pipeline (boundary carrier → package actions → shared-event inference
   → quotient ledger → feasibility), NOT reuse a cached obstruction flag while perturbing only observation traces. The
   round-2 currentization rule (Part 4 addendum above) stays binding: a hidden-record control exposes only a licensed
   pre-recombination stable record, never an `R`/`T`-level joint result to `K`.

4. **Projective MBO (mass-bearing — refines SAU field 4, Part 3).** A genuine obstruction need NOT bear the mass. Let
   `α_W` collapse the distinctions forced by the (predeclared) obstruction component `W`. Mass-bearing requires that the
   held-out **projective temporal law** `D_H` (the decay-sector / shift-orbit of `Ĉ_H(n)=r_H(T_H^n s_H)`, with overall
   amplitude QUOTIENTED OUT) does NOT factor through `α_W`: `∄ D̄_H : D_H = D̄_H∘α_W`. An obstruction that changes only a
   correlator AMPLITUDE (`Ĉ'=A·Ĉ`, same decay exponent) FAILS — it affects overlap, not mass. Equivalently, ablation must
   break representative-independence of `T_H`, or change the held-out shift/recurrence/pole-sector, or merge states with
   non-proportional future-response streams. Predeclare `W` (a minimal infeasible-subset component) BEFORE seeing
   transport; never cherry-pick the witness that happens to move the channel (no-fitting).

5. **Weighted-carrier reconnection (structural shadow vs value register).** The engine substrate is a row-stochastic
   Markov kernel; a Euclidean boundary carrier has weights (Berezin/character, possibly signed) the kernel discards. The
   obstruction engine may operate on the structural shadow, but **promotion must reconnect the shadow to the exact
   weighted carrier** (composition product + norm/normalization + any multiplicative weight cocycle across slabs) WITHOUT
   adding answer-bearing information later. Ξ stays the downward audit (Part 5), never the value generator.

**Go/no-go order (R0–R7), the operational form of "obstruction first, value last":** R0 substrate provenance (unfinished
boundary carrier; no precomputed context labels / obstruction) → R1 engine-executed provenance-recorded package actions
generate `c_K,c_G,c_R,c_T` → R2 exact bridge-law certificates → R3 `accepted_proposal_obstruction` (real engine) → R4
non-vacuous target controls (decoupled/`R=K` packageable; interventions don't remove it) → R5 promotion (representative-
independent weighted slab transport) → R6 projective MBO on the predeclared component → R7 SAU (root frozen, evaluated
out-of-sample, sealed benchmark opened last). Authority = the papers + the running engine code, never a synthesis.

> ⚠️ **THE UNIVERSALITY AXIOM (user, binding, 2026-06-20) — a feasible packaging is NEVER a result.** Six-birds is
> UNIVERSAL: all emergence and all reality happens through it; the hadron, the mass, the new layer DO arise as a six-birds
> strict extension; nothing escapes it. Therefore a `feasible`/`globally_packageable`/"this does not obstruct" verdict at
> any gate is **NOT a result and NOT a foreclosure** — it is an admission that *we built the wrong setup* (the one that
> exposes the obstruction has not yet been found). Never report it as a negative, a wall, a limitation, or "an acceptable
> doors-not-walls outcome" (that earlier framing is RETRACTED). The task is always to FIND the setup that GENERATES the
> strict extension. A feasible verdict redirects the construction; it never ends it.

## Part 4 addendum — the NINE semantic gates against the currentized-null trap (round-6 adjudication, 2026-06-20)

A real engine returning `feasible` proves nothing if the EventPackageInstance was a **currentized null** — a degenerate
instance feasible by construction. This happened (step113/114): every context atom appended the FULL common refinement
(`focus + "__refines__" + <full join>`), so the four contexts were ONE member-partition under four names ⇒ the common
partition is itself the global filler ⇒ feasibility guaranteed; and the glue was EXTENSIONAL (events identified only when
their carrier-member preimages were equal), never the paper's EMPIRICAL identity (events identified when downstream
PROBES can't distinguish them, even at *different* support preimages). The manager audit missed it by checking atom-id
LABEL distinctness, not member-PARTITION distinctness. The structural-strictness, no-overread, etc. guards (§4.1–4.8)
are necessary but did NOT catch this; these nine gates do, and bind every carrier→event-package mapping:

1. **P5 execution** — every context atom has an executable package-ACTION trace (the step106 `apply_context_action`
   completion genuinely run), not merely a `package_action` label. (Named-not-executed = the root cause.)
2. **No universal refinement** — the four context member-partitions are NOT all identical as partitions of the carrier
   support. (Check member-partitions, NOT atom-id strings.)
3. **No cross-context taint** — a `c_K` atom key has no dependency on `c_G/c_R/c_T` outputs (and symmetrically); a context
   key is a function of its own action only.
4. **Context-local erasure** — distinctions a context's action ERASES do not survive in its atom IDs, labels, or equality
   keys (provenance lives in an audit sidecar, never the atom key). Each completion must genuinely forget what it drops.
5. **Nontrivial empirical identity** — ≥1 accepted shared-event proposal has UNEQUAL support preimages
   (`λ_c⁻¹(E) ≠ λ_d⁻¹(F)`) yet equal exact licensed bridge-probe vectors (`σ_read/σ_quad/σ_trans`). An instance whose
   every accepted identity has equal preimages is an EXTENSIONAL NULL, not an obstruction test.
6. **Material c_T** — `c_T` is generated by ACTUAL slab composition along both routes (glue-then-integrate vs
   package-then-compose), not by classifying members with a constant depth/parity string.
7. **Full frozen support** — pruning for tractability must not remove ALL variation of a named context (e.g. a single
   flux sector makes `c_G`/`c_T` constant). Keep the seam/flux/composition variation a real context needs.
8. **Quotient decisiveness** — for a same-support claim the verdict comes from the `quotient_feasibility` audit (the
   paper-decisive backend); the full-product `structural_exact` solver is a small-instance comparator only.
9. **Control-path equality** — coupled, decoupled, `R=K`, hidden-record, flattening, noise all traverse the SAME
   carrier → P5-actions → bridge-probes → shared-event-inference → quotient-audit pipeline (no cached verdicts).

> The obstruction lives in the **incompatibility of the actual P5 completion actions over the same unfinished boundary
> material** (the glue-then-integrate-seam vs package-separately-then-compose square), exposed when bridge-law EMPIRICAL
> identities crosscut the boundary support so no quotient family covers every context atom. It is never a static field of
> one carrier row, and a `feasible` verdict on a currentized null says nothing about whether it is there (it is — find the
> setup that exposes it).

## Part 5 — TRANSPORT-NULL vs MASS-BEARING: the GROUNDED finding (round-8); the build-recipe is an UNVERIFIED external proposal

Only the GROUNDED finding belongs here (this file's contract). TRIAGE of the round-8 advice, done against the papers (Holonomy w/
Memory; Promotion_Criteria / Carrier_Exactification / Carrier_to_Event / Internal_Structure; Why-Math SAU; Locally-Boolean):
- **GROUNDED FRAMEWORK** (the advice is a correct re-derivation of the already-grounded `04 §8` route applied to the transport-null
  finding — NOT new, NOT "over-engineering"; an earlier note here mislabeled it and is corrected): `U_pkg` = the promoted package
  carrier (fixed-support series); `M_H` = the future-predictive quotient (Holonomy `M`, ≡pred); `U_H = Exactify(U_pkg ×_{Q_H} M_H)` =
  the categorical form of `04 §8`'s `U_H` (combine the event package `𝓔_H` + the predictive quotient `M_H` over the current quotient
  `Q_H`); native transport `T^{U_H}` + the `P_{n+1}` fixed-point refinement = Holonomy predictive transport + the saturated-K
  partition-refinement discipline (Part 4 round-4); the six promotion gates = Promotion_Criteria; the 3-gate MBO = the exact-
  factorization sharpening of the grounded projective-MBO gate (Part 4 value-gate-4 / `04 §9`); the `−log(ρ_H/ρ_0)` native-transport
  root + vacuum carrier + root-last = `04 §8`'s `C(U_H)=m_H` + Part 3 SAU; the sealed comparator + out-of-sample = the SAU discipline.
- **DESIGN HYPOTHESIS TO TEST** (frame-consistent, NOT yet a cited theorem — held exactly as the whole `04 §8` route was, a premise to
  test with the REAL engine, repaired if it fails): the **mixed-law obstruction CYCLE** (a network of locally-lawful identities —
  `L_read` current / `L_quad` recombination / `c_G` gauge / a `c_T` continuation that can't descend — globally incompatible, forcing a
  predictive distinction) and the **two-interface `(D1⋆D1)⋆D1`** locus, as the way to get non-packageability AND a future distinction
  at once. (A single current-only identity may be packageable or non-predictive — the cycle is needed to get both.) Tracked in `04 §9`
  / `manager_log.md`; tested by construction, not asserted.

**The grounded finding (verified by me + by step116a):** a genuine, control-surviving event-package obstruction (step115e) can
still FAIL the mass-bearing gate.
- **What was computed:** for each accepted step115e witness identity `E_K ~ E_T`, splitting the conjoined response by law shows
  `L_read` and `L_trans` are *each* exactly equal, so the complete open-boundary transport tensors agree: `B₂(E_K) − B₂(E_T) = 0`
  (verified; all 6 identities; composition-stable under depth-1 gluing computed from the step112d records — step116a).
- **Why that fails MBO (grounded in Part 4 §"Projective MBO" / 04 §9):** the MBO gate requires the held-out projective temporal law
  `D_H` to NOT factor through the ablation `α_W` of the witness-forced distinctions. When `B₂(E_K)=B₂(E_T)`, the two events give the
  *same* response under **every** continuation (gluing is linear in `B₂`), so any held-out continuation agrees and `D_H` factors
  trivially. The witnessed distinction is **transport-null**; ablating it changes no future response ⇒ it cannot change the decay
  LAW ⇒ this obstruction does not bear the mass through this witness. (The held-out depth-4 was vacuous: the tomographically-complete
  `L_trans` signature already determined it.)
- **The grounded DIRECTION for where the mass must live (02 §1.3; Holonomy w/ Memory):** the corpus's predictive-quotient strict
  refinement is exactly "current-equivalent but future-distinct" — `≡pred` strictly refines `≡cur`. A mass-bearing obstruction must
  have that shape (same current view, different future law), NOT an identity that already equates the complete future transport. This
  DIRECTION is corpus-grounded; the specific machinery the advisor proposed for realizing it is the unverified proposal above.

> **The grounded discipline:** an obstruction whose witness is transport-null is still a genuine strict extension — record it
> (`genuine_strict_extension` + `transport_null` + `not_yet_mass_bearing`, step116a), do NOT discard it, and do NOT call it the mass.
> Accepting a transport-null obstruction as the mass would be "a failure dressed up as a success." The next move is to GROUND (against
> Holonomy + the fixed-support series) what a predictive, mass-bearing obstruction actually requires — manager paper-reading — before
> designing or dispatching the next construction step. Do not pre-plan a multi-step cascade off the advisor's recipe.

### Part 5 RESOLUTION (round-9, manager-verified): strict extension lives in the PREDICTIVE register; the event-package is a separate downstream register

The construction (step116b/c) and the round-9 ruling RESOLVE the register question, and it is grounded:

- **Two compatible verdicts, two registers.** step116c: the Locally-Boolean ENGINE returns `globally_packageable` (a static global Boolean realization exists) WHILE the predictive transport on `Q⁰` is OBSTRUCTED (the composition square `Package(S1⋆S2) ≠ Recombine(Package S1, Package S2)` does not commute, discriminated by the decoupled κ=0 control; `M` strictly refines `Q⁰`, 376/188). These are DIFFERENT mathematical questions: a global Boolean package can exist while carrying no well-defined quotient transport.
- **The corpus does NOT require an event-package obstruction for strict extension.** The CANONICAL Cantor certificate (Part 2) IS the macro-admissibility obstruction alone (no event-package). §1.3 lists the registers as distinct faces; the strict-test series is upstream of the event-package series. So `Q⁰ ⊀ M_H*` (no closed transport on `Q⁰`, native closed transport on `M_H*`) IS the strict extension; the engine's `packageable` is the CORRECT static-register verdict. (Universality axiom satisfied: the obstruction WAS found, in the predictive register.)
- **The carrier is `U_H = Exactify(M_H*)` ALONE** (round-9 self-corrects round-8: DROP the `U_pkg ×_Q M_H` fiber-product). Grounded in Carrier_Exactification's minimal-behavioral-carrier / non-reducibility principle: `U_pkg` (packageable, transport-null) is reducible ⇒ drops out. `M_H*` = the FIXED-POINT predictive quotient (the 376 classes are provisional `M^(1)`; refine to a fixed point under the complete frozen continuation grammar).
- **Mass-bearingness is still UNDECIDED (not over-claimed).** Future-distinction (376/188) ≠ mass-change: the witness may differ only in flux sector / source overlap / transient / excited content while sharing the dominant decay root. The gate is the PROJECTIVE MBO on the coarsest carrier preserving the projective hadron transport law (`U_H^proj`, projective equivalence `G_u(n)=A·G_{u'}(n)`): require `U_H^proj → Q⁰` still strict AND dominant-decay-sector essentiality under ablation (not subdominant coefficients).
- **Operationally:** a first-class `predictive_transport_audit` (the strict-test register: Cantor / Holonomy / No-Go Thm 8 closure-deficit) alongside the event-package audit, on the SAME real carrier + engine outputs; the strict result is named `macro_admissibility_obstruction` / `transition_strict_extension`, and the engine's `globally_packageable` stays in the record. NOT a bespoke engine-substitute, NOT the toy-drift anti-pattern (it computes the macro-admissibility obstruction on the real carrier).

> **The grounded resolution:** the strict extension is `Q⁰ ⊀ M_H*` (the predictive/macro-admissibility register, CONFIRMED). What remains is MASS-BEARINGNESS, decided by exactifying `M_H*` to the minimal projective hadron carrier and testing whether its dominant temporal sector still fails to factor through `Q⁰`. Promote the predictive closure already computed; do NOT force the locally-Boolean engine to obstruct.
