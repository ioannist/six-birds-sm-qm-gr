# PROG3 — track closure (2026-08-27)

**Track question** (open program 3 of `review_2026/CLAIMS_MAP.md`, P1 graph level): are the 13
P1-v3 residual-deficiency survivor carriers' kernel directions a further exact quotient (gauge), or
genuine ambiguity of the cut fingerprint?

**Answer: genuine ambiguity at the certified strength — RETYPED 2026-08-27; the controlling
statement is in the STEP 3 RETYPING section below.** [The blockquote that follows is the
historical Step-2 wording; its "complete queue-exhaustive closure ... orbits" phrase was
mistyped — the computation established directed FORWARD-reachability disjointness, not
symmetric-closure orbit disjointness.] Certified across step1_finite_range/ and step2_orbit_saturation/ (both reviewer-PASSED on
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

**Literature position** (LITERATURE.md) [CORRECTED 2026-08-27 — the original completeness
sentence here was an incorrect application and is withdrawn]: Kalman–Krauthgamer
arXiv:2112.06916, Thm 3.24 excludes only a universal local degree-k>3 star-to-clique rule in
the min-cut metric (their Open Question 4.5 leaves context-dependent/nonlocal transforms
open); it supports "Delta–Y is the only local star-mesh move available below k=4," NOT
completeness of the five-class repertoire. The
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


---

<a id="step-3-retyping-controlling-track-wording"></a>
## STEP 3 RETYPING (2026-08-27) — CONTROLLING TRACK WORDING

An external adversarial review of the published Version 3 showed the Step-2 orbit language was
mistyped (four of the five move classes are directed-only reductions in saturation_engine.py; their
exact inverse-series witness reduces back to a certified endpoint yet is absent from the
"saturated" set — reproduced on this tree). Step 3 (step3_symmetric_closure/) landed the retype
plus an upgrade attempt toward symmetric-closure orbit disjointness for {series, Delta-Y}, which
FAILED honestly at its coherence lemma with an exact counterexample. Reviewer verdict:
CODE/SCIENCE/GRADE PASS (the reviewer independently reconstructed both the L2 counterexample and
the external witness with exact arithmetic; fix round added the per-pair quantifier, inline
admission restrictions, the series-reduced-base hypothesis for L1, and five can-fail controls;
manager validator reruns reproduce all lines).

The CONTROLLING statement of the track is now the reviewer-certified two-paragraph wording of
step3_symmetric_closure/statement.md, verbatim:

> On 13 fixed exact-rational graph topologies, 19 kernel directions yield nondegenerate
> positive-capacity intervals with identical complete terminal min-cut fingerprints and unique
> active minimizers. Selected endpoints have different weights and are not related by
> terminal-label-fixed weighted automorphism. For each of the 19 corresponding base/perturbed
> pairs, a queue-exhaustive forward search under four directed reduction rules and bidirectional
> Delta-Y/Y-Delta finds the two reachability sets disjoint. The search admits only intermediate
> presentations with the unchanged complete fingerprint and unique active minimizers and
> canonicalizes them modulo terminal-label-fixed exact weighted isomorphism. This establishes
> forward-reachability disjointness only; it establishes no symmetric-closure, completeness, or
> gauge-irreducibility claim.
>
> An exact inverse-series witness proves that the symmetric closure is strictly larger than the
> computed forward sets. Series removal has a unique normal form on admissible homeomorphic
> subdivisions of the 13 pinned series-reduced carriers. However, an exact subdivided-Y-leg
> counterexample refutes the attempted series/Delta-Y projection lemma. It neither connects nor
> separates any certified endpoint pair; symmetric-closure orbit disjointness remains open.
> Kalman-Krauthgamer exclude only universal local degree-k>3 star-to-clique rules, not undeclared,
> inverse, context-dependent, nonlocal, or degenerate-intermediate transformations.

Retired phrases (no longer to be used for this result): "complete five-move-orbit-disjoint",
"complete queue-exhaustive closure ... orbits disjoint", "gauge=0", "irreducible carriers",
"provably complete at the star-mesh level".

<a id="successor-construction-target-open-door"></a>
**Successor construction target (open door):** symmetric-closure orbit disjointness under the
declared moves. The exact obstruction is located: the subdivided-Y-leg / Y-Delta interaction
(l2_counterexample_step3.csv) defeats series-normal-form projection; any successor must handle
that interaction (or find an invariant that survives it).

Artifacts: step3_symmetric_closure/ (validator: run_step3.py --self, 19 fibers + 5 controls +
external-witness regression; external review materials in external_input/).
