# PROG3 — track closure (2026-08-27)

**Track question** (open program 3 of `review_2026/CLAIMS_MAP.md`, P1 graph level): are the 13
P1-v3 residual-deficiency survivor carriers' kernel directions a further exact quotient (gauge), or
genuine ambiguity of the cut fingerprint?

**Answer: genuine ambiguity, at the strongest strength available relative to the declared
equivalences.** Certified across step1_finite_range/ and step2_orbit_saturation/ (both reviewer-PASSED on
CODE/SCIENCE/GRADE, with independent reviewer orbit rebuilds, manager validator reruns, and a
manager-authored independent brute-force check of the named K2,3 fiber):

> For all 19 pinned exact-rational cut-fingerprint fibers (at least one per carrier, 13/13), the
> two endpoint orbits are disjoint after complete queue-exhaustive closure under the five declared
> exact fingerprint-preserving graph-move classes, modulo terminal-label-fixed exact weighted
> isomorphism. No first-four-class transition is admitted anywhere in those saturated orbits; all
> nonidentity admitted transitions are Delta–Y/Y–Delta. Transformations outside the declared
> classes and all state-level conclusions remain open.

Supporting certified facts: exact recertification of all 13 v3 survivors (the three
near-float-tolerance margins are genuinely tiny-positive; no v3 status changed); every fiber pair
has differing positive exact weights, no graph automorphism relation, and identical complete
terminal fingerprints re-established by exhaustive enumeration (never Jacobian extrapolation);
circular planarity 0/13 raw and 7/13 reduced, with the electrical (Dirichlet-to-Neumann)
uniqueness theorem explicitly not applicable — the seven reduced-circular-planar rows show
circular planarity alone does not remove min-cut fibers, and no counterexample to the electrical
theorem is claimed.

**Literature position** (LITERATURE.md): the local-move repertoire is provably complete at the
star-mesh level (Kalman–Krauthgamer arXiv:2112.06916, Thm 3.24 — no k-star-mesh transform
preserves min-cut for k > 3), so the five classes are not an arbitrary stopping point. The
fingerprint-realizability question at k ≥ 6 terminals is open in the literature (Chen–Tan
arXiv:2310.11367), and the mimicking-network literature does not pose the move-uniqueness
question. The recorded survey found no prior work exhibiting this min-cut analogue of a Levy-style
unrecoverability fiber (arXiv:1410.5903); this is a literature-position observation, not an
exhaustive priority claim.

**What this closure does NOT claim:** no irreducibility under undeclared, non-local, arbitrary
mimicking-network, continuum, or future enlarged transformation classes; no contracted-state,
quantum-entropy, or RT conclusion (PROG2 evaluated these same fibers and obtained 19/19 SPLIT
classifications at dense-numerical-evidence grade under one declared convention); no
universality beyond the 13 pinned carriers and 19 pinned directions; and no characterization of
all min-cut fibers or theorem-level complete invariant.

**Reopening doors** (out of scope for this closure; each is a well-posed successor):
1. A complete invariant / uniqueness theorem for min-cut fingerprints (CIM medial-strand
   analogue; candidate invariant: the active-cut combinatorial type).
2. Undeclared transformation classes (non-local or non-star-mesh exact moves).
3. The Chen–Tan k ≥ 6 realizability question, for which the 13 carriers are concrete data.

Track artifacts: LITERATURE.md, manager_log.md, step1_finite_range/ (19 certified fibers, exact
recertification), step2_orbit_saturation/ (complete-orbit disjointness). Validation:
`step1_finite_range/run_step1.py --self` and `step2_orbit_saturation/run_step2.py --self`.
