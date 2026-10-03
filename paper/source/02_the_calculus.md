# The Six Birds emergence calculus, in brief

This section is self-contained and assumes no prior exposure to the framework. The formal development is in the
foundations papers (Foundations II–IV [@Tsiokos_FoundationsII; @Tsiokos_FoundationsIII; @Tsiokos_FoundationsIV];
*Foundations of Emergence Calculus* [@Tsiokos_FoEC]; *Why Mathematics Even Works* [@Tsiokos_WhyMath]),
and Appendix A states every formal object used here. What follows is the
minimum needed to read the rest of the paper.

## Layers, quotients, and descent

Physical description is layered [@Anderson1972]: thermodynamics sits over statistical mechanics, hadrons over
quarks, classical fields over quantum states. The calculus models a layer as a *quotient* of a finer description.
Three ingredients are needed:

- a **carrier** $H$, the set of finer-grained configurations (microstates, field configurations, tensor data);
- an **access map** $q:H\to Q$, a surjection that forgets what the layer cannot see, so that two
   configurations look identical to the layer exactly when $q$ sends them to the same point;
- a **readout** $t:H\to T$, a quantity one would like to evaluate.

The question asked again and again in this paper is whether the readout **descends** to the layer, that is,
whether the layer can compute it:
$$
\begin{aligned}
t \text{ descends through } q
&\iff q(h)=q(h') \text{ implies } t(h)=t(h') \text{ for all } h,h'\in H\\
&\iff t=\bar t\circ q \text{ for some } \bar t:Q\to T .
\end{aligned}
$$
When descent fails, the failure is recorded as an **obstruction set**
$$
\mathcal O_q(t)=\{(h,h') : q(h)=q(h')\ \text{and}\ t(h)\neq t(h')\}.
$$
Each pair in it is a *witness*: two configurations the layer cannot tell apart that nonetheless differ in $t$.
Figure 2 shows the idea on a toy carrier. When the carrier is a finite set, these sets can be enumerated exactly, and many of the constructions below reduce
to showing that a particular obstruction set is empty or not. Where the configuration space is not finite (real
capacities on a fixed graph, or real matrices of fixed size), the corresponding statements are proved as general
theorems and only their finite instances are checked by computation.

The same test compares two maps on one carrier. For $\pi_0,\pi_1$ defined on $S$, the **factorization
defect** is
$$
\Deltafact(\pi_0,\pi_1)=\{(s,s') : \pi_0(s)=\pi_0(s')\ \text{and}\ \pi_1(s)\neq\pi_1(s')\},
$$
and $\Delta_{\mathrm{fact}}\neq\varnothing$ exactly when $\pi_1$ is *not* a function of $\pi_0$. This elementary
equivalence (Appendix A.2) does a great deal of work.
In Section 4 it sorts symmetry-breaking branches into
clean and breaking ones; in Section 5
it shows that a gravitational readout is not a coarse-graining of a quantum one. Using the same test in both places does
not identify the physical objects involved.

> **Figure (drawn in TikZ; see the PDF).** **Descent and obstruction on a toy carrier.** Boxes are the fibers of the access map $q$: sets of
configurations that the coarse layer cannot distinguish. Colors are values of a readout $t$. (a) Every fiber is
one color, so the layer can compute $t$. (b) One fiber contains two colors; the pair $(h,h')$ is a witness in the
obstruction set. The factorization defect $\Delta_{\mathrm{fact}}(\pi_0,\pi_1)$ is the same construction with $q=\pi_0$ and
$t=\pi_1$.

## Six role names

The calculus files its judgments under six **primitive roles** $\mathbb P=\{P_1,\dots,P_6\}$, which name the
recurring ways in which layers relate (Foundations III):

| role | name | what it asks, and where it appears here |
| --- | --- | --- |
| $P_1$ | descent | does a property pass through a quotient? (every descent and obstruction test) |
| $P_2$ | representability | what can a layer admissibly express or select? (the SM selection layer, Section 4) |
| $P_3$ | route mismatch | do two routes to “the same” object fail to commute? (the quantize/curve pair, Section 5.1) |
| $P_4$ | refinement | does one layer refine another? (common refinements; the $SU(5)$ frame and the QM–GR parent) |
| $P_5$ | packaging | is structure closed into an auditable unit? (closure chains and record packets) |
| $P_6$ | audit | was anything smuggled between layers? (the checks of Section 2.4) |

The six are role names, not an algebra, and the calculus says so formally. Foundations III proves that no total binary
operation on the six labels can decode the status of a typed judgment: it exhibits two judgments with the same pair of
labels but different statuses, so status is not a function of the pair. (This is weaker than saying that no binary
operation on six symbols exists, which would be false.) Nor does the calculus claim that all of physics decomposes into
six primitives.

On top of the roles sits a catalog of **structural laws** (“F-laws”, Foundations
IV [@Tsiokos_FoundationsIV]): statements about quotients and closures that hold on any substrate satisfying their
hypotheses. Each law used here has a one-line form in Appendix A.5,
together with the inputs it needs. Briefly:
F23 (probability as a stable measure on an unresolved fiber, given that measure);
F26/F47 (contingency and fine-tuning);
F27 (conservation as descent through a supplied orbit relation);
F34 (information loss as a nonempty obstruction set);
F37 (complementarity as the absence of a joint quotient in a declared admissible class);
F39 (entropy as fiber volume, under its stated chain-rule premises);
F48 (topological obstruction as a nontrivial gluing class);
F49 (common-source factorization of correlations);
F50 (background selection: necessary, moduli, or vacuum);
F51 (unification as common refinement).
A law supplies a form, not its premises: wherever one is used, the measure, orbit relation, admissible class, or
gluing data it needs is either constructed or named as an input.

## What counts as a result: grades

Because the calculus is built to audit claims, every result carries a grade (a *landing mode*), and the grade
is part of the result:

- **COMPUTE**: a number, relation, or verdict drops out of the construction.
- **SELECT**: the construction picks a structure out of a declared space, on declared conditions.
- **RECOGNITION**: a known result is reproduced as an instance of a law, without the target being used as an
   input (for example the min-cut/LP identity of Section 5.4).
- **FORBIDDEN RULE / DEMARCATION**: a configuration is excluded, or a quantity is classified as law-fixable
   versus contingent, with a control on which the verdict comes out the other way.
- **PROVE-BLIND** and **GROUND** complete the vocabulary but are not used: no result here proves that a
   quantity is undeterminable on a declared class, and no condition is supplied as the shadow of a named higher source.
   The two natural candidates for GROUND are stated as hypotheses or open programs
   (Sections 4.5 and 5.3).

The grades keep three distinctions explicit: a selection is not a derivation, a recognition is not a discovery, and a
forbidden rule on a toy carrier is not a fact about nature. Attaching a grade cannot rescue a claim whose carrier,
quantifier, or bridge to physics has not been built.

## Guarding against smuggled conclusions

Any flexible framework risks building its conclusion into its premises. The audit role $P_6$ is a set of checks
against this, mechanical where they are implemented. A quantity may not be *defined* to equal its target
(anti-tautology). Each hypothesis must be satisfiable by some structure that violates the conclusion
(anti-circularity). Imported machinery is frozen and pinned by hash, so it cannot be retuned toward an answer. Every
positive claim needs a **can-fail control**, a configuration on which the claim comes out false, which shows that
the test actually discriminates. Section 3 describes how
these checks operated in practice, including the many cases in which they rejected our own constructions.
