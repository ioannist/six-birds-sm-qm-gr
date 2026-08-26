# The Six Birds emergence calculus, in brief

This section is a self-contained primer; no prior exposure to the framework is assumed. The formal development lives in
the foundations papers (Foundations II–IV [@Tsiokos_FoundationsII; @Tsiokos_FoundationsIII; @Tsiokos_FoundationsIV]; *Foundations of Emergence Calculus* [@Tsiokos_FoEC]; *Why Mathematics Even Works* [@Tsiokos_WhyMath]) and is
summarized operationally in Appendix A. Here we give the minimum a working physicist needs to read Sections 4–8.

## Layers, quotients, and descent

The organizing picture is that physical description is **layered** [@Anderson1972]: thermodynamics over statistical mechanics, hadrons
over quarks, classical fields over quantum states, geometry over whatever underlies it. The calculus models a layer as
a **quotient of a carrier**:

- a **carrier** $H$ — a set of finer-grained configurations (microstates, field configurations, tensor data);
- an **access quotient** $q : H \to Q$ — the surjection that forgets what the layer cannot see (two configurations are
   layer-identical iff $q$ maps them together);
- **readouts** $t : H \to T$ — quantities one wants to evaluate.

The central, endlessly reused question is whether a readout **descends** to the layer:

$$
t \text{ descends through } q
\;\iff\;
\forall h,h':\; q(h)=q(h') \Rightarrow t(h)=t(h')
\;\iff\;
\exists\, \bar t : Q \to T,\;\; \bar t \circ q = t .
$$

When descent fails, the failure is recorded as a finite **obstruction set**

$$
\mathcal O_q(t) \;=\; \{(h,h') : q(h)=q(h') \ \wedge\ t(h)\neq t(h')\},
$$

and the pair $(h,h')$ is a *witness*: two configurations the layer cannot distinguish that nonetheless differ in $t$.
Many constructions in this paper reduce to such obstruction sets being empty or non-empty on finite carriers. The three
former forcing predictions do not follow merely from this vocabulary and are restated as open programs in Section 6.

A second reusable object is the **factorization defect** between two maps $\pi_0,\pi_1$ on a common carrier:

$$
\Delta_{\mathrm{fact}}(\pi_0,\pi_1)
\;=\;
\{(s,s') : \pi_0(s)=\pi_0(s') \ \wedge\ \pi_1(s)\neq\pi_1(s')\},
\qquad
\Delta_{\mathrm{fact}} \neq \varnothing \iff \pi_1 \not\preceq \pi_0,
$$

i.e., $\pi_1$ fails to factor through $\pi_0$ exactly when the defect is non-empty (a theorem-grade equivalence;
Appendix A). In Section 4 it classifies clean and breaking scalar branches; within the constructed $SU(5)$ frame,
generator action separately computes the $X/Y$ roles. In Section 5 it witnesses non-factorization of declared access
partitions. These uses do not identify the physical objects across tracks.

## The six primitive roles

The calculus fixes a finite alphabet of six **primitive roles**,

$$
\mathbb P = \{P_1,\dots,P_6\},
$$

naming the recurring ways layers relate (Foundations III). Operationally:

| primitive | role | one-line gloss | where it appears in this paper |
| --- | --- | --- | --- |
| $P_1$ | **descent** | a property pushes down through a quotient | every descent/blindness theorem (§4, §5) |
| $P_2$ | **representability** | what a layer can admissibly express or select | the SM selection layer (§4) |
| $P_3$ | **route mismatch** | two construction routes to “the same” object fail to commute | general mathematical definition; published quantize/curve pair corrected in §5.1 |
| $P_4$ | **refinement** | one layer refines another (common refinements, towers) | the QM–GR parent $L$ (§5.2), GUT$\leftrightarrow$SM (§4.4) |
| $P_5$ | **packaging** | closure of structure into an auditable unit | closure chains, record packets (§4.5, §§6.2–6.3) |
| $P_6$ | **audit** | the ledger check that nothing was smuggled between layers | the anti-smuggling discipline (§3) |

Two disclaimers are part of the calculus itself (and are proved, not just stated, in Foundations III): the labels form
**no algebra** — there is no total operation $*:\mathbb P^2 \to \mathbb P$, and a “no total six-symbol algebra” theorem
forbids reading interactions off the labels alone; and there is **no universal reduction claim** — the calculus does not
assert that all of physics decomposes into six primitives. The six are role names under which finite, typed,
individually-audited judgments are filed.

On top of the primitives sits a catalog of **layer-agnostic structural laws** (“F-laws”, Foundations IV [@Tsiokos_FoundationsIV]): theorem-grade
statements about quotients and closures that hold regardless of substrate, each verified formally and instantiated
across multiple sciences. The ones used in this paper (one-line forms in Appendix A): F23 (probability as a stable
measure on an unresolved fiber), F27 (conservation as orbit descent), F34 (information loss as an obstruction-set
verdict), F37 (complementarity as non-existence of a joint quotient), F39 (entropy as fiber volume), F47/F26
(fine-tuning and contingency: no value-law lands on a contingent selection), F48 (topological obstruction/gluing), F49
(common-source/nonlocal correlation normal form), F50 (vacuum/background selection: necessary vs moduli vs vacuum), F51
(unification as common refinement).

## What counts as a result: landing modes

Because the calculus is built to *audit* claims, every result in this paper carries one of a small set of grades — the
**landing modes** — and the grade is part of the result:

- **COMPUTE** — a relation, number, or verdict drops out of the construction (e.g., the factorization defects of §4–5).
- **SELECT** — the machinery picks a structure out of a space, *on declared conditions* (e.g., the SM gauge algebra,
   conditional on clean-separation).
- **PROVE-BLIND** — a proof, on a declared class, that the chosen predicates cannot determine a quantity. The
   published generation-count example is withdrawn; the grade remains part of the formal vocabulary.
- **GROUND** — a condition not derivable within its own layer is supplied as the *down-shadow of a named higher source*,
   with the source and its warrant declared. A GROUND landing is conditional and is tagged as such. The two principal
   published GROUND examples fail post-publication review and are now hypotheses/open programs (§§4.5, 5.3).
- **RECOGNITION** — a known result is shown to be a special case of one of the calculus's laws, *non-circularly*: the
   law's machinery reproduces it without the target being used as the computed quantity (e.g., the finite-graph
   min-cut/LP certificate of §5.4, conditional on its graph model).
- **FORBIDDEN-RULE / DEMARCATION** — the calculus forbids a configuration, or classifies a quantity as law-fixable
   versus contingent, with an explicit can-fail control. Its validity is only as broad as the enumerated class.

The grades keep these distinctions explicit: a SELECT is not a derivation, a RECOGNITION not a discovery, and a
toy-level FORBIDDEN-RULE not a fact about nature. Version 2 also makes explicit that attaching a grade cannot rescue a
claim whose carrier, quantifier, or bridge to physics was not constructed.

## The anti-smuggling discipline

The standing failure mode of any flexible framework is to smuggle its conclusion into its premises. The calculus's
$P_6$ (audit) role is a set of mechanical gates against this: a quantity may not be *defined* to equal the target
(anti-tautology); each hypothesis must be independently satisfiable by a structure that *fails* the conclusion
(anti-circularity); imported machinery is frozen and hash-pinned so it cannot be retuned toward the answer
(frozen-machinery); and every positive claim must be accompanied by a **can-fail control** — a configuration on which
the claim comes out false, demonstrating the test discriminates. Section 3 describes how these gates operated in
practice, including the cases where they fired against our own constructions.
