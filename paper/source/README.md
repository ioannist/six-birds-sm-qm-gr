# Paper — file index and reading order

Version-2 semantic mirrors of the authoritative LaTeX paper. One file mirrors each section or appendix; LaTeX math is
retained inline and figures point to `paper/figures/`. Regenerate the mirrors with
`python3 scripts/regenerate_paper_source.py`. `ABSTRACT.md` mirrors the corrected abstract; `OUTLINE.md` records the
corrected section architecture.

| order | file | section |
|---|---|---|
| 0 | `00_title_abstract.md` | Title + abstract |
| 1 | `01_introduction.md` | §1 Introduction |
| 2 | `02_the_calculus.md` | §2 The Six Birds emergence calculus, in brief |
| 3 | `03_method.md` | §3 Method: finite audited carriers, adversarial self-correction |
| 4 | `04_result_sm.md` | §4 Result I — the Standard Model as a selection layer |
| 5 | `05_result_qmgr.md` | §5 Result II — QM↔GR as a common refinement |
| 6 | `06_predictions.md` | §6 Three former predictions: corrected status and open programs |
| 7 | `07_breadth.md` | §7 Breadth: Bell, black-hole information, Λ |
| 8 | `08_one_grammar.md` | §8 Cross-track ties, and the one-grammar thesis |
| 9 | `09_scope_falsifiability.md` | §9 Scope, limits, and falsifiability |
| 10 | `10_discussion.md` | §10 Discussion and outlook |
| 11 | `11_conclusion.md` | §11 Conclusion |
| A | `appendix_A_formal_calculus.md` | App. A — the calculus, formally |
| B | `appendix_B_reproducibility.md` | App. B — toy constructions & reproducibility |
| C | `appendix_C_audit_trail.md` | App. C — adversarial audit trail (what was rejected) |
| D | `appendix_D_adversarial_review.md` | App. D — adversarial review record |
| E | `appendix_E_notation.md` | App. E — notation & the six primitives at a glance |

The source of truth for Version-2 claim strength is `review_2026/CLAIMS_MAP.md`, revision 3. Numerical support is in the
frozen `physics_atlas/` artifacts and the versioned repairs/probes under `review_2026/`; Appendix B records validator
coverage and its exceptions.
