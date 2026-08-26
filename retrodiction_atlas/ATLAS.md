# The Six Birds Theory Retrodiction Opportunity Atlas

*A skeptic-calibrated map of what Six Birds Theory (SBT) can and cannot honestly retrodict in physics.*

Author: Fertility Judge / Atlas stage. Date: 2026-06-02. Frozen ledger: `retrodiction_atlas/ledger.json`. Candidate cards: `retrodiction_atlas/cards/<id>.json`.

---

## 1. Methodology note

### 1.1 The three-stage adversarial pipeline

Each of the 32 candidates (`R001`–`R032`) passed through a fixed pipeline whose output is the per-card JSON on disk:

1. **Candidate construction + parameter/overfitting audit.** A retrodiction claim is stated, its theory basis is cited to SBT paper filenames and theorem labels, a minimum-viable proof route is sketched, and every free parameter / auxiliary assumption / imported fact is enumerated. An overfitting auditor counts degrees of freedom against independently-constrained matched data points.
2. **Four-member adversarial skeptic panel.** Each claim is attacked on `is_actually_new`, `beats_baseline`, `imports_known_physics`, `target_used_to_design_theory`, and an `opposite_world` test (would the framework "retrodict" the contrary observation equally well?). Fatal objections are recorded.
3. **Repair + fertility judging.** A repair agent narrows or splits over-claims to their honest defensible core; the Fertility Judge then assigns the ten component scores and the composites, marks `any_fatal`, and writes a verdict.

This Atlas stage consumes the **deterministically pre-computed composite scores** (not recomputed here), reads the top cards and the avoid-list in depth, and synthesizes strategic and audience portfolios.

### 1.2 Composite-score formulas (as supplied)

Ten components in [0,5]: `impact, execution_ease, plausibility, non_ad_hocness, discriminative_power, audience_legibility, precision, robustness, baseline_advantage, publication_potential`. Four composites are derived deterministically:

- **practical_fertility** — weighted toward execution_ease, audience_legibility, robustness, publication_potential (can it be written and read?).
- **scientific_persuasiveness** — weighted toward non_ad_hocness, plausibility, discriminative_power, baseline_advantage (will a hostile specialist accept it?).
- **flagship_potential** — weighted toward impact, discriminative_power, publication_potential (could it headline?).
- **overall_fertility** — the headline blend used for ranking.

Also reported per card: `min_survival` / `mean_survival` (skeptic survival, 0–5), `any_fatal`, `overfitting_risk`, and `opposite_world_elastic`.

### 1.3 Grounding discipline

All claims are grounded against the **frozen Theory Ledger**: the closure-package axioms (`T=(Z,f,Sigma_f,E,A)`), the six closure roles **P1–P6** (operator-rewrite, gating, route-mismatch/holonomy, staging, packaging, accounting/audit), the three certificate families (idempotence defect; path-KL / cycle-affinity directionality; route mismatch), the export interfaces, the **missing interfaces**, and the **23 disclaimers**. Citations use paper filenames plus theorem/section labels; quotes are kept under 25 words.

### 1.4 SBT's self-disclaimers (honored throughout)

SBT explicitly **does not**: derive the Born rule; derive single-outcome collapse or take a stand on ontic-vs-epistemic collapse; select the pointer basis / lens / record algebra (no canonical-lens principle); derive continuum theories, a metric tensor, GR, or Navier-Stokes; rule out a fundamental cosmological constant; treat `Sigma_T`/EPR as physical entropy production (informational proxies only); treat P3 route mismatch as a directionality certificate; or claim a closed macro law when the closure deficit `CD_tau>0`. **Any claim crossing these is treated as ad hoc unless real machinery exists**, and is down-ranked or placed on the avoid-list.

---

## 2. Executive summary

Honestly scored, **SBT retrodicts nothing new.** Every one of the 32 physics-facing results is a **recovery, structural reorganization, or honest negative** of standard mathematics/physics; all empirically decisive content — Born weights, the pointer basis, single-outcome selection, the gauge group, the matter power spectrum, the cosmological measure — is **imported by declaration or explicitly disclaimed**.

What SBT *can* honestly offer is twofold. First, faithful, often Lean-certified **structural normal forms** that re-express textbook facts as instances of a small set of closure primitives. Second, a falsification-first **audit discipline**: no false arrows (DPI), no fake force (force needs positive cycle rank), no claimed closed macro law without checking the closure deficit. The genuine selling point is **cross-domain mechanism reuse**: four mechanisms — *idempotent-packaging*, *route-mismatch*, *audit-DPI / cycle-affinity*, *orbit-descent* — each fire across multiple physics domains, compressing apparently unrelated facts under one move.

**The 3–4 flagship arguments are all structural and disclaimer-respecting:**

- **R001** — collapse as idempotent **P5** packaging closure: dephasing fixed points are exactly the diagonal record-classical states (`thm:dephase`, Lean `dephase_idem`/`dephase_fixed_iff_exists_diagonal`). A clean recovery of Lueders pinching / einselection, with pointer-basis selection correctly flagged as the named repair frontier.
- **R028** — one coarsening-monotone **audit contract** recovers the classical path-KL data-processing inequality (Lean `tvdist_pushforward_le`) and the quantum relative-entropy DPI under one law.
- **R027** — one sign-free **route-mismatch** scalar recovers the LES subgrid stress, the quantum dephasing-vs-unitary defect, and a scalar backreaction proxy — flagship only as a *unifying diagnostic/taxonomy*, never a physical unification.
- **R024** — a verbatim-verified **honest negative**: SBT contains zero exchange-statistics / spin-statistics / three-generation machinery.

**What SBT cannot honestly retrodict:** any quantitative constant; the Born rule; single-outcome collapse; a preferred basis; dark-energy magnitude; neutrino-sector physics; or anything requiring a continuum / Lorentz / Fock interface. The three numerical-constant cards (R014 EPR closed form, R025 `Omega_Lambda~0.60`, R032 m_nu direction) and any disclaimer-crossing reading are down-ranked or placed on the avoid-list. This Atlas is a credibility map, not a marketing document.

---

## 3. The ranked table

| Rank | ID | Family | Deriv. | Bin | Overall | Mean surv. | Key flag |
|---:|:--|:--|:--:|:--:|:--:|:--:|:--|
| 1 | R001 | low-energy-limit | A | B | 3.09 | 2.88 | Lean-certified (matrix-level) recovery of Lueders pinching; pointer-basis is the repair frontier |
| 2 | R002 | paradox-resolution | B | E | 3.00 | 3.00 | Cat as layer-relative objecthood; load-bearing OI-EI operator lemma unwritten |
| 3 | R024 | constraint-null | E | B | 2.97 | 4.00 | Honest NEGATIVE, grep-verified; documented silence, not a result |
| 4 | R028 | cross-domain-unif. | B | B | 2.85 | 3.00 | Two DPIs under one contract; opposite-world INELASTIC; "one law" is naming |
| 5 | R029 | cross-domain-unif. | B | E | 2.84 | 2.25 | CD_tau recovers lumpability; legs (b),(c) not unified |
| 6 | R016 | uniqueness-necessity | A | B | 2.83 | 2.88 | Dobrushin uniqueness recovery; contrapositive is one line |
| 7 | R015 | uniqueness-necessity | A | B | 2.79 | 2.63 | Schnakenberg + Hodge necessity; sufficiency imported |
| 8 | R020 | symmetry-emergence | C | B | 2.79 | 2.50 | F15a selection no-go (Lean); F15b formation half axiomatizes its conclusion (fatal-if-claimed) |
| 9 | R018 | symmetry-emergence | A | E | 2.69 | 2.13 | Conservation = orbit descent (F27), Noether NAMED; analytic near-tautology |
| 10 | R013 | paradox-resolution | A | B | 2.67 | 3.50 | Three arrow-of-time facts in one package; informational proxy only |
| 11 | R030 | numerical-match (null) | B | B | 2.56 | 2.00 | NULL-CONTROL calibration, not a retrodiction; only content is no-false-positive rigidity |
| 12 | R004 | constraint-null | A | B | 2.49 | 2.75 | No-signalling as marginal invariance; deep physics imported, artifacts unverified here |
| 13 | R014 | closed-form + match | A | B | 2.48 | 2.50 | EPR closed form = Schnakenberg 1976; 0 data points |
| 14 | R009 | numerical-match | A | B | 2.43 | 3.00 | LES tau_sgs exact identity, residual ~1e-14; opposite-world INELASTIC |
| 15 | R008 | low-energy-limit | C | E | 2.40 | 3.00 | BGK closure defect reduced not eliminated (0.285); sign imported |
| 16 | R011 | low-energy-limit | C | E | 2.39 | 1.88 | Diffusive cost => Euclidean; CLT imported, substrate-injected |
| 17 | R017 | structural | B | E | 2.36 | 2.13 | Metastability pairing; PCCA bridge unproved; worked example absent |
| 18 | R019 | symmetry-emergence | B | E | 2.36 | 1.88 | Gauge principle as Leibniz quotient; bridge lemma circular |
| 19 | R026 | parameter-compression | C | E | 2.36 | 1.63 | No-global-time = H^1 exactness; Sagnac is analogy only (fatal) |
| 20 | R027 | cross-domain-unif. | B | E | 2.30 | 1.88 | Route-mismatch diagnostic across 3 domains; common ambient algebra absent (fatal to unification) |
| 21 | R007 | uniqueness-necessity | D | E | 2.26 | 2.13 | Probability on stable unresolved fibers (F23); produces no measure |
| 22 | R003 | paradox-resolution | B | E | 2.24 | 1.50 | Complementarity + eraser; central witness sign-ambiguous (fatal) |
| 23 | R010 | parameter-compression | C | E | 2.22 | 2.00 | Shadow price = budget dual; signature ansatz-forced; budget step asserted |
| 24 | R025 | reinterpretation | E | E | 2.21 | 2.25 | Dark energy as forced rewrite; Omega_L~0.60 synthetic/tunable (NEVER a retrodiction) |
| 25 | R005 | uniqueness-necessity | B | E | 2.16 | 1.75 | Bell common-cause trichotomy; definition-unfolding, discriminative power 0 |
| 26 | R012 | cross-domain-unif. | C | E | 2.11 | 2.38 | Diffusion-geometry + EPR co-detection; curvature spliced across substrates |
| 27 | R023 | structural | C | E | 2.11 | 1.75 | Two-class layer birth; Prigogine headline absent from corpus |
| 28 | R006 | parameter-compression | D | E | 2.01 | 1.88 | Contextuality premise-isolation; no PM-specific machinery (fatal) |
| 29 | R032 | forced-target | C | F | 2.01 | 1.25 | m_nu lens-swap audit; direction 100% external, sign-blind (fatal) |
| 30 | R031 | forced-target | C | F | 2.00 | 1.50 | F40 "anomaly" relabeled; cannot express cancellation (fatal) |
| 31 | R022 | structural | C | E | 1.98 | 1.50 | WWW superselection co-statusing; discriminative power 0 |
| 32 | R021 | symmetry-emergence | D | B | 1.94 | 1.00 | CPT confinement; opposite-world-symmetric relabel (fatal); ship only the engine validation |

Derivability classes: **A** = load-bearing statement proved (often Lean) inside SBT, recovery given a declared input; **B** = recovery with a cited/imported leg; **C** = recovery requiring an imported sign/endpoint; **D** = heavily imported with an undischarged primitive; **E** = honest negative / documented silence. Bins (§7) are an Atlas-level disposition, distinct from derivability class.

---

## 4. Strategic portfolios

### 4.1 Near-term credibility (cheap, defensible, build infrastructure)

- **R001** — cleanest Lean-anchored anchor; first consolidated note.
- **R028** — parameter-rigid, survives all skeptics, opposite-world inelastic.
- **R024** — grep-verified honest negative; scope hygiene that pre-empts overclaiming.
- **R009** — exact LES identity (~1e-14); anchors the route-mismatch family.
- **R016** — fully proven Dobrushin recovery with an explicit eps-stable bound.
- **R015** — internally-proved Schnakenberg + Hodge necessity; hardens the directionality spine.

### 4.2 Flagship / high-impact

- **R001**, **R028**, **R027**, **R002** — see §2. Each headlines a different audience (foundations; stat-mech + quantum info; cross-domain methods; the famous cat).

### 4.3 Skeptic-resistant (lowest ad-hocness, clearest parameter accounting)

- **R024** (`non_ad_hocness=5`, `overfitting=none`) — nothing is fit.
- **R028** (`opposite_world_elastic=false`, overfitting low) — matches inequalities that must hold.
- **R016**, **R015** — Class A proofs with fitting freedom outside the proof.
- **R001** — the only flexibility (basis) is disclaimed and flagged, not hidden.

### 4.4 Cross-domain unification (SBT's real selling point)

- **R028** (audit-DPI: stat-mech + quantum info, with a proved leg).
- **R027** (route-mismatch: turbulence + cosmology + quantum measurement).
- **R001** (idempotent-packaging seeds the largest mechanism family).
- **R019** (orbit-descent: the widest mechanism by count).
- **R029** (closure-deficit: one exact obstruction across coarse-graining results).

### 4.5 Avoid or delay

- **R021** — CPT relabel, opposite-world symmetric, undischarged opaque source. Ship only the typed-cone engine validation, never as a CPT theorem.
- **R022** — WWW superselection co-statusing; imports everything, discriminative power 0.
- **R031** — F40 "anomaly" relabeled; cannot even express cancellation.
- **R032** — m_nu direction is 100% external; sign-blind, bin F.
- **R025** — `Omega_Lambda~0.60` is synthetic/tunable; on real data it loses to LambdaCDM (`Delta-AIC ~2` worse). Never cite as a retrodiction.
- **R014** — Schnakenberg 1976 recovery on a hand-built kernel; zero data points.

---

## 5. Audience-specific portfolios

**Mathematical physics:** R028 (monotone divergences / Petz), R016 (Dobrushin / eps-stable bound), R019 (Leibniz-quotient descent), R027 (operator-algebra route-mismatch + the open ambient algebra), R029 (Csiszar KL-projection / conditional-MI obstruction).

**Particle physics:** R024 (honest statistics/generations negative), R020 (vacuum-selection no-go F15a), R019 (gauge as A/G), R031 (anomaly-as-descent *scope critique*), R021 (CPT *engine validation only*).

**Relativity:** R026 (no-global-time as H^1 exactness; Sagnac is analogy), R027 (backreaction Jensen proxy, not Buchert Q_D), R004 (no-signalling / light-cone-as-P2-cone), R025 (dark energy as forced rewrite, number quarantined).

**Cosmology:** R025 (dark-energy reinterpretation + DES constraint-null; Lambda not refuted), R027 (backreaction leg), R032 (SPT-3G m_nu stability *report card only*).

**Quantum foundations:** R001 (collapse-as-closure), R002 (cat), R004 (no-signalling), R006 (contextuality premise-isolation), R007 (probability on unresolved fibers), R003 (complementarity/eraser), R005 (Bell trichotomy).

---

## 6. Mechanism reuse — SBT's real selling point

Six mechanisms recur. Two caveats frame all of them: most cards are `opposite_world_elastic=true` (the lens/basis/group is a free input, so the framework forbids no outcome), and a harsh reviewer can argue the six mechanisms collapse to three textbook lemmas (linear-algebra noncommutation; monotone divergences; quotient-by-fibers) wearing costumes. We foreground reuse as a strength while disclosing this deflation.

| Mechanism | Cards | Domains spanned | Verdict |
|:--|:--|:--|:--|
| **orbit-descent** | R005, R007, R018, R019, R020, R021, R024, R031 (8) | gauge theory, conservation, SSB, Bell, probability, anomaly, CPT, superselection | Widest by count and genuinely layer-agnostic, but the certified content is an analytic near-tautology; group, action, and symmetry->current map all imported; opposite-world passes for every leg. Bookkeeping unification, zero inferential weight. |
| **route-mismatch** | R003, R006, R009, R025, R026, R027, R032 (7) | turbulence, quantum, cosmology, relativity-adjacent | SBT's most far-reaching mechanism; the ledger itself names non-commutation as THE source of correction terms. LES leg is an exact verified identity. But RM is sign-free, the per-domain metric makes the scalars incommensurable, and the common ambient algebra does not exist. Portable diagnostic, not unification. |
| **idempotent-packaging** | R001, R002, R008, R011, R012 (5) | quantum, kinetic theory, emergent geometry, stat-mech | Precise, Lean-anchored compression (collapse, cat, BGK closure, emergent metric all read as Fix(E)). But the D-IC-02 guardrail (a constant map has defect 0, one fixed point) means objecthood is often definitional; inputs are selected. Compression real, predictive content nil. |
| **cycle-affinity** | R010, R013, R014, R015, R023 (5) | finite-state nonequilibrium stat-mech (one domain) | Faithful no-fake-arrow discipline (forest => no drive; exact 1-form => zero affinity), but the LEAST cross-domain: all five live in one domain. The affinity 1-form IS Schnakenberg's force (imported), Sigma_T/EPR are informational proxies, closed forms have 0 data points. |
| **audit-DPI** | R004, R028 (2) | stat-mech, quantum info | Most parameter-rigid; a real monotone-divergence contract with a proved Lean-anchored classical leg and a falsifiable "no arrow exceeds the micro arrow" guard. Opposite-world inelastic (R028). Limit: the "one law" is naming until the commutative-subalgebra lemma is written; quantum half imported. |
| **contraction-uniqueness** | R016, R017 (2) | finite Markov chains / metastability | Faithful Class-A Dobrushin recovery with an explicit eps-stable bound; smallest family. Inequality is logically equivalent to imported Dobrushin uniqueness; SBT cannot predict sector count (PCCA bridge unproved). |

---

## 7. Parameter accounting and ad-hocness

SBT's overfitting risk is **not** classical constant-fitting — most cards match exact-zero null gates or analytic identities with zero or two data points. The risk is **lens-selection freedom plus import.**

Three free-parameter classes dominate (ledger `free_parameters`, `missing_interfaces`):

1. **The lens / pointer basis / record algebra has no selection rule** (missing interface #1; pointer-basis selection explicitly disclaimed). Because the lens is free, the **opposite-world test passes for 28 of 32 cards**: the framework reorganizes whatever partition/basis/group it is handed and forbids no outcome.
2. **The completion `U_f` / prototypes** (uniform, Maxwellian, Gaussian, one-hot, max-entropy) are *selected*, not unique; for LES there is no canonical `U` at all.
3. **Declared substrate data in Foundations IV laws** (symmetry group, future-probe family, measure record, budgets) inject whatever physics is smuggled into the declaration.

**Where overfitting concentrates — the three numerical-constant cards:**

- **R025**: `Omega_Lambda=0.602429` from ~12 tunable knobs against ~1 chosen target value, openly synthetic.
- **R032**: m_nu *direction* from ~9 choices against 1 *external* matched fact.
- **R010**: shadow price from ~10 structural choices (including the load-bearing cost matrix) against ~2 matched facts; the only signature is ansatz-forced.

**By contrast, the skeptic-resistant cards have essentially zero fitting freedom** because they match inequalities/identities that *must* hold: R024 (`none`), R028 (`low`, inelastic), R016/R015 (`low`), R009 (`low`, inelastic).

The decisive discipline: every card must carry (a) a null-gate control value, (b) an explicit imported-vs-recovered ledger, and (c) the statement that the matched target is identically zero / forced / external where that is true. **Aggregate verdict: SBT cannot overfit a constant it does not produce, but it can accommodate almost any structure via lens/declaration freedom.** Its honest scientific value lives in the rigid, lens-independent inequalities and identities, not in any "match."

---

## 8. Publication strategy

| Step | Artifact | IDs | Rationale / dependency |
|---:|:--|:--|:--|
| 1 | Null-control calibration methods note | R030 | Infrastructure first: machine-zero null gates, labeled NOT a retrodiction; underwrites every nonzero audit reading. Prereq for steps 2,5,6. |
| 2 | Collapse-as-P5-closure note | R001, R002 | Flagship near-term: `thm:dephase` + dim>=2 witness; cat as companion. Depends on step 1 (cat-metric calibration). |
| 3 | LES route-mismatch reproducibility note | R009 | One-afternoon exact identity (~1e-14); disciplines the route-mismatch family. |
| 4 | Honest-negative scope addendum | R024 | Grep manifest over 50 .tex; scope hygiene before any flagship meets a hostile reviewer. |
| 5 | One-audit-monotonicity-contract note | R028 | Flagship recovery: classical + quantum DPI under one contract; optional unification lemma. Depends on step 1. |
| 6 | Directionality-certificate spine note | R015, R013 | Cycle-affinity necessity + three-fact arrow package; depends on protocol-trap/DPI guards (steps 1,5). |
| 7 | Contraction / metastability objecthood corollary | R016, R017 | Completes the no-go obstruction layer; names the open PCCA bridge. |
| 8 | Cross-domain route-mismatch diagnostic (flagship) | R027 | Retitled as diagnostic/taxonomy; depends on R009 + R001 legs. |
| 9 | Foundations-IV orbit-descent catalog | R019, R018, R020, R005, R007 | Bundle Lean-faithful instantiations with an imported-hypotheses ledger; reframing tier, after the credible core. |
| 10 | Dark-energy structural reinterpretation (constraint-null) | R025 | Last and most fenced: conditional necessity + DES constraint-null (Lambda not ruled out), synthetic number quarantined. High reputational risk; needs steps 4,8. |

---

## 9. Top-12 profiles

### R001 — Collapse as idempotent P5 packaging closure  *(rank 1, bin B, deriv A)*

- **Claim.** Given a fixed record basis and full pinch (`lambda=1`), the P5 objecthood law instantiated as dephasing `Delta(rho)=sum_i Pi_i rho Pi_i` has fixed-point set exactly the diagonal record-classical states (with a `dim>=2` witness certifying multiple objects), recovering Lueders pinching / einselection and reframing collapse as once-and-done idempotent packaging.
- **Target fact.** Nonselective Lueders update in a fixed pointer basis is an idempotent CPTP projector whose fixed points are the diagonal density operators (Zurek 2003; Nielsen-Chuang).
- **Theory basis.** P5 / `D-IC-01`, `sec:idempotent-endo` (Foundations of Emergence Calculus); `thm:dephase`, Lean `dephase_idem`, `dephase_fixed_iff_exists_diagonal` (`QuantumDephase.lean`, Quantum paper); section axiom `Q_f U_f = id`.
- **Minimum-viable plan.** State the P5 law; instantiate the QM package; invoke the two proved lemmas; add the dim>=2 nontriviality witness to clear the `D-IC-02` guardrail; state the Lean scope honestly (matrix-level diagonal extraction, not a CPTP channel).
- **Parameters / flexibility.** Record basis (the disclaimed free input), completion map, `lambda`/`tau`. All flagged, none hidden.
- **Strongest objection + acceptance conditions.** Pure recovery, no new number; the pointer basis is free, so opposite-world relabeling accommodates any basis. *Accept iff* presented as A-given-basis recovery with pointer-basis selection named as the repair frontier, and "Lean-certified" scoped to the matrix algebra.
- **Scores.** overall 3.09; mean survival 2.88; no fatal; overfitting low.
- **Artifact.** A short "Collapse as P5 closure" note consolidating `thm:dephase` + the witness, with a scope paragraph separating Lean-proved from Python-numeric from prose-interpretation.

### R002 — Schrodinger cat as layer-relative objecthood  *(rank 2, bin E, deriv B)*

- **Claim.** Conditional on a fixed pointer basis and standard QM, the EXP-CAT1 S-A-E qubit model is an exact instance of decoherence as P5 layer-relative objecthood: global state exactly pure (`Tr rho^2 = 1`) and entangled, while the discard+dephase record state is an idempotent classical mixture in `Fix(Pack)` (idempotence error 0; dist-to-mixture ~1.11e-16). "Alive-vs-dead" is not a record-layer object.
- **Target fact.** Standard decoherence: tracing the environment yields a classical pointer mixture while the global state stays near-pure.
- **Theory basis.** `thm:dephase` backbone; EXP-CAT1 (Quantum paper); OI-EI principle.
- **Minimum-viable plan.** A conditional-proposition note with a statused lemma chain (L1–L2 proved+Lean; L3 numerical; L4 the *new* operator-algebra OI-EI off-diagonal-silence lemma; L5 imported Born weights; L6 optional general theorem).
- **Strongest objection + acceptance conditions.** The load-bearing dissolution lemma (L4) is unwritten; `Fix(Pack)` is diagonal by construction (not earned). *Accept iff* framed strictly as recovery, with single-outcome/pointer-basis/Born quarantined.
- **Scores.** overall 3.00; mean survival 3.00; no fatal; overfitting low.
- **Artifact.** "Macroscopic definiteness as layer-relative objecthood", paired with a re-run of EXP-CAT1.

### R024 — Honest negative: no statistics, spin-statistics, or generations  *(rank 3, bin B, deriv E)*

- **Claim.** SBT does NOT reproduce the fermion/boson dichotomy, the spin-statistics theorem, or the three-generation pattern: an exhaustive grep of all 50 `.tex` files finds zero exchange-symmetry / antisymmetrization / Fock / permutation-group / anyon machinery, and every contact point is an imported declaration.
- **Target fact.** QFT derives the statistics dichotomy and Pauli exclusion from Lorentz invariance + microcausality + positive energy.
- **Theory basis.** Forced by the ledger missing-interface inventory (no Born valuation, no continuum, no Lorentz/spacetime, no multiparticle Fock).
- **Minimum-viable plan.** A 2–4 page scope-boundary addendum: reproducible grep manifest; five import-not-derivation readings with <=25-word quotes; the P4 disanalogy; the missing-interface table; the "not-expressible / outside scope" remark.
- **Strongest objection + acceptance conditions.** Near-vacuity: documented silence is a disclaimer, not a result. *Accept iff* framed as a class-E disclaimer addendum bundled with the existing negatives.
- **Scores.** overall 2.97; mean survival 4.00; no fatal; overfitting none.
- **Artifact.** Ledger disclaimer addendum, cross-listed with the eight no-go theorems.

### R028 — One audit-monotonicity contract: two data-processing inequalities  *(rank 4, bin B, deriv B)*

- **Claim.** The classical finite path-space arrow DPI (forward-vs-reversed KL: macro <= micro, `NG_ARROW_DPI`) and the quantum relative-entropy DPI under CPTP maps are two instances of one coarsening-monotone audit contract `A(Q mu, Q mu') <= A(mu, mu')`, giving the falsifiable guard "a coarse-grained arrow exceeding the micro arrow is spurious."
- **Target fact.** (a) Coarse-graining cannot increase forward/reverse path-KL (Cover-Thomas; Esposito 2012); (b) relative entropy is monotone under CPTP maps (Lindblad/Petz/Uhlmann; Wilde).
- **Theory basis.** `NG_ARROW_DPI` / `T-AOT-01` (No-Go), proved from the log-sum inequality + reversal commutation; Lean `tvdist_pushforward_le`; quantum half cited + 0-violation regression (`d in {2,3,4,6}`).
- **Minimum-viable plan.** A 5–8 page expository note with the self-contained classical proof, the cited quantum DPI + regression table, the shared-contract statement labeled naming-level, and an honesty box separating proved+Lean(TV) from proved-not-mechanized (KL/Sigma_T) from cited+regression-tested (quantum).
- **Strongest objection + acceptance conditions.** The "one law" is naming, not a theorem; zero new bound; quantum half imported. *Accept iff* the unification is labeled naming and the `Sigma_T`-informational-proxy disclaimer travels with it.
- **Scores.** overall 2.85; mean survival 3.00; no fatal; overfitting low; **opposite-world inelastic.**
- **Artifact.** "One audit-monotonicity contract: no false arrows."

### R029 — One conditional-MI obstruction recovering lumpability  *(rank 5, bin E, deriv B)*

- **Claim.** The exact obstruction `CD_tau(Pi)=I(X_t;Y_{t+tau}|Y_t)`, with `H(Y_{t+tau}|Y_t)=H(Y_{t+tau}|X_t)+CD_tau`, is the single object whose vanishing characterizes closed coarse-grained Markov dynamics — recovering Kemeny-Snell/Buchholz lumpability at `tau=1` — and cleanly splits macro-noise into intrinsic substrate uncertainty plus lens-manufactured randomness.
- **Target fact.** Exact lumpability of finite Markov chains; predictive sufficiency / causal states.
- **Theory basis.** `prop:cd-decomposition`, `prop:cd-kl`, `prop:cd-zero` (To_Cast_a_Stone); `NG_MACRO_CLOSURE_DEFICIT`; Lean KL-bridge module.
- **Minimum-viable plan.** The exact-decomposition theorem + the best-macro-kernel variational identity (acknowledged Csiszar KL-projection) + the Markov benchmark + Pinsker route-mismatch calibration (`r=0.959`); the two needed bridging lemmas listed as open.
- **Strongest objection + acceptance conditions.** Recovery + reorganization; leg (b) is an unproved cross-formalism adjacency, leg (c)'s `q/2^n` is an imported toy. *Accept iff* framed as a diagnostic, not a three-domain unification.
- **Scores.** overall 2.84; mean survival 2.25; no fatal; overfitting low-but-misframed.

### R016 — Contraction => unique object (objecthood necessity)  *(rank 6, bin B, deriv A)*

- **Claim.** Within strict Dobrushin contraction, the objecthood-as-fixed-points law (on `E_{tau,f}` or `M_Pi`, never the bare micro kernel) forces at most one nontrivial robust object, with separation bound `TV(nu,nu') <= 2 eps/(1-lambda(E))`; contrapositively, exact multiplicity certifies only `lambda(E)=1`, not a closed spectral gap.
- **Target fact.** Strict (Dobrushin) contraction implies a unique stationary distribution.
- **Theory basis.** `NG_OBJECT_CONTRACTIVE` (No-Go); `D-IC-02` nontriviality guardrail.
- **Minimum-viable plan.** A 1–3 pp corollary note stated for ONE named operator with its own `lambda(E)`, plus reducibility-vs-metastability demarcation; optional Lean stub for the eps-stable bound.
- **Strongest objection + acceptance conditions.** Pure recovery; the contrapositive is a one-line restatement; `lambda(E)=1` is weak. *Accept iff* presented as a presentational corollary, not a metastability diagnostic.
- **Scores.** overall 2.83; mean survival 2.88; no fatal; overfitting low.

### R015 — Cycle-affinity + discrete-Hodge necessity  *(rank 7, bin B, deriv A)*

- **Claim.** In the AUT+REV+ACC regime at stationarity, a sustained directionality certificate is necessarily carried only on positive-cycle-rank support by a non-exact 1-form: forests (`beta_1=0`) or exact affinities certify zero arrow (`NG_FORCE_FOREST` + `NG_FORCE_NULL`), recovering Schnakenberg cycle-affinity + discrete-Hodge necessity; the matching sufficiency is imported from Schnakenberg.
- **Target fact.** Nonequilibrium drive is supported on cycles; exact 1-forms carry no circulation; forests carry none.
- **Theory basis.** `NG_FORCE_FOREST`, `NG_FORCE_NULL`, `cycle-criterion-exact`, `cor:null-regime` (No-Go).
- **Strongest objection + acceptance conditions.** Near-zero novelty (textbook graph theory); the applied verdict is lens-contingent. *Accept iff* the imported sufficiency is tagged and the informational-proxy reading is kept.
- **Scores.** overall 2.79; mean survival 2.63; no fatal; overfitting low.

### R020 — Selection obstruction: a symmetry cannot select its vacuum  *(rank 8, bin B, deriv C)*

- **Claim.** F15a (Lean `selection_obstruction`) recovers the textbook impossibility of selecting a vacuum by exactly symmetric means: under a declared group with an equivariant selector and trivial orbit action, the selector lands only in the G-fixed locus, so any SSB / gauge-fixing account must import a declared breaker. F15b "formation" is reported only as a conditional obligation-wrapper.
- **Target fact.** Goldstone / Anderson / Gribov-Singer: symmetric dynamics cannot pick a degenerate vacuum.
- **Theory basis.** `Symmetry.SelectionObstruction.selection_obstruction`; F2 minimal source refinement (Foundations IV).
- **Strongest objection + acceptance conditions.** `any_fatal=true`: F15b axiomatizes its own conclusion via an opaque `FutureBranchSelectionFormationSource`. *Accept iff* F15b is reported as a conditional typing wrapper that derives no formation, and the no-go is one worked finite instance.
- **Scores.** overall 2.79; mean survival 2.50; **fatal-if-claimed** (defused by narrowing).

### R018 — Conservation as orbit descent (F27)  *(rank 9, bin E, deriv A)*

- **Claim.** F27 is a Lean-certified normal form: a readout `C` is conserved iff it factors as `C = barC o q_orb` iff it is closure-invariant — the textbook "function-on-the-quotient = function-constant-on-fibers" fact, re-organizing Lavoisier mass, knot invariants, subject reduction, Meselson-Stahl, and the martingale property as five instances, with Noether NAMED not derived.
- **Target fact.** Conservation laws / Noether's theorem.
- **Strongest objection + acceptance conditions.** `any_fatal=true`: the certified content is an analytic near-tautology with discriminative power exactly zero; the substantive Noether direction (`d_mu J^mu=0` on-shell) is out of scope. *Accept iff* filed as a conceptual-reframing note with Noether explicitly only NAMED.
- **Scores.** overall 2.69; mean survival 2.13; overfitting high (for any reading beyond bookkeeping).

### R013 — Arrow of time within scope, in one package  *(rank 10, bin B, deriv A)*

- **Claim.** Three standard facts consolidated as distinct finite certificates: (i) detailed-balance => `Sigma_T=0` at every horizon (`NG_PROTOCOL_TRAP`); (ii) deterministic coarse-graining cannot increase the audit (`NG_ARROW_DPI`, Lean `tvdist_pushforward_le`); (iii) an arrow is the monotone direction of a descended record quotient (F38). A fake arrow cannot be manufactured from reversible micro-dynamics + deterministic coarse-graining + hidden holonomy alone.
- **Target fact.** Kelly 1979; Cover-Thomas; Schnakenberg 1976; Eddington 1928.
- **Strongest objection + acceptance conditions.** Bundle of standard theorems; `Sigma_T`/EPR are informational proxies; does NOT derive the Second Law or Past Hypothesis. *Accept iff* the holonomy-robust content is attributed to the Protocol_Trap construction (not the bare theorem) and the proxy disclaimer is loud.
- **Scores.** overall 2.67; mean survival 3.50; no fatal; overfitting low.

### R030 — Null-control calibration (NOT a retrodiction)  *(rank 11, bin B, deriv B)*

- **Claim.** At declared null-gate control values, four audit functionals return machine zero (`CD_1=4.34e-17`; no-signalling `2.22e-16`; cat dist `1.11e-16`; `EPR_lifted=5.55e-18`) — each an IEEE-754 realization of a standard exact-zero theorem. The only genuine theorem-backed content is the one-directional rigidity "no false positive at the null gate."
- **Target fact.** Four identically-zero theorems (Kemeny-Snell, no-signalling, Lueders idempotence, detailed-balance EPR=0).
- **Strongest objection + acceptance conditions.** `any_fatal=true` *as a retrodiction* — the target is identically zero and carries no empirical content. *Accept iff* reclassified as a null-control calibration that underwrites the credibility of nonzero readings elsewhere.
- **Scores.** overall 2.56; mean survival 2.00; fatal-as-retrodiction (defused by reclassification).

### R004 — No-signalling as marginal invariance  *(rank 12, bin B, deriv A)*

- **Claim.** Conditional on a declared record lens, SBT re-expresses operational no-signalling as marginal-invariance under remote-setting variation, with a uniform max-TV separator classifying a family as a "constraint" (classical XOR box max-TV=0; quantum EPR ~2.2e-16) vs a "channel" (signalling box max-TV=1); the finite deterministic TV-DPI (`tvdist_pushforward_le`) is the classical no-false-positives analogue, while the quantum CPTP marginal invariance is imported by citation.
- **Target fact.** No-signalling: a local setting choice does not change the distant reduced state; conditioning does.
- **Strongest objection + acceptance conditions.** Deep physics imported (partial-trace/CPTP invariance); data are forced extremes {0, ~2.2e-16, 1}; cited Lean/Python artifacts not verifiable in this corpus snapshot. *Accept iff* titled as recovery + category-error demarcation with an imported-vs-recovered disclaimer block.
- **Scores.** overall 2.49; mean survival 2.75; no fatal; overfitting high.

---

## 10. Avoid-list profiles

### R025 — Dark energy as a forced closure rewrite  *(rank 24, bin E, deriv E)*
The conditional necessity ("route mismatch + insist on closure => some `Delta_H`") is honest, but the headline `Omega_Lambda=0.602429` is a hand-built synthetic number with ~12 knobs tuned to land near 0.6, and on real DES SN5YR + Y6 BAO the rewrite collapses to `m~0` with `Delta-AIC ~2` **worse** than LambdaCDM. The Identification lemma connecting the finite toy to real GR cosmology is undischarged. **Never cite the synthetic number as a retrodiction;** ship only the structural reinterpretation + the constraint-null (Lambda explicitly NOT ruled out).

### R021 — CPT/C confinement  *(rank 32, bin B, deriv D)*
A real Lean-certified typed-cone squeeze (`masterTheorem`) wrapped around a CPT "prediction" that is a declared, opposite-world-symmetric relabeling with zero discriminative power and an undischarged opaque recognition source. `mean_survival=1`, `any_fatal=true`. **Ship only the honest engine validation** on transpose/`Sym_n` with a constructed domination sequence; keep CPT as a flagged conditional, never a theorem.

### R022 — WWW superselection co-statusing  *(rank 31, bin E, deriv C)*
Two content-free normal forms (F9 + a proposed F4) co-status superselection while importing every load-bearing fact; opposite-world passes both ways; the F4 leg is uncertified for the quantum instance. `discriminative_power=0`, `baseline_advantage=0`. A calibration entry only, strictly weaker than DHR.

### R031 — F40 anomaly as descent obstruction  *(rank 30, bin F, deriv C)*
The quotient universal property relabeled "anomaly"; ratifies both anomalous and non-anomalous worlds and **cannot express anomaly cancellation** (structurally inexpressible). Bin F. Tightly scope-boxed expository classification only.

### R032 — SPT-3G m_nu lens-swap audit  *(rank 29, bin F, deriv C)*
A sign-blind, uncalibrated cross-lens audit whose headline DIRECTION is 100% external (arXiv:2601.16277); the packaging-stability certificate is applied by analogy with no stochastic-lens backbone. `any_fatal=true`. Reusable only as a methodological report card, never a neutrino-mass result.

### R014 — Driven-3-cycle EPR closed form  *(rank 13, bin B, deriv A)*
*(Listed in avoid_or_delay for priority, not because it is unsound.)* A trivially-exact RECOVERY of Schnakenberg's 1976 current x affinity identity on a hand-built kernel, already in the corpus, with zero independent data points. Keep as a low-priority dictionary note; do not invest.

---

## 11. Completeness critique

This Atlas inherits limits from its inputs and method:

1. **Unverified artifacts.** Many Lean lemmas and Python scripts are cited by identifier from `.tex`; several cards (e.g. R004) flag that zero `.lean` files and zero Python exhibits were independently confirmed in the corpus snapshot. "Lean-certified" rests on the cards' verification logs, not a fresh build. Re-run the named modules before publishing.
2. **Scores not recomputed.** Composites were used as given; if the formula weights or skeptic panel were miscalibrated, the ranking shifts.
3. **Targets not covered.** The 32 are curated. SBT cannot reach — and a hostile reviewer will ask about — particle mass ratios, coupling-constant running, CKM/PMNS mixing, the fine-structure constant, the Planck spectrum, the Hubble-tension magnitude, muon g-2, neutrino oscillation parameters, and any S-matrix observable. The Atlas states this rather than implying the 32 exhaust the space.
4. **Modalities not run.** No fresh red-team beyond the frozen four-skeptic panel; no out-of-sample / pre-registration test (all matched data are frozen certificates of identities that must hold); no sensitivity analysis on the lens-selection freedom driving opposite-world elasticity.
5. **Where this analysis could be wrong.** The cross-domain mechanism-reuse framing is the most flattering honest reading. A harsher reviewer could argue it is a single trivial fact (noncommutation; monotone divergences; quotient-by-fibers) wearing six costumes — collapsing "six mechanisms across many domains" to "three textbook lemmas relabeled." The Atlas foregrounds reuse as a strength while disclosing this deflation.
6. **Disclaimer drift.** Several cards carry framings the source papers do not contain (R013 Loschmidt/Second-Law; R014/R023 thermodynamic framing; R025 dark energy). The Atlas relies on the repair stage having stripped these; residual drift is possible.

---

## 12. Appendix — all 32 with composite scores

| Rank | ID | overall | practical | persuasive | flagship | min surv. | mean surv. | fatal | overfit | opp-world elastic |
|---:|:--|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | R001 | 3.09 | 4.10 | 2.75 | 2.20 | 2.5 | 2.88 | no | low | yes |
| 2 | R002 | 3.00 | 3.95 | 2.75 | 2.05 | 3.0 | 3.00 | no | low | yes |
| 3 | R024 | 2.97 | 3.95 | 2.90 | 1.70 | 4.0 | 4.00 | no | none | yes |
| 4 | R028 | 2.85 | 3.80 | 2.70 | 1.75 | 3.0 | 3.00 | no | low | **no** |
| 5 | R029 | 2.84 | 3.80 | 2.50 | 2.05 | 2.0 | 2.25 | no | low* | yes |
| 6 | R016 | 2.83 | 3.80 | 2.55 | 1.90 | 2.5 | 2.88 | no | low | yes |
| 7 | R015 | 2.79 | 3.80 | 2.55 | 1.75 | 2.0 | 2.63 | no | low | yes |
| 8 | R020 | 2.79 | 3.80 | 2.55 | 1.75 | 2.0 | 2.50 | yes | low | yes |
| 9 | R018 | 2.69 | 3.80 | 2.40 | 1.60 | 2.0 | 2.13 | yes | high | yes |
| 10 | R013 | 2.67 | 3.72 | 2.35 | 1.70 | 3.0 | 3.50 | no | low | yes |
| 11 | R030 | 2.56 | 3.65 | 2.20 | 1.60 | 1.0 | 2.00 | yes | low | yes |
| 12 | R004 | 2.49 | 3.45 | 2.20 | 1.60 | 2.0 | 2.75 | no | high | yes |
| 13 | R014 | 2.48 | 3.43 | 2.23 | 1.55 | 2.0 | 2.50 | no | none | yes |
| 14 | R009 | 2.43 | 3.65 | 2.20 | 1.10 | 2.5 | 3.00 | no | low | **no** |
| 15 | R008 | 2.40 | 3.65 | 1.90 | 1.45 | 3.0 | 3.00 | no | medium | yes |
| 16 | R011 | 2.39 | 3.65 | 1.70 | 1.75 | 1.5 | 1.88 | yes | high | yes |
| 17 | R017 | 2.36 | 3.25 | 2.05 | 1.60 | 2.0 | 2.13 | no | high | yes |
| 18 | R019 | 2.36 | 3.50 | 1.85 | 1.60 | 1.0 | 1.88 | yes | low | yes |
| 19 | R026 | 2.36 | 3.50 | 1.85 | 1.60 | 1.0 | 1.63 | yes | high | yes |
| 20 | R027 | 2.30 | 3.30 | 1.85 | 1.60 | 1.5 | 1.88 | yes | high | yes |
| 21 | R007 | 2.26 | 3.25 | 1.90 | 1.45 | 2.0 | 2.13 | yes | high | yes |
| 22 | R003 | 2.24 | 3.30 | 1.70 | 1.60 | 1.0 | 1.50 | yes | high | yes |
| 23 | R010 | 2.22 | 3.10 | 1.85 | 1.60 | 2.0 | 2.00 | no | high | yes |
| 24 | R025 | 2.21 | 2.90 | 1.90 | 1.75 | 2.0 | 2.25 | yes | high | yes |
| 25 | R005 | 2.16 | 3.45 | 1.60 | 1.25 | 1.0 | 1.75 | yes | high | yes |
| 26 | R012 | 2.11 | 2.95 | 1.70 | 1.60 | 2.0 | 2.38 | no | high | yes |
| 27 | R023 | 2.11 | 2.95 | 1.70 | 1.60 | 1.5 | 1.75 | yes | high | yes |
| 28 | R006 | 2.01 | 2.95 | 1.55 | 1.45 | 1.5 | 1.88 | yes | high | yes |
| 29 | R032 | 2.01 | 2.95 | 1.55 | 1.45 | 1.0 | 1.25 | yes | high | yes |
| 30 | R031 | 2.00 | 3.33 | 1.40 | 1.10 | 1.0 | 1.50 | yes | high | yes |
| 31 | R022 | 1.98 | 3.30 | 1.40 | 1.05 | 1.0 | 1.50 | yes | high | yes |
| 32 | R021 | 1.94 | 3.10 | 1.40 | 1.20 | 1.0 | 1.00 | yes | high | yes |

\* R029 overfitting is "low-but-misframed." Bin counts: B=12, E=18, F=2 (derivability classes are orthogonal to these dispositions).

*End of Atlas.*
