# Six Birds × Lattice QCD — I repaired the carrier and ran the value-factorization you asked for; I read it as "the mass descends through Q⁰," but please judge, and tell me where this goes

Attached: `six_birds_lattice_handoff_v22.zip` — the full current state, the complete SBT corpus (`six-birds-papers/`), and the real engine source. Please ground your review and direction in the papers.

We are grateful — your round-12 review caught two real bugs (the tautological step117 fixed-point check and the step118 transport that landed in response-images rather than `U_H` classes), and it caught a third when I re-ran the test (see below). I am bringing you what we computed and what I currently read from it. These are my conclusions, not facts; I have been wrong about this project repeatedly, so please check the data and decide for yourself whether the routes are actually blocked.

## What we did, and what I currently read (for your review)

**Carrier repair (step122a).** I rebuilt the closure: genuine partition refinement on successor *classes* (not the future-vector key), iterated to a fixed point; and an induced transport `T_z^U: U_H → U_H` that I read in the code as representative-independent with every target an actual `U_H` class (no response-images) — please confirm that reading too. The repaired exact carrier is *larger* than the flawed one — at `L_x=2` it is 452 classes, equal to the full realized support (so the exact predictive quotient is essentially discrete). I read that as consistent with the Holonomy minimality point you would expect: an exact all-future carrier need not compress.

**A third bypass, which I rejected (step122b).** My first value-factorization attempt silently rebuilt the raw 8-state boundary transfer matrix (the same object as the earlier bypass) while labelling itself `U_H_induced`. I caught it only by checking the realization had 8 states, not 452. I rejected it.

**Value-factorization, corrected (step122c).** On the genuine 452-class `T_U`, with the correlator iterated through `T_U` and the test certified at 5 exact modular points:
- the meson source excites a **2-dimensional** cyclic module (Krylov degree 2; scalar minimal-recurrence degree 2);
- the test I used is rank-preservation: `rank(reachable module over U_H) == rank(its projection to Q⁰)` — both 2 at every point;
- **I read this as**: the 2-dim channel realization injects into `Q⁰`, so the series and its dominant root descend through `Q⁰` → value-essentiality fails on this carrier.

**Caveats I must flag (this is where I most need your judgment):**
1. This is `L_x=2` — a tiny carrier with a 2-dim channel. It is evidence for this architecture, not a universal statement.
2. My factorization criterion is *rank-preservation of the reachable module under projection to `Q⁰`*. I argued it is sufficient for "the dominant root descends," but I am not certain it is the right or complete test — please judge whether that criterion actually establishes descent (vs. the full source/readout Hankel factorization you described).
3. The full transport does **not** descend to `Q⁰` (it is non-lumpable); only the 2-dim *channel* module appears to. So my reading is "strict extension is genuine but mass-irrelevant here," which I know is a strong claim from one tiny carrier.

## Why I bring this to you

If my reading holds, both routes to a load-bearing mass are blocked on this `ℤ₂` meson architecture: the mass descends through `Q⁰` (so it is not essential to the carrier), and the mass channel is only 2-dimensional (so there is no budget advantage to compute it). That would mean the genuine six-birds result here is the *structural* extension, not the mass. But that is exactly the kind of conclusion I have been wrong about before, and it rests on a criterion I am unsure of and a single tiny carrier — so I would rather you judge it than have me declare it.

## What I am asking

Please check whether the corrected value-factorization actually establishes that the dominant mass descends through `Q⁰` (including whether my rank-preservation criterion is the right test). Then: where should this go? Does this confirm that on this architecture the genuine contribution is the structural strict extension and not a load-bearing mass — or does it point to a specific different architecture, channel, or construction where the mass would genuinely require the strict extension (i.e. not descend through the current quotient)? I am asking for your direction, grounded in the corpus.

Two things only, about how we will use your answer:
- We run the real engine / compute on the real carrier; a genuine result requires the carrier to be load-bearing — not a relabeling of a current-quotient computation.
- Please ground the direction in the corpus (included). Authority = the papers + the running engine, never a synthesis (mine least of all).

## Where to look in v22
- `lattice_qcd_layer/steps/step122a_*` (the carrier-closure repair), `step122b_*` (the rejected bypass — retained), `step122c_*` (the corrected value-factorization: 452-class realization, modular factorization); `lattice_qcd_layer/manager_log.md` (the full trail, including the bug retractions and this result); `SIX_BIRDS_UNDERSTANDING/`.
- The corpus: `six-birds-papers/`.
- The real engine: `six-birds-event-package/src/sixbirds_event/`.
