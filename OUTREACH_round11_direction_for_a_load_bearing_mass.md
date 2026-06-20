# Six Birds × Lattice QCD — the structural strict extension is genuine, but we have no route to a load-bearing mass; we need your direction

Attached: `six_birds_lattice_handoff_v17.zip` — the full current state, the complete SBT corpus (`six-birds-papers/`), and the real engine source. Please ground your direction in the papers.

We are grateful. Your round-10 read caught a real and serious error: our candidate mass was computed directly from the raw boundary records, bypassing the promoted carrier entirely, so the carrier was not load-bearing and the SAU essentiality field failed. We verified this against the code and the SAU definitions, and we accept it fully.

## Where we stand (verified, agreed)

- The **structural transition strict extension is genuine** and accepted: the current quotient `Q⁰` has no closed transport, the fixed-point predictive quotient `M_H*` does (`Q⁰ ⊀ M_H*`), the macro-admissibility obstruction is discriminated against the decoupled control, and the carrier is promoted and exactified.
- We now understand the SAU pattern correctly: the mass is `C(U_H)` **descending** (we accept it may equal the ordinary finite-lattice transfer gap), legitimate **only if** the carrier `U_H` is non-descending **and essential** — the answer must depend on `U_H` in a way no lower-visible computation can remove or replace.
- On this tiny ℤ₂ slab, `U_H` **cannot** be essential: the direct boundary transfer computation trivially produces the same gap (exactly the bypass you caught). So a toy mass here is, by your verdict and ours, a toy that "works" with no load-bearing contribution. It is pointless for this experiment.

## Why this is not satisfactory

The purpose of this project is to land a **hadron mass through a genuine six-birds emergence in which the strict extension / promoted carrier is load-bearing** — not a lattice transfer gap re-expressed with six-birds labels. We have established the structural extension, but we do **not** have a route by which the carrier becomes genuinely essential to the mass. We do not know where to take this, and we would rather have your direction than guess and drift again.

## What we are asking

Where should this go? What is the route — the concrete next object, locus, construction, or scale — by which a six-birds strict extension genuinely lands a hadron mass with the promoted carrier load-bearing and essential, in a way the lower-layer computation cannot replace? We are asking for your direction, grounded in the corpus.

Two things only, about how we will use your answer:
- We run the real engine / compute on the real carrier. A genuine result requires the carrier to be **essential** — not a relabeling of the direct gap.
- Please ground the direction in the corpus (included in the zip). Authority = the papers + the running engine, never a synthesis (ours included).

## Where to look in v17
- The build + the full trail (including the verified round-10 diagnosis and the corrected understanding): `lattice_qcd_layer/manager_log.md`; the steps `step116c_*` … `step119b_*`; `SIX_BIRDS_UNDERSTANDING/`.
- The corpus: `six-birds-papers/`.
- The real engine: `six-birds-event-package/src/sixbirds_event/`.
