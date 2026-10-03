# Result I: a finite Standard-Model selection construction

This section treats the Standard Model's gauge structure as something *selected* from a finite space of
alternatives and asks what the selection depends on. The short answer is that, within declared windows, a “clean”
symmetry-breaking condition singles out the $SU(2)\times SU(3)$ family, but only as a property of a structure
together with a breaking branch. Figure 4 summarizes the census and the branch typing.

## The selection layer

The construction (called L*) places a finite space of candidate structures, a set of constraints, and a selector one
layer above the realized candidate. Its descent and role-split diagnostics form a coherent finite construction, not
a derivation from nature. Two caveats are essential. First, the construction assumes a single selection layer; the
supporting evidence shows block structure only within that layer and does not exclude hidden or multi-layer selectors.
Second, the *architecture* of the selector is not determined. Two constructed families, a scale-carrying memory
layer and a finite naturalness budget, both form, are admissible, and reach a closure fixed point on the $468$-row
admissible carrier. The memory-layer closure gate is an experimental finite diagnostic, not evidence of a physically
independent scale layer (`review_2026/repairs/s5_f24_f47/`).

## The carrier and what it excludes

The carrier enumerates candidate chiral gauge structures within declared windows: one or two nonabelian factors
with $SU(N)$ dimensions $2$ through $4$, a field cap of five, a component cap of six, and a declared
$U(1)$ charge alphabet. Representation conjugation is implemented as an involution, including the special cases of
pseudoreal and real $SU(2)$ representations, so the alphabet is closed under conjugation and contains no aliases.
This matters: an alphabet without this closure inflates the count to $11{,}990$ rows, of which $9{,}126$ are
duplicates. Dimensions, Dynkin indices, and cubic anomalies are checked against an independent table, and again by the
independent oracle of Section 3.1.

Within these windows the carrier contains $1{,}066$ labelled, genuinely chiral structures. How many of them are
“different” depends on a declared equivalence. Freely adjoined, fully neutral singlets are deleted, and the orbit
convention identifies structures related by exchanging equal-dimension factors, conjugating all nonabelian
representations at once, or flipping the sign of the $U(1)$ charge. It does not identify charge rescalings or
field-by-field conjugation. This gives $419$ orbits. Normalizing charges to primitive integers instead gives $195$
orbits; this is an alternative convention, not a convention-free physical count. Three successive filters, atomic packaging, closure
consistency, and chirality-faithfulness, then leave
$$
1{,}066\to84\to62\to52,\qquad
419\to37\to27\to24,\qquad
195\to37\to27\to24,
$$
a cumulative exclusion of $95.12%$, $94.27%$, and $87.69%$ respectively. The $52$ survivors are the
chirality-faithful structures used below.
These percentages belong to their exact denominators and are not a measure on gauge theories in general. The
representation model, quotient mutations, and an independent scalar gate are in
`review_2026/repairs/s1_carrier_reconstruction/`.

> **Figure (drawn in TikZ; see the PDF).** **The Standard-Model census.** (a) Within the declared windows, three successive filters (atomic packaging,
closure consistency, chirality-faithfulness) remove most candidate structures under each of three counting
conventions. (b) A branch is a structure together with a choice of
breaking scalar (or scalar pair). Clean branches exist only for $2|3$ and always act on the $SU(2)$ factor, but
every $2|3$ structure also has breaking branches. The selection is therefore existential over branches, not a
property of the bare gauge structure.

## Clean separation selects a branch, not a structure

For each chirality-faithful structure $C$, the construction enumerates *every* admissible complex scalar
$\phi$ in the inherited alphabet and cap, rather than picking one witness, and separately every scalar pair
$(\phi_1,\phi_2)$ that jointly covers the Yukawa couplings and jointly breaks. Each such choice is a *branch*.
On each branch the construction applies a fixed residual proxy, in which the factor $SU(N)$ on which the scalar acts
breaks to $SU(N-1)$, and computes the active factor, the residual structure, the number of broken (coset)
generators, and the factorization defect between the confinement readout and the mass readout. A branch is called
*clean* when this defect is empty:
$$
\text{clean separation}\iff\Deltafact=\varnothing .
$$
Both cleanliness and the defect are functions of the same proxy count, so the census is a classification conditional
on the proxy, not a derivation of symmetry breaking.

Only $8$ of the $52$ structures have an admissible singleton branch ($12$ branches in all); every one of the
$52$ has admissible scalar-pair branches. Within the declared singleton and two-scalar caps, the result is as
follows. Clean branches occur only in the $2|3$
family, with nonabelian factors $SU(2)$ and $SU(3)$. The four labelled clean singleton structures form a single
carrier orbit, and the $68$ clean two-scalar rows form $17$ pair-branch orbits. Every clean branch is
*$SU(2)$-active*, meaning that the scalar acts on the $SU(2)$ factor; every branch with an $SU(4)$ factor
is breaking. The quantifier is what matters:

- **“every branch is clean” is false for $2|3$:** every $2|3$ structure also has a breaking branch, so
   clean separation is not a property of the bare structure;
- **“some branch is clean” holds only for $2|3$:** clean separation selects the branch class
   ($2|3$, $SU(2)$-active orientation).

No clean branch outside this class appears in the two-scalar extension either. The result is a uniqueness statement
on an explicitly finite domain.

**A toy theorem for one factor.** Separately, a witness-independent theorem excludes single-factor
candidates in its toy grammar. Suppose a single-factor $SU(N)$ structure passes the grammar's stability condition,
which requires a confining residual. The breaking scalar must then act on the only nonabelian factor, so the residual is
$SU(N-1)$ with $N-1\ge2$, and the broken coset contributes $2(N-1)>0$ massive vectors charged under the
confining residual. The grammar's deliberately coarse confinement readout gives these massive vectors the same value
as the massless residual generators, while their mass status differs. That pair is a witness, so
$\Delta_{\mathrm{fact}}\neq\varnothing$ for every $N$. The validator rebuilds all released artifacts and constructs the actual
witness pairs for $N=3,\dots,12$, with a same-mass control (which must remove the defect) and a clean two-factor
control. This is a theorem about the toy grammar, not about confinement or the Standard Model in nature. A companion
exclusion of three active factors is weaker: it rests on the declared component cap, since a scalar charged under three
nonabelian factors has at least $2^3=8>6$ components.

## An explicit $SU(5)$ frame and the recovered ratios

Grand unification [@GeorgiGlashow1974] is reconstructed here as an explicit object rather than assumed. The
construction starts from exact $5\times5$ traceless Hermitian generators. For the regular embedding of
$SU(3)\times SU(2)$, the commutant of the embedded algebra inside $\mathfrak{su}(5)$ is one-dimensional (the
linear constraints have rank $23$ on the $24$-dimensional algebra). Tracelessness and commutation therefore force
the hypercharge direction, up to scale and sign, to be proportional to $\mathrm{diag}(-1/3,-1/3,-1/3,1/2,1/2)$. The
twelve coset generators transform as $(\mathbf3,\mathbf2)_{-5/6}\oplus(\overline{\mathbf3},\mathbf2)_{+5/6}$.

Decomposing the $\overline{\mathbf5}+\mathbf{10}$ package and adopting the named weak-pair normalization gives
$\operatorname{Tr}T_3^2=2$ and $\operatorname{Tr}Q^2=16/3$, hence exactly
$$
\sin^2\theta_W=\frac{\operatorname{Tr}T_3^2}{\operatorname{Tr}Q^2}=\frac38,
\qquad k_Y=\frac53 .
$$
These are standard group-theoretic facts, reconstructed exactly with every input declared. They hold *given* the
regular embedding, the fermion package, and the normalization convention. They do not select the parent group: the
Pati–Salam group [@PatiSalam1974] also gives $3/8$, and no well-posed alternative product parent with a
different ratio has a constructed realization. They are not low-energy predictions either, since no running to a
measured scale is performed. The contribution is an audited reconstruction, not a new derivation.

Inside the same frame, the roles of the coset are computed from generator action rather than assigned as labels.
Generator action shows that the coset transitions carry $\Delta B\neq0$. With
$H=(SU(3)\times SU(2)\times U(1))/\mathbb Z_6$, the extracted cocharacter lattice, combined with three imported
facts ($H$ is connected, $\pi_1(SU(5))=0$, and $\pi_2(SU(5))=0$), gives the monopole class
$\pi_2(SU(5)/H)\cong\mathbb Z$. So the
proton-decay, monopole, and clean-separation roles all attach to one object, inside this constructed frame. A
six-generator $SU(4)\to SU(3)$ object from the earlier toy grammar is a structural analogue only. It is not the
twelve-generator $X/Y$ coset, and a computed $SU(2)$ commutator shows that a fixed six-generator slice is not
invariant (`review_2026/repairs/s3_generator_construction/`).

## Does record stability force clean separation?

A natural hope is that clean separation is not an extra condition but follows from something deeper, such as the
requirement that the low-energy theory support stable records. On this carrier the answer depends on what counts as a
record. On the $12$ admissible singleton branches, at the reference record threshold, a restricted record-token grammar
makes the implication hold. A bounded but complete census of candidate invariant operators makes it fail in every
reading, with or without scalar dressings.
Section 6.3 gives the details. The phrase “gauge shadow of a memory layer” is
therefore a narrative over a correlation, not a computed projection between layers, and the question of which
candidate operators persist as physical records is an open program.

## Content, generations, masses, and scales

**Content.** Under global color conjugation, global $U(1)$ sign, factor exchange, and deletion of inert
singlets, the $28$ labelled anomaly-free supports in the declared template form $14$ orbits. The strongest
conjunction of conditions selects one content orbit, and the SM and its superficially different alternative turn out
to be two presentations of that orbit. This is uniqueness *within the template*; the associated minimality no-go
has rank $14/14$.

**Generations.** The grammar neither ignores the number of generations $N$ nor selects $N=3$. A
materialized probe for $N=1,\dots,4$ finds the anomaly, parity, chirality, branch, and mass predicates unchanged by
replication, while atomicity and route-incidence fail for every $N\ge2$ for reasons internal to the grammar.
Structural conditions that would make the grammar blind to $N$ reduce to “at least one family”.

**Mass-matrix rank.** Rank is computed with independent symbolic coefficients and with multiplicities
retained; mere coverage of the coupling graph does not determine rank. For the renormalizable one-scalar grammar, the
generic charged ranks are $14,28,42,56$ for $N=1,2,3,4$, and the neutral deficiencies are $1,2,3,4$, one unpaired
left-handed neutrino per generation. No masses, textures, or measured values are derived
(`review_2026/repairs/s4_content_quotient/`).

**Naturalness.** The F47 naturalness fraction is a surface, not a number. In one declared cell (weighted
admissible rows, upstream threshold) it is $2.247%$, but that cell is not uniquely privileged: across the declared
sweep the fraction ranges from $0$ to $40.6%$. The realized point sits exactly at the threshold $2.75$, so a
strict comparison excludes it.

## Summary

| question | status | scope |
| --- | --- | --- |
| gauge-structure exclusion | finite census | $1{,}066\to52$, $419\to24$, or $195\to24$ through three filters, under the named equivalences |
| clean-separation selection | branch-level finite selection | unique clean branch class: $2\|3$, $SU(2)$-active; no selection of a bare structure |
| single-factor exclusion | toy theorem | witness-independent in the stated grammar; validator rebuilds artifacts and witnesses |
| hypercharge and ratios | conditional exact construction | regular $SU(5)$ embedding, $\overline{\mathbf5}+\mathbf{10}$, weak-pair normalization; imported topology for the monopole class |
| content | unique orbit in template | recognition within the template; minimality rank $14/14$ |
| generations | no blindness theorem | mixed $N$-dependence for $N=1,\dots,4$; no selection of three |
| record-stability grounding | open program | bounded candidate census is token-definition-sensitive |
| architecture and scale | underdetermined; sensitive | two architecture families close; F47 surface $0$–$40.6%$ |
