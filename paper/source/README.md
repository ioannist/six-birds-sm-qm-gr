# Paper — file index and reading order

Markdown mirrors of the authoritative LaTeX paper (Version 3). One file mirrors each section or appendix; LaTeX math is
retained inline. Figures are drawn in TikZ inside the LaTeX source, so the mirrors carry their captions only; see the
PDF for the drawings. Regenerate the mirrors after a LaTeX build (cross-references are resolved from
`paper/build/main.aux`) with `python3 scripts/regenerate_paper_source.py`. `ABSTRACT.md` mirrors the abstract;
`OUTLINE.md` is a historical outline and is not regenerated.

| order | file | section |
|---|---|---|
| 0 | `00_title_abstract.md` | Title + abstract |
| 1 | `01_introduction.md` | §1 Introduction |
| 2 | `02_the_calculus.md` | §2 The Six Birds emergence calculus, in brief |
| 3 | `03_method.md` | §3 Method: finite audited carriers |
| 4 | `04_result_sm.md` | §4 Result I: a finite Standard-Model selection construction |
| 5 | `05_result_qmgr.md` | §5 Result II: QM and GR readouts and finite graph duality |
| 6 | `06_predictions.md` | §6 Three construction programs |
| 7 | `07_breadth.md` | §7 Further applications: Bell, information loss, Λ, measurement |
| 8 | `08_one_grammar.md` | §8 What the two tracks share |
| 9 | `09_scope_falsifiability.md` | §9 Scope, limits, and testability |
| 10 | `10_discussion.md` | §10 Discussion and outlook |
| 11 | `11_conclusion.md` | §11 Conclusion |
| A | `appendix_A_formal_calculus.md` | App. A — the calculus, formally |
| B | `appendix_B_reproducibility.md` | App. B — constructions and reproducibility |
| C | `appendix_C_audit_trail.md` | App. C — audit trail and review record |
| D | `appendix_D_notation.md` | App. D — notation and key numbers |
| E | `appendix_E_version_history.md` | App. E — version history |

The source of truth for current claim strength is `review_2026/CLAIMS_REGISTRY.md`, with the mathematics review in
`review_2026/mathematics_audit_20261003/`. Numerical support is in the frozen `physics_atlas/` artifacts, the versioned
repairs and probes under `review_2026/`, and `open_programs/`; Appendix B records validator coverage and its exceptions.
