# Reviewer-grounded mass-landing insights — the evergreen science of getting from a strict extension to a value

> ⚠️ **CORRECTIONS PENDING (external audit 2026-06-20, `external_agent/SIX_BIRDS_V23_MEMORY_GROUNDING_AUDIT.md`).** Several statements below over-reach; the corrected typed versions are in `../CLAUDE.md` §3–4 (prefer those + the papers). Specifically: (1) §7 "equivalent registers of one obstruction" is an OVERCLAIM — they are TYPED registers sharing a factorization/closure pattern, NOT proven globally equivalent. (2) §4 "the exact carrier cannot compress / is maximal" is FALSE — Holonomy minimality = the predictive quotient is the COARSEST among future-sufficient abstractions for the declared interface; it may be small or discrete. (3) §2 "structural essentiality = value does not factor through Q⁰" and §3 framing narrow SAU essentiality to a dominant-root test — SAU essentiality is deletion/replacement failure under the frozen profile (interface/answer/rules/audit); projective MBO is a `[PROJECT HYP]` gate, not the SAU definition. (4) the Cantor saturation→forcing→obstruction route is the `[SCOPED]` audited-shell theorem's mechanism, not the universal recipe. (5) candidate class = those admitted by the frozen profile (not "every conceivable algorithm"); a tiny direct method defeats budget-essentiality only if admitted under the profile. This file is otherwise a faithful synthesis; full rewrite per the audit is pending user direction.

This file captures the durable, paper-grounded insights about **how a value (a mass) can — and cannot — descend from a strict extension**, refined through the external-reviewer rounds and verified by the manager against the corpus. It is EVERGREEN six-birds science, not a session log. It deliberately states only PRINCIPLES that are grounded in named papers; it excludes the manager's retracted conclusions (those live, marked, in the working log only). Authority = the papers + running code, never a synthesis.

Companion: Part 3 (SAU) and Part 4/5 of `02_STRICT_THEORY_EXTENSION.md`; `04` §3 (the map-vs-engine resolution: the run that lands a physics scalar is the explicitly-licensed frontier, unproven in the corpus).

## 1. The SAU shape: the VALUE descends; the CARRIER is non-descending and ESSENTIAL

The SAU certificate is `U ↛_q , C(U) ↓_B a^♯` (Why-Math / Non-Descending Objects). The **value** `C(U)` (a trace/norm/**root** — e.g. a mass) is *supposed* to descend to an ordinary lower answer; it may even equal a value computable by standard means. What must be **non-descending** is the **carrier** `U`, and it must be **essential**: by **Essential Boundary Necessity**, the accepted answer must depend on hidden promoted support that **cannot be removed or replaced by lower-visible data** while preserving the interface, answer, rules, and audit. Only the descended `C(U)` is claimed at the lower layer (no-overread), and the value must not be smuggled in (no-smuggle).
- **Corollary (mis-typing to avoid):** demanding a "non-descending scalar" is the wrong target. The scalar descends; the carrier must be non-descending + essential.

## 2. Essentiality is PROFILE-relative — two distinct notions

SAU saturation is defined relative to a **frozen lower problem profile** (theory, instrument, candidate class, accepted-answer type, defect, threshold) — it is *not* an absolute impossibility claim. Two essentiality notions follow:
- **Structural essentiality:** the value does not factor through the lower quotient (`Q⁰`) — the dominant invariant genuinely needs the promoted distinctions.
- **Budget-relative essentiality:** the carrier is the *only admissible way to obtain the value within the declared budget*. On a **tiny instance a direct lower computation always reproduces the value**, so the carrier is never budget-essential there; budget-essentiality can appear only at **scale**.
- **Candidate class must admit ALL lawful competitors** (P/NP-under-Closure: the instrument fixes the machine class and admits every lawful machine — dense diagonalization, sparse/Krylov, tensor-network/MPS/DMRG, variational, stochastic, …). SBT is essential **iff every lawful competitor fails within budget**. Never exclude a method because it would defeat SBT.

## 3. Transport-null vs mass-bearing (the projective MBO)

- **Transport-null trap:** if a witness identity equates two events under the **complete** open-boundary transport tensor, then because slab gluing is **linear** in that tensor, *every* continuation gives equal responses → ablating the distinction changes no future → it cannot change the decay LAW. A complete-transport identity is **always** transport-null and never mass-bearing. Do not seek another such identity.
- **Mass-bearing target (Holonomy):** the opposite kernel — **same current shadow, different future projective law** (`h ≡cur h' ∧ ¬(h ≡pred h')`, predictive holonomy). The predictive quotient `M` (≡pred) strictly refines the current quotient `Q⁰` (≡cur); `M` is future-sufficient and carries native transport `T^M`.
- **The projective MBO gate:** ablating the obstruction-forced distinctions must change the **dominant decay sector / transfer root** — the projective temporal law `D_H = [(r_H T_H^n u)_n]` with **amplitude quotiented out** — not merely an amplitude, a source overlap, a transient, or a subdominant coefficient. A "dark"/zero-overlap distinction is overlap, not mass. Use several held-out depths or the exact minimal recurrence of the source-generated cyclic subspace; a single held-out depth that is already a function of the construction signature is vacuous (`D_hold ⋠ Σ_EI`).

## 4. The exact carrier is maximal — compression must change the observable surface

**Holonomy minimality:** any state abstraction preserving **all** exact future observables must factor through the predictive quotient `M`. So the exact all-future carrier **cannot** be small — expect it to track the realized support. Therefore a *commodity/budget* advantage cannot come from the exact carrier; it must come from a layer with a **coarser, task-specific observable surface** — a **mass-channel-at-defect** carrier (keep only what the gauge-invariant channel response needs, to a declared error `ε`).

**Bounded interface is a HYPOTHESIS, not a consequence of refinement** (Foundations I, D-META-BND-01): the bound `|P/∼_j| ≤ C₀(j+1)` "is not derived from refinement alone"; refinement permits exponential growth (`|X_j|=2^j`); "the linear bound must be assumed or VERIFIED in an instantiation." So "does the promoted carrier scale boundedly while the raw boundary grows exponentially?" is a real, **falsifiable go/no-go**, and an honest negative (the carrier grows like the raw boundary) is the correct result, not a failure.

## 5. The layer stack (the corpus-permitted architecture for the mass)

```
L0  local exact gauge-matter slab grammar
 └─ L1  exact predictive / structural carrier   (certification; may be exponentially large — Holonomy minimality)
       ├─ event/audit branch        (Locally-Boolean global-packaging register)
       └─ scale/value branch
 └─ L2  mass-specific scale carrier at fixed certified error (ε, B)   (observable surface = the channel response, NOT the full future tensor)
 └─ L3  run / cyclic channel carrier   (the source-generated module that carries the correlator + its transfer roots)
 └─ C(L3) = a·m_H
```
Grounded: Institutions ("above the exact carrier sits a second layer used for run-only quantities"); To_Spend ("what one layer spends to stay closed becomes the next layer's feasibility constraint"); To_Kill (layers as quotients of carriers; P4 refinement = common refinements/towers; conditions grounded one layer up; one shared rung supporting distinct branches); Foundations defect calculus (exact laws generally hold only approximately at multiscale).

## 6. Promotion and exactification gates (the carrier must be earned)

- **Promotion (Promotion_Criteria):** `Promoted ⟺ Suf ∧ Clos ∧ Stab ∧ Ctrl ∧ Hon ∧ Leg`. **Induced update law / closure** = admissible lower operations act on the package **representative-independently** (a well-defined class→class update; identified representatives stay identified after every continuation and land in the package). **Second-stage stability** = the decisive structure survives further admissible coarse-graining. A partition with future-response labels is *not* a promoted carrier without the induced update law.
- **Exactification (Carrier_Exactification):** reduce to the **minimal behavioral carrier** / reachable-image baseline `Λ*`; a candidate is **reducible** (drops out) when its states/readout/transport factor through a lower baseline. The carrier is earned only by **non-reducibility** against the lower baselines.

## 7. Registers of the one obstruction — the engine is one of several

Strict extension has several equivalent/faces, and the event-package engine is **one register, not the only certificate**:
- set-map `Δ_fact ≠ ∅` (Found III); information `CD_τ > 0` (closure deficit / No-Go Thm 8); currency `Ξ ⋠ Ω` (Adequacy); SAU `δ_fact ≠ ∅`; **Locally-Boolean** no-admissible-global-packaging (`sixbirds_event`); **Holonomy** current-equal/future-distinct; **Cantor** macro-admissibility obstruction.
- The **Cantor macro-admissibility obstruction certifies strict extension WITHOUT an event-package**. So a *feasible* `sixbirds_event` verdict can coexist with a genuine predictive/macro-admissibility obstruction — the strict-test register is upstream of the event-package register. Choose the register that fits the question; a feasible verdict in one register is not a wall (universality axiom).

## 8. The honest scope (do not overclaim)

The corpus does **not** yet contain a worked SAU landing of a *physics scalar* from a run: the cleanest proven strict extension (Cantor) yields **structural non-factorization + a thermodynamic deficit, not a clean scalar**, and explicitly parks stratumwise root separation as future work; the SM track (To_Kill) reports measured masses as **"not landed — need running"**; To_Create lands emergent **regimes, not values**. So a load-bearing mass is the **frontier this project works**, with the discipline: structural OBSTRUCTION first (surviving the false-positive controls), the carrier promoted + exactified + shown ESSENTIAL, and the value descending LAST via an audited SAU root, validated out-of-sample with a sealed comparator opened only at the end.
