# Introduction

Two of the deepest open problems in physics look nothing alike. The first is a *selection* problem: why the
Standard Model has the gauge algebra $\mathfrak{su}(3)\oplus\mathfrak{su}(2)\oplus\mathfrak{u}(1)$, its particular
representations, three generations, and its scales [@Weinberg1967]. The second is a *compatibility*
problem: general relativity is perturbatively non-renormalizable [@tHooftVeltman1974; @GoroffSagnotti1985], and
no quantum theory of gravity has been confirmed experimentally. This paper asks a modest question about the two: can
both be studied with one small, finite vocabulary, and if so, what does that vocabulary actually deliver?

The vocabulary comes from the Six Birds emergence calculus (Section 2).
Its working core fits in a sentence. A coarse description is a *quotient* of a finer one; a quantity of interest
either *descends* through the quotient or leaves a set of
witnesses showing that it does not; and two
coarse descriptions may share a *common refinement* that carries both. These are elementary notions. What makes
them useful here is that they can be evaluated exactly on finite carriers, so each step can be checked, controlled,
and, where it fails, recorded as a result.

A shared vocabulary is not a solution to either problem. It earns evidential weight only where it produces explicit
constructions that could have come out differently and that survive review. For that reason the paper is built
around finite, declared carriers, and every result carries a grade that states what kind of result it is. We use
the calculus's finite toolkit (obstructions, quotients, construction audit, and claim bookkeeping). We do not use its
strict-extension, reclosure, promotion, endogenous-repair, or run-level dynamical machinery, and we supply no
continuum bridge to a physical substrate.

## Main results

1. **A branch-level selection of $SU(2)\times SU(3)$** (Section 4).
   A conjugation-consistent census contains $1{,}066$ labelled genuinely chiral gauge structures ($419$ orbits under
   the declared symmetries, or $195$ under an alternative charge normalization). Within the declared representation,
   charge, field, and scalar caps, only structures with nonabelian factors of dimensions $2$ and $3$ (the
   $2|3$ family) admit a *clean* breaking branch. Every clean branch breaks the $SU(2)$ factor, and every
   $SU(4)$ branch is breaking. Every $2|3$ structure also has a breaking branch, so the selection is of a
   structure-plus-branch pair, not of a bare gauge structure. A separate witness-independent toy theorem excludes stable
   single-factor $SU(N)$ candidates.
1. **Exact unification objects, recovered rather than predicted** (Section 4.4).
   For the regular $SU(5)$ embedding, exact matrix algebra forces a one-dimensional hypercharge direction and gives
   $\sin^2\theta_W=3/8$ and $k_Y=5/3$ for the $\overline{\mathbf5}+\mathbf{10}$ package. Generator action
   identifies the $X/Y$ coset roles. The ratios do not select the parent group, since Pati–Salam also gives $3/8$.
   Under a declared content quotient, the SM and its candidate alternative are one orbit.
1. **QM and GR readouts as siblings, and a finite min-cut duality** (Section 5).
   On an abstract Boolean carrier, the declared QM and GR coordinate readouts are mutually non-factorizing: neither is a
   coarse-graining of the other, though both factor through a common refinement. A 54-record field-plus-background
   construction realizes such readouts under stated conditions. On finite graphs, exact LP certificates give
   $\operatorname{Area}(\mathrm{min\ cut})=\sum_e c_e y_e$, with the $y_e$ the per-edge shadow prices. An exact
   computation also shows that the natural “quantize” and “curve” completions on this carrier *commute*, so
   this level offers no route-mismatch explanation of why quantizing gravity is hard.
1. **Three construction programs** (Section 6).
   The first asks whether the same min-cut data can hide different geometries. Its graph-level subproblem shows that,
   for nineteen exact equal-cut pairs, the two sets of presentations reachable by forward reduction moves are disjoint.
   Whether they are disjoint under arbitrary moves in both directions remains open. Its state-level subproblem finds six
   exact pairs with identical cut and state data, all of which turn out to be gauge-equivalent tensor networks. The
   second and third programs, on whether gravity must act as a classical record channel and on which invariant
   operators persist as records, remain open. Their finite precursors are, respectively, conditional on an assumed
   channel and sensitive to how records are defined.
1. **Further applications and two toy theorems** (Sections 4,
   5,
   and 7). The single-factor exclusion and the coordinate-partition
   incomparability are genuine theorems on their toy carriers. In a toy holographic carrier, a general factorization
   theorem shows that the full boundary readout loses only gauge data, while a half-boundary readout provably loses
   physical information. Bell, cosmological-constant, and measurement rows carry their own finite grades. None
   establishes universality.

Figure 1 places these results side by side, colored by the kind of evidence behind each one.

> **Figure (drawn in TikZ; see the PDF).** **The results at a glance.** Each box is one statement, colored by the kind of evidence that supports
it. “Exact finite computation” means an exhaustive or exact-arithmetic computation on a declared finite carrier;
“theorem” means a written proof whose hypotheses are stated in the text. Every statement holds only on its declared
carrier and under its stated caps and conventions; none is a claim about nature.

**Scope.** Nothing here derives Standard-Model parameters, solves quantum gravity, proves a universal
composition law, or transfers a statement from these carriers to nature. Two words are used in a narrow sense
throughout. A *recognition* means that a known exact structure is reproduced once all named inputs are declared.
An *open program* means that the missing construction has been identified and the repository isolates exactly
what would have to be built.

**How to read the paper.** Section 2 introduces the vocabulary
with a worked picture, and Section 3 describes how
results were checked. Sections 4
and 5 present the two tracks,
Section 6 the three construction programs, and
Section 7 four further applications.
Section 8 asks what the two tracks share, and
Section 9 collects every statement with its grade and its most direct test. The
appendices give formal definitions (A), reproducibility details (B), the record of rejected constructions (C),
notation (D), and the version history (E).
