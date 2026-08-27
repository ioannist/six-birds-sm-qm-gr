# PROG3 — prior-art check (2026-08-27, Opus survey via paperclip; manager-digested)

Question Q: when does the all-subset terminal min-cut fingerprint determine a weighted graph up
to exact local moves? (Successor of review_2026/probes/p1_kernel_quotient/ — 13 five-move
irreducible survivors, named K2,3 candidate.)

VERDICT: PARTIALLY_SOLVED in the literature; the move-generation/uniqueness question is OPEN for
min-cut. Key findings (paper quotes CHECKED by the surveyor unless marked INFERRED):

1. The fingerprint object IS the literature's "terminal cut function" / mimicking network
   (Hagerup et al.; Krauthgamer-Rika arXiv:1207.6246; Khan-Raghavendra-Tetali-Vegh
   arXiv:1207.6371). That literature proves SIZE bounds only; the local-move uniqueness question
   is not posed there.
2. Realizability of fingerprints is characterized only for |T| <= 5 (CSWZ00; Chen-Tan
   arXiv:2310.11367 lists |T| = 6 as open). Our survivors have b = 6,7,8 — inside the
   uncharacterized regime.
3. STRONGEST RESULT: Kalman-Krauthgamer "Flow Metrics on Graphs" (arXiv:2112.06916) Thm 3.24 —
   for every k > 3 there is NO local k-star-mesh transform preserving min-cut (Lemma 3.26 =
   CSWZ00 Lemma 4). So the five-move repertoire is essentially the complete LOCAL star-mesh
   repertoire; a "sixth local move" of that type cannot exist. This rationalizes the v3
   EXPLAINS_NONE outcome. Non-local / non-star-mesh moves are not excluded.
4. Electrical analogue fully solved UNDER CIRCULAR PLANARITY (Curtis-Ingerman-Morrow;
   Colin de Verdiere-Gitler-Vertigan via Kenyon-Wilson arXiv:1411.7425: five transformations,
   minimal networks unique up to Y-Delta, medial strand matching = complete invariant;
   Lam-Pylyavskyy cell structure). OFF circular planarity uniqueness FAILS: Levy
   (arXiv:1410.5903) exhibits a fixed graph with a 3-to-1 response-matrix fiber. Our survivors
   are K2,3 / W4-based — outerplanarity obstructions, i.e. plausibly outside the circular-planar
   hypothesis (INFERRED per-carrier, not yet verified). Literature-informed prior: the survivors
   are GENUINE AMBIGUITY, not gauge.
5. Holographic entropy graph-model papers (arXiv:2512.18702, 2512.24490, 1505.07839, 2102.07535,
   2204.00075): existence/realizability only; zero matches for uniqueness/degeneracy content.

SHARPEST REFORMULATION: the fingerprint map w -> (mincut(S))_S is piecewise-linear; the kernel we
computed is the lineality space of a maximal cell of its polyhedral fan. Q becomes: for an
irreducible carrier with unique minimizers, is that lineality space tangent to the orbit of an
exact move? Electrical answer: YES under circular planarity, NO in general. Min-cut/tropical
case: open. Sub-questions: (i) a min-cut analogue of the medial strand-matching invariant
(candidate: the active-cut combinatorial type); (ii) fingerprint-image characterization at
k >= 6 (Chen-Tan open problem).

ACTIONABLE CAVEATS FOR STEP 1:
- A first-order Jacobian kernel is NOT ambiguity: a null direction must stay null over a finite
  weight range AND land on a non-equivalent network.
- Three survivor rows have minimum_unique_cut_margin ~ 4.9e-10 / 4.1e-10 / 4.6e-9 — float
  tolerance; their unique-minimizer status must be re-established in exact rationals before they
  are counted.

UPDATE 2026-08-27 (post STEP1 + review): the off-circular-planarity prior in item 4 is now stale in
one direction — STEP1 found 0/13 raw carriers circular planar but 7/13 reduced presentations ARE
circular planar, and those rows still carry exact min-cut fibers. The electrical uniqueness theorem
is not directly applicable (observable = terminal min-cut function, not a Dirichlet-to-Neumann
response matrix; electrical criticality unchecked), so this is NOT a counterexample to it — but
circular planarity alone does not remove min-cut fibers.
