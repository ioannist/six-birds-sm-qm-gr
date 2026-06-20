# Six Birds × Lattice QCD — the obstruction verdict hinges entirely on the bridge-law probe calibration, and we have bracketed it wrong in both directions; we need the correct one

Attached: `six_birds_lattice_handoff_v13.zip` — the full current state, the complete SBT corpus, and the real engine source.

We are grateful for your help. We built the route you prescribed in round 6, and we have reached a point where the obstruction verdict depends entirely on one subtle calibration we keep getting wrong. We are not asking you to confirm a guess — we have deliberately bracketed it and need your read of the bridge laws.

## Where we stand (facts)

1. We fixed the currentized-null failure you found. The four packaging contexts (`c_K`/`c_G`/`c_R`/`c_T`) are now produced by EXECUTING the P5 completion actions with context-local erasure — they are genuinely distinct member-partitions (4 of 4, not 1 of 4), and a genuine K-equal/R-distinct pair exists: an onsite-vs-stretched meson that is branchwise-equal (same `c_K` atom) but recombination-distinct (different `c_R` atoms). [step115a in the zip.]
2. We built the empirical-identity glue (keyed on bridge-law probe vectors, not carrier membership) and ran the real engine (quotient + structural). The verdict depends ENTIRELY on how we compute the bridge-law probe vectors `σ_read` / `σ_quad` / `σ_trans`, and we have now bracketed it:
   - **Coarse probe** (`σ_quad` = a histogram of `{onsite, stretched}` joint-position labels, flux-blind): the engine returns an **OBSTRUCTION** — but it is spurious. The witness identity unifies a `c_G` event of 16 members all at flux `+++` with a `c_T` event of 16 members at fluxes `++-/+--/-++/--+` — "the same event" only because the probe ignores the gauge flux. [step115b.]
   - **Full-record probe** (`σ` = the full exact record: flux word + recombination pairs + q/aq tensor positions + exact weight terms): the engine returns **FEASIBLE** — but it is spurious too. All 68 events have a unique `σ` (zero coincidences anywhere, not even within one context), so the probe is effectively extensional and no empirical identity can ever form. [step115c.]
   Both are artifacts of probe granularity. Neither is the genuine verdict.

## Why this is not acceptable

Six-birds is universal — the obstruction is there. But the verdict we obtain is entirely an artifact of how finely we probe: too coarse manufactures a fake obstruction; too fine manufactures a fake feasibility. The genuine answer requires the CORRECT bridge-law observable — what `L_read` / `L_quad` / `L_trans` admissibly identify as the same layer-event (the physical response, on which genuinely-different configurations can coincide), neither flux-blind nor the full configuration record. We have guessed this calibration wrong in both directions.

## What we are asking

What is the correct exact bridge-law observable — the admissible probe — for `L_read`, `L_quad` (OS reflected-half-slab recombination pairing), and `L_trans` (slab composition / continuation), such that two genuinely-empirically-identical events (different configurations, same admissible response) coincide while genuinely-distinct events do not? And under that correct probe, on the `D1 ×∂ D1` ℤ₂ seam with our four genuine contexts and the K-equal/R-distinct pair, does a genuine empirical identity exist that crosscuts the contexts so the real engine returns a control-surviving obstruction — or must we enrich the setup (and toward what)? We have shown both failed brackets; we need the correct calibration from your read of the bridge laws and the carrier, not a confirmation of ours.

Two things only, about how we will use your answer:
- We run the REAL engine. The obstruction must be its computed verdict under the genuine probe, not a hand-built object or a known result re-expressed.
- The goal is to FIND the route that generates the strict extension. "This seam is feasible" is incomplete unless it points at where the obstruction is.

## Where to look in v13
- The build: `lattice_qcd_layer/steps/step112d_*` (carrier), `step115a_*` (genuine distinct contexts + the K-R pair), `step115b_*` (coarse-probe spurious obstruction), `step115c_*` (full-record spurious feasibility); `lattice_qcd_layer/manager_log.md` (the full trail, incl. the probe-bracketing analysis); `SIX_BIRDS_UNDERSTANDING/`.
- The real engine: `six-birds-event-package/src/sixbirds_event/` (`audits/quotient_feasibility.py`, `solvers/structural_exact.py`, `schemas/event_package.py`, `benchmarks/parity_context_witness.py`, `vision.md`).
- The bridge laws + the carrier: `lattice_qcd_layer/steps/step106_*` (L_read/L_quad/L_trans, SE1–SE12); the complete corpus in `six-birds-papers/`.

Authority = the papers + the running engine, never a synthesis (ours included).
