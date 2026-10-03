# Further applications

This section applies the same vocabulary to four further puzzles. The applications differ in strength and are graded
individually: the Bell row recovers a standard result, the information-loss row rests on a general theorem with exact
certificates, the cosmological-constant row is sample-bounded numerics, and the measurement row is a conditional lemma
with a stipulated two-example taxonomy. They show that the vocabulary travels; they are not evidence of universality.

## Bell nonlocality: the common carrier is not a hidden variable

The common-carrier hypothesis of Section 5.3 invites an obvious objection: a single carrier
underlying both readouts sounds like a local hidden variable, and local hidden variables are ruled out by
experiment. The calculus turns the objection into a computation.

For a Bell pair with the standard CHSH settings [@Bell1964; @CHSH1969] ($a_0=Z$, $a_1=X$,
$b_{0,1}=(Z\pm X)/\sqrt2$), the correlations computed from the state give
$\mathrm{CHSH}_{\rm quantum}=2\sqrt2\approx2.8284$. Enumerating all $16$ deterministic local strategies gives a
maximum of exactly $2$, and since CHSH is linear in the correlations, no mixture of those strategies does better. This
is Bell's theorem in its usual CHSH form, recovered, not discovered. A classical mixture with
$\mathrm{CHSH}=\sqrt2$ serves as the control: an explicit $16$-row local table reproduces its correlations to
$1.8\times10^{-15}$.

The repository files this result in the form of the F49 law. F49 asks whether a correlation table factors
deterministically through a common source fiber, through an interface, or through a declared direct route between the
wings, each with its own admissibility conditions. Formally, a *nonlocal residual* requires that all of these
explanations fail *and* that a declared locality package fail. The finite construction records the failure of
the declared common-source and interface explanations for the Bell table; it does not construct the full set of
deterministic maps, admissible classes, and locality-package failure that a formal F49 nonlocal-residual instance
would need. The F49 label is therefore bookkeeping for the standard result. The probabilistic content comes from the
CHSH bound, not from F49, which concerns deterministic factorization and is not a probabilistic Bell theorem.

The calculus-specific point concerns the carrier. A local hidden variable would have to be an *admissible* common
source for the complementary settings. F37 says that complementary accesses have no joint quotient within a declared
admissible class. (The paired map $(q_A,q_B)$ always exists as a mathematical map; what fails is its admissibility
as a joint access.) The computed normalized commutator residuals of the settings, $1/\sqrt2\approx0.707$ under the declared
normalization, match the carrier's complementary-pair control. Hence
the following **forbidden rule**: a common mathematical carrier sitting above the access structure is not a
Bell-local hidden-variable mechanism, and any reading of the framework that uses it as one is excluded.

## Information loss: a property of the readout

The F34 law asks whether information is lost along a map. Given a transport $\tau:H_0\to H_1$, a readout $\rho$ on
$H_1$, and source information $\sigma$ on $H_0$, consider
$$
\mathcal O_\rho=\{(h,h') : \rho(\tau h)=\rho(\tau h')\ \text{and}\ \sigma(h)\neq\sigma(h')\}.
$$
If $\mathcal O_\rho$ is empty, $\sigma$ can be recovered from the readout (as a function on the image of
$\rho\circ\tau$); if not, information is lost. We apply this to a toy holographic carrier, with no dynamics and no
evaporation, asking where information loss lives. Figure 6 summarizes the answer.

**The carrier.** An interior configuration is a pair of real tensor frames $(L,R)$, each $81\times27$,
joined along an internal bond of dimension $d=27$. The transport $\tau$ contracts the bond to the raw boundary
matrix $M=LR^{\mathsf T}$. Internal gauge transformations $(L,R)\mapsto(LG,\,RG^{-\mathsf T})$, with $G\in GL(d)$,
leave $M$ unchanged. “Physical” interior information means gauge-invariant functions of the pair.

**Theorem (Full-readout fibers are gauge orbits).**
Let $K$ be a field, $L\in K^{m\times d}$, $R\in K^{n\times d}$, and $M=LR^{\mathsf T}$ with
$\operatorname{rank}M=d$. If $L'\in K^{m\times d}$ and $R'\in K^{n\times d}$ satisfy $L'R'^{\mathsf T}=M$, then
there is a unique $G\in GL(d,K)$ with $L'=LG$ and $R'=RG^{-\mathsf T}$. Conversely, every such pair satisfies
$L'R'^{\mathsf T}=M$.

*Proof.*
Since $\operatorname{rank}M=d$ and every factor has $d$ columns, $L,R,L',R'$ all have full column rank. Because
$R^{\mathsf T}$ is onto $K^d$, the column space of $M$ equals that of $L$, and likewise that of $L'$. The
columns of $L$ and of $L'$ are therefore two bases of one $d$-dimensional space, so $L'=LG$ for a unique
invertible $G$. Multiplying $LR^{\mathsf T}=LGR'^{\mathsf T}$ on the left by any left inverse of $L$ gives
$R^{\mathsf T}=GR'^{\mathsf T}$, that is, $R'=RG^{-\mathsf T}$. The converse is
$LG(RG^{-\mathsf T})^{\mathsf T}=LR^{\mathsf T}$.
∎

Hence, at full rank, the fiber of the raw boundary readout is exactly one gauge orbit, and every gauge-invariant
function of $(L,R)$ factors through the readout on its image. Whether the theorem applies to the actual carrier is a
question of exact rank, which floating-point singular values cannot settle. It is settled by certificate: for each of
the three seeds, both frames, with their double-precision entries read as exact binary rationals, are reduced modulo the prime
$2^{31}-1$ and have a nonzero $27\times27$ minor. Each frame thus has exact rank $27$, and so does the exact product
$M$. (This does not certify the rank of the *rounded* floating-point product.) The rank hypothesis is needed:
with $d=2$, the pairs $L=\mathrm{diag}(1,0)$, $R=I$ and $L'=R'=\mathrm{diag}(1,0)$ contract to the same
nonzero matrix, yet $R$ and $R'$ have different ranks, so no gauge transformation relates them.

One subtlety matters for physics. A quantum state is a normalized ray, not a raw matrix. If the readout is the
normalized boundary state, its fibers are gauge orbits only after an overall scalar is also allowed, and only
functions invariant under both the gauge and that rescaling can be recovered. For example, $\|M\|^2$ is
gauge-invariant but cannot be recovered from the normalized ray, since $(2L,R)$ gives the same ray with four times
the squared norm.

**Partial readout.** Now let the readout be only the reduced state on the left half of the boundary, the toy
analogue of seeing only the early radiation. Replace $R$ by $UR$, where $U$ is the permutation exchanging the
first two right-boundary coordinates. Then $M'=MU^{\mathsf T}$ and $M'M'^{\mathsf T}=MM^{\mathsf T}$, so the left
reduced state is exactly unchanged. But the right-boundary observable $Z=\mathrm{diag}(1,-1,0,\dots,0)$ has
expectation $-4.674\times10^{-3}$ before the swap and $+4.674\times10^{-3}$ after it, computed exactly in integer
Gram arithmetic for seed $101$. The two full normalized states therefore differ while the partial readout agrees:
physical information is genuinely lost.

**Forbidden rule.** In this toy carrier, loss of physical (gauge- and scale-invariant) information is excluded at
the full boundary readout and forced at the half-boundary readout. The information puzzle [@Hawking1976] is, here,
a property of the readout rather than of the carrier. No dynamics, evaporation, or Page curve [@Page1993] is
modeled, and nothing follows about real black holes (`review_2026/repairs/f34_exact_factorization/`).

> **Figure (drawn in TikZ; see the PDF).** **Where information loss lives in the toy holographic carrier.** (a) Inserting $GG^{-1}$ on the
internal bond never changes the boundary matrix, and by Theorem 7.1 nothing else does at full rank: what
the full raw readout forgets is pure gauge (for normalized states, gauge plus an overall scale). (b) A readout of the
left half alone cannot see a permutation $U$ of the right half, yet that permutation changes a right-boundary
expectation value. Information loss is a property of the readout, not of the carrier.

## The cosmological constant: no in-layer value law

The F50 carrier contains an analogue of a cosmological background [@Weinberg1989]: the matter-independent term
$V_0$ in $V[\psi]=V_0+\kappa T_{00}[\psi]$. A fixed solver budget ($60$ iterations at mixing $0.5$) converges for
only $15$ of $18$ sampled background offsets (it fails at offsets $-5$, $-3$, and $10$), which looks like an
admissibility boundary. It is an artifact of the budget: at $120$ iterations all $18$ converge. A historical
finite-budget boundary in $\kappa$ is likewise not an existence boundary, since all $12$ sampled $\kappa$ values have
fixed points. Adaptive iteration with damping values $0.2,0.35,0.5,0.7$ and at least three initial states finds a fixed point
for every sampled background and every sampled $\kappa$, so there is no existence boundary on the declared sample. The
Jacobian of the raw (undamped) fixed-point map offers a different, non-unique discriminator: its spectral radius crosses
one near background offset $3.6535$ and near $\kappa=5.8675$, and $15$ of the $18$ sampled backgrounds are linearly
stable under that map. Whether that criterion defines physical admissibility is a modeling
choice. The sample therefore supports only this: *no unique value law for $\Lambda$ is selected within the layer,
and every sampled background admits a fixed point*. These are sampled numerics, not interval-certified existence or
bifurcation theorems (`review_2026/repairs/q7_f50_convergence/`).

## The measurement problem: a conditional discriminator

The established content is a definability lemma, conditional on a supplied source language and closure
$§igma_f$ on the declared carrier, together with a two-example taxonomy that is stipulated to separate
“ledger-changing” from “readout-changing” accounts of measurement. It is not a theorem that strictly extends
quantum mechanics, and it is not an operational test for future measurement theories. A generated class of theories
and a physical correspondence would be needed before that language is warranted.

## Summary

| puzzle | law | verdict | control |
| --- | --- | --- | --- |
| Bell nonlocality | F49, F37 | CHSH $2\sqrt2>2$ recovered; the carrier is not a local hidden variable | classical mixture with an explicit local table |
| information loss | F34 | full raw readout loses only gauge data (theorem); half readout loses physical data | rank-deficient pair; exact permutation witness |
| cosmological constant | F50, F47/F26 | fixed points for every sampled background; no unique in-layer value law | raw-map stability crossing, if adopted |
| measurement | non-factorization | $§igma_f$-conditional lemma; stipulated two-example taxonomy | identical-diagonal witness pair |

These rows are bounded diagnostics on their declared carriers. They add neither established predictions nor a
universality result.
