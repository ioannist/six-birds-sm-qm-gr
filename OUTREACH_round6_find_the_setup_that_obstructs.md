# Six Birds × Lattice QCD — we built and ran the genuine engine on a lattice slab; it returns a feasible packaging (no strict extension); we need your help finding where the obstruction is

Attached: `six_birds_lattice_handoff_v12.zip` — the full current state, the complete SBT corpus, and the real engine source (Python `sixbirds_event` + Rust `six-birds-pica` + `vision.md`).

We are grateful for your help. We have built the genuine-engine route and run it on the real engine, and we have reached a result we cannot accept. We are not asking you to confirm a guess of ours — we have deliberately not pre-supposed where the problem is. We need your full read of the framework and the engine to find it.

## Where we stand (facts)

1. We built an exact, non-descending boundary carrier for a tiny ℤ₂ gauge-matter Euclidean slab: a local gauge-dressed action, the interior integrated exactly and erased, the hadron channel's matter legs left open. [`step112d` in the zip.]
2. We mapped that carrier into the REAL `sixbirds_event` engine as a genuine `EventPackageInstance`: the four packaging contexts (`c_K` branchwise / `c_G` gauge-dressed / `c_R` singlet-recombination / `c_T` slab-composition), with the cross-context shared-event glue licensed by the `BridgeLevelLawBasis` (`L_read`/`L_quad`/`L_trans`) and exact certificates. The engine accepts the instance; its decoupled and `R=K` control packages come out packageable; and the engine itself is healthy (its full test suite passes, and on its own parity witness it correctly returns a global-packaging obstruction). [`step113`.]
3. We ran the real engine's exact-feasibility solver on the coupled package at the smallest geometry. It is **feasible** — a genuine, non-degenerate global package exists (four distinct contexts, 84 cross-context glue constraints, jointly satisfiable). The engine finds **no obstruction**. [`step114`.]

(Neutral engine facts: the exact-feasibility solver enumerates the full product over per-context outcomes, so it does not scale to large instances; the engine also has a `quotient_feasibility` path that works from trajectory signatures. Both, and the parity worked example, are in the zip for you to inspect.)

## Why this is not acceptable

Six-birds is universal: all emergence and all reality happens through it — the hadron, the mass, the new layer arise as a six-birds strict extension; nothing escapes it. A feasible packaging with no obstruction is therefore not a result we can accept — it means the strict extension we are after is simply not being exposed by what we have built. We need the genuine global-packaging obstruction — the non-extendability that forces the mass-bearing carrier into existence — computed by the real engine and surviving its controls, on the way to the hadron mass.

## What we are asking

Find where the obstruction is, and how to make the real engine return it. We do not know whether the gap is in the slab, the gauge content, the way we constructed the contexts / completions / bridge laws, the engine path we used, or something we have not seen — and we are not steering you toward any of these. Please use your full understanding of the framework and the engine (both in the zip) to tell us where the strict-extension obstruction lives and what we must build, and run through the real engine, to expose it.

Two things only, about how we will use your answer:
- We run the REAL engine. The obstruction has to be its computed verdict, not a hand-built object or a known result re-expressed. (Constructions that re-package an already-known answer have set us back before; we need the genuine engine result.)
- The goal is to FIND the route that generates the strict extension. An answer that bounds it, or concludes that some setup simply does not obstruct, is not what we need.

## Where to look in v12
- The build: `lattice_qcd_layer/steps/step112d_*` (carrier), `step113_*` (carrier→engine mapping + controls), `step114_*` (the feasible coupled test); `lattice_qcd_layer/manager_log.md` (the full trail); `SIX_BIRDS_UNDERSTANDING/` (our working notes).
- The real engine: `six-birds-event-package/src/sixbirds_event/` (incl. `solvers/structural_exact.py`, `audits/quotient_feasibility.py`, `schemas/event_package.py`, `benchmarks/parity_context_witness.py`, `vision.md`).
- The complete corpus: `six-birds-papers/`.

Authority = the papers + the running engine, never a synthesis (ours included).
