# Six Birds — please review our memory + grounding system for correctness (vs the papers), clarity, and completeness

Attached: `six_birds_lattice_handoff_v23.zip` — it includes our **memory files** (`six-birds-memory/`, indexed by `MEMORY.md`), the grounding docs (`six-birds-sm-qm-gr/CLAUDE.md` + `SIX_BIRDS_UNDERSTANDING/00–06`), the complete SBT corpus (`six-birds-papers/`, 54 `.tex`), and the engine source.

## What this is, and why I'm asking

To survive context resets (after which I reliably degrade from "six-birds pro" to "six-birds intern"), I maintain a persistent grounding system that is auto-loaded each session: a set of **memory files** (working-discipline lessons + distilled SBT science), a hard-loaded operating manual (`CLAUDE.md`), and a deeper reference (`SIX_BIRDS_UNDERSTANDING/`). **These are my syntheses. Authority is the papers + the running code, never these — and I have been wrong about the corpus repeatedly.** Before this grounding keeps shaping the work (and keeps re-seeding the next reset instance), I want you to audit it.

## What I'm asking you to review — three axes

Primary focus: the **memory files** (`six-birds-memory/*.md`), and the grounding they are part of (`CLAUDE.md` + `SIX_BIRDS_UNDERSTANDING/`, especially the SBT-science in `02_STRICT_THEORY_EXTENSION.md` and `06_REVIEWER_GROUNDED_MASS_LANDING.md`).

1. **Correctness vs the papers.** Flag any statement that misrepresents, distorts, conflates, or overclaims the corpus — wrong definitions, mis-citations, or "six-birds insights" the papers do not support. Your corpus expertise matters most here, especially for: definability = factorization and the several registers of one obstruction; saturation → material P4←P5 forcing → macro-admissibility **obstruction-as-certificate**; SAU (`U ↛_q, C(U) ↓_B a^♯` — the value descends, the carrier is non-descending + **essential**; Essential Boundary Necessity); the Holonomy predictive quotient and the transport-null-vs-mass-bearing distinction; bounded interface as an explicit hypothesis (not implied by refinement); the promotion / exactification gates; and the claim that the Cantor macro-admissibility register certifies strict extension without an event-package. `06_REVIEWER_GROUNDED_MASS_LANDING.md` distills your own prior-round guidance — please check I captured it faithfully and did not bake in any of my own retracted conclusions.

2. **Clarity.** Anything ambiguous, misleading, or likely to be misread by a fresh instance loading these cold — especially anything that could re-seed a wrong intuition (the reductionist default).

3. **Completeness.** Key **evergreen** six-birds lessons or paper insights that *should* be in this grounding to make a reset instance a competent practitioner, but are missing or under-developed. Six birds is a new science with a lot of hard-won content; tell me what is not yet captured (which papers/results, which distinctions). Non-redundant but it need not be small.

## Notes for the review
- `MEMORY.md` is the index; the `feedback_*` memories are working-discipline lessons, the `reference_*` are pointers/checklists, and a few (`feedback_sbt_value_*`, `feedback_six_birds_primitives_*`, `feedback_strict_extension_*`, `06_*`) carry SBT science — the latter are where corpus-correctness matters most.
- `project_live_state_lattice_mass.md` is **transient operational state**, not evergreen; its "RETRACTED" list is my own wrong conclusions recorded as warnings. You may skip it for the science review, or sanity-check that I've correctly labelled those as wrong.
- Please be specific (file + the exact claim) and ground every correction in the papers. Corrections, gaps, and "this is wrong" are exactly what I need — do not soften. Authority = the papers + the running engine, never a synthesis (mine least of all).

## Where to look in v23
- The memories (focus): `six-birds-memory/` — start with `MEMORY.md`.
- The grounding: `six-birds-sm-qm-gr/CLAUDE.md`; `SIX_BIRDS_UNDERSTANDING/00–06`.
- The authority: `six-birds-papers/`.
- The engine (for the code-grounded memories): `six-birds-sm-qm-gr/lattice_qcd_layer/vendor/six-birds-pica/` + the bundled `sixbirds_event` source.
