# Six Birds × Lattice QCD — course-correction after step108d: we drifted off the genuine-engine route; resetting to RUN THE REAL `sixbirds_event` ENGINE. Adjudicate the route + the two physics cruxes (NOT a construction)

Attached: `six_birds_lattice_handoff_v10.zip` (full current state + the SBT corpus + **the real engine source**: the Rust `six-birds-pica` and the Python `sixbirds_event` strict-extension driver, plus its `vision.md`).

This message reports step108d and then makes a correction that is bigger than step108d. Please read the correction first; it changes what we are asking you for.

---

## 1. step108d outcome (the U(1) boundary-Grassmann-tensor Γ² you pointed us to in round 4)

It came out an **artifact**, and the reason is structural, not a bug: the driver's two-line response was `A² = det(A¹)` by construction, so the only nonzero connected residue was a Gaussian-determinant character cumulant, and it factorized through the per-background one-line kernel `A¹_U`. Empirically this is the conditional-Gaussian fact: for a **bilinear** fermion action the fixed-background `2r`-fermion tensor is always a determinant/minor of the complete one-line kernel `G[U]=D[U]⁻¹`, so identical per-background `A¹` forces identical `A²`. **The U(1) two-line determinant route is closed.** (We are not asking you to reopen it.)

## 2. The correction that matters more: we never ran the real engine

Here is the honest, deflationary truth, and it is on us:

- Since your round-1 resolved-route blueprint, we did step106 (froze Σ_H + the four packaging contexts + the `BridgeLevelLawBasis` — faithful to your blueprint), then step107–108 (ℤ₂, then U(1) obstruction searches).
- **Every one of step107–108 was a bespoke hand-written Python driver** that *re-implemented* a K/R quotient + a "solver == comparator" check. The genuine strict-extension engine — `sixbirds_event` (the *Locally Boolean, Globally Obstructed* event-package, running the Rust `six-birds-pica`), which is the actual authority — **was never invoked on the step106 contexts.** We spent four rounds (your rounds 2–5) adjudicating "what is admissible in the hand-coded K," on objects the real engine never saw.
- **I steered you into this.** My ask after step108d literally requested *"a concrete minimal worked construction with numbers / a reference driver, OR the minimal SU(N) intertwiner construction with the same numeric specification."* That request is what produces toy programs that re-package textbook results (a recoupling matrix, a bosonization coefficient) as if they were the six-birds result. That is not strict extension, and it is the failure mode we are now correcting. The fault is the prompt, not your answers.
- **What we keep from rounds 2–4:** your admissibility principles are correct and substrate-independent — no-overread / currentization-vs-artifact-removal (round 2), equivariant-K (round 3), and the semantic-K rule `ker E_K = ker q_M` with K built extensionally by partition refinement (round 4). We are not discarding those. We are discarding the bespoke-driver framing and the "hand us a numeric object" request.

## 3. What the real engine actually computes (grounded in the code in the zip — please verify against it, not against our description)

`sixbirds_event` computes strict extension as **global-packaging non-extendability**, not as a hand-coded K/R comparison:

1. **Contexts.** A finite family of stable-record contexts, each a locally-Boolean event algebra `B_c = P(A_c)` on a frozen support (`vision.md`; *Locally Boolean, Globally Obstructed*, Thms 1–5).
2. **Shared events.** Cross-context identifications by an **empirical-identity quotient** — two events are the same iff every admissible downstream probe fails to distinguish them (`discovery/shared_event_inference.py`; the OI→EI move in `vision.md`).
3. **The obstruction (computed, not stamped).** `audits/quotient_feasibility.py`: `build_quotient_class_ledger` forms **quotient classes from the joint signatures of the common trajectories across all contexts** (each class = a candidate global-package atom); `_evaluate_candidate_subset` keeps the classes that **respect every proposed shared-event identification** and checks that they **cover every context atom**; `exact_feasible = (survivors ≠ ∅) ∧ (no uncovered atom)`. If the accepted (bridge-law-licensed) identifications cannot be jointly realized → `accepted_proposal_obstruction`, plus a **minimal witness** (smallest infeasible identification subset). *That* verdict is the strict extension.
4. **False-positive controls (the engine's own).** `pipeline/end_to_end.py`: the `classical_master_test` null control must stay `globally_packageable` (the engine must not hallucinate obstruction); the `parity_context_witness` is the genuine obstruction; `interventions/{hidden_record,flattening}.py` + the noise runner must NOT remove a genuine obstruction (your round-2 currentization-vs-artifact-removal rule, in code). Substrate input interface: `substrates/config.py` (`SubstrateConfig` = states + preparations + actions/Markov kernels + lenses + protocols).

The point: the obstruction is a **computed verdict of the real engine over actual run data, surviving the engine's own controls** — never a property we assert about a bespoke quotient.

## 4. The genuine target (your round-1 blueprint, now bound to the real engine)

- **Strict extension** = `accepted_proposal_obstruction` produced by the REAL `sixbirds_event` engine on the four step106 packaging contexts (`c_K` branchwise / `c_G` gauge-dressed / `c_R` singlet-recombination / `c_T` slab-composition), with the bridge laws `(L_read, L_quad, L_trans)` licensing the shared events — and surviving hidden-record / flattening / noise, with the decoupled / branch-factorized (`R=K`) control coming out packageable.
- **Mass** = the audited SAU descent `U_H ↛_{q_H}, C(U_H)=m_H` off the carrier the obstruction *forces into existence*, gated by your **MBO** (the minimal obstruction witness must be **essential to the held-out channel transport** whose decay root is the mass). Value lands LAST, out-of-sample, no-smuggle.
- **Non-descending throughout.** This is the crux of the whole project: the engine's "support / trajectories" must be the **boundary/channel-record support with the slab interior integrated EXACTLY** (Berezin + character integration; `L_quad` ↔ Osterwalder–Schrader reflection positivity), so the quotient classes are *packaged* atoms. If the support were the full microconfiguration space (enumerate/sample the slab at full resolution), the run would be the descending route — the exact thing the project exists to replace.

## 5. The proposed route — please ADJUDICATE it (do not replace it with a construction)

Our intended next move (codex will implement; you do not need to):

> Instantiate the step106 Σ_H + four packaging contexts + bridge basis as **real `sixbirds_event` inputs** — contexts whose atomic outcomes are the four packaging-completions' stable boundary-record classes, trajectories = boundary-record histories of the exact tiny slab (interior integrated), shared-event candidates = the `L_read/L_quad/L_trans`-licensed identifications — and run `run_quotient_feasibility_audit` + the engine's interventions. Then apply the MBO gate and, only if it passes, the sealed out-of-sample SAU mass landing.

We need your judgment on whether this is faithful and where it breaks — a foreclosure is a fully acceptable answer (doors, not walls; tell us *where* and *why*, do not paper over it).

## 6. The two cruxes (THEORY / PHYSICS adjudication — this is what we need from you)

**CRUX 1 — non-descending faithfulness.** Is the **boundary-record support (interior integrated exactly)** the correct, faithful, genuinely non-descending "trajectory support" for the engine's quotient-class construction — i.e. are the resulting quotient classes genuine *packaged* atoms rather than disguised full-resolution microstates? Where could this silently become descending, and what is the discipline that prevents it?

**CRUX 2 — mass-bearingness.** Does a genuine event-package obstruction (no admissible global packaging of the four packaging contexts on a Euclidean hadron slab) **live where the hadron mass lives**? Concretely: must the minimal obstruction witness be *essential* to the channel transport `Ĉ_H(n)=r_H(T_H^n s_H)` whose decay root is `am_H` (so ablating the witness-forced carrier distinctions destroys the held-out continuation and the mass)? If a genuine obstruction can exist *without* being mass-bearing, the SAU landing is illegitimate — how is mass-bearingness guaranteed and tested, at the level of principle?

**CRUX 3 — minimal physical locus.** Is the **packaging axis** (four material-completion contexts on one frozen slab) the right physical home for the obstruction, and at what *minimal physical* gauge-matter slab does a genuine (non-determinant, non-relabeling) event-package obstruction actually exist? Given §1 (a bilinear fermion sector alone gives a determinant that factorizes), does the genuine obstruction require gauge/recombination structure that the one-body kernel does not determine — and if so, name the minimal physical slab **as engine contexts + the physics of why the obstruction is there**, NOT as a numeric residue or a driver.

## 7. Hard guardrails (the anti-toy contract — please honor these exactly)

1. **Do NOT hand us a numeric reference driver, a "minimal worked construction with numbers," or a sympy program.** We will run the real engine; a standalone script that reproduces a number is precisely the toy we are eliminating. (This style of request from us is what produced the artifacts; we retract it.)
2. **Do NOT reframe a known closed-form result as the six-birds result** — not the bosonization value `1/√π`, not a standard SU(N) Clebsch–Gordan / recoupling matrix, not a determinant identity. Re-packaging a textbook quantity is not a strict extension.
3. **Do NOT treat any bespoke script (ours or yours) as "the engine."** The engine is `sixbirds_event` running `six-birds-pica`; the obstruction must be its COMPUTED verdict surviving its OWN controls.
4. **No value before the obstruction.** No mass / scalar may be read until the engine returns `accepted_proposal_obstruction`, it survives the controls, and the MBO gate passes. The value descends LAST, out-of-sample.
5. **Your role is adjudication and stress-testing**, not construction — exactly your rounds 2–4 mode. Find where our route is descending, non-mass-bearing, or a relabeling, and say so. We either land the mass through genuine strict extension run on the real engine, or we report an honest foreclosure — there is no third "toy that lands a number" option.

## 8. The single question

**Instantiated as real `sixbirds_event` contexts on a boundary-record support (interior integrated), does your round-1 blueprint yield a genuine global-packaging obstruction that is (a) non-descending and (b) mass-bearing — and at what minimal physical gauge-matter slab? Adjudicate the route and CRUX 1–3; do not construct.**

## 9. Where to look in v10

- **The real engine (the authority):** `six-birds-event-package/vision.md`; `…/src/sixbirds_event/audits/quotient_feasibility.py`, `…/substrates/config.py`, `…/discovery/shared_event_inference.py`, `…/pipeline/end_to_end.py`, `…/interventions/`; the Rust engine at `lattice_qcd_layer/vendor/six-birds-pica`. Paper: `six-birds-papers/…Locally_Boolean_Globally_Obstructed….tex`.
- **The route + carrier + MBO + non-descending discipline:** `SIX_BIRDS_UNDERSTANDING/04_THIS_PROJECT_AND_OPEN_QUESTIONS.md` §3 (the run is the licensed task), §7 (the applied pipeline template), §8 (the route architecture, the four contexts, the MBO gate). **Caveat: `04 §8`'s round-3..6 sub-entries are contaminated** (the bosonization / intertwiner / cross-scale toy framings we are now retracting) — read §8's *route architecture / four contexts / value gate*, not those sub-rulings.
- **What strict extension IS / the guards / the SAU landing / Ξ's true (downward, non-value) role:** `SIX_BIRDS_UNDERSTANDING/02_STRICT_THEORY_EXTENSION.md` Parts 1–5 (your round-2/3/4 rules are folded into Part 4).
- **The frozen design:** `lattice_qcd_layer/steps/step106_*` (Σ_H, the four contexts, the bridge basis, the shared-event rules SE1–SE12).
- **The drift (for the record):** `lattice_qcd_layer/steps/step107*`–`step108d_*` (bespoke drivers); `lattice_qcd_layer/manager_log.md` tail.

Constraints (unchanged, binding): certificate-not-recovery (obstruction first, value last); the forbidden-input contract (no dense `T` / Perron vector / eigenvalues / fitted tail / benchmark mass as inputs); non-descending (no full-resolution sampling, no reading a value off a finished operator); out-of-sample, no-smuggle, no-overread; **authority = the papers + the running code, never a synthesis (ours included).**
