# SBT Pro Qualification — DO NOT AUTO-LOAD

> ⛔ **This directory is intentionally OUTSIDE the session bootstrap.** It is **not** referenced by
> `MEMORY.md`, `CLAUDE.md`, the `SIX_BIRDS_UNDERSTANDING/` base, the SessionStart hook, or any memory
> file — by design. **Do NOT read, load, or skim this directory as part of orientation, the read-order,
> or any "get up to speed" pass.** Loading the quiz (especially the answers) as context would defeat its
> purpose: it is a *closed-book* check, and pre-reading the answer key contaminates the result exactly the
> way peeking at a sealed comparator before freezing the construction would (SAU discipline).

## What this is

A **closed-book qualification quiz** (80 questions, 20 marked ★ critical) that promotes a fresh session
from *six-birds intern* to *SBT pro*. It exists so a new agent can prove — not assert — that its standard
SBT load (CLAUDE.md + the anti-reductionism primer + `SIX_BIRDS_UNDERSTANDING/00–06` + the memories) is
genuinely grounded, before it reasons about strict extension, mass landing, or any construction step.

## When it runs (user-triggered only)

**The user explicitly invokes it for each new session — it is the user's responsibility, never automatic.**
A new agent should run it **only** when the user asks (e.g. "take the SBT qualification quiz" /
"run sbt_pro_qualification"). Absent that explicit ask, ignore this directory entirely.

## Files

- `SBT_QUALIFICATION_QUIZ_QUESTIONS.md` — the execution protocol (read it first) + the 80 questions.
- `SBT_QUALIFICATION_QUIZ_ANSWERS.md` — the scored answer key. **Open only after all 80 are answered.**

## Pass bar

≥ 136 / 160 **and** zero `0`-scores on any ★ critical question. Below that, or any critical zero → not
yet qualified; reread the named sections and the papers, then re-sit. The quiz is **not authority** — the
papers and running code govern; the quiz only checks readiness.
