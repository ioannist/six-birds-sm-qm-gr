# Six Birds × Lattice QCD — the predictive/closure-deficit obstruction is confirmed, but the real engine returns packageable; where does the mass-bearing strict extension live?

Attached: `six_birds_lattice_handoff_v15.zip` — the full current state, the complete SBT corpus, and the real engine source.

We are grateful for your help. We built the predictive-obstruction route from your round-8 read, and we have reached a clean, verified juncture where two things we expected to coincide do not, and we do not want to resolve it by guessing.

## Where we stand (facts, verified)

We first classified the step115e obstruction exactly as you said: its witness identities equate events under the complete transport tensor (`B₂(E_K)=B₂(E_T)`, each law separately equal), so it is transport-null and not mass-bearing (step116a).

Then we searched for the predictive obstruction (`h ≡cur h' ∧ ¬(h ≡pred h')`). On a two-interface `(D1⋆D1)⋆D1` ℤ₂ gauge-matter slab:

1. **The predictive structure is genuinely present.** The predictive quotient `M` (≡pred, by all admissible continuations + readouts) strictly refines the current quotient `Q⁰` (≡cur): 376 vs 188 classes. There are concrete current-equal/future-distinct witnesses — e.g. the `pp` and `mm` flux members share one current class but split into two predictive classes. [step116b]
2. **The composition square genuinely does not commute.** Computing both routes exactly on the carrier, `Package(S1⋆S2) ≠ Recombine(Package S1, Package S2)` on **all 188** current-equal classes, and it **commutes when decoupled** (`κ=0`) — so the non-commutativity is coupling-induced, not a packaging-order artifact. The packaged future cannot close on the current quotient. [step116c]
3. **But the real `sixbirds_event` engine returns packageable.** No cross-context mixed-law `K/R/T` identity cycle closes with the route events (2516 K-candidates, 15 R-candidates searched, 0 cycles), so the engine receives no obstruction proposals and the coupled package is `exact_feasible=True`. The obstruction appears to be *internal to the composition* (the `c_T` square), not a cross-context global-packaging failure.

## Why this is not satisfactory

Your round-8 target was: *same complete lower-layer event shadow + different promoted future projective law + no admissible global package*. We now have the first two — the closure deficit and the current-equal/future-distinct structure are confirmed and discriminated — but **not** the third: the real engine does not return "no admissible global package" here. So the obstruction we can see is in the closure-deficit / macro-admissibility register, not in the engine's identity-coverage register. We do not want to (a) quietly switch to a non-engine register and call the closure deficit the strict extension without it being the right thing, nor (b) manufacture an engine obstruction by forcing an artificial instance.

## What we are asking

Given a confirmed, discriminated closure-deficit obstruction (the composition square does not commute; `M` strictly refines `Q⁰`) that the real Locally-Boolean engine does **not** register as a global-packaging failure — where does the mass-bearing strict extension genuinely live here, and what carries it to the meson mass? We are not asking you to confirm a guess; we have shown exactly what is and is not present, and we need your read of the corpus on which object is the one we promote.

Two things only, about how we will use your answer:
- We run the REAL engine / compute on the real carrier. The obstruction and the value must be a computed / audited verdict, not a hand-built object or a known result re-expressed.
- The goal is to FIND the route to the mass. A "packageable" verdict is, by our working axiom, a sign the setup is not yet right rather than a wall — so if the engine should obstruct, where is the setup that exposes it; and if the closure-deficit object is itself the mass-bearing strict extension, what makes it so.

## Where to look in v15
- The build: `lattice_qcd_layer/steps/step116a_*` (transport-null classification), `step116b_*` (M refines Q⁰; the predictive witnesses), `step116c_*` (the non-commuting composition square; the engine-packageable verdict; the empty cycle search); `step112d_*` (the exact carrier); `step106_*` (the slab grammar, the four contexts, the bridge basis); `lattice_qcd_layer/manager_log.md` (the full trail, incl. the verified step116b/c audits and the register fork); `SIX_BIRDS_UNDERSTANDING/`.
- The real engine: `six-birds-event-package/src/sixbirds_event/` (`audits/quotient_feasibility.py`, `solvers/structural_exact.py`, `schemas/event_package.py`, `vision.md`).
- The corpus: `six-birds-papers/` (the Cantor strict-extension / macro-admissibility paper; Holonomy w/ Memory; the promotion / carrier-exactification series; Locally-Boolean; Why-Math SAU).

Authority = the papers + the running engine, never a synthesis (ours included).
