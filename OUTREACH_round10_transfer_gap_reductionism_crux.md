# Six Birds × Lattice QCD — the mass-bearing carrier reduces to the lattice transfer gap; is a NON-DESCENDING dominant scalar achievable, or does this confirm the scalar-landing is beyond strict extension?

Attached: `six_birds_lattice_handoff_v16.zip` — the full current state, the **complete SBT corpus** (`six-birds-papers/`), and the real engine source. **We ask that you ground your answer in the papers.**

We are grateful for your help. We built the predictive-carrier route from your round-9 read all the way to the cyclic recurrence, and we have reached what looks like the project's deepest question. We would rather you tell us "the goal is not achievable as posed, and here is why in the corpus" than route around it.

## Where we stand (facts, verified)

Following round 9: we promoted the fixed-point predictive quotient `M_H*` (it strictly refines the current quotient `Q⁰`; `Q⁰` has **no** closed transport while `M_H*` has native closed transport — the macro-admissibility / transition strict extension is genuine and discriminated), exactified the minimal weighted meson carrier `U_H`, built its native transport `T_H`, and derived the exact cyclic (Krylov) recurrence of the meson correlator.

1. **The carrier's native-transport recurrence IS the lattice transfer-matrix spectrum.** Exactly: the vacuum recurrence is `χ₀ = λ − 4·cosh²β`; the meson recurrence is a degree-8 characteristic polynomial in `(cosh β, sinh β, κ)`. So the candidate mass `−log(ρ_H/ρ₀)` is the lattice meson transfer gap, and "carrier → native transport → dominant root" is a Krylov diagonalization of the lattice transfer operator.
2. **The predictive distinction appears to be subdominant, not the mass.** The projective-MBO test (sampled-depth first, then the definitive cyclic recurrence, which we could not yet complete over all carrier classes) indicates the projective meson decay law **factors through `Q⁰`** — the **dominant** decay root looks determined by the current quotient, while the strict-extension refinement (`M_H*` over `Q⁰`) lives in the **subdominant / overlap** structure.

## Why this is not satisfactory

By the Strict Audited Utility discipline — **Essential Boundary Necessity** in *The Usefulness of Non-Descending Objects* — a strict-extension value must **not** descend through the lower theory. If the **dominant** mass descends through `Q⁰`, then the number we would report is the reductionist transfer gap: a lattice computation with six-birds labels, not a genuine strict-extension value. The strict extension is real for the **full** transport, but the scalar we care about (the mass) appears to be a shadow of the current quotient. We will not manufacture a transfer gap and call it a six-birds mass — a toy that "works" this way has no load-bearing contribution.

This also matches what the corpus already says: the cleanest proven strict extension (the Cantor shell) yields **structural** non-factorization plus a thermodynamic **deficit** object, not a clean scalar, and parks stratumwise value separation as future work; and the SM demarcation track reports measured masses as *"not landed — need running."* So reading a scalar mass off a strict extension appears to be beyond what the corpus currently proves.

## What we are asking (please ground in the papers)

Is there a genuine six-birds mechanism by which a strict extension produces a **non-descending dominant scalar** — two **current-equal** configurations carrying genuinely different **dominant** masses (a predictive-holonomy mass), so that ablating the obstruction changes the **dominant decay sector** and not merely a subdominant coefficient or a source overlap — or does the present evidence confirm that the **dominant mode always descends** through the current quotient, so that the scalar-mass landing is beyond strict extension and the genuine six-birds contribution here is the **structural** strict extension plus the demarcation/audit, not the scalar?

- If a non-descending dominant scalar **IS** achievable: what in the corpus shows it, and what is the concrete object / locus that carries it? We are not asking you to confirm a guess — point us at the mechanism the papers support.
- If it is **NOT** — if the honest reading is that the dominant scalar descends and the mass-via-run is genuinely beyond the strict-extension calculus — please say so directly and grounded in the papers. **That is a result we need, not one we will resist.**

Two things only, about how we will use your answer:
- We run the REAL engine / compute on the real carrier. A genuine six-birds mass must be a **non-descending** value (essential — not a function of the current quotient `Q⁰`), not the lattice transfer gap re-expressed.
- **Ground the answer in the corpus** (included in the zip). Authority = the papers + the running engine, never a synthesis (ours included).

## Where to look in v16
- The build: `lattice_qcd_layer/steps/step116c_*` (the macro-admissibility obstruction), `step117_*` (`M_H*` promotion; `Q⁰` has no closed transport), `step118_*` (the exactified meson carrier `U_H`), `step119_*` + `step119b_*` (the projective MBO; the transfer-spectrum recurrence `χ₀=λ−4cosh²β`, meson degree-8); `lattice_qcd_layer/manager_log.md` (the full trail incl. the reductionism diagnosis); `SIX_BIRDS_UNDERSTANDING/`.
- **The corpus — please ground here:** `six-birds-papers/` — esp. *The Usefulness of Non-Descending Objects* (SAU / Essential Boundary Necessity), the *Cantor shell* strict-extension paper, *Holonomy with Memory* (predictive quotients), *To Kill Three Stones* (SM demarcation: masses "not landed — need running"), *To Create a Stone* (emergent regimes, not values).
- The real engine: `six-birds-event-package/src/sixbirds_event/`.
