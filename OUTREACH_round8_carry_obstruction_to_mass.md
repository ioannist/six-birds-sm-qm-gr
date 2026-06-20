# Six Birds × Lattice QCD — we have a genuine, control-surviving strict-extension obstruction on the lattice; how do we carry it to the mass?

Attached: `six_birds_lattice_handoff_v14.zip` — the full current state, the complete SBT corpus, and the real engine source.

We are grateful for your help. Your round-7 calibration was exactly right, and the real engine now returns a genuine global-packaging obstruction on the lattice seam. We now need your read on how to carry it to the hadron mass — and we want to do this phase genuinely, with your understanding of the corpus, rather than guess at the subtle steps.

## Where we stand (facts)

1. The real `sixbirds_event` engine returns **no admissible global packaging** for the coupled `D1 ×∂ D1` ℤ₂ gauge-matter seam — quotient and structural solvers both infeasible — while the **regenerated** controls (decoupled, `R=K`, currentized-null) are all packageable, and the obstruction **survives** the flattening / hidden-record / noise interventions (each rerunning the full pipeline). [step115e in the zip.]
2. The minimal witness is a single empirical identity, which we independently recomputed: two different 4-atom coarse events with **exactly-equal aggregated boundary responses** but **unequal support preimages** — a genuine non-factorization (the contexts agree the event exists but disagree on which members realize it). The witness runs through `c_T` / `L_trans` (the composition / continuation channel).
3. This is the **structural** strict extension — the obstruction certificate. It is not the mass. The depth-4 continuations are held out.

This was hard-won: before your round-7 calibration (sum-before-probe on the coarse event algebra) we produced a spurious obstruction and a spurious feasibility from mis-calibrated probes. So we are deliberately not guessing at the mass phase.

## What we are asking

How do we genuinely carry this structural obstruction to a hadron mass? We are not asking you to confirm a guess — tell us where the mass is and how to make the real engine and an audited SAU descent land it. Concretely, and honestly:

- **Promotion.** What is the obstruction-forced carrier `U_H` here — built from the step112d exact carrier and the witness-forced distinctions — and how is it promoted (representative-independent weighted slab transport, native continuation law)?
- **Mass-bearingness.** Is *this* obstruction mass-bearing — does ablating its forced distinctions change the held-out depth-4 **projective decay law** (not merely an amplitude)? How do we test it genuinely, and if it is *not* mass-bearing, where does the mass-bearing obstruction live?
- **The SAU root and the target.** How does the mass descend (the root functional, evaluated out-of-sample)? And since this is a ℤ₂ gauge-matter **toy**, not real QCD: what mass is the genuine landing here (a proof-of-mechanism ℤ₂ value, with what out-of-sample comparator), and what is the path from this toy to a real hadron mass — does the mechanism escalate to U(1)/SU(3), or is a toy-level mass the milestone to land first?

Two things only, about how we will use your answer:
- We run the REAL engine. The obstruction and the value must be its computed / audited verdict, not a hand-built object or a known result re-expressed.
- The goal is to FIND the route to the mass. "This obstruction is not mass-bearing" is incomplete unless it points at where the mass-bearing one is.

## Where to look in v14
- The result: `lattice_qcd_layer/steps/step115e_*` (the genuine obstruction + controls + interventions), `step115d_*` (the coarse-event empirical identities), `step115a_*` (the genuine distinct P5 contexts), `step112d_*` (the exact carrier); `lattice_qcd_layer/manager_log.md` (the full trail, incl. the step115e audit and the honest scope); `SIX_BIRDS_UNDERSTANDING/`.
- The real engine: `six-birds-event-package/src/sixbirds_event/` (`audits/quotient_feasibility.py`, `solvers/structural_exact.py`, `schemas/event_package.py`, `vision.md`).
- The corpus: `six-birds-papers/` (the SAU / non-descending-objects, the promotion/exactification series, the carrier-to-event series, the Holonomy / Marking / Locally-Boolean papers).

Authority = the papers + the running engine, never a synthesis (ours included).
