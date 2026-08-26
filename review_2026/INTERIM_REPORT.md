# Interim consolidated report — post-publication verification review
**As of 2026-08-26 (late), 23 Eddy rounds + 14 repair packets.** ALL 23 result units reviewed; repair phase in its final iterations. Working docs: REVIEW_PLAN.md,
REVIEW_LEDGER.md (per-unit detail), FINDINGS.md (infra defects), manager_log.md (full trail),
repairs/ and probes/ (new constructions). Paper edits deferred throughout; this report is the input
for that later stage.

## The repo-wide pattern (verified in every failing unit)
The finite arithmetic is almost always sound, deterministic, and reproducible (132/132 validators
pass; scratch rebuilds byte-identical or FP-noise). The failures sit one level up, in a single
recurring shape: **the load-bearing structure is asserted rather than computed** — hardcoded data
(SU(5) eigenvalues, SM rosters, record channels), literal verdict booleans (competitor "defeats",
audit gates, door tests), prose derivations in CSVs, and validators that re-read stored summaries
instead of recomputing. The repair pattern is correspondingly uniform: construct the object, compute
the predicate — and where done, several claims land at equal or GREATER strength.

## Scoreboard by unit

| Unit | Verdict | One-line status |
|---|---|---|
| P1 entanglement≠geometry | Published kernel = parameterization gauge (confirmed twice; probe carriers also gauge under exact quotients) | Graph-level route closed at claimed strength; landing = active-cut irreducibility search (specced) or state-level construction (specced) |
| P2 BMV-null | Forcing step absent (channel hardcoded; geometry-diagonal coherent countermodel verified) | Surviving: conditional LOCC example. Repair = derive record-formation from upstream (open construction) |
| P3 record-stability | Table flat-wrong → repaired (proxy) → grammar ablation refuted it → refutation overturned (spectator-Cartan bias) → restoration overturned (missed scalar-dressed records) | UNCERTIFIED, token-definition-sensitive; S6-v3 completeness probe decides; dynamics-based records = the remaining door |
| S1 SM selection | Published carrier unsound (conjugation defect, 9,126 alias dups); REPAIRED v1→v3: 419/195-orbit carrier, branch-complete selection | LANDED STRONGER as typed statement: clean branches = (2|3, SU(2)-active) only, robust to two-scalar sectors; FIT-WITH-CONDITIONS certified |
| S2 window+theorem | BEST published unit: step61 single-factor theorem genuine and witness-independent; step44 sound cap-conditional | Step43 counts stale (family conclusion survives); validators weak (F-008) |
| S3 ratios+spine | Published: recognition import + assigned booleans; REPAIRED: hypercharge DERIVED (centralizer), ratios computed, coset QNs + ΔB + monopole ℤ computed; graded CONDITIONAL EXACT CONSTRUCTION | New: Pati–Salam control also gives 3/8 — the ratio does NOT discriminate simple-vs-product parent (paper's 3/23 claim unsupported) |
| S4 content blindness + N_gen | REPAIRED & CERTIFIED: unique content orbit (recognition-under-template caveat typed); real mass-rank shadow (neutral deficiency = missing RH-neutrino pairing); N_gen theorem formally WITHDRAWN, replaced by the computed invariance map | Certified statements (a)(b)(c) issued |
| S5 L* layer | RoleSplit computed; architecture verdict NOT landed either way (published BudgetedRole = booleans; repair's MemoryLayer closure = tautological reachability); F47 CERTIFIED as sensitivity surface (2.247% defensible cell, realized point excluded, 0–40.6% range) | Architecture = open question, honestly typed |
| S6 memory grounding + E032 | Gauge-shadow = narrative; grammar question still live after 3 ablation rounds (see P3); E032 overgeneralized in paper | Correlation real; grounding + grammar robustness unresolved |
| Q1 carrier+theorems | Sound core (declared-access incomparability + nested control); access tuple never derived from ψ; competitor defeats = literal booleans; quantifiers unexhausted | Repair specced (field→mode provenance, partition-lattice exhaustion, generated competitors) |
| Q2 route-mismatch | FLAT-WRONG: the two completions COMMUTE exactly (manager-reproduced); 0.5 is an encoding artifact | Repair-or-retract |
| Q3 fork-over-ladder | Narrow certified PASS: q_GR not a deterministic quotient of q_QM on the declared carrier; nested control genuine; fork closure definitional | Conditional carries common-carrier + hardcoded-access assumptions |
| Q4 common-carrier GROUND | Controls test the wrong predicates (commutativity conflation; same-field identity); door test = prose booleans | Honest: plausible named recognition source, not computationally grounded |
| Q5 RT/shadow-price | REPAIRED & CERTIFIED: exact LP duality with constructed dual certificate (corrected identity); step45 Einstein leg closed negative at honest base point (conditional on pairing); step50 one-ledger refuted by gluing probe | LANDED·CONDITIONAL FINITE-GRAPH RECOGNITION |
| Q6 Born+area ledger | Downgraded (from Q5 round): shared inequality class, not one ledger | Composition-operation option in Q5-REPAIR |
| Q7 F50 Λ claim site | 15/18 split + κ boundary = solver-budget artifacts (manager-reproduced: all converge ≤120 iters) | Repair in flight (adaptive convergence + bifurcation analysis); non-uniqueness direction likely strengthens |
| G1/G2 | G1 adjudication circular; G2 honest contested toy; NEITHER is paper-load-bearing (paper's Λ site = Q7) | Repairs parked |
| A1 atlas machinery | UNFIT as prereg/blinding evidence (consistency-gate only; self-reported blinding; hardcoded map topology); FIT as internal catalog | Paper must not cite it as independent audit |
| A2 missing-layer cards | UNFIT: grades exceed reviewed reality; external gate never closed (v7 approve-w-changes, v8 needs-work, v9 blank) | Card-regrade packet queued |
| A3 retrodiction atlas | FIT (honest recovery/reframe framing throughout) | Minor path fixes |
| A4 unification atlas | Scientifically honest+severe; mechanically UNFIT (19/34 cards missing, malformed JSON) | Packaging fix queued |

## Paper corrections required (flat-wrong list; edits deferred)
1. P3 2×2 table (24/0/292/11674): "breaking" column mixes 60 evaluated + 11,614 unevaluated; capacity
   witnesses hollow. (Repaired numbers exist.)
2. S1: "11,990" denominator + "99.3% → {2|3, SU(4)}" pairing + bare-structure selection wording — all
   superseded by the branch-typed result on the sound carrier.
3. S3: "product parent yields 3/23" — matches no computation; canonical product parent (Pati–Salam)
   computes 3/8. "Non-circular recovery" must carry the parent/package/convention conditions.
4. S4: "cannot uniquely select the SM content" + "type-limit/blindness" — the two classes are one
   orbit; "N_gen blindness theorem" proves a surrogate. "Mass-matrix rank" is edge coverage.
5. Q2: "E₁E₂ ≠ E₂E₁" — the completions commute exactly on the published carrier; 0.5 is
   encoding-dependent.
6. Q5: "area = shadow price" — misidentifies the LP dual optimum as a dual multiplier; "linearized
   Einstein" leg invalid at the degenerate base point; "one ledger" (Q6) not established.
7. P1: "any non-trivial geometry" universal + "robust kernel" — kernel is gauge on the published
   carrier and on all probed carriers under exact quotients.
8. P2: "forced, not a modeling choice" + "validator fails on any T00 coupling" (it is a 6-token grep).
9. Q1/§5: theorem names ("quantum gravity is illegal", unique reconciliation) exceed the finite
   declared-access facts; E032 "strict extension of QM" exceeds the Σ_f-conditional lemma.
10. Q7: "15/18 pass / computed admissibility boundary" — solver-budget artifact (all 18 converge when
    the solver finishes); the κ tooth moves with damping.
11. S5/Result C: "one layer + currency, not two" — architecture is underdetermined/open (both the
    published verdict and the first counter-construction failed verification); 3.96% unstable.
12. sec_08 "one grammar": "forces", "foundational-grade", "universality demonstrated" — exceeds every
    reviewed unit.
13. The "adversarial review record" framing: the external missing-layer gate never issued a final
    approval (v7 approve-with-changes → v8 still-needs-work → v9 blank template).

## What has LANDED (verified constructions, new or strengthened)
- S1: branch-typed selection on a conjugation-consistent, convention-declared carrier (unique clean
  branch class; robust to two-scalar sectors). STRONGER than the published claim in uniqueness terms.
- S3: derived hypercharge/ratios/coset/ΔB/monopole (conditional on named imports) with honest claim
  ledger and mutation-hardened validators.
- P3: full-carrier proxy table with genuine anti-circularity witnesses; typed statement.
- S2: step61 theorem certified witness-independent (pre-existing, confirmed).
- S4 (pending repair): unique-orbit content selection (from the review's own finding).

## Process record
Two agent lanes (Cody implement / Eddy review), 16 review rounds, 8 repair packets, every reviewer
claim and every repair manager-verified independently (decisive computations reproduced from scratch:
P1 quotient, Q2 commutator, P3 recounts, S1 branch census, S3 validator+mutations). Infra: F-001
closed (self-containment; 132/132), F-002..F-008 tracked in FINDINGS.md.
